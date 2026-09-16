# [A_test] module_id: MOD-BT-COST-ATTRIB | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §test
# [MODULE] tests.backtest.test_cost_attribution
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_cost_attribution.py
# [TTL] task_bound
"""成交成本归因回归锁（台账 #23 H2 车道 M：地板佣金 + 冲击旁路 + 滑点未校准）。

三侧同锁（缺一即可被静默回退，故分别钉死）：

1. **地板佣金侧**（H2-A）：¥5 下限在小额单上必须**可见**——5000 元名义按万0.854
   只该收 ¥0.427，被抬到 ¥5.00，这 ¥4.573 溢价必须出现在归因产物的
   ``floor_commission`` 分量里（不是注释里）。抬升口径与撮合引擎同源
   （``max(名义×rate, min_commission)``），费率一律由 ``matching_logic`` 注入，
   本用例零费率字面量（万0.854 是 Owner 确认的券商真实费率，禁改禁抄第二处）。
2. **冲击侧**（H2-B）：应计冲击腿 = max(引擎实测, 标定档)，**任何入参组合都无法
   把它清零**（``consumed_slippage_bps=0`` / 无 ADV 表 / 实测上报恒零 / 实测
   1e-15 / 数组截断…）；实测恒零或欠计越过容忍线必须转 ``IMPACT-LEG-BYPASSED``
   P0 告警——"假装已计费"在这里是断言失败，不是文档承诺。
3. **沉默禁令侧**：阈值全过才给 ``COST-MODEL-OK``；不可算的量以 ``None`` 字段
   显式披露，绝不静默省略字段或返回零值假象；结构性非法输入 Fail-Closed 抛
   ``CostAttributionError``（ZA-BT-0043）。

测试只写 ``tmp_path``，绝不触达 ``data/``（宪法 §9.6）。
"""

from __future__ import annotations

import ast
import inspect
import json
import math
from decimal import Decimal

import pytest

from zephyr.backtest.core import cost_attribution as mod
from zephyr.backtest.core.cost_attribution import (
    COMMISSION_RECON_TOLERANCE,
    FLOOR_BOUND_SHARE_ALERT,
    FLOOR_DRAG_CAP_BPS,
    IMPACT_MEASURED_ZERO_EPS_BPS,
    CostAttribution,
    CostAttributionError,
    attribute_trade_costs,
)
from zephyr.backtest.core.cost_model_calibration import (
    SLIPPAGE_TIER_BPS,
    impact_level_for_tier,
    liquidity_tier,
)
from zephyr.backtest.core.matching_logic import (
    COMMISSION_RATE,
    MIN_COMMISSION,
    SLIPPAGE_BPS,
    STAMP_TAX_RATE,
    TRANSFER_FEE_RATE,
)


def _trade(
    *,
    price: float,
    quantity: int,
    side: str = "BUY",
    symbol: str = "600519",
    timestamp: str = "2026-09-15",
    **extra: object,
) -> dict[str, object]:
    """artifact trade_log 形态的一行（commission/decision_price 按需追加）。"""
    row: dict[str, object] = {
        "timestamp": timestamp,
        "symbol": symbol,
        "side": side,
        "price": price,
        "quantity": quantity,
    }
    row.update(extra)
    return row


