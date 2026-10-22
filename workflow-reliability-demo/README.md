# Workflow Reliability Demo — Read-only n8n Inspector

**Independent educational demonstration by Edmon A. Capsa.** Built with AI assistance, manually reviewed and tested locally. **Not a previous paid client case study.**

A Python-standard-library command line tool that reads a **sanitized n8n workflow JSON export** and identifies a few common structural red flags:

- dangling/missing target connections and unknown sources;
- duplicate node names;
- unreachable non-trigger nodes and disabled nodes;
- HTTP nodes whose export does not declare retry/error options (review prompt, not proof of failure);
- create/append operations that warrant a manual duplicate/idempotency check.

It performs **static inspection only**. It does not run workflows, confirm credentials, test live API endpoints, determine n8n server version, or guarantee production reliability.

## Run a fully synthetic demonstration

From this folder:

~~~bash
python workflow_audit.py sample_workflow.json --json
python -m unittest -v test_workflow_audit.py
~~~

The example deliberately contains a missing link to "Missing Alert", an unreachable formatter, a disabled node, and operations needing a manual review. The unit tests exercise five detector behaviors.

**Security:** Never upload live passwords, access tokens, connection credentials, personal customer data, webhook secrets, or production exports without sanitizing. Work on client systems only with explicit owner authorization. Proper production QA also requires runtime logs, safe reproduction, human validation, staging checks, and agreed acceptance criteria.

## Pilot service (proposed, not established track record)

Introductory **$49** for a fixed-scope written audit of **one sanitized n8n workflow up to 15 nodes**, subject to written agreement. Findings and acceptance-test proposals only. Repairs, actual runtime testing, hosting, subscriptions, or deployments are outside this price unless separately agreed. No claims of guaranteed revenue or operational savings.

**Contact:** edmon.capsa5@gmail.com
