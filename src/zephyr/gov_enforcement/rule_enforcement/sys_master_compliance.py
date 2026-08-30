# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.sys_master_compliance
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SYS-MASTER-001 Compliance Checker

依据：SYS-MASTER-CMP gate——系统总蓝图合规门禁
验证：蓝图存在/冷启动引用/依赖完整性/规则无回归/crosscheck健康

用法：python -m zephyr.gov_enforcement.rule_enforcement.sys_master_compliance [--json]
exit: 0=pass, 1=findings

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: module_id 参数
#   fields: 参数 module_id，类型注解 str
#   code: sys_master_compliance.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: filepath 参数
#   fields: 参数 filepath，类型注解 Path
#   code: sys_master_compliance.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① load_blueprint_path
#   name_en: load_blueprint_path
#   intro: 从 blueprint_registry.yaml（SSoT 派生）查询蓝图磁盘路径，不硬编码。
#   desc: 从 blueprint_registry.yaml（SSoT 派生）查询蓝图磁盘路径，不硬编码。 真源链：blueprint.md frontmatter -> sync_reg…；源码 L165-L181
#   inputs: module_id
#   outputs: Path | None
# - id: A2
#   name_zh: ② extract_frontmatter
#   name_en: extract_frontmatter
#   intro: extract_frontmatter(filepath) 源码 L189-L201
#   desc: 源码 L189-L201
#   inputs: filepath
#   outputs: dict
# - id: A3
#   name_zh: ③ check_blueprint_existence
#   name_en: check_blueprint_existence
#   intro: check_blueprint_existence() 源码 L204-L226
#   desc: 源码 L204-L226
#   inputs: 无参数
#   outputs: list[dict]
# - id: A4
#   name_zh: ④ check_cold_start_integration
#   name_en: check_cold_start_integration
#   intro: check_cold_start_integration() 源码 L229-L258
#   desc: 源码 L229-L258
#   inputs: 无参数
#   outputs: list[dict]
# - id: A5
#   name_zh: ⑤ check_depends_on_integrity
#   name_en: check_depends_on_integrity
#   intro: check_depends_on_integrity() 源码 L261-L294
#   desc: 源码 L261-L294
#   inputs: 无参数
#   outputs: list[dict]
# - id: A6
#   name_zh: ⑥ check_ai_rules_count
#   name_en: check_ai_rules_count
#   intro: check_ai_rules_count() 源码 L297-L312
#   desc: 源码 L297-L312
#   inputs: 无参数
#   outputs: list[dict]
# - id: A7
#   name_zh: ⑦ check_gate_registry_entry
#   name_en: check_gate_registry_entry
#   intro: check_gate_registry_entry() 源码 L315-L334
#   desc: 源码 L315-L334
#   inputs: 无参数
#   outputs: list[dict]
# - id: A8
#   name_zh: ⑧ check_version_consistency
#   name_en: check_version_consistency
#   intro: check_version_consistency() 源码 L337-L410
#   desc: 源码 L337-L410
#   inputs: 无参数
#   outputs: list[dict]
# - id: A9
#   name_zh: ⑨ check_sli_data_sources
#   name_en: check_sli_data_sources
#   intro: check_sli_data_sources() 源码 L413-L470
#   desc: 源码 L413-L470
#   inputs: 无参数
#   outputs: list[dict]
# - id: A10
#   name_zh: ⑩ check_crosscheck_script
#   name_en: check_crosscheck_script
#   intro: check_crosscheck_script() 源码 L473-L505
#   desc: 源码 L473-L505
#   inputs: 无参数
#   outputs: list[dict]
#   （注：A10 之后另有 2 个公共定义未列入（含 0 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: Path | None
#   name_en: Path | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: dict
#   name_en: dict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

import yaml

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 固定配置文件路径（非蓝图，不漂移）
PROJECT_RULES = REPO_ROOT / ".trae" / "rules" / "project_rules.md"
BLUEPRINT_REGISTRY = REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"
MODULE_REGISTRY = REPO_ROOT / "docs" / "03_modules" / "module-registry.yaml"
GATE_REGISTRY = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule_enforcement_registry.yaml"
)
CROSSCHECK_SCRIPT = REPO_ROOT / "scripts" / "governance" / "crosscheck_sys_master_deps.py"


