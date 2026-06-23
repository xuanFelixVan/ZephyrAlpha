---
doc_type: domain_architecture_doc
title: D-FRONTEND 前端架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 10_d_frontend 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 10 | Number | 10 |
| 域ID | D-FRONTEND | Domain ID | D-FRONTEND |
| 域名称 | 前端 | Domain Name | 前端 |
| 层级 | L1_platform | Layer | L1_platform |
| 模块数 | 237 | Module Count | 237 |
| 域内依赖 | 220 | Internal Dependencies | 220 |
| 跨域入边 | 66 | Cross-domain Incoming | 66 |
| 跨域出边 | 369 | Cross-domain Outgoing | 369 |
| 设计态模块 | 213 | Design Modules | 213 |
| 原型态模块 | 11 | Prototype Modules | 11 |
| 生产态模块 | 7 | Production Modules | 7 |
| 容量 | 237/150 (超容) | Capacity | 237/150 (超容) |
| 描述 | Web界面、可视化看板、交互组件。人机交互入口。 | Description | Web界面、可视化看板、交互组件。人机交互入口。 |

## 模块清单 / Module List

共 237 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-FRONTEND/3D Force-Directed Layout 3D力导向布局器 | 3D Force-Directed Layout 3D力导向布局器 | design | design_only | D-FRONTEND/3D Force-Directed Layout 3D力导向布局器 | 3D Force-Directed Layout 3D力导向布局器 | design | design_only |
| D-FRONTEND/4-Level Risk Decision 4级风控决策 | 4-Level Risk Decision 4级风控决策 | design | design_only | D-FRONTEND/4-Level Risk Decision 4级风控决策 | 4-Level Risk Decision 4级风控决策 | design | design_only |
| D-FRONTEND/AI Agent调用链追踪器 AI Agent Call Chain Tracer | AI Agent调用链追踪器 AI Agent Call Chain Tr... | design | design_only | D-FRONTEND/AI Agent调用链追踪器 AI Agent Call Chain Tracer | AI Agent调用链追踪器 AI Agent Call Chain Tr... | design | design_only |
| D-FRONTEND/AI Autonomy Dashboard AI自治仪表盘 | AI Autonomy Dashboard AI自治仪表盘 | design | design_only | D-FRONTEND/AI Autonomy Dashboard AI自治仪表盘 | AI Autonomy Dashboard AI自治仪表盘 | design | design_only |
| D-FRONTEND/AI Collection Result Display AI采集结果展示 | AI Collection Result Display AI采集结果展示 | design | design_only | D-FRONTEND/AI Collection Result Display AI采集结果展示 | AI Collection Result Display AI采集结果展示 | design | design_only |
| D-FRONTEND/AI Model HR Dashboard AI模型HR管理面板 | AI Model HR Dashboard AI模型HR管理面板 | design | design_only | D-FRONTEND/AI Model HR Dashboard AI模型HR管理面板 | AI Model HR Dashboard AI模型HR管理面板 | design | design_only |
| D-FRONTEND/AI Role AI角色 | AI Role AI角色 | design | design_only | D-FRONTEND/AI Role AI角色 | AI Role AI角色 | design | design_only |
| D-FRONTEND/AI-Driven Dependency Explorer AI驱动依赖图探索器 | AI-Driven Dependency Explorer AI驱动依赖图探索器 | design | design_only | D-FRONTEND/AI-Driven Dependency Explorer AI驱动依赖图探索器 | AI-Driven Dependency Explorer AI驱动依赖图探索器 | design | design_only |
| D-FRONTEND/API Dependency Visualizer API依赖可视化器 | API Dependency Visualizer API依赖可视化器 | design | design_only | D-FRONTEND/API Dependency Visualizer API依赖可视化器 | API Dependency Visualizer API依赖可视化器 | design | design_only |
| D-FRONTEND/API Gateway Proxy API网关代理 | API Gateway Proxy API网关代理 | design | design_only | D-FRONTEND/API Gateway Proxy API网关代理 | API Gateway Proxy API网关代理 | design | design_only |
| D-FRONTEND/API Gateway UI API网关界面 | API Gateway UI API网关界面 | design | design_only | D-FRONTEND/API Gateway UI API网关界面 | API Gateway UI API网关界面 | design | design_only |
| D-FRONTEND/AST Sandbox Validation Result AST沙箱验证结果 | AST Sandbox Validation Result AST沙箱验证结果 | design | design_only | D-FRONTEND/AST Sandbox Validation Result AST沙箱验证结果 | AST Sandbox Validation Result AST沙箱验证结果 | design | design_only |
| D-FRONTEND/Administrator Role 管理员角色 | Administrator Role 管理员角色 | design | design_only | D-FRONTEND/Administrator Role 管理员角色 | Administrator Role 管理员角色 | design | design_only |
| D-FRONTEND/Adversarial Test Result 对抗性测试结果 | Adversarial Test Result 对抗性测试结果 | design | design_only | D-FRONTEND/Adversarial Test Result 对抗性测试结果 | Adversarial Test Result 对抗性测试结果 | design | design_only |
| D-FRONTEND/Agent Behavior Monitoring Agent行为监控 | Agent Behavior Monitoring Agent行为监控 | design | design_only | D-FRONTEND/Agent Behavior Monitoring Agent行为监控 | Agent Behavior Monitoring Agent行为监控 | design | design_only |
| D-FRONTEND/Agent Dependency Heatmap Agent依赖热力图 | Agent Dependency Heatmap Agent依赖热力图 | design | design_only | D-FRONTEND/Agent Dependency Heatmap Agent依赖热力图 | Agent Dependency Heatmap Agent依赖热力图 | design | design_only |
| D-FRONTEND/Alert Notification UI 告警通知界面 | Alert Notification UI 告警通知界面 | design | design_only | D-FRONTEND/Alert Notification UI 告警通知界面 | Alert Notification UI 告警通知界面 | design | design_only |
| D-FRONTEND/Alert Output Alert产出 | Alert Output Alert产出 | design | design_only | D-FRONTEND/Alert Output Alert产出 | Alert Output Alert产出 | design | design_only |
| D-FRONTEND/AlertTriggered 告警已触发 | AlertTriggered 告警已触发 | design | design_only | D-FRONTEND/AlertTriggered 告警已触发 | AlertTriggered 告警已触发 | design | design_only |
| D-FRONTEND/AlertVisualization 告警可视化 | AlertVisualization 告警可视化 | design | design_only | D-FRONTEND/AlertVisualization 告警可视化 | AlertVisualization 告警可视化 | design | design_only |
| D-FRONTEND/Anomaly Propagation 3D Visualizer 异常传播3D可视化器 | Anomaly Propagation 3D Visualizer 异常传... | design | design_only | D-FRONTEND/Anomaly Propagation 3D Visualizer 异常传播3D可视化器 | Anomaly Propagation 3D Visualizer 异常传... | design | design_only |
| D-FRONTEND/Approval Interface Security 审批界面安全约束 | Approval Interface Security 审批界面安全约束 | design | design_only | D-FRONTEND/Approval Interface Security 审批界面安全约束 | Approval Interface Security 审批界面安全约束 | design | design_only |
| D-FRONTEND/Approval Workflow UI 审批流程界面 | Approval Workflow UI 审批流程界面 | design | design_only | D-FRONTEND/Approval Workflow UI 审批流程界面 | Approval Workflow UI 审批流程界面 | design | design_only |
| D-FRONTEND/ApprovalRequest Output ApprovalRequest产出 | ApprovalRequest Output ApprovalRequest产出 | design | design_only | D-FRONTEND/ApprovalRequest Output ApprovalRequest产出 | ApprovalRequest Output ApprovalRequest产出 | design | design_only |
| D-FRONTEND/ApprovalRequested 审批已请求 | ApprovalRequested 审批已请求 | design | design_only | D-FRONTEND/ApprovalRequested 审批已请求 | ApprovalRequested 审批已请求 | design | design_only |
| D-FRONTEND/ApprovalWorkflowUI 审批工作流UI | ApprovalWorkflowUI 审批工作流UI | design | design_only | D-FRONTEND/ApprovalWorkflowUI 审批工作流UI | ApprovalWorkflowUI 审批工作流UI | design | design_only |
| D-FRONTEND/Architecture Doc Auto-Generator 架构文档自动生成器 | Architecture Doc Auto-Generator 架构文档自... | design | design_only | D-FRONTEND/Architecture Doc Auto-Generator 架构文档自动生成器 | Architecture Doc Auto-Generator 架构文档自... | design | design_only |
| D-FRONTEND/Auto-Layout Optimizer 自动布局优化器 | Auto-Layout Optimizer 自动布局优化器 | design | design_only | D-FRONTEND/Auto-Layout Optimizer 自动布局优化器 | Auto-Layout Optimizer 自动布局优化器 | design | design_only |
| D-FRONTEND/Backtest Result Summary 回测结果摘要 | Backtest Result Summary 回测结果摘要 | design | design_only | D-FRONTEND/Backtest Result Summary 回测结果摘要 | Backtest Result Summary 回测结果摘要 | design | design_only |
| D-FRONTEND/BacktestPassed 回测已通过 | BacktestPassed 回测已通过 | design | design_only | D-FRONTEND/BacktestPassed 回测已通过 | BacktestPassed 回测已通过 | design | design_only |
| D-FRONTEND/CLI Interface 命令行交互入口 | CLI Interface 命令行交互入口 | design | design_only | D-FRONTEND/CLI Interface 命令行交互入口 | CLI Interface 命令行交互入口 | design | design_only |
| D-FRONTEND/CQRS Visualization CQRS可视化器 | CQRS Visualization CQRS可视化器 | design | design_only | D-FRONTEND/CQRS Visualization CQRS可视化器 | CQRS Visualization CQRS可视化器 | design | design_only |
| D-FRONTEND/CVaR Conditional VaR 条件风险价值 | CVaR Conditional VaR 条件风险价值 | design | design_only | D-FRONTEND/CVaR Conditional VaR 条件风险价值 | CVaR Conditional VaR 条件风险价值 | design | design_only |
| D-FRONTEND/Call Graph Visualizer 调用图可视化器 | Call Graph Visualizer 调用图可视化器 | design | design_only | D-FRONTEND/Call Graph Visualizer 调用图可视化器 | Call Graph Visualizer 调用图可视化器 | design | design_only |
| D-FRONTEND/Capacity Dashboard 容量仪表盘 | Capacity Dashboard 容量仪表盘 | design | design_only | D-FRONTEND/Capacity Dashboard 容量仪表盘 | Capacity Dashboard 容量仪表盘 | design | design_only |
| D-FRONTEND/Chart Engine 图表引擎 | Chart Engine 图表引擎 | design | design_only | D-FRONTEND/Chart Engine 图表引擎 | Chart Engine 图表引擎 | design | design_only |
| D-FRONTEND/Cluster Heatmap 集群热力图 | Cluster Heatmap 集群热力图 | design | design_only | D-FRONTEND/Cluster Heatmap 集群热力图 | Cluster Heatmap 集群热力图 | design | design_only |
| D-FRONTEND/Code Comparison View 代码对比视图 | Code Comparison View 代码对比视图 | design | design_only | D-FRONTEND/Code Comparison View 代码对比视图 | Code Comparison View 代码对比视图 | design | design_only |
| D-FRONTEND/Code Review Panel 代码审查面板 | Code Review Panel 代码审查面板 | design | design_only | D-FRONTEND/Code Review Panel 代码审查面板 | Code Review Panel 代码审查面板 | design | design_only |
| D-FRONTEND/Collaboration Annotation 协作批注 | Collaboration Annotation 协作批注 | design | design_only | D-FRONTEND/Collaboration Annotation 协作批注 | Collaboration Annotation 协作批注 | design | design_only |
| D-FRONTEND/Collaboration Annotation 报告协作批注 | Collaboration Annotation 报告协作批注 | design | design_only | D-FRONTEND/Collaboration Annotation 报告协作批注 | Collaboration Annotation 报告协作批注 | design | design_only |
| D-FRONTEND/Collaboration Watermark 协作平台水印 | Collaboration Watermark 协作平台水印 | design | design_only | D-FRONTEND/Collaboration Watermark 协作平台水印 | Collaboration Watermark 协作平台水印 | design | design_only |
| D-FRONTEND/Collaboration Watermark 协作版报告水印 | Collaboration Watermark 协作版报告水印 | design | design_only | D-FRONTEND/Collaboration Watermark 协作版报告水印 | Collaboration Watermark 协作版报告水印 | design | design_only |
| D-FRONTEND/Collaborative Dependency Annotator 协作依赖图标注器 | Collaborative Dependency Annotator 协作... | design | design_only | D-FRONTEND/Collaborative Dependency Annotator 协作依赖图标注器 | Collaborative Dependency Annotator 协作... | design | design_only |
| D-FRONTEND/Collaborative Workspace 协作工作区 | Collaborative Workspace 协作工作区 | design | design_only | D-FRONTEND/Collaborative Workspace 协作工作区 | Collaborative Workspace 协作工作区 | design | design_only |
| D-FRONTEND/Collection Progress Tracking 采集进度追踪 | Collection Progress Tracking 采集进度追踪 | design | design_only | D-FRONTEND/Collection Progress Tracking 采集进度追踪 | Collection Progress Tracking 采集进度追踪 | design | design_only |
| D-FRONTEND/Collection Strategy Adjustment Log 采集策略调整日志 | Collection Strategy Adjustment Log 采集... | design | design_only | D-FRONTEND/Collection Strategy Adjustment Log 采集策略调整日志 | Collection Strategy Adjustment Log 采集... | design | design_only |
| D-FRONTEND/Conformal VaR 共形VaR | Conformal VaR 共形VaR | design | design_only | D-FRONTEND/Conformal VaR 共形VaR | Conformal VaR 共形VaR | design | design_only |
| D-FRONTEND/Convergence Status Indicator 收敛状态指示 | Convergence Status Indicator 收敛状态指示 | design | design_only | D-FRONTEND/Convergence Status Indicator 收敛状态指示 | Convergence Status Indicator 收敛状态指示 | design | design_only |
| D-FRONTEND/Coupling Heatmap 耦合热力图 | Coupling Heatmap 耦合热力图 | design | design_only | D-FRONTEND/Coupling Heatmap 耦合热力图 | Coupling Heatmap 耦合热力图 | design | design_only |
| D-FRONTEND/Critic Criticism Display Critic批评展示 | Critic Criticism Display Critic批评展示 | design | design_only | D-FRONTEND/Critic Criticism Display Critic批评展示 | Critic Criticism Display Critic批评展示 | design | design_only |
| D-FRONTEND/Critic 批评器 | Critic 批评器 | design | design_only | D-FRONTEND/Critic 批评器 | Critic 批评器 | design | design_only |
| D-FRONTEND/Cross-Service Trace Correlator 跨服务Trace关联器 | Cross-Service Trace Correlator 跨服务Tra... | design | design_only | D-FRONTEND/Cross-Service Trace Correlator 跨服务Trace关联器 | Cross-Service Trace Correlator 跨服务Tra... | design | design_only |
| D-FRONTEND/Custom Chart Builder 自定义图表 | Custom Chart Builder 自定义图表 | design | design_only | D-FRONTEND/Custom Chart Builder 自定义图表 | Custom Chart Builder 自定义图表 | design | design_only |
| D-FRONTEND/D-FRONTEND 前端 | D-FRONTEND 前端 | design | design_only | D-FRONTEND/D-FRONTEND 前端 | D-FRONTEND 前端 | design | design_only |
| D-FRONTEND/D-PORTFOLIO Domain 组合域 | D-PORTFOLIO Domain 组合域 | design | design_only | D-FRONTEND/D-PORTFOLIO Domain 组合域 | D-PORTFOLIO Domain 组合域 | design | design_only |
| D-FRONTEND/Daily Risk Report 日度风险报告 | Daily Risk Report 日度风险报告 | design | design_only | D-FRONTEND/Daily Risk Report 日度风险报告 | Daily Risk Report 日度风险报告 | design | design_only |
| D-FRONTEND/Daily Risk Summary 日度风险摘要 | Daily Risk Summary 日度风险摘要 | design | design_only | D-FRONTEND/Daily Risk Summary 日度风险摘要 | Daily Risk Summary 日度风险摘要 | design | design_only |
| D-FRONTEND/Dashboard Framework 仪表盘框架 | Dashboard Framework 仪表盘框架 | design | design_only | D-FRONTEND/Dashboard Framework 仪表盘框架 | Dashboard Framework 仪表盘框架 | design | design_only |
| D-FRONTEND/Dashboard Output Dashboard产出 | Dashboard Output Dashboard产出 | design | design_only | D-FRONTEND/Dashboard Output Dashboard产出 | Dashboard Output Dashboard产出 | design | design_only |
| D-FRONTEND/Dashboard 仪表盘 | Dashboard 仪表盘 | design | design_only | D-FRONTEND/Dashboard 仪表盘 | Dashboard 仪表盘 | design | design_only |
| D-FRONTEND/DashboardUpdated 仪表盘已更新 | DashboardUpdated 仪表盘已更新 | design | design_only | D-FRONTEND/DashboardUpdated 仪表盘已更新 | DashboardUpdated 仪表盘已更新 | design | design_only |
| D-FRONTEND/Decision Gate Progress 决策门控进度 | Decision Gate Progress 决策门控进度 | design | design_only | D-FRONTEND/Decision Gate Progress 决策门控进度 | Decision Gate Progress 决策门控进度 | design | design_only |
| D-FRONTEND/Decision Gate State Machine 决策门控状态机 | Decision Gate State Machine 决策门控状态机 | design | design_only | D-FRONTEND/Decision Gate State Machine 决策门控状态机 | Decision Gate State Machine 决策门控状态机 | design | design_only |
| D-FRONTEND/Decision Tree Visualizer 决策树可视化器 | Decision Tree Visualizer 决策树可视化器 | design | design_only | D-FRONTEND/Decision Tree Visualizer 决策树可视化器 | Decision Tree Visualizer 决策树可视化器 | design | design_only |
| D-FRONTEND/Degradation Status Dashboard 降级状态仪表盘 | Degradation Status Dashboard 降级状态仪表盘 | design | design_only | D-FRONTEND/Degradation Status Dashboard 降级状态仪表盘 | Degradation Status Dashboard 降级状态仪表盘 | design | design_only |
| D-FRONTEND/Density-Aware VaR 密度感知VaR | Density-Aware VaR 密度感知VaR | design | design_only | D-FRONTEND/Density-Aware VaR 密度感知VaR | Density-Aware VaR 密度感知VaR | design | design_only |
| D-FRONTEND/Dependency Diff Viewer 依赖图差异查看器 | Dependency Diff Viewer 依赖图差异查看器 | design | design_only | D-FRONTEND/Dependency Diff Viewer 依赖图差异查看器 | Dependency Diff Viewer 依赖图差异查看器 | design | design_only |
| D-FRONTEND/Dependency Graph LOD Engine 依赖图LOD引擎 | Dependency Graph LOD Engine 依赖图LOD引擎 | design | design_only | D-FRONTEND/Dependency Graph LOD Engine 依赖图LOD引擎 | Dependency Graph LOD Engine 依赖图LOD引擎 | design | design_only |
| D-FRONTEND/Dependency Timeline Player 依赖图时间线播放器 | Dependency Timeline Player 依赖图时间线播放器 | design | design_only | D-FRONTEND/Dependency Timeline Player 依赖图时间线播放器 | Dependency Timeline Player 依赖图时间线播放器 | design | design_only |
| D-FRONTEND/Developer Dashboard 开发者仪表盘 | Developer Dashboard 开发者仪表盘 | design | design_only | D-FRONTEND/Developer Dashboard 开发者仪表盘 | Developer Dashboard 开发者仪表盘 | design | design_only |
| D-FRONTEND/Drift Detection Status Panel 漂移检测状态面板 | Drift Detection Status Panel 漂移检测状态面板 | design | design_only | D-FRONTEND/Drift Detection Status Panel 漂移检测状态面板 | Drift Detection Status Panel 漂移检测状态面板 | design | design_only |
| D-FRONTEND/E-SIM-04 BacktestPassed 回测通过 | E-SIM-04 BacktestPassed 回测通过 | design | design_only | D-FRONTEND/E-SIM-04 BacktestPassed 回测通过 | E-SIM-04 BacktestPassed 回测通过 | design | design_only |
| D-FRONTEND/Effect Evaluation Report 效果评估报告 | Effect Evaluation Report 效果评估报告 | design | design_only | D-FRONTEND/Effect Evaluation Report 效果评估报告 | Effect Evaluation Report 效果评估报告 | design | design_only |
| D-FRONTEND/Effect Metric Trend 效果指标趋势 | Effect Metric Trend 效果指标趋势 | design | design_only | D-FRONTEND/Effect Metric Trend 效果指标趋势 | Effect Metric Trend 效果指标趋势 | design | design_only |
| D-FRONTEND/Email SMTP 邮件SMTP | Email SMTP 邮件SMTP | design | design_only | D-FRONTEND/Email SMTP 邮件SMTP | Email SMTP 邮件SMTP | design | design_only |
| D-FRONTEND/End-to-End Trace Visualizer 端到端追踪可视化 | End-to-End Trace Visualizer 端到端追踪可视化 | design | design_only | D-FRONTEND/End-to-End Trace Visualizer 端到端追踪可视化 | End-to-End Trace Visualizer 端到端追踪可视化 | design | design_only |
| D-FRONTEND/EndToEndTraceVisualizer 端到端追踪可视化 | EndToEndTraceVisualizer 端到端追踪可视化 | design | design_only | D-FRONTEND/EndToEndTraceVisualizer 端到端追踪可视化 | EndToEndTraceVisualizer 端到端追踪可视化 | design | design_only |
| D-FRONTEND/Endpoint Refiner 端点级细化器 | Endpoint Refiner 端点级细化器 | design | design_only | D-FRONTEND/Endpoint Refiner 端点级细化器 | Endpoint Refiner 端点级细化器 | design | design_only |
| D-FRONTEND/EscalationTriggered 升级已触发 | EscalationTriggered 升级已触发 | design | design_only | D-FRONTEND/EscalationTriggered 升级已触发 | EscalationTriggered 升级已触发 | design | design_only |
| D-FRONTEND/Event Risk Flash 事件风险快报 | Event Risk Flash 事件风险快报 | design | design_only | D-FRONTEND/Event Risk Flash 事件风险快报 | Event Risk Flash 事件风险快报 | design | design_only |
| D-FRONTEND/Event Risk Report 事件风险报告 | Event Risk Report 事件风险报告 | design | design_only | D-FRONTEND/Event Risk Report 事件风险报告 | Event Risk Report 事件风险报告 | design | design_only |
| D-FRONTEND/Execution Agent 执行Agent | Execution Agent 执行Agent | design | design_only | D-FRONTEND/Execution Agent 执行Agent | Execution Agent 执行Agent | design | design_only |
| D-FRONTEND/Explainable Design Display 可解释设计展示 | Explainable Design Display 可解释设计展示 | design | design_only | D-FRONTEND/Explainable Design Display 可解释设计展示 | Explainable Design Display 可解释设计展示 | design | design_only |
| D-FRONTEND/Exporter 导出器 | Exporter 导出器 | design | design_only | D-FRONTEND/Exporter 导出器 | Exporter 导出器 | design | design_only |
| D-FRONTEND/ExternalCommand 外部指令 | ExternalCommand 外部指令 | design | design_only | D-FRONTEND/ExternalCommand 外部指令 | ExternalCommand 外部指令 | design | design_only |
| D-FRONTEND/Feature Lineage Visualizer 特征血缘可视化器 | Feature Lineage Visualizer 特征血缘可视化器 | design | design_only | D-FRONTEND/Feature Lineage Visualizer 特征血缘可视化器 | Feature Lineage Visualizer 特征血缘可视化器 | design | design_only |
| D-FRONTEND/Feishu Bot 飞书机器人 | Feishu Bot 飞书机器人 | design | design_only | D-FRONTEND/Feishu Bot 飞书机器人 | Feishu Bot 飞书机器人 | design | design_only |
| D-FRONTEND/Feishu REST Webhook 飞书REST Webhook | Feishu REST Webhook 飞书REST Webhook | design | design_only | D-FRONTEND/Feishu REST Webhook 飞书REST Webhook | Feishu REST Webhook 飞书REST Webhook | design | design_only |
| D-FRONTEND/Force-Directed GPU Accelerator 力导向GPU加速器 | Force-Directed GPU Accelerator 力导向GPU加速器 | design | design_only | D-FRONTEND/Force-Directed GPU Accelerator 力导向GPU加速器 | Force-Directed GPU Accelerator 力导向GPU加速器 | design | design_only |
| D-FRONTEND/Frontend Domain 前端域 | Frontend Domain 前端域 | design | design_only | D-FRONTEND/Frontend Domain 前端域 | Frontend Domain 前端域 | design | design_only |
| D-FRONTEND/Frontend-Autonomy Contract 01 前端-自治权限契约 | Frontend-Autonomy Contract 01 前端-自治权限契约 | design | design_only | D-FRONTEND/Frontend-Autonomy Contract 01 前端-自治权限契约 | Frontend-Autonomy Contract 01 前端-自治权限契约 | design | design_only |
| D-FRONTEND/Frontend-Data Contract 01 前端-数据契约 | Frontend-Data Contract 01 前端-数据契约 | design | design_only | D-FRONTEND/Frontend-Data Contract 01 前端-数据契约 | Frontend-Data Contract 01 前端-数据契约 | design | design_only |
| D-FRONTEND/Frontend-Governance Contract 01 前端-治理契约 | Frontend-Governance Contract 01 前端-治理契约 | design | design_only | D-FRONTEND/Frontend-Governance Contract 01 前端-治理契约 | Frontend-Governance Contract 01 前端-治理契约 | design | design_only |
| D-FRONTEND/Frontend-Infrastructure Contract 01 前端-基础设施契约 | Frontend-Infrastructure Contract 01 前... | design | design_only | D-FRONTEND/Frontend-Infrastructure Contract 01 前端-基础设施契约 | Frontend-Infrastructure Contract 01 前... | design | design_only |
| D-FRONTEND/Frontend-Integration Contract 01 前端-集成契约 | Frontend-Integration Contract 01 前端-集成契约 | design | design_only | D-FRONTEND/Frontend-Integration Contract 01 前端-集成契约 | Frontend-Integration Contract 01 前端-集成契约 | design | design_only |
| D-FRONTEND/Frontend-Knowledge Contract 01 前端-知识契约 | Frontend-Knowledge Contract 01 前端-知识契约 | design | design_only | D-FRONTEND/Frontend-Knowledge Contract 01 前端-知识契约 | Frontend-Knowledge Contract 01 前端-知识契约 | design | design_only |
| D-FRONTEND/Frontend-ML Contract 01 前端-ML契约 | Frontend-ML Contract 01 前端-ML契约 | design | design_only | D-FRONTEND/Frontend-ML Contract 01 前端-ML契约 | Frontend-ML Contract 01 前端-ML契约 | design | design_only |
| D-FRONTEND/Frontend-Ops Contract 01 前端-运维契约 | Frontend-Ops Contract 01 前端-运维契约 | design | design_only | D-FRONTEND/Frontend-Ops Contract 01 前端-运维契约 | Frontend-Ops Contract 01 前端-运维契约 | design | design_only |
| D-FRONTEND/Frontend-Report Contract 01 前端-报告契约 | Frontend-Report Contract 01 前端-报告契约 | design | design_only | D-FRONTEND/Frontend-Report Contract 01 前端-报告契约 | Frontend-Report Contract 01 前端-报告契约 | design | design_only |
| D-FRONTEND/Frontend-Risk Contract 01 前端-风控契约 | Frontend-Risk Contract 01 前端-风控契约 | design | design_only | D-FRONTEND/Frontend-Risk Contract 01 前端-风控契约 | Frontend-Risk Contract 01 前端-风控契约 | design | design_only |
| D-FRONTEND/Frontend-Risk Contract 02 前端-风控契约 | Frontend-Risk Contract 02 前端-风控契约 | design | design_only | D-FRONTEND/Frontend-Risk Contract 02 前端-风控契约 | Frontend-Risk Contract 02 前端-风控契约 | design | design_only |
| D-FRONTEND/Frontend-Risk Contract 03 前端-风控契约 | Frontend-Risk Contract 03 前端-风控契约 | design | design_only | D-FRONTEND/Frontend-Risk Contract 03 前端-风控契约 | Frontend-Risk Contract 03 前端-风控契约 | design | design_only |
| D-FRONTEND/Frontend-Simulation Contract 01 前端-模拟契约 | Frontend-Simulation Contract 01 前端-模拟契约 | design | design_only | D-FRONTEND/Frontend-Simulation Contract 01 前端-模拟契约 | Frontend-Simulation Contract 01 前端-模拟契约 | design | design_only |
| D-FRONTEND/Frontend→Autonomy Interface 01 前端→自治接口 | Frontend→Autonomy Interface 01 前端→自治接口 | design | design_only | D-FRONTEND/Frontend→Autonomy Interface 01 前端→自治接口 | Frontend→Autonomy Interface 01 前端→自治接口 | design | design_only |
| D-FRONTEND/Frontend→Governance Interface 01 前端→治理接口 | Frontend→Governance Interface 01 前端→治理接口 | design | design_only | D-FRONTEND/Frontend→Governance Interface 01 前端→治理接口 | Frontend→Governance Interface 01 前端→治理接口 | design | design_only |
| D-FRONTEND/Frontend→Portfolio Interface 01 前端→组合接口 | Frontend→Portfolio Interface 01 前端→组合接口 | design | design_only | D-FRONTEND/Frontend→Portfolio Interface 01 前端→组合接口 | Frontend→Portfolio Interface 01 前端→组合接口 | design | design_only |
| D-FRONTEND/Generator 生成器 | Generator 生成器 | design | design_only | D-FRONTEND/Generator 生成器 | Generator 生成器 | design | design_only |
| D-FRONTEND/Graph Rendering Engine 图渲染引擎 | Graph Rendering Engine 图渲染引擎 | design | design_only | D-FRONTEND/Graph Rendering Engine 图渲染引擎 | Graph Rendering Engine 图渲染引擎 | design | design_only |
| D-FRONTEND/Gray Release Status 灰度发布状态 | Gray Release Status 灰度发布状态 | design | design_only | D-FRONTEND/Gray Release Status 灰度发布状态 | Gray Release Status 灰度发布状态 | design | design_only |
| D-FRONTEND/HITL Trigger Condition HITL触发条件 | HITL Trigger Condition HITL触发条件 | design | design_only | D-FRONTEND/HITL Trigger Condition HITL触发条件 | HITL Trigger Condition HITL触发条件 | design | design_only |
| D-FRONTEND/HealthDegraded 健康已降级 | HealthDegraded 健康已降级 | design | design_only | D-FRONTEND/HealthDegraded 健康已降级 | HealthDegraded 健康已降级 | design | design_only |
| D-FRONTEND/IS Stability Gate IS阶段稳定性门控 | IS Stability Gate IS阶段稳定性门控 | design | design_only | D-FRONTEND/IS Stability Gate IS阶段稳定性门控 | IS Stability Gate IS阶段稳定性门控 | design | design_only |
| D-FRONTEND/Impact Visualizer 影响可视化器 | Impact Visualizer 影响可视化器 | design | design_only | D-FRONTEND/Impact Visualizer 影响可视化器 | Impact Visualizer 影响可视化器 | design | design_only |
| D-FRONTEND/Integration API 集成API契约 | Integration API 集成API契约 | design | design_only | D-FRONTEND/Integration API 集成API契约 | Integration API 集成API契约 | design | design_only |
| D-FRONTEND/Interaction Controller 交互控制器 | Interaction Controller 交互控制器 | design | design_only | D-FRONTEND/Interaction Controller 交互控制器 | Interaction Controller 交互控制器 | design | design_only |
| D-FRONTEND/Interactive Analysis 交互式分析 | Interactive Analysis 交互式分析 | design | design_only | D-FRONTEND/Interactive Analysis 交互式分析 | Interactive Analysis 交互式分析 | design | design_only |
| D-FRONTEND/Judge 裁判器 | Judge 裁判器 | design | design_only | D-FRONTEND/Judge 裁判器 | Judge 裁判器 | design | design_only |
| D-FRONTEND/KGImpactAnalysis 知识图谱影响分析 | KGImpactAnalysis 知识图谱影响分析 | design | design_only | D-FRONTEND/KGImpactAnalysis 知识图谱影响分析 | KGImpactAnalysis 知识图谱影响分析 | design | design_only |
| D-FRONTEND/L08 HMI CLI 人机交互CLI | L08 HMI CLI 人机交互CLI | design | design_only | D-FRONTEND/L08 HMI CLI 人机交互CLI | L08 HMI CLI 人机交互CLI | design | design_only |
| D-FRONTEND/L08 HMI Notifications 人机交互通知 | L08 HMI Notifications 人机交互通知 | design | design_only | D-FRONTEND/L08 HMI Notifications 人机交互通知 | L08 HMI Notifications 人机交互通知 | design | design_only |
| D-FRONTEND/L08 HMI Orchestration 人机交互编排 | L08 HMI Orchestration 人机交互编排 | design | design_only | D-FRONTEND/L08 HMI Orchestration 人机交互编排 | L08 HMI Orchestration 人机交互编排 | design | design_only |
| D-FRONTEND/LP-021 Frontend Domain Substitute 前端域替代 | LP-021 Frontend Domain Substitute 前端域替代 | design | design_only | D-FRONTEND/LP-021 Frontend Domain Substitute 前端域替代 | LP-021 Frontend Domain Substitute 前端域替代 | design | design_only |
| D-FRONTEND/Large-Scale Graph Rendering Engine 大规模图渲染引擎 | Large-Scale Graph Rendering Engine 大规... | design | design_only | D-FRONTEND/Large-Scale Graph Rendering Engine 大规模图渲染引擎 | Large-Scale Graph Rendering Engine 大规... | design | design_only |
| D-FRONTEND/Latency Waterfall Chart 延迟瀑布图 | Latency Waterfall Chart 延迟瀑布图 | design | design_only | D-FRONTEND/Latency Waterfall Chart 延迟瀑布图 | Latency Waterfall Chart 延迟瀑布图 | design | design_only |
| D-FRONTEND/M5-S07 | M5-S07 | design | design_only | D-FRONTEND/M5-S07 | M5-S07 | design | design_only |
| D-FRONTEND/M6-S07 | M6-S07 | design | design_only | D-FRONTEND/M6-S07 | M6-S07 | design | design_only |
| D-FRONTEND/M7-NEW-06 | M7-NEW-06 | design | design_only | D-FRONTEND/M7-NEW-06 | M7-NEW-06 | design | design_only |
| D-FRONTEND/M7-NEW-07 | M7-NEW-07 | design | design_only | D-FRONTEND/M7-NEW-07 | M7-NEW-07 | design | design_only |
| D-FRONTEND/M7-S06 | M7-S06 | design | design_only | D-FRONTEND/M7-S06 | M7-S06 | design | design_only |
| D-FRONTEND/M8-S08 | M8-S08 | design | design_only | D-FRONTEND/M8-S08 | M8-S08 | design | design_only |
| D-FRONTEND/Manual Review Decision 人工审核决策 | Manual Review Decision 人工审核决策 | design | design_only | D-FRONTEND/Manual Review Decision 人工审核决策 | Manual Review Decision 人工审核决策 | design | design_only |
| D-FRONTEND/Manual Review Panel 人工审核面板 | Manual Review Panel 人工审核面板 | design | design_only | D-FRONTEND/Manual Review Panel 人工审核面板 | Manual Review Panel 人工审核面板 | design | design_only |
| D-FRONTEND/Manual Submit Interface 手动提交界面 | Manual Submit Interface 手动提交界面 | design | design_only | D-FRONTEND/Manual Submit Interface 手动提交界面 | Manual Submit Interface 手动提交界面 | design | design_only |
| D-FRONTEND/Manual Supplement Input 人工补充输入 | Manual Supplement Input 人工补充输入 | design | design_only | D-FRONTEND/Manual Supplement Input 人工补充输入 | Manual Supplement Input 人工补充输入 | design | design_only |
| D-FRONTEND/Mathematical Reflection Optimization 数学反思优化结果 | Mathematical Reflection Optimization ... | design | design_only | D-FRONTEND/Mathematical Reflection Optimization 数学反思优化结果 | Mathematical Reflection Optimization ... | design | design_only |
| D-FRONTEND/Mesh Visualizer 网格可视化器 | Mesh Visualizer 网格可视化器 | design | design_only | D-FRONTEND/Mesh Visualizer 网格可视化器 | Mesh Visualizer 网格可视化器 | design | design_only |
| D-FRONTEND/Mobile Dashboard 移动端仪表盘 | Mobile Dashboard 移动端仪表盘 | design | design_only | D-FRONTEND/Mobile Dashboard 移动端仪表盘 | Mobile Dashboard 移动端仪表盘 | design | design_only |
| D-FRONTEND/ModelDriftDetected 模型漂移已检测 | ModelDriftDetected 模型漂移已检测 | design | design_only | D-FRONTEND/ModelDriftDetected 模型漂移已检测 | ModelDriftDetected 模型漂移已检测 | design | design_only |
| D-FRONTEND/Module Output Monitoring 模块输出监控 | Module Output Monitoring 模块输出监控 | design | design_only | D-FRONTEND/Module Output Monitoring 模块输出监控 | Module Output Monitoring 模块输出监控 | design | design_only |
| D-FRONTEND/Monthly Risk Governance 月度风险治理 | Monthly Risk Governance 月度风险治理 | design | design_only | D-FRONTEND/Monthly Risk Governance 月度风险治理 | Monthly Risk Governance 月度风险治理 | design | design_only |
| D-FRONTEND/Monthly Risk Report 月度风险报告 | Monthly Risk Report 月度风险报告 | design | design_only | D-FRONTEND/Monthly Risk Report 月度风险报告 | Monthly Risk Report 月度风险报告 | design | design_only |
| D-FRONTEND/Multi-Scale Drift Level 多尺度漂移等级 | Multi-Scale Drift Level 多尺度漂移等级 | design | design_only | D-FRONTEND/Multi-Scale Drift Level 多尺度漂移等级 | Multi-Scale Drift Level 多尺度漂移等级 | design | design_only |
| D-FRONTEND/Natural Language Interface 自然语言界面 | Natural Language Interface 自然语言界面 | design | design_only | D-FRONTEND/Natural Language Interface 自然语言界面 | Natural Language Interface 自然语言界面 | design | design_only |
| D-FRONTEND/NotificationRouter 通知路由 | NotificationRouter 通知路由 | design | design_only | D-FRONTEND/NotificationRouter 通知路由 | NotificationRouter 通知路由 | design | design_only |
| D-FRONTEND/OOS Gate OOS阶段门控 | OOS Gate OOS阶段门控 | design | design_only | D-FRONTEND/OOS Gate OOS阶段门控 | OOS Gate OOS阶段门控 | design | design_only |
| D-FRONTEND/OTel Trace Renderer OTel追踪渲染器 | OTel Trace Renderer OTel追踪渲染器 | design | design_only | D-FRONTEND/OTel Trace Renderer OTel追踪渲染器 | OTel Trace Renderer OTel追踪渲染器 | design | design_only |
| D-FRONTEND/OTel追踪渲染器族 OTel Trace Renderers | OTel追踪渲染器族 OTel Trace Renderers | design | design_only | D-FRONTEND/OTel追踪渲染器族 OTel Trace Renderers | OTel追踪渲染器族 OTel Trace Renderers | design | design_only |
| D-FRONTEND/One-Click Quant Interface 一键量化交易界面 | One-Click Quant Interface 一键量化交易界面 | design | design_only | D-FRONTEND/One-Click Quant Interface 一键量化交易界面 | One-Click Quant Interface 一键量化交易界面 | design | design_only |
| D-FRONTEND/Orchestration Visualizer 编排可视化器 | Orchestration Visualizer 编排可视化器 | design | design_only | D-FRONTEND/Orchestration Visualizer 编排可视化器 | Orchestration Visualizer 编排可视化器 | design | design_only |
| D-FRONTEND/Phase 5 Activation Phase 5激活阶段 | Phase 5 Activation Phase 5激活阶段 | design | design_only | D-FRONTEND/Phase 5 Activation Phase 5激活阶段 | Phase 5 Activation Phase 5激活阶段 | design | design_only |
| D-FRONTEND/PlantUML Rendering PlantUML渲染 | PlantUML Rendering PlantUML渲染 | design | design_only | D-FRONTEND/PlantUML Rendering PlantUML渲染 | PlantUML Rendering PlantUML渲染 | design | design_only |
| D-FRONTEND/Real-time Dashboard 实时仪表盘 | Real-time Dashboard 实时仪表盘 | design | design_only | D-FRONTEND/Real-time Dashboard 实时仪表盘 | Real-time Dashboard 实时仪表盘 | design | design_only |
| D-FRONTEND/Real-time P&L 实时P&L | Real-time P&L 实时P&L | design | design_only | D-FRONTEND/Real-time P&L 实时P&L | Real-time P&L 实时P&L | design | design_only |
| D-FRONTEND/Real-time Renderer 实时渲染器 | Real-time Renderer 实时渲染器 | design | design_only | D-FRONTEND/Real-time Renderer 实时渲染器 | Real-time Renderer 实时渲染器 | design | design_only |
| D-FRONTEND/Real-time Rendering Enhancer 实时渲染增强器 | Real-time Rendering Enhancer 实时渲染增强器 | design | design_only | D-FRONTEND/Real-time Rendering Enhancer 实时渲染增强器 | Real-time Rendering Enhancer 实时渲染增强器 | design | design_only |
| D-FRONTEND/Real-time Updater 实时更新器 | Real-time Updater 实时更新器 | design | design_only | D-FRONTEND/Real-time Updater 实时更新器 | Real-time Updater 实时更新器 | design | design_only |
| D-FRONTEND/RealtimeDashboard 实时仪表盘 | RealtimeDashboard 实时仪表盘 | design | design_only | D-FRONTEND/RealtimeDashboard 实时仪表盘 | RealtimeDashboard 实时仪表盘 | design | design_only |
| D-FRONTEND/Report Visualization 报告可视化 | Report Visualization 报告可视化 | design | design_only | D-FRONTEND/Report Visualization 报告可视化 | Report Visualization 报告可视化 | design | design_only |
| D-FRONTEND/Representation Learning Drift Warning 表示学习漂移预警 | Representation Learning Drift Warning... | design | design_only | D-FRONTEND/Representation Learning Drift Warning 表示学习漂移预警 | Representation Learning Drift Warning... | design | design_only |
| D-FRONTEND/Result Renderer 结果渲染器 | Result Renderer 结果渲染器 | design | design_only | D-FRONTEND/Result Renderer 结果渲染器 | Result Renderer 结果渲染器 | design | design_only |
| D-FRONTEND/Risk Contagion Visualizer 风险传染可视化器 | Risk Contagion Visualizer 风险传染可视化器 | design | design_only | D-FRONTEND/Risk Contagion Visualizer 风险传染可视化器 | Risk Contagion Visualizer 风险传染可视化器 | design | design_only |
| D-FRONTEND/Risk Control System Role 风控系统角色 | Risk Control System Role 风控系统角色 | design | design_only | D-FRONTEND/Risk Control System Role 风控系统角色 | Risk Control System Role 风控系统角色 | design | design_only |
| D-FRONTEND/Robo-Advisor 智能投顾 | Robo-Advisor 智能投顾 | design | design_only | D-FRONTEND/Robo-Advisor 智能投顾 | Robo-Advisor 智能投顾 | design | design_only |
| D-FRONTEND/Saga Visualizer Saga可视化器 | Saga Visualizer Saga可视化器 | design | design_only | D-FRONTEND/Saga Visualizer Saga可视化器 | Saga Visualizer Saga可视化器 | design | design_only |
| D-FRONTEND/Search Locator 搜索定位器 | Search Locator 搜索定位器 | design | design_only | D-FRONTEND/Search Locator 搜索定位器 | Search Locator 搜索定位器 | design | design_only |
| D-FRONTEND/Security Dependency Visualizer 安全依赖可视化器 | Security Dependency Visualizer 安全依赖可视化器 | design | design_only | D-FRONTEND/Security Dependency Visualizer 安全依赖可视化器 | Security Dependency Visualizer 安全依赖可视化器 | design | design_only |
| D-FRONTEND/Signal Agent 信号Agent | Signal Agent 信号Agent | design | design_only | D-FRONTEND/Signal Agent 信号Agent | Signal Agent 信号Agent | design | design_only |
| D-FRONTEND/Simulation Observation Data 模拟盘观察数据 | Simulation Observation Data 模拟盘观察数据 | design | design_only | D-FRONTEND/Simulation Observation Data 模拟盘观察数据 | Simulation Observation Data 模拟盘观察数据 | design | design_only |
| D-FRONTEND/Strategy Management UI 策略管理界面 | Strategy Management UI 策略管理界面 | design | design_only | D-FRONTEND/Strategy Management UI 策略管理界面 | Strategy Management UI 策略管理界面 | design | design_only |
| D-FRONTEND/Streamlit Dashboard Streamlit轻量仪表盘 | Streamlit Dashboard Streamlit轻量仪表盘 | design | design_only | D-FRONTEND/Streamlit Dashboard Streamlit轻量仪表盘 | Streamlit Dashboard Streamlit轻量仪表盘 | design | design_only |
| D-FRONTEND/Streamlit Streamlit仪表盘 | Streamlit Streamlit仪表盘 | design | design_only | D-FRONTEND/Streamlit Streamlit仪表盘 | Streamlit Streamlit仪表盘 | design | design_only |
| D-FRONTEND/Stress Test 压力测试 | Stress Test 压力测试 | design | design_only | D-FRONTEND/Stress Test 压力测试 | Stress Test 压力测试 | design | design_only |
| D-FRONTEND/System Health Dashboard 系统健康仪表盘 | System Health Dashboard 系统健康仪表盘 | design | design_only | D-FRONTEND/System Health Dashboard 系统健康仪表盘 | System Health Dashboard 系统健康仪表盘 | design | design_only |
| D-FRONTEND/SystemDegraded 系统已降级 | SystemDegraded 系统已降级 | design | design_only | D-FRONTEND/SystemDegraded 系统已降级 | SystemDegraded 系统已降级 | design | design_only |
| D-FRONTEND/SystemHealthVisualization 系统健康可视化 | SystemHealthVisualization 系统健康可视化 | design | design_only | D-FRONTEND/SystemHealthVisualization 系统健康可视化 | SystemHealthVisualization 系统健康可视化 | design | design_only |
| D-FRONTEND/Time Dimension Animator 时间维度动画器 | Time Dimension Animator 时间维度动画器 | design | design_only | D-FRONTEND/Time Dimension Animator 时间维度动画器 | Time Dimension Animator 时间维度动画器 | design | design_only |
| D-FRONTEND/Time Travel Controller 时间旅行控制器 | Time Travel Controller 时间旅行控制器 | design | design_only | D-FRONTEND/Time Travel Controller 时间旅行控制器 | Time Travel Controller 时间旅行控制器 | design | design_only |
| D-FRONTEND/Trace Anomaly ML Detector Trace异常ML检测器 | Trace Anomaly ML Detector Trace异常ML检测器 | design | design_only | D-FRONTEND/Trace Anomaly ML Detector Trace异常ML检测器 | Trace Anomaly ML Detector Trace异常ML检测器 | design | design_only |
| D-FRONTEND/Trace Reporter 追踪报告器 | Trace Reporter 追踪报告器 | design | design_only | D-FRONTEND/Trace Reporter 追踪报告器 | Trace Reporter 追踪报告器 | design | design_only |
| D-FRONTEND/Trace Topology Auto-Extractor Trace拓扑自动提取器 | Trace Topology Auto-Extractor Trace拓扑... | design | design_only | D-FRONTEND/Trace Topology Auto-Extractor Trace拓扑自动提取器 | Trace Topology Auto-Extractor Trace拓扑... | design | design_only |
| D-FRONTEND/Trace Visualizer 追踪可视化器 | Trace Visualizer 追踪可视化器 | design | design_only | D-FRONTEND/Trace Visualizer 追踪可视化器 | Trace Visualizer 追踪可视化器 | design | design_only |
| D-FRONTEND/Traceability Visualizer 追溯可视化器 | Traceability Visualizer 追溯可视化器 | design | design_only | D-FRONTEND/Traceability Visualizer 追溯可视化器 | Traceability Visualizer 追溯可视化器 | design | design_only |
| D-FRONTEND/Trace到依赖图映射器 Trace to DepGraph Mapper | Trace到依赖图映射器 Trace to DepGraph Mapper | design | design_only | D-FRONTEND/Trace到依赖图映射器 Trace to DepGraph Mapper | Trace到依赖图映射器 Trace to DepGraph Mapper | design | design_only |
| D-FRONTEND/Trader Role 交易员角色 | Trader Role 交易员角色 | design | design_only | D-FRONTEND/Trader Role 交易员角色 | Trader Role 交易员角色 | design | design_only |
| D-FRONTEND/Trading Architecture Visualizer 交易架构可视化器 | Trading Architecture Visualizer 交易架构可视化器 | design | design_only | D-FRONTEND/Trading Architecture Visualizer 交易架构可视化器 | Trading Architecture Visualizer 交易架构可视化器 | design | design_only |
| D-FRONTEND/Trading Chatbot 交易智能客服 | Trading Chatbot 交易智能客服 | design | design_only | D-FRONTEND/Trading Chatbot 交易智能客服 | Trading Chatbot 交易智能客服 | design | design_only |
| D-FRONTEND/Trading Monitoring Dashboard 交易监控仪表盘 | Trading Monitoring Dashboard 交易监控仪表盘 | design | design_only | D-FRONTEND/Trading Monitoring Dashboard 交易监控仪表盘 | Trading Monitoring Dashboard 交易监控仪表盘 | design | design_only |
| D-FRONTEND/Triple Semantic Consistency Display 三重语义一致性展示 | Triple Semantic Consistency Display 三... | design | design_only | D-FRONTEND/Triple Semantic Consistency Display 三重语义一致性展示 | Triple Semantic Consistency Display 三... | design | design_only |
| D-FRONTEND/Ultra-Large Graph Interaction Optimizer 超大规模图交互优化器 | Ultra-Large Graph Interaction Optimiz... | design | design_only | D-FRONTEND/Ultra-Large Graph Interaction Optimizer 超大规模图交互优化器 | Ultra-Large Graph Interaction Optimiz... | design | design_only |
| D-FRONTEND/UserAction 用户操作 | UserAction 用户操作 | design | design_only | D-FRONTEND/UserAction 用户操作 | UserAction 用户操作 | design | design_only |
| D-FRONTEND/VR Renderer VR渲染器 | VR Renderer VR渲染器 | design | design_only | D-FRONTEND/VR Renderer VR渲染器 | VR Renderer VR渲染器 | design | design_only |
| D-FRONTEND/VaR Value at Risk 风险价值 | VaR Value at Risk 风险价值 | design | design_only | D-FRONTEND/VaR Value at Risk 风险价值 | VaR Value at Risk 风险价值 | design | design_only |
| D-FRONTEND/WFA Gate WFA阶段门控 | WFA Gate WFA阶段门控 | design | design_only | D-FRONTEND/WFA Gate WFA阶段门控 | WFA Gate WFA阶段门控 | design | design_only |
| D-FRONTEND/Waterfall Interaction Engine 瀑布图交互引擎 | Waterfall Interaction Engine 瀑布图交互引擎 | design | design_only | D-FRONTEND/Waterfall Interaction Engine 瀑布图交互引擎 | Waterfall Interaction Engine 瀑布图交互引擎 | design | design_only |
| D-FRONTEND/WeChat Bot 微信机器人 | WeChat Bot 微信机器人 | design | design_only | D-FRONTEND/WeChat Bot 微信机器人 | WeChat Bot 微信机器人 | design | design_only |
| D-FRONTEND/WeChat Webhook 微信Webhook | WeChat Webhook 微信Webhook | design | design_only | D-FRONTEND/WeChat Webhook 微信Webhook | WeChat Webhook 微信Webhook | design | design_only |
| D-FRONTEND/WebGPU Large-Scale Renderer WebGPU大规模渲染器 | WebGPU Large-Scale Renderer WebGPU大规模渲染器 | design | design_only | D-FRONTEND/WebGPU Large-Scale Renderer WebGPU大规模渲染器 | WebGPU Large-Scale Renderer WebGPU大规模渲染器 | design | design_only |
| D-FRONTEND/Weekly Risk Deep Dive 周度风险深度 | Weekly Risk Deep Dive 周度风险深度 | design | design_only | D-FRONTEND/Weekly Risk Deep Dive 周度风险深度 | Weekly Risk Deep Dive 周度风险深度 | design | design_only |
| D-FRONTEND/Weekly Risk Report 周度风险报告 | Weekly Risk Report 周度风险报告 | design | design_only | D-FRONTEND/Weekly Risk Report 周度风险报告 | Weekly Risk Report 周度风险报告 | design | design_only |

