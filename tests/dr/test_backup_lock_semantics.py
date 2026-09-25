# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §
# [MODULE] tests.dr.test_backup_lock_semantics
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/backup/backup.ps1 (regex-extracted Test-BackupLock body), git show (pre-fix blob)
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/dr/test_backup_lock_semantics.py
"""backup.ps1 Test-BackupLock 语义常驻尺（P-9 长期化，2026-09-26 车道 I）。

背景：2026-09-25 06:00 备份断链第一根因——backup.ps1 的 Test-BackupLock 只看
"锁龄 ≥4h" 就判上一轮已死并抢锁，而一轮完整备份本来就要跑几小时；06:00 轮跑到
4.04h 时被 post-commit 轮判为僵尸并抢锁，两轮同写同一当日快照目录，产出
code_backup=failed / failures=1。治本（入 HEAD 于 5aef239f7c）＝
**以锁内 PID 存活为第一判据**：活=一律让步；死=接管；PID 存在但锁内 START 与真实
进程启动时间差 >5 分钟判 PID 复用=接管；锁内容读不到才退回旧 4h 规则。
同一契约 python 侧早有常驻尺 tests/dr/test_backup_lock_stale.py
（backup_runtime_state._backup_lock），**ps1 侧一直缺**——夜班是用"正则从 ps1 抽
函数体 + powershell 实跑"临时证明的，脚本落在 .runtime/tmp/ 24h 后即灭。本文件把
那把尺长期化。

判别力（同时锁两态，否则本尺没有意义）：
- 修复版（工作区 scripts/backup/backup.ps1 抽出的真函数体 + HEAD 版本）六用例全绿；
- 旧 age-only 版（从 git 历史修复前 blob 抽出）必红——CASE1 返回 False
  （活锁被抢＝事故复现）、CASE2/CASE3 返回 True（僵尸锁/PID 复用被误让步）。

实现要点（夜班实测踩过的坑，勿改）：
1. 函数体用正则从 ps1 正文抽（不复制粘贴进本文件），抽不到即 fail——这本身就是
   "函数被改名/删除"的守卫。
2. 注入桩 Write-Warn 必须走 [Console]::Error.WriteLine：Write-Host 在 -File 重定向
   下会把 warn 混进 stdout，$r 变数组，返回值判读假绿。
3. 活锁持有者 PID 取本 pytest 进程 os.getpid()（必然存活，与同目录
   test_backup_lock_stale 同构）；锁内 START 由 powershell 侧
   (Get-Process -Id <pid>).StartTime 取真值——与被测函数同一个 API，无时钟口径漂移。
4. 时间判据全用 os.utime 设 mtime，零 sleep。
5. 只在 pytest tmp_path 里造锁文件；不删任何真实文件；绝不真跑 backup.ps1。

旧版实现的 git 证据（本文件不写死 HEAD~k，按"标记边界"自定位）：
- 修复提交 = 5aef239f7c「[B7 治本] 备份锁改 PID 探活＋stage_timeline 观测面」
  （git log --oneline -- scripts/backup/backup.ps1 可见）；
- 修复前正文 blob = a389773a4cc00eefd2527706369c896bc1bb1200
  = git show 5aef239f7c^:scripts/backup/backup.ps1
  = git show 47e9673e94:scripts/backup/backup.ps1（同一 blob，两处等价）；
- git 历史不可用时退内联 _LEGACY_TEST_BACKUP_LOCK_INLINE——它就是上述 blob 里
  `function Test-BackupLock {…}` 的逐字拷贝（age-only，无 Get-Process）。
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PS1_REL = "scripts/backup/backup.ps1"
_PS1_PATH = _REPO_ROOT / _PS1_REL

# 抽取锚：行首 `function Test-BackupLock {` 直到首个行首 `}`（ps1 里函数闭括号一律
# 顶格）。函数改名/删除/整段搬走都会导致抽不到 → fail 并给出原因。
_TEST_BACKUP_LOCK_RE = re.compile(r"(?ms)^function\s+Test-BackupLock\s*\{.*?^\}")

# 新实现（PID 存活第一判据）的结构标记——HEAD 正文里可见 "holder PID" 消息串。
_NEW_IMPL_MARKER = "holder PID"

# 旧实现（age-only）的 git 证据，见模块 docstring。
_LEGACY_BLOB_SHA = "a389773a4cc00eefd2527706369c896bc1bb1200"

_DEAD_PID = 999999  # 远大于 Windows PID 上限，几乎必然不存在（与 test_backup_lock_stale 同口径）

_LEGACY_TEST_BACKUP_LOCK_INLINE = """function Test-BackupLock {
    if (Test-Path $LockFile) {
        $lockAge = ((Get-Date) - (Get-Item $LockFile).LastWriteTime).TotalHours
        if ($lockAge -lt 4) {
            Write-Warn "Another backup is running (lock age $([math]::Round($lockAge,1))h < 4h). Exiting."
            return $true
        }
        Write-Warn "Stale lock found (age $([math]::Round($lockAge,1))h >= 4h). Proceeding."
    }
    return $false
}"""


# --------------------------------------------------------------------------- #
# powershell 执行底座
# --------------------------------------------------------------------------- #
def _run_powershell(script_text: str, work_dir: Path, name: str) -> tuple[str, str, int]:
    """脚本落 work_dir 后以 powershell -File 实跑，返回 (stdout, stderr, returncode)。

    临时 .ps1 一律纯 ASCII——PowerShell 5.1 无 BOM 按 GBK 解码，中文注释会变成假语法错误。
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    script_path = work_dir / f"{name}.ps1"
    script_path.write_text(script_text, encoding="ascii")
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )
    return proc.stdout, proc.stderr, proc.returncode


