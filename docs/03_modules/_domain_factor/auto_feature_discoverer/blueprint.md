---
blueprint_id: MOD-FAC-001
module_name: auto_feature_discoverer
domain: D_FACTOR
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
domain_id: D_FACTOR
path: src/zephyr/research/auto_feature_discoverer.py
granularity: file
---

# MOD-FAC-001 auto_feature_discoverer 蓝图（AI自动特征发现器）

> **module_id**: MOD-FAC-001 | **域**: D_FACTOR | **优先级**: P2
> **来源**: B1-00630（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-016，C2 74）
> 代码：`src/zephyr/research/auto_feature_discoverer.py`

## 0. 定位

价量算子模板库（算术/滚动统计算子词表闭合）笛卡尔组合批量生成特征+IC/IR初筛（注入ic计算器）+TopN人工确认队列（未确认不入库）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/research/test_auto_feature_discoverer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
