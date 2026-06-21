---
module_id: KE-161-------c---14-005
title: 2.1 业务核心层（C 轨 14 层）
category: documentation
---

# 2.1 业务核心层（C 轨 14 层）

2.1 业务核心层（C 轨 14 层）

| 模块 | 路径 | 权限 | 判定理由 | 审批要求 |
|------|------|------|---------|---------|
| L00 数据接入 | `src/zephyr/l00-data-source/` | Human-Gated | 数据源连接参数影响数据完整性 | Owner 审批连接配置 |
| L01 基础设施 | `src/zephyr/l01-infrastructure/` | Human-Gated | 基础设施变更影响所有上层 | Owner 审批 |
| L02 Alpha 因子 | `src/zephyr/l02-alpha-factor/` | AI-Modifiable | 因子算法可自主优化 | 写 Provenance |
| L03 信号生成 | `src/zephyr/l03-signal-generation/` | AI-Modifiable | 信号生成算法 | 写 Provenance |
| **L04 风险管理** | `src/zephyr/l04-risk-management/` | **Immutable Core** | 风控是量化系统不可变层 | Owner + ADR |
| L05 组合构建 | `src/zephyr/l05-portfolio-construction/` | Human-Gated | 组合策略影响资金分配 | Owner 审批策略修改 |
| L06 交易执行 | `src/zephyr/l06-trade-execution/` | Human-Gated | 执行参数影响成交质量 | Owner 审批 |
| **L06 风控参数（限额）** | 同上 子模块 | **Immutable Core** | 限额参数不可 AI 改 | Owner + ADR |
| L07 归因分析 | `src/zephyr/l07-post-trade-analytics/` | Human-Gated（**修正**：原 GLM 标 AI-Modifiable 偏松） | L7 风控关联 | Owner 审批 |
| L08 人机界面 | `src/zephyr/l08-human-ai-interface/` | AI-Modifiable | UI 实现 | 写 Provenance |
| L09 研究创新 | `src/zephyr/l09-research-innovation/` | AI-Modifiable | 实验性研究 | 写 Provenance |
| **L10 合规** | `src/zephyr/l10-compliance/` | **Immutable Core** | 合规规则刚性 | Owner + ADR |
| L11 ML 平台 | `src/zephyr/l11-ml-platform/` | AI-Modifiable | 模型训练实现 | 写 Provenance |
| L12 系统遥测 | `src/zephyr/l12_system_telemetry/` | AI-Modifiable | 日志实现 | 写 Provenance |
| L12 采样率 | 同上 子模块 | Human-Gated（**修正**） | 采样率影响审计完整性 | Owner 审批 |
| L13 实验平台 | `src/zephyr/l13-experimentation/` | AI-Modifiable | 实验框架 | 写 Provenance |
