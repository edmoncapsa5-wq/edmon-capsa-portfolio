const E = window.QuoteRescueEngine;
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
let counter = 0;
const SETTINGS_KEY = 'quoteRescue.settings.v02';

function num(v){ const x=Number(v); return Number.isFinite(x)?x:0; }
function currency(){ return $('#currency').value || '$'; }
function fmt(v){ return `${currency()}${num(v).toFixed(2)}`; }
function esc(s){ return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }

function itemSummary(div){
  const name = div.querySelector('.c-name').value.trim() || 'Untitled quote item';
  const price = num(div.querySelector('.c-price').value);
  const cost = num(div.querySelector('.c-cost').value);
  div.querySelector('.component-title').textContent = name;
  div.querySelector('.component-meta').textContent = price || cost ? `${fmt(price)} quote · ${fmt(cost)} cost` : 'Tap to add price, cost and flexibility';
}

function addComponent(data={}){
  counter += 1;
  const id = `component-${counter}`;
  const div = document.createElement('details');
  div.className='component'; div.dataset.id=id; div.open = !data.name;
  div.innerHTML = `
    <summary class="component-summary"><span><strong class="component-title">Quote item</strong><small class="component-meta">Tap to add price, cost and flexibility</small></span><span class="chev">⌄</span></summary>
    <div class="component-body">
      <div class="component-head"><span class="mini-label">QUOTE ITEM</span><button type="button" class="btn small danger remove-component">Remove</button></div>
      <div class="field"><label>Item name</label><input class="c-name" placeholder="e.g. 12-ft balloon garland" value="${esc(data.name||'')}"></div>
      <div class="row"><div class="field"><label>Price in current quote</label><input class="c-price" type="number" min="0" step="0.01" value="${data.originalPrice ?? ''}"></div><div class="field"><label>Your internal cost</label><input class="c-cost" type="number" min="0" step="0.01" value="${data.originalCost ?? ''}"></div></div>
      <div class="field"><label>How important is this to the client?</label><select class="c-priority"><option value="essential">Must stay if possible</option><option value="important">Prefer to keep</option><option value="nice">Optional / nice-to-have</option></select></div>
      <div class="toggleline"><label><input class="c-simplify" type="checkbox"> I have a cheaper version</label><label><input class="c-remove" type="checkbox"> I can remove it</label></div>
      <div class="alt hidden"><div class="field"><label>Cheaper version</label><input class="c-s-label" placeholder="e.g. 8-ft garland"></div><div class="row"><div class="field"><label>Cheaper version price</label><input class="c-s-price" type="number" min="0" step="0.01"></div><div class="field"><label>Cheaper version cost</label><input class="c-s-cost" type="number" min="0" step="0.01"></div></div></div>
    </div>`;
  $('#components').appendChild(div);
  div.querySelector('.c-priority').value=data.priority||'important';
  div.querySelector('.c-remove').checked=!!data.canRemove;
  if(data.simplify?.enabled){
    div.querySelector('.c-simplify').checked=true;
    div.querySelector('.alt').classList.remove('hidden');
    div.querySelector('.c-s-label').value=data.simplify.label||'';
    div.querySelector('.c-s-price').value=data.simplify.price ?? '';
    div.querySelector('.c-s-cost').value=data.simplify.cost ?? '';
  }
  div.querySelector('.c-simplify').addEventListener('change',ev=>div.querySelector('.alt').classList.toggle('hidden',!ev.target.checked));
  div.querySelector('.remove-component').addEventListener('click',ev=>{ev.preventDefault();div.remove();});
  ['input','change'].forEach(evt=>div.addEventListener(evt,()=>itemSummary(div)));
  itemSummary(div);
}

function collectComponents(){
  return $$('.component').map((el,i)=>({
    id:el.dataset.id,
    name:el.querySelector('.c-name').value.trim() || `Component ${i+1}`,
    originalPrice:num(el.querySelector('.c-price').value),
    originalCost:num(el.querySelector('.c-cost').value),
    priority:el.querySelector('.c-priority').value,
    canRemove:el.querySelector('.c-remove').checked,
    simplify:{enabled:el.querySelector('.c-simplify').checked,label:el.querySelector('.c-s-label').value.trim() || 'Simplified version',price:num(el.querySelector('.c-s-price').value),cost:num(el.querySelector('.c-s-cost').value)}
  }));
}

function collectSettings(){return {paymentFee:num($('#paymentFee').value)/100,minMargin:num($('#minMargin').value)/100,targetMargin:num($('#targetMargin').value)/100,minProfit:num($('#minProfit').value),minimumBooking:num($('#minimumBooking').value)};}
function saveSettings(){localStorage.setItem(SETTINGS_KEY,JSON.stringify({currency:currency(),...collectSettings()}));$('#saved').textContent='Saved.';setTimeout(()=>$('#saved').textContent='',1600);}
function loadSettings(){try{const s=JSON.parse(localStorage.getItem(SETTINGS_KEY)||'null');if(!s)return;$('#currency').value=s.currency||'$';$('#paymentFee').value=(num(s.paymentFee)*100)||0;$('#minMargin').value=(num(s.minMargin)*100)||0;$('#targetMargin').value=(num(s.targetMargin)*100)||0;$('#minProfit').value=num(s.minProfit)||0;$('#minimumBooking').value=num(s.minimumBooking)||0;}catch{}}
function setError(msg=''){const el=$('#error');el.textContent=msg;el.classList.toggle('show',!!msg);}
function buildInput(){const unresolved=[];if($('#unresolved').checked) unresolved.push($('#unresolvedText').value.trim()||'Venue/logistics details still unresolved');return {clientBudget:num($('#budget').value),settings:collectSettings(),components:collectComponents(),unresolvedLogistics:unresolved};}

