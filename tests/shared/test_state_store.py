# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""JsonStateStore / AppendOnlyDedupSet 单元测试（#ARCH-QUANT-002 状态外部化原语 · 文件后端）。

覆盖：JSON 快照三分语义（无记录/正常/损坏）、原子写、append-only 去重集
重启存活、crash 残行容忍、非法输入拦截、工厂文件后端默认与拦截。

Redis 后端测试（接口契约双后端参数化同跑/fail-fast/无 TTL/键规约）见
tests/shared/test_state_store_redis.py（#ARCH-118 对称拆分）。
"""

from __future__ import annotations

import pytest

from zephyr.shared.state_store import (
    AppendOnlyDedupSet,
    JsonStateStore,
    StateCorruptError,
    StateStoreError,
    make_dedup_set,
    make_state_store,
)


class TestJsonStateStore:
    def test_load_absent_returns_none(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert store.load("kill_switch") is None

    def test_save_load_roundtrip(self, tmp_path):
        store = JsonStateStore(tmp_path)
        payload = {"active": True, "event_id": "evt-1", "reason": "dd>25%"}
        store.save("kill_switch", payload)
        assert store.load("kill_switch") == payload

    def test_save_overwrites(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"v": 1})
        store.save("ns", {"v": 2})
        assert store.load("ns") == {"v": 2}

    def test_load_corrupt_raises(self, tmp_path):
        store = JsonStateStore(tmp_path)
        (tmp_path / "kill_switch.json").write_bytes(b"{not-json!!")
        with pytest.raises(StateCorruptError):
            store.load("kill_switch")

    def test_load_non_dict_raises(self, tmp_path):
        store = JsonStateStore(tmp_path)
        (tmp_path / "ns.json").write_text("[1,2,3]", encoding="utf-8")
        with pytest.raises(StateCorruptError):
            store.load("ns")

    def test_delete(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"v": 1})
        assert store.delete("ns") is True
        assert store.load("ns") is None
        assert store.delete("ns") is False

    def test_namespace_path_traversal_rejected(self, tmp_path):
        store = JsonStateStore(tmp_path)
        with pytest.raises(StateStoreError):
            store.save("../evil", {"v": 1})
        with pytest.raises(StateStoreError):
            store.load("a/b")

    def test_unicode_content(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"reason": "回撤>25%熔断"})
        assert store.load("ns")["reason"] == "回撤>25%熔断"

    def test_no_tmp_residue_after_save(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"v": 1})
        leftovers = [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
        assert leftovers == []


class TestAppendOnlyDedupSet:
    def test_add_first_true_second_false(self, tmp_path):
        dedup = AppendOnlyDedupSet(tmp_path / "ids.txt")
        assert dedup.add("fill-1") is True
        assert dedup.add("fill-1") is False
        assert len(dedup) == 1

    def test_contains(self, tmp_path):
        dedup = AppendOnlyDedupSet(tmp_path / "ids.txt")
        dedup.add("fill-1")
        assert "fill-1" in dedup
        assert "fill-2" not in dedup

    def test_survives_restart(self, tmp_path):
        path = tmp_path / "ids.txt"
        AppendOnlyDedupSet(path).add("fill-1")
        # 模拟重启：新实例加载同一文件
        dedup2 = AppendOnlyDedupSet(path)
        assert "fill-1" in dedup2
        assert dedup2.add("fill-1") is False

    def test_partial_last_line_tolerated(self, tmp_path):
        """crash 残行（末行无换行）丢弃，该 ID 视为未见过（fail-safe 重判）。"""
        path = tmp_path / "ids.txt"
        path.write_bytes(b"fill-1\nfill-2\nfill-3-partia")
        dedup = AppendOnlyDedupSet(path)
        assert "fill-1" in dedup
        assert "fill-2" in dedup
        assert "fill-3-partia" not in dedup
        # 残行 ID 重新登记后可正常去重
        assert dedup.add("fill-3-partial") is True
        assert dedup.add("fill-3-partial") is False

    def test_blank_lines_ignored(self, tmp_path):
        path = tmp_path / "ids.txt"
        path.write_text("fill-1\n\n  \nfill-2\n", encoding="utf-8")
        dedup = AppendOnlyDedupSet(path)
        assert len(dedup) == 2

    def test_invalid_id_rejected(self, tmp_path):
        dedup = AppendOnlyDedupSet(tmp_path / "ids.txt")
        with pytest.raises(StateStoreError):
            dedup.add("")
        with pytest.raises(StateStoreError):
            dedup.add("has\nnewline")

    def test_persisted_as_lines(self, tmp_path):
        path = tmp_path / "ids.txt"
        dedup = AppendOnlyDedupSet(path)
        dedup.add("a")
        dedup.add("b")
        assert path.read_text(encoding="utf-8") == "a\nb\n"

    def test_unicode_id(self, tmp_path):
        path = tmp_path / "ids.txt"
        dedup = AppendOnlyDedupSet(path)
        dedup.add("成交-600000")
        dedup2 = AppendOnlyDedupSet(path)
        assert "成交-600000" in dedup2


class TestFactories:
    """消费方切换机制（验收③）：工厂选择后端，默认文件后端。"""

    def test_make_state_store_default_json(self, tmp_path):
        store = make_state_store(root_dir=tmp_path)
        assert isinstance(store, JsonStateStore)

    def test_make_state_store_json(self, tmp_path):
        store = make_state_store("json", root_dir=tmp_path)
        assert isinstance(store, JsonStateStore)

    def test_make_dedup_set_default_json(self, tmp_path):
        dedup = make_dedup_set(path=tmp_path / "ids.txt")
        assert isinstance(dedup, AppendOnlyDedupSet)

    def test_unknown_backend_rejected(self):
        with pytest.raises(StateStoreError):
            make_state_store("etcd", root_dir="/tmp/x")
        with pytest.raises(StateStoreError):
            make_dedup_set("etcd", path="/tmp/x")

    def test_missing_required_args_rejected(self):
        with pytest.raises(StateStoreError):
            make_state_store("json")  # 缺 root_dir
        with pytest.raises(StateStoreError):
            make_dedup_set("json")  # 缺 path
