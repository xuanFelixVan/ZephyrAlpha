---
blueprint_id: MOD-KNW-002
module_name: knowledge_quality_assessor
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
path: src/zephyr/knowledge/knowledge_quality_assessor.py
granularity: file
---

# MOD-KNW-002 knowledge_quality_assessor 蓝图（知识质量评估器）

> **module_id**: MOD-KNW-002 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B14-04624（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-013，A9 D-KNOWLEDGE-11）
> 代码：`src/zephyr/knowledge/knowledge_quality_assessor.py`

## 0. 定位

知识条目四维评分（准确性/时效性/来源可信度/引用频次，权重可配）+时效衰减模型（注入时钟）+低分条目隔离降权（阈值判定）+定期复核队列（FIFO）+评分变化写审计回调，质量分写回KBEngine元数据语义。RAGAS思想单机版。canonical承接KNW-003/KNW-006归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_knowledge_quality_assessor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
