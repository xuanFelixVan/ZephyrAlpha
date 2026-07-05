# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.agent_orchestrator
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.input_sanitizer; zephyr.integration.shared.schema.schemas; zephyr.shared.utils.time_utils; zephyr.autonomy_core.token_budget; zephyr.shared.contracts.security.__init__; zephyr.security.llm_defense.llm_security.gateway
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
# [A_module] module_id=MOD-ORC_agent_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-3-10 Agent Orchestrator (
"""
AgentOrchestrator · 多角色 Agent 路由、工具链编排与健康监控
===========================================================

Task ID     : T-3-10 (A22)
KBG         :  协作边界 + 6 角色 × 10 域矩阵）
Depends     : T-3-09（ 决策）、T-3-04（MCP Server 基础设施）、
              T-3-07（hallucination_detector.CoVe 后置钩子）
safety_level: H

病根澄清（审计易混点）
---------------------
名称含 *Orchestrator* 常与「TaskCard 生命周期编排」混淆。**本模块真源为
Agent / MCP 工具调用链**，**不读写** ``TaskCard.status``。**任务十态与合法迁移**
见 ``zephyr.shared.schemas.TaskStatus`` 与 ``zephyr.governance.persistence.task_repo.TaskRepository``。

本模块职责
----------
在**不外接**任何生产 LLM / 任务队列 SDK 的前提下，提供一个
**纯内存、可注入**的多角色 Agent 编排层，覆盖：

1. **AgentRouter（无状态路由）**
   - 6 角色 × 10 域（D0~D9）静态映射表
   - 四种路由策略：
     ``capability_match`` / ``load_balance`` / ``specialist_first`` / ``fallback_chain``
   - 路由决策不落盘；load 信息由外部注入

2. **Orchestrator Agent（directive ↔ MCP tool 链编排）**
   - 将 DOS directive（如 "325+344+999"）解析成 MCP 工具链
   - 逐 tool 调用注入的 ``ToolInvoker`` 协议，收集每步日志
   - **CoVe post-hook**：在最终产出 ``claim`` 上调用
     ``hallucination_detector.HallucinationDetector.detect``，
     并把结果附加到 ``OrchestrationResult.hallucination``

3. **HealthMonitor（5 项 SLO）**
   - ``latency_p99`` 毫秒
   - ``error_rate`` 0-1
   - ``throughput`` 每分钟完成任务数
   - ``hallucination_rate`` 0-1（来自 CoVe post-hook）
   - ``context_utilization`` 0-1（token_used / token_budget）

设计原则
--------
- **零外部依赖**：仅使用 ``pydantic`` + 标准库；不 import mcp 具体 Server
  实现，避免循环依赖；通过 ``ToolInvoker`` / ``HallucinationCaller`` Protocol 注入。
- **纯内存状态**：Orchestrator 本身无持久化；健康指标累计保留在
  ``HealthMonitor`` 内部的固定窗口滑动队列中。
- **可测试**：时间源 ``now`` 与 UUID 生成器 ``id_factory`` 均可注入。
"""

from __future__ import annotations

import json
import logging
import statistics
import time
import uuid
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界
from typing import (
    Any,
    Literal,
    Protocol,
    runtime_checkable,
)

from pydantic import BaseModel, Field, field_validator

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import default_now
from zephyr.security.llm_defense.llm_security.input_sanitizer import ContextInjectionError, InputSanitizer
from zephyr.infrastructure.capacity_assurance.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_ROLE_DOMAIN_MATRIX",
    "AgentOrchestrator",
    "AgentProfile",
    "AgentRole",
    "AgentRouter",
    "HallucinationCaller",
    "HealthMonitor",
    "OrchestrationResult",
    "RouteDecision",
    "RoutingStrategy",
    "SLOSnapshot",
    "ToolCallRecord",
    "ToolInvoker",
]

# ---------------------------------------------------------------------------
# 枚举与常量
# ---------------------------------------------------------------------------


