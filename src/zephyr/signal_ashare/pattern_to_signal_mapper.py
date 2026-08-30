# [BLUEPRINT] MOD-SIG-115 | docs/03_modules/_domain_signal/pattern_to_signal_mapper/blueprint.md
# [MODULE] zephyr.signal_ashare.pattern_to_signal_mapper
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.unified_pattern_engine（MOD-SIG-091 PatternEvent 契约，testing）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 消费 PatternEvent 契约（类型+置信度+关键点位+方向+历史胜率）；方向词表闭合（long/short/neutral）；强度=置信度×胜率加权∈[0,1]；止损=关键点位外扩 k%（k>0）；CTR-002 输出恒过注入校验器（未注入/拒绝即 Fail-Closed 不出伪信号）；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/pattern_to_signal_mapper/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PatternSignalMapError(占位 ZA-SIG-UNREGISTERED-PATTERN-SIGNAL-MAP)——空 symbol/置信度或胜率越界/stop_buffer非正/无关键点位可止损/校验器未注入或拒绝时抛
# [TESTS] tests/signal_ashare/test_pattern_to_signal_mapper.py
# [A_module] module_id=MOD-SIG-115 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
PatternToSignalMapper — 97形态→信号转化层（MOD-SIG-115，B1-00849，C2 97）。

消费 unified_pattern_engine 的 PatternEvent（类型+置信度+关键点位+方向+
历史胜率）→ 方向/强度/止损位映射（形态→方向映射表 + 强度=置信度×胜率
加权 + 止损=关键点位外扩 k%）+ CTR-002 兼容 FactorSignal 输出
（注入产出校验器，未注入/拒绝即 Fail-Closed 不出伪信号）。

纯内存/DI设计；外部副作用全部经注入回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: stop_buffer_pct 参数
#   fields: 参数 stop_buffer_pct（无注解）
#   code: pattern_to_signal_mapper.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: default_win_rate 参数
#   fields: 参数 default_win_rate（无注解）
#   code: pattern_to_signal_mapper.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: validator 参数
#   fields: 参数 validator（无注解）
#   code: pattern_to_signal_mapper.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: pattern_to_signal_mapper.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PatternToSignalMapper
#   name_en: PatternToSignalMapper
#   intro: 形态信号转化层（PatternEvent→方向/强度/止损→CTR-002 输出）。
#   desc: 形态信号转化层（PatternEvent→方向/强度/止损→CTR-002 输出）。；公共方法（定义序）: map_event, map_batch, emit_signal；源码 L132-L254
#   inputs: stop_buffer_pct default_win_rate validator clock
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: PatternToSignalMapper
#   downstream: 运行时装配批（统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

from zephyr.signal_ashare.unified_pattern_engine import (
    PatternDirection,
    PatternEvent,
)

_log = logging.getLogger(__name__)

__all__: Final = [
    "MappedSignal",
    "PatternSignalMapError",
    "PatternToSignalMapper",
    "SignalDirection",
]


class PatternSignalMapError(Exception):
    """形态信号转化协议输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-PATTERN-SIGNAL-MAP。
    """


class SignalDirection(str, Enum):
    """信号方向词表（闭合）。"""

    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class MappedSignal:
    """映射后信号（方向+强度+止损）。"""

    pattern_id: str
    pattern_name: str
    direction: SignalDirection
    strength: float  # 置信度×胜率加权，∈[0,1]
    stop_loss: float | None  # 关键点位外扩 k%；NEUTRAL 为 None
    advisory: bool = True
    notes: tuple[str, ...] = ()


#: 形态→方向映射表（PatternDirection → SignalDirection）
_DIRECTION_MAP: Final[dict[PatternDirection, SignalDirection]] = {
    PatternDirection.UP: SignalDirection.LONG,
    PatternDirection.DOWN: SignalDirection.SHORT,
    PatternDirection.NEUTRAL: SignalDirection.NEUTRAL,
}

#: CTR-002 产出校验器签名：signal -> True 放行 / False 拒绝
SignalValidator = Callable[[Mapping[str, object]], bool]


