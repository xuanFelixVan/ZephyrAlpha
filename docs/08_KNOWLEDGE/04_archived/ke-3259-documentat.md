---
module_id: KE-3259
title: 1.1 维度清单
category: documentation
ttl: permanent
---

# 1.1 维度清单

1.1 维度清单

| 维度 | 名称 | 关注点 | 权重 | 对应架构文档 |
|:----:|------|-------|:----:|-------------|
| **D1** | 业务架构 | 业务能力完整性、需求覆盖 | 0.08 | `business_architecture.md` |
| **D2** | 信息架构 | 数据模型、元数据治理、schema 演化 | 0.08 | `information_architecture.md` |
| **D3** | 应用架构 | 模块边界、服务拆分、职责清晰度 | 0.10 | `application_architecture.md` |
| **D4** | 技术架构 | 技术栈成熟度、升级路径、零依赖原则 | 0.08 | `technology_architecture.md` + `technology_landscape.yaml` |
| **D5** | MCP 集成 | AI IDE 兼容性、MCP 协议通道覆盖 | 0.08 | `context-engine-interface.md §5` |
| **D6** | 安全架构 | 防御深度、OWASP LLM Top 10 覆盖、沙箱隔离 | 0.12 | `security_architecture.md` + `llm-security-gateway-interface.md` |
| **D7** | Agent 编排 | 任务生命周期、幻觉检测、状态机完整性 | 0.10 | `agent-orchestrator-interface.md` |
| **D8** | 反馈闭环 | 指标-异常-动作链路、可观测性 | 0.10 | `feedback-loop-engine-interface.md` |
| **D9** | 数据架构 | 存储一致性、备份/恢复、容灾 | 0.06 | `data_architecture.md` |
| **D10** | 运维架构 | SLI/SLO、可观测性三支柱、告警 | 0.08 | `operations_architecture.md` |
| **D11** | 安全运营 | Secret 防护、供应链安全、审计合规 | 0.06 | `security_architecture.md §6` |
| **D12** | 治理架构 | SSoT 一致性、ADR 覆盖、流程门禁 | 0.06 | `governance_architecture.md` |
| **合计** | — | — | **1.00** | — |
