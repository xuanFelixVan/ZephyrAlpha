---
blueprint_id: MOD-DATA_GOV-009
module_name: market_data_aggregates
domain: D_DATA_GOV
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
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/market_data_aggregates.py
granularity: file
---

# MOD-DATA_GOV-009 market_data_aggregates 蓝图（行情聚合根与生命周期）

> **module_id**: MOD-DATA_GOV-009 | **域**: D_DATA_GOV | **优先级**: P2
> **来源**: B1-00648（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-006，C2 130~136）
> 代码：`src/zephyr/data_governance/market_data_aggregates.py`

## 0. 定位

MarketData/Instrument轻量聚合（值对象Bar/OHLCV/FinancialReport为frozen dataclass+聚合根版本不变量）+仓储接口协议（get/save/snapshot语义，对齐ch_reader/pit_query注入）+跨域保留归档策略协调表（TTL/归档目标/演练频次登记）+恢复演练记录，不建完整DDD分层。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data_governance/test_market_data_aggregates.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
