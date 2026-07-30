# 决策流图 · 不变量图

> 生成时间: 2026-07-30T20:58:07
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 辅助图

6 节点类型 + 5 承重墙不变量 + 合法/非法连接标注。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    NT_signal["信号节点<br/>Signal"]
    NT_portfolio_target["仓位目标节点<br/>Portfolio Target"]
    NT_risk_check["风控节点<br/>Risk Check"]
    NT_order["订单节点<br/>Order"]
    NT_execution["执行节点<br/>Execution"]
    NT_feedback["反馈节点<br/>Feedback"]
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
```

