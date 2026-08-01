---
doc_type: architecture_view
title: 决策流图 不变量图
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 决策流图 · 不变量图

> 生成时间: 2026-08-01T22:22:08
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 辅助图

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/06_decision_architecture/_zoomable_html/21_decision_invariants.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

6 节点类型 + 5 承重墙不变量 + 合法/非法连接标注。

> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 `-->` = 运营态依赖**（两端都 production）
> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    NT_signal["(设计态 / design) 信号节点 / Signal"]
    NT_portfolio_target["(设计态 / design) 仓位目标节点 / Portfolio<br/>Target"]
    NT_risk_check["(设计态 / design) 风控节点 / Risk Check"]
    NT_order["(设计态 / design) 订单节点 / Order"]
    NT_execution["(设计态 / design) 执行节点 / Execution"]
    NT_feedback["(设计态 / design) 反馈节点 / Feedback"]
    NT_signal -->|portfolio_target / 仓位目标| NT_portfolio_target
    NT_portfolio_target -->|risk_check / 风控检查| NT_risk_check
    NT_risk_check -->|approving / 批准| NT_order
    NT_order -->|triggering / 触发| NT_execution
    NT_execution -.->|feedback / 反馈| NT_feedback
    NT_feedback -.->|informing / 告知| NT_signal
    NT_signal -.->|禁止| NT_order
    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5
    INV_DEC_INV_001(["DEC-INV-001<br/>风控一票否决<br/>Risk Veto Mandatory"])
    INV_DEC_INV_002(["DEC-INV-002<br/>信号仓位分离<br/>Signal-Order Separation"])
    INV_DEC_INV_003(["DEC-INV-003<br/>DAG 无环<br/>DAG No-Cycle"])
    INV_DEC_INV_004(["DEC-INV-004<br/>时间单调性<br/>Time Monotonicity"])
    INV_DEC_INV_005(["DEC-INV-005<br/>证据哈希必填<br/>Evidence Hash Required"])
    INV_DEC_INV_001 -.- NT_order
    INV_DEC_INV_002 -.- NT_signal
    INV_DEC_INV_003 -.- NT_feedback
    INV_DEC_INV_005 -.- NT_signal
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class NT_signal,NT_portfolio_target,NT_risk_check,NT_order,NT_execution,NT_feedback,INV_DEC_INV_001,INV_DEC_INV_002,INV_DEC_INV_003,INV_DEC_INV_004,INV_DEC_INV_005 design
```

