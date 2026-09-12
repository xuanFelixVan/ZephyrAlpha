# [MODULE] scripts.industry_graph.websearch_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer (stock_basic 反查)
# [CONSUMERS] 夜班 SOP industry_chain_data_audit_sop §5 全轮次写入(唯一合法通道)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 写入唯一通道: 全部走 ingest 子命令(禁手写 SQL); 批次=单事务全成全败; 幂等(UNIQUE 锚 ON CONFLICT); 硬校验(SOP §5): source_doc 三段式/confidence<=0.7(websearch)/symbol 正则+cn 反查 stock_basic/词表白名单(tier 三位置值 v0.4+function_role 八值/category/edge_type v2/role 五值)/链名标题腔拒绝/node.name 无 -tier 后缀残留/backup 幂等; UNLISTED:UE-xxx 唯一合法格式(旧格式公司名直写拒绝,§4.10); unlisted_entity 记录 status 枚举+listed_symbol 真代码格式校验; equity_edge 记录(relation 六值/as_of 必填/PERSON: 前缀/verification 三值,2026-09-09 分域裁定); node 深度列 child_chain_id+drill_status(child 交叉校验,drill_manual=Owner 钉死 AI 不可写); PIT 三时间戳 websearch 边必填; 节点引用(node/node_company/node_edge)按(链+名)查库解析存量真实ID(存量采购包节点非md5方案,重算ID会FK违规/造重复行,2026-09-08修复); chain 支持 status/merged_into(deprecated 须带 merged_into,幂等 append 不覆盖原 source_note,2026-09-08 裁定执行); chain/placement_close 可选 chain_id 显式寻址(legacy-id 链 md5(现名)≠chain_id 场景,带值须命中存量行防伪造,2026-09-11); node_rename 环节改名(node_id 稳定键不动,新名过文章词/长度/-tier 三关+(链,名)防撞,2026-09-11); fact_close 事实层 PIT 关闭(fact_id 数组直指+reason_doc 留痕,幂等禁 DELETE,2026-09-11)
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from psycopg2.extras import execute_values

from vocab_loader import load_vocab  # 词表唯一真源=industry_graph_field_dictionary.yaml(改词表只改 YAML)
from zephyr.data.table_registry import get_registry
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# ARCH-CH-024: 表名经 TableRegistry 真源派生,禁硬编码;SQL 集中化(§5.160.2)
_TBL_STOCK_BASIC = get_registry().table("meta_stock_basic")
_SQL_ALIVE_SYMBOLS = (
    f"SELECT DISTINCT symbol_canonical FROM {_TBL_STOCK_BASIC} FINAL WHERE valid_to IS NULL"
)

