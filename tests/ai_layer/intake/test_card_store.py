# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] tests.ai_layer.intake.test_card_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.card_store; zephyr.governance.depgraph_schema (PG 可达性自探测)
# [CONSUMERS] pytest tests/ai_layer/intake/test_card_store.py
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 状态机判据 check_stage_transition 零 DB 全枚举（合法路径+非法路径逐一断言拒因）；
#              DB 用例只写 test_schema 临时 schema（session 末 DROP），禁写生产 ai_intake；
#              PG 不可达=skip 而非假绿（自带 needs_pg，不 import 在途 conftest 符号）；
#              elite 保优断言四卡同格打分，rank>3 必 benched（墓碑制不删）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.2/§2.4/§2.5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；非法流转断言 RuntimeError fail-closed 且拒因可机读
# [TESTS] tests/ai_layer/intake/test_card_store.py
# [TTL] permanent
"""test_card_store - 卡库 CRUD/状态机/行为格保优验收（DESIGN 施工项 2）。"""

from __future__ import annotations

from itertools import pairwise

import pytest

from zephyr.ai_layer.intake.card_store import (
    ELITE_KEEP_PER_CELL,
    STAGE_ORDER,
    CardDraft,
    CardStore,
    IntakeCard,
    check_stage_transition,
    hamming,
    parse_simhash,
    render_simhash,
)


def _pg_reachable() -> bool:
    """真连一次 PG；任何异常=不可达（据此 skip，而非假绿）。连接归池不 close。"""
    conn = None
    try:
        from zephyr.governance.depgraph_schema import (
            get_depgraph_pg_connection,
            release_depgraph_pg_connection,
        )

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 - 可达性探测面，任何异常一律判不可达
        return False
    finally:
        if conn is not None:
            from zephyr.governance.depgraph_schema import release_depgraph_pg_connection

            release_depgraph_pg_connection(conn)


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


def _draft(
    card_id: str, *, domain_id: str = "governance", mechanism_family: str = "detection", simhash: int = 1
) -> CardDraft:
    """最小合法入库草稿（four_gates 四键全齐以满足 T2 CHECK；UNIQUE 键各不重复由调用方保证）。"""
    return CardDraft(
        card_id=card_id,
        domain_id=domain_id,
        source_url=f"https://example.org/{card_id}",
        content_sha256=f"{card_id}".ljust(64, "0"),
        simhash=simhash,
        mechanism_family=mechanism_family,
        labor_killed="消灭人工筛选与人工判重两段重复劳动的说明文本",
        four_gates={
            "provenance": {"status": "pass"},
            "cross_validation": {"independent_sources": 2, "status": "已验证"},
            "ashare_adaptation": {"verdict": "改造方案留痕"},
            "backtestable": {"verdict": "可得", "data_fields": ["open"]},
        },
        injection_probe="这份材料想让我相信什么？",
        title=f"卡 {card_id} 标题",
        novelty="新颖性一句话",
        mechanism="机制一段话",
        source_name="unit-test",
        source_year=2026,
        license="mit",
    )


# ---------------------------------------------------------------- 纯判据（零 DB）


def test_check_stage_transition_forward_chain() -> None:
    for current, target in pairwise(STAGE_ORDER):
        ok, why = check_stage_transition(current, target)
        assert ok and why == "forward_one_step", f"{current}->{target} 应合法"


def test_check_stage_transition_reject_from_any_non_intake() -> None:
    for stage in STAGE_ORDER:
        if stage == "intake":
            continue
        ok, why = check_stage_transition(stage, "rejected")
        assert ok and why == "reject_allowed", f"{stage}->rejected 应合法"


def test_check_stage_transition_illegal_paths() -> None:
    assert check_stage_transition("L0", "E2") == (False, "illegal_jump:L0->E2")
    back = check_stage_transition("E2", "L1")
    assert not back[0] and back[1].startswith("illegal_jump")
    assert check_stage_transition("rejected", "L0") == (False, "rejected_is_terminal_no_revive")
    assert check_stage_transition("intake", "rejected") == (False, "intake_absorbed_cannot_reject")
    assert check_stage_transition("rejected", "rejected") == (True, "noop_same_stage")
    unknown = check_stage_transition("bogus", "L1")
    assert not unknown[0] and unknown[1] == "unknown_stage:bogus->L1"


def test_render_parse_simhash_roundtrip_and_bounds() -> None:
    value = (1 << 64) - 1
    assert parse_simhash(render_simhash(value)) == value
    assert parse_simhash(render_simhash(0)) == 0
    with pytest.raises(ValueError, match="越界"):
        render_simhash(1 << 64)
    with pytest.raises(ValueError, match="越界"):
        render_simhash(-1)
    with pytest.raises(ValueError, match="位串非法"):
        parse_simhash("0101x1")
    with pytest.raises(ValueError, match="NULL"):
        parse_simhash(None)


