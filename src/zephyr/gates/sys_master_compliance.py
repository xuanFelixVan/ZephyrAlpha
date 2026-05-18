# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.gates.sys_master_compliance

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
SYS-MASTER-001 Compliance Checker

依据：SYS-MASTER-CMP gate——系统总蓝图合规门禁
验证：蓝图存在/冷启动引用/依赖完整性/进度一致性/规则无回归/crosscheck健康

用法：python -m zephyr.gates.sys_master_compliance [--json]
exit: 0=pass, 1=findings
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SYS_MASTER_PATH = PROJECT_ROOT / "docs" / "03_modules" / "_sys-master" / "blueprint.md"
MOD_MASTER_PATH = PROJECT_ROOT / "docs" / "03_modules" / "_master-blueprint" / "blueprint.md"
PROJECT_RULES = PROJECT_ROOT / ".trae" / "rules" / "project_rules.md"
BLUEPRINT_REGISTRY = PROJECT_ROOT / "docs" / "03_modules" / "blueprint-registry.yaml"
MODULE_REGISTRY = PROJECT_ROOT / "docs" / "03_modules" / "module-registry.yaml"
GATE_REGISTRY = PROJECT_ROOT / "src" / "zephyr" / "gates" / "_registry.yaml"
CROSSCHECK_SCRIPT = PROJECT_ROOT / "scripts" / "governance" / "crosscheck_sys_master_deps.py"


def extract_frontmatter(filepath: Path) -> dict:
    text = filepath.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    if not text.startswith("---"):
        return {}
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def check_blueprint_existence() -> list[dict]:
    results = []
    for label, path in [("SYS-MASTER-001", SYS_MASTER_PATH), ("MOD-MASTER-001", MOD_MASTER_PATH)]:
        ok = path.exists() and path.is_file()
        results.append({
            "check_id": "SYS-C00",
            "label": f"{label} blueprint_exists",
            "status": "PASS" if ok else "FAIL",
            "detail": str(path.relative_to(PROJECT_ROOT)) if ok else f"{label} MISSING",
        })
    return results


def check_cold_start_integration() -> list[dict]:
    if not PROJECT_RULES.exists():
        return [{"check_id": "SYS-C01", "label": "cold_start_integration", "status": "FAIL",
                  "detail": "project_rules.md MISSING"}]
    content = PROJECT_RULES.read_text(encoding="utf-8")
    has_sys_master = "SYS-MASTER-001" in content or "_sys-master" in content
    in_cold_start = False
    cold_start_section = re.search(r"STEP 1.*?STEP 5", content, re.DOTALL)
    if cold_start_section:
        section_text = cold_start_section.group(0)
        in_cold_start = "SYS-MASTER" in section_text or "_sys-master" in section_text
    status = "PASS" if in_cold_start else ("WARN" if has_sys_master else "FAIL")
    return [{"check_id": "SYS-C01", "label": "cold_start_integration",
             "status": status,
             "detail": "SYS-MASTER-001 referenced in cold start sequence" if in_cold_start
             else "SYS-MASTER-001 referenced in rules but NOT in cold start sequence" if has_sys_master
             else "SYS-MASTER-001 not referenced anywhere in project_rules.md"}]


def check_depends_on_integrity() -> list[dict]:
    fm = extract_frontmatter(SYS_MASTER_PATH)
    if not fm:
        return [{"check_id": "SYS-C02", "label": "depends_on_integrity", "status": "FAIL",
                  "detail": "Cannot parse SYS-MASTER-001 frontmatter"}]
    deps = fm.get("depends_on", [])
    has_mod_master = any(
        d.get("target", "") == "MOD-MASTER-001" for d in deps
    ) if isinstance(deps, list) else False
    return [{"check_id": "SYS-C02", "label": "depends_on_integrity",
             "status": "PASS" if has_mod_master else "FAIL",
             "detail": "MOD-MASTER-001 found in depends_on" if has_mod_master else "MOD-MASTER-001 NOT in depends_on"}]


