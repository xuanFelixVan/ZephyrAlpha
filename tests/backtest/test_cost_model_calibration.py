# [A_test] module_id: MOD-BT-COST-CALIB | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §test
# [MODULE] tests.backtest.test_cost_model_calibration
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_cost_model_calibration.py
# [TTL] task_bound
"""成本模型标定单一真源回归锁（台账 #23 H2-A/H2-C 车道 M：滑点未校准治本）。

钉死四件事（任何一件松动，"已标定"就退回成一句注释）：

1. **证据与表自洽**：分层边界/档位表长度互锁（标定表自毁即红），PROVENANCE 的窗口、
   样本量、量纲陷阱（volume 单位=**手**）随产物披露；
2. **有界**：滑点档必落在实证区间 [2.34, 7.24] bp/边、单调非增（越不流动越贵）；
   冲击比 p=1 时不超过 η·σ 上界（≈2%），γ=0 ⇒ 永久项恒零（静态快照不可辨识，
   拆半给 γ=0.5η 会把同一段位移计费两次）；
3. **可复现**：同一条固定 fixture 序列（ADV×名义）跑两遍逐位相同——纯函数、无墙钟、
   无随机、无 I/O，任何非确定性都是成本口径的假绿；
4. **地板佣金闭式**：万0.854 + ¥5 下限结构下 ``floor_drag_bps`` 与
   ``notional_for_floor_drag_bps`` 互逆（费率一律 Decimal 注入，真源在 matching_logic；
   万0.854 是 Owner 确认的券商真实费率，本件零费率字面量）。
"""

from __future__ import annotations

import ast
import inspect
import json
import math
from decimal import Decimal
from itertools import pairwise

import pytest

from zephyr.backtest.core import cost_model_calibration as cal
from zephyr.backtest.core.cost_model_calibration import (
    ADV_QUINTILE_BOUNDS_YUAN,
    CALIBRATION_TABLE_VERSION,
    DEFAULT_PARAMS_REF,
    IMPACT_BETA,
    IMPACT_GAMMA_RATIO,
    IMPACT_PERMANENT_EXPONENT,
    IMPACT_TIER_ETA,
    IMPACT_TIER_SIGMA,
    LEGACY_FLAT_SLIPPAGE_BPS,
    PROVENANCE,
    SLIPPAGE_BPS_UNIVERSAL,
    SLIPPAGE_TIER_BPS,
    TIER_ADV_MEDIAN_YUAN,
    TIER_NAMES,
    TIER_TICK_BPS,
    CalibratedImpactLevel,
    CostCalibrationError,
    commission_floor_nonbinding_notional,
    floor_drag_bps,
    impact_level_for_notional,
    impact_level_for_tier,
    liquidity_tier,
    n_tiers,
    notional_for_floor_drag_bps,
    slippage_bps_for_notional,
    slippage_bps_universal,
)
from zephyr.backtest.core.matching_logic import COMMISSION_RATE, MIN_COMMISSION

#: 实证区间（挖矿窗口 2026-07-24~2026-09-16 的结论，越界=无出处调参）
SLIPPAGE_MIN_BPS = Decimal("2.34")
SLIPPAGE_MAX_BPS = Decimal("7.24")

#: 平方根律等价系数 Y=cost/(σ·√p) 的业界容忍带（A股中小票 1~3，美股大盘 ≈0.5）
SQRT_LAW_Y_BAND = (0.5, 3.0)

#: 固定 fixture 序列：(标的, 日均成交额 ADV 元, 单笔名义 元)——覆盖五层与地板两侧
FIXTURE_SERIES: tuple[tuple[str, float, float], ...] = (
    ("000001", 28_000_000.0, 5_000.0),
    ("000002", 41_000_000.0, 5_500.0),
    ("300750", 60_000_000.0, 58_548.0),
    ("600000", 88_000_000.0, 120_000.0),
    ("600519", 150_000_000.0, 250_000.0),
    ("601318", 300_000_000.0, 500_000.0),
    ("688981", 700_000_000.0, 1_000_000.0),
    ("000063", 1_200_000_000.0, 2_000_000.0),
    ("601899", 2_600_000_000.0, 5_000.0),
    ("600030", 6_500_000_000.0, 3_000_000.0),
    ("603259", 9_000_000.0, 1_000.0),
    ("002594", 46_410_406.0, 500_000.0),
)


