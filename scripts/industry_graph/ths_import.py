# [BLUEPRINT] NIGHT-R3B-THS-IMPORT | (night 20260908 R3b construction) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.ths_import
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.table_registry (get_registry, meta_stock_basic 表名真源); zephyr.data.ch_reader (stock_basic 快照只读); zephyr.governance.depgraph_schema (存量活跃链名只读盘点)
# [CONSUMERS] 夜班 SOP industry_chain_data_audit_sop §6 第3轮 R3b(总控执行 plan/ingest)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部写库走 websearch_ingest ingest 唯一通道(禁手写 SQL); 批次=单事务全成全败; ths_export 来源 confidence 固定 0.6; 股权被投关系只落台账禁入 ig_company_edge(SOP §4.10 硬边界); 映射多数票只裁决 SOP §4.7.3 词表内; 拆细 L1(电子/计算机/通信)取 L2 多数票; 3 行业显式判定并登记开放问题; UNMAPPED 不落库; 存量同名链复用不重建
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] THS 文件缺失->抛出; CH 不可达->stock_basic 预查降级 warn(工具侧反查兜底); PG 不可达->ingest 通道侧报错
# [TESTS] 2026-09-08 首跑: plan 90 行业全映射(unmapped=0,judged=3)/批次 173+5215+13976+5201 全部 ingest 落库/幂等复跑零增量
"""ths_import.py — R3b 宽度铺面施工件(SOP §6 第3轮 R3b,夜班指令书第1优先)。

读 docs/_working/同花顺资料/ 下 3 个 GBK 编码 TSV 伪 xlsx:
  个股1 (1).xlsx / 个股1 (2).xlsx(两文件零重叠,合计 5217 只) / 板块行业.xlsx(816 板块,8811xx 行业指数 68 个仅作锚点参考)

产出(全走 websearch_ingest.py ingest 唯一通道,禁手写 SQL):
  1. ths_industry_mapping.yaml — THS 90 二级行业→SOP §4.7.3 申万词表 category 映射
     (成分股"所属同花顺行业"首段多数票;首段∈{电子,计算机,通信}时取第二段多数票
      落细分词表;词表装不下的三个行业按显式判定表裁决并登记 AI 判定理由)
  2. 被投清单留档 — 被投资公司(已上市)只登记台账落盘,
     禁入 ig_company_edge(SOP §4.10 硬边界/开放问题7 股权分域裁定)
  3. 批次 JSON(batches/ths_*.json):
     - 行业锚点链+每链"行业聚合"节点(存量同名链复用不重建,链 category 不动)
     - 全股落位 node_company(source=ths_export,confidence=0.6,预过 stock_basic 反查)
     - 子公司→ig_unlisted_entity 登记(unlisted_entity 通道,幂等)
     - 公司简介→ig_document+ig_chunk(ths_profile,内容层)
  4. 执行摘要落盘 night_audit/ths_import_summary.json

用法:
  python scripts/industry_graph/ths_import.py plan     # 生成映射表+留档+批次 JSON(不写库)
  python scripts/industry_graph/ths_import.py ingest   # 逐批走 ingest 通道写库
  python scripts/industry_graph/ths_import.py all      # plan+ingest
"""
from __future__ import annotations

import json
import re
import sys
import os
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.data.table_registry import get_registry

ROOT = Path(__file__).resolve().parents[2]
THS_DIR = ROOT / "docs" / "_working" / "同花顺资料"
OUT_DIR = ROOT / ".runtime" / "industry_graph" / "night_audit" / "batches"
SUMMARY_PATH = ROOT / ".runtime" / "industry_graph" / "night_audit" / "ths_import_summary.json"
MAPPING_PATH = Path(__file__).resolve().parent / "ths_industry_mapping.yaml"
INVESTED_LEDGER = THS_DIR / f"被投清单登记_ths_import_{date.today().isoformat()}.md"

SOURCE = "ths_export"  # SOP §4.2 v1.4.0 新增来源
TODAY = date.today().isoformat()
SOURCE_DOC = f"同花顺导出|docs/_working/同花顺资料/个股1*.xlsx|{TODAY}"
DOC_SOURCE_DOC = f"同花顺导出|docs/_working/同花顺资料|{TODAY}"

