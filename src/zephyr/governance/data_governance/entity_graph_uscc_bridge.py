# [BLUEPRINT] MOD-USCC-BRIDGE | src/zephyr/governance/data_governance/entity_graph_uscc_bridge.py | §entity_graph uscc 富化最小消歧桥（EC1 §5.3 → C122；只读提案器，零写）
# [MODULE] zephyr.governance.data_governance.entity_graph_uscc_bridge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib(re/dataclasses)；psycopg2 仅 TYPE_CHECKING（连接由调用方注入，默认 depgraph_reader 只读角色）
# [CONSUMERS] uscc 富化跑批（WAIT：真实数据富化另批执行人）；tests/governance/data_governance/test_entity_graph_uscc_bridge.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只读提案器——本模块零 INSERT/UPDATE/DDL（富化写入属另批跑批，双写纪律：提案与施写分离）;
#   公司消歧金标准=uscc（设计真源 §4.1 钉死），名称匹配只产提案不产事实;
#   命中分级：uscc 直键=confidence 1.0 / name_norm 唯一=0.9 / 多义=ambiguous 附候选列表（禁自动择一）/ 零命中=unresolved（B/C/D 层富化 WAIT）;
#   人物概率消歧（姓名+出生年+任职轨迹 hash+关联公司交集）=骨架占位 NotReady——三证据齐才许合并（§7 坑：同名合并错误=假边=假信号）;
#   零新表：提案以内存 dataclass 返回，落盘由调用方走 .runtime/sessions/<sid>/staging/（24h TTL 语义）;
#   若未来立提案持久表=新 DDL=Owner 门位（本骨架明确不触发）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接异常照抛给调用方；查询零行=unresolved 提案（非异常）；多行=ambiguous（非异常）
# [TESTS] tests/governance/data_governance/test_entity_graph_uscc_bridge.py（mock 连接层，零真实 PG）
# [TTL] permanent
# [not-trading:数据治理侧 uscc 富化提案器（只读消歧桥），非交易决策节点——挂载豁免登记 tdm_mount_exemption_registry，复审点=uscc 富化跑批立项时]
"""entity_graph uscc 富化最小消歧桥（C122 骨架：读边名称 → 提案富化，零写）。

# [ALGO_FLOW]
# 输入: edge_holding 股东名称批次（只读连接，depgraph_reader 角色）
# 特征: 名称规范化（剥组织形式/全半角归一）→ name_norm；uscc 直键/唯一名/多义/零命中四态分级
# 算法: 消歧提案器——直键 confidence 1.0、name_norm 唯一 0.9、多义 ambiguous 附候选（禁自动择一）、
#       零命中 unresolved；人物三证据概率消歧骨架 NotReady 占位
# 输出: CompanyEnrichmentProposal 内存 dataclass 序列（零写库，落盘由调用方走 staging 24h TTL）

背景（EC1 台账 §5.3 + 设计真源 altdata_line/02 §2/§4/§7）：entity_graph 六表底座已建成，
node_person/node_company v1 空表——A 层 akshare 十大股东只有股东"名称"无 uscc/无人物属性，
富化（公司 uscc 直键 + 人物概率消歧）是数据面 P1①缺口。本模块是最小消歧桥：

1. :func:`normalize_cn_company_name` 名称规范化（剥组织形式后缀/全半角/空白）→ name_norm；
2. :func:`propose_company_enrichment` 对 edge_holding 侧股东名称批量出
   :class:`CompanyEnrichmentProposal`（uscc 直键 / name_norm 唯一 / ambiguous / unresolved 四态）；
3. :func:`propose_person_identity` 人物概率消歧骨架（三证据规则立法，实现占位 NotReady）。

消费方式：跑批（WAIT）拿提案列表 → 人工/高置信自动施写 node_company/node_person——
施写通道不在本模块（提案/施写分离，写前走 RULE-DATA-OPS 三步验证）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:  # pragma: no cover — 仅类型标注；psycopg2 由调用方注入
    import psycopg2.extensions

__all__: Final = [
    "normalize_cn_company_name",
    "CompanyEnrichmentProposal",
    "propose_company_enrichment",
    "propose_person_identity",
]

# 组织形式/地区后缀剥离表（name_norm 归一用；剥尽主干词，避开"主义/银行为"假剥）
_ORG_SUFFIXES: Final[tuple[str, ...]] = (
    "股份有限公司",
    "有限责任公司",
    "有限公司",
    "集团有限公司",
    "（集团）",
    "(集团)",
    "集团",
    "公司",
)
_CONFIDENCE_USCC: Final[float] = 1.0
_CONFIDENCE_NORM_UNIQUE: Final[float] = 0.9
_AMBIGUOUS: Final[str] = "ambiguous"
_UNRESOLVED: Final[str] = "unresolved"

_SQL_BY_USCC = "SELECT entity_id, uscc, name, name_norm FROM node_company WHERE uscc = %s LIMIT 2"
_SQL_BY_NORM = (
    "SELECT entity_id, uscc, name, name_norm FROM node_company WHERE name_norm = %s ORDER BY entity_id LIMIT 5"
)


def normalize_cn_company_name(raw: str) -> str:
    """中文名规范化：去空白/全角括号转半角/剥组织形式后缀 → name_norm（可迭代细化，禁倒挂真源）。"""
    name = (raw or "").strip()
    name = name.replace("（", "(").replace("）", ")")
    name = re.sub(r"\s+", "", name)
    changed = True
    while changed and name:
        changed = False
        for suffix in _ORG_SUFFIXES:
            if name.endswith(suffix) and len(name) > len(suffix):
                name = name[: -len(suffix)]
                changed = True
    return name


@dataclass(frozen=True)
class CompanyEnrichmentProposal:
    """单条公司富化提案（只描述，不施写；四态见 INVARIANTS）。"""

    holder_name: str
    name_norm: str
    verdict: str  # uscc_direct / norm_unique / ambiguous / unresolved
    confidence: float
    matched_entity_id: str = ""
    matched_uscc: str = ""
    candidates: list[dict[str, str]] = field(default_factory=list)
    evidence: dict[str, str] = field(default_factory=dict)


def propose_company_enrichment(
    conn: psycopg2.extensions.connection,
    holder_names: list[str],
    *,
    uscc_hints: dict[str, str] | None = None,
) -> list[CompanyEnrichmentProposal]:
    """批量出公司富化提案（只读 SELECT；每名一提案，输入顺序保持）。

    uscc_hints: 上游已知 名称→uscc 直键（如来自 A 层结构化字段），命中即 confidence 1.0。
    """
    proposals: list[CompanyEnrichmentProposal] = []
    hints = uscc_hints or {}
    with conn.cursor() as cur:
        for raw in holder_names:
            norm = normalize_cn_company_name(raw)
            hint_uscc = hints.get(raw) or hints.get(norm)
            if hint_uscc:
                cur.execute(_SQL_BY_USCC, (hint_uscc,))
                rows = cur.fetchall()
                if rows:
                    row = rows[0]
                    proposals.append(
                        CompanyEnrichmentProposal(
                            holder_name=raw,
                            name_norm=norm,
                            verdict="uscc_direct",
                            confidence=_CONFIDENCE_USCC,
                            matched_entity_id=str(row[0]),
                            matched_uscc=str(row[1]),
                            evidence={"source": "uscc_hint"},
                        )
                    )
                    continue
            cur.execute(_SQL_BY_NORM, (norm,))
            rows = cur.fetchall()
            if len(rows) == 1:
                row = rows[0]
                proposals.append(
                    CompanyEnrichmentProposal(
                        holder_name=raw,
                        name_norm=norm,
                        verdict="norm_unique",
                        confidence=_CONFIDENCE_NORM_UNIQUE,
                        matched_entity_id=str(row[0]),
                        matched_uscc=str(row[1] or ""),
                        evidence={"name_norm": norm},
                    )
                )
            elif len(rows) > 1:
                proposals.append(
                    CompanyEnrichmentProposal(
                        holder_name=raw,
                        name_norm=norm,
                        verdict=_AMBIGUOUS,
                        confidence=0.0,
                        candidates=[{"entity_id": str(r[0]), "uscc": str(r[1] or ""), "name": str(r[2])} for r in rows],
                        evidence={"rule": "multi_name_norm_hit", "hits": str(len(rows))},
                    )
                )
            else:
                proposals.append(
                    CompanyEnrichmentProposal(
                        holder_name=raw,
                        name_norm=norm,
                        verdict=_UNRESOLVED,
                        confidence=0.0,
                        evidence={"rule": "no_node_company_row"},
                    )
                )
    return proposals


def propose_person_identity(
    name: str,
    *,
    birth_year: int | None = None,
    career_track_hash: str | None = None,
    company_overlap: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    """人物概率消歧提案（骨架占位，恒返回 NotReady——三证据立法见下）。

    立法（设计真源 §4.1/§7）：合并两"同名"人物记录须**三证据齐二强**——
    ①出生年一致 ②任职轨迹 hash 一致 ③关联公司交集非空。缺证据合并=假边=假信号
    （八成工作量在消歧，宁挂起勿错并）。实现随 B 层（招股书董监高简历）富化批另落。
    """
    evidence = {
        "birth_year": birth_year is not None,
        "career_track_hash": bool(career_track_hash),
        "company_overlap": bool(company_overlap),
    }
    strong = sum(1 for ok in evidence.values() if ok)
    return {
        "name": name,
        "status": "not_ready",
        "reason": "person probabilistic merge 骨架占位（C122）；实现随 B 层富化批",
        "evidence_present": evidence,
        "strong_evidence_count": strong,
        "merge_allowed_if": "三证据立法（任二强证据+人工复核）——实现另批",
    }


if __name__ == "__main__":  # pragma: no cover — 冒烟：规范化自检（零连接零写）
    print(normalize_cn_company_name("江苏济川控股集团有限公司"))
    print(normalize_cn_company_name("济川控股（集团）股份有限公司"))
