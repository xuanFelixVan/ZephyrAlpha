# 决策流图 · 应急保命轨（Emergency Track）

> 生成时间: 2026-07-19T06:21:57
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | Track 4

**track_id**: `emergency` | **优先级**: 4 | **激活条件**: 所有模型/策略/信号失效时

全系统降级到最简规则：L2失效→硬编码均线 / L3失效→固定比例仓位 / L4失效→硬编码10%上限 / 数据断流→仅执行卖出


## 统计

| 视图 | Layer 数 | Edge 数 |
|------|----------|---------|
| 合并 | 0 | 0 |
| 设计态 | 0 | 0 |
| 运营态 | 0 | 0 |

## 合并全景图（设计态 + 运营态，标签标注 [design]/[production]）

```mermaid
flowchart TD

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

## 设计态全景图（仅 design_maturity=design）

> （本轨无设计态节点）

## 运营态全景图（仅 design_maturity=production）

> （本轨无运营态节点）

## Layer 清单

| layer_id | 名称 | 英文名 | 所属轨 | 蓝图(module_id) | 蓝图名(派生) | 代码引用 | 功能简述 | 决策频率 | 成熟度 | build_status |
|----------|------|--------|--------|-----------------|--------------|----------|----------|----------|--------|--------------|

## Node 清单

> （无节点）

## Edge 清单（本轨内）

> （无决策因果边）

## 跨轨边

> （无跨轨边）

