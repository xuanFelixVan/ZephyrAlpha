# [BLUEPRINT] MOD-BT-190 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_hypothesis_translator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-190 hypothesis_translator 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM：prompt/解析/阴性档案纯函数验证
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-190 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E3 假说轨翻译纯函数单测——prompt 边界/翻译解析/阴性档案，零网络。"""
from __future__ import annotations

from scripts.backtest.hypothesis_translator import (
    parse_translation,
    build_translation_prompt,
)


class TestTranslationPrompt:
    def test_deterministic_and_bounded(self):
        p1 = build_translation_prompt("低PE假说", ["ret_1d"], ["add", "log"])
        p2 = build_translation_prompt("低PE假说", ["ret_1d"], ["add", "log"])
        assert p1 == p2
        assert "低PE假说" in p1 and "add" in p1 and "ret_1d" in p1

    def test_boundary_written_into_prompt(self):
        p = build_translation_prompt("x", ["ret_1d"], ["add"])
        for token in ("translatable=false", "事件窗口", "禁止硬翻", "交易对手三问"):
            assert token in p


class TestParseTranslation:
    def test_translatable_object(self):
        raw = '{"translatable": true, "expression": "neg(ret_1d)", "description": "d", "mechanism": "m", "top_n": 15}'
        tr = parse_translation(raw)
        assert tr["translatable"] is True and tr["expression"] == "neg(ret_1d)"
        assert tr["top_n"] == 15

    def test_refusal_object(self):
        raw = '{"translatable": false, "refusal_reason": "涉及财报公告"}'
        tr = parse_translation(raw)
        assert tr["translatable"] is False
        assert "财报" in tr["refusal_reason"]

    def test_garbage_becomes_refusal(self):
        tr = parse_translation("我觉得这条没法翻译")
        assert tr["translatable"] is False and tr["refusal_reason"] == "parse_fail"

    def test_think_block_noise_tolerated(self):
        # r1 类推理模型 <think> 尾噪声：仍能提取 JSON 对象
        raw = '推理过程 {"x": 1} …… 结论 {"translatable": false, "refusal_reason": "r"}'
        assert parse_translation(raw)["translatable"] is False


if __name__ == "__main__":  # pragma: no cover
    import pytest
    pytest.main([__file__, "-v"])
