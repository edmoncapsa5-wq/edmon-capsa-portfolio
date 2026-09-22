(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.QuoteRescueEngine = api;
})(typeof self !== 'undefined' ? self : globalThis, function () {
  const EPS = 1e-9;

  function n(value) {
    const x = Number(value);
    return Number.isFinite(x) ? x : 0;
  }

  function clampPct(value) {
    return Math.min(Math.max(n(value), 0), 0.95);
  }

  function moneyRound(value) {
    return Math.round((n(value) + Number.EPSILON) * 100) / 100;
  }

  function priorityWeight(priority) {
    if (priority === 'essential') return 100;
    if (priority === 'important') return 20;
    return 5;
  }

  function normalizeSettings(settings = {}) {
    const paymentFee = clampPct(settings.paymentFee);
    const minMargin = clampPct(settings.minMargin);
    const targetMargin = clampPct(settings.targetMargin);
    if (paymentFee + minMargin >= 0.99) {
      throw new Error('Payment fee + minimum margin must be below 99%.');
    }
    if (paymentFee + targetMargin >= 0.99) {
      throw new Error('Payment fee + target margin must be below 99%.');
    }
    return {
      paymentFee,
      minMargin,
      targetMargin: Math.max(targetMargin, minMargin),
      minProfit: Math.max(n(settings.minProfit), 0),
      minimumBooking: Math.max(n(settings.minimumBooking), 0),
    };
  }

  function floors(cost, settings) {
    const s = normalizeSettings(settings);
    const c = Math.max(n(cost), 0);
    const marginFloor = c / (1 - s.paymentFee - s.minMargin);
    const profitFloor = (c + s.minProfit) / (1 - s.paymentFee);
    const protectedFloor = Math.max(marginFloor, profitFloor, s.minimumBooking);
    const targetMarginFloor = c / (1 - s.paymentFee - s.targetMargin);
    const targetFloor = Math.max(targetMarginFloor, protectedFloor, s.minimumBooking);
    return {
      cost: moneyRound(c),
      marginFloor: moneyRound(marginFloor),
      profitFloor: moneyRound(profitFloor),
      protectedFloor: moneyRound(protectedFloor),
      targetFloor: moneyRound(targetFloor),
    };
  }

  function optionLoss(component, option) {
    if (option.kind === 'original') return 0;
    const base = priorityWeight(component.priority || 'important');
    if (option.kind === 'simplify') return base;
    if (option.kind === 'remove') return base * 3;
    return base * 2;
  }

  function normalizeComponent(component, idx) {
    const name = String(component.name || `Component ${idx + 1}`).trim();
    const options = [{
      kind: 'original',
      label: String(component.originalLabel || 'Keep original'),
      price: Math.max(n(component.originalPrice), 0),
      cost: Math.max(n(component.originalCost), 0),
      change: false,
    }];

    if (component.simplify && component.simplify.enabled) {
      options.push({
        kind: 'simplify',
        label: String(component.simplify.label || 'Simplified version'),
        price: Math.max(n(component.simplify.price), 0),
        cost: Math.max(n(component.simplify.cost), 0),
        change: true,
      });
    }
    if (component.canRemove) {
      options.push({
        kind: 'remove',
        label: 'Remove',
        price: 0,
        cost: 0,
        change: true,
      });
    }

    return {
      id: component.id || `c${idx + 1}`,
      name,
      priority: component.priority || 'important',
      options,
    };
  }

  function enumerateConfigurations(components) {
    const normalized = components.map(normalizeComponent);
    const out = [];
    function walk(i, selected) {
      if (i >= normalized.length) {
        const quotedPrice = selected.reduce((a, s) => a + s.option.price, 0);
        const cost = selected.reduce((a, s) => a + s.option.cost, 0);
        const loss = selected.reduce((a, s) => a + optionLoss(s.component, s.option), 0);
        const changes = selected.reduce((a, s) => a + (s.option.change ? 1 : 0), 0);
        out.push({ selected: selected.slice(), quotedPrice, cost, loss, changes });
        return;
      }
      const component = normalized[i];
      for (const option of component.options) {
        selected.push({ component, option });
        walk(i + 1, selected);
        selected.pop();
      }
    }
    walk(0, []);
    return out;
  }

  function decorateConfig(config, settings) {
    const f = floors(config.cost, settings);
    const recommendedPrice = Math.max(config.quotedPrice, f.targetFloor, f.protectedFloor);
    const profitAtRecommended = recommendedPrice * (1 - settings.paymentFee) - config.cost;
    const marginAtRecommended = recommendedPrice > 0 ? profitAtRecommended / recommendedPrice : 0;
    return {
      ...config,
      ...f,
      recommendedPrice: moneyRound(recommendedPrice),
      profitAtRecommended: moneyRound(profitAtRecommended),
      marginAtRecommended,
    };
  }

  function sortBest(a, b) {
    if (a.loss !== b.loss) return a.loss - b.loss;
    if (a.changes !== b.changes) return a.changes - b.changes;
    if (Math.abs(a.recommendedPrice - b.recommendedPrice) > EPS) return b.recommendedPrice - a.recommendedPrice;
    return b.profitAtRecommended - a.profitAtRecommended;
  }

  function summarizeSelected(config) {
    return config.selected.map(({ component, option }) => ({
      id: component.id,
      name: component.name,
      priority: component.priority,
      kind: option.kind,
      label: option.label,
      price: moneyRound(option.price),
      cost: moneyRound(option.cost),
    }));
  }

  function solve(input) {
    const budget = Math.max(n(input.clientBudget), 0);
    const settings = normalizeSettings(input.settings || {});
    const components = Array.isArray(input.components) ? input.components : [];

    if (!components.length) {
      return { decision: 'INVALID', reason: 'Add at least one quote component.' };
    }

    const unresolved = Array.isArray(input.unresolvedLogistics)
      ? input.unresolvedLogistics.filter(Boolean).map(String)
      : [];
    if (unresolved.length) {
      return {
        decision: 'NEED_MORE_INFORMATION',
        reason: 'Material logistics are unresolved and could change the job economics.',
        unresolvedLogistics: unresolved,
      };
    }

    const configs = enumerateConfigurations(components).map(c => decorateConfig(c, settings));
    const full = configs.find(c => c.changes === 0);
    if (!full) throw new Error('Full-scope configuration is missing.');

    const fullQuote = moneyRound(full.quotedPrice);
    const fullRecommended = full.recommendedPrice;

    if (fullQuote <= budget + EPS && fullQuote + EPS >= full.targetFloor) {
      return {
        decision: 'QUOTE_FULL_SCOPE',
        reason: 'The original scope fits the client budget and meets the target economics.',
        budget: moneyRound(budget),
        originalQuote: fullQuote,
        selectedPrice: fullQuote,
        selected: summarizeSelected(full),
        financials: full,
      };
    }

    if (fullQuote < full.targetFloor - EPS && fullRecommended <= budget + EPS) {
      return {
        decision: 'REPRICE_FULL_SCOPE',
        reason: 'The client can afford the full scope, but the entered quote is below the business target.',
        budget: moneyRound(budget),
        originalQuote: fullQuote,
        selectedPrice: fullRecommended,
        selected: summarizeSelected(full),
        financials: full,
      };
    }

    const targetSafe = configs
      .filter(c => c.changes > 0 && c.recommendedPrice <= budget + EPS)
      .sort(sortBest);

    if (targetSafe.length) {
      const best = targetSafe[0];
      return {
        decision: 'RE_SCOPE',
        reason: 'An approved lower-scope configuration fits the budget while protecting target economics.',
        budget: moneyRound(budget),
        originalQuote: fullQuote,
        selectedPrice: best.recommendedPrice,
        selected: summarizeSelected(best),
        financials: best,
      };
    }

    const protectedFeasible = configs
      .filter(c => c.protectedFloor <= budget + EPS)
      .sort((a, b) => {
        if (a.loss !== b.loss) return a.loss - b.loss;
        if (a.changes !== b.changes) return a.changes - b.changes;
        return b.protectedFloor - a.protectedFloor;
      });

    if (protectedFeasible.length) {
      const best = protectedFeasible[0];
      return {
        decision: 'NEGOTIATION_ZONE',
        reason: 'A version can stay above the protected floor, but the budget is below target economics. Do not auto-discount.',
        budget: moneyRound(budget),
        originalQuote: fullQuote,
        selectedPrice: moneyRound(budget),
        selected: summarizeSelected(best),
        financials: best,
      };
    }

    const cheapestFloor = [...configs].sort((a, b) => a.protectedFloor - b.protectedFloor || a.loss - b.loss)[0];
    return {
      decision: 'NO_SAFE_FIT',
      reason: 'No approved configuration can meet the client budget without crossing the business protected floor.',
      budget: moneyRound(budget),
      originalQuote: fullQuote,
      selectedPrice: null,
      selected: summarizeSelected(cheapestFloor),
      financials: cheapestFloor,
    };
  }

  function createClientMessage(result, currencySymbol = '$') {
    const fmt = v => `${currencySymbol}${moneyRound(v).toFixed(2)}`;
    if (!result || !result.decision) return '';
    const changed = (result.selected || []).filter(x => x.kind !== 'original');
    const kept = (result.selected || []).filter(x => x.kind === 'original');

    if (result.decision === 'QUOTE_FULL_SCOPE') {
      return `Thanks for confirming your budget. The original setup can stay exactly as quoted at ${fmt(result.selectedPrice)}.`;
    }
    if (result.decision === 'REPRICE_FULL_SCOPE') {
      return `Thanks for confirming your budget. I can keep the full setup as requested. The corrected total for the complete scope is ${fmt(result.selectedPrice)}.`;
    }
    if (result.decision === 'RE_SCOPE') {
      const keepText = kept.length ? kept.map(x => x.name).join(', ') : 'the core look';
      const changeText = changed.length ? changed.map(x => `${x.name}: ${x.label}`).join('; ') : 'a simplified scope';
      return `Thanks for sharing your budget. I can adjust the setup while keeping ${keepText}. The revised option changes ${changeText}, bringing the total to ${fmt(result.selectedPrice)}. The full original design remains available at ${fmt(result.originalQuote)}.`;
    }
    if (result.decision === 'NEGOTIATION_ZONE') {
      return `Thanks for sharing your budget. I can review a reduced-scope option, but I need to confirm the final design before committing to a price. The full original setup is ${fmt(result.originalQuote)}.`;
    }
    if (result.decision === 'NO_SAFE_FIT') {
      return `Thanks for sharing your budget. I’m not able to offer the requested setup within that budget without changing the job beyond what I can responsibly deliver. The full original setup is ${fmt(result.originalQuote)}.`;
    }
    if (result.decision === 'NEED_MORE_INFORMATION') {
      return `Before I confirm the quote, I need a few logistics details that could affect the setup and final price.`;
    }
    return '';
  }

  return {
    solve,
    floors,
    enumerateConfigurations,
    createClientMessage,
    normalizeSettings,
  };
});