def _calibrated_impact_bps(adv: float, notional: float) -> float:
    """按标定档算一笔的冲击 bps（fixture 序列复现性比对用的公共口径）。"""
    tier = liquidity_tier(adv)
    participation = min(max(notional / adv, 0.0), 1.0)
    return impact_level_for_tier(tier).cost_bps_at(participation)


# ---------------------------------------------------------------------------
# 错误码契约
# ---------------------------------------------------------------------------


def test_error_code_is_registered_unique_code():
    assert CostCalibrationError.error_code == "ZA-BT-0044"
    assert CostCalibrationError("boom").error_code == "ZA-BT-0044"
    # 与重码原主解绑（ZA-BT-0021 归 ParamAnalysisError），并允许显式覆写
    assert CostCalibrationError("x").error_code != "ZA-BT-0021"
    assert CostCalibrationError("x", error_code="ZA-BT-0001").error_code == "ZA-BT-0001"


# ---------------------------------------------------------------------------
# 1. 表自洽 + 证据披露
# ---------------------------------------------------------------------------


def test_calibration_tables_are_internally_consistent():
    assert n_tiers() == len(ADV_QUINTILE_BOUNDS_YUAN) + 1 == 5
    for table in (
        SLIPPAGE_TIER_BPS,
        IMPACT_TIER_ETA,
        IMPACT_TIER_SIGMA,
        TIER_ADV_MEDIAN_YUAN,
        TIER_TICK_BPS,
        TIER_NAMES,
    ):
        assert len(table) == n_tiers(), "档位表与层数不自洽=标定表自毁"
    assert all(b0 < b1 for b0, b1 in pairwise(ADV_QUINTILE_BOUNDS_YUAN))
    # 各层代表 ADV 必落在本层区间内（横截面中位不能被写出层外）
    bounds = (0.0, *ADV_QUINTILE_BOUNDS_YUAN, math.inf)
    for i, med in enumerate(TIER_ADV_MEDIAN_YUAN):
        assert bounds[i] < med < bounds[i + 1], f"层 {i} 代表 ADV {med} 越界"
    assert TIER_NAMES[0].startswith("Q1") and TIER_NAMES[-1].endswith("liquid")
    assert PROVENANCE.calibration_id == CALIBRATION_TABLE_VERSION


def test_tick_cost_floor_table_is_sane():
    """最小变动价位成本：量级必须 >1bp（tick 是硬底），且整体上「越流动越便宜」。

    TIER_TICK_BPS 是横截面中位的**证据列**（不参与计算），相邻五分位之间的中位抖动
    （Q1 8.783 vs Q2 9.170）不是标定缺陷，故这里校"半数趋势+端点"而非逐点单调；
    真正参与计费的滑点/冲击表在下面的测试里逐点单调卡死。
    """
    assert len(TIER_TICK_BPS) == n_tiers()
    assert all(1.0 < t < 20.0 for t in TIER_TICK_BPS), "tick 成本量级越界=按错价格带算的"
    assert min(TIER_TICK_BPS) == TIER_TICK_BPS[-1], "最便宜 tick 成本必须在最流动层"
    assert TIER_TICK_BPS.index(max(TIER_TICK_BPS)) < n_tiers() // 2, "最贵 tick 成本必须落在不流动侧"
    illiquid_half = sum(TIER_TICK_BPS[:2]) / 2
    liquid_half = sum(TIER_TICK_BPS[3:]) / 2
    assert illiquid_half > liquid_half, "不流动侧 tick 占比必须更高（否则分层量纲搞反了）"


def test_provenance_is_disclosed_and_serializable(tmp_path):
    d = PROVENANCE.to_dict()
    assert d["window_start"] < d["window_end"]
    assert d["n_symbols"] == 5519 and d["n_tick_snapshots"] == 13_119_233
    assert "c1_market.tick_depth_5" in d["tables"]
    assert d["known_limits"] and d["identifiability"] and d["impact_measure"]
    # 量纲陷阱必须写在证据里（volume 单位=手；读成股会让 η 虚高 100^β 倍）
    assert any("手" in g for g in d["unit_gotchas"])
    assert set(d["cross_checks"]) == {"eff_vs_quoted", "sqrt_law_Y", "turnover_premise"}
    out = tmp_path / "provenance.json"
    out.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    assert json.loads(out.read_text(encoding="utf-8"))["calibration_id"] == CALIBRATION_TABLE_VERSION
    assert not (tmp_path / "data").exists()  # 测试不外溢生产路径


