# [BLUEPRINT] MOD-INF-086 | docs/03_modules/_domain_infrastructure_operations/storage_cost_calculator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-086 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_ops.test_storage_cost_calculator
# [TESTS] src/zephyr/infra_ops/storage_cost_calculator.py
"""MOD-INF-086 单元测试：storage_cost_calculator 存储成本量化核算器。

蓝图验收（B13-04333/CAND-INFRAOPS-004，A3数据架构）：
热/温/冷三层占用字节采集（注入 probe）+ TB 单价表（本地盘折旧折算）+
cost_calculator() 对比报表（字典结构）+ 归档收益量化（归档前后成本差）。
全内存替身，确定性换算（TB=1024**4），不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.infra_ops.storage_cost_calculator",
    reason="storage_cost_calculator not importable",
)

from zephyr.infra_ops.storage_cost_calculator import (  # noqa: E402
    TB_BYTES,
    StorageCostCalculator,
    StorageCostError,
    StorageLayer,
    derive_tb_price,
)

_PRICES = {
    StorageLayer.HOT: 300.0,
    StorageLayer.WARM: 100.0,
    StorageLayer.COLD: 30.0,
}


def _calc(usage=None, probe="default") -> StorageCostCalculator:
    if probe == "default":
        probe = lambda: usage if usage is not None else {}  # noqa: E731
    return StorageCostCalculator(usage_probe=probe, price_per_tb_month=_PRICES)


# ──────────────────────────────────────────────────────────────────────────────
# 折旧折算 TB 单价
# ──────────────────────────────────────────────────────────────────────────────


class TestDeriveTbPrice:
    def test_ok(self) -> None:
        # 12000 元盘 / 4TB / 30 个月摊销 = 100 元/TB/月
        assert derive_tb_price(disk_cost=12000.0, disk_tb=4.0, amortize_months=30) == pytest.approx(100.0)

    def test_negative_cost_raises(self) -> None:
        with pytest.raises(StorageCostError):
            derive_tb_price(disk_cost=-1.0, disk_tb=4.0, amortize_months=36)

    def test_zero_tb_raises(self) -> None:
        with pytest.raises(StorageCostError):
            derive_tb_price(disk_cost=100.0, disk_tb=0.0, amortize_months=36)

    def test_zero_months_raises(self) -> None:
        with pytest.raises(StorageCostError):
            derive_tb_price(disk_cost=100.0, disk_tb=4.0, amortize_months=0)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConstruct:
    def test_empty_price_table_raises(self) -> None:
        with pytest.raises(StorageCostError):
            StorageCostCalculator(usage_probe=lambda: {}, price_per_tb_month={})

    def test_missing_layer_raises(self) -> None:
        with pytest.raises(StorageCostError):
            StorageCostCalculator(
                usage_probe=lambda: {},
                price_per_tb_month={StorageLayer.HOT: 1.0, StorageLayer.WARM: 1.0},
            )

    def test_negative_price_raises(self) -> None:
        bad = dict(_PRICES, **{StorageLayer.COLD: -1.0})
        with pytest.raises(StorageCostError):
            StorageCostCalculator(usage_probe=lambda: {}, price_per_tb_month=bad)


# ──────────────────────────────────────────────────────────────────────────────
# 占用采集
# ──────────────────────────────────────────────────────────────────────────────


class TestCollectUsage:
    def test_probe_missing_fail_closed(self) -> None:
        calc = StorageCostCalculator(usage_probe=None, price_per_tb_month=_PRICES)
        with pytest.raises(StorageCostError):
            calc.collect_usage()

    def test_negative_bytes_raises(self) -> None:
        calc = _calc({StorageLayer.HOT: -1})
        with pytest.raises(StorageCostError):
            calc.collect_usage()

    def test_unknown_layer_raises(self) -> None:
        calc = _calc({"hot": 1})  # str 键非 StorageLayer
        with pytest.raises(StorageCostError):
            calc.collect_usage()

    def test_collect_ok(self) -> None:
        calc = _calc({StorageLayer.HOT: 10})
        assert calc.collect_usage() == {StorageLayer.HOT: 10}


# ──────────────────────────────────────────────────────────────────────────────
# 成本报表
# ──────────────────────────────────────────────────────────────────────────────


class TestCostCalculator:
    def test_report_values(self) -> None:
        calc = _calc(
            {
                StorageLayer.HOT: TB_BYTES,  # 1 TB × 300 = 300
                StorageLayer.WARM: 2 * TB_BYTES,  # 2 TB × 100 = 200
                StorageLayer.COLD: TB_BYTES // 2,  # 0.5 TB × 30 = 15
            }
        )
        report = calc.cost_calculator()
        assert report["layers"]["hot"]["monthly_cost"] == pytest.approx(300.0)
        assert report["layers"]["warm"]["monthly_cost"] == pytest.approx(200.0)
        assert report["layers"]["cold"]["monthly_cost"] == pytest.approx(15.0)
        assert report["layers"]["hot"]["tb"] == pytest.approx(1.0)
        assert report["total"]["monthly_cost"] == pytest.approx(515.0)
        assert report["total"]["bytes"] == TB_BYTES * 3 + TB_BYTES // 2

    def test_missing_layer_treated_zero(self) -> None:
        calc = _calc({StorageLayer.HOT: TB_BYTES})
        report = calc.cost_calculator()
        assert report["layers"]["warm"]["bytes"] == 0
        assert report["layers"]["cold"]["monthly_cost"] == 0.0
        assert report["total"]["monthly_cost"] == pytest.approx(300.0)

    def test_deterministic_key_order_and_repeat(self) -> None:
        calc = _calc({StorageLayer.HOT: 1, StorageLayer.WARM: 2, StorageLayer.COLD: 3})
        r1 = calc.cost_calculator()
        r2 = calc.cost_calculator()
        assert list(r1["layers"].keys()) == ["hot", "warm", "cold"]
        assert r1 == r2  # 同输入必同输出

    def test_empty_usage_zero_total(self) -> None:
        report = _calc({}).cost_calculator()
        assert report["total"]["monthly_cost"] == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# 归档收益量化
# ──────────────────────────────────────────────────────────────────────────────


class TestArchiveBenefit:
    def test_saving_and_ratio(self) -> None:
        calc = _calc({})
        before = {StorageLayer.HOT: TB_BYTES}
        after = {StorageLayer.HOT: TB_BYTES // 2, StorageLayer.COLD: TB_BYTES // 2}
        got = calc.archive_benefit(before, after)
        # before=300; after=150+15=165; saving=135; ratio=0.45
        assert got["before_monthly_cost"] == pytest.approx(300.0)
        assert got["after_monthly_cost"] == pytest.approx(165.0)
        assert got["saving_monthly_cost"] == pytest.approx(135.0)
        assert got["saving_ratio"] == pytest.approx(0.45)

    def test_zero_before_ratio_zero(self) -> None:
        calc = _calc({})
        got = calc.archive_benefit({}, {StorageLayer.COLD: TB_BYTES})
        assert got["saving_ratio"] == 0.0
        assert got["saving_monthly_cost"] == pytest.approx(-30.0)  # 成本上升为负收益

    def test_negative_usage_raises(self) -> None:
        calc = _calc({})
        with pytest.raises(StorageCostError):
            calc.archive_benefit({StorageLayer.HOT: -1}, {})

    def test_deterministic(self) -> None:
        calc = _calc({})
        before = {StorageLayer.WARM: 3 * TB_BYTES}
        after = {StorageLayer.COLD: 3 * TB_BYTES}
        assert calc.archive_benefit(before, after) == calc.archive_benefit(before, after)
