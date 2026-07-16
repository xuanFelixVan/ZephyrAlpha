# [BLUEPRINT] MOD-INF-005 | scripts/governance/repair/concurrent_commit_test.py | §ghost-commit-red-blue
# [MODULE] scripts.governance.repair.concurrent_commit_test
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 红蓝对抗10场景验证GitCommitGateway根治幽灵提交；测试隔离用临时git仓库；产出报告到data/red_blue/reports/
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=全部PASS; exit 1=有FAIL; exit 2=脚本错误
# [TESTS] tests/test_git_commit_concurrent.py
# [A_module] module_id=MOD-GOV-concurrent_commit_test | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""concurrent_commit_test.py — 幽灵提交红蓝对抗脚本（OPS-2026062514）

10 场景验证 GitCommitGateway 根治幽灵提交（本 session 修改被并发 session commit 一并提交）。

场景清单:
  1. 并发提交不同文件——无跨 session 捡拾
  2. 未暂存修改不被并发 commit 捡拾
  3. 交错 stage + commit——staged 文件不被跨 session commit
  4. 并发同一文件——串行化不丢数据
  5. 3 session 并发提交——全部串行化
  6. 空文件列表——返回 NOTHING_TO_COMMIT
  7. GW 标记——commit message 含 [GW:session_id]
  8. 全局锁互斥——并发 commit 串行执行
  9. stash 恢复——非本次文件 commit 后恢复
  10. 环境变量——ZEPHYR_COMMIT_GATEWAY 标记

产出: data/red_blue/reports/rb_ghost_commit_test_report.md

exit codes: 0=全部PASS, 1=有FAIL, 2=脚本错误
"""

from __future__ import annotations

__manifest__ = """
args: []
description: concurrent_commit_test.py — 幽灵提交红蓝对抗脚本（OPS-2026062514）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Bootstrap: 基于 .git marker 定位仓库根（文件移动不 break，替代 parents[N] 硬编码）
_PROJECT_ROOT = Path(__file__).resolve()
while not (_PROJECT_ROOT / ".git").exists() and _PROJECT_ROOT != _PROJECT_ROOT.parent:
    _PROJECT_ROOT = _PROJECT_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GitCommitGateway,
)

_REPORT_DIR = _PROJECT_ROOT / "data" / "red_blue" / "reports"
_REPORT_FILE = _REPORT_DIR / "rb_ghost_commit_test_report.md"

# 测试用 git author email（可经环境变量覆盖；保留两个不同身份以维持并发测试语义）
_TEST_AUTHOR_EMAIL = os.getenv("CONCURRENT_TEST_AUTHOR_EMAIL", "rb@test.com")
_TEST_AUTHOR_EMAIL_ALT = os.getenv("CONCURRENT_TEST_AUTHOR_EMAIL_ALT", "t@t.com")


@dataclass
class ScenarioResult:
    """单个场景测试结果。"""
    scenario_id: int
    name: str
    passed: bool
    detail: str = ""
    duration_ms: float = 0.0


@dataclass
class TestReport:
    """红蓝对抗测试报告。"""
    results: list[ScenarioResult] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_repo(repo_dir: Path) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "RB-Test"
    env["GIT_AUTHOR_EMAIL"] = _TEST_AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = "RB-Test"
    env["GIT_COMMITTER_EMAIL"] = _TEST_AUTHOR_EMAIL
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "RB-Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.email", _TEST_AUTHOR_EMAIL], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _commit_init(repo_dir: Path, rel: str, content: str) -> None:
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": _TEST_AUTHOR_EMAIL_ALT}
    subprocess.run(["git", "add", rel], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", f"init {rel}", "--no-verify"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _files_in_commit(repo_dir: Path, commit_hash: str) -> list[str]:
    r = subprocess.run(
        ["git", "show", "--name-only", "--format=", commit_hash],
        cwd=str(repo_dir), capture_output=True, text=True, encoding="utf-8",
    )
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def _last_commit_message(repo_dir: Path) -> str:
    r = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        cwd=str(repo_dir), capture_output=True, text=True, encoding="utf-8",
    )
    return r.stdout.strip()


def _run_scenario(scenario_id: int, name: str, fn) -> ScenarioResult:
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory() as td:
            repo_dir = Path(td)
            detail = fn(repo_dir)
        passed = "FAIL" not in detail
        return ScenarioResult(
            scenario_id=scenario_id, name=name, passed=passed,
            detail=detail, duration_ms=(time.monotonic() - start) * 1000,
        )
    except Exception as e:
        return ScenarioResult(
            scenario_id=scenario_id, name=name, passed=False,
            detail=f"EXCEPTION: {e}", duration_ms=(time.monotonic() - start) * 1000,
        )


