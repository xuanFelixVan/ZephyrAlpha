# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
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
    tags 全被判"非枚举"（假红风暴），而合成词库的单测全绿看不见。
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


def test_fs_collector_family_dirs_are_not_itemized(tmp_path) -> None:
    """族级大盘目录只出 1 条族资产（st-ulib3c）：逐件入册=轮转删除即产 ghost 债。"""
    from zephyr.library.collectors.fs_collector import _FAMILY_DIRS, collect

    for rel in ("data/architecture_health/dash_20260923.json", "data/runtime_violation_snapshot/s.json"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}", encoding="utf-8")
    keep = tmp_path / "data/keep_me.json"
    keep.parent.mkdir(parents=True, exist_ok=True)
    keep.write_text("{}", encoding="utf-8")

    assets = collect(str(tmp_path))
    homes = {a["home"] for a in assets}
    assert "data/keep_me.json" in homes, homes  # 绝对路径父目录含跳词也不吞全树（旧缺陷面）
    fams = [a for a in assets if a["home"] in _FAMILY_DIRS]
    assert len(fams) == len(_FAMILY_DIRS)
    assert all(a["fingerprint_aux"].get("family") for a in fams)
    assert not [h for h in homes if h.startswith(tuple(f"{d}/" for d in _FAMILY_DIRS))]


def test_logs_collector_emits_unique_ids_for_placeholder_paths() -> None:
    """日志抽屉 98 条必须出 98 唯一索书号（st-ulib3c）：占位 path 不得塌缩同 id。"""
    from zephyr.library.collectors.logs_collector import collect

    assets = [a for a in collect(".") if "error" not in a]
    ids = [a["asset_id"] for a in assets]
    assert len(ids) == len(set(ids)), f"抽屉 asset_id 塌缩：{len(ids)} 条只出 {len(set(ids))} 号"
    registry_homes = [a["home"] for a in assets if "#" in a["home"]]
    assert registry_homes, "占位 path 抽屉应改以 registry_of_logs#log_id 定位"
