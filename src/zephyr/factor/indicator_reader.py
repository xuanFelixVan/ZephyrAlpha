# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.indicator_reader
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.factor.technical_indicators.indicator_base; pandas(pip)
# [CONSUMERS] 回测/因子消费方（批 7 消费端接线批首建，docs/_working/2026-09-14-tilib-batch7-wiring-plan.md 块 A）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT 铁律：end>as_of 硬拒；预热 NaN 不前向填充；列名白名单校验（防拼错静默空返回）；只读
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法列名/period→ValueError；as_of 越界→ValueError；CH 不可达→异常透传
# [TESTS] tests/zephyr/factor/test_indicator_reader.py
# [A_module] module_id=MOD-L02-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""技术指标 PIT 安全读取 API（批 7 消费端接线批，2026-09-14）。

消费范式（对齐 Qlib DataLoader→Handler 分层，qlib.readthedocs.io/en/v0.6.2/component/data.html）：
指标宽表 c1_market.technical_indicator = 预计算特征库（DataLoader 层），
本模块 = 消费方统一读取入口（Handler 层薄封装）。

三约束：
  1. PIT：as_of 给定时 end>as_of 直接 ValueError（禁"用未来数据算现在的指标"）
  2. 去重：经 ch_reader 自动注入 FINAL（ReplacingMergeTree 同键取最新）
  3. 白名单：columns 必须在 TechnicalIndicatorRegistry 注册输出列内
     （拼错列名 → ValueError 而非静默空 DataFrame）

预热语义：指标预热期在表中即 NULL，本层不前向填充——消费方自行决定
（fill/丢头/截断），这是 16 号设计文档"PIT 铁律在指标层"的消费端延续。
"""

from __future__ import annotations

import io
import logging
from datetime import date, datetime

import pandas as pd

from zephyr.data import ch_reader

logger = logging.getLogger(__name__)

_TABLE = "c1_market.technical_indicator"
_VALID_PERIODS = ("1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly")


def _valid_columns() -> set[str]:
    """注册表白名单（延迟导入防环）。"""
    from zephyr.factor.technical_indicators import autodiscover_technical_indicators
    from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

    if not TechnicalIndicatorRegistry.list_all():
        autodiscover_technical_indicators()
    return set(TechnicalIndicatorRegistry.list_output_columns())


def read_indicator(
    symbol: str,
    period: str = "daily",
    columns: list[str] | tuple[str, ...] = (),
    start: str | date | datetime | None = None,
    end: str | date | datetime | None = None,
    as_of: str | date | datetime | None = None,
) -> pd.DataFrame:
    """PIT 安全读取技术指标宽表。

    Args:
        symbol: 证券代码，**裸码口径与 kline 表一致**（如 '000852'；全市场扫描显式传 '*'）
        period: 周期（9 值枚举）
        columns: 指标输出列子集（白名单校验；空=全部指标列）
        start/end: 日期闭区间（str YYYY-MM-DD / date / datetime）
        as_of: PIT 截止日——end 晚于 as_of 时硬拒（回测防前视）

    Returns:
        DataFrame（index=RangeIndex；含 trade_date/trade_time/symbol/period + 指标列）

    Raises:
        ValueError: 列名不在白名单 / period 非法 / end>as_of / symbol 为空
    """
    if not symbol:
        raise ValueError("symbol 不能为空（全市场扫描显式传 '*'）")
    if period not in _VALID_PERIODS:
        raise ValueError(f"非法 period: {period}（可选 {_VALID_PERIODS}）")

    whitelist = _valid_columns()
    cols = list(columns) if columns else sorted(whitelist)
    illegal = [c for c in cols if c not in whitelist]
    if illegal:
        raise ValueError(f"非法指标列（不在注册表白名单）: {illegal}；请对照 TechnicalIndicatorRegistry")

    end_d = _to_date(end) if end else date.today()
    if as_of is not None:
        as_of_d = _to_date(as_of)
        if end_d > as_of_d:
            raise ValueError(f"PIT 违规: end({end_d}) 晚于 as_of({as_of_d})——回测读取禁止前视")
        if as_of_d > date.today():
            raise ValueError(f"as_of({as_of_d}) 在未来")

    where_parts = [f"period = '{period}'", f"symbol = '{symbol}'" if symbol != "*" else "1"]
    if start:
        where_parts.append(f"trade_date >= '{_to_date(start)}'")
    if end:
        where_parts.append(f"trade_date <= '{end_d}'")
    frame_cols = ["trade_date", "trade_time", "symbol", "period", *cols]
    select_cols = ", ".join(frame_cols)
    # ch_writer.query 对 SELECT 强制 FORMAT TSV（无表头）——列名按 SELECT 顺序自行构造
    sql = f"SELECT {select_cols} FROM {_TABLE} WHERE {' AND '.join(where_parts)} ORDER BY trade_time"

    tsv = ch_reader.query(sql)
    if not tsv.strip():
        return pd.DataFrame(columns=frame_cols)
    df = pd.read_csv(io.StringIO(tsv), sep="\t", header=None, names=frame_cols)
    logger.info("read_indicator: %s %s %d 列 %d 行 (%s~%s)", symbol, period, len(cols), len(df), start, end)
    return df


def _to_date(v: str | date | datetime) -> date:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return date.fromisoformat(v)
