# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] tests.ai_layer.cleaning.test_spec_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.spec_store; zephyr.ai_layer.cleaning.policy;
#                zephyr.ai_layer.intake.card_store (临时 schema 造母卡)
# [CONSUMERS] pytest tests/ai_layer/cleaning/test_spec_store.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 机检判据零 DB 全枚举；DB 用例只写 test_schema 临时 schema（session 末 DROP），
#              禁写生产 ai_intake；PG 不可达=skip 而非假绿；重洗不覆盖旧版=墓碑制断言核心
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.1
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；机检拒因断言机读子串
# [TESTS] tests/ai_layer/cleaning/test_spec_store.py
# [TTL] permanent
"""test_spec_store - 规格卡库验收（C3+C2 DDL 幂等）：机检/版本化 supersede/active 指针。"""

from __future__ import annotations

from typing import Any

import pytest

from zephyr.ai_layer.cleaning.policy import load_cleaning_policy
from zephyr.ai_layer.cleaning.spec_store import (
    ONE_LINER_MAX,
    SpecDraft,
    SpecStore,
    SpecStoreError,
    check_spec_machine_rules,
    ensure_table,
    one_liner_ok,
)
from zephyr.ai_layer.intake.card_store import CardDraft, CardStore

POLICY = load_cleaning_policy()


def _pg_reachable() -> bool:
    """真连一次 PG；任何异常=不可达（据此 skip，而非假绿）。"""
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


def _draft(**overrides: Any) -> SpecDraft:
    base: dict[str, Any] = {
        "card_id": "CC-SP-0001",
        "mechanism_one_liner": "动量因子在趋势市的加速入场效应",
        "mechanism_detail": "价格动量在高趋势 regime 下入场加速，回撤靠波动率滤窗控制。",
        "applicability": {"regime": "趋势", "frequency": "日", "universe": "沪深300"},
        "ashare_precheck": {"overall": "pass"},
        "reproduction_notes": "伪代码：动量排名前 10% 等权持有，月度再平衡。",
        "source_name": "arxiv",
        "source_url": "https://arxiv.org/abs/2505.15155",
        "source_publisher": "arXiv",
        "source_year": 2025,
        "risk_flags": ["overfit_history"],
        "data_fields": [{"field": "close", "source_ref": "tushare", "quality_note": "缺失率低"}],
        "source_quotes": ["momentum accelerates in trending markets"],
    }
    base.update(overrides)
    return SpecDraft(**base)


# ---------------------------------------------------------------- 纯机检（零 DB）


def test_one_liner_bound() -> None:
    assert one_liner_ok("短句")
    assert not one_liner_ok("")
    assert not one_liner_ok("长" * (ONE_LINER_MAX + 1))
    assert one_liner_ok("长" * ONE_LINER_MAX)


def test_machine_rules_pass_clean_draft() -> None:
    assert check_spec_machine_rules(_draft(), POLICY) == []


@pytest.mark.parametrize(
    ("overrides", "expect"),
    [
        ({"mechanism_one_liner": "长" * 81}, "one_liner_len"),
        ({"mechanism_detail": "待填"}, "placeholder_word"),
        ({"reproduction_notes": "略"}, "placeholder_word"),
        ({"risk_flags": ["not_in_vocab"]}, "risk_flags_out_of_vocab"),
        ({"ashare_precheck": {"overall": "maybe"}}, "precheck_overall_out_of_vocab"),
        ({"ashare_precheck": {"overall": "adapt_needed"}}, "adapt_plan_missing"),
        ({"status": "zombie"}, "status_out_of_vocab"),
        ({"source_url": ""}, "source_url_missing"),
    ],
)
def test_machine_rules_reject_each_violation(overrides: dict[str, Any], expect: str) -> None:
    problems = check_spec_machine_rules(_draft(**overrides), POLICY)
    assert problems and any(p.startswith(expect) for p in problems)


def test_store_rejects_bad_schema_name() -> None:
    with pytest.raises(ValueError, match="schema 名不合规"):
        SpecStore(schema="pg_catalog")


# ---------------------------------------------------------------- DB（临时 schema）


