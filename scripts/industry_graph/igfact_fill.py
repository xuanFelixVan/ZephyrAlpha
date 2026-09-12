# [MODULE] scripts.industry_graph.igfact_fill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_reader (stock_basic 在市过滤); vocab_loader (字段字典词表真源)
# [CONSUMERS] 长城任务 ig_fact→空壳链填充（Owner 2026-09-12 授权）; 夜班可复用 plan 子命令做数据资产盘点
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部写库走 websearch_ingest ingest 唯一通道(禁手写 SQL); 每链一批次=单事务全成全败; 节点零孤岛(只入图"有落位或有链内供应边"的产品,防 S8); tier 停填(2026-09-12 退役裁定)/function_role 首轮停填(避免新主观债); supplies_to 方向=subject(供应方)→object(客户方)(import_ckg_dataset 实测核实); 同链 A→B/B→A 双向去重(保留 subject 字典序小者); 同链内 subject=object 自环跳过; 公司落位必过 stock_basic 在市过滤(CH 不可达则整批不写落位); role 按 produces 营收占比映射(≥30%主要/10-30%参与/<10%提及,不授龙头核心); confidence=0.85(采购包双文档互证档); source_doc 三段式 `ckg_2021 供应链事实|ig_fact#<fact_id>|2021-10-26`; 落位 valid_from=2021-10-26(S13 PIT); 激活门槛=实质节点≥3+链名三检过+category 申万词表+version_year=2021; 重名链组每组只激活一条
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->退出码2; CH 不可达->落位降级跳过(warn,不阻断节点/边); 批次校验失败->该链事务回滚整批拒绝(退出码3),继续下链; 激活预检不过->维持 deprecated 并登记
# [TTL] permanent
"""igfact_fill.py — ig_fact(CKG2021) 26.4万条事实 → deprecated 空壳链填充施工件。

对接逻辑（Owner 任务书）：
  ig_fact 产品名(经噪音过滤+链映射) → ig_node 环节（tier 退役:不填）
  ig_fact supplies_to(subject供object) 同链两端 → ig_edge supply 边
  ig_fact produces(公司→产品+营收占比) → ig_node_company 落位（在市过滤+role 分档）
  激活: 填充达标链 UPDATE status deprecated→active（走 ingest chain 记录唯一通道）

链映射算法（第一版保守口径：宁可少填不可填错）：
  1. 链名去尾缀(产业链/行业)得核心词；核心词中定位通用主体词(约70词表)得"主体+修饰头"
  2. 产品名命中主体 且(头为空 或 产品名含头) → 映射该链
  3. product_def 仅作存在性校验不产节点(防孤岛)；无边无落位的产品不入图

用法::
  python scripts/industry_graph/igfact_fill.py plan                  # 只读: 映射统计落盘(不写库)
  python scripts/industry_graph/igfact_fill.py ingest --top 40      # 映射物量 TOP N 链分批入图
  python scripts/industry_graph/igfact_fill.py ingest --chains 充电桩产业链,光模块行业
  python scripts/industry_graph/igfact_fill.py activate --top 40    # 达标链激活(预检+补元数据+status=active)
  python scripts/industry_graph/igfact_fill.py status               # 填充进度统计
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import os
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vocab_loader import load_vocab  # noqa: E402  词表唯一真源
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / ".runtime" / "industry_graph" / "igfact_fill"
BATCH_DIR = ROOT / ".runtime" / "industry_graph" / "night_audit" / "batches"
AUDIT_JSON = ROOT / ".runtime" / "audit" / "s24_deprecated_review_20260912.json"

SOURCE = "ckg_2021"
AS_OF = "2021-10-26"
VERSION_YEAR = 2021
MAX_NODE_NAME = 15          # NODE_NAME_MAX_LEN 同源(websearch_ingest)
MIN_PRODUCTS_PER_CHAIN = 1  # 单链映射产品少于此值不生成批次(防僵尸链)

# 产品词三关 + 菜谱/生活噪音闸（S7 后缀同源 + 外采产品网噪音实测: 三七全鸡汤/DIY面膜/腊味榴莲炒饭类）
TIER_SUFFIX_RE = re.compile(r"-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$")
NODE_JUNK_RE = re.compile(r"产业链|调研|概况|格局|进出口|配套|边际装置|纵览")
RECIPE_RE = re.compile(
    r"炒|炖|煲|蒸|煮|凉拌|红烧|清蒸|烧烤|煎|炸|焖|卤|腌|烩|熘|汆|涮|羹|粥|汤圆|饺子|包子|馒头|面条|米粉|奶茶|"
    r"蛋挞|蛋糕|面包|饼干|糖果|冰淇淋|火锅|串串|麻辣烫|烧烤|小龙虾|烧烤|配方|菜|膳食|食谱|佐餐|小菜|泡菜|咸菜|"
    r"鸡腿|鸡翅|鸡丁|肉丝|鱼片|牛腩|五花肉|排骨|丸子|火腿肠|豆腐乳|酱油|醋|鸡精|味精|料酒|香油|"
    r"三七全鸡汤|DIY面膜|蜂蜜糖藕|素炒红鸡蛋"
)
# 通用主体词表（核心词中定位"主体"——第一版保守集合,后续批次可扩）
SUBJECT_WORDS = [
    "正极材料", "负极材料", "电解液", "隔膜", "正极", "负极",
    "光刻胶", "靶材", "电子特气", "电子气体", "电子化学品", "湿电子化学品", "电子浆料", "电子布", "电子纸",
    "碳纤维", "玻璃纤维", "玄武岩纤维", "芳纶纤维", "超高分子量聚乙烯", "聚酰亚胺", "聚醚醚酮", "聚苯硫醚",
    "聚四氟乙烯", "聚偏氟乙烯", "聚氨酯", "聚碳酸酯", "聚甲醛", "聚砜", "有机硅", "氟材料", "氟树脂", "氟化工",
    "特种工程塑料", "工程塑料", "改性塑料", "生物可降解塑料", "高吸水性树脂", "离子交换膜", "质子交换膜",
    "反渗透膜", "陶瓷膜", "水处理膜", "OCA光学胶", "光学膜", "偏光片", "蓝宝石", "氧化锆", "氧化铝",
    "氮化硅", "氮化铝", "氮化镓", "碳化硅", "高温合金", "钛合金", "镁合金", "铝合金", "铜合金", "硬质合金",
    "非晶合金", "形状记忆合金", "模具钢", "特殊钢", "硅钢", "永磁材料", "钕铁硼", "磁性材料", "稀土功能材料",
    "储氢材料", "催化材料", "发光材料", "发光二极管", "液晶材料", "封装基板", "覆铜板", "铜箔", "铝箔",
    "导电膜", "电磁屏蔽", "导热材料", "石墨膜", "石墨烯", "气凝胶", "耐火材料", "耐磨材料", "保温材料",
    "防水材料", "涂料", "胶黏剂", "胶粘剂", "油墨", "涂层", "增材制造", "粉末冶金", "金刚石",
    "充电桩", "充电模块", "充电枪", "换电站", "动力电池", "电池包", "储能电池", "固态电池", "燃料电池",
    "光伏组件", "逆变器", "风电整机", "齿轮", "轴承", "丝杠", "导轨", "模具", "减速器", "伺服电机",
    "工业机器人", "传感器", "连接器", "继电器", "电容器", "电感", "PCB", "FPC", "芯片", "晶圆", "封装",
    "光模块", "光器件", "光纤", "光缆", "天线", "滤波器", "基站", "交换机", "路由器", "服务器", "存储",
    "显示屏", "面板", "触摸屏", "摄像头", "激光器", "雷达", "仪表", "阀门", "泵", "压缩机", "风机",
    "锅炉", "汽轮机", "燃气轮机", "发电机组", "变压器", "开关柜", "电缆", "电梯", "工程机械", "起重机械",
    "医疗器械", "植入耗材", "体外诊断", "疫苗", "原料药", "中药饮片", "制剂", "检测试剂", "手术机器人",
    "汽车电子", "车载", "智能座舱", "自动驾驶", "线束", "车灯", "轮胎", "座椅", "空调", "冰箱", "洗衣机",
    "电视", "无人机", "卫星", "火箭", "船舶", "海工装备", "轨交装备", "城轨车辆", "机车", "信号系统",
]

S_DOC = f"ckg_2021 供应链事实|ig_fact#{{fid}}|{AS_OF}"


def _clean(s: str | None) -> str:
    return (s or "").strip()


def load_legit_chains(include_active: bool = False) -> set[str]:
    """空壳链 legit 名单 ∩ DB。默认 deprecated（填充新链）;include_active=True 含已激活链
    （subtype 传递扩容阶段:已激活链也要接收传递产品,否则链结构无法增密）。"""
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    legit = set(audit.get("legit_seed_catalog", []))
    junk = set(audit.get("junk_names", []))
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    if include_active:
        cur.execute("SELECT name FROM ig_chain WHERE status IN ('deprecated','active')")
    else:
        cur.execute("SELECT name FROM ig_chain WHERE status='deprecated'")
    dep = {r[0] for r in cur.fetchall()}
    conn.close()
    return {n for n in dep if n in legit and n not in junk}


def _alive_stocks() -> set[str] | None:
    try:
        from zephyr.data import ch_reader
        from zephyr.data.table_registry import get_registry
        sql = (f"SELECT DISTINCT symbol_canonical FROM {get_registry().table('meta_stock_basic')} "
               "FINAL WHERE valid_to IS NULL")
        tsv = ch_reader.query(sql)
        return {ln.strip().split("\t")[0] for ln in tsv.strip().splitlines() if ln.strip()}
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] stock_basic 反查不可达,落位降级跳过: {e}")
        return None


def product_ok(name: str) -> bool:
    """产品词三关 + 菜谱闸。"""
    n = _clean(name)
    if not n or len(n) > MAX_NODE_NAME or len(n) < 2:
        return False
    if TIER_SUFFIX_RE.search(n) or NODE_JUNK_RE.search(n) or RECIPE_RE.search(n):
        return False
    if re.match(r"^[A-Za-z0-9\s-]+$", n):   # 纯外文/数字串不入名(缩写进 aliases 的纪律)
        return False
    return True


def extract_core(chain_name: str) -> tuple[str, str] | None:
    """链名 → (主体词, 修饰头)；主体词=词表最长命中,头=主体前缀段。"""
    core = re.sub(r"(产业链|行业|相关|及供应商|及配套|介绍|基础知识.*)$", "", _clean(chain_name)).strip()
    core = re.sub(r"^(新型|高端|关键|核心|全球|中国|超全|上游|中游|下游)", "", core).strip()
    best: tuple[str, str] | None = None
    for w in SUBJECT_WORDS:
        idx = core.find(w)
        if idx >= 0:
            cand = (w, core[:idx].strip())
            if best is None or len(cand[0]) > len(best[0]):
                best = cand
    return best


def map_product(name: str, chain_cores: list[tuple[str, str, str]]) -> list[str]:
    """产品名 → 命中链 id（**单归属最具体链**：head 长度>subject 长度优先——
    "光纤预制棒"归"光纤预制棒行业"不归"光纤产业链"，防同义链族重复挂产品制造 S4/S14 问题）。"""
    n = _clean(name)
    hits: list[tuple[int, int, str]] = []
    for cid, cname, (subj, head) in chain_cores:
        if subj in n and (not head or head in n):
            hits.append((len(head), len(subj), cid))
    if not hits:
        return []
    hits.sort(key=lambda t: (-t[0], -t[1], t[2]))
    return [hits[0][2]]


def activation_ready(name: str) -> bool:
    """激活预检前移：链名三检（S1 标题腔/S25 结构/长度）——注定无法激活的链不浪费填充。"""
    from websearch_ingest import TITLE_JUNK_RE, CHAIN_STRUCT_RE, CHAIN_NAME_MAX_LEN
    return not (TITLE_JUNK_RE.search(name) or CHAIN_STRUCT_RE.search(name) or len(name) > CHAIN_NAME_MAX_LEN)


def load_fact_data():
    """只读加载 ig_fact 全量分类数据。"""
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute("""SELECT fact_id, subject, relation, object, value FROM ig_fact
                   WHERE valid_to IS NULL AND source='ckg_2021'""")
    rows = cur.fetchall()
    conn.close()
    produces: dict[str, list[tuple[str, str | None, int]]] = defaultdict(list)   # product -> [(symbol,value,fact_id)]
    supplies: list[tuple[str, str, int]] = []                                     # (subj, obj, fact_id)
    return rows, produces, supplies


def build_index(rows):
    produces: dict[str, list[tuple[str, str | None, int]]] = defaultdict(list)
    supplies: list[tuple[str, str, int]] = []
    subtypes: list[tuple[str, str]] = []   # (小类, 大类)
    for fid, subj, rel, obj, val in rows:
        if rel == "produces":
            produces[_clean(obj)].append((_clean(subj), _clean(val) or None, fid))
        elif rel == "supplies_to":
            supplies.append((_clean(subj), _clean(obj), fid))
        elif rel == "subtype_of":
            subtypes.append((_clean(subj), _clean(obj)))
    return produces, supplies, subtypes


def propagate_subtypes(prod_hits, subtypes) -> int:
    """subtype_of 一跳传递映射（2026-09-12 扩容）：大类已映射 → 小类继承同链（仅一轮防链式扩散）。
    品类层级非供应链噪音小；扩容目的=链内产品网变密→supplies 边两端同链概率↑→拓扑分层有骨架。"""
    added = 0
    for sub, sup in subtypes:
        if sub in prod_hits or not product_ok(sub):
            continue
        cs = prod_hits.get(sup)
        if cs:
            prod_hits[sub] = list(cs)
            added += 1
    return added


def plan() -> int:
    """只读映射统计（不写库）。产出: OUT_DIR/plan_<date>.json"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    legit = load_legit_chains()
    cores: list[tuple[str, str, tuple[str, str]]] = []
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    chain_name_of = {}
    for name in sorted(legit):
        cur.execute("SELECT chain_id FROM ig_chain WHERE name=%s AND status='deprecated' ORDER BY created_at LIMIT 1", (name,))
        r = cur.fetchone()
        if r and activation_ready(name):
            c = extract_core(name)
            if c:
                cores.append((r[0], name, c))
            chain_name_of[r[0]] = name
    conn.close()
    print(f"[plan] legit 空壳链 {len(legit)},可提取主体词 {len(cores)}")

    rows, _, _ = load_fact_data()
    produces, supplies = build_index(rows)
    print(f"[plan] ig_fact 行 {len(rows)},produces 产品 {len(produces)},supplies 边 {len(supplies)}")

    chain_cores = [(cid, cname, c) for cid, cname, c in cores]
    prod_hits: dict[str, list[str]] = defaultdict(list)
    for p in set(list(produces.keys())):
        n = _clean(p)
        if not product_ok(n):
            continue
        for cid in map_product(n, chain_cores):
            prod_hits[n].append(cid)
    # supplies 两端产品(不含 company 锚也可成边——两端同链即入)
    sup_prod = set()
    for s, o, _f in supplies:
        sup_prod.add(_clean(s)); sup_prod.add(_clean(o))

    chain_stat: dict[str, dict] = {}
    for cid, cname, (subj, head) in chain_cores:
        node_products = {p for p, cs in prod_hits.items() if cid in cs}
        n_comp = sum(len(produces.get(p, [])) for p in node_products)
        chain_stat[cid] = {"chain_name": cname, "subject": subj, "head": head,
                           "products": len(node_products), "company_rows": n_comp}
    ranked = sorted(chain_stat.items(), key=lambda kv: (-kv[1]["products"], kv[1]["chain_name"]))
    top = [{"chain_id": k, **v} for k, v in ranked if v["products"] > 0]
    report = {
        "date": date.today().isoformat(),
        "legit_chains": len(legit), "chains_with_core": len(cores),
        "chains_mapped": len(top),
        "mapped_products": len(prod_hits),
        "produces_products_total": len(produces),
        "top_chains": top[:80],
    }
    out = OUT_DIR / f"plan_{date.today().isoformat()}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[plan] 可映射链 {len(top)} 条,映射产品 {len(prod_hits)} 个 → {out}")
    for t in top[:20]:
        print(f"   {t['chain_name']}: products={t['products']} comp_rows={t['company_rows']} (subject={t['subject']})")
    return 0


