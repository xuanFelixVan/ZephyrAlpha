---
blueprint_id: MOD-DATA_GOV-012
module_name: column_lineage_tracker
domain: D_DATA_GOV
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
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/column_lineage_tracker.py
granularity: file
---

# MOD-DATA_GOV-012 column_lineage_tracker 蓝图（列级血缘追踪器）

> **module_id**: MOD-DATA_GOV-012 | **域**: D_DATA_GOV | **优先级**: P2
> **来源**: B10-02321（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-009，A1 M8-NEW-02）
> 代码：`src/zephyr/data_governance/column_lineage_tracker.py`

## 0. 定位

列级血缘：血缘边扩展column映射（source_col->target_col+transform表达式字段）+登记接口+列级上下游查询（给定表.列查上游列链/下游影响列）+列级影响分析（删列影响面）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_governance/test_column_lineage_tracker.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
