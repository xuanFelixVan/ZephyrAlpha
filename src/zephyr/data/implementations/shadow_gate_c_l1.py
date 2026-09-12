#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-DATA-071 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §
# [MODULE] zephyr.data.implementations.shadow_gate_c_l1
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib；zephyr.shared（按需）
# [CONSUMERS] 数据源集成器/币圈影子 MVP 验证批
# [STARTUP] manual
# noqa: m11-perm-manual-legitimate  M11豁免: 币圈影子 MVP 一次性验证脚本（A 类非永久，按需手动触发跑批出报告，无常驻进程）
# [MATURITY] testing
# [INVARIANTS] 影子采集零实盘副作用；免费公开端点无密钥；失败不阻塞主数据链
# [MODIFY-GUARD] 币圈影子 MVP 批（night-gw-2300）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采集失败返回非零退出码/空数据集，不抛入主链
# [TESTS] 无（影子 MVP 验证批随批补）
# [TTL-NOTE] 币圈影子 MVP 验证批：一次性手动跑批，验证完成即归档（勿改回 permanent——PERM-TRIGGER 将拒绝其时间触发模式）
# [TTL] task_bound
"""shadow_gate_c_l1.py — C-L1 影子判定脚本（币圈免费影子 MVP）。

真源：95_crypto_system_blueprint.md（结构）+ 2026-09-11 影子 MVP 会话指令（C-L1 语义）：
  门 1（BTC 趋势门）：BTC 收盘价 vs 200 日均线（1D），above=开 / below=关。
  门 2（山寨季门）：Top-50 USDT 现货 90 日滚动窗内跑赢 BTC 的币占比 >= 75% → 山寨季 on。
  三档组合（影子 MVP 解释口径，Phase 2 Owner 拍板后对齐 TDM/gate_registry）：
    off       = BTC 趋势门关（close < MA200）
    tightened = BTC 门开 + 山寨季门开（过热收紧档）
    normal    = BTC 门开 + 山寨季门未触发
  ready 语义：BTC MA200 滚动窗样本 >= 200 即就绪；山寨季窗有效样本 >= 40/50 币。
  口径注：加密 7×24 无休市，"90 天"与"90 个交易日"等价（每 UTC 日一根 1D K 线）。

输入：data/crypto/kline_daily/<SYMBOL>.csv（crypto_kline_collector.py 输出，confirm=1 已完结行）
输出：data/crypto/shadow/gate_c_l1.csv（镜像 c1_market.crypto_shadow_gate_c_l1 DDL 列，逐日幂等重算）
      --print-tail N 额外打印最近 N 行（首跑样例/报告引用）。

铁律：shadow_only 恒=1，只记录不进决策；禁碰 config/trading_decision_map.yaml 与 okx_broker。
零第三方依赖（csv+math 标准库实现）。
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from typing import Final
from pathlib import Path

KLINE_DIR = Path("data/crypto/kline_daily")
OUT_CSV = Path("data/crypto/shadow/gate_c_l1.csv")

SHADOW_HEADER: Final = [
    "trade_date", "btc_ma200", "btc_above_ma200", "btc_ma200_ready",
    "alt_ratio_90d", "altseason_on", "alt_season_ready",
    "gate_state", "gate_reason", "eval_version", "shadow_only",
]
EVAL_VERSION = "C-L1-shadow-v0.1"
BTC = "BTC-USDT"
MA200_WINDOW = 200
ALT_WINDOW = 90
ALT_RATIO_THRESHOLD = 0.75
ALT_MIN_SAMPLES = 40


def load_kline(csv_path: Path) -> dict[str, float]:
    """读取单币种日线 → {trade_date: close}，仅保留已完结 K 线（confirm=1）。"""
    out: dict[str, float] = {}
    if not csv_path.exists():
        return out
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if int(r.get("confirm", "1")) == 1:
                out[r["trade_date"]] = float(r["close"])
    return out


def all_dates(btc: dict[str, float], alts: dict[str, dict[str, float]]) -> list[str]:
    """全量交易日轴 = BTC 与全部 Alt 的日期并集（7×24 市场，逐日都有行）。"""
    dates = set(btc)
    for d in alts.values():
        dates.update(d)
    return sorted(dates)


def rolling_mean(closes: list[float], window: int) -> float | None:
    """末 window 个样本均值；样本不足返回 None。"""
    if len(closes) < window:
        return None
    seg = closes[-window:]
    return sum(seg) / len(seg)


def _btc_trend_gate(d: str, date_axis: list[str], btc: dict[str, float]) -> tuple[dict, list, float | None, bool | None]:
    """门 1：BTC 200 日趋势门。返回 (行片段, btc_seq, ma200, above)；ma200=None=样本不足。"""
    btc_seq = [btc[x] for x in date_axis if x <= d and x in btc]
    ma200 = rolling_mean(btc_seq, MA200_WINDOW)
    upd = {"btc_ma200_ready": int(ma200 is not None),
           "btc_ma200": "" if ma200 is None else round(ma200, 2)}
    above = None if ma200 is None else btc_seq[-1] > ma200
    return upd, btc_seq, ma200, above


def _btc_not_ready_row() -> dict:
    """MA200 样本不足 → 保守全关行（原 eval_date 早退路径逐键等价）。"""
    return {"btc_above_ma200": 0, "gate_state": "off",
            "gate_reason": "BTC MA200 样本不足(<200)，趋势门默认关（保守）",
            "altseason_on": 0, "alt_season_ready": 0, "alt_ratio_90d": ""}


def _altseason_window(d: str, date_axis: list[str], btc: dict[str, float],
                      alts: dict[str, dict[str, float]], alt_names: list[str]) -> tuple[dict, float | None, int, int]:
    """门 2：山寨季 90 日滚动跑赢占比。返回 (行片段, ratio, beat, valid)；样本不足 ratio=None。"""
    win_dates = [x for x in date_axis if x <= d][-ALT_WINDOW:]
    if len(win_dates) < ALT_WINDOW:
        return ({"altseason_on": 0, "alt_season_ready": 0, "alt_ratio_90d": "",
                 "gate_state": "off",
                 "gate_reason": f"山寨季窗样本不足({len(win_dates)}/{ALT_WINDOW})，默认关（保守）"},
                None, 0, 0)
    btc_ret = btc[win_dates[-1]] / btc[win_dates[0]] - 1.0
    beat = 0
    valid = 0
    for name in alt_names:
        s = alts.get(name) or {}
        a, b = s.get(win_dates[0]), s.get(win_dates[-1])
        if a is None or b is None or a == 0:
            continue  # 上线不足/缺样本 → 剔除有效样本
        valid += 1
        if b / a - 1.0 > btc_ret:
            beat += 1
    ratio = beat / valid if valid else None
    upd = {"alt_ratio_90d": "" if ratio is None else round(ratio, 4),
           "alt_season_ready": int(valid >= ALT_MIN_SAMPLES)}
    return upd, ratio, beat, valid


def _combine(above: bool, btc_seq: list, ma200: float, ratio: float | None,
             beat: int, valid: int, alt_ready: bool) -> dict:
    """三档组合（原 if/elif 链逐分支等价）。"""
    if not above:
        alt_on = int(bool(ratio is not None and alt_ready and ratio >= ALT_RATIO_THRESHOLD))
        return {"altseason_on": alt_on, "gate_state": "off",
                "gate_reason": f"BTC close {btc_seq[-1]:.2f} < MA200 {ma200:.2f}：趋势门关"}
    if ratio is None or not alt_ready:
        return {"altseason_on": 0, "gate_state": "normal",
                "gate_reason": f"BTC 趋势门开；山寨季样本不足(valid={valid})，按 normal 记录"}
    if ratio >= ALT_RATIO_THRESHOLD:
        return {"altseason_on": 1, "gate_state": "tightened",
                "gate_reason": f"BTC 趋势门开；山寨季门开({beat}/{valid}={ratio:.2%}>=75%)：收紧档"}
    return {"altseason_on": 0, "gate_state": "normal",
            "gate_reason": f"BTC 趋势门开；山寨季门未触发({beat}/{valid}={ratio:.2%}<75%)"}


def eval_date(d: str, date_axis: list[str], btc: dict[str, float],
              alts: dict[str, dict[str, float]], alt_names: list[str]) -> dict:
    """单日 C-L1 判定。返回镜像 DDL 的一行。（三门拆分至 helper，行为逐键等价 2026-09-11 复杂度治本）"""
    row = {k: "" for k in SHADOW_HEADER}
    row["trade_date"] = d
    row["eval_version"] = EVAL_VERSION
    row["shadow_only"] = 1

    upd, btc_seq, ma200, above = _btc_trend_gate(d, date_axis, btc)
    row.update(upd)
    if ma200 is None:
        row.update(_btc_not_ready_row())
        return row
    row["btc_above_ma200"] = int(above)

    upd2, ratio, beat, valid = _altseason_window(d, date_axis, btc, alts, alt_names)
    row.update(upd2)
    alt_ready = bool(row["alt_season_ready"])

    row.update(_combine(above, btc_seq, ma200, ratio, beat, valid, alt_ready))
    return row


def run(kline_dir: Path, out_csv: Path, print_tail: int = 0) -> int:
    btc = load_kline(kline_dir / f"{BTC}.csv")
    if not btc:
        print(f"[fail] 缺少 BTC 基准数据: {kline_dir / (BTC + '.csv')}", file=sys.stderr)
        return 1
    alt_names = sorted(p.stem for p in kline_dir.glob("*.csv") if p.stem != BTC)
    alts = {n: load_kline(kline_dir / f"{n}.csv") for n in alt_names}
    date_axis = all_dates(btc, alts)

    rows = [eval_date(d, date_axis, btc, alts, alt_names) for d in date_axis]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SHADOW_HEADER)
        w.writeheader()
        w.writerows(rows)

    n_off = sum(1 for r in rows if r["gate_state"] == "off")
    n_norm = sum(1 for r in rows if r["gate_state"] == "normal")
    n_tight = sum(1 for r in rows if r["gate_state"] == "tightened")
    print(f"shadow gate C-L1: dates={len(rows)} off={n_off} normal={n_norm} "
          f"tightened={n_tight} alts={len(alt_names)} -> {out_csv}")
    if print_tail:
        with out_csv.open("r", encoding="utf-8", newline="") as f:
            tail = list(csv.DictReader(f))[-print_tail:]
        for r in tail:
            print({k: r[k] for k in ("trade_date", "btc_ma200", "btc_above_ma200",
                                     "alt_ratio_90d", "altseason_on", "gate_state", "gate_reason")})
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="C-L1 影子判定（只记录不进决策）")
    ap.add_argument("--kline-dir", default=str(KLINE_DIR))
    ap.add_argument("--out", default=str(OUT_CSV))
    ap.add_argument("--print-tail", type=int, default=0)
    args = ap.parse_args()
    return run(Path(args.kline_dir), Path(args.out), args.print_tail)


if __name__ == "__main__":
    sys.exit(main())
