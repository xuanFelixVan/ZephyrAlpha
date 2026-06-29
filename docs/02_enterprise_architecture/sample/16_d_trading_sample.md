---
module_id: ARCH-SMP-004
title: "16dtrading 域文档样板"
doc_type: architecture_view
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 16_d_trading 域文档样板

> 这是给人看的功能域文档——这个域是干什么的、有哪些模块、模块之间怎么依赖。
> 依赖图内嵌在本文档中（Mermaid 代码块），IDE 可直接渲染显示。

---

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 16 | Number | 16 |
| 域ID | D_TRADING | Domain ID | D_TRADING |
| 域名称 | 交易运营 | Domain Name | Trading Operations |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 249 | Module Count | 249 |
| 域内依赖 | 180 | Internal Dependencies | 180 |
| 跨域入边 | 45 | Cross-domain Incoming | 45 |
| 跨域出边 | 30 | Cross-domain Outgoing | 30 |

---

## 域职责 / Domain Responsibilities

**中文**：交易运营域负责订单生命周期管理，包括订单生成、提交、成交回报、持仓更新、风险控制触发等核心交易流程。

**English**: The Trading Operations domain is responsible for order lifecycle management, including order generation, submission, fill reports, position updates, and risk control triggers.

---

## 模块清单 / Module List

| 模块路径 | 模块功能 | Module Path | Module Function |
|---------|---------|-------------|-----------------|
| `src/zephyr/trading/order/` | 订单生成和管理 / Order generation and management | `src/zephyr/trading/order/` | Order generation and management |
| `src/zephyr/trading/execution/` | 订单执行引擎 / Order execution engine | `src/zephyr/trading/execution/` | Order execution engine |
| `src/zephyr/trading/fill/` | 成交回报处理 / Fill report processing | `src/zephyr/trading/fill/` | Fill report processing |
| `src/zephyr/trading/position/` | 持仓管理 / Position management | `src/zephyr/trading/position/` | Position management |
| `src/zephyr/trading/risk/` | 风险控制 / Risk control | `src/zephyr/trading/risk/` | Risk control |
| ... | ... | ... | ... |

---

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    %% 域内模块 / Internal Modules
    subgraph D_TRADING["D_TRADING 交易运营"]
        order["订单生成和管理 运营<br/>Order Generation production"]
        exec["订单执行引擎 运营<br/>Execution Engine production"]
        fill["成交回报处理 运营<br/>Fill Processing production"]
        pos["持仓管理 运营<br/>Position Management production"]
        risk["风险控制 运营<br/>Risk Control production"]
        portfolio["组合管理 设计<br/>Portfolio Management design"]
    end

    %% 域内依赖关系 / Internal Dependencies
    order -->|生成订单| exec
    exec -->|提交订单| fill
    fill -->|成交数据| pos
    pos -->|持仓数据| portfolio
    portfolio -->|风险指标| risk
    risk -.->|触发风控| order

    %% 跨域入边 / Cross-domain Incoming
    market_data["D-MARKET_DATA 运营<br/>行情数据"]
    market_data -->|行情数据| order

    risk_domain["D_RISK 运营<br/>风险域"]
    risk_domain -->|风控规则| risk

    %% 跨域出边 / Cross-domain Outgoing
    fill -->|成交记录| reporting["D_REPORTING 运营<br/>报告域"]
    pos -.->|持仓数据 设计态| backtest["D_BACKTEST 设计<br/>回测域"]

    %% 样式 / Styling
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5

    class order,exec,fill,pos,risk production
    class portfolio design
    class market_data,risk_domain,reporting external_prod
    class backtest external_design
```

---

## 跨域依赖 / Cross-domain Dependencies

### 依赖的域 / Depends On

| 目标域 | 依赖数 | 主要依赖类型 | Target Domain | Dependency Count | Main Type |
|--------|:---:|------|-------|:---:|------|
| D-MARKET_DATA | 15 | 数据读取 / Data Read | D-MARKET_DATA | 15 | Data Read |
| D_RISK | 10 | 风控检查 / Risk Check | D_RISK | 10 | Risk Check |
| ... | ... | ... | ... | ... | ... |

### 被依赖的域 / Depended By

| 源域 | 依赖数 | 主要依赖类型 | Source Domain | Dependency Count | Main Type |
|------|:---:|------|-------|:---:|------|
| D_BACKTEST | 20 | 回测调用 / Backtest Call | D_BACKTEST | 20 | Backtest Call |
| D_REPORTING | 8 | 报告数据 / Report Data | D_REPORTING | 8 | Report Data |
| ... | ... | ... | ... | ... | ... |

---

## 说明

- **数据源**：`depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器**：`generate_domain_doc.py`
- **维护方式**：自动生成，全景图更新时刷新
- **格式要求**：中英文对照，模块功能一句话简介，Mermaid 依赖图内嵌在文档中
- **文件名规则**：`{编号}_{域ID小写}.md`，如 `16_d_trading.md`