def _attrib(trades: list[dict[str, object]], **kwargs: object) -> CostAttribution:
    """费率一律注入 matching_logic 真源常量（本用例零费率字面量）。"""
    base: dict[str, object] = {
        "commission_rate": COMMISSION_RATE,
        "stamp_tax_rate": STAMP_TAX_RATE,
        "transfer_fee_rate": TRANSFER_FEE_RATE,
        "min_commission": MIN_COMMISSION,
    }
    base.update(kwargs)
    return attribute_trade_costs(trades, **base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 错误码契约（GATE-ERRCODE-CONSISTENCY 对账锚）
# ---------------------------------------------------------------------------


def test_error_code_is_registered_unique_code():
    assert CostAttributionError.error_code == "ZA-BT-0043"
    assert CostAttributionError("x").error_code == "ZA-BT-0043"


# ---------------------------------------------------------------------------
# H2-A：地板佣金必须咬合小额单，且溢价在归因分量里可见
# ---------------------------------------------------------------------------


def test_floor_commission_binds_on_small_order_exact_decimal_arithmetic():
    """¥5,000 名义 @ 万0.854 = ¥0.427 → 抬到 ¥5.00，抬升量 4.573 进产物。"""
    notional = Decimal("5000")
    proportional = notional * COMMISSION_RATE  # 与撮合引擎同一 Decimal 口径
    assert proportional == Decimal("0.4270000")
    assert proportional < MIN_COMMISSION
    assert max(proportional, MIN_COMMISSION) == Decimal("5")

    a = _attrib([_trade(price=10.0, quantity=500)])  # 10.0 × 500 = ¥5,000

    assert a.trades_count == 1
    assert a.floor_bound_trades == 1
    assert a.floor_bound_share == pytest.approx(1.0)
    assert a.commission_pure_total == pytest.approx(5.0, abs=1e-12)
    # 地板溢价 = 应计纯佣金 − 纯比例佣金 = 5.000 − 0.427
    assert a.commission_floor_premium_total == pytest.approx(4.573, abs=1e-9)
    assert a.commission_reported_total == pytest.approx(5.0 + 0.05 + 0.0, abs=1e-9)  # +过户万0.1，买无印花

    m = a.to_metrics_dict()
    floor = m["floor_commission"]
    assert floor["floor_bound_trades"] == 1
    assert floor["commission_pure_total"] == pytest.approx(5.0)
    assert floor["commission_floor_premium_total"] == pytest.approx(4.573, abs=0.005)
    assert floor["floor_premium_share_of_commission"] == pytest.approx(4.573 / 5.0, abs=1e-3)
    # 有效费率 vs 报价费率：地板把万0.854 抬到万10（≈11.7 倍）——这正是"一半亏损是佣金"的成因
    assert floor["quoted_commission_rate_bps"] == pytest.approx(0.854, abs=1e-9)
    assert floor["effective_commission_rate_median_bps"] == pytest.approx(10.0, abs=1e-9)
    assert floor["rate_inflation_x"] == pytest.approx(10.0 / 0.854, abs=0.02)
    assert m["extra"]["proportional_commission_only_total"] == pytest.approx(0.43, abs=0.005)
    assert a.quoted_commission_rate_bps == pytest.approx(float(COMMISSION_RATE * Decimal("10000")))
    # 地板拖累容忍线（政策单一真源）随产物披露，供 order_size_discipline 引用
    assert floor["floor_drag_cap_bps"] == FLOOR_DRAG_CAP_BPS
    assert m["extra"]["floor_drag_median_bps"] == pytest.approx(9.146, abs=1e-3)


def test_floor_alert_fires_when_floor_bound_share_breaks_line():
    """一地板（¥5,000）一正常（¥100,000）→ 占比 0.5 > 25% 线 → P0 告警。"""
    a = _attrib(
        [
            _trade(price=10.0, quantity=500, symbol="600519"),
            _trade(price=100.0, quantity=1000, symbol="000001", side="SELL"),
        ]
    )
    assert a.floor_bound_trades == 1
    assert a.floor_bound_share == pytest.approx(0.5)
    codes = {x.code for x in a.alerts}
    assert "COST-FLOOR-DOMINANT" in codes
    assert a.sell_count == 1 and a.buy_count == 1
    # 印花税只在卖出腿计一次（禁重复相加）
    assert a.stamp_tax_total == pytest.approx(100000 * 0.0005, abs=1e-9)
    assert a.transfer_fee_total == pytest.approx(105000 * 0.00001, abs=1e-9)
    sev = {x.code: x.severity for x in a.alerts}
    assert sev["COST-FLOOR-DOMINANT"] == "P0"


def test_large_order_not_floor_bound_and_share_below_line():
    """单一大额单（¥1,000,000）不顶地板 → 无地板告警（阈值判据不被误触）。"""
    a = _attrib([_trade(price=100.0, quantity=10000)], net_result=-1_000_000.0)
    assert a.floor_bound_trades == 0
    assert a.floor_bound_share == 0.0
    assert "COST-FLOOR-DOMINANT" not in {x.code for x in a.alerts}
    assert a.commission_pure_total == pytest.approx(float(Decimal("1000000.00") * COMMISSION_RATE), abs=1e-9)


# ---------------------------------------------------------------------------
# H2-B：冲击成本不可被任何配置清零（fail-closed 反旁路）
# ---------------------------------------------------------------------------

_SMALL = [_trade(price=10.0, quantity=500), _trade(price=20.0, quantity=250)]
_BIG = [_trade(price=100.0, quantity=10000)]


def _bypass_configs() -> list[dict[str, object]]:
    """穷举"把冲击清零"的每一条配置路径（旁路尝试）。"""
    return [
        {},  # 引擎未上报：应计腿必须自查表取标定档
        {"impact_bps_by_trade": [0.0, 0.0]},  # 上报恒零（DEFAULT_PARAMS 旁路的确定症状）
        {"impact_bps_by_trade": [1e-15, 1e-15]},  # 上报浮点噪声级"近似零"
        {"impact_bps_by_trade": [0.0, 0.0], "consumed_slippage_bps": 0},
        {"consumed_slippage_bps": 0},  # 滑点被配成 0 也带不动冲击腿
        {"impact_bps_by_trade": [0.0, 0.0], "adv_notional_by_symbol": None},
        {"impact_bps_by_trade": [0.0, 0.0], "net_result": 0.0, "initial_capital": None},
    ]


@pytest.mark.parametrize("cfg", _bypass_configs(), ids=lambda c: json.dumps(c, sort_keys=True, default=str)[:60])
def test_impact_cost_cannot_be_zeroed_by_any_config(cfg: dict[str, object]):
    a = _attrib(_SMALL, **cfg)
    assert a.impact_cost_total > 0.0, f"冲击应计腿被配置清零：{cfg}"
    assert a.cost_total >= a.impact_cost_total > 0.0
    assert a.to_metrics_dict()["friction"]["impact_cost_total"] > 0.0
    assert a.extra["impact_accrued_w_bps"] > 0.0
    # 未上报 → 应计=标定档；上报恒零/近零 → 应计仍取标定档且立刻点名旁路
    if "impact_bps_by_trade" in cfg:
        assert a.impact_leg_bypassed is True, f"上报被静默采信：{cfg}"
        codes = {x.code for x in a.alerts}
        assert "IMPACT-LEG-BYPASSED" in codes
        sev = {x.code: x.severity for x in a.alerts}
        assert sev["IMPACT-LEG-BYPASSED"] == "P0"
        # as-run 实测轨如实记录（不粉饰），但应计腿严格高于它——两轨不得互相遮蔽
        reported_bps = float(cfg["impact_bps_by_trade"][0])  # type: ignore[index]
        assert a.impact_cost_measured_total == pytest.approx(a.notional_total * reported_bps / 1e4, rel=1e-9)
        assert a.impact_cost_total > a.impact_cost_measured_total
    else:
        assert a.impact_leg_bypassed is False  # 「未上报」本身不判旁路


def test_measured_impact_above_calibrated_is_kept_never_understated():
    """引擎实测高于标定档时：应计取实测（不降标），且不算旁路。"""
    measured = 100.0  # 远高于该流动性层的标定冲击档（个位数 bp 量级）
    adv_table = {"600519": 5_000_000_000.0}
    a = _attrib(_BIG, impact_bps_by_trade=[measured], adv_notional_by_symbol=adv_table)
    expected = a.notional_total * measured / 1e4
    assert a.impact_cost_measured_total == pytest.approx(expected, rel=1e-12)
    assert a.impact_cost_total == pytest.approx(expected, rel=1e-12)
    assert a.calibrated_impact_w_bps < measured  # 前提：实测确实高于标定档
    assert a.impact_leg_bypassed is False
    assert "IMPACT-LEG-BYPASSED" not in {x.code for x in a.alerts}
    # 同一构造输入不上报实测时，应计腿取标定档（更低但严格为正）
    b = _attrib(_BIG, adv_notional_by_symbol=adv_table)
    assert 0.0 < b.impact_cost_total < a.impact_cost_total


def test_measured_impact_equal_to_calibration_is_clean():
    """实测=标定档（正确计费）时不告旁路，两轨相等。"""
    notional = 1_000_000.0
    adv = 5_000_000_000.0
    tier = liquidity_tier(adv)
    p = notional / adv
    bps = impact_level_for_tier(tier).cost_bps_at(min(max(p, 0.0), 1.0))
    a = _attrib(
        _BIG,
        adv_notional_by_symbol={"600519": adv},
        consumed_slippage_bps=SLIPPAGE_BPS,
        impact_bps_by_trade=[bps],
    )
    assert a.impact_leg_bypassed is False
    assert a.impact_cost_total == pytest.approx(a.impact_cost_measured_total, rel=1e-9)
    assert a.impact_cost_total > 0.0


def test_impact_threshold_constants_are_tiny_and_positive():
    assert IMPACT_MEASURED_ZERO_EPS_BPS > 0.0
    assert IMPACT_MEASURED_ZERO_EPS_BPS < 1e-6


@pytest.mark.parametrize("series", [[0.0], [0.0, 0.0, 0.0], [], "0.0"], ids=["短1", "长3", "空", "非序列"])
def test_impact_series_shape_mismatch_is_fail_closed(series: object):
    """数组长度/类型与成交笔数不匹配 → 结构性非法（不接受静默补齐或截断）。"""
    with pytest.raises(CostAttributionError):
        _attrib(_SMALL, impact_bps_by_trade=series)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf")])
def test_non_finite_or_negative_measured_impact_is_fail_closed(bad: float):
    with pytest.raises(CostAttributionError):
        _attrib(_SMALL, impact_bps_by_trade=[bad, 1.0])


def test_non_numeric_measured_impact_is_fail_closed():
    with pytest.raises(CostAttributionError):
        _attrib(_SMALL, impact_bps_by_trade=["x", 1.0])


def test_impact_series_must_be_a_sequence():
    with pytest.raises(CostAttributionError):
        _attrib(_SMALL, impact_bps_by_trade=0)


# ---------------------------------------------------------------------------
# 结构非法输入 Fail-Closed（沉默禁令的反面：不许返回零值假象）
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "trades",
    [
        None,
        [],
        "not-a-sequence",
        b"bytes",
        [123],
        [{"side": "BUY", "quantity": 100}],
        [{"side": "BUY", "price": 0.0, "quantity": 100}],
        [{"side": "BUY", "price": -1.0, "quantity": 100}],
        [{"side": "HOLD", "price": 10.0, "quantity": 100}],
        [{"side": "", "price": 10.0, "quantity": 100}],
        [{"side": "BUY", "price": "abc", "quantity": 100}],
    ],
    ids=repr,
)
def test_structurally_illegal_input_raises(trades: object):
    with pytest.raises(CostAttributionError) as ei:
        _attrib(trades)  # type: ignore[arg-type]
    assert ei.value.error_code == "ZA-BT-0043"
    assert str(ei.value).strip(), "抛错必须带可定位上下文，不许空消息"


