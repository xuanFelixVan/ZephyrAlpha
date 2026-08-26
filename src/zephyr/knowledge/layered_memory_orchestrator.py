# [BLUEPRINT] MOD-KNW-009 | docs/03_modules/_domain_knowledge/layered_memory_orchestrator/blueprint.md
# [MODULE] zephyr.knowledge.layered_memory_orchestrator
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（编排核心纯内存；五层检索适配器/时钟 全注入）
# [CONSUMERS] 运行时装配批（五层记忆统一注入点装配 / RAG 检索收口）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层词表闭合(faiss|fts5|graph|git|rag); 层适配器全注入缺层标记 degraded 不重建; 检索分层扇出+结果按 doc_id 合并去重(取最高分); 层故障降级不阻断; 结果按 (-score, doc_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/layered_memory_orchestrator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LayeredMemoryError(占位 ZA-KNW-UNREGISTERED-LAYERED-MEMORY)——非法层/重复注册/空查询/未注册层注销/适配器返回非法命中时抛
# [TESTS] tests/knowledge/test_layered_memory_orchestrator.py
# [A_module] module_id=MOD-KNW-009 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""LayeredMemoryOrchestrator — 五层记忆编排器（MOD-KNW-009）。

B13-04342（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-011，A3 D-AUTONOMY-05）：
MemGPT 分层思想单机版——FAISS 语义 / SQLite FTS5 全文 / 知识图谱 / Git 仓库 /
RAG **五层记忆收口编排**：层适配器**全注入**（缺层标记 degraded 不重建）+
统一检索编排（分层扇出 + 结果按 doc_id 合并去重 + 层故障降级不阻断）+
层健康检查。

查重分工（蓝图 §0）：kb_engine=八 Collection CRUD 门面（本件不做存储只做跨层
检索编排）；rag_pipeline=RAG 问答生成管道（本件把 RAG 当一层检索源，不做生成）；
cross_collection_retriever=向量库内跨集合检索（本件=跨异构记忆层编排，层适配
器由装配批注入）。纯内存/DI，不触网不起子进程。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "LayerHealth",
    "LayerHit",
    "LayeredMemoryError",
    "LayeredMemoryOrchestrator",
    "MemoryLayer",
    "MergedHit",
    "SearchResult",
]


class LayeredMemoryError(Exception):
    """五层记忆编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-LAYERED-MEMORY。
    """


class MemoryLayer(str, Enum):
    """记忆层（词表闭合，定义序即健康检查/合并输出序）。"""

    FAISS = "faiss"
    FTS5 = "fts5"
    GRAPH = "graph"
    GIT = "git"
    RAG = "rag"


_LAYER_ORDER: Final[tuple[MemoryLayer, ...]] = tuple(MemoryLayer)
_LAYER_RANK: Final[dict[MemoryLayer, int]] = {layer: i for i, layer in enumerate(_LAYER_ORDER)}

#: 层检索适配器签名：adapter(query, limit) -> Iterable[LayerHit]
LayerAdapter = Callable[[str, int], Iterable["LayerHit"]]


@dataclass(frozen=True)
class LayerHit:
    """单层检索命中（适配器返回载体，frozen）。"""

    doc_id: str
    layer: MemoryLayer
    score: float
    snippet: str


@dataclass(frozen=True)
class MergedHit:
    """跨层合并命中（按 doc_id 去重，layers 按层定义序）。"""

    doc_id: str
    score: float
    layers: tuple[MemoryLayer, ...]
    snippet: str


@dataclass(frozen=True)
class SearchResult:
    """统一检索结果（degraded_layers 按层定义序）。"""

    query: str
    hits: tuple[MergedHit, ...]
    degraded_layers: tuple[MemoryLayer, ...]


@dataclass(frozen=True)
class LayerHealth:
    """单层健康视图（缺层/曾故障 → degraded）。"""

    layer: MemoryLayer
    registered: bool
    degraded: bool
    failure_count: int
    last_error: str | None


def _validate_layer(layer: MemoryLayer) -> MemoryLayer:
    if not isinstance(layer, MemoryLayer):
        raise LayeredMemoryError(f"非法记忆层: {layer!r}（词表闭合 faiss|fts5|graph|git|rag）")
    return layer


