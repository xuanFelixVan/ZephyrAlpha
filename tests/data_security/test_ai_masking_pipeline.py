# [BLUEPRINT] MOD-DATSEC-001 | docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATSEC-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_security.test_ai_masking_pipeline
# [TESTS] src/zephyr/data_security/ai_masking_pipeline.py
"""MOD-DATSEC-001 单元测试：ai_masking_pipeline AI 分级脱敏管道。

蓝图验收（B13-04183/CAND-DATSEC-001，A3数据架构）：
L1-L4 分级脱敏（L4 仅统计摘要 / L3 金额标的泛化 / L2 禁发原值序列 / L1 放行）
+ 策略表驱动（未注册 Fail-Closed）+ 每次调用脱敏前后对比入审计回调。
审计回调全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_security.ai_masking_pipeline",
    reason="ai_masking_pipeline not importable",
)

from zephyr.data_security.ai_masking_pipeline import (  # noqa: E402
    AiMaskingError,
    AiMaskingPipeline,
    MaskingAuditRecord,
    MaskingLevel,
    MaskingPolicy,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_POLICIES = {
    "digest": MaskingPolicy(level=MaskingLevel.L1),
    "factor_doc": MaskingPolicy(level=MaskingLevel.L2),
    "strategy_note": MaskingPolicy(level=MaskingLevel.L3),
    "raw_export": MaskingPolicy(level=MaskingLevel.L4),
}


def _pipe(audits: list | None = None, policies: dict | None = None) -> AiMaskingPipeline:
    return AiMaskingPipeline(
        policies=policies if policies is not None else _POLICIES,
        clock=lambda: _T0,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造（策略表校验，Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_policies_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(policies={}, clock=lambda: _T0)

    def test_empty_purpose_key_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(policies={"": MaskingPolicy(level=MaskingLevel.L1)}, clock=lambda: _T0)

    def test_invalid_policy_type_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(policies={"x": "L1"}, clock=lambda: _T0)  # type: ignore[dict-item]

    def test_invalid_level_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(
                policies={"x": MaskingPolicy(level="L9")},  # type: ignore[arg-type]
                clock=lambda: _T0,
            )

    def test_large_below_medium_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(
                policies={"x": MaskingPolicy(level=MaskingLevel.L3, large_amount=10.0, medium_amount=100.0)},
                clock=lambda: _T0,
            )

    def test_negative_medium_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(
                policies={"x": MaskingPolicy(level=MaskingLevel.L3, medium_amount=-1.0)},
                clock=lambda: _T0,
            )

    def test_invalid_sequence_min_len_raises(self) -> None:
        with pytest.raises(AiMaskingError):
            AiMaskingPipeline(
                policies={"x": MaskingPolicy(level=MaskingLevel.L2, sequence_min_len=1)},
                clock=lambda: _T0,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 分级脱敏（L1/L2/L3/L4）
# ──────────────────────────────────────────────────────────────────────────────


class TestMaskLevels:
    def test_l1_passthrough(self) -> None:
        pipe = _pipe()
        text = "600519.SH 成交 2500000 元"
        assert pipe.mask_for_llm("digest", text) == text

    def test_l2_sequence_masked_with_stats(self) -> None:
        pipe = _pipe()
        text = "动量因子原值序列 1.0, 2.0, 3.0 已入库"
        out = pipe.mask_for_llm("factor_doc", text)
        assert "[原值序列已脱敏" in out
        assert "均值=2.0000" in out
        assert "1.0, 2.0, 3.0" not in out
        assert "动量因子原值序列" in out  # 因子定义保留

    def test_l2_short_sequence_kept(self) -> None:
        pipe = _pipe()
        text = "区间 1.5, 2.5 说明"  # 仅 2 个数值，未达序列最小长度
        assert pipe.mask_for_llm("factor_doc", text) == text

    def test_l2_no_sequence_text_kept(self) -> None:
        pipe = _pipe()
        text = "因子定义：过去20日收益率均值"
        assert pipe.mask_for_llm("factor_doc", text) == text

    def test_l3_ticker_generalized_by_first_appearance(self) -> None:
        pipe = _pipe()
        text = "买入600519.SH，关注000001.SZ"
        out = pipe.mask_for_llm("strategy_note", text)
        assert "标的A" in out and "标的B" in out
        assert "600519.SH" not in out and "000001.SZ" not in out
        assert out.index("标的A") < out.index("标的B")  # 首现序

    def test_l3_amount_buckets(self) -> None:
        pipe = _pipe()
        text = "成交2500000元，另投500000元与500元"
        out = pipe.mask_for_llm("strategy_note", text)
        assert "大额" in out and "中额" in out and "小额" in out
        assert "2500000" not in out and "500000" not in out

    def test_l3_ticker_repeat_same_mapping(self) -> None:
        pipe = _pipe()
        text = "600519.SH 加仓，600519.SH 持有"
        out = pipe.mask_for_llm("strategy_note", text)
        assert out.count("标的A") == 2

    def test_l4_summary_only(self) -> None:
        pipe = _pipe()
        text = "买入600519.SH 成交2500000元"
        out = pipe.mask_for_llm("raw_export", text)
        assert out.startswith("[L4统计摘要]")
        assert "600519" not in out and "2500000" not in out and "买入" not in out
        assert f"字符数={len(text)}" in out
        assert "标的出现数=1" in out


# ──────────────────────────────────────────────────────────────────────────────
# 审计回调（每次调用前后对比）
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_audit_records_before_after(self) -> None:
        audits: list[MaskingAuditRecord] = []
        pipe = _pipe(audits)
        text = "600519.SH 成交2500000元"
        out = pipe.mask_for_llm("strategy_note", text)
        assert len(audits) == 1
        rec = audits[0]
        assert rec.purpose == "strategy_note"
        assert rec.level is MaskingLevel.L3
        assert rec.before == text
        assert rec.after == out
        assert rec.masked_at == _T0
        assert rec.note

    def test_audit_every_call(self) -> None:
        audits: list[MaskingAuditRecord] = []
        pipe = _pipe(audits)
        pipe.mask_for_llm("digest", "甲")
        pipe.mask_for_llm("digest", "乙")
        assert len(audits) == 2

    def test_audit_sink_failure_not_blocking(self) -> None:
        def _bad_sink(_r: MaskingAuditRecord) -> None:
            raise RuntimeError("audit down")

        pipe = AiMaskingPipeline(policies=_POLICIES, clock=lambda: _T0, audit_sink=_bad_sink)
        assert pipe.mask_for_llm("digest", "文本") == "文本"


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_unknown_purpose_raises(self) -> None:
        pipe = _pipe()
        with pytest.raises(AiMaskingError):
            pipe.mask_for_llm("ghost", "文本")

    def test_empty_text_raises(self) -> None:
        pipe = _pipe()
        with pytest.raises(AiMaskingError):
            pipe.mask_for_llm("digest", "")

    def test_level_of(self) -> None:
        pipe = _pipe()
        assert pipe.level_of("raw_export") is MaskingLevel.L4
        with pytest.raises(AiMaskingError):
            pipe.level_of("ghost")

    def test_determinism(self) -> None:
        text = "买入600519.SH 与000001.SZ 成交2500000元"
        assert _pipe().mask_for_llm("strategy_note", text) == _pipe().mask_for_llm("strategy_note", text)
