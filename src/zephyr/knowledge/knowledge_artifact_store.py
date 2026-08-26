# [BLUEPRINT] MOD-KNW-004 | docs/03_modules/_domain_knowledge/knowledge_artifact_store/blueprint.md
# [MODULE] zephyr.knowledge.knowledge_artifact_store
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（聚合根纯内存；clock 注入）
# [CONSUMERS] 运行时装配批（研究产出版本链归档 / 六维索引检索 / 聚合根不变量挂载）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 6类产出词表闭合(RawKnowledgePacket|StructuredKnowledgeFragment|ClassifiedKnowledgePackage|ModuleMappingResult|NewModule|TrialResult); 各类payload键集合闭合不可变(缺/多键拒绝); 同artifact_id版本链严格递增(写不可改,改即新版本); 无更新/删除API; 6维索引(来源/作者/类型/目标层级/时间/效果)查询确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/knowledge_artifact_store/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ArtifactStoreError(占位 ZA-KNW-UNREGISTERED-ARTIFACT-STORE)——非法类型/schema键不符/空标识/未知工件/未知版本/非法时间窗时抛
# [TESTS] tests/knowledge/test_knowledge_artifact_store.py
# [A_module] module_id=MOD-KNW-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""KnowledgeArtifactStore — 知识工件库（MOD-KNW-004）。

B12-03637（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-008，B12）：6 类知
识产出（RawKnowledgePacket/StructuredKnowledgeFragment/
ClassifiedKnowledgePackage/ModuleMappingResult/NewModule/TrialResult 词表
闭合）不可变 schema + 版本化存储（同 artifact_id 版本链，写不可改，改即
新版本）+ 6 维索引（来源/作者/类型/目标层级/时间/效果）查询。聚合根版
本不变量不变式。canonical 承接 KNW-018（6 类 schema 重登稿）归并。

查重分工：research/evidence/evidence_chain=证据链挂载（本件=产出版本链归
档基座，不做证据关联）；kb_engine=通用条目 CRUD（本件=闭合 schema 的聚
合根存储，零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "Artifact",
    "ArtifactStoreError",
    "ArtifactType",
    "KnowledgeArtifactStore",
]


class ArtifactStoreError(Exception):
    """知识工件库存储输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-ARTIFACT-STORE。
    """


class ArtifactType(str, Enum):
    """6 类知识产出（词表闭合）。"""

    RAW_KNOWLEDGE_PACKET = "RawKnowledgePacket"
    STRUCTURED_KNOWLEDGE_FRAGMENT = "StructuredKnowledgeFragment"
    CLASSIFIED_KNOWLEDGE_PACKAGE = "ClassifiedKnowledgePackage"
    MODULE_MAPPING_RESULT = "ModuleMappingResult"
    NEW_MODULE = "NewModule"
    TRIAL_RESULT = "TrialResult"


#: 各类产出 payload 键集合（闭合不可变 schema：缺键/多键均拒绝）
ARTIFACT_SCHEMAS: Final = {
    ArtifactType.RAW_KNOWLEDGE_PACKET: frozenset({"content"}),
    ArtifactType.STRUCTURED_KNOWLEDGE_FRAGMENT: frozenset({"fragment"}),
    ArtifactType.CLASSIFIED_KNOWLEDGE_PACKAGE: frozenset({"category", "fragments"}),
    ArtifactType.MODULE_MAPPING_RESULT: frozenset({"mapping"}),
    ArtifactType.NEW_MODULE: frozenset({"module_id", "blueprint"}),
    ArtifactType.TRIAL_RESULT: frozenset({"metrics"}),
}

#: 6 维索引词表（来源/作者/类型/目标层级/时间/效果）
_INDEX_DIMS: Final = ("source", "author", "artifact_type", "target_layer", "created_at", "effect")


@dataclass(frozen=True)
class Artifact:
    """知识工件单版本（frozen；版本链节点不可改）。"""

    artifact_id: str
    version: int
    artifact_type: ArtifactType
    source: str
    author: str
    target_layer: str
    effect: str
    payload: dict
    created_at: datetime.datetime


