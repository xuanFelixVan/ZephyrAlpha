# [BLUEPRINT] MOD-SIG-070 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-14 行）
# [MODULE] tests.signal_ashare.test_limit_up_reason_attribution
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.limit_up_reason_attribution
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=涨停归因逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-070_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-070 涨停原因归因 单元测试（GAP-F-14，合成数据不触库）。

覆盖：个股直命中匹配、主题词典命中、板块主题聚合双腿、三级归因判定
（直命中/板块联动双条件/无明确归因）、板块多归属择优、主入口降级链
（客户端不可得/票池空/单腿异常独立降级）、日期非法 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

import pytest

from zephyr.signal_ashare.limit_up_reason_attribution import (
    REASON_DIRECT_NEWS,
    REASON_SECTOR_LINKAGE,
    REASON_UNATTRIBUTED,
    AttributionConfig,
    LimitUpStockInput,
    NewsItemInput,
    attribute_limit_up_reasons,
    attribute_stocks,
    build_sector_themes,
    match_stock_news,
    match_themes,
)

TD = date(2026, 8, 21)


def _stocks() -> list[LimitUpStockInput]:
    return [
        LimitUpStockInput(symbol="000001.SZ", name="华芯科技", pct_change=10.0),
        LimitUpStockInput(symbol="000002.SZ", name="中微半导体", pct_change=10.0),
        LimitUpStockInput(symbol="000003.SZ", name="东方物流", pct_change=9.9),
        LimitUpStockInput(symbol="000004.SZ", name="静默股份", pct_change=10.0),
    ]


def _news() -> list[NewsItemInput]:
    return [
        NewsItemInput(news_id="n1", title="华芯科技发布新一代AI芯片", publish_time="2026-08-21 10:00:00"),
        NewsItemInput(news_id="n2", title="芯片产业再迎政策利好，晶圆厂扩产", publish_time="2026-08-21 11:00:00"),
        NewsItemInput(
            news_id="n3", title="华芯科技获大基金增持", publish_time="2026-08-21 12:00:00", content="半导体板块走强"
        ),
        NewsItemInput(news_id="n4", title="物流业整合传闻发酵", publish_time="2026-08-20 20:00:00"),
    ]


def _sector_map() -> dict[str, list[tuple[str, str]]]:
    return {
        "000001.SZ": [("880201.SH", "半导体")],
        "000002.SZ": [("880201.SH", "半导体")],
        "000003.SZ": [("880301.SH", "交通运输")],
        "000004.SZ": [("880401.SH", "综合")],
    }


# ------------------------------------------------------------------
# match_stock_news
# ------------------------------------------------------------------


def test_match_stock_news_direct_hit_sorted_desc():
    hits = match_stock_news(_stocks()[0], _news())
    assert [n.news_id for n in hits] == ["n3", "n1"]  # 按发布时间倒序


def test_match_stock_news_topk_cap():
    cfg = AttributionConfig(max_news_per_stock=1)
    hits = match_stock_news(_stocks()[0], _news(), cfg)
    assert len(hits) == 1 and hits[0].news_id == "n3"


def test_match_stock_news_short_name_no_match():
    stock = LimitUpStockInput(symbol="X", name="甲", pct_change=10.0)
    assert match_stock_news(stock, _news()) == []


def test_match_stock_news_no_hit():
    hits = match_stock_news(_stocks()[3], _news())  # 静默股份
    assert hits == []


# ------------------------------------------------------------------
# match_themes
# ------------------------------------------------------------------


def test_match_themes_alias_hit():
    themes = match_themes("晶圆厂扩产叠加光刻突破")
    assert "半导体" in themes


def test_match_themes_no_hit():
    assert match_themes("今日天气晴朗") == []


def test_match_themes_custom_dict():
    themes = match_themes("合成文本含量子", {"量子科技": ("量子",)})
    assert themes == ["量子科技"]


# ------------------------------------------------------------------
# build_sector_themes
# ------------------------------------------------------------------


def test_build_sector_themes_two_legs():
    themes = build_sector_themes(
        _stocks(), _news(), _sector_map(), {s.symbol: match_stock_news(s, _news()) for s in _stocks()}
    )
    semi = themes["880201.SH"]
    assert semi.limit_up_count == 2
    assert semi.sector_name == "半导体"
    assert semi.themes[0].theme == "半导体"  # 直命中腿命中最多
    assert semi.themes[0].hit_count == 2  # n1/n3 直命中（n2 未点名股票/板块名，不计入）
    logistics = themes["880301.SH"]
    assert logistics.limit_up_count == 1  # 无主题命中（交通板块名未被点名）


