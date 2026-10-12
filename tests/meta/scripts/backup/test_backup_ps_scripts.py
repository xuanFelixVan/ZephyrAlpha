# tests/scripts/backup/test_backup_ps_scripts.py
"""PowerShell 备份脚本 smoke test——语法解析 + 关键参数契约（#ARCH-BACKUP-PS-SMOKE，2026-08-13）。

病根：backup.ps1 的 `-Encoding UTF8`（大写）在 PS5 下 ValidateSet 校验失败，存在 N 天未被发现——
PowerShell 脚本不在任何测试/门禁射程内，只在真实备份时才暴露。

治本：用 .NET PS 引擎（Parser.ParseFile）对 scripts/backup 下全部 .ps1 做语法解析冒烟，
并校验关键参数契约（-Mode ValidateSet、-Encoding 不得为大写 UTF8）。纳入 pytest，不加新 gate。

运行前提：Windows + powershell.exe 可用（非 Windows 环境自动 skip）。
"""

from __future__ import annotations

import re
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


# ==================== 2026-10-12 统筹工单⑧：备份轮转腿改造三判据 ====================


def _ps_code_lines(text: str) -> list[str]:
    """语句位扫描：剔除整行注释与空行。

    为什么必须这样量：修因说明里会**合法地**提到被禁形态（如 Remove-Item -Recurse），
    拿全文 grep 当判据会把说明文本读成违规；而只看语句位又会让"被包进注释的修复"
    蒙混过关——所以两处并用：结构测走语句位，行为测真跑函数。
    """
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]


def _first_idx(lines: list[str], needle: str) -> int:
    for idx, ln in enumerate(lines):
        if needle in ln:
            return idx
    return -1


def test_dumps_copy_leg_runs_before_the_slow_rotation_delete() -> None:
    """工单⑧第1项（最高优先＝数据安全）：当日 DB dumps 必须先落备份盘，再删旧快照。

    病形实测（2026-10-12 那发 duration_seconds=27844.9）：PG/SQLite dump 于 01:07:04 产出，
    而 "DB dumps snapshot done: G:/backup/db_dumps/20261012" 打在 08:43:51——中间隔着一轮
    6h42m44s 的 vault 轮转删除（02:00:50 → 08:43:34），当日数据库备份单份裸奔 7h36m。
    """
    src = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    lines = _ps_code_lines(src)
    i_copy = _first_idx(lines, "& robocopy $DumpDir")
    i_done = _first_idx(lines, "DB dumps snapshot done")
    i_rot = _first_idx(lines, "Rotation start: about to remove")
    assert min(i_copy, i_done, i_rot) >= 0, (
        f"锚语句没找到（被改名或掉进注释）：copy={i_copy} done={i_done} rotation_start={i_rot}"
    )
    assert i_copy < i_rot and i_done < i_rot, (
        f"腿序回退：dumps 拷贝在 {i_copy}/{i_done}，轮转删除在 {i_rot}（必须更小）"
    )


def test_rotation_and_space_guard_legs_announce_before_deleting() -> None:
    """工单⑧第2项（＝候裁㉘ 落地）：长删除腿必须"开局打一行"，否则小时级零输出与挂死同形。

    01:06 那发的日志形状：02:00:50 打完 Snapshot 行后整整 6h42m 零行，直到 08:43:34 才出现
    "Rotation: removed 1 old snapshot(s)"——观测面上与进程死掉无法区分。
    """
    src = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    lines = _ps_code_lines(src)
    i_rot = _first_idx(lines, "Rotation start: about to remove")
    i_evict = _first_idx(lines, "Space guard start: about to evict")
    assert i_rot >= 0, "轮转腿没有起始日志语句（又退回只打收官行的形状）"
    assert i_evict >= 0, "空间闸逐出腿没有起始日志语句（同形病，删的也是整日树）"
    i_del = next((j for j in range(i_rot, len(lines)) if "Remove-DatedTree $d.FullName" in lines[j]), -1)
    assert i_del > i_rot, "起始日志没排在轮转删除动作之前（打了等于没打）"


def test_dated_tree_deletes_use_native_helper_defined_before_first_call() -> None:
    """工单⑧第3项：整日快照树的删除改走原生单程递归，且函数必须先定义后调用。

    两条各对应一场在册病：①provider 递归删在整日树上实测 6h42m（PS 引擎逐件开销）；
    ②"定义晚于首次调用"是本链的 P0 形态（Test-CapacityGuardBreach 曾定义在 :963 而首调在
    :825，EAP=Continue 下整个 if/else 被静默跳过，dumps 腿空转两天）。
    """
    src = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    lines = _ps_code_lines(src)
    offenders = [ln for ln in lines if "Remove-Item" in ln and "-Recurse" in ln]
    assert not offenders, f"仍有 provider 整树递归删的语句位：{offenders[:3]}"
    i_def = _first_idx(lines, "function Remove-DatedTree")
    assert i_def >= 0, "Remove-DatedTree 没定义"
    calls = [j for j, ln in enumerate(lines) if "Remove-DatedTree " in ln and not ln.startswith("function")]
    assert len(calls) >= 3, f"调用面不足：实测 {len(calls)} 处，应覆盖 vault 轮转／空间闸逐出／dumps 轮转三处"
    late = [c for c in calls if c < i_def]
    assert not late, f"首次调用 {late[:3]} 早于定义 {i_def}（E-4 同族静默空转病复发）"


