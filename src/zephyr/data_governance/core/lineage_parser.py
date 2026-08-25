# [BLUEPRINT] MOD-DATA_GOV-004 | docs/03_modules/_domain_data_governance/lineage_parser/blueprint.md
# [MODULE] zephyr.data_governance.core.lineage_parser
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.lineage_tracker
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 幂等与环检测复用 MOD-DATA_GOV-002 不重造; 契约缺 id/source_domain Fail-Closed; 空节点名 Fail-Closed; 批内(source,target)去重首条胜出; 环拒记不中断批; CTR 真源文件只读解析不修改
# [MODIFY-GUARD] tests/data_governance/test_lineage_parser.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LineageParseError(未登记错误码-申请中)
# [TESTS] tests/data_governance/test_lineage_parser.py
# [A_module] module_id=MOD-DATA_GOV-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""M8-S01 血缘解析器（MOD-DATA_GOV-004）。

真源：construction_backlog_dig.tsv B10-02313（A1 交易决策架构 §30.4.3，
裁定=做 P1）+ CAND-DATGOV-001。

定位：血缘边注册/上下游查询底座（MOD-DATA_GOV-002 lineage_tracker）已有，
本模块补**从契约定义自动解析提取数据流转关系**的缺口——幂等与环检测复用
tracker 现有实现，不重造：

  ① CTR 契约解析：cross_layer_contracts.yaml 单条契约 → source_domain
     --produces--> CTR-id --consumed_by--> 各 target_domains 边；
  ② 模块头注解解析：`# [MODULE]` 当前模块、`# [DEPENDENCIES]`（`;` 分隔，
     仅 zephyr.* 内部件成边，外部库略过记 skipped）→ dep --imports--> module；
     `# [CONSUMERS]` 括号内模块名/独立 MOD-id 令牌 → module --consumed_by--> consumer；
  ③ 入图：批内 (source,target) 去重（首条胜出），tracker 幂等重加计
     updated，环 ValueError 捕获记 rejected 不中断批，产出 LineageParseReport。
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from zephyr.data_governance.core.lineage_tracker import LineageEdge, LineageTracker

__all__: Final = [
    "LineageParseError",
    "LineageParseReport",
    "ModuleHeaderAnnotations",
    "edges_of_annotations",
    "ingest_into_tracker",
    "parse_ctr_contract",
    "parse_module_header",
]

_log = logging.getLogger(__name__)

#: 转换类型词表（source→transformation→target 三元组中段）
TRANSFORMATION_PRODUCES: Final[str] = "produces"
TRANSFORMATION_CONSUMED_BY: Final[str] = "consumed_by"
TRANSFORMATION_IMPORTS: Final[str] = "imports"

_HEADER_MODULE_RE: Final = re.compile(r"^# \[MODULE\]\s*(\S+)\s*$", re.MULTILINE)
_HEADER_DEPENDENCIES_RE: Final = re.compile(r"^# \[DEPENDENCIES\]\s*(.*?)\s*$", re.MULTILINE)
_HEADER_CONSUMERS_RE: Final = re.compile(r"^# \[CONSUMERS\]\s*(.*?)\s*$", re.MULTILINE)
# CONSUMERS 条目：括号内首个令牌（模块名/文件名）优先，否则独立 MOD-id 令牌
_CONSUMER_PAREN_RE: Final = re.compile(r"\(([^),;\s]+)")
_MOD_ID_RE: Final = re.compile(r"^(MOD-[A-Z0-9_\-]+)")
_INTERNAL_MODULE_PREFIX: Final[str] = "zephyr."


class LineageParseError(ValueError):
    """血缘解析输入畸形（Fail-Closed；未登记错误码-申请中）。"""


def _validate_node(name: str, *, field_name: str) -> str:
    """节点名校验：非空非空白（Fail-Closed）。"""
    if not isinstance(name, str) or not name.strip():
        raise LineageParseError(f"血缘节点名为空: {field_name}={name!r}")
    return name.strip()


@dataclass(frozen=True)
class ModuleHeaderAnnotations:
    """模块头三注解解析结果。

    Attributes:
        module: `# [MODULE]` 当前模块路径
        dependencies: `# [DEPENDENCIES]` 中 zephyr.* 内部依赖（成边面）
        consumers: `# [CONSUMERS]` 抽取的消费者标识（括号内模块名/MOD-id）
        skipped_external: 外部依赖（非 zephyr.*，略过不成边，留痕）
    """

    module: str
    dependencies: tuple[str, ...] = ()
    consumers: tuple[str, ...] = ()
    skipped_external: tuple[str, ...] = ()


@dataclass(frozen=True)
class LineageParseReport:
    """入图报告（幂等/环检测语义如实记录）。

    Attributes:
        edges: 本批抽取的边总数
        added: 新入图边数
        updated: tracker 幂等重加（边已存在，transformation 以首条语义保留）边数
        rejected: 环拒记 (source, target, reason) 三元组
        skipped: 批内 (source,target) 重复去重边数（首条胜出）
        sources: 本批解析来源标签
    """

    edges: int
    added: int
    updated: int
    rejected: tuple[tuple[str, str, str], ...] = ()
    skipped: int = 0
    sources: tuple[str, ...] = field(default=())


