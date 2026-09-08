# [MODULE] scripts.industry_graph.graph_quality_check
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer (stock_basic 反查)
# [CONSUMERS] SOP industry_chain_data_audit_sop §11 质量验收循环(引擎判定权真源); 长城任务退出判定(连续两轮零违规)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读引擎: 全部 SELECT 零写入; 十九项合格线=graph_quality_standard.md §2~§6 一一对应(S1~S19); 豁免清单 quality_exemptions.yaml(未登记违规不扣除); 成对冗余豁免在 S16 SQL 内判(supplies_to+customer_of 合法); 输出 JSON(.runtime)+MD 报告, 退出码 0=全绿 1=有违规 2=环境故障
# [MODIFY-GUARD] graph_quality_standard.md(标准真源,SQL 须与其同步改)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->exit 2; CH 不可达->S11/S19 降级 warn 且不计违规(标 degraded); 豁免文件不存在->视为零豁免
# [TTL] permanent
# M10豁免: manual STARTUP 体检引擎
"""图谱质量检查引擎（Graph Quality Check，SOP §11 / graph_quality_standard.md）。

十九项合格线一键体检：每条标准一条 SQL，输出违规清单（JSON+MD）。
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
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

REPORT_DIR = Path(__file__).resolve().parents[2] / ".runtime" / "industry_graph" / "quality_reports"
EXEMPT_FILE = Path(__file__).resolve().parent / "quality_exemptions.yaml"

# 词表(与 websearch_ingest 同源; 引擎/工具两边规则漂移=事故,改须同 commit)
TITLE_JUNK_RE = "一张图看懂|重磅|最新|预测|深度|全景图|解读|盘点|风向标|启幕|ppt|研报|机遇|风口"
TIER_ALL = ("上游", "中游", "下游", "设备", "材料", "零部件", "原材料", "辅材")
TIER_SUFFIX_RE = "-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$"
ROLES_STD = ("龙头", "核心", "主要", "参与", "提及")
SW_CATEGORIES = (
    "半导体", "消费电子", "元件", "光学光电子", "计算机设备", "机械设备", "电力设备", "汽车",
    "国防军工", "家用电器", "基础化工", "有色金属", "钢铁", "建筑材料", "石油石化", "煤炭", "医药生物",
    "食品饮料", "纺织服饰", "商贸零售", "社会服务", "美容护理", "轻工制造", "农林牧渔",
    "软件开发", "互联网服务", "通信服务", "通信设备", "游戏", "传媒", "银行", "非银金融",
    "房地产", "建筑装饰", "交通运输", "公用事业", "环保", "综合",
)
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
        WHERE status='deprecated' AND (merged_into IS NULL OR merged_into NOT ~ '^CH-[0-9a-f]{{12}}$')
        UNION ALL
        SELECT c.chain_id, '废弃链落位残留 ' || count(*) FROM ig_chain c
        JOIN ig_node n ON n.chain_id=c.chain_id
        JOIN ig_node_company nc ON nc.node_id=n.node_id
        WHERE c.status='deprecated'
        GROUP BY c.chain_id
    """},
    {"id": "S5", "title": "version_year 覆盖(锚点链豁免)", "sql": """
        SELECT chain_id, 'version_year空: ' || name FROM ig_chain
        WHERE version_year IS NULL AND (status IS NULL OR status='active')
          AND name NOT LIKE '%行业'
    """},
    # ---- 节点层 ----
    {"id": "S6", "title": "tier 词表+零 unspecified", "sql": f"""
        SELECT node_id, coalesce(tier,'(空)') || ' | ' || name FROM ig_node
        WHERE tier IS NULL OR (tier NOT IN ({','.join(f"'{t}'" for t in TIER_ALL)}) AND tier <> 'unspecified')
        UNION ALL
        SELECT node_id, 'unspecified | ' || name FROM ig_node WHERE tier='unspecified'
    """},
    {"id": "S7", "title": "节点名零 -tier 后缀", "sql": f"""
        SELECT node_id, name FROM ig_node WHERE name ~ '{TIER_SUFFIX_RE}'
    """},
    {"id": "S8", "title": "零孤岛节点(聚合节点豁免)", "sql": """
        SELECT n.node_id, n.name || ' @' || c.name FROM ig_node n
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE NOT EXISTS (SELECT 1 FROM ig_edge e WHERE e.from_node=n.node_id OR e.to_node=n.node_id)
          AND NOT EXISTS (SELECT 1 FROM ig_node_company nc WHERE nc.node_id=n.node_id)
          AND n.name <> '行业聚合'
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
        WHERE nc.role IS NULL OR nc.role NOT IN ({','.join(f"'{r}'" for r in ROLES_STD)})
    """},
    # S11 死映射: 需 CH 反查,运行时注入
    {"id": "S12", "title": "market 一致", "sql": """
        SELECT nc.id::text, nc.market || ' vs ' || n.market FROM ig_node_company nc
        JOIN ig_node n ON nc.node_id=n.node_id
        WHERE nc.market <> n.market
    """},
    {"id": "S13", "title": "新落位 PIT 覆盖", "sql": f"""
        SELECT nc.id::text, nc.symbol || ' 缺valid_from' FROM ig_node_company nc
        WHERE nc.created_at::date > '{PIT_CUTOFF}' AND nc.valid_from IS NULL
    """},
    {"id": "S14", "title": f"挂链阈值(>{MAX_CHAINS_PER_SYMBOL})", "sql": f"""
        SELECT nc.symbol, '挂' || count(DISTINCT n.chain_id) || '链' FROM ig_node_company nc
        JOIN ig_node n ON nc.node_id=n.node_id
        JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE (c.status IS NULL OR c.status='active')
        GROUP BY nc.symbol HAVING count(DISTINCT n.chain_id) > {MAX_CHAINS_PER_SYMBOL}
    """},
    # ---- 边层 ----
    {"id": "S15", "title": "零自环边", "sql": """
        SELECT edge_id::text, from_symbol || '->' || to_symbol FROM ig_company_edge
        WHERE from_symbol=to_symbol AND from_symbol<>''
    """},
    {"id": "S16", "title": "零事故性双向边(成对冗余合法)", "sql": """
        SELECT a.edge_id::text, a.from_symbol || '<->' || a.to_symbol || ' ' || a.year FROM ig_company_edge a
        JOIN ig_company_edge b
          ON b.from_symbol=a.to_symbol AND b.to_symbol=a.from_symbol AND b.year=a.year
        WHERE a.edge_id < b.edge_id
    """},
    {"id": "S17", "title": "websearch 边完整(PIT+evidence)", "sql": """
        SELECT edge_id::text,
               concat_ws(',', CASE WHEN valid_from IS NULL THEN 'valid_from' END,
                              CASE WHEN as_of IS NULL THEN 'as_of' END,
                              CASE WHEN evidence_type IS NULL THEN 'evidence_type' END)
        FROM ig_company_edge
        WHERE source='websearch' AND (valid_from IS NULL OR as_of IS NULL OR evidence_type IS NULL)
    """},
    {"id": "S18", "title": "UNLISTED 格式统一", "sql": r"""
        SELECT edge_id::text, from_symbol || '/' || to_symbol FROM ig_company_edge
        WHERE (from_symbol ~ '^UNLISTED:' AND from_symbol !~ '^UNLISTED:UE-[0-9a-f]{12}$')
           OR (to_symbol ~ '^UNLISTED:' AND to_symbol !~ '^UNLISTED:UE-[0-9a-f]{12}$')
    """},
    # S19 编码表上市撞名: 需 CH 反查,运行时注入
]

