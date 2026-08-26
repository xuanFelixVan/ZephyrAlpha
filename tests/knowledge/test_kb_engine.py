# [BLUEPRINT] MOD-KNW-001 | docs/03_modules/_domain_knowledge/kb_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_kb_engine
# [TESTS] src/zephyr/knowledge/kb_engine.py
"""MOD-KNW-001 单元测试：kb_engine 统一知识库引擎。

蓝图验收（B1-00128/CAND-KNW-002，C2 D-KNOW-06）：
八Collection通用CRUD（词表注入校验）+ 版本递增+历史留存 + 按版本回滚 +
FTS5全文搜索（真:memory: sqlite）+ 变更审计回调。连接/时钟/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.knowledge.kb_engine",
    reason="kb_engine not importable",
)

from zephyr.knowledge.kb_engine import (  # noqa: E402
    AuditAction,
    KbAuditRecord,
    KbEngine,
    KbEngineError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_COLLECTIONS = ("alpha", "beta")


def _engine(audits: list | None = None) -> KbEngine:
    return KbEngine(
        conn=sqlite3.connect(":memory:"),
        collections=_COLLECTIONS,
        clock=lambda: _T0,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造 / 词表校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        engine = _engine()
        assert engine.list_entries("alpha") == []

    def test_default_vocab_eight_collections(self) -> None:
        engine = KbEngine(conn=sqlite3.connect(":memory:"), clock=lambda: _T0)
        engine.create("knowledge", "e1", "默认词表可用")
        assert engine.get("knowledge", "e1").version == 1

    def test_conn_missing_raises(self) -> None:
        with pytest.raises(KbEngineError):
            KbEngine(conn=None, collections=_COLLECTIONS)  # type: ignore[arg-type]

    def test_empty_vocab_raises(self) -> None:
        with pytest.raises(KbEngineError):
            KbEngine(conn=sqlite3.connect(":memory:"), collections=())

    def test_duplicate_vocab_raises(self) -> None:
        with pytest.raises(KbEngineError):
            KbEngine(conn=sqlite3.connect(":memory:"), collections=("a", "a"))

    def test_blank_vocab_name_raises(self) -> None:
        with pytest.raises(KbEngineError):
            KbEngine(conn=sqlite3.connect(":memory:"), collections=("a", ""))


# ──────────────────────────────────────────────────────────────────────────────
# CRUD + 版本 + 历史
# ──────────────────────────────────────────────────────────────────────────────


class TestCrud:
    def test_create_and_get(self) -> None:
        engine = _engine()
        entry = engine.create("alpha", "e1", "动量因子定义", metadata={"src": "unit"})
        assert entry.version == 1
        assert entry.updated_at == _T0
        assert engine.get("alpha", "e1").content == "动量因子定义"

    def test_create_unknown_collection_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.create("ghost", "e1", "x")

    def test_create_duplicate_raises(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "x")
        with pytest.raises(KbEngineError):
            engine.create("alpha", "e1", "y")

    def test_create_blank_entry_id_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.create("alpha", "", "x")

    def test_update_increments_version_keeps_history(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "v1内容")
        e2 = engine.update("alpha", "e1", "v2内容", metadata={"rev": 2})
        assert e2.version == 2
        history = engine.history("alpha", "e1")
        assert [h.version for h in history] == [1, 2]
        assert history[0].content == "v1内容"  # 历史留存
        assert engine.get("alpha", "e1").content == "v2内容"

    def test_update_unknown_entry_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.update("alpha", "ghost", "x")

    def test_delete_marks_and_hides(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "x")
        engine.delete("alpha", "e1")
        with pytest.raises(KbEngineError):
            engine.get("alpha", "e1")
        history = engine.history("alpha", "e1")
        assert history[-1].deleted is True  # 历史留存

    def test_delete_unknown_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.delete("alpha", "ghost")

    def test_get_unknown_collection_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.get("ghost", "e1")

    def test_list_entries_sorted_excludes_deleted(self) -> None:
        engine = _engine()
        engine.create("alpha", "b", "x")
        engine.create("alpha", "a", "x")
        engine.create("alpha", "c", "x")
        engine.delete("alpha", "c")
        assert [e.entry_id for e in engine.list_entries("alpha")] == ["a", "b"]


# ──────────────────────────────────────────────────────────────────────────────
# 回滚
# ──────────────────────────────────────────────────────────────────────────────


class TestRollback:
    def test_rollback_appends_new_version(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "原始内容")
        engine.update("alpha", "e1", "改坏的内容")
        rolled = engine.rollback("alpha", "e1", 1)
        assert rolled.version == 3  # 回滚=追加新版本
        assert rolled.content == "原始内容"
        assert engine.get("alpha", "e1").content == "原始内容"
        assert len(engine.history("alpha", "e1")) == 3

    def test_rollback_unknown_version_raises(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "x")
        with pytest.raises(KbEngineError):
            engine.rollback("alpha", "e1", 9)
        with pytest.raises(KbEngineError):
            engine.rollback("alpha", "e1", 0)

    def test_rollback_unknown_entry_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.rollback("alpha", "ghost", 1)


# ──────────────────────────────────────────────────────────────────────────────
# FTS5 搜索
# ──────────────────────────────────────────────────────────────────────────────


class TestSearch:
    def test_search_hit(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "动量 因子 夏普比率 回测")
        engine.create("alpha", "e2", "基本面 财报 营收")
        hits = engine.search("动量")
        assert [h.entry_id for h in hits] == ["e1"]

    def test_search_scoped_collection(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "回撤 控制")
        engine.create("beta", "e2", "回撤 控制")
        hits = engine.search("回撤", collection="beta")
        assert [(h.collection, h.entry_id) for h in hits] == [("beta", "e2")]

    def test_search_reflects_update(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "旧关键词 甲")
        engine.update("alpha", "e1", "新关键词 乙")
        assert engine.search("旧关键词") == []
        assert [h.entry_id for h in engine.search("新关键词")] == ["e1"]

    def test_search_excludes_deleted(self) -> None:
        engine = _engine()
        engine.create("alpha", "e1", "将被删除的词")
        engine.delete("alpha", "e1")
        assert engine.search("删除") == []

    def test_search_blank_query_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.search("  ")

    def test_search_unknown_collection_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.search("x", collection="ghost")

    def test_search_bad_limit_raises(self) -> None:
        engine = _engine()
        with pytest.raises(KbEngineError):
            engine.search("x", limit=0)


# ──────────────────────────────────────────────────────────────────────────────
# 审计 + 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestAuditAndDeterminism:
    def test_audit_trail(self) -> None:
        audits: list[KbAuditRecord] = []
        engine = _engine(audits)
        engine.create("alpha", "e1", "v1")
        engine.update("alpha", "e1", "v2")
        engine.rollback("alpha", "e1", 1)
        engine.delete("alpha", "e1")
        assert [(a.action, a.version) for a in audits] == [
            (AuditAction.CREATE, 1),
            (AuditAction.UPDATE, 2),
            (AuditAction.ROLLBACK, 3),
            (AuditAction.DELETE, 4),
        ]
        assert all(a.at == _T0 for a in audits)

    def test_determinism_same_input_same_output(self) -> None:
        def _run() -> list:
            engine = _engine()
            engine.create("alpha", "e1", "确定性 校验 内容")
            engine.update("alpha", "e1", "确定性 校验 第二版")
            engine.rollback("alpha", "e1", 1)
            hits = [(h.collection, h.entry_id, h.version, h.content) for h in engine.search("确定性")]
            hist = [(h.version, h.content, h.deleted) for h in engine.history("alpha", "e1")]
            return hits + hist

        assert _run() == _run()
