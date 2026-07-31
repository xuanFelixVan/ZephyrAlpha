# Decision Flow · L3 Functional Domain aut_core（自主核心）

> 生成时间: 2026-07-30T22:18:45
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 模型驱动轨 → L3 → aut_core

**所属轨**: 模型驱动轨（`model_driven`） | **所属层**: L3 | **功能域**: `aut_core`（自主核心）

> **域职责 / Responsibility**: 自主决策编排——权限守卫、自愈回滚、预算执行、健康监控、漂移检测、自动修复与 Agent 编排

## 统计

- 设计态节点数: 11
- 域内边数: 10
- 跨域出边: 2（2 个外部域）
- 跨域入边: 2（2 个外部域）

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
| 113 | L3 | portfolio_target / 组合目标节点 | Permission Guard 七层纵深防御 | decision/aut_core/ac_01 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 115 | L3 | portfolio_target / 组合目标节点 | Self-Healing Git-native自愈 | decision/aut_core/ac_03 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 116 | L3 | portfolio_target / 组合目标节点 | Budget Enforcer 七级预算 | decision/aut_core/ac_04 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 117 | L3 | portfolio_target / 组合目标节点 | Health Monitor 9子系统监控 | decision/aut_core/ac_05 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 118 | L3 | portfolio_target / 组合目标节点 | Escalation Engine 升级引擎 | decision/aut_core/ac_06 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 119 | L3 | portfolio_target / 组合目标节点 | Rollback Engine Git-native回滚 | decision/aut_core/ac_07 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 120 | L3 | portfolio_target / 组合目标节点 | Drift Detector 39检测器 | decision/aut_core/ac_08 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 121 | L3 | portfolio_target / 组合目标节点 | Auto-Fix Engine 16修复器 | decision/aut_core/ac_09 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 133 | L3 | portfolio_target / 组合目标节点 | 编排Agent Orchestrator | decision/aut_core/ac_21 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 135 | L3 | portfolio_target / 组合目标节点 | 做TAgent T0Trader | decision/aut_core/ac_23 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |
| 136 | L3 | portfolio_target / 组合目标节点 | 路由Agent Router | decision/aut_core/ac_24 | MOD-L05-001 | - | design / 设计 | planned / 已规划 |

## Edge 清单（域内）

| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |
|---------|-------|-----|------|-----------|-------|
| 65 | 113 | 115 | informing / 告知 | L3层内顺序流 | - |
| 66 | 115 | 116 | informing / 告知 | L3层内顺序流 | - |
| 67 | 116 | 117 | informing / 告知 | L3层内顺序流 | - |
| 68 | 117 | 118 | informing / 告知 | L3层内顺序流 | - |
| 69 | 118 | 119 | informing / 告知 | L3层内顺序流 | - |
| 70 | 119 | 120 | informing / 告知 | L3层内顺序流 | - |
| 71 | 120 | 121 | informing / 告知 | L3层内顺序流 | - |
| 72 | 121 | 133 | informing / 告知 | L3层内顺序流 | - |
| 73 | 133 | 135 | informing / 告知 | L3层内顺序流 | - |
| 74 | 135 | 136 | informing / 告知 | L3层内顺序流 | - |

## 跨域出边（Depends On）

| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/aut_core/ac_24 | → | decision/ex_core/ex_03 | informing / 告知 |
| 2 | decision/aut_core/ac_22 | → | decision/aut_perm/ap_11 | informing / 告知 |

## 跨域入边（Depended By）

| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |
|:--:|---------|:--:|---------|---------|
| 1 | decision/simulation/sim_g1 | → | decision/aut_core/ac_01 | informing / 告知 |
| 2 | decision/trading/trd_11 | → | decision/aut_core/ac_02 | informing / 告知 |

## 跨域依赖图（Cross-Domain Dependency Graph）

> 本域与 4 个外部域直接连接 / This domain directly connects to 4 external domain(s).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart LR
    SELF["aut_core（自主核心）"]
    EXT_ex_core["ex_core（执行核心）"]
    SELF -->|出 1| EXT_ex_core
    EXT_aut_perm["aut_perm（aut_perm）"]
    SELF -->|出 1| EXT_aut_perm
    EXT_simulation["simulation（仿真）"]
    EXT_simulation -->|入 1| SELF
    EXT_trading["trading（交易）"]
    EXT_trading -->|入 1| SELF
```

