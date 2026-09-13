#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §alt-regime
# [MODULE] zephyr.alt_data.alt_regime_signals
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.ch_reader; stdlib
# [CONSUMERS] zephyr.data.scheduler; regime 消费链（index_regime_panel/risk_signal_builder 后续接线）
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] 市场级信号计算器——只读 CH 另类表、不发外部请求、不做个股横截面（个股因子走 factor_feature_value）；
#              全历史重算幂等（ReplacingMergeTree 同键替换）；PIT=signal_date 仅用 ≤当日收盘数据；
#              涨停情绪阶段阈值 v1 为社区共识 provisional（挖矿 R10 多源），毕业前不得进决策硬链
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源表缺失/空数据->yield FetchResult(error=...) 单信号降级不拖垮其他信号
# [TESTS] tests/zephyr/alt_data/test_alt_regime_signals.py
# [TTL] permanent
"""AltRegimeSignalProvider — 市场级另类数据 regime 信号计算器（C-1 消费端首批）.

消费方案：docs/_working/alt_data_consumption_plan.md（F4/F7/F14/F15/F23 设计卡）。

信号位 -> 数据源（全部已落库）：
    F4_BDI_MOMENTUM_Z20   c1_market.alt_shipping_index (BDI)      20 日动量 vs 252 日分布 z 分数
    F14_BTC_MOMENTUM_30D  c1_market.crypto_kline_daily (BTCUSDT)  30 日收益 %
    F15_FNG_INDEX         c1_market.sentiment_panel (fear_greed_index) 恐贪 0-100 + 极值分档
    F23_LIMITUP_EMOTION   c1_market.limit_up_down (涨停)          连板高度/晋级率/涨停家数 -> 阶段
    F7_TYPHOON_EVENT      内置事件表（11 次登陆台风，已实弹验证 BDI 后 10 日均值 +8.86%）

消费定位：market regime 输入（轮动/风险节流），非个股 alpha；F15 极值反转与 F23 阶段
为 C4 双窗及格策略（恐慌反弹）的信号源候选，毕业前不得进决策硬链。
"""

from __future__ import annotations

import datetime
import json
import logging
import time
from typing import Iterator

import pandas as pd

from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)

log = logging.getLogger(__name__)

_SIGNAL_COLUMNS = ["signal_date", "signal_id", "signal_value", "state", "detail", "source"]
_SOURCE = "alt_regime_signals"

_ALT_REGIME_CAPABILITIES = frozenset({"alt_regime_signal"})

# F15 恐贪分档（alternative.me 官方口径）
_FNG_BANDS = ((20, "extreme_fear"), (40, "fear"), (60, "neutral"), (80, "greed"), (101, "extreme_greed"))

# F23 阶段阈值 v1（provisional：挖矿 R10 社区共识口径，待 OOS 毕业校准）
_PHASE_PROMOTION_HIGH = 0.6
_PHASE_PROMOTION_LOW = 0.3
_PHASE_HEIGHT_HIGH = 5
_PHASE_HEIGHT_MID = 3


# ================= 纯函数计算核（可独立单测） =================

def momentum_zscore(close: pd.Series, window: int = 20, norm: int = 252) -> pd.Series:
    """动量 z 分数：window 日收益对其 norm 日滚动分布标准化（需 ≥window+norm+1 样本，暖机期 NaN）。"""
    mom = close.pct_change(window)
    return (mom - mom.rolling(norm).mean()) / mom.rolling(norm).std()


def z_state(z: float, band: float = 1.0) -> str:
    if z != z:  # NaN 暖机期
        return "warmup"
    if z >= band:
        return "risk_on"
    if z <= -band:
        return "risk_off"
    return "neutral"


def ret_state(ret_pct: float, band_pct: float = 0.0) -> str:
    if ret_pct != ret_pct:
        return "warmup"
    return "risk_on" if ret_pct > band_pct else "risk_off"


def fng_state(value: float) -> str:
    for upper, label in _FNG_BANDS:
        if value < upper:
            return label
    return "extreme_greed"


def limitup_streaks(streaks: dict[str, int], today_symbols: set[str]) -> dict[str, int]:
    """连板 streak 单日推进：昨日 streak + 今日仍涨停 = +1，否则重置（缺席=重置）。

    streak 口径：按涨停事件表中出现过的交易日序列连计（停牌视为断板，v1 简化并文档化）。
    """
    new_streaks: dict[str, int] = {}
    for sym in today_symbols:
        new_streaks[sym] = streaks.get(sym, 0) + 1
    return new_streaks


