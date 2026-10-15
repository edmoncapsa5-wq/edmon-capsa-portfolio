# SME FAQ Intake — Synthetic Workflow Proof

**AI-assisted portfolio demonstration, October 2026.** This is **not** an externally commissioned, production, or deployed customer-support solution. It uses **rule-based** FAQ matching, not an LLM. No WhatsApp API is connected; no message ever leaves the demo. All inputs are synthetic.

## Implemented
- Local FastAPI inbound webhook with mock shared-key access check
- Fixed, approved FAQ topics (hours, prices, bookings)
- Draft responses that **require human approval** (no auto-send)
- Human handoff for unknown/ambiguous requests
- Opt-out handling that suppresses later inputs and queued approvals
- Deduplication by message ID persisted in SQLite
- Separate review endpoint with reviewer key
- Nine passing automated tests for authorization, deduplication, escalation, opt-outs and approval transitions

## Run (Python 3.11+)
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
```

Set WEBHOOK_SECRET, ADMIN_TOKEN and optional DEMO_DB_PATH, then start locally:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
curl -X POST http://127.0.0.1:8000/webhook/mock -H 'Content-Type: application/json' -H 'X-Demo-Webhook-Key: your-demo-key' -d '{"message_id":"001","customer_id":"synthetic-001","text":"What are your hours?"}'
```

Review through `POST /review/001` with `{"approved":true}` and header `X-Demo-Admin-Token`; it records approval locally **without external transmission**.

## Important production gaps
No actual Meta API, webhook HMAC verification, message delivery, LLM inference, source-grounded retrieval, tenant security, secrets rotation, privacy controls, audit log, durable distributed queues, backups, observability, rate controls or deployment. Demo keys are not production authentication. **Do not deploy as-is**.

A client pilot would require one approved FAQ source, explicit response/handoff policy, a client-provisioned channel, verified permissions, data protection and specified acceptance tests. Provider/API fees are separately agreed.

**Disclosure to employers:** Independently packaged AI-assisted code proof using synthetic data; **not** evidence of previously paid client work. The tests verify only this bounded demonstration.
