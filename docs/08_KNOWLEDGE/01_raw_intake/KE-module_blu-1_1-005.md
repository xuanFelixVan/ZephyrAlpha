---
module_id: KE-module_blu-1_1-005
title: 1.1 缺口 → 原因 → 解法
category: module_blueprint
---

# 1.1 缺口 → 原因 → 解法

1.1 缺口 → 原因 → 解法

**缺口**：AI Agent 执行任务时，或者上下文爆炸（token 超限、延迟飙升、hallucination 增加），或者上下文饥饿（找不到相关 ADR/接口/教训），两难症导致编码质量不稳定。

**原因**：
1. 老方案让人工维护 `context-spec.md` 预拼上下文——规模一旦超过 10 个任务就不可维护
2. Prompt 拼接没有 token budget 概念，超限靠截断，关键信息反而被裁掉
3. MCP 协议三家 IDE 能力不一（Cursor 支持 tools、Trae 侧重 resources、Claude-Desktop 强 prompts），老方案用单一通道导致部分 IDE 只能降级
4. 没有闭环反馈——某类上下文（例如 `lessons`）经常不被 AI 使用就该降权，但无机制

**解法**：
- **build-compress-validate-inject 四段流水**——每段可独立度量与替换
- **entity-graph + VMS + 文件系统三源**——结构化依赖 + 语义检索 + 精确兜底
- **MCP 能力矩阵**——探测 IDE 能力后多路注入，不支持的能力降级到 `prompts` 单通道
- **Feedback Loop 反馈通道（Protocol 引用）**——异常信号驱动策略调参