> (仅显示前 200 个模块，共 237 个)

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_FRONTEND["D-FRONTEND 前端"]
        D_FRONTEND_3D_Force_Directed_Layout_3D["3D Force-Directed Layout 3D力导向布局器 design"]
        D_FRONTEND_4_Level_Risk_Decision_4["4-Level Risk Decision 4级风控决策 design"]
        D_FRONTEND_AI_Agent_AI_Agent_Call_Chain_Tracer["AI Agent调用链追踪器 AI Agent Call Chain Tracer design"]
        D_FRONTEND_AI_Autonomy_Dashboard_AI["AI Autonomy Dashboard AI自治仪表盘 design"]
        D_FRONTEND_AI_Collection_Result_Display_AI["AI Collection Result Display AI采集结果展示 design"]
        D_FRONTEND_AI_Model_HR_Dashboard_AI_HR["AI Model HR Dashboard AI模型HR管理面板 design"]
        D_FRONTEND_AI_Role_AI["AI Role AI角色 design"]
        D_FRONTEND_AI_Driven_Dependency_Explorer_AI["AI-Driven Dependency Explorer AI驱动依赖图探索器 design"]
        D_FRONTEND_API_Dependency_Visualizer_API["API Dependency Visualizer API依赖可视化器 design"]
        D_FRONTEND_API_Gateway_Proxy_API["API Gateway Proxy API网关代理 design"]
        D_FRONTEND_API_Gateway_UI_API["API Gateway UI API网关界面 design"]
        D_FRONTEND_AST_Sandbox_Validation_Result_AST["AST Sandbox Validation Result AST沙箱验证结果 design"]
        D_FRONTEND_Administrator_Role["Administrator Role 管理员角色 design"]
        D_FRONTEND_Adversarial_Test_Result["Adversarial Test Result 对抗性测试结果 design"]
        D_FRONTEND_Agent_Behavior_Monitoring_Agent["Agent Behavior Monitoring Agent行为监控 design"]
        D_FRONTEND_Agent_Dependency_Heatmap_Agent["Agent Dependency Heatmap Agent依赖热力图 design"]
        D_FRONTEND_Alert_Notification_UI["Alert Notification UI 告警通知界面 design"]
        D_FRONTEND_Alert_Output_Alert["Alert Output Alert产出 design"]
        D_FRONTEND_AlertTriggered["AlertTriggered 告警已触发 design"]
        D_FRONTEND_AlertVisualization["AlertVisualization 告警可视化 design"]
        D_FRONTEND_Anomaly_Propagation_3D_Visualizer_3D["Anomaly Propagation 3D Visualizer 异常传播3D可视化器 design"]
        D_FRONTEND_Approval_Interface_Security["Approval Interface Security 审批界面安全约束 design"]
        D_FRONTEND_Approval_Workflow_UI["Approval Workflow UI 审批流程界面 design"]
        D_FRONTEND_ApprovalRequest_Output_ApprovalRequest["ApprovalRequest Output ApprovalRequest产出 design"]
        D_FRONTEND_ApprovalRequested["ApprovalRequested 审批已请求 design"]
        D_FRONTEND_ApprovalWorkflowUI_UI["ApprovalWorkflowUI 审批工作流UI design"]
        D_FRONTEND_Architecture_Doc_Auto_Generator["Architecture Doc Auto-Generator 架构文档自动生成器 design"]
        D_FRONTEND_Auto_Layout_Optimizer["Auto-Layout Optimizer 自动布局优化器 design"]
        D_FRONTEND_Backtest_Result_Summary["Backtest Result Summary 回测结果摘要 design"]
        D_FRONTEND_BacktestPassed["BacktestPassed 回测已通过 design"]
    end
    D_FRONTEND_API_Gateway_UI_API -.->|import_depends| D_FRONTEND_Approval_Workflow_UI
    D_FRONTEND_AI_Model_HR_Dashboard_AI_HR -.->|import_depends| D_FRONTEND_API_Gateway_Proxy_API
    D_FRONTEND_AI_Model_HR_Dashboard_AI_HR -.->|contract| D_FRONTEND_Approval_Interface_Security
    D_FRONTEND_AlertTriggered -.->|event| D_FRONTEND_ApprovalWorkflowUI_UI
    D_FRONTEND_Auto_Layout_Optimizer -.->|import_depends| D_FRONTEND_Architecture_Doc_Auto_Generator
    D_FRONTEND_Alert_Output_Alert -.->|import_depends| D_FRONTEND_ApprovalRequest_Output_ApprovalRequest
    D_REPORTING["D-REPORTING design"]
    D_FRONTEND_AlertVisualization -.->|event| D_REPORTING
    D_INTEGRATION["D-INTEGRATION design"]
    D_FRONTEND_AlertVisualization -.->|event| D_INTEGRATION
    D_SIGNAL["D-SIGNAL design"]
    D_FRONTEND_AlertVisualization -.->|config_depends| D_SIGNAL
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_FRONTEND_AlertVisualization -.->|config_depends| D_INFRA_RUNTIME
    D_FRONTEND_API_Gateway_UI_API -.->|event| D_INTEGRATION
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_FRONTEND_Approval_Workflow_UI -.->|data| D_KNOWLEDGE
    D_RISK["D-RISK design"]
    D_FRONTEND_Approval_Workflow_UI -.->|contract| D_RISK
    D_EX_CORE["D-EX_CORE design"]
    D_FRONTEND_AI_Model_HR_Dashboard_AI_HR -.->|event| D_EX_CORE
    D_MKT_DATA["D-MKT_DATA design"]
    D_FRONTEND_AI_Model_HR_Dashboard_AI_HR -.->|config_depends| D_MKT_DATA
    D_FACTOR["D-FACTOR design"]
    D_FRONTEND_AI_Model_HR_Dashboard_AI_HR -.->|contract| D_FACTOR
    D_OPS["D-OPS design"]
    D_FRONTEND_AI_Model_HR_Dashboard_AI_HR -.->|event| D_OPS
    D_FRONTEND_API_Gateway_Proxy_API -.->|event| D_FACTOR
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_FRONTEND_API_Gateway_Proxy_API -.->|event| D_INTELLIGENCE
    D_FRONTEND_AI_Agent_AI_Agent_Call_Chain_Tracer -.->|contract| D_REPORTING
    D_FRONTEND_AI_Agent_AI_Agent_Call_Chain_Tracer -.->|contract| D_MKT_DATA
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_FRONTEND_API_Gateway_UI_API
    D_COMPLIANCE -.->|event| D_FRONTEND_ApprovalRequested
    D_COMPLIANCE -.->|contract| D_FRONTEND_ApprovalRequested
    D_COMPLIANCE -.->|event| D_FRONTEND_Agent_Dependency_Heatmap_Agent
    D_COMPLIANCE -.->|data| D_FRONTEND_Anomaly_Propagation_3D_Visualizer_3D
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_FRONTEND_3D_Force_Directed_Layout_3D,D_FRONTEND_4_Level_Risk_Decision_4,D_FRONTEND_AI_Agent_AI_Agent_Call_Chain_Tracer,D_FRONTEND_AI_Autonomy_Dashboard_AI,D_FRONTEND_AI_Collection_Result_Display_AI,D_FRONTEND_AI_Model_HR_Dashboard_AI_HR,D_FRONTEND_AI_Role_AI,D_FRONTEND_AI_Driven_Dependency_Explorer_AI,D_FRONTEND_API_Dependency_Visualizer_API,D_FRONTEND_API_Gateway_Proxy_API,D_FRONTEND_API_Gateway_UI_API,D_FRONTEND_AST_Sandbox_Validation_Result_AST,D_FRONTEND_Administrator_Role,D_FRONTEND_Adversarial_Test_Result,D_FRONTEND_Agent_Behavior_Monitoring_Agent,D_FRONTEND_Agent_Dependency_Heatmap_Agent,D_FRONTEND_Alert_Notification_UI,D_FRONTEND_Alert_Output_Alert,D_FRONTEND_AlertTriggered,D_FRONTEND_AlertVisualization,D_FRONTEND_Anomaly_Propagation_3D_Visualizer_3D,D_FRONTEND_Approval_Interface_Security,D_FRONTEND_Approval_Workflow_UI,D_FRONTEND_ApprovalRequest_Output_ApprovalRequest,D_FRONTEND_ApprovalRequested,D_FRONTEND_ApprovalWorkflowUI_UI,D_FRONTEND_Architecture_Doc_Auto_Generator,D_FRONTEND_Auto_Layout_Optimizer,D_FRONTEND_Backtest_Result_Summary,D_FRONTEND_BacktestPassed design
    class D_REPORTING,D_INTEGRATION,D_SIGNAL,D_INFRA_RUNTIME,D_KNOWLEDGE,D_RISK,D_EX_CORE,D_MKT_DATA,D_FACTOR,D_OPS,D_INTELLIGENCE,D_COMPLIANCE external_design
