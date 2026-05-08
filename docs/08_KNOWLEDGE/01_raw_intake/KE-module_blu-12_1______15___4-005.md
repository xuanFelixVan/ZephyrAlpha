---
module_id: KE-module_blu-12_1______15___4-005
title: 12.1 盲点总览（15 项，4 个优先级）
category: module_blueprint
---

# 12.1 盲点总览（15 项，4 个优先级）

12.1 盲点总览（15 项，4 个优先级）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase | 专业对标 |
|:---:|:---:|------|:---:|------|
| 🔴 | B26 | **AI 成本预算与强制熔断**——LLM API 调用无硬性成本限制。Agent 异常循环可在 10 分钟内刷光 $200 配额。`metrics.py` 只有 technical metrics（latency/count），零成本感知 | 11 | AgentBudget、PydanticAI Logfire |
| 🔴 | B27 | **AI 上下文文件自更新基础设施**——AGENTS.md 是静态的，AI 无法把"犯错-学到"写回宪法。Boris Cherny 的 CLAUDE.md 每周更新多次，所有 AI session 共享学习 | 14 | Claude Code CLAUDE.md、@.claude PR review |
| 🔴 | B28 | **Token 计数与上下文预算管理**——`token_utils.py` 已存在于 shared/ 但未被 `__init__.py` 导出。缺少上下文配额分配、预算追踪器、超预算截断策略 | 11 | OpenAI tiktoken、LangChain token counter |
| 🟠 | B29 | **Evals 框架**——有 contract tests（代码正确性），缺 Agent 输出质量系统评估。需要结构化 eval 用例定义、评分 rubrics、回归检测 | 12 | PydanticAI Evals、LangChain eval harness |
| 🟠 | B30 | **Durable Execution（断点续跑）**——长流程 AI task 可能运行数小时。进程崩溃后从头重跑 → 浪费全部已消耗的 token 和成本 | 13 | PydanticAI Durable Execution、Temporal.io |
| 🟠 | B31 | **AI 输出后处理管道**——Boris Cherny 的核心技巧：AI 生成代码后自动跑 lint/format/typecheck，修复最后 10% 质量问题 | 13 | Claude Code PostToolUse hooks、pre-commit |
| 🟠 | B32 | **AI Session 完整审计轨迹**——每次 AI session 的记录（prompts、decisions、tool calls、costs、errors、outcomes）。1人+AI 维护下唯一的学习来源 | 12 | PydanticAI Logfire audit、AgentBudget webhooks |
| 🟡 | B33 | **Multi-Agent 团队编排基座**——Agent role 定义 + task dispatch + result merge。Boris Cherny 三阶段流水线：Opus 规划→Sonnet 实现→Haiku 验证。**2026 深化**: A2A Protocol v1.0（Google Cloud 发起，50+ 合作伙伴）为生产级 agent-to-agent 通信标准——Agent Card 能力发现 + Task 生命周期 + Signed Agent Cards 密码学验证 | 14 | Claude Code Agent Teams、BridgeSwarm、A2A v1.0 |
| 🟡 | B34 | **Agent Skill/Prompt 注册表（共享层）**——`prompt_registry.py` 在 `context_engine/` 而非 shared/。共享层应提供通用 PromptTemplate + Skill 注册接口 | 14 | PydanticAI Agent Skills、MCP prompts |
| 🟡 | B35 | **Model Provider 抽象层**——`api_client.py` 有 HTTP 层统一 client，缺模型语义层（pricing-aware provider、自动 fallback、capability 查询） | 15 | PydanticAI model-agnostic providers、LiteLLM |
| 🟡 | B36 | **上下文窗口压缩/截断策略**——当上下文接近模型上限时，需智能压缩（摘要旧消息、保留关键决策）。共享层应有 TruncationStrategy 接口 | 15 | LangChain summarization、Claude prompt caching |
| 🔵 | B37 | **结构化 Agent 输出质量评分**——不仅是"对不对"，而是"好不好"。Relevance/Accuracy/Completeness 三维评分 + 自动回归 | 15 | PydanticAI Evals scoring rubrics |
| 🔵 | B38 | **配置覆盖链（环境 > YAML > 默认）**——1人+AI 维护时需要清晰的配置优先级 | 15 | Spring Profiles、12-Factor §III |
| 🔵 | B39 | **依赖注入容器**——AI agent 组件化：constructor injection → 组件可替换 → 测试可隔离 | 15 | Spring DI、FastAPI Depends |
| 🔵 | B40 | **AI 代码生成沙箱（共享层统一接口）**——`process_sandbox.py` 在 `llm_security/`，shared/ 应有沙箱接口抽象 | 15 | LLMCore sandboxed execution |
