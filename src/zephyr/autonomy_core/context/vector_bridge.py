# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.vector_bridge
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE-VMS-001)
========================================================
Task ID    : MOD-CONTEXT_ENGINE-TASK-010
Priority   : P1 (beta)
Depends    : MOD-CONTEXT_ENGINE-TASK-002 (Build 阶段)

职责
----
在 CE.build() 和 VMS.search() 之间建立调用桥接，接受 query Embedding +
Collection name -> 返回 top-K results。

设计决策
--------
- 桥接模式：低耦合——CE 不直接依赖 VMS 具体实现
- 超时机制：每次 VMS 调用带 5s 超时
- 降级策略：VMS 不可用时返回空结果集（由调用方 build_context 降级处理）
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VMSSearchProtocol(Protocol):
    """VMS 检索协议——vector_bridge 依赖此协议而非具体实现。"""

    def search(self, collection: str, query: str, top_k: int) -> list[Any]: ...


@dataclass
class VectorSearchResult:
    """单条 VMS 检索结果。"""

    content: str = ""
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    collection: str = ""


@dataclass
class VectorSearchResponse:
    """VMS 检索响应——含超时/降级标记。"""

    results: list[VectorSearchResult] = field(default_factory=list)
    total_found: int = 0
    elapsed_ms: float = 0.0
    degraded: bool = False
    error: str = ""
    collection: str = ""


class VectorBridge:
    """CE↔VMS 检索桥接。

    接受 collection name + query embedding -> 返回 top-K 结构化结果。

    Using::

        bridge = VectorBridge(vms_client)
        response = bridge.search("ke_entries", "task_type:CODE_GEN", top_k=5)
        for r in response.results:
            print(f"[{r.score:.3f}] {r.content[:50]}")
    """

    def __init__(
        self,
        vms_client: object | None = None,
        *,
        default_timeout_s: float = 5.0,
    ) -> None:
        self._vms = vms_client
        self._timeout_s = default_timeout_s

    def search(
        self,
        collection: str,
        query: str,
        top_k: int = 5,
        *,
        timeout_s: float | None = None,
    ) -> VectorSearchResponse:
        """执行 VMS 检索——带超时 + 降级。

        Parameters
        ----------
        collection : str
            VMS Collection 名称 (decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces)
        query : str
            检索查询文本
        top_k : int
            返回结果数量
        timeout_s : float | None
            超时秒数（None 使用默认值）

        Returns
        -------
        VectorSearchResponse
        """
        timeout = timeout_s if timeout_s is not None else self._timeout_s
        start = time.monotonic()

        if self._vms is None:
            return VectorSearchResponse(
                results=[],
                total_found=0,
                elapsed_ms=(time.monotonic() - start) * 1000,
                degraded=True,
                error="VMS client not available",
                collection=collection,
            )

        try:
            raw = self._vms.search(collection, query, top_k=top_k)
            elapsed_ms = (time.monotonic() - start) * 1000

            if elapsed_ms > timeout * 1000:
                return VectorSearchResponse(
                    results=[],
                    total_found=0,
                    elapsed_ms=elapsed_ms,
                    degraded=True,
                    error="VMS search timed out",
                    collection=collection,
                )

            results = self._parse_raw_results(raw, collection)
            return VectorSearchResponse(
                results=results,
                total_found=len(results),
                elapsed_ms=elapsed_ms,
                degraded=False,
                collection=collection,
            )
        except Exception as e:
            return VectorSearchResponse(
                results=[],
                total_found=0,
                elapsed_ms=(time.monotonic() - start) * 1000,
                degraded=True,
                error=str(e),
                collection=collection,
            )

    @staticmethod
    def _parse_raw_results(
        raw: list[Any],
        collection: str,
    ) -> list[VectorSearchResult]:
        results: list[VectorSearchResult] = []
        for item in raw:
            if isinstance(item, dict):
                results.append(
                    VectorSearchResult(
                        content=str(item.get("content", item.get("summary", ""))),
                        score=float(item.get("score", 0.0)),
                        metadata=item.get("metadata", {}),
                        collection=collection,
                    )
                )
            elif isinstance(item, str):
                results.append(
                    VectorSearchResult(
                        content=item,
                        score=0.0,
                        collection=collection,
                    )
                )
            else:
                results.append(
                    VectorSearchResult(
                        content=str(item),
                        score=0.0,
                        collection=collection,
                    )
                )
        return sorted(results, key=lambda x: x.score, reverse=True)

    @property
    def is_available(self) -> bool:
        return self._vms is not None

    @property
    def timeout_s(self) -> float:
        return self._timeout_s

    CT_CE_VMS_COLLECTIONS: tuple[str, ...] = (
        "ke_entries",
        "vibe_rules",
        "blueprints",
        "failure_patterns",
    )

    def search_all_collections(
        self,
        query: str,
        top_k: int = 5,
        timeout_s: float | None = None,
    ) -> list[VectorSearchResponse]:
        responses: list[VectorSearchResponse] = []
        for coll in self.CT_CE_VMS_COLLECTIONS:
            resp = self.search(coll, query, top_k=top_k, timeout_s=timeout_s)
            responses.append(resp)
        return responses
