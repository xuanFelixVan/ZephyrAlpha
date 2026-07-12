# [A_test] module_id: SRC-TST-2120 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_boot_integrity_attestation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.boot_integrity_attestation
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_boot_integrity_attestation.py
# [TTL] task_bound

from __future__ import annotations

import hashlib
import os
import tempfile

from zephyr.feedback_loop.forensic.boot_integrity_attestation import (
    BootIntegrityAttestation,
    BootIntegrityResult,
)


class TestBootIntegrityResult:
    def test_enum_values(self):
        assert BootIntegrityResult.ATTESTED.value == "ATTESTED"
        assert BootIntegrityResult.MODIFIED_UNVERIFIED.value == "MODIFIED_UNVERIFIED"
        assert BootIntegrityResult.CORRUPTED.value == "CORRUPTED"
        assert BootIntegrityResult.TAMPERED.value == "TAMPERED"


class TestBootIntegrityAttestation:
    def test_instantiation_defaults(self):
        bia = BootIntegrityAttestation()
        assert bia.known_good_hashes == {}
        assert bia.boot_integrity is BootIntegrityResult.ATTESTED
        assert bia.auto_degrade_on_failure is True

    def test_compute_file_hash_existing_file(self):
        bia = BootIntegrityAttestation()
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
            f.write("print('hello')")
            f.flush()
            path = f.name
        try:
            h = bia.compute_file_hash(path)
            assert len(h) == 64
            assert h == hashlib.sha256(b"print('hello')").hexdigest()
        finally:
            os.unlink(path)

    def test_compute_file_hash_nonexistent_file(self):
        bia = BootIntegrityAttestation()
        h = bia.compute_file_hash("/nonexistent/path/file.py")
        assert h == ""

    def test_build_manifest(self):
        bia = BootIntegrityAttestation()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "sample.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("x = 1")
            result = bia.build_manifest([tmpdir])
            assert result["files_hashed"] == 1
            assert result["manifest_root_count"] == 1
            assert len(bia.known_good_hashes) == 1

    def test_build_manifest_nonexistent_root(self):
        bia = BootIntegrityAttestation()
        result = bia.build_manifest(["/nonexistent/root"])
        assert result["files_hashed"] == 0

    def test_attest_no_manifest(self):
        bia = BootIntegrityAttestation()
        result = bia.attest(["/some/root"])
        assert result["integrity"] == BootIntegrityResult.CORRUPTED.value

    def test_attest_clean(self):
        bia = BootIntegrityAttestation()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "clean.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("x = 1")
            bia.build_manifest([tmpdir])
            result = bia.attest([tmpdir])
            assert result["integrity"] == BootIntegrityResult.ATTESTED.value
            assert result["violation_count"] == 0
            assert result["degraded"] is False

    def test_attest_modified_file(self):
        bia = BootIntegrityAttestation()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "mod.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("x = 1")
            bia.build_manifest([tmpdir])
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("x = 2")
            result = bia.attest([tmpdir])
            assert result["integrity"] == BootIntegrityResult.MODIFIED_UNVERIFIED.value
            assert result["violation_count"] > 0

    def test_attest_deleted_files_tampered(self):
        bia = BootIntegrityAttestation()
        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(7):
                p = os.path.join(tmpdir, f"file_{i}.py")
                with open(p, "w", encoding="utf-8") as f:
                    f.write(f"x = {i}")
                files.append(p)
            bia.build_manifest([tmpdir])
            for p in files:
                os.unlink(p)
            result = bia.attest([tmpdir])
            assert result["integrity"] == BootIntegrityResult.TAMPERED.value

    def test_owner_attest_override_tampered(self):
        bia = BootIntegrityAttestation()
        bia.boot_integrity = BootIntegrityResult.TAMPERED
        result = bia.owner_attest_override("owner-sig")
        assert result["override_accepted"] is True
        assert bia.boot_integrity is BootIntegrityResult.ATTESTED

    def test_owner_attest_override_not_tampered(self):
        bia = BootIntegrityAttestation()
        bia.boot_integrity = BootIntegrityResult.ATTESTED
        result = bia.owner_attest_override("owner-sig")
        assert result["override_accepted"] is False

    def test_get_integrity_status(self):
        bia = BootIntegrityAttestation()
        status = bia.get_integrity_status()
        assert status["boot_integrity"] == BootIntegrityResult.ATTESTED.value
        assert status["safe_to_operate"] is True
        assert status["mismatch_count"] == 0
