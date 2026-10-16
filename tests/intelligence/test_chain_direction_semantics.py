"""chain_direction_semantics＋resolve_directed 测试（st-infoaxis P2 传导链）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.intelligence.chain_direction_semantics import (  # noqa: E402
    DIRECTION_MATRIX,
    EVENT_TYPES,
    classify_event,
    effective_sign,
    role_sign,
)
from zephyr.intelligence.chain_impact_resolver import ChainImpactResolver  # noqa: E402
from zephyr.intelligence.news_chain_node_linker import ChainNodeHit  # noqa: E402


def test_classify_longest_word_priority_and_miss():
    assert classify_event("锂矿价格大幅上涨，多家中游厂承压") == "price_up"
    assert classify_event("海外制裁导致芯片断供") == "supply_cut"
    assert classify_event("公司中标 10 亿元大单") == "big_order"
    assert classify_event("今日天气晴朗") is None
    assert classify_event("") is None


def test_matrix_covers_all_event_types():
    for et in EVENT_TYPES:
        assert DIRECTION_MATRIX.get(et), et
    assert DIRECTION_MATRIX["price_up"]["customer_side"] == -1
    assert DIRECTION_MATRIX["supply_cut"]["substitute_side"] == 1


def test_role_sign_unknown_fail_open():
    assert role_sign(None, "supplier_side") == 1
    assert role_sign("price_up", "nonexistent_side") == 1
    assert effective_sign(1, "price_up", "customer_side") == -1
    assert effective_sign(-1, "price_up", "supplier_side") == -1


def _resolver():
    return ChainImpactResolver(
        edges=[("ND-A", "ND-B", "supplies_to"), ("ND-A", "ND-C", "structure")],
        nodes=[
            ("ND-A", "c1", "锂", "L1"),
            ("ND-B", "c1", "电池", "L2"),
            ("ND-C", "c1", "矿", "L1"),
        ],
        company_rows=[
            ("ND-A", "600001.SH", "core", 1.0),
            ("ND-B", "300002.SZ", "core", 1.0),
            ("ND-C", "000003.SZ", "core", 1.0),
        ],
    )


def _hit():
    return ChainNodeHit(
        node_id="ND-A",
        chain_id="c1",
        node_name="锂",
        tier="L1",
        confidence=0.9,
        match_source="lex",
        matched_term="锂",
        ambiguous=False,
    )


def test_resolve_directed_backward_compat():
    r = _resolver()
    legacy = r.resolve([_hit()], 0.8)
    none_type = r.resolve_directed([_hit()], 0.8, None)
    assert [(t.symbol, t.direction) for t in legacy] == [(t.symbol, t.direction) for t in none_type]


def test_resolve_directed_price_up_flips_customer():
    r = _resolver()
    res = {t.symbol: t.direction for t in r.resolve_directed([_hit()], 0.8, "price_up")}
    assert res["600001.SH"] == 1  # 供方受益
    assert res["300002.SZ"] == -1  # supplies_to 客户侧反号（W4 反例闭合）
    assert res["000003.SZ"] == 1  # structure 边 role 未知→同向


def test_resolve_directed_supply_cut_double_negative():
    r = _resolver()
    res = {t.symbol: t.direction for t in r.resolve_directed([_hit()], 0.8, "supply_cut")}
    assert res["600001.SH"] == -1  # 断供方受损
    assert res["300002.SZ"] == -1  # 原需方断料
