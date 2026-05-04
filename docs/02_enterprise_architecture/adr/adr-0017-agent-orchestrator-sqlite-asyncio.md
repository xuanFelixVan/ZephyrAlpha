---
module_id: ADR-0017
doc_type: adr
title: Agent Orchestrator — SQLite + asyncio.Queue 起步，NATS 升级路径
version: 1.0.0
status: active
date: '2026-04-24'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0015
- ADR-0016
- ADR-0018
- ADR-0019
- ADR-0020
- ADR-0021
priority: P0
phase: Phase-1
tech_refs:
- TECH-07
- TECH-08
- TECH-09
- TECH-10
- TECH-11
supersedes_doc: archive/reorg-2026-04-24/08_ai_engineering/workflow-interface-contract.md
layer: L12
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags: [adr, vibe-coding]
summary: "**Vibe Coding 2.0 核心服务** Agent Orchestrator（SQLite + asyncio.Queue + enum 状态机 + 规则基幻觉检测）| accepted"
---

# ADR-0017: Agent Orchestrator — SQLite + asyncio.Queue 起步，NATS 升级路径

**状态**：Accepted
**日期**：2026-04-24
**决策者**：ZephyrAlpha-Owner
**优先级**：P0
**阶段**：Phase 1 首批上线

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-24

## 2. 背景与问题（Context）

### 2.1 问题陈述

原 `workflow-interface-contract.md`（2026-04-24 归档）只定义了"任务流转"抽象，没有落地实现。Vibe Coding 2.0 需要一个统一的 **Agent Orchestrator (Orc)** 承担：

- **任务队列**：ADR / 因子开发 / 回测 / Post-mortem 等任务的生命周期
- **状态机**：`pending → running → succeeded/failed/degraded/cancelled` 全部显式建模
- **Agent 调度**：Cursor / Trae 多 Agent 并行运行的协调
- **幻觉循环检测**：防止 AI 陷入"生成-回退-再生成"死循环
- **Agent 间通信**：共享状态 + 事件广播

### 2.2 设计目标

- 单人个人系统，Phase 1 并发任务 < 20，不需要重型消息队列
- 任务持久化（重启不丢）
- 所有任务都过 LSG + Sandbox 门禁
- FLE 可以通过 Protocol 调整 Orc 调度策略（限流 / 降级）

### 2.3 参考真源

- `vibe-coding-audit-merged.md §Kimi 10.6.2 Agent Orchestrator`
- `vibe-coding-audit-merged.md §Qwen 选型表 #7-11`
- `agent-orchestrator-interface.md v1.0.0`（850 行，B-a-3）

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：SQLite + asyncio.Queue + Python enum 状态机（轻量）✅

- **优点**：
  - 零外部依赖，单进程单机可跑
  - SQLite WAL 模式并发读写 OK（并发 < 100 写/s）
  - asyncio.Queue 天然与项目全异步栈一致
  - enum + dataclass 状态机可测试 + 可审计
- **缺点**：
  - 任务量 > 100/天 或实时通信 < 1s 时性能受限
  - 跨机器分布式不支持（Phase 1 单机无需）

### 方案 B：Celery + Redis + 独立 Worker 进程

- **优点**：业界事实标准，生态完善
- **缺点**：
  - Redis 独立服务，运维成本
  - Celery 对异步 Python 3.12 支持较新，坑多
  - 单人系统 overkill

### 方案 C：ARQ + Redis（Celery 的 asyncio 版）

- **优点**：异步原生，API 简洁
- **缺点**：仍需 Redis 独立服务
- **结论**：**保留为升级路径**（任务量 > 100/天触发）

### 方案 D：NATS JetStream

- **优点**：< 1s 实时通信，分布式
- **缺点**：Phase 1 不需要
- **结论**：**保留为 Phase 3+ 升级路径**

---

## 4. 决策（Decision）

**最终选择：方案 A — SQLite + asyncio.Queue + Python enum 状态机**

### 4.1 关键决策点

| 决策点 | 首选 | 备选 | 升级触发条件 |
|-------|------|------|-------------|
| **任务队列** | SQLite + asyncio.Queue | ARQ + Redis | 并发 RUNNING 任务 > 20（TECH-07 watchboard）|
| **状态机** | Python enum + dataclass | `transitions` 库 | 状态 > 15 个或嵌套需求 |
| **健康监控** | 内存 metrics + SQLite | Prometheus | Phase 2 运维栈升级 |
| **幻觉检测** | 规则引擎 + 阈值 | 轻量 ML | 漏检率 > 10%（TECH-09 watchboard）|
| **Agent 通信** | SQLite 共享状态表 | NATS JetStream | 实时延迟要求 < 1s |
| **并发原语** | `asyncio.Lock` + `filelock.FileLock`（跨进程）| — | — |
| **持久化路径** | `.runtime/sqlite/orchestrator.db` | — | — |

### 4.2 任务状态机

