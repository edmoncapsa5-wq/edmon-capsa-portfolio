#!/usr/bin/env python3
"""Read-only static checker for sanitized n8n workflow export JSON.

This does not execute workflows, validate credentials, or guarantee runtime safety.
Python standard library only. MIT-licensed educational demonstration.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def inspect(workflow: dict) -> list[dict]:
    findings: list[dict] = []
    def add(level: str, code: str, details: str, node: str = ""):
        findings.append({"severity": level, "code": code, "node": node, "details": details})

    nodes = workflow.get("nodes", [])
    if not isinstance(nodes, list):
        raise ValueError("'nodes' must be an array")
    conns = workflow.get("connections", {})
    if not isinstance(conns, dict):
        raise ValueError("'connections' must be an object")
    names = [n.get("name", "") for n in nodes if isinstance(n, dict)]
    duplicates = {name for name, count in Counter(names).items() if count > 1}
    for name in sorted(duplicates):
        add("error", "DUPLICATE_NAME", "Node names should be unique", name)
    known = set(names)
    incoming = defaultdict(int)
    for source, types in conns.items():
        if source not in known:
            add("error", "UNKNOWN_SOURCE", "Connection references missing source node", source)
        if not isinstance(types, dict):
            add("error", "MALFORMED_CONNECTION", "Connection branches must be an object", source)
            continue
        for outputs in types.values():
            if not isinstance(outputs, list):
                add("error", "MALFORMED_CONNECTION", "Connection outputs must be an array", source)
                continue
            for port in outputs:
                if not isinstance(port, list):
                    continue
                for edge in port:
                    if not isinstance(edge, dict):
                        continue
                    target = edge.get("node")
                    if target not in known:
                        add("error", "DANGLING_CONNECTION", f"Connection points to missing node: {target!r}", source)
                    else:
                        incoming[target] += 1
    for node in nodes:
        if not isinstance(node, dict):
            add("error", "MALFORMED_NODE", "Node must be an object")
            continue
        name = node.get("name", "(unnamed)")
        kind = str(node.get("type", ""))
        if node.get("disabled"):
            add("info", "DISABLED_NODE", "Node is disabled; check whether this is intentional", name)
        is_trigger = kind.lower().endswith("trigger") or kind.lower().endswith(".webhook") or kind.lower().endswith(".manualtrigger")
        if not is_trigger and not incoming.get(name, 0):
            add("warning", "NO_INCOMING_PATH", "Non-trigger node is unreachable via declared connections", name)
        params = node.get("parameters", {})
        if isinstance(params, dict) and "httprequest" in kind.lower():
            if not node.get("retryOnFail") and not node.get("onError"):
                add("warning", "NETWORK_FAILURE_PATH_UNSPECIFIED", "Review timeout, retry, failure routing and observability; static export cannot prove the runtime behavior", name)
        if isinstance(params, dict):
            operation = str(params.get("operation", "")).lower()
            if any(word in operation for word in ("append", "create", "insert")):
                add("info", "WRITE_OPERATION_REVIEW", "Verify idempotency, duplicate prevention and partial-failure behavior manually", name)
    if nodes and not any(str(n.get("type", "")).lower().endswith(("trigger", ".webhook")) for n in nodes if isinstance(n, dict)):
        add("info", "TRIGGER_REVIEW", "No obvious trigger node; may be a called subworkflow or use a different node type")
    return sorted(findings, key=lambda x: ({"error":0, "warning":1, "info":2}[x["severity"]], x["code"], x["node"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path, help="Sanitized n8n export JSON; never upload credentials")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable findings")
    args = parser.parse_args()
    try:
        payload = json.loads(args.workflow.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Workflow JSON must be an object")
        findings = inspect(payload)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Audit input error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"workflow": payload.get("name", ""), "findings": findings}, indent=2))
    else:
        print(f"Static audit: {payload.get('name', '(unnamed)')} — {len(findings)} findings")
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['code']} | {f['node']}: {f['details']}")
    return 1 if any(f["severity"] == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
