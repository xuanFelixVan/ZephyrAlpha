---
blueprint_id: MOD-INF-086
module_name: storage_cost_calculator
domain: D_INFRA_OPS
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
domain_id: D_INFRA_OPS
path: src/zephyr/infra_ops/storage_cost_calculator.py
granularity: file
---

# MOD-INF-086 storage_cost_calculator 蓝图（存储成本量化核算器）

> **module_id**: MOD-INF-086 | **域**: D_INFRA_OPS | **优先级**: P2
> **来源**: B13-04333（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-004，A3数据架构）
> 代码：`src/zephyr/infra_ops/storage_cost_calculator.py`

## 0. 定位

存储成本核算器：按热/温/冷层统计占用字节/TB单价(本地盘折旧折算)/月成本，cost_calculator()输出对比报表（字典结构），归档策略收益量化（归档前后成本差）。注入层占用采集器。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infra_ops/test_storage_cost_calculator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
