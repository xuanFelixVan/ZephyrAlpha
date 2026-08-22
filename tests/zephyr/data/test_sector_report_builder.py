"""MOD-L00-009 板块盘后全景报告器 单元测试（92号清单 §7.5 / 架构审查报告 §11.5 SEC-01，合成数据不触库）"""

import json
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.data.sector_report_builder import (
    SectorReport,
    build_sector_report,
    main,
    report_to_dict,
    write_report,
)

D0 = date(2026, 5, 4)  # 合成序列起始日（连续自然日当交易日用，模块不校验周末）
SECTORS880 = [f"8805{i:02d}.SH" for i in range(1, 9)]
IND0, IND1 = "881386.SH", "881394.SH"  # 881xxx 纯行业板（无 K 线，成分等权聚合）
MKT = "880001.SH"
N = 30  # 合成窗长（RRG 维度按数据积累期降级，榜单/资金流/梯队/状态维度不受影响）


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由返回合成行（不触库）。"""

    def __init__(
        self,
        sector_rows=None,
        constituent_rows=None,
        stock_rows=None,
        mf_today_rows=None,
        mf_window_rows=None,
        limit_rows=None,
        stk_limit_rows=None,
        snapshot_rows=None,
        meta_rows=None,
        exc_on=None,
    ):
        self._sector = sector_rows or []
        self._constituent = constituent_rows or []
        self._stock = stock_rows or []
        self._mf_today = mf_today_rows or []
        self._mf_window = mf_window_rows or []
        self._limit = limit_rows or []
        self._stk_limit = stk_limit_rows or []
        self._snapshot = snapshot_rows or []
        self._meta = meta_rows or []
        self._exc_on = exc_on

    def execute(self, sql, params=None):
        if self._exc_on and self._exc_on in sql:
            raise RuntimeError(f"合成故障: {self._exc_on}")
        if "sector_snapshot" in sql:
            return list(self._snapshot)
        if "sector_constituent" in sql:
            return list(self._constituent)
        if "sector_meta" in sql:
            return list(self._meta)
        if "super_large" in sql:
            return list(self._mf_today)
        if "money_flow" in sql:
            return list(self._mf_window)
        if "limit_up_down" in sql:
            return list(self._limit)
        if "stk_limit" in sql:
            return list(self._stk_limit)
        if "max(trade_date)" in sql:
            return [(max(r[1] for r in self._sector),)] if self._sector else [(None,)]
        if "kline_sector_880" in sql:
            return list(self._sector)
        if "kline_daily" in sql:
            return list(self._stock)
        return []


def _days(n: int) -> list[date]:
    return [D0 + timedelta(days=i) for i in range(n)]


def _closes_const(n: int, daily: float, start: float = 100.0) -> list[float]:
    out = [start]
    for _ in range(1, n):
        out.append(out[-1] * (1 + daily))
    return out


def _closes_accel(n: int, base: float, accel: float, start: float = 100.0) -> list[float]:
    out = [start]
    for i in range(1, n):
        out.append(out[-1] * (1 + base + accel * i))
    return out


def _sector_rows(closes: dict[str, list[float]], amounts: dict[str, list[float]], n: int) -> list[tuple]:
    rows: list[tuple] = []
    for code, c_series in closes.items():
        for i, d in enumerate(_days(n)):
            rows.append((code, d, c_series[i], amounts[code][i]))
    return rows


def _stock_rows(
    stock_pct: dict[str, list[float]],
    stock_amt: dict[str, list[float]],
    n: int,
    stock_close_today: dict[str, float] | None = None,
) -> list[tuple]:
    """(symbol_canonical, trade_date, close, amount, pct_change)（pct 单位=%；close 默认 100 平走）。"""
    rows: list[tuple] = []
    for sym, pcts in stock_pct.items():
        for i, d in enumerate(_days(n)):
            close = 100.0
            if stock_close_today and i == n - 1:
                close = stock_close_today.get(sym, 100.0)
            rows.append((sym, d, close, stock_amt[sym][i], pcts[i]))
    return rows


CONSTITUENTS = [
    (IND0, "半导体", "STK_A1.SH"),
    (IND0, "半导体", "STK_A2.SH"),
    (IND0, "半导体", "STK_A3.SH"),
    (IND1, "券商", "STK_B1.SH"),
    (IND1, "券商", "STK_B2.SH"),
    ("880501.SH", "机器人", "STK_C1.SH"),
    ("880501.SH", "机器人", "STK_C2.SH"),
    ("880502.SH", "磷化工", "STK_D1.SH"),
]

# 个股资金流（当日五层；单位：万元，2026-08-22 实证口径——schema COMMENT 标"元"与实值不符）
MF_TODAY = [
    ("STK_A1.SH", 1e4, 5e3, 2e3, -1e3, -5e2),
    ("STK_A2.SH", 2e4, 1e4, 5e3, 0.0, 0.0),
    ("STK_A3.SH", 0.0, 0.0, 0.0, 1e3, 5e2),
    ("STK_B1.SH", -5e3, -2e3, -1e3, 1e3, 5e2),
    ("STK_B2.SH", -1e4, 0.0, 0.0, 0.0, 0.0),
    ("STK_C1.SH", 5e3, 2e3, 1e3, -5e2, -2e2),
    ("STK_D1.SH", 1e4, 0.0, 0.0, 0.0, 0.0),
]


def _mf_window_rows(n: int) -> list[tuple]:
    """虹吸历史序列窗（近 5 日主力净流入小额交替，万元口径，不构成虹吸）。"""
    rows: list[tuple] = []
    syms = ["STK_A1.SH", "STK_A2.SH", "STK_A3.SH", "STK_B1.SH", "STK_B2.SH", "STK_C1.SH", "STK_D1.SH"]
    for i, d in enumerate(_days(n)[-5:]):
        for si, sym in enumerate(syms):
            rows.append((d, sym, 1e3 if (i + si) % 2 == 0 else -1e3))
    return rows


def _base_fixture(n: int = N) -> dict:
    """Top10 榜/资金流基础场景：880501 今日 +3% 领涨，881386 成分等权 +1.1667% 居次。"""
    closes = {MKT: [100.0] * n}
    closes["880501.SH"] = [100.0] * (n - 1) + [103.0]
    closes["880502.SH"] = [100.0] * (n - 1) + [101.0]
    closes["880503.SH"] = [100.0] * (n - 1) + [97.5]
    amounts = {
        MKT: [100.0] * n,
        "880501.SH": [20.0] * n,
        "880502.SH": [30.0] * n,
        "880503.SH": [10.0] * n,
    }
    stock_pct = {
        "STK_A1.SH": [0.0] * (n - 1) + [2.5],
        "STK_A2.SH": [0.0] * (n - 1) + [1.0],
        "STK_A3.SH": [0.0] * (n - 1) + [0.0],
        "STK_B1.SH": [0.0] * (n - 1) + [-1.0],
        "STK_B2.SH": [0.0] * (n - 1) + [-3.0],
        "STK_C1.SH": [0.0] * n,
        "STK_C2.SH": [0.0] * n,
        "STK_D1.SH": [0.0] * n,
    }
    stock_amt = {
        "STK_A1.SH": [4.0] * n,
        "STK_A2.SH": [3.0] * n,
        "STK_A3.SH": [3.0] * n,
        "STK_B1.SH": [5.0] * n,
        "STK_B2.SH": [5.0] * n,
        "STK_C1.SH": [10.0] * n,
        "STK_C2.SH": [10.0] * n,
        "STK_D1.SH": [15.0] * n,
    }
    snapshot = [
        ("880501.SH", 103.0, 100.0, 102.0, 20.0, 11.0, 9.0, _days(n)[-1]),
        ("880502.SH", 101.0, 100.0, 100.5, 30.0, 15.0, 15.0, _days(n)[-1]),
        ("880503.SH", 97.5, 100.0, 99.0, 10.0, 6.0, 4.0, _days(n)[-1]),
    ]
    return {
        "sector_rows": _sector_rows(closes, amounts, n),
        "constituent_rows": list(CONSTITUENTS),
        "stock_rows": _stock_rows(stock_pct, stock_amt, n),
        "mf_today_rows": list(MF_TODAY),
        "mf_window_rows": _mf_window_rows(n),
        "snapshot_rows": snapshot,
    }


# ---------- Top10 榜聚合 + 资金流聚合 ----------


class TestTopLadderAndMoneyFlow:
    def test_ladder_order_and_881_equal_weight(self):
        """Top10 榜：按当日涨幅降序；881xxx 行业收益=成分股 pct_change 等权均值；市场指数剔除。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**_base_fixture(n)))
        assert report.degraded is False
        codes = [e.sector_code for e in report.top_sectors]
        assert codes == ["880501.SH", IND0, "880502.SH", IND1, "880503.SH"]
        assert MKT not in codes
        e0, e1 = report.top_sectors[0], report.top_sectors[1]
        assert e0.change_pct == pytest.approx(0.03)
        assert e1.change_pct == pytest.approx((2.5 + 1.0 + 0.0) / 3 / 100)
        assert e0.rank == 1 and e1.rank == 2

    def test_money_flow_five_layer_aggregation(self):
        """资金流聚合：money_flow 五层净流入 × sector_constituent 逐板块求和（万元→亿）。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**_base_fixture(n)))
        by_code = {e.sector_code: e for e in report.top_sectors}
        semi = by_code[IND0]
        assert semi.main_net_inflow == pytest.approx(3.0)  # (1+2+0)e8 元
        assert semi.super_large_net_inflow == pytest.approx(1.5)
        assert semi.large_net_inflow == pytest.approx(0.7)
        assert semi.medium_net_inflow == pytest.approx(0.0)
        assert semi.small_net_inflow == pytest.approx(0.0)
        assert by_code[IND1].main_net_inflow == pytest.approx(-1.5)
        assert by_code["880501.SH"].main_net_inflow == pytest.approx(0.5)  # C2 缺席按缺失剔除
        assert by_code["880503.SH"].main_net_inflow is None  # 无成分映射 → 缺数据非零
        assert report.availability["money_flow"] == "ok"

    def test_names_amounts_constituents_and_scores(self):
        """名称映射/成交额/成分数/momentum/ranking 附挂（快照外的 881xxx ranking=None）。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**_base_fixture(n)))
        by_code = {e.sector_code: e for e in report.top_sectors}
        assert by_code[IND0].sector_name == "半导体"
        assert by_code[IND0].amount == pytest.approx(10.0)  # 成分 amount 合计 4+3+3
        assert by_code[IND0].constituent_count == 3
        assert by_code["880503.SH"].sector_name == "880503.SH"  # 无成分 → 回退代码
        assert by_code["880503.SH"].constituent_count == 0
        assert by_code["880501.SH"].ranking_score is not None  # 快照覆盖
        assert by_code[IND0].ranking_score is None  # 881xxx 不在 880 快照
        assert all(e.momentum_score is not None for e in report.top_sectors)
        assert report.availability["ranking"] == "ok"
        assert report.availability["momentum"] == "ok"
        assert report.availability["siphon"] == "ok"
        assert report.siphon_flag is False

    def test_trade_date_none_resolves_latest(self):
        """trade_date=None → 取 kline_sector_880 最新数据日。"""
        n = N
        report = build_sector_report(None, ch_client=_FakeCH(**_base_fixture(n)))
        assert report.degraded is False
        assert report.date == _days(n)[-1].isoformat()

    def test_sector_meta_names_override_echo(self):
        """名称真源：成分表回显名（=代码）过滤，sector_meta 881xxx 真名接管；880 无名代码直出。"""
        n = N
        data = _base_fixture(n)
        data["constituent_rows"] = [(c, c, s) for c, _, s in CONSTITUENTS]  # 全部回显为代码
        data["meta_rows"] = [("881386", "半导体"), ("881394", "券商")]  # meta 裸码真名
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**data))
        by_code = {e.sector_code: e for e in report.top_sectors}
        assert by_code[IND0].sector_name == "半导体"
        assert by_code[IND1].sector_name == "券商"
        assert by_code["880501.SH"].sector_name == "880501.SH"  # 880 全库无名 → 代码直出


