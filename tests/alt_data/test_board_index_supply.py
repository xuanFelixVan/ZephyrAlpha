# [BLUEPRINT] MOD-ALT-BOARD-INDEX-SUPPLY | docs/_working/t0_matrix/BOARD_INDEX_INTRADAY_SUPPLY_DESIGN.md | §4
# [MODULE] tests.alt_data.test_board_index_supply
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] stdlib; pytest; zephyr.alt_data.board_index_supply; yaml
# [CONSUMERS] none (测试)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 零 CH/零生产写路径：reader/表名解析全 fake 注入，断言契约列/FINAL 读纪律/
#              vendor 兜底语义（自算缺位才启用）/PIT snapshot_date<=day 零前视/注册表登记项在册。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；不触网不落库。
# [TESTS] tests/alt_data/test_board_index_supply.py
# [A_module] module_id=MOD-TEST-BOARD-IDX-SUPPLY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""board_index_supply 单元测试（fake reader + fake 表名解析注入，同构 emotion_index 测试口径）。

覆盖（设计验收 §4 的可离线子集，CH 依赖项另列延后核验清单）：
注册登记（CTR-P1-018 三消费者+summary 计数）、契约列、FINAL 读纪律、vendor 对账兜底
（自算缺位才启用、source=vendor 标记、禁跨源拼接）、PIT 成分零前视、品类未注册 fail-closed。
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
import yaml

import zephyr.alt_data.board_index_supply as bis

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT_ID = "CTR-P1-018"

# 表名解析 fake：品类 ID→fake 全限定表名（与 FakeReader 路由键对应）。
_FAKE_TABLES = {
    bis.CATEGORY_L1_BOARD_MINUTE: "c1_market.board_index_1min_fake",
    bis.CATEGORY_VENDOR_BOARD_TICK: "c1_market.board_index_tick_fake",
    bis.CATEGORY_SECTOR_CONSTITUTENT: "c1_market.sector_constituent_snapshot_fake",
}


def _fake_resolver(category_id: str) -> str:
    return _FAKE_TABLES[category_id]


class FakeReader:
    """按 SQL 子串路由返回预制 TSV（同 cohort/emotion fake reader 口径，记录调用）。"""

    def __init__(self, routes: dict[str, str]):
        self.routes = routes
        self.calls: list[str] = []

    def query(self, sql: str) -> str:
        self.calls.append(sql)
        for key, tsv in self.routes.items():
            if key in sql:
                return tsv
        return ""


_SELF_TSV = (
    "BK.demo\t2026-09-26 09:31:00\t1050.5\t35\t15\t0.7\t1.2e8\t50\tself_comp_v1\t2026-09-26 15:01:00\n"
    "BK.demo\t2026-09-26 09:32:00\t1051.0\t38\t12\t0.76\t1.3e8\t50\tself_comp_v1\t2026-09-26 15:01:00\n"
)
_VENDOR_TSV = "BK.demo\t2026-09-26 09:31:00\t1049.9\nBK.demo\t2026-09-26 09:32:00\t1050.4\n"
_CONSTIT_TSV = "600000\n000001\n300750\n"