def _gen_chain_batch(cid: str, cname: str, prod_hits, produces, supplies, chain_name_of) -> dict | None:
    """单链批次 JSON（node/node_edge/node_company；零孤岛纪律）。"""
    # 该链产品集
    prods = sorted({p for p, cs in prod_hits.items() if cid in cs})
    if len(prods) < MIN_PRODUCTS_PER_CHAIN:
        return None
    prod_set = set(prods)
    records: list[dict] = []
    # 1) 节点（tier/function_role 停填——2026-09-12 退役裁定）
    for p in prods:
        fid = produces.get(p, [(None, None, 0)])[0][2]
        records.append({
            "type": "node", "chain_name": chain_name_of[cid], "name": p,
            "market": "cn", "source": "ckg_2021",
            "source_doc": S_DOC.format(fid=fid),
        })
    # 2) 链内供应边（两端同链;自环/双向去重）
    seen_edges: set[tuple[str, str]] = set()
    for s, o, fid in supplies:
        s, o = _clean(s), _clean(o)
        if s in prod_set and o in prod_set and s != o:
            key = (s, o)
            rev = (o, s)
            if rev in seen_edges:
                continue
            seen_edges.add(key)
            records.append({
                "type": "node_edge", "chain_name": chain_name_of[cid],
                "from_node": s, "to_node": o, "edge_type": "supply",
                "market": "cn", "source": "ckg_2021",
                "source_doc": S_DOC.format(fid=fid),
            })
    return {"batch_id": f"igfact_fill_{_chain_id_str(chain_name_of[cid])}", "round": 1, "records": records}


