---
blueprint_id: MOD-OPS-001
module_name: ops_incident_aggregate
domain: D_OPS
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
domain_id: D_OPS
path: src/zephyr/infrastructure/system_telemetry/ops_incident_aggregate.py
granularity: file
---

# MOD-OPS-001 ops_incident_aggregate 蓝图（运维事件聚合根）

> **module_id**: MOD-OPS-001 | **域**: D_OPS | **优先级**: P2
> **来源**: B9-11460（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-OPS-001，B9 D-OPS）
> 代码：`src/zephyr/infrastructure/system_telemetry/ops_incident_aggregate.py`

## 0. 定位

OpsIncident核心聚合：incident_id+分级（P0~P2）+状态机（open→ack→mitigating→resolved→postmortem）+运维事件三件套（detected/escalated/resolved事件schema）+持久化注入。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/system_telemetry/test_ops_incident_aggregate.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
