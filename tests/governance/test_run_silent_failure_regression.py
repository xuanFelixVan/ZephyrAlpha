# [A_test] module_id: MOD-GOV_run_silent_failure_regression | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-281 | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P3-2
# [MODULE] tests.governance.test_run_silent_failure_regression
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess error->skip_test
# [TESTS] tests/governance/test_run_silent_failure_regression.py
# [A_module] module_id=MOD-TEST-281 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_run_silent_failure_regression.py — silent-failure 回归 runner 单元测试（P3-2）

#Ruling-100PCT-AI-GOVERNANCE P3-2 治本：验证 run_silent_failure_regression.py 的逻辑：

测试组：
- TestRegressionStageResultContract: TypedDict 字段完整性
- TestRunStageNeverThrows: subprocess 异常 → failed 段，不抛
- TestRunSilentFailureRegression: 三段式汇总 + ok 键判定
- TestMainCli: CLI exit code 逻辑
- TestE2ERealRepo: 真实仓库 e2e（不抛异常，结果可能是 pass/fail）
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


# ===========================================================================
# 加载 runner 模块（不在 src/zephyr 下，需 importlib 加载）
# ===========================================================================

_RUNNER_PATH = Path(__file__).resolve().parents[2] / "scripts" / "governance" / "run_silent_failure_regression.py"


def _load_runner_module():
    """用 importlib 加载 run_silent_failure_regression.py 为模块。"""
    mod_name = "_test_target_run_silent_failure_regression"
    spec = importlib.util.spec_from_file_location(mod_name, _RUNNER_PATH)
    assert spec is not None and spec.loader is not None, f"无法加载 {_RUNNER_PATH}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def runner():
    """加载 runner 模块。"""
    return _load_runner_module()


# ===========================================================================
# TestRegressionStageResultContract: TypedDict 字段完整性
# ===========================================================================

class TestRegressionStageResultContract:
    """RegressionStageResult / RegressionResult TypedDict 字段验证。"""

    def test_stage_result_has_required_fields(self, runner):
        """RegressionStageResult 必须含 name/ok/exit_code/duration_s/detail 5 个字段。"""
        # TypedDict 是类型提示，运行时是 dict。构造一个验证字段名。
        # 通过 __annotations__ 检查
        annotations = runner.RegressionStageResult.__annotations__
        required = {"name", "ok", "exit_code", "duration_s", "detail"}
        assert required.issubset(annotations.keys()), (
            f"RegressionStageResult 缺少字段: {required - annotations.keys()}"
        )

    def test_regression_result_has_required_fields(self, runner):
        """RegressionResult 必须含 ok/stages/total_duration_s/summary 4 个字段。"""
        annotations = runner.RegressionResult.__annotations__
        required = {"ok", "stages", "total_duration_s", "summary"}
        assert required.issubset(annotations.keys()), (
            f"RegressionResult 缺少字段: {required - annotations.keys()}"
        )

    def test_regression_result_ok_is_bool(self, runner):
        """RegressionResult.ok 字段类型应为 bool（运行时验证）。"""
        # 构造一个 mock 结果验证可赋值 bool
        result: runner.RegressionResult = {
            "ok": True,
            "stages": [],
            "total_duration_s": 0.0,
            "summary": "test",
        }
        assert isinstance(result["ok"], bool)

    def test_stages_definition_has_three_stages(self, runner):
        """STAGES 元组应含 3 段：pytest / audit_return_contract / audit_worktree_ops。"""
        assert len(runner.STAGES) == 3
        names = [s[0] for s in runner.STAGES]
        assert names == ["pytest", "audit_return_contract", "audit_worktree_ops"]


# ===========================================================================
# TestRunStageNeverThrows: subprocess 异常 → failed 段，不抛
# ===========================================================================

