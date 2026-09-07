# [MODULE] scripts.industry_graph.merge_semiconductor_chains
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 全行业链合并治理的样板(其余行业按同款规则批量化,待 Owner 批准)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删(子链 deprecated+merged_into 不物理删除); 公司迁移 confidence 取 GREATEST; 误挂(000591.SZ)不迁移留 Owner 裁定; 幂等(主键/UNIQUE 锚 ON CONFLICT); 已执行一次(2026-09-07), 复跑零副作用
# [MODIFY-GUARD] MOTHERS 合并方案表(SOP §4.7.4 定稿)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->抛出
# [TTL] permanent
# M10豁免: manual STARTUP 一次性治理脚本
# [TESTS] 执行日志见本会话 commit 信息(15->8: 5 母链/10 子链 deprecated/000591.SZ 11 处未迁移)
"""半导体链合并施工（SOP industry_chain_data_audit_sop §4.7.4 样板执行，2026-09-07）。

只增不删：新建母链节点+迁移公司落位+子链标 deprecated+merged_into。
结果：5 条母链(设备15/材料21/光刻胶35/存储5/封装5 家公司)+3 条已合规链补 category+10 条子链 deprecated。
误挂 000591.SZ(太阳能) 11 处未迁移——留 Owner 裁定移除。

用法::

    python scripts/industry_graph/merge_semiconductor_chains.py
"""
import sys

sys.path.insert(0, r"d:\ZephyrAlpha\src")
import hashlib

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

conn = get_depgraph_pg_connection(read_only=False)
cur = conn.cursor()
SRC = "merge_2026-09-07"
log = []


def chain_id_for(name: str) -> str:
    h = hashlib.md5(name.encode("utf-8")).hexdigest()[:12]
    return f"CH-{h}"


def node_id_for(chain: str, node: str, tier: str) -> str:
    h = hashlib.md5(f"{chain}|{node}|{tier}".encode("utf-8")).hexdigest()[:12]
    return f"ND-{h}"


# 母链定义（SOP §4.7.4 定稿）：name -> (吸收的子链名列表, [(节点名, tier)], )
MOTHERS = {
    "半导体设备产业链": {
        "absorb": ["半导体设备行业", "长鑫科技IPO启幕：半导体设备与材料产业链深度投资"],
        "nodes": [("光刻设备", "设备"), ("刻蚀设备", "设备"), ("薄膜沉积设备", "设备"), ("离子注入设备", "设备"), ("CMP设备", "设备"), ("清洗设备", "设备"), ("检测设备", "设备")],
    },
    "半导体材料产业链": {
        "absorb": ["半导体硅材料行业", "半导体硅片行业", "氮化镓半导体材料行业", "80页PPT全方位解读半导体行业"],
        "nodes": [("硅片", "材料"), ("电子特气", "材料"), ("光掩模", "材料"), ("抛光液", "材料"), ("氮化镓衬底", "材料"), ("靶材", "材料")],
    },
    "光刻胶产业链": {
        "absorb": ["光刻胶产业链行业", "光刻胶行业", "一张图看懂光刻胶"],
        "nodes": [("树脂与单体", "上游"), ("溶剂", "上游"), ("光引发剂", "上游"), ("光刻胶生产", "中游"), ("晶圆制造", "下游"), ("PCB制造", "下游"), ("涂胶显影设备", "设备")],
    },
    "存储芯片产业链": {
        "absorb": ["存储芯片本轮涨价能走多远？一文看懂产业链"],
        "nodes": [("存储晶圆制造", "上游"), ("存储芯片封测", "中游"), ("内存模组", "下游"), ("嵌入式存储", "下游")],
    },
    "先进封装产业链": {
        "absorb": ["一张图看懂倒装芯片行业"],
        "nodes": [("封装基板", "上游"), ("倒装芯片封装", "中游"), ("晶圆级封装", "中游"), ("先进测试", "下游")],
    },
}

# 已合规链：仅补 category/version_year
PATCH_ONLY = {"模拟芯片": "半导体", "光芯片": "半导体", "算力芯片": "半导体"}

