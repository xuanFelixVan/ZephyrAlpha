---
doc_type: architecture_view
title: D-REPORTING 报告架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 17_d_reporting / 报告 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示报告（D-REPORTING）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 报告（D-REPORTING）的模块分布。共 19 个模块 / 19 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (4 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   Report Watermark Tracker  [design]                             │
│   Report Publisher  [design]                                     │
│   Risk Report Engine  [design]                                   │
│   Regulatory Report Generator  [design]                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (14 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/reporting/__init__.py  [prototype]                  │
│   src/zephyr/reporting/__init___from_obs.py  [prototype]         │
│   src/zephyr/reporting/_extensions/__init__.py  [prototype]      │
│   src/zephyr/reporting/analytics_base.py  [prototype]            │
│   src/zephyr/reporting/api/__init__.py  [prototype]              │
│   src/zephyr/reporting/core/__init__.py  [prototype]             │
│   src/zephyr/reporting/default_attribution_engine.py  [protot... │
│   src/zephyr/reporting/default_tca_engine.py  [prototype]        │
│   src/zephyr/reporting/implementations/__init__.py  [prototype]  │
│   src/zephyr/reporting/implementations/default_attribution_en... │
│   src/zephyr/reporting/implementations/default_tca_engine.py ... │
│   src/zephyr/reporting/infrastructure/__init__.py  [prototype]   │
│   src/zephyr/reporting/models/__init__.py  [prototype]           │
│   src/zephyr/reporting/services/__init__.py  [prototype]         │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (1 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   scripts/demos/demo_e2e_pipeline.py  [production]               │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 19 个模块 / 19 modules）。

### L1 基础层 / Foundation Layer (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 报告域-水印追踪/D-REPORTING-17 | Report Watermark Tracker | design | planned |
| 2 | 报告域/D-REPORTING-03 | Report Publisher | design | planned |
| 3 | 报告域/D-REPORTING-08 | Risk Report Engine | design | planned |
| 4 | 监管报告生成器(证监会/交易所报告+数据完整性校验)/D-REPORT... | Regulatory Report Generator | design | planned |

### L2 领域层 / Domain Layer (14 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/reporting/__init__.py | src/zephyr/reporting/__init__.py | prototype | generated |
| 2 | src/zephyr/reporting/__init___from_obs.py | src/zephyr/reporting/__init___from_ob... | prototype | generated |
| 3 | src/zephyr/reporting/_extensions/__init__.py | src/zephyr/reporting/_extensions/__in... | prototype | deprecated |
| 4 | src/zephyr/reporting/analytics_base.py | src/zephyr/reporting/analytics_base.py | prototype | generated |
| 5 | src/zephyr/reporting/api/__init__.py | src/zephyr/reporting/api/__init__.py | prototype | deprecated |
| 6 | src/zephyr/reporting/core/__init__.py | src/zephyr/reporting/core/__init__.py | prototype | deprecated |
| 7 | src/zephyr/reporting/default_attribution_engine.py | src/zephyr/reporting/default_attribut... | prototype | generated |
| 8 | src/zephyr/reporting/default_tca_engine.py | src/zephyr/reporting/default_tca_engi... | prototype | generated |
| 9 | src/zephyr/reporting/implementations/__init__.py | src/zephyr/reporting/implementations/... | prototype | generated |
| 10 | src/zephyr/reporting/implementations/default_attribution_... | src/zephyr/reporting/implementations/... | prototype | generated |
| 11 | src/zephyr/reporting/implementations/default_tca_engine.py | src/zephyr/reporting/implementations/... | prototype | generated |
| 12 | src/zephyr/reporting/infrastructure/__init__.py | src/zephyr/reporting/infrastructure/_... | prototype | deprecated |
| 13 | src/zephyr/reporting/models/__init__.py | src/zephyr/reporting/models/__init__.py | prototype | deprecated |
| 14 | src/zephyr/reporting/services/__init__.py | src/zephyr/reporting/services/__init_... | prototype | deprecated |

### 未分类 / Unclassified (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | scripts/demos/demo_e2e_pipeline.py | scripts/demos/demo_e2e_pipeline.py | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 1 条 / 1 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 1 条 / 1 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init___from_obs.py → __init__.py                             │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `17_d_reporting_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
