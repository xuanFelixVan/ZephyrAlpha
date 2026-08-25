# [BLUEPRINT] MOD-INT-API-LLM-POOL | docs/03_modules/_domain_intelligence/api_llm_pool/blueprint.md
# [MODULE] zephyr.intelligence.api_llm_pool
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（provider 注册表装配 / usage_sink 接 cost_tracker / degrade_to_local 接本地池切换）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定核心纯内存无IO; spec/config 非法 Fail-Closed; 未注册 provider 操作 Fail-Closed; 台账只增不改且同输入必同 cost_usd; 连续失败≥阈值不入选择集; 成本超限/全不健康产 degrade_to_local 信号（不执行切换）; 零密钥字段; usage_sink 异常不阻断
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/api_llm_pool/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidProviderSpecError; ProviderAlreadyRegisteredError; ProviderNotRegisteredError; InvalidUsageError
# [TESTS] tests/intelligence/test_api_llm_pool.py
# [A_module] module_id=MOD-INT-API-LLM-POOL | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ApiLlmPool — API LLM 池 (MOD-INT-API-LLM-POOL)

B11-02629（AUD-DRAFT-001-DIGEST P1 波 W-P1-11，§8.1）：provider 池注册
（模型/价格/限额/超时）+ token 计费台账（按 Agent/任务归集，经
``usage_sink`` 委托 cost_tracker 落账）+ 池健康度（成功率/延迟 EMA）驱动
调度 + 成本超限/全不健康产 **degrade_to_local 信号**（切换执行委托本地
LLM 池 B11-02628 与 llm_gateway 降级链，本模块不执行）。

查重裁定：不复制 llm_gateway（MOD-INF-009，真实调用面）与 model_router
（任务→模型静态路由）逻辑；密钥零字段（secrets 管理在 llm_gateway 层）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ApiLlmPool",
    "ApiLlmPoolConfig",
    "ApiProviderSpec",
    "InvalidProviderSpecError",
    "InvalidUsageError",
    "ProviderAlreadyRegisteredError",
    "ProviderHealth",
    "ProviderNotRegisteredError",
    "ProviderSelection",
    "UsageRecord",
]

_EMA_ALPHA: Final[float] = 0.3  # 延迟 EMA 平滑系数


class InvalidProviderSpecError(ZephyrBaseError):
    """provider spec / 池配置非法（Fail-Closed）。"""


class ProviderAlreadyRegisteredError(ZephyrBaseError):
    """同名 provider 重复注册。"""


class ProviderNotRegisteredError(ZephyrBaseError):
    """操作未注册 provider（Fail-Closed）。"""


class InvalidUsageError(ZephyrBaseError):
    """用量/调用结果输入非法（负 token / 负延迟，Fail-Closed）。"""


@dataclass(frozen=True)
class ApiProviderSpec:
    """provider 池注册条目（零密钥：密钥在 llm_gateway 层经 secrets 管理）。"""

    provider: str  # 池内唯一键（deepseek/glm/claude/openai...）
    model: str
    input_price_per_m: float  # USD / 1M input tokens
    output_price_per_m: float  # USD / 1M output tokens
    rate_limit_rpm: int  # 每分钟请求限额
    timeout_s: float

    def __post_init__(self) -> None:
        if not self.provider or not self.provider.strip():
            raise InvalidProviderSpecError("provider 不能为空")
        if not self.model or not self.model.strip():
            raise InvalidProviderSpecError("model 不能为空")
        if self.input_price_per_m < 0:
            raise InvalidProviderSpecError(f"input_price_per_m 不能为负: {self.input_price_per_m}")
        if self.output_price_per_m < 0:
            raise InvalidProviderSpecError(f"output_price_per_m 不能为负: {self.output_price_per_m}")
        if self.rate_limit_rpm <= 0:
            raise InvalidProviderSpecError(f"rate_limit_rpm 必须为正: {self.rate_limit_rpm}")
        if self.timeout_s <= 0:
            raise InvalidProviderSpecError(f"timeout_s 必须为正: {self.timeout_s}")


@dataclass(frozen=True)
class ApiLlmPoolConfig:
    """池配置（C 类可调参数）。"""

    unhealthy_threshold: int = 3  # 连续失败 ≥ 该值 → unhealthy
    cost_limit_usd: float | None = None  # 成本上限（None=不限）；累计 ≥ 即产 degrade_to_local

    def __post_init__(self) -> None:
        if self.unhealthy_threshold <= 0:
            raise InvalidProviderSpecError(f"unhealthy_threshold 必须为正: {self.unhealthy_threshold}")
        if self.cost_limit_usd is not None and self.cost_limit_usd < 0:
            raise InvalidProviderSpecError(f"cost_limit_usd 不能为负: {self.cost_limit_usd}")


@dataclass(frozen=True)
class ProviderHealth:
    """池健康度快照（不可变）。"""

    success_count: int
    failure_count: int
    ema_latency_ms: float
    consecutive_failures: int
    is_healthy: bool


@dataclass(frozen=True)
class UsageRecord:
    """token 计费台账记录（不可变，台账只增不改）。"""

    provider: str
    model: str
    agent_id: str
    task_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass(frozen=True)
class ProviderSelection:
    """健康度驱动调度结论（建议语义，执行委托调用方）。"""

    selected: str | None
    degrade_to_local: bool
    reasons: tuple[str, ...]


