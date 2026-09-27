# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.6
# [MODULE] tests.dr.test_backup_ch_vm_autocheck
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/backup/backup_ch_vm.ps1 (regex-extracted decision fns + AutoCheck/CompactWindow 分支正文), scripts/backup/restore.ps1 ($ChVmImageHome 读侧对齐)
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/dr/test_backup_ch_vm_autocheck.py
"""backup_ch_vm.ps1 判定语义常驻尺（09-26 事故治本 + 停机压缩窗口，FMS 收尾班 2026-09-27）。

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
    """语法自检：改完必须 ParseErrors 数=0（PS 语言解析器实跑，非肉眼、非只数 token）。"""
    probe = tmp_path / "parse.ps1"
    probe.write_text(
        "$errs=$null\n$toks=$null\n"
        "[void][System.Management.Automation.Language.Parser]::ParseFile("
        "(Convert-Path '" + str(SCRIPT).replace("'", "''") + "'),[ref]$toks,[ref]$errs)\n"
        'Write-Output "PARSE_ERRORS=$($errs.Count)"\n'
        'foreach($e in $errs){ Write-Output "ERR_LINE=$($e.Extent.StartLineNumber)" }\n',
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
    m = re.search(r"PARSE_ERRORS=(\d+)", r.stdout)
    assert m, f"解析器未回报错误数：{r.stdout}"
    assert int(m.group(1)) == 0, f"backup_ch_vm.ps1 存在语法错：{r.stdout}"


class TestCapacityGuard:
    """写侧容量硬闸：四盘红线必须有代码读者，且缺配置不得静默归零变成"永远放行"。"""

    _GUARD_FUNC = "Get-CapacityGuardDecision"

    def _guard_body(self) -> str:
        text = _script_text()
        m = re.search(rf"^function {self._GUARD_FUNC}\s*\{{(?P<body>.*?)^\}}\s*$", text, re.M | re.S)
        if not m:
            pytest.fail(f"{self._GUARD_FUNC} 不在 ps1 中（容量硬闸被删/改名）")
        return f"function {self._GUARD_FUNC} {{{m.group('body')}\n}}"

    def _decide(self, tmp: Path, free: float, need: float, minfree: float) -> str:
        ps = tmp / "guard.ps1"
        ps.write_text(
            "$ErrorActionPreference='Stop'\n"
            + self._guard_body()
            + f"\n$d = {self._GUARD_FUNC} -FreeGB {free} -NeedGB {need} -MinFreeGB {minfree}\n"
            + 'Write-Output "RESULT=$d"\n',
            encoding="ascii",
        )
        r = subprocess.run(  # noqa: bare-subprocess  同族：ps1 语义须真跑 PowerShell
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        m = re.search(r"RESULT=(\S+)", r.stdout)
        assert m, r.stdout
        return m.group(1).strip()

    def test_0926_incident_shape_refused(self, tmp_path: Path) -> None:
        """09-26 实况形态：free 766.7、需 619 → 余 147.7 < 红线 700 ⇒ 必拒（旧代码此处放行）。"""
        assert self._decide(tmp_path, 766.7, 619.0, 700.0) == "refuse_below_red_line"

    def test_healthy_shape_proceeds(self, tmp_path: Path) -> None:
        assert self._decide(tmp_path, 1500.0, 619.0, 700.0) == "proceed"

    def test_too_small_still_refused(self, tmp_path: Path) -> None:
        assert self._decide(tmp_path, 300.0, 619.0, 700.0) == "refuse_too_small"

    def test_guard_is_called_and_exits_loudly(self) -> None:
        """防装饰件：判定必须在预检段被调用，且非 proceed 分支以非零退出报警+落报告。"""
        text = _script_text()
        call_idx = text.find(f"{self._GUARD_FUNC} -FreeGB")
        assert call_idx > 0, "容量判定未在预检段被调用=护栏是摆设"
        tail = text[call_idx:]
        assert "exit 4" in tail[:1800], "拒绝分支未以非零退出报警"
        assert "capacity_guard" in tail[:1800], "拒绝分支未落机读报告"

    def test_missing_config_never_means_zero_floor(self) -> None:
        """读不到配置必须回退内置常量并标 source=fallback，绝不允许 min=0=永久放行。"""
        text = _script_text()
        assert "$MinFreeFallbackGB" in text, "缺兜底常量：配置一坏护栏即失效"
        fb_idx = text.find('guardSource -eq "fallback"')
        assert fb_idx > 0, "无 fallback 处置分支"
        assert "$minFreeGB = $MinFreeFallbackGB" in text[fb_idx : fb_idx + 400], "fallback 未赋值=0"

    def test_red_line_now_has_machine_readable_source(self) -> None:
        """红线数落机读真源（原先只活在 F 盘上的 SOP 散文里，无任何代码读者）。"""
        import yaml

        cfg = REPO_ROOT / "scripts" / "backup" / "backup_config.yaml"
        mins = yaml.safe_load(cfg.read_text(encoding="utf-8"))["capacity_guard"]["min_free_gb"]
        assert mins["F"] == 700 and mins["G"] == 500, mins


def _extract_named_function(name: str) -> str:
    """抽 ps1 里指定函数全文；抽不到=该护栏被改名/删除=直接 fail。"""
    text = _script_text()
    m = re.search(rf"^function {name}\s*\{{(?P<body>.*?)^\}}\s*$", text, re.M | re.S)
    if not m:
        pytest.fail(f"{name} 不在 {SCRIPT.name} 中（被改名/删除=治本回退）")
    return f"function {name} {{{m.group('body')}\n}}"


def _run_ps(tmp: Path, body: str) -> str:
    ps = tmp / "case.ps1"
    ps.write_text("$ErrorActionPreference='Stop'\n" + body + "\n", encoding="ascii")
    r = subprocess.run(  # noqa: bare-subprocess  同族：ps1 语义只能真跑 PowerShell 来裁
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
    m = re.search(r"RESULT=(\S+)", r.stdout)
    assert m, f"判定函数无返回值：{r.stdout}"
    return m.group(1).strip()


class TestCompactionPreconditions:
    """停机压缩前置闸：五态拒绝必须优先于任何"停机"动作，未知态一律 blocked。"""

    _F = "Get-CompactionPrereqDecision"
    _OK = "-HyperVUsable $true -VmFound $true -ImageFreeGB 900 -ImageNeedGB 620 -ActiveSessions 0 -BackupFresh $true"

    def _decide(self, tmp: Path, args: str) -> str:
        return _run_ps(tmp, _extract_named_function(self._F) + f'\n$d = {self._F} {args}\nWrite-Output "RESULT=$d"\n')

    def test_happy_path_proceeds(self, tmp_path: Path) -> None:
        assert self._decide(tmp_path, self._OK) == "proceed"

    def test_hyperv_unusable_blocks_before_any_stop(self, tmp_path: Path) -> None:
        """Hyper-V _cmdlets_ 打不开盘＝Optimize-VHD 必失败；必须拒绝而不是把 VM 停下来再失败（那才是真事故）。"""
        assert (
            self._decide(tmp_path, self._OK.replace("-HyperVUsable $true", "-HyperVUsable $false"))
            == "blocked_not_hyperv_usable"
        )

    def test_gate_is_a_capability_probe_not_a_token_claim(self) -> None:
        """闸必须量"能不能做到"，不能量"令牌上写着什么"。

        本账号在 BUILTIN\\Hyper-V Administrators 里而 IsInRole(Administrator)=False；
        若按提权裁，这条窗口在这台机器上永远打不开——假阻断也是缺陷。
        09-26 事故那次是在 RunLevel=Limited 的计划任务里真把 VM 停了并复制了 599 GiB，
        足证"未提权"不等于"做不到"。
        """
        text = _script_text()
        m = re.search(r"^if \(\$CompactWindow\) \{(?P<body>.*?)^\}\s*$", text, re.M | re.S)
        assert m, "-CompactWindow 分支结构漂移，本尺失去落点"
        branch = m.group("body")
        assert "blocked_not_admin" not in text, "仍在用 Administrator 令牌声明裁停机=假阻断"
        assert "Get-VHD" in branch, "前置闸未实探 Hyper-V 能力（只看了声明）"
        assert "$hvUsable" in branch, "探测结果未接入判定"

    def test_active_lane_blocks(self, tmp_path: Path) -> None:
        """还有别的会话在跑＝CH 可能正在被写，停机即打断别人施工。"""
        assert (
            self._decide(tmp_path, self._OK.replace("-ActiveSessions 0", "-ActiveSessions 1")) == "blocked_lanes_active"
        )

    def test_unreadable_session_count_blocks(self, tmp_path: Path) -> None:
        """会话计数读不到（-1）不得当成 0 放行——未知＝不安全，与 09-26 同型病根。"""
        assert (
            self._decide(tmp_path, self._OK.replace("-ActiveSessions 0", "-ActiveSessions -1"))
            == "blocked_sessions_unreadable"
        )

    def test_stale_backup_blocks(self, tmp_path: Path) -> None:
        assert (
            self._decide(tmp_path, self._OK.replace("-BackupFresh $true", "-BackupFresh $false"))
            == "blocked_backup_stale"
        )

    def test_image_home_without_room_blocks(self, tmp_path: Path) -> None:
        assert self._decide(tmp_path, self._OK.replace("-ImageFreeGB 900", "-ImageFreeGB 100")) == "blocked_image_space"

    def test_vm_missing_blocks(self, tmp_path: Path) -> None:
        assert self._decide(tmp_path, self._OK.replace("-VmFound $true", "-VmFound $false")) == "blocked_vm_missing"

    def test_wired_into_compactwindow_branch_and_exits_loudly(self) -> None:
        """防装饰件：前置闸必须在 -CompactWindow 分支被调用且拒绝即 exit，不得往下落到停机。"""
        text = _script_text()
        m = re.search(r"^if \(\$CompactWindow\) \{(?P<body>.*?)^\}\s*$", text, re.M | re.S)
        assert m, "-CompactWindow 分支结构漂移，本尺失去落点"
        branch = m.group("body")
        assert "Get-CompactionPrereqDecision" in branch, "前置闸未接入=摆设"
        i_call = branch.find("Get-CompactionPrereqDecision")
        i_exit = branch.find("exit 6", i_call)
        i_force = branch.find("$Force = $true", i_call)
        assert i_exit > i_call, "拒绝分支未以非零退出报警"
        assert i_exit < i_force, "拒绝后仍可置 Force=停机路径未被闸住"

    def test_compaction_cannot_leak_into_plain_backup(self) -> None:
        """DoCompact 只能由 -CompactWindow 置真：weekly/手动全量备份绝不许夹带停机压缩。"""
        text = _script_text()
        assert text.count("DoCompact = $true") == 1, "置位点不止一处=普通备份可能夹带压缩"
        m = re.search(r"^if \(\$CompactWindow\) \{(?P<body>.*?)^\}\s*$", text, re.M | re.S)
        assert m and "DoCompact = $true" in m.group("body"), "唯一置位点不在 -CompactWindow 分支内"


class TestOrderedWindowSafety:
    """顺序即安全：刷新→验长→压缩→开机→健康探针→回写→最后才退役旧副本。"""

    def test_verify_image_precedes_optimize(self) -> None:
        """Optimize-VHD 之前必须有"新镜像存在 + 字节不短于源"两道验长，任一不过先开机再 exit 7。"""
        text = _script_text()
        i_short = text.find("copy is short, aborting before any shrink")
        i_nofile = text.find("Refusing to compact: no freshly copied image")
        i_opt = text.find("Optimize-VHD -Path $dataVhdx -Mode Full")
        assert i_short > 0 and i_nofile > 0, "缺镜像存在/字节长度双验"
        assert i_opt > 0, "Optimize-VHD 未接入"
        assert i_nofile < i_short < i_opt, "验长未排在压缩之前=可能压缩一个不完整的档"
        assert text.count("exit 7") >= 2, "拒绝分支未以非零退出报警"
        assert "Start-VM" in text[i_nofile:i_opt], "拒绝时未先把 VM 开回去（会把停机窗口拖长）"

    def test_vm_is_off_during_compaction_and_back_on_after(self) -> None:
        """压缩必须在停机段内、Step 4 开机之前；否则 Optimize-VHD 直接失败。"""
        text = _script_text()
        i_stop = text.find("Stop-VM -Name $VmName")
        i_opt = text.find("Optimize-VHD -Path $dataVhdx -Mode Full")
        i_start = text.find('Write-Stage "Step 4: Starting VM')
        assert -1 < i_stop < i_opt < i_start, "停机→压缩→开机 次序漂移"

    def test_retire_predicate_only_retires_with_a_verified_successor(self, tmp_path: Path) -> None:
        """Owner 令"先定刷新、再删副本"：删旧的唯一许可=G 侧已有一份不短于旧档且不比旧档更老。"""
        f = "Get-RetireDecision"
        base = "-StaleExists $true -FreshExists $true -StaleGB 599 -FreshGB 599 -StaleAgeDays 30 -FreshAgeDays 0"
        assert self._retire(tmp_path, f, base) == "retire"
        assert (
            self._retire(tmp_path, f, base.replace("-FreshExists $true", "-FreshExists $false"))
            == "skipped_no_fresh_image"
        )
        assert (
            self._retire(tmp_path, f, base.replace("-StaleExists $true", "-StaleExists $false")) == "skipped_no_stale"
        )
        assert self._retire(tmp_path, f, base.replace("-FreshGB 599", "-FreshGB 120")) == "skipped_fresh_smaller"
        assert self._retire(tmp_path, f, base.replace("-FreshAgeDays 0", "-FreshAgeDays 90")) == "skipped_fresh_older"

    def _retire(self, tmp: Path, fname: str, args: str) -> str:
        return _run_ps(tmp, _extract_named_function(fname) + f'\n$d = {fname} {args}\nWrite-Output "RESULT=$d"\n')

    def test_retire_is_last_and_never_bare_delete(self) -> None:
        """退役段必须排在压缩与开机之后，且走回收站（InvokeVerb），禁 Remove-Item。"""
        text = _script_text()
        i_retire = text.find("Get-RetireDecision -StaleExists")
        i_opt = text.find("Optimize-VHD -Path $dataVhdx -Mode Full")
        i_start = text.find('Write-Stage "Step 4: Starting VM')
        assert i_retire > 0, "退役判定未接入=旧副本永不清理，F 盘红线继续被占"
        assert i_start < i_retire and i_opt < i_retire, "退役排在压缩/开机之前＝灾备真空窗口"
        assert 'InvokeVerb("delete")' in text[i_retire:], "退役未走回收站"
        assert "Remove-Item" not in text[i_retire:], "退役段出现裸删命令"

    def test_data_image_home_matches_restore_reader(self) -> None:
        """写侧镜像家必须等于 restore.ps1 的读取家，否则备份"成功"而灾备取不到。"""
        text = _script_text()
        m = re.search(r'^\$ImageHome\s*=\s*"([^"]+)"', text, re.M)
        assert m, "$ImageHome 未以常量形式声明"
        writer = m.group(1).rstrip("\\").lower()
        rt = (REPO_ROOT / "scripts" / "backup" / "restore.ps1").read_text(encoding="utf-8")
        m2 = re.search(r'^\$ChVmImageHome\s*=\s*"([^"]+)"', rt, re.M)
        assert m2, "restore.ps1 已不再声明 $ChVmImageHome＝读侧改名，须同步本尺"
        reader = m2.group(1).rstrip("\\").lower()
        assert writer == reader, f"写家 {writer} != 读家 {reader}"
        assert "\\ch_vm_backup" in reader and not reader.startswith("f:"), reader

    def test_success_formula_includes_compaction(self) -> None:
        """整体 success 必须纳入压缩结果：压缩失败仍报全绿＝假绿。"""
        m = re.search(r"^\s*success = .*$", _script_text(), re.M)
        assert m, "success 判定式未找到"
        assert "compact" in m.group(0), "success 未纳入压缩结果=压缩失败仍报全绿"


def _compact_block() -> str:
    """取含 Optimize-VHD 的那段 DoCompact 正文（供行为考试真跑）。"""
    text = _script_text()
    for m in re.finditer(r"^if \(\$script:DoCompact\) \{(?P<body>.*?)^\}\s*$", text, re.M | re.S):
        if "Optimize-VHD" in m.group("body"):
            return m.group("body")
    pytest.fail("含 Optimize-VHD 的 DoCompact 段不见了（压缩步骤被摘出=整套顺序护栏消失）")


@pytest.mark.skipif(sys.platform != "win32", reason="需要 PowerShell（Windows 宿主）")
class TestCompactionFailurePaths:
    """行为考试（不是 grep）：把三种坏前提真喂给压缩段，看它到底怎么走。

    grep 只能证明"字还在"，证不了"失败时会不会把 VM 落在关机态"。这里用假 cmdlet
    真跑那一段：Optimize-VHD 抛异常 / 镜像不存在 / 镜像字节不足。
    """

    def _run(self, tmp: Path, *, make_image: bool, img_len: int, src_len: int, optimize_body: str) -> tuple[int, str]:
        img_dir = tmp / "IMG"
        vm_dir = tmp / "VM"
        img_dir.mkdir(parents=True, exist_ok=True)
        vm_dir.mkdir(parents=True, exist_ok=True)
        (vm_dir / "data.vhdx").write_bytes(b"src")
        if make_image:
            (img_dir / "data.vhdx").write_bytes(b"img")
        ps = tmp / "harness.ps1"
        ps.write_text(
            "$ErrorActionPreference='Continue'\n"
            f"$srcLen={src_len}\n$imgLen={img_len}\n"
            'function Write-Stage { param($m) Write-Host "STAGE:$m" }\n'
            'function Write-OK    { param($m) Write-Host "OK:$m" }\n'
            'function Write-Warn  { param($m) Write-Host "WARN:$m" }\n'
            'function Write-Err   { param($m) Write-Host "ERR:$m" }\n'
            'function Set-StateField { param($n,$v) Write-Host "STATE:$n=$v" }\n'
            "function Get-VHD { param([string]$Path) [pscustomobject]@{ FileSize = $srcLen } }\n"
            "function Start-VM { param([string]$Name) Write-Host 'STARTVM' }\n"
            "function Get-Item { param([string]$Path) if ($Path -like '*IMG*') { [pscustomobject]@{ Length = $imgLen } } else { [pscustomobject]@{ Length = $srcLen } } }\n"
            f"function Optimize-VHD {{ param([string]$Path,[string]$Mode) {optimize_body} }}\n"
            "$steps=@{};$VmName='zephyr-ch';$ImageHome='"
            + str(img_dir)
            + "';$dataVhdx='"
            + str(vm_dir / "data.vhdx")
            + "'\n"
            "$script:DoCompact=$true\n" + _compact_block() + "\nWrite-Host 'END-REACHED'\n",
            encoding="ascii",
        )
        r = subprocess.run(  # noqa: bare-subprocess  同族：ps1 行为只能真跑 PowerShell 来裁
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        return r.returncode, r.stdout

    def test_access_denied_still_boots_the_vm(self, tmp_path: Path) -> None:
        """权限被拒：不得中断脚本（中断＝VM 留在关机态），状态须标 failed 并提示提权重跑。

        本例只喂压缩段那一段，"开回 VM"由紧随其后的 Step 4 承担——那条次序由
        test_vm_is_off_during_compaction_and_back_on_after 锁；这里锁的是
        "失败段自己不抢跑 exit"，那才是把停机窗口拖成事故的地方。
        """
        rc, out = self._run(
            tmp_path,
            make_image=True,
            img_len=500,
            src_len=500,
            optimize_body="throw [System.UnauthorizedAccessException]'Access to the virtual hard disk was denied'",
        )
        assert rc == 0, f"失败路径中断了脚本（VM 会留在关机态）：rc={rc}\n{out}"
        assert "END-REACHED" in out, "压缩失败后未继续走到 Step 4"
        assert "last_vhdx_compaction_result=failed" in out, f"失败未回写状态：{out}"
        assert "elevated" in out, "未提示这是权限性拒绝、该提权重跑"

    def test_missing_image_refuses_and_boots_vm_before_exit(self, tmp_path: Path) -> None:
        """镜像不存在：必须先开 VM 再以非零码退出，绝不允许"没验过档也压缩"。"""
        rc, out = self._run(
            tmp_path,
            make_image=False,
            img_len=0,
            src_len=500,
            optimize_body="Write-Host 'OPTIMIZE-RAN'",
        )
        assert "OPTIMIZE-RAN" not in out, "无镜像仍执行了压缩"
        assert "STARTVM" in out, "拒绝时未开回 VM"
        assert rc == 7, f"拒绝未以 exit 7 报警：rc={rc}\n{out}"
        assert "END-REACHED" not in out

    def test_short_image_refuses_and_boots_vm_before_exit(self, tmp_path: Path) -> None:
        """镜像字节短于源（robocopy 半截）：同样必须拒压+开回 VM，防"压一个不完整的档"。"""
        rc, out = self._run(
            tmp_path,
            make_image=True,
            img_len=100,
            src_len=500,
            optimize_body="Write-Host 'OPTIMIZE-RAN'",
        )
        assert "OPTIMIZE-RAN" not in out, "短镜像仍执行了压缩"
        assert "STARTVM" in out, "拒绝时未开回 VM"
        assert rc == 7, f"拒绝未以 exit 7 报警：rc={rc}\n{out}"

    def test_happy_path_compacts_once_and_writes_state(self, tmp_path: Path) -> None:
        """正例：镜像齐长→压缩调用恰一次+回写 ok+reclaimed 记账（防"只喊不压"）。"""
        rc, out = self._run(
            tmp_path,
            make_image=True,
            img_len=500,
            src_len=500,
            optimize_body="Write-Host 'OPTIMIZE-RAN'",
        )
        assert rc == 0 and "END-REACHED" in out, f"正例被拦：rc={rc}\n{out}"
        assert out.count("OPTIMIZE-RAN") == 1, "Optimize-VHD 调用次数不为 1"
        assert "last_vhdx_compaction_result=ok" in out, f"正例未回写 ok：{out}"

    def test_boot_and_config_stay_on_f_and_only_data_moves_to_g(self) -> None:
        """拆分口径：boot.vhdx+VM 配置留 F（快速恢复），只有 data.vhdx 走 G。

        断在 robocopy 调用行本身，不断"文件里提到过 boot.vhdx"——前者才证分流，
        后者连 $bootVhdx 赋值行都能满足（第一版本尺就因此选错落点）。
        """
        text = _script_text()
        mb = re.search(r"robocopy\s+\$VmRoot\s+(\$\w+)\s+`?" + re.escape('"boot.vhdx"'), text)
        md = re.search(r"robocopy\s+\$VmRoot\s+(\$\w+)\s+`?" + re.escape('"data.vhdx"'), text)
        assert mb, "boot.vhdx 的 robocopy 目标未成一行＝本尺失去落点，请同步修正"
        assert md, "data.vhdx 的 robocopy 目标未成一行＝本尺失去落点，请同步修正"
        assert mb.group(1) == "$BackupRoot", f"boot.vhdx 未留在配置级家：{mb.group(1)}"
        assert md.group(1) == "$ImageHome", f"data.vhdx 未归档到镜像家：{md.group(1)}"
