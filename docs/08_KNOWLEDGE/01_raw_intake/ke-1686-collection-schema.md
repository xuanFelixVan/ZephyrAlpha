---
module_id: KE-1596-----collection-schema-003
status: active
title: 2. 八大 Collection Schema
category: module_blueprint
---

# 2. 八大 Collection Schema

2. 八大 Collection Schema

| Collection | 写入方 | 读取方 | 存储内容 | 嵌入维度 | 分块策略 | TTL | 预估规模 | 数据来源 | AI自治级别 |
|------|:---:|:---:|------|:---:|------|:---:|:---:|------|:---:|
| **decisions** | Orchestrator | CE、FLE | 任务决策记录（做了什么+为什么） | 1024d | semantic 500-800 token | permanent | 1000-5000 | 新建 | supervised |
| **code_context** | Script System、Orc | CE | 代码上下文片段（AST-aware函数/类级） | 1024d | AST-aware function/class | 90d | 500-2000 | 新建 | autonomous |
| **lessons** | FLE、Script System | CE、KB | 经验教训（失败模式+修正） | 1024d | paragraph 300-500 token | permanent | 100-500 | **继承 failure_patterns** | autonomous |
| **knowledge** | KB | CE | 知识条目（KE全文向量） | 1024d | heading-aware 500-800 token | permanent | 100-1000 | **继承 ke_entries** | supervised |
| **rules** | Governance | CE、Orc | 治理规则（单条rule整存，42条） | 1024d | rule-level 整条存储 | permanent | 200-500 | **继承 vibe_rules** | human-gated |
| **blueprints** | Doc System | CE、Orc | 蓝图文档（按§节拆分） | 512d | section-aware 按§拆分 | permanent | 10000-30000 | **继承 blueprints** | supervised |
| **session_snapshots** | SessionManager | CE | 会话压缩摘要（最近N个session） | 512d | session-level 单摘要 | 90d | 50-200 | 新建 | autonomous |
| **execution_traces** | All systems | FLE、CE | 运行时任务执行语义摘要 | 512d | time-window 1min窗口 | 30d | 1000-5000 | 新建（替代 runtime_logs） | autonomous |

> **继承标记**：`failure_patterns` → `lessons`，`ke_entries` → `knowledge`，`vibe_rules` → `rules`，`blueprints` → `blueprints`。Phase 2 执行数据迁移 + 重命名。
> `runtime_logs` 已重命名为 `execution_traces`，语义更精确——区分"系统健康日志"和"任务执行轨迹"。
