#!/usr/bin/env python3
# [BLUEPRINT] MOD-SECTOR_LINE | docs/_working/sector_line/sector_layer_skeleton_v0.md | §6 GPU 输入包
# [MODULE] scripts.sector_line.build_gpu_input_pack
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.infrastructure.database_service (CH reader); scripts.sector_line.freeze_baseline (880 链 hash 单一真源); numpy
# [CONSUMERS] A 包 GPU 搜索窗（59h 消费窗，周五 12:00 点火）——产物 data/strategy_intake/grid_gpu_sectorcond_*/
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] CH 只读（DatabaseService role='reader'）；禁消费列 strength/net_inflow_pct/capital_score 零进包（capital_score 活表 100% NULL）；NaN 策略如实不插值；tz-aware now（RULE-SCHEMA-TZ）；幂等可重跑（同参字节级一致）；生成前断言 880 链 hash=710fe244…（freeze_baseline.snapshot 单一真源，禁第二套格式化）
# [MODIFY-GUARD] 产物格式=深度案卷 §6 契约：通道增删/编码变更/切点变更一律新版本目录，禁原地改写
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 880 链漂移→exit 2；自验失败→exit 3；正常→exit 0；永不静默吞异常
# [TESTS] 手工验收=replay_report.md 自验 15/15 记录（shape/dtype/NaN 逐项+3 点 CH 逐位+两连跑 sha256 全等）；自动化测试待 GPU 消费方接入补
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（GPU 输入包建造器，产物 data/strategy_intake/grid_*），非 cron 非 daemon 非常驻服务，会话显式触发
"""build_gpu_input_pack.py — GPU 板块条件矩阵输入包建造器（深度案卷 §6 / 考卡 v2 §2 规格）。

用法: python scripts/sector_line/build_gpu_input_pack.py --out-dir data/strategy_intake/grid_<ts> [--generated-at ISO]
幂等: 同参数两连跑产物 sha256 逐字节一致。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from scripts.sector_line import freeze_baseline  # noqa: E402  冻结驱动单一真源，禁自造第二套 hash 格式化
from zephyr.data.table_registry import get_registry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402

# 表名唯一真源=TableRegistry（#ARCH-CH-024 Phase 5），禁硬编码字符串
_T_K880 = get_registry().table("market_sector_kline_880")
_T_SSTATE = get_registry().table("market_sector_state")

FROZEN_880_CHAIN = "710fe24490fbfe29dcbf90daf5f53904883add86782492bcd6cc6663f440ddd0"
MANIFEST_PATH = REPO / ".runtime/sessions/st-statreplay-20260923/staging/baseline_manifest_v0.json"
HOLDOUT_CUT = date(2025, 9, 9)  # 考卡 v2 §2 / 裁定#407 保密切点
BOARD_MIN = 367  # 可用窗骨架阈值（深度案卷 §2 修正版，板数≥367 的 985 日）
NO_EDGE_TEXT = (
    "v1 S10 判 NO_EDGE：Q5−Q1=−0.2717%，t=−0.571，年度同号率 0.20——本包是同数据的条件化第二次提问，非独立发现"
)
FORBIDDEN_COLS = ("strength", "net_inflow_pct", "capital_score")
SPEC_SOURCES = (
    ".runtime/sessions/st-statreplay-20260923/staging/sector_replay_depth_dossier_v0.md §6",
    "docs/_working/sector_line/statreplay/sector_prereg_exam_cards_v2_frozen.md §2",
    "docs/_working/sector_line/statreplay/replay_report.md",
)

SQL_SKELETON = (
    "SELECT trade_date, uniqExact(sector_code) AS n FROM " + _T_K880 + " FINAL "
    "WHERE period = '1d' GROUP BY trade_date ORDER BY trade_date"
)
SQL_STATE = (
    "SELECT trade_date, sector_code, momentum_pct, rrg_quadrant, watch_score "
    "FROM " + _T_SSTATE + " FINAL WHERE stage = 'close_final' "
    "AND trade_date >= '{first}' AND trade_date <= '{last}' "
    "ORDER BY trade_date, sector_code"
)
SQL_BOARDS = (
    "SELECT DISTINCT sector_code FROM " + _T_K880 + " FINAL WHERE period='1d' "
    "AND trade_date >= '{first}' AND trade_date <= '{last}'"
)
SQL_MOM_NULL = (
    "SELECT countIf(momentum_pct IS NULL) FROM " + _T_SSTATE + " FINAL "
    "WHERE stage='close_final' AND trade_date IN ({day_list})"
)
SQL_RRG_EMPTY = (
    "SELECT countIf(rrg_quadrant = '') FROM " + _T_SSTATE + " FINAL "
    "WHERE stage='close_final' AND trade_date IN ({day_list})"
)
SQL_SPOT = (
    "SELECT momentum_pct, rrg_quadrant, watch_score FROM " + _T_SSTATE + " FINAL "
    "WHERE stage='close_final' AND trade_date='{dk}' AND sector_code='{sc}'"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="build_gpu_input_pack.py")
    ts = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d-%H%M")
    ap.add_argument("--out-dir", default=str(REPO / f"data/strategy_intake/grid_gpu_sectorcond_{ts}"))
    ap.add_argument("--generated-at", default=None, help="ISO 时间戳覆盖（幂等复现用；缺省取当前上海时区时间）")
    a = ap.parse_args(argv)
    out = Path(a.out_dir)
    generated_at = a.generated_at or datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")

    conn = DatabaseService().get_clickhouse_conn("reader")

    # ---- 前置断言：880 链 hash（复用冻结驱动 snapshot，禁第二套格式化） ----
    snap = freeze_baseline.snapshot(conn)
    chain = snap["kline_sector_880_1d"]["chain_sha256"]
    manifest_chain = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["kline_sector_880_1d"]["chain_sha256"]
    if not (chain == FROZEN_880_CHAIN == manifest_chain):
        print(
            f"FATAL: 880 chain drift: now={chain[:12]} frozen={FROZEN_880_CHAIN[:12]} "
            f"manifest={manifest_chain[:12]} —— 考卡 v2 §2：漂移即作废重做",
            file=sys.stderr,
        )
        return 2
    print(f"[ASSERT] 880 chain MATCH {chain[:12]}…（=冻结常数=manifest）")
    state_chain_now = snap["sector_state_live"]["chain_sha256"]
    print(
        f"[NOTE] state chain now {state_chain_now[:12]}…（活值 011d4528→含回放行 8d8f95ce 的"
        f"设计内演进，见 replay_report.md；全量 --manifest 对 state 报 DRIFT 属预期）"
    )

    # ---- 日期骨架：板数≥367 的交易日（与回放窗一致） ----
    skel = [(d, n) for d, n in conn.execute(SQL_SKELETON) if n >= BOARD_MIN]
    days = [d for d, _ in skel]
    day_keys = [d.isoformat()[:10] for d in days]
    board_count_per_day = {d.isoformat()[:10]: n for d, n in skel}
    boards = sorted(r[0] for r in conn.execute(SQL_BOARDS.format(first=day_keys[0], last=day_keys[-1])))
    n_b, n_d = len(boards), len(days)
    print(f"[SKELETON] days={n_d} ({day_keys[0]}→{day_keys[-1]}) boards={n_b}")

    # ---- 状态面（stage='close_final'） ----
    rows = conn.execute(SQL_STATE.format(first=day_keys[0], last=day_keys[-1]))
    col = {d: j for j, d in enumerate(day_keys)}
    row = {b: i for i, b in enumerate(boards)}

    momentum = np.full((n_b, n_d), np.nan, dtype=np.float32)
    rrg = np.zeros((n_b, n_d), dtype=np.int8)  # 0=未判定（'' 或缺格，meta 分记）
    watch = np.full((n_b, n_d), np.nan, dtype=np.float32)
    present = np.zeros((n_b, n_d), dtype=bool)

    rrg_seen: set[str] = set()
    mom_null_in_present = 0
    watch_per_day_distinct: dict[str, set] = {}
    for td, sc, mom, rq, ws in rows:
        i, j = row[sc], col[td.isoformat()[:10]]
        present[i, j] = True
        if mom is None:
            mom_null_in_present += 1
        else:
            momentum[i, j] = np.float32(mom)
        rrg_seen.add(rq)
        rrg[i, j] = -1  # 暂存，下面统一编码
        watch[i, j] = np.float32(ws) if ws is not None else np.nan
        watch_per_day_distinct.setdefault(td.isoformat()[:10], set()).add(ws)
    rrg_vocab = sorted(rrg_seen)  # 实际取值集合排序；'' 自然居首
    rrg_map = {v: k for k, v in enumerate(rrg_vocab)}
    for td, sc, _mom, rq, _ws in rows:
        rrg[row[sc], col[td.isoformat()[:10]]] = rrg_map[rq]

    absent_cells = int((~present).sum())
    watch_day_vec_ok = max(len(s) for s in watch_per_day_distinct.values()) == 1  # 市场级标量→每板同值

    is_holdout = np.array([d >= HOLDOUT_CUT for d in days], dtype=np.bool_)

    # ---- 源侧核对数（供自验断言） ----
    day_list_sql = ",".join(f"'{k}'" for k in day_keys)
    src_mom_null = conn.execute(SQL_MOM_NULL.format(day_list=day_list_sql))[0][0]
    src_rrg_empty = conn.execute(SQL_RRG_EMPTY.format(day_list=day_list_sql))[0][0]
    src_capital_null_all = snap["sector_state_live"]["null_counts"]["capital_score"]
    src_rows_total = snap["sector_state_live"]["rows"]

    # ---- 自验：载回断言 + 单点抽查 ----
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "momentum_pct.npy", momentum)
    np.save(out / "rrg_quadrant.npy", rrg)
    np.save(out / "watch_score.npy", watch)
    np.save(out / "is_holdout.npy", is_holdout)

    m2 = np.load(out / "momentum_pct.npy")
    r2 = np.load(out / "rrg_quadrant.npy")
    w2 = np.load(out / "watch_score.npy")
    h2 = np.load(out / "is_holdout.npy")
    checks: list[tuple[str, bool]] = [
        ("momentum shape", m2.shape == (n_b, n_d)),
        ("momentum dtype float32", m2.dtype == np.float32),
        (
            "momentum NaN == NULL(present)+absent",
            int(np.isnan(m2).sum()) == src_mom_null + absent_cells == mom_null_in_present + absent_cells,
        ),
        ("momentum finite == present-nulls 补集", int(np.isfinite(m2).sum()) == int(present.sum()) - src_mom_null),
        ("rrg shape/dtype int8", r2.shape == (n_b, n_d) and r2.dtype == np.int8),
        ("rrg 零值 == ''行+缺格", int((r2 == 0).sum()) == src_rrg_empty + absent_cells),
        ("rrg vocab 完备", set(np.unique(r2).tolist()) <= set(rrg_map.values())),
        ("watch shape/dtype float32", w2.shape == (n_b, n_d) and w2.dtype == np.float32),
        ("watch NaN == 缺格", int(np.isnan(w2).sum()) == absent_cells),
        ("watch 市场级（每日截面 distinct=1）", bool(watch_day_vec_ok)),
        ("is_holdout dtype bool / shape", h2.dtype == np.bool_ and h2.shape == (n_d,)),
        ("is_holdout True 数 == 切点后日数", int(h2.sum()) == sum(1 for k in day_keys if k >= HOLDOUT_CUT.isoformat())),
    ]
    # 抽查 3 个 (板,日) 格与 CH 单点查询逐位对拍
    spot_pick = [("880001.SH", "2022-09-01"), ("880001.SH", "2024-06-03"), ("880001.SH", "2026-09-22")]
    spot_log = []
    for sc, dk in spot_pick:
        t = conn.execute(SQL_SPOT.format(dk=dk, sc=sc))[0]
        i, j = row[sc], col[dk]
        ok = m2[i, j] == np.float32(t[0]) and r2[i, j] == rrg_map[t[1]] and w2[i, j] == np.float32(t[2])
        checks.append((f"spot {sc}@{dk}", bool(ok)))
        spot_log.append(
            {
                "cell": f"{sc}@{dk}",
                "ch": [t[0], t[1], t[2]],
                "pack": [float(m2[i, j]), rrg_vocab[int(r2[i, j])], float(w2[i, j])],
                "match": bool(ok),
            }
        )
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  [CHECK] {'PASS' if ok else 'FAIL'} {name}")
    if failed:
        print(f"FATAL: self-verify failed: {failed}", file=sys.stderr)
        return 3

    # ---- sector_index.json（双向映射+meta） ----
    index = {
        "pack": "gpu_sectorcond_v1",
        "generated_at": generated_at,
        "spec_sources": list(SPEC_SOURCES),
        "rows": {"n_boards": n_b, "order": "sector_code 升序", "sector_code_to_row": {b: row[b] for b in boards}},
        "cols": {"n_days": n_d, "order": "trade_date 升序", "date_to_col": {k: col[k] for k in day_keys}},
        "board_count_per_day": board_count_per_day,
        "meta": {
            "consumer": "单机 RTX 3090 24GB 59h 搜索窗（周五 12:00 点火）；整阵常驻显存 <0.05%，无需分片",
            "skeleton": {
                "rule": f"kline_sector_880 period='1d' 板数≥{BOARD_MIN} 的交易日",
                "n_days": n_d,
                "first": day_keys[0],
                "last": day_keys[-1],
                "boards_per_day_min": min(board_count_per_day.values()),
                "boards_per_day_max": max(board_count_per_day.values()),
            },
            "channels": {
                "momentum_pct.npy": {
                    "dtype": "float32",
                    "shape": [n_b, n_d],
                    "unit": "sector_state.momentum_pct 原值",
                    "nan_policy": "缺格/NULL 如实落 NaN 不插值",
                    "nan_split": {
                        "source_null_in_present_cells": int(src_mom_null),
                        "absent_cells_no_close_final_row": absent_cells,
                        "total_nan": int(src_mom_null) + absent_cells,
                    },
                },
                "rrg_quadrant.npy": {
                    "dtype": "int8",
                    "shape": [n_b, n_d],
                    "value_map": {k: rrg_map[k] for k in rrg_vocab},
                    "zero_semantics": "0=未判定：既含源内空串行（'') 也含缺格（无 close_final 行）",
                    "counts": {"source_empty_string_cells": int(src_rrg_empty), "absent_cells": absent_cells},
                },
                "watch_score.npy": {
                    "dtype": "float32",
                    "shape": [n_b, n_d],
                    "form": "市场级标量（每日截面 distinct=1 实测）按板广播；缺格=NaN",
                    "distinct_values_observed": [0.0, 0.03],
                    "per_day_broadcast_confirmed": bool(watch_day_vec_ok),
                },
                "is_holdout.npy": {
                    "dtype": "bool",
                    "shape": [n_d],
                    "rule": f"trade_date >= {HOLDOUT_CUT.isoformat()} 为 True（考卡 v2 §2 / 裁定#407 保密切点）",
                    "n_true": int(h2.sum()),
                    "n_false": int((~h2).sum()),
                },
            },
            "known_gap": f"末列 {day_keys[-1]} 活值仅 stage='pre_open' 行，close_final 过滤后全板缺格"
            "（momentum=NaN、rrg=0、watch=NaN）——如实呈现，不借用 pre_open 值",
            "forbidden_columns_not_in_pack": {
                "cols": list(FORBIDDEN_COLS),
                "reason": "考卡 v2 §2：strength/net_inflow_pct 42 日内 constituent_count 重复计数；"
                f"capital_score 活表+回放面 {src_capital_null_all}/{src_rows_total} 全 NULL，无活值可包",
            },
            "spot_checks": spot_log,
        },
        "provenance": {
            "source_tables": [
                f"{_T_SSTATE} (stage='close_final')",
                f"{_T_K880} (period='1d'，仅作日期骨架)",
            ],
            "kline_sector_880_chain_sha256": chain,
            "chain_assertion": f"生成前断言 MATCH：驱动 freeze_baseline.snapshot 单一真源，"
            f"{chain[:12]}… = 冻结常数 = baseline_manifest_v0.json（漂移即作废重做）",
            "manifest_path": str(MANIFEST_PATH.relative_to(REPO)),
            "state_chain_note": "sector_state 链已由活值 011d4528… 演进为含回放行 "
            f"{state_chain_now[:12]}…（replay_report.md 登记的设计内变化，日期不相交方案）",
            "sql": {"skeleton": SQL_SKELETON, "state": SQL_STATE.format(first=day_keys[0], last=day_keys[-1])},
            "builder": "docs/_working/sector_line/gpu_input_pack/build_gpu_input_pack.py",
            "replay_face": "sector_state 425,787 行/985 日 close_final（docs/_working/sector_line/statreplay/replay_report.md）",
        },
    }
    (out / "sector_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- README.md ----
    sizes = {p.name: p.stat().st_size for p in sorted(out.iterdir())}
    readme = f"""# GPU 板块条件矩阵输入包（grid_gpu_sectorcond）