# ---- 词表(字段字典单一真源加载,本文件不再硬编码词表;对齐由 test_field_dictionary_alignment 强制) ----
_V = load_vocab()
TIERS = set(_V["tiers"]["values"]) | set(_V["tiers_legacy"]["values"])
# v0.4 职能化迁移(Owner 2026-09-09 裁定): tier 仅三位置值,职能拆 function_role 八值
TIERS_NEW = set(_V["tiers"]["values"])
FUNCTION_ROLES = tuple(_V["function_roles"]["values"])
ROLES_STD = tuple(_V["roles_std"]["values"])  # role 五值(Owner 2026-09-09 裁定)
# 深度体系 drill_status: AI 可写三值; drill_manual=Owner 钉死 AI 不可写(SOP 节点模板裁定1)
DRILL_STATUSES_AI = set(_V["drill_statuses_ai"]["values"])
CHAIN_ID_RE = re.compile(r"^CH-[0-9a-f]{12}$")
# 链名标题腔(与引擎 TITLE_JUNK_RE 同源;2026-09-10 扩词: Owner 点名"中国节水装备行业发展现状"
# "环氧丙烷产业链供需格局"穿透事故——补 现状/格局/趋势/展望/前景/图解/一文/解析/洞察/应用)
TITLE_JUNK_RE = re.compile("一张图看懂|重磅|最新|预测|深度|全景图|解读|盘点|风向标|启幕|ppt|研报|机遇|风口|现状|格局|趋势|展望|前景|图解|一文|解析|洞察|市场和应用")
# 链名长度上限(SOP §4.7.1 ≤12 字,2026-09-10 起工具硬校验——此前只写在 SOP 未执行)
CHAIN_NAME_MAX_LEN = 12
# 2026-09-10 词汇审计新增: 传导类型四值(SOP §4.8 朝阳永续对标;存量 14 条 websearch 边自创
# direct/indirect 违反词表,工具一直未拦——补拦防新增,存量归一另批)+weight_type 词表化
TRANSMISSION_TYPES = {"利润传导", "政策传导", "价格传导", "情绪传导"}
WEIGHT_TYPES = {"sales_pct", "collab_count", "amount_yi", "revenue_pct"}
# 环节名结构(词汇审计:文章标题混入环节名"唐山地区黑色产业链调研（一"/"PVC产业链配套与边际装置"——
# S7 只拦 -tier 后缀不拦文章词;环节=标准工序/部件名词 ≤15 字)
NODE_NAME_MAX_LEN = 15
NODE_JUNK_RE = re.compile(r"产业链|调研|概况|格局|进出口|配套|边际装置|纵览|概况及")
# 链名结构完整性(S25 同源,SOP §4.7.0 链名分类学 2026-09-10): 截断括号/虚词悬空尾/外文缩写裸名/报告词
CHAIN_STRUCT_RE = re.compile(r"（(?![^）]*）)|\((?![^)]*\))|[的与及了]$|^[A-Z0-9]{2,6}$|指数|白皮书|研究报告|年鉴")
CATEGORIES = set(_V["categories"]["values"])
CHAIN_STATUSES = set(_V["chain_statuses"]["values"])  # SOP §4.6 ig_chain.status 封闭枚举
MERGED_INTO_RE = re.compile(r"^CH-[0-9a-f]{12}$")
EDGE_TYPES_V2 = set(_V["edge_types_v2"]["values"])
NODE_SUFFIX_RE = re.compile(r"-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$")
SYMBOL_CN_RE = re.compile(r"^\d{6}\.(SH|SZ|BJ)$")
SYMBOL_GLOBAL_RE = re.compile(r"^[A-Z0-9]{1,6}\.(US|KS|TW|T|HK|DE|LN|JP|SM)$")
# UNLISTED 唯一合法格式=编码表主键引用(SOP §4.10,2026-09-08 开放问题9裁定:
# 旧格式 UNLISTED:公司名 禁止,防双格式并存致夜班模型幻觉/漂移)
SYMBOL_UNLISTED_RE = re.compile(r"^UNLISTED:UE-[0-9a-f]{12}$")
SOURCEDOC_RE = re.compile(r"^[^|]+\|[^|]+\|\d{4}-\d{2}-\d{2}$")
# 股权穿透表(2026-09-09 裁定: 同库独立表 ig_equity_edge,与 ig_company_edge 分域;
# 分流硬规则: 被投/持股/实控/质押->equity_edge, 供应/客户/竞争/合作->company_edge)
EQUITY_RELATIONS = set(_V["equity_relations"]["values"])
EQUITY_VERIFICATION = set(_V["equity_verification"]["values"])
PERSON_PREFIX = "PERSON:"

# 落位PIT关闭/产品营收归一 SQL 集中化(NO-BARE-SQL 同款口径)
_SQL_PLACEMENT_CLOSE = """UPDATE ig_node_company SET valid_to=%s, updated_at=now()
                    WHERE valid_to IS NULL AND symbol=%s
                      AND node_id IN (SELECT node_id FROM ig_node WHERE chain_id=%s)"""
