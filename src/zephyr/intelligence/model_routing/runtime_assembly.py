# [BLUEPRINT] MOD-MODEL_ROUTER_ORCH | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/11_evidence_skill_router.md | §4.3
# [MODULE] zephyr.intelligence.model_routing.runtime_assembly
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_routing.cascade_orchestrator(CascadeOrchestrator/CascadeDecision/DEFAULT_POLICY_PATH 只消费不改); zephyr.intelligence.llm_agent_router(LlmAgentRouter/RouteRequest/AgentRouterConfig/RouteAuditRecord 只消费不改); zephyr.governance.intelligence_governance.model_router(TaskComplexity 只消费不改); zephyr.governance.ops_governance.budget_engine(BudgetEngine 台账只读); zephyr.governance.ops_governance.budget_models(BudgetDimension); zephyr.data.calendar(get_market_calendar 交易时段真源); zephyr.shared.io.paths(AUDIT_DATA_DIR); zephyr.trading.task_gate(TaskGate 懒加载 opt-in); zephyr.intelligence.model_profiling.exam_trigger_scheduler(ExamTriggerScheduler 懒加载 opt-in 登记拦截计数)
# [CONSUMERS] 06号文 Phase 2 dispatch 链 + AutoRuntime（经 assemble_agent_router 取装配完成的 LlmAgentRouter）；手动 CLI 冒烟入口（python -m zephyr.intelligence.model_routing.runtime_assembly）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只装配不改被接方逻辑（cascade_orchestrator/model_router/llm_agent_router 源文件零改动）; 级联异常降级返回 model=None 由门面走既有静态兜底（级联异常绝不阻断运行时路由）; 运行时装配默认懒加载（orchestrator/台账/日历/审计落盘均在首次调用时解析，assemble 本身不构造重基座）; 全部构造期依赖可注入 fake（测试零网络零真 LLM）; 时段词表=策略 period_rules 键（pre_open/call_auction/trading/post_close），门面旧词 intraday 由适配器映射为 trading; 审计落盘 append-only JSONL（16号文统一事件 schema：schema_version/event_id/ts/source/event_type/payload）; task_gate dispatch 硬门 opt-in（缺省 None 零行为变化；门控钩子异常 fail-closed 按拦截处理不阻断路由；复核建议 human_gated 不变量不动）; task_gate 影子模式 observe-only（ARCH-302：ZEPHYR_TASK_GATE_SHADOW=1 时记录 would-block 决策到 data/brain/task_gate_shadow_log.jsonl 但一律放行，shadow 下任何异常也只告警放行，绝不阻断路由）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CLI 参数非法（空 task_type/空候选）-> ValueError（fail-closed 输入校验）; 级联运行期异常不抛 -> decision_engine 返回 model=None 静态兜底+留痕; cost_ledger 台账异常不抛 -> 返回 0.0+告警（观测降级不阻断路由）; period 解析/日历异常 -> 返回 trading（最严时段 fail-closed）; audit_sink 异常由门面既有 try/except 捕获不阻断
# [TESTS] tests/intelligence/model_routing/test_runtime_assembly.py
# [A_module] module_id=MOD-MODEL_ROUTER_ORCH | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""
runtime_assembly — 模型路由级联的运行时装配层（11号文 §4.3 Phase 1 收尾）
================================================================================

把四个运行时真源接进 LlmAgentRouter（MOD-INT-AGENT-ROUTER）的注入缝，
被接方源文件零改动（只消费串联，与 cascade_orchestrator 同款纪律）：

- **decision_engine 接级联**：CascadeOrchestrator.route 适配为门面契约
  ``RouteRequest -> dict``（model/provider/reasons 字段映射；complexity 字符串
  -> TaskComplexity 枚举，非法值归 MODERATE；门面旧时段词 intraday -> 策略词
  trading）。级联任何异常降级为 ``{"model": None, ...}``——等价于门面
  decision_engine 缺省时的静态兜底路径，绝不让级联异常阻断运行时路由。
- **cost_ledger 接台账**：BudgetEngine.get_consumption_summary() 的 COST 维
  （BP-COST-001，美元口径，与 AgentRouterConfig.daily_budget_usd 同单位）
  daily 已耗值；台账异常按 0.0 观测降级（不阻断路由）。
