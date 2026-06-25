---
doc_type: domain_architecture_diagram
title: D-PF_CORE 组合核心架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 45_d_pf_core / 组合核心 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示组合核心（D-PF_CORE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 组合核心（D-PF_CORE）的模块分布。共 48 个模块 / 48 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (48 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   A-001  [design]                                                │
│   MS-02  [design]                                                │
│   MT-02  [design]                                                │
│   MS-04  [design]                                                │
│   MT-03  [design]                                                │
│   MS-03  [design]                                                │
│   MS-05  [design]                                                │
│   MT-05  [design]                                                │
│   MT-04  [design]                                                │
│   D-ALT-DATA-03  [design]                                        │
│   D-ALT-DATA-11  [design]                                        │
│   D-ALT-DATA-06  [design]                                        │
│   D-ALT-DATA-07  [design]                                        │
│   D-ALT-DATA-09  [design]                                        │
│   D-ALT-DATA-10  [design]                                        │
│   D-ALT-DATA-13  [design]                                        │
│   D-ALT-DATA-15  [design]                                        │
│   D-ALT-DATA-17  [design]                                        │
│   ...还有 30 个模块 / 30 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 48 个模块 / 48 modules）。

### L2 领域层 / Domain Layer (48 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 |  | A-001 | design | stable |
| 2 |  | MS-02 | design | generated |
| 3 |  | MT-02 | design | generated |
| 4 |  | MS-04 | design | generated |
| 5 |  | MT-03 | design | generated |
| 6 |  | MS-03 | design | generated |
| 7 |  | MS-05 | design | generated |
| 8 |  | MT-05 | design | generated |
| 9 |  | MT-04 | design | generated |
| 10 |  | D-ALT-DATA-03 | design | generated |
| 11 |  | D-ALT-DATA-11 | design | generated |
| 12 |  | D-ALT-DATA-06 | design | generated |
| 13 |  | D-ALT-DATA-07 | design | generated |
| 14 |  | D-ALT-DATA-09 | design | generated |
| 15 |  | D-ALT-DATA-10 | design | generated |
| 16 |  | D-ALT-DATA-13 | design | generated |
| 17 |  | D-ALT-DATA-15 | design | generated |
| 18 |  | D-ALT-DATA-17 | design | generated |
| 19 |  | D-ALT-DATA-06扩展 | design | generated |
| 20 |  | D-ALT-DATA-14 | design | generated |
| 21 |  | D-CROSS-ASSET-03 | design | generated |
| 22 |  | D-CROSS-ASSET-13 | design | generated |
| 23 |  | AP-07 | design | generated |
| 24 |  | AP-09 | design | generated |
| 25 |  | RK-10 | design | generated |
| 26 |  | PA-01 | design | generated |
| 27 | src/zephyr/pf_core/__init__.py | src/zephyr/pf_core/__init__.py | prototype | generated |
| 28 | src/zephyr/pf_core/_extensions/__init__.py | src/zephyr/pf_core/_extensions/__init... | prototype | deprecated |
| 29 | src/zephyr/pf_core/analytics_base.py | src/zephyr/pf_core/analytics_base.py | production | generated |
| 30 | src/zephyr/pf_core/api/__init__.py | src/zephyr/pf_core/api/__init__.py | prototype | deprecated |
| 31 | src/zephyr/pf_core/compliance_rule.py | src/zephyr/pf_core/compliance_rule.py | production | generated |
| 32 | src/zephyr/pf_core/core/__init__.py | src/zephyr/pf_core/core/__init__.py | prototype | deprecated |
| 33 | src/zephyr/pf_core/default_attribution_engine.py | src/zephyr/pf_core/default_attributio... | production | generated |
| 34 | src/zephyr/pf_core/default_tca_engine.py | src/zephyr/pf_core/default_tca_engine.py | production | generated |
| 35 | src/zephyr/pf_core/infrastructure/__init__.py | src/zephyr/pf_core/infrastructure/__i... | prototype | deprecated |
| 36 | src/zephyr/pf_core/performance_attribution_engine/__init_... | src/zephyr/pf_core/performance_attrib... | prototype | generated |
| 37 | src/zephyr/pf_core/performance_attribution_report.py | src/zephyr/pf_core/performance_attrib... | production | generated |
| 38 | src/zephyr/pf_core/risk_limits.py | src/zephyr/pf_core/risk_limits.py | prototype | generated |
| 39 | src/zephyr/pf_core/services/__init__.py | src/zephyr/pf_core/services/__init__.py | prototype | deprecated |
| 40 | src/zephyr/pf_core/strategies/__init__.py | src/zephyr/pf_core/strategies/__init_... | prototype | generated |
| 41 | src/zephyr/pf_core/strategies/default_equity_strategy.py | src/zephyr/pf_core/strategies/default... | prototype | generated |
| 42 | src/zephyr/pf_core/strategy_base.py | src/zephyr/pf_core/strategy_base.py | production | generated |
| 43 | src/zephyr/pf_core/strategy_engine/__init__.py | src/zephyr/pf_core/strategy_engine/__... | prototype | generated |
| 44 | src/zephyr/pf_core/strategy_registry.py | src/zephyr/pf_core/strategy_registry.py | prototype | generated |
| 45 | 另类数据域缩写，D-ALT-02=SentimentEngine | D-ALT-DATA-02 | design | planned |
| 46 | 推理域缩写，D-ML-02=ModelRegistry→归入MS-01 | MS-01 | design | planned |
| 47 | 训练域缩写，D-ML-01=TrainingPipeline→归入MT-01 | MT-01 | design | planned |
| 48 | 跨资产域缩写，D-XA=D-CROSS-ASSET(CA) | D-CROSS-ASSET-01 | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `45_d_pf_core_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
