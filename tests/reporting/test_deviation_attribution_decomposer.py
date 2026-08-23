# [BLUEPRINT] MOD-RPT-031 | 待统筹登记（battle_map BM-BT-05-H） | §test
# [MODULE] tests.reporting.test_deviation_attribution_decomposer
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.deviation_attribution_decomposer
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;纯函数直注零 DB/网络
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] test_deviation_attribution_decomposer.py
# [A_test] module_id: MOD-RPT-031 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RPT-031 单元测试: 回测-实盘偏离归因分解器（battle_map BM-BT-05-H 四因子）。

覆盖：
- 四因子全量分解：explained/residual/dominant/share 数值断言 + 加性不变量 PASS；
- 子维度闭合：dimensions 合计须等于因子偏差（battle_map "归因到子维度" 口径），
  不闭合 fail-closed；
- 降级口径（battle_map ⑥）：measured=False 因子不参与分解、unmeasured_factors
  留痕；全未就绪 → 仅总值偏差 + dominant=None；
- fail-closed：未知因子/重复因子/NaN/inf/未就绪因子携带数值；
- 边界：total=0、空因子序列、残差大于已解释部分 notes 提示；
- 契约：frozen、to_dict JSON 可序列化。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.reporting.deviation_attribution_decomposer import (
    FACTOR_H_A,
    FACTOR_H_B,
    FACTOR_H_C,
    FACTOR_H_D,
    DeviationAttribution,
    DimensionBias,
    FactorBias,
    InvalidDeviationAttributionError,
    decompose_deviation_attribution,
)


def _full_factors() -> list[FactorBias]:
    return [
        FactorBias(factor=FACTOR_H_A, bias=-0.020),
        FactorBias(factor=FACTOR_H_B, bias=-0.010),
        FactorBias(factor=FACTOR_H_C, bias=-0.005),
        FactorBias(factor=FACTOR_H_D, bias=-0.010),
    ]


# ----------------------------------------------------------------------
# 全量分解
# ----------------------------------------------------------------------


class TestFullDecomposition:
    def test_four_factor_values(self) -> None:
        r = decompose_deviation_attribution(-0.050, _full_factors())
        assert r.total_deviation == pytest.approx(-0.050)
        assert r.explained_deviation == pytest.approx(-0.045)
        assert r.unexplained_residual == pytest.approx(-0.005)
        assert r.invariant_status == "PASS"
        assert r.unmeasured_factors == ()

    def test_dominant_factor_by_abs(self) -> None:
        r = decompose_deviation_attribution(-0.050, _full_factors())
        assert r.dominant_factor == FACTOR_H_A  # |-0.020| 最大

    def test_dominant_positive_bias_wins(self) -> None:
        factors = [
            FactorBias(factor=FACTOR_H_A, bias=-0.01),
            FactorBias(factor=FACTOR_H_D, bias=0.03),
        ]
        r = decompose_deviation_attribution(0.020, factors)
        assert r.dominant_factor == FACTOR_H_D

    def test_share_of_total_signed(self) -> None:
        r = decompose_deviation_attribution(-0.040, _full_factors())
        shares = {f.factor: f.share_of_total for f in r.factors}
        assert shares[FACTOR_H_A] == pytest.approx(0.5)
        assert shares[FACTOR_H_C] == pytest.approx(0.125)

    def test_factor_order_preserved(self) -> None:
        r = decompose_deviation_attribution(-0.050, _full_factors())
        assert [f.factor for f in r.factors] == [FACTOR_H_A, FACTOR_H_B, FACTOR_H_C, FACTOR_H_D]


# ----------------------------------------------------------------------
# 子维度闭合（battle_map "归因到子维度" 口径）
# ----------------------------------------------------------------------


class TestDimensions:
    def test_dimensions_partition_ok(self) -> None:
        factors = [
            FactorBias(
                factor=FACTOR_H_A,
                bias=-0.020,
                dimensions=(
                    DimensionBias("模型简化偏差", -0.008),
                    DimensionBias("流动性误判", -0.006),
                    DimensionBias("时机漂移", -0.004),
                    DimensionBias("价差变化", -0.002),
                ),
            )
        ]
        r = decompose_deviation_attribution(-0.020, factors)
        dims = {d.name: d.bias for d in r.factors[0].dimensions}
        assert dims["流动性误判"] == pytest.approx(-0.006)

    def test_dimensions_not_closed_raises(self) -> None:
        factors = [
            FactorBias(
                factor=FACTOR_H_A,
                bias=-0.020,
                dimensions=(DimensionBias("模型简化偏差", -0.008),),
            )
        ]
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(-0.020, factors)

    def test_dimension_nan_raises(self) -> None:
        factors = [
            FactorBias(
                factor=FACTOR_H_A,
                bias=-0.020,
                dimensions=(DimensionBias("模型简化偏差", float("nan")),),
            )
        ]
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(-0.020, factors)


