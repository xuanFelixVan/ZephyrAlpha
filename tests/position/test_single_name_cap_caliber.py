"""single_name_cap_caliber（单票上限三层口径映射+校验）单元测试。

覆盖：31号 §2.4.1/§5——
- 三层口径映射常量（MOD-POS-001 5% / MOD-POS-021 8% / MOD-POS-010 5%）
- validate_tier_calibers：合法性 + 冗余裁剪 WARNING 检测
- check_production_consistency：映射表 vs 生产默认漂移检测
"""

from __future__ import annotations

import pytest

from zephyr.position.core.single_name_cap_caliber import (
    LAYER_FINAL_HARD,
    LAYER_FIRM_AGG,
    LAYER_PIPELINE_ORDER,
    LAYER_STRATEGY,
    SINGLE_NAME_CAP_LAYERS,
    check_production_consistency,
    validate_tier_calibers,
)


class TestLayerMapping:
    def test_three_layers_present(self) -> None:
        """三层口径映射齐全且与 31号 §2.4.1 真源值一致。"""
        assert set(SINGLE_NAME_CAP_LAYERS) == {LAYER_STRATEGY, LAYER_FIRM_AGG, LAYER_FINAL_HARD}
        assert SINGLE_NAME_CAP_LAYERS[LAYER_STRATEGY] == pytest.approx(0.05)
        assert SINGLE_NAME_CAP_LAYERS[LAYER_FIRM_AGG] == pytest.approx(0.08)
        assert SINGLE_NAME_CAP_LAYERS[LAYER_FINAL_HARD] == pytest.approx(0.05)

    def test_pipeline_order(self) -> None:
        """流水线顺序：策略层 → firm 聚合 → 最终硬限。"""
        assert LAYER_PIPELINE_ORDER == (LAYER_STRATEGY, LAYER_FIRM_AGG, LAYER_FINAL_HARD)


class TestValidateTierCalibers:
    def test_default_mapping_passes_with_redundancy_warning(self) -> None:
        """默认映射：合法但 firm 8% > 最终 5% → 冗余裁剪 WARNING（§2.4.1 登记非错误）。"""
        issues = validate_tier_calibers()
        assert not any(i.startswith("ERROR") for i in issues)
        assert any("WARNING" in i and "冗余" in i for i in issues)

    def test_aligned_tiers_no_warning(self) -> None:
        """三层全对齐（如统一 5%）→ 无任何问题（§5 统一后的目标态）。"""
        aligned = {LAYER_STRATEGY: 0.05, LAYER_FIRM_AGG: 0.05, LAYER_FINAL_HARD: 0.05}
        assert validate_tier_calibers(aligned) == []

    def test_missing_layer_error(self) -> None:
        """缺层 → ERROR。"""
        issues = validate_tier_calibers({LAYER_STRATEGY: 0.05})
        assert any("ERROR" in i and "缺少" in i for i in issues)

    def test_out_of_range_error(self) -> None:
        """cap 越界（≤0 或 >1）→ ERROR。"""
        bad = {LAYER_STRATEGY: 0.05, LAYER_FIRM_AGG: 1.5, LAYER_FINAL_HARD: 0.05}
        issues = validate_tier_calibers(bad)
        assert any("ERROR" in i and "越界" in i for i in issues)

    def test_firm_tighter_than_final_no_redundancy(self) -> None:
        """firm 层 ≤ 最终硬限（如 firm 4% < 最终 5%）→ 无冗余 WARNING。"""
        caps = {LAYER_STRATEGY: 0.05, LAYER_FIRM_AGG: 0.04, LAYER_FINAL_HARD: 0.05}
        issues = validate_tier_calibers(caps)
        assert issues == []


class TestProductionConsistency:
    def test_production_defaults_match_mapping(self) -> None:
        """映射表与三模块生产默认零漂移（漂移检测基线）。"""
        assert check_production_consistency() == []