```
            submit()
                │
                ▼
        ┌──────────────┐
        │   pending    │
        └──────┬───────┘
               │ dispatch() (Orc 拉取)
               ▼
        ┌──────────────┐
        │   queued     │
        └──────┬───────┘
               │ Sandbox + LSG 门禁
               ▼
        ┌──────────────┐
        │   running    │◀───┐
        └────┬─────┬───┘     │ retry (< max_retries)
             │     │         │
    succeeded│     │failed───┘
             │     │
             │     │ hallucination_detected
             │     ▼
             │  ┌──────────────┐
             │  │  degraded    │ (FLE 降级信号)
             │  └──────────────┘
             │
             ▼
        ┌──────────────┐
        │  succeeded   │
        └──────────────┘

        (任何阶段可 cancelled)
```

### 4.3 幻觉检测规则集（Phase 1 基础版）

- **Rule-H01**：同一 `task_id` 生成相同代码片段 ≥ 3 次 → 标记幻觉循环
- **Rule-H02**：输出包含"As an AI / 抱歉 / 无法完成"等降级关键词 → 告警
- **Rule-H03**：工具调用连续 5 次返回空 → 暂停任务 + 人工介入
- **Rule-H04**：LSG L4 Pattern 告警累计 3 次/任务 → 强制 degraded

漏检率 > 10% 时升级为 **LLM-as-Judge**（TECH-09 watchboard）。

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **2-3 人日 Phase 1 MVP 上线**
- **零新外部依赖**：复用 SQLite + asyncio
- **可审计**：所有任务状态变更写入 `agent_actions` 表（供 §06-security §9 消费）
- **可升级**：OrchestratorProtocol 保证切 ARQ/NATS 零业务层改动

### 5.2 负面后果

- **任务量上限**：并发 RUNNING > 20 时需升级
- **跨机器分布式不支持**：Phase 1 单机可接受
- **幻觉检测规则基覆盖有限**：10% 漏检率是已知上限

### 5.3 未来重新评估触发条件

- **TECH-07**：并发 RUNNING 任务 > 20 → 升级 NATS JetStream
- **TECH-09**：幻觉漏检率 > 10% → 升级规则集 + LLM-as-Judge
- 跨机器需求（团队扩容）→ 升级分布式
- Phase 2 接入真实资金 → 任务必须带交易授权链

---

## 6. 落地动作（Implementation）

| # | 动作 | 物理位置 | 估时 |
|---|------|---------|:----:|
| 1 | `OrchestratorProtocol` 抽象基类 | `src/zephyr/orchestrator/protocol.py` | 0.5 天 |
| 2 | `TaskState` enum + dataclass 状态机 | `src/zephyr/orchestrator/state_machine.py` | 0.5 天 |
| 3 | SQLite schema + DAO | `src/zephyr/orchestrator/storage.py` | 0.5 天 |
| 4 | `InProcessOrchestrator` 主循环 | `src/zephyr/orchestrator/in_process.py` | 1 天 |
| 5 | 幻觉检测规则引擎 | `src/zephyr/orchestrator/hallucination.py` | 0.5 天 |
| 6 | Agent 调度 + Sandbox 集成（ADR-0018）| `src/zephyr/orchestrator/dispatcher.py` | 1 天 |
| 7 | LSG 前置校验集成（ADR-0020）| `src/zephyr/orchestrator/security_gate.py` | 0.5 天 |
| 8 | FLE Protocol 适配器 | `src/zephyr/orchestrator/fle_adapter.py` | 0.5 天 |
| 9 | P0 测试组（状态机 + 并发 + 幻觉）| `tests/orchestrator/test_p0.py` | 1 天 |

**总工时**：约 6 人日

---

## 7. 参考

- **真源**：`vibe-coding-audit-merged.md §Kimi 10.6.2` + `§Qwen 选型表 #7-11`
- **接口规范**：[`agent-orchestrator-interface.md v1.0.0`](../../03_modules/_b_track_interfaces/agent-orchestrator-interface.md)
- **归档旧契约**：`archive/reorg-2026-04-24/08_ai_engineering/workflow-interface-contract.md`
- **架构位置**：[`03-application-architecture.md §4A.1`](../target-architecture/03-application-architecture.md)
- **技术选型**：[`technology-landscape.yaml TECH-07~11`](../target-architecture/architecture-model/technology/technology-landscape.yaml)
- **相关 ADR**：ADR-0015（CE 消费者）/ ADR-0016（VMS 消费者）/ ADR-0018（Sandbox 配套）/ ADR-0019（FLE 通知方）/ ADR-0020（LSG 前置）
- **外部**：[SQLite WAL docs](https://www.sqlite.org/wal.html) / [asyncio Queue](https://docs.python.org/3/library/asyncio-queue.html)

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：SQLite + asyncio.Queue + enum 状态机；规则基幻觉检测；B-e-4 产出。 |
