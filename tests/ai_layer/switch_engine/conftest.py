"""conftest — L6 治理四件（S5-S8）测试夹具：tmp SQLite 注入+到态链路工厂，零生产写。"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from zephyr.intelligence.switch_engine.switch_engine import SwitchEngine
from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)


def _make_store(tmp_path: Path) -> SwitchRegistryStore:
    def factory() -> sqlite3.Connection:
        conn = sqlite3.connect(tmp_path / "governance_test.db")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    store = SwitchRegistryStore(conn_factory=factory)
    store.ensure_schema()
    return store


@pytest.fixture()
def store(tmp_path: Path) -> SwitchRegistryStore:
    return _make_store(tmp_path)


@pytest.fixture()
def engine(store: SwitchRegistryStore) -> SwitchEngine:
    return SwitchEngine(store)


RecordFactory = Callable[..., SwitchRegistryRecord]


@pytest.fixture()
def make_record() -> RecordFactory:
    def _factory(switch_id: str = "SW-20260923-demo", **overrides: Any) -> SwitchRegistryRecord:
        defaults: dict[str, Any] = {
            "switch_id": switch_id,
            "object_family": "code_module",
            "object_ref": "zephyr.demo.module",
            "domain": "D_GOVERNANCE",
            "champion_ref": "main",
            "challenger_ref": "session/st-demo",
            "criteria_yaml_ref": "config/switch_criteria.yaml",
            "criteria_hash": "0" * 64,
            "state": "shadow",
        }
        defaults.update(overrides)
        return SwitchRegistryRecord(**defaults)

    return _factory


@pytest.fixture()
def git_calls() -> list[list[str]]:
    return []


@pytest.fixture()
def fake_git(git_calls: list[list[str]]):
    """git 替身：记录调用零触真仓。"""

    def runner(args: Any) -> str:
        git_calls.append([str(a) for a in args])
        return ""

    return runner


@pytest.fixture()
def retired_switch(
    store: SwitchRegistryStore, engine: SwitchEngine, make_record: RecordFactory
) -> str:
    """走到 retired 的在册 switch（封存测试前置：champion 被下一代顶替退位）。"""
    switch_id = "SW-20260923-retired"
    engine.open_switch(make_record(switch_id))
    engine.transition(switch_id, "graduate", "green")
    engine.promote(switch_id, approved_by="owner_one_click", receipt_ref="r-1")
    engine.transition(switch_id, "stabilize", "stable-window")
    engine.transition(switch_id, "supersede", "next-gen-promoted")
    return switch_id
