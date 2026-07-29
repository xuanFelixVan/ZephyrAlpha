---
module_id: VIEW-TA-TOPO
title: 架构拓扑图
doc_type: architecture_view
status: Active
version: 0.2.0
owner: ZephyrAlpha-Owner
valid_from: 2026-07-22
ttl: permanent
tags:
- architecture-view
---

# 架构拓扑图

> **单一真源 / Single Source of Truth** — 本文档内嵌 mermaid 图，原独立 `.mmd` 已删除。

> **生成视图 / Generated View** — 集成拓扑图（integration topology）已由 `generate_integration_topology.py` 从 depgraph 自动生成，见 [`01_global_architecture_diagram/integration_topology.md`](../01_global_architecture_diagram/integration_topology.md)。本文件仅保留无生成器的手绘概念图（TOGAF 层栈 + docs/scripts/runtime 拓扑）。

---

## togaf layer stack

```mermaid
%%{init: {'theme': 'default'}}%%
graph TB
    BA["<b>01. Business Architecture (BA)</b><br/>业务架构<br/>Who we serve · What we do · Core processes · NFR<br/>为谁服务 · 做什么 · 核心流程 · 非功能需求"]
    IA["<b>02. Information Architecture (IA)</b><br/>信息架构<br/>What information assets exist · docs/ drawer taxonomy<br/>有哪些信息资产 · docs/ 抽屉体系"]
    AA["<b>03. Application Architecture (AA)</b><br/>应用架构<br/>What modules/services · How they interact · src/ + scripts/<br/>有哪些应用/模块 · 如何交互 · src/ + scripts/"]
    TA["<b>04. Technology Architecture (TA)</b><br/>技术架构<br/>What tech stack · Runtime topology · Deployment<br/>用什么技术栈 · 运行时拓扑 · 部署方式"]

    BA -->|drives / 驱动| IA
    IA -->|drives / 驱动| AA
    AA -->|drives / 驱动| TA
    TA -.->|reverse constrains / 反向约束| AA
    AA -.->|reverse constrains / 反向约束| IA
    IA -.->|reverse constrains / 反向约束| BA

    style BA fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    style IA fill:#dcfce7,stroke:#16a34a,color:#14532d
    style AA fill:#fef9c3,stroke:#ca8a04,color:#713f12
    style TA fill:#fce7f3,stroke:#db2777,color:#831843
```

---

## docs drawer topology

```mermaid
%%{init: {'theme': 'default'}}%%
%% v2.0.0: 同步对齐 information_principles.md §2 + directory_registry.yaml 的6顶级目录结构（原20+抽屉已简化）
graph TB
    subgraph GOV["治理层 / Governance"]
        G01["01_policies_and_standards<br/>规则 / 标准 / 模板 / 注册表"]
    end

    subgraph ARCH["架构层 / Architecture"]
        A02["02_enterprise_architecture<br/>target_architecture/ + generated/<br/>04_architecture_principles_decisions/"]
    end

    subgraph DESIGN["设计层 / Design"]
        D04["04_design<br/>技术设计文档 / RFC / 方案"]
    end

    subgraph MOD["模块蓝图层 / Module Blueprints"]
        M03["03_modules<br/>_domain_* 53域 + _cross_layer<br/>+ _master_blueprint + _system_master"]
    end

    subgraph KB["知识层 / Knowledge"]
        K08["08_knowledge<br/>研究 / 决策 / 未来能力"]
    end

    WS["docs/_working/<br/>过程区（task_bound）"]
    AR["docs/_archive/<br/>历史区（retired）"]

    GOV -->|"政策 / 标准 / 风险"| ARCH
    ARCH -->|"原则 / 决策"| DESIGN
    DESIGN -->|"蓝图 / 施工图"| MOD
    MOD -->|"沉淀 / 反馈"| KB
    WS -->|"promote / 升格"| ARCH
    WS -->|"promote / 升格"| MOD
    ARCH -->|"retire / 退役"| AR
    MOD -->|"retire / 退役"| AR

    style GOV fill:#fef2f2,stroke:#ef4444
    style ARCH fill:#eff6ff,stroke:#3b82f6
    style DESIGN fill:#fffbeb,stroke:#f59e0b
    style MOD fill:#f0fdf4,stroke:#16a34a
    style KB fill:#fdf4ff,stroke:#a855f7
    style WS fill:#f8fafc,stroke:#94a3b8
    style AR fill:#f1f5f9,stroke:#cbd5e1
```

---

## scripts topology