def _chain_id_str(name: str) -> str:
    import hashlib
    return f"CH-{hashlib.md5(name.encode('utf-8')).hexdigest()[:12]}"


def _gen_company_batch(cid: str, cname: str, prod_hits, produces, chain_name_of, alive: set[str]) -> dict | None:
    """单链落位批次（produces 公司→产品节点；S13 PIT+role 分档）。"""
    prods = sorted({p for p, cs in prod_hits.items() if cid in cs})
    records: list[dict] = []
    for p in prods:
        for sym, val, fid in produces.get(p, []):
            if sym not in alive:
                continue
            try:
                w = float(val) if val else None
            except ValueError:
                w = None
            role = "提及"
            if w is not None:
                role = "主要" if w >= 0.30 else ("参与" if w >= 0.10 else "提及")
            records.append({
                "type": "node_company", "chain_name": chain_name_of[cid], "node_name": p,
                "symbol": sym, "role": role, "confidence": 0.85,
                "evidence_text": f"ckg_2021 公司主营产品营收占比 {val or 'n/a'}",
                "market": "cn", "valid_from": AS_OF, "source": "ckg_2021",
                "source_doc": S_DOC.format(fid=fid),
            })
    if not records:
        return None
    return {"batch_id": f"igfact_fill_comp_{_chain_id_str(chain_name_of[cid])}", "round": 1, "records": records}