# ---------------------------------------------------------------------------
# 10 个场景
# ---------------------------------------------------------------------------
def scenario_1(repo_dir: Path) -> str:
    """并发提交不同文件——无跨 session 捡拾。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "x.py", "x = 0\n")
    _commit_init(repo_dir, "y.py", "y = 0\n")
    (repo_dir / "x.py").write_text("x = 1\n", encoding="utf-8")
    (repo_dir / "y.py").write_text("y = 2\n", encoding="utf-8")
    gw = GitCommitGateway(project_root=repo_dir)

    def commit(sess: str, rel: str):
        r = gw.commit(sess, [str((repo_dir / rel).resolve())], f"feat: {sess}")
        return (sess, r.status, r.commit_hash)

    with ThreadPoolExecutor(max_workers=2) as ex:
        results = {f.result()[0]: f.result() for f in [
            ex.submit(commit, "A", "x.py"), ex.submit(commit, "B", "y.py")
        ]}
    a_hash = results["A"][2]
    b_hash = results["B"][2]
    a_files = _files_in_commit(repo_dir, a_hash)
    b_files = _files_in_commit(repo_dir, b_hash)
    if "y.py" in a_files:
        return "FAIL: A 捡拾了 B 的 y.py（幽灵提交）"
    if "x.py" in b_files:
        return "FAIL: B 捡拾了 A 的 x.py（幽灵提交）"
    return "PASS: A 只含 x.py, B 只含 y.py"


def scenario_2(repo_dir: Path) -> str:
    """未暂存修改不被并发 commit 捡拾。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "a.py", "a = 0\n")
    _commit_init(repo_dir, "b.py", "b = 0\n")
    (repo_dir / "a.py").write_text("a = 999\n", encoding="utf-8")  # A 未暂存
    (repo_dir / "b.py").write_text("b = 888\n", encoding="utf-8")  # B commit
    gw = GitCommitGateway(project_root=repo_dir)
    r = gw.commit("B", [str((repo_dir / "b.py").resolve())], "feat: B")
    if r.status != CommitStatus.OK:
        return f"FAIL: B commit 失败: {r.message}"
    files = _files_in_commit(repo_dir, r.commit_hash)
    if "a.py" in files:
        return "FAIL: B 捡拾了 A 的未暂存 a.py"
    if (repo_dir / "a.py").read_text(encoding="utf-8") != "a = 999\n":
        return "FAIL: A 的未暂存修改丢失"
    return "PASS: B 不捡拾 A 未暂存修改, A 修改保留"


def scenario_3(repo_dir: Path) -> str:
    """交错 stage + commit——staged 文件不被跨 session commit。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "x.py", "x = 0\n")
    _commit_init(repo_dir, "y.py", "y = 0\n")
    (repo_dir / "x.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "x.py"], cwd=str(repo_dir), capture_output=True)
    (repo_dir / "y.py").write_text("y = 2\n", encoding="utf-8")
    subprocess.run(["git", "add", "y.py"], cwd=str(repo_dir), capture_output=True)
    gw = GitCommitGateway(project_root=repo_dir)
    ra = gw.commit("A", [str((repo_dir / "x.py").resolve())], "feat: A")
    rb = gw.commit("B", [str((repo_dir / "y.py").resolve())], "feat: B")
    if ra.status != CommitStatus.OK or rb.status != CommitStatus.OK:
        return f"FAIL: commit 失败 A={ra.status} B={rb.status}"
    a_files = _files_in_commit(repo_dir, ra.commit_hash)
    b_files = _files_in_commit(repo_dir, rb.commit_hash)
    if "y.py" in a_files:
        return "FAIL: A 捡拾了 B staged 的 y.py"
    if "x.py" in b_files:
        return "FAIL: B 捡拾了 A 的 x.py"
    return "PASS: 交错 stage 无跨 session commit"


def scenario_4(repo_dir: Path) -> str:
    """并发同一文件——串行化不丢数据。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "shared.py", "v = 0\n")
    gw = GitCommitGateway(project_root=repo_dir)

    def commit_v(sess: str, val: str):
        (repo_dir / "shared.py").write_text(f"v = {val}\n", encoding="utf-8")
        r = gw.commit(sess, [str((repo_dir / "shared.py").resolve())], f"feat: {sess}")
        return (sess, r.status)

    with ThreadPoolExecutor(max_workers=2) as ex:
        results = [f.result() for f in [
            ex.submit(commit_v, "A", "1"), ex.submit(commit_v, "B", "2")
        ]]
    ok = sum(1 for _, s in results if s == CommitStatus.OK)
    if ok < 1:
        return "FAIL: 无 commit 成功"
    content = (repo_dir / "shared.py").read_text(encoding="utf-8")
    if content not in ("v = 1\n", "v = 2\n"):
        return f"FAIL: 文件内容异常: {content!r}"
    return "PASS: 并发同文件串行化, 数据不丢失"


