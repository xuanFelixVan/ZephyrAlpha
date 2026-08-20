# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.reporting.reconciliation_schema
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] stdlib
# [CONSUMERS] 54_reconciliation_attribution §3.3/§3.7 落库施工批次(DDL 执行方)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 仅 schema 定义不执行 DDL(54号§7开放问题落地前提); append-only 语义(审计轨迹 30 天 read-only 触发器位预留); 哈希链字段齐全(prev_hash/record_hash 对齐 ReportPublisher 模式); SQLite 方言
# [MODIFY-GUARD] 54_reconciliation_attribution.md §3.3/§3.7
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/reporting/test_reconciliation_schema.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 无运行时输入（纯 DDL 常量模块）
# F1: reconciliation_differences——对账差异表(成交对账 5 类 DriftType 落库, 54 号 §3.3)
# F2: attribution_results——归因结果表(策略层/firm 层两层归因产物, §3.5 两层架构)
# F3: audit_trail——三阶段审计轨迹(原始事件/匹配决策/归因结果, §3.3, append-only + 哈希链)
# F4: report_archive——报告归档表(§3.7 ReportPublisher DB 归档位, 对齐哈希链模式)
# O1: ALL_TABLES 有序 DDL 元组 + table_names() 查询
# [/ALGO_FLOW]
"""D_REPORTING — 对账/归因 DB 持久化 schema 定义（54 号 §7 开放问题落地前提）。

**只做 schema 定义，不执行 DDL**（施工口径：schema 定义文件级）。
落库执行（连接管理/迁移/30 天 read-only 触发器安装）归后续持久化批次。

四张表（SQLite 方言，对齐 54 号 §3.3 三阶段审计轨迹 + §3.7 双渠道归档）：
  - reconciliation_differences：成交/持仓对账差异（DriftType 5 类 + 容差口径）
  - attribution_results：归因结果（策略层 StrategyBook 独立 PnL + firm 层聚合，
    portfolio_id 口径=策略 ID 或 firm 账户 ID，§3.5 对接契约）
  - audit_trail：三阶段审计轨迹（raw_event/match_decision/attribution 三阶段，
    append-only + prev_hash/record_hash 哈希链，30 天 read-only 触发器位预留）
  - report_archive：报告归档（ReportPublisher DB 归档位，哈希链对齐
    report_publisher.py _compute_record_hash 模式）
"""

from __future__ import annotations

from typing import Final

SCHEMA_VERSION: Final[str] = "1.0"

# ── 对账差异表（54 号 §3.3 三层对账差异落库）──
DDL_RECONCILIATION_DIFFERENCES: Final[str] = """
CREATE TABLE IF NOT EXISTS reconciliation_differences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,               -- 结算日 YYYY-MM-DD
    recon_layer TEXT NOT NULL,              -- trade / position / cash（三层对账）
    trade_id TEXT,                          -- 券商结算单 trade_id（持仓层为 NULL）
    symbol TEXT NOT NULL,
    drift_type TEXT NOT NULL,               -- DriftType 5 类（price/quantity/commission/missing_in_system/missing_in_broker）
    system_value TEXT,                      -- 系统侧值（Decimal 字符串，缺失侧为 NULL）
    broker_value TEXT,                      -- 券商侧值
    diff TEXT,                              -- system - broker（Decimal 字符串）
    detected_at TEXT NOT NULL,              -- UTC ISO8601
    schema_version TEXT NOT NULL DEFAULT '1.0'
)
""".strip()

