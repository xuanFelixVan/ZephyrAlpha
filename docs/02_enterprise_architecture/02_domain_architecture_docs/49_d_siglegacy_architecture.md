---
doc_type: architecture_view
title: D-SIGLEGACY 信号遗留设计态架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 49_d_siglegacy / 信号遗留设计态 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示信号遗留设计态（D-SIGLEGACY）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:21
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 信号遗留设计态（D-SIGLEGACY）的模块分布。共 45 个模块 / 45 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (45 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   信号域仓储接口  [design]                                       │
│   策略框架升级迁移适配器  [design]                               │
│   Regime Sample Size Adequacy Checker  [design]                  │
│   Regime Signal Contextualizer  [design]                         │
│   Regime Failure Mode Diagnoser  [design]                        │
│   Regime Macro Indicator Driver  [design]                        │
│   Strategy Shared Kernel Synchronizer  [design]                  │
│   Strategy Historical Performance Data Provider  [design]        │
│   Risk Event E-RK-01 Consumer Handler  [design]                  │
│   策略引擎信号聚合  [design]                                     │
│   Capital Allocation Constraint Validator  [design]              │
│   Regime-Aware Market State Adaptive Synthesizer  [design]       │
│   ML Weight Synthesis Strategist  [design]                       │
│   SynthesizedSignal Event Publisher  [design]                    │
│   Sharpe Ratio Allocation Strategist  [design]                   │
│   CTR-TRACE-001 TraceContext传播器  [design]                     │
│   因子计算结果消费桥接器  [design]                               │
│   Signal Audit Logger  [design]                                  │
│   ...还有 27 个模块 / 27 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 45 个模块 / 45 modules）。

### L2 领域层 / Domain Layer (45 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 信号域-DDD契约/D-SIGNAL-160 | 信号域仓储接口 | design | planned |
| 2 | 信号域-DDD契约/D-SIGNAL-162 | 策略框架升级迁移适配器 | design | planned |
| 3 | 信号域-Regime/D-SIGNAL-65 | Regime Sample Size Adequacy Checker | design | planned |
| 4 | 信号域-Regime/D-SIGNAL-67 | Regime Signal Contextualizer | design | planned |
| 5 | 信号域-Regime/D-SIGNAL-74 | Regime Failure Mode Diagnoser | design | planned |
| 6 | 信号域-Regime/D-SIGNAL-76 | Regime Macro Indicator Driver | design | planned |
| 7 | 信号域-事件追踪/D-SIGNAL-101 | Strategy Shared Kernel Synchronizer | design | planned |
| 8 | 信号域-事件追踪/D-SIGNAL-103 | Strategy Historical Performance Data ... | design | planned |
| 9 | 信号域-事件追踪/D-SIGNAL-99 | Risk Event E-RK-01 Consumer Handler | design | planned |
| 10 | 信号域-冲突融合/D-SIGNAL-134 | 策略引擎信号聚合 | design | planned |
| 11 | 信号域-合成分配/D-SIGNAL-85 | Capital Allocation Constraint Validator | design | planned |
| 12 | 信号域-合成分配/D-SIGNAL-87 | Regime-Aware Market State Adaptive Sy... | design | planned |
| 13 | 信号域-合成分配/D-SIGNAL-90 | ML Weight Synthesis Strategist | design | planned |
| 14 | 信号域-合成分配/D-SIGNAL-94 | SynthesizedSignal Event Publisher | design | planned |
| 15 | 信号域-合成分配/D-SIGNAL-96 | Sharpe Ratio Allocation Strategist | design | planned |
| 16 | 信号域-契约/D-SIGNAL-100 | CTR-TRACE-001 TraceContext传播器 | design | planned |
| 17 | 信号域-契约/D-SIGNAL-158 | 因子计算结果消费桥接器 | design | planned |
| 18 | 信号域-审计/D-SIGNAL-06 | Signal Audit Logger | design | planned |
| 19 | 信号域-技术指标/D-SIGNAL-114 | 技术指标信号生成器 | design | planned |
| 20 | 信号域-技术指标/D-SIGNAL-116 | 策略逻辑流程图生成器 | design | planned |
| 21 | 信号域-技术指标/D-SIGNAL-120 | 统一策略接口定义器 | design | planned |
| 22 | 信号域-技术指标/D-SIGNAL-122 | TA-Lib技术指标信号计算器 | design | planned |
| 23 | 信号域-技术指标/D-SIGNAL-124 | 图形形态识别算法库 | design | planned |
| 24 | 信号域-技术指标/D-SIGNAL-126 | 蜡烛图模式识别器 | design | planned |
| 25 | 信号域-技术指标/D-SIGNAL-128 | 缺口形态识别器 | design | planned |
| 26 | 信号域-核心基础设施/D-SIGNAL-12 | Signal Version Manager | design | planned |
| 27 | 信号域-核心基础设施/D-SIGNAL-14 | Strategy Lifecycle Manager | design | planned |
| 28 | 信号域-核心基础设施/D-SIGNAL-16 | Signal Conflict Resolution Engine | design | planned |
| 29 | 信号域-核心基础设施/D-SIGNAL-18 | Signal Out-of-Sample Validator | design | planned |
| 30 | 信号域-策略发布/D-SIGNAL-140 | 策略灰度发布 | design | planned |
| 31 | 信号域-策略可视化/D-SIGNAL-105 | 代码生成流程编排器 | design | planned |
| 32 | 信号域-策略可视化/D-SIGNAL-107 | 画布拖拽连线引擎 | design | planned |
| 33 | 信号域-策略可视化/D-SIGNAL-109 | 策略流程图编辑器 | design | planned |
| 34 | 信号域-策略可视化/D-SIGNAL-111 | 策略可解释性引擎 | design | planned |
| 35 | 信号域-策略管理/D-SIGNAL-137 | 策略生命周期管理 | design | planned |
| 36 | 信号域-策略管理/D-SIGNAL-139 | 策略状态持久化 | design | planned |
| 37 | 信号域-策略管理/D-SIGNAL-141 | 策略模板版本管理 | design | planned |
| 38 | 信号域-策略管理/D-SIGNAL-143 | 策略生命周期钩子 | design | planned |
| 39 | 信号域-策略质量/D-SIGNAL-145 | 风格轮动检测器 | design | planned |
| 40 | 信号域-策略质量/D-SIGNAL-147 | 策略归因分析器 | design | planned |
| 41 | 信号域-策略运行时/D-SIGNAL-150 | 策略异常退出处理 | design | planned |
| 42 | 信号域-策略运行时/D-SIGNAL-152 | 策略基类接口兼容性版本化器 | design | planned |
| 43 | 信号域-质量降级/D-SIGNAL-79 | Factor Decay Linkage Degradation Handler | design | planned |
| 44 | 信号域-降级/D-SIGNAL-80 | Degradation Notification Downstream M... | design | planned |
| 45 | 信号域/D-SIGNAL-20 | Signal Tail Risk Protector | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `49_d_siglegacy_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
