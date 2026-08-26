---
blueprint_id: MOD-KNW-008
module_name: rag_pipeline
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
path: src/zephyr/knowledge/rag_pipeline.py
granularity: file
---

# MOD-KNW-008 rag_pipeline 蓝图（RAG问答管道）

> **module_id**: MOD-KNW-008 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B13-04034（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-009，A3）
> 代码：`src/zephyr/knowledge/rag_pipeline.py`

## 0. 定位

RAG问答管道：文档分块（重叠滑窗）→hybrid检索（向量+关键词双路注入检索器，RRF融合）→重排（注入reranker）→本地LLM生成（注入生成器）+引用溯源（chunk id回链源文档，引用列表随答案输出）+统一ingest入口。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_rag_pipeline.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
