# [BLUEPRINT] MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §ARCH-WORKTREE-LIFECYCLE-001
# [MODULE] tests.governance.rule_bridge.test_worktree_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.worktree_lifecycle
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时目录隔离；不依赖真实 Zephyr 项目结构
# [MODIFY-GUARD] 测试函数名与 #ARCH-WORKTREE-LIFECYCLE-001 API 对齐
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_worktree_lifecycle.py — #ARCH-WORKTREE-LIFECYCLE-001 状态机测试

测试覆盖：
  1. WorktreeState 5态枚举完整性
  2. load_state_machine_config 加载 worktree_state_machine.yaml
  3. WorktreeLifecycle.register 注册新 session（CREATED 态）
  4. WorktreeLifecycle.transition 合法/非法转换
  5. WorktreeLifecycle.get_state / get_history / list_by_state
  6. check_quarantine_expiry 72h 过期检测
  7. cleanup_swept 清理归档记录
  8. 持久化：JSON 文件读写 + 跨实例恢复
  9. 幂等性：重复 register 不抛错
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SRC_DIR = str(_PROJECT_ROOT / "src")
import sys

if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_lifecycle(tmp_path, monkeypatch):
    """临时 WorktreeLifecycle 实例（自定义 config + records_dir）。"""
    # 创建临时 config
    config_path = tmp_path / "worktree_state_machine.yaml"
    config_data = {
        "module_id": "MOD-GOV_ENFORCEMENT_worktree_lifecycle",
        "states": [
            {"name": s, "description": f"state {s}"} for s in ["created", "active", "idle", "quarantined", "swept"]
        ],
        "transitions": [
            {"from": "created", "to": "active"},
            {"from": "created", "to": "swept"},
            {"from": "active", "to": "idle"},
            {"from": "active", "to": "swept"},
            {"from": "active", "to": "quarantined"},
            {"from": "idle", "to": "active"},
            {"from": "idle", "to": "quarantined"},
            {"from": "idle", "to": "swept"},
            {"from": "quarantined", "to": "active"},
            {"from": "quarantined", "to": "swept"},
        ],
        "timeout_rules": [],
    }
    config_path.write_text(yaml.safe_dump(config_data), encoding="utf-8")

    records_dir = tmp_path / "records"
    records_dir.mkdir()

    # patch DEFAULT paths in module to use tmp
    import zephyr.gov_enforcement.rule_bridge.worktree_lifecycle as wl_mod

    monkeypatch.setattr(wl_mod, "DEFAULT_STATE_MACHINE_PATH", config_path)
    monkeypatch.setattr(wl_mod, "DEFAULT_RECORDS_DIR", records_dir)

    wl = wl_mod.WorktreeLifecycle(
        config_path=config_path,
        records_dir=records_dir,
    )
    return wl, records_dir, wl_mod


# ---------------------------------------------------------------------------
# TestWorktreeStateEnum
# ---------------------------------------------------------------------------


class TestWorktreeStateEnum:
    """WorktreeState 5态枚举测试。"""

    def test_all_states(self):
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import WorktreeState

        assert WorktreeState.CREATED.value == "created"
        assert WorktreeState.ACTIVE.value == "active"
        assert WorktreeState.IDLE.value == "idle"
        assert WorktreeState.QUARANTINED.value == "quarantined"
        assert WorktreeState.SWEPT.value == "swept"

    def test_state_count(self):
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import WorktreeState

        assert len(WorktreeState) == 5

    def test_inherits_str_enum(self):
        """WorktreeState 是 str Enum，可直接与字符串比较。"""
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import WorktreeState

        assert WorktreeState.CREATED == "created"


# ---------------------------------------------------------------------------
# TestLoadStateMachineConfig
# ---------------------------------------------------------------------------


class TestLoadStateMachineConfig:
    """load_state_machine_config 测试。"""

    def test_load_valid_config(self, tmp_lifecycle):
        wl, records_dir, wl_mod = tmp_lifecycle
        config = wl_mod.load_state_machine_config()
        assert "states" in config
        assert "transitions" in config
        assert len(config["states"]) == 5

    def test_load_missing_file(self, tmp_path):
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
            load_state_machine_config,
        )

        with pytest.raises(FileNotFoundError):
            load_state_machine_config(tmp_path / "nonexistent.yaml")


