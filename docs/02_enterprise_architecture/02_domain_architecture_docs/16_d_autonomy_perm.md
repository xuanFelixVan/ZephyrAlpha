---
doc_type: domain_architecture_doc
title: D-AUTONOMY_PERM 自治保护架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 16_d_autonomy_perm 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 16 | Number | 16 |
| 域ID | D-AUTONOMY_PERM | Domain ID | D-AUTONOMY_PERM |
| 域名称 | 自治保护 | Domain Name | 自治保护 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 270 | Module Count | 270 |
| 域内依赖 | 181 | Internal Dependencies | 181 |
| 跨域入边 | 174 | Cross-domain Incoming | 174 |
| 跨域出边 | 339 | Cross-domain Outgoing | 339 |
| 设计态模块 | 197 | Design Modules | 197 |
| 原型态模块 | 63 | Prototype Modules | 63 |
| 生产态模块 | 4 | Production Modules | 4 |
| 容量 | 270/150 (超容) | Capacity | 270/150 (超容) |
| 描述 | 自治保护域。负责自治系统的安全边界保护，包括权限守卫、升级引擎、预算执行器、回滚系统。 | Description | 自治保护域。负责自治系统的安全边界保护，包括权限守卫、升级引擎、预算执行器、回滚系统。 |

## 模块清单 / Module List

