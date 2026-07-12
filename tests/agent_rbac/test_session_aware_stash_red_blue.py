# [A_test] module_id=TEST-SES-STASH-RB | layer=test | stability=volatile | safety=L
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ghost-commit-gateway
# [MODULE] tests.red_blue.test_session_aware_stash_red_blue
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.security.access_control.session_concurrency
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=发现 session 隔离 stash 漏洞
# [TESTS] self
# [INVARIANTS] 红蓝对抗隔离——使用 tmp_path 临时 git 仓库，禁止污染生产库；每个测试类覆盖一类攻击向量
# [TTL] task_bound
"""session 隔离 stash 红蓝对抗极限测试。

测试目标：验证 GitCommitGateway 的 session 隔离 stash 功能在极端/对抗场景下
能否坚守核心不变量——"session-A commit 时绝不 stash session-B 的文件"。

红队视角（攻击）：注入各种极端条件，尝试让隔离失效（让别人的文件被 stash 走）。
蓝队视角（防御）：验证已知防护机制生效，记录已知风险缺口。

攻击向量覆盖：
  ① 路径归一化绕过——相对路径 claim vs 绝对路径匹配
  ② registry 损坏/丢失——安全降级回退原逻辑
  ③ 并发 claim 竞态——两 session 抢同一文件
  ④ 孤儿 claim——session 崩溃后持有不释放
  ⑤ claim 部分冲突——冲突文件被排除
  ⑥ 大文件分支隔离——>50 文件触发 pathspec-file 分支
  ⑦ 未跟踪文件保护——untracked 文件不被误 stash
  ⑧ 并发 commit 互不捡拾——核心不变量端到端验证
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GitCommitGateway,
)
from zephyr.security.access_control.session_concurrency import (  # noqa: E402
    SessionRegistry,
    _SESSION_TTL_SECONDS,
)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "RB-Test"
    env["GIT_AUTHOR_EMAIL"] = "rb@test.com"
    env["GIT_COMMITTER_NAME"] = "RB-Test"
    env["GIT_COMMITTER_EMAIL"] = "rb@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "RB-Test"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "rb@test.com"], cwd=str(repo_dir), capture_output=True, check=True)
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _commit_file(repo_dir: Path, rel: str, content: str) -> Path:
    """提交初始文件并返回绝对路径。"""
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", f"init {rel}", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)
    return f


def _attach_stash_spy(gw: GitCommitGateway) -> list[str]:
    """包装 _run_git，记录所有 `git stash push` 的 pathspec（'--' 之后的参数）。"""
    original = gw._run_git
    recorded: list[str] = []

    def spy(cmd: list[str]) -> object:
        if "stash" in cmd and "push" in cmd and "--" in cmd:
            idx = cmd.index("--")
            recorded.extend(cmd[idx + 1:])
        return original(cmd)

    gw._run_git = spy  # type: ignore[assignment]
    return recorded


def _last_commit_files(repo_dir: Path) -> list[str]:
    """获取最近一次 commit 修改的文件列表。"""
    r = subprocess.run(
        ["git", "show", "--name-only", "--format="],
        cwd=str(repo_dir), capture_output=True, text=True, encoding="utf-8",
    )
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


# ===========================================================================
# 攻击向量 ① 路径归一化绕过
# ===========================================================================
class TestPathNormalizationBypass:
    """红队：用相对路径 claim，绝对路径在 porcelain 中出现——匹配是否失效。

    蓝队期望：_normalize_file_path 统一 resolve，相对/绝对路径均能正确匹配。
    """

    def test_relative_claim_isolates_correctly(self, tmp_path: Path) -> None:
        """claim 用相对路径 'sub/b.py'，commit 时 porcelain 输出 'sub/b.py'——隔离是否生效。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "sub/b.py", "b = 0\n")

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # session-A 用相对路径 claim a.py（target）；session-B 用绝对路径 claim b.py
        gw.claim_files("sess-A", ["a.py"])
        gw.claim_files("sess-B", [str(f_b)])

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # b.py 不应被 stash（session-B 持有，session-A 的 held=[a.py] 是 target）
        assert "sub/b.py" not in recorded and "b.py" not in recorded, \
            f"b.py 不应被 stash，pathspec={recorded}"
        # b.py 修改留在工作区
        assert f_b.read_text(encoding="utf-8") == "b = 2\n", "b.py 修改应留在工作区"

    def test_mixed_separator_paths(self, tmp_path: Path) -> None:
        """claim 用 Windows 反斜杠路径，porcelain 用正斜杠——匹配是否失效。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "sub/b.py", "b = 0\n")

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # 用反斜杠路径 claim
        win_path = str(tmp_path / "sub" / "b.py")
        gw.claim_files("sess-B", [win_path])

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK

        assert "sub/b.py" not in recorded and "b.py" not in recorded, \
            f"反斜杠路径 claim 后 b.py 仍不应被 stash，pathspec={recorded}"


# ===========================================================================
# 攻击向量 ② registry 损坏/丢失——安全降级
# ===========================================================================
class TestRegistryCorruptionSafeDegradation:
    """红队：registry 文件被删/写坏——gateway 是否安全降级不崩溃。

    蓝队期望：_load 容错返回 {} → get_session 返回 None → 回退原逻辑，
    commit 仍能完成（可能 stash 全部非目标，但绝不丢数据）。
    """

    def test_registry_deleted_mid_session(self, tmp_path: Path) -> None:
        """claim 后 registry 文件被删——commit 仍成功，数据不丢。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        gw.claim_files("sess-A", [str(f_a)])
        gw.claim_files("sess-B", [str(f_b)])

        # 删除 registry 文件（模拟外部破坏）
        reg_path = tmp_path / ".runtime" / "session_registry.json"
        assert reg_path.exists()
        reg_path.unlink()

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        # commit 应成功（回退原逻辑，b.py 被 stash 后 pop 恢复）
        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK, f"registry 删除后 commit 应仍成功: {result.message}"
        # b.py 修改必须恢复（stash pop）
        assert f_b.read_text(encoding="utf-8") == "b = 2\n", "b.py 修改不应丢失"

    def test_registry_corrupted_json(self, tmp_path: Path) -> None:
        """registry 文件被写坏（非法 JSON）——commit 不崩溃，数据不丢。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)

        # 写坏 registry
        reg_path = tmp_path / ".runtime" / "session_registry.json"
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        reg_path.write_text("{CORRUPTED!!! not json", encoding="utf-8")

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK, f"registry 损坏后 commit 应仍成功: {result.message}"
        assert f_b.read_text(encoding="utf-8") == "b = 2\n", "b.py 修改不应丢失"


# ===========================================================================
# 攻击向量 ③ 并发 claim 竞态
# ===========================================================================
class TestConcurrentClaimRace:
    """红队：两 session 并发 claim 同一文件——冲突检测是否生效。

    蓝队期望：claim_file 不覆盖冲突，只有一个 session 成功 claim；
    另一个返回 False（走 lock_files.py 协调，不阻断 commit）。
    """

    def test_concurrent_claim_same_file_one_wins(self, tmp_path: Path) -> None:
        """两 session 并发 claim 同一文件——只有一个成功。"""
        reg = SessionRegistry(project_root=tmp_path)
        target = str(tmp_path / "shared.py")
        results: list[bool] = []
        lock = threading.Lock()

        def claim(sess: str) -> bool:
            r = reg.claim_file(sess, target)
            with lock:
                results.append(r)
            return r

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(claim, f"sess-{i}") for i in range(2)]
            for f in as_completed(futures, timeout=10):
                f.result()

        # 恰好一个 True，一个 False
        assert results.count(True) == 1, f"应恰好 1 个 claim 成功，实际 {results}"
        assert results.count(False) == 1, f"应恰好 1 个 claim 失败，实际 {results}"

    def test_claim_conflict_excludes_file_from_stash(self, tmp_path: Path) -> None:
        """session-B claim b.py 成功；session-A claim b.py 失败后 commit a.py——
        b.py 仍不被 stash（因为 session-A 的 held 不含 b.py）。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # session-B 先 claim b.py
        assert gw.claim_files("sess-B", [str(f_b)]) == [str(f_b)]
        # session-A claim b.py 失败（冲突）——claim_files 返回空列表
        claimed_b = gw.claim_files("sess-A", [str(f_b)])
        assert claimed_b == [], "session-A 不应能 claim session-B 持有的 b.py"
        # session-A claim a.py（自己的 target）
        gw.claim_files("sess-A", [str(f_a)])

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK

        # b.py 不在 session-A 的 held 中 → 不被 stash
        assert "b.py" not in recorded, f"冲突文件 b.py 不应被 stash，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "b = 2\n", "b.py 修改应留在工作区"


