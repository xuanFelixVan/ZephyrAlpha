# [BLUEPRINT] MOD-DAT-REF-DATA | tests/zephyr/data/test_reference_data_manager.py
# [MODULE] tests.zephyr.data.test_reference_data_manager
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.reference_data_manager
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT-REF-DATA | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ReferenceDataManager 单元测试——参考数据管理器（CAND-DAT-015 / B13-04240 / D-DATA-08）。

覆盖：
    1. DDL 常量交付（行业分类/指数成分/多源映射三表）
    2. 行业分类：双码全空 fail-closed；登记与查询
    3. 指数成分 PIT：effective_date/removed_date 时点语义 constituents_at
    4. 多源 ID 映射：登记/双向翻译/未知源 fail-closed/缺失返回 None
    5. 变更事件：内嵌日志 + 注入 publisher 外发；publisher 异常不阻断
"""

from __future__ import annotations

import datetime

import pytest

from zephyr.data.reference_data_manager import (
    REF_ID_MAPPING_DDL,
    REF_INDEX_CONSTITUENT_DDL,
    REF_INDUSTRY_DDL,
    ReferenceDataManager,
)

D = datetime.date


# ── 1. DDL 常量 ──


def test_ddl_constants_present():
    assert "gics" in REF_INDUSTRY_DDL and "sw" in REF_INDUSTRY_DDL
    assert "effective_date" in REF_INDEX_CONSTITUENT_DDL
    assert "minqmt" in REF_ID_MAPPING_DDL
    assert "tushare" in REF_ID_MAPPING_DDL and "akshare" in REF_ID_MAPPING_DDL


# ── 2. 行业分类 ──


def test_upsert_industry_requires_at_least_one_code():
    mgr = ReferenceDataManager()
    with pytest.raises(ValueError):
        mgr.upsert_industry("600519")


def test_upsert_and_query_industry():
    mgr = ReferenceDataManager()
    mgr.upsert_industry("600519", gics="4010", sw="食品饮料", source="akshare")
    rec = mgr.industry_of("600519")
    assert rec is not None
    assert rec.gics == "4010" and rec.sw == "食品饮料"
    assert mgr.industry_of("000001") is None


# ── 3. 指数成分 PIT ──


def test_index_constituent_pit_semantics():
    mgr = ReferenceDataManager()
    mgr.set_index_constituent("000300", "600519", D(2026, 1, 1))
    mgr.set_index_constituent("000300", "601318", D(2026, 3, 1))
    mgr.remove_index_constituent("000300", "601318", D(2026, 6, 1))
    assert mgr.constituents_at("000300", D(2026, 2, 1)) == frozenset({"600519"})
    assert mgr.constituents_at("000300", D(2026, 4, 1)) == frozenset({"600519", "601318"})
    assert mgr.constituents_at("000300", D(2026, 7, 1)) == frozenset({"600519"})
    assert mgr.constituents_at("000300", D(2025, 12, 1)) == frozenset()


def test_set_index_constituent_validates_input():
    mgr = ReferenceDataManager()
    with pytest.raises(ValueError):
        mgr.set_index_constituent("", "600519", D(2026, 1, 1))
    with pytest.raises(ValueError):
        mgr.set_index_constituent("000300", "", D(2026, 1, 1))


def test_remove_before_set_fail_closed():
    mgr = ReferenceDataManager()
    with pytest.raises(ValueError):
        mgr.remove_index_constituent("000300", "600519", D(2026, 6, 1))


# ── 4. 多源 ID 映射 ──


def test_register_mapping_requires_one_code():
    mgr = ReferenceDataManager()
    with pytest.raises(ValueError):
        mgr.register_mapping("600519")


def test_map_id_bidirectional_translation():
    mgr = ReferenceDataManager()
    mgr.register_mapping("600519", minqmt="600519.SH", tushare="600519.SH", akshare="sh600519")
    assert mgr.map_id("600519", "minqmt", "akshare") == "sh600519"
    assert mgr.map_id("600519", "akshare", "tushare") == "600519.SH"
    assert mgr.map_id("600519", "minqmt", "minqmt") == "600519.SH"


def test_map_id_unknown_source_fail_closed():
    mgr = ReferenceDataManager()
    mgr.register_mapping("600519", minqmt="600519.SH")
    with pytest.raises(ValueError):
        mgr.map_id("600519", "bogus", "minqmt")
    with pytest.raises(ValueError):
        mgr.map_id("600519", "minqmt", "bogus")


def test_map_id_missing_returns_none():
    mgr = ReferenceDataManager()
    mgr.register_mapping("600519", minqmt="600519.SH")
    assert mgr.map_id("600519", "minqmt", "tushare") is None
    assert mgr.map_id("000001", "minqmt", "tushare") is None


# ── 5. 变更事件 ──


def test_change_events_logged_and_published():
    events = []
    mgr = ReferenceDataManager(event_publisher=events.append)
    mgr.upsert_industry("600519", sw="食品饮料")
    mgr.register_mapping("600519", minqmt="600519.SH")
    assert len(mgr.change_events) == 2
    assert len(events) == 2
    kinds = {e.kind for e in mgr.change_events}
    assert kinds == {"industry_upsert", "id_mapping_register"}


def test_publisher_error_not_blocking():
    def bad_pub(_):
        raise RuntimeError("bus down")

    mgr = ReferenceDataManager(event_publisher=bad_pub)
    mgr.upsert_industry("600519", sw="食品饮料")
    assert len(mgr.change_events) == 1
    assert mgr.industry_of("600519") is not None
