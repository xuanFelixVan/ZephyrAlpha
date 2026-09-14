# [BLUEPRINT] MOD-BT-193 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_graph_enrich_staging
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-193 graph_enrich_staging 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM：prompt/解析/校验纯函数验证
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-193 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1D 图谱增补 P0 纯函数单测——prompt 边界/抽取解析/校验门，零网络。"""
from __future__ import annotations

import json

from scripts.backtest.graph_enrich_staging import (
    CONFIDENCE_FLOOR,
    build_extract_prompt,
    parse_extraction,
    validate_extraction,
)


class TestExtractPrompt:
    def test_deterministic_and_bounded(self):
        p1 = build_extract_prompt("标题", "正文内容" * 50)
        p2 = build_extract_prompt("标题", "正文内容" * 50)
        assert p1 == p2
        assert "标题" in p1 and "禁止编造" in p1 and "discovered" in p1

    def test_anti_hallucination_written(self):
        p = build_extract_prompt("t", "c")
        assert "原文摘录" in p and "禁止编造正文没有的名字" in p


class TestParseExtraction:
    def test_discovered_object(self):
        raw = json.dumps({"discovered": True, "supplier": "A公司", "product": "硅料",
                          "customer": "B公司", "confidence": 0.9, "evidence": "A向B供货"})
        tr = parse_extraction(raw)
        assert tr["discovered"] is True and tr["supplier"] == "A公司"

    def test_not_discovered(self):
        tr = parse_extraction(json.dumps({"discovered": False, "reason": "无关系"}))
        assert tr["discovered"] is False

    def test_garbage_parse_fail(self):
        tr = parse_extraction("看不出供应链关系")
        assert tr["discovered"] is False and tr["reason"] == "parse_fail"


class TestValidateExtraction:
    def _ok(self):
        return {"discovered": True, "supplier": "A公司", "product": "硅料",
                "customer": "B公司", "confidence": 0.9, "evidence": "原文"}

    def test_valid_passes(self):
        ok, why = validate_extraction(self._ok())
        assert ok, why

    def test_same_party_rejected(self):
        e = self._ok(); e["customer"] = e["supplier"]
        ok, why = validate_extraction(e)
        assert not ok and "supplier=customer" in why

    def test_low_confidence_rejected(self):
        e = self._ok(); e["confidence"] = 0.5
        ok, why = validate_extraction(e)
        assert not ok and "0.5" in why

    def test_empty_evidence_rejected(self):
        e = self._ok(); e["evidence"] = "  "
        ok, why = validate_extraction(e)
        assert not ok and "幻觉" in why

    def test_confidence_floor(self):
        assert CONFIDENCE_FLOOR == 0.7


if __name__ == "__main__":  # pragma: no cover
    import pytest
    pytest.main([__file__, "-v"])
