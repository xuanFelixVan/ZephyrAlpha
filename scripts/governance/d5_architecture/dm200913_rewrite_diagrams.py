"""DM-200913 Phase4-B: 重写9个14层相关图表为52域派生

基于§2.1裁定，将 diagrams/ 下9个图表从14层(L00-L13)节点改为52域节点。
数据源: depgraph.db
保留: P0跨层契约标注(CTR-001~CTR-006)、C4层级语义、业务数据流。
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
DIAGRAMS_DIR = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams")

NOW = datetime.now().strftime("%Y-%m-%d")
HEADER = f"""%% 重写时间: {NOW} (DM-200913 Phase4-B)
%% 基于§2.1裁定: 14层降级为域属性，52域为唯一物理分类体系
%% 数据源: depgraph.db
%% 图例: 🔒 = frozen (不可变契约) | 🔓 = mutable (可变契约，状态机)
%% 契约真源: architecture_model/contracts/cross_layer_contracts.yaml
"""


def get_domain_stats():
    """从depgraph.db获取域统计"""
    conn = sqlite3.connect(str(DEPGRAPH_DB))
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name, d.layer_id,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as nodes,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as prod
           FROM domains d ORDER BY d.layer_id, d.domain_id"""
    )
    stats = {r[0]: {"name": r[1], "layer": r[2] or "N/A", "nodes": r[3], "prod": r[4]} for r in cur.fetchall()}
    conn.close()
    return stats


# ============================================================
# 1. integration_topology.mmd — 集成拓扑图
# ============================================================
def write_integration_topology():
    content = HEADER + f"""
%% Source: integration_architecture.md §3
%% v2.0.0: 14层节点→52域节点，保留P0跨层契约标注

graph LR
    subgraph External["外部系统 External Systems"]
        MD["行情数据源<br/>Market Data Provider<br/>(EI-002)"]
        BK["券商 API<br/>Broker API<br/>(EI-001)"]
        LLM["LLM 服务商<br/>LLM Providers<br/>(EI-003)"]
        FS["飞书 Feishu<br/>(EI-004)"]
        ALT["另类数据源<br/>Alternative Data<br/>(EI-005)"]
    end

    subgraph ACL_Layer["反腐层 Anti-Corruption Layer"]
        CONN["D-MKT_DATA connectors/<br/>(ACL for market data)"]
        BROKER_A["D-EX_CORE adapters/<br/>(ACL for broker)"]
        LLM_A["D-FRONTEND/<br/>(ACL for LLM)"]
    end

    subgraph Core["ZephyrAlpha Core Domains (depgraph.db派生)"]
        D_MKT_DATA["D-MKT_DATA<br/>行情数据"]
        D_ALT_DATA["D-ALT_DATA<br/>另类数据"]
        D_FACTOR["D-FACTOR<br/>因子"]
        D_SIGNAL["D-SIGNAL<br/>信号"]
        D_RISK["D-RISK<br/>风控"]
        D_PF_CORE["D-PF_CORE<br/>组合核心"]
        D_EX_CORE["D-EX_CORE<br/>执行核心"]
        D_TRADING["D-TRADING<br/>交易运营"]
        D_REPORTING["D-REPORTING<br/>报告"]
        D_FRONTEND["D-FRONTEND<br/>前端"]
        D_ML_TRAIN["D-ML_TRAIN<br/>训练"]
        D_OPS["D-OPS<br/>反馈循环"]
    end

    subgraph Notify["通知输出 Output"]
        FS2["飞书 Feishu<br/>报告/通知"]
    end

    MD -- "REST/WebSocket<br/>行情数据" --> CONN
    ALT -- "REST/File<br/>另类数据" --> CONN
    CONN --> D_MKT_DATA
    BK -- "REST/FIX<br/>订单/成交" --> BROKER_A
    BROKER_A --> D_EX_CORE
    LLM -- "REST<br/>OpenAI-compatible" --> LLM_A
    LLM_A --> D_FRONTEND
    D_FRONTEND -- "决策/报告" --> FS2

    %% P0 Cross-Layer Contracts / 跨层数据契约承重墙
    %% 契约真源: cross_layer_contracts.yaml
    %% CTR-001: NormalizedMarketData (frozen) — D-MKT_DATA → D-FACTOR
    D_MKT_DATA -- "🔒 CTR-001<br/>NormalizedMarketData<br/>D-MKT_DATA → D-FACTOR" --> D_FACTOR

    %% CTR-002: FactorSignal (frozen) — D-FACTOR → D-SIGNAL/D-RISK/D-PF_CORE
    D_FACTOR -- "🔒 CTR-002<br/>FactorSignal<br/>D-FACTOR → D-SIGNAL" --> D_SIGNAL
    D_FACTOR -- "🔒 CTR-002<br/>FactorSignal<br/>D-FACTOR → D-RISK" --> D_RISK
    D_FACTOR -- "🔒 CTR-002<br/>FactorSignal<br/>D-FACTOR → D-PF_CORE" --> D_PF_CORE

    %% CTR-003: RiskLimits (frozen) — D-RISK → D-PF_CORE
    D_RISK -- "🔒 CTR-003<br/>RiskLimits<br/>D-RISK → D-PF_CORE" --> D_PF_CORE

    %% CTR-004: Order (mutable) — D-PF_CORE → D-EX_CORE
    D_PF_CORE -- "🔓 CTR-004<br/>Order<br/>D-PF_CORE → D-EX_CORE" --> D_EX_CORE

    %% CTR-005: Fill (frozen) — D-EX_CORE → D-TRADING
    D_EX_CORE -- "🔒 CTR-005<br/>Fill<br/>D-EX_CORE → D-TRADING" --> D_TRADING

    %% CTR-006: PositionSnapshot (frozen) — D-EX_CORE/D-TRADING → D-RISK/D-ML_TRAIN
    D_EX_CORE -- "🔒 CTR-006<br/>PositionSnapshot<br/>D-EX_CORE → D-RISK" --> D_RISK
    D_TRADING -- "🔒 CTR-006<br/>PositionSnapshot<br/>D-TRADING → D-ML_TRAIN" --> D_ML_TRAIN

    D_TRADING -- "PnL/Risk Metrics" --> D_OPS
    D_ML_TRAIN -- "ModelPrediction" --> D_FACTOR
    D_ML_TRAIN -- "ModelPrediction" --> D_PF_CORE
"""
    (DIAGRAMS_DIR / "integration_topology.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] integration_topology.mmd ({len(content)} chars)")


