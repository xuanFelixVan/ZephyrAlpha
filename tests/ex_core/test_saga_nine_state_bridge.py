# [A_test] module_id: MOD-L06-001-SAGAO-test-bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_saga_nine_state_bridge
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""F53 九态桥 Saga 面——全枚举对账/流转守卫 fail-closed 单元测试。

覆盖（F53 预检 §四缺口 2 处方：T 线桥覆盖映射真源，Saga 面补断言与守卫）：
  - 九态→内部 7 态映射真源全枚举自证（9 态逐格，禁 KeyError）
  - 内部 7 态→九态词表反向表完备性（7 态全覆盖、派生一致性）
  - 流转守卫全枚举（7×9=63 组合三分归桶：IDEMPOTENT/ALLOWED/BLOCKED）
  - 未知九态 fail-closed（词表外 ValueError/UNKNOWN_STATE）
  - 九态对账断言（matched/漂移；SUBMITTED 三词互认）
"""

from __future__ import annotations

import pytest

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.saga_session_orchestrator import (
    ORDER_STATUS_TO_BROKER_STATES,
    GuardVerdict,
    ReconciliationVerdict,
    SagaNineStateBridge,
)
from zephyr.shared.contracts.enums.order_enums import (
    BROKER_STATE_TO_ORDER_STATUS,
    BrokerOrderState,
    OrderStatus,
)

_TERMINALS = [
    OrderStatus.FILLED,
    OrderStatus.CANCELLED,
    OrderStatus.REJECTED,
    OrderStatus.EXPIRED,
]

_SUBMITTED_WORDS = [
    BrokerOrderState.ACCEPTED,
    BrokerOrderState.SUSPENDED,
    BrokerOrderState.PENDING_CANCEL,
]


# ---------------------------------------------------------------------
# 九态 → 内部 7 态（映射真源全枚举自证）
# ---------------------------------------------------------------------


def test_nine_to_seven_full_mapping_parity() -> None:
    """九态 9 词全枚举：每词映射成功且封闭表逐格一致（禁隐式）。"""
    bridge = SagaNineStateBridge()
    for state in BrokerOrderState:
        mapped = bridge.map_broker_state(state)
        assert mapped is BROKER_STATE_TO_ORDER_STATUS[state]
        # 字符串入参同口径（适配器面 value 直传场景）
        assert bridge.map_broker_state(state.value) is mapped


def test_nine_vocabulary_has_exactly_nine_members() -> None:
    """九态词表=9 词（New/Accepted/Partial/Filled/Cancelled/Rejected/Expired/Suspended/PendingCancel）。"""
    assert len(BrokerOrderState) == 9
    assert len(BROKER_STATE_TO_ORDER_STATUS) == 9  # 封闭表禁缺格


def test_unknown_nine_state_fail_closed() -> None:
    """词表外九态：映射 fail-closed ValueError（禁隐式吞掉）。

    注：真源对入参做 upper() 归一（"pending_cancel" 合法词小写直传可映射），
    fail-closed 只对真正词表外的词生效——用例词表逐词核对九态全集。
    """
    bridge = SagaNineStateBridge()
    for bogus in ("BOGUS", "PENDING_NEW", "PARTIAL_FILLED", "PENDINGCANCEL"):
        with pytest.raises(ValueError):
            bridge.map_broker_state(bogus)


# ---------------------------------------------------------------------
# 内部 7 态 → 九态词表（反向表完备性）
# ---------------------------------------------------------------------


def test_inverse_table_covers_all_seven_statuses() -> None:
    """反向表=内部 7 态全覆盖且无多余键（派生自封闭表，禁手工漂移）。"""
    assert set(ORDER_STATUS_TO_BROKER_STATES.keys()) == set(OrderStatus)
    for status in OrderStatus:
        exits = ORDER_STATUS_TO_BROKER_STATES[status]
        assert exits, f"{status} 反向表出口为空"
        # 派生一致性：每个出口正向映射回本态
        for state in exits:
            assert BROKER_STATE_TO_ORDER_STATUS[state] is status


def test_submitted_exits_are_three_words() -> None:
    """SUBMITTED 工作态九态出口=三词（ACCEPTED/SUSPENDED/PENDING_CANCEL）。"""
    assert ORDER_STATUS_TO_BROKER_STATES[OrderStatus.SUBMITTED] == frozenset(_SUBMITTED_WORDS)


def test_terminal_statuses_have_single_word_exit() -> None:
    """终态九态出口=单词（对账断言的确定性前提）。"""
    for status in _TERMINALS:
        exits = ORDER_STATUS_TO_BROKER_STATES[status]
        assert len(exits) == 1
        assert BROKER_STATE_TO_ORDER_STATUS[next(iter(exits))] is status


# ---------------------------------------------------------------------
# 流转守卫（7×9 全枚举三分归桶）
# ---------------------------------------------------------------------


def test_guard_exhaustive_seven_by_nine_bucketing() -> None:
    """流转守卫全枚举 63 组合：每组合落在 IDEMPOTENT/ALLOWED/BLOCKED 之一，
    且 ALLOWED 桶与 OrderManager.VALID_TRANSITIONS 白名单严格等价。"""
    bridge = SagaNineStateBridge()
    seen_verdicts: set[GuardVerdict] = set()
    for current in OrderStatus:
        for state in BrokerOrderState:
            verdict = bridge.assert_transition("o-guard", current, state)
            seen_verdicts.add(verdict.verdict)
            if verdict.mapped_status is current:
                assert verdict.verdict is GuardVerdict.IDEMPOTENT
            elif verdict.mapped_status in OrderManager.VALID_TRANSITIONS[current]:
                assert verdict.verdict is GuardVerdict.ALLOWED
            else:
                assert verdict.verdict is GuardVerdict.BLOCKED
    assert seen_verdicts == {
        GuardVerdict.IDEMPOTENT,
        GuardVerdict.ALLOWED,
        GuardVerdict.BLOCKED,
    }
    # 全枚举无 UNKNOWN_STATE（九态词表内组合不可能未知）
    assert GuardVerdict.UNKNOWN_STATE not in seen_verdicts


def test_guard_unknown_state_fail_closed_verdict() -> None:
    """词表外九态：守卫返回 UNKNOWN_STATE 判定（不抛出，判定面 fail-closed）。"""
    bridge = SagaNineStateBridge()
    verdict = bridge.assert_transition("o-x", OrderStatus.SUBMITTED, "NOT_IN_VOCAB")
    assert verdict.verdict is GuardVerdict.UNKNOWN_STATE
    assert verdict.mapped_status is None
    assert verdict.broker_state == "NOT_IN_VOCAB"


def test_guard_terminal_absorbs_everything() -> None:
    """终态吸收律：CANCELLED 之后任何非同态九态事件一律 BLOCKED（终态禁再流转）。"""
    bridge = SagaNineStateBridge()
    for state in BrokerOrderState:
        verdict = bridge.assert_transition("o-cxl", OrderStatus.CANCELLED, state)
        expected = GuardVerdict.IDEMPOTENT if state is BrokerOrderState.CANCELLED else GuardVerdict.BLOCKED
        assert verdict.verdict is expected, f"CANCELLED×{state}"


def test_guard_partial_fill_path_allowed() -> None:
    """部成→全成/撤改 主链放行（F53 部分成交撤改语义）。"""
    bridge = SagaNineStateBridge()
    for target in (BrokerOrderState.FILLED, BrokerOrderState.CANCELLED, BrokerOrderState.EXPIRED):
        verdict = bridge.assert_transition("o-p", OrderStatus.PARTIAL, target)
        assert verdict.verdict is GuardVerdict.ALLOWED
    # 部成→重报（NEW→PENDING）属回退，非法
    assert bridge.assert_transition("o-p", OrderStatus.PARTIAL, BrokerOrderState.NEW).verdict is GuardVerdict.BLOCKED


# ---------------------------------------------------------------------
# 九态对账断言
# ---------------------------------------------------------------------


def test_reconcile_matched_paths() -> None:
    """对账一致：本地态与券商九态映射全等（SUBMITTED 三词互认）。"""
    bridge = SagaNineStateBridge()
    for word in _SUBMITTED_WORDS:
        verdict = bridge.reconcile("o-r", OrderStatus.SUBMITTED, word)
        assert isinstance(verdict, ReconciliationVerdict)
        assert verdict.matched is True
    assert bridge.reconcile("o-r", OrderStatus.PENDING, BrokerOrderState.NEW).matched
    assert bridge.reconcile("o-r", OrderStatus.FILLED, BrokerOrderState.FILLED).matched


def test_reconcile_drift_detected_not_mutated() -> None:
    """对账漂移：本地 FILLED vs 券商 PARTIAL → matched=False；断言面不改账（冻结判据）。"""
    bridge = SagaNineStateBridge()
    verdict = bridge.reconcile("o-d", OrderStatus.FILLED, BrokerOrderState.PARTIAL)
    assert verdict.matched is False
    assert verdict.mapped_status is OrderStatus.PARTIAL
    assert "需人工对账" in verdict.detail


def test_reconcile_unknown_state_raises() -> None:
    """对账词表外：直接 ValueError（批量面负责吞没为漂移记录）。"""
    bridge = SagaNineStateBridge()
    with pytest.raises(ValueError):
        bridge.reconcile("o-u", OrderStatus.SUBMITTED, "GHOST_STATE")