# SOP §4.7.3 category 词表(38+综合)——多数票仅在其中裁决
CATEGORIES = {
    "半导体", "消费电子", "元件", "光学光电子", "计算机设备", "机械设备", "电力设备", "汽车",
    "国防军工", "家用电器", "基础化工", "有色金属", "钢铁", "建筑材料", "石油石化", "煤炭", "医药生物",
    "食品饮料", "纺织服饰", "商贸零售", "社会服务", "美容护理", "轻工制造", "农林牧渔",
    "软件开发", "互联网服务", "通信服务", "通信设备", "游戏", "传媒", "银行", "非银金融",
    "房地产", "建筑装饰", "交通运输", "公用事业", "环保", "综合",
}
# 申万真一级拆细后词表装不下的 THS 行业 → 显式判定(非垃圾桶,理由登记开放问题)
JUDGED = {
    "电子化学品": ("基础化工", "电子化学品本质精细化工材料(湿化学品/光刻胶/特气),SOP词表无此值;旧申万口径归化工,判定登记开放问题待Owner复核"),
    "其他电子": ("消费电子", "THS其他电子为电子杂项,SOP词表无此值;按电子零部件多数属性判消费电子,判定登记开放问题待Owner复核"),
    "IT服务": ("软件开发", "申万计算机-IT服务Ⅱ,SOP词表无IT服务值;金融IT/系统集成主体属软件开发,判定登记开放问题待Owner复核"),
}
# 申万真一级在 SOP 词表中拆成细分类的三个 L1(取第二段多数票落词表)
SPLIT_L1 = {"电子", "计算机", "通信"}

STOCKS_FILES = ["个股1 (1).xlsx", "个股1 (2).xlsx"]
SECTOR_FILE = "板块行业.xlsx"

# ARCH-CH-024: 表名经 TableRegistry 真源派生,禁硬编码
_TBL_STOCK_BASIC = get_registry().table("meta_stock_basic")


def read_tsv(path: Path) -> list[dict]:
    rows: list[dict] = []
    with open(path, encoding="gbk", errors="replace") as f:
        header = [h.strip() for h in f.readline().rstrip("\r\n").split("\t")]
        for ln in f:
            ln = ln.rstrip("\r\n")
            if not ln.strip():
                continue
            parts = ln.split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            rows.append({k: v.strip() for k, v in zip(header, parts)})
    return rows


def load_stocks() -> list[dict]:
    seen: dict[str, dict] = {}
    for fn in STOCKS_FILES:
        for r in read_tsv(THS_DIR / fn):
            code = r.get("代码", "")
            if code and code not in seen:
                seen[code] = r
    return list(seen.values())


def ths_code_to_symbol(code: str) -> str | None:
    m = re.match(r"^(SH|SZ|BJ)(\d{6})$", code)
    if not m:
        return None
    return f"{m.group(2)}.{m.group(1)}"


def bracket_of(row: dict) -> list[str]:
    m = re.match(r"【(.+?)】", row.get("所属同花顺行业", ""))
    return m.group(1).split("-") if m else []


def _l1_votes(rows: list[dict]) -> Counter:
    votes: Counter = Counter()
    for r in rows:
        b = bracket_of(r)
        if b:
            votes[b[0]] += 1
    return votes


def _l2_votes(rows: list[dict], top: str) -> Counter:
    votes: Counter = Counter()
    for r in rows:
        b = bracket_of(r)
        if len(b) > 1 and b[0] == top:
            votes[b[1]] += 1
    return votes


def _resolve_category(rows: list[dict], top: str) -> tuple[str, str, Counter]:
    """拆细 L1(电子/计算机/通信)→L2 多数票→JUDGED 兜底。返回 (category, note, l2votes)。"""
    l2v = _l2_votes(rows, top)
    if not l2v:
        return "UNMAPPED", f"拆细L1 {top} 无第二段", l2v
    l2, _n = l2v.most_common(1)[0]
    if l2 in CATEGORIES:
        return l2, "", l2v
    if l2 in JUDGED:
        return JUDGED[l2][0], JUDGED[l2][1], l2v
    return "UNMAPPED", f"拆细后仍无词表值: {top}-{l2}", l2v