def parse_ctr_contract(contract: Mapping[str, object]) -> list[LineageEdge]:
    """解析单条 CTR 契约为血缘边（缺 id/source_domain Fail-Closed）。

    边集：source_domain --produces--> contract_id；contract_id
    --consumed_by--> 各 target_domains。target_domains 缺省/空列表 → 仅
    produces 边；非列表 → Fail-Closed。
    """
    contract_id = _validate_node(str(contract.get("id") or ""), field_name="id")
    source_domain = _validate_node(
        str(contract.get("source_domain") or ""), field_name="source_domain"
    )
    raw_targets = contract.get("target_domains") or []
    if not isinstance(raw_targets, (list, tuple)):
        raise LineageParseError(
            f"契约 {contract_id} target_domains 非列表: {type(raw_targets).__name__}"
        )
    edges = [
        LineageEdge(source_domain, contract_id, TRANSFORMATION_PRODUCES),
    ]
    for target in raw_targets:
        edges.append(
            LineageEdge(
                contract_id,
                _validate_node(str(target), field_name="target_domains[]"),
                TRANSFORMATION_CONSUMED_BY,
            )
        )
    return edges


def parse_module_header(text: str) -> ModuleHeaderAnnotations:
    """解析模块头 `# [MODULE]`/`# [DEPENDENCIES]`/`# [CONSUMERS]` 三注解。

    DEPENDENCIES 按 `;` 分隔；仅 zephyr.* 内部件入 dependencies，外部库
    （numpy/hmmlearn 等）入 skipped_external。CONSUMERS 条目优先取括号内首个
    令牌（模块名/文件名），无括号取独立 MOD-id 令牌，其余自由文本略过。
    `# [MODULE]` 缺失 → Fail-Closed（无法定位边端点）。
    """
    module_match = _HEADER_MODULE_RE.search(text)
    if module_match is None:
        raise LineageParseError("模块头缺 # [MODULE] 注解（无法定位血缘边端点）")
    module = _validate_node(module_match.group(1), field_name="MODULE")

    dependencies: list[str] = []
    skipped: list[str] = []
    dep_match = _HEADER_DEPENDENCIES_RE.search(text)
    if dep_match is not None:
        for token in dep_match.group(1).split(";"):
            token = token.strip()
            if not token:
                continue
            if token.startswith(_INTERNAL_MODULE_PREFIX):
                dependencies.append(token)
            else:
                skipped.append(token)

    consumers: list[str] = []
    con_match = _HEADER_CONSUMERS_RE.search(text)
    if con_match is not None:
        for entry in con_match.group(1).split(";"):
            entry = entry.strip()
            if not entry:
                continue
            paren = _CONSUMER_PAREN_RE.search(entry)
            if paren is not None:
                consumers.append(paren.group(1).strip())
                continue
            mod_id = _MOD_ID_RE.match(entry)
            if mod_id is not None:
                consumers.append(mod_id.group(1))

    return ModuleHeaderAnnotations(
        module=module,
        dependencies=tuple(dependencies),
        consumers=tuple(consumers),
        skipped_external=tuple(skipped),
    )


def edges_of_annotations(annotations: ModuleHeaderAnnotations) -> list[LineageEdge]:
    """模块头注解 → 血缘边：dep --imports--> module；module --consumed_by--> consumer。"""
    edges = [
        LineageEdge(dep, annotations.module, TRANSFORMATION_IMPORTS)
        for dep in annotations.dependencies
    ]
    edges.extend(
        LineageEdge(annotations.module, consumer, TRANSFORMATION_CONSUMED_BY)
        for consumer in annotations.consumers
    )
    return edges


def ingest_into_tracker(
    edges: Sequence[LineageEdge],
    tracker: LineageTracker,
    *,
    sources: Sequence[str] = (),
) -> LineageParseReport:
    """边集入 lineage_tracker（幂等与环检测复用 MOD-DATA_GOV-002 实现）。

    - 批内 (source,target) 去重：首条胜出，其余计 skipped；
    - tracker 已有同键边：幂等重加计 updated（add_edge 语义保留首条 transformation）；
    - 环 ValueError：捕获记 rejected（source, target, reason），不中断批；
    - 自环/空节点名：Fail-Closed（LineageParseError）。
    """
    existing = {(e.source, e.target) for e in tracker.get_edges()}
    seen: set[tuple[str, str]] = set()
    added = 0
    updated = 0
    skipped = 0
    rejected: list[tuple[str, str, str]] = []

    for edge in edges:
        _validate_node(edge.source, field_name="source")
        _validate_node(edge.target, field_name="target")
        key = (edge.source, edge.target)
        if edge.source == edge.target:
            raise LineageParseError(f"自环不被允许: {edge.source!r}（解析面 Fail-Closed）")
        if key in seen:
            skipped += 1
            continue
        seen.add(key)
        was_present = key in existing
        try:
            tracker.add_edge(edge.source, edge.target, edge.transformation)
        except ValueError as exc:
            rejected.append((edge.source, edge.target, str(exc)))
            _log.warning("血缘边环拒记: %s -> %s: %s", edge.source, edge.target, exc)
            continue
        if was_present:
            updated += 1
        else:
            added += 1
            existing.add(key)

    return LineageParseReport(
        edges=len(edges),
        added=added,
        updated=updated,
        rejected=tuple(rejected),
        skipped=skipped,
        sources=tuple(sources),
    )