@dataclass
class _HealthState:
    """内部健康度累计态（可变，不导出）。"""

    success_count: int = 0
    failure_count: int = 0
    ema_latency_ms: float = 0.0
    consecutive_failures: int = 0


class ApiLlmPool:
    """API LLM 池：注册 + 计费台账 + 健康度调度（判定核心纯内存无 IO）。

    Args:
        config: 池配置（不健康阈值/成本上限）。
        usage_sink: 台账外发回调（dict）；异常不阻断台账内嵌。
    """

    def __init__(
        self,
        config: ApiLlmPoolConfig | None = None,
        usage_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._config = config or ApiLlmPoolConfig()
        self._usage_sink = usage_sink
        self._specs: dict[str, ApiProviderSpec] = {}
        self._health: dict[str, _HealthState] = {}
        self._ledger: list[UsageRecord] = []

    # ── 注册 ──────────────────────────────────────────────────────────────

    def register_provider(self, spec: ApiProviderSpec) -> None:
        """注册 provider；同名重复 → ProviderAlreadyRegisteredError。"""
        if spec.provider in self._specs:
            raise ProviderAlreadyRegisteredError(f"provider 已注册: {spec.provider}")
        self._specs[spec.provider] = spec
        self._health[spec.provider] = _HealthState()

    def providers(self) -> tuple[str, ...]:
        """已注册 provider 键集。"""
        return tuple(self._specs)

    def _require(self, provider: str) -> ApiProviderSpec:
        spec = self._specs.get(provider)
        if spec is None:
            raise ProviderNotRegisteredError(f"provider 未注册: {provider}")
        return spec

    # ── 计费台账 ──────────────────────────────────────────────────────────

    def record_usage(
        self,
        provider: str,
        agent_id: str,
        task_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> UsageRecord:
        """记一笔 token 用量：确定性成本 = in/1M×in价 + out/1M×out价。"""
        spec = self._require(provider)
        if input_tokens < 0 or output_tokens < 0:
            raise InvalidUsageError(f"token 数不能为负: input={input_tokens} output={output_tokens}")
        record = UsageRecord(
            provider=provider,
            model=spec.model,
            agent_id=agent_id,
            task_id=task_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=(input_tokens / 1_000_000) * spec.input_price_per_m
            + (output_tokens / 1_000_000) * spec.output_price_per_m,
        )
        self._ledger.append(record)
        if self._usage_sink is not None:
            try:
                self._usage_sink(asdict(record))
            except Exception:  # noqa: BLE001 — sink 异常不阻断（台账仍内嵌）
                _logger.exception("usage_sink 异常（已降级，台账不受影响）")
        return record

    def ledger(self) -> tuple[UsageRecord, ...]:
        """台账快照（只增不改）。"""
        return tuple(self._ledger)

    def total_cost(self, agent_id: str | None = None, task_id: str | None = None) -> float:
        """台账按 Agent/任务维度归集成本。"""
        return sum(
            r.cost_usd
            for r in self._ledger
            if (agent_id is None or r.agent_id == agent_id) and (task_id is None or r.task_id == task_id)
        )

    # ── 健康度 ────────────────────────────────────────────────────────────

    def record_call_result(self, provider: str, success: bool, latency_ms: float) -> None:
        """累计一次调用结果（成功/失败计数 + 延迟 EMA + 连续失败数）。"""
        self._require(provider)
        if latency_ms < 0:
            raise InvalidUsageError(f"latency_ms 不能为负: {latency_ms}")
        h = self._health[provider]
        if success:
            h.success_count += 1
            h.consecutive_failures = 0
        else:
            h.failure_count += 1
            h.consecutive_failures += 1
        h.ema_latency_ms = (
            latency_ms
            if h.success_count + h.failure_count == 1
            else _EMA_ALPHA * latency_ms + (1 - _EMA_ALPHA) * h.ema_latency_ms
        )

    def health(self, provider: str) -> ProviderHealth:
        """健康度快照。"""
        self._require(provider)
        h = self._health[provider]
        return ProviderHealth(
            success_count=h.success_count,
            failure_count=h.failure_count,
            ema_latency_ms=h.ema_latency_ms,
            consecutive_failures=h.consecutive_failures,
            is_healthy=h.consecutive_failures < self._config.unhealthy_threshold,
        )

    # ── 调度（建议语义） ─────────────────────────────────────────────────

    def select_provider(self, preferred_chain: list[str] | tuple[str, ...]) -> ProviderSelection:
        """健康度驱动调度：preferred_chain 序取首个 healthy；全不健康或成本超限 → degrade_to_local。"""
        reasons: list[str] = []
        degrade = False
        if self._config.cost_limit_usd is not None and self.total_cost() >= self._config.cost_limit_usd:
            degrade = True
            reasons.append(
                f"累计成本 {self.total_cost():.4f} USD ≥ 上限 {self._config.cost_limit_usd:.4f}（预算超限自动降级本地池建议）"
            )
        selected: str | None = None
        for name in preferred_chain:
            if name not in self._specs:
                reasons.append(f"provider 未注册，跳过: {name}")
                continue
            if self.health(name).is_healthy:
                selected = name
                break
            reasons.append(f"provider 不健康（连续失败 ≥{self._config.unhealthy_threshold}），跳过: {name}")
        if selected is None:
            degrade = True
            reasons.append("选择集无健康 provider（降级本地池建议）")
        if not reasons:
            reasons.append(f"选中健康 provider: {selected}")
        return ProviderSelection(selected=selected, degrade_to_local=degrade, reasons=tuple(reasons))
