---
blueprint_id: MOD-PA-014
module_name: strategy_screener_3d
domain: D_PF_ALLOC
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
domain_id: D_PF_ALLOC
path: src/zephyr/pf_alloc/core/strategy_screener_3d.py
granularity: file
---

# MOD-PA-014 strategy_screener_3d 蓝图（策略筛选三维评估器）

> **module_id**: MOD-PA-014 | **域**: D_PF_ALLOC | **优先级**: P2
> **来源**: B10-02090（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PFALLOC-009，A1 PA-02）
> 代码：`src/zephyr/pf_alloc/core/strategy_screener_3d.py`

## 0. 定位

策略入库三维评分：收益风险清晰性（Sharpe/回撤/卡玛复合）+参数稳定性（参数邻域敏感性注入回测序列）+天然互补性（与现有策略相关性矩阵注入）三维加权评分+入库建议阈值档。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/pf_alloc/test_strategy_screener_3d.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
