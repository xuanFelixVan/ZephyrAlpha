---
doc_type: domain_architecture_diagram
title: D-DATA_SEC 数据安全与契约架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 07_d_data_sec / 数据安全与契约 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示数据安全与契约（D-DATA_SEC）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 数据安全与契约（D-DATA_SEC）的模块分布。共 30 个模块 / 30 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (10 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/data/persistence/__init__.py  [prototype]           │
│   src/zephyr/data/persistence/circuit_breaker_types.py  [prot... │
│   src/zephyr/data/persistence/sqlite_schema.py  [prototype]      │
│   src/zephyr/data_security/__init__.py  [prototype]              │
│   src/zephyr/data_security/_extensions/__init__.py  [scaffold... │
│   src/zephyr/data_security/api/__init__.py  [scaffold_placeho... │
│   src/zephyr/data_security/core/__init__.py  [scaffold_placeh... │
│   src/zephyr/data_security/infrastructure/__init__.py  [scaff... │
│   src/zephyr/data_security/models/__init__.py  [scaffold_plac... │
│   src/zephyr/data_security/services/__init__.py  [scaffold_pl... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (20 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   AI Call Audit Log AI调用审计日志  [design]                     │
│   Audit Log 审计日志  [design]                                   │
│   CTR-001 System-Wide Data Contract Registry 数据契约注册中心... │
│   Contract DDD 契约与DDD  [design]                               │
│   Contract Enforcement 契约强制执行  [design]                    │
│   Data Access Audit Log 数据访问审计日志  [design]               │
│   Data Access Auditor 数据访问审计器  [design]                   │
│   Data Contract YAML 数据契约YAML  [design]                      │
│   Data Contract 数据契约  [design]                               │
│   Data Masking Engine 数据脱敏引擎  [design]                     │
│   Data Security Compliance Constraint 数据安全与合规约束  [de... │
│   Data Security Law Benchmark 数据安全法对标  [design]           │
│   Decision Audit Log 决策审计日志  [design]                      │
│   Financial Instrument Contract Library 金融工具契约库  [design] │
│   JR/T 0197 Benchmark 金融数据安全分级指南对标  [design]         │
│   Security Compliance 安全与合规  [design]                       │
│   System Change Audit Log 系统变更审计日志  [design]             │
│   Trading Audit Log 交易审计日志  [design]                       │
│   可执行数据契约 Executable Data Contract  [design]              │
│   引入数据契约标准 Data Contract Standard  [design]              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 30 个模块 / 30 modules）。

### L2 领域层 / Domain Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/data/persistence/__init__.py | src/zephyr/data/persistence/__init__.py | prototype | draft |
| 2 | src/zephyr/data/persistence/circuit_breaker_types.py | src/zephyr/data/persistence/circuit_b... | prototype | draft |
| 3 | src/zephyr/data/persistence/sqlite_schema.py | src/zephyr/data/persistence/sqlite_sc... | prototype | draft |
| 4 | src/zephyr/data_security/__init__.py | src/zephyr/data_security/__init__.py | prototype | orphan |
| 5 | src/zephyr/data_security/_extensions/__init__.py | src/zephyr/data_security/_extensions/... | scaffold_placeholder | orphan |
| 6 | src/zephyr/data_security/api/__init__.py | src/zephyr/data_security/api/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/data_security/core/__init__.py | src/zephyr/data_security/core/__init_... | scaffold_placeholder | orphan |
| 8 | src/zephyr/data_security/infrastructure/__init__.py | src/zephyr/data_security/infrastructu... | scaffold_placeholder | orphan |
| 9 | src/zephyr/data_security/models/__init__.py | src/zephyr/data_security/models/__ini... | scaffold_placeholder | orphan |
| 10 | src/zephyr/data_security/services/__init__.py | src/zephyr/data_security/services/__i... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (20 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-DATA-SEC/AI Call Audit Log AI调用审计日志 | AI Call Audit Log AI调用审计日志 | design | design_only |
| 2 | D-DATA-SEC/Audit Log 审计日志 | Audit Log 审计日志 | design | design_only |
| 3 | D-DATA-SEC/CTR-001 System-Wide Data Contract Registry 数... | CTR-001 System-Wide Data Contract Reg... | design | design_only |
| 4 | D-DATA-SEC/Contract DDD 契约与DDD | Contract DDD 契约与DDD | design | design_only |
| 5 | D-DATA-SEC/Contract Enforcement 契约强制执行 | Contract Enforcement 契约强制执行 | design | design_only |
| 6 | D-DATA-SEC/Data Access Audit Log 数据访问审计日志 | Data Access Audit Log 数据访问审计日志 | design | design_only |
| 7 | D-DATA-SEC/Data Access Auditor 数据访问审计器 | Data Access Auditor 数据访问审计器 | design | design_only |
| 8 | D-DATA-SEC/Data Contract YAML 数据契约YAML | Data Contract YAML 数据契约YAML | design | design_only |
| 9 | D-DATA-SEC/Data Contract 数据契约 | Data Contract 数据契约 | design | design_only |
| 10 | D-DATA-SEC/Data Masking Engine 数据脱敏引擎 | Data Masking Engine 数据脱敏引擎 | design | design_only |
| 11 | D-DATA-SEC/Data Security Compliance Constraint 数据安全与... | Data Security Compliance Constraint ... | design | design_only |
| 12 | D-DATA-SEC/Data Security Law Benchmark 数据安全法对标 | Data Security Law Benchmark 数据安全... | design | design_only |
| 13 | D-DATA-SEC/Decision Audit Log 决策审计日志 | Decision Audit Log 决策审计日志 | design | design_only |
| 14 | D-DATA-SEC/Financial Instrument Contract Library 金融工具... | Financial Instrument Contract Library... | design | design_only |
| 15 | D-DATA-SEC/JR/T 0197 Benchmark 金融数据安全分级指南对标 | JR/T 0197 Benchmark 金融数据安全分级... | design | design_only |
| 16 | D-DATA-SEC/Security Compliance 安全与合规 | Security Compliance 安全与合规 | design | design_only |
| 17 | D-DATA-SEC/System Change Audit Log 系统变更审计日志 | System Change Audit Log 系统变更审计日志 | design | design_only |
| 18 | D-DATA-SEC/Trading Audit Log 交易审计日志 | Trading Audit Log 交易审计日志 | design | design_only |
| 19 | D-DATA-SEC/可执行数据契约 Executable Data Contract | 可执行数据契约 Executable Data Contract | design | design_only |
| 20 | D-DATA-SEC/引入数据契约标准 Data Contract Standard | 引入数据契约标准 Data Contract Standard | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 20 条 / 20 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 20 条 / 20 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 12 条 / edges                                │
│   [contract]: 6 条 / edges                                       │
│   [config_depends]: 1 条 / edges                                 │
│   [runtime]: 1 条 / edges                                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (12 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Data Access Auditor 数据... → Data Masking Engine 数据...      │
│   Data Access Auditor 数据... → JR/T 0197 Benchmark 金融...      │
│   Data Access Auditor 数据... → Security Compliance 安全...      │
│   Data Masking Engine 数据... → Audit Log 审计日志               │
│   Audit Log 审计日志 → Data Security Compliance ...              │
│   Data Security Compliance ... → Trading Audit Log 交易审...     │
│   Data Security Compliance ... → Contract DDD 契约与DDD          │
│   Trading Audit Log 交易审... → Decision Audit Log 决策审...     │
│   Decision Audit Log 决策审... → Data Access Audit Log 数...     │
│   Data Access Audit Log 数... → AI Call Audit Log AI调用...      │
│   Data Access Audit Log 数... → Data Security Law Benchma...     │
│   AI Call Audit Log AI调用... → System Change Audit Log ...      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    [contract] (6 条 / edges)                     │
├──────────────────────────────────────────────────────────────────┤
│   Data Contract 数据契约 → AI Call Audit Log AI调用...           │
│   可执行数据契约 Executable... → Decision Audit Log 决策审...    │
│   CTR-001 System-Wide Data ... → Audit Log 审计日志              │
│   Data Masking Engine 数据... → Data Contract YAML 数据契...     │
│   Contract Enforcement 契约... → Trading Audit Log 交易审...     │
│   Financial Instrument Cont... → Data Security Compliance ...    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → sqlite_schema.py                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     [runtime] (1 条 / edges)                     │
├──────────────────────────────────────────────────────────────────┤
│   引入数据契约标准 Data Con... → Data Access Auditor 数据...     │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `07_d_data_sec_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
