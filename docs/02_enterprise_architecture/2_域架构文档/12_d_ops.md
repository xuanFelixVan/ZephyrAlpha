---
doc_type: domain_architecture_doc
title: D-OPS feedback-loop架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 12_d_ops 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 12 | Number | 12 |
| 域ID | D-OPS | Domain ID | D-OPS |
| 域名称 | feedback-loop | Domain Name | feedback-loop |
| 层级 | L1_platform | Layer | L1_platform |
| 模块数 | 697 | Module Count | 697 |
| 域内依赖 | 602 | Internal Dependencies | 602 |
| 跨域入边 | 558 | Cross-domain Incoming | 558 |
| 跨域出边 | 507 | Cross-domain Outgoing | 507 |
| 设计态模块 | 264 | Design Modules | 264 |
| 原型态模块 | 422 | Prototype Modules | 422 |
| 生产态模块 | 5 | Production Modules | 5 |
| 容量 | 697/150 (超容) | Capacity | 697/150 (超容) |
| 描述 | 反馈收集器(collectors) | Description | 反馈收集器(collectors) |

## 模块清单 / Module List

共 697 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-GOVERNANCE/GAAT Governance-Aware Agent Telemetry 治理感知遥测 | GAAT Governance-Aware Agent Telemetry... | design | design_only | D-GOVERNANCE/GAAT Governance-Aware Agent Telemetry 治理感知遥测 | GAAT Governance-Aware Agent Telemetry... | design | design_only |
| D-GOVERNANCE/GAAT Governance-Aware Telemetry GAAT治理感知遥测 | GAAT Governance-Aware Telemetry GAAT治... | design | design_only | D-GOVERNANCE/GAAT Governance-Aware Telemetry GAAT治理感知遥测 | GAAT Governance-Aware Telemetry GAAT治... | design | design_only |
| D-GOVERNANCE/Observability Dashboard 可观测性仪表盘 | Observability Dashboard 可观测性仪表盘 | design | design_only | D-GOVERNANCE/Observability Dashboard 可观测性仪表盘 | Observability Dashboard 可观测性仪表盘 | design | design_only |
| D-GOVERNANCE/Trusted Telemetry Plane 可信遥测平面 | Trusted Telemetry Plane 可信遥测平面 | design | design_only | D-GOVERNANCE/Trusted Telemetry Plane 可信遥测平面 | Trusted Telemetry Plane 可信遥测平面 | design | design_only |
| D-OPS/AI Agent Chaos Experiment Designer AI Agent混沌实验设计器 | AI Agent Chaos Experiment Designer AI... | design | design_only | D-OPS/AI Agent Chaos Experiment Designer AI Agent混沌实验设计器 | AI Agent Chaos Experiment Designer AI... | design | design_only |
| D-OPS/AI Autonomous Operations Closed Loop AI自治运维闭环 | AI Autonomous Operations Closed Loop ... | design | design_only | D-OPS/AI Autonomous Operations Closed Loop AI自治运维闭环 | AI Autonomous Operations Closed Loop ... | design | design_only |
| D-OPS/AI Autonomous Ops Engine AI自治运维引擎 | AI Autonomous Ops Engine AI自治运维引擎 | design | design_only | D-OPS/AI Autonomous Ops Engine AI自治运维引擎 | AI Autonomous Ops Engine AI自治运维引擎 | design | design_only |
| D-OPS/AI Inference Dependency Discovery AI推理依赖发现 | AI Inference Dependency Discovery AI推... | design | design_only | D-OPS/AI Inference Dependency Discovery AI推理依赖发现 | AI Inference Dependency Discovery AI推... | design | design_only |
| D-OPS/API Rate Limit Dependency Propagator API速率限制依赖传播器 | API Rate Limit Dependency Propagator ... | design | design_only | D-OPS/API Rate Limit Dependency Propagator API速率限制依赖传播器 | API Rate Limit Dependency Propagator ... | design | design_only |
| D-OPS/API Traffic Policy Mapper API流量策略映射器 | API Traffic Policy Mapper API流量策略映射器 | design | design_only | D-OPS/API Traffic Policy Mapper API流量策略映射器 | API Traffic Policy Mapper API流量策略映射器 | design | design_only |
| D-OPS/Adaptive Scheduler 自适应调度器 | Adaptive Scheduler 自适应调度器 | design | design_only | D-OPS/Adaptive Scheduler 自适应调度器 | Adaptive Scheduler 自适应调度器 | design | design_only |
| D-OPS/Alert Fatigue Management 通知疲劳管理 | Alert Fatigue Management 通知疲劳管理 | design | design_only | D-OPS/Alert Fatigue Management 通知疲劳管理 | Alert Fatigue Management 通知疲劳管理 | design | design_only |
| D-OPS/Alert Manager 告警管理 | Alert Manager 告警管理 | design | design_only | D-OPS/Alert Manager 告警管理 | Alert Manager 告警管理 | design | design_only |
| D-OPS/Anomaly Detection 异常检测 | Anomaly Detection 异常检测 | design | design_only | D-OPS/Anomaly Detection 异常检测 | Anomaly Detection 异常检测 | design | design_only |
| D-OPS/Anomaly Detector 异常检测器 | Anomaly Detector 异常检测器 | design | design_only | D-OPS/Anomaly Detector 异常检测器 | Anomaly Detector 异常检测器 | design | design_only |
| D-OPS/Anomaly Propagation GNN Predictor 异常传播GNN预测器 | Anomaly Propagation GNN Predictor 异常传... | design | design_only | D-OPS/Anomaly Propagation GNN Predictor 异常传播GNN预测器 | Anomaly Propagation GNN Predictor 异常传... | design | design_only |
| D-OPS/Anomaly Propagation Tracker 异常传播追踪器 | Anomaly Propagation Tracker 异常传播追踪器 | design | design_only | D-OPS/Anomaly Propagation Tracker 异常传播追踪器 | Anomaly Propagation Tracker 异常传播追踪器 | design | design_only |
| D-OPS/Application Layer Dependency Supplementer 应用层依赖补充器 | Application Layer Dependency Suppleme... | design | design_only | D-OPS/Application Layer Dependency Supplementer 应用层依赖补充器 | Application Layer Dependency Suppleme... | design | design_only |
| D-OPS/Asset Inventory 资产盘点 | Asset Inventory 资产盘点 | design | design_only | D-OPS/Asset Inventory 资产盘点 | Asset Inventory 资产盘点 | design | design_only |
| D-OPS/Auto Degradation Executor 自动降级执行器 | Auto Degradation Executor 自动降级执行器 | design | design_only | D-OPS/Auto Degradation Executor 自动降级执行器 | Auto Degradation Executor 自动降级执行器 | design | design_only |
| D-OPS/Auto Dependency Replacer 自动依赖替换器 | Auto Dependency Replacer 自动依赖替换器 | design | design_only | D-OPS/Auto Dependency Replacer 自动依赖替换器 | Auto Dependency Replacer 自动依赖替换器 | design | design_only |
| D-OPS/Auto Repair Executor 自动修复执行器 | Auto Repair Executor 自动修复执行器 | design | design_only | D-OPS/Auto Repair Executor 自动修复执行器 | Auto Repair Executor 自动修复执行器 | design | design_only |
| D-OPS/Auto Rollback Executor 自动回滚执行器 | Auto Rollback Executor 自动回滚执行器 | design | design_only | D-OPS/Auto Rollback Executor 自动回滚执行器 | Auto Rollback Executor 自动回滚执行器 | design | design_only |
| D-OPS/Auto Rollback Strategy Selector 自动回滚策略选择器 | Auto Rollback Strategy Selector 自动回滚策... | design | design_only | D-OPS/Auto Rollback Strategy Selector 自动回滚策略选择器 | Auto Rollback Strategy Selector 自动回滚策... | design | design_only |
| D-OPS/Backup Recovery Manager 备份与恢复管理器 | Backup Recovery Manager 备份与恢复管理器 | design | design_only | D-OPS/Backup Recovery Manager 备份与恢复管理器 | Backup Recovery Manager 备份与恢复管理器 | design | design_only |
| D-OPS/Batch Simulator 批量仿真器 | Batch Simulator 批量仿真器 | design | design_only | D-OPS/Batch Simulator 批量仿真器 | Batch Simulator 批量仿真器 | design | design_only |
| D-OPS/Bidirectional Synchronizer 双向同步器 | Bidirectional Synchronizer 双向同步器 | design | design_only | D-OPS/Bidirectional Synchronizer 双向同步器 | Bidirectional Synchronizer 双向同步器 | design | design_only |
| D-OPS/Blast Radius Calculator 爆炸半径计算器 | Blast Radius Calculator 爆炸半径计算器 | design | design_only | D-OPS/Blast Radius Calculator 爆炸半径计算器 | Blast Radius Calculator 爆炸半径计算器 | design | design_only |
| D-OPS/Blast Radius Predictor 爆炸半径预测器 | Blast Radius Predictor 爆炸半径预测器 | design | design_only | D-OPS/Blast Radius Predictor 爆炸半径预测器 | Blast Radius Predictor 爆炸半径预测器 | design | design_only |
| D-OPS/Bulkhead Modeler 舱壁建模器 | Bulkhead Modeler 舱壁建模器 | design | design_only | D-OPS/Bulkhead Modeler 舱壁建模器 | Bulkhead Modeler 舱壁建模器 | design | design_only |
| D-OPS/Bus Factor Defense 巴士因子防御 | Bus Factor Defense 巴士因子防御 | design | design_only | D-OPS/Bus Factor Defense 巴士因子防御 | Bus Factor Defense 巴士因子防御 | design | design_only |
| D-OPS/Capacity Assurance 容量保障 | Capacity Assurance 容量保障 | design | design_only | D-OPS/Capacity Assurance 容量保障 | Capacity Assurance 容量保障 | design | design_only |
| D-OPS/Capacity Planning Resource Prediction 容量规划与资源预测 | Capacity Planning Resource Prediction... | design | design_only | D-OPS/Capacity Planning Resource Prediction 容量规划与资源预测 | Capacity Planning Resource Prediction... | design | design_only |
| D-OPS/Carbon Budget Tracker 碳预算追踪器 | Carbon Budget Tracker 碳预算追踪器 | design | design_only | D-OPS/Carbon Budget Tracker 碳预算追踪器 | Carbon Budget Tracker 碳预算追踪器 | design | design_only |
| D-OPS/Carbon Budget Tracking Enhancer 碳预算追踪增强器 | Carbon Budget Tracking Enhancer 碳预算追踪增强器 | design | design_only | D-OPS/Carbon Budget Tracking Enhancer 碳预算追踪增强器 | Carbon Budget Tracking Enhancer 碳预算追踪增强器 | design | design_only |
| D-OPS/Carbon Intensity API Integrator 碳强度API集成器 | Carbon Intensity API Integrator 碳强度AP... | design | design_only | D-OPS/Carbon Intensity API Integrator 碳强度API集成器 | Carbon Intensity API Integrator 碳强度AP... | design | design_only |
| D-OPS/Carbon-Aware SDK v2 Integrator Carbon-Aware SDK v2集成器 | Carbon-Aware SDK v2 Integrator Carbon... | design | design_only | D-OPS/Carbon-Aware SDK v2 Integrator Carbon-Aware SDK v2集成器 | Carbon-Aware SDK v2 Integrator Carbon... | design | design_only |
| D-OPS/Cascade Fault Generator 级联故障生成器 | Cascade Fault Generator 级联故障生成器 | design | design_only | D-OPS/Cascade Fault Generator 级联故障生成器 | Cascade Fault Generator 级联故障生成器 | design | design_only |
| D-OPS/Causal Inference Correlator 因果推断关联器 | Causal Inference Correlator 因果推断关联器 | design | design_only | D-OPS/Causal Inference Correlator 因果推断关联器 | Causal Inference Correlator 因果推断关联器 | design | design_only |
| D-OPS/Change Management Engine 变更管理引擎 | Change Management Engine 变更管理引擎 | design | design_only | D-OPS/Change Management Engine 变更管理引擎 | Change Management Engine 变更管理引擎 | design | design_only |
| D-OPS/Change Management 变更管理 | Change Management 变更管理 | design | design_only | D-OPS/Change Management 变更管理 | Change Management 变更管理 | design | design_only |
| D-OPS/Change Manager 变更管理器 | Change Manager 变更管理器 | design | design_only | D-OPS/Change Manager 变更管理器 | Change Manager 变更管理器 | design | design_only |
| D-OPS/Change Notification Enhancer 变更通知增强器 | Change Notification Enhancer 变更通知增强器 | design | design_only | D-OPS/Change Notification Enhancer 变更通知增强器 | Change Notification Enhancer 变更通知增强器 | design | design_only |
| D-OPS/Change Notifier 变更通知器 | Change Notifier 变更通知器 | design | design_only | D-OPS/Change Notifier 变更通知器 | Change Notifier 变更通知器 | design | design_only |
| D-OPS/Chaos Engineering Engine 混沌工程引擎 | Chaos Engineering Engine 混沌工程引擎 | design | design_only | D-OPS/Chaos Engineering Engine 混沌工程引擎 | Chaos Engineering Engine 混沌工程引擎 | design | design_only |
| D-OPS/Chaos Engineering Fault Injection 混沌工程与故障注入 | Chaos Engineering Fault Injection 混沌工... | design | design_only | D-OPS/Chaos Engineering Fault Injection 混沌工程与故障注入 | Chaos Engineering Fault Injection 混沌工... | design | design_only |
| D-OPS/Chaos Experiment Dependency Graph Builder 混沌实验依赖图构建器 | Chaos Experiment Dependency Graph Bui... | design | design_only | D-OPS/Chaos Experiment Dependency Graph Builder 混沌实验依赖图构建器 | Chaos Experiment Dependency Graph Bui... | design | design_only |
| D-OPS/Chaos Experiment Dependency Validator 混沌实验依赖验证器 | Chaos Experiment Dependency Validator... | design | design_only | D-OPS/Chaos Experiment Dependency Validator 混沌实验依赖验证器 | Chaos Experiment Dependency Validator... | design | design_only |
| D-OPS/Chaos Result Knowledge Base 混沌结果知识库 | Chaos Result Knowledge Base 混沌结果知识库 | design | design_only | D-OPS/Chaos Result Knowledge Base 混沌结果知识库 | Chaos Result Knowledge Base 混沌结果知识库 | design | design_only |
| D-OPS/Circuit Breaker Dependency Graph Builder 熔断器依赖图构建器 | Circuit Breaker Dependency Graph Buil... | design | design_only | D-OPS/Circuit Breaker Dependency Graph Builder 熔断器依赖图构建器 | Circuit Breaker Dependency Graph Buil... | design | design_only |
| D-OPS/Circuit Breaker Modeler 熔断器建模器 | Circuit Breaker Modeler 熔断器建模器 | design | design_only | D-OPS/Circuit Breaker Modeler 熔断器建模器 | Circuit Breaker Modeler 熔断器建模器 | design | design_only |
| D-OPS/Cloud-Edge-Device Scheduler 云-边-端调度器 | Cloud-Edge-Device Scheduler 云-边-端调度器 | design | design_only | D-OPS/Cloud-Edge-Device Scheduler 云-边-端调度器 | Cloud-Edge-Device Scheduler 云-边-端调度器 | design | design_only |
| D-OPS/Conditional Dependency Activation Detector 条件依赖激活检测器 | Conditional Dependency Activation Det... | design | design_only | D-OPS/Conditional Dependency Activation Detector 条件依赖激活检测器 | Conditional Dependency Activation Det... | design | design_only |
| D-OPS/Configuration Manager 配置管理 | Configuration Manager 配置管理 | design | design_only | D-OPS/Configuration Manager 配置管理 | Configuration Manager 配置管理 | design | design_only |
| D-OPS/Critical Path Fault Generator 关键路径故障生成器 | Critical Path Fault Generator 关键路径故障生成器 | design | design_only | D-OPS/Critical Path Fault Generator 关键路径故障生成器 | Critical Path Fault Generator 关键路径故障生成器 | design | design_only |
| D-OPS/Cross-Domain Ops Event Chain Tracking 跨域运维事件链追踪 | Cross-Domain Ops Event Chain Tracking... | design | design_only | D-OPS/Cross-Domain Ops Event Chain Tracking 跨域运维事件链追踪 | Cross-Domain Ops Event Chain Tracking... | design | design_only |
| D-OPS/Cross-Env Dependency Diff Analyzer 跨环境依赖差异分析 | Cross-Env Dependency Diff Analyzer 跨环... | design | design_only | D-OPS/Cross-Env Dependency Diff Analyzer 跨环境依赖差异分析 | Cross-Env Dependency Diff Analyzer 跨环... | design | design_only |
| D-OPS/Cross-Language Dependency Chain Fixer 跨语言依赖链修复器 | Cross-Language Dependency Chain Fixer... | design | design_only | D-OPS/Cross-Language Dependency Chain Fixer 跨语言依赖链修复器 | Cross-Language Dependency Chain Fixer... | design | design_only |
| D-OPS/D-OPS | D-OPS | design | design_only | D-OPS/D-OPS | D-OPS | design | design_only |
| D-OPS/DNS Dependency Discoverer DNS依赖发现器 | DNS Dependency Discoverer DNS依赖发现器 | design | design_only | D-OPS/DNS Dependency Discoverer DNS依赖发现器 | DNS Dependency Discoverer DNS依赖发现器 | design | design_only |
| D-OPS/DNS Dependency Discovery Enhancer DNS依赖发现增强 | DNS Dependency Discovery Enhancer DNS... | design | design_only | D-OPS/DNS Dependency Discovery Enhancer DNS依赖发现增强 | DNS Dependency Discovery Enhancer DNS... | design | design_only |
| D-OPS/DNS Query Collector DNS查询采集器 | DNS Query Collector DNS查询采集器 | design | design_only | D-OPS/DNS Query Collector DNS查询采集器 | DNS Query Collector DNS查询采集器 | design | design_only |
| D-OPS/DR Manager 灾难恢复 | DR Manager 灾难恢复 | design | design_only | D-OPS/DR Manager 灾难恢复 | DR Manager 灾难恢复 | design | design_only |
| D-OPS/DSV Encoding Enhancer DSV编码增强 | DSV Encoding Enhancer DSV编码增强 | design | design_only | D-OPS/DSV Encoding Enhancer DSV编码增强 | DSV Encoding Enhancer DSV编码增强 | design | design_only |
| D-OPS/Data Quality SLA Monitor 数据质量SLA监控 | Data Quality SLA Monitor 数据质量SLA监控 | design | design_only | D-OPS/Data Quality SLA Monitor 数据质量SLA监控 | Data Quality SLA Monitor 数据质量SLA监控 | design | design_only |
| D-OPS/Degradation Chain Validator 降级链验证器 | Degradation Chain Validator 降级链验证器 | design | design_only | D-OPS/Degradation Chain Validator 降级链验证器 | Degradation Chain Validator 降级链验证器 | design | design_only |
| D-OPS/Degradation Path Modeler 降级路径建模器 | Degradation Path Modeler 降级路径建模器 | design | design_only | D-OPS/Degradation Path Modeler 降级路径建模器 | Degradation Path Modeler 降级路径建模器 | design | design_only |
| D-OPS/Degradation Strategy Manager 降级策略管理器 | Degradation Strategy Manager 降级策略管理器 | design | design_only | D-OPS/Degradation Strategy Manager 降级策略管理器 | Degradation Strategy Manager 降级策略管理器 | design | design_only |
| D-OPS/Dependency Bottleneck Resource Optimizer 依赖瓶颈资源优化 | Dependency Bottleneck Resource Optimi... | design | design_only | D-OPS/Dependency Bottleneck Resource Optimizer 依赖瓶颈资源优化 | Dependency Bottleneck Resource Optimi... | design | design_only |
| D-OPS/Dependency Circuit Breaker 依赖断路器 | Dependency Circuit Breaker 依赖断路器 | design | design_only | D-OPS/Dependency Circuit Breaker 依赖断路器 | Dependency Circuit Breaker 依赖断路器 | design | design_only |
| D-OPS/Dependency Cost Tracker 依赖图成本追踪 | Dependency Cost Tracker 依赖图成本追踪 | design | design_only | D-OPS/Dependency Cost Tracker 依赖图成本追踪 | Dependency Cost Tracker 依赖图成本追踪 | design | design_only |
| D-OPS/Dependency Criticality DCS Scoring Enhancer 依赖关键度DCS评分增强 | Dependency Criticality DCS Scoring En... | design | design_only | D-OPS/Dependency Criticality DCS Scoring Enhancer 依赖关键度DCS评分增强 | Dependency Criticality DCS Scoring En... | design | design_only |
| D-OPS/Dependency Criticality Scorer 依赖关键度评分器 | Dependency Criticality Scorer 依赖关键度评分器 | design | design_only | D-OPS/Dependency Criticality Scorer 依赖关键度评分器 | Dependency Criticality Scorer 依赖关键度评分器 | design | design_only |
| D-OPS/Dependency Drift Distance Metric Enhancer 依赖漂移距离度量增强 | Dependency Drift Distance Metric Enha... | design | design_only | D-OPS/Dependency Drift Distance Metric Enhancer 依赖漂移距离度量增强 | Dependency Drift Distance Metric Enha... | design | design_only |
| D-OPS/Dependency Graph Builder 依赖图构建器 | Dependency Graph Builder 依赖图构建器 | design | design_only | D-OPS/Dependency Graph Builder 依赖图构建器 | Dependency Graph Builder 依赖图构建器 | design | design_only |
| D-OPS/Dependency Graph Resilience Scorer 依赖图韧性评分器 | Dependency Graph Resilience Scorer 依赖... | design | design_only | D-OPS/Dependency Graph Resilience Scorer 依赖图韧性评分器 | Dependency Graph Resilience Scorer 依赖... | design | design_only |
| D-OPS/Dependency Health Scoring Engine 依赖健康评分引擎 | Dependency Health Scoring Engine 依赖健康... | design | design_only | D-OPS/Dependency Health Scoring Engine 依赖健康评分引擎 | Dependency Health Scoring Engine 依赖健康... | design | design_only |
| D-OPS/Dependency State Vector Encoder 依赖状态向量编码器 | Dependency State Vector Encoder 依赖状态向... | design | design_only | D-OPS/Dependency State Vector Encoder 依赖状态向量编码器 | Dependency State Vector Encoder 依赖状态向... | design | design_only |
| D-OPS/Deploy Order CSP Solver 部署顺序CSP求解器 | Deploy Order CSP Solver 部署顺序CSP求解器 | design | design_only | D-OPS/Deploy Order CSP Solver 部署顺序CSP求解器 | Deploy Order CSP Solver 部署顺序CSP求解器 | design | design_only |
| D-OPS/Deployment Manager 部署管理 | Deployment Manager 部署管理 | design | design_only | D-OPS/Deployment Manager 部署管理 | Deployment Manager 部署管理 | design | design_only |
| D-OPS/Differentiable Impact Simulation Enhancer 可微分影响仿真增强 | Differentiable Impact Simulation Enha... | design | design_only | D-OPS/Differentiable Impact Simulation Enhancer 可微分影响仿真增强 | Differentiable Impact Simulation Enha... | design | design_only |
| D-OPS/Differentiable Impact Simulator 可微分影响仿真器 | Differentiable Impact Simulator 可微分影响仿真器 | design | design_only | D-OPS/Differentiable Impact Simulator 可微分影响仿真器 | Differentiable Impact Simulator 可微分影响仿真器 | design | design_only |
| D-OPS/Disaster Recovery 3-2-1-1-0 灾备架构3-2-1-1-0 | Disaster Recovery 3-2-1-1-0 灾备架构3-2-1... | design | design_only | D-OPS/Disaster Recovery 3-2-1-1-0 灾备架构3-2-1-1-0 | Disaster Recovery 3-2-1-1-0 灾备架构3-2-1... | design | design_only |
| D-OPS/Disaster Recovery Architecture 灾备架构 | Disaster Recovery Architecture 灾备架构 | design | design_only | D-OPS/Disaster Recovery Architecture 灾备架构 | Disaster Recovery Architecture 灾备架构 | design | design_only |
| D-OPS/Disaster Recovery Engine 灾备引擎 | Disaster Recovery Engine 灾备引擎 | design | design_only | D-OPS/Disaster Recovery Engine 灾备引擎 | Disaster Recovery Engine 灾备引擎 | design | design_only |
| D-OPS/Distributed Trace Dependency Correlator 分布式追踪依赖关联 | Distributed Trace Dependency Correlat... | design | design_only | D-OPS/Distributed Trace Dependency Correlator 分布式追踪依赖关联 | Distributed Trace Dependency Correlat... | design | design_only |
| D-OPS/Documentation Drift Anti-Pattern Detection Enhancer 文档漂移反模式检测增强 | Documentation Drift Anti-Pattern Dete... | design | design_only | D-OPS/Documentation Drift Anti-Pattern Detection Enhancer 文档漂移反模式检测增强 | Documentation Drift Anti-Pattern Dete... | design | design_only |
| D-OPS/Dual Machine Hot Standby 双机热备 | Dual Machine Hot Standby 双机热备 | design | design_only | D-OPS/Dual Machine Hot Standby 双机热备 | Dual Machine Hot Standby 双机热备 | design | design_only |
| D-OPS/Dynamic Dependency Graph Builder 动态依赖图构建器 | Dynamic Dependency Graph Builder 动态依赖... | design | design_only | D-OPS/Dynamic Dependency Graph Builder 动态依赖图构建器 | Dynamic Dependency Graph Builder 动态依赖... | design | design_only |
| D-OPS/Edge Dependency Constraint Modeler 边缘依赖约束建模器 | Edge Dependency Constraint Modeler 边缘... | design | design_only | D-OPS/Edge Dependency Constraint Modeler 边缘依赖约束建模器 | Edge Dependency Constraint Modeler 边缘... | design | design_only |
| D-OPS/Emergency Life Saving Track 应急保命轨 | Emergency Life Saving Track 应急保命轨 | design | design_only | D-OPS/Emergency Life Saving Track 应急保命轨 | Emergency Life Saving Track 应急保命轨 | design | design_only |
| D-OPS/Emergency Preservation Track 应急保命轨 | Emergency Preservation Track 应急保命轨 | design | design_only | D-OPS/Emergency Preservation Track 应急保命轨 | Emergency Preservation Track 应急保命轨 | design | design_only |
| D-OPS/Emergency Survival Track 应急保命轨 | Emergency Survival Track 应急保命轨 | design | design_only | D-OPS/Emergency Survival Track 应急保命轨 | Emergency Survival Track 应急保命轨 | design | design_only |
| D-OPS/EmergencyDegradationTrack 保命轨 | EmergencyDegradationTrack 保命轨 | design | design_only | D-OPS/EmergencyDegradationTrack 保命轨 | EmergencyDegradationTrack 保命轨 | design | design_only |
| D-OPS/Envoy Dependency Extractor Envoy依赖提取器 | Envoy Dependency Extractor Envoy依赖提取器 | design | design_only | D-OPS/Envoy Dependency Extractor Envoy依赖提取器 | Envoy Dependency Extractor Envoy依赖提取器 | design | design_only |
| D-OPS/Experiment Recorder 实验记录器 | Experiment Recorder 实验记录器 | design | design_only | D-OPS/Experiment Recorder 实验记录器 | Experiment Recorder 实验记录器 | design | design_only |
| D-OPS/Experiment Reporter 实验报告器 | Experiment Reporter 实验报告器 | design | design_only | D-OPS/Experiment Reporter 实验报告器 | Experiment Reporter 实验报告器 | design | design_only |
| D-OPS/External Dependency SLA Monitor 外部依赖SLA监控 | External Dependency SLA Monitor 外部依赖S... | design | design_only | D-OPS/External Dependency SLA Monitor 外部依赖SLA监控 | External Dependency SLA Monitor 外部依赖S... | design | design_only |
| D-OPS/Fault Injector 故障注入器 | Fault Injector 故障注入器 | design | design_only | D-OPS/Fault Injector 故障注入器 | Fault Injector 故障注入器 | design | design_only |
| D-OPS/Fault Scenario Definer 故障场景定义器 | Fault Scenario Definer 故障场景定义器 | design | design_only | D-OPS/Fault Scenario Definer 故障场景定义器 | Fault Scenario Definer 故障场景定义器 | design | design_only |
| D-OPS/File Access Collector 文件访问采集器 | File Access Collector 文件访问采集器 | design | design_only | D-OPS/File Access Collector 文件访问采集器 | File Access Collector 文件访问采集器 | design | design_only |
| D-OPS/File I/O Dependency Discoverer 文件I/O依赖发现器 | File I/O Dependency Discoverer 文件I/O依... | design | design_only | D-OPS/File I/O Dependency Discoverer 文件I/O依赖发现器 | File I/O Dependency Discoverer 文件I/O依... | design | design_only |
| D-OPS/File I/O Dependency Discovery Enhancer 文件I/O依赖发现增强 | File I/O Dependency Discovery Enhance... | design | design_only | D-OPS/File I/O Dependency Discovery Enhancer 文件I/O依赖发现增强 | File I/O Dependency Discovery Enhance... | design | design_only |
| D-OPS/FinOps Cost Anomaly Detector FinOps成本异常检测 | FinOps Cost Anomaly Detector FinOps成本... | design | design_only | D-OPS/FinOps Cost Anomaly Detector FinOps成本异常检测 | FinOps Cost Anomaly Detector FinOps成本... | design | design_only |
| D-OPS/GPU Scheduling GPU调度上岗 | GPU Scheduling GPU调度上岗 | design | design_only | D-OPS/GPU Scheduling GPU调度上岗 | GPU Scheduling GPU调度上岗 | design | design_only |
| D-OPS/GPU显存异常检测规则 | GPU显存异常检测规则 | design | design_only | D-OPS/GPU显存异常检测规则 | GPU显存异常检测规则 | design | design_only |
| D-OPS/GitOps Dependency Resolver GitOps依赖解析器 | GitOps Dependency Resolver GitOps依赖解析器 | design | design_only | D-OPS/GitOps Dependency Resolver GitOps依赖解析器 | GitOps Dependency Resolver GitOps依赖解析器 | design | design_only |
| D-OPS/Green Deployment Strategist 绿色部署策略器 | Green Deployment Strategist 绿色部署策略器 | design | design_only | D-OPS/Green Deployment Strategist 绿色部署策略器 | Green Deployment Strategist 绿色部署策略器 | design | design_only |
| D-OPS/Health Check Readiness Probe 健康检查与就绪探针 | Health Check Readiness Probe 健康检查与就绪探针 | design | design_only | D-OPS/Health Check Readiness Probe 健康检查与就绪探针 | Health Check Readiness Probe 健康检查与就绪探针 | design | design_only |
| D-OPS/Health Monitoring 健康监控 | Health Monitoring 健康监控 | design | design_only | D-OPS/Health Monitoring 健康监控 | Health Monitoring 健康监控 | design | design_only |
| D-OPS/High-Risk Node Fault Generator 高风险节点故障生成器 | High-Risk Node Fault Generator 高风险节点故... | design | design_only | D-OPS/High-Risk Node Fault Generator 高风险节点故障生成器 | High-Risk Node Fault Generator 高风险节点故... | design | design_only |
| D-OPS/ISO 23247-4 Dependency Entity Model ISO 23247-4依赖实体模型 | ISO 23247-4 Dependency Entity Model I... | design | design_only | D-OPS/ISO 23247-4 Dependency Entity Model ISO 23247-4依赖实体模型 | ISO 23247-4 Dependency Entity Model I... | design | design_only |
| D-OPS/ISO 23247-4 Entity Model Enhancer ISO 23247-4实体模型增强 | ISO 23247-4 Entity Model Enhancer ISO... | design | design_only | D-OPS/ISO 23247-4 Entity Model Enhancer ISO 23247-4实体模型增强 | ISO 23247-4 Entity Model Enhancer ISO... | design | design_only |
| D-OPS/Implicit Dependency Discoverer 隐式依赖发现器 | Implicit Dependency Discoverer 隐式依赖发现器 | design | design_only | D-OPS/Implicit Dependency Discoverer 隐式依赖发现器 | Implicit Dependency Discoverer 隐式依赖发现器 | design | design_only |
| D-OPS/Incremental Chaos Validation Enhancer 增量混沌验证增强 | Incremental Chaos Validation Enhancer... | design | design_only | D-OPS/Incremental Chaos Validation Enhancer 增量混沌验证增强 | Incremental Chaos Validation Enhancer... | design | design_only |
| D-OPS/Incremental Chaos Validator 增量混沌验证器 | Incremental Chaos Validator 增量混沌验证器 | design | design_only | D-OPS/Incremental Chaos Validator 增量混沌验证器 | Incremental Chaos Validator 增量混沌验证器 | design | design_only |
| D-OPS/Integration Health Monitor 集成健康监控器 | Integration Health Monitor 集成健康监控器 | design | design_only | D-OPS/Integration Health Monitor 集成健康监控器 | Integration Health Monitor 集成健康监控器 | design | design_only |
| D-OPS/Istio Ambient Mode Dependency Enhancer Istio Ambient模式依赖增强 | Istio Ambient Mode Dependency Enhance... | design | design_only | D-OPS/Istio Ambient Mode Dependency Enhancer Istio Ambient模式依赖增强 | Istio Ambient Mode Dependency Enhance... | design | design_only |
| D-OPS/Istio Config Parser Istio配置解析器 | Istio Config Parser Istio配置解析器 | design | design_only | D-OPS/Istio Config Parser Istio配置解析器 | Istio Config Parser Istio配置解析器 | design | design_only |
| D-OPS/Istio Policy DSL Generation Enhancer Istio策略DSL生成增强 | Istio Policy DSL Generation Enhancer ... | design | design_only | D-OPS/Istio Policy DSL Generation Enhancer Istio策略DSL生成增强 | Istio Policy DSL Generation Enhancer ... | design | design_only |
| D-OPS/Istio Policy DSL Generator Istio策略DSL生成器 | Istio Policy DSL Generator Istio策略DSL生成器 | design | design_only | D-OPS/Istio Policy DSL Generator Istio策略DSL生成器 | Istio Policy DSL Generator Istio策略DSL生成器 | design | design_only |
| D-OPS/LLM API SLA Monitor LLM API SLA监控 | LLM API SLA Monitor LLM API SLA监控 | design | design_only | D-OPS/LLM API SLA Monitor LLM API SLA监控 | LLM API SLA Monitor LLM API SLA监控 | design | design_only |
| D-OPS/LLM Hallucination Correlation Misjudgment Filter LLM幻觉关联误判过滤器 | LLM Hallucination Correlation Misjudg... | design | design_only | D-OPS/LLM Hallucination Correlation Misjudgment Filter LLM幻觉关联误判过滤器 | LLM Hallucination Correlation Misjudg... | design | design_only |
| D-OPS/Left Kan Extension Dependency Resolver 左Kan扩展依赖解析器 | Left Kan Extension Dependency Resolve... | design | design_only | D-OPS/Left Kan Extension Dependency Resolver 左Kan扩展依赖解析器 | Left Kan Extension Dependency Resolve... | design | design_only |
| D-OPS/Linkerd Policy Generation Enhancer Linkerd策略生成增强 | Linkerd Policy Generation Enhancer Li... | design | design_only | D-OPS/Linkerd Policy Generation Enhancer Linkerd策略生成增强 | Linkerd Policy Generation Enhancer Li... | design | design_only |
| D-OPS/Linkerd Policy Generator Linkerd策略生成器 | Linkerd Policy Generator Linkerd策略生成器 | design | design_only | D-OPS/Linkerd Policy Generator Linkerd策略生成器 | Linkerd Policy Generator Linkerd策略生成器 | design | design_only |
| D-OPS/Log Correlator 日志关联器 | Log Correlator 日志关联器 | design | design_only | D-OPS/Log Correlator 日志关联器 | Log Correlator 日志关联器 | design | design_only |
| D-OPS/Low-Carbon Window Detection Enhancer 低碳窗口检测增强器 | Low-Carbon Window Detection Enhancer ... | design | design_only | D-OPS/Low-Carbon Window Detection Enhancer 低碳窗口检测增强器 | Low-Carbon Window Detection Enhancer ... | design | design_only |
| D-OPS/Low-Carbon Window Detector 低碳窗口检测器 | Low-Carbon Window Detector 低碳窗口检测器 | design | design_only | D-OPS/Low-Carbon Window Detector 低碳窗口检测器 | Low-Carbon Window Detector 低碳窗口检测器 | design | design_only |
| D-OPS/Metric Correlator 指标关联器 | Metric Correlator 指标关联器 | design | design_only | D-OPS/Metric Correlator 指标关联器 | Metric Correlator 指标关联器 | design | design_only |
| D-OPS/Metric Dependency Anomaly Detector 指标依赖异常检测 | Metric Dependency Anomaly Detector 指标... | design | design_only | D-OPS/Metric Dependency Anomaly Detector 指标依赖异常检测 | Metric Dependency Anomaly Detector 指标... | design | design_only |
| D-OPS/Minimum Blast Radius Calculator 最小爆破半径计算器 | Minimum Blast Radius Calculator 最小爆破半... | design | design_only | D-OPS/Minimum Blast Radius Calculator 最小爆破半径计算器 | Minimum Blast Radius Calculator 最小爆破半... | design | design_only |
| D-OPS/Model Hot Swap 模型热交换 | Model Hot Swap 模型热交换 | design | design_only | D-OPS/Model Hot Swap 模型热交换 | Model Hot Swap 模型热交换 | design | design_only |
| D-OPS/Monitor Agent 监控Agent | Monitor Agent 监控Agent | design | design_only | D-OPS/Monitor Agent 监控Agent | Monitor Agent 监控Agent | design | design_only |
| D-OPS/Monitoring System 监控体系 | Monitoring System 监控体系 | design | design_only | D-OPS/Monitoring System 监控体系 | Monitoring System 监控体系 | design | design_only |
| D-OPS/Multi-Cloud SLA Aggregation Engine 多云SLA聚合引擎 | Multi-Cloud SLA Aggregation Engine 多云... | design | design_only | D-OPS/Multi-Cloud SLA Aggregation Engine 多云SLA聚合引擎 | Multi-Cloud SLA Aggregation Engine 多云... | design | design_only |
| D-OPS/Network Connection Collector 网络连接采集器 | Network Connection Collector 网络连接采集器 | design | design_only | D-OPS/Network Connection Collector 网络连接采集器 | Network Connection Collector 网络连接采集器 | design | design_only |
| D-OPS/Network Resilience Scoring Engine 网络韧性评分引擎 | Network Resilience Scoring Engine 网络韧... | design | design_only | D-OPS/Network Resilience Scoring Engine 网络韧性评分引擎 | Network Resilience Scoring Engine 网络韧... | design | design_only |
| D-OPS/Network Topology Discoverer 网络拓扑发现器 | Network Topology Discoverer 网络拓扑发现器 | design | design_only | D-OPS/Network Topology Discoverer 网络拓扑发现器 | Network Topology Discoverer 网络拓扑发现器 | design | design_only |
| D-OPS/Network Topology Discovery Enhancer 网络拓扑发现增强 | Network Topology Discovery Enhancer 网... | design | design_only | D-OPS/Network Topology Discovery Enhancer 网络拓扑发现增强 | Network Topology Discovery Enhancer 网... | design | design_only |
| D-OPS/Neuromorphic Event-Driven Scheduler 神经形态事件驱动调度器 | Neuromorphic Event-Driven Scheduler 神... | design | design_only | D-OPS/Neuromorphic Event-Driven Scheduler 神经形态事件驱动调度器 | Neuromorphic Event-Driven Scheduler 神... | design | design_only |
| D-OPS/OTel Auto-Topology Builder OTel自动拓扑构建器 | OTel Auto-Topology Builder OTel自动拓扑构建器 | design | design_only | D-OPS/OTel Auto-Topology Builder OTel自动拓扑构建器 | OTel Auto-Topology Builder OTel自动拓扑构建器 | design | design_only |
| D-OPS/OTel Collector Integration OTel Collector集成 | OTel Collector Integration OTel Colle... | design | design_only | D-OPS/OTel Collector Integration OTel Collector集成 | OTel Collector Integration OTel Colle... | design | design_only |
| D-OPS/OTel GenAI SemConv Integrator OTel GenAI语义约定集成器 | OTel GenAI SemConv Integrator OTel Ge... | design | design_only | D-OPS/OTel GenAI SemConv Integrator OTel GenAI语义约定集成器 | OTel GenAI SemConv Integrator OTel Ge... | design | design_only |
| D-OPS/OTel GenAI Semantic Conventions OTel GenAI语义约定 | OTel GenAI Semantic Conventions OTel ... | design | design_only | D-OPS/OTel GenAI Semantic Conventions OTel GenAI语义约定 | OTel GenAI Semantic Conventions OTel ... | design | design_only |
| D-OPS/OpenTelemetry 2.0 | OpenTelemetry 2.0 | design | design_only | D-OPS/OpenTelemetry 2.0 | OpenTelemetry 2.0 | design | design_only |
| D-OPS/OpenTelemetry分布式追踪 分布式追踪 | OpenTelemetry分布式追踪 分布式追踪 | design | design_only | D-OPS/OpenTelemetry分布式追踪 分布式追踪 | OpenTelemetry分布式追踪 分布式追踪 | design | design_only |
| D-OPS/Operations Specification 运维规格 | Operations Specification 运维规格 | design | design_only | D-OPS/Operations Specification 运维规格 | Operations Specification 运维规格 | design | design_only |
| D-OPS/Ops Automation Runbook Engine 运维自动化Runbook引擎 | Ops Automation Runbook Engine 运维自动化Ru... | design | design_only | D-OPS/Ops Automation Runbook Engine 运维自动化Runbook引擎 | Ops Automation Runbook Engine 运维自动化Ru... | design | design_only |
| D-OPS/Ops Foundation 运维基础 | Ops Foundation 运维基础 | design | design_only | D-OPS/Ops Foundation 运维基础 | Ops Foundation 运维基础 | design | design_only |
| D-OPS/OpsIncident 运维事件 | OpsIncident 运维事件 | design | design_only | D-OPS/OpsIncident 运维事件 | OpsIncident 运维事件 | design | design_only |
| D-OPS/Paper Live Transition 模拟实盘转换 | Paper Live Transition 模拟实盘转换 | design | design_only | D-OPS/Paper Live Transition 模拟实盘转换 | Paper Live Transition 模拟实盘转换 | design | design_only |
| D-OPS/Performance Baseline 性能基线 | Performance Baseline 性能基线 | design | design_only | D-OPS/Performance Baseline 性能基线 | Performance Baseline 性能基线 | design | design_only |
| D-OPS/Performance Profiler 性能分析器 | Performance Profiler 性能分析器 | design | design_only | D-OPS/Performance Profiler 性能分析器 | Performance Profiler 性能分析器 | design | design_only |
| D-OPS/Post Live Verification 上线后验证 | Post Live Verification 上线后验证 | design | design_only | D-OPS/Post Live Verification 上线后验证 | Post Live Verification 上线后验证 | design | design_only |
| D-OPS/Post Process 后处理 | Post Process 后处理 | design | design_only | D-OPS/Post Process 后处理 | Post Process 后处理 | design | design_only |
| D-OPS/Predictive System Maintenance 预测性系统维护 | Predictive System Maintenance 预测性系统维护 | design | design_only | D-OPS/Predictive System Maintenance 预测性系统维护 | Predictive System Maintenance 预测性系统维护 | design | design_only |
| D-OPS/Process Call Collector 进程调用采集器 | Process Call Collector 进程调用采集器 | design | design_only | D-OPS/Process Call Collector 进程调用采集器 | Process Call Collector 进程调用采集器 | design | design_only |
| D-OPS/Process Relationship Tracker 进程关系追踪器 | Process Relationship Tracker 进程关系追踪器 | design | design_only | D-OPS/Process Relationship Tracker 进程关系追踪器 | Process Relationship Tracker 进程关系追踪器 | design | design_only |
| D-OPS/Process Relationship Tracking Enhancer 进程关系追踪增强 | Process Relationship Tracking Enhance... | design | design_only | D-OPS/Process Relationship Tracking Enhancer 进程关系追踪增强 | Process Relationship Tracking Enhance... | design | design_only |
| D-OPS/Progressive Delivery Dependency Checker 渐进式交付依赖检查器 | Progressive Delivery Dependency Check... | design | design_only | D-OPS/Progressive Delivery Dependency Checker 渐进式交付依赖检查器 | Progressive Delivery Dependency Check... | design | design_only |
| D-OPS/PubGrub Version Solver PubGrub版本求解器 | PubGrub Version Solver PubGrub版本求解器 | design | design_only | D-OPS/PubGrub Version Solver PubGrub版本求解器 | PubGrub Version Solver PubGrub版本求解器 | design | design_only |
| D-OPS/Query Router 查询路由器 | Query Router 查询路由器 | design | design_only | D-OPS/Query Router 查询路由器 | Query Router 查询路由器 | design | design_only |
| D-OPS/Query Routing Enhancer 查询路由增强器 | Query Routing Enhancer 查询路由增强器 | design | design_only | D-OPS/Query Routing Enhancer 查询路由增强器 | Query Routing Enhancer 查询路由增强器 | design | design_only |
| D-OPS/RED方法指标 请求错误延迟 | RED方法指标 请求错误延迟 | design | design_only | D-OPS/RED方法指标 请求错误延迟 | RED方法指标 请求错误延迟 | design | design_only |
| D-OPS/Rate Limiter Modeler 限流器建模器 | Rate Limiter Modeler 限流器建模器 | design | design_only | D-OPS/Rate Limiter Modeler 限流器建模器 | Rate Limiter Modeler 限流器建模器 | design | design_only |
| D-OPS/Real-time Graph Diff Enhancer 实时图差异增强器 | Real-time Graph Diff Enhancer 实时图差异增强器 | design | design_only | D-OPS/Real-time Graph Diff Enhancer 实时图差异增强器 | Real-time Graph Diff Enhancer 实时图差异增强器 | design | design_only |
| D-OPS/Real-time Graph Differ 实时图差异器 | Real-time Graph Differ 实时图差异器 | design | design_only | D-OPS/Real-time Graph Differ 实时图差异器 | Real-time Graph Differ 实时图差异器 | design | design_only |
| D-OPS/Real-time Simulator 实时仿真器 | Real-time Simulator 实时仿真器 | design | design_only | D-OPS/Real-time Simulator 实时仿真器 | Real-time Simulator 实时仿真器 | design | design_only |
| D-OPS/Recovery Validator 恢复验证器 | Recovery Validator 恢复验证器 | design | design_only | D-OPS/Recovery Validator 恢复验证器 | Recovery Validator 恢复验证器 | design | design_only |
| D-OPS/Redis Cluster Sentinel Redis集群/哨兵 | Redis Cluster Sentinel Redis集群/哨兵 | design | design_only | D-OPS/Redis Cluster Sentinel Redis集群/哨兵 | Redis Cluster Sentinel Redis集群/哨兵 | design | design_only |
| D-OPS/Redis内存预测异常检测规则 | Redis内存预测异常检测规则 | design | design_only | D-OPS/Redis内存预测异常检测规则 | Redis内存预测异常检测规则 | design | design_only |
| D-OPS/RemediationExecuted 修复动作执行完成 | RemediationExecuted 修复动作执行完成 | design | design_only | D-OPS/RemediationExecuted 修复动作执行完成 | RemediationExecuted 修复动作执行完成 | design | design_only |
| D-OPS/RemediationRolledBack 修复回滚 | RemediationRolledBack 修复回滚 | design | design_only | D-OPS/RemediationRolledBack 修复回滚 | RemediationRolledBack 修复回滚 | design | design_only |
| D-OPS/Repair Roller 修复回滚器 | Repair Roller 修复回滚器 | design | design_only | D-OPS/Repair Roller 修复回滚器 | Repair Roller 修复回滚器 | design | design_only |
| D-OPS/Repair Suggester 修复建议器 | Repair Suggester 修复建议器 | design | design_only | D-OPS/Repair Suggester 修复建议器 | Repair Suggester 修复建议器 | design | design_only |
| D-OPS/Repair Validation Gate 修复验证门禁 | Repair Validation Gate 修复验证门禁 | design | design_only | D-OPS/Repair Validation Gate 修复验证门禁 | Repair Validation Gate 修复验证门禁 | design | design_only |
| D-OPS/Repair Validator 修复验证器 | Repair Validator 修复验证器 | design | design_only | D-OPS/Repair Validator 修复验证器 | Repair Validator 修复验证器 | design | design_only |
| D-OPS/Resilience Evaluator 韧性评估器 | Resilience Evaluator 韧性评估器 | design | design_only | D-OPS/Resilience Evaluator 韧性评估器 | Resilience Evaluator 韧性评估器 | design | design_only |
| D-OPS/Resilience Scorer 韧性评分器 | Resilience Scorer 韧性评分器 | design | design_only | D-OPS/Resilience Scorer 韧性评分器 | Resilience Scorer 韧性评分器 | design | design_only |
| D-OPS/Resource Dependency Capacity Planner 资源依赖容量规划 | Resource Dependency Capacity Planner ... | design | design_only | D-OPS/Resource Dependency Capacity Planner 资源依赖容量规划 | Resource Dependency Capacity Planner ... | design | design_only |
| D-OPS/Retry Storm Predictor 重试风暴预测器 | Retry Storm Predictor 重试风暴预测器 | design | design_only | D-OPS/Retry Storm Predictor 重试风暴预测器 | Retry Storm Predictor 重试风暴预测器 | design | design_only |
| D-OPS/Retry Strategy Modeler 重试策略建模器 | Retry Strategy Modeler 重试策略建模器 | design | design_only | D-OPS/Retry Strategy Modeler 重试策略建模器 | Retry Strategy Modeler 重试策略建模器 | design | design_only |
| D-OPS/Runbook Automator 运维手册自动化 | Runbook Automator 运维手册自动化 | design | design_only | D-OPS/Runbook Automator 运维手册自动化 | Runbook Automator 运维手册自动化 | design | design_only |
| D-OPS/Runtime Architecture 运行时架构 | Runtime Architecture 运行时架构 | design | design_only | D-OPS/Runtime Architecture 运行时架构 | Runtime Architecture 运行时架构 | design | design_only |
| D-OPS/Runtime Dependency Collector 运行时依赖采集器 | Runtime Dependency Collector 运行时依赖采集器 | design | design_only | D-OPS/Runtime Dependency Collector 运行时依赖采集器 | Runtime Dependency Collector 运行时依赖采集器 | design | design_only |
| D-OPS/Runtime vs Static Differ 运行时vs静态差异器 | Runtime vs Static Differ 运行时vs静态差异器 | design | design_only | D-OPS/Runtime vs Static Differ 运行时vs静态差异器 | Runtime vs Static Differ 运行时vs静态差异器 | design | design_only |
| D-OPS/SLA Breach Detector SLA违约检测器 | SLA Breach Detector SLA违约检测器 | design | design_only | D-OPS/SLA Breach Detector SLA违约检测器 | SLA Breach Detector SLA违约检测器 | design | design_only |
| D-OPS/SLA Breach Predictor SLA违约预测器 | SLA Breach Predictor SLA违约预测器 | design | design_only | D-OPS/SLA Breach Predictor SLA违约预测器 | SLA Breach Predictor SLA违约预测器 | design | design_only |
| D-OPS/SLA Definer SLA定义器 | SLA Definer SLA定义器 | design | design_only | D-OPS/SLA Definer SLA定义器 | SLA Definer SLA定义器 | design | design_only |
| D-OPS/SLA Monitor SLA监控器 | SLA Monitor SLA监控器 | design | design_only | D-OPS/SLA Monitor SLA监控器 | SLA Monitor SLA监控器 | design | design_only |
| D-OPS/SLA Report Generator SLA报告生成器 | SLA Report Generator SLA报告生成器 | design | design_only | D-OPS/SLA Report Generator SLA报告生成器 | SLA Report Generator SLA报告生成器 | design | design_only |
| D-OPS/SLA-Aware Traffic Router SLA感知流量路由器 | SLA-Aware Traffic Router SLA感知流量路由器 | design | design_only | D-OPS/SLA-Aware Traffic Router SLA感知流量路由器 | SLA-Aware Traffic Router SLA感知流量路由器 | design | design_only |
| D-OPS/SLO Manager SLO管理 | SLO Manager SLO管理 | design | design_only | D-OPS/SLO Manager SLO管理 | SLO Manager SLO管理 | design | design_only |
| D-OPS/SLO Manager SLO管理器 | SLO Manager SLO管理器 | design | design_only | D-OPS/SLO Manager SLO管理器 | SLO Manager SLO管理器 | design | design_only |
| D-OPS/SLOBreached SLO违约 | SLOBreached SLO违约 | design | design_only | D-OPS/SLOBreached SLO违约 | SLOBreached SLO违约 | design | design_only |
| D-OPS/SLO定义 服务等级目标 | SLO定义 服务等级目标 | design | design_only | D-OPS/SLO定义 服务等级目标 | SLO定义 服务等级目标 | design | design_only |
| D-OPS/SNN Anomaly Detection Enhancer SNN异常检测增强 | SNN Anomaly Detection Enhancer SNN异常检测增强 | design | design_only | D-OPS/SNN Anomaly Detection Enhancer SNN异常检测增强 | SNN Anomaly Detection Enhancer SNN异常检测增强 | design | design_only |
| D-OPS/SNN Dependency Anomaly Detector SNN依赖异常检测器 | SNN Dependency Anomaly Detector SNN依赖... | design | design_only | D-OPS/SNN Dependency Anomaly Detector SNN依赖异常检测器 | SNN Dependency Anomaly Detector SNN依赖... | design | design_only |
| D-OPS/STDP Dynamic Weight Engine STDP脉冲学习动态权重引擎 | STDP Dynamic Weight Engine STDP脉冲学习动态... | design | design_only | D-OPS/STDP Dynamic Weight Engine STDP脉冲学习动态权重引擎 | STDP Dynamic Weight Engine STDP脉冲学习动态... | design | design_only |

