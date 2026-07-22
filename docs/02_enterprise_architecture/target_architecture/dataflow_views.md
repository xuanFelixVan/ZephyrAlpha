---
module_id: VIEW-TA-DATAFLOW
title: 数据流图
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

# 数据流图

> ⚠️ **价值评估中** — 本文档由独立 `.mmd` 转换为内嵌 mermaid，供挨个评估其架构价值。

---

## business value stream

> Source: 04_architecture_principles_decisions/business_principles.md

```mermaid
flowchart LR
    subgraph INPUT["① 输入 / Input"]
        MH["Market Hypothesis<br/>市场假设<br/>(S2 Quant)"]
        MD["Market Data<br/>市场数据<br/>(S10 Vendor / S6 Data)"]
    end

    subgraph RESEARCH["② Research & Factor / 研究与因子 [C02]"]
        FR["Factor Research<br/>因子研发<br/>LT 5-20d / PT 2-8h / C&A 70%<br/>Owner: S2"]
        FL["Factor Library<br/>因子入库<br/>LT 15-60min / PT 10-30min / C&A 98%<br/>Owner: S2 + S6"]
    end

    subgraph SIGNAL["③ Signal / 信号 [C03/C04]"]
        MT["Model Train/Deploy<br/>模型训练部署<br/>LT 2-24h / PT 30min-4h / C&A 95%<br/>Owner: S7 (deferred)"]
        SG["Signal Generation<br/>信号生成<br/>LT 15-60min / PT 5-15min / C&A 98%<br/>Owner: S2"]
    end

    subgraph PORTFOLIO["④ Portfolio / 组合 [C04]"]
        PC["Portfolio Construction<br/>组合构建<br/>LT 5-15min / PT 1-5min / C&A 99%<br/>Owner: S2 → S9 (future)"]
        RC["Risk Check (pre-trade)<br/>事前风控门<br/>LT &lt;1min / PT 5-30s / C&A 99.9%<br/>Owner: S4"]
    end

    subgraph EXEC["⑤ Execution / 执行 [C05]"]
        OS["Order Submission<br/>下单<br/>LT 1-5min / PT 10-60s / C&A 99.5%<br/>Owner: S3"]
        FB["Fill &amp; Reconcile<br/>成交与对账<br/>LT intraday / PT 1-5min / C&A 99%<br/>Owner: S3 + S6"]
    end

    subgraph POST["⑥ Post-trade / 交易后 [C06]"]
        AT["Attribution &amp; PnL<br/>归因与 PnL<br/>LT T+1 / PT 10-30min / C&A 99%<br/>Owner: S2"]
    end

    subgraph FEEDBACK["⑦ Feedback / 反馈回路"]
        FD["Feedback to Research<br/>反馈至研究<br/>LT T+1 to T+5 / PT 1-4h / C&A 85%<br/>Owner: S1 + S2"]
    end

    MH --> FR
    MD --> FL
    FR --> FL
    FL --> MT
    MT --> SG
    SG --> PC
    PC --> RC
    RC -->|approved| OS
    RC -.->|rejected / rework| SG
    OS --> FB
    FB --> AT
    AT --> FD
    FD -.-> FR
    FD -.-> SG

    %% Handoffs
    classDef handoff fill:#ffe0b2,stroke:#e65100,stroke-width:2px;
    class FL,RC,OS,FB,FD handoff;

    %% Governance cross-cut
    GOV["Cross-cutting / 横向治理<br/>00_governance · 17_risk_and_controls · META_GOVERNANCE (decision logs)<br/>_b_track_interfaces · 08_knowledge"]
    GOV -.-> RESEARCH
    GOV -.-> SIGNAL
    GOV -.-> PORTFOLIO
    GOV -.-> EXEC
    GOV -.-> POST
```

---

## data flow

> 重写时间: 2026-06-26 (DM-200913 Phase4-B)
> 基于§2.1裁定: 14层降级为域属性，53域为唯一物理分类体系
> 数据源: depgraph
> 图例: 🔒 = frozen (不可变契约) | 🔓 = mutable (可变契约，状态机)
> 契约真源: architecture_model/contracts/cross_layer_contracts.yaml

