# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign_20260924/links/L05_t0/（匹配矩阵产物族）
# [MODULE] tests.backtest.test_t0_state_match_matrix
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest, pandas, numpy
# [CONSUMERS] t0_state_match_matrix（L05-C04）同批测试
# [STARTUP] manual（pytest tests/backtest/test_t0_state_match_matrix.py）
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数面零 IO 零网络（禁触 CH 禁真全量跑；manifest 测试走 tmp_path 构造）；四元组数学对手算值；n<30 无并格；闭卷硬拦必须红；Wilson LB import 复用断言（禁本地重写公式）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [TTL] task_bound
"""t0_state_match_matrix 单测——构造数据纯函数面：四元组数学/无并格/轴对齐（unrouted/
unknown/missing）/闭卷硬拦/manifest 显式清单消费。禁真全量跑。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest import t0_state_match_matrix as sm


def make_pairs(n: int, wins: int, symbol: str = "000001", date: str = "2024-03-04") -> pd.DataFrame:
    gross = [50.0] * n
    net = [100.0 if i < wins else -100.0 for i in range(n)]
    return pd.DataFrame(
        {
            "symbol": [symbol] * n,
            "trade_date": [date] * n,
            "gross_bp": gross,
            "net_bp": net,
            "vwap_buy": [10.0] * n,
            "vwap_sell": [10.05] * n,
        }
    )


# ---------- 四元组数学（Wilson 95%，手算锚） ----------


def test_cell_stats_quadruple_hand_computed():
    g = make_pairs(30, 15)  # raw=0.5；Wilson95 LB 手算≈0.3127
    s = sm.cell_stats(g)
    assert s["n"] == 30
    assert s["win_rate_raw"] == pytest.approx(0.5)
    assert s["wilson_lb"] == pytest.approx(0.3315, abs=1e-3)  # 15/30 Wilson95 LB 手算锚
    assert s["wilson_ub"] > s["wilson_lb"] > 0.3
    assert s["interval_width"] == pytest.approx(s["wilson_ub"] - s["wilson_lb"], abs=1e-5)
    assert s["verdict"] == "ok"
    assert s["net_mean_bp"] == pytest.approx(0.0)


def test_cell_stats_insufficient_no_merge_gate():
    s = sm.cell_stats(make_pairs(29, 20))
    assert s["verdict"] == "insufficient_no_merge"  # n<30：即使 69% 胜率也不给 ok


def test_wilson_lb_is_reused_not_rewritten():
    """LB 必须 import 自仓内 fail-closed 实现（禁本地公式顶替）。"""
    assert sm.wilson_lb.__module__.endswith("pattern_win_rate_provider")
    with pytest.raises(ValueError):
        sm.wilson_lb(1.5, 10)  # fail-closed：越界 rate 拒绝
    assert sm.wilson_lb(0.5, 0) == 0.0


def test_build_matrix_no_cell_merging():
    """两不同相位格各 n=10 不得合并为 n=20（禁并格纪律：稀格保持独立 INSUFFICIENT）。"""
    df1 = make_pairs(10, 6, symbol="000001", date="2024-03-04")
    df2 = make_pairs(10, 7, symbol="000001", date="2024-03-05")
    df = pd.concat([df1, df2], ignore_index=True)
    df["rule"] = "r01"
    df["period"] = 5
    df["phase"] = (["ignition", "expansion"] * 10)[: len(df)]  # 仅相位不同 ⇒ 两个独立格
    df["sector_family"] = "银行"
    df["mcap_q"] = "q3"
    df["news_axis"] = sm.NEWS_AXIS_BLOCK
    m = sm.build_matrix(df, ["rule", "period", "phase", "sector_family", "mcap_q", "news_axis"])
    assert len(m) == 2  # 两格保持两行
    assert sorted(m["n"].tolist()) == [10, 10]
    assert (m["verdict"] == "insufficient_no_merge").all()
    assert set(m["phase"]) == {"ignition", "expansion"}


def test_build_matrix_pools_days_within_cell():
    """同格内跨日合并是合法语义（格=轴组合，不按日切分）。"""
    df1 = make_pairs(10, 6, symbol="000001", date="2024-03-04")
    df2 = make_pairs(10, 7, symbol="000001", date="2024-03-05")
    df = pd.concat([df1, df2], ignore_index=True)
    df["rule"] = "r01"
    df["period"] = 5
    df["phase"] = "expansion"
    df["sector_family"] = "银行"
    df["mcap_q"] = "q3"
    df["news_axis"] = sm.NEWS_AXIS_BLOCK
    m = sm.build_matrix(df, ["rule", "period", "phase", "sector_family", "mcap_q", "news_axis"])
    assert len(m) == 1 and m["n"].iloc[0] == 20 and m["verdict"].iloc[0] == "insufficient_no_merge"


# ---------- 轴对齐 ----------


def test_attach_axes_unrouted_unknown_missing():
    pairs = make_pairs(3, 2, symbol="999999", date="2024-03-04")
    phase_map = {"2024-03-05": "expansion"}  # 03-04 未路由
    sector_map = {"000001": "银行"}  # 999999 缺失
    mcap = pd.DataFrame({"symbol": ["000001"], "trade_date": ["2024-03-04"], "mcap_q": ["q1"]})
    df = sm.attach_axes(pairs, phase_map, sector_map, mcap)
    assert (df["phase"] == "unrouted").all()
    assert (df["sector_family"] == "unknown").all()
    assert (df["mcap_q"] == "missing").all()
    assert (df["news_axis"] == sm.NEWS_AXIS_BLOCK).all()


# ---------- manifest 显式清单消费 + 闭卷硬拦 ----------


def _write_manifest(tmp_path, trade_date: str) -> tuple:
    parquet = tmp_path / "t0_rule_pairs_t_b0000_r01_5min.parquet"
    make_pairs(2, 1).assign(trade_date=trade_date).to_parquet(parquet, index=False)
    man_path = tmp_path / "t0_rule_manifest_t.yaml"
    man_path.write_text(
        yaml.safe_dump({"tag": "t", "rules": ["r01"], "pairs_files": {"r01": [parquet.name]}}),
        encoding="utf-8",
    )
    return man_path, parquet


def test_load_pairs_rejects_closed_book(tmp_path):
    man_path, _ = _write_manifest(tmp_path, "2025-09-10")  # 切点后=闭卷
    with pytest.raises(SystemExit):
        sm.load_pairs_from_manifest(man_path, ["r01"], [5])


def test_load_pairs_missing_file_aborts(tmp_path):
    man_path = tmp_path / "m.yaml"
    man_path.write_text(
        yaml.safe_dump({"tag": "t", "rules": ["r01"], "pairs_files": {"r01": ["nope.parquet"]}}),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        sm.load_pairs_from_manifest(man_path, ["r01"], [5])


def test_load_pairs_filters_periods(tmp_path):
    man_path, _ = _write_manifest(tmp_path, "2024-03-04")
    with pytest.raises(SystemExit):
        sm.load_pairs_from_manifest(man_path, ["r01"], [1])  # 只要对 1min ⇒ 无匹配文件=显式报错非静默空


# ---------- 相位映射加载（真源文件只读校验解析面） ----------


def test_load_phase_map_reads_truth_source():
    if not sm.SIX_PHASE_CSV.exists():
        pytest.skip("six_phase_history_v1.csv 不在当前工作区（worktree 件）")
    phase_map, meta = sm.load_phase_map(sm.SIX_PHASE_CSV, "2021-09-01")
    assert meta["routed_days_in_window"] > 0
    assert set(phase_map.values()) <= {
        "ignition",
        "expansion",
        "euphoria",
        "distribution",
        "capitulation",
        "accumulation",
    }
    # 闭卷日禁入映射
    assert all(d <= sm.CLOSED_BOOK_CUTOFF for d in phase_map)