class AgentRole(str, Enum):
    """§3 — 6 个 Agent 角色。"""

    ARCHITECT = "architect"  # 架构师：蓝图/KBG/模块拆分
    IMPLEMENTER = "implementer"  # 实施者：代码产出与修复
    REVIEWER = "reviewer"  # 复核者：评审/CoVe/SSoT 校对
    GOVERNOR = "governor"  # 治理官：合规/标准/审计
    RESEARCHER = "researcher"  # 研究员：因子/策略/实验
    OPERATOR = "operator"  # 运营员：运行/监控/回放


class RoutingStrategy(str, Enum):
    """四种路由策略。"""

    CAPABILITY_MATCH = "capability_match"
    LOAD_BALANCE = "load_balance"
    SPECIALIST_FIRST = "specialist_first"
    FALLBACK_CHAIN = "fallback_chain"


#  §3.2 — 6 角色 × 10 域静态映射
# 每个 (role, domain) 有一个 0.0-1.0 的 capability score；0.0 表示不覆盖
DEFAULT_ROLE_DOMAIN_MATRIX: dict[AgentRole, dict[str, float]] = {
    AgentRole.ARCHITECT: {
        "D0": 0.8,
        "D1": 0.4,
        "D2": 1.0,
        "D3": 0.5,
        "D4": 0.5,
        "D5": 0.4,
        "D6": 0.6,
        "D7": 0.3,
        "D8": 0.4,
        "D9": 0.3,
    },
    AgentRole.IMPLEMENTER: {
        "D0": 0.5,
        "D1": 0.8,
        "D2": 0.6,
        "D3": 0.7,
        "D4": 0.7,
        "D5": 0.5,
        "D6": 0.3,
        "D7": 0.4,
        "D8": 0.6,
        "D9": 1.0,
    },
    AgentRole.REVIEWER: {
        "D0": 0.6,
        "D1": 0.5,
        "D2": 0.7,
        "D3": 0.6,
        "D4": 0.6,
        "D5": 0.7,
        "D6": 0.9,
        "D7": 0.5,
        "D8": 0.4,
        "D9": 0.6,
    },
    AgentRole.GOVERNOR: {
        "D0": 0.9,
        "D1": 0.4,
        "D2": 0.5,
        "D3": 0.2,
        "D4": 0.2,
        "D5": 0.6,
        "D6": 1.0,
        "D7": 0.3,
        "D8": 0.3,
        "D9": 0.3,
    },
    AgentRole.RESEARCHER: {
        "D0": 0.3,
        "D1": 0.7,
        "D2": 0.4,
        "D3": 1.0,
        "D4": 0.9,
        "D5": 0.5,
        "D6": 0.2,
        "D7": 0.7,
        "D8": 0.2,
        "D9": 0.3,
    },
    AgentRole.OPERATOR: {
        "D0": 0.7,
        "D1": 0.6,
        "D2": 0.2,
        "D3": 0.3,
        "D4": 0.4,
        "D5": 0.7,
        "D6": 0.4,
        "D7": 1.0,
        "D8": 0.8,
        "D9": 0.8,
    },
}

# ---------------------------------------------------------------------------
# 数据契约
# ---------------------------------------------------------------------------


class AgentProfile(BaseModel):
    """单个 Agent 实例的状态画像（用于 load_balance 策略）。"""

    model_config = BASE_CONFIG

    agent_id: str = Field(min_length=1, description="Agent 实例 ID")
    role: AgentRole = Field(description="Agent 角色")
    current_load: int = Field(default=0, ge=0, description="当前并发任务数")
    max_load: int = Field(default=5, ge=1, description="最大并发阈值")
    healthy: bool = Field(default=True, description="是否健康可用")

    @property
    def utilization(self) -> float:
        """当前负载率 = current_load / max_load。"""
        return self.current_load / self.max_load if self.max_load else 1.0


class RouteDecision(BaseModel):
    """路由器决策输出。"""

    model_config = BASE_CONFIG

    domain: str = Field(min_length=1, description="目标域 D0-D9")
    strategy: RoutingStrategy = Field(description="使用的路由策略")
    primary_role: AgentRole = Field(description="首选角色")
    primary_agent_id: str | None = Field(default=None, description="首选 Agent 实例 ID")
    fallback_roles: list[AgentRole] = Field(default_factory=list, description="回退角色链")
    capability_score: float = Field(ge=0.0, le=1.0, description="首选角色在该域的能力分")
    rationale: str = Field(default="", description="决策解释")