```mermaid
%%{init: {'theme': 'default'}}%%
%% Data Flow Diagram — ZephyrAlpha 2.0 Core Pipeline
%% v2.0.0: 14层节点→53域节点，保留P0跨层契约标注

flowchart TD
    subgraph External["外部系统 External Systems"]
        MD["行情数据源<br/>Market Data Provider"]
        BK["券商 API<br/>Broker API"]
    end

    subgraph D_MKT_DATA_Grp["D-MKT_DATA · 行情数据 / Market Data"]
        D_MKT_DATA["D-MKT_DATA<br/>Ingestion · Standardization · Quality Gating<br/>接入 · 标准化 · 质量门禁"]
    end

    subgraph D_FACTOR_Grp["D-FACTOR · 因子 / Alpha Factor"]
        D_FACTOR["D-FACTOR<br/>Factor Calculation · Evaluation · Engineering<br/>因子计算 · 评估 · 工程"]
    end

    subgraph D_SIGNAL_Grp["D-SIGLEGACY · 信号 / Signal Generation"]
        D_SIGNAL["D-SIGLEGACY<br/>Sentiment · Signal Extraction · Predictions<br/>舆情 · 信号提取 · 预测"]
    end

    subgraph D_RISK_Grp["D-RISK · 风控 / Risk Management"]
        D_RISK["D-RISK<br/>Risk Measurement · Limits · Stop-loss<br/>风险度量 · 限额 · 止损"]
    end

    subgraph D_PF_CORE_Grp["D-PF_CORE · 组合核心 / Portfolio Construction"]
        D_PF_CORE["D-PF_CORE<br/>Weight Allocation · Optimization · Backtest<br/>权重分配 · 优化 · 回测"]
    end

    subgraph D_EX_CORE_Grp["D-EX_CORE · 执行核心 / Trade Execution"]
        D_EX_CORE["D-EX_CORE<br/>OMS · SOR · Order Execution · Pre-trade Risk<br/>OMS · SOR · 委托执行 · 执行前风控"]
    end

    subgraph D_TRADING_Grp["D-TRADING · 交易运营 / Post-Trade Analytics"]
        D_TRADING["D-TRADING<br/>Performance Attribution · Review · Reporting<br/>绩效归因 · 复盘 · 报告"]
    end

    subgraph D_ML_TRAIN_Grp["D-ML_TRAIN · 训练 / ML Platform"]
        D_ML_TRAIN["D-ML_TRAIN<br/>Model Training · Registry · Inference<br/>模型训练 · 注册 · 推理"]
    end

    subgraph D_OPS_Grp["D-OPS · 反馈循环 / System Telemetry"]
        D_OPS["D-OPS<br/>Structured Metrics · Observability<br/>结构化指标 · 可观测性"]
    end

    %% External → D-MKT_DATA
    MD -->|"REST/WebSocket<br/>原始行情数据"| D_MKT_DATA

    %% D-MKT_DATA → D-FACTOR: CTR-001 NormalizedMarketData (frozen)
    D_MKT_DATA -->|"🔒 CTR-001<br/>NormalizedMarketData<br/>[frozen]"| D_FACTOR

    %% D-FACTOR → D-SIGLEGACY: CTR-002 FactorSignal (frozen)
    D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal<br/>[frozen]"| D_SIGNAL

    %% D-FACTOR → D-RISK: CTR-002 FactorSignal (frozen)
    D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal<br/>[frozen]"| D_RISK

    %% D-FACTOR → D-PF_CORE: CTR-002 FactorSignal (frozen)
    D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal<br/>[frozen]"| D_PF_CORE

    %% D-SIGLEGACY → D-PF_CORE: 信号输入（非 P0 契约，内部调用）
    D_SIGNAL -->|"Signal<br/>预测信号"| D_PF_CORE

    %% D-RISK → D-PF_CORE: CTR-003 RiskLimits (frozen)
    D_RISK -->|"🔒 CTR-003<br/>RiskLimits<br/>[frozen]"| D_PF_CORE

    %% D-PF_CORE → D-EX_CORE: CTR-004 Order (mutable)
    D_PF_CORE -->|"🔓 CTR-004<br/>Order<br/>[mutable / 状态机]"| D_EX_CORE

    %% D-EX_CORE → BK: 委托发送
    D_EX_CORE -->|"REST/FIX<br/>委托发送"| BK
    BK -->|"成交回报"| D_EX_CORE

    %% D-EX_CORE → D-TRADING: CTR-005 Fill (frozen)
    D_EX_CORE -->|"🔒 CTR-005<br/>Fill<br/>[frozen]"| D_TRADING

    %% D-EX_CORE → D-RISK: CTR-006 PositionSnapshot (frozen) — 风控监控
    D_EX_CORE -->|"🔒 CTR-006<br/>PositionSnapshot<br/>[frozen]"| D_RISK

    %% D-TRADING → D-RISK: CTR-006 PositionSnapshot (frozen) — 复盘后风险更新
    D_TRADING -->|"🔒 CTR-006<br/>PositionSnapshot<br/>[frozen]"| D_RISK

    %% D-TRADING → D-ML_TRAIN: CTR-006 PositionSnapshot (frozen) — 战略决策
    D_TRADING -->|"🔒 CTR-006<br/>PositionSnapshot<br/>[frozen]"| D_ML_TRAIN

    %% D-TRADING → D-OPS: 绩效指标上报
    D_TRADING -->|"PnL / Risk Metrics<br/>绩效与风险指标"| D_OPS

    %% D-ML_TRAIN → D-FACTOR: 模型预测反馈
    D_ML_TRAIN -->|"ModelPrediction<br/>模型预测"| D_FACTOR

    %% D-ML_TRAIN → D-PF_CORE: 模型预测反馈
    D_ML_TRAIN -->|"ModelPrediction<br/>模型预测"| D_PF_CORE

    %% D-RISK → D-OPS: 风险指标上报
    D_RISK -->|"Risk Metrics<br/>风险指标"| D_OPS

    %% 样式定义
    style D_MKT_DATA fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style D_FACTOR fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style D_SIGNAL fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style D_RISK fill:#fdf4ff,stroke:#a855f7,stroke-width:2px
    style D_PF_CORE fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style D_EX_CORE fill:#fff7ed,stroke:#f97316,stroke-width:2px
    style D_TRADING fill:#fefce8,stroke:#eab308,stroke-width:2px
    style D_ML_TRAIN fill:#f5f3ff,stroke:#7c3aed,stroke-width:2px
    style D_OPS fill:#f0f9ff,stroke:#0ea5e9,stroke-width:2px
    style MD fill:#e2e8f0,stroke:#64748b
    style BK fill:#e2e8f0,stroke:#64748b
```

