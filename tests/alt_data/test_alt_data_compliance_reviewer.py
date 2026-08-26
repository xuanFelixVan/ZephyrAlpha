# [BLUEPRINT] MOD-ALT-015 | docs/03_modules/_domain_alt_data/alt_data_compliance_reviewer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-015 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_alt_data_compliance_reviewer
# [TESTS] src/zephyr/alt_data/alt_data_compliance_reviewer.py
"""MOD-ALT-015 单元测试：alt_data_compliance_reviewer 另类数据合规审查器。

蓝图验收（B13-04283/CAND-TESTA-016，A3 D-ALT-DATA-14）：
四要素台账登记 + 上线前审查清单逐项判定（含证据）+ 定期复核提醒（注入时钟）
+ 合规白名单与禁用源清单输出 + 审查记录留痕。时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.alt_data_compliance_reviewer",
    reason="alt_data_compliance_reviewer not importable",
)

from zephyr.alt_data.alt_data_compliance_reviewer import (  # noqa: E402
    AltComplianceError,
    AltDataComplianceReviewer,
    SourceStatus,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_CHECKLIST = ("采集授权", "ToS合规", "许可范围", "隐私评估")


def _reviewer(
    *,
    now: datetime.datetime = _T0,
    interval: int = 90,
) -> AltDataComplianceReviewer:
    return AltDataComplianceReviewer(
        checklist=_CHECKLIST,
        review_interval_days=interval,
        clock=lambda: now,
    )


def _register(r: AltDataComplianceReviewer, source_id: str = "src-1") -> None:
    r.register(
        source_id,
        collection_method="RSS 抓取",
        tos_terms="允许聚合",
        license_scope="CC-BY",
        privacy_impact="低（无个人信息）",
    )


def _pass_results() -> dict:
    return {item: (True, f"证据-{item}") for item in _CHECKLIST}


def _fail_results(fail_item: str = "隐私评估") -> dict:
    out = _pass_results()
    out[fail_item] = (False, f"未通过-{fail_item}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_empty_checklist_raises(self) -> None:
        with pytest.raises(AltComplianceError):
            AltDataComplianceReviewer(checklist=())

    def test_blank_checklist_item_raises(self) -> None:
        with pytest.raises(AltComplianceError):
            AltDataComplianceReviewer(checklist=(" ok ", " "))

    def test_duplicate_checklist_item_raises(self) -> None:
        with pytest.raises(AltComplianceError):
            AltDataComplianceReviewer(checklist=("a", "a"))

    def test_nonpositive_interval_raises(self) -> None:
        with pytest.raises(AltComplianceError):
            AltDataComplianceReviewer(checklist=("a",), review_interval_days=0)


# ──────────────────────────────────────────────────────────────────────────────
# 四要素台账登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok(self) -> None:
        r = _reviewer()
        rec = r.register(
            "src-1",
            collection_method="API",
            tos_terms="允许",
            license_scope="MIT",
            privacy_impact="低",
        )
        assert rec.source_id == "src-1"
        assert rec.registered_at == _T0
        assert r.status_of("src-1") is SourceStatus.PENDING

    def test_blank_source_id_raises(self) -> None:
        r = _reviewer()
        with pytest.raises(AltComplianceError):
            r.register(" ", collection_method="a", tos_terms="b",
                       license_scope="c", privacy_impact="d")

    def test_duplicate_register_raises(self) -> None:
        r = _reviewer()
        _register(r)
        with pytest.raises(AltComplianceError):
            _register(r)

    def test_blank_element_raises(self) -> None:
        r = _reviewer()
        with pytest.raises(AltComplianceError):
            r.register(
                "src-1",
                collection_method="",
                tos_terms="b",
                license_scope="c",
                privacy_impact="d",
            )

    def test_record_of_unknown_raises(self) -> None:
        r = _reviewer()
        with pytest.raises(AltComplianceError):
            r.record_of("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 审查清单逐项判定
# ──────────────────────────────────────────────────────────────────────────────


class TestReview:
    def test_review_all_pass_approved(self) -> None:
        r = _reviewer()
        _register(r)
        rec = r.review("src-1", results=_pass_results())
        assert rec.overall_passed is True
        assert r.status_of("src-1") is SourceStatus.APPROVED

    def test_review_partial_fail_stays_pending(self) -> None:
        r = _reviewer()
        _register(r)
        rec = r.review("src-1", results=_fail_results())
        assert rec.overall_passed is False
        assert r.status_of("src-1") is SourceStatus.PENDING

    def test_review_unknown_source_raises(self) -> None:
        r = _reviewer()
        with pytest.raises(AltComplianceError):
            r.review("ghost", results=_pass_results())

    def test_review_missing_item_raises(self) -> None:
        r = _reviewer()
        _register(r)
        results = _pass_results()
        results.pop("隐私评估")
        with pytest.raises(AltComplianceError):
            r.review("src-1", results=results)

    def test_review_extra_item_raises(self) -> None:
        r = _reviewer()
        _register(r)
        results = _pass_results()
        results["多余项"] = (True, "x")
        with pytest.raises(AltComplianceError):
            r.review("src-1", results=results)

    def test_review_blank_evidence_raises(self) -> None:
        r = _reviewer()
        _register(r)
        results = _pass_results()
        results["采集授权"] = (True, " ")
        with pytest.raises(AltComplianceError):
            r.review("src-1", results=results)

    def test_review_banned_raises(self) -> None:
        r = _reviewer()
        _register(r)
        r.ban("src-1")
        with pytest.raises(AltComplianceError):
            r.review("src-1", results=_pass_results())

    def test_review_history_appended(self) -> None:
        r = _reviewer()
        _register(r)
        r.review("src-1", results=_fail_results())
        r.review("src-1", results=_pass_results())
        hist = r.review_history("src-1")
        assert len(hist) == 2
        assert hist[0].overall_passed is False
        assert hist[1].overall_passed is True


# ──────────────────────────────────────────────────────────────────────────────
# 白名单 / 禁用清单 / 定期复核
# ──────────────────────────────────────────────────────────────────────────────


class TestLists:
    def test_whitelist_approved_not_expired(self) -> None:
        r = _reviewer()
        _register(r, "src-1")
        _register(r, "src-2")
        r.review("src-1", results=_pass_results())
        assert r.whitelist() == ("src-1",)
        assert r.blacklist() == ()

    def test_banned_goes_to_blacklist(self) -> None:
        r = _reviewer()
        _register(r, "src-1")
        _register(r, "src-2")
        r.ban("src-2")
        assert r.blacklist() == ("src-2",)
        assert r.status_of("src-2") is SourceStatus.BANNED

    def test_expired_dropped_from_whitelist(self) -> None:
        now = [_T0]  # 可推进时钟
        r = AltDataComplianceReviewer(
            checklist=_CHECKLIST, review_interval_days=90, clock=lambda: now[0]
        )
        _register(r, "src-1")
        r.review("src-1", results=_pass_results())
        now[0] = _T0 + datetime.timedelta(days=91)  # 推进时钟至过期
        assert r.status_of("src-1") is SourceStatus.EXPIRED
        assert r.whitelist() == ()
        assert r.pending_reviews() == ("src-1",)

    def test_not_expired_stays_whitelist(self) -> None:
        now = [_T0]
        r = AltDataComplianceReviewer(
            checklist=_CHECKLIST, review_interval_days=90, clock=lambda: now[0]
        )
        _register(r, "src-1")
        r.review("src-1", results=_pass_results())
        now[0] = _T0 + datetime.timedelta(days=30)
        assert r.status_of("src-1") is SourceStatus.APPROVED
        assert r.whitelist() == ("src-1",)
        assert r.pending_reviews() == ()

    def test_ban_unknown_raises(self) -> None:
        r = _reviewer()
        with pytest.raises(AltComplianceError):
            r.ban("ghost")

    def test_sources_sorted(self) -> None:
        r = _reviewer()
        _register(r, "b")
        _register(r, "a")
        assert r.sources() == ("a", "b")

    def test_determinism_same_input_same_output(self) -> None:
        def run() -> tuple:
            r = _reviewer()
            _register(r, "src-1")
            rec = r.review("src-1", results=_pass_results())
            return (rec.overall_passed, r.status_of("src-1"), r.whitelist())

        assert run() == run()
