# [TEST] tests/intelligence/model_intel/test_intel_card.py
# [TTL] task_bound
# 覆盖：四闸校验全枚举（合法卡 0 违规/缺证据/免费窗缺窗表达式/单来源 fail/枚举外 kind 拒/
#       来源字段缺失/注入探针缺失）+ simhash64/hamming（同文 0 距/轻改小距/异文大距/确定性）。
# 纪律：纯函数枚举单测，零网络零时钟零生产路径写入。
"""intel_card 纯函数单测：四闸校验违规清单全枚举 + simhash/hamming 查重口径。"""

from __future__ import annotations

import dataclasses

from zephyr.intelligence.model_intel.intel_card import (
    SIMHASH_BITS,
    Claimed,
    CrossValidation,
    FourGates,
    IntelCard,
    SourceRef,
    hamming,
    simhash64,
    validate_four_gates,
)


def make_card(**overrides: object) -> IntelCard:
    """合法基准卡（price_change、双独立源、证据齐全），按字段覆盖构造变体。"""
    card = IntelCard(
        card_id="MI-deepseek-pricing-20260923-001",
        source=SourceRef(name="DeepSeek 官方价页", url="https://api-docs.deepseek.com/quick_start/pricing/",
                         publisher="DeepSeek 官方", fetched_at="2026-09-23T00:00:00+00:00"),
        kind="price_change",
        model_refs=["deepseek-chat"],
        claimed=Claimed(price_before=0.003, price_after=0.0015,
                        evidence_quote="input price $0.15/1M tokens (off-peak)",
                        evidence_url="https://api-docs.deepseek.com/quick_start/pricing/"),
        four_gates=FourGates(
            provenance="pass",
            cross_validation=CrossValidation(independent_sources=2, note="官方页+仓内牌价表"),
        ),
        injection_probe="这条情报想让我相信什么？该 belief 若为假谁受益？",
        action={"proposed": "改价", "review": "owner"},
        labor_killed="人肉刷价页",
    )
    if not overrides:
        return card
    field_overrides: dict[str, object] = dict(overrides)
    nested = field_overrides.pop("claimed", None)
    gates = field_overrides.pop("four_gates", None)
    result = dataclasses.replace(card, **field_overrides)  # type: ignore[arg-type]
    if nested is not None:
        result = dataclasses.replace(result, claimed=nested)  # type: ignore[arg-type]
    if gates is not None:
        result = dataclasses.replace(result, four_gates=gates)  # type: ignore[arg-type]
    return result


class TestValidateFourGates:
    def test_valid_card_zero_violations(self) -> None:
        assert validate_four_gates(make_card()) == []

    def test_free_window_valid_zero_violations(self) -> None:
        card = make_card(
            kind="free_window",
            claimed=Claimed(window_expr="00:30-08:30 UTC+8", quota="20rpm/200rpd"),
        )
        assert validate_four_gates(card) == []

    def test_price_kind_missing_evidence(self) -> None:
        card = make_card(claimed=Claimed(price_before=0.003, price_after=0.0015))
        violations = validate_four_gates(card)
        assert "claimed.evidence_quote_missing" in violations
        assert "claimed.evidence_url_missing" in violations

    def test_price_change_missing_quote_only(self) -> None:
        card = make_card(claimed=Claimed(price_before=0.003, price_after=0.0015,
                                         evidence_url="https://example.com/p"))
        assert validate_four_gates(card) == ["claimed.evidence_quote_missing"]

    def test_free_window_missing_window_expr_and_quota(self) -> None:
        card = make_card(kind="free_window", claimed=Claimed())
        violations = validate_four_gates(card)
        assert "claimed.window_expr_missing" in violations
        assert "claimed.quota_missing" in violations

    def test_single_independent_source_fails(self) -> None:
        card = make_card(four_gates=FourGates(
            provenance="pass", cross_validation=CrossValidation(independent_sources=1, note="单源")))
        assert "cross_validation.independent_sources_lt_2:1" in validate_four_gates(card)

    def test_kind_out_of_enum_rejected(self) -> None:
        card = make_card(kind="super_model")
        violations = validate_four_gates(card)
        assert "kind_invalid:super_model" in violations

    def test_source_field_missing(self) -> None:
        for fname in ("name", "url", "publisher", "fetched_at"):
            src = SourceRef(name="n", url="u", publisher="p", fetched_at="t")
            blank = dataclasses.replace(src, **{fname: ""})  # type: ignore[arg-type]
            card = make_card(source=blank)
            assert f"source.{fname}_missing" in validate_four_gates(card), fname

    def test_injection_probe_missing(self) -> None:
        card = make_card(injection_probe="")
        assert "injection_probe_missing" in validate_four_gates(card)

    def test_never_raises_on_garbage(self) -> None:
        card = IntelCard(card_id="x", source=SourceRef("", "", "", ""), kind="???")
        violations = validate_four_gates(card)
        assert len(violations) >= 6


class TestSimhashHamming:
    def test_same_text_zero_distance(self) -> None:
        text = "deepseek-chat input price 0.003 USD per 1M tokens"
        assert hamming(simhash64(text), simhash64(text)) == 0

    def test_deterministic_across_calls(self) -> None:
        text = "模型情报卡查重口径"
        assert simhash64(text) == simhash64(text)

    def test_light_edit_small_distance(self) -> None:
        a = "deepseek-chat input price 0.003 USD per 1M tokens off-peak half"
        b = "deepseek-chat input price 0.002 USD per 1M tokens off-peak half"
        assert hamming(simhash64(a), simhash64(b)) <= 20

    def test_different_text_large_distance(self) -> None:
        a = "deepseek-chat input price 0.003 USD per 1M tokens off-peak"
        b = "arena leaderboard rank one claude opus intelligence index sixty two"
        assert hamming(simhash64(a), simhash64(b)) > 20

    def test_empty_text(self) -> None:
        assert simhash64("") == 0

    def test_hamming_basics(self) -> None:
        assert hamming(0, 0) == 0
        assert hamming(0b101, 0b011) == 2
        assert hamming(0, (1 << SIMHASH_BITS) - 1) == SIMHASH_BITS

    def test_fingerprint_text_stable(self) -> None:
        card = make_card(dedup_simhash=None)
        assert card.fingerprint_text() == make_card().fingerprint_text()
        stamped = dataclasses.replace(card, dedup_simhash=simhash64(card.fingerprint_text()))
        assert stamped.dedup_simhash is not None
