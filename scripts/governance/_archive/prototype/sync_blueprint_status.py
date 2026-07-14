# [BLUEPRINT] MOD-INF-005 | scripts/governance/sync_blueprint_status.py | §
# [MODULE] scripts.governance.sync_blueprint_status
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
"""机械强制：construction_plan=phase_2_complete → blueprint.status=Active.

规则
----
    construction_plan.status == 'phase_2_complete' → blueprint.status MUST == 'Active'
    construction_plan.status != 'phase_2_complete' → blueprint.status MAY be 'Draft'

此脚本零人工介入。纯机械映射。

用法
----
    python scripts/governance/sync_blueprint_status.py              # 干跑，不写盘
    python scripts/governance/sync_blueprint_status.py --apply      # 写入修复
    python scripts/governance/sync_blueprint_status.py --json       # JSON 输出
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import json
import os
import sys
from pathlib import Path

import yaml
from _shared.constants import EXIT_PASS, REPO_ROOT as _PROJECT_ROOT

_MODULE_REGISTRY = _PROJECT_ROOT / "docs" / "03_modules" / "module-registry.yaml"
_BLUEPRINT_REGISTRY = _PROJECT_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"


def _safe_read_yaml(path: Path) -> dict:
    """_safe_read_yaml implementation."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _atomic_write_yaml(path: Path, data: dict) -> None:
    """_atomic_write_yaml implementation."""
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def _fix_blueprint_frontmatter(blueprint_dir: Path, expected_status: str) -> bool:
    """检查单个蓝图 frontmatter 的 status 并修复."""
    bp_md = blueprint_dir / "blueprint.md"
    if not bp_md.exists():
        return False

    content = bp_md.read_text(encoding="utf-8")
    lines = content.split("\n")
    changed = False

    for i, line in enumerate(lines):
        if line.strip() == "status: Draft" and expected_status == "Active":
            lines[i] = line.replace("status: Draft", "status: Active")
            changed = True
            break
        if line.strip() == "status: Active" and expected_status == "Draft":
            lines[i] = line.replace("status: Active", "status: Draft")
            changed = True
            break

    if changed:
        tmp = f"{bp_md}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            os.replace(tmp, str(bp_md))
        except Exception:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

    return changed


def analyze() -> list[dict]:
    """返回所有需要修复的条目."""
    reg = _safe_read_yaml(_MODULE_REGISTRY)
    issues: list[dict] = []

    for mod in reg.get("modules", []):
        bp = mod.get("blueprint", {})
        cp = mod.get("construction_plan", {})

        bp_status = bp.get("status", "Draft")
        cp_status = cp.get("status", "")
        mod_id = mod.get("module_id", "?")
        mod_name = mod.get("name", "?")
        bp_dir = _PROJECT_ROOT / "docs" / "03_modules" / (mod.get("layer", "") or "infrastructure_runtime_integration")
        name = mod.get("path", "").split("/")[-1] if mod.get("path") else mod_name
        blueprint_dir = _PROJECT_ROOT / "docs" / "03_modules" / "infrastructure_runtime_integration" / name

        expected = (
            "Active"
            if cp_status in ("phase_2_complete", "completed")
            or (isinstance(cp_status, str) and cp_status.startswith("phase_") and cp_status.endswith("_complete"))
            else "Draft"
        )

        # normalize: "active"→"Active"
        if isinstance(bp_status, str):
            bp_status = bp_status.strip().title()

        if bp_status != expected:
            issues.append(
                {
                    "module_id": mod_id,
                    "name": mod_name,
                    "current": bp_status,
                    "expected": expected,
                    "cp_status": cp_status,
                    "registry_fix": True,  # any mismatch → fix
                    "blueprint_dir": str(blueprint_dir),
                    "blueprint_exists": (blueprint_dir / "blueprint.md").exists(),
                }
            )

    return issues


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = sys.argv[1:]
    apply_mode = "--apply" in args
    json_mode = "--json" in args

    issues = analyze()

    if not issues:
        print("CLEAN: 所有模块 status 与 construction_plan 一致")
        return EXIT_PASS

    fixes_registry = 0
    fixes_blueprint = 0

    # 加载注册表
    reg = _safe_read_yaml(_MODULE_REGISTRY) if apply_mode else None

    for issue in issues:
        mid = issue["module_id"]
        cur = issue["current"]
        exp = issue["expected"]
        cp = issue["cp_status"]
        bp_dir = Path(issue["blueprint_dir"])

        if json_mode:
            print(json.dumps(issue, ensure_ascii=False))
            continue

        label = "REGISTRY+BLUEPRINT" if issue["blueprint_exists"] else "REGISTRY-ONLY"
        print(f"DRIFT  {mid} ({issue['name']})  {cur}→{exp}  cp={cp}  [{label}]")

        if apply_mode:
            if issue["registry_fix"]:
                for mod in reg["modules"]:
                    if mod["module_id"] == mid:
                        mod["blueprint"]["status"] = exp
                        fixes_registry += 1
                        break

            if issue["blueprint_exists"]:
                ok = _fix_blueprint_frontmatter(bp_dir, exp)
                if ok:
                    fixes_blueprint += 1

    if apply_mode:
        if fixes_registry > 0:
            _atomic_write_yaml(_MODULE_REGISTRY, reg)
        print(
            f"\nAPPLIED: {fixes_registry} registry + {fixes_blueprint} blueprint = {fixes_registry + fixes_blueprint} fixes"
        )

    n = len(issues)
    if apply_mode:
        print(f"RESULT: {n} drift(s) fixed → CLEAN")
    else:
        print(f"\n{n} drift(s) found. Re-run with --apply to fix.")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
