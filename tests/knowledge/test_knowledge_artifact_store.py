# [BLUEPRINT] MOD-KNW-004 | docs/03_modules/_domain_knowledge/knowledge_artifact_store/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_knowledge_artifact_store
# [TESTS] src/zephyr/knowledge/knowledge_artifact_store.py
"""MOD-KNW-004 单元测试：knowledge_artifact_store 知识工件库。

蓝图验收（B12-03637/CAND-KNW-008，B12）：
6类产出词表闭合不可变schema + 同artifact_id版本链（写不可改,改即新版本）+
6维索引（来源/作者/类型/目标层级/时间/效果）查询。时钟注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.knowledge_artifact_store",
    reason="knowledge_artifact_store not importable",
)

from zephyr.knowledge.knowledge_artifact_store import (  # noqa: E402
    ArtifactStoreError,
    ArtifactType,
    KnowledgeArtifactStore,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 30, 0)


class _Clock:
    """可推进内存时钟（DI）。"""

    def __init__(self) -> None:
        self.now = _T0

    def __call__(self) -> datetime.datetime:
        return self.now


def _store(clock: _Clock | None = None) -> KnowledgeArtifactStore:
    return KnowledgeArtifactStore(clock=clock or _Clock())


def _put(store: KnowledgeArtifactStore, artifact_id: str = "art-1", **kwargs):
    params = dict(
        source="research_bot",
        author="agent-a",
        target_layer="L2",
        effect="positive",
        payload={"content": "原始语料"},
    )
    params.update(kwargs)
    return store.put(artifact_id, ArtifactType.RAW_KNOWLEDGE_PACKET, **params)


# ──────────────────────────────────────────────────────────────────────────────
# schema / 写入校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestPut:
    def test_put_ok_version_one(self) -> None:
        store = _store()
        artifact = _put(store)
        assert artifact.version == 1
        assert artifact.created_at == _T0
        assert artifact.payload == {"content": "原始语料"}

    def test_six_types_schemas(self) -> None:
        store = _store()
        store.put(
            "a1",
            ArtifactType.RAW_KNOWLEDGE_PACKET,
            source="s",
            author="a",
            target_layer="L1",
            effect="e",
            payload={"content": "x"},
        )
        store.put(
            "a2",
            ArtifactType.STRUCTURED_KNOWLEDGE_FRAGMENT,
            source="s",
            author="a",
            target_layer="L1",
            effect="e",
            payload={"fragment": "x"},
        )
        store.put(
            "a3",
            ArtifactType.CLASSIFIED_KNOWLEDGE_PACKAGE,
            source="s",
            author="a",
            target_layer="L1",
            effect="e",
            payload={"category": "c", "fragments": []},
        )
        store.put(
            "a4",
            ArtifactType.MODULE_MAPPING_RESULT,
            source="s",
            author="a",
            target_layer="L1",
            effect="e",
            payload={"mapping": {}},
        )
        store.put(
            "a5",
            ArtifactType.NEW_MODULE,
            source="s",
            author="a",
            target_layer="L1",
            effect="e",
            payload={"module_id": "m", "blueprint": "b"},
        )
        store.put(
            "a6",
            ArtifactType.TRIAL_RESULT,
            source="s",
            author="a",
            target_layer="L1",
            effect="e",
            payload={"metrics": {}},
        )
        assert len(store.query()) == 6

    def test_bad_type_raises(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            store.put(
                "a1",
                "GhostType",
                source="s",
                author="a",  # type: ignore[arg-type]
                target_layer="L1",
                effect="e",
                payload={"content": "x"},
            )

    def test_schema_missing_key_raises(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            store.put(
                "a1",
                ArtifactType.NEW_MODULE,
                source="s",
                author="a",
                target_layer="L1",
                effect="e",
                payload={"module_id": "m"},
            )

    def test_schema_extra_key_raises(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            _put(store, payload={"content": "x", "hack": "y"})

    def test_blank_fields_raise(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            _put(store, artifact_id="")
        with pytest.raises(ArtifactStoreError):
            _put(store, source="")
        with pytest.raises(ArtifactStoreError):
            _put(store, author="")
        with pytest.raises(ArtifactStoreError):
            _put(store, target_layer="")
        with pytest.raises(ArtifactStoreError):
            _put(store, effect="")


# ──────────────────────────────────────────────────────────────────────────────
# 版本链（写不可改，改即新版本）
# ──────────────────────────────────────────────────────────────────────────────


class TestVersionChain:
    def test_same_id_appends_version(self) -> None:
        store = _store()
        _put(store)
        v2 = _put(store, payload={"content": "修订语料"})
        assert v2.version == 2
        history = store.history("art-1")
        assert [a.version for a in history] == [1, 2]
        assert history[0].payload == {"content": "原始语料"}  # 旧版本不可改

    def test_get_latest_and_specific(self) -> None:
        store = _store()
        _put(store)
        _put(store, payload={"content": "修订语料"})
        assert store.get("art-1").version == 2  # 缺省最新
        assert store.get("art-1", 1).payload == {"content": "原始语料"}

    def test_get_unknown_raises(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            store.get("ghost")
        with pytest.raises(ArtifactStoreError):
            store.history("ghost")

    def test_get_unknown_version_raises(self) -> None:
        store = _store()
        _put(store)
        with pytest.raises(ArtifactStoreError):
            store.get("art-1", 9)
        with pytest.raises(ArtifactStoreError):
            store.get("art-1", 0)

    def test_no_update_or_delete_api(self) -> None:
        store = _store()
        assert not hasattr(store, "update")
        assert not hasattr(store, "delete")
        assert not hasattr(store, "remove")


# ──────────────────────────────────────────────────────────────────────────────
# 6 维索引查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def _seed(self, store: KnowledgeArtifactStore, clock: _Clock) -> None:
        _put(store, "art-1")
        clock.now = _T1
        _put(store, "art-2", source="human", author="agent-b", effect="negative", target_layer="L3")
        store.put(
            "art-3",
            ArtifactType.TRIAL_RESULT,
            source="research_bot",
            author="agent-a",
            target_layer="L2",
            effect="neutral",
            payload={"metrics": {"ic": 0.05}},
        )

    def test_query_by_source(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        hits = store.query(source="human")
        assert [a.artifact_id for a in hits] == ["art-2"]

    def test_query_by_author(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        assert {a.artifact_id for a in store.query(author="agent-a")} == {"art-1", "art-3"}

    def test_query_by_type(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        hits = store.query(artifact_type=ArtifactType.TRIAL_RESULT)
        assert [a.artifact_id for a in hits] == ["art-3"]

    def test_query_by_target_layer_and_effect(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        assert {a.artifact_id for a in store.query(target_layer="L2")} == {"art-1", "art-3"}
        assert [a.artifact_id for a in store.query(effect="neutral")] == ["art-3"]

    def test_query_by_time_range(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        assert [a.artifact_id for a in store.query(created_to=_T0)] == ["art-1"]
        assert {a.artifact_id for a in store.query(created_from=_T1)} == {"art-2", "art-3"}
        assert len(store.query(created_from=_T0, created_to=_T1)) == 3

    def test_query_multi_dim_intersection(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        hits = store.query(source="research_bot", effect="neutral", target_layer="L2")
        assert [a.artifact_id for a in hits] == ["art-3"]

    def test_query_no_match_returns_empty(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        assert store.query(source="ghost") == []

    def test_query_bad_time_window_raises(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            store.query(created_from=_T1, created_to=_T0)

    def test_query_bad_type_raises(self) -> None:
        store = _store()
        with pytest.raises(ArtifactStoreError):
            store.query(artifact_type="ghost")  # type: ignore[arg-type]

    def test_query_deterministic_order(self) -> None:
        clock = _Clock()
        store = _store(clock)
        self._seed(store, clock)
        _put(store, "art-1")  # art-1 v2
        hits = store.query()
        assert [(a.artifact_id, a.version) for a in hits] == [
            ("art-1", 1),
            ("art-1", 2),
            ("art-2", 1),
            ("art-3", 1),
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        def _run() -> list:
            clock = _Clock()
            store = _store(clock)
            _put(store, "art-1")
            _put(store, "art-1", payload={"content": "二版"})
            _put(store, "art-2", source="human")
            return [
                [(a.artifact_id, a.version, a.created_at.isoformat()) for a in store.query()],
                [a.payload["content"] for a in store.history("art-1")],
                [a.artifact_id for a in store.query(source="human")],
            ]

        assert _run() == _run()