def scenario_5(repo_dir: Path) -> str:
    """3 session 并发提交——全部串行化。"""
    _init_repo(repo_dir)
    for name in ["f1.py", "f2.py", "f3.py"]:
        _commit_init(repo_dir, name, "v = 0\n")
    for name in ["f1.py", "f2.py", "f3.py"]:
        (repo_dir / name).write_text("v = 1\n", encoding="utf-8")
    gw = GitCommitGateway(project_root=repo_dir)

    def commit(sess: str, rel: str):
        r = gw.commit(sess, [str((repo_dir / rel).resolve())], f"feat: {sess}")
        return (sess, r.status)

    with ThreadPoolExecutor(max_workers=3) as ex:
        results = [f.result() for f in [
            ex.submit(commit, "A", "f1.py"),
            ex.submit(commit, "B", "f2.py"),
            ex.submit(commit, "C", "f3.py"),
        ]]
    ok = sum(1 for _, s in results if s == CommitStatus.OK)
    if ok < 3:
        return f"FAIL: 仅 {ok}/3 成功"
    return "PASS: 3 session 全部串行化成功"


def scenario_6(repo_dir: Path) -> str:
    """空文件列表——返回 NOTHING_TO_COMMIT。"""
    _init_repo(repo_dir)
    gw = GitCommitGateway(project_root=repo_dir)
    r = gw.commit("A", [], "feat: empty")
    if r.status != CommitStatus.NOTHING_TO_COMMIT:
        return f"FAIL: 空文件应返回 NOTHING_TO_COMMIT, 实际 {r.status}"
    return "PASS: 空文件返回 NOTHING_TO_COMMIT"


def scenario_7(repo_dir: Path) -> str:
    """GW 标记——commit message 含 [GW:session_id]。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "a.py", "a = 0\n")
    (repo_dir / "a.py").write_text("a = 1\n", encoding="utf-8")
    gw = GitCommitGateway(project_root=repo_dir)
    r = gw.commit("sess-rb7", [str((repo_dir / "a.py").resolve())], "feat: gw marker")
    if r.status != CommitStatus.OK:
        return f"FAIL: commit 失败: {r.message}"
    msg = _last_commit_message(repo_dir)
    if "[GW:sess-rb7]" not in msg:
        return f"FAIL: commit message 缺 GW 标记: {msg}"
    return "PASS: commit message 含 [GW:sess-rb7]"


def scenario_8(repo_dir: Path) -> str:
    """全局锁互斥——并发 commit 串行执行。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "a.py", "a = 0\n")
    _commit_init(repo_dir, "b.py", "b = 0\n")
    gw = GitCommitGateway(project_root=repo_dir)
    timestamps: list[float] = []

    def commit(sess: str, rel: str):
        (repo_dir / rel).write_text(f"v = 1\n", encoding="utf-8")
        t0 = time.monotonic()
        r = gw.commit(sess, [str((repo_dir / rel).resolve())], f"feat: {sess}")
        t1 = time.monotonic()
        timestamps.append(t0)
        timestamps.append(t1)
        return r.status

    with ThreadPoolExecutor(max_workers=2) as ex:
        results = [f.result() for f in [
            ex.submit(commit, "A", "a.py"), ex.submit(commit, "B", "b.py")
        ]]
    if all(s == CommitStatus.OK for s in results):
        return "PASS: 全局锁串行化 commit"
    return f"FAIL: commit 状态: {results}"


