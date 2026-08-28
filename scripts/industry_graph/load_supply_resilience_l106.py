# [MODULE] scripts.industry_graph.load_supply_resilience_l106
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.industry_graph.apply_industry_graph_ddl
# [CONSUMERS] 风控引擎; 选股因子
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重跑(ON CONFLICT); 只取'原始数据'sheet(插值/回归填补为人造数据不入库)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源文件不存在->退出码2
# [TTL] permanent
"""导入 L106 包：上市公司供应链韧性替代指标（2000-2025）→ ig_company_metric。

metric='supply_chain_resilience', value=供应链韧性, value_aux=供应链韧性_缩尾。
仅用"原始数据"sheet（库存周转率真实计算值），线性插值/回归填补为人造数据不入库。

用法::

    python scripts/industry_graph/load_supply_resilience_l106.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SOURCE_FILE = (
    r"E:\数据下载\供应链数据\L106-上市公司供应链韧性替代指标（2000-2025年）"
    r"\供应链韧性替代指标（2000-2025年）.xlsx"
)
SOURCE_TAG = "L106_resilience"


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


def main() -> int:
    if not os.path.isfile(SOURCE_FILE):
        print(f"[ERROR] 源文件不存在: {SOURCE_FILE}")
        return 2

    df = pd.read_excel(SOURCE_FILE, sheet_name="原始数据")
    val_col = next((c for c in df.columns if str(c).strip() == "供应链韧性"), None)
    aux_col = next((c for c in df.columns if "缩尾" in str(c)), None)
    if val_col is None:
        print(f"[ERROR] 未找到'供应链韧性'列，实际列: {list(df.columns)}")
        return 2

    rows = []
    for r in df.itertuples(index=False):
        sym = to_symbol(r[1])  # 股票代码
        try:
            year = int(r[0])
        except (TypeError, ValueError):
            continue
        v = r[df.columns.get_loc(val_col)]
        a = r[df.columns.get_loc(aux_col)] if aux_col else None
        if not sym or pd.isna(v):
            continue
        rows.append((sym, year, "supply_chain_resilience", float(v),
                     float(a) if a is not None and pd.notna(a) else None, SOURCE_TAG))

    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    try:
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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*), count(DISTINCT symbol), min(year), max(year) "
                "FROM ig_company_metric WHERE source=%s",
                (SOURCE_TAG,),
            )
            total, n_sym, y_min, y_max = cur.fetchone()
    finally:
        conn.close()
    print(f"[STAT] {SOURCE_TAG}: 指标={total}, 公司={n_sym}, 年份 {y_min}-{y_max}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
