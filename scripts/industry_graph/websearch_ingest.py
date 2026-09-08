# [MODULE] scripts.industry_graph.websearch_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer (stock_basic 反查)
# [CONSUMERS] 夜班 SOP industry_chain_data_audit_sop §5 全轮次写入(唯一合法通道)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 写入唯一通道: 全部走 ingest 子命令(禁手写 SQL); 批次=单事务全成全败; 幂等(UNIQUE 锚 ON CONFLICT); 硬校验(SOP §5): source_doc 三段式/confidence<=0.7(websearch)/symbol 正则+cn 反查 stock_basic/词表白名单(tier/category/edge_type v2)/node.name 无 -tier 后缀残留/backup 幂等; UNLISTED:UE-xxx 唯一合法格式(旧格式公司名直写拒绝,§4.10); unlisted_entity 记录 status 枚举+listed_symbol 真代码格式校验; PIT 三时间戳 websearch 边必填; 节点引用(node/node_company/node_edge)按(链+名)查库解析存量真实ID(存量采购包节点非md5方案,重算ID会FK违规/造重复行,2026-09-08修复); chain 支持 status/merged_into(deprecated 须带 merged_into,幂等 append 不覆盖原 source_note,2026-09-08 裁定执行)
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
    controller ACTION --session S  单夜单总控锁(acquire/release/status,SOP §3 总则 9)

批次 JSON 格式与硬校验规则见 SOP §5。websearch/corpus_rag 来源强制:
source_doc="查询词|URL|YYYY-MM-DD"; company_edge 必带 valid_from/as_of(PIT)。
unlisted_entity 记录(§4.10): name/country/status/listed_symbol,编码表登记与
上市标定走本通道;UNLISTED symbol 唯一合法格式=UNLISTED:UE-{12hex}。
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
    "国防军工", "家用电器", "基础化工", "有色金属", "钢铁", "建筑材料", "石油石化", "煤炭", "医药生物",
    "食品饮料", "纺织服饰", "商贸零售", "社会服务", "美容护理", "轻工制造", "农林牧渔",
    "软件开发", "互联网服务", "通信服务", "通信设备", "游戏", "传媒", "银行", "非银金融",
    "房地产", "建筑装饰", "交通运输", "公用事业", "环保", "综合",
}
CHAIN_STATUSES = {"active", "deprecated"}  # SOP §4.6 ig_chain.status 封闭枚举
MERGED_INTO_RE = re.compile(r"^CH-[0-9a-f]{12}$")
EDGE_TYPES_V2 = {"supplies_to", "customer_of", "competitor_of", "partners_with", "produces", "belongs_to_sector", "structure", "supply"}
NODE_SUFFIX_RE = re.compile(r"-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$")
SYMBOL_CN_RE = re.compile(r"^\d{6}\.(SH|SZ|BJ)$")
SYMBOL_GLOBAL_RE = re.compile(r"^[A-Z0-9]{1,6}\.(US|KS|TW|T|HK|DE|LN|JP|SM)$")
# UNLISTED 唯一合法格式=编码表主键引用(SOP §4.10,2026-09-08 开放问题9裁定:
# 旧格式 UNLISTED:公司名 禁止,防双格式并存致夜班模型幻觉/漂移)
SYMBOL_UNLISTED_RE = re.compile(r"^UNLISTED:UE-[0-9a-f]{12}$")
SOURCEDOC_RE = re.compile(r"^[^|]+\|[^|]+\|\d{4}-\d{2}-\d{2}$")

_ALL_TABLES = ("ig_chain", "ig_node", "ig_edge", "ig_node_company", "ig_document", "ig_company_edge", "ig_company_metric", "ig_chunk", "ig_fact", "ig_unlisted_entity")
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


def _controller_lock_dir() -> Path:
    return Path(__file__).resolve().parents[2] / ".runtime" / "industry_graph"