def limitup_emotion_phase(height: int, promotion: float) -> str:
    """涨停情绪阶段 v1：provisional 阈值（挖矿 R10 社区共识），毕业前不得进决策硬链。"""
    if height >= _PHASE_HEIGHT_HIGH and promotion >= _PHASE_PROMOTION_HIGH:
        return "高潮"
    if promotion < _PHASE_PROMOTION_LOW:
        return "退潮"
    if height >= _PHASE_HEIGHT_MID and promotion >= 0.4:
        return "发酵"
    return "中性"


# ================= Provider 壳（CH 读取 + 组装 FetchResult） =================

class AltRegimeSignalProvider(IngestProviderBase):
    """市场级另类 regime 信号 provider（source=alt_regime_signal，全历史重算幂等）。"""

    _connected: bool = False

    meta: IngestProviderMeta = IngestProviderMeta(
        name="alt_regime_signal",
        display_name="另类数据市场级 regime 信号",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,
        capabilities=[
            CapabilityContract(
                "alt_regime_signal",
                supports_symbols_null=True,
                supports_incremental=False,
                supports_full_refresh=True,
                requires_date_range=False,
                expected_market="cross",
                expected_variety="index",
            ),
        ],
        known_issues=[
            "F15 依赖 sentiment_panel 表（crypto_fear_greed_incremental 任务先行）",
            "F23 阶段阈值为 provisional v1，待 OOS 毕业校准",
        ],
    )

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        """无持久连接资源。"""

    def health_check(self) -> bool:
        return True

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """计算全部信号位并整表重算（增量声明不支持，RMT 幂等去重）。"""
        cap = (payload.extra or {}).get("capability")
        if cap not in _ALT_REGIME_CAPABILITIES:
            yield FetchResult(
                table=payload.table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"unsupported capability: {cap}",
            )
            return

        table = payload.table or "c1_market.alt_regime_signal"
        t0 = time.monotonic()
        rows: list[tuple] = []
        errors: list[str] = []
        for sid, computed in self._compute_all_signals():
            try:
                rows.extend(computed)
            except Exception as e:  # noqa: BLE001 — 单信号降级不拖垮其他信号
                errors.append(f"{sid}: {e}")
                self._log.warning(f"{sid} 计算失败: {e}")

        if not rows and errors:
            yield FetchResult(
                table=table, columns=_SIGNAL_COLUMNS, rows=[], last_key="",
                elapsed_sec=time.monotonic() - t0, error="; ".join(errors),
            )
            return
        yield FetchResult(
            table=table, columns=_SIGNAL_COLUMNS, rows=rows,
            last_key=max((r[0] for r in rows), default=""),
            elapsed_sec=time.monotonic() - t0,
        )

    # ---- 各信号计算（CH 读取 + 纯函数核） ----

    def _compute_all_signals(self):
        from zephyr.data import ch_reader

        yield "F4_BDI_MOMENTUM_Z20", self._compute_bdi(ch_reader)
        yield "F14_BTC_MOMENTUM_30D", self._compute_btc(ch_reader)
        yield "F15_FNG_INDEX", self._compute_fng(ch_reader)
        yield "F23_LIMITUP_EMOTION", self._compute_limitup(ch_reader)
        yield "F7_TYPHOON_EVENT", self._compute_typhoon(ch_reader)

    @staticmethod
    def _row(signal_date: str, sid: str, value: float, state: str, detail: dict) -> tuple:
        return (signal_date, sid, float(value), state, json.dumps(detail, ensure_ascii=False), _SOURCE)

    def _compute_bdi(self, ch_reader) -> list[tuple]:
        """F4：BDI 20 日动量 z 分数（窗口 20/规范 252，暖机期跳过）。

        位置访问（防重复日期标签下 .loc 返回 Series）。
        """
        tsv = ch_reader.query(
            "SELECT trade_date, value FROM c1_market.alt_shipping_index FINAL "
            "WHERE index_code='BDI' ORDER BY trade_date"
        )
        data = [ln.split("\t") for ln in tsv.strip().split("\n") if ln.strip()]
        close = pd.Series([float(v) for _, v in data])
        mom = close.pct_change(20)
        z = momentum_zscore(close)
        out = []
        for i in range(len(data)):
            zv = z.iloc[i]
            if zv != zv:  # 暖机期
                continue
            zval = round(float(zv), 4)
            out.append(self._row(
                data[i][0], "F4_BDI_MOMENTUM_Z20", zval, z_state(zval),
                {"mom20": round(float(mom.iloc[i]) * 100, 2)},
            ))
        return out

    def _compute_btc(self, ch_reader) -> list[tuple]:
        """F14：BTCUSDT 30 日收益 %（位置访问）。"""
        tsv = ch_reader.query(
            "SELECT trade_date, close FROM c1_market.crypto_kline_daily FINAL "
            "WHERE symbol='BTCUSDT' ORDER BY trade_date"
        )
        data = [ln.split("\t") for ln in tsv.strip().split("\n") if ln.strip()]
        close = pd.Series([float(v) for _, v in data])
        ret = close.pct_change(30) * 100
        out = []
        for i in range(len(data)):
            rv = ret.iloc[i]
            if rv != rv:
                continue
            rval = round(float(rv), 4)
            out.append(self._row(data[i][0], "F14_BTC_MOMENTUM_30D", rval, ret_state(rval), {}))
        return out

    def _compute_fng(self, ch_reader) -> list[tuple]:
        """F15：恐贪指数极值分档（<20 extreme_fear=反转窗候选）。"""
        tsv = ch_reader.query(
            "SELECT trade_date, value FROM c1_market.sentiment_panel FINAL "
            "WHERE metric='fear_greed_index' ORDER BY trade_date"
        )
        data = [ln.split("\t") for ln in tsv.strip().split("\n") if ln.strip()]
        out = []
        for d, v in data:
            val = float(v)
            out.append(self._row(d, "F15_FNG_INDEX", val, fng_state(val), {}))
        return out

    def _compute_limitup(self, ch_reader) -> list[tuple]:
        """F23：涨停情绪——涨停家数/连板高度/晋级率 -> 阶段（全历史逐日推进）。"""
        tsv = ch_reader.query(
            "SELECT trade_date, symbol FROM c1_market.limit_up_down FINAL "
            "WHERE limit_type='涨停' ORDER BY trade_date"
        )
        data = [ln.split("\t") for ln in tsv.strip().split("\n") if ln.strip()]
        by_date: dict[str, set[str]] = {}
        for d, sym in data:
            by_date.setdefault(d, set()).add(sym)
        dates = sorted(by_date)
        out: list[tuple] = []
        streaks: dict[str, int] = {}
        prev_symbols: set[str] = set()
        for d in dates:
            today = by_date[d]
            streaks = limitup_streaks(streaks, today)
            height = max(streaks.values()) if streaks else 0
            promotion = (len(today & prev_symbols) / len(prev_symbols)) if prev_symbols else float("nan")
            phase = limitup_emotion_phase(height, promotion) if promotion == promotion else "warmup"
            out.append(self._row(
                d, "F23_LIMITUP_EMOTION", round(promotion, 4) if promotion == promotion else 0.0,
                phase,
                {"height": height, "limit_count": len(today), "promotion": round(promotion, 4) if promotion == promotion else None},
            ))
            prev_symbols = today
        return out

    def _compute_typhoon(self, ch_reader) -> list[tuple]:
        """F7：台风登陆事件（alt_typhoon_landfall_history × alt_typhoon_track 联合推导）。

        landfall_history 提供事件本体（年/编号/中文名/省份/强度），track 提供
        精确日期（该台风首个预报点日期=事件窗起点代理）。同日多登陆合并进 detail。
        Join 键：track.tcno 为年+序号四位码（2317=2023 年 17 号），landfall.tcno 为
        纯序号（17）——映射 (track_year, int(tcno)%100)；tcno='0000' 为脏码剔除。
        """
        lf_tsv = ch_reader.query(
            "SELECT year, tcno, tc_cn_name, land_prov, land_lev FROM c1_market.alt_typhoon_landfall_history FINAL"
        )
        lf_rows = [ln.split("\t") for ln in lf_tsv.strip().split("\n") if ln.strip()]
        if not lf_rows:
            raise RuntimeError("alt_typhoon_landfall_history 空，F7 无法计算")
        tk_tsv = ch_reader.query(
            "SELECT toYear(parseDateTimeBestEffort(issue_ts)) AS y, tcno, "
            "min(toDate(parseDateTimeBestEffort(issue_ts))) AS first_date "
            "FROM c1_market.alt_typhoon_track FINAL WHERE tcno != '0000' GROUP BY y, tcno"
        )
        first_date: dict[tuple[str, int], str] = {}
        for ln in tk_tsv.strip().split("\n"):
            if not ln.strip():
                continue
            y, tcno, d = ln.split("\t")
            try:
                first_date[(y.strip(), int(tcno.strip()) % 100)] = d.strip()
            except ValueError:  # 非四位码格式，跳过
                continue

        by_date: dict[str, list[dict]] = {}
        skipped = 0
        for year, tcno, cn_name, prov, lev in lf_rows:
            d = first_date.get((year.strip(), int(tcno.strip())))
            if not d:
                skipped += 1
                continue
            by_date.setdefault(d, []).append(
                {"name": cn_name, "prov": prov, "lev": lev, "year": year}
            )
        if skipped:
            self._log.warning(f"F7: {skipped} 条登陆记录在 track 中无日期（跳过，多为 2017 前历史）")
        out = []
        for d in sorted(by_date):
            events = by_date[d]
            out.append(self._row(
                d, "F7_TYPHOON_EVENT", float(len(events)), "landfall",
                {"events": events, "window_days": 10},
            ))
        return out
