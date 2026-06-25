---
doc_type: domain_architecture_diagram
title: D-ASHARE_SIGNAL A股特色信号架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 21_d_ashare_signal / A股特色信号 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示A股特色信号（D-ASHARE_SIGNAL）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 A股特色信号（D-ASHARE_SIGNAL）的模块分布。共 27 个模块 / 27 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (27 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/signal_ashare/__init__.py  [prototype]              │
│   src/zephyr/signal_ashare/_extensions/__init__.py  [prototype]  │
│   src/zephyr/signal_ashare/api/__init__.py  [prototype]          │
│   src/zephyr/signal_ashare/core/__init__.py  [prototype]         │
│   src/zephyr/signal_ashare/infrastructure/__init__.py  [proto... │
│   src/zephyr/signal_ashare/models/__init__.py  [prototype]       │
│   src/zephyr/signal_ashare/services/__init__.py  [prototype]     │
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
| 1 | src/zephyr/signal_ashare/__init__.py | src/zephyr/signal_ashare/__init__.py | prototype | deprecated |
| 2 | src/zephyr/signal_ashare/_extensions/__init__.py | src/zephyr/signal_ashare/_extensions/... | prototype | deprecated |
| 3 | src/zephyr/signal_ashare/api/__init__.py | src/zephyr/signal_ashare/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/signal_ashare/core/__init__.py | src/zephyr/signal_ashare/core/__init_... | prototype | deprecated |
| 5 | src/zephyr/signal_ashare/infrastructure/__init__.py | src/zephyr/signal_ashare/infrastructu... | prototype | deprecated |
| 6 | src/zephyr/signal_ashare/models/__init__.py | src/zephyr/signal_ashare/models/__ini... | prototype | deprecated |
| 7 | src/zephyr/signal_ashare/services/__init__.py | src/zephyr/signal_ashare/services/__i... | prototype | deprecated |
| 8 | 信号域-A股特色-主力资金/D-SIGNAL-21 | A-Share Institutional Behavior Analyzer | design | planned |
| 9 | 信号域-A股特色-主力资金/D-SIGNAL-23 | A-Share Short-term Stock Selector | design | planned |
| 10 | 信号域-A股特色-主力资金/D-SIGNAL-36 | A-Share Capital-Force Conflict Observer | design | planned |
| 11 | 信号域-A股特色-买卖点/D-SIGNAL-47 | A-Share Post-Buy Quick Diagnostician | design | planned |
| 12 | 信号域-A股特色-决策评估/D-SIGNAL-27 | A-Share Decision Priority Engine | design | planned |
| 13 | 信号域-A股特色-决策评估/D-SIGNAL-45 | A-Share Plan Conformity Evaluator | design | planned |
| 14 | 信号域-A股特色-分时技术/D-SIGNAL-29 | A-Share Intraday Pattern Analyzer | design | planned |
| 15 | 信号域-A股特色-分时技术/D-SIGNAL-40 | A-Share KDJ-MACD Multi-Period Screener | design | planned |
| 16 | 信号域-A股特色-分时技术/D-SIGNAL-51 | A-Share 4-Min Surge Anomaly Detector | design | planned |
| 17 | 信号域-A股特色-大盘阶段/D-SIGNAL-31 | A-Share Market Phase Threshold Classi... | design | planned |
| 18 | 信号域-A股特色-大盘阶段/D-SIGNAL-49 | A-Share Contrarian Signal Sensitivity... | design | planned |
| 19 | 信号域-A股特色-情绪周期/D-SIGNAL-25 | A-Share Market Sentiment Analyzer | design | planned |
| 20 | 信号域-A股特色-情绪周期/D-SIGNAL-33 | A-Share Youzi Relay Emotion Engine | design | planned |
| 21 | 信号域-A股特色-板块轮动/D-SIGNAL-63 | A-Share Rotation Warning Signaler | design | planned |
| 22 | 信号域-A股特色-涨停封单/D-SIGNAL-53 | A-Share Seal Order Level Jump Detector | design | planned |
| 23 | 信号域-A股特色-特殊信号/D-SIGNAL-38 | A-Share Contrarian Capital 5-Day Tracker | design | planned |
| 24 | 信号域-A股特色-特殊信号/D-SIGNAL-42 | A-Share Signal Post-Rise Filter | design | planned |
| 25 | 信号域-A股特色-特殊信号/D-SIGNAL-55 | A-Share National Team Dual-Mode Ident... | design | planned |
| 26 | 信号域-A股特色-特殊信号/D-SIGNAL-61 | A-Share Unexpected Strength/Weakness ... | design | planned |
| 27 | 信号域-A股特色-量化双引擎/D-SIGNAL-57 | A-Share Dual-Engine 5-Type Decision M... | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `21_d_ashare_signal_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
