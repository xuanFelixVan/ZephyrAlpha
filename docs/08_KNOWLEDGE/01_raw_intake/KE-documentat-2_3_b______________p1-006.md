---
module_id: KE-documentat-2_3_b______________p1-006
title: 2.3 B 轨目录游离于架构模型之外（P1 严重）
category: documentation
---

# 2.3 B 轨目录游离于架构模型之外（P1 严重）

2.3 B 轨目录游离于架构模型之外（P1 严重）

以下 **14 个 B 轨目录**在 `src/zephyr/` 下实际存在，但架构模型 YAML 中**完全没有定义**：

| 代码目录 | 内容概要 | KB 决策记录关联 | YAML 状态 |
|---------|---------|---------|----------|
| `context_engine/` | 上下文注入、意图解析、Prompt 注册 | ADR-0015 | ❌ 未定义 |
| `core/` | 文件任务映射、回滚管理、状态同步 | — | ❌ 未定义 |
| `dashboard/` | Web 仪表盘（5 个组件） | — | ❌ 未定义 |
| `db/` | SQLite schema、OLAP、事务管理 | ADR-0030 | ❌ 未定义 |
| `feedback_loop/` | 自动进化、评估、进化引擎 | ADR-0019 | ❌ 未定义 |
| `gates/` | 门禁引擎（G1-G5 配置） | — | ❌ 未定义 |
| `hooks/` | SSOT 守卫 | T-1-26 | ❌ 未定义 |
| `kb/` | 知识库（ingest/triage/activate 等） | — | ❌ 未定义 |
| `llm_security/` | 行为审计、输入净化 | ADR-0020 | ❌ 未定义 |
| `mcp/` | MCP 服务器（5 个） | ADR-0033 | ❌ 未定义 |
| `orchestrator/` | Agent 编排、幻觉检测 | ADR-0017 | ❌ 未定义 |
| `rules/` | 上下文规则、会话状态机 | — | ❌ 未定义 |
| `vector_memory/` | 向量记忆 | ADR-0016 | ❌ 未定义 |
| `config/` | 嵌入模型注册表 | — | ❌ 未定义 |

**影响**：架构模型无法完整描述系统现状，CI 门禁无法校验 B 轨模块合规性，`check_architecture_gates.py` 对 B 轨完全盲区。