# ============================================================
# 2. data_flow.mmd — 数据流图
# ============================================================
def write_data_flow():
    content = HEADER + """
%%{init: {'theme': 'default'}}%%
%% Data Flow Diagram — ZephyrAlpha 2.0 Core Pipeline
%% v2.0.0: 14层节点→52域节点，保留P0跨层契约标注

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

    subgraph D_SIGNAL_Grp["D-SIGNAL · 信号 / Signal Generation"]
        D_SIGNAL["D-SIGNAL<br/>Sentiment · Signal Extraction · Predictions<br/>舆情 · 信号提取 · 预测"]
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

    %% D-FACTOR → D-SIGNAL: CTR-002 FactorSignal (frozen)
    D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal<br/>[frozen]"| D_SIGNAL

    %% D-FACTOR → D-RISK: CTR-002 FactorSignal (frozen)
    D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal<br/>[frozen]"| D_RISK

    %% D-FACTOR → D-PF_CORE: CTR-002 FactorSignal (frozen)
    D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal<br/>[frozen]"| D_PF_CORE

    %% D-SIGNAL → D-PF_CORE: 信号输入（非 P0 契约，内部调用）
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
"""
    (DIAGRAMS_DIR / "data_flow.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] data_flow.mmd ({len(content)} chars)")


