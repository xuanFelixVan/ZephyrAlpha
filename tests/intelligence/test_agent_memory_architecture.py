# [BLUEPRINT] MOD-INT-AGENT-MEMORY | docs/03_modules/_domain_intelligence/agent_memory_architecture/blueprint.md | §test
# [A_test] module_id: MOD-INT-AGENT-MEMORY | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# add-design-node tests/intelligence/test_agent_memory_architecture.py MOD-INT-AGENT-MEMORY D_INTELLIGENCE planned --granularity file
"""AgentMemoryArchitecture 单元测试 (MOD-INT-AGENT-MEMORY, MVP)。

覆盖: 策略非法 Fail-Closed / encode 空内容/未知层 / store 层路由与
LRU/FIFO 淘汰 / backend 缺失 Fail-Closed / retrieve k 非正 / consolidate
方向非法与程序记忆人工源 / forget TTL 过期 / 程序记忆非人工源拒。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.agent_memory_architecture import (
    AgentMemoryArchitecture,
    InvalidMemoryPolicyError,
    MemoryBackendMissingError,
    MemoryItem,
    MemoryLayer,
    MemoryPolicy,
    PipelineStage,
)


def _policy(eviction: str = "lru", max_entries: int = 2, ttl: int = 10) -> MemoryPolicy:
    return MemoryPolicy(ttl_seconds=ttl, max_entries=max_entries, eviction=eviction)


def _make_arch(policies: dict | None = None, backends: dict | None = None) -> AgentMemoryArchitecture:
    return AgentMemoryArchitecture(
        policies=policies or {"working": _policy(), "episodic": _policy(), "semantic": _policy(), "procedural": _policy()},
        backends=backends or {layer: _FakeBackend() for layer in ("working", "episodic", "semantic", "procedural")},
    )


class _FakeBackend:
    def __init__(self) -> None:
        self.stored: list[MemoryItem] = []

    def store(self, item: MemoryItem) -> None:
        self.stored.append(item)

    def retrieve(self, query: str, k: int) -> list[MemoryItem]:
        return self.stored[:k]

    def delete(self, item_id: str) -> None:
        self.stored = [i for i in self.stored if i.item_id != item_id]


class TestMemoryPolicy:
    def test_ok(self) -> None:
        p = _policy()
        assert p.eviction == "lru"

    @pytest.mark.parametrize("bad", [
        {"ttl_seconds": 0},
        {"max_entries": 0},
        {"eviction": "bad"},
    ])
    def test_invalid(self, bad: dict) -> None:
        base = {"ttl_seconds": 10, "max_entries": 2, "eviction": "lru"}
        base.update(bad)
        with pytest.raises(InvalidMemoryPolicyError):
            MemoryPolicy(**base)


class TestEncode:
    def test_ok(self) -> None:
        arch = _make_arch()
        item = arch.encode("i1", "working", "content")
        assert item.layer == "working"

    def test_empty_content(self) -> None:
        arch = _make_arch()
        with pytest.raises(ValueError):
            arch.encode("i1", "working", "")

    def test_unknown_layer(self) -> None:
        arch = _make_arch()
        with pytest.raises(ValueError):
            arch.encode("i1", "bad", "c")


class TestStore:
    def test_ok(self) -> None:
        arch = _make_arch()
        item = arch.encode("i1", "working", "c")
        ev = arch.store(item)
        assert ev.layer == "working"
        assert len(ev.evicted_ids) == 0

    def test_backend_missing(self) -> None:
        arch = AgentMemoryArchitecture(policies={"working": _policy()}, backends={})
        item = arch.encode("i1", "working", "c")
        with pytest.raises(MemoryBackendMissingError):
            arch.store(item)

    def test_lru_eviction(self) -> None:
        arch = _make_arch(policies={"working": _policy(max_entries=2)})
        b = arch._backends["working"]
        arch.store(arch.encode("i1", "working", "c1"))
        arch.store(arch.encode("i2", "working", "c2"))
        ev = arch.store(arch.encode("i3", "working", "c3"))
        assert len(ev.evicted_ids) == 1
        assert "lru" in ev.reasons[0]

    def test_fifo_eviction(self) -> None:
        arch = _make_arch(policies={"working": _policy(eviction="fifo", max_entries=2)})
        arch.store(arch.encode("i1", "working", "c1"))
        arch.store(arch.encode("i2", "working", "c2"))
        ev = arch.store(arch.encode("i3", "working", "c3"))
        assert len(ev.evicted_ids) == 1
        assert "fifo" in ev.reasons[0]


class TestRetrieve:
    def test_ok(self) -> None:
        arch = _make_arch()
        b = arch._backends["working"]
        arch.store(arch.encode("i1", "working", "c1"))
        hits = arch.retrieve("q", "working", 1)
        assert len(hits) == 1

    def test_k_invalid(self) -> None:
        arch = _make_arch()
        with pytest.raises(ValueError):
            arch.retrieve("q", "working", 0)

    def test_backend_missing(self) -> None:
        arch = AgentMemoryArchitecture(policies={"working": _policy()}, backends={})
        with pytest.raises(MemoryBackendMissingError):
            arch.retrieve("q", "working", 1)


class TestConsolidate:
    def test_ok(self) -> None:
        arch = _make_arch()
        item = arch.encode("i1", "working", "c", {"source": "auto"})
        new = arch.consolidate(item, "working", "episodic")
        assert new.layer == "episodic"

    def test_reverse(self) -> None:
        arch = _make_arch()
        item = arch.encode("i1", "semantic", "c")
        with pytest.raises(ValueError):
            arch.consolidate(item, "semantic", "working")

    def test_procedural_manual(self) -> None:
        arch = _make_arch()
        item = arch.encode("i1", "working", "c", {"source": "manual"})
        new = arch.consolidate(item, "working", "procedural")
        assert new.layer == "procedural"

    def test_procedural_non_manual(self) -> None:
        arch = _make_arch()
        item = arch.encode("i1", "working", "c", {"source": "auto"})
        with pytest.raises(ValueError):
            arch.consolidate(item, "working", "procedural")


class TestForget:
    def test_ttl_expired(self) -> None:
        arch = _make_arch(policies={"working": _policy(ttl=1)})
        arch.store(arch.encode("i1", "working", "c1"))
        import time
        time.sleep(1.1)
        ev = arch.forget("working")
        assert len(ev.evicted_ids) == 1

    def test_no_expired(self) -> None:
        arch = _make_arch(policies={"working": _policy(ttl=9999)})
        arch.store(arch.encode("i1", "working", "c1"))
        ev = arch.forget("working")
        assert len(ev.evicted_ids) == 0
