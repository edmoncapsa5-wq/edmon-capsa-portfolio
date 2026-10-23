#!/usr/bin/env python3
"""Locate references to selected Oct 23 2026 retired OpenAI API model IDs in a sanitized n8n export.

Textual inspection, not verification of active execution or API model availability.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Official list: https://developers.openai.com/api/docs/deprecations
RETIRED_MODELS = frozenset({
    "gpt-3.5-turbo-0125", "gpt-4-0613", "gpt-4-1106-preview",
    "gpt-4-turbo", "gpt-4.1-nano", "gpt-4o-2024-05-13",
    "gpt-image-1", "o1-2024-12-17", "o1-pro-2025-03-19",
    "o3-mini-2025-01-31", "o4-mini-2025-04-16",
    "ft-gpt-3.5-turbo", "ft-gpt-4", "ft-gpt-4.1-nano-2025-04-14",
    "ft-babbage-002", "ft-davinci-002", "ft-o4-mini-2025-04-16"
})
# Avoid confusing a retired alias with a different longer model snapshot.
MODEL_PATTERN = re.compile(r"(?<![A-Za-z0-9_-])(?:" +
    "|".join(re.escape(n) for n in sorted(RETIRED_MODELS, key=len, reverse=True)) +
    r")(?![A-Za-z0-9_-])")

def scan(workflow):
    if not isinstance(workflow, dict):
        raise ValueError("top-level workflow must be a JSON object")
    matches = []
    def walk(value, path, node_name=None):
        if isinstance(value, dict):
            node_name = str(value.get("name", node_name)) if "name" in value else node_name
            for key, child in value.items():
                walk(child, f"{path}.{key}", node_name)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}[{i}]", node_name)
        elif isinstance(value, str):
            for m in MODEL_PATTERN.finditer(value):
                matches.append({
                    "model": m.group(0), "json_path": path,
                    "node": node_name or "",
                    "status": "reference detected; active use unverified"
                })
    walk(workflow, "$", None)
    return matches

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
        "reference_count": len(hits), "matches": hits,
        "note": "Static references, not verified API usage. Check expressions, config, tools, and real executions before migration."
    }, indent=2))
    return 1 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
