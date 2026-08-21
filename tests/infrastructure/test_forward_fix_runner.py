# [A_test] module_id: MOD-GOV_forward_fix_runner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_forward_fix_runner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.forward_fix_runner import FixResult, ForwardFixRunner


@pytest.fixture
def tmp_project(tmp_path):
    return tmp_path


@pytest.fixture
def runner(tmp_project):
    return ForwardFixRunner(project_root=tmp_project)


class TestForwardFixRunnerInstantiation:
    def test_default_project_root(self):
        r = ForwardFixRunner()
        assert r.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_project):
        r = ForwardFixRunner(project_root=tmp_project)
        assert r.project_root == tmp_project


class TestCanForwardFix:
    def test_low_risk_few_files(self, runner):
        assert runner.can_forward_fix(["a.py", "b.py"], "low") is True

    def test_low_risk_three_files(self, runner):
        assert runner.can_forward_fix(["a.py", "b.py", "c.py"], "low") is True

    def test_low_risk_four_files(self, runner):
        assert runner.can_forward_fix(["a.py", "b.py", "c.py", "d.py"], "low") is False

    def test_high_risk_blocks(self, runner):
        assert runner.can_forward_fix(["a.py"], "high") is False

    def test_medium_risk_few_files(self, runner):
        assert runner.can_forward_fix(["a.py"], "medium") is True

    def test_medium_risk_many_files(self, runner):
        assert runner.can_forward_fix(["a", "b", "c", "d"], "medium") is False

    def test_empty_file_list(self, runner):
        assert runner.can_forward_fix([], "low") is True

    def test_high_risk_empty_files(self, runner):
        assert runner.can_forward_fix([], "high") is False

    def test_exactly_three_files(self, runner):
        assert runner.can_forward_fix(["1", "2", "3"], "low") is True

    def test_four_files_any_risk(self, runner):
        assert runner.can_forward_fix(["1", "2", "3", "4"], "medium") is False


class TestGenerateFix:
    @pytest.fixture(autouse=True)
    def _block_real_git(self, monkeypatch):
        """隔离真实 git 子进程：tmp_project 落在仓内 .runtime/tmp（pytest basetemp），
        git 会从该目录上溯命中真实仓 D:\\ZephyrAlpha——generate_fix 内的
        git add -A / git commit 将对真实仓执行并触发 pre-commit 门禁链挂起
        （120s timeout 实证），且有污染真实工作区风险。本 fixture 模拟 git
        失败路径（generate_fix 契约：子进程异常 → 返回 success=False 的
        FixResult），使测试与真实 git 零接触。
        """

        def _raise(*args, **kwargs):
            raise RuntimeError("mocked git failure")

        monkeypatch.setattr(
            "zephyr.infrastructure.rollback.forward_fix_runner.run_subprocess_hidden",
            _raise,
        )

    def test_returns_fix_result_on_git_failure(self, runner):
        result = runner.generate_fix("abc123", "test error")
        assert isinstance(result, FixResult)
        assert result.commit_sha == "abc123"
        assert result.fix_type == "forward_fix"
        assert result.success is False

    def test_fix_result_has_details(self, runner):
        result = runner.generate_fix("sha", "error msg")
        assert isinstance(result.details, list)

    def test_fix_result_success_field_is_bool(self, runner):
        result = runner.generate_fix("sha", "msg")
        assert isinstance(result.success, bool)

    def test_patch_file_field(self, runner):
        result = runner.generate_fix("deadbeef", "err")
        assert isinstance(result.patch_file, str)


class TestFixResultDataclass:
    def test_default_details(self):
        r = FixResult(success=True, commit_sha="abc", fix_type="forward_fix", patch_file="p.patch")
        assert r.details == []

    def test_custom_details(self):
        r = FixResult(success=False, commit_sha="abc", fix_type="forward_fix", patch_file="", details=["err1", "err2"])
        assert len(r.details) == 2