_SQL_PRODUCT_REVENUE_UPSERT = """INSERT INTO ig_product_revenue (symbol,year,product,revenue_pct,node_ref,source,source_doc,evidence,as_of)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (symbol,year,product,source) DO UPDATE SET revenue_pct=EXCLUDED.revenue_pct, as_of=EXCLUDED.as_of"""
# chain_id 显式寻址防伪校验(2026-09-11): legacy-id 链(chain_id≠md5(现名),曾改名/旧命名方案)
# 无法按名寻址——chain/placement_close 记录可带 chain_id 直指,带值时 MUST 命中存量行
_SQL_CHAIN_EXISTS = "SELECT 1 FROM ig_chain WHERE chain_id=%s"
# 环节改名(词汇治理): node_id 稳定键不动仅改 name,存量引用(node_company/ig_edge 按 node_id)零影响
_SQL_NODE_RENAME = "UPDATE ig_node SET name=%s, updated_at=now() WHERE node_id=%s"
# fact_close(2026-09-11 ig_fact 事实层 PIT 收口): 噪音/离型事实关闭唯一通道,幂等(valid_to IS NULL 才关),禁 DELETE
_SQL_FACT_CLOSE = "UPDATE ig_fact SET valid_to=%s WHERE fact_id=ANY(%s) AND valid_to IS NULL"