# ============================================================
# 3. dataflow_terminal.mmd — 终端数据流图（域组件级）
# ============================================================
def write_dataflow_terminal():
    content = HEADER + """
%%{init: {'theme': 'default'}}%%
%% Dataflow Terminal Diagram — ZephyrAlpha 2.0
%% v2.0.0: 14层节点→52域节点，保留P0跨层契约标注和组件级细节

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

    %% ── D-SIGNAL 信号 ─────────────────────────────────────────────
    subgraph D_SIGNAL["D-SIGNAL · 信号 / Signal Generation"]
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
"""
    (DIAGRAMS_DIR / "dataflow_terminal.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] dataflow_terminal.mmd ({len(content)} chars)")


# ============================================================
# 4. runtime_topology.mmd — 运行时拓扑图
# ============================================================
def write_runtime_topology():
    content = HEADER + """
%% Source: technology_architecture.md §3.2
%% v2.0.0: 14层节点→52域节点，保留P0跨层契约标注

graph TD
    subgraph HOST["Host Machine（当前：Windows / 计划：Linux）"]
        subgraph MAIN["ZephyrAlpha Main Process (Python)"]
            direction TB
            D_MKT_DATA["D-MKT_DATA<br/>行情数据"] -->|"🔒 CTR-001<br/>NormalizedMarketData"| D_FACTOR["D-FACTOR<br/>因子"]
            D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal"| D_SIGNAL["D-SIGNAL<br/>信号"]
            D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal"| D_RISK["D-RISK<br/>风控"]
            D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal"| D_PF_CORE["D-PF_CORE<br/>组合"]
            D_RISK -->|"🔒 CTR-003<br/>RiskLimits"| D_PF_CORE
            D_PF_CORE -->|"🔓 CTR-004<br/>Order"| D_EX_CORE["D-EX_CORE<br/>执行"]
            D_EX_CORE -->|"🔒 CTR-005<br/>Fill + 🔒 CTR-006<br/>PositionSnapshot"| D_TRADING["D-TRADING<br/>交易运营"]
            D_TRADING -->|"Report"| D_FRONTEND["D-FRONTEND<br/>前端"]
        end
        subgraph STORAGE["Local Storage"]
            DB["Data Store (Parquet / DuckDB · 待定)"]
            DOCS["docs/ (Git + Markdown)"]
        end
        MAIN -->|"写入"| DB
        MAIN -->|"读写"| DOCS
    end
    subgraph EXT["External Systems"]
        MKT["Market Data (REST/WS)"]
        BRK["Broker API (REST/FIX)"]
        LLM["LLM Providers (REST)"]
        FEISHU["Feishu (Webhook)"]
    end
    MKT -->|"行情"| D_MKT_DATA
    D_EX_CORE -->|"委托"| BRK
    BRK -->|"成交回报"| D_EX_CORE
    D_FRONTEND -->|"AI 推理"| LLM
    D_FRONTEND -->|"通知"| FEISHU

    style MAIN fill:#eff6ff,stroke:#3b82f6
    style HOST fill:#f8fafc,stroke:#94a3b8
    style EXT fill:#fef2f2,stroke:#ef4444
    style STORAGE fill:#fefce8,stroke:#eab308
"""
    (DIAGRAMS_DIR / "runtime_topology.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] runtime_topology.mmd ({len(content)} chars)")


