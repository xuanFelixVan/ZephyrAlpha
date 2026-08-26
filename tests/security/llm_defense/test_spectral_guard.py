# [BLUEPRINT] MOD-SECLLM-002 | docs/03_modules/_domain_security_llm/spectral_guard/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SECLLM-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.security.llm_defense.test_spectral_guard
# [TESTS] src/zephyr/security/llm_defense/spectral_guard.py
"""MOD-SECLLM-002 单元测试：spectral_guard Spectral 注意力谱幻觉检测器。

蓝图验收（B10-01868/CAND-SECLLM-001，A1 §29.24-7）：注意力矩阵→Laplacian
谱能量特征（度-邻接，谱集中度/归一化谱熵，纯 numpy）+ 幻觉评分（能量分
散度）+ 分模型双阈值表注入（Qwen/DeepSeek）+ recall 优先判定。阈值表全
注入内存替身，纯内存确定性。
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip(
    "zephyr.security.llm_defense.spectral_guard",
    reason="spectral_guard not importable",
)

from zephyr.security.llm_defense.spectral_guard import (  # noqa: E402
    SpectralGuard,
    SpectralGuardError,
    SpectralThresholds,
    Verdict,
)

_THRESHOLDS = {
    "qwen": SpectralThresholds(warn=0.4, block=0.6),
    "deepseek": SpectralThresholds(warn=0.3, block=0.55),
}

#: 均匀注意力（能量最分散）n=3 → L 特征值 {0,3,3}，dispersion=ln2/ln3
_UNIFORM3 = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
#: 星型注意力（中度分散）→ L 特征值 {0,1,3}
_STAR3 = [[0.0, 1.0, 1.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
#: 对角注意力（能量零分散）→ L 全零
_DIAG3 = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

_UNIFORM3_DISPERSION = math.log(2) / math.log(3)


def _guard(**overrides) -> SpectralGuard:
    kwargs = {"thresholds": _THRESHOLDS}
    kwargs.update(overrides)
    return SpectralGuard(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_thresholds_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard(thresholds={})

    def test_empty_model_name_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard(thresholds={"": SpectralThresholds(0.1, 0.2)})

    def test_warn_above_block_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard(thresholds={"qwen": SpectralThresholds(0.7, 0.6)})

    def test_threshold_out_of_range_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard(thresholds={"qwen": SpectralThresholds(-0.1, 0.6)})
        with pytest.raises(SpectralGuardError):
            SpectralGuard(thresholds={"qwen": SpectralThresholds(0.4, 1.1)})

    def test_illegal_threshold_type_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard(thresholds={"qwen": (0.4, 0.6)})


# ──────────────────────────────────────────────────────────────────────────────
# 谱特征
# ──────────────────────────────────────────────────────────────────────────────


class TestFeatures:
    def test_uniform_max_dispersion(self) -> None:
        feats = SpectralGuard.features(_UNIFORM3)
        assert feats.size == 3
        assert feats.spectral_entropy == pytest.approx(math.log(2))
        assert feats.dispersion == pytest.approx(_UNIFORM3_DISPERSION)
        assert feats.concentration == pytest.approx(0.5)

    def test_star_mid_dispersion(self) -> None:
        feats = SpectralGuard.features(_STAR3)
        expected_entropy = -(0.25 * math.log(0.25) + 0.75 * math.log(0.75))
        assert feats.spectral_entropy == pytest.approx(expected_entropy)
        assert feats.concentration == pytest.approx(0.75)
        assert 0.0 < feats.dispersion < _UNIFORM3_DISPERSION

    def test_diagonal_zero_energy(self) -> None:
        feats = SpectralGuard.features(_DIAG3)
        assert feats.spectral_entropy == 0.0
        assert feats.dispersion == 0.0
        assert feats.concentration == 1.0

    def test_single_element_matrix(self) -> None:
        feats = SpectralGuard.features([[2.0]])
        assert feats.size == 1
        assert feats.dispersion == 0.0

    def test_asymmetric_input_symmetrized(self) -> None:
        # 非对称注意力对称化后谱特征确定：单边 (1,2) → L 特征值 {0,0,2}
        feats = SpectralGuard.features([[0.0, 2.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        assert feats.spectral_entropy == 0.0  # 能量全集中于单一特征值
        assert feats.dispersion == 0.0
        assert feats.concentration == 1.0

    def test_non_square_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard.features([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

    def test_empty_matrix_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard.features([[]])

    def test_negative_value_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard.features([[1.0, -0.5], [0.0, 1.0]])

    def test_non_finite_raises(self) -> None:
        with pytest.raises(SpectralGuardError):
            SpectralGuard.features([[1.0, float("nan")], [0.0, 1.0]])
        with pytest.raises(SpectralGuardError):
            SpectralGuard.features([[1.0, float("inf")], [0.0, 1.0]])


# ──────────────────────────────────────────────────────────────────────────────
# 幻觉判定（分模型双阈值 + recall 优先）
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_clean_below_warn(self) -> None:
        result = _guard().evaluate("qwen", _DIAG3)
        assert result.score == 0.0
        assert result.verdict is Verdict.CLEAN
        assert result.is_hallucination is False

    def test_hallucinated_above_block(self) -> None:
        result = _guard().evaluate("qwen", _UNIFORM3)
        assert result.verdict is Verdict.HALLUCINATED
        assert result.is_hallucination is True

    def test_suspect_recall_first_counts_positive(self) -> None:
        result = _guard().evaluate("qwen", _STAR3)
        assert result.verdict is Verdict.SUSPECT
        assert result.is_hallucination is True  # recall 优先：疑似按阳性计

    def test_suspect_not_recall_first_counts_negative(self) -> None:
        result = _guard(recall_first=False).evaluate("qwen", _STAR3)
        assert result.verdict is Verdict.SUSPECT
        assert result.is_hallucination is False

    def test_per_model_thresholds_differ(self) -> None:
        # 同一矩阵：deepseek block=0.55 < qwen block=0.6 → 判定不同
        matrix = _UNIFORM3  # dispersion≈0.6309，两模型均 block
        assert _guard().evaluate("deepseek", matrix).verdict is Verdict.HALLUCINATED
        # star dispersion≈0.512：deepseek(0.3~0.55)=SUSPECT，qwen(0.4~0.6)=SUSPECT
        assert _guard().evaluate("deepseek", _STAR3).verdict is Verdict.SUSPECT

    def test_unregistered_model_fail_closed(self) -> None:
        with pytest.raises(SpectralGuardError):
            _guard().evaluate("gpt-x", _UNIFORM3)

    def test_result_carries_features(self) -> None:
        result = _guard().evaluate("qwen", _STAR3)
        assert result.features.size == 3
        assert result.score == result.features.dispersion

    def test_determinism_same_input_same_result(self) -> None:
        guard = _guard()
        r1 = guard.evaluate("deepseek", _UNIFORM3)
        r2 = guard.evaluate("deepseek", _UNIFORM3)
        assert r1 == r2