def build_mapping(stocks: list[dict]) -> dict[str, dict]:
    """THS 二级行业(列'所属行业')→SOP 词表 category(多数票+拆细回落+显式判定)。"""
    by_ind: dict[str, list[dict]] = defaultdict(list)
    for r in stocks:
        t = r.get("所属行业", "")
        if t:
            by_ind[t].append(r)
    mapping: dict[str, dict] = {}
    for t, rs in by_ind.items():
        votes = _l1_votes(rs)
        if not votes:
            mapping[t] = {"category": "UNMAPPED", "votes": "0/0", "runner_up": "", "note": "无分类括号"}
            continue
        mapping[t] = _industry_entry(rs, votes)
    return mapping


def _industry_entry(rows: list[dict], votes: Counter) -> dict:
    """单行业条目:L1 多数票在词表→直用;拆细 L1→L2 回落;否则 UNMAPPED。"""
    top, n = votes.most_common(1)[0]
    entry: dict = {
        "votes": f"{n}/{sum(votes.values())}",
        "runner_up": votes.most_common(2)[1][0] if len(votes) > 1 else "",
    }
    if top in CATEGORIES:
        entry["category"] = top
        return entry
    if top in SPLIT_L1:
        return _split_l1_entry(rows, top)
    entry["category"] = "UNMAPPED"
    entry["note"] = f"首段非词表且非拆细L1: {top}"
    return entry


def _split_l1_entry(rows: list[dict], top: str) -> dict:
    """拆细 L1(电子/计算机/通信)→L2 多数票→JUDGED 兜底。"""
    cat, note, l2v = _resolve_category(rows, top)
    entry: dict = {"category": cat}
    if l2v:
        l2, n2 = l2v.most_common(1)[0]
        entry["votes"] = f"{n2}/{sum(l2v.values())}"
        entry["runner_up"] = l2v.most_common(2)[1][0] if len(l2v) > 1 else ""
        if l2 in JUDGED:
            entry["judged"] = JUDGED[l2][1]
    if note:
        entry["note"] = note
    return entry


def write_mapping_yaml(mapping: dict[str, dict]) -> None:
    lines = [
        "# THS 90 二级行业 → SOP §4.7.3 申万词表 category 分层映射表(SOP §6 R3b 操作2)",
        f"# 自动生成 by ths_import.py 多数票规则 at {TODAY}; judged=AI显式判定(开放问题登记); UNMAPPED=不落库",
        "mapping:",
    ]
    for k in sorted(mapping):
        v = mapping[k]
        lines.append(f'  "{k}":')
        lines.append(f'    category: "{v["category"]}"')
        lines.append(f'    votes: "{v["votes"]}"')
        if v.get("runner_up"):
            lines.append(f'    runner_up: "{v["runner_up"]}"')
        if v.get("judged"):
            lines.append(f'    judged: "{v["judged"]}"')
        if v.get("note"):
            lines.append(f'    note: "{v["note"]}"')
    MAPPING_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_invested_ledger(stocks: list[dict]) -> int:
    """被投关系只登记清单落盘留档,禁入 ig_company_edge(SOP §4.10 硬边界)。"""
    lines = [
        "# THS 被投清单登记台账(股权关系分域裁定:SOP §4.10/开放问题7)",
        f"# 生成于 {TODAY} by ths_import.py;只落盘留档供将来股权穿透表消费,禁入 ig_company_edge",
        "",
        "| 股票代码 | 股票名称 | 被投资公司简称(已上市) |",
        "|---|---|---|",
    ]
    n = 0
    for r in sorted(stocks, key=lambda x: x.get("代码", "")):
        inv = r.get("被投资公司简称(已上市)[2025财年 年报]", "")
        if inv and inv != "--":
            lines.append(f"| {r.get('代码','')} | {r.get('名称','')} | {inv} |")
            n += 1
    INVESTED_LEDGER.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return n


def clean_sub_name(s: str) -> str:
    return re.sub(r"\s+", "", s).strip()


def load_stock_basic() -> set[str] | None:
    try:
        from zephyr.data import ch_reader

        tsv = ch_reader.query(f"SELECT symbol_canonical FROM {_TBL_STOCK_BASIC} WHERE valid_to IS NULL")  # noqa: bare-sql  stock_basic 快照统一走 ch_reader TSV 只读通道,全项目唯一采集路径
        return {ln.strip().split("\t")[0] for ln in tsv.strip().splitlines() if ln.strip()}
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] stock_basic 预查降级(将由工具侧反查兜底): {e}")
        return None