class LayeredMemoryOrchestrator:
    """五层记忆收口编排件（层注册 + 统一检索 + 降级 + 健康检查）。"""

    def __init__(
        self,
        *,
        adapters: Mapping[MemoryLayer, LayerAdapter] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._adapters: dict[MemoryLayer, LayerAdapter] = {}
        self._failures: dict[MemoryLayer, tuple[int, str | None]] = {
            layer: (0, None) for layer in _LAYER_ORDER
        }
        for layer, adapter in (adapters or {}).items():
            self.register_layer(layer, adapter)

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _record_failure(self, layer: MemoryLayer, err: str) -> None:
        count, _ = self._failures[layer]
        self._failures[layer] = (count + 1, err)

    # ── 层注册 ────────────────────────────────────────────────────────────

    def register_layer(self, layer: MemoryLayer, adapter: LayerAdapter) -> None:
        """注册层适配器（缺层不重建；重复注册 → Fail-Closed）。"""
        _validate_layer(layer)
        if not callable(adapter):
            raise LayeredMemoryError(f"层 {layer.value} 适配器不可调用: {adapter!r}")
        if layer in self._adapters:
            raise LayeredMemoryError(f"层 {layer.value} 重复注册")
        self._adapters[layer] = adapter

    def unregister_layer(self, layer: MemoryLayer) -> None:
        """摘除层适配器（未注册 → Fail-Closed）。"""
        _validate_layer(layer)
        if layer not in self._adapters:
            raise LayeredMemoryError(f"层 {layer.value} 未注册，无法摘除")
        del self._adapters[layer]

    def registered_layers(self) -> tuple[MemoryLayer, ...]:
        """已注册层（按层定义序确定性输出）。"""
        return tuple(layer for layer in _LAYER_ORDER if layer in self._adapters)

    # ── 统一检索编排 ───────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        layers: Sequence[MemoryLayer] | None = None,
    ) -> SearchResult:
        """分层扇出检索：合并去重 + 层故障降级不阻断（确定性排序）。"""
        if not query or not query.strip():
            raise LayeredMemoryError("query 为空")
        if limit < 1:
            raise LayeredMemoryError(f"limit 非法: {limit!r}")
        targets: tuple[MemoryLayer, ...]
        if layers is None:
            targets = _LAYER_ORDER
        else:
            if not layers:
                raise LayeredMemoryError("layers 为空（显式指定时须非空）")
            targets = tuple(_validate_layer(layer) for layer in layers)

        best: dict[str, tuple[float, str, set[MemoryLayer]]] = {}
        degraded: set[MemoryLayer] = set()
        for layer in targets:
            adapter = self._adapters.get(layer)
            if adapter is None:
                degraded.add(layer)  # 缺层标记 degraded，不重建
                continue
            try:
                raw_hits = list(adapter(query, limit))
            except Exception as exc:  # noqa: BLE001 — 层故障降级不阻断（蓝图 §0）
                _log.warning("层 %s 检索故障降级: %s", layer.value, exc)
                self._record_failure(layer, f"{type(exc).__name__}: {exc}")
                degraded.add(layer)
                continue
            for hit in raw_hits:
                if not isinstance(hit, LayerHit):
                    raise LayeredMemoryError(
                        f"层 {layer.value} 适配器返回非法命中: {hit!r}（须为 LayerHit）"
                    )
                if not hit.doc_id:
                    raise LayeredMemoryError(f"层 {layer.value} 命中 doc_id 为空")
                entry = best.get(hit.doc_id)
                if entry is None:
                    best[hit.doc_id] = (float(hit.score), hit.snippet, {layer})
                else:
                    score, snippet, srcs = entry
                    srcs.add(layer)
                    if float(hit.score) > score:
                        best[hit.doc_id] = (float(hit.score), hit.snippet, srcs)

        merged = [
            MergedHit(
                doc_id=doc_id,
                score=score,
                layers=tuple(sorted(srcs, key=lambda la: _LAYER_RANK[la])),
                snippet=snippet,
            )
            for doc_id, (score, snippet, srcs) in best.items()
        ]
        merged.sort(key=lambda h: (-h.score, h.doc_id))  # 确定性
        return SearchResult(
            query=query,
            hits=tuple(merged[:limit]),
            degraded_layers=tuple(layer for layer in _LAYER_ORDER if layer in degraded),
        )

    # ── 健康检查 ──────────────────────────────────────────────────────────

    def health_check(self) -> tuple[LayerHealth, ...]:
        """五层健康视图（按层定义序；缺层/曾故障 → degraded）。"""
        out: list[LayerHealth] = []
        for layer in _LAYER_ORDER:
            count, last_error = self._failures[layer]
            registered = layer in self._adapters
            out.append(
                LayerHealth(
                    layer=layer,
                    registered=registered,
                    degraded=(not registered) or count > 0,
                    failure_count=count,
                    last_error=last_error,
                )
            )
        return tuple(out)