共 270 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-AUTONOMY-PERM/AI Autonomy Boundary Not Self-Extendable AI自治边界不可被AI自行扩展 | AI Autonomy Boundary Not Self-Extenda... | design | design_only | D-AUTONOMY-PERM/AI Autonomy Boundary Not Self-Extendable AI自治边界不可被AI自行扩展 | AI Autonomy Boundary Not Self-Extenda... | design | design_only |
| D-AUTONOMY-PERM/AI Comprehension Cost Dynamic Estimator AI理解成本动态估算器 | AI Comprehension Cost Dynamic Estimat... | design | design_only | D-AUTONOMY-PERM/AI Comprehension Cost Dynamic Estimator AI理解成本动态估算器 | AI Comprehension Cost Dynamic Estimat... | design | design_only |
| D-AUTONOMY-PERM/AI Governance Framework Compliance Assessor AI治理框架合规性评估器 | AI Governance Framework Compliance As... | design | design_only | D-AUTONOMY-PERM/AI Governance Framework Compliance Assessor AI治理框架合规性评估器 | AI Governance Framework Compliance As... | design | design_only |
| D-AUTONOMY-PERM/AI Risk Assessor AI风险评估器 | AI Risk Assessor AI风险评估器 | design | design_only | D-AUTONOMY-PERM/AI Risk Assessor AI风险评估器 | AI Risk Assessor AI风险评估器 | design | design_only |
| D-AUTONOMY-PERM/AI Risk Classifier AI风险分类器 | AI Risk Classifier AI风险分类器 | design | design_only | D-AUTONOMY-PERM/AI Risk Classifier AI风险分类器 | AI Risk Classifier AI风险分类器 | design | design_only |
| D-AUTONOMY-PERM/AI Risk Dependency Mapper AI风险依赖映射器 | AI Risk Dependency Mapper AI风险依赖映射器 | design | design_only | D-AUTONOMY-PERM/AI Risk Dependency Mapper AI风险依赖映射器 | AI Risk Dependency Mapper AI风险依赖映射器 | design | design_only |
| D-AUTONOMY-PERM/AI-Driven Saga Orchestrator AI驱动Saga编排器 | AI-Driven Saga Orchestrator AI驱动Saga编排器 | design | design_only | D-AUTONOMY-PERM/AI-Driven Saga Orchestrator AI驱动Saga编排器 | AI-Driven Saga Orchestrator AI驱动Saga编排器 | design | design_only |
| D-AUTONOMY-PERM/APPROVE 通过 | APPROVE 通过 | design | design_only | D-AUTONOMY-PERM/APPROVE 通过 | APPROVE 通过 | design | design_only |
| D-AUTONOMY-PERM/ARS Dual-Track Settlement ARS双轨结算模型 | ARS Dual-Track Settlement ARS双轨结算模型 | design | design_only | D-AUTONOMY-PERM/ARS Dual-Track Settlement ARS双轨结算模型 | ARS Dual-Track Settlement ARS双轨结算模型 | design | design_only |
| D-AUTONOMY-PERM/AWS Agentic AI Security Scoping Matrix AWS Agent AI安全范围矩阵 | AWS Agentic AI Security Scoping Matri... | design | design_only | D-AUTONOMY-PERM/AWS Agentic AI Security Scoping Matrix AWS Agent AI安全范围矩阵 | AWS Agentic AI Security Scoping Matri... | design | design_only |
| D-AUTONOMY-PERM/Agent Cannot Auto-Execute Large Order Agent不可自动执行大额下单 | Agent Cannot Auto-Execute Large Order... | design | design_only | D-AUTONOMY-PERM/Agent Cannot Auto-Execute Large Order Agent不可自动执行大额下单 | Agent Cannot Auto-Execute Large Order... | design | design_only |
| D-AUTONOMY-PERM/Agent Cannot Auto-Online Strategy Agent不可自动上线新策略 | Agent Cannot Auto-Online Strategy Age... | design | design_only | D-AUTONOMY-PERM/Agent Cannot Auto-Online Strategy Agent不可自动上线新策略 | Agent Cannot Auto-Online Strategy Age... | design | design_only |
| D-AUTONOMY-PERM/Agent Cannot Autonomously Modify Boundary Agent不可自主修改自治边界 | Agent Cannot Autonomously Modify Boun... | design | design_only | D-AUTONOMY-PERM/Agent Cannot Autonomously Modify Boundary Agent不可自主修改自治边界 | Agent Cannot Autonomously Modify Boun... | design | design_only |
| D-AUTONOMY-PERM/Audit Trail 审计链 | Audit Trail 审计链 | design | design_only | D-AUTONOMY-PERM/Audit Trail 审计链 | Audit Trail 审计链 | design | design_only |
| D-AUTONOMY-PERM/Audit-Persistence Dual-Write Coordinator 审计-持久化双写协调器 | Audit-Persistence Dual-Write Coordina... | design | design_only | D-AUTONOMY-PERM/Audit-Persistence Dual-Write Coordinator 审计-持久化双写协调器 | Audit-Persistence Dual-Write Coordina... | design | design_only |
| D-AUTONOMY-PERM/AuditLogWrite 审计日志写入 | AuditLogWrite 审计日志写入 | design | design_only | D-AUTONOMY-PERM/AuditLogWrite 审计日志写入 | AuditLogWrite 审计日志写入 | design | design_only |
| D-AUTONOMY-PERM/AuditRecord 审计记录 | AuditRecord 审计记录 | design | design_only | D-AUTONOMY-PERM/AuditRecord 审计记录 | AuditRecord 审计记录 | design | design_only |
| D-AUTONOMY-PERM/Auto Fix Engine 自动修复引擎 | Auto Fix Engine 自动修复引擎 | design | design_only | D-AUTONOMY-PERM/Auto Fix Engine 自动修复引擎 | Auto Fix Engine 自动修复引擎 | design | design_only |
| D-AUTONOMY-PERM/Auto-Guard Async Approval Manager Auto-Guard异步审批管理器 | Auto-Guard Async Approval Manager Aut... | design | design_only | D-AUTONOMY-PERM/Auto-Guard Async Approval Manager Auto-Guard异步审批管理器 | Auto-Guard Async Approval Manager Aut... | design | design_only |
| D-AUTONOMY-PERM/Autonomy Boundary Change Process 自治边界变更流程 | Autonomy Boundary Change Process 自治边界... | design | design_only | D-AUTONOMY-PERM/Autonomy Boundary Change Process 自治边界变更流程 | Autonomy Boundary Change Process 自治边界... | design | design_only |
| D-AUTONOMY-PERM/Autonomy Fuse 自治熔断器 | Autonomy Fuse 自治熔断器 | design | design_only | D-AUTONOMY-PERM/Autonomy Fuse 自治熔断器 | Autonomy Fuse 自治熔断器 | design | design_only |
| D-AUTONOMY-PERM/Backtest-Live Deviation Monitor 回测-实盘偏差监控器 | Backtest-Live Deviation Monitor 回测-实盘... | design | design_only | D-AUTONOMY-PERM/Backtest-Live Deviation Monitor 回测-实盘偏差监控器 | Backtest-Live Deviation Monitor 回测-实盘... | design | design_only |
| D-AUTONOMY-PERM/BacktestRealtimeDeviation 回测-实盘偏差 | BacktestRealtimeDeviation 回测-实盘偏差 | design | design_only | D-AUTONOMY-PERM/BacktestRealtimeDeviation 回测-实盘偏差 | BacktestRealtimeDeviation 回测-实盘偏差 | design | design_only |
| D-AUTONOMY-PERM/BacktestRealtimeDeviationAlert 回测实盘偏差告警 | BacktestRealtimeDeviationAlert 回测实盘偏差告警 | design | design_only | D-AUTONOMY-PERM/BacktestRealtimeDeviationAlert 回测实盘偏差告警 | BacktestRealtimeDeviationAlert 回测实盘偏差告警 | design | design_only |
| D-AUTONOMY-PERM/BlockCommand 阻止指令 | BlockCommand 阻止指令 | design | design_only | D-AUTONOMY-PERM/BlockCommand 阻止指令 | BlockCommand 阻止指令 | design | design_only |
| D-AUTONOMY-PERM/Budget Enforcer On-Demand Activator Budget Enforcer按需激活器 | Budget Enforcer On-Demand Activator B... | design | design_only | D-AUTONOMY-PERM/Budget Enforcer On-Demand Activator Budget Enforcer按需激活器 | Budget Enforcer On-Demand Activator B... | design | design_only |
| D-AUTONOMY-PERM/BudgetExemption 预算豁免 | BudgetExemption 预算豁免 | design | design_only | D-AUTONOMY-PERM/BudgetExemption 预算豁免 | BudgetExemption 预算豁免 | design | design_only |
| D-AUTONOMY-PERM/Choreography Saga Engine 协调式Saga引擎 | Choreography Saga Engine 协调式Saga引擎 | design | design_only | D-AUTONOMY-PERM/Choreography Saga Engine 协调式Saga引擎 | Choreography Saga Engine 协调式Saga引擎 | design | design_only |
| D-AUTONOMY-PERM/Circuit Breaker State Machine 熔断器状态机 | Circuit Breaker State Machine 熔断器状态机 | design | design_only | D-AUTONOMY-PERM/Circuit Breaker State Machine 熔断器状态机 | Circuit Breaker State Machine 熔断器状态机 | design | design_only |
| D-AUTONOMY-PERM/Cluster Behavior Risk Protection 群集行为风险防护 | Cluster Behavior Risk Protection 群集行为... | design | design_only | D-AUTONOMY-PERM/Cluster Behavior Risk Protection 群集行为风险防护 | Cluster Behavior Risk Protection 群集行为... | design | design_only |
| D-AUTONOMY-PERM/Code Health Assessor 代码健康度评估器 | Code Health Assessor 代码健康度评估器 | design | design_only | D-AUTONOMY-PERM/Code Health Assessor 代码健康度评估器 | Code Health Assessor 代码健康度评估器 | design | design_only |
| D-AUTONOMY-PERM/Compensation Action Manager 补偿动作管理器 | Compensation Action Manager 补偿动作管理器 | design | design_only | D-AUTONOMY-PERM/Compensation Action Manager 补偿动作管理器 | Compensation Action Manager 补偿动作管理器 | design | design_only |
| D-AUTONOMY-PERM/Compensation Dependency Graph Analyzer 补偿依赖图分析器 | Compensation Dependency Graph Analyze... | design | design_only | D-AUTONOMY-PERM/Compensation Dependency Graph Analyzer 补偿依赖图分析器 | Compensation Dependency Graph Analyze... | design | design_only |
| D-AUTONOMY-PERM/Core Chain E2E Health Monitor 核心链路端到端健康监控器 | Core Chain E2E Health Monitor 核心链路端到端... | design | design_only | D-AUTONOMY-PERM/Core Chain E2E Health Monitor 核心链路端到端健康监控器 | Core Chain E2E Health Monitor 核心链路端到端... | design | design_only |
| D-AUTONOMY-PERM/CoreReadOnlyState CORE只读状态 | CoreReadOnlyState CORE只读状态 | design | design_only | D-AUTONOMY-PERM/CoreReadOnlyState CORE只读状态 | CoreReadOnlyState CORE只读状态 | design | design_only |
| D-AUTONOMY-PERM/Cross-Saga Transaction Coordinator 跨Saga事务协调器 | Cross-Saga Transaction Coordinator 跨S... | design | design_only | D-AUTONOMY-PERM/Cross-Saga Transaction Coordinator 跨Saga事务协调器 | Cross-Saga Transaction Coordinator 跨S... | design | design_only |
| D-AUTONOMY-PERM/D-AUT-PERM | D-AUT-PERM | design | design_only | D-AUTONOMY-PERM/D-AUT-PERM | D-AUT-PERM | design | design_only |
| D-AUTONOMY-PERM/D-AUTONOMY-PERM | D-AUTONOMY-PERM | design | design_only | D-AUTONOMY-PERM/D-AUTONOMY-PERM | D-AUTONOMY-PERM | design | design_only |
| D-AUTONOMY-PERM/Dependency Upgrade Sandbox Approval Gateway 依赖升级沙箱审批网关 | Dependency Upgrade Sandbox Approval G... | design | design_only | D-AUTONOMY-PERM/Dependency Upgrade Sandbox Approval Gateway 依赖升级沙箱审批网关 | Dependency Upgrade Sandbox Approval G... | design | design_only |
| D-AUTONOMY-PERM/DependencyUpgradeApproval 依赖升级审批 | DependencyUpgradeApproval 依赖升级审批 | design | design_only | D-AUTONOMY-PERM/DependencyUpgradeApproval 依赖升级审批 | DependencyUpgradeApproval 依赖升级审批 | design | design_only |
| D-AUTONOMY-PERM/DependencyUpgradeCompleted 依赖库升级完成 | DependencyUpgradeCompleted 依赖库升级完成 | design | design_only | D-AUTONOMY-PERM/DependencyUpgradeCompleted 依赖库升级完成 | DependencyUpgradeCompleted 依赖库升级完成 | design | design_only |
| D-AUTONOMY-PERM/Drift Detector Statistical Drift Checker Drift Detector统计漂移检测器 | Drift Detector Statistical Drift Chec... | design | design_only | D-AUTONOMY-PERM/Drift Detector Statistical Drift Checker Drift Detector统计漂移检测器 | Drift Detector Statistical Drift Chec... | design | design_only |
| D-AUTONOMY-PERM/Drift Guard 漂移守卫 | Drift Guard 漂移守卫 | design | design_only | D-AUTONOMY-PERM/Drift Guard 漂移守卫 | Drift Guard 漂移守卫 | design | design_only |
| D-AUTONOMY-PERM/DriftDetected 漂移检测 | DriftDetected 漂移检测 | design | design_only | D-AUTONOMY-PERM/DriftDetected 漂移检测 | DriftDetected 漂移检测 | design | design_only |
| D-AUTONOMY-PERM/Dual-Storage Rollback Coordinator 双存储回滚协调器 | Dual-Storage Rollback Coordinator 双存储... | design | design_only | D-AUTONOMY-PERM/Dual-Storage Rollback Coordinator 双存储回滚协调器 | Dual-Storage Rollback Coordinator 双存储... | design | design_only |
| D-AUTONOMY-PERM/Enhanced Confidence Cascade Mapper 增强置信度级联映射器 | Enhanced Confidence Cascade Mapper 增强... | design | design_only | D-AUTONOMY-PERM/Enhanced Confidence Cascade Mapper 增强置信度级联映射器 | Enhanced Confidence Cascade Mapper 增强... | design | design_only |
| D-AUTONOMY-PERM/Escalation Protocol 升级协议 | Escalation Protocol 升级协议 | design | design_only | D-AUTONOMY-PERM/Escalation Protocol 升级协议 | Escalation Protocol 升级协议 | design | design_only |
| D-AUTONOMY-PERM/FLATTEN 紧急平仓 | FLATTEN 紧急平仓 | design | design_only | D-AUTONOMY-PERM/FLATTEN 紧急平仓 | FLATTEN 紧急平仓 | design | design_only |
| ...TONOMY-PERM/Feedback Loop Three-Layer Escalation Trigger Feedback Loop三层升级触发器 | Feedback Loop Three-Layer Escalation ... | design | design_only | ...TONOMY-PERM/Feedback Loop Three-Layer Escalation Trigger Feedback Loop三层升级触发器 | Feedback Loop Three-Layer Escalation ... | design | design_only |
| D-AUTONOMY-PERM/Four-Level Autonomy Boundary Agent自治边界分四级 | Four-Level Autonomy Boundary Agent自治边... | design | design_only | D-AUTONOMY-PERM/Four-Level Autonomy Boundary Agent自治边界分四级 | Four-Level Autonomy Boundary Agent自治边... | design | design_only |
| D-AUTONOMY-PERM/Four-Level Autonomy Model 四级自治模型 | Four-Level Autonomy Model 四级自治模型 | design | design_only | D-AUTONOMY-PERM/Four-Level Autonomy Model 四级自治模型 | Four-Level Autonomy Model 四级自治模型 | design | design_only |
| D-AUTONOMY-PERM/Governance Dashboard 治理仪表盘 | Governance Dashboard 治理仪表盘 | design | design_only | D-AUTONOMY-PERM/Governance Dashboard 治理仪表盘 | Governance Dashboard 治理仪表盘 | design | design_only |
| D-AUTONOMY-PERM/Governance Phase Check Slimmer Governance Phase Check精简器 | Governance Phase Check Slimmer Govern... | design | design_only | D-AUTONOMY-PERM/Governance Phase Check Slimmer Governance Phase Check精简器 | Governance Phase Check Slimmer Govern... | design | design_only |
| D-AUTONOMY-PERM/Governance Policy Engine 治理策略引擎 | Governance Policy Engine 治理策略引擎 | design | design_only | D-AUTONOMY-PERM/Governance Policy Engine 治理策略引擎 | Governance Policy Engine 治理策略引擎 | design | design_only |
| D-AUTONOMY-PERM/HITL Confidence Upgrade HITL置信度升级 | HITL Confidence Upgrade HITL置信度升级 | design | design_only | D-AUTONOMY-PERM/HITL Confidence Upgrade HITL置信度升级 | HITL Confidence Upgrade HITL置信度升级 | design | design_only |
| D-AUTONOMY-PERM/HITL Human-in-the-Loop 人在闭环机制 | HITL Human-in-the-Loop 人在闭环机制 | design | design_only | D-AUTONOMY-PERM/HITL Human-in-the-Loop 人在闭环机制 | HITL Human-in-the-Loop 人在闭环机制 | design | design_only |
| D-AUTONOMY-PERM/HITL Mechanism HITL人在闭环机制 | HITL Mechanism HITL人在闭环机制 | design | design_only | D-AUTONOMY-PERM/HITL Mechanism HITL人在闭环机制 | HITL Mechanism HITL人在闭环机制 | design | design_only |
| D-AUTONOMY-PERM/Half-Open Probe 熔断器半开试探 | Half-Open Probe 熔断器半开试探 | design | design_only | D-AUTONOMY-PERM/Half-Open Probe 熔断器半开试探 | Half-Open Probe 熔断器半开试探 | design | design_only |
| D-AUTONOMY-PERM/Hard Block 硬阻断 | Hard Block 硬阻断 | design | design_only | D-AUTONOMY-PERM/Hard Block 硬阻断 | Hard Block 硬阻断 | design | design_only |
| D-AUTONOMY-PERM/Hard Reset Permission Gate Hard Reset权限门控 | Hard Reset Permission Gate Hard Reset... | design | design_only | D-AUTONOMY-PERM/Hard Reset Permission Gate Hard Reset权限门控 | Hard Reset Permission Gate Hard Reset... | design | design_only |
| D-AUTONOMY-PERM/Hard-Gate 硬门禁架构 | Hard-Gate 硬门禁架构 | design | design_only | D-AUTONOMY-PERM/Hard-Gate 硬门禁架构 | Hard-Gate 硬门禁架构 | design | design_only |
| D-AUTONOMY-PERM/Health Check Service 健康检查服务 | Health Check Service 健康检查服务 | design | design_only | D-AUTONOMY-PERM/Health Check Service 健康检查服务 | Health Check Service 健康检查服务 | design | design_only |
| D-AUTONOMY-PERM/HealthReport 健康报告 | HealthReport 健康报告 | design | design_only | D-AUTONOMY-PERM/HealthReport 健康报告 | HealthReport 健康报告 | design | design_only |
| D-AUTONOMY-PERM/Immutable Audit Log Writer 不可变审计日志写入器 | Immutable Audit Log Writer 不可变审计日志写入器 | design | design_only | D-AUTONOMY-PERM/Immutable Audit Log Writer 不可变审计日志写入器 | Immutable Audit Log Writer 不可变审计日志写入器 | design | design_only |
| D-AUTONOMY-PERM/KILLSWITCH.md AI Agent Emergency Stop Protocol AI Agent紧急停止协议 | KILLSWITCH.md AI Agent Emergency Stop... | design | design_only | D-AUTONOMY-PERM/KILLSWITCH.md AI Agent Emergency Stop Protocol AI Agent紧急停止协议 | KILLSWITCH.md AI Agent Emergency Stop... | design | design_only |
| D-AUTONOMY-PERM/Kill Switch Controlled Reentry Kill Switch激活后必须受控重入 | Kill Switch Controlled Reentry Kill S... | design | design_only | D-AUTONOMY-PERM/Kill Switch Controlled Reentry Kill Switch激活后必须受控重入 | Kill Switch Controlled Reentry Kill S... | design | design_only |
| D-AUTONOMY-PERM/Kill Switch Direct Path Kill Switch直通路径 | Kill Switch Direct Path Kill Switch直通路径 | design | design_only | D-AUTONOMY-PERM/Kill Switch Direct Path Kill Switch直通路径 | Kill Switch Direct Path Kill Switch直通路径 | design | design_only |
| D-AUTONOMY-PERM/Kill Switch Layered & Local Evaluated Kill Switch必须分层且本地评估 | Kill Switch Layered & Local Evaluated... | design | design_only | D-AUTONOMY-PERM/Kill Switch Layered & Local Evaluated Kill Switch必须分层且本地评估 | Kill Switch Layered & Local Evaluated... | design | design_only |
| D-AUTONOMY-PERM/Kill Switch 紧急制动开关 | Kill Switch 紧急制动开关 | design | design_only | D-AUTONOMY-PERM/Kill Switch 紧急制动开关 | Kill Switch 紧急制动开关 | design | design_only |
| D-AUTONOMY-PERM/KillSwitchDirect Kill Switch直通 | KillSwitchDirect Kill Switch直通 | design | design_only | D-AUTONOMY-PERM/KillSwitchDirect Kill Switch直通 | KillSwitchDirect Kill Switch直通 | design | design_only |
| D-AUTONOMY-PERM/KillSwitchDirectActivated Kill Switch直通激活 | KillSwitchDirectActivated Kill Switch... | design | design_only | D-AUTONOMY-PERM/KillSwitchDirectActivated Kill Switch直通激活 | KillSwitchDirectActivated Kill Switch... | design | design_only |
| D-AUTONOMY-PERM/KillSwitch直通路径 KillSwitch Direct Path | KillSwitch直通路径 KillSwitch Direct Path | design | design_only | D-AUTONOMY-PERM/KillSwitch直通路径 KillSwitch Direct Path | KillSwitch直通路径 KillSwitch Direct Path | design | design_only |
| D-AUTONOMY-PERM/Knowledge Snapshot Rollback Manager 知识快照回滚管理器 | Knowledge Snapshot Rollback Manager 知... | design | design_only | D-AUTONOMY-PERM/Knowledge Snapshot Rollback Manager 知识快照回滚管理器 | Knowledge Snapshot Rollback Manager 知... | design | design_only |
| D-AUTONOMY-PERM/Knowledge Write Guard Protector 知识Write Guard保护器 | Knowledge Write Guard Protector 知识Wri... | design | design_only | D-AUTONOMY-PERM/Knowledge Write Guard Protector 知识Write Guard保护器 | Knowledge Write Guard Protector 知识Wri... | design | design_only |
| D-AUTONOMY-PERM/LLM Cost Guard LLM成本守卫 | LLM Cost Guard LLM成本守卫 | design | design_only | D-AUTONOMY-PERM/LLM Cost Guard LLM成本守卫 | LLM Cost Guard LLM成本守卫 | design | design_only |
| D-AUTONOMY-PERM/Large Order Requires Approval 大额下单需人工审批 | Large Order Requires Approval 大额下单需人工审批 | design | design_only | D-AUTONOMY-PERM/Large Order Requires Approval 大额下单需人工审批 | Large Order Requires Approval 大额下单需人工审批 | design | design_only |
| D-AUTONOMY-PERM/Learning System Kill Switch 学习系统Kill Switch | Learning System Kill Switch 学习系统Kill ... | design | design_only | D-AUTONOMY-PERM/Learning System Kill Switch 学习系统Kill Switch | Learning System Kill Switch 学习系统Kill ... | design | design_only |
| D-AUTONOMY-PERM/Level 0-3 Autonomy Levels 0-3自治级别 | Level 0-3 Autonomy Levels 0-3自治级别 | design | design_only | D-AUTONOMY-PERM/Level 0-3 Autonomy Levels 0-3自治级别 | Level 0-3 Autonomy Levels 0-3自治级别 | design | design_only |
| D-AUTONOMY-PERM/Local Model 本地推理模型 | Local Model 本地推理模型 | design | design_only | D-AUTONOMY-PERM/Local Model 本地推理模型 | Local Model 本地推理模型 | design | design_only |
| D-AUTONOMY-PERM/M10 Audit Report Finding Format Generator M10审计报告Finding格式生成器 | M10 Audit Report Finding Format Gener... | design | design_only | D-AUTONOMY-PERM/M10 Audit Report Finding Format Generator M10审计报告Finding格式生成器 | M10 Audit Report Finding Format Gener... | design | design_only |
| D-AUTONOMY-PERM/MCP Gateway Rate-Limit Audit Manager MCP网关限流审计管理器 | MCP Gateway Rate-Limit Audit Manager ... | design | design_only | D-AUTONOMY-PERM/MCP Gateway Rate-Limit Audit Manager MCP网关限流审计管理器 | MCP Gateway Rate-Limit Audit Manager ... | design | design_only |
| D-AUTONOMY-PERM/Model Drift Dependency Propagator 模型漂移依赖传播器 | Model Drift Dependency Propagator 模型漂... | design | design_only | D-AUTONOMY-PERM/Model Drift Dependency Propagator 模型漂移依赖传播器 | Model Drift Dependency Propagator 模型漂... | design | design_only |
| D-AUTONOMY-PERM/Model Drift Detector 模型漂移检测器 | Model Drift Detector 模型漂移检测器 | design | design_only | D-AUTONOMY-PERM/Model Drift Detector 模型漂移检测器 | Model Drift Detector 模型漂移检测器 | design | design_only |
| D-AUTONOMY-PERM/Model Inventory Dependency Graph Builder 模型清单依赖图构建器 | Model Inventory Dependency Graph Buil... | design | design_only | D-AUTONOMY-PERM/Model Inventory Dependency Graph Builder 模型清单依赖图构建器 | Model Inventory Dependency Graph Buil... | design | design_only |
| D-AUTONOMY-PERM/Model Monitoring Dependency Tracker 模型监控依赖追踪器 | Model Monitoring Dependency Tracker 模... | design | design_only | D-AUTONOMY-PERM/Model Monitoring Dependency Tracker 模型监控依赖追踪器 | Model Monitoring Dependency Tracker 模... | design | design_only |
| D-AUTONOMY-PERM/Model Override Dependency Impact Analyzer 模型覆盖依赖影响分析器 | Model Override Dependency Impact Anal... | design | design_only | D-AUTONOMY-PERM/Model Override Dependency Impact Analyzer 模型覆盖依赖影响分析器 | Model Override Dependency Impact Anal... | design | design_only |
| D-AUTONOMY-PERM/Model Override Impact Analyzer 模型覆盖影响分析器 | Model Override Impact Analyzer 模型覆盖影响分析器 | design | design_only | D-AUTONOMY-PERM/Model Override Impact Analyzer 模型覆盖影响分析器 | Model Override Impact Analyzer 模型覆盖影响分析器 | design | design_only |
| D-AUTONOMY-PERM/Model Registry 模型注册表 | Model Registry 模型注册表 | design | design_only | D-AUTONOMY-PERM/Model Registry 模型注册表 | Model Registry 模型注册表 | design | design_only |
| D-AUTONOMY-PERM/Model Risk Tier Classifier 模型风险分级器 | Model Risk Tier Classifier 模型风险分级器 | design | design_only | D-AUTONOMY-PERM/Model Risk Tier Classifier 模型风险分级器 | Model Risk Tier Classifier 模型风险分级器 | design | design_only |
| D-AUTONOMY-PERM/Model Risk Tier Dependency Classifier 模型风险等级依赖分类器 | Model Risk Tier Dependency Classifier... | design | design_only | D-AUTONOMY-PERM/Model Risk Tier Dependency Classifier 模型风险等级依赖分类器 | Model Risk Tier Dependency Classifier... | design | design_only |
| D-AUTONOMY-PERM/Model Validation Dependency Orchestrator v2 模型验证依赖编排器v2 | Model Validation Dependency Orchestra... | design | design_only | D-AUTONOMY-PERM/Model Validation Dependency Orchestrator v2 模型验证依赖编排器v2 | Model Validation Dependency Orchestra... | design | design_only |
| D-AUTONOMY-PERM/Model Validation Dependency Orchestrator 模型验证依赖编排器 | Model Validation Dependency Orchestra... | design | design_only | D-AUTONOMY-PERM/Model Validation Dependency Orchestrator 模型验证依赖编排器 | Model Validation Dependency Orchestra... | design | design_only |
| D-AUTONOMY-PERM/NIST AI 100-5 Three-Layer Security NIST AI 100-5三层安全 | NIST AI 100-5 Three-Layer Security NI... | design | design_only | D-AUTONOMY-PERM/NIST AI 100-5 Three-Layer Security NIST AI 100-5三层安全 | NIST AI 100-5 Three-Layer Security NI... | design | design_only |
| D-AUTONOMY-PERM/NVIDIA Agentic Autonomy Levels NVIDIA Agent自治级别 | NVIDIA Agentic Autonomy Levels NVIDIA... | design | design_only | D-AUTONOMY-PERM/NVIDIA Agentic Autonomy Levels NVIDIA Agent自治级别 | NVIDIA Agentic Autonomy Levels NVIDIA... | design | design_only |
| D-AUTONOMY-PERM/Non-AI Boundary Guard 非AI边界守卫 | Non-AI Boundary Guard 非AI边界守卫 | design | design_only | D-AUTONOMY-PERM/Non-AI Boundary Guard 非AI边界守卫 | Non-AI Boundary Guard 非AI边界守卫 | design | design_only |
| D-AUTONOMY-PERM/Non-worsening 不恶化性 | Non-worsening 不恶化性 | design | design_only | D-AUTONOMY-PERM/Non-worsening 不恶化性 | Non-worsening 不恶化性 | design | design_only |
| D-AUTONOMY-PERM/Orchestrated Saga Engine 编排式Saga引擎 | Orchestrated Saga Engine 编排式Saga引擎 | design | design_only | D-AUTONOMY-PERM/Orchestrated Saga Engine 编排式Saga引擎 | Orchestrated Saga Engine 编排式Saga引擎 | design | design_only |
| D-AUTONOMY-PERM/PERM Budget Exempt Executor PERM预算豁免执行器 | PERM Budget Exempt Executor PERM预算豁免执行器 | design | design_only | D-AUTONOMY-PERM/PERM Budget Exempt Executor PERM预算豁免执行器 | PERM Budget Exempt Executor PERM预算豁免执行器 | design | design_only |
| D-AUTONOMY-PERM/PERM Independent Health Checker PERM独立健康检查器 | PERM Independent Health Checker PERM独... | design | design_only | D-AUTONOMY-PERM/PERM Independent Health Checker PERM独立健康检查器 | PERM Independent Health Checker PERM独... | design | design_only |
| D-AUTONOMY-PERM/PERM-CORE Read-Only Interface Contract PERM-CORE只读接口契约 | PERM-CORE Read-Only Interface Contrac... | design | design_only | D-AUTONOMY-PERM/PERM-CORE Read-Only Interface Contract PERM-CORE只读接口契约 | PERM-CORE Read-Only Interface Contrac... | design | design_only |
| D-AUTONOMY-PERM/PERMBlockCommand PERM阻止命令 | PERMBlockCommand PERM阻止命令 | design | design_only | D-AUTONOMY-PERM/PERMBlockCommand PERM阻止命令 | PERMBlockCommand PERM阻止命令 | design | design_only |
| D-AUTONOMY-PERM/PERMBlockExecuted PERM阻止指令执行 | PERMBlockExecuted PERM阻止指令执行 | design | design_only | D-AUTONOMY-PERM/PERMBlockExecuted PERM阻止指令执行 | PERMBlockExecuted PERM阻止指令执行 | design | design_only |
| D-AUTONOMY-PERM/PERMBudgetExemption PERM预算豁免 | PERMBudgetExemption PERM预算豁免 | design | design_only | D-AUTONOMY-PERM/PERMBudgetExemption PERM预算豁免 | PERMBudgetExemption PERM预算豁免 | design | design_only |
| D-AUTONOMY-PERM/PERMBudgetExemptionUsed PERM预算豁免被使用 | PERMBudgetExemptionUsed PERM预算豁免被使用 | design | design_only | D-AUTONOMY-PERM/PERMBudgetExemptionUsed PERM预算豁免被使用 | PERMBudgetExemptionUsed PERM预算豁免被使用 | design | design_only |
| D-AUTONOMY-PERM/PERMIndependentHealthCheck PERM独立健康检查 | PERMIndependentHealthCheck PERM独立健康检查 | design | design_only | D-AUTONOMY-PERM/PERMIndependentHealthCheck PERM独立健康检查 | PERMIndependentHealthCheck PERM独立健康检查 | design | design_only |
| D-AUTONOMY-PERM/PERM不修改CORE状态 PERM No Modify CORE State | PERM不修改CORE状态 PERM No Modify CORE State | design | design_only | D-AUTONOMY-PERM/PERM不修改CORE状态 PERM No Modify CORE State | PERM不修改CORE状态 PERM No Modify CORE State | design | design_only |
| D-AUTONOMY-PERM/PERM预算豁免 PERM Budget Exemption | PERM预算豁免 PERM Budget Exemption | design | design_only | D-AUTONOMY-PERM/PERM预算豁免 PERM Budget Exemption | PERM预算豁免 PERM Budget Exemption | design | design_only |
| D-AUTONOMY-PERM/Parameter Optimizer 参数优化器 | Parameter Optimizer 参数优化器 | design | design_only | D-AUTONOMY-PERM/Parameter Optimizer 参数优化器 | Parameter Optimizer 参数优化器 | design | design_only |
| D-AUTONOMY-PERM/PermissionCheck 权限检查 | PermissionCheck 权限检查 | design | design_only | D-AUTONOMY-PERM/PermissionCheck 权限检查 | PermissionCheck 权限检查 | design | design_only |
| D-AUTONOMY-PERM/PermissionDenied 权限拒绝 | PermissionDenied 权限拒绝 | design | design_only | D-AUTONOMY-PERM/PermissionDenied 权限拒绝 | PermissionDenied 权限拒绝 | design | design_only |
| ...MY-PERM/PipelineOrchestrator CostTracker Component PipelineOrchestrator成本追踪组件 | PipelineOrchestrator CostTracker Comp... | design | design_only | ...MY-PERM/PipelineOrchestrator CostTracker Component PipelineOrchestrator成本追踪组件 | PipelineOrchestrator CostTracker Comp... | design | design_only |
| D-AUTONOMY-PERM/RBAC Permission Check Embedded Bridge RBAC权限检查内嵌桥接器 | RBAC Permission Check Embedded Bridge... | design | design_only | D-AUTONOMY-PERM/RBAC Permission Check Embedded Bridge RBAC权限检查内嵌桥接器 | RBAC Permission Check Embedded Bridge... | design | design_only |
| D-AUTONOMY-PERM/RBACDecision RBAC决策 | RBACDecision RBAC决策 | design | design_only | D-AUTONOMY-PERM/RBACDecision RBAC决策 | RBACDecision RBAC决策 | design | design_only |
| D-AUTONOMY-PERM/REDUCE 缩量保留方向 | REDUCE 缩量保留方向 | design | design_only | D-AUTONOMY-PERM/REDUCE 缩量保留方向 | REDUCE 缩量保留方向 | design | design_only |
| D-AUTONOMY-PERM/REJECT 完全阻断 | REJECT 完全阻断 | design | design_only | D-AUTONOMY-PERM/REJECT 完全阻断 | REJECT 完全阻断 | design | design_only |
| D-AUTONOMY-PERM/Red-Blue Validator 红蓝对抗验证器 | Red-Blue Validator 红蓝对抗验证器 | design | design_only | D-AUTONOMY-PERM/Red-Blue Validator 红蓝对抗验证器 | Red-Blue Validator 红蓝对抗验证器 | design | design_only |
| D-AUTONOMY-PERM/Responsible AI Dependency Auditor 负责任AI依赖审计器 | Responsible AI Dependency Auditor 负责任... | design | design_only | D-AUTONOMY-PERM/Responsible AI Dependency Auditor 负责任AI依赖审计器 | Responsible AI Dependency Auditor 负责任... | design | design_only |
| D-AUTONOMY-PERM/Reversibility 可撤销性 | Reversibility 可撤销性 | design | design_only | D-AUTONOMY-PERM/Reversibility 可撤销性 | Reversibility 可撤销性 | design | design_only |
| D-AUTONOMY-PERM/Risk Alert Notification Dispatcher 风控告警通知分发器 | Risk Alert Notification Dispatcher 风控... | design | design_only | D-AUTONOMY-PERM/Risk Alert Notification Dispatcher 风控告警通知分发器 | Risk Alert Notification Dispatcher 风控... | design | design_only |
| D-AUTONOMY-PERM/Risk Check RBAC Permission Controller 风控检查RBAC权限控制器 | Risk Check RBAC Permission Controller... | design | design_only | D-AUTONOMY-PERM/Risk Check RBAC Permission Controller 风控检查RBAC权限控制器 | Risk Check RBAC Permission Controller... | design | design_only |
| D-AUTONOMY-PERM/Role and Interaction Journey 角色与交互旅程 | Role and Interaction Journey 角色与交互旅程 | design | design_only | D-AUTONOMY-PERM/Role and Interaction Journey 角色与交互旅程 | Role and Interaction Journey 角色与交互旅程 | design | design_only |
| D-AUTONOMY-PERM/Rollback Four-Tier Strategy Selector 回滚四级策略选择器 | Rollback Four-Tier Strategy Selector ... | design | design_only | D-AUTONOMY-PERM/Rollback Four-Tier Strategy Selector 回滚四级策略选择器 | Rollback Four-Tier Strategy Selector ... | design | design_only |
| D-AUTONOMY-PERM/Rollback Operation Visual Tracker 回滚操作可视化追踪器 | Rollback Operation Visual Tracker 回滚操... | design | design_only | D-AUTONOMY-PERM/Rollback Operation Visual Tracker 回滚操作可视化追踪器 | Rollback Operation Visual Tracker 回滚操... | design | design_only |
| D-AUTONOMY-PERM/Rollback System 回滚系统 | Rollback System 回滚系统 | design | design_only | D-AUTONOMY-PERM/Rollback System 回滚系统 | Rollback System 回滚系统 | design | design_only |
| D-AUTONOMY-PERM/Saga Deadlock Detector Saga死锁检测器 | Saga Deadlock Detector Saga死锁检测器 | design | design_only | D-AUTONOMY-PERM/Saga Deadlock Detector Saga死锁检测器 | Saga Deadlock Detector Saga死锁检测器 | design | design_only |
| D-AUTONOMY-PERM/Saga Definition Saga定义器 | Saga Definition Saga定义器 | design | design_only | D-AUTONOMY-PERM/Saga Definition Saga定义器 | Saga Definition Saga定义器 | design | design_only |
| D-AUTONOMY-PERM/Saga Observability Tracer Saga可观测性追踪器 | Saga Observability Tracer Saga可观测性追踪器 | design | design_only | D-AUTONOMY-PERM/Saga Observability Tracer Saga可观测性追踪器 | Saga Observability Tracer Saga可观测性追踪器 | design | design_only |
| D-AUTONOMY-PERM/Saga State Tracker Saga状态追踪器 | Saga State Tracker Saga状态追踪器 | design | design_only | D-AUTONOMY-PERM/Saga State Tracker Saga状态追踪器 | Saga State Tracker Saga状态追踪器 | design | design_only |
| D-AUTONOMY-PERM/Saga Version Compatibility Manager Saga版本兼容性管理器 | Saga Version Compatibility Manager Sa... | design | design_only | D-AUTONOMY-PERM/Saga Version Compatibility Manager Saga版本兼容性管理器 | Saga Version Compatibility Manager Sa... | design | design_only |
| D-AUTONOMY-PERM/Saga/Process Manager Dependency Orchestrator Saga/流程管理器依赖编排器 | Saga/Process Manager Dependency Orche... | design | design_only | D-AUTONOMY-PERM/Saga/Process Manager Dependency Orchestrator Saga/流程管理器依赖编排器 | Saga/Process Manager Dependency Orche... | design | design_only |
| D-AUTONOMY-PERM/Soft Block 软阻断 | Soft Block 软阻断 | design | design_only | D-AUTONOMY-PERM/Soft Block 软阻断 | Soft Block 软阻断 | design | design_only |
| D-AUTONOMY-PERM/System Health Five-Star Scorer 系统健康度五星评分器 | System Health Five-Star Scorer 系统健康度五... | design | design_only | D-AUTONOMY-PERM/System Health Five-Star Scorer 系统健康度五星评分器 | System Health Five-Star Scorer 系统健康度五... | design | design_only |
| D-AUTONOMY-PERM/System Version Upgrade Path Manager 系统版本升级路径管理器 | System Version Upgrade Path Manager 系... | design | design_only | D-AUTONOMY-PERM/System Version Upgrade Path Manager 系统版本升级路径管理器 | System Version Upgrade Path Manager 系... | design | design_only |
| D-AUTONOMY-PERM/Szpruch Conditional Gate Szpruch条件门禁 | Szpruch Conditional Gate Szpruch条件门禁 | design | design_only | D-AUTONOMY-PERM/Szpruch Conditional Gate Szpruch条件门禁 | Szpruch Conditional Gate Szpruch条件门禁 | design | design_only |
| D-AUTONOMY-PERM/TNR Safety Specification TNR安全规范 | TNR Safety Specification TNR安全规范 | design | design_only | D-AUTONOMY-PERM/TNR Safety Specification TNR安全规范 | TNR Safety Specification TNR安全规范 | design | design_only |
| D-AUTONOMY-PERM/TaskCard Six-Dimension Anti-Drift Validator TaskCard六维防漂移校验器 | TaskCard Six-Dimension Anti-Drift Val... | design | design_only | D-AUTONOMY-PERM/TaskCard Six-Dimension Anti-Drift Validator TaskCard六维防漂移校验器 | TaskCard Six-Dimension Anti-Drift Val... | design | design_only |
| D-AUTONOMY-PERM/Temporal GNN Dependency Drift Predictor 时序GNN依赖漂移预测器 | Temporal GNN Dependency Drift Predict... | design | design_only | D-AUTONOMY-PERM/Temporal GNN Dependency Drift Predictor 时序GNN依赖漂移预测器 | Temporal GNN Dependency Drift Predict... | design | design_only |
| D-AUTONOMY-PERM/Token Budget Coordinator Token预算协调器 | Token Budget Coordinator Token预算协调器 | design | design_only | D-AUTONOMY-PERM/Token Budget Coordinator Token预算协调器 | Token Budget Coordinator Token预算协调器 | design | design_only |
| D-AUTONOMY-PERM/Token Budget Manager Token预算管理器 | Token Budget Manager Token预算管理器 | design | design_only | D-AUTONOMY-PERM/Token Budget Manager Token预算管理器 | Token Budget Manager Token预算管理器 | design | design_only |
| D-AUTONOMY-PERM/Trading Session Aware Ops Scheduler 交易时段感知运维调度器 | Trading Session Aware Ops Scheduler 交... | design | design_only | D-AUTONOMY-PERM/Trading Session Aware Ops Scheduler 交易时段感知运维调度器 | Trading Session Aware Ops Scheduler 交... | design | design_only |
| D-AUTONOMY-PERM/TradingSessionSchedule 交易时段调度 | TradingSessionSchedule 交易时段调度 | design | design_only | D-AUTONOMY-PERM/TradingSessionSchedule 交易时段调度 | TradingSessionSchedule 交易时段调度 | design | design_only |
| D-AUTONOMY-PERM/TradingSessionSwitch 交易时段切换 | TradingSessionSwitch 交易时段切换 | design | design_only | D-AUTONOMY-PERM/TradingSessionSwitch 交易时段切换 | TradingSessionSwitch 交易时段切换 | design | design_only |
| D-AUTONOMY-PERM/Transactionality 事务性 | Transactionality 事务性 | design | design_only | D-AUTONOMY-PERM/Transactionality 事务性 | Transactionality 事务性 | design | design_only |
| D-AUTONOMY-PERM/Vector Index Health Monitor 向量索引健康监控器 | Vector Index Health Monitor 向量索引健康监控器 | design | design_only | D-AUTONOMY-PERM/Vector Index Health Monitor 向量索引健康监控器 | Vector Index Health Monitor 向量索引健康监控器 | design | design_only |
| D-AUTONOMY-PERM/Zone Crossing Boundary Validator Zone Crossing边界校验器 | Zone Crossing Boundary Validator Zone... | design | design_only | D-AUTONOMY-PERM/Zone Crossing Boundary Validator Zone Crossing边界校验器 | Zone Crossing Boundary Validator Zone... | design | design_only |
| D-AUTONOMY-PERM/agent_creation_policy.py Agent创建策略 | agent_creation_policy.py Agent创建策略 | design | design_only | D-AUTONOMY-PERM/agent_creation_policy.py Agent创建策略 | agent_creation_policy.py Agent创建策略 | design | design_only |
| D-AUTONOMY-PERM/ai_modifiable 自治区 | ai_modifiable 自治区 | design | design_only | D-AUTONOMY-PERM/ai_modifiable 自治区 | ai_modifiable 自治区 | design | design_only |
| D-AUTONOMY-PERM/anomaly_detector.py 异常检测器 | anomaly_detector.py 异常检测器 | design | design_only | D-AUTONOMY-PERM/anomaly_detector.py 异常检测器 | anomaly_detector.py 异常检测器 | design | design_only |
| D-AUTONOMY-PERM/anti_pattern_guard.py 反模式守卫 | anti_pattern_guard.py 反模式守卫 | design | design_only | D-AUTONOMY-PERM/anti_pattern_guard.py 反模式守卫 | anti_pattern_guard.py 反模式守卫 | design | design_only |
| D-AUTONOMY-PERM/asymmetric_audit.py 非对称审计 | asymmetric_audit.py 非对称审计 | design | design_only | D-AUTONOMY-PERM/asymmetric_audit.py 非对称审计 | asymmetric_audit.py 非对称审计 | design | design_only |
| D-AUTONOMY-PERM/auto_maintenance.py 自动维护 | auto_maintenance.py 自动维护 | design | design_only | D-AUTONOMY-PERM/auto_maintenance.py 自动维护 | auto_maintenance.py 自动维护 | design | design_only |
| D-AUTONOMY-PERM/bootstrap_verifier.py 引导验证器 | bootstrap_verifier.py 引导验证器 | design | design_only | D-AUTONOMY-PERM/bootstrap_verifier.py 引导验证器 | bootstrap_verifier.py 引导验证器 | design | design_only |
| D-AUTONOMY-PERM/build_sanitizer.py 构建清洗器 | build_sanitizer.py 构建清洗器 | design | design_only | D-AUTONOMY-PERM/build_sanitizer.py 构建清洗器 | build_sanitizer.py 构建清洗器 | design | design_only |
| D-AUTONOMY-PERM/cache_invalidation.py 缓存失效器 | cache_invalidation.py 缓存失效器 | design | design_only | D-AUTONOMY-PERM/cache_invalidation.py 缓存失效器 | cache_invalidation.py 缓存失效器 | design | design_only |
| D-AUTONOMY-PERM/contract_verifier.py 契约验证器 | contract_verifier.py 契约验证器 | design | design_only | D-AUTONOMY-PERM/contract_verifier.py 契约验证器 | contract_verifier.py 契约验证器 | design | design_only |
| D-AUTONOMY-PERM/cross_cutting.py 横切关注点 | cross_cutting.py 横切关注点 | design | design_only | D-AUTONOMY-PERM/cross_cutting.py 横切关注点 | cross_cutting.py 横切关注点 | design | design_only |
| D-AUTONOMY-PERM/dependency_auditor.py 依赖审计器 | dependency_auditor.py 依赖审计器 | design | design_only | D-AUTONOMY-PERM/dependency_auditor.py 依赖审计器 | dependency_auditor.py 依赖审计器 | design | design_only |
| D-AUTONOMY-PERM/environment_manager.py 环境管理器 | environment_manager.py 环境管理器 | design | design_only | D-AUTONOMY-PERM/environment_manager.py 环境管理器 | environment_manager.py 环境管理器 | design | design_only |
| D-AUTONOMY-PERM/exceptions.py 异常定义 | exceptions.py 异常定义 | design | design_only | D-AUTONOMY-PERM/exceptions.py 异常定义 | exceptions.py 异常定义 | design | design_only |
| D-AUTONOMY-PERM/genesis_bootstrap.py 创世引导 | genesis_bootstrap.py 创世引导 | design | design_only | D-AUTONOMY-PERM/genesis_bootstrap.py 创世引导 | genesis_bootstrap.py 创世引导 | design | design_only |
| D-AUTONOMY-PERM/human_gated 门控区 | human_gated 门控区 | design | design_only | D-AUTONOMY-PERM/human_gated 门控区 | human_gated 门控区 | design | design_only |
| D-AUTONOMY-PERM/immutable 禁区 | immutable 禁区 | design | design_only | D-AUTONOMY-PERM/immutable 禁区 | immutable 禁区 | design | design_only |
| D-AUTONOMY-PERM/串谋/策略同质化 Collusion/Strategy Homogeneity | 串谋/策略同质化 Collusion/Strategy Homogeneity | design | design_only | D-AUTONOMY-PERM/串谋/策略同质化 Collusion/Strategy Homogeneity | 串谋/策略同质化 Collusion/Strategy Homogeneity | design | design_only |
| D-AUTONOMY-PERM/交易时段仅监控 Trading Session Monitor Only | 交易时段仅监控 Trading Session Monitor Only | design | design_only | D-AUTONOMY-PERM/交易时段仅监控 Trading Session Monitor Only | 交易时段仅监控 Trading Session Monitor Only | design | design_only |
| D-AUTONOMY-PERM/决策一致性 Decision Consistency | 决策一致性 Decision Consistency | design | design_only | D-AUTONOMY-PERM/决策一致性 Decision Consistency | 决策一致性 Decision Consistency | design | design_only |
| D-AUTONOMY-PERM/权限边界偏离 Permission Boundary Deviation | 权限边界偏离 Permission Boundary Deviation | design | design_only | D-AUTONOMY-PERM/权限边界偏离 Permission Boundary Deviation | 权限边界偏离 Permission Boundary Deviation | design | design_only |
| D-AUTONOMY-PERM/涌现行为 Emergent Behavior | 涌现行为 Emergent Behavior | design | design_only | D-AUTONOMY-PERM/涌现行为 Emergent Behavior | 涌现行为 Emergent Behavior | design | design_only |
| D-AUTONOMY-PERM/禁止AI自动升级交易时段依赖库 | 禁止AI自动升级交易时段依赖库 | design | design_only | D-AUTONOMY-PERM/禁止AI自动升级交易时段依赖库 | 禁止AI自动升级交易时段依赖库 | design | design_only |
| D-AUTONOMY-PERM/禁止AI自动清理未归档交易日志和审计记录 | 禁止AI自动清理未归档交易日志和审计记录 | design | design_only | D-AUTONOMY-PERM/禁止AI自动清理未归档交易日志和审计记录 | 禁止AI自动清理未归档交易日志和审计记录 | design | design_only |
| D-AUTONOMY-PERM/禁止AI自动订阅付费数据源 | 禁止AI自动订阅付费数据源 | design | design_only | D-AUTONOMY-PERM/禁止AI自动订阅付费数据源 | 禁止AI自动订阅付费数据源 | design | design_only |
| D-AUTONOMY-PERM/禁止AI自动重启交易时段核心进程 | 禁止AI自动重启交易时段核心进程 | design | design_only | D-AUTONOMY-PERM/禁止AI自动重启交易时段核心进程 | 禁止AI自动重启交易时段核心进程 | design | design_only |
| D-AUTONOMY-PERM/资源消耗异常 Resource Consumption Anomaly | 资源消耗异常 Resource Consumption Anomaly | design | design_only | D-AUTONOMY-PERM/资源消耗异常 Resource Consumption Anomaly | 资源消耗异常 Resource Consumption Anomaly | design | design_only |
| D-AUTONOMY-PERM/通信异常 Communication Anomaly | 通信异常 Communication Anomaly | design | design_only | D-AUTONOMY-PERM/通信异常 Communication Anomaly | 通信异常 Communication Anomaly | design | design_only |
| D-AUTONOMY-PERM/隐性串谋 Implicit Collusion | 隐性串谋 Implicit Collusion | design | design_only | D-AUTONOMY-PERM/隐性串谋 Implicit Collusion | 隐性串谋 Implicit Collusion | design | design_only |
| D-GOVERNANCE/Agent RBAC Approver Check Agent RBAC审批人检查 | Agent RBAC Approver Check Agent RBAC审... | design | design_only | D-GOVERNANCE/Agent RBAC Approver Check Agent RBAC审批人检查 | Agent RBAC Approver Check Agent RBAC审... | design | design_only |
| D-GOVERNANCE/Agent RBAC Governance Bridges Contracts Agent RBAC治理桥契约 | Agent RBAC Governance Bridges Contrac... | design | design_only | D-GOVERNANCE/Agent RBAC Governance Bridges Contracts Agent RBAC治理桥契约 | Agent RBAC Governance Bridges Contrac... | design | design_only |
| D-GOVERNANCE/Kill Switch (Governance Layer) 治理层Kill Switch | Kill Switch (Governance Layer) 治理层Kil... | design | design_only | D-GOVERNANCE/Kill Switch (Governance Layer) 治理层Kill Switch | Kill Switch (Governance Layer) 治理层Kil... | design | design_only |
| D-GOVERNANCE/Kill Switch Layered Kill Switch分层 | Kill Switch Layered Kill Switch分层 | design | design_only | D-GOVERNANCE/Kill Switch Layered Kill Switch分层 | Kill Switch Layered Kill Switch分层 | design | design_only |
| config/runtime/kill_switch_state.yaml |  | production | orphan | config/runtime/kill_switch_state.yaml |  | production | orphan |
| docs/03_modules/_domain_autonomy_core/agent_rbac/adversarial_test_report.yaml |  | production | orphan | docs/03_modules/_domain_autonomy_core/agent_rbac/adversarial_test_report.yaml |  | production | orphan |
| docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | docs__03_modules___domain_autonomy_co... | design | design_only | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | docs__03_modules___domain_autonomy_co... | design | design_only |
| scripts/arch_guard/fitness_functions/check_kill_switch_latency.py |  | prototype | draft | scripts/arch_guard/fitness_functions/check_kill_switch_latency.py |  | prototype | draft |
| scripts/governance/meta/kill_switch_state.yaml |  | production | orphan | scripts/governance/meta/kill_switch_state.yaml |  | production | orphan |
| scripts/governance/meta/manage_kill_switch.py |  | prototype | draft | scripts/governance/meta/manage_kill_switch.py |  | prototype | draft |
| src/zephyr/autonomy_perm/__init__.py |  | prototype | orphan | src/zephyr/autonomy_perm/__init__.py |  | prototype | orphan |
| src/zephyr/autonomy_perm/_extensions/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/autonomy_perm/_extensions/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/autonomy_perm/api/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/autonomy_perm/api/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/autonomy_perm/core/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/autonomy_perm/core/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/autonomy_perm/infrastructure/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/autonomy_perm/infrastructure/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/autonomy_perm/models/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/autonomy_perm/models/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/autonomy_perm/red_blue_validator/__init__.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/__init__.py |  | prototype | draft |
| src/zephyr/autonomy_perm/red_blue_validator/attack_registry.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/attack_registry.py |  | prototype | draft |
| src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder.py |  | prototype | draft |
| src/zephyr/autonomy_perm/red_blue_validator/constitution_guard.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/constitution_guard.py |  | prototype | draft |
| src/zephyr/autonomy_perm/red_blue_validator/convergence_checker.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/convergence_checker.py |  | prototype | draft |
| src/zephyr/autonomy_perm/red_blue_validator/defense_runner.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/defense_runner.py |  | prototype | draft |
| src/zephyr/autonomy_perm/red_blue_validator/game_day_runner.py |  | prototype | draft | src/zephyr/autonomy_perm/red_blue_validator/game_day_runner.py |  | prototype | draft |
| src/zephyr/autonomy_perm/services/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/autonomy_perm/services/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/governance/agent_signer.py |  | prototype | draft | src/zephyr/governance/agent_signer.py |  | prototype | draft |
| src/zephyr/security/access_control/governance_bridges/__init__.py |  | prototype | production | src/zephyr/security/access_control/governance_bridges/__init__.py |  | prototype | production |