def load_active_chain_names() -> set[str]:
    """存量活跃链名(只读,防同名锚点链重建,find-chain 纪律的机械实现)。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM ig_chain WHERE status='active'")  # noqa: bare-sql  只读盘点存量活跃链名,单条快照查询不设集中化文件
        names = {r[0] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return names
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] 存量链名读取降级(全部按新建处理): {e}")
        return set()


def resolve_anchor(ths2: str, active_names: set[str]) -> tuple[str, bool]:
    if f"{ths2}行业" in active_names:
        return f"{ths2}行业", True
    if ths2 in active_names:
        return ths2, True
    return f"{ths2}行业", False


def _anchor_map(mapping: dict[str, dict], active_names: set[str]) -> tuple[dict[str, str], list[str], list[str]]:
    anchors: dict[str, str] = {}
    reused: list[str] = []
    created: list[str] = []
    for ths2 in sorted(mapping):
        if mapping[ths2]["category"] == "UNMAPPED":
            continue
        anchor, is_reuse = resolve_anchor(ths2, active_names)
        anchors[ths2] = anchor
        if is_reuse:
            if anchor not in reused:
                reused.append(anchor)
        else:
            created.append(anchor)
    return anchors, reused, created


def _batch_anchor_chains(mapping: dict[str, dict], anchors: dict[str, str], created: list[str]) -> list[dict]:
    recs: list[dict] = []
    for ths2 in sorted(anchors):
        anchor = anchors[ths2]
        if anchor in created:
            recs.append({
                "type": "chain", "name": anchor, "category": mapping[ths2]["category"],
                "version_year": 2026, "market": "cn", "source": SOURCE, "source_doc": SOURCE_DOC,
            })
        recs.append({
            "type": "node", "chain_name": anchor, "name": "行业聚合", "tier": "中游",
            "market": "cn", "source": SOURCE, "source_doc": SOURCE_DOC,
        })
    return recs


def _batch_placements(stocks: list[dict], anchors: dict[str, str], stock_basic: set[str] | None) -> tuple[list[dict], list[str]]:
    recs: list[dict] = []
    miss: list[str] = []
    for r in stocks:
        ths2 = r.get("所属行业", "")
        sym = ths_code_to_symbol(r.get("代码", ""))
        if not sym or ths2 not in anchors:
            miss.append(f"{r.get('代码','')}({ths2})")
            continue
        if stock_basic is not None and sym not in stock_basic:
            miss.append(f"{sym}(非在市)")
            continue
        recs.append({
            "type": "node_company", "chain_name": anchors[ths2], "node_name": "行业聚合",
            "symbol": sym, "role": "参与", "confidence": 0.6,
            "evidence_text": "THS申万分类:" + "-".join(bracket_of(r)),
            "market": "cn", "source": SOURCE, "source_doc": SOURCE_DOC,
        })
    return recs, miss


def _batch_unlisted(stocks: list[dict]) -> list[dict]:
    recs: list[dict] = []
    seen: set[str] = set()
    for r in stocks:
        for raw in re.findall(r"【([^【】]+)】", r.get("子公司", "")):
            name = clean_sub_name(raw)
            if not name or name in seen:
                continue
            seen.add(name)
            recs.append({
                "type": "unlisted_entity", "name": name, "country": "CN",
                "status": "unlisted", "source": SOURCE, "source_doc": SOURCE_DOC,
            })
    return recs


def _batch_chunks(stocks: list[dict]) -> list[dict]:
    recs: list[dict] = []
    doc_id = f"DOC-ths-stock-profiles-{TODAY.replace('-', '')}"
    recs.append({
        "type": "document", "doc_id": doc_id,
        "relative_path": "docs/_working/同花顺资料/个股1(1+2)_公司简介.tsv",
        "bundle": "同花顺资料", "file_name": "个股1(1+2)_公司简介.tsv", "ext": ".tsv",
        "size_bytes": sum(len(r.get("公司简介", "")) for r in stocks),
        "doc_type": "ths_profile", "title": f"同花顺个股公司简介汇总({TODAY})",
        "year": 2026, "market": "cn", "source": SOURCE, "source_doc": DOC_SOURCE_DOC,
    })
    for r in stocks:
        prof = r.get("公司简介", "").strip()
        code, name = r.get("代码", ""), r.get("名称", "")
        if len(prof) <= 40 or not code:
            continue
        sym = ths_code_to_symbol(code) or code
        recs.append({
            "type": "chunk", "chunk_id": f"CK-ths-{code}", "doc_id": doc_id,
            "title": f"{sym} {name} 公司简介", "doc_type": "ths_profile", "year": 2026,
            "chunk_text": prof, "source": SOURCE, "source_doc": DOC_SOURCE_DOC,
        })
    return recs


def _write_batch(name: str, records: list[dict]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / name
    p.write_text(json.dumps({"batch_id": name.replace(".json", ""), "round": 3, "records": records}, ensure_ascii=False), encoding="utf-8")
    return p


def build_batches(stocks, mapping, sector_rows, active_names, stock_basic):
    anchors, reused, created = _anchor_map(mapping, active_names)
    paths = [
        _write_batch("ths_l1_industry_chains.json", _batch_anchor_chains(mapping, anchors, created)),
        _write_batch("ths_l2_stock_placements.json", _batch_placements(stocks, anchors, stock_basic)[0]),
        _write_batch("ths_l3_unlisted_entities.json", _batch_unlisted(stocks)),
        _write_batch("ths_l4_profile_chunks.json", _batch_chunks(stocks)),
    ]
    _placements_count = len(json.loads(paths[1].read_text(encoding="utf-8"))["records"])
    stats = {
        "reused_chains": reused, "created_chains": created, "anchors": anchors,
        "placements": _placements_count,
        "symbol_miss": _batch_placements(stocks, anchors, stock_basic)[1],
        "sector_industry_index_8811xx": [
            {"code": r.get("代码", ""), "name": r.get("名称", "")}
            for r in sector_rows if r.get("代码", "").startswith("8811")
        ],
    }
    return paths, stats


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    stocks = load_stocks()
    sector_rows = read_tsv(THS_DIR / SECTOR_FILE)
    mapping = build_mapping(stocks)
    unmapped = {k: v for k, v in mapping.items() if v["category"] == "UNMAPPED"}
    judged = {k: v for k, v in mapping.items() if v.get("judged")}
    invested_n = write_invested_ledger(stocks)
    print(json.dumps({
        "stocks": len(stocks), "ths_industries": len(mapping),
        "unmapped": unmapped, "judged": judged,
        "invested_ledger_rows": invested_n, "sector_rows": len(sector_rows),
    }, ensure_ascii=False))
    if cmd in ("plan", "all"):
        write_mapping_yaml(mapping)
        active_names = load_active_chain_names()
        stock_basic = load_stock_basic()
        batches, stats = build_batches(stocks, mapping, sector_rows, active_names, stock_basic)
        for b in batches:
            n = len(json.loads(b.read_text(encoding="utf-8"))["records"])
            print(f"BATCH {b.name} records={n}")
        print(json.dumps({
            "reused_chains": len(stats["reused_chains"]),
            "created_chains": len(stats["created_chains"]),
            "placements": stats["placements"],
            "symbol_miss_count": len(stats["symbol_miss"]),
            "symbol_miss_sample": stats["symbol_miss"][:10],
            "sector_8811xx": len(stats["sector_industry_index_8811xx"]),
        }, ensure_ascii=False))
        SUMMARY_PATH.write_text(json.dumps({
            "date": TODAY, "stocks": len(stocks), "ths_industries": len(mapping),
            "mapping": mapping, **stats,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    if cmd in ("ingest", "all"):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import websearch_ingest as wi

        order = ["ths_l1_industry_chains.json", "ths_l2_stock_placements.json",
                 "ths_l3_unlisted_entities.json", "ths_l4_profile_chunks.json"]
        rc = 0
        for name in order:
            b = OUT_DIR / name
            if not b.is_file():
                continue
            print(f"INGEST {name} ...")
            rc = wi.cmd_ingest(str(b))
            print(f"  exit={rc}")
            if rc != 0:
                break
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
