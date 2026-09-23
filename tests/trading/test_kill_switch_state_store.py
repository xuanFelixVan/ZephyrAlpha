# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §test
# [MODULE] tests.trading.test_kill_switch_state_store
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.kill_switch_state_store; zephyr.trading.trading_contracts.risk.trading_kill_switch
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;测试隔离零生产路径(state 文件一律 tmp_path;trigger 钩子经 monkeypatch 录制器验证)
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_test] module_id: MOD-INF-016 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""O-6/S-3 单元测试：五级熔断触发态持久化（落盘影子+重启重臂+auto_reenable 冷却豁免）。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytest.importorskip(
    "zephyr.trading.trading_contracts.risk.kill_switch_state_store",
    reason="kill_switch_state_store not importable",
)

from zephyr.trading.trading_contracts.risk import (  # noqa: E402
    kill_switch_state_store as store,
)
from zephyr.trading.trading_contracts.risk import trading_kill_switch as tks  # noqa: E402
from zephyr.trading.trading_contracts.risk.trading_kill_switch import (  # noqa: E402
    KillSwitchLevel,
)


@pytest.fixture(autouse=True)
def _restore_switches():
    """测试前后清零内存 active 态（KILL_SWITCHES 为模块级单例）。"""
    for level in KillSwitchLevel:
        tks.reset(level)
    yield
    for level in KillSwitchLevel:
        tks.reset(level)


class TestSaveAndRebuild:
    def test_trigger_then_snapshot_reflects_active(self, tmp_path):
        tks.trigger(KillSwitchLevel.DAILY_LOSS)
        state_path = tmp_path / "ks_state.json"
        assert store.save_state(state_path) is True
        rebuilt = store.rebuild_from_disk(state_path, now=datetime.now(tz=UTC))
        assert rebuilt == ["DAILY_LOSS"]  # 幂等重臂：影子 active 且内存已 active
        assert tks.get_switch(KillSwitchLevel.DAILY_LOSS).active is True

    def test_rebuild_rearms_active_after_reset(self, tmp_path):
        # 进程一：触发+落盘
        tks.trigger(KillSwitchLevel.DAILY_LOSS)
        state_path = tmp_path / "ks_state.json"
        store.save_state(state_path)
        # 进程二：内存态归零（模拟重启），从影子重臂
        tks.reset(KillSwitchLevel.DAILY_LOSS)
        rearmed = store.rebuild_from_disk(state_path, now=datetime.now(tz=UTC))
        assert "DAILY_LOSS" in rearmed
        assert tks.get_switch(KillSwitchLevel.DAILY_LOSS).active is True

    def test_rebuild_skips_expired_auto_reenable(self, tmp_path):
        # POSITION_LIMIT: auto_reenable=True cooldown=300s——影子落盘于 400s 前 → 不重臂
        tks.trigger(KillSwitchLevel.POSITION_LIMIT)
        state_path = tmp_path / "ks_state.json"
        backdated = datetime.now(tz=UTC) - timedelta(seconds=400)
        store.save_state(state_path, now=backdated)
        tks.reset(KillSwitchLevel.POSITION_LIMIT)
        rearmed = store.rebuild_from_disk(state_path, now=datetime.now(tz=UTC))
        assert "POSITION_LIMIT" not in rearmed
        assert tks.get_switch(KillSwitchLevel.POSITION_LIMIT).active is False

    def test_rebuild_keeps_non_auto_within_cooldown(self, tmp_path):
        # DAILY_LOSS: auto_reenable=False（当日不再恢复）——即使影子陈旧也重臂
        tks.trigger(KillSwitchLevel.DAILY_LOSS)
        state_path = tmp_path / "ks_state.json"
        backdated = datetime.now(tz=UTC) - timedelta(hours=5)
        store.save_state(state_path, now=backdated)
        tks.reset(KillSwitchLevel.DAILY_LOSS)
        rearmed = store.rebuild_from_disk(state_path, now=datetime.now(tz=UTC))
        assert "DAILY_LOSS" in rearmed

    def test_rebuild_missing_or_corrupt_file_is_empty(self, tmp_path):
        assert store.rebuild_from_disk(tmp_path / "nope.json") == []
        bad = tmp_path / "corrupt.json"
        bad.write_text("{ not json", encoding="utf-8")
        assert store.rebuild_from_disk(bad) == []


class TestTriggerHooks:
    def test_trigger_and_reset_persist(self, tmp_path, monkeypatch):
        calls: list[bool] = []
        monkeypatch.setattr(
            store, "save_state", lambda state_path=None, **kw: calls.append(True) or True
        )
        tks.trigger(KillSwitchLevel.CIRCUIT_BREAKER)
        tks.reset(KillSwitchLevel.CIRCUIT_BREAKER)
        assert len(calls) == 2  # 触发+复位各落盘一次

    def test_hook_save_failure_does_not_break_trigger(self, tmp_path, monkeypatch):
        def _boom(state_path=None, **kw):
            raise RuntimeError("disk full")

        monkeypatch.setattr(store, "save_state", _boom)
        assert tks.trigger(KillSwitchLevel.API_TIMEOUT) is True  # 主路径不受落盘失败牵连
        assert tks.get_switch(KillSwitchLevel.API_TIMEOUT).active is True
