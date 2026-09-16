# [BLUEPRINT] MOD-PA-043 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] scripts.ch.apply_pf_alloc_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.alloc_budget_daily;
#   schemas.categories.alloc_shrinkage_daily; schemas.categories.alloc_budget_change_log
# [CONSUMERS] c1_backtest.alloc_*（三张分配链落地表部署+列校验）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] DDL 用 admin（base 账号）执行（writer 无 CREATE 权限，#ARCH-CH-027）；
#   CREATE TABLE IF NOT EXISTS 幂等——可重复执行、只建不改（RULE-DATA-OPS：禁 DROP/ALTER 生产数据）；
#   表结构唯一真源在 schemas/categories/alloc_*.py，本脚本不内联 DDL；
#   双态：默认 --dry-run（零连接零副作用，只出预演文本）→ --apply 才碰生产 CH
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(DDL 失败或列漂移)；连接失败由 DatabaseService 抛
#   ClickHouseConnectionError(2002)->get_db_service().invalidate_clickhouse_conn 后人工重试
# [TESTS] tests/pf_alloc/test_pf_alloc_schemas.py; tests/pf_alloc/test_allocation_chain.py
# [A_module] module_id=MOD-PA-043 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] apply-pf_alloc-ddl-mod-pa-043-20260916
"""组合分配链三张落地表建表 DDL 部署+列校验（车道 D 实盘接线，2026-09-16）。

真源：pf_alloc_consumer_mining PFA-2——"ClickHouse 里没有任何 alloc/budget/shrinkage 表"，
分配链输出无处落地 => 不可对账、不可归因、不可回滚。本脚本落地 PFA-2 的建表面。

部署面（DDL-as-Code，表结构真源在 schemas/categories/）：
  c1_backtest.alloc_budget_daily       每策略每日分配/预算落地（grain 含 strategy_id）
  c1_backtest.alloc_shrinkage_daily    全局 Shrinkage 节流与总暴露（grain=trade_date+run_id）
  c1_backtest.alloc_budget_change_log  budget 变动裁决与三级升级事件流水（E-POS-40/41）

[ALGO_FLOW]
输入: 无（读 schemas/categories/alloc_*.py 的 DDL 常量）
前置检查: DatabaseService admin 角色可用（CH 维护窗口外）
执行: 逐表 execute(DDL) -> system.columns 取实际列 -> 与 INSERT_COLUMNS 声明列比对
输出: stdout 每表 OK/FAIL；returncode 0=全部一致
降级: 单表失败不阻断其余表部署（汇总后 exit 1），已建表不回滚（IF NOT EXISTS 幂等，重跑收敛）
不变量: 只 CREATE IF NOT EXISTS，无任何 DROP/ALTER/TRUNCATE（RULE-DATA-OPS）
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories import (  # noqa: E402
    alloc_budget_change_log,
    alloc_budget_daily,
    alloc_shrinkage_daily,
)

# (模块, 表名, 写侧声明列)——声明列必须全部真实存在于 DB，否则写侧 INSERT 静默列错位
TARGETS = (
    (alloc_budget_daily, "alloc_budget_daily"),
    (alloc_shrinkage_daily, "alloc_shrinkage_daily"),
    (alloc_budget_change_log, "alloc_budget_change_log"),
)


def _declared_columns(insert_columns: str) -> list[str]:
    """从 INSERT_COLUMNS 字面量解析列名（"(a, b,\n c)" -> [a,b,c]）。"""
    body = insert_columns.strip()
    if body.startswith("(") and body.endswith(")"):
        body = body[1:-1]
    return [c.strip() for c in body.split(",") if c.strip()]


def plan() -> list[tuple[str, str, list[str]]]:
    """干跑清单：(表名, DDL, 写侧声明列)——不连库、零副作用（三步验证的"真实性"取证面）。"""
    return [
        (module.TABLE_NAME, module.DDL, _declared_columns(module.INSERT_COLUMNS))
        for module, _category in TARGETS
    ]


def dry_run() -> int:
    """预演态（默认）：打印 DDL 与声明列 + 自校验声明列非空/无重复，**不连生产 CH**。"""
    print("== DRY-RUN（不连库、不建表）==")
    bad = 0
    for table, ddl, declared in plan():
        dup = {c for c in declared if declared.count(c) > 1}
        print(f"\n-- {table} 写侧列 {len(declared)}: {', '.join(declared)}")
        if not declared or dup:
            print(f"FAIL: {table} 声明列异常 dup={sorted(dup)}")
            bad += 1
        if "IF NOT EXISTS" not in ddl.upper():
            print(f"FAIL: {table} DDL 非幂等（缺 IF NOT EXISTS）")
            bad += 1
        if any(k in ddl.upper() for k in ("DROP ", "TRUNCATE ", "ALTER ")):
            print(f"FAIL: {table} DDL 含破坏性语句（RULE-DATA-OPS 禁）")
            bad += 1
        print(ddl.strip())
    print("\n== 执行建表请显式加 --apply ==")
    return 1 if bad else 0


def apply(dry_run_flag: bool = False) -> int:
    """建表 + 列校验。dry_run_flag=True 时等价 --dry-run（不连库）。"""
    if dry_run_flag:
        return dry_run()
    from zephyr.infrastructure.database_service import get_db_service

    client = get_db_service().get_clickhouse_conn(role="admin")
    failures: list[str] = []
    for module, category in TARGETS:
        table = module.TABLE_NAME
        client.execute(module.DDL)
        rows = client.execute(
            "SELECT name FROM system.columns WHERE database=%(db)s AND table=%(tb)s",
            {"db": module.DATABASE, "tb": category},
        )
        actual = {r[0] for r in rows}
        declared = set(_declared_columns(module.INSERT_COLUMNS))
        missing = declared - actual
        if missing:
            print(f"FAIL: {table} 列缺失 {sorted(missing)}")
            failures.append(table)
            continue
        print(
            f"OK {table} 列数={len(actual)} 写侧列={len(declared)} "
            f"order_by={module.ORDER_BY}"
        )
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="pf_alloc 三张分配链落地表：DDL-as-Code 部署（默认 dry-run，不连库）"
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="预演：打印 DDL/声明列并自校验（默认）")
    mode.add_argument("--apply", action="store_true", help="真建表（CREATE IF NOT EXISTS）+ 列校验")
    args = ap.parse_args()
    sys.exit(apply(dry_run_flag=not args.apply))
