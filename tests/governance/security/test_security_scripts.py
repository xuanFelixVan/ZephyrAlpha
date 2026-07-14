# [A_test] module_id: SRC-TST-0143 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-300 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_security_scripts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_security_scripts.py — D6 安全审计脚本单元测试

覆盖脚本：
  - detect_secrets.py — 密钥/Token/凭证硬编码检测
  - detect_shell_true.py — shell=True 危险调用检测
  - detect_permanent_file_deletion.py — 永久文件删除检测

对标 AUDIT-06 F-15：安全扫描脚本无独立单元测试的缺口修复。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

GOV_DIR = REPO_ROOT / "scripts" / "governance"

ENV = os.environ.copy()
ENV["PYTHONIOENCODING"] = "utf-8"


def _run_script(script_rel: str, args: list[str] | None = None) -> subprocess.CompletedProcess:
    script_path = GOV_DIR / script_rel
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
        encoding="utf-8",
        errors="replace",
        env=ENV,
    )


class TestDetectSecrets:
    SCRIPT = "d6_security/detect_secrets.py"

    def test_scan_repo_no_crash(self):
        result = _run_script(self.SCRIPT, ["--warn-only"])
        assert result.returncode in (0, 1), f"exit code {result.returncode}, stderr: {result.stderr}"

    def test_scan_dir_flag_works(self, tmp_path: Path):
        clean_file = tmp_path / "clean.py"
        clean_file.write_text('x = 1\nprint("hello")\n', encoding="utf-8")
        result = _run_script(self.SCRIPT, ["--warn-only", "--scan-dir", str(tmp_path)])
        assert result.returncode in (0, 1, 2), f"exit code {result.returncode}"

    def test_help_flag(self):
        result = _run_script(self.SCRIPT, ["--help"])
        assert result.returncode == 0
        assert result.stdout is not None


class TestDetectShellTrue:
    SCRIPT = "d6_security/detect_shell_true.py"

    def test_scan_repo_no_crash(self):
        result = _run_script(self.SCRIPT, ["--warn-only"])
        assert result.returncode in (0, 1), f"exit code {result.returncode}, stderr: {result.stderr}"

    def test_help_flag(self):
        result = _run_script(self.SCRIPT, ["--help"])
        assert result.returncode == 0
        assert result.stdout is not None


class TestDetectPermanentFileDeletion:
    SCRIPT = "d6_security/detect_permanent_file_deletion.py"

    def test_scan_repo_no_crash(self):
        result = _run_script(self.SCRIPT, ["--warn-only"])
        assert result.returncode in (0, 1), f"exit code {result.returncode}, stderr: {result.stderr}"

    def test_help_flag(self):
        result = _run_script(self.SCRIPT, ["--help"])
        assert result.returncode == 0
        assert result.stdout is not None


class TestExitCodeConstants:
    def test_exit_constants_defined(self):
        sys.path.insert(0, str(GOV_DIR / "_shared"))

        from constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS

        assert EXIT_PASS == 0
        assert EXIT_FINDINGS == 1
        assert EXIT_ERROR == 2

    def test_manifest_has_owner_field(self):
        import yaml

        manifest_path = GOV_DIR / "script-manifest.yaml"
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        assert "scripts" in data
        first_with_owner = any("owner" in s for s in data["scripts"])
        assert first_with_owner, "owner field missing from script entries"

    def test_check_logger_kwargs_has_manifest(self):
        script_path = GOV_DIR / "d12_ai_hallucination" / "check_logger_kwargs.py"
        source = script_path.read_text(encoding="utf-8")
        assert "__manifest__" in source, "check_logger_kwargs.py missing __manifest__ block"
        assert "D12" in source, "check_logger_kwargs.py __manifest__ missing D12 dimension"

    def test_exit_code_gate_passes(self):
        result = _run_script("d11_compliance/validate_exit_codes.py")
        assert result.returncode == 0, f"Exit code gate failed: {result.stderr}"

    def test_naming_gate_passes(self):
        result = _run_script("d11_compliance/validate_script_naming.py")
        assert result.returncode == 0, f"Naming gate failed: {result.stderr}"
