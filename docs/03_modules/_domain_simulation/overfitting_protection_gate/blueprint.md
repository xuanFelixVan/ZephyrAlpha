---
blueprint_id: MOD-SIM-028
module_name: overfitting_protection_gate
domain: D_SIMULATION
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
domain_id: D_SIMULATION
path: src/zephyr/simulation/overfitting_protection_gate.py
granularity: file
---

# MOD-SIM-028 overfitting_protection_gate 蓝图（过拟合系统性防护门禁）

> **module_id**: MOD-SIM-028 | **域**: D_SIMULATION | **优先级**: P2
> **来源**: B1-00261（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-SIM-009，C2 C-033）
> 代码：`src/zephyr/simulation/overfitting_protection_gate.py`

## 0. 定位

四层防护统一门禁：因子（IC衰减+多重检验校正）/策略（deflated SR+PBO注入计算器）/信号（walkforward折叠一致性）/ML（OOS退化+对抗注入）四层检查项注册表+统一裁决（任一层失败即拦截上线）+防护报告。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/simulation/test_overfitting_protection_gate.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
