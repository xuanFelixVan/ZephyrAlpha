# [BLUEPRINT] MOD-FBL-003 | docs/03_modules/_domain_feedback_loop/skill_library/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FBL-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.feedback_loop.test_skill_library
# [TESTS] src/zephyr/feedback_loop/skill_library.py
"""MOD-FBL-003 单元测试：skill_library Voyager 式技能库。

蓝图验收（B12-03612/CAND-FBL-005，B12）：
技能条目 Schema（三类词表闭合+来源任务+成功指标）+ 向量索引（注入 embedder+
余弦 TopK 检索，同分确定性 tie-break）+ 复用登记 + 版本递增。
embedder/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.feedback_loop.skill_library",
    reason="skill_library not importable",
)

from zephyr.feedback_loop.skill_library import (  # noqa: E402
    SkillEntry,
    SkillKind,
    SkillLibrary,
    SkillLibraryError,
    SkillReuseRecord,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 30, 0)


def _embed(text: str) -> tuple[float, float, float]:
    """确定性关键词计数 embedder（内存替身）：三维词袋。"""
    return (
        float(text.count("动量")),
        float(text.count("均值")),
        float(text.count("突破")),
    )


def _library(clock=lambda: _T0) -> SkillLibrary:
    return SkillLibrary(embedder=_embed, clock=clock)


def _register(lib: SkillLibrary, content: str = "动量策略代码", **kw) -> SkillEntry:
    return lib.register_skill(
        kind=kw.pop("kind", SkillKind.CODE_SNIPPET),
        content=content,
        source_task=kw.pop("source_task", "任务-001"),
        success_metrics=kw.pop("success_metrics", {"sharpe": 1.5}),
        **kw,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注册（Schema 校验 + 词表闭合 + skill_id 递增）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterSkill:
    def test_register_ok_fields(self) -> None:
        lib = _library()
        entry = _register(lib)
        assert entry.skill_id == "skill-0001"
        assert entry.kind is SkillKind.CODE_SNIPPET
        assert entry.source_task == "任务-001"
        assert entry.success_metrics == {"sharpe": 1.5}
        assert entry.version == 1
        assert entry.embedding == (1.0, 0.0, 0.0)
        assert entry.created_at == _T0
        assert len(lib) == 1

    def test_skill_id_deterministic_increment(self) -> None:
        lib = _library()
        e1 = _register(lib, "动量")
        e2 = _register(lib, "均值")
        e3 = _register(lib, "突破")
        assert (e1.skill_id, e2.skill_id, e3.skill_id) == (
            "skill-0001", "skill-0002", "skill-0003",
        )

    def test_kind_str_accepted_and_normalized(self) -> None:
        lib = _library()
        entry = _register(lib, kind="factor_formula")
        assert entry.kind is SkillKind.FACTOR_FORMULA

    def test_kind_invalid_rejected(self) -> None:
        lib = _library()
        with pytest.raises(SkillLibraryError):
            _register(lib, kind="magic_recipe")  # 词表外
        with pytest.raises(SkillLibraryError):
            _register(lib, kind=123)  # 非法类型

    def test_empty_content_or_source_task_rejected(self) -> None:
        lib = _library()
        with pytest.raises(SkillLibraryError):
            _register(lib, "")
        with pytest.raises(SkillLibraryError):
            _register(lib, source_task="")

    def test_metrics_invalid_rejected(self) -> None:
        lib = _library()
        bad_metrics = (
            [("sharpe", 1.5)],          # 非映射
            {"sharpe": "高"},           # 非数值
            {"sharpe": float("nan")},   # 非有限
            {"": 1.0},                  # 空指标名
            {"sharpe": True},           # bool 非数值
        )
        for bad in bad_metrics:
            with pytest.raises(SkillLibraryError):
                _register(lib, success_metrics=bad)


# ──────────────────────────────────────────────────────────────────────────────
# embedder 注入（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestEmbedderInjection:
    def test_embedder_not_injected_fail_closed(self) -> None:
        with pytest.raises(SkillLibraryError):
            SkillLibrary(embedder=None, clock=lambda: _T0)

    def test_embedder_bad_vector_rejected(self) -> None:
        bad_embedders = (
            lambda t: (),                        # 空向量
            lambda t: ("x", 1.0),                # 非数值分量
            lambda t: (float("nan"), 1.0),       # 非有限分量
        )
        for bad in bad_embedders:
            lib = SkillLibrary(embedder=bad, clock=lambda: _T0)
            with pytest.raises(SkillLibraryError):
                _register(lib)


# ──────────────────────────────────────────────────────────────────────────────
# 向量检索（余弦 TopK + 确定性 tie-break）
# ──────────────────────────────────────────────────────────────────────────────


class TestRetrieve:
    def test_top1_most_similar(self) -> None:
        lib = _library()
        _register(lib, "均值均值回归模板", kind=SkillKind.STRATEGY_TEMPLATE)
        _register(lib, "动量动量动量因子", kind=SkillKind.FACTOR_FORMULA)
        hits = lib.retrieve("动量策略", top_k=1)
        assert len(hits) == 1
        assert hits[0].kind is SkillKind.FACTOR_FORMULA  # 动量计数更近

    def test_top_k_order_by_similarity(self) -> None:
        lib = _library()
        _register(lib, "动量均值")          # (1,1,0)
        _register(lib, "动量动量均值")      # (2,1,0)
        _register(lib, "突破突破突破")      # (0,0,3)
        hits = lib.retrieve("动量动量", top_k=3)  # (2,0,0)
        assert [h.skill_id for h in hits] == ["skill-0002", "skill-0001", "skill-0003"]

    def test_tie_break_by_skill_id(self) -> None:
        lib = _library()
        _register(lib, "动量")  # skill-0001
        _register(lib, "动量")  # skill-0002（同向量同分）
        hits = lib.retrieve("动量", top_k=2)
        assert [h.skill_id for h in hits] == ["skill-0001", "skill-0002"]

    def test_top_k_exceeds_size_and_empty_library(self) -> None:
        lib = _library()
        assert lib.retrieve("动量") == ()  # 空库返回空
        _register(lib, "动量")
        assert len(lib.retrieve("动量", top_k=99)) == 1  # 超量截断

    def test_invalid_top_k_rejected(self) -> None:
        lib = _library()
        _register(lib)
        for bad in (0, -1, 1.5, True, "2"):
            with pytest.raises(SkillLibraryError):
                lib.retrieve("动量", top_k=bad)

    def test_empty_task_description_rejected(self) -> None:
        lib = _library()
        with pytest.raises(SkillLibraryError):
            lib.retrieve("")

    def test_dimension_mismatch_fail_closed(self) -> None:
        calls = {"n": 0}

        def flaky(text: str):
            calls["n"] += 1
            return (1.0, 0.0) if calls["n"] == 1 else (1.0, 0.0, 0.0)

        lib = SkillLibrary(embedder=flaky, clock=lambda: _T0)
        _register(lib)  # 2 维
        with pytest.raises(SkillLibraryError):
            lib.retrieve("查询")  # 3 维 → 维度不符

    def test_retrieve_deterministic_same_input(self) -> None:
        def build() -> list[str]:
            lib = _library()
            _register(lib, "动量均值")
            _register(lib, "动量突破")
            _register(lib, "均值突破")
            return [h.skill_id for h in lib.retrieve("动量动量突破", top_k=3)]

        assert build() == build()


# ──────────────────────────────────────────────────────────────────────────────
# 更新（版本递增 + 内容变更重算向量）
# ──────────────────────────────────────────────────────────────────────────────


class TestUpdateSkill:
    def test_update_content_version_increment_reembed(self) -> None:
        times = iter([_T0, _T1])
        lib = SkillLibrary(embedder=_embed, clock=lambda: next(times))
        entry = _register(lib, "动量")
        updated = lib.update_skill(entry.skill_id, content="均值均值")
        assert updated.version == 2
        assert updated.content == "均值均值"
        assert updated.embedding == (0.0, 2.0, 0.0)  # 重算向量
        assert updated.created_at == entry.created_at
        assert updated.updated_at == _T1  # 注入时钟
        assert lib.get(entry.skill_id).version == 2

    def test_update_metrics_only_keeps_embedding(self) -> None:
        lib = _library()
        entry = _register(lib, "动量")
        updated = lib.update_skill(
            entry.skill_id, success_metrics={"sharpe": 2.0, "win_rate": 0.6}
        )
        assert updated.version == 2
        assert updated.embedding == entry.embedding  # 内容未变不重算
        assert updated.success_metrics == {"sharpe": 2.0, "win_rate": 0.6}

    def test_update_invalid_rejected(self) -> None:
        lib = _library()
        entry = _register(lib)
        with pytest.raises(SkillLibraryError):
            lib.update_skill("skill-9999", content="动量")  # 未知技能
        with pytest.raises(SkillLibraryError):
            lib.update_skill(entry.skill_id)  # 无更新字段
        with pytest.raises(SkillLibraryError):
            lib.update_skill(entry.skill_id, content="")  # 空内容


# ──────────────────────────────────────────────────────────────────────────────
# 复用登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterReuse:
    def test_reuse_ok_and_count(self) -> None:
        lib = _library()
        entry = _register(lib)
        r1 = lib.register_reuse(
            entry.skill_id, task_description="新任务A", similarity=0.9
        )
        r2 = lib.register_reuse(
            entry.skill_id, task_description="新任务B", similarity=0.7
        )
        assert isinstance(r1, SkillReuseRecord)
        assert r1.record_id == "reuse-0001"
        assert r2.record_id == "reuse-0002"
        assert r1.reused_at == _T0
        assert lib.reuse_count(entry.skill_id) == 2
        assert len(lib.reuse_records(entry.skill_id)) == 2

    def test_reuse_invalid_rejected(self) -> None:
        lib = _library()
        entry = _register(lib)
        with pytest.raises(SkillLibraryError):
            lib.register_reuse("skill-9999", task_description="任务", similarity=0.5)
        for bad in (1.1, -1.1, float("nan"), "0.9"):
            with pytest.raises(SkillLibraryError):
                lib.register_reuse(
                    entry.skill_id, task_description="任务", similarity=bad
                )
        with pytest.raises(SkillLibraryError):
            lib.register_reuse(entry.skill_id, task_description="", similarity=0.5)


# ──────────────────────────────────────────────────────────────────────────────
# 查询（确定性排序）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_unknown_skill_fail_closed(self) -> None:
        lib = _library()
        with pytest.raises(SkillLibraryError):
            lib.get("skill-9999")
        with pytest.raises(SkillLibraryError):
            lib.reuse_records("skill-9999")
        with pytest.raises(SkillLibraryError):
            lib.reuse_count("skill-9999")

    def test_list_skills_sorted_and_filterable(self) -> None:
        lib = _library()
        _register(lib, "动量", kind=SkillKind.CODE_SNIPPET)
        _register(lib, "均值", kind=SkillKind.FACTOR_FORMULA)
        _register(lib, "突破", kind=SkillKind.CODE_SNIPPET)
        all_entries = lib.list_skills()
        assert [e.skill_id for e in all_entries] == [
            "skill-0001", "skill-0002", "skill-0003",
        ]
        code_only = lib.list_skills(kind=SkillKind.CODE_SNIPPET)
        assert [e.skill_id for e in code_only] == ["skill-0001", "skill-0003"]
        with pytest.raises(SkillLibraryError):
            lib.list_skills(kind="magic_recipe")
