# [BLUEPRINT] MOD-GOV-r5_digit_suffix_gate | tests/governance/commit_gates/test_r5_digit_suffix_gate.py
# [MODULE] tests.governance.commit_gates.test_r5_digit_suffix_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.r5_digit_suffix_gate, zephyr.governance.rule_bridge.commit_gate_registry
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，不读/不写真实仓库
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元测试

覆盖 r5_digit_suffix_gate._check 的核心场景：
1. GateSpec 属性（gate_id / priority / isinstance）
2. 无数字后缀目录 → 通过
3. 新建 _NN 数字后缀目录 → 阻断
4. 历史违规 _NN 目录（已存在于 HEAD）→ 通过（progressive_convergence）
5. deletion commit（文件不存在）→ 跳过
6. 空文件列表 → 通过

测试隔离：所有测试用 tmp_path 临时 git 仓库，不污染生产仓库。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.r5_digit_suffix_gate import (  # noqa: E402
    make_r5_digit_suffix_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


class _MockGateway:
    """Mock gateway——R5 gate 只用 project_root 属性。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


def _init_git_repo(repo_dir: Path) -> None:
    """初始化 git 仓库（含初始 commit）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30)
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
        timeout=30,
    )
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
        timeout=30,
    )


def _make_file(repo_dir: Path, rel_path: str) -> Path:
    """在 repo_dir 下创建文件，返回绝对路径。"""
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x = 1\n", encoding="utf-8")
    return f


def _commit_all(repo_dir: Path, msg: str = "wip") -> None:
    """git add . + commit（用于创建 HEAD 历史记录）。"""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30)
    subprocess.run(
        ["git", "commit", "-m", msg, "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
        timeout=30,
    )


class TestGateSpecAttributes:
    """GateSpec 属性。"""

    def test_gate_id(self):
        spec = make_r5_digit_suffix_gate()
        assert spec.gate_id == "R5-DIGIT-SUFFIX"

    def test_priority_is_35(self):
        spec = make_r5_digit_suffix_gate()
        assert spec.priority == 35

    def test_returns_gate_spec_instance(self):
        spec = make_r5_digit_suffix_gate()
        assert isinstance(spec, GateSpec)


class TestNoDigitSuffix:
    """无数字后缀目录 → 通过。"""

    def test_normal_directory_passes(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        f = _make_file(tmp_path, "src/zephyr/governance/foo.py")
        gw = _MockGateway(tmp_path)
        spec = make_r5_digit_suffix_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is True

    def test_empty_files_passes(self, tmp_path: Path) -> None:
        gw = _MockGateway(tmp_path)
        spec = make_r5_digit_suffix_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert "no digit-suffix" in detail


class TestNewDigitSuffixBlocked:
    """新建 _NN 数字后缀目录 → 阻断。"""

    def test_new_digit_suffix_blocked(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        f = _make_file(tmp_path, "src/zephyr/governance/foo_01/bar.py")
        gw = _MockGateway(tmp_path)
        spec = make_r5_digit_suffix_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is False
        assert "R5" in detail
        assert "foo_01" in detail

    def test_multiple_new_digit_suffix_blocked(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        f1 = _make_file(tmp_path, "src/zephyr/infra_06/a.py")
        f2 = _make_file(tmp_path, "src/zephyr/api_03/b.py")
        gw = _MockGateway(tmp_path)
        spec = make_r5_digit_suffix_gate()
        passed, detail = spec.check(gw, [str(f1), str(f2)])
        assert passed is False
        assert "infra_06" in detail
        assert "api_03" in detail


class TestHistoricalDigitSuffixPassed:
    """历史违规 _NN 目录（已存在于 HEAD）→ 通过（progressive_convergence）。"""

    def test_historical_digit_suffix_passed(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        # 先创建 _NN 目录并 commit 到 HEAD（成为历史违规）
        _make_file(tmp_path, "src/zephyr/governance/legacy_01/old.py")
        _commit_all(tmp_path, "historical violation")
        # 再在同目录新增文件（目录已在 HEAD → 历史违规，跳过）
        f_new = _make_file(tmp_path, "src/zephyr/governance/legacy_01/new.py")
        gw = _MockGateway(tmp_path)
        spec = make_r5_digit_suffix_gate()
        passed, detail = spec.check(gw, [str(f_new)])
        assert passed is True
        assert "historical" in detail.lower()


class TestDeletionCommit:
    """deletion commit（文件不存在）→ 跳过（os.path.isfile 返回 False）。"""

    def test_nonexistent_file_in_digit_suffix_dir_skipped(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        gw = _MockGateway(tmp_path)
        spec = make_r5_digit_suffix_gate()
        # 文件不存在（deletion commit），即使路径含 _NN 目录也不阻断
        passed, detail = spec.check(gw, [str(tmp_path / "src/zephyr/governance/deleted_01/gone.py")])
        assert passed is True
        assert "no digit-suffix" in detail