# ============================================================
# 5. capability_heatmap_visual.mmd — 能力热力图可视化
# ============================================================
def write_capability_heatmap_visual(stats):
    """52域×10能力域矩阵（与capability_heatmap.md v2.0.0对齐）"""
    # 10能力域定义
    capability_domains = [
        ("数据接入", ["D-MKT_DATA", "D-ALT_DATA", "D-DATA_ENG"]),
        ("因子研究", ["D-FACTOR", "D-SIGNAL", "D-SIGNAL_FUNDAMENTAL", "D-SIGNAL_ASHARE", "D-SIGNAL_QUALITY"]),
        ("策略决策", ["D-PF_CORE", "D-PF_ALLOC", "D-SELL_DECISION", "D-CROSS_ASSET"]),
        ("执行交易", ["D-EX_CORE", "D-EX_SOR", "D-TRADING", "D-POSITION"]),
        ("风险控制", ["D-RISK", "D-COMPLIANCE"]),
        ("回测仿真", ["D-BACKTEST", "D-SIMULATION", "D-EXEC_SIM", "D-DIGITAL_TWIN"]),
        ("ML平台", ["D-ML_TRAIN", "D-ML_SERVE"]),
        ("治理(横切)", ["D-GOVERNANCE", "D-GOV_RULE", "D-GOV_AUDIT", "D-GOV_DRIFT"]),
        ("安全(横切)", ["D-SECURITY", "D-BEHAVIORAL_AUDIT", "D-DATA_SEC", "D-AUTONOMY_PERM"]),
        ("基础设施(横切)", ["D-INFRA_OPS", "D-INFRA_RUNTIME", "D-INTEGRATION", "D-SHARED", "D-FRONTEND", "D-REPORTING", "D-KNOWLEDGE", "D-INTELLIGENCE", "D-AUTONOMY_CORE", "D-OPS"]),
    ]

    def maturity_label(did):
        s = stats.get(did, {})
        nodes = s.get("nodes", 0)
        prod = s.get("prod", 0)
        if nodes == 0:
            return "L0"
        if prod > 0:
            return "L3+"
        return "L1-L2"

    lines = [HEADER]
    lines.append("%% Source: capability_heatmap.md §3")
    lines.append("%%{init: {'theme': 'default'}}%%")
    lines.append("%% v2.0.0: 14层×7能力域 → 52域×10能力域矩阵")
    lines.append("%% 成熟度数据由depgraph.db派生")
    lines.append("")
    lines.append("graph LR")
    lines.append(f'    subgraph Heatmap["52域×10能力域热力图（{NOW}快照）"]')

    for cap_name, domains in capability_domains:
        cap_safe = cap_name.replace("(", "_").replace(")", "_").replace("（", "_").replace("）", "_")
        lines.append(f'        subgraph {cap_safe}["{cap_name}"]')
        for did in domains:
            safe_id = did.replace("-", "_")
            name = stats.get(did, {}).get("name", did)
            mat = maturity_label(did)
            node_count = stats.get(did, {}).get("nodes", 0)
            lines.append(f'        {safe_id}["{did}<br/>{name}<br/>{mat} ({node_count}节点)"]')
        lines.append("    end")

    lines.append("")
    lines.append("    %% 成熟度图例: L0=缺失 L1=设计 L2=草稿 L3+=可用/生产级")
    lines.append("    %% 完整数据见 generated/design_vs_production.md")

    # 样式
    color_map = {"L0": "#e5e7eb", "L1-L2": "#bfdbfe", "L3+": "#fde68a"}
    for cap_name, domains in capability_domains:
        for did in domains:
            safe_id = did.replace("-", "_")
            mat = maturity_label(did)
            color = color_map.get(mat, "#e5e7eb")
            lines.append(f"    style {safe_id} fill:{color}")

    content = "\n".join(lines) + "\n"
    (DIAGRAMS_DIR / "capability_heatmap_visual.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] capability_heatmap_visual.mmd ({len(content)} chars)")


# ============================================================
# 6. c4_l2_containers.mmd — C4 L2 容器图
# ============================================================
def write_c4_l2_containers():
    content = HEADER + """
%%{init: {'theme': 'default'}}%%
%% C4-L2 Container Diagram — ZephyrAlpha 2.0
%% v2.0.0: 14层容器→52域容器，保留P0跨层契约标注

C4Container
    title Container Diagram — ZephyrAlpha 2.0
    title (with Cross-Domain Contracts / 含跨域数据契约标注)

    Person(operator, "Independent Operator", "独立操作者")

    System_Boundary(zephyr, "ZephyrAlpha 2.0") {
        Container(data_pipeline, "Data Pipeline", "Python / D-MKT_DATA", "Market data ingestion,<br/>standardization, quality gating<br/>行情数据接入、标准化、质量门禁")

        Container(factor_engine, "Factor Engine", "Python / D-FACTOR+D-SIGNAL", "Alpha factor calculation,<br/>signal generation<br/>Alpha 因子计算、信号生成")

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

    %% CTR-002: FactorSignal (frozen) — D-FACTOR → D-SIGNAL/D-RISK/D-PF_CORE
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
"""
    (DIAGRAMS_DIR / "c4_l2_containers.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] c4_l2_containers.mmd ({len(content)} chars)")


