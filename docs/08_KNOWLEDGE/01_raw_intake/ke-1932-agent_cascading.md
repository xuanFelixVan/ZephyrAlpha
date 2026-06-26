---
module_id: KE-1841---------agent---cascading-000
status: active
title: 2.26 级联故障隔离——Agent链中的Cascading Failure防护（决策 D-018-24）
category: module_blueprint
ttl: permanent
---

# 2.26 级联故障隔离——Agent链中的Cascading Failure防护（决策 D-018-24）

2.26 级联故障隔离——Agent链中的Cascading Failure防护（决策 D-018-24）

> **决策 D-018-24**：在多Agent场景（Orchestrator→Worker）中，单个Agent的错误输出会级联感染下游Agent。蓝图当前没有建模级联故障场景。新增**级联故障隔离器**。
>
> **可信主体**：Perplexity——"Cascading Failures in Long-Running Workflows——Error in Agent A's output causes Agent B to make unauthorized decisions"。NVIDIA多Agent全生命周期——"单点漏洞可快速传导至全链路"。

```python