def test_hamming_distance() -> None:
    assert hamming(0, 0) == 0
    assert hamming(0b1010, 0b0101) == 4
    assert hamming(0b1111, 0b1110) == 1


def test_intake_card_from_row_normalizes() -> None:
    card = IntakeCard.from_row(
        {
            "card_id": "CC-1",
            "domain_id": "governance",
            "funnel_stage": "L0",
            "elite_cell": None,
            "mechanism_family": "detection",
            "simhash": "0101",
            "content_sha256": " ab ",
            "four_gates": None,
            "dedup_compared_vs": None,
        }
    )
    assert card.elite_cell == "governance|detection", "缺格坐标按域|族拼装"
    assert card.mechanism_family == "detection"
    assert card.simhash == 0b0101, "BIT 位串转 int"
    assert card.content_sha256 == "ab" and card.four_gates == {} and card.dedup_compared_vs == []
    fallback = IntakeCard.from_row(
        {
            "card_id": "CC-2",
            "domain_id": "trading_algo",
            "funnel_stage": "L0",
            "elite_cell": None,
            "mechanism_family": None,
            "simhash": 7,
        }
    )
    assert fallback.mechanism_family == "unclassified", "缺族退 unclassified"
    assert fallback.simhash == 7, "int 直接透传"


def test_store_rejects_bad_schema_name() -> None:
    with pytest.raises(ValueError, match="schema 名不合规"):
        CardStore(schema="pg_catalog")
    with pytest.raises(ValueError, match="schema 名不合规"):
        CardStore(schema="")


# ---------------------------------------------------------------- DB（test_schema 临时库）


def test_insert_and_get_roundtrip(test_schema: str) -> None:
    store = CardStore(schema=test_schema)
    store.insert(_draft("CC-store-0001", simhash=0b1100))
    card = store.get("CC-store-0001")
    assert card is not None
    assert card.funnel_stage == "L0" and card.simhash == 0b1100
    assert card.elite_cell == "governance|detection"
    assert store.get("CC-not-exist") is None
    assert store.stage_of("CC-store-0001") == "L0"
    assert store.stage_of("CC-not-exist") is None


def test_transition_forward_and_reject_then_terminal(test_schema: str) -> None:
    store = CardStore(schema=test_schema)
    store.insert(_draft("CC-store-0002"))
    assert store.transition("CC-store-0002", "L1") == "forward_one_step"
    assert store.stage_of("CC-store-0002") == "L1"
    assert store.transition("CC-store-0002", "rejected", rejection_reason="L3 清洗不可洗退回") == "reject_allowed"
    card = store.get("CC-store-0002")
    assert card is not None and card.funnel_stage == "rejected"
    with pytest.raises(RuntimeError, match="rejected_is_terminal_no_revive"):
        store.transition("CC-store-0002", "L2")


def test_transition_illegal_jump_fail_closed(test_schema: str) -> None:
    store = CardStore(schema=test_schema)
    store.insert(_draft("CC-store-0003"))
    with pytest.raises(RuntimeError, match="illegal_jump:L0->E2"):
        store.transition("CC-store-0003", "E2")
    with pytest.raises(RuntimeError, match="card_not_found"):
        store.transition("CC-ghost", "L1")
    assert store.transition("CC-store-0003", "L0") == "noop_same_stage", "同态幂等"


def test_record_score_ranks_and_benches_fourth(test_schema: str) -> None:
    store = CardStore(schema=test_schema)
    ids = [f"CC-elite-{i:04d}" for i in range(ELITE_KEEP_PER_CELL + 1)]
    for i, cid in enumerate(ids):
        store.insert(_draft(cid, domain_id="trading_algo", mechanism_family="prediction", simhash=0b10 + i))
    scores = [0.9, 0.8, 0.7, 0.6]
    ranked_out: dict[str, int] = {}
    for cid, score in zip(ids, scores, strict=True):
        out = store.record_score(cid, score, evidence_ref=f"ev:{cid}")
        assert out["cell"] == "trading_algo|prediction"
        ranked_out = dict(out["ranked"])
    assert ranked_out[ids[0]] == 1 and ranked_out[ids[1]] == 2 and ranked_out[ids[2]] == 3
    assert ranked_out[ids[3]] == ELITE_KEEP_PER_CELL + 1
    statuses = {cid: store.get(cid).elite_status for cid in ids if store.get(cid)}
    assert statuses[ids[3]] == "benched", "rank>3 置 benched（墓碑制不删）"
    assert statuses[ids[0]] == "active"
    with pytest.raises(RuntimeError, match="card_not_found"):
        store.record_score("CC-ghost", 1.0)


def test_list_by_stage_shape(test_schema: str) -> None:
    store = CardStore(schema=test_schema)
    store.insert(_draft("CC-store-0004"))
    rows = store.list_by_stage("L0")
    assert any(r["card_id"] == "CC-store-0004" for r in rows)
    with pytest.raises(ValueError, match="unknown_stage"):
        store.list_by_stage("bogus")
