# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-DATA-061 盘中板块实时聚合器（SEC-02）单元测试（92号清单 §7.6，合成快照注入不触库）"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any

import pytest

from zephyr.data.sector_intraday_aggregator import (
    SectorIntradayBoard,
    SectorIntradayConfig,
    aggregate_sector_intraday,
    load_latest_snapshots,
)

T0 = datetime(2026, 8, 21, 9, 45, 0)  # 合成窗口起点（盘中）
SECTORS = ["880301.SH", "880302.SH", "880303.SH"]


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由返回合成行（不触库）。"""

    def __init__(self, rows: list[tuple] | None = None, exc: bool = False):
        self._rows = rows or []
        self._exc = exc
        self.calls: list[tuple[str, Any]] = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        if self._exc:
            raise RuntimeError("合成故障")
        if "sector_snapshot" in sql:
            return list(self._rows)
        return []


def _snap(
    code: str,
    ts: datetime,
    *,
    now: float = 100.0,
    last_close: float = 100.0,
    amount: float = 0.0,
    up: int = 0,
    down: int = 0,
    inside: int = 0,
    outside: int = 0,
    zangsu: float = 0.0,
    avg: float = 100.0,
    mtype: str = "sector",
    td: str = "2026-08-21",
) -> dict:
    """合成一条 sector_snapshot 快照 dict（键=表列名）。"""
    return {
        "sector_code": code,
        "timestamp": ts,
        "now_price": now,
        "last_close": last_close,
        "amount": amount,
        "up_home": up,
        "down_home": down,
        "inside": inside,
        "outside": outside,
        "zangsu": zangsu,
        "average_price": avg,
        "market_type": mtype,
        "trade_date": td,
    }


def _series(
    code: str,
    amounts: list[float],
    *,
    zangsus: list[float] | None = None,
    ups: list[int] | None = None,
    downs: list[int] | None = None,
    now: float = 100.0,
    last_close: float = 100.0,
    step_sec: int = 30,
) -> list[dict]:
    """合成单板块 30s 等距快照序列（amount 累计单调）。"""
    n = len(amounts)
    zangsus = zangsus or [0.0] * n
    ups = ups or [0] * n
    downs = downs or [0] * n
    return [
        _snap(
            code,
            T0 + timedelta(seconds=step_sec * i),
            now=now,
            last_close=last_close,
            amount=amounts[i],
            up=ups[i],
            down=downs[i],
            zangsu=zangsus[i],
        )
        for i in range(n)
    ]


# ---------- 资金榜（成交额增量代理口径） ----------


class TestInflowTop:
    def test_amount_delta_ranking(self):
        """三板块窗口成交增量 300/100/200 → 资金榜次序 880301>880303>880302。"""
        snaps = (
            _series("880301.SH", [1000.0, 1100.0, 1300.0])
            + _series("880302.SH", [500.0, 550.0, 600.0])
            + _series("880303.SH", [800.0, 900.0, 1000.0])
        )
        board = aggregate_sector_intraday(snaps)
        assert board.degraded is False
        assert board.n_sectors == 3
        assert [r.sector_code for r in board.inflow_top] == ["880301.SH", "880303.SH", "880302.SH"]
        assert board.inflow_top[0].amount_delta == pytest.approx(300.0)
        # 窗口 1 分钟 → 速度=增量/1min
        assert board.inflow_top[0].amount_velocity == pytest.approx(300.0)

    def test_zero_delta_excluded(self):
        """窗口零成交增量板块不入资金榜（min_amount_delta 默认 0 严格大于）。"""
        snaps = _series("880301.SH", [500.0, 500.0, 500.0]) + _series("880302.SH", [100.0, 150.0, 200.0])
        board = aggregate_sector_intraday(snaps)
        assert [r.sector_code for r in board.inflow_top] == ["880302.SH"]
        assert not any("单快照" in n for n in board.notes)  # 3 快照/板块，不触发单快照注解

    def test_top_n_truncation(self):
        """资金榜长度受 inflow_top_n 截断。"""
        cfg = SectorIntradayConfig(inflow_top_n=1)
        snaps = _series("880301.SH", [0.0, 300.0]) + _series("880302.SH", [0.0, 200.0])
        board = aggregate_sector_intraday(snaps, config=cfg)
        assert len(board.inflow_top) == 1
        assert board.inflow_top[0].sector_code == "880301.SH"

    def test_net_active_buy_forward_field(self):
        """内外盘差×均价×手数 → net_active_buy（前向兼容字段，复位守卫）。"""
        snaps = [
            _snap("880301.SH", T0, inside=10, outside=20, avg=50.0),
            _snap("880301.SH", T0 + timedelta(seconds=30), inside=15, outside=32, avg=50.0),
        ]
        board = aggregate_sector_intraday(snaps)
        row = board.rows[0]
        # Δout=12, Δin=5 → (12-5)×50×100=35000
        assert row.net_active_buy == pytest.approx(35000.0)

    def test_counter_reset_guard(self):
        """inside/outside 计数器复位（负差）回退取当前值不炸。"""
        snaps = [
            _snap("880301.SH", T0, inside=100, outside=200, avg=10.0),
            _snap("880301.SH", T0 + timedelta(seconds=30), inside=5, outside=8, avg=10.0),
        ]
        board = aggregate_sector_intraday(snaps)
        # 复位：d_out=8, d_in=5 → (8-5)×10×100=3000
        assert board.rows[0].net_active_buy == pytest.approx(3000.0)


# ---------- 涨速榜 ----------


class TestSpeedTop:
    def test_zangsu_ranking_and_positive_filter(self):
        """涨速榜按最新 zangsu 降序，负/零涨速默认剔除。"""
        snaps = (
            _series("880301.SH", [0.0, 0.0], zangsus=[0.1, 0.5])
            + _series("880302.SH", [0.0, 0.0], zangsus=[0.2, -0.3])
            + _series("880303.SH", [0.0, 0.0], zangsus=[0.0, 0.9])
        )
        board = aggregate_sector_intraday(snaps)
        assert [r.sector_code for r in board.speed_top] == ["880303.SH", "880301.SH"]
        assert board.speed_top[0].zangsu == pytest.approx(0.9)
        # 涨速窗口变化量
        assert board.speed_top[0].zangsu_delta == pytest.approx(0.9)


# ---------- 涨跌家数结构 ----------


class TestBreadth:
    def test_breadth_totals_and_delta(self):
        """合计涨跌家数+涨跌比+结构变化量正确。"""
        snaps = (
            _series("880301.SH", [0.0, 0.0], ups=[100, 120], downs=[50, 40], now=101.0)
            + _series("880302.SH", [0.0, 0.0], ups=[30, 30], downs=[70, 80], now=99.0)
            + _series("880303.SH", [0.0, 0.0], ups=[10, 10], downs=[10, 10])
        )
        board = aggregate_sector_intraday(snaps)
        b = board.breadth
        assert b.total_up == 160  # 120+30+10
        assert b.total_down == 130  # 40+80+10
        assert b.up_down_ratio == pytest.approx(160 / 130, abs=1e-4)
        assert b.total_up_delta == 20  # (120-100)+(30-30)+(10-10)
        assert b.total_down_delta == 0  # (40-50)+(80-70)+(10-10)=0
        assert (b.sectors_up, b.sectors_down, b.sectors_flat) == (1, 1, 1)


# ---------- 新开板清单（对照上一周期榜） ----------


class TestNewOpenBoards:
    def _board_round1(self) -> SectorIntradayBoard:
        """首轮：仅 880301 在榜（增量 300+涨速 0.5）；880302/880303 零增量负涨速不入榜。"""
        snaps = (
            _series("880301.SH", [0.0, 300.0], zangsus=[0.0, 0.5])
            + _series("880302.SH", [10.0, 10.0], zangsus=[-0.01, -0.01])
            + _series("880303.SH", [10.0, 10.0], zangsus=[-0.02, -0.02])
        )
        return aggregate_sector_intraday(snaps)

    def test_new_entry_detected(self):
        """次轮 880303 新晋资金+涨速榜 → 新开板清单含且仅含 880303。"""
        prev = self._board_round1()
        assert prev.new_open_boards == []  # 首轮无基线
        assert any("对照基线" in n for n in prev.notes)

        snaps2 = (
            _series("880301.SH", [300.0, 400.0], zangsus=[0.5, 0.4])
            + _series("880302.SH", [10.0, 10.0], zangsus=[-0.01, -0.01])
            + _series("880303.SH", [10.0, 500.0], zangsus=[-0.02, 0.8])
        )
        board2 = aggregate_sector_intraday(snaps2, previous_board=prev)
        assert board2.new_open_boards == ["880303.SH"]

    def test_no_new_entry_when_stable(self):
        """榜单成员不变 → 新开板清单为空。"""
        prev = self._board_round1()
        snaps2 = (
            _series("880301.SH", [300.0, 600.0], zangsus=[0.5, 0.6])
            + _series("880302.SH", [10.0, 10.0], zangsus=[-0.01, -0.01])
            + _series("880303.SH", [10.0, 10.0], zangsus=[-0.02, -0.02])
        )
        board2 = aggregate_sector_intraday(snaps2, previous_board=prev)
        assert board2.new_open_boards == []


# ---------- 输入健壮性 ----------


class TestInputRobustness:
    def test_empty_input(self):
        """空输入 → degraded=True 空榜不炸。"""
        board = aggregate_sector_intraday([])
        assert board.degraded is True
        assert board.n_sectors == 0
        assert board.inflow_top == [] and board.speed_top == []
        assert board.new_open_boards == []
        assert any("为空" in n for n in board.notes)

    def test_market_index_excluded(self):
        """880001-880009 市场统计指数剔除出板块榜（前缀+market_type 双保险）。"""
        snaps = _series("880001.SH", [0.0, 999.0], zangsus=[0.0, 5.0]) + _series(
            "880301.SH", [0.0, 100.0], zangsus=[0.0, 0.5]
        )
        board = aggregate_sector_intraday(snaps)
        assert board.n_sectors == 1
        assert [r.sector_code for r in board.inflow_top] == ["880301.SH"]

    def test_bad_timestamp_skipped(self):
        """timestamp 无法解析的记录跳过不炸，notes 留痕。"""
        snaps = _series("880301.SH", [0.0, 100.0])
        snaps.append(_snap("880302.SH", T0, amount=50.0))
        snaps[-1]["timestamp"] = "not-a-time"
        board = aggregate_sector_intraday(snaps)
        assert board.n_sectors == 1
        assert any("timestamp" in n for n in board.notes)

    def test_dataframe_ducktype(self):
        """DataFrame 鸭子类型（to_dict('records')）输入等价 list[dict]。"""
        snaps = _series("880301.SH", [0.0, 100.0])

        class _FakeDF:
            def __init__(self, records):
                self._records = records

            def to_dict(self, orient):
                assert orient == "records"
                return list(self._records)

        board = aggregate_sector_intraday(_FakeDF(snaps))
        assert board.n_sectors == 1
        assert board.rows[0].amount_delta == pytest.approx(100.0)

    def test_unsupported_type_raises(self):
        """不支持类型 → TypeError（调用方契约违例，fail-closed）。"""
        with pytest.raises(TypeError):
            aggregate_sector_intraday("not-a-list")

    def test_string_timestamp_accepted(self):
        """timestamp 为 ISO 字符串同样可聚合（TSV 通道兼容性）。"""
        snaps = [
            _snap("880301.SH", T0, amount=0.0),
            _snap("880301.SH", T0, amount=60.0),
        ]
        snaps[1]["timestamp"] = (T0 + timedelta(seconds=30)).isoformat()
        board = aggregate_sector_intraday(snaps)
        assert board.rows[0].amount_delta == pytest.approx(60.0)

    def test_asdict_json_serializable(self):
        """frozen dataclass asdict 可 JSON 序列化。"""
        import json

        board = aggregate_sector_intraday(_series("880301.SH", [0.0, 100.0]))
        json.dumps(asdict(board), ensure_ascii=False)


# ---------- load_latest_snapshots（ch_client 注入） ----------


class TestLoadLatestSnapshots:
    def _ch_rows(self) -> list[tuple]:
        """合成 CH 行（列序=_SNAPSHOT_KEYS）。"""
        return [
            (
                "880301.SH",
                T0,
                100.0,
                100.0,
                1000.0,
                10,
                5,
                0,
                0,
                0.5,
                100.0,
                "sector",
                "2026-08-21",
            ),
            (
                "880301.SH",
                T0 + timedelta(seconds=30),
                101.0,
                100.0,
                1300.0,
                12,
                4,
                0,
                0,
                0.6,
                100.5,
                "sector",
                "2026-08-21",
            ),
        ]

    def test_injected_client_roundtrip(self):
        """注入 _FakeCH → dict 列表键齐全且可直接喂 aggregate。"""
        client = _FakeCH(rows=self._ch_rows())
        snaps = load_latest_snapshots(ch_client=client, minutes=5)
        assert len(snaps) == 2
        assert snaps[0]["sector_code"] == "880301.SH"
        assert snaps[1]["amount"] == 1300.0
        # SQL 参数化留痕（minutes 走 params 非 f-string）
        assert client.calls[0][1] == {"minutes": 5}
        board = aggregate_sector_intraday(snaps)
        assert board.degraded is False
        assert board.rows[0].amount_delta == pytest.approx(300.0)

    def test_query_exception_returns_empty(self):
        """CH 查询异常 → 返回 [] 不抛（对齐 ch_reader 降级语义）。"""
        assert load_latest_snapshots(ch_client=_FakeCH(exc=True)) == []

    def test_no_data_returns_empty(self):
        assert load_latest_snapshots(ch_client=_FakeCH(rows=[])) == []

    def test_minutes_validation(self):
        """minutes 非正 → ValueError（调用方契约违例）。"""
        with pytest.raises(ValueError):
            load_latest_snapshots(ch_client=_FakeCH(), minutes=0)
