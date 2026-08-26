---
blueprint_id: MOD-FE-010
module_name: compliance_dashboard
domain: D_FRONTEND
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
domain_id: D_FRONTEND
path: src/zephyr/frontend/compliance_dashboard.py
granularity: file
---

# MOD-FE-010 compliance_dashboard 蓝图（合规仪表盘数据器）

> **module_id**: MOD-FE-010 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B14-04672（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-011，A9 M36-S07）
> 代码：`src/zephyr/frontend/compliance_dashboard.py`

## 0. 定位

合规仪表盘数据：规则命中率/审查异常清单/证据链完整度/整改任务看板四卡数据聚合（数据源注入）+趋势序列（按日窗口）。GRC仪表盘思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_compliance_dashboard.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
