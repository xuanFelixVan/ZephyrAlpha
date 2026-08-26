# [BLUEPRINT] MOD-KNW-007 | docs/03_modules/_domain_knowledge/ai_knowledge_extractor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-007 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_ai_knowledge_extractor
# [TESTS] src/zephyr/knowledge/ai_knowledge_extractor.py
"""MOD-KNW-007 单元测试：ai_knowledge_extractor AI 自动知识提取器。

蓝图验收（B10-02191/CAND-KNW-007，A1 D-KNOWLEDGE-17）：
三类源（experiment_report|research_note|strategy_code 词表闭合）批处理管线 +
LLM 抽取注入（schema 校验坏输出 Fail-Closed 标记 FAILED）+ 低置信度转人工队列
+ checkpoint 断点续跑（COMPLETED 幂等跳过/FAILED 重试）+ 写 KB 注入回调。
LLM/kb_writer/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.ai_knowledge_extractor",
    reason="ai_knowledge_extractor not importable",
)

from zephyr.knowledge.ai_knowledge_extractor import (  # noqa: E402
    AiExtractorError,
    AiKnowledgeExtractor,
    SourceStatus,
    SourceType,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _good_output(source) -> dict:
    return {
        "items": [
            {"title": "动量因子在震荡市失效", "content": "IC 转负", "confidence": 0.9, "tags": ["因子"]},
            {"title": "低置信猜想", "content": "待验证", "confidence": 0.4},
        ]
    }


def _ext(
    written: list | None = None,
    llm=None,
    threshold: float = 0.7,
    checkpoint=None,
) -> AiKnowledgeExtractor:
    return AiKnowledgeExtractor(
        llm_extractor=llm if llm is not None else _good_output,
        kb_writer=(lambda item: written.append(item)) if written is not None else None,
        clock=lambda: _T0,
        confidence_threshold=threshold,
        checkpoint=checkpoint,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 源注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterSource:
    def test_register_ok(self) -> None:
        ext = _ext([])
        src = ext.register_source(SourceType.EXPERIMENT_REPORT, "exp-001", "实验报告正文")
        assert src.registered_at == _T0
        assert ext.source_status("exp-001") is SourceStatus.PENDING

    def test_register_all_three_types(self) -> None:
        ext = _ext([])
        ext.register_source(SourceType.EXPERIMENT_REPORT, "a", "x")
        ext.register_source(SourceType.RESEARCH_NOTE, "b", "x")
        ext.register_source(SourceType.STRATEGY_CODE, "c", "x")
        assert all(ext.source_status(s) is SourceStatus.PENDING for s in ("a", "b", "c"))

    def test_register_invalid_raises(self) -> None:
        ext = _ext([])
        with pytest.raises(AiExtractorError):
            ext.register_source(SourceType.RESEARCH_NOTE, "", "x")  # 空 id
        with pytest.raises(AiExtractorError):
            ext.register_source("web_page", "a", "x")  # 词表外
        with pytest.raises(AiExtractorError):
            ext.register_source(SourceType.RESEARCH_NOTE, "a", "")  # 空内容

    def test_register_duplicate_raises(self) -> None:
        ext = _ext([])
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.register_source(SourceType.RESEARCH_NOTE, "a", "y")

    def test_threshold_out_of_range_raises(self) -> None:
        with pytest.raises(AiExtractorError):
            _ext([], threshold=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# 批处理管线（LLM 抽取 + 写 KB + 人工队列）
# ──────────────────────────────────────────────────────────────────────────────


class TestRunBatch:
    def test_batch_high_confidence_written_low_to_review(self) -> None:
        written: list = []
        ext = _ext(written)
        ext.register_source(SourceType.EXPERIMENT_REPORT, "exp-001", "正文")
        report = ext.run_batch()
        assert report.processed == 1 and report.completed == 1
        assert report.written_count == 1 and report.review_count == 1
        assert ext.source_status("exp-001") is SourceStatus.COMPLETED
        assert written[0].title == "动量因子在震荡市失效"
        assert written[0].item_key == "exp-001#K0001"
        pending = ext.pending_review()
        assert len(pending) == 1 and pending[0].confidence == 0.4

    def test_batch_deterministic_registration_order(self) -> None:
        order: list[str] = []

        def _llm(source):
            order.append(source.source_id)
            return {"items": []}

        ext = _ext([], llm=_llm)
        ext.register_source(SourceType.RESEARCH_NOTE, "z-src", "x")
        ext.register_source(SourceType.RESEARCH_NOTE, "a-src", "x")
        ext.run_batch()
        assert order == ["z-src", "a-src"]  # 注册序而非字典序

    def test_batch_selected_sources(self) -> None:
        written: list = []
        ext = _ext(written)
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        ext.register_source(SourceType.RESEARCH_NOTE, "b", "x")
        report = ext.run_batch(("b",))
        assert report.processed == 1
        assert ext.source_status("a") is SourceStatus.PENDING
        assert ext.source_status("b") is SourceStatus.COMPLETED

    def test_batch_unknown_source_raises(self) -> None:
        ext = _ext([])
        with pytest.raises(AiExtractorError):
            ext.run_batch(("ghost",))

    def test_llm_missing_fail_closed(self) -> None:
        ext = AiKnowledgeExtractor(llm_extractor=None, kb_writer=lambda i: None, clock=lambda: _T0)
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.run_batch()

    def test_llm_bad_schema_fail_closed(self) -> None:
        ext = _ext([], llm=lambda s: {"unexpected": True})
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.run_batch()
        assert ext.source_status("a") is SourceStatus.FAILED  # 坏输出不入库

    @pytest.mark.parametrize("bad_item", [
        {"content": "c", "confidence": 0.9},                    # 缺 title
        {"title": "", "content": "c", "confidence": 0.9},       # 空 title
        {"title": "t", "confidence": 0.9},                      # 缺 content
        {"title": "t", "content": "c"},                         # 缺 confidence
        {"title": "t", "content": "c", "confidence": "高"},      # 非数值
        {"title": "t", "content": "c", "confidence": 1.2},      # 越界
        {"title": "t", "content": "c", "confidence": True},     # bool 拒绝
        {"title": "t", "content": "c", "confidence": 0.9, "tags": "非法"},  # tags 非列表
    ])
    def test_llm_bad_item_schema_fail_closed(self, bad_item) -> None:
        ext = _ext([], llm=lambda s: {"items": [bad_item]})
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.run_batch()
        assert ext.source_status("a") is SourceStatus.FAILED

    def test_llm_exception_fail_closed(self) -> None:
        def _boom(source):
            raise RuntimeError("LLM 超时")

        ext = _ext([], llm=_boom)
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.run_batch()
        assert ext.source_status("a") is SourceStatus.FAILED

    def test_kb_writer_missing_fail_closed(self) -> None:
        ext = _ext(written=None)  # 未注入 kb_writer
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.run_batch()  # 高置信项需写 KB → Fail-Closed
        assert ext.source_status("a") is SourceStatus.FAILED

    def test_threshold_boundary(self) -> None:
        written: list = []
        ext = _ext(written, llm=lambda s: {"items": [
            {"title": "恰达阈值", "content": "c", "confidence": 0.7},
        ]})
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        ext.run_batch()
        assert len(written) == 1  # 0.7 不低于阈值 → 直写
        assert ext.pending_review() == ()


# ──────────────────────────────────────────────────────────────────────────────
# 人工确认队列
# ──────────────────────────────────────────────────────────────────────────────


class TestReviewQueue:
    def _with_pending(self) -> tuple[AiKnowledgeExtractor, list]:
        written: list = []
        ext = _ext(written)
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        ext.run_batch()
        return ext, written

    def test_resolve_approve_writes_kb(self) -> None:
        ext, written = self._with_pending()
        key = ext.pending_review()[0].item_key
        ext.resolve_review(key, approve=True)
        assert len(written) == 2  # 原直写 1 + 复核通过 1
        assert ext.pending_review() == ()

    def test_resolve_reject_discards(self) -> None:
        ext, written = self._with_pending()
        key = ext.pending_review()[0].item_key
        ext.resolve_review(key, approve=False)
        assert len(written) == 1  # 驳回不写 KB
        assert ext.pending_review() == ()

    def test_resolve_unknown_raises(self) -> None:
        ext, _ = self._with_pending()
        with pytest.raises(AiExtractorError):
            ext.resolve_review("ghost#K9999", approve=True)

    def test_pending_review_sorted(self) -> None:
        ext = _ext([], llm=lambda s: {"items": [
            {"title": f"项{i}", "content": "c", "confidence": 0.1} for i in range(3)
        ]})
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        ext.run_batch()
        keys = [item.item_key for item in ext.pending_review()]
        assert keys == sorted(keys)


# ──────────────────────────────────────────────────────────────────────────────
# 断点续跑（checkpoint）
# ──────────────────────────────────────────────────────────────────────────────


class TestCheckpoint:
    def test_resume_skips_completed(self) -> None:
        written: list = []
        ext = _ext(written)
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        ext.register_source(SourceType.RESEARCH_NOTE, "b", "x")
        ext.run_batch(("a",))
        report = ext.run_batch()  # 续跑：a 幂等跳过
        assert report.processed == 1  # 仅 b
        assert ext.source_status("a") is SourceStatus.COMPLETED
        assert ext.source_status("b") is SourceStatus.COMPLETED

    def test_failed_retried_on_resume(self) -> None:
        calls = {"n": 0}

        def _flaky(source):
            calls["n"] += 1
            if calls["n"] == 1:
                return {"bad": True}
            return {"items": [{"title": "恢复", "content": "c", "confidence": 0.95}]}

        written: list = []
        ext = _ext(written, llm=_flaky)
        ext.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        with pytest.raises(AiExtractorError):
            ext.run_batch()
        assert ext.source_status("a") is SourceStatus.FAILED
        report = ext.run_batch()  # FAILED 重试成功
        assert report.completed == 1
        assert written[0].title == "恢复"

    def test_export_import_checkpoint_new_instance(self) -> None:
        written1: list = []
        ext1 = _ext(written1)
        ext1.register_source(SourceType.RESEARCH_NOTE, "a", "x")
        ext1.run_batch()
        ckpt = ext1.export_checkpoint()
        assert dict(ckpt.statuses)["a"] == "completed"
        assert ckpt.item_seq == 2

        written2: list = []
        llm_calls: list[str] = []

        def _llm2(source):
            llm_calls.append(source.source_id)
            return {"items": [{"title": "新", "content": "c", "confidence": 0.95}]}

        ext2 = _ext(written2, llm=_llm2, checkpoint=ckpt)
        ext2.register_source(SourceType.RESEARCH_NOTE, "a", "x")  # 恢复后沿用 COMPLETED
        ext2.register_source(SourceType.RESEARCH_NOTE, "b", "x")
        report = ext2.run_batch()
        assert llm_calls == ["b"]  # a 不重跑
        assert report.processed == 1
        assert written2[0].item_key == "b#K0003"  # item_seq 延续

    def test_checkpoint_bad_vocab_raises(self) -> None:
        from zephyr.knowledge.ai_knowledge_extractor import CheckpointState

        bad = CheckpointState(statuses=(("a", "paused"),), item_seq=0)
        with pytest.raises(AiExtractorError):
            _ext([], checkpoint=bad)

    def test_determinism_same_input_same_output(self) -> None:
        def _build() -> tuple:
            written: list = []
            ext = _ext(written)
            ext.register_source(SourceType.EXPERIMENT_REPORT, "s1", "x")
            ext.register_source(SourceType.STRATEGY_CODE, "s2", "x")
            report = ext.run_batch()
            return (
                (report.processed, report.completed, report.written_count, report.review_count),
                tuple(i.item_key for i in written),
                tuple(i.item_key for i in ext.pending_review()),
                ext.export_checkpoint().statuses,
            )

        assert _build() == _build()
