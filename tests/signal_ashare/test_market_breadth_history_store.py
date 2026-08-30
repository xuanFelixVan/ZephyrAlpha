# [A_test] module_id: MOD-SIG-063-store | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-063 | 待统筹登记 | 44号 §9.3 + 92号 §8.1/§8.2
# [MODULE] tests.signal_ashare.test_market_breadth_history_store
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""MarketBreadthHistoryStore（MOD-SIG-063-store）施工验证测试。

覆盖：
- 重采样：分钟快照 → 30 时点网格线性插值；
- 契约适配：HistoryRecord → DataFrame 列名与 similar_day_inference 输入契约一致；
- fail-open：CH 异常/空表/查询失败 → 空列表；
- 剔除规则：单日有效点<2、无指数收盘 → 剔除；
- 零运行时调用：默认参数下表空 → 空列表（到量自动切换由 similar_day_inference 侧负责）。
全 mock CH 连接，不触真 ClickHouse。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.signal_ashare.market_breadth_history_store import (
    HistoryRecord,
    MarketBreadthHistoryStore,
    load_history_store,
)


def _tsv(rows: list[tuple]) -> str:
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


def _mk_breadth_rows(trade_date: str, n: int = 30) -> str:
    """合成 n 分钟快照 TSV（线性增长形态）。"""
    rows = []
    for i in range(n):
        # 09:30 起每分钟一行
        hh = 9 + (30 + i) // 60
        mm = (30 + i) % 60
        ts = f"{trade_date} {hh:02d}:{mm:02d}:00"
        rows.append((
            trade_date, ts,
            2000 + i * 10,   # advancing
            1500 - i * 5,    # declining
            300,             # flat
            50 + i,          # limit_up
            10,              # limit_down
            45,              # sealed
            60,              # attempted
            5000,            # total_count
            1e9 + i * 1e7,   # total_amount
        ))
    return _tsv(rows)


def _mk_index_rows(trade_date: str, close: float = 3200.0) -> str:
    return _tsv([(trade_date, close)])


def test_load_history_store_assembles_records():
    """正常数据：按日分组 → 重采样 → HistoryRecord 列表（含 index_price）。"""
    breadth_tsv = (
        _mk_breadth_rows("2026-08-20", 30)
        + "\n"
        + _mk_breadth_rows("2026-08-21", 30)
    )
    index_tsv = _mk_index_rows("2026-08-20", 3200.0) + "\n" + _mk_index_rows("2026-08-21", 3210.0)

    def _ch(sql: str) -> str:
        if "kline_index" in sql:
            return index_tsv
        return breadth_tsv

    store = load_history_store("2026-08-21", lookback_days=10, query_fn=_ch)
    assert len(store) == 2
    rec0 = store.records[0]
    assert rec0.trade_date == "2026-08-20"
    assert rec0.index_price[0] == pytest.approx(3200.0)
    # breadth_vel = advancing 在 30 网格点上的差分（grid 步长 ≈ 11.38 分钟）
    assert rec0.breadth_vel[1] > 0.0  # 正值（advancing 递增）
    assert rec0.lu_net[0] == pytest.approx(40.0)  # 50 - 10
    assert np.isnan(rec0.yw_spread).all()
    assert np.isnan(rec0.if_basis).all()


def test_to_dataframe_matches_similar_day_contract():
    """HistoryRecord.to_dataframe 列契约 = similar_day_inference 输入契约。"""
    grid = np.linspace(570.0, 900.0, 30)
    rec = HistoryRecord(
        trade_date="2026-08-21",
        breadth_vel=np.arange(30.0),
        lu_net=np.arange(30.0),
        vol_extrap_ratio=np.full(30, np.nan),
        yw_spread=np.full(30, np.nan),
        if_basis=np.full(30, np.nan),
        index_price=np.full(30, 3200.0),
    )
    df = rec.to_dataframe()
    assert list(df.columns) == [
        "ts", "breadth_vel", "lu_net", "vol_extrap_ratio",
        "yw_spread", "if_basis", "index_price",
    ]
    assert len(df) == 30
    assert df["ts"].iloc[0] == pytest.approx(570.0)
    assert df["ts"].iloc[-1] == pytest.approx(900.0)


def test_fail_open_on_ch_exception():
    """CH 查询抛异常 → 空列表（fail-open）。"""
    def _ch(sql: str) -> str:
        raise RuntimeError("boom")

    store = load_history_store("2026-08-21", query_fn=_ch)
    assert len(store) == 0
    assert list(store) == []


def test_fail_open_on_empty_table():
    """表空 → 空列表。"""
    store = load_history_store("2026-08-21", query_fn=lambda sql: "")
    assert len(store) == 0


def test_skip_day_with_insufficient_snapshots():
    """单日有效快照 <2 → 剔除该日。"""
    breadth_tsv = _mk_breadth_rows("2026-08-20", 1)  # 仅 1 条
    index_tsv = _mk_index_rows("2026-08-20", 3200.0)

    def _ch(sql: str) -> str:
        if "kline_index" in sql:
            return index_tsv
        return breadth_tsv

    store = load_history_store("2026-08-21", lookback_days=10, query_fn=_ch)
    assert len(store) == 0


def test_skip_day_without_index_close():
    """无指数收盘 → 剔除该日（标签无法计算）。"""
    breadth_tsv = _mk_breadth_rows("2026-08-20", 30)
    index_tsv = ""  # 无指数数据

    def _ch(sql: str) -> str:
        if "kline_index" in sql:
            return index_tsv
        return breadth_tsv

    store = load_history_store("2026-08-21", lookback_days=10, query_fn=_ch)
    assert len(store) == 0


def test_invalid_end_date_fail_closed():
    """end_date 非法 → ValueError（fail-closed）。"""
    with pytest.raises(ValueError):
        load_history_store("not-a-date", query_fn=lambda sql: "")


def test_iteration_yields_dataframes():
    """MarketBreadthHistoryStore 可迭代，逐元素为 DataFrame。"""
    rec = HistoryRecord(
        trade_date="2026-08-21",
        breadth_vel=np.zeros(30),
        lu_net=np.zeros(30),
        vol_extrap_ratio=np.full(30, np.nan),
        yw_spread=np.full(30, np.nan),
        if_basis=np.full(30, np.nan),
        index_price=np.full(30, 3200.0),
    )
    store = MarketBreadthHistoryStore(records=(rec,))
    dfs = list(store)
    assert len(dfs) == 1
    assert isinstance(dfs[0], pd.DataFrame)
    assert dfs[0]["index_price"].iloc[-1] == pytest.approx(3200.0)
