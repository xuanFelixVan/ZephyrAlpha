# [A_test] module_id: zephyr.ai_layer.redline.negative_list | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_negative_list
# [MODULE] tests.ai_layer.redline.test_negative_list
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.negative_list; zephyr.security.access_control.kill_switch
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_negative_list.py
# [MATURITY] testing
# [INVARIANTS] 只测纯常量与注册 helper（fresh KillSwitch 实例，不碰进程级单例）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_negative_list.py — NL-1..NL-6 常量真源与 payment_confirm_action 注册面单测。"""

from __future__ import annotations

from zephyr.ai_layer.redline.negative_list import (
    DENY_ENV_PATTERNS,
    NL_DESCRIPTIONS,
    NL_RULE_IDS,
    PAYMENT_TRIGGER_NAME,
    PAYMENT_TRIGGER_THRESHOLD,
    REAL_KEY_MARKER,
    register_payment_confirm_trigger,
)
from zephyr.security.access_control.kill_switch import (
    KillSwitch,
    KillSwitchState,
    TriggerEvent,
)


def test_six_rule_ids_in_appendix_c_order():
    assert NL_RULE_IDS == ("NL-1", "NL-2", "NL-3", "NL-4", "NL-5", "NL-6")
    assert set(NL_DESCRIPTIONS) == set(NL_RULE_IDS), "六条描述全集零漏"


def test_deny_env_patterns_three_families():
    assert DENY_ENV_PATTERNS == ("QMT" "_REAL_*", "ZEPHYR_AUDIT_HMAC_SECRET", "*_LIVE_*")
    assert REAL_KEY_MARKER == "QMT" "_REAL"


def test_payment_trigger_registration_threshold_one_and_blocks():
    """NL-1：注册后 threshold=1，一触即断（record_event 即 BLOCK_AGENT）。"""
    ks = KillSwitch()
    register_payment_confirm_trigger(ks)
    definition = {t.trigger: t for t in ks.triggers}[PAYMENT_TRIGGER_NAME]
    assert definition.default_threshold == PAYMENT_TRIGGER_THRESHOLD == 1
    result = ks.record_event(TriggerEvent(trigger=PAYMENT_TRIGGER_NAME, agent_id="agent-x"))
    assert result.action == "block_agent"
    assert ks.is_agent_blocked("agent-x")
    assert ks.state is not KillSwitchState.TRIPPED, "单 agent 阻断≠全局熔断（≥3 agent 才级联）"


def test_payment_trigger_registration_idempotent_on_default_singleton_shape():
    """幂等注册：同 trigger 重复注册覆盖不报错（用 fresh 实例验证语义，不污染单例）。"""
    ks = KillSwitch()
    register_payment_confirm_trigger(ks)
    register_payment_confirm_trigger(ks)
    assert sum(1 for t in ks.triggers if t.trigger == PAYMENT_TRIGGER_NAME) == 1
