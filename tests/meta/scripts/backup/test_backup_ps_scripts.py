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

BACKUP_DIR = Path(__file__).resolve().parents[4] / "scripts" / "backup"
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


def test_dumps_rotation_leg_logs_the_state_value_it_read() -> None:
    """⑫（2026-10-11 统筹批复三）：轮转腿必须把"读到的状态位值"写进日志。

    病形：轮转判据读的是 state 文件里**上一轮**写的 last_ch_backup_status（本轮的值要到
    Stage 4 才落盘），而旧实现只打一句 "CH backup not ok"——事后无法区分"旧值非 ok"与
    "读失败被 catch 兜成 false"。本测钉三件事：①读值有默认占位（catch 支也留得下痕）；
    ②两条出口消息都内插该值；③判据本身一字未动（仍 -eq "ok"）。
    """
    text = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    assert '$dumpsStateRead = "<unreadable>"' in text, "缺读值占位：catch 支会无痕"
    assert "$dumpsStateRead = [string]$sJson.last_ch_backup_status" in text, "没把读到的状态位取出来"
    assert '$dumpsStateOk = ($dumpsStateRead -eq "ok")' in text, '判据被改动（应仍比较 "ok"）'
    assert "state last_ch_backup_status={0}" in text or "state last_ch_backup_status={1}" in text, "两条出口未内插读值"
    assert 'Write-Warn "DB dumps rotation skipped (CH backup not ok' not in text, "仍留着不可归因的旧 WARN"


def _extract_ps_function(text: str, name: str) -> str:
    """按大括号配对切出顶层 function 原文（含签名行），用于把单个函数搬进临时 harness 真跑。"""
    marker = "function " + name
    start = text.index(marker)
    brace = text.index("{", start)
    depth = 0
    for idx in range(brace, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    raise AssertionError("unbalanced braces for " + name)


def test_journal_writer_emits_strict_utf8(tmp_path) -> None:
    """⑫同款可观测性修复（2026-10-12 统筹批复二）：run journal 必须是显式 UTF-8（无 BOM）。

    病形实测：两支完赛样本（194841／225255）严格 UTF-8 解码当场抛错（0xd3@3249／0xbb@2719），
    根因是 `Add-Content` 不带 -Encoding 时继承控制台代码页（本机 936/GBK），凡带中文原生
    错误文本的行就永久解不开——"日志在，但读不出"。本测把真函数搬进 harness 真写一行中文，
    再严格解码回来的字节；harness 本身保持纯 ASCII（PS5.1 读无 BOM UTF-8 脚本会按 ANSI 解，
    中文源码字面量本身就会被曲解），故中文字符用 [char]0xXXXX 构造。
    """
    src = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    fn = _extract_ps_function(src, "Write-Journal")
    out = tmp_path / "journal.log"
    harness = tmp_path / "journal_harness.ps1"
    body = (
        "$script:JournalFile = '"
        + out.as_posix().replace("/", "\\")
        + "'\n"
        + fn
        + "\n$zh = [string][char]0x4E2D + [string][char]0x6587\n"
        + "Write-Journal ('WARN ' + $zh + ' native error text')\n"
    )
    harness.write_text(body, encoding="ascii")
    proc = _run_ps("& '" + harness.as_posix().replace("/", "\\") + "'")
    assert proc.returncode == 0, f"harness 未跑通: {proc.stderr[:200]}"
    assert out.exists(), "Write-Journal 没产出任何文件（函数搬家失败或路径不对）"
    data = out.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf"), "journal 落成带 BOM，与 report 的无 BOM 口径不一致"
    text = data.decode("utf-8")  # 严格解码：GBK 字节会在这里抛 UnicodeDecodeError
    assert "中文" in text, f"中文行没原样回来: {text!r}"
    assert "| WARN 中文 native error text" in text, "行格式（时刻 | 消息）被改动"


def test_journal_writer_does_not_rely_on_bare_add_content() -> None:
    """结构位：禁回退到 `Add-Content -LiteralPath $script:JournalFile`（无 -Encoding 即继承代码页）。

    只看**语句位**，不看注释——修因说明里合法地提到 Add-Content。
    """
    src = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    fn = _extract_ps_function(src, "Write-Journal")
    code = [ln.strip() for ln in fn.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert not [ln for ln in code if ln.startswith("Add-Content")], (
        "Write-Journal 回退到 Add-Content 隐式编码（GBK 陷阱源头）"
    )
    joined = " ".join(code)
    assert "UTF8Encoding" in joined and "$false" in joined, "没写明显式 UTF-8 且无 BOM"
    assert "AppendAllText" in joined, "写盘口被换成未知路径，回归测与结构测须一起复核"
