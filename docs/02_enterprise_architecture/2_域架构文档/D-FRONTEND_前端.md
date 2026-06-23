---
doc_type: domain_architecture_doc
title: D-FRONTEND 前端架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-FRONTEND 前端架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-FRONTEND |
| 域名称 | 前端 |
| 架构层 | L1_platform |
| 模块总数 | 237 |
| 设计态模块 | 213 |
| 原型态模块 | 11 |
| 生产态模块 | 7 |
| 容量 | 7/150 (正常) |
| 描述 | Web界面、可视化看板、交互组件。人机交互入口。 |

## 模块清单

共 237 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-FRONTEND/3D Force-Directed Layout 3D力导向布局器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/4-Level Risk Decision 4级风控决策 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AI Agent调用链追踪器 AI Agent Call Chain Tracer |  | design_only | design | 0 | 0 |
| D-FRONTEND/AI Autonomy Dashboard AI自治仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AI Collection Result Display AI采集结果展示 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AI Model HR Dashboard AI模型HR管理面板 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AI Role AI角色 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AI-Driven Dependency Explorer AI驱动依赖图探索器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/API Dependency Visualizer API依赖可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/API Gateway Proxy API网关代理 |  | design_only | design | 0 | 0 |
| D-FRONTEND/API Gateway UI API网关界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AST Sandbox Validation Result AST沙箱验证结果 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Administrator Role 管理员角色 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Adversarial Test Result 对抗性测试结果 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Agent Behavior Monitoring Agent行为监控 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Agent Dependency Heatmap Agent依赖热力图 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Alert Notification UI 告警通知界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Alert Output Alert产出 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AlertTriggered 告警已触发 |  | design_only | design | 0 | 0 |
| D-FRONTEND/AlertVisualization 告警可视化 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Anomaly Propagation 3D Visualizer 异常传播3D可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Approval Interface Security 审批界面安全约束 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Approval Workflow UI 审批流程界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/ApprovalRequest Output ApprovalRequest产出 |  | design_only | design | 0 | 0 |
| D-FRONTEND/ApprovalRequested 审批已请求 |  | design_only | design | 0 | 0 |
| D-FRONTEND/ApprovalWorkflowUI 审批工作流UI |  | design_only | design | 0 | 0 |
| D-FRONTEND/Architecture Doc Auto-Generator 架构文档自动生成器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Auto-Layout Optimizer 自动布局优化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Backtest Result Summary 回测结果摘要 |  | design_only | design | 0 | 0 |
| D-FRONTEND/BacktestPassed 回测已通过 |  | design_only | design | 0 | 0 |
| D-FRONTEND/CLI Interface 命令行交互入口 |  | design_only | design | 0 | 0 |
| D-FRONTEND/CQRS Visualization CQRS可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/CVaR Conditional VaR 条件风险价值 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Call Graph Visualizer 调用图可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Capacity Dashboard 容量仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Chart Engine 图表引擎 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Cluster Heatmap 集群热力图 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Code Comparison View 代码对比视图 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Code Review Panel 代码审查面板 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collaboration Annotation 协作批注 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collaboration Annotation 报告协作批注 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collaboration Watermark 协作平台水印 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collaboration Watermark 协作版报告水印 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collaborative Dependency Annotator 协作依赖图标注器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collaborative Workspace 协作工作区 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collection Progress Tracking 采集进度追踪 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Collection Strategy Adjustment Log 采集策略调整日志 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Conformal VaR 共形VaR |  | design_only | design | 0 | 0 |
| D-FRONTEND/Convergence Status Indicator 收敛状态指示 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Coupling Heatmap 耦合热力图 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Critic Criticism Display Critic批评展示 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Critic 批评器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Cross-Service Trace Correlator 跨服务Trace关联器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Custom Chart Builder 自定义图表 |  | design_only | design | 0 | 0 |
| D-FRONTEND/D-FRONTEND 前端 |  | design_only | design | 0 | 0 |
| D-FRONTEND/D-PORTFOLIO Domain 组合域 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Daily Risk Report 日度风险报告 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Daily Risk Summary 日度风险摘要 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Dashboard Framework 仪表盘框架 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Dashboard Output Dashboard产出 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Dashboard 仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/DashboardUpdated 仪表盘已更新 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Decision Gate Progress 决策门控进度 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Decision Gate State Machine 决策门控状态机 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Decision Tree Visualizer 决策树可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Degradation Status Dashboard 降级状态仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Density-Aware VaR 密度感知VaR |  | design_only | design | 0 | 0 |
| D-FRONTEND/Dependency Diff Viewer 依赖图差异查看器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Dependency Graph LOD Engine 依赖图LOD引擎 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Dependency Timeline Player 依赖图时间线播放器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Developer Dashboard 开发者仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Drift Detection Status Panel 漂移检测状态面板 |  | design_only | design | 0 | 0 |
| D-FRONTEND/E-SIM-04 BacktestPassed 回测通过 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Effect Evaluation Report 效果评估报告 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Effect Metric Trend 效果指标趋势 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Email SMTP 邮件SMTP |  | design_only | design | 0 | 0 |
| D-FRONTEND/End-to-End Trace Visualizer 端到端追踪可视化 |  | design_only | design | 0 | 0 |
| D-FRONTEND/EndToEndTraceVisualizer 端到端追踪可视化 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Endpoint Refiner 端点级细化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/EscalationTriggered 升级已触发 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Event Risk Flash 事件风险快报 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Event Risk Report 事件风险报告 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Execution Agent 执行Agent |  | design_only | design | 0 | 0 |
| D-FRONTEND/Explainable Design Display 可解释设计展示 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Exporter 导出器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/ExternalCommand 外部指令 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Feature Lineage Visualizer 特征血缘可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Feishu Bot 飞书机器人 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Feishu REST Webhook 飞书REST Webhook |  | design_only | design | 0 | 0 |
| D-FRONTEND/Force-Directed GPU Accelerator 力导向GPU加速器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend Domain 前端域 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Autonomy Contract 01 前端-自治权限契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Data Contract 01 前端-数据契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Governance Contract 01 前端-治理契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Infrastructure Contract 01 前端-基础设施契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Integration Contract 01 前端-集成契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Knowledge Contract 01 前端-知识契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-ML Contract 01 前端-ML契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Ops Contract 01 前端-运维契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Report Contract 01 前端-报告契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Risk Contract 01 前端-风控契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Risk Contract 02 前端-风控契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Risk Contract 03 前端-风控契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend-Simulation Contract 01 前端-模拟契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend→Autonomy Interface 01 前端→自治接口 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend→Governance Interface 01 前端→治理接口 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Frontend→Portfolio Interface 01 前端→组合接口 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Generator 生成器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Graph Rendering Engine 图渲染引擎 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Gray Release Status 灰度发布状态 |  | design_only | design | 0 | 0 |
| D-FRONTEND/HITL Trigger Condition HITL触发条件 |  | design_only | design | 0 | 0 |
| D-FRONTEND/HealthDegraded 健康已降级 |  | design_only | design | 0 | 0 |
| D-FRONTEND/IS Stability Gate IS阶段稳定性门控 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Impact Visualizer 影响可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Integration API 集成API契约 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Interaction Controller 交互控制器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Interactive Analysis 交互式分析 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Judge 裁判器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/KGImpactAnalysis 知识图谱影响分析 |  | design_only | design | 0 | 0 |
| D-FRONTEND/L08 HMI CLI 人机交互CLI |  | design_only | design | 0 | 0 |
| D-FRONTEND/L08 HMI Notifications 人机交互通知 |  | design_only | design | 0 | 0 |
| D-FRONTEND/L08 HMI Orchestration 人机交互编排 |  | design_only | design | 0 | 0 |
| D-FRONTEND/LP-021 Frontend Domain Substitute 前端域替代 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Large-Scale Graph Rendering Engine 大规模图渲染引擎 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Latency Waterfall Chart 延迟瀑布图 |  | design_only | design | 0 | 0 |
| D-FRONTEND/M5-S07 |  | design_only | design | 0 | 0 |
| D-FRONTEND/M6-S07 |  | design_only | design | 0 | 0 |
| D-FRONTEND/M7-NEW-06 |  | design_only | design | 0 | 0 |
| D-FRONTEND/M7-NEW-07 |  | design_only | design | 0 | 0 |
| D-FRONTEND/M7-S06 |  | design_only | design | 0 | 0 |
| D-FRONTEND/M8-S08 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Manual Review Decision 人工审核决策 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Manual Review Panel 人工审核面板 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Manual Submit Interface 手动提交界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Manual Supplement Input 人工补充输入 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Mathematical Reflection Optimization 数学反思优化结果 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Mesh Visualizer 网格可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Mobile Dashboard 移动端仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/ModelDriftDetected 模型漂移已检测 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Module Output Monitoring 模块输出监控 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Monthly Risk Governance 月度风险治理 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Monthly Risk Report 月度风险报告 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Multi-Scale Drift Level 多尺度漂移等级 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Natural Language Interface 自然语言界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/NotificationRouter 通知路由 |  | design_only | design | 0 | 0 |
| D-FRONTEND/OOS Gate OOS阶段门控 |  | design_only | design | 0 | 0 |
| D-FRONTEND/OTel Trace Renderer OTel追踪渲染器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/OTel追踪渲染器族 OTel Trace Renderers |  | design_only | design | 0 | 0 |
| D-FRONTEND/One-Click Quant Interface 一键量化交易界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Orchestration Visualizer 编排可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Phase 5 Activation Phase 5激活阶段 |  | design_only | design | 0 | 0 |
| D-FRONTEND/PlantUML Rendering PlantUML渲染 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Real-time Dashboard 实时仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Real-time P&L 实时P&L |  | design_only | design | 0 | 0 |
| D-FRONTEND/Real-time Renderer 实时渲染器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Real-time Rendering Enhancer 实时渲染增强器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Real-time Updater 实时更新器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/RealtimeDashboard 实时仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Report Visualization 报告可视化 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Representation Learning Drift Warning 表示学习漂移预警 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Result Renderer 结果渲染器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Risk Contagion Visualizer 风险传染可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Risk Control System Role 风控系统角色 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Robo-Advisor 智能投顾 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Saga Visualizer Saga可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Search Locator 搜索定位器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Security Dependency Visualizer 安全依赖可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Signal Agent 信号Agent |  | design_only | design | 0 | 0 |
| D-FRONTEND/Simulation Observation Data 模拟盘观察数据 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Strategy Management UI 策略管理界面 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Streamlit Dashboard Streamlit轻量仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Streamlit Streamlit仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Stress Test 压力测试 |  | design_only | design | 0 | 0 |
| D-FRONTEND/System Health Dashboard 系统健康仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/SystemDegraded 系统已降级 |  | design_only | design | 0 | 0 |
| D-FRONTEND/SystemHealthVisualization 系统健康可视化 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Time Dimension Animator 时间维度动画器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Time Travel Controller 时间旅行控制器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trace Anomaly ML Detector Trace异常ML检测器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trace Reporter 追踪报告器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trace Topology Auto-Extractor Trace拓扑自动提取器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trace Visualizer 追踪可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Traceability Visualizer 追溯可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trace到依赖图映射器 Trace to DepGraph Mapper |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trader Role 交易员角色 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trading Architecture Visualizer 交易架构可视化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trading Chatbot 交易智能客服 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Trading Monitoring Dashboard 交易监控仪表盘 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Triple Semantic Consistency Display 三重语义一致性展示 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Ultra-Large Graph Interaction Optimizer 超大规模图交互优化器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/UserAction 用户操作 |  | design_only | design | 0 | 0 |
| D-FRONTEND/VR Renderer VR渲染器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/VaR Value at Risk 风险价值 |  | design_only | design | 0 | 0 |
| D-FRONTEND/WFA Gate WFA阶段门控 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Waterfall Interaction Engine 瀑布图交互引擎 |  | design_only | design | 0 | 0 |
| D-FRONTEND/WeChat Bot 微信机器人 |  | design_only | design | 0 | 0 |
| D-FRONTEND/WeChat Webhook 微信Webhook |  | design_only | design | 0 | 0 |
| D-FRONTEND/WebGPU Large-Scale Renderer WebGPU大规模渲染器 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Weekly Risk Deep Dive 周度风险深度 |  | design_only | design | 0 | 0 |
| D-FRONTEND/Weekly Risk Report 周度风险报告 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 237 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 47 | event,config_depends,data,contract |
| D-INTEGRATION | 34 | event,contract,data,config_depends |
| D-SECURITY | 29 | contract,event,data,config_depends |
| D-SIGNAL | 28 | config_depends,event,data,contract |
| D-AUTONOMY_CORE | 25 | data,contract,config_depends,event |
| D-INFRA_OPS | 23 | import_depends,contract,config_depends,data,event |
| D-GOVERNANCE | 23 | import_depends,data,contract,config_depends,event |
| D-FACTOR | 22 | event,config_depends,contract,data |
| D-OPS | 21 | contract,import_depends,event,config_depends,data |
| D-MKT_DATA | 15 | config_depends,data,contract,event |
| D-PF_CORE | 11 | contract,event,config_depends,data |
| D-REPORTING | 10 | data,event,contract,config_depends,domain_dependency |
| D-AUTONOMY_PERM | 10 | data,contract,event |
| D-INTELLIGENCE | 9 | contract,event,data |
| D-SIMULATION | 7 | data,config_depends,contract |
| D-EX_SOR | 7 | data,config_depends,contract |
| D-KNOWLEDGE | 6 | contract,data,event |
| D-INFRA_RUNTIME | 6 | config_depends,data,contract |
| D-SELL_DECISION | 5 | contract,data,config_depends |
| D-PF_ALLOC | 5 | contract,config_depends,data |
| D-EX_CORE | 5 | event,data,config_depends |
| D-DATA_ENG | 5 | event,data,contract |
| D-TRADING | 4 | contract,event,config_depends |
| D-ML_TRAIN | 4 | contract,event |
| D-ML_SERVE | 4 | event,data,contract |
| D-POSITION | 2 | config_depends,contract |
| D-SHARED | 1 | import_depends |
| D-ALT_DATA | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 52 | contract,event,data,config_depends |
| D-GOVERNANCE | 11 | test_depends |
| D-DATA_SEC | 1 | event |
| D-DATA_GOV | 1 | data |
| D-CROSS_ASSET | 1 | contract |

## 域内依赖图

详见 [d_frontend_dependency.mmd](d_frontend_dependency.mmd)
