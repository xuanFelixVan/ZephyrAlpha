---
blueprint_id: MOD-INF-079
module_name: cold_plane_isolation
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
path: src/zephyr/infra_runtime/cold_plane_isolation.py
granularity: file
---

# MOD-INF-079 cold_plane_isolation 蓝图（Cold平面隔离器）

> **module_id**: MOD-INF-079 | **域**: D_INFRA_RUNTIME | **优先级**: P2
> **来源**: B14-04550（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-012，A9运维架构 §平面隔离）
> 代码：`src/zephyr/infra_runtime/cold_plane_isolation.py`

## 0. 定位

Cold平面（>1s）隔离：核16-19/内存≤20GB/IO BelowNormal/iFind≤5QPS令牌桶声明与校验，Cold→Warm仅经config:*(30s轮询)通道白名单，Cold→Hot禁直连（越界调用拒绝+告警），盘中产出入待激活队列盘后应用（队列状态机）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infra_runtime/test_cold_plane_isolation.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
