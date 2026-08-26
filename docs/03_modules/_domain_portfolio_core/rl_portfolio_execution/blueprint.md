---
blueprint_id: MOD-PF-013
module_name: rl_portfolio_execution
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
path: src/zephyr/pf_core/rl_portfolio_execution.py
granularity: file
---

# MOD-PF-013 rl_portfolio_execution 蓝图（RL组合优化与执行）

> **module_id**: MOD-PF-013 | **域**: D_PF_CORE | **优先级**: P2
> **来源**: B10-01835（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PF004-006，A1 §29.9）
> 代码：`src/zephyr/pf_core/rl_portfolio_execution.py`

## 0. 定位

RL三场景分立编排：RL组合优化（状态/动作/奖励schema+Constrained RL Lagrangian注入trainer，风险预算硬上限钳制不可越）/RL最优执行（增强Almgren-Chriss，偏离AC轨迹超阈值熔断）/RL做T（底仓不变+风控硬约束校验）；统一经C-003回测门禁注入（不过不启用）+RL仅离线评估语义标注。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/pf_core/test_rl_portfolio_execution.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
