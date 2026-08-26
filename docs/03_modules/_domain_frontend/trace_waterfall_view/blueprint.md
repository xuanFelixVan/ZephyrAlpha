---
blueprint_id: MOD-FE-009
module_name: trace_waterfall_view
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
path: src/zephyr/frontend/trace_waterfall_view.py
granularity: file
---

# MOD-FE-009 trace_waterfall_view 蓝图（端到端追踪瀑布视图器）

> **module_id**: MOD-FE-009 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B14-04627（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-010，A9 D-FRONTEND-15）
> 代码：`src/zephyr/frontend/trace_waterfall_view.py`

## 0. 定位

跨进程Trace瀑布图数据：四视图（交易主链路/数据链/AI运维链/GPU推理链词表闭合）+trace_id检索（注入span存储）+span瀑布布局（父子嵌套时间轴）+采样率配置+慢链路高亮（阈值映射）。canonical承接FE-005归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_trace_waterfall_view.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
