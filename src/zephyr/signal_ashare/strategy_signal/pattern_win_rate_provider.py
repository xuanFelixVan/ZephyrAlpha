# [BLUEPRINT] MOD-SIG-145 | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] schemas.categories.market.market_pattern_win_rate(INSERT_COLUMNS 真源); zephyr.data.ch_writer(client,延迟加载)
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
_Z95 = 1.959963984540054


def _wilson_lower_bound(rate: float, n: int, *, z: float = _Z95) -> float:
    """Wilson 得分区间下界（二项比例小样本保守估计）。

    n<=0 → 0.0（无样本=零信任）；LB 恒 ≤ rate，n 越大越贴近 rate。
    消费班方案 v1.0 挖矿 M1 裁定：加权输入用 LB 口径（TradingView
    winrate 脚本实照同法），raw 口径仍经 get()/get_detail() 可得。
    """
    if n <= 0:
        return 0.0
    p = float(rate)
    denom = 1.0 + z * z / n
    centre = p + z * z / (2.0 * n)
    margin = z * ((p * (1.0 - p) + z * z / (4.0 * n)) / n) ** 0.5
    return max(0.0, (centre - margin) / denom)


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

    def get_detail(
        self,
        pattern_id: str,
        *,
        timeframe: str = "day",
        direction: str = "向上",
        fwd_window: int = 10,
        regime_tag: str = "",
    ) -> dict[str, Any] | None:
        """查全行（hit_rate/n_events/low_sample）——审计快照与小样本判读用。

        查无→None；行内字段原样返回（不做 None/low_sample 归并，由消费方判读）。
        """
        return self._fetch_one(
            pattern_id=pattern_id,
            timeframe=timeframe,
            direction=direction,
            fwd_window=fwd_window,
            regime_tag=regime_tag,
        )

    def get_conservative(
        self,
        pattern_id: str,
        *,
        timeframe: str = "day",
        direction: str = "向上",
        fwd_window: int = 10,
        regime_tag: str = "",
        z: float = _Z95,
    ) -> float | None:
        """Wilson 95% 下界口径的历史胜率（消费班方案 v1.0 挖矿 M1）。

        与 get() 同门禁（查无/low_sample/NULL→None），有统计时返回
        wilson_lower_bound(hit_rate, n_events)——小样本保守估计，防
        n 小时的过信加权（20 笔 55% 真胜率的观测噪声带 40%~70%）。
        """
        row = self._fetch_one(
            pattern_id=pattern_id,
            timeframe=timeframe,
            direction=direction,
            fwd_window=fwd_window,
            regime_tag=regime_tag,
        )
        rate = self._to_rate(row)
        if rate is None or row is None:
            return None
        n = int(row.get("n_events") or 0)
        return _wilson_lower_bound(rate, n, z=z)

    def list_pattern_ids(
        self,
        *,
        timeframe: str = "day",
        direction: str = "向上",
        fwd_window: int = 10,
        regime_tag: str = "",
    ) -> list[str]:
        """枚举统计表在册形态键（W-C3 调权同步的自动发现入口）。

        只返回键列表；样本门禁由 get/get_conservative 各自把关。
        """
        client = self._ensure_client()
        rows = client.execute(
            f"SELECT pattern_id FROM {self._table} FINAL "
            "WHERE timeframe = %(tf)s AND direction = %(d)s "
            "AND fwd_window = %(w)d AND regime_tag = %(rt)s "
            "AND pattern_id != %(base)s "
            "ORDER BY pattern_id",
            {"tf": timeframe, "d": direction, "w": int(fwd_window), "rt": regime_tag, "base": _BASELINE_ID},
        )
        return [str(r[0]) for r in rows]

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


# 引擎事件名 → 方向（经典腿封闭集；name-only 契约下方向可由名字唯一确定。
# 缠论/SR/趋势线等名字方向随事件变化，不在本表→wrapper 返回 None 走无统计路径）
_ENGINE_NAME_DIRECTION = {
    "双底": "向上",
    "双顶": "向下",
    "平台突破": "向上",
    "平台跌破": "向下",
    "头肩底": "向上",
    "头肩顶": "向下",
    "三重底": "向上",
    "三重顶": "向下",
    "上升三角形": "向上",
    "下降三角形": "向下",
    "上升楔形": "向下",
    "下降楔形": "向上",
}


def engine_win_rate_callable(
    provider: PatternWinRateProvider | None = None,
    *,
    timeframe: str = "day",
    fwd_window: int = 10,
    regime_tag: str = "",
) -> "callable":
    """组装 MOD-SIG-091 引擎的 win_rate_provider 注入物（Callable[[name], float|None]）。

    引擎契约只传事件 name（unified_pattern_engine L475）；本 wrapper 用
    name→方向封闭集补全查询键。查不到方向的名字（缠论/SR/趋势线等）返回
    None——引擎按"无统计"路径处理，行为退化为现状（fail-open 保持）。
    """
    provider = provider or PatternWinRateProvider()

    def _rate(name: str) -> float | None:
        direction = _ENGINE_NAME_DIRECTION.get(str(name))
        if direction is None:
            return None
        return provider.get(
            str(name),
            timeframe=timeframe,
            direction=direction,
            fwd_window=fwd_window,
            regime_tag=regime_tag,
        )

    return _rate


__all__ = [
    "PatternWinRateProvider",
    "default_provider",
    "engine_win_rate_callable",
]
