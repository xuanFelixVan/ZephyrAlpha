# [BLUEPRINT] MOD-SEC-024 | docs/03_modules/_domain_security/outbound_data_sanitizer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SEC-024 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.security.test_outbound_data_sanitizer
# [TESTS] src/zephyr/security/outbound_data_sanitizer.py
"""MOD-SEC-024 单元测试：outbound_data_sanitizer 外发数据脱敏拦截器。

蓝图验收（B1-00372/CAND-SEC-005，C2）：持仓/策略/因子三类白名单字段级过
滤（白名单外剥离）+ PII/凭证正则词表掩码（递归嵌套）+ 统一出口拦截（未
过检不放行 Fail-Closed）。时钟/词表全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.security.outbound_data_sanitizer",
    reason="outbound_data_sanitizer not importable",
)

from zephyr.security.outbound_data_sanitizer import (  # noqa: E402
    MASK_REPLACEMENT,
    OutboundDataSanitizer,
    OutboundSanitizeError,
    PayloadCategory,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_WHITELISTS = {
    PayloadCategory.POSITIONS: {"symbol", "quantity", "avg_cost"},
    PayloadCategory.STRATEGY: {"strategy_id", "name", "params"},
    PayloadCategory.FACTORS: {"factor_id", "formula", "window"},
}


def _sanitizer(**overrides) -> OutboundDataSanitizer:
    kwargs = {"field_whitelists": _WHITELISTS, "clock": lambda: _T0}
    kwargs.update(overrides)
    return OutboundDataSanitizer(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_whitelists_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            OutboundDataSanitizer(field_whitelists={}, clock=lambda: _T0)

    def test_illegal_category_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            OutboundDataSanitizer(
                field_whitelists={"positions": {"symbol"}}, clock=lambda: _T0
            )

    def test_empty_field_set_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            OutboundDataSanitizer(
                field_whitelists={PayloadCategory.POSITIONS: set()}, clock=lambda: _T0
            )

    def test_empty_field_name_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            OutboundDataSanitizer(
                field_whitelists={PayloadCategory.POSITIONS: {"symbol", ""}},
                clock=lambda: _T0,
            )

    def test_illegal_mask_regex_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            _sanitizer(mask_patterns={"bad": r"(["})

    def test_empty_mask_rule_name_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            _sanitizer(mask_patterns={"": r"x+"})


# ──────────────────────────────────────────────────────────────────────────────
# 白名单字段级过滤
# ──────────────────────────────────────────────────────────────────────────────


class TestWhitelistFilter:
    def test_strip_non_whitelisted_fields(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.POSITIONS,
            {"symbol": "600519", "quantity": 100, "internal_note": "勿外发"},
        )
        assert report.sanitized == {"symbol": "600519", "quantity": 100}
        assert report.stripped_fields == ("internal_note",)
        assert report.kept_fields == ("quantity", "symbol")

    def test_strategy_category(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.STRATEGY,
            {"strategy_id": "s1", "name": "双均线", "secret_source": "x"},
        )
        assert report.sanitized == {"strategy_id": "s1", "name": "双均线"}
        assert report.stripped_fields == ("secret_source",)

    def test_factors_category(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.FACTORS, {"factor_id": "f1", "formula": "close/ma20"}
        )
        assert report.stripped_fields == ()
        assert report.kept_fields == ("factor_id", "formula")

    def test_all_stripped_fail_closed(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            _sanitizer().sanitize(PayloadCategory.POSITIONS, {"internal_only": 1})

    def test_unknown_category_payload_raises(self) -> None:
        # FACTORS 白名单未覆盖 strategy 字段 → 全剥离 → 不放行
        with pytest.raises(OutboundSanitizeError):
            _sanitizer().sanitize(PayloadCategory.FACTORS, {"strategy_id": "s1"})

    def test_empty_payload_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            _sanitizer().sanitize(PayloadCategory.POSITIONS, {})

    def test_illegal_category_type_raises(self) -> None:
        with pytest.raises(OutboundSanitizeError):
            _sanitizer().sanitize("positions", {"symbol": "600519"})


# ──────────────────────────────────────────────────────────────────────────────
# PII/凭证掩码
# ──────────────────────────────────────────────────────────────────────────────


class TestMasking:
    def test_phone_masked(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.POSITIONS, {"symbol": "联系电话13800001111"}
        )
        assert MASK_REPLACEMENT in report.sanitized["symbol"]
        assert "13800001111" not in report.sanitized["symbol"]
        assert report.masked_fields == ("symbol",)

    def test_credential_masked(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.STRATEGY, {"name": "cfg api_key=abcdef12345"}
        )
        assert "abcdef12345" not in report.sanitized["name"]
        assert report.masked_fields == ("name",)

    def test_email_masked_in_nested_dict(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.STRATEGY,
            {"name": "n", "params": {"owner": "a@b.com", "depth": 3}},
        )
        assert report.sanitized["params"]["owner"] == MASK_REPLACEMENT
        assert report.sanitized["params"]["depth"] == 3
        assert report.masked_fields == ("params",)

    def test_id_card_masked_in_list(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.STRATEGY,
            {"name": "n", "params": ["11010119900307777X"]},
        )
        assert "11010119900307777X" not in report.sanitized["params"][0]
        assert report.masked_fields == ("params",)

    def test_no_mask_when_clean(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.POSITIONS, {"symbol": "600519", "quantity": 100}
        )
        assert report.masked_fields == ()
        assert report.sanitized["quantity"] == 100

    def test_custom_mask_pattern_injected(self) -> None:
        san = _sanitizer(mask_patterns={"acct": r"acct-\d+"})
        report = san.sanitize(PayloadCategory.STRATEGY, {"name": "acct-9981"})
        assert report.sanitized["name"] == MASK_REPLACEMENT


# ──────────────────────────────────────────────────────────────────────────────
# 确定性 / 报告
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        san = _sanitizer()
        payload = {"quantity": 5, "symbol": "000001", "note": "x", "avg_cost": 1.5}
        r1 = san.sanitize(PayloadCategory.POSITIONS, dict(payload))
        r2 = san.sanitize(PayloadCategory.POSITIONS, dict(payload))
        assert r1 == r2
        assert r1.checked_at == _T0

    def test_report_fields_sorted(self) -> None:
        report = _sanitizer().sanitize(
            PayloadCategory.POSITIONS,
            {"symbol": "s", "quantity": 1, "avg_cost": 2.0, "z_extra": 9, "a_extra": 8},
        )
        assert report.kept_fields == ("avg_cost", "quantity", "symbol")
        assert report.stripped_fields == ("a_extra", "z_extra")
