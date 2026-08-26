---
blueprint_id: MOD-PF-014
module_name: rebalance_cost_analyzer
domain: D_PF_CORE
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
domain_id: D_PF_CORE
path: src/zephyr/pf_core/core/rebalance_cost_analyzer.py
granularity: file
---

# MOD-PF-014 rebalance_cost_analyzer 蓝图（再平衡成本分析器）

> **module_id**: MOD-PF-014 | **域**: D_PF_CORE | **优先级**: P2
> **来源**: B10-02079（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PF004-007，A1 PC-10）
> 代码：`src/zephyr/pf_core/core/rebalance_cost_analyzer.py`

## 0. 定位

调仓成本四拆解：显性（佣金/印花税）+隐性（冲击/价差）+税收（股息税/资本利得语义注入税率表）+机会成本（调仓期间偏离基准收益）+拆解报告（占比排序）+成本异常告警阈值。Decimal-only。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/pf_core/test_rebalance_cost_analyzer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
