# [A_module] module_id=MOD-UNK_signal_synthesizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md

# [MODULE] zephyr.signal_fundamental.synth.signal_synthesizer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ---
# domain: signal
# category: signal_synthesis
# status: active
# created: "2026-05-05"
# ---

"""L03 — Signal Synthesizer

信号合成引擎。将 L02 产出的多因子信号 (FactorSignal) 聚合为统一的合成交易信号。

核心职责：
  - 多因子加权聚合 → SynthesizedSignal（CTR-P1-015）
  - 信号归一化与去噪
  - 市场状态(regime)识别附着
  - 信号降级检测 → SignalDegradationWarning（CTR-ERR-003）

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← L02
  生产者 — CTR-P1-015 (SynthesizedSignal) → L04, L05
  生产者 — CTR-ERR-003 (SignalDegradationWarning) → L04, L05

依赖方向：L02 → L03 → L04/L05
"""

from __future__ import annotations

import abc
import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional

from zephyr.trading.trading_contracts.market.factor_signal import FactorSignal
from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal


class SignalSynthesizerBase(abc.ABC):
    """信号合成器抽象基类（OCP 扩展点）

    实现者要求：
      - synthesize(): 接收多条 FactorSignal，产出单条 SynthesizedSignal
      - 加权策略必须可配置：equal_weight / sharpe_weight / ic_weight
      - 合成后 signal_value 必须归一化到 [-3.0, 3.0]
      - confidence < 0.5 时 MUST 设置 is_degraded=True 并发布 SignalDegradationWarning
      - 幂等键（INV-007）：每个合成操作必须关联 idempotency_key

    门禁约束（GATE-F）：
      - 不得在合成过程中引入 look-ahead bias
      - 因子权重不得动态调整为负值（禁止做空因子——那在 L05 做组合层面处理）
    """
    _registry: ClassVar[dict[str, type["SignalSynthesizerBase"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if abc.ABC not in cls.__bases__ and hasattr(cls, "__synthesizer_id__"):
            SignalSynthesizerBase._registry[cls.__synthesizer_id__] = cls

    @abc.abstractmethod
    def synthesize(
        self,
        factor_signals: List[FactorSignal],
        symbol: str,
        as_of_timestamp: datetime,
        weights: Optional[Dict[str, float]] = None,
    ) -> SynthesizedSignal:
        """将因子信号列表合成为统一交易信号"""
        ...

    @staticmethod
    def normalize_signal(raw: float) -> float:
        """归一化到 [-3.0, 3.0]"""
        return max(-3.0, min(3.0, raw))

    @staticmethod
    def direction_from_value(value: float, threshold: float = 0.2) -> str:
        """从信号值推断方向"""
        if value > threshold:
            return "LONG"
        elif value < -threshold:
            return "SHORT"
        return "NEUTRAL"

    @staticmethod
    def default_idempotency_key(symbol: str, as_of_timestamp: datetime) -> str:
        """合成操作的默认幂等键（INV-007）。"""
        ts = int(as_of_timestamp.timestamp() * 1000)
        return f"syn-{symbol}-{ts}-{uuid.uuid4().hex[:8]}"


__all__ = [
    "SignalSynthesizerBase",
]
