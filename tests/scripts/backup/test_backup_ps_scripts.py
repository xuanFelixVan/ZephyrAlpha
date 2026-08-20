# tests/scripts/backup/test_backup_ps_scripts.py
"""PowerShell 备份脚本 smoke test——语法解析 + 关键参数契约（#ARCH-BACKUP-PS-SMOKE，2026-08-13）。

病根：backup.ps1 的 `-Encoding UTF8`（大写）在 PS5 下 ValidateSet 校验失败，存在 N 天未被发现——
PowerShell 脚本不在任何测试/门禁射程内，只在真实备份时才暴露。

治本：用 .NET PS 引擎（Parser.ParseFile）对 scripts/backup 下全部 .ps1 做语法解析冒烟，
并校验关键参数契约（-Mode ValidateSet、-Encoding 不得为大写 UTF8）。纳入 pytest，不加新 gate。

运行前提：Windows + powershell.exe 可用（非 Windows 环境自动 skip）。
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

BACKUP_DIR = Path(__file__).resolve().parents[3] / "scripts" / "backup"
PS_SCRIPTS = [
    "backup.ps1",
    "backup_daily_trigger.ps1",
    "backup_ch_vm.ps1",
    "restore.ps1",
    "backup_manual.ps1",
]

pytestmark = pytest.mark.skipif(
    shutil.which("powershell") is None,
    reason="powershell.exe 不可用（非 Windows 环境），跳过 PS smoke test",
)


def _run_ps(ps_command: str) -> subprocess.CompletedProcess:
    """执行一段 PowerShell 并返回结果（-NoProfile 保证环境干净）。"""
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.parametrize("script_name", PS_SCRIPTS)
def test_ps_script_parses(script_name: str) -> None:
    """每个 .ps1 必须被 PS 引擎成功解析（无语法错误）。"""
    script_path = BACKUP_DIR / script_name
    assert script_path.exists(), f"脚本不存在: {script_path}"

    # 用单引号包裹路径（路径无单引号），ParseFile 返回语法错误集合
    ps = (
        "$errs=$null; $tokens=$null; "
        f"$null=[System.Management.Automation.Language.Parser]::ParseFile('{script_path}',[ref]$tokens,[ref]$errs); "
        "if($errs -and $errs.Count -gt 0){ $errs | ForEach-Object { Write-Output $_.Message }; exit 1 } "
        "else { Write-Output 'PARSE_OK' }"
    )
    proc = _run_ps(ps)
    assert proc.returncode == 0 and "PARSE_OK" in proc.stdout, (
        f"{script_name} 语法解析失败:\n{proc.stdout}\n{proc.stderr}"
    )


def test_no_uppercase_utf8_outfile() -> None:
    """回归门禁：Out-File 不得使用大写 -Encoding UTF8（PS5 ValidateSet 不接受）。

    直接扫源码文本（比跑 PS 更快），命中即失败。Get-Content 读取用大写 UTF8 合法，
    仅 Out-File/Set-Content 等写入 cmdlet 的大写 UTF8 在 PS5 下报错。
    """
    offenders: list[str] = []
    for script_name in PS_SCRIPTS:
        text = (BACKUP_DIR / script_name).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "Out-File" in line and "-Encoding UTF8" in line:
                offenders.append(f"{script_name}:{lineno}: {line.strip()}")
    assert not offenders, "发现 PS5 不兼容的大写 Out-File -Encoding UTF8：\n" + "\n".join(offenders)


def test_backup_ps1_mode_validateset() -> None:
    """契约：backup.ps1 的 -Mode 参数 ValidateSet 必须含 all/code/ch（AST 级校验）。"""
    script_path = BACKUP_DIR / "backup.ps1"
    ps = (
        "$errs=$null; $tokens=$null; "
        f"$ast=[System.Management.Automation.Language.Parser]::ParseFile('{script_path}',[ref]$tokens,[ref]$errs); "
        "$param=$ast.FindAll({param($n) $n -is [System.Management.Automation.Language.ParameterAst]},$true) "
        "  | Where-Object { $_.Name.VariablePath.UserPath -eq 'Mode' }; "
        "if(-not $param){ Write-Output 'NO_MODE_PARAM'; exit 1 } "
        "$vs=$param.Attributes | Where-Object { $_.TypeName.Name -eq 'ValidateSet' }; "
        "if(-not $vs){ Write-Output 'NO_VALIDATESET'; exit 1 } "
        "$vals=$vs.PositionalArguments | ForEach-Object { $_.Extent.Text -replace '[\"'']','' }; "
        "Write-Output ($vals -join ',')"
    )
    proc = _run_ps(ps)
    out = proc.stdout
    for expected in ("all", "code", "ch"):
        assert expected in out, f"backup.ps1 -Mode ValidateSet 缺少 '{expected}': {out}\n{proc.stderr}"
