# [BLUEPRINT] MOD-SIG-147 | docs/03_modules/_domain_signal/pattern_signal_runtime/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_signal_runtime
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.unified_pattern_engine（MOD-SIG-091，production）；zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider（MOD-SIG-145，production）；zephyr.signal_ashare.strategy_signal.pattern_to_signal_mapper（MOD-SIG-115，production）；zephyr.signal_ashare.strategy_signal.signal_factory（SignalDraft，production）；zephyr.shared.contracts.ctr002_producer_validator（MOD-CON-002，production）
# [CONSUMERS] 信号管线运行时装配批（signal_factory 档注册投票源；W-C3 接 MOD-SIG-131）；消费班方案 v1.0 §C1/C2
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯装配根零业务算法（组合 145→091 注入+115 映射+MOD-CON-002 校验+signal_factory 注册五生产件）；validator 恒非 None 且适配器异常一律 False（CTR-002 Fail-Closed 拒绝出网）；regime_filter 拒准→空载荷；审计快照（win_rate_snapshot/regime_tag/weight_version）随 payload metadata 出网；provider 与 win_rate_query 互斥（装配歧义禁止）；idempotency_key=blake2b(symbol+as_of+values) 确定性且工厂注册键=键:方向（重复幂等跳过留痕）；零新增错误码（委托 ZA-SIG-0147 与 provider 既有契约）；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/pattern_signal_runtime/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无新增错误码——映射错=PatternSignalMapError(ZA-SIG-0147)，库错=provider RuntimeError，装配歧义=ValueError，工厂重复注册=幂等跳过留痕（notes），全权委托既有契约（净零）
# [TESTS] tests/signal_ashare/strategy_signal/test_pattern_signal_runtime.py
# [A_module] module_id=MOD-SIG-147 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
PatternSignalRuntime — 图形库消费端装配根（MOD-SIG-147）。

组合根：把五个生产件拼成一台能开机的机器（消费班方案 v1.0 §C1/C2，
docs/_working/2026-09-14-pattern-consumer-plan.md）：

    PatternWinRateProvider(145) ──win_rate_fn──▶ UnifiedPatternEngine(091 注入契约)
    PatternEvent ──regime_filter 门──▶ PatternToSignalMapper(115) ──payload──▶ CTR-002 校验
                                                          │ Fail-Closed
                                                          ▼
                                    CTR-002 载荷 + 审计快照 ──▶ SignalFactory 逐方向注册

本模块零业务算法：只做接线组装+默认装配参数+门序编排；任何一层的行为
问题去各自模块的 blueprint（091/115/145/MOD-CON-002/signal_factory）。
断点背景：2026-09-14 反查实证全仓仅回填脚本构造引擎、mapper/adjuster
零装配调用——本模块即"通电工程"。

