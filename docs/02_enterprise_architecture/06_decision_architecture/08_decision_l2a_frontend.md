# Decision Flow · L2A Functional Domain frontend（前端）

> 生成时间: 2026-07-20T01:15:30
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → frontend

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `frontend`（前端）

## 统计

- 设计态节点数: 6
- 域内边数: 5
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 7 层，5 边。

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["[design]L2A: 信号层<br/>功能: 信号工厂 → 多策略投票 → 收益率条…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        N200("[design]signal: Approval Workflow UI 审批流程界面<br/>path: decision/frontend/fe_12"):::bsPlanned
        LL2A --- N200
        N201("[design]signal: Notification Router 通知路由<br/>path: decision/frontend/fe_13"):::bsPlanned
        LL2A --- N201
        N202("[design]signal: Real-time Dashboard 实时仪表盘<br/>path: decision/frontend/fe_09"):::bsPlanned
        LL2A --- N202
        N203("[design]signal: 决策树可视化器 ADR Decision Tree Visualizer<br/>path: decision/frontend/fe_m76"):::bsPlanned
        LL2A --- N203
        N209("[design]signal: 服务降级管理 Service Degradation Manager<br/>path: decision/frontend/fe_14"):::bsPlanned
        LL2A --- N209
        N210("[design]signal: 跨域运维事件链追踪 Cross-Domain Event Chain<br/>path: decision/frontend/fe_15"):::bsPlanned
        LL2A --- N210
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
    N202 -->|informing| N200
    N200 -->|informing| N201
    N201 -->|informing| N209
    N209 -->|informing| N210
    N210 -->|informing| N203

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

## Node 清单

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 200 | L2A | signal | Approval Workflow UI 审批流程界面 | decision/frontend/fe_12 | - | - | design | planned |
| 201 | L2A | signal | Notification Router 通知路由 | decision/frontend/fe_13 | - | - | design | planned |
| 202 | L2A | signal | Real-time Dashboard 实时仪表盘 | decision/frontend/fe_09 | - | - | design | planned |
| 203 | L2A | signal | 决策树可视化器 ADR Decision Tree Visualizer | decision/frontend/fe_m76 | - | - | design | planned |
| 209 | L2A | signal | 服务降级管理 Service Degradation Manager | decision/frontend/fe_14 | - | - | design | planned |
| 210 | L2A | signal | 跨域运维事件链追踪 Cross-Domain Event Chain | decision/frontend/fe_15 | - | - | design | planned |

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 6 | 202 | 200 | informing | L2A层内顺序流 | - |
| 7 | 200 | 201 | informing | L2A层内顺序流 | - |
| 8 | 201 | 209 | informing | L2A层内顺序流 | - |
| 9 | 209 | 210 | informing | L2A层内顺序流 | - |
| 10 | 210 | 203 | informing | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 | → | 外部域-目标节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/frontend/fe_m76 | → | decision/research/rs_01 | informing |

## 跨域入边（Depended By）

| # | 外部域-源节点 | → | 本域节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/factor/fc_02 | → | decision/frontend/fe_09 | informing |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 2 个外部域直接连接 / This domain directly connects to 2 external domain(s).

```mermaid
flowchart LR
    SELF["frontend（前端）"]:::selfDomain
    EXT_research["research（研究）"]:::extDomain
    SELF -->|出 1| EXT_research
    EXT_factor["factor（因子）"]:::extDomain
    EXT_factor -->|入 1| SELF

    classDef selfDomain fill:#fff9c4,stroke:#f9a825,stroke-width:3px,color:#000
    classDef extDomain fill:#e3f2fd,stroke:#1565c0,stroke-width:1px,color:#000
```