def cmd_controller(action: str, session: str, ttl_min: int = 30) -> int:
    """单夜单总控锁(SOP §3 总则 9,2026-09-08 B 项治本)。

    acquire: 抢锁(已锁且未过期->exit 4 报占用者;过期->接管)
    release: 释放(须同 session,防误释放他线)
    status: 查看
    心跳: 每次 ingest 自动续期(锁文件 mtime 即心跳)。
    """
    import time

    lock = _controller_lock_dir() / "controller.lock"
    now = time.time()
    if action == "status":
        if lock.is_file():
            d = json.loads(lock.read_text(encoding="utf-8"))
            age = (now - lock.stat().st_mtime) / 60
            print(json.dumps({**d, "age_min": round(age, 1), "alive": age < ttl_min}, ensure_ascii=False))
        else:
            print(json.dumps({"state": "free"}))
        return 0
    if action == "acquire":
        if lock.is_file():
            d = json.loads(lock.read_text(encoding="utf-8"))
            age = (now - lock.stat().st_mtime) / 60
            if d.get("session") != session and age < ttl_min:
                print(f"[BUSY] 总控锁被占用: {d.get('session')} (age {age:.0f}min < ttl {ttl_min}min)")
                return 4
        _controller_lock_dir().mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps({"session": session, "acquired_at": time.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False), encoding="utf-8")
        print(f"[LOCKED] {session}")
        return 0
    if action == "release":
        if lock.is_file():
            d = json.loads(lock.read_text(encoding="utf-8"))
            if d.get("session") != session:
                print(f"[DENIED] 锁属 {d.get('session')} 非 {session},拒绝释放")
                return 4
            lock.unlink(missing_ok=True)
            print(f"[RELEASED] {session}")
        else:
            print("[FREE] 无锁")
        return 0
    print(f"[ERROR] 未知 action: {action}")
    return 2


def _resolve_node(cur, chain_id: str, name: str) -> str | None:
    """按(链,环节名)解析节点真实 node_id（存量与同批次新写节点统一走此解析）。

    存量采购包节点 ID 非本工具 md5 方案（2026-09-08 实测仅 28/2939 命中），
    重算 ID 会致 node_company FK 违规整批回滚、node 重写造重复行、node_edge
    悬空——引用节点必须查库解析，解析不到（且本批次未先写 node）才报错。
    """
    cur.execute(
        "SELECT node_id FROM ig_node WHERE chain_id=%s AND name=%s "
        "ORDER BY created_at, node_id LIMIT 1",
        (chain_id, name),
    )
    row = cur.fetchone()
    return row[0] if row else None