# [ALGO_FLOW]
# 层: 装配
# - id: A1
#   name: 胜率注入
#   code: win_rate_fn = win_rate_query 显式注入 或 provider.get(pattern_id, timeframe, fwd_window, regime_tag)
# - id: A2
#   name: CTR-002 适配器
#   code: mapper payload dict → FactorSignal（raw_value=最强分量符号值）→ MOD-CON-002 validate().ok；symbol/values/as_of 显式增查；任何异常一律 False（Fail-Closed）
# 层: 门序（W-C2）
# - id: G1
#   name: regime 门
#   code: regime_filter(symbol, regime_tag) 为 False → 返回空载荷（准入路由，不造检测器，复用胜率表 regime_tag 切片口径）
# - id: G2
#   name: 审计快照
#   code: metadata 增 win_rate_snapshot（逐事件 win_rate）+regime_tag+weight_version 四元组（信号可溯源到"当时为什么发"）
# - id: G3
#   name: 总线注册
#   code: 逐方向取最强分量 MappedSignal → SignalDraft(signal_id=幂等键:方向) → factory.register；NEUTRAL 跳过；重复 ValueError 幂等跳过留痕 notes
"""

from __future__ import annotations

import datetime
import hashlib
from collections.abc import Callable, Mapping
from typing import Any

from zephyr.shared.contracts.ctr002_producer_validator import Ctr002ProducerValidator
from zephyr.signal_ashare.strategy_signal.pattern_to_signal_mapper import (
    PatternSignalMapError,
    PatternToSignalMapper,
    SignalDirection,
)
from zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider import (
    PatternWinRateProvider,
)
from zephyr.signal_ashare.strategy_signal.signal_factory import SignalDraft
from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import (
    UnifiedPatternEngine,
)

__all__ = ["Ctr002PayloadValidator", "PatternSignalRuntime"]

_DEFAULT_TIMEFRAME = "day"
_DEFAULT_FWD_WINDOW = 10
_DEFAULT_SOURCE = "pattern_signal_runtime"


def _payload_idempotency_key(payload: Mapping[str, Any]) -> str:
    """确定性幂等键（对齐事件表 blake2b 惯例）。"""
    h = hashlib.blake2b(digest_size=16)
    h.update(str(payload.get("symbol", "")).encode("utf-8"))
    h.update(str(payload.get("as_of", "")).encode("utf-8"))
    values = payload.get("values")
    h.update(repr(sorted((values or {}).items())).encode("utf-8"))
    return h.hexdigest()


def _payload_to_factor_signal(
    payload: Mapping[str, Any], *, as_of_date: datetime.datetime
) -> Any:
    """mapper 载荷 → FactorSignal（MOD-CON-002 校验输入形）。

    raw_value 取最强分量符号值（多形态聚合载荷的代表值；全量
    values 进 extra，语义不丢失）。
    """
    from zephyr.shared.contracts.factor_signal import FactorSignal

    values = dict(payload.get("values") or {})
    raw = max(values.values(), key=abs) if values else 0.0
    return FactorSignal(
        as_of_date=as_of_date,
        factor_id=str(payload.get("factor_id") or "pattern_signal"),
        idempotency_key=_payload_idempotency_key(payload),
        raw_value=float(raw),
        symbol=str(payload.get("symbol") or ""),
        confidence=1.0,
        extra={"values": values, "advisory": bool(payload.get("advisory", True))},
    )


class Ctr002PayloadValidator:
    """mapper 校验器契约（payload Mapping→bool）到 MOD-CON-002 的适配器。

    显式增查三件（schema 之外的装配级防线）：symbol 非空、values 非空、
    as_of 不晚于时钟（PIT）。任何异常一律 False——适配器崩溃等于拒绝
    出网，绝不 Fail-Open。
    """

    def __init__(self, *, clock: Callable[[], datetime.datetime] | None = None) -> None:
        self._clock = clock or datetime.datetime.now
        self._inner = Ctr002ProducerValidator(clock=self._clock)

    def __call__(self, payload: Mapping[str, Any]) -> bool:
        try:
            if not isinstance(payload, Mapping):
                return False
            if not str(payload.get("symbol") or "").strip():
                return False
            values = payload.get("values")
            if not isinstance(values, Mapping) or not values:
                return False
            as_of = datetime.datetime.fromisoformat(str(payload["as_of"]))
            if as_of > self._clock():
                return False
            fs = _payload_to_factor_signal(payload, as_of_date=as_of)
            return bool(self._inner.validate(fs).ok)
        except Exception:
            return False


class PatternSignalRuntime:
    """图形库消费端装配根（四生产件的组合点，见 blueprint §0.1）。"""

    def __init__(
        self,
        *,
        provider: PatternWinRateProvider | None = None,
        win_rate_query: Callable[[str], float | None] | None = None,
        validator: Callable[[Mapping[str, Any]], bool] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        stop_buffer_pct: float = 1.0,
        default_win_rate: float = 0.5,
        timeframe: str = _DEFAULT_TIMEFRAME,
        fwd_window: int = _DEFAULT_FWD_WINDOW,
        regime_tag: str = "",
        regime_filter: Callable[[str, str], bool] | None = None,
        weight_version: str = "",
        factory: Any = None,
        source: str = _DEFAULT_SOURCE,
    ) -> None:
        if win_rate_query is not None and provider is not None:
            raise ValueError("provider 与 win_rate_query 二选一（装配歧义禁止）")
        self._clock = clock or datetime.datetime.now
        self._provider = provider if provider is not None else PatternWinRateProvider()
        self._timeframe = timeframe
        self._fwd_window = int(fwd_window)
        self._regime_tag = regime_tag
        self._regime_filter = regime_filter
        self._weight_version = weight_version
        self._factory = factory
        self._source = source
        if win_rate_query is not None:
            self._win_rate_fn: Callable[[str], float | None] = win_rate_query
        else:
            def _query(pattern_id: str) -> float | None:
                return self._provider.get(
                    pattern_id,
                    timeframe=self._timeframe,
                    fwd_window=self._fwd_window,
                    regime_tag=self._regime_tag,
                )

            self._win_rate_fn = _query
        self._validator = (
            validator if validator is not None else Ctr002PayloadValidator(clock=self._clock)
        )
        self._mapper = PatternToSignalMapper(
            stop_buffer_pct=stop_buffer_pct,
            default_win_rate=default_win_rate,
            validator=self._validator,
            clock=self._clock,
        )

    # ── 装配出口 ──────────────────────────────────────────────────────────

    @property
    def win_rate_fn(self) -> Callable[[str], float | None]:
        """引擎注入契约（MOD-SIG-091 win_rate_provider 参数用）。"""
        return self._win_rate_fn

    @property
    def mapper(self) -> PatternToSignalMapper:
        return self._mapper

    def build_engine(self, config: Any = None, **kwargs: Any) -> UnifiedPatternEngine:
        """引擎工厂：胜率注入已接好（091 契约），宿主直接用。"""
        return UnifiedPatternEngine(config, win_rate_provider=self._win_rate_fn, **kwargs)

    def on_events(
        self,
        symbol: str,
        events: Any,
        *,
        as_of: datetime.datetime | None = None,
    ) -> dict[str, Any]:
        """图形事件流 → CTR-002 信号载荷（唯一出口经校验器）。

        W-C2 meta 门序：①regime_filter 拒准→空载荷（不发信号）；
        ②映射出口；③审计快照（win_rate/regime_tag/weight_version）入
        metadata；④factory 在册时逐方向注册 SignalDraft（最强分量）。
        空事件序列=空 dict（无形态不发信号，不出空载荷）。
        映射/出口错误透传 MOD-SIG-115 既有契约（PatternSignalMapError）。
        """
        if as_of is None:
            as_of = self._clock()
        if self._regime_filter is not None and not self._regime_filter(symbol, self._regime_tag):
            return {}
        event_list = list(events)
        mapped = self._mapper.map_batch(event_list)
        if not mapped:
            return {}
        payload = self._mapper.emit_signal(symbol, mapped, as_of=as_of)
        metadata = payload.setdefault("metadata", {})
        metadata["regime_tag"] = self._regime_tag
        metadata["weight_version"] = self._weight_version
        metadata["win_rate_snapshot"] = {
            e.pattern_id: {"win_rate": e.historical_win_rate} for e in event_list
        }
        if self._factory is not None:
            metadata["signal_ids"] = self._register_to_factory(payload, mapped)
        return payload

    def _register_to_factory(
        self, payload: Mapping[str, Any], mapped: Any
    ) -> list[str]:
        """逐方向注册最强分量信号（NEUTRAL 跳过；重复幂等跳过留痕）。"""
        best: dict[str, tuple[float, str]] = {}
        for m in mapped:
            if m.direction is SignalDirection.NEUTRAL:
                continue
            d = "LONG" if m.direction is SignalDirection.LONG else "SHORT"
            if d not in best or abs(m.strength) > abs(best[d][0]):
                best[d] = (m.strength, m.pattern_id)
        key = _payload_idempotency_key(payload)
        ids: list[str] = []
        for d in sorted(best):
            strength, pid = best[d]
            draft = SignalDraft(
                signal_id=f"{key}:{d}",
                symbol=str(payload["symbol"]),
                direction=d,
                strength=abs(strength),
                source=f"{self._source}:{pid}",
            )
            try:
                self._factory.register(draft)
                ids.append(draft.signal_id)
            except ValueError:
                metadata_note = "factory_duplicate_skipped"
                ids.append(draft.signal_id)
                log_note = payload.setdefault("notes", [])
                if isinstance(log_note, list) and metadata_note not in log_note:
                    log_note.append(metadata_note)
        return ids
