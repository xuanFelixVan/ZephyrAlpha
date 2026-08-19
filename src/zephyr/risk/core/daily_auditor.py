# [BLUEPRINT] MOD-RK-20 | docs/03_modules/_domain_risk/daily_auditor/blueprint.md
# [MODULE] zephyr.risk.core.daily_auditor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.alerts.threshold_loader; MOD-RK-16(Risk Decomposition,归因复用); MOD-RK-06(限额消耗); MOD-RK-03(持仓快照)
# [CONSUMERS] D-REPORTING(CTR-P1-011 AuditRiskMetricsReport)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] total_pnl=realized+unrealized;gap=expected-total_pnl;归因占比分母=|factor_pnl|+|residual_pnl|;任一FAIL→整体FAIL;报告幂等(同日同组合等价)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAuditInputError; AlertThresholdConfigError(注册表缺失/畸形)
# [TESTS] tests/risk/test_daily_auditor.py
# [A_module] module_id=MOD-RK-20 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Post-Trade Daily Auditor — 日终审计器 (MOD-RK-20)

D-RISK §1.2 L3 Post-Trade 盘后审计核心模块。每个交易日收盘后执行:
    1. 日终 PnL 对账: 预期 (Mark-to-Market) vs 账面 (realized+unrealized), 检测资金缺口
       - expected = Σ qty_i × (close_i − prev_close_i) − total_cost
       - total_pnl = realized + unrealized
       - gap = expected − total_pnl ; gap_pct = gap / |nav|
    2. 归因偏差检测: 预测因子贡献占比 (RK-16) vs 实际 PnL 因子占比
       - bias = predicted_factor_pct − actual_factor_pct
    3. 合规报告: 逐项限额检查 (OK/WARNING/BREACHED)
    4. 日终检查清单: 持仓/PnL/限额/Kill Switch/数据完整性 (5 项)
    5. 问题追溯修正: 失败项自动登记 IssueRecord
    6. CTR-P1-011 AuditRiskMetricsReport: 产出报告契约供 D-REPORTING

属 A 类基础设施 (对账 + 报告装配, 逻辑确定), 不参与热路径。
依据: D:\临时工作区\依赖图	-D-RISK-风控域.md §1.2 RK-20, §2 依赖(RK-03/RK-06/RK-16→RK-20)
SSoT: depgraph MOD-RK-20
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓快照对 列表
#   fields: positions_prev(提供前收)+positions_now(提供当收/开仓价) AuditPositionSnapshot{symbol,qty,avg_entry_price,close_price}拒绝NaN
#   code: AuditRequest L502-503
# - id: I2
#   name: 当日成交记录 列表
#   fields: FillRecord{symbol,qty(正买负卖),price,realized_pnl,cost佣金滑点}
#   code: AuditRequest fills L504
# - id: I3
#   name: 限额消耗 列表
#   fields: LimitConsumption{limit_type,value上限,consumed已消耗}来自RK-06; 拒绝NaN/负消耗
#   code: AuditRequest consumptions L506
# - id: I4
#   name: 风险分解与实际因子PnL
#   fields: DecompositionResult(RK-16, None=不检测归因) + actual_factor_pnl + actual_residual_pnl
#   code: AuditRequest L507-509
# - id: I5
#   name: 组合状态参数
#   fields: nav组合净值/kill_switch_state(Kill Switch状态)/data_completeness数据完整性
#   code: AuditRequest L505 + L510-511
# 层: 算法
# - id: A1
#   name_zh: ① PnL对账
#   name_en: reconcile_pnl
#   intro: 资产负债表恒等式对账预期vs账面PnL, 检测资金缺口
#   desc: expected=(MV_now−MV_prev)−trade_cash; total_pnl=realized+unrealized(未实现按prev_close→close, 新仓用avg_entry); gap=expected−total; gap_pct=gap/|nav|; |gap_pct|≤0.001容差→MATCH否则MISMATCH
#   inputs: I1 I2 I5
#   outputs: PnLReconciliation(含gap/gap_pct/status)
#   invariant: total_pnl=realized+unrealized; gap=expected−total_pnl
# - id: A2
#   name_zh: ② 归因偏差检测
#   name_en: detect_attribution_bias
#   intro: 预测因子贡献占比vs实际因子PnL占比算归因偏差
#   desc: actual_pct=factor_pnl/(|factor_pnl|+|residual_pnl|); bias=predicted−actual; |bias|>0.1→BIASED; 无分解或分母=0→NOT_APPLICABLE/ALIGNED
#   inputs: I4
#   outputs: AttributionBias
#   invariant: 归因占比分母=|factor_pnl|+|residual_pnl|
# - id: A3
#   name_zh: ③ 限额合规检查
#   name_en: run_compliance_check
#   intro: 逐项限额算利用率分OK/WARNING/BREACHED再汇总整体状态
#   desc: utilization=consumed/value; >1.0→BREACHED; >0.8→WARNING; 否则OK; value≤0有消耗→BREACHED; 有BREACHED→FAIL, 有WARNING→PASS_WITH_WARNINGS
#   inputs: I3
#   outputs: ComplianceReport
#   invariant: 任一BREACHED→整体FAIL
# - id: A4
#   name_zh: ④ 日终审计聚合
#   name_en: DailyAuditor.audit
#   intro: 串起对账+归因+合规+5项检查清单聚成总报告并自动登记问题
#   desc: 5项清单(持仓/PnL/限额/KillSwitch终态CLOSED/数据完整性); 失败项自动登记IssueRecord(根因/修正待人工); 任一FAIL→FAIL有WARNING→PASS_WITH_WARNINGS
#   inputs: A1 A2 A3 I1 I5
#   outputs: DailyAuditReport(含issues)
#   invariant: 任一FAIL→整体FAIL; 报告幂等(同日同组合等价)
# - id: A5
#   name_zh: ⑤ 风险指标报告生成
#   name_en: generate_risk_metrics_report
#   intro: 从审计报告抽关键指标产出CTR-P1-011契约报告
#   desc: report_id=RMR-{portfolio_id}-{trading_date}; 汇总total_pnl/gap_pct/合规与审计状态/issues数/HIGH严重度数
#   inputs: A4
#   outputs: AuditRiskMetricsReport
# 层: 输出
# - id: O1
#   name_zh: 日终审计报告
#   name_en: DailyAuditReport
#   intro: 含PnL对账/归因偏差/合规报告/检查清单/问题追溯/整体状态的完整日终审计报告
#   invariant: 报告幂等(同日同组合等价)
#   downstream: 无下游/内部使用(经A5转为契约报告外发)
# - id: O2
#   name_zh: 审计风险指标报告
#   name_en: AuditRiskMetricsReport
#   intro: CTR-P1-011产出契约, 供报表域消费的审计指标报告
#   downstream: D-REPORTING(CTR-P1-011 AuditRiskMetricsReport)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I5 --> A1
# I4 --> A2
# I3 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> A4
# I1 --> A4
# I5 --> A4
# A4 --> O1
# A4 --> A5
# A5 --> O2
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Final

