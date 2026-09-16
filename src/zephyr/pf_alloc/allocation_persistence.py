# [BLUEPRINT] MOD-PA-032 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.allocation_persistence
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.data.ch_writer(write_tsv_outcome/tsv_escape, 经 DatabaseService 写角色);
#   schemas.categories.alloc_budget_daily / alloc_shrinkage_daily / alloc_budget_change_log(列清单真源)
# [CONSUMERS] zephyr.pf_alloc.allocation_orchestrator
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 写侧唯一出口（宪法 §9.1：禁裸 SQL 散落——列清单/表名一律取自 schemas DDL-as-Code）；
#   列序 = 各表 INSERT_COLUMNS 声明序（行以映射传入，按声明序取列，缺列=报错不静默补空）；
#   投递口径 = WriteOutcome.disposition（禁把 local_durable 伪装成 ch_committed）；
#   NOT_DURABLE → AllocationPersistenceError（fail-closed，分配结果不得"算了但没落地"）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AllocationPersistenceError(未持久化/行缺列)；sink 注入时由注入方决定返回语义
# [TESTS] tests/pf_alloc/test_pf_alloc_schemas.py; tests/pf_alloc/test_allocation_orchestrator.py
# [A_module] module_id=MOD-PA-032 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] allocation-persistence-mod-pa-032-20260916
"""allocation_persistence——分配链落地写侧（三表，车道 D 实盘接线，2026-09-16）。

真源：pf_alloc_consumer_mining PFA-2——"ClickHouse 里没有任何 alloc/budget/shrinkage 表"，
分配链即使被调用也无处落地 → 不可对账/不可归因。本模块是那张落地面的**写侧唯一出口**。

[ALGO_FLOW]
输入: 行映射序列（键=列名）+ 注入式 sink（默认 ch_writer.write_tsv_outcome）
前置检查: 每行必须含 INSERT_COLUMNS 声明的全部列（缺列抛错，禁静默补空掩盖口径漂移）
执行: 行映射 -> 按声明列序取格 -> tsv_escape -> TSV 字节 -> sink(table, cols, payload)
输出: 投递事实 "ch_committed" | "local_durable" | "not_durable"
降级: local_durable=CH 不可达时本地兜底待回灌（如实上报，不谎称入库）；not_durable=抛错
不变量: 只 INSERT 追加，永不 UPDATE/DELETE（MergeTree 只增，重跑=新 run_id）；
        ingest_ts 由 DB DEFAULT now64(3) 生成（本模块不传该列 → 生成器零墙钟，RULE-SCHEMA-TZ）
[/ALGO_FLOW]
"""

from __future__ import annotations

import math
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

try:
    from zephyr.shared.io.paths import REPO_ROOT as _REPO_ROOT
except Exception:  # noqa: BLE001 — 仅路径解析降级
    _REPO_ROOT = Path(__file__).resolve().parents[2]

# schemas/ DDL-as-Code 真源在仓根（不在 src 包内）——同 allocation_inputs 的挂载理由
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from schemas.categories import (  # noqa: E402
    alloc_budget_change_log,
    alloc_budget_daily,
    alloc_shrinkage_daily,
)

# sink: (table, columns_clause, tsv_bytes) -> 投递事实字符串
WriteSink = Callable[[str, str, bytes], str]


class AllocationPersistenceError(RuntimeError):
    """分配结果未获持久化（fail-closed，禁止"算了但没落地"）。"""

    error_code = "ZA-PA-0032"


def _declared_columns(insert_columns: str) -> tuple[str, ...]:
    """解析 INSERT_COLUMNS 字面量 "(a, b,\\n c)" -> ("a","b","c")（声明列唯一真源）。"""
    body = insert_columns.strip().strip("()")
    return tuple(c.strip() for c in body.split(",") if c.strip())


_SCHEMA_MODULES = (alloc_budget_daily, alloc_shrinkage_daily, alloc_budget_change_log)

# 表名 -> (声明列, 列子句)（写侧唯一映射，禁在调用方硬编码列名串）
TABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    mod.TABLE_NAME: _declared_columns(mod.INSERT_COLUMNS) for mod in _SCHEMA_MODULES
}
_CLAUSE_BY_TABLE: dict[str, str] = {
    mod.TABLE_NAME: mod.INSERT_COLUMNS for mod in _SCHEMA_MODULES
}


def _cell(value: Any) -> str:
    """单格 TSV 序列化（bool→1/0；NaN/None→\\N；其余交 ch_writer.tsv_escape）。"""
    from zephyr.data.ch_writer import tsv_escape

    if isinstance(value, bool):
        return "1" if value else "0"
    if value is None:
        return tsv_escape(None)
    if isinstance(value, float) and math.isnan(value):
        return tsv_escape(None)  # NaN 业务语义=未知 → NULL（CH Float64 可空，归因不造假）
    return tsv_escape(value)


def _default_sink(table: str, columns: str, payload: bytes) -> str:
    from zephyr.data import ch_writer

    outcome = ch_writer.write_tsv_outcome(table, columns, payload)
    return outcome.disposition.value


def write_rows(
    table: str,
    rows: Iterable[Mapping[str, Any]],
    *,
    sink: WriteSink | None = None,
    fail_closed: bool = True,
) -> tuple[int, str]:
    """按 DDL-as-Code 声明列序落一张表的一批行 -> (行数, 投递事实)。

    Raises:
        AllocationPersistenceError: 未知表名 / 行缺声明列 / 未持久化且 fail_closed=True
    """
    if table not in TABLE_COLUMNS:
        raise AllocationPersistenceError(f"未登记的分配表 {table}（须先在 schemas/categories 建 DDL）")
    declared = TABLE_COLUMNS[table]
    materialized = list(rows)
    lines: list[str] = []
    for idx, row in enumerate(materialized):
        missing = [c for c in declared if c not in row]
        if missing:
            raise AllocationPersistenceError(
                f"{table} 第 {idx} 行缺声明列 {missing}（禁静默补空——缺列即口径漂移）"
            )
        lines.append("\t".join(_cell(row[c]) for c in declared))
    if not lines:
        return 0, "skipped_empty"
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    disposition = (sink or _default_sink)(table, _CLAUSE_BY_TABLE[table], payload)
    if fail_closed and disposition not in ("ch_committed", "local_durable"):
        raise AllocationPersistenceError(f"{table} 落库未确认（disposition={disposition}）——fail-closed")
    return len(materialized), disposition


def write_budget_daily(rows: Sequence[Mapping[str, Any]], *, sink: WriteSink | None = None, **kw):
    return write_rows(alloc_budget_daily.TABLE_NAME, rows, sink=sink, **kw)


def write_shrinkage_daily(rows: Sequence[Mapping[str, Any]], *, sink: WriteSink | None = None, **kw):
    return write_rows(alloc_shrinkage_daily.TABLE_NAME, rows, sink=sink, **kw)


def write_budget_change_log(
    rows: Sequence[Mapping[str, Any]], *, sink: WriteSink | None = None, **kw
):
    return write_rows(alloc_budget_change_log.TABLE_NAME, rows, sink=sink, **kw)


# 表名常量（供报告/测试引用，禁散落字符串）
TABLE_NAMES = {
    "budget_daily": alloc_budget_daily.TABLE_NAME,
    "shrinkage_daily": alloc_shrinkage_daily.TABLE_NAME,
    "budget_change_log": alloc_budget_change_log.TABLE_NAME,
}