class KnowledgeArtifactStore:
    """6 类产出不可变 schema + 版本链存储 + 6 维索引查询（聚合根）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        # 版本链：{artifact_id: [Artifact, ...按 version 递增...]}
        self._chains: dict[str, list[Artifact]] = {}
        # 等值维索引：{维度: {取值: {(artifact_id, version), ...}}}
        self._index: dict[str, dict[str, set[tuple[str, int]]]] = {
            dim: {} for dim in _INDEX_DIMS if dim != "created_at"
        }

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _require_text(value: str, name: str) -> None:
        if not value or not isinstance(value, str):
            raise ArtifactStoreError(f"{name} 为空")

    @staticmethod
    def _type_of(raw: object) -> ArtifactType:
        try:
            return raw if isinstance(raw, ArtifactType) else ArtifactType(str(raw))
        except ValueError as exc:
            raise ArtifactStoreError(f"非法工件类型: {raw!r}（6类词表闭合）") from exc

    def _index_put(self, artifact: Artifact) -> None:
        key = (artifact.artifact_id, artifact.version)
        for dim, value in (
            ("source", artifact.source),
            ("author", artifact.author),
            ("artifact_type", artifact.artifact_type.value),
            ("target_layer", artifact.target_layer),
            ("effect", artifact.effect),
        ):
            self._index[dim].setdefault(value, set()).add(key)

    def _chain(self, artifact_id: str) -> list[Artifact]:
        chain = self._chains.get(artifact_id)
        if not chain:
            raise ArtifactStoreError(f"未知工件: {artifact_id!r}")
        return chain

    # ── 写入（写不可改，改即新版本） ──────────────────────────────────────

    def put(
        self,
        artifact_id: str,
        artifact_type: ArtifactType,
        *,
        source: str,
        author: str,
        target_layer: str,
        effect: str,
        payload: Mapping,
    ) -> Artifact:
        """写入新版本：同 artifact_id 版本链严格 +1；schema 键集合闭合校验。"""
        self._require_text(artifact_id, "artifact_id")
        atype = self._type_of(artifact_type)
        self._require_text(source, "source")
        self._require_text(author, "author")
        self._require_text(target_layer, "target_layer")
        self._require_text(effect, "effect")
        keys = frozenset(payload.keys()) if isinstance(payload, Mapping) else frozenset()
        required = ARTIFACT_SCHEMAS[atype]
        if keys != required:
            raise ArtifactStoreError(
                f"schema 键不符: {atype.value} 要求 {sorted(required)!r}，实收 {sorted(keys)!r}"
                "（闭合不可变 schema）"
            )
        chain = self._chains.setdefault(artifact_id, [])
        artifact = Artifact(
            artifact_id=artifact_id,
            version=len(chain) + 1,
            artifact_type=atype,
            source=source,
            author=author,
            target_layer=target_layer,
            effect=effect,
            payload=dict(payload),
            created_at=self._clock(),
        )
        chain.append(artifact)
        self._index_put(artifact)
        _log.info("工件入链: %s v%d (%s)", artifact_id, artifact.version, atype.value)
        return artifact

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get(self, artifact_id: str, version: int | None = None) -> Artifact:
        """取指定版本（缺省最新；未知工件/版本 → Fail-Closed）。"""
        chain = self._chain(artifact_id)
        if version is None:
            return chain[-1]
        if version < 1 or version > len(chain):
            raise ArtifactStoreError(
                f"未知版本: {artifact_id!r} v{version}（现存 1..{len(chain)}）"
            )
        return chain[version - 1]

    def history(self, artifact_id: str) -> list[Artifact]:
        """全版本链（按 version 递增）。"""
        return list(self._chain(artifact_id))

    def query(
        self,
        *,
        source: str | None = None,
        author: str | None = None,
        artifact_type: ArtifactType | None = None,
        target_layer: str | None = None,
        effect: str | None = None,
        created_from: datetime.datetime | None = None,
        created_to: datetime.datetime | None = None,
    ) -> list[Artifact]:
        """6 维索引查询：等值维走索引交集，时间维按 [from, to] 闭区间过滤。"""
        if artifact_type is not None:
            atype = self._type_of(artifact_type)
        else:
            atype = None
        if created_from is not None and created_to is not None and created_from > created_to:
            raise ArtifactStoreError(
                f"非法时间窗: from {created_from!r} > to {created_to!r}"
            )
        filters = (
            ("source", source),
            ("author", author),
            ("artifact_type", atype.value if atype is not None else None),
            ("target_layer", target_layer),
            ("effect", effect),
        )
        hit: set[tuple[str, int]] | None = None
        for dim, value in filters:
            if value is None:
                continue
            bucket = self._index[dim].get(value, set())
            hit = set(bucket) if hit is None else (hit & bucket)
            if not hit:
                return []
        keys = hit if hit is not None else {
            (aid, a.version) for aid, chain in self._chains.items() for a in chain
        }
        out = [self._chains[aid][ver - 1] for aid, ver in keys]
        if created_from is not None:
            out = [a for a in out if a.created_at >= created_from]
        if created_to is not None:
            out = [a for a in out if a.created_at <= created_to]
        out.sort(key=lambda a: (a.artifact_id, a.version))
        return out