- **audit_sink 接审计落盘**：RouteAuditRecord 逐条 append-only 写 JSONL，
  信封采 16号文 §4.2 P0-1 统一事件 schema 口径（schema_version/event_id/ts/
  source/event_type/payload），默认落 AUDIT_DATA_DIR/agent_router_audit.jsonl。
- **period 接交易时段真源**：data/calendar（94号 §4.1 策略对象，按市场注入）
  is_trading_day + Asia/Shanghai 墙钟 -> 策略 period_rules 词表
  （pre_open/call_auction/trading/post_close）；非交易日按 post_close（API
  allowed）；日历/解析异常 fail-closed 按 trading（最严时段）。
- **task_gate 接 dispatch 硬门（opt-in，默认不启用）**：TaskGate.can_dispatch
  经 ExamTriggerScheduler.check_and_record 适配为门面 task_gate 缝（判定同时
  登记拦截计数，连续 low_accuracy 超阈发复核建议，human_gated 不变量不动）；
  门控/调度器异常 fail-closed 按拦截处理，不阻断路由返回。
- **task_gate 影子模式（ARCH-302 金丝雀发布，observe-only）**：环境变量
  ``ZEPHYR_TASK_GATE_SHADOW=1`` 且 ``assemble_agent_router(task_gate=True)``
  时，dispatch 钩子照常过 TaskGate+调度器判定，但**一律放行**——决策
  （model_id/capability/gate_allowed/reason）append-only 落盘
  ``data/brain/task_gate_shadow_log.jsonl``（16号文统一事件信封），供观察期
  would-block 画像评审；shadow 下任何异常（含门控/落盘故障）也只告警放行，
  绝不阻断路由。影子日志路径可用 ``ZEPHYR_TASK_GATE_SHADOW_LOG`` 覆盖。

时段词表说明：门面 LlmAgentRouter 既有逻辑只特判 "intraday"（盘中强制本地），
级联策略 period_rules 词表为 pre_open/call_auction/trading/post_close。装配层
请求一律使用级联词表（时段限制由级联策略执行，严于门面旧词语义）；外部遗留
调用方传入 "intraday" 时由 decision_engine 适配器映射为 "trading" 再进级联。

用法
----
    router = assemble_agent_router()                      # 全默认懒加载真源
    dec = router.route(RouteRequest(task_type="signal_generation",
                                    candidates=["qwen3:8b"],
                                    period=current_trading_period()))

CLI 冒烟（dry-run 打印路由决策，不真调 LLM）：

    python -m zephyr.intelligence.model_routing.runtime_assembly \
        --task-type signal_generation --candidates qwen3:8b,qwen2.5-coder:14b
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import uuid
from dataclasses import asdict
from datetime import UTC, datetime, time as dt_time
from pathlib import Path
from typing import Any, Final
from zoneinfo import ZoneInfo

import yaml

from zephyr.governance.intelligence_governance.model_router import TaskComplexity
from zephyr.governance.ops_governance.budget_engine import BudgetEngine
from zephyr.governance.ops_governance.budget_models import BudgetDimension
from zephyr.intelligence.llm_agent_router import (
    AgentRouterConfig,
    LlmAgentRouter,
    RouteAuditRecord,
    RouteRequest,
)
from zephyr.intelligence.model_routing.cascade_orchestrator import (
    DEFAULT_POLICY_PATH,
    CascadeOrchestrator,
)
from zephyr.shared.io.paths import AUDIT_DATA_DIR, REPO_ROOT

__all__: Final = [
    "AUDIT_SCHEMA_VERSION",
    "DEFAULT_AUDIT_LOG_PATH",
    "DEFAULT_TASK_GATE_SHADOW_LOG_PATH",
    "TASK_GATE_SHADOW_ENV",
    "TASK_GATE_SHADOW_LOG_ENV",
    "assemble_agent_router",
    "budget_cost_ledger",
    "cascade_decision_engine",
    "current_trading_period",
    "default_router_config",
    "jsonl_audit_sink",
    "main",
    "task_gate_dispatch_hook",
    "task_gate_shadow_enabled",
]

_log = logging.getLogger(__name__)

# ── 时段词表与映射 ──
# 门面旧词 -> 级联策略 period_rules 词表（门面只特判 intraday，级联执行附表 B 时段限制）
_FACADE_TO_CASCADE_PERIOD: Final[dict[str, str]] = {"intraday": "trading"}

