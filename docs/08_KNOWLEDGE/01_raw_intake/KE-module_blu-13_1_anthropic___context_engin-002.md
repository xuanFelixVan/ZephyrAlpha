---
module_id: KE-module_blu-13_1_anthropic___context_engin-002
title: 13.1 Anthropic — Context Engineering（上下文工程）
category: module_blueprint
---

# 13.1 Anthropic — Context Engineering（上下文工程）

13.1 Anthropic — Context Engineering（上下文工程）

2025 年 9 月，Anthropic 正式提出上下文工程取代提示工程。

| 维度 | 提示工程（旧） | 上下文工程（新） |
|---|---|---|
| 关注点 | "怎么问" | "提问时，模型应该知道什么" |
| 范围 | 单次 system prompt | 系统指令 + 工具 + MCP + 消息历史 + 检索 |
| 核心约束 | 措辞 | **注意力预算**：每新增 token 稀释注意力（n² 问题） |

**Anthropic 关键实践：**
1. **Context Rot 模型** — n² pairwise attention 衰减，"LLM 像人类有工作记忆上限"
2. **XML Tag 强制分区** — `<background_information>` `<instructions>` 分区防信息混杂
3. **Multi-Turn Curation Loop** — 每轮从"信息宇宙"策展最少量最高信号 token
4. **System Prompt 版本化** — 15+ 版，时态行为精确校准
5. **Hybrid Approach** — 本地上下文 + 全局 MCP 知识基
