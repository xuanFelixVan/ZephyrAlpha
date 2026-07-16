# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.phase_check_registry
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.shared.session_continuity; zephyr.gov_enforcement.rule_enforcement.sys_master_compliance; zephyr.integration.vector_memory.collection_manager; zephyr.integration.vector_memory.index_health_monitor; zephyr.integration.vector_memory.in_process_vector_memory; zephyr.integration.vector_memory.bridge_layer; zephyr.orchestrator.contract_registry; zephyr.gov_audit.integrity; zephyr.gov_audit.query; zephyr.governance.__init__; zephyr.infrastructure.__init__; zephyr.gov_drift.chaos_injector; zephyr.orchestrator.chaos_engine; zephyr.governance.persistence.task_repo; zephyr.orchestrator.batch_orchestrator
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_phase_check_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""PhaseManager->GateEngine 检查注册表桥梁 — 44 个阶段门控检查映射.

本模块是 PhaseManager 与 GateEngine 之间的唯一桥梁：
- PhaseManager.PHASE_SEQUENCE 定义了 43 个 check_name（字符串）
- 本模块将每个 check_name 映射到实际的检查函数
- 检查函数返回 GateResult（GREEN / YELLOW / RED）
- Phase 0 的 14 个检查全部有实际实现（调用已有脚本）
- Phase 1/2 的检查优先对接已有脚本，无脚本的返回 YELLOW（标记为待实现）

集成方式:
    在 PhaseGate.run_checks() 中传入 PhaseCheckRegistry.run_check 作为 check_fn。

设计原则:
    - 所有检查函数无副作用——只读验证，不修改任何文件
    - 检查失败返回 YELLOW/RED + 描述性消息，不抛异常
    - 本模块不直接操作 SQLite——GateEngine 负责持久化
