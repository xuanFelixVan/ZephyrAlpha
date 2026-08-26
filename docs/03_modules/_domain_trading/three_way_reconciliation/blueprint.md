---
blueprint_id: MOD-TRADING-013
module_name: three_way_reconciliation
domain: D_TRADING
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
domain_id: D_TRADING
path: src/zephyr/trading/three_way_reconciliation.py
granularity: file
---

# MOD-TRADING-013 three_way_reconciliation 蓝图（三向对账引擎）

> **module_id**: MOD-TRADING-013 | **域**: D_TRADING | **优先级**: P2
> **来源**: B13-04352（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-TRD-011，A3 D-TRADING-02）
> 代码：`src/zephyr/trading/three_way_reconciliation.py`

## 0. 定位

三向对账收口：交易/持仓/资金三方流水（券商资金流水：佣金/印花税/利息逐笔）+异常分类（价格/数量/费用/缺失四类词表闭合）+自动匹配规则（标的+数量+金额容差）+未匹配项台账与跟进状态机。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/trading/test_three_way_reconciliation.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
