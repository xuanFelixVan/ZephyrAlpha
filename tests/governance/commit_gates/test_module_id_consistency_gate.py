# [A_test] module_id: SRC-TST-2141 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-module_id_consistency_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] tests.governance.commit_gates.test_module_id_consistency_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_module_id_consistency_gate.py — module_id 三声明轨道一致性 + count 派生 + 跨文件唯一性门禁单测

权威依据：module_id_consistency_gate.py（make_module_id_consistency_gate）

测试组：
- TestTripleDeclarationConsistency: 三声明轨道一致性（CFG/MOD/rule）单文件校验
- TestCountDerivation: total_registered/total_templates/total_dependencies count 派生
- TestCrossFileUniqueness: 跨文件 module_id 唯一性（git grep 全仓检测）
- TestGateSpecFields: gate_id / priority 字段正确
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.governance.commit_gates.module_id_consistency_gate import (
    make_module_id_consistency_gate,
)

# registry 在 project_root 下的相对路径（对标 module_id_consistency_gate._REGISTRY_REL）
_REGISTRY_REL = "architecture_model/module_id_registry.yaml"
_TEMPLATE_REGISTRY_REL = "docs/03_modules/template_registry.yaml"
_DEP_REGISTRY_REL = (
    "docs/01_policies_and_standards/_registry/catalogs/"
    "cross_module_dependency_registry.yaml"
)


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway，仅需 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


# ============================================================
# TestTripleDeclarationConsistency: 三声明轨道一致性校验
# ============================================================


class TestTripleDeclarationConsistency:
    """三声明轨道一致性（CFG/MOD/rule）单文件校验。"""

    def test_triple_declaration_consistent_passes(self, tmp_path):
        """三声明轨道一致（CFG+MOD+rule）→ 通过。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "# module_id: MOD-REG-001\n"
            "module_id: REG-REG-001\n"
            "total_registered: 0\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"应通过，但: {detail}"

    def test_incomplete_tracks_blocked(self, tmp_path):
        """仅 CFG 头（1/3 轨）→ 阻断 incomplete_tracks。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "total_registered: 0\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "incomplete_tracks" in detail

    def test_two_tracks_passes(self, tmp_path):
        """两轨一致（CFG+MOD，无 rule）→ 通过（tracks_found=2 不 < 2）。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "# module_id: MOD-REG-001\n"
            "total_registered: 0\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"两轨应通过，但: {detail}"

    def test_non_registry_file_skipped(self, tmp_path):
        """非 registry 的 .yaml 文件 → 跳过三声明轨道校验（通过）。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "some_other.yaml"
        target.write_text(
            "# [A_config] module_id=CFG-X-001\n"
            "total_registered: 0\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed


# ============================================================
# TestCountDerivation: count 派生校验
# ============================================================


class TestCountDerivation:
    """total_registered/total_templates/total_dependencies count 派生。"""

    def test_count_match_passes(self, tmp_path):
        """total_registered 与实际条目数匹配 → 通过。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "# module_id: MOD-REG-001\n"
            "module_id: REG-REG-001\n"
            "total_registered: 2\n"
            "entries:\n"
            "  - module_id: MOD-001\n"
            "  - module_id: MOD-002\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"count 匹配应通过，但: {detail}"

    def test_count_mismatch_blocked(self, tmp_path):
        """total_registered 与实际条目数不匹配 → 阻断 count_mismatch。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "# module_id: MOD-REG-001\n"
            "module_id: REG-REG-001\n"
            "total_registered: 5\n"
            "entries:\n"
            "  - module_id: MOD-001\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "count_mismatch" in detail
        assert "5" in detail
        assert "1" in detail

    def test_no_total_declared_passes(self, tmp_path):
        """无 total_registered 声明 → 跳过 count 校验（通过）。"""
        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "# module_id: MOD-REG-001\n"
            "module_id: REG-REG-001\n"
            "entries:\n"
            "  - module_id: MOD-001\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"无 total 声明应通过，但: {detail}"


# ============================================================
# TestCrossFileUniqueness: 跨文件 module_id 唯一性
# ============================================================


class TestCrossFileUniqueness:
    """跨文件 module_id 唯一性（git grep 全仓检测）。

    需要 mock _is_tracked_in_head（历史豁免）和 subprocess.run（git grep）。
    """

    def test_collision_blocked(self, tmp_path, monkeypatch):
        """新增文件（不在 HEAD），module_id 被其他文件声明 → 阻断。"""
        import zephyr.governance.commit_gates.module_id_consistency_gate as mod

        # mock: 文件不在 HEAD（新增文件 A）
        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda rel, pr: False)

        # mock: git grep 返回两个文件（含当前文件）
        class _FakeResult:
            returncode = 0
            stdout = (
                "tests/fake/test_current.py\n"
                "tests/other/test_other.py\n"
            )

        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **kw: _FakeResult())

        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_current.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-9999 | layer=test\n"
            "x = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "module_id_collision" in detail
        assert "SRC-TST-9999" in detail
        assert "test_other.py" in detail

    def test_unique_passes(self, tmp_path, monkeypatch):
        """新增文件（不在 HEAD），module_id 唯一 → 通过。"""
        import zephyr.governance.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda rel, pr: False)

        # mock: git grep 无匹配（returncode=1）
        class _FakeResult:
            returncode = 1
            stdout = ""

        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **kw: _FakeResult())

        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_unique.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-8888 | layer=test\n"
            "x = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"唯一 module_id 应通过，但: {detail}"

    def test_tracked_file_exempt(self, tmp_path, monkeypatch):
        """已跟踪文件（在 HEAD，M 状态）→ 跳过碰撞检查（通过）。"""
        import zephyr.governance.commit_gates.module_id_consistency_gate as mod

        # mock: 文件在 HEAD（修改文件 M）→ 历史豁免
        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda rel, pr: True)

        # 即使 git grep 会返回碰撞，也不应触发（因为已跳过）
        call_count = {"n": 0}

        class _FakeResult:
            returncode = 0
            stdout = "tests/other/test_other.py\n"

        def _counting_run(*a, **kw):
            call_count["n"] += 1
            return _FakeResult()

        monkeypatch.setattr(mod.subprocess, "run", _counting_run)

        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_tracked.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-7777 | layer=test\n"
            "x = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"已跟踪文件应豁免，但: {detail}"
        # git grep 不应被调用（_is_tracked_in_head 返回 True 时 continue）
        assert call_count["n"] == 0

    def test_no_module_id_header_skipped(self, tmp_path, monkeypatch):
        """无 [A_*] module_id 头的 .py 文件 → 跳过碰撞检查（通过）。"""
        import zephyr.governance.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda rel, pr: False)

        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_no_header.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# plain comment\n"
            "x = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed

    def test_git_grep_error_fail_open(self, tmp_path, monkeypatch):
        """git grep 超时/异常 → fail-open（通过）。"""
        import subprocess as _sp

        import zephyr.governance.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda rel, pr: False)

        def _raising_run(*a, **kw):
            raise _sp.TimeoutExpired(cmd=a[0] if a else "git", timeout=10)

        monkeypatch.setattr(mod.subprocess, "run", _raising_run)

        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_timeout.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-6666 | layer=test\n"
            "x = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"git grep 异常应 fail-open，但: {detail}"


# ============================================================
# TestGateSpecFields: gate 字段正确
# ============================================================


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id(self):
        gate = make_module_id_consistency_gate()
        assert gate.gate_id == "MODULE-ID-CONSISTENCY"

    def test_priority(self):
        gate = make_module_id_consistency_gate()
        assert gate.priority == 88