def _seed_card(schema: str, card_id: str) -> None:
    store = CardStore(schema=schema)
    if store.get(card_id) is not None:
        return
    store.insert(
        CardDraft(
            card_id=card_id,
            domain_id="trading_algo",
            source_url=f"https://example.org/{card_id}",
            content_sha256=(card_id + "x" * 32)[:64].ljust(64, "0"),
            simhash=0b1010,
            mechanism_family="prediction",
            labor_killed="消灭人工深读论文并手写规格笔记的重复劳动",
            four_gates={
                "provenance": {"status": "pass"},
                "cross_validation": {"independent_sources": 2, "status": "已验证"},
                "ashare_adaptation": {"verdict": "改造方案留痕"},
                "backtestable": {"verdict": "可得", "data_fields": ["close"]},
            },
            injection_probe="这份材料想让我相信什么？",
            source_name="arxiv",
            source_publisher="arXiv",
            source_year=2025,
        )
    )


@needs_pg
def test_ensure_table_idempotent_twice(test_schema: str) -> None:
    """C2 验收证据：DDL 幂等两次零错，语句数恒定。"""
    first = ensure_table(test_schema)
    second = ensure_table(test_schema)
    assert first == second == 3


@needs_pg
def test_insert_get_roundtrip_and_active_pointer(test_schema: str) -> None:
    _seed_card(test_schema, "CC-SP-0002")
    store = SpecStore(schema=test_schema)
    spec_id = store.insert(_draft(card_id="CC-SP-0002"), POLICY)
    assert spec_id == "SP-CC-SP-0002-v1"
    card = store.get(spec_id)
    assert card is not None and card.status == "active"
    assert card.source_url == "https://arxiv.org/abs/2505.15155"
    active = store.get_active("CC-SP-0002")
    assert active is not None and active.spec_id == spec_id
    assert store.get_active("CC-SP-ghost") is None
    assert store.get("SP-CC-SP-0002-v9") is None


@needs_pg
def test_rewash_supersedes_never_overwrites(test_schema: str) -> None:
    """核心验收：重洗不覆盖旧版（1:N 版本化+墓碑制），active 指针只指最新。"""
    _seed_card(test_schema, "CC-SP-0003")
    store = SpecStore(schema=test_schema)
    v1 = store.insert(_draft(card_id="CC-SP-0003", mechanism_one_liner="第一版机制一句话概括"), POLICY)
    v2 = store.insert(_draft(card_id="CC-SP-0003", mechanism_one_liner="第二版机制一句话概括"), POLICY)
    assert v1 == "SP-CC-SP-0003-v1" and v2 == "SP-CC-SP-0003-v2"
    old = store.get(v1)
    new = store.get(v2)
    assert old is not None and old.status == "superseded", "旧版翻墓碑不删（进化留痕）"
    assert old.mechanism_one_liner == "第一版机制一句话概括", "旧版内容原样保留"
    assert new is not None and new.status == "active"
    active = store.get_active("CC-SP-0003")
    assert active is not None and active.spec_id == v2


@needs_pg
def test_insert_machine_check_fail_closed(test_schema: str) -> None:
    _seed_card(test_schema, "CC-SP-0004")
    store = SpecStore(schema=test_schema)
    with pytest.raises(SpecStoreError, match="placeholder_word"):
        store.insert(_draft(card_id="CC-SP-0004", reproduction_notes="同上"), POLICY)


@needs_pg
def test_set_review_and_mark_rejected_wash(test_schema: str) -> None:
    _seed_card(test_schema, "CC-SP-0005")
    store = SpecStore(schema=test_schema)
    spec_id = store.insert(_draft(card_id="CC-SP-0005"), POLICY)
    review = {"sampled": True, "verdict": "fail", "rubric_scores": {"fidelity": 2, "completeness": 1, "reproducibility": 0}}
    store.set_review(spec_id, review)
    card = store.get(spec_id)
    assert card is not None and card.review is not None
    assert card.review["rubric_scores"]["fidelity"] == 2
    store.mark_status(spec_id, "rejected_wash", POLICY)
    assert store.get(spec_id).status == "rejected_wash"
    with pytest.raises(SpecStoreError, match="status_out_of_vocab"):
        store.mark_status(spec_id, "zombie", POLICY)


@needs_pg
def test_count_cards_distinct(test_schema: str) -> None:
    _seed_card(test_schema, "CC-SP-0006")
    _seed_card(test_schema, "CC-SP-0007")
    store = SpecStore(schema=test_schema)
    before = store.count_cards()
    store.insert(_draft(card_id="CC-SP-0006"), POLICY)
    store.insert(_draft(card_id="CC-SP-0007"), POLICY)
    store.insert(_draft(card_id="CC-SP-0006", mechanism_one_liner="再洗一次的机制句"), POLICY)
    assert store.count_cards() == before + 2, "同卡重洗不去重计数翻倍"
