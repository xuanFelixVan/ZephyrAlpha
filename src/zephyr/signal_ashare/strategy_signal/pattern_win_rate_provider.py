# [BLUEPRINT] MOD-SIG-145 | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] schemas.categories.market_pattern_win_rate(INSERT_COLUMNS 真源); zephyr.data.ch_writer(client,延迟加载)
# [CONSUMERS] MOD-SIG-115 pattern_to_signal_mapper（historical_win_rate 注入契约）; unified_pattern_engine win_rate_provider 参数（W4 接线）; REG-PAT-001 evidence 回填（W4）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 只读 c1_market.market_pattern_win_rate；low_sample=true 或 hit_rate=NULL 或查无→返回 None（保持 MOD-SIG-091 契约：无统计=None，消费方退化行为不变）；注入式 client（测试不触库）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查无/样本不足/中性=NULL 语义->返回 None；client 不可得->RuntimeError
# [TESTS] tests/signal_ashare/test_pattern_win_rate_provider.py
# [A_module] module_id=MOD-SIG-145 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图形历史胜率 provider（MOD-SIG-145 W3——win_rate_provider 注入契约的实现侧）。

MOD-SIG-091 引擎蓝图约定"引擎不自建统计，win_rate_provider 注入（None=无统计）"，
MOD-SIG-115 映射器按 强度=置信度×胜率 加权——本模块补齐注入侧：

    c1_market.market_pattern_win_rate（W3 物化统计）
    → PatternWinRateProvider.get(pattern_id, timeframe, direction, fwd_window, regime_tag)
    → float | None（None=无统计/样本不足，消费方退化为现状）

baseline 对照：get_baseline(...) 返回 '__baseline__' 行（全体事件同口径），
消费方可算形态相对基准的增量（hit_rate - baseline）。
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

_FULL_TABLE = "c1_market.market_pattern_win_rate"
_BASELINE_ID = "__baseline__"


class PatternWinRateProvider:
    """c1_market.market_pattern_win_rate 只读出口（注入式 client，测试不触库）。"""

    def __init__(self, client=None, table: str = _FULL_TABLE):
        self._client = client
        self._table = table

    def _ensure_client(self):
        if self._client is None:
            from zephyr.data.ch_writer import get_client

            self._client = get_client()
        if self._client is None:
            raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
        return self._client

    def get(
        self,
        pattern_id: str,
        *,
        timeframe: str = "day",
        direction: str = "向上",
        fwd_window: int = 10,
        regime_tag: str = "",
    ) -> float | None:
        """查形态历史胜率；查无 / low_sample / hit_rate=NULL → None。

        None 语义 = MOD-SIG-091 契约的"无统计"：消费方必须退化为现状行为，
        禁止把 None 当 0 或 0.5 参与加权。
        """
        row = self._fetch_one(
            pattern_id=pattern_id,
            timeframe=timeframe,
            direction=direction,
            fwd_window=fwd_window,
            regime_tag=regime_tag,
        )
        return self._to_rate(row)

    def get_baseline(
        self,
        *,
        timeframe: str = "day",
        direction: str = "向上",
        fwd_window: int = 10,
        regime_tag: str = "",
    ) -> float | None:
        """全体事件基准胜率（pattern_id='__baseline__'），供相对增量对照。"""
        row = self._fetch_one(
            pattern_id=_BASELINE_ID,
            timeframe=timeframe,
            direction=direction,
            fwd_window=fwd_window,
            regime_tag=regime_tag,
        )
        return self._to_rate(row)

    def _fetch_one(
        self,
        *,
        pattern_id: str,
        timeframe: str,
        direction: str,
        fwd_window: int,
        regime_tag: str,
    ) -> dict[str, Any] | None:
        client = self._ensure_client()
        rows = client.execute(
            f"SELECT n_events, hit_rate, low_sample FROM {self._table} FINAL "
            "WHERE pattern_id = %(p)s AND timeframe = %(tf)s AND direction = %(d)s "
            "AND fwd_window = %(w)d AND regime_tag = %(rt)s "
            "LIMIT 1",
            {"p": pattern_id, "tf": timeframe, "d": direction, "w": int(fwd_window), "rt": regime_tag},
        )
        if not rows:
            return None
        return {"n_events": rows[0][0], "hit_rate": rows[0][1], "low_sample": rows[0][2]}

    @staticmethod
    def _to_rate(row: dict[str, Any] | None) -> float | None:
        if row is None:
            return None
        if row.get("low_sample"):
            return None
        rate = row.get("hit_rate")
        if rate is None:
            return None
        return float(rate)


def default_provider() -> PatternWinRateProvider:
    """生产默认 provider（延迟取 ch_writer writer 通道 client）。"""
    return PatternWinRateProvider()


__all__ = [
    "PatternWinRateProvider",
    "default_provider",
]