> (仅显示前 200 个模块，共 270 个)

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
    subgraph D_AUTONOMY_PERM["D-AUTONOMY_PERM 自治保护"]
        D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI["AI Autonomy Boundary Not Self-Extendable AI自治边界... design"]
        D_AUTONOMY_PERM_AI_Comprehension_Cost_Dynamic_Estimator_AI["AI Comprehension Cost Dynamic Estimator AI理解成本动... design"]
        D_AUTONOMY_PERM_AI_Governance_Framework_Compliance_Assessor_AI["AI Governance Framework Compliance Assessor AI治... design"]
        D_AUTONOMY_PERM_AI_Risk_Assessor_AI["AI Risk Assessor AI风险评估器 design"]
        D_AUTONOMY_PERM_AI_Risk_Classifier_AI["AI Risk Classifier AI风险分类器 design"]
        D_AUTONOMY_PERM_AI_Risk_Dependency_Mapper_AI["AI Risk Dependency Mapper AI风险依赖映射器 design"]
        D_AUTONOMY_PERM_AI_Driven_Saga_Orchestrator_AI_Saga["AI-Driven Saga Orchestrator AI驱动Saga编排器 design"]
        D_AUTONOMY_PERM_APPROVE["APPROVE 通过 design"]
        D_AUTONOMY_PERM_ARS_Dual_Track_Settlement_ARS["ARS Dual-Track Settlement ARS双轨结算模型 design"]
        D_AUTONOMY_PERM_AWS_Agentic_AI_Security_Scoping_Matrix_AWS_Agent_AI["AWS Agentic AI Security Scoping Matrix AWS Agen... design"]
        D_AUTONOMY_PERM_Agent_Cannot_Auto_Execute_Large_Order_Agent["Agent Cannot Auto-Execute Large Order Agent不可自动... design"]
        D_AUTONOMY_PERM_Agent_Cannot_Auto_Online_Strategy_Agent["Agent Cannot Auto-Online Strategy Agent不可自动上线新策略 design"]
        D_AUTONOMY_PERM_Agent_Cannot_Autonomously_Modify_Boundary_Agent["Agent Cannot Autonomously Modify Boundary Agent... design"]
        D_AUTONOMY_PERM_Audit_Trail["Audit Trail 审计链 design"]
        D_AUTONOMY_PERM_Audit_Persistence_Dual_Write_Coordinator["Audit-Persistence Dual-Write Coordinator 审计-持久化... design"]
        D_AUTONOMY_PERM_AuditLogWrite["AuditLogWrite 审计日志写入 design"]
        D_AUTONOMY_PERM_AuditRecord["AuditRecord 审计记录 design"]
        D_AUTONOMY_PERM_Auto_Fix_Engine["Auto Fix Engine 自动修复引擎 design"]
        D_AUTONOMY_PERM_Auto_Guard_Async_Approval_Manager_Auto_Guard["Auto-Guard Async Approval Manager Auto-Guard异步审... design"]
        D_AUTONOMY_PERM_Autonomy_Boundary_Change_Process["Autonomy Boundary Change Process 自治边界变更流程 design"]
        D_AUTONOMY_PERM_Autonomy_Fuse["Autonomy Fuse 自治熔断器 design"]
        D_AUTONOMY_PERM_Backtest_Live_Deviation_Monitor["Backtest-Live Deviation Monitor 回测-实盘偏差监控器 design"]
        D_AUTONOMY_PERM_BacktestRealtimeDeviation["BacktestRealtimeDeviation 回测-实盘偏差 design"]
        D_AUTONOMY_PERM_BacktestRealtimeDeviationAlert["BacktestRealtimeDeviationAlert 回测实盘偏差告警 design"]
        D_AUTONOMY_PERM_BlockCommand["BlockCommand 阻止指令 design"]
        D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer["Budget Enforcer On-Demand Activator Budget Enfo... design"]
        D_AUTONOMY_PERM_BudgetExemption["BudgetExemption 预算豁免 design"]
        D_AUTONOMY_PERM_Choreography_Saga_Engine_Saga["Choreography Saga Engine 协调式Saga引擎 design"]
        D_AUTONOMY_PERM_Circuit_Breaker_State_Machine["Circuit Breaker State Machine 熔断器状态机 design"]
        D_AUTONOMY_PERM_Cluster_Behavior_Risk_Protection["Cluster Behavior Risk Protection 群集行为风险防护 design"]
    end
    D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI -.->|config_depends| D_AUTONOMY_PERM_AI_Driven_Saga_Orchestrator_AI_Saga
    D_AUTONOMY_PERM_Auto_Fix_Engine -.->|config_depends| D_AUTONOMY_PERM_Agent_Cannot_Auto_Online_Strategy_Agent
    D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer -.->|import_depends| D_AUTONOMY_PERM_AI_Comprehension_Cost_Dynamic_Estimator_AI
    D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer -.->|contract| D_AUTONOMY_PERM_BacktestRealtimeDeviation
    D_AUTONOMY_PERM_AI_Risk_Assessor_AI -.->|import_depends| D_AUTONOMY_PERM_AI_Risk_Dependency_Mapper_AI
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_AUTONOMY_PERM_Autonomy_Fuse -.->|data| D_INTELLIGENCE
    D_TRADING["D-TRADING design"]
    D_AUTONOMY_PERM_Autonomy_Fuse -.->|contract| D_TRADING
    D_ML_TRAIN["D-ML_TRAIN design"]
    D_AUTONOMY_PERM_Audit_Trail -.->|config_depends| D_ML_TRAIN
    D_SECURITY["D-SECURITY design"]
    D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI -.->|data| D_SECURITY
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI -.->|data| D_INFRA_RUNTIME
    D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI -.->|config_depends| D_TRADING
    D_MKT_DATA["D-MKT_DATA design"]
    D_AUTONOMY_PERM_AuditLogWrite -.->|data| D_MKT_DATA
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_AUTONOMY_PERM_AuditLogWrite -.->|contract| D_KNOWLEDGE
    D_PF_CORE["D-PF_CORE design"]
    D_AUTONOMY_PERM_Auto_Fix_Engine -.->|contract| D_PF_CORE
    D_RISK["D-RISK design"]
    D_AUTONOMY_PERM_Auto_Guard_Async_Approval_Manager_Auto_Guard -.->|contract| D_RISK
    D_AUTONOMY_PERM_Audit_Persistence_Dual_Write_Coordinator -.->|event| D_RISK
    D_INTEGRATION["D-INTEGRATION design"]
    D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer -.->|contract| D_INTEGRATION
    D_AUTONOMY_PERM_AI_Comprehension_Cost_Dynamic_Estimator_AI -.->|contract| D_RISK
    D_AUTONOMY_PERM_AI_Governance_Framework_Compliance_Assessor_AI -.->|data| D_RISK
    D_EX_SOR["D-EX_SOR design"]
    D_AUTONOMY_PERM_Choreography_Saga_Engine_Saga -.->|data| D_EX_SOR
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|data| D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|event| D_AUTONOMY_PERM_AuditLogWrite
    D_COMPLIANCE -.->|contract| D_AUTONOMY_PERM_AuditLogWrite
    D_COMPLIANCE -.->|contract| D_AUTONOMY_PERM_Auto_Fix_Engine
    D_AUTONOMY_CORE -.->|data| D_AUTONOMY_PERM_Auto_Guard_Async_Approval_Manager_Auto_Guard
    D_AUTONOMY_CORE -.->|data| D_AUTONOMY_PERM_Audit_Persistence_Dual_Write_Coordinator
    D_COMPLIANCE -.->|data| D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer
    D_AUTONOMY_CORE -.->|data| D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer
    D_COMPLIANCE -.->|config_depends| D_AUTONOMY_PERM_AI_Comprehension_Cost_Dynamic_Estimator_AI
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_GOVERNANCE -.->|contract| D_AUTONOMY_PERM_AI_Governance_Framework_Compliance_Assessor_AI
    D_CROSS_ASSET["D-CROSS_ASSET design"]
    D_CROSS_ASSET -.->|contract| D_AUTONOMY_PERM_AI_Governance_Framework_Compliance_Assessor_AI
    D_ALT_DATA["D-ALT_DATA design"]
    D_ALT_DATA -.->|data| D_AUTONOMY_PERM_AI_Governance_Framework_Compliance_Assessor_AI
    D_DATA_GOV["D-DATA_GOV design"]
    D_DATA_GOV -.->|contract| D_AUTONOMY_PERM_Choreography_Saga_Engine_Saga
    D_AUTONOMY_CORE -.->|data| D_AUTONOMY_PERM_Choreography_Saga_Engine_Saga
    D_SIMULATION["D-SIMULATION design"]
    D_SIMULATION -.->|config_depends| D_AUTONOMY_PERM_AI_Risk_Dependency_Mapper_AI
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_AUTONOMY_PERM_AI_Autonomy_Boundary_Not_Self_Extendable_AI_AI,D_AUTONOMY_PERM_AI_Comprehension_Cost_Dynamic_Estimator_AI,D_AUTONOMY_PERM_AI_Governance_Framework_Compliance_Assessor_AI,D_AUTONOMY_PERM_AI_Risk_Assessor_AI,D_AUTONOMY_PERM_AI_Risk_Classifier_AI,D_AUTONOMY_PERM_AI_Risk_Dependency_Mapper_AI,D_AUTONOMY_PERM_AI_Driven_Saga_Orchestrator_AI_Saga,D_AUTONOMY_PERM_APPROVE,D_AUTONOMY_PERM_ARS_Dual_Track_Settlement_ARS,D_AUTONOMY_PERM_AWS_Agentic_AI_Security_Scoping_Matrix_AWS_Agent_AI,D_AUTONOMY_PERM_Agent_Cannot_Auto_Execute_Large_Order_Agent,D_AUTONOMY_PERM_Agent_Cannot_Auto_Online_Strategy_Agent,D_AUTONOMY_PERM_Agent_Cannot_Autonomously_Modify_Boundary_Agent,D_AUTONOMY_PERM_Audit_Trail,D_AUTONOMY_PERM_Audit_Persistence_Dual_Write_Coordinator,D_AUTONOMY_PERM_AuditLogWrite,D_AUTONOMY_PERM_AuditRecord,D_AUTONOMY_PERM_Auto_Fix_Engine,D_AUTONOMY_PERM_Auto_Guard_Async_Approval_Manager_Auto_Guard,D_AUTONOMY_PERM_Autonomy_Boundary_Change_Process,D_AUTONOMY_PERM_Autonomy_Fuse,D_AUTONOMY_PERM_Backtest_Live_Deviation_Monitor,D_AUTONOMY_PERM_BacktestRealtimeDeviation,D_AUTONOMY_PERM_BacktestRealtimeDeviationAlert,D_AUTONOMY_PERM_BlockCommand,D_AUTONOMY_PERM_Budget_Enforcer_On_Demand_Activator_Budget_Enforcer,D_AUTONOMY_PERM_BudgetExemption,D_AUTONOMY_PERM_Choreography_Saga_Engine_Saga,D_AUTONOMY_PERM_Circuit_Breaker_State_Machine,D_AUTONOMY_PERM_Cluster_Behavior_Risk_Protection design
    class D_INTELLIGENCE,D_TRADING,D_ML_TRAIN,D_SECURITY,D_INFRA_RUNTIME,D_MKT_DATA,D_KNOWLEDGE,D_PF_CORE,D_RISK,D_INTEGRATION,D_EX_SOR,D_AUTONOMY_CORE,D_COMPLIANCE,D_GOVERNANCE,D_CROSS_ASSET,D_ALT_DATA,D_DATA_GOV,D_SIMULATION external_design
