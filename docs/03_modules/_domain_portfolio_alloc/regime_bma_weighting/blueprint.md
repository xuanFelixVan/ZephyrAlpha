---
blueprint_id: MOD-PA-015
module_name: regime_bma_weighting
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
path: src/zephyr/pf_alloc/core/regime_bma_weighting.py
granularity: file
---

# MOD-PA-015 regime_bma_weighting 蓝图（体制条件BMA信号权重）

> **module_id**: MOD-PA-015 | **域**: D_PF_ALLOC | **优先级**: P2
> **来源**: B11-02963（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PFALLOC-010，A7）
> 代码：`src/zephyr/pf_alloc/core/regime_bma_weighting.py`

## 0. 定位

regime条件BMA权重：按市场体制分组滚动250日估计各信号历史预测精度（命中率/IC）+后验归一（Σ=1）+权重变更落审计回调+体制切换权重平滑过渡（半衰期混合）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/pf_alloc/test_regime_bma_weighting.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
