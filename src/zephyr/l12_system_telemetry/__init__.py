"""L12 System Telemetry
=====================================

14 层量化架构 · L12 系统遥测层

职责
----
全系统可观测性基础设施：Prometheus 指标导出、OpenTelemetry 链路追踪、
结构化日志聚合、历史数据归档与 AI 行为遥测。

与 AI/ML Platform 三件套的关系
------------------------------
L11 ML Platform       — ML 生命周期（训练/推理/模型注册）
L12 System Telemetry  — 系统可观测性（本层）
L13 Experimentation   — 自动化实验

子模块
------
- contract_metrics.py : SLA 测量 + 契约漂移检测 + 违规记录
- metrics/            : blueprint_metrics（JSONL instrumentation）
- traces/             : span_stub（OTEL 前占位）
- logs/               : structured_sink（JSONL）
- archive/            : cold_stub（批次 ID）
- ai_behavior/        : event_sink（AI 行为出站钩子）

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为生产者（Producer）：
  - CTR-P1-013  TelemetryEmitter       → L01, L04, L06, L07, L10, L12（系统级遥测发射器）

作为 SLA 测量提供者（跨层契约 SLA 监控）：
  - CTR-SLA-001~006  SLA 测量         → 监控 CTR-001~006 的端到端延迟
  - CTR-TRACE-001    TraceContext      → span 关联与延迟计算
  - CTR-VER-001       契约版本协商通知  → 通过 contract_version_change 事件发布

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

from zephyr.l12_system_telemetry.contract_metrics import (
    ContractMetricsCollector,
    DriftAlert,
    SlaRecord,
    get_contract_metrics,
)

__all__ = [
    "ContractMetricsCollector",
    "SlaRecord",
    "DriftAlert",
    "get_contract_metrics",
]
