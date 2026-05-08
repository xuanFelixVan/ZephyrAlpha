---
module_id: KE-module_blu-2_24_____________agent________-000
title: 2.24 连续验证——每步重验证 Agent 身份与权限一致性（决策 D-018-22）
category: module_blueprint
---

# 2.24 连续验证——每步重验证 Agent 身份与权限一致性（决策 D-018-22）

2.24 连续验证——每步重验证 Agent 身份与权限一致性（决策 D-018-22）

> **决策 D-018-22**：当前模型是"Tool调用前检查一次"。在Agent链中（特别是Orchestrator→Worker委托），身份可能在中途被篡改或上下文被污染。引入**连续验证**——每一步执行后、下一步执行前都重新验证。
>
> **可信主体**：Cisco TBAC——"Zero Trust for Agents——Verification at Every Step"。Perplexity——"Agent Identity——每一步重验证 Non-Human Identity"。NIST Zero Trust——"从不信任，始终验证"。

```python