def check_construction_progress_consistency() -> list[dict]:
    VALID_PROGRESS_VALUES = {
        "not_started", "in_progress", "planning", "design",
        "phase_0_complete", "phase_0_completed",
        "phase_1_complete", "phase_1_partial", "phase_1_scaffold_partial",
        "phase_2_complete",
        "phase_3_complete",
        "phase_4_complete",
        "phase_9_complete", "phase_14_early_bird",
        "completed", "active", "operational",
        "deprecated", "backlog", "blocked_by_infrastructure",
        "blueprint_complete", "design_complete",
    }
    results = []
    for target_id, target_path, fm_key in [
        ("SYS-MASTER-001", SYS_MASTER_PATH, "construction_progress"),
        ("MOD-MASTER-001", MOD_MASTER_PATH, "construction_progress"),
    ]:
        if not target_path.exists():
            results.append({
                "check_id": "SYS-C03",
                "label": f"{target_id} construction_progress_consistency",
                "status": "FAIL",
                "detail": f"{target_id} blueprint MISSING, cannot verify consistency",
            })
            continue
        fm = extract_frontmatter(target_path)
        fm_progress = fm.get(fm_key, "unknown")

        bp_reg = {}
        mod_reg = {}
        if BLUEPRINT_REGISTRY.exists():
            bp_reg = yaml.safe_load(BLUEPRINT_REGISTRY.read_text(encoding="utf-8")) or {}
        if MODULE_REGISTRY.exists():
            mod_reg = yaml.safe_load(MODULE_REGISTRY.read_text(encoding="utf-8")) or {}

        bp_progress = "unknown"
        for bp in bp_reg.get("blueprints", []):
            if bp.get("module_id") == target_id:
                bp_progress = bp.get("construction_progress", "unknown")
                break

        mod_progress = "unknown"
        for mod in mod_reg.get("modules", []):
            if mod.get("module_id") == target_id:
                mod_progress = mod.get("construction_plan", {}).get("status", "unknown")
                break

        all_match = fm_progress == bp_progress == mod_progress
        fm_valid = fm_progress in VALID_PROGRESS_VALUES
        if not fm_valid:
            results.append({
                "check_id": "SYS-C03",
                "label": f"{target_id} construction_progress_consistency",
                "status": "FAIL",
                "detail": f"frontmatter={fm_progress} (INVALID), blueprint-registry={bp_progress}, module-registry={mod_progress}",
            })
        elif not all_match:
            results.append({
                "check_id": "SYS-C03",
                "label": f"{target_id} construction_progress_consistency",
                "status": "FAIL",
                "detail": f"frontmatter={fm_progress}, blueprint-registry={bp_progress}, module-registry={mod_progress}",
            })
        else:
            results.append({
                "check_id": "SYS-C03",
                "label": f"{target_id} construction_progress_consistency",
                "status": "PASS",
                "detail": f"frontmatter={fm_progress}, blueprint-registry={bp_progress}, module-registry={mod_progress}",
            })
    return results


def check_ai_rules_count() -> list[dict]:
    fm = extract_frontmatter(SYS_MASTER_PATH)
    ai_role = fm.get("ai_role_instruction", "")
    if isinstance(ai_role, str):
        rules = re.findall(r"\(\d+\)", ai_role)
        count = len(rules)
    else:
        count = 0
    status = "PASS" if count >= 76 else "FAIL"
    return [{"check_id": "SYS-C04", "label": "ai_rules_count",
             "status": status,
             "detail": f"{count} numbered rules found (minimum required: 76)"}]


def check_gate_registry_entry() -> list[dict]:
    if not GATE_REGISTRY.exists():
        return [{"check_id": "SYS-C05", "label": "gate_registry_entry", "status": "FAIL",
                  "detail": "gate _registry.yaml MISSING"}]
    content = GATE_REGISTRY.read_text(encoding="utf-8")
    has_entry = "SYS-MASTER-CMP" in content
    return [{"check_id": "SYS-C05", "label": "gate_registry_entry",
             "status": "PASS" if has_entry else "FAIL",
             "detail": "SYS-MASTER-CMP found in gate registry" if has_entry else "SYS-MASTER-CMP NOT in gate registry"}]


def check_version_consistency() -> list[dict]:
    results = []
    for target_id, target_path in [
        ("SYS-MASTER-001", SYS_MASTER_PATH),
        ("MOD-MASTER-001", MOD_MASTER_PATH),
    ]:
        if not target_path.exists():
            results.append({
                "check_id": "SYS-C07",
                "label": f"{target_id} version_consistency",
                "status": "FAIL",
                "detail": f"{target_id} blueprint MISSING, cannot verify version",
            })
            continue
        fm = extract_frontmatter(target_path)
        fm_version = fm.get("version", "unknown")

        bp_reg = {}
        mod_reg = {}
        if BLUEPRINT_REGISTRY.exists():
            bp_reg = yaml.safe_load(BLUEPRINT_REGISTRY.read_text(encoding="utf-8")) or {}
        if MODULE_REGISTRY.exists():
            mod_reg = yaml.safe_load(MODULE_REGISTRY.read_text(encoding="utf-8")) or {}

        bp_version = "unknown"
        for bp in bp_reg.get("blueprints", []):
            if bp.get("module_id") == target_id:
                bp_version = bp.get("version", "unknown")
                break

        mod_version = "unknown"
        for mod in mod_reg.get("modules", []):
            if mod.get("module_id") == target_id:
                mod_version = mod.get("blueprint", {}).get("version", "unknown")
                break

        all_match = fm_version == bp_version == mod_version
        results.append({
            "check_id": "SYS-C07",
            "label": f"{target_id} version_consistency",
            "status": "PASS" if all_match else "FAIL",
            "detail": f"frontmatter={fm_version}, blueprint-registry={bp_version}, module-registry={mod_version}",
        })
    return results