> 规格=深度案卷 §6（容量口径与义务定义）+ 考卡 v2 §2（frozen 输入）；回放面=
> replay_report.md（sector_state 425,787 行/985 日 close_final）。生成于 {generated_at}。

## provenance

- 源表：`{_T_SSTATE}`（stage='close_final'，CH reader 只读）；日期骨架取
  `{_T_K880}`（period='1d'，板数≥{BOARD_MIN} 的 {n_d} 日，与回放窗一致）。
- **链 hash 前置断言**：生成前经冻结驱动 `freeze_baseline.py` 单一真源断言
  `kline_sector_880`/1d 链 sha256 = `{chain}`，与冻结常数及 `baseline_manifest_v0.json`
  逐位一致（MATCH，零漂移）。考卡 v2 §2：漂移即作废重做。
- sector_state 链现为 {state_chain_now[:12]}…：由活值快照 011d4528… 经深窗回放演进而来，
  属 replay_report.md 登记的设计内变化（日期不相交方案），非 880 回补。

## 通道说明（全部稠密 .npy；行=板块、列=交易日升序，映射见 sector_index.json）

| 文件 | shape | dtype | 说明 |
|---|---|---|---|
| momentum_pct.npy | ({n_b}, {n_d}) | float32 | sector_state.momentum_pct 原值；NaN=缺格/NULL（如实不插值：源内 NULL {src_mom_null} 格 + 无 close_final 行缺格 {absent_cells} 格） |
| rrg_quadrant.npy | ({n_b}, {n_d}) | int8 | 象限编码 {"，".join(f"{k!r}={v}" for k, v in rrg_map.items())}；0 同时覆盖源内空串（{src_rrg_empty} 格）与缺格（{absent_cells} 格） |
| watch_score.npy | ({n_b}, {n_d}) | float32 | **市场级标量**（实测每日截面 distinct=1，取值 {{0.0, 0.03}}）按板广播；缺格=NaN |
| is_holdout.npy | ({n_d},) | bool | trade_date ≥ {HOLDOUT_CUT.isoformat()} 为 True（裁定#407 保密切点）；True={int(h2.sum())} 日 / False={int((~h2).sum())} 日 |
| sector_index.json | — | — | sector_code→行号、日期→列号双向映射 + 板数/日数/生成参数/抽查对拍记录 |

