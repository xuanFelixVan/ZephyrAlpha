# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-DATA-063 M1-④ 盘中情绪调度回路 run_once 单拍单元测试（92号清单 §8.2，合成快照注入不触库不触网）。

覆盖：
- rows_to_time_series 装配：合成快照行 → BreadthTimeSeries（ts 升序重排/缺 ts 跳过/
  total_count 取最新行/字段映射对照 M1-① 波3 契约）；空序列 → None；
- run_once 单拍链路：合成 6 分钟快照 → time_series 装配正确 → MOD-SIG-025 analyze
  → prediction_log 真实写入（临时 sqlite 库）+ payload 关键字段断言；
- SEC-02 挂接同载体：sector_snapshot 合成行 → sector_board 入结果；两轮 run_once
  previous_board 传递 → new_open_boards 对照生效；
- fail-open：快照查询异常/无当日快照 → degraded 返回不抛；log_prediction 异常 →
  errors 留痕不炸；ch_client 缺失 → degraded 直返；
- 有界形态：模块无 while True 自旋（源码静态断言）。
"""

from __future__ import annotations

import inspect
import json
from datetime import date, datetime, timedelta
from typing import Any

import pytest

from zephyr.data.intraday_sentiment_loop import (
    IntradayLoopResult,
    rows_to_time_series,
    run_once,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    query_predictions,
)

_TD = date(2026, 8, 21)
_T0 = datetime(2026, 8, 21, 9, 31, 0)  # 盘中首分钟


def _breadth_row(
    i: int,
    *,
    adv: int,
    dec: int,
    lu: int,
    sealed: int,
    attempted: int,
    total: int = 5000,
    amount: float = 1e11,
    flat: int = 100,
    ld: int = 0,
) -> tuple:
    """合成一行 market_breadth_snapshot（列序=_BREADTH_ROW_KEYS）。"""
    return (
        _T0 + timedelta(minutes=i),
        adv,
        dec,
        flat,
        lu,
        ld,
        sealed,
        attempted,
        total,
        amount + i * 1e9,
        _TD,
    )


def _six_minute_rows() -> list[tuple]:
    """6 分钟合成序列：上涨家数逐分钟走高（vel>0），涨停 2→3。"""
    advs = [2400, 2450, 2500, 2550, 2600, 2650]
    lus = [2, 2, 3, 3, 3, 3]
    return [
        _breadth_row(i, adv=advs[i], dec=5000 - 100 - advs[i], lu=lus[i], sealed=lus[i], attempted=lus[i] + 1)
        for i in range(6)
    ]


def _sector_rows() -> list[tuple]:
    """合成 sector_snapshot 两行（880301.SH 单板块双快照，列序=aggregator _SNAPSHOT_KEYS）。"""
    base = datetime(2026, 8, 21, 10, 0, 0)
    return [
        ("880301.SH", base, 100.0, 99.0, 1e6, 10, 5, 0, 0, 0.5, 100.0, "sector", _TD),
        ("880301.SH", base + timedelta(seconds=30), 101.0, 99.0, 2e6, 12, 4, 0, 0, 0.8, 100.5, "sector", _TD),
    ]


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由返回合成行（不触库）。"""

    def __init__(self, *, breadth=None, sector=None, index_price=None, index_prev=None, boom_on=None):
        self._breadth = breadth if breadth is not None else _six_minute_rows()
        self._sector = sector if sector is not None else _sector_rows()
        self._index_price = index_price if index_price is not None else [(3950.0, datetime(2026, 8, 21, 10, 36))]
        self._index_prev = index_prev if index_prev is not None else [(3900.0,)]
        self._boom = boom_on  # 'breadth' | 'sector' | 'index' | None
        self.calls: list[str] = []

    def execute(self, sql, params=None):
        self.calls.append(sql)
        if "market_breadth_snapshot" in sql:
            if self._boom == "breadth":
                raise RuntimeError("合成快照故障")
            return list(self._breadth)
        if "sector_snapshot" in sql:
            if self._boom == "sector":
                raise RuntimeError("合成板块故障")
            return list(self._sector)
        if "index_quote" in sql:
            if self._boom == "index":
                raise RuntimeError("合成指数故障")
            return list(self._index_price)
        if "kline_index" in sql:
            return list(self._index_prev)
        return []


class TestRowsToTimeSeries:
    def test_mapping_and_sort(self):
        rows = [
            dict(
                zip(
                    (
                        "ts",
                        "advancing",
                        "declining",
                        "flat",
                        "limit_up",
                        "limit_down",
                        "sealed",
                        "attempted",
                        "total_count",
                        "total_amount",
                        "trade_date",
                    ),
                    r,
                    strict=True,
                )
            )
            for r in _six_minute_rows()
        ]
        rows.reverse()  # 乱序输入 → 装配按 ts 升序
        assembled = rows_to_time_series(rows)
        assert assembled is not None
        ts_series, td = assembled
        assert td == "2026-08-21"
        assert ts_series.total_count == 5000
        snaps = ts_series.snapshots
        assert len(snaps) == 6
        assert [s.advancing_count for s in snaps] == [2400, 2450, 2500, 2550, 2600, 2650]
        assert snaps[0].timestamp < snaps[-1].timestamp
        assert snaps[-1].limit_up_count == 3 and snaps[-1].sealed_limit_up_count == 3
        assert snaps[-1].attempted_limit_up_count == 4
        assert ts_series.zscore_stats is None  # 20 日统计=数据期后补

    def test_missing_ts_skipped(self):
        rows = [
            {
                "ts": None,
                "advancing": 1,
                "declining": 0,
                "limit_up": 0,
                "sealed": 0,
                "attempted": 0,
                "total_count": 10,
                "trade_date": "2026-08-21",
            },
            {
                "ts": "2026-08-21 09:31:00",
                "advancing": 2,
                "declining": 1,
                "limit_up": 0,
                "sealed": 0,
                "attempted": 0,
                "total_count": 10,
                "trade_date": "2026-08-21",
            },
        ]
        assembled = rows_to_time_series(rows)
        assert assembled is not None and len(assembled[0].snapshots) == 1

    def test_empty_returns_none(self):
        assert rows_to_time_series([]) is None
        assert rows_to_time_series([{"ts": None}]) is None


