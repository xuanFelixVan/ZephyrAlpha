---
doc_type: domain_architecture_doc
title: D-INFRA_RUNTIME runtime_integration架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-INFRA_RUNTIME runtime_integration架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-INFRA_RUNTIME |
| 域名称 | runtime_integration |
| 架构层 | L0_infrastructure |
| 模块总数 | 726 |
| 设计态模块 | 311 |
| 原型态模块 | 0 |
| 生产态模块 | 409 |
| 容量 | 1/150 (正常) |
| 描述 | 运行时集成层 |

## 模块清单

共 726 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-INFRA-RUNTIME/A-Share Diffusion Model Data Augmentation A股扩散模型数据增强 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/AB Test Dependency Mapper AB测试依赖映射器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/API Documentation Synchronizer API文档同步器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/API Version Compatibility Detector API版本兼容检测器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/API Version Manager API版本管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Alert Escalation Strategy Engine 告警升级策略引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Alert Silence Manager 告警静默管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Alternative Data Source Expansion 另类数据源扩展 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/App 包装器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Application State Snapshotter 应用状态快照器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Architecture Compliance Checker 架构合规检查器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Architecture Evolution Planner 架构演进规划器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Architecture Recommendation Engine 架构推荐引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Automated Code Reviewer 自动代码审查器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Bandwidth Optimizer 带宽优化 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Base 基础 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Batch Data Processor 批量数据处理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Blue-Green Dependency Mapper 蓝绿依赖映射器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Blueprint Code Sync 蓝图代码同步 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/CPU Core Allocation Manager CPU核心分配管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cache Data Preloader 缓存数据预加载器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cache Warmup Manager 缓存预热管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Canary Dependency Mapper 金丝雀依赖映射器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Capacity Alert 容量告警 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/CapacityThresholdBreached 容量阈值突破事件 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Causal ML 深度补充 因果ML深度补充 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/ChromaDB Vector Database ChromaDB向量数据库 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Circular Dependency Detector 循环依赖检测器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/ClickHouse Database ClickHouse数据库 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Clock Sync Service 时钟同步服务 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Change Impact Analyzer 代码变更影响分析器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Complexity Analyzer 代码复杂度分析器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Duplication Detector 代码重复检测器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Security Static Analyzer 代码安全静态分析器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Standard Enforcer 代码规范强制执行器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Structure Visualizer 代码结构可视化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Code Template Engine 代码模板引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cold Start Optimizer 冷启动优化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cold Storage 冷存储 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cold平面 冷平面 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Communication Protocol Adapter 通信协议适配器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/ConfigManager 配置管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Change Notifier 配置变更通知器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Code Generator 配置代码生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Dependency Mapper 配置依赖映射器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Diff Detector 配置差异检测器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Encryption Manager 配置加密管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Hot Update Engine 配置热更新引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Manager 配置管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Merge Engine 配置合并引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Configuration Validation Engine 配置校验引擎 |  | design_only | design | 0 | 0 |
| ...FRA-RUNTIME/Configuration Version Management & Rollback Framework 配置版本管理与回滚框架 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Conformal Prediction 共形预测 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Connection Pool Manager 连接池管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Container Image Cache Manager 容器镜像缓存管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Container Orchestrator 容器编排器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Container Resource Isolator 容器资源隔离器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Continuous Improvement Engine 持续改进引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Conversation Context Compressor 对话上下文压缩 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cross-Module Interface Registry 跨模块接口注册中心 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cross-Origin Resource Sharing Manager 跨域资源共享管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cross-Phase State Propagator 跨阶段状态传递器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Cybersecurity Shield 网络安全防护组件 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/D-INFRA |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/D-INFRA-RUNTIME |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/DAO Layer Code Generator DAO层代码生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Aggregation View Manager 数据聚合视图管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Buffer Pool Manager 数据缓冲池管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Compression Manager 数据压缩管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Format Version Coordinator 数据格式版本协调器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Migration Script Generator 数据迁移脚本生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Model Generator 数据模型生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Source Star Rating Dynamic Updater 数据源星级评分动态更新器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Sovereignty Manager 数据主权管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Transfer Validator 数据传输校验器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Transformation Performance Optimizer 数据转换性能优化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Data Transformation Pipeline Orchestrator 数据转换管线编排器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Database Layer 数据库层 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Database Schema Synchronizer 数据库Schema同步器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/DegradationTriggered 降级触发事件 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Deliverable Version Tracker 交付物版本追踪器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Dependency Conflict Resolver 依赖冲突解决器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Dependency Graph Visualization Renderer 依赖图可视化渲染器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Dependency Security Vulnerability Scanner 依赖安全漏洞扫描器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Dependency Upgrade Compatibility Checker 依赖升级兼容性检查器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Dependency Version Lock Manager 依赖版本锁定管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Dependency Visualizer 依赖可视化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Deployment Topology Manager 部署拓扑管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Development Plan Visualizer 开发计划可视化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Distributed Lock Manager 分布式锁管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Document Link Validator 文档链接验证器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Document Search Indexer 文档搜索索引器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Document Template Engine 文档模板引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Document Version Manager 文档版本管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Domain-Driven Design Validator 领域驱动设计校验器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/DuckDB Database DuckDB数据库 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Elastic Scaling Manager 弹性伸缩管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Endpoint Response Format Validator 端点响应格式校验器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Environment Configuration Layering Manager 环境配置分层管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Environment Manager 环境管理 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Environment Variable Manager 环境变量管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Error Handling Code Generator 错误处理代码生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/EventBus 事件总线 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/EventStoreDB Event Store EventStoreDB事件存储 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Experiment and Resilience Testing 实验与韧性测试 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/FAISS Vector Search FAISS向量检索 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Factor Warmup Manager 因子预热管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Failover Coordinator 故障转移协调器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Faiss GPU Vector Search Faiss GPU向量搜索 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Feature Drift & Concept Drift Detection 特征漂移与概念漂移检测 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Feature Lifecycle Manager 功能生命周期管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Field Mapping Converter 字段映射转换器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Financial Time Series Data Augmentation 金融时序数据增强 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Compute Pipeline Manager GPU计算管线管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Inference Training Dynamic Allocator GPU推理训练动态分配器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Kernel Launch Optimizer GPU内核启动优化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU MPS多进程并发 GPU Multi-Process Service |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Memory Transfer Optimizer GPU内存传输优化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Programming Abstraction Layer GPU编程抽象层 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Resource Monitor GPU资源监控器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU Scheduler GPU调度器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPUOOMDetected GPU OOM检测事件 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU调度上岗+热交换 GPU调度 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/GPU调度层 GPU调度 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Global Dependency Graph Calculator 全局依赖图计算器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Governance Adapter 治理适配器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Governance Protocol 治理协议 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Graceful Shutdown Coordinator 优雅关闭协调器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Graph Neural Network for Stock Relations 图神经网络用于股票关系建模 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Hardware Accelerator 硬件加速器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/High Performance HA Framework 高性能高可用保障框架 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Hot Storage 热存储 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Hot↔Warm必须通过IPC协议通信 Hot-Warm IPC Protocol |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Hot平面 热平面 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Inference Engine Warmer 推理引擎预热器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Infrastructure Status 基础设施状态 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Infrastructure Topology Visualizer 基础设施拓扑可视化器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/InfrastructureAlert 基础设施告警 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/InfrastructureNode 基础设施节点 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Inter-Layer Data Format Converter & Validator 层间数据格式转换与校验器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Inter-Module Communication Protocol Manager 模块间通信协议管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Inter-Process Communication Manager 进程间通信管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Interface Mock Generator 接口Mock生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Iteration Cycle Tracker 迭代周期追踪器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Kafka Message Queue Kafka消息队列 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Knowledge Base Data Sovereignty 知识库数据主权管理 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Knowledge Base Indexer 知识库索引器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/LLM Agent for Fundamental Analysis 大语言模型Agent用于基本面分析 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Learning System Bridge Declaration 学习系统桥接声明 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Live Data to Research Domain Feedback Channel 实盘数据→研究域反馈通道 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Load Balancing Strategy Engine 负载均衡策略引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Local First Architecture 本地优先架构 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/MCP Sentinel System Monitor MCP哨兵系统监控器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Mamba/SSM State Space Model Mamba/SSM状态空间模型 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Market Microstructure Deep Modeling 市场微观结构深度建模 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Message Queue Manager 消息队列管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Message Queue 消息队列 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Metric Anomaly Detector 指标异常检测器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Milestone Dependency Validator 里程碑依赖校验器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/MinIO Object Storage MinIO对象存储 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Model Registry & Experiment Management 模型注册与实验管理 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Model Warmup Manager 模型预热管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Configuration Aggregator 模块配置聚合器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Dependency Injector 模块依赖注入器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Documentation Indexer 模块文档索引器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Exception Boundary Manager 模块异常边界管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Feature Toggle Manager 模块功能开关管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Health Checker 模块健康检查器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Hot Update Manager 模块热更新管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Interface Contract Manager 模块接口契约管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Lifecycle Manager 模块生命周期管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Log Aggregator 模块日志聚合器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Metrics Collector 模块度量采集器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Performance Profiler 模块性能分析器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Registry 模块注册中心 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Sandbox Isolator 模块沙箱隔离器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Test Runner 模块测试运行器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Module Version Dependency Resolver 模块版本依赖解析器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Monitoring Dashboard Process 监控面板进程 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Monitoring Data Aggregator 监控数据聚合器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Multi-Device State Coordinator 多端状态协调器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Multi-Modal Input Router 多模态输入路由 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Multi-Process Isolation & Runtime Architecture 多进程隔离与运行时架构 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Multi-Protocol Network Adapter 多协议网络适配器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Multi-Region Collaboration Manager 多区域协同管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/NAS Storage NAS存储 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/NSSM+自研Supervisor 进程守护层 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/NSSM注册Windows服务 NSSM Windows Service |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Network Policy Manager 网络策略管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Node Return Type Contractor 节点返回值类型契约器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/P3 Process Specification P3进程规格 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Package Dependency Graph Generator 包依赖图生成器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Panel Layout Engine 面板布局引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Parquet Columnar Storage Parquet列式存储 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Parquet Parquet列式存储格式 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Path Resolver 路径解析 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Phase Retrospective Analyzer 阶段回顾分析器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Phase Synchronization Coordinator 阶段同步协调器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Plugin System Manager 插件系统管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-RUNTIME/Policy Conflict Auto Detector 策略冲突自动检测器 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 726 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SHARED | 67 | import_depends,contract,data,event |
| D-INTEGRATION | 26 | import_depends |
| D-GOVERNANCE | 19 | import_depends |
| D-GOV_AUDIT | 10 | import_depends |
| D-OPS | 2 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 207 | runtime,import_depends,test_depends,config_depends,data,event,contract |
| D-RISK | 63 | data,contract,config_depends,event |
| D-COMPLIANCE | 62 | contract,data,event,config_depends |
| D-SECURITY | 50 | contract,event,config_depends,data |
| D-OPS | 48 | import_depends,domain_dependency,data,contract,config_depends,event |
| D-INTEGRATION | 31 | domain_dependency,contract,data,event,config_depends |
| D-AUTONOMY_CORE | 31 | config_depends,event,data,contract |
| D-INFRA_OPS | 30 | contract,event,config_depends,data |
| D-SIGNAL | 27 | data,contract,event,config_depends |
| D-MKT_DATA | 24 | contract,data,config_depends,event |
| D-DATA_ENG | 20 | domain_dependency,contract,event,data,config_depends |
| D-FACTOR | 19 | contract,data,event,config_depends |
| D-PF_CORE | 15 | contract,data,event,config_depends |
| D-EX_SOR | 12 | domain_dependency,data,contract,event |
| D-ML_TRAIN | 11 | contract,data,event,config_depends |
| D-REPORTING | 10 | contract,event,config_depends,data |
| D-PF_ALLOC | 10 | event,data,config_depends,contract |
| D-KNOWLEDGE | 10 | event,contract,data |
| D-INTELLIGENCE | 10 | import_depends,data,contract,event,config_depends |
| D-EX_CORE | 10 | contract,event,data,config_depends |
| D-CROSS_ASSET | 9 | contract,config_depends,event,data |
| D-AUTONOMY_PERM | 9 | event,data,config_depends,contract |
| D-TRADING | 7 | contract,import_depends,event,data |
| D-SHARED | 7 | import_depends |
| D-SIMULATION | 6 | event,contract |
| D-ML_SERVE | 6 | domain_dependency,event,contract,data |
| D-FRONTEND | 6 | data,config_depends,contract |
| D-ALT_DATA | 3 | event,data,contract |
| D-POSITION | 2 | event,contract |
| D-DATA_SEC | 2 | config_depends,data |
| D-DATA_GOV | 2 | event |

## 域内依赖图

详见 [d_infra_runtime_dependency.mmd](d_infra_runtime_dependency.mmd)