# ============================================================
# 7. c4_l3_l00_data_source.mmd — C4 L3 数据源域组件
# ============================================================
def write_c4_l3_data_source():
    content = HEADER + """
%%{init: {'theme': 'default'}}%%
%% v2.0.0: L00 Data Source → D-MKT_DATA 行情数据域组件
%% 文件名保留l00前缀以兼容现有引用

C4Component
    title C4 Level 3 — D-MKT_DATA 行情数据域组件
    title (D-MKT_DATA 数据源域组件分解 / H5)

    Container_Boundary(d_mkt_data, "D-MKT_DATA 行情数据 / Market Data (depgraph.db派生)") {

        Component(vendor_registry, "Vendor Registry", "Python / vendor_registry.py", "Vendor 统一注册中心：按 asset_class/jurisdiction/data_domain 解析可用 Vendor，含优先级排序与健康状态上报<br/>Vendor Registry: register / resolve / healthcheck_all")

        Component(vendor_base, "IDataSource Base", "Python / vendor_base.py", "抽象接口锁定：fetch_bars / fetch_fundamentals / fetch_corp_actions / healthcheck<br/>所有 Vendor facade 必须实现")

        Component(failover_policy, "Failover Policy", "YAML / failover_policy.yaml", "故障转移策略配置：circuit_breaker 参数 / primary+fallbacks 链 / data_quality_degraded 标志")

        Boundary(connectors, "connectors/ ACL 扩展区") {
            Component(ifind_facade, "iFinD Facade", "Python / stock/cn_ifind/facade.py", "Primary vendor (L0 contractual SLA, ¥2000/mo)：实现 IDataSource，内含 retry + breaker + OTel span")

            Component(ifind_mapper, "iFinD Mapper", "Python / stock/cn_ifind/mapper.py", "外部 iFinD DTO → canonical schema 翻译：单位/时区/PIT 三字段补全")

            Component(ifind_raw, "iFinD Raw Client", "Python / stock/cn_ifind/raw_client.py", "原始 SDK 包装：网络重试、反序列化 Vendor 原生 DTO（不可被其他域 import）")

            Component(tushare_facade, "Tushare Pro Facade", "Python / stock/cn_tushare_pro/facade.py", "Fallback priority 1（UAT 激活后就绪）：同三段结构")

            Component(akshare_facade, "AKShare Facade", "Python / stock/cn_akshare/facade.py", "Fallback priority 2（免费备源）：同三段结构")
        }

        Component(loader, "Autoload Bootstrapper", "Python / __init__.py loader", "启动时遍历 connectors/ 子包，触发 VendorRegistry.register 装饰器")

        ComponentDb(cache, "Raw Data Cache", "DuckDB / Parquet", "按 asof_date 分区的 PIT 原始数据快照（可选缓存层）")
    }

    Container_Ext(shared_contracts, "D-SHARED/contracts/", "Python / canonical schema", "Instrument / Bar / Tick / CorporateAction / FundamentalSnapshot")

    Container_Ext(d_factor, "D-FACTOR 因子", "Python / D-FACTOR/", "因子消费侧（通过 IDataSource）")

    System_Ext(vendor_ext, "External Vendors", "iFinD / Tushare / AKShare / Polygon / ...")

    System_Ext(d_ops, "D-OPS 反馈循环", "OTel Collector / Prometheus", "metrics + traces 接收")

    Rel(d_factor, vendor_registry, "resolve(asset_class, jurisdiction, data_domain)", "解析可用 Vendor")
    Rel(vendor_registry, ifind_facade, "returns (primary)")
    Rel(vendor_registry, tushare_facade, "returns (fallback 1)")
    Rel(vendor_registry, akshare_facade, "returns (fallback 2)")
    Rel(vendor_registry, failover_policy, "reads policy")

    Rel(ifind_facade, ifind_mapper, "applies mapper", "canonical 翻译")
    Rel(ifind_mapper, ifind_raw, "calls raw_client", "Vendor 原生 DTO")
    Rel(ifind_mapper, shared_contracts, "outputs canonical", "Bar / Instrument / ...")
    Rel(ifind_raw, vendor_ext, "HTTPS / SDK", "REST / WebSocket")

    Rel(loader, vendor_registry, "bootstraps registration", "autodiscover on import")
    Rel(ifind_facade, failover_policy, "circuit breaker config")
    Rel(ifind_facade, cache, "read/write snapshot", "PIT 缓存")
    Rel(ifind_facade, d_ops, "emits trace + metric", "zephyr_vendor_hit / zephyr_vendor_failure")

    UpdateRelStyle(d_factor, vendor_registry, $offsetX="-40", $offsetY="-10")
"""
    (DIAGRAMS_DIR / "c4_l3_l00_data_source.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] c4_l3_l00_data_source.mmd ({len(content)} chars)")


