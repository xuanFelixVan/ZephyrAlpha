# [A_module] module_id=MOD-UNK_risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""L04 Risk Management
=====================================

14 层量化架构 · L04 风险管理层

职责
----
实时风控与止损执行：止损计算、头寸校验与风险敞口监控。
上位层 L05（组合构建）的约束提供者。

子模块
------
- stop_loss.py      : 止损执行引擎（与 kill_switch）
- risk_limits.py    : 风险限额计算器 (RiskLimitsCalculator) — Phase B 骨架已生成
- risk_validator.py : 风险校验器 (RiskValidator) — Phase B 骨架已生成

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-002  FactorSignal              ← L02
  - CTR-006  PositionSnapshot          ← L06
  - CTR-ERR-003  SignalDegradationWarning ← L03
  - CTR-ERR-005  ExecutionRejectionError  ← L06/L07
  - CTR-P1-011  RiskMetricsReport      ← L05
  - CTR-P1-012  ComplianceRule         ← L10
  - CTR-P1-013  TelemetryEmitter       ← L12
  - CTR-P1-015  SynthesizedSignal      ← L03

作为生产者（Producer）：
  - CTR-003  RiskLimits                  → L05
  - CTR-ERR-004  RiskLimitViolationError → L05, L06
  - CTR-P1-008  RiskDashboardSnapshot    → L08

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

from __future__ import annotations

import importlib as _importlib

# MIGRATED: from zephyr.risk.risk_manager import (  # removed by TC-7-2
# RiskDashboardSnapshot,  # removed by TC-7-2
# RiskLimitViolationError,  # removed by TC-7-2
# RiskLimits,  # removed by TC-7-2
# RiskManagerBase,  # removed by TC-7-2
# RiskMetricsReport,  # removed by TC-7-2
# )  # removed by TC-7-2
# from zephyr.risk.risk_limits import (
# RiskLimitsCalculator,
# )
# MIGRATED: from zephyr.risk.risk_validator import (  # removed by TC-7-2
# RiskValidator,  # removed by TC-7-2
# ViolatedConstraint,  # removed by TC-7-2
# ViolationDetail,  # removed by TC-7-2
# )  # removed by TC-7-2
# MIGRATED: from zephyr.risk.risk_manager_base import (  # removed by TC-7-2
# PositionLimitCheckerBase,  # removed by TC-7-2
# RiskCheckResult,  # removed by TC-7-2
# RiskManagerOrchestratorBase,  # removed by TC-7-2
# RiskReport,  # removed by TC-7-2
# StopLossEngineBase,  # removed by TC-7-2
# )  # removed by TC-7-2
#
# __all__ = ['PositionLimitCheckerBase', 'RiskCheckResult', 'RiskDashboardSnapshot', 'RiskLimitViolationError', 'RiskLimits', 'RiskLimitsCalculator', 'RiskManagerBase', 'RiskManagerOrchestratorBase', 'RiskMetricsReport', 'RiskReport', 'RiskValidator', 'StopLossEngineBase', 'ViolatedConstraint', 'ViolationDetail', 'risk_limits', 'risk_manager', 'risk_manager_base', 'risk_validator', 'stop_loss']
#

__all__ = [
    "cross_asset",
    "risk_limits",
    "risk_manager",
    "risk_manager_base",
    "risk_validator",
    "stop_loss",
]


def __getattr__(name):
    if name == "cross_asset":
        return _importlib.import_module(".cross_asset", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