class TestRunOnce:
    def test_happy_path_writes_prediction_log(self, tmp_path):
        db = tmp_path / "gov_test.db"
        ensure_prediction_log_table(db)
        result = run_once(ch_client=_FakeCH(), db_path=str(db))
        assert isinstance(result, IntradayLoopResult)
        assert result.trade_date == "2026-08-21"
        assert result.n_snapshots == 6
        assert result.total_count == 5000
        assert result.sentiment is not None
        assert 0.0 <= result.sentiment.overall_score <= 100.0
        # M1-① 增量被 time_series 激活（6 分钟 ≥ vel 5m 窗口）
        assert result.sentiment.breadth_acceleration is not None
        assert result.sentiment.breadth_acceleration.breadth_vel_5m == pytest.approx((2650 - 2400) / 5000)
        assert result.prediction_log_id is not None and result.prediction_log_id > 0
        # prediction_log 落库验证（M4-② 载体）
        rows = query_predictions(trade_date="2026-08-21", module="zephyr.data.intraday_sentiment_loop", db_path=str(db))
        assert len(rows) == 1
        assert rows[0]["prediction_type"] == "sentiment_score"
        payload = json.loads(rows[0]["payload_json"])
        assert payload["time_series_minutes"] == 6
        assert payload["snapshot"]["advancing"] == 2650
        assert payload["snapshot"]["attempted"] == 4
        assert payload["breadth_acceleration"]["lu_net_rate_5m"] == 1
        assert "sector_board" in payload  # SEC-02 榜面摘要注解留痕

    def test_sector_board_hooked_with_previous(self, tmp_path):
        db = tmp_path / "gov_test.db"
        ensure_prediction_log_table(db)
        r1 = run_once(ch_client=_FakeCH(), db_path=str(db))
        assert r1.sector_board is not None and r1.sector_board.n_sectors == 1
        assert r1.sector_board.new_open_boards == []  # 首轮无对照基线
        # 第二轮：880302.SH 新晋入资金榜（对照 r1 榜 → new_open_boards 检出）
        base = datetime(2026, 8, 21, 10, 1, 0)
        sector_r2 = _sector_rows() + [
            ("880302.SH", base, 50.0, 49.0, 1e6, 3, 2, 0, 0, 0.3, 50.0, "sector", _TD),
            ("880302.SH", base + timedelta(seconds=30), 51.0, 49.0, 9e6, 5, 1, 0, 0, 1.2, 50.5, "sector", _TD),
        ]
        r2 = run_once(ch_client=_FakeCH(sector=sector_r2), db_path=str(db), previous_board=r1.sector_board)
        assert r2.sector_board is not None
        assert "880302.SH" in r2.sector_board.new_open_boards
        assert "880301.SH" not in r2.sector_board.new_open_boards  # 已在首轮榜 → 非新开

    def test_index_degradation_note(self, tmp_path):
        db = tmp_path / "gov_test.db"
        ensure_prediction_log_table(db)
        result = run_once(ch_client=_FakeCH(index_price=[]), db_path=str(db))
        assert result.sentiment is not None  # 指数缺失不阻塞情绪分析
        assert any("指数涨跌幅不可得" in n for n in result.notes)

    def test_breadth_query_failure_fail_open(self, tmp_path):
        result = run_once(ch_client=_FakeCH(boom_on="breadth"), db_path=str(tmp_path / "x.db"))
        assert result.degraded is True
        assert any("market_breadth_snapshot 查询失败" in e for e in result.errors)
        assert result.sector_board is not None  # SEC-02 独立环节仍执行（载体职责）

    def test_no_snapshot_skips_sentiment(self, tmp_path):
        result = run_once(ch_client=_FakeCH(breadth=[]), db_path=str(tmp_path / "x.db"))
        assert result.degraded is True
        assert result.sentiment is None
        assert any("无快照" in n for n in result.notes)
        assert result.sector_board is not None

    def test_prediction_log_failure_recorded(self, tmp_path, monkeypatch):
        def _boom(**kw):
            raise RuntimeError("合成写库故障")

        monkeypatch.setattr("zephyr.data.intraday_sentiment_loop.log_prediction", _boom)
        result = run_once(ch_client=_FakeCH(), db_path=str(tmp_path / "x.db"))
        assert result.sentiment is not None  # 分析仍完成
        assert result.prediction_log_id is None
        assert any("prediction_log 写入失败" in e for e in result.errors)
        assert result.degraded is True

    def test_client_missing_degraded(self, monkeypatch):
        # 默认客户端不可用路径：_default_client 返回 None → degraded 直返不抛
        monkeypatch.setattr("zephyr.data.intraday_sentiment_loop._default_client", lambda: None)
        result = run_once(ch_client=None)
        assert result.degraded is True and result.sentiment is None
        assert any("客户端不可用" in e for e in result.errors)

    def test_bounded_form_no_spin_loop(self):
        # PERM-TRIGGER 纪律：模块只含单拍函数，禁止 while True 常驻循环
        # （头注/docstring 文本提及该词作纪律说明，故断言代码形态带冒号的循环语句）
        import zephyr.data.intraday_sentiment_loop as loop_mod

        src = inspect.getsource(loop_mod)
        assert "while True:" not in src
        assert "while 1:" not in src
