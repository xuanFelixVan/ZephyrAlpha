---
blueprint_id: MOD-FAC-004
module_name: factor_vote_mining
domain: D_FACTOR
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
domain_id: D_FACTOR
path: src/zephyr/research/factor_vote_mining.py
granularity: file
---

# MOD-FAC-004 factor_vote_mining 蓝图（FactorMAD多智能体投票因子挖掘）

> **module_id**: MOD-FAC-004 | **域**: D_FACTOR | **优先级**: P2
> **来源**: B10-01845（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-020，A1 §29.14-3.5）
> 代码：`src/zephyr/research/factor_vote_mining.py`

## 0. 定位

FactorMAD：3-5个生成Agent独立产出因子（Agent回调全注入）+多数投票选优（票数>半入选）+性能不足升级辩论（辩论轮次护栏）+候选须过IC验证+样本外测试（注入验证器）+<1分钟/因子时延预算标记。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/research/test_factor_vote_mining.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
