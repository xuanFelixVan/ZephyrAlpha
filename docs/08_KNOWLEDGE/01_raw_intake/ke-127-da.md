---
module_id: KE-114
status: active
title: 10.3 DA 不做什么（防止越界）
category: documentation
---

# 10.3 DA 不做什么（防止越界）

10.3 DA 不做什么（防止越界）

| DA 不做的事 | 归属视图 |
|------------|---------|
| 字段级 schema DDL | 09_data_platform |
| 选具体存储产品（TimescaleDB vs ClickHouse vs DuckDB） | 04-TA |
| 因子计算的具体算法 | 10_research_and_factor_lab |
| 监管条款映射 | 16_compliance_and_legal |
| 加密 / 脱敏算法 | 06-Security |
| AI 自治的数据血缘自动发现 | 08_ai_engineering（未来） |

> **📊 数据流时序图**：
> - [`diagrams/data_flow.mmd`](diagrams/data_flow.mmd) — 跨域核心数据流（L00→L02→L03→L05→L06→L07 主链路）
> - [`diagrams/dataflow_terminal.mmd`](diagrams/dataflow_terminal.mmd) — 终端数据流详细时序

---