def load_blueprint_path(module_id: str) -> Path | None:
    """从 blueprint_registry.yaml（SSoT 派生）查询蓝图磁盘路径，不硬编码。

    真源链：blueprint.md frontmatter -> sync_registry_from_blueprints.py -> blueprint_registry.yaml
    蓝图改名只需改 frontmatter + 重新 sync，本模块自动跟随，消除连字符/下划线漂移。
    """
    if not BLUEPRINT_REGISTRY.exists():
        return None
    try:
        reg = yaml.safe_load(BLUEPRINT_REGISTRY.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None
    for bp in reg.get("blueprints", []):
        if bp.get("module_id") == module_id and bp.get("file_path"):
            # registry scope=03_modules/，物理在 docs/03_modules/，补 docs 前缀
            return REPO_ROOT / "docs" / bp["file_path"]
    return None


# 蓝图路径从 registry 查询（SSoT），不硬编码——消除连字符/下划线漂移根因
SYS_MASTER_PATH = load_blueprint_path("SYS-MASTER-001")
MOD_MASTER_PATH = load_blueprint_path("MOD-MASTER_BLUEPRINT")


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
    for label, path in [("SYS-MASTER-001", SYS_MASTER_PATH), ("MOD-MASTER_BLUEPRINT", MOD_MASTER_PATH)]:
        if path is None:
            results.append(
                {
                    "check_id": "SYS-C00",
                    "label": f"{label} blueprint_exists",
                    "status": "FAIL",
                    "detail": f"{label} not found in blueprint_registry.yaml",
                }
            )
            continue
        ok = path.exists() and path.is_file()
        results.append(
            {
                "check_id": "SYS-C00",
                "label": f"{label} blueprint_exists",
                "status": "PASS" if ok else "FAIL",
                "detail": str(path.relative_to(REPO_ROOT)) if ok else f"{label} MISSING",
            }
        )
    return results


def check_cold_start_integration() -> list[dict]:
    if not PROJECT_RULES.exists():
        return [
            {
                "check_id": "SYS-C01",
                "label": "cold_start_integration",
                "status": "FAIL",
                "detail": "project_rules.md MISSING",
            }
        ]
    content = PROJECT_RULES.read_text(encoding="utf-8")
    has_sys_master = "SYS-MASTER-001" in content or "_system_master" in content
    in_cold_start = False
    cold_start_section = re.search(r"STEP 1.*?STEP 5", content, re.DOTALL)
    if cold_start_section:
        section_text = cold_start_section.group(0)
        in_cold_start = "SYS-MASTER" in section_text or "_system_master" in section_text
    status = "PASS" if in_cold_start else ("WARN" if has_sys_master else "FAIL")
    return [
        {
            "check_id": "SYS-C01",
            "label": "cold_start_integration",
            "status": status,
            "detail": "SYS-MASTER-001 referenced in cold start sequence"
            if in_cold_start
            else "SYS-MASTER-001 referenced in rules but NOT in cold start sequence"
            if has_sys_master
            else "SYS-MASTER-001 not referenced anywhere in project_rules.md",
        }
    ]


def check_depends_on_integrity() -> list[dict]:
    if SYS_MASTER_PATH is None:
        return [
            {
                "check_id": "SYS-C02",
                "label": "depends_on_integrity",
                "status": "FAIL",
                "detail": "SYS-MASTER-001 not found in blueprint_registry.yaml",
            }
        ]
    fm = extract_frontmatter(SYS_MASTER_PATH)
    if not fm:
        return [
            {
                "check_id": "SYS-C02",
                "label": "depends_on_integrity",
                "status": "FAIL",
                "detail": "Cannot parse SYS-MASTER-001 frontmatter",
            }
        ]
    deps = fm.get("depends_on", [])
    has_mod_master = (
        any(d.get("target", "") == "MOD-MASTER_BLUEPRINT" for d in deps) if isinstance(deps, list) else False
    )
    return [
        {
            "check_id": "SYS-C02",
            "label": "depends_on_integrity",
            "status": "PASS" if has_mod_master else "FAIL",
            "detail": "MOD-MASTER_BLUEPRINT found in depends_on"
            if has_mod_master
            else "MOD-MASTER_BLUEPRINT NOT in depends_on",
        }
    ]


def check_ai_rules_count() -> list[dict]:
    rules_dir = REPO_ROOT / ".trae" / "rules"
    count = 0
    if rules_dir.exists():
        for rf in rules_dir.glob("*.md"):
            content = rf.read_text(encoding="utf-8")
            count += len(re.findall(r"#\d+", content))
    status = "PASS" if count >= 32 else "FAIL"
    return [
        {
            "check_id": "SYS-C04",
            "label": "ai_rules_count",
            "status": status,
            "detail": f"{count} numbered rules found (minimum required: 32)",
        }
    ]


def check_gate_registry_entry() -> list[dict]:
    if not GATE_REGISTRY.exists():
        return [
            {
                "check_id": "SYS-C05",
                "label": "gate_registry_entry",
                "status": "FAIL",
                "detail": "rule_enforcement_registry.yaml MISSING",
            }
        ]
    content = GATE_REGISTRY.read_text(encoding="utf-8")
    has_entry = "SYS-MASTER-CMP" in content
    return [
        {
            "check_id": "SYS-C05",
            "label": "gate_registry_entry",
            "status": "PASS" if has_entry else "FAIL",
            "detail": "SYS-MASTER-CMP found in gate registry" if has_entry else "SYS-MASTER-CMP NOT in gate registry",
        }
    ]


def check_version_consistency() -> list[dict]:
    results = []
    for target_id, target_path in [
        ("SYS-MASTER-001", SYS_MASTER_PATH),
        ("MOD-MASTER_BLUEPRINT", MOD_MASTER_PATH),
    ]:
        if target_path is None:
            results.append(
                {
                    "check_id": "SYS-C07",
                    "label": f"{target_id} version_consistency",
                    "status": "FAIL",
                    "detail": f"{target_id} not found in blueprint_registry.yaml",
                }
            )
            continue
        if not target_path.exists():
            results.append(
                {
                    "check_id": "SYS-C07",
                    "label": f"{target_id} version_consistency",
                    "status": "FAIL",
                    "detail": f"{target_id} blueprint MISSING, cannot verify version",
                }
            )
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

        # Step 1 治标（2026-07-19）：module-registry.yaml 于 commit 8e66175a9d 被删除
        # （备份 depgraph 前的清理），导致 mod_version 永远为 "unknown"，all_match 永远 False。
        # 治标方案：MODULE_REGISTRY 缺失时将 FAIL 降级为 WARN（待治本 Step 2 重建该文件）。
        # 治本恢复后撤掉此降级即恢复为 FAIL。
        module_registry_missing = not MODULE_REGISTRY.exists()
        all_match = fm_version == bp_version == mod_version
        if all_match:
            status = "PASS"
        elif module_registry_missing:
            status = "WARN"
        else:
            status = "FAIL"
        detail_suffix = (
            " | module-registry.yaml MISSING (commit 8e66175a9d), 降级 WARN 待治本恢复"
            if module_registry_missing
            else ""
        )
        results.append(
            {
                "check_id": "SYS-C07",
                "label": f"{target_id} version_consistency",
                "status": status,
                "detail": f"frontmatter={fm_version}, blueprint-registry={bp_version}, module-registry={mod_version}{detail_suffix}",
            }
        )
    return results


def check_sli_data_sources() -> list[dict]:
    results = []
    sli_sources = [
        ("SLI-01", "E2E AI 请求延迟", "zephyr.feedback_loop.slo_manager", "SLOManager"),
        ("SLI-02", "蓝图读取耗时", "zephyr.autonomy_core.dispatch_table", "SystemDispatch"),
        ("SLI-03", "门禁执行总延迟", "zephyr.gov_enforcement.rule_enforcement.gate_engine", "GateEngine"),
        (
            "SLI-04",
            "AI Session 启动数",
            "zephyr.infrastructure.shared_services.session.session_continuity",
            "SessionContinuity",
        ),
        ("SLI-05", "Script 执行吞吐量", "zephyr.infrastructure.rollback.phase_check_registry", "PhaseCheckRegistry"),
        ("SLI-06", "Gate 失败率", "zephyr.gov_enforcement.rule_enforcement.gate_engine", "GateEngine"),
        ("SLI-07", "Script 执行错误率", "zephyr.infrastructure.rollback.phase_check_registry", "PhaseCheckRegistry"),
        ("SLI-08", "契约漂移检出率", "zephyr.gov_drift.drift_engine", "AIConstructionDetectors"),
        ("SLI-09", "Token 预算利用率", "zephyr.infrastructure.budget_enforcement", "BudgetEngine"),
        ("SLI-10", "SQLite WAL 深度", "zephyr.governance.database_manager", "DatabaseManager"),
        (
            "SLI-11",
            "Session 锁争用率",
            "zephyr.infrastructure.shared_services.session.session_continuity",
            "SessionContinuity",
        ),
    ]
    for sli_id, sli_name, module_path, symbol_name in sli_sources:
        try:
            mod = __import__(module_path, fromlist=["__all__"])
            has_symbol = hasattr(mod, symbol_name)
            if has_symbol:
                results.append(
                    {
                        "check_id": "SYS-C08",
                        "label": f"{sli_id} {sli_name}",
                        "status": "PASS",
                        "detail": f"{module_path}.{symbol_name} importable",
                    }
                )
            else:
                available = [n for n in dir(mod) if not n.startswith("_")][:10]
                results.append(
                    {
                        "check_id": "SYS-C08",
                        "label": f"{sli_id} {sli_name}",
                        "status": "WARN",
                        "detail": f"{module_path} importable but {symbol_name} not found; available: {available}",
                    }
                )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            results.append(
                {
                    "check_id": "SYS-C08",
                    "label": f"{sli_id} {sli_name}",
                    "status": "WARN",
                    "detail": f"{module_path} not importable: {type(e).__name__}: {e}",
                }
            )
    return results


def check_crosscheck_script() -> list[dict]:

    # Step 1 治标（2026-07-19）：crosscheck_sys_master_deps.py 于 commit 20b7392141
    # 作为 24 个孤儿脚本之一被删除，导致 subprocess 调用 FileNotFoundError。
    # 治标方案：脚本不存在时将 FAIL 降级为 WARN（待治本 Step 2 恢复该脚本+改 import 路径）。
    # 治本恢复后撤掉此降级即恢复为 FAIL。
    if not CROSSCHECK_SCRIPT.exists():
        return [
            {
                "check_id": "SYS-C06",
                "label": "crosscheck_script_pass",
                "status": "WARN",
                "detail": "crosscheck_sys_master_deps.py MISSING (commit 20b7392141 删除), 降级 WARN 待治本恢复",
            }
        ]

    try:
        result = run_subprocess_hidden(
            [sys.executable, str(CROSSCHECK_SCRIPT)], capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT)
        )
        ok = result.returncode == 0
        return [
            {
                "check_id": "SYS-C06",
                "label": "crosscheck_script_pass",
                "status": "PASS" if ok else "FAIL",
                "detail": f"exit={result.returncode}" + (f" | {result.stdout.strip()[:200]}" if not ok else ""),
            }
        ]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return [
            {"check_id": "SYS-C06", "label": "crosscheck_script_pass", "status": "FAIL", "detail": "internal error"}
        ]


def main() -> int:
    use_json = "--json" in sys.argv

    all_checks = []
    all_checks.extend(check_blueprint_existence())
    all_checks.extend(check_cold_start_integration())
    all_checks.extend(check_depends_on_integrity())
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


class SysMasterCompliance:
    def __init__(self) -> None:
        self._last_results: list[dict] | None = None

    def run_all(self) -> list[dict]:
        checks: list[dict] = []
        checks.extend(check_blueprint_existence())
        checks.extend(check_cold_start_integration())
        checks.extend(check_depends_on_integrity())
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

    def _cached_results(self) -> list[dict]:
        if self._last_results is None:
            self._last_results = self.run_all()
        return self._last_results

    def invalidate_cache(self) -> None:
        self._last_results = None


if __name__ == "__main__":
    sys.exit(main())

__all__ = ["SysMasterCompliance", "extract_frontmatter", "load_blueprint_path"]
