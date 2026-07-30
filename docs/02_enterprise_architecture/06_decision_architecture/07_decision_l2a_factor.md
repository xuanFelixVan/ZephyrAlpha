# Decision Flow · L2A Functional Domain factor（因子）

> 生成时间: 2026-07-30T19:38:34
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → factor

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `factor`（因子）

## 统计

- 设计态节点数: 2
- 域内边数: 1
- 跨域出边: 1（1 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 7 层，1 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'fontSize': '14px'}}}%%
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["L2A: 信号层<br/>design/planned"]
        N190("signal: 末位淘汰 IC-Based Factor Replacement")
        LL2A --- N190
        N191("signal: 批量裁剪 Batch Factor Pruning")
        LL2A --- N191
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
    N190 -->|informing| N191
```

## Node 清单

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 190 | L2A | signal | 末位淘汰 IC-Based Factor Replacement | decision/factor/fc_01 | - | - | design | planned |
| 191 | L2A | signal | 批量裁剪 Batch Factor Pruning | decision/factor/fc_02 | - | - | design | planned |

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 4 | 190 | 191 | informing | L2A层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 | → | 外部域-目标节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/factor/fc_02 | → | decision/frontend/fe_09 | informing |

## 跨域入边（Depended By）

| # | 外部域-源节点 | → | 本域节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/data/dt_03 | → | decision/factor/fc_01 | informing |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 2 个外部域直接连接 / This domain directly connects to 2 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'fontSize': '14px'}}}%%
flowchart LR
    subgraph cd_sg["跨域依赖（Cross-Domain Dependency）"]
        SELF["factor（因子）"]
        EXT_frontend["frontend（前端）"]
        SELF -->|出 1| EXT_frontend
        EXT_data["data（数据）"]
        EXT_data -->|入 1| SELF
    end
```

