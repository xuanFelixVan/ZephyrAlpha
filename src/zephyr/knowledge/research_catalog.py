# [BLUEPRINT] MOD-KNW-012 | docs/03_modules/_domain_knowledge/research_catalog/blueprint.md
# [MODULE] zephyr.knowledge.research_catalog
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（目录核心纯内存；SQLite FTS5 连接/时钟/语义检索适配器 全注入）
# [CONSUMERS] 运行时装配批（研究资产索引 / 引用图谱 / L1-L4 分级检索注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 资产类型词表闭合(paper|hypothesis|evidence|experiment|factor|dataset|note); 标签多对多; FTS5 经注入连接; 引用关系 cites/cited_by 双向一致禁自引; L1-L4 分级低于级别不可见; 检索结果确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/research_catalog/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResearchCatalogError(占位 ZA-KNW-UNREGISTERED-RESEARCH-CATALOG)——连接缺失/未知资产/非法类型或级别/重复资产/自引/空查询/语义适配器缺失时抛
# [TESTS] tests/knowledge/test_research_catalog.py
# [A_module] module_id=MOD-KNW-012 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ResearchCatalog — 研究目录（MOD-KNW-012）。

B6-08548（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-015，B6 D-RESEARCH-06）：
研究资产**元数据索引**（资产类型词表闭合）+ **标签系统**（多对多）+
SQLite **FTS5 全文检索**（注入连接）+ **引用关系表**（cites/cited_by 双
向）+ **语义检索**挂 vector_memory（注入适配器）+ **L1-L4 数据分级访问
过滤**（低于级别不可见）。

查重分工（蓝图 §0）：kb_engine=知识条目 CRUD/版本/审计（本件=研究资产目
录索引与分级可见性，不管条目正文版本）；research_project_aggregate=项目
维度聚合（本件=资产维度目录与引用）；cross_collection_retriever=向量库
跨集合检索（本件语义检索仅挂注入适配器）。纯内存/DI，不触网不起子进程。
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AccessLevel",
    "AssetMeta",
    "AssetType",
    "CatalogHit",
    "ResearchCatalog",
    "ResearchCatalogError",
]


class ResearchCatalogError(Exception):
    """研究目录输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-RESEARCH-CATALOG。
    """


class AssetType(str, Enum):
    """研究资产类型（词表闭合）。"""

    PAPER = "paper"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    EXPERIMENT = "experiment"
    FACTOR = "factor"
    DATASET = "dataset"
    NOTE = "note"


class AccessLevel(str, Enum):
    """数据分级（L1 最低公开，L4 最高受限；低于级别不可见）。"""

    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


_LEVEL_RANK: Final[dict[AccessLevel, int]] = {
    AccessLevel.L1: 1,
    AccessLevel.L2: 2,
    AccessLevel.L3: 3,
    AccessLevel.L4: 4,
}


@dataclass(frozen=True)
class AssetMeta:
    """研究资产元数据（frozen）。"""

    asset_id: str
    asset_type: AssetType
    title: str
    abstract: str
    level: AccessLevel
    created_at: datetime.datetime
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CatalogHit:
    """检索命中（score 越大越相关）。"""

    asset_id: str
    title: str
    score: float


#: 语义检索适配器签名：adapter(query, limit) -> Sequence[(asset_id, score)]
SemanticAdapter = Callable[[str, int], Sequence[tuple[str, float]]]

_SCHEMA: Final = """
CREATE TABLE IF NOT EXISTS catalog_assets (
    asset_id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    level TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS catalog_fts USING fts5(
    asset_id UNINDEXED, title, abstract, tags
);
CREATE TABLE IF NOT EXISTS catalog_tags (
    asset_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (asset_id, tag)
);
CREATE TABLE IF NOT EXISTS catalog_citations (
    citing_id TEXT NOT NULL,
    cited_id TEXT NOT NULL,
    PRIMARY KEY (citing_id, cited_id)
);
"""

_TS_FMT: Final = "%Y-%m-%dT%H:%M:%S.%f"


def _is_cjk(ch: str) -> bool:
    return "一" <= ch <= "鿿"


