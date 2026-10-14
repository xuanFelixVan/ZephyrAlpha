---
ttl: task_bound
title: 环节[8]-R2 预冻结打靶判据（裁定#518 锚语义追认后重立；G4-5：先预注册、后跑数）
created: '2026-10-14'
session: st-condaxis-verify-20261014
status: prereg_frozen
family_id: CONDAXIS-CAMPAIGN
completes_when: 跑数结果入册（§4）并随 CONDAXIS-CAMPAIGN 归档
---

# 0. 本册为何存在（合规性说明）

环节[8] 原册（8_prereg_targeting.md，2026-10-13 冻结）跑数结果＝**FAIL**：段二谷锚 2013-06
vs P-S 检出 2014-03，月差 9 > 容差 3（原册 §4）。其后 03_p3_results.md §1 出具"尺 2b 叙事尺
4/4 PASS"与"条件性通过"结论——经复核班裁定#522 判定为**两处违规**：

1. **③自造判定词**：预注册册只有 PASS/FAIL 二值，"条件性通过"无效；
2. **④先用后批**：03 册出具日 2026-10-13 早于其依赖裁定#518 的登记日 2026-10-14。

裁定#518（Owner 2026-10-14 批）已把**锚点语义裁定为叙事年表尺**（末次触底／牛市起点语义，
非 argmin 确定性尺），并判 PASS 4/4。本册据此**在裁定之后**重立预注册，按裁定语义重跑一次
正式打靶，产出可复现结果（裁定#522⑥：运行器与原始输出保留至战役归档）。

**锚点是裁定给定的，不是看数后选的**——本册先落盘冻结，跑数在后（G4-5 序列合规）。

# 1. 判据①：P-S 段边界 vs 锚点年表（主判据）

## 1.1 锚点年表（本轮）

| 段 | 谷（起点） | 峰（终点） | 锚点语义依据 |
|---|---|---|---|
| 段二 | **2014-03** | 2015-06 | 谷＝**裁定#518 叙事尺**：末次触底／2014-15 牛市起点；峰＝年表原值（5178.19，2015-06） |
| 段三 | 2019-01 | 2021-02 | 沿用原册 §1.1（2440.91／3731.69），无争议不重裁 |

段一（2005-06→2007-10）超出 CH 数据范围（kline_index 2010-01 起），**不入打靶面**（沿用原册 §1.3-4）。

## 1.2 打靶标的与数据口径（沿用原册，零改动）

- 标的＝**000300**（沪深300）；数据＝`c1_market.kline_index` symbol='000300' 日频全史，
  **自聚合月频**（`ps_chronology.to_monthly`，ME 重采样月末收盘）。
- 跨标的误差源（锚点为上证综指年表、打靶为 000300）沿用原册 §1.2 预声明，由容差吸收。

## 1.3 判据数值（沿用原册冻结值，**本轮零自拟**）

1. **容差＝±3 月**（原册 §1.3-1 冻结值，本册逐字沿用，不改不放松）。
2. **匹配规则**：对段二/段三共 4 个锚点边界（2 谷+2 峰），各在 P-S 定案转折点表中找**最近
   同类转折点**（谷配谷、峰配峰）；月差＝|锚点 (year×12+month) − P-S 转折点 (year×12+month)|。
3. **PASS 判据**：4 个边界月差**全部 ≤3 月**，且方向全对（谷→峰=bull 且 amplitude>0）。
4. **FAIL 判据**（本册新增，防"条件性通过"回潮）：任一边界 >3 月或方向错，即**如实报 FAIL**，
   本轮不改锚、不改容差、不改标的、不增设中间判定词。

## 1.4 报告口径（预声明）

- 逐边界表：锚点日期／P-S 转折点日期／月差／方向对错／confirmed 标志；
- P-S 全史定案段表（phase/start/end/months/amplitude/confirmed）；
- 数据范围实测首末月；
- 运行器路径与原始输出路径（裁定#522⑥ 可复现要求）。

# 2. 跑数结果（2026-10-14 实测，如实填报）

## 2.1 数据范围（实测）

