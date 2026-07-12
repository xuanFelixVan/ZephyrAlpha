# [A_test] module_id: SRC-TST-1444 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_remote_attestation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.security.remote_attestation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_remote_attestation.py
# [TTL] task_bound


from zephyr.feedback_loop.security.remote_attestation import (
    AttestationReport,
    RemoteAttestation,
)


class TestRemoteAttestationInstantiation:
    def test_default_instantiation(self):
        ra = RemoteAttestation()
        assert ra.reports == []
        assert ra.expected_pcr_hashes == {}
        assert ra.attestation_required is True

    def test_custom_instantiation(self):
        ra = RemoteAttestation(
            expected_pcr_hashes={0: "abc123"},
            attestation_required=False,
        )
        assert ra.expected_pcr_hashes == {0: "abc123"}
        assert ra.attestation_required is False


class TestVerify:
    def test_verify_matching_pcrs(self):
        ra = RemoteAttestation(expected_pcr_hashes={0: "hash0", 1: "hash1"})
        report = AttestationReport(
            pcr_values={0: "hash0", 1: "hash1"},
            quote="q",
            signature="s",
        )
        result = ra.verify(report)
        assert result is True
        assert report.verified is True

    def test_verify_mismatched_pcrs(self):
        ra = RemoteAttestation(expected_pcr_hashes={0: "hash0"})
        report = AttestationReport(
            pcr_values={0: "wrong_hash"},
            quote="q",
            signature="s",
        )
        result = ra.verify(report)
        assert result is False
        assert report.verified is False

    def test_verify_missing_pcr_index(self):
        ra = RemoteAttestation(expected_pcr_hashes={0: "hash0", 5: "hash5"})
        report = AttestationReport(
            pcr_values={0: "hash0"},
            quote="q",
            signature="s",
        )
        result = ra.verify(report)
        assert result is False

    def test_verify_no_expected_hashes(self):
        ra = RemoteAttestation(expected_pcr_hashes={})
        report = AttestationReport(
            pcr_values={0: "anything"},
            quote="q",
            signature="s",
        )
        result = ra.verify(report)
        assert result is True

    def test_verify_appends_report(self):
        ra = RemoteAttestation()
        report = AttestationReport(pcr_values={}, quote="q", signature="s")
        ra.verify(report)
        assert len(ra.reports) == 1


class TestLastVerified:
    def test_no_reports(self):
        ra = RemoteAttestation()
        assert ra.last_verified() is None

    def test_returns_last_report(self):
        ra = RemoteAttestation()
        r1 = AttestationReport(pcr_values={}, quote="q1", signature="s1")
        r2 = AttestationReport(pcr_values={}, quote="q2", signature="s2")
        ra.verify(r1)
        ra.verify(r2)
        assert ra.last_verified().quote == "q2"


class TestAttestationReport:
    def test_report_defaults(self):
        report = AttestationReport(pcr_values={}, quote="q", signature="s")
        assert report.verified is False
