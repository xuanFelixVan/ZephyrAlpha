# [A_test] module_id: MOD-GOV_git_bisector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_git_bisector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_git_bisector.py -q
# [TTL] task_bound

from __future__ import annotations

import subprocess
import uuid

import pytest

from zephyr.gov_drift.git_bisector import BisectResult, GitBisector


class TestBisectResultInstantiation:
    def test_default_fields(self):
        eid = uuid.uuid4()
        br = BisectResult(event_id=eid)
        assert br.event_id == eid
        assert br.root_cause_commit == ""
        assert br.author == ""
        assert br.message == ""
        assert br.changed_files == []
        assert br.ai_session_hint == ""
        assert br.found is False

    def test_custom_fields(self):
        eid = uuid.uuid4()
        br = BisectResult(
            event_id=eid,
            root_cause_commit="abc123",
            author="dev",
            message="fix bug",
            changed_files=["a.py", "b.py"],
            ai_session_hint="review needed",
            found=True,
        )
        assert br.root_cause_commit == "abc123"
        assert br.author == "dev"
        assert br.message == "fix bug"
        assert len(br.changed_files) == 2
        assert br.found is True
        assert br.ai_session_hint == "review needed"


class TestGitBisectorInstantiation:
    def test_with_explicit_project_root(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        assert gb.project_root == str(tmp_path)

    def test_default_project_root_not_empty(self):
        gb = GitBisector()
        assert gb.project_root != ""

    def test_max_bisect_commits_constant(self):
        assert GitBisector.MAX_BISECT_COMMITS == 50

    def test_cache_initialized_empty(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        assert gb.cache == {}


class TestGitBisectorFindLastGoodCommit:
    def test_returns_none_when_no_manifest(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        result = gb.find_last_good_commit("MOD-A")
        assert result is None


class TestGitBisectorGetCommitRange:
    def test_non_git_directory_returns_empty_or_list(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        commits = gb.get_commit_range("abc123", "HEAD")
        assert isinstance(commits, list)

    def test_returns_list_of_strings(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        commits = gb.get_commit_range("abc123", "def456")
        for c in commits:
            assert isinstance(c, str)


class TestGitBisectorBisect:
    def test_bisect_non_git_raises_index_error(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        with pytest.raises(IndexError):
            gb.bisect("det-1", "script.py", last_good="abc123", first_bad="def456")

    def test_bisect_no_commits_returns_not_found(self, tmp_path):
        # 治本（2026-08-18 第八统筹 merge 验收）：tmp_path 落在主仓 .runtime\tmp 内时，
        # git 向上遍历命中主仓历史致 HEAD~21..HEAD~1 非空（root_cause=真实 merge commit），
        # 用例环境脆性必红。git init 空仓（零提交）使 range 解析失败→stdout 空→found=False，
        # 与 tmp_path 落点无关，环境无关确定性。
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
        gb = GitBisector(project_root=str(tmp_path))
        result = gb.bisect("det-1", "script.py", first_bad="HEAD~1")
        assert isinstance(result, BisectResult)
        assert result.found is False


class TestGitBisectorRunDetectorOnCommit:
    def test_missing_script_returns_true(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        result = gb.run_detector_on_commit("abc123", "nonexistent_script.py")
        assert result is True

    def test_cached_pass_returns_true(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        gb.cache["test.py:abc123"] = {"commit": "abc123", "status": "pass", "cached_at": "2025-01-01"}
        result = gb.run_detector_on_commit("abc123", "test.py")
        assert result is True

    def test_cached_fail_returns_false(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        gb.cache["test.py:def456"] = {"commit": "def456", "status": "fail", "cached_at": "2025-01-01"}
        result = gb.run_detector_on_commit("def456", "test.py")
        assert result is False

    def test_cache_key_format(self, tmp_path):
        gb = GitBisector(project_root=str(tmp_path))
        gb.cache["my_script.py:commit1"] = {"commit": "commit1", "status": "pass", "cached_at": "2025-01-01"}
        assert gb.run_detector_on_commit("commit1", "my_script.py") is True
        assert gb.run_detector_on_commit("commit2", "my_script.py") is not gb.cache.get("my_script.py:commit1")
