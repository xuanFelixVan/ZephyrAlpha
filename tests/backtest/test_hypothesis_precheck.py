# [BLUEPRINT] MOD-BT-091 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_hypothesis_precheck
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-091 hypothesis_precheck 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数测试零 IO 零 LLM（禁触生产数据路径与网络）；解析器对格式漂移的映射表穷举
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-091 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E2 假说预审纯函数核单测——prompt 确定性/回复强解析/理由码体系闭合，零 IO 零 LLM。"""
from __future__ import annotations

import json

import pytest

from scripts.backtest.hypothesis_precheck import (
    DEFER_REASONS,
    LOW_CONFIDENCE,
    REASON_PASS,
    REJECT_REASONS,
    VERDICT_DEFER,
    VERDICT_PASS,
    VERDICT_REJECT,
    build_prompt,
    parse_reply,
)


class TestPrompt:
    def test_deterministic_and_contains_hypothesis(self):
        h = "做多黄金环节——三高共振"
        p1, p2 = build_prompt(h, "D"), build_prompt(h, "D")
        assert p1 == p2
        assert h in p1
        assert "D" in p1

    def test_six_questions_present(self):
        p = build_prompt("x")
        for token in ("机制", "前视", "成本", "可证伪", "同义反复", "边界"):
            assert token in p

    def test_reason_code_vocabulary_in_prompt(self):
        p = build_prompt("x")
        for rc in (REASON_PASS, *REJECT_REASONS, "defer_low_confidence"):
            assert rc in p, rc


class TestReasonCodeSystem:
    def test_vocabulary_disjoint_and_closed(self):
        assert REASON_PASS not in REJECT_REASONS
        assert not (set(REJECT_REASONS) & set(DEFER_REASONS))
        assert len(REJECT_REASONS) == 6 and len(DEFER_REASONS) == 3

    def test_low_confidence_threshold(self):
        assert 0 < LOW_CONFIDENCE < 1


class TestParseReply:
    def test_clean_json_pass(self):
        raw = json.dumps({"verdict": "pass", "reason_code": REASON_PASS,
                          "confidence": 0.8, "rationale": "风险溢价机制成立"})
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_PASS and v["reason_code"] == REASON_PASS
        assert v["confidence"] == 0.8

    def test_clean_json_reject(self):
        raw = json.dumps({"verdict": "reject", "reason_code": "reject_lookahead",
                          "confidence": 0.9, "rationale": "用到未来数据"})
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_REJECT and v["reason_code"] == "reject_lookahead"

    def test_json_wrapped_in_noise(self):
        raw = f"模型思考中……{json.dumps({'verdict': 'pass', 'reason_code': REASON_PASS, 'confidence': 0.7, 'rationale': 'ok'})}以上。"
        assert parse_reply(raw)["verdict"] == VERDICT_PASS

    def test_keyword_fallback_pass(self):
        v = parse_reply("我判断该假说 pass，机制是风险溢价")
        assert v["verdict"] == VERDICT_PASS and v["reason_code"] == REASON_PASS

    def test_keyword_fallback_reject_reason_code(self):
        v = parse_reply("该想法 reject：reject_cost_prohibitive 成本太高")
        assert v["verdict"] == VERDICT_REJECT and v["reason_code"] == "reject_cost_prohibitive"

    def test_garbage_becomes_defer_parse_fail(self):
        v = parse_reply("嗯……这个想法大概也许可能行吧")
        assert v["verdict"] == VERDICT_DEFER and v["reason_code"] == "defer_parse_fail"

    def test_empty_and_none_become_defer(self):
        for bad in ("", None):
            v = parse_reply(bad)
            assert v["verdict"] == VERDICT_DEFER

    def test_reject_with_unknown_reason_maps_to_defer_low_confidence(self):
        raw = json.dumps({"verdict": "reject", "reason_code": "reject_我不认识",
                          "confidence": 0.9, "rationale": "怪理由"})
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_DEFER and v["reason_code"] == "defer_low_confidence"

    def test_defer_roundtrip(self):
        raw = json.dumps({"verdict": "defer", "reason_code": "defer_low_confidence",
                          "confidence": 0.3, "rationale": "说不准"})
        v = parse_reply(raw)
        assert v["verdict"] == VERDICT_DEFER and v["confidence"] == 0.3

    def test_non_numeric_confidence_tolerated(self):
        raw = json.dumps({"verdict": "pass", "reason_code": REASON_PASS,
                          "confidence": "高", "rationale": "x"})
        assert parse_reply(raw)["confidence"] is None

    def test_deterministic(self):
        raw = '{"verdict": "reject", "reason_code": "reject_tautology", "confidence": 0.75, "rationale": "动量同义反复"}'
        assert parse_reply(raw) == parse_reply(raw)


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