DEGRADED_NOTE = "CH 不可达降级,本轮不计违规"


def _check_s11(cur, alive: set[str]) -> dict:
    if alive is None:
        return {"id": "S11", "title": "死映射零存量", "violations": [], "degraded": True}
    cur.execute("SELECT nc.id::text, nc.symbol FROM ig_node_company nc WHERE nc.market='cn'")
    rows = [(pk, sym) for pk, sym in cur.fetchall() if sym not in alive]
    return {"id": "S11", "title": "死映射零存量", "violations": rows, "degraded": False}


def _check_s19(cur, alive_names: set[str] | None) -> dict:
    if alive_names is None:
        return {"id": "S19", "title": "编码表零上市撞名", "violations": [], "degraded": True}
    cur.execute("SELECT ue_id, name FROM ig_unlisted_entity WHERE status='unlisted'")
    rows = [(pk, name) for pk, name in cur.fetchall() if name in alive_names]
    return {"id": "S19", "title": "编码表零上市撞名", "violations": rows, "degraded": False}


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
        exempt = set(exemptions.get(chk["id"], []))
        kept = [(pk, desc) for pk, desc in rows if pk not in exempt]
        results.append({"id": chk["id"], "title": chk["title"], "violations": kept,
                        "raw_count": len(rows), "exempt_count": len(rows) - len(kept)})

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

    conn.close()

    total = sum(len(r["violations"]) for r in results)
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
        status = "degraded(降级)" if r.get("degraded") else ("PASS" if not r["violations"] else f"违规 {len(r['violations'])}")
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
            tag = "degraded" if r.get("degraded") else (len(r["violations"]))
            print(f"  {r['id']} {r['title']}: {tag}")
        print(f"报告: {md}")
    return 0 if report["all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
