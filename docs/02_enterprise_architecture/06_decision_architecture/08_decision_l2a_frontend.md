# Decision Flow · L2A Functional Domain frontend（前端）

> 生成时间: 2026-07-30T17:45:57
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
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'clusterBkg': '#eaeaea', 'clusterBorder': '#666666', 'fontSize': '14px'}}}%%
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["L2A: 信号层<br/>design/planned"]
        N200("signal: Approval Workflow UI 审批流程界面")
        LL2A --- N200
        N201("signal: Notification Router 通知路由")
        LL2A --- N201
        N202("signal: Real-time Dashboard 实时仪表盘")
        LL2A --- N202
        N203("signal: 决策树可视化器 ADR Decision Tree Visualizer")
        LL2A --- N203
        N209("signal: 服务降级管理 Service Degradation Manager")
        LL2A --- N209
        N210("signal: 跨域运维事件链追踪 Cross-Domain Event Chain")
        LL2A --- N210
        LL2B["L2B: 主力行为层<br/>design/planned"]
        LL2C["L2C: 市场状态与大盘预测层<br/>design/planned"]
        LL2D["L2D: 知识图谱与因果推演层<br/>design/planned"]
        LL3["L3: 策略组合层<br/>design/planned"]
        LL5["L5: 学习层<br/>design/planned"]
        LL6["L6: 自评估层<br/>design/planned"]
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
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'clusterBkg': '#eaeaea', 'clusterBorder': '#666666', 'fontSize': '14px'}}}%%
flowchart LR
    subgraph cd_sg["跨域依赖（Cross-Domain Dependency）"]
        SELF["frontend（前端）"]
        EXT_research["research（研究）"]
        SELF -->|出 1| EXT_research
        EXT_factor["factor（因子）"]
        EXT_factor -->|入 1| SELF
    end
```

