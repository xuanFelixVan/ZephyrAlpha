# [BLUEPRINT] MOD-EX-049 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-EXE-daban_execution_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_execution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板执行族单元测试（§3.13 缺失#4 DabanExecutionAlgorithm / §3.14 缺失#11 DabanTimingDecision / 缺失#12 DynamicCapacityCalculator）。

覆盖：
  - estimate_fill_probability：基础强度/距离指数衰减/队列位置衰减/零订单量边界
  - estimate_sar：深度+集中度/仅前 5 档/空订单簿兜底
  - build_execution_plan：三段计划齐全+总量守恒/SaR>2%→SAR_TRIM 削 30%/小额目标边界
  - decide_timing：CHASE/AMBUSH/封流比不足拦截/概率下边界 0.5（spec 登记①：WAIT 不可达）
  - DynamicCapacityCalculator.calculate：四约束各 binding/sar/seal/nav/空订单簿→0/price<=0→0

依据：24_daban_strategy_detail.md v1.9.2 §3.13 缺失#4 / v1.9.3 §3.14 缺失#11/#12
"""

from __future__ import annotations

import math

import pytest

from zephyr.ex_core.daban_execution import (
    DabanExecutionAlgorithm,
    DabanTimingDecision,
    DynamicCapacityCalculator,
)

# ---------------------------------------------------------------------
# DabanExecutionAlgorithm（§3.13#4）
# ---------------------------------------------------------------------


class TestEstimateFillProbability:
    def test_full_fill_base_case(self):
        """封单充足+队首+零距离→填充概率 1.0。"""
        algo = DabanExecutionAlgorithm()
        assert algo.estimate_fill_probability(0, 100_000, 1_000) == pytest.approx(1.0)

    def test_queue_position_decay(self):
        """队列位置衰减 0.85^queue：queue=2→0.7225。"""
        algo = DabanExecutionAlgorithm()
        assert algo.estimate_fill_probability(2, 100_000, 1_000) == pytest.approx(0.7225)

    def test_distance_exponential_decay(self):
        """距 midprice 指数衰减 exp(-κ·d)：κ=0.20/d=5→e^-1。"""
        algo = DabanExecutionAlgorithm()
        got = algo.estimate_fill_probability(0, 100_000, 1_000, distance_to_mid=5.0)
        assert got == pytest.approx(math.exp(-1.0))

    def test_base_prob_seal_order_ratio(self):
        """基础强度=封单/(订单×10) 夹取：seal=500/order=1000→0.05。"""
        algo = DabanExecutionAlgorithm()
        assert algo.estimate_fill_probability(0, 500, 1_000) == pytest.approx(0.05)

    def test_zero_order_volume_no_crash(self):
        """边界：订单量 0→分母兜底为 1，不抛异常。"""
        algo = DabanExecutionAlgorithm()
        assert algo.estimate_fill_probability(0, 10, 0) == pytest.approx(1.0)


class TestEstimateSar:
    def test_depth_and_concentration(self):
        """SaR=(q/depth)·(1+concentration)·η：depth=11500/conc=5000/11500。"""
        algo = DabanExecutionAlgorithm()
        book = {"bid_levels": [{"volume": v} for v in (5000, 3000, 2000, 1000, 500)]}
        expected = (1000 / 11500) * (1 + 5000 / 11500) * 0.001
        assert algo.estimate_sar(book, 1000) == pytest.approx(expected)

    def test_only_top5_levels_counted(self):
        """深度仅取前 5 档：第 6 档不计入 depth，但集中度取全簿最大档。"""
        algo = DabanExecutionAlgorithm()
        book = {"bid_levels": [{"volume": 100}] * 5 + [{"volume": 10_000}]}
        # depth=500；concentration=max(全簿)/depth=10000/500=20（spec 原文 max 不限前 5 档）
        expected = (1000 / 500) * (1 + 20) * 0.001
        assert algo.estimate_sar(book, 1000) == pytest.approx(expected)

    def test_empty_order_book_fail_closed(self):
        """异常：空订单簿→depth=0/concentration=0 兜底，sar=order×η（保守放大不崩）。"""
        algo = DabanExecutionAlgorithm()
        assert algo.estimate_sar({"bid_levels": []}, 1000) == pytest.approx(1.0)
        assert algo.estimate_sar({}, 1000) == pytest.approx(1.0)


class TestBuildExecutionPlan:
    def test_three_batch_plan_volume_conserved(self):
        """无订单簿：FIRST 60%/REFLUSH 30%/RESERVE 余量，总量守恒。"""
        algo = DabanExecutionAlgorithm()
        plan = algo.build_execution_plan(10_000, 1_000_000, 0)
        assert [b["batch"] for b in plan] == ["FIRST", "REFLUSH", "RESERVE"]
        assert [b["qty"] for b in plan] == [6000, 3000, 1000]
        assert sum(b["qty"] for b in plan) == 10_000
        assert plan[0]["timing"] == "SEAL_INSTANT" and plan[0]["fill_prob"] == pytest.approx(1.0)
        assert plan[1]["timing"] == "RESEAL" and plan[1]["fill_prob"] == pytest.approx(0.85**5)
        assert plan[2]["timing"] == "OPPORTUNISTIC" and plan[2]["fill_prob"] == pytest.approx(0.3)

    def test_sar_trim_when_slippage_above_2pct(self):
        """浅簿 SaR≈2.2%>2%→SAR_TRIM 削 30%，后续三段按 7000 拆分。"""
        algo = DabanExecutionAlgorithm()
        book = {"bid_levels": [{"volume": 900}]}  # sar=(10000/900)·2·0.001≈0.0222
        plan = algo.build_execution_plan(10_000, 1_000_000, 0, order_book=book)
        assert plan[0]["batch"] == "SAR_TRIM" and plan[0]["qty"] == 7000
        assert [b["batch"] for b in plan[1:]] == ["FIRST", "REFLUSH", "RESERVE"]
        assert sum(b["qty"] for b in plan[1:]) == 7000

    def test_sar_exactly_2pct_not_trimmed(self):
        """边界：SaR 恰好=2%（不>2%）→不削减。"""
        algo = DabanExecutionAlgorithm()
        book = {"bid_levels": [{"volume": 1000}]}  # sar=(10000/1000)·2·0.001=0.020
        plan = algo.build_execution_plan(10_000, 1_000_000, 0, order_book=book)
        assert plan[0]["batch"] == "FIRST"

    def test_tiny_target_volume(self):
        """边界：目标 3 股→1/0/2，总量守恒无负量。"""
        algo = DabanExecutionAlgorithm()
        plan = algo.build_execution_plan(3, 1_000_000, 0)
        assert [b["qty"] for b in plan] == [1, 0, 2]
        assert sum(b["qty"] for b in plan) == 3


# ---------------------------------------------------------------------
# DabanTimingDecision（§3.14#11）
# ---------------------------------------------------------------------


class TestDecideTiming:
    def test_chase_market_order(self):
        """封板概率 0.95（封顶）≥85%+封流比 6%≥5%→CHASE 市价单。"""
        dec = DabanTimingDecision()
        out = dec.decide_timing(near_limit=True, seal_strength=0.06, volume_surge=1.0, time_to_close_min=60)
        assert out["action"] == "CHASE" and out["order_type"] == "MARKET"

    def test_chase_blocked_by_weak_seal_falls_to_ambush(self):
        """封板概率达标但封流比 4%<5%→不追板，落 AMBUSH 限价单。"""
        dec = DabanTimingDecision()
        out = dec.decide_timing(near_limit=True, seal_strength=0.04, volume_surge=1.0, time_to_close_min=60)
        assert out["action"] == "AMBUSH"
        assert out["order_type"] == "LIMIT" and out["max_wait"] == 120

    def test_ambush_mid_probability(self):
        """封板概率 50-85%→AMBUSH：near_limit=False/seal=5%/surge=1.0→0.5+0.2+0.1=0.8。"""
        dec = DabanTimingDecision()
        out = dec.decide_timing(near_limit=False, seal_strength=0.05, volume_surge=1.0, time_to_close_min=60)
        assert out["action"] == "AMBUSH"

    def test_probability_floor_is_0_5_ambush(self):
        """边界（spec 登记①）：概率公式下限 0.5（全零输入）→恰达 AMBUSH 阈值，WAIT 分支不可达。"""
        dec = DabanTimingDecision()
        out = dec.decide_timing(near_limit=False, seal_strength=0.0, volume_surge=0.0, time_to_close_min=10)
        assert dec._estimate_seal_probability(False, 0.0, 0.0) == pytest.approx(0.5)
        assert out["action"] == "AMBUSH"

    def test_probability_capped_at_0_95(self):
        """边界：强信号叠加→概率封顶 0.95。"""
        dec = DabanTimingDecision()
        assert dec._estimate_seal_probability(True, 1.0, 10.0) == pytest.approx(0.95)


# ---------------------------------------------------------------------
# DynamicCapacityCalculator（§3.14#12）
# ---------------------------------------------------------------------


def _deep_book() -> dict:
    return {"bid_levels": [{"volume": v} for v in (4_000_000, 3_000_000, 2_000_000, 1_000_000, 500_000)]}


class TestDynamicCapacityCalculator:
    def test_nav_binding(self):
        """深簿+充足封单/流通盘→NAV 约束 binding（C12 单票 5% NAV）。"""
        calc = DynamicCapacityCalculator()
        out = calc.calculate(
            nav=1_000_000, seal_volume=1_000_000, float_shares=100_000_000, order_book=_deep_book(), price=10.0
        )
        assert out["binding_constraint"] == "nav" and out["max_qty"] == 5000
        assert set(out["all_constraints"]) == {"sar", "seal", "float", "nav"}

    def test_sar_binding_shallow_book(self):
        """浅簿→SaR 反推容量 binding：int(0.015·100/((1+1)·0.001))=750。"""
        calc = DynamicCapacityCalculator()
        out = calc.calculate(
            nav=1_000_000,
            seal_volume=1_000_000,
            float_shares=100_000_000,
            order_book={"bid_levels": [{"volume": 100}]},
            price=10.0,
        )
        assert out["binding_constraint"] == "sar" and out["max_qty"] == 750

    def test_seal_binding(self):
        """封单量小→封单 10% 约束 binding。"""
        calc = DynamicCapacityCalculator()
        out = calc.calculate(
            nav=1_000_000, seal_volume=1000, float_shares=100_000_000, order_book=_deep_book(), price=10.0
        )
        assert out["binding_constraint"] == "seal" and out["max_qty"] == 100

    def test_float_binding(self):
        """流通盘小→流通盘 2% 约束 binding。"""
        calc = DynamicCapacityCalculator()
        out = calc.calculate(
            nav=1_000_000, seal_volume=1_000_000, float_shares=100_000, order_book=_deep_book(), price=10.0
        )
        assert out["binding_constraint"] == "float" and out["max_qty"] == 2000

    def test_empty_order_book_zero_capacity(self):
        """异常：空订单簿→depth=0→sar 容量 0→可下 0 股（Fail-Closed）。"""
        calc = DynamicCapacityCalculator()
        out = calc.calculate(
            nav=1_000_000, seal_volume=1_000_000, float_shares=100_000_000, order_book={"bid_levels": []}, price=10.0
        )
        assert out["max_qty"] == 0 and out["binding_constraint"] == "sar"

    def test_zero_price_fail_closed(self):
        """异常：price<=0→nav 容量 0→拒绝下仓（Fail-Closed 不抛异常）。"""
        calc = DynamicCapacityCalculator()
        out = calc.calculate(
            nav=1_000_000, seal_volume=1_000_000, float_shares=100_000_000, order_book=_deep_book(), price=0.0
        )
        assert out["max_qty"] == 0 and out["binding_constraint"] == "nav"