# A 股交易时段墙钟边界（Asia/Shanghai；与策略 period_rules 注释口径一致：
# 盘前 ~9:15 / 集合竞价 9:15-9:30 / 盘中 9:30-15:00 / 盘后 15:00~）
_BEIJING_TZ: Final = ZoneInfo("Asia/Shanghai")
_PRE_OPEN_END: Final = dt_time(9, 15)
_CALL_AUCTION_END: Final = dt_time(9, 30)
_TRADING_END: Final = dt_time(15, 0)

# BudgetEngine COST 维台账策略 ID（美元口径，与 AgentRouterConfig.daily_budget_usd 同单位）
_COST_POLICY_ID: Final = "BP-COST-001"

# 审计落盘默认路径与 16号文统一事件 schema 版本
DEFAULT_AUDIT_LOG_PATH: Final[Path] = AUDIT_DATA_DIR / "agent_router_audit.jsonl"
AUDIT_SCHEMA_VERSION: Final = "1.0"

# task_gate 影子模式（ARCH-302 observe-only）：开关环境变量 + 影子日志默认路径
# （与模型画像域同区 data/brain/，路径真源 REPO_ROOT 对齐 capability_passport 口径）
TASK_GATE_SHADOW_ENV: Final = "ZEPHYR_TASK_GATE_SHADOW"
TASK_GATE_SHADOW_LOG_ENV: Final = "ZEPHYR_TASK_GATE_SHADOW_LOG"
DEFAULT_TASK_GATE_SHADOW_LOG_PATH: Final[Path] = (
    REPO_ROOT / "data" / "brain" / "task_gate_shadow_log.jsonl"
)

# 级联路由表 preferred -> 门面 task_kinds 词表（门面 local_pref 判定：kind in (local, hybrid)）
_PREFERRED_TO_FACADE_KIND: Final[dict[str, str]] = {
    "local": "local",
    "hybrid": "hybrid",
    "api": "api",
    "api_multi": "api",
    "rule_engine": "rule",
}


# ── period 缝：data/calendar 交易时段真源 ──


def current_trading_period(
    now: datetime | None = None,
    *,
    calendar: Any | None = None,
    market: str = "ashare",
) -> str:
    """当前交易时段（策略 period_rules 词表：pre_open/call_auction/trading/post_close）。

    日历真源：data/calendar get_market_calendar（94号 §4.1 策略对象按市场注入）。
    非交易日按 post_close（无交易即无时段限制，API allowed）；naive datetime 按
    Asia/Shanghai 解释；日历/解析异常 fail-closed 返回 trading（最严时段）。
    """
    try:
        if now is None:
            moment = datetime.now(tz=_BEIJING_TZ)
        elif now.tzinfo is None:
            moment = now.replace(tzinfo=_BEIJING_TZ)
        else:
            moment = now.astimezone(_BEIJING_TZ)
        if calendar is None:
            from zephyr.data.calendar import get_market_calendar

            calendar = get_market_calendar(market)
        if not calendar.is_trading_day(moment.date()):
            return "post_close"
        t = moment.time()
        if t < _PRE_OPEN_END:
            return "pre_open"
        if t < _CALL_AUCTION_END:
            return "call_auction"
        if t < _TRADING_END:
            return "trading"
        return "post_close"
    except Exception as exc:  # noqa: BLE001 — 时段真源故障 fail-closed 按最严时段，不放行 API
        _log.warning("period 解析异常，fail-closed 按 trading（最严时段）处理: %s", exc)
        return "trading"


# ── decision_engine 缝：级联 -> 门面 dict 契约适配 ──


