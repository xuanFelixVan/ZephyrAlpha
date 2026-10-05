# [MODULE] tests.backup.test_stage3_vault_mtime_and_verdict
# [TTL] task_bound
# [STARTUP] on_demand_test（仅 pytest 触发，零 scheduled_task）
# [CONSUMERS] pytest；案卷 docs/_working/total_command_closeout/wave4/dr_chain_report.md §4.2/§4.3
# [DOMAIN] D_INFRA_RUNTIME
# [BLUEPRINT] MOD-BACKUP-STAGE3-VAULT | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md | §4.2/§4.3
# [DEPENDENCIES] pytest；tests/backup conftest
# [MATURITY] stable
# [MODIFY-GUARD] none（只读校验/生成器，无状态写盘）
# [STABILITY] stable
# [SAFETY] n/a
# [AI_AUTONOMY] n/a
# [ERROR_CONTRACT] n/a
# [TESTS] n/a
# [INVARIANTS] 被测代码从 scripts/backup/backup.ps1 **原文抽取**后执行（禁复刻第二套判据）；
#   全程只写 pytest tmp_path，禁触 F:/G: 真实备份盘；禁任何删除动作；只读探测
"""P-27 只读位打时间戳 + X-17/N-5 汇总判据的回归网（波 4.2/4.3）。

红证口径：
1. 只读件（实测 0o100444 的等价物）上直接赋 LastWriteTimeUtc 必抛"访问被拒绝"＝改前病；
2. 过 `Set-VaultMtime` 后清位成功、时间戳落定、**源件只读位保持**（只解冻快照副本）；
3. 汇总判据真值表：单件失败 → partial（不得一票否决），robocopy 硬错/全件失败 → failed
   （不得静默忽略），零失败 → ok。
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT  # SSoT：本文件原自算 parents[N]，与 canonical 等值

PS1 = REPO_ROOT / "scripts" / "backup" / "backup.ps1"

pytestmark = pytest.mark.skipif(not PS1.exists(), reason="backup.ps1 absent")


def _extract_shipped_function(name: str) -> str:
    """按大括号配平从真源抽函数原文（复刻＝第二套判据，禁）。"""
    text = PS1.read_text(encoding="utf-8")
    start = text.index("function " + name)
    i = text.index("{", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start : j + 1]
    raise AssertionError("unbalanced braces for " + name)


def _extract_verdict_block() -> str:
    text = PS1.read_text(encoding="utf-8")
    m = re.search(r"(?m)^\s*\$structural = .*$", text)
    assert m, "shipping backup.ps1 lost the $structural aggregate verdict line"
    return m.group(0).strip()


def _run_ps(tmp_path: Path, body: str) -> str:
    script = tmp_path / "probe.ps1"
    script.write_text(body, encoding="utf-8")
    res = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert res.returncode == 0, f"powershell failed rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res.stdout


def test_readonly_snapshot_copy_gets_mtime_without_touching_source(tmp_path: Path) -> None:
    """红证 1+2：改前直赋必抛，改后 helper 成且源件只读位不动。"""
    fn = _extract_shipped_function("Set-VaultMtime")
    verdict = _extract_verdict_block()
    assert "$itemTotal -gt 0 -and $linkFail -ge $itemTotal" in verdict
    body = f"""
