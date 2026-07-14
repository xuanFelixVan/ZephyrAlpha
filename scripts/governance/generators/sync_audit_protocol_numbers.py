# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/sync_audit_protocol_numbers.py | §
# [MODULE] scripts.governance.generators.sync_audit_protocol_numbers
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
#!/usr/bin/env python3
"""sync_audit_protocol_numbers.py — 从 SSoT 注册表自动同步审计协议中的硬编码数字。

用法:
    python scripts/governance/generators/sync_audit_protocol_numbers.py          # 同步
    python scripts/governance/generators/sync_audit_protocol_numbers.py --check   # 仅检查漂移

原理:
    audit-protocol.md 中用 <!-- AUTO_SYNC:key:old_value --> 占位符标记需要自动同步的数字。
    本脚本从 4 个 SSoT 源读取最新值，替换占位符中的数字。
    同时扫描正文中与 key 关联的裸数字并同步替换。

SSoT 源:
    - script_manifest.yaml  → total_scripts
    - gate_registry.yaml    → total_gates
    - registry-master-index.yaml → total_registries
    - .pre_commit-config.yaml   → precommit_hooks

占位符格式:
    <!-- AUTO_SYNC:total_scripts:201 -->  →  <!-- AUTO_SYNC:total_scripts:177 -->
    数字部分会被自动替换，key 和注释结构不变。

正文裸数字映射:
    每个占位符行之后的同一逻辑段落中，与旧值相同的数字也会被替换为新值。
    changelog 区域（§10 修订记录）中的数字不会被替换。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: sync_audit_protocol_numbers.py — 从 SSoT 注册表自动同步审计协议中的硬编码数字。
dimensions:
- D1
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import os
import re
import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

SSOT_PATHS = {
    "total_scripts": REPO_ROOT / "scripts" / "governance" / "script_manifest.yaml",
    "total_gates": REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "gate_registry.yaml",
    "total_registries": REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "registry-master-index.yaml",
    "precommit_hooks": REPO_ROOT / ".pre-commit-config.yaml",
}

AUDIT_PROTOCOL = REPO_ROOT / "docs" / "01_policies_and_standards" / "governance" / "compliance" / "audit-protocol.md"

PLACEHOLDER_RE = re.compile(r"<!--\s*AUTO_SYNC:(\w+):(\d+)\s*-->")

CHANGELOG_HEADER = "## 10. 修订记录"


def read_ssot_values() -> dict[str, int]:
    """read_ssot_values implementation."""
    values: dict[str, int] = {}

    p = SSOT_PATHS["total_scripts"]
    if p.exists():
        with open(p, encoding="utf-8") as f:
            m = yaml.safe_load(f)
        values["total_scripts"] = m.get("total_scripts", len(m.get("scripts", [])))

    p = SSOT_PATHS["total_gates"]
    if p.exists():
        with open(p, encoding="utf-8") as f:
            g = yaml.safe_load(f)
        values["total_gates"] = g.get("total_gates", len(g.get("gates", [])))

    p = SSOT_PATHS["total_registries"]
    if p.exists():
        with open(p, encoding="utf-8") as f:
            r = yaml.safe_load(f)
        values["total_registries"] = r.get("total_registries", 0)

    p = SSOT_PATHS["precommit_hooks"]
    if p.exists():
        with open(p, encoding="utf-8") as f:
            pc = yaml.safe_load(f)
        values["precommit_hooks"] = sum(len(repo.get("hooks", [])) for repo in pc.get("repos", []))

    return values


def sync(check_only: bool = False) -> int:
    """sync implementation."""
    ssot = read_ssot_values()
    if not AUDIT_PROTOCOL.exists():
        print(f"ERROR: {AUDIT_PROTOCOL} not found")
        return EXIT_ERROR
    text = AUDIT_PROTOCOL.read_text(encoding="utf-8")
    drifts: list[tuple[str, int, int]] = []

    def replacer(m: re.Match) -> str:
        """replacer implementation."""
        key = m.group(1)
        old_val = int(m.group(2))
        new_val = ssot.get(key)
        if new_val is None:
            return m.group(0)
        if old_val != new_val:
            drifts.append((key, old_val, new_val))
        return f"<!-- AUTO_SYNC:{key}:{new_val} -->"

    new_text = PLACEHOLDER_RE.sub(replacer, text)

    for key, old_val, new_val in drifts:
        new_text = _replace_bare_numbers(new_text, key, old_val, new_val)

    if not drifts:
        print("OK — all AUTO_SYNC placeholders match SSoT values")
        return EXIT_PASS
    print(f"DRIFT — {len(drifts)} placeholder(s) out of sync:")
    for key, old, new in drifts:
        print(f"  {key}: {old} -> {new}")

    if check_only:
        return EXIT_FINDINGS
    atomic_write_safe(AUDIT_PROTOCOL, new_text)
    print(f"SYNCED — {AUDIT_PROTOCOL.name} updated")
    return EXIT_PASS


def _replace_bare_numbers(text: str, key: str, old_val: int, new_val: int) -> str:
    """_replace_bare_numbers implementation."""
    changelog_idx = text.find(CHANGELOG_HEADER)
    body = text[:changelog_idx] if changelog_idx >= 0 else text
    tail = text[changelog_idx:] if changelog_idx >= 0 else ""

    old_s = str(old_val)
    new_s = str(new_val)
    body = body.replace(old_s, new_s)

    return body + tail


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Sync audit-protocol.md numbers from SSoT registries")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check only, do not write",
    )
    args = parser.parse_args()
    return sync(check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
