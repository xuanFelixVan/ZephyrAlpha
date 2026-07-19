# 决策流图 · L2A 功能域 research

> 生成时间: 2026-07-19T16:24:12
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → research

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `research`

## 统计

- 设计态节点数: 7
- 域内边数: 6
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 7 层，6 边。

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["[design]L2A: 信号层<br/>功能: 信号工厂 → 多策略投票 → 收益率条…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        N204("[design]signal: 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN<br/>path: decision/research/rs_01"):::bsPlanned
        LL2A --- N204
        N205("[design]signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate<br/>path: decision/research/rs_02"):::bsPlanned
        LL2A --- N205
        N206("[design]signal: Decision Audit Trail R-102 Decision Audit Trail<br/>path: decision/research/rs_03"):::bsPlanned
        LL2A --- N206
        N211("[design]signal: 策略可解释性报告器 Strategy Explainability Reporter<br/>path: decision/research/rs_04"):::bsPlanned
        LL2A --- N211
        N212("[design]signal: A股绩效审计与优化触发器 A-Share Performance Audit<br/>path: decision/research/rs_05"):::bsPlanned
        LL2A --- N212
        N213("[design]signal: 异常决策自检 Anomaly Decision Self-Check<br/>path: decision/research/rs_06"):::bsPlanned
        LL2A --- N213
        N214("[design]signal: Knowledge Feedback Loop 知识反馈循环<br/>path: decision/research/rs_07"):::bsPlanned
        LL2A --- N214
        LL2B["[design]L2B: 主力行为层<br/>功能: 六阶段识别 + 自迭代推演 + 庄家专…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2C["[design]L2C: 市场状态与大盘预测层<br/>功能: 3×3矩阵 + 2叠加态 + 三层大盘…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2D["[design]L2D: 知识图谱与因果推演层<br/>功能: 六类知识图谱 → 事件影响链分析 → …<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL3["[design]L3: 策略组合层<br/>功能: 多策略信号合成 → 资本分配 → 元策…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL5["[design]L5: 学习层<br/>功能: 7阶段学习流水线 → 模块工厂 → 知…<br/>freq: weekly<br/>build: planned"]:::bsPlanned
        LL6["[design]L6: 自评估层<br/>功能: LLM 自评估(Judge+交叉验证)…<br/>freq: weekly<br/>build: planned"]:::bsPlanned
    end
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL5
    LL5 -.->|triggering| LL6
    N204 -->|informing| N205
    N205 -->|informing| N206
    N206 -->|informing| N211
    N211 -->|informing| N212
    N212 -->|informing| N213
    N213 -->|informing| N214

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

## Node 清单

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 204 | L2A | signal | 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN | decision/research/rs_01 | - | - | design | planned |
| 205 | L2A | signal | 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate | decision/research/rs_02 | - | - | design | planned |
| 206 | L2A | signal | Decision Audit Trail R-102 Decision Audit Trail | decision/research/rs_03 | - | - | design | planned |
| 211 | L2A | signal | 策略可解释性报告器 Strategy Explainability Reporter | decision/research/rs_04 | - | - | design | planned |
| 212 | L2A | signal | A股绩效审计与优化触发器 A-Share Performance Audit | decision/research/rs_05 | - | - | design | planned |
| 213 | L2A | signal | 异常决策自检 Anomaly Decision Self-Check | decision/research/rs_06 | - | - | design | planned |
| 214 | L2A | signal | Knowledge Feedback Loop 知识反馈循环 | decision/research/rs_07 | - | - | design | planned |

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 12 | 204 | 205 | informing | L2A层内顺序流 | - |
| 13 | 205 | 206 | informing | L2A层内顺序流 | - |
| 14 | 206 | 211 | informing | L2A层内顺序流 | - |
| 15 | 211 | 212 | informing | L2A层内顺序流 | - |
| 16 | 212 | 213 | informing | L2A层内顺序流 | - |
| 17 | 213 | 214 | informing | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 | → | 外部域-目标节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/research/rs_07 | → | decision/sell/sell_00 | informing |

## 跨域入边（Depended By）

| # | 外部域-源节点 | → | 本域节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/frontend/fe_m76 | → | decision/research/rs_01 | informing |

## 跨域依赖图

> 本域与 2 个外部域直接连接。

```mermaid
flowchart LR
    SELF["research"]:::selfDomain
    EXT_sell["sell"]:::extDomain
    SELF -->|出 1| EXT_sell
    EXT_frontend["frontend"]:::extDomain
    EXT_frontend -->|入 1| SELF

    classDef selfDomain fill:#fff9c4,stroke:#f9a825,stroke-width:3px,color:#000
    classDef extDomain fill:#e3f2fd,stroke:#1565c0,stroke-width:1px,color:#000
```

