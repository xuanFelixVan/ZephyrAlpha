# [BLUEPRINT] MOD-DATSEC-003 | docs/03_modules/_domain_data_security/data_masking_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATSEC-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_security.test_data_masking_engine
# [TESTS] src/zephyr/data_security/data_masking_engine.py
"""MOD-DATSEC-003 单元测试：data_masking_engine 数据脱敏引擎。

蓝图验收（B13-04295/CAND-DATSEC-003，A3数据架构）：
格式保留加密（注入 cipher 回调 / 默认确定性伪 FPE 占位，非密码学安全）+
动态脱敏（角色策略表：同字段不同角色不同掩码，未注册 Fail-Closed）+
差分隐私拉普拉斯噪声（ε 可配，随机源注入确定性复现）。不触网。
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip(
    "zephyr.data_security.data_masking_engine",
    reason="data_masking_engine not importable",
)

from zephyr.data_security.data_masking_engine import (  # noqa: E402
    DataMaskingEngine,
    DataMaskingError,
    MaskKind,
)


def _engine(**kw) -> DataMaskingEngine:
    return DataMaskingEngine(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 格式保留加密（默认伪 FPE 占位）
# ──────────────────────────────────────────────────────────────────────────────


class TestFpe:
    def test_encrypt_preserves_digit_format(self) -> None:
        engine = _engine()
        text = "110101199003077777"
        out = engine.fpe_encrypt(text)
        assert len(out) == len(text)
        assert out.isdigit()
        assert out != text

    def test_encrypt_preserves_mixed_format(self) -> None:
        engine = _engine()
        out = engine.fpe_encrypt("Ab3-xY9z")
        assert len(out) == 8
        assert out[0].isupper() and out[1].islower() and out[2].isdigit()
        assert out[3] == "-"  # 类外字符原样保留
        assert out[4].islower() and out[5].isupper() and out[6].isdigit() and out[7].islower()

    def test_decrypt_roundtrip(self) -> None:
        engine = _engine()
        for text in ("110101199003077777", "Ab3-xY9z", "6222020200112233"):
            assert engine.fpe_decrypt(engine.fpe_encrypt(text)) == text

    def test_encrypt_deterministic(self) -> None:
        assert _engine().fpe_encrypt("abc123") == _engine().fpe_encrypt("abc123")

    def test_different_keys_differ(self) -> None:
        assert _engine(key="k1").fpe_encrypt("abc123") != _engine(key="k2").fpe_encrypt(
            "abc123"
        )

    def test_empty_text_raises(self) -> None:
        engine = _engine()
        with pytest.raises(DataMaskingError):
            engine.fpe_encrypt("")
        with pytest.raises(DataMaskingError):
            engine.fpe_decrypt("")

    def test_empty_key_raises(self) -> None:
        with pytest.raises(DataMaskingError):
            DataMaskingEngine(key="")

    def test_cipher_callback_injected(self) -> None:
        seen: list[tuple[str, str, bool]] = []

        def _cipher(text: str, key: str, encrypt: bool) -> str:
            seen.append((text, key, encrypt))
            return text[::-1]

        engine = _engine(key="kw", cipher=_cipher)
        assert engine.fpe_encrypt("abc123") == "321cba"
        assert seen == [("abc123", "kw", True)]

    def test_cipher_callback_decrypt_flag(self) -> None:
        engine = _engine(cipher=lambda t, _k, e: t[::-1] if e else t[::-1])
        assert engine.fpe_decrypt("xyz") == "zyx"


# ──────────────────────────────────────────────────────────────────────────────
# 动态脱敏（角色策略表）
# ──────────────────────────────────────────────────────────────────────────────


class TestDynamicMask:
    def _engine_with_policies(self) -> DataMaskingEngine:
        engine = _engine()
        engine.register_policy("admin", "id_card", MaskKind.NONE)
        engine.register_policy("analyst", "id_card", MaskKind.PARTIAL)
        engine.register_policy("guest", "id_card", MaskKind.FULL)
        engine.register_policy("auditor", "id_card", MaskKind.HASH)
        return engine

    def test_same_field_different_roles(self) -> None:
        engine = self._engine_with_policies()
        value = "110101199003077777"
        assert engine.mask_field("admin", "id_card", value) == value
        assert engine.mask_field("analyst", "id_card", value) == "1****************7"
        assert engine.mask_field("guest", "id_card", value) == "*" * 18
        assert engine.mask_field("auditor", "id_card", value).startswith("h:")

    def test_unregistered_policy_raises(self) -> None:
        engine = _engine()
        engine.register_policy("admin", "id_card", MaskKind.NONE)
        with pytest.raises(DataMaskingError):
            engine.mask_field("ghost", "id_card", "110")
        with pytest.raises(DataMaskingError):
            engine.mask_field("admin", "phone", "110")
        with pytest.raises(DataMaskingError):
            engine.policy_of("ghost", "id_card")

    def test_partial_mask_short_values(self) -> None:
        engine = _engine()
        engine.register_policy("r", "f", MaskKind.PARTIAL)
        assert engine.mask_field("r", "f", "张三") == "张*"
        assert engine.mask_field("r", "f", "张") == "*"
        assert engine.mask_field("r", "f", "") == ""

    def test_full_mask_empty_value(self) -> None:
        engine = _engine()
        engine.register_policy("r", "f", MaskKind.FULL)
        assert engine.mask_field("r", "f", "") == ""

    def test_hash_mask_deterministic(self) -> None:
        engine = self._engine_with_policies()
        first = engine.mask_field("auditor", "id_card", "110101199003077777")
        second = engine.mask_field("auditor", "id_card", "110101199003077777")
        assert first == second
        assert len(first) == 2 + 8  # "h:" + 8 位摘要

    def test_register_overwrite(self) -> None:
        engine = _engine()
        engine.register_policy("r", "f", MaskKind.FULL)
        engine.register_policy("r", "f", MaskKind.NONE)  # 覆盖式登记
        assert engine.policy_of("r", "f") is MaskKind.NONE

    def test_register_invalid_input_raises(self) -> None:
        engine = _engine()
        with pytest.raises(DataMaskingError):
            engine.register_policy("", "f", MaskKind.FULL)
        with pytest.raises(DataMaskingError):
            engine.register_policy("r", "", MaskKind.FULL)
        with pytest.raises(DataMaskingError):
            engine.register_policy("r", "f", "full")  # type: ignore[arg-type]

    def test_mask_non_string_value_raises(self) -> None:
        engine = _engine()
        engine.register_policy("r", "f", MaskKind.FULL)
        with pytest.raises(DataMaskingError):
            engine.mask_field("r", "f", 123)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 差分隐私（拉普拉斯噪声，随机源注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestLaplace:
    def test_zero_noise_at_center(self) -> None:
        engine = _engine(rng=lambda: 0.5)  # u'=0 → log(1)=0 → 零噪声
        assert engine.add_laplace_noise(100.0, epsilon=1.0) == pytest.approx(100.0)

    def test_fixed_rng_deterministic(self) -> None:
        engine = _engine(rng=lambda: 0.9)  # u'=0.4 → noise = scale*ln5
        expected = 100.0 + (1.0 / 0.5) * math.log(5)
        out = engine.add_laplace_noise(100.0, epsilon=0.5, sensitivity=1.0)
        assert out == pytest.approx(expected)

    def test_negative_side_noise(self) -> None:
        engine = _engine(rng=lambda: 0.1)  # u'=-0.4 → noise = -scale*ln5
        out = engine.add_laplace_noise(100.0, epsilon=1.0, sensitivity=2.0)
        assert out == pytest.approx(100.0 - 2.0 * math.log(5))

    def test_smaller_epsilon_larger_noise(self) -> None:
        strong = _engine(rng=lambda: 0.9).add_laplace_noise(0.0, epsilon=0.1)
        weak = _engine(rng=lambda: 0.9).add_laplace_noise(0.0, epsilon=10.0)
        assert abs(strong) > abs(weak)

    def test_invalid_epsilon_raises(self) -> None:
        engine = _engine(rng=lambda: 0.5)
        with pytest.raises(DataMaskingError):
            engine.add_laplace_noise(1.0, epsilon=0.0)
        with pytest.raises(DataMaskingError):
            engine.add_laplace_noise(1.0, epsilon=-1.0)

    def test_invalid_sensitivity_raises(self) -> None:
        engine = _engine(rng=lambda: 0.5)
        with pytest.raises(DataMaskingError):
            engine.add_laplace_noise(1.0, epsilon=1.0, sensitivity=0.0)

    def test_non_numeric_value_raises(self) -> None:
        engine = _engine(rng=lambda: 0.5)
        with pytest.raises(DataMaskingError):
            engine.add_laplace_noise("100", epsilon=1.0)  # type: ignore[arg-type]

    def test_rng_out_of_range_raises(self) -> None:
        with pytest.raises(DataMaskingError):
            _engine(rng=lambda: 1.0).add_laplace_noise(1.0, epsilon=1.0)
        with pytest.raises(DataMaskingError):
            _engine(rng=lambda: "x").add_laplace_noise(1.0, epsilon=1.0)  # type: ignore[arg-type]
