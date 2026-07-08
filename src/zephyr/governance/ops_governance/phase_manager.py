# [BLUEPRINT] SRC-061 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.phase_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.phase_check_registry
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
# [A_module] module_id=MOD-GOV_phase_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Phase Manager — ZephyrAlpha 施工阶段门控引擎.

五层强制集成架构 — Layer 3（阶段门控）:
    每个 ConstructionPhase 定义一组 gate_checks —— AI 在进入下一阶段前 MUST 全部 GREEN.
    对标: K8s Pod Phase + CI Pipeline Stage Gates + ITIL Change Enablement.

三阶段 51 检查（2026-05-08 ISSUE-3 扩展）:
    Phase 0 (15 检查) — 基础设施就绪：项目骨架、安全基线、注册表一致性 [全部已实现]
    Phase 1 (24 检查) — 核心系统就绪：各引擎健康、数据库完整性、契约合规 [对接已有脚本]
    Phase 2 (16 检查) — 全链路集成：审计回归、技能金丝雀、回滚演练、E2E [stub 待基建就绪]

PhaseManager ↔ GateEngine 桥梁:
    PhaseCheckRegistry（phase_check_registry.py）将所有 43 个 check_name
    映射到实际的 Python 函数。PhaseGate.run_checks() 默认使用 run_check 作为 check_fn。
    无需外部传入回调——桥梁已内置。

冷启动集成 — SYS-MASTER-001:
    新 AI session 进入本项目时，必须先读 docs/03_modules/_system_master/blueprint.md §0
    （81 域分派表）定位任务域，再使用本 PhaseManager 判断施工阶段。
    冷启动序列：AGENTS.md -> SYS-MASTER-001 §0 -> project_rules.md -> SessionContinuity -> PhaseManager