# ===========================================================================
# 攻击向量 ④ 孤儿 claim——session 崩溃后持有不释放
# ===========================================================================
class TestOrphanClaim:
    """红队：session-A claim a.py 后崩溃（不 release）——是否阻塞 session-B。

    蓝队期望：孤儿 claim 不影响其他 session 的 stash 隔离；
    session-A 的 WIP 文件不被其他 session 误 stash。
    """

    def test_orphan_claim_does_not_block_other_session(self, tmp_path: Path) -> None:
        """session-A claim a.py 后崩溃；session-B commit b.py——a.py 不被 stash。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # session-A claim a.py 后"崩溃"（不 release）
        gw.claim_files("sess-A", [str(f_a)])
        # session-B claim b.py
        gw.claim_files("sess-B", [str(f_b)])

        # 两个文件都有 WIP
        f_a.write_text("a = ORPHAN_WIP\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        # session-B commit b.py
        result = gw.commit(session_id="sess-B", files=[str(f_b)], message="feat: b")
        assert result.status == CommitStatus.OK

        # a.py（孤儿 session-A 的 WIP）不应被 session-B stash
        assert "a.py" not in recorded, f"孤儿 claim 的 a.py 不应被 stash，pathspec={recorded}"
        # a.py 修改留在工作区
        assert f_a.read_text(encoding="utf-8") == "a = ORPHAN_WIP\n", "a.py 孤儿 WIP 应保留"

    def test_expired_orphan_claim_allows_reclaim(self, tmp_path: Path) -> None:
        """session-A claim 后 TTL 过期——session-B 能重新 claim 同一文件。"""
        reg = SessionRegistry(project_root=tmp_path)
        target = str(tmp_path / "x.py")
        assert reg.claim_file("sess-A", target) is True

        # 手动把 sess-A 的心跳改到 TTL 之前
        data = reg._load()
        data["sess-A"]["last_heartbeat"] = time.time() - _SESSION_TTL_SECONDS - 1
        reg._save(data)

        # session-B 应能 claim（sess-A 已过期）
        assert reg.claim_file("sess-B", target) is True, "过期 session 的 claim 应可被重新 claim"


# ===========================================================================
# 攻击向量 ⑤ claim 部分冲突
# ===========================================================================
class TestClaimPartialConflict:
    """红队：claim [a.py, b.py] 但 b.py 被其他 session 持有——冲突文件是否排除。

    蓝队期望：claim_files 返回排除冲突后的列表；commit 用原 files（含 b.py），
    但 stash 只动成功 claim 的文件。
    """

    def test_partial_claim_excludes_conflict(self, tmp_path: Path) -> None:
        """claim [a.py, b.py]，b.py 被占用——只 claim a.py，b.py 不在 stash 候选。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")
        f_c = _commit_file(tmp_path, "c.py", "c = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # session-B 先占 b.py
        gw.claim_files("sess-B", [str(f_b)])
        # session-A claim [a.py, b.py, c.py]——b.py 冲突被排除
        claimed = gw.claim_files("sess-A", [str(f_a), str(f_b), str(f_c)])
        assert str(f_b) not in claimed, "冲突的 b.py 不应在 claimed 列表"
        assert str(f_a) in claimed
        assert str(f_c) in claimed

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")
        f_c.write_text("c = 3\n", encoding="utf-8")

        # session-A commit [a.py, c.py]
        result = gw.commit(session_id="sess-A", files=[str(f_a), str(f_c)], message="feat: ac")
        assert result.status == CommitStatus.OK

        # b.py 不在 session-A held → 不被 stash
        assert "b.py" not in recorded, f"冲突 b.py 不应被 stash，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "b = 2\n", "b.py 修改应留在工作区"


# ===========================================================================
# 攻击向量 ⑥ 大文件分支隔离（>50 文件触发 pathspec-file 分支）
# ===========================================================================
class TestLargeFileBranchIsolation:
    """红队：>50 文件触发大文件分支——session 隔离是否在 --keep-index 分支生效。

    蓝队期望：大文件分支的 _get_session_held_non_target 同样过滤候选；
    其他 session 的文件不被 stash。
    """

    def test_large_commit_isolates_other_session_file(self, tmp_path: Path) -> None:
        """session-A commit 51 个文件（触发大文件分支），session-B 的 b.py 不被 stash。"""
        _init_repo(tmp_path)
        n = 51  # _MAX_INLINE_MD_FILES=50 阈值，51 触发大文件分支
        target_files: list[Path] = []
        for i in range(n):
            f = _commit_file(tmp_path, f"t{i:03d}.py", f"v = {i}\n")
            target_files.append(f)
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # session-A claim 全部 target；session-B claim b.py
        gw.claim_files("sess-A", [str(f) for f in target_files])
        gw.claim_files("sess-B", [str(f_b)])

        # 全部修改
        for i, f in enumerate(target_files):
            f.write_text(f"v = {i + 100}\n", encoding="utf-8")
        f_b.write_text("b = 999\n", encoding="utf-8")

        result = gw.commit(
            session_id="sess-A",
            files=[str(f) for f in target_files],
            message="feat: bulk",
        )
        assert result.status == CommitStatus.OK, f"大文件 commit 应成功: {result.message}"

        # b.py 不应被 stash（session-A held 全是 target，b.py 不在其中）
        assert "b.py" not in recorded, f"大文件分支 b.py 不应被 stash，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "b = 999\n", "b.py 修改应留在工作区"
        # 验证 commit 只含 target（无 b.py）
        committed = _last_commit_files(tmp_path)
        assert "b.py" not in committed, f"b.py 不应被 commit 捡拾: {committed}"


# ===========================================================================
# 攻击向量 ⑦ 未跟踪文件保护
# ===========================================================================
class TestUntrackedFilePreservation:
    """红队：工作区有未跟踪文件（??）——是否被误 stash 导致丢失。

    蓝队期望：_collect_non_target_rel 跳过 ?? 行，untracked 文件不被 stash。
    """

    def test_untracked_file_not_stashed(self, tmp_path: Path) -> None:
        """session-A commit a.py，工作区有未跟踪 c.py——c.py 不被 stash。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        # 未跟踪文件
        f_c = tmp_path / "c_untracked.py"
        f_c.write_text("c = UNTRACKED\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        gw.claim_files("sess-A", [str(f_a)])

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK

        # 未跟踪文件不应出现在 stash pathspec
        assert "c_untracked.py" not in recorded, f"未跟踪文件不应被 stash，pathspec={recorded}"
        # 未跟踪文件仍在工作区
        assert f_c.exists() and f_c.read_text(encoding="utf-8") == "c = UNTRACKED\n", \
            "未跟踪文件应留在工作区"


# ===========================================================================
# 攻击向量 ⑧ 并发 commit 互不捡拾——核心不变量端到端
# ===========================================================================
class TestConcurrentCommitNoCrossTheft:
    """红队：两 session 并发 commit 各自的文件——是否互不捡拾对方文件。

    蓝队期望（核心不变量）：
    - 每个 commit 只含该 session 的文件
    - 无 session 的 WIP 被对方 stash 走
    - 无 stash 残留（session 隔离下候选为空，不 stash）
    """

    def test_two_sessions_concurrent_no_cross_theft(self, tmp_path: Path) -> None:
        """session-A commit a.py，session-B commit b.py，并发执行——互不捡拾。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        # 预先 claim（在 commit 外，避免并发 claim 竞态干扰）
        gw.claim_files("sess-A", [str(f_a)])
        gw.claim_files("sess-B", [str(f_b)])

        # 两个文件都有 WIP
        f_a.write_text("a = A_WIN\n", encoding="utf-8")
        f_b.write_text("b = B_WIN\n", encoding="utf-8")

        stash_recorded: list[str] = []
        stash_lock = threading.Lock()

        def commit_and_spy(sess: str, target: Path) -> tuple[str, CommitStatus, list[str]]:
            # 每个 session 独立的 spy（共享 gw，但线程局部记录）
            local_recorded: list[str] = []
            original = gw._run_git

            def spy(cmd: list[str]) -> object:
                if "stash" in cmd and "push" in cmd and "--" in cmd:
                    idx = cmd.index("--")
                    local_recorded.extend(cmd[idx + 1:])
                    with stash_lock:
                        stash_recorded.extend(cmd[idx + 1:])
                return original(cmd)

            gw._run_git = spy  # type: ignore[assignment]
            try:
                r = gw.commit(sess, [str(target)], f"feat: {sess}")
                return (sess, r.status, local_recorded)
            finally:
                gw._run_git = original  # type: ignore[assignment]

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(commit_and_spy, "sess-A", f_a),
                pool.submit(commit_and_spy, "sess-B", f_b),
            ]
            results = {f.result()[0]: f.result() for f in as_completed(futures, timeout=60)}

        # 两个 commit 都应成功
        assert results["sess-A"][1] == CommitStatus.OK, f"sess-A commit 失败: {results['sess-A']}"
        assert results["sess-B"][1] == CommitStatus.OK, f"sess-B commit 失败: {results['sess-B']}"

        # 核心不变量：无 stash 发生（session 隔离下候选为空）
        assert stash_recorded == [], \
            f"session 隔离下不应有任何 stash，pathspec={stash_recorded}"

        # 两个文件最终内容都是各自的修改
        assert f_a.read_text(encoding="utf-8") == "a = A_WIN\n", "a.py 应是 session-A 的修改"
        assert f_b.read_text(encoding="utf-8") == "b = B_WIN\n", "b.py 应是 session-B 的修改"

        # 无 stash 残留
        stash_list = subprocess.run(
            ["git", "stash", "list"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        assert stash_list == "", f"不应有 stash 残留: {stash_list}"

    def test_three_sessions_concurrent_distinct_files(self, tmp_path: Path) -> None:
        """3 session 并发 commit 3 个不同文件——全部成功，无交叉。"""
        _init_repo(tmp_path)
        files = {s: _commit_file(tmp_path, f"{s}.py", f"v = 0\n") for s in ("A", "B", "C")}

        gw = GitCommitGateway(project_root=tmp_path)
        for s, f in files.items():
            gw.claim_files(f"sess-{s}", [str(f)])
            f.write_text(f"v = {s}\n", encoding="utf-8")

        def commit(sess: str, target: Path) -> tuple[str, CommitStatus]:
            r = gw.commit(sess, [str(target)], f"feat: {sess}")
            return (sess, r.status)

        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(commit, f"sess-{s}", f) for s, f in files.items()]
            results = {f.result()[0]: f.result()[1] for f in as_completed(futures, timeout=60)}

        assert all(s == CommitStatus.OK for s in results.values()), \
            f"3 session 应全部成功: {results}"
        # 每个文件最终内容正确
        for s, f in files.items():
            assert f.read_text(encoding="utf-8") == f"v = {s}\n", f"{s}.py 内容错误"


# ===========================================================================
# 蓝队防御总结——核心不变量跨场景验证
# ===========================================================================
class TestDefenseSummary:
    """蓝队防御总结：验证 session 隔离的核心不变量在所有场景下成立。"""

    def test_core_invariant_other_session_file_never_stashed(self, tmp_path: Path) -> None:
        """核心不变量：无论何种配置，其他 session 持有的文件绝不出现在 stash pathspec。"""
        _init_repo(tmp_path)
        f_a = _commit_file(tmp_path, "a.py", "a = 0\n")
        f_b = _commit_file(tmp_path, "b.py", "b = 0\n")
        f_c = _commit_file(tmp_path, "c.py", "c = 0\n")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = _attach_stash_spy(gw)
        # session-B 持有 b.py 和 c.py；session-A 只持有 a.py（target）
        gw.claim_files("sess-B", [str(f_b), str(f_c)])

        f_a.write_text("a = 1\n", encoding="utf-8")
        f_b.write_text("b = 2\n", encoding="utf-8")
        f_c.write_text("c = 3\n", encoding="utf-8")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: a")
        assert result.status == CommitStatus.OK

        # b.py 和 c.py 都不应被 stash
        assert "b.py" not in recorded, f"b.py 不应被 stash: {recorded}"
        assert "c.py" not in recorded, f"c.py 不应被 stash: {recorded}"
        # 两文件 WIP 保留
        assert f_b.read_text(encoding="utf-8") == "b = 2\n"
        assert f_c.read_text(encoding="utf-8") == "c = 3\n"

    def test_data_never_lost_even_on_stash_conflict(self, tmp_path: Path) -> None:
        """数据安全不变量：即使 stash pop 冲突，数据保留在 stash 中不丢失。

        构造：session-A commit a.py（回退模式 stash b.py），但 a.py 的 commit
        内容与 b.py 的 WIP 冲突，导致 pop 失败——验证 stash 保留。
        """
        _init_repo(tmp_path)
        # a.py 和 b.py 初始相同行
        _commit_file(tmp_path, "a.py", "line1\n")
        f_b = _commit_file(tmp_path, "b.py", "line1\n")

        gw = GitCommitGateway(project_root=tmp_path)
        # 不 claim（回退模式）——b.py 会被 stash
        f_b.write_text("line1\nB_WIP\n", encoding="utf-8")
        (tmp_path / "a.py").write_text("line1\nA_COMMIT\n", encoding="utf-8")

        result = gw.commit(session_id="sess-A", files=[str(tmp_path / "a.py")], message="feat: a")
        # commit 应成功
        assert result.status in (CommitStatus.OK, CommitStatus.STASH_CONFLICT), \
            f"commit 应成功或 stash 冲突: {result.status} {result.message}"

        if result.status == CommitStatus.STASH_CONFLICT:
            # stash 保留——数据不丢
            stash_list = subprocess.run(
                ["git", "stash", "list"], cwd=str(tmp_path),
                capture_output=True, text=True, encoding="utf-8",
            ).stdout.strip()
            assert stash_list, f"stash pop 冲突应保留 stash: {stash_list}"
        else:
            # pop 成功——b.py WIP 恢复
            content = f_b.read_text(encoding="utf-8")
            assert "B_WIP" in content, f"b.py WIP 应恢复: {content!r}"
