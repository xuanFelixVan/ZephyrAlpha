# [BLUEPRINT] MOD-KNW-005 | docs/03_modules/_domain_knowledge/factor_knowledge_base/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-005 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_factor_knowledge_base
# [TESTS] src/zephyr/knowledge/factor_knowledge_base.py
"""MOD-KNW-005 单元测试：factor_knowledge_base 因子知识库。

蓝图验收（B10-02181/CAND-KNW-004，A1 D-KNOWLEDGE-02）：
定义/关系/历史三表（关系词表闭合 same_family|orthogonal|parent_child）+
状态机 DRAFT→ACTIVE→DEPRECATED + IC 序列/衰减 + kb 写入回调注入 +
按类别/状态/相关性查询确定性排序。时钟/kb_writer 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.factor_knowledge_base",
    reason="factor_knowledge_base not importable",
)

from zephyr.knowledge.factor_knowledge_base import (  # noqa: E402
    FactorDefinition,
    FactorKbError,
    FactorKnowledgeBase,
    FactorStatus,
    RelationType,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 30, 0)
_T2 = datetime.datetime(2026, 8, 26, 11, 30, 0)


def _def(factor_id: str = "mom_20", category: str = "动量") -> FactorDefinition:
    return FactorDefinition(
        factor_id=factor_id,
        formula="close / close.shift(20) - 1",
        category=category,
        hypothesis="过去20日涨幅正向预测未来收益",
    )


def _kb(entries: list | None = None) -> FactorKnowledgeBase:
    return FactorKnowledgeBase(
        clock=lambda: _T0,
        kb_writer=(lambda e: entries.append(e)) if entries is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 定义表注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterFactor:
    def test_register_ok_initial_draft(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        assert kb.get_definition("mom_20").category == "动量"
        assert kb.get_status("mom_20") is FactorStatus.DRAFT

    def test_register_writes_kb_callback(self) -> None:
        entries: list[dict] = []
        kb = _kb(entries)
        kb.register_factor(_def())
        assert len(entries) == 1
        assert entries[0]["kind"] == "factor_definition"
        assert entries[0]["factor_id"] == "mom_20"
        assert entries[0]["status"] == "draft"

    def test_register_empty_fields_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.register_factor(FactorDefinition(factor_id="", formula="f", category="c", hypothesis="h"))
        with pytest.raises(FactorKbError):
            kb.register_factor(FactorDefinition(factor_id="x", formula="", category="c", hypothesis="h"))
        with pytest.raises(FactorKbError):
            kb.register_factor(FactorDefinition(factor_id="x", formula="f", category="", hypothesis="h"))
        with pytest.raises(FactorKbError):
            kb.register_factor(FactorDefinition(factor_id="x", formula="f", category="c", hypothesis=""))

    def test_register_duplicate_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        with pytest.raises(FactorKbError):
            kb.register_factor(_def())

    def test_unknown_factor_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.get_definition("ghost")
        with pytest.raises(FactorKbError):
            kb.get_status("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 关系表（词表闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestRelations:
    def _two(self, kb: FactorKnowledgeBase) -> None:
        kb.register_factor(_def("mom_20"))
        kb.register_factor(_def("mom_60"))

    def test_add_relation_ok(self) -> None:
        kb = _kb()
        self._two(kb)
        kb.add_relation("mom_20", "mom_60", RelationType.SAME_FAMILY)
        assert kb.related_factors("mom_20") == ("mom_60",)
        assert kb.related_factors("mom_60") == ("mom_20",)  # 双向可见

    def test_relation_unknown_factor_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def("mom_20"))
        with pytest.raises(FactorKbError):
            kb.add_relation("mom_20", "ghost", RelationType.ORTHOGONAL)
        with pytest.raises(FactorKbError):
            kb.add_relation("ghost", "mom_20", RelationType.ORTHOGONAL)

    def test_relation_self_loop_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def("mom_20"))
        with pytest.raises(FactorKbError):
            kb.add_relation("mom_20", "mom_20", RelationType.SAME_FAMILY)

    def test_relation_bad_vocab_raises(self) -> None:
        kb = _kb()
        self._two(kb)
        with pytest.raises(FactorKbError):
            kb.add_relation("mom_20", "mom_60", "cousin")  # 词表外

    def test_relation_duplicate_idempotent(self) -> None:
        kb = _kb()
        self._two(kb)
        kb.add_relation("mom_20", "mom_60", RelationType.SAME_FAMILY)
        kb.add_relation("mom_20", "mom_60", RelationType.SAME_FAMILY)  # 幂等不抛
        assert kb.related_factors("mom_20") == ("mom_60",)

    def test_related_filter_by_type_and_sorted(self) -> None:
        kb = _kb()
        for fid in ("a", "b", "c", "d"):
            kb.register_factor(_def(fid))
        kb.add_relation("a", "c", RelationType.SAME_FAMILY)
        kb.add_relation("a", "b", RelationType.SAME_FAMILY)
        kb.add_relation("a", "d", RelationType.PARENT_CHILD)
        assert kb.related_factors("a", RelationType.SAME_FAMILY) == ("b", "c")  # 确定性排序
        assert kb.related_factors("a", RelationType.PARENT_CHILD) == ("d",)
        assert kb.related_factors("a") == ("b", "c", "d")
        assert kb.related_factors("a", RelationType.ORTHOGONAL) == ()

    def test_related_unknown_factor_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.related_factors("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 历史表（IC 序列/衰减/状态变迁）
# ──────────────────────────────────────────────────────────────────────────────


class TestHistory:
    def test_record_ic_ok_and_series_sorted(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        kb.record_ic("mom_20", 0.05, observed_at=_T2)
        kb.record_ic("mom_20", 0.08, observed_at=_T1)  # 乱序写入
        series = kb.ic_series("mom_20")
        assert [r.ic_value for r in series] == [0.08, 0.05]  # 按 observed_at 排序
        assert series[0].observed_at == _T1

    def test_record_ic_default_clock(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        rec = kb.record_ic("mom_20", 0.1)
        assert rec.observed_at == _T0

    def test_record_ic_out_of_range_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        with pytest.raises(FactorKbError):
            kb.record_ic("mom_20", 1.5)
        with pytest.raises(FactorKbError):
            kb.record_ic("mom_20", -1.2)

    def test_record_ic_unknown_factor_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.record_ic("ghost", 0.1)

    def test_ic_decay_slope(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        kb.record_ic("mom_20", 0.10, observed_at=_T0)
        kb.record_ic("mom_20", 0.06, observed_at=_T1)
        kb.record_ic("mom_20", 0.02, observed_at=_T2)
        assert kb.ic_decay("mom_20") == pytest.approx(-0.04)  # 每期衰减 0.04

    def test_ic_decay_insufficient_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        with pytest.raises(FactorKbError):
            kb.ic_decay("mom_20")  # 0 样本
        kb.record_ic("mom_20", 0.1)
        with pytest.raises(FactorKbError):
            kb.ic_decay("mom_20")  # 1 样本


# ──────────────────────────────────────────────────────────────────────────────
# 状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestStatusMachine:
    def test_legal_transition_with_history_and_kb(self) -> None:
        entries: list[dict] = []
        kb = _kb(entries)
        kb.register_factor(_def())
        tr = kb.transition_status("mom_20", FactorStatus.ACTIVE)
        assert kb.get_status("mom_20") is FactorStatus.ACTIVE
        assert tr.from_status is FactorStatus.DRAFT
        assert tr.changed_at == _T0
        history = kb.status_history("mom_20")
        assert len(history) == 1
        assert entries[-1]["kind"] == "factor_status"
        assert entries[-1]["to_status"] == "active"

    def test_full_lifecycle(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        kb.transition_status("mom_20", FactorStatus.ACTIVE)
        kb.transition_status("mom_20", FactorStatus.DEPRECATED)
        assert kb.get_status("mom_20") is FactorStatus.DEPRECATED
        assert [t.to_status for t in kb.status_history("mom_20")] == [
            FactorStatus.ACTIVE,
            FactorStatus.DEPRECATED,
        ]

    def test_illegal_transition_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        kb.transition_status("mom_20", FactorStatus.DEPRECATED)
        with pytest.raises(FactorKbError):
            kb.transition_status("mom_20", FactorStatus.ACTIVE)  # 终态不可逆

    def test_transition_unknown_factor_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.transition_status("ghost", FactorStatus.ACTIVE)

    def test_transition_bad_vocab_raises(self) -> None:
        kb = _kb()
        kb.register_factor(_def())
        with pytest.raises(FactorKbError):
            kb.transition_status("mom_20", "paused")  # 词表外


# ──────────────────────────────────────────────────────────────────────────────
# 查询（确定性排序）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_by_category_sorted(self) -> None:
        kb = _kb()
        kb.register_factor(_def("vol_20", category="波动"))
        kb.register_factor(_def("mom_60", category="动量"))
        kb.register_factor(_def("mom_20", category="动量"))
        out = kb.by_category("动量")
        assert [d.factor_id for d in out] == ["mom_20", "mom_60"]  # 确定性排序
        assert kb.by_category("价值") == ()

    def test_by_category_empty_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.by_category("")

    def test_by_status_sorted(self) -> None:
        kb = _kb()
        kb.register_factor(_def("b"))
        kb.register_factor(_def("a"))
        kb.transition_status("a", FactorStatus.ACTIVE)
        assert [d.factor_id for d in kb.by_status(FactorStatus.ACTIVE)] == ["a"]
        assert [d.factor_id for d in kb.by_status(FactorStatus.DRAFT)] == ["b"]

    def test_by_status_bad_vocab_raises(self) -> None:
        kb = _kb()
        with pytest.raises(FactorKbError):
            kb.by_status("paused")

    def test_determinism_same_input_same_output(self) -> None:
        def _build() -> tuple:
            kb = _kb()
            kb.register_factor(_def("x"))
            kb.register_factor(_def("y"))
            kb.add_relation("x", "y", RelationType.ORTHOGONAL)
            kb.record_ic("x", 0.1, observed_at=_T0)
            kb.record_ic("x", 0.2, observed_at=_T1)
            return (
                kb.related_factors("x"),
                tuple(r.ic_value for r in kb.ic_series("x")),
                kb.ic_decay("x"),
                tuple(d.factor_id for d in kb.by_status(FactorStatus.DRAFT)),
            )

        assert _build() == _build()
