# 决策流图 · 层级详情图

> 生成时间: 2026-07-30T17:45:57
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 辅助图

L0-L6 层级卡片 + 频率/成熟度/状态 + 流向箭头 + 学习闭环反馈边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'clusterBkg': '#eaeaea', 'clusterBorder': '#666666', 'fontSize': '14px'}}}%%
flowchart LR
    subgraph layers_sg["决策层级（Decision Layers）"]
        LL0["L0 数据接入与预处理层<br/>production/stable"]
        LL1["L1 因子计算层<br/>production/stable"]
        LL2A["L2A 信号层<br/>design/planned"]
        LL2B["L2B 主力行为层<br/>design/planned"]
        LL2C["L2C 市场状态与大盘预测层<br/>design/planned"]
        LL2D["L2D 知识图谱与因果推演层<br/>design/planned"]
        LL3["L3 策略组合层<br/>design/planned"]
        LL4["L4 风控层<br/>production/stable"]
        LL5["L5 学习层<br/>design/planned"]
        LL6["L6 自评估层<br/>design/planned"]
    end
    LL0 -->|triggering| LL1
    LL1 -->|triggering| LL2A
    LL2A -->|triggering| LL2B
    LL2B -->|triggering| LL2C
    LL2C -->|triggering| LL2D
    LL2D -->|triggering| LL3
    LL3 -->|triggering| LL4
    LL4 -->|triggering| LL5
    LL5 -->|triggering| LL6
    LL6 -.->|feedback| LL1
    LL6 -.->|feedback| LL5
```

