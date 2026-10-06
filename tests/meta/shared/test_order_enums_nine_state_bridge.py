# [BLUEPRINT] MOD-INF-016 | src/zephyr/shared/contracts/enums/order_enums.py（G41-2a 九态映射桥）
# [MODULE] tests.shared.test_order_enums_nine_state_bridge
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 测试隔离零生产写入；映射桥双态验收（F41 卷 G41-2）：九态成员全覆盖→内部
#   7 态合法目标、value 串入口等价、未知态 fail-closed、终态四格语义不变
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=AssertionError
# [TESTS] self
# [TTL] permanent
"""BrokerOrderState 九态→OrderStatus 七态映射桥单测（G41-2a，zc-lane-t-20260927）。

TDM-E-L4-10 判据面九态（QMT 风格：New/Accepted/Suspended/PendingCancel 为码面
7 态所无）↔ 内部封闭 7 态——映射全格收口 + fail-closed 词表外拒绝。
"""

from __future__ import annotations

import pytest

from zephyr.shared.contracts.enums.order_enums import (
    BROKER_STATE_TO_ORDER_STATUS,
    BrokerOrderState,
    OrderStatus,
    map_broker_state_to_order_status,
)


def test_nine_members_complete():
    """九态词表闭合：4 个补态 + 7 态同名词齐。"""
    expected = {
        "NEW",
        "ACCEPTED",
        "PARTIAL",
        "FILLED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
        "SUSPENDED",
        "PENDING_CANCEL",
    }
    assert {m.value for m in BrokerOrderState} == expected
    assert len(BROKER_STATE_TO_ORDER_STATUS) == 9


def test_bridge_dual_state_all_cells():
    """映射桥双态：九格全量→内部 7 态合法成员（新增四格显式断言）。"""
    targets = {m.value for m in OrderStatus}
    for state, status in BROKER_STATE_TO_ORDER_STATUS.items():
        assert status.value in targets
    # 判据面新增四格的收口策略
    assert map_broker_state_to_order_status("NEW") is OrderStatus.PENDING
    assert map_broker_state_to_order_status("ACCEPTED") is OrderStatus.SUBMITTED
    # 停牌挂起/待撤 = 委托在柜台侧仍存活 → SUBMITTED 工作态（禁映射终态）
    assert map_broker_state_to_order_status("SUSPENDED") is OrderStatus.SUBMITTED
    assert map_broker_state_to_order_status("PENDING_CANCEL") is OrderStatus.SUBMITTED


def test_bridge_terminal_states_unchanged():
    """终态四格语义不变（对码面 7 态同名词直映）。"""
    pairs = {
        "PARTIAL": OrderStatus.PARTIAL,
        "FILLED": OrderStatus.FILLED,
        "CANCELLED": OrderStatus.CANCELLED,
        "REJECTED": OrderStatus.REJECTED,
        "EXPIRED": OrderStatus.EXPIRED,
    }
    for value, want in pairs.items():
        assert map_broker_state_to_order_status(value) is want


def test_bridge_accepts_enum_and_string_equally():
    """成员与 value 串双入口等价。"""
    for member, status in BROKER_STATE_TO_ORDER_STATUS.items():
        assert map_broker_state_to_order_status(member) is status
        assert map_broker_state_to_order_status(member.value) is status


def test_bridge_unknown_state_fail_closed():
    """词表外未知态 ValueError（禁隐式吞——扩表必须显式）。"""
    with pytest.raises(ValueError):
        map_broker_state_to_order_status("TELEPORTED")
    with pytest.raises(ValueError):
        map_broker_state_to_order_status("")
    with pytest.raises(ValueError):
        map_broker_state_to_order_status("pending_cancel ")  # 尾随空格非词表内
