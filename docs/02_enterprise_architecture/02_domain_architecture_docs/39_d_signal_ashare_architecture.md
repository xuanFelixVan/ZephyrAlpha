---
doc_type: domain_architecture_diagram
title: D-SIGNAL_ASHARE A股特色信号架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 39_d_signal_ashare / A股特色信号 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示A股特色信号（D-SIGNAL_ASHARE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 A股特色信号（D-SIGNAL_ASHARE）的模块分布。共 27 个模块 / 27 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (27 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/signal_ashare/__init__.py  [prototype]              │
│   src/zephyr/signal_ashare/_extensions/__init__.py  [scaffold... │
│   src/zephyr/signal_ashare/api/__init__.py  [scaffold_placeho... │
│   src/zephyr/signal_ashare/core/__init__.py  [scaffold_placeh... │
│   src/zephyr/signal_ashare/infrastructure/__init__.py  [scaff... │
│   src/zephyr/signal_ashare/models/__init__.py  [scaffold_plac... │
│   src/zephyr/signal_ashare/services/__init__.py  [scaffold_pl... │
│   A-Share Institutional Behavior Analyzer  [design]              │
│   A-Share Short-term Stock Selector  [design]                    │
│   A-Share Capital-Force Conflict Observer  [design]              │
│   A-Share Post-Buy Quick Diagnostician  [design]                 │
│   A-Share Decision Priority Engine  [design]                     │
│   A-Share Plan Conformity Evaluator  [design]                    │
│   A-Share Intraday Pattern Analyzer  [design]                    │
│   A-Share KDJ-MACD Multi-Period Screener  [design]               │
│   A-Share 4-Min Surge Anomaly Detector  [design]                 │
│   A-Share Market Phase Threshold Classifier  [design]            │
│   A-Share Contrarian Signal Sensitivity Configurator  [design]   │
│   ...还有 9 个模块 / 9 more modules                              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 27 个模块 / 27 modules）。

### L2 领域层 / Domain Layer (27 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/signal_ashare/__init__.py | src/zephyr/signal_ashare/__init__.py | prototype | orphan |
| 2 | src/zephyr/signal_ashare/_extensions/__init__.py | src/zephyr/signal_ashare/_extensions/... | scaffold_placeholder | orphan |
| 3 | src/zephyr/signal_ashare/api/__init__.py | src/zephyr/signal_ashare/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/signal_ashare/core/__init__.py | src/zephyr/signal_ashare/core/__init_... | scaffold_placeholder | orphan |
| 5 | src/zephyr/signal_ashare/infrastructure/__init__.py | src/zephyr/signal_ashare/infrastructu... | scaffold_placeholder | orphan |
| 6 | src/zephyr/signal_ashare/models/__init__.py | src/zephyr/signal_ashare/models/__ini... | scaffold_placeholder | orphan |
| 7 | src/zephyr/signal_ashare/services/__init__.py | src/zephyr/signal_ashare/services/__i... | scaffold_placeholder | orphan |
| 8 | 信号域-A股特色-主力资金/D-SIGNAL-21 | A-Share Institutional Behavior Analyzer | design | design_only |
| 9 | 信号域-A股特色-主力资金/D-SIGNAL-23 | A-Share Short-term Stock Selector | design | design_only |
| 10 | 信号域-A股特色-主力资金/D-SIGNAL-36 | A-Share Capital-Force Conflict Observer | design | design_only |
| 11 | 信号域-A股特色-买卖点/D-SIGNAL-47 | A-Share Post-Buy Quick Diagnostician | design | design_only |
| 12 | 信号域-A股特色-决策评估/D-SIGNAL-27 | A-Share Decision Priority Engine | design | design_only |
| 13 | 信号域-A股特色-决策评估/D-SIGNAL-45 | A-Share Plan Conformity Evaluator | design | design_only |
| 14 | 信号域-A股特色-分时技术/D-SIGNAL-29 | A-Share Intraday Pattern Analyzer | design | design_only |
| 15 | 信号域-A股特色-分时技术/D-SIGNAL-40 | A-Share KDJ-MACD Multi-Period Screener | design | design_only |
| 16 | 信号域-A股特色-分时技术/D-SIGNAL-51 | A-Share 4-Min Surge Anomaly Detector | design | design_only |
| 17 | 信号域-A股特色-大盘阶段/D-SIGNAL-31 | A-Share Market Phase Threshold Classi... | design | design_only |
| 18 | 信号域-A股特色-大盘阶段/D-SIGNAL-49 | A-Share Contrarian Signal Sensitivity... | design | design_only |
| 19 | 信号域-A股特色-情绪周期/D-SIGNAL-25 | A-Share Market Sentiment Analyzer | design | design_only |
| 20 | 信号域-A股特色-情绪周期/D-SIGNAL-33 | A-Share Youzi Relay Emotion Engine | design | design_only |
| 21 | 信号域-A股特色-板块轮动/D-SIGNAL-63 | A-Share Rotation Warning Signaler | design | design_only |
| 22 | 信号域-A股特色-涨停封单/D-SIGNAL-53 | A-Share Seal Order Level Jump Detector | design | design_only |
| 23 | 信号域-A股特色-特殊信号/D-SIGNAL-38 | A-Share Contrarian Capital 5-Day Tracker | design | design_only |
| 24 | 信号域-A股特色-特殊信号/D-SIGNAL-42 | A-Share Signal Post-Rise Filter | design | design_only |
| 25 | 信号域-A股特色-特殊信号/D-SIGNAL-55 | A-Share National Team Dual-Mode Ident... | design | design_only |
| 26 | 信号域-A股特色-特殊信号/D-SIGNAL-61 | A-Share Unexpected Strength/Weakness ... | design | design_only |
| 27 | 信号域-A股特色-量化双引擎/D-SIGNAL-57 | A-Share Dual-Engine 5-Type Decision M... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `39_d_signal_ashare_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
