# [MODULE] scripts.industry_graph.load_supply_match_list
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.industry_graph.apply_industry_graph_ddl
# [CONSUMERS] 供应链传导因子; 图谱可视化
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重跑(ON CONFLICT DO NOTHING); 符号规范 6位+.SH/.SZ/.BJ; 跳过字段说明行
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源文件不存在->退出码2; 单行解析失败->跳过并计数
# [TTL] permanent
"""导入《供应链上下游匹配名单 2012-2023》到 ig_company_edge。

数据源：上市公司企业供应链上下游匹配名单2012-2023年/最终结果-供应链上下游匹配名单.xlsx
边语义：from_symbol=上游（供应商）→ to_symbol=下游（客户），按 year 记录。
source='match_list_2012_2023'（证据源 1，与后续 483/J88 交叉验证）。

用法::

    python scripts/industry_graph/load_supply_match_list.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SOURCE_FILE = (
    r"E:\数据下载\供应链数据\上市公司企业供应链上下游匹配名单2012-2023年"
    r"\最终结果-供应链上下游匹配名单.xlsx"
)
SOURCE_TAG = "match_list_2012_2023"


def to_symbol(stkcd) -> str | None:
    """股票代码数字 → 项目符号规范（6 位 + 交易所后缀）。"""
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


def main() -> int:
    if not os.path.isfile(SOURCE_FILE):
        print(f"[ERROR] 源文件不存在: {SOURCE_FILE}")
        return 2

    df = pd.read_excel(SOURCE_FILE)
    rows, skipped = [], 0
    for r in df.itertuples(index=False):
        try:
            year = int(r.year)
        except (TypeError, ValueError):
            skipped += 1  # 字段说明行（year='年份'）等
            continue
        # 中文列名在 itertuples 下不稳定，用位置索引：0=上游代码 2=下游代码 4=年份
        frm = to_symbol(r[0])
        to = to_symbol(r[2])
        if not frm or not to or frm == to:
            skipped += 1
            continue
        rows.append((frm, to, year, SOURCE_TAG))

    print(f"[LOAD] 解析 {len(df)} 行 → 有效边 {len(rows)} 条，跳过 {skipped} 行")

    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO ig_company_edge (from_symbol, to_symbol, year, source)
                VALUES %s
                ON CONFLICT (from_symbol, to_symbol, year, source) DO NOTHING
                """,
                rows,
                page_size=1000,
            )
        conn.commit()
        # 注：execute_values 的 rowcount 仅反映最后一批，插入量以库内总数为准
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(*), count(DISTINCT from_symbol), count(DISTINCT to_symbol),
                       min(year), max(year)
                FROM ig_company_edge WHERE source = %s
                """,
                (SOURCE_TAG,),
            )
            total, n_from, n_to, y_min, y_max = cur.fetchone()
    finally:
        conn.close()

    print(f"[STAT] source={SOURCE_TAG}: 边={total}, 上游公司={n_from}, 下游公司={n_to}, 年份 {y_min}-{y_max}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