# ============================================================
# 8. c4_l3_l06_trade_execution.mmd — C4 L3 执行核心域组件
# ============================================================
def write_c4_l3_trade_execution():
    content = HEADER + """
%%{init: {'theme': 'default'}}%%
%% v2.0.0: L06 Trade Execution → D-EX_CORE 执行核心域组件
%% 文件名保留l06前缀以兼容现有引用

C4Component
    title C4 Level 3 — D-EX_CORE 执行核心域组件
    title (D-EX_CORE 执行域组件分解 / H5)

    Container_Boundary(d_ex_core, "D-EX_CORE 执行核心 / Trade Execution (depgraph.db派生)") {

        Component(broker_interface, "IBroker Interface", "Python / broker_interface.py", "🔒 BrokerInterface 抽象契约（锁死）：submit / cancel / query_status / stream_fills / get_positions")

        Component(oms, "OMS — Order Management", "Python / oms.py", "订单生命周期管理：pending → submitted → filled / cancelled；状态机 + audit hook")

        Component(idempotency_guard, "Idempotency Guard", "Python / idempotency.py", "**量化红线**：Idempotency Key 生成 + Redis SETNX 去重 + journal append-only 冷层（详见 §9 H10 / src-domain/idempotency-design.md）")

        Component(sor, "SOR — Smart Order Router", "Python / sor.py", "多 broker 路由决策：按 fee / 流动性 / 接入状态选 broker；接入 §8 failover")

        Component(pre_trade_risk_proxy, "Pre-Trade Risk Proxy", "Python / pre_trade_proxy.py", "风控代理（调用 D-RISK）：单订单阈值 + 组合级校验 ≤1s 延迟（SLO-3）")

        Boundary(adapters, "adapters/ Broker 扩展区") {
            Component(sim_adapter, "Simulation Adapter", "Python / adapters/simulation_adapter.py", "当前阶段默认：本地撮合模拟，实现 IBroker")

            Component(broker_xxx, "Real Broker Adapter", "Python / adapters/broker_{vendor}.py", "Post-Activation 激活：各家券商 SDK 实现 IBroker（Interactive Brokers / 华泰 / 中信 / ...）")
        }

        Component(fill_handler, "Fill Handler", "Python / fill_handler.py", "成交回报消费：写 audit journal（RPO=0）+ 更新 positions + 触发 D-TRADING")

        Component(position_tracker, "Position Tracker", "Python / positions.py", "实时持仓跟踪：内存缓存 + 定期持久化 + T+1 对账")
    }

    Container_Ext(d_pf_core, "D-PF_CORE 组合核心", "Python / D-PF_CORE/", "订单源：optimizer 输出目标仓位")

    Container_Ext(d_risk, "D-RISK 风控", "Python / D-RISK/", "pre-trade 实时风控决策")

    Container_Ext(d_trading, "D-TRADING 交易运营", "Python / D-TRADING/", "成交后归因 + 对账")

    Container_Ext(d_compliance, "D-COMPLIANCE 合规", "Python / D-COMPLIANCE/", "合规检查（辖区规则 / 自成交 / 洗售）")

    ContainerDb_Ext(audit_journal, "Audit Journal (L2 Log)", "JSONL append-only + Loki", "**零丢失约束**：每笔订单/成交/幂等 key 持久化（DR RPO=0）")

    ContainerDb_Ext(redis_idem, "Redis Idempotency Layer", "Redis SETNX + TTL", "Key 热层：交易日级去重窗口")

    System_Ext(broker_ext, "Broker API", "券商 API（实盘激活后）")

    Container_Ext(d_ops, "D-OPS 反馈循环", "OTel / Prometheus", "订单延迟 + 成交吞吐 + 幂等命中率")

    Rel(d_pf_core, oms, "submits target orders", "目标委托")
    Rel(oms, idempotency_guard, "check before send", "Key 生成 + SETNX")
    Rel(idempotency_guard, redis_idem, "SETNX + TTL", "交易日窗口")
    Rel(idempotency_guard, audit_journal, "append Key + decision", "append-only")

    Rel(oms, pre_trade_risk_proxy, "risk check", "<1s SLO-3")
    Rel(pre_trade_risk_proxy, d_risk, "delegates", "风控规则执行")
    Rel(pre_trade_risk_proxy, d_compliance, "delegates", "合规检查")

    Rel(oms, sor, "route decision", "选 broker")
    Rel(sor, sim_adapter, "when simulation", "模拟撮合")
    Rel(sor, broker_xxx, "when live", "Post-Activation")

    Rel(sim_adapter, broker_interface, "implements")
    Rel(broker_xxx, broker_interface, "implements")
    Rel(broker_xxx, broker_ext, "HTTPS / FIX", "submit + stream")

    Rel(broker_ext, fill_handler, "fills / status", "成交回报")
    Rel(sim_adapter, fill_handler, "simulated fills")
    Rel(fill_handler, audit_journal, "append fill", "RPO=0")
    Rel(fill_handler, position_tracker, "update positions")
    Rel(fill_handler, d_trading, "notifies", "归因入口")

    Rel(oms, d_ops, "emits", "zephyr_order_duration / zephyr_order_outcome")
    Rel(idempotency_guard, d_ops, "emits", "zephyr_idempotency_hit")
"""
    (DIAGRAMS_DIR / "c4_l3_l06_trade_execution.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] c4_l3_l06_trade_execution.mmd ({len(content)} chars)")


