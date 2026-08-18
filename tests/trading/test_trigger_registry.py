# [A_test] module_id: MOD-TRIG-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TRIG-001 | docs/03_modules/_domain_trading/trigger_registry/blueprint.md | §
# [MODULE] tests.trading.test_trigger_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""TriggerRegistry 施工验证测试。

覆盖：
- TriggerEntry dataclass 契约
- TriggerRegistry 注册/注销/评估/冲突消解
- 15 条 MVP 扳机清单注册表
- 同源去重 / 冷却期 / 优先级仲裁
"""

from __future__ import annotations

import pytest

from zephyr.trading.trigger_registry import (
    DEFAULT_COOLDOWN_SEC,
    MVP_TRIGGER_LIST,
    PRIORITY_MAX,
    PRIORITY_MIN,
    TriggeredEvent,
    TriggerEntry,
    TriggerRegistry,
    create_mvp_registry,
)

# ══════════════════════════════════════════════════════════════
# TriggerEntry dataclass 契约
# ══════════════════════════════════════════════════════════════


class TestTriggerEntry:
    """TriggerEntry 契约验证。"""

    def test_fields(self):
        """字段完整。"""
        entry = TriggerEntry(
            trigger_id="TEST",
            source_module="41",
            condition=lambda ctx: True,
            action="PLACE_ORDER",
            priority=3,
            scope="POSITION",
        )
        assert entry.trigger_id == "TEST"
        assert entry.source_module == "41"
        assert entry.priority == 3
        assert entry.scope == "POSITION"
        assert entry.cooldown_sec == DEFAULT_COOLDOWN_SEC

    def test_custom_cooldown(self):
        """自定义冷却期。"""
        entry = TriggerEntry(
            trigger_id="TEST",
            source_module="41",
            condition=lambda ctx: True,
            action="PLACE_ORDER",
            priority=3,
            scope="POSITION",
            cooldown_sec=120,
        )
        assert entry.cooldown_sec == 120


# ══════════════════════════════════════════════════════════════
# TriggerRegistry 注册/评估/仲裁
# ══════════════════════════════════════════════════════════════


class TestTriggerRegistry:
    """TriggerRegistry 核心功能。"""

    def test_register(self):
        """注册触发器。"""
        reg = TriggerRegistry()
        entry = TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=3, scope="POSITION",
        )
        reg.register(entry)
        assert "T1" in reg.entries

    def test_register_duplicate_raises(self):
        """重复注册 trigger_id→ValueError。"""
        reg = TriggerRegistry()
        entry = TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=3, scope="POSITION",
        )
        reg.register(entry)
        with pytest.raises(ValueError, match="重复注册"):
            reg.register(entry)

    def test_register_invalid_priority(self):
        """priority 越界→ValueError。"""
        reg = TriggerRegistry()
        entry = TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=0, scope="POSITION",
        )
        with pytest.raises(ValueError, match="越界"):
            reg.register(entry)

    def test_unregister(self):
        """注销触发器。"""
        reg = TriggerRegistry()
        entry = TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=3, scope="POSITION",
        )
        reg.register(entry)
        reg.unregister("T1")
        assert "T1" not in reg.entries

    def test_evaluate_all_fires(self):
        """condition=True→触发。"""
        reg = TriggerRegistry()
        reg.register(TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=3, scope="POSITION",
        ))
        events = reg.evaluate_all()
        assert len(events) == 1
        assert events[0].trigger_id == "T1"

    def test_evaluate_all_no_fire(self):
        """condition=False→不触发。"""
        reg = TriggerRegistry()
        reg.register(TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: False, action="A1",
            priority=3, scope="POSITION",
        ))
        events = reg.evaluate_all()
        assert len(events) == 0

    def test_cooldown_blocks_repeat(self):
        """冷却期内不重复触发。"""
        reg = TriggerRegistry()
        reg.register(TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=3, scope="POSITION", cooldown_sec=60,
        ))
        events1 = reg.evaluate_all()
        assert len(events1) == 1
        events2 = reg.evaluate_all()
        assert len(events2) == 0  # 冷却期内

    def test_priority_sorting(self):
        """触发事件按优先级升序排序。"""
        reg = TriggerRegistry()
        reg.register(TriggerEntry(
            trigger_id="LOW", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=5, scope="POSITION",
        ))
        reg.register(TriggerEntry(
            trigger_id="HIGH", source_module="35",
            condition=lambda ctx: True, action="A2",
            priority=1, scope="PORTFOLIO",
        ))
        reg.register(TriggerEntry(
            trigger_id="MID", source_module="42",
            condition=lambda ctx: True, action="A3",
            priority=3, scope="POSITION",
        ))
        events = reg.evaluate_all()
        assert [e.trigger_id for e in events] == ["HIGH", "MID", "LOW"]

    def test_scope_sorting_same_priority(self):
        """同优先级按 scope 排序（PORTFOLIO>STRATEGY>POSITION）。"""
        reg = TriggerRegistry()
        reg.register(TriggerEntry(
            trigger_id="POS", source_module="41",
            condition=lambda ctx: True, action="A1",
            priority=3, scope="POSITION",
        ))
        reg.register(TriggerEntry(
            trigger_id="PF", source_module="35",
            condition=lambda ctx: True, action="A2",
            priority=3, scope="PORTFOLIO",
        ))
        events = reg.evaluate_all()
        assert events[0].trigger_id == "PF"
        assert events[1].trigger_id == "POS"

    def test_shared_condition_dedup(self):
        """同源去重：共享 condition 只算一次。"""
        call_count = 0

        def shared_condition(ctx):
            nonlocal call_count
            call_count += 1
            return True

        reg = TriggerRegistry()
        reg.register(TriggerEntry(
            trigger_id="T1", source_module="41",
            condition=shared_condition, action="A1",
            priority=3, scope="POSITION",
        ))
        reg.register(TriggerEntry(
            trigger_id="T2", source_module="42",
            condition=shared_condition, action="A2",
            priority=4, scope="POSITION",
        ))
        events = reg.evaluate_all()
        assert len(events) == 2
        assert call_count == 1  # 只算一次

    def test_resolve_conflicts_kill_switch(self):
        """Kill Switch（priority=1）覆盖一切。"""
        reg = TriggerRegistry()
        events = [
            TriggeredEvent("T1", "41", "A1", 3, "POSITION"),
            TriggeredEvent("KILL", "35", "HALT_ALL", 1, "PORTFOLIO"),
            TriggeredEvent("T2", "42", "A2", 4, "POSITION"),
        ]
        result = reg.resolve_conflicts(events)
        assert len(result) == 1
        assert result[0].trigger_id == "KILL"

    def test_resolve_conflicts_sell_over_buy(self):
        """止损暂停（priority=3）优先于加仓放行（priority=5）。"""
        reg = TriggerRegistry()
        events = [
            TriggeredEvent("BUY", "41", "PLACE_ORDER", 5, "POSITION"),
            TriggeredEvent("SELL", "42", "CANCEL_BATCH2", 3, "POSITION"),
        ]
        result = reg.resolve_conflicts(events)
        assert len(result) == 1
        assert result[0].trigger_id == "SELL"


# ══════════════════════════════════════════════════════════════
# 15 条 MVP 扳机清单
# ══════════════════════════════════════════════════════════════


class TestMVPTriggerList:
    """15 条 MVP 扳机清单验证。"""

    def test_count(self):
        """恰好 15 条。"""
        assert len(MVP_TRIGGER_LIST) == 15

    def test_all_fields_present(self):
        """每条都有 trigger_id/source_module/action/priority/scope/cooldown_sec。"""
        for item in MVP_TRIGGER_LIST:
            assert "trigger_id" in item
            assert "source_module" in item
            assert "action" in item
            assert "priority" in item
            assert "scope" in item
            assert "cooldown_sec" in item

    def test_priority_range(self):
        """priority 在 [1, 5] 范围内。"""
        for item in MVP_TRIGGER_LIST:
            assert PRIORITY_MIN <= item["priority"] <= PRIORITY_MAX

    def test_scope_valid(self):
        """scope 是 POSITION/STRATEGY/PORTFOLIO 之一。"""
        for item in MVP_TRIGGER_LIST:
            assert item["scope"] in ("POSITION", "STRATEGY", "PORTFOLIO")

    def test_trigger_ids_unique(self):
        """trigger_id 唯一。"""
        ids = [item["trigger_id"] for item in MVP_TRIGGER_LIST]
        assert len(ids) == len(set(ids))

    def test_priority_1_has_kill_switch(self):
        """priority=1 含 RISK_KILL_SWITCH。"""
        p1_ids = [i["trigger_id"] for i in MVP_TRIGGER_LIST if i["priority"] == 1]
        assert "RISK_KILL_SWITCH" in p1_ids

    def test_priority_5_has_buy_release(self):
        """priority=5 含 BUY_BATCH2_RELEASE。"""
        p5_ids = [i["trigger_id"] for i in MVP_TRIGGER_LIST if i["priority"] == 5]
        assert "BUY_BATCH2_RELEASE" in p5_ids

    def test_create_mvp_registry(self):
        """create_mvp_registry 创建 15 条注册表。"""
        reg = create_mvp_registry()
        assert len(reg.entries) == 15

    def test_mvp_registry_entries_valid(self):
        """注册表条目都是合法 TriggerEntry。"""
        reg = create_mvp_registry()
        for trigger_id, entry in reg.entries.items():
            assert isinstance(entry, TriggerEntry)
            assert entry.trigger_id == trigger_id

    def test_expected_trigger_ids(self):
        """15 条 trigger_id 与 41 §3.9 表一致。"""
        expected = {
            "RISK_KILL_SWITCH", "RISK_DRAWDOWN_L4",
            "RISK_DRAWDOWN_L3", "RISK_LIQUIDITY_CRISIS", "RISK_VAR_BREACH",
            "SELL_BREAKOUT_FAIL", "SELL_SUPPORT_BREAK", "SELL_CIRCUIT_BREAKER",
            "BUY_BREAKOUT_FAIL", "SELL_ATR_STOP", "SELL_TRAILING_STOP", "SELL_TAKE_PROFIT",
            "BUY_BATCH2_RELEASE", "EXE_MAKE_OR_TAKE", "EXE_CANCEL_RATE",
        }
        actual = {item["trigger_id"] for item in MVP_TRIGGER_LIST}
        assert actual == expected
