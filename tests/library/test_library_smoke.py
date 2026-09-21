"""图书馆总账域冒烟测试（MOD-LIB-001..004 纯函数层，零 DB 依赖）。"""

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.commit_gates.library_coverage_gate import _has_call_number
from zephyr.library.collectors.mcp_collector import _server_tools
from zephyr.library.ledger_schema import (
    _SQL_ENSURE_ASSETS,
    _SQL_ENSURE_EVENTS,
    ACTIONS,
    derive_asset_id,
    validate_action,
)


def test_derive_asset_id_deterministic_and_normalized() -> None:
    """索书号派生：确定性+反斜杠归一。"""
    first = derive_asset_id("file", "docs\\library\\INDEX.md")
    second = derive_asset_id("file", "docs/library/INDEX.md")
    assert first == second == "FILE:docs/library/INDEX.md"


def test_derive_asset_id_rejects_bad_kind_and_empty_home() -> None:
    """非法 kind/空 home 必须拒绝。"""
    with pytest.raises(ValueError):
        derive_asset_id("alien", "x")
    with pytest.raises(ValueError):
        derive_asset_id("file", "")


def test_validate_action_delete_requires_authority() -> None:
    """注销权：delete 无预授权必须拒绝（08 §3.1 死亡证明）。"""
    validate_action("register", None)
    with pytest.raises(ValueError):
        validate_action("delete", None)
    validate_action("delete", "裁定#NNN")


def test_actions_frozen_set() -> None:
    """六动作+死亡证明授权语义不被误改。"""
    assert frozenset({"register", "read", "update", "move", "delete", "audit"}) == ACTIONS


def test_ddl_contains_core_tables() -> None:
    """总账两表 DDL 存在且含核心列。"""
    assert "lib_assets" in _SQL_ENSURE_ASSETS
    assert "asset_id text PRIMARY KEY" in _SQL_ENSURE_ASSETS
    assert "lib_events" in _SQL_ENSURE_EVENTS


def test_call_number_detector() -> None:
    """索书号探测器：frontmatter 键与 # asset: 注释两种形态。"""
    assert _has_call_number("x\nasset_id: FILE:a.md\n")
    assert _has_call_number("# asset: MOD:src/x.py\n")
    assert not _has_call_number("no id here\n")


def test_mcp_tool_counter() -> None:
    """MCP 契约 tool 计数器基本形态。"""
    assert _server_tools({"gateway_server": {"t1": {}, "t2": {}}}) == {"gateway_server": 2}
    assert _server_tools({}) == {}
