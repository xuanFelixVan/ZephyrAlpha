# [BLUEPRINT] MOD-FACTORY-001 | docs/03_modules/_domain_autonomy_core/knowledge_classifier/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FACTORY-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.autonomy.test_knowledge_classifier
# [TESTS] src/zephyr/autonomy_core/module_factory/knowledge_classifier.py
"""MOD-FACTORY-001 单元测试：knowledge_classifier 知识分类器（13号文 §3.2）。

覆盖验收点：受控词表外输出被拒 / 信息价值四维评分 REJECT 门禁 / schema 校验失败
fail-closed / tags 归并纪律（同义词归并 + 新词待登记）/ 交叉字段矛盾拒绝。
LLM 全 fake（实现 LLMInferProtocol 的假网关），禁网络禁真 LLM。
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip(
    "zephyr.autonomy_core.module_factory.knowledge_classifier",
    reason="knowledge_classifier not importable",
)

from zephyr.autonomy_core.module_factory.knowledge_classifier import (  # noqa: E402
    CLASSIFIER_TASK_TYPE,
    KnowledgeClassifier,
    KnowledgeClassifierError,
    KnowledgeItem,
    QualityGateConfig,
)

# ──────────────────────────────────────────────────────────────────────────────
# Fake LLM 网关（对齐 llm_runtime_gateway infer 签名；duck-type status/text）
# ──────────────────────────────────────────────────────────────────────────────


class _FakeResponse:
    def __init__(self, status: str = "ok", text: str = "") -> None:
        self.status = status
        self.text = text


class _FakeGateway:
    """实现 LLMInferProtocol 的假网关：返回预置载荷，记录全部调用。"""

    def __init__(self, payload=None, status: str = "ok") -> None:
        self._payload = payload
        self._status = status
        self.calls: list[tuple[str, str, dict]] = []

    def infer(self, task_type, prompt, **kw):
        self.calls.append((task_type, prompt, kw))
        if isinstance(self._payload, Exception):
            raise self._payload
        text = (
            self._payload
            if isinstance(self._payload, str)
            else json.dumps(self._payload, ensure_ascii=False)
        )
        return _FakeResponse(self._status, text)


def _item(**over) -> KnowledgeItem:
    base = {
        "knowledge_id": "KE-TEST-001",
        "title": "20日动量因子",
        "content": "过去 20 日收益率排序选股，强者恒强。适用于趋势市。",
        "source_ref": "unit-test",
    }
    base.update(over)
    return KnowledgeItem(**base)


def _factor_payload(**over) -> dict:
    base = {
        "quality": {"relevance": 0.9, "timeliness": 0.8, "information": 0.8, "reliability": 0.9},
        "target_kind": "factor",
        "factor_class": "momentum",
        "strategy_class": None,
        "other_subtype": None,
        "primary_timeframe": "daily",
        "applicable_timeframes": ["daily", "weekly"],
        "regime_valid": ["trend_up"],
        "regime_invalid": ["panic"],
        "direction": "long",
        "entry_role": "ranking",
        "applies_to": ["stock"],
        "tags": ["动量", "趋势"],
        "confidence": 0.9,
        "rationale": "典型动量因子",
    }
    base.update(over)
    return base


# ──────────────────────────────────────────────────────────────────────────────
# 构造期配置校验（fail-fast）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_zero_weight_raises(self) -> None:
        gate = QualityGateConfig(weight_relevance=0.0)
        with pytest.raises(KnowledgeClassifierError):
            KnowledgeClassifier(llm=_FakeGateway(), quality_gate=gate)

    def test_threshold_out_of_range_raises(self) -> None:
        with pytest.raises(KnowledgeClassifierError):
            KnowledgeClassifier(llm=_FakeGateway(), quality_gate=QualityGateConfig(threshold=1.0))

    def test_empty_tag_vocab_raises(self) -> None:
        with pytest.raises(KnowledgeClassifierError):
            KnowledgeClassifier(llm=_FakeGateway(), known_tags=frozenset())


# ──────────────────────────────────────────────────────────────────────────────
# 正常分类路径
# ──────────────────────────────────────────────────────────────────────────────


class TestClassifyHappyPath:
    def test_factor_classified(self) -> None:
        gw = _FakeGateway(_factor_payload())
        result = KnowledgeClassifier(llm=gw).classify(_item())
        assert result.verdict == "classified"
        assert result.classification is not None
        assert result.classification.target_kind == "factor"
        assert result.classification.factor_class == "momentum"
        assert result.classification.primary_timeframe == "daily"
        assert result.classification.direction == "long"
        assert result.quality_score == pytest.approx(0.85)
        assert result.human_gate_required is True

    def test_strategy_classified(self) -> None:
        payload = _factor_payload(
            target_kind="strategy",
            factor_class=None,
            strategy_class="momentum_trend",
            entry_role="trigger",
        )
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.verdict == "classified"
        assert result.classification.strategy_class == "momentum_trend"
        assert result.classification.factor_class is None

    def test_other_subtype_classified(self) -> None:
        payload = _factor_payload(
            target_kind="other",
            factor_class=None,
            other_subtype="risk_rule",
        )
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.verdict == "classified"
        assert result.classification.other_subtype == "risk_rule"

    def test_prompt_carries_controlled_vocab(self) -> None:
        gw = _FakeGateway(_factor_payload())
        KnowledgeClassifier(llm=gw).classify(_item())
        task_type, prompt, kw = gw.calls[0]
        assert task_type == CLASSIFIER_TASK_TYPE
        assert "value/quality/momentum/volatility/size/liquidity/event/intraday/technical/sentiment" in prompt
        assert "daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation" in prompt
        assert "动量" in prompt  # 既有标签词表注入 prompt
        assert kw.get("system")

    def test_markdown_fence_json_extracted(self) -> None:
        fenced = "```json\n" + json.dumps(_factor_payload(), ensure_ascii=False) + "\n```"
        result = KnowledgeClassifier(llm=_FakeGateway(fenced)).classify(_item())
        assert result.verdict == "classified"


# ──────────────────────────────────────────────────────────────────────────────
# 信息价值四维评分门禁（13号文 §3.1）
# ──────────────────────────────────────────────────────────────────────────────


class TestQualityGate:
    def test_low_value_rejected(self) -> None:
        payload = _factor_payload(
            quality={"relevance": 0.1, "timeliness": 0.2, "information": 0.1, "reliability": 0.2}
        )
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.verdict == "rejected"
        assert result.classification is None  # REJECT 不进分类
        assert "quality_gate" in result.error

    def test_threshold_boundary_passes(self) -> None:
        # 综合分恰好等于阈值（0.3）不拦截（< threshold 才 REJECT）
        payload = _factor_payload(
            quality={"relevance": 0.3, "timeliness": 0.3, "information": 0.3, "reliability": 0.3}
        )
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.verdict == "classified"

    def test_custom_threshold(self) -> None:
        gate = QualityGateConfig(threshold=0.9)
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload()), quality_gate=gate
        ).classify(_item())
        assert result.verdict == "rejected"  # 0.85 < 0.9


# ──────────────────────────────────────────────────────────────────────────────
# fail-closed：词表外 / schema 非法 / 解析失败 / 网关非 ok
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_out_of_vocab_factor_class_rejected(self) -> None:
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload(factor_class="magic"))
        ).classify(_item())
        assert result.verdict == "error"
        assert result.classification is None
        assert "schema_validation_failed" in result.error

    def test_out_of_vocab_enum_rejected(self) -> None:
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload(direction="sideways"))
        ).classify(_item())
        assert result.verdict == "error"
        assert result.classification is None

    def test_cross_field_conflict_rejected(self) -> None:
        # factor 却带 strategy_class -> 交叉字段矛盾
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload(strategy_class="daban"))
        ).classify(_item())
        assert result.verdict == "error"

    def test_factor_missing_class_rejected(self) -> None:
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload(factor_class=None))
        ).classify(_item())
        assert result.verdict == "error"

    def test_regime_overlap_rejected(self) -> None:
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload(regime_invalid=["trend_up"]))
        ).classify(_item())
        assert result.verdict == "error"

    def test_extra_key_rejected(self) -> None:
        result = KnowledgeClassifier(
            llm=_FakeGateway(_factor_payload(hallucinated_field="x"))
        ).classify(_item())
        assert result.verdict == "error"

    def test_garbage_text_fail_closed(self) -> None:
        result = KnowledgeClassifier(llm=_FakeGateway("这不是JSON输出")).classify(_item())
        assert result.verdict == "error"
        assert result.classification is None
        assert result.raw_text == "这不是JSON输出"

    def test_empty_text_fail_closed(self) -> None:
        result = KnowledgeClassifier(llm=_FakeGateway("")).classify(_item())
        assert result.verdict == "error"

    def test_gateway_blocked_status(self) -> None:
        gw = _FakeGateway(_factor_payload(), status="blocked")
        result = KnowledgeClassifier(llm=gw).classify(_item())
        assert result.verdict == "error"
        assert "blocked" in result.error

    def test_gateway_exception_fail_closed(self) -> None:
        gw = _FakeGateway(RuntimeError("network down"))
        result = KnowledgeClassifier(llm=gw).classify(_item())
        assert result.verdict == "error"
        assert "llm_call_failed" in result.error


# ──────────────────────────────────────────────────────────────────────────────
# 标签归并纪律（13号文 §3.2：先归并既有词表，新词标记待登记，不静默造词）
# ──────────────────────────────────────────────────────────────────────────────


class TestTagDiscipline:
    def test_synonym_merged(self) -> None:
        payload = _factor_payload(tags=["翻转", "破位", "横盘", "动量"])
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.verdict == "classified"
        assert set(result.classification.tags) == {"反转", "突破", "震荡", "动量"}
        assert result.tags_pending_registration == ()

    def test_new_tag_pending_not_silent(self) -> None:
        payload = _factor_payload(tags=["动量", "自创词甲"])
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.classification.tags == ["动量"]
        assert result.tags_pending_registration == ("自创词甲",)

    def test_duplicate_tags_deduped(self) -> None:
        payload = _factor_payload(tags=["翻转", "反转", "动量", "动量"])
        result = KnowledgeClassifier(llm=_FakeGateway(payload)).classify(_item())
        assert result.classification.tags == ["反转", "动量"]

    def test_custom_known_tags(self) -> None:
        payload = _factor_payload(tags=["动量", "私有词"])
        clf = KnowledgeClassifier(
            llm=_FakeGateway(payload), known_tags=frozenset({"私有词"})
        )
        result = clf.classify(_item())
        assert result.classification.tags == ["私有词"]
        assert result.tags_pending_registration == ("动量",)
