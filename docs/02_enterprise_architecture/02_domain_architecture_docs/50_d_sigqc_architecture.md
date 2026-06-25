---
doc_type: domain_architecture_diagram
title: D-SIGQC 信号质量控制架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 50_d_sigqc / 信号质量控制 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示信号质量控制（D-SIGQC）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:21
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 信号质量控制（D-SIGQC）的模块分布。共 17 个模块 / 17 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (17 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/signal_quality/__init__.py  [prototype]             │
│   src/zephyr/signal_quality/_extensions/__init__.py  [prototype] │
│   src/zephyr/signal_quality/api/__init__.py  [prototype]         │
│   src/zephyr/signal_quality/core/__init__.py  [prototype]        │
│   src/zephyr/signal_quality/infrastructure/__init__.py  [prot... │
│   src/zephyr/signal_quality/models/__init__.py  [prototype]      │
│   src/zephyr/signal_quality/services/__init__.py  [prototype]    │
│   Signal Normalizer  [design]                                    │
│   Signal TTL Timeout Manager  [design]                           │
│   信号去重模块  [design]                                         │
│   信号冲突解决  [design]                                         │
│   Signal Revocation Executor  [design]                           │
│   实时模式检测与信号质量评估器  [design]                         │
│   信号质量退化监控  [design]                                     │
│   Factor Coverage Rate Calculator  [design]                      │
│   Empty Signal NEUTRAL Strategy Manager  [design]                │
│   Signal Expired Unconsumed Detector  [design]                   │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 17 个模块 / 17 modules）。

### L2 领域层 / Domain Layer (17 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/signal_quality/__init__.py | src/zephyr/signal_quality/__init__.py | prototype | deprecated |
| 2 | src/zephyr/signal_quality/_extensions/__init__.py | src/zephyr/signal_quality/_extensions... | prototype | deprecated |
| 3 | src/zephyr/signal_quality/api/__init__.py | src/zephyr/signal_quality/api/__init_... | prototype | deprecated |
| 4 | src/zephyr/signal_quality/core/__init__.py | src/zephyr/signal_quality/core/__init... | prototype | deprecated |
| 5 | src/zephyr/signal_quality/infrastructure/__init__.py | src/zephyr/signal_quality/infrastruct... | prototype | deprecated |
| 6 | src/zephyr/signal_quality/models/__init__.py | src/zephyr/signal_quality/models/__in... | prototype | deprecated |
| 7 | src/zephyr/signal_quality/services/__init__.py | src/zephyr/signal_quality/services/__... | prototype | deprecated |
| 8 | 信号域-信号处理/D-SIGNAL-69 | Signal Normalizer | design | planned |
| 9 | 信号域-信号处理/D-SIGNAL-71 | Signal TTL Timeout Manager | design | planned |
| 10 | 信号域-冲突融合/D-SIGNAL-130 | 信号去重模块 | design | planned |
| 11 | 信号域-冲突融合/D-SIGNAL-132 | 信号冲突解决 | design | planned |
| 12 | 信号域-合成分配/D-SIGNAL-92 | Signal Revocation Executor | design | planned |
| 13 | 信号域-技术指标/D-SIGNAL-118 | 实时模式检测与信号质量评估器 | design | planned |
| 14 | 信号域-策略运行时/D-SIGNAL-156 | 信号质量退化监控 | design | planned |
| 15 | 信号域-质量降级/D-SIGNAL-77 | Factor Coverage Rate Calculator | design | planned |
| 16 | 信号域-质量降级/D-SIGNAL-81 | Empty Signal NEUTRAL Strategy Manager | design | planned |
| 17 | 信号域-质量降级/D-SIGNAL-83 | Signal Expired Unconsumed Detector | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `50_d_sigqc_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
