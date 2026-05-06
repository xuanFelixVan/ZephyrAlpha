"""L13 Experimentation
=====================================

14 层量化架构 · L13 自动化实验层

职责
----
AI 时代的"自动化实验"层：Scout Agent 自动抓取外部资讯 + 内部 repo diff，
设计并执行对照实验（A/B 测试、因子消融、策略变种）、沉淀实验结论到 KMS。

架构真源
--------
docs/02_enterprise_architecture/target-architecture/
  03-application-architecture.md §4.3（AI/ML Platform：L11/L12/L13）

CTR 契约依赖声明（承重墙标记）
------------------------------
作为生产者（Producer）：
  - CTR-P1-014 (ExperimentResult) — 实验结论，发布至 L09/L11

作为消费者（Consumer）：
  - CTR-001 (NormalizedMarketData) — 实验需要市场数据上下文
  - CTR-P1-004/005 (ModelServing) — Scout Agent 调用 L11 模型推断
  - CTR-P1-013 (TelemetryEmitter) — 实验运行数据上报 L12

与 L11/L12 的关系
-----------------
L11 ml_platform       : ML 生命周期（训练/推理/模型注册）
L12 system_telemetry  : 系统可观测性
L13 experimentation   : 自动化实验（Scout + A/B + 结论沉淀）

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

from __future__ import annotations

from zephyr.l13_experimentation.pipeline_base import (
    ExperimentConfig,
    ExperimentMetric,
    ExperimentPipelineBase,
    ScoutAgentBase,
)

__all__ = [
    "ExperimentConfig",
    "ExperimentMetric",
    "ExperimentPipelineBase",
    "ScoutAgentBase",
]
