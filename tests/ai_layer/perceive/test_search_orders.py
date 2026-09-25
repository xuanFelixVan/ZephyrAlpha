# [MODULE] tests.ai_layer.perceive.test_search_orders
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""施工项 5 验收机检面：开单/状态机/TTL 过期全走 schema 校验（journal 全程 tmp_path 注入）。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.ai_layer.perceive.search_orders import (
    SearchOrderError,
    SearchOrderJournal,
)

FIXED_NOW: datetime = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)

OPEN_KW = {
    "vein_id": "VEIN-FAC-E6",
    "vein_family": "E6",
    "trigger": "detector",
    "trigger_ref": "strategy_decay_certifier#certified",
    "keyword_groups": ("因子拥挤度监控", "factor crowding"),
}


def _journal(tmp_path) -> SearchOrderJournal:
    return SearchOrderJournal(tmp_path / "orders")


def test_open_order_assigns_date_seq_ids_and_defaults(tmp_path) -> None:
    journal = _journal(tmp_path)
    first = journal.open_order(**OPEN_KW, now=FIXED_NOW)
    second = journal.open_order(**OPEN_KW, now=FIXED_NOW)
    assert first.order_id == "20260923-001"
    assert second.order_id == "20260923-002"
    assert first.status == "open"
    assert first.budget["max_searches"] == 6 and first.budget["minutes_per_vein"] == 20
    assert first.created_at == FIXED_NOW.isoformat()
    assert first.expiry == (FIXED_NOW + timedelta(days=7)).isoformat()
    # 时间戳显式带时区（RULE-SCHEMA-TZ）
    assert "+00:00" in first.created_at and "+00:00" in first.expiry


def test_open_order_schema_gate_rejects_bad_input(tmp_path) -> None:
    journal = _journal(tmp_path)
    with pytest.raises(SearchOrderError, match="trigger"):
        journal.open_order(**{**OPEN_KW, "trigger": "scheduler"}, now=FIXED_NOW)
    with pytest.raises(SearchOrderError, match="keyword_groups"):
        journal.open_order(**{**OPEN_KW, "keyword_groups": ()}, now=FIXED_NOW)
    with pytest.raises(SearchOrderError, match="vein_id"):
        journal.open_order(**{**OPEN_KW, "vein_id": ""}, now=FIXED_NOW)
    assert journal.list_orders() == []  # 坏单不落盘


def test_transition_whitelist_and_collected_contract(tmp_path) -> None:
    journal = _journal(tmp_path)
    order = journal.open_order(**OPEN_KW, staging_path=".runtime/sessions/s/staging/", now=FIXED_NOW)
    blocked = journal.transition(order.order_id, "blocked")
    assert blocked.status == "blocked"
    resumed = journal.transition(order.order_id, "open")
    assert resumed.status == "open"
    # collected 必须回填 produced_ref（L2 候选卡出生证）
    with pytest.raises(SearchOrderError, match="produced"):
        journal.transition(order.order_id, "collected")
    done = journal.transition(
        order.order_id, "collected", produced_ref="search_order_ref=20260923-001"
    )
    assert done.status == "collected" and done.produced_ref


def test_illegal_transitions_rejected(tmp_path) -> None:
    journal = _journal(tmp_path)
    order = journal.open_order(**OPEN_KW, now=FIXED_NOW)
    # open→collected 白名单允许，但缺 produced_ref 在 collected 契约闸拦截
    with pytest.raises(SearchOrderError, match="produced"):
        journal.transition(order.order_id, "collected")
    expired = journal.transition(order.order_id, "expired")
    with pytest.raises(SearchOrderError, match="非法流转"):
        journal.transition(expired.order_id, "open")  # expired=终态禁复活
    with pytest.raises(SearchOrderError, match="非法流转"):
        journal.transition(expired.order_id, "blocked")  # 禁跳跃


def test_expire_due_marks_only_stale_open_orders(tmp_path) -> None:
    journal = _journal(tmp_path)
    stale = journal.open_order(**OPEN_KW, now=FIXED_NOW - timedelta(days=9))
    fresh = journal.open_order(**OPEN_KW, now=FIXED_NOW)
    blocked = journal.open_order(**OPEN_KW, now=FIXED_NOW - timedelta(days=9))
    journal.transition(blocked.order_id, "blocked")
    expired_ids = journal.expire_due(now=FIXED_NOW)
    assert expired_ids == [stale.order_id]
    assert journal.get_order(stale.order_id).status == "expired"
    assert journal.get_order(fresh.order_id).status == "open"
    assert journal.get_order(blocked.order_id).status == "blocked"  # 非 open 态不 TTL 过期


def test_journal_bad_line_skipped_fail_open(tmp_path) -> None:
    journal = _journal(tmp_path)
    journal.open_order(**OPEN_KW, now=FIXED_NOW)
    with journal.journal_path.open("a", encoding="utf-8") as handle:
        handle.write("{not-json}\n")
    orders = journal.list_orders()
    assert len(orders) == 1  # 坏行跳过不炸（fail-open 读）


def test_journal_roundtrip_payload_fidelity(tmp_path) -> None:
    journal = _journal(tmp_path)
    order = journal.open_order(
        **OPEN_KW,
        source_scope=("qlib", "hf-papers"),
        priority=1.5,
        expected_cards=6,
        now=FIXED_NOW,
    )
    reloaded = journal.get_order(order.order_id)
    assert reloaded.source_scope == ("qlib", "hf-papers")
    assert reloaded.priority == 1.5 and reloaded.expected_cards == 6
    assert reloaded.to_payload()["produced"] == {"search_order_ref": ""}