```mermaid
%%{init: {'theme': 'default'}}%%
graph LR
    subgraph SCRIPTS["scripts/ — Governance code / 治理代码"]
        GOV["governance/<br/>File governance automation<br/>文件治理自动化"]
        ARCH_GUARD["arch_guard/<br/>Architecture guards<br/>架构守护"]
        HOOKS["hooks/<br/>Pre-commit &amp; local guards<br/>pre-commit 与本地守卫"]
        PRECOMMIT["pre_commit/<br/>Pre-commit config &amp; scripts<br/>pre-commit 配置与脚本"]
        REPORTS["reports/<br/>Report generation<br/>报告生成"]
        MCP["mcp/<br/>MCP tools<br/>MCP 工具"]
        OPS["ops/<br/>Ops scripts<br/>运维脚本"]
        CONSTRUCTION["construction/<br/>Construction scripts<br/>施工脚本"]
    end

    subgraph SRC["src/zephyr/ — Product code / 产品代码"]
        D10["D_COMPLIANCE 域<br/>Product-level governance<br/>产品级治理合规"]
    end

    HOOKS -->|"runs on commit / 提交时运行"| GOV
    HOOKS -->|"runs on commit / 提交时运行"| ARCH_GUARD
    PRECOMMIT -->|"runs on commit / 提交时运行"| GOV
    GOV -.->|"boundary: repo-level only<br/>边界：仅仓库级"| D10

    style SCRIPTS fill:#f8fafc,stroke:#94a3b8
    style SRC fill:#eff6ff,stroke:#3b82f6
    style HOOKS fill:#fef9c3,stroke:#ca8a04
    style GOV fill:#dcfce7,stroke:#16a34a
    style ARCH_GUARD fill:#fce7f3,stroke:#db2777
    style PRECOMMIT fill:#e0f2fe,stroke:#0284c7
    style REPORTS fill:#f0fdf4,stroke:#16a34a
    style MCP fill:#fdf4ff,stroke:#a855f7
    style OPS fill:#fffbeb,stroke:#f59e0b
    style CONSTRUCTION fill:#f1f5f9,stroke:#cbd5e1
    style D10 fill:#eff6ff,stroke:#3b82f6
```

---

## runtime topology

> 重写时间: 2026-06-26 (DM-200913 Phase4-B)
> 基于§2.1裁定: 14层降级为域属性，53域为唯一物理分类体系
> 数据源: depgraph
> 图例: 🔒 = frozen (不可变契约) | 🔓 = mutable (可变契约，状态机)
> 契约真源: architecture_model/contracts/cross_layer_contracts.yaml
> Source: technology_principles.md §3.2
> v2.0.0: 14层节点→53域节点，保留P0跨层契约标注

```mermaid
graph TD
    subgraph HOST["Host Machine（当前：Windows / 计划：Linux）"]
        subgraph MAIN["ZephyrAlpha Main Process (Python)"]
            direction TB
            D_MKT_DATA["D-MKT_DATA<br/>行情数据"] -->|"🔒 CTR-001<br/>NormalizedMarketData"| D_FACTOR["D-FACTOR<br/>因子"]
            D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal"| D_SIGNAL["D-SIGLEGACY<br/>信号"]
            D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal"| D_RISK["D-RISK<br/>风控"]
            D_FACTOR -->|"🔒 CTR-002<br/>FactorSignal"| D_PF_CORE["D-PF_CORE<br/>组合"]
            D_RISK -->|"🔒 CTR-003<br/>RiskLimits"| D_PF_CORE
            D_PF_CORE -->|"🔓 CTR-004<br/>Order"| D_EX_CORE["D-EX_CORE<br/>执行"]
            D_EX_CORE -->|"🔒 CTR-005<br/>Fill + 🔒 CTR-006<br/>PositionSnapshot"| D_TRADING["D-TRADING<br/>交易运营"]
            D_TRADING -->|"Report"| D_FRONTEND["D-FRONTEND<br/>前端"]
        end
        subgraph STORAGE["Local Storage"]
            DB["Data Store (Parquet / DuckDB · 待定)"]
            DOCS["docs/ (Git + Markdown)"]
        end
        MAIN -->|"写入"| DB
        MAIN -->|"读写"| DOCS
    end
    subgraph EXT["External Systems"]
        MKT["Market Data (REST/WS)"]
        BRK["Broker API (REST/FIX)"]
        LLM["LLM Providers (REST)"]
        FEISHU["Feishu (Webhook)"]
    end
    MKT -->|"行情"| D_MKT_DATA
    D_EX_CORE -->|"委托"| BRK
    BRK -->|"成交回报"| D_EX_CORE
    D_FRONTEND -->|"AI 推理"| LLM
    D_FRONTEND -->|"通知"| FEISHU

    style MAIN fill:#eff6ff,stroke:#3b82f6
    style HOST fill:#f8fafc,stroke:#94a3b8
    style EXT fill:#fef2f2,stroke:#ef4444
    style STORAGE fill:#fefce8,stroke:#eab308
```
