---
blueprint_id: MOD-KNW-012
module_name: research_catalog
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
path: src/zephyr/knowledge/research_catalog.py
granularity: file
---

# MOD-KNW-012 research_catalog 蓝图（研究目录）

> **module_id**: MOD-KNW-012 | **域**: D_KNOWLEDGE | **优先级**: P2
> **来源**: B6-08548（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-015，B6 D-RESEARCH-06）
> 代码：`src/zephyr/knowledge/research_catalog.py`

## 0. 定位

研究目录：研究资产元数据索引（资产类型词表）+标签系统（多对多）+SQLite FTS5检索（注入连接）+引用关系表（cites/cited_by双向）+语义检索挂vector_memory注入适配器+访问控制按L1-L4数据分级过滤。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/knowledge/test_research_catalog.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
