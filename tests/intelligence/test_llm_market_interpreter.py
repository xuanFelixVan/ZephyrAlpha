# [BLUEPRINT] MOD-INT-MKT-INTERPRETER | tests/intelligence/test_llm_market_interpreter.py
# [MODULE] tests.intelligence.test_llm_market_interpreter
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.llm_market_interpreter
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT-MKT-INTERPRETER | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""LlmMarketInterpreter 单元测试——LLM 市场解读引擎（CAND-AISA-002 / B1-00118 / D-ALT-11）。

覆盖：
    1. 输入校验：三路全空 → ValueError fail-closed
    2. 双模选择：显式 local/api；缺省走 mode_selector；callable 缺失 fail-closed
    3. 结构化解析：JSON 合法 → MarketInterpretation；非 JSON/缺字段/越界 → InterpretationError
    4. 三路来源留痕 sources_used
    5. 审计链：audit_sink 外发；sink 异常不阻断（sink_errors 留痕）
    6. 信号边界：输出无下单语义字段
"""

from __future__ import annotations

import datetime
import json

import pytest

from zephyr.intelligence.llm_market_interpreter import (
    InterpretationError,
    LlmMarketInterpreter,
    MarketInputBundle,
)

NOW = datetime.datetime(2026, 8, 25, 20, 0, tzinfo=datetime.timezone.utc)

GOOD_JSON = json.dumps(
    {
        "theme": "白酒板块情绪修复",
        "sentiment": 0.35,
        "affected_symbols": ["600519", "000858"],
        "confidence": 0.72,
    },
    ensure_ascii=False,
)


def _bundle(**kw) -> MarketInputBundle:
    base = {"news": ("茅台中报超预期",), "research": (), "social": (), "as_of": NOW}
    base.update(kw)
    return MarketInputBundle(**base)


def _local_ok(prompt: str) -> str:
    return GOOD_JSON


def _api_ok(prompt: str) -> str:
    return GOOD_JSON


# ── 1. 输入校验 ──


def test_empty_bundle_fail_closed():
    it = LlmMarketInterpreter(local_llm=_local_ok)
    with pytest.raises(ValueError):
        it.interpret(_bundle(news=(), research=(), social=()), mode="local")


# ── 2. 双模选择 ──


def test_explicit_local_mode():
    it = LlmMarketInterpreter(local_llm=_local_ok, api_llm=_api_ok)
    out = it.interpret(_bundle(), mode="local")
    assert out.mode == "local"
    assert out.theme == "白酒板块情绪修复"
    assert out.sentiment == pytest.approx(0.35)
    assert out.affected_symbols == ("600519", "000858")
    assert out.confidence == pytest.approx(0.72)


def test_explicit_api_mode():
    it = LlmMarketInterpreter(local_llm=_local_ok, api_llm=_api_ok)
    out = it.interpret(_bundle(), mode="api")
    assert out.mode == "api"


def test_mode_selector_default():
    it = LlmMarketInterpreter(
        local_llm=_local_ok,
        api_llm=_api_ok,
        mode_selector=lambda as_of: "api",
    )
    out = it.interpret(_bundle())
    assert out.mode == "api"


def test_missing_callable_fail_closed():
    it = LlmMarketInterpreter(local_llm=_local_ok)
    with pytest.raises(ValueError):
        it.interpret(_bundle(), mode="api")
    it2 = LlmMarketInterpreter()
    with pytest.raises(ValueError):
        it2.interpret(_bundle(), mode="local")


def test_unknown_mode_fail_closed():
    it = LlmMarketInterpreter(local_llm=_local_ok)
    with pytest.raises(ValueError):
        it.interpret(_bundle(), mode="bogus")


def test_no_mode_and_no_selector_fail_closed():
    it = LlmMarketInterpreter(local_llm=_local_ok)
    with pytest.raises(ValueError):
        it.interpret(_bundle())


# ── 3. 结构化解析 Fail-Closed ──


def test_non_json_output_rejected():
    it = LlmMarketInterpreter(local_llm=lambda p: "市场看涨，关注白酒")
    with pytest.raises(InterpretationError):
        it.interpret(_bundle(), mode="local")


def test_missing_field_rejected():
    bad = json.dumps({"theme": "t", "sentiment": 0.1, "confidence": 0.5})
    it = LlmMarketInterpreter(local_llm=lambda p: bad)
    with pytest.raises(InterpretationError):
        it.interpret(_bundle(), mode="local")


def test_out_of_range_values_rejected():
    bad1 = json.dumps({"theme": "t", "sentiment": 1.5, "affected_symbols": [], "confidence": 0.5})
    it = LlmMarketInterpreter(local_llm=lambda p: bad1)
    with pytest.raises(InterpretationError):
        it.interpret(_bundle(), mode="local")
    bad2 = json.dumps({"theme": "t", "sentiment": 0.1, "affected_symbols": [], "confidence": 1.2})
    it = LlmMarketInterpreter(local_llm=lambda p: bad2)
    with pytest.raises(InterpretationError):
        it.interpret(_bundle(), mode="local")


# ── 4. 三路来源留痕 ──


def test_sources_used_tracks_non_empty_channels():
    it = LlmMarketInterpreter(local_llm=_local_ok)
    out = it.interpret(_bundle(research=("中金：上调评级",), social=("雪球热议",)), mode="local")
    assert out.sources_used == ("news", "research", "social")
    out2 = it.interpret(_bundle(), mode="local")
    assert out2.sources_used == ("news",)


# ── 5. 审计链 ──


def test_audit_sink_receives_record():
    records = []
    it = LlmMarketInterpreter(local_llm=_local_ok, audit_sink=records.append)
    out = it.interpret(_bundle(), mode="local")
    assert len(records) == 1
    rec = records[0]
    assert rec.mode == "local"
    assert rec.interpretation is out
    assert rec.raw_digest


def test_audit_sink_error_not_blocking():
    def bad_sink(_):
        raise RuntimeError("audit down")

    it = LlmMarketInterpreter(local_llm=_local_ok, audit_sink=bad_sink)
    out = it.interpret(_bundle(), mode="local")
    assert out.theme == "白酒板块情绪修复"
    assert it.sink_errors


# ── 6. 信号边界 ──


def test_output_has_no_order_semantics():
    it = LlmMarketInterpreter(local_llm=_local_ok)
    out = it.interpret(_bundle(), mode="local")
    for forbidden in ("order", "side", "quantity", "buy", "sell", "position"):
        assert not hasattr(out, forbidden)
