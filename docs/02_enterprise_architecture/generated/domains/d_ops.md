---
doc_type: domain_architecture_doc
title: D-OPS feedback-loop架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-OPS feedback-loop架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-OPS |
| 域名称 | feedback-loop |
| 架构层 | L1_platform |
| 模块总数 | 641 |
| 设计态模块 | 259 |
| 原型态模块 | 375 |
| 生产态模块 | 1 |
| 容量 | 1/150 (正常) |
| 描述 | 反馈收集器(collectors) |

## 模块清单

共 641 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-OPS/AI Agent Chaos Experiment Designer AI Agent混沌实验设计器 |  | design_only | design | 0 | 0 |
| D-OPS/AI Autonomous Operations Closed Loop AI自治运维闭环 |  | design_only | design | 0 | 0 |
| D-OPS/AI Autonomous Ops Engine AI自治运维引擎 |  | design_only | design | 0 | 0 |
| D-OPS/AI Inference Dependency Discovery AI推理依赖发现 |  | design_only | design | 0 | 0 |
| D-OPS/API Rate Limit Dependency Propagator API速率限制依赖传播器 |  | design_only | design | 0 | 0 |
| D-OPS/API Traffic Policy Mapper API流量策略映射器 |  | design_only | design | 0 | 0 |
| D-OPS/Adaptive Scheduler 自适应调度器 |  | design_only | design | 0 | 0 |
| D-OPS/Alert Fatigue Management 通知疲劳管理 |  | design_only | design | 0 | 0 |
| D-OPS/Alert Manager 告警管理 |  | design_only | design | 0 | 0 |
| D-OPS/Anomaly Detection 异常检测 |  | design_only | design | 0 | 0 |
| D-OPS/Anomaly Detector 异常检测器 |  | design_only | design | 0 | 0 |
| D-OPS/Anomaly Propagation GNN Predictor 异常传播GNN预测器 |  | design_only | design | 0 | 0 |
| D-OPS/Anomaly Propagation Tracker 异常传播追踪器 |  | design_only | design | 0 | 0 |
| D-OPS/Application Layer Dependency Supplementer 应用层依赖补充器 |  | design_only | design | 0 | 0 |
| D-OPS/Asset Inventory 资产盘点 |  | design_only | design | 0 | 0 |
| D-OPS/Auto Degradation Executor 自动降级执行器 |  | design_only | design | 0 | 0 |
| D-OPS/Auto Dependency Replacer 自动依赖替换器 |  | design_only | design | 0 | 0 |
| D-OPS/Auto Repair Executor 自动修复执行器 |  | design_only | design | 0 | 0 |
| D-OPS/Auto Rollback Executor 自动回滚执行器 |  | design_only | design | 0 | 0 |
| D-OPS/Auto Rollback Strategy Selector 自动回滚策略选择器 |  | design_only | design | 0 | 0 |
| D-OPS/Backup Recovery Manager 备份与恢复管理器 |  | design_only | design | 0 | 0 |
| D-OPS/Batch Simulator 批量仿真器 |  | design_only | design | 0 | 0 |
| D-OPS/Bidirectional Synchronizer 双向同步器 |  | design_only | design | 0 | 0 |
| D-OPS/Blast Radius Calculator 爆炸半径计算器 |  | design_only | design | 0 | 0 |
| D-OPS/Blast Radius Predictor 爆炸半径预测器 |  | design_only | design | 0 | 0 |
| D-OPS/Bulkhead Modeler 舱壁建模器 |  | design_only | design | 0 | 0 |
| D-OPS/Bus Factor Defense 巴士因子防御 |  | design_only | design | 0 | 0 |
| D-OPS/Capacity Assurance 容量保障 |  | design_only | design | 0 | 0 |
| D-OPS/Capacity Planning Resource Prediction 容量规划与资源预测 |  | design_only | design | 0 | 0 |
| D-OPS/Carbon Budget Tracker 碳预算追踪器 |  | design_only | design | 0 | 0 |
| D-OPS/Carbon Budget Tracking Enhancer 碳预算追踪增强器 |  | design_only | design | 0 | 0 |
| D-OPS/Carbon Intensity API Integrator 碳强度API集成器 |  | design_only | design | 0 | 0 |
| D-OPS/Carbon-Aware SDK v2 Integrator Carbon-Aware SDK v2集成器 |  | design_only | design | 0 | 0 |
| D-OPS/Cascade Fault Generator 级联故障生成器 |  | design_only | design | 0 | 0 |
| D-OPS/Causal Inference Correlator 因果推断关联器 |  | design_only | design | 0 | 0 |
| D-OPS/Change Management Engine 变更管理引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Change Management 变更管理 |  | design_only | design | 0 | 0 |
| D-OPS/Change Manager 变更管理器 |  | design_only | design | 0 | 0 |
| D-OPS/Change Notification Enhancer 变更通知增强器 |  | design_only | design | 0 | 0 |
| D-OPS/Change Notifier 变更通知器 |  | design_only | design | 0 | 0 |
| D-OPS/Chaos Engineering Engine 混沌工程引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Chaos Engineering Fault Injection 混沌工程与故障注入 |  | design_only | design | 0 | 0 |
| D-OPS/Chaos Experiment Dependency Graph Builder 混沌实验依赖图构建器 |  | design_only | design | 0 | 0 |
| D-OPS/Chaos Experiment Dependency Validator 混沌实验依赖验证器 |  | design_only | design | 0 | 0 |
| D-OPS/Chaos Result Knowledge Base 混沌结果知识库 |  | design_only | design | 0 | 0 |
| D-OPS/Circuit Breaker Dependency Graph Builder 熔断器依赖图构建器 |  | design_only | design | 0 | 0 |
| D-OPS/Circuit Breaker Modeler 熔断器建模器 |  | design_only | design | 0 | 0 |
| D-OPS/Cloud-Edge-Device Scheduler 云-边-端调度器 |  | design_only | design | 0 | 0 |
| D-OPS/Conditional Dependency Activation Detector 条件依赖激活检测器 |  | design_only | design | 0 | 0 |
| D-OPS/Configuration Manager 配置管理 |  | design_only | design | 0 | 0 |
| D-OPS/Critical Path Fault Generator 关键路径故障生成器 |  | design_only | design | 0 | 0 |
| D-OPS/Cross-Domain Ops Event Chain Tracking 跨域运维事件链追踪 |  | design_only | design | 0 | 0 |
| D-OPS/Cross-Env Dependency Diff Analyzer 跨环境依赖差异分析 |  | design_only | design | 0 | 0 |
| D-OPS/Cross-Language Dependency Chain Fixer 跨语言依赖链修复器 |  | design_only | design | 0 | 0 |
| D-OPS/D-OPS |  | design_only | design | 0 | 0 |
| D-OPS/DNS Dependency Discoverer DNS依赖发现器 |  | design_only | design | 0 | 0 |
| D-OPS/DNS Dependency Discovery Enhancer DNS依赖发现增强 |  | design_only | design | 0 | 0 |
| D-OPS/DNS Query Collector DNS查询采集器 |  | design_only | design | 0 | 0 |
| D-OPS/DR Manager 灾难恢复 |  | design_only | design | 0 | 0 |
| D-OPS/DSV Encoding Enhancer DSV编码增强 |  | design_only | design | 0 | 0 |
| D-OPS/Data Quality SLA Monitor 数据质量SLA监控 |  | design_only | design | 0 | 0 |
| D-OPS/Degradation Chain Validator 降级链验证器 |  | design_only | design | 0 | 0 |
| D-OPS/Degradation Path Modeler 降级路径建模器 |  | design_only | design | 0 | 0 |
| D-OPS/Degradation Strategy Manager 降级策略管理器 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Bottleneck Resource Optimizer 依赖瓶颈资源优化 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Circuit Breaker 依赖断路器 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Cost Tracker 依赖图成本追踪 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Criticality DCS Scoring Enhancer 依赖关键度DCS评分增强 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Criticality Scorer 依赖关键度评分器 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Drift Distance Metric Enhancer 依赖漂移距离度量增强 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Graph Builder 依赖图构建器 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Graph Resilience Scorer 依赖图韧性评分器 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency Health Scoring Engine 依赖健康评分引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Dependency State Vector Encoder 依赖状态向量编码器 |  | design_only | design | 0 | 0 |
| D-OPS/Deploy Order CSP Solver 部署顺序CSP求解器 |  | design_only | design | 0 | 0 |
| D-OPS/Deployment Manager 部署管理 |  | design_only | design | 0 | 0 |
| D-OPS/Differentiable Impact Simulation Enhancer 可微分影响仿真增强 |  | design_only | design | 0 | 0 |
| D-OPS/Differentiable Impact Simulator 可微分影响仿真器 |  | design_only | design | 0 | 0 |
| D-OPS/Disaster Recovery 3-2-1-1-0 灾备架构3-2-1-1-0 |  | design_only | design | 0 | 0 |
| D-OPS/Disaster Recovery Architecture 灾备架构 |  | design_only | design | 0 | 0 |
| D-OPS/Disaster Recovery Engine 灾备引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Distributed Trace Dependency Correlator 分布式追踪依赖关联 |  | design_only | design | 0 | 0 |
| D-OPS/Documentation Drift Anti-Pattern Detection Enhancer 文档漂移反模式检测增强 |  | design_only | design | 0 | 0 |
| D-OPS/Dual Machine Hot Standby 双机热备 |  | design_only | design | 0 | 0 |
| D-OPS/Dynamic Dependency Graph Builder 动态依赖图构建器 |  | design_only | design | 0 | 0 |
| D-OPS/Edge Dependency Constraint Modeler 边缘依赖约束建模器 |  | design_only | design | 0 | 0 |
| D-OPS/Emergency Life Saving Track 应急保命轨 |  | design_only | design | 0 | 0 |
| D-OPS/Emergency Preservation Track 应急保命轨 |  | design_only | design | 0 | 0 |
| D-OPS/Emergency Survival Track 应急保命轨 |  | design_only | design | 0 | 0 |
| D-OPS/EmergencyDegradationTrack 保命轨 |  | design_only | design | 0 | 0 |
| D-OPS/Envoy Dependency Extractor Envoy依赖提取器 |  | design_only | design | 0 | 0 |
| D-OPS/Experiment Recorder 实验记录器 |  | design_only | design | 0 | 0 |
| D-OPS/Experiment Reporter 实验报告器 |  | design_only | design | 0 | 0 |
| D-OPS/External Dependency SLA Monitor 外部依赖SLA监控 |  | design_only | design | 0 | 0 |
| D-OPS/Fault Injector 故障注入器 |  | design_only | design | 0 | 0 |
| D-OPS/Fault Scenario Definer 故障场景定义器 |  | design_only | design | 0 | 0 |
| D-OPS/File Access Collector 文件访问采集器 |  | design_only | design | 0 | 0 |
| D-OPS/File I/O Dependency Discoverer 文件I/O依赖发现器 |  | design_only | design | 0 | 0 |
| D-OPS/File I/O Dependency Discovery Enhancer 文件I/O依赖发现增强 |  | design_only | design | 0 | 0 |
| D-OPS/FinOps Cost Anomaly Detector FinOps成本异常检测 |  | design_only | design | 0 | 0 |
| D-OPS/GPU Scheduling GPU调度上岗 |  | design_only | design | 0 | 0 |
| D-OPS/GPU显存异常检测规则 |  | design_only | design | 0 | 0 |
| D-OPS/GitOps Dependency Resolver GitOps依赖解析器 |  | design_only | design | 0 | 0 |
| D-OPS/Green Deployment Strategist 绿色部署策略器 |  | design_only | design | 0 | 0 |
| D-OPS/Health Check Readiness Probe 健康检查与就绪探针 |  | design_only | design | 0 | 0 |
| D-OPS/Health Monitoring 健康监控 |  | design_only | design | 0 | 0 |
| D-OPS/High-Risk Node Fault Generator 高风险节点故障生成器 |  | design_only | design | 0 | 0 |
| D-OPS/ISO 23247-4 Dependency Entity Model ISO 23247-4依赖实体模型 |  | design_only | design | 0 | 0 |
| D-OPS/ISO 23247-4 Entity Model Enhancer ISO 23247-4实体模型增强 |  | design_only | design | 0 | 0 |
| D-OPS/Implicit Dependency Discoverer 隐式依赖发现器 |  | design_only | design | 0 | 0 |
| D-OPS/Incremental Chaos Validation Enhancer 增量混沌验证增强 |  | design_only | design | 0 | 0 |
| D-OPS/Incremental Chaos Validator 增量混沌验证器 |  | design_only | design | 0 | 0 |
| D-OPS/Integration Health Monitor 集成健康监控器 |  | design_only | design | 0 | 0 |
| D-OPS/Istio Ambient Mode Dependency Enhancer Istio Ambient模式依赖增强 |  | design_only | design | 0 | 0 |
| D-OPS/Istio Config Parser Istio配置解析器 |  | design_only | design | 0 | 0 |
| D-OPS/Istio Policy DSL Generation Enhancer Istio策略DSL生成增强 |  | design_only | design | 0 | 0 |
| D-OPS/Istio Policy DSL Generator Istio策略DSL生成器 |  | design_only | design | 0 | 0 |
| D-OPS/LLM API SLA Monitor LLM API SLA监控 |  | design_only | design | 0 | 0 |
| D-OPS/LLM Hallucination Correlation Misjudgment Filter LLM幻觉关联误判过滤器 |  | design_only | design | 0 | 0 |
| D-OPS/Left Kan Extension Dependency Resolver 左Kan扩展依赖解析器 |  | design_only | design | 0 | 0 |
| D-OPS/Linkerd Policy Generation Enhancer Linkerd策略生成增强 |  | design_only | design | 0 | 0 |
| D-OPS/Linkerd Policy Generator Linkerd策略生成器 |  | design_only | design | 0 | 0 |
| D-OPS/Log Correlator 日志关联器 |  | design_only | design | 0 | 0 |
| D-OPS/Low-Carbon Window Detection Enhancer 低碳窗口检测增强器 |  | design_only | design | 0 | 0 |
| D-OPS/Low-Carbon Window Detector 低碳窗口检测器 |  | design_only | design | 0 | 0 |
| D-OPS/Metric Correlator 指标关联器 |  | design_only | design | 0 | 0 |
| D-OPS/Metric Dependency Anomaly Detector 指标依赖异常检测 |  | design_only | design | 0 | 0 |
| D-OPS/Minimum Blast Radius Calculator 最小爆破半径计算器 |  | design_only | design | 0 | 0 |
| D-OPS/Model Hot Swap 模型热交换 |  | design_only | design | 0 | 0 |
| D-OPS/Monitor Agent 监控Agent |  | design_only | design | 0 | 0 |
| D-OPS/Monitoring System 监控体系 |  | design_only | design | 0 | 0 |
| D-OPS/Multi-Cloud SLA Aggregation Engine 多云SLA聚合引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Network Connection Collector 网络连接采集器 |  | design_only | design | 0 | 0 |
| D-OPS/Network Resilience Scoring Engine 网络韧性评分引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Network Topology Discoverer 网络拓扑发现器 |  | design_only | design | 0 | 0 |
| D-OPS/Network Topology Discovery Enhancer 网络拓扑发现增强 |  | design_only | design | 0 | 0 |
| D-OPS/Neuromorphic Event-Driven Scheduler 神经形态事件驱动调度器 |  | design_only | design | 0 | 0 |
| D-OPS/OTel Auto-Topology Builder OTel自动拓扑构建器 |  | design_only | design | 0 | 0 |
| D-OPS/OTel Collector Integration OTel Collector集成 |  | design_only | design | 0 | 0 |
| D-OPS/OTel GenAI SemConv Integrator OTel GenAI语义约定集成器 |  | design_only | design | 0 | 0 |
| D-OPS/OTel GenAI Semantic Conventions OTel GenAI语义约定 |  | design_only | design | 0 | 0 |
| D-OPS/OpenTelemetry 2.0 |  | design_only | design | 0 | 0 |
| D-OPS/OpenTelemetry分布式追踪 分布式追踪 |  | design_only | design | 0 | 0 |
| D-OPS/Operations Specification 运维规格 |  | design_only | design | 0 | 0 |
| D-OPS/Ops Automation Runbook Engine 运维自动化Runbook引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Ops Foundation 运维基础 |  | design_only | design | 0 | 0 |
| D-OPS/OpsIncident 运维事件 |  | design_only | design | 0 | 0 |
| D-OPS/Paper Live Transition 模拟实盘转换 |  | design_only | design | 0 | 0 |
| D-OPS/Performance Baseline 性能基线 |  | design_only | design | 0 | 0 |
| D-OPS/Performance Profiler 性能分析器 |  | design_only | design | 0 | 0 |
| D-OPS/Post Live Verification 上线后验证 |  | design_only | design | 0 | 0 |
| D-OPS/Post Process 后处理 |  | design_only | design | 0 | 0 |
| D-OPS/Predictive System Maintenance 预测性系统维护 |  | design_only | design | 0 | 0 |
| D-OPS/Process Call Collector 进程调用采集器 |  | design_only | design | 0 | 0 |
| D-OPS/Process Relationship Tracker 进程关系追踪器 |  | design_only | design | 0 | 0 |
| D-OPS/Process Relationship Tracking Enhancer 进程关系追踪增强 |  | design_only | design | 0 | 0 |
| D-OPS/Progressive Delivery Dependency Checker 渐进式交付依赖检查器 |  | design_only | design | 0 | 0 |
| D-OPS/PubGrub Version Solver PubGrub版本求解器 |  | design_only | design | 0 | 0 |
| D-OPS/Query Router 查询路由器 |  | design_only | design | 0 | 0 |
| D-OPS/Query Routing Enhancer 查询路由增强器 |  | design_only | design | 0 | 0 |
| D-OPS/RED方法指标 请求错误延迟 |  | design_only | design | 0 | 0 |
| D-OPS/Rate Limiter Modeler 限流器建模器 |  | design_only | design | 0 | 0 |
| D-OPS/Real-time Graph Diff Enhancer 实时图差异增强器 |  | design_only | design | 0 | 0 |
| D-OPS/Real-time Graph Differ 实时图差异器 |  | design_only | design | 0 | 0 |
| D-OPS/Real-time Simulator 实时仿真器 |  | design_only | design | 0 | 0 |
| D-OPS/Recovery Validator 恢复验证器 |  | design_only | design | 0 | 0 |
| D-OPS/Redis Cluster Sentinel Redis集群/哨兵 |  | design_only | design | 0 | 0 |
| D-OPS/Redis内存预测异常检测规则 |  | design_only | design | 0 | 0 |
| D-OPS/RemediationExecuted 修复动作执行完成 |  | design_only | design | 0 | 0 |
| D-OPS/RemediationRolledBack 修复回滚 |  | design_only | design | 0 | 0 |
| D-OPS/Repair Roller 修复回滚器 |  | design_only | design | 0 | 0 |
| D-OPS/Repair Suggester 修复建议器 |  | design_only | design | 0 | 0 |
| D-OPS/Repair Validation Gate 修复验证门禁 |  | design_only | design | 0 | 0 |
| D-OPS/Repair Validator 修复验证器 |  | design_only | design | 0 | 0 |
| D-OPS/Resilience Evaluator 韧性评估器 |  | design_only | design | 0 | 0 |
| D-OPS/Resilience Scorer 韧性评分器 |  | design_only | design | 0 | 0 |
| D-OPS/Resource Dependency Capacity Planner 资源依赖容量规划 |  | design_only | design | 0 | 0 |
| D-OPS/Retry Storm Predictor 重试风暴预测器 |  | design_only | design | 0 | 0 |
| D-OPS/Retry Strategy Modeler 重试策略建模器 |  | design_only | design | 0 | 0 |
| D-OPS/Runbook Automator 运维手册自动化 |  | design_only | design | 0 | 0 |
| D-OPS/Runtime Architecture 运行时架构 |  | design_only | design | 0 | 0 |
| D-OPS/Runtime Dependency Collector 运行时依赖采集器 |  | design_only | design | 0 | 0 |
| D-OPS/Runtime vs Static Differ 运行时vs静态差异器 |  | design_only | design | 0 | 0 |
| D-OPS/SLA Breach Detector SLA违约检测器 |  | design_only | design | 0 | 0 |
| D-OPS/SLA Breach Predictor SLA违约预测器 |  | design_only | design | 0 | 0 |
| D-OPS/SLA Definer SLA定义器 |  | design_only | design | 0 | 0 |
| D-OPS/SLA Monitor SLA监控器 |  | design_only | design | 0 | 0 |
| D-OPS/SLA Report Generator SLA报告生成器 |  | design_only | design | 0 | 0 |
| D-OPS/SLA-Aware Traffic Router SLA感知流量路由器 |  | design_only | design | 0 | 0 |
| D-OPS/SLO Manager SLO管理 |  | design_only | design | 0 | 0 |
| D-OPS/SLO Manager SLO管理器 |  | design_only | design | 0 | 0 |
| D-OPS/SLOBreached SLO违约 |  | design_only | design | 0 | 0 |
| D-OPS/SLO定义 服务等级目标 |  | design_only | design | 0 | 0 |
| D-OPS/SNN Anomaly Detection Enhancer SNN异常检测增强 |  | design_only | design | 0 | 0 |
| D-OPS/SNN Dependency Anomaly Detector SNN依赖异常检测器 |  | design_only | design | 0 | 0 |
| D-OPS/STDP Dynamic Weight Engine STDP脉冲学习动态权重引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Script System 脚本系统 |  | design_only | design | 0 | 0 |
| D-OPS/Self-Healing Policy Engine 自愈策略引擎 |  | design_only | design | 0 | 0 |
| D-OPS/Self-Healing Strategy Selector 自愈策略选择器 |  | design_only | design | 0 | 0 |
| D-OPS/Semantic Convention Integrator 语义约定集成器 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 641 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-GOVERNANCE | 56 | contract,config_depends,import_depends,runtime,domain_dependency,event,data |
| D-RISK | 50 | event,contract,data,config_depends |
| D-INFRA_RUNTIME | 48 | import_depends,domain_dependency,event,contract,data,config_depends |
| D-AUTONOMY_CORE | 37 | runtime,import_depends,data,contract,event,config_depends |
| D-SECURITY | 34 | import_depends,data,contract,config_depends,event |
| D-INTEGRATION | 27 | import_depends,runtime,data,contract,event,config_depends |
| D-SIGNAL | 25 | contract,event,data,config_depends |
| D-FACTOR | 25 | runtime,contract,event,config_depends,data |
| D-MKT_DATA | 18 | contract,event,data,config_depends |
| D-EX_SOR | 13 | contract,data,event |
| D-AUTONOMY_PERM | 13 | data,event,contract,config_depends |
| D-INTELLIGENCE | 12 | data,event,contract,config_depends |
| D-ML_SERVE | 11 | contract,event,data,config_depends |
| D-TRADING | 10 | import_depends,config_depends,data,contract |
| D-EX_CORE | 10 | data,contract,event |
| D-DATA_ENG | 9 | config_depends,contract,data,event |
| D-PF_ALLOC | 8 | data,event,contract,config_depends |
| D-KNOWLEDGE | 8 | data,contract,event |
| D-SIMULATION | 7 | contract,event,data |
| D-SHARED | 7 | import_depends |
| D-PF_CORE | 7 | contract,event,data |
| D-REPORTING | 5 | data,contract |
| D-ML_TRAIN | 5 | contract,config_depends |
| D-POSITION | 4 | contract,event,config_depends |
| D-ALT_DATA | 4 | contract,event |
| D-BEHAVIORAL_AUDIT | 2 | runtime,import_depends |
| D-SELL_DECISION | 1 | config_depends |
| D-GOV_DRIFT | 1 | import_depends |
| D-GOV_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 422 | import_depends,runtime,test_depends,config_depends |
| D-COMPLIANCE | 61 | contract,data,config_depends,event |
| D-INFRA_OPS | 26 | import_depends,data,config_depends,contract,event |
| D-FRONTEND | 21 | contract,import_depends,data,config_depends,event |
| D-SHARED | 6 | import_depends |
| D-DATA_GOV | 6 | data,contract,config_depends |
| D-TRADING | 3 | runtime,import_depends |
| D-INFRA_RUNTIME | 2 | import_depends |
| D-CROSS_ASSET | 2 | event,data |
| D-INTEGRATION | 1 | import_depends |
| D-DATA_SEC | 1 | import_depends |

## 域内依赖图

详见 [d_ops_dependency.mmd](d_ops_dependency.mmd)
