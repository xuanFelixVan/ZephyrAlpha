# [BLUEPRINT] MOD-DAT-MTF-FUSION | docs/03_modules/_domain_data/multi_timeframe_fusion/blueprint.md
# [MODULE] zephyr.data.multi_timeframe_fusion
# [DOMAIN] D_DATA
# [DEPENDENCIES] pandas（纯内存计算；zephyr.data.calendar 仅 TYPE_CHECKING 类型注解，零运行时 zephyr import）
# [CONSUMERS] 运行时装配批（miniqmt_service/mkt_data 多周期消费接线 / 交易日历真源装配）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 统一 resample 接口 1min~1d；bar close 时间戳归一；ffill 上限默认 3 根超限留 NaN；同输入必同输出；OHLC 聚合 open首/high max/low min/close尾/volume sum
# [MODIFY-GUARD] docs/03_modules/_domain_data/multi_timeframe_fusion/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知频率/缺必需列/粒度倒挂→ValueError
# [TESTS] tests/zephyr/data/test_multi_timeframe_fusion.py
# [A_module] module_id=MOD-DAT-MTF-FUSION | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
MultiTimeframeFusion — 多时间尺度数据融合（MOD-DAT-MTF-FUSION）

B13-04249（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-DATA-25，§17.1）：
``resample()`` 统一接口（1min~1d）——交易日历对齐 + 时间戳归一
（bar close 口径）+ 前向填充上限（≤3 根）+ 融合质量评分（覆盖率/对齐
误差）输出 quality_flag。纯 pandas 内存计算，provider 无关。

查重裁定：kline_resampler（MOD-L00-004，10603322）为 880 板块 K线
15m/30m/60m ClickHouse 库内合成（DB 面向、板块专用）；本模块为内存态
统一重采样接口（任意标的、1min~1d 全域、质量评分面向），不复制其 SQL
合成路径。B1-00634 dig 已裁定重复并入本模块。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: multi_timeframe_fusion.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MultiTimeframeFusion
#   name_en: MultiTimeframeFusion
#   intro: 多周期数据融合器（纯 pandas 内存计算，零 IO）。
#   desc: 多周期数据融合器（纯 pandas 内存计算，零 IO）。；公共方法（定义序）: resample；源码 L124-L274
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: MultiTimeframeFusion
#   downstream: 运行时装配批（miniqmt_service/mkt_data 多周期消费接线 / 交易日历真源装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Optional, Sequence

import pandas as pd

if TYPE_CHECKING:  # 仅类型注解：保持本模块零运行时 zephyr import（纯 pandas 不变量）
    from zephyr.data.calendar.base import MarketCalendar

log = logging.getLogger(__name__)

__all__: Final = [
    "FusionConfig",
    "FusionQuality",
    "FusionResult",
    "MultiTimeframeFusion",
    "SUPPORTED_FREQS",
]

#: 频率表：目标频率 → 分钟数（1d=1440 特例；4h=240 币 7×24 周期，CAND-CRYPTO-001 增量，
#: A股 9 周期不含 4h——A股调用路径不触碰该键，零行为变化）
SUPPORTED_FREQS: Final[dict[str, int]] = {
    "1min": 1,
    "5min": 5,
    "15min": 15,
    "30min": 30,
    "60min": 60,
    "4h": 240,
    "1d": 1440,
}

