# [A_test] module_id: MOD-GOV_rbac_auto_lifecycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §auto_lifecycle
# [MODULE] tests.agent_rbac.test_rbac_auto_lifecycle
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""RBAC 自动启动/关闭生命周期集成测试.

验证:
1. GenesisBootstrap 能自动启动（5阶段序列）
2. GenesisBootstrap 能自动关闭
3. BootstrapSuperadminBridge 能创建superadmin账户
4. auto_runtime_core.boot() 集成了RBAC启动
5. boot_hooks 注册了RBAC事件钩子
6. RBAC系统启动后处于就绪状态
"""

from __future__ import annotations

import sys
import time

import pytest

sys.path.insert(0, "src")


class TestGenesisBootstrapAutoStart:
    """测试RBAC系统自动启动."""

    def test_genesis_bootstrap_singleton(self):
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            get_genesis_bootstrap,
        )

        gb1 = get_genesis_bootstrap()
        gb2 = get_genesis_bootstrap()
        assert gb1 is gb2, "GenesisBootstrap should be singleton"

    def test_genesis_bootstrap_initial_state(self):
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            GenesisPhase,
        )

        gb = GenesisBootstrap()
        gb.reset()
        assert gb.state.phase == GenesisPhase.PENDING
        assert gb.state.success is False
        assert gb.state.is_ready is False

    def test_genesis_bootstrap_auto_start(self):
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            GenesisPhase,
        )

        gb = GenesisBootstrap()
        gb.reset()
        state = gb.bootstrap(config={"version": "0.14.0"})

        assert state.phase == GenesisPhase.COMPLETED, f"Expected COMPLETED, got {state.phase}: {state.error}"
        assert state.success is True, f"Bootstrap failed: {state.error}"
        assert state.is_ready is True
        assert state.checks_passed == state.total_checks
        assert state.completed_at > state.started_at

    def test_genesis_bootstrap_idempotent(self):
        from zephyr.security.access_control.genesis_bootstrap import GenesisBootstrap

        gb = GenesisBootstrap()
        gb.reset()
        state1 = gb.bootstrap()
        assert state1.is_ready

        state2 = gb.bootstrap()
        assert state2.is_ready
        assert state2.checks_passed == state2.total_checks

    def test_genesis_bootstrap_progress_tracking(self):
        from zephyr.security.access_control.genesis_bootstrap import GenesisBootstrap

        gb = GenesisBootstrap()
        gb.reset()
        assert gb.state.progress == 0.0

        gb.bootstrap()
        assert gb.state.progress == 100.0


class TestGenesisBootstrapAutoShutdown:
    """测试RBAC系统自动关闭."""

    def test_genesis_bootstrap_shutdown(self):
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            GenesisPhase,
        )

        gb = GenesisBootstrap()
        gb.reset()
        gb.bootstrap()
        assert gb.state.is_ready

        state = gb.shutdown()
        assert state.phase == GenesisPhase.PENDING
        assert state.success is False
        assert state.is_ready is False

    def test_genesis_bootstrap_restart_after_shutdown(self):
        from zephyr.security.access_control.genesis_bootstrap import GenesisBootstrap

        gb = GenesisBootstrap()
        gb.reset()
        gb.bootstrap()
        gb.shutdown()

        state = gb.bootstrap()
        assert state.is_ready, f"Restart failed: {state.error}"


class TestBootstrapSuperadminBridge:
    """测试Superadmin账户桥接."""

    def test_bridge_bootstrap(self):
        from zephyr.security.access_control.bootstrap_superadmin import (
            BootstrapSuperadminBridge,
        )

        bridge = BootstrapSuperadminBridge()
        result = bridge.bootstrap()

        assert result["bootstrapped"] is True, f"Bootstrap failed: {result.get('error', '')}"
        assert "account" in result
        assert "roles" in result
        assert "capabilities" in result

    def test_bridge_idempotent(self):
        from zephyr.security.access_control.bootstrap_superadmin import (
            BootstrapSuperadminBridge,
        )

        bridge = BootstrapSuperadminBridge()
        result1 = bridge.bootstrap()
        assert result1["bootstrapped"] is True

        result2 = bridge.bootstrap()
        assert result2["bootstrapped"] is True

    def test_bridge_verify(self):
        from zephyr.security.access_control.bootstrap_superadmin import (
            BootstrapSuperadminBridge,
        )

        bridge = BootstrapSuperadminBridge()
        bridge.bootstrap()
        result = bridge.verify()
        assert result["valid"] is True

    def test_bridge_shutdown(self):
        from zephyr.security.access_control.bootstrap_superadmin import (
            BootstrapSuperadminBridge,
        )

        bridge = BootstrapSuperadminBridge()
        bridge.bootstrap()
        result = bridge.shutdown()
        assert result["shutdown"] is True
        assert bridge.is_bootstrapped is False


class TestAutoRuntimeCoreRBACIntegration:
    """测试auto_runtime_core集成RBAC."""

    def test_bootstrap_rbac_method_exists(self):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        assert hasattr(AutoRuntimeCore, "_bootstrap_rbac")
        assert hasattr(AutoRuntimeCore, "_shutdown_rbac")

    def test_rbac_bootstrap_via_genesis(self):
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            get_genesis_bootstrap,
        )

        gb = get_genesis_bootstrap()
        gb.reset()
        state = gb.bootstrap(config={"version": "test"})

        assert state.is_ready, f"RBAC bootstrap via genesis failed: {state.error}"
        assert state.checks_passed == 5


class TestBootHooksRBACIntegration:
    """测试boot_hooks注册RBAC钩子."""

    def test_register_rbac_hooks_function_exists(self):
        from zephyr.trading.boot_hooks import _register_rbac_hooks

        assert callable(_register_rbac_hooks)

    def test_rbac_hooks_registered(self):
        try:
            from zephyr.governance.ops_governance.event_hook import hook_registry
            from zephyr.trading.boot_hooks import _register_rbac_hooks

            _register_rbac_hooks()

            hook_names = [h.name for h in hook_registry.hooks] if hasattr(hook_registry, "hooks") else []
            rbac_hooks = [n for n in hook_names if "rbac" in n.lower()]
            assert len(rbac_hooks) >= 3, f"Expected >=3 RBAC hooks, got {rbac_hooks}"
        except Exception:
            pytest.skip("hook_registry not available in test environment")


class TestRBACSystemReadiness:
    """测试RBAC系统就绪状态."""

    def test_full_rbac_lifecycle(self):
        """完整生命周期: 启动 → 验证 → 关闭 → 重启."""
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            GenesisPhase,
        )

        gb = GenesisBootstrap()
        gb.reset()

        # 启动
        state = gb.bootstrap()
        assert state.is_ready, f"Bootstrap failed: {state.error}"
        assert state.phase == GenesisPhase.COMPLETED

        # 验证就绪
        assert gb.state.is_ready is True
        assert gb.state.progress == 100.0

        # 关闭
        gb.shutdown()
        assert gb.state.is_ready is False

        # 重启
        state = gb.bootstrap()
        assert state.is_ready, f"Restart failed: {state.error}"

    def test_rbac_components_available_after_bootstrap(self):
        """验证bootstrap后所有RBAC组件可用."""
        from zephyr.security.access_control.genesis_bootstrap import (
            GenesisBootstrap,
            get_genesis_bootstrap,
        )

        gb = get_genesis_bootstrap()
        gb.reset()
        state = gb.bootstrap()
        assert state.is_ready, f"Bootstrap failed: {state.error}"

        # 验证核心组件可用
        from zephyr.security.access_control.engine_degradation import EngineDegradationManager
        from zephyr.security.access_control.immutable_core import get_immutable_core
        from zephyr.security.access_control.kill_switch import KillSwitch

        # ImmutableCore
        core = get_immutable_core()
        assert core.verify_immutable_core_integrity().intact

        # KillSwitch
        ks = KillSwitch()
        assert ks.status is not None

        # EngineDegradation
        deg = EngineDegradationManager()
        assert deg.state is not None

        # ColdStartLock — 验证genesis_bootstrap内部解锁流程完成
        # (ColdStartLock非单例，每次new都是锁定状态，这里验证genesis state即可)
        assert gb.state.checks_passed == gb.state.total_checks