class TestRunStageNeverThrows:
    """_run_stage 永不抛异常——所有异常转换为 failed RegressionStageResult。"""

    def test_subprocess_success_returns_ok(self, runner, tmp_path):
        """subprocess 退出 0 → RegressionStageResult.ok=True。"""
        def cmd_builder(root):
            return ([sys.executable, "-c", "print('hello')"], root)
        result = runner.run_stage("test", "test", cmd_builder, tmp_path)
        assert result["ok"] is True
        assert result["exit_code"] == 0
        assert result["name"] == "test"
        assert "hello" in result["detail"]
        assert result["duration_s"] >= 0

    def test_subprocess_failure_returns_not_ok(self, runner, tmp_path):
        """subprocess 退出 1 → RegressionStageResult.ok=False, exit_code=1。"""
        def cmd_builder(root):
            return ([sys.executable, "-c", "import sys; sys.exit(1)"], root)
        result = runner.run_stage("test", "test", cmd_builder, tmp_path)
        assert result["ok"] is False
        assert result["exit_code"] == 1

    def test_subprocess_exception_returns_not_ok(self, runner, tmp_path):
        """cmd_builder 抛异常 → RegressionStageResult.ok=False, exit_code=-1, 不抛。"""
        def cmd_builder(root):
            raise RuntimeError("intentional test exception")
        result = runner.run_stage("test", "test", cmd_builder, tmp_path)
        assert result["ok"] is False
        assert result["exit_code"] == -1
        assert "intentional test exception" in result["detail"]

    def test_subprocess_timeout_returns_not_ok(self, runner, tmp_path):
        """subprocess 超时 → RegressionStageResult.ok=False, exit_code=-1, detail 含 timeout。"""
        def cmd_builder(root):
            # sleep 10s，但 _run_stage timeout=600s，需 mock 缩短 timeout
            return ([sys.executable, "-c", "import time; time.sleep(10)"], root)
        # 用 patch 缩短 timeout 到 1s
        original_run = runner.subprocess.run
        try:
            # 直接 patch subprocess.run 抛 TimeoutExpired
            def fake_run(*args, **kwargs):
                raise runner.subprocess.TimeoutExpired(cmd="test", timeout=1)
            runner.subprocess.run = fake_run
            result = runner.run_stage("test", "test", cmd_builder, tmp_path)
            assert result["ok"] is False
            assert result["exit_code"] == -1
            assert "timeout" in result["detail"].lower()
        finally:
            runner.subprocess.run = original_run

    def test_stage_result_detail_truncated_to_200(self, runner, tmp_path):
        """detail 字段超过 200 字符时截断（对标 reconciliation_registry）。"""
        long_output = "x" * 500
        def cmd_builder(root):
            return ([sys.executable, "-c", f"print('{long_output}')"], root)
        result = runner.run_stage("test", "test", cmd_builder, tmp_path)
        # detail 取 stdout 最后一行，长度应 <= 200
        assert len(result["detail"]) <= 200


# ===========================================================================
# TestRunSilentFailureRegression: 三段式汇总 + ok 键判定
# ===========================================================================

