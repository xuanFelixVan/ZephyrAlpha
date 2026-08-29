# [BLUEPRINT] MOD-RPT-037 | 待统筹登记（54号 BM-REC-02-B 归因结果落库+查询，§3.5 两层归因持久化）
# [MODULE] zephyr.reporting.attribution_result_store
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.reconciliation_schema(DDL真源); zephyr.reporting.attribution(求和不变量复用); zephyr.shared.contracts.performance_attribution_report(CTR-P1-009); zephyr.shared.io.paths(DB_PATH SSoT); zephyr.shared.io.sqlite_factory(get_db_connection)
# [CONSUMERS] 归因报告生成链路(54号 BM-REC-02-B); 55号复盘(归因结果消费)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] append-only仅INSERT(INSERT OR IGNORE同幂等键跳过保首条); SQL参数化+常量(NO-BARE-SQL); db_path默认None走DB_PATH SSoT(测试注入临时库); DDL真源=reconciliation_schema.get_ddl("attribution_results")不复制副本; 数值落库=repr保原文字符串(防浮点二次失真); 只消费不改对账内核
# [MODIFY-GUARD] 54_reconciliation_attribution.md §3.5/§7
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(输入非法fail-closed); sqlite3.Error透传
# [TESTS] tests/reporting/test_attribution_result_store.py
# [A_module] module_id=MOD-RPT-037 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_REPORTING — 归因结果落库 + 查询接口（54 号 BM-REC-02-B 残余清偿）。

残余阻塞清偿口径（#ARCH-214 留痕："BM-REC-02-B 数据模型+产出逻辑+契约层
三段齐备；残余阻塞=消费落库 DDL" + 54 号 §2.4 横向缺口"归因结果表无 DDL 执行
/无查询接口"）：
  1. ensure_attribution_results_table——消费 reconciliation_schema 既有
     attribution_results DDL 真源执行建表（54 号 §7"对账/归因 DB 持久化 schema"
     开放问题的归因侧落地；本模块即 reconciliation_schema.py [CONSUMERS] 登记的
     "54 号 §3.3/§3.7 落库施工批次（DDL 执行方）"）。不新建表、不复制 DDL。
  2. store_attribution_report——CTR-P1-009 报告落库（firm/strategy 两层），
     idempotency_key UNIQUE 幂等（同键重复=跳过保首条返同 id，对齐
     prediction_log_writer 落库语义先例）。
  3. persist_two_layer_attribution——两层归因编排落库（54 号 §3.5）：firm 层
     挂求和不变量门禁状态（复用 zephyr.reporting.attribution.
     validate_strategy_pnl_invariant，不重复实现），策略层逐策略落 net_pnl；
     FAIL 显式落 invariant_status 供发布方拒发+告警。
  4. query_attribution_results / get_attribution_by_key——组合过滤查询接口
     （保原文字符串不回解析，调用方自行 float()——防浮点二次失真，同
     prediction_log_writer 契约）。

落库库位：governance.db（DB_PATH SSoT，对齐 reconciliation_differences 落
治理库先例，见 trading/recon_runner.py）。本模块只消费既有表/内核，不改
SettlementReconciler/PositionReconciler/DailyAuditor。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Mapping

from zephyr.reporting.attribution import (
    INVARIANT_TOLERANCE_BPS,
    validate_strategy_pnl_invariant,
)
from zephyr.reporting.reconciliation_schema import SCHEMA_VERSION, get_ddl
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.sqlite_factory import get_db_connection

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ATTRIBUTION_LAYERS",
    "LAYER_FIRM",
    "LAYER_STRATEGY",
    "TwoLayerPersistResult",
    "ensure_attribution_results_table",
    "get_attribution_by_key",
    "persist_two_layer_attribution",
    "query_attribution_results",
    "store_attribution_report",
]

