# Decision Flow · L2A Functional Domain data（数据）

> 生成时间: 2026-07-30T19:38:34
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → data

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `data`（数据）

## 统计

- 设计态节点数: 3
- 域内边数: 2
- 跨域出边: 1（1 个外部域）
- 跨域入边: 0（0 个外部域）

## 设计态全景图

> 共 7 层，2 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'fontSize': '14px'}}}%%
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["L2A: 信号层<br/>design/planned"]
        N192("signal: Multi-Source Priority Router 多源优先级路由")
        LL2A --- N192
        N193("signal: Cross-Source Reconciler 多源对账")
        LL2A --- N193
        N194("signal: Multi-Timeframe Fusion 跨频率融合")
        LL2A --- N194
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
    N192 -->|informing| N193
    N193 -->|informing| N194
```

## Node 清单

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 192 | L2A | signal | Multi-Source Priority Router 多源优先级路由 | decision/data/dt_01 | - | - | design | planned |
| 193 | L2A | signal | Cross-Source Reconciler 多源对账 | decision/data/dt_02 | - | - | design | planned |
| 194 | L2A | signal | Multi-Timeframe Fusion 跨频率融合 | decision/data/dt_03 | - | - | design | planned |

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 1 | 192 | 193 | informing | L2A层内顺序流 | - |
| 2 | 193 | 194 | informing | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 | → | 外部域-目标节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/data/dt_03 | → | decision/factor/fc_01 | informing |

## 跨域入边（Depended By）

> （无跨域入边）

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 1 个外部域直接连接 / This domain directly connects to 1 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'fontSize': '14px'}}}%%
flowchart LR
    subgraph cd_sg["跨域依赖（Cross-Domain Dependency）"]
        SELF["data（数据）"]
        EXT_factor["factor（因子）"]
        SELF -->|出 1| EXT_factor
    end
```