from zephyr.risk.core.risk_decomposition import DecompositionResult
from zephyr.risk.core.var_backtester import BacktestObservation, VarBacktester
from zephyr.shared.alerts.threshold_loader import load_alert_thresholds
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "AuditPositionSnapshot",
    "FillRecord",
    "LimitConsumption",
    "PnLReconciliation",
    "AttributionBias",
    "ComplianceCheck",
    "ComplianceReport",
    "ChecklistItem",
    "IssueRecord",
    "DailyAuditReport",
    "AuditRiskMetricsReport",
    "AuditConfig",
    "AuditRequest",
    "DailyAuditor",
    "InvalidAuditInputError",
    "VarBacktestReport",
    "VAR_BACKTEST_MIN_SAMPLES",
    "VAR_BACKTEST_LOW_POWER_SAMPLES",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidAuditInputError(ZephyrBaseError):
    """日终审计输入数据非法 (持仓 symbol 不一致 / 数量 NaN / 容差非正 / 限额消耗非法)。"""

    error_code = "ZA-RK-0020"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class ReconciliationStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"


class AttributionStatus(str, Enum):
    ALIGNED = "ALIGNED"
    BIASED = "BIASED"
    NOT_APPLICABLE = "NOT_APPLICABLE"  # 无因子模型, 无法判定


class CheckStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    BREACHED = "BREACHED"
    FAIL = "FAIL"
    PASS = "PASS"


class AuditStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"


class IssueSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IssueStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


# ──────────────────────────────────────────────────────────────────────────────
# 输入数据结构
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AuditPositionSnapshot:
    """持仓快照 (单个 symbol)。

    Attributes:
        symbol: 标的代码
        qty: 持仓数量 (可为 0, 表示已平仓)
        avg_entry_price: 平均开仓价
        close_price: 收盘价 (当日)
    """

    symbol: str
    qty: float
    avg_entry_price: float
    close_price: float


@dataclass(frozen=True)
class FillRecord:
    """成交记录。

    Attributes:
        symbol: 标的代码
        qty: 成交数量 (正=买入, 负=卖出)
        price: 成交价
        realized_pnl: 已实现盈亏 (卖出时产生)
        cost: 交易成本 (佣金+滑点)
    """

    symbol: str
    qty: float
    price: float
    realized_pnl: float = 0.0
    cost: float = 0.0


@dataclass(frozen=True)
class LimitConsumption:
    """限额消耗 (来自 RK-06)。

    Attributes:
        limit_type: 限额类型 (如 VAR_95 / SECTOR_EXPOSURE)
        value: 限额值 (上限)
        consumed: 已消耗值
    """

    limit_type: str
    value: float
    consumed: float


# ──────────────────────────────────────────────────────────────────────────────
# 结果数据结构
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PnLReconciliation:
    """PnL 对账结果。

    采用资产负债表恒等式 (gross, 成本单列):
        expected = (MV_now − MV_prev) − trade_cash
        - MV_now = Σ qty_now × close ; MV_prev = Σ qty_prev × close_prev
        - trade_cash = Σ fill.qty × fill.price (买入 cash out, 卖出 cash in)
        total_pnl = realized + unrealized (gross)
        - unrealized = Σ qty_now × (close − prev_close)  [当日, prev_close→close]
        gap = expected − total_pnl  (一致时 =0; 检测缺失成交/已实现盈亏错误)

    Attributes:
        expected_pnl: 预期 PnL (资产负债表)
        realized_pnl: 已实现 PnL (gross, 不含成本)
        unrealized_pnl: 未实现 PnL (当日 prev_close→close)
        total_pnl: 账面总 PnL = realized + unrealized
        gap: 对账缺口 = expected − total_pnl
        gap_pct: 缺口占 NAV 比例 = gap / |nav|
        status: MATCH (|gap_pct| ≤ tolerance) / MISMATCH
        total_cost: 交易成本合计 (佣金+滑点, 报告用, 不参与 gap)
    """

    expected_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    gap: float
    gap_pct: float
    status: ReconciliationStatus
    total_cost: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "expected_pnl": self.expected_pnl,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "total_pnl": self.total_pnl,
            "gap": self.gap,
            "gap_pct": self.gap_pct,
            "status": self.status.value,
            "total_cost": self.total_cost,
        }


@dataclass(frozen=True)
class AttributionBias:
    """归因偏差检测结果。

    Attributes:
        predicted_factor_pct: 预测因子贡献占比 (来自 RK-16, 0~1)
        actual_factor_pct: 实际因子 PnL 占比
        bias: 偏差 = predicted − actual
        status: ALIGNED / BIASED / NOT_APPLICABLE
    """

    predicted_factor_pct: float | None
    actual_factor_pct: float
    bias: float
    status: AttributionStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "predicted_factor_pct": self.predicted_factor_pct,
            "actual_factor_pct": self.actual_factor_pct,
            "bias": self.bias,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ComplianceCheck:
    """单项限额合规检查。

    Attributes:
        limit_type: 限额类型
        value: 限额值
        consumed: 已消耗
        utilization: 利用率 = consumed / value (value<=0 时为 0 或 inf)
        status: OK / WARNING / BREACHED
        message: 说明
    """

    limit_type: str
    value: float
    consumed: float
    utilization: float
    status: CheckStatus
    message: str


