# [BLUEPRINT] MOD-BT-IBT-MATRIX | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.ibt.ibt_mining_matrix
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; pandas
# [CONSUMERS] Max 施工方案 MAX-REMEDIATION-PLAN（复现/回归对照工具）；Owner 交付审计
# [STARTUP] manual CLI
# [MATURITY] experimental
# [INVARIANTS] 数据完备性探针：表级 SQL 覆盖（FINAL 去重读，ch_reader 统一读侧，SQL 集中于 _SQL_* 常量，表名经 table_registry/schema 真源）×E4 存活池 build 冒烟，落 ibt_data_matrix.yaml；协议冻结参数（IBT-PROTOCOL-V1）禁跑中改动；不接实盘不下单
# [MODIFY-GUARD] none（复现/回归对照工具件，改动须随数值回归对照 R-022）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/协议违规) | 探针失败记入矩阵 err 字段不中断（单表故障不拖垮全矩阵）
# [TESTS] none（工具件；红蓝对抗 ibt_redblue.py 即其自证）
# [TTL] permanent
# [A_module] module_id=MOD-BT-IBT-MATRIX | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""分包1① 数据完备性矩阵挖掘正式版（批A 工具正门化，源自 st-integrated-bt-20260922 原稿）.

两部分:
  A. 表级覆盖矩阵: 协议窗口族 × 核心表 (kline_daily_hfq/kline_index/stock_indicator/
     stk_limit/index_constituent/regime_snapshot_history/financial_derived)
  B. 策略级面板冒烟: E4 存活 17 条 c4 翻译件 build(start,end) 逐窗口实测
输出: docs/_working/integrated_backtest/ibt_data_matrix.yaml (+stdout md 表)
用法: python scripts/backtest/ibt/ibt_mining_matrix.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))  # schemas/ DDL-as-code 真源包在仓根（allocation_inputs 同款显式挂载）
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "backtest" / "translated"))
sys.path.insert(0, str(ROOT / "scripts" / "backtest" / "ibt"))

import ibt_runner as runner  # noqa: E402  同目录共享件（ch_query/regime_table 唯一实现于此）
import pandas as pd  # noqa: E402

WINDOWS = {
    "W_IS": ("2019-04-01", "2023-12-31"),
    "W_OOS": ("2024-01-01", "2025-09-08"),
    "W_HOLDOUT": ("2025-09-09", "2026-09-08"),
    "W_POSTD": ("2026-09-09", "2026-09-18"),
}

# E4 存活 17 条 (sharpe2_prep pool_manifest; 2 条死刑件标记 DR=death-row 仅供参考)
POOL = [
    ("FACT-4db4c41e", "c4_fact_4db4c41e.py", True),   # DR: beta 伪装
    ("FACT-4f749668", "c4_fact_4f749668.py", False),
    ("FACT-4228020a", "c4_fact_4228020a.py", False),
    ("FACT-e293e217", "c4_fact_e293e217.py", False),
    ("FACT-e831084c", "c4_fact_e831084c.py", False),
    ("FACT-4b200528", "c4_fact_4b200528.py", False),
    ("CAND-8d000bf3ccc3", "c4_8d000bf3ccc3_pb_poe.py", False),  # STR-VAL-001
    ("CAND-c4ec6332c07f", "c4_c4ec6332c07f_trend_score.py", False),
    ("CAND-e3da6fa71af1", "c4_e3da6fa71af1_panic_rebound.py", False),  # STR-VREV-025
    ("CAND-4440d07f973f", "c4_4440d07f973f_ultrashort.py", False),    # STR-DABAN-023
    ("CAND-eaddc3f9db4e", "c4_eaddc3f9db4e_rsrs_r2.py", False),
    ("CAND-d06cab686cef", "c4_d06cab686cef_rsrs_opt.py", False),
    ("CAND-29eb91dbaf60", "c4_29eb91dbaf60_crash_dodge.py", False),
    ("CAND-a4543012b464", "c4_a4543012b464_trend5.py", False),
    ("CAND-e2e7f033d97c", "c4_e2e7f033d97c_kd_cross.py", True),  # DR: 运气候选
    ("CAND-bd42540f86e4", "c4_bd42540f86e4_pe_pb.py", False),
    ("CAND-6a6ec8869ddb", "c4_6a6ec8869ddb_momentum62.py", False),
]

