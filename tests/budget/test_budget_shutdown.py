# [A_test] module_id: SRC-TST-0447 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §2.28-2.30
# [MODULE] tests.test_budget_shutdown
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_budget_shutdown.py
# [TTL] task_bound

"""DM-201504: F4 BudgetEngine自动关闭——shutdown资源清理+状态持久化+session_shutdown钩子。

测试内容:
1. shutdown() 状态持久化（写入 data/budget/shutdown_snapshot.json）
2. shutdown() 资源清理（IPI/Spiral/gate_history 清空）
3. shutdown() 单例重置
4. shutdown() 幂等性
5. session_shutdown_budget_close 钩子注册
6. session_shutdown 钩子调用 shutdown()
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.ops_governance.budget_engine import BudgetEngine


@pytest.fixture
def engine():
    """提供干净的 BudgetEngine 实例。"""
    BudgetEngine._instance = None
    e = BudgetEngine()
    yield e
    BudgetEngine._instance = None


class TestShutdown:
    def test_shutdown_persists_state(self, engine, tmp_path):
        """shutdown() 应将快照持久化到文件。"""
        persist_path = tmp_path / "shutdown_snapshot.json"
        with patch("os.path.join", return_value=str(persist_path)):
            result = engine.shutdown()

        assert result["cleaned_up"] is True
        assert "snapshot" in result
        assert Path(persist_path).exists()

        with open(persist_path, encoding="utf-8") as f:
            saved = json.load(f)
        assert "consumption" in saved
        assert "health" in saved

    def test_shutdown_cleans_up_resources(self, engine):
        """shutdown() 应清理 IPI/Spiral/gate_history。"""
        from zephyr.governance.security_governance.ipi_defense import IPIDefense
        from zephyr.gov_drift.spiral_ews import SpiralEarlyWarningSystem

        engine._ipi_defense = IPIDefense()
        engine._spiral_ews = SpiralEarlyWarningSystem()
        engine._gate_history.append(MagicMock())

        assert engine._ipi_defense is not None
        assert engine._spiral_ews is not None
        assert len(engine._gate_history) > 0

        engine.shutdown()

        assert engine._ipi_defense is None
        assert engine._spiral_ews is None
        assert len(engine._gate_history) == 0

    def test_shutdown_resets_singleton(self, engine):
        """shutdown() 应重置单例 _instance。"""
        BudgetEngine._instance = engine
        assert BudgetEngine._instance is not None

        engine.shutdown()

        assert BudgetEngine._instance is None

    def test_shutdown_is_idempotent(self, engine):
        """shutdown() 重复调用不应抛异常。"""
        result1 = engine.shutdown()
        assert result1["cleaned_up"] is True

        result2 = engine.shutdown()
        assert result2["cleaned_up"] is True

    def test_shutdown_returns_snapshot(self, engine):
        """shutdown() 返回值应包含快照。"""
        result = engine.shutdown()

        assert "snapshot" in result
        snapshot = result["snapshot"]
        assert "consumption" in snapshot
        assert "degradation_level" in snapshot
        assert "health" in snapshot

    def test_shutdown_after_consumption(self, engine):
        """在有消费记录后 shutdown() 应正确持久化。"""
        from zephyr.governance.ops_governance.budget_models import BudgetDimension

        token_policy = engine.get_active_policy(BudgetDimension.TOKEN)
        engine.record_consumption(token_policy.policy_id, 5000, 0.05, 0.5)

        result = engine.shutdown()
        snapshot = result["snapshot"]

        consumption = snapshot["consumption"]
        assert token_policy.policy_id in consumption
        assert consumption[token_policy.policy_id]["daily"] == 5000


class TestSessionShutdownHook:
    def test_session_shutdown_hook_registered(self):
        """验证 session_shutdown_budget_close 钩子已注册。"""
        BudgetEngine._instance = None

        mock_registry = MagicMock()
        captured = {}

        def _capture(callback, *, priority=0, name=None):
            captured[name] = callback

        mock_registry.register.side_effect = _capture

        hook_path = "zephyr.governance.ops_governance.event_hook.hook_registry"
        task_repo_path = "zephyr.governance.persistence.task_repo.TaskRepository"

        with patch(hook_path, mock_registry), patch(task_repo_path, create=True):
            from zephyr.trading.boot_hooks import register_boot_hooks

            register_boot_hooks()

        assert "session_shutdown_budget_close" in captured
        BudgetEngine._instance = None

    def test_session_shutdown_hook_calls_shutdown(self):
        """session_shutdown 钩子应调用 BudgetEngine.shutdown()。"""
        BudgetEngine._instance = None

        mock_registry = MagicMock()
        captured = {}

        def _capture(callback, *, priority=0, name=None):
            captured[name] = callback

        mock_registry.register.side_effect = _capture

        hook_path = "zephyr.governance.ops_governance.event_hook.hook_registry"
        task_repo_path = "zephyr.governance.persistence.task_repo.TaskRepository"

        with patch(hook_path, mock_registry), patch(task_repo_path, create=True):
            from zephyr.trading.boot_hooks import register_boot_hooks

            register_boot_hooks()

        cb = captured.get("session_shutdown_budget_close")
        assert cb is not None

        engine = BudgetEngine.ensure_initialized()
        assert BudgetEngine._instance is not None

        event = MagicMock()
        cb(event)

        assert BudgetEngine._instance is None
        BudgetEngine._instance = None

    def test_session_shutdown_hook_safe_when_no_instance(self):
        """无单例时 session_shutdown 钩子应安全跳过。"""
        BudgetEngine._instance = None

        mock_registry = MagicMock()
        captured = {}

        def _capture(callback, *, priority=0, name=None):
            captured[name] = callback

        mock_registry.register.side_effect = _capture

        hook_path = "zephyr.governance.ops_governance.event_hook.hook_registry"
        task_repo_path = "zephyr.governance.persistence.task_repo.TaskRepository"

        with patch(hook_path, mock_registry), patch(task_repo_path, create=True):
            from zephyr.trading.boot_hooks import register_boot_hooks

            register_boot_hooks()

        cb = captured.get("session_shutdown_budget_close")
        assert cb is not None

        event = MagicMock()
        cb(event)

        assert BudgetEngine._instance is None
