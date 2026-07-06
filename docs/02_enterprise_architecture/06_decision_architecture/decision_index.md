# 决策流图（decisiongraph）索引

> 生成时间: 2026-07-06T13:22:03
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)

## 概述

决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖，静态）
- dataflowgraph 表达"数据从哪流到哪"（数据流向，动态）
- decisiongraph 表达"决策如何产生"（决策流，动态）
- 三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）

## 统计

| 类型 | 数量 |
|------|------|
| Track（轨） | 4 |
| Layer（层） | 10 |
| Node（节点） | 0 |
| Edge（边） | 0 |
| 运营态 Layer（design_maturity=production） | 3 |
| 设计态 Layer（design_maturity=design） | 7 |
| 原型态 Layer（design_maturity=prototype） | 0 |
| 运营态 Node（design_maturity=production） | 0 |
| 设计态 Node（design_maturity=design） | 0 |

> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行，`prototype`=原型验证中。对标 depgraph 的设计态/运营态机制。

## Mermaid 图表

> 以下图表通过 Mermaid 代码块内嵌，可直接在 Markdown 查看器中渲染。

### 全景图（设计态 + 运营态合并，标签标注 [design]/[production]）

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL0["[production]L0: 数据接入与预处理层<br/>freq: tick<br/>build: stable"]:::bsStable
        LL1["[production]L1: 因子计算层<br/>freq: daily<br/>build: stable"]:::bsStable
        LL2A["[design]L2A: 信号层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2B["[design]L2B: 主力行为层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2C["[design]L2C: 市场状态与大盘预测层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2D["[design]L2D: 知识图谱与因果推演层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL3["[design]L3: 策略组合层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL4["[production]L4: 风控层<br/>freq: realtime<br/>build: stable"]:::bsStable
        LL5["[design]L5: 学习层<br/>freq: weekly<br/>build: planned"]:::bsPlanned
        LL6["[design]L6: 自评估层<br/>freq: weekly<br/>build: planned"]:::bsPlanned
    end
    subgraph track_data_driven["数据驱动轨（Data-Driven Track）"]
    end
    subgraph track_human_override["人工指令轨（Human Override Track）"]
    end
    subgraph track_emergency["应急保命轨（Emergency Track）"]
    end
    LL0 -.->|triggering| LL1
    LL1 -.->|triggering| LL2A
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL4
    LL4 -.->|triggering| LL5
    LL5 -.->|triggering| LL6

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 运营态全景图（仅 design_maturity=production 的 layer/node）

> 仅展示已实现稳定运行的决策层/节点（共 3 层，0 边）。

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL0["[production]L0: 数据接入与预处理层<br/>freq: tick<br/>build: stable"]:::bsStable
        LL1["[production]L1: 因子计算层<br/>freq: daily<br/>build: stable"]:::bsStable
        LL4["[production]L4: 风控层<br/>freq: realtime<br/>build: stable"]:::bsStable
    end
    subgraph track_data_driven["数据驱动轨（Data-Driven Track）"]
    end
    subgraph track_human_override["人工指令轨（Human Override Track）"]
    end
    subgraph track_emergency["应急保命轨（Emergency Track）"]
    end
    LL0 -.->|triggering| LL1
    LL1 -.->|triggering| LL4

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 设计态全景图（仅 design_maturity=design 的 layer/node）

> 仅展示蓝图规划中尚未实现的决策层/节点（共 7 层，0 边）。

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["[design]L2A: 信号层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2B["[design]L2B: 主力行为层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2C["[design]L2C: 市场状态与大盘预测层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2D["[design]L2D: 知识图谱与因果推演层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL3["[design]L3: 策略组合层<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL5["[design]L5: 学习层<br/>freq: weekly<br/>build: planned"]:::bsPlanned
        LL6["[design]L6: 自评估层<br/>freq: weekly<br/>build: planned"]:::bsPlanned
    end
    subgraph track_data_driven["数据驱动轨（Data-Driven Track）"]
    end
    subgraph track_human_override["人工指令轨（Human Override Track）"]
    end
    subgraph track_emergency["应急保命轨（Emergency Track）"]
    end
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL5
    LL5 -.->|triggering| LL6

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 层级详情图（10 层卡片 + 频率/状态，标签标注 [design]/[production]）

```mermaid
flowchart LR
    LL0["[production] L0 数据接入与预处理层<br/>Data Ingestion & Preprocessing<br/>频率: tick<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL1["[production] L1 因子计算层<br/>Factor Calculation<br/>频率: daily<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL2A["[design] L2A 信号层<br/>Signal Generation<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2B["[design] L2B 主力行为层<br/>Main Force Behavior Analysis<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2C["[design] L2C 市场状态与大盘预测层<br/>Market State & Index Prediction<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2D["[design] L2D 知识图谱与因果推演层<br/>Knowledge Graph & Causal Inference<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL3["[design] L3 策略组合层<br/>Strategy & Portfolio Combination<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL4["[production] L4 风控层<br/>Risk Control<br/>频率: realtime<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL5["[design] L5 学习层<br/>Learning & Optimization<br/>频率: weekly<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL6["[design] L6 自评估层<br/>Self Evaluation<br/>频率: weekly<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL0 -->|triggering| LL1
    LL1 -->|triggering| LL2A
    LL2A -->|triggering| LL2B
    LL2B -->|triggering| LL2C
    LL2C -->|triggering| LL2D
    LL2D -->|triggering| LL3
    LL3 -->|triggering| LL4
    LL4 -->|triggering| LL5
    LL5 -->|triggering| LL6
    L6 -.->|feedback| L1
    L6 -.->|feedback| L5

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 不变量图（6 节点类型 + 5 承重墙不变量）

```mermaid
flowchart TD
    NT_signal["信号节点<br/>Signal"]:::nodeType
    NT_portfolio_target["仓位目标节点<br/>Portfolio Target"]:::nodeType
    NT_risk_check["风控节点<br/>Risk Check"]:::nodeType
    NT_order["订单节点<br/>Order"]:::nodeType
    NT_execution["执行节点<br/>Execution"]:::nodeType
    NT_feedback["反馈节点<br/>Feedback"]:::nodeType
    NT_signal -->|portfolio_target| NT_portfolio_target
    NT_portfolio_target -->|risk_check| NT_risk_check
    NT_risk_check -->|approving| NT_order
    NT_order -->|triggering| NT_execution
    NT_execution -.->|feedback| NT_feedback
    NT_feedback -.->|informing| NT_signal
    NT_signal -.->|禁止| NT_order
    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5
    INV_DEC_INV_001(["DEC-INV-001<br/>风控一票否决<br/>Risk Veto Mandatory"]):::invariant
    INV_DEC_INV_002(["DEC-INV-002<br/>信号仓位分离<br/>Signal-Order Separation"]):::invariant
    INV_DEC_INV_003(["DEC-INV-003<br/>DAG 无环<br/>DAG No-Cycle"]):::invariant
    INV_DEC_INV_004(["DEC-INV-004<br/>时间单调性<br/>Time Monotonicity"]):::invariant
    INV_DEC_INV_005(["DEC-INV-005<br/>证据哈希必填<br/>Evidence Hash Required"]):::invariant
    INV_DEC_INV_001 -.- NT_order
    INV_DEC_INV_002 -.- NT_signal
    INV_DEC_INV_003 -.- NT_feedback
    INV_DEC_INV_005 -.- NT_signal

    classDef nodeType fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef invariant fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#000
```

## Track 清单（四轨）

| track_id | 名称 | 英文名 | 优先级 | 激活条件 |
|----------|------|--------|--------|----------|
| model_driven | 模型驱动轨 | Model-Driven Track | 1 | 正常运行时 |
| data_driven | 数据驱动轨 | Data-Driven Track | 2 | 模型驱动轨信号不足时补充 |
| human_override | 人工指令轨 | Human Override Track | 3 | 人工干预时 |
| emergency | 应急保命轨 | Emergency Track | 4 | 所有模型/策略/信号失效时 |

## Layer 清单（L0-L6）

| layer_id | 名称 | 英文名 | 所属轨 | 决策频率 | 成熟度 | build_status |
|----------|------|--------|--------|----------|--------|--------------|
| L0 | 数据接入与预处理层 | Data Ingestion & Preprocessing | model_driven | tick | production | stable |
| L1 | 因子计算层 | Factor Calculation | model_driven | daily | production | stable |
| L2A | 信号层 | Signal Generation | model_driven | daily | design | planned |
| L2B | 主力行为层 | Main Force Behavior Analysis | model_driven | daily | design | planned |
| L2C | 市场状态与大盘预测层 | Market State & Index Prediction | model_driven | daily | design | planned |
| L2D | 知识图谱与因果推演层 | Knowledge Graph & Causal Inference | model_driven | daily | design | planned |
| L3 | 策略组合层 | Strategy & Portfolio Combination | model_driven | daily | design | planned |
| L4 | 风控层 | Risk Control | model_driven | realtime | production | stable |
| L5 | 学习层 | Learning & Optimization | model_driven | weekly | design | planned |
| L6 | 自评估层 | Self Evaluation | model_driven | weekly | design | planned |
