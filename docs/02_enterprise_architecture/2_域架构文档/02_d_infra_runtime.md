---
doc_type: domain_architecture_doc
title: D-INFRA_RUNTIME runtime_integration架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 02_d_infra_runtime 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 02 | Number | 02 |
| 域ID | D-INFRA_RUNTIME | Domain ID | D-INFRA_RUNTIME |
| 域名称 | runtime_integration | Domain Name | runtime_integration |
| 层级 | L0_infrastructure | Layer | L0_infrastructure |
| 模块数 | 727 | Module Count | 727 |
| 域内依赖 | 674 | Internal Dependencies | 674 |
| 跨域入边 | 763 | Cross-domain Incoming | 763 |
| 跨域出边 | 125 | Cross-domain Outgoing | 125 |
| 设计态模块 | 311 | Design Modules | 311 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 410 | Production Modules | 410 |
| 容量 | 726/150 (超容) | Capacity | 726/150 (超容) |
| 描述 | 运行时集成层 | Description | 运行时集成层 |

## 模块清单 / Module List

共 727 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-INFRA-RUNTIME/A-Share Diffusion Model Data Augmentation A股扩散模型数据增强 | A-Share Diffusion Model Data Augmenta... | design | design_only | D-INFRA-RUNTIME/A-Share Diffusion Model Data Augmentation A股扩散模型数据增强 | A-Share Diffusion Model Data Augmenta... | design | design_only |
| D-INFRA-RUNTIME/AB Test Dependency Mapper AB测试依赖映射器 | AB Test Dependency Mapper AB测试依赖映射器 | design | design_only | D-INFRA-RUNTIME/AB Test Dependency Mapper AB测试依赖映射器 | AB Test Dependency Mapper AB测试依赖映射器 | design | design_only |
| D-INFRA-RUNTIME/API Documentation Synchronizer API文档同步器 | API Documentation Synchronizer API文档同步器 | design | design_only | D-INFRA-RUNTIME/API Documentation Synchronizer API文档同步器 | API Documentation Synchronizer API文档同步器 | design | design_only |
| D-INFRA-RUNTIME/API Version Compatibility Detector API版本兼容检测器 | API Version Compatibility Detector AP... | design | design_only | D-INFRA-RUNTIME/API Version Compatibility Detector API版本兼容检测器 | API Version Compatibility Detector AP... | design | design_only |
| D-INFRA-RUNTIME/API Version Manager API版本管理器 | API Version Manager API版本管理器 | design | design_only | D-INFRA-RUNTIME/API Version Manager API版本管理器 | API Version Manager API版本管理器 | design | design_only |
| D-INFRA-RUNTIME/Alert Escalation Strategy Engine 告警升级策略引擎 | Alert Escalation Strategy Engine 告警升级... | design | design_only | D-INFRA-RUNTIME/Alert Escalation Strategy Engine 告警升级策略引擎 | Alert Escalation Strategy Engine 告警升级... | design | design_only |
| D-INFRA-RUNTIME/Alert Silence Manager 告警静默管理器 | Alert Silence Manager 告警静默管理器 | design | design_only | D-INFRA-RUNTIME/Alert Silence Manager 告警静默管理器 | Alert Silence Manager 告警静默管理器 | design | design_only |
| D-INFRA-RUNTIME/Alternative Data Source Expansion 另类数据源扩展 | Alternative Data Source Expansion 另类数... | design | design_only | D-INFRA-RUNTIME/Alternative Data Source Expansion 另类数据源扩展 | Alternative Data Source Expansion 另类数... | design | design_only |
| D-INFRA-RUNTIME/App 包装器 | App 包装器 | design | design_only | D-INFRA-RUNTIME/App 包装器 | App 包装器 | design | design_only |
| D-INFRA-RUNTIME/Application State Snapshotter 应用状态快照器 | Application State Snapshotter 应用状态快照器 | design | design_only | D-INFRA-RUNTIME/Application State Snapshotter 应用状态快照器 | Application State Snapshotter 应用状态快照器 | design | design_only |
| D-INFRA-RUNTIME/Architecture Compliance Checker 架构合规检查器 | Architecture Compliance Checker 架构合规检查器 | design | design_only | D-INFRA-RUNTIME/Architecture Compliance Checker 架构合规检查器 | Architecture Compliance Checker 架构合规检查器 | design | design_only |
| D-INFRA-RUNTIME/Architecture Evolution Planner 架构演进规划器 | Architecture Evolution Planner 架构演进规划器 | design | design_only | D-INFRA-RUNTIME/Architecture Evolution Planner 架构演进规划器 | Architecture Evolution Planner 架构演进规划器 | design | design_only |
| D-INFRA-RUNTIME/Architecture Recommendation Engine 架构推荐引擎 | Architecture Recommendation Engine 架构... | design | design_only | D-INFRA-RUNTIME/Architecture Recommendation Engine 架构推荐引擎 | Architecture Recommendation Engine 架构... | design | design_only |
| D-INFRA-RUNTIME/Automated Code Reviewer 自动代码审查器 | Automated Code Reviewer 自动代码审查器 | design | design_only | D-INFRA-RUNTIME/Automated Code Reviewer 自动代码审查器 | Automated Code Reviewer 自动代码审查器 | design | design_only |
| D-INFRA-RUNTIME/Bandwidth Optimizer 带宽优化 | Bandwidth Optimizer 带宽优化 | design | design_only | D-INFRA-RUNTIME/Bandwidth Optimizer 带宽优化 | Bandwidth Optimizer 带宽优化 | design | design_only |
| D-INFRA-RUNTIME/Base 基础 | Base 基础 | design | design_only | D-INFRA-RUNTIME/Base 基础 | Base 基础 | design | design_only |
| D-INFRA-RUNTIME/Batch Data Processor 批量数据处理器 | Batch Data Processor 批量数据处理器 | design | design_only | D-INFRA-RUNTIME/Batch Data Processor 批量数据处理器 | Batch Data Processor 批量数据处理器 | design | design_only |
| D-INFRA-RUNTIME/Blue-Green Dependency Mapper 蓝绿依赖映射器 | Blue-Green Dependency Mapper 蓝绿依赖映射器 | design | design_only | D-INFRA-RUNTIME/Blue-Green Dependency Mapper 蓝绿依赖映射器 | Blue-Green Dependency Mapper 蓝绿依赖映射器 | design | design_only |
| D-INFRA-RUNTIME/Blueprint Code Sync 蓝图代码同步 | Blueprint Code Sync 蓝图代码同步 | design | design_only | D-INFRA-RUNTIME/Blueprint Code Sync 蓝图代码同步 | Blueprint Code Sync 蓝图代码同步 | design | design_only |
| D-INFRA-RUNTIME/CPU Core Allocation Manager CPU核心分配管理器 | CPU Core Allocation Manager CPU核心分配管理器 | design | design_only | D-INFRA-RUNTIME/CPU Core Allocation Manager CPU核心分配管理器 | CPU Core Allocation Manager CPU核心分配管理器 | design | design_only |
| D-INFRA-RUNTIME/Cache Data Preloader 缓存数据预加载器 | Cache Data Preloader 缓存数据预加载器 | design | design_only | D-INFRA-RUNTIME/Cache Data Preloader 缓存数据预加载器 | Cache Data Preloader 缓存数据预加载器 | design | design_only |
| D-INFRA-RUNTIME/Cache Warmup Manager 缓存预热管理器 | Cache Warmup Manager 缓存预热管理器 | design | design_only | D-INFRA-RUNTIME/Cache Warmup Manager 缓存预热管理器 | Cache Warmup Manager 缓存预热管理器 | design | design_only |
| D-INFRA-RUNTIME/Canary Dependency Mapper 金丝雀依赖映射器 | Canary Dependency Mapper 金丝雀依赖映射器 | design | design_only | D-INFRA-RUNTIME/Canary Dependency Mapper 金丝雀依赖映射器 | Canary Dependency Mapper 金丝雀依赖映射器 | design | design_only |
| D-INFRA-RUNTIME/Capacity Alert 容量告警 | Capacity Alert 容量告警 | design | design_only | D-INFRA-RUNTIME/Capacity Alert 容量告警 | Capacity Alert 容量告警 | design | design_only |
| D-INFRA-RUNTIME/CapacityThresholdBreached 容量阈值突破事件 | CapacityThresholdBreached 容量阈值突破事件 | design | design_only | D-INFRA-RUNTIME/CapacityThresholdBreached 容量阈值突破事件 | CapacityThresholdBreached 容量阈值突破事件 | design | design_only |
| D-INFRA-RUNTIME/Causal ML 深度补充 因果ML深度补充 | Causal ML 深度补充 因果ML深度补充 | design | design_only | D-INFRA-RUNTIME/Causal ML 深度补充 因果ML深度补充 | Causal ML 深度补充 因果ML深度补充 | design | design_only |
| D-INFRA-RUNTIME/ChromaDB Vector Database ChromaDB向量数据库 | ChromaDB Vector Database ChromaDB向量数据库 | design | design_only | D-INFRA-RUNTIME/ChromaDB Vector Database ChromaDB向量数据库 | ChromaDB Vector Database ChromaDB向量数据库 | design | design_only |
| D-INFRA-RUNTIME/Circular Dependency Detector 循环依赖检测器 | Circular Dependency Detector 循环依赖检测器 | design | design_only | D-INFRA-RUNTIME/Circular Dependency Detector 循环依赖检测器 | Circular Dependency Detector 循环依赖检测器 | design | design_only |
| D-INFRA-RUNTIME/ClickHouse Database ClickHouse数据库 | ClickHouse Database ClickHouse数据库 | design | design_only | D-INFRA-RUNTIME/ClickHouse Database ClickHouse数据库 | ClickHouse Database ClickHouse数据库 | design | design_only |
| D-INFRA-RUNTIME/Clock Sync Service 时钟同步服务 | Clock Sync Service 时钟同步服务 | design | design_only | D-INFRA-RUNTIME/Clock Sync Service 时钟同步服务 | Clock Sync Service 时钟同步服务 | design | design_only |
| D-INFRA-RUNTIME/Code Change Impact Analyzer 代码变更影响分析器 | Code Change Impact Analyzer 代码变更影响分析器 | design | design_only | D-INFRA-RUNTIME/Code Change Impact Analyzer 代码变更影响分析器 | Code Change Impact Analyzer 代码变更影响分析器 | design | design_only |
| D-INFRA-RUNTIME/Code Complexity Analyzer 代码复杂度分析器 | Code Complexity Analyzer 代码复杂度分析器 | design | design_only | D-INFRA-RUNTIME/Code Complexity Analyzer 代码复杂度分析器 | Code Complexity Analyzer 代码复杂度分析器 | design | design_only |
| D-INFRA-RUNTIME/Code Duplication Detector 代码重复检测器 | Code Duplication Detector 代码重复检测器 | design | design_only | D-INFRA-RUNTIME/Code Duplication Detector 代码重复检测器 | Code Duplication Detector 代码重复检测器 | design | design_only |
| D-INFRA-RUNTIME/Code Security Static Analyzer 代码安全静态分析器 | Code Security Static Analyzer 代码安全静态分析器 | design | design_only | D-INFRA-RUNTIME/Code Security Static Analyzer 代码安全静态分析器 | Code Security Static Analyzer 代码安全静态分析器 | design | design_only |
| D-INFRA-RUNTIME/Code Standard Enforcer 代码规范强制执行器 | Code Standard Enforcer 代码规范强制执行器 | design | design_only | D-INFRA-RUNTIME/Code Standard Enforcer 代码规范强制执行器 | Code Standard Enforcer 代码规范强制执行器 | design | design_only |
| D-INFRA-RUNTIME/Code Structure Visualizer 代码结构可视化器 | Code Structure Visualizer 代码结构可视化器 | design | design_only | D-INFRA-RUNTIME/Code Structure Visualizer 代码结构可视化器 | Code Structure Visualizer 代码结构可视化器 | design | design_only |
| D-INFRA-RUNTIME/Code Template Engine 代码模板引擎 | Code Template Engine 代码模板引擎 | design | design_only | D-INFRA-RUNTIME/Code Template Engine 代码模板引擎 | Code Template Engine 代码模板引擎 | design | design_only |
| D-INFRA-RUNTIME/Cold Start Optimizer 冷启动优化器 | Cold Start Optimizer 冷启动优化器 | design | design_only | D-INFRA-RUNTIME/Cold Start Optimizer 冷启动优化器 | Cold Start Optimizer 冷启动优化器 | design | design_only |
| D-INFRA-RUNTIME/Cold Storage 冷存储 | Cold Storage 冷存储 | design | design_only | D-INFRA-RUNTIME/Cold Storage 冷存储 | Cold Storage 冷存储 | design | design_only |
| D-INFRA-RUNTIME/Cold平面 冷平面 | Cold平面 冷平面 | design | design_only | D-INFRA-RUNTIME/Cold平面 冷平面 | Cold平面 冷平面 | design | design_only |
| D-INFRA-RUNTIME/Communication Protocol Adapter 通信协议适配器 | Communication Protocol Adapter 通信协议适配器 | design | design_only | D-INFRA-RUNTIME/Communication Protocol Adapter 通信协议适配器 | Communication Protocol Adapter 通信协议适配器 | design | design_only |
| D-INFRA-RUNTIME/ConfigManager 配置管理器 | ConfigManager 配置管理器 | design | design_only | D-INFRA-RUNTIME/ConfigManager 配置管理器 | ConfigManager 配置管理器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Change Notifier 配置变更通知器 | Configuration Change Notifier 配置变更通知器 | design | design_only | D-INFRA-RUNTIME/Configuration Change Notifier 配置变更通知器 | Configuration Change Notifier 配置变更通知器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Code Generator 配置代码生成器 | Configuration Code Generator 配置代码生成器 | design | design_only | D-INFRA-RUNTIME/Configuration Code Generator 配置代码生成器 | Configuration Code Generator 配置代码生成器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Dependency Mapper 配置依赖映射器 | Configuration Dependency Mapper 配置依赖映射器 | design | design_only | D-INFRA-RUNTIME/Configuration Dependency Mapper 配置依赖映射器 | Configuration Dependency Mapper 配置依赖映射器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Diff Detector 配置差异检测器 | Configuration Diff Detector 配置差异检测器 | design | design_only | D-INFRA-RUNTIME/Configuration Diff Detector 配置差异检测器 | Configuration Diff Detector 配置差异检测器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Encryption Manager 配置加密管理器 | Configuration Encryption Manager 配置加密管理器 | design | design_only | D-INFRA-RUNTIME/Configuration Encryption Manager 配置加密管理器 | Configuration Encryption Manager 配置加密管理器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Hot Update Engine 配置热更新引擎 | Configuration Hot Update Engine 配置热更新引擎 | design | design_only | D-INFRA-RUNTIME/Configuration Hot Update Engine 配置热更新引擎 | Configuration Hot Update Engine 配置热更新引擎 | design | design_only |
| D-INFRA-RUNTIME/Configuration Manager 配置管理器 | Configuration Manager 配置管理器 | design | design_only | D-INFRA-RUNTIME/Configuration Manager 配置管理器 | Configuration Manager 配置管理器 | design | design_only |
| D-INFRA-RUNTIME/Configuration Merge Engine 配置合并引擎 | Configuration Merge Engine 配置合并引擎 | design | design_only | D-INFRA-RUNTIME/Configuration Merge Engine 配置合并引擎 | Configuration Merge Engine 配置合并引擎 | design | design_only |
| D-INFRA-RUNTIME/Configuration Validation Engine 配置校验引擎 | Configuration Validation Engine 配置校验引擎 | design | design_only | D-INFRA-RUNTIME/Configuration Validation Engine 配置校验引擎 | Configuration Validation Engine 配置校验引擎 | design | design_only |
| ...FRA-RUNTIME/Configuration Version Management & Rollback Framework 配置版本管理与回滚框架 | Configuration Version Management & Ro... | design | design_only | ...FRA-RUNTIME/Configuration Version Management & Rollback Framework 配置版本管理与回滚框架 | Configuration Version Management & Ro... | design | design_only |
| D-INFRA-RUNTIME/Conformal Prediction 共形预测 | Conformal Prediction 共形预测 | design | design_only | D-INFRA-RUNTIME/Conformal Prediction 共形预测 | Conformal Prediction 共形预测 | design | design_only |
| D-INFRA-RUNTIME/Connection Pool Manager 连接池管理器 | Connection Pool Manager 连接池管理器 | design | design_only | D-INFRA-RUNTIME/Connection Pool Manager 连接池管理器 | Connection Pool Manager 连接池管理器 | design | design_only |
| D-INFRA-RUNTIME/Container Image Cache Manager 容器镜像缓存管理器 | Container Image Cache Manager 容器镜像缓存管理器 | design | design_only | D-INFRA-RUNTIME/Container Image Cache Manager 容器镜像缓存管理器 | Container Image Cache Manager 容器镜像缓存管理器 | design | design_only |
| D-INFRA-RUNTIME/Container Orchestrator 容器编排器 | Container Orchestrator 容器编排器 | design | design_only | D-INFRA-RUNTIME/Container Orchestrator 容器编排器 | Container Orchestrator 容器编排器 | design | design_only |
| D-INFRA-RUNTIME/Container Resource Isolator 容器资源隔离器 | Container Resource Isolator 容器资源隔离器 | design | design_only | D-INFRA-RUNTIME/Container Resource Isolator 容器资源隔离器 | Container Resource Isolator 容器资源隔离器 | design | design_only |
| D-INFRA-RUNTIME/Continuous Improvement Engine 持续改进引擎 | Continuous Improvement Engine 持续改进引擎 | design | design_only | D-INFRA-RUNTIME/Continuous Improvement Engine 持续改进引擎 | Continuous Improvement Engine 持续改进引擎 | design | design_only |
| D-INFRA-RUNTIME/Conversation Context Compressor 对话上下文压缩 | Conversation Context Compressor 对话上下文压缩 | design | design_only | D-INFRA-RUNTIME/Conversation Context Compressor 对话上下文压缩 | Conversation Context Compressor 对话上下文压缩 | design | design_only |
| D-INFRA-RUNTIME/Cross-Module Interface Registry 跨模块接口注册中心 | Cross-Module Interface Registry 跨模块接口... | design | design_only | D-INFRA-RUNTIME/Cross-Module Interface Registry 跨模块接口注册中心 | Cross-Module Interface Registry 跨模块接口... | design | design_only |
| D-INFRA-RUNTIME/Cross-Origin Resource Sharing Manager 跨域资源共享管理器 | Cross-Origin Resource Sharing Manager... | design | design_only | D-INFRA-RUNTIME/Cross-Origin Resource Sharing Manager 跨域资源共享管理器 | Cross-Origin Resource Sharing Manager... | design | design_only |
| D-INFRA-RUNTIME/Cross-Phase State Propagator 跨阶段状态传递器 | Cross-Phase State Propagator 跨阶段状态传递器 | design | design_only | D-INFRA-RUNTIME/Cross-Phase State Propagator 跨阶段状态传递器 | Cross-Phase State Propagator 跨阶段状态传递器 | design | design_only |
| D-INFRA-RUNTIME/Cybersecurity Shield 网络安全防护组件 | Cybersecurity Shield 网络安全防护组件 | design | design_only | D-INFRA-RUNTIME/Cybersecurity Shield 网络安全防护组件 | Cybersecurity Shield 网络安全防护组件 | design | design_only |
| D-INFRA-RUNTIME/D-INFRA | D-INFRA | design | design_only | D-INFRA-RUNTIME/D-INFRA | D-INFRA | design | design_only |
| D-INFRA-RUNTIME/D-INFRA-RUNTIME | D-INFRA-RUNTIME | design | design_only | D-INFRA-RUNTIME/D-INFRA-RUNTIME | D-INFRA-RUNTIME | design | design_only |
| D-INFRA-RUNTIME/DAO Layer Code Generator DAO层代码生成器 | DAO Layer Code Generator DAO层代码生成器 | design | design_only | D-INFRA-RUNTIME/DAO Layer Code Generator DAO层代码生成器 | DAO Layer Code Generator DAO层代码生成器 | design | design_only |
| D-INFRA-RUNTIME/Data Aggregation View Manager 数据聚合视图管理器 | Data Aggregation View Manager 数据聚合视图管理器 | design | design_only | D-INFRA-RUNTIME/Data Aggregation View Manager 数据聚合视图管理器 | Data Aggregation View Manager 数据聚合视图管理器 | design | design_only |
| D-INFRA-RUNTIME/Data Buffer Pool Manager 数据缓冲池管理器 | Data Buffer Pool Manager 数据缓冲池管理器 | design | design_only | D-INFRA-RUNTIME/Data Buffer Pool Manager 数据缓冲池管理器 | Data Buffer Pool Manager 数据缓冲池管理器 | design | design_only |
| D-INFRA-RUNTIME/Data Compression Manager 数据压缩管理器 | Data Compression Manager 数据压缩管理器 | design | design_only | D-INFRA-RUNTIME/Data Compression Manager 数据压缩管理器 | Data Compression Manager 数据压缩管理器 | design | design_only |
| D-INFRA-RUNTIME/Data Format Version Coordinator 数据格式版本协调器 | Data Format Version Coordinator 数据格式版... | design | design_only | D-INFRA-RUNTIME/Data Format Version Coordinator 数据格式版本协调器 | Data Format Version Coordinator 数据格式版... | design | design_only |
| D-INFRA-RUNTIME/Data Migration Script Generator 数据迁移脚本生成器 | Data Migration Script Generator 数据迁移脚... | design | design_only | D-INFRA-RUNTIME/Data Migration Script Generator 数据迁移脚本生成器 | Data Migration Script Generator 数据迁移脚... | design | design_only |
| D-INFRA-RUNTIME/Data Model Generator 数据模型生成器 | Data Model Generator 数据模型生成器 | design | design_only | D-INFRA-RUNTIME/Data Model Generator 数据模型生成器 | Data Model Generator 数据模型生成器 | design | design_only |
| D-INFRA-RUNTIME/Data Source Star Rating Dynamic Updater 数据源星级评分动态更新器 | Data Source Star Rating Dynamic Updat... | design | design_only | D-INFRA-RUNTIME/Data Source Star Rating Dynamic Updater 数据源星级评分动态更新器 | Data Source Star Rating Dynamic Updat... | design | design_only |
| D-INFRA-RUNTIME/Data Sovereignty Manager 数据主权管理器 | Data Sovereignty Manager 数据主权管理器 | design | design_only | D-INFRA-RUNTIME/Data Sovereignty Manager 数据主权管理器 | Data Sovereignty Manager 数据主权管理器 | design | design_only |
| D-INFRA-RUNTIME/Data Transfer Validator 数据传输校验器 | Data Transfer Validator 数据传输校验器 | design | design_only | D-INFRA-RUNTIME/Data Transfer Validator 数据传输校验器 | Data Transfer Validator 数据传输校验器 | design | design_only |
| D-INFRA-RUNTIME/Data Transformation Performance Optimizer 数据转换性能优化器 | Data Transformation Performance Optim... | design | design_only | D-INFRA-RUNTIME/Data Transformation Performance Optimizer 数据转换性能优化器 | Data Transformation Performance Optim... | design | design_only |
| D-INFRA-RUNTIME/Data Transformation Pipeline Orchestrator 数据转换管线编排器 | Data Transformation Pipeline Orchestr... | design | design_only | D-INFRA-RUNTIME/Data Transformation Pipeline Orchestrator 数据转换管线编排器 | Data Transformation Pipeline Orchestr... | design | design_only |
| D-INFRA-RUNTIME/Database Layer 数据库层 | Database Layer 数据库层 | design | design_only | D-INFRA-RUNTIME/Database Layer 数据库层 | Database Layer 数据库层 | design | design_only |
| D-INFRA-RUNTIME/Database Schema Synchronizer 数据库Schema同步器 | Database Schema Synchronizer 数据库Schem... | design | design_only | D-INFRA-RUNTIME/Database Schema Synchronizer 数据库Schema同步器 | Database Schema Synchronizer 数据库Schem... | design | design_only |
| D-INFRA-RUNTIME/DegradationTriggered 降级触发事件 | DegradationTriggered 降级触发事件 | design | design_only | D-INFRA-RUNTIME/DegradationTriggered 降级触发事件 | DegradationTriggered 降级触发事件 | design | design_only |
| D-INFRA-RUNTIME/Deliverable Version Tracker 交付物版本追踪器 | Deliverable Version Tracker 交付物版本追踪器 | design | design_only | D-INFRA-RUNTIME/Deliverable Version Tracker 交付物版本追踪器 | Deliverable Version Tracker 交付物版本追踪器 | design | design_only |
| D-INFRA-RUNTIME/Dependency Conflict Resolver 依赖冲突解决器 | Dependency Conflict Resolver 依赖冲突解决器 | design | design_only | D-INFRA-RUNTIME/Dependency Conflict Resolver 依赖冲突解决器 | Dependency Conflict Resolver 依赖冲突解决器 | design | design_only |
| D-INFRA-RUNTIME/Dependency Graph Visualization Renderer 依赖图可视化渲染器 | Dependency Graph Visualization Render... | design | design_only | D-INFRA-RUNTIME/Dependency Graph Visualization Renderer 依赖图可视化渲染器 | Dependency Graph Visualization Render... | design | design_only |
| D-INFRA-RUNTIME/Dependency Security Vulnerability Scanner 依赖安全漏洞扫描器 | Dependency Security Vulnerability Sca... | design | design_only | D-INFRA-RUNTIME/Dependency Security Vulnerability Scanner 依赖安全漏洞扫描器 | Dependency Security Vulnerability Sca... | design | design_only |
| D-INFRA-RUNTIME/Dependency Upgrade Compatibility Checker 依赖升级兼容性检查器 | Dependency Upgrade Compatibility Chec... | design | design_only | D-INFRA-RUNTIME/Dependency Upgrade Compatibility Checker 依赖升级兼容性检查器 | Dependency Upgrade Compatibility Chec... | design | design_only |
| D-INFRA-RUNTIME/Dependency Version Lock Manager 依赖版本锁定管理器 | Dependency Version Lock Manager 依赖版本锁... | design | design_only | D-INFRA-RUNTIME/Dependency Version Lock Manager 依赖版本锁定管理器 | Dependency Version Lock Manager 依赖版本锁... | design | design_only |
| D-INFRA-RUNTIME/Dependency Visualizer 依赖可视化器 | Dependency Visualizer 依赖可视化器 | design | design_only | D-INFRA-RUNTIME/Dependency Visualizer 依赖可视化器 | Dependency Visualizer 依赖可视化器 | design | design_only |
| D-INFRA-RUNTIME/Deployment Topology Manager 部署拓扑管理器 | Deployment Topology Manager 部署拓扑管理器 | design | design_only | D-INFRA-RUNTIME/Deployment Topology Manager 部署拓扑管理器 | Deployment Topology Manager 部署拓扑管理器 | design | design_only |
| D-INFRA-RUNTIME/Development Plan Visualizer 开发计划可视化器 | Development Plan Visualizer 开发计划可视化器 | design | design_only | D-INFRA-RUNTIME/Development Plan Visualizer 开发计划可视化器 | Development Plan Visualizer 开发计划可视化器 | design | design_only |
| D-INFRA-RUNTIME/Distributed Lock Manager 分布式锁管理器 | Distributed Lock Manager 分布式锁管理器 | design | design_only | D-INFRA-RUNTIME/Distributed Lock Manager 分布式锁管理器 | Distributed Lock Manager 分布式锁管理器 | design | design_only |
| D-INFRA-RUNTIME/Document Link Validator 文档链接验证器 | Document Link Validator 文档链接验证器 | design | design_only | D-INFRA-RUNTIME/Document Link Validator 文档链接验证器 | Document Link Validator 文档链接验证器 | design | design_only |
| D-INFRA-RUNTIME/Document Search Indexer 文档搜索索引器 | Document Search Indexer 文档搜索索引器 | design | design_only | D-INFRA-RUNTIME/Document Search Indexer 文档搜索索引器 | Document Search Indexer 文档搜索索引器 | design | design_only |
| D-INFRA-RUNTIME/Document Template Engine 文档模板引擎 | Document Template Engine 文档模板引擎 | design | design_only | D-INFRA-RUNTIME/Document Template Engine 文档模板引擎 | Document Template Engine 文档模板引擎 | design | design_only |
| D-INFRA-RUNTIME/Document Version Manager 文档版本管理器 | Document Version Manager 文档版本管理器 | design | design_only | D-INFRA-RUNTIME/Document Version Manager 文档版本管理器 | Document Version Manager 文档版本管理器 | design | design_only |
| D-INFRA-RUNTIME/Domain-Driven Design Validator 领域驱动设计校验器 | Domain-Driven Design Validator 领域驱动设计校验器 | design | design_only | D-INFRA-RUNTIME/Domain-Driven Design Validator 领域驱动设计校验器 | Domain-Driven Design Validator 领域驱动设计校验器 | design | design_only |
| D-INFRA-RUNTIME/DuckDB Database DuckDB数据库 | DuckDB Database DuckDB数据库 | design | design_only | D-INFRA-RUNTIME/DuckDB Database DuckDB数据库 | DuckDB Database DuckDB数据库 | design | design_only |
| D-INFRA-RUNTIME/Elastic Scaling Manager 弹性伸缩管理器 | Elastic Scaling Manager 弹性伸缩管理器 | design | design_only | D-INFRA-RUNTIME/Elastic Scaling Manager 弹性伸缩管理器 | Elastic Scaling Manager 弹性伸缩管理器 | design | design_only |
| D-INFRA-RUNTIME/Endpoint Response Format Validator 端点响应格式校验器 | Endpoint Response Format Validator 端点... | design | design_only | D-INFRA-RUNTIME/Endpoint Response Format Validator 端点响应格式校验器 | Endpoint Response Format Validator 端点... | design | design_only |
| D-INFRA-RUNTIME/Environment Configuration Layering Manager 环境配置分层管理器 | Environment Configuration Layering Ma... | design | design_only | D-INFRA-RUNTIME/Environment Configuration Layering Manager 环境配置分层管理器 | Environment Configuration Layering Ma... | design | design_only |
| D-INFRA-RUNTIME/Environment Manager 环境管理 | Environment Manager 环境管理 | design | design_only | D-INFRA-RUNTIME/Environment Manager 环境管理 | Environment Manager 环境管理 | design | design_only |
| D-INFRA-RUNTIME/Environment Variable Manager 环境变量管理器 | Environment Variable Manager 环境变量管理器 | design | design_only | D-INFRA-RUNTIME/Environment Variable Manager 环境变量管理器 | Environment Variable Manager 环境变量管理器 | design | design_only |
| D-INFRA-RUNTIME/Error Handling Code Generator 错误处理代码生成器 | Error Handling Code Generator 错误处理代码生成器 | design | design_only | D-INFRA-RUNTIME/Error Handling Code Generator 错误处理代码生成器 | Error Handling Code Generator 错误处理代码生成器 | design | design_only |
| D-INFRA-RUNTIME/EventBus 事件总线 | EventBus 事件总线 | design | design_only | D-INFRA-RUNTIME/EventBus 事件总线 | EventBus 事件总线 | design | design_only |
| D-INFRA-RUNTIME/EventStoreDB Event Store EventStoreDB事件存储 | EventStoreDB Event Store EventStoreDB... | design | design_only | D-INFRA-RUNTIME/EventStoreDB Event Store EventStoreDB事件存储 | EventStoreDB Event Store EventStoreDB... | design | design_only |
| D-INFRA-RUNTIME/Experiment and Resilience Testing 实验与韧性测试 | Experiment and Resilience Testing 实验与... | design | design_only | D-INFRA-RUNTIME/Experiment and Resilience Testing 实验与韧性测试 | Experiment and Resilience Testing 实验与... | design | design_only |
| D-INFRA-RUNTIME/FAISS Vector Search FAISS向量检索 | FAISS Vector Search FAISS向量检索 | design | design_only | D-INFRA-RUNTIME/FAISS Vector Search FAISS向量检索 | FAISS Vector Search FAISS向量检索 | design | design_only |
| D-INFRA-RUNTIME/Factor Warmup Manager 因子预热管理器 | Factor Warmup Manager 因子预热管理器 | design | design_only | D-INFRA-RUNTIME/Factor Warmup Manager 因子预热管理器 | Factor Warmup Manager 因子预热管理器 | design | design_only |
| D-INFRA-RUNTIME/Failover Coordinator 故障转移协调器 | Failover Coordinator 故障转移协调器 | design | design_only | D-INFRA-RUNTIME/Failover Coordinator 故障转移协调器 | Failover Coordinator 故障转移协调器 | design | design_only |
| D-INFRA-RUNTIME/Faiss GPU Vector Search Faiss GPU向量搜索 | Faiss GPU Vector Search Faiss GPU向量搜索 | design | design_only | D-INFRA-RUNTIME/Faiss GPU Vector Search Faiss GPU向量搜索 | Faiss GPU Vector Search Faiss GPU向量搜索 | design | design_only |
| D-INFRA-RUNTIME/Feature Drift & Concept Drift Detection 特征漂移与概念漂移检测 | Feature Drift & Concept Drift Detecti... | design | design_only | D-INFRA-RUNTIME/Feature Drift & Concept Drift Detection 特征漂移与概念漂移检测 | Feature Drift & Concept Drift Detecti... | design | design_only |
| D-INFRA-RUNTIME/Feature Lifecycle Manager 功能生命周期管理器 | Feature Lifecycle Manager 功能生命周期管理器 | design | design_only | D-INFRA-RUNTIME/Feature Lifecycle Manager 功能生命周期管理器 | Feature Lifecycle Manager 功能生命周期管理器 | design | design_only |
| D-INFRA-RUNTIME/Field Mapping Converter 字段映射转换器 | Field Mapping Converter 字段映射转换器 | design | design_only | D-INFRA-RUNTIME/Field Mapping Converter 字段映射转换器 | Field Mapping Converter 字段映射转换器 | design | design_only |
| D-INFRA-RUNTIME/Financial Time Series Data Augmentation 金融时序数据增强 | Financial Time Series Data Augmentati... | design | design_only | D-INFRA-RUNTIME/Financial Time Series Data Augmentation 金融时序数据增强 | Financial Time Series Data Augmentati... | design | design_only |
| D-INFRA-RUNTIME/GPU Compute Pipeline Manager GPU计算管线管理器 | GPU Compute Pipeline Manager GPU计算管线管理器 | design | design_only | D-INFRA-RUNTIME/GPU Compute Pipeline Manager GPU计算管线管理器 | GPU Compute Pipeline Manager GPU计算管线管理器 | design | design_only |
| D-INFRA-RUNTIME/GPU Inference Training Dynamic Allocator GPU推理训练动态分配器 | GPU Inference Training Dynamic Alloca... | design | design_only | D-INFRA-RUNTIME/GPU Inference Training Dynamic Allocator GPU推理训练动态分配器 | GPU Inference Training Dynamic Alloca... | design | design_only |
| D-INFRA-RUNTIME/GPU Kernel Launch Optimizer GPU内核启动优化器 | GPU Kernel Launch Optimizer GPU内核启动优化器 | design | design_only | D-INFRA-RUNTIME/GPU Kernel Launch Optimizer GPU内核启动优化器 | GPU Kernel Launch Optimizer GPU内核启动优化器 | design | design_only |
| D-INFRA-RUNTIME/GPU MPS多进程并发 GPU Multi-Process Service | GPU MPS多进程并发 GPU Multi-Process Service | design | design_only | D-INFRA-RUNTIME/GPU MPS多进程并发 GPU Multi-Process Service | GPU MPS多进程并发 GPU Multi-Process Service | design | design_only |
| D-INFRA-RUNTIME/GPU Memory Transfer Optimizer GPU内存传输优化器 | GPU Memory Transfer Optimizer GPU内存传输优化器 | design | design_only | D-INFRA-RUNTIME/GPU Memory Transfer Optimizer GPU内存传输优化器 | GPU Memory Transfer Optimizer GPU内存传输优化器 | design | design_only |
| D-INFRA-RUNTIME/GPU Programming Abstraction Layer GPU编程抽象层 | GPU Programming Abstraction Layer GPU... | design | design_only | D-INFRA-RUNTIME/GPU Programming Abstraction Layer GPU编程抽象层 | GPU Programming Abstraction Layer GPU... | design | design_only |
| D-INFRA-RUNTIME/GPU Resource Monitor GPU资源监控器 | GPU Resource Monitor GPU资源监控器 | design | design_only | D-INFRA-RUNTIME/GPU Resource Monitor GPU资源监控器 | GPU Resource Monitor GPU资源监控器 | design | design_only |
| D-INFRA-RUNTIME/GPU Scheduler GPU调度器 | GPU Scheduler GPU调度器 | design | design_only | D-INFRA-RUNTIME/GPU Scheduler GPU调度器 | GPU Scheduler GPU调度器 | design | design_only |
| D-INFRA-RUNTIME/GPUOOMDetected GPU OOM检测事件 | GPUOOMDetected GPU OOM检测事件 | design | design_only | D-INFRA-RUNTIME/GPUOOMDetected GPU OOM检测事件 | GPUOOMDetected GPU OOM检测事件 | design | design_only |
| D-INFRA-RUNTIME/GPU调度上岗+热交换 GPU调度 | GPU调度上岗+热交换 GPU调度 | design | design_only | D-INFRA-RUNTIME/GPU调度上岗+热交换 GPU调度 | GPU调度上岗+热交换 GPU调度 | design | design_only |
| D-INFRA-RUNTIME/GPU调度层 GPU调度 | GPU调度层 GPU调度 | design | design_only | D-INFRA-RUNTIME/GPU调度层 GPU调度 | GPU调度层 GPU调度 | design | design_only |
| D-INFRA-RUNTIME/Global Dependency Graph Calculator 全局依赖图计算器 | Global Dependency Graph Calculator 全局... | design | design_only | D-INFRA-RUNTIME/Global Dependency Graph Calculator 全局依赖图计算器 | Global Dependency Graph Calculator 全局... | design | design_only |
| D-INFRA-RUNTIME/Governance Adapter 治理适配器 | Governance Adapter 治理适配器 | design | design_only | D-INFRA-RUNTIME/Governance Adapter 治理适配器 | Governance Adapter 治理适配器 | design | design_only |
| D-INFRA-RUNTIME/Governance Protocol 治理协议 | Governance Protocol 治理协议 | design | design_only | D-INFRA-RUNTIME/Governance Protocol 治理协议 | Governance Protocol 治理协议 | design | design_only |
| D-INFRA-RUNTIME/Graceful Shutdown Coordinator 优雅关闭协调器 | Graceful Shutdown Coordinator 优雅关闭协调器 | design | design_only | D-INFRA-RUNTIME/Graceful Shutdown Coordinator 优雅关闭协调器 | Graceful Shutdown Coordinator 优雅关闭协调器 | design | design_only |
| D-INFRA-RUNTIME/Graph Neural Network for Stock Relations 图神经网络用于股票关系建模 | Graph Neural Network for Stock Relati... | design | design_only | D-INFRA-RUNTIME/Graph Neural Network for Stock Relations 图神经网络用于股票关系建模 | Graph Neural Network for Stock Relati... | design | design_only |
| D-INFRA-RUNTIME/Hardware Accelerator 硬件加速器 | Hardware Accelerator 硬件加速器 | design | design_only | D-INFRA-RUNTIME/Hardware Accelerator 硬件加速器 | Hardware Accelerator 硬件加速器 | design | design_only |
| D-INFRA-RUNTIME/High Performance HA Framework 高性能高可用保障框架 | High Performance HA Framework 高性能高可用保障框架 | design | design_only | D-INFRA-RUNTIME/High Performance HA Framework 高性能高可用保障框架 | High Performance HA Framework 高性能高可用保障框架 | design | design_only |
| D-INFRA-RUNTIME/Hot Storage 热存储 | Hot Storage 热存储 | design | design_only | D-INFRA-RUNTIME/Hot Storage 热存储 | Hot Storage 热存储 | design | design_only |
| D-INFRA-RUNTIME/Hot↔Warm必须通过IPC协议通信 Hot-Warm IPC Protocol | Hot↔Warm必须通过IPC协议通信 Hot-Warm IPC Prot... | design | design_only | D-INFRA-RUNTIME/Hot↔Warm必须通过IPC协议通信 Hot-Warm IPC Protocol | Hot↔Warm必须通过IPC协议通信 Hot-Warm IPC Prot... | design | design_only |
| D-INFRA-RUNTIME/Hot平面 热平面 | Hot平面 热平面 | design | design_only | D-INFRA-RUNTIME/Hot平面 热平面 | Hot平面 热平面 | design | design_only |
| D-INFRA-RUNTIME/Inference Engine Warmer 推理引擎预热器 | Inference Engine Warmer 推理引擎预热器 | design | design_only | D-INFRA-RUNTIME/Inference Engine Warmer 推理引擎预热器 | Inference Engine Warmer 推理引擎预热器 | design | design_only |
| D-INFRA-RUNTIME/Infrastructure Status 基础设施状态 | Infrastructure Status 基础设施状态 | design | design_only | D-INFRA-RUNTIME/Infrastructure Status 基础设施状态 | Infrastructure Status 基础设施状态 | design | design_only |
| D-INFRA-RUNTIME/Infrastructure Topology Visualizer 基础设施拓扑可视化器 | Infrastructure Topology Visualizer 基础... | design | design_only | D-INFRA-RUNTIME/Infrastructure Topology Visualizer 基础设施拓扑可视化器 | Infrastructure Topology Visualizer 基础... | design | design_only |
| D-INFRA-RUNTIME/InfrastructureAlert 基础设施告警 | InfrastructureAlert 基础设施告警 | design | design_only | D-INFRA-RUNTIME/InfrastructureAlert 基础设施告警 | InfrastructureAlert 基础设施告警 | design | design_only |
| D-INFRA-RUNTIME/InfrastructureNode 基础设施节点 | InfrastructureNode 基础设施节点 | design | design_only | D-INFRA-RUNTIME/InfrastructureNode 基础设施节点 | InfrastructureNode 基础设施节点 | design | design_only |
| D-INFRA-RUNTIME/Inter-Layer Data Format Converter & Validator 层间数据格式转换与校验器 | Inter-Layer Data Format Converter & V... | design | design_only | D-INFRA-RUNTIME/Inter-Layer Data Format Converter & Validator 层间数据格式转换与校验器 | Inter-Layer Data Format Converter & V... | design | design_only |
| D-INFRA-RUNTIME/Inter-Module Communication Protocol Manager 模块间通信协议管理器 | Inter-Module Communication Protocol M... | design | design_only | D-INFRA-RUNTIME/Inter-Module Communication Protocol Manager 模块间通信协议管理器 | Inter-Module Communication Protocol M... | design | design_only |
| D-INFRA-RUNTIME/Inter-Process Communication Manager 进程间通信管理器 | Inter-Process Communication Manager 进... | design | design_only | D-INFRA-RUNTIME/Inter-Process Communication Manager 进程间通信管理器 | Inter-Process Communication Manager 进... | design | design_only |
| D-INFRA-RUNTIME/Interface Mock Generator 接口Mock生成器 | Interface Mock Generator 接口Mock生成器 | design | design_only | D-INFRA-RUNTIME/Interface Mock Generator 接口Mock生成器 | Interface Mock Generator 接口Mock生成器 | design | design_only |
| D-INFRA-RUNTIME/Iteration Cycle Tracker 迭代周期追踪器 | Iteration Cycle Tracker 迭代周期追踪器 | design | design_only | D-INFRA-RUNTIME/Iteration Cycle Tracker 迭代周期追踪器 | Iteration Cycle Tracker 迭代周期追踪器 | design | design_only |
| D-INFRA-RUNTIME/Kafka Message Queue Kafka消息队列 | Kafka Message Queue Kafka消息队列 | design | design_only | D-INFRA-RUNTIME/Kafka Message Queue Kafka消息队列 | Kafka Message Queue Kafka消息队列 | design | design_only |
| D-INFRA-RUNTIME/Knowledge Base Data Sovereignty 知识库数据主权管理 | Knowledge Base Data Sovereignty 知识库数据... | design | design_only | D-INFRA-RUNTIME/Knowledge Base Data Sovereignty 知识库数据主权管理 | Knowledge Base Data Sovereignty 知识库数据... | design | design_only |
| D-INFRA-RUNTIME/Knowledge Base Indexer 知识库索引器 | Knowledge Base Indexer 知识库索引器 | design | design_only | D-INFRA-RUNTIME/Knowledge Base Indexer 知识库索引器 | Knowledge Base Indexer 知识库索引器 | design | design_only |
| D-INFRA-RUNTIME/LLM Agent for Fundamental Analysis 大语言模型Agent用于基本面分析 | LLM Agent for Fundamental Analysis 大语... | design | design_only | D-INFRA-RUNTIME/LLM Agent for Fundamental Analysis 大语言模型Agent用于基本面分析 | LLM Agent for Fundamental Analysis 大语... | design | design_only |
| D-INFRA-RUNTIME/Learning System Bridge Declaration 学习系统桥接声明 | Learning System Bridge Declaration 学习... | design | design_only | D-INFRA-RUNTIME/Learning System Bridge Declaration 学习系统桥接声明 | Learning System Bridge Declaration 学习... | design | design_only |
| D-INFRA-RUNTIME/Live Data to Research Domain Feedback Channel 实盘数据→研究域反馈通道 | Live Data to Research Domain Feedback... | design | design_only | D-INFRA-RUNTIME/Live Data to Research Domain Feedback Channel 实盘数据→研究域反馈通道 | Live Data to Research Domain Feedback... | design | design_only |
| D-INFRA-RUNTIME/Load Balancing Strategy Engine 负载均衡策略引擎 | Load Balancing Strategy Engine 负载均衡策略引擎 | design | design_only | D-INFRA-RUNTIME/Load Balancing Strategy Engine 负载均衡策略引擎 | Load Balancing Strategy Engine 负载均衡策略引擎 | design | design_only |
| D-INFRA-RUNTIME/Local First Architecture 本地优先架构 | Local First Architecture 本地优先架构 | design | design_only | D-INFRA-RUNTIME/Local First Architecture 本地优先架构 | Local First Architecture 本地优先架构 | design | design_only |
| D-INFRA-RUNTIME/MCP Sentinel System Monitor MCP哨兵系统监控器 | MCP Sentinel System Monitor MCP哨兵系统监控器 | design | design_only | D-INFRA-RUNTIME/MCP Sentinel System Monitor MCP哨兵系统监控器 | MCP Sentinel System Monitor MCP哨兵系统监控器 | design | design_only |
| D-INFRA-RUNTIME/Mamba/SSM State Space Model Mamba/SSM状态空间模型 | Mamba/SSM State Space Model Mamba/SSM... | design | design_only | D-INFRA-RUNTIME/Mamba/SSM State Space Model Mamba/SSM状态空间模型 | Mamba/SSM State Space Model Mamba/SSM... | design | design_only |
| D-INFRA-RUNTIME/Market Microstructure Deep Modeling 市场微观结构深度建模 | Market Microstructure Deep Modeling 市... | design | design_only | D-INFRA-RUNTIME/Market Microstructure Deep Modeling 市场微观结构深度建模 | Market Microstructure Deep Modeling 市... | design | design_only |
| D-INFRA-RUNTIME/Message Queue Manager 消息队列管理器 | Message Queue Manager 消息队列管理器 | design | design_only | D-INFRA-RUNTIME/Message Queue Manager 消息队列管理器 | Message Queue Manager 消息队列管理器 | design | design_only |
| D-INFRA-RUNTIME/Message Queue 消息队列 | Message Queue 消息队列 | design | design_only | D-INFRA-RUNTIME/Message Queue 消息队列 | Message Queue 消息队列 | design | design_only |
| D-INFRA-RUNTIME/Metric Anomaly Detector 指标异常检测器 | Metric Anomaly Detector 指标异常检测器 | design | design_only | D-INFRA-RUNTIME/Metric Anomaly Detector 指标异常检测器 | Metric Anomaly Detector 指标异常检测器 | design | design_only |
| D-INFRA-RUNTIME/Milestone Dependency Validator 里程碑依赖校验器 | Milestone Dependency Validator 里程碑依赖校验器 | design | design_only | D-INFRA-RUNTIME/Milestone Dependency Validator 里程碑依赖校验器 | Milestone Dependency Validator 里程碑依赖校验器 | design | design_only |
| D-INFRA-RUNTIME/MinIO Object Storage MinIO对象存储 | MinIO Object Storage MinIO对象存储 | design | design_only | D-INFRA-RUNTIME/MinIO Object Storage MinIO对象存储 | MinIO Object Storage MinIO对象存储 | design | design_only |
| D-INFRA-RUNTIME/Model Registry & Experiment Management 模型注册与实验管理 | Model Registry & Experiment Managemen... | design | design_only | D-INFRA-RUNTIME/Model Registry & Experiment Management 模型注册与实验管理 | Model Registry & Experiment Managemen... | design | design_only |
| D-INFRA-RUNTIME/Model Warmup Manager 模型预热管理器 | Model Warmup Manager 模型预热管理器 | design | design_only | D-INFRA-RUNTIME/Model Warmup Manager 模型预热管理器 | Model Warmup Manager 模型预热管理器 | design | design_only |
| D-INFRA-RUNTIME/Module Configuration Aggregator 模块配置聚合器 | Module Configuration Aggregator 模块配置聚合器 | design | design_only | D-INFRA-RUNTIME/Module Configuration Aggregator 模块配置聚合器 | Module Configuration Aggregator 模块配置聚合器 | design | design_only |
| D-INFRA-RUNTIME/Module Dependency Injector 模块依赖注入器 | Module Dependency Injector 模块依赖注入器 | design | design_only | D-INFRA-RUNTIME/Module Dependency Injector 模块依赖注入器 | Module Dependency Injector 模块依赖注入器 | design | design_only |
| D-INFRA-RUNTIME/Module Documentation Indexer 模块文档索引器 | Module Documentation Indexer 模块文档索引器 | design | design_only | D-INFRA-RUNTIME/Module Documentation Indexer 模块文档索引器 | Module Documentation Indexer 模块文档索引器 | design | design_only |
| D-INFRA-RUNTIME/Module Exception Boundary Manager 模块异常边界管理器 | Module Exception Boundary Manager 模块异... | design | design_only | D-INFRA-RUNTIME/Module Exception Boundary Manager 模块异常边界管理器 | Module Exception Boundary Manager 模块异... | design | design_only |
| D-INFRA-RUNTIME/Module Feature Toggle Manager 模块功能开关管理器 | Module Feature Toggle Manager 模块功能开关管理器 | design | design_only | D-INFRA-RUNTIME/Module Feature Toggle Manager 模块功能开关管理器 | Module Feature Toggle Manager 模块功能开关管理器 | design | design_only |
| D-INFRA-RUNTIME/Module Health Checker 模块健康检查器 | Module Health Checker 模块健康检查器 | design | design_only | D-INFRA-RUNTIME/Module Health Checker 模块健康检查器 | Module Health Checker 模块健康检查器 | design | design_only |
| D-INFRA-RUNTIME/Module Hot Update Manager 模块热更新管理器 | Module Hot Update Manager 模块热更新管理器 | design | design_only | D-INFRA-RUNTIME/Module Hot Update Manager 模块热更新管理器 | Module Hot Update Manager 模块热更新管理器 | design | design_only |
| D-INFRA-RUNTIME/Module Interface Contract Manager 模块接口契约管理器 | Module Interface Contract Manager 模块接... | design | design_only | D-INFRA-RUNTIME/Module Interface Contract Manager 模块接口契约管理器 | Module Interface Contract Manager 模块接... | design | design_only |
| D-INFRA-RUNTIME/Module Lifecycle Manager 模块生命周期管理器 | Module Lifecycle Manager 模块生命周期管理器 | design | design_only | D-INFRA-RUNTIME/Module Lifecycle Manager 模块生命周期管理器 | Module Lifecycle Manager 模块生命周期管理器 | design | design_only |
| D-INFRA-RUNTIME/Module Log Aggregator 模块日志聚合器 | Module Log Aggregator 模块日志聚合器 | design | design_only | D-INFRA-RUNTIME/Module Log Aggregator 模块日志聚合器 | Module Log Aggregator 模块日志聚合器 | design | design_only |
| D-INFRA-RUNTIME/Module Metrics Collector 模块度量采集器 | Module Metrics Collector 模块度量采集器 | design | design_only | D-INFRA-RUNTIME/Module Metrics Collector 模块度量采集器 | Module Metrics Collector 模块度量采集器 | design | design_only |
| D-INFRA-RUNTIME/Module Performance Profiler 模块性能分析器 | Module Performance Profiler 模块性能分析器 | design | design_only | D-INFRA-RUNTIME/Module Performance Profiler 模块性能分析器 | Module Performance Profiler 模块性能分析器 | design | design_only |
| D-INFRA-RUNTIME/Module Registry 模块注册中心 | Module Registry 模块注册中心 | design | design_only | D-INFRA-RUNTIME/Module Registry 模块注册中心 | Module Registry 模块注册中心 | design | design_only |
| D-INFRA-RUNTIME/Module Sandbox Isolator 模块沙箱隔离器 | Module Sandbox Isolator 模块沙箱隔离器 | design | design_only | D-INFRA-RUNTIME/Module Sandbox Isolator 模块沙箱隔离器 | Module Sandbox Isolator 模块沙箱隔离器 | design | design_only |
| D-INFRA-RUNTIME/Module Test Runner 模块测试运行器 | Module Test Runner 模块测试运行器 | design | design_only | D-INFRA-RUNTIME/Module Test Runner 模块测试运行器 | Module Test Runner 模块测试运行器 | design | design_only |
| D-INFRA-RUNTIME/Module Version Dependency Resolver 模块版本依赖解析器 | Module Version Dependency Resolver 模块... | design | design_only | D-INFRA-RUNTIME/Module Version Dependency Resolver 模块版本依赖解析器 | Module Version Dependency Resolver 模块... | design | design_only |
| D-INFRA-RUNTIME/Monitoring Dashboard Process 监控面板进程 | Monitoring Dashboard Process 监控面板进程 | design | design_only | D-INFRA-RUNTIME/Monitoring Dashboard Process 监控面板进程 | Monitoring Dashboard Process 监控面板进程 | design | design_only |
| D-INFRA-RUNTIME/Monitoring Data Aggregator 监控数据聚合器 | Monitoring Data Aggregator 监控数据聚合器 | design | design_only | D-INFRA-RUNTIME/Monitoring Data Aggregator 监控数据聚合器 | Monitoring Data Aggregator 监控数据聚合器 | design | design_only |
| D-INFRA-RUNTIME/Multi-Device State Coordinator 多端状态协调器 | Multi-Device State Coordinator 多端状态协调器 | design | design_only | D-INFRA-RUNTIME/Multi-Device State Coordinator 多端状态协调器 | Multi-Device State Coordinator 多端状态协调器 | design | design_only |
| D-INFRA-RUNTIME/Multi-Modal Input Router 多模态输入路由 | Multi-Modal Input Router 多模态输入路由 | design | design_only | D-INFRA-RUNTIME/Multi-Modal Input Router 多模态输入路由 | Multi-Modal Input Router 多模态输入路由 | design | design_only |
| D-INFRA-RUNTIME/Multi-Process Isolation & Runtime Architecture 多进程隔离与运行时架构 | Multi-Process Isolation & Runtime Arc... | design | design_only | D-INFRA-RUNTIME/Multi-Process Isolation & Runtime Architecture 多进程隔离与运行时架构 | Multi-Process Isolation & Runtime Arc... | design | design_only |
| D-INFRA-RUNTIME/Multi-Protocol Network Adapter 多协议网络适配器 | Multi-Protocol Network Adapter 多协议网络适配器 | design | design_only | D-INFRA-RUNTIME/Multi-Protocol Network Adapter 多协议网络适配器 | Multi-Protocol Network Adapter 多协议网络适配器 | design | design_only |
| D-INFRA-RUNTIME/Multi-Region Collaboration Manager 多区域协同管理器 | Multi-Region Collaboration Manager 多区... | design | design_only | D-INFRA-RUNTIME/Multi-Region Collaboration Manager 多区域协同管理器 | Multi-Region Collaboration Manager 多区... | design | design_only |
| D-INFRA-RUNTIME/NAS Storage NAS存储 | NAS Storage NAS存储 | design | design_only | D-INFRA-RUNTIME/NAS Storage NAS存储 | NAS Storage NAS存储 | design | design_only |
| D-INFRA-RUNTIME/NSSM+自研Supervisor 进程守护层 | NSSM+自研Supervisor 进程守护层 | design | design_only | D-INFRA-RUNTIME/NSSM+自研Supervisor 进程守护层 | NSSM+自研Supervisor 进程守护层 | design | design_only |
| D-INFRA-RUNTIME/NSSM注册Windows服务 NSSM Windows Service | NSSM注册Windows服务 NSSM Windows Service | design | design_only | D-INFRA-RUNTIME/NSSM注册Windows服务 NSSM Windows Service | NSSM注册Windows服务 NSSM Windows Service | design | design_only |
| D-INFRA-RUNTIME/Network Policy Manager 网络策略管理器 | Network Policy Manager 网络策略管理器 | design | design_only | D-INFRA-RUNTIME/Network Policy Manager 网络策略管理器 | Network Policy Manager 网络策略管理器 | design | design_only |
| D-INFRA-RUNTIME/Node Return Type Contractor 节点返回值类型契约器 | Node Return Type Contractor 节点返回值类型契约器 | design | design_only | D-INFRA-RUNTIME/Node Return Type Contractor 节点返回值类型契约器 | Node Return Type Contractor 节点返回值类型契约器 | design | design_only |
| D-INFRA-RUNTIME/P3 Process Specification P3进程规格 | P3 Process Specification P3进程规格 | design | design_only | D-INFRA-RUNTIME/P3 Process Specification P3进程规格 | P3 Process Specification P3进程规格 | design | design_only |
| D-INFRA-RUNTIME/Package Dependency Graph Generator 包依赖图生成器 | Package Dependency Graph Generator 包依... | design | design_only | D-INFRA-RUNTIME/Package Dependency Graph Generator 包依赖图生成器 | Package Dependency Graph Generator 包依... | design | design_only |
| D-INFRA-RUNTIME/Panel Layout Engine 面板布局引擎 | Panel Layout Engine 面板布局引擎 | design | design_only | D-INFRA-RUNTIME/Panel Layout Engine 面板布局引擎 | Panel Layout Engine 面板布局引擎 | design | design_only |
| D-INFRA-RUNTIME/Parquet Columnar Storage Parquet列式存储 | Parquet Columnar Storage Parquet列式存储 | design | design_only | D-INFRA-RUNTIME/Parquet Columnar Storage Parquet列式存储 | Parquet Columnar Storage Parquet列式存储 | design | design_only |
| D-INFRA-RUNTIME/Parquet Parquet列式存储格式 | Parquet Parquet列式存储格式 | design | design_only | D-INFRA-RUNTIME/Parquet Parquet列式存储格式 | Parquet Parquet列式存储格式 | design | design_only |
| D-INFRA-RUNTIME/Path Resolver 路径解析 | Path Resolver 路径解析 | design | design_only | D-INFRA-RUNTIME/Path Resolver 路径解析 | Path Resolver 路径解析 | design | design_only |
| D-INFRA-RUNTIME/Phase Retrospective Analyzer 阶段回顾分析器 | Phase Retrospective Analyzer 阶段回顾分析器 | design | design_only | D-INFRA-RUNTIME/Phase Retrospective Analyzer 阶段回顾分析器 | Phase Retrospective Analyzer 阶段回顾分析器 | design | design_only |
| D-INFRA-RUNTIME/Phase Synchronization Coordinator 阶段同步协调器 | Phase Synchronization Coordinator 阶段同... | design | design_only | D-INFRA-RUNTIME/Phase Synchronization Coordinator 阶段同步协调器 | Phase Synchronization Coordinator 阶段同... | design | design_only |
| D-INFRA-RUNTIME/Plugin System Manager 插件系统管理器 | Plugin System Manager 插件系统管理器 | design | design_only | D-INFRA-RUNTIME/Plugin System Manager 插件系统管理器 | Plugin System Manager 插件系统管理器 | design | design_only |
| D-INFRA-RUNTIME/Policy Conflict Auto Detector 策略冲突自动检测器 | Policy Conflict Auto Detector 策略冲突自动检测器 | design | design_only | D-INFRA-RUNTIME/Policy Conflict Auto Detector 策略冲突自动检测器 | Policy Conflict Auto Detector 策略冲突自动检测器 | design | design_only |