@pytest.mark.parametrize(
    "overrides",
    [
        {"commission_rate": Decimal("0")},
        {"commission_rate": Decimal("-1")},
        {"min_commission": Decimal("0")},
        {"min_commission": Decimal("-5")},
        {"stamp_tax_rate": Decimal("-1")},
        {"transfer_fee_rate": Decimal("-1")},
    ],
    ids=lambda d: next(iter(d)),
)
def test_illegal_injected_rates_are_fail_closed(overrides: dict[str, Decimal]):
    trades: list[dict[str, object]] = [
        {"side": "SELL", "price": 10.0, "quantity": 500},
        {"side": "BUY", "price": 10.0, "quantity": 500},
    ]
    kwargs: dict[str, object] = {
        "commission_rate": COMMISSION_RATE,
        "stamp_tax_rate": STAMP_TAX_RATE,
        "transfer_fee_rate": TRANSFER_FEE_RATE,
        "min_commission": MIN_COMMISSION,
    }
    kwargs.update(overrides)
    with pytest.raises(CostAttributionError):
        attribute_trade_costs(trades, **kwargs)


def test_side_vocabulary_accepts_cn_and_lowercase_aliases():
    """词表闭合但容忍别名（BUY/B/买/买入 与 SELL/S/卖/卖出），未知值抛错。"""
    for side in ("BUY", "B", "买", "买入", "buy"):
        a = _attrib([_trade(price=10.0, quantity=500, side=side)])
        assert a.buy_count == 1 and a.sell_count == 0
    for side in ("SELL", "S", "卖", "卖出", "sell"):
        a = _attrib([_trade(price=10.0, quantity=500, side=side)])
        assert a.sell_count == 1 and a.buy_count == 0


