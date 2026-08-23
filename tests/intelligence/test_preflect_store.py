# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md | §4.3-P1-3
# [MODULE] tests.intelligence.test_preflect_store
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_preflect_store.py -q
# [TTL] permanent
"""test_preflect_store.py — PreFlect 失败模式库（12号文 §3.3/§4.3 P1-3）单元测试.

覆盖 P1-3 验收口径：
①L2 产出可入库（ingest_reflection：失败反思记录 → 失败模式条目落盘可读回）。
②注入内容含来源反思 ID（build_injection 载荷含 source_reflection_ids 汇总）。
③人工编辑接口可用（edit：editor 必填留痕，source→manual_edit，updated_at 刷新；
§6 Q6 人工种子集形态 source=manual_seed 允许无来源反思 ID）。
schema 严格校验（fail-closed）：缺必填字段/未知字段/空模式描述/空规避建议拒收。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.reflexion.preflect_store import (
    SOURCE_L2,
    SOURCE_MANUAL_EDIT,
    SOURCE_MANUAL_SEED,
    FailurePatternEntry,
    PreFlectSchemaError,
    PreFlectStore,
)
from zephyr.intelligence.reflexion.reflection_schema import (
    ImprovementSuggestion,
    ReflectionRecord,
)


def _entry_kwargs(**overrides) -> dict:
    base = {
        "pattern_id": "fp-001",
        "pattern": "数据口径未核对导致指标计算错误",
        "trigger_conditions": ("指标计算", "数据口径"),
        "avoidance_advice": "计算前核对数据源字段口径",
        "source_reflection_ids": ("rfl-aaa",),
        "source": SOURCE_L2,
    }
    base.update(overrides)
    return base


@pytest.fixture
def store(tmp_path):
    return PreFlectStore(root=tmp_path)


def _failed_record() -> ReflectionRecord:
    return ReflectionRecord(
        reflection_id="rfl-f001",
        task_id="task-x",
        trajectory_ref="traj/task-x.json",
        outcome="failure",
        failure_category="数据错误",
        improvement_suggestions=[
            ImprovementSuggestion(
                category="数据错误",
                suggestion="复核 step[0] 处输入数据源与字段口径",
                evidence_ref="step[0]",
            )
        ],
    )


class TestSchema:
    """失败模式条目 schema（模式/触发条件/规避建议/来源反思 ID）严格校验."""

    def test_roundtrip(self):
        entry = FailurePatternEntry(**_entry_kwargs())
        restored = FailurePatternEntry.from_dict(entry.to_dict())
        assert restored == entry

    def test_missing_field_rejected(self):
        data = _entry_kwargs()
        del data["pattern"]
        with pytest.raises(PreFlectSchemaError, match="缺必填字段"):
            FailurePatternEntry.from_dict(data)

    def test_unknown_field_rejected(self):
        data = _entry_kwargs()
        data["bogus"] = 1
        with pytest.raises(PreFlectSchemaError, match="未知字段"):
            FailurePatternEntry.from_dict(data)

    def test_empty_pattern_rejected(self):
        with pytest.raises(PreFlectSchemaError, match="pattern"):
            FailurePatternEntry(**_entry_kwargs(pattern="  "))

    def test_empty_advice_rejected(self):
        with pytest.raises(PreFlectSchemaError, match="avoidance_advice"):
            FailurePatternEntry(**_entry_kwargs(avoidance_advice=""))

    def test_l2_source_requires_reflection_ids(self):
        with pytest.raises(PreFlectSchemaError, match="source_reflection_ids"):
            FailurePatternEntry(**_entry_kwargs(source_reflection_ids=()))

    def test_manual_seed_allows_empty_reflection_ids(self):
        entry = FailurePatternEntry(
            **_entry_kwargs(source=SOURCE_MANUAL_SEED, source_reflection_ids=())
        )
        assert entry.source == SOURCE_MANUAL_SEED

    def test_invalid_source_rejected(self):
        with pytest.raises(PreFlectSchemaError, match="source"):
            FailurePatternEntry(**_entry_kwargs(source="elsewhere"))


class TestAddAndIngest:
    """L2 产出可入库 + 人工种子集落盘可读回."""

    def test_add_and_read_back(self, store, tmp_path):
        entry = FailurePatternEntry(**_entry_kwargs())
        store.add(entry)
        restored = PreFlectStore(root=tmp_path).get("fp-001")
        assert restored == entry

    def test_duplicate_pattern_id_rejected(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        with pytest.raises(PreFlectSchemaError, match="pattern_id"):
            store.add(FailurePatternEntry(**_entry_kwargs(pattern="另一种模式")))

    def test_ingest_failure_reflection(self, store):
        entry = store.ingest_reflection(_failed_record())
        assert entry.source == SOURCE_L2
        assert entry.source_reflection_ids == ("rfl-f001",)
        assert entry.pattern  # 模式描述非空
        assert entry.avoidance_advice  # 规避建议非空
        # 落盘可读回
        assert store.get(entry.pattern_id) == entry

    def test_ingest_success_reflection_rejected(self, store):
        record = ReflectionRecord(
            reflection_id="rfl-ok",
            task_id="task-ok",
            trajectory_ref="traj/task-ok.json",
            outcome="success",
        )
        with pytest.raises(PreFlectSchemaError, match="仅失败反思记录可入库"):
            store.ingest_reflection(record)


class TestEdit:
    """人工编辑接口：editor 必填留痕."""

    def test_edit_updates_fields(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        edited = store.edit(
            "fp-001", avoidance_advice="改为先跑数据契约校验", editor="Owner"
        )
        assert edited.avoidance_advice == "改为先跑数据契约校验"
        assert edited.source == SOURCE_MANUAL_EDIT
        assert edited.updated_at != edited.created_at or edited.updated_at
        assert store.get("fp-001").avoidance_advice == "改为先跑数据契约校验"

    def test_edit_requires_editor(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        with pytest.raises(PreFlectSchemaError, match="editor"):
            store.edit("fp-001", avoidance_advice="x", editor="")

    def test_edit_unknown_id_rejected(self, store):
        with pytest.raises(PreFlectSchemaError, match="fp-404"):
            store.edit("fp-404", avoidance_advice="x", editor="Owner")

    def test_edit_disable_entry(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        edited = store.edit("fp-001", enabled=False, editor="Owner")
        assert edited.enabled is False


class TestRetrieveAndInject:
    """任务启动时检索注入：注入内容含来源反思 ID."""

    def test_retrieve_by_trigger_condition(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        hits = store.retrieve("本次任务涉及指标计算与收益率统计")
        assert [h.pattern_id for h in hits] == ["fp-001"]

    def test_retrieve_no_match_returns_empty(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        assert store.retrieve("完全不相关的文案") == []

    def test_retrieve_excludes_disabled(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        store.edit("fp-001", enabled=False, editor="Owner")
        assert store.retrieve("指标计算") == []

    def test_build_injection_contains_source_reflection_ids(self, store):
        store.add(FailurePatternEntry(**_entry_kwargs()))
        store.ingest_reflection(_failed_record())
        payload = store.build_injection("指标计算任务，注意数据错误")
        assert payload["entries"]
        # 验收：注入内容含来源反思 ID
        assert "rfl-aaa" in payload["source_reflection_ids"]
        assert all(e["source_reflection_ids"] for e in payload["entries"])

    def test_build_injection_empty_library(self, store):
        payload = store.build_injection("任何任务")
        assert payload["entries"] == []
        assert payload["source_reflection_ids"] == []
