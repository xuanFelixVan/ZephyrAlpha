---
module_id: KE-2966------beta-005
status: active
title: Track D：AI-AI 协作知识（beta+ 预留接口）
category: module_blueprint
ttl: permanent
---

# Track D：AI-AI 协作知识（beta+ 预留接口）

Track D：AI-AI 协作知识（beta+ 预留接口）

> **状态**：`planned`——分类桩已就位，接口契约已定义，beta 之前不实现提取/入库逻辑。
> **为什么现在就要定义**：§6.3 埋雷判定——如果等 1000+ KE 入库后再补 AI-AI 协作分类，全量重新打标的工量 = 埋雷。现在定义空壳 = 零成本的"接口预留位"。

**场景**（beta 未来状态）：

| 场景 | 描述 | 产生什么知识 |
|------|------|------------|
| 双 Agent 对等讨论 | Agent A 提出方案 → Agent B 挑战/改进 → 收敛 | 协作决策日志（哪个 Agent 的方案赢了、为什么） |
| Agent 分工协作 | Agent A 负责代码 → Agent B 负责测试 → 结果合并 | 分工模式（并行/串行/接力）、Agent 专长画像 |
| Agent 交叉审查 | Agent A 写的 ADR → Agent B 审查 → 发现问题 | 审查发现（Agent B 发现了 Agent A 的什么盲区） |
| 多 Agent 投票 | 3 个 Agent 对同一问题给出不同答案 → 投票裁决 | 投票模式（哪个 Agent 的方案更正确/更高效） |

**Track D 分类桩（3 类，beta 实现）**：

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例（beta 才产生） |
|:--:|-----------|------|:---:|:---:|---------|------|
| D1 | `agent_collab_pattern` | Agent 协作模式 | — | — | 双 Agent 讨论日志 | "Agent B 挑战了 Agent A 的 SQLite 选型，最终 Agent A 引用 ChromaDB 官方文档胜出" |
| D2 | `agent_expertise_profile` | Agent 能力画像 | — | — | 交叉审查记录 | "Agent Qwen 在编码约定类偏差最大（20% 违反 A1 规则），建议加强 A1 上下文注入" |
| D3 | `multi_agent_decision` | 多 Agent 联合决策 | — | — | 投票日志 | "3/3 Agent 一致选择 ruff；2/3 Agent 建议 pytest -x 而非 pytest --lf" |
| D4 | `graphrag_integration` | **GraphRAG 图谱检索增强** | — | — | `ke_relations` 表 + NetworkX | **Phase 5 预留**——实体-关系-推理链的图遍历检索。当前图只用于"验证"不用于"检索"→KE > 500 时启用图遍历与向量检索的混合排序。需要：`ke_relations` 表（source_ke_id, relation_type, target_ke_id）+ `relation_type` 枚举（depends_on/contradicts/supersedes/refines/exemplifies/generalizes）+ `graph_retriever.py` + Community Summary 生成 |

**接口契约（现在定义，beta 实现）**：

```python