@dataclass(frozen=True)
class ComplianceReport:
    """合规报告。

    Attributes:
        checks: 各限额检查结果
        overall_status: PASS (全 OK) / PASS_WITH_WARNINGS (有 WARNING 无 BREACHED) / FAIL (有 BREACHED)
    """

    checks: list[ComplianceCheck]
    overall_status: AuditStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [
                {
                    "limit_type": c.limit_type,
                    "value": c.value,
                    "consumed": c.consumed,
                    "utilization": c.utilization,
                    "status": c.status.value,
                    "message": c.message,
                }
                for c in self.checks
            ],
            "overall_status": self.overall_status.value,
        }


@dataclass(frozen=True)
class ChecklistItem:
    """日终检查清单项。

    Attributes:
        name: 检查项名称
        status: PASS / WARNING / FAIL
        detail: 说明
    """

    name: str
    status: CheckStatus
    detail: str


@dataclass(frozen=True)
class IssueRecord:
    """问题追溯记录。

    Attributes:
        issue_id: 问题 ID
        category: 类别 (PNL_RECONCILIATION / LIMIT_BREACH / KILL_SWITCH / DATA_INTEGRITY / ATTRIBUTION_BIAS)
        severity: LOW / MEDIUM / HIGH
        description: 问题描述
        root_cause: 根因 (初始为 "待分析", 由人工/上游填充)
        correction: 修正动作 (初始为 "待定")
        status: OPEN / IN_PROGRESS / RESOLVED
    """

    issue_id: str
    category: str
    severity: IssueSeverity
    description: str
    root_cause: str = "待分析"
    correction: str = "待定"
    status: IssueStatus = IssueStatus.OPEN


