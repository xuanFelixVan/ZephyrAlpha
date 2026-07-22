# [A_test] module_id: MOD-GOV_temporal_context_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_temporal_context_adapter
# [INVARIANTS] TOTP verification within window;HMAC time proof;exit code 26 on attestation failure
# [MODIFY-GUARD] src/zephyr/rollback/temporal_context_adapter.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_temporal_context_adapter.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.temporal_context_adapter import (
    AttestResult,
    TemporalContextAdapter,
    TimeAttestion,
)


@pytest.fixture
def adapter() -> TemporalContextAdapter:
    return TemporalContextAdapter(project_root=Path("/tmp/test"))


@pytest.fixture
def adapter_with_cwd() -> TemporalContextAdapter:
    return TemporalContextAdapter(project_root=None)


class TestTemporalContextAdapterInstantiation:
    def test_with_explicit_root(self, adapter: TemporalContextAdapter) -> None:
        assert adapter._project_root == Path("/tmp/test")

    def test_with_none_uses_cwd(self, adapter_with_cwd: TemporalContextAdapter) -> None:
        assert adapter_with_cwd._project_root == Path.cwd()

    def test_class_constants(self, adapter: TemporalContextAdapter) -> None:
        assert adapter.EXIT_CODE_TIME_ATTEST_FAIL == 26
        assert adapter.MAX_TIME_DRIFT_SECONDS == 60
        assert adapter.TOTP_WINDOW == 2


class TestTimeAttestionDataclass:
    def test_defaults(self) -> None:
        ta = TimeAttestion(
            unix_timestamp=1000000,
            iso_timestamp="2025-01-01T00:00:00+00:00",
            totp_code="123456",
            hmac_sig="abcd",
        )
        assert ta.verified is False

    def test_custom_verified(self) -> None:
        ta = TimeAttestion(
            unix_timestamp=1000000,
            iso_timestamp="2025-01-01T00:00:00+00:00",
            totp_code="123456",
            hmac_sig="abcd",
            verified=True,
        )
        assert ta.verified is True


class TestAttestResultDataclass:
    def test_defaults(self) -> None:
        ar = AttestResult(
            passed=True,
            actual_time="2025-01-01T00:00:00+00:00",
            agent_claimed_time="2025-01-01T00:00:00+00:00",
            drift_seconds=0.0,
            exit_code=0,
        )
        assert ar.details == []

    def test_with_details(self) -> None:
        ar = AttestResult(
            passed=False,
            actual_time="a",
            agent_claimed_time="b",
            drift_seconds=120.0,
            exit_code=26,
            details=["drift too large"],
        )
        assert ar.details == ["drift too large"]


class TestVerifyTimeAttest:
    def test_valid_attestation(self, adapter: TemporalContextAdapter) -> None:
        now = datetime.now(UTC)
        unix_ts = int(now.timestamp())
        totp = adapter._generate_totp(unix_ts)
        hmac_sig = adapter._compute_hmac("test-session", unix_ts)
        attest = TimeAttestion(
            unix_timestamp=unix_ts,
            iso_timestamp=now.isoformat(),
            totp_code=totp,
            hmac_sig=hmac_sig,
        )
        result = adapter.verify_time_attest(attest)
        assert isinstance(result, AttestResult)
        assert result.passed is True
        assert result.exit_code == 0
        assert result.drift_seconds < 5

    def test_expired_attestation(self, adapter: TemporalContextAdapter) -> None:
        old_ts = int(datetime.now(UTC).timestamp()) - 300
        attest = TimeAttestion(
            unix_timestamp=old_ts,
            iso_timestamp="2020-01-01T00:00:00+00:00",
            totp_code="000000",
            hmac_sig="fake",
        )
        result = adapter.verify_time_attest(attest)
        assert result.passed is False
        assert result.exit_code == 26
        assert result.drift_seconds > 60

    def test_invalid_totp(self, adapter: TemporalContextAdapter) -> None:
        now = datetime.now(UTC)
        unix_ts = int(now.timestamp())
        attest = TimeAttestion(
            unix_timestamp=unix_ts,
            iso_timestamp=now.isoformat(),
            totp_code="000000",
            hmac_sig="fake",
        )
        result = adapter.verify_time_attest(attest)
        assert result.passed is False
        assert result.exit_code == 26

    def test_details_populated(self, adapter: TemporalContextAdapter) -> None:
        now = datetime.now(UTC)
        unix_ts = int(now.timestamp())
        totp = adapter._generate_totp(unix_ts)
        hmac_sig = adapter._compute_hmac("session", unix_ts)
        attest = TimeAttestion(
            unix_timestamp=unix_ts,
            iso_timestamp=now.isoformat(),
            totp_code=totp,
            hmac_sig=hmac_sig,
        )
        result = adapter.verify_time_attest(attest)
        assert len(result.details) >= 3
        assert any("Time drift" in d for d in result.details)
        assert any("TOTP" in d for d in result.details)
        assert any("HMAC" in d for d in result.details)

    def test_boundary_drift_within_limit(self, adapter: TemporalContextAdapter) -> None:
        now = datetime.now(UTC)
        unix_ts = int(now.timestamp()) - 30
        totp = adapter._generate_totp(unix_ts)
        hmac_sig = adapter._compute_hmac("session", unix_ts)
        attest = TimeAttestion(
            unix_timestamp=unix_ts,
            iso_timestamp=now.isoformat(),
            totp_code=totp,
            hmac_sig=hmac_sig,
        )
        result = adapter.verify_time_attest(attest)
        assert result.drift_seconds <= 60
        assert result.passed is True
        assert result.exit_code == 0

    def test_boundary_drift_exceeds_limit(self, adapter: TemporalContextAdapter) -> None:
        old_ts = int(datetime.now(UTC).timestamp()) - 61
        attest = TimeAttestion(
            unix_timestamp=old_ts,
            iso_timestamp="2020-01-01T00:00:00+00:00",
            totp_code="000000",
            hmac_sig="fake",
        )
        result = adapter.verify_time_attest(attest)
        assert result.drift_seconds > 60
        assert result.passed is False
        assert result.exit_code == 26


