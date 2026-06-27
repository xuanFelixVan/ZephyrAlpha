# [A_test] module_id: SRC-TST-0615 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.continuous_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.continuous_verifier import ContinuousVerifier, VerificationRecord

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestVerificationRecord:
    def test_creation_defaults(self):
        vr = VerificationRecord(session_id="s1", check_time="2026-01-01T00:00:00Z", status="ok")
        assert vr.session_id == "s1"
        assert vr.status == "ok"
        assert vr.drift_detected is False

    def test_creation_with_drift(self):
        vr = VerificationRecord(session_id="s2", check_time="2026-01-01T00:00:00Z", status="drift", drift_detected=True)
        assert vr.drift_detected is True

    def test_empty_session_id(self):
        vr = VerificationRecord(session_id="", check_time="", status="")
        assert vr.session_id == ""


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestContinuousVerifier:
    def test_record_no_drift(self):
        cv = ContinuousVerifier()
        vr = cv.record("sess-1", "ok")
        assert vr.session_id == "sess-1"
        assert vr.status == "ok"
        assert vr.drift_detected is False
        assert cv.get_drifts() == []

    def test_record_with_drift(self):
        cv = ContinuousVerifier()
        vr = cv.record("sess-2", "drift", drift=True)
        assert vr.drift_detected is True
        drifts = cv.get_drifts()
        assert len(drifts) == 1
        assert drifts[0]["session_id"] == "sess-2"

    def test_should_reverify_no_records(self):
        cv = ContinuousVerifier()
        assert cv.should_reverify("unknown-session") is True

    def test_should_reverify_recent_record(self):
        cv = ContinuousVerifier()
        cv.record("sess-recent", "ok")
        assert cv.should_reverify("sess-recent") is False

    def test_multiple_records_same_session(self):
        cv = ContinuousVerifier()
        cv.record("sess-m", "ok")
        cv.record("sess-m", "ok")
        cv.record("sess-m", "drift", drift=True)
        assert len(cv.get_drifts()) == 1

    def test_record_empty_inputs(self):
        cv = ContinuousVerifier()
        vr = cv.record("", "", drift=False)
        assert vr.session_id == ""
        assert vr.status == ""

    def test_drifts_across_sessions(self):
        cv = ContinuousVerifier()
        cv.record("s1", "drift", drift=True)
        cv.record("s2", "drift", drift=True)
        cv.record("s3", "ok")
        assert len(cv.get_drifts()) == 2
