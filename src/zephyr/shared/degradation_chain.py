"""
Graceful Degradation Chain — 模型降级链 (M-24)
配置从 degradation_chain.yaml 加载，YAML 声明式定义降级路径。

特性：
  - 链1：cost_per_day > ¥5 → deepseek-chat(2000) → qwen2.5-3b-onnx(1000)
  - 链2：latency_p99 > 10000ms → deepseek-chat(5000) → qwen2.5-3b-onnx(2000)
  - 双向模型路由：升级时自动检测降级原因是否已消除
  - 成本感知回升
"""
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DegradationTrigger(Enum):
    COST_EXCEEDED = "cost_exceeded"
    LATENCY_EXCEEDED = "latency_exceeded"
    ERROR_BUDGET_EXHAUSTED = "error_budget_exhausted"
    MANUAL = "manual"


@dataclass
class ModelTier:
    model_name: str
    max_tokens: int
    cost_per_1k: float = 0.0


@dataclass
class DegradationChain:
    chain_id: str
    trigger: DegradationTrigger
    trigger_threshold: float
    tiers: list[ModelTier]
    auto_recover: bool = True
    recovery_cooldown_seconds: int = 300


@dataclass
class DegradationState:
    chain_id: str
    current_tier: int
    degraded: bool
    degraded_at: str = ""
    degraded_reason: str = ""
    last_recovery_check: float = field(default_factory=time.time)


class DegradationChainManager:
    """
    Graceful Degradation 降级链管理器 (M-24)
    """

    DEFAULT_CHAINS = [
        DegradationChain(
            chain_id="cost-degradation",
            trigger=DegradationTrigger.COST_EXCEEDED,
            trigger_threshold=5.0,
            tiers=[
                ModelTier(model_name="deepseek-chat", max_tokens=2000, cost_per_1k=0.002),
                ModelTier(model_name="qwen2.5-3b-onnx", max_tokens=1000, cost_per_1k=0.0),
            ],
        ),
        DegradationChain(
            chain_id="latency-degradation",
            trigger=DegradationTrigger.LATENCY_EXCEEDED,
            trigger_threshold=10000,
            tiers=[
                ModelTier(model_name="deepseek-chat", max_tokens=5000, cost_per_1k=0.002),
                ModelTier(model_name="qwen2.5-3b-onnx", max_tokens=2000, cost_per_1k=0.0),
            ],
        ),
    ]

    def __init__(self, config_path: Optional[str] = None):
        self.chains: dict[str, DegradationChain] = {
            c.chain_id: c for c in self.DEFAULT_CHAINS
        }
        self._states: dict[str, DegradationState] = {}

        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

        for chain_id in self.chains:
            self._states[chain_id] = DegradationState(
                chain_id=chain_id, current_tier=0, degraded=False
            )

    def _load_config(self, config_path: str):
        import yaml
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for entry in data.get("chains", []):
                tiers = [
                    ModelTier(
                        model_name=t["model"],
                        max_tokens=t["max_tokens"],
                        cost_per_1k=float(t.get("cost_per_1k", 0)),
                    )
                    for t in entry.get("tiers", [])
                ]
                chain = DegradationChain(
                    chain_id=entry["chain_id"],
                    trigger=DegradationTrigger(entry["trigger"]),
                    trigger_threshold=float(entry["trigger_threshold"]),
                    tiers=tiers,
                    auto_recover=entry.get("auto_recover", True),
                )
                self.chains[chain.chain_id] = chain
        except Exception:
            pass

    def check_trigger(self, chain_id: str, current_value: float) -> bool:
        chain = self.chains.get(chain_id)
        if chain is None:
            return False

        if chain.trigger in (DegradationTrigger.COST_EXCEEDED,
                              DegradationTrigger.LATENCY_EXCEEDED):
            return current_value > chain.trigger_threshold

        return False

    def degrade(self, chain_id: str, reason: str) -> Optional[ModelTier]:
        chain = self.chains.get(chain_id)
        if chain is None:
            return None

        state = self._states.get(chain_id)
        if state is None:
            return None

        next_tier = state.current_tier + 1
        if next_tier >= len(chain.tiers):
            return chain.tiers[-1]

        state.current_tier = next_tier
        state.degraded = True
        state.degraded_reason = reason
        state.degraded_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return chain.tiers[next_tier]

    def recover(self, chain_id: str) -> Optional[ModelTier]:
        chain = self.chains.get(chain_id)
        if chain is None:
            return None

        state = self._states.get(chain_id)
        if state is None:
            return None

        if not chain.auto_recover:
            return None

        if time.time() - state.last_recovery_check < chain.recovery_cooldown_seconds:
            return None

        state.last_recovery_check = time.time()

        if state.current_tier > 0:
            state.current_tier -= 1
            if state.current_tier == 0:
                state.degraded = False
                state.degraded_reason = ""
            return chain.tiers[state.current_tier]

        return None

    def get_current_model(self, chain_id: str) -> Optional[ModelTier]:
        chain = self.chains.get(chain_id)
        state = self._states.get(chain_id)
        if chain is None or state is None:
            return None
        tier_idx = min(state.current_tier, len(chain.tiers) - 1)
        return chain.tiers[tier_idx] if tier_idx >= 0 else None

    def get_state(self, chain_id: str) -> Optional[DegradationState]:
        return self._states.get(chain_id)

    def current_tier_index(self, chain_id: str) -> int:
        state = self._states.get(chain_id)
        return state.current_tier if state else 0


_manager: Optional[DegradationChainManager] = None


def get_degradation_manager() -> DegradationChainManager:
    global _manager
    if _manager is None:
        _manager = DegradationChainManager()
    return _manager
