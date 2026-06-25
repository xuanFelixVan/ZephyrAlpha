---
doc_type: domain_architecture_diagram
title: D-RISK 风控架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 47_d_risk / 风控 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示风控（D-RISK）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 风控（D-RISK）的模块分布。共 82 个模块 / 82 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/risk/oms_risk_engine.py  [prototype]                │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (81 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/risk/__init__.py  [prototype]                       │
│   src/zephyr/risk/_extensions/__init__.py  [prototype]           │
│   src/zephyr/risk/api/__init__.py  [prototype]                   │
│   src/zephyr/risk/core/__init__.py  [prototype]                  │
│   src/zephyr/risk/cross_asset/__init__.py  [prototype]           │
│   src/zephyr/risk/cross_asset/cross_asset_risk_decomposer/__i... │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/__ini... │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_ex... │
│   src/zephyr/risk/cross_asset/currency_hedger_and_fixed_incom... │
│   src/zephyr/risk/cross_asset/risk_manager.py  [prototype]       │
│   src/zephyr/risk/cross_asset/risk_manager_base.py  [prototype]  │
│   src/zephyr/risk/implementations/__init__.py  [prototype]       │
│   src/zephyr/risk/implementations/default_position_limit_chec... │
│   src/zephyr/risk/implementations/default_risk_limits_calcula... │
│   src/zephyr/risk/implementations/default_risk_manager_orches... │
│   src/zephyr/risk/implementations/default_risk_validator.py  ... │
│   src/zephyr/risk/implementations/default_stop_loss_engine.py... │
│   src/zephyr/risk/infrastructure/__init__.py  [prototype]        │
│   ...还有 63 个模块 / 63 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 82 个模块 / 82 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/risk/oms_risk_engine.py | src/zephyr/risk/oms_risk_engine.py | prototype | generated |

### L2 领域层 / Domain Layer (81 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/risk/__init__.py | src/zephyr/risk/__init__.py | prototype | generated |
| 2 | src/zephyr/risk/_extensions/__init__.py | src/zephyr/risk/_extensions/__init__.py | prototype | deprecated |
| 3 | src/zephyr/risk/api/__init__.py | src/zephyr/risk/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/risk/core/__init__.py | src/zephyr/risk/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/risk/cross_asset/__init__.py | src/zephyr/risk/cross_asset/__init__.py | prototype | generated |
| 6 | src/zephyr/risk/cross_asset/cross_asset_risk_decomposer/_... | src/zephyr/risk/cross_asset/cross_ass... | prototype | deprecated |
| 7 | src/zephyr/risk/cross_asset/cross_market_data_adapter/__i... | src/zephyr/risk/cross_asset/cross_mar... | prototype | generated |
| 8 | src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_... | src/zephyr/risk/cross_asset/cross_mar... | prototype | generated |
| 9 | src/zephyr/risk/cross_asset/currency_hedger_and_fixed_inc... | src/zephyr/risk/cross_asset/currency_... | prototype | deprecated |
| 10 | src/zephyr/risk/cross_asset/risk_manager.py | src/zephyr/risk/cross_asset/risk_mana... | prototype | generated |
| 11 | src/zephyr/risk/cross_asset/risk_manager_base.py | src/zephyr/risk/cross_asset/risk_mana... | prototype | generated |
| 12 | src/zephyr/risk/implementations/__init__.py | src/zephyr/risk/implementations/__ini... | prototype | generated |
| 13 | src/zephyr/risk/implementations/default_position_limit_ch... | src/zephyr/risk/implementations/defau... | production | generated |
| 14 | src/zephyr/risk/implementations/default_risk_limits_calcu... | src/zephyr/risk/implementations/defau... | production | generated |
| 15 | src/zephyr/risk/implementations/default_risk_manager_orch... | src/zephyr/risk/implementations/defau... | production | generated |
| 16 | src/zephyr/risk/implementations/default_risk_validator.py | src/zephyr/risk/implementations/defau... | production | generated |
| 17 | src/zephyr/risk/implementations/default_stop_loss_engine.py | src/zephyr/risk/implementations/defau... | production | generated |
| 18 | src/zephyr/risk/infrastructure/__init__.py | src/zephyr/risk/infrastructure/__init... | prototype | deprecated |
| 19 | src/zephyr/risk/risk_limits.py | src/zephyr/risk/risk_limits.py | prototype | generated |
| 20 | src/zephyr/risk/risk_manager.py | src/zephyr/risk/risk_manager.py | production | generated |
| 21 | src/zephyr/risk/risk_manager_base.py | src/zephyr/risk/risk_manager_base.py | production | generated |
| 22 | src/zephyr/risk/risk_validator.py | src/zephyr/risk/risk_validator.py | production | generated |
| 23 | src/zephyr/risk/services/__init__.py | src/zephyr/risk/services/__init__.py | prototype | deprecated |
| 24 | src/zephyr/risk/stop_loss.py | src/zephyr/risk/stop_loss.py | production | generated |
| 25 | 风控-策略管理/D-RISK-01 | Risk Policy Manager | design | planned |
| 26 | 风控-组合监控/D-RISK-03 | Portfolio Risk Monitor | design | planned |
| 27 | 风控域-A股特色/D-RISK-27 | A-Share Stop-Loss Rule Engine | design | planned |
| 28 | 风控域-A股特色/D-RISK-29 | A-Share PDF Tail Risk Auto-Hedger | design | planned |
| 29 | 风控域-A股特色/D-RISK-30 | A-Share Loss Limit Enforcer | design | planned |
| 30 | 风控域-A股特色/D-RISK-32 | A-Share Contrarian Dedicated Stop-Loss | design | planned |
| 31 | 风控域-A股特色/D-RISK-34 | A-Share First-Minute Stop-Loss Executor | design | planned |
| 32 | 风控域-A股特色/D-RISK-36 | A-Share Multi-Level Loss Circuit Breaker | design | planned |
| 33 | 风控域-A股特色/D-RISK-39 | A-Share Cascading Circuit Breaker | design | planned |
| 34 | 风控域-Kill Switch/D-RISK-54 | Kill Switch Cooldown Manager | design | planned |
| 35 | 风控域-Kill Switch/D-RISK-66 | Kill Switch Multi-Domain Notifier | design | planned |
| 36 | 风控域-Kill Switch/D-RISK-83 | Kill Switch New Order Rejector | design | planned |
| 37 | 风控域-VaR/D-RISK-07 | VaR Calculator | design | planned |
| 38 | 风控域-VaR/D-RISK-41 | Historical Data Representativeness Va... | design | planned |
| 39 | 风控域-VaR/D-RISK-43 | VaR Fast Pre-Screen Alerter | design | planned |
| 40 | 风控域-VaR/D-RISK-45 | Two-Tier Alert Strategy Engine | design | planned |
| 41 | 风控域-VaR/D-RISK-47 | VaR Cross-Validation Engine | design | planned |
| 42 | 风控域-VaR/D-RISK-71 | VaR Phase Independence Guarantor | design | planned |
| 43 | 风控域-VaR/D-RISK-73 | Monte Carlo Precision Level Manager | design | planned |
| 44 | 风控域-分析引擎/D-RISK-06 | Scenario Analyzer | design | planned |
| 45 | 风控域-分析引擎/D-RISK-103 | 风险预算调整器 | design | planned |
| 46 | 风控域-分析引擎/D-RISK-16 | Counterfactual Analyzer | design | planned |
| 47 | 风控域-回测/D-RISK-24 | Risk Policy Backtester | design | planned |
| 48 | 风控域-基础设施/D-RISK-121 | 风控域仓储接口 | design | planned |
| 49 | 风控域-基础设施/D-RISK-21 | Risk Rule DSL Compiler | design | planned |
| 50 | 风控域-基础设施/D-RISK-50 | Position Write Authority Arbiter | design | planned |
| 51 | 风控域-基础设施/D-RISK-56 | Rule Engine vs Statistical Engine Router | design | planned |
| 52 | 风控域-基础设施/D-RISK-77 | Risk Policy SQLite Schema Designer | design | planned |
| 53 | 风控域-契约/D-RISK-80 | CTR-006 PositionSnapshot Provider | design | planned |
| 54 | 风控域-契约/D-RISK-87 | CTR-004 Order Consumer | design | planned |
| 55 | 风控域-审计/D-RISK-15 | Risk Breach Logger | design | planned |
| 56 | 风控域-报告/D-RISK-23 | Risk Report Auto-Generator | design | planned |
| 57 | 风控域-止损/D-RISK-64 | ATR Dynamic Stop Loss Calculator | design | planned |
| 58 | 风控域-盘中监控/D-RISK-08 | Liquidity Risk Monitor | design | planned |
| 59 | 风控域-盘中监控/D-RISK-13 | Concentration Risk Monitor | design | planned |
| 60 | 风控域-盘中监控/D-RISK-18 | Crowding Risk Monitor | design | planned |
| 61 | 风控域-盘中监控/D-RISK-63 | Sector Concentration Real-Time Calcul... | design | planned |
| 62 | 风控域-盘中监控/D-RISK-70 | Enforcement 3-Level Executor | design | planned |
| 63 | 风控域-盘中监控/D-RISK-97 | 保证金比例安全检查器 | design | planned |
| 64 | 风控域-盘中监控/D-RISK-99 | 动态仓位调整器 | design | planned |
| 65 | 风控域-盘前拦截/D-RISK-53 | Pre-Trade Idempotency Guarantor | design | planned |
| 66 | 风控域-盘前拦截/D-RISK-78 | Pre-Trade 50ms SLA Monitor | design | planned |
| 67 | 风控域-规则引擎/D-RISK-105 | 风险规则用户配置器 | design | planned |
| 68 | 风控域-规则引擎/D-RISK-109 | 风控规则验证与压力测试器 | design | planned |
| 69 | 风控域-规则引擎/D-RISK-113 | 风控规则DSL引擎 | design | planned |
| 70 | 风控域-规则引擎/D-RISK-117 | 风控规则版本化与热更新器 | design | planned |
| 71 | 风控域-迁移/D-RISK-86 | DefaultRiskValidator to Configurable ... | design | planned |
| 72 | 风控域-远期❌/D-RISK-09 | Counterparty Risk Manager | design | planned |
| 73 | 风控域-远期❌/D-RISK-19 | Climate Risk Engine | design | planned |
| 74 | 风控域-远期❌/D-RISK-48 | Monte Carlo Batch Backtester | design | planned |
| 75 | 风控域-远期❌/D-RISK-95 | AI增强风控引擎 | design | planned |
| 76 | 风控域-门禁/D-RISK-92 | Strategy Correlation Gate Checker | design | planned |
| 77 | 风控域-预测/D-RISK-25 | Limit Consumption Predictor | design | planned |
| 78 | 风控域-风险报告/D-RISK-101 | 每日风险报告生成器 | design | planned |
| 79 | 风控域-风险报告/D-RISK-22 | Risk Dashboard Generator | design | planned |
| 80 | 风控域-风险报告/D-RISK-90 | RiskDashboardSnapshot CTR-P1-008 Builder | design | planned |
| 81 | 风控域-风险治理/D-RISK-49 | Risk Policy Persister | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 16 条 / 16 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 16 条 / 16 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 14 条 / edges                                │
│   [config_depends]: 2 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (14 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → risk_manager.py                                  │
│   __init__.py → risk_manager_base.py                             │
│   default_position_limit_ch... → risk_manager.py                 │
│   default_position_limit_ch... → risk_manager_base.py            │
│   default_stop_loss_engine.py → risk_manager_base.py             │
│   default_risk_manager_orch... → risk_manager.py                 │
│   default_risk_manager_orch... → risk_manager_base.py            │
│   default_risk_manager_orch... → default_position_limit_ch...    │
│   default_risk_manager_orch... → default_stop_loss_engine.py     │
│   default_risk_manager_orch... → default_risk_validator.py       │
│   default_risk_manager_orch... → default_risk_limits_calcu...    │
│   default_risk_validator.py → risk_manager.py                    │
│   default_risk_validator.py → risk_validator.py                  │
│   default_risk_limits_calcu... → risk_manager.py                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (2 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → ml_experiment_pipeline.py                        │
│   __init__.py → default_position_limit_ch...                     │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `47_d_risk_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