# ---------------------------------------------------------------------------
# 产物契约：字段不缺席、告警不沉默、序列化不外溢
# ---------------------------------------------------------------------------


def test_uncomputable_metrics_are_none_not_omitted():
    """不可算的量必须显式为 None（省略字段=假象）。"""
    a = _attrib(_SMALL)  # 不给 initial_capital/n_trading_days/net_result
    m = a.to_metrics_dict()
    assert m["friction"]["cost_share_of_abs_result"] is None
    assert m["friction"]["turnover_one_side_annualized"] is None
    assert "turnover_one_side_annualized" in m["friction"]
    assert "cost_share_of_abs_result_as_run" in m["friction"]
    assert m["schema"] == "cost_attribution/1.0"


def test_alerts_never_empty_silence_ban():
    """全阈值通过时给 COST-MODEL-OK（而非空列表）——沉默是被禁止的行为。"""
    notional = 1_000_000.0
    adv = 5_000_000_000.0
    tier = liquidity_tier(adv)
    bps = impact_level_for_tier(tier).cost_bps_at(min(notional / adv, 1.0))
    reported = float(Decimal("1000000.00") * COMMISSION_RATE + Decimal("1000000.00") * TRANSFER_FEE_RATE)
    a = _attrib(
        [_trade(price=100.0, quantity=10000, commission=reported)],
        consumed_slippage_bps=float(SLIPPAGE_TIER_BPS[tier]),
        adv_notional_by_symbol={"600519": adv},
        impact_bps_by_trade=[bps],
        net_result=-1_000_000.0,
    )
    codes = [x.code for x in a.alerts]
    assert codes == ["COST-MODEL-OK"], codes
    assert a.alerts[0].severity == "P2"
    assert a.recon_max_relative_error == pytest.approx(0.0, abs=1e-12)