```

> (依赖图最多显示前 30 个节点，共 270 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-SECURITY | 171 | contract,import_depends,test_depends,domain_dependency,event,data,config_depends | D-SECURITY | 171 | contract,import_depends,test_depends,domain_dependency,event,data,config_depends |
| D-RISK | 48 | contract,config_depends,data,event | D-RISK | 48 | contract,config_depends,data,event |
| D-SIGNAL | 15 | event,data,config_depends,contract | D-SIGNAL | 15 | event,data,config_depends,contract |
| D-MKT_DATA | 15 | contract,data,event,config_depends | D-MKT_DATA | 15 | contract,data,event,config_depends |
| D-INTEGRATION | 13 | test_depends,contract,data,event,config_depends | D-INTEGRATION | 13 | test_depends,contract,data,event,config_depends |
| D-INTELLIGENCE | 10 | data,config_depends,contract | D-INTELLIGENCE | 10 | data,config_depends,contract |
| D-INFRA_RUNTIME | 10 | test_depends,event,data,config_depends,contract | D-INFRA_RUNTIME | 10 | test_depends,event,data,config_depends,contract |
| D-FACTOR | 10 | data,event,contract,config_depends | D-FACTOR | 10 | data,event,contract,config_depends |
| D-GOVERNANCE | 8 | config_depends,test_depends,import_depends | D-GOVERNANCE | 8 | config_depends,test_depends,import_depends |
| D-EX_SOR | 8 | config_depends,event,data,contract | D-EX_SOR | 8 | config_depends,event,data,contract |
| D-KNOWLEDGE | 7 | contract,data,event,config_depends | D-KNOWLEDGE | 7 | contract,data,event,config_depends |
| D-DATA_ENG | 6 | contract,data,event | D-DATA_ENG | 6 | contract,data,event |
| D-EX_CORE | 4 | event,contract | D-EX_CORE | 4 | event,contract |
| D-POSITION | 3 | data | D-POSITION | 3 | data |
| D-PF_CORE | 3 | contract,data | D-PF_CORE | 3 | contract,data |
| D-ML_TRAIN | 3 | data,config_depends,event | D-ML_TRAIN | 3 | data,config_depends,event |
| D-TRADING | 2 | contract,config_depends | D-TRADING | 2 | contract,config_depends |
| D-ML_SERVE | 1 | data | D-ML_SERVE | 1 | data |
| D-GOV_AUDIT | 1 | test_depends | D-GOV_AUDIT | 1 | test_depends |
| D-AUTONOMY_CORE | 1 | test_depends | D-AUTONOMY_CORE | 1 | test_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-COMPLIANCE | 47 | event,data,contract,config_depends | D-COMPLIANCE | 47 | event,data,contract,config_depends |
| D-GOVERNANCE | 33 | runtime,contract,import_depends,config_depends,event,data | D-GOVERNANCE | 33 | runtime,contract,import_depends,config_depends,event,data |
| D-AUTONOMY_CORE | 32 | config_depends,domain_dependency,contract,data,event | D-AUTONOMY_CORE | 32 | config_depends,domain_dependency,contract,data,event |
| D-OPS | 14 | config_depends,data,contract,event | D-OPS | 14 | config_depends,data,contract,event |
| D-INFRA_OPS | 12 | data,contract,event,config_depends | D-INFRA_OPS | 12 | data,contract,event,config_depends |
| D-FRONTEND | 10 | data,contract,event | D-FRONTEND | 10 | data,contract,event |
| D-SIMULATION | 7 | config_depends,data,contract | D-SIMULATION | 7 | config_depends,data,contract |
| D-PF_ALLOC | 5 | event,contract,data | D-PF_ALLOC | 5 | event,contract,data |
| D-REPORTING | 4 | data,contract,event,config_depends | D-REPORTING | 4 | data,contract,event,config_depends |
| D-CROSS_ASSET | 3 | contract,data,event | D-CROSS_ASSET | 3 | contract,data,event |
| D-SELL_DECISION | 2 | config_depends,data | D-SELL_DECISION | 2 | config_depends,data |
| D-GOV_DRIFT | 1 | runtime | D-GOV_DRIFT | 1 | runtime |
| D-GOV_AUDIT | 1 | event | D-GOV_AUDIT | 1 | event |
| D-DATA_SEC | 1 | contract | D-DATA_SEC | 1 | contract |
| D-DATA_GOV | 1 | contract | D-DATA_GOV | 1 | contract |
| D-ALT_DATA | 1 | data | D-ALT_DATA | 1 | data |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
