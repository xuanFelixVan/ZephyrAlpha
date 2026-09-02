# [BLUEPRINT] MOD-INT-EPISODIC-MEM | docs/03_modules/_domain_intelligence/episodic_memory_store/blueprint.md | §test
# [A_test] module_id: MOD-INT-EPISODIC-MEM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# add-design-node tests/intelligence/test_episodic_memory_store.py MOD-INT-EPISODIC-MEM D_INTELLIGENCE planned --granularity file
"""EpisodicMemoryStore 单元测试 (MOD-INT-EPISODIC-MEM, MVP)。

覆盖: 轨迹 Schema 非法 Fail-Closed / 双写 sink 异常不阻断 / LRU 淘汰 /
Top-K 检索排序与访问时间刷新 / 归档（sink 缺失仅建议 / sink 正常删除）/
配置非法 Fail-Closed / forget 删除。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.episodic_memory_store import (
    EpisodicMemoryConfig,
    EpisodicMemoryStore,
    InvalidTrajectoryError,
    TrajectoryRecord,
)


def _rec(rid: str, created: float = 0.0) -> TrajectoryRecord:
    return TrajectoryRecord(
        record_id=rid,
        task_input="in",
        action="act",
        result="res",
        reflection="ref",
        created_at=created,
        last_accessed_at=created,
    )


class TestSchema:
    def test_ok(self) -> None:
        s = EpisodicMemoryStore()
        s.store(_rec("r1"))
        assert s.stats()["total"] == 1

    @pytest.mark.parametrize("field", ["task_input", "action", "result"])
    def test_fail_closed(self, field: str) -> None:
        base = {
            "record_id": "r1",
            "task_input": "i",
            "action": "a",
            "result": "r",
            "reflection": "x",
            "created_at": 0.0,
            "last_accessed_at": 0.0,
        }
        base[field] = ""
        with pytest.raises(InvalidTrajectoryError):
            EpisodicMemoryStore().store(TrajectoryRecord(**base))


class TestConfig:
    @pytest.mark.parametrize("bad", [{"max_entries": 0}, {"archive_after_days": 0}])
    def test_invalid(self, bad: dict) -> None:
        base = {"max_entries": 1000, "archive_after_days": 90}
        base.update(bad)
        with pytest.raises(Exception):
            EpisodicMemoryConfig(**base)


class TestStoreSinks:
    def test_hash_sink_error_not_blocking(self) -> None:
        def bad(rec: TrajectoryRecord) -> None:
            raise RuntimeError("boom")

        s = EpisodicMemoryStore(hash_sink=bad)
        s.store(_rec("r1"))
        assert s.stats()["total"] == 1

    def test_vector_sink_called(self) -> None:
        calls: list = []
        s = EpisodicMemoryStore(vector_sink=lambda rec, emb: calls.append(rec.record_id))
        s.store(_rec("r1"), embedding=[0.1, 0.2])
        assert calls == ["r1"]


class TestEviction:
    def test_lru(self) -> None:
        clock = [100.0]
        s = EpisodicMemoryStore(
            config=EpisodicMemoryConfig(max_entries=2, archive_after_days=90),
            clock=lambda: clock[0],
        )
        s.store(_rec("r1", created=100.0))
        s.store(_rec("r2", created=100.0))
        ev = s.store(_rec("r3", created=100.0))
        assert ev is not None
        assert len(ev.evicted_ids) == 1
        assert s.stats()["total"] == 2


class TestRetrieve:
    def test_topk_sorted(self) -> None:
        def fake_search(emb: list[float], k: int) -> list:
            return [
                (_rec("r1"), 0.5),
                (_rec("r2"), 0.9),
            ]

        s = EpisodicMemoryStore(search=fake_search)
        hits = s.retrieve_similar([0.1], 2)
        assert hits[0].record.record_id == "r2"

    def test_k_invalid(self) -> None:
        s = EpisodicMemoryStore()
        with pytest.raises(ValueError):
            s.retrieve_similar([0.1], 0)


class TestArchive:
    def test_no_sink_suggestion_only(self) -> None:
        clock = [10000000.0]
        s = EpisodicMemoryStore(
            config=EpisodicMemoryConfig(max_entries=1000, archive_after_days=1),
            clock=lambda: clock[0],
        )
        s.store(_rec("r1", created=1.0))
        ev = s.archive_expired()
        assert ev is not None
        assert "建议" in ev.reason
        assert s.stats()["total"] == 1

    def test_sink_archives(self) -> None:
        clock = [10000000.0]
        archived: list = []
        s = EpisodicMemoryStore(
            config=EpisodicMemoryConfig(max_entries=1000, archive_after_days=1),
            archive_sink=lambda rec: archived.append(rec.record_id),
            clock=lambda: clock[0],
        )
        s.store(_rec("r1", created=1.0))
        ev = s.archive_expired()
        assert archived == ["r1"]
        assert s.stats()["total"] == 0


class TestForget:
    def test_forget(self) -> None:
        s = EpisodicMemoryStore()
        s.store(_rec("r1"))
        assert s.forget("r1") is True
        assert s.forget("r1") is False