# 执行
for mname, spec in MOTHERS.items():
    cid = chain_id_for(mname)
    cur.execute(
        """
        INSERT INTO ig_chain (chain_id, name, category, version_year, market, status, source_note, created_at, updated_at)
        VALUES (%s, %s, '半导体', 2026, 'cn', 'active', %s, now(), now())
        ON CONFLICT (chain_id) DO UPDATE SET updated_at=now()
        """,
        (cid, mname, SRC),
    )
    # 母链节点
    for nname, tier in spec["nodes"]:
        nid = node_id_for(cid, nname, tier)
        cur.execute(
            """
            INSERT INTO ig_node (node_id, chain_id, name, tier, market, created_at, updated_at)
            VALUES (%s, %s, %s, %s, 'cn', now(), now())
            ON CONFLICT (node_id) DO UPDATE SET updated_at=now()
            """,
            (nid, cid, nname, tier),
        )
    # 吸收子链：公司落位迁移到母链"对应 tier 的首个节点"，子链标 deprecated
    for sub in spec["absorb"]:
        cur.execute("SELECT chain_id FROM ig_chain WHERE name=%s AND status='active'", (sub,))
        row = cur.fetchone()
        if not row:
            log.append(f"[skip] 子链不存在或已废弃: {sub}")
            continue
        sub_cid = row[0]
        # 子链全部公司落位
        cur.execute(
            """
            SELECT nc.symbol, nc.role, nc.confidence, nc.evidence_text, nc.source_doc, n.tier, nc.node_id
            FROM ig_node_company nc JOIN ig_node n ON n.node_id=nc.node_id
            WHERE n.chain_id=%s
            """,
            (sub_cid,),
        )
        rows = cur.fetchall()
        moved = 0
        for sym, role, conf, ev, sdoc, tier, old_nid in rows:
            # 000591.SZ（太阳能）误挂处置：SOP 样板裁定降 confidence 保留证据、不迁移（留开放问题）
            if sym == "000591.SZ":
                log.append(f"[misfile] 000591.SZ 未迁移（误挂，留 Owner 裁定）from={sub}")
                continue
            # 目标节点：同 tier 首个，否则中游兜底
            target = None
            for nname, t in spec["nodes"]:
                if t == tier:
                    target = nname
                    break
            if target is None:
                target = spec["nodes"][0][0]
            tnid = node_id_for(cid, target, dict(spec["nodes"])[target])
            cur.execute(
                """
                INSERT INTO ig_node_company (node_id, symbol, role, confidence, evidence_text, source_doc, market, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'cn', now(), now())
                ON CONFLICT (node_id, symbol) DO UPDATE
                  SET confidence=GREATEST(ig_node_company.confidence, EXCLUDED.confidence), updated_at=now()
                """,
                (tnid, sym, role, conf, ev, sdoc or f"merged_from:{sub}"),
            )
            moved += 1
        # 子链标 deprecated
        cur.execute(
            "UPDATE ig_chain SET status='deprecated', source_note=%s, updated_at=now() WHERE chain_id=%s",
            (f"merged_into:{cid}", sub_cid),
        )
        log.append(f"[merged] {sub} -> {mname}: {moved} companies moved")

# 已合规链补 category/version_year
for pname, cat in PATCH_ONLY.items():
    cur.execute(
        "UPDATE ig_chain SET category=%s, version_year=COALESCE(version_year,2026), updated_at=now() "
        "WHERE name=%s AND status='active'",
        (cat, pname),
    )
    log.append(f"[patched] {pname}: category={cat}")

conn.commit()

# 复核
cur.execute("SELECT name, status, source_note FROM ig_chain WHERE name ~ '半导体|集成电路|芯片|晶圆|光刻|存储芯片|封测|氮化镓|硅片|硅材料|倒装|算力|模拟|光芯片' ORDER BY status, name")
for r in cur.fetchall():
    log.append(f"[final] {r[0]} | {r[1]} | {r[2] or ''}")
cur.execute(
    """
    SELECT c.name, COUNT(nc.id) FROM ig_chain c JOIN ig_node n ON n.chain_id=c.chain_id
    LEFT JOIN ig_node_company nc ON nc.node_id=n.node_id
    WHERE c.name IN ('半导体设备产业链','半导体材料产业链','光刻胶产业链','存储芯片产业链','先进封装产业链')
    GROUP BY c.name
    """
)
log.append("[companies per mother] " + str(cur.fetchall()))
conn.close()
print("\n".join(log))
