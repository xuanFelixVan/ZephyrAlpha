---
blueprint_id: MOD-SIG-132
module_name: day_trade_pnl_estimator
domain: D_ASHARE_SIGNAL
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
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/day_trade_pnl_estimator.py
granularity: file
---

# MOD-SIG-132 day_trade_pnl_estimator 蓝图（做T盈亏预估器）

> **module_id**: MOD-SIG-132 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B11-02600（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-055，A7 技能day-trade-pnl-estimate）
> 代码：`src/zephyr/signal_ashare/day_trade_pnl_estimator.py`

## 0. 定位

做T成本模型净盈亏预估（价差-双边佣金-印花税-冲击成本四要素）+置信度（历史相似价差实现率）+成交回写校准（预估vs实现偏差滚动校正参数）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_day_trade_pnl_estimator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