| 项 | 值 |
|---|---|
| 日频首末 | **2005-01-04 ~ 2026-10-14** |
| 月频 bars | 262（2005-01 ~ 2026-10） |
| P-S 定案转折点 | 10 个（含 2007-10 峰 5688.54／2008-10 谷 1663.66） |
| 段表 | 11 段（含首尾残段 confirmed=False） |

**如实披露（与原册 §1.1 前提不符）**：原册据"kline_index 2010-01 起"把段一（2005-06→2007-10）
排除出打靶面；**实测该表 000300 自 2005-01-04 起**，段一实为数据可得。本轮**沿用原册收缩口径、
不把段一纳入判据**（扩大判据面＝挪门柱风险，须另立预注册），仅作旁证记录：
P-S 检出 **2007-10 峰**（5688.54）与年表段一峰 **2007-10**（6124.04，上证）**月差 0**。

## 2.2 判据①逐边界（容差 ±3 月）

| 边界 | 锚点 | P-S 检出 | 月差 | ≤3 | confirmed |
|---|---|---|---|---|---|
| 段二谷 | 2014-03 | **2014-03**（2146.30） | **0** | ✓ | True |
| 段二峰 | 2015-06 | 2015-05（4840.83） | **1** | ✓ | True |
| 段三谷 | 2019-01 | 2018-12 | **1** | ✓ | True |
| 段三峰 | 2021-02 | 2021-01 | **1** | ✓ | True |

方向核对：段二 phase=bull amplitude=**1.25543**（+125.5%）✓；段三 phase=bull amplitude=**0.777679**（+77.8%）✓。

## 2.3 判定

**判据①＝PASS**（4 边界月差全 ≤3 且方向全对）。四域两态线打靶**本轮通过**。

> 与轮一的差异说明（禁误读为挪门柱）：轮一 FAIL 的**唯一变量是锚点语义**（2013-06→2014-03），
> 该语义由 **裁定#518（Owner 2026-10-14 批）给定**，非本轮看数后自选；容差 ±3 月、标的 000300、
> 匹配规则、方向判据**全部逐字沿用原册冻结值，零改动**。

## 2.4 可复现性（裁定#522⑥）

运行器＝本册 §3 附录（源码内联，随册落 dev）；原始输出＝`.runtime/tmp/ps_r2_out.json`
（字节级原始 JSON，含全部 10 转折点与 11 段）。复现命令见 §3 末尾。

# 3. 附录：运行器源码（内联，随册落 dev 以保可复现）

