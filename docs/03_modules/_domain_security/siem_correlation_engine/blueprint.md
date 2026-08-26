---
blueprint_id: MOD-SEC-025
module_name: siem_correlation_engine
domain: D_SECURITY
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
domain_id: D_SECURITY
path: src/zephyr/security/siem_correlation_engine.py
granularity: file
---

# MOD-SEC-025 siem_correlation_engine 蓝图（SIEM跨域关联引擎）

> **module_id**: MOD-SEC-025 | **域**: D_SECURITY | **优先级**: P2
> **来源**: B12-03820（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SEC-006，B12）
> 代码：`src/zephyr/security/siem_correlation_engine.py`

## 0. 定位

SIEM关联规则引擎：Sigma风格yaml规则注册（同主体/同会话滑动时间窗多域事件序列聚合，如注入→越权→数据导出链）+命中提升严重度+告警分级路由（P0/P1/系统级立即通知语义，P2/P3每日汇总语义，注入时钟）+复用security_event_bus路由。ML异常检测不建。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/security/test_siem_correlation_engine.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
