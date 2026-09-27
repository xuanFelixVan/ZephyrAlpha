# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.2/§3.6
# [MODULE] tests.dr.test_backup_mirror_deletion_cap
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/backup/backup.ps1 (regex-extracted mirror-guard fns + STAGE 3c/3d 正文), scripts/backup/backup_config.yaml (mirror_guard)
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/dr/test_backup_mirror_deletion_cap.py
"""backup.ps1 镜像删除传播护栏常驻尺（案 G 治本配套，FMS 收尾班 2026-09-27）。

背景（外审案卷 docs/_working/fms_overhaul/95_external_review/backup_cold_store_review.md
§案 G [亲验码]）：`backup.ps1` STAGE 3c/3d 对**唯一夜镜像**执行 `robocopy /MIR`，
而 2026-09-14 docs/_working 误删事故已经证明过同一条机制："镜像当晚连源一起毁掉最后
恢复源"（该教训写进了 backup_config.yaml v2.1.0 变更注与 backup.ps1 STAGE 3 头注）。
本册原先给 3d 的开脱是"源 immutable/版本化，/MIR 风险可控"——实测该前提已不成立：
F:\\zephyr_cold 里有每日改写住民（library_ledger_backup.py 滚动 30 天）+ 90_tmp + 人工
.bak，而读侧没有任何尺能区分"30 天到期"与"有人删了一批"，两种都长得像镜像成功。

判据取向（本尺存在的理由）：
1. **先数后删**——/MIR 之前必须先用 /L 探针数出"将被清除条目数"，超帽即降级为只增 /E；
2. **未知必降级**——探针失败/取不到数（-1）走 /E，绝不允许"没数出来就当没东西要删"；
   即"最坏结果=副本偏旧"，而不是"最坏结果=副本被清空"；
3. **取数信号不得依赖本机 locale**——robocopy 汇总行在本机是 GBK 的 "文件:"
   而非 "Files :"，按列名解析会永久返回未知、护栏静默失效（我第一版就写成这样，
   实测输出后改判）；
4. **护栏必须接在两个 /MIR 落点上**，只装一处等于另一处照旧裸删。

函数体用正则从 ps1 抽（不复制粘贴进本文件），抽不到即 fail——这本身就是"函数被改名/
删除"的守卫。同族先例：tests/dr/test_backup_ch_vm_autocheck.py、
tests/dr/test_backup_lock_semantics.py。真跑 robocopy 的用例只在 tmp_path 里操作，
不碰任何生产盘。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "backup" / "backup.ps1"
CONFIG = REPO_ROOT / "scripts" / "backup" / "backup_config.yaml"

_NEEDS_PS = pytest.mark.skipif(sys.platform != "win32", reason="需要 PowerShell/robocopy（Windows 宿主）")


def _script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _extract_function(name: str) -> str:
    text = _script_text()
    m = re.search(rf"^function {name}\s*\{{(?P<body>.*?)^\}}\s*$", text, re.M | re.S)
    if not m:
        pytest.fail(f"{name} 不在 {SCRIPT.name} 中（被改名/删除=镜像删除护栏回退）")
    return f"function {name} {{{m.group('body')}\n}}"


def _run_ps(tmp: Path, body: str, label: str = "case") -> subprocess.CompletedProcess[str]:
    ps = tmp / f"{label}.ps1"
    ps.write_text("$ErrorActionPreference='Continue'\n" + body + "\n", encoding="ascii")
    return subprocess.run(  # noqa: bare-subprocess  ps1 语义只能真跑 PowerShell 来裁（同族先例）
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


def _decide(tmp: Path, fname: str, args: str) -> str:
    r = _run_ps(tmp, _extract_function(fname) + f'\n$d = {fname} {args}\nWrite-Output "RESULT=$d"\n')
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
    m = re.search(r"RESULT=(\S+)", r.stdout)
    assert m, f"判定函数无返回值：{r.stdout}"
    return m.group(1).strip()


class TestPurgeCountSignal:
    """取数面：数的是 *EXTRA 行，不是本机 locale 下的汇总列名。"""

    @staticmethod
    def _count(tmp: Path, output: str, exit_code: int) -> str:
        body = _extract_function("Get-RobocopyPurgeCount") + (
            f"\n$out = @'\n{output}\n'@\n$d = Get-RobocopyPurgeCount -Output $out -ExitCode {exit_code}\n"
            'Write-Output "RESULT=$d"\n'
        )
        r = _run_ps(tmp, body)
        assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
        m = re.search(r"RESULT=(\S+)", r.stdout)
        assert m, r.stdout
        return m.group(1).strip()

    def test_counts_every_extra_line(self, tmp_path: Path) -> None:
        """5 条 *EXTRA 行 = 5 个待清除条目（本机 robocopy 输出行首带制表符与 GBK 标签）。"""
        out = "\n".join(f"\t  *EXTRA File   \t1\tC:\\t\\b{i}.txt" for i in range(5))
        assert self._count(tmp_path, out, 3) == "5"

    def test_probe_failure_is_unknown_not_zero(self, tmp_path: Path) -> None:
        """robocopy 探针自身失败（exit>=8）必须 -1=未知；返回 0 会让护栏当"没东西要删"。"""
        assert self._count(tmp_path, "*EXTRA File\tC:\\t\\x.txt", 16) == "-1"

    def test_clean_probe_reports_zero(self, tmp_path: Path) -> None:
        assert self._count(tmp_path, "", 0) == "0"

    def test_signal_is_locale_independent(self) -> None:
        """尺锁实现取向：不得按汇总区列名（Files/Extras）解析——本机是 GBK 标签。"""
        body = _extract_function("Get-RobocopyPurgeCount")
        assert not re.search(r"Files\s*:\\s*\(\.\+\)\$", body), "按英文列名解析=本机永不命中"
        assert 'StartsWith("*")' in body, "未使用 locale 无关的 *EXTRA 行信号"


class TestSyncModeDecision:
    """判据面：未知与超帽都降级为只增不删。"""

    def test_unknown_degrades_to_additive(self, tmp_path: Path) -> None:
        assert _decide(tmp_path, "Get-MirrorSyncMode", "-Extras -1 -Cap 200") == "additive_unproven"

    def test_over_cap_degrades_to_additive(self, tmp_path: Path) -> None:
        assert _decide(tmp_path, "Get-MirrorSyncMode", "-Extras 201 -Cap 200") == "additive_over_cap"

    def test_at_cap_still_mirrors(self, tmp_path: Path) -> None:
        assert _decide(tmp_path, "Get-MirrorSyncMode", "-Extras 200 -Cap 200") == "mirror"

    def test_zero_mirrors(self, tmp_path: Path) -> None:
        assert _decide(tmp_path, "Get-MirrorSyncMode", "-Extras 0 -Cap 200") == "mirror"


class TestCapConfigNeverMeansUnlimited:
    """配置面：读不到帽必须回退内置常量；显式 0 必须保持 0（=永不传播删除）。"""

    def test_config_value_wins(self, tmp_path: Path) -> None:
        yaml_text = "mirror_guard:\n  max_propagated_deletes: 37\n"
        body = _extract_function("Get-MirrorPurgeCap") + (
            f"\n$y = @'\n{yaml_text}\n'@\n$d = Get-MirrorPurgeCap -Yaml $y -Fallback 200\nWrite-Output \"RESULT=$d\"\n"
        )
        r = _run_ps(tmp_path, body)
        assert re.search(r"RESULT=37", r.stdout), f"{r.stdout}\n{r.stderr}"

    def test_missing_key_falls_back(self, tmp_path: Path) -> None:
        assert _decide(tmp_path, "Get-MirrorPurgeCap", "-Yaml 'code_backup:' -Fallback 200") == "200"

    def test_explicit_zero_is_not_replaced_by_fallback(self, tmp_path: Path) -> None:
        """`$x -or $fallback` 形态会把 0 吃成 200——本帽 0 的含义恰是"绝不传播删除"。"""
        yaml_text = "mirror_guard:\n  max_propagated_deletes: 0\n"
        body = _extract_function("Get-MirrorPurgeCap") + (
            f"\n$y = @'\n{yaml_text}\n'@\n$d = Get-MirrorPurgeCap -Yaml $y -Fallback 200\nWrite-Output \"RESULT=$d\"\n"
        )
        r = _run_ps(tmp_path, body)
        assert re.search(r"RESULT=0\s*$", r.stdout), f"显式 0 被兜底顶包：{r.stdout}\n{r.stderr}"

    def test_registered_cap_exists_in_config(self) -> None:
        import yaml

        cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        assert cfg["mirror_guard"]["max_propagated_deletes"] == 200, cfg.get("mirror_guard")


@_NEEDS_PS
class TestGuardedMirrorReallyRuns:
    """行为考试：真起 robocopy，只看 tmp_path，验"超帽不删 / 在帽才删 / 探不到数不删"。"""

    def _call(self, tmp: Path, src: Path, tgt: Path, cap: int) -> dict[str, str]:
        body = (
            _extract_function("Get-RobocopyPurgeCount")
            + _extract_function("Get-MirrorSyncMode")
            + _extract_function("Invoke-GuardedMirror")
            + f"\n$r = Invoke-GuardedMirror -Source '{src}' -Target '{tgt}' -Cap {cap}\n"
            + 'Write-Output "mode=$($r.mode)"\nWrite-Output "purge=$($r.would_purge)"\n'
            + 'Write-Output "exit=$($r.robocopy_exit)"\n'
        )
        r = _run_ps(tmp, body, label="guarded")
        assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
        return dict(re.findall(r"^(mode|purge|exit)=(\S+)$", r.stdout, re.M))

    @staticmethod
    def _trees(tmp: Path, src_files: int, extra_files: int) -> tuple[Path, Path]:
        src = tmp / "src"
        tgt = tmp / "tgt"
        src.mkdir(parents=True, exist_ok=True)
        tgt.mkdir(parents=True, exist_ok=True)
        for i in range(src_files):
            (src / f"a{i}.txt").write_text("keep", encoding="ascii")
            (tgt / f"a{i}.txt").write_text("keep", encoding="ascii")
        for i in range(extra_files):
            (tgt / f"stale{i}.txt").write_text("orphan", encoding="ascii")
        return src, tgt

    def test_under_cap_purges_the_stale_extras(self, tmp_path: Path) -> None:
        src, tgt = self._trees(tmp_path, 2, 3)
        got = self._call(tmp_path, src, tgt, cap=10)
        assert got["mode"] == "mirror", got
        assert got["purge"] == "3", got
        assert not list(tgt.glob("stale*.txt")), "在帽之内却没清除（=护栏反向失灵）"

    def test_over_cap_keeps_them_and_still_syncs_new_files(self, tmp_path: Path) -> None:
        src, tgt = self._trees(tmp_path, 2, 3)
        (src / "fresh.txt").write_text("new", encoding="ascii")
        got = self._call(tmp_path, src, tgt, cap=2)
        assert got["mode"] == "additive_over_cap", got
        assert len(list(tgt.glob("stale*.txt"))) == 3, "超帽仍清除了副本内容=最后恢复源被传播"
        assert (tgt / "fresh.txt").exists(), "降级为只增时漏掉了正常同步"

    def test_unprobeable_source_degrades_to_additive(self, tmp_path: Path) -> None:
        """探针失败=未知：必须走只增分支，绝不允许"当 0 处理"再 /MIR。

        生产面 STAGE 3c/3d 在调用前已 Test-Path 挡过源缺失，这里喂一个不存在的路径是
        为了构造"探针拿不到可解析输出"这一类失败（盘符漂移/目标不可读/瞬时 IO 错都同型）。
        """
        _src, tgt = self._trees(tmp_path, 1, 2)
        got = self._call(tmp_path, tmp_path / "gone", tgt, cap=5)
        assert got["mode"] == "additive_unproven", got
        assert got["purge"] == "-1", got
        assert len(list(tgt.glob("stale*.txt"))) == 2, "探针未知却执行了清除"


@_NEEDS_PS
class TestWiringAndScriptHealth:
    """防装饰件 + 脚本本体健康：两处 /MIR 落点都要过闸，且 backup.ps1 仍可解析、纯 ASCII。"""

    def _stage(self, header: str, nxt: str) -> str:
        text = _script_text()
        i = text.index(header)
        j = text.index(nxt, i)
        return text[i:j]

    def test_both_mirror_stages_go_through_the_guard(self) -> None:
        s3c = self._stage("# ==================== STAGE 3c", "# ==================== STAGE 3d")
        s3d = self._stage("# ==================== STAGE 3d", "# ==================== STAGE 4:")
        for label, seg in (("3c", s3c), ("3d", s3d)):
            assert "Invoke-GuardedMirror" in seg, f"STAGE {label} 未接护栏=该处照旧裸 /MIR"
            assert not re.search(r'robocopy[^|]*?"/MIR"', seg), f"STAGE {label} 仍有裸 /MIR 直调"

    def test_guard_reports_the_decision_where_a_human_can_see_it(self) -> None:
        text = _script_text()
        assert text.count('Write-Warn ("G-mirror') + text.count('Write-Warn ("Off-repo') >= 2, "降级未高声报告"
        assert "would_purge" in text, "判定数未入机读报告"

    def test_script_is_pure_ascii(self) -> None:
        """.ps1 含非 ASCII 会被 PS5.1 按 GBK 解码出假语法错误（根宪法 §9.7）。"""
        bad = [i for i, b in enumerate(SCRIPT.read_bytes()) if b > 127]
        assert not bad, f"backup.ps1 非 ASCII 字节 {len(bad)} 个，首个偏移 {bad[:3]}"

    def test_script_parses_without_syntax_errors(self, tmp_path: Path) -> None:
        probe = tmp_path / "parse.ps1"
        probe.write_text(
            "$errs=$null\n$toks=$null\n"
            "[void][System.Management.Automation.Language.Parser]::ParseFile("
            "(Convert-Path '" + str(SCRIPT).replace("'", "''") + "'),[ref]$toks,[ref]$errs)\n"
            'Write-Output "PARSE_ERRORS=$($errs.Count)"\n'
            'foreach($e in $errs){ Write-Output "ERR_LINE=$($e.Extent.StartLineNumber) MSG=$($e.Message)" }\n',
            encoding="ascii",
        )
        r = _run_ps(tmp_path, probe.read_text(encoding="ascii"), label="parse_probe")
        m = re.search(r"PARSE_ERRORS=(\d+)", r.stdout)
        assert m, f"解析器未回报错误数：{r.stdout}\n{r.stderr}"
        assert int(m.group(1)) == 0, f"backup.ps1 存在语法错：{r.stdout}"
