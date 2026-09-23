"""图书馆总账域冒烟测试（MOD-LIB-001..004 纯函数层，零 DB 依赖）。"""

from __future__ import annotations

import pytest

from zephyr.library.collectors.mcp_collector import _server_tools
from zephyr.library.ledger_schema import (
    _SQL_ENSURE_ASSETS,
    _SQL_ENSURE_EVENTS,
    ACTIONS,
    _has_call_number,
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


def test_real_tag_vocabulary_loads_strict() -> None:
    """真词库自检（st-ulib3c 红证）：TAG-VOCAB 闸对真词库 strict 必须加载成功。

    别名冲突会让闸内 `_load_vocab` 退化为空词库——生产实测后果是 catalogs 每笔
    tags 全被判“非枚举”（假红风暴），而合成词库的单测全绿看不见。
    """
    from pathlib import Path

    from zephyr.shared.io.yaml_utils import load_vocabulary_alias_map

    root = Path(__file__).resolve().parents[2]
    vocab = root / "docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml"
    canonical, alias_map = load_vocabulary_alias_map(vocab, strict=True)
    assert canonical and alias_map
    # 物理真源：market_kline_daily.turnover 注释=换手率(%)，成交额列名=amount
    assert alias_map["turnover"] == "换手"
    assert "turnover" not in canonical


def test_fs_collector_skips_rotating_snapshot_dirs(tmp_path) -> None:
    """轮转快照目录不入册（st-ulib3c 红证）：盘上会滚动删除，入册即产 ghost 债。"""
    from zephyr.library.collectors.fs_collector import collect

    for rel in (
        "data/architecture_health/dashboard_20260923T000000Z.json",
        "data/runtime_violation_snapshot/v_20260923T000000Z.json",
    ):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}", encoding="utf-8")
    keep = tmp_path / "data/keep_me.json"
    keep.parent.mkdir(parents=True, exist_ok=True)
    keep.write_text("{}", encoding="utf-8")

    homes = {a["home"] for a in collect(str(tmp_path))}
    assert any(h.endswith("data/keep_me.json") for h in homes), homes
    assert not [h for h in homes if "architecture_health" in h or "runtime_violation_snapshot" in h]
