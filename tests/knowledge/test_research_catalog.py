# [BLUEPRINT] MOD-KNW-012 | docs/03_modules/_domain_knowledge/research_catalog/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-012 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_research_catalog
# [TESTS] src/zephyr/knowledge/research_catalog.py
"""MOD-KNW-012 单元测试：research_catalog 研究目录。

蓝图验收（B6-08548/CAND-KNW-015，B6 D-RESEARCH-06）：
研究资产元数据索引（类型词表闭合）+ 标签多对多 + SQLite FTS5 检索
（真 :memory: FTS5）+ 引用关系 cites/cited_by 双向 + 语义检索注入适配器
+ L1-L4 分级访问过滤（低于级别不可见）。全内存替身，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.knowledge.research_catalog",
    reason="research_catalog not importable",
)

from zephyr.knowledge.research_catalog import (  # noqa: E402
    AccessLevel,
    AssetMeta,
    AssetType,
    ResearchCatalog,
    ResearchCatalogError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _cat(semantic=None) -> ResearchCatalog:
    return ResearchCatalog(conn=sqlite3.connect(":memory:"), clock=lambda: _T0, semantic_adapter=semantic)


def _meta(
    asset_id: str,
    title: str,
    *,
    asset_type: AssetType = AssetType.PAPER,
    abstract: str = "",
    level: AccessLevel = AccessLevel.L1,
) -> AssetMeta:
    return AssetMeta(
        asset_id=asset_id,
        asset_type=asset_type,
        title=title,
        abstract=abstract or f"{title} 摘要",
        level=level,
        created_at=_T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 元数据索引 + 分级可见性
# ──────────────────────────────────────────────────────────────────────────────


class TestIndexAsset:
    def test_conn_not_injected_fail_closed(self) -> None:
        with pytest.raises(ResearchCatalogError):
            ResearchCatalog(conn=None, clock=lambda: _T0)

    def test_index_and_get(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "动量因子综述"))
        asset = cat.get_asset("a1")
        assert asset.title == "动量因子综述"
        assert asset.asset_type is AssetType.PAPER
        assert asset.created_at == _T0

    def test_index_duplicate_raises(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        with pytest.raises(ResearchCatalogError):
            cat.index_asset(_meta("a1", "y"))

    def test_index_invalid_type_raises(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.index_asset(_meta("a1", "x", asset_type="blog"))  # type: ignore[arg-type]

    def test_index_empty_title_raises(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.index_asset(_meta("a1", ""))

    def test_get_unknown_raises(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.get_asset("ghost")

    def test_get_invisible_level_raises(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("sec", "核心策略", level=AccessLevel.L4))
        with pytest.raises(ResearchCatalogError):
            cat.get_asset("sec", caller_level=AccessLevel.L2)  # 低于级别不可见
        assert cat.get_asset("sec", caller_level=AccessLevel.L4).asset_id == "sec"

    def test_list_assets_level_filter_and_type_filter(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "公开论文", level=AccessLevel.L1))
        cat.index_asset(_meta("a2", "内部因子", asset_type=AssetType.FACTOR, level=AccessLevel.L3))
        cat.index_asset(_meta("a3", "机密实验", asset_type=AssetType.EXPERIMENT, level=AccessLevel.L4))
        l1 = cat.list_assets(caller_level=AccessLevel.L1)
        assert [a.asset_id for a in l1] == ["a1"]
        l4 = cat.list_assets(caller_level=AccessLevel.L4)
        assert [a.asset_id for a in l4] == ["a1", "a2", "a3"]  # asset_id 确定性排序
        factors = cat.list_assets(asset_type=AssetType.FACTOR, caller_level=AccessLevel.L4)
        assert [a.asset_id for a in factors] == ["a2"]

    def test_invalid_caller_level_raises(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.list_assets(caller_level="L9")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 标签系统（多对多）
# ──────────────────────────────────────────────────────────────────────────────


class TestTags:
    def test_add_and_query_tags(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        cat.add_tags("a1", ["动量", "A股"])
        cat.add_tags("a1", ["动量"])  # 幂等
        assert cat.tags_of("a1") == ("A股", "动量")  # 确定性排序

    def test_remove_tags(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        cat.add_tags("a1", ["动量", "A股"])
        cat.remove_tags("a1", ["动量"])
        assert cat.tags_of("a1") == ("A股",)

    def test_add_tags_empty_raises(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        with pytest.raises(ResearchCatalogError):
            cat.add_tags("a1", [])
        with pytest.raises(ResearchCatalogError):
            cat.add_tags("a1", ["  "])

    def test_tags_unknown_asset_raises(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.add_tags("ghost", ["x"])

    def test_assets_by_tag_many_to_many(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "论文一"))
        cat.index_asset(_meta("a2", "论文二", level=AccessLevel.L3))
        cat.add_tags("a1", ["动量"])
        cat.add_tags("a2", ["动量"])
        assert [a.asset_id for a in cat.assets_by_tag("动量", caller_level=AccessLevel.L4)] == ["a1", "a2"]
        assert [a.asset_id for a in cat.assets_by_tag("动量", caller_level=AccessLevel.L1)] == ["a1"]

    def test_tag_searchable_via_fts(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "量化研究", abstract="中性摘要"))
        cat.add_tags("a1", ["双均线"])
        hits = cat.search_fts("双均线")
        assert [h.asset_id for h in hits] == ["a1"]


# ──────────────────────────────────────────────────────────────────────────────
# FTS5 全文检索（真 :memory: FTS5）
# ──────────────────────────────────────────────────────────────────────────────


class TestFtsSearch:
    def test_fts_hit_title_and_abstract(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "动量 因子研究", abstract="反转效应对照"))
        cat.index_asset(_meta("a2", "波动率笔记", abstract="无关内容"))
        hits = cat.search_fts("动量")
        assert [h.asset_id for h in hits] == ["a1"]

    def test_fts_level_filter(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "动量 公开", level=AccessLevel.L1))
        cat.index_asset(_meta("a2", "动量 机密", level=AccessLevel.L4))
        hits = cat.search_fts("动量", caller_level=AccessLevel.L1)
        assert [h.asset_id for h in hits] == ["a1"]

    def test_fts_deterministic_order(self) -> None:
        cat = _cat()
        for i in range(3):
            cat.index_asset(_meta(f"a{i}", "动量 因子 研究"))
        r1 = [h.asset_id for h in cat.search_fts("动量 因子")]
        r2 = [h.asset_id for h in cat.search_fts("动量 因子")]
        assert r1 == r2 and len(r1) == 3

    def test_fts_empty_query_raises(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.search_fts("  ")

    def test_fts_no_match_returns_empty(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "动量"))
        assert cat.search_fts("不存在的关键词xyz") == ()


# ──────────────────────────────────────────────────────────────────────────────
# 引用关系（cites/cited_by 双向）
# ──────────────────────────────────────────────────────────────────────────────


class TestCitations:
    def test_cites_and_cited_by_bidirectional(self) -> None:
        cat = _cat()
        for aid in ("a1", "a2", "a3"):
            cat.index_asset(_meta(aid, f"论文{aid}"))
        cat.add_citation("a1", "a2")
        cat.add_citation("a1", "a3")
        cat.add_citation("a2", "a3")
        assert cat.cites("a1") == ("a2", "a3")  # 确定性排序
        assert cat.cited_by("a3") == ("a1", "a2")

    def test_citation_self_raises(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        with pytest.raises(ResearchCatalogError):
            cat.add_citation("a1", "a1")

    def test_citation_unknown_asset_raises(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        with pytest.raises(ResearchCatalogError):
            cat.add_citation("a1", "ghost")

    def test_citation_duplicate_idempotent(self) -> None:
        cat = _cat()
        cat.index_asset(_meta("a1", "x"))
        cat.index_asset(_meta("a2", "y"))
        cat.add_citation("a1", "a2")
        cat.add_citation("a1", "a2")  # 幂等
        assert cat.cites("a1") == ("a2",)


# ──────────────────────────────────────────────────────────────────────────────
# 语义检索（注入适配器 + 级别过滤）
# ──────────────────────────────────────────────────────────────────────────────


class TestSemanticSearch:
    def test_semantic_ok_with_level_filter(self) -> None:
        cat = _cat(semantic=lambda q, n: [("a2", 0.95), ("a1", 0.9), ("ghost", 0.8)])
        cat.index_asset(_meta("a1", "公开", level=AccessLevel.L1))
        cat.index_asset(_meta("a2", "机密", level=AccessLevel.L3))
        hits = cat.semantic_search("动量", caller_level=AccessLevel.L4)
        assert [h.asset_id for h in hits] == ["a2", "a1"]  # 按分数降序；ghost 忽略
        hits_l1 = cat.semantic_search("动量", caller_level=AccessLevel.L1)
        assert [h.asset_id for h in hits_l1] == ["a1"]  # L3 不可见

    def test_semantic_not_injected_fail_closed(self) -> None:
        cat = _cat()
        with pytest.raises(ResearchCatalogError):
            cat.semantic_search("动量")

    def test_semantic_adapter_failure_wrapped(self) -> None:
        def _boom(q: str, n: int):
            raise RuntimeError("向量库不可用")

        cat = _cat(semantic=_boom)
        with pytest.raises(ResearchCatalogError):
            cat.semantic_search("动量")

    def test_semantic_empty_query_raises(self) -> None:
        cat = _cat(semantic=lambda q, n: [])
        with pytest.raises(ResearchCatalogError):
            cat.semantic_search("")
