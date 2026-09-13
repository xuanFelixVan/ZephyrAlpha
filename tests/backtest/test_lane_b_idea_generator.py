# [BLUEPRINT] MOD-BT-150 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_lane_b_idea_generator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-150 lane_b_idea_generator 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数测试零 IO 零 LLM（tmp_path 外禁写；不触生产 intake 路径）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-150 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1B 车道B 纯函数核单测——生成 prompt/假说解析/内容寻址 id/出生证，零 IO 零 LLM。"""
from __future__ import annotations

import json

import pytest

from scripts.backtest.lane_b_idea_generator import (
    SEED_THEMES,
    attach_birth_certificate,
    build_generation_prompt,
    make_candidate_id,
    parse_ideas,
)


class TestSeedThemes:
    def test_twelve_distinct_themes(self):
        assert len(SEED_THEMES) == 12
        assert len(set(SEED_THEMES)) == 12


class TestGenerationPrompt:
    def test_deterministic_with_theme_and_n(self):
        p1, p2 = build_generation_prompt("动量", 3), build_generation_prompt("动量", 3)
        assert p1 == p2
        assert "动量" in p1 and "3" in p1

    def test_guardrails_present(self):
        p = build_generation_prompt("反转", 1)
        for token in ("交易对手", "T 日收盘", "不涉及做空"):
            assert token in p


class TestParseIdeas:
    def _idea(self, h: str = "低波动股票长期跑赢") -> dict:
        return {"hypothesis_zh": h, "mechanism_hint": "风险溢价", "horizon": "20日",
                "universe": "沪深300"}

    def test_clean_array(self):
        raw = json.dumps([self._idea(), self._idea("放量突破买入")])
        out = parse_ideas(raw)
        assert len(out) == 2 and out[0]["hypothesis_zh"] == "低波动股票长期跑赢"

    def test_array_wrapped_in_noise(self):
        raw = f"好的，生成如下：\n{json.dumps([self._idea()])}\n请查收。"
        assert len(parse_ideas(raw)) == 1

    def test_object_extraction_fallback(self):
        raw = "前言 " + json.dumps(self._idea()) + " 中间 " + json.dumps(self._idea("另一条")) + " 结尾"
        assert len(parse_ideas(raw)) == 2

    def test_items_without_hypothesis_dropped(self):
        raw = json.dumps([{"mechanism_hint": "无假说字段"}, self._idea()])
        assert len(parse_ideas(raw)) == 1

    def test_garbage_returns_empty(self):
        assert parse_ideas("这个主题我想不出什么") == []
        assert parse_ideas("") == []
        assert parse_ideas(None) == []

    def test_deterministic(self):
        raw = json.dumps([self._idea()])
        assert parse_ideas(raw) == parse_ideas(raw)


class TestCandidateId:
    def test_content_addressed_stable(self):
        assert make_candidate_id("假说A") == make_candidate_id("假说A")
        assert make_candidate_id("假说A") != make_candidate_id("假说B")
        assert make_candidate_id("假说A ").startswith("CAND-")  # 空白已 strip 归一

    def test_md5_12_format(self):
        cid = make_candidate_id("x")
        assert len(cid) == len("CAND-") + 12


class TestBirthCertificate:
    def test_machine_written_and_stable_prompt_fp(self):
        ideas = [{"hypothesis_zh": "a"}, {"hypothesis_zh": "b"}]
        out = attach_birth_certificate(ideas, "E1B-20260914-000000", "动量", "PROMPT")
        assert all(x["birth_channel"] == "B" for x in out)
        assert all(x["birth_batch"] == "E1B-20260914-000000" for x in out)
        assert out[0]["birth_source"] == out[1]["birth_source"]
        assert "llm:" in out[0]["birth_source"] and "prompt_md5=" in out[0]["birth_source"]

    def test_no_mutation_of_input(self):
        ideas = [{"hypothesis_zh": "a"}]
        attach_birth_certificate(ideas, "E1B-x", "动量", "P")
        assert "birth_channel" not in ideas[0]


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