def check_sli_data_sources() -> list[dict]:
    results = []
    sli_sources = [
        ("SLI-01", "E2E AI 请求延迟", "zephyr.feedback_loop.slo_manager", "SLOManager"),
        ("SLI-02", "蓝图读取耗时", "zephyr.context_engine.dispatch_table", "SystemDispatch"),
        ("SLI-03", "门禁执行总延迟", "zephyr.gates.gate_engine", "GateEngine"),
        ("SLI-04", "AI Session 启动数", "zephyr.core.session.session_continuity", "SessionContinuity"),
        ("SLI-05", "Script 执行吞吐量", "zephyr.governance.phase_check_registry", "PhaseCheckRegistry"),
        ("SLI-06", "Gate 失败率", "zephyr.gates.gate_engine", "GateEngine"),
        ("SLI-07", "Script 执行错误率", "zephyr.governance.phase_check_registry", "PhaseCheckRegistry"),
        ("SLI-08", "契约漂移检出率", "zephyr.drift_detector.drift_engine", "AIConstructionDetectors"),
        ("SLI-09", "Token 预算利用率", "zephyr.budget_enforcer", "BudgetEngine"),
        ("SLI-10", "SQLite WAL 深度", "zephyr.db.database_manager", "DatabaseManager"),
        ("SLI-11", "Session 锁争用率", "zephyr.core.session.session_continuity", "SessionContinuity"),
    ]
    for sli_id, sli_name, module_path, symbol_name in sli_sources:
        try:
            mod = __import__(module_path, fromlist=["__all__"])
            has_symbol = hasattr(mod, symbol_name)
            if has_symbol:
                results.append({
                    "check_id": "SYS-C08",
                    "label": f"{sli_id} {sli_name}",
                    "status": "PASS",
                    "detail": f"{module_path}.{symbol_name} importable",
                })
            else:
                available = [n for n in dir(mod) if not n.startswith("_")][:10]
                results.append({
                    "check_id": "SYS-C08",
                    "label": f"{sli_id} {sli_name}",
                    "status": "WARN",
                    "detail": f"{module_path} importable but {symbol_name} not found; available: {available}",
                })
        except Exception as e:
            results.append({
                "check_id": "SYS-C08",
                "label": f"{sli_id} {sli_name}",
                "status": "WARN",
                "detail": f"{module_path} not importable: {type(e).__name__}: {e}",
            })
    return results


def check_crosscheck_script() -> list[dict]:
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(CROSSCHECK_SCRIPT)],
            capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT)
        )
        ok = result.returncode == 0
        return [{"check_id": "SYS-C06", "label": "crosscheck_script_pass",
                 "status": "PASS" if ok else "FAIL",
                 "detail": f"exit={result.returncode}" + (f" | {result.stdout.strip()[:200]}" if not ok else "")}]
    except Exception as e:
        return [{"check_id": "SYS-C06", "label": "crosscheck_script_pass", "status": "FAIL",
                  "detail": str(e)}]


def main() -> int:
    use_json = "--json" in sys.argv

    all_checks = []
    all_checks.extend(check_blueprint_existence())
    all_checks.extend(check_cold_start_integration())
    all_checks.extend(check_depends_on_integrity())
    all_checks.extend(check_construction_progress_consistency())
    all_checks.extend(check_version_consistency())
    all_checks.extend(check_ai_rules_count())
    all_checks.extend(check_gate_registry_entry())
    all_checks.extend(check_sli_data_sources())
    all_checks.extend(check_crosscheck_script())

    if use_json:
        print(json.dumps(all_checks, indent=2, ensure_ascii=False))
    else:
        for c in all_checks:
            icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(c["status"], "❓")
            print(f"{icon} [{c['status']}] {c['label']}: {c.get('detail', '')}")

    failed = sum(1 for c in all_checks if c["status"] == "FAIL")
    warnings = sum(1 for c in all_checks if c["status"] == "WARN")
    if not use_json:
        print(f"\n{failed} FAILED, {warnings} WARNINGS, {len(all_checks) - failed - warnings} PASSED")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())


class SysMasterCompliance:
    """SYS-MASTER-001 合规检查器——封装所有检查项为可实例化的类。"""

    def __init__(self) -> None:
        pass

    def run_all(self) -> list[dict]:
        checks: list[dict] = []
        checks.extend(check_blueprint_existence())
        checks.extend(check_cold_start_integration())
        checks.extend(check_depends_on_integrity())
        checks.extend(check_construction_progress_consistency())
        checks.extend(check_version_consistency())
        checks.extend(check_ai_rules_count())
        checks.extend(check_gate_registry_entry())
        checks.extend(check_sli_data_sources())
        checks.extend(check_crosscheck_script())
        return checks

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self._cached_results() if c["status"] == "FAIL")

    @property
    def passed(self) -> bool:
        return self.failed_count == 0

    _last_results: list[dict] | None = None

    def _cached_results(self) -> list[dict]:
        if self._last_results is None:
            self._last_results = self.run_all()
        return self._last_results

    def invalidate_cache(self) -> None:
        self._last_results = None


__all__ = ["SysMasterCompliance", "extract_frontmatter"]
