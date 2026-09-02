"""MOD-SIG-060 板块分歧度与轮动速度计+SEC-03 标定器 单元测试（44号备忘录 §9.13/§9.2c，合成数据不触库）"""

import json
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare import sector_divergence as mod
from zephyr.signal_ashare.sector_divergence import (
    SectorDivergenceConfig,
    compute_sector_divergence,
    load_sector_attribute_labels,
)

D0 = date(2026, 8, 3)  # 合成序列起始日（连续自然日当交易日用，模块不校验周末）
SECTORS = [f"8805{i:02d}.SH" for i in range(1, 9)]  # 8 板块合成宇宙
MKT = "880001.SH"


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由返回合成行（不触库）。"""

    def __init__(
        self,
        sector_rows=None,
        constituent_rows=None,
        moneyflow_rows=None,
        stock_rows=None,
        limit_rows=None,
        lhb_rows=None,
        breadth_rows=None,
        exc_on: str | None = None,
    ):
        self._sector = sector_rows or []
        self._constituent = constituent_rows or []
        self._mf = moneyflow_rows or []
        self._stock = stock_rows or []
        self._limit = limit_rows or []
        self._lhb = lhb_rows or []
        self._breadth = breadth_rows or []
        self._exc_on = exc_on

    def execute(self, sql, params=None):
        if self._exc_on and self._exc_on in sql:
            raise RuntimeError(f"合成故障: {self._exc_on}")
        if "countIf" in sql:
            return list(self._breadth)
        if "stk_limit" in sql:
            return list(self._limit)
        if "dragon_tiger_seat" in sql:
            return list(self._lhb)
        if "sector_constituent" in sql:
            return list(self._constituent)
        if "money_flow" in sql:
            return list(self._mf)
        if "max(trade_date)" in sql:
            return [(max(r[1] for r in self._sector),)] if self._sector else [(None,)]
        if "kline_sector_880" in sql:
            return list(self._sector)
        if "kline_daily" in sql:
            return list(self._stock)
        return []


def _days(n: int) -> list[date]:
    return [D0 + timedelta(days=i) for i in range(n)]


def _sector_rows(closes: dict[str, list[float]], amounts: dict[str, list[float]], n: int) -> list[tuple]:
    """合成板块 K 线行（含 880001 市场指数腿，closes/amounts 按代码给等长序列）。"""
    rows: list[tuple] = []
    for code in [MKT] + SECTORS:
        c_series = closes[code]
        a_series = amounts[code]
        for i, d in enumerate(_days(n)):
            rows.append((code, d, c_series[i], a_series[i]))
    return rows


def _flat(n: int, v: float = 100.0) -> list[float]:
    return [v] * n


def _base_closes(n: int) -> dict[str, list[float]]:
    """基准：全板块平走 100（收益恒 0）。"""
    return {code: _flat(n) for code in [MKT] + SECTORS}


def _base_amounts(n: int, v: float = 10.0) -> dict[str, list[float]]:
    return {code: [v] * n for code in [MKT] + SECTORS}


# ---------- 板块族标签 loader ----------


class TestLabelsLoader:
    def test_load_real_config(self):
        """真源 yaml 落盘可读：防御族含银行/保险/公用/煤炭，进攻族含科技两件+券商。"""
        labels = load_sector_attribute_labels()
        assert "881386.SH" in labels.defensive_boards  # 银行
        assert "881395.SH" in labels.defensive_boards  # 保险
        assert "881459.SH" in labels.defensive_boards  # 公用(电力)
        assert "881002.SH" in labels.defensive_boards  # 煤炭
        assert "881319.SH" in labels.offensive_boards  # 半导体
        assert "881338.SH" in labels.offensive_boards  # 通信设备
        assert "881394.SH" in labels.offensive_boards  # 券商
        assert labels.board_names["881386.SH"] == "银行"
        assert labels.rs_sigma_window == 20

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_sector_attribute_labels("nonexistent_dir/sector_attribute_labels.yaml")

    def test_bad_structure_raises(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("families:\n  defensive:\n    boards: []\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_sector_attribute_labels(p)


# ---------- a) 5 状态消费接入（合成板块序列五状态各一） ----------


def _run_state_scenario(closes, amounts, n=7):
    client = _FakeCH(sector_rows=_sector_rows(closes, amounts, n))
    cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")  # rs 维度随个股缺失降级，隔离断言
    return compute_sector_divergence(_days(n)[-1], ch_client=client, config=cfg)


class TestRotationStateConsumption:
    def test_consensus_climax(self):
        """高集中(>0.30)+普涨(>0.70) → CONSENSUS_CLIMAX + 见顶风险标记。"""
        n = 7
        closes = _base_closes(n)
        for s in SECTORS[:7]:
            closes[s][-1] = 101.0  # 7/8 上涨
        closes[SECTORS[7]][-1] = 99.0
        amounts = _base_amounts(n)
        amounts[SECTORS[0]] = [100.0] * n  # 头部集中
        result = _run_state_scenario(closes, amounts, n)
        assert result.degraded is False
        assert result.rotation_state == "CONSENSUS_CLIMAX"
        assert result.top_risk_flag is True
        assert any("见顶" in a for a in result.annotations)

    def test_distribution_risk(self):
        """领涨放量滞涨+集中(>0.25) → DISTRIBUTION_RISK（优先级最高）。"""
        n = 7
        closes = _base_closes(n)
        closes[SECTORS[0]] = [100, 100, 100, 100, 100, 110.0, 111.0]  # 昨 +10%，今 +0.9%<5%
        for s in SECTORS[1:]:
            closes[s][-1] = 99.5  # 其余微跌，领涨=板块0
        amounts = _base_amounts(n)
        amounts[SECTORS[0]] = [10, 10, 10, 10, 10, 10.0, 100.0]  # 今日额 > 5日均×1.2
        result = _run_state_scenario(closes, amounts, n)
        assert result.rotation_state == "DISTRIBUTION_RISK"
        assert result.top_risk_flag is True

    def test_healthy_mainline(self):
        """同一板块连涨 3+ 日+低集中(<0.20) → HEALTHY_MAINLINE，无见顶标记。"""
        n = 7
        closes = _base_closes(n)
        for i in (4, 5, 6):
            closes[SECTORS[0]][i] = closes[SECTORS[0]][i - 1] * 1.01  # 板块0 连涨
        for s in SECTORS[1:5]:
            closes[s][-1] = closes[s][-2] * 1.001
        for s in SECTORS[5:]:
            closes[s][-1] = closes[s][-2] * 0.999
        result = _run_state_scenario(closes, _base_amounts(n), n)
        assert result.rotation_state == "HEALTHY_MAINLINE"
        assert result.top_risk_flag is False
        assert result.lead_streak is not None and result.lead_streak >= 3

    def test_disagreement_pullback(self):
        """涨跌严重分化(<0.40)+头部集中(>0.20) → DISAGREEMENT_PULLBACK（观察，不加权）。"""
        n = 7
        closes = _base_closes(n)
        for s in SECTORS[:3]:
            closes[s][-1] = 101.0
        for s in SECTORS[3:]:
            closes[s][-1] = 99.0  # 5/8 下跌 → up_ratio=0.375
        amounts = _base_amounts(n)
        amounts[SECTORS[0]] = [50.0] * n  # hhi≈0.2014>0.20
        result = _run_state_scenario(closes, amounts, n)
        assert result.rotation_state == "DISAGREEMENT_PULLBACK"
        assert result.top_risk_flag is False

    def test_neutral_mixed(self):
        """涨跌互现+低集中+领涨切换 → NEUTRAL_MIXED（默认态）。"""
        n = 7
        closes = _base_closes(n)
        for s in SECTORS[:4]:
            closes[s][-1] = closes[s][-2] * 1.005
        for s in SECTORS[4:]:
            closes[s][-1] = closes[s][-2] * 0.995
        closes[SECTORS[1]][-1] = closes[SECTORS[1]][-2] * 1.02  # 今日领涨=板块1（昨日并列第一=板块0）
        result = _run_state_scenario(closes, _base_amounts(n), n)
        assert result.rotation_state == "NEUTRAL_MIXED"
        assert result.top_risk_flag is False


# ---------- b) 电风扇速度计 ----------


def _velocity_fixture(n: int, fan_today: bool) -> tuple:
    """合成速度计场景：fan_today=True → 历史排名稳定今日全反转；False → 历史剧烈今日稳定。"""
    closes = _base_closes(n)
    amounts = _base_amounts(n)
    for i in range(1, n):
        for si, s in enumerate(SECTORS):
            if fan_today:
                # 历史：板块序固定（日收益按代码序递增）；今日：完全反转
                r = (si + 1) * 0.001 if i < n - 1 else (len(SECTORS) - si) * 0.001
            else:
                # 历史：奇偶日排名互换（高速度）；最后 6 日固定（今日 vs t-5 同序 → 速度 0）
                rev = i % 2 == 1 and i < n - 6
                r = ((len(SECTORS) - si) if rev else (si + 1)) * 0.001
            closes[s][i] = closes[s][i - 1] * (1 + r)
    return closes, amounts


class TestRotationVelocity:
    def test_fan_market_and_no_mainline(self):
        """速度计 250 分位>0.75 → 电风扇行情；streak<2 → 无主线混沌；Top3 全换 → 一日游。"""
        n = 66
        closes, amounts = _velocity_fixture(n, fan_today=True)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1], ch_client=_FakeCH(sector_rows=_sector_rows(closes, amounts, n)), config=cfg
        )
        assert result.rotation_velocity == pytest.approx(4.0)  # 8 元序反转 mean|Δrank|=4
        assert result.velocity_percentile == pytest.approx(0.99167, abs=1e-4)  # 中秩 (59+60)/2/60
        assert result.fan_market_flag is True
        assert result.lead_streak == 1
        assert result.no_mainline_flag is True
        assert result.top3_overlap == pytest.approx(0.0)
        assert result.one_day_ecology is True

    def test_calm_market_not_fan(self):
        """历史高速度+今日稳定 → 今日分位低，不触发电风扇/无主线。"""
        n = 66
        closes, amounts = _velocity_fixture(n, fan_today=False)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1], ch_client=_FakeCH(sector_rows=_sector_rows(closes, amounts, n)), config=cfg
        )
        assert result.rotation_velocity == pytest.approx(0.0)
        assert result.velocity_percentile is not None and result.velocity_percentile < 0.75
        assert result.fan_market_flag is False
        assert result.no_mainline_flag is False
        assert result.one_day_ecology is False

    def test_velocity_min_periods_degraded(self):
        """速度计样本 <60 日守卫 → velocity_percentile=None 降级（原值仍出）。"""
        n = 10
        closes, amounts = _velocity_fixture(n, fan_today=True)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1], ch_client=_FakeCH(sector_rows=_sector_rows(closes, amounts, n)), config=cfg
        )
        assert result.rotation_velocity is not None
        assert result.velocity_percentile is None
        assert result.fan_market_flag is False
        assert any("速度计分位窗" in note for note in result.notes)


# ---------- c) 虹吸态消费 ----------


def _siphon_fixture(n: int, extreme_today: bool):
    """合成虹吸场景：成分每板块 2 股；extreme_today → 今日头部成交额/净流入极端集中。"""
    closes = _base_closes(n)
    amounts: dict[str, list[float]] = {}
    for si, s in enumerate(SECTORS):
        amounts[s] = [10.0 + ((i + si) % 3) for i in range(n)]  # 历史轻微波动（σ>0）
    amounts[MKT] = _flat(n)
    constituents: list[tuple] = []
    mf: list[tuple] = []
    for si, s in enumerate(SECTORS):
        stocks = [f"STK{si}A.SH", f"STK{si}B.SH"]
        for st in stocks:
            constituents.append((s, st))
        for i, d in enumerate(_days(n)):
            for st in stocks:
                mf.append((d, st, 1.0 if (i + si) % 2 == 0 else -1.0))
    if extreme_today:
        amounts[SECTORS[0]][-1] = 1000.0
        mf = [r for r in mf if not (r[0] == _days(n)[-1] and r[1].startswith("STK0"))]
        mf.append((_days(n)[-1], "STK0A.SH", 500.0))
        mf.append((_days(n)[-1], "STK0B.SH", 500.0))
    return _sector_rows(closes, amounts, n), constituents, mf


class TestSiphon:
    def test_extreme_concentration_triggers(self):
        """头部成交额/净流入极端集中 → 虹吸态 z>1.5σ 触发。"""
        n = 10
        sector_rows, constituents, mf = _siphon_fixture(n, extreme_today=True)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1],
            ch_client=_FakeCH(sector_rows=sector_rows, constituent_rows=constituents, moneyflow_rows=mf),
            config=cfg,
        )
        assert result.siphon_z is not None
        assert result.siphon_flag is True
        assert any("虹吸态" in a for a in result.annotations)

    def test_balanced_not_siphon(self):
        """均衡资金流 → 不触发；z 分出值（历史序列可算）。"""
        n = 10
        sector_rows, constituents, mf = _siphon_fixture(n, extreme_today=False)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1],
            ch_client=_FakeCH(sector_rows=sector_rows, constituent_rows=constituents, moneyflow_rows=mf),
            config=cfg,
        )
        assert result.siphon_z is not None
        assert result.siphon_flag is False

    def test_moneyflow_missing_degrades(self):
        """money_flow 空 → 虹吸独立降级（siphon_z=None），不累及 5 状态。"""
        n = 7
        closes, amounts = _velocity_fixture(n, fan_today=True)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1], ch_client=_FakeCH(sector_rows=_sector_rows(closes, amounts, n)), config=cfg
        )
        assert result.siphon_z is None
        assert result.siphon_flag is False
        assert result.rotation_state is not None
        assert any("虹吸态降级" in note for note in result.notes)


# ---------- c2) 个股分歧度 ----------


def _stock_universe(n: int = 21, hot: bool = True) -> list[tuple]:
    """40 股宇宙：39 股平稳（换手恒 1，上影 0.1）；hot 股今日换手×5+长上影。"""
    rows: list[tuple] = []
    days = _days(n)
    for i in range(39):
        sym = f"6000{i:02d}.SH"
        for d in days:
            rows.append((sym, d, 10.5, 9.5, 10.4, 1.0, 0.1))
    if hot:
        for d in days[:-1]:
            rows.append(("600099.SH", d, 10.5, 9.5, 10.4, 1.0, 0.1))
        rows.append(("600099.SH", days[-1], 11.0, 10.0, 10.1, 5.0, 1.0))  # 换手突增 5×+上影 0.9
    return rows


def _lhb_fight_rows(net_ratio_ok: bool = True, sell_side_top: bool = True) -> list[tuple]:
    buy, sell = (100e6, 99e6) if net_ratio_ok else (100e6, 50e6)
    seller = "方新侠" if sell_side_top else "某不知名营业部"
    return [
        ("600099.SH", "章盟主", buy, 0.0, buy, 1, None),
        ("600099.SH", seller, 0.0, sell, -sell, None, 1),
    ]


class TestStockDivergence:
    def test_four_components_and_watchlist(self):
        """四件全触发（换手突增/上影/炸板/对打）→ 例外清单首位+理由链齐全。"""
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        client = _FakeCH(
            sector_rows=_sector_rows(_base_closes(21), _base_amounts(21), 21),
            stock_rows=_stock_universe(),
            limit_rows=[("600099.SH", 11.0)],  # 涨停价 11.0：high 触板 close 未封 → 炸板
            lhb_rows=_lhb_fight_rows(),
        )
        result = compute_sector_divergence(_days(21)[-1], ch_client=client, config=cfg)
        assert len(result.stock_watchlist) == 1
        w = result.stock_watchlist[0]
        assert w.symbol == "600099.SH"
        assert w.percentile == pytest.approx(0.9875)  # 中秩 (39+40)/2/40
        assert w.turnover_surge == pytest.approx(5.0)
        assert w.upper_shadow == pytest.approx(0.9)
        assert w.limit_broken is True
        assert w.lhb_fight is True
        assert any("换手突增" in r for r in w.reasons)
        assert any("上影" in r for r in w.reasons)
        assert any("炸板" in r for r in w.reasons)
        assert any("对打" in r for r in w.reasons)
        # 合分手算复核：surge 截面 mean=1.1/std=0.6325 → z=6.166；0.4z+0.3×0.9+0.2+0.1
        assert w.score == pytest.approx(3.0365, abs=1e-3)

    def test_lhb_fight_requires_both_sides_top_and_small_net(self):
        """对打判定：净额占比 25%>1% → 不对打；卖方非一线游资 → 不对打。"""
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        for lhb in (_lhb_fight_rows(net_ratio_ok=False), _lhb_fight_rows(sell_side_top=False)):
            client = _FakeCH(
                sector_rows=_sector_rows(_base_closes(21), _base_amounts(21), 21),
                stock_rows=_stock_universe(),
                limit_rows=[("600099.SH", 11.0)],
                lhb_rows=lhb,
            )
            result = compute_sector_divergence(_days(21)[-1], ch_client=client, config=cfg)
            w = next((x for x in result.stock_watchlist if x.symbol == "600099.SH"), None)
            assert w is not None
            assert w.lhb_fight is False

    def test_watchlist_min_universe_guard(self):
        """可评分宇宙 <30 → 清单空 + 降级留痕（小样本不出例外清单）。"""
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        rows = [r for r in _stock_universe() if r[0] < "600005"]  # 仅 600000-600004 五股
        client = _FakeCH(
            sector_rows=_sector_rows(_base_closes(21), _base_amounts(21), 21),
            stock_rows=rows,
        )
        result = compute_sector_divergence(_days(21)[-1], ch_client=client, config=cfg)
        assert result.stock_watchlist == []
        assert any("可评分宇宙" in note for note in result.notes)


# ---------- d) SEC-03 概率标定器 ----------


class TestStateCalibrator:
    def test_conditional_frequency_math(self):
        """标定器纯函数：条件频率=后续 N 日跌>2% 占比，可复算。"""
        days = _days(16)
        states = {d: mod.RotationState.NEUTRAL_MIXED for d in days[:10]}
        closes = [(d, 100.0) for d in days]
        # 第 0/1/2 日的 +3 日（第 3/4/5 日）设为 97 → 跌 3%；其余平
        closes[3] = (days[3], 97.0)
        closes[4] = (days[4], 97.0)
        closes[5] = (days[5], 97.0)
        stats = mod._calibrate_states(states, closes, SectorDivergenceConfig())
        stat = next(s for s in stats if s.state == "NEUTRAL_MIXED")
        # 3 日前向可算日：索引 0..12 中状态日前 10 日 → i+3≤15 全可算（10 样本），跌>2% 为 i=0,1,2
        assert stat.n_samples == 10
        assert stat.freq_down_3d == pytest.approx(0.3)
        # 5 日前向：i+5≤15 → i≤10 → 10 样本全可算，跌>2% 仅 i=0（第 5 日 97）
        assert stat.freq_down_5d == pytest.approx(0.1)
        assert stat.sufficient is False  # 10 < 30

    def test_sufficient_flag_threshold(self):
        """样本量守卫：calib_min_samples=3 → sufficient=True；默认 30 → False。"""
        days = _days(16)
        states = {d: mod.RotationState.HEALTHY_MAINLINE for d in days[:5]}
        closes = [(d, 100.0) for d in days]
        cfg = SectorDivergenceConfig(calib_min_samples=3)
        stat = next(s for s in mod._calibrate_states(states, closes, cfg) if s.state == "HEALTHY_MAINLINE")
        assert stat.n_samples == 5
        assert stat.sufficient is True

    def test_calibrator_via_main_entry_insufficient(self):
        """主入口短窗（板块 K 线 8 日）→ 标定器出统计但 sufficient=False+摘要可审计。"""
        n = 8
        closes, amounts = _velocity_fixture(n, fan_today=True)
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence(
            _days(n)[-1], ch_client=_FakeCH(sector_rows=_sector_rows(closes, amounts, n)), config=cfg
        )
        assert result.state_conditional_stats
        assert all(not s.sufficient for s in result.state_conditional_stats)
        assert result.current_state_summary is not None
        assert "当前状态=" in result.current_state_summary
        assert "insufficient" in result.current_state_summary


# ---------- e) M1-②c 族相对强度雷达 ----------


def _labels_yaml(tmp_path) -> str:
    p = tmp_path / "labels.yaml"
    p.write_text(
        "families:\n"
        "  defensive:\n"
        "    boards:\n"
        "      - {key: bank, name: 银行, code: '881386.SH'}\n"
        "  offensive:\n"
        "    boards:\n"
        "      - {key: broker, name: 证券, code: '881394.SH'}\n"
        "params:\n"
        "  rs_sigma_window: 20\n"
        "  rs_min_periods: 5\n",
        encoding="utf-8",
    )
    return str(p)


def _rs_stock_rows(n: int, today_gap: float) -> list[tuple]:
    """防御 2 股+进攻 2 股：历史日差交替 0.1%/0.3%（σ>0 守卫可算），今日进攻−防御日差=today_gap（%）。"""
    rows: list[tuple] = []
    days = _days(n)
    members = {"DEF0.SH": "def", "DEF1.SH": "def", "OFF0.SH": "off", "OFF1.SH": "off"}
    for sym, fam in members.items():
        for i, d in enumerate(days):
            if i < n - 1:
                pct = (0.2 + 0.2 * (i % 2)) if fam == "off" else 0.1  # 历史 rs 交替 +0.1/+0.3pct
            else:
                pct = (0.1 + today_gap) if fam == "off" else 0.1
            rows.append((sym, d, 10.5, 9.5, 10.4, 1.0, pct))
    return rows


_RS_CONSTITUENTS = [
    ("881386.SH", "DEF0.SH"),
    ("881386.SH", "DEF1.SH"),
    ("881394.SH", "OFF0.SH"),
    ("881394.SH", "OFF1.SH"),
]


class TestRsRadar:
    def test_true_sentiment_good(self, tmp_path):
        """rs_z>+1σ 且 adv 改善 → 真情绪好注解。"""
        cfg = SectorDivergenceConfig(labels_path=_labels_yaml(tmp_path))
        client = _FakeCH(
            sector_rows=_sector_rows(_base_closes(7), _base_amounts(7), 7),
            constituent_rows=_RS_CONSTITUENTS,
            stock_rows=_rs_stock_rows(7, today_gap=2.0),  # 今日（末日=数据日）进攻族额外 +2%
            breadth_rows=[(_days(7)[-2], 40, 100), (_days(7)[-1], 60, 100)],  # adv 0.4→0.6 改善
        )
        result = compute_sector_divergence(_days(7)[-1], ch_client=client, config=cfg)
        assert result.rs_ratio is not None
        assert result.rs_z is not None and result.rs_z > 1.0
        assert any("真情绪好" in a for a in result.annotations)

    def test_safe_haven_huddle(self, tmp_path):
        """rs_z<−1σ 且指数红 → 避险抱团注解（情绪差）。"""
        cfg = SectorDivergenceConfig(labels_path=_labels_yaml(tmp_path))
        closes = _base_closes(7)
        closes[MKT][-1] = closes[MKT][-2] * 1.005  # 指数红 +0.5%
        client = _FakeCH(
            sector_rows=_sector_rows(closes, _base_amounts(7), 7),
            constituent_rows=_RS_CONSTITUENTS,
            stock_rows=_rs_stock_rows(7, today_gap=-2.0),  # 今日（末日=数据日）进攻族额外 −2%
            breadth_rows=[(_days(7)[-2], 40, 100), (_days(7)[-1], 60, 100)],
        )
        result = compute_sector_divergence(_days(7)[-1], ch_client=client, config=cfg)
        assert result.rs_z is not None and result.rs_z < -1.0
        assert any("避险抱团" in a for a in result.annotations)

    def test_missing_labels_yaml_degrades(self):
        """标签 yaml 缺失 → rs 维度降级留痕，主结果不炸。"""
        n = 7
        cfg = SectorDivergenceConfig(labels_path="nonexistent_dir/labels.yaml")
        client = _FakeCH(
            sector_rows=_sector_rows(_base_closes(n), _base_amounts(n), n),
            stock_rows=_stock_universe(),
        )
        result = compute_sector_divergence(_days(n)[-1], ch_client=client, config=cfg)
        assert result.degraded is False
        assert result.rs_ratio is None
        assert any("板块族标签加载失败" in note for note in result.notes)


# ---------- f) 降级与契约 ----------


class TestDegradation:
    def test_client_unavailable(self):
        result = compute_sector_divergence("2026-08-07", ch_client=None, config=SectorDivergenceConfig(labels_path="x"))
        # ch_writer 默认客户端在测试环境可能可用也可能不可用；仅当不可用时 degraded
        assert isinstance(result.degraded, bool)

    def test_empty_sector_kline_degraded(self):
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence("2026-08-07", ch_client=_FakeCH(), config=cfg)
        assert result.degraded is True
        assert any("无数据" in note for note in result.notes)

    def test_trade_date_not_in_data_degraded(self):
        n = 7
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        client = _FakeCH(sector_rows=_sector_rows(_base_closes(n), _base_amounts(n), n))
        result = compute_sector_divergence("2099-01-04", ch_client=client, config=cfg)
        assert result.degraded is True

    def test_sector_query_exception_degraded(self):
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        result = compute_sector_divergence("2026-08-07", ch_client=_FakeCH(exc_on="kline_sector_880"), config=cfg)
        assert result.degraded is True
        assert any("查询异常" in note for note in result.notes)

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            compute_sector_divergence("2026-13-99", ch_client=_FakeCH())

    def test_none_date_uses_latest(self):
        """trade_date=None → 取 kline_sector_880 最新数据日。"""
        n = 7
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        client = _FakeCH(sector_rows=_sector_rows(_base_closes(n), _base_amounts(n), n))
        result = compute_sector_divergence(None, ch_client=client, config=cfg)
        assert result.date == _days(n)[-1].isoformat()

    def test_json_serializable(self):
        """frozen dataclass asdict JSON 可序列化（prediction_log 预留）。"""
        n = 21
        cfg = SectorDivergenceConfig(labels_path="nonexistent.yaml")
        client = _FakeCH(
            sector_rows=_sector_rows(_base_closes(n), _base_amounts(n), n),
            stock_rows=_stock_universe(),
            limit_rows=[("600099.SH", 11.0)],
            lhb_rows=_lhb_fight_rows(),
        )
        result = compute_sector_divergence(_days(n)[-1], ch_client=client, config=cfg)
        payload = json.dumps(asdict(result), ensure_ascii=False)
        assert payload
        assert asdict(result)["date"] == _days(n)[-1].isoformat()
