# [A_test] module_id: MOD-INF-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/check_protected_paths.py | §B4-merge-approval-transpose
# [MODULE] tests.scripts.test_check_protected_paths_merge
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_check_protected_paths_merge.py — B4 治本（2026-08-19）merge 场景审批转置单测

误伤实证：受保护路径改动在分支侧 commit 已带 [ARCH-APPROVAL] 审批标记，裸 git merge
触发的 pre-commit 拿不到分支侧 message，merge commit 本身无标记被拦（05/08 两域实证）。
治本：在途 merge 时改查分支侧 commit 链（HEAD..第二父）审批标记，有则放无则拦。

场景覆盖：
1. 分支侧带审批标记 → 放行
2. 分支侧无审批标记 → 拦截（含分支侧 sha 清单）
3. 逐文件粒度：一个受保护文件已审批、另一个未审批 → 拦未审批那个
4. 非 merge 场景 → 原逻辑拦截（回归防破）
5. MERGE_HEAD 内容损坏 → fail-closed 拦截
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "d6_security" / "check_protected_paths.py"


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    for k in ("ZEPHYR_SESSION_ID", "ZEPHYR_RECONCILER_AUTO_COMMIT", "ZEPHYR_PROTECTED_PATHS_BYPASS"):
        env.pop(k, None)
    return env


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_git_env(),
        check=True,
    )


def _init_repo(repo_dir: Path) -> str:
    """初始化仓库（含 .gitignore/AGENTS.md 基线 commit），返回主分支名。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    _git(repo_dir, "init")
    _git(repo_dir, "config", "user.name", "Test")
    _git(repo_dir, "config", "user.email", "test@test.com")
    (repo_dir / ".gitignore").write_text("*.log\n", encoding="utf-8")
    (repo_dir / "AGENTS.md").write_text("# stub\n", encoding="utf-8")
    (repo_dir / "main.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo_dir, "add", ".")
    _git(repo_dir, "commit", "-m", "init", "--no-verify")
    return _git(repo_dir, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def _make_merge_scene(
    repo: Path,
    base_ref: str,
    side_changes: list[tuple[str, str, str]],
) -> None:
    """构造在途 merge：side 分支按 (file, content, message) 逐个 commit，回主干 merge --no-commit。

    主干先独立前进一格（真分叉，防 fast-forward 规范化），再 merge --no-commit --no-ff side，
    结束后 staged 区持有 side 带入的变更 + MERGE_HEAD 在途。
    """
    _git(repo, "checkout", "-qb", "side")
    for rel, content, msg in side_changes:
        (repo / rel).write_text(content, encoding="utf-8")
        _git(repo, "add", rel)
        _git(repo, "commit", "-m", msg, "--no-verify")
    _git(repo, "checkout", "-q", base_ref)
    (repo / "main2.py").write_text("y = 2\n", encoding="utf-8")
    _git(repo, "add", "main2.py")
    _git(repo, "commit", "-m", "main advances", "--no-verify")
    _git(repo, "merge", "--no-commit", "--no-ff", "side")


def _run_staged(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--staged"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_git_env(),
        timeout=30,
    )


class TestMergeBranchApproval:
    """B4：merge 场景分支侧审批标记转置核验。"""

    def test_merge_with_branch_approval_passes(self, tmp_path: Path) -> None:
        """分支侧 commit 带 [ARCH-APPROVAL] → merge 场景放行。"""
        base = _init_repo(tmp_path)
        _make_merge_scene(
            tmp_path,
            base,
            [
                (".gitignore", "*.log\n*.tmp\n", "chore: gitignore tmp rule [ARCH-APPROVAL:ARCH-TEST-001]"),
            ],
        )
        r = _run_staged(tmp_path)
        assert r.returncode == 0, f"分支侧已审批应放行: rc={r.returncode} out={r.stdout} err={r.stderr}"
        assert "分支侧审批标记核验通过" in r.stderr

    def test_merge_without_branch_approval_blocks(self, tmp_path: Path) -> None:
        """分支侧 commit 无标记 → 拦截且列出分支侧 sha。"""
        base = _init_repo(tmp_path)
        _make_merge_scene(
            tmp_path,
            base,
            [
                (".gitignore", "*.log\n*.tmp\n", "chore: gitignore tmp rule (no approval)"),
            ],
        )
        r = _run_staged(tmp_path)
        assert r.returncode == 1, f"无审批应拦截: rc={r.returncode} out={r.stdout}"
        assert "IRN-010 FAIL" in r.stdout and ".gitignore" in r.stdout
        assert "分支侧 commits:" in r.stdout, f"应列分支侧 sha 清单: {r.stdout}"

    def test_merge_partial_approval_blocks(self, tmp_path: Path) -> None:
        """逐文件粒度：.gitignore 已审批 + AGENTS.md 未审批 → 只拦 AGENTS.md。"""
        base = _init_repo(tmp_path)
        _make_merge_scene(
            tmp_path,
            base,
            [
                (".gitignore", "*.log\n*.tmp\n", "chore: gitignore [ARCH-APPROVAL:ARCH-TEST-002]"),
                ("AGENTS.md", "# stub v2\n", "docs: agents tweak (no approval)"),
            ],
        )
        r = _run_staged(tmp_path)
        assert r.returncode == 1, f"部分未审批应拦截: rc={r.returncode} out={r.stdout}"
        assert "AGENTS.md" in r.stdout, f"未审批文件应在 findings: {r.stdout}"
        assert "'AGENTS.md'" in r.stdout or "AGENTS.md'" in r.stdout
        # 已审批的 .gitignore 不出现在 findings 行
        fail_lines = [ln for ln in r.stdout.splitlines() if "IRN-010 FAIL" in ln]
        assert all(".gitignore" not in ln for ln in fail_lines), f"已审批文件不得入 findings: {fail_lines}"

    def test_non_merge_still_blocks(self, tmp_path: Path) -> None:
        """回归防破：非 merge 场景 staged 受保护路径 → 原逻辑拦截。"""
        _init_repo(tmp_path)
        (tmp_path / ".gitignore").write_text("*.log\n*.tmp\n", encoding="utf-8")
        _git(tmp_path, "add", ".gitignore")
        r = _run_staged(tmp_path)
        assert r.returncode == 1, f"非 merge 无标记应拦截: rc={r.returncode} out={r.stdout}"
        assert ".gitignore" in r.stdout

    def test_merge_head_unparseable_fails_closed(self, tmp_path: Path) -> None:
        """MERGE_HEAD 内容损坏 → fail-closed 按无审批拦截。"""
        _init_repo(tmp_path)
        (tmp_path / ".gitignore").write_text("*.log\n*.tmp\n", encoding="utf-8")
        _git(tmp_path, "add", ".gitignore")
        (tmp_path / ".git" / "MERGE_HEAD").write_bytes(b"garbage-not-a-sha\n")
        r = _run_staged(tmp_path)
        assert r.returncode == 1, f"MERGE_HEAD 损坏应 fail-closed 拦截: rc={r.returncode}"
        assert "IRN-010 FAIL" in r.stdout
