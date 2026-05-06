"""L06 Trade Execution
=====================================

14 层量化架构 · L06 交易执行层

职责
----
订单执行与成交管理：多券商路由（SOR）、委托指令下发、成交回报处理与持仓快照维护。

子模块
------
- broker_interface.py : BrokerInterface（OCP-003 扩展点）
- adapters/           : 券商适配器实现目录

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标。任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-004  Order                      ← L05
  - CTR-ERR-004  RiskLimitViolationError ← L04

作为生产者（Producer）：
  - CTR-005  Fill                       → L07
  - CTR-006  PositionSnapshot           → L04, L07, L11
  - CTR-ERR-005  ExecutionRejectionError → L05, L07
  - CTR-P1-007  ExecutionReport         → L07

外部系统边界：
  - EXT-001  Broker API（双向：REST / FIX 4.2+）

作为全局配置消费者（Consumer）：
  - CTR-P1-010  SystemConfiguration    ← L01
  - CTR-P1-012  ComplianceRule         ← L10
  - CTR-P1-013  TelemetryEmitter       ← L12

SSoT: cross-layer-contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

# CODEGEN-GUARD: CTR-declarations-manual
# DO NOT regenerate: CTR declarations are manually curated SSoT annotations

from .broker_interface import *  # noqa: F403
