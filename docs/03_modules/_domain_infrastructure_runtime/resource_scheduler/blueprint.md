---
blueprint_id: MOD-INF-074
module_name: resource_scheduler
domain: D_INFRA_RUNTIME
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
domain_id: D_INFRA_RUNTIME
path: src/zephyr/infra_runtime/resource_scheduler.py
granularity: file
---

# MOD-INF-074 resource_scheduler 蓝图（IR-06 资源调度器）

> **module_id**: MOD-INF-074 | **域**: D_INFRA_RUNTIME | **优先级**: P2
> **来源**: B7-09926（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-014，D-INFRA-RUNTIME §2）
> 代码：`src/zephyr/infra_runtime/resource_scheduler.py`

## 0. 定位

CPU核心亲和绑定+内存预算强制+Cold/Warm/Hot三平面资源隔离+QPS限流统一入口。业界对标cgroup式资源隔离+CPU亲和+令牌桶限流。纯内存逻辑：亲和映射表/预算表/平面配额/QPS令牌桶统一裁决入口，实际OS级设置经注入executor回调（默认空操作记录），超限拒绝+告警。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infra_runtime/test_resource_scheduler.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