> (仅显示前 200 个模块，共 697 个)

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
    subgraph D_OPS["D-OPS feedback-loop"]
        D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry["GAAT Governance-Aware Agent Telemetry 治理感知遥测 design"]
        D_GOVERNANCE_GAAT_Governance_Aware_Telemetry_GAAT["GAAT Governance-Aware Telemetry GAAT治理感知遥测 design"]
        D_GOVERNANCE_Observability_Dashboard["Observability Dashboard 可观测性仪表盘 design"]
        D_GOVERNANCE_Trusted_Telemetry_Plane["Trusted Telemetry Plane 可信遥测平面 design"]
        D_OPS_AI_Agent_Chaos_Experiment_Designer_AI_Agent["AI Agent Chaos Experiment Designer AI Agent混沌实验设计器 design"]
        D_OPS_AI_Autonomous_Operations_Closed_Loop_AI["AI Autonomous Operations Closed Loop AI自治运维闭环 design"]
        D_OPS_AI_Autonomous_Ops_Engine_AI["AI Autonomous Ops Engine AI自治运维引擎 design"]
        D_OPS_AI_Inference_Dependency_Discovery_AI["AI Inference Dependency Discovery AI推理依赖发现 design"]
        D_OPS_API_Rate_Limit_Dependency_Propagator_API["API Rate Limit Dependency Propagator API速率限制依赖传播器 design"]
        D_OPS_API_Traffic_Policy_Mapper_API["API Traffic Policy Mapper API流量策略映射器 design"]
        D_OPS_Adaptive_Scheduler["Adaptive Scheduler 自适应调度器 design"]
        D_OPS_Alert_Fatigue_Management["Alert Fatigue Management 通知疲劳管理 design"]
        D_OPS_Alert_Manager["Alert Manager 告警管理 design"]
        D_OPS_Anomaly_Detection["Anomaly Detection 异常检测 design"]
        D_OPS_Anomaly_Detector["Anomaly Detector 异常检测器 design"]
        D_OPS_Anomaly_Propagation_GNN_Predictor_GNN["Anomaly Propagation GNN Predictor 异常传播GNN预测器 design"]
        D_OPS_Anomaly_Propagation_Tracker["Anomaly Propagation Tracker 异常传播追踪器 design"]
        D_OPS_Application_Layer_Dependency_Supplementer["Application Layer Dependency Supplementer 应用层依赖补充器 design"]
        D_OPS_Asset_Inventory["Asset Inventory 资产盘点 design"]
        D_OPS_Auto_Degradation_Executor["Auto Degradation Executor 自动降级执行器 design"]
        D_OPS_Auto_Dependency_Replacer["Auto Dependency Replacer 自动依赖替换器 design"]
        D_OPS_Auto_Repair_Executor["Auto Repair Executor 自动修复执行器 design"]
        D_OPS_Auto_Rollback_Executor["Auto Rollback Executor 自动回滚执行器 design"]
        D_OPS_Auto_Rollback_Strategy_Selector["Auto Rollback Strategy Selector 自动回滚策略选择器 design"]
        D_OPS_Backup_Recovery_Manager["Backup Recovery Manager 备份与恢复管理器 design"]
        D_OPS_Batch_Simulator["Batch Simulator 批量仿真器 design"]
        D_OPS_Bidirectional_Synchronizer["Bidirectional Synchronizer 双向同步器 design"]
        D_OPS_Blast_Radius_Calculator["Blast Radius Calculator 爆炸半径计算器 design"]
        D_OPS_Blast_Radius_Predictor["Blast Radius Predictor 爆炸半径预测器 design"]
        D_OPS_Bulkhead_Modeler["Bulkhead Modeler 舱壁建模器 design"]
    end
    D_OPS_Blast_Radius_Calculator -.->|import_depends| D_OPS_API_Traffic_Policy_Mapper_API
    D_OPS_API_Traffic_Policy_Mapper_API -.->|import_depends| D_OPS_API_Rate_Limit_Dependency_Propagator_API
    D_OPS_Auto_Degradation_Executor -.->|import_depends| D_OPS_Auto_Rollback_Executor
    D_OPS_Auto_Rollback_Executor -.->|import_depends| D_OPS_Auto_Dependency_Replacer
    D_OPS_Adaptive_Scheduler -.->|import_depends| D_OPS_AI_Agent_Chaos_Experiment_Designer_AI_Agent
    D_ML_SERVE["D-ML_SERVE design"]
    D_OPS_AI_Autonomous_Ops_Engine_AI -.->|contract| D_ML_SERVE
    D_RISK["D-RISK design"]
    D_OPS_AI_Autonomous_Ops_Engine_AI -.->|event| D_RISK
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_OPS_AI_Autonomous_Ops_Engine_AI -.->|contract| D_AUTONOMY_CORE
    D_DATA_ENG["D-DATA_ENG design"]
    D_OPS_AI_Autonomous_Ops_Engine_AI -.->|config_depends| D_DATA_ENG
    D_OPS_Alert_Manager -.->|data| D_DATA_ENG
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_OPS_Alert_Manager -.->|event| D_GOVERNANCE
    D_OPS_Alert_Manager -.->|config_depends| D_GOVERNANCE
    D_OPS_Asset_Inventory -.->|contract| D_AUTONOMY_CORE
    D_TRADING["D-TRADING design"]
    D_OPS_Asset_Inventory -.->|config_depends| D_TRADING
    D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry -.->|import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry -.->|data| D_INFRA_RUNTIME
    D_SIGNAL["D-SIGNAL design"]
    D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry -.->|event| D_SIGNAL
    D_INTEGRATION["D-INTEGRATION design"]
    D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry -.->|data| D_INTEGRATION
    D_GOVERNANCE_Trusted_Telemetry_Plane -.->|import_depends| D_GOVERNANCE
    D_GOVERNANCE_Trusted_Telemetry_Plane -.->|contract| D_GOVERNANCE
    D_FRONTEND["D-FRONTEND design"]
    D_FRONTEND -.->|contract| D_OPS_AI_Autonomous_Ops_Engine_AI
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_OPS_AI_Autonomous_Ops_Engine_AI
    D_COMPLIANCE -.->|data| D_OPS_AI_Autonomous_Ops_Engine_AI
    D_GOVERNANCE -.->|import_depends| D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry
    D_GOVERNANCE -.->|import_depends| D_GOVERNANCE_Trusted_Telemetry_Plane
    D_COMPLIANCE -.->|contract| D_GOVERNANCE_Trusted_Telemetry_Plane
    D_GOVERNANCE -.->|import_depends| D_GOVERNANCE_GAAT_Governance_Aware_Telemetry_GAAT
    D_COMPLIANCE -.->|data| D_OPS_AI_Autonomous_Operations_Closed_Loop_AI
    D_GOVERNANCE -.->|import_depends| D_GOVERNANCE_Observability_Dashboard
    D_COMPLIANCE -.->|event| D_OPS_Backup_Recovery_Manager
    D_FRONTEND -.->|contract| D_OPS_Alert_Fatigue_Management
    D_FRONTEND -.->|config_depends| D_OPS_Alert_Fatigue_Management
    D_FRONTEND -.->|config_depends| D_OPS_AI_Inference_Dependency_Discovery_AI
    D_DATA_GOV["D-DATA_GOV design"]
    D_DATA_GOV -.->|config_depends| D_OPS_Blast_Radius_Calculator
    D_COMPLIANCE -.->|event| D_OPS_API_Rate_Limit_Dependency_Propagator_API
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_GOVERNANCE_GAAT_Governance_Aware_Agent_Telemetry,D_GOVERNANCE_GAAT_Governance_Aware_Telemetry_GAAT,D_GOVERNANCE_Observability_Dashboard,D_GOVERNANCE_Trusted_Telemetry_Plane,D_OPS_AI_Agent_Chaos_Experiment_Designer_AI_Agent,D_OPS_AI_Autonomous_Operations_Closed_Loop_AI,D_OPS_AI_Autonomous_Ops_Engine_AI,D_OPS_AI_Inference_Dependency_Discovery_AI,D_OPS_API_Rate_Limit_Dependency_Propagator_API,D_OPS_API_Traffic_Policy_Mapper_API,D_OPS_Adaptive_Scheduler,D_OPS_Alert_Fatigue_Management,D_OPS_Alert_Manager,D_OPS_Anomaly_Detection,D_OPS_Anomaly_Detector,D_OPS_Anomaly_Propagation_GNN_Predictor_GNN,D_OPS_Anomaly_Propagation_Tracker,D_OPS_Application_Layer_Dependency_Supplementer,D_OPS_Asset_Inventory,D_OPS_Auto_Degradation_Executor,D_OPS_Auto_Dependency_Replacer,D_OPS_Auto_Repair_Executor,D_OPS_Auto_Rollback_Executor,D_OPS_Auto_Rollback_Strategy_Selector,D_OPS_Backup_Recovery_Manager,D_OPS_Batch_Simulator,D_OPS_Bidirectional_Synchronizer,D_OPS_Blast_Radius_Calculator,D_OPS_Blast_Radius_Predictor,D_OPS_Bulkhead_Modeler design
    class D_ML_SERVE,D_RISK,D_AUTONOMY_CORE,D_DATA_ENG,D_GOVERNANCE,D_TRADING,D_INFRA_RUNTIME,D_SIGNAL,D_INTEGRATION,D_FRONTEND,D_COMPLIANCE,D_DATA_GOV external_design