@dataclass(frozen=True)
class DailyAuditReport:
    """日终审计报告。

    Attributes:
        trading_date: 交易日
        portfolio_id: 组合 ID
        pnl_reconciliation: PnL 对账结果
        attribution_bias: 归因偏差结果 (None=未提供风险分解)
        compliance_report: 合规报告
        checklist: 日终检查清单
        issues: 自动登记的问题列表
        overall_status: 整体状态 (PASS / PASS_WITH_WARNINGS / FAIL)
        timestamp: 审计时间
    """

    trading_date: date
    portfolio_id: str
    pnl_reconciliation: PnLReconciliation
    compliance_report: ComplianceReport
    checklist: list[ChecklistItem]
    issues: list[IssueRecord]
    overall_status: AuditStatus
    timestamp: datetime
    attribution_bias: AttributionBias | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "trading_date": self.trading_date.isoformat(),
            "portfolio_id": self.portfolio_id,
            "pnl_reconciliation": self.pnl_reconciliation.to_dict(),
            "attribution_bias": self.attribution_bias.to_dict() if self.attribution_bias else None,
            "compliance_report": self.compliance_report.to_dict(),
            "checklist": [
                {"name": c.name, "status": c.status.value, "detail": c.detail}
                for c in self.checklist
            ],
            "issues": [
                {
                    "issue_id": i.issue_id,
                    "category": i.category,
                    "severity": i.severity.value,
                    "description": i.description,
                    "root_cause": i.root_cause,
                    "correction": i.correction,
                    "status": i.status.value,
                }
                for i in self.issues
            ],
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class AuditRiskMetricsReport:
    """CTR-P1-011 AuditRiskMetricsReport — 产出契约 (供 D-REPORTING)。

    Attributes:
        report_id: 报告 ID
        trading_date: 交易日
        portfolio_id: 组合 ID
        total_pnl: 总 PnL
        gap_pct: 对账缺口占比
        compliance_status: 合规状态
        audit_status: 审计状态
        issues_count: 问题数量
        high_severity_count: 高严重度问题数量
        generated_at: 生成时间
    """

    report_id: str
    trading_date: date
    portfolio_id: str
    total_pnl: float
    gap_pct: float
    compliance_status: AuditStatus
    audit_status: AuditStatus
    issues_count: int
    high_severity_count: int
    generated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "trading_date": self.trading_date.isoformat(),
            "portfolio_id": self.portfolio_id,
            "total_pnl": self.total_pnl,
            "gap_pct": self.gap_pct,
            "compliance_status": self.compliance_status.value,
            "audit_status": self.audit_status.value,
            "issues_count": self.issues_count,
            "high_severity_count": self.high_severity_count,
            "generated_at": self.generated_at.isoformat(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────

#: 审计阈值 ↔ 注册表条目映射（55 号 §3.3 统读：THD-AUDIT-001/002/003）
_AUDIT_THRESHOLD_SPEC: Final[dict[str, str]] = {
    "THD-AUDIT-001": "pnl_tolerance",
    "THD-AUDIT-002": "warn_ratio",
    "THD-AUDIT-003": "bias_threshold",
}


def _load_audit_thresholds(registry_path: Path | None = None) -> dict[str, float]:
    """从告警阈值注册表加载审计三阈值（fail-closed；registry_path 为测试逃生门）。"""
    return load_alert_thresholds(_AUDIT_THRESHOLD_SPEC, registry_path=registry_path)


#: import 期 fail-closed 加载（注册表缺失/畸形 → import 即 raise，禁止码内第二真源兜底）
_AUDIT_DEFAULTS: Final[dict[str, float]] = _load_audit_thresholds()


@dataclass(frozen=True)
class AuditConfig:
    """日终审计配置。

    默认值真源=alert_threshold_registry（THD-AUDIT-001/002/003，import 期 fail-closed 加载）；
    显式传参可覆盖注册表默认（测试/特殊场景逃生门）。

    Attributes:
        pnl_tolerance: PnL 对账容差 (gap_pct 绝对值阈值), 默认 0.001 (0.1%)
        warn_ratio: 限额预警利用率阈值, 默认 0.8 (consumed/value > 0.8 → WARNING)
        bias_threshold: 归因偏差阈值, 默认 0.1 (|bias| > 0.1 → BIASED)
    """

    pnl_tolerance: float = _AUDIT_DEFAULTS["pnl_tolerance"]
    warn_ratio: float = _AUDIT_DEFAULTS["warn_ratio"]
    bias_threshold: float = _AUDIT_DEFAULTS["bias_threshold"]

    def __post_init__(self) -> None:
        if self.pnl_tolerance <= 0:
            raise InvalidAuditInputError(
                f"pnl_tolerance must be >0, got {self.pnl_tolerance}"
            )
        if not 0 < self.warn_ratio <= 1:
            raise InvalidAuditInputError(
                f"warn_ratio must be in (0,1], got {self.warn_ratio}"
            )
        if self.bias_threshold <= 0:
            raise InvalidAuditInputError(
                f"bias_threshold must be >0, got {self.bias_threshold}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 日终审计请求 (参数对象, 治本 §5.150 Long Parameter List)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AuditRequest:
    """日终审计请求参数对象——封装 audit() 的全部输入。

    Attributes:
        trading_date: 交易日
        portfolio_id: 组合 ID
        positions_prev: 上一交易日持仓快照
        positions_now: 当前持仓快照
        fills: 当日成交记录
        nav: 组合净值
        consumptions: 限额消耗列表
        decomposition: 风险归因结果 (None=不检测归因偏差)
        actual_factor_pnl: 实际因子 PnL
        actual_residual_pnl: 实际残差 PnL
        kill_switch_state: Kill Switch 状态
        data_completeness: 数据完整性
        now: 时间戳
    """

    trading_date: date
    portfolio_id: str
    positions_prev: list[AuditPositionSnapshot]
    positions_now: list[AuditPositionSnapshot]
    fills: list[FillRecord]
    nav: float
    consumptions: list[LimitConsumption]
    decomposition: DecompositionResult | None = None
    actual_factor_pnl: float = 0.0
    actual_residual_pnl: float = 0.0
    kill_switch_state: str = "CLOSED"
    data_completeness: bool = True
    now: datetime | None = None


# ──────────────────────────────────────────────────────────────────────────────
# VaR 回测综合定级报告 (36号 §3.11 集成包装层)
# ──────────────────────────────────────────────────────────────────────────────

#: run_var_backtest 最少样本数（n<30 跳过回测强制 PASS，§3.10 样本不足处理表）
VAR_BACKTEST_MIN_SAMPLES: Final = 30
#: 低检验力窗口上界（30≤n<60 仅 E-backtesting 参与定级，传统 3 法标记 low_power）
VAR_BACKTEST_LOW_POWER_SAMPLES: Final = 60


@dataclass(frozen=True)
class VarBacktestReport:
    """VaR 回测综合定级报告 (36号 §3.11, daily_auditor 集成包装层产出)。

    Attributes:
        trade_date: 交易日
        action: 综合定级 (PASS / RECALIBRATE / REBUILD, §3.10 三档响应)
        reason: 定级理由 (命中信号人类可读摘要)
        flags: 定级标记 (INSUFFICIENT_SAMPLE_SKIP / LOW_POWER_WARNING)
        n_obs: 回测观测样本数
        report: var_backtester.full_report 原始报告字典 (样本不足跳过时为 None)
    """

    trade_date: date
    action: str
    reason: str
    flags: tuple[str, ...]
    n_obs: int
    report: dict[str, Any] | None


# ──────────────────────────────────────────────────────────────────────────────
# 日终审计器
# ──────────────────────────────────────────────────────────────────────────────


class DailyAuditor:
    """日终审计器——PnL 对账 + 归因偏差 + 合规报告 + 检查清单 + 问题追溯。

    用法 (完整日终审计):
        auditor = DailyAuditor()
        report = auditor.audit(
            trading_date=date(2026, 8, 1),
            portfolio_id="PF-001",
            positions_prev=[...], positions_now=[...],
            fills=[...], nav=1_000_000.0,
            consumptions=[...],
            decomposition=decomp_result,
            actual_factor_pnl=..., actual_residual_pnl=...,
            kill_switch_state="CLOSED", data_completeness=True,
        )
        # report.overall_status → PASS / PASS_WITH_WARNINGS / FAIL

    用法 (单独 PnL 对账):
        recon = auditor.reconcile_pnl(positions_prev, positions_now, fills, nav)
    """

    def __init__(self, config: AuditConfig | None = None) -> None:
        self._config = config or AuditConfig()

    @property
    def config(self) -> AuditConfig:
        return self._config

    # ── 公开 API: PnL 对账 ──

    def reconcile_pnl(
        self,
        positions_prev: list[AuditPositionSnapshot],
        positions_now: list[AuditPositionSnapshot],
        fills: list[FillRecord],
        nav: float,
        now: datetime | None = None,
    ) -> PnLReconciliation:
        """日终 PnL 对账。

        Args:
            positions_prev: 前一日持仓快照 (提供 prev_close)
            positions_now: 当日持仓快照 (提供 close/avg_entry)
            fills: 当日成交记录
            nav: 组合净值 (用于计算 gap_pct)
            now: 时间戳

        Returns:
            PnLReconciliation

        Raises:
            InvalidAuditInputError: 持仓数据含 NaN / nav 为 NaN
        """
        self._validate_positions(positions_prev, "positions_prev")
        self._validate_positions(positions_now, "positions_now")
        if math.isnan(nav):
            raise InvalidAuditInputError("nav must not be NaN")
        now = now or datetime.now(timezone.utc)

        # 前收盘价查找表 (symbol → prev_close), 缺失则用 avg_entry
        prev_close_map: dict[str, float] = {
            p.symbol: p.close_price for p in positions_prev
        }

        # ── 资产负债表恒等式 (gross) ──
        # MV_prev = Σ qty_prev × close_prev ; MV_now = Σ qty_now × close
        mv_prev = sum(p.qty * p.close_price for p in positions_prev)
        mv_now = sum(p.qty * p.close_price for p in positions_now)
        # 交易现金流 (买入 qty>0 → cash out; 卖出 qty<0 → cash in)
        trade_cash = sum(f.qty * f.price for f in fills)
        total_cost = sum(f.cost for f in fills)
        # 预期 PnL = 市值变动 − 净交易投入 (成本单列, 不参与 gap)
        expected = (mv_now - mv_prev) - trade_cash

        # 已实现 PnL (gross, 不含成本)
        realized = sum(f.realized_pnl for f in fills)

        # 未实现 PnL (当日, prev_close → close; 新持仓 prev_close=avg_entry)
        unrealized = 0.0
        for p in positions_now:
            pc = prev_close_map.get(p.symbol, p.avg_entry_price)
            unrealized += p.qty * (p.close_price - pc)

        total_pnl = realized + unrealized
        gap = expected - total_pnl
        gap_pct = gap / abs(nav) if abs(nav) > 0 else 0.0
        status = (
            ReconciliationStatus.MATCH
            if abs(gap_pct) <= self._config.pnl_tolerance
            else ReconciliationStatus.MISMATCH
        )

        return PnLReconciliation(
            expected_pnl=expected,
            realized_pnl=realized,
            unrealized_pnl=unrealized,
            total_pnl=total_pnl,
            gap=gap,
            gap_pct=gap_pct,
            status=status,
            total_cost=total_cost,
        )

    # ── 公开 API: 归因偏差检测 ──

    def detect_attribution_bias(
        self,
        decomposition: DecompositionResult | None,
        actual_factor_pnl: float,
        actual_residual_pnl: float,
        now: datetime | None = None,
    ) -> AttributionBias:
        """归因偏差检测 (复用 RK-16 风险分解)。

        Args:
            decomposition: RK-16 风险分解结果 (None=无因子模型, 返回 NOT_APPLICABLE)
            actual_factor_pnl: 实际因子 PnL
            actual_residual_pnl: 实际残差 PnL
            now: 时间戳

        Returns:
            AttributionBias
        """
        now = now or datetime.now(timezone.utc)

        # 无因子模型 → 无法判定
        if decomposition is None or decomposition.factor_contribution_pct is None:
            return AttributionBias(
                predicted_factor_pct=None,
                actual_factor_pct=0.0,
                bias=0.0,
                status=AttributionStatus.NOT_APPLICABLE,
            )

        predicted = decomposition.factor_contribution_pct
        denom = abs(actual_factor_pnl) + abs(actual_residual_pnl)
        if denom <= 0:
            # 实际 PnL 全为 0 → 占比无意义, 偏差视为 0
            actual_pct = 0.0
            bias = 0.0
            status = AttributionStatus.ALIGNED
        else:
            actual_pct = actual_factor_pnl / denom
            bias = predicted - actual_pct
            status = (
                AttributionStatus.BIASED
                if abs(bias) > self._config.bias_threshold
                else AttributionStatus.ALIGNED
            )

        return AttributionBias(
            predicted_factor_pct=predicted,
            actual_factor_pct=actual_pct,
            bias=bias,
            status=status,
        )

    # ── 公开 API: 合规检查 ──

    def run_compliance_check(
        self,
        consumptions: list[LimitConsumption],
        now: datetime | None = None,
    ) -> ComplianceReport:
        """合规报告——逐项限额检查。

        Args:
            consumptions: 限额消耗列表 (来自 RK-06)
            now: 时间戳

        Returns:
            ComplianceReport
        """
        self._validate_consumptions(consumptions)
        now = now or datetime.now(timezone.utc)

        checks: list[ComplianceCheck] = []
        for c in consumptions:
            checks.append(self._check_single_limit(c))

        has_breached = any(ch.status == CheckStatus.BREACHED for ch in checks)
        has_warning = any(ch.status == CheckStatus.WARNING for ch in checks)
        if has_breached:
            overall = AuditStatus.FAIL
        elif has_warning:
            overall = AuditStatus.PASS_WITH_WARNINGS
        else:
            overall = AuditStatus.PASS

        return ComplianceReport(checks=checks, overall_status=overall)

    # ── 公开 API: 日终检查清单 ──

    def run_daily_checklist(
        self,
        positions_prev: list[AuditPositionSnapshot],
        positions_now: list[AuditPositionSnapshot],
        pnl_reconciliation: PnLReconciliation,
        compliance_report: ComplianceReport,
        kill_switch_state: str,
        data_completeness: bool,
        now: datetime | None = None,
    ) -> list[ChecklistItem]:
        """日终检查清单 (5 项必查)。

        1. 持仓对账: 持仓数据完整性 (无 NaN)
        2. PnL 对账: 缺口在容差内
        3. 限额合规: 无 BREACHED
        4. Kill Switch: 终态 CLOSED
        5. 数据完整性: 行情/成交数据无缺失
        """
        now = now or datetime.now(timezone.utc)
        items: list[ChecklistItem] = []

        # 1. 持仓对账
        invalid = self._count_invalid_positions(positions_now)
        if invalid == 0:
            items.append(
                ChecklistItem(
                    name="持仓对账",
                    status=CheckStatus.PASS,
                    detail=f"{len(positions_now)} 个持仓, 数据完整",
                )
            )
        else:
            items.append(
                ChecklistItem(
                    name="持仓对账",
                    status=CheckStatus.FAIL,
                    detail=f"{invalid} 个持仓含非法值 (NaN/缺失)",
                )
            )

        # 2. PnL 对账
        if pnl_reconciliation.status == ReconciliationStatus.MATCH:
            items.append(
                ChecklistItem(
                    name="PnL对账",
                    status=CheckStatus.PASS,
                    detail=f"缺口 {pnl_reconciliation.gap_pct:.4%} 在容差内",
                )
            )
        else:
            items.append(
                ChecklistItem(
                    name="PnL对账",
                    status=CheckStatus.FAIL,
                    detail=f"缺口 {pnl_reconciliation.gap_pct:.4%} 超容差 "
                    f"(gap={pnl_reconciliation.gap:.2f})",
                )
            )

        # 3. 限额合规
        if compliance_report.overall_status == AuditStatus.FAIL:
            breached = [
                c.limit_type
                for c in compliance_report.checks
                if c.status == CheckStatus.BREACHED
            ]
            items.append(
                ChecklistItem(
                    name="限额合规",
                    status=CheckStatus.FAIL,
                    detail=f"{len(breached)} 项限额突破: {breached}",
                )
            )
        elif compliance_report.overall_status == AuditStatus.PASS_WITH_WARNINGS:
            items.append(
                ChecklistItem(
                    name="限额合规",
                    status=CheckStatus.WARNING,
                    detail="存在预警级限额消耗",
                )
            )
        else:
            items.append(
                ChecklistItem(
                    name="限额合规",
                    status=CheckStatus.PASS,
                    detail="所有限额在范围内",
                )
            )

        # 4. Kill Switch 状态
        ks = kill_switch_state.upper()
        if ks == "CLOSED":
            items.append(
                ChecklistItem(
                    name="Kill Switch状态",
                    status=CheckStatus.PASS,
                    detail="Kill Switch 终态 CLOSED",
                )
            )
        else:
            items.append(
                ChecklistItem(
                    name="Kill Switch状态",
                    status=CheckStatus.FAIL,
                    detail=f"Kill Switch 非 CLOSED (当前={kill_switch_state})",
                )
            )

        # 5. 数据完整性
        if data_completeness:
            items.append(
                ChecklistItem(
                    name="数据完整性",
                    status=CheckStatus.PASS,
                    detail="行情/成交数据完整",
                )
            )
        else:
            items.append(
                ChecklistItem(
                    name="数据完整性",
                    status=CheckStatus.FAIL,
                    detail="行情/成交数据存在缺失",
                )
            )

        return items

    # ── 公开 API: 完整日终审计 ──

    def audit(self, request: AuditRequest) -> DailyAuditReport:
        """完整日终审计——对账 + 归因 + 合规 + 清单 + 问题追溯。

        幂等: 同一 (trading_date, portfolio_id) + 相同输入产生等价报告。

        Args:
            request: 审计请求参数对象 (AuditRequest)
        """
        now = request.now or datetime.now(timezone.utc)

        pnl_recon = self.reconcile_pnl(
            request.positions_prev, request.positions_now, request.fills, request.nav, now
        )
        attribution = self.detect_attribution_bias(
            request.decomposition, request.actual_factor_pnl, request.actual_residual_pnl, now
        )
        compliance = self.run_compliance_check(request.consumptions, now)
        checklist = self.run_daily_checklist(
            request.positions_prev,
            request.positions_now,
            pnl_recon,
            compliance,
            request.kill_switch_state,
            request.data_completeness,
            now,
        )
        issues = self._collect_issues(
            pnl_recon, attribution, compliance, request.kill_switch_state, request.data_completeness
        )

        overall = self._aggregate_status(checklist)

        logger.info(
            "Daily audit: portfolio=%s date=%s status=%s pnl=%.2f gap=%.4f issues=%d",
            request.portfolio_id,
            request.trading_date.isoformat(),
            overall.value,
            pnl_recon.total_pnl,
            pnl_recon.gap_pct,
            len(issues),
        )

        return DailyAuditReport(
            trading_date=request.trading_date,
            portfolio_id=request.portfolio_id,
            pnl_reconciliation=pnl_recon,
            attribution_bias=attribution,
            compliance_report=compliance,
            checklist=checklist,
            issues=issues,
            overall_status=overall,
            timestamp=now,
        )

    # ── 公开 API: AuditRiskMetricsReport ──

    def generate_risk_metrics_report(
        self,
        audit_report: DailyAuditReport,
        now: datetime | None = None,
    ) -> AuditRiskMetricsReport:
        """生成 CTR-P1-011 AuditRiskMetricsReport (供 D-REPORTING)。"""
        now = now or datetime.now(timezone.utc)
        report_id = (
            f"RMR-{audit_report.portfolio_id}-{audit_report.trading_date.isoformat()}"
        )
        high_count = sum(
            1 for i in audit_report.issues if i.severity == IssueSeverity.HIGH
        )
        return AuditRiskMetricsReport(
            report_id=report_id,
            trading_date=audit_report.trading_date,
            portfolio_id=audit_report.portfolio_id,
            total_pnl=audit_report.pnl_reconciliation.total_pnl,
            gap_pct=audit_report.pnl_reconciliation.gap_pct,
            compliance_status=audit_report.compliance_report.overall_status,
            audit_status=audit_report.overall_status,
            issues_count=len(audit_report.issues),
            high_severity_count=high_count,
            generated_at=now,
        )

    # ── 公开 API: VaR 回测综合定级 (36号 §3.11 集成包装层) ──

    def run_var_backtest(
        self,
        trade_date: date,
        observations: list[BacktestObservation],
        backtester: VarBacktester | None = None,
    ) -> VarBacktestReport:
        """VaR/ES 回测综合定级 (36号 §3.11, 对齐 §3.10 三档矩阵)。

        包装 var_backtester.full_report → PASS/RECALIBRATE/REBUILD:
        - n < 30: 跳过回测, 强制 PASS + INSUFFICIENT_SAMPLE_SKIP (§3.10 样本不足表)
        - 30 ≤ n < 60: 仅 E-backtesting 参与定级 + LOW_POWER_WARNING
          (传统 3 法小样本检验力不足假阳性高, 标记 low_power 不参与 reject 判定)
        - n ≥ 60: 全 4 法 + Basel 交通灯参与定级

        定级矩阵 (§3.10 触发→动作映射对齐解读; §3.11 "overall_reject→REBUILD"
        按 §3.10 矩阵吸收——单信号 reject 一律 RECALIBRATE, REBUILD 由
        Basel red / E-backtesting black 严重信号承载):
        - REBUILD: basel_zone=="red" 或 ebt_alert=="black"
        - RECALIBRATE: basel_zone=="yellow" 或 kupiec/christoffersen/z2 reject
          或 ebt_alert ∈ (yellow, red)
        - 否则 PASS

        校准动作执行 (RiskLayerOrchestrator.apply_var_backtest_action) 与
        log_recalibration 审计留痕由调用方按 §3.10 D1 时序串联
        (动作执行后立即补记), 本方法只产定级。
        """
        n_obs = len(observations)
        if n_obs < VAR_BACKTEST_MIN_SAMPLES:
            return VarBacktestReport(
                trade_date=trade_date,
                action="PASS",
                reason=(
                    f"样本 {n_obs} < {VAR_BACKTEST_MIN_SAMPLES}, 跳过回测强制 PASS "
                    f"(min_history 下限, 回测无统计意义)"
                ),
                flags=("INSUFFICIENT_SAMPLE_SKIP",),
                n_obs=n_obs,
                report=None,
            )
        bt = backtester or VarBacktester()
        report = bt.full_report(observations)
        low_power = n_obs < VAR_BACKTEST_LOW_POWER_SAMPLES
        action, reason = self._grade_var_backtest(report, low_power=low_power)
        flags = ("LOW_POWER_WARNING",) if low_power else ()
        logger.info(
            "VAR_BACKTEST date=%s action=%s n_obs=%d flags=%s reason=%s",
            trade_date.isoformat(),
            action,
            n_obs,
            flags,
            reason,
        )
        return VarBacktestReport(
            trade_date=trade_date,
            action=action,
            reason=reason,
            flags=flags,
            n_obs=n_obs,
            report=report,
        )

    @staticmethod
    def _grade_var_backtest(report: dict[str, Any], *, low_power: bool) -> tuple[str, str]:
        """full_report 字典 → (action, reason)。单项 error/缺失按不拒绝处理。"""
        basel = report.get("basel_traffic_light") or {}
        ebt = report.get("e_backtesting") or {}
        basel_zone = basel.get("zone")
        ebt_alert = ebt.get("alert_level")

        if low_power:
            # §3.10 样本不足表: 30≤n<60 仅 E-backtesting (anytime-valid 小样本友好) 参与定级
            if ebt_alert == "black":
                return "REBUILD", "low_power: E-backtesting black (决定性证据)"
            if ebt_alert in ("yellow", "red"):
                return "RECALIBRATE", f"low_power: E-backtesting {ebt_alert}"
            return "PASS", "low_power: 仅 E-backtesting 参与定级, 未触发告警"

        def _reject(key: str) -> bool:
            sub = report.get(key) or {}
            return bool(sub.get("reject", False))

        if basel_zone == "red" or ebt_alert == "black":
            return "REBUILD", f"严重信号: basel_zone={basel_zone} ebt_alert={ebt_alert}"
        hits: list[str] = []
        if basel_zone == "yellow":
            hits.append("basel_yellow")
        if _reject("kupiec_pof"):
            hits.append("kupiec_reject")
        if _reject("christoffersen"):
            hits.append("christoffersen_reject")
        if _reject("acerbi_szekely_z2"):
            hits.append("z2_reject")
        if ebt_alert in ("yellow", "red"):
            hits.append(f"ebt_{ebt_alert}")
        if hits:
            return "RECALIBRATE", "校准信号: " + ",".join(hits)
        return "PASS", "全 4 法 + Basel 未触发拒绝"

    # ── 公开 API: clean/dirty P&L 双轨 (36号 §3.13) ──

    def compute_clean_pnl(
        self,
        positions_prev: list[AuditPositionSnapshot],
        positions_now: list[AuditPositionSnapshot],
        fills: list[FillRecord],
        *,
        new_position_symbols: frozenset[str] | set[str] | None = None,
    ) -> float:
        """clean P&L (§3.13): 可平仓头寸已实现 + 未实现 MtM, 不含交易成本/融资/分红。

        T+1 口径 (§3.13 T+1 表): new_position_symbols (当日新建仓标的) 的未实现
        MtM 全部剔除——锁仓风险非可交易风险, 不纳入 VaR 回测; 不可平仓头寸当日
        不可卖出无已实现, fills 已实现盈亏天然全属可平仓头寸。
        MVP 近似: 标的级判定 (同日同标的旧仓+新仓混持时不拆 lot 级)。
        持久化: backtest_store.save_pnl_dual (§3.18 阶段 4)。
        """
        recon = self.reconcile_pnl(positions_prev, positions_now, fills, nav=1.0)
        locked_mtm = 0.0
        if new_position_symbols:
            for p in positions_now:
                if p.symbol in new_position_symbols:
                    # 当日新建仓: prev_close 缺省回退 avg_entry, MtM = qty×(close−entry)
                    locked_mtm += p.qty * (p.close_price - p.avg_entry_price)
        return recon.total_pnl - locked_mtm

    def compute_dirty_pnl(
        self,
        positions_prev: list[AuditPositionSnapshot],
        positions_now: list[AuditPositionSnapshot],
        fills: list[FillRecord],
    ) -> float:
        """dirty P&L (§3.13): 全部头寸已实现 + 未实现 MtM − 交易成本 (实际盈亏口径)。

        成本口径: FillRecord.cost 为费用正数 (佣金+滑点), 从 gross P&L 扣减;
        融资成本/分红未建模 (MVP 范围外, 后续扩 FillRecord 字段)。
        """
        recon = self.reconcile_pnl(positions_prev, positions_now, fills, nav=1.0)
        return recon.total_pnl - recon.total_cost

    # ── 公开 API: VaR 审计日志 (36号 §3.11 跨文档契约, 35号 §3.15/§3.17) ──

    @staticmethod
    def _var_audit_record(event: str, trade_date: date, **fields: Any) -> dict[str, Any]:
        rec = {
            "event": event,
            "trade_date": trade_date.isoformat(),
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }
        rec.update(fields)
        return rec

    def log_entry_var(
        self,
        trade_date: date,
        entry_var: float,
        *,
        entry_es: float | None = None,
    ) -> dict[str, Any]:
        """记录入场 VaR 快照 (§3.4 入场基准; 35号 §3.11 持久化契约配套审计)。

        持久化由 backtest_store.save_entry_var 承载 (§3.18 阶段 4b),
        本方法只产审计日志记录。
        """
        rec = self._var_audit_record(
            "entry_var", trade_date, entry_var=entry_var, entry_es=entry_es
        )
        logger.info(
            "VAR_AUDIT entry_var date=%s entry_var=%.6f entry_es=%s",
            trade_date.isoformat(),
            entry_var,
            entry_es,
        )
        return rec

    def log_baseline(self, trade_date: date, var_95: float, es_95: float) -> dict[str, Any]:
        """记录当日 VaR/ES 基线 (供次日回撤归因对比 + §3.12 盘中重算对比)。"""
        rec = self._var_audit_record("baseline", trade_date, var_95=var_95, es_95=es_95)
        logger.info(
            "VAR_AUDIT baseline date=%s var_95=%.6f es_95=%.6f",
            trade_date.isoformat(),
            var_95,
            es_95,
        )
        return rec

    def log_recalibration(self, trade_date: date, action: str, reason: str) -> dict[str, Any]:
        """记录校准/重构事件 (§3.10 D1 审计追溯)。

        action ∈ RECALIBRATE / REBUILD / RECOVERED_FROM_REBUILD:
        - REBUILD → CRITICAL (模型不可用, 人工审查)
        - RECALIBRATE → WARNING
        - 其他 (含 RECOVERED_FROM_REBUILD) → INFO
        """
        action_norm = action.upper()
        rec = self._var_audit_record(
            "recalibration", trade_date, action=action_norm, reason=reason
        )
        if action_norm == "REBUILD":
            logger.critical(
                "VAR_AUDIT recalibration date=%s action=REBUILD reason=%s",
                trade_date.isoformat(),
                reason,
            )
        elif action_norm == "RECALIBRATE":
            logger.warning(
                "VAR_AUDIT recalibration date=%s action=RECALIBRATE reason=%s",
                trade_date.isoformat(),
                reason,
            )
        else:
            logger.info(
                "VAR_AUDIT recalibration date=%s action=%s reason=%s",
                trade_date.isoformat(),
                action_norm,
                reason,
            )
        return rec


    # ── 内部: 单项限额检查 ──

    def _check_single_limit(self, c: LimitConsumption) -> ComplianceCheck:
        """检查单项限额: BREACHED (consumed>value) / WARNING (>warn_ratio) / OK。"""
        if c.value <= 0:
            # 无限额配置: consumed>0 视为突破 (不应有消耗)
            if c.consumed > 0:
                return ComplianceCheck(
                    limit_type=c.limit_type,
                    value=c.value,
                    consumed=c.consumed,
                    utilization=math.inf,
                    status=CheckStatus.BREACHED,
                    message=f"{c.limit_type}: 无限额(value=0) 但有消耗 {c.consumed}",
                )
            return ComplianceCheck(
                limit_type=c.limit_type,
                value=c.value,
                consumed=c.consumed,
                utilization=0.0,
                status=CheckStatus.OK,
                message=f"{c.limit_type}: 无限额配置",
            )

        utilization = c.consumed / c.value
        if utilization > 1.0:
            return ComplianceCheck(
                limit_type=c.limit_type,
                value=c.value,
                consumed=c.consumed,
                utilization=utilization,
                status=CheckStatus.BREACHED,
                message=f"{c.limit_type}: 消耗 {c.consumed} 超限额 {c.value}",
            )
        if utilization > self._config.warn_ratio:
            return ComplianceCheck(
                limit_type=c.limit_type,
                value=c.value,
                consumed=c.consumed,
                utilization=utilization,
                status=CheckStatus.WARNING,
                message=f"{c.limit_type}: 利用率 {utilization:.1%} 超预警",
            )
        return ComplianceCheck(
            limit_type=c.limit_type,
            value=c.value,
            consumed=c.consumed,
            utilization=utilization,
            status=CheckStatus.OK,
            message=f"{c.limit_type}: 利用率 {utilization:.1%}",
        )

    # ── 内部: 问题收集 ──

    def _collect_issues(
        self,
        pnl_recon: PnLReconciliation,
        attribution: AttributionBias,
        compliance: ComplianceReport,
        kill_switch_state: str,
        data_completeness: bool,
    ) -> list[IssueRecord]:
        """从失败项自动登记问题 (根因/修正待人工填充)。"""
        issues: list[IssueRecord] = []
        seq = 0

        def _next_id() -> str:
            nonlocal seq
            seq += 1
            return f"ISS-{seq:03d}"

        if pnl_recon.status == ReconciliationStatus.MISMATCH:
            issues.append(
                IssueRecord(
                    issue_id=_next_id(),
                    category="PNL_RECONCILIATION",
                    severity=IssueSeverity.HIGH,
                    description=(
                        f"PnL 对账缺口 {pnl_recon.gap_pct:.4%} "
                        f"(gap={pnl_recon.gap:.2f}) 超容差"
                    ),
                )
            )

        if attribution.status == AttributionStatus.BIASED:
            issues.append(
                IssueRecord(
                    issue_id=_next_id(),
                    category="ATTRIBUTION_BIAS",
                    severity=IssueSeverity.MEDIUM,
                    description=(
                        f"归因偏差 {attribution.bias:.4f} 超阈值 "
                        f"(预测因子占比={attribution.predicted_factor_pct:.3f}, "
                        f"实际={attribution.actual_factor_pct:.3f})"
                    ),
                )
            )

        for ch in compliance.checks:
            if ch.status == CheckStatus.BREACHED:
                issues.append(
                    IssueRecord(
                        issue_id=_next_id(),
                        category="LIMIT_BREACH",
                        severity=IssueSeverity.HIGH,
                        description=ch.message,
                    )
                )

        if kill_switch_state.upper() != "CLOSED":
            issues.append(
                IssueRecord(
                    issue_id=_next_id(),
                    category="KILL_SWITCH",
                    severity=IssueSeverity.MEDIUM,
                    description=f"Kill Switch 非 CLOSED (当前={kill_switch_state})",
                )
            )

        if not data_completeness:
            issues.append(
                IssueRecord(
                    issue_id=_next_id(),
                    category="DATA_INTEGRITY",
                    severity=IssueSeverity.HIGH,
                    description="行情/成交数据存在缺失",
                )
            )

        return issues

    # ── 内部: 状态聚合 ──

    @staticmethod
    def _aggregate_status(checklist: list[ChecklistItem]) -> AuditStatus:
        """聚合检查清单状态: 任一 FAIL→FAIL; 有 WARNING 无 FAIL→PASS_WITH_WARNINGS; 全 PASS→PASS。"""
        if any(c.status == CheckStatus.FAIL for c in checklist):
            return AuditStatus.FAIL
        if any(c.status == CheckStatus.WARNING for c in checklist):
            return AuditStatus.PASS_WITH_WARNINGS
        return AuditStatus.PASS

    # ── 内部: 校验 ──

    @staticmethod
    def _validate_positions(positions: list[AuditPositionSnapshot], label: str) -> None:
        """校验持仓快照: 拒绝 NaN 数值。"""
        for p in positions:
            for field_name in ("qty", "avg_entry_price", "close_price"):
                v = getattr(p, field_name)
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    raise InvalidAuditInputError(
                        f"{label}: 持仓字段必须为有效数值",
                        details={"symbol": p.symbol, "field": field_name, "value": v},
                    )

    @staticmethod
    def _count_invalid_positions(positions: list[AuditPositionSnapshot]) -> int:
        """统计含非法值的持仓数 (宽松, 不抛异常)。"""
        count = 0
        for p in positions:
            for field_name in ("qty", "avg_entry_price", "close_price"):
                v = getattr(p, field_name)
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    count += 1
                    break
        return count

    @staticmethod
    def _validate_consumptions(consumptions: list[LimitConsumption]) -> None:
        """校验限额消耗: 拒绝 NaN / 负消耗。"""
        for c in consumptions:
            if math.isnan(c.value) or math.isnan(c.consumed):
                raise InvalidAuditInputError(
                    f"limit {c.limit_type}: value/consumed 禁止 NaN"
                )
            if c.consumed < 0:
                raise InvalidAuditInputError(
                    f"limit {c.limit_type}: consumed 禁止负值, got {c.consumed}"
                )