def test_build_sector_themes_leg2_sector_name_mention():
    # 腿2：新闻点名板块名（"半导体板块"）→ 主题计入，即使非个股直命中
    news = _news() + [
        NewsItemInput(news_id="n5", title="半导体板块午后异动拉升", publish_time="2026-08-21 13:00:00"),
    ]
    themes = build_sector_themes(
        _stocks(),
        news,
        _sector_map(),
        {s.symbol: match_stock_news(s, news) for s in _stocks()},
    )
    semi = themes["880201.SH"]
    assert semi.themes[0].hit_count == 3  # n1/n3 直命中 + n5 板块名点名


def test_build_sector_themes_theme_cap():
    cfg = AttributionConfig(max_themes_per_sector=1)
    themes = build_sector_themes(
        _stocks(),
        _news(),
        _sector_map(),
        {s.symbol: match_stock_news(s, _news()) for s in _stocks()},
        cfg,
    )
    assert len(themes["880201.SH"].themes) == 1


# ------------------------------------------------------------------
# attribute_stocks 三级判定
# ------------------------------------------------------------------


def test_attribute_direct_news_reason():
    items, _, stats = attribute_stocks(_stocks(), _news(), _sector_map())
    first = items[0]
    assert first.reason_type == REASON_DIRECT_NEWS
    assert first.matched_news_ids == ["n3", "n1"]
    assert "半导体" in first.matched_keywords
    assert stats[REASON_DIRECT_NEWS] == 1


def test_attribute_sector_linkage_double_condition():
    # 中微半导体：无个股名直命中，但半导体板块 2 家涨停+主题命中 → 板块联动
    items, _, stats = attribute_stocks(_stocks(), _news(), _sector_map())
    second = items[1]
    assert second.reason_type == REASON_SECTOR_LINKAGE
    assert second.sector_code == "880201.SH"
    assert "半导体" in second.reason_text
    assert stats[REASON_SECTOR_LINKAGE] == 1


def test_attribute_unattributed_when_sector_theme_missing():
    # 交通运输板块仅 1 家涨停且无主题命中 → 双条件不满足 → 无明确归因
    items, _, stats = attribute_stocks(_stocks(), _news(), _sector_map())
    third = items[2]
    assert third.reason_type == REASON_UNATTRIBUTED
    assert stats[REASON_UNATTRIBUTED] == 2  # 东方物流 + 静默股份


def test_attribute_linkage_min_limitups_guard():
    cfg = AttributionConfig(sector_linkage_min_limitups=3)  # 提高阈值 → 半导体 2 家不满足
    items, _, _ = attribute_stocks(_stocks(), _news(), _sector_map(), cfg)
    assert items[1].reason_type == REASON_UNATTRIBUTED


def test_attribute_empty_stocks():
    items, themes, stats = attribute_stocks([], _news(), _sector_map())
    assert items == [] and themes == {} and stats[REASON_UNATTRIBUTED] == 0


# ------------------------------------------------------------------
# 主入口（注入位 + 降级链）
# ------------------------------------------------------------------


def test_main_entry_injected_full():
    result = attribute_limit_up_reasons(
        TD,
        stocks=_stocks(),
        news_items=_news(),
        sector_map=_sector_map(),
    )
    assert result.date == "2026-08-21"
    assert len(result.items) == 4
    assert result.degraded is False
    assert result.sector_themes[0].sector_code == "880201.SH"  # 涨停家数排序
    assert result.stats[REASON_DIRECT_NEWS] == 1


def test_main_entry_client_unavailable_degraded(monkeypatch):
    monkeypatch.setattr("zephyr.signal_ashare.limit_up_reason_attribution._default_client", lambda: None)
    result = attribute_limit_up_reasons(TD)  # 未注入任何腿
    assert result.degraded is True
    assert result.items == []


def test_main_entry_leg_exception_independent_degrade():
    class _BoomClient:
        def execute(self, sql, params):  # noqa: ARG002
            raise RuntimeError("boom")

    result = attribute_limit_up_reasons(TD, ch_client=_BoomClient())
    assert result.degraded is False  # 腿异常独立降级，不炸整体
    assert result.items == []  # 票池空
    assert any("票池腿降级" in n for n in result.notes)


def test_main_entry_empty_pool_note():
    result = attribute_limit_up_reasons(TD, stocks=[], news_items=_news(), sector_map=_sector_map())
    assert result.items == []
    assert any("票池为空" in n for n in result.notes)


def test_main_entry_bad_date_fail_closed():
    with pytest.raises(ValueError):
        attribute_limit_up_reasons("2026/08/21", stocks=[], news_items=[], sector_map={})


def test_result_json_serializable():
    result = attribute_limit_up_reasons(
        TD,
        stocks=_stocks(),
        news_items=_news(),
        sector_map=_sector_map(),
    )
    json.dumps(asdict(result), ensure_ascii=False)  # 不抛即过
