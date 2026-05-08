---
module_id: KE-documentat-3_2_container_inventory-004
title: 3.2 Container inventory / 容器清单
category: documentation
---

# 3.2 Container inventory / 容器清单

3.2 Container inventory / 容器清单

| Container / 容器 | Tech / 技术 | `src/` layer / 对应层 | Responsibility / 职责边界 |
|----------------|-----------|---------------------|--------------------------|
| **Data Pipeline** | Python | `l00_data_source` | 行情数据接入、标准化、质量门禁、落库 |
| **Factor Engine** | Python | `l02_alpha_factor` + `l03_signal_generation` | Alpha 因子计算、舆情信号提取、预测信号生成 |
| **Risk Engine** | Python | `l04_risk_management` | 风险度量、限额执行、止损触发 |
| **Portfolio Engine** | Python | `l05_portfolio_construction` | 权重优化、组合构建、回测框架 |
| **Execution Engine** | Python | `l06_trade_execution` | OMS、SOR、委托路由、执行前风控 |
| **Post-Trade Analytics** | Python | `l07_post_trade_analytics` | 绩效归因、交易复盘、报告生成 |
| **AI Agent Ops** | Python | `l08_human_ai_interface` + `03_modules/_b_track_interfaces/` | Agent 规则、记忆管理、上下文服务、LLM 调用编排 |
| **Data Storage** | PostgreSQL + TimescaleDB（主存储）/ DuckDB（分析）/ Parquet（归档） | — | 行情、因子信号、持仓、交易数据的持久化存储；experimental 确定选型见 04-TA §Q5-1 |
| **Documentation Store** | Git + Markdown | — | 架构文档、决策记录；`docs/` 即文档存储本身 |