def test_remove_dated_tree_actually_deletes_a_nested_tree(tmp_path) -> None:
    """行为红绿证：把真函数搬进 harness，对含只读文件与空目录的嵌套树实测删干净。

    提速改动不能只测"语句位像不像"：rotated 计数由调用方按 Test-Path 复核后才累加，
    所以这里同时验返回值与"树真的没了"，并带一个只读件（两条删除路径都得吃下只读属性）。
    """
    src = (BACKUP_DIR / "backup.ps1").read_text(encoding="utf-8")
    fn = _extract_ps_function(src, "Remove-DatedTree")
    root = tmp_path / "20260927"
    (root / "a" / "b").mkdir(parents=True)
    (root / "a" / "empty").mkdir()
    (root / "f0.txt").write_text("x", encoding="ascii")
    deep = root / "a" / "b" / "f1.txt"
    deep.write_text("y" * 64, encoding="ascii")
    deep.chmod(0o444)
    assert root.exists() and any(root.rglob("*")), "测试自设的树没建起来，本测无判别力"
    harness = tmp_path / "del_harness.ps1"
    body = (
        "function Write-Warn($m){ Write-Output ('WARN ' + $m) }\n"
        + fn
        + "\n$t='"
        + root.as_posix().replace("/", "\\")
        + "'\n$r=Remove-DatedTree $t\n"
        + "Write-Output ('RET=' + $r)\n"
        + "Write-Output ('STILL=' + (Test-Path -LiteralPath $t))\n"
    )
    harness.write_text(body, encoding="ascii")
    proc = _run_ps("& '" + harness.as_posix().replace("/", "\\") + "'")
    assert proc.returncode == 0, f"harness 没跑通: {proc.stderr[:200]}"
    out = proc.stdout
    assert "RET=True" in out, f"函数返回值不是 True: {out[:240]}"
    assert "STILL=False" in out, f"Test-Path 说树还在: {out[:240]}"
    assert not root.exists(), "树还在盘上（返回 True 却没删＝计数会虚报）"


def test_daily_task_time_limit_clears_the_worst_measured_run() -> None:
    """工单⑧第3项后半：注册脚本里的 ExecutionTimeLimit 必须容得下实测最长轮（7h44m）。

    病形：任务动作链是 wscript.exe -> launch_hidden.vbs -> backup.ps1，而该 vbs 用等待式
    启动（`sh.Run cmd, 0, True`，文内无任何超时/杀原语），所以整棵备份树都在任务时限里；
    旧值 PT4H < 2026-10-12 实测 27844.9s＝7h44m ⇒ 长跑半程会被硬停（AllowHardTerminate
    节点缺省＝true），留下"死 PID 持有 .runtime/backup.lock"的残锁＋截断的轮。
    本测钉住脚本真源值；活体任务面另由 Set-ScheduledTask 改（凭据见台账工单⑧段）。
    """
    src = (BACKUP_DIR / "backup_daily_trigger.ps1").read_text(encoding="utf-8")
    i = src.find("-ExecutionTimeLimit")
    assert i >= 0, "注册脚本里没有 -ExecutionTimeLimit 语句位（时限由谁定？须先查明再改判据）"
    match = re.search(r"-\s*Hours\s+(\d+)", src[i : i + 220])
    assert match, f"-ExecutionTimeLimit 之后 220 字符内找不到 New-TimeSpan -Hours N：{src[i : i + 220]!r}"
    hours = int(match.group(1))
    assert hours >= 12, f"时限 {hours}h 容不下实测最长轮 7.73h，会复现半程硬停"
    assert "-Hours 4" not in src, "旧值 4h 回退（会把长跑截断成残锁）"


def test_daily_trigger_action_carries_the_no_flash_launcher() -> None:
    """统筹裁定⑥：注册脚本的 Action 必须与活体任务同形（wscript + launch_hidden.vbs）。

    病形：无闪窗治本只存在于活体任务面（实测 EXEC=wscript.exe ARG="…launch_hidden.vbs
    …backup.ps1" -Mode all -Force），而脚本真源仍是 powershell.exe -File backup.ps1
    ⇒ 任何人重跑注册脚本，闪窗缺陷就**静默回归**（每次运行弹一个控制台窗），
    且回归后没有测试会红。副作用前置测量已在台账 ⑥ 段留痕：四条收割路径都够不到
    wscript/powershell，vbs 又是等待式启动（无早退父），故对齐不新增被杀面。
    """
    src = (BACKUP_DIR / "backup_daily_trigger.ps1").read_text(encoding="utf-8")
    code = "\n".join(_ps_code_lines(src))
    assert '-Execute "wscript.exe"' in code, "注册脚本 Action 不是无闪窗启动器（闪窗回归通道开着）"
    assert "launch_hidden.vbs" in code, "Action 没引用无闪窗启动器件本体"
    assert '-Execute "powershell.exe"' not in code, "旧 powershell 直启 Action 回退"
    assert "Test-Path $FlashFreeLauncher" in code, "启动器缺件没有前置拦截（会注册出一个坏任务）"
