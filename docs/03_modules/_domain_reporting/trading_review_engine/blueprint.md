---
blueprint_id: MOD-RPT-034
module_name: trading_review_engine
domain: D_REPORTING
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
domain_id: D_REPORTING
path: src/zephyr/reporting/trading_review_engine.py
granularity: file
---

# MOD-RPT-034 trading_review_engine 蓝图（A股交易审查引擎）

> **module_id**: MOD-RPT-034 | **域**: D_REPORTING | **优先级**: P2
> **来源**: B14-04662（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-RPT-009，A9 D-REPORTING-15）
> 代码：`src/zephyr/reporting/trading_review_engine.py`

## 0. 定位

日终交易审查：撤单率/申报速率/自成交/拉抬打压四模式扫描（阈值表注入）→审查报告（异常标的+证据+处置建议三要素）+联动检测数据注入+报告版本化。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/reporting/test_trading_review_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
