---
blueprint_id: MOD-FAC-007
module_name: strategy_iteration_upgrader
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
path: src/zephyr/research/strategy_iteration_upgrader.py
granularity: file
---

# MOD-FAC-007 strategy_iteration_upgrader 蓝图（策略迭代升级器）

> **module_id**: MOD-FAC-007 | **域**: D_FACTOR | **优先级**: P2
> **来源**: B10-02221（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-022，A1 D-RESEARCH-17）
> 代码：`src/zephyr/research/strategy_iteration_upgrader.py`

## 0. 定位

归因→权重调整建议（归因报告注入解析）+新因子候选生成（弱点方向映射算子库）+产物入hypothesis_registry回调+迭代历史留痕。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/research/test_strategy_iteration_upgrader.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