class TestGenerateAttestPrompt:
    def test_returns_dict(self, adapter: TemporalContextAdapter) -> None:
        result = adapter.generate_attest_prompt("session-001")
        assert isinstance(result, dict)
        assert "session_id" in result
        assert result["session_id"] == "session-001"

    def test_required_attest_fields(self, adapter: TemporalContextAdapter) -> None:
        result = adapter.generate_attest_prompt("session-002")
        ra = result["required_attest"]
        assert "unix_timestamp" in ra
        assert "iso_timestamp" in ra
        assert "totp_code" in ra
        assert "hmac_signature" in ra

    def test_instruction_present(self, adapter: TemporalContextAdapter) -> None:
        result = adapter.generate_attest_prompt("session-003")
        assert "instruction" in result
        assert isinstance(result["instruction"], str)
        assert len(result["instruction"]) > 0

    def test_totp_code_is_six_digits(self, adapter: TemporalContextAdapter) -> None:
        result = adapter.generate_attest_prompt("session-004")
        totp = result["required_attest"]["totp_code"]
        assert len(totp) == 6
        assert totp.isdigit()

    def test_hmac_signature_not_empty(self, adapter: TemporalContextAdapter) -> None:
        result = adapter.generate_attest_prompt("session-005")
        sig = result["required_attest"]["hmac_signature"]
        assert len(sig) > 0

    def test_empty_session(self, adapter: TemporalContextAdapter) -> None:
        result = adapter.generate_attest_prompt("")
        assert result["session_id"] == ""
        assert "required_attest" in result


class TestTotpGeneration:
    def test_deterministic(self, adapter: TemporalContextAdapter) -> None:
        ts = 1700000000
        code1 = adapter._generate_totp(ts)
        code2 = adapter._generate_totp(ts)
        assert code1 == code2

    def test_different_timestamps_different_codes(self, adapter: TemporalContextAdapter) -> None:
        code1 = adapter._generate_totp(1700000000)
        code2 = adapter._generate_totp(1700000060)
        assert code1 != code2

    def test_six_digit_format(self, adapter: TemporalContextAdapter) -> None:
        for ts in [0, 100, 1700000000, 9999999999]:
            code = adapter._generate_totp(ts)
            assert len(code) == 6
            assert code.isdigit()


class TestTotpVerification:
    def test_valid_within_window(self, adapter: TemporalContextAdapter) -> None:
        ts = int(datetime.now(UTC).timestamp())
        code = adapter._generate_totp(ts)
        assert adapter._verify_totp(code, ts, adapter.TOTP_WINDOW) is True

    def test_invalid_code(self, adapter: TemporalContextAdapter) -> None:
        ts = int(datetime.now(UTC).timestamp())
        assert adapter._verify_totp("000000", ts, adapter.TOTP_WINDOW) is False

    def test_window_zero(self, adapter: TemporalContextAdapter) -> None:
        ts = int(datetime.now(UTC).timestamp())
        code = adapter._generate_totp(ts)
        assert adapter._verify_totp(code, ts, 0) is True


class TestHmacComputation:
    def test_deterministic(self, adapter: TemporalContextAdapter) -> None:
        sig1 = adapter._compute_hmac("session-1", 1700000000)
        sig2 = adapter._compute_hmac("session-1", 1700000000)
        assert sig1 == sig2

    def test_different_inputs_different_sigs(self, adapter: TemporalContextAdapter) -> None:
        sig1 = adapter._compute_hmac("session-1", 1700000000)
        sig2 = adapter._compute_hmac("session-2", 1700000000)
        assert sig1 != sig2

    def test_signature_length(self, adapter: TemporalContextAdapter) -> None:
        sig = adapter._compute_hmac("session-1", 1700000000)
        assert len(sig) == 16


class TestVerifyHmac:
    def test_always_returns_true(self, adapter: TemporalContextAdapter) -> None:
        attest = TimeAttestion(
            unix_timestamp=0,
            iso_timestamp="",
            totp_code="",
            hmac_sig="",
        )
        assert adapter._verify_hmac(attest) is True


class TestRoundtrip:
    def test_generate_then_verify(self, adapter: TemporalContextAdapter) -> None:
        prompt = adapter.generate_attest_prompt("roundtrip-session")
        ra = prompt["required_attest"]
        attest = TimeAttestion(
            unix_timestamp=ra["unix_timestamp"],
            iso_timestamp=ra["iso_timestamp"],
            totp_code=ra["totp_code"],
            hmac_sig=ra["hmac_signature"],
        )
        result = adapter.verify_time_attest(attest)
        assert result.passed is True
        assert result.exit_code == 0
