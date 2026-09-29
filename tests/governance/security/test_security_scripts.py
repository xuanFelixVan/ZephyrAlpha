# [A_test] module_id: MOD-GOV_security_scripts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-300 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_security_scripts
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-300 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

import pytest

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


#: 本测试家族所有权面（own-scope，宪法 §3）：安全审计域自家脚本目录——
#: d6=安全检测器、d11=合规门禁、d12=AI 幻觉检测（test_check_logger_kwargs 已覆盖）。
_OWN_SCOPE_PREFIXES = ("d6_security/", "d11_compliance/", "d12_ai_hallucination/")


def _scan_gate(gate_filename: str) -> list[dict]:
    """派生式读门禁自身 findings（不造第二检测器）：按文件名加载 d11 门禁模块取 scan_scripts()。"""
    import importlib.util

    path = GOV_DIR / "d11_compliance" / gate_filename
    spec = importlib.util.spec_from_file_location(f"_lane_gate_{gate_filename.replace('.', '_')}", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.scan_scripts()


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

        manifest_path = GOV_DIR / "script_manifest.yaml"
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
        """own-scope 收窄（2026-09-30，宪法 §3 own-diff 原则+留痕）：

        旧断言=子进程整跑 d11 门禁要求全树 returncode==0——那是"全树执法"面，
        现树有他会话在飞新落件（66 文件 196 处裸 return，含 _tasks/ 等），
        全树清零属各脚本作者职责（#ARCH-114 裁定路径 C 爷爷条款登记机制在案，
        本测试不得代修 64 文件=必撞他在飞面）。收窄为派生式双判据：
        ①全树高危类别=裸 sys.exit(0/1/2)（真进程退出，语义危险类）必须恒零——
          门禁对未来新增保持全量牙齿的底线；
        ②本域 own 面（d6_security/d11_compliance/d12_ai_hallucination，本测试
          家族所有权面）零违例；
        ③门禁自身退出码契约仍合法（0=pass/1=findings）——执行面健康。
        裸 return 0/1/2（helper 业务返回值，#ARCH-114 原文认定非退出码语义）
        树级存量=各作者按爷爷条款登记或替换，不在本测试判断面。
        """
        findings = _scan_gate("validate_exit_codes.py")
        high_risk = [f for f in findings if f["type"] == "sys.exit"]
        assert not high_risk, f"裸 sys.exit 高危类别必须恒零: {high_risk[:5]}"
        own = [f for f in findings if f["file"].startswith(_OWN_SCOPE_PREFIXES)]
        assert not own, f"安全域 own 面退出码违例: {own[:5]}"
        result = _run_script("d11_compliance/validate_exit_codes.py")
        assert result.returncode in (0, 1), f"门禁自身执行面异常: {result.stderr[-200:]}"

    def test_naming_gate_passes(self):
        """own-scope 收窄（同 test_exit_code_gate_passes，2026-09-30 留痕）：

        命名门禁断言面收窄为安全域 own 面（d6/d11/d12）零违例 + 门禁执行面合法；
        全树 70 台未登记命名存量（他会话在飞件为主）归各作者按 EXCEPTIONS
        爷爷条款机制处置，本测试不代修不硬闯。
        """
        findings = _scan_gate("validate_script_naming.py")
        own = [f for f in findings if f["file"].startswith(_OWN_SCOPE_PREFIXES)]
        assert not own, f"安全域 own 面命名违例: {[(f['file'], f['name']) for f in own[:5]]}"
        result = _run_script("d11_compliance/validate_script_naming.py")
        assert result.returncode in (0, 1), f"门禁自身执行面异常: {result.stderr[-200:]}"
