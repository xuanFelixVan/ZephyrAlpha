# [A_test] module_id: MOD-GOV_test_execution_route_policy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_sor.test_execution_route_policy
# [TESTS] src/zephyr/ex_sor/core/execution_route_policy.py
# [TTL] task_bound
"""90 号 Phase1 项③：执行路由策略（默认限价单+打板专用路径）toy 断言。

裁定真源：90_methodology_open_questions.md §19（v2.0.0）——
  ② 默认单笔限价单；③ 打板逻辑上不可拆单→打板专用执行路径（涨停价限价申报
  +封成比≥5%过滤）；④ 单笔>分钟级均量 5 倍→分 2-3 笔间隔 3-5 秒（防异常交易监控）；
  ⑦ TWAP/VWAP/POV/ICEBERG 算法族降级远期（单票百万+前不启用）；
  ① 删除"单笔>5% ADV 切算法执行"硬条款。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_sor.core.execution_route_policy import (
    ExecutionRoute,
    ExecutionRoutePolicy,
    route_order,
)


class TestDefaults:
    def test_default_route_is_direct_limit(self):
        policy = ExecutionRoutePolicy()
        assert policy.default_route == ExecutionRoute.DIRECT_LIMIT
        # ⑦ 算法族降级远期：默认不启用
        assert policy.algo_enabled is False
        # ③ 打板封成比≥5% 过滤
        assert policy.daban_seal_ratio_min == Decimal("0.05")
        # ④ 异常交易监控拆分阈值=分钟级均量 5 倍
        assert policy.abnormal_volume_multiplier == Decimal("5")


class TestRouteOrder:
    def test_plain_order_direct_limit_single(self):
        decision = route_order(
            order_qty=Decimal("1000"), minute_avg_volume=Decimal("100000")
        )
        assert decision.route == ExecutionRoute.DIRECT_LIMIT
        assert decision.allowed is True
        assert decision.parts == 1

    def test_daban_route_single_limit_no_split(self):
        """打板=抢排队优先级，逻辑上不可拆单：封成比达标→单笔限价（涨停价申报由调用方定价）。"""
        decision = route_order(
            order_qty=Decimal("1000"),
            minute_avg_volume=Decimal("100"),  # 10×分钟均量也不得拆单
            is_daban=True,
            seal_ratio=Decimal("0.06"),
        )
        assert decision.route == ExecutionRoute.DABAN_LIMIT
        assert decision.allowed is True
        assert decision.parts == 1

    def test_daban_weak_seal_blocked(self):
        """封成比<5%→封单强度过滤，打板路径拒绝申报。"""
        decision = route_order(
            order_qty=Decimal("1000"),
            minute_avg_volume=Decimal("100000"),
            is_daban=True,
            seal_ratio=Decimal("0.03"),
        )
        assert decision.route == ExecutionRoute.DABAN_LIMIT
        assert decision.allowed is False

    def test_abnormal_volume_split_3_parts(self):
        """单笔>分钟级均量 5 倍→分 3 笔、间隔 3 秒（2026-04 程序化新规防异常交易监控）。"""
        decision = route_order(
            order_qty=Decimal("6000"), minute_avg_volume=Decimal("1000")
        )
        assert decision.route == ExecutionRoute.DIRECT_LIMIT
        assert decision.parts == 3
        assert decision.split_interval_seconds == 3

    def test_algo_never_selected_when_disabled(self):
        """①⑦ 删除 5%ADV 硬条款+算法族降级远期：即使超大单也不路由算法执行。"""
        decision = route_order(
            order_qty=Decimal("1000000"), minute_avg_volume=Decimal("1000000")
        )
        assert decision.route != ExecutionRoute.ALGO

    def test_invalid_qty_raises(self):
        with pytest.raises(ValueError):
            route_order(order_qty=Decimal("0"), minute_avg_volume=Decimal("1000"))
