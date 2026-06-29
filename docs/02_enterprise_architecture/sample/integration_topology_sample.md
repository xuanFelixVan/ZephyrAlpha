---
module_id: ARCH-SMP-005
title: "集成拓扑图样板 / Integration Topology Sample"
doc_type: architecture_view
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 集成拓扑图样板 / Integration Topology Sample

> 这是给人看的所有功能域集成依赖关系图，用 Mermaid 格式可视化。
> IDE 可直接渲染显示。

---

## 集成拓扑图 / Integration Topology

```mermaid
graph LR
    %% 按层分组显示域节点 / Group domains by layer
    subgraph L0["基础设施层 / Infrastructure"]
        infra_ops["D_INFRA_OPS<br/>基础设施运维"]
        infra_runtime["D_INFRA_RUNTIME<br/>运行时集成"]
    end

    subgraph L1_foundation["基础层 / Foundation"]
        alt_data["D_ALT_DATA<br/>另类数据"]
        data_eng["D_DATA_ENG<br/>数据工程"]
        data_sec["D_DATA_SEC<br/>数据安全"]
    end

    subgraph L1_platform["平台层 / Platform"]
        autonomy["D_AUTONOMY_CORE<br/>自治核心"]
        frontend["D_FRONTEND<br/>前端"]
        integration["D_INTEGRATION<br/>集成"]
    end

    subgraph L2_domain["业务域层 / Business Domain"]
        trading["D_TRADING<br/>交易运营"]
        backtest["D_BACKTEST<br/>回测"]
        risk["D_RISK<br/>风险"]
        reporting["D_REPORTING<br/>报告"]
        compliance["D_COMPLIANCE<br/>合规"]
    end

    %% 跨域依赖关系 / Cross-domain dependencies
    infra_ops -->|基础设施服务| infra_runtime
    infra_runtime -->|运行时支持| autonomy
    infra_runtime -->|运行时支持| integration

    alt_data -->|数据输入| data_eng
    data_eng -->|数据服务| trading
    data_eng -->|数据服务| backtest
    data_sec -->|安全校验| trading

    autonomy -->|调度| trading
    autonomy -->|调度| backtest

    integration -->|集成管道| trading
    integration -->|集成管道| reporting

    trading -->|交易数据| risk
    trading -->|交易数据| reporting
    trading -->|交易数据| compliance

    backtest -->|回测结果| trading
    risk -.->|风控信号| trading

    %% 样式 / Styling
    classDef infra fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef foundation fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef platform fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px
    classDef business fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class infra_ops,infra_runtime infra
    class alt_data,data_eng,data_sec foundation
    class autonomy,frontend,integration platform
    class trading,backtest,risk,reporting,compliance business
```

---

## 说明

- **数据源**：`depgraph.db` 的 `edges` 表（跨域依赖）
- **生成器**：`generate_integration_topology.py`
- **维护方式**：自动生成，全景图更新时刷新
- **格式要求**：Mermaid 代码块内嵌在 .md 文件中，IDE 可直接渲染显示
- **文件名规则**：`integration_topology.md`（英文 snake_case）