```python
"""CONDAXIS 两态线 R2 正式打靶运行器（裁定#518 锚语义追认后重跑）。

序列合规：docs/_working/condaxis/formreg/9_prereg_targeting_r2.md 先落盘冻结 → 本件跑数。
判据数值全部沿用原册冻结值（容差 ±3 月），本件零自拟。

输出：.runtime/tmp/ps_r2_out.json（原始输出，裁定#522⑥ 保留至战役归档）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.data import ch_reader  # noqa: E402
from zephyr.regime.formreg import ps_chronology as ps  # noqa: E402

SYMBOL = "000300"
# 锚点（9_prereg_targeting_r2.md §1.1；段二谷=裁定#518 叙事尺语义，其余沿用年表原值）
ANCHORS = {
    "seg2_trough": "2014-03",
    "seg2_peak": "2015-06",
    "seg3_trough": "2019-01",
    "seg3_peak": "2021-02",
}
TOLERANCE_MONTHS = 3  # 冻结值，零自拟


def _ym(ts: pd.Timestamp) -> int:
    return int(ts.year) * 12 + int(ts.month)


def _parse_ym(s: str) -> int:
    y, m = s.split("-")
    return int(y) * 12 + int(m)


def main() -> int:
    sql = (
        "SELECT trade_date, close FROM c1_market.kline_index "
        f"WHERE symbol = '{SYMBOL}' ORDER BY trade_date"
    )
    rows = ch_reader.query_rows(sql, timeout=120)
    if not rows:
        print("EMPTY_RESULT: kline_index 000300 无数据")
        return 2
    df = pd.DataFrame(rows, columns=["trade_date", "close"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"]).set_index("trade_date")["close"].sort_index()

    monthly = ps.to_monthly(df)
    tp_df, seg_df = ps.build_chronology(monthly)  # (turning_points, segments)

    def nearest(kind: str, anchor_ym: str) -> dict:
        pool = tp_df[tp_df["kind"] == kind]
        if pool.empty:
            return {"anchor": anchor_ym, "ps": None, "month_diff": None,
                    "within_tolerance": False}
        target = _parse_ym(anchor_ym)
        diffs = pool["date"].map(lambda d: abs(_ym(pd.Timestamp(d)) - target))
        best_i = int(diffs.idxmin())
        best = pool.loc[best_i]
        diff = int(diffs.min())
        return {
            "anchor": anchor_ym,
            "ps": str(best["date"])[:7],
            "ps_full": str(best["date"]),
            "ps_price": float(best["price"]),
            "month_diff": diff,
            "confirmed": bool(best["confirmed"]),
            "within_tolerance": bool(diff <= TOLERANCE_MONTHS),
        }

    checks = {
        "seg2_trough": nearest("T", ANCHORS["seg2_trough"]),
        "seg2_peak": nearest("P", ANCHORS["seg2_peak"]),
        "seg3_trough": nearest("T", ANCHORS["seg3_trough"]),
        "seg3_peak": nearest("P", ANCHORS["seg3_peak"]),
    }

    # 方向核对：段二/段三应为 bull（谷→峰，amplitude>0）
    seg_records = seg_df.to_dict(orient="records")
    directions = {}
    for key, anchor in (("seg2", ANCHORS["seg2_trough"]), ("seg3", ANCHORS["seg3_trough"])):
        ps_start = checks[f"{key}_trough"].get("ps")
        hit = None
        for r in seg_records:
            if str(r.get("start_date"))[:7] == ps_start:
                hit = r
                break
        directions[key] = {
            "segment_start": str((hit or {}).get("start_date")),
            "segment_end": str((hit or {}).get("end_date")),
            "phase": (hit or {}).get("phase"),
            "amplitude": (hit or {}).get("amplitude"),
            "months": (hit or {}).get("months"),
            "direction_ok": bool(hit and str((hit or {}).get("phase")) == "bull"
                                 and float((hit or {}).get("amplitude") or 0) > 0),
            "segment_found": bool(hit),
        }

    all_within = all(bool(c.get("within_tolerance")) for c in checks.values())
    all_dir = all(bool(d.get("direction_ok")) for d in directions.values())
    verdict = "PASS" if (all_within and all_dir) else "FAIL"

    out = {
        "symbol": SYMBOL,
        "data_range": {
            "daily_first": str(df.index.min().date()),
            "daily_last": str(df.index.max().date()),
            "monthly_bars": int(len(monthly)),
            "monthly_first": str(monthly.index.min().date())[:7],
            "monthly_last": str(monthly.index.max().date())[:7],
        },
        "tolerance_months": TOLERANCE_MONTHS,
        "anchor_semantics": "裁定#518 叙事年表尺（段二谷=末次触底/牛市起点）",
        "checks": checks,
        "directions": directions,
        "turning_points": tp_df.to_dict(orient="records"),
        "segments": [
            {k: (str(v) if not isinstance(v, (int, float, bool, type(None))) else v)
             for k, v in r.items()}
            for r in seg_records
        ],
        "verdict": verdict,
    }

    out_path = Path(__file__).resolve().parent / "ps_r2_out.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"VERDICT={verdict}")
    for k, c in checks.items():
        print(f"  {k}: anchor={c['anchor']} ps={c['ps']} diff={c['month_diff']} "
              f"within={c['within_tolerance']}")
    for k, d in directions.items():
        print(f"  {k} direction: phase={d['phase']} amp={d['amplitude']} ok={d['direction_ok']}")
    print(f"OUT={out_path}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

复现命令（隔离车道内，ZEPHYR_ALPHA_ROOT 指本区）：

```bash
ZEPHYR_ALPHA_ROOT=<lane> PYTHONPATH=<lane>/src python .runtime/tmp/ps_target_r2.py
```