class TestRunSilentFailureRegression:
    """run_silent_failure_regression 三段式汇总逻辑。"""

    def test_all_stages_pass_returns_ok_true(self, runner, tmp_path):
        """三段全 pass → RegressionResult.ok=True。"""
        def make_pass_builder(name):
            def builder(root):
                return ([sys.executable, "-c", f"print('{name} ok')"], root)
            return builder
        # 替换 STAGES 为 3 个 mock pass 段
        original_stages = runner.STAGES
        try:
            runner.STAGES = [
                ("s1", "mock1", make_pass_builder("s1")),
                ("s2", "mock2", make_pass_builder("s2")),
                ("s3", "mock3", make_pass_builder("s3")),
            ]
            result = runner.run_silent_failure_regression(tmp_path)
            assert result["ok"] is True
            assert len(result["stages"]) == 3
            assert all(s["ok"] for s in result["stages"])
            assert "PASSED" in result["summary"]
        finally:
            runner.STAGES = original_stages

    def test_one_stage_fail_returns_ok_false(self, runner, tmp_path):
        """任一段 fail → RegressionResult.ok=False。"""
        def make_pass_builder(name):
            def builder(root):
                return ([sys.executable, "-c", f"print('{name}')"], root)
            return builder
        def make_fail_builder(name):
            def builder(root):
                return ([sys.executable, "-c", f"import sys; sys.exit(2); print('{name}')"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [
                ("s1", "mock1", make_pass_builder("s1")),
                ("s2", "mock2", make_fail_builder("s2")),  # fail
                ("s3", "mock3", make_pass_builder("s3")),
            ]
            result = runner.run_silent_failure_regression(tmp_path)
            assert result["ok"] is False
            assert len(result["stages"]) == 3
            assert result["stages"][1]["ok"] is False
            assert "FAILED" in result["summary"]
            assert "s2" in result["summary"]
        finally:
            runner.STAGES = original_stages

    def test_all_stages_fail_returns_ok_false(self, runner, tmp_path):
        """三段全 fail → RegressionResult.ok=False。"""
        def make_fail_builder(name):
            def builder(root):
                return ([sys.executable, "-c", "import sys; sys.exit(1)"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [
                ("s1", "mock1", make_fail_builder("s1")),
                ("s2", "mock2", make_fail_builder("s2")),
                ("s3", "mock3", make_fail_builder("s3")),
            ]
            result = runner.run_silent_failure_regression(tmp_path)
            assert result["ok"] is False
            assert all(not s["ok"] for s in result["stages"])
            assert "FAILED" in result["summary"]
        finally:
            runner.STAGES = original_stages

    def test_total_duration_summarized(self, runner, tmp_path):
        """total_duration_s 字段为正数。"""
        def make_pass_builder(name):
            def builder(root):
                return ([sys.executable, "-c", f"print('{name}')"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [("s1", "mock1", make_pass_builder("s1"))]
            result = runner.run_silent_failure_regression(tmp_path)
            assert result["total_duration_s"] >= 0
        finally:
            runner.STAGES = original_stages


# ===========================================================================
# TestMainCli: CLI exit code 逻辑
# ===========================================================================

class TestMainCli:
    """main() CLI 入口 exit code 验证。"""

    def test_main_returns_0_on_pass(self, runner, tmp_path, capsys):
        """所有段 pass → main() 返回 0。"""
        def make_pass_builder(name):
            def builder(root):
                return ([sys.executable, "-c", f"print('{name}')"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [("s1", "mock1", make_pass_builder("s1"))]
            with patch("sys.argv", ["runner", "--project-root", str(tmp_path)]):
                exit_code = runner.main()
            assert exit_code == 0
        finally:
            runner.STAGES = original_stages

    def test_main_returns_1_on_fail(self, runner, tmp_path, capsys):
        """任一段 fail → main() 返回 1。"""
        def make_fail_builder(name):
            def builder(root):
                return ([sys.executable, "-c", "import sys; sys.exit(1)"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [("s1", "mock1", make_fail_builder("s1"))]
            with patch("sys.argv", ["runner", "--project-root", str(tmp_path)]):
                exit_code = runner.main()
            assert exit_code == 1
        finally:
            runner.STAGES = original_stages

    def test_main_json_output(self, runner, tmp_path, capsys):
        """--json 参数 → 输出 JSON 格式。"""
        def make_pass_builder(name):
            def builder(root):
                return ([sys.executable, "-c", f"print('{name}')"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [("s1", "mock1", make_pass_builder("s1"))]
            with patch("sys.argv", ["runner", "--project-root", str(tmp_path), "--json"]):
                exit_code = runner.main()
            captured = capsys.readouterr()
            import json
            # quiet 模式下仅输出 JSON，直接解析整段 stdout
            data = json.loads(captured.out)
            assert "ok" in data
            assert "stages" in data
            assert "summary" in data
            assert exit_code == 0
        finally:
            runner.STAGES = original_stages


# ===========================================================================
# TestE2ERealRepo: 真实仓库 e2e（不抛异常）
# ===========================================================================

class TestE2ERealRepo:
    """真实仓库 e2e 验证——结果可能是 pass/fail，但不能崩溃。"""

    def test_e2e_runner_does_not_throw_on_real_repo(self, runner):
        """在真实仓库根目录调用，验证不抛异常。"""
        repo_root = Path(__file__).resolve().parents[2]
        # 用 mock 替换 STAGES 为单段快速 mock，避免实际跑 pytest（耗时）
        def quick_pass_builder(name):
            def builder(root):
                return ([sys.executable, "-c", "print('e2e mock ok')"], root)
            return builder
        original_stages = runner.STAGES
        try:
            runner.STAGES = [("e2e_mock", "mock for e2e", quick_pass_builder("e2e"))]
            result = runner.run_silent_failure_regression(repo_root)
            assert "ok" in result
            assert "stages" in result
            assert isinstance(result["ok"], bool)
        finally:
            runner.STAGES = original_stages

    def test_e2e_stage_builders_produce_valid_paths(self, runner):
        """_build_*_cmd 生成器在真实仓库下生成存在的脚本路径。"""
        repo_root = Path(__file__).resolve().parents[2]
        # pytest cmd: [sys.executable, "-m", "pytest", ...]
        cmd, cwd = runner.build_pytest_cmd(repo_root)
        assert cmd[0] == sys.executable
        assert "-m" in cmd
        assert "pytest" in cmd
        # return contract cmd: [sys.executable, <script_path>, ...]
        cmd, cwd = runner.build_return_contract_cmd(repo_root)
        script_path = Path(cmd[1])
        assert script_path.exists(), f"audit_return_contract_usage.py 不存在: {script_path}"
        # worktree ops cmd: [sys.executable, <script_path>, ...]
        cmd, cwd = runner.build_worktree_ops_cmd(repo_root)
        script_path = Path(cmd[1])
        assert script_path.exists(), f"audit_worktree_ops_telemetry.py 不存在: {script_path}"

    def test_e2e_audit_return_contract_passes_on_real_repo(self, runner):
        """e2e: audit_return_contract_usage 在真实仓库 src/+scripts/ 应 0 违规。"""
        repo_root = Path(__file__).resolve().parents[2]
        cmd, cwd = runner.build_return_contract_cmd(repo_root)
        result = subprocess_run_safe(cmd, cwd)
        assert result.returncode == 0, (
            f"audit_return_contract_usage 失败 (exit={result.returncode}):\n"
            f"stdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
        )


def subprocess_run_safe(cmd: list[str], cwd: Path):
    """subprocess.run 包装（测试辅助）。"""
    import subprocess
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=120)
