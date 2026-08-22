"""MOD-SIG-061 主线候选榜 单元测试（92号清单 §7.8 / 架构审查报告 §11.5 SEC-05，合成数据不触库）"""

from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare.mainline_candidates import (
    MainlineCandidatesConfig,
    MainlineCandidatesResult,
    compute_mainline_candidates,
    select_mainline_candidates,
)

D0 = date(2026, 5, 4)  # 合成序列起始日（连续自然日当交易日用，模块不校验周末）
SECTORS880 = [f"8805{i:02d}.SH" for i in range(1, 9)]  # 8 只 880 概念板块合成宇宙
IND0, IND1 = "881386.SH", "881394.SH"  # 881xxx 纯行业板（无 K 线，成分等权聚合）
MKT = "880001.SH"


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由返回合成行（不触库）。"""

    def __init__(self, sector_rows=None, constituent_rows=None, stock_rows=None, meta_rows=None, exc_on=None):
        self._sector = sector_rows or []
        self._constituent = constituent_rows or []
        self._stock = stock_rows or []
        self._meta = meta_rows or []
        self._exc_on = exc_on

    def execute(self, sql, params=None):
        if self._exc_on and self._exc_on in sql:
            raise RuntimeError(f"合成故障: {self._exc_on}")
        if "sector_constituent" in sql:
            return list(self._constituent)
        if "sector_meta" in sql:
            return list(self._meta)
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
    """等比日收益收盘价序列。"""
    out = [start]
    for _ in range(1, n):
        out.append(out[-1] * (1 + daily))
    return out


def _closes_accel(n: int, base: float, accel: float, start: float = 100.0) -> list[float]:
    """加速日收益收盘价序列（ret_i = base + accel×i）——RS 加速上行，RRG 稳定落领先象限。"""
    out = [start]
    for i in range(1, n):
        out.append(out[-1] * (1 + base + accel * i))
    return out


def _sector_rows(closes: dict[str, list[float]], amounts: dict[str, list[float]], n: int) -> list[tuple]:
    """合成板块 K 线行 (sector_code, trade_date, close, amount)，含 880001 市场指数腿。"""
    rows: list[tuple] = []
    for code, c_series in closes.items():
        for i, d in enumerate(_days(n)):
            rows.append((code, d, c_series[i], amounts[code][i]))
    return rows


def _stock_rows(stock_pct: dict[str, list[float]], stock_amt: dict[str, list[float]], n: int) -> list[tuple]:
    """合成个股 K 线行 (symbol_canonical, trade_date, close, amount, pct_change)（pct 单位=%）。"""
    rows: list[tuple] = []
    for sym, pcts in stock_pct.items():
        for i, d in enumerate(_days(n)):
            rows.append((sym, d, 100.0, stock_amt[sym][i], pcts[i]))
    return rows


CONSTITUENTS = [
    (IND0, "半导体", "STK_A1.SH"),
    (IND0, "半导体", "STK_A2.SH"),
    (IND0, "半导体", "STK_A3.SH"),
    (IND1, "券商", "STK_B1.SH"),
    (IND1, "券商", "STK_B2.SH"),
    ("880501.SH", "机器人", "STK_C1.SH"),
    ("880501.SH", "机器人", "STK_C2.SH"),
]


def _scenario_mainline(n: int = 70) -> _FakeCH:
    """健康主线合成场景：880501 每日加速领涨（连续领涨贯穿全窗），881386 温和加速跟随。

    宇宙 = 8×880 概念板 + 2×881 行业板（成分等权合成）；成交额常量（HHI 低分散）；
    上涨面 = 领涨+3 只 880 上行+IND0 上行 = 5/10；880501 RRG 加速→领先象限。
    """
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
    pct_ind0 = [0.6 + 0.01 * i for i in range(n)]
    stock_pct = {
        "STK_A1.SH": pct_ind0,
        "STK_A2.SH": list(pct_ind0),
        "STK_A3.SH": list(pct_ind0),
        "STK_B1.SH": [-0.6] * n,
        "STK_B2.SH": [-0.6] * n,
    }
    stock_amt = {sym: [5.0] * n for sym in stock_pct}
    return _FakeCH(
        sector_rows=_sector_rows(closes, amounts, n),
        constituent_rows=list(CONSTITUENTS),
        stock_rows=_stock_rows(stock_pct, stock_amt, n),
    )


# ---------- 纯函数评分核心（select_mainline_candidates） ----------


class TestSelectMainlineCandidates:
    def test_reason_labels_complete(self):
        """理由标签齐全：连续领涨/q3 前排/RRG 象限逐条命中，单维度不足门槛者出局。"""
        cands, no_mainline, ann = select_mainline_candidates(
            rotation_state="NEUTRAL_MIXED",
            leader_code="A",
            lead_streak=2,
            sector_streaks={"A": 2, "B": 0, "C": 0},
            q3_percentiles={"A": 0.90, "B": 0.85, "C": 0.50},
            rrg_quadrants={"A": "LAGGING", "B": "IMPROVING", "C": "LEADING"},
            sector_names={"A": "甲", "B": "乙", "C": "丙"},
        )
        assert no_mainline is False
        assert [c.sector_code for c in cands] == ["A", "B"]
        assert cands[0].score == 3
        assert cands[0].sector_name == "甲"
        assert cands[0].reasons == ["连续领涨2日", "q3动量前排（3日涨幅分位90%）"]
        assert cands[1].score == 2
        assert cands[1].reasons == ["q3动量前排（3日涨幅分位85%）", "RRG改善象限（提前布局）"]
        assert ann == []

    def test_healthy_mainline_leader_bonus(self):
        """健康主线态下当日领涨且 streak≥3 → +3 健康主线领涨理由。"""
        cands, _, _ = select_mainline_candidates(
            rotation_state="HEALTHY_MAINLINE",
            leader_code="A",
            lead_streak=4,
            sector_streaks={"A": 4},
            q3_percentiles={"A": 0.95},
            rrg_quadrants={"A": "LEADING"},
            sector_names={"A": "甲"},
        )
        assert cands[0].score == 5
        assert "健康主线领涨" in cands[0].reasons[0]
        assert "连续领涨4日" in cands[0].reasons[0]
        assert "RRG领先象限（接棒中）" in cands[0].reasons

    def test_no_mainline_chaos_empty(self):
        """无主线混沌（lead_streak<2）→ 空榜+注解，即使存在 q3/RRG 双优板块。"""
        cands, no_mainline, ann = select_mainline_candidates(
            rotation_state="NEUTRAL_MIXED",
            leader_code="A",
            lead_streak=1,
            sector_streaks={"A": 1},
            q3_percentiles={"A": 0.99},
            rrg_quadrants={"A": "LEADING"},
            sector_names={"A": "甲"},
        )
        assert cands == []
        assert no_mainline is True
        assert any("无主线" in a for a in ann)

    def test_no_qualified_candidates(self):
        """非混沌态但无板块过门槛 → 空榜+门槛注解（区分混沌态）。"""
        cands, no_mainline, ann = select_mainline_candidates(
            rotation_state="NEUTRAL_MIXED",
            leader_code="A",
            lead_streak=2,
            sector_streaks={"A": 2, "B": 0},
            q3_percentiles={"A": 0.50, "B": 0.40},
            rrg_quadrants={"A": None, "B": "LEADING"},
            sector_names={"A": "甲", "B": "乙"},
        )
        # A 连续领涨 2 日 → score 2 过门槛；剔除 A 场景：
        assert [c.sector_code for c in cands] == ["A"]
        cands2, _, ann2 = select_mainline_candidates(
            rotation_state="NEUTRAL_MIXED",
            leader_code="B",
            lead_streak=2,
            sector_streaks={"B": 2},
            q3_percentiles={"B": 0.10},
            rrg_quadrants={"B": None},
            sector_names={"B": "乙"},
        )
        # B 连续领涨 2 日（score 2）仍过门槛；真正的空榜：无领涨维度且无复合维度
        assert [c.sector_code for c in cands2] == ["B"]
        cands3, nm3, ann3 = select_mainline_candidates(
            rotation_state="DISAGREEMENT_PULLBACK",
            leader_code="C",
            lead_streak=3,
            sector_streaks={"C": 0, "D": 0},
            q3_percentiles={"C": 0.50, "D": 0.40},
            rrg_quadrants={"C": "WEAKENING", "D": "LAGGING"},
            sector_names={"C": "丙", "D": "丁"},
        )
        assert cands3 == []
        assert nm3 is False
        assert any("门槛" in a for a in ann3)

    def test_lead_streak_none_not_chaos(self):
        """lead_streak 缺失（None）不判混沌，纯复合维度可入榜。"""
        cands, no_mainline, _ = select_mainline_candidates(
            rotation_state=None,
            leader_code=None,
            lead_streak=None,
            sector_streaks={},
            q3_percentiles={"A": 0.9},
            rrg_quadrants={"A": "LEADING"},
            sector_names={"A": "甲"},
        )
        assert no_mainline is False
        assert [c.sector_code for c in cands] == ["A"]


# ---------- 端到端（_FakeCH 注入） ----------


class TestHealthyMainlinePipeline:
    def test_healthy_mainline_scenario(self):
        """健康主线合成场景：5 状态=HEALTHY_MAINLINE，领涨板块居首且理由链完整。"""
        n = 70
        result = compute_mainline_candidates(ch_client=_scenario_mainline(n))
        assert result.degraded is False
        assert result.date == _days(n)[-1].isoformat()
        assert result.rotation_state == "HEALTHY_MAINLINE"
        assert result.watch_score == pytest.approx(0.03)
        assert result.lead_streak is not None and result.lead_streak >= 3
        assert result.no_mainline_flag is False
        assert len(result.candidates) == 2

        top = result.candidates[0]
        assert top.sector_code == "880501.SH"
        assert top.sector_name == "机器人"  # 名称来自 sector_constituent（kline sector_name 空）
        assert top.lead_streak == result.lead_streak
        assert top.q3_percentile == pytest.approx(1.0)
        assert top.rrg_quadrant == "LEADING"
        assert any("健康主线领涨" in r for r in top.reasons)
        assert any("q3动量前排" in r for r in top.reasons)
        assert any("RRG领先象限" in r for r in top.reasons)

        second = result.candidates[1]
        assert second.sector_code == IND0  # 881xxx 行业板经成分等权聚合入榜
        assert second.sector_name == "半导体"
        assert second.score == 2
        assert second.reasons == ["q3动量前排（3日涨幅分位89%）", "RRG领先象限（接棒中）"]

    def test_trade_date_none_resolves_latest(self):
        """trade_date=None → 取 kline_sector_880 最新数据日（PIT 数据日口径）。"""
        n = 70
        result = compute_mainline_candidates(None, ch_client=_scenario_mainline(n))
        assert result.degraded is False
        assert result.date == _days(n)[-1].isoformat()

    def test_result_json_serializable(self):
        """frozen dataclass asdict → JSON 可序列化契约（落盘/展示消费）。"""
        import json

        result = compute_mainline_candidates(ch_client=_scenario_mainline(70))
        payload = asdict(result)
        assert isinstance(payload, dict)
        json.dumps(payload, ensure_ascii=False)


class TestNoMainlineChaos:
    def test_rotating_leaders_empty_board(self):
        """领涨每日轮换（streak 恒 1）→ 无主线混沌空榜+注解。"""
        n = 70
        closes = {MKT: [100.0] * n}
        for k, s in enumerate(SECTORS880):
            series = [100.0]
            for i in range(1, n):
                series.append(series[-1] * (1.02 if i % 8 == k else 1.0))
            closes[s] = series
        amounts = {code: [10.0] * n for code in [MKT] + SECTORS880}
        stock_pct = {sym: [0.0] * n for sym in ("STK_A1.SH", "STK_A2.SH", "STK_A3.SH", "STK_B1.SH", "STK_B2.SH")}
        stock_amt = {sym: [5.0] * n for sym in stock_pct}
        client = _FakeCH(
            sector_rows=_sector_rows(closes, amounts, n),
            constituent_rows=list(CONSTITUENTS),
            stock_rows=_stock_rows(stock_pct, stock_amt, n),
        )
        result = compute_mainline_candidates(_days(n)[-1], ch_client=client)
        assert result.degraded is False
        assert result.rotation_state == "NEUTRAL_MIXED"
        assert result.lead_streak == 1
        assert result.no_mainline_flag is True
        assert result.candidates == []
        assert any("无主线" in a for a in result.annotations)


# ---------- 降级同族 ----------


class TestDegradation:
    def test_all_data_missing_degraded(self):
        """主数据（板块 K 线 + 个股 K 线）全缺 → degraded=True 空榜不炸。"""
        result = compute_mainline_candidates("2026-08-20", ch_client=_FakeCH())
        assert result.degraded is True
        assert result.candidates == []
        assert result.notes

    def test_rrg_insufficient_history_degraded_dimension(self):
        """K 线 <62 日（数据积累期）→ RRG 维度整体降级留痕，其余维度照常出榜。"""
        n = 30
        closes = {MKT: [100.0] * n}
        closes["880501.SH"] = _closes_accel(n, 0.005, 0.0003)
        for k, s in enumerate(SECTORS880[1:]):
            closes[s] = _closes_const(n, 0.001 * (k + 1))
        amounts = {code: [10.0] * n for code in [MKT] + SECTORS880}
        client = _FakeCH(
            sector_rows=_sector_rows(closes, amounts, n),
            constituent_rows=[("880501.SH", "机器人", "STK_C1.SH")],
            stock_rows=[],
        )
        result = compute_mainline_candidates(_days(n)[-1], ch_client=client)
        assert result.degraded is False
        assert result.rotation_state == "HEALTHY_MAINLINE"
        assert result.candidates
        top = result.candidates[0]
        assert top.sector_code == "880501.SH"
        assert top.rrg_quadrant is None
        assert not any("RRG" in r for r in top.reasons)
        assert any("RRG" in note for note in result.notes)

    def test_stock_kline_missing_drops_881(self):
        """kline_daily 无数据 → 881xxx 行业合成降级留痕，宇宙收敛为 880 板块。"""
        n = 70
        client = _scenario_mainline(n)
        client._stock = []
        result = compute_mainline_candidates(_days(n)[-1], ch_client=client)
        assert result.degraded is False
        assert any("881xxx" in note for note in result.notes)
        assert all(c.sector_code.startswith("880") for c in result.candidates)

    def test_query_exception_degraded(self):
        """板块 K 线查询异常 → degraded=True（数据层异常不炸）。"""
        result = compute_mainline_candidates("2026-08-20", ch_client=_FakeCH(exc_on="kline_sector_880"))
        assert result.degraded is True
        assert result.candidates == []

    def test_880_without_kline_not_synthesized(self):
        """880xxx 有官方 K 线真源：成分在册但 K 线缺失的 880 板不按成分合成（防代理指数冒充官方），
        合成路径仅服务 881xxx 行业族（2026-08-22 数据实证裁定）。"""
        n = 70
        client = _scenario_mainline(n)
        # 追加一只有成分但无 K 线的 880 板（880599.SH）及其成分股 K 线
        client._constituent = list(client._constituent) + [("880599.SH", "伪概念", "STK_Z1.SH")]
        client._stock = list(client._stock) + [
            ("STK_Z1.SH", d, 100.0, 5.0, 9.9) for d in _days(n)  # 日涨 9.9%，若被合成必上榜
        ]
        result = compute_mainline_candidates(_days(n)[-1], ch_client=client)
        assert result.degraded is False
        assert all(c.sector_code != "880599.SH" for c in result.candidates)
        assert any("880xxx" in note for note in result.notes)

    def test_sector_meta_names_override_echo(self):
        """名称真源：成分表回显名（=代码）过滤，sector_meta 881xxx 真名接管；880 无名代码直出。"""
        n = 70
        client = _scenario_mainline(n)
        client._constituent = [(c, c, s) for c, _, s in CONSTITUENTS]  # 全部回显为代码
        client._meta = [("881386", "半导体")]  # meta 裸码真名
        result = compute_mainline_candidates(_days(n)[-1], ch_client=client)
        by_code = {c.sector_code: c for c in result.candidates}
        assert by_code[IND0].sector_name == "半导体"
        assert by_code["880501.SH"].sector_name == "880501.SH"  # 880 全库无名 → 代码直出

    def test_invalid_trade_date_raises(self):
        """trade_date 格式非法 → ValueError（调用方契约违例，fail-closed）。"""
        with pytest.raises(ValueError):
            compute_mainline_candidates("2026/08/20", ch_client=_FakeCH())

    def test_result_type_contract(self):
        """返回 MainlineCandidatesResult 且 candidates/annotations/notes 为 list。"""
        result = compute_mainline_candidates(ch_client=_scenario_mainline(70))
        assert isinstance(result, MainlineCandidatesResult)
        assert isinstance(result.candidates, list)
        assert isinstance(result.annotations, list)
        assert isinstance(result.notes, list)
