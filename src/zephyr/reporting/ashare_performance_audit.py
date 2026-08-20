# [BLUEPRINT] MOD-RPT-026 | docs/03_modules/_domain_reporting/ashare_performance_audit/blueprint.md
# [MODULE] zephyr.reporting.ashare_performance_audit
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.contracts.performance_attribution_report
# [CONSUMERS] zephyr.reporting
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 5类审计(收益率/回撤/风险调整/归因一致性/交易成本); data_hash=SHA-256(canonical_json(content)); 阈值封装AuditThresholds; 纯建议不自动执行; 纯消费层不发布事件(D-RPT-D01)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAuditInputError(ZA-RPT-0026)
# [TESTS] tests/reporting/test_ashare_performance_audit.py
# [A_module] module_id=MOD-RPT-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_REPORTING — A-Share Performance Audit & Optimization Trigger

A股绩效审计与优化触发器——消费归因结果(CTR-P1-009) + 绩效指标, 执行 5 类审计规则,
自动触发优化建议。

5 类审计规则:
  - 收益率审计: return_pct vs 阈值
  - 回撤审计: max_drawdown vs 阈值
  - 风险调整收益审计: sharpe_ratio / sortino_ratio vs 阈值
  - 归因一致性校验: allocation+selection+interaction ≈ total_return
  - 交易成本审计: transaction_cost_drag vs expected_cost 比例

优化建议: 基于审计发现自动生成, 纯建议输出不自动执行。

属 A 类基础设施(确定性审计 + 规则触发), 纯消费层不发布事件。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.2 D-REPORTING-26, §2.1
蓝图: docs/03_modules/_domain_reporting/ashare_performance_audit/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 绩效指标 performance_metrics dict
#   fields: return_pct / max_drawdown / sharpe_ratio / sortino_ratio
#   code: performance_metrics（audit() 参数）
# - id: I2
#   name: 归因结果 attribution_result dict（CTR-P1-009）
#   fields: total_return / allocation_effect / selection_effect / interaction_effect / transaction_cost_drag
#   code: attribution_result（audit() 参数）
# - id: I3
#   name: 预期交易成本 expected_cost float
#   fields: 预期成本（可选，提供时才执行成本审计）
#   code: expected_cost
# - id: I4
#   name: 审计阈值配置 AuditThresholds
#   fields: 收益率-1%/-5%、回撤-10%/-15%、Sharpe 0/0.5、归因容忍0.1%、成本比1.5x/2.0x
#   code: AuditThresholds（L102 frozen dataclass）
# 层: 算法
# - id: A1
#   name_zh: ① 收益率审计
#   name_en: ASharePerformanceAuditor._audit_return
#   intro: 拿 return_pct 对照 -1% 警告 / -5% 临界阈值定严重度
#   desc: return_pct<critical→CRITICAL，<warning→WARNING，否则无发现；缺指标安静跳过
#   inputs: I1 I4
#   outputs: 收益率 AuditFinding 列表
# - id: A2
#   name_zh: ② 回撤审计
#   name_en: ASharePerformanceAuditor._audit_drawdown
#   intro: 拿 max_drawdown 对照 -10% 警告 / -15% 临界阈值定严重度
#   desc: max_drawdown<critical→CRITICAL，<warning→WARNING
#   inputs: I1 I4
#   outputs: 回撤 AuditFinding 列表
# - id: A3
#   name_zh: ③ 风险调整收益审计
#   name_en: ASharePerformanceAuditor._audit_risk_adjusted
#   intro: 检查 Sharpe<0 警告 / <0.5 提示，Sortino<0 警告
#   desc: sharpe_ratio 与 sortino_ratio 分别对照 sharpe_warning/sharpe_info/sortino_warning
#   inputs: I1 I4
#   outputs: 风险调整 AuditFinding 列表
# - id: A4
#   name_zh: ④ 归因一致性校验
#   name_en: ASharePerformanceAuditor._audit_attribution
#   intro: 校验 allocation+selection+interaction 是否约等于 total_return
#   desc: diff=|allocation+selection+interaction-total_return|，diff>0.1%容忍→WARNING
#   inputs: I2 I4
#   outputs: 归因一致性 AuditFinding 列表
#   invariant: allocation+selection+interaction ≈ total_return（容忍 0.1%）
# - id: A5
#   name_zh: ⑤ 交易成本审计
#   name_en: ASharePerformanceAuditor._audit_cost
#   intro: 实际成本拖累与预期成本的比值超 1.5x/2.0x 触发警告/临界
#   desc: cost_ratio=|transaction_cost_drag|/expected_cost；>2.0→CRITICAL，>1.5→WARNING；expected_cost 缺失或≤0 跳过
#   inputs: I2 I3 I4
#   outputs: 成本 AuditFinding 列表
# - id: A6
#   name_zh: ⑥ 优化建议触发（_TRIGGER_MAP 规则映射）
#   name_en: _build_recommendation
#   intro: 按（审计类别,严重度）查映射表生成策略调整/风控收紧/成本控制等纯建议
#   desc: (category,severity)→(recommendation_type,priority)，target_module 经 _TARGET_MODULE_MAP 映射到 D_PF_CORE/D_RISK/D_POSITION/D_EX_CORE；无映射返回 None
#   inputs: A1 A2 A3 A4 A5
#   outputs: OptimizationRecommendation 列表
#   invariant: 纯建议输出不自动执行
# - id: A7
#   name_zh: ⑦ 审计报告组装与完整性指纹
#   name_en: ASharePerformanceAuditor.audit/_compute_data_hash/validate_report
#   intro: 汇总发现与建议生成不可变报告，用 SHA-256 指纹防篡改
#   desc: content={绩效摘要,归因摘要,findings,recommendations}→data_hash=SHA-256(canonical_json)；validate_report 重算哈希比对验真
#   inputs: A6
#   outputs: PerformanceAuditReport
#   invariant: data_hash=SHA-256(canonical_json(content))；纯消费层不发布事件(D-RPT-D01)
# 层: 输出
# - id: O1
#   name_zh: A股绩效审计报告
#   name_en: PerformanceAuditReport
#   intro: 含 5 类审计发现、优化建议与 SHA-256 完整性指纹的不可变审计报告
#   invariant: 5类审计(收益率/回撤/风险调整/归因一致性/交易成本)
#   downstream: zephyr.reporting（报告域内部消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A4
# I2 --> A5
# I3 --> A5
# I4 --> A1
# I4 --> A2
# I4 --> A3
# I4 --> A4
# I4 --> A5
# A1 --> A6
# A2 --> A6
# A3 --> A6
# A4 --> A6
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"


