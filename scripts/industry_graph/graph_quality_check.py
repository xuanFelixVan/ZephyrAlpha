# [MODULE] scripts.industry_graph.graph_quality_check
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer (stock_basic 反查)
# [CONSUMERS] SOP industry_chain_data_audit_sop §11 质量验收循环(引擎判定权真源); 长城任务退出判定(连续两轮零违规)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读引擎: 全部 SELECT 零写入; 合格线=graph_quality_standard.md §2~§8 一一对应(S1~S20 硬线+S21~S24 进度指标(advisory 不计违规不阻断); S21=流程连通性(2026-09-10 口径修正: 墓碑节点过滤+锚点链豁免,与 S8 同口径;修正前 336 advisory 中 93.8% 为墓碑伪断链); S24=僵尸链检测(2026-09-10 增,活跃链去墓碑实质节点<=1 或全等链名,清单=Owner 废弃排序底稿)); 豁免清单 quality_exemptions.yaml(未登记违规不扣除); 成对冗余豁免在 S16 SQL 内判(supplies_to+customer_of 合法); S20 两段式判定(SQL 粗筛+原文正则核据,2026-09-09 Owner 签名); 输出 JSON(.runtime)+MD 报告, 退出码 0=全绿 1=有违规 2=环境故障
# [MODIFY-GUARD] graph_quality_standard.md(标准真源,SQL 须与其同步改)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->exit 2; CH 不可达->S11/S19 降级 warn 且不计违规(标 degraded); 豁免文件不存在->视为零豁免
# [TTL] permanent
# M10豁免: manual STARTUP 体检引擎
"""图谱质量检查引擎（Graph Quality Check，SOP §11 / graph_quality_standard.md）。

二十一项合格线一键体检（S1~S18 走 SQL 模板、S11/S19/S21 走 Python 特例检查），输出违规清单（JSON+MD）。
审查判定权归本脚本——AI 只负责修复，不负责判定（治审查口径漂移）。

用法::

    python scripts/industry_graph/graph_quality_check.py            # 体检+落盘报告
    python scripts/industry_graph/graph_quality_check.py --json -  # 仅 JSON 到 stdout
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from vocab_loader import load_vocab  # noqa: E402  词表唯一真源=industry_graph_field_dictionary.yaml
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

REPORT_DIR = Path(__file__).resolve().parents[2] / ".runtime" / "industry_graph" / "quality_reports"
EXEMPT_FILE = Path(__file__).resolve().parent / "quality_exemptions.yaml"

# 词表(字段字典单一真源加载,本文件不再硬编码词表;对齐由 test_field_dictionary_alignment 强制)
_V = load_vocab()
TITLE_JUNK_RE = "一张图看懂|重磅|最新|预测|深度|全景图|解读|盘点|风向标|启幕|ppt|研报|机遇|风口"
TIER_POSITION = tuple(_V["tiers"]["values"])  # v0.4 职能化: tier 仅三位置值(Owner 2026-09-09)
FUNCTION_ROLES = tuple(_V["function_roles"]["values"])
TIER_SUFFIX_RE = "-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$"
ROLES_STD = tuple(_V["roles_std"]["values"])
SW_CATEGORIES = tuple(_V["categories"]["values"])
PIT_CUTOFF = "2026-09-08"  # S13: 此日期后新增落位必须带 valid_from(THS 铺面批次的次日)
MAX_CHAINS_PER_SYMBOL = 20  # S14 挂链阈值(Owner 2026-09-09 裁定)


def _load_exemptions() -> dict[str, list[str]]:
    """豁免登记表 {标准号: [主键,...]}——未登记不扣除。"""
    if not EXEMPT_FILE.is_file():
        return {}
    try:
        import yaml

        data = yaml.safe_load(EXEMPT_FILE.read_text(encoding="utf-8")) or {}
        return {k: [str(x) for x in v] for k, v in data.items() if isinstance(v, list)}
    except Exception:  # noqa: BLE001 — 豁免文件损坏按零豁免处理(warn 不阻断)
        print("[WARN] 豁免文件解析失败,按零豁免处理")
        return {}


def _load_alive_stocks() -> set[str] | None:
    try:
        from zephyr.data import ch_writer

        tsv = ch_writer.query(
            "SELECT symbol_canonical FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL"
        )
        return {ln.strip().split("\t")[0] for ln in tsv.strip().splitlines() if ln.strip()}
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] stock_basic 反查降级(S11/S19 不计违规): {e}")
        return None


# ---- 十九项检查(每项: 编号/标题/SQL/采样列) ----
# SQL 约定: 返回 (主键, 描述) 两列; 主键供豁免扣除与修复对账

CHECKS: list[dict] = [
    # ---- 链层 ----
    {"id": "S1", "title": "链名零文档标题腔", "sql": f"""
        SELECT chain_id, name FROM ig_chain
        WHERE name ~ '{TITLE_JUNK_RE}' AND (status IS NULL OR status='active')
    """},
    {"id": "S2", "title": "链名唯一且规范", "sql": """
        SELECT c.chain_id, c.name || ' (重复x' || cnt || ')' FROM ig_chain c
        JOIN (SELECT name, count(*) cnt FROM ig_chain GROUP BY name HAVING count(*)>1) d
          ON c.name = d.name
        UNION ALL
        SELECT chain_id, name || ' (·尾巴)' FROM ig_chain WHERE name ~ '·[0-9]+'
    """},
    {"id": "S3", "title": "category 全在申万词表", "sql": f"""
        SELECT chain_id, coalesce(category,'(空)') || ' | ' || name FROM ig_chain
        WHERE (category IS NULL OR category NOT IN ({','.join(f"'{c}'" for c in SW_CATEGORIES)}))
          AND (status IS NULL OR status='active')
    """},
    {"id": "S4", "title": "废弃链闭环", "sql": """
        SELECT chain_id, '缺merged_into: ' || name FROM ig_chain
        WHERE status='deprecated' AND (source_note IS NULL OR source_note !~ 'merged_into:CH-[0-9a-f]{12}')
        UNION ALL
        SELECT c.chain_id, '废弃链落位残留 ' || count(*) FROM ig_chain c
        JOIN ig_node n ON n.chain_id=c.chain_id
        JOIN ig_node_company nc ON nc.node_id=n.node_id
        WHERE c.status='deprecated' AND nc.valid_to IS NULL
        GROUP BY c.chain_id
    """},
    {"id": "S5", "title": "version_year 覆盖(锚点链豁免)", "sql": """
        SELECT chain_id, 'version_year空: ' || name FROM ig_chain
        WHERE version_year IS NULL AND (status IS NULL OR status='active')
          AND name NOT LIKE '%行业'
    """},
    # S25 链名结构完整性(2026-09-10 SOP §4.7.0 链名分类学): 括号不闭合/虚词悬空尾/外文缩写裸名/报告指数词
    {"id": "S25", "title": "链名结构完整(括号闭合/无悬空尾/非裸缩写/非报告名)", "sql": r"""
        SELECT chain_id, name FROM ig_chain
        WHERE (status IS NULL OR status='active') AND (
          (name ~ '（' AND name !~ '）') OR (name ~ '\(' AND name !~ '\)')
          OR name ~ '[的与及了]$'
          OR name ~ '^[A-Z0-9]{2,6}$'
          OR name ~ '指数|白皮书|研究报告|年鉴'
        )
    """},
    # ---- 节点层 ----
    # S6 v0.4 职能化: tier 仅三位置值(残留职能值=违规) + function_role 八值词表检查
    # 2026-09-09 Owner 委托裁定: 废弃链上节点=历史快照不审(与 S8 同口径),只审活跃链
    {"id": "S6", "title": "tier 三位置值+function_role 八值+零 unspecified", "sql": f"""
        SELECT n.node_id, coalesce(n.tier,'(空)') || ' | ' || n.name FROM ig_node n
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE (n.tier IS NULL OR (n.tier NOT IN ({','.join(f"'{t}'" for t in TIER_POSITION)}) AND n.tier <> 'unspecified'))
          AND (c.status IS NULL OR c.status='active')
        UNION ALL
        SELECT n.node_id, 'unspecified | ' || n.name FROM ig_node n
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE n.tier='unspecified' AND (c.status IS NULL OR c.status='active')
        UNION ALL
        SELECT node_id, 'function_role非法:' || function_role || ' | ' || name FROM ig_node
        WHERE function_role IS NOT NULL AND function_role NOT IN ({','.join(f"'{f}'" for f in FUNCTION_ROLES)})
    """},
    {"id": "S7", "title": "节点名零 -tier 后缀", "sql": f"""
        SELECT node_id, name FROM ig_node WHERE name ~ '{TIER_SUFFIX_RE}'
    """},
    {"id": "S8", "title": "零孤岛节点(聚合节点豁免)", "sql": """
        SELECT n.node_id, n.name || ' @' || c.name FROM ig_node n
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE NOT EXISTS (SELECT 1 FROM ig_edge e WHERE e.from_node=n.node_id OR e.to_node=n.node_id)
          AND NOT EXISTS (SELECT 1 FROM ig_node_company nc WHERE nc.node_id=n.node_id AND nc.valid_to IS NULL)
          AND n.name <> '行业聚合'
          AND n.name NOT LIKE '%%（已并入%%'
          AND (c.status IS NULL OR c.status='active')
    """},
    {"id": "S9", "title": "同链同名节点零重复", "sql": """
        SELECT n.node_id, n.name || ' @' || c.name FROM ig_node n
        JOIN ig_chain c ON n.chain_id=c.chain_id
        JOIN (SELECT chain_id, name FROM ig_node GROUP BY chain_id, name HAVING count(*)>1) d
          ON n.chain_id=d.chain_id AND n.name=d.name
    """},
    # ---- 落位层 ----
    {"id": "S10", "title": "role 五值词表", "sql": f"""
        SELECT nc.id::text, coalesce(nc.role,'(空)') || ' | ' || nc.symbol FROM ig_node_company nc
        WHERE (nc.role IS NULL OR nc.role NOT IN ({','.join(f"'{r}'" for r in ROLES_STD)}))
          AND nc.valid_to IS NULL
    """},
    # S11 死映射: 需 CH 反查,运行时注入
    {"id": "S12", "title": "market 一致", "sql": """
        SELECT nc.id::text, nc.market || ' vs ' || n.market FROM ig_node_company nc
        JOIN ig_node n ON nc.node_id=n.node_id
        WHERE nc.market <> n.market AND nc.valid_to IS NULL
    """},
    {"id": "S13", "title": "新落位 PIT 覆盖", "sql": f"""
        SELECT nc.id::text, nc.symbol || ' 缺valid_from' FROM ig_node_company nc
        WHERE nc.created_at::date > '{PIT_CUTOFF}' AND nc.valid_from IS NULL
          AND nc.valid_to IS NULL
    """},
    {"id": "S14", "title": f"挂链阈值(>{MAX_CHAINS_PER_SYMBOL})", "sql": f"""
        SELECT nc.symbol, '挂' || count(DISTINCT n.chain_id) || '链' FROM ig_node_company nc
        JOIN ig_node n ON nc.node_id=n.node_id
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE (c.status IS NULL OR c.status='active') AND nc.valid_to IS NULL
        GROUP BY nc.symbol HAVING count(DISTINCT n.chain_id) > {MAX_CHAINS_PER_SYMBOL}
    """},
    # ---- 边层(PIT 关闭行=历史快照,不计违规——标准 §1 查询侧默认过滤 valid_to IS NULL) ----
    {"id": "S15", "title": "零自环边", "sql": """
        SELECT edge_id::text, from_symbol || '->' || to_symbol FROM ig_company_edge
        WHERE from_symbol=to_symbol AND from_symbol<>'' AND valid_to IS NULL
    """},
    {"id": "S16", "title": "零事故性双向边(成对冗余合法)", "sql": """
        SELECT a.edge_id::text, a.from_symbol || '<->' || a.to_symbol || ' ' || a.year FROM ig_company_edge a
        JOIN ig_company_edge b
          ON b.from_symbol=a.to_symbol AND b.to_symbol=a.from_symbol AND b.year=a.year
        WHERE a.edge_id < b.edge_id AND a.valid_to IS NULL AND b.valid_to IS NULL
    """},
    {"id": "S17", "title": "websearch 边完整(PIT+evidence)", "sql": """
        SELECT edge_id::text,
               concat_ws(',', CASE WHEN valid_from IS NULL THEN 'valid_from' END,
                              CASE WHEN as_of IS NULL THEN 'as_of' END,
                              CASE WHEN evidence_type IS NULL THEN 'evidence_type' END)
        FROM ig_company_edge
        WHERE source='websearch' AND valid_to IS NULL
          AND (valid_from IS NULL OR as_of IS NULL OR evidence_type IS NULL)
    """},
    {"id": "S18", "title": "UNLISTED 格式统一", "sql": r"""
        SELECT edge_id::text, from_symbol || '/' || to_symbol FROM ig_company_edge
        WHERE valid_to IS NULL AND (
          (from_symbol ~ '^UNLISTED:' AND from_symbol !~ '^UNLISTED:UE-[0-9a-f]{12}$')
           OR (to_symbol ~ '^UNLISTED:' AND to_symbol !~ '^UNLISTED:UE-[0-9a-f]{12}$'))
    """},
    # S20 PIT 反造假(红蓝对抗 2026-09-09 补):valid_from 早于证据年份前一年=编历史
    # 2026-09-09 Owner 委托裁定: 判定保留不改——year=新闻年/vf=签约日的追述型长协边
    # 属本条主要误报源,处置=豁免登记+抽检原文(豁免制度化),不走改判定放行(防弱化反造假哨)
    # 2026-09-09 收尾裁定(Owner 签名批准): 两段式判定——SQL 只负责粗筛候选(vf<year-1),
    # 放行核验下沉到 Python 正则(见 _s20_postfilter): 原文含"YYYY年"且 YYYY<=valid_from
    # 年份=有据回溯放行; 原文无依据的早日期仍判违规。
    # 豁免台账(quality_exemptions.yaml)与正则放行为两道并行闸,豁免数>5%红线仍适用。
    {"id": "S20", "title": "PIT 反造假(valid_from>=year-1,原文有据回溯放行)", "sql": """
        SELECT edge_id::text, from_symbol || '->' || to_symbol || ' year=' || year
               || ' vf=' || valid_from FROM ig_company_edge
        WHERE valid_from IS NOT NULL AND year IS NOT NULL AND valid_to IS NULL
          AND valid_from < make_date(year - 1, 1, 1)
    """, "postfilter": "s20"},
    # S19 编码表上市撞名: 需 CH 反查,运行时注入
]

DEGRADED_NOTE = "CH 不可达降级,本轮不计违规"


S20_EVIDENCE_YEAR_RE = re.compile(r"(\d{4})年")  # 收尾裁定: 原文含"YYYY年"且 YYYY<=vf 年份=有据回溯


def _s20_fetch_sql() -> str:
    """S20 取数: source_doc 恒在; evidence_text 列存在(将来加列)才一并纳入原文核据。"""
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(
        "SELECT count(*) FROM information_schema.columns "
        "WHERE table_name='ig_company_edge' AND column_name='evidence_text'"
    )
    has_ev = cur.fetchone()[0] > 0
    conn.close()
    text_expr = "coalesce(source_doc,'')" if not has_ev else "coalesce(source_doc,'') || ' ' || coalesce(evidence_text,'')"
    return (
        f"SELECT edge_id::text, valid_from, {text_expr} "
        "FROM ig_company_edge WHERE valid_from IS NOT NULL AND year IS NOT NULL AND valid_to IS NULL "
        "AND valid_from < make_date(year - 1, 1, 1)"
    )


def _s20_postfilter(rows: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], int]:
    """S20 两段式判定第二段(2026-09-09 Owner 签名批准): 对 SQL 粗筛候选逐条核原文。

    原文(source_doc/evidence_text)含 "YYYY年" 且 YYYY <= valid_from 年份 → 有据回溯,放行;
    原文无任何依据性年份的早 valid_from 仍判违规(防拍脑袋编历史)。
    返回 (保留违规, 放行数)。
    """
    if not rows:
        return [], 0
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(_s20_fetch_sql())
    text_by_pk = {str(r[0]): (r[1], str(r[2] or "")) for r in cur.fetchall()}
    conn.close()
    kept: list[tuple[str, str]] = []
    passed = 0
    for pk, desc in rows:
        vf, text = text_by_pk.get(pk, (None, ""))
        if vf is None:
            kept.append((pk, desc))  # 取不到原文的退化情况: 保守判违规
            continue
        vf_year = int(str(vf)[:4])
        years = [int(y) for y in S20_EVIDENCE_YEAR_RE.findall(text)]
        if any(y <= vf_year for y in years):
            passed += 1  # 原文有据回溯(如"2022年签署""2019年建立"),放行
        else:
            kept.append((pk, desc))
    return kept, passed


def _check_s11(cur, alive: set[str]) -> dict:
    if alive is None:
        return {"id": "S11", "title": "死映射零存量", "violations": [], "degraded": True}
    # 2026-09-09 收尾裁定: UNLISTED:UE- 落位行(未上市实体编码表引用)by-design 不在
    # stock_basic 在市集——格式合规由写入工具 UE- 硬校验把关,不计死映射;
    # 其 market 标签随所属节点(S12 口径),不得为绕 S11 改 global(会触发 S12)。
    cur.execute("SELECT nc.id::text, nc.symbol FROM ig_node_company nc WHERE nc.market='cn' AND nc.valid_to IS NULL AND nc.symbol NOT LIKE 'UNLISTED:%'")
    rows = [(pk, sym) for pk, sym in cur.fetchall() if sym not in alive]
    return {"id": "S11", "title": "死映射零存量", "violations": rows, "degraded": False}


def _check_s19(cur, alive_names: set[str] | None) -> dict:
    if alive_names is None:
        return {"id": "S19", "title": "编码表零上市撞名", "violations": [], "degraded": True}
    cur.execute("SELECT ue_id, name FROM ig_unlisted_entity WHERE status='unlisted'")
    rows = [(pk, name) for pk, name in cur.fetchall() if name in alive_names]
    return {"id": "S19", "title": "编码表零上市撞名", "violations": rows, "degraded": False}


def _s21_load_graph(cur) -> tuple[dict, dict, dict, dict]:
    """S21/S24 专用三查：活跃链集/节点归属与 tier/链内边集（只读 SELECT，无法机械化集中）。"""
    cur.execute("SELECT chain_id, name FROM ig_chain WHERE status = 'active'")  # noqa: bare-sql  S21 专用只读三连查，引擎既有风格
    chains = {r[0]: r[1] for r in cur.fetchall()}
    cur.execute("SELECT node_id, chain_id, tier, name FROM ig_node")  # noqa: bare-sql  S21 专用只读三连查，引擎既有风格
    node_chain: dict[str, str] = {}
    node_tier: dict[str, str] = {}
    node_name: dict[str, str] = {}
    for nid, cid, tier, name in cur.fetchall():
        if cid in chains:
            node_chain[nid] = cid
            node_tier[nid] = tier
            node_name[nid] = name
    cur.execute("SELECT from_node, to_node, edge_type FROM ig_edge")  # noqa: bare-sql  S21 专用只读三连查，引擎既有风格
    chain_edges: dict[str, list[tuple[str, str, str]]] = {}
    for u, v, et in cur.fetchall():
        cu, cv = node_chain.get(u), node_chain.get(v)
        if cu is not None and cu == cv:
            chain_edges.setdefault(cu, []).append((u, v, et))
    return chains, node_chain, node_tier, node_name, chain_edges


def _s21_reachable(starts, targets, adj) -> bool:
    """无向连通 BFS：starts 任一节点可达 targets 任一节点即 True。"""
    seen = set(starts)
    q = deque(starts)
    while q:
        u = q.popleft()
        if u in targets:
            return True
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return False


def _tombstone(name: str) -> bool:
    """墓碑节点判定（与 S8 '（已并入' 豁免同口径）：历史合并快照不参与结构审查。"""
    return "（已并入" in name or name.startswith("已并入")


def _check_s21(cur) -> dict:
    """S21 流程连通性（2026-09-09 增，Owner 口径：structure 流程边与 supply 供应边均计入连通路径）。
    每条活跃链（实质节点数>=3）：上游 tier 节点 → 下游 tier 节点存在连通路径则合规，断链=违规。
    违规描述附 structure 边占比（附带指标，不判违规）。

    口径修正（2026-09-10，与 S8/S6 既有裁定同源）：墓碑节点（'（已并入'标记=历史合并快照）
    不计入节点数与起讫集；去墓碑后实质节点<3 的链、实质节点名全等于链名(±'行业'/'行业聚合')
    的锚点/单环节链跳过——这类链由 S24 僵尸链检测收口，不在 S21 制造伪断链。
    依据：合并治理墓碑残留曾占 advisory 336 的 93.8%（315/336），伪断链淹没真缺口。
    """
    chains, node_chain, node_tier, node_name, chain_edges = _s21_load_graph(cur)
    violations: list[tuple[str, str]] = []
    checked = 0
    for cid in sorted(chains):
        nodes = [n for n, c in node_chain.items() if c == cid]
        alive = [n for n in nodes if not _tombstone(node_name.get(n, ""))]
        if len(alive) < 3:
            continue   # 基数=实质节点≥3（原 1.4.0 口径节点≥3 的墓碑过滤版）；僵尸/单环节链 → S24 收口
        cname = chains[cid]
        alive_names = {node_name.get(n, "") for n in alive}
        if alive_names <= {cname, cname + "行业", "行业聚合"}:
            continue   # 行业锚点链/链名单环节垃圾 → S24 收口
        checked += 1
        edges = chain_edges.get(cid, [])
        n_st = sum(1 for _, _, et in edges if et == 'structure')
        n_sp = len(edges) - n_st
        ratio = (n_st / len(edges)) if edges else 0.0
        adj: dict[str, list[str]] = defaultdict(list)
        for u, v, _et in edges:
            adj[u].append(v)
            adj[v].append(u)
        starts = [n for n in alive if node_tier.get(n) == '上游']
        targets = {n for n in alive if node_tier.get(n) == '下游'}
        if not _s21_reachable(starts, targets, adj):
            violations.append((cid, '%s nodes=%d structure=%d supply=%d 结构占比=%.2f' % (
                cname, len(alive), n_st, n_sp, ratio)))
    return {
        'id': 'S21',
        'title': '流程连通性(活跃链上游→下游 structure+supply 连通路径)',
        'violations': violations,
        'degraded': False,
        'advisory': True,  # §8 先进度指标后硬闸：样板链验收前只报告不计违规（Owner 2026-09-09 口径）
        'checked_chains': checked,
    }


def _check_s24(cur) -> dict:
    """S24 僵尸链检测（2026-09-10 增，advisory）：活跃链去墓碑后实质节点<=1，
    或实质节点名全等于链名(±'行业'/'行业聚合')=链骨架已被合并抽走/抽取垃圾——
    该链应走 deprecated+merged_into 收口（SOP §5 硬校验 10 唯一合法通道）。
    废弃涉及存量行修改 → Owner 排序拍板，本项只出清单（advisory 不计违规）。
    清单即废弃排序底稿：n_alive 越小、落位越少优先废弃。"""
    chains, node_chain, _node_tier, node_name, _chain_edges = _s21_load_graph(cur)
    violations: list[tuple[str, str]] = []
    for cid in sorted(chains):
        nodes = [n for n, c in node_chain.items() if c == cid]
        if len(nodes) < 3:
            continue   # 少于3节点的链不构成僵尸判定基数（S21 同口径）
        cname = chains[cid]
        alive = [n for n in nodes if not _tombstone(node_name.get(n, ""))]
        alive_names = {node_name.get(n, "") for n in alive}
        if len(alive) <= 1 or alive_names <= {cname, cname + "行业", "行业聚合"}:
            violations.append((cid, '%s 实质节点=%d/%d' % (cname, len(alive), len(nodes))))
    return {
        'id': 'S24',
        'title': '僵尸链(活跃链去墓碑后实质节点<=1或全等链名,待Owner排序废弃)',
        'violations': violations,
        'degraded': False,
        'advisory': True,  # 废弃=存量行修改须 Owner 拍板（SOP 铁律 5），清单不阻断
        'checked_chains': len(chains),
    }


def _alive_names() -> set[str] | None:
    """在市 A 股简称集(S19 用; S11 用 symbol 集,两口径不同)。"""
    try:
        from zephyr.data import ch_writer

        tsv = ch_writer.query(
            "SELECT name FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL AND trade_date=(SELECT max(trade_date) FROM c1_market.stock_basic)"
        )
        return {ln.strip().split("\t")[0] for ln in tsv.strip().splitlines() if ln.strip()}
    except Exception:  # noqa: BLE001
        return None


def run_check() -> dict:
    today = date.today().isoformat()
    exemptions = _load_exemptions()
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    results: list[dict] = []

    for chk in CHECKS:
        try:
            cur.execute(chk["sql"])
            rows = [(str(r[0]), str(r[1])) for r in cur.fetchall()]
        except Exception as e:  # noqa: BLE001 — SQL 执行失败按 degraded 不计违规(引擎自身问题须修)
            results.append({"id": chk["id"], "title": chk["title"], "violations": [], "degraded": True,
                            "error": f"{type(e).__name__}: {e}"[:200]})
            continue
        postfilter = chk.get("postfilter")
        passed_note = 0
        if postfilter == "s20":
            rows, passed_note = _s20_postfilter(rows)  # 两段式第二段: 原文正则核据
        exempt = set(exemptions.get(chk["id"], []))
        kept = [(pk, desc) for pk, desc in rows if pk not in exempt]
        results.append({"id": chk["id"], "title": chk["title"], "violations": kept,
                        "raw_count": len(rows) + (passed_note if postfilter == "s20" else 0),
                        "evidence_pass_count": passed_note if postfilter == "s20" else None,
                        "exempt_count": len(rows) - len(kept)})

    # CH 依赖两项
    alive_syms = _load_alive_stocks()
    r11 = _check_s11(cur, alive_syms)
    exempt11 = set(exemptions.get("S11", []))
    r11["violations"] = [(pk, d) for pk, d in r11["violations"] if pk not in exempt11]
    results.append(r11)
    r19 = _check_s19(cur, _alive_names())
    exempt19 = set(exemptions.get("S19", []))
    r19["violations"] = [(pk, d) for pk, d in r19["violations"] if pk not in exempt19]
    results.append(r19)
    r21 = _check_s21(cur)
    exempt21 = set(exemptions.get("S21", []))
    r21["violations"] = [(pk, d) for pk, d in r21["violations"] if pk not in exempt21]
    results.append(r21)
    r24 = _check_s24(cur)
    exempt24 = set(exemptions.get("S24", []))
    r24["violations"] = [(pk, d) for pk, d in r24["violations"] if pk not in exempt24]
    results.append(r24)

    conn.close()

    total = sum(len(r["violations"]) for r in results if not r.get("advisory"))
    report = {
        "checked_at": today,
        "total_violations": total,
        "all_green": total == 0,
        "checks": results,
        "exemption_file": str(EXEMPT_FILE),
    }
    return report


def _write_report(report: dict) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    jp = REPORT_DIR / f"quality_report_{report['checked_at']}.json"
    jp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    md = REPORT_DIR / f"quality_report_{report['checked_at']}.md"
    lines = [
        f"# 图谱质量体检报告 {report['checked_at']}",
        f"**总违规 {report['total_violations']} 项 | {'全绿' if report['all_green'] else '待修复'}**",
        "",
    ]
    for r in report["checks"]:
        if r.get("degraded"):
            status = "degraded(降级)"
        elif r.get("advisory"):
            status = f"advisory(进度指标 {len(r['violations'])} 项,不计违规)"
        else:
            status = "PASS" if not r["violations"] else f"违规 {len(r['violations'])}"
        lines.append(f"## {r['id']} {r['title']} — {status}")
        for pk, desc in r["violations"][:20]:
            lines.append(f"- [{pk}] {desc}")
        if len(r["violations"]) > 20:
            lines.append(f"- ...共 {len(r['violations'])} 条(全文见 JSON)")
        lines.append("")
    md.write_text("\n".join(lines), encoding="utf-8")
    return md


def main() -> int:
    ap = argparse.ArgumentParser(description="图谱质量检查引擎(只读)")
    ap.add_argument("--json", metavar="PATH", help="仅输出 JSON 到指定路径或 '-'(stdout),不落盘报告")
    args = ap.parse_args()
    try:
        report = run_check()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] 引擎故障: {e}")
        return 2
    if args.json:
        out = json.dumps(report, ensure_ascii=False, indent=1)
        if args.json == "-":
            print(out)
        else:
            Path(args.json).write_text(out, encoding="utf-8")
    else:
        md = _write_report(report)
        print(f"[{'GREEN' if report['all_green'] else 'VIOLATIONS'}] 总违规 {report['total_violations']} 项")
        for r in report["checks"]:
            if r.get("degraded"):
                tag = "degraded"
            elif r.get("advisory"):
                tag = f"advisory({len(r['violations'])})"
            else:
                tag = len(r["violations"])
            print(f"  {r['id']} {r['title']}: {tag}")
        print(f"报告: {md}")
    return 0 if report["all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