---

## dataflow terminal

> 重写时间: 2026-06-26 (DM-200913 Phase4-B)
> 基于§2.1裁定: 14层降级为域属性，53域为唯一物理分类体系
> 数据源: depgraph
> 图例: 🔒 = frozen (不可变契约) | 🔓 = mutable (可变契约，状态机)
> 契约真源: architecture_model/contracts/cross_layer_contracts.yaml

```mermaid
%%{init: {'theme': 'default'}}%%
%% Dataflow Terminal Diagram — ZephyrAlpha 2.0
%% v2.0.0: 14层节点→53域节点，保留P0跨层契约标注和组件级细节

flowchart TD

    %% ── External Sources ──────────────────────────────────────────
    subgraph EXT["External Systems / 外部系统"]
        MD_EXT["Market Data Provider<br/>行情数据源<br/>(REST / WebSocket)"]
        ALT_EXT["Alternative Data<br/>另类数据源<br/>(REST / file)"]
        BROKER_EXT["Broker API<br/>券商 API<br/>(REST / FIX)"]
        LLM_EXT["LLM Providers<br/>LLM 服务商<br/>(REST)"]
        FEISHU_EXT["Feishu<br/>飞书<br/>(REST Webhook)"]
    end

    %% ── D-MKT_DATA 行情数据 ───────────────────────────────────────
    subgraph D_MKT_DATA["D-MKT_DATA · 行情数据 / Market Data"]
        MKT_CONN["connectors/<br/>数据源适配器"]
        MKT_NORM["normalizers/<br/>标准化"]
        MKT_QG["quality/<br/>质量门禁"]
        MKT_STORE["storage/<br/>数据落库"]
        MKT_CACHE["cache/<br/>缓存"]
    end

    %% ── D-SHARED 基础设施 (cross-cutting) ────────────────────────
    D_SHARED["D-SHARED · 基础设施 / Infrastructure<br/>config · logging · exceptions · runtime<br/>配置 · 日志 · 异常 · 运行时<br/>⟵ 所有域依赖，省略连线"]

    %% ── D-FACTOR 因子 ─────────────────────────────────────────────
    subgraph D_FACTOR["D-FACTOR · 因子 / Alpha Factor"]
        FAC_BASE["FactorBase<br/>因子基类契约 🔒"]
        FAC_REG["FactorRegistry<br/>因子注册表 🔒"]
        FAC_FACTORS["factors/<br/>具体因子实现<br/>(可扩展 ∞)"]
        FAC_EVAL["evaluation/<br/>IC · IR · 衰减评估"]
        FAC_PIPE["pipeline/<br/>因子计算流水线"]
    end

    %% ── D-SIGLEGACY 信号 ─────────────────────────────────────────────
    subgraph D_SIGNAL["D-SIGLEGACY · 信号 / Signal Generation"]
        SIG_SENT["sentiment/<br/>舆情分析"]
        SIG_SIG["signals/<br/>复合信号构建"]
        SIG_PRED["predictions/<br/>预测模型推理"]
    end

    %% ── D-RISK 风控 ───────────────────────────────────────────────
    subgraph D_RISK["D-RISK · 风控 / Risk Management"]
        RISK_METRICS["metrics/<br/>VaR · CVaR · 回撤 · Beta"]
        RISK_LIMITS["limits/<br/>持仓限额执行"]
        RISK_SL["stop_loss/<br/>止损触发"]
        RISK_MON["monitor/<br/>实时风险监控"]
    end

    %% ── D-PF_CORE 组合核心 ────────────────────────────────────────
    subgraph D_PF_CORE["D-PF_CORE · 组合核心 / Portfolio Construction"]
        PF_BASE["StrategyBase<br/>策略基类契约 🔒"]
        PF_REG["StrategyRegistry<br/>策略注册表 🔒"]
        PF_STRATS["strategies/<br/>具体策略实现<br/>(可扩展 ∞)"]
        PF_OPT["optimization/<br/>均值方差 · 风险平价"]
        PF_REB["rebalancing/<br/>再平衡计划生成"]
        PF_BT["backtest/<br/>事件驱动回测引擎"]
    end

    %% ── D-EX_CORE 执行核心 ───────────────────────────────────────
    subgraph D_EX_CORE["D-EX_CORE · 执行核心 / Trade Execution"]
        EX_PT["pre_trade/<br/>执行前风控"]
        EX_OMS["oms/<br/>委托生命周期 OMS"]
        EX_SOR["sor/<br/>智能路由 SOR"]
        EX_IFACE["BrokerInterface<br/>券商接口契约 🔒"]
        EX_ADP["adapters/<br/>具体券商适配器<br/>(可扩展 ∞)"]
    end

    %% ── D-TRADING 交易运营 ────────────────────────────────────────
    subgraph D_TRADING["D-TRADING · 交易运营 / Post-Trade Analytics"]
        TRD_ATTR["attribution/<br/>绩效归因"]
        TRD_REV["review/<br/>执行质量 TCA · 滑点"]
        TRD_RPT["reports/<br/>报告生成"]
    end

    %% ── D-FRONTEND 前端 ──────────────────────────────────────────
    subgraph D_FRONTEND["D-FRONTEND · 前端 / Human-AI Interface"]
        FE_CLI["cli/<br/>操作者入口"]
        FE_ORCH["orchestration/<br/>人机协作编排"]
        FE_NOTIF["notifications/<br/>飞书 · 告警分发"]
    end

    %% ── D-COMPLIANCE 合规 (横切) ─────────────────────────────────
    D_COMPLIANCE["D-COMPLIANCE · 合规 / Governance & Compliance<br/>合规校验 · 审计痕迹 · 规则引擎<br/>⟵ 横向贯穿所有业务域"]

    %% ── D-INTELLIGENCE 战略决策 ───────────────────────────────────
    D_INTELLIGENCE["D-INTELLIGENCE · 战略决策 / Strategic Decision<br/>长期配置 · 决策支持 · 战略报告<br/>⟵ 消费所有域输出"]

    %% ── AI Agent Ops (D-INTELLIGENCE + D-AUTONOMY_CORE) ──────────
    AI_OPS["AI Agent Ops<br/>D-INTELLIGENCE + D-AUTONOMY_CORE<br/>LLM 调用 · 记忆 · 实验研究"]

    %% ══════════════════════════════════════════════════════════════
    %% DATA FLOW EDGES — 主流数据流（含 P0 跨域数据契约标注）
    %% ══════════════════════════════════════════════════════════════

    MD_EXT -->|"RawMarketData"| MKT_CONN
    ALT_EXT -->|"RawAlternativeData"| MKT_CONN

    MKT_CONN --> MKT_NORM
    MKT_NORM --> MKT_QG
    MKT_QG -->|"QualityGatePass"| MKT_STORE
    MKT_QG -->|"QualityGatePass"| MKT_CACHE
    MKT_STORE -->|"🔒 CTR-001<br/>NormalizedMarketData"| FAC_PIPE
    MKT_CACHE -->|"🔒 CTR-001<br/>NormalizedMarketData"| FAC_PIPE

    FAC_PIPE --> FAC_BASE
    FAC_BASE --> FAC_FACTORS
    FAC_FACTORS --> FAC_EVAL
    FAC_EVAL -->|"🔒 CTR-002<br/>FactorSignal"| SIG_SIG
    FAC_REG -.->|"注册/发现"| FAC_FACTORS

    ALT_EXT -->|"SentimentRawData"| SIG_SENT
    SIG_SENT -->|"SentimentSignal"| SIG_SIG
    SIG_PRED -->|"PredictionSignal"| SIG_SIG
    SIG_SIG -->|"CompositeSignal"| RISK_METRICS
    SIG_SIG -->|"CompositeSignal"| PF_OPT

    RISK_METRICS --> RISK_LIMITS
    RISK_LIMITS -->|"🔒 CTR-003<br/>RiskLimits"| PF_OPT
    RISK_SL -.->|"StopLoss触发"| EX_OMS
    RISK_MON -.->|"RiskAlert"| FE_NOTIF

    PF_BASE --> PF_STRATS
    PF_STRATS --> PF_OPT
    PF_REG -.->|"注册/发现"| PF_STRATS
    PF_OPT --> PF_REB
    PF_REB -->|"🔓 CTR-004<br/>Order"| EX_PT
    PF_BT -.->|"回测反馈"| FAC_EVAL

    EX_PT -->|"PreTradeCheckPass"| EX_OMS
    EX_OMS --> EX_SOR
    EX_SOR --> EX_IFACE
    EX_IFACE --> EX_ADP
    EX_ADP -->|"Order (REST/FIX)"| BROKER_EXT
    BROKER_EXT -->|"🔒 CTR-005<br/>Fill + 🔒 CTR-006<br/>PositionSnapshot"| EX_ADP
    EX_ADP -->|"FillEvent"| EX_OMS
    EX_OMS -->|"🔒 CTR-005<br/>Fill + 🔒 CTR-006<br/>PositionSnapshot"| TRD_ATTR

    TRD_ATTR --> TRD_REV
    TRD_REV --> TRD_RPT
    TRD_RPT -->|"PerformanceReport"| FE_ORCH
    TRD_ATTR -.->|"归因反馈"| FAC_EVAL

    FE_ORCH -->|"Alert / Report"| FE_NOTIF
    FE_NOTIF -->|"通知"| FEISHU_EXT
    FE_CLI -.->|"操作者指令"| FE_ORCH

    %% ── AI Ops 横向接入 ───────────────────────────────────────────
    AI_OPS -->|"LLM推理请求"| LLM_EXT
    LLM_EXT -->|"LLM推理结果"| AI_OPS
    AI_OPS -.->|"实验因子/策略"| FAC_PIPE
    AI_OPS -.->|"辅助决策"| PF_OPT
    AI_OPS -.->|"知识沉淀"| TRD_RPT

    %% ── Compliance 横切 ───────────────────────────────────────────
    D_COMPLIANCE -.->|"合规校验贯穿"| MKT_QG
    D_COMPLIANCE -.->|"合规校验贯穿"| EX_PT
    D_COMPLIANCE -.->|"审计痕迹"| TRD_RPT

    %% ── Strategic 消费 ────────────────────────────────────────────
    TRD_RPT -->|"绩效洞察"| D_INTELLIGENCE
    RISK_METRICS -->|"风险指标"| D_INTELLIGENCE

    %% ══════════════════════════════════════════════════════════════
    %% STYLES
    %% ══════════════════════════════════════════════════════════════
    style EXT fill:#f8fafc,stroke:#94a3b8
    style D_MKT_DATA fill:#fef2f2,stroke:#ef4444
    style D_FACTOR fill:#f0fdf4,stroke:#22c55e
    style D_SIGNAL fill:#eff6ff,stroke:#3b82f6
    style D_RISK fill:#fdf4ff,stroke:#a855f7
    style D_PF_CORE fill:#ecfdf5,stroke:#10b981
    style D_EX_CORE fill:#fff7ed,stroke:#f97316
    style D_TRADING fill:#fefce8,stroke:#eab308
    style D_FRONTEND fill:#eff6ff,stroke:#3b82f6
    style D_SHARED fill:#f8fafc,stroke:#94a3b8
    style D_COMPLIANCE fill:#fef2f2,stroke:#ef4444
    style D_INTELLIGENCE fill:#f5f3ff,stroke:#7c3aed
    style AI_OPS fill:#e0f2fe,stroke:#0284c7

    %% 🔒 标注 OCP 扩展点契约节点
    style FAC_BASE fill:#bbf7d0,stroke:#16a34a
    style FAC_REG fill:#bbf7d0,stroke:#16a34a
    style PF_BASE fill:#bbf7d0,stroke:#16a34a
    style PF_REG fill:#bbf7d0,stroke:#16a34a
    style EX_IFACE fill:#bbf7d0,stroke:#16a34a
```