def _expand_for_fts(text: str) -> str:
    """FTS5 unicode61 不切中文：CJK 串转二元组，ASCII 词原样（确定性）。"""
    tokens: list[str] = []
    seg: list[str] = []
    seg_cjk: bool | None = None

    def _flush() -> None:
        if not seg:
            return
        s = "".join(seg)
        if seg_cjk:
            if len(s) == 1:
                tokens.append(s)
            else:
                tokens.extend(s[i : i + 2] for i in range(len(s) - 1))
        else:
            tokens.extend(w for w in s.split() if w)
        seg.clear()

    for ch in text:
        if _is_cjk(ch):
            if seg_cjk is False:
                _flush()
            seg.append(ch)
            seg_cjk = True
        elif ch.isalnum():
            if seg_cjk is True:
                _flush()
            seg.append(ch)
            seg_cjk = False
        else:
            _flush()
            seg_cjk = None
    _flush()
    return " ".join(tokens)


def _ts(dt: datetime.datetime) -> str:
    return dt.strftime(_TS_FMT)


def _parse(ts: str) -> datetime.datetime:
    return datetime.datetime.strptime(ts, _TS_FMT)


def _validate_level(level: AccessLevel) -> AccessLevel:
    if not isinstance(level, AccessLevel):
        raise ResearchCatalogError(f"非法访问级别: {level!r}（词表闭合 L1-L4）")
    return level