# ── 两层归因层位枚举（54 号 §3.5：firm=组合层账户 ID / strategy=策略层策略 ID）──
LAYER_FIRM: Final = "firm"
LAYER_STRATEGY: Final = "strategy"
ATTRIBUTION_LAYERS: Final = frozenset({LAYER_FIRM, LAYER_STRATEGY})

_INVARIANT_STATUSES: Final = frozenset({"PASS", "FAIL"})
_DEFAULT_QUERY_LIMIT: Final = 1000

# ── SQL 常量（NO-BARE-SQL 门禁；append-only 仅 INSERT，参数化防注入）──
_SQL_INSERT: Final = (
    "INSERT OR IGNORE INTO attribution_results "
    "(period, portfolio_id, layer, allocation_effect, selection_effect, "
    "interaction_effect, total_return, transaction_cost_drag, net_pnl, "
    "invariant_status, computed_at, idempotency_key, schema_version) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SQL_SELECT_ID_BY_KEY: Final = (
    "SELECT id FROM attribution_results WHERE idempotency_key = ?"
)
_SQL_QUERY_BASE: Final = (
    "SELECT id, period, portfolio_id, layer, allocation_effect, selection_effect, "
    "interaction_effect, total_return, transaction_cost_drag, net_pnl, "
    "invariant_status, computed_at, idempotency_key, schema_version "
    "FROM attribution_results"
)
_SQL_WHERE_PORTFOLIO: Final = "portfolio_id = ?"
_SQL_WHERE_PERIOD: Final = "period = ?"
_SQL_WHERE_LAYER: Final = "layer = ?"
_SQL_QUERY_TAIL: Final = "ORDER BY period DESC, id DESC LIMIT ?"
_SQL_SELECT_BY_KEY: Final = _SQL_QUERY_BASE + " WHERE idempotency_key = ?"


@dataclass(frozen=True)
class TwoLayerPersistResult:
    """两层归因编排落库结果（不可变）。"""

    firm_row_id: int
    strategy_row_ids: dict[str, int]
    invariant_status: str  # PASS / FAIL（54 号 §3.5 硬门禁状态，FAIL 供发布方拒发）
    invariant: dict  # validate_strategy_pnl_invariant 完整返回（差异定位用）
    rows_written: int


def _resolve_db_path(db_path: str | Path | None) -> Path:
    """db_path 解析：None=DB_PATH SSoT（测试注入临时库走显式参数）。"""
    return Path(db_path) if db_path is not None else DB_PATH


def _validate_layer(layer: object) -> str:
    if layer not in ATTRIBUTION_LAYERS:
        raise ValueError(f"layer 非法（须 firm/strategy）: {layer!r}")
    return str(layer)


def _validate_invariant_status(status: object) -> str | None:
    if status is None:
        return None
    if status not in _INVARIANT_STATUSES:
        raise ValueError(f"invariant_status 非法（须 PASS/FAIL/None）: {status!r}")
    return str(status)


def _validate_idempotency_key(key: object) -> str:
    if not isinstance(key, str) or not key.strip():
        raise ValueError(f"idempotency_key 非法（须非空字符串）: {key!r}")
    return key.strip()


def _derive_period(report: PerformanceAttributionReport) -> str:
    """period 列推导：单日=YYYY-MM-DD；跨期="start~end"（schema 注释口径）。"""
    start = report.period_start.strip() if isinstance(report.period_start, str) else ""
    end = report.period_end.strip() if isinstance(report.period_end, str) else ""
    if not start or not end:
        raise ValueError(
            f"period_start/period_end 不能为空: {report.period_start!r}/{report.period_end!r}"
        )
    return start if start == end else f"{start}~{end}"


def ensure_attribution_results_table(db_path: str | Path | None = None) -> Path:
    """幂等建表（CREATE TABLE IF NOT EXISTS；DDL 真源=reconciliation_schema）。

    Args:
        db_path: 库路径；None=DB_PATH SSoT（governance.db）。

    Returns:
        实际建表库路径。
    """
    resolved = _resolve_db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(resolved)
    try:
        conn.execute(get_ddl("attribution_results"))
    finally:
        conn.close()
    return resolved