def _ps_single_quote(value: str) -> str:
    return value.replace("'", "''")


def _harness_script(function_body: str, lock_file: Path) -> str:
    """注入 $LockFile + Write-Warn 桩（走 stderr，不污染返回值）+ 从 ps1 抽出的真函数体。"""
    return (
        "$ErrorActionPreference = 'Stop'\n"
        f"$LockFile = '{_ps_single_quote(str(lock_file))}'\n"
        "function Write-Warn($msg) { [Console]::Error.WriteLine('[WARN] ' + $msg) }\n"
        f"{function_body}\n"
        "$r = Test-BackupLock\n"
        'Write-Output ("RESULT=" + [string]$r)\n'
    )


def _call_test_backup_lock(function_body: str, lock_file: Path, work_dir: Path, case_id: str) -> tuple[bool, str]:
    """实跑一次 Test-BackupLock，返回 (blocked, stderr)。

    blocked=True ⇔ ps1 里 `if (Test-BackupLock) { …exit 0 }` 会让步；False=接管继续。
    stdout 判读从严：非"恰好一行 RESULT=True/False"一律 fail——桩污染 stdout 或函数
    输出泄漏都会让 $r 变数组，那是夜班实测过的假绿来源。
    """
    stdout, stderr, returncode = _run_powershell(
        _harness_script(function_body, lock_file), work_dir, f"harness_{case_id}"
    )
    if returncode != 0:
        raise AssertionError(
            f"[{case_id}] powershell harness 退出码 {returncode}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}"
        )
    result_lines = [line for line in stdout.splitlines() if line.startswith("RESULT=")]
    if len(result_lines) != 1:
        raise AssertionError(
            f"[{case_id}] 期望恰好一行 RESULT=，实得 {result_lines!r}（stdout={stdout!r}）"
            "——Test-BackupLock 输出泄漏或 Write-Warn 桩污染 stdout"
        )
    payload = result_lines[0][len("RESULT=") :].strip()
    if payload == "True":
        return True, stderr
    if payload == "False":
        return False, stderr
    raise AssertionError(
        f"[{case_id}] RESULT 载荷非单一布尔：{payload!r}——返回值被数组污染"
        "（Write-Warn 桩必须走 [Console]::Error.WriteLine，勿改回 Write-Host）"
    )


