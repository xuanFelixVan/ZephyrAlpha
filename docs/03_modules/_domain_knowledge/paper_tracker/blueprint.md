---
blueprint_id: MOD-KNW-013
module_name: paper_tracker
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
path: src/zephyr/knowledge/paper_tracker.py
granularity: file
---

# MOD-KNW-013 paper_tracker 蓝图（论文追踪器）

> **module_id**: MOD-KNW-013 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B6-08549（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-016，B6 D-RESEARCH-07）
> 代码：`src/zephyr/knowledge/paper_tracker.py`

## 0. 定位

论文追踪：arXiv API按主题订阅（API调用全注入不真发）+标题/DOI去重（规范化指纹）+本地LLM摘要（注入摘要器）+关键词频次趋势检测（滚动窗统计）+与假设提取对接（注入hypothesis_sink）。Zotero式管理。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_paper_tracker.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