```

> (依赖图最多显示前 30 个节点，共 697 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 72 | contract,config_depends,import_depends,runtime,test_depends,event,data | D-GOVERNANCE | 72 | contract,config_depends,import_depends,runtime,test_depends,event,data |
| D-INFRA_RUNTIME | 58 | import_depends,test_depends,domain_dependency,event,contract,data,config_depends | D-INFRA_RUNTIME | 58 | import_depends,test_depends,domain_dependency,event,contract,data,config_depends |
| D-RISK | 51 | event,contract,data,config_depends | D-RISK | 51 | event,contract,data,config_depends |
| D-AUTONOMY_CORE | 42 | runtime,import_depends,test_depends,data,contract,event,config_depends | D-AUTONOMY_CORE | 42 | runtime,import_depends,test_depends,data,contract,event,config_depends |
| D-SECURITY | 36 | import_depends,test_depends,data,contract,config_depends,event | D-SECURITY | 36 | import_depends,test_depends,data,contract,config_depends,event |
| D-INTEGRATION | 29 | import_depends,runtime,data,contract,event,config_depends | D-INTEGRATION | 29 | import_depends,runtime,data,contract,event,config_depends |
| D-SIGNAL | 26 | contract,event,data,config_depends | D-SIGNAL | 26 | contract,event,data,config_depends |
| D-FACTOR | 25 | runtime,contract,event,config_depends,data | D-FACTOR | 25 | runtime,contract,event,config_depends,data |
| D-MKT_DATA | 19 | contract,event,config_depends,data | D-MKT_DATA | 19 | contract,event,config_depends,data |
| D-SHARED | 14 | import_depends,test_depends | D-SHARED | 14 | import_depends,test_depends |
| D-AUTONOMY_PERM | 14 | data,event,contract,config_depends | D-AUTONOMY_PERM | 14 | data,event,contract,config_depends |
| D-EX_SOR | 13 | contract,data,event | D-EX_SOR | 13 | contract,data,event |
| D-INTELLIGENCE | 12 | data,event,contract,config_depends | D-INTELLIGENCE | 12 | data,event,contract,config_depends |
| D-ML_SERVE | 11 | contract,event,data,config_depends | D-ML_SERVE | 11 | contract,event,data,config_depends |
| D-TRADING | 10 | import_depends,config_depends,data,contract | D-TRADING | 10 | import_depends,config_depends,data,contract |
| D-EX_CORE | 10 | data,contract,event | D-EX_CORE | 10 | data,contract,event |
| D-DATA_ENG | 9 | config_depends,contract,data,event | D-DATA_ENG | 9 | config_depends,contract,data,event |
| D-PF_ALLOC | 8 | data,event,contract,config_depends | D-PF_ALLOC | 8 | data,event,contract,config_depends |
| D-KNOWLEDGE | 8 | data,contract,event | D-KNOWLEDGE | 8 | data,contract,event |
| D-SIMULATION | 7 | contract,event,data | D-SIMULATION | 7 | contract,event,data |
| D-PF_CORE | 7 | contract,event,data | D-PF_CORE | 7 | contract,event,data |
| D-REPORTING | 5 | data,contract | D-REPORTING | 5 | data,contract |
| D-ML_TRAIN | 5 | contract,config_depends | D-ML_TRAIN | 5 | contract,config_depends |
| D-POSITION | 4 | contract,event,config_depends | D-POSITION | 4 | contract,event,config_depends |
| D-ALT_DATA | 4 | contract,event | D-ALT_DATA | 4 | contract,event |
| D-GOV_AUDIT | 3 | import_depends,test_depends,domain_dependency | D-GOV_AUDIT | 3 | import_depends,test_depends,domain_dependency |
| D-BEHAVIORAL_AUDIT | 3 | import_depends,runtime | D-BEHAVIORAL_AUDIT | 3 | import_depends,runtime |
| D-SELL_DECISION | 1 | config_depends | D-SELL_DECISION | 1 | config_depends |
| D-GOV_DRIFT | 1 | import_depends | D-GOV_DRIFT | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 425 | import_depends,runtime,test_depends,config_depends | D-GOVERNANCE | 425 | import_depends,runtime,test_depends,config_depends |
| D-COMPLIANCE | 62 | contract,data,config_depends,event | D-COMPLIANCE | 62 | contract,data,config_depends,event |
| D-INFRA_OPS | 26 | import_depends,data,config_depends,contract,event | D-INFRA_OPS | 26 | import_depends,data,config_depends,contract,event |
| D-FRONTEND | 21 | contract,import_depends,data,config_depends,event | D-FRONTEND | 21 | contract,import_depends,data,config_depends,event |
| D-SHARED | 6 | import_depends | D-SHARED | 6 | import_depends |
| D-DATA_GOV | 6 | data,contract,config_depends | D-DATA_GOV | 6 | data,contract,config_depends |
| D-TRADING | 3 | runtime,import_depends | D-TRADING | 3 | runtime,import_depends |
| D-GOV_AUDIT | 3 | test_depends,import_depends | D-GOV_AUDIT | 3 | test_depends,import_depends |
| D-INFRA_RUNTIME | 2 | import_depends | D-INFRA_RUNTIME | 2 | import_depends |
| D-CROSS_ASSET | 2 | event,data | D-CROSS_ASSET | 2 | event,data |
| D-INTEGRATION | 1 | import_depends | D-INTEGRATION | 1 | import_depends |
| D-DATA_SEC | 1 | import_depends | D-DATA_SEC | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
