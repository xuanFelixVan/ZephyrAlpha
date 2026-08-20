# [A_test] module_id: MOD-GOV_module_id_consistency_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_MODULE_ID_CONSISTENCY_GATE | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] tests.governance.commit_gates.test_module_id_consistency_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_MODULE_ID_CONSISTENCY_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

from zephyr.gov_enforcement.commit_gates.module_id_consistency_gate import (
    make_module_id_consistency_gate,
)

# registry 在 project_root 下的相对路径（对标 module_id_consistency_gate._REGISTRY_REL）
_REGISTRY_REL = "architecture_model/module_id_registry.yaml"
_TEMPLATE_REGISTRY_REL = "docs/03_modules/template_registry.yaml"
_DEP_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml"


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
            "# [A_config] module_id=CFG-REG-001\ntotal_registered: 0\n",
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
            "# [A_config] module_id=CFG-REG-001\n# module_id: MOD-REG-001\ntotal_registered: 0\n",
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
            "# [A_config] module_id=CFG-X-001\ntotal_registered: 0\n",
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
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        # mock: 文件不在 HEAD（新增文件 A）
        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)

        # mock: git grep 返回两个文件（含当前文件）
        class _FakeResult:
            returncode = 0
            stdout = "tests/fake/test_current.py\ntests/other/test_other.py\n"

        gw.run_git.return_value = _FakeResult()
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_current.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-9999 | layer=test\nx = 1\n",
            encoding="utf-8",
        )
        # 候选文件也声明相同 module_id（精确验证治本：必须 [A_*] 头声明才算碰撞）
        other = tmp_path / "tests/other/test_other.py"
        other.parent.mkdir(parents=True, exist_ok=True)
        other.write_text(
            "# [A_test] module_id: SRC-TST-9999 | layer=test\ny = 2\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "module_id_collision" in detail
        assert "SRC-TST-9999" in detail
        assert "test_other.py" in detail

    def test_blueprint_reference_not_collision(self, tmp_path, monkeypatch):
        """test 文件 [BLUEPRINT] 引用源模块 id → 不算碰撞（精确验证治本 ARCH-TTL-DOC-001）。

        场景：test 文件按约定在 [BLUEPRINT] 头引用源模块的 module_id（如
        MOD-GOV-xxx），但 [A_test] 头声明自己的 SRC-TST-NNNN。git grep -F
        纯文本搜索会匹配 [BLUEPRINT] 引用，但精确验证应排除——[BLUEPRINT]
        是引用不是声明。
        """
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)

        # mock: git grep 返回源文件（含 [BLUEPRINT] 引用，但 [A_module] 声明不同 id）
        class _FakeResult:
            returncode = 0
            stdout = "tests/fake/test_current.py\nsrc/zephyr/gov_enforcement/commit_gates/fake_gate.py\n"

        gw.run_git.return_value = _FakeResult()
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_current.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-9999 | layer=test\n"
            "# [BLUEPRINT] MOD-GOV-fake_gate | docs/...md | §0.1\n"
            "x = 1\n",
            encoding="utf-8",
        )
        # 源文件：[A_module] 声明 MOD-GOV-fake_gate（≠ SRC-TST-9999），
        # [BLUEPRINT] 也引用 MOD-GOV-fake_gate（与 test 文件 [BLUEPRINT] 一致）
        source = tmp_path / "src/zephyr/gov_enforcement/commit_gates/fake_gate.py"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "# [BLUEPRINT] MOD-GOV-fake_gate | docs/...md | §0.1\n"
            "# [A_module] module_id=MOD-GOV-fake_gate | layer=module\n"
            "z = 3\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"[BLUEPRINT] 引用不应触发碰撞，但: {detail}"

    def test_same_blueprint_same_module_id_not_collision(self, tmp_path, monkeypatch):
        """同 [BLUEPRINT] 的多文件共享 module_id → 非碰撞（同模块预期行为）。

        场景：MOD-GATE_ENGINE 模块下 20+ gate 文件均声明 module_id=MOD-GATE_ENGINE，
        且均引用 [BLUEPRINT] MOD-GATE_ENGINE。新增文件属于同模块 → 不应阻断。
        治本（2026-08-03, #ARCH-GATE-COLLISION-SAME-MODULE）：原 collision check
        不区分同模块/跨模块，误阻断同模块新文件入库。
        """
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)

        # mock: git grep 返回新文件 + 已有同模块文件
        class _FakeResult:
            returncode = 0
            stdout = (
                "src/zephyr/gov_enforcement/commit_gates/new_gate.py\n"
                "src/zephyr/gov_enforcement/commit_gates/existing_gate.py\n"
            )

        gw.run_git.return_value = _FakeResult()
        gate = make_module_id_consistency_gate()
        target = tmp_path / "src/zephyr/gov_enforcement/commit_gates/new_gate.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1\n"
            "# [A_module] module_id=MOD-GATE_ENGINE | layer=module\n"
            "x = 1\n",
            encoding="utf-8",
        )
        # 已有文件：同 [BLUEPRINT] + 同 [A_module] module_id → 同模块，非碰撞
        existing = tmp_path / "src/zephyr/gov_enforcement/commit_gates/existing_gate.py"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text(
            "# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1\n"
            "# [A_module] module_id=MOD-GATE_ENGINE | layer=module\n"
            "y = 2\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"同 [BLUEPRINT] 同 module_id 应非碰撞，但: {detail}"

    def test_different_blueprint_same_module_id_collision(self, tmp_path, monkeypatch):
        """不同 [BLUEPRINT] 但相同 module_id → 真碰撞（阻断）。

        场景：文件 A 引用 [BLUEPRINT] MOD-FOO 声明 module_id=MOD-FOO，
        文件 B 引用 [BLUEPRINT] MOD-BAR 也声明 module_id=MOD-FOO → 真碰撞。
        """
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)

        class _FakeResult:
            returncode = 0
            stdout = "src/new_file.py\nsrc/colliding_file.py\n"

        gw.run_git.return_value = _FakeResult()
        gate = make_module_id_consistency_gate()
        target = tmp_path / "src/new_file.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [BLUEPRINT] MOD-FOO | docs/foo.md | §0.1\n# [A_module] module_id=MOD-FOO | layer=module\nx = 1\n",
            encoding="utf-8",
        )
        # 碰撞文件：不同 [BLUEPRINT] 但相同 [A_module] module_id → 真碰撞
        colliding = tmp_path / "src/colliding_file.py"
        colliding.parent.mkdir(parents=True, exist_ok=True)
        colliding.write_text(
            "# [BLUEPRINT] MOD-BAR | docs/bar.md | §0.1\n# [A_module] module_id=MOD-FOO | layer=module\ny = 2\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "module_id_collision" in detail
        assert "MOD-FOO" in detail

    def test_unique_passes(self, tmp_path, monkeypatch):
        """新增文件（不在 HEAD），module_id 唯一 → 通过。"""
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)

        # mock: git grep 无匹配（returncode=1）
        class _FakeResult:
            returncode = 1
            stdout = ""

        gw.run_git.return_value = _FakeResult()
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_unique.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-8888 | layer=test\nx = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"唯一 module_id 应通过，但: {detail}"

    def test_tracked_file_exempt(self, tmp_path, monkeypatch):
        """已跟踪文件（在 HEAD，M 状态）→ 跳过碰撞检查（通过）。"""
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        # mock: 文件在 HEAD（修改文件 M）→ 历史豁免
        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: True)

        gw = _make_gateway(tmp_path)

        # 即使 git grep 会返回碰撞，也不应触发（因为已跳过）
        call_count = {"n": 0}

        class _FakeResult:
            returncode = 0
            stdout = "tests/other/test_other.py\n"

        def _counting_run(*a, **kw):
            call_count["n"] += 1
            return _FakeResult()

        gw.run_git.side_effect = _counting_run
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_tracked.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-7777 | layer=test\nx = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed, f"已跟踪文件应豁免，但: {detail}"
        # git grep 不应被调用（_is_tracked_in_head 返回 True 时 continue）
        assert call_count["n"] == 0

    def test_no_module_id_header_skipped(self, tmp_path, monkeypatch):
        """无 [A_*] module_id 头的 .py 文件 → 跳过碰撞检查（通过）。"""
        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_no_header.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# plain comment\nx = 1\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed

    def test_git_grep_error_fail_open(self, tmp_path, monkeypatch):
        """git grep 超时/异常 → fail-open（通过）。"""
        import subprocess as _sp

        import zephyr.gov_enforcement.commit_gates.module_id_consistency_gate as mod

        monkeypatch.setattr(mod, "_is_tracked_in_head", lambda gateway, rel: False)

        gw = _make_gateway(tmp_path)

        def _raising_run(*a, **kw):
            raise _sp.TimeoutExpired(cmd=a[0] if a else "git", timeout=10)

        gw.run_git.side_effect = _raising_run
        gate = make_module_id_consistency_gate()
        target = tmp_path / "tests/fake/test_timeout.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# [A_test] module_id: SRC-TST-6666 | layer=test\nx = 1\n",
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
