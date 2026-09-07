# [MODULE] scripts.industry_graph.websearch_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer (stock_basic 反查)
# [CONSUMERS] 夜班 SOP industry_chain_data_audit_sop §5 全轮次写入(唯一合法通道)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 写入唯一通道: 全部走 ingest 子命令(禁手写 SQL); 批次=单事务全成全败; 幂等(UNIQUE 锚 ON CONFLICT); 硬校验九条(SOP §5): source_doc 三段式/confidence<=0.7(websearch)/symbol 正则+cn 反查 stock_basic/词表白名单(tier/category/edge_type v2)/node.name 无 -tier 后缀残留/backup 幂等; PIT 三时间戳 websearch 边必填
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->退出码2; 批次校验失败->退出码3+逐条错误清单(不落库); stock_basic 不可达->cn symbol 校验降级 warn
# [TTL] permanent
# M10豁免: manual STARTUP 夜班工具
"""夜班写入工具（SOP industry_chain_data_audit_sop §5，#ARCH-308 后续）。

子命令::

    stats                 七表计数+关键缺口统计(JSON)
    backup                七表库内备份(幂等,当日表已存在则跳过)
    find-chain --name X   模糊找链(前5相似)
    ingest --batch PATH   校验+事务写入批次 JSON

批次 JSON 格式与硬校验规则见 SOP §5。websearch/corpus_rag 来源强制:
source_doc="查询词|URL|YYYY-MM-DD"; company_edge 必带 valid_from/as_of(PIT)。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from psycopg2.extras import execute_values

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# ---- 词表(SOP §4.7/§4.8) ----
TIERS = {"上游", "中游", "下游", "设备", "材料", "零部件", "原材料", "辅材", "unspecified"}
TIERS_NEW = {"上游", "中游", "下游", "设备", "材料"}  # websearch 只许前 5 值
CATEGORIES = {
    "半导体", "消费电子", "元件", "光学光电子", "计算机设备", "机械设备", "电力设备", "汽车",
    "国防军工", "家用电器", "基础化工", "有色金属", "钢铁", "建筑材料", "石油石化", "医药生物",
    "食品饮料", "纺织服饰", "商贸零售", "社会服务", "美容护理", "轻工制造", "农林牧渔",
    "软件开发", "互联网服务", "通信服务", "通信设备", "游戏", "传媒", "银行", "非银金融",
    "房地产", "建筑装饰", "交通运输", "公用事业", "环保", "综合",
}
EDGE_TYPES_V2 = {"supplies_to", "customer_of", "competitor_of", "partners_with", "produces", "belongs_to_sector", "structure", "supply"}
NODE_SUFFIX_RE = re.compile(r"-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$")
SYMBOL_CN_RE = re.compile(r"^\d{6}\.(SH|SZ|BJ)$")
SYMBOL_GLOBAL_RE = re.compile(r"^[A-Z0-9]{1,6}\.(US|KS|TW|T|HK)$")
SOURCEDOC_RE = re.compile(r"^[^|]+\|[^|]+\|\d{4}-\d{2}-\d{2}$")

_ALL_TABLES = ("ig_chain", "ig_node", "ig_edge", "ig_node_company", "ig_document", "ig_company_edge", "ig_company_metric", "ig_chunk", "ig_fact")
_DATE = None


def _today() -> str:
    global _DATE
    if _DATE is None:
        from datetime import date

        _DATE = date.today().isoformat()
    return _DATE


def _chain_id(name: str) -> str:
    return f"CH-{hashlib.md5(name.encode('utf-8')).hexdigest()[:12]}"


def _node_id(chain_id: str, name: str, tier: str) -> str:
    return f"ND-{hashlib.md5(f'{chain_id}|{name}|{tier}'.encode('utf-8')).hexdigest()[:12]}"


def _load_stock_basic() -> set[str] | None:
    try:
        from zephyr.data import ch_writer

        tsv = ch_writer.query(
            "SELECT symbol_canonical FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL"
        )
        return {ln.split("\t")[0] for ln in tsv.strip().splitlines()[1:] if "\t" in ln}
    except Exception as e:  # noqa: BLE001 — CH 不可达降级 warn
        print(f"[WARN] stock_basic 反查降级: {e}")
        return None


def cmd_stats() -> int:
    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    out: dict = {}
    for t in _ALL_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        out[t] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM ig_chain WHERE version_year<=2023 OR version_year IS NULL")
    out["chains_stale_or_noyear"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM ig_chain WHERE status='deprecated'")
    out["chains_deprecated"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT symbol) FROM ig_node_company WHERE market='cn'")
    chained = cur.fetchone()[0]
    out["cn_chained_companies"] = chained
    out["cn_anchored_nodes"] = None
    conn.close()
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


def cmd_backup() -> int:
    from datetime import date

    tag = date.today().strftime("%Y%m%d")
    # CREATE TABLE 需 superuser（writer 角色无建表权，实测 2026-09-07）
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    cur = conn.cursor()
    made = []
    for t in _ALL_TABLES:
        bak = f"{t}_bak_{tag}"
        cur.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", (bak,)
        )
        if cur.fetchone()[0] == 0:
            cur.execute(f"CREATE TABLE {bak} AS SELECT * FROM {t}")
            made.append(bak)
    conn.close()
    print(json.dumps({"backed_up": made, "tag": tag}, ensure_ascii=False))
    return 0


def cmd_find_chain(name: str) -> int:
    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT chain_id, name, category, version_year, status FROM ig_chain "
        "WHERE name LIKE %s ORDER BY length(name) LIMIT 5",
        (f"%{name}%",),
    )
    rows = [list(r) for r in cur.fetchall()]
    conn.close()
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    return 0


def _validate_records(records: list[dict], stocks: set[str] | None) -> list[str]:
    errs: list[str] = []
    for i, r in enumerate(records):
        typ = r.get("type")
        sd = r.get("source_doc", "")
        src = r.get("source", "")
        idx = f"record[{i}]"
        # 硬校验 1: source_doc 三段式(websearch/corpus_rag 强制)
        if src in ("websearch", "corpus_rag") and not SOURCEDOC_RE.match(sd):
            errs.append(f"{idx}: source_doc 非三段式: {sd!r}")
        # 硬校验 2: confidence 上限
        if src in ("websearch", "corpus_rag") and (r.get("confidence") or 0) > 0.7:
            errs.append(f"{idx}: confidence>{0.7}: {r.get('confidence')}")
        market = r.get("market", "cn")
        # 硬校验 3: symbol 正则
        for k in ("symbol", "from_symbol", "to_symbol"):
            sym = r.get(k)
            if not sym:
                continue
            if market == "cn":
                if not SYMBOL_CN_RE.match(sym):
                    errs.append(f"{idx}: cn symbol 非法: {sym}")
                elif stocks is not None and sym not in stocks:
                    errs.append(f"{idx}: cn symbol 不在 stock_basic: {sym}")
            elif market == "global":
                if not SYMBOL_GLOBAL_RE.match(sym):
                    errs.append(f"{idx}: global symbol 非法: {sym}")
        # 硬校验 7: tier 词表(websearch 禁 unspecified)
        if typ == "node":
            tier = r.get("tier")
            if tier and tier not in TIERS:
                errs.append(f"{idx}: tier 非词表: {tier}")
            if tier and src in ("websearch", "corpus_rag") and tier not in TIERS_NEW:
                errs.append(f"{idx}: websearch 禁 tier={tier}")
            if NODE_SUFFIX_RE.search(r.get("name", "")):
                errs.append(f"{idx}: node.name 含 -tier 后缀残留: {r.get('name')}")
        # 硬校验 8: category
        if typ == "chain":
            cat = r.get("category")
            if cat and cat not in CATEGORIES and cat != "综合":
                errs.append(f"{idx}: category 非申万词表: {cat}")
        if typ in ("node_edge", "company_edge"):
            et = r.get("edge_type", r.get("relation"))
            if et and et not in EDGE_TYPES_V2:
                errs.append(f"{idx}: edge_type 非 v2 词表: {et}")
        # PIT: websearch company_edge 必带
        if typ == "company_edge" and src == "websearch":
            for k in ("valid_from", "as_of"):
                if not r.get(k):
                    errs.append(f"{idx}: company_edge 缺 PIT 字段 {k}")
    return errs


def cmd_ingest(batch_path: str) -> int:
    bp = Path(batch_path)
    if not bp.is_file():
        print(f"[ERROR] 批次文件不存在: {bp}")
        return 2
    batch = json.loads(bp.read_text(encoding="utf-8"))
    records = batch.get("records", [])
    stocks = _load_stock_basic()
    errs = _validate_records(records, stocks)
    if errs:
        print(f"[REJECTED] {len(errs)} 校验错误(未落库):")
        for e in errs[:30]:
            print(f"  - {e}")
        return 3

    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    counts: dict[str, int] = {}
    try:
        for r in records:
            typ = r["type"]
            counts[typ] = counts.get(typ, 0) + 1
            sd, src, mkt = r.get("source_doc", ""), r.get("source", "websearch"), r.get("market", "cn")
            if typ == "chain":
                cid = _chain_id(r["name"])
                cur.execute(
                    """INSERT INTO ig_chain (chain_id,name,category,version_year,market,status,source_note,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,'active',%s,now(),now())
                    ON CONFLICT (chain_id) DO UPDATE SET updated_at=now(), category=COALESCE(EXCLUDED.category,ig_chain.category)""",
                    (cid, r["name"], r.get("category"), r.get("version_year"), mkt, sd or src),
                )
            elif typ == "node":
                cid = _chain_id(r["chain_name"])
                nid = _node_id(cid, r["name"], r.get("tier", ""))
                cur.execute(
                    """INSERT INTO ig_node (node_id,chain_id,name,tier,aliases,description,market,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (node_id) DO UPDATE SET updated_at=now(), tier=COALESCE(NULLIF(EXCLUDED.tier,''),ig_node.tier)""",
                    (nid, cid, r["name"], r.get("tier"), r.get("aliases"), r.get("description"), mkt),
                )
            elif typ == "node_edge":
                cid = _chain_id(r["chain_name"])
                fn, tn = _node_id(cid, r["from_node"], ""), _node_id(cid, r["to_node"], "")
                cur.execute(
                    """INSERT INTO ig_edge (from_node,to_node,edge_type,source_doc,market,created_at)
                    VALUES (%s,%s,%s,%s,%s,now()) ON CONFLICT (from_node,to_node,edge_type) DO NOTHING""",
                    (fn, tn, r.get("edge_type", "structure"), sd, mkt),
                )
            elif typ == "node_company":
                cid = _chain_id(r["chain_name"])
                nid = _node_id(cid, r["node_name"], "")
                cur.execute(
                    """INSERT INTO ig_node_company (node_id,symbol,role,confidence,evidence_text,source_doc,market,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (node_id,symbol) DO UPDATE SET updated_at=now(),
                      confidence=GREATEST(ig_node_company.confidence,EXCLUDED.confidence),
                      evidence_text=COALESCE(EXCLUDED.evidence_text,ig_node_company.evidence_text)""",
                    (nid, r["symbol"], r.get("role"), r.get("confidence", 0.5), r.get("evidence_text"), sd, mkt),
                )
            elif typ == "company_edge":
                cur.execute(
                    """INSERT INTO ig_company_edge (from_symbol,to_symbol,year,product,weight,weight_type,source,source_doc,
                       from_name,to_name,amount,rank,market,created_at,valid_from,valid_to,as_of,evidence_type,revenue_pct,subsidiary,relevance,transmission_type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (from_symbol,to_symbol,year,source) DO UPDATE SET
                      product=COALESCE(EXCLUDED.product,ig_company_edge.product),
                      valid_from=COALESCE(EXCLUDED.valid_from,ig_company_edge.valid_from),
                      as_of=COALESCE(EXCLUDED.as_of,ig_company_edge.as_of)""",
                    (r["from_symbol"], r.get("to_symbol", ""), r["year"], r.get("product"), r.get("weight"),
                     r.get("weight_type"), src, sd, r.get("from_name"), r.get("to_name"), r.get("amount"),
                     r.get("rank"), mkt, r.get("valid_from"), r.get("valid_to"), r.get("as_of"),
                     r.get("evidence_type"), r.get("revenue_pct"), r.get("subsidiary"), r.get("relevance"),
                     r.get("transmission_type")),
                )
            elif typ == "metric":
                cur.execute(
                    """INSERT INTO ig_company_metric (symbol,year,metric,value,value_aux,source,market,created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,now())
                    ON CONFLICT (symbol,year,metric,source) DO NOTHING""",
                    (r["symbol"], r["year"], r["metric"], r.get("value"), r.get("value_aux"), src, mkt),
                )
            elif typ == "fact":
                cur.execute(
                    """INSERT INTO ig_fact (subject,relation,object,value,evidence_chunk_id,confidence,as_of,source,market,created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,now())
                    ON CONFLICT (subject,relation,object,as_of,source) DO NOTHING""",
                    (r["subject"], r["relation"], r["object"], r.get("value"), r.get("evidence_chunk_id"),
                     r.get("confidence", 0.5), r.get("as_of"), src, mkt),
                )
            else:
                raise ValueError(f"未知 record type: {typ}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print(json.dumps({"batch": batch.get("batch_id"), "written": counts}, ensure_ascii=False))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="夜班写入工具(SOP §5)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stats")
    sub.add_parser("backup")
    fc = sub.add_parser("find-chain")
    fc.add_argument("--name", required=True)
    ing = sub.add_parser("ingest")
    ing.add_argument("--batch", required=True)
    args = p.parse_args()

    try:
        if args.cmd == "stats":
            return cmd_stats()
        if args.cmd == "backup":
            return cmd_backup()
        if args.cmd == "find-chain":
            return cmd_find_chain(args.name)
        if args.cmd == "ingest":
            return cmd_ingest(args.batch)
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
