# [MODULE] scripts.industry_graph.import_ckg_dataset
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 量化消费侧(ig_fact 多跳传导查询); 夜班 SOP §4.9 数据渠道①
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全量落 ig_fact 事实层(不碰 ig_node/ig_edge/ig_chain 防污染现有链结构); source='ckg_2021' 统一标记; as_of='2021-10-26'(CKG 数据实态时点, PIT 诚实); UNIQUE(subject,relation,object,as_of,source) 幂等; 产品/行业名去首尾空白
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源目录缺失->退出码2; 单文件解析失败->打印计数继续; PG失败->抛出
# [TTL] permanent
# M10豁免: manual STARTUP 一次性导入脚本
"""ChainKnowledgeGraph 数据集导入（SOP industry_chain_data_audit_sop §4.9 数据渠道①）。

来源: https://github.com/liuhuanyong/ChainKnowledgeGraph (2021-10 构建, 769★)
规模: 4,654 上市公司 / 511 申万行业 / 95,559 产品 / 110,153 产品-产品边 /
      53,785 公司-主营产品边(带 rel_weight 营收占比) / 4,430 公司-行业 / 480 行业树

映射(全部落 ig_fact 事实层):
    company_industry -> relation='belongs_to_sector' (subject=symbol, object=行业名)
    industry_industry -> relation='sector_parent_of' (下级行业 -> 上级行业)
    industry_up      -> relation='supplies_to' (行业级上游聚合, value=完整ups JSON)
    product          -> relation='product_def' (产品存在性登记, 防歧义锚)
    company_product  -> relation='produces' (value=rel_weight 营收占比)
    product_product  -> rel 映射: 上游材料->'supplies_to' / 下游产品->'product_downstream_of' /
                        产品小类->'subtype_of' (subject=小类, object=大类)

PIT: source='ckg_2021', as_of='2021-10-26' (CKG 最后数据 commit 日)。

用法::

    python scripts/industry_graph/import_ckg_dataset.py [--src DIR] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from psycopg2.extras import execute_values

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SOURCE_TAG = "ckg_2021"
AS_OF = "2021-10-26"
DEFAULT_SRC = r"E:\数据下载\CKG_tmp\ChainKnowledgeGraph-main\data"
_BATCH = 5000


def load_jsonl(p: Path) -> list[dict]:
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _clean(s: str | None) -> str:
    return (s or "").strip()


def build_facts(src: Path) -> list[tuple]:
    """返回 ig_fact 行元组列表: (subject, relation, object, value, confidence, market)。"""
    facts: list[tuple] = []
    skipped = {"cp_nosuffix": 0, "pp_badrel": 0}

    # 1. 公司-行业 -> belongs_to_sector
    for it in load_jsonl(src / "company_industry.json"):
        sym = _clean(it.get("company_code"))
        ind = _clean(it.get("industry_name"))
        if not sym or not ind:
            continue
        facts.append((sym, "belongs_to_sector", ind, None, 0.85, "cn"))

    # 2. 行业树 -> sector_parent_of (下级 -> 上级)
    for it in load_jsonl(src / "industry_industry.json"):
        child, parent = _clean(it.get("from_industry")), _clean(it.get("to_industry"))
        if child and parent and child != parent:
            facts.append((child, "sector_parent_of", parent, None, 0.85, "cn"))

    # 3. 行业上游聚合 -> supplies_to (行业级, value=完整聚合 JSON)
    for it in load_jsonl(src / "industry_up.json"):
        ind = _clean(it.get("industry"))
        ups = it.get("ups") or {}
        if not ind or not ups:
            continue
        # 取 top-1 上游作主 object(可成边), 完整聚合存 value
        top = max(ups.items(), key=lambda kv: kv[1])
        facts.append((top[0], "supplies_to", ind, json.dumps(ups, ensure_ascii=False), 0.6, "cn"))

    # 4. 产品存在性 -> product_def
    for it in load_jsonl(src / "product.json"):
        name = _clean(it.get("name"))
        if name:
            facts.append((name, "product_def", name, None, 0.85, "cn"))

    # 5. 公司-主营产品 -> produces (value=营收占比)
    for it in load_jsonl(src / "company_product.json"):
        sym = _clean(it.get("company_code"))
        prod = _clean(it.get("product_name"))
        w = it.get("rel_weight")
        if not sym or not prod:
            continue
        if "." not in sym:  # 无交易所后缀的行(如旧code)跳过
            skipped["cp_nosuffix"] += 1
            continue
        val = f"{float(w):.6f}" if w is not None and str(w).strip() != "" else None
        facts.append((sym, "produces", prod, val, 0.85, "cn"))

    # 6. 产品-产品 -> supplies_to / product_downstream_of / subtype_of
    # 方向语义（2026-09-07 实测源数据核实）：
    #   上游材料: "from 的上游材料是 to"（红豆薏米仁汤→冰糖）→ 供应方向 to→from，
    #             故 supplies_to 映射为 (to, supplies_to, from)
    #   下游产品: "from 的下游产品是 to"（生丝→丝绸）→ 供应方向 from→to，保持 from→to
    #   产品小类: "from 的产品小类是 to"（解决方案→RFID解决方案）→ to 是 from 的子类，
    #             故 subtype_of 映射为 (to, subtype_of, from)
    rel_map = {"上游材料": "supplies_to", "下游产品": "product_downstream_of", "产品小类": "subtype_of"}
    swap = {"上游材料", "产品小类"}
    for it in load_jsonl(src / "product_product.json"):
        f, t, rel = _clean(it.get("from_entity")), _clean(it.get("to_entity")), _clean(it.get("rel"))
        m = rel_map.get(rel)
        if not f or not t or not m:
            skipped["pp_badrel"] += 1
            continue
        subj, obj = (t, f) if rel in swap else (f, t)
        facts.append((subj, m, obj, None, 0.6, "cn"))

    print(f"[facts] built {len(facts)}, skipped={skipped}")
    return facts


def write_facts(facts: list[tuple], dry_run: bool = False) -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    written = 0
    try:
        with conn.cursor() as cur:
            for i in range(0, len(facts), _BATCH):
                batch = facts[i : i + _BATCH]
                execute_values(
                    cur,
                    """
                    INSERT INTO ig_fact (subject, relation, object, value, confidence,
                                         as_of, source, market)
                    VALUES %s
                    ON CONFLICT (subject, relation, object, as_of, source) DO NOTHING
                    """,
                    [(s, r, o, v, c, AS_OF, SOURCE_TAG, m) for s, r, o, v, c, m in batch],
                )
                written += len(batch)
                print(f"  batch {i // _BATCH + 1}: cumulative {written}")
        conn.commit()
    finally:
        conn.close()
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="ChainKnowledgeGraph 数据集导入 ig_fact")
    parser.add_argument("--src", default=DEFAULT_SRC)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.is_dir():
        print(f"[ERROR] 源目录不存在: {src}")
        return 2

    facts = build_facts(src)
    if args.dry_run:
        print(f"[dry-run] {len(facts)} facts, no write")
        return 0
    written = write_facts(facts)
    print(f"[OK] ig_fact 写入完成: attempted={written} (冲突行自动跳过)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
