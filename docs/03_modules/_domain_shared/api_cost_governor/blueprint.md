---
blueprint_id: MOD-SHARED-003
module_name: api_cost_governor
domain: D_SHARED
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
domain_id: D_SHARED
path: src/zephyr/shared/capacity_governance/api_cost_governor.py
granularity: file
---

# MOD-SHARED-003 api_cost_governor 蓝图（外部API成本治理器）

> **module_id**: MOD-SHARED-003 | **域**: D_SHARED | **优先级**: P2
> **来源**: B1-00308（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-SHARED-001，C2 C-044）
> 代码：`src/zephyr/shared/capacity_governance/api_cost_governor.py`

## 0. 定位

外部API调用计量（按源计数/成本单价表）+成本预算（日/月预算注册，超预算自动降级标记）+QPS动态分配令牌桶（按预算剩余比例动态调速率，注入时钟）。OpenTelemetry计费思想单机化。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/shared/capacity_governance/test_api_cost_governor.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
