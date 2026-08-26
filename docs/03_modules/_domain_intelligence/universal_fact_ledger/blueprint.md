---
blueprint_id: MOD-INT-FACT-LEDGER
module_name: universal_fact_ledger
domain: D_INTELLIGENCE
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
domain_id: D_INTELLIGENCE
path: src/zephyr/intelligence/universal_fact_ledger.py
granularity: file
---

# MOD-INT-FACT-LEDGER universal_fact_ledger 蓝图（通用事实账本与双重锚定）

> **module_id**: MOD-INT-FACT-LEDGER | **域**: D_INTELLIGENCE | **优先级**: P2
> **来源**: B10-01952（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-AISA-014，A1 §29.24-1）
> 代码：`src/zephyr/intelligence/universal_fact_ledger.py`

## 0. 定位

VeNRA架构UFL：追加式事实账本（{entity/attribute/value/timestamp/source}五要素+数值/枚举/关系3类型词表闭合，confidence=1.0硬约束）+DoubleLockGrounding校验器（LLM输出实体不存在于UFL或数值非检索自UFL即拒绝，拒绝不可降级须修正重提）+约束强度3档可配+查询接口。canonical承接AISA-012归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/intelligence/test_universal_fact_ledger.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
