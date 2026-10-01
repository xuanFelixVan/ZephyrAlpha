# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/（4 张预注册规则卡）+ T0_MATERIAL_EXAM_CARD_draft.md §4 骨架
# [MODULE] t0_rule_engine（T0 多周期买卖点规则引擎：L05-C03 执行件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/t0_material_line.py（数据面/周期接口/判据格式，import 复用禁重写）；scripts/audit/cost_trio_exam.py（判据唯一真源）；docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/*.yaml（预注册规则卡，frozen）
# [CONSUMERS] scripts/backtest/t0_state_match_matrix.py（C04 匹配引擎，消费本件 manifest 与 pairs parquet）；L05 后续方法卡考程
# [STARTUP] manual/脱管（python scripts/backtest/t0_rule_engine.py --rule r01 --batch-size 20 --resume --process-priority low；全市场长跑须脱管+low 档（禁 IDLE 优先级托管：实测饿到 0.74 核），process_reaper_keep 已登记）
# [MATURITY] draft（卡驱动信号面；判据零改动，31.2bp/≥30bp/30 对全部 import 复用）
# [INVARIANTS] 规则卡先于跑（预注册制：卡哈希入 manifest，批间校验不一致即 SystemExit）；R01 委托 t0_material_line.run_model_m0 零重实现；配对/成本/材料门全复用 t0_material_line 与 cost_trio_exam；闭卷切点 2025-09-09 硬拦（继承 enforce_closed_book）；bar 按 (symbol,trade_date,trade_time) 去重（ReplacingMergeTree 免疫）；批次=sorted universe 顺序等分（确定性可复跑）；产物=parquet+yaml 禁 summary.json（n_trial_ledger glob 污染教训）；查库只读
# [MODIFY-GUARD] 规则卡参数属预注册面，改卡才改行为；本件不得为过 30 对土规而调参（D-7 禁造料同构）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 分钟腿零行/卡缺失/卡哈希漂移/周期越允许集=显式报错非静默空产物；--end 越闭卷切点=SystemExit；产物写失败=非零退出码
# [TESTS] tests/backtest/test_t0_rule_engine.py（R01 与 M0 同参逐位一致/R02 band 机械复算/R03 运行 VWAP/R04 OR 窗口/批次确定性/闭卷硬拦/FakeConn 端到端；禁真全量跑）
# [TTL] task_bound
"""t0_rule_engine.py — T0 多周期买卖点规则引擎（L05-C03）。

规则 YAML 卡预注册制（17 号文 §三.1：买卖点=指标规则卡预注册禁主观盘感）：
- 卡目录（默认 docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/），
  每规则一卡；本件读卡驱动触发逻辑，卡哈希写入 manifest 并逐批校验（改动=中断）。
- 执行骨架（成交模型 M0 公共部分）零重写：复用 t0_material_line 的 load_bars /
  resample_period / run_model_m0 / fills_to_cost_trio_format / apply_material_gates /
  board_limit_bp / MIN_BARS_BY_PERIOD / enforce_closed_book / list_universe。
- 判据唯一真源=cost_trio_exam（31.2bp / ≥30bp 前置 / 30 对土规，import 复用）。
- R01（固定网格 100bp）与 t0_material_line M0 同参同模型：触发直接委托 run_model_m0。
- R02（波动自适应带）/R03（VWAP 带反转）/R04（ORB）为本件实现的卡驱动触发函数，
  成交价档/强平/数量/材料门语义与骨架逐字一致。
- 批量断点续跑：sorted universe 等分为 --batch-size 只/批（确定性），逐批取数→逐周期→
  逐规则构建，批产物 parquet + 批 manifest yaml（显式路径清单，禁 glob 消费）。
  --resume 跳过已落盘批次。

用法（容量预检抽样）：
  python scripts/backtest/t0_rule_engine.py --sample 20 --rule r01,r02,r03,r04
全市场 v1（脱管+low 调度档，process_reaper_keep 已登记 t0_rule_engine）：
  python scripts/backtest/t0_rule_engine.py --rule r01 --period 1,5,15,30,60 --batch-size 20 --tag r01_grid100bp_full_v1 --resume --process-priority low --mem-cap-mb 6000
调度档纪律（lane_t0 实测）：
  --process-priority low = BELOW_NORMAL CPU（本机实测生效）+ LOW IO 尽力项。本机
  SetProcessInformation 对 IoPriority/MemoryPriority 一律返 winerr 87(ERROR_INVALID_PARAMETER)，
  故 IO 档以回执如实记 failed 不假绿——IO/内存的真实约束由启动侧线程上限 + --batch-size 分批承担。
  不要用外部 IDLE 优先级托管：2026-09-25 微冒烟实测 IDLE 档 745.8s 墙钟只吃 552.4s CPU
  （0.74 核），24h 长跑必饿死。
  --mem-cap-mb 默认 warn-only（只落 t0_memalert_<tag>.log 证据不中断）；--mem-cap-hard 才自退出。
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backtest"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audit"))
import cost_trio_exam as ct  # 判据唯一真源（31.2bp/30bp/30 对）
import t0_material_line as t0m  # 数据面/周期接口/判据格式，import 复用禁重写

DEFAULT_CARDS_DIR = Path("docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards")
ALL_RULES = ("r01", "r02", "r03", "r04")
DEFAULT_BATCH_SIZE = 50


# ------------------------------------------------------- ops-only priority knob
#
# 与判据/口径零耦合：只改本进程的 CPU/IO 调度档，不改任何取数、触发、配对、判据逻辑。
# 立此 knob 的实测病根（2026-09-25 lane_t0 微冒烟，tag lanet0_micro4）：
#   4 只 × 4 规则 × 5 周期 = 20 遍，墙钟 745.8s 只计得 CPU 552.4s ⇒ 有效核 0.74，
#   即外部用 Win32 IDLE 优先级托管时本件长期饿在不足 1 核上，24h 长跑跑不完。
#   BELOW_NORMAL 仍让路给正常优先级的 T1 GPU 搜索车道（PID 3584），而本件是单线程
#   Python，吞吐天花板 1 核，结构上挤不死 T1。
# 注：本仓不存在 process_extrema.set_process_priority（全库 rg 零命中），故在本件内
#     实现等价能力；是否抽象为共享件已记入案卷交治理裁。

_BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
_NORMAL_PRIORITY_CLASS = 0x00000020
_IO_PRIORITY_LOW = 2  # IO_USER_PRIORITY_LEVELS.LOW
_PROCESS_IO_PRIORITY_INFO_CLASS = 2  # PROCESS_INFORMATION_CLASS.ProcessIoPriorityInfoClass


class _IoPriorityInfo(ctypes.Structure):
    _fields_ = [
        ("IoPriority", ctypes.c_uint32),
        ("PagePriority", ctypes.c_uint32),
        ("PagePriorityHistoryValue", ctypes.c_void_p),
    ]


def set_process_priority(level: str) -> dict:
    """设定本进程调度档：level='low' → BELOW_NORMAL CPU + LOW IO；'normal' → 显式回 NORMAL。

    永不抛（运维旋钮不得阻断 24h 长跑），返回逐项落档回执供案卷/manifest 审计。
    """
    receipt: dict = {"requested": level, "applied": "failed"}
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        kernel32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        kernel32.SetPriorityClass.restype = ctypes.c_int
        cls = _BELOW_NORMAL_PRIORITY_CLASS if level == "low" else _NORMAL_PRIORITY_CLASS
        ok = kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), cls)
        receipt["cpu"] = (
            ("below_normal" if cls == _BELOW_NORMAL_PRIORITY_CLASS else "normal")
            if ok
            else (f"SetPriorityClass_failed_winerr={ctypes.get_last_error()}")
        )
    except Exception as e:  # noqa: BLE001
        receipt["cpu"] = f"exc:{e!r}"
    if level != "low":
        receipt["io"] = "skipped(normal)"
        receipt["applied"] = "normal" if str(receipt["cpu"]) == "normal" else "failed"
        return receipt
    try:
        info = _IoPriorityInfo()
        info.IoPriority = _IO_PRIORITY_LOW
        # 只降 IO 档；PagePriority 显式留 NORMAL(5)，不改页面驻留语义（避免本批自 thrash）
        info.PagePriority = 5
        info.PagePriorityHistoryValue = None
        kernel32.SetProcessInformation.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        kernel32.SetProcessInformation.restype = ctypes.c_int
        ok = kernel32.SetProcessInformation(
            kernel32.GetCurrentProcess(),
            _PROCESS_IO_PRIORITY_INFO_CLASS,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        receipt["io"] = "low" if ok else f"SetProcessInformation_failed_winerr={ctypes.get_last_error()}"
    except Exception as e:  # noqa: BLE001
        receipt["io"] = f"exc:{e!r}"
    if receipt.get("cpu") == "below_normal" or receipt.get("io") == "low":
        receipt["applied"] = "below_normal_cpu+low_io" if receipt.get("io") == "low" else "below_normal_cpu"
    return receipt


def start_mem_watchdog(cap_mb: int, marker: Path | None = None, hard: bool = False) -> dict:
    """RSS 采样哨兵：超 cap_mb 只落警不中断（默认），hard=True 才自退出（退出码 3）。

    默认 warn-only 的判据：误报杀 24h 长跑比超卖更糟——本件是单线程 Python，内存由
    --batch-size 决定（实测 4 只峰值 805MB ⇒ 20 只约 4GB，远在 reaper dangerous:mem 10GB
    线内），哨兵只是把越线留成证据供裁量，不当刽子手。
    背景：keep 清单在册会使 reaper 的 dangerous:mem(10GB) 与 orphan_aged(2h) 两条线双双
    免疫，所以内存这件事不能指望外部兜底——但兜底方式是"分批保守+留痕"，不是"临场斩首"。
    只读自身 RSS，零业务耦合。
    """
    receipt: dict = {"cap_mb": cap_mb, "armed": False, "hard": hard, "peak_rss_mb": 0.0}
    if cap_mb <= 0:
        return receipt
    try:
        from ctypes import wintypes

        class _PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (n, ctypes.c_size_t)
                for n in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                )
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        get_pmc = getattr(kernel32, "K32GetProcessMemoryInfo", None)
        if get_pmc is None:  # 老导出在 psapi.dll
            get_pmc = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
        get_pmc.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        get_pmc.restype = wintypes.BOOL

        def rss_mb() -> float:
            pmc = _PMC()
            pmc.cb = ctypes.sizeof(_PMC)
            if not get_pmc(kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
                return -1.0
            return float(pmc.WorkingSetSize) / 1024.0 / 1024.0
    except Exception as e:  # noqa: BLE001
        receipt["error"] = f"watchdog_unavailable:{e!r}"
        return receipt

    def _loop() -> None:
        peak = 0.0
        was_over = False
        hits = 0
        while True:
            r = rss_mb()
            if r > peak:
                peak = r
            receipt["peak_rss_mb"] = round(peak, 1)
            over = r > cap_mb
            if over and not was_over:  # 边沿触发：只在越线瞬间落一次证据，不每 5s 刷盘
                hits += 1
                receipt["hit_rss_mb"] = round(r, 1)
                receipt["hits"] = hits
                if marker is not None:
                    try:
                        with marker.open("a", encoding="utf-8") as fh:
                            fh.write(
                                f"memcap_{'hard' if hard else 'warn'} rss_mb={r:.0f} cap_mb={cap_mb} "
                                f"peak_mb={peak:.0f} hit={hits}\n"
                            )
                    except OSError:
                        pass
                print(
                    f"{'FAIL' if hard else 'WARN'}: RSS {r:.0f}MB 越内存自设线 {cap_mb}MB"
                    + (
                        "——主动退出护并发车道；调小 --batch-size 后 --resume 续跑（已完成批不丢）"
                        if hard
                        else f"（warn-only，不中断；峰值 {peak:.0f}MB，越线第 {hits} 次）"
                    ),
                    flush=True,
                )
            was_over = over
            if hard and over:
                os._exit(3)
            time.sleep(5.0)

    threading.Thread(target=_loop, name="t0-mem-watchdog", daemon=True).start()
    receipt["armed"] = True
    return receipt


# ---------------------------------------------------------------- card loading


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rule_card(cards_dir: Path, rule_id: str) -> dict:
    """读单张规则卡：文件名须以 <rule_id>_ 开头；卡内 rule_id 须一致。"""
    matches = sorted(cards_dir.glob(f"{rule_id}_*.yaml"))
    if len(matches) != 1:
        raise SystemExit(f"FAIL: 规则卡 {rule_id} 在 {cards_dir} 下匹配到 {len(matches)} 件（须恰 1 件）")
    card = yaml.safe_load(matches[0].read_text(encoding="utf-8"))
    if not isinstance(card, dict) or str(card.get("rule_id")) != rule_id:
        raise SystemExit(f"FAIL: 卡 {matches[0].name} 的 rule_id 字段与文件名不符")
    card["_path"] = str(matches[0])
    card["_sha256"] = sha256_file(matches[0])
    return card


# ------------------------------------------------------- trigger implementations
#
# 约定（与 t0_material_line.run_model_m0 骨架逐字一致）：
#   输入 day_bars=单 symbol-day 的周期级 bar（已重采样、按 trade_time 排序）；
#   买腿成交价=min(bar.open, 触发价)、卖腿=max(bar.open, 触发价)（R04 stop 进入语义除外，卡内显式声明）；
#   收盘强平=末根 close；每 symbol-day 至多一次往返；返回 (fills|None, reason)。


def _make_fills(day_bars: pd.DataFrame, buy_i: int, buy_fill: float, sell_i: int, sell_fill: float) -> dict:
    return {
        "buy_ts": day_bars["trade_time"].to_numpy()[buy_i],
        "buy_price": float(buy_fill),
        "sell_ts": day_bars["trade_time"].to_numpy()[sell_i],
        "sell_price": float(sell_fill),
        "qty": max(int(t0m.DEFAULT_NOTIONAL / buy_fill // 100) * 100, 100),
    }


def run_rule_r02(day_bars: pd.DataFrame, prev_day_tr_bp: float | None, card: dict) -> tuple[dict | None, str]:
    """R02 波动率自适应带（卡 params：band_k/band_floor_bp/band_cap_bp；带宽=T-1 真波幅缩放）。"""
    p = card["params"]
    if float((day_bars["low"] <= 0).any()) or float((day_bars["open"] <= 0).any()):
        return None, "zero_price"
    if prev_day_tr_bp is None:
        return None, "no_prev_day"
    band_bp = min(max(p["band_k"] * prev_day_tr_bp, p["band_floor_bp"]), p["band_cap_bp"])
    base = float(day_bars["open"].iloc[0])
    buy_level = base * (1.0 - band_bp / 1e4)
    lows = day_bars["low"].to_numpy()
    opens = day_bars["open"].to_numpy()
    buy_i = buy_fill = None
    for i in range(len(day_bars)):
        if lows[i] <= buy_level:
            buy_i, buy_fill = i, min(float(opens[i]), buy_level)
            break
    if buy_i is None:
        return None, "no_touch"
    sell_level = buy_fill * (1.0 + band_bp / 1e4)
    highs = day_bars["high"].to_numpy()
    for j in range(buy_i + 1, len(day_bars)):
        if highs[j] >= sell_level:
            return _make_fills(day_bars, buy_i, buy_fill, j, max(float(opens[j]), sell_level)), "pair"
    return _make_fills(day_bars, buy_i, buy_fill, len(day_bars) - 1, float(day_bars["close"].to_numpy()[-1])), "pair"


def run_rule_r03(day_bars: pd.DataFrame, card: dict) -> tuple[dict | None, str]:
    """R03 VWAP 带反转（卡 params：vwap_band_bp=50；typical 价；运行 VWAP 零量沿用前值）。"""
    band_bp = float(card["params"]["vwap_band_bp"])
    if len(day_bars) < 2:
        return None, "one_bar"
    if float((day_bars["low"] <= 0).any()) or float((day_bars["open"] <= 0).any()):
        return None, "zero_price"
    highs = day_bars["high"].to_numpy()
    lows = day_bars["low"].to_numpy()
    closes = day_bars["close"].to_numpy()
    volumes = day_bars["volume"].to_numpy(dtype=float)
    opens = day_bars["open"].to_numpy()
    typical = (highs + lows + closes) / 3.0
    cum_pv = 0.0
    cum_v = 0.0
    vwap = None
    buy_i = buy_fill = None
    for i in range(len(day_bars)):
        if volumes[i] > 0:
            cum_pv += float(typical[i]) * volumes[i]
            cum_v += volumes[i]
            vwap = cum_pv / cum_v
            if vwap is not None:
                trig = vwap * (1.0 - band_bp / 1e4)
                if lows[i] <= trig:
                    buy_i, buy_fill = i, min(float(opens[i]), trig)
                    break
    if buy_i is None:
        return None, "no_touch" if vwap is not None else "no_vwap"
    sell_level = buy_fill * (1.0 + band_bp / 1e4)
    for j in range(buy_i + 1, len(day_bars)):
        if highs[j] >= sell_level:
            return _make_fills(day_bars, buy_i, buy_fill, j, max(float(opens[j]), sell_level)), "pair"
    return _make_fills(day_bars, buy_i, buy_fill, len(day_bars) - 1, float(closes[-1])), "pair"


def run_rule_r04(day_bars: pd.DataFrame, card: dict, period: int) -> tuple[dict | None, str]:
    """R04 ORB（卡 params：or_bars_by_period/target_bp=100；stop 进入语义 fill=max(open,or_high)）。"""
    k = int(
        card["params"]["or_bars_by_period"][str(period)]
        if str(period) in card["params"]["or_bars_by_period"]
        else card["params"]["or_bars_by_period"][period]
    )
    target_bp = float(card["params"]["target_bp"])
    if len(day_bars) < 2:
        return None, "one_bar"
    if float((day_bars["low"] <= 0).any()) or float((day_bars["open"] <= 0).any()):
        return None, "zero_price"
    if len(day_bars) <= k:
        return None, "no_or"
    or_bars = day_bars.iloc[:k]
    or_high = float(or_bars["high"].max())
    if or_high <= 0:
        return None, "zero_price"
    opens = day_bars["open"].to_numpy()
    highs = day_bars["high"].to_numpy()
    buy_i = buy_fill = None
    for i in range(k, len(day_bars)):
        if highs[i] >= or_high:
            buy_i, buy_fill = i, max(float(opens[i]), or_high)  # stop 进入：开盘即高于 or_high 按开盘
            break
    if buy_i is None:
        return None, "no_breakout"
    sell_level = buy_fill * (1.0 + target_bp / 1e4)
    for j in range(buy_i + 1, len(day_bars)):
        if highs[j] >= sell_level:
            return _make_fills(day_bars, buy_i, buy_fill, j, max(float(opens[j]), sell_level)), "pair"
    return _make_fills(day_bars, buy_i, buy_fill, len(day_bars) - 1, float(day_bars["close"].to_numpy()[-1])), "pair"


# ---------------------------------------------------------------- batch engine


def plan_batches(symbols: list[str], batch_size: int) -> list[list[str]]:
    """sorted universe 顺序等分（确定性，禁随机）。"""
    syms = sorted(str(s) for s in symbols)
    return [syms[i : i + batch_size] for i in range(0, len(syms), batch_size)]


def batch_out_paths(out_dir: Path, tag: str, bidx: int, rules: list[str], periods: list[int]) -> list[Path]:
    return [out_dir / f"t0_rule_pairs_{tag}_b{bidx:04d}_{r}_{p}min.parquet" for r in rules for p in periods]


def evaluate_day(
    day_bars: pd.DataFrame, period_bars: pd.DataFrame, period: int, rule_id: str, card: dict, prev_ctx: dict
) -> tuple[list[dict], str]:
    """单 symbol-day 单周期单规则 → cost_trio 格式两腿（骨架语义；period_bars=已重采样 bars）。"""
    min_bars = t0m.MIN_BARS_BY_PERIOD[period]
    if len(period_bars) < 2:
        return [], "one_bar"
    if len(period_bars) < min_bars:
        return [], "low_bars"
    if rule_id == "r01":
        fills, reason = t0m.run_model_m0(period_bars, float(card["params"]["grid_bp"]), t0m.DEFAULT_NOTIONAL, min_bars)
    elif rule_id == "r02":
        fills, reason = run_rule_r02(period_bars, prev_ctx.get("tr_bp"), card)
    elif rule_id == "r03":
        fills, reason = run_rule_r03(period_bars, card)
    elif rule_id == "r04":
        fills, reason = run_rule_r04(period_bars, card, period)
    else:
        raise SystemExit(f"FAIL: 未知规则 {rule_id}")
    if fills is None:
        return [], reason
    symbol = str(day_bars["symbol"].iloc[0])
    trade_date = str(day_bars["trade_date"].iloc[0])
    return t0m.fills_to_cost_trio_format(symbol, trade_date, fills, card["run_id_prefix"] + f"-p{period}"), "pair"


def update_prev_ctx(period_bars: pd.DataFrame, prev_ctx: dict) -> None:
    """R02 依赖：记录当日（将成为下一交易日的 T-1）周期级真波幅 bp（输入=已重采样 bars）。"""
    if len(period_bars) == 0:
        return
    last_close = float(period_bars["close"].iloc[-1])
    if last_close <= 0:
        prev_ctx["tr_bp"] = None
        return
    prev_ctx["tr_bp"] = (float(period_bars["high"].max()) - float(period_bars["low"].min())) / last_close * 1e4


def run_batch(
    conn,
    card_map: dict,
    rules: list[str],
    periods: list[int],
    symbols: list[str],
    start: str,
    end: str,
    bidx: int,
    out_dir: Path,
    tag: str,
) -> dict:
    """单批：取数一次 → 逐周期逐规则构建 → 配对 → M-4 门 → 落盘。"""
    bars, bar_stats = t0m.load_bars(conn, symbols, start, end)
    if not bars.empty:
        # CH Decimal→float64（r02/r03 向量算术需要；数值恒等，r01 的 run_model_m0 本就逐位 float()）
        bars[["open", "high", "low", "close", "volume"]] = bars[["open", "high", "low", "close", "volume"]].astype(
            "float64"
        )
    stats: dict = {
        "batch": bidx,
        "n_symbols": len(symbols),
        **bar_stats,
        "rules": {},
    }
    out: dict[tuple[str, int], pd.DataFrame] = {}
    if bars.empty:
        stats["empty"] = True
        return stats
    grouped = list(bars.groupby(["symbol", "trade_date"], sort=True))
    need_prev_ctx = "r02" in rules  # R01/R03/R04 无前置日依赖，免重采样开销
    for period in periods:
        prev_ctx: dict = {}
        prev_symbol = None
        for rule_id in rules:
            card = card_map[rule_id]
            t1 = time.perf_counter()
            fills_all: list[dict] = []
            reason_counts: dict[str, int] = {}
            for (symbol, trade_date), day_bars in grouped:
                if str(symbol) != prev_symbol:  # 换票即清 R02 前置日上下文（票内日序=组序）
                    prev_ctx, prev_symbol = {}, str(symbol)
                day_bars = day_bars.sort_values("trade_time")
                period_bars = t0m.resample_period(day_bars, period)
                fills, reason = evaluate_day(day_bars, period_bars, period, rule_id, card, prev_ctx)
                if need_prev_ctx:
                    update_prev_ctx(period_bars, prev_ctx)
                fills_all.extend(fills)
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
            pairs = ct.build_pairs(fills_all)
            kept, audit = t0m.apply_material_gates(pairs)
            df = pd.DataFrame(kept)
            out[(rule_id, period)] = df
            stats["rules"][f"{rule_id}_{period}min"] = {
                "n_symbol_days": len(grouped),
                "reason_counts": reason_counts,
                "n_pairs_before_m4": len(pairs),
                "n_pairs": len(kept),
                "m4_rejected": audit["m4_rejected_price_limit"],
                "edge_ge_30bp": int((df["gross_bp"] >= ct.EDGE_PRECONDITION_BP).sum()) if len(df) else 0,
                "net_positive": int((df["net_bp"] > 0).sum()) if len(df) else 0,
                "seconds": round(time.perf_counter() - t1, 3),
            }
    for (rule_id, period), df in out.items():
        df.to_parquet(out_dir / f"t0_rule_pairs_{tag}_b{bidx:04d}_{rule_id}_{period}min.parquet", index=False)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="T0 多周期买卖点规则引擎（规则卡预注册驱动，判据 import 复用零改动）")
    ap.add_argument("--cards-dir", default=str(DEFAULT_CARDS_DIR))
    ap.add_argument("--rule", default="r01", help="规则 id，逗号分隔（r01,r02,r03,r04）")
    ap.add_argument("--symbols", default="")
    ap.add_argument("--pool-file", default="")
    ap.add_argument("--sample", type=int, default=0, help="确定性行距抽样 N 只（预检模式）")
    ap.add_argument("--start", default=t0m.RESEARCH_START)
    ap.add_argument("--end", default=t0m.CLOSED_BOOK_CUTOFF)
    ap.add_argument("--period", default="1,5,15,30,60")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    ap.add_argument("--out", default="data/backtest_artifacts/t0_rule_engine")
    ap.add_argument("--tag", required=True, help="产物标签（批产物文件名与 manifest 命名）")
    ap.add_argument("--resume", action="store_true", help="跳过已落盘批次（断点续跑）")
    ap.add_argument(
        "--process-priority",
        choices=("low", "normal"),
        default="low",
        help="长跑调度档：low=BELOW_NORMAL CPU（实测生效）+ 尽力 LOW IO（本机 SetProcessInformation 拒：winerr=87，回执如实记 failed）；normal=显式回 NORMAL",
    )
    ap.add_argument("--mem-cap-mb", type=int, default=0, help="RSS 自设线（MB），0=关；默认只留警不中断")
    ap.add_argument(
        "--mem-cap-hard", action="store_true", help="越 --mem-cap-mb 即自退出（默认 warn-only，误报杀长跑更糟）"
    )
    args = ap.parse_args()

    t0m.enforce_closed_book(args.start, args.end)
    periods = [int(p) for p in str(args.period).split(",")]
    bad = [p for p in periods if p not in t0m.ALLOWED_PERIODS]
    if bad:
        raise SystemExit(f"FAIL: 周期 {bad} 不在允许集 {t0m.ALLOWED_PERIODS}（120min 不做，Owner 明令）")
    rules = [r.strip() for r in str(args.rule).split(",") if r.strip()]
    unknown = [r for r in rules if r not in ALL_RULES]
    if unknown:
        raise SystemExit(f"FAIL: 未知规则 {unknown}（允许集 {ALL_RULES}）")
    cards_dir = Path(args.cards_dir)
    card_map = {r: load_rule_card(cards_dir, r) for r in rules}
    for r in rules:
        card_map[r]["run_id_prefix"] = f"t0rule-{r}-{args.tag}-{args.start}_{args.end}"

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"t0_rule_manifest_{args.tag}.yaml"

    # 运维落档（零口径耦合）：优先级档 + RSS 哨兵，回执入 manifest 供案卷复核
    ops_receipt: dict = {"process_priority": set_process_priority(args.process_priority)}
    if args.mem_cap_mb > 0:
        ops_receipt["mem_watchdog"] = start_mem_watchdog(
            args.mem_cap_mb, out_dir / f"t0_memalert_{args.tag}.log", hard=args.mem_cap_hard
        )
    print(f"OPS: {json.dumps(ops_receipt, ensure_ascii=False)}", flush=True)

    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    if args.sample > 0:
        symbols = t0m.deterministic_sample(t0m.list_universe(conn), args.sample)
    elif args.pool_file:
        symbols = [
            ln.strip()
            for ln in Path(args.pool_file).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = t0m.list_universe(conn)  # 全市场（研究段有数票，与材料线口径一致）

    batches = plan_batches(symbols, max(1, args.batch_size))
    manifest: dict = {
        "tag": args.tag,
        "created_batch_run": len(batches),
        "window": {"start": args.start, "end": args.end, "closed_book_cutoff": t0m.CLOSED_BOOK_CUTOFF},
        "rules": rules,
        "periods": periods,
        "batch_size": args.batch_size,
        "ops": ops_receipt,  # 调度档/RSS 哨兵回执（peak_rss_mb 由哨兵线程就地刷新，逐批落盘可见）
        "cards": {
            r: {"path": card_map[r]["_path"], "sha256": card_map[r]["_sha256"], "status": card_map[r].get("status")}
            for r in rules
        },
        "criteria_source": {
            "rt_cost_bp": ct.RT_COST_BP,
            "edge_precondition_bp": ct.EDGE_PRECONDITION_BP,
            "pair_gate": ct.PAIR_GATE,
            "pairing_rule": "cost_trio_exam.build_pairs import 复用（禁重写）",
        },
        "batches_done": {},
        "pairs_files": {},  # rule -> [显式 parquet 路径清单]（禁 glob 消费）
    }
    if manifest_path.exists():
        prior = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if prior and prior.get("cards") != manifest["cards"]:
            raise SystemExit(f"FAIL: 规则卡哈希与既有 manifest 不一致——卡在跑中被改=作废重开（{manifest_path}）")
        # 断点续跑复用 batches_done 的键是"批序号"，而批序号由 batch_size/窗/规则/周期共同
        # 决定：任一项变了，同一个序号就指向另一批 symbol——静默漏算或重算语料（lane_t0 治本）。
        # 运维档（process_priority/mem_cap）不在此比对：resume 时改调度档是合法救火动作。
        plan_keys = ("batch_size", "rules", "periods", "window")
        drift = [k for k in plan_keys if prior and prior.get(k) != manifest[k]]
        if prior and drift:
            raise SystemExit(
                f"FAIL: 同 tag 复用但切分面已变 {drift}——旧 batches_done 的批序号不再对应同一批 "
                f"symbol（续跑得语料静默漏算/重算）。请换新 --tag 重开，或还原参数。"
            )
        manifest["batches_done"] = prior.get("batches_done", {})
        manifest["pairs_files"] = prior.get("pairs_files", {})

    t0 = time.perf_counter()
    for bidx, batch_syms in enumerate(batches):
        expected = batch_out_paths(out_dir, args.tag, bidx, rules, periods)
        if args.resume and manifest["batches_done"].get(str(bidx)) and all(p.exists() for p in expected):
            continue
        bstats = run_batch(conn, card_map, rules, periods, batch_syms, args.start, args.end, bidx, out_dir, args.tag)
        if bstats.get("empty"):
            raise SystemExit(f"FAIL: 批 {bidx} 分钟腿 {args.start}..{args.end} 零行——禁静默空产物")
        manifest["batches_done"][str(bidx)] = {
            "n_symbols": bstats["n_symbols"],
            "n_pairs_by_rule_period": {k: v["n_pairs"] for k, v in bstats["rules"].items()},
        }
        for r in rules:
            files = manifest["pairs_files"].setdefault(r, [])
            for p in periods:
                rel = f"t0_rule_pairs_{args.tag}_b{bidx:04d}_{r}_{p}min.parquet"
                if (out_dir / rel).exists() and rel not in files:
                    files.append(rel)
        # 逐批落 manifest（断点续跑锚点；yaml 追加写以重读-改-写全量覆盖）
        manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(
            json.dumps(
                {
                    "batch": bidx,
                    "n_symbols": bstats["n_symbols"],
                    "elapsed_s": round(time.perf_counter() - t0, 1),
                    "pairs": {k: v["n_pairs"] for k, v in bstats["rules"].items()},
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    total_by_rp: dict[str, int] = {}
    for binfo in manifest["batches_done"].values():
        for k, v in binfo["n_pairs_by_rule_period"].items():
            total_by_rp[k] = total_by_rp.get(k, 0) + v
    run_stats = {
        "tag": args.tag,
        "window": manifest["window"],
        "universe": {"n_symbols": len(symbols), "n_batches": len(batches), "batch_size": args.batch_size},
        "ops": manifest.get("ops", {}),
        "cards": manifest["cards"],
        "criteria_source": manifest["criteria_source"],
        "n_pairs_by_rule_period": total_by_rp,
        "manifest": str(manifest_path),
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
    }
    (out_dir / f"t0_rule_stats_{args.tag}.yaml").write_text(
        yaml.safe_dump(run_stats, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(yaml.safe_dump(run_stats, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