def test_commission_recon_drift_is_alerted_not_silently_refloated():
    """上报佣金与重构口径背离 → COMMISSION-RECON-DRIFT（不得静默改口径）。"""
    reported = float(Decimal("1000000.00") * COMMISSION_RATE)  # 少计过户费
    a = _attrib(
        [_trade(price=100.0, quantity=10000, commission=reported)],
        adv_notional_by_symbol={"600519": 5_000_000_000.0},
    )
    assert a.recon_max_relative_error > COMMISSION_RECON_TOLERANCE
    assert "COMMISSION-RECON-DRIFT" in {x.code for x in a.alerts}
    assert a.commission_reported_total == pytest.approx(reported, rel=1e-12)


def test_impact_identifiability_signature_alerts_on_affine_exec_prices():
    """成交价是决策价的仿射函数（σ≈0）⇒ 冲击项实际恒零 → 立刻点名。"""
    trades = [
        _trade(price=100.01, quantity=1000, decision_price=100.0),
        _trade(price=100.01, quantity=2000, decision_price=100.0, symbol="000001"),
        _trade(price=100.01, quantity=3000, decision_price=100.0, symbol="600000"),
    ]
    a = _attrib(trades)
    assert a.realized_exec_cost_bps_stdev == pytest.approx(0.0, abs=1e-12)
    assert "IMPACT-TERMS-UNIDENTIFIED" in {x.code for x in a.alerts}
    assert a.realized_exec_cost_coverage == pytest.approx(1.0)


def test_as_run_track_is_wired_not_silently_zero():
    """as-run 分量（该 run 真扣掉的钱）算而不接=假绿，必须进产物。"""
    a = _attrib([_trade(price=100.01, quantity=1000, decision_price=100.0)], net_result=-1000.0)
    assert a.realized_exec_cost_coverage == pytest.approx(1.0)
    assert a.realized_exec_cost_total == pytest.approx(100010.0 * 1.0 / 1e4, rel=1e-9)  # 1bp × ¥100,010
    assert a.cost_total_as_run > 0.0
    assert a.cost_share_of_abs_result_as_run is not None
    m = a.to_metrics_dict()["friction"]
    assert m["realized_exec_cost_total"] > 0.0
    assert m["cost_total_as_run"] > 0.0
    assert m["realized_exec_cost_coverage"] == pytest.approx(1.0)
    assert m["cost_share_of_abs_result_as_run"] is not None


