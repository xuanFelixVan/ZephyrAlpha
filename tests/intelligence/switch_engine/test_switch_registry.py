"""S1 switch_registry 验收测试：schema 幂等/CRUD/七态校验/互斥生效/history 只追加。

零生产写：连接工厂注入 tmp_path（tests/intelligence/switch_engine/conftest.py）。
"""

from __future__ import annotations

import sqlite3

import pytest

from zephyr.intelligence.switch_engine.switch_registry import (
    SEVEN_STATES,
    SwitchRegistryRecord,
    SwitchRegistryStore,
    ensure_schema,
)


def test_schema_idempotent(store: SwitchRegistryStore) -> None:
    ensure_schema(store.connection())  # 二次建表不炸
    names = {
        row[0]
        for row in store.connection().execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert "switch_registry" in names


def test_create_get_roundtrip(
    store: SwitchRegistryStore, make_record
) -> None:
    record = make_record(observation={"start": "2026-09-01", "min_months": 1})
    store.create(record)
    loaded = store.require("SW-20260923-demo")
    assert isinstance(loaded, SwitchRegistryRecord)
    assert loaded.state == "shadow"
    assert loaded.observation["min_months"] == 1
    assert loaded.champion_ref == "main"
    assert loaded.created_at.endswith("+00:00")  # 显式时区（RULE-SCHEMA-TZ 精神）
    assert loaded.updated_at.endswith("+00:00")


def test_invalid_state_rejected(store: SwitchRegistryStore, make_record) -> None:
    with pytest.raises(ValueError, match="非法 state"):
        store.create(make_record(state="fifth_state"))
    assert {
        "shadow", "canary", "promoted", "champion", "retired", "tombstone", "aborted",
    } == SEVEN_STATES


def test_invalid_family_rejected(store: SwitchRegistryStore, make_record) -> None:
    with pytest.raises(ValueError, match="非法 object_family"):
        store.create(make_record(object_family="pokemon"))


def test_mutual_exclusion_two_versions_same_object(
    store: SwitchRegistryStore, make_record
) -> None:
    """验收锚 S1：两版本同登记互斥生效——同对象仅一行活跃 switch。"""
    store.create(make_record("SW-1"))
    with pytest.raises(RuntimeError, match="互斥生效"):
        store.create(make_record("SW-2"))  # 同 family+ref 第二活跃行被拒


def test_tombstone_releases_exclusivity(store: SwitchRegistryStore, make_record) -> None:
    store.create(make_record("SW-1"))
    store.update_state("SW-1", "tombstone", "seal:test")
    store.create(make_record("SW-2", champion_ref="v2", challenger_ref="v3"))  # 坑已让位
    assert store.require("SW-2").state == "shadow"


def test_state_history_append_only(store: SwitchRegistryStore, make_record) -> None:
    store.create(make_record("SW-1"))
    store.update_state("SW-1", "canary", "graduate:e1")
    store.update_state("SW-1", "promoted", "promote:e2")
    record = store.require("SW-1")
    assert [entry["state"] for entry in record.state_history] == [
        "shadow", "canary", "promoted",
    ]
    assert all(entry["evidence_ref"] for entry in record.state_history)


def test_update_state_requires_evidence(store: SwitchRegistryStore, make_record) -> None:
    store.create(make_record("SW-1"))
    with pytest.raises(ValueError, match="evidence_ref"):
        store.update_state("SW-1", "canary", "")


def test_require_missing_raises(store: SwitchRegistryStore) -> None:
    with pytest.raises(KeyError):
        store.require("SW-404")


def test_list_by_state_filters_and_validates(
    store: SwitchRegistryStore, make_record
) -> None:
    store.create(make_record("SW-1"))
    store.create(make_record("SW-2", object_ref="zephyr.demo.other"))
    assert len(store.list_by_state("shadow")) == 2
    assert store.list_by_state("champion") == []
    with pytest.raises(ValueError):
        store.list_by_state("nope")


def test_injected_factory_isolated(
    isolated_store: SwitchRegistryStore, store: SwitchRegistryStore, make_record
) -> None:
    """两个独立注入库互不可见（隔离证明，零生产路径写）。"""
    store.create(make_record("SW-A"))
    assert isolated_store.get("SW-A") is None
    assert isinstance(store.connection(), sqlite3.Connection)
