---
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
status: active
---

# L01 — 基础设施层（Infrastructure）

**职责**：消息队列、缓存、数据库连接池、对象存储、API 网关等底层基础设施。也包括 Vibe Coding 双管线、脚本系统、任务卡系统等 AI 辅助开发基础设施。

**功能域**：infra（基础设施）、observability（容量保障）

**代码对应**：`src/zephyr/l01_infrastructure/`

**已登记模块**（详见 `../module-registry.yaml`）：

| module_id | 名称 | 状态 | 优先级 |
|-----------|------|------|:--:|
| MOD-INF-001 | capacity-assurance | approved | P0 |
| MOD-INF-002 | runtime-integration | approved | P0 |
| MOD-INF-003 | task-card-kms | **retired** | P1 |
| MOD-INF-004 | vibe-coding-pipelines | **retired** | P0 |
| MOD-INF-005 | script-system | approved | P0 |
| MOD-INF-006 | task-system | approved | P0 |
| MOD-KB-001 | knowledge-base | approved | P0 |
| MOD-MASTER-001 | master-blueprint | draft | P0 |
| MOD-INF-007 | gate-engine | draft | P0 |
| MOD-INF-008 | context-engine | draft | P0 |
| MOD-INF-009 | pipeline | draft | P0 |
| MOD-INF-010 | feedback-loop | draft | P0 |
| MOD-INF-011 | vector-memory | draft | P1 |
| MOD-INF-012 | database | draft | P1 |
| MOD-INF-013 | mcp-servers | draft | P1 |
| MOD-INF-014 | llm-security | draft | P2 |
| MOD-INF-015 | system-telemetry | draft | P2 |
| MOD-INF-016 | shared-core | draft | P2 |
| MOD-INF-017 | code-dedup-engine | draft | P2 |

**模块登记**：见 `../module-registry.yaml`，按 `layer: "L01"` 或 `layer: "cross_layer"` 过滤。

## 责任声明（Single Responsibility）

本目录只存放：**L01 基础设施层 — AI 基础设施（容量保障 / 运行时集成 / 任务系统 / 脚本系统 / 知识库 / 门禁引擎 / 上下文引擎 / 管线 / 反馈循环 / 向量记忆 / 数据库 / MCP服务 / LLM安全 / 遥测 / 共享基础设施）**。

## 文件清单

| 文件 | 说明 |
|------|------|
| index.md | 本层级索引（唯一真源） |

## 排除规则（不应放入本目录的内容）

- ❌ 非 C 轨业务层文档 → `_b_track_interfaces/ 或 01_policies_and_standards/`

## 父级目录

- 父级：[03_modules](../index.md)
