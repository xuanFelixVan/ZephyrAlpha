---
doc_type: architecture_view
title: D-INFRA_OPS 基础设施运维架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 02_d_infra_ops / 基础设施运维 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示基础设施运维（D-INFRA_OPS）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 基础设施运维（D-INFRA_OPS）的模块分布。共 46 个模块 / 46 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│         L0 基础设施层 / Infrastructure Layer (5 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   基础设施运维域  [design]                                       │
│   告警管理  [design]                                             │
│   容量管理  [design]                                             │
│   部署管理  [design]                                             │
│   基础设施监控  [design]                                         │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (29 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   config/infra/grafana/dashboards/provider.yml  [production]     │
│   config/infra/grafana/datasources/prometheus.yml  [production]  │
│   config/infra/prometheus/prometheus.yml  [production]           │
│   src/zephyr/governance/auto_rollback_trigger.py  [prototype]    │
│   src/zephyr/governance/rollback_simulator.py  [prototype]       │
│   src/zephyr/governance/rollback_wal.py  [prototype]             │
│   src/zephyr/infra_ops/__init__.py  [prototype]                  │
│   src/zephyr/infra_ops/_extensions/__init__.py  [prototype]      │
│   src/zephyr/infra_ops/api/__init__.py  [prototype]              │
│   src/zephyr/infra_ops/core/__init__.py  [prototype]             │
│   src/zephyr/infra_ops/dashboard/app.py  [prototype]             │
│   src/zephyr/infra_ops/dashboard/components/fitness_functions... │
│   src/zephyr/infra_ops/dashboard/components/gate_statistics.p... │
│   src/zephyr/infra_ops/dashboard/components/knowledge_overvie... │
│   src/zephyr/infra_ops/dashboard/components/olap_trend.py  [p... │
│   src/zephyr/infra_ops/dashboard/components/task_progress.py ... │
│   src/zephyr/infra_ops/infrastructure/__init__.py  [prototype]   │
│   src/zephyr/infra_ops/interface_base.py  [prototype]            │
│   ...还有 11 个模块 / 11 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (12 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   F15-auto-fix/  [design]                                        │
│   F19-telemetry/  [design]                                       │
│   F21-ide-health/  [design]                                      │
│   F25-db-integration/  [design]                                  │
│   F27-capacity/  [design]                                        │
│   F33-local-model/  [design]                                     │
│   F37-resource-opt/  [design]                                    │
│   F9-rollback/  [design]                                         │
│   scripts/construction/test_deepseek_api.py  [production]        │
│   scripts/ide_health_service.py  [production]                    │
│   src/zephyr/infra_ops/dashboard/__init__.py  [production]       │
│   src/zephyr/infra_ops/dashboard/components/__init__.py  [pro... │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 46 个模块 / 46 modules）。

### L0 基础设施层 / Infrastructure Layer (5 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/infra_ops/ | 基础设施运维域 | design | planned |
| 2 | src/zephyr/infra_ops/alerting/ | 告警管理 | design | planned |
| 3 | src/zephyr/infra_ops/capacity/ | 容量管理 | design | planned |
| 4 | src/zephyr/infra_ops/deployment/ | 部署管理 | design | planned |
| 5 | src/zephyr/infra_ops/monitoring/ | 基础设施监控 | design | planned |

### L1 基础层 / Foundation Layer (29 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/infra/grafana/dashboards/provider.yml | config/infra/grafana/dashboards/provi... | production | deprecated |
| 2 | config/infra/grafana/datasources/prometheus.yml | config/infra/grafana/datasources/prom... | production | deprecated |
| 3 | config/infra/prometheus/prometheus.yml | config/infra/prometheus/prometheus.yml | production | deprecated |
| 4 | src/zephyr/governance/auto_rollback_trigger.py | src/zephyr/governance/auto_rollback_t... | prototype | generated |
| 5 | src/zephyr/governance/rollback_simulator.py | src/zephyr/governance/rollback_simula... | prototype | generated |
| 6 | src/zephyr/governance/rollback_wal.py | src/zephyr/governance/rollback_wal.py | prototype | generated |
| 7 | src/zephyr/infra_ops/__init__.py | src/zephyr/infra_ops/__init__.py | prototype | generated |
| 8 | src/zephyr/infra_ops/_extensions/__init__.py | src/zephyr/infra_ops/_extensions/__in... | prototype | deprecated |
| 9 | src/zephyr/infra_ops/api/__init__.py | src/zephyr/infra_ops/api/__init__.py | prototype | deprecated |
| 10 | src/zephyr/infra_ops/core/__init__.py | src/zephyr/infra_ops/core/__init__.py | prototype | deprecated |
| 11 | src/zephyr/infra_ops/dashboard/app.py | src/zephyr/infra_ops/dashboard/app.py | prototype | generated |
| 12 | src/zephyr/infra_ops/dashboard/components/fitness_functio... | src/zephyr/infra_ops/dashboard/compon... | prototype | generated |
| 13 | src/zephyr/infra_ops/dashboard/components/gate_statistics.py | src/zephyr/infra_ops/dashboard/compon... | prototype | generated |
| 14 | src/zephyr/infra_ops/dashboard/components/knowledge_overv... | src/zephyr/infra_ops/dashboard/compon... | prototype | generated |
| 15 | src/zephyr/infra_ops/dashboard/components/olap_trend.py | src/zephyr/infra_ops/dashboard/compon... | prototype | generated |
| 16 | src/zephyr/infra_ops/dashboard/components/task_progress.py | src/zephyr/infra_ops/dashboard/compon... | prototype | generated |
| 17 | src/zephyr/infra_ops/infrastructure/__init__.py | src/zephyr/infra_ops/infrastructure/_... | prototype | deprecated |
| 18 | src/zephyr/infra_ops/interface_base.py | src/zephyr/infra_ops/interface_base.py | prototype | generated |
| 19 | src/zephyr/infra_ops/models/__init__.py | src/zephyr/infra_ops/models/__init__.py | prototype | deprecated |
| 20 | src/zephyr/infra_ops/services/__init__.py | src/zephyr/infra_ops/services/__init_... | prototype | deprecated |
| 21 | src/zephyr/infrastructure/rollback/governance/__init__.py | src/zephyr/infrastructure/rollback/go... | prototype | generated |
| 22 | src/zephyr/infrastructure/rollback/governance/auditor.py | src/zephyr/infrastructure/rollback/go... | prototype | generated |
| 23 | src/zephyr/infrastructure/rollback/governance/budget_trac... | src/zephyr/infrastructure/rollback/go... | prototype | generated |
| 24 | src/zephyr/infrastructure/rollback/governance/contracts.py | src/zephyr/infrastructure/rollback/go... | prototype | generated |
| 25 | src/zephyr/infrastructure/rollback/governance/drift_fix.py | src/zephyr/infrastructure/rollback/go... | prototype | generated |
| 26 | src/zephyr/infrastructure/rollback/governance/result_type... | src/zephyr/infrastructure/rollback/go... | prototype | generated |
| 27 | tests/test_auto_rollback_trigger.py | tests/test_auto_rollback_trigger.py | prototype | generated |
| 28 | tests/test_rollback_simulator.py | tests/test_rollback_simulator.py | prototype | generated |
| 29 | tests/test_rollback_wal.py | tests/test_rollback_wal.py | prototype | generated |

### 未分类 / Unclassified (12 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F15-auto-fix/ | F15-auto-fix/ | design | stable |
| 2 | F19-telemetry/ | F19-telemetry/ | design | stable |
| 3 | F21-ide-health/ | F21-ide-health/ | design | stable |
| 4 | F25-db-integration/ | F25-db-integration/ | design | stable |
| 5 | F27-capacity/ | F27-capacity/ | design | stable |
| 6 | F33-local-model/ | F33-local-model/ | design | stable |
| 7 | F37-resource-opt/ | F37-resource-opt/ | design | stable |
| 8 | F9-rollback/ | F9-rollback/ | design | stable |
| 9 | scripts/construction/test_deepseek_api.py | scripts/construction/test_deepseek_ap... | production | generated |
| 10 | scripts/ide_health_service.py | scripts/ide_health_service.py | production | generated |
| 11 | src/zephyr/infra_ops/dashboard/__init__.py | src/zephyr/infra_ops/dashboard/__init... | production | generated |
| 12 | src/zephyr/infra_ops/dashboard/components/__init__.py | src/zephyr/infra_ops/dashboard/compon... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 11 条 / 11 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 11 条 / 11 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 3                               │
│   [config_depends]: 8 条 / edges                                 │
│   [data]: 2 条 / edges                                           │
│   [import_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (8 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   interface_base.py → __init__.py                                │
│   gate_statistics.py → fitness_functions.py                      │
│   task_progress.py → gate_statistics.py                          │
│   knowledge_overview.py → gate_statistics.py                     │
│   olap_trend.py → gate_statistics.py                             │
│   budget_tracker.py → __init__.py                                │
│   drift_fix.py → __init__.py                                     │
│   result_types.py → __init__.py                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      [data] (2 条 / edges)                       │
├──────────────────────────────────────────────────────────────────┤
│    →                                                             │
│    →                                                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   app.py → __init__.py                                           │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `02_d_infra_ops_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
