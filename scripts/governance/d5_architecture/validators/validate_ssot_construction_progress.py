# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_ssot_construction_progress.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_ssot_construction_progress
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [TTL] permanent
"""
validate_ssot_construction_progress.py — G8 SSoT 一致性门禁强制执行脚本
=========================================================================
检查项：
  G8-C01: frontmatter.construction_progress == blueprint_registry.yaml 同 module_id
  G8-C02: frontmatter.construction_progress == module-registry.yaml 同 module_id
  G8-C03: blueprint-registry == module-registry 交叉一致
  G8-C04: 所有 construction_progress 值在受控词表内

受控词表（对齐 blueprint_registry.yaml _schema）：
  not_started / phase_1_partial / phase_1_complete / phase_2_complete
  / blocked_by_infrastructure / completed / phase_production_complete

用法：
  python validate_ssot_construction_progress.py           # 扫描 + 报告
  python validate_ssot_construction_progress.py --ci      # CI 模式,不一致→exit(1)
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import BLUEPRINTS_DIR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from zephyr.governance.rule_patterns import MODULE_ID_RE  # noqa: E402  # SSoT 治本 2026-07-02 (ARCH-033 Phase 7)
from _shared.walk import iter_files

__manifest__ = """
args: []
description: G8 SSoT一致性门禁——frontmatter↔registry construction_progress三向校验
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

_REPO_ROOT = REPO_ROOT

VALID_PROGRESS = frozenset(
    {
        "not_started",
        "phase_1_partial",
        "phase_1_complete",
        "phase_2_complete",
        "blocked_by_infrastructure",
        "completed",
        "phase_production_complete",
    }
)

BLUEPRINT_REGISTRY_PATH = _REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"
MODULE_REGISTRY_PATH = _REPO_ROOT / "docs" / "03_modules" / "module-registry.yaml"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
PROGRESS_RE = re.compile(r"^construction_progress:\s*(.+)$", re.MULTILINE)
# MODULE_ID_RE 已迁移到 zephyr.governance.rule_patterns（SSoT 治本 2026-07-02, ARCH-033 Phase 7）


def _collect_frontmatter_progress() -> dict[str, str]:
    """_collect_frontmatter_progress implementation."""
    result: dict[str, str] = {}
    for bp_path in iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md"):
        content = bp_path.read_text(encoding="utf-8")
        fm_match = FRONTMATTER_RE.match(content)
        if not fm_match:
            continue
        fm = fm_match.group(1)
        mid_match = MODULE_ID_RE.search(fm)
        prog_match = PROGRESS_RE.search(fm)
        if not mid_match or not prog_match:
            continue
        module_id = mid_match.group(1).strip().strip("\"'")
        progress = prog_match.group(1).strip().strip("\"'")
        result[module_id] = progress
    return result


def _load_blueprint_registry_progress() -> dict[str, str]:
    """_load_blueprint_registry_progress implementation."""
    if not BLUEPRINT_REGISTRY_PATH.exists():
        return {}
    with open(BLUEPRINT_REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    result: dict[str, str] = {}
    for bp in data.get("blueprints", []):
        mid = bp.get("module_id", "")
        prog = bp.get("construction_progress", "")
        if mid and prog:
            result[mid] = prog
    return result


def _load_module_registry_progress() -> dict[str, str]:
    """_load_module_registry_progress implementation."""
    if not MODULE_REGISTRY_PATH.exists():
        return {}
    with open(MODULE_REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    result: dict[str, str] = {}
    for mod in data.get("modules", []):
        mid = mod.get("module_id", "")
        plan = mod.get("construction_plan", {})
        prog = plan.get("status", "") if isinstance(plan, dict) else ""
        if mid and prog:
            result[mid] = prog
    return result


def _check_vocabulary(progress_map: dict[str, str], source_label: str) -> list[str]:
    """_check_vocabulary implementation."""
    errors: list[str] = []
    for mid, prog in progress_map.items():
        if prog not in VALID_PROGRESS:
            errors.append(
                f"G8-C04 [{source_label}] {mid}: construction_progress={prog!r} 不在受控词表 {sorted(VALID_PROGRESS)}"
            )
    return errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="G8 SSoT construction_progress 一致性校验")
    parser.add_argument("--ci", action="store_true", help="CI 模式: 不一致时 exit(1)")
    args = parser.parse_args()

    fm_progress = _collect_frontmatter_progress()
    bp_registry = _load_blueprint_registry_progress()
    mod_registry = _load_module_registry_progress()

    all_module_ids = set(fm_progress.keys()) | set(bp_registry.keys()) | set(mod_registry.keys())

    errors: list[str] = []
    warnings: list[str] = []

    # G8-C04: vocabulary check for all three sources
    errors.extend(_check_vocabulary(fm_progress, "frontmatter"))
    errors.extend(_check_vocabulary(bp_registry, "blueprint-registry"))
    errors.extend(_check_vocabulary(mod_registry, "module-registry"))

    for mid in sorted(all_module_ids):
        fm_val = fm_progress.get(mid)
        bp_val = bp_registry.get(mid)
        mod_val = mod_registry.get(mid)

        # Skip C-track blocked modules
        if bp_val == "blocked_by_infrastructure" or fm_val == "blocked_by_infrastructure":
            continue

        # G8-C01: frontmatter vs blueprint-registry
        if fm_val is not None and bp_val is not None and fm_val != bp_val:
            errors.append(f"G8-C01 {mid}: frontmatter={fm_val!r} != blueprint-registry={bp_val!r}")

        # G8-C02: frontmatter vs module-registry
        if fm_val is not None and mod_val is not None and fm_val != mod_val:
            errors.append(f"G8-C02 {mid}: frontmatter={fm_val!r} != module-registry={mod_val!r}")

        # G8-C03: blueprint-registry vs module-registry
        if bp_val is not None and mod_val is not None and bp_val != mod_val:
            errors.append(f"G8-C03 {mid}: blueprint-registry={bp_val!r} != module-registry={mod_val!r}")

        # Warn about missing entries
        if fm_val is not None and bp_val is None:
            warnings.append(f"{mid}: 仅在 frontmatter 中存在，blueprint-registry 未登记")
        if fm_val is not None and mod_val is None:
            warnings.append(f"{mid}: 仅在 frontmatter 中存在，module-registry 未登记")

    total = len(errors) + len(warnings)
    if errors:
        print(f"[G8] {len(errors)} 错误, {len(warnings)} 警告 (共 {total})")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")
        if args.ci:
            return EXIT_FINDINGS
    elif warnings:
        print(f"[G8] CLEAN — 0 错误, {len(warnings)} 警告")
        for w in warnings:
            print(f"  WARN:  {w}")
    else:
        print(f"[G8] CLEAN — 扫描 {len(all_module_ids)} 模块, 0 矛盾")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
