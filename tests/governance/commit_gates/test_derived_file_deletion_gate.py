# [A_test] module_id: MOD-GOV_derived_file_deletion_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_derived_file_deletion_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# [ARCH-BP-REGISTRY-DELETION-001] P1 治本——GATE-21 守护洞封堵 in-process gate 单测
"""test_derived_file_deletion_gate.py — 派生文件删除保护门禁单测（DERIVED-FILE-DELETION-PROTECTION）

权威依据：derived_file_deletion_gate.py（make_derived_file_deletion_gate）

测试组：
- TestNoDeletionPasses: 无 staged 删除 → passed=True
- TestProtectedDeletionBlocked: 暂存删除受保护派生文件（blueprint_registry.yaml）→ passed=False
- TestNonProtectedDeletionPasses: 暂存删除非保护文件 → passed=True
- TestEscapeHatchPasses: allow_derived_deletion=True 逃生通道放行
- TestGitDiffFailOpen: git diff returncode!=0 → fail-open（passed=True）
- TestGitDiffExceptionFailOpen: git diff 抛异常 → fail-open（passed=True）
- TestPathNormalization: 反斜杠路径归一化（Windows 兼容）
- TestGateSpecFields: gate_id / priority 字段正确
- TestAllProtectedFiles: 受保护清单全覆盖（blueprint_registry + path_ownership_map）
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.commit_gates.derived_file_deletion_gate import (
    _PROTECTED_DERIVED_FILES,
    make_derived_file_deletion_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec


def _make_gateway(
    project_root: Path,
    deleted_files_stdout: str = "",
    returncode: int = 0,
    raise_exc: Exception | None = None,
) -> MagicMock:
    """构造 mock gateway，模拟 run_git 返回 staged 删除清单。

    Args:
        project_root: 项目根目录。
        deleted_files_stdout: `git diff --cached --name-only --diff-filter=D` 的
            stdout（正斜杠相对路径，换行分隔）。
        returncode: git diff 的 returncode（非 0 触发 fail-open）。
        raise_exc: 若非 None，run_git 抛此异常（测试异常安全降级）。
    """
    gw = MagicMock()
    gw.project_root = project_root
    if raise_exc is not None:
        gw.run_git.side_effect = raise_exc
    else:
        result = MagicMock()
        result.returncode = returncode
        result.stdout = deleted_files_stdout
        gw.run_git.return_value = result
    return gw


class TestNoDeletionPasses:
    """无 staged 删除 → 放行。"""

    def test_empty_deletion_list_passes(self, tmp_path):
        """staged 删除清单为空 → passed=True。"""
        gw = _make_gateway(tmp_path, deleted_files_stdout="")
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["src/a.py"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is True
        assert detail == ""


class TestProtectedDeletionBlocked:
    """暂存删除受保护派生文件 → 阻断。"""

    def test_blueprint_registry_deletion_blocked(self, tmp_path):
        """暂存删除 blueprint_registry.yaml → passed=False（三次删除事故对象）。"""
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout="docs/03_modules/blueprint_registry.yaml\n",
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["docs/03_modules/blueprint_registry.yaml"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is False
        assert "DERIVED_FILE_DELETION_VIOLATION" in detail
        assert "blueprint_registry.yaml" in detail

    def test_path_ownership_map_deletion_blocked(self, tmp_path):
        """暂存删除 path_ownership_map.yaml → passed=False（5710 path claims）。"""
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout="docs/03_modules/path_ownership_map.yaml\n",
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["docs/03_modules/path_ownership_map.yaml"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is False
        assert "DERIVED_FILE_DELETION_VIOLATION" in detail
        assert "path_ownership_map.yaml" in detail

    def test_mixed_deletion_blocked_lists_only_protected(self, tmp_path):
        """多文件删除中含受保护文件 → 阻断，detail 仅列受保护文件。"""
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout=("src/old_module.py\ndocs/03_modules/blueprint_registry.yaml\ntests/test_old.py\n"),
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["src/old_module.py", "docs/03_modules/blueprint_registry.yaml"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is False
        assert "blueprint_registry.yaml" in detail
        # 非保护文件不在违规描述中
        assert "old_module.py" not in detail


class TestNonProtectedDeletionPasses:
    """暂存删除非保护文件 → 放行。"""

    def test_regular_file_deletion_passes(self, tmp_path):
        """暂存删除普通源文件 → passed=True（gate 只保护派生文件）。"""
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout="src/legacy/old_module.py\n",
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["src/legacy/old_module.py"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is True
        assert detail == ""


class TestEscapeHatchPasses:
    """allow_derived_deletion=True 逃生通道放行。"""

    def test_escape_hatch_passes_even_on_protected_deletion(self, tmp_path):
        """受保护文件删除 + allow_derived_deletion=True → 放行（P3 退库场景）。"""
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout="docs/03_modules/blueprint_registry.yaml\n",
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["docs/03_modules/blueprint_registry.yaml"],
            session_id="s1",
            allow_derived_deletion=True,
        )
        assert passed is True
        assert detail == ""


class TestGitDiffFailOpen:
    """git diff returncode!=0 → fail-open（不阻断 commit）。"""

    def test_nonzero_returncode_passes(self, tmp_path):
        """git diff 失败（rc=1）→ 降级为放行（治标不卡死工作流）。"""
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout="",
            returncode=1,
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["docs/03_modules/blueprint_registry.yaml"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is True
        assert detail == ""


class TestGitDiffExceptionFailOpen:
    """git diff 抛异常 → fail-open（不阻断 commit）。"""

    def test_exception_degrades_to_pass(self, tmp_path):
        """run_git 抛 RuntimeError → 降级为放行（检测器失效不卡死 commit）。"""
        gw = _make_gateway(
            tmp_path,
            raise_exc=RuntimeError("git binary not found"),
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["docs/03_modules/blueprint_registry.yaml"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is True
        assert detail == ""


class TestPathNormalization:
    """反斜杠路径归一化（Windows 兼容）。"""

    def test_backslash_paths_normalized(self, tmp_path):
        """git diff 输出反斜杠路径时仍能匹配受保护清单（正斜杠）。"""
        # 模拟 Windows git 输出反斜杠（罕见但需兼容）
        gw = _make_gateway(
            tmp_path,
            deleted_files_stdout="docs\\03_modules\\blueprint_registry.yaml\n",
        )
        gate = make_derived_file_deletion_gate()
        passed, detail = gate.check(
            gw,
            ["docs/03_modules/blueprint_registry.yaml"],
            session_id="s1",
            allow_derived_deletion=False,
        )
        assert passed is False
        assert "blueprint_registry.yaml" in detail


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        """返回的 GateSpec 字段符合约定。"""
        spec = make_derived_file_deletion_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "DERIVED-FILE-DELETION-PROTECTION"
        assert spec.priority == 46  # FOREIGN-CHANGE(45) 后、HELD-OVERLAP(50) 前


class TestAllProtectedFiles:
    """受保护清单全覆盖——每个登记文件都能被拦截。"""

    def test_every_protected_file_is_blocked(self, tmp_path):
        """_PROTECTED_DERIVED_FILES 中每个文件删除都被阻断。"""
        gate = make_derived_file_deletion_gate()
        for protected in _PROTECTED_DERIVED_FILES:
            gw = _make_gateway(
                tmp_path,
                deleted_files_stdout=protected + "\n",
            )
            passed, detail = gate.check(
                gw,
                [protected],
                session_id="s1",
                allow_derived_deletion=False,
            )
            assert passed is False, f"受保护文件 {protected} 删除未被拦截"
            assert protected in detail

    def test_protected_list_contains_known_victims(self):
        """受保护清单包含已知删除受害者。"""
        assert "docs/03_modules/blueprint_registry.yaml" in _PROTECTED_DERIVED_FILES
        assert "docs/03_modules/path_ownership_map.yaml" in _PROTECTED_DERIVED_FILES
