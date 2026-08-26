---
blueprint_id: MOD-RK-044
module_name: risk_policy_persister
domain: D_RISK
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
domain_id: D_RISK
path: src/zephyr/risk/risk_policy_persister.py
granularity: file
---

# MOD-RK-044 risk_policy_persister 蓝图（风控策略持久化器）

> **module_id**: MOD-RK-044 | **域**: D_RISK | **优先级**: P2
> **来源**: B13-04311（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-048，A3 D-RISK-49）
> 代码：`src/zephyr/risk/risk_policy_persister.py`

## 0. 定位

风控策略SQLite持久化：risk_policy/risk_limit/risk_policy_version三表（注入连接）+版本递增不可变+激活版本热加载（切换原子）+与risk_limits契约双向同步校验（漂移清单）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/risk/test_risk_policy_persister.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