> (仅显示前 200 个模块，共 727 个)

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
    subgraph D_INFRA_RUNTIME["D-INFRA_RUNTIME runtime_integration"]
        D_INFRA_RUNTIME_A_Share_Diffusion_Model_Data_Augmentation_A["A-Share Diffusion Model Data Augmentation A股扩散模... design"]
        D_INFRA_RUNTIME_AB_Test_Dependency_Mapper_AB["AB Test Dependency Mapper AB测试依赖映射器 design"]
        D_INFRA_RUNTIME_API_Documentation_Synchronizer_API["API Documentation Synchronizer API文档同步器 design"]
        D_INFRA_RUNTIME_API_Version_Compatibility_Detector_API["API Version Compatibility Detector API版本兼容检测器 design"]
        D_INFRA_RUNTIME_API_Version_Manager_API["API Version Manager API版本管理器 design"]
        D_INFRA_RUNTIME_Alert_Escalation_Strategy_Engine["Alert Escalation Strategy Engine 告警升级策略引擎 design"]
        D_INFRA_RUNTIME_Alert_Silence_Manager["Alert Silence Manager 告警静默管理器 design"]
        D_INFRA_RUNTIME_Alternative_Data_Source_Expansion["Alternative Data Source Expansion 另类数据源扩展 design"]
        D_INFRA_RUNTIME_App["App 包装器 design"]
        D_INFRA_RUNTIME_Application_State_Snapshotter["Application State Snapshotter 应用状态快照器 design"]
        D_INFRA_RUNTIME_Architecture_Compliance_Checker["Architecture Compliance Checker 架构合规检查器 design"]
        D_INFRA_RUNTIME_Architecture_Evolution_Planner["Architecture Evolution Planner 架构演进规划器 design"]
        D_INFRA_RUNTIME_Architecture_Recommendation_Engine["Architecture Recommendation Engine 架构推荐引擎 design"]
        D_INFRA_RUNTIME_Automated_Code_Reviewer["Automated Code Reviewer 自动代码审查器 design"]
        D_INFRA_RUNTIME_Bandwidth_Optimizer["Bandwidth Optimizer 带宽优化 design"]
        D_INFRA_RUNTIME_Base["Base 基础 design"]
        D_INFRA_RUNTIME_Batch_Data_Processor["Batch Data Processor 批量数据处理器 design"]
        D_INFRA_RUNTIME_Blue_Green_Dependency_Mapper["Blue-Green Dependency Mapper 蓝绿依赖映射器 design"]
        D_INFRA_RUNTIME_Blueprint_Code_Sync["Blueprint Code Sync 蓝图代码同步 design"]
        D_INFRA_RUNTIME_CPU_Core_Allocation_Manager_CPU["CPU Core Allocation Manager CPU核心分配管理器 design"]
        D_INFRA_RUNTIME_Cache_Data_Preloader["Cache Data Preloader 缓存数据预加载器 design"]
        D_INFRA_RUNTIME_Cache_Warmup_Manager["Cache Warmup Manager 缓存预热管理器 design"]
        D_INFRA_RUNTIME_Canary_Dependency_Mapper["Canary Dependency Mapper 金丝雀依赖映射器 design"]
        D_INFRA_RUNTIME_Capacity_Alert["Capacity Alert 容量告警 design"]
        D_INFRA_RUNTIME_CapacityThresholdBreached["CapacityThresholdBreached 容量阈值突破事件 design"]
        D_INFRA_RUNTIME_Causal_ML_ML["Causal ML 深度补充 因果ML深度补充 design"]
        D_INFRA_RUNTIME_ChromaDB_Vector_Database_ChromaDB["ChromaDB Vector Database ChromaDB向量数据库 design"]
        D_INFRA_RUNTIME_Circular_Dependency_Detector["Circular Dependency Detector 循环依赖检测器 design"]
        D_INFRA_RUNTIME_ClickHouse_Database_ClickHouse["ClickHouse Database ClickHouse数据库 design"]
        D_INFRA_RUNTIME_Clock_Sync_Service["Clock Sync Service 时钟同步服务 design"]
    end
    D_INFRA_RUNTIME_Alert_Silence_Manager -.->|import_depends| D_INFRA_RUNTIME_Alert_Escalation_Strategy_Engine
    D_INFRA_RUNTIME_Canary_Dependency_Mapper -.->|import_depends| D_INFRA_RUNTIME_Blue_Green_Dependency_Mapper
    D_INFRA_RUNTIME_Blue_Green_Dependency_Mapper -.->|import_depends| D_INFRA_RUNTIME_AB_Test_Dependency_Mapper_AB
    D_INFRA_RUNTIME_Blueprint_Code_Sync -.->|import_depends| D_INFRA_RUNTIME_Base
    D_INFRA_RUNTIME_Base -.->|import_depends| D_INFRA_RUNTIME_App
    D_MKT_DATA["D-MKT_DATA design"]
    D_MKT_DATA -.->|data| D_INFRA_RUNTIME_Causal_ML_ML
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|config_depends| D_INFRA_RUNTIME_A_Share_Diffusion_Model_Data_Augmentation_A
    D_MKT_DATA -.->|config_depends| D_INFRA_RUNTIME_CPU_Core_Allocation_Manager_CPU
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_INTELLIGENCE -.->|data| D_INFRA_RUNTIME_CPU_Core_Allocation_Manager_CPU
    D_RISK["D-RISK design"]
    D_RISK -.->|event| D_INFRA_RUNTIME_Cache_Warmup_Manager
    D_AUTONOMY_CORE -.->|contract| D_INFRA_RUNTIME_Cache_Warmup_Manager
    D_PF_ALLOC["D-PF_ALLOC design"]
    D_PF_ALLOC -.->|contract| D_INFRA_RUNTIME_Cache_Data_Preloader
    D_ML_TRAIN["D-ML_TRAIN design"]
    D_ML_TRAIN -.->|data| D_INFRA_RUNTIME_Cache_Data_Preloader
    D_CROSS_ASSET["D-CROSS_ASSET design"]
    D_CROSS_ASSET -.->|event| D_INFRA_RUNTIME_Cache_Data_Preloader
    D_SECURITY["D-SECURITY design"]
    D_SECURITY -.->|config_depends| D_INFRA_RUNTIME_Batch_Data_Processor
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_GOVERNANCE -.->|data| D_INFRA_RUNTIME_Batch_Data_Processor
    D_RISK -.->|contract| D_INFRA_RUNTIME_Alert_Silence_Manager
    D_INTEGRATION["D-INTEGRATION design"]
    D_INTEGRATION -.->|data| D_INFRA_RUNTIME_Alert_Silence_Manager
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_INFRA_RUNTIME_Alert_Silence_Manager
    D_PF_CORE["D-PF_CORE design"]
    D_PF_CORE -.->|data| D_INFRA_RUNTIME_Alert_Escalation_Strategy_Engine
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_INFRA_RUNTIME_A_Share_Diffusion_Model_Data_Augmentation_A,D_INFRA_RUNTIME_AB_Test_Dependency_Mapper_AB,D_INFRA_RUNTIME_API_Documentation_Synchronizer_API,D_INFRA_RUNTIME_API_Version_Compatibility_Detector_API,D_INFRA_RUNTIME_API_Version_Manager_API,D_INFRA_RUNTIME_Alert_Escalation_Strategy_Engine,D_INFRA_RUNTIME_Alert_Silence_Manager,D_INFRA_RUNTIME_Alternative_Data_Source_Expansion,D_INFRA_RUNTIME_App,D_INFRA_RUNTIME_Application_State_Snapshotter,D_INFRA_RUNTIME_Architecture_Compliance_Checker,D_INFRA_RUNTIME_Architecture_Evolution_Planner,D_INFRA_RUNTIME_Architecture_Recommendation_Engine,D_INFRA_RUNTIME_Automated_Code_Reviewer,D_INFRA_RUNTIME_Bandwidth_Optimizer,D_INFRA_RUNTIME_Base,D_INFRA_RUNTIME_Batch_Data_Processor,D_INFRA_RUNTIME_Blue_Green_Dependency_Mapper,D_INFRA_RUNTIME_Blueprint_Code_Sync,D_INFRA_RUNTIME_CPU_Core_Allocation_Manager_CPU,D_INFRA_RUNTIME_Cache_Data_Preloader,D_INFRA_RUNTIME_Cache_Warmup_Manager,D_INFRA_RUNTIME_Canary_Dependency_Mapper,D_INFRA_RUNTIME_Capacity_Alert,D_INFRA_RUNTIME_CapacityThresholdBreached,D_INFRA_RUNTIME_Causal_ML_ML,D_INFRA_RUNTIME_ChromaDB_Vector_Database_ChromaDB,D_INFRA_RUNTIME_Circular_Dependency_Detector,D_INFRA_RUNTIME_ClickHouse_Database_ClickHouse,D_INFRA_RUNTIME_Clock_Sync_Service design
    class D_MKT_DATA,D_AUTONOMY_CORE,D_INTELLIGENCE,D_RISK,D_PF_ALLOC,D_ML_TRAIN,D_CROSS_ASSET,D_SECURITY,D_GOVERNANCE,D_INTEGRATION,D_COMPLIANCE,D_PF_CORE external_design
