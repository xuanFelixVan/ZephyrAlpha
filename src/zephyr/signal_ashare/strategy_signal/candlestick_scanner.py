# [BLUEPRINT] MOD-SIG-145 | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_signal.candlestick_scanner
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] talib(CDL 61,ta-lib>=0.6 二进制轮子); zephyr.signal_ashare.strategy_signal.pattern_event_store(行契约)
# [CONSUMERS] c1_market.market_pattern_event（pattern_class=K线，data_source=candle_scanner）；pattern_win_rate 物化（胜率统计自动覆盖本模块事件）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 只读 OHLC 产出事件行 dict（落库统一走 pattern_event_store.build_event_rows 校验）；不触发任何信号/下单路径；direction=CDL 符号（100→向上/-100→向下）；confidence=MVP 初拍值 0.6（待回验标定批替换）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺 open/high/low/close 列->ValueError; talib 不可得->RuntimeError(建依赖 ta-lib>=0.6)
# [TESTS] tests/signal_ashare/test_candlestick_scanner.py
# [A_module] module_id=MOD-SIG-145 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""蜡烛形态扫描器（MOD-SIG-145 P2-a——83 条蜡烛目录的实现主体）。

三层来源：
    1. TA-Lib CDL 61 函数（行业标准语义，ta-lib>=0.6 自带二进制）——
       pattern_id=CDL 函数名（如 CDLHAMMER，基础名粒度天然成立）。
    2. A股特色 7 + Nison 镊子 2 + Crabel NR7 + 关键反转日/WRB/Oops +
       短线 + 三空 + 塔形 2 = 16 条手写规则（_EXTRA_RULES）；
       2026-09-15 增补 Bulkowski 小形态绩效榜 6 条（内包日/周线反转/开收反转/
       钩形反转/枢轴点反转/鲨鱼32，PAT-CANDLE-078..083）。
    3. 对应 REG-PAT-001 PAT-CANDLE-001..083，种子映射见
       _CDL_PAT_SEED / _EXTRA_PAT_SEED（evidence 回填与 code_path 同步用）。

事件口径（与统一形态引擎对齐）：
    anchor_trade_date/confirmed_at=该 K 线收盘（仅已完成 bar）；
    pattern_class=K线；direction=CDL 符号或规则判定（中性类如 NR7/短线=中性，
    胜率统计按 NULL 处理）；confidence=MVP 初拍 0.6。