class ToolCallRecord(BaseModel):
    """单次 MCP 工具调用记录。"""

    model_config = BASE_CONFIG

    directive: str = Field(description="触发该调用的 DOS directive id")
    tool_name: str = Field(description="MCP 工具全名")
    arguments: dict[str, Any] = Field(default_factory=dict, description="调用参数")
    success: bool = Field(description="是否成功")
    latency_ms: int = Field(ge=0, description="耗时毫秒")
    error: str | None = Field(default=None, description="失败原因")
    result_preview: str = Field(default="", description="结果摘要（截断 400 字符）")


class OrchestrationResult(BaseModel):
    """单次 orchestrate() 的最终输出。"""

    model_config = BASE_CONFIG

    task_id: str = Field(min_length=1)
    route: RouteDecision
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    claim: str = Field(default="", description="最终对外 claim（用于 CoVe 后置检测）")
    hallucination: dict[str, Any] | None = Field(
        default=None, description="CoVe post-hook 输出（HallucinationResult.model_dump）"
    )
    success: bool = Field(description="整链是否成功")
    latency_ms: int = Field(ge=0)
    token_used: int = Field(default=0, ge=0)
    token_budget: int = Field(default=0, ge=0)
    errors: list[str] = Field(default_factory=list)

    @field_validator("claim")
    @classmethod
    def _strip_claim(cls, v: str) -> str:
        return v.strip()


class SLOSnapshot(BaseModel):
    """5 项 SLO 快照。"""

    model_config = BASE_CONFIG

    latency_p99_ms: float = Field(ge=0.0)
    error_rate: float = Field(ge=0.0, le=1.0)
    throughput_per_min: float = Field(ge=0.0)
    hallucination_rate: float = Field(ge=0.0, le=1.0)
    context_utilization: float = Field(ge=0.0, le=1.0)
    window_size: int = Field(ge=0)
    healthy: bool = Field(description="是否全部 SLO 达标")


# ---------------------------------------------------------------------------
# 协议：依赖注入（解耦 MCP 与 CoVe）
# ---------------------------------------------------------------------------