```

> (依赖图最多显示前 30 个节点，共 237 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-RISK | 47 | event,config_depends,data,contract | D-RISK | 47 | event,config_depends,data,contract |
| D-INTEGRATION | 34 | event,contract,data,config_depends | D-INTEGRATION | 34 | event,contract,data,config_depends |
| D-SECURITY | 29 | contract,event,data,config_depends | D-SECURITY | 29 | contract,event,data,config_depends |
| D-SIGNAL | 28 | config_depends,event,data,contract | D-SIGNAL | 28 | config_depends,event,data,contract |
| D-AUTONOMY_CORE | 25 | data,contract,config_depends,event | D-AUTONOMY_CORE | 25 | data,contract,config_depends,event |
| D-INFRA_OPS | 23 | import_depends,contract,config_depends,data,event | D-INFRA_OPS | 23 | import_depends,contract,config_depends,data,event |
| D-GOVERNANCE | 23 | import_depends,data,contract,config_depends,event | D-GOVERNANCE | 23 | import_depends,data,contract,config_depends,event |
| D-FACTOR | 22 | event,config_depends,contract,data | D-FACTOR | 22 | event,config_depends,contract,data |
| D-OPS | 21 | contract,import_depends,event,config_depends,data | D-OPS | 21 | contract,import_depends,event,config_depends,data |
| D-MKT_DATA | 15 | config_depends,data,contract,event | D-MKT_DATA | 15 | config_depends,data,contract,event |
| D-PF_CORE | 11 | contract,event,config_depends,data | D-PF_CORE | 11 | contract,event,config_depends,data |
| D-REPORTING | 10 | data,event,contract,config_depends,domain_dependency | D-REPORTING | 10 | data,event,contract,config_depends,domain_dependency |
| D-AUTONOMY_PERM | 10 | data,contract,event | D-AUTONOMY_PERM | 10 | data,contract,event |
| D-INTELLIGENCE | 9 | contract,event,data | D-INTELLIGENCE | 9 | contract,event,data |
| D-SIMULATION | 7 | data,config_depends,contract | D-SIMULATION | 7 | data,config_depends,contract |
| D-EX_SOR | 7 | data,config_depends,contract | D-EX_SOR | 7 | data,config_depends,contract |
| D-KNOWLEDGE | 6 | contract,data,event | D-KNOWLEDGE | 6 | contract,data,event |
| D-INFRA_RUNTIME | 6 | config_depends,data,contract | D-INFRA_RUNTIME | 6 | config_depends,data,contract |
| D-SELL_DECISION | 5 | contract,data,config_depends | D-SELL_DECISION | 5 | contract,data,config_depends |
| D-PF_ALLOC | 5 | contract,config_depends,data | D-PF_ALLOC | 5 | contract,config_depends,data |
| D-EX_CORE | 5 | event,data,config_depends | D-EX_CORE | 5 | event,data,config_depends |
| D-DATA_ENG | 5 | event,data,contract | D-DATA_ENG | 5 | event,data,contract |
| D-TRADING | 4 | contract,event,config_depends | D-TRADING | 4 | contract,event,config_depends |
| D-ML_TRAIN | 4 | contract,event | D-ML_TRAIN | 4 | contract,event |
| D-ML_SERVE | 4 | event,data,contract | D-ML_SERVE | 4 | event,data,contract |
| D-POSITION | 2 | config_depends,contract | D-POSITION | 2 | config_depends,contract |
| D-SHARED | 1 | import_depends | D-SHARED | 1 | import_depends |
| D-ALT_DATA | 1 | contract | D-ALT_DATA | 1 | contract |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-COMPLIANCE | 52 | contract,event,data,config_depends | D-COMPLIANCE | 52 | contract,event,data,config_depends |
| D-GOVERNANCE | 11 | test_depends | D-GOVERNANCE | 11 | test_depends |
| D-DATA_SEC | 1 | event | D-DATA_SEC | 1 | event |
| D-DATA_GOV | 1 | data | D-DATA_GOV | 1 | data |
| D-CROSS_ASSET | 1 | contract | D-CROSS_ASSET | 1 | contract |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
