# [A_test] module_id: MOD-INF-043 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §dr-vault
# [MODULE] tests.dr.test_backup_copy_share
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/backup/backup.ps1 (regex-extracted Copy-FileShareTolerant body), powershell
# [CONSUMERS] pytest tests/dr
# [STARTUP] manual
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/dr/test_backup_copy_share.py
# [TTL] task_bound
"""test_backup_copy_share.py — backup.ps1 vault 句柄复制（H04, 2026-09-29 SW11）常驻尺。

大白话：夜间备份搬文件用的是"普通复制"，它有两个坑会喂大 error_sample：
（a）只读位源——普通复制把只读位一并遗传给副本，紧随其后的 mtime 对齐写回
（LastWriteTimeUtc 赋值）在只读位上必炸 UnauthorizedAccessException，该文件
被计成一次失败；（b）源正被别的进程以窄共享模式持有。治本=改"句柄复制"：
副本按全新流建出（不遗传只读位，(a) 断根），源按 FileShare.ReadWrite 开门
（(b) 缓解）。本尺钉三件事：
1. 函数存在性：Copy-FileShareTolerant 必须仍以同名在 backup.ps1 里（正则抽体，
   抽不到=被改名/删除=本尺红），同 test_backup_lock_semantics 的守卫口径。
2. 判别力（同进程红绿对拍）：只读位源上——旧路（File.Copy+mtime 写回）必炸
   （事故形态复现），新路必绿、字节一致、且只读位不遗传。
3. mtime 与源逐刻一致（vault diff 一致性契约，旧路既有行为不回退）。

实现要点：
- 函数体正则从 ps1 正文抽，注入临时 ps1 执行；不复制粘贴进本文件（防两处漂移）。
- 只读位用真实 IsReadOnly 属性构造，零 sleep，全部 tmp_path，不碰生产路径。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PS1 = _REPO_ROOT / "scripts" / "backup" / "backup.ps1"


def _extract_function_body() -> str:
    """从 backup.ps1 正则抽 Copy-FileShareTolerant 函数体；抽不到=契约破坏=fail。"""
    src = _PS1.read_text(encoding="ascii")
    m = re.search(r"function Copy-FileShareTolerant \{.*?\n\}", src, re.DOTALL)
    assert m, "backup.ps1 缺 Copy-FileShareTolerant（H04 契约破坏：函数被改名/删除）"
    return m.group(0)


def test_function_body_present_and_ascii_pure():
    body = _extract_function_body()
    assert "FileShare]::ReadWrite" in body
    assert "CopyTo(" in body
    # .ps1 必须纯 ASCII（PowerShell 5.1 无 BOM 按 GBK 解码铁律）
    _PS1.read_text(encoding="ascii")


_PWSH_RUNNER_TEMPLATE = r"""
{func_body}

$ErrorActionPreference = 'Stop'
$src = '{src}'
$dstFail = '{dst_fail}'
$dstOk = '{dst_ok}'

# 1) read-only-attributed source (the incident form): legacy File.Copy inherits
#    the ReadOnly bit onto the destination, so the vault's mtime-parity write
#    throws UnauthorizedAccessException and the file counts as a failure.
$bytes = [System.Text.Encoding]::ASCII.GetBytes('vault-copy-share-tolerance-probe-0123456789')
[System.IO.File]::WriteAllBytes($src, $bytes)
(Get-Item -LiteralPath $src).IsReadOnly = $true

# 2) red leg: legacy File.Copy + mtime-parity write must throw (incident repro)
$oldFailed = $false
try {{
    [System.IO.File]::Copy($src, $dstFail, $false)
    (Get-Item -LiteralPath $dstFail).LastWriteTimeUtc = (Get-Item -LiteralPath $src).LastWriteTimeUtc
}} catch {{ $oldFailed = $true }}
if ($oldFailed) {{ Write-Output 'OLD_PATH_BLOCKED=1' }} else {{ Write-Output 'OLD_PATH_BLOCKED=0' }}

# 3) green leg: handle copy creates a fresh (non-readonly) destination, so the
#    mtime-parity write succeeds and the bytes match the source.
Copy-FileShareTolerant -Source $src -Dest $dstOk -Overwrite $false
(Get-Item -LiteralPath $dstOk).LastWriteTimeUtc = (Get-Item -LiteralPath $src).LastWriteTimeUtc
$same = (Compare-Object -ReferenceObject $bytes -DifferenceObject ([System.IO.File]::ReadAllBytes($dstOk)) -SyncWindow 0) -eq $null
$ro = (Get-Item -LiteralPath $dstOk).IsReadOnly
Write-Output ("NEW_COPY_OK=" + [bool]$same)
Write-Output ("NEW_DST_READONLY=" + $ro)
"""


def test_share_tolerant_copy_beats_readonly_bit_inheritance(tmp_path):
    """只读位源（事故形态）：旧路 mtime 写回必炸（error_sample 失败源），新路绿且只读位不遗传。"""
    body = _extract_function_body()
    src = tmp_path / "src_readonly.tmp"
    dst_fail = tmp_path / "dst_old.bin"
    dst_ok = tmp_path / "dst_new.bin"
    script = tmp_path / "probe.ps1"
    script.write_text(
        _PWSH_RUNNER_TEMPLATE.format(
            func_body=body,
            src=str(src),
            dst_fail=str(dst_fail),
            dst_ok=str(dst_ok),
        ),
        encoding="ascii",
    )
    r = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    out = r.stdout
    assert "OLD_PATH_BLOCKED=1" in out, f"红证失效（旧路未在只读位上炸）: {out} {r.stderr}"
    assert "NEW_COPY_OK=True" in out, f"绿证失败（句柄复制未成或字节不一致）: {out} {r.stderr}"
    assert "NEW_DST_READONLY=False" in out, f"只读位被遗传（事故未治本）: {out} {r.stderr}"
    assert not dst_fail.exists() or dst_fail.exists()  # 旧路产物可有可无（throw 点不定）


_PWSH_MTIME_TEMPLATE = r"""
{func_body}

$ErrorActionPreference = 'Stop'
$src = '{src}'
$dst = '{dst}'
[System.IO.File]::WriteAllText($src, 'mtime-parity-probe')
$srcMtime = (Get-Item -LiteralPath $src).LastWriteTimeUtc
Copy-FileShareTolerant -Source $src -Dest $dst -Overwrite $false
(Get-Item -LiteralPath $dst).LastWriteTimeUtc = $srcMtime
$par = ((Get-Item -LiteralPath $dst).LastWriteTimeUtc -eq $srcMtime)
Write-Output ("MTIME_PARITY=" + $par)
"""


def test_mtime_parity_with_source(tmp_path):
    """vault 复制后 mtime 与源逐刻一致（diff 一致性契约，旧路既有行为不回退）。"""
    body = _extract_function_body()
    src = tmp_path / "src_mtime.txt"
    dst = tmp_path / "dst_mtime.txt"
    script = tmp_path / "mtime_probe.ps1"
    script.write_text(
        _PWSH_MTIME_TEMPLATE.format(func_body=body, src=str(src), dst=str(dst)),
        encoding="ascii",
    )
    r = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert "MTIME_PARITY=True" in r.stdout, f"mtime 失真: {r.stdout} {r.stderr}"


if __name__ == "__main__":
    sys.exit(pytest_main := __import__("pytest").main([__file__, "-q"]))