def _load_stock_basic() -> set[str] | None:
    try:
        from zephyr.data import ch_writer

        tsv = ch_writer.query(
            "SELECT symbol_canonical FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL"
        )
        # ch_writer TSV 无表头且单列无 \t（2026-09-08 实测：旧解析 [1:]+要求含\t
        # 会把 5215 只在市股全集滤成空集，致所有 cn symbol 被误拒）——逐行取第一列
        return {
            ln.strip().split("\t")[0]
            for ln in tsv.strip().splitlines()
            if ln.strip()
        }
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
        # 硬校验 3: symbol 正则(按端点各自市场判定,2026-09-08 跨市场治本:
        # global 边可混端 cn+海外 symbol;单边 market=cn 但 symbol 是海外格式时按
        # 该 symbol 实际市场校验,不再因边级 market 标签误拒合法混端边)
        for k in ("symbol", "from_symbol", "to_symbol"):
            sym = r.get(k)
            if not sym:
                continue
            if SYMBOL_CN_RE.match(sym):
                if stocks is not None and sym not in stocks:
                    errs.append(f"{idx}: cn symbol 不在 stock_basic: {sym}")
            elif SYMBOL_GLOBAL_RE.match(sym):
                pass  # 海外格式合法,按格式判市场
            elif SYMBOL_UNLISTED_RE.match(sym):
                pass  # 未上市实体编码表引用合法(SOP §4.10)
            elif sym.startswith("UNLISTED:"):
                errs.append(f"{idx}: UNLISTED 旧格式(公司名直写)已禁,须先登记编码表换 UNLISTED:UE-xxx: {sym}")
            elif market == "cn":
                errs.append(f"{idx}: cn symbol 非法: {sym}")
            else:
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
            # chain 状态与合并指向(2026-09-08 裁定执行: 碎片链 deprecated 走唯一合法通道)
            st = r.get("status")
            if st is not None and st not in CHAIN_STATUSES:
                errs.append(f"{idx}: status 非法(仅 active/deprecated): {st}")
            mi = r.get("merged_into")
            if mi is not None and not MERGED_INTO_RE.match(mi):
                errs.append(f"{idx}: merged_into 非 chain_id 格式: {mi}")
            if st == "deprecated" and not mi:
                errs.append(f"{idx}: deprecated 链须带 merged_into(SOP §4.6)")
        if typ in ("node_edge", "company_edge"):
            et = r.get("edge_type", r.get("relation"))
            if et and et not in EDGE_TYPES_V2:
                errs.append(f"{idx}: edge_type 非 v2 词表: {et}")
        # PIT: websearch company_edge 必带
        if typ == "company_edge" and src == "websearch":
            for k in ("valid_from", "as_of"):
                if not r.get(k):
                    errs.append(f"{idx}: company_edge 缺 PIT 字段 {k}")
        # 跨市场治本(2026-09-08): company_edge 两端 symbol 必须非空——
        # 禁止新写入留空 symbol 用 name 编码公司(存量修复见 normalize_global_edges)
        if typ == "company_edge" and src in ("websearch", "corpus_rag"):
            if not r.get("from_symbol"):
                errs.append(f"{idx}: company_edge 缺 from_symbol")
            if not r.get("to_symbol"):
                errs.append(f"{idx}: company_edge 缺 to_symbol")
        # 编码表登记校验(SOP §4.10): status 封闭枚举;listed_symbol 非空时必须真代码格式
        if typ == "unlisted_entity":
            st = r.get("status") or "unlisted"
            if st not in ("unlisted", "listed", "merged"):
                errs.append(f"{idx}: unlisted_entity.status 非法(仅 unlisted/listed/merged): {st}")
            ls = r.get("listed_symbol")
            if ls is not None and not (SYMBOL_GLOBAL_RE.match(ls) or SYMBOL_CN_RE.match(ls)):
                errs.append(f"{idx}: unlisted_entity.listed_symbol 非真代码格式: {ls}")
            if not r.get("name"):
                errs.append(f"{idx}: unlisted_entity 缺 name")
            if st == "listed" and not ls:
                errs.append(f"{idx}: unlisted_entity status=listed 须带 listed_symbol(一手来源)")
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
                merged = r.get("merged_into")
                cur.execute(
                    """INSERT INTO ig_chain (chain_id,name,category,version_year,market,status,source_note,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (chain_id) DO UPDATE SET updated_at=now(),
                      category=COALESCE(EXCLUDED.category,ig_chain.category),
                      status=CASE WHEN EXCLUDED.status IS DISTINCT FROM 'active'
                             THEN EXCLUDED.status ELSE ig_chain.status END,
                      source_note=CASE
                        WHEN %s::text IS NOT NULL AND position(%s::text in ig_chain.source_note)=0
                        THEN ig_chain.source_note||' | merged_into:'||%s::text
                        ELSE ig_chain.source_note END""",
                    (cid, r["name"], r.get("category"), r.get("version_year"), mkt,
                     r.get("status") or "active", sd or src, merged, merged, merged),
                )
            elif typ == "node":
                cid = _chain_id(r["chain_name"])
                nid = _resolve_node(cur, cid, r["name"])
                if nid is not None:
                    cur.execute(
                        """UPDATE ig_node SET updated_at=now(),
                             tier=COALESCE(NULLIF(%s,''), ig_node.tier),
                             aliases=COALESCE(%s, ig_node.aliases),
                             description=COALESCE(%s, ig_node.description)
                           WHERE node_id=%s""",
                        (r.get("tier") or "", r.get("aliases"), r.get("description"), nid),
                    )
                else:
                    nid = _node_id(cid, r["name"], r.get("tier", ""))
                    cur.execute(
                        """INSERT INTO ig_node (node_id,chain_id,name,tier,aliases,description,market,created_at,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,now(),now())
                        ON CONFLICT (node_id) DO UPDATE SET updated_at=now(), tier=COALESCE(NULLIF(EXCLUDED.tier,''),ig_node.tier)""",
                        (nid, cid, r["name"], r.get("tier"), r.get("aliases"), r.get("description"), mkt),
                    )
            elif typ == "node_edge":
                cid = _chain_id(r["chain_name"])
                fn, tn = _resolve_node(cur, cid, r["from_node"]), _resolve_node(cur, cid, r["to_node"])
                if fn is None or tn is None:
                    raise ValueError(
                        f"node_edge 端点节点不存在(先在同批次写 node 或确认存量已有): "
                        f"{r['from_node']}->{r['to_node']} (chain={r['chain_name']})"
                    )
                cur.execute(
                    """INSERT INTO ig_edge (from_node,to_node,edge_type,source_doc,market,created_at)
                    VALUES (%s,%s,%s,%s,%s,now()) ON CONFLICT (from_node,to_node,edge_type) DO NOTHING""",
                    (fn, tn, r.get("edge_type", "structure"), sd, mkt),
                )
            elif typ == "node_company":
                cid = _chain_id(r["chain_name"])
                nid = _resolve_node(cur, cid, r["node_name"])
                if nid is None:
                    raise ValueError(
                        f"node_company 引用节点不存在(先在同批次写 node 或确认存量已有): "
                        f"{r['node_name']} (chain={r['chain_name']})"
                    )
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
            elif typ == "unlisted_entity":
                # 编码表登记/上市标定(SOP §4.10): name+country 登记幂等;
                # listed_symbol 须一手来源(交易所公告),工具只信入参不查外源
                country = r.get("country", "CN")
                uid = f"UE-{hashlib.md5(f'{r['name']}|{country}'.encode('utf-8')).hexdigest()[:12]}"
                cur.execute(
                    """INSERT INTO ig_unlisted_entity (ue_id,name,country,status,listed_symbol,source_doc,as_of,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (name,country) DO UPDATE SET updated_at=now(),
                      status=EXCLUDED.status,
                      listed_symbol=COALESCE(EXCLUDED.listed_symbol,ig_unlisted_entity.listed_symbol),
                      source_doc=COALESCE(EXCLUDED.source_doc,ig_unlisted_entity.source_doc)""",
                    (uid, r["name"], country, r.get("status") or "unlisted",
                     r.get("listed_symbol"), sd, r.get("as_of")),
                )
            elif typ == "document":
                # 源语料登记(SOP §4.9 内容层前置): THS 导出/其他新源登记 ig_document,
                # relative_path UNIQUE 幂等; doc_type 自由词(ths_profile 等)
                cur.execute(
                    """INSERT INTO ig_document (doc_id,relative_path,bundle,file_name,ext,size_bytes,mtime,
                       is_canonical,doc_type,title,year,org,market,excluded,parse_status,source_note,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,true,%s,%s,%s,%s,%s,false,'raw',%s,now(),now())
                    ON CONFLICT (relative_path) DO UPDATE SET updated_at=now(),
                      title=COALESCE(EXCLUDED.title,ig_document.title),
                      parse_status=EXCLUDED.parse_status""",
                    (
                        r["doc_id"], r["relative_path"], r.get("bundle") or r.get("title") or Path(r["relative_path"]).name,
                        r.get("file_name") or Path(r["relative_path"]).name, r.get("ext") or "",
                        r.get("size_bytes"), r.get("mtime"), r.get("doc_type") or "ths_profile",
                        r.get("title"), r.get("year"), r.get("org"), r.get("market", "cn"),
                        sd or src,
                    ),
                )
            elif typ == "chunk":
                # 内容层(SOP §4.9): 全量文本块入 ig_chunk; chunk_id 主键幂等;
                # doc_id 外键 -> 同批次或存量须已有 document 记录
                cur.execute(
                    """INSERT INTO ig_chunk (chunk_id,doc_id,title,doc_type,year,chunk_text,created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,now())
                    ON CONFLICT (chunk_id) DO UPDATE SET chunk_text=EXCLUDED.chunk_text""",
                    (r["chunk_id"], r["doc_id"], r.get("title"), r.get("doc_type"), r.get("year"), r["chunk_text"]),
                )
            else:
                raise ValueError(f"未知 record type: {typ}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    # 总控锁心跳续期(锁文件 mtime 即心跳;无锁时静默跳过)
    lock = _controller_lock_dir() / "controller.lock"
    if lock.is_file():
        lock.touch()
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
    ctl = sub.add_parser("controller")
    ctl.add_argument("action", choices=["acquire", "release", "status"])
    ctl.add_argument("--session", default="")
    ctl.add_argument("--ttl-min", type=int, default=30)
    args = p.parse_args()

    try:
        if args.cmd == "controller":
            return cmd_controller(args.action, args.session, args.ttl_min)
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


