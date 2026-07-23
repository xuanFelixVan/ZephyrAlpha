---
module_id: VIEW-04PRINC-CAPABILITY-MATURITY
title: Capability Maturity Principles / 能力成熟度原则
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-07-19
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags:
- architecture-principle
- capability-maturity
- maturity-model
- orthogonal-view
- domain-driven
summary: 能力成熟度评估的永恒原则——五档成熟度模型定义、评分规则、季度 review 流程。派生数据（全域×10能力域热力图快照）由 depgraph 自动生成，不在本文档。
date: '2026-07-19'
ttl: permanent
---

# Capability Maturity Principles / 能力成熟度原则

> 本文档定义永恒指导内容。
> 派生数据（域成熟度快照、热力图可视化）由 `scripts/governance/d5_architecture/generators/generate_design_vs_production.py` 自动生成到 `../01_global_architecture_diagram/global_capability_heatmap.md`。

## 1. 业界对标

| 机构 | 能力地图实现 | 成熟度模型 | 刷新频率 |
|---|---|---|---|
| **Goldman Sachs** | Enterprise Architecture Capability Dashboard | 5 档 | 季度 |
| **BlackRock** | Aladdin Capability Heatmap | 5 档 | 季度 |
| **Gartner IT Capability Framework** | Generic Capability Map | 5 档（CMMI-aligned）| 半年 |

**ZephyrAlpha 采纳**：Goldman / BlackRock / Gartner 共识的 5 档模型，季度刷新。

## 2. 五档成熟度模型

### 2.1 档位定义

| 档位 | 名称 | 定义 | depgraph 映射 |
|:---:|------|------|----------------|
| **L0** | 缺失 | 能力完全不存在，无设计无代码 | 域无节点 |
| **L1** | 设计 | 仅有设计文档/蓝图，无代码 | `design_maturity='design'` |
| **L2** | 草稿 | 有原型代码，未集成 | `design_maturity='design'` |
| **L3** | 可用 | 代码可用但未生产验证 | `design_maturity='production'` + `build_status!='active'` |
| **L4** | 生产级 | 生产环境稳定运行 | `design_maturity='production'` + `build_status='active'` |
| **L5** | 顶级机构对标 | 达到 Goldman/BlackRock 水平 | 待评估 |

### 2.2 评分规则

- **域成熟度** = 该域所有节点的最高成熟度
- **能力域成熟度** = 该能力域下所有域成熟度的加权平均（按节点数加权）

## 3. 能力域划分原则

能力域采用"7 业务 + 3 横切"的二维分类：

- **业务能力域（7）**：数据接入、因子研究、策略决策、执行交易、风险控制、回测仿真、ML 平台
- **横切能力域（3）**：治理、安全、基础设施

能力域到具体域的映射由 `architecture_model/cross_cutting/capability_heatmap.yaml`（canonical schema）定义，随域增减而演进。

## 4. 季度 Review 机制

### 4.1 刷新流程

1. 运行 `generate_design_vs_production.py` 刷新域成熟度快照
2. 架构师逐域评估 L4/L5 达标情况
3. 更新差距表
4. 识别 P0/P1/P2 短板 → 纳入下季度任务卡

### 4.2 刷新频率

- **季度例行**：每 3 个月
- **事件驱动**：真实资金接入 / 架构重大变更

## 5. 目标状态定义

| 里程碑 | 目标 | 触发条件 |
|--------|------|---------|
| **T1** | 真实资金接入 | 模拟盘稳定运行 3 个月 |
| **T3** | AI 自治升格 | 5 大核心服务全部 L4 |
| **T-ENDGAME** | 顶级机构对标 | 全域能力 L4+，30% 域 L5 |

## 6. 与其他文档的关系

| 其他文档 | 关系 |
|---|---|
| `architecture_principles.md` | 本文是总纲 §4 核心架构决策的能力成熟度子原则 |
| `architecture_model/cross_cutting/capability_heatmap.yaml` | YAML 是机器可读能力清单（canonical schema）；本文是人类可读原则定义 |
| `../01_global_architecture_diagram/global_capability_heatmap.md` | 自动生成的热力图快照（派生数据），以本文档定义的