def cascade_decision_engine(orchestrator: Any) -> Any:
    """把 CascadeOrchestrator.route 适配为门面 decision_engine 契约（RouteRequest -> dict）。

    orchestrator 可为实例（duck-typed .route）或零参工厂（懒解析，首次调用才构造）。
    契约映射：model_key->model / provider->provider / reason+alerts+degraded_stages->reasons；
    complexity 字符串 -> TaskComplexity（非法值归 MODERATE）；门面旧词 intraday -> trading。
    级联任何异常（含懒构造失败）降级返回 model=None——等价门面静态兜底路径，不阻断路由。
    """
    if hasattr(orchestrator, "route"):
        resolve = lambda: orchestrator  # noqa: E731 — 单表达式闭包，无需 def
    else:
        resolve = orchestrator

    def engine(request: RouteRequest) -> dict[str, Any]:
        try:
            try:
                complexity = TaskComplexity(request.complexity)
            except ValueError:
                complexity = TaskComplexity.MODERATE
            period = _FACADE_TO_CASCADE_PERIOD.get(request.period, request.period)
            decision = resolve().route(
                request.task_type,
                list(request.candidates),
                complexity=complexity,
                period=period,
            )
        except Exception as exc:  # noqa: BLE001 — 级联异常绝不阻断运行时路由：model=None 走门面静态兜底
            _log.warning("级联路由异常，降级 model=None 由门面静态兜底: %s", exc)
            return {
                "model": None,
                "provider": "local",
                "reasons": [f"级联异常降级: {type(exc).__name__}: {exc}"],
            }
        reasons = [decision.reason, *decision.alerts]
        if decision.degraded_stages:
            reasons.append("degraded_stages:" + ",".join(decision.degraded_stages))
        if decision.risk_locked:
            reasons.append("risk_locked(HB-09)")
        return {"model": decision.model_key, "provider": decision.provider, "reasons": reasons}

    return engine


# ── cost_ledger 缝：BudgetEngine 台账（COST 维 daily，美元口径）──


def budget_cost_ledger(engine: Any | None = None) -> Any:
    """cost_ledger（() -> float）：BudgetEngine COST 维（BP-COST-001）当日已耗美元。

    engine 缺省首次调用时懒解析 BudgetEngine.ensure_initialized() 单例；
    台账异常不抛——按 0.0 观测降级并告警（路由不阻断，预算判定由门面自有日账兜底）。
    """

    def ledger() -> float:
        try:
            eng = engine if engine is not None else BudgetEngine.ensure_initialized()
            summary = eng.get_consumption_summary()
            return float(summary.get(_COST_POLICY_ID, {}).get("daily", 0.0))
        except Exception as exc:  # noqa: BLE001 — 观测降级不阻断路由
            _log.warning("cost_ledger 台账异常，按 0.0 观测降级: %s", exc)
            return 0.0

    return ledger


# ── audit_sink 缝：16号文统一事件 schema JSONL 落盘（append-only）──


def jsonl_audit_sink(path: Path | str | None = None) -> Any:
    """audit_sink（RouteAuditRecord -> None）：统一事件信封 append-only JSONL 落盘。

    信封口径对齐 16号文 §4.2 P0-1（schema_version/event_id/ts/source/event_type/
    payload）；path 缺省首次写入时解析 DEFAULT_AUDIT_LOG_PATH。落盘异常向调用方
    透传——由门面既有 try/except 捕获留痕，不阻断路由。
    """

    def sink(record: RouteAuditRecord) -> None:
        p = Path(path) if path is not None else DEFAULT_AUDIT_LOG_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "schema_version": AUDIT_SCHEMA_VERSION,
            "event_id": uuid.uuid4().hex[:16],
            "ts": datetime.now(tz=UTC).isoformat(),
            "source": "llm_agent_router",
            "event_type": "agent_route_decision",
            "payload": asdict(record),
        }
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    return sink


# ── task_gate 缝：TaskGate + ExamTriggerScheduler dispatch 硬门（06号文 §2.1，opt-in）──
#            + ARCH-302 影子模式（observe-only 金丝雀：记录 would-block 但一律放行）


def task_gate_shadow_enabled(env: Any | None = None) -> bool:
    """影子模式开关（ARCH-302）：``ZEPHYR_TASK_GATE_SHADOW`` 真值（1/true/yes/on）即启用。

    仅决定 task_gate=True 时装配影子钩子还是硬门钩子；不自行开启 task_gate
    （opt-in 语义不变——task_gate=None 时本开关零效果）。
    """
    source = os.environ if env is None else env
    return str(source.get(TASK_GATE_SHADOW_ENV, "")).strip().lower() in ("1", "true", "yes", "on")


