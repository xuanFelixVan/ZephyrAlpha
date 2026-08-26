---
blueprint_id: MOD-KNW-003
module_name: financial_knowledge_graph
domain: D_KNOWLEDGE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_KNOWLEDGE
path: src/zephyr/knowledge/financial_knowledge_graph.py
granularity: file
---

# MOD-KNW-003 financial_knowledge_graph 蓝图（金融知识图谱）

> **module_id**: MOD-KNW-003 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B1-00126（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-001，C2 D-KNOW-01）
> 代码：`src/zephyr/knowledge/financial_knowledge_graph.py`

## 0. 定位

SQLite邻接表轻量图谱：六类实体（公司/行业/供应链/股东/事件/概念词表闭合）+关系表（类型词表+权重+属性JSON）+增删查+子图抽取（N跳邻域）+邻居/路径查询API（BFS最短路径）+LLM抽取结果人工审核入图接口（pending_review状态机）+规模护栏（≤百万边计数拒绝）。严禁Neo4j。canonical承接KNW-010归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_financial_knowledge_graph.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
