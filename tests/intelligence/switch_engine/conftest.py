"""conftest — L6 switch_engine（S1-S4）测试夹具：tmp_path SQLite 注入，零生产写。"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)


def _make_store(tmp_path: Path) -> SwitchRegistryStore:
    """连接工厂注入 tmp_path 零生产写（测试隔离铁律）。"""

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
def isolated_store(tmp_path_factory: pytest.TempPathFactory) -> SwitchRegistryStore:
    return _make_store(tmp_path_factory.mktemp("switch_db"))


RecordFactory = Callable[..., SwitchRegistryRecord]


@pytest.fixture()
def make_record() -> RecordFactory:
    """SwitchRegistryRecord 工厂：默认 code_module/D_GOVERNANCE/shadow，kwargs 覆盖任意字段。"""

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
