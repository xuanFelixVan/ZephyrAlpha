---
module_id: "MOD-INF-009"
title: "Task Pipeline 蓝图 — M1-M11 双管线路由"
doc_type: blueprint
status: draft
version: "0.1.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_1_partial
summary: "ZephyrAlpha Task Pipeline 蓝图——定义 M1-M11 双管线架构：A区(M1-M5)生产管线 + B区(M6-M11)审计管线。决定每个任务用哪个 AI 模型、哪个 sandbox 配置、哪个门禁组合。决策树依据 GOV-AI-002 模型路由策略。对标 K8s Scheduler（Pod→Node路由）+ CI/CD Pipeline（Stage门控）。"
tags: [pipeline, task-pipeline, m1-m11, dual-pipeline, model-routing, pipeline-orchestrator, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-MASTER-001", at: "§2.7", why: "CT-PIPE-ORC-001 集成契约——Pipeline→Orc路由决策"}
  - {target: "MOD-INF-006", at: "§5", why: "任务系统——M1-M11节点的任务消费方"}
  - {target: "GOV-AI-002", at: "全篇", why: "模型路由策略——Pipeline决策树依据"}
  - {target: "architecture-model/layers/b_pipeline.yaml", at: "全篇", why: "Pipeline YAML SSoT——本蓝图真源"}
---

# Task Pipeline 蓝图 — M1-M11 双管线路由

> **module_id**: MOD-INF-009 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_pipeline.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_pipeline.yaml)。
> 代码落位：`src/zephyr/pipeline/`（2 个 .py 文件 + models.py + orchestrator）。

> **对标**：K8s Scheduler（Pod→最适合的Node）+ CI/CD Pipeline（Stage门控：build→test→deploy）+
> GitHub Actions `jobs.<job_id>.runs-on`（任务→执行环境路由）。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-009 |
| 代码落位 | `src/zephyr/pipeline/` |
| 核心职责 | 决定"这个任务用什么模型 + 什么沙箱 + 什么门禁" |

### 1.2 核心职能（一句话）

**Pipeline 是任务的调度中心**——每个 TaskCard 进入管线 → Pipeline 根据任务类型/优先级/复杂度 → 匹配到 M1-M11 的具体节点 → 分配执行模型 + sandbox + gate_profile。

大白话：Pipeline 就是"任务快递分拣中心"。快递（任务）来了后，分拣员（Pipeline）看"这是生鲜（P0审计）还是普通包裹（文档写作）"——生鲜走冷链（M3 Opus复审路线），普通包裹走普通物流（M6 Claude路线）。

---

## 2. M1-M11 双管线架构

### 2.1 A区：生产管线（M1-M5）

| 节点 | 模型 | Sandbox | Gate | 适用 |
|:---:|------|:---:|:---:|------|
| **M1** | Opus 4.5 | full | full_g0_g7 | 高复杂度 MODEL_BUILD |
| **M2** | GPT-5.2 | standard | pre_commit_only | 标准 MODEL_BUILD |
| **M3** | Opus 4.5 复审 | audit | full_g0_g7 | P0 AUDIT |
| **M4** | Claude 4.5 Sonnet | audit | post_exec_only | 标准 AUDIT |
| **M5** | GPT-5.2 | full | full_g0_g7 | 核心层 DOC_WRITE/REFACTOR |

### 2.2 B区：审计管线（M6-M11）

| 节点 | 模型 | Sandbox | Gate | 适用 |
|:---:|------|:---:|:---:|------|
| **M6** | Claude 4.5 Sonnet | standard | pre_commit_only | 普通层 DOC_WRITE/REFACTOR |
| **M7** | Claude 4.5 Haiku | restricted | none | 低优先级批量任务 |
| **M8** | Gemini 3.0 Pro | standard | post_exec_only | 多模态任务（如有截图） |
| **M9** | Qwen 3 Max | standard | post_exec_only | 中文繁重任务 |
| **M10** | GLM 5.1 | restricted | none | 草稿/实验性任务 |
| **M11** | Claude 4.5 Haiku | restricted | none | 自动修复 AUTO_FIX |

---

## 3. 路由决策树

```yaml
routing_decision_tree:
  input: "TaskCard { task_type, priority, target_layer, estimated_complexity }"
  output: "PipelineNode { node_id, execution_model, sandbox_profile, gate_profile }"

  rules:
    - condition: "task_type == MODEL_BUILD AND estimated_complexity == HIGH"
      route: "M1 (Opus 4.5 + full sandbox + full_g0_g7)"

    - condition: "task_type == MODEL_BUILD"
      route: "M2 (GPT-5.2 + standard sandbox + pre_commit_only)"

    - condition: "task_type == AUDIT AND priority == P0"
      route: "M3 (Opus 4.5 复审 + audit sandbox + full_g0_g7)"

    - condition: "task_type == AUDIT"
      route: "M4 (Claude 4.5 Sonnet + audit sandbox + post_exec_only)"

    - condition: "task_type ∈ {DOC_WRITE, REFACTOR} AND target_layer ∈ {L00,L01,L10}"
      route: "M5 (GPT-5.2 + full sandbox + full_g0_g7)"

    - condition: "task_type ∈ {DOC_WRITE, REFACTOR}"
      route: "M6 (Claude 4.5 Sonnet + standard sandbox + pre_commit_only)"

    - condition: "task_type == AUTO_FIX"
      route: "M11 (Claude 4.5 Haiku + restricted + none)"
```

---

## 4. Pipeline 输出模型

```python
@dataclass
class PipelineNode:
    node_id: str          # "M1" ~ "M11"
    execution_model: str  # "opus-4.5" | "gpt-5.2" | ...
    sandbox_profile: str  # "full" | "standard" | "audit" | "restricted"
    gate_profile: str     # "full_g0_g7" | "pre_commit_only" | "post_exec_only" | "none"

@dataclass
class PipelineResult:
    node: PipelineNode
    routing_reason: str   # 为什么路由到这个节点（可审计）
```

---

## 5. 与 Orchestrator 的集成（CT-PIPE-ORC-001）

> 详见总蓝图 [MOD-MASTER-001 §2.7](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md)。

```
Orc.create_task(task_card)
      ↓
Pipeline.route(task_card) → PipelineNode
      ↓
Orc.assign_session(node)
```

---

## 6. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 0 | models.py + pipeline_orchestrator.py 骨架 | ✅ implemented |
| Phase 1 | M1-M11 完整路由逻辑 + GOV-AI-002 决策树落地 | 📋 Backlog |
| Phase 2 | 动态调路由——FLE反馈→调整复杂度估计→重新路由 | 📋 Backlog |

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 任务管线——pipeline_orchestrator+models骨架完成

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pipeline/models.py` | ✅ 已实现 | |
| `src/zephyr/pipeline/pipeline_orchestrator.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_pipeline_orchestrator.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 0.1.0 | 初始创建——从 b_pipeline.yaml SSoT 派生。双管线(M1-M5 A区 + M6-M11 B区) + 路由决策树 + CT-PIPE-ORC-001 集成。 |
