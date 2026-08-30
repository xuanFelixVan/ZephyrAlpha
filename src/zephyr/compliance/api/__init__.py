# [TTL] permanent
# compliance/api — 合规域公共 API 出口（43 号施工挂载，2026-08-15）

"""
D_COMPLIANCE 公共 API 面。

43 号合规纪律体系（43_compliance_discipline.md）施工的 7 模块经本出口对外暴露，
供 C-004 风控引擎 / C-002 执行域 / MOD-PA-006 分批建仓 / 62 号治理流程引用：

- discipline_must_do_checker（§3 BM-BUY-08-A）：四时点必做清单完成度检测
- discipline_prohibition_checker（§4 BM-BUY-08-B）：四项严禁检测 + KillSwitchLite
- license_usage_auditor（§5 BM-BUY-09）：数据源授权条款合规审计
- hard_boundary_adjudicator（§6 BM-BUY-12）：功能二元裁定门禁 FeatureGate
- trading_compliance_detector（§7 BM-BUY-15）：异常交易 2 条 + 市场操纵 4 类
- compliance_report_registry（§7.4/§7.5）：6 项报告义务登记 + ReportGate
- compliance_log（§3.2）：compliance_log JSONL append-only 落库

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, ComplianceLogger, ComplianceLogRecord, ComplianceReportR…
#   code: __init__.py import L45
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 annotations, ComplianceLogger, ComplianceLogRecord, ComplianceReportRegistr…
#   desc: __init__ import L45；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（36 符号）
#   name_en: __all__
#   intro: annotations, ComplianceLogger, ComplianceLogRecord, ComplianceReportRegistry, R…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.compliance.compliance_log import (
    ComplianceLogger,
    ComplianceLogRecord,
)
from zephyr.compliance.compliance_report_registry import (
    ComplianceReportRegistry,
    ReportGate,
    ReportGateDecision,
    ReportGateResult,
    ReportItem,
)
from zephyr.compliance.discipline_must_do_checker import (
    ChecklistAction,
    ChecklistCheckpoint,
    ChecklistCompletionChecker,
    ChecklistVerdict,
)
from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineAction,
    DisciplineContext,
    DisciplineGuard,
    DisciplineThresholds,
    DisciplineVerdict,
    KillSwitchLite,
    OrderRequest,
    ProhibitedBehavior,
)
from zephyr.compliance.hard_boundary_adjudicator import (
    FeatureEntry,
    FeatureGate,
    FeatureGateDecision,
    FeatureGateResult,
    FeatureVerdict,
)
from zephyr.compliance.license_usage_auditor import (
    LicenseAuditReport,
    LicenseUsageAuditor,
    SourceLicense,
    ViolationLevel,
)
from zephyr.compliance.trading_compliance_detector import (
    ComplianceAction,
    ComplianceOrderRecord,
    ComplianceThresholds,
    ComplianceTradeRecord,
    ManipulationType,
    ManipulationVerdict,
    TradingComplianceDetector,
)

__all__: list[str] = [
    "ChecklistAction",
    "ChecklistCheckpoint",
    "ChecklistCompletionChecker",
    "ChecklistVerdict",
    "ComplianceAction",
    "ComplianceLogger",
    "ComplianceLogRecord",
    "ComplianceOrderRecord",
    "ComplianceReportRegistry",
    "ComplianceThresholds",
    "ComplianceTradeRecord",
    "DisciplineAction",
    "DisciplineContext",
    "DisciplineGuard",
    "DisciplineThresholds",
    "DisciplineVerdict",
    "FeatureEntry",
    "FeatureGate",
    "FeatureGateDecision",
    "FeatureGateResult",
    "FeatureVerdict",
    "KillSwitchLite",
    "LicenseAuditReport",
    "LicenseUsageAuditor",
    "ManipulationType",
    "ManipulationVerdict",
    "OrderRequest",
    "ProhibitedBehavior",
    "ReportGate",
    "ReportGateDecision",
    "ReportGateResult",
    "ReportItem",
    "SourceLicense",
    "TradingComplianceDetector",
    "ViolationLevel",
]
