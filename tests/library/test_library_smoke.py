# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
"""图书馆总账域冒烟测试（MOD-LIB-001..004 纯函数层，零 DB 依赖）。"""

from __future__ import annotations

import pytest

from zephyr.library.collectors.mcp_collector import _server_tools
from zephyr.library.librarian import Librarian
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


def test_ddl_ensure_assets_contains_potential_consumers() -> None:
    """增枝一致性（裁定#410②）：CREATE TABLE 与 upsert 列面必须同列——新库
    ensure 建表缺列会让首个 upsert 直接 undefined column。"""
    assert "potential_consumers text[] NOT NULL DEFAULT '{}'" in _SQL_ENSURE_ASSETS
    from zephyr.library.ledger_schema import _SQL_UPSERT_ASSET

    assert "potential_consumers" in _SQL_UPSERT_ASSET


def test_upsert_protects_potential_consumers_from_ingest_clobber() -> None:
    """回填保护（#410②批1 实测事故）：采集器全量再采集不携 potential_consumers，
    INSERT 缺省必须 COALESCE 到 '{}'、冲突路径 NULL=保留存量，否则人工回填被冲回空数组
    （实证：图书馆班回填 31 资产被 post-commit reconciler 再采集清零）。"""
    from zephyr.library.ledger_schema import _SQL_UPSERT_ASSET

    assert "COALESCE(%s::text[], '{}')" in _SQL_UPSERT_ASSET
    conflict_clause = _SQL_UPSERT_ASSET.split("ON CONFLICT", 1)[1]
    assert (
        "potential_consumers = COALESCE(EXCLUDED.potential_consumers, lib_assets.potential_consumers)"
        in conflict_clause
    )


def test_act_without_potential_consumers_passes_null() -> None:
    """act 字段缺省传 None（=SQL 层保留存量），禁 `or []` 把缺省变显式清空。"""

    class _RecordingCur:
        def __init__(self) -> None:
            self.calls: list[tuple] = []

        def __enter__(self) -> "_RecordingCur":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def execute(self, sql: object, *args: object) -> None:
            self.calls.append((sql, args))

        def fetchone(self) -> tuple:
            return (1,)

    class _RecordingConn:
        def __init__(self) -> None:
            self.cur = _RecordingCur()

        def cursor(self) -> _RecordingCur:
            return self.cur

        def commit(self) -> None:
            pass

    conn = _RecordingConn()
    lib = Librarian(conn)  # type: ignore[arg-type]
    lib.act("register", "MOD:x.py", actor="t", fields={"kind": "module", "home": "src/x.py"})
    upsert_params = conn.cur.calls[-1][1][0]
    assert upsert_params[10] is None  # potential_consumers 位次：缺省=None


def test_lookup_by_feeds_filters_and_respects_limit() -> None:
    """供数反查（裁定#410 步骤⑤）：数组包含匹配+大小写无关+limit 截断。"""

    class _StubCur:
        def __init__(self, rows: list[tuple]) -> None:
            self._rows = rows

        def __enter__(self) -> "_StubCur":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def execute(self, *args: object, **kwargs: object) -> None:
            pass

        def fetchall(self) -> list[tuple]:
            return self._rows

    class _StubConn:
        def __init__(self, rows: list[tuple]) -> None:
            self._rows = rows

        def cursor(self) -> _StubCur:
            return _StubCur(self._rows)

    rows = [
        ("MOD:src/a.py", "module", "src/a.py", "active", "甲", ["板块hot_money维", "BM-SEL-05"]),
        ("TBL:c1.dragon_tiger", "table", "c1_market.dragon_tiger", "active", "龙虎榜", ["游资温度成分"]),
        ("FILE:docs/b.md", "file", "docs/b.md", "archived", "乙", ["hot_money另维"]),
        ("MOD:src/c.py", "module", "src/c.py", "active", "丙", []),
    ]
    lib = Librarian(_StubConn(rows))  # type: ignore[arg-type]

    hits = lib.lookup_by_feeds("HOT_MONEY")
    assert [r["asset_id"] for r in hits] == ["MOD:src/a.py", "FILE:docs/b.md"]

    only_active = lib.lookup_by_feeds("游资温度")
    assert [r["asset_id"] for r in only_active] == ["TBL:c1.dragon_tiger"]

    assert lib.lookup_by_feeds("nomatch") == []
    assert lib.lookup_by_feeds("o", limit=1) == [hits[0]]


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


def test_fs_collector_keeps_real_models_packages_skips_vendored(tmp_path) -> None:
    """审计失明清单#6 红测：裸词 "models" 跳词吞掉 src/*/models 真包（26 处）。

    真包必须入册、vendored 产物（data/models）必须仍被显式前缀跳过。
    """
    from zephyr.library.collectors.fs_collector import collect

    real_pkg = tmp_path / "src/zephyr/some_dom/models/__init__.py"
    real_pkg.parent.mkdir(parents=True, exist_ok=True)
    real_pkg.write_text("# real models package\n", encoding="utf-8")
    vendored = tmp_path / "data/models/qwen25-7b/config.json"
    vendored.parent.mkdir(parents=True, exist_ok=True)
    vendored.write_text("{}", encoding="utf-8")

    homes = {a["home"] for a in collect(str(tmp_path))}
    assert "src/zephyr/some_dom/models/__init__.py" in homes, homes
    assert not any(h.startswith("data/models") for h in homes), homes