"""

from __future__ import annotations

from typing import Final
import logging
from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConstructionPhase(str, Enum):
    PHASE_0_SKELETON = "PHASE_0_SKELETON"
    PHASE_1_FUNCTIONAL = "PHASE_1_FUNCTIONAL"
    PHASE_2_E2E = "PHASE_2_E2E"


class GateResult(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class PhaseGate(BaseModel):
    phase: ConstructionPhase
    name: str
    description: str = ""
    dependencies: list[ConstructionPhase] = Field(default_factory=list)
    gate_checks: list[str] = Field(default_factory=list)
    result: GateResult = GateResult.GREEN

    @property
    def check_count(self) -> int:
        return len(self.gate_checks)

    def run_checks(self, check_fn: Callable[[str], GateResult] | None = None) -> GateResult:
        if check_fn is None:
            from zephyr.governance.ops_governance.phase_check_registry import run_check as _run_check

            check_fn = _run_check
        worst = GateResult.GREEN
        for check_name in self.gate_checks:
            r = check_fn(check_name)
            if r == GateResult.RED:
                self.result = GateResult.RED
                return GateResult.RED
            if r == GateResult.YELLOW:
                worst = GateResult.YELLOW
        self.result = worst
        return worst


PHASE_SEQUENCE: Final[dict[ConstructionPhase, PhaseGate]] = {
    # ================================================================
    # Phase 0 — 骨架搭建 (15 checks)
    # 对标: 项目初始化 + RULE-ZERO~FIVE 合规 + 安全/目录基线 + 代码去重
    # ================================================================
    ConstructionPhase.PHASE_0_SKELETON: PhaseGate(
        phase=ConstructionPhase.PHASE_0_SKELETON,
        name="Phase 0 — 骨架搭建",
        description="基础设施就绪：项目骨架、安全基线、注册表一致性、编码规范",
        dependencies=[],
        gate_checks=[
            # ── 会话与锁协议 ──
            "gate_session_manager",
            "gate_session_continuity",
            "gate_lock_protocol",
            # ── 蓝图与路径 ──
            "gate_blueprint_mandatory",
            "gate_path_resolver",
            "gate_path_tree_freshness",
            "gate_script_manifest",
            # ── 环境与编码 ──
            "gate_env_vars",
            "gate_encoding_safety",
            # ── 安全基线 (D6 子集) ──
            "gate_secret_leak_scan",
            "gate_shell_dangerous",
            # ── 结构完整性 (D1 子集) ──
            "gate_orphan_detection",
            "gate_temp_file_scan",
            # ── 代码去重 ──
            "gate_code_dedup",
            # ── 注册表完整性 ──
            "gate_registry_consistency",
            "gate_precommit_config",
            "gate_sys_master_compliance",
        ],
    ),
    # ================================================================
    # Phase 1 (24 checks) — 核心系统就绪：各引擎健康、数据库完整性、契约合规
    # ================================================================
    ConstructionPhase.PHASE_1_FUNCTIONAL: PhaseGate(
        phase=ConstructionPhase.PHASE_1_FUNCTIONAL,
        name="Phase 1 — 功能集成",
        description="核心系统就绪：各引擎健康、数据库完整性、契约合规、蓝图同步",
        dependencies=[ConstructionPhase.PHASE_0_SKELETON],
        gate_checks=[
            # ── 数据与因子 ──
            "gate_data_vendor_integration",
            "gate_factor_factory",
            "gate_alpha_validator",
            "gate_backtest_minimal",
            # ── 核心引擎 ──
            "gate_context_engine_health",
            "gate_kb_pipeline",
            "gate_vms_health",
            "gate_vms_migration",
            "gate_gate_engine_judge",
            "gate_feedback_loop",
            # ── 数据库 ──
            "gate_db_integrity",
            "gate_query_metrics",
            # ── 任务系统 (Task System MOD-TASK_SYSTEM) ──
            "gate_task_system",
            # ── 架构合规 ──
            "gate_ssot_validator",
            "gate_contract_compliance",
            "gate_blueprint_compliance",
            # ── Agent 系统 ──
            "gate_agent_rbac",
            "gate_audit_trail",
            "gate_audit_trail_context",
            # ── 资产盘点 ──
            "gate_asset_inventory",
            # ── 观测基线 (System Telemetry MOD-INF-015) ──
            "gate_observability_baseline",
            "gate_mcp_servers_health",
            # ── 升级协议 ──
            "gate_escalation_protocol",
            # ── LLM 安全网关 ──
            "gate_lsg_security",
            # ── 预算执行 ──
            "gate_budget_enforcer",
        ],
    ),
    # ================================================================
    # Phase 2 — 全链路集成 (15 checks)
    # 对标: end-to-end pipeline + 全量审计回归 + Canary/Shadow/Rollback
    # ================================================================
    ConstructionPhase.PHASE_2_E2E: PhaseGate(
        phase=ConstructionPhase.PHASE_2_E2E,
        name="Phase 2 — 全链路集成",
        description="全链路就绪：审计全量回归、架构守卫、金丝雀测试、回滚演练、E2E",
        dependencies=[ConstructionPhase.PHASE_1_FUNCTIONAL],
        gate_checks=[
            # ── 策略与执行管道 ──
            "gate_strategy_pipeline",
            "gate_execution_pipeline",
            # ── 全量审计回归 ──
            "gate_full_audit_regression",
            "gate_architecture_guard",
            "gate_full_backtest",
            # ── Resilience 测试 ──
            "gate_chaos_test",
            "gate_kill_switch",
            "gate_shadow_mode",
            # ── 回滚与恢复 ──
            "gate_rollback_drill",
            "gate_drift_detection",
            # ── 集成 E2E ──
            "gate_e2e_integration_test",
            "gate_mcp_e2e",
            "gate_pipeline_e2e",
            # ── 技能与依赖 ──
            "gate_skill_canary",
            "gate_dependency_audit",
            # ── A2A Hold 占位 ──
            "gate_a2a_hold",
        ],
    ),
}


def get_phase(phase: ConstructionPhase) -> PhaseGate | None:
    return PHASE_SEQUENCE.get(phase)


def get_next_phase(current: ConstructionPhase) -> ConstructionPhase | None:
    phases = list(ConstructionPhase)
    try:
        idx = phases.index(current)
        if idx + 1 < len(phases):
            return phases[idx + 1]
    except ValueError:
        pass
    return None


def phase_resolver(completed_gates: set[str]) -> ConstructionPhase:
    """根据已完成的 gate 集合判断当前施工阶段。"""
    p0_gates = set(PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON].gate_checks)
    p1_gates = set(PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL].gate_checks)
    p2_gates = set(PHASE_SEQUENCE[ConstructionPhase.PHASE_2_E2E].gate_checks)

    if p2_gates.issubset(completed_gates):
        return ConstructionPhase.PHASE_2_E2E
    if p1_gates.issubset(completed_gates):
        return ConstructionPhase.PHASE_1_FUNCTIONAL
    if p0_gates.issubset(completed_gates):
        return ConstructionPhase.PHASE_0_SKELETON
    return ConstructionPhase.PHASE_0_SKELETON


def session_startup(quick: bool = True) -> dict:
    """AI Session 冷启动门禁 — 进入项目后 MUST 调用的第一个函数.

    对标: K8s Pod Init Container — 主容器启动前必须完成初始化检查.
    对标: 航空 pre-flight checklist — 起飞前逐项打勾.

    本函数执行 Phase 0 骨架检查的快速子集 (quick=True, ~3s)
    或全量子集 (quick=False, ~15s, 包含子进程调用).

    返回 dict:
        {
            "ready": bool,          # True = 可以开工
            "phase": str,           # 当前施工阶段
            "green": int,           # GREEN 检查数
            "yellow": int,          # YELLOW 警告数
            "red": int,             # RED 阻断数
            "checks": [             # 每项检查结果
                {"name": str, "status": str, "message": str}
            ],
            "next_action": str,     # 下一步建议
        }

    Usage:
        # import session_startup from this module directly
        result = session_startup()
        if not result["ready"]:
            print(f"Session : {result['next_action']}")
    """
    from zephyr.governance.ops_governance.phase_check_registry import (
        check_audit_trail_context,
        check_blueprint_mandatory,
        check_budget_enforcer,
        check_encoding_safety,
        check_env_vars,
        check_lock_protocol,
        check_orphan_detection,
        check_path_resolver,
        check_precommit_config,
        check_registry_consistency,
        check_script_manifest,
        check_secret_leak_scan,
        check_session_continuity,
        check_session_manager,
        check_shell_dangerous,
        check_temp_file_scan,
    )

    _FAST_CHECKS = [
        ("会话管理器", check_session_manager),
        ("会话连续性", check_session_continuity),
        ("锁协议可用", check_lock_protocol),
        ("蓝图完整性", check_blueprint_mandatory),
        ("关键路径", check_path_resolver),
        ("脚本清单", check_script_manifest),
        ("Python环境", check_env_vars),
        ("Pre-commit配置", check_precommit_config),
        ("审计上下文", check_audit_trail_context),
        ("预算执行器", check_budget_enforcer),
    ]

    _SLOW_CHECKS = [
        ("孤儿检测", check_orphan_detection),
        ("临时文件扫描", check_temp_file_scan),
        ("注册表一致性", check_registry_consistency),
        ("编码安全", check_encoding_safety),
        ("密钥泄漏扫描", check_secret_leak_scan),
        ("危险Shell检测", check_shell_dangerous),
    ]

    active_checks = _FAST_CHECKS if quick else _FAST_CHECKS + _SLOW_CHECKS

    from concurrent.futures import ThreadPoolExecutor, as_completed

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for name, fn in active_checks:
            futures[executor.submit(fn)] = name
        for future in as_completed(futures):
            name = futures[future]
            try:
                status = future.result()
            except Exception:
                status = GateResult.RED
            results.append(
                {
                    "name": name,
                    "status": status.value if hasattr(status, "value") else str(status),
                    "message": f"{name}: {status.value}" if hasattr(status, "value") else str(status),
                }
            )

    green = sum(1 for r in results if r["status"] == "GREEN")
    yellow = sum(1 for r in results if r["status"] == "YELLOW")
    red = sum(1 for r in results if r["status"] == "RED")

    ready = red == 0

    if not ready:
        next_action = f"🔴 {red} 项阻断。先修复 RED 项再开工: " + ", ".join(
            r["name"] for r in results if r["status"] == "RED"
        )
    elif yellow > 0:
        next_action = f"⚠ {yellow} 项警告。可以开工, 但建议先检查: " + ", ".join(
            r["name"] for r in results if r["status"] == "YELLOW"
        )
    else:
        next_action = "✅ 全部 GREEN。可以开工。"

    return {
        "ready": ready,
        "phase": "PHASE_0_SKELETON",
        "green": green,
        "yellow": yellow,
        "red": red,
        "checks": results,
        "next_action": next_action,
    }


def session_shutdown(session_id: str, summary: str = "") -> dict:
    """AI Session 关闭 handoff — commit 成功后写 handoff package 供下一 session 恢复.

    对标: session_startup 的逆操作 — 启动时读 handoff, 关闭时写 handoff.
    对标: K8s Pod preStop hook — 终止前写状态供恢复.

    P4-T2 crash recovery: GitCommitGateway.commit() 成功后调用本函数,
    将 commit summary 写入 .runtime/handoffs/handoff_<session_id>.json,
    供下一 session 的 session_startup() 通过 read_latest_handoff() 恢复上下文.

    Args:
        session_id: session 标识
        summary: commit summary (message + GW marker)

    Returns:
        dict: {"written": bool, "path": str}
    """
    from zephyr.security.access_control.session_concurrency import SessionHandoff

    handoff = SessionHandoff()
    path = handoff.write_handoff(session_id, summary=summary)
    logger.info("session_shutdown: wrote handoff for session=%s path=%s", session_id, path)
    return {"written": path.exists(), "path": str(path)}
