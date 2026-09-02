# [MODULE] scripts.industry_graph.load_supply_top5_483
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.industry_graph.apply_industry_graph_ddl
# [CONSUMERS] 供应链传导因子; 图谱可视化
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重跑(ON CONFLICT); 只取年报(12-31)+前五大(排名<=5)剔除合计行; to_symbol='' 表非上市客户(名称在 to_name)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源文件不存在->退出码2
# [TTL] permanent
"""导入 483 包：前五大客户销售表 → ig_company_edge；客户稳定性 → ig_company_metric。

- 边：from_symbol=披露公司(供应商) → to=客户(上市则取代码，否则 ''+to_name)，
  weight=客户销售额占比(%), amount=客户销售额, rank=排名, source='483_top5_customer'
- 指标：metric='customer_stability', value=Stability, value_aux=Dummy, source='483_stability'

用法::

    python scripts/industry_graph/load_supply_top5_483.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

PKG_DIR = r"E:\数据下载\供应链数据\483供应链客户稳定性"
EDGE_FILE = os.path.join(PKG_DIR, "前五大客户销售信息表.xlsx")
METRIC_FILE = os.path.join(PKG_DIR, "计算结果.xlsx")
EDGE_SOURCE = "483_top5_customer"
METRIC_SOURCE = "483_stability"


def to_symbol(stkcd) -> str | None:
    try:
        code = str(int(float(stkcd))).zfill(6)
    except (TypeError, ValueError):
        return None
    if code.startswith("6"):
        return code + ".SH"
    if code.startswith(("0", "3")):
        return code + ".SZ"
    if code.startswith(("4", "8")):
        return code + ".BJ"
    return None


def load_edges(conn) -> None:
    df = pd.read_excel(EDGE_FILE)
    # 键内去重：同一 (公司,客户,年份) 可能同时披露合并报表/母公司报表两行，
    # 优先报表类型=1（合并），其次排名靠前者；否则 ON CONFLICT 同批重复会报错
    best: dict[tuple, tuple] = {}
    for r in df.itertuples(index=False):
        # 位置: 0股票代码 1统计截止日期 2报表类型 3排名 5客户名称 6是否上市 7公司股票代码
        #       9关联上市公司股票代码 10客户销售额 11客户销售额占比
        try:
            frm = to_symbol(r[0])
            rank = int(r[3])
            name = str(r[5]).strip() if pd.notna(r[5]) else ""
            dt = pd.Timestamp(r[1])
            rpt = int(r[2])
        except (TypeError, ValueError):
            continue
        if not frm or not name or name == "合计" or rank > 5:
            continue
        if not (dt.month == 12 and dt.day == 31):  # 只取年报截面
            continue
        to = None
        if str(r[6]).strip().upper() == "Y" and pd.notna(r[7]):
            to = to_symbol(r[7])
        if to is None and pd.notna(r[9]):
            to = to_symbol(r[9])  # 客户非上市但其关联方为上市公司
        to_name = "" if to else name
        weight = float(r[11]) if pd.notna(r[11]) else None
        amount = float(r[10]) if pd.notna(r[10]) else None
        row = (frm, to or "", dt.year, weight, "sales_pct", EDGE_SOURCE, None, to_name or None, amount, rank)
        key = (frm, to or "", dt.year)
        score = (1 if rpt == 1 else 0, -rank)  # 合并报表优先，其次排名靠前
        if key not in best or score > best[key][0]:
            best[key] = (score, row)
    rows = [v[1] for v in best.values()]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ig_company_edge
                (from_symbol, to_symbol, year, weight, weight_type, source,
                 from_name, to_name, amount, rank)
            VALUES %s
            ON CONFLICT (from_symbol, to_symbol, year, source) DO UPDATE SET
                weight = EXCLUDED.weight, amount = EXCLUDED.amount, rank = EXCLUDED.rank
            """,
            rows,
            page_size=2000,
        )
    conn.commit()
    print(f"[483-EDGE] 有效边 {len(rows)} 条（已 upsert）")


def load_metric(conn) -> None:
    df = pd.read_excel(METRIC_FILE)
    rows = []
    for r in df.itertuples(index=False):
        # 位置: 2=stkcd 3=year 7=Dummy 8=Stability
        sym = to_symbol(r[2])
        try:
            year = int(r[3])
        except (TypeError, ValueError):
            continue
        if not sym or pd.isna(r[8]):
            continue
        rows.append(
            (sym, year, "customer_stability", float(r[8]), float(r[7]) if pd.notna(r[7]) else None, METRIC_SOURCE)
        )

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ig_company_metric (symbol, year, metric, value, value_aux, source)
            VALUES %s
            ON CONFLICT (symbol, year, metric, source) DO UPDATE SET
                value = EXCLUDED.value, value_aux = EXCLUDED.value_aux
            """,
            rows,
            page_size=2000,
        )
    conn.commit()
    print(f"[483-METRIC] customer_stability {len(rows)} 条（已 upsert）")


def main() -> int:
    for f in (EDGE_FILE, METRIC_FILE):
        if not os.path.isfile(f):
            print(f"[ERROR] 源文件不存在: {f}")
            return 2
    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    try:
        load_edges(conn)
        load_metric(conn)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*), count(*) FILTER (WHERE to_symbol <> '') FROM ig_company_edge WHERE source=%s",
                (EDGE_SOURCE,),
            )
            total, listed = cur.fetchone()
    finally:
        conn.close()
    print(f"[STAT] {EDGE_SOURCE}: 边={total}, 其中对手方为上市公司={listed}, 非上市={total - listed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
