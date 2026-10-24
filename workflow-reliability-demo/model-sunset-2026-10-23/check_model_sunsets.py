#!/usr/bin/env python3
"""Find exact references to OpenAI API model IDs scheduled for shutdown Oct 23, 2026.

Read-only, static inspection of a sanitized n8n JSON export. Does not execute nodes,
verify API responses, inspect connected credentials or certify production readiness.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Names and aliases transcribed from:
# https://developers.openai.com/api/docs/deprecations
# Section "2026-04-22: Legacy GPT model snapshots" (October 23 shutdown).
# Keep exact aliases: e.g. gpt-4-turbo-2024-04-09 also retired.
RETIRED_MODELS = frozenset({
    "gpt-3.5-turbo-0125", "gpt-3.5-turbo", "gpt-3.5-turbo-completions",
    "gpt-4-0613", "gpt-4", "gpt-4-0613-completions", "gpt-4-completions",
    "gpt-4-1106-preview", "gpt-4-turbo", "gpt-4-turbo-2024-04-09",
    "gpt-4-turbo-completions", "gpt-4.1-nano", "gpt-4.1-nano-2025-04-14",
    "gpt-4o-2024-05-13", "gpt-image-1",
    "o1-2024-12-17", "o1", "o1-pro-2025-03-19", "o1-pro",
    "o3-mini-2025-01-31", "o3-mini", "o4-mini-2025-04-16", "o4-mini",
    "ft-o4-mini-2025-04-16", "ft-gpt-3.5-turbo", "ft-gpt-4",
    "ft-gpt-4.1-nano-2025-04-14", "ft-babbage-002", "ft-davinci-002",
})
# Match whole model IDs, not prefixes embedded in unrelated longer versions.
MODEL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_-])(?:" +
    "|".join(re.escape(v) for v in sorted(RETIRED_MODELS, key=len, reverse=True)) +
    r")(?![A-Za-z0-9_-])"
)

def scan(workflow):
    if not isinstance(workflow, dict):
        raise ValueError("top-level workflow must be a JSON object")
    findings = []
    def walk(value, path, node_name=None):
        if isinstance(value, dict):
            current_name = str(value["name"]) if isinstance(value.get("name"), str) else node_name
            for key, child in value.items():
                walk(child, f"{path}.{key}", current_name)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}[{i}]", node_name)
        elif isinstance(value, str):
            for match in MODEL_PATTERN.finditer(value):
                findings.append({
                    "model": match.group(0),
                    "json_path": path,
                    "node": node_name or "",
                    "status": "text reference detected; active runtime use unverified"
                })
    walk(workflow, "$")
    return findings

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path, help="sanitized n8n workflow JSON export")
    args = parser.parse_args(argv)
    try:
        workflow = json.loads(args.workflow.read_text(encoding="utf-8"))
        hits = scan(workflow)
    except (ValueError, OSError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2
    print(json.dumps({
        "reference_count": len(hits),
        "matches": hits,
        "note": "Text search only. Verify the official list, actual execution, configuration, credentials, and migration tests before changes."
    }, indent=2))
    return 1 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
