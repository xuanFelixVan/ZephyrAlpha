"""
l12_system_telemetry/__init__.py — 系统遥测层入口

CTR-SLA-001~006 的测量基础设施。当前为框架就绪状态——层实现落盘后激活。

模块
----
- contract_metrics.py  — SLA 测量 + 契约漂移检测 + 违规记录
- (待实现) metrics/     — Prometheus 指标导出
- (待实现) traces/      — OpenTelemetry trace 导出
- (待实现) logs/        — 结构化日志
- (待实现) archive/     — 历史数据归档
- (待实现) ai_behavior/ — AI 行为遥测

SSoT: cross-layer-contracts.yaml → CTR-SLA-001~006, CTR-TRACE-001
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