def _record_shadow_decision(
    path: Path | str | None,
    model_id: str,
    capability: str,
    gate_allowed: bool,
    reason: str,
) -> None:
    """影子决策 append-only JSONL 落盘（16号文统一事件信封；gate_allowed=门原始判定）。

    path 缺省解析顺序：``ZEPHYR_TASK_GATE_SHADOW_LOG`` 环境变量 ->
    DEFAULT_TASK_GATE_SHADOW_LOG_PATH（data/brain/task_gate_shadow_log.jsonl）。
    调用方负责异常兜底（shadow 语义下落盘故障绝不阻断路由）。
    """
    if path is None:
        path = os.environ.get(TASK_GATE_SHADOW_LOG_ENV) or DEFAULT_TASK_GATE_SHADOW_LOG_PATH
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "event_id": uuid.uuid4().hex[:16],
        "ts": datetime.now(tz=UTC).isoformat(),
        "source": "task_gate_dispatch_hook",
        "event_type": "task_gate_shadow_decision",
        "payload": {
            "model_id": model_id,
            "capability": capability,
            "gate_allowed": gate_allowed,
            "would_block": not gate_allowed,
            "reason": reason,
        },
    }
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def task_gate_dispatch_hook(
    gate: Any | None = None,
    scheduler: Any | None = None,
    *,
    shadow: bool = False,
    shadow_log_path: Path | str | None = None,
) -> Any:
    """task_gate 缝：TaskGate + ExamTriggerScheduler 适配为门面 task_gate 契约
    ``(model_id, capability) -> (bool, reason)``。

    判定经 ExamTriggerScheduler.check_and_record 透传 TaskGate.can_dispatch 并登记
    拦截计数（连续 low_accuracy 超阈自动发复核建议，human_gated 不变量不动）。
    gate/scheduler 缺省首次调用时懒构造（TaskGate.load_passports 全量护照 +
    ExamTriggerScheduler 默认参数）。

    非 shadow（默认）：任何异常不抛 -> (False, reason) fail-closed 由门面按拦截
    语义处理。

    shadow=True（ARCH-302 影子模式，observe-only）：照常过门判定并登记计数，
    决策落盘影子日志（_record_shadow_decision），但**一律返回放行**——
    would-block 仅供观察期画像评审；任何异常（门控/调度器/落盘故障）也只告警
    放行，绝不阻断路由。
    """
    holder: list[Any] = [gate, scheduler]

    def _resolve() -> tuple[Any, Any]:
        if holder[0] is None:
            from zephyr.trading.task_gate import TaskGate

            real_gate = TaskGate()
            real_gate.load_passports()
            holder[0] = real_gate
        if holder[1] is None:
            from zephyr.intelligence.model_profiling.exam_trigger_scheduler import (
                ExamTriggerScheduler,
            )

            holder[1] = ExamTriggerScheduler()
        return holder[0], holder[1]

    def hook(model_id: str, capability: str) -> tuple[bool, str]:
        if shadow:
            try:
                g, s = _resolve()
                allowed, reason = s.check_and_record(g, model_id, capability)
                _record_shadow_decision(
                    shadow_log_path, model_id, capability, bool(allowed), str(reason)
                )
                return (True, f"shadow 放行(gate_allowed={bool(allowed)}): {reason}")
            except Exception as exc:  # noqa: BLE001 — shadow observe-only：异常只告警放行，绝不阻断路由
                _log.warning("task_gate shadow 钩子异常，observe-only 放行: %s", exc)
                return (True, f"shadow 放行(钩子异常 {type(exc).__name__}): {exc}")
        try:
            g, s = _resolve()
            allowed, reason = s.check_and_record(g, model_id, capability)
            return (bool(allowed), str(reason))
        except Exception as exc:  # noqa: BLE001 — 门控异常 fail-closed 按拦截处理，不阻断路由调用
            _log.warning("task_gate 钩子异常，fail-closed 按拦截处理: %s", exc)
            return (False, f"task_gate 异常: {type(exc).__name__}: {exc}")

    return hook


# ── 装配入口 ──


def _load_task_kinds(policy_path: Path | str | None) -> dict[str, str]:
    """从级联策略 task_routes.preferred 导出门面 task_kinds 词表（配置真源不重抄）。"""
    path = Path(policy_path) if policy_path is not None else DEFAULT_POLICY_PATH
    policy = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    task_routes = policy.get("task_routes", {})
    return {
        task: _PREFERRED_TO_FACADE_KIND.get(str(spec.get("preferred", "")), "general")
        for task, spec in task_routes.items()
        if isinstance(spec, dict)
    }


def default_router_config(
    *,
    daily_budget_usd: float | None = None,
    policy_path: Path | str | None = None,
) -> AgentRouterConfig:
    """缺省门面配置：task_kinds 源自级联策略 task_routes；日预算缺省=BudgetEngine
    COST 维策略 daily_limit（BP-COST-001，美元口径真源，不另立数值）。"""
    if daily_budget_usd is None:
        daily_budget_usd = float(BudgetEngine.DEFAULT_POLICIES[BudgetDimension.COST].daily_limit)
    return AgentRouterConfig(
        daily_budget_usd=float(daily_budget_usd),
        period_rules={"task_kinds": _load_task_kinds(policy_path)},
    )


