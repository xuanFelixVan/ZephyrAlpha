# 决策流图 · 不变量图

> 生成时间: 2026-07-20T01:15:30
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 辅助图

6 节点类型 + 5 承重墙不变量 + 合法/非法连接标注。

```mermaid
flowchart TD
    NT_signal["信号节点<br/>Signal"]:::nodeType
    NT_portfolio_target["仓位目标节点<br/>Portfolio Target"]:::nodeType
    NT_risk_check["风控节点<br/>Risk Check"]:::nodeType
    NT_order["订单节点<br/>Order"]:::nodeType
    NT_execution["执行节点<br/>Execution"]:::nodeType
    NT_feedback["反馈节点<br/>Feedback"]:::nodeType
    NT_signal -->|portfolio_target| NT_portfolio_target
    NT_portfolio_target -->|risk_check| NT_risk_check
    NT_risk_check -->|approving| NT_order
    NT_order -->|triggering| NT_execution
    NT_execution -.->|feedback| NT_feedback
    NT_feedback -.->|informing| NT_signal
    NT_signal -.->|禁止| NT_order
    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5
    INV_DEC_INV_001(["DEC-INV-001<br/>风控一票否决<br/>Risk Veto Mandatory"]):::invariant
    INV_DEC_INV_002(["DEC-INV-002<br/>信号仓位分离<br/>Signal-Order Separation"]):::invariant
    INV_DEC_INV_003(["DEC-INV-003<br/>DAG 无环<br/>DAG No-Cycle"]):::invariant
    INV_DEC_INV_004(["DEC-INV-004<br/>时间单调性<br/>Time Monotonicity"]):::invariant
    INV_DEC_INV_005(["DEC-INV-005<br/>证据哈希必填<br/>Evidence Hash Required"]):::invariant
    INV_DEC_INV_001 -.- NT_order
    INV_DEC_INV_002 -.- NT_signal
    INV_DEC_INV_003 -.- NT_feedback
    INV_DEC_INV_005 -.- NT_signal

    classDef nodeType fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef invariant fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#000
```

