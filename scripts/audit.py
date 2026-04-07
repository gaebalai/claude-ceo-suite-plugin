#!/usr/bin/env python3
"""Conformance audit for Claude CEO-Suite Plugin command files.

Verifies that every command file under commands/ adheres to the
conventions defined in v1.4 (Consistency Pass) and documented in
AUDIT.md and CONTRIBUTING.md.

Usage:
    python3 scripts/audit.py            # report only
    python3 scripts/audit.py --matrix   # also print the conformance matrix

Exit code 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD_DIR = os.path.join(ROOT, "commands")

# Each check is (key, label, predicate). The predicate receives the file
# content as a string and returns True if the check passes.
COMMAND_CHECKS = [
    ("frontmatter",
     "Frontmatter (description + arguments)",
     lambda c: c.startswith("---\n")
               and "description:" in c[:500]
               and "arguments:" in c[:500]),
    ("trust_boundary",
     "## Trust boundary section",
     lambda c: "## Trust boundary" in c),
    ("mode_detection",
     "## Mode detection section",
     lambda c: "## Mode detection" in c),
    ("question_mode",
     "## Question Mode section",
     lambda c: "## Question Mode" in c),
    ("review_mode",
     "## Review Mode section",
     lambda c: "## Review Mode" in c),
    ("scope_args",
     "Argument convention is scope-keyword (no owner/repo)",
     lambda c: "owner/repo" not in c),
    ("cross_reference",
     "Cross-references peer roles",
     lambda c: "cross-reference" in c.lower()),
    ("phd_panel_ref",
     "References PhD Panel plugin",
     lambda c: "claude-phd-panel" in c),
    ("ai_disclaimer",
     "AI-generated advice disclaimer footer",
     lambda c: "AI-generated advice" in c),
    ("analysis_only",
     "Analysis-only guarantee (Do NOT execute / move)",
     lambda c: "Do NOT execute" in c or "Do NOT move" in c),
]

# Role commands are full executive perspectives subject to all conventions.
ROLE_COMMANDS = {
    "ceo.md", "cto.md", "pm.md", "cdo.md", "cso.md",
    "clo.md", "coo.md", "cmo.md", "caio.md", "cfo.md",
    "cio.md", "qa-lead.md", "dx-lead.md",
}

# Utility commands are maintainer tools (e.g., the audit gate itself).
# They share the safety conventions (Trust boundary, AI disclaimer) but
# are exempt from role-specific conventions (Question/Review modes,
# Top 3 cross-references, PhD Panel cross-references, scope-keyword args).
UTILITY_COMMANDS = {
    "audit.md",
}

# Router commands are user-facing dispatchers that delegate to role
# commands rather than performing analysis themselves (e.g., /ask).
# They must satisfy nearly all role conventions — they are user-facing
# and produce analysis output via the role they adopt — but they have
# no Review Mode by design (reviews live on the individual role
# commands and on /ceo).
ROUTER_COMMANDS = {
    "ask.md",
}

EXPECTED_COMMANDS = ROLE_COMMANDS | UTILITY_COMMANDS | ROUTER_COMMANDS

# Subset of COMMAND_CHECKS that applies to utility commands.
UTILITY_CHECK_KEYS = {"frontmatter", "trust_boundary", "ai_disclaimer"}

# Subset of COMMAND_CHECKS that applies to router commands.
# Same as role commands minus review_mode.
ROUTER_CHECK_KEYS = {
    "frontmatter", "trust_boundary", "mode_detection", "question_mode",
    "scope_args", "cross_reference", "phd_panel_ref", "ai_disclaimer",
    "analysis_only",
}


def audit_commands() -> tuple[dict[str, dict[str, bool | None]], list[str]]:
    """Run all checks against every command file. Returns (results, errors)."""
    results: dict[str, dict[str, bool | None]] = {}
    errors: list[str] = []

    found = {f for f in os.listdir(CMD_DIR) if f.endswith(".md")}
    missing = EXPECTED_COMMANDS - found
    extra = found - EXPECTED_COMMANDS
    if missing:
        errors.append(f"Missing expected command files: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected command files: {sorted(extra)}")

    for fname in sorted(found):
        with open(os.path.join(CMD_DIR, fname)) as f:
            content = f.read()
        if fname in UTILITY_COMMANDS:
            applicable: set[str] = set(UTILITY_CHECK_KEYS)
        elif fname in ROUTER_COMMANDS:
            applicable = set(ROUTER_CHECK_KEYS)
        else:
            applicable = {key for key, _, _ in COMMAND_CHECKS}
        per_file: dict[str, bool | None] = {}
        for key, _, predicate in COMMAND_CHECKS:
            per_file[key] = predicate(content) if key in applicable else None
        results[fname] = per_file

    return results, errors


def audit_metadata() -> list[str]:
    """Run repository-level metadata checks. Returns list of failure messages."""
    errors: list[str] = []
    plugin_path = os.path.join(ROOT, ".claude-plugin", "plugin.json")
    market_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")

    with open(plugin_path) as f:
        plugin = json.load(f)
    with open(market_path) as f:
        market = json.load(f)

    plugin_version = plugin.get("version")
    market_version = market.get("plugins", [{}])[0].get("version")
    if plugin_version != market_version:
        errors.append(
            f"plugin.json version ({plugin_version}) != "
            f"marketplace.json version ({market_version})"
        )

    for required in ("SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
                     "README.md", "README.md", "AUDIT.md"):
        if not os.path.exists(os.path.join(ROOT, required)):
            errors.append(f"Missing required document: {required}")

    return errors


def render_matrix(results: dict[str, dict[str, bool | None]]) -> str:
    headers = ["Command"] + [label for _, label, _ in COMMAND_CHECKS]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join([" :--- "] + [" :-: " for _ in COMMAND_CHECKS]) + "|")
    for fname in sorted(results):
        cells = ["`/" + fname.replace(".md", "") + "`"]
        for key, _, _ in COMMAND_CHECKS:
            value = results[fname][key]
            if value is None:
                cells.append("—")
            elif value:
                cells.append("✅")
            else:
                cells.append("❌")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    show_matrix = "--matrix" in sys.argv
    results, structural_errors = audit_commands()
    metadata_errors = audit_metadata()

    failures: list[str] = list(structural_errors)
    total_checks = 0
    for fname, checks in results.items():
        for key, label, _ in COMMAND_CHECKS:
            value = checks[key]
            if value is None:
                continue
            total_checks += 1
            if not value:
                failures.append(f"{fname}: {label}")
    total_checks += 1 + 6  # version sync + 6 required documents
    failures.extend(metadata_errors)

    if show_matrix:
        print(render_matrix(results))
        print()

    if failures:
        print("AUDIT FAILED:")
        for f in failures:
            print(f"  ❌ {f}")
        return 1

    role_count = sum(1 for f in results if f in ROLE_COMMANDS)
    util_count = sum(1 for f in results if f in UTILITY_COMMANDS)
    router_count = sum(1 for f in results if f in ROUTER_COMMANDS)
    print(f"✅ All {total_checks} conformance checks passed "
          f"({role_count} role commands × {len(COMMAND_CHECKS)} checks "
          f"+ {util_count} utility commands × {len(UTILITY_CHECK_KEYS)} checks "
          f"+ {router_count} router commands × {len(ROUTER_CHECK_KEYS)} checks "
          f"+ metadata).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