# ----------------------------------------------------------------------
# 降级口径（battle_map ⑥ 归因未就绪→仅总值偏差）
# ----------------------------------------------------------------------


class TestDegradation:
    def test_unmeasured_factor_excluded(self) -> None:
        factors = [
            FactorBias(factor=FACTOR_H_A, bias=-0.020),
            FactorBias(factor=FACTOR_H_B, measured=False),
        ]
        r = decompose_deviation_attribution(-0.050, factors)
        assert r.explained_deviation == pytest.approx(-0.020)
        assert r.unexplained_residual == pytest.approx(-0.030)
        assert r.unmeasured_factors == (FACTOR_H_B, FACTOR_H_C, FACTOR_H_D)
        assert any("未就绪" in n for n in r.notes)

    def test_all_unmeasured_total_only(self) -> None:
        factors = [FactorBias(factor=f, measured=False) for f in (FACTOR_H_A, FACTOR_H_B, FACTOR_H_C, FACTOR_H_D)]
        r = decompose_deviation_attribution(-0.050, factors)
        assert r.explained_deviation == 0.0
        assert r.unexplained_residual == pytest.approx(-0.050)
        assert r.dominant_factor is None
        assert r.factors == ()
        assert any("仅总值偏差" in n for n in r.notes)

    def test_empty_factors_all_unmeasured(self) -> None:
        r = decompose_deviation_attribution(0.012, [])
        assert r.unmeasured_factors == (FACTOR_H_A, FACTOR_H_B, FACTOR_H_C, FACTOR_H_D)
        assert r.dominant_factor is None
        assert r.unexplained_residual == pytest.approx(0.012)

    def test_unmeasured_with_bias_raises(self) -> None:
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(
                -0.05, [FactorBias(factor=FACTOR_H_A, bias=-0.01, measured=False)]
            )

    def test_unmeasured_with_dimensions_raises(self) -> None:
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(
                -0.05,
                [FactorBias(factor=FACTOR_H_A, measured=False, dimensions=(DimensionBias("x", 0.0),))],
            )


# ----------------------------------------------------------------------
# fail-closed 校验
# ----------------------------------------------------------------------


class TestValidation:
    def test_unknown_factor_raises(self) -> None:
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(-0.05, [FactorBias(factor="H-E", bias=-0.01)])

    def test_duplicate_factor_raises(self) -> None:
        factors = [FactorBias(factor=FACTOR_H_A, bias=-0.01), FactorBias(factor=FACTOR_H_A, bias=-0.02)]
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(-0.05, factors)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_total_raises(self, bad: float) -> None:
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(bad, _full_factors())

    @pytest.mark.parametrize("bad", [float("nan"), float("inf")])
    def test_non_finite_bias_raises(self, bad: float) -> None:
        with pytest.raises(InvalidDeviationAttributionError):
            decompose_deviation_attribution(-0.05, [FactorBias(factor=FACTOR_H_A, bias=bad)])


# ----------------------------------------------------------------------
# 边界与契约
# ----------------------------------------------------------------------


class TestEdgesAndContract:
    def test_zero_total_shares_zero(self) -> None:
        r = decompose_deviation_attribution(0.0, [FactorBias(factor=FACTOR_H_A, bias=-0.01)])
        assert r.factors[0].share_of_total == 0.0
        assert r.unexplained_residual == pytest.approx(0.01)
        assert r.invariant_status == "PASS"

    def test_residual_dominant_note(self) -> None:
        r = decompose_deviation_attribution(-0.050, [FactorBias(factor=FACTOR_H_A, bias=-0.005)])
        assert any("残差" in n for n in r.notes)  # 未解释残差大于已解释部分

    def test_to_dict_json_serializable(self) -> None:
        r = decompose_deviation_attribution(-0.050, _full_factors())
        json.dumps(r.to_dict(), ensure_ascii=False)

    def test_report_frozen(self) -> None:
        r = decompose_deviation_attribution(-0.050, _full_factors())
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.dominant_factor = FACTOR_H_B  # type: ignore[misc]

    def test_return_type(self) -> None:
        r = decompose_deviation_attribution(-0.050, _full_factors())
        assert isinstance(r, DeviationAttribution)
