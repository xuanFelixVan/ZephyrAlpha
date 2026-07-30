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
> 派生数据（域成熟度快照、热力图可视化）由 depgraph 生成器自动生成到 `../01_global_architecture_diagram/global_capability_heatmap.md`。

## 1. 业界对标

ZephyrAlpha 对标业界共识的 5 档能力成熟度模型（CMMI-aligned），定期刷新（当前为季度，可调）。

> 注：各机构内部能力地图产品名属易变实现细节，不在此记录；仅保留"5 档模型"的结构性结论。

## 2. 五档成熟度模型

### 2.1 档位定义

| 档位 | 名称 | 定义 |
|:---:|------|------|
| **L0** | 缺失 | 能力完全不存在，无设计无代码 |
| **L1** | 设计 | 仅有设计文档/蓝图，无代码 |
| **L2** | 草稿 | 有原型代码，未集成 |
| **L3** | 可用 | 代码可用但未生产验证 |
| **L4** | 生产级 | 生产环境稳定运行 |
| **L5** | 顶级机构对标 | 达到 Goldman/BlackRock 水平 |

### 2.2 评分规则

- **域成熟度** = 该域所有节点的最高成熟度
- **能力域成熟度** = 该能力域下所有域成熟度的加权平均（按节点数加权）

## 3. 能力域划分原则

能力域采用"7 业务 + 3 横切"的二维分类。**能力域的永恒定义真源是 [business_principles.md §2](business_principles.md) 的 C1-C7（业务能力域）+ CC1-CC3（横切能力域）框架**，本文档不重复列举，避免真源分裂与顺序漂移。

能力域到具体物理域的映射由 `architecture_model/cross_cutting/capability_heatmap.yaml`（canonical schema）定义，随域增减而演进。

## 4. 季度 Review 机制

### 4.1 刷新流程

1. 运行 depgraph 生成器刷新域成熟度快照
2. 架构师逐域评估 L4/L5 达标情况
3. 更新差距表
4. 识别 P0/P1/P2 短板 → 纳入下季度任务卡

### 4.2 刷新频率

- **季度例行**：每 3 个月（决策快照，可调）
- **事件驱动**：真实资金接入 / 架构重大变更

## 5. 目标状态定义

| 里程碑 | 目标 | 触发条件 |
|--------|------|---------|
| **T1** | 真实资金接入 | 模拟盘稳定运行 3 个月（决策快照，可调） |
| **T3** | AI 自治升格 | 核心 AI 自治域全部达 L4（决策快照，具体域见 `capability_heatmap.yaml`） |
| **T-ENDGAME** | 顶级机构对标 | 全域能力 L4+，若干能力域达 L5（决策快照，具体目标见 `capability_heatmap.yaml`） |

## 6. 与其他文档的关系

| 其他文档 | 关系 |
|---|---|
| `architecture_principles.md` | 本文是总纲 §4 核心架构决策的能力成熟度子原则 |
| `architecture_model/cross_cutting/capability_heatmap.yaml` | YAML 是机器可读能力清单（canonical schema）；本文是人类可读原则定义 |
| `../01_global_architecture_diagram/global_capability_heatmap.md` | 自动生成的热力图快照（派生数据），以本文档定义的档位框架为准 |