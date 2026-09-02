# [BLUEPRINT] MOD-INT-LOCAL-LLM-POOL | docs/03_modules/_domain_intelligence/local_llm_pool/blueprint.md | §0-5
# [MODULE] zephyr.intelligence.local_llm_pool
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors(ZephyrBaseError)
# [CONSUMERS] 运行时装配批（executor 接 ollama_chat/vLLM / gpu_stats_provider 接 gpu_monitor / profile_sink 接模型画像 / degrade_to_api 接 api_llm_pool 切换）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定核心纯内存无IO; 显存预算门Fail-Closed超预算拒载产degrade_to_api信号; 健康度连续失败≥阈值→unhealthy; 已载台账只增不改; 同输入必同判定; 零密钥字段
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/local_llm_pool/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidLocalModelSpecError(ZA-IT-0013); LocalModelAlreadyRegisteredError(ZA-IT-0014); LocalModelNotRegisteredError(ZA-IT-0015)
# [TESTS] tests/intelligence/test_local_llm_pool.py
# [A_module] module_id=MOD-INT-LOCAL-LLM-POOL | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""LocalLlmPool — 本地 LLM 池治理（MOD-INT-LOCAL-LLM-POOL）。

B11-02628（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§8.1）：主力 Qwen2.5-7B +
备选 DeepSeek-7B 注册表；AWQ 4bit 模型加载/卸载管理；显存预算门
（盘中 6GB 含 KV cache，超限拒载并产降级 API 池信号）；与 gpu_monitor
联动；延迟/成功率入模型画像。

查重裁定：与 api_llm_pool 对称不重复（API 池 vs 本地池）；不复制
ollama_chat（单模型客户端）、local_model_scheduler（调度循环）、
gpu_monitor（nvidia-smi 采集）、profiler（benchmark 画像）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_log = logging.getLogger(__name__)

__all__: Final = [
    "InvalidLocalModelSpecError",
    "LoadDecision",
    "LocalLlmPool",
    "LocalLlmPoolConfig",
    "LocalModelAlreadyRegisteredError",
    "LocalModelHealth",
    "LocalModelNotRegisteredError",
    "LocalModelSelection",
    "LocalModelSpec",
    "PoolBudgets",
]


class InvalidLocalModelSpecError(ZephyrBaseError):
    """本地模型规格非法（Fail-Closed）。"""

    error_code = "ZA-IT-0013"


class LocalModelAlreadyRegisteredError(ZephyrBaseError):
    """同名本地模型重复注册。"""

    error_code = "ZA-IT-0014"


class LocalModelNotRegisteredError(ZephyrBaseError):
    """操作未注册本地模型（Fail-Closed）。"""

    error_code = "ZA-IT-0015"


@dataclass(frozen=True)
class LocalModelSpec:
    """本地模型规格。"""

    name: str
    quant: str
    vram_gb: float
    role: str  # "primary" | "backup"

    def __post_init__(self) -> None:
        if not self.name:
            raise InvalidLocalModelSpecError("name 不能为空")
        if self.vram_gb < 0:
            raise InvalidLocalModelSpecError(f"vram_gb 不能为负: {self.vram_gb}")
        if self.role not in ("primary", "backup"):
            raise InvalidLocalModelSpecError(f"未知角色: {self.role}")


@dataclass(frozen=True)
class PoolBudgets:
    """显存预算（盘中/盘后）。"""

    intraday_gb: float = 6.0
    postmarket_gb: float = 8.0


@dataclass(frozen=True)
class LocalModelHealth:
    """本地模型健康度。"""

    success_count: int
    failure_count: int
    ema_latency_ms: float
    consecutive_failures: int
    is_healthy: bool


@dataclass(frozen=True)
class LoadDecision:
    """加载决策。"""

    model: str
    loaded: bool
    degrade_to_api: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class LocalModelSelection:
    """模型选择结果。"""

    selected: str | None
    degrade_to_api: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class LocalLlmPoolConfig:
    """本地池配置。"""

    unhealthy_threshold: int = 3
    budgets: PoolBudgets = PoolBudgets()

    def __post_init__(self) -> None:
        if self.unhealthy_threshold <= 0:
            raise InvalidLocalModelSpecError(f"unhealthy_threshold 必须为正: {self.unhealthy_threshold}")