# ---------- 涨停梯队（stk_limit/limit_up_down 聚合） ----------


class TestLimitLadder:
    def _fixture_with_ladder(self, n: int) -> dict:
        data = _base_fixture(n)
        data["limit_rows"] = [
            ("STK_A1.SH", _days(n)[-2], "涨停"),
            ("STK_A1.SH", _days(n)[-1], "涨停"),  # 二连板
            ("STK_C1.SH", _days(n)[-1], "涨停"),
            ("STK_B1.SH", _days(n)[-1], "跌停"),  # 跌停腿不入梯队
        ]
        data["stk_limit_rows"] = [
            ("STK_A2.SH", 10.0),
            ("STK_A3.SH", 10.0),
            ("STK_C2.SH", 10.0),
        ]
        # 重造个股行：A2/C2 今日收盘=涨停价（并集路径），A3 收盘低于涨停价（不计）
        base = _base_fixture(n)
        data["stock_rows"] = _stock_rows(
            {sym: [r[4] for r in base["stock_rows"] if r[0] == sym] for sym in
             {r[0] for r in base["stock_rows"]}},
            {sym: [r[3] for r in base["stock_rows"] if r[0] == sym] for sym in
             {r[0] for r in base["stock_rows"]}},
            n,
            stock_close_today={"STK_A2.SH": 10.0, "STK_A3.SH": 9.5, "STK_C2.SH": 10.0},
        )
        return data

    def test_ladder_tiers_and_streak(self):
        """梯队：连板高度（stk 序列 trailing 连续）+ 一板/二板/三板+ 分档 + 板块归属聚合。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**self._fixture_with_ladder(n)))
        ladder = report.limit_ladder
        assert ladder is not None
        assert ladder.total_limit_up == 4  # A1/A2/C1/C2（A3 触价未收封不计）
        assert ladder.tier1 == 3
        assert ladder.tier2 == 1
        assert ladder.tier3_plus == 0
        assert ladder.max_streak == 2
        by_code = {s.sector_code: s for s in ladder.sectors}
        semi = by_code[IND0]
        assert semi.limit_up_count == 2  # A1（limit_up_down）+A2（stk_limit 并集）
        assert semi.tier1 == 1 and semi.tier2 == 1 and semi.tier3_plus == 0
        assert semi.max_streak == 2
        assert semi.limit_up_ratio == pytest.approx(2 / 3)
        robot = by_code["880501.SH"]
        assert robot.limit_up_count == 2  # C1+C2
        assert robot.tier1 == 2 and robot.max_streak == 1

    def test_ladder_attached_to_top_entries_and_strength(self):
        """梯队附挂 Top10 榜：涨停比（sector_breadth）+ evaluate_strength 结构强度（sector_analyzer）。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**self._fixture_with_ladder(n)))
        by_code = {e.sector_code: e for e in report.top_sectors}
        robot = by_code["880501.SH"]
        assert robot.limit_up_count == 2
        assert robot.limit_up_ratio == pytest.approx(1.0)
        assert robot.breadth_label == "极强"  # 涨停比 >10%
        # evaluate_strength：涨停 2 家(+20) + 无二/三板(+10) + 指数 +3%≥3%(+30) = 60 → 中
        assert robot.strength_score == pytest.approx(60.0)
        assert robot.strength_status == "中"
        semi = by_code[IND0]
        # 涨停 2(+20) + 二板>0(+20) + 指数 +1.17%∈[0,3%)(+15) = 55 → 中
        assert semi.strength_score == pytest.approx(55.0)
        assert report.availability["limit_ladder"] == "ok"

    def test_empty_limit_tables_is_zero_ladder_not_unavailable(self):
        """无涨停日=合法零梯队（availability=ok），非缺数据。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**_base_fixture(n)))
        assert report.limit_ladder is not None
        assert report.limit_ladder.total_limit_up == 0
        assert report.availability["limit_ladder"] == "ok"


# ---------- 5 状态标签 + 主线候选嵌入 ----------


class TestRotationStateAndMainline:
    def _healthy_fixture(self, n: int) -> dict:
        closes = {MKT: [100.0] * n}
        closes["880501.SH"] = _closes_accel(n, 0.005, 0.0003)
        closes["880502.SH"] = _closes_const(n, 0.004)
        closes["880503.SH"] = _closes_const(n, 0.002)
        closes["880504.SH"] = _closes_const(n, 0.001)
        closes["880505.SH"] = _closes_const(n, -0.001)
        closes["880506.SH"] = _closes_const(n, -0.002)
        closes["880507.SH"] = _closes_const(n, -0.003)
        closes["880508.SH"] = _closes_const(n, -0.004)
        amounts = {code: [10.0] * n for code in [MKT] + SECTORS880}
        stock_pct = {sym: [0.0] * n for sym in
                     ("STK_A1.SH", "STK_A2.SH", "STK_A3.SH", "STK_B1.SH", "STK_B2.SH",
                      "STK_C1.SH", "STK_C2.SH", "STK_D1.SH")}
        stock_amt = {sym: [5.0] * n for sym in stock_pct}
        return {
            "sector_rows": _sector_rows(closes, amounts, n),
            "constituent_rows": list(CONSTITUENTS),
            "stock_rows": _stock_rows(stock_pct, stock_amt, n),
        }

    def test_healthy_mainline_state_label(self):
        """5 状态标签（sector_rotation_state 输出）：HEALTHY_MAINLINE + watch_score +0.03。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**self._healthy_fixture(n)))
        assert report.degraded is False
        assert report.rotation_state == "HEALTHY_MAINLINE"
        assert report.watch_score == pytest.approx(0.03)
        assert report.lead_streak is not None and report.lead_streak >= 3
        assert report.availability["rotation_state"] == "ok"

    def test_mainline_embedded(self):
        """主线候选（调 SEC-05 模块）：候选榜嵌入报告，领涨板块居首。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**self._healthy_fixture(n)))
        assert report.availability["mainline"] == "ok"
        assert report.mainline is not None
        assert report.mainline.candidates
        assert report.mainline.candidates[0].sector_code == "880501.SH"
        assert report.top_sectors[0].sector_code == "880501.SH"


# ---------- 缺数据降级（单维度 unavailable 不炸整体） ----------


class TestDegradation:
    def test_money_flow_exception_degrades_flow_and_siphon(self):
        """money_flow 查询异常 → 资金流/虹吸两维度 unavailable，榜单/梯队照常。"""
        n = N
        report = build_sector_report(
            _days(n)[-1], ch_client=_FakeCH(exc_on="money_flow", **self._base(n))
        )
        assert report.degraded is False
        assert report.availability["money_flow"] == "unavailable"
        assert report.availability["siphon"] == "unavailable"
        assert report.siphon_flag is False
        assert all(e.main_net_inflow is None for e in report.top_sectors)
        assert len(report.top_sectors) == 5  # 榜单不受影响
        assert any("money_flow" in note for note in report.notes)

    def _base(self, n: int) -> dict:
        return _base_fixture(n)

    def test_snapshot_missing_degrades_ranking(self):
        """sector_snapshot 无数据 → ranking 维度 unavailable，ranking_score=None。"""
        n = N
        data = _base_fixture(n)
        data["snapshot_rows"] = []
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**data))
        assert report.degraded is False
        assert report.availability["ranking"] == "unavailable"
        assert all(e.ranking_score is None for e in report.top_sectors)

    def test_snapshot_stale_date_degrades_ranking(self):
        """快照最新时间戳非报告日（历史回跑）→ ranking 维度 unavailable 留痕。"""
        n = N
        data = _base_fixture(n)
        data["snapshot_rows"] = [
            (r[0], r[1], r[2], r[3], r[4], r[5], r[6], _days(n)[-2]) for r in data["snapshot_rows"]
        ]
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**data))
        assert report.availability["ranking"] == "unavailable"
        assert any("快照" in note for note in report.notes)

    def test_sector_kline_missing_falls_back_to_881(self):
        """880xxx K 线缺失 → 宇宙收敛为 881xxx 行业合成，报告仍出（notes 留痕）。"""
        n = N
        data = _base_fixture(n)
        data["sector_rows"] = []
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**data))
        assert report.degraded is False
        assert report.top_sectors
        assert all(e.sector_code.startswith("881") for e in report.top_sectors)
        assert any("880xxx" in note for note in report.notes)

    def test_all_data_missing_degraded(self):
        """板块全集为空 → degraded=True，维度全 unavailable。"""
        report = build_sector_report("2026-08-20", ch_client=_FakeCH())
        assert report.degraded is True
        assert report.top_sectors == []
        assert all(v == "unavailable" for v in report.availability.values())
        assert report.notes

    def test_invalid_trade_date_raises(self):
        """trade_date 格式非法 → ValueError（调用方契约违例，fail-closed）。"""
        with pytest.raises(ValueError):
            build_sector_report("2026/08/20", ch_client=_FakeCH())


# ---------- 落盘 + CLI 摘要 ----------


class TestReportIO:
    def test_report_to_dict_json_serializable(self):
        """结构化 dict：asdict 嵌套展开 + JSON 可序列化契约。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**_base_fixture(n)))
        payload = report_to_dict(report)
        assert isinstance(payload, dict)
        assert payload["date"] == _days(n)[-1].isoformat()
        assert payload["top_sectors"][0]["sector_code"] == "880501.SH"
        json.dumps(payload, ensure_ascii=False)
        assert isinstance(report, SectorReport)
        assert asdict(report) == payload

    def test_write_report_file(self, tmp_path):
        """落报告文件：sector_report_YYYYMMDD.json 写入指定目录并可回读。"""
        n = N
        report = build_sector_report(_days(n)[-1], ch_client=_FakeCH(**_base_fixture(n)))
        path = write_report(report, tmp_path)
        assert path.name == f"sector_report_{_days(n)[-1]:%Y%m%d}.json"
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["date"] == _days(n)[-1].isoformat()
        assert loaded["top_sectors"]

    def test_cli_main_writes_and_prints_summary(self, tmp_path, capsys):
        """CLI：python -m zephyr.data.sector_report_builder --date …… → rc=0 + 落盘 + 中文摘要。"""
        n = N
        d_str = _days(n)[-1].isoformat()
        rc = main(["--date", d_str, "--out-dir", str(tmp_path)], ch_client=_FakeCH(**_base_fixture(n)))
        assert rc == 0
        assert (tmp_path / f"sector_report_{_days(n)[-1]:%Y%m%d}.json").is_file()
        out = capsys.readouterr().out
        assert "板块盘后全景报告" in out
        assert "880501.SH" in out
        assert "涨停梯队" in out
        assert "主线候选" in out

    def test_cli_main_no_write(self, tmp_path):
        """--no-write：只打印不落盘。"""
        n = N
        rc = main(
            ["--date", _days(n)[-1].isoformat(), "--out-dir", str(tmp_path), "--no-write"],
            ch_client=_FakeCH(**_base_fixture(n)),
        )
        assert rc == 0
        assert not list(tmp_path.glob("sector_report_*.json"))