_ALL_TABLES = ("ig_chain", "ig_node", "ig_edge", "ig_node_company", "ig_document", "ig_company_edge", "ig_company_metric", "ig_chunk", "ig_fact", "ig_unlisted_entity", "ig_equity_edge", "ig_product_revenue")
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
        from zephyr.data import ch_reader

        tsv = ch_reader.query(_SQL_ALIVE_SYMBOLS)
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

        if typ == "product_revenue":
            # 营收归因豁免在市校验(2026-09-11): CKG 数据集含退市/B股历史公司,营收归因含历史公司
            # by-design(回测口径), symbol 仅查基本格式(6位数字.市场)
            pre: list[str] = []
            sym = r.get("symbol", "")
            if not re.match(r"^\d{6}\.(SH|SZ|BJ)$", sym):
                pre.append(f"{idx}: product_revenue symbol 非法: {sym}")
            if not r.get("as_of"):
                pre.append(f"{idx}: product_revenue 缺 as_of")
            errs.extend(pre)
            if not pre:
                continue   # product_revenue 合法(或已记错),跳过后续通用 symbol 校验
        market = r.get("market", "cn")
        # 硬校验 3: symbol 正则(按端点各自市场判定,2026-09-08 跨市场治本:
        # global 边可混端 cn+海外 symbol;单边 market=cn 但 symbol 是海外格式时按
        # 该 symbol 实际市场校验,不再因边级 market 标签误拒合法混端边)
        if typ == "placement_close":
            # 关闭操作豁免在市校验(2026-09-11): placement_close 正是关死映射/误挂的通道,
            # 目标 symbol 可能已被主数据标记退场(如 stock_basic 误标),按 chain_name+symbol 关闭
            if not r.get("symbol"):
                errs.append(f"{idx}: placement_close 缺 symbol")
            else:
                return errs   # 只需 symbol 非空+下面 valid_to 由执行层校验
        if typ == "fact_close":
            # 事实层关闭(2026-09-11): fact_id 整数数组直指+reason_doc 留痕;无 symbol 概念,豁免在市校验
            fids = r.get("fact_ids")
            if not fids or not isinstance(fids, list) or not all(
                isinstance(x, int) and not isinstance(x, bool) for x in fids
            ):
                errs.append(f"{idx}: fact_close 缺 fact_ids(非空整数数组)")
            if not r.get("reason_doc"):
                errs.append(f"{idx}: fact_close 缺 reason_doc 留痕")
        if typ == "node_close":
            # 节点层关闭(2026-09-12 ig_node.valid_to PIT 收口): node_id 数组直指+reason_doc 留痕;
            # 幂等可逆(valid_to IS NULL 才关),对标 fact_close;禁 DELETE 的节点治理唯一通道
            nids = r.get("node_ids")
            if not nids or not isinstance(nids, list) or not all(
                isinstance(x, str) and x.startswith("ND-") for x in nids
            ):
                errs.append(f"{idx}: node_close 缺 node_ids(非空 ND- 前缀字符串数组)")
            if not r.get("reason_doc"):
                errs.append(f"{idx}: node_close 缺 reason_doc 留痕")
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
        # 硬校验 7: tier 词表(v0.4 职能化: websearch 新写仅三位置值,职能走 function_role)
        if typ == "node":
            tier = r.get("tier")
            if tier and tier not in TIERS:
                errs.append(f"{idx}: tier 非词表: {tier}")
            if tier and src in ("websearch", "corpus_rag") and tier not in TIERS_NEW:
                errs.append(f"{idx}: websearch 禁 tier={tier}(v0.4 后 tier 仅 上游/中游/下游,职能写 function_role)")
            if NODE_SUFFIX_RE.search(r.get("name", "")):
                errs.append(f"{idx}: node.name 含 -tier 后缀残留: {r.get('name')}")
            fr = r.get("function_role")
            if fr is not None and fr not in FUNCTION_ROLES:
                errs.append(f"{idx}: function_role 非八值词表: {fr}")
            ds = r.get("drill_status")
            if ds is not None:
                if ds == "drill_manual":
                    errs.append(f"{idx}: drill_status=drill_manual 为 Owner 钉死值,AI 不可写")
                elif ds not in DRILL_STATUSES_AI:
                    errs.append(f"{idx}: drill_status 非法(child/brick_mass/brick_noalpha): {ds}")
            cc = r.get("child_chain_id")
            if cc is not None and not CHAIN_ID_RE.match(cc):
                errs.append(f"{idx}: child_chain_id 非 chain_id 格式: {cc}")
            if ds == "child" and not cc:
                errs.append(f"{idx}: drill_status=child 须带 child_chain_id(交叉校验)")
            if cc and ds not in ("child", None):
                errs.append(f"{idx}: 带 child_chain_id 时 drill_status 须为 child: {ds}")
        # 硬校验: role 五值白名单(Owner 2026-09-09 裁定,与引擎 S10 同词表)
        if typ == "node_company":
            role = r.get("role")
            if role is not None and role not in ROLES_STD:
                errs.append(f"{idx}: role 非五值词表(龙头/核心/主要/参与/提及): {role}")
            # S13 PIT: websearch 新落位必带 valid_from(2026-09-09 长城任务收紧)
            if src in ("websearch", "corpus_rag") and not r.get("valid_from"):
                errs.append(f"{idx}: node_company 缺 valid_from(S13 PIT)")
        # 硬校验 8: category
        if typ == "chain":
            cat = r.get("category")
            if cat and cat not in CATEGORIES and cat != "综合":
                errs.append(f"{idx}: category 非申万词表: {cat}")
            # chain 状态与合并指向(2026-09-08 裁定执行: 碎片链 deprecated 走唯一合法通道)
            st = r.get("status")
            if st is not None and st not in CHAIN_STATUSES:
                errs.append(f"{idx}: status 非法(仅 active/deprecated): {st}")
            act = bool(r.get("activate"))
            if act and st != "active":
                errs.append(f"{idx}: activate=true 仅可与 status='active' 搭配(显式激活通道,须带激活留痕 source_doc)")
            mi = r.get("merged_into")
            if mi is not None and not MERGED_INTO_RE.match(mi):
                errs.append(f"{idx}: merged_into 非 chain_id 格式: {mi}")
            if st == "deprecated" and not mi:
                errs.append(f"{idx}: deprecated 链须带 merged_into(SOP §4.6)")
            # 链名三查只约束新写/活跃链;deprecated 重发=垃圾名废弃动作,旧名豁免(2026-09-10);
            # 显式激活(activate=true)走激活留痕,新名同样过三查(2026-09-12)
            if st != "deprecated":
                if TITLE_JUNK_RE.search(r.get("name", "")):
                    errs.append(f"{idx}: 链名标题腔拒绝(规范名=XX产业链句式): {r.get('name')}")
                if len(r.get("name", "")) > CHAIN_NAME_MAX_LEN:
                    errs.append(f"{idx}: 链名超长(>{CHAIN_NAME_MAX_LEN}字,SOP §4.7.1): {r.get('name')}")
                if CHAIN_STRUCT_RE.search(r.get("name", "")):
                    errs.append(f"{idx}: 链名结构违规(S25:括号不闭合/虚词悬空尾/外文缩写裸名/报告词,缩写进aliases): {r.get('name')}")
        if typ in ("node_edge", "company_edge"):
            et = r.get("edge_type", r.get("relation"))
            if et and et not in EDGE_TYPES_V2:
                errs.append(f"{idx}: edge_type 非 v2 词表: {et}")
        # transmission_type 四值词表+weight_type 词表(2026-09-10 词汇审计补拦防新增)
        if typ == "company_edge":
            tt = r.get("transmission_type")
            if tt:
                for v in (tt if isinstance(tt, list) else [tt]):
                    if v not in TRANSMISSION_TYPES:
                        errs.append(f"{idx}: transmission_type 非四值词表(利润传导/政策传导/价格传导/情绪传导): {v}")
            wt = r.get("weight_type")
            if wt and wt not in WEIGHT_TYPES:
                errs.append(f"{idx}: weight_type 非词表(sales_pct/collab_count/amount_yi/revenue_pct): {wt}")
        # 环节名结构(2026-09-10 词汇审计:文章标题混入环节名,补文章词+长度拦截)
        if typ == "node":
            nn = r.get("name", "")
            if len(nn) > NODE_NAME_MAX_LEN:
                errs.append(f"{idx}: 环节名超长(>{NODE_NAME_MAX_LEN}字,环节=标准工序/部件名词): {nn}")
            hit = NODE_JUNK_RE.search(nn)
            if hit:
                errs.append(f"{idx}: 环节名含文章词({hit.group(0)}),环节名禁报告式短语: {nn}")
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
        # 股权穿透记录校验(2026-09-09 裁定: ig_equity_edge 21 列 UBO 标准;
        # relation 六值枚举; as_of 必填=年报口径期末日/公告日; holder/held 同 symbol
        # 契约 + PERSON:人名 前缀; verification 三值)
        if typ == "equity_edge":
            for k in ("holder", "held"):
                v = r.get(k)
                if not v:
                    errs.append(f"{idx}: equity_edge 缺 {k}")
                    continue
                if v.startswith(PERSON_PREFIX):
                    if not v[len(PERSON_PREFIX):].strip():
                        errs.append(f"{idx}: equity_edge {k} PERSON: 后人名非空: {v!r}")
                    continue
                if SYMBOL_CN_RE.match(v):
                    if stocks is not None and v not in stocks:
                        errs.append(f"{idx}: equity_edge {k} cn symbol 不在 stock_basic: {v}")
                elif SYMBOL_GLOBAL_RE.match(v) or SYMBOL_UNLISTED_RE.match(v):
                    pass
                elif v.startswith("UNLISTED:"):
                    errs.append(f"{idx}: equity_edge {k} UNLISTED 旧格式已禁,须 UNLISTED:UE-xxx: {v}")
                else:
                    errs.append(f"{idx}: equity_edge {k} 非 symbol/PERSON:/UNLISTED:UE- 格式: {v}")
            rel = r.get("relation")
            if rel not in EQUITY_RELATIONS:
                errs.append(f"{idx}: equity_edge.relation 非六值枚举(invests_in/subsidiary/shareholding/actual_control/pledge/judicial_frozen): {rel}")
            if not r.get("as_of"):
                errs.append(f"{idx}: equity_edge 缺 as_of(年报口径期末日/公告日,必填)")
            vf = r.get("valid_from")
            if vf and r.get("as_of") and str(vf) > str(r.get("as_of")):
                errs.append(f"{idx}: equity_edge valid_from 晚于 as_of(时间倒挂): {vf}>{r.get('as_of')}")
            ver = r.get("verification")
            if ver is not None and ver not in EQUITY_VERIFICATION:
                errs.append(f"{idx}: equity_edge.verification 非三值(unverified/verified/official): {ver}")
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
                # 可选 chain_id 显式寻址(2026-09-11): legacy-id 链(md5(现名)≠chain_id)按值直指,
                # 带值 MUST 命中存量行(禁造任意 id 新行);不带值走 md5(name) 派生老路径
                cid = r.get("chain_id") or _chain_id(r["name"])
                if r.get("chain_id"):
                    cur.execute(_SQL_CHAIN_EXISTS, (cid,))
                    if cur.fetchone() is None:
                        raise ValueError(f"chain.chain_id 寻址不存在(防伪,禁造新id行): {cid}")
                merged = r.get("merged_into")
                # 2026-09-12 显式激活通道: activate=true+status=active 才允许 deprecated→active
                # 转换(ig_fact 空壳链填充任务);普通重发防复活保护不变
                act = bool(r.get("activate")) and r.get("status") == "active"
                cur.execute(
                    """INSERT INTO ig_chain (chain_id,name,category,version_year,market,status,source_note,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (chain_id) DO UPDATE SET updated_at=now(),
                      category=COALESCE(EXCLUDED.category,ig_chain.category),
                      version_year=COALESCE(EXCLUDED.version_year,ig_chain.version_year),
                      status=CASE
                        WHEN EXCLUDED.status IS DISTINCT FROM 'active' THEN EXCLUDED.status
                        WHEN %s THEN 'active'
                        ELSE ig_chain.status END,
                      source_note=CASE
                        WHEN %s::text IS NOT NULL AND position(%s::text in ig_chain.source_note)=0
                        THEN ig_chain.source_note||' | merged_into:'||%s::text
                        ELSE ig_chain.source_note END""",
                    (cid, r["name"], r.get("category"), r.get("version_year"), mkt,
                     r.get("status") or "active", (sd or src) + (f" | merged_into:{merged}" if merged and "merged_into:" not in (sd or src) else ""),
                     act, merged, merged, merged),
                )
            elif typ == "node":
                cid = _chain_id(r["chain_name"])
                nid = _resolve_node(cur, cid, r["name"])
                if nid is not None:
                    # drill_manual=Owner 钉死值: AI 更新不得触碰该两列(节点模板裁定1)
                    cur.execute(
                        """UPDATE ig_node SET updated_at=now(),
                             tier=COALESCE(NULLIF(%s,''), ig_node.tier),
                             aliases=COALESCE(%s, ig_node.aliases),
                             description=COALESCE(%s, ig_node.description),
                             function_role=COALESCE(%s, ig_node.function_role),
                             child_chain_id=CASE WHEN ig_node.drill_status='drill_manual' THEN ig_node.child_chain_id
                                                 ELSE COALESCE(%s, ig_node.child_chain_id) END,
                             drill_status=CASE WHEN ig_node.drill_status='drill_manual' THEN ig_node.drill_status
                                               ELSE COALESCE(%s, ig_node.drill_status) END
                           WHERE node_id=%s""",
                        (r.get("tier") or "", r.get("aliases"), r.get("description"), r.get("function_role"),
                         r.get("child_chain_id"), r.get("drill_status"), nid),
                    )
                else:
                    nid = _node_id(cid, r["name"], r.get("tier", ""))
                    cur.execute(
                        """INSERT INTO ig_node (node_id,chain_id,name,tier,aliases,description,market,function_role,child_chain_id,drill_status,created_at,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())
                        ON CONFLICT (node_id) DO UPDATE SET updated_at=now(), tier=COALESCE(NULLIF(EXCLUDED.tier,''),ig_node.tier),
                          function_role=COALESCE(EXCLUDED.function_role,ig_node.function_role)""",
                        (nid, cid, r["name"], r.get("tier"), r.get("aliases"), r.get("description"), mkt,
                         r.get("function_role"), r.get("child_chain_id"), r.get("drill_status")),
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
                    """INSERT INTO ig_node_company (node_id,symbol,role,confidence,evidence_text,source_doc,market,valid_from,valid_to,pit_strength,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (node_id,symbol) DO UPDATE SET updated_at=now(),
                      confidence=GREATEST(ig_node_company.confidence,EXCLUDED.confidence),
                      evidence_text=COALESCE(EXCLUDED.evidence_text,ig_node_company.evidence_text)""",
                    (nid, r["symbol"], r.get("role"), r.get("confidence", 0.5), r.get("evidence_text"), sd, mkt,
                     r.get("valid_from"), r.get("valid_to"), r.get("pit_strength")),
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
            elif typ == "equity_edge":
                # 股权穿透边(2026-09-09 裁定: 与 ig_company_edge 分域;UNIQUE 锚幂等)
                cur.execute(
                    """INSERT INTO ig_equity_edge (holder,held,stake_pct,voting_pct,layer,relation,control_method,
                       acquisition_cost,acquisition_date,as_of,valid_from,valid_to,holder_name,holder_country,
                       verification,source,source_doc,evidence,created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())
                    ON CONFLICT (holder,held,as_of,source) DO UPDATE SET
                      relation=EXCLUDED.relation,
                      stake_pct=COALESCE(EXCLUDED.stake_pct,ig_equity_edge.stake_pct),
                      voting_pct=COALESCE(EXCLUDED.voting_pct,ig_equity_edge.voting_pct),
                      layer=COALESCE(EXCLUDED.layer,ig_equity_edge.layer),
                      control_method=COALESCE(EXCLUDED.control_method,ig_equity_edge.control_method),
                      acquisition_cost=COALESCE(EXCLUDED.acquisition_cost,ig_equity_edge.acquisition_cost),
                      acquisition_date=COALESCE(EXCLUDED.acquisition_date,ig_equity_edge.acquisition_date),
                      valid_from=COALESCE(EXCLUDED.valid_from,ig_equity_edge.valid_from),
                      valid_to=COALESCE(EXCLUDED.valid_to,ig_equity_edge.valid_to),
                      holder_name=COALESCE(EXCLUDED.holder_name,ig_equity_edge.holder_name),
                      holder_country=COALESCE(EXCLUDED.holder_country,ig_equity_edge.holder_country),
                      verification=COALESCE(EXCLUDED.verification,ig_equity_edge.verification),
                      evidence=COALESCE(EXCLUDED.evidence,ig_equity_edge.evidence),
                      source_doc=COALESCE(EXCLUDED.source_doc,ig_equity_edge.source_doc)""",
                    (r["holder"], r["held"], r.get("stake_pct"), r.get("voting_pct"), r.get("layer", 1),
                     r["relation"], r.get("control_method"), r.get("acquisition_cost"), r.get("acquisition_date"),
                     r["as_of"], r.get("valid_from"), r.get("valid_to"), r.get("holder_name"),
                     r.get("holder_country"), r.get("verification") or "unverified", src, sd, r.get("evidence")),
                )
            elif typ == "product_revenue":
                # 产品营收归因(SOP §4.9 四层架构;2026-09-11 ETL 落地: ig_fact produces 关系同构迁移)
                rp = r.get("revenue_pct")
                if rp is not None and not (0 <= float(rp) <= 1):
                    raise ValueError(f"product_revenue revenue_pct 越界[0,1]: {rp}")
                if not r.get("as_of"):
                    raise ValueError("product_revenue 缺 as_of")
                cur.execute(_SQL_PRODUCT_REVENUE_UPSERT,
                    (r["symbol"], r["year"], r["product"], rp, r.get("node_ref"),
                     src, sd, r.get("evidence"), r.get("as_of")))
            elif typ == "placement_close":
                # 落位 PIT 关闭(梳理工程唯一合法通道,2026-09-10;禁手写 SQL):
                # 幂等(valid_to IS NULL 才关);须 chain_name+symbol 精确定位;reason_doc 留痕
                # 可选 chain_id 显式寻址(2026-09-11): legacy-id 链 md5(名)≠chain_id 时按值直指,
                # 带值 MUST 命中存量行(防伪造 id);不带值走 md5 老路径(幂等重放不报错)
                cid = r.get("chain_id") or _chain_id(r["chain_name"])
                if r.get("chain_id"):
                    cur.execute(_SQL_CHAIN_EXISTS, (cid,))
                    if cur.fetchone() is None:
                        raise ValueError(f"placement_close chain_id 寻址不存在(防伪): {cid}")
                vt = r.get("valid_to") or _today()
                if not re.match(r"\d{4}-\d{2}-\d{2}", str(vt)):
                    raise ValueError(f"placement_close valid_to 非日期: {vt}")
                cur.execute(_SQL_PLACEMENT_CLOSE, (vt, r["symbol"], cid))
            elif typ == "node_rename":
                # 环节改名(2026-09-11 词汇治理): node_id 稳定键不动,仅改 name——存量
                # node_company/ig_edge 引用按 node_id 外键,零影响。硬校验: 旧名须存在、
                # 新名过 NODE_JUNK_RE/长度/-tier 后缀三关、(链,新名)不撞存量、新旧不同名。
                cid = r.get("chain_id") or _chain_id(r["chain_name"])
                if r.get("chain_id"):
                    cur.execute(_SQL_CHAIN_EXISTS, (cid,))
                    if cur.fetchone() is None:
                        raise ValueError(f"node_rename chain_id 寻址不存在(防伪): {cid}")
                nid = _resolve_node(cur, cid, r["old_name"])
                if nid is None:
                    raise ValueError(
                        f"node_rename 旧环节名不存在: {r['old_name']} (chain={r['chain_name']})"
                    )
                nn = r["new_name"]
                if nn == r["old_name"]:
                    raise ValueError("node_rename 新旧同名")
                if NODE_JUNK_RE.search(nn):
                    raise ValueError(f"node_rename 新名含文章词: {nn}")
                if len(nn) > NODE_NAME_MAX_LEN:
                    raise ValueError(f"node_rename 新名超长(>{NODE_NAME_MAX_LEN}字): {nn}")
                if NODE_SUFFIX_RE.search(nn):
                    raise ValueError(f"node_rename 新名含 -tier 后缀残留: {nn}")
                if _resolve_node(cur, cid, nn) is not None:
                    raise ValueError(f"node_rename (链,新名)已存在: {nn} (chain={r['chain_name']})")
                cur.execute(_SQL_NODE_RENAME, (nn, nid))
            elif typ == "fact_close":
                # 事实层 PIT 关闭(2026-09-11 ig_fact 收口): 噪音/离型事实唯一出清通道,
                # 幂等(valid_to IS NULL 才关),禁 DELETE;fact_id 数组直指,reason_doc 校验层留痕
                vt = r.get("valid_to") or _today()
                if not re.match(r"\d{4}-\d{2}-\d{2}", str(vt)):
                    raise ValueError(f"fact_close valid_to 非日期: {vt}")
                cur.execute(_SQL_FACT_CLOSE, (vt, r["fact_ids"]))
            elif typ == "node_close":
                # 节点层 PIT 关闭(2026-09-12 ig_node.valid_to 收口): 孤岛等治理节点唯一出清通道,
                # 幂等(valid_to IS NULL 才关),禁 DELETE;node_id 数组直指,reason_doc 校验层留痕
                vt = r.get("valid_to") or _today()
                if not re.match(r"\d{4}-\d{2}-\d{2}", str(vt)):
                    raise ValueError(f"node_close valid_to 非日期: {vt}")
                cur.execute(
                    """UPDATE ig_node SET valid_to=%s, updated_at=now()
                       WHERE node_id = ANY(%s) AND valid_to IS NULL""",
                    (vt, r["node_ids"]),
                )
            elif typ == "unlisted_entity":
                # 编码表登记/上市标定(SOP §4.10): name+country 登记幂等;
                # listed_symbol 须一手来源(交易所公告),工具只信入参不查外源;
                # covered=主数据收录标记(Owner 2026-09-10 留痕指令: 北交所/海外实体一律登记,
                # 行情库收录后按 covered=false 清单 promote 对上,DDL v6)
                country = r.get("country", "CN")
                uid = f"UE-{hashlib.md5(f'{r['name']}|{country}'.encode('utf-8')).hexdigest()[:12]}"
                cur.execute(
                    """INSERT INTO ig_unlisted_entity (ue_id,name,country,status,listed_symbol,covered,source_doc,as_of,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now(),now())
                    ON CONFLICT (name,country) DO UPDATE SET updated_at=now(),
                      status=EXCLUDED.status,
                      listed_symbol=COALESCE(EXCLUDED.listed_symbol,ig_unlisted_entity.listed_symbol),
                      covered=EXCLUDED.covered,
                      source_doc=COALESCE(EXCLUDED.source_doc,ig_unlisted_entity.source_doc)""",
                    (uid, r["name"], country, r.get("status") or "unlisted",
                     r.get("listed_symbol"), bool(r.get("covered", False)), sd, r.get("as_of")),
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