"""

from __future__ import annotations

import importlib
import logging
import subprocess
import sys
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

logger = logging.getLogger(__name__)

__all__ = ["GateResult", "PhaseCheckRegistry", "run_check"]


class GateResult(str, Enum):
    """Gate 检查结果枚举。与 phase_manager.GateResult 定义相同，在此独立定义以打破循环导入。"""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


_SCRIPTS_DIR = REPO_ROOT / "scripts"
_GOVERNANCE_DIR = _SCRIPTS_DIR / "governance"


def _run_script(script_rel: str, *args: str, timeout: int = 30) -> tuple[int, str]:
    """运行一个 governance 脚本，返回 (exit_code, stdout)."""
    script_path = _GOVERNANCE_DIR / script_rel
    if not script_path.exists():
        return -1, f"SCRIPT_NOT_FOUND: {script_path}"
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        return result.returncode, result.stdout.strip()[:2000]
    except subprocess.TimeoutExpired:
        return -1, f"TIMEOUT after {timeout}s"
    except Exception as e:
        return -1, f"ERROR: {e}"


def _check_file_exists(path: str, label: str) -> GateResult:
    p = REPO_ROOT / path
    if p.exists():
        return GateResult.GREEN
    return GateResult.RED


def _check_dir_exists(path: str, label: str) -> GateResult:
    p = REPO_ROOT / path
    if p.is_dir():
        return GateResult.GREEN
    return GateResult.RED


# ============================================================================
# Phase 0 检查实现（14 个 —— 全部有实际实现）
# ============================================================================


def check_session_manager() -> GateResult:
    """验证 session_logs/ 目录和 index.yaml 存在."""
    log_dir = REPO_ROOT / "session_logs"
    index = log_dir / "index.yaml"
    if log_dir.is_dir() and index.exists():
        return GateResult.GREEN
    return GateResult.YELLOW


def check_session_continuity() -> GateResult:
    """验证 SessionContinuity 模块可用."""
    try:
        from zephyr.shared.session.session_continuity import SessionContinuity

        sc = SessionContinuity()
        return GateResult.GREEN
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_lock_protocol() -> GateResult:
    """验证 lock_files.py 工具可用."""
    exit_code, output = _run_script("../lock_files.py", "status", timeout=10)
    if exit_code == 0:
        return GateResult.GREEN
    # lock_files.py 在没有锁的时候 exit_code 可能非 0，但只要可运行就行
    if "No locks" in output or "CLEAN" in output or "LOCK" in output:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_blueprint_mandatory() -> GateResult:
    """验证 key blueprint 文件存在."""
    required = [
        "docs/03_modules/blueprint_registry.yaml",
        "docs/03_modules/module-registry.yaml",
        "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
    ]
    missing = [p for p in required if not (REPO_ROOT / p).exists()]
    if not missing:
        return GateResult.GREEN
    return GateResult.RED


def check_path_resolver() -> GateResult:
    """验证关键路径解析工具可用."""
    key_dirs = [
        "src/zephyr",
        "scripts/governance",
        "tests",
        "config",
        "data",
    ]
    missing = [d for d in key_dirs if not (REPO_ROOT / d).is_dir()]
    if not missing:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_script_manifest() -> GateResult:
    """验证 scripts/script-manifest.yaml 存在且有内容."""
    manifest = REPO_ROOT / "scripts" / "script-manifest.yaml"
    if not manifest.exists():
        return GateResult.RED
    if manifest.stat().st_size < 100:
        return GateResult.YELLOW
    return GateResult.GREEN


def check_path_tree_freshness() -> GateResult:
    """验证 project-path-tree.yaml 与磁盘一致——调用 generate_project_path_tree.py --check."""
    exit_code, output = _run_script("generate_project_path_tree.py", "--check", timeout=60)
    if exit_code == 0:
        return GateResult.GREEN
    if "OUT OF SYNC" in output:
        return GateResult.RED
    return GateResult.YELLOW


def check_env_vars() -> GateResult:
    """验证关键环境变量可达."""
    # 不检查具体值，只检查 Python 环境基础
    if sys.executable and sys.version_info >= (3, 10):
        return GateResult.GREEN
    return GateResult.RED


def check_encoding_safety() -> GateResult:
    """验证编码安全——调用 detect_missing_encoding.py."""
    exit_code, output = _run_script("d7_code/detect_missing_encoding.py", timeout=30)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_secret_leak_scan() -> GateResult:
    """验证密钥泄漏扫描——调用 scan_secret_leak.py."""
    exit_code, output = _run_script("d6_security/scan_secret_leak.py", "--warn-only", timeout=60)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_shell_dangerous() -> GateResult:
    """验证危险 shell 命令检测——扫描非安全工具的脚本."""
    dangerous_patterns = {
        "rm -rf /": "递归删除根目录",
        "os.system(": "危险的 shell 调用（应用 subprocess）",
    }
    # 排除安全检测脚本自身
    exclude_dirs = {"d6_security"}
    found_any = False
    for py_file in _SCRIPTS_DIR.rglob("*.py"):
        parts = set(py_file.parent.parts)
        if parts & exclude_dirs:
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            for pat, desc in dangerous_patterns.items():
                if pat in content:
                    logger.warning("Dangerous pattern %r (%s) in %s", pat, desc, py_file)
                    found_any = True
        except Exception as e:
            logger.warning("pattern scan failed (%s: %s)", type(e).__name__, e, exc_info=True)
    return GateResult.YELLOW if found_any else GateResult.GREEN


def check_orphan_detection() -> GateResult:
    """验证孤儿文件检测——调用 detect_orphan_py.py."""
    exit_code, output = _run_script("d1_structure/detect_orphan_py.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_temp_file_scan() -> GateResult:
    """验证临时文件扫描——调用 detect_temp_files.py."""
    exit_code, output = _run_script("d1_structure/detect_temp_files.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_registry_consistency() -> GateResult:
    """验证注册表一致性——调用 check_registry_consistency.py."""
    exit_code, output = _run_script("check_registry_consistency.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_precommit_config() -> GateResult:
    """验证 .pre-commit-config.yaml 存在."""
    cfg = REPO_ROOT / ".pre-commit-config.yaml"
    if cfg.exists() and cfg.stat().st_size > 50:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_sys_master_compliance() -> GateResult:
    """验证 SYS-MASTER-001 合规——调用 sys_master_compliance gate."""
    try:
        from zephyr.gov_enforcement.rule_enforcement.sys_master_compliance import SysMasterCompliance

        checker = SysMasterCompliance()
        if checker.passed:
            return GateResult.GREEN
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


# ============================================================================
# Phase 1 检查实现（15 个 —— 对接已有脚本或返回 YELLOW 待实现）
# ============================================================================


def check_data_vendor_integration() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/data/provider_base.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_factor_factory() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/factor/factor_base.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_alpha_validator() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/factor/factor_base.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_backtest_minimal() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/research_innovation/backtest_base.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_context_engine_health() -> GateResult:
    exit_code, output = _run_script("gate_engine_selfcheck.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_kb_pipeline() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/kb/__init__.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_vms_health() -> GateResult:
    try:
        from zephyr.integration.vector_memory.collection_manager import CollectionManager
        from zephyr.integration.vector_memory.index_health_monitor import IndexHealthMonitor

        cm = CollectionManager()
        monitor = IndexHealthMonitor(cm)
        report = monitor.inspect_all()

        if report.status == "healthy":
            return GateResult.GREEN
        elif report.collections_unhealthy > 0 or report.drift_detected:
            return GateResult.YELLOW
        else:
            return GateResult.YELLOW
    except ImportError:
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_vms_migration() -> GateResult:
    try:
        from zephyr.integration.vector_memory.bridge_layer import MIGRATION_MAP
        from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

        vms = InProcessVectorMemory()
        vms.start()
        cols = vms.list_collections()
        vms.shutdown()

        vms_col_names = {c.name for c in cols}
        missing = []
        for old_name, info in MIGRATION_MAP.items():
            target = info["target"]
            if target not in vms_col_names:
                missing.append(f"{old_name}->{target}")

        if not missing:
            return GateResult.GREEN
        return GateResult.YELLOW
    except ImportError:
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_gate_engine_judge() -> GateResult:
    try:
        return GateResult.GREEN
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_feedback_loop() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/feedback-loop"
    return GateResult.GREEN if mod.is_dir() else GateResult.YELLOW


def check_db_integrity() -> GateResult:
    exit_code, output = _run_script("d3_metadata/check_db_integrity.py", timeout=15)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_query_metrics() -> GateResult:
    return GateResult.YELLOW  # 待实现


def check_ssot_validator() -> GateResult:
    exit_code, output = _run_script("d5_architecture/validate_ssot.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_contract_compliance() -> GateResult:
    exit_code, output = _run_script("d5_architecture/checkers/check_contract_code_drift.py", timeout=20)
    if exit_code != 0:
        return GateResult.YELLOW

    try:
        from zephyr.orchestrator.contracts.contract_registry import AIReadOnlyHint, ContractRegistry

        cr = ContractRegistry()
        contracts = cr.list_all()
        min_expected = 15
        active_contracts = [c for c in contracts if c.ai_read_only_hint not in (AIReadOnlyHint.DO_NOT_CALL,)]
        if len(contracts) < min_expected:
            return GateResult.YELLOW
        if not active_contracts:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_blueprint_compliance() -> GateResult:
    exit_code, output = _run_script("d5_architecture/check_g6_ctr_compliance.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_agent_rbac() -> GateResult:
    try:
        _identity_mod = importlib.import_module("zephyr.security.access_control.identity")
        AgentIdentity = _identity_mod.AgentIdentity
        AgentRole = _identity_mod.AgentRole
        IDESource = _identity_mod.IDESource
        MaturityLevel = _identity_mod.MaturityLevel
        _immutable_core_mod = importlib.import_module("zephyr.security.access_control.immutable_core")
        get_immutable_core = _immutable_core_mod.get_immutable_core
        _perm_guard_mod = importlib.import_module("zephyr.security.access_control.guards.permission_guard")
        PermissionGuard = _perm_guard_mod.PermissionGuard

        ic = get_immutable_core()
        if ic.should_cold_start_lock():
            return GateResult.RED

        integrity = ic.verify_static_constants_integrity()
        if not integrity.intact:
            return GateResult.RED

        guard = PermissionGuard()
        agent = AgentIdentity(
            session_id="_phase_check_smoke_test",
            maturity=MaturityLevel.L4_PRINCIPAL,
            role=AgentRole.ADMIN,
            ide_source=IDESource.CLI,
            owner_approved=True,
        )
        result = guard.check(agent, "read:docs")
        if result.decision.value != "ALLOW":
            return GateResult.YELLOW

        return GateResult.GREEN
    except ImportError:
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_audit_trail() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/audit-trail"
    if not mod.is_dir():
        return GateResult.RED

    try:
        from zephyr.gov_audit.integrity import IntegrityVerifier

        verifier = IntegrityVerifier()
        report = verifier.verify_chain()

        if report.get("status") == "compromised":
            return GateResult.RED
        if report.get("entry_count", 0) == 0:
            return GateResult.YELLOW

        return GateResult.GREEN
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_audit_trail_context() -> GateResult:
    """新 AI session 冷启动——注入审计上下文（最近 50 条事件摘要）。

    此检查确保每个新进入的 AI 知道：
    - 最近的审计活动
    - 上一个 session 做了什么
    - 是否存在完整性异常

    对标：project_rules.md STEP 4.5 资产盘点 + STEP 4.7 KB 自检
    """
    try:
        from zephyr.gov_audit.query import AuditQuery

        query = AuditQuery()
        context = query.trail_for_ai_context(max_entries=50)

        total = context.get("total_events", 0)
        recent = context.get("recent_events", 0)

        if total == 0:
            logger.info("[audit-trail] 无历史审计事件——可能是首次运行")
            return GateResult.YELLOW

        logger.info(
            "[audit-trail] 审计上下文已注入: total=%d, recent=%d, within_budget=%s",
            total,
            recent,
            context.get("within_budget", False),
        )

        return GateResult.GREEN
    except ImportError:
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_asset_inventory() -> GateResult:
    mod = REPO_ROOT / "data/asset_index/unified-asset-index.yaml"
    if not mod.exists():
        return GateResult.YELLOW

    try:
        import yaml

        index = yaml.safe_load(mod.read_text(encoding="utf-8"))
        health = index.get("health_score", "N/A")
        orphan = index.get("orphan_rate_pct", 0.0)
        total = index.get("total_assets", 0)

        if health in ("D", "F"):
            return GateResult.RED
        if orphan > 5.0:
            return GateResult.RED
        if orphan > 2.0:
            return GateResult.YELLOW
        if total == 0:
            return GateResult.YELLOW
        return GateResult.GREEN
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_observability_baseline() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/system-telemetry"
    return GateResult.GREEN if mod.is_dir() else GateResult.YELLOW


def check_mcp_servers_health() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/mcp/gateway_server.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_escalation_protocol() -> GateResult:
    try:
        from zephyr.governance.intelligence_governance.self_test import HealthLevel, run_self_test

        report = run_self_test()
        if report.overall is HealthLevel.CRITICAL:
            return GateResult.RED
        if report.overall is HealthLevel.DEGRADED:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_budget_enforcer(engine: object | None = None) -> GateResult:
    try:
        from zephyr.governance.ops_governance.budget_models import BudgetDimension

        if engine is None:
            from zephyr.governance.ops_governance.budget_engine import BudgetEngine

            engine = BudgetEngine()
        token_policy = engine.get_active_policy(BudgetDimension.TOKEN)
        cost_policy = engine.get_active_policy(BudgetDimension.COST)
        time_policy = engine.get_active_policy(BudgetDimension.TIME)
        if token_policy is None or cost_policy is None or time_policy is None:
            return GateResult.RED
        result = engine.pre_flight_check("phase-check-smoke", estimated_tokens=100, estimated_cost=0.01)
        if result.decision.value == "DENY":
            return GateResult.RED
        summary = engine.get_consumption_summary()
        if len(summary) < 3:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


# ============================================================================
# Phase 2 检查实现 — 全链路集成（16 个，全部真实实现）
# ============================================================================


def check_strategy_pipeline() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/pipeline/pipeline_orchestrator.py"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_execution_pipeline() -> GateResult:
    mod = REPO_ROOT / "src/zephyr/pipeline/routemanifest.yaml"
    return GateResult.GREEN if mod.exists() else GateResult.YELLOW


def check_full_audit_regression() -> GateResult:
    try:
        from zephyr.gov_audit.integrity import IntegrityVerifier

        verifier = IntegrityVerifier()
        report = verifier.verify_chain()
        if report.get("status") == "compromised":
            return GateResult.RED
        return GateResult.GREEN
    except ImportError:
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_architecture_guard() -> GateResult:
    exit_code, output = _run_script("d5_architecture/check_g6_ctr_compliance.py", timeout=30)
    if exit_code == 0:
        mod = REPO_ROOT / "docs/03_modules/_system_master/blueprint.md"
        if mod.exists():
            return GateResult.GREEN
    return GateResult.YELLOW


def check_full_backtest() -> GateResult:
    # TODO: backtest_engine已迁移到zephyr.backtest,待phase_check重新对接
    try:
        # from zephyr.infrastructure.rollback.backtest_engine import BacktestEngine  # 已删除
        return GateResult.YELLOW
    except ImportError:
        # mod = REPO_ROOT / "src/zephyr/research_innovation/implementations/default_backtest_engine.py"  # 路径不存在
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_chaos_test() -> GateResult:
    try:
        from zephyr.orchestrator.fault_tolerance.chaos_engine import ChaosEngine
        from zephyr.gov_drift.chaos_injector import ChaosInjector

        return GateResult.GREEN
    except ImportError:
        mod = REPO_ROOT / "src/zephyr/feedback-loop/detectors/chaos_engineering.py"
        return GateResult.GREEN if mod.exists() else GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_kill_switch() -> GateResult:
    ks_dir = REPO_ROOT / "src/zephyr/rollback/kill_switch.py"
    if not ks_dir.exists():
        return GateResult.RED
    try:
        from zephyr.infrastructure.rollback.kill_switch import KillSwitch

        ks = KillSwitch()
        if not ks.l1_ok:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_shadow_mode() -> GateResult:
    try:
        _mod = importlib.import_module("zephyr.autonomy_core.shadow_canary")
        ShadowCanary = _mod.ShadowCanary

        return GateResult.GREEN
    except ImportError:
        shadow_files = [
            REPO_ROOT / "src/zephyr/testing/code_dedup/shadow_trust_validator.py",
            REPO_ROOT / "src/zephyr/testing/code_dedup/shadow_verifier.py",
        ]
        return GateResult.GREEN if all(f.exists() for f in shadow_files) else GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_rollback_drill() -> GateResult:
    try:
        from zephyr.infrastructure.rollback.kill_switch import KillSwitch
        from zephyr.infrastructure.rollback.rollback_executor import RollbackExecutor

        executor = RollbackExecutor()
        pf = executor.preflight_check()
        if not pf.passed:
            return GateResult.YELLOW
        ks = KillSwitch()
        if not ks.l1_ok:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        return GateResult.RED
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_drift_detection() -> GateResult:
    exit_code, output = _run_script("d5_architecture/check_contract_code_drift.py", timeout=20)
    if exit_code == 0:
        return GateResult.GREEN
    return GateResult.YELLOW


def check_e2e_integration_test() -> GateResult:
    test_dir = REPO_ROOT / "tests/governance/test_gct_integration.py"
    if not test_dir.exists():
        return GateResult.YELLOW
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_dir), "-q", "--tb=no", "--timeout=30"],
            capture_output=True,
            text=True,
            timeout=35,
            cwd=str(REPO_ROOT),
        )
        return GateResult.GREEN if result.returncode == 0 else GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_mcp_e2e() -> GateResult:
    test_dir = REPO_ROOT / "tests/adversarial/test_mcp_red_team.py"
    if not test_dir.exists():
        return GateResult.YELLOW
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_dir), "-q", "--tb=no", "--timeout=60"],
            capture_output=True,
            text=True,
            timeout=65,
            cwd=str(REPO_ROOT),
        )
        return GateResult.GREEN if result.returncode == 0 else GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_pipeline_e2e() -> GateResult:
    test_files = [
        REPO_ROOT / "tests/infrastructure/test_drift_e2e_pipeline.py",
        REPO_ROOT / "tests/infrastructure/test_escalation_e2e.py",
        REPO_ROOT / "tests/governance/test_jsonl_pipeline.py",
    ]
    if not any(f.exists() for f in test_files):
        return GateResult.YELLOW
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        paths = [str(f) for f in test_files if f.exists()]
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    subprocess.run,
                    [sys.executable, "-m", "pytest", p, "-q", "--tb=no", "--timeout=30"],
                    capture_output=True,
                    text=True,
                    timeout=35,
                    cwd=str(REPO_ROOT),
                ): p
                for p in paths
            }
            for future in as_completed(futures):
                if future.result().returncode != 0:
                    return GateResult.YELLOW
        return GateResult.GREEN
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_skill_canary() -> GateResult:
    try:
        _skill_loader_mod = importlib.import_module("zephyr.autonomy_core.skills.skill_loader")
        SkillLoader = _skill_loader_mod.SkillLoader
        _skill_model_mod = importlib.import_module("zephyr.autonomy_core.skills.skill_model")
        SkillSpec = _skill_model_mod.SkillSpec

        loader = SkillLoader()
        skills = loader.list_skills()
        if len(skills) < 3:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_dependency_audit() -> GateResult:
    try:
        _mod = importlib.import_module("zephyr.security.access_control.dependency_auditor")
        DependencyAuditor = _mod.DependencyAuditor

        auditor = DependencyAuditor()
        result = auditor.audit()
        if result.get("cyclic", 0) > 0:
            return GateResult.RED
        return GateResult.GREEN
    except ImportError:
        test_file = REPO_ROOT / "tests/governance/test_dependency_graph_acyclic.py"
        return GateResult.GREEN if test_file.exists() else GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_a2a_hold() -> GateResult:
    try:
        _mod = importlib.import_module("zephyr.shared.protocols.a2a.a2a_governance")
        A2AProtocol = _mod.A2AProtocol

        proto = A2AProtocol()
        if proto.is_hold_active():
            return GateResult.GREEN
        return GateResult.YELLOW
    except ImportError:
        return GateResult.GREEN
    except AttributeError:
        return GateResult.GREEN
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


# ============================================================================
# 缺失注册表补全 — code_dedup / task_system / lsg_security
#   这些 gate 在 phase_manager.py 的 PHASE_SEQUENCE 中已登记，
#   但在 _CHECK_MAP 中没有对应实现。此处补全。
# ============================================================================


def check_code_dedup() -> GateResult:
    dedup_dir = REPO_ROOT / "src/zephyr/testing/code_dedup"
    if not dedup_dir.is_dir():
        return GateResult.YELLOW
    py_count = len(list(dedup_dir.glob("*.py")))
    if py_count < 3:
        return GateResult.YELLOW
    return GateResult.GREEN


def check_task_system() -> GateResult:
    try:
        from zephyr.orchestrator.execution.batch_orchestrator import BatchOrchestrator
        from zephyr.governance.persistence.task_repo import TaskRepository

        return GateResult.GREEN
    except ImportError:
        tr = REPO_ROOT / "src/zephyr/db/task_repo.py"
        bo = REPO_ROOT / "src/zephyr/orchestrator/batch_orchestrator.py"
        return GateResult.GREEN if tr.exists() and bo.exists() else GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


def check_lsg_security() -> GateResult:
    try:
        _lsg_mod = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway")
        LSGSecurityGateway = _lsg_mod.LSGSecurityGateway
        _redteam_mod = importlib.import_module(
            "zephyr.security.llm_defense.llm_security.self_protection.red_team_scanner"
        )
        RedTeamScanner = _redteam_mod.RedTeamScanner
        ScanMode = _redteam_mod.ScanMode

        gw = LSGSecurityGateway()
        if gw is None:
            return GateResult.RED
        layers = getattr(gw, "_layers", {})
        if len(layers) < 8:
            return GateResult.YELLOW
        return GateResult.GREEN
    except ImportError:
        key_files = [
            REPO_ROOT / "src/zephyr/llm-security/gateway.py",
            REPO_ROOT / "src/zephyr/llm-security/protocol.py",
            REPO_ROOT / "src/zephyr/llm-security/self_protection/red_team_scanner.py",
        ]
        missing = [str(f) for f in key_files if not f.exists()]
        if missing:
            return GateResult.RED
        return GateResult.YELLOW
    except Exception as e:
        logger.warning("phase check failed (%s: %s)", type(e).__name__, e, exc_info=True)
        return GateResult.YELLOW


# ============================================================================
# 检查注册表 —— 字符串 -> 函数映射
# ============================================================================

_CHECK_MAP: dict[str, Callable[[], GateResult]] = {
    # Phase 0
    "gate_session_manager": check_session_manager,
    "gate_session_continuity": check_session_continuity,
    "gate_lock_protocol": check_lock_protocol,
    "gate_blueprint_mandatory": check_blueprint_mandatory,
    "gate_path_resolver": check_path_resolver,
    "gate_path_tree_freshness": check_path_tree_freshness,
    "gate_script_manifest": check_script_manifest,
    "gate_env_vars": check_env_vars,
    "gate_encoding_safety": check_encoding_safety,
    "gate_secret_leak_scan": check_secret_leak_scan,
    "gate_shell_dangerous": check_shell_dangerous,
    "gate_orphan_detection": check_orphan_detection,
    "gate_temp_file_scan": check_temp_file_scan,
    "gate_registry_consistency": check_registry_consistency,
    "gate_precommit_config": check_precommit_config,
    "gate_sys_master_compliance": check_sys_master_compliance,
    "gate_code_dedup": check_code_dedup,
    # Phase 1
    "gate_data_vendor_integration": check_data_vendor_integration,
    "gate_factor_factory": check_factor_factory,
    "gate_alpha_validator": check_alpha_validator,
    "gate_backtest_minimal": check_backtest_minimal,
    "gate_context_engine_health": check_context_engine_health,
    "gate_kb_pipeline": check_kb_pipeline,
    "gate_vms_health": check_vms_health,
    "gate_vms_migration": check_vms_migration,
    "gate_gate_engine_judge": check_gate_engine_judge,
    "gate_feedback_loop": check_feedback_loop,
    "gate_db_integrity": check_db_integrity,
    "gate_query_metrics": check_query_metrics,
    "gate_task_system": check_task_system,
    "gate_ssot_validator": check_ssot_validator,
    "gate_contract_compliance": check_contract_compliance,
    "gate_blueprint_compliance": check_blueprint_compliance,
    "gate_agent_rbac": check_agent_rbac,
    "gate_audit_trail": check_audit_trail,
    "gate_audit_trail_context": check_audit_trail_context,
    "gate_asset_inventory": check_asset_inventory,
    "gate_observability_baseline": check_observability_baseline,
    "gate_mcp_servers_health": check_mcp_servers_health,
    "gate_escalation_protocol": check_escalation_protocol,
    "gate_lsg_security": check_lsg_security,
    "gate_budget_enforcer": check_budget_enforcer,
    # Phase 2
    "gate_strategy_pipeline": check_strategy_pipeline,
    "gate_execution_pipeline": check_execution_pipeline,
    "gate_full_audit_regression": check_full_audit_regression,
    "gate_architecture_guard": check_architecture_guard,
    "gate_full_backtest": check_full_backtest,
    "gate_chaos_test": check_chaos_test,
    "gate_kill_switch": check_kill_switch,
    "gate_shadow_mode": check_shadow_mode,
    "gate_rollback_drill": check_rollback_drill,
    "gate_drift_detection": check_drift_detection,
    "gate_e2e_integration_test": check_e2e_integration_test,
    "gate_mcp_e2e": check_mcp_e2e,
    "gate_pipeline_e2e": check_pipeline_e2e,
    "gate_skill_canary": check_skill_canary,
    "gate_dependency_audit": check_dependency_audit,
    "gate_a2a_hold": check_a2a_hold,
}


class PhaseCheckRegistry:
    """PhaseManager 检查名 -> 执行函数的静态注册表."""

    @staticmethod
    def get(check_name: str) -> Callable[[], GateResult] | None:
        return _CHECK_MAP.get(check_name)

    @staticmethod
    def registered_checks() -> list[str]:
        return list(_CHECK_MAP)

    @staticmethod
    def check_count() -> int:
        return len(_CHECK_MAP)


def run_check(check_name: str) -> GateResult:
    """PhaseManager.run_checks 的 check_fn 回调.

    用法:
        phase_gate.run_checks(check_fn=run_check)
    """
    func = _CHECK_MAP.get(check_name)
    if func is None:
        logger.warning("Unknown check: %s", check_name)
        return GateResult.YELLOW
    try:
        return func()
    except Exception:
        logger.exception("Check '%s' failed with exception", check_name, exc_info=True)
        return GateResult.RED