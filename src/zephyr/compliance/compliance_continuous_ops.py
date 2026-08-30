# [BLUEPRINT] MOD-CMP-004 | docs/03_modules/MOD-CMP-004/
# [MODULE] zephyr.compliance.compliance_continuous_ops
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L10-001(合规域运营巡检) ; D_FRONTEND(合规健康面板)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 留存核查类别缺失=无法验证→CRITICAL(fail-closed,不可验证即违规); healthy=无CRITICAL finding(WARNING不阻断); 探针异常→CRITICAL probe_error(宁可误报不可漏报); 评估核心为纯函数(evaluate_continuous_ops); run_once单次有界执行(无循环); 留存基线B-016(交易2555天/决策1095天/系统365天)
# [MODIFY-GUARD] docs/03_modules/MOD-CMP-004/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 探针异常不外抛(转CRITICAL finding)
# [TESTS] tests/compliance/test_compliance_continuous_ops.py
# [A_module] module_id=MOD-CMP-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



Compliance Continuous Ops — 合规持续运营 (MOD-CMP-004)

合规域的持续运营巡检（非一次性门禁）：每次运行产出结构化合规健康报告。
三类常态化检查（宪章 §4.4 B-016 / §6 合规性 P0 映射）：
  1. retention_shortfall / retention_unverifiable
     审计日志留存核查（B-016：交易≥7年 / 决策≥3年 / 系统≥1年）；
     类别缺失=无法验证 → CRITICAL（fail-closed：不可验证即违规）
  2. rule_stale / rules_absent
     合规规则新鲜度（超 rule_stale_days 未更新 → WARNING；零规则 → WARNING）
  3. intercept_backlog
     异步拦截队列积压（MOD-L10-001 GAP-L10-001 配套运营指标）

数据全部经探针注入（生产接线: 审计存储/规则注册表/拦截队列），
本模块只做纯函数评估 + 单次有界编排（无持续循环，调度由上层任务系统负责）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ops_input 参数
#   fields: 参数 ops_input，类型注解 ComplianceOpsInput
#   code: compliance_continuous_ops.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config，类型注解 ComplianceOpsConfig
#   code: compliance_continuous_ops.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: run_id 参数
#   fields: 参数 run_id（无注解）
#   code: compliance_continuous_ops.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① evaluate_continuous_ops
#   name_en: evaluate_continuous_ops
#   intro: 合规持续运营评估（纯函数：同输入必同输出，可单测）。
#   desc: 合规持续运营评估（纯函数：同输入必同输出，可单测）。；源码 L159-L240
#   inputs: ops_input config run_id
#   outputs: ComplianceOpsReport
# - id: A2
#   name_zh: ② ComplianceContinuousOps
#   name_en: ComplianceContinuousOps
#   intro: 合规持续运营编排器（单次有界 run_once；探针失败 fail-closed 转 CRITICAL）。
#   desc: 合规持续运营编排器（单次有界 run_once；探针失败 fail-closed 转 CRITICAL）。；公共方法（定义序）: run_once；源码 L243-L311
#   inputs: retention_probe rule_update_probe queue_pending_probe config
#   outputs: 返回值
#   （注：A2 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ComplianceOpsReport
#   name_en: ComplianceOpsReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-L10-001(合规域运营巡检) ; D_FRONTEND(合规健康面板)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

_logger = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_RETENTION_REQUIREMENTS",
    "ComplianceContinuousOps",
    "ComplianceOpsConfig",
    "ComplianceOpsInput",
    "ComplianceOpsReport",
    "OpsFinding",
    "RetentionRequirement",
    "evaluate_continuous_ops",
]


@dataclass(frozen=True)
class RetentionRequirement:
    """单类日志的留存下限（B-016 映射）。"""

    category: str
    min_days: int


#: B-016 留存基线：交易日志≥7年(2555天) / 决策日志≥3年(1095天) / 系统日志≥1年(365天)
DEFAULT_RETENTION_REQUIREMENTS: Final = (
    RetentionRequirement(category="trade_log", min_days=2555),
    RetentionRequirement(category="decision_log", min_days=1095),
    RetentionRequirement(category="system_log", min_days=365),
)


@dataclass(frozen=True)
class ComplianceOpsConfig:
    """持续运营阈值配置（C 类可调参数）。"""

    intercept_queue_backlog_threshold: int = 500
    rule_stale_days: int = 365
    retention_requirements: tuple[RetentionRequirement, ...] = DEFAULT_RETENTION_REQUIREMENTS


@dataclass(frozen=True)
class ComplianceOpsInput:
    """持续运营评估输入（>4 探针数据收 dataclass；全探针注入，无真源留接口位）。"""

    retention_status: Mapping[str, int]  # category -> 当前最老留存天数
    rule_updates: Mapping[str, datetime]  # rule_id -> 最近更新时间
    intercept_queue_pending: int
    now: datetime


@dataclass(frozen=True)
class OpsFinding:
    """单条运营发现（结构化）。"""

    check_id: str
    severity: str  # "INFO" | "WARNING" | "CRITICAL"
    message: str
    details: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ComplianceOpsReport:
    """合规持续运营报告（frozen；healthy=无 CRITICAL finding）。"""

    run_id: str
    evaluated_at: datetime
    healthy: bool
    findings: tuple[OpsFinding, ...]


