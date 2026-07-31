# Decision Flow · L3 Functional Domain ex_sor（执行排序）

> 生成时间: 2026-07-30T22:18:45
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → ex_sor

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `ex_sor`（执行排序）

> **域职责 / Responsibility**: 智能订单路由(SOR)——路由决策、通道熔断、Kill-Switch 与熔断器矩阵

## 统计

- 设计态节点数: 5
- 域内边数: 4
- 跨域出边: 2（2 个外部域）
- 跨域入边: 2（1 个外部域）

## 设计态全景图

> 共 6 层，0 边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL2A["L2A: 信号层<br/>design/planned<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 → Tr…"]
    LL2B["L2B: 主力行为层<br/>design/planned<br/>六阶段识别 + 自迭代推演 + 庄家专项 + 群体博弈模拟…"]
    LL2C["L2C: 市场状态与大盘预测层<br/>design/planned<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 + T+1次日…"]
    LL2D["L2D: 知识图谱与因果推演层<br/>design/planned<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 → G…"]
    LL5["L5: 学习层<br/>design/planned<br/>7阶段学习流水线 → 模块工厂 → 知识采集 → 反馈闭环…"]
    LL6["L6: 自评估层<br/>design/planned<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理…"]
    LL2A -.->|triggering / 触发| LL2B
    LL2B -.->|triggering / 触发| LL2C
    LL2C -.->|triggering / 触发| LL2D
    LL2D -.->|triggering / 触发| LL5
    LL5 -.->|triggering / 触发| LL6
```

## Node 清单

| node_id / 节点ID | layer / 层 | type / 类型 | name / 名称 | path / 路径 | module_id / 模块 | 代码引用 / ref | maturity / 成熟度 | build_status / 构建状态 |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 72 | L3 | order / 订单节点 | 订单路由决策 Order Routing Decision | decision/ex_sor/ex_16 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 73 | L3 | order / 订单节点 | SOR路由决策延迟 SOR Routing Latency | decision/ex_sor/ex_17 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 75 | L3 | order / 订单节点 | 交易通道熔断人工恢复 Trading Channel Manual Recovery | decision/ex_sor/ex_19 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 77 | L3 | order / 订单节点 | Kill-Switch四级阶梯 Kill-Switch 4-Level Cascade | decision/ex_sor/ex_21 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 78 | L3 | order / 订单节点 | 熔断器矩阵 Circuit Breaker Matrix | decision/ex_sor/ex_22 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 85 | 72 | 73 | informing / 告知 | L3层内顺序流 | - |
| 86 | 73 | 75 | informing / 告知 | L3层内顺序流 | - |
| 87 | 75 | 77 | informing / 告知 | L3层内顺序流 | - |
| 88 | 77 | 78 | informing / 告知 | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/ex_sor/ex_22 | → | decision/pf_alloc/pa_01 | informing / 告知 |
| 2 | decision/ex_sor/ex_23 | → | decision/governance/gov_001 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/ex_core/ex_15 | → | decision/ex_sor/ex_16 | informing / 告知 |
| 2 | decision/ex_core/ex_14 | → | decision/ex_sor/ex_18 | informing / 告知 |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 3 个外部域直接连接 / This domain directly connects to 3 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["ex_sor（执行排序）"]
    EXT_pf_alloc["pf_alloc（组合分配）"]
    SELF -->|出 1| EXT_pf_alloc
    EXT_governance["governance（governance）"]
    SELF -->|出 1| EXT_governance
    EXT_ex_core["ex_core（执行核心）"]
    EXT_ex_core -->|入 2| SELF
```