OUT = ROOT / "docs" / "_working" / "integrated_backtest" / "ibt_data_matrix.yaml"

# ---- CH 读侧（SQL 集中化：_SQL_* 常量 + ch_reader；表名真源=table_registry / schemas） ----
# ch_reader 对 ReplacingMergeTree 自动注入 FINAL；模板内显式 FINAL 沿用原稿口径（inject_final 幂等跳过）
_SQL_HFQ_WINDOW = (
    "SELECT count(), uniqExact(symbol), min(trade_date), max(trade_date), countDistinct(trade_date) "
    "FROM {tbl} FINAL WHERE trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_INDEX_WINDOW = (
    "SELECT count(), min(trade_date), max(trade_date) FROM {tbl} FINAL "
    "WHERE symbol='{sym}' AND trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_STOCK_INDICATOR_WINDOW = (
    "SELECT count(), countIf(pe>0), countIf(pb>0), countIf(total_mv>0), min(trade_date), max(trade_date) "
    "FROM {tbl} FINAL WHERE trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_STK_LIMIT_WINDOW = (
    "SELECT count(), min(trade_date), max(trade_date) FROM {tbl} FINAL "
    "WHERE trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_INDEX_CONSTITUENT_WINDOW = (
    "SELECT uniqExact(symbol), min(valid_from), max(valid_from) FROM {tbl} FINAL "
    "WHERE index_code='{sym}' AND valid_from <= '{e}' AND (valid_to='1900-01-01' OR valid_to > '{s}')"
)
_SQL_REGIME_WINDOW = (
    "SELECT count(), uniqExact(trade_date), min(trade_date), max(trade_date), uniqExact(run_id) "
    "FROM {tbl} WHERE trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_FINANCIAL_WINDOW = (
    "SELECT count(), min(trade_date), max(trade_date) FROM {tbl} FINAL "
    "WHERE trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_REGIME_STATES_ALL = "SELECT dominant, count() FROM {tbl} GROUP BY dominant ORDER BY count() DESC"
_SQL_REGIME_RUNS = (
    "SELECT run_id, count(), min(trade_date), max(trade_date) FROM {tbl} "
    "GROUP BY run_id ORDER BY max(trade_date) DESC LIMIT 5"
)


def _tbl(key: str) -> str:
    """表名真源解析（table_registry，裁定 #ARCH-CH-024，禁硬编码）。"""
    from zephyr.data.table_registry import get_registry

    return get_registry().table(key)




def part_a_tables() -> dict:
    probes = {}

    def probe(name: str, sql: str) -> None:
        t0 = time.time()
        try:
            tsv = runner.ch_query(sql)
            rows = [line.split("\t") for line in tsv.splitlines() if line.strip()]
            probes[name] = {"ok": True, "rows": rows, "sec": round(time.time() - t0, 1)}
        except Exception as exc:  # noqa: BLE001
            probes[name] = {"ok": False, "err": f"{type(exc).__name__}: {exc}", "sec": round(time.time() - t0, 1)}

    hfq = _tbl("market_kline_daily_hfq")
    kidx = _tbl("market_index_kline")
    sind = _tbl("market_stock_indicator")
    slim = _tbl("market_stk_limit")
    icon = _tbl("market_index_constituent")
    fin = _tbl("fund_financial_derived")
    reg = runner.regime_table()

    for wname, (s, e) in WINDOWS.items():
        probe(f"kline_daily_hfq#{wname}", _SQL_HFQ_WINDOW.format(tbl=hfq, s=s, e=e))
    for sym in ("000001", "000016", "000300", "000852"):
        for wname, (s, e) in WINDOWS.items():
            probe(f"kline_index[{sym}]#{wname}", _SQL_INDEX_WINDOW.format(tbl=kidx, sym=sym, s=s, e=e))
    for wname, (s, e) in WINDOWS.items():
        probe(
            f"stock_indicator#{wname}",
            _SQL_STOCK_INDICATOR_WINDOW.format(tbl=sind, s=s, e=e),
        )
        probe(f"stk_limit#{wname}", _SQL_STK_LIMIT_WINDOW.format(tbl=slim, s=s, e=e))
        probe(
            f"index_constituent[000300.SH]#{wname}",
            _SQL_INDEX_CONSTITUENT_WINDOW.format(tbl=icon, sym="000300.SH", s=s, e=e),
        )
        probe(f"regime_snapshot_history#{wname}", _SQL_REGIME_WINDOW.format(tbl=reg, s=s, e=e))
        probe(f"financial_derived#{wname}", _SQL_FINANCIAL_WINDOW.format(tbl=fin, s=s, e=e))
    probe("regime_states_all", _SQL_REGIME_STATES_ALL.format(tbl=reg))
    probe("regime_runs", _SQL_REGIME_RUNS.format(tbl=reg))
    return probes


def part_b_strategies() -> dict:
    import importlib.util

    results = {}
    for sid, fname, dr in POOL:
        results[sid] = {"file": fname, "death_row": dr, "windows": {}}
        fpath = ROOT / "scripts" / "backtest" / "translated" / fname
        if not fpath.exists():
            results[sid]["windows"]["ERROR"] = {"err": "file missing"}
            continue
        for wname, (s, e) in WINDOWS.items():
            t0 = time.time()
            try:
                spec = importlib.util.spec_from_file_location(f"ibt_{fname[:-3]}_{wname}", fpath)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                weights, closes = mod.build(s, e)
                nz_rows = int((weights.sum(axis=1) > 0).sum()) if not weights.empty else 0
                results[sid]["windows"][wname] = {
                    "ok": True,
                    "rows": int(len(weights)),
                    "cols": int(len(weights.columns)),
                    "nonzero_rows": nz_rows,
                    "closes_cols": int(len(closes.columns)) if closes is not None and not closes.empty else 0,
                    "sec": round(time.time() - t0, 1),
                }
            except Exception as exc:  # noqa: BLE001
                results[sid]["windows"][wname] = {
                    "ok": False,
                    "err": f"{type(exc).__name__}: {exc}",
                    "tb": traceback.format_exc(limit=3),
                    "sec": round(time.time() - t0, 1),
                }
        print(f"[B] {sid} done: {json.dumps({k: v.get('ok') for k, v in results[sid]['windows'].items()})}", flush=True)
    return results


def main() -> None:
    t0 = time.time()
    print("=== Part A: 表级覆盖矩阵 ===", flush=True)
    tables = part_a_tables()
    for k, v in tables.items():
        if v.get("ok"):
            print(f"  {k}: {v['rows']} ({v['sec']}s)", flush=True)
        else:
            print(f"  {k}: FAIL {v['err']}", flush=True)
    print("=== Part B: 策略面板冒烟 ===", flush=True)
    strategies = part_b_strategies()
    out = {
        "campaign": "st-integrated-bt-20260922",
        "generated_at": pd.Timestamp.now().isoformat(),
        "windows": {k: list(v) for k, v in WINDOWS.items()},
        "part_a_tables": tables,
        "part_b_strategies": strategies,
        "wall_sec": round(time.time() - t0, 1),
    }
    import yaml

    OUT.write_text(yaml.dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8")
    print(f"saved -> {OUT} (wall {out['wall_sec']}s)", flush=True)


if __name__ == "__main__":
    main()
