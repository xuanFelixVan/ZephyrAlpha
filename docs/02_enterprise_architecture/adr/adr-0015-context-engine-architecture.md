---
module_id: ADR-0015
doc_type: adr
title: "Context Engine 架构与技术选型"
version: "1.0.0"
status: active
date: "2026-04-24"
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs: ["ADR-0016", "ADR-0017", "ADR-0019", "ADR-0020", "ADR-0021"]
priority: P0
phase: Phase-1
tech_refs: ["TECH-01", "TECH-02", "TECH-03"]
layer: L12
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: null
related_rationale: ""
related_open_questions: []
tags: [adr, vibe-coding]
summary: **Vibe Coding 2.0 核心服务** Context Engine 架构（NetworkX + Qwen2.5-3B ONNX + MCP 能力协商）| accepted
---

# ADR-0015: Context Engine 架构与技术选型

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

Vibe Coding 2.0 五大核心服务中，Context Engine（CE）是"AI 编码的中枢神经"，负责**上下文 build / compress / validate / inject** 四段流水线。当前（Phase 0 末）系统没有统一的上下文编排层，导致：

- AI IDE（Cursor / Trae / Claude Desktop）各自拉取上下文，相互独立不共享
- Token 预算控制碎片化，常见超限（单次 > 50K）或稀疏（< 5K）两极分化
- 无法基于 Feedback Loop Engine 的异常信号**动态调整**上下文策略

### 2.2 设计目标

- **统一入口**：所有 AI IDE 通过 MCP 协议接入，CE 是唯一上下文生产者
- **Token 预算**：硬约束 `opus_calls_today ≤ 10`（见 `session-carryover-schema.md`），CE 必须智能压缩
- **可降级**：LLM 压缩失败 / VMS 不可用时必须有规则基后备路径（DEGRADE-*）
- **可反馈**：FLE 检测到"幻觉 / 冗余 / 截断"时能调整 CE 策略

### 2.3 参考真源

- `vibe-coding-audit-merged.md §Kimi 9.7 Context Engine 核心架构`
- `vibe-coding-audit-merged.md §Qwen 选型表 #1-3`
- `context-engine-interface.md v1.0.0`（B-a-2 产出，814 行）

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：NetworkX + JSON + 本地 LLM 压缩（轻量栈）✅

- **优点**：
  - NetworkX 节点 < 1000 时 < 50ms 查询延迟（本项目 Phase 1 估计 300-600 节点）
  - JSON 持久化 / 可版本化 / git diff 友好
  - 本地 Qwen2.5-3B-Instruct ONNX（int8 量化 ~2GB）可离线运行
  - 零外部服务依赖，与 SSoT 原则一致
- **缺点**：
  - 节点数 > 50K 时性能退化（Phase 3+ 风险）
  - 本地 LLM 压缩质量 < GPT-4 ~15%

### 方案 B：Neo4j + LangChain + OpenAI API（重栈）

- **优点**：节点数无上限；压缩质量业界最高
- **缺点**：
  - Neo4j 独立服务，个人系统运维负担
  - LangChain 依赖链膨胀（100+ 间接依赖）
  - OpenAI API 破坏离线原则 + 花费不可控（Opus 10 次 / 天硬约束会冲突）
- **结论**：**否决**

### 方案 C：自建图引擎 + 规则摘要（极简栈）

- **优点**：全可控
- **缺点**：图遍历算法复杂度高，单人维护成本不现实；压缩质量远低于 LLM

---

## 4. 决策（Decision）

**最终选择：方案 A — NetworkX 3.2 + JSON + Qwen2.5-3B-Instruct ONNX（int8）**

### 4.1 关键决策点

| 决策点 | 首选 | 备选 | 升级触发条件 |
|-------|------|------|-------------|
| **entity-graph 存储** | NetworkX 3.2 + JSON | Neo4j Community | 节点数 > 50K 持续 7 天（TECH-01 watchboard）|
| **向量检索入口** | VMS 调用（见 ADR-0016）| — | — |
| **文本压缩** | Qwen2.5-3B-Instruct ONNX int8 | Qwen2.5-7B 或外部 API | 压缩延迟 P99 > 5s 持续 7 天（TECH-02 watchboard）|
| **压缩降级** | 规则基（首段 + 标题 + 最近 k 条）| — | LLM 服务不可用时自动启用 |
| **并发原语** | `asyncio.Lock`（进程内）+ `filelock.FileLock`（跨进程）| — | — |

### 4.2 架构位置