def assemble_agent_router(
    config: AgentRouterConfig | None = None,
    *,
    orchestrator: Any | None = None,
    cost_ledger: Any | None = None,
    audit_sink: Any | None = None,
    clock: Any | None = None,
    policy_path: Path | str | None = None,
    audit_log_path: Path | str | None = None,
    daily_budget_usd: float | None = None,
    task_gate: Any | None = None,
) -> LlmAgentRouter:
    """装配运行时 LlmAgentRouter：四缝接真源，全部构造期依赖可注入 fake。

    config 缺省走 default_router_config（task_kinds 源自级联策略）；orchestrator
    缺省懒构造 CascadeOrchestrator（首次 route 才解析，其内部三基座仍各自懒加载）；
    cost_ledger 缺省接 BudgetEngine COST 台账；audit_sink 缺省 16号文统一事件
    JSONL 落盘。
    task_gate（06号文 §2.1 dispatch 硬门）opt-in：缺省 None 不启用（零行为变化）；
    True 接 TaskGate+ExamTriggerScheduler 生产硬门（首次调用懒构造）；可直接注入
    fake callable 测试。task_gate=True 且环境变量 ZEPHYR_TASK_GATE_SHADOW 为真值时
    装配影子钩子（ARCH-302 observe-only：照常判定+落影子日志但一律放行，见
    task_gate_dispatch_hook）；task_gate=None 时影子开关零效果（opt-in 语义不变）。
    """
    if config is None:
        config = default_router_config(daily_budget_usd=daily_budget_usd, policy_path=policy_path)
    holder: list[Any] = [orchestrator]

    def _resolve_orchestrator() -> Any:
        if holder[0] is None:
            holder[0] = CascadeOrchestrator(policy_path=policy_path)
        return holder[0]

    if task_gate is True:
        task_gate = task_gate_dispatch_hook(shadow=task_gate_shadow_enabled())

    return LlmAgentRouter(
        config,
        decision_engine=cascade_decision_engine(_resolve_orchestrator),
        cost_ledger=cost_ledger or budget_cost_ledger(),
        audit_sink=audit_sink or jsonl_audit_sink(audit_log_path),
        clock=clock,
        task_gate=task_gate,
    )


# ── 手动 CLI 冒烟（dry-run 打印路由决策，不真调 LLM）──


def main(argv: list[str] | None = None, *, router_factory: Any | None = None) -> int:
    """CLI 入口：装配 -> 单次路由 -> 打印决策 JSON。audit 打印到 stdout（不落盘）。"""
    parser = argparse.ArgumentParser(
        prog="runtime_assembly",
        description="模型路由级联运行时装配冒烟（dry-run 打印路由决策，不真调 LLM）",
    )
    parser.add_argument("--task-type", required=True, help="任务类型（策略 task_routes 键）")
    parser.add_argument(
        "--candidates",
        default="qwen3:8b,qwen2.5-coder:14b",
        help="逗号分隔候选模型（缺省=qwen3:8b,qwen2.5-coder:14b）",
    )
    parser.add_argument("--complexity", default="moderate", help="simple/moderate/complex")
    parser.add_argument("--period", default=None, help="缺省取 data/calendar 交易时段真源")
    args = parser.parse_args(argv)

    task_type = args.task_type.strip()
    if not task_type:
        raise ValueError("--task-type 不能为空（fail-closed 输入校验）")
    candidates = [c.strip() for c in args.candidates.split(",") if c.strip()]
    if not candidates:
        raise ValueError("--candidates 解析后为空（fail-closed 输入校验）")
    period = args.period or current_trading_period()

    def _stdout_sink(record: RouteAuditRecord) -> None:
        print("audit:", json.dumps(asdict(record), ensure_ascii=False, sort_keys=True))

    factory = router_factory if router_factory is not None else assemble_agent_router
    router = factory(audit_sink=_stdout_sink)
    request = RouteRequest(
        task_type=task_type,
        candidates=candidates,
        period=period,
        complexity=args.complexity,
    )
    decision = router.route(request)
    print(json.dumps(asdict(decision), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
