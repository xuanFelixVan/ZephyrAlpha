---
doc_type: domain_architecture_diagram
title: D-COMPLIANCE 合规架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 24_d_compliance / 合规 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示合规（D-COMPLIANCE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 合规（D-COMPLIANCE）的模块分布。共 30 个模块 / 30 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (30 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/compliance/__init__.py  [prototype]                 │
│   src/zephyr/compliance/_extensions/__init__.py  [prototype]     │
│   src/zephyr/compliance/aisg_sandbox.py  [prototype]             │
│   src/zephyr/compliance/api/__init__.py  [prototype]             │
│   src/zephyr/compliance/artifact_scanner.py  [prototype]         │
│   src/zephyr/compliance/audit_orchestrator/__init__.py  [prot... │
│   src/zephyr/compliance/audit_trail/__init__.py  [prototype]     │
│   src/zephyr/compliance/audit_trail/bridges/__init__.py  [pro... │
│   src/zephyr/compliance/behavioral_admission/__init__.py  [pr... │
│   src/zephyr/compliance/behavioral_auditor/__init__.py  [prot... │
│   src/zephyr/compliance/compliance_gate_a6/__init__.py  [prot... │
│   src/zephyr/compliance/compliance_manager.py  [prototype]       │
│   src/zephyr/compliance/core/__init__.py  [prototype]            │
│   src/zephyr/compliance/default_security_gateway.py  [prototype] │
│   src/zephyr/compliance/evidence_pack.py  [prototype]            │
│   src/zephyr/compliance/financial_compliance.py  [prototype]     │
│   src/zephyr/compliance/implementations/__init__.py  [prototype] │
│   src/zephyr/compliance/infrastructure/__init__.py  [prototype]  │
│   ...还有 12 个模块 / 12 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 30 个模块 / 30 modules）。

### L2 领域层 / Domain Layer (30 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/compliance/__init__.py | src/zephyr/compliance/__init__.py | prototype | generated |
| 2 | src/zephyr/compliance/_extensions/__init__.py | src/zephyr/compliance/_extensions/__i... | prototype | deprecated |
| 3 | src/zephyr/compliance/aisg_sandbox.py | src/zephyr/compliance/aisg_sandbox.py | prototype | generated |
| 4 | src/zephyr/compliance/api/__init__.py | src/zephyr/compliance/api/__init__.py | prototype | deprecated |
| 5 | src/zephyr/compliance/artifact_scanner.py | src/zephyr/compliance/artifact_scanne... | prototype | generated |
| 6 | src/zephyr/compliance/audit_orchestrator/__init__.py | src/zephyr/compliance/audit_orchestra... | prototype | generated |
| 7 | src/zephyr/compliance/audit_trail/__init__.py | src/zephyr/compliance/audit_trail/__i... | prototype | generated |
| 8 | src/zephyr/compliance/audit_trail/bridges/__init__.py | src/zephyr/compliance/audit_trail/bri... | prototype | generated |
| 9 | src/zephyr/compliance/behavioral_admission/__init__.py | src/zephyr/compliance/behavioral_admi... | prototype | generated |
| 10 | src/zephyr/compliance/behavioral_auditor/__init__.py | src/zephyr/compliance/behavioral_audi... | prototype | generated |
| 11 | src/zephyr/compliance/compliance_gate_a6/__init__.py | src/zephyr/compliance/compliance_gate... | prototype | generated |
| 12 | src/zephyr/compliance/compliance_manager.py | src/zephyr/compliance/compliance_mana... | prototype | generated |
| 13 | src/zephyr/compliance/core/__init__.py | src/zephyr/compliance/core/__init__.py | prototype | deprecated |
| 14 | src/zephyr/compliance/default_security_gateway.py | src/zephyr/compliance/default_securit... | prototype | generated |
| 15 | src/zephyr/compliance/evidence_pack.py | src/zephyr/compliance/evidence_pack.py | prototype | generated |
| 16 | src/zephyr/compliance/financial_compliance.py | src/zephyr/compliance/financial_compl... | prototype | generated |
| 17 | src/zephyr/compliance/implementations/__init__.py | src/zephyr/compliance/implementations... | prototype | generated |
| 18 | src/zephyr/compliance/infrastructure/__init__.py | src/zephyr/compliance/infrastructure/... | prototype | deprecated |
| 19 | src/zephyr/compliance/integrity.py | src/zephyr/compliance/integrity.py | prototype | generated |
| 20 | src/zephyr/compliance/merkle_hourly.py | src/zephyr/compliance/merkle_hourly.py | prototype | generated |
| 21 | src/zephyr/compliance/models/__init__.py | src/zephyr/compliance/models/__init__.py | prototype | deprecated |
| 22 | src/zephyr/compliance/security_gateway_base.py | src/zephyr/compliance/security_gatewa... | prototype | generated |
| 23 | src/zephyr/compliance/semantic_auditor/__init__.py | src/zephyr/compliance/semantic_audito... | prototype | generated |
| 24 | src/zephyr/compliance/services/__init__.py | src/zephyr/compliance/services/__init... | prototype | deprecated |
| 25 | src/zephyr/compliance/zero_knowledge_audit_stub/__init__.py | src/zephyr/compliance/zero_knowledge_... | prototype | generated |
| 26 | 交易监控规则引擎+监管报告生成器+身份验证集成器+风险管理集... | RegTech Compliance Automation Engine | design | planned |
| 27 | 合规域-交易纪律/D-COMPLIANCE-23 | A-Share Trading Discipline Checker | design | planned |
| 28 | 合规域-持续运营/D-COMPLIANCE-13 | AML/KYC Engine | design | planned |
| 29 | 合规域-规则验证/D-COMPLIANCE-20 | Compliance Rule Backtester | design | planned |
| 30 | 异常交易披露数据采集器(监管披露数据→统计因子)/D-DATA-89 | 龙虎榜 | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 2 条 / 2 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 2 条 / 2 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [config_depends]: 1 条 / edges                                 │
│   [import_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → artifact_scanner.py                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → __init__.py                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `24_d_compliance_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
