# [BLUEPRINT] MOD-ALT-012 | docs/03_modules/_domain_alt_data/alt_data_privacy_protector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-012 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_alt_data_privacy_protector
# [TESTS] src/zephyr/alt_data/alt_data_privacy_protector.py
"""MOD-ALT-012 单元测试：alt_data_privacy_protector 另类数据隐私保护器。

蓝图验收（B14-04665/CAND-TESTA-021，A9 D-ALT-DATA-17）：
PII 识别（手机号/身份证/姓名默认正则+注入扩展）+ 入库前脱敏管道 +
字段白名单最小化留存 + TTL 裁决 + 访问审计回调。
时钟/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.alt_data_privacy_protector",
    reason="alt_data_privacy_protector not importable",
)

from zephyr.alt_data.alt_data_privacy_protector import (  # noqa: E402
    AccessAudit,
    AltDataPrivacyProtector,
    AltPrivacyError,
    PiiPattern,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _protector(
    audits: list | None = None,
    extra: tuple = (),
    now: datetime.datetime = _T0,
) -> AltDataPrivacyProtector:
    return AltDataPrivacyProtector(
        extra_patterns=extra,
        clock=lambda: now,
        audit_sink=(lambda a: audits.append(a)) if audits is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_blank_pii_type_raises(self) -> None:
        with pytest.raises(AltPrivacyError):
            _protector(extra=(PiiPattern(pii_type=" ", pattern=r"x", mask="[X]"),))

    def test_duplicate_pii_type_raises(self) -> None:
        with pytest.raises(AltPrivacyError):
            _protector(extra=(PiiPattern(pii_type="mobile_phone", pattern=r"x", mask="[X]"),))

    def test_uncompilable_pattern_raises(self) -> None:
        with pytest.raises(AltPrivacyError):
            _protector(extra=(PiiPattern(pii_type="bad", pattern=r"([", mask="[X]"),))

    def test_blank_mask_raises(self) -> None:
        with pytest.raises(AltPrivacyError):
            _protector(extra=(PiiPattern(pii_type="t", pattern=r"x", mask=""),))


# ──────────────────────────────────────────────────────────────────────────────
# PII 识别
# ──────────────────────────────────────────────────────────────────────────────


class TestDetectPii:
    def test_detect_mobile_phone(self) -> None:
        p = _protector()
        findings = p.detect_pii("联系电话13812345678备用")
        assert len(findings) == 1
        assert findings[0].pii_type == "mobile_phone"
        assert findings[0].matched == "13812345678"

    def test_detect_id_card(self) -> None:
        p = _protector()
        findings = p.detect_pii("证件号11010119900307753X登记")
        assert any(f.pii_type == "id_card" for f in findings)

    def test_detect_person_name(self) -> None:
        p = _protector()
        findings = p.detect_pii("姓名:张三丰 提交了材料")
        assert any(f.pii_type == "person_name" for f in findings)

    def test_detect_extra_pattern(self) -> None:
        p = _protector(extra=(PiiPattern(pii_type="email", pattern=r"[\w.]+@[\w.]+", mask="[EMAIL]"),))
        findings = p.detect_pii("邮箱 a.b@example.com 失效")
        assert any(f.pii_type == "email" for f in findings)

    def test_detect_sorted_by_position(self) -> None:
        p = _protector()
        findings = p.detect_pii("13900001111 与 13700002222")
        assert [f.matched for f in findings] == ["13900001111", "13700002222"]

    def test_detect_non_string_raises(self) -> None:
        p = _protector()
        with pytest.raises(AltPrivacyError):
            p.detect_pii(123)  # type: ignore[arg-type]

    def test_detect_no_pii_empty(self) -> None:
        p = _protector()
        assert p.detect_pii("没有任何隐私信息") == []


# ──────────────────────────────────────────────────────────────────────────────
# 脱敏管道
# ──────────────────────────────────────────────────────────────────────────────


class TestSanitize:
    def test_sanitize_text_masks_all_types(self) -> None:
        p = _protector()
        out = p.sanitize_text("姓名:张三 手机 13812345678 证件 11010119900307753X")
        assert "13812345678" not in out
        assert "11010119900307753X" not in out
        assert "[PHONE]" in out and "[IDCARD]" in out and "[NAME]" in out

    def test_sanitize_text_idempotent(self) -> None:
        p = _protector()
        once = p.sanitize_text("手机 13812345678")
        assert p.sanitize_text(once) == once

    def test_sanitize_record_whitelist_minimization(self) -> None:
        p = _protector()
        record = {
            "title": "某招聘帖",
            "content": "联系人:李四 电话13900001111",
            "author_raw": "内部账号A",
            "crawl_ts": "2026-08-26",
        }
        out = p.sanitize_record(record, whitelist=("title", "content"))
        assert set(out) == {"title", "content"}  # 非白名单字段丢弃
        assert "13900001111" not in out["content"]
        assert "[NAME]" in out["content"]

    def test_sanitize_record_non_string_value_passthrough(self) -> None:
        p = _protector()
        out = p.sanitize_record({"n": 42, "s": "ok"}, whitelist=("n", "s"))
        assert out == {"n": 42, "s": "ok"}

    def test_sanitize_record_empty_whitelist_raises(self) -> None:
        p = _protector()
        with pytest.raises(AltPrivacyError):
            p.sanitize_record({"a": 1}, whitelist=())

    def test_sanitize_record_non_mapping_raises(self) -> None:
        p = _protector()
        with pytest.raises(AltPrivacyError):
            p.sanitize_record([("a", 1)], whitelist=("a",))  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# TTL 裁决
# ──────────────────────────────────────────────────────────────────────────────


class TestTtl:
    def test_register_and_retain_within_ttl(self) -> None:
        p = _protector()
        p.register_ttl("social_posts", 30)
        stored = _T0 - datetime.timedelta(days=29)
        assert p.should_retain("social_posts", stored) is True

    def test_expired_not_retained(self) -> None:
        p = _protector()
        p.register_ttl("social_posts", 30)
        stored = _T0 - datetime.timedelta(days=31)
        assert p.should_retain("social_posts", stored) is False

    def test_unknown_dataset_raises(self) -> None:
        p = _protector()
        with pytest.raises(AltPrivacyError):
            p.should_retain("ghost", _T0)

    def test_duplicate_ttl_registration_raises(self) -> None:
        p = _protector()
        p.register_ttl("d1", 30)
        with pytest.raises(AltPrivacyError):
            p.register_ttl("d1", 60)

    def test_nonpositive_ttl_raises(self) -> None:
        p = _protector()
        with pytest.raises(AltPrivacyError):
            p.register_ttl("d1", 0)

    def test_future_stored_at_raises(self) -> None:
        p = _protector()
        p.register_ttl("d1", 30)
        with pytest.raises(AltPrivacyError):
            p.should_retain("d1", _T0 + datetime.timedelta(seconds=1))

    def test_clock_injected_deterministic(self) -> None:
        now = _T0 + datetime.timedelta(days=100)
        p = _protector(now=now)
        p.register_ttl("d1", 30)
        assert p.should_retain("d1", _T0) is False


# ──────────────────────────────────────────────────────────────────────────────
# 访问审计
# ──────────────────────────────────────────────────────────────────────────────


class TestAccessAudit:
    def test_record_access_logs_and_callbacks(self) -> None:
        audits: list[AccessAudit] = []
        p = _protector(audits)
        audit = p.record_access("research_agent", "social_posts", "情绪信号提取")
        assert audit.accessed_at == _T0
        assert audits == [audit]
        assert p.access_log() == (audit,)

    def test_record_access_blank_field_raises(self) -> None:
        p = _protector()
        with pytest.raises(AltPrivacyError):
            p.record_access("", "d1", "p")
        with pytest.raises(AltPrivacyError):
            p.record_access("a", " ", "p")
        with pytest.raises(AltPrivacyError):
            p.record_access("a", "d1", "")

    def test_audit_sink_exception_not_blocking(self) -> None:
        def bad_sink(_a: AccessAudit) -> None:
            raise RuntimeError("boom")

        p = AltDataPrivacyProtector(clock=lambda: _T0, audit_sink=bad_sink)
        audit = p.record_access("a", "d1", "p")  # 回调异常不阻断
        assert p.access_log() == (audit,)

    def test_determinism_same_input_same_output(self) -> None:
        def run() -> tuple:
            p = _protector()
            text = "姓名:王五 电话13711112222"
            findings = tuple((f.pii_type, f.matched, f.start, f.end) for f in p.detect_pii(text))
            return findings, p.sanitize_text(text)

        assert run() == run()
