---
module_id: AI-ENG-PIP-001
title: Task Pipeline Service Interface / 任务双管线服务接口规范
doc_type: service_interface_spec
status: Active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
created_date: "2026-05-06"
last_updated: "2026-05-06"
ttl: permanent
template_source: "vector-memory-service-interface.md（B 轨接口目录结构对齐）"
truth_source:
  - "03_modules/_cross_layer/pipeline/blueprint.md（MOD-INF-009 — 详细设计与 CT 锚点；Phase 5 真源）"
  - "architecture-model/layers/b_pipeline.yaml（Pipeline YAML SSoT）"
related_adrs: []
integration_points:
  - "Agent Orchestrator（downstream，任务调度与状态机消费 Pipeline 路由决策）"
  - "LLM Security Gateway MOD-INF-014（Pipeline L1/L3 输入输出检测）"
  - "Task System MOD-INF-006（M1–M11 节点与任务卡消费方）"
  - "Database MOD-INF-012（deferred queue / task_repo 查询）"
tags:
  - pipeline
  - m1-m11
  - b-track
  - service-interface
depends_on:
  - target: AI-ENG-ORC-001
    at: "§编排边界"
    why: "Orchestrator 消费本接口的调度/decision surface"
mod_master_blueprint: "MOD-MASTER-001"
mod_master_contracts:
  - "CT-PIPE-ORC-001"
---

# Task Pipeline Service Interface / 任务双管线服务接口规范

> **定位**：B 轨第 6 份核心服务接口——与 VMS/CTX/ORC/FLE/LSG 并列。权威设计细节在 **`MOD-INF-009`** 蓝图；本文件给出**稳定对外边界**（消费者、契约编号、真源指针），避免在长蓝图中检索接口轮廓。

---

## 1. 读者指南

| 章节 | 内容 |
|------|------|
| §1 | 服务职责与真源 |
| §2 | 对外抽象（命名 / 协议形态） |
| §3 | 与集成总蓝图契约对齐 |

---

## 2. 服务职责（一句话）

**Task Pipeline** 负责任务在 **A 区（M1–M5）** 与 **B 区（M6–M11）** 之间的**模型路由、门禁组合、sandbox 配置与降级策略**，使每个 `TaskCard` 在执行路径上绑定一致的策略剖面。

---

## 3. 对外抽象（实现无关）

- **输入**：已通过 `MOD-INF-006` / Gate 的 `TaskCard`（或等价 task 句柄）+ 组织策略（`GOV-AI-002` 路由树）。
- **输出**：**路由决策**（目标模型 profile、管线区段、门禁集合、预算钩子）供 Orchestrator / Runtime 执行。
- **失败语义**：对齐 **fail-closed / degraded mode** 由 `MOD-INF-014`、`MOD-INF-001` 在链路下游执行；本层只产出**结构化决策或阻断原因码**。

具体 **Pydantic / Protocol** 签名以 **`MOD-INF-009` §接口契约** 为准；蓝图真源 `docs/03_modules/_cross_layer/pipeline/blueprint.md`；代码落位 `src/zephyr/pipeline/`。

---

## 4. 与 MOD-MASTER-001 契约对齐

| 契约 / 引用 | 说明 |
|-------------|------|
| `CT-PIPE-ORC-001` | Pipeline ↔ Agent Orchestrator 集成边界 |
| `GOV-AI-002` | 模型路由策略真源 |

---

## 5. 变更同步

| 变更类型 | 必须先更新的真源 |
|----------|------------------|
| 路由阶段 / M1–M11 语义 | `MOD-INF-009`（`_cross_layer/pipeline/blueprint.md`）+ `b_pipeline.yaml` |
| 与 Orchestrator 边界 | 本文件 §2 + `_b_track_interfaces/agent-orchestrator-interface.md` |