已知缺口：末列 {day_keys[-1]} 活值仅 stage='pre_open' 行，close_final 过滤后全板缺格
（momentum=NaN、rrg=0、watch=NaN），如实呈现不借用 pre_open 值。

## 容量口径（防误读，案卷 §6 原义）

四通道合计约 {sum(sizes.values()) / 1e6:.1f} MB，RTX 3090 24GB 显存占用 <0.05%——**整阵可常驻，
消费方无需分片加载**。59h（周五 12:00→周日 23:00）是**消费窗**而非施工窗：本包能否跑完取决于
消费方搜索空间（矩阵单元数 × 假设数），**不取决于本包体积**。本包义务=把贵算部分（动量分位原料/
RRG 象限/轮动标签/考试窗位图）预置交付，59h 预算全部留给搜索，不耗在预处理。

## NO_EDGE 警示（原文，随包必带）

> {NO_EDGE_TEXT}

## 禁消费列声明

`strength`、`net_inflow_pct`、`capital_score` 三列**不在本包任何通道中**（考卡 v2 §2 frozen）：
前两者 42 日内 `constituent_count` 重复计数；`capital_score` 活表+回放面
{src_capital_null_all}/{src_rows_total} 全 NULL，该轴无活值，回放只能如实产 NULL，故不进包。

## 保密段声明

`trade_date ≥ {HOLDOUT_CUT.isoformat()}`（=考卡 v2 commit 冻结时点 −12 个月，裁定#407 滚动条款）
的数据**只供消费（考试），禁用于调参**（PB-08 + 裁定#407）。对应通道位图=is_holdout.npy。

## 自验记录

- 全部 .npy 载回断言 shape/dtype/NaN 计数与源查询一致（{"；".join(n for n, _ in checks if not n.startswith("spot"))}）。
- 抽查 3 个 (板,日) 格与 CH 单点查询逐位对拍 PASS：{"；".join(s["cell"] for s in spot_log)}。
- 链 hash 前置断言 MATCH（见 provenance）。

规格真源：{"；".join(SPEC_SOURCES)}
"""
    (out / "README.md").write_text(readme, encoding="utf-8")

    sizes = {p.name: p.stat().st_size for p in sorted(out.iterdir())}
    print(f"[DONE] {out}")
    for k, v in sizes.items():
        print(f"  {k:22s} {v:>9,} bytes")
    print(f"  {'TOTAL':22s} {sum(sizes.values()):>9,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
