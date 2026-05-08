---
module_id: KE-module_blu-2_23_context_drift____________-000
title: 2.23 Context Drift 检测——操作链中的意图漂移（决策 D-018-21）
category: module_blueprint
---

# 2.23 Context Drift 检测——操作链中的意图漂移（决策 D-018-21）

2.23 Context Drift 检测——操作链中的意图漂移（决策 D-018-21）

> **决策 D-018-21**：AI Agent 在长时间的操作链中可能出现"Context Drift"——从最初"修复一个Bug"逐渐变为"重构整个模块"。L2 ABAC 的意图感知当前只检查TaskType，不检测链上漂移。新增语义漂移检测。
>
> **可信主体**：Enterprise research——"Context Drift——Agent Chains Break Security Boundaries——授权边界随操作链漂移是最隐蔽的越权形式"。Claude Code——long conversations 中 agent 行为漂移是已知问题。

```python
