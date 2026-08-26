# [BLUEPRINT] MOD-FAC-002 | docs/03_modules/_domain_factor/signature_feature_extractor/blueprint.md | §test
# [A_module] module_id=MOD-FAC-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-FAC-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.factor.test_signature_feature_extractor
# [TESTS] src/zephyr/factor/signature_feature_extractor.py
"""MOD-FAC-002 单元测试：signature_feature_extractor 签名方法特征提取器。

蓝图验收（B10-01834/CAND-FAC-018，A1 §29.8）：
截断 2-4 阶 log-signature（对数变换 + 增量 + 张量积迭代截断）+
阶数护栏 ≤4 防组合爆炸 + 确定性输出（同序列必同向量）。
纯内存数值核，手算样例可核对。
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip(
    "zephyr.factor.signature_feature_extractor",
    reason="signature_feature_extractor not importable",
)

from zephyr.factor.signature_feature_extractor import (  # noqa: E402
    SignatureError,
    SignatureFeatureExtractor,
    SignatureFeatures,
)

_E = math.e


# ──────────────────────────────────────────────────────────────────────────────
# 阶数护栏（≤4 防组合爆炸）
# ──────────────────────────────────────────────────────────────────────────────


class TestOrderGuard:
    def test_order_too_low_raises(self) -> None:
        with pytest.raises(SignatureError):
            SignatureFeatureExtractor(order=1)

    def test_order_too_high_raises(self) -> None:
        with pytest.raises(SignatureError):
            SignatureFeatureExtractor(order=5)

    def test_order_non_int_raises(self) -> None:
        with pytest.raises(SignatureError):
            SignatureFeatureExtractor(order=2.5)  # type: ignore[arg-type]

    def test_order_bool_raises(self) -> None:
        with pytest.raises(SignatureError):
            SignatureFeatureExtractor(order=True)  # type: ignore[arg-type]

    def test_order_bounds_accepted(self) -> None:
        assert SignatureFeatureExtractor(order=2).order == 2
        assert SignatureFeatureExtractor(order=4).order == 4


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_path_too_short(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([(1.0, 2.0)])

    def test_empty_path(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([])

    def test_ragged_path_raises(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([(1.0, 2.0), (1.0,)])

    def test_zero_dim_raises(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([(), ()])

    def test_non_positive_raises(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([(1.0,), (0.0,)])  # log(0) 无定义
        with pytest.raises(SignatureError):
            ex.extract([(1.0,), (-2.0,)])

    def test_non_finite_raises(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([(1.0,), (math.inf,)])
        with pytest.raises(SignatureError):
            ex.extract([(1.0,), (math.nan,)])

    def test_non_numeric_raises(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.extract([(1.0,), ("x",)])  # type: ignore[list-item]

    def test_feature_names_dim_invalid(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        with pytest.raises(SignatureError):
            ex.feature_names(0)


# ──────────────────────────────────────────────────────────────────────────────
# 数值正确性（手算可核对）
# ──────────────────────────────────────────────────────────────────────────────


class TestNumeric:
    def test_feature_count_level_dims(self) -> None:
        ex = SignatureFeatureExtractor(order=3)
        names = ex.feature_names(2)
        assert len(names) == 2 + 4 + 8  # level-k 维数 dim^k
        assert names[0] == "s1_0"
        assert "s2_0_1" in names
        assert "s3_1_0_1" in names

    def test_known_two_increment_path(self) -> None:
        # log 点 (0,0),(1,2),(2,2) → 增量 (1,2),(1,0)
        # sig1=(2,2)；sig2 = (1,2)⊗(1,0) = (1,0,2,0)
        ex = SignatureFeatureExtractor(order=2)
        feats = ex.extract([(1.0, 1.0), (_E, _E**2), (_E**2, _E**2)])
        assert feats.names == ("s1_0", "s1_1", "s2_0_0", "s2_0_1", "s2_1_0", "s2_1_1")
        assert feats.values == pytest.approx((2.0, 2.0, 1.0, 0.0, 2.0, 0.0))

    def test_constant_path_all_zero(self) -> None:
        ex = SignatureFeatureExtractor(order=3)
        feats = ex.extract([(2.0, 3.0), (2.0, 3.0), (2.0, 3.0)])
        assert feats.values == pytest.approx(tuple([0.0] * len(feats.values)))

    def test_single_dim_linear_path(self) -> None:
        # log 点 0,1,2 → 增量 1,1；sig1=1+1=2；sig2 = 1*1 = 1
        ex = SignatureFeatureExtractor(order=2)
        feats = ex.extract([(1.0,), (_E,), (_E**2,)])
        assert feats.values == pytest.approx((2.0, 1.0))

    def test_order4_runs_and_sizes(self) -> None:
        ex = SignatureFeatureExtractor(order=4)
        feats = ex.extract([(1.0, 2.0), (2.0, 3.0), (4.0, 5.0)])
        assert len(feats.values) == 2 + 4 + 8 + 16
        assert len(feats.names) == len(feats.values)

    def test_as_dict_alignment(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        feats = ex.extract([(1.0, 2.0), (2.0, 4.0)])
        d = feats.as_dict()
        assert list(d.keys()) == list(feats.names)
        assert d["s1_0"] == pytest.approx(math.log(2.0))
        assert d["s1_1"] == pytest.approx(math.log(2.0))

    def test_returns_frozen_dataclass(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        feats = ex.extract([(1.0,), (2.0,)])
        assert isinstance(feats, SignatureFeatures)
        assert feats.order == 2 and feats.dim == 1
        with pytest.raises(Exception):
            feats.order = 3  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性（同序列必同向量）
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_vector(self) -> None:
        path = [(1.0, 2.0), (1.5, 2.5), (2.0, 4.0), (3.0, 4.5)]
        ex = SignatureFeatureExtractor(order=3)
        f1, f2 = ex.extract(path), ex.extract(path)
        assert f1 == f2

    def test_int_float_inputs_identical(self) -> None:
        ex = SignatureFeatureExtractor(order=2)
        f_int = ex.extract([(1, 2), (2, 4)])
        f_float = ex.extract([(1.0, 2.0), (2.0, 4.0)])
        assert f_int.values == f_float.values
