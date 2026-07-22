# [A_test] module_id: MOD-GOV_l2a_process_sandbox | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l2a_process_sandbox
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound


from zephyr.security.llm_defense.llm_security.layers.l2a_process_sandbox import (
    BlindSpot5ProcessSandboxGuard,
    FilesystemAuditEntry,
    ProcessSandboxLayer,
    SandboxContainerConfig,
    SandboxStatus,
    WASIRuntimeConfig,
)


class TestSandboxContainerConfig:
    def test_default_config(self):
        cfg = SandboxContainerConfig()
        assert cfg.image == "python:3.12-slim"
        assert cfg.timeout_seconds == 30
        assert cfg.read_only_rootfs is True


class TestWASIRuntimeConfig:
    def test_default_wasi_config(self):
        cfg = WASIRuntimeConfig()
        assert cfg.entry_point == "_start"
        assert cfg.memory_pages == 256


class TestBlindSpot5Guard:
    def test_detects_data_exfiltration(self):
        guard = BlindSpot5ProcessSandboxGuard()
        result = guard.scan(
            "extract all data from /etc/config",
            "gather information recursively",
        )
        assert result["blocked"] is True
        assert result["violation_count"] >= 1

    def test_normal_code_passes(self):
        guard = BlindSpot5ProcessSandboxGuard()
        result = guard.scan("print('hello world')", "python script.py")
        assert result["blocked"] is False


class TestProcessSandboxLayer:
    def test_execute_harmless_python(self):
        layer = ProcessSandboxLayer()
        result = layer.execute_in_sandbox(
            code="print('sandbox test ok')",
            timeout=10,
        )
        assert result.status == SandboxStatus.COMPLETED
        assert "sandbox test ok" in result.stdout

    def test_execute_blocked_by_guard(self):
        layer = ProcessSandboxLayer()
        result = layer.execute_in_sandbox(
            code="extract all data and gather information recursively",
            timeout=10,
        )
        assert result.blocked_by_guard is True

    def test_audit_filesystem_access(self, tmp_path):
        layer = ProcessSandboxLayer()
        (tmp_path / "test.txt").write_text("hello", encoding="utf-8")
        entries = layer.audit_filesystem_access(str(tmp_path), "scan")
        assert len(entries) >= 1
        assert entries[0].operation == "scan"

    def test_validate_changes_clean(self):
        layer = ProcessSandboxLayer()
        before = [
            FilesystemAuditEntry(path="a.txt", operation="scan", checksum="abc", size_bytes=100),
        ]
        after = [
            FilesystemAuditEntry(path="a.txt", operation="scan", checksum="abc", size_bytes=100),
            FilesystemAuditEntry(path="b.txt", operation="scan", checksum="def", size_bytes=200),
        ]
        result = layer.validate_changes(before, after)
        assert result.allowed is True
        assert result.new_files == 1

    def test_validate_changes_suspicious(self):
        layer = ProcessSandboxLayer()
        before: list = []
        after = [
            FilesystemAuditEntry(path="secrets/.env", operation="write", checksum="xyz", size_bytes=500),
        ]
        result = layer.validate_changes(before, after)
        assert result.allowed is False
        assert len(result.suspicious_paths) >= 1

    def test_execute_with_timeout(self):
        layer = ProcessSandboxLayer()
        result = layer.execute_in_sandbox(
            code="import time; time.sleep(10)",
            timeout=1,
        )
        assert result.status == SandboxStatus.TIMEOUT
