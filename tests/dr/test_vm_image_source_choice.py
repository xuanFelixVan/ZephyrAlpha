# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.6/§dr-drill
# [MODULE] tests.dr.test_vm_image_source_choice
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts/backup/restore.ps1 (regex-extracted Get-VmImageChoice/Get-VmImageSrc + Do-Verify/Do-Vm 段正文)
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/dr/test_vm_image_source_choice.py
r"""restore.ps1 的 data.vhdx 取件裁决常驻尺（外审案卷 §210 治本，FMS 收尾班 2026-09-27）。

病灶（[亲验码] 修前）：`Do-Vm` 的取件逻辑是"F:\ch_vm_backup\data.vhdx 在就用它"，
而 `Do-Verify` 只看 G:\backup\ch_vm_backup。F 侧按 2026-09-24 裁定只放配置级件，
盘上那个 643,175,546,880 B（09-26 事故复活件）是残留而非权威档。两者一错开就是：
**演练报 ALL CHECKS PASSED，真恢复时回放的却是另一份从未被验过的镜像。**

判据取向：
1. 取件必由**同一条纯函数**裁决（verify 打印它、vm 执行它）；两处各写一遍
   if/else 正是本次事故的成因；
2. 两份并存且字节不等 ⇒ G 胜（F 是残留），并把冲突印出来；
3. 只有 F 有 ⇒ 允许回放但高声 WARN（灾备真空，须尽快重建 G）；
4. 两处都没有 ⇒ exit 1，不得静默降级。

函数体用正则从 ps1 抽（不复制粘贴进本文件），抽不到即 fail=改名/删除守卫。
同族先例：tests/dr/test_backup_mirror_deletion_cap.py、
tests/dr/test_backup_ch_vm_autocheck.py。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "backup" / "restore.ps1"

G_HOME = "G:\\backup\\ch_vm_backup"
F_HOME = "F:\\ch_vm_backup"
_NEEDS_PS = pytest.mark.skipif(sys.platform != "win32", reason="需要 PowerShell（Windows 宿主）")


def _script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _extract_function(name: str) -> str:
    text = _script_text()
    m = re.search(rf"^function {name}\s*\{{(?P<body>.*?)^\}}\s*$", text, re.M | re.S)
    if not m:
        pytest.fail(f"{name} 不在 {SCRIPT.name} 中（被改名/删除=取件裁决回退成两处各写一遍）")
    return f"function {name} {{{m.group('body')}\n}}"


def _decide(tmp: Path, fname: str, args: str) -> str:
    """跑一次判定函数，取 RESULT= 之后的原文（含空串——none 态的正确返回就是空）。"""
    ps = tmp / "case.ps1"
    ps.write_text(
        "$ErrorActionPreference='Stop'\n"
        + _extract_function(fname)
        + f"\n$d = {fname} {args}\n"
        + 'Write-Output "RESULT=$d"\n',
        encoding="ascii",
    )
    r = subprocess.run(  # noqa: bare-subprocess  ps1 语义只能真跑 PowerShell 来裁（同族先例）
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
    m = re.search(r"^RESULT=(.*)$", r.stdout, re.M)
    assert m, f"判定函数无返回值：{r.stdout}"
    return m.group(1).strip()


def _choice(tmp: Path, g_ok: bool, g_bytes: int, f_ok: bool, f_bytes: int) -> str:
    return _decide(
        tmp,
        "Get-VmImageChoice",
        f"-GExists {'$true' if g_ok else '$false'} -GBytes {g_bytes} "
        f"-FExists {'$true' if f_ok else '$false'} -FBytes {f_bytes}",
    )


@_NEEDS_PS
class TestImageChoiceAdjudication:
    """四态取件裁决：G 优先、冲突印出、无 G 降级告警、两处皆无不得静默。"""

    def test_g_archive_is_preferred(self, tmp_path: Path) -> None:
        assert _choice(tmp_path, True, 500_000, False, 0) == "g_archive"

    def test_dual_copy_equal_bytes_is_plain_g(self, tmp_path: Path) -> None:
        assert _choice(tmp_path, True, 500_000, True, 500_000) == "g_archive"

    def test_dual_copy_unequal_is_flagged_as_conflict(self, tmp_path: Path) -> None:
        """09-26 实况形态：F 上 643,175,546,880 B 残留 + G 上另一尺寸 ⇒ 必判冲突。"""
        assert _choice(tmp_path, True, 591_568_912_384, True, 643_175_546_880) == "g_conflict_remnant"

    def test_f_only_is_remnant(self, tmp_path: Path) -> None:
        assert _choice(tmp_path, False, 0, True, 599_000) == "f_remnant_only"

    def test_nothing_available(self, tmp_path: Path) -> None:
        assert _choice(tmp_path, False, 0, False, 0) == "none"

    def test_source_path_follows_the_choice(self, tmp_path: Path) -> None:
        """取件路径必须由裁决单点派生：冲突态即便 F 有文件也须指向 G。"""
        args = f"-ImageHome '{G_HOME}' -ConfigHome '{F_HOME}'"
        assert _decide(tmp_path, "Get-VmImageSrc", f"-Choice 'g_archive' {args}") == f"{G_HOME}\\data.vhdx"
        assert _decide(tmp_path, "Get-VmImageSrc", f"-Choice 'g_conflict_remnant' {args}") == f"{G_HOME}\\data.vhdx"
        assert _decide(tmp_path, "Get-VmImageSrc", f"-Choice 'f_remnant_only' {args}") == f"{F_HOME}\\data.vhdx"
        assert _decide(tmp_path, "Get-VmImageSrc", f"-Choice 'none' {args}") == ""


@_NEEDS_PS
class TestVerifyAndVmShareOneCaliber:
    """防"两处各写一遍"回退：verify 与 vm 必须都过同一把裁决函数。"""

    def _func_body(self, name: str) -> str:
        text = _script_text()
        m = re.search(rf"^function {name}\s*\{{(?P<body>.*?)^\}}\s*$", text, re.M | re.S)
        assert m, f"{name} 不见了"
        return m.group("body")

    def test_both_paths_call_the_adjudicator(self) -> None:
        ver = self._func_body("Do-Verify")
        vm = self._func_body("Do-Vm")
        assert "Get-VmImageChoice" in ver, "verify 未打印实际取件=演练仍可对未验过的档报 PASS"
        assert "Get-VmImageChoice" in vm, "vm 未走裁决=回退成裸判 F 是否存在"
        assert "Get-VmImageSrc" in ver and "Get-VmImageSrc" in vm, "取件路径未由裁决派生"

    def test_conflict_and_remnant_are_loudly_reported(self) -> None:
        ver = self._func_body("Do-Verify")
        assert "g_conflict_remnant" in ver, "冲突态未在 verify 出现"
        assert "Write-Warn" in ver, "冲突未高声告警"
        assert "f_remnant_only" in ver, "灾备真空态未告警"
        assert "data.vhdx missing in BOTH" in self._func_body("Do-Vm"), "两处皆无未硬失败"

    def test_vm_no_longer_uses_bare_f_presence(self) -> None:
        """旧形态 `if (-not (Test-Path $imgDst)) { copy from G }` 等于"F 有就直接用 F"。"""
        vm = self._func_body("Do-Vm")
        assert not re.search(r"if \(-not \(Test-Path \$imgDst\)\) \{", vm), "取件回退成裸判 F 存在"

    def test_script_is_pure_ascii(self) -> None:
        """.ps1 含非 ASCII 会被 PS5.1 按 GBK 解码出假语法错误（根宪法 §9.7）。"""
        bad = [i for i, b in enumerate(SCRIPT.read_bytes()) if b > 127]
        assert not bad, f"restore.ps1 非 ASCII 字节 {len(bad)} 个，首个偏移 {bad[:3]}"

    def test_script_parses_without_syntax_errors(self, tmp_path: Path) -> None:
        probe = tmp_path / "parse.ps1"
        probe.write_text(
            "$errs=$null\n$toks=$null\n"
            "[void][System.Management.Automation.Language.Parser]::ParseFile("
            "(Convert-Path '" + str(SCRIPT).replace("'", "''") + "'),[ref]$toks,[ref]$errs)\n"
            'Write-Output "PARSE_ERRORS=$($errs.Count)"\n'
            'foreach($e in $errs){ Write-Output "ERR_LINE=$($e.Extent.StartLineNumber)" }\n',
            encoding="ascii",
        )
        r = subprocess.run(  # noqa: bare-subprocess  同上：语法只能由 PowerShell 自己裁
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(probe)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        m = re.search(r"PARSE_ERRORS=(\d+)", r.stdout)
        assert m, f"解析器未回报错误数：{r.stdout}\n{r.stderr}"
        assert int(m.group(1)) == 0, f"restore.ps1 存在语法错：{r.stdout}"
