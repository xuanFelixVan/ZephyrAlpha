# [BLUEPRINT] MOD-DAT-foreign_coverage | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-23 行）
# [MODULE] tests.zephyr.data.test_foreign_market_coverage
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.foreign_market_coverage
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网（query_fn 全 mock）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=外盘覆盖核查逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-foreign_coverage_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DAT-foreign_coverage 外盘覆盖核查器 单元测试（GAP-F-23/D3，mock 不触库）。

覆盖：12 标的三态判定（covered/stale/missing）、探测异常不误判 covered、
新鲜度窗口边界、TSV 解析容错、缺口采集配置位子集、symbol 白名单防注入、
日期非法 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

import pytest

from zephyr.data.foreign_market_coverage import (
    FOREIGN_COLLECTOR_SLOTS,
    FOREIGN_WATCHLIST,
    STATUS_COVERED,
    STATUS_MISSING,
    STATUS_STALE,
    TableProbeSpec,
    ForeignTarget,
    check_foreign_coverage,
    gap_collector_slots,
)

TD = date(2026, 8, 23)


def _fake_query(sql: str) -> str:
    """按 SQL 子串路由的查询桩（实测口径回放）。"""
    if "us_futures_intraday" in sql:
        return "CHA50CFD\t1\t2026-08-22\t2026-08-22\nES\t1\t2026-08-22\t2026-08-22"
    if "us_index" in sql:
        if "DJI" in sql:
            return "DJI\t29\t2026-07-14\t2026-08-21"
        if "IXIC" in sql:
            return "IXIC\t29\t2026-07-14\t2026-08-21"
        if "SPX" in sql:
            return "SPX\t29\t2026-07-14\t2026-08-21"
    return ""


def test_watchlist_twelve_targets():
    assert len(FOREIGN_WATCHLIST) == 12
    keys = [t.key for t in FOREIGN_WATCHLIST]
    assert keys == [
        "dow_jones", "nasdaq", "sp500", "hsi", "nikkei", "kospi",
        "a50", "dxy", "usdcnh", "wti", "gold", "ust10y",
    ]


def test_check_full_watchlist_statuses():
    report = check_foreign_coverage(query_fn=_fake_query, check_date=TD)
    by_key = {i.key: i for i in report.items}
    assert by_key["dow_jones"].status == STATUS_COVERED
    assert by_key["nasdaq"].status == STATUS_COVERED
    assert by_key["sp500"].status == STATUS_COVERED
    assert by_key["a50"].status == STATUS_COVERED  # 2026-08-22 快照在窗内
    for key in ("hsi", "nikkei", "kospi", "dxy", "usdcnh", "wti", "gold", "ust10y"):
        assert by_key[key].status == STATUS_MISSING
    assert report.covered_count == 4
    assert report.missing_count == 8
    assert report.check_date == "2026-08-23"


def test_stale_when_beyond_window():
    report = check_foreign_coverage(query_fn=_fake_query, check_date=date(2026, 9, 15))
    by_key = {i.key: i for i in report.items}
    assert by_key["dow_jones"].status == STATUS_STALE
    assert "陈旧" in by_key["dow_jones"].note


def test_probe_error_not_covered():
    def _boom(sql: str) -> str:
        raise RuntimeError("table not found")

    report = check_foreign_coverage(query_fn=_boom, check_date=TD)
    by_key = {i.key: i for i in report.items}
    assert by_key["dow_jones"].status == STATUS_MISSING  # 异常不误判 covered
    assert any(p.error for p in by_key["dow_jones"].probes)


def test_no_probe_table_target_missing_with_slot():
    report = check_foreign_coverage(query_fn=_fake_query, check_date=TD)
    usdcnh = next(i for i in report.items if i.key == "usdcnh")
    assert usdcnh.status == STATUS_MISSING
    assert usdcnh.collector_slot == "usdcnh_forex"
    assert "无探测表" in usdcnh.note


def test_gap_collector_slots_subset():
    report = check_foreign_coverage(query_fn=_fake_query, check_date=TD)
    slots = gap_collector_slots(report)
    assert set(slots) == {
        "hsi_index", "nikkei_index", "kospi_index", "dxy_forex",
        "usdcnh_forex", "wti_commodity", "gold_commodity", "ust10y_bond",
    }
    assert "provider_hint" in slots["ust10y_bond"]


def test_collector_slots_cover_all_missing_slot_keys():
    for target in FOREIGN_WATCHLIST:
        if target.collector_slot:
            assert target.collector_slot in FOREIGN_COLLECTOR_SLOTS


def test_symbol_whitelist_injection_guard():
    target = ForeignTarget(
        "evil", "注入", "index",
        (TableProbeSpec("c1_market.us_index", ("DJI' OR 1=1 --",)),), "",
    )
    with pytest.raises(ValueError):
        check_foreign_coverage(query_fn=_fake_query, check_date=TD, watchlist=(target,))


def test_bad_check_date_fail_closed():
    with pytest.raises(ValueError):
        check_foreign_coverage(query_fn=_fake_query, check_date="2026年8月")


def test_tsv_parse_tolerant():
    def _messy(sql: str) -> str:
        return "DJI\t29\t2026-07-14\t2026-08-21\nbroken-line\nXX\tNaN\tx\ty"

    target = ForeignTarget("dow_jones", "道琼斯", "index", (TableProbeSpec("c1_market.us_index", ("DJI",)),), "")
    report = check_foreign_coverage(query_fn=_messy, check_date=TD, watchlist=(target,))
    assert report.items[0].status == STATUS_COVERED  # 坏行被跳过，好行仍判定
    assert len(report.items[0].probes) == 1


def test_report_json_serializable():
    report = check_foreign_coverage(query_fn=_fake_query, check_date=TD)
    json.dumps(asdict(report), ensure_ascii=False)
