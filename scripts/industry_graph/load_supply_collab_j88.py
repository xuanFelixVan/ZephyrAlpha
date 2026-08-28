# [MODULE] scripts.industry_graph.load_supply_collab_j88
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.industry_graph.apply_industry_graph_ddl
# [CONSUMERS] 供应链传导因子; 图谱可视化
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重跑(ON CONFLICT); 只用重构后tidy版(宽表原始版不入); weight=联合专利合作次数
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源文件不存在->退出码2
# [TTL] permanent
"""导入 J88 包：上下游供应链协同创新数据（2013-2024）→ ig_company_edge。

- 重构后的供应商数据：from=供应商 → to=中游公司，weight=合作次数
- 重构后的客户数据：  from=中游公司 → to=客户，  weight=合作次数
source='J88_collab_patent', weight_type='collab_count'（第三证据源，创新维度）。

用法::

    python scripts/industry_graph/load_supply_collab_j88.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

PKG_DIR = r"E:\数据下载\供应链数据\J88-上市公司-上下游供应链协同创新数据（2013-2024年）"
SUPPLIER_FILE = os.path.join(PKG_DIR, "重构后的供应商数据.xlsx")
CUSTOMER_FILE = os.path.join(PKG_DIR, "重构后的客户数据.xlsx")
SOURCE_TAG = "J88_collab_patent"


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


def parse(file: str, direction: str) -> list[tuple]:
    """direction='supplier': from=列0(供应商) to=列4(中游); 'customer': from=列4(中游) to=列0(客户)"""
    df = pd.read_excel(file)
    rows = []
    for r in df.itertuples(index=False):
        # 位置: 0=名称 1=代码 2=年份 3=合作次数 4=中游代码 5=中游名称
        a_sym, a_name = to_symbol(r[1]), (str(r[0]).strip() if pd.notna(r[0]) else None)
        b_sym, b_name = to_symbol(r[4]), (str(r[5]).strip() if pd.notna(r[5]) else None)
        try:
            year = int(r[2])
            cnt = float(r[3]) if pd.notna(r[3]) else None
        except (TypeError, ValueError):
            continue
        if direction == "supplier":
            frm, to, f_name, t_name = a_sym, b_sym, a_name, b_name
        else:
            frm, to, f_name, t_name = b_sym, a_sym, b_name, a_name
        if not frm or not to or frm == to:
            continue
        rows.append((frm, to, year, cnt, "collab_count", SOURCE_TAG, f_name, t_name))
    return rows


def main() -> int:
    for f in (SUPPLIER_FILE, CUSTOMER_FILE):
        if not os.path.isfile(f):
            print(f"[ERROR] 源文件不存在: {f}")
            return 2

    rows = parse(SUPPLIER_FILE, "supplier") + parse(CUSTOMER_FILE, "customer")
    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO ig_company_edge
                    (from_symbol, to_symbol, year, weight, weight_type, source, from_name, to_name)
                VALUES %s
                ON CONFLICT (from_symbol, to_symbol, year, source) DO UPDATE SET
                    weight = EXCLUDED.weight
                """,
                rows,
                page_size=2000,
            )
        conn.commit()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*), count(DISTINCT from_symbol), count(DISTINCT to_symbol) "
                "FROM ig_company_edge WHERE source=%s",
                (SOURCE_TAG,),
            )
            total, n_from, n_to = cur.fetchone()
    finally:
        conn.close()
    print(f"[STAT] {SOURCE_TAG}: 边={total}, 上游公司={n_from}, 下游公司={n_to}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
