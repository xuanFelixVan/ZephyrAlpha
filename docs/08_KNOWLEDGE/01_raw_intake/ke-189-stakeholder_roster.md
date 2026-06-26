---
module_id: KE-189
title: 2.1 Stakeholder Roster / 利益相关者清单
category: documentation
ttl: permanent
---

# 2.1 Stakeholder Roster / 利益相关者清单

2.1 Stakeholder Roster / 利益相关者清单

专业量化机构的 Stakeholder 画像在"单人 + AI 协同"阶段**物理上由同一个人承担多个角色**，但**架构语义上必须拆开**——否则未来引入合伙人 / 外部投资人 / 多 AI Operator 时会出现责任真空。下表 8 类为终局形态，当前阶段的角色归属见 §2.2 注脚。

| # | Stakeholder / 利益相关者 | Role / 角色 | Primary concerns / 主要关注点 | 当前阶段归属 |
|---|-------------------------|------------|------------------------------|------------|
| S1 | **Architect / 架构师** | 系统设计、视图一致性、ADR 决策 | 架构完整性、TOGAF 8 视图对齐、技术债可控 | you |
| S2 | **Quant researcher / 策略研究员** | 策略研发、因子构造、假设检验 | Alpha 质量、PIT 一致性、回测可信度 | you |
| S3 | **Trader / 交易员** | 下单执行、成交监控、异常处置 | 执行滑点、成交质量、下单延迟 | you |
| S4 | **Risk officer / 风控官** | 事前限额、事中监控、事后审查 | 仓位限额、回撤止损、幂等红线 | you |
| S5 | **Compliance officer / 合规官** | 合规审查、监管留痕、报告披露 | 交易记录留痕、ADR 审计链、合规触发 | you（deferred，`16_compliance_and_legal/` 激活后独立）|
| S6 | **Data engineer / 数据工程师** | 数据接入、质量门禁、血缘追踪 | Data Freshness、Quality 断言、血缘完整 | you |
| S7 | **SRE / Ops / 运维** | 部署、监控、容量、成本、DR | 可用性、Runbook 可演练、成本可控 | you（deferred，`operations_architecture.md` skeleton 激活后独立）|
| S8 | **AI collaborators / AI 协作者** | Kimi（diverge 发散）+ Cursor/Opus（converge 收敛）| 文档可读性、上下文质量、结构一致性 | Kimi / Cursor-Opus / Sonnet / GLM / Qwen |
| S9 | **AI Operators / AI 代理人**（预留，`OQ-063` AC-1/2/3 + C-1/2/3）| 未来承担日常执行类职责的自治 Agent（如 factor-refresh-operator / rebalancer-operator）| 决策日志完整、可审计、红线不越界 | **未激活**；激活前接口位于 `src/zephyr/layers/{L}/_ai_operator/` + `META_GOVERNANCE/ai_operators_registry.md` |
| S10 | **External data vendor / 外部数据供应商** | 同花顺 iFinD（已采购）+ 未来 Bloomberg / Wind / 交易所直连 | 契约 SLA、API 限流、计费、字段稳定 | iFinD（合同 + API key，1 条 Vendor Registry 记录）|
| S11 | **Future partners / 未来合伙人** | 潜在合作者 / 外部投资人 | 策略透明度、合规记录、绩效归因可验证 | **未激活**（personal-scale initially）|
| S12 | **Regulators / 监管方** | 证监 / 交易所 / 银行监管 | 交易记录留痕、合规报告、风险披露 | **未激活**（external investors or live trading 前 deferred）|