# ---------------------------------------------------------------------------
# 2. 滑点腿：有界 + 单调 + 旧一口价确被证伪
# ---------------------------------------------------------------------------


def test_slippage_tiers_are_exact_monotone_and_bounded():
    expected_tier_bps = (
        Decimal("7.24"),
        Decimal("5.69"),
        Decimal("4.67"),
        Decimal("4.00"),
        Decimal("2.34"),
    )
    assert SLIPPAGE_TIER_BPS == expected_tier_bps  # noqa: SIM300 — 读作「实表 == 实证期望表」
    assert all(a >= b for a, b in pairwise(SLIPPAGE_TIER_BPS)), "越不流动必须越贵"
    assert min(SLIPPAGE_TIER_BPS) == SLIPPAGE_MIN_BPS
    assert max(SLIPPAGE_TIER_BPS) == SLIPPAGE_MAX_BPS
    assert cal.SLIPPAGE_TIERING_ENABLED is True


def test_legacy_flat_slippage_is_dethroned_not_reused_as_default():
    """旧 SLIPPAGE_BPS=1 只能作披露/对照，禁止再当默认值（比最便宜一层还低 2.3 倍）。"""
    assert LEGACY_FLAT_SLIPPAGE_BPS == Decimal("1")  # noqa: SIM300 — 读作「旧一口价恒等于 1bp」
    assert min(SLIPPAGE_TIER_BPS) > LEGACY_FLAT_SLIPPAGE_BPS
    assert SLIPPAGE_BPS_UNIVERSAL == Decimal("3.79")  # noqa: SIM300 — 读作「加权值恒等于 3.79bp」
    assert SLIPPAGE_MIN_BPS <= slippage_bps_universal() <= SLIPPAGE_MAX_BPS
    # 无流动性信息时走实证加权值，绝不回落到旧一口价
    assert slippage_bps_universal() > LEGACY_FLAT_SLIPPAGE_BPS


@pytest.mark.parametrize(
    ("adv", "expected_tier", "expected_bps"),
    [
        (1_000.0, 0, Decimal("7.24")),
        (46_410_406.8, 0, Decimal("7.24")),
        (46_410_406.9, 1, Decimal("5.69")),  # 边界：等于上界即进入下一层
        (90_212_531.7, 2, Decimal("4.67")),
        (173_965_046.8, 3, Decimal("4.00")),
        (417_979_415.5, 4, Decimal("2.34")),
        (9_999_999_999_999.0, 4, Decimal("2.34")),
    ],
)
def test_liquidity_tier_boundaries_and_slippage_lookup(adv: float, expected_tier: int, expected_bps: Decimal):
    assert liquidity_tier(adv) == expected_tier
    assert slippage_bps_for_notional(adv) == expected_bps


def test_liquidity_tier_is_monotone_over_ascending_series():
    tiers = [liquidity_tier(v) for v in sorted({a for _, a, _ in FIXTURE_SERIES} | {1e5, 1e7, 1e9})]
    assert tiers == sorted(tiers)
    assert tiers[0] == 0 and tiers[-1] == n_tiers() - 1


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf"), -1.0, "1000", None, True, [], {}])
def test_liquidity_tier_fail_closed_on_illegal_input(bad: object):
    with pytest.raises(CostCalibrationError):
        liquidity_tier(bad)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 3. 冲击腿：γ=0 不重复计费 + 有界 + 单调 + 越界 Fail-Closed
# ---------------------------------------------------------------------------


