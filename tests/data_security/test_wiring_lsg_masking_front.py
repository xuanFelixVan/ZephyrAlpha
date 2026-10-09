# [BLUEPRINT] MOD-DATSEC-005 | docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md | wiring 抢救配套测试（车道 2a st-chiefc-20261009）
# [MODULE] tests.data_security.test_wiring_lsg_masking_front
# [DEPENDENCIES] zephyr.data_security.wiring；pytest
# [INVARIANTS] 审计 sink=内存 list；gateway 用进程内 fake（零网络零 LLM 调用）
# [TTL] permanent
"""LSGMaskingFront（MOD-DATSEC-005）最小可红行为测试：purpose 解析/L1 放行/输出直通/Fail-Closed。"""

from __future__ import annotations

import asyncio

import pytest

from zephyr.data_security.ai_masking_pipeline import AiMaskingError, MaskingLevel
from zephyr.data_security.wiring import LSGMaskingFront


class _FakeGateway:
    """进程内假 LSG 网关（记录调用，零外部依赖）。"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def scan_input(self, text: str, **_kw):
        self.calls.append(("in", text))
        return {"ok": True, "text": text}

    async def scan_output(self, text: str, **_kw):
        self.calls.append(("out", text))
        return {"ok": True, "text": text}


def _front(gateway: _FakeGateway | None = None) -> tuple[LSGMaskingFront, _FakeGateway]:
    gw = gateway or _FakeGateway()
    records: list = []
    return LSGMaskingFront(gw, audit_sink=records.append), gw


def test_empty_gateway_fails_closed() -> None:
    with pytest.raises(AiMaskingError):
        LSGMaskingFront(None)


def test_unknown_purpose_falls_back_to_default_l1() -> None:
    front, _ = _front()
    assert front.default_purpose == "default"
    assert front.level_of("never-registered") is MaskingLevel.L1


def test_resolve_purpose_precedence_and_fallback() -> None:
    front, _ = _front()
    assert front.resolve_purpose("explicit", {"masking_purpose": "meta"}) == "default"
    assert front.resolve_purpose(None, {"masking_purpose": "meta"}) == "default"
    assert front.resolve_purpose(None, None) == "default"


def test_scan_input_l1_passthrough_keeps_text() -> None:
    """出厂 L1：先脱敏后防御，L1 层文本原样进入 gateway。"""
    front, gw = _front()
    out = asyncio.run(front.scan_input("hello 世界", purpose="default"))
    assert out["text"] == "hello 世界"
    assert gw.calls == [("in", "hello 世界")]


def test_scan_output_delegates_verbatim() -> None:
    """输出侧直通委托（LSG L3 输出防御本职，包装层不改写）。"""
    front, gw = _front()
    out = asyncio.run(front.scan_output("model-said"))
    assert out["text"] == "model-said"
    assert gw.calls == [("out", "model-said")]


def test_audit_redaction_keeps_l2_before_out_of_sink() -> None:
    """L2+ before 红字化：sink 只见摘要（字符计数），不见原文。"""
    from zephyr.data_security.ai_masking_pipeline import MaskingPolicy

    gw = _FakeGateway()
    records: list = []
    table = {"default": MaskingPolicy(level=MaskingLevel.L2)}
    front = LSGMaskingFront(gw, policies=table, audit_sink=records.append)
    assert front.level_of("secret") is MaskingLevel.L2
    asyncio.run(front.scan_input("金额 1234567.89 标的 SH600000", purpose="default"))
    assert records, "L2 调用应产出一条审计记录"
    assert "1234567.89" not in str(records[0].before)
    assert "字符数" in str(records[0].before)
