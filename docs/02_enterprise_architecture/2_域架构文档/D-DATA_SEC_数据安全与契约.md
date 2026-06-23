---
doc_type: domain_architecture_doc
title: D-DATA_SEC 数据安全与契约架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-DATA_SEC 数据安全与契约架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-DATA_SEC |
| 域名称 | 数据安全与契约 |
| 架构层 | L1_foundation |
| 模块总数 | 30 |
| 设计态模块 | 20 |
| 原型态模块 | 4 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 数据安全与契约域。负责数据安全策略、数据契约定义与执行，包括数据加密、访问控制、数据脱敏、数据契约验证。拆分自原D-DATA域。 |

## 模块清单

共 30 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-DATA-SEC/AI Call Audit Log AI调用审计日志 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Audit Log 审计日志 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/CTR-001 System-Wide Data Contract Registry 数据契约注册中心 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Contract DDD 契约与DDD |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Contract Enforcement 契约强制执行 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Access Audit Log 数据访问审计日志 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Access Auditor 数据访问审计器 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Contract YAML 数据契约YAML |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Contract 数据契约 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Masking Engine 数据脱敏引擎 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Security Compliance Constraint 数据安全与合规约束 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Data Security Law Benchmark 数据安全法对标 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Decision Audit Log 决策审计日志 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Financial Instrument Contract Library 金融工具契约库 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/JR/T 0197 Benchmark 金融数据安全分级指南对标 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Security Compliance 安全与合规 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/System Change Audit Log 系统变更审计日志 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/Trading Audit Log 交易审计日志 |  | design_only | design | 0 | 0 |
| D-DATA-SEC/可执行数据契约 Executable Data Contract |  | design_only | design | 0 | 0 |
| D-DATA-SEC/引入数据契约标准 Data Contract Standard |  | design_only | design | 0 | 0 |
| src/zephyr/data/persistence/__init__.py | MOD-DATA_SEC | draft | prototype | 0 | 1 |
| src/zephyr/data/persistence/circuit_breaker_types.py | MOD-DATA_SEC | draft | prototype | 0 | 1 |
| src/zephyr/data/persistence/sqlite_schema.py | MOD-DATA_SEC | draft | prototype | 1 | 1 |
| src/zephyr/data_security/__init__.py | MOD-DATA_SEC | orphan | prototype | 0 | 0 |
| src/zephyr/data_security/_extensions/__init__.py | MOD-DATA_SEC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_security/api/__init__.py | MOD-DATA_SEC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_security/core/__init__.py | MOD-DATA_SEC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_security/infrastructure/__init__.py | MOD-DATA_SEC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_security/models/__init__.py | MOD-DATA_SEC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_security/services/__init__.py | MOD-DATA_SEC | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SECURITY | 7 | event,contract,data,domain_dependency |
| D-GOVERNANCE | 6 | import_depends,contract,data,event |
| D-SIGNAL | 3 | contract,data,event |
| D-MKT_DATA | 3 | data,event |
| D-INTEGRATION | 2 | contract,event |
| D-INFRA_RUNTIME | 2 | data,config_depends |
| D-INFRA_OPS | 2 | contract |
| D-AUTONOMY_CORE | 2 | data,contract |
| D-TRADING | 1 | event |
| D-SIMULATION | 1 | data |
| D-RISK | 1 | event |
| D-REPORTING | 1 | config_depends |
| D-POSITION | 1 | event |
| D-OPS | 1 | import_depends |
| D-ML_TRAIN | 1 | config_depends |
| D-KNOWLEDGE | 1 | data |
| D-INTELLIGENCE | 1 | config_depends |
| D-FRONTEND | 1 | event |
| D-FACTOR | 1 | data |
| D-EX_SOR | 1 | data |
| D-AUTONOMY_PERM | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 3 | data |

## 域内依赖图

详见 [d_data_sec_dependency.mmd](d_data_sec_dependency.mmd)
