---
module_id: GOV-043
doc_type: index
status: Active
version: 3.0.0
generated: '2026-06-23'
depends_on:
- target: EA-INDEX
  at: §子目录
  why: 顶层EA索引——architecture_model为EA抽屉子目录
title: Architecture Model
ttl: permanent
---
# Architecture Model — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**架构模型YAML**——`domains`（52域索引，真源depgraph.db）、`contracts/`（跨域契约）、`events/`（领域事件）、`cross_cutting/`（横切）、`domain/`（DDD）、`frontend/`（前端）、`scripts/`（脚本）、`technology/`（技术栈）、`infra/`（基础设施骨架，planned）。

> **§2.1裁定（2026-06-22）**：52域是唯一物理分类体系，14层（L00-L13）降级为域的`layer_id`属性。旧的`layers/l00-l13-*.yaml`文件已废弃，信息合并入depgraph.db域定义。结构化数据从depgraph.db派生，禁止在MD中硬编码会变化的数字。

## 分区管理约定

**铁律**（定义在`index.yaml`顶部）：
1. `index.yaml`中每个分区必须有对应的YAML文件——不允许"虚分区"
2. `status: planned`的骨架文件是合法状态——不是bug，是TOGAF渐进式填充

## 文件清单

| 文件/目录 | 说明 |
|-----------|------|
| `index.yaml` | 全部分区的索引 + 52域清单 + 分区管理约定 + global_stats |
| `module_id_registry.yaml` | 模块ID注册表 |
| `domains` | **52域物理分类唯一真源**——depgraph.db domains表 |
| `contracts/` | 跨域数据契约CTR-001~006（P0）+ CTR-P1-001~013（P1）+ OCP + EXT + AI-GOV |
| `events/` | 22条领域事件 |
| `cross_cutting/` | 运行平面 + 不变量 + 能力热力图（52域×10能力域矩阵） |
| `domain/` | DDD战术模式 |
| `frontend/` | 前端模型FE-L1~L4 |
| `scripts/` | 治理/审计脚本模型 |
| `technology/` | 技术雷达43条 + Vibe Coding基础设施17项 |
| `infra/` | core-services（6模块）+ shared-infra（5模块），planned |

## 废弃分区（§2.1裁定后移除）

| 废弃分区 | 废弃原因 |
|----------|---------|
| `layers/l00-l13-*.yaml` | 14层降级为域属性，信息合并入depgraph.db域定义 |

## 排除规则（不应放入本目录的内容）

- ❌ .md架构视图文档 → `02_enterprise_architecture/target_architecture/（上层）`

## 父级目录

- 父级：[target_architecture](../index.md)
