# [BLUEPRINT] MOD-FACTORY-002 | docs/03_modules/_domain_autonomy_core/module_mapper/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FACTORY-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.autonomy.test_module_mapper
# [TESTS] src/zephyr/autonomy_core/module_factory/module_mapper.py
"""MOD-FACTORY-002 单元测试：module_mapper 知识→模块映射引擎（13号文 §3.3）。

覆盖验收点：四选一裁决各一例（new_entry/variant_of/reject_duplicate/combination）/
重复检出 / 变体判定 / embedding 缺失与异常降级显式标注 / 失效墓园告警 /
schema_plan LLM 生成失败 fail-closed / 注册表 YAML 只读加载。
LLM/embedding/注册表全 fake+夹具（tmp_path YAML 或直接注入语料），禁网络禁真 LLM。
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip(
    "zephyr.autonomy_core.module_factory.module_mapper",
    reason="module_mapper not importable",
)

from zephyr.autonomy_core.module_factory.knowledge_classifier import (  # noqa: E402
    ClassificationPayload,
    ClassificationResult,
    KnowledgeItem,
    QualityScores,
)
from zephyr.autonomy_core.module_factory.module_mapper import (  # noqa: E402
    MAPPER_TASK_TYPE,
    MapperThresholds,
    ModuleMapper,
    ModuleMapperError,
    load_registry_entries,
)

# ──────────────────────────────────────────────────────────────────────────────
# 夹具
# ──────────────────────────────────────────────────────────────────────────────

_PLAN = {
    "event": "二十日收益率突破均线",
    "context": "趋势市场环境",
    "qualities": "流动性过滤低质",
    "direction": "做多强势股",
    "output": "截面排序打分",
}

_ITEM = KnowledgeItem(
    knowledge_id="KE-T-001",
    title="动量反转双因子策略",
    content="动量与反转组合的选股思路。",
    source_ref="unit-test",
)


class _FakeResponse:
    def __init__(self, status: str = "ok", text: str = "") -> None:
        self.status = status
        self.text = text


class _FakeGateway:
    """schema_plan 生成用假 LLM 网关（对齐 llm_runtime_gateway infer 签名）。"""

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


class _HashEmbedder:
    """确定性假 embedding：字符袋hash向量（进程内一致即可，无需真模型）。"""

    def __init__(self, dim: int = 256) -> None:
        self._dim = dim

    def embed(self, text, collection_name):
        vec = [0.0] * self._dim
        for ch in text:
            vec[hash(ch) % self._dim] += 1.0
        return vec


class _BoomEmbedder:
    def embed(self, text, collection_name):
        raise RuntimeError("embedding backend down")


def _classification(**over) -> ClassificationResult:
    kwargs = {
        "quality": QualityScores(relevance=0.9, timeliness=0.9, information=0.9, reliability=0.9),
        "target_kind": "factor",
        "factor_class": "momentum",
        "strategy_class": None,
        "other_subtype": None,
        "primary_timeframe": "daily",
        "applicable_timeframes": ["daily"],
        "regime_valid": ["trend_up"],
        "regime_invalid": [],
        "direction": "long",
        "entry_role": "ranking",
        "applies_to": ["stock"],
        "tags": ["动量"],
        "confidence": 0.9,
        "rationale": "fixture",
    }
    kwargs.update(over)
    return ClassificationResult(
        verdict="classified",
        knowledge_id="KE-T-001",
        classification=ClassificationPayload(**kwargs),
    )


def _factor_entry(fid: str, name: str, formula: str, *, status: str = "candidate") -> dict:
    return {
        "registry": "factor_registry",
        "factor_id": fid,
        "name": name,
        "name_zh": name,
        "aliases": [],
        "factor_class": "momentum",
        "formula": formula,
        "tags": ["动量"],
        "status": status,
    }


def _mapper(entries, **kw) -> ModuleMapper:
    kw.setdefault("entries", entries)
    return ModuleMapper(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期阈值校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_threshold_order_violation_raises(self) -> None:
        with pytest.raises(ModuleMapperError):
            ModuleMapper(
                entries=[],
                thresholds=MapperThresholds(duplicate=0.5, variant=0.7),
            )

    def test_non_positive_weight_raises(self) -> None:
        with pytest.raises(ModuleMapperError):
            ModuleMapper(entries=[], thresholds=MapperThresholds(embedding_weight=0.0))

    def test_combination_min_components_guard(self) -> None:
        with pytest.raises(ModuleMapperError):
            ModuleMapper(
                entries=[],
                thresholds=MapperThresholds(combination_min_components=1),
            )


# ──────────────────────────────────────────────────────────────────────────────
# 入口契约（fail-closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestEntryContract:
    def test_rejected_classification_refused(self) -> None:
        rejected = ClassificationResult(verdict="rejected", knowledge_id="KE-T-001")
        with pytest.raises(ModuleMapperError):
            _mapper([]).map_knowledge(_ITEM, rejected, schema_plan=_PLAN)

    def test_invalid_provided_schema_plan_raises(self) -> None:
        bad_plan = {"event": "x"}  # 缺键
        with pytest.raises(ModuleMapperError):
            _mapper([]).map_knowledge(_ITEM, _classification(), schema_plan=bad_plan)

    def test_schema_plan_llm_garbage_fail_closed(self) -> None:
        gw = _FakeGateway("这不是JSON")
        spec = _mapper([], llm=gw).map_knowledge(_ITEM, _classification())
        assert spec.verdict == "error"
        assert spec.entry_draft is None
        assert spec.human_gate_required is True
        assert gw.calls[0][0] == MAPPER_TASK_TYPE

    def test_schema_plan_llm_blocked_fail_closed(self) -> None:
        gw = _FakeGateway(_PLAN, status="blocked")
        spec = _mapper([], llm=gw).map_knowledge(_ITEM, _classification())
        assert spec.verdict == "error"

    def test_schema_plan_llm_success(self) -> None:
        gw = _FakeGateway(_PLAN)
        spec = _mapper([], llm=gw).map_knowledge(_ITEM, _classification())
        assert spec.verdict == "new_entry"
        assert spec.schema_plan == _PLAN
        assert gw.calls[0][0] == MAPPER_TASK_TYPE

    def test_provided_schema_plan_skips_llm(self) -> None:
        gw = _FakeGateway(RuntimeError("must not be called"))
        spec = _mapper([], llm=gw).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        assert spec.verdict == "new_entry"
        assert gw.calls == []


# ──────────────────────────────────────────────────────────────────────────────
# 四选一裁决（FTS5-only 通道，embedding 缺失降级）
# ──────────────────────────────────────────────────────────────────────────────

_FULL_COVER_FORMULA = (
    "动量反转双因子策略 二十日收益率突破均线 趋势市场环境 "
    "流动性过滤低质 做多强势股 截面排序打分"
)


class TestVerdicts:
    def test_reject_duplicate(self) -> None:
        entries = [_factor_entry("FCT-MOM-001", "动量反转双因子策略", _FULL_COVER_FORMULA)]
        spec = _mapper(entries).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        assert spec.verdict == "reject_duplicate"
        assert spec.candidates[0].entry_id == "FCT-MOM-001"
        assert spec.candidates[0].score == pytest.approx(1.0)
        assert spec.entry_draft is None  # 重复不产草稿
        assert "重复" in spec.rationale
        assert spec.human_gate_required is True

    def test_variant_of(self) -> None:
        entries = [
            _factor_entry(
                "FCT-MOM-002",
                "动量反转半相似因子",
                "动量反转双因子策略 二十日收益率突破均线 趋势市场环境",
            )
        ]
        thresholds = MapperThresholds(duplicate=0.97, variant=0.3, combination=0.1)
        spec = _mapper(entries, thresholds=thresholds).map_knowledge(
            _ITEM, _classification(), schema_plan=_PLAN
        )
        assert spec.verdict == "variant_of"
        assert spec.candidates[0].entry_id == "FCT-MOM-002"
        assert 0.3 <= spec.candidates[0].score < 0.97
        assert spec.entry_draft["variant_of"] == "FCT-MOM-002"
        assert "parent=FCT-MOM-002" in spec.rationale

    def test_new_entry(self) -> None:
        entries = [_factor_entry("FCT-QLT-001", "盈利质量因子", "财报盈利质量评估审计")]
        spec = _mapper(entries).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        assert spec.verdict == "new_entry"
        assert spec.target_registry == "factor_registry"
        assert spec.entry_draft is not None
        assert spec.entry_draft["variant_of"] is None
        assert spec.code_skeleton is not None

    def test_combination(self) -> None:
        entries = [
            _factor_entry(
                "FCT-MOM-003", "动量侧", "动量反转双因子策略 二十日收益率突破均线"
            ),
            _factor_entry("FCT-REV-003", "反转侧", "做多强势股 截面排序打分"),
        ]
        thresholds = MapperThresholds(
            duplicate=0.97, variant=0.9, combination=0.15, combination_min_components=2
        )
        spec = _mapper(entries, thresholds=thresholds).map_knowledge(
            _ITEM, _classification(), schema_plan=_PLAN
        )
        assert spec.verdict == "combination"
        assert set(spec.code_skeleton["components"]) == {"FCT-MOM-003", "FCT-REV-003"}
        assert "组合成分" in spec.rationale

    def test_empty_corpus_new_entry(self) -> None:
        spec = _mapper([]).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        assert spec.verdict == "new_entry"
        assert spec.candidates == ()


# ──────────────────────────────────────────────────────────────────────────────
# embedding 通道：双通道 / 缺失降级 / 异常降级（显式标注）
# ──────────────────────────────────────────────────────────────────────────────


class TestRetrievalChannels:
    def test_dual_channel(self) -> None:
        entries = [_factor_entry("FCT-MOM-001", "动量反转双因子策略", _FULL_COVER_FORMULA)]
        spec = _mapper(entries, embedder=_HashEmbedder()).map_knowledge(
            _ITEM, _classification(), schema_plan=_PLAN
        )
        assert spec.retrieval_channel == "dual"
        assert spec.degraded is False
        assert spec.degradation_reason is None
        assert spec.candidates[0].embedding_score is not None
        assert spec.candidates[0].fts_score is not None

    def test_embedding_missing_degrades_fts_only(self) -> None:
        entries = [_factor_entry("FCT-MOM-001", "动量反转双因子策略", _FULL_COVER_FORMULA)]
        spec = _mapper(entries, embedder=None).map_knowledge(
            _ITEM, _classification(), schema_plan=_PLAN
        )
        assert spec.retrieval_channel == "fts_only"
        assert spec.degraded is True
        assert "未注入" in spec.degradation_reason
        assert "降级" in spec.rationale
        # 降级不影响裁决：完全覆盖仍检出重复
        assert spec.verdict == "reject_duplicate"

    def test_embedding_exception_degrades_fts_only(self) -> None:
        entries = [_factor_entry("FCT-MOM-001", "动量反转双因子策略", _FULL_COVER_FORMULA)]
        spec = _mapper(entries, embedder=_BoomEmbedder()).map_knowledge(
            _ITEM, _classification(), schema_plan=_PLAN
        )
        assert spec.retrieval_channel == "fts_only"
        assert spec.degraded is True
        assert "异常" in spec.degradation_reason
        assert spec.verdict == "reject_duplicate"


# ──────────────────────────────────────────────────────────────────────────────
# 失效墓园告警 + 其他分流 + ModuleSpec 草稿纪律
# ──────────────────────────────────────────────────────────────────────────────


class TestGovernance:
    def test_retired_graveyard_warning(self) -> None:
        entries = [
            _factor_entry(
                "FCT-OLD-001", "已退役动量因子", _FULL_COVER_FORMULA, status="retired"
            )
        ]
        spec = _mapper(entries).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        assert spec.verdict == "reject_duplicate"
        assert spec.candidates[0].retired is True
        assert "失效墓园" in spec.rationale

    def test_other_kind_routed_without_retrieval(self) -> None:
        cls = _classification(
            target_kind="other",
            factor_class=None,
            other_subtype="risk_rule",
        )
        spec = _mapper([_factor_entry("FCT-MOM-001", "x", _FULL_COVER_FORMULA)]).map_knowledge(
            _ITEM, cls, schema_plan=_PLAN
        )
        assert spec.verdict == "routed"
        assert spec.target_registry == "risk_limit_registry"
        assert spec.retrieval_channel == "none"
        assert spec.candidates == ()

    def test_factor_entry_draft_must_fields(self) -> None:
        spec = _mapper([]).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        draft = spec.entry_draft
        assert draft["status"] == "candidate"
        assert draft["algorithm_status"] == "pending_backtest"
        assert draft["evidence"] == ""
        assert draft["discovery_agent"] == "module_factory"
        assert draft["schema_plan"] == _PLAN
        assert draft["factor_class"] == "momentum"
        assert draft["tags"] == ["动量"]
        assert spec.draft_notes  # 人审待办留痕

    def test_strategy_entry_draft_must_fields(self) -> None:
        cls = _classification(
            target_kind="strategy",
            factor_class=None,
            strategy_class="momentum_trend",
            entry_role="trigger",
        )
        spec = _mapper([]).map_knowledge(_ITEM, cls, schema_plan=_PLAN)
        assert spec.target_registry == "strategy_registry"
        draft = spec.entry_draft
        assert draft["lifecycle_status"] == "candidate"
        assert draft["origin"] == "hybrid"
        assert draft["risk_rules"] == []
        assert draft["strategy_class"] == "momentum_trend"
        assert spec.code_skeleton["form"] == "strategy_template"

    def test_verification_plan_l4_human_gate(self) -> None:
        spec = _mapper([]).map_knowledge(_ITEM, _classification(), schema_plan=_PLAN)
        assert any("L4" in step for step in spec.verification_plan)
        assert spec.human_gate_required is True


# ──────────────────────────────────────────────────────────────────────────────
# 注册表 YAML 只读加载
# ──────────────────────────────────────────────────────────────────────────────


class TestRegistryLoading:
    def test_load_from_tmp_yaml(self, tmp_path) -> None:
        (tmp_path / "factor_registry.yaml").write_text(
            "factors:\n"
            "- factor_id: FCT-T-001\n"
            "  name: 测试因子\n"
            "  status: candidate\n",
            encoding="utf-8",
        )
        (tmp_path / "strategy_registry.yaml").write_text(
            "strategies:\n"
            "- strategy_id: STR-T-001\n"
            "  name: 测试策略\n"
            "  status: retired\n",
            encoding="utf-8",
        )
        docs = load_registry_entries(tmp_path)
        assert len(docs) == 2
        by_id = {d.entry_id: d for d in docs}
        assert by_id["FCT-T-001"].registry == "factor_registry"
        assert by_id["STR-T-001"].registry == "strategy_registry"
        assert by_id["STR-T-001"].retired is True

    def test_missing_registry_file_raises(self, tmp_path) -> None:
        with pytest.raises(ModuleMapperError):
            load_registry_entries(tmp_path)

    def test_real_catalogs_readonly_load(self) -> None:
        # 真实注册表只读加载（catalogs active 语料；本模块无写路径）
        docs = load_registry_entries()
        assert len(docs) >= 200
        assert any(d.entry_id.startswith("FCT-") for d in docs)
        assert any(d.entry_id.startswith("STR-") for d in docs)