$ErrorActionPreference='Continue'
$script:MtimeFail=0; $script:RoCleared=0; $script:errors3=@()
{fn}
$srcDir = Join-Path $PSScriptRoot 'src'
$dstDir = Join-Path $PSScriptRoot 'snap'
New-Item -ItemType Directory -Path $srcDir, $dstDir | Out-Null
$srcFile = Join-Path $srcDir 'readonly_item.md'
Set-Content -LiteralPath $srcFile -Value 'probe' -Encoding UTF8
Set-ItemProperty -LiteralPath $srcFile -Name IsReadOnly -Value $true
$dstFile = Join-Path $dstDir 'readonly_item.md'
[System.IO.File]::Copy($srcFile, $dstFile, $true)
$stamp = (Get-Date).AddHours(-3)
$directErr = ''
try {{ (Get-Item -LiteralPath $dstFile -Force).LastWriteTimeUtc = $stamp }} catch {{ $directErr = 'THREW' }}
Write-Output ("DIRECT_ASSIGN_THREW=" + $directErr)
$ok = Set-VaultMtime $dstFile $stamp
$dst = Get-Item -LiteralPath $dstFile -Force
$src = Get-Item -LiteralPath $srcFile -Force
Write-Output ("HELPER_OK=" + $ok + " RoCleared=" + $script:RoCleared + " MtimeFail=" + $script:MtimeFail)
Write-Output ("DST_READONLY=" + $dst.IsReadOnly + " SRC_READONLY=" + $src.IsReadOnly)
Write-Output ("MTIME_MATCH=" + [string]($dst.LastWriteTimeUtc -eq $stamp.ToUniversalTime()))
"""
    out = _run_ps(tmp_path, body)
    assert "DIRECT_ASSIGN_THREW=THREW" in out, out  # 改前病复现
    assert "HELPER_OK=True RoCleared=1 MtimeFail=0" in out, out
    assert "DST_READONLY=False SRC_READONLY=True" in out, out  # 只解冻副本，不碰源
    assert "MTIME_MATCH=True" in out, out


def test_healthy_item_does_not_inflate_counters(tmp_path: Path) -> None:
    """helper 不得把正常件记成异常（否则 partial 计数虚高＝新的静默失真）。"""
    fn = _extract_shipped_function("Set-VaultMtime")
    body = f"""
$script:MtimeFail=0; $script:RoCleared=0; $script:errors3=@()
{fn}
$f = Join-Path $PSScriptRoot 'plain.txt'
Set-Content -LiteralPath $f -Value 'plain' -Encoding UTF8
$ok = Set-VaultMtime $f (Get-Date).AddHours(-1)
Write-Output ("OK=" + $ok + " RoCleared=" + $script:RoCleared + " MtimeFail=" + $script:MtimeFail)
"""
    out = _run_ps(tmp_path, body)
    assert "OK=True RoCleared=0 MtimeFail=0" in out, out


@pytest.mark.parametrize(
    ("rc", "total", "copy_fail", "mtime_fail", "want"),
    [
        (0, 336678, 0, 1, "partial"),  # 09-26 06:00 实测轮：旧尺判 failed
        (0, 336678, 0, 0, "ok"),
        (16, 100, 0, 0, "failed"),  # robocopy 硬错
        (0, 100, 100, 0, "failed"),  # 逐件全失败＝整轮没交付
        (0, 100, 5, 2, "partial"),
        (0, 0, 1, 0, "partial"),  # 首建全量分支（itemTotal 未知）
    ],
)
def test_aggregate_verdict_matrix(
    tmp_path: Path, rc: int, total: int, copy_fail: int, mtime_fail: int, want: str
) -> None:
    """真值表跑在**抽取的 shipped 判据**上：一票否决已拆，静默忽略未取。"""
    body = f"""
$rcCode={rc}; $itemTotal={total}; $linkFail={copy_fail}; $script:MtimeFail={mtime_fail}
{_extract_verdict_block()}
$vaultStatus = 'ok'
if ($structural) {{ $vaultStatus = 'failed' }}
elseif ($linkFail -gt 0 -or $script:MtimeFail -gt 0) {{ $vaultStatus = 'partial' }}
Write-Output ("VERDICT=" + $vaultStatus)
"""
    out = _run_ps(tmp_path, body)
    assert f"VERDICT={want}" in out, out


def test_partial_is_not_vetoed_but_is_mirrored_into_state() -> None:
    """STAGE 4 汇总：partial 不得把 last_backup_status 拖成 failed，但必须另键可见。"""
    text = PS1.read_text(encoding="utf-8")
    stage4 = text[text.index("# ==================== STAGE 4: Report") :]
    assert '-eq "failed"' in stage4, "aggregate veto must stay keyed on failed only"
    assert "last_backup_partial_items" in stage4, "partial items must be mirrored into state"
    assert "last_code_backup_snapshot_mode" in stage4, "hardlinked 读数必须可与 snapshot_mode 一起解释"
    report_keys = ("snapshot_mode", "item_total", "mtime_failures", "readonly_bits_cleared")
    stage3 = text[: text.index("# ==================== STAGE 4: Report")]
    for k in report_keys:
        assert k + "=" in stage3 or k + "=" in text, f"code_backup lost interpretability field {k}"
