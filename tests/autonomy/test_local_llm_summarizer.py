# [A_test] module_id: MOD-CONTEXT_ENGINE_local_llm_summarizer | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | 07号文 §4-P1
# [MODULE] tests.autonomy.test_local_llm_summarizer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""LocalLLMSummarizer 测试（07 号文 §4 P1-2 llm_summary 生产摘要器）。

覆盖：分 slot 摘要（单段/多段/递归合并）、integrity_check 串联校验
（不过则不替换原文）、infer 失败/网关缺省降级空串、DocCompressor 三档
兜底链不变（llm 空 -> rule_based）、ContextAssembler opt-in 接线与默认
行为零变化。网关/校验器一律 fake——不触网、不加载真模型。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zephyr.autonomy_core.context import local_llm_summarizer as lls
from zephyr.autonomy_core.context.local_llm_summarizer import (
    LocalLLMSummarizer,
    verify_summary_integrity,
)

_FRONTMATTER = "---\ntitle: 测试文档\n---\n"
_HEADERS = "# 第一章\n## 第一节\n"


def _long_body(chars_per_line: int = 80, lines: int = 30) -> str:
    """多段落长正文（每 3 行一空行分段，防 rule_based 长段落截断干扰断言；不以空白结尾）。"""
    rows: list[str] = []
    for i in range(lines):
        rows.append(f"第{i:02d}行 " + "正文内容" * (chars_per_line // 8))
        if i % 3 == 2 and i != lines - 1:
            rows.append("")
    return "\n".join(rows)


def _raw_with_structure() -> str:
    return _FRONTMATTER + _HEADERS + _long_body()


def _valid_summary_for(raw: str) -> str:
    """满足 integrity + DocCompressor 不变量的合法摘要：保留 frontmatter/标题且更短。"""
    parts: list[str] = []
    if raw.startswith("---\n"):
        parts.append(_FRONTMATTER)
    if "# 第一章" in raw:
        parts.append(_HEADERS)
    parts.append("摘要正文：" + "关键事实保留。" * 30)
    return "".join(parts)


@dataclass
class _FakeInferResult:
    text: str
    status: str = "ok"
    error: str | None = None


class _FakeGateway:
    """LLMRuntimeGateway 假实现——按预设行为返回 InferResult。"""

    def __init__(
        self,
        *,
        summary_fn: Any = None,
        status: str = "ok",
        raises: bool = False,
        fail_on_call: int | None = None,
    ) -> None:
        self._summary_fn = summary_fn
        self._status = status
        self._raises = raises
        self._fail_on_call = fail_on_call
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def infer(self, task_type: str, prompt: str, **kw: Any) -> _FakeInferResult:
        self.calls.append((task_type, prompt, kw))
        if self._raises or (self._fail_on_call is not None and len(self.calls) == self._fail_on_call):
            raise RuntimeError("local model down")
        if self._status != "ok":
            return _FakeInferResult(text="", status=self._status, error="blocked")
        if self._summary_fn is not None:
            return _FakeInferResult(text=self._summary_fn(prompt))
        return _FakeInferResult(text="摘要：" + "内容" * 30)


class _FakeIntegrityChecker:
    """IntegrityCheck 假实现——记录 verify 调用并按预设判决。"""

    def __init__(self, *, hashes_match: bool = True) -> None:
        self._hashes_match = hashes_match
        self.calls: list[tuple[str, str, str]] = []

    def verify(self, layer: str, before_hash: str, after_hash: str) -> Any:
        self.calls.append((layer, before_hash, after_hash))
        from zephyr.autonomy_core.context.integrity_check import IntegrityReport

        return IntegrityReport(
            layer=layer,
            content_hash=before_hash,
            inject_time="2026-08-29",
            hashes_match=self._hashes_match,
            order_preserved=True,
        )


class TestSlotSummarization:
    def test_single_slot_short_text(self) -> None:
        raw = _raw_with_structure()
        summary = _valid_summary_for(raw)
        gateway = _FakeGateway(summary_fn=lambda _prompt: summary)
        summarizer = LocalLLMSummarizer(gateway)

        result = summarizer.summarize(raw)

        assert result == summary
        assert len(gateway.calls) == 1
        task_type, prompt, kw = gateway.calls[0]
        assert task_type == "doc_summary_slot"
        assert "slot 1/1" in prompt
        assert kw.get("complexity") == "simple"

    def test_multi_slot_split_and_merge(self) -> None:
        raw = _long_body(chars_per_line=50, lines=20)  # 纯正文，无 frontmatter/标题
        gateway = _FakeGateway()
        summarizer = LocalLLMSummarizer(gateway, slot_chars=200)

        result = summarizer.summarize(raw)

        assert result != ""
        assert len(gateway.calls) >= 2, "超长文本应切多 slot 逐段摘要"
        first_prompt = gateway.calls[0][1]
        assert "slot 1/" in first_prompt

    def test_channel_pinned_when_configured(self) -> None:
        raw = _long_body(chars_per_line=50, lines=3)
        gateway = _FakeGateway()
        summarizer = LocalLLMSummarizer(gateway, channel="ollama")
        summarizer.summarize(raw)
        assert gateway.calls[0][2].get("channel") == "ollama"

    def test_merged_oversize_triggers_second_pass(self) -> None:
        import re

        raw = _long_body(chars_per_line=50, lines=20)
        # 每段摘要返回 60 字单段文本 -> 合并稿仍超 slot_chars -> 递归第二轮
        gateway = _FakeGateway(summary_fn=lambda _prompt: "段摘要" * 20)
        summarizer = LocalLLMSummarizer(gateway, slot_chars=200, max_passes=2)

        result = summarizer.summarize(raw)

        assert result != ""
        slot_totals = {
            int(m.group(1)) for _, prompt, _ in gateway.calls if (m := re.search(r"slot \d+/(\d+)", prompt)) is not None
        }
        assert len(slot_totals) >= 2, "合并稿超 slot_chars 应触发第二轮压缩（新一轮 slot 总数不同）"


class TestDegradation:
    def test_infer_non_ok_returns_empty(self) -> None:
        summarizer = LocalLLMSummarizer(_FakeGateway(status="blocked"))
        assert summarizer.summarize(_raw_with_structure()) == ""

    def test_infer_exception_returns_empty(self) -> None:
        summarizer = LocalLLMSummarizer(_FakeGateway(raises=True))
        assert summarizer.summarize(_raw_with_structure()) == ""

    def test_slot_failure_aborts_whole_summary(self) -> None:
        raw = _long_body(chars_per_line=50, lines=20)
        gateway = _FakeGateway(fail_on_call=2)
        summarizer = LocalLLMSummarizer(gateway, slot_chars=200)
        assert summarizer.summarize(raw) == ""

    def test_missing_gateway_degrades_to_empty(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(lls, "_build_default_gateway", lambda: None)
        summarizer = LocalLLMSummarizer()
        assert summarizer.summarize(_raw_with_structure()) == ""

    def test_blank_text_returns_empty_without_gateway(self) -> None:
        gateway = _FakeGateway()
        summarizer = LocalLLMSummarizer(gateway)
        assert summarizer.summarize("   ") == ""
        assert gateway.calls == []

    def test_callable_matches_summarize(self) -> None:
        raw = _raw_with_structure()
        summary = _valid_summary_for(raw)
        summarizer = LocalLLMSummarizer(_FakeGateway(summary_fn=lambda _prompt: summary))
        assert summarizer(raw) == summarizer.summarize(raw)


class TestIntegrityGate:
    def test_summary_longer_than_original_rejected(self) -> None:
        raw = _long_body(chars_per_line=50, lines=5)
        gateway = _FakeGateway(summary_fn=lambda _prompt: raw + "额外追加内容")
        assert LocalLLMSummarizer(gateway).summarize(raw) == ""

    def test_collapsed_summary_rejected(self) -> None:
        raw = _long_body(chars_per_line=80, lines=30)
        gateway = _FakeGateway(summary_fn=lambda _prompt: "太短")
        assert LocalLLMSummarizer(gateway).summarize(raw) == ""

    def test_missing_frontmatter_rejected(self) -> None:
        raw = _raw_with_structure()
        summary = _HEADERS + "摘要正文：" + "关键事实保留。" * 30  # 丢 frontmatter
        gateway = _FakeGateway(summary_fn=lambda _prompt: summary)
        assert LocalLLMSummarizer(gateway).summarize(raw) == ""

    def test_missing_header_rejected(self) -> None:
        raw = _raw_with_structure()
        summary = _FRONTMATTER + "摘要正文：" + "关键事实保留。" * 30  # 丢标题
        gateway = _FakeGateway(summary_fn=lambda _prompt: summary)
        assert LocalLLMSummarizer(gateway).summarize(raw) == ""

    def test_checker_wired_into_frontmatter_verification(self) -> None:
        raw = _raw_with_structure()
        summary = _valid_summary_for(raw)
        checker = _FakeIntegrityChecker(hashes_match=True)
        gateway = _FakeGateway(summary_fn=lambda _prompt: summary)
        summarizer = LocalLLMSummarizer(gateway, integrity_checker=checker)

        assert summarizer.summarize(raw) == summary
        assert len(checker.calls) == 1
        assert checker.calls[0][0] == "llm_summary"

    def test_checker_hash_mismatch_rejects_summary(self) -> None:
        raw = _raw_with_structure()
        checker = _FakeIntegrityChecker(hashes_match=False)
        gateway = _FakeGateway(summary_fn=lambda _prompt: _valid_summary_for(raw))
        summarizer = LocalLLMSummarizer(gateway, integrity_checker=checker)
        assert summarizer.summarize(raw) == ""

    def test_verify_summary_integrity_rules(self) -> None:
        raw = _raw_with_structure()
        good = _valid_summary_for(raw)
        assert verify_summary_integrity(raw, good) is True
        assert verify_summary_integrity(raw, "") is False
        assert verify_summary_integrity(raw, raw) is False
        assert verify_summary_integrity(raw, "塌缩") is False
        no_fm_raw = _long_body(chars_per_line=80, lines=10)
        no_fm_summary = "摘要：" + "内容" * 30
        assert verify_summary_integrity(no_fm_raw, no_fm_summary) is True


class TestDocCompressorChainUnchanged:
    """DocCompressor 三档兜底链纪律：llm 空/违反不变量 -> rule_based。"""

    def _compressor(self) -> Any:
        from zephyr.shared.io.doc_compressor import CompressionPolicy, DocCompressor

        return DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=2000))

    def test_llm_summary_tier_effective_with_summarizer(self) -> None:
        raw = _raw_with_structure()
        summary = _valid_summary_for(raw)
        gateway = _FakeGateway(summary_fn=lambda _prompt: summary)
        outcome = self._compressor().compress_with_provenance(raw, llm_summarizer=LocalLLMSummarizer(gateway))
        assert outcome.strategy_used == "llm_summary"
        assert outcome.compressed_text == summary
        assert outcome.raw_text == raw

    def test_empty_summary_falls_back_to_rule_based(self) -> None:
        raw = _raw_with_structure()
        gateway = _FakeGateway(status="error")
        outcome = self._compressor().compress_with_provenance(raw, llm_summarizer=LocalLLMSummarizer(gateway))
        assert outcome.strategy_used == "rule_based"
        assert outcome.compressed_text != ""

    def test_invariant_violating_summary_falls_back_to_rule_based(self) -> None:
        raw = _raw_with_structure()
        bad_summary = "无标题无frontmatter但长度足够的文本 " * 20  # 丢标题 -> 违反 preserve_structure
        outcome = self._compressor().compress_with_provenance(raw, llm_summarizer=lambda _text: bad_summary)
        assert outcome.strategy_used == "rule_based"

    def test_no_summarizer_keeps_rule_based_default(self) -> None:
        raw = _raw_with_structure()
        outcome = self._compressor().compress_with_provenance(raw)
        assert outcome.strategy_used == "rule_based"


class TestContextAssemblerOptIn:
    """context_assembler._compress_context 接线：opt-in 启用，默认零变化。"""

    def _make_ctx(self, raw: str) -> Any:
        from zephyr.autonomy_core.context.context_assembler import AssembledContext

        return AssembledContext(context_text=raw, file_count=1, total_chars=len(raw), token_estimate=len(raw) // 4)

    def test_default_behavior_unchanged(self) -> None:
        from zephyr.autonomy_core.context.context_assembler import ContextAssembler

        raw = _raw_with_structure()
        assembler = ContextAssembler()  # 未注入 summarizer
        assert assembler._llm_summarizer is None
        ctx = assembler._compress_context(self._make_ctx(raw), token_budget=100)

        assert ctx.was_compressed is True
        assert not any("COMPRESSION_FAILED" in e for e in ctx.errors)
        assert ctx.raw_context_text == raw
        assert ctx.context_text != _valid_summary_for(raw), "默认走 rule_based，不应出现 llm 摘要"

    def test_opt_in_summarizer_enables_llm_summary_tier(self) -> None:
        from zephyr.autonomy_core.context.context_assembler import ContextAssembler

        raw = _raw_with_structure()
        summary = _valid_summary_for(raw)
        assert len(summary) >= 200, "须满足默认 policy min_chars=200"
        summarizer = LocalLLMSummarizer(_FakeGateway(summary_fn=lambda _prompt: summary))
        assembler = ContextAssembler(llm_summarizer=summarizer)
        ctx = assembler._compress_context(self._make_ctx(raw), token_budget=100)

        assert ctx.was_compressed is True
        assert ctx.context_text == summary, "注入 summarizer 后 llm_summary 档应生效"
        assert ctx.raw_context_text == raw
        assert not any("COMPRESSION_FAILED" in e for e in ctx.errors)

    def test_opt_in_summarizer_failure_degrades_to_rule_based(self) -> None:
        from zephyr.autonomy_core.context.context_assembler import ContextAssembler

        raw = _raw_with_structure()
        summarizer = LocalLLMSummarizer(_FakeGateway(raises=True))
        assembler = ContextAssembler(llm_summarizer=summarizer)
        ctx = assembler._compress_context(self._make_ctx(raw), token_budget=100)

        assert ctx.was_compressed is True
        assert ctx.context_text != ""
        assert not any("COMPRESSION_FAILED" in e for e in ctx.errors)