const labels={QUOTE_FULL_SCOPE:'QUOTE FULL SCOPE',REPRICE_FULL_SCOPE:'REPRICE FULL SCOPE',RE_SCOPE:'RE-SCOPE',NEGOTIATION_ZONE:'NEGOTIATION ZONE',NO_SAFE_FIT:'NO SAFE FIT',NEED_MORE_INFORMATION:'NEED MORE INFORMATION',INVALID:'CHECK INPUTS'};
function render(result){
  const box=$('#result');box.classList.add('show');const head=$('#resultHead');head.classList.remove('warn','danger');
  if(['NEGOTIATION_ZONE','NEED_MORE_INFORMATION','REPRICE_FULL_SCOPE'].includes(result.decision))head.classList.add('warn');
  if(['NO_SAFE_FIT','INVALID'].includes(result.decision))head.classList.add('danger');
  $('#decision').textContent=labels[result.decision]||result.decision;$('#reason').textContent=result.reason||'';
  if(result.decision==='NEED_MORE_INFORMATION'||result.decision==='INVALID'){$('#financialResult').classList.add('hidden');$('#scopeResult').classList.add('hidden');$('#clientMessage').textContent=E.createClientMessage(result,currency());box.scrollIntoView({behavior:'smooth',block:'start'});return;}
  $('#financialResult').classList.remove('hidden');$('#scopeResult').classList.remove('hidden');
  $('#mBudget').textContent=fmt(result.budget);$('#mOriginal').textContent=fmt(result.originalQuote);$('#mOffer').textContent=result.selectedPrice==null?'—':fmt(result.selectedPrice);$('#mFloor').textContent=fmt(result.financials.protectedFloor);
  const list=$('#scopeList');list.innerHTML='';(result.selected||[]).forEach(x=>{const row=document.createElement('div');row.className='scope-item';const kind=x.kind==='original'?'KEEP':x.kind==='simplify'?'CHANGE':'REMOVE';row.innerHTML=`<div><div class="kind">${kind}</div><strong>${esc(x.name)}</strong></div><div class="scope-right"><div>${esc(x.label)}</div><small>${fmt(x.price)}</small></div>`;list.appendChild(row);});
  $('#clientMessage').textContent=E.createClientMessage(result,currency());box.scrollIntoView({behavior:'smooth',block:'start'});
}
function solve(){
  setError('');const components=collectComponents();
  if(!$('#costConfirmed').checked)return setError('Confirm that the relevant job costs are included first.');
  if(!components.length)return setError('Add at least one quote item.');
  if(num($('#budget').value)<=0)return setError('Enter the client budget.');
  if(components.some(x=>x.originalPrice<=0))return setError('Every quote item needs a current quoted price.');
  if(num($('#targetMargin').value)<num($('#minMargin').value))return setError('Your target margin cannot be lower than your minimum margin.');
  try{render(E.solve(buildInput()));}catch(err){setError(err.message||String(err));}
}
function loadSample(){
  $('#budget').value=500;$('#currency').value='$';$('#paymentFee').value=3;$('#minMargin').value=20;$('#targetMargin').value=35;$('#minProfit').value=75;$('#minimumBooking').value=0;$('#components').innerHTML='';
  [
    {name:'Premium backdrop',originalPrice:180,originalCost:90,priority:'essential',simplify:{enabled:true,label:'Simple backdrop',price:120,cost:62}},
    {name:'Balloon garland',originalPrice:300,originalCost:135,priority:'essential',simplify:{enabled:true,label:'8-ft garland',price:220,cost:95}},
    {name:'Custom sign',originalPrice:80,originalCost:32,priority:'important',canRemove:true},
    {name:'Delivery + install',originalPrice:130,originalCost:73,priority:'important',simplify:{enabled:true,label:'Pickup / grab-and-go',price:0,cost:0}},
    {name:'Foil accents',originalPrice:45,originalCost:20,priority:'nice',canRemove:true}
  ].forEach(addComponent);
  $$('.component').forEach(x=>x.open=false);$('#costConfirmed').checked=true;$('#unresolved').checked=false;$('#unresolvedWrap').classList.add('hidden');$('#guardrailDetails').open=false;setError('');
}

$('#addComponent').addEventListener('click',()=>addComponent());$('#solve').addEventListener('click',solve);$('#saveSettings').addEventListener('click',saveSettings);$('#loadSample').addEventListener('click',loadSample);$('#unresolved').addEventListener('change',e=>$('#unresolvedWrap').classList.toggle('hidden',!e.target.checked));
$('#copyMessage').addEventListener('click',async()=>{const text=$('#clientMessage').textContent;try{await navigator.clipboard.writeText(text);$('#copyMessage').textContent='Copied';setTimeout(()=>$('#copyMessage').textContent='Copy message',1200);}catch{}});
loadSettings();addComponent();
