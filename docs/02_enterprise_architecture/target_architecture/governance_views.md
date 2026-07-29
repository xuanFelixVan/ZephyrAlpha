---
module_id: VIEW-TA-GOV
title: 治理架构图
doc_type: architecture_view
status: Active
version: 0.1.0
owner: ZephyrAlpha-Owner
valid_from: 2026-07-22
ttl: permanent
tags:
- architecture-view
- pending-review
---

# 治理架构图

> **单一真源 / Single Source of Truth** — 本文档内嵌 mermaid 图，原独立 `.mmd` 已删除。

---

## governance d2b loop

> Source: 04_architecture_principles_decisions/governance_principles.md

```mermaid
graph LR
    P["① Policy 层<br/>规则文本定义"]
    F["② Factory 层<br/>检查器工厂"]
    R["③ Runtime 层<br/>执行+审计"]
    A["④ Audit Log<br/>append-only ledger"]

    P -->|"① policy_compiler<br/>(Markdown → Rego / config)"| F
    F -->|"② hook registration<br/>(pre-commit / CI / call)"| R
    R -->|"③ ledger write<br/>(JSONL append-only)"| A
    A -->|"④ feedback_to_policy.py<br/>(聚合审计数据 → PR 提案)"| P

    classDef policy fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef factory fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef runtime fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef audit fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class P policy
    class F factory
    class R runtime
    class A audit
```

---

## governance three layers

> Source: 04_architecture_principles_decisions/governance_principles.md

```mermaid
graph TB
    subgraph 被治理者[被治理者：业务层 + 文档层 + 前端层 + 治理层自己]
        BIZ["src/zephyr/ 53 域业务代码"]
        DOC["docs/ 21 抽屉文档"]
        FE["frontend/ 4 子层"]
        CONTRACT["shared/contracts/ 契约基类"]
        GOV_SELF["治理层自己（自治）"]
    end

    subgraph 治理三层[治理三层：横切正交]
        P["Policy 层<br/>定规则 / 存 / 版本化<br/>docs/01_policies_and_standards/<br/>docs/02_enterprise_architecture/adr/<br/>.cursor/rules/ + .trae/rules/"]
        F["Factory 层<br/>造工具 / 编译规则<br/>scripts/arch_guard/<br/>scripts/governance/<br/>scripts/quality/"]
        R["Runtime 层<br/>执行 / 审计 / 反馈<br/>.pre-commit / CI<br/>d_compliance/<br/>scripts/audit_log/ + opa/"]
    end

    BIZ --> P
    DOC --> P
    FE --> P
    CONTRACT --> P
    GOV_SELF --> P

    P -->|规则编译| F
    F -->|工具调度| R
    R -->|审计反馈回写| P

    R -->|拦截+放行| BIZ
    R -->|拦截+放行| DOC
    R -->|拦截+放行| FE
    R -->|拦截+放行| CONTRACT
    R -->|拦截+放行| GOV_SELF

    classDef policy fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef factory fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef runtime fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef bizLayer fill:#e8f5f9,stroke:#1b5e20,stroke-width:1px

    class P policy
    class F factory
    class R runtime
    class BIZ,DOC,FE,CONTRACT,GOV_SELF bizLayer
```
