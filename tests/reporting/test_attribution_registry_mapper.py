# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] tests.reporting.test_attribution_registry_mapper
# [DOMAIN] D_REPORTING
# [A_module] module_id=MOD-TEST-RPT-MAPPER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""attribution_result 映射函数单元测试（62 号 §7.2 ← 54 号 attribution）。

覆盖:
  - build_attribution_result：method 枚举门禁 / None 字段不写出 / NaN-inf 拒 /
    factor_contributions 数值化
  - map_shapley_to_attribution_result：PASS → factor_based + 贡献映射；
    FAIL → fail-closed 拒；shapley_values 缺失 → 拒
  - map_invariant_to_attribution_result：contribution_ratio + alpha=diff 残差；
    FAIL 仍映射（审计事实）；contributions 缺失 → 拒
  - validate_attribution_result：合规空列表 / method 越枚举 / NaN / 非 dict fc
  - 端到端：用 reporting.attribution 真实产出喂映射（不 mock）
"""

from __future__ import annotations

import pytest

from zephyr.reporting.attribution import (
    shapley_strategy_attribution,
    validate_strategy_pnl_invariant,
)
from zephyr.reporting.attribution_registry_mapper import (
    AttributionMappingError,
    build_attribution_result,
    map_invariant_to_attribution_result,
    map_shapley_to_attribution_result,
    validate_attribution_result,
)


class TestBuild:
    def test_minimal(self):
        assert build_attribution_result("none") == {"method": "none"}

    def test_full_fields(self):
        out = build_attribution_result(
            "brinson",
            allocation_effect=0.01,
            selection_effect=0.02,
            interaction_effect=0.003,
            alpha=0.005,
            factor_contributions={"value": 0.6, "momentum": 0.4},
        )
        assert out["method"] == "brinson"
        assert out["allocation_effect"] == pytest.approx(0.01)
        assert out["factor_contributions"] == {"value": 0.6, "momentum": 0.4}

    def test_none_fields_omitted(self):
        out = build_attribution_result("factor_based", factor_contributions={"a": 1.0})
        assert "alpha" not in out
        assert "allocation_effect" not in out

    @pytest.mark.parametrize("bad", ["shapley", "Brinson", "", None])
    def test_method_enum_gate(self, bad):
        with pytest.raises(AttributionMappingError):
            build_attribution_result(bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), "abc"])
    def test_numeric_gate(self, bad):
        with pytest.raises(AttributionMappingError):
            build_attribution_result("factor_based", alpha=bad)


class TestShapleyMap:
    def test_pass_maps(self):
        shap = shapley_strategy_attribution(
            {
                "s1": [0.01, 0.02, -0.01],
                "s2": [0.005, -0.01, 0.02],
            }
        )
        out = map_shapley_to_attribution_result(shap)
        assert out["method"] == "factor_based"
        assert set(out["factor_contributions"]) == {"s1", "s2"}
        # Shapley 效率公理：Σ 贡献 == 组合收益
        total = sum(out["factor_contributions"].values())
        assert total == pytest.approx(shap["full_portfolio_return"])
        assert validate_attribution_result(out) == []

    def test_fail_rejected(self):
        with pytest.raises(AttributionMappingError):
            map_shapley_to_attribution_result({"invariant_status": "FAIL", "shapley_values": {"s1": 0.1}})

    def test_missing_values_rejected(self):
        with pytest.raises(AttributionMappingError):
            map_shapley_to_attribution_result({"invariant_status": "PASS"})


class TestInvariantMap:
    def test_pass_maps(self):
        inv = validate_strategy_pnl_invariant({"s1": 60.0, "s2": 40.0}, firm_pnl=100.0)
        assert inv["invariant_status"] == "PASS"
        out = map_invariant_to_attribution_result(inv)
        assert out["method"] == "factor_based"
        assert out["factor_contributions"] == {"s1": 0.6, "s2": 0.4}
        assert out["alpha"] == pytest.approx(0.0)
        assert validate_attribution_result(out) == []

    def test_fail_still_maps_residual(self):
        """FAIL 仍映射：alpha=diff 未解释残差（审计事实登记）。"""
        inv = validate_strategy_pnl_invariant({"s1": 60.0}, firm_pnl=100.0)
        assert inv["invariant_status"] == "FAIL"
        out = map_invariant_to_attribution_result(inv)
        assert out["alpha"] == pytest.approx(40.0)

    def test_missing_contributions_rejected(self):
        with pytest.raises(AttributionMappingError):
            map_invariant_to_attribution_result({"strategy_contributions": {}})


class TestValidateShape:
    def test_valid_empty_violations(self):
        assert validate_attribution_result({"method": "none"}) == []

    def test_not_dict(self):
        assert validate_attribution_result("x") != []

    def test_bad_method(self):
        violations = validate_attribution_result({"method": "shapley"})
        assert any("method" in v for v in violations)

    def test_nan_field(self):
        violations = validate_attribution_result({"method": "brinson", "alpha": float("nan")})
        assert violations != []

    def test_bad_factor_contributions(self):
        violations = validate_attribution_result({"method": "factor_based", "factor_contributions": [1, 2]})
        assert violations != []
