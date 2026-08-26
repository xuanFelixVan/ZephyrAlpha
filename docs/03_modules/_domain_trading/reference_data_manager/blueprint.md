---
blueprint_id: MOD-TRADING-014
module_name: reference_data_manager
domain: D_TRADING
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
domain_id: D_TRADING
path: src/zephyr/trading/reference_data_manager.py
granularity: file
---

# MOD-TRADING-014 reference_data_manager 蓝图（证券主数据管理器）

> **module_id**: MOD-TRADING-014 | **域**: D_TRADING | **优先级**: P2
> **来源**: B14-04639（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-TRD-013，A9 D-TRADING-14）
> 代码：`src/zephyr/trading/reference_data_manager.py`

## 0. 定位

主数据SSOT：代码/名称/行业分类/涨跌停规则/ST与退市标记/交易日历统一登记（注入sqlite连接）+日终刷新+版本号递增+查询API（监控与风控经API引用禁各自维护副本语义）+变更审计回调。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/trading/test_reference_data_manager.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
