---
module_id: GOV-043
doc_type: index
status: Active
version: 2.0.0
generated: '2026-05-02'
depends_on:
- target: EA-INDEX
  at: §子目录
  why: 顶层 EA 索引——architecture-model 为 EA 抽屉子目录，引用顶层抽屉一览
title: Architecture Model
---

# Architecture Model — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**架构模型 YAML**——`layers/`（14 层层定义）、`contracts/`（跨层契约）、`events/`（领域事件）、`cross-cutting/`（横切）、`domain/`（DDD）、`frontend/`（前端）、`scripts/`（脚本）、`technology/`（技术栈）、`infra/`（基础设施骨架，planned）。

## 分区管理约定

**铁律**（定义在 `_index.yaml` 顶部）：
1. `_index.yaml` 中每个分区必须有对应的 YAML 文件——不允许"虚分区"
2. `status: planned` 的骨架文件是合法状态——不是 bug，是 TOGAF 渐进式填充

新 AI session 读此目录时：如果 `_index.yaml` 的某个分区 `path` 指向的文件不存在 → 🔴 这是一致性破坏。如果文件存在但 `status: planned` → 🟢 正常。

## 文件清单

| 文件/目录 | 说明 |
|-----------|------|
| `_index.yaml` | 全部分区的索引 + 分区管理约定 + global_stats |
| `module_id_registry.yaml` | 模块 ID 注册表（68 个已注册 ID，含 active/draft/merged/deprecated 多种状态） |
| `layers/` | L00-L13 + shared，14 层业务模块定义 |
| `contracts/` | 跨层数据契约 CTR-001~006（P0）+ CTR-P1-001~013（P1）+ OCP-001~003 + EXT-001~004 + AI-GOV-001~003 |
| `events/` | 22 条领域事件 |
| `cross-cutting/` | 运行平面 + 不变量 + 能力热力图（10 域：C1~C7 业务 + CC1~CC3 横切） |
| `domain/` | DDD 战术模式 |
| `frontend/` | 前端模型 FE-L1~L4 |
| `scripts/` | 治理/审计脚本模型 |
| `technology/` | 技术雷达 43 条 + Vibe Coding 基础设施 17 项 |
| `infra/` | **2026-05-02 新增**——core-services（6 模块）+ shared-infra（5 模块），均为 status: planned |
| `scripts/check_architecture_gates.py` | CI 门禁脚本（GATE-01~08；**Note:已迁移至 `scripts/governance/d5_architecture/`**，此处仅保留索引引用）|
| ~~`architecture_endgame_locked.md`~~ | **已移出**（2026-05-03）：.md 治理文档不属于 YAML-only 目录，已迁至 `target-architecture/architecture_endgame_locked.md` |

## 排除规则（不应放入本目录的内容）

- ❌ .md 架构视图文档 → `02_enterprise_architecture/target-architecture/（上层）`

## 父级目录

- 父级：[target-architecture](../index.md)
