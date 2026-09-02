# [A_test] module_id: MOD-INF-002_compressor_tiered | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] tests.context.test_doc_compressor_tiered
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""DocCompressor 三档降级测试（07 号文 §4 Phase 1 P1-2）。

llm_summary（LLM 调用注入位 mock）→ rule_based → truncate 降级链；
摘要违反不变量时绝不替换原文；truncate 保底档必成功。
"""

from __future__ import annotations

import pytest

from zephyr.shared.io.doc_compressor import (
    DEFAULT_POLICY,
    CompressionOutcome,
    CompressionPolicy,
    CompressionStrategy,
    DocCompressor,
)

_FRONTMATTER = "---\nttl: permanent\n---\n"
_HEADER = "# 设计文档\n"
# 3 行一段、空行分隔——规则压缩不截断短段落，压缩结果稳定 ≥ min_chars
_LONG_BODY = "\n\n".join(
    "\n".join(
        f"第{i}段第{j}行：本地 Qwen INT4 摘要模型的分 slot 压缩策略细节说明，含显存约束与延迟预算。" for j in range(3)
    )
    for i in range(8)
)
_DOC = _FRONTMATTER + _HEADER + _LONG_BODY


def _make_compressor() -> DocCompressor:
    return DocCompressor(policy=DEFAULT_POLICY)


class TestLlmSummaryTier:
    def test_llm_summary_success_uses_llm_tier(self) -> None:
        summary = _FRONTMATTER + _HEADER + ("摘要：" + "要点。" * 120)  # ≥ min_chars，保留标题与 frontmatter
        compressor = _make_compressor()
        outcome = compressor.compress_with_provenance(_DOC, llm_summarizer=lambda text: summary)
        assert outcome.strategy_used == CompressionStrategy.LLM_SUMMARY.value
        assert outcome.compressed_text == summary
        assert outcome.raw_text == _DOC

    def test_llm_exception_degrades_to_rule_based(self) -> None:
        def _boom(text: str) -> str:
            raise RuntimeError("local qwen unavailable")

        outcome = _make_compressor().compress_with_provenance(_DOC, llm_summarizer=_boom)
        assert outcome.strategy_used == CompressionStrategy.RULE_BASED.value
        assert "已截断" not in outcome.compressed_text or len(outcome.compressed_text) <= DEFAULT_POLICY.max_chars

    def test_llm_empty_result_degrades_to_rule_based(self) -> None:
        outcome = _make_compressor().compress_with_provenance(_DOC, llm_summarizer=lambda text: "   ")
        assert outcome.strategy_used == CompressionStrategy.RULE_BASED.value

    def test_llm_invariant_violation_never_replaces_original(self) -> None:
        """摘要丢弃标题/frontmatter → 不变量校验失败 → 降级 rule_based，原文不被替换。"""
        bad_summary = "没有任何标题也没有frontmatter的坏摘要。" * 20
        outcome = _make_compressor().compress_with_provenance(_DOC, llm_summarizer=lambda text: bad_summary)
        assert outcome.strategy_used == CompressionStrategy.RULE_BASED.value
        assert _HEADER.strip() in outcome.compressed_text
        assert outcome.compressed_text.startswith("---\n")

    def test_no_summarizer_skips_llm_tier(self) -> None:
        outcome = _make_compressor().compress_with_provenance(_DOC)
        assert outcome.strategy_used == CompressionStrategy.RULE_BASED.value


class TestRuleBasedTier:
    def test_rule_based_strategy_direct(self) -> None:
        called = False

        def _spy(text: str) -> str:
            nonlocal called
            called = True
            return "x"

        outcome = _make_compressor().compress_with_provenance(
            _DOC, strategy=CompressionStrategy.RULE_BASED, llm_summarizer=_spy
        )
        assert outcome.strategy_used == CompressionStrategy.RULE_BASED.value
        assert called is False, "rule_based 首选档不得触达 llm_summarizer"

    def test_rule_based_invariant_violation_raises_fail_closed(self) -> None:
        """rule_based 档不变量违反保持 fail-closed（存量契约），不被降级掩盖。"""
        from zephyr.shared.io.doc_compressor import CompressionInvariantError

        compressor = _make_compressor()
        paragraph = "".join(f"行{i}：" + "正文内容片段。" * 3 + "\n" for i in range(12))
        assert len(paragraph) >= DEFAULT_POLICY.min_chars
        with pytest.raises(CompressionInvariantError):
            compressor.compress_with_provenance(paragraph, strategy=CompressionStrategy.RULE_BASED)

    def test_rule_based_crash_degrades_to_truncate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """rule_based 档执行异常（非不变量违反）→ 降 truncate 保底。"""
        compressor = _make_compressor()

        def _crash(text: str, policy: CompressionPolicy) -> str:
            raise RuntimeError("rule engine broken")

        monkeypatch.setattr(compressor, "_rule_based_compress", _crash)
        outcome = compressor.compress_with_provenance(_DOC, strategy=CompressionStrategy.RULE_BASED)
        assert outcome.strategy_used == CompressionStrategy.TRUNCATE.value
        assert outcome.compressed_text != ""


class TestTruncateTier:
    def test_truncate_enforces_max_chars(self) -> None:
        long_doc = _FRONTMATTER + "正文" * 5000
        outcome = _make_compressor().compress_with_provenance(long_doc, strategy=CompressionStrategy.TRUNCATE)
        assert outcome.strategy_used == CompressionStrategy.TRUNCATE.value
        assert len(outcome.compressed_text) <= DEFAULT_POLICY.max_chars
        assert "已截断" in outcome.compressed_text

    def test_truncate_preserves_frontmatter(self) -> None:
        long_doc = _FRONTMATTER + "正文" * 5000
        outcome = _make_compressor().compress_with_provenance(long_doc, strategy=CompressionStrategy.TRUNCATE)
        assert outcome.compressed_text.startswith("---\n")

    def test_truncate_empty_text(self) -> None:
        outcome = _make_compressor().compress_with_provenance("", strategy=CompressionStrategy.TRUNCATE)
        assert outcome.compressed_text == ""


class TestBackwardCompat:
    def test_default_call_matches_legacy_rule_based_output(self) -> None:
        """旧式调用（无新参数）输出与既有规则式一致——演进不破坏存量行为。"""
        compressor = _make_compressor()
        legacy = compressor._rule_based_compress(_DOC, compressor.policy)
        outcome = compressor.compress_with_provenance(_DOC)
        assert outcome.compressed_text == legacy
        assert outcome.strategy_used == "rule_based"

    def test_compress_str_entry(self) -> None:
        result = _make_compressor().compress(_DOC)
        assert isinstance(result, str)
        assert result != ""

    def test_outcome_default_strategy_field(self) -> None:
        outcome = CompressionOutcome(raw_text="a", compressed_text="b")
        assert outcome.strategy_used == "rule_based"

    def test_custom_policy_respected(self) -> None:
        policy = CompressionPolicy(min_chars=100, max_chars=500)
        compressor = DocCompressor(policy=policy)
        outcome = compressor.compress_with_provenance(
            _FRONTMATTER + "正文" * 1000, strategy=CompressionStrategy.TRUNCATE
        )
        assert len(outcome.compressed_text) <= 500
