# [BLUEPRINT] MOD-BT-212 | docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md
# [MODULE] scripts.ch.apply_decision_daily_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.decision_daily
# [CONSUMERS] c1_backtest.decision_daily（日度决策快照表部署+列校验+DESCRIBE 复核）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] DDL 用 admin（base 账号）执行（writer 无 CREATE 权限，#ARCH-CH-027）；
#   CREATE TABLE IF NOT EXISTS 幂等——可重复执行、只建不改（RULE-DATA-OPS：禁 DROP/ALTER 生产数据）；
#   表结构唯一真源在 schemas/categories/decision_daily.py，本脚本不内联 DDL；
#   双态：默认 --dry-run（零连接零副作用，只出预演文本）→ --apply 才碰生产 CH
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(DDL 失败或列漂移)；连接失败由 DatabaseService 抛
#   ClickHouseConnectionError(2002)->get_db_service().invalidate_clickhouse_conn 后人工重试
# [TESTS] tests/strategy_pipeline/test_decision_orchestrator.py
# [A_module] module_id=MOD-BT-212 | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# [COMPLETES_WHEN] c1_backtest.decision_daily 已在生产 CH 落地（apply --apply 全 OK+
#   DESCRIBE 复核过+verify_schema_truth 零漂移）；此后本脚本仅作重跑收敛与复核面
# [CREATION-TOKEN] apply-decision-daily-ddl-mod-bt-212-20260916
"""日度决策快照表 decision_daily 建表 DDL 部署+列校验（BT-P1-031 刀 1 一库，2026-09-16）。

真源：docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md §四.1/§七刀 1。
部署面：c1_backtest.decision_daily——日度编排器 T2 拍板留痕真源（一行=当日唯一放行凭证）。
apply 后自动 DESCRIBE 复核（蓝图刀 1 验收标准），漂移校验走 scripts/ch/verify_schema_truth.py。

[ALGO_FLOW]
输入: 无（读 schemas/categories/decision_daily.py 的 DDL 常量）
前置检查: DatabaseService admin 角色可用（CH 维护窗口外）
执行: execute(DDL) -> system.columns 取实际列 -> 与 INSERT_COLUMNS 声明列比对 -> DESCRIBE 复核
输出: stdout OK/FAIL；returncode 0=一致
降级: 建表失败 exit 1（单表件无多表降级语义），已建不回滚（IF NOT EXISTS 幂等，重跑收敛）
不变量: 只 CREATE IF NOT EXISTS，无任何 DROP/ALTER/TRUNCATE（RULE-DATA-OPS）
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories import decision_daily  # noqa: E402

TARGET = (decision_daily, "decision_daily")


def plan() -> tuple[str, str, list[str]]:
    """干跑清单：(表名, DDL, 写侧声明列)——不连库、零副作用（三步验证的"真实性"取证面）。

    声明列解析内联（FUNCTION-DUP 合规：与 allocation_persistence/apply_pf_alloc_ddl 的
    _declared_columns 同语义但单点内联，不再克隆第三份函数实现）。
    """
    module, category = TARGET
    body = module.INSERT_COLUMNS.strip()
    if body.startswith("(") and body.endswith(")"):
        body = body[1:-1]
    declared = [c.strip() for c in body.split(",") if c.strip()]
    return module.TABLE_NAME, module.DDL, declared


def dry_run() -> int:
    """预演态（默认）：打印 DDL 与声明列 + 自校验声明列非空/无重复，**不连生产 CH**。"""
    table, ddl, declared = plan()
    print("== DRY-RUN（不连库、不建表）==")
    bad = 0
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
    """建表 + 列校验 + DESCRIBE 复核。dry_run_flag=True 时等价 --dry-run（不连库）。"""
    if dry_run_flag:
        return dry_run()
    from zephyr.infrastructure.database_service import get_db_service

    module, category = TARGET
    table = module.TABLE_NAME
    client = get_db_service().get_clickhouse_conn(role="admin")
    client.execute(module.DDL)
    rows = client.execute(
        "SELECT name FROM system.columns WHERE database=%(db)s AND table=%(tb)s",
        {"db": module.DATABASE, "tb": category},
    )
    actual = {r[0] for r in rows}
    _, _, declared = plan()
    missing = set(declared) - actual
    if missing:
        print(f"FAIL: {table} 列缺失 {sorted(missing)}")
        return 1
    # DESCRIBE 复核（蓝图刀 1 验收标准：建表后 DESCRIBE 逐列打印人工可核）
    print(f"== DESCRIBE {table} ==")
    for line in client.execute(f"DESCRIBE TABLE {table}"):
        print("\t".join(str(c) for c in line[:2]))
    print(
        f"OK {table} 列数={len(actual)} 写侧列={len(declared)} "
        f"engine={module.ENGINE} order_by={module.ORDER_BY}"
    )
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="decision_daily 日度决策快照表：DDL-as-Code 部署（默认 dry-run，不连库）"
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="预演：打印 DDL/声明列并自校验（默认）")
    mode.add_argument("--apply", action="store_true", help="真建表（CREATE IF NOT EXISTS）+ 列校验 + DESCRIBE")
    args = ap.parse_args()
    sys.exit(apply(dry_run_flag=not args.apply))