def _register() -> dict:
    with open(_REPO / "architecture_model/contracts/consumer_registry.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_registration_entries_in_registry():
    """CTR-P1-018 登记在册：做T 6.1/6.2 + emotion_index C1/C2 三消费者。"""
    data = _register()
    contract = next(c for c in data["consumers"] if c["contract_id"] == _CONTRACT_ID)
    assert contract["contract_name"] == "BoardIndexIntradaySupply"
    entries = contract["registered_consumers"]
    assert len(entries) == 3
    modules = " | ".join(e["module"] for e in entries)
    assert "6.1" in modules and "6.2" in modules and "emotion_index_builder" in modules
    assert all(e["domain"] in ("D_BACKTEST", "D_ALT_DATA") for e in entries)


def test_registration_summary_counts_consistent():
    """summary 三类聚合计数与实际一致（机栅 validate_yaml_summaries 同口径）。"""
    data = _register()
    entries = [e for c in data["consumers"] for e in c["registered_consumers"]]
    s = data["summary"]
    assert s["total_contracts_registered"] == len(data["consumers"])
    assert s["total_consumer_entries"] == len(entries)
    t1 = sum(1 for e in entries if e.get("tier") == 1)
    assert s["tier_distribution"]["tier_1_critical"] == t1
    assert s["tier_distribution"]["tier_2_secondary"] == len(entries) - t1


def test_self_comp_primary_returns_contract_columns():
    """自算主力层：契约列逐一对应、source=self_comp、FINAL 读纪律、不触发 vendor 路由。"""
    reader = FakeReader({"board_index_1min_fake": _SELF_TSV, "board_index_tick_fake": _VENDOR_TSV})
    got = bis.get_board_index_minute(reader, "BK.demo", "2026-09-26 09:30:00", "2026-09-26 15:00:00", _fake_resolver)
    assert not got.fallback_engaged
    assert got.source == bis.SOURCE_SELF_COMP
    assert list(got.df.columns) == bis.BOARD_INDEX_CONTRACT_COLUMNS
    assert len(got.df) == 2
    self_sql = [c for c in reader.calls if "board_index_1min_fake" in c]
    assert self_sql and all(" FINAL " in c for c in self_sql)
    assert not any("board_index_tick_fake" in c for c in reader.calls)  # 禁跨源拼接：厂商未参与


def test_vendor_fallback_engages_when_self_comp_absent():
    """兜底语义：自算缺位→vendor 对账兜底启用，source=vendor+原因位，禁静默混源。"""
    reader = FakeReader({"board_index_tick_fake": _VENDOR_TSV})  # L1 路由缺→空表
    got = bis.get_board_index_minute(reader, "BK.demo", "2026-09-26 09:30:00", "2026-09-26 15:00:00", _fake_resolver)
    assert got.fallback_engaged
    assert got.source == bis.SOURCE_VENDOR
    assert got.reason and "兜底" in got.reason
    assert list(got.df.columns) == ["board_code", "ts", "close"]
    assert len(got.df) == 2


def test_both_absent_degrades_empty_without_raise():
    """双源皆缺（断流可活 §4.4）：空表降级不抛错，reason 记录断流语义。"""
    reader = FakeReader({})
    got = bis.get_board_index_minute(reader, "BK.demo", "2026-09-26 09:30:00", "2026-09-26 15:00:00", _fake_resolver)
    assert got.df.empty and got.fallback_engaged and got.source == bis.SOURCE_VENDOR
    assert any("断流" in w for w in got.warnings)


def test_pit_constituents_zero_lookahead():
    """PIT 成分：SQL 带 snapshot_date<=day 上界与最新快照子查询，返回 ≤day 成员。"""
    reader = FakeReader({"sector_constituent_snapshot_fake": _CONSTIT_TSV})
    codes = bis.fetch_constituents_asof(reader, "BK.demo", "2026-09-26", _fake_resolver)
    assert codes == ["000001", "300750", "600000"]
    sql = reader.calls[0]
    assert "snapshot_date <= '2026-09-26'" in sql
    assert "max(snapshot_date)" in sql and " FINAL " in sql


def test_pit_no_snapshot_returns_empty_not_today_constituents():
    """无满足 PIT 的快照→空列表，禁拍今日成分（§3 L3 禁近端成分回看远端）。"""
    reader = FakeReader({})
    assert bis.fetch_constituents_asof(reader, "BK.demo", "2026-09-26", _fake_resolver) == []


def test_unregistered_category_fails_closed():
    """品类未注册→KeyError fail-closed（禁凭记忆编表名；S3/§4.6 注册后自愈）。"""
    with pytest.raises(KeyError):
        bis.resolve_table(
            "market_board_index_1min", lambda _c: (_ for _ in ()).throw(KeyError("market_board_index_1min"))
        )