def test_fragmentation_facts_and_turnover_alert_shape():
    trades = [
        _trade(price=10.0, quantity=500, timestamp="2026-09-15"),
        _trade(price=10.0, quantity=500, timestamp="2026-09-15"),
        _trade(price=11.0, quantity=500, timestamp="2026-09-16", symbol="000001"),
    ]
    a = _attrib(trades, initial_capital=100_000.0, n_trading_days=2, net_result=-50.0)
    assert a.distinct_symbol_days == 2
    assert a.orders_per_symbol_day_mean == pytest.approx(1.5)
    assert a.notional_median == pytest.approx(5000.0)
    assert a.turnover_one_side_annualized is not None and a.turnover_one_side_annualized > 12.0
    codes = {x.code for x in a.alerts}
    assert "TURNOVER-BREAKS-SLIPPAGE-PREMISE" in codes
    assert "COST-DOMINATES-RESULT" in codes
    assert math.isfinite(a.commission_share_of_cost) and a.commission_share_of_cost > 0.0


def test_result_is_deterministic_and_json_serializable(tmp_path):
    """同输入必同输出（无墙钟/无随机/无 I/O）；产物可直接进 artifact。"""
    trades = [
        _trade(price=10.0, quantity=500, commission=5.05),
        _trade(price=100.0, quantity=10000, side="SELL", commission=90.4),
    ]
    first = _attrib(trades, net_result=-5000.0, initial_capital=1_000_000.0, n_trading_days=20).to_metrics_dict()
    second = _attrib(trades, net_result=-5000.0, initial_capital=1_000_000.0, n_trading_days=20).to_metrics_dict()
    assert json.dumps(first, sort_keys=True, ensure_ascii=False) == json.dumps(
        second, sort_keys=True, ensure_ascii=False
    )
    assert first["provenance"]["calibration_id"]
    out = tmp_path / "cost_attribution.json"
    out.write_text(json.dumps(first, ensure_ascii=False), encoding="utf-8")
    assert json.loads(out.read_text(encoding="utf-8"))["schema"] == "cost_attribution/1.0"
    assert not (tmp_path / "data").exists()  # 测试不外溢生产路径


