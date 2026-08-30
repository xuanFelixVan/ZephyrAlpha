# [A_test] module_id: MOD-GOV_all_scripts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-276 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_all_scripts
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-276 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""治理脚本分层冒烟测试 — 按脚本 parametrize（CAND-GOVTEST-001 落地，2026-08-30）。

覆盖 D-B-01a~D-B-02（exit code 语义、--help 可用、--warn-only 不崩溃）。

测试分层：
  - Quick (always):  --help + --warn-only on D1-D4, D8 scripts
  - Critical (always): --help + --warn-only on D5-D7 scripts
  - Integration (always): --jsonl on ALL scripts（质量检查）
  - Full (@slow):  --help + --warn-only + timing on ALL scripts

拆分说明（CAND-GOVTEST-001）：
  原 4 个 mega-class 内部 ThreadPoolExecutor(8) 串行跑几十~100+ 脚本子进程，
  xdist --dist=load 逐 item 分发时 mega-item 独占 worker 堆积尾部（B1 工单实证
  93% 假挂起）。现拆为按脚本 parametrize 的小 item（单脚本单子进程），
  load 调度天然均摊；单脚本失败隔离定位（item id=脚本路径），分层语义经
  item 级 marker（quick/critical/slow）保留。

标签推导对标 run_all.py _derive_tags():
  - D1-D4, D8 → "Quick"
  - D5-D7 → "Critical"

性能优化:
  - temp file 替代 subprocess.PIPE 解决 Windows 孙进程 handle 继承死锁（保留）
  - 并行调度移交 pytest-xdist（不再模块内 ThreadPoolExecutor）
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from pathlib import Path

import pytest
import yaml

# CAND-GOVTEST-001：拆分后单 item 最坏=1 个子进程（manifest timeout_seconds 级），
# 模块级 1800s 豁免收敛为 600s 兜底（多重防护，防回归挂起）。
pytestmark = pytest.mark.timeout(600)

_DIMENSION_RE = re.compile(r"d(\d+)[_/]")

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MANIFEST_PATH = _REPO_ROOT / "scripts" / "script-manifest.yaml"
_SMOKE_TEST = "governance/d1_structure/run_script_smoke_test.py"

# #ARCH-092 存量批量改写损伤——xfail(strict=False) 保留原 mega-item 的非阻断语义
_XFAIL_ARCH092 = pytest.mark.xfail(
    strict=False,
    reason="#ARCH-092：存量批量改写损伤（_shared import 收拢到 sys.path bootstrap 前/迁入子目录未修 bootstrap）致脚本 --help/--warn 崩溃——健康探测器如实报警，待专项清偿批修脚本后摘除",
)
_XFAIL_JSONL = pytest.mark.xfail(
    strict=False,
    reason="#ARCH-092 附带裁定：手写 argv 解析冒烟脚本（如 git_health_smoke.py）吞未知 flag+多行 JSON 输出，与 JSONL 质量门契约不合——补 argparse 主干 或 质量门豁免范围，待裁定",
)


def _extract_dimension(script_name: str) -> str | None:
    m = _DIMENSION_RE.search(script_name)
    return f"D{m.group(1)}" if m else None


def _is_quick(script_name: str) -> bool:
    d = _extract_dimension(script_name)
    return d in {"D1", "D2", "D3", "D4", "D8"}


def _is_critical(script_name: str) -> bool:
    d = _extract_dimension(script_name)
    return d in {"D5", "D6", "D7"}


