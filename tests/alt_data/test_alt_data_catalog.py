# [BLUEPRINT] MOD-ALT-008 | docs/03_modules/_domain_alt_data/alt_data_catalog/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-008 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_alt_data_catalog
# [TESTS] src/zephyr/alt_data/alt_data_catalog.py
"""MOD-ALT-008 单元测试：alt_data_catalog 另类数据目录。

蓝图验收（B5-07089/CAND-TESTA-024，B5 D-ALT-DATA-09，承接 TESTA-011）：
元数据登记（quality∈[0,1]/cost_quota≥0）+ 标签系统（去重升序）+ 血缘
lineage_sink 回调（未注入 Fail-Closed）+ SQLite FTS5 检索（注入内存连接，
source_id 升序确定性）+ 注册→审批→下线生命周期状态机（越迁 Fail-Closed）。
时钟/血缘/FTS 连接全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.alt_data.alt_data_catalog",
    reason="alt_data_catalog not importable",
)

from zephyr.alt_data.alt_data_catalog import (  # noqa: E402
    AltDataCatalog,
    AltDataCatalogError,
    CatalogEntry,
    CatalogLifecycle,
    CatalogSourceType,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 0, 0)


def _entry(
    source_id: str = "src_news_1",
    source_type: CatalogSourceType = CatalogSourceType.NEWS,
    tags: tuple = ("akshare", "news"),
    description: str = "akshare free news feed",
    quality_score: float = 0.8,
    cost_quota: int = 500,
) -> CatalogEntry:
    return CatalogEntry(
        source_id=source_id,
        source_type=source_type,
        update_frequency="daily",
        quality_score=quality_score,
        cost_quota=cost_quota,
        description=description,
        tags=tags,
    )


def _catalog(**kw) -> AltDataCatalog:
    kw.setdefault("clock", lambda: _T0)
    return AltDataCatalog(**kw)


def _fts_conn() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")


# ──────────────────────────────────────────────────────────────────────────────
# 元数据登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_and_get_roundtrip(self) -> None:
        cat = _catalog()
        cat.register(_entry(tags=("b_tag", "a_tag", "b_tag")))
        record = cat.get("src_news_1")
        assert record.state is CatalogLifecycle.REGISTERED
        assert record.registered_at == _T0 and record.state_updated_at == _T0
        assert record.entry.tags == ("a_tag", "b_tag")  # 去重升序归一
        assert record.entry.quality_score == 0.8
        assert record.entry.update_frequency == "daily"

    def test_duplicate_raises(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        with pytest.raises(AltDataCatalogError):
            cat.register(_entry())

    def test_invalid_entry_raises(self) -> None:
        cat = _catalog()
        with pytest.raises(AltDataCatalogError):
            cat.register(_entry(source_id=""))  # 空 id
        with pytest.raises(AltDataCatalogError):
            cat.register(_entry(source_type="news"))  # 类型非枚举
        for bad_score in (1.5, -0.1, float("nan"), True, "0.8"):
            with pytest.raises(AltDataCatalogError):
                cat.register(_entry(source_id=f"s{bad_score}", quality_score=bad_score))
        for bad_quota in (-1, True, 1.5, "500"):
            with pytest.raises(AltDataCatalogError):
                cat.register(_entry(source_id=f"q{bad_quota}", cost_quota=bad_quota))
        with pytest.raises(AltDataCatalogError):
            cat.register(_entry(source_id="t1", tags=("ok", "")))  # 空标签
        with pytest.raises(AltDataCatalogError):
            cat.register("not-an-entry")  # 类型非法
        with pytest.raises(AltDataCatalogError):
            cat.get("ghost")  # 未知数据源


# ──────────────────────────────────────────────────────────────────────────────
# 标签系统
# ──────────────────────────────────────────────────────────────────────────────


class TestTags:
    def test_add_tags_merge_sorted(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        merged = cat.add_tags("src_news_1", ("etf", "akshare"))
        assert merged == ("akshare", "etf", "news")  # 合并去重升序
        assert cat.tags_of("src_news_1") == merged

    def test_remove_tags(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        remaining = cat.remove_tags("src_news_1", ("news", "ghost_tag"))
        assert remaining == ("akshare",)  # 不存在者静默略过

    def test_tag_errors_raise(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        with pytest.raises(AltDataCatalogError):
            cat.add_tags("src_news_1", ("",))  # 空标签
        with pytest.raises(AltDataCatalogError):
            cat.add_tags("ghost", ("x",))  # 未知源
        with pytest.raises(AltDataCatalogError):
            cat.remove_tags("ghost", ("x",))
        with pytest.raises(AltDataCatalogError):
            cat.tags_of("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 生命周期状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestLifecycle:
    def test_approve_ok_timestamps(self) -> None:
        now = [_T0]
        cat = AltDataCatalog(clock=lambda: now[0])
        cat.register(_entry())
        now[0] = _T1
        assert cat.approve("src_news_1") is CatalogLifecycle.APPROVED
        record = cat.get("src_news_1")
        assert record.state is CatalogLifecycle.APPROVED
        assert record.registered_at == _T0 and record.state_updated_at == _T1

    def test_approve_wrong_state_raises(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        cat.approve("src_news_1")
        with pytest.raises(AltDataCatalogError):
            cat.approve("src_news_1")  # 重复审批非法迁移

    def test_offline_flow_and_illegal_transitions(self) -> None:
        cat = _catalog()
        cat.register(_entry("src_a"))
        cat.register(_entry("src_b"))
        with pytest.raises(AltDataCatalogError):
            cat.offline("src_a")  # REGISTERED → OFFLINE 越迁
        cat.approve("src_a")
        assert cat.offline("src_a") is CatalogLifecycle.OFFLINE
        with pytest.raises(AltDataCatalogError):
            cat.approve("src_a")  # OFFLINE 不可逆
        assert cat.get("src_b").state is CatalogLifecycle.REGISTERED

    def test_list_by_state_sorted(self) -> None:
        cat = _catalog()
        cat.register(_entry("src_z"))
        cat.register(_entry("src_a"))
        cat.approve("src_z")
        approved = cat.list_by_state(CatalogLifecycle.APPROVED)
        assert [r.entry.source_id for r in approved] == ["src_z"]
        registered = cat.list_by_state(CatalogLifecycle.REGISTERED)
        assert [r.entry.source_id for r in registered] == ["src_a"]
        with pytest.raises(AltDataCatalogError):
            cat.list_by_state("approved")  # 状态非枚举


# ──────────────────────────────────────────────────────────────────────────────
# 血缘回调
# ──────────────────────────────────────────────────────────────────────────────


class TestLineage:
    def test_attach_lineage_ok(self) -> None:
        edges: list = []
        cat = _catalog(lineage_sink=lambda s, t, tf: edges.append((s, t, tf)))
        cat.register(_entry())
        cat.attach_lineage("src_news_1", "raw_layer.news")
        assert edges == [("raw_layer.news", "src_news_1", "catalog_register")]

    def test_attach_without_sink_fail_closed(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        with pytest.raises(AltDataCatalogError):
            cat.attach_lineage("src_news_1", "raw_layer.news")

    def test_attach_errors_raise(self) -> None:
        def _cycle_sink(s, t, tf):
            raise ValueError("会形成环")

        cat = _catalog(lineage_sink=_cycle_sink)
        cat.register(_entry())
        with pytest.raises(AltDataCatalogError):
            cat.attach_lineage("src_news_1", "raw_layer.news")  # 回调异常包装
        with pytest.raises(AltDataCatalogError):
            cat.attach_lineage("src_news_1", "")  # upstream 空
        with pytest.raises(AltDataCatalogError):
            cat.attach_lineage("ghost", "raw_layer.news")  # 未知源


# ──────────────────────────────────────────────────────────────────────────────
# FTS5 检索（注入连接）
# ──────────────────────────────────────────────────────────────────────────────


class TestSearch:
    def test_search_hit_ordering(self) -> None:
        cat = _catalog(fts_connection=_fts_conn())
        cat.register(_entry("src_b", description="free news feed"))
        cat.register(_entry("src_a", description="news and announcement"))
        cat.register(_entry("src_c", tags=("social",), description="social posts stream"))
        assert cat.search("news") == ("src_a", "src_b")  # 命中 + id 升序
        assert cat.search("social") == ("src_c",)
        assert cat.search("nonexistent") == ()

    def test_search_reflects_tag_changes(self) -> None:
        cat = _catalog(fts_connection=_fts_conn())
        cat.register(_entry(tags=("akshare",)))
        assert cat.search("etf") == ()
        cat.add_tags("src_news_1", ("etf",))
        assert cat.search("etf") == ("src_news_1",)  # 加签可检
        cat.remove_tags("src_news_1", ("etf",))
        assert cat.search("etf") == ()  # 移除后不再命中

    def test_search_without_connection_fail_closed(self) -> None:
        cat = _catalog()
        cat.register(_entry())
        with pytest.raises(AltDataCatalogError):
            cat.search("news")

    def test_search_invalid_query_raises(self) -> None:
        cat = _catalog(fts_connection=_fts_conn())
        cat.register(_entry())
        with pytest.raises(AltDataCatalogError):
            cat.search("")  # 空查询
        with pytest.raises(AltDataCatalogError):
            cat.search('"unclosed')  # FTS5 语法错包装