def evaluate_continuous_ops(
    ops_input: ComplianceOpsInput,
    config: ComplianceOpsConfig,
    *,
    run_id: str | None = None,
) -> ComplianceOpsReport:
    """合规持续运营评估（纯函数：同输入必同输出，可单测）。"""
    findings: list[OpsFinding] = []

    # ① 审计留存核查（B-016）
    for requirement in config.retention_requirements:
        retained_days = ops_input.retention_status.get(requirement.category)
        if retained_days is None:
            findings.append(
                OpsFinding(
                    check_id="retention_unverifiable",
                    severity="CRITICAL",
                    message=(f"留存无法验证: {requirement.category} 无探针数据（fail-closed: 不可验证即违规, B-016）"),
                    details=(("category", requirement.category),),
                )
            )
        elif retained_days < requirement.min_days:
            findings.append(
                OpsFinding(
                    check_id="retention_shortfall",
                    severity="CRITICAL",
                    message=(
                        f"留存不足: {requirement.category} 最老留存 {retained_days} 天 "
                        f"< 要求 {requirement.min_days} 天（B-016）"
                    ),
                    details=(
                        ("category", requirement.category),
                        ("retained_days", str(retained_days)),
                        ("min_days", str(requirement.min_days)),
                    ),
                )
            )

    # ② 规则新鲜度
    if not ops_input.rule_updates:
        findings.append(
            OpsFinding(
                check_id="rules_absent",
                severity="WARNING",
                message="合规规则集为空（无任何规则更新记录）",
            )
        )
    else:
        stale_cutoff_seconds = config.rule_stale_days * 86400
        for rule_id, updated_at in sorted(ops_input.rule_updates.items()):
            age_seconds = (ops_input.now - updated_at).total_seconds()
            if age_seconds > stale_cutoff_seconds:
                findings.append(
                    OpsFinding(
                        check_id="rule_stale",
                        severity="WARNING",
                        message=(f"合规规则超期未更新: {rule_id} 已 {int(age_seconds // 86400)} 天"),
                        details=(("rule_id", rule_id),),
                    )
                )

    # ③ 拦截队列积压
    if ops_input.intercept_queue_pending > config.intercept_queue_backlog_threshold:
        findings.append(
            OpsFinding(
                check_id="intercept_backlog",
                severity="WARNING",
                message=(
                    f"异步拦截队列积压: {ops_input.intercept_queue_pending} > "
                    f"{config.intercept_queue_backlog_threshold}"
                ),
                details=(("pending", str(ops_input.intercept_queue_pending)),),
            )
        )

    healthy = not any(f.severity == "CRITICAL" for f in findings)
    return ComplianceOpsReport(
        run_id=run_id or f"ops-{uuid.uuid4().hex[:12]}",
        evaluated_at=ops_input.now,
        healthy=healthy,
        findings=tuple(findings),
    )


class ComplianceContinuousOps:
    """合规持续运营编排器（单次有界 run_once；探针失败 fail-closed 转 CRITICAL）。"""

    def __init__(
        self,
        retention_probe: Callable[[], Mapping[str, int]],
        rule_update_probe: Callable[[], Mapping[str, datetime]],
        queue_pending_probe: Callable[[], int],
        config: ComplianceOpsConfig | None = None,
    ) -> None:
        self._retention_probe = retention_probe
        self._rule_update_probe = rule_update_probe
        self._queue_pending_probe = queue_pending_probe
        self._config = config or ComplianceOpsConfig()

    def run_once(self, *, now: datetime | None = None) -> ComplianceOpsReport:
        """执行一轮运营巡检（单次，无循环；调度由上层任务系统负责）。"""
        now = now or datetime.now(UTC)
        pre_findings: list[OpsFinding] = []

        probes: dict[str, Callable] = {
            "retention": self._retention_probe,
            "rule_update": self._rule_update_probe,
            "queue_pending": self._queue_pending_probe,
        }
        collected: dict[str, object] = {}
        for probe_name, probe in probes.items():
            try:
                collected[probe_name] = probe()
            except Exception as exc:  # noqa: BLE001 — fail-closed 转 CRITICAL
                _logger.error("COMPLIANCE_OPS_PROBE_ERROR probe=%s error=%s", probe_name, exc)
                pre_findings.append(
                    OpsFinding(
                        check_id="probe_error",
                        severity="CRITICAL",
                        message=f"运营探针异常: {probe_name}（fail-closed，宁可误报）",
                        details=(("probe", probe_name), ("error", str(exc))),
                    )
                )
                collected[probe_name] = None

        ops_input = ComplianceOpsInput(
            retention_status=collected["retention"] if collected["retention"] is not None else {},
            rule_updates=collected["rule_update"] if collected["rule_update"] is not None else {},
            intercept_queue_pending=(
                collected["queue_pending"]
                if collected["queue_pending"] is not None
                else self._config.intercept_queue_backlog_threshold + 1
            ),
            now=now,
        )
        report = evaluate_continuous_ops(ops_input, self._config)
        if pre_findings:
            # 探针异常 finding 并入（healthy 重算）
            merged = tuple(pre_findings) + report.findings
            healthy = not any(f.severity == "CRITICAL" for f in merged)
            report = ComplianceOpsReport(
                run_id=report.run_id,
                evaluated_at=report.evaluated_at,
                healthy=healthy,
                findings=merged,
            )
        if not report.healthy:
            _logger.warning(
                "COMPLIANCE_OPS_UNHEALTHY run=%s criticals=%s",
                report.run_id,
                [f.check_id for f in report.findings if f.severity == "CRITICAL"],
            )
        return report