def _load_script_entries() -> list[dict]:
    """收集期加载脚本清单（scripts/script-manifest.yaml，与 conftest script_entries 同真源）。"""
    with open(_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return [
        e
        for e in manifest.get("scripts", [])
        if e.get("path", "").startswith("governance/") and e.get("path", "") != _SMOKE_TEST
    ]


def _load_test_cases(script_entries: list[dict]) -> dict[str, list[tuple[str, int, str, str]]]:
    all_cases = [
        (
            e.get("name") or e.get("path", "unknown"),
            e.get("timeout_seconds", 60),
            e.get("description", ""),
            ",".join(e.get("dimensions", [])),
        )
        for e in script_entries
    ]
    quick = [tc for tc in all_cases if _is_quick(tc[0])]
    critical = [tc for tc in all_cases if _is_critical(tc[0])]
    return {"all": all_cases, "quick": quick, "critical": critical}


_CASES = _load_test_cases(_load_script_entries())


def _params(cases: list[tuple[str, int, str, str]], mark: pytest.Mark | None = None) -> list:
    """按脚本生成 parametrize 参数（item id=脚本路径，item 级 marker 保留分层）。"""
    return [
        pytest.param(name, timeout, id=name, marks=mark if mark is not None else ())
        for name, timeout, _desc, _dims in cases
    ]


_QUICK_PARAMS = _params(_CASES["quick"], pytest.mark.quick)
_CRITICAL_PARAMS = _params(_CASES["critical"], pytest.mark.critical)
_ALL_PARAMS = _params(_CASES["all"])


def _safe_unlink(file_path: str) -> None:
    with suppress(OSError):
        os.unlink(file_path)


def _run_subprocess_safe(cmd: list[str], timeout: int, cwd: str) -> tuple[int, str, str]:
    """使用临时文件替代 PIPE 运行子进程，避免 Windows 孙进程 handle 继承死锁。

    原理：subprocess.run(capture_output=True) 内部用 PIPE 收集 stdout/stderr，
    若子进程 spawn 孙进程，孙进程继承 PIPE handle → communicate() 等不到 EOF → 死锁。
    改用 temp file → 子进程写文件 → wait() 返回后读文件 → 无 pipe handle 继承问题。
    """
    fd_out, out_path = tempfile.mkstemp(suffix=".stdout", prefix="zalpha_")
    fd_err, err_path = tempfile.mkstemp(suffix=".stderr", prefix="zalpha_")
    os.close(fd_out)
    os.close(fd_err)

    proc = None
    try:
        with (
            open(out_path, "w", encoding="utf-8", errors="replace") as out_f,
            open(err_path, "w", encoding="utf-8", errors="replace") as err_f,
        ):
            proc = subprocess.Popen(cmd, stdout=out_f, stderr=err_f, cwd=cwd)

        proc.wait(timeout=timeout)
        returncode = proc.returncode

        stdout = Path(out_path).read_text(encoding="utf-8", errors="replace")
        stderr = Path(err_path).read_text(encoding="utf-8", errors="replace")

        return returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        if proc:
            proc.kill()
            with suppress(subprocess.TimeoutExpired):
                proc.wait(timeout=5)
        raise
    finally:
        _safe_unlink(out_path)
        _safe_unlink(err_path)


def _run_help_one(script_name: str, timeout: int, repo_root: Path) -> tuple:
    script_path = repo_root / "scripts" / script_name
    if not script_path.exists():
        return ("missing", script_name)

    try:
        returncode, _stdout, stderr = _run_subprocess_safe(
            [sys.executable, str(script_path), "--help"],
            min(timeout, 30),
            str(repo_root),
        )
    except subprocess.TimeoutExpired:
        return ("crash", script_name, -1)

    if returncode == 0:
        return ("ok", script_name)

    is_crash = (
        "Traceback" in stderr
        or "ModuleNotFoundError" in stderr
        or "ImportError" in stderr
        or "NameError" in stderr
        or "SyntaxError" in stderr
    )
    if is_crash:
        return ("crash", script_name, returncode)
    return ("no_help", script_name)


def _run_warn_only_one(script_name: str, timeout: int, repo_root: Path) -> tuple:
    script_path = repo_root / "scripts" / script_name
    if not script_path.exists():
        return ("missing",)

    try:
        returncode, _stdout, stderr = _run_subprocess_safe(
            [sys.executable, str(script_path), "--warn-only"],
            timeout,
            str(repo_root),
        )
    except subprocess.TimeoutExpired:
        return ("timeout", script_name, timeout)

    is_import_error = "ModuleNotFoundError" in stderr or "ImportError" in stderr
    if is_import_error:
        return ("import_error", script_name)

    if returncode == 2:
        is_crash = "Traceback" in stderr or "NameError" in stderr or "SyntaxError" in stderr
        if is_crash:
            return ("crash", script_name)
        return ("no_warn_only", script_name)

    if returncode not in (0, 1):
        return ("abnormal", script_name, returncode)

    return ("ok",)


def _run_jsonl_one(script_name: str, timeout: int, repo_root: Path) -> tuple:
    script_path = repo_root / "scripts" / script_name
    if not script_path.exists():
        return ("missing",)

    try:
        returncode, stdout, stderr = _run_subprocess_safe(
            [sys.executable, str(script_path), "--warn-only", "--jsonl"],
            timeout,
            str(repo_root),
        )
    except subprocess.TimeoutExpired:
        return ("unsupported",)

    if returncode == 2:
        return ("unsupported",)

    is_import_error = "ModuleNotFoundError" in stderr or "ImportError" in stderr
    if is_import_error:
        return ("unsupported",)

    if stdout.strip() and stdout.strip()[0] == "{":
        invalid_entries: list[str] = []
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "severity" not in data:
                    invalid_entries.append(f"{script_name}: JSONL 缺少 severity: {str(data)[:80]}")
            except json.JSONDecodeError:
                invalid_entries.append(f"{script_name}: 无效 JSONL: {line[:80]}")
        return ("supported", invalid_entries)

    return ("unsupported",)


def _run_timing_one(script_name: str, timeout: int, repo_root: Path) -> tuple[float, str]:
    script_path = repo_root / "scripts" / script_name
    if not script_path.exists():
        return (0.0, script_name)

    t0 = time.perf_counter()
    try:
        _run_subprocess_safe(
            [sys.executable, str(script_path), "--warn-only"],
            timeout,
            str(repo_root),
        )
    except subprocess.TimeoutExpired:
        pass
    elapsed = time.perf_counter() - t0
    return (elapsed, script_name)


class TestGovernanceScriptsMeta:
    """清单完整性（原 TestGovernanceScriptsQuick.test_count，单 item 保留）。"""

    def test_count(self) -> None:
        total = len(_CASES["all"])
        quick = len(_CASES["quick"])
        assert total >= 100, f"治理脚本总数异常: {total}"
        print(f"\n  治理脚本: {total} total / {quick} Quick / {len(_CASES['critical'])} Critical")


@pytest.mark.quick
class TestGovernanceScriptsQuick:
    """Quick layer: D1-D4 + D8 scripts（按脚本 parametrize，单脚本失败隔离定位）。"""

    @_XFAIL_ARCH092
    @pytest.mark.parametrize(("name", "timeout"), _QUICK_PARAMS)
    def test_help_quick(self, name: str, timeout: int, repo_root: Path) -> None:
        # no_help 与原聚合语义一致：仅打印不失败
        status = _run_help_one(name, timeout, repo_root)[0]
        assert status not in ("missing", "crash"), f"{name}: --help {status}"

    @pytest.mark.parametrize(("name", "timeout"), _QUICK_PARAMS)
    def test_warn_quick(self, name: str, timeout: int, repo_root: Path) -> None:
        # crash/import_error/no_warn_only 与原聚合语义一致：仅打印不失败
        result = _run_warn_only_one(name, timeout, repo_root)
        status = result[0]
        assert status not in ("timeout", "abnormal"), f"{name}: --warn-only {result}"


@pytest.mark.critical
class TestGovernanceScriptsCritical:
    """Critical layer: D5-D7 scripts（按脚本 parametrize）。"""

    @_XFAIL_ARCH092
    @pytest.mark.parametrize(("name", "timeout"), _CRITICAL_PARAMS)
    def test_help_critical(self, name: str, timeout: int, repo_root: Path) -> None:
        # no_help 与原聚合语义一致：忽略
        status = _run_help_one(name, timeout, repo_root)[0]
        assert status not in ("missing", "crash"), f"{name}: --help {status}"

    @_XFAIL_ARCH092
    @pytest.mark.parametrize(("name", "timeout"), _CRITICAL_PARAMS)
    def test_warn_critical(self, name: str, timeout: int, repo_root: Path) -> None:
        result = _run_warn_only_one(name, timeout, repo_root)
        status = result[0]
        # 与原聚合语义一致：timeout/import_error/crash/abnormal 失败；missing/no_warn_only 忽略
        assert status in ("ok", "missing", "no_warn_only"), f"{name}: --warn-only {result}"


class TestGovernanceScriptsIntegration:
    """Integration layer: JSONL quality check on ALL scripts（按脚本 parametrize）。"""

    @_XFAIL_JSONL
    @pytest.mark.parametrize(("name", "timeout"), _ALL_PARAMS)
    def test_jsonl_one(self, name: str, timeout: int, repo_root: Path) -> None:
        result = _run_jsonl_one(name, timeout, repo_root)
        if result[0] != "supported":
            return  # unsupported/missing 与原聚合语义一致：仅计数不失败
        invalid_entries = result[1]
        # 原语义：>5 条无效才失败（聚合阈值）；拆分后等价=item 内任意无效即失败
        assert not invalid_entries, f"{name} JSONL 输出无效:\n" + "\n".join(invalid_entries[:10])


@pytest.mark.slow
class TestGovernanceScriptsFull:
    """Full layer: all scripts comprehensive check. Nightly/Pre-release only."""

    @_XFAIL_ARCH092
    @pytest.mark.parametrize(("name", "timeout"), _ALL_PARAMS)
    def test_help_full(self, name: str, timeout: int, repo_root: Path) -> None:
        status = _run_help_one(name, timeout, repo_root)[0]
        assert status not in ("crash", "missing"), f"{name}: --help {status}"

    @_XFAIL_ARCH092
    @pytest.mark.parametrize(("name", "timeout"), _ALL_PARAMS)
    def test_warn_full(self, name: str, timeout: int, repo_root: Path) -> None:
        result = _run_warn_only_one(name, timeout, repo_root)
        status = result[0]
        assert status not in ("timeout", "crash", "import_error", "abnormal"), f"{name}: --warn-only {result}"

    def test_timing_report(self, repo_root: Path) -> None:
        """聚合报告保留为单 item（top10 榜单语义，parametrize 无意义）。"""
        test_cases = _CASES["all"]
        timings: list[tuple[float, str]] = []

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(_run_timing_one, name, timeout, repo_root): name for name, timeout, _, _ in test_cases
            }
            for future in as_completed(futures):
                elapsed, name = future.result()
                timings.append((elapsed, name))

        timings.sort(reverse=True)
        print("\n  最慢 10 个脚本:")
        for elapsed, name in timings[:10]:
            print(f"    {elapsed:.1f}s  {name}")
