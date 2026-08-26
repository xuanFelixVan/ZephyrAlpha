---
blueprint_id: MOD-CMP-017
module_name: regulatory_change_tracker
domain: D_COMPLIANCE
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
domain_id: D_COMPLIANCE
path: src/zephyr/compliance/regulatory_change_tracker.py
granularity: file
---

# MOD-CMP-017 regulatory_change_tracker 蓝图（监管变更追踪器）

> **module_id**: MOD-CMP-017 | **域**: D_COMPLIANCE | **优先级**: P2
> **来源**: B14-04671（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-008，A9 M36-S05）
> 代码：`src/zephyr/compliance/regulatory_change_tracker.py`

## 0. 定位

监管变更追踪：证监会/交易所公告采集（注入源不真发）+NLP变更抽取（注入llm：变更类型/生效日期/涉及条款结构化校验）+影响域映射（规则库条款关联表）→合规规则评审任务（人工确认后入Policy-as-Code规则库语义）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/compliance/test_regulatory_change_tracker.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
