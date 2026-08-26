---
blueprint_id: MOD-CMP-015
module_name: compliance_policy_engine
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
path: src/zephyr/compliance/compliance_policy_engine.py
granularity: file
---

# MOD-CMP-015 compliance_policy_engine 蓝图（合规策略即代码引擎）

> **module_id**: MOD-CMP-015 | **域**: D_COMPLIANCE | **优先级**: P2
> **来源**: B14-04651（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-006，A9 D-COMPLIANCE-16）
> 代码：`src/zephyr/compliance/compliance_policy_engine.py`

## 0. 定位

合规规则声明式DSL（YAML规则schema：条件/动作/严重度）+版本管理+规则回放验证（历史交易重放比对注入回放器）+非交易时段热加载（注入时段判定）+变更须人工审批队列。OPA/Rego思想轻量版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/compliance/test_compliance_policy_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