# ── 归因结果表（54 号 §3.5 两层归因：策略层 + firm 层）──
DDL_ATTRIBUTION_RESULTS: Final[str] = """
CREATE TABLE IF NOT EXISTS attribution_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,                   -- 归因周期（日 YYYY-MM-DD / 周 ISO 周 / 月 YYYY-MM）
    portfolio_id TEXT NOT NULL,             -- firm 层=账户 ID；策略层=策略 ID（§3.5 对接契约）
    layer TEXT NOT NULL,                    -- strategy / firm
    allocation_effect TEXT,                 -- Brinson 配置效应（Decimal 字符串）
    selection_effect TEXT,                  -- 选择效应
    interaction_effect TEXT,                -- 交互效应
    total_return TEXT NOT NULL,             -- 区间总收益
    transaction_cost_drag TEXT,             -- TCA 成本拖拽（§3.2，未接入为 NULL）
    net_pnl TEXT,                           -- 净 PnL（策略层独立 PnL 主键字段）
    invariant_status TEXT,                  -- 求和不变量 PASS/FAIL（§3.5 硬门禁，策略层为 NULL）
    computed_at TEXT NOT NULL,              -- UTC ISO8601
    idempotency_key TEXT NOT NULL UNIQUE,   -- 幂等键（CTR-P1-009 对齐）
    schema_version TEXT NOT NULL DEFAULT '1.0'
)
""".strip()

# ── 三阶段审计轨迹表（54 号 §3.3：原始事件/匹配决策/归因结果）──
DDL_AUDIT_TRAIL: Final[str] = """
CREATE TABLE IF NOT EXISTS audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,
    stage TEXT NOT NULL,                    -- raw_event / match_decision / attribution
    event_type TEXT NOT NULL,               -- system_fill / broker_settlement / match_verdict / brinson_result ...
    payload_json TEXT NOT NULL,             -- 事件负载（canonical JSON）
    prev_hash TEXT NOT NULL,                -- 哈希链（首条空串）
    record_hash TEXT NOT NULL UNIQUE,       -- SHA-256 记录指纹
    recorded_at TEXT NOT NULL,              -- UTC ISO8601
    read_only_after TEXT,                   -- 30 天 read-only 触发器口径（到期日，§3.3）
    schema_version TEXT NOT NULL DEFAULT '1.0'
)
""".strip()

# ── 报告归档表（54 号 §3.7：ReportPublisher DB 归档位）──
DDL_REPORT_ARCHIVE: Final[str] = """
CREATE TABLE IF NOT EXISTS report_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archive_id TEXT NOT NULL UNIQUE,        -- ARCH-xxxxxxxxxx（ReportPublisher 口径）
    report_id TEXT NOT NULL,                -- 报告逻辑标识
    source TEXT NOT NULL,                   -- ReportSource 枚举值
    report_type TEXT NOT NULL,
    archived_at TEXT NOT NULL,              -- UTC ISO8601
    content_json TEXT NOT NULL,             -- canonical JSON
    content_hash TEXT NOT NULL,             -- SHA-256(content)
    prev_hash TEXT NOT NULL,                -- 哈希链（首条空串）
    record_hash TEXT NOT NULL UNIQUE,       -- SHA-256(链指纹)
    schema_version TEXT NOT NULL DEFAULT '1.0'
)
""".strip()

#: 全部建表 DDL（有序——audit_trail/report_archive 哈希链表依赖概念先行声明）
ALL_TABLES: Final[tuple[str, ...]] = (
    DDL_RECONCILIATION_DIFFERENCES,
    DDL_ATTRIBUTION_RESULTS,
    DDL_AUDIT_TRAIL,
    DDL_REPORT_ARCHIVE,
)

_TABLE_NAME_MAP: Final[dict[str, str]] = {
    "reconciliation_differences": DDL_RECONCILIATION_DIFFERENCES,
    "attribution_results": DDL_ATTRIBUTION_RESULTS,
    "audit_trail": DDL_AUDIT_TRAIL,
    "report_archive": DDL_REPORT_ARCHIVE,
}


def table_names() -> tuple[str, ...]:
    """返回已定义的表名（有序）。"""
    return tuple(_TABLE_NAME_MAP)


def get_ddl(table_name: str) -> str:
    """按表名取 DDL；未知表名抛 KeyError。"""
    return _TABLE_NAME_MAP[table_name]


__all__ = [
    "ALL_TABLES",
    "DDL_ATTRIBUTION_RESULTS",
    "DDL_AUDIT_TRAIL",
    "DDL_RECONCILIATION_DIFFERENCES",
    "DDL_REPORT_ARCHIVE",
    "SCHEMA_VERSION",
    "get_ddl",
    "table_names",
]