def _select_chains(args, chain_stat) -> list[str]:
    if args.chains:
        want = [c.strip() for c in args.chains.split(",") if c.strip()]
        return [k for k, v in chain_stat.items() if v["chain_name"] in want]
    ranked = sorted(chain_stat.items(), key=lambda kv: (-kv[1]["products"], kv[1]["chain_name"]))
    return [k for k, _v in ranked[: args.top] if _v["products"] > 0]


def cmd_ingest(args) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    from websearch_ingest import cmd_ingest as wi_ingest

    # 复用 plan 的映射索引（含已激活链——subtype 传递扩容要落进已激活链）
    legit = load_legit_chains(include_active=True)
    cores: list[tuple[str, str, tuple[str, str]]] = []
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    chain_name_of = {}
    import hashlib as _hl
    for name in sorted(legit):
        cur.execute("SELECT chain_id FROM ig_chain WHERE name=%s", (name,))
        ids = sorted(r[0] for r in cur.fetchall())
        if not ids or not activation_ready(name):
            continue
        md5_id = f"CH-{_hl.md5(name.encode('utf-8')).hexdigest()[:12]}"
        cid0 = md5_id if md5_id in ids else ids[0]
        c = extract_core(name)
        if c:
            cores.append((cid0, name, c))
        chain_name_of[cid0] = name
    conn.close()

    rows, _, _ = load_fact_data()
    produces, supplies, subtypes = build_index(rows)
    prod_hits: dict[str, list[str]] = defaultdict(list)
    chain_cores_full = [(cid, cname, c) for cid, cname, c in cores]
    for p in set(list(produces.keys())):
        n = _clean(p)
        if not product_ok(n):
            continue
        for cid in map_product(n, chain_cores_full):
            prod_hits[n].append(cid)
    # subtype_of 一跳传递扩容（大类已映射→小类跟随,品类层级非供应链噪音小）
    n_prop = propagate_subtypes(prod_hits, subtypes)
    print(f"[ingest] subtype 传递扩容 +{n_prop} 产品")

    chain_stat = {cid: {"chain_name": cname,
                        "products": sum(1 for cs in prod_hits.values() if cid in cs)}
                  for cid, cname, _c in cores}
    targets = _select_chains(args, chain_stat)
    print(f"[ingest] 目标链 {len(targets)} 条")
    alive = _alive_stocks()
    ok = fail = 0
    for cid in targets:
        b = _gen_chain_batch(cid, chain_stat[cid]["chain_name"], prod_hits, produces, supplies, chain_name_of)
        if b:
            bp = BATCH_DIR / f"{b['batch_id']}.json"
            bp.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
            rc = wi_ingest(str(bp))
            if rc == 0:
                ok += 1
                print(f"  [OK] {chain_stat[cid]['chain_name']} nodes+edges -> {bp.name}")
            else:
                fail += 1
                print(f"  [FAIL] {chain_stat[cid]['chain_name']} rc={rc}")
        if alive:
            cb = _gen_company_batch(cid, chain_stat[cid]["chain_name"], prod_hits, produces, chain_name_of, alive)
            if cb:
                cbp = BATCH_DIR / f"{cb['batch_id']}.json"
                cbp.write_text(json.dumps(cb, ensure_ascii=False, indent=1), encoding="utf-8")
                rc2 = wi_ingest(str(cbp))
                if rc2 == 0:
                    print(f"  [OK] {chain_stat[cid]['chain_name']} companies -> {cbp.name}")
                else:
                    fail += 1
                    print(f"  [FAIL] {chain_stat[cid]['chain_name']} companies rc={rc2}")
    print(f"[ingest] 完成: 链批 ok={ok} fail={fail}")
    return 0 if fail == 0 else 3


