# [A_test] module_id: MOD-GOV_post_commit_guard_no_verify_threshold | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-277 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_post_commit_guard_no_verify_threshold
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess error->skip_test
# [TESTS] tests/governance/test_post_commit_guard_no_verify_threshold.py
# [A_module] module_id=MOD-TEST-277 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_post_commit_guard_no_verify_threshold.py — 高基数 --no-verify 阈值阻断 e2e 测试

#ARCH-TOOL-HEALTH-V1 Phase 5 治本：验证 post_commit_guard.sh 的 warn-only 计数阈值阻断逻辑。

病根
----
POST-COMMIT-GUARD 对 ZEPHYR_COMMIT_GATEWAY=1 + session 未注册的 commit 采用 warn-only
（allow_overlap 逃生通道）。但同 session 反复触发 warn-only = 系统性问题
（session 注册表 bug 或 --no-verify 滥用），warn-only 无法有效约束。

治本
----
统计 24h 内同 session 的 warn-only 次数（从 .runtime/reconcile_reports/
post_commit_guard_*.json 读取 violation=unregistered_session_id + action=warn_only），
超阈值（默认 3）则升级为阻断（git reset --soft HEAD~1）。

测试策略
--------
1. 创建临时 git 仓库 + 安装 post_commit_guard.sh 为 post-commit hook
2. 在 .runtime/reconcile_reports/ 预置 N 个 mock warn-only 报告
3. 用 [GW:sess-xxx] marker + ZEPHYR_COMMIT_GATEWAY=1 commit
4. 验证：
   - count < threshold → warn-only，commit 保留（HEAD 推进）
   - count >= threshold → block，commit 被 reset（HEAD 回退）
   - 阈值可通过 POST_COMMIT_GUARD_NO_VERIFY_THRESHOLD 环境变量覆盖
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SRC = REPO_ROOT / "scripts" / "governance" / "git_hooks" / "post_commit_guard.sh"


def _git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a git command in repo, return CompletedProcess."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


@pytest.fixture
def temp_git_repo(tmp_path):
    """临时 git 仓库 + post_commit_guard.sh 已安装为 post-commit hook。

    返回 (repo_path, reports_dir)。
    session_registry.json 不含测试 session（触发 warn-only 路径）。
    """
    repo = tmp_path / "test_repo"
    repo.mkdir()
    # git init
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@test.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "commit.gpgsign", "false")
    # 安装 hook
    hook_dir = repo / ".git" / "hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hook_dir / "post-commit"
    shutil.copy(HOOK_SRC, hook_file)
    hook_file.chmod(0o755)
    # .runtime/reconcile_reports 目录
    reports_dir = repo / ".runtime" / "reconcile_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    # session_registry.json 不含测试 session（触发 warn-only 路径，而非 fail-open）
    # 注意：post_commit_guard.sh 在 registry_file 不存在时 fail-open（exit 0），
    # 因此必须创建一个不含测试 session 的 registry 才能进入 warn-only 路径
    registry = repo / ".runtime" / "session_registry.json"
    registry.write_text('{"sessions": {}}', encoding="utf-8")
    return repo, reports_dir


def _make_warn_only_report(reports_dir: Path, session_id: str, timestamp: int, hash_val: str = "abc123"):
    """创建一个 mock warn-only 报告文件（模拟历史 warn-only 事件）。

    使用紧凑 JSON（separators=(",", ":")）——与 post_commit_guard.sh
    实际写入的格式一致（echo "{...}" 无空格），确保 hook 的 grep 模式能匹配。
    """
    report = {
        "gate_id": "POST-COMMIT-GUARD",
        "timestamp": timestamp,
        "hash": hash_val,
        "violation": "unregistered_session_id",
        "session_id": session_id,
        "gw_env": "1",
        "prior_warn_count": 0,
        "threshold": 3,
        "action": "warn_only",
    }
    report_file = reports_dir / f"post_commit_guard_{timestamp}_{os.urandom(2).hex()}.json"
    report_file.write_text(json.dumps(report, separators=(",", ":")), encoding="utf-8")
    return report_file


def _make_initial_commit(repo: Path, session_id: str = "sess-initial") -> str:
    """创建初始 commit（为后续 reset 提供回退点），返回 HEAD hash。"""
    (repo / "initial.txt").write_text("initial", encoding="utf-8")
    _git(repo, "add", "initial.txt")
    env = {**os.environ, "ZEPHYR_COMMIT_GATEWAY": "1"}
    _git(repo, "commit", "--no-verify", "-m", f"initial [GW:{session_id}]", env=env)
    head = _git(repo, "rev-parse", "HEAD")
    return head.stdout.strip()


def _make_test_commit(repo: Path, session_id: str, threshold: int | None = None) -> subprocess.CompletedProcess:
    """创建测试 commit（触发 post-commit hook），返回 git commit 的 CompletedProcess。"""
    test_file = repo / f"test_{os.urandom(4).hex()}.txt"
    test_file.write_text("test", encoding="utf-8")
    _git(repo, "add", str(test_file.name))
    env = {**os.environ, "ZEPHYR_COMMIT_GATEWAY": "1"}
    if threshold is not None:
        env["POST_COMMIT_GUARD_NO_VERIFY_THRESHOLD"] = str(threshold)
    return _git(repo, "commit", "--no-verify", "-m", f"test commit [GW:{session_id}]", env=env)