class PatternToSignalMapper:
    """形态信号转化层（PatternEvent→方向/强度/止损→CTR-002 输出）。"""

    def __init__(
        self,
        *,
        stop_buffer_pct: float = 1.0,
        default_win_rate: float = 0.5,
        validator: SignalValidator | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not 0.0 < stop_buffer_pct < 100.0:
            raise PatternSignalMapError(f"stop_buffer_pct 越界: {stop_buffer_pct!r}（须∈(0,100)）")
        if not 0.0 <= default_win_rate <= 1.0:
            raise PatternSignalMapError(f"default_win_rate 越界: {default_win_rate!r}")
        self._stop_buffer_pct = float(stop_buffer_pct)
        self._default_win_rate = float(default_win_rate)
        self._validator = validator
        self._clock = clock or datetime.datetime.now

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _now(self) -> datetime.datetime:
        return self._clock()

    # ── 映射 ──────────────────────────────────────────────────────────────

    def map_event(self, event: PatternEvent) -> MappedSignal:
        """PatternEvent → MappedSignal（方向/强度/止损）。"""
        if not isinstance(event, PatternEvent):
            raise PatternSignalMapError("event 非 PatternEvent 实例")
        if not 0.0 <= event.confidence <= 1.0:
            raise PatternSignalMapError(f"置信度越界: {event.confidence!r}")
        win_rate = event.historical_win_rate
        if win_rate is not None and not 0.0 <= win_rate <= 1.0:
            raise PatternSignalMapError(f"历史胜率越界: {win_rate!r}")
        effective_win_rate = win_rate if win_rate is not None else self._default_win_rate
        strength = round(event.confidence * effective_win_rate, 6)

        direction = _DIRECTION_MAP.get(event.direction)
        if direction is None:
            raise PatternSignalMapError(f"未知方向映射: {event.direction!r}")

        stop_loss: float | None = None
        if direction is SignalDirection.NEUTRAL:
            notes = ("中性形态，无止损位",)
        else:
            if not event.key_points:
                raise PatternSignalMapError(f"形态 {event.pattern_id!r} 无关键点位，无法计算止损")
            prices = [kp.price for kp in event.key_points]
            if direction is SignalDirection.LONG:
                anchor = min(prices)
                stop_loss = round(anchor * (1.0 - self._stop_buffer_pct / 100.0), 6)
            else:  # SHORT
                anchor = max(prices)
                stop_loss = round(anchor * (1.0 + self._stop_buffer_pct / 100.0), 6)
            notes = ()

        return MappedSignal(
            pattern_id=event.pattern_id,
            pattern_name=event.name,
            direction=direction,
            strength=strength,
            stop_loss=stop_loss,
            advisory=True,
            notes=notes,
        )

    def map_batch(self, events: tuple[PatternEvent, ...] | list[PatternEvent]) -> tuple[MappedSignal, ...]:
        """批量映射（按 pattern_id 确定性排序）。"""
        mapped = [self.map_event(e) for e in events]
        mapped.sort(key=lambda m: (m.pattern_id, m.pattern_name))
        return tuple(mapped)

    # ── CTR-002 兼容输出（注入校验器） ─────────────────────────────────────

    def emit_signal(
        self,
        symbol: str,
        signals: tuple[MappedSignal, ...] | list[MappedSignal],
        *,
        as_of: datetime.datetime,
    ) -> dict[str, object]:
        """唯一信号出口：CTR-002 FactorSignal 兼容载荷，过注入校验器方可出网。"""
        if not symbol or not str(symbol).strip():
            raise PatternSignalMapError("标的代码空白")
        if self._validator is None:
            raise PatternSignalMapError("validator 未注入（CTR-002 出口强制校验，禁止旁路）")
        if not signals:
            raise PatternSignalMapError("signals 为空（无映射结果不可发信号）")
        if as_of > self._now():
            raise PatternSignalMapError(f"as_of 晚于当前时钟（未来信号）: {as_of!r}")

        values: dict[str, float] = {}
        for sig in signals:
            signed = (
                sig.strength
                if sig.direction is SignalDirection.LONG
                else (-sig.strength if sig.direction is SignalDirection.SHORT else 0.0)
            )
            values[sig.pattern_id] = round(signed, 6)

        payload: dict[str, object] = {
            "contract": "CTR-002",
            "factor_id": "pattern_signal",
            "source_domain": "ashare_signal",
            "symbol": symbol,
            "values": values,
            "as_of": as_of.isoformat(),
            "advisory": True,
            "metadata": {
                "directions": {s.pattern_id: s.direction.value for s in signals},
                "stop_losses": {s.pattern_id: s.stop_loss for s in signals},
            },
        }
        try:
            ok = bool(self._validator(payload))
        except Exception as exc:  # noqa: BLE001 — 校验器违约 Fail-Closed
            raise PatternSignalMapError(f"validator 执行异常: {exc}") from exc
        if not ok:
            raise PatternSignalMapError(f"CTR-002 校验拒绝: symbol {symbol!r}（Fail-Closed 不出伪信号）")
        _log.info("形态信号出网: %s（%d 形态）", symbol, len(signals))
        return payload
