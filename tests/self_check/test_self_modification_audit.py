# [A_test] module_id: SRC-TST-1561 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_modification_audit
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.self_modification_audit
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_modification_audit.py
# [TTL] task_bound

from __future__ import annotations

import hashlib

from zephyr.feedback_loop.forensic.self_modification_audit import (
    FileIntegrity,
    SelfModificationAudit,
)


class TestFileIntegrity:
    def test_creation(self):
        fi = FileIntegrity(path="/app/main.py", sha256="abc123", last_verified="2026-01-01T00:00:00")
        assert fi.path == "/app/main.py"
        assert fi.sha256 == "abc123"
        assert fi.last_verified == "2026-01-01T00:00:00"

    def test_creation_default_last_verified(self):
        fi = FileIntegrity(path="/app/main.py", sha256="def456")
        assert fi.last_verified == ""


class TestSelfModificationAudit:
    def test_instantiation_defaults(self):
        sma = SelfModificationAudit()
        assert sma.files == {}
        assert sma.unauthorized_changes == []
        assert sma.protected_paths == []

    def test_instantiation_with_protected_paths(self):
        sma = SelfModificationAudit(protected_paths=["/app/core.py", "/app/config.yaml"])
        assert len(sma.protected_paths) == 2

    def test_register_creates_file_integrity(self):
        sma = SelfModificationAudit()
        sma.register("/app/main.py", "original content")
        assert "/app/main.py" in sma.files
        assert sma.files["/app/main.py"].sha256 == hashlib.sha256(b"original content").hexdigest()
        assert sma.files["/app/main.py"].last_verified != ""

    def test_register_deterministic_hash(self):
        sma1 = SelfModificationAudit()
        sma2 = SelfModificationAudit()
        sma1.register("/app/main.py", "same content")
        sma2.register("/app/main.py", "same content")
        assert sma1.files["/app/main.py"].sha256 == sma2.files["/app/main.py"].sha256

    def test_verify_unchanged_file(self):
        sma = SelfModificationAudit()
        sma.register("/app/main.py", "original content")
        result = sma.verify("/app/main.py", "original content")
        assert result is True
        assert "/app/main.py" not in sma.unauthorized_changes

    def test_verify_modified_file(self):
        sma = SelfModificationAudit()
        sma.register("/app/main.py", "original content")
        result = sma.verify("/app/main.py", "modified content")
        assert result is False
        assert "/app/main.py" in sma.unauthorized_changes

    def test_verify_unregistered_file(self):
        sma = SelfModificationAudit()
        result = sma.verify("/app/unknown.py", "any content")
        assert result is True

    def test_verify_updates_last_verified(self):
        sma = SelfModificationAudit()
        sma.register("/app/main.py", "content")
        old_verified = sma.files["/app/main.py"].last_verified
        sma.verify("/app/main.py", "content")
        assert sma.files["/app/main.py"].last_verified >= old_verified

    def test_scan_all_clean(self):
        sma = SelfModificationAudit()
        sma.register("/app/a.py", "content-a")
        sma.register("/app/b.py", "content-b")
        changed = sma.scan_all({"/app/a.py": "content-a", "/app/b.py": "content-b"})
        assert changed == []

    def test_scan_all_with_changes(self):
        sma = SelfModificationAudit()
        sma.register("/app/a.py", "original-a")
        sma.register("/app/b.py", "original-b")
        changed = sma.scan_all({"/app/a.py": "modified-a", "/app/b.py": "original-b"})
        assert changed == ["/app/a.py"]

    def test_scan_all_multiple_changes(self):
        sma = SelfModificationAudit()
        sma.register("/app/a.py", "original-a")
        sma.register("/app/b.py", "original-b")
        changed = sma.scan_all({"/app/a.py": "modified-a", "/app/b.py": "modified-b"})
        assert len(changed) == 2

    def test_scan_all_empty_contents(self):
        sma = SelfModificationAudit()
        changed = sma.scan_all({})
        assert changed == []

    def test_register_empty_content(self):
        sma = SelfModificationAudit()
        sma.register("/app/empty.py", "")
        assert sma.files["/app/empty.py"].sha256 == hashlib.sha256(b"").hexdigest()

    def test_verify_multiple_times_accumulates_unauthorized(self):
        sma = SelfModificationAudit()
        sma.register("/app/a.py", "original")
        sma.verify("/app/a.py", "changed1")
        sma.register("/app/a.py", "changed1")
        sma.verify("/app/a.py", "changed2")
        assert len(sma.unauthorized_changes) == 2