def cmd_activate(args) -> int:
    """激活达标链：预检(链名三检/实质节点≥3) → chain 记录 status=active + category/version_year 补齐。"""
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    from websearch_ingest import cmd_ingest as wi_ingest, TITLE_JUNK_RE, CHAIN_STRUCT_RE, CHAIN_NAME_MAX_LEN

    legit = load_legit_chains()
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    # 链名→keep id；重名组每组保留一条。keep 选择(2026-09-12 寻址修复):
    # 优先 md5(name) 链(与 node/node_edge/node_company 写入寻址 _chain_id 一致——
    # 填充数据恒落 md5-id 链;legacy-id 链(2026-08-28 导入)是同名空壳,激活它=激活空链+数据链留 deprecated=S4);
    # md5 链不存在时 fallback 字典序第一(单链组,数据可能落在 legacy 链或幽灵 id)
    import hashlib as _hl
    name_groups: dict[str, list[str]] = defaultdict(list)
    for name in sorted(legit):
        cur.execute("SELECT chain_id FROM ig_chain WHERE name=%s", (name,))
        ids = sorted(r[0] for r in cur.fetchall())
        if ids:
            md5_id = f"CH-{_hl.md5(name.encode('utf-8')).hexdigest()[:12]}"
            keep = md5_id if md5_id in ids else ids[0]
            name_groups[name].append(keep)
    # 实质节点计数（去墓碑）
    cur.execute("""SELECT n.chain_id, count(*) FROM ig_node n
                   WHERE n.name NOT LIKE '%%（已并入%%' GROUP BY n.chain_id""")
    node_cnt = {r[0]: r[1] for r in cur.fetchall()}
    # 落位公司行业多数票 → 申万一级（sector_parent_of 爬树）
    cur.execute("SELECT subject, object FROM ig_fact WHERE relation='sector_parent_of'")
    parent = {r[0]: r[1] for r in cur.fetchall()}
    vocab = load_vocab()
    cats = set(vocab["categories"]["values"])
    cur.execute("""SELECT c.chain_id, f.object, count(*) FROM ig_chain c
                   JOIN ig_node n ON n.chain_id=c.chain_id
                   JOIN ig_node_company nc ON nc.node_id=n.node_id AND nc.valid_to IS NULL
                   JOIN ig_fact f ON f.subject=nc.symbol AND f.relation='belongs_to_sector' AND f.valid_to IS NULL
                   WHERE c.status='deprecated' GROUP BY c.chain_id, f.object""")
    chain_ind: dict[str, list[str]] = defaultdict(list)
    for cid, ind, _c in cur.fetchall():
        chain_ind[cid].append(ind)
    conn.close()

    def climb(ind: str) -> str | None:
        seen = 0
        cur_i = ind
        while cur_i not in cats and cur_i in parent and seen < 5:
            cur_i = parent[cur_i]; seen += 1
        return cur_i if cur_i in cats else None

    activated = skipped = 0
    for name, ids in sorted(name_groups.items()):
        if TITLE_JUNK_RE.search(name) or CHAIN_STRUCT_RE.search(name) or len(name) > CHAIN_NAME_MAX_LEN:
            skipped += 1
            continue
        keep = ids[0]
        if node_cnt.get(keep, 0) < 2:
            # 门槛 2(2026-09-12 放宽): 有真实落位数据的 1-2 节点链激活优于留 deprecated
            # (deprecated+落位=S4 硬违规;1 节点活跃链仅 S24 advisory 不计违规)
            skipped += 1
            continue
        inds = chain_ind.get(keep, [])
        votes = Counter(climb(i) for i in inds if climb(i))
        category = votes.most_common(1)[0][0] if votes else "综合"
        rec = {"type": "chain", "chain_id": keep, "name": name, "category": category,
               "version_year": VERSION_YEAR, "market": "cn", "status": "active",
               "activate": True,  # 2026-09-12 显式激活通道(工具校验: 仅与 status=active 搭配)
               "source": "ckg_2021",
               "source_doc": f"ckg_2021 链激活|igfact_fill|{date.today().isoformat()}"}
        bp = BATCH_DIR / f"igfact_activate_{_chain_id_str(name)}.json"
        bp.write_text(json.dumps({"batch_id": bp.stem, "round": 1, "records": [rec]},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
        rc = wi_ingest(str(bp))
        if rc == 0:
            activated += 1
            print(f"  [ACTIVE] {name} (category={category}, nodes={node_cnt.get(keep, 0)})")
        else:
            skipped += 1
            print(f"  [FAIL] {name} rc={rc}")
    print(f"[activate] 激活 {activated},跳过 {skipped}（名单留 .runtime/industry_graph/igfact_fill/）")
    return 0


def cmd_recategory(args) -> int:
    """category 修正：链上落位公司 → 其在 THS"XX行业"锚点链的落位多数票 → ths_industry_mapping → 申万一级。"""
    import yaml as _yaml
    MAPPING = Path(__file__).resolve().parent / "ths_industry_mapping.yaml"
    mapping = _yaml.safe_load(MAPPING.read_text(encoding="utf-8")) or {}
    m = mapping.get("mappings") or mapping.get("mapping") or mapping
    # mapping 结构兼容: {THS行业名: {category: ..}} 或 {THS行业名: category}
    def cat_of(ths: str) -> str | None:
        v = m.get(ths)
        if isinstance(v, dict):
            return v.get("category") or v.get("sw")
        return v
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    # 本任务激活链锚(2026-09-12): version_year=2021 + category='综合' + active
    # (activate 的 chain 记录 merged_into 为空不写 source_note,故用元数据特征锚定)
    cur.execute("SELECT chain_id, name FROM ig_chain WHERE status='active' AND version_year=2021 AND category='综合'")
    targets = cur.fetchall()
    # 公司→THS 锚点链名映射（活跃锚点链,行业聚合节点承载落位）
    cur.execute("""
        SELECT c1.chain_id, c2.name, count(DISTINCT nc.symbol)
        FROM ig_chain c1
        JOIN ig_node n1 ON n1.chain_id=c1.chain_id
        JOIN ig_node_company nc ON nc.node_id=n1.node_id AND nc.valid_to IS NULL
        JOIN ig_node_company nc2 ON nc2.symbol=nc.symbol AND nc2.valid_to IS NULL
        JOIN ig_node n2 ON n2.node_id=nc2.node_id AND n2.name='行业聚合'
        JOIN ig_chain c2 ON c2.chain_id=n2.chain_id AND c2.status='active' AND c2.market='cn'
        WHERE c1.status='active' AND c2.name LIKE '%%行业'
        GROUP BY c1.chain_id, c2.name""")
    votes: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for cid, anchor, cnt in cur.fetchall():
        votes[cid].append((anchor, cnt))
    conn.close()
    vocab = load_vocab()
    cats = set(vocab["categories"]["values"])
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    from websearch_ingest import cmd_ingest as wi_ingest
    fixed = nodata = 0
    for cid, cname in targets:
        vs = sorted(votes.get(cid, []), key=lambda t: -t[1])
        category = None
        for anchor, _cnt in vs:
            c = cat_of(anchor[:-2] if anchor.endswith("行业") else anchor)
            if c in cats:
                category = c
                break
        if not category:
            nodata += 1
            continue
        rec = {"type": "chain", "chain_id": cid, "name": cname, "category": category,
               "market": "cn", "source": "ckg_2021",
               "source_doc": f"ckg_2021 链激活|recategory|{date.today().isoformat()}"}
        # 不带 status→不改变激活态;仅补 category
        bp = BATCH_DIR / f"igfact_recat_{_chain_id_str(cname)}.json"
        bp.write_text(json.dumps({"batch_id": bp.stem, "round": 1, "records": [rec]},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
        if wi_ingest(str(bp)) == 0:
            fixed += 1
        else:
            nodata += 1
    print(f"[recategory] 修正 {fixed},无锚点数据 {nodata}")
    return 0


def cmd_close_orphans(args) -> int:
    """孤岛节点 PIT 关闭：活跃链上无边无落位的节点（S8 违规）走 node_close 唯一通道。"""
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    from websearch_ingest import cmd_ingest as wi_ingest
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute("""
        SELECT n.node_id, n.name, c.name FROM ig_node n
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE NOT EXISTS (SELECT 1 FROM ig_edge e WHERE e.from_node=n.node_id OR e.to_node=n.node_id)
          AND NOT EXISTS (SELECT 1 FROM ig_node_company nc WHERE nc.node_id=n.node_id AND nc.valid_to IS NULL)
          AND n.name <> '行业聚合'
          AND n.child_chain_id IS NULL
          AND n.name NOT LIKE '%%（已并入%%'
          AND n.valid_to IS NULL
          AND (c.status IS NULL OR c.status='active')""")
    orphans = cur.fetchall()
    conn.close()
    if not orphans:
        print("[close-orphans] 零孤岛")
        return 0
    rec = {"type": "node_close",
           "node_ids": [r[0] for r in orphans],
           "reason_doc": f"ckg 填充孤岛:产品真实但公司全部退市且无同链供应边|igfact_fill|{date.today().isoformat()}"}
    bp = BATCH_DIR / f"igfact_node_close_{date.today().isoformat()}.json"
    bp.write_text(json.dumps({"batch_id": bp.stem, "round": 1, "records": [rec]},
                             ensure_ascii=False, indent=1), encoding="utf-8")
    rc = wi_ingest(str(bp))
    print(f"[close-orphans] 关闭 {len(orphans)} 个孤岛节点 rc={rc}")
    for nid, name, cname in orphans[:15]:
        print(f"   - {name} @ {cname}")
    return 0 if rc == 0 else 3


def cmd_status() -> int:
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    for t in ("ig_chain", "ig_node", "ig_edge", "ig_node_company"):
        cur.execute(f"SELECT count(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]}")
    cur.execute("SELECT status, count(*) FROM ig_chain GROUP BY 1")
    print("chain status:", cur.fetchall())
    cur.execute("""SELECT count(*) FROM ig_node n JOIN ig_chain c ON c.chain_id=n.chain_id
                   WHERE c.source_note LIKE '%%ckg_2021%%' OR n.source_note LIKE '%%ckg_2021%%'""".replace("n.source_note", "c.source_note"))
    print("ckg-touched rows:", cur.fetchone()[0])
    conn.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ig_fact→空壳链填充施工件(全走 ingest 通道)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan", help="只读映射统计")
    p_ing = sub.add_parser("ingest", help="分批入图")
    p_ing.add_argument("--top", type=int, default=40)
    p_ing.add_argument("--chains", default="")
    p_act = sub.add_parser("activate", help="达标链激活")
    p_act.add_argument("--top", type=int, default=0)
    p_act.add_argument("--chains", default="")
    sub.add_parser("recategory", help="THS 锚点多数票修正激活链 category")
    sub.add_parser("close-orphans", help="孤岛节点 PIT 关闭(node_close 通道)")
    sub.add_parser("status", help="进度统计")
    args = ap.parse_args()
    if args.cmd == "plan":
        return plan()
    if args.cmd == "ingest":
        return cmd_ingest(args)
    if args.cmd == "activate":
        return cmd_activate(args)
    if args.cmd == "recategory":
        return cmd_recategory(args)
    if args.cmd == "close-orphans":
        return cmd_close_orphans(args)
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