def test_module_is_pure_no_clock_no_io():
    """INVARIANTS 钉扎（校代码 AST，不校注释措辞）：纯函数 + 零费率字面量。

    (a) 依赖面：无墙钟/随机/I-O/DB，且**不外引 matching_logic**——费率只能由调用方注入；
    (b) 零费率字面量：万0.854 / ¥5 地板 / 印花税 / 过户费 不得以数值或 Decimal 字面量出现。
    """
    tree = ast.parse(inspect.getsource(mod))
    tops: set[str] = set()
    segments: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            tops.update(alias.name.split(".")[0] for alias in node.names)
            segments.update(s for alias in node.names for s in alias.name.split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            tops.add(node.module.split(".")[0])
            segments.update(node.module.split("."))
    assert tops <= {"__future__", "math", "collections", "dataclasses", "decimal", "typing", "zephyr"}, (
        f"归因件依赖面越界: {sorted(tops)}"
    )
    for banned in ("matching_logic", "duckdb", "io", "pathlib", "subprocess", "datetime", "random", "time", "os"):
        assert banned not in segments, f"归因件外引 {banned}（纯函数/费率注入铁律）"

    injected_rates = {
        COMMISSION_RATE: "佣金万0.854",
        MIN_COMMISSION: "佣金地板 ¥5",
        STAMP_TAX_RATE: "印花税",
        TRANSFER_FEE_RATE: "过户费",
    }
    for raw in (
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Decimal"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, int | str)
    ):
        assert Decimal(str(raw)) not in injected_rates, f"归因件写死费率字面量 {raw!r}（真源在 matching_logic）"
    tiny_rates = {float(COMMISSION_RATE), float(STAMP_TAX_RATE), float(TRANSFER_FEE_RATE)}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
            continue
        if not isinstance(node.value, int | float):
            continue
        assert float(node.value) not in tiny_rates, f"归因件写死费率字面量 {node.value!r}（真源在 matching_logic）"


# ---------------------------------------------------------------------------
# 落盘注入侧（车道 M 收口）：归因必须真的进 artifact metrics，而不是躺在模块里
# ---------------------------------------------------------------------------


def _sink_data(
    trade_rows: list[dict[str, object]],
    *,
    total_return: float = -0.18,
    equity: float = 1_000_000.0,
):
    """构造 BacktestSinkData（build_artifact_from_data 的唯一入参形态）。"""
    from datetime import datetime, timezone

    from zephyr.backtest.io.backtest_result_sink import BacktestSinkData, EquityPoint, TradeRecord

    return BacktestSinkData(
        strategy_id="laneM-probe",
        run_id="laneM-run-1",
        start_date=datetime(2026, 8, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 15, tzinfo=timezone.utc),
        total_return=total_return,
        annual_return=total_return,
        sharpe_ratio=-0.5,
        max_drawdown=0.2,
        win_rate=0.4,
        trades_count=len(trade_rows),
        timestamp=datetime(2026, 9, 16, tzinfo=timezone.utc),
        equity_curve=tuple(
            EquityPoint(timestamp=f"2026-09-{10 + i:02d}T00:00:00+00:00", equity=equity * (1 + total_return * i / 5))
            for i in range(6)
        ),
        trade_log=tuple(TradeRecord(**row) for row in trade_rows),  # type: ignore[arg-type]
    )


def test_artifact_metrics_carry_cost_attribution_snapshot():
    """碎片化成交的 run：落盘 artifact 必须自带地板佣金归因（不再是"吞掉一半亏损"）。"""
    from zephyr.backtest.io.result_repository import build_artifact_from_data

    rows = (
        [
            _trade(price=10.0, quantity=100, commission=5.0),  # ¥1,000 名义 → 顶 ¥5 地板
            _trade(price=12.5, quantity=160, commission=5.0, symbol="000001"),
            _trade(price=9.0, quantity=200, side="SELL", commission=5.0, symbol="000002"),
        ]
    )
    artifact = build_artifact_from_data(_sink_data(rows))
    snap = artifact.metrics["cost_attribution"]
    assert snap["status"] == "ok"
    assert snap["trades"]["count"] == 3
    floor = snap["floor_commission"]
    assert floor["floor_bound_trades"] == 3  # 笔笔顶地板（H2-A 病灶本体）
    assert floor["quoted_commission_rate_bps"] == float(COMMISSION_RATE) * 1e4  # 费率真源，非抄写
    assert floor["rate_inflation_x"] > 4.0
    codes = {a["code"] for a in snap["alerts"]}
    assert "COST-FLOOR-DOMINANT" in codes  # 告警是数据，随产物出门


def test_injection_uses_calibrated_slippage_not_legacy_flat():
    """补计口径必须是标定档（>旧 1bp），且 provenance 随盘披露（禁无出处回退）。"""
    from zephyr.backtest.io.result_repository import build_artifact_from_data

    rows = [_trade(price=10.0, quantity=100, commission=5.0)]
    snap = build_artifact_from_data(_sink_data(rows)).metrics["cost_attribution"]
    gap = snap["calibration_gap"]
    assert snap["consumed_slippage_provenance"].startswith("calibrated")
    assert gap["consumed_slippage_w_bps"] > gap["legacy_flat_slippage_bps"]


def test_empty_trade_log_is_explicit_no_trades_not_silence():
    """零成交 run：显式 status=no_trades，既不是异常也不是假零值。"""
    from zephyr.backtest.io.result_repository import build_artifact_from_data

    snap = build_artifact_from_data(_sink_data([])).metrics["cost_attribution"]
    assert snap["status"] == "no_trades"
    assert snap["schema"] == "cost_attribution/1.0"


def test_attribution_failure_is_recorded_and_logged_never_swallowed(monkeypatch, caplog):
    """归因通道坏：artifact 仍落盘，但必须留 status=error + ERROR 日志（沉默禁令）。"""
    import logging

    import zephyr.backtest.core.cost_attribution as ca_mod
    from zephyr.backtest.io.result_repository import build_artifact_from_data

    def _boom(*_a, **_k):
        raise ca_mod.CostAttributionError("注入侧探针：归因不可算")

    monkeypatch.setattr(ca_mod, "attribute_trade_costs", _boom)
    rows = [_trade(price=10.0, quantity=100, commission=5.0)]
    with caplog.at_level(logging.ERROR, logger="zephyr.backtest.io.result_repository"):
        snap = build_artifact_from_data(_sink_data(rows)).metrics["cost_attribution"]
    assert snap["status"] == "error"
    assert "归因不可算" in snap["error"]
    assert any("成本归因快照失败" in r.getMessage() for r in caplog.records)


def test_injection_point_is_single_choke_point():
    """注入点唯一：除 build_artifact_from_data 外不得有第二处写 cost_attribution（防口径分裂）。"""
    import inspect

    from zephyr.backtest.io import result_repository as rr

    src = inspect.getsource(rr)
    assert src.count('metrics["cost_attribution"]') == 1
    assert "cost_attribution" not in inspect.getsource(rr.save_artifact)
