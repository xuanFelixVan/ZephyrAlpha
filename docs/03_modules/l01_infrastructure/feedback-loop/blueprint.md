---
module_id: "MOD-INF-010"
title: "Feedback Loop Engine 蓝图 — collect→detect→dispatch 自我改进闭环"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_1_partial
summary: "ZephyrAlpha Feedback Loop Engine 蓝图——定义系统自我改进闭环：collect_metric→detect_anomaly→dispatch_action。SQLite时序存储 + EMA异常检测 + 4种action_type（ESCALATE/REPAIR/NOTIFY_OWNER/ADJUST_GATE）。FLE通过Protocol适配器fire-and-forget调用其他系统，防止循环依赖。fitness_functions.py 被 l08 dashboard 消费。对标 ITIL Continual Improvement + K8s HPA (自动扩缩) + Netflix Chaos Monkey (自动恢复)。"
tags: [feedback-loop, fle, self-improvement, anomaly-detection, metrics, auto-evolution, fitness-functions, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-MASTER-001", at: "§2.5", why: "CT-FLE-ORC-001 集成契约——FLE→Orc异常调度"}
  - {target: "MOD-MASTER-001", at: "§4", why: "全局状态传播链——FLE位置"}
  - {target: "MOD-INF-006", at: "§4", why: "任务系统——FLE异常检测的输入源+输出目标"}
  - {target: "architecture-model/layers/b_feedback_loop.yaml", at: "全篇", why: "FLE YAML SSoT——本蓝图真源"}
---

# Feedback Loop Engine 蓝图 — 自我改进闭环

> **module_id**: MOD-INF-010 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_feedback_loop.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_feedback_loop.yaml)。
> 代码落位：`src/zephyr/feedback_loop/`（6 个 .py 文件，bounded_context=true）。

> **对标**：ITIL Continual Improvement（持续改进7步法）+ K8s HPA（Horizontal Pod Autoscaler——负载触发自动扩缩）+
> Netflix Chaos Monkey（自动检测+恢复）+ Amazon DevOps Guru（ML驱动异常检测）。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-010 |
| 代码落位 | `src/zephyr/feedback_loop/` |
| 边界上下文 | bounded_context: true（独立领域模型）|
| 伞盖层 | l12（可观测层覆盖）|
| 核心职责 | 系统自我调节——"发现问题 → 分析根因 → 调度修复" |

### 1.2 核心职能（一句话）

**FLE 是系统的免疫系统**——持续采集全系统指标 → 检测异常模式 → 自动调度修复动作。不生产内容，只修复"系统自身的问题"。

大白话：人发烧是免疫系统在报警。FLE 就是 ZephyrAlpha 的免疫系统——脚本 exit 2 持续 3 次 = "系统在发烧" → FLE 检测到 → 自动通知 Owner "系统可能感染了"。

### 1.3 防循环依赖设计

FLE 通过 **Protocol 适配器** fire-and-forget 调用其他系统（单向依赖）：

```
FLE ──(Protocol适配器)──→ Orchestrator
FLE ──(Protocol适配器)──→ Gates
FLE ──(Protocol适配器)──→ GPT-5.2 (通知)

Orchestrator ──X──→ FLE  （禁止反向依赖）
```

---

## 2. 三阶段流水线

```
Telemetry (l12) → metrics
      ↓
┌─────────────────┐
│ COLLECT_METRIC   │  周期轮询 30s → 收集全系统指标
│ metrics_collector│
└────────┬────────┘
         │ MetricSnapshot { task_failure_rate, gate_fail_rate, script_exit_codes, ... }
         ▼
┌─────────────────┐
│ DETECT_ANOMALY   │  EMA指数移动平均 vs 历史基线 → 检测偏离
│ eval_harness     │
└────────┬────────┘
         │ AnomalyReport { type, severity, affected_system, confidence }
         ▼
┌─────────────────┐
│ DISPATCH_ACTION  │  根据 anomaly type → 选择 ESCALATE/REPAIR/NOTIFY_OWNER/ADJUST_GATE
│ auto_evolution   │  → fire-and-forget 发送到目标系统
└─────────────────┘
```

### 2.1 Collect — metrics_collector.py + feedback_collector.py

```python
class MetricSnapshot:
    task_failure_rate: float      # 任务失败率
    gate_fail_rate: float         # 门禁阻断率
    script_exit_distribution: dict  # {dimension: {exit_0: N, exit_1: N, ...}}
    context_token_usage: float    # Token 使用率
    mtbf: float                   # Mean Time Between Failures
    timestamp: datetime
```

### 2.2 Detect — eval_harness.py

```python
# EMA (Exponential Moving Average) 异常检测
def detect_anomaly(current: MetricSnapshot, baseline: EMA) -> AnomalyReport:
    deviation = abs(current - baseline) / baseline.std_dev
    if deviation > 3.0:
        return AnomalyReport(type="SPIKE", severity="CRITICAL", ...)
    if deviation > 2.0:
        return AnomalyReport(type="DRIFT", severity="HIGH", ...)
```

### 2.3 Dispatch — auto_evolution.py + evolution_engine.py

四种 action_type（与 CT-FLE-ORC-001 对齐）：

