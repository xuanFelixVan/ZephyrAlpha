---
blueprint_id: MOD-FBL-002
module_name: module_matcher
domain: D_FEEDBACK_LOOP
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
domain_id: D_FEEDBACK_LOOP
path: src/zephyr/feedback_loop/module_matcher.py
granularity: file
---

# MOD-FBL-002 module_matcher 蓝图（模块匹配器）

> **module_id**: MOD-FBL-002 | **域**: D_FEEDBACK_LOOP | **优先级**: P2
> **来源**: B12-03549（AUD-DRAFT-001-DIGEST P2 波 P2-W14，CAND-FBL-004，B12）
> 代码：`src/zephyr/feedback_loop/module_matcher.py`

## 0. 定位

Module Matcher：提取知识包功能需求→按capability_tags注册表搜索→embedding语义相似度（注入embedder）→EXACT(>0.85)/PARTIAL(0.5~0.85)/NO_MATCH(<0.5)三档判定输出（阈值边界恰等归低档）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/feedback_loop/test_module_matcher.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
