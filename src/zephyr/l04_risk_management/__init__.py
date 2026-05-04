"""L04 Risk Management
=====================================

14 层量化架构 · L04 风险管理层

职责
----
实时风控与止损执行：止损计算、头寸校验与风险敞口监控。
上位层 L05（组合构建）的约束提供者。

子模块
------
- stop_loss.py : 止损执行引擎

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
架构决策：ADR-0022 目录双轨治理
"""
