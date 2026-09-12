# [A_test] module_id: MOD-GOV_audit_self_healer_e2e | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §test
# [MODULE] tests.test_audit_self_healer_e2e
# [INVARIANTS] tmp_path隔离; rollback_handler注入; 禁止修改项目文件
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

_mod = pytest.importorskip("zephyr.governance.semantic_audit.self_healer")
SelfHealer = _mod.SelfHealer
HealResult = _mod.HealResult


class _InMemoryRollbackHandler:
    def __init__(self) -> None:
        self._snapshots: dict[str, str] = {}

    def checkpoint(self, target_path: str) -> bool:
        try:
            with open(target_path, encoding="utf-8") as f:
                self._snapshots[target_path] = f.read()
            return True
        except OSError:
            return False

    def restore(self, target_path: str) -> bool:
        content = self._snapshots.get(target_path)
        if content is None:
            return False
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError:
            return False


@pytest.mark.e2e
class TestSelfHealerE2E:
    def test_heal_fixes_syntax_error(self, tmp_path):
        """端到端：创建一个有语法错误的Python文件→heal修复→验证修复成功"""
        broken = tmp_path / "broken.py"
        broken.write_text("def foo()\n    pass\n", encoding="utf-8")

        fixed_content = "def foo():\n    pass\n"
        healer = SelfHealer()
        result = healer.heal(
            str(broken),
            issue_description="缺少冒号",
            fix_suggestion=fixed_content,
        )

        assert result.success is True
        assert broken.read_text(encoding="utf-8") == fixed_content

    def test_heal_rollback_on_failure(self, tmp_path):
        """端到端：修复失败时自动回滚"""
        target = tmp_path / "valid.py"
        original = "def hello():\n    print('hello')\n"
        target.write_text(original, encoding="utf-8")

        bad_fix = "def hello(\n    print('broken'\n"
        rollback_handler = _InMemoryRollbackHandler()
        healer = SelfHealer(rollback_handler=rollback_handler)
        result = healer.heal(
            str(target),
            issue_description="故意注入无效修复",
            fix_suggestion=bad_fix,
        )

        assert result.success is False
        assert result.rollback_applied is True
        assert target.read_text(encoding="utf-8") == original

    def test_heal_refuses_frozen_file(self, tmp_path):
        """端到端：拒绝修改[STABILITY]=frozen的文件"""
        frozen = tmp_path / "frozen_module.py"
        frozen.write_text(
            "[STABILITY] frozen\ndef critical():\n    pass\n",
            encoding="utf-8",
        )

        healer = SelfHealer()
        result = healer.heal(
            str(frozen),
            issue_description="尝试修改冻结文件",
            fix_suggestion="def critical():\n    return 42\n",
        )

        assert result.success is False
        assert "frozen" in result.reason

    def test_heal_refuses_immutable_core(self, tmp_path):
        """端到端：拒绝修改[AI_AUTONOMY]=immutable_core的文件"""
        immutable = tmp_path / "immutable_core.py"
        immutable.write_text(
            "[AI_AUTONOMY] immutable_core\ndef core():\n    pass\n",
            encoding="utf-8",
        )

        healer = SelfHealer()
        result = healer.heal(
            str(immutable),
            issue_description="尝试修改不可变核心",
            fix_suggestion="def core():\n    return 1\n",
        )

        assert result.success is False
        assert "immutable_core" in result.reason

    def test_batch_heal(self, tmp_path):
        """端到端：批量修复多个文件"""
        file_a = tmp_path / "a.py"
        file_a.write_text("def a()\n    pass\n", encoding="utf-8")

        file_b = tmp_path / "b.py"
        file_b.write_text(
            "[STABILITY] frozen\ndef b():\n    pass\n",
            encoding="utf-8",
        )

        file_c = tmp_path / "c.py"
        file_c.write_text("def c()\n    pass\n", encoding="utf-8")

        healer = SelfHealer()
        issues = [
            {
                "target_path": str(file_a),
                "issue_description": "缺少冒号",
                "fix_suggestion": "def a():\n    pass\n",
            },
            {
                "target_path": str(file_b),
                "issue_description": "尝试修改冻结文件",
                "fix_suggestion": "def b():\n    return 1\n",
            },
            {
                "target_path": str(file_c),
                "issue_description": "缺少冒号",
                "fix_suggestion": "def c():\n    pass\n",
            },
        ]
        results = healer.batch_heal(issues)

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert "frozen" in results[1].reason
        assert results[2].success is True