```

> (依赖图最多显示前 30 个节点，共 727 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-SHARED | 67 | import_depends,contract,data,event | D-SHARED | 67 | import_depends,contract,data,event |
| D-INTEGRATION | 26 | import_depends | D-INTEGRATION | 26 | import_depends |
| D-GOVERNANCE | 17 | import_depends | D-GOVERNANCE | 17 | import_depends |
| D-GOV_AUDIT | 12 | import_depends | D-GOV_AUDIT | 12 | import_depends |
| D-OPS | 2 | import_depends | D-OPS | 2 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends | D-BEHAVIORAL_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 194 | runtime,import_depends,test_depends,config_depends,data,event,contract,import | D-GOVERNANCE | 194 | runtime,import_depends,test_depends,config_depends,data,event,contract,import |
| D-RISK | 63 | data,contract,config_depends,event | D-RISK | 63 | data,contract,config_depends,event |
| D-COMPLIANCE | 62 | contract,data,event,config_depends | D-COMPLIANCE | 62 | contract,data,event,config_depends |
| D-OPS | 58 | import_depends,test_depends,domain_dependency,data,contract,config_depends,event | D-OPS | 58 | import_depends,test_depends,domain_dependency,data,contract,config_depends,event |
| D-SECURITY | 50 | contract,event,config_depends,data | D-SECURITY | 50 | contract,event,config_depends,data |
| D-INTEGRATION | 31 | domain_dependency,contract,data,event,config_depends | D-INTEGRATION | 31 | domain_dependency,contract,data,event,config_depends |
| D-INFRA_OPS | 31 | import_depends,contract,event,config_depends,data | D-INFRA_OPS | 31 | import_depends,contract,event,config_depends,data |
| D-AUTONOMY_CORE | 31 | config_depends,event,data,contract | D-AUTONOMY_CORE | 31 | config_depends,event,data,contract |
| D-SIGNAL | 27 | data,contract,event,config_depends | D-SIGNAL | 27 | data,contract,event,config_depends |
| D-MKT_DATA | 24 | contract,data,config_depends,event | D-MKT_DATA | 24 | contract,data,config_depends,event |
| D-DATA_ENG | 20 | domain_dependency,contract,event,data,config_depends | D-DATA_ENG | 20 | domain_dependency,contract,event,data,config_depends |
| D-FACTOR | 19 | contract,data,event,config_depends | D-FACTOR | 19 | contract,data,event,config_depends |
| D-PF_CORE | 15 | contract,data,event,config_depends | D-PF_CORE | 15 | contract,data,event,config_depends |
| D-EX_SOR | 12 | domain_dependency,data,contract,event | D-EX_SOR | 12 | domain_dependency,data,contract,event |
| D-ML_TRAIN | 11 | contract,data,event,config_depends | D-ML_TRAIN | 11 | contract,data,event,config_depends |
| D-REPORTING | 10 | contract,event,config_depends,data | D-REPORTING | 10 | contract,event,config_depends,data |
| D-PF_ALLOC | 10 | event,data,config_depends,contract | D-PF_ALLOC | 10 | event,data,config_depends,contract |
| D-KNOWLEDGE | 10 | event,contract,data | D-KNOWLEDGE | 10 | event,contract,data |
| D-INTELLIGENCE | 10 | import_depends,data,contract,event,config_depends | D-INTELLIGENCE | 10 | import_depends,data,contract,event,config_depends |
| D-EX_CORE | 10 | contract,event,data,config_depends | D-EX_CORE | 10 | contract,event,data,config_depends |
| D-AUTONOMY_PERM | 10 | test_depends,event,data,config_depends,contract | D-AUTONOMY_PERM | 10 | test_depends,event,data,config_depends,contract |
| D-CROSS_ASSET | 9 | contract,config_depends,event,data | D-CROSS_ASSET | 9 | contract,config_depends,event,data |
| D-TRADING | 7 | contract,import_depends,event,data | D-TRADING | 7 | contract,import_depends,event,data |
| D-SHARED | 7 | import_depends | D-SHARED | 7 | import_depends |
| D-SIMULATION | 6 | event,contract | D-SIMULATION | 6 | event,contract |
| D-ML_SERVE | 6 | domain_dependency,event,contract,data | D-ML_SERVE | 6 | domain_dependency,event,contract,data |
| D-FRONTEND | 6 | data,config_depends,contract | D-FRONTEND | 6 | data,config_depends,contract |
| D-GOV_AUDIT | 5 | import_depends | D-GOV_AUDIT | 5 | import_depends |
| D-ALT_DATA | 3 | event,data,contract | D-ALT_DATA | 3 | event,data,contract |
| D-POSITION | 2 | event,contract | D-POSITION | 2 | event,contract |
| D-DATA_SEC | 2 | config_depends,data | D-DATA_SEC | 2 | config_depends,data |
| D-DATA_GOV | 2 | event | D-DATA_GOV | 2 | event |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
