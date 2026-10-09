# [A_test] module_id: MOD-GOV_FOLDER_CAPACITY_HARD_LIMIT_GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.commit_gates.test_folder_capacity_hard_limit_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=TEST-MOD-GATE_ENGINE-TEST_FOLDER_CAPACITY_HARD_LI | layer=module | stability=stable | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_folder_capacity_hard_limit_gate.py — FOLDER-CAPACITY-HARD-LIMIT 门禁单测

权威依据：folder_capacity_hard_limit_gate.py（make_folder_capacity_hard_limit_gate）

测试组：
- TestDepthPredicate: tests 豁免收窄判定矩阵（一级豁免、二级受限；嵌套 tests 段；
  反斜杠路径；非 tests 文件恒不豁免）
- TestCountFlatFiles: 平铺计数口径（排 __init__.py/隐藏文件/子目录）
- TestScanViolations: 超限目录检出与消息（>120 阻断面/≤120 放行面/同目录去重）
- TestFailOpen: git diff 不可达 fail-open（返回空清单不抛异常）
"""

from __future__ import annotations

from types import SimpleNamespace

from zephyr.gov_enforcement.commit_gates.folder_capacity_hard_limit_gate import (
    _HARD_LIMIT,
    _collect_staged_trigger_files,
    _count_flat_files,
    _scan_violations,
    _tests_depth_exceeded,
    make_folder_capacity_hard_limit_gate,
)


class TestDepthPredicate:
    """tests/ 豁免收窄（Owner 批"一级豁免、二级受限"）：相对最右 tests 段深度。"""

    def test_root_scattered_file_exempt(self) -> None:
        # tests/ 根散文件：深度 0，豁免
        assert _tests_depth_exceeded("tests/a.py") is False

    def test_first_level_exempt(self) -> None:
        # 一级平铺（tests/<dir>/a.py）：深度 1，豁免
        assert _tests_depth_exceeded("tests/governance/x.py") is False

    def test_second_level_restricted(self) -> None:
        # 二级平铺（tests/<dir>/<sub>/a.py）：深度 2，受限
        assert _tests_depth_exceeded("tests/governance/commit_gates/x.py") is True

    def test_deep_path_restricted(self) -> None:
        assert _tests_depth_exceeded("tests/a/b/c/d.py") is True

    def test_non_test_file_never_exempt(self) -> None:
        # 非 tests 文件：恒不豁免（与原 is_test_exempt=False 语义一致）
        assert _tests_depth_exceeded("src/zephyr/x.py") is True

    def test_nested_tests_root_and_first_level(self) -> None:
        # 嵌套 tests 段（scripts/tests/）：同口径按相对深度判
        assert _tests_depth_exceeded("scripts/tests/a.py") is False
        assert _tests_depth_exceeded("scripts/tests/a/b.py") is False

    def test_nested_tests_second_level(self) -> None:
        assert _tests_depth_exceeded("scripts/tests/a/b/c.py") is True

    def test_backslash_path_normalized(self) -> None:
        # Windows 反斜杠路径归一化后判定：一级=豁免，二级=受限
        assert _tests_depth_exceeded("tests\\a.py") is False
        assert _tests_depth_exceeded("tests\\a\\b.py") is False
        assert _tests_depth_exceeded("tests\\a\\b\\c.py") is True

    def test_space_in_dir_name(self) -> None:
        assert _tests_depth_exceeded("tests/a b/x.py") is False

    def test_non_trigger_extension_untouched_by_predicate(self) -> None:
        # 谓词只管豁免判定；扩展名过滤在调用方（此处验证组合语义入口恒量）
        assert _HARD_LIMIT == 120


class TestCountFlatFiles:
    """平铺计数口径：排 __init__.py、隐藏文件、子目录内文件。"""

    def test_excludes_init_hidden_and_subdirs(self, tmp_path) -> None:
        (tmp_path / "__init__.py").touch()
        (tmp_path / ".hidden.cfg").touch()
        (tmp_path / "a.py").touch()
        (tmp_path / "b.md").touch()
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.py").touch()
        assert _count_flat_files(str(tmp_path)) == 2

    def test_missing_dir_returns_zero(self, tmp_path) -> None:
        assert _count_flat_files(str(tmp_path / "nope")) == 0


class _FakeGateway:
    """最小 gateway 桩：project_root + run_git 返回可控。"""

    def __init__(self, project_root, run_git_result=None) -> None:
        self.project_root = project_root
        self._run_git_result = run_git_result

    def run_git(self, cmd: list[str]):
        return self._run_git_result


class TestScanViolations:
    """超限目录检出：>120 出违规消息；≤120 放行；同目录去重。"""

    def test_over_limit_detected(self, tmp_path) -> None:
        big = tmp_path / "tests" / "gov" / "deep"
        big.mkdir(parents=True)
        for i in range(_HARD_LIMIT + 1):
            (big / f"f{i:03d}.py").touch()
        gw = _FakeGateway(project_root=tmp_path)
        violations = _scan_violations(gw, ["tests/gov/deep/f000.py"])
        assert len(violations) == 1
        assert "tests/gov/deep" in violations[0]
        assert str(_HARD_LIMIT + 1) in violations[0]

    def test_at_limit_passes(self, tmp_path) -> None:
        ok = tmp_path / "tests" / "gov" / "ok"
        ok.mkdir(parents=True)
        for i in range(_HARD_LIMIT):
            (ok / f"f{i:03d}.py").touch()
        gw = _FakeGateway(project_root=tmp_path)
        assert _scan_violations(gw, ["tests/gov/ok/f000.py"]) == []

    def test_same_dir_checked_once(self, tmp_path) -> None:
        big = tmp_path / "pkg"
        big.mkdir()
        for i in range(_HARD_LIMIT + 5):
            (big / f"f{i:03d}.py").touch()
        gw = _FakeGateway(project_root=tmp_path)
        violations = _scan_violations(gw, ["pkg/f000.py", "pkg/f001.py", "pkg/f002.py"])
        assert len(violations) == 1

    def test_root_level_file_skipped(self, tmp_path) -> None:
        gw = _FakeGateway(project_root=tmp_path)
        assert _scan_violations(gw, ["readme.md"]) == []


class TestFailOpen:
    """git diff 不可达 → 空清单不抛异常（fail-open 语义不回归）。"""

    def test_diff_failure_returns_empty(self) -> None:
        gw = _FakeGateway(
            project_root=".",
            run_git_result=SimpleNamespace(returncode=128, stdout=""),
        )
        assert _collect_staged_trigger_files(gw) == []


class TestGateSpecFields:
    def test_gate_identity(self) -> None:
        spec = make_folder_capacity_hard_limit_gate()
        assert spec.gate_id == "FOLDER-CAPACITY-HARD-LIMIT"
        assert spec.priority == 112
