---
module_id: KE-documentat-1_1-006
title: 1.1 维度清单
category: documentation
---

# 1.1 维度清单

1.1 维度清单

| 维度 | 名称 | 关注点 | 权重 | 对应架构文档 |
|:----:|------|-------|:----:|-------------|
| **D1** | 业务架构 | 业务能力完整性、需求覆盖 | 0.08 | `01-business-architecture.md` |
| **D2** | 信息架构 | 数据模型、元数据治理、schema 演化 | 0.08 | `02-information-architecture.md` |
| **D3** | 应用架构 | 模块边界、服务拆分、职责清晰度 | 0.10 | `03-application-architecture.md` |
| **D4** | 技术架构 | 技术栈成熟度、升级路径、零依赖原则 | 0.08 | `04-technology-architecture.md` + `technology-landscape.yaml` |
| **D5** | MCP 集成 | AI IDE 兼容性、MCP 协议通道覆盖 | 0.08 | `context-engine-interface.md §5` |
| **D6** | 安全架构 | 防御深度、OWASP LLM Top 10 覆盖、沙箱隔离 | 0.12 | `06-security-architecture.md` + `llm-security-gateway-interface.md` |
| **D7** | Agent 编排 | 任务生命周期、幻觉检测、状态机完整性 | 0.10 | `agent-orchestrator-interface.md` |
| **D8** | 反馈闭环 | 指标-异常-动作链路、可观测性 | 0.10 | `feedback-loop-engine-interface.md` |
| **D9** | 数据架构 | 存储一致性、备份/恢复、容灾 | 0.06 | `05-data-architecture.md` |
| **D10** | 运维架构 | SLI/SLO、可观测性三支柱、告警 | 0.08 | `08-operations-architecture.md` |
| **D11** | 安全运营 | Secret 防护、供应链安全、审计合规 | 0.06 | `06-security-architecture.md §6` |
| **D12** | 治理架构 | SSoT 一致性、ADR 覆盖、流程门禁 | 0.06 | `09-governance-architecture.md` |
| **合计** | — | — | **1.00** | — |
