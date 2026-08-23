# [A_test] module_id: MOD-SIG-076 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-076 | 待统筹登记 | 缺口总账 GAP-F-42 行
# [MODULE] tests.plan_engine.test_evidence_chain_decision
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""证据链决策数据结构（MOD-SIG-076，GAP-F-42）施工验证测试。

覆盖：
- 正常构建：五字段保留、条目 strip/剔空、subject/as_of 透传；
- fail-closed：thesis/catalyst/invalidation 空或空白拒；evidence_for/against 全空拒；
  as_of 日期格式/真实性强拒；
- 生成器填充校验：missing_fields 诊断列名；build_evidence_chain 缺字段一次性列全；
- 契约：frozen 不可变；to_dict/from_dict JSON 往返一致。
全程内存构造，无 DB 无 LLM。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.plan_engine.evidence_chain_decision import (
    REQUIRED_CHAIN_FIELDS,
    EvidenceChain,
    build_evidence_chain,
    missing_fields,
)

_GOOD = {
    "thesis": "主线龙头二波接力，板块梯队完整",
    "catalyst": "业绩预告超预期 + 板块政策催化",
    "invalidation": "跌破 20 日线且板块退潮",
    "evidence_for": ["封单比 0.8 板块第一", "北向三日净买"],
    "evidence_against": ["大盘情绪弱修复"],
}


def _build(**overrides) -> EvidenceChain:
    payload = dict(_GOOD)
    payload.update(overrides)
    return EvidenceChain(
        thesis=payload["thesis"],
        catalyst=payload["catalyst"],
        invalidation=payload["invalidation"],
        evidence_for=tuple(payload["evidence_for"]),
        evidence_against=tuple(payload["evidence_against"]),
        subject_id=payload.get("subject_id", "000001.SZ"),
        as_of=payload.get("as_of"),
    )


class TestEvidenceChainBuild:
    def test_valid_build_preserves_fields(self) -> None:
        chain = _build(as_of="2026-08-21")
        assert chain.thesis == _GOOD["thesis"]
        assert chain.catalyst == _GOOD["catalyst"]
        assert chain.invalidation == _GOOD["invalidation"]
        assert chain.evidence_for == tuple(_GOOD["evidence_for"])
        assert chain.evidence_against == tuple(_GOOD["evidence_against"])
        assert chain.subject_id == "000001.SZ"
        assert chain.as_of == "2026-08-21"

    def test_items_stripped_and_empties_dropped(self) -> None:
        chain = _build(evidence_for=["  有效条目  ", "", "   "])
        assert chain.evidence_for == ("有效条目",)

    @pytest.mark.parametrize("field_name", ["thesis", "catalyst", "invalidation"])
    def test_blank_text_field_rejected(self, field_name: str) -> None:
        with pytest.raises(ValueError, match=field_name):
            _build(**{field_name: "   "})

    @pytest.mark.parametrize("field_name", ["evidence_for", "evidence_against"])
    def test_empty_evidence_rejected(self, field_name: str) -> None:
        with pytest.raises(ValueError, match=field_name):
            _build(**{field_name: ["", "  "]})

    def test_as_of_format_rejected(self) -> None:
        with pytest.raises(ValueError, match="as_of"):
            _build(as_of="2026/08/21")

    def test_as_of_unreal_date_rejected(self) -> None:
        with pytest.raises(ValueError, match="as_of"):
            _build(as_of="2026-02-30")

    def test_frozen_immutable(self) -> None:
        chain = _build()
        with pytest.raises(dataclasses.FrozenInstanceError):
            chain.thesis = "改写"  # type: ignore[misc]


class TestGeneratorFillValidation:
    def test_missing_fields_none_when_complete(self) -> None:
        assert missing_fields(_GOOD) == ()

    def test_missing_fields_lists_all_gaps(self) -> None:
        miss = missing_fields({"thesis": "有", "evidence_for": ["x"]})
        assert "catalyst" in miss
        assert "invalidation" in miss
        assert "evidence_against" in miss
        assert "thesis" not in miss
        assert "evidence_for" not in miss

    def test_missing_fields_blank_counts_as_missing(self) -> None:
        miss = missing_fields({**_GOOD, "catalyst": "  ", "evidence_against": []})
        assert "catalyst" in miss
        assert "evidence_against" in miss

    def test_build_ok(self) -> None:
        chain = build_evidence_chain(_GOOD)
        assert isinstance(chain, EvidenceChain)
        assert chain.subject_id == ""

    def test_build_fail_closed_lists_missing(self) -> None:
        with pytest.raises(ValueError, match="catalyst") as exc:
            build_evidence_chain({"thesis": "只有论点"})
        for name in ("catalyst", "invalidation", "evidence_for", "evidence_against"):
            assert name in str(exc.value)

    def test_build_passes_subject_and_as_of(self) -> None:
        chain = build_evidence_chain({**_GOOD, "subject_id": " 600519.SH ", "as_of": "2026-08-21"})
        assert chain.subject_id == "600519.SH"
        assert chain.as_of == "2026-08-21"


class TestSerialization:
    def test_to_dict_json_round_trip(self) -> None:
        chain = _build(as_of="2026-08-21")
        text = json.dumps(chain.to_dict(), ensure_ascii=False)
        restored = EvidenceChain.from_dict(json.loads(text))
        assert restored == chain

    def test_required_fields_constant(self) -> None:
        assert set(REQUIRED_CHAIN_FIELDS) == {
            "thesis",
            "catalyst",
            "invalidation",
            "evidence_for",
            "evidence_against",
        }
