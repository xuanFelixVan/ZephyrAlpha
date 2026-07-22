---
module_id: VIEW-TA-C4L1L2
title: C4-L1/L2 系统上下文与容器图
doc_type: architecture_view
status: Active
version: 0.1.0
owner: ZephyrAlpha-Owner
valid_from: 2026-07-22
ttl: permanent
tags:
- architecture-view
- pending-review
---

# C4-L1/L2 系统上下文与容器图

> ⚠️ **价值评估中** — 本文档由独立 `.mmd` 转换为内嵌 mermaid，供挨个评估其架构价值。

---

## c4 l1 system context

```mermaid
%%{init: {'theme': 'default'}}%%
C4Context
    title System Context — ZephyrAlpha 2.0

    Person(operator, "Independent Operator", "独立操作者<br/>System owner, strategy designer,<br/>risk decision maker<br/>系统拥有者、策略设计者、风险决策者")

    Person(ai_collab, "AI Collaborators", "AI 协作者<br/>Kimi (Trae) + Opus/Sonnet (Cursor)<br/>Diverge + converge workflow<br/>发散+收口工作流")

    System(zephyr, "ZephyrAlpha 2.0", "Quantitative investment system<br/>量化投资系统<br/>Full lifecycle: Data→Research→Model→Strategy→Execution→Report<br/>全生命周期：数据→研究→模型→策略→执行→报告")

    System_Ext(broker, "Broker API", "券商 API<br/>Trade order routing &amp; execution<br/>交易委托路由与执行")

    System_Ext(market_data, "Market Data Provider", "行情数据源<br/>Historical + realtime market data<br/>历史+实时行情数据")

    System_Ext(llm, "LLM Providers", "LLM 服务商<br/>OpenAI / Anthropic / etc.<br/>AI inference &amp; reasoning<br/>AI 推理与推断")

    System_Ext(feishu, "Feishu", "飞书<br/>Notification &amp; report distribution<br/>通知与报告分发")

    Rel(operator, zephyr, "Configures, monitors, decides", "策略配置、监控与决策")
    Rel(ai_collab, zephyr, "Designs docs, reviews architecture", "设计文档、审查架构")
    Rel(zephyr, broker, "Sends orders", "发送委托 (REST/FIX)")
    Rel(broker, zephyr, "Returns fills & positions", "返回成交与持仓")
    Rel(market_data, zephyr, "Provides market data", "提供行情数据 (REST/WS)")
    Rel(zephyr, llm, "AI inference calls", "AI 推理调用 (REST)")
    Rel(zephyr, feishu, "Sends reports & alerts", "发送报告与告警")
```

---

## c4 l2 containers

> 重写时间: 2026-06-26 (DM-200913 Phase4-B)
> 基于§2.1裁定: 14层降级为域属性，53域为唯一物理分类体系
> 数据源: depgraph
> 图例: 🔒 = frozen (不可变契约) | 🔓 = mutable (可变契约，状态机)
> 契约真源: architecture_model/contracts/cross_layer_contracts.yaml

```mermaid
%%{init: {'theme': 'default'}}%%
%% C4-L2 Container Diagram — ZephyrAlpha 2.0
%% v2.0.0: 14层容器→53域容器，保留P0跨层契约标注

C4Container
    title Container Diagram — ZephyrAlpha 2.0
    title (with Cross-Domain Contracts / 含跨域数据契约标注)

    Person(operator, "Independent Operator", "独立操作者")

    System_Boundary(zephyr, "ZephyrAlpha 2.0") {
        Container(data_pipeline, "Data Pipeline", "Python / D-MKT_DATA", "Market data ingestion,<br/>standardization, quality gating<br/>行情数据接入、标准化、质量门禁")

        Container(factor_engine, "Factor Engine", "Python / D-FACTOR+D-SIGLEGACY", "Alpha factor calculation,<br/>signal generation<br/>Alpha 因子计算、信号生成")

        Container(risk_engine, "Risk Engine", "Python / D-RISK", "Risk measurement,<br/>limits enforcement<br/>风险度量、限额执行")

        Container(portfolio_engine, "Portfolio Engine", "Python / D-PF_CORE", "Portfolio optimization,<br/>backtesting<br/>组合优化、回测")

        Container(execution_engine, "Execution Engine", "Python / D-EX_CORE", "OMS, SOR,<br/>order routing<br/>OMS、SOR、委托路由")

        Container(analytics, "Post-Trade Analytics", "Python / D-TRADING", "Performance attribution,<br/>reporting<br/>绩效归因、报告")

        Container(ai_ops, "AI Agent Ops", "Python / D-FRONTEND + D-AUTONOMY_CORE", "Agent rules, memory,<br/>context management<br/>Agent 规则、记忆、上下文")

        ContainerDb(storage, "Data Storage", "PostgreSQL + TimescaleDB / DuckDB / Parquet", "Market data, factor signals,<br/>positions, trades<br/>行情、因子、持仓、交易数据")

        ContainerDb(doc_store, "Documentation Store", "Git + Markdown", "Architecture docs,<br/>decision records<br/>架构文档、决策记录")
    }

    System_Ext(broker, "Broker API", "券商 API")
    System_Ext(market_data, "Market Data", "行情数据源")
    System_Ext(llm, "LLM Providers", "LLM 服务商")

    Rel(operator, ai_ops, "Interacts via", "交互 (UI/CLI)")
    Rel(market_data, data_pipeline, "Provides data", "行情数据")
    Rel(data_pipeline, storage, "Stores processed data", "写入")

    %% P0 Cross-Domain Contracts / 跨域数据契约承重墙
    %% 契约真源: cross_layer_contracts.yaml
    %% CTR-001: NormalizedMarketData (frozen) — D-MKT_DATA → D-FACTOR
    Rel(data_pipeline, factor_engine, "CTR-001<br/>NormalizedMarketData<br/>[frozen]", "标准化行情数据")

    %% CTR-002: FactorSignal (frozen) — D-FACTOR → D-SIGLEGACY/D-RISK/D-PF_CORE
    Rel(factor_engine, risk_engine, "CTR-002<br/>FactorSignal<br/>[frozen]", "因子信号")
    Rel(factor_engine, portfolio_engine, "CTR-002<br/>FactorSignal<br/>[frozen]", "因子信号")

    %% CTR-003: RiskLimits (frozen) — D-RISK → D-PF_CORE
    Rel(risk_engine, portfolio_engine, "CTR-003<br/>RiskLimits<br/>[frozen]", "风险限额")

    %% CTR-004: Order (mutable) — D-PF_CORE → D-EX_CORE
    Rel(portfolio_engine, execution_engine, "CTR-004<br/>Order<br/>[mutable]", "委托指令")

    %% CTR-005: Fill (frozen) — D-EX_CORE → D-TRADING
    Rel(execution_engine, analytics, "CTR-005<br/>Fill<br/>[frozen]", "成交回报")

    %% CTR-006: PositionSnapshot (frozen) — D-EX_CORE/D-TRADING → D-RISK/D-ML_TRAIN
    Rel(execution_engine, risk_engine, "CTR-006<br/>PositionSnapshot<br/>[frozen]", "持仓快照")

    Rel(execution_engine, broker, "Routes orders", "发送委托")
    Rel(broker, execution_engine, "Fills", "成交回报")
    Rel(ai_ops, llm, "AI inference", "AI 推理")
    Rel(ai_ops, doc_store, "Reads/writes docs", "读写文档")
```
