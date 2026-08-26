---
blueprint_id: MOD-FE-008
module_name: lineage_view_renderer
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
path: src/zephyr/frontend/lineage_view_renderer.py
granularity: file
---

# MOD-FE-008 lineage_view_renderer 蓝图（血缘DAG渲染数据器）

> **module_id**: MOD-FE-008 | **域**: D_FRONTEND | **优先级**: P2
> **来源**: B10-02413（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-009，A1 M8-S08）
> 代码：`src/zephyr/frontend/lineage_view_renderer.py`

## 0. 定位

血缘DAG渲染数据：上下游高亮闭包（选中实体N跳邻居）+变更影响范围着色（变更实体→下游影响集合着色映射）+布局分层数据。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/frontend/test_lineage_view_renderer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
