---
blueprint_id: MOD-KNW-004
module_name: knowledge_artifact_store
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
path: src/zephyr/knowledge/knowledge_artifact_store.py
granularity: file
---

# MOD-KNW-004 knowledge_artifact_store 蓝图（知识工件库）

> **module_id**: MOD-KNW-004 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B12-03637（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-008，B12）
> 代码：`src/zephyr/knowledge/knowledge_artifact_store.py`

## 0. 定位

6类知识产出（RawKnowledgePacket/StructuredKnowledgeFragment/ClassifiedKnowledgePackage/ModuleMappingResult/NewModule/TrialResult词表闭合）不可变schema+版本化存储（同artifact_id版本链，写不可改）+6维索引（来源/作者/类型/目标层级/时间/效果）查询。聚合根版本不变量不变式。canonical承接KNW-018归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_knowledge_artifact_store.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