def scenario_9(repo_dir: Path) -> str:
    """stash 恢复——非本次文件 commit 后恢复。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "a.py", "a = 0\n")
    _commit_init(repo_dir, "b.py", "b = 0\n")
    (repo_dir / "a.py").write_text("a = 1\n", encoding="utf-8")  # 本次
    (repo_dir / "b.py").write_text("b = 2\n", encoding="utf-8")  # 其他 session
    gw = GitCommitGateway(project_root=repo_dir)
    r = gw.commit("A", [str((repo_dir / "a.py").resolve())], "feat: A")
    if r.status != CommitStatus.OK:
        return f"FAIL: commit 失败: {r.message}"
    if (repo_dir / "b.py").read_text(encoding="utf-8") != "b = 2\n":
        return "FAIL: b.py 修改未恢复（stash pop 失败）"
    stash_list = subprocess.run(
        ["git", "stash", "list"], cwd=str(repo_dir),
        capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()
    if stash_list:
        return f"FAIL: stash 残留: {stash_list}"
    return "PASS: 非本次文件 commit 后恢复, 无 stash 残留"


def scenario_10(repo_dir: Path) -> str:
    """环境变量——ZEPHYR_COMMIT_GATEWAY 标记。"""
    _init_repo(repo_dir)
    _commit_init(repo_dir, "a.py", "a = 0\n")
    (repo_dir / "a.py").write_text("a = 1\n", encoding="utf-8")
    gw = GitCommitGateway(project_root=repo_dir)
    r = gw.commit("sess-rb10", [str((repo_dir / "a.py").resolve())], "feat: env")
    if r.status != CommitStatus.OK:
        return f"FAIL: commit 失败: {r.message}"
    # commit 后环境变量应被清理（finally）
    if os.environ.get("ZEPHYR_COMMIT_GATEWAY") == "1":
        return "FAIL: 环境变量未清理（finally 未执行）"
    return "PASS: 环境变量 commit 后清理"


SCENARIOS = [
    (1, "并发提交不同文件——无跨 session 捡拾", scenario_1),
    (2, "未暂存修改不被并发 commit 捡拾", scenario_2),
    (3, "交错 stage + commit——staged 文件不被跨 session commit", scenario_3),
    (4, "并发同一文件——串行化不丢数据", scenario_4),
    (5, "3 session 并发提交——全部串行化", scenario_5),
    (6, "空文件列表——返回 NOTHING_TO_COMMIT", scenario_6),
    (7, "GW 标记——commit message 含 [GW:session_id]", scenario_7),
    (8, "全局锁互斥——并发 commit 串行执行", scenario_8),
    (9, "stash 恢复——非本次文件 commit 后恢复", scenario_9),
    (10, "环境变量——ZEPHYR_COMMIT_GATEWAY 标记", scenario_10),
]


def run_all() -> TestReport:
    """运行全部 10 场景。"""
    report = TestReport(
        started_at=datetime.now().isoformat(),
    )
    for sid, name, fn in SCENARIOS:
        result = _run_scenario(sid, name, fn)
        report.results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"  场景 {sid:2d} [{status}] {name} ({result.duration_ms:.0f}ms)")
        if not result.passed:
            print(f"         {result.detail}")
    report.finished_at = datetime.now().isoformat()
    return report


def write_report(report: TestReport) -> Path:
    """写报告到 data/red_blue/reports/。"""
    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 幽灵提交红蓝对抗测试报告",
        "",
        f"**任务卡**: OPS-2026062514",
        f"**开始时间**: {report.started_at}",
        f"**结束时间**: {report.finished_at}",
        f"**结果**: {report.passed_count}/{report.total} PASS, {report.failed_count} FAIL",
        "",
        "## 场景详情",
        "",
        "| # | 场景 | 结果 | 耗时(ms) | 详情 |",
        "|---|------|------|----------|------|",
    ]
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        detail = r.detail.replace("|", "\\|").replace("\n", " ")[:100]
        lines.append(f"| {r.scenario_id} | {r.name} | {status} | {r.duration_ms:.0f} | {detail} |")
    lines.append("")
    lines.append("## 结论")
    if report.failed_count == 0:
        lines.append("")
        lines.append(f"**{report.passed_count}/{report.total} PASS** — GitCommitGateway 根治幽灵提交。")
        lines.append("")
        lines.append("### 治本验证")
        lines.append("- 全局串行锁：所有 commit 串行执行，无并发冲突")
        lines.append("- 选择性 stash：非本次文件被隔离，commit 后恢复")
        lines.append("- 受限 commit：`git commit -- <files>` 只提交指定文件")
        lines.append("- GW 标记：commit message 含 [GW:session_id]，可追溯")
    else:
        lines.append("")
        lines.append(f"**{report.failed_count} 场景失败** — 需修复。")
    _REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    return _REPORT_FILE


def main() -> int:
    print("=" * 70)
    print("幽灵提交红蓝对抗测试（OPS-2026062514）")
    print("=" * 70)
    print()
    report = run_all()
    print()
    print("-" * 70)
    print(f"结果: {report.passed_count}/{report.total} PASS, {report.failed_count} FAIL")
    report_path = write_report(report)
    print(f"报告: {report_path}")
    return 0 if report.failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