class InvalidAuditInputError(ZephyrBaseError):
    """绩效审计输入非法——缺必填字段/类型错/值为空。"""

    error_code = "ZA-RPT-0026"


# ── 枚举 ──


class AuditCategory(str, Enum):
    """审计类别——5类审计规则。"""

    RETURN = "return"
    DRAWDOWN = "drawdown"
    RISK_ADJUSTED = "risk_adjusted"
    ATTRIBUTION = "attribution"
    COST = "cost"


class AuditSeverity(str, Enum):
    """审计严重度——3级。"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class RecommendationType(str, Enum):
    """优化建议类型——5种。"""

    STRATEGY_ADJUST = "strategy_adjust"
    RISK_TIGHTEN = "risk_tighten"
    POSITION_ADJUST = "position_adjust"
    PARAM_OPTIMIZE = "param_optimize"
    COST_CONTROL = "cost_control"


class RecommendationPriority(str, Enum):
    """优化建议优先级——3级。"""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ── 审计阈值 (C 类可调参数) ──


@dataclass(frozen=True)
class AuditThresholds:
    """审计阈值——全部可调参数, 非硬编码。"""

    # 收益率
    return_warning: float = -0.01  # -1%
    return_critical: float = -0.05  # -5%
    # 回撤
    drawdown_warning: float = -0.10  # -10%
    drawdown_critical: float = -0.15  # -15%
    # 风险调整
    sharpe_warning: float = 0.0
    sharpe_info: float = 0.5
    sortino_warning: float = 0.0
    # 归因一致性（误差容忍）
    attribution_tolerance: float = 0.001  # 0.1%
    # 交易成本
    cost_warning_ratio: float = 1.5  # 实际/预期 > 1.5
    cost_critical_ratio: float = 2.0  # 实际/预期 > 2.0


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class AuditFinding:
    """审计发现——单条审计结果。"""

    finding_id: str
    category: AuditCategory
    severity: AuditSeverity
    metric_name: str
    actual_value: float
    threshold: float
    description: str


@dataclass(frozen=True)
class OptimizationRecommendation:
    """优化建议——基于审计发现自动生成。"""

    recommendation_id: str
    finding_id: str
    type: RecommendationType
    priority: RecommendationPriority
    description: str
    target_module: str


@dataclass(frozen=True)
class PerformanceAuditReport:
    """绩效审计报告——含发现+建议+完整性指纹的不可变记录。

    data_hash = SHA-256(canonical_json(content)), 用于防篡改校验。
    """

    report_id: str
    portfolio_id: str
    audit_period: str
    generated_at: datetime
    performance_summary: dict
    attribution_summary: dict
    findings: list[dict]
    recommendations: list[dict]
    data_hash: str
    schema_version: str = _SCHEMA_VERSION


# ── 哈希工具 ──


def _canonical_json(content: dict) -> str:
    """规范 JSON 序列化（sort_keys 确保确定性）。"""
    return json.dumps(content, sort_keys=True, ensure_ascii=False, default=str)


def _compute_data_hash(content: dict) -> str:
    """计算内容指纹——SHA-256(canonical_json(content))。"""
    return hashlib.sha256(_canonical_json(content).encode("utf-8")).hexdigest()


def _require(value: object, field_name: str) -> object:
    """提取必填字段, 缺失或空抛异常。"""
    if value is None:
        raise InvalidAuditInputError(
            f"缺少必填字段: {field_name}",
            details={"missing_field": field_name},
        )
    if isinstance(value, str) and not value.strip():
        raise InvalidAuditInputError(
            f"字段 {field_name} 不能为空",
            details={"field": field_name},
        )
    if isinstance(value, (list, dict)) and len(value) == 0:
        raise InvalidAuditInputError(
            f"字段 {field_name} 不能为空列表/字典",
            details={"field": field_name},
        )
    return value


def _get_float(data: dict, key: str, default: float | None = None) -> float:
    """安全提取 float 字段, 缺失返回 default (None 则抛异常)。"""
    val = data.get(key, default)
    if val is None:
        raise InvalidAuditInputError(
            f"缺少必填指标: {key}",
            details={"missing_metric": key},
        )
    try:
        return float(val)
    except (TypeError, ValueError) as e:
        raise InvalidAuditInputError(
            f"指标 {key} 不是合法数值: {val!r}",
            details={"field": key, "value": str(val)},
        ) from e


# ── 优化建议触发规则 ──
# (category, severity) → (recommendation_type, priority)
_TRIGGER_MAP: dict[
    tuple[AuditCategory, AuditSeverity],
    tuple[RecommendationType, RecommendationPriority],
] = {
    (AuditCategory.RETURN, AuditSeverity.CRITICAL): (
        RecommendationType.STRATEGY_ADJUST,
        RecommendationPriority.HIGH,
    ),
    (AuditCategory.RETURN, AuditSeverity.WARNING): (
        RecommendationType.STRATEGY_ADJUST,
        RecommendationPriority.MEDIUM,
    ),
    (AuditCategory.DRAWDOWN, AuditSeverity.CRITICAL): (
        RecommendationType.RISK_TIGHTEN,
        RecommendationPriority.HIGH,
    ),
    (AuditCategory.DRAWDOWN, AuditSeverity.WARNING): (
        RecommendationType.RISK_TIGHTEN,
        RecommendationPriority.MEDIUM,
    ),
    (AuditCategory.COST, AuditSeverity.CRITICAL): (
        RecommendationType.COST_CONTROL,
        RecommendationPriority.HIGH,
    ),
    (AuditCategory.COST, AuditSeverity.WARNING): (
        RecommendationType.COST_CONTROL,
        RecommendationPriority.LOW,
    ),
    (AuditCategory.RISK_ADJUSTED, AuditSeverity.WARNING): (
        RecommendationType.PARAM_OPTIMIZE,
        RecommendationPriority.MEDIUM,
    ),
    (AuditCategory.RISK_ADJUSTED, AuditSeverity.INFO): (
        RecommendationType.PARAM_OPTIMIZE,
        RecommendationPriority.LOW,
    ),
    (AuditCategory.ATTRIBUTION, AuditSeverity.WARNING): (
        RecommendationType.STRATEGY_ADJUST,
        RecommendationPriority.MEDIUM,
    ),
    # NOTE: Sortino WARNING 复用 RISK_ADJUSTED WARNING 映射
}

# target_module 映射
_TARGET_MODULE_MAP: dict[RecommendationType, str] = {
    RecommendationType.STRATEGY_ADJUST: "D_PF_CORE",
    RecommendationType.RISK_TIGHTEN: "D_RISK",
    RecommendationType.POSITION_ADJUST: "D_POSITION",
    RecommendationType.PARAM_OPTIMIZE: "D_PF_CORE",
    RecommendationType.COST_CONTROL: "D_EX_CORE",
}


def _build_recommendation(finding: AuditFinding) -> OptimizationRecommendation | None:
    """基于审计发现构建优化建议, 无映射则返回 None。"""
    trigger = _TRIGGER_MAP.get((finding.category, finding.severity))
    if trigger is None:
        return None
    rec_type, priority = trigger
    return OptimizationRecommendation(
        recommendation_id=f"REC-{uuid.uuid4().hex[:10]}",
        finding_id=finding.finding_id,
        type=rec_type,
        priority=priority,
        description=(
            f"{finding.description} 建议执行 {rec_type.value} 操作"
            f" (指标 {finding.metric_name}={finding.actual_value:.4f}, "
            f"阈值={finding.threshold:.4f})"
        ),
        target_module=_TARGET_MODULE_MAP.get(rec_type, "unknown"),
    )


# ── 审计器主类 ──


class ASharePerformanceAuditor:
    """A股绩效审计器——5类审计规则 + 优化建议触发。

    纯基础设施, 无外部状态。线程安全（无共享可变状态）。
    审计规则确定性: 同输入 → 同输出。

    Usage:
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            portfolio_id="PF-001",
            audit_period="2026-Q3",
            performance_metrics={"return_pct": 0.12, "max_drawdown": -0.08,
                                 "sharpe_ratio": 1.5, "sortino_ratio": 2.0},
            attribution_result={"total_return": 0.12, "allocation_effect": 0.05,
                                "selection_effect": 0.06, "interaction_effect": 0.01,
                                "transaction_cost_drag": 0.001},
            expected_cost=0.002,
        )
        assert auditor.validate_report(report) is True
    """

    def __init__(self, thresholds: AuditThresholds | None = None) -> None:
        self._thresholds = thresholds or AuditThresholds()

    # ── 主审计方法 ──

    def audit(
        self,
        portfolio_id: str,
        audit_period: str,
        performance_metrics: dict,
        attribution_result: dict,
        expected_cost: float | None = None,
    ) -> PerformanceAuditReport:
        """执行绩效审计 + 生成优化建议。

        Args:
            portfolio_id: 账户标识。
            audit_period: 审计期 (如 "2026-Q3")。
            performance_metrics: 绩效指标, 含 return_pct/max_drawdown/
                sharpe_ratio/sortino_ratio。
            attribution_result: 归因结果, 含 total_return/allocation_effect/
                selection_effect/interaction_effect/transaction_cost_drag。
            expected_cost: 预期交易成本, 可选。提供时执行成本审计。

        Returns:
            PerformanceAuditReport: 审计报告。
        """
        _require(portfolio_id, "portfolio_id")
        _require(audit_period, "audit_period")
        _require(performance_metrics, "performance_metrics")
        _require(attribution_result, "attribution_result")

        findings: list[AuditFinding] = []
        findings.extend(self._audit_return(performance_metrics))
        findings.extend(self._audit_drawdown(performance_metrics))
        findings.extend(self._audit_risk_adjusted(performance_metrics))
        findings.extend(self._audit_attribution(attribution_result))
        findings.extend(self._audit_cost(attribution_result, expected_cost))

        recommendations: list[OptimizationRecommendation] = []
        for f in findings:
            rec = _build_recommendation(f)
            if rec is not None:
                recommendations.append(rec)

        # 构建报告内容
        performance_summary = dict(performance_metrics)
        attribution_summary = dict(attribution_result)

        findings_dicts = [
            {
                "finding_id": f.finding_id,
                "category": f.category.value,
                "severity": f.severity.value,
                "metric_name": f.metric_name,
                "actual_value": f.actual_value,
                "threshold": f.threshold,
                "description": f.description,
            }
            for f in findings
        ]
        recommendations_dicts = [
            {
                "recommendation_id": r.recommendation_id,
                "finding_id": r.finding_id,
                "type": r.type.value,
                "priority": r.priority.value,
                "description": r.description,
                "target_module": r.target_module,
            }
            for r in recommendations
        ]

        content = {
            "performance_summary": performance_summary,
            "attribution_summary": attribution_summary,
            "findings": findings_dicts,
            "recommendations": recommendations_dicts,
        }

        report = PerformanceAuditReport(
            report_id=f"AUDIT-{uuid.uuid4().hex[:10]}",
            portfolio_id=portfolio_id,
            audit_period=audit_period,
            generated_at=datetime.now(UTC),
            performance_summary=performance_summary,
            attribution_summary=attribution_summary,
            findings=findings_dicts,
            recommendations=recommendations_dicts,
            data_hash=_compute_data_hash(content),
            schema_version=_SCHEMA_VERSION,
        )

        _logger.debug(
            "audit: portfolio=%s period=%s findings=%d recommendations=%d",
            portfolio_id,
            audit_period,
            len(findings),
            len(recommendations),
        )
        return report

    # ── 5类审计规则 ──

    def _audit_return(self, metrics: dict) -> list[AuditFinding]:
        """收益率审计。"""
        findings: list[AuditFinding] = []
        try:
            return_pct = _get_float(metrics, "return_pct")
        except InvalidAuditInputError:
            return findings

        if return_pct < self._thresholds.return_critical:
            findings.append(
                self._make_finding(
                    AuditCategory.RETURN,
                    AuditSeverity.CRITICAL,
                    "return_pct",
                    return_pct,
                    self._thresholds.return_critical,
                    f"收益率 {return_pct:.2%} 低于临界阈值 {self._thresholds.return_critical:.2%}",
                )
            )
        elif return_pct < self._thresholds.return_warning:
            findings.append(
                self._make_finding(
                    AuditCategory.RETURN,
                    AuditSeverity.WARNING,
                    "return_pct",
                    return_pct,
                    self._thresholds.return_warning,
                    f"收益率 {return_pct:.2%} 低于警告阈值 {self._thresholds.return_warning:.2%}",
                )
            )
        return findings

    def _audit_drawdown(self, metrics: dict) -> list[AuditFinding]:
        """回撤审计。"""
        findings: list[AuditFinding] = []
        try:
            max_drawdown = _get_float(metrics, "max_drawdown")
        except InvalidAuditInputError:
            return findings

        if max_drawdown < self._thresholds.drawdown_critical:
            findings.append(
                self._make_finding(
                    AuditCategory.DRAWDOWN,
                    AuditSeverity.CRITICAL,
                    "max_drawdown",
                    max_drawdown,
                    self._thresholds.drawdown_critical,
                    f"最大回撤 {max_drawdown:.2%} 超过临界阈值 {self._thresholds.drawdown_critical:.2%}",
                )
            )
        elif max_drawdown < self._thresholds.drawdown_warning:
            findings.append(
                self._make_finding(
                    AuditCategory.DRAWDOWN,
                    AuditSeverity.WARNING,
                    "max_drawdown",
                    max_drawdown,
                    self._thresholds.drawdown_warning,
                    f"最大回撤 {max_drawdown:.2%} 超过警告阈值 {self._thresholds.drawdown_warning:.2%}",
                )
            )
        return findings

    def _audit_risk_adjusted(self, metrics: dict) -> list[AuditFinding]:
        """风险调整收益审计——Sharpe + Sortino。"""
        findings: list[AuditFinding] = []

        # Sharpe
        try:
            sharpe = _get_float(metrics, "sharpe_ratio")
            if sharpe < self._thresholds.sharpe_warning:
                findings.append(
                    self._make_finding(
                        AuditCategory.RISK_ADJUSTED,
                        AuditSeverity.WARNING,
                        "sharpe_ratio",
                        sharpe,
                        self._thresholds.sharpe_warning,
                        f"Sharpe比率 {sharpe:.4f} 低于警告阈值 {self._thresholds.sharpe_warning}",
                    )
                )
            elif sharpe < self._thresholds.sharpe_info:
                findings.append(
                    self._make_finding(
                        AuditCategory.RISK_ADJUSTED,
                        AuditSeverity.INFO,
                        "sharpe_ratio",
                        sharpe,
                        self._thresholds.sharpe_info,
                        f"Sharpe比率 {sharpe:.4f} 低于信息阈值 {self._thresholds.sharpe_info}",
                    )
                )
        except InvalidAuditInputError:
            pass

        # Sortino
        try:
            sortino = _get_float(metrics, "sortino_ratio")
            if sortino < self._thresholds.sortino_warning:
                findings.append(
                    self._make_finding(
                        AuditCategory.RISK_ADJUSTED,
                        AuditSeverity.WARNING,
                        "sortino_ratio",
                        sortino,
                        self._thresholds.sortino_warning,
                        f"Sortino比率 {sortino:.4f} 低于警告阈值 {self._thresholds.sortino_warning}",
                    )
                )
        except InvalidAuditInputError:
            pass

        return findings

    def _audit_attribution(self, attribution: dict) -> list[AuditFinding]:
        """归因一致性校验——allocation+selection+interaction ≈ total_return。"""
        findings: list[AuditFinding] = []
        try:
            total_return = _get_float(attribution, "total_return")
            allocation = _get_float(attribution, "allocation_effect")
            selection = _get_float(attribution, "selection_effect")
            interaction = _get_float(attribution, "interaction_effect")
        except InvalidAuditInputError:
            return findings

        decomposed_sum = allocation + selection + interaction
        diff = abs(decomposed_sum - total_return)

        if diff > self._thresholds.attribution_tolerance:
            findings.append(
                self._make_finding(
                    AuditCategory.ATTRIBUTION,
                    AuditSeverity.WARNING,
                    "attribution_consistency",
                    diff,
                    self._thresholds.attribution_tolerance,
                    f"归因分解不自洽: allocation+selection+interaction={decomposed_sum:.6f}"
                    f" vs total_return={total_return:.6f}, 误差={diff:.6f}"
                    f" > 容忍阈值={self._thresholds.attribution_tolerance}",
                )
            )
        return findings

    def _audit_cost(self, attribution: dict, expected_cost: float | None) -> list[AuditFinding]:
        """交易成本审计——实际成本 vs 预期成本比例。"""
        findings: list[AuditFinding] = []
        if expected_cost is None or expected_cost <= 0:
            return findings

        try:
            cost_drag = _get_float(attribution, "transaction_cost_drag")
        except InvalidAuditInputError:
            return findings

        cost_ratio = abs(cost_drag) / expected_cost

        if cost_ratio > self._thresholds.cost_critical_ratio:
            findings.append(
                self._make_finding(
                    AuditCategory.COST,
                    AuditSeverity.CRITICAL,
                    "cost_ratio",
                    cost_ratio,
                    self._thresholds.cost_critical_ratio,
                    f"交易成本比例 {cost_ratio:.2f}x 超过临界阈值"
                    f" {self._thresholds.cost_critical_ratio}x"
                    f" (实际={abs(cost_drag):.6f}, 预期={expected_cost:.6f})",
                )
            )
        elif cost_ratio > self._thresholds.cost_warning_ratio:
            findings.append(
                self._make_finding(
                    AuditCategory.COST,
                    AuditSeverity.WARNING,
                    "cost_ratio",
                    cost_ratio,
                    self._thresholds.cost_warning_ratio,
                    f"交易成本比例 {cost_ratio:.2f}x 超过警告阈值"
                    f" {self._thresholds.cost_warning_ratio}x"
                    f" (实际={abs(cost_drag):.6f}, 预期={expected_cost:.6f})",
                )
            )
        return findings

    # ── 完整性校验 ──

    def validate_report(self, report: PerformanceAuditReport) -> bool:
        """校验报告完整性——重算 data_hash 比对。

        Args:
            report: 待校验报告。

        Returns:
            bool: True=内容未篡改, False=内容被篡改。
        """
        content = {
            "performance_summary": report.performance_summary,
            "attribution_summary": report.attribution_summary,
            "findings": report.findings,
            "recommendations": report.recommendations,
        }
        actual_hash = _compute_data_hash(content)
        if actual_hash != report.data_hash:
            _logger.warning(
                "validate_report FAIL: report_id=%s data_hash 不匹配（内容被篡改）",
                report.report_id,
            )
            return False
        return True

    # ── 内部工具 ──

    @staticmethod
    def _make_finding(
        category: AuditCategory,
        severity: AuditSeverity,
        metric_name: str,
        actual_value: float,
        threshold: float,
        description: str,
    ) -> AuditFinding:
        """构建审计发现。"""
        return AuditFinding(
            finding_id=f"FIND-{uuid.uuid4().hex[:8]}",
            category=category,
            severity=severity,
            metric_name=metric_name,
            actual_value=actual_value,
            threshold=threshold,
            description=description,
        )


__all__ = [
    "ASharePerformanceAuditor",
    "AuditCategory",
    "AuditFinding",
    "AuditSeverity",
    "AuditThresholds",
    "InvalidAuditInputError",
    "OptimizationRecommendation",
    "PerformanceAuditReport",
    "RecommendationPriority",
    "RecommendationType",
]