def test_impact_level_is_calibrated_not_engine_default():
    lvl = impact_level_for_tier(0)
    assert isinstance(lvl, CalibratedImpactLevel)
    assert lvl.tier == 0 and lvl.beta == IMPACT_BETA
    assert lvl.beta < 0.5 and lvl.beta != DEFAULT_PARAMS_REF["beta"]  # A-C 默认档 β=1.0
    assert lvl.eta > DEFAULT_PARAMS_REF["eta"]  # η 相差 3~10 倍，"永远消费默认档"不是保守而是错误
    assert lvl.source == f"offline_table:{CALIBRATION_TABLE_VERSION}"
    assert IMPACT_GAMMA_RATIO == 0.0 and lvl.gamma == 0.0


def test_permanent_impact_is_zero_so_no_double_charge():
    """γ=0：测得的瞬时位移已全部计在临时项，再拆一半给永久项=重复计费。"""
    for tier in range(n_tiers()):
        lvl = impact_level_for_tier(tier)
        for p in (1e-6, 1e-3, 0.05, 1.0):
            temp_only = lvl.eta * (p**lvl.beta) * lvl.sigma
            assert lvl.cost_ratio_at(p) == pytest.approx(temp_only, rel=1e-12)
        # 永久指数即便被注入也不改变结果（γ=0 时不生效）
        assert lvl.permanent_exponent == IMPACT_PERMANENT_EXPONENT


def test_impact_is_monotone_in_participation_and_hard_bounded():
    for tier in range(n_tiers()):
        lvl = impact_level_for_tier(tier)
        ps = [0.0, 1e-6, 1e-4, 1e-2, 0.2, 1.0]
        costs = [lvl.cost_bps_at(p) for p in ps]
        assert costs == sorted(costs), f"层 {tier} 冲击对参与率非单调"
        assert costs[0] == pytest.approx(0.0)
        assert costs[-1] == pytest.approx(lvl.eta * lvl.sigma * 1e4, rel=1e-12)
        assert lvl.cost_ratio_at(1.0) < 0.02  # 满参与上界 ≈2%（199.7bp），不是 13~18bp 那种荒谬外推
        assert all(math.isfinite(c) and c >= 0.0 for c in costs)


def test_impact_grows_as_liquidity_tier_worsens_at_equal_participation():
    p = 5e-4
    by_tier = [impact_level_for_tier(t).cost_bps_at(p) for t in range(n_tiers())]
    assert by_tier == sorted(by_tier, reverse=True), "越不流动必须冲击越高"
    assert impact_level_for_notional(2.6e9).tier == liquidity_tier(2.6e9)


@pytest.mark.parametrize("bad_p", [-1e-9, 1.0000001, 2.0, float("nan"), float("inf")])
def test_participation_out_of_range_is_fail_closed(bad_p: float):
    with pytest.raises(CostCalibrationError):
        impact_level_for_tier(0).cost_ratio_at(bad_p)


@pytest.mark.parametrize("bad_tier", [-1, 5, 99, 1.0, "0", None, True])
def test_tier_out_of_range_is_fail_closed(bad_tier: object):
    with pytest.raises(CostCalibrationError):
        impact_level_for_tier(bad_tier)  # type: ignore[arg-type]


def test_sqrt_law_coefficient_stays_in_industry_band():
    """交叉校验：Y=η·p^(β−0.5) 落在 A股中小票 1~3 / 美股大盘 0.5 量级。"""
    lo, hi = SQRT_LAW_Y_BAND
    for tier in range(n_tiers()):
        y = impact_level_for_tier(tier).sqrt_law_coefficient(1e-3)
        assert lo <= y <= hi, f"层 {tier} 平方根律系数 {y} 越出业界带 {SQRT_LAW_Y_BAND}"
    with pytest.raises(CostCalibrationError):
        impact_level_for_tier(0).sqrt_law_coefficient(0.0)


def test_impact_level_to_dict_is_serializable(tmp_path):
    d = impact_level_for_tier(2).to_dict()
    assert d["tier"] == 2 and d["beta"] == IMPACT_BETA
    assert d["sqrt_law_Y@p=1e-3"] > 0
    out = tmp_path / "impact_level.json"
    out.write_text(json.dumps(d), encoding="utf-8")
    assert json.loads(out.read_text(encoding="utf-8"))["eta"] == IMPACT_TIER_ETA[2]


# ---------------------------------------------------------------------------
# 4. 地板佣金 → 最小下单规模（闭式互逆，费率注入）
# ---------------------------------------------------------------------------