塔形顶/底为 MVP 近似（高位长上影+两连跌 / 低位长下影+两连涨），
algorithm_status 维持 catalog 口径，回验标定批再收紧。
"""

from __future__ import annotations

import logging
from typing import Any, Callable

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

_REQUIRED_COLUMNS = ("open", "high", "low", "close")
_DEFAULT_CONFIDENCE = 0.6
_ASHARE_LIMIT_RATIO = 0.095  # 涨跌停判定容差（主板 10% 口径；创业板/科创板宽板另批）
_TOL = 1e-6

# TA-Lib CDL 61 → REG-PAT-001 PAT-CANDLE 种子映射（TA-Lib 官方语义名对照；
# evidence 回填/code_path 同步用，未列出的 CDL 表示目录条目 id 待核对）
_CDL_PAT_SEED = {
    "CDLHAMMER": "PAT-CANDLE-001",
}


def _cdl_functions() -> list[str]:
    """枚举 talib 全部 CDL 函数名（排序保证确定性）。"""
    import talib

    return sorted(f for f in dir(talib) if f.startswith("CDL") and callable(getattr(talib, f)))


# ── 手写规则（extras 16 条）─────────────────────────────────────
# 每条签名: fn(o, h, l, c, prev_c) -> (bull_mask, bear_mask) 或
# (neutral_mask,) —— numpy 布尔序列，anchor=当前 bar。


def _r_short_line(o, h, l, c, pc):  # PAT-CANDLE-062 短线
    body = np.abs(c - o)
    rng = h - l
    with np.errstate(divide="ignore", invalid="ignore"):
        small = np.where(rng > 0, body / rng < 0.3, False)
    return (), (), (small & (rng > 0),)


def _r_limit_up_flat(o, h, l, c, pc):  # 063 一字涨停板
    flat = (np.abs(h - l) < _TOL) & (np.abs(c - o) < _TOL) & (np.abs(h - c) < _TOL)
    lim = pc > 0
    up = np.zeros(len(o), dtype=bool)
    up[1:] = flat[1:] & lim[1:] & (c[1:] / pc[1:] - 1 >= _ASHARE_LIMIT_RATIO)
    return (up,), (), ()


def _r_limit_down_flat(o, h, l, c, pc):  # 064 一字跌停板
    flat = (np.abs(h - l) < _TOL) & (np.abs(c - o) < _TOL) & (np.abs(h - c) < _TOL)
    lim = pc > 0
    dn = np.zeros(len(o), dtype=bool)
    dn[1:] = flat[1:] & lim[1:] & (1 - c[1:] / pc[1:] >= _ASHARE_LIMIT_RATIO)
    return (), (dn,), ()


def _r_cuoxian(o, h, l, c, pc):  # 065 搓揉线（长上影+长下影连续两根，洗盘语义中性）
    body = np.abs(c - o)
    rng = h - l
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    b1 = (rng > 0) & (upper > 2 * body) & (body > 0)
    b2 = (rng > 0) & (lower > 2 * body) & (body > 0)
    both = np.zeros(len(o), dtype=bool)
    both[2:] = b1[1:-1] & b2[2:]
    return (), (), (both,)


def _r_tiandi(o, h, l, c, pc):  # 066 天地板（开涨停收跌停）
    lim = pc > 0
    m = np.zeros(len(o), dtype=bool)
    m[1:] = lim[1:] & (o[1:] / pc[1:] - 1 >= _ASHARE_LIMIT_RATIO) & (1 - c[1:] / pc[1:] >= _ASHARE_LIMIT_RATIO)
    return (), (m,), ()


def _r_ditian(o, h, l, c, pc):  # 067 地天板（开跌停收涨停）
    lim = pc > 0
    m = np.zeros(len(o), dtype=bool)
    m[1:] = lim[1:] & (1 - o[1:] / pc[1:] >= _ASHARE_LIMIT_RATIO) & (c[1:] / pc[1:] - 1 >= _ASHARE_LIMIT_RATIO)
    return (), (m,), ()


def _r_one_yang_mas(o, h, l, c, pc):  # 068 一阳穿多线（开在均线下、收在均线上）
    import warnings

    mas = []
    for n in (5, 10, 20, 30):
        ma = pd.Series(c).rolling(n).mean().to_numpy()
        mas.append(ma)
    mas_arr = np.stack(mas)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # 预热期全 NaN 切片为合法空集
        lo = np.nanmin(mas_arr, axis=0)
        hi = np.nanmax(mas_arr, axis=0)
    with np.errstate(invalid="ignore"):
        m = (c > o) & (o < lo) & (c > hi) & ~np.isnan(lo)
    return (m,), (), ()


def _r_tweezer_bottom(o, h, l, c, pc):  # 069 镊子底
    tol = 0.002 * np.maximum(l[:-1], 1e-9)
    eq_low = np.abs(l[1:] - l[:-1]) <= tol
    m = np.zeros(len(o), dtype=bool)
    m[1:] = eq_low
    return (m,), (), ()


def _r_tweezer_top(o, h, l, c, pc):  # 070 镊子顶
    tol = 0.002 * np.maximum(h[:-1], 1e-9)
    eq_high = np.abs(h[1:] - h[:-1]) <= tol
    m = np.zeros(len(o), dtype=bool)
    m[1:] = eq_high
    return (), (m,), ()


def _r_nr7(o, h, l, c, pc):  # 071 NR7/NR4 窄幅整理（中性 setup）
    rng = h - l
    m7 = np.zeros(len(o), dtype=bool)
    for i in range(6, len(o)):
        m7[i] = rng[i] <= np.min(rng[i - 6 : i + 1])
    return (), (), (m7,)


def _r_key_reversal(o, h, l, c, pc):  # 072 关键反转日（外包反转）
    prev_h = np.concatenate(([np.nan], h[:-1]))
    prev_l = np.concatenate(([np.nan], l[:-1]))
    bear = np.zeros(len(o), dtype=bool)
    bull = np.zeros(len(o), dtype=bool)
    with np.errstate(invalid="ignore"):
        bear[1:] = (h[1:] > prev_h[1:]) & (c[1:] < pc[1:]) & (c[1:] < o[1:])
        bull[1:] = (l[1:] < prev_l[1:]) & (c[1:] > pc[1:]) & (c[1:] > o[1:])
    return (bull,), (bear,), ()


def _r_wrb(o, h, l, c, pc):  # 073 宽幅推进K线（range>=2×前5日均range，按阴阳定向）
    rng = h - l
    avg = pd.Series(rng).rolling(5).mean().shift(1).to_numpy()
    wide = (rng >= 2 * avg) & ~np.isnan(avg)
    bull = wide & (c > o)
    bear = wide & (c < o)
    return (bull,), (bear,), ()


def _r_oops(o, h, l, c, pc):  # 074 Oops 跳空反向陷阱（Larry Williams）
    prev_l = np.concatenate(([np.nan], l[:-1]))
    prev_h = np.concatenate(([np.nan], h[:-1]))
    bull = np.zeros(len(o), dtype=bool)
    bear = np.zeros(len(o), dtype=bool)
    with np.errstate(invalid="ignore"):
        bull[1:] = (o[1:] < prev_l[1:]) & (c[1:] > prev_l[1:])
        bear[1:] = (o[1:] > prev_h[1:]) & (c[1:] < prev_h[1:])
    return (bull,), (bear,), ()


def _r_sanku(o, h, l, c, pc):  # 075 三空（酒田五法：三连空=力竭反转）
    gap_up = np.zeros(len(o), dtype=bool)
    gap_dn = np.zeros(len(o), dtype=bool)
    gap_up[1:] = o[1:] > h[:-1]
    gap_dn[1:] = o[1:] < l[:-1]
    up3 = np.zeros(len(o), dtype=bool)
    dn3 = np.zeros(len(o), dtype=bool)
    up3[2:] = gap_up[2:] & gap_up[1:-1] & gap_up[:-2]
    dn3[2:] = gap_dn[2:] & gap_dn[1:-1] & gap_dn[:-2]
    # 三连上跳空=上极力竭（看跌）；三连下跳空=下极力竭（看涨）
    return (dn3,), (up3,), ()


def _r_tower_top(o, h, l, c, pc):  # 076 塔形顶（MVP 近似：高位长上影+两连跌）
    body = np.abs(c - o)
    rng = h - l
    upper = h - np.maximum(o, c)
    tall_shadow = (rng > 0) & (upper >= 2 * body) & (body > 0)
    falling = (c < o) | (c < np.roll(c, 1))
    m = np.zeros(len(o), dtype=bool)
    m[:-2] = tall_shadow[:-2] & falling[1:-1] & falling[2:]
    return (), (m,), ()


def _r_tower_bottom(o, h, l, c, pc):  # 077 塔形底（MVP 近似：低位长下影+两连涨）
    body = np.abs(c - o)
    rng = h - l
    lower = np.minimum(o, c) - l
    tall_shadow = (rng > 0) & (lower >= 2 * body) & (body > 0)
    rising = (c > o) | (c > np.roll(c, 1))
    m = np.zeros(len(o), dtype=bool)
    m[:-2] = tall_shadow[:-2] & rising[1:-1] & rising[2:]
    return (m,), (), ()


def _rolling_extreme(arr: np.ndarray, n: int, mode: str) -> np.ndarray:
    """滚动 n 窗极值（含当前 bar），前 n-1 位 NaN。"""
    out = np.full(len(arr), np.nan)
    if len(arr) >= n:
        win = np.lib.stride_tricks.sliding_window_view(arr, n)
        out[n - 1 :] = win.max(axis=1) if mode == "max" else win.min(axis=1)
    return out


def _r_inside_days(o, h, l, c, pc):  # 078 内包日（高低点皆包络前一日，中性 setup）
    ph = np.roll(h, 1)
    pl = np.roll(l, 1)
    inside = (h < ph) & (l > pl)
    inside[0] = False
    return (), (), (inside,)


def _r_weekly_reversal(o, h, l, c, pc):  # 079 周线反转（创 12 窗新极端但反向收盘）
    hh = _rolling_extreme(h, 12, "max")
    ll = _rolling_extreme(l, 12, "min")
    with np.errstate(invalid="ignore"):
        new_high = h >= hh
        new_low = l <= ll
    bear = new_high & (c < o)  # 创新高收阴=顶反转
    bull = new_low & (c > o)  # 创新低收阳=底反转
    bear &= ~np.isnan(hh)
    bull &= ~np.isnan(ll)
    return (bull,), (bear,), ()


def _r_open_close_reversal(o, h, l, c, pc):  # 080 开收反转（两 bar：首 bar 单边推进、次 bar 反向且收穿首 bar 收盘）
    n = len(o)
    rng = h - l
    valid = (rng > 0) & ~np.isnan(c)
    open_near_high = (h - o) <= 0.25 * rng
    open_near_low = (o - l) <= 0.25 * rng
    close_near_low = (c - l) <= 0.25 * rng
    close_near_high = (h - c) <= 0.25 * rng
    b1_black = (open_near_high & close_near_low & (c < o)) & valid  # 长阴（开近高收近低）
    b2_white = (open_near_low & close_near_high & (c > o)) & valid  # 长阳（开近低收近高）
    b1_white = (open_near_low & close_near_high & (c > o)) & valid
    b2_black = (open_near_high & close_near_low & (c < o)) & valid
    bull = np.zeros(n, dtype=bool)
    bear = np.zeros(n, dtype=bool)
    bull[1:] = b1_black[:-1] & b2_white[1:] & (c[1:] > c[:-1])  # OCRU
    bear[1:] = b1_white[:-1] & b2_black[1:] & (c[1:] < c[:-1])  # OCRD
    return (bull,), (bear,), ()


def _r_hook_reversal(o, h, l, c, pc):  # 081 钩形反转（开破前日极值、收穿前日收盘=钩回）
    ph = np.roll(h, 1)
    pl = np.roll(l, 1)
    pcc = np.roll(c, 1)
    bear = (o > ph) & (c < pcc)  # HRD：跳空开在昨高之上、收在昨收之下
    bull = (o < pl) & (c > pcc)  # HRU：跳空开在昨低之下、收在昨收之上
    bear[0] = False
    bull[0] = False
    return (bull,), (bear,), ()


def _r_pivot_point_reversal(o, h, l, c, pc):  # 082 枢轴点反转（创昨高新高但收穿昨低/镜像，不要求外包）
    ph = np.roll(h, 1)
    pl = np.roll(l, 1)
    bear = (h > ph) & (c < pl)  # PPRD
    bull = (l < pl) & (c > ph)  # PPRU
    bear[0] = False
    bull[0] = False
    return (bull,), (bear,), ()


def _r_shark32(o, h, l, c, pc):  # 083 鲨鱼32（三连跌+Setup bar 开收近低；次日收盘破 Setup 高=触发向上）
    n = len(o)
    rng = h - l
    valid = rng > 0
    near_low = (((o - l) <= 0.25 * rng) & ((c - l) <= 0.25 * rng)) & valid
    bull = np.zeros(n, dtype=bool)
    s = np.arange(3, n - 1)  # setup bar 下标
    if len(s):
        dec3 = (c[s - 3] > c[s - 2]) & (c[s - 2] > c[s - 1])  # 前三根连跌
        bull[s + 1] = dec3 & near_low[s] & (c[s + 1] > h[s])  # 触发：收盘破 Setup 高
    return (bull,), (), ()


_EXTRA_RULES: dict[str, tuple[Callable, str]] = {
    "短线": (_r_short_line, "PAT-CANDLE-062"),
    "一字涨停板": (_r_limit_up_flat, "PAT-CANDLE-063"),
    "一字跌停板": (_r_limit_down_flat, "PAT-CANDLE-064"),
    "搓揉线": (_r_cuoxian, "PAT-CANDLE-065"),
    "天地板": (_r_tiandi, "PAT-CANDLE-066"),
    "地天板": (_r_ditian, "PAT-CANDLE-067"),
    "一阳穿多线": (_r_one_yang_mas, "PAT-CANDLE-068"),
    "镊子底": (_r_tweezer_bottom, "PAT-CANDLE-069"),
    "镊子顶": (_r_tweezer_top, "PAT-CANDLE-070"),
    "窄幅整理日": (_r_nr7, "PAT-CANDLE-071"),
    "关键反转日": (_r_key_reversal, "PAT-CANDLE-072"),
    "宽幅推进K线": (_r_wrb, "PAT-CANDLE-073"),
    "Oops跳空反向陷阱": (_r_oops, "PAT-CANDLE-074"),
    "三空": (_r_sanku, "PAT-CANDLE-075"),
    "塔形顶": (_r_tower_top, "PAT-CANDLE-076"),
    "塔形底": (_r_tower_bottom, "PAT-CANDLE-077"),
    "内包日": (_r_inside_days, "PAT-CANDLE-078"),
    "周线反转": (_r_weekly_reversal, "PAT-CANDLE-079"),
    "开收反转": (_r_open_close_reversal, "PAT-CANDLE-080"),
    "钩形反转": (_r_hook_reversal, "PAT-CANDLE-081"),
    "枢轴点反转": (_r_pivot_point_reversal, "PAT-CANDLE-082"),
    "鲨鱼32": (_r_shark32, "PAT-CANDLE-083"),
}


def scan_candles(
    symbol: str,
    df: pd.DataFrame,
    *,
    timeframe: str = "day",
    confidence: float = _DEFAULT_CONFIDENCE,
) -> list[dict[str, Any]]:
    """OHLC DataFrame → 蜡烛形态事件行 dict 列表（store.build_event_rows 可直接消费）。

    仅输出已完成 bar 上命中的事件；同 bar 同形态只产一条。
    df 需按时间升序，含 open/high/low/close（升/跌停类规则另用 prev_close，内部推导）。
    """
    missing = [col for col in _REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"缺少必需列: {missing}")
    if df.empty:
        return []
    try:
        import talib
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("talib 不可得（依赖 ta-lib>=0.6）") from exc

    if "trade_date" in df.columns:
        dates = list(pd.to_datetime(df["trade_date"]).dt.date)
    else:
        dates = list(df.index)
    o = df["open"].to_numpy(dtype=np.float64)
    h = df["high"].to_numpy(dtype=np.float64)
    l = df["low"].to_numpy(dtype=np.float64)
    c = df["close"].to_numpy(dtype=np.float64)
    prev_c = np.concatenate(([np.nan], c[:-1]))

    rows: list[dict[str, Any]] = []

    def _emit(pid: str, name: str, idx: int, direction: str) -> None:
        d = dates[idx]
        d_str = d.isoformat() if hasattr(d, "isoformat") else str(d)[:10]
        rows.append(
            {
                "pattern_id": pid,
                "pattern_class": "K线",
                "direction": direction,
                "confidence": float(confidence),
                "timeframe": timeframe,
                "symbol": symbol,
                "anchor_trade_date": d_str,
                "confirmed_at": f"{d_str}T07:00:00+00:00",  # A股 15:00 CST
                "name": name,
                "key_points": [],
                "regime_tag": "",
                "scan_run_id": "",
            }
        )

    # 1) TA-Lib CDL 61
    for fname in _cdl_functions():
        try:
            out = getattr(talib, fname)(o, h, l, c)
        except Exception as exc:  # noqa: BLE001 单函数异常不拖垮整批
            log.warning("CDL %s 失败: %s", fname, exc)
            continue
        for idx in np.nonzero(out)[0]:
            direction = "向上" if out[idx] > 0 else "向下"
            _emit(fname, fname, int(idx), direction)

    # 2) 手写 extras 22（062..077 原有 16 + 078..083 Bulkowski 小形态 6）
    for name, (fn, _pat_id) in _EXTRA_RULES.items():
        bull_groups, bear_groups, neutral_groups = fn(o, h, l, c, prev_c)
        for m, direction in (
            (bull_groups, "向上"),
            (bear_groups, "向下"),
            (neutral_groups, "中性"),
        ):
            for msk in m:
                for idx in np.nonzero(msk)[0]:
                    _emit(f"X-{name}", name, int(idx), direction)

    return rows


__all__ = ["scan_candles", "_cdl_functions", "_EXTRA_RULES"]