# ============================================================
# 9. c4_l3_l11_ml_platform.mmd — C4 L3 ML训练域组件
# ============================================================
def write_c4_l3_ml_platform():
    content = HEADER + """
%%{init: {'theme': 'default'}}%%
%% v2.0.0: L11 ML Platform → D-ML_TRAIN 训练域组件
%% 文件名保留l11前缀以兼容现有引用

C4Component
    title C4 Level 3 — D-ML_TRAIN 训练域组件
    title (D-ML_TRAIN ML平台域组件分解 / H5)

    Container_Boundary(d_ml_train, "D-ML_TRAIN 训练 / ML Platform (depgraph.db派生)") {

        Component(feature_store, "Feature Store", "Python / feature_store/", "特征物化层：按 entity_id × asof_date PIT 对齐；写入供训练、读取供 inference")

        Component(pit_query, "PIT Query Engine", "Python / pit_query.py", "反 Survivorship 查询：强制带 asof_date + knowledge_date 双游标（05-DA §5 铁律）")

        Component(training_pipeline, "Training Pipeline", "Python / training/", "模型训练编排：数据集切分 + CV + metric 记录，输出 model artifact")

        Component(model_registry, "Model Registry", "Python / model_registry.py", "模型版本化 + lifecycle：draft/staging/prod/archived；每版绑定训练数据快照 id")

        Component(inference_engine, "Inference Engine", "Python / inference/", "生产推理：load by model_id + version + stage，emit metric 延迟/吞吐")

        Component(drift_monitor, "Drift Monitor", "Python / monitoring/drift.py", "feature drift / label drift / concept drift 三类监控；超阈值触发回滚或重训")

        Component(shadow_mode, "Shadow / Canary Mode", "Python / deployment/shadow.py", "新模型对比生产模型：影子跑不写下游 / 金丝雀 5-10% 流量")

        Boundary(ai_operator_slot, "ai_operator/ 预留口子（OQ-063 C-1）") {
            Component(ai_op_reserved, "AI Operator Slot", "Python / D-ML_TRAIN/_ai_operator/ (reserved)", "AI Operator 激活口子：OQ-063 P4 未来态，当前为空 skeleton")
        }
    }

    Container_Ext(d_factor, "D-FACTOR 因子", "Python / D-FACTOR/", "因子供 feature 来源")

    Container_Ext(d_mkt_data, "D-MKT_DATA 行情数据", "Python / D-MKT_DATA/", "原始数据 via IDataSource")

    Container_Ext(d_signal_pf, "D-SIGNAL/D-PF_CORE 信号&组合", "Python / D-SIGNAL + D-PF_CORE/", "下游推理消费者")

    Container_Ext(d_intelligence, "D-INTELLIGENCE 战略决策", "Python / D-INTELLIGENCE/", "A/B 实验与批跑研究")

    ContainerDb_Ext(artifact_storage, "Model Artifact Storage", "MLflow / 本地 + S3", "模型文件 + training dataset snapshot hash")

    ContainerDb_Ext(feature_storage, "Feature Storage", "Parquet / DuckDB", "按 entity × asof_date 分区")

    Container_Ext(d_ops, "D-OPS 反馈循环", "OTel + Prometheus", "训练/推理 metric + 漂移 metric")

    Rel(d_factor, feature_store, "writes factors as features", "feature ingest")
    Rel(d_mkt_data, feature_store, "writes raw features", "via pit_query")
    Rel(feature_store, feature_storage, "persists", "Parquet partition")
    Rel(feature_store, pit_query, "uses PIT semantics", "asof + knowledge")

    Rel(training_pipeline, feature_store, "reads training data", "PIT window")
    Rel(training_pipeline, model_registry, "registers artifact", "new version draft")
    Rel(model_registry, artifact_storage, "stores artifact", "versioned")

    Rel(inference_engine, model_registry, "loads model", "by stage")
    Rel(inference_engine, feature_store, "reads live features", "for scoring")
    Rel(inference_engine, d_signal_pf, "serves predictions", "signal input")

    Rel(drift_monitor, feature_store, "observes distribution")
    Rel(drift_monitor, inference_engine, "observes predictions")
    Rel(drift_monitor, d_ops, "emits drift metric", "zephyr_model_drift_score")

    Rel(shadow_mode, inference_engine, "duplicates traffic", "5-10% canary")
    Rel(d_intelligence, training_pipeline, "triggers experiments", "A/B job")

    Rel(ai_op_reserved, model_registry, "future: auto-promote/rollback", "OQ-063 P4")
"""
    (DIAGRAMS_DIR / "c4_l3_l11_ml_platform.mmd").write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] c4_l3_l11_ml_platform.mmd ({len(content)} chars)")


# ============================================================
# Main
# ============================================================
def main():
    print(f"DM-200913 Phase4-B: 重写9个图表为52域派生")
    print(f"时间: {NOW}")
    print(f"数据源: {DEPGRAPH_DB}")
    print()

    stats = get_domain_stats()
    print(f"从depgraph.db加载 {len(stats)} 个域统计")
    print()

    write_integration_topology()
    write_data_flow()
    write_dataflow_terminal()
    write_runtime_topology()
    write_capability_heatmap_visual(stats)
    write_c4_l2_containers()
    write_c4_l3_data_source()
    write_c4_l3_trade_execution()
    write_c4_l3_ml_platform()

    print()
    print("完成: 9个图表已重写为52域派生")


if __name__ == "__main__":
    main()
