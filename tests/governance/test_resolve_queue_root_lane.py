# [BLUEPRINT] MOD-ALT-001 | (auto-injected by S4 reconciler) | §
# [MODULE] tests.governance.test_resolve_queue_root_lane
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
"""resolve_queue_root 车道感知回归（修3，2026-10-05）：双标记前缀截断+默认分支覆盖。

背景：车道（.aidrafts/<车道>、.worktrees/<sid>）内按 __file__ 派生的队列根落进
车道本地目录，主带不排=袋搁浅——10-05 三车道独立实证。修2 只盖显式+.aidrafts，
本批（修3）补 .worktrees、默认 __file__ 分支与子路径保留。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent
for p in (str(_REPO_ROOT.parent.parent / "scripts"),):
    if p not in sys.path:
        sys.path.insert(0, p)

import commit_queue as cq  # noqa: E402


class TestStripLanePrefix:
    def test_aidrafts_stripped_keep_subpath(self):
        p = Path("D:/repo/.aidrafts/laneA/.runtime/commit_queue")
        assert cq._strip_lane_prefix(p) == Path("D:/repo/.runtime/commit_queue")

    def test_worktrees_stripped_keep_subpath(self):
        p = Path("D:/repo/.worktrees/st-sid-1/.runtime/commit_queue")
        assert cq._strip_lane_prefix(p) == Path("D:/repo/.runtime/commit_queue")

    def test_lane_root_only_back_to_main(self):
        assert cq._strip_lane_prefix(Path("D:/repo/.aidrafts/laneA")) == Path("D:/repo")

    def test_plain_path_unchanged(self):
        p = Path("D:/repo/.runtime/commit_queue")
        assert cq._strip_lane_prefix(p) == p


class TestResolveQueueRootLane:
    def test_explicit_aidrafts_redirects(self):
        r = cq.resolve_queue_root("D:/repo/.aidrafts/laneB/.runtime/commit_queue")
        assert r == Path("D:/repo/.runtime/commit_queue")

    def test_explicit_worktrees_redirects(self):
        r = cq.resolve_queue_root(Path("D:/repo/.worktrees/st-x/.runtime/commit_queue"))
        assert r == Path("D:/repo/.runtime/commit_queue")

    def test_default_branch_lane_anchored_to_main(self, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.delenv(cq.QUEUE_ENV_VAR, raising=False)
        # 纯路径数学（不触盘）：假路径避开 pytest basetemp 自身位于 .worktrees 的污染
        monkeypatch.setattr(cq, "_REPO_ROOT", Path("D:/fake/repo/.worktrees/st-sid-2"))
        assert cq.resolve_queue_root() == Path("D:/fake/repo/.runtime/commit_queue")

    def test_default_branch_main_unchanged(self, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.delenv(cq.QUEUE_ENV_VAR, raising=False)
        monkeypatch.setattr(cq, "_REPO_ROOT", Path("D:/fake/repo"))
        assert cq.resolve_queue_root() == Path("D:/fake/repo/.runtime/commit_queue")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