# --------------------------------------------------------------------------- #
# 锁文件构造（mtime 一律 os.utime，零 sleep）
# --------------------------------------------------------------------------- #
def _write_lock(lock_file: Path, content: str | None, age_minutes: float) -> None:
    """按规格造锁文件；content=None 表示"锁文件不存在"。全程只在 tmp 里写，不删任何东西。"""
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        assert not lock_file.exists(), f"前置不成立：{lock_file} 不该存在"
        return
    lock_file.write_text(content, encoding="ascii", newline="\n")
    aged_epoch = datetime.now(UTC).timestamp() - age_minutes * 60.0
    os.utime(lock_file, (aged_epoch, aged_epoch))


def _lock_content(pid: int, start_iso: str) -> str:
    """与 backup.ps1 的 Acquire-Lock 同格式：`PID:<n> START:<iso>`。"""
    return f"PID:{pid} START:{start_iso}"


@pytest.fixture(scope="module")
def alive_holder(tmp_path_factory: pytest.TempPathFactory) -> tuple[int, str]:
    """(必然存活的 PID, 该进程的真实启动时间 ISO)。

    PID 取本 pytest 进程（与同目录 test_backup_lock_stale 的活锁用例同构）；真实
    StartTime 由 powershell 侧 Get-Process 读出——被测函数比的正是这个属性。
    """
    pid = os.getpid()
    stdout, stderr, returncode = _run_powershell(
        f"Write-Output (Get-Process -Id {pid}).StartTime.ToString('o')\n",
        tmp_path_factory.mktemp("ps_start_probe"),
        "start_probe",
    )
    if returncode != 0 or not stdout.strip():
        raise AssertionError(f"读不到 PID {pid} 的 StartTime（rc={returncode}）：{stderr}")
    start_iso = stdout.strip()
    # 自检：读回的时间须与当前时刻同数量级（远小于被测的 5 分钟复用判据 × N 倍安全）
    drift = abs((datetime.fromisoformat(start_iso) - datetime.now(UTC)).total_seconds())
    assert drift < 3 * 24 * 3600, f" StartTime 读回异常：{start_iso}（drift={drift}s）"
    return pid, start_iso


# --------------------------------------------------------------------------- #
# 被测实现抽取（工作区真源 / HEAD / 修复前旧版）
# --------------------------------------------------------------------------- #
def _extract_function(text: str, source_desc: str) -> str:
    match = _TEST_BACKUP_LOCK_RE.search(text)
    if match is None:
        raise AssertionError(
            f"在 {source_desc} 里抽不到 `function Test-BackupLock {{…}}`。\n"
            f"抽取锚（正则）：{_TEST_BACKUP_LOCK_RE.pattern!r}\n"
            "两种可能：(a) 函数被改名/删除/整段搬走——备份并发锁契约失去守卫，"
            "要改的请连本尺一起改；(b) 闭括号不再顶格（ps1 里函数 `}` 一律顶格，"
            "缩进风格变化会破锚）。"
        )
    return match.group(0)


def _read_working_tree_ps1() -> str:
    if not _PS1_PATH.exists():
        raise AssertionError(f"真源脚本不存在：{_PS1_PATH}")
    return _PS1_PATH.read_text(encoding="utf-8", errors="replace")