def store_attribution_report(
    report: PerformanceAttributionReport,
    *,
    layer: str = LAYER_FIRM,
    net_pnl: float | None = None,
    invariant_status: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    """CTR-P1-009 归因报告落库（幂等：同 idempotency_key 重复写=跳过保首条）。

    Args:
        report: CTR-P1-009 契约报告（firm 层=账户 ID；策略层=策略 ID，54 号 §3.5）。
        layer: firm / strategy。
        net_pnl: 净 PnL（策略层独立 PnL 主键字段；可空）。
        invariant_status: 求和不变量门禁状态（firm 层挂 PASS/FAIL；策略层 None）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。

    Returns:
        行 id——新插入=新 id；同键重复=已存在行 id（首条保留不覆写）。

    Raises:
        ValueError: layer/invariant_status/idempotency_key/period 非法（fail-closed）。
        sqlite3.Error: 库级异常透传（表缺失先调 ensure_attribution_results_table）。
    """
    v_layer = _validate_layer(layer)
    v_status = _validate_invariant_status(invariant_status)
    v_key = _validate_idempotency_key(report.idempotency_key)
    v_period = _derive_period(report)
    computed_at = datetime.now(UTC).isoformat()

    conn = get_db_connection(_resolve_db_path(db_path))
    try:
        cur = conn.execute(
            _SQL_INSERT,
            (
                v_period,
                report.portfolio_id,
                v_layer,
                repr(report.allocation_effect),
                repr(report.selection_effect),
                repr(report.interaction_effect),
                repr(report.total_return),
                repr(report.transaction_cost_drag),
                repr(net_pnl) if net_pnl is not None else None,
                v_status,
                computed_at,
                v_key,
                SCHEMA_VERSION,
            ),
        )
        if cur.rowcount == 1:
            return int(cur.lastrowid)
        # 同幂等键重复：跳过保首条，返回已存在行 id
        row = conn.execute(_SQL_SELECT_ID_BY_KEY, (v_key,)).fetchone()
        return int(row["id"]) if row is not None else -1
    finally:
        conn.close()


def persist_two_layer_attribution(
    firm_report: PerformanceAttributionReport,
    strategy_reports: Mapping[str, PerformanceAttributionReport],
    strategy_pnls: Mapping[str, float],
    firm_pnl: float,
    *,
    tolerance_bps: float = INVARIANT_TOLERANCE_BPS,
    db_path: str | Path | None = None,
) -> TwoLayerPersistResult:
    """两层归因编排落库（54 号 §3.5：firm 层 + 策略层 + 求和不变量硬门禁）。

    流程：①键集一致性 fail-closed → ②求和不变量校验（复用
    zephyr.reporting.attribution.validate_strategy_pnl_invariant）→ ③firm 行
    挂 invariant_status 落库 → ④策略行逐策略落 net_pnl（invariant_status=None，
    schema 口径）。FAIL 不静默：状态落库供发布方拒发+告警，差异定位信息随
    result.invariant 返回（成交漏算/费率错算/T+1 跨日/firm 裁剪副作用）。

    Args:
        firm_report: firm 层 CTR-P1-009 报告（portfolio_id=账户 ID）。
        strategy_reports: {strategy_id: 策略层 CTR-P1-009 报告}（portfolio_id=策略 ID）。
        strategy_pnls: {strategy_id: 净 PnL}（不变量校验策略层输入）。
        firm_pnl: firm 层净 PnL（不变量校验基准）。
        tolerance_bps: 不变量容差（默认 1bp=0.01%，54 号 §3.5）。
        db_path: 库路径；None=DB_PATH SSoT。

    Returns:
        TwoLayerPersistResult（含不变量完整判定，FAIL 时调用方据以拒发报告）。

    Raises:
        ValueError: strategy_reports 与 strategy_pnls 键集不一致（fail-closed，
            先于任何落库）。
    """
    report_keys = set(strategy_reports)
    pnl_keys = set(strategy_pnls)
    if report_keys != pnl_keys:
        raise ValueError(
            f"strategy_reports 与 strategy_pnls 键集不一致: "
            f"only_reports={sorted(report_keys - pnl_keys)} "
            f"only_pnls={sorted(pnl_keys - report_keys)}"
        )

    invariant = validate_strategy_pnl_invariant(
        dict(strategy_pnls), firm_pnl, tolerance_bps
    )
    status = str(invariant["invariant_status"])
    if status != "PASS":
        _logger.warning(
            "两层归因求和不变量 FAIL: diff=%s diff_bps=%s（54 号 §3.5 硬门禁，供发布方拒发）",
            invariant["diff"],
            invariant["diff_bps"],
        )

    firm_row_id = store_attribution_report(
        firm_report, layer=LAYER_FIRM, net_pnl=firm_pnl, invariant_status=status,
        db_path=db_path,
    )
    strategy_row_ids = {
        sid: store_attribution_report(
            strategy_reports[sid], layer=LAYER_STRATEGY, net_pnl=strategy_pnls[sid],
            db_path=db_path,
        )
        for sid in strategy_reports
    }
    return TwoLayerPersistResult(
        firm_row_id=firm_row_id,
        strategy_row_ids=strategy_row_ids,
        invariant_status=status,
        invariant=invariant,
        rows_written=1 + len(strategy_row_ids),
    )


def query_attribution_results(
    portfolio_id: str | None = None,
    period: str | None = None,
    layer: str | None = None,
    limit: int = _DEFAULT_QUERY_LIMIT,
    db_path: str | Path | None = None,
) -> list[dict]:
    """查询归因结果（过滤器可组合，按 period/id 倒序）。

    Args:
        portfolio_id: 组合/策略 ID 过滤（None=不限；给定须非空）。
        period: 周期过滤（None=不限；给定须非空；跨期口径 "start~end"）。
        layer: firm/strategy 过滤（None=不限）。
        limit: 返回上限（须正整数）。
        db_path: 库路径；None=DB_PATH SSoT。

    Returns:
        行 dict 列表（数值列保持落库原文字符串，调用方自行 float()——
        落库契约保原文不回解析，防浮点二次失真）。

    Raises:
        ValueError: 过滤器非法（fail-closed）。
    """
    where: list[str] = []
    params: list[object] = []
    if portfolio_id is not None:
        if not isinstance(portfolio_id, str) or not portfolio_id.strip():
            raise ValueError(f"portfolio_id 非法（须非空字符串）: {portfolio_id!r}")
        where.append(_SQL_WHERE_PORTFOLIO)
        params.append(portfolio_id.strip())
    if period is not None:
        if not isinstance(period, str) or not period.strip():
            raise ValueError(f"period 非法（须非空字符串）: {period!r}")
        where.append(_SQL_WHERE_PERIOD)
        params.append(period.strip())
    if layer is not None:
        where.append(_SQL_WHERE_LAYER)
        params.append(_validate_layer(layer))
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError(f"limit 非法（须正整数）: {limit!r}")

    sql = _SQL_QUERY_BASE
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " " + _SQL_QUERY_TAIL
    params.append(limit)

    conn = get_db_connection(_resolve_db_path(db_path))
    try:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_attribution_by_key(
    idempotency_key: str,
    db_path: str | Path | None = None,
) -> dict | None:
    """按幂等键精确查询归因结果（未命中返回 None）。

    Raises:
        ValueError: idempotency_key 非法（fail-closed）。
    """
    v_key = _validate_idempotency_key(idempotency_key)
    conn = get_db_connection(_resolve_db_path(db_path))
    try:
        row = conn.execute(_SQL_SELECT_BY_KEY, (v_key,)).fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()