def test_floor_drag_exact_bps_on_small_order():
    """¥5,000 名义：有效费率 5/5000=万10 → 比报价万0.854 高 9.146bp。"""
    assert Decimal("5000") * COMMISSION_RATE == Decimal("0.4270000")  # < ¥5 下限
    drag = floor_drag_bps(5000.0, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
    assert drag == pytest.approx(9.146, abs=1e-9)
    assert drag == pytest.approx(
        float(Decimal("5") / Decimal("5000") * Decimal("10000") - COMMISSION_RATE * Decimal("10000")), rel=1e-12
    )


def test_floor_drag_is_zero_once_order_is_big_enough():
    assert commission_floor_nonbinding_notional(
        commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION
    ) == Decimal("58548.01")
    big = 1_000_000.0
    drag = floor_drag_bps(big, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
    assert drag == pytest.approx(0.0, abs=1e-12)
    # 恰在不再咬合的名义上：拖累收敛到 0（容差按分位量化留下的 ¥0.01 残差）
    at_boundary = float(
        commission_floor_nonbinding_notional(commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
    )
    assert floor_drag_bps(
        at_boundary * 1.01, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION
    ) == pytest.approx(0.0, abs=1e-9)


def test_min_notional_and_floor_drag_are_inverse():
    """闭式互逆：按 drag 上限反解出名义，再算回去必须落在同一 drag。"""
    for cap_bps in (1.0, 2.0, 5.0, 10.0):
        notional = notional_for_floor_drag_bps(cap_bps, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
        nonbinding = commission_floor_nonbinding_notional(
            commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION
        )
        assert Decimal("0") < notional < nonbinding, "drag 上限反解必须落在地板仍咬合的区间内"
        got = floor_drag_bps(float(notional), commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
        assert got == pytest.approx(cap_bps, abs=1e-3)
    # 现网结论锚定：把地板拖累压进 5bp 需名义 ≥¥8,541（cost_attribution.FLOOR_DRAG_CAP_BPS 口径）
    assert notional_for_floor_drag_bps(5.0, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION) == Decimal(
        "8541.17"
    )
    assert notional_for_floor_drag_bps(
        5.0, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION
    ) > notional_for_floor_drag_bps(10.0, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"notional": 0.0},
        {"notional": -1.0},
        {"notional": float("nan")},
        {"notional": float("inf")},
        {"notional": "1000"},
        {"notional": None},
        {"notional": True},
        {"notional": 1000.0, "rate": Decimal("0")},
        {"notional": 1000.0, "floor": Decimal("0")},
        {"notional": 1000.0, "rate": Decimal("-1")},
        {"notional": 1000.0, "floor": Decimal("nan")},
        {"notional": 1000.0, "rate": Decimal("Infinity")},
        {"notional": 1000.0, "rate": "not-a-rate"},
    ],
    ids=lambda d: str(sorted((k, str(v)) for k, v in d.items())),
)
def test_floor_drag_inputs_are_fail_closed(kwargs: dict):
    rate = kwargs.get("rate", COMMISSION_RATE)
    floor = kwargs.get("floor", MIN_COMMISSION)
    with pytest.raises(CostCalibrationError):
        floor_drag_bps(kwargs["notional"], commission_rate=rate, min_commission=floor)
    if "rate" in kwargs or "floor" in kwargs:  # 反解口径同样不接受非法费率/下限注入
        with pytest.raises(CostCalibrationError):
            notional_for_floor_drag_bps(1.0, commission_rate=rate, min_commission=floor)
        with pytest.raises(CostCalibrationError):
            commission_floor_nonbinding_notional(commission_rate=rate, min_commission=floor)


@pytest.mark.parametrize("bad_drag", [0.0, -1.0, float("nan"), float("inf"), "1bp"])
def test_notional_for_drag_rejects_illegal_target(bad_drag: object):
    with pytest.raises(CostCalibrationError):
        notional_for_floor_drag_bps(bad_drag, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
    with pytest.raises(CostCalibrationError):
        commission_floor_nonbinding_notional(commission_rate=Decimal("0"), min_commission=MIN_COMMISSION)


# ---------------------------------------------------------------------------
# 5. 固定 fixture 序列：有界 + 逐位可复现
# ---------------------------------------------------------------------------


def _run_fixture_pass() -> list[tuple[int, Decimal, float, float]]:
    out: list[tuple[int, Decimal, float, float]] = []
    for _sym, adv, notional in FIXTURE_SERIES:
        tier = liquidity_tier(adv)
        out.append(
            (
                tier,
                SLIPPAGE_TIER_BPS[tier],
                _calibrated_impact_bps(adv, notional),
                floor_drag_bps(notional, commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION),
            )
        )
    return out


def test_calibration_output_is_bounded_and_reproducible_on_fixed_fixture():
    first = _run_fixture_pass()
    second = _run_fixture_pass()
    assert first == second, "同输入不同输出=标定件被塞进墙钟/随机/I-O"

    slip_min, slip_max = float(SLIPPAGE_MIN_BPS), float(SLIPPAGE_MAX_BPS)
    for (tier, slip, imp_bps, drag), (_sym, adv, notional) in zip(first, FIXTURE_SERIES, strict=True):
        assert 0 <= tier < n_tiers()
        assert slip_min <= float(slip) <= slip_max
        assert math.isfinite(imp_bps) and imp_bps > 0.0
        assert imp_bps <= impact_level_for_tier(tier).cost_bps_at(1.0)  # 不超满参与上界
        assert math.isfinite(drag) and drag >= 0.0
        # 两腿语义互斥：滑点与 ADV 相关但与本笔名义无关；冲击随本笔名义单调
        assert slip == slippage_bps_for_notional(adv)
        assert _calibrated_impact_bps(adv, notional * 2) >= imp_bps

    tiers = {t for t, _s, _i, _d in first}
    assert len(tiers) >= 3, "fixture 未覆盖足够多层，单调性检查形同虚设"


def test_impact_leg_is_size_dependent_and_slippage_leg_is_not():
    """同一 ADV 下改名义：冲击变、滑点不变（两腿不得混用）。"""
    adv = 150_000_000.0
    small = _calibrated_impact_bps(adv, 5_000.0)
    large = _calibrated_impact_bps(adv, 1_000_000.0)
    assert 0.0 < small < large
    assert slippage_bps_for_notional(adv) == SLIPPAGE_TIER_BPS[liquidity_tier(adv)]  # 滑点只看 ADV
    assert slippage_bps_for_notional(adv) != slippage_bps_for_notional(adv / 10.0)  # 确按流动性分层，非一口价
    assert _calibrated_impact_bps(adv / 10.0, 5_000.0) > small  # 同名义下更差流动性→更高冲击


# ---------------------------------------------------------------------------
# 6. 纯度与单一真源（INVARIANTS 的机器化）
# ---------------------------------------------------------------------------


def test_module_is_pure_no_clock_no_io_no_fee_literals():
    """纯度按**代码**校（AST），不按注释/文档措辞校。

    (a) 依赖面：只准 stdlib 纯件——无墙钟、无随机、无 I/O、无 DuckDB、不外引 zephyr；
    (b) 零费率字面量：券商真源常量（万0.854 / ¥5 地板 / 印花税 / 过户费）不得以
        数值或 Decimal 字符串形式出现在本件（费率一律由调用方注入）。
    """
    tree = ast.parse(inspect.getsource(cal))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "math", "dataclasses", "decimal", "typing"}, (
        f"标定件依赖面越界（墙钟/随机/I-O/DB/跨域外引）: {sorted(imported)}"
    )

    forbidden_rates = {
        float(COMMISSION_RATE): "万0.854 佣金费率",
        float(MIN_COMMISSION): "¥5 佣金地板",
        0.0005: "印花税",
        0.00001: "过户费",
    }
    offenders: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        raw: object = node.value
        if isinstance(raw, bool) or not isinstance(raw, (int, float, str)):
            continue
        try:
            val = float(raw)
        except ValueError:
            continue
        why = forbidden_rates.get(val)
        if why is not None:
            offenders.add(f"{raw!r}={why}")
    assert not offenders, f"标定件出现费率字面量 {sorted(offenders)}（真源在 matching_logic，本件须零字面量）"
