# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] scripts.ch.apply_fundamental_tables_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_reader
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: income_statement DDL 真源为 schemas/categories/fundamental_income_statement.py; balance_sheet 真源为 fundamental_balance_sheet.py; cashflow_statement 真源为 fundamental_cashflow_statement.py; apply() 通过 ch_writer.query 执行 DDL; verify() 通过 ch_reader.query 读取 system.tables/system.columns 验证引擎+Decimal 精度(audit 1.2)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->打印错误+退出码2; 引擎/精度不匹配->列出差异+退出码1; 全部匹配->退出码0
# [TESTS] scripts/ch/apply_fundamental_tables_ddl.py --verify (smoke test: 引擎+Decimal精度)
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: 部署脚本与 schema 文件 DDL 内容相同但用途不同(apply vs SSoT)
"""ClickHouse c3_fundamental 财务三表 DDL 部署 + 精度验证脚本（audit 1.2 治本）。

DDL-as-Code 模式：
    - income_statement  DDL 真源为 schemas/categories/fundamental_income_statement.py
    - balance_sheet     DDL 真源为 schemas/categories/fundamental_balance_sheet.py
    - cashflow_statement DDL 真源为 schemas/categories/fundamental_cashflow_statement.py

精度裁定（audit 1.2 #ARCH-CH-026，2026-07-23）：
    金额字段 Decimal(18,2)、EPS 字段 Decimal(18,4)；verify() 强制校验金额字段为 Decimal
    而非 Float64，防止精度回退。

用法::

    python scripts/ch/apply_fundamental_tables_ddl.py           # 建表 + 验证
    python scripts/ch/apply_fundamental_tables_ddl.py --verify  # 仅验证

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
# schemas/ 在仓库根，需加入 path 以便导入 DDL 真源
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from zephyr.data import ch_reader, ch_writer

_DATABASE = "c3_fundamental"

# ========== DDL 真源导入 ==========
try:
    from schemas.categories.fundamental_balance_sheet import BALANCE_SHEET_DDL
    from schemas.categories.fundamental_cashflow_statement import CASHFLOW_STATEMENT_DDL
    from schemas.categories.fundamental_income_statement import INCOME_STATEMENT_DDL
except ImportError:
    print("[ERROR] 无法导入 schemas.categories.fundamental_* DDL 真源")
    sys.exit(2)

_ALL_DDL = [
    ("income_statement", INCOME_STATEMENT_DDL),
    ("balance_sheet", BALANCE_SHEET_DDL),
    ("cashflow_statement", CASHFLOW_STATEMENT_DDL),
]

# 金额字段（必须为 Decimal，audit 1.2 精度校验真源）
_MONEY_FIELDS = {
    "income_statement": {
        "Decimal(18,2)": ["total_revenue", "operating_revenue", "total_cost", "operating_cost",
                          "tax_surcharge", "selling_expense", "admin_expense", "financial_expense",
                          "rd_expense", "operating_profit", "non_op_income", "non_op_expense",
                          "total_profit", "income_tax", "net_profit_incl_minority",
                          "net_profit_excl_minority", "minority_interest", "comprehensive_income"],
        "Decimal(18,4)": ["eps_basic", "eps_diluted"],
    },
    "balance_sheet": {
        "Decimal(18,2)": ["monetary_capital", "accounts_receivable", "inventory", "total_current_assets",
                          "fixed_assets", "intangible_assets", "goodwill", "total_non_current_assets",
                          "total_assets", "short_term_loan", "long_term_loan", "accounts_payable",
                          "total_current_liabilities", "total_non_current_liabilities", "total_liabilities",
                          "equity_excl_minority", "equity_incl_minority", "capital_reserve",
                          "retained_earnings", "surplus_reserve"],
    },
    "cashflow_statement": {
        "Decimal(18,2)": ["ocf_net", "cash_from_sales", "ocf_inflow", "ocf_outflow", "icf_net",
                          "icf_inflow", "icf_outflow", "fcf_net", "fcf_inflow", "fcf_outflow",
                          "net_cash_increase", "ending_cash_balance", "fcff"],
    },
}

# SQL 常量集中化（NO-BARE-SQL gate 豁免 SQL_* 前缀）
SQL_CREATE_DB = "CREATE DATABASE IF NOT EXISTS {db}"
SQL_TABLES_ENGINE = "SELECT name, engine FROM system.tables WHERE database = '{db}' ORDER BY name"
SQL_COLUMNS_TYPE = ("SELECT name, type FROM system.columns "
                     "WHERE database='{db}' AND table='{table}' FORMAT TabSeparated")


def apply() -> int:
    """执行建表 DDL（CREATE TABLE IF NOT EXISTS，已存在表不受影响）。

    DDL 通过 ch_reader.query 执行（裁定 #ARCH-CH-007 CH-FINAL-GATE）：
    ch_reader.inject_final 仅对 SELECT 的 FROM 子句注入 FINAL，
    对 CREATE DATABASE/CREATE TABLE 无 FROM 子句则透传，功能等价 ch_writer.query。
    """
    print("=== 创建数据库 ===")
    ch_reader.query(SQL_CREATE_DB.format(db=_DATABASE))
    print(f"  {_DATABASE} ✓")

    print("\n=== 执行建表 DDL ===")
    for table, ddl in _ALL_DDL:
        print(f"  {table} ...", end=" ")
        ch_reader.query(ddl)
        print("✓")

    print("\n=== 建表完成 ===")
    return 0


def _parse_kv_lines(raw: str) -> dict[str, str]:
    """将 TSV 格式（key\\tvalue 每行）解析为 dict。"""
    result: dict[str, str] = {}
    for line in raw.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result


def _verify_engines(actual_engine: dict[str, str]) -> bool:
    """校验三表引擎均为 ReplacingMergeTree。返回是否全部一致。"""
    print("=== 引擎校验 ===")
    print(f"{'表名':<25} {'实际引擎':<35} {'状态'}")
    print("-" * 80)
    all_match = True
    for table, _ in _ALL_DDL:
        engine = actual_engine.get(table, "")
        if not engine:
            print(f"{table:<25} {'(不存在)':<35} ❌ 表不存在")
            all_match = False
            continue
        ok = engine.startswith("ReplacingMergeTree")
        print(f"{table:<25} {engine:<35} {'✅' if ok else '❌ 非 ReplacingMergeTree'}")
        if not ok:
            all_match = False
    return all_match


def _check_table_precision(table: str, prec_map: dict[str, list[str]],
                           col_types: dict[str, str]) -> tuple[int, int, list[str]]:
    """校验单表金额字段 Decimal 精度。返回 (total, decimal_ok, bad_list)。"""
    total = 0
    decimal_ok = 0
    bad: list[str] = []
    for expected_prec, fields in prec_map.items():
        for f in fields:
            total += 1
            actual_type = col_types.get(f, "")
            # 容忍 CH 格式空格：Nullable(Decimal(18, 2)) ~ Nullable(Decimal(18,2))
            norm = actual_type.replace(" ", "")
            if norm == f"Nullable({expected_prec.replace(' ', '')})":
                decimal_ok += 1
            else:
                bad.append(f"{f}={actual_type}(expect {expected_prec})")
    return total, decimal_ok, bad


def _verify_precision(all_match: bool) -> bool:
    """校验金额字段 Decimal 精度（audit 1.2 防回退核心）。"""
    print("\n=== 金额字段 Decimal 精度校验（audit 1.2 防回退）===")
    print(f"{'表名':<25} {'金额字段数':<12} {'Decimal 命中':<14} {'状态'}")
    print("-" * 80)
    for table, prec_map in _MONEY_FIELDS.items():
        col_raw = ch_reader.query(SQL_COLUMNS_TYPE.format(db=_DATABASE, table=table))
        col_types = _parse_kv_lines(col_raw)
        total, decimal_ok, bad = _check_table_precision(table, prec_map, col_types)
        status = "✅" if not bad else "❌"
        if bad:
            all_match = False
        print(f"{table:<25} {total:<12} {decimal_ok:<14} {status}")
        for b in bad:
            print(f"    {b}")
    return all_match


def verify() -> int:
    """验证引擎 + 金额字段 Decimal 精度（audit 1.2 防回退）。"""
    raw = ch_reader.query(SQL_TABLES_ENGINE.format(db=_DATABASE))
    if not raw.strip():
        print(f"[ERROR] 查询 system.tables 返回空——ClickHouse 可能不可达或库 {_DATABASE} 不存在")
        return 2

    actual_engine = _parse_kv_lines(raw)
    all_match = _verify_engines(actual_engine)
    all_match = _verify_precision(all_match)

    print("-" * 80)
    if all_match:
        print("[OK] 财务三表引擎 + 金额字段 Decimal 精度全部一致")
        return 0
    print("[FAIL] 存在不一致，请检查（金额字段回退 Float64 会导致 audit 1.2 复发）")
    return 1


def main() -> int:
    if "--verify" in sys.argv:
        return verify()
    rc = apply()
    if rc != 0:
        return rc
    return verify()


if __name__ == "__main__":
    sys.exit(main())