@runtime_checkable
class ToolInvoker(Protocol):
    """MCP 工具调用协议。生产中由 MCP client 适配；测试传 mock。"""

    def __call__(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover - Protocol 签名
        ...


@runtime_checkable
class HallucinationCaller(Protocol):
    """CoVe 检测器协议。生产传 ``HallucinationDetector.detect``。"""

    def __call__(
        self, claim: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:  # pragma: no cover - Protocol 签名
        ...


# ---------------------------------------------------------------------------
# AgentRouter — 无状态路由
# ---------------------------------------------------------------------------


class AgentRouter:
    """6 角色 × 10 域的无状态路由器。

    Parameters
    ----------
    matrix : dict[AgentRole, dict[str, float]] | None
        角色-域能力矩阵；默认使用 ``DEFAULT_ROLE_DOMAIN_MATRIX``。
    agent_pool : list[AgentProfile] | None
        可用 Agent 实例池（load_balance 策略需要）。
    """

    def __init__(
        self,
        matrix: dict[AgentRole, dict[str, float]] | None = None,
        agent_pool: list[AgentProfile] | None = None,
    ) -> None:
        self._matrix = matrix or DEFAULT_ROLE_DOMAIN_MATRIX
        self._pool: list[AgentProfile] = list(agent_pool or [])

    @property
    def pool_size(self) -> int:
        return len(self._pool)

    def register(self, agent: AgentProfile) -> None:
        """注册一个 Agent 实例到内存池。"""
        self._pool = [a for a in self._pool if a.agent_id != agent.agent_id]
        self._pool.append(agent)

    def update_load(self, agent_id: str, *, delta: int) -> None:
        """增减指定 Agent 的当前负载。"""
        for a in self._pool:
            if a.agent_id == agent_id:
                a.current_load = max(0, a.current_load + delta)
                return

    def score(self, role: AgentRole, domain: str) -> float:
        """查询 (role, domain) 的能力分。"""
        return self._matrix.get(role, {}).get(domain, 0.0)

    def route(
        self,
        domain: str,
        *,
        strategy: RoutingStrategy = RoutingStrategy.CAPABILITY_MATCH,
        required_role: AgentRole | None = None,
    ) -> RouteDecision:
        """按策略返回路由决策。

        Parameters
        ----------
        domain : str
            目标域 D0-D9。未登记的域会回退到所有角色 score=0，
            ``primary_role`` 取字典序最小的角色，``capability_score=0``。
        strategy : RoutingStrategy
            路由策略，默认 capability_match。
        required_role : AgentRole | None
            specialist_first 策略必须指定。

        Returns
        -------
        RouteDecision
        """
        if strategy is RoutingStrategy.SPECIALIST_FIRST:
            if required_role is None:
                raise ValueError("specialist_first 策略必须指定 required_role")
            return self._specialist_first(domain, required_role)

        if strategy is RoutingStrategy.LOAD_BALANCE:
            return self._load_balance(domain)

        if strategy is RoutingStrategy.FALLBACK_CHAIN:
            return self._fallback_chain(domain)

        return self._capability_match(domain)

    # ---- strategies ---------------------------------------------------

    def _capability_match(self, domain: str) -> RouteDecision:
        ranked = self._ranked_roles(domain)
        primary_role, primary_score = ranked[0]
        agent_id = self._pick_agent(primary_role)
        return RouteDecision(
            domain=domain,
            strategy=RoutingStrategy.CAPABILITY_MATCH,
            primary_role=primary_role,
            primary_agent_id=agent_id,
            fallback_roles=[r for r, _ in ranked[1:3]],
            capability_score=primary_score,
            rationale=f"capability_match: {primary_role.value}={primary_score:.2f}",
        )

    def _load_balance(self, domain: str) -> RouteDecision:
        """加权：score × (1 - utilization)；取最大。"""
        ranked = self._ranked_roles(domain)
        best_role = ranked[0][0]
        best_score = ranked[0][1]
        best_agent: AgentProfile | None = None
        best_metric = -1.0
        for role, score in ranked:
            if score <= 0.0:
                continue
            for agent in self._pool:
                if agent.role != role or not agent.healthy:
                    continue
                metric = score * (1.0 - agent.utilization)
                if metric > best_metric:
                    best_metric = metric
                    best_role = role
                    best_score = score
                    best_agent = agent
        return RouteDecision(
            domain=domain,
            strategy=RoutingStrategy.LOAD_BALANCE,
            primary_role=best_role,
            primary_agent_id=best_agent.agent_id if best_agent else None,
            fallback_roles=[r for r, _ in ranked[1:3] if r != best_role],
            capability_score=best_score,
            rationale=(
                f"load_balance: score={best_score:.2f} util={best_agent.utilization:.2f}"
                if best_agent
                else "load_balance: no-agent"
            ),
        )

    def _specialist_first(self, domain: str, required_role: AgentRole) -> RouteDecision:
        """强制指定角色，失败再回退到 capability_match 的 top-2。"""
        score = self.score(required_role, domain)
        ranked = self._ranked_roles(domain)
        fallbacks = [r for r, _ in ranked if r != required_role][:2]
        agent_id = self._pick_agent(required_role)
        return RouteDecision(
            domain=domain,
            strategy=RoutingStrategy.SPECIALIST_FIRST,
            primary_role=required_role,
            primary_agent_id=agent_id,
            fallback_roles=fallbacks,
            capability_score=score,
            rationale=f"specialist_first: forced {required_role.value} (score={score:.2f})",
        )

    def _fallback_chain(self, domain: str) -> RouteDecision:
        """按 capability 降序产生一条完整链，首位是 primary。"""
        ranked = self._ranked_roles(domain)
        primary_role, primary_score = ranked[0]
        chain = [r for r, _ in ranked[1:]]
        return RouteDecision(
            domain=domain,
            strategy=RoutingStrategy.FALLBACK_CHAIN,
            primary_role=primary_role,
            primary_agent_id=self._pick_agent(primary_role),
            fallback_roles=chain,
            capability_score=primary_score,
            rationale=f"fallback_chain: {len(chain) + 1} roles",
        )

    # ---- helpers ------------------------------------------------------

    def _ranked_roles(self, domain: str) -> list[tuple[AgentRole, float]]:
        """按 capability_score 降序返回 (role, score) 列表。"""
        scored = [(role, self.score(role, domain)) for role in AgentRole]
        scored.sort(key=lambda x: (-x[1], x[0].value))
        return scored

    def _pick_agent(self, role: AgentRole) -> str | None:
        """在池中挑选一个健康且负载最低的该角色 Agent。"""
        candidates = [a for a in self._pool if a.role == role and a.healthy]
        if not candidates:
            return None
        candidates.sort(key=lambda a: (a.utilization, a.agent_id))
        return candidates[0].agent_id


# ---------------------------------------------------------------------------
# HealthMonitor — 5 项 SLO
# ---------------------------------------------------------------------------


class HealthMonitor:
    """滑窗口累计 5 项 SLO 的健康监控器。

    Parameters
    ----------
    window_size : int
        最近 N 次 orchestrate 的事件窗口（默认 100）。
    thresholds : dict[str, float] | None
        5 项 SLO 的健康阈值；超出则 ``healthy=False``。
    throughput_window_sec : int
        吞吐量统计窗口（默认 60s）。
    now : Callable[[], datetime]
        时间源，便于测试。
    """

    DEFAULT_THRESHOLDS: dict[str, float] = {
        "latency_p99_ms": 5000.0,
        "error_rate": 0.1,
        "throughput_per_min": 1.0,  # 最低吞吐；低于此值视为停滞
        "hallucination_rate": 0.15,
        "context_utilization": 0.9,
    }

    def __init__(
        self,
        window_size: int = 100,
        thresholds: dict[str, float] | None = None,
        throughput_window_sec: int = 60,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        if window_size < 1:
            raise ValueError("window_size 必须 >= 1")
        self._window = window_size
        self._thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
        self._throughput_window_sec = throughput_window_sec
        self._now = now
        self._latencies: deque[float] = deque(maxlen=window_size)
        self._errors: deque[int] = deque(maxlen=window_size)
        self._hallu: deque[int] = deque(maxlen=window_size)
        self._ctx_util: deque[float] = deque(maxlen=window_size)
        self._completions: deque[datetime] = deque(maxlen=window_size * 4)

    # ---- public -------------------------------------------------------

    def record(self, result: OrchestrationResult) -> None:
        """注入一次 orchestrate 结果，自动累计 5 项指标。"""
        self._latencies.append(float(result.latency_ms))
        self._errors.append(0 if result.success else 1)
        is_hallu = bool(result.hallucination is not None and result.hallucination.get("is_hallucination"))
        self._hallu.append(1 if is_hallu else 0)
        if result.token_budget > 0:
            self._ctx_util.append(result.token_used / result.token_budget)
        else:
            self._ctx_util.append(0.0)
        self._completions.append(self._now())

    def snapshot(self) -> SLOSnapshot:
        """生成当前窗口的 SLO 快照。"""
        latency_p99 = self._percentile(list(self._latencies), 99) if self._latencies else 0.0
        error_rate = (sum(self._errors) / len(self._errors)) if self._errors else 0.0
        hallu_rate = (sum(self._hallu) / len(self._hallu)) if self._hallu else 0.0
        ctx_util = sum(self._ctx_util) / len(self._ctx_util) if self._ctx_util else 0.0
        throughput = self._recent_throughput_per_min()
        healthy = self._evaluate_healthy(latency_p99, error_rate, throughput, hallu_rate, ctx_util)
        return SLOSnapshot(
            latency_p99_ms=round(latency_p99, 3),
            error_rate=round(error_rate, 4),
            throughput_per_min=round(throughput, 3),
            hallucination_rate=round(hallu_rate, 4),
            context_utilization=round(min(ctx_util, 1.0), 4),
            window_size=len(self._latencies),
            healthy=healthy,
        )

    def reset(self) -> None:
        """清空历史窗口。"""
        self._latencies.clear()
        self._errors.clear()
        self._hallu.clear()
        self._ctx_util.clear()
        self._completions.clear()

    # ---- helpers ------------------------------------------------------

    @staticmethod
    def _percentile(values: list[float], pct: float) -> float:
        """简易 p99：对有序序列取索引 ceil(n * pct / 100) - 1。"""
        if not values:
            return 0.0
        sorted_v = sorted(values)
        if len(sorted_v) == 1:
            return sorted_v[0]
        # nearest-rank 法，向上取整
        rank = max(1, int(round(len(sorted_v) * pct / 100.0 + 0.5)) - 1)
        rank = min(rank, len(sorted_v) - 1)
        return sorted_v[rank]

    def _recent_throughput_per_min(self) -> float:
        if not self._completions:
            return 0.0
        now = self._now()
        window_start = now.timestamp() - self._throughput_window_sec
        count = sum(1 for ts in self._completions if ts.timestamp() >= window_start)
        return count * (60.0 / self._throughput_window_sec)

    def _evaluate_healthy(
        self,
        latency_p99: float,
        error_rate: float,
        throughput: float,
        hallu_rate: float,
        ctx_util: float,
    ) -> bool:
        if latency_p99 > self._thresholds["latency_p99_ms"]:
            return False
        if error_rate > self._thresholds["error_rate"]:
            return False
        if hallu_rate > self._thresholds["hallucination_rate"]:
            return False
        if ctx_util > self._thresholds["context_utilization"]:
            return False
        # throughput 门禁仅在窗口已满时触发（避免冷启动误报）
        if len(self._latencies) >= self._window and throughput < self._thresholds["throughput_per_min"]:
            return False
        return True

    # 仅用于统计辅助
    @property
    def sample_count(self) -> int:
        return len(self._latencies)


# ---------------------------------------------------------------------------
# Orchestrator — directive ↔ MCP 工具链编排
# ---------------------------------------------------------------------------

# directive -> (tool_name, 默认参数构造器) 映射。生产可替换注入。
DirectiveChain = list[tuple[str, str, dict[str, Any]]]

# agent_orchestrator.py 位于 src/zephyr/orchestrator/ → 仓库根为 parents[3]


class AgentOrchestrator:
    """Orchestrator Agent：将 directive 序列编排为 MCP 工具链，并运行 CoVe post-hook。

    Parameters
    ----------
    router : AgentRouter
        路由器实例。
    tool_invoker : ToolInvoker | None
        MCP 工具调用者；None 时 orchestrate() 会直接将每步标为失败
        （便于离线单测）。
    hallucination_caller : HallucinationCaller | None
        CoVe 检测器回调；None 时跳过 post-hook。
    directive_mapping : dict[str, list[tuple[str, dict[str, Any]]]] | None
        directive_id -> [(tool_name, arguments), ...] 映射；生产可注入真实契约。
    monitor : HealthMonitor | None
        健康监控器；None 时内部新建一个默认监控器。
    now : Callable[[], datetime]
        时间源。
    id_factory : Callable[[], str]
        task_id 工厂；默认生成 ``T-ORCH-<uuid4-hex12>``。
    default_token_budget : int
        token 预算默认值，用于 context_utilization 基准。
    sanitize_llm_context : bool
        True 时在未显式注入 ``input_sanitizer`` 的情况下，使用仓库根目录构造默认
        ``InputSanitizer``，在编排与 CoVe 之前校验 ``claim`` / ``context``（CT-CE-LSG-001 L1）。
    input_sanitizer : InputSanitizer | None
        非 None 时始终使用该实例（与 ``sanitize_llm_context`` 独立）；若需完全关闭校验，请传
        ``input_sanitizer=None`` 且 ``sanitize_llm_context=False``。
    """

    def __init__(
        self,
        router: AgentRouter,
        *,
        tool_invoker: ToolInvoker | None = None,
        hallucination_caller: HallucinationCaller | None = None,
        directive_mapping: dict[str, list[tuple[str, dict[str, Any]]]] | None = None,
        monitor: HealthMonitor | None = None,
        now: Callable[[], datetime] = default_now,
        id_factory: Callable[[], str] | None = None,
        default_token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
        sanitize_llm_context: bool = True,
        input_sanitizer: InputSanitizer | None = None,
    ) -> None:
        self._router = router
        self._invoker = tool_invoker
        self._cove = hallucination_caller
        self._mapping = directive_mapping or {}
        self._monitor = monitor or HealthMonitor()
        self._now = now
        self._id_factory = id_factory or (lambda: f"T-ORCH-{uuid.uuid4().hex[:12]}")
        self._default_budget = default_token_budget
        if input_sanitizer is not None:
            self._input_sanitizer = input_sanitizer
        elif sanitize_llm_context:
            self._input_sanitizer = InputSanitizer(root=str(REPO_ROOT))
        else:
            self._input_sanitizer = None

    # ---- accessors ---------------------------------------------------

    @property
    def router(self) -> AgentRouter:
        return self._router

    @property
    def monitor(self) -> HealthMonitor:
        return self._monitor

    # ---- main orchestration ------------------------------------------

    def orchestrate(
        self,
        *,
        domain: str,
        directive_chain: str,
        claim: str = "",
        context: dict[str, Any] | None = None,
        strategy: RoutingStrategy = RoutingStrategy.CAPABILITY_MATCH,
        required_role: AgentRole | None = None,
        token_used: int = 0,
        token_budget: int | None = None,
        task_id: str | None = None,
    ) -> OrchestrationResult:
        """对一个 directive 链执行 MCP 工具编排 + CoVe post-hook。

        Parameters
        ----------
        domain : str
            目标域 D0-D9。
        directive_chain : str
            ``"325+344+999"`` 形式的 directive 串，或空串（仅走 CoVe）。
        claim : str
            最终 claim（将传入 CoVe）。
        context : dict
            附加上下文（给 CoVe 与工具）。
        strategy : RoutingStrategy
            路由策略。
        required_role : AgentRole | None
            specialist_first 时必填。
        token_used : int
            已使用 token 数。
        token_budget : int | None
            本次预算；None 使用默认值。
        task_id : str | None
            外部传入 task_id；None 时自动生成。
        """
        started = time.perf_counter()
        t_id = task_id or self._id_factory()
        route = self._router.route(domain, strategy=strategy, required_role=required_role)
        ctx = context or {}
        if self._input_sanitizer is not None:
            try:
                if claim:
                    self._input_sanitizer.validate_llm_context(claim)
                if ctx:
                    self._input_sanitizer.validate_llm_context(json.dumps(ctx, ensure_ascii=False, default=str))
            except ContextInjectionError as exc:
                budget = token_budget if token_budget is not None else self._default_budget
                latency_ms = int((time.perf_counter() - started) * 1000)
                result = OrchestrationResult(
                    task_id=t_id,
                    route=route,
                    tool_calls=[],
                    claim=claim,
                    hallucination=None,
                    success=False,
                    latency_ms=latency_ms,
                    token_used=token_used,
                    token_budget=budget,
                    errors=[f"context_sanitization_failed: {exc}"],
                )
                self._monitor.record(result)
                return result

        calls: list[ToolCallRecord] = []
        errors: list[str] = []
        chain_ok = True

        directives = [d.strip() for d in directive_chain.split("+") if d.strip()]
        for did in directives:
            steps = self._mapping.get(did, [])
            if not steps:
                calls.append(
                    ToolCallRecord(
                        directive=did,
                        tool_name="<unmapped>",
                        arguments={},
                        success=False,
                        latency_ms=0,
                        error=f"directive {did} 未在 directive_mapping 中注册",
                    )
                )
                errors.append(f"unmapped_directive: {did}")
                chain_ok = False
                continue
            for tool_name, args in steps:
                record = self._invoke_tool(did, tool_name, args)
                calls.append(record)
                if not record.success:
                    chain_ok = False
                    errors.append(f"tool_failed: {tool_name}")
                    break  # 当前 directive 失败则进入下一个 directive

        budget = token_budget if token_budget is not None else self._default_budget
        latency_ms = int((time.perf_counter() - started) * 1000)

        hallu_payload: dict[str, Any] | None = None
        if claim and self._cove is not None:
            hallu_payload = self._cove(claim, ctx)

        result = OrchestrationResult(
            task_id=t_id,
            route=route,
            tool_calls=calls,
            claim=claim,
            hallucination=hallu_payload,
            success=chain_ok and (hallu_payload is None or not hallu_payload.get("is_hallucination", False)),
            latency_ms=latency_ms,
            token_used=token_used,
            token_budget=budget,
            errors=errors,
        )
        self._monitor.record(result)
        return result

    # ---- internal -----------------------------------------------------

    def _invoke_tool(self, directive: str, tool_name: str, arguments: dict[str, Any]) -> ToolCallRecord:
        """调用一次 MCP 工具；invoker=None 或抛错都返回失败记录。"""
        started = time.perf_counter()
        if self._invoker is None:
            return ToolCallRecord(
                directive=directive,
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                latency_ms=0,
                error="no tool_invoker injected",
            )
        lsg_blocked = self._lsg_scan_agent_action(tool_name, arguments)
        if lsg_blocked:
            elapsed = int((time.perf_counter() - started) * 1000)
            return ToolCallRecord(
                directive=directive,
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                latency_ms=elapsed,
                error=f"LSG security blocked: {lsg_blocked}",
            )
        try:
            result = self._invoker(tool_name, arguments)
            elapsed = int((time.perf_counter() - started) * 1000)
            preview = str(result)[:400]
            return ToolCallRecord(
                directive=directive,
                tool_name=tool_name,
                arguments=arguments,
                success=True,
                latency_ms=elapsed,
                result_preview=preview,
            )
        except Exception as exc:  # — 工具错误必须被收敛
            elapsed = int((time.perf_counter() - started) * 1000)
            return ToolCallRecord(
                directive=directive,
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                latency_ms=elapsed,
                error=f"{type(exc).__name__}: {exc}",
            )

    _lsg_gateway_instance = None

    def _lsg_scan_agent_action(self, tool_name: str, tool_params: dict[str, Any]) -> str | None:
        if AgentOrchestrator._lsg_gateway_instance is None:
            try:
                from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

                AgentOrchestrator._lsg_gateway_instance = LSGSecurityGateway()
            except Exception as e:
                logger.warning("_lsg_scan_agent_action: failed to init LSG gateway (%s: %s)", type(e).__name__, e)
                return None
        gw = AgentOrchestrator._lsg_gateway_instance
        try:
            import asyncio

            from zephyr.shared.contracts.security import SecurityDecision

            text = json.dumps(tool_params, ensure_ascii=False) if tool_params else tool_name
            result = run_sync(
                gw.scan_agent_action(
                    text=text,
                    tool_name=tool_name,
                    tool_params=tool_params,
                    metadata={"source": "agent_orchestrator"},
                )
            )
            if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                return result.blocked_by or "lsg_agent_scan"
        except RuntimeError:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    return None
                result = loop.run_until_complete(
                    gw.scan_agent_action(
                        text=json.dumps(tool_params, ensure_ascii=False) if tool_params else tool_name,
                        tool_name=tool_name,
                        tool_params=tool_params,
                        metadata={"source": "agent_orchestrator"},
                    )
                )
                from zephyr.shared.contracts.security import SecurityDecision

                if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                    return result.blocked_by or "lsg_agent_scan"
            except Exception:
                pass
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# 仅用于静态检查：statistics 被保留以便未来扩展 p50/p95；防止 ruff unused
# ---------------------------------------------------------------------------
_ = statistics
_LITERAL_GUARD: Literal["orchestrator"] = "orchestrator"
