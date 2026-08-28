# [MODULE] scripts.industry_graph.calc_customer_concentration
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 风控引擎; 选股因子; 大客户依赖预警
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重算(ON CONFLICT UPDATE); 只统计 weight 非空的 483 边; HHI 口径为占比百分数平方和
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无边数据->退出码2
# [TTL] permanent
"""T4：客户集中度因子计算（483 前五大客户边 → ig_company_metric）。

衍生指标（公司-年度）：
  customer_hhi        前五大客户占比的赫芬达尔指数 sum(占比^2)，越高越集中
  customer_top1_ratio 第一大客户占比（>30% 即大客户依赖预警线，如歌尔→苹果）
  customer_top5_ratio 前五大客户合计占比

用法::

    python scripts/industry_graph/calc_customer_concentration.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from psycopg2.extras import execute_values

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SOURCE_TAG = "483_derived"


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT from_symbol, year,
                   sum(weight * weight) AS hhi,
                   max(weight)          AS top1,
                   sum(weight)          AS top5
            FROM ig_company_edge
            WHERE source = '483_top5_customer' AND weight IS NOT NULL
            GROUP BY 1, 2
            """
        )
        agg = cur.fetchall()
    if not agg:
        print("[ERROR] 无 483 边数据")
        return 2

    rows = []
    for sym, year, hhi, top1, top5 in agg:
        rows.append((sym, year, "customer_hhi", float(hhi), None, SOURCE_TAG))
        rows.append((sym, year, "customer_top1_ratio", float(top1), None, SOURCE_TAG))
        rows.append((sym, year, "customer_top5_ratio", float(top5), None, SOURCE_TAG))

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ig_company_metric (symbol, year, metric, value, value_aux, source)
            VALUES %s
            ON CONFLICT (symbol, year, metric, source) DO UPDATE SET value = EXCLUDED.value
            """,
            rows,
            page_size=2000,
        )
        cur.execute(
            "SELECT metric, count(*) FROM ig_company_metric WHERE source=%s GROUP BY 1",
            (SOURCE_TAG,),
        )
        stats = dict(cur.fetchall())
        # 大客户依赖预警样例：最新年份 top1>30% 的公司数
        cur.execute(
            """
            SELECT count(*) FROM ig_company_metric
            WHERE source=%s AND metric='customer_top1_ratio' AND value > 30
              AND year = (SELECT max(year) FROM ig_company_metric
                          WHERE source=%s AND metric='customer_top1_ratio')
            """,
            (SOURCE_TAG, SOURCE_TAG),
        )
        risky = cur.fetchone()[0]
    conn.commit()
    conn.close()
    print(f"[T4] 完成: {stats}; 最新年 top1>30% 依赖型公司 {risky} 家")
    return 0


if __name__ == "__main__":
    sys.exit(main())
