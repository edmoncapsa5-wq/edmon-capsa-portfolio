# OpenAI API model shutdown reference scanner (Oct 23, 2026)

**Independent AI-assisted demonstration, not a production validation or a client case study.**

OpenAI's [official deprecations](https://developers.openai.com/api/docs/deprecations) identify several API model shutdowns on October 23, 2026. This standard-library Python tool scans a **sanitized n8n JSON export** for textual references to exact model IDs. This version covers all exact model IDs and aliases listed in the October 23, 2026 official model shutdown table, including gpt-4-turbo-2024-04-09, which the original version wrongly excluded. A match is **not proof of an active model invocation**: the reference could be in comments, disabled nodes, expressions or documentation. It does not evaluate n8n expressions or test live API calls.

## Run

```bash
python -m unittest -v test_model_sunsets.py
python check_model_sunsets.py example_redacted.json
```

Expected: eight passing tests, two synthetic model references. Exit code 1 means references found, 0 means none found, 2 means input error.

## Review a match

Check whether the node is actually executed. Consult the live official deprecation documentation for model replacements. Validate response structure, token usage, cost, tool calling, failure behavior and downstream effects in staging before any authorized migration.

## Proposed diagnostic

$49 fixed scope: one sanitized n8n workflow export, up to 15 nodes, written findings and five proposed acceptance scenarios. Live API calls, implementation, production deployment and certification are excluded. Repairs can be separately quoted after scope review. This is proposed introductory pricing, not evidence of prior client delivery.