def _git_show(rev: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{rev}:{_PS1_REL}"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return proc.stdout if proc.returncode == 0 else None


def _git_rev_parse(rev: str) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", rev],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def _load_legacy_impl() -> tuple[str, str]:
    """取修复前 age-only 实现：按标记边界在 ps1 提交历史里自定位（不写死 HEAD~k）。

    沿 `git log -- scripts/backup/backup.ps1`（新→旧）逐版取正文，找到"带新实现
    标记的版"与"紧邻其前的无标记版"这一边界 → 后者即修复前正文。
    git 不可用时退内联逐字拷贝，证据串里如实标明。
    """
    proc = subprocess.run(
        ["git", "log", "--format=%H", "-n", "40", "--", _PS1_REL],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    commits = [c.strip() for c in proc.stdout.splitlines() if c.strip()] if proc.returncode == 0 else []
    texts: list[tuple[str, str]] = []
    for commit in commits:
        shown = _git_show(commit)
        if shown is None:
            continue
        texts.append((commit, shown))
        if len(texts) >= 2 and _NEW_IMPL_MARKER in texts[-2][1] and _NEW_IMPL_MARKER not in texts[-1][1]:
            pre_fix_commit, pre_fix_text = texts[-1]
            blob = _git_rev_parse(f"{pre_fix_commit}:{_PS1_REL}")
            body = _extract_function(pre_fix_text, f"git show {pre_fix_commit}:{_PS1_REL}")
            if "Get-Process" in body or _NEW_IMPL_MARKER in body:
                raise AssertionError(f"取到的『旧版』含探活逻辑，不是 age-only 实现：{pre_fix_commit}")
            return body, f"git show {pre_fix_commit}:{_PS1_REL} (blob {blob})"
    return _LEGACY_TEST_BACKUP_LOCK_INLINE, f"inline copy of blob {_LEGACY_BLOB_SHA} (git history walk unavailable)"


@pytest.fixture(scope="module")
def current_body() -> str:
    """工作区真源 ps1 的 Test-BackupLock（改名/删除/回退 age-only 都会在这里炸）。"""
    body = _extract_function(_read_working_tree_ps1(), f"工作区 {_PS1_REL}")
    if _NEW_IMPL_MARKER not in body:
        raise AssertionError(
            f"工作区 {_PS1_REL} 的 Test-BackupLock 不含新实现标记 {_NEW_IMPL_MARKER!r}——"
            "疑似回退成 age-only（2026-09-25 断链第一根因），PID 探活契约已失守"
        )
    return body


@pytest.fixture(scope="module")
def head_body() -> str:
    """HEAD 已入袋版本的 Test-BackupLock（持久态守卫，不受他车道在途编辑左右）。"""
    text = _git_show("HEAD")
    if text is None:
        pytest.skip(f"git show HEAD:{_PS1_REL} 不可用（非 git 环境）")
    body = _extract_function(text, f"git HEAD:{_PS1_REL}")
    if _NEW_IMPL_MARKER not in body:
        raise AssertionError(f"HEAD 版 Test-BackupLock 不含 {_NEW_IMPL_MARKER!r}——已回退成 age-only")
    return body


@pytest.fixture(scope="module")
def legacy_impl() -> tuple[str, str]:
    """(修复前 age-only 函数体, 来源证据串)。"""
    return _load_legacy_impl()


# --------------------------------------------------------------------------- #
# 用例矩阵（同一份规格分别喂给三种实现）
# --------------------------------------------------------------------------- #
# 每案：id / 锁内容（None=无锁文件）/ 锁 mtime 龄（分钟）/ 修复版期望 / 旧 age-only 期望
# 期望 blocked：True=让步（ps1 exit 0），False=接管。
def _cases(alive_pid: int, real_start_iso: str) -> list[dict[str, object]]:
    now_iso = datetime.now(UTC).astimezone().isoformat(timespec="microseconds")
    recycled_iso = (datetime.fromisoformat(real_start_iso) - timedelta(days=3)).isoformat(timespec="microseconds")
    corrupt = "runn0f238f no pid marker here"
    return [
        {
            "id": "CASE1_live_holder_5h_old",
            # 09-25 06:00 轮实况：持有进程仍活着，锁龄早已越过 4h。旧规则在这里抢锁＝断链事故。
            "content": _lock_content(alive_pid, real_start_iso),
            "age_min": 300.0,
            "new": True,  # 活锁 → 一律让步
            "legacy": False,  # 红证：旧逻辑判"僵尸"并抢锁
        },
        {
            "id": "CASE2_dead_holder_young",
            "content": _lock_content(_DEAD_PID, now_iso),
            "age_min": 10.0,
            "new": False,  # 持有 PID 已死 → 接管（僵尸锁不再永挡门）
            "legacy": True,  # 红证：旧逻辑只看到 10min 就让步
        },
        {
            "id": "CASE3_recycled_pid_young",
            "content": _lock_content(alive_pid, recycled_iso),
            "age_min": 10.0,
            "new": False,  # PID 存活但锁内 START 比真实启动早 3 天 → PID 复用 → 接管
            "legacy": True,  # 红证：旧逻辑无从识别复用，直接让步
            "stderr_contains": "recycled",
        },
        {
            "id": "CASE4_no_lock_file",
            "content": None,
            "age_min": 0.0,
            "new": False,
            "legacy": False,  # 两态一致，不参与判别力断言
        },
        {
            "id": "CASE5a_corrupt_lock_5h",
            # 锁内容读不到 PID → 才退回旧 4h 规则；5h ≥ 4h → 接管
            "content": corrupt,
            "age_min": 300.0,
            "new": False,
            "legacy": False,
        },
        {
            "id": "CASE5b_corrupt_lock_10min",
            "content": corrupt,
            "age_min": 10.0,
            "new": True,  # 不可读且 <4h → 保守让步
            "legacy": True,
        },
    ]


def _run_case(function_body: str, case: dict[str, object], work_dir: Path) -> tuple[bool, str]:
    content = case["content"]
    lock_file = work_dir / "backup.lock"
    _write_lock(lock_file, None if content is None else str(content), float(str(case["age_min"])))
    return _call_test_backup_lock(function_body, lock_file, work_dir, str(case["id"]))


def _case(cases: dict[str, dict[str, object]], case_id: str) -> dict[str, object]:
    assert case_id in cases, f"用例 {case_id} 未定义"
    return cases[case_id]


_NEW_CASE_IDS = [
    "CASE1_live_holder_5h_old",
    "CASE2_dead_holder_young",
    "CASE3_recycled_pid_young",
    "CASE4_no_lock_file",
    "CASE5a_corrupt_lock_5h",
    "CASE5b_corrupt_lock_10min",
]


@pytest.mark.parametrize("case_id", _NEW_CASE_IDS)
def test_fixed_impl_contract_case(
    case_id: str,
    tmp_path: Path,
    alive_holder: tuple[int, str],
    current_body: str,
) -> None:
    """修复版（从工作区 backup.ps1 抽出的真函数体）六用例全绿——ps1 侧常驻契约尺。"""
    alive_pid, real_start_iso = alive_holder
    case = _case({c["id"]: c for c in _cases(alive_pid, real_start_iso)}, case_id)
    blocked, stderr = _run_case(current_body, case, tmp_path)
    assert blocked is case["new"], f"{case_id}：期望 blocked={case['new']}，实得 blocked={blocked}；stderr={stderr!r}"
    needle = case.get("stderr_contains")
    if needle is not None:
        assert str(needle) in stderr, f"{case_id}：应走 {needle!r} 分支，实际 stderr={stderr!r}"


@pytest.mark.parametrize("case_id", ["CASE1_live_holder_5h_old", "CASE2_dead_holder_young"])
def test_head_impl_contract_case(
    case_id: str,
    tmp_path: Path,
    alive_holder: tuple[int, str],
    head_body: str,
) -> None:
    """同一判据在 HEAD 已入袋版本上必须成立（事故核心两案：活锁让步、死锁接管）。"""
    alive_pid, real_start_iso = alive_holder
    case = _case({c["id"]: c for c in _cases(alive_pid, real_start_iso)}, case_id)
    blocked, stderr = _run_case(head_body, case, tmp_path)
    assert blocked is case["new"], f"HEAD 版 {case_id}：期望 {case['new']}，实得 {blocked}；stderr={stderr!r}"


def test_head_and_working_tree_agree_on_the_lock_contract(
    tmp_path: Path,
    alive_holder: tuple[int, str],
    head_body: str,
    current_body: str,
) -> None:
    """HEAD 与工作区的 Test-BackupLock 判据方向必须一致。

    不做逐字节相等断言——他车道可以改脚本别处；只锁"两态行为同向"这条底线。
    """
    alive_pid, real_start_iso = alive_holder
    cases = {c["id"]: c for c in _cases(alive_pid, real_start_iso)}
    for case_id in ("CASE1_live_holder_5h_old", "CASE2_dead_holder_young"):
        case = cases[case_id]
        blocked_head, _ = _run_case(head_body, case, tmp_path / case_id / "head")
        blocked_current, _ = _run_case(current_body, case, tmp_path / case_id / "current")
        assert blocked_head == blocked_current, (
            f"{case_id}：HEAD={blocked_head} 与工作区={blocked_current} 判据方向分叉"
        )


def test_legacy_age_only_impl_reproduces_the_incident(
    tmp_path: Path,
    alive_holder: tuple[int, str],
    legacy_impl: tuple[str, str],
) -> None:
    """红证：修复前 age-only 实现下 CASE1 必判"抢锁"（False）、CASE2/CASE3 必判"让步"（True）。

    这条断的是本尺的判别力——若旧逻辑也一样绿，说明两态无区分度，尺子是空的。
    """
    legacy_body, evidence = legacy_impl
    alive_pid, real_start_iso = alive_holder
    cases = {c["id"]: c for c in _cases(alive_pid, real_start_iso)}
    observed: dict[str, bool] = {}
    for case_id in ("CASE1_live_holder_5h_old", "CASE2_dead_holder_young", "CASE3_recycled_pid_young"):
        case = cases[case_id]
        blocked, stderr = _run_case(legacy_body, case, tmp_path / case_id)
        observed[case_id] = blocked
        assert blocked is case["legacy"], (
            f"旧 age-only 实现 {case_id}：期望 {case['legacy']}，实得 {blocked}"
            f"（旧版来源：{evidence}）；stderr={stderr!r}"
        )
    assert observed["CASE1_live_holder_5h_old"] is False, "旧逻辑竟也对活锁让步——本尺无判别力"
    assert observed["CASE2_dead_holder_young"] is True, "旧逻辑竟也对僵尸锁接管——本尺无判别力"


def test_legacy_impl_is_the_recorded_pre_fix_blob(legacy_impl: tuple[str, str]) -> None:
    """旧版来源核账：红证用的必须是 git 历史里那个 blob（或如实标注的内联抄件）。

    防"红证其实是随手编的旧实现"——它得真是 5aef239f7c 之前那份正文。
    """
    legacy_body, evidence = legacy_impl
    assert "Get-Process" not in legacy_body, f"旧版含进程探活，不是 age-only 实现：{evidence}"
    assert _NEW_IMPL_MARKER not in legacy_body, f"旧版含新实现标记：{evidence}"
    assert "-lt 4" in legacy_body, f"旧版缺 4h 龄判据（-lt 4），不是修复前正文：{evidence}"
    if evidence.startswith("git show "):
        assert _LEGACY_BLOB_SHA in evidence, (
            f"修复前正文 blob 与登记证据不符：{evidence}\n"
            f"登记值={_LEGACY_BLOB_SHA}（= git show 5aef239f7c^:{_PS1_REL}）——"
            "历史被改写时要一起更新本文件头注释与本常量"
        )
    else:
        assert legacy_body == _LEGACY_TEST_BACKUP_LOCK_INLINE, "内联兜底抄件与实际使用者不一致"
