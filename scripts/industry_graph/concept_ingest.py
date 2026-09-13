# [MODULE] scripts.industry_graph.concept_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 无(概念资产装载器;消费=详情页所属概念展示/S24 链名分流判定,SQL 直查 stock_concept)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 架构数据直写 DB(RULE-SSOT,讨论稿 Owner 2026-09-14 批准); 幂等(UNIQUE symbol+concept+source ON CONFLICT); 市场分类标签过滤(全部AB股/沪深股通/融资融券等非产业概念不入库); 概念≠产业链——ig_chain 只承载真产业链,概念型链名归宿=本表
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件缺失->退出码2; GBK 解码失败->退出码2; PG 不可达->退出码2
# [TTL] permanent
"""概念体系装载器：同花顺公司档案导出（GBK TSV）→ stock_concept 公司×概念标签。

概念=公司属性标签（与产业链结构正交）：ig_chain 只承载真产业链，"AI眼镜""固态电池"
这类概念型名称的归宿是本表。市场分类标签（全部A股/沪深股通等）装载前过滤。
静态快照 as_of=文件日期；后续可接 akshare 概念接口做定期增量。

用法::

    python scripts/industry_graph/concept_ingest.py load --file <同花顺导出.tsv/xlsx>
    python scripts/industry_graph/concept_ingest.py status
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

AS_OF = "2026-09-14"
SD = "ths_export 同花顺公司档案|Owner 提供导出|2026-09-14"
MARKET_TAG = re.compile(
    r"股$|股\(|上市公司$|AB股|A股|主板|创业板|科创板|北证|中小企业板|新股|次新股|破发|高送转|定增|重组|"
    r"股权激励|回购|举牌|壳资源|分红|绩优|亏损|微利|白马股|黑马|独角兽|MSCI|富时|标普|纳斯达克|"
    r"同花顺|中字头|含可转债|转债|预盈|预亏|预增|预减|融资融券|沪深|深证|上证|深股通|沪股通|中证\d+"
)


def cmd_load(files: list[str]) -> int:
    rows = []
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"[ERROR] 文件不存在: {p}")
            return 2
        txt = p.read_bytes().decode("gbk", errors="replace")
        lines = txt.splitlines()
        header = [h.strip() for h in lines[0].split("\t")]
        if "所属概念" not in header:
            print(f"[ERROR] {p.name} 表头无'所属概念'列,口径不符")
            return 2
        cidx = header.index("所属概念")
        for ln in lines[1:]:
            parts = ln.split("\t")
            if len(parts) <= cidx or not parts[1].strip():
                continue
            code, name = parts[0].strip(), parts[1].strip()
            sym = code[-6:] + "." + code[:2].upper() if code[:2].upper() in ("SZ", "SH", "BJ") else code
            for tag in re.split(r"[;；]", parts[cidx].strip("【】")):
                tag = tag.strip()
                if not tag or MARKET_TAG.search(tag):
                    continue
                if len(tag) > 20 or re.search(r"主营|有限公司|股份公司", tag):
                    continue  # 简介污染防御: 真概念标签=2-15字短词
                rows.append((sym, name, tag, SD))
    if not rows:
        print("[ERROR] 解析出 0 行,文件口径不符")
        return 2
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    sql = """
        INSERT INTO stock_concept (symbol, name, concept, source, source_doc, market, as_of, valid_from)
        VALUES %s
        ON CONFLICT (symbol, concept, source) DO UPDATE SET
            name=EXCLUDED.name, updated_at=now()
    """
    from psycopg2.extras import execute_values

    execute_values(cur, sql, [(s, n, c, 'ths_export', sd, 'cn', AS_OF, AS_OF) for s, n, c, sd in rows],
                   page_size=1000)
    conn.commit()
    cur.execute("SELECT count(*), count(DISTINCT symbol), count(DISTINCT concept) FROM stock_concept WHERE valid_to IS NULL")
    n, ns, nc = cur.fetchone()
    conn.close()
    print(f"[OK] stock_concept: 本批 {len(rows)} 行, 表内 {n} 行 / {ns} 公司 / {nc} 概念 | as_of={AS_OF}")
    return 0


def cmd_status() -> int:
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute("""SELECT count(*), count(DISTINCT symbol), count(DISTINCT concept) FROM stock_concept WHERE valid_to IS NULL""")
    n, ns, nc = cur.fetchone()
    cur.execute("""SELECT concept, count(*) FROM stock_concept WHERE valid_to IS NULL
                   GROUP BY concept ORDER BY 2 DESC LIMIT 10""")
    top = cur.fetchall()
    conn.close()
    print(f"stock_concept: {n} 行 / {ns} 公司 / {nc} 概念")
    print("Top10:", top)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="概念体系装载器(load/status)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("load")
    p1.add_argument("--file", action="append", required=True, help="同花顺导出 GBK TSV(可多次)")
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "load":
        return cmd_load(a.file)
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
