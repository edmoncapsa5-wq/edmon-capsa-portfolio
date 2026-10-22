# Static Workflow Audit — Synthetic Example

**Status:** Demonstration only. The workflow and all data are fabricated. No client workflow was accessed or repaired.

**Workflow:** `DEMO ONLY - webhook lead intake with planted faults`  
**Nodes inspected:** 5  
**Flagged observations:** 6 (1 error, 3 warnings, 2 informational review items)

## Observations

| Severity | Code | Node | What to check |
|---|---|---|---|
| ERROR | `DANGLING_CONNECTION` | Lookup API | Connection points to missing node: 'Missing Alert' |
| WARNING | `NETWORK_FAILURE_PATH_UNSPECIFIED` | Lookup API | Review timeout, retry, failure routing and observability; static export cannot prove the runtime behavior |
| WARNING | `NO_INCOMING_PATH` | Old Route | Non-trigger node is unreachable via declared connections |
| WARNING | `NO_INCOMING_PATH` | Orphan Formatter | Non-trigger node is unreachable via declared connections |
| INFO | `DISABLED_NODE` | Old Route | Node is disabled; check whether this is intentional |
| INFO | `WRITE_OPERATION_REVIEW` | Create Row | Verify idempotency, duplicate prevention and partial-failure behavior manually |

## Proposed remediation and acceptance checks

1. Remove the invalid `Lookup API → Missing Alert` edge or restore the intended destination node. Re-run the static scanner: `DANGLING_CONNECTION` should disappear.
2. For `Lookup API`, document expected HTTP status codes, timeouts, retries, rate limits and an explicit exception path. Simulate a 500 response and a timeout in a controlled test environment.
3. Confirm whether `Old Route` and `Orphan Formatter` should exist. Remove dead branches or connect intended behavior, then rerun the check.
4. For `Create Row`, specify a stable idempotency key and test that replaying identical sample payloads does not produce duplicated records.
5. Capture a test matrix including valid data, missing required fields, duplicate events, API failure and recovery, with expected versus actual results.

## What this report does not establish

This is not proof the supplied workflow has a real business impact or is production-ready. The tool only inspects export structure and heuristics; it cannot validate credentials, webhook URLs, account quotas, live execution, authorization, security, data loss, or client-specific business rules. Network and write-operation findings are *review prompts*, not verified defects.

## Reproduce the results

```bash
python workflow_audit.py sample_workflow.json --json
python -m unittest -v test_workflow_audit.py
```

Written as an independent AI-assisted portfolio demonstration, October 22, 2026.
