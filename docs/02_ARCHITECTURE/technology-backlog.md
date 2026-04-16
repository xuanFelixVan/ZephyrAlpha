---
module_id: ARCH_TECHNOLOGY_BACKLOG
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 技术 Backlog (Technology Backlog)

> **用途**：记录所有 P2 未来能力（计划实现但暂不在当前 Phase 的功能）、被废弃蓝图中提取的有价值构想、以及技术评估候选项。
> **规则**：清理幽灵引用时，有价值的名称/构想应提取至本文件（Ghost Reference Salvage 规则）。

---

## P2 能力清单（计划但暂不实现）

### L04 ML 模型层

| 构想 | 来源 | 技术方向 | 备注 |
|------|------|---------|------|
| 强化学习策略优化 | 蓝图 `reinforcement-learning-blueprint.md` | RLlib, PPO/SAC | P2，规模化后才有价值 |
| 主动学习样本选择 | 蓝图 `active-learning-blueprint.md` | 不确定性采样 | P2 |
| Transformer 情感模型 | 舆情层 gap 分析报告 | BERT/FinBERT | ADR 记录：为何先用 LSTM |

### L06 执行层

| 构想 | 来源 | 技术方向 | 备注 |
|------|------|---------|------|
| 智能订单路由 (SOR) | 蓝图 `smart-order-routing-blueprint.md` | 机器学习路由优化 | P2，机构级需求 |
| 暗池接入 | 架构讨论 | FIX 协议扩展 | P2，监管合规前置 |

### L07 AI 报告层

| 构想 | 来源 | 技术方向 | 备注 |
|------|------|---------|------|
| 多智能体协作研究 | `10_AI_WORKFLOW/` 多个蓝图 | LangGraph, AutoGen | P2 |
| 自动化情景分析 | `scenario-analysis-stress-test-blueprint.md` | LLM + 历史回放 | P1→P2 降级 |

### L10 治理合规层

| 构想 | 来源 | 技术方向 | 备注 |
|------|------|---------|------|
| 实时合规监控 | `compliance-monitoring-blueprint.md` | 规则引擎 | P2，机构级合规需求 |
| MiFID II 报告 | 架构讨论 | 监管报告生成 | P2 |

---

## 技术评估候选

| 技术 | 评估状态 | 建议 | 决策日期 |
|------|---------|------|---------|
| Polars vs Pandas | 待评估 | 大数据量时考虑 Polars | - |
| Ray vs Dask | 待评估 | 分布式回测时考虑 | - |
| MLflow vs W&B | 待评估 | 模型追踪工具 | - |

---

## Ghost Reference Salvage 记录

> 每次从幽灵引用中提取的有价值构想记录于此。

| 日期 | 来源幽灵引用 | 提取内容 | 分类 |
|------|------------|---------|------|
| 2026-04-16 | `IDEAS_PIPELINE.md`（不存在）| 创意流水线功能→合并至本 BACKLOG | P2 能力清单 |

---

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建 | AI |