# ---------------------------------------------------------------------------
# TestRegister
# ---------------------------------------------------------------------------


class TestRegister:
    """WorktreeLifecycle.register 测试。"""

    def test_register_creates_record_with_created_state(self, tmp_lifecycle):
        wl, records_dir, _ = tmp_lifecycle
        state = wl.register("sess-001")
        assert state.value == "created"
        record_path = records_dir / "sess-001.json"
        assert record_path.exists()
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["state"] == "created"
        assert record["session_id"] == "sess-001"
        assert len(record["history"]) == 1

    def test_register_idempotent(self, tmp_lifecycle):
        """重复 register 已存在的 session 不抛错，返回当前状态。"""
        wl, _, _ = tmp_lifecycle
        wl.register("sess-002")
        wl.transition("sess-002", "active")
        state = wl.register("sess-002")  # 重复
        assert state.value == "active"  # 返回当前状态，不是 created


# ---------------------------------------------------------------------------
# TestTransition
# ---------------------------------------------------------------------------


class TestTransition:
    """WorktreeLifecycle.transition 合法/非法转换测试。"""

    def test_valid_transition_created_to_active(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-t1")
        state = wl.transition("sess-t1", "active")
        assert state.value == "active"

    def test_valid_transition_active_to_idle(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-t2")
        wl.transition("sess-t2", "active")
        state = wl.transition("sess-t2", "idle")
        assert state.value == "idle"

    def test_valid_transition_idle_to_quarantined(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-t3")
        wl.transition("sess-t3", "active")
        wl.transition("sess-t3", "idle")
        state = wl.transition("sess-t3", "quarantined")
        assert state.value == "quarantined"

    def test_valid_transition_quarantined_to_swept(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-t4")
        wl.transition("sess-t4", "active")
        wl.transition("sess-t4", "idle")
        wl.transition("sess-t4", "quarantined")
        state = wl.transition("sess-t4", "swept")
        assert state.value == "swept"

    def test_invalid_transition_created_to_idle(self, tmp_lifecycle):
        """created → idle 直接跳跃不合法。"""
        wl, _, _ = tmp_lifecycle
        wl.register("sess-t5")
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
            WorktreeTransitionError,
        )

        with pytest.raises(WorktreeTransitionError):
            wl.transition("sess-t5", "idle")

    def test_invalid_transition_swept_to_anything(self, tmp_lifecycle):
        """swept 是终态，不能再转换。"""
        wl, _, _ = tmp_lifecycle
        wl.register("sess-t6")
        wl.transition("sess-t6", "active")
        wl.transition("sess-t6", "swept")
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
            WorktreeTransitionError,
        )

        with pytest.raises(WorktreeTransitionError):
            wl.transition("sess-t6", "active")

    def test_transition_nonexistent_session(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
            WorktreeLifecycleError,
        )

        with pytest.raises(WorktreeLifecycleError):
            wl.transition("nonexistent", "active")

    def test_transition_records_history(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-h1")
        wl.transition("sess-h1", "active", detail="start construction")
        history = wl.get_history("sess-h1")
        assert len(history) == 2  # register + transition
        assert history[1]["from"] == "created"
        assert history[1]["to"] == "active"
        assert history[1]["detail"] == "start construction"


# ---------------------------------------------------------------------------
# TestGetStateAndHistory
# ---------------------------------------------------------------------------


class TestGetStateAndHistory:
    """get_state / get_history 测试。"""

    def test_get_state_returns_current(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-g1")
        wl.transition("sess-g1", "active")
        assert wl.get_state("sess-g1").value == "active"

    def test_get_state_nonexistent_raises(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
            WorktreeLifecycleError,
        )

        with pytest.raises(WorktreeLifecycleError):
            wl.get_state("nonexistent")

    def test_get_history_empty_for_new_session(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-g2")
        history = wl.get_history("sess-g2")
        assert len(history) == 1  # register creates initial history entry


# ---------------------------------------------------------------------------
# TestListByState
# ---------------------------------------------------------------------------


class TestListByState:
    """list_by_state 测试。"""

    def test_list_active_sessions(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-a1")
        wl.register("sess-a2")
        wl.register("sess-a3")
        wl.transition("sess-a1", "active")
        wl.transition("sess-a2", "active")
        # sess-a3 still created
        active = wl.list_by_state("active")
        assert set(active) == {"sess-a1", "sess-a2"}

    def test_list_by_enum_state(self, tmp_lifecycle):
        """传入 WorktreeState enum 也可。"""
        from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import WorktreeState

        wl, _, _ = tmp_lifecycle
        wl.register("sess-l1")
        created = wl.list_by_state(WorktreeState.CREATED)
        assert "sess-l1" in created

    def test_list_empty_when_no_records(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        assert wl.list_by_state("active") == []


# ---------------------------------------------------------------------------
# TestQuarantineExpiry
# ---------------------------------------------------------------------------


class TestQuarantineExpiry:
    """check_quarantine_expiry 72h 过期检测。"""

    def test_recent_quarantine_not_expired(self, tmp_lifecycle):
        wl, records_dir, _ = tmp_lifecycle
        wl.register("sess-q1")
        wl.transition("sess-q1", "active")
        wl.transition("sess-q1", "idle")
        wl.transition("sess-q1", "quarantined")
        expired = wl.check_quarantine_expiry()
        assert expired == []  # 刚 quarantine，未过期

    def test_old_quarantine_expired(self, tmp_lifecycle):
        """手动修改 last_transition_at 模拟 73h 前。"""
        wl, records_dir, _ = tmp_lifecycle
        wl.register("sess-q2")
        wl.transition("sess-q2", "active")
        wl.transition("sess-q2", "idle")
        wl.transition("sess-q2", "quarantined")
        # 手动改 last_transition_at 为 73h 前
        record_path = records_dir / "sess-q2.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["last_transition_at"] = time.time() - 73 * 3600
        record_path.write_text(json.dumps(record), encoding="utf-8")
        expired = wl.check_quarantine_expiry()
        assert "sess-q2" in expired


# ---------------------------------------------------------------------------
# TestCleanupSwept
# ---------------------------------------------------------------------------


class TestCleanupSwept:
    """cleanup_swept 清理归档记录。"""

    def test_cleanup_removes_swept_records(self, tmp_lifecycle):
        wl, records_dir, _ = tmp_lifecycle
        wl.register("sess-c1")
        wl.transition("sess-c1", "active")
        wl.transition("sess-c1", "swept")
        assert (records_dir / "sess-c1.json").exists()
        count = wl.cleanup_swept()
        assert count == 1
        assert not (records_dir / "sess-c1.json").exists()

    def test_cleanup_does_not_affect_other_states(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-c2")
        wl.transition("sess-c2", "active")
        count = wl.cleanup_swept()
        assert count == 0


# ---------------------------------------------------------------------------
# TestPersistence
# ---------------------------------------------------------------------------


class TestPersistence:
    """持久化：跨实例恢复。"""

    def test_new_instance_reads_existing_records(self, tmp_lifecycle):
        wl, records_dir, wl_mod = tmp_lifecycle
        wl.register("sess-p1")
        wl.transition("sess-p1", "active")

        # 新实例（同 records_dir）
        wl2 = wl_mod.WorktreeLifecycle(
            config_path=wl.config_path,
            records_dir=records_dir,
        )
        state = wl2.get_state("sess-p1")
        assert state.value == "active"


# ---------------------------------------------------------------------------
# TestActiveSessionsProperty
# ---------------------------------------------------------------------------


class TestActiveSessionsProperty:
    """active_sessions 属性测试。"""

    def test_active_sessions_returns_list(self, tmp_lifecycle):
        wl, _, _ = tmp_lifecycle
        wl.register("sess-as1")
        wl.register("sess-as2")
        wl.transition("sess-as1", "active")
        active = wl.active_sessions
        assert "sess-as1" in active
        assert "sess-as2" not in active