---

## deployment experimental

> Source: technology_principles.md §4.1（experimental vs Post-Activation 部署框架）

```mermaid
%%{init: {'theme': 'default'}}%%
graph TD
    subgraph DEV["开发机（Windows 10/11）"]
        subgraph VENV["Python Virtual Env"]
            APP["ZephyrAlpha Main Process\n53域全链路"]
            HOOKS["Git Hooks (pre-commit)"]
        end
        subgraph STORAGE["本地存储"]
            PARQUET["Data Store (PostgreSQL + TimescaleDB + DuckDB + Parquet)"]
            DOCS["docs/ (Git + Markdown)"]
        end
    end
    subgraph EXT["外部系统"]
        MKT_DATA["行情数据源"]
        BROKER["券商网关"]
        LLM_API["LLM 提供商"]
        FEISHU["飞书 Webhook"]
    end
    subgraph CI["CI (GitHub Actions)"]
        CI_SCAN["ci_audit/ 全仓扫描"]
    end
    MKT_DATA -->|行情| APP
    APP -->|委托| BROKER
    BROKER -->|成交回报| APP
    APP -->|LLM 推理| LLM_API
    APP -->|通知| FEISHU
    APP -->|写入| PARQUET
    APP -->|读写| DOCS

    style DEV fill:#eff6ff,stroke:#3b82f6
    style EXT fill:#fef2f2,stroke:#ef4444
    style CI fill:#f0fdf4,stroke:#22c55e
```
