# Decision Flow · L2A Functional Domain research（研究）

> 生成时间: 2026-07-30T19:59:19
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L2A → research

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L2A | **功能域**: `research`（研究）

## 统计

- 设计态节点数: 6
- 域内边数: 5
- 跨域出边: 0（0 个外部域）
- 跨域入边: 1（1 个外部域）

## 设计态全景图

> 共 7 层，5 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["L2A: 信号层<br/>design/planned"]
    N204("signal: 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN")
    LL2A --- N204
    N205("signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate")
    LL2A --- N205
    N206("signal: Decision Audit Trail R-102 Decision Audit Trail")
    LL2A --- N206
    N211("signal: 策略可解释性报告器 Strategy Explainability Reporter")
    LL2A --- N211
    N212("signal: A股绩效审计与优化触发器 A-Share Performance Audit")
    LL2A --- N212
    N213("signal: 异常决策自检 Anomaly Decision Self-Check")
    LL2A --- N213
    LL2B["L2B: 主力行为层<br/>design/planned"]
    LL2C["L2C: 市场状态与大盘预测层<br/>design/planned"]
    LL2D["L2D: 知识图谱与因果推演层<br/>design/planned"]
    LL3["L3: 策略组合层<br/>design/planned"]
    LL5["L5: 学习层<br/>design/planned"]
    LL6["L6: 自评估层<br/>design/planned"]
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

## Edge 清单（域内）

| edge_id | from | to | type | condition | track |
|---------|-------|-----|------|-----------|-------|
| 12 | 204 | 205 | informing | L2A层内顺序流 | - |
| 13 | 205 | 206 | informing | L2A层内顺序流 | - |
| 14 | 206 | 211 | informing | L2A层内顺序流 | - |
| 15 | 211 | 212 | informing | L2A层内顺序流 | - |
| 16 | 212 | 213 | informing | L2A层内顺序流 | - |

## 跨域出边（Depends On）

> （无跨域出边）

## 跨域入边（Depended By）

| # | 外部域-源节点 | → | 本域节点 | type |
|:--:|---------|:--:|---------|---------|
| 1 | decision/frontend/fe_m76 | → | decision/research/rs_01 | informing |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 1 个外部域直接连接 / This domain directly connects to 1 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["research（研究）"]
    EXT_frontend["frontend（前端）"]
    EXT_frontend -->|入 1| SELF
```

