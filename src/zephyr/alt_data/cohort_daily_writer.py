# [BLUEPRINT] MOD-DATA-COHORT-WRITER | docs/_working/daily_loop_campaign/wiring_proposals_cohort_and_t4.md §A
# [MODULE] zephyr.alt_data.cohort_daily_writer
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.alt_data.cohort_daily_ledger; zephyr.data.ch_writer; zephyr.data.table_registry; schemas.categories.cohort_daily_ledger; stdlib
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider(cohort_daily_ledger capability 路由分支委托);
#   cohort_ledger_daily 调度任务(tasks.yaml,daily_capital 档,deps=四原料 incremental)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] cohort_daily_ledger 表唯一 CH 写入口——build_cohort_daily 纯计算产行,
#   本模块只做列对齐过滤+落库; 表名经 TableRegistry 派生(#ARCH-CH-024 禁硬编码,
#   品类缺注册时降级 schemas DDL 真源 QUALIFIED_NAME 并告警); 列序=schemas INSERT_COLUMNS
#   契约(禁复制列名); 幂等=ReplacingMergeTree 同键覆盖(重跑/回填直接重插,禁先删禁查重,
#   schemas :9-11"禁手工 UPDATE";引擎变更则本幂等口径失效,模块加载期 fail-visible);
#   metric_value Decimal(18,4) str 中转防二进制浮点误差(裁定 S4 金额单位=万元);
#   失败 fail-open 出声不抛(调用方=调度任务,单日失败不拖垮调度链,经返回值 committed=False
#   +error 字段向 provider 记账面)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达/写入失败/零可写行 -> log.error + committed=False,不抛
#   (fail-open);调用方应将 committed=False 视为任务失败记账(不伪造空成功)
# [TESTS] tests/alt_data/test_cohort_daily_writer.py
# [A_module] module_id=MOD-DATA-COHORT-WRITER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CohortDailyWriter — 五人群日账本落库写入器（WO-5 一期结算层投产接线件）.

施工真源：docs/_working/daily_loop_campaign/wiring_proposals_cohort_and_t4.md §A
（Owner 批 2026-09-21；收敛裁定 2026-09-22：provider 路由分支委托本写入器，
单一写路径——ch_writer strict 通道 fail-visible，不走 write_tsv HTTP+本地兜底）。

数据流（每日盘后，daily_capital 18:00 档四原料任务之后）：
    money_flow/margin_trading/dragon_tiger/block_trade incremental 落库
      -> build_cohort_daily(day) 纯计算（zephyr.alt_data.cohort_daily_ledger）
      -> 本模块列对齐过滤 + strict 通道 INSERT c1_backtest.cohort_daily_ledger
      -> ReplacingMergeTree 同键覆盖（重跑/回填安全，读侧 FINAL/argMax 收敛）