```
AI IDE (Cursor/Trae/Claude Desktop)
    │ MCP 协议
    ▼
┌───────────────────────────────────┐
│  LSG (ADR-0020) — 前置安全闸      │
└────────────────┬──────────────────┘
                 ▼
┌───────────────────────────────────┐
│   Context Engine (本 ADR)         │
│   build → compress → validate     │
│               → inject            │
└────┬───────────────┬──────────────┘
     │ 检索           │ 策略调整
     ▼               ▲
┌──────────┐   ┌─────┴──────────────┐
│ VMS      │   │ FLE (ADR-0019)     │
│ADR-0016  │   │ Protocol 单向通知   │
└──────────┘   └────────────────────┘
```

### 4.3 MCP 兼容性（必须处理的遗漏点）

不同 AI IDE 对 MCP 通道支持能力不一，CE 必须按**能力协商**降级：

| IDE | tools | resources | prompts | CE 注入通道优先级 |
|-----|:-----:|:---------:|:-------:|------------------|
| Cursor | ✅ | ✅ | ✅ | resources > prompts > tools |
| Trae | ✅ | ⚠️ 部分 | ✅ | prompts > tools |
| Claude Desktop | ✅ | ✅ | ✅ | resources > prompts |

CE `inject()` 必须先调用 `client_info/capabilities` 协商，不支持时降级到可用通道。详见 `context-engine-interface.md §7.2`。

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **零外部依赖**：本地可运行完整 CE，与 ZephyrAlpha 个人量化定位一致
- **可落地**：3-5 人日（一人周）可完成 Phase 1 MVP（library 模式）
- **可升级**：Protocol 抽象基类保证未来切 Neo4j / 大模型 API 零业务层改动

### 5.2 负面后果

- **Qwen2.5-3B 质量上限**：复杂代码库（> 1000 文件）压缩可能失真，需要人工审核
- **NetworkX 线程安全弱**：需 `asyncio.Lock` 保护读写（已在接口规范约定）
- **模型磁盘占用**：~2GB（需纳入 `.runtime/` 规划）

### 5.3 未来重新评估触发条件

- **TECH-01**：entity-graph 节点数 > 50K → 迁 Neo4j
- **TECH-02**：压缩延迟 P99 > 5s 持续 7 天 → 升级 Qwen2.5-7B 或外部 API
- FLE 检测"CE 压缩后幻觉率 > 10%" → 重评压缩策略
- Cursor / Trae 发布 MCP 2.x breaking changes → 兼容层补丁

---

## 6. 落地动作（Implementation）

| # | 动作 | 物理位置 | 估时 |
|---|------|---------|:----:|
| 1 | 实现 `ContextEngineProtocol` 抽象基类 | `src/zephyr/context_engine/protocol.py` | 0.5 天 |
| 2 | 实现 `InProcessContextEngine` | `src/zephyr/context_engine/in_process.py` | 2 天 |
| 3 | 集成 NetworkX graph store | `src/zephyr/context_engine/graph_store.py` | 1 天 |
| 4 | 集成 Qwen2.5-3B ONNX 推理 | `src/zephyr/context_engine/compressor.py` | 1 天 |
| 5 | 降级路径：规则基摘要 | `src/zephyr/context_engine/fallback.py` | 0.5 天 |
| 6 | MCP capability 协商 + 降级注入 | `src/zephyr/context_engine/mcp_adapter.py` | 1 天 |
| 7 | P0 测试组（含冷启动 + 降级）| `tests/context_engine/test_p0.py` | 1 天 |

**总工时**：约 7 人日（单人）

---

## 7. 参考

- **真源**：`vibe-coding-audit-merged.md §Kimi 9.7` + `§Qwen 选型表 #1-3`
- **接口规范**：[`context-engine-interface.md v1.0.0`](../../03_modules/_b_track_interfaces/context-engine-interface.md)
- **架构位置**：[`03-application-architecture.md §4A.1`](../target-architecture/03-application-architecture.md)
- **技术选型**：[`technology-landscape.yaml TECH-01/02/03`](../target-architecture/architecture-model/technology/technology-landscape.yaml)
- **相关 ADR**：ADR-0016（VMS）/ ADR-0017（Orc）/ ADR-0019（FLE）/ ADR-0020（LSG）/ ADR-0021（SSoT 前置）
- **外部**：[NetworkX docs](https://networkx.org/) / [Model Context Protocol spec](https://modelcontextprotocol.io/)

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：选型 NetworkX + JSON + Qwen2.5-3B ONNX；MCP 能力协商 + 降级策略；B-e-2 产出。 |
