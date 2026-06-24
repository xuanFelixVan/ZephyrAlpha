---
doc_type: domain_architecture_diagram
title: D-FRONTEND 前端架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 10_d_frontend / 前端 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示前端（D-FRONTEND）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 前端（D-FRONTEND）的模块分布。共 237 个模块 / 237 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│         L0 基础设施层 / Infrastructure Layer (8 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   frontend/app.py  [prototype]                                   │
│   frontend/fitness_functions.py  [prototype]                     │
│   frontend/gate_statistics.py  [prototype]                       │
│   frontend/interface_base.py  [prototype]                        │
│   frontend/knowledge_overview.py  [prototype]                    │
│   frontend/olap_trend.py  [prototype]                            │
│   frontend/real_time_dashboard/__init__.py  [prototype]          │
│   frontend/task_progress.py  [prototype]                         │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (16 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/frontend/__init__.py  [prototype]                   │
│   src/zephyr/frontend/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/frontend/api/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/frontend/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/frontend/dashboard/__init__.py  [prototype]         │
│   src/zephyr/frontend/dashboard/app.py  [production]             │
│   src/zephyr/frontend/dashboard/components/__init__.py  [prot... │
│   src/zephyr/frontend/dashboard/components/fitness_functions.... │
│   src/zephyr/frontend/dashboard/components/gate_statistics.py... │
│   src/zephyr/frontend/dashboard/components/knowledge_overview... │
│   src/zephyr/frontend/dashboard/components/olap_trend.py  [pr... │
│   src/zephyr/frontend/dashboard/components/task_progress.py  ... │
│   src/zephyr/frontend/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/frontend/interface_base.py  [production]            │
│   src/zephyr/frontend/models/__init__.py  [scaffold_placeholder] │
│   src/zephyr/frontend/services/__init__.py  [scaffold_placeho... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L3 应用层 / Application Layer (10 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   Report Visualization  [design]                                 │
│   Alert Visualization  [design]                                  │
│   Custom Chart Builder  [design]                                 │
│   Approval Workflow UI  [design]                                 │
│   Mobile Dashboard  [design]                                     │
│   Collaborative Workspace  [design]                              │
│   Trading Chatbot  [design]                                      │
│   One-Click Quant Interface  [design]                            │
│   API Gateway Proxy  [design]                                    │
│   Feishu Bot  [design]                                           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (203 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   3D Force-Directed Layout 3D力导向布局器  [design]              │
│   4-Level Risk Decision 4级风控决策  [design]                    │
│   AI Agent调用链追踪器 AI Agent Call Chain Tracer  [design]      │
│   AI Autonomy Dashboard AI自治仪表盘  [design]                   │
│   AI Collection Result Display AI采集结果展示  [design]          │
│   AI Model HR Dashboard AI模型HR管理面板  [design]               │
│   AI Role AI角色  [design]                                       │
│   AI-Driven Dependency Explorer AI驱动依赖图探索器  [design]     │
│   API Dependency Visualizer API依赖可视化器  [design]            │
│   API Gateway Proxy API网关代理  [design]                        │
│   API Gateway UI API网关界面  [design]                           │
│   AST Sandbox Validation Result AST沙箱验证结果  [design]        │
│   Administrator Role 管理员角色  [design]                        │
│   Adversarial Test Result 对抗性测试结果  [design]               │
│   Agent Behavior Monitoring Agent行为监控  [design]              │
│   Agent Dependency Heatmap Agent依赖热力图  [design]             │
│   Alert Notification UI 告警通知界面  [design]                   │
│   Alert Output Alert产出  [design]                               │
│   ...还有 185 个模块 / 185 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 237 个模块 / 237 modules）。

### L0 基础设施层 / Infrastructure Layer (8 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | frontend/app.py | frontend/app.py | prototype | draft |
| 2 | frontend/fitness_functions.py | frontend/fitness_functions.py | prototype | draft |
| 3 | frontend/gate_statistics.py | frontend/gate_statistics.py | prototype | draft |
| 4 | frontend/interface_base.py | frontend/interface_base.py | prototype | draft |
| 5 | frontend/knowledge_overview.py | frontend/knowledge_overview.py | prototype | draft |
| 6 | frontend/olap_trend.py | frontend/olap_trend.py | prototype | draft |
| 7 | frontend/real_time_dashboard/__init__.py | frontend/real_time_dashboard/__init__.py | prototype | orphan |
| 8 | frontend/task_progress.py | frontend/task_progress.py | prototype | draft |

### L1 基础层 / Foundation Layer (16 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/frontend/__init__.py | src/zephyr/frontend/__init__.py | prototype | draft |
| 2 | src/zephyr/frontend/_extensions/__init__.py | src/zephyr/frontend/_extensions/__ini... | scaffold_placeholder | orphan |
| 3 | src/zephyr/frontend/api/__init__.py | src/zephyr/frontend/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/frontend/core/__init__.py | src/zephyr/frontend/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/frontend/dashboard/__init__.py | src/zephyr/frontend/dashboard/__init_... | prototype | draft |
| 6 | src/zephyr/frontend/dashboard/app.py | src/zephyr/frontend/dashboard/app.py | production | draft |
| 7 | src/zephyr/frontend/dashboard/components/__init__.py | src/zephyr/frontend/dashboard/compone... | prototype | draft |
| 8 | src/zephyr/frontend/dashboard/components/fitness_function... | src/zephyr/frontend/dashboard/compone... | production | draft |
| 9 | src/zephyr/frontend/dashboard/components/gate_statistics.py | src/zephyr/frontend/dashboard/compone... | production | draft |
| 10 | src/zephyr/frontend/dashboard/components/knowledge_overvi... | src/zephyr/frontend/dashboard/compone... | production | draft |
| 11 | src/zephyr/frontend/dashboard/components/olap_trend.py | src/zephyr/frontend/dashboard/compone... | production | draft |
| 12 | src/zephyr/frontend/dashboard/components/task_progress.py | src/zephyr/frontend/dashboard/compone... | production | draft |
| 13 | src/zephyr/frontend/infrastructure/__init__.py | src/zephyr/frontend/infrastructure/__... | scaffold_placeholder | orphan |
| 14 | src/zephyr/frontend/interface_base.py | src/zephyr/frontend/interface_base.py | production | draft |
| 15 | src/zephyr/frontend/models/__init__.py | src/zephyr/frontend/models/__init__.py | scaffold_placeholder | orphan |
| 16 | src/zephyr/frontend/services/__init__.py | src/zephyr/frontend/services/__init__.py | scaffold_placeholder | orphan |

### L3 应用层 / Application Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 前端域/D-FRONTEND-06 | Report Visualization | design | design_only |
| 2 | 前端域/D-FRONTEND-08 | Alert Visualization | design | design_only |
| 3 | 前端域/D-FRONTEND-10 | Custom Chart Builder | design | design_only |
| 4 | 前端域/D-FRONTEND-12 | Approval Workflow UI | design | design_only |
| 5 | 前端域/D-FRONTEND-14 | Mobile Dashboard | design | design_only |
| 6 | 前端域/D-FRONTEND-16 | Collaborative Workspace | design | design_only |
| 7 | 前端域/D-FRONTEND-18 | Trading Chatbot | design | design_only |
| 8 | 前端域/D-FRONTEND-20 | One-Click Quant Interface | design | design_only |
| 9 | 前端域/D-FRONTEND-22 | API Gateway Proxy | design | design_only |
| 10 | 前端域/D-FRONTEND-24 | Feishu Bot | design | design_only |

### 未分类 / Unclassified (203 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-FRONTEND/3D Force-Directed Layout 3D力导向布局器 | 3D Force-Directed Layout 3D力导向布局器 | design | design_only |
| 2 | D-FRONTEND/4-Level Risk Decision 4级风控决策 | 4-Level Risk Decision 4级风控决策 | design | design_only |
| 3 | D-FRONTEND/AI Agent调用链追踪器 AI Agent Call Chain Tracer | AI Agent调用链追踪器 AI Agent Call Ch... | design | design_only |
| 4 | D-FRONTEND/AI Autonomy Dashboard AI自治仪表盘 | AI Autonomy Dashboard AI自治仪表盘 | design | design_only |
| 5 | D-FRONTEND/AI Collection Result Display AI采集结果展示 | AI Collection Result Display AI采集结... | design | design_only |
| 6 | D-FRONTEND/AI Model HR Dashboard AI模型HR管理面板 | AI Model HR Dashboard AI模型HR管理面板 | design | design_only |
| 7 | D-FRONTEND/AI Role AI角色 | AI Role AI角色 | design | design_only |
| 8 | D-FRONTEND/AI-Driven Dependency Explorer AI驱动依赖图探索器 | AI-Driven Dependency Explorer AI驱动... | design | design_only |
| 9 | D-FRONTEND/API Dependency Visualizer API依赖可视化器 | API Dependency Visualizer API依赖可视... | design | design_only |
| 10 | D-FRONTEND/API Gateway Proxy API网关代理 | API Gateway Proxy API网关代理 | design | design_only |
| 11 | D-FRONTEND/API Gateway UI API网关界面 | API Gateway UI API网关界面 | design | design_only |
| 12 | D-FRONTEND/AST Sandbox Validation Result AST沙箱验证结果 | AST Sandbox Validation Result AST沙箱... | design | design_only |
| 13 | D-FRONTEND/Administrator Role 管理员角色 | Administrator Role 管理员角色 | design | design_only |
| 14 | D-FRONTEND/Adversarial Test Result 对抗性测试结果 | Adversarial Test Result 对抗性测试结果 | design | design_only |
| 15 | D-FRONTEND/Agent Behavior Monitoring Agent行为监控 | Agent Behavior Monitoring Agent行为监控 | design | design_only |
| 16 | D-FRONTEND/Agent Dependency Heatmap Agent依赖热力图 | Agent Dependency Heatmap Agent依赖热力图 | design | design_only |
| 17 | D-FRONTEND/Alert Notification UI 告警通知界面 | Alert Notification UI 告警通知界面 | design | design_only |
| 18 | D-FRONTEND/Alert Output Alert产出 | Alert Output Alert产出 | design | design_only |
| 19 | D-FRONTEND/AlertTriggered 告警已触发 | AlertTriggered 告警已触发 | design | design_only |
| 20 | D-FRONTEND/AlertVisualization 告警可视化 | AlertVisualization 告警可视化 | design | design_only |
| 21 | D-FRONTEND/Anomaly Propagation 3D Visualizer 异常传播3D可... | Anomaly Propagation 3D Visualizer 异... | design | design_only |
| 22 | D-FRONTEND/Approval Interface Security 审批界面安全约束 | Approval Interface Security 审批界面... | design | design_only |
| 23 | D-FRONTEND/Approval Workflow UI 审批流程界面 | Approval Workflow UI 审批流程界面 | design | design_only |
| 24 | D-FRONTEND/ApprovalRequest Output ApprovalRequest产出 | ApprovalRequest Output ApprovalReques... | design | design_only |
| 25 | D-FRONTEND/ApprovalRequested 审批已请求 | ApprovalRequested 审批已请求 | design | design_only |
| 26 | D-FRONTEND/ApprovalWorkflowUI 审批工作流UI | ApprovalWorkflowUI 审批工作流UI | design | design_only |
| 27 | D-FRONTEND/Architecture Doc Auto-Generator 架构文档自动生... | Architecture Doc Auto-Generator 架构... | design | design_only |
| 28 | D-FRONTEND/Auto-Layout Optimizer 自动布局优化器 | Auto-Layout Optimizer 自动布局优化器 | design | design_only |
| 29 | D-FRONTEND/Backtest Result Summary 回测结果摘要 | Backtest Result Summary 回测结果摘要 | design | design_only |
| 30 | D-FRONTEND/BacktestPassed 回测已通过 | BacktestPassed 回测已通过 | design | design_only |
| 31 | D-FRONTEND/CLI Interface 命令行交互入口 | CLI Interface 命令行交互入口 | design | design_only |
| 32 | D-FRONTEND/CQRS Visualization CQRS可视化器 | CQRS Visualization CQRS可视化器 | design | design_only |
| 33 | D-FRONTEND/CVaR Conditional VaR 条件风险价值 | CVaR Conditional VaR 条件风险价值 | design | design_only |
| 34 | D-FRONTEND/Call Graph Visualizer 调用图可视化器 | Call Graph Visualizer 调用图可视化器 | design | design_only |
| 35 | D-FRONTEND/Capacity Dashboard 容量仪表盘 | Capacity Dashboard 容量仪表盘 | design | design_only |
| 36 | D-FRONTEND/Chart Engine 图表引擎 | Chart Engine 图表引擎 | design | design_only |
| 37 | D-FRONTEND/Cluster Heatmap 集群热力图 | Cluster Heatmap 集群热力图 | design | design_only |
| 38 | D-FRONTEND/Code Comparison View 代码对比视图 | Code Comparison View 代码对比视图 | design | design_only |
| 39 | D-FRONTEND/Code Review Panel 代码审查面板 | Code Review Panel 代码审查面板 | design | design_only |
| 40 | D-FRONTEND/Collaboration Annotation 协作批注 | Collaboration Annotation 协作批注 | design | design_only |
| 41 | D-FRONTEND/Collaboration Annotation 报告协作批注 | Collaboration Annotation 报告协作批注 | design | design_only |
| 42 | D-FRONTEND/Collaboration Watermark 协作平台水印 | Collaboration Watermark 协作平台水印 | design | design_only |
| 43 | D-FRONTEND/Collaboration Watermark 协作版报告水印 | Collaboration Watermark 协作版报告水印 | design | design_only |
| 44 | D-FRONTEND/Collaborative Dependency Annotator 协作依赖图... | Collaborative Dependency Annotator 协... | design | design_only |
| 45 | D-FRONTEND/Collaborative Workspace 协作工作区 | Collaborative Workspace 协作工作区 | design | design_only |
| 46 | D-FRONTEND/Collection Progress Tracking 采集进度追踪 | Collection Progress Tracking 采集进度... | design | design_only |
| 47 | D-FRONTEND/Collection Strategy Adjustment Log 采集策略调... | Collection Strategy Adjustment Log 采... | design | design_only |
| 48 | D-FRONTEND/Conformal VaR 共形VaR | Conformal VaR 共形VaR | design | design_only |
| 49 | D-FRONTEND/Convergence Status Indicator 收敛状态指示 | Convergence Status Indicator 收敛状态... | design | design_only |
| 50 | D-FRONTEND/Coupling Heatmap 耦合热力图 | Coupling Heatmap 耦合热力图 | design | design_only |
| 51 | D-FRONTEND/Critic Criticism Display Critic批评展示 | Critic Criticism Display Critic批评展示 | design | design_only |
| 52 | D-FRONTEND/Critic 批评器 | Critic 批评器 | design | design_only |
| 53 | D-FRONTEND/Cross-Service Trace Correlator 跨服务Trace关联器 | Cross-Service Trace Correlator 跨服务... | design | design_only |
| 54 | D-FRONTEND/Custom Chart Builder 自定义图表 | Custom Chart Builder 自定义图表 | design | design_only |
| 55 | D-FRONTEND/D-FRONTEND 前端 | D-FRONTEND 前端 | design | design_only |
| 56 | D-FRONTEND/D-PORTFOLIO Domain 组合域 | D-PORTFOLIO Domain 组合域 | design | design_only |
| 57 | D-FRONTEND/Daily Risk Report 日度风险报告 | Daily Risk Report 日度风险报告 | design | design_only |
| 58 | D-FRONTEND/Daily Risk Summary 日度风险摘要 | Daily Risk Summary 日度风险摘要 | design | design_only |
| 59 | D-FRONTEND/Dashboard Framework 仪表盘框架 | Dashboard Framework 仪表盘框架 | design | design_only |
| 60 | D-FRONTEND/Dashboard Output Dashboard产出 | Dashboard Output Dashboard产出 | design | design_only |
| 61 | D-FRONTEND/Dashboard 仪表盘 | Dashboard 仪表盘 | design | design_only |
| 62 | D-FRONTEND/DashboardUpdated 仪表盘已更新 | DashboardUpdated 仪表盘已更新 | design | design_only |
| 63 | D-FRONTEND/Decision Gate Progress 决策门控进度 | Decision Gate Progress 决策门控进度 | design | design_only |
| 64 | D-FRONTEND/Decision Gate State Machine 决策门控状态机 | Decision Gate State Machine 决策门控... | design | design_only |
| 65 | D-FRONTEND/Decision Tree Visualizer 决策树可视化器 | Decision Tree Visualizer 决策树可视化器 | design | design_only |
| 66 | D-FRONTEND/Degradation Status Dashboard 降级状态仪表盘 | Degradation Status Dashboard 降级状态... | design | design_only |
| 67 | D-FRONTEND/Density-Aware VaR 密度感知VaR | Density-Aware VaR 密度感知VaR | design | design_only |
| 68 | D-FRONTEND/Dependency Diff Viewer 依赖图差异查看器 | Dependency Diff Viewer 依赖图差异查看器 | design | design_only |
| 69 | D-FRONTEND/Dependency Graph LOD Engine 依赖图LOD引擎 | Dependency Graph LOD Engine 依赖图LOD... | design | design_only |
| 70 | D-FRONTEND/Dependency Timeline Player 依赖图时间线播放器 | Dependency Timeline Player 依赖图时间... | design | design_only |
| 71 | D-FRONTEND/Developer Dashboard 开发者仪表盘 | Developer Dashboard 开发者仪表盘 | design | design_only |
| 72 | D-FRONTEND/Drift Detection Status Panel 漂移检测状态面板 | Drift Detection Status Panel 漂移检测... | design | design_only |
| 73 | D-FRONTEND/E-SIM-04 BacktestPassed 回测通过 | E-SIM-04 BacktestPassed 回测通过 | design | design_only |
| 74 | D-FRONTEND/Effect Evaluation Report 效果评估报告 | Effect Evaluation Report 效果评估报告 | design | design_only |
| 75 | D-FRONTEND/Effect Metric Trend 效果指标趋势 | Effect Metric Trend 效果指标趋势 | design | design_only |
| 76 | D-FRONTEND/Email SMTP 邮件SMTP | Email SMTP 邮件SMTP | design | design_only |
| 77 | D-FRONTEND/End-to-End Trace Visualizer 端到端追踪可视化 | End-to-End Trace Visualizer 端到端追... | design | design_only |
| 78 | D-FRONTEND/EndToEndTraceVisualizer 端到端追踪可视化 | EndToEndTraceVisualizer 端到端追踪可视化 | design | design_only |
| 79 | D-FRONTEND/Endpoint Refiner 端点级细化器 | Endpoint Refiner 端点级细化器 | design | design_only |
| 80 | D-FRONTEND/EscalationTriggered 升级已触发 | EscalationTriggered 升级已触发 | design | design_only |
| 81 | D-FRONTEND/Event Risk Flash 事件风险快报 | Event Risk Flash 事件风险快报 | design | design_only |
| 82 | D-FRONTEND/Event Risk Report 事件风险报告 | Event Risk Report 事件风险报告 | design | design_only |
| 83 | D-FRONTEND/Execution Agent 执行Agent | Execution Agent 执行Agent | design | design_only |
| 84 | D-FRONTEND/Explainable Design Display 可解释设计展示 | Explainable Design Display 可解释设计... | design | design_only |
| 85 | D-FRONTEND/Exporter 导出器 | Exporter 导出器 | design | design_only |
| 86 | D-FRONTEND/ExternalCommand 外部指令 | ExternalCommand 外部指令 | design | design_only |
| 87 | D-FRONTEND/Feature Lineage Visualizer 特征血缘可视化器 | Feature Lineage Visualizer 特征血缘可... | design | design_only |
| 88 | D-FRONTEND/Feishu Bot 飞书机器人 | Feishu Bot 飞书机器人 | design | design_only |
| 89 | D-FRONTEND/Feishu REST Webhook 飞书REST Webhook | Feishu REST Webhook 飞书REST Webhook | design | design_only |
| 90 | D-FRONTEND/Force-Directed GPU Accelerator 力导向GPU加速器 | Force-Directed GPU Accelerator 力导向... | design | design_only |
| 91 | D-FRONTEND/Frontend Domain 前端域 | Frontend Domain 前端域 | design | design_only |
| 92 | D-FRONTEND/Frontend-Autonomy Contract 01 前端-自治权限契约 | Frontend-Autonomy Contract 01 前端-自... | design | design_only |
| 93 | D-FRONTEND/Frontend-Data Contract 01 前端-数据契约 | Frontend-Data Contract 01 前端-数据契约 | design | design_only |
| 94 | D-FRONTEND/Frontend-Governance Contract 01 前端-治理契约 | Frontend-Governance Contract 01 前端-... | design | design_only |
| 95 | D-FRONTEND/Frontend-Infrastructure Contract 01 前端-基础... | Frontend-Infrastructure Contract 01 ... | design | design_only |
| 96 | D-FRONTEND/Frontend-Integration Contract 01 前端-集成契约 | Frontend-Integration Contract 01 前端... | design | design_only |
| 97 | D-FRONTEND/Frontend-Knowledge Contract 01 前端-知识契约 | Frontend-Knowledge Contract 01 前端-... | design | design_only |
| 98 | D-FRONTEND/Frontend-ML Contract 01 前端-ML契约 | Frontend-ML Contract 01 前端-ML契约 | design | design_only |
| 99 | D-FRONTEND/Frontend-Ops Contract 01 前端-运维契约 | Frontend-Ops Contract 01 前端-运维契约 | design | design_only |
| 100 | D-FRONTEND/Frontend-Report Contract 01 前端-报告契约 | Frontend-Report Contract 01 前端-报告... | design | design_only |
| 101 | D-FRONTEND/Frontend-Risk Contract 01 前端-风控契约 | Frontend-Risk Contract 01 前端-风控契约 | design | design_only |
| 102 | D-FRONTEND/Frontend-Risk Contract 02 前端-风控契约 | Frontend-Risk Contract 02 前端-风控契约 | design | design_only |
| 103 | D-FRONTEND/Frontend-Risk Contract 03 前端-风控契约 | Frontend-Risk Contract 03 前端-风控契约 | design | design_only |
| 104 | D-FRONTEND/Frontend-Simulation Contract 01 前端-模拟契约 | Frontend-Simulation Contract 01 前端-... | design | design_only |
| 105 | D-FRONTEND/Frontend→Autonomy Interface 01 前端→自治接口 | Frontend→Autonomy Interface 01 前端... | design | design_only |
| 106 | D-FRONTEND/Frontend→Governance Interface 01 前端→治理接口 | Frontend→Governance Interface 01 前... | design | design_only |
| 107 | D-FRONTEND/Frontend→Portfolio Interface 01 前端→组合接口 | Frontend→Portfolio Interface 01 前端... | design | design_only |
| 108 | D-FRONTEND/Generator 生成器 | Generator 生成器 | design | design_only |
| 109 | D-FRONTEND/Graph Rendering Engine 图渲染引擎 | Graph Rendering Engine 图渲染引擎 | design | design_only |
| 110 | D-FRONTEND/Gray Release Status 灰度发布状态 | Gray Release Status 灰度发布状态 | design | design_only |
| 111 | D-FRONTEND/HITL Trigger Condition HITL触发条件 | HITL Trigger Condition HITL触发条件 | design | design_only |
| 112 | D-FRONTEND/HealthDegraded 健康已降级 | HealthDegraded 健康已降级 | design | design_only |
| 113 | D-FRONTEND/IS Stability Gate IS阶段稳定性门控 | IS Stability Gate IS阶段稳定性门控 | design | design_only |
| 114 | D-FRONTEND/Impact Visualizer 影响可视化器 | Impact Visualizer 影响可视化器 | design | design_only |
| 115 | D-FRONTEND/Integration API 集成API契约 | Integration API 集成API契约 | design | design_only |
| 116 | D-FRONTEND/Interaction Controller 交互控制器 | Interaction Controller 交互控制器 | design | design_only |
| 117 | D-FRONTEND/Interactive Analysis 交互式分析 | Interactive Analysis 交互式分析 | design | design_only |
| 118 | D-FRONTEND/Judge 裁判器 | Judge 裁判器 | design | design_only |
| 119 | D-FRONTEND/KGImpactAnalysis 知识图谱影响分析 | KGImpactAnalysis 知识图谱影响分析 | design | design_only |
| 120 | D-FRONTEND/L08 HMI CLI 人机交互CLI | L08 HMI CLI 人机交互CLI | design | design_only |
| 121 | D-FRONTEND/L08 HMI Notifications 人机交互通知 | L08 HMI Notifications 人机交互通知 | design | design_only |
| 122 | D-FRONTEND/L08 HMI Orchestration 人机交互编排 | L08 HMI Orchestration 人机交互编排 | design | design_only |
| 123 | D-FRONTEND/LP-021 Frontend Domain Substitute 前端域替代 | LP-021 Frontend Domain Substitute 前... | design | design_only |
| 124 | D-FRONTEND/Large-Scale Graph Rendering Engine 大规模图渲... | Large-Scale Graph Rendering Engine 大... | design | design_only |
| 125 | D-FRONTEND/Latency Waterfall Chart 延迟瀑布图 | Latency Waterfall Chart 延迟瀑布图 | design | design_only |
| 126 | D-FRONTEND/M5-S07 | M5-S07 | design | design_only |
| 127 | D-FRONTEND/M6-S07 | M6-S07 | design | design_only |
| 128 | D-FRONTEND/M7-NEW-06 | M7-NEW-06 | design | design_only |
| 129 | D-FRONTEND/M7-NEW-07 | M7-NEW-07 | design | design_only |
| 130 | D-FRONTEND/M7-S06 | M7-S06 | design | design_only |
| 131 | D-FRONTEND/M8-S08 | M8-S08 | design | design_only |
| 132 | D-FRONTEND/Manual Review Decision 人工审核决策 | Manual Review Decision 人工审核决策 | design | design_only |
| 133 | D-FRONTEND/Manual Review Panel 人工审核面板 | Manual Review Panel 人工审核面板 | design | design_only |
| 134 | D-FRONTEND/Manual Submit Interface 手动提交界面 | Manual Submit Interface 手动提交界面 | design | design_only |
| 135 | D-FRONTEND/Manual Supplement Input 人工补充输入 | Manual Supplement Input 人工补充输入 | design | design_only |
| 136 | D-FRONTEND/Mathematical Reflection Optimization 数学反思... | Mathematical Reflection Optimization ... | design | design_only |
| 137 | D-FRONTEND/Mesh Visualizer 网格可视化器 | Mesh Visualizer 网格可视化器 | design | design_only |
| 138 | D-FRONTEND/Mobile Dashboard 移动端仪表盘 | Mobile Dashboard 移动端仪表盘 | design | design_only |
| 139 | D-FRONTEND/ModelDriftDetected 模型漂移已检测 | ModelDriftDetected 模型漂移已检测 | design | design_only |
| 140 | D-FRONTEND/Module Output Monitoring 模块输出监控 | Module Output Monitoring 模块输出监控 | design | design_only |
| 141 | D-FRONTEND/Monthly Risk Governance 月度风险治理 | Monthly Risk Governance 月度风险治理 | design | design_only |
| 142 | D-FRONTEND/Monthly Risk Report 月度风险报告 | Monthly Risk Report 月度风险报告 | design | design_only |
| 143 | D-FRONTEND/Multi-Scale Drift Level 多尺度漂移等级 | Multi-Scale Drift Level 多尺度漂移等级 | design | design_only |
| 144 | D-FRONTEND/Natural Language Interface 自然语言界面 | Natural Language Interface 自然语言界面 | design | design_only |
| 145 | D-FRONTEND/NotificationRouter 通知路由 | NotificationRouter 通知路由 | design | design_only |
| 146 | D-FRONTEND/OOS Gate OOS阶段门控 | OOS Gate OOS阶段门控 | design | design_only |
| 147 | D-FRONTEND/OTel Trace Renderer OTel追踪渲染器 | OTel Trace Renderer OTel追踪渲染器 | design | design_only |
| 148 | D-FRONTEND/OTel追踪渲染器族 OTel Trace Renderers | OTel追踪渲染器族 OTel Trace Renderers | design | design_only |
| 149 | D-FRONTEND/One-Click Quant Interface 一键量化交易界面 | One-Click Quant Interface 一键量化交... | design | design_only |
| 150 | D-FRONTEND/Orchestration Visualizer 编排可视化器 | Orchestration Visualizer 编排可视化器 | design | design_only |
| 151 | D-FRONTEND/Phase 5 Activation Phase 5激活阶段 | Phase 5 Activation Phase 5激活阶段 | design | design_only |
| 152 | D-FRONTEND/PlantUML Rendering PlantUML渲染 | PlantUML Rendering PlantUML渲染 | design | design_only |
| 153 | D-FRONTEND/Real-time Dashboard 实时仪表盘 | Real-time Dashboard 实时仪表盘 | design | design_only |
| 154 | D-FRONTEND/Real-time P&L 实时P&L | Real-time P&L 实时P&L | design | design_only |
| 155 | D-FRONTEND/Real-time Renderer 实时渲染器 | Real-time Renderer 实时渲染器 | design | design_only |
| 156 | D-FRONTEND/Real-time Rendering Enhancer 实时渲染增强器 | Real-time Rendering Enhancer 实时渲染... | design | design_only |
| 157 | D-FRONTEND/Real-time Updater 实时更新器 | Real-time Updater 实时更新器 | design | design_only |
| 158 | D-FRONTEND/RealtimeDashboard 实时仪表盘 | RealtimeDashboard 实时仪表盘 | design | design_only |
| 159 | D-FRONTEND/Report Visualization 报告可视化 | Report Visualization 报告可视化 | design | design_only |
| 160 | D-FRONTEND/Representation Learning Drift Warning 表示学习... | Representation Learning Drift Warning... | design | design_only |
| 161 | D-FRONTEND/Result Renderer 结果渲染器 | Result Renderer 结果渲染器 | design | design_only |
| 162 | D-FRONTEND/Risk Contagion Visualizer 风险传染可视化器 | Risk Contagion Visualizer 风险传染可... | design | design_only |
| 163 | D-FRONTEND/Risk Control System Role 风控系统角色 | Risk Control System Role 风控系统角色 | design | design_only |
| 164 | D-FRONTEND/Robo-Advisor 智能投顾 | Robo-Advisor 智能投顾 | design | design_only |
| 165 | D-FRONTEND/Saga Visualizer Saga可视化器 | Saga Visualizer Saga可视化器 | design | design_only |
| 166 | D-FRONTEND/Search Locator 搜索定位器 | Search Locator 搜索定位器 | design | design_only |
| 167 | D-FRONTEND/Security Dependency Visualizer 安全依赖可视化器 | Security Dependency Visualizer 安全依... | design | design_only |
| 168 | D-FRONTEND/Signal Agent 信号Agent | Signal Agent 信号Agent | design | design_only |
| 169 | D-FRONTEND/Simulation Observation Data 模拟盘观察数据 | Simulation Observation Data 模拟盘观... | design | design_only |
| 170 | D-FRONTEND/Strategy Management UI 策略管理界面 | Strategy Management UI 策略管理界面 | design | design_only |
| 171 | D-FRONTEND/Streamlit Dashboard Streamlit轻量仪表盘 | Streamlit Dashboard Streamlit轻量仪表盘 | design | design_only |
| 172 | D-FRONTEND/Streamlit Streamlit仪表盘 | Streamlit Streamlit仪表盘 | design | design_only |
| 173 | D-FRONTEND/Stress Test 压力测试 | Stress Test 压力测试 | design | design_only |
| 174 | D-FRONTEND/System Health Dashboard 系统健康仪表盘 | System Health Dashboard 系统健康仪表盘 | design | design_only |
| 175 | D-FRONTEND/SystemDegraded 系统已降级 | SystemDegraded 系统已降级 | design | design_only |
| 176 | D-FRONTEND/SystemHealthVisualization 系统健康可视化 | SystemHealthVisualization 系统健康可视化 | design | design_only |
| 177 | D-FRONTEND/Time Dimension Animator 时间维度动画器 | Time Dimension Animator 时间维度动画器 | design | design_only |
| 178 | D-FRONTEND/Time Travel Controller 时间旅行控制器 | Time Travel Controller 时间旅行控制器 | design | design_only |
| 179 | D-FRONTEND/Trace Anomaly ML Detector Trace异常ML检测器 | Trace Anomaly ML Detector Trace异常ML... | design | design_only |
| 180 | D-FRONTEND/Trace Reporter 追踪报告器 | Trace Reporter 追踪报告器 | design | design_only |
| 181 | D-FRONTEND/Trace Topology Auto-Extractor Trace拓扑自动提取器 | Trace Topology Auto-Extractor Trace拓... | design | design_only |
| 182 | D-FRONTEND/Trace Visualizer 追踪可视化器 | Trace Visualizer 追踪可视化器 | design | design_only |
| 183 | D-FRONTEND/Traceability Visualizer 追溯可视化器 | Traceability Visualizer 追溯可视化器 | design | design_only |
| 184 | D-FRONTEND/Trace到依赖图映射器 Trace to DepGraph Mapper | Trace到依赖图映射器 Trace to DepGraph... | design | design_only |
| 185 | D-FRONTEND/Trader Role 交易员角色 | Trader Role 交易员角色 | design | design_only |
| 186 | D-FRONTEND/Trading Architecture Visualizer 交易架构可视化器 | Trading Architecture Visualizer 交易... | design | design_only |
| 187 | D-FRONTEND/Trading Chatbot 交易智能客服 | Trading Chatbot 交易智能客服 | design | design_only |
| 188 | D-FRONTEND/Trading Monitoring Dashboard 交易监控仪表盘 | Trading Monitoring Dashboard 交易监控... | design | design_only |
| 189 | D-FRONTEND/Triple Semantic Consistency Display 三重语义一... | Triple Semantic Consistency Display ... | design | design_only |
| 190 | D-FRONTEND/Ultra-Large Graph Interaction Optimizer 超大规... | Ultra-Large Graph Interaction Optimiz... | design | design_only |
| 191 | D-FRONTEND/UserAction 用户操作 | UserAction 用户操作 | design | design_only |
| 192 | D-FRONTEND/VR Renderer VR渲染器 | VR Renderer VR渲染器 | design | design_only |
| 193 | D-FRONTEND/VaR Value at Risk 风险价值 | VaR Value at Risk 风险价值 | design | design_only |
| 194 | D-FRONTEND/WFA Gate WFA阶段门控 | WFA Gate WFA阶段门控 | design | design_only |
| 195 | D-FRONTEND/Waterfall Interaction Engine 瀑布图交互引擎 | Waterfall Interaction Engine 瀑布图交... | design | design_only |
| 196 | D-FRONTEND/WeChat Bot 微信机器人 | WeChat Bot 微信机器人 | design | design_only |
| 197 | D-FRONTEND/WeChat Webhook 微信Webhook | WeChat Webhook 微信Webhook | design | design_only |
| 198 | D-FRONTEND/WebGPU Large-Scale Renderer WebGPU大规模渲染器 | WebGPU Large-Scale Renderer WebGPU大... | design | design_only |
| 199 | D-FRONTEND/Weekly Risk Deep Dive 周度风险深度 | Weekly Risk Deep Dive 周度风险深度 | design | design_only |
| 200 | D-FRONTEND/Weekly Risk Report 周度风险报告 | Weekly Risk Report 周度风险报告 | design | design_only |

> (仅显示前 200 个模块，共 203 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 220 条 / 220 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 220 条 / 220 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 165 条 / edges                               │
│   [contract]: 24 条 / edges                                      │
│   [config_depends]: 15 条 / edges                                │
│   [event]: 15 条 / edges                                         │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (165 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   app.py → fitness_functions.py                                  │
│   app.py → knowledge_overview.py                                 │
│   app.py → gate_statistics.py                                    │
│   app.py → olap_trend.py                                         │
│   app.py → task_progress.py                                      │
│   Real-time Dashboard 实时... → M5-S07                           │
│   M5-S07 → M6-S07                                                │
│   M6-S07 → M7-S06                                                │
│   M6-S07 → Administrator Role 管理员...                          │
│   M7-S06 → M7-NEW-06                                             │
│   M7-NEW-06 → M7-NEW-07                                          │
│   M7-NEW-07 → M8-S08                                             │
│   M8-S08 → Dashboard Framework 仪表...                           │
│   Dashboard Framework 仪表... → Chart Engine 图表引擎            │
│   Chart Engine 图表引擎 → Alert Notification UI 告...            │
│   Alert Notification UI 告... → Strategy Management UI 策...     │
│   Alert Notification UI 告... → Trader Role 交易员角色           │
│   Strategy Management UI 策... → Report Visualization 报告...    │
│   Report Visualization 报告... → Interactive Analysis 交互...    │
│   Interactive Analysis 交互... → AlertVisualization 告警可...    │
│   AlertVisualization 告警可... → SystemHealthVisualization...    │
│   SystemHealthVisualization... → Custom Chart Builder 自定...    │
│   Custom Chart Builder 自定... → API Gateway UI API网关界面      │
│   API Gateway UI API网关界面 → Approval Workflow UI 审批...      │
│   Approval Workflow UI 审批... → NotificationRouter 通知路由     │
│   NotificationRouter 通知路由 → Mobile Dashboard 移动端仪...     │
│   Mobile Dashboard 移动端仪... → End-to-End Trace Visualiz...    │
│   End-to-End Trace Visualiz... → Collaborative Workspace ...     │
│   Collaborative Workspace ... → Trading Chatbot 交易智能客服     │
│   Trading Chatbot 交易智能客服 → Robo-Advisor 智能投顾           │
│   Robo-Advisor 智能投顾 → One-Click Quant Interface...           │
│   One-Click Quant Interface... → AI Model HR Dashboard AI...     │
│   AI Model HR Dashboard AI... → API Gateway Proxy API网关...     │
│   API Gateway Proxy API网关... → Feishu Bot 飞书机器人           │
│   Feishu Bot 飞书机器人 → WeChat Bot 微信机器人                  │
│   Feishu Bot 飞书机器人 → Signal Agent 信号Agent                 │
│   WeChat Bot 微信机器人 → WeChat Webhook 微信Webhook             │
│   Frontend Domain 前端域 → Real-time Updater 实时更新器          │
│   WeChat Webhook 微信Webhook → Email SMTP 邮件SMTP               │
│   Email SMTP 邮件SMTP → Collaboration Watermark ...              │
│   Collaboration Watermark ... → Collaboration Annotation ...     │
│   Collaboration Annotation ... → PlantUML Rendering PlantU...    │
│   PlantUML Rendering PlantU... → Streamlit Streamlit仪表盘       │
│   Streamlit Streamlit仪表盘 → Collaboration Watermark ...        │
│   Collaboration Watermark ... → Collaboration Annotation ...     │
│   Collaboration Annotation ... → 仪表盘设计 仪表盘 Table         │
│   LP-021 Frontend Domain Su... → Cluster Heatmap 集群热力图      │
│   仪表盘设计 仪表盘 Table → OTel追踪渲染器族 OTel Tra...         │
│   OTel追踪渲染器族 OTel Tra... → 运行时依赖可视化器 Runtim...    │
│   ...还有 116 条 / 116 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[contract]** (24 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (15 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (15 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 220 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `10_d_frontend_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