class TestNoVerifyThreshold:
    """--no-verify 高基数阈值阻断逻辑 e2e 测试。"""

    def test_below_threshold_warns_and_preserves_commit(self, temp_git_repo):
        """count < threshold → warn-only，commit 保留（HEAD 推进）。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 预置 2 个 warn-only 报告（threshold=3，2 < 3 → warn）
        now = int(time.time())
        for i in range(2):
            _make_warn_only_report(reports_dir, "sess-test-warn", now - 100 + i)
        # 创建 commit → 应该 warn-only 但保留
        result = _make_test_commit(repo, "sess-test-warn")
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head != initial_head, (
            f"commit 应被保留（warn-only），HEAD 应推进。current={current_head[:8]} initial={initial_head[:8]}"
        )
        combined = result.stdout + result.stderr
        assert "WARN" in combined, f"输出应含 WARN：{combined}"

    def test_at_threshold_blocks_and_resets_commit(self, temp_git_repo):
        """count >= threshold → block，commit 被 reset（HEAD 回退到 initial）。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 预置 3 个 warn-only 报告（threshold=3，3 >= 3 → block）
        now = int(time.time())
        for i in range(3):
            _make_warn_only_report(reports_dir, "sess-test-block", now - 100 + i)
        # 创建 commit → 应该 block 并 reset
        result = _make_test_commit(repo, "sess-test-block")
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head == initial_head, (
            f"commit 应被 reset（block），HEAD 应回退到 initial。current={current_head[:8]} initial={initial_head[:8]}"
        )
        combined = result.stdout + result.stderr
        assert "BLOCK" in combined, f"输出应含 BLOCK：{combined}"

    def test_threshold_configurable_via_env_var(self, temp_git_repo):
        """POST_COMMIT_GUARD_NO_VERIFY_THRESHOLD=1 → 1 个 warn-only 后即 block。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 预置 1 个 warn-only 报告（自定义 threshold=1，1 >= 1 → block）
        now = int(time.time())
        _make_warn_only_report(reports_dir, "sess-test-cfg", now - 100)
        # 创建 commit → threshold=1，1 个 prior warn → block
        result = _make_test_commit(repo, "sess-test-cfg", threshold=1)
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head == initial_head, (
            f"threshold=1 时 1 个 prior warn 应 block。current={current_head[:8]} initial={initial_head[:8]}"
        )
        combined = result.stdout + result.stderr
        assert "BLOCK" in combined, f"输出应含 BLOCK：{combined}"

    def test_zero_prior_warnings_preserves_commit(self, temp_git_repo):
        """无历史 warn-only → warn-only（count=0），commit 保留。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 不预置任何 warn-only 报告（count=0）
        result = _make_test_commit(repo, "sess-test-fresh")
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head != initial_head, (
            f"无历史 warn-only 时 commit 应保留。current={current_head[:8]} initial={initial_head[:8]}"
        )
        combined = result.stdout + result.stderr
        assert "WARN" in combined, f"输出应含 WARN：{combined}"
        # 验证累计计数显示 0/3
        assert "0/3" in combined, f"应显示累计 0/3：{combined}"

    def test_expired_reports_not_counted(self, temp_git_repo):
        """超过 24h 窗口的 warn-only 报告不计入。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 预置 3 个 25h 前的 warn-only 报告（超出 24h 窗口 → 不计入 → warn-only）
        now = int(time.time())
        expired_ts = now - 25 * 3600  # 25h ago
        for i in range(3):
            _make_warn_only_report(reports_dir, "sess-test-expire", expired_ts + i)
        result = _make_test_commit(repo, "sess-test-expire")
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head != initial_head, (
            f"过期的 warn-only 报告不应计入，commit 应保留。current={current_head[:8]} initial={initial_head[:8]}"
        )
        combined = result.stdout + result.stderr
        assert "WARN" in combined, f"输出应含 WARN（过期报告不计）：{combined}"

    def test_different_session_reports_not_counted(self, temp_git_repo):
        """其他 session 的 warn-only 报告不计入当前 session。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 预置 3 个 OTHER session 的 warn-only 报告
        now = int(time.time())
        for i in range(3):
            _make_warn_only_report(reports_dir, "sess-other", now - 100 + i)
        # 当前 session commit → 应 warn-only（其他 session 的不计入）
        result = _make_test_commit(repo, "sess-test-isolated")
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head != initial_head, (
            f"其他 session 的报告不应计入，commit 应保留。current={current_head[:8]} initial={initial_head[:8]}"
        )

    def test_spaced_json_reports_also_counted(self, temp_git_repo):
        """spaced JSON 格式（json.dumps 默认）的报告也能被正确计数（健壮性）。"""
        repo, reports_dir = temp_git_repo
        initial_head = _make_initial_commit(repo)
        # 预置 3 个 spaced JSON 格式的 warn-only 报告（模拟外部工具写入）
        now = int(time.time())
        for i in range(3):
            report = {
                "gate_id": "POST-COMMIT-GUARD",
                "timestamp": now - 100 + i,
                "hash": "abc123",
                "violation": "unregistered_session_id",
                "session_id": "sess-test-spaced",
                "gw_env": "1",
                "action": "warn_only",
            }
            # 默认 json.dumps 带空格（"key": value）——hook 的 grep 模式应容忍
            report_file = reports_dir / f"post_commit_guard_spaced_{now}_{i}.json"
            report_file.write_text(json.dumps(report), encoding="utf-8")
        # 创建 commit → spaced JSON 也应被计数，3 >= 3 → block
        result = _make_test_commit(repo, "sess-test-spaced")
        current_head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        assert current_head == initial_head, (
            f"spaced JSON 报告应被计数（3 >= 3 → block）。current={current_head[:8]} initial={initial_head[:8]}"
        )
        combined = result.stdout + result.stderr
        assert "BLOCK" in combined, f"spaced JSON 应触发 BLOCK：{combined}"