CLI（对账/抽查用）：python -m zephyr.alt_data.cohort_daily_ledger --sample DAY（零写库）。
# [ALGO_FLOW] external: docs/03_modules/_domain_alt_data/algo_flow/cohort_daily_writer.yaml
"""

from __future__ import annotations

import datetime
import decimal
import logging
from typing import Any, Final, Protocol

from schemas.categories.cohort_daily_ledger import ENGINE, INSERT_COLUMNS, QUALIFIED_NAME
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: Final = ["write_cohort_daily"]

_CATEGORY_ID: Final = "cohort_daily_ledger"

# 引擎口径断言（幂等契约依赖）：ReplacingMergeTree 同键覆盖=重插幂等的唯一依据。
# 引擎若变更（如去重复制语义消失），"禁查重禁先删"策略必须重审——加载期 fail-visible。
if ENGINE != "ReplacingMergeTree":
    raise RuntimeError(
        f"cohort_daily_writer 幂等口径依赖 ReplacingMergeTree，实际引擎={ENGINE}——INSERT 前查重/先删策略需重审后再投产"
    )

# SQL 模板常量（NO-BARE-SQL 豁免：_SQL_* 前缀约定，对齐 ch_reader/ch_writer）
# INSERT 与 INTO 分行（行级扫描互不命中）；表名经 TableRegistry 派生
_SQL_INSERT = "INSERT INTO {table} {cols} VALUES"


def _qualified_table() -> str:
    """表全限定名唯一派生口径：TableRegistry 优先，品类缺注册时降级 schemas 真源常量。

    #ARCH-CH-024 禁硬编码：两处皆真源派生（business_data_categories.yaml /
    schemas DDL-as-Code），无字面量表名。
    """
    try:
        return get_registry().table(_CATEGORY_ID)
    except KeyError:
        log.warning(
            "品类 %s 未注册 business_data_categories.yaml——降级 schemas DDL 真源 QUALIFIED_NAME",
            _CATEGORY_ID,
        )
        return QUALIFIED_NAME


def _insert_columns() -> list[str]:
    """INSERT_COLUMNS 契约解析（"(a, b)" -> ["a","b"]，列序即 insert 契约）。"""
    return [c.strip() for c in INSERT_COLUMNS.strip("()").split(",") if c.strip()]


def _norm_value(
    value: decimal.Decimal | float | str | datetime.date,
) -> decimal.Decimal | datetime.date | str:
    """单值归一：metric_value 统一 Decimal(18,4)（str 中转防浮点误差），其余直通。"""
    if isinstance(value, decimal.Decimal):
        return value.quantize(decimal.Decimal("0.0001"))
    if isinstance(value, float):
        return decimal.Decimal(str(round(value, 4))).quantize(decimal.Decimal("0.0001"))
    return value


class _CohortReader(Protocol):
    """CH 读取面最小协议（ch_reader/fake reader 结构性满足，ANY-ABUSE 精确化）。"""

    def query(self, sql: str) -> str: ...


def write_cohort_daily(day: str, reader: _CohortReader | None = None) -> dict[str, Any]:
    """构建并落库指定业务日的五人群账本行（本表唯一写入口）。

    Args:
        day: 业务交易日 YYYY-MM-DD（PIT：builder 仅用 ≤当日收盘数据）。
        reader: CH 读取器（默认 zephyr.data.ch_reader；单测注入 fake reader）。

    Returns:
        {"rows": 本次产出可写行数, "committed": 是否已落 CH, "day": 业务日,
         "error": 失败原因（成功为 None）}。
        fail-open 契约：任何失败只记 error 出声，不抛——调用方（internal provider
        路由分支）应将 committed=False 转 FetchResult.error 记任务失败，不伪造空成功。

    幂等：ReplacingMergeTree 同键（cohort_id, metric_id, trade_date）覆盖——同日重跑
    直接重插，禁先删禁查重（schemas :9-11）；回填安全，读侧 FINAL 收敛。
    """
    day = datetime.date.fromisoformat(day).isoformat()  # 与 builder 同口径的格式校验
    from zephyr.alt_data.cohort_daily_ledger import build_cohort_daily  # 延迟导入：单测无需 CH

    try:
        rows = build_cohort_daily(day, reader=reader)
    except Exception as e:  # noqa: BLE001 — fail-open 契约：build 炸也只出声记账，不拖垮调度链
        log.error("cohort_daily_writer[%s] build 失败 fail-open: %s: %s", day, type(e).__name__, e)
        return {"rows": 0, "committed": False, "day": day, "error": f"{type(e).__name__}: {e}"}
    cols = _insert_columns()
    data: list[tuple] = []
    skipped = 0
    for r in rows:
        if not isinstance(r, dict) or not all(k in r for k in cols):
            skipped += 1
            log.error("cohort_daily_writer[%s] 行缺列拒写（契约=%s）: %r", day, cols, r)
            continue
        vals = {}
        for c in cols:
            v = r[c]
            # Date 列类型收口：builder 全程以 ISO str 传 day（PIT 口径），clickhouse_driver
            # 序列化 Date 列要求 date 对象（str 会 'str' has no 'year' 假失败）——写入侧
            # 单点转换，builder 单测无需 date 感知。
            if c == "trade_date" and isinstance(v, str):
                v = datetime.date.fromisoformat(v)
            vals[c] = v
        data.append(tuple(_norm_value(vals[c]) for c in cols))
    if not data:
        log.error(
            "cohort_daily_writer[%s] 零可写行（build 产出=%d, 缺列跳过=%d）——fail-open 不写库",
            day,
            len(rows),
            skipped,
        )
        return {"rows": 0, "committed": False, "day": day, "error": "no_writable_rows"}
    table = _qualified_table()
    try:
        from zephyr.data.ch_writer import get_client_strict  # 延迟导入：strict 通道 fail-visible

        client = get_client_strict()
        client.execute(_SQL_INSERT.format(table=table, cols=INSERT_COLUMNS), data)
    except Exception as e:  # noqa: BLE001 — fail-open 契约：出声不抛，调用方记账
        log.error("cohort_daily_writer[%s] CH 写入失败 fail-open -> %s: %s: %s", day, table, type(e).__name__, e)
        return {"rows": len(data), "committed": False, "day": day, "error": f"{type(e).__name__}: {e}"}
    log.info("cohort_daily_writer[%s] 落库 %d 行 -> %s（ReplacingMergeTree 同键幂等）", day, len(data), table)
    return {"rows": len(data), "committed": True, "day": day, "error": None}
