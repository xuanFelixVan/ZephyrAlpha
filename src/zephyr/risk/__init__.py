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
# [TTL] permanent
"""D_RISK Risk Management
=====================================

域量化架构 · D_RISK 风险管理层

职责
----
实时风控与止损执行：止损计算、头寸校验与风险敞口监控。
上位层 D_PORTFOLIO_CORE（组合构建）的约束提供者。

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
  - CTR-002  FactorSignal              ← D_FACTOR
  - CTR-006  PositionSnapshot          ← D_EXECUTION_CORE
  - CTR-ERR-003  SignalDegradationWarning ← D_SIGNAL
  - CTR-ERR-005  ExecutionRejectionError  ← D_EXECUTION_CORE/D_REPORTING
  - CTR-P1-011  RiskMetricsReport      ← D_PORTFOLIO_CORE
  - CTR-P1-012  ComplianceRule         ← D_COMPLIANCE
  - CTR-P1-013  TelemetryEmitter       ← 遥测
  - CTR-P1-015  SynthesizedSignal      ← D_SIGNAL

作为生产者（Producer）：
  - CTR-003  RiskLimits                  → D_PORTFOLIO_CORE
  - CTR-ERR-004  RiskLimitViolationError → D_PORTFOLIO_CORE, D_EXECUTION_CORE
  - CTR-P1-008  RiskDashboardSnapshot    → D_FRONTEND

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

from __future__ import annotations

import importlib as _importlib

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
