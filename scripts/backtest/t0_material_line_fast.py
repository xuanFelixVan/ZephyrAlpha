# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign/links/L05_t0/T0_MATERIAL_EXAM_CARD_draft.md | §4 成交模型 M0（本件=同语义路径并行核，判据零改动）
# [MODULE] t0_material_line_fast
# create-guard-not-dup: 本件是 t0_material_line 建模循环的路径并行加速核（同语义复刻+批量向量化），非配对判据/成交模型的第二实现——判据真源仍是 cost_trio_exam.build_pairs，M0 语义真源仍是 t0_material_line.run_model_m0（逐标量复刻，对拍钉死）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/t0_material_line.py（M0 语义真源+fills 格式化，import 复用禁重写）；scripts/audit/cost_trio_exam.py（判据真源，经 t0_material_line 间接复用）；numpy(pip)；numba(pip, 可选——缺席自动 numpy reduceat 兜底)
# [CONSUMERS] t0_material_line.run_pipeline（engine="fast" 单点切挂，本件唯一生产消费方）；tests/research/backtest/test_t0_material_line_fast.py；对拍 harness=scripts/backtest/t0_material_line_parity.py
# [STARTUP] library（由 t0_material_line.run_pipeline 延迟导入；独立 bench 走 t0_material_line_parity.py）
# [MATURITY] draft（对拍逐位+单测过绿后方可在生产 pipeline 挂 fast；卡 frozen 前产物仍仅限容量预检/验证）
# [INVARIANTS] M0 语义逐标量复刻：reason 优先级 one_bar→low_bars→zero_price→no_touch→pair 与 legacy if 链一致；买腿=首根 low≤base×(1−grid_bp/1e4)、成交价=min(open,触发价)、卖腿=买后首根 high≥buy_fill×(1+grid_bp/1e4)、成交价=max(open,触发价)、末日强平=末根 close、qty=max(floor(notional/buy_fill/100)×100,100)——float64 标量运算序与 legacy 逐位一致（对拍验收=逐位相等非 1e-9 容差）；resample=日内 bar 序数分桶（桶时刻=桶内末根、open=桶首根、close=桶末根、high/low=桶极值），period=1 恒等直通；volume 聚合不入 M0 不入对拍面（M0 零消费 volume）；numba 缺席=numpy reduceat 兜底（同读数，两路径均对拍）；输入契约=bar 已按 (symbol,trade_date,trade_time) 去重排序（load_bars 产物）、价格非 NaN 非≤0（zero_price 契约）；查库只读零写库零落盘（产物经调用方 write_outputs）；回滚口径=t0_material_line 侧 env ZEPHYR_T0_MATERIAL_ENGINE=legacy 或 revert 切挂 diff（单点）
# [MODIFY-GUARD] M0 参数语义（grid_bp/period 桶规则/min_bars/notional）与 reason 优先级属考试卡预注册面，本件禁改动语义只许改实现；改动须先过对拍 harness 逐位再合入
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol-day 输入=返回空产物（调用方 run_pipeline_fast 负责空库显式报错）；numba 编译失败=自动降级 numpy 兜底并在返回 stats 标注 engine_kernel；非法 period（非正整数）=ValueError
# [TESTS] tests/research/backtest/test_t0_material_line_fast.py（构造数据纯函数面：逐位对拍 legacy run_model_m0/reason 优先级/末日强平/除零挡/numba 与 numpy 兜底同读数/确定性；禁真全量跑）
# [TTL] task_bound
"""t0_material_line_fast — 做T 材料线路径并行加速核（st-mx07-W1，裁定#489⑤）。

背景：material_precapacity_report §三 实测外推全市场 5 周期建模 ≈21.4h（legacy 逐
symbol-day 纯 Python 双循环 ×5 周期），加取数 ≈23.3h。本件把"每 symbol-day 独立"
的路径级并行暴露出来：
  1. resample：numpy reduceat 扁平分桶（period=1 恒等），替代 pandas iloc 逐桶切片；
  2. M0 扫描：numba prange 逐路径并行核（标量运算序与 legacy 逐位一致），
     numba 缺席时 numpy reduceat 首索引法兜底（min/max/索引均为精确整型/浮点操作，
     两实现读数相同）；
  3. fills 组装：仅 pair 日走 t0_material_line.fills_to_cost_trio_format（格式零重写），
     配对仍由 cost_trio_exam.build_pairs 唯一真源消费。

对拍锚点：scripts/backtest/t0_material_line_parity.py（legacy 循环 vs 本件，同输入
逐位比对 fills/pairs/reason_counts + 耗时对比，索引注入法）。

用法（库面）：
  from t0_material_line_fast import build_corpus_fast, run_pipeline_fast
  frames, stats = run_pipeline_fast(conn, symbols, start, end, periods, grid_bp, notional, run_id)

"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

try:  # numba 可选依赖：缺席自动走 numpy 兜底（同读数）
    from numba import njit, prange

    NUMBA_AVAILABLE = True
except ImportError:  # pragma: no cover - 环境无 numba 时
    NUMBA_AVAILABLE = False

    def njit(*args, **kwargs):  # type: ignore[misc]  # 兜底占位：装饰器退化为恒等
        def wrap(fn):
            return fn

        return wrap if not args else args[0]

    def prange(n):  # type: ignore[misc]
        return range(n)


# reason 代码（优先级=legacy if 链顺序：one_bar→low_bars→zero_price→no_touch→pair）
REASON_PAIR = 0
REASON_NO_TOUCH = 1
REASON_LOW_BARS = 2
REASON_ZERO_PRICE = 3
REASON_ONE_BAR = 4
REASON_NAMES = {
    REASON_PAIR: "pair",
    REASON_NO_TOUCH: "no_touch",
    REASON_LOW_BARS: "low_bars",
    REASON_ZERO_PRICE: "zero_price",
    REASON_ONE_BAR: "one_bar",
}
# BIG 哨兵：numpy 兜底首索引法的"未命中"（=n，超出任何合法索引）
_BIG = -1


def segment_days(bars: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """把全局有序 bar 分割成 symbol-day 段。

    输入契约：bars 已按 (symbol, trade_date, trade_time) 排序（load_bars 产物）。
    返回 (day_symbols, day_dates, day_start, day_len)，均与 day 数 D 对齐。
    """
    n = len(bars)
    sym = bars["symbol"].to_numpy()
    dates = bars["trade_date"].to_numpy()
    if n == 0:
        return sym, dates, np.empty(0, dtype=np.int64), np.empty(0, dtype=np.int64)
    new_day = np.empty(n, dtype=bool)
    new_day[0] = True
    if n > 1:
        np.logical_or(sym[1:] != sym[:-1], dates[1:] != dates[:-1], out=new_day[1:])
    day_start = np.flatnonzero(new_day).astype(np.int64)
    day_len = np.diff(np.append(day_start, n)).astype(np.int64)
    return sym[day_start], dates[day_start], day_start, day_len


def extract_base_arrays(bars: pd.DataFrame) -> dict[str, np.ndarray]:
    """基础列一次性抽取（跨周期复用，免碎片帧反复 to_numpy 合并复制）。"""
    return {
        "open": bars["open"].to_numpy(dtype=np.float64),
        "high": bars["high"].to_numpy(dtype=np.float64),
        "low": bars["low"].to_numpy(dtype=np.float64),
        "close": bars["close"].to_numpy(dtype=np.float64),
        "volume": bars["volume"].to_numpy(dtype=np.float64),
        "time": bars["trade_time"].to_numpy(),
        "n": len(bars),
    }


def resample_arrays(
    bars: pd.DataFrame | dict[str, np.ndarray], day_start: np.ndarray, day_len: np.ndarray, period: int
) -> dict[str, np.ndarray]:
    """日内序数分桶重采样（扁平 reduceat 版，与 t0_material_line.resample_period 同口径）。

    桶时刻=桶内末根 trade_time；open=桶首根、close=桶末根、high/low=桶极值、volume=桶和。
    period=1 恒等直通（与 legacy reset_index(drop=True) 同构）。
    bars 可传 DataFrame（内部抽取，测试便利面）或 extract_base_arrays 产物 dict
    （生产面：多周期共享一次抽取）。
    返回 dict(r_open/r_high/r_low/r_close/r_volume/r_time, res_day_start, res_day_len)。
    """
    if period <= 0:
        raise ValueError(f"period 须为正整数，得 {period}")
    if isinstance(bars, dict):
        cols = bars
    else:
        cols = extract_base_arrays(bars)
    opens = cols["open"]
    highs = cols["high"]
    lows = cols["low"]
    closes = cols["close"]
    volumes = cols["volume"]
    times = cols["time"]
    n = int(cols["n"])
    if period == 1:
        return {
            "r_open": opens,
            "r_high": highs,
            "r_low": lows,
            "r_close": closes,
            "r_volume": volumes,
            "r_time": times,
            "res_day_start": day_start.copy(),
            "res_day_len": day_len.copy(),
        }
    n_bkt = (day_len + period - 1) // period  # 每日桶数=ceil(len/period)
    day_id = np.repeat(np.arange(len(day_len)), day_len)
    bkt_off = np.concatenate(([0], np.cumsum(n_bkt)[:-1])).astype(np.int64)
    intra = np.arange(n, dtype=np.int64) - day_start[day_id]
    bucket_id = bkt_off[day_id] + intra // period
    boundary = np.flatnonzero(bucket_id[1:] != bucket_id[:-1]) + 1
    starts = np.concatenate(([0], boundary)).astype(np.int64)
    ends = np.append(starts[1:], n) - 1
    return {
        "r_open": opens[starts],
        "r_high": np.maximum.reduceat(highs, starts),
        "r_low": np.minimum.reduceat(lows, starts),
        "r_close": closes[ends],
        "r_volume": np.add.reduceat(volumes, starts),
        "r_time": times[ends],
        "res_day_start": bkt_off,
        "res_day_len": n_bkt,
    }


if NUMBA_AVAILABLE:

    @njit(parallel=True, cache=True)
    def _m0_scan_numba(  # noqa: PLR0913 - 核签名扁平化是 numba 约束
        r_open: np.ndarray,
        r_high: np.ndarray,
        r_low: np.ndarray,
        r_close: np.ndarray,
        day_start: np.ndarray,
        day_len: np.ndarray,
        grid_bp: float,
        min_bars: int,
        reason: np.ndarray,
        buy_i: np.ndarray,
        buy_fill: np.ndarray,
        sell_i: np.ndarray,
        sell_fill: np.ndarray,
    ) -> None:
        """逐路径（symbol-day）M0 扫描：标量运算序与 t0_material_line.run_model_m0 逐位一致。"""
        n_days = len(day_start)
        for d in prange(n_days):
            s = day_start[d]
            ln = day_len[d]
            e = s + ln
            if ln < 2:
                reason[d] = 4  # one_bar（优先级第一位，与 legacy 一致）
                buy_i[d] = 0
                buy_fill[d] = 0.0
                sell_i[d] = 0
                sell_fill[d] = 0.0
                continue
            if ln < min_bars:
                reason[d] = 2  # low_bars
                buy_i[d] = 0
                buy_fill[d] = 0.0
                sell_i[d] = 0
                sell_fill[d] = 0.0
                continue
            zero = False
            for i in range(s, e):
                if r_low[i] <= 0.0 or r_open[i] <= 0.0:
                    zero = True
                    break
            if zero:
                reason[d] = 3  # zero_price（除零契约）
                buy_i[d] = 0
                buy_fill[d] = 0.0
                sell_i[d] = 0
                sell_fill[d] = 0.0
                continue
            base = r_open[s]
            buy_level = base * (1.0 - grid_bp / 1e4)
            bi = -1
            bf = 0.0
            for i in range(s, e):
                if r_low[i] <= buy_level:
                    bi = i
                    bf = min(r_open[i], buy_level)  # 挂单限价机制
                    break
            if bi < 0:
                reason[d] = 1  # no_touch
                buy_i[d] = 0
                buy_fill[d] = 0.0
                sell_i[d] = 0
                sell_fill[d] = 0.0
                continue
            sell_level = bf * (1.0 + grid_bp / 1e4)
            si = -1
            sf = 0.0
            for j in range(bi + 1, e):
                if r_high[j] >= sell_level:
                    si = j
                    sf = max(r_open[j], sell_level)
                    break
            if si < 0:
                si = e - 1
                sf = r_close[si]  # 收盘强平（同日两腿仍在）
            reason[d] = 0  # pair
            buy_i[d] = bi
            buy_fill[d] = bf
            sell_i[d] = si
            sell_fill[d] = sf


def _m0_scan_numpy(
    r_open: np.ndarray,
    r_high: np.ndarray,
    r_low: np.ndarray,
    r_close: np.ndarray,
    day_start: np.ndarray,
    day_len: np.ndarray,
    grid_bp: float,
    min_bars: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """numba 缺席兜底：reduceat 首索引法（min/max/比较均为精确操作，读数与 numba 核相同）。"""
    n_days = len(day_start)
    n = len(r_open)
    reason = np.zeros(n_days, dtype=np.int8)
    reason[day_len < 2] = REASON_ONE_BAR
    reason[(day_len >= 2) & (day_len < min_bars)] = REASON_LOW_BARS
    active = reason == REASON_PAIR
    zp_day = np.maximum.reduceat(((r_low <= 0.0) | (r_open <= 0.0)).astype(np.int8), day_start) > 0
    reason[active & zp_day] = REASON_ZERO_PRICE
    active = reason == REASON_PAIR

    base = r_open[day_start]
    buy_level = base * (1.0 - grid_bp / 1e4)
    lvl_per_bar = np.repeat(buy_level, day_len)
    act_per_bar = np.repeat(active, day_len)
    ar = np.arange(n, dtype=np.int64)
    cand_buy = np.where((r_low <= lvl_per_bar) & act_per_bar, ar, n)
    bi = np.minimum.reduceat(cand_buy, day_start)  # 未命中=n
    has_buy = (bi < n) & active
    bix = np.minimum(bi, n - 1)
    bf = np.minimum(r_open[bix], buy_level)

    sell_level = bf * (1.0 + grid_bp / 1e4)
    slv_per_bar = np.repeat(sell_level, day_len)
    day_end = np.append(day_start[1:], n)
    de_per_bar = np.repeat(day_end, day_len)
    bix_per_bar = np.repeat(bix, day_len)
    hb_per_bar = np.repeat(has_buy, day_len)
    cand_sell = np.where((r_high >= slv_per_bar) & (ar > bix_per_bar) & (ar < de_per_bar) & hb_per_bar, ar, n)
    si = np.minimum.reduceat(cand_sell, day_start)
    day_sell = (si < n) & has_buy
    six = np.where(day_sell, si, day_end - 1)
    sf_touch = np.maximum(r_open[np.minimum(si, n - 1)], sell_level)
    sf = np.where(day_sell, sf_touch, r_close[np.minimum(day_end - 1, n - 1)])  # 收盘强平
    # reason 终局：有买即 pair（末日强平仍是 pair，legacy 语义）；active 但无买=no_touch
    reason[active & ~has_buy] = REASON_NO_TOUCH
    buy_i = np.where(has_buy, bix, 0).astype(np.int64)
    buy_fill = np.where(has_buy, bf, 0.0)
    sell_i_arr = np.where(has_buy, six, 0).astype(np.int64)  # 非 pair 日=0（与 numba 核一致）
    sell_fill = np.where(has_buy, sf, 0.0)
    return reason, buy_i, buy_fill, sell_i_arr, sell_fill


def m0_scan(
    r_open: np.ndarray,
    r_high: np.ndarray,
    r_low: np.ndarray,
    r_close: np.ndarray,
    day_start: np.ndarray,
    day_len: np.ndarray,
    grid_bp: float,
    min_bars: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """M0 扫描统一入口：numba 并行核优先，缺席/编译失败降级 numpy 兜底。

    返回 (reason_codes, buy_i, buy_fill, sell_i, sell_fill, kernel)。
    """
    n_days = len(day_start)
    if NUMBA_AVAILABLE:
        try:
            reason = np.empty(n_days, dtype=np.int8)
            buy_i = np.empty(n_days, dtype=np.int64)
            buy_fill = np.empty(n_days, dtype=np.float64)
            sell_i = np.empty(n_days, dtype=np.int64)
            sell_fill = np.empty(n_days, dtype=np.float64)
            _m0_scan_numba(
                r_open,
                r_high,
                r_low,
                r_close,
                day_start,
                day_len,
                float(grid_bp),
                int(min_bars),
                reason,
                buy_i,
                buy_fill,
                sell_i,
                sell_fill,
            )
            return reason, buy_i, buy_fill, sell_i, sell_fill, "numba_prange"
        except Exception:  # noqa: BLE001, S110 - 编译失败降级 numpy 兜底（numba 环境差异免疫，禁静默=stats 标注降级）
            pass
    reason, buy_i, buy_fill, sell_i, sell_fill = _m0_scan_numpy(
        r_open, r_high, r_low, r_close, day_start, day_len, grid_bp, min_bars
    )
    return reason, buy_i, buy_fill, sell_i, sell_fill, "numpy_reduceat"


def normalize_prices_float64(bars: pd.DataFrame) -> pd.DataFrame:
    """价格/量列 float64 规范化（本核输入契约的唯一语义缝，见 INVARIANTS）。

    CH Decimal 列经此统一为 float64：legacy M0 的 fill 价格本就 float() 转换
    （fills 算术逐位同源），仅"扫描比较"在恰好触档 ±1ulp 边界存在 Decimal 精确
    比较语义差异（实测翻转率 1/216 日 ≈0.46%，parity harness 披露段留档）。
    实现注记：整帧构造（非逐列赋值）——逐列赋值产生碎片帧，后续 to_numpy 反复
    触发整帧合并复制（实测 4.6M 行 ~6s/次），是首版 resample 33s 的元凶。
    """
    data: dict[str, object] = {}
    for c in bars.columns:
        col = bars[c]
        if c in ("open", "high", "low", "close", "volume"):
            if not pd.api.types.is_float_dtype(col) or str(col.dtype) != "float64":
                col = col.astype("float64")
        data[c] = col
    return pd.DataFrame(data, index=bars.index)


def build_corpus_fast(
    bars: pd.DataFrame,
    periods: list[int],
    grid_bp: float,
    notional: float,
    run_id: str,
    min_bars_by_period: dict[int, int],
) -> tuple[dict[str, list[dict]], dict[str, dict[str, int]], int, dict]:
    """材料线建模循环的并行版（替代 run_pipeline 内层逐 symbol-day Python 循环）。

    输入契约：bars=load_bars 产物（已去重、全局按 (symbol,trade_date,trade_time) 排序），
    价格/量列经 normalize_prices_float64 规范化（Decimal 边界语义缝，见 INVARIANTS）。
    返回 (fills_by_period, reason_counts_by_period, n_days, engine_stats)。
    fills_by_period[label] 与 legacy 循环产出逐位一致（同 float64 规范化输入），
    直接喂 build_pairs。
    """
    t0 = time.perf_counter()
    bars = normalize_prices_float64(bars)
    day_syms, day_dates, day_start, day_len = segment_days(bars)
    n_days = len(day_start)
    kernels: dict[str, str] = {}
    fills_by_period: dict[str, list[dict]] = {}
    reason_counts_by_period: dict[str, dict[str, int]] = {}

    if n_days:
        import t0_material_line as t0m  # 延迟导入防环：M0 语义真源+fills 格式化复用

        cols = extract_base_arrays(bars)  # 一次抽取，多周期共享
        for period in periods:
            min_bars = int(min_bars_by_period[period])
            arrs = resample_arrays(cols, day_start, day_len, period)
            reason, buy_i, buy_fill, sell_i, sell_fill, kernel = m0_scan(
                arrs["r_open"],
                arrs["r_high"],
                arrs["r_low"],
                arrs["r_close"],
                arrs["res_day_start"],
                arrs["res_day_len"],
                grid_bp,
                min_bars,
            )
            kernels[f"{period}min"] = kernel
            ts = arrs["r_time"]
            pair_days = np.flatnonzero(reason == REASON_PAIR)
            qty_f = np.floor(notional / buy_fill[pair_days] / 100.0) * 100.0
            qty_arr = np.maximum(qty_f, 100.0).astype(np.int64)
            fills_all: list[dict] = []
            for row, d in enumerate(pair_days):
                fills = {
                    "buy_ts": ts[buy_i[d]],
                    "buy_price": float(buy_fill[d]),
                    "sell_ts": ts[sell_i[d]],
                    "sell_price": float(sell_fill[d]),
                    "qty": int(qty_arr[row]),
                }
                fills_all.extend(t0m.fills_to_cost_trio_format(str(day_syms[d]), str(day_dates[d]), fills, run_id))
            fills_by_period[f"{period}min"] = fills_all
            codes, counts = np.unique(reason, return_counts=True)
            reason_counts_by_period[f"{period}min"] = {
                REASON_NAMES[int(c)]: int(v) for c, v in zip(codes, counts, strict=True)
            }
    engine_stats = {
        "engine": "fast",
        "kernels": kernels,
        "numba_available": NUMBA_AVAILABLE,
        "model_seconds": round(time.perf_counter() - t0, 3),
    }
    return fills_by_period, reason_counts_by_period, n_days, engine_stats


def run_pipeline_fast(
    conn,
    symbols: list[str],
    start: str,
    end: str,
    periods: list[int],
    grid_bp: float,
    notional: float,
    run_id: str,
    batch_symbols: int = 100,
) -> tuple[dict[str, pd.DataFrame], dict]:
    """与 t0_material_line.run_pipeline 同签名同产出的加速版。

    差异面（语义等价，留档 parity harness）：
    - 建模循环=build_corpus_fast（路径并行核）；
    - 取数按 sorted(set(symbols)) 分批（batch_symbols，默认 100 只/批）——去重键含
      symbol，分批去重与单查询全局去重同值，stats 按批累加；批序=sorted 序，
      与 legacy 全局 ORDER BY 的 fills 顺序一致。
    回滚口径：t0_material_line.run_pipeline engine="legacy"。
    """
    import t0_material_line as t0m  # 延迟导入：判据常量/load_bars 复用

    t0 = time.perf_counter()
    syms = sorted(set(str(s) for s in symbols))
    t_fetch = 0.0
    bars_raw = bars_kept = 0
    fills_by_period: dict[str, list[dict]] = {f"{p}min": [] for p in periods}
    reason_by_period: dict[str, dict[str, int]] = {f"{p}min": {} for p in periods}
    n_symbol_days = 0
    engine_stats: dict = {}
    for i in range(0, len(syms), batch_symbols):
        batch = syms[i : i + batch_symbols]
        ta = time.perf_counter()
        bars, bar_stats = t0m.load_bars(conn, batch, start, end)
        t_fetch += time.perf_counter() - ta
        bars_raw += bar_stats["bars_raw"]
        bars_kept += bar_stats["bars_after_dedup"]
        if bars.empty:
            continue
        fp, rp, n_sd, engine_stats = build_corpus_fast(bars, periods, grid_bp, notional, run_id, t0m.MIN_BARS_BY_PERIOD)
        n_symbol_days += n_sd
        for label in fills_by_period:
            fills_by_period[label].extend(fp.get(label, []))
            for k, v in rp.get(label, {}).items():
                reason_by_period[label][k] = reason_by_period[label].get(k, 0) + v
    if bars_kept == 0:
        raise SystemExit(f"FAIL: 分钟腿 {start}..{end} x {len(syms)} 只零行——禁静默空产物")

    import cost_trio_exam as ct

    stats: dict = {
        "window": {"start": start, "end": end, "closed_book_cutoff": t0m.CLOSED_BOOK_CUTOFF, "closed_book_ok": True},
        "universe": {
            "n_symbols_requested": len(symbols),
            "bars_raw": bars_raw,
            "bars_after_dedup": bars_kept,
            "bars_deduped_away": bars_raw - bars_kept,
            "fetch_batches": (len(syms) + batch_symbols - 1) // batch_symbols,
        },
        "model_m0": {"grid_bp": grid_bp, "notional_cny": notional, "min_bars_by_period": t0m.MIN_BARS_BY_PERIOD},
        "criteria_source": {
            "rt_cost_bp": ct.RT_COST_BP,
            "pair_gate": ct.PAIR_GATE,
            "edge_precondition_bp": ct.EDGE_PRECONDITION_BP,
            "pairing_rule": "cost_trio_exam.build_pairs import 复用（同票同日既买又卖，禁重写）",
        },
        "periods": {},
        "timing_seconds": {"fetch": round(t_fetch, 3)},
        "engine": engine_stats,
    }
    out: dict[str, pd.DataFrame] = {}
    for period in periods:
        label = f"{period}min"
        pairs = ct.build_pairs(fills_by_period[label])
        kept, audit = t0m.apply_material_gates(pairs)
        stats["periods"][label] = {
            "n_symbol_days": n_symbol_days,
            "reason_counts": reason_by_period[label],
            "n_pairs_before_m4": len(pairs),
            "n_pairs": len(kept),
            "material_audit": audit,
            "edge_ge_30bp": sum(1 for p in kept if float(p["gross_bp"]) >= ct.EDGE_PRECONDITION_BP),
            "net_positive": sum(1 for p in kept if float(p["net_bp"]) > 0),
            "model_seconds": engine_stats.get("model_seconds", 0.0),
        }
        out[label] = pd.DataFrame(kept)
    stats["timing_seconds"]["total"] = round(time.perf_counter() - t0, 3)
    return out, stats
