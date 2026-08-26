---
blueprint_id: MOD-SIG-118
module_name: supply_chain_momentum
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
path: src/zephyr/signal_ashare/supply_chain_momentum.py
granularity: file
---

# MOD-SIG-118 supply_chain_momentum 蓝图（产业链传导与供应链动量）

> **module_id**: MOD-SIG-118 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01376（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-038，A1 模块22）
> 代码：`src/zephyr/signal_ashare/supply_chain_momentum.py`

## 0. 定位

产业链邻接表（投入产出关系注入）+上游动量因子（客户/供应商收益领先1-5日加权）+传导强度R²>5%筛选（注入回归器）+传导异常>2σ标记。Cohen&Frazzini供应链动量。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_supply_chain_momentum.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
