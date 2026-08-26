---
blueprint_id: MOD-KNW-007
module_name: ai_knowledge_extractor
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
path: src/zephyr/knowledge/ai_knowledge_extractor.py
granularity: file
---

# MOD-KNW-007 ai_knowledge_extractor 蓝图（AI自动知识提取器）

> **module_id**: MOD-KNW-007 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B10-02191（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-007，A1 D-KNOWLEDGE-17）
> 代码：`src/zephyr/knowledge/ai_knowledge_extractor.py`

## 0. 定位

实验报告/研究笔记/策略代码三类源经LLM抽取写KB的批处理管线：源注册+抽取（注入llm回调，结构化输出schema校验）+人工确认队列（置信度低于阈值转人工）+批处理进度断点续跑+写KB注入回调。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_ai_knowledge_extractor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