class ResearchCatalog:
    """研究资产目录件（索引 + 标签 + FTS5 + 引用 + 语义检索 + 分级过滤）。"""

    def __init__(
        self,
        *,
        conn: sqlite3.Connection | None,
        clock: Callable[[], datetime.datetime] | None = None,
        semantic_adapter: SemanticAdapter | None = None,
    ) -> None:
        if conn is None:
            raise ResearchCatalogError("sqlite 连接未注入（FTS5 检索强制经注入连接）")
        self._conn = conn
        self._clock = clock or datetime.datetime.now
        self._semantic = semantic_adapter
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _exists(self, asset_id: str) -> bool:
        return self._conn.execute(
            "SELECT 1 FROM catalog_assets WHERE asset_id = ?", (asset_id,)
        ).fetchone() is not None

    def _require(self, asset_id: str) -> None:
        if not asset_id:
            raise ResearchCatalogError("asset_id 为空")
        if not self._exists(asset_id):
            raise ResearchCatalogError(f"未知研究资产: {asset_id!r}")

    @staticmethod
    def _visible(row_level: str, caller_level: AccessLevel) -> bool:
        return _LEVEL_RANK[AccessLevel(row_level)] <= _LEVEL_RANK[caller_level]

    def _refresh_fts_tags(self, asset_id: str) -> None:
        tags = _expand_for_fts(" ".join(self.tags_of(asset_id)))
        self._conn.execute(
            "UPDATE catalog_fts SET tags = ? WHERE asset_id = ?", (tags, asset_id)
        )

    # ── 元数据索引 ──────────────────────────────────────────────────────────

    def index_asset(self, meta: AssetMeta) -> None:
        """登记资产元数据（重复 asset_id → Fail-Closed）。"""
        if not isinstance(meta, AssetMeta):
            raise ResearchCatalogError(f"非法资产元数据: {meta!r}（须为 AssetMeta）")
        if not meta.asset_id:
            raise ResearchCatalogError("asset_id 为空")
        if not meta.title:
            raise ResearchCatalogError("资产标题为空")
        if not isinstance(meta.asset_type, AssetType):
            raise ResearchCatalogError(f"非法资产类型: {meta.asset_type!r}（词表闭合）")
        _validate_level(meta.level)
        if self._exists(meta.asset_id):
            raise ResearchCatalogError(f"asset_id 重复: {meta.asset_id!r}")
        self._conn.execute(
            "INSERT INTO catalog_assets "
            "(asset_id, asset_type, title, abstract, level, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (meta.asset_id, meta.asset_type.value, meta.title, meta.abstract,
             meta.level.value, _ts(meta.created_at)),
        )
        self._conn.execute(
            "INSERT INTO catalog_fts (asset_id, title, abstract, tags) VALUES (?, ?, ?, '')",
            (meta.asset_id, _expand_for_fts(meta.title), _expand_for_fts(meta.abstract)),
        )
        self._conn.commit()
        _log.info("研究资产建档: %s (%s/%s)", meta.asset_id, meta.asset_type.value, meta.level.value)

    def get_asset(self, asset_id: str, *, caller_level: AccessLevel = AccessLevel.L4) -> AssetMeta:
        """资产查询（不可见即不存在，Fail-Closed）。"""
        _validate_level(caller_level)
        self._require(asset_id)
        row = self._conn.execute(
            "SELECT asset_id, asset_type, title, abstract, level, created_at "
            "FROM catalog_assets WHERE asset_id = ?",
            (asset_id,),
        ).fetchone()
        if not self._visible(row[4], caller_level):
            raise ResearchCatalogError(
                f"资产不可见: {asset_id!r}（{row[4]} 高于调用方 {caller_level.value}）"
            )
        return AssetMeta(
            asset_id=row[0], asset_type=AssetType(row[1]), title=row[2],
            abstract=row[3], level=AccessLevel(row[4]), created_at=_parse(row[5]),
        )

    def list_assets(
        self,
        *,
        asset_type: AssetType | None = None,
        caller_level: AccessLevel = AccessLevel.L4,
    ) -> tuple[AssetMeta, ...]:
        """资产列表（按 asset_id 确定性排序 + 级别过滤）。"""
        _validate_level(caller_level)
        if asset_type is not None and not isinstance(asset_type, AssetType):
            raise ResearchCatalogError(f"非法资产类型: {asset_type!r}")
        rows = self._conn.execute(
            "SELECT asset_id, asset_type, title, abstract, level, created_at "
            "FROM catalog_assets ORDER BY asset_id"
        ).fetchall()
        out = [
            AssetMeta(
                asset_id=r[0], asset_type=AssetType(r[1]), title=r[2],
                abstract=r[3], level=AccessLevel(r[4]), created_at=_parse(r[5]),
            )
            for r in rows
            if self._visible(r[4], caller_level)
            and (asset_type is None or AssetType(r[1]) is asset_type)
        ]
        return tuple(out)

    # ── 标签系统（多对多） ──────────────────────────────────────────────────

    def add_tags(self, asset_id: str, tags: Sequence[str]) -> None:
        """打标签（幂等；空标签/未知资产 → Fail-Closed）。"""
        self._require(asset_id)
        if not tags:
            raise ResearchCatalogError("tags 为空")
        for tag in tags:
            if not tag or not tag.strip():
                raise ResearchCatalogError("标签为空")
            self._conn.execute(
                "INSERT OR IGNORE INTO catalog_tags (asset_id, tag) VALUES (?, ?)",
                (asset_id, tag.strip()),
            )
        self._refresh_fts_tags(asset_id)
        self._conn.commit()

    def remove_tags(self, asset_id: str, tags: Sequence[str]) -> None:
        """摘标签（幂等）。"""
        self._require(asset_id)
        if not tags:
            raise ResearchCatalogError("tags 为空")
        for tag in tags:
            self._conn.execute(
                "DELETE FROM catalog_tags WHERE asset_id = ? AND tag = ?",
                (asset_id, tag.strip()),
            )
        self._refresh_fts_tags(asset_id)
        self._conn.commit()

    def tags_of(self, asset_id: str) -> tuple[str, ...]:
        """资产标签（确定性排序）。"""
        self._require(asset_id)
        rows = self._conn.execute(
            "SELECT tag FROM catalog_tags WHERE asset_id = ? ORDER BY tag", (asset_id,)
        ).fetchall()
        return tuple(r[0] for r in rows)

    def assets_by_tag(
        self,
        tag: str,
        *,
        caller_level: AccessLevel = AccessLevel.L4,
    ) -> tuple[AssetMeta, ...]:
        """按标签反查（asset_id 确定性排序 + 级别过滤）。"""
        _validate_level(caller_level)
        if not tag or not tag.strip():
            raise ResearchCatalogError("标签为空")
        rows = self._conn.execute(
            "SELECT a.asset_id, a.asset_type, a.title, a.abstract, a.level, a.created_at "
            "FROM catalog_assets a JOIN catalog_tags t ON t.asset_id = a.asset_id "
            "WHERE t.tag = ? ORDER BY a.asset_id",
            (tag.strip(),),
        ).fetchall()
        return tuple(
            AssetMeta(
                asset_id=r[0], asset_type=AssetType(r[1]), title=r[2],
                abstract=r[3], level=AccessLevel(r[4]), created_at=_parse(r[5]),
            )
            for r in rows
            if self._visible(r[4], caller_level)
        )

    # ── FTS5 全文检索 ───────────────────────────────────────────────────────

    def search_fts(
        self,
        query: str,
        *,
        caller_level: AccessLevel = AccessLevel.L4,
        limit: int = 10,
    ) -> tuple[CatalogHit, ...]:
        """FTS5 全文检索（bm25 升序取反为相关性分 + 级别过滤 + 确定性排序）。"""
        _validate_level(caller_level)
        if not query or not query.strip():
            raise ResearchCatalogError("query 为空")
        if limit < 1:
            raise ResearchCatalogError(f"limit 非法: {limit!r}")
        match = _expand_for_fts(query.strip())
        if not match:
            raise ResearchCatalogError("query 无有效检索词")
        rows = self._conn.execute(
            "SELECT f.asset_id, a.title, bm25(catalog_fts) AS rank, a.level "
            "FROM catalog_fts f JOIN catalog_assets a ON a.asset_id = f.asset_id "
            "WHERE catalog_fts MATCH ? "
            "ORDER BY rank, f.asset_id",
            (match,),
        ).fetchall()
        hits = [
            CatalogHit(asset_id=r[0], title=r[1], score=-float(r[2]))
            for r in rows
            if self._visible(r[3], caller_level)
        ]
        return tuple(hits[:limit])

    # ── 引用关系（双向） ────────────────────────────────────────────────────

    def add_citation(self, citing_id: str, cited_id: str) -> None:
        """登记引用：citing 引用 cited；自引 → Fail-Closed；重复幂等。"""
        self._require(citing_id)
        self._require(cited_id)
        if citing_id == cited_id:
            raise ResearchCatalogError(f"自引非法: {citing_id!r}")
        self._conn.execute(
            "INSERT OR IGNORE INTO catalog_citations (citing_id, cited_id) VALUES (?, ?)",
            (citing_id, cited_id),
        )
        self._conn.commit()

    def cites(self, asset_id: str) -> tuple[str, ...]:
        """资产引用了谁（确定性排序）。"""
        self._require(asset_id)
        rows = self._conn.execute(
            "SELECT cited_id FROM catalog_citations WHERE citing_id = ? ORDER BY cited_id",
            (asset_id,),
        ).fetchall()
        return tuple(r[0] for r in rows)

    def cited_by(self, asset_id: str) -> tuple[str, ...]:
        """谁引用了资产（确定性排序）。"""
        self._require(asset_id)
        rows = self._conn.execute(
            "SELECT citing_id FROM catalog_citations WHERE cited_id = ? ORDER BY citing_id",
            (asset_id,),
        ).fetchall()
        return tuple(r[0] for r in rows)

    # ── 语义检索（注入适配器 + 级别过滤） ───────────────────────────────────

    def semantic_search(
        self,
        query: str,
        *,
        caller_level: AccessLevel = AccessLevel.L4,
        limit: int = 10,
    ) -> tuple[CatalogHit, ...]:
        """语义检索：挂 vector_memory 注入适配器；未注入 Fail-Closed。"""
        _validate_level(caller_level)
        if not query or not query.strip():
            raise ResearchCatalogError("query 为空")
        if limit < 1:
            raise ResearchCatalogError(f"limit 非法: {limit!r}")
        if self._semantic is None:
            raise ResearchCatalogError("semantic_adapter 未注入（语义检索强制挂 vector_memory 适配器）")
        try:
            raw = list(self._semantic(query.strip(), limit))
        except Exception as exc:  # noqa: BLE001 — 适配器失败 Fail-Closed 包装
            raise ResearchCatalogError(f"语义检索适配器失败: {exc}") from exc
        level_rows = self._conn.execute(
            "SELECT asset_id, title, level FROM catalog_assets"
        ).fetchall()
        assets = {r[0]: (r[1], r[2]) for r in level_rows}
        hits: list[CatalogHit] = []
        for asset_id, score in raw:
            entry = assets.get(asset_id)
            if entry is None:
                continue  # 适配器返回未索引资产 → 忽略
            title, lvl = entry
            if not self._visible(lvl, caller_level):
                continue  # 低于级别不可见
            hits.append(CatalogHit(asset_id=asset_id, title=title, score=float(score)))
        hits.sort(key=lambda h: (-h.score, h.asset_id))  # 确定性
        return tuple(hits[:limit])
