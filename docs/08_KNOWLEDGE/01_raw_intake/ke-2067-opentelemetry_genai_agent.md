---
module_id: KE-1976---ai-a-000
title: 2f. OpenTelemetry GenAI + AI Agent 语义约定对齐 🆕
category: module_blueprint
ttl: permanent
---

# 2f. OpenTelemetry GenAI + AI Agent 语义约定对齐 🆕

2f. OpenTelemetry GenAI + AI Agent 语义约定对齐 🆕

> **B44 修复**——v0.7.0 新增。OTel 于 2025 年 9 月发布了 GenAI Semantic Conventions（v1.37+），定义了 LLM 调用的标准 trace span 属性；2025 年 11 月 Traceloop/OpenLLMetry 提交了 AI Agent Observability RFC（20 种 span 类型 + 300+ 属性）。Honeycomb 2026 年 3 月发布 MCP 集成 + AI Agent Monitoring；Datadog 2025 年 6 月 DASH 大会发布 AI Agent Monitoring。全行业正在用一套统一语义描述 AI 系统的可观测性数据。Telemetry 蓝图必须显式对齐这一标准，否则 AI 生成的遥测数据无法被行业标准工具消费。