REQUIRED_COLUMNS: Final = ("timestamp", "open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class FusionQuality:
    """融合质量评分。"""

    expected_bars: int
    actual_bars: int
    coverage_ratio: float
    alignment_error_count: int
    ffill_used: int
    quality_flag: str


@dataclass(frozen=True)
class FusionResult:
    """融合结果：重采样后 DataFrame + 质量评分。"""

    data: pd.DataFrame
    quality: FusionQuality


@dataclass(frozen=True)
class FusionConfig:
    """配置。"""

    ffill_limit: int = 3
    good_coverage: float = 0.95
    degraded_coverage: float = 0.80


class MultiTimeframeFusion:
    """多周期数据融合器（纯 pandas 内存计算，零 IO）。"""

    def __init__(self, config: FusionConfig | None = None) -> None:
        self._config = config or FusionConfig()
        if self._config.ffill_limit < 0:
            raise ValueError("ffill_limit 不能为负")

    # ── 校验 ──

    @staticmethod
    def _validate(bars: pd.DataFrame, source_freq: str, target_freq: str) -> None:
        if source_freq not in SUPPORTED_FREQS:
            raise ValueError(f"未知源频率: {source_freq!r}（合法: {tuple(SUPPORTED_FREQS)}）")
        if target_freq not in SUPPORTED_FREQS:
            raise ValueError(f"未知目标频率: {target_freq!r}（合法: {tuple(SUPPORTED_FREQS)}）")
        if SUPPORTED_FREQS[source_freq] >= SUPPORTED_FREQS[target_freq]:
            raise ValueError(f"粒度倒挂: {source_freq} → {target_freq}（源须细于目标）")
        missing = [c for c in REQUIRED_COLUMNS if c not in bars.columns]
        if missing:
            raise ValueError(f"缺必需列: {missing}")

    # ── 主接口 ──

    def resample(
        self,
        bars: pd.DataFrame,
        source_freq: str,
        target_freq: str,
        trading_days: Sequence[datetime.date] | None = None,
        ffill_limit: int | None = None,
        expected_start: pd.Timestamp | None = None,
        expected_end: pd.Timestamp | None = None,
        calendar: MarketCalendar | None = None,
    ) -> FusionResult:
        """统一重采样：交易日历对齐 + bar close 归一 + ffill 上限 + 质量评分。

        Args:
            calendar: 可选市场日历注入（CAND-CRYPTO-001）。仅当 trading_days 未显式
                传入且 expected_start/expected_end 齐备时，展开为
                calendar.trading_days_in_range(start.date(), end.date()) 作为日历
                对齐集合；显式 trading_days 永远优先。未注入时行为与现状逐字节一致。
        """
        self._validate(bars, source_freq, target_freq)
        if trading_days is None and calendar is not None and expected_start is not None and expected_end is not None:
            trading_days = calendar.trading_days_in_range(
                pd.Timestamp(expected_start).date(),
                pd.Timestamp(expected_end).date(),
            )
        cfg = self._config
        limit = cfg.ffill_limit if ffill_limit is None else ffill_limit
        if limit < 0:
            raise ValueError("ffill_limit 不能为负")
        tmin = SUPPORTED_FREQS[target_freq]
        smin = SUPPORTED_FREQS[source_freq]
        rule = f"{tmin}min"

        df = bars.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        if df.empty and (expected_start is None or expected_end is None):
            return FusionResult(
                data=df[[c for c in REQUIRED_COLUMNS]].reset_index(drop=True),
                quality=FusionQuality(0, 0, 0.0, 0, 0, "poor"),
            )

        # 对齐误差：源条未落地源频率边界
        src_floor = df["timestamp"].dt.floor(f"{smin}min")
        alignment_errors = int((df["timestamp"] != src_floor).sum())

        # 目标桶：floor 到目标边界；bar close = 桶起点 + 目标分钟
        df["bin_start"] = df["timestamp"].dt.floor(rule)

        grouped = []
        for bin_start, g in df.groupby("bin_start", sort=True):
            g = g.sort_values("timestamp")
            grouped.append(
                {
                    "bin_start": bin_start,
                    "timestamp": bin_start + pd.Timedelta(minutes=tmin),
                    "open": g.iloc[0]["open"],
                    "high": g["high"].max(),
                    "low": g["low"].min(),
                    "close": g.iloc[-1]["close"],
                    "volume": g["volume"].sum(),
                }
            )
        agg = pd.DataFrame(grouped)

        # 应到桶序列
        if expected_start is not None and expected_end is not None:
            first_bin = pd.Timestamp(expected_start).floor(rule)
            bins = []
            cur = first_bin
            while cur < pd.Timestamp(expected_end):
                bins.append(cur)
                cur += pd.Timedelta(minutes=tmin)
            expected = pd.DataFrame({"bin_start": bins})
        else:
            expected = agg[["bin_start"]].copy()

        # 交易日历对齐：剔除日历外目标桶
        if trading_days is not None:
            tdays = {pd.Timestamp(d).date() for d in trading_days}
            expected = expected[expected["bin_start"].map(lambda b: b.date() in tdays)]
            agg = agg[agg["bin_start"].map(lambda b: b.date() in tdays)]

        merged = expected.merge(agg, on="bin_start", how="left").sort_values("bin_start")
        merged = merged.reset_index(drop=True)
        merged["timestamp"] = merged["bin_start"] + pd.Timedelta(minutes=tmin)

        # ffill：连续缺口 ≤ limit 根以前值填充（价格四列带前值，volume=0）
        ffill_used = 0
        gap_run = 0
        last_close: float | None = None
        for i in range(len(merged)):
            if pd.notna(merged.at[i, "close"]):
                gap_run = 0
                last_close = merged.at[i, "close"]
                continue
            if last_close is not None and gap_run < limit:
                for col in ("open", "high", "low", "close"):
                    merged.at[i, col] = last_close
                merged.at[i, "volume"] = 0
                gap_run += 1
                ffill_used += 1
            else:
                gap_run += 1  # 超限留 NaN

        expected_bars = len(merged)
        actual_bars = int(merged["close"].notna().sum())
        coverage = (actual_bars / expected_bars) if expected_bars else 0.0
        if coverage >= cfg.good_coverage:
            flag = "good"
        elif coverage >= cfg.degraded_coverage:
            flag = "degraded"
        else:
            flag = "poor"

        out = merged[["timestamp", "open", "high", "low", "close", "volume"]]
        return FusionResult(
            data=out.reset_index(drop=True),
            quality=FusionQuality(
                expected_bars=expected_bars,
                actual_bars=actual_bars,
                coverage_ratio=coverage,
                alignment_error_count=alignment_errors,
                ffill_used=ffill_used,
                quality_flag=flag,
            ),
        )
