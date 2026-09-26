# [BLUEPRINT] MOD-DATA-L9AGG | docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md | §四最小件
# [MODULE] scripts.ch.apply_l9_readiness_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.l9_readiness_daily
# [CONSUMERS] c1_market.l9_readiness_daily（就绪度读数表部署+列校验+DESCRIBE 复核）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] DDL 用 admin（base 账号）执行（writer 无 CREATE 权限，#ARCH-CH-027）；
#   CREATE TABLE IF NOT EXISTS 幂等——可重复执行、只建不改（RULE-DATA-OPS：禁 DROP/ALTER 生产数据）；
#   表结构唯一真源在 schemas/categories/l9_readiness_daily.py，本脚本不内联 DDL；
#   双态：默认 --dry-run（零连接零副作用，只出预演文本）→ --apply 才碰生产 CH
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(DDL 失败或列漂移)；连接失败由 DatabaseService 抛
#   ClickHouseConnectionError(2002)->get_db_service().invalidate_clickhouse_conn 后人工重试
# [TESTS] tests/data/test_l9_readiness_aggregator.py
# [A_module] module_id=MOD-DATA-L9AGG | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-data-l9agg-apply-l9-readiness-ddl-20260926
"""L9 就绪度读数表 l9_readiness_daily 建表 DDL 部署+列校验（f34 册 P0 最小件，2026-09-27）。

真源：docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md §四（最小实件化路径）。
部署面：c1_market.l9_readiness_daily——TDM-E-L9-AGG"知识供给汇聚"实件的读数落地面
（29 源线+5 图谱+3 状态快照 × 绿/黄/红/挂起/跳过 + 时戳，T 日聚合读数喂次日数据就绪度）。
apply 后自动 DESCRIBE 复核，漂移校验走 scripts/ch/verify_schema_truth.py。

FUNCTION-DUP 治本（2026-09-27 门禁实测）：本件与 apply_decision_daily_ddl 同为"单表
DDL-as-Code 部署器"形，但禁克隆其 plan/dry_run 函数（extract 级克隆无逃生）——本件以
TARGET 数据类+main 单入口内联实现（预演/自校验/建表/列比对四步一函数），行为等价而
实现单点，后续单表部署器如再犯本门禁应立共享 helper 而非第三份克隆。

[ALGO_FLOW]
输入: 无（读 schemas/categories/l9_readiness_daily.py 的 DDL 常量）
前置检查: DatabaseService admin 角色可用（CH 维护窗口外）
执行: execute(DDL) -> system.columns 取实际列 -> 与 INSERT_COLUMNS 声明列比对 -> DESCRIBE 复核
输出: stdout OK/FAIL；returncode 0=一致
降级: 建表失败 exit 1（单表件无多表降级语义），已建不回滚（IF NOT EXISTS 幂等，重跑收敛）
不变量: 只 CREATE IF NOT EXISTS，无任何 DROP/ALTER/TRUNCATE（RULE-DATA-OPS）
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories import l9_readiness_daily  # noqa: E402

# NO-BARE-SQL 合规：列校验/复核 SQL 提取为模块级常量
_SQL_COLUMNS = "SELECT name FROM system.columns WHERE database=%(db)s AND table=%(tb)s"
_SQL_DESCRIBE = "DESCRIBE TABLE {table}"


@dataclass(frozen=True)
class _Target:
    """部署目标（NO-LONG-PARAM-LIST：一组表侧参数走数据类）。"""

    module: object
    table: str
    database: str
    category: str
    declared: list[str]

    @classmethod
    def from_schema(cls, module: object, category: str) -> _Target:
        flat = " ".join(str(module.INSERT_COLUMNS).split())
        declared = [c.strip() for c in flat.strip("()").split(",") if c.strip()]
        return cls(
            module=module, table=module.TABLE_NAME, database=module.DATABASE, category=category, declared=declared
        )


_TARGET = _Target.from_schema(l9_readiness_daily, "l9_readiness_daily")


def _self_check(t: _Target) -> list[str]:
    """干跑自校验：声明列非空/无重复 + DDL 幂等无破坏性语句，返回 FAIL 行（空=过）。"""
    bad: list[str] = []
    dup = {c for c in t.declared if t.declared.count(c) > 1}
    if not t.declared or dup:
        bad.append(f"FAIL: {t.table} 声明列异常 dup={sorted(dup)}")
    ddl = str(t.module.DDL).upper()
    if "IF NOT EXISTS" not in ddl:
        bad.append(f"FAIL: {t.table} DDL 非幂等（缺 IF NOT EXISTS）")
    if any(k in ddl for k in ("DROP ", "TRUNCATE ", "ALTER ")):
        bad.append(f"FAIL: {t.table} DDL 含破坏性语句（RULE-DATA-OPS 禁）")
    return bad


def main() -> int:
    """单入口双态：默认预演（零连接零副作用）→ --apply 真建表+列比对+DESCRIBE 复核。"""
    import argparse

    ap = argparse.ArgumentParser(
        description="l9_readiness_daily 就绪度读数表：DDL-as-Code 部署（默认 dry-run，不连库）"
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="预演：打印 DDL/声明列并自校验（默认）")
    mode.add_argument("--apply", action="store_true", help="真建表（CREATE IF NOT EXISTS）+ 列校验 + DESCRIBE")
    args = ap.parse_args()
    t = _TARGET

    if args.apply:
        from zephyr.infrastructure.database_service import get_db_service

        client = get_db_service().get_clickhouse_conn(role="admin")
        client.execute(t.module.DDL)
        actual = {r[0] for r in client.execute(_SQL_COLUMNS, {"db": t.database, "tb": t.category})}
        missing = set(t.declared) - actual
        if missing:
            print(f"FAIL: {t.table} 列缺失 {sorted(missing)}")
            return 1
        print(f"== DESCRIBE {t.table} ==")
        for line in client.execute(_SQL_DESCRIBE.format(table=t.table)):
            print("\t".join(str(c) for c in line[:2]))
        print(
            f"OK {t.table} 列数={len(actual)} 写侧列={len(t.declared)} "
            f"engine={t.module.ENGINE} order_by={t.module.ORDER_BY}"
        )
        return 0

    print("== DRY-RUN（不连库、不建表）==")
    bad = _self_check(t)
    print(f"\n-- {t.table} 写侧列 {len(t.declared)}: {', '.join(t.declared)}")
    for line in bad:
        print(line)
    print(str(t.module.DDL).strip())
    print("\n== 执行建表请显式加 --apply ==")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