class LocalLlmPool:
    """本地 LLM 池判定核心（纯内存，无 IO）。"""

    def __init__(
        self,
        config: LocalLlmPoolConfig | None = None,
        executor: Callable[[str, str], Any] | None = None,
        gpu_stats_provider: Callable[[], dict[str, Any]] | None = None,
        profile_sink: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._config = config or LocalLlmPoolConfig()
        self._executor = executor
        self._gpu_stats_provider = gpu_stats_provider
        self._profile_sink = profile_sink
        self._registry: dict[str, LocalModelSpec] = {}
        self._loaded: set[str] = set()
        self._health: dict[str, dict[str, Any]] = {}
        self._ema_alpha: float = 0.3

    def register_model(self, spec: LocalModelSpec) -> None:
        if spec.name in self._registry:
            raise LocalModelAlreadyRegisteredError(f"模型已注册: {spec.name}")
        self._registry[spec.name] = spec
        self._health[spec.name] = {
            "success_count": 0,
            "failure_count": 0,
            "ema_latency_ms": 0.0,
            "consecutive_failures": 0,
        }

    def request_load(self, model: str, period: str = "intraday") -> LoadDecision:
        if model not in self._registry:
            raise LocalModelNotRegisteredError(f"模型未注册: {model}")
        spec = self._registry[model]
        budget = self._config.budgets.intraday_gb if period == "intraday" else self._config.budgets.postmarket_gb
        used = self._current_vram_gb()
        if used + spec.vram_gb > budget:
            return LoadDecision(
                model=model,
                loaded=False,
                degrade_to_api=True,
                reasons=(f"显存超限 used={used:.2f}GB + {spec.vram_gb}GB > budget={budget}GB",),
            )
        if self._executor is not None:
            try:
                self._executor(model, "load")
            except Exception as exc:
                _log.warning("executor load 异常: %s", exc)
        self._loaded.add(model)
        return LoadDecision(
            model=model,
            loaded=True,
            degrade_to_api=False,
            reasons=(f"显存充足 used={used:.2f}GB",),
        )

    def request_unload(self, model: str) -> LoadDecision:
        if model not in self._registry:
            raise LocalModelNotRegisteredError(f"模型未注册: {model}")
        if model not in self._loaded:
            raise LocalModelNotRegisteredError(f"模型未加载: {model}")
        if self._executor is not None:
            try:
                self._executor(model, "unload")
            except Exception as exc:
                _log.warning("executor unload 异常: %s", exc)
        self._loaded.discard(model)
        return LoadDecision(
            model=model,
            loaded=False,
            degrade_to_api=False,
            reasons=("已卸载",),
        )

    def record_call_result(self, model: str, success: bool, latency_ms: float) -> None:
        if model not in self._health:
            return
        h = self._health[model]
        if success:
            h["success_count"] += 1
            h["consecutive_failures"] = 0
        else:
            h["failure_count"] += 1
            h["consecutive_failures"] += 1
        h["ema_latency_ms"] = self._ema_alpha * latency_ms + (1 - self._ema_alpha) * h["ema_latency_ms"]
        if self._profile_sink is not None:
            try:
                self._profile_sink(
                    model,
                    {
                        "success": success,
                        "latency_ms": latency_ms,
                        "ema_latency_ms": h["ema_latency_ms"],
                        "consecutive_failures": h["consecutive_failures"],
                    },
                )
            except Exception as exc:
                _log.warning("profile_sink 异常: %s", exc)

    def select_model(self, preferred_role: str | None = None) -> LocalModelSelection:
        candidates = [
            name
            for name in self._loaded
            if self._is_healthy(name) and (preferred_role is None or self._registry[name].role == preferred_role)
        ]
        if not candidates:
            # 尝试 fallback：忽略角色，只看已载 healthy
            candidates = [name for name in self._loaded if self._is_healthy(name)]
        if candidates:
            return LocalModelSelection(
                selected=candidates[0],
                degrade_to_api=False,
                reasons=("已载且 healthy",),
            )
        reasons: list[str] = ["无可用本地模型"]
        if not self._loaded:
            reasons.append("当前无模型已加载")
        return LocalModelSelection(
            selected=None,
            degrade_to_api=True,
            reasons=tuple(reasons),
        )

    def health(self, model: str) -> LocalModelHealth:
        h = self._health.get(model, {})
        cf = h.get("consecutive_failures", 0)
        return LocalModelHealth(
            success_count=h.get("success_count", 0),
            failure_count=h.get("failure_count", 0),
            ema_latency_ms=h.get("ema_latency_ms", 0.0),
            consecutive_failures=cf,
            is_healthy=cf < self._config.unhealthy_threshold,
        )

    def loaded_models(self) -> list[str]:
        return sorted(self._loaded)

    def _is_healthy(self, model: str) -> bool:
        return self.health(model).is_healthy

    def _current_vram_gb(self) -> float:
        if self._gpu_stats_provider is not None:
            try:
                stats = self._gpu_stats_provider()
                return float(stats.get("memory_used_gb", 0.0))
            except Exception as exc:
                _log.warning("gpu_stats_provider 异常: %s", exc)
        return sum(self._registry[m].vram_gb for m in self._loaded)
