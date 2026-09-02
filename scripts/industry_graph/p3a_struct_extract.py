# [MODULE] scripts.industry_graph.p3a_struct_extract
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer
# [CONSUMERS] 主题联动; 传导因子; 图谱可视化
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重跑(ON CONFLICT); 自动抽取置信度0.6留人工抽检口; 公司名仅匹配>=3字简称/全称防误配; 节点按链×环节合并
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH名录为空->退出码2; 单文档失败->跳过计数
# [TTL] permanent
"""T6/P3a：产业链结构化抽取（规则 + 公司名录匹配，零 LLM 全自动版）。

从已提取文本（panorama_pdf 的 OCR/文字层）中抽取三级结构：
  链（文档标题归一，如"光伏产业链"）
  → 环节（按 上游/中游/下游/设备/材料 标记分段，节点为 链×环节 粒度）
  → 公司（c1_market.stock_basic 名录在分段文本中的精确出现，>=3字简称或全称）

产出 ig_chain / ig_node / ig_edge(structure) / ig_node_company，
全部 source='p3a_auto'、confidence=0.6，供后续人工抽检升级。

用法::

    python scripts/industry_graph/p3a_struct_extract.py
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from psycopg2.extras import execute_values

from zephyr.data import ch_writer
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SOURCE_TAG = "p3a_auto"
_TIER_RE = re.compile(r"(上游|中游|下游|设备|材料|辅材|零部件|原材料)")
# 链名清洗（按序执行）：编号前缀、日期/页码前缀、后缀关键词截断、年份前缀、尾巴残留
_PREFIX_RULES = [
    re.compile(r"^\d{1,2}新增[-—–]?"),  # 02新增- / 04新增-
    re.compile(r"^新增[-—–]?"),
    re.compile(r"^(20\d{2})?[-—–]?\d{1,4}[-—–]"),  # 2026182- / 38- / 2024-
    re.compile(r"^(20\d{2})?年\d{1,3}页"),  # 2026年29页 / 年307页（页字必需，防误吃"年3月"）
    re.compile(r"^(20\d{2})?年\d{0,2}月?[:：]?"),  # 2026年2月： / 年2月：
    re.compile(r"^\d{1,2}月[:：]?"),  # 月： 残留
    re.compile(r"^\d{4,6}[-—–]?(?!年)"),  # 202437- / 202505-（保留"2024年"开头给年份规则）
]
_SUFFIX_CUT = re.compile(
    r"(产业链)?(全景图|产业链图|图谱|图解|全景|分析|研究|专题|梳理|详情|白皮书|蓝皮书|报告|洞察|指南|手册|图鉴|图集|行业深度|深度报告).*$",
    re.IGNORECASE,
)
_YEAR_LEAD = re.compile(r"^20\d{2}年?")
_TAIL_RULES = [re.compile(r"标的$"), re.compile(r"[:：]$"), re.compile(r"产业链大$")]
_MIN_NAME_LEN = 3


def load_registry() -> dict[str, str]:
    """公司名(简称>=3字/全称) → symbol_canonical。"""
    tsv = ch_writer.query(
        "SELECT symbol_canonical, name, fullname FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL"
    )
    reg: dict[str, str] = {}
    for line in tsv.strip().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        sym, name, fullname = parts[0], parts[1], parts[2]
        if len(name) >= _MIN_NAME_LEN:
            reg.setdefault(name, sym)
        if len(fullname) >= _MIN_NAME_LEN:
            reg.setdefault(fullname, sym)
    return reg


def clean_chain_name(title: str) -> str:
    name = (title or "").strip()
    name = re.sub(r"\.(pdf|png|jpe?g)$", "", name, flags=re.IGNORECASE)
    for _ in range(2):  # 前缀规则可叠加（如"年307页2024年..."），跑两遍
        for pat in _PREFIX_RULES:
            name = pat.sub("", name).strip()
    name = _SUFFIX_CUT.sub("", name)
    name = _YEAR_LEAD.sub("", name).strip()
    for pat in _TAIL_RULES:
        name = pat.sub("", name).strip()
    name = name.strip(" -_（）()：:，,")
    return name if 2 <= len(name) <= 30 else ""


def segment_tiers(text: str) -> dict[str, str]:
    """按上/中/下游等标记分段。返回 {tier: 段落文本}。无标记全文归 'unspecified'。"""
    sections: dict[str, list[str]] = defaultdict(list)
    current = "unspecified"
    for line in text.splitlines():
        m = _TIER_RE.search(line)
        if m and len(line) <= 40:  # 短行含环节词视为小节标题
            current = m.group(1)
            continue
        sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items() if v}


def main() -> int:
    reg = load_registry()
    if not reg:
        print("[ERROR] ClickHouse 公司名录为空")
        return 2
    print(f"[T6] 公司名录 {len(reg)} 条")
    # 按首字索引加速匹配
    by_first: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for name, sym in reg.items():
        by_first[name[0]].append((name, sym))

    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, title, year, bundle, extracted_text_path
            FROM ig_document
            WHERE doc_type = 'panorama_pdf' AND is_canonical AND NOT excluded
              AND parse_status IN ('extracted', 'ocr_done') AND extracted_text_path IS NOT NULL
            """
        )
        docs = cur.fetchall()
    print(f"[T6] 待抽取文档 {len(docs)} 份")

    chains: dict[str, dict] = {}
    nodes: dict[str, dict] = {}
    edges: set[tuple[str, str]] = set()
    node_companies: dict[tuple[str, str], dict] = {}
    skipped = 0

    for doc_id, title, year, bundle, text_path in docs:
        try:
            text = open(text_path, encoding="utf-8").read()
        except OSError:
            skipped += 1
            continue
        chain_name = clean_chain_name(title or "")
        if not chain_name:
            skipped += 1
            continue
        chain_id = "CH-" + hashlib.md5(chain_name.encode("utf-8")).hexdigest()[:12]
        ch = chains.setdefault(chain_id, {"name": chain_name, "category": bundle, "year": year})
        if year and (ch["year"] is None or year > ch["year"]):
            ch["year"] = year

        tiers = segment_tiers(text)
        present_tiers = []
        for tier, seg in tiers.items():
            node_id = "ND-" + hashlib.md5(f"{chain_name}|{tier}".encode("utf-8")).hexdigest()[:12]
            nodes.setdefault(node_id, {"chain_id": chain_id, "name": f"{chain_name}-{tier}", "tier": tier})
            present_tiers.append((tier, node_id))
            # 公司匹配：扫描段落中出现的首字集合
            for ch0 in set(seg):
                for name, sym in by_first.get(ch0, ()):  # noqa: B905
                    if name in seg:
                        key = (node_id, sym)
                        ent = node_companies.setdefault(
                            key,
                            {"role": "mentioned", "evidence": (title or "")[:200], "source_doc": doc_id, "docs": set()},
                        )
                        ent["docs"].add(doc_id)
        # 结构边：按业界通用流向串联已出现环节
        flow = ["原材料", "材料", "辅材", "零部件", "上游", "中游", "下游"]
        ordered = sorted(present_tiers, key=lambda t: flow.index(t[0]) if t[0] in flow else 99)
        for (t1, n1), (t2, n2) in zip(ordered, ordered[1:]):
            if t1 != "unspecified" and t2 != "unspecified" and n1 != n2:
                edges.add((n1, n2))

    print(f"[T6] 链={len(chains)} 节点={len(nodes)} 结构边={len(edges)} 环节-公司={len(node_companies)} 跳过={skipped}")

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ig_chain (chain_id, name, category, version_year, source_note)
            VALUES %s
            ON CONFLICT (chain_id) DO UPDATE SET
                category = EXCLUDED.category,
                version_year = GREATEST(ig_chain.version_year, EXCLUDED.version_year),
                updated_at = now()
            """,
            [(cid, c["name"], c["category"], c["year"], SOURCE_TAG) for cid, c in chains.items()],
            page_size=500,
        )
        execute_values(
            cur,
            """
            INSERT INTO ig_node (node_id, chain_id, name, tier)
            VALUES %s
            ON CONFLICT (node_id) DO NOTHING
            """,
            [(nid, n["chain_id"], n["name"], n["tier"]) for nid, n in nodes.items()],
            page_size=500,
        )
        execute_values(
            cur,
            """
            INSERT INTO ig_edge (from_node, to_node, edge_type, source_doc)
            VALUES %s
            ON CONFLICT (from_node, to_node, edge_type) DO NOTHING
            """,
            [(f, t, "structure", SOURCE_TAG) for f, t in edges],
            page_size=500,
        )
        execute_values(
            cur,
            """
            INSERT INTO ig_node_company (node_id, symbol, role, confidence, evidence_text, source_doc)
            VALUES %s
            ON CONFLICT (node_id, symbol) DO NOTHING
            """,
            [
                (nid, sym, v["role"], 0.85 if len(v["docs"]) >= 2 else 0.6, v["evidence"], v["source_doc"])
                for (nid, sym), v in node_companies.items()
            ],
            page_size=1000,
        )
    conn.commit()
    conn.close()
    print("[T6] 完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