| Action | 触发条件 | 目标系统 | Severity |
|------|------|------|:---:|
| **ESCALATE** | 任务失败率 3x > 基线 | GPT-5.2 → Owner 飞书 | P0_immediate |
| **REPAIR** | 特定维度脚本持续 exit 2 | Orchestrator → 创建 OPS 任务 | P1_24h |
| **NOTIFY_OWNER** | D12 幻觉检测连续 3 次 fail | Orchestrator → 暂停调度 | P0_immediate |
| **ADJUST_GATE** | 门禁假阳性率 > 5%（连续一周）| Gates → 建议调阈值（需Owner确认）| P2_72h |

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `metrics_collector.py` | Collect——全系统指标采集（30s轮询）|
| `feedback_collector.py` | Collect——任务级别反馈收集 |
| `eval_harness.py` | Detect——EMA异常检测 + 基线训练 |
| `auto_evolution.py` | Dispatch——自动进化调度（action dispatch）|
| `evolution_engine.py` | Dispatch——进化引擎（action执行追踪）|
| `fitness_functions.py` | 系统适应度函数——被 l08 dashboard 消费 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 6 文件骨架 + metrics_collector + fitness_functions | ✅ implemented |
| experimental | 完整的 collect→detect→dispatch 链路 + EMA基线训练 | 📋 Backlog |
| beta | ADJUST_GATE 自动阈值建议 + dashboard fitness展示 | 📋 Backlog |

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 反馈闭环——6文件骨架+metrics_collector+fitness_functions已实现

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/feedback_loop/auto_evolution.py` | ✅ 已实现 | |
| `src/zephyr/feedback_loop/eval_harness.py` | ✅ 已实现 | |
| `src/zephyr/feedback_loop/evolution_engine.py` | ✅ 已实现 | |
| `src/zephyr/feedback_loop/feedback_collector.py` | ✅ 已实现 | |
| `src/zephyr/feedback_loop/fitness_functions.py` | ✅ 已实现 | |
| `src/zephyr/feedback_loop/metrics_collector.py` | ✅ 已实现 | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_metrics_collector.py` | ❌ 未实现 | |
| `tests/unit/test_fitness_functions.py` | ✅ 已实现 | |
| `tests/unit/test_feedback_collector.py` | ✅ 已实现 | |
| `tests/unit/test_auto_evolution.py` | ✅ 已实现 | |
| `tests/unit/test_evolution_engine.py` | ✅ 已实现 | |
| `tests/unit/test_eval_harness.py` | ✅ 已实现 | |
| `tests/integration/test_evolution_e2e.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 6. 依赖关系（结构化）

| 依赖目标 | 关系类型 | 为什么 |
|------|:--:|------|
| MOD-INF-006 (Task System) | data_source | 收集任务执行结果 feedback_collector |
| MOD-INF-007 (Gate Engine) | feedback_to | ADJUST_GATE 建议调门禁阈值 |
| MOD-INF-012 (Database) | persistence | FLE 结果写入 SQLite → CT-FLE-DB-001 |
| MOD-INF-015 (Telemetry) | emit_to | metrics/logs/traces → CT-TELE-FLE-001 |
| MOD-INF-003 (Orchestrator) | action_target | REPAIR → 创建 OPS 任务；NOTIFY_OWNER → 暂停调度 |
| MOD-INF-009 (Pipeline) | feedback_to | 反馈→调复杂度估计→重新路由 |
| L08 (Human-AI Interface) | dashboard | fitness_functions → Dashboard 展示 |
| `architecture-model/layers/b_feedback_loop.yaml` | ssoT | FLE YAML canonical source |

## 7. 产出物存放目录

| 产出物 | 路径 |
|------|------|
| 指标采集器 | `src/zephyr/feedback_loop/metrics_collector.py` |
| 反馈采集器 | `src/zephyr/feedback_loop/feedback_collector.py` |
| 异常检测 | `src/zephyr/feedback_loop/eval_harness.py` |
| 进化调度 | `src/zephyr/feedback_loop/auto_evolution.py` |
| 进化引擎 | `src/zephyr/feedback_loop/evolution_engine.py` |
| 适应度函数 | `src/zephyr/feedback_loop/fitness_functions.py` |
| FLE 测试 | `tests/unit/test_*.py` + `tests/integration/test_evolution_e2e.py` |

## 8. 集成目标

| 集成目标 | 状态 | 验证方式 |
|------|:--:|------|
| collect→detect→dispatch 完整链路 | 📋 Backlog | 端到端测试 |
| EMA 基线训练 + 异常检测 | ✅ scaffold | eval_harness scaffold |
| ADJUST_GATE 自动阈值建议 | 📋 Backlog | beta Phase |
| Dashboard fitness 展示 | ✅ scaffold | fitness_functions 被 l08 consumer |

## 9. 需要更新的相关内容

当本蓝图变更时，同步更新：
1. `docs/03_modules/blueprint-registry.yaml` — 版本号和完整度
2. `src/zephyr/l08_human_ai_interface/dashboard/components/fitness_functions.py` — 若 metric schema 变更
3. `docs/03_modules/_master-blueprint/blueprint.md` — MOD-MASTER-001 CT-FLE-* 契约

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 0.1.0 | 初始创建——从 b_feedback_loop.yaml SSoT 派生。三阶段流水线 + 4种action_type + Protocol防循环依赖 + EMA异常检测。 |
