# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.6
# [MODULE] tests.dr.test_backup_ch_vm_autocheck
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/backup/backup_ch_vm.ps1 (regex-extracted Get-AutoCheckDecision body + AutoCheck 分支正文)
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/dr/test_backup_ch_vm_autocheck.py
"""backup_ch_vm.ps1 AutoCheck 判定语义常驻尺（09-26 事故治本配套，FMS 收尾班 2026-09-27）。

背景（[亲验] 09-26 06:00 实跑）：WeeklyVMBackup 计划任务走 -AutoCheck，SSH 探测
"成功返回但 stdout 里没有 =V=/=H="，旧代码把 `$version`/`$hash` 留空后仍落到
"proceeding to full backup"——即**探测未知=判定为变更=复制 599 GiB**（fail-open）。
后果：`F:\\ch_vm_backup\\data.vhdx` 被复活，F 盘 free 766.6→167.6 GiB，击穿
backup_cold_audit_sop §一.1 的 F≥700 GiB 红线；同型预测见
docs/_working/disk_reorg_campaign/LEDGER_final.md 处方 P-6。

本尺锁三件事（缺一即本尺无判别力）：
1. **判定纯函数四态**（skip/proceed/blocked_unprobeable/blocked_unparsable）——
   未知态必须 blocked，绝不 proceed；
2. **函数有调用点**（防"装饰件"：一行判定挂在无人读的位置＝没修）；
3. **blocked 必真停机**（AutoCheck 分支内 blocked 路径必须 exit，且旧 fail-open
   字样"forcing full backup"不得复现）。

函数体用正则从 ps1 抽（不复制粘贴进本文件），抽不到即 fail——这本身就是
"函数被改名/删除"的守卫。同族先例：tests/dr/test_backup_lock_semantics.py。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "backup" / "backup_ch_vm.ps1"

_FUNC_NAME = "Get-AutoCheckDecision"
_OLD_FAIL_OPEN_PHRASE = "forcing full backup"


def _script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _extract_function_body() -> str:
    """抽 ps1 里的判定函数全文（含签名），抽不到=判据被删/改名=直接 fail。"""
    text = _script_text()
    m = re.search(rf"^function {_FUNC_NAME}\s*\{{(?P<body>.*?)^\}}\s*$", text, re.M | re.S)
    if not m:
        pytest.fail(f"{_FUNC_NAME} 不在 {SCRIPT.name} 中（被改名/删除=治本回退）")
    return f"function {_FUNC_NAME} {{{m.group('body')}\n}}"


def _extract_autocheck_branch() -> str:
    """抽 -AutoCheck 分支正文，用于校验调用点与停机位置。"""
    text = _script_text()
    m = re.search(r"^if \(\$AutoCheck\) \{(?P<body>.*?)^\}\s*$", text, re.M | re.S)
    if not m:
        pytest.fail("-AutoCheck 分支结构漂移，本尺失去落点（请同步修正本测试选择器）")
    return m.group("body")


@pytest.fixture(scope="module")
def harness_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("chvm_autocheck")


def _decide(
    tmp: Path,
    probe_ok: bool,
    version: str,
    hashv: str,
    last_version: str,
    last_hash: str,
) -> str:
    ps = tmp / "case.ps1"
    ps.write_text(
        "$ErrorActionPreference='Stop'\n"
        + _extract_function_body()
        + "\n$d = "
        + f"{_FUNC_NAME} -ProbeOk {'$true' if probe_ok else '$false'} "
        + f"-Version '{version}' -Hash '{hashv}' "
        + f"-LastVersion '{last_version}' -LastHash '{last_hash}'\n"
        + 'Write-Output "RESULT=$d"\n',
        encoding="ascii",
    )
    r = subprocess.run(  # noqa: bare-subprocess  ps1 语义常驻尺需真跑 PowerShell，与同目录 test_backup_lock_semantics 同构
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert r.returncode == 0, f"powershell 非零退出：{r.stdout}\n{r.stderr}"
    m = re.search(r"RESULT=(\S+)", r.stdout)
    assert m, f"判定函数无返回值（stdout）：{r.stdout}"
    return m.group(1).strip()


class TestDecisionSemantics:
    """四态判定：未知态必须 blocked，绝不 proceed。"""

    def test_probe_failure_blocks_not_proceeds(self, harness_dir: Path) -> None:
        """09-26 事故复现案①：探测失败→blocked（旧代码此处 proceed）。"""
        got = _decide(harness_dir, False, "", "", "26.6.1", "a" * 64)
        assert got == "blocked_unprobeable", got

    def test_empty_probe_output_blocks(self, harness_dir: Path) -> None:
        """09-26 事故真实形态：SSH 返回 0 但 =V=/=H= 皆空→blocked_unparsable。"""
        got = _decide(harness_dir, True, "", "", "26.6.1.1193", "a" * 64)
        assert got == "blocked_unparsable", got

    def test_partial_probe_output_blocks(self, harness_dir: Path) -> None:
        """只有版本没有 hash（users.xml 缺失等）→ 仍是未知态，不得复制。"""
        got = _decide(harness_dir, True, "26.6.1.1193", "", "26.6.1.1193", "a" * 64)
        assert got == "blocked_unparsable", got

    def test_unchanged_skips(self, harness_dir: Path) -> None:
        got = _decide(harness_dir, True, "26.6.1.1193", "b" * 64, "26.6.1.1193", "b" * 64)
        assert got == "skip", got

    def test_version_change_proceeds(self, harness_dir: Path) -> None:
        got = _decide(harness_dir, True, "26.7.1.1", "b" * 64, "26.6.1.1193", "b" * 64)
        assert got == "proceed", got

    def test_hash_change_proceeds(self, harness_dir: Path) -> None:
        got = _decide(harness_dir, True, "26.6.1.1193", "c" * 64, "26.6.1.1193", "b" * 64)
        assert got == "proceed", got

    def test_first_ever_baseline_proceeds_with_real_readings(self, harness_dir: Path) -> None:
        """装完第一次跑：有真实 version+hash 且无基线=确属"需要建基线的全量"，放行是设计内。

        与 blocked 的分界=**有没有可信读数**；09-26 的病根是没读数还装成"有变更"。
        """
        got = _decide(harness_dir, True, "26.6.1.1193", "b" * 64, "", "")
        assert got == "proceed", got


class TestWiringNotDecorative:
    """判定必须接在 -AutoCheck 分支上并真停机（防装饰件）。"""

    def test_function_is_called_on_autocheck_path(self) -> None:
        branch = _extract_autocheck_branch()
        assert _FUNC_NAME in branch, f"-AutoCheck 分支未调用 {_FUNC_NAME}=护栏是摆设"

    def test_blocked_path_exits_loudly(self) -> None:
        branch = _extract_autocheck_branch()
        blocked_idx = branch.find("blocked*")
        assert blocked_idx >= 0, "AutoCheck 分支缺 blocked 处置段"
        tail = branch[blocked_idx:]
        assert "exit 3" in tail, "blocked 段未以非零退出报警（fail-visible 缺失）"
        copy_idx = tail.find("$Force = $true")
        exit_idx = tail.find("exit 3")
        assert copy_idx < 0 or exit_idx < copy_idx, "blocked 段之后仍可落到全量复制=治本失效"

    def test_old_fail_open_wording_gone(self) -> None:
        """旧措辞（探测失败→forcing full backup）不得复现。"""
        assert _OLD_FAIL_OPEN_PHRASE not in _script_text(), _OLD_FAIL_OPEN_PHRASE

    def test_script_stays_ascii(self) -> None:
        """.ps1 含非 ASCII 会被 PS5.1 按 GBK 解码出假语法错误（根宪法 §9.7）。"""
        raw = SCRIPT.read_bytes()
        bad = [i for i, b in enumerate(raw) if b > 127]
        assert not bad, f"backup_ch_vm.ps1 非 ASCII 字节 {len(bad)} 个，首个偏移 {bad[:3]}"


@pytest.mark.skipif(sys.platform != "win32", reason="需要 PowerShell（Windows 宿主）")
def test_script_parses_without_syntax_errors(tmp_path: Path) -> None:
    """语法自检：改完必须 ParseErrors=0（PS 解析器实跑，非肉眼）。"""
    probe = tmp_path / "parse.ps1"
    probe.write_text(
        "$t=[System.Management.Automation.PSParser]::Tokenize("
        "(Get-Content -Raw -LiteralPath '" + str(SCRIPT).replace("'", "''") + "'),"
        '[ref]$null)\nWrite-Output "TOKENS=$($t.Count)"\n',
        encoding="ascii",
    )
    r = subprocess.run(  # noqa: bare-subprocess  同上：ps1 语法只能由 PowerShell 自己裁
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(probe)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"TOKENS=(\d+)", r.stdout)
    assert m and int(m.group(1)) > 1000, f"token 数异常（解析可能失败）：{r.stdout}"
