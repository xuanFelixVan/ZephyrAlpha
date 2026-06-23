---
doc_type: domain_architecture_doc
title: D-AUTONOMY_PERM 自治保护架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-AUTONOMY_PERM 自治保护架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-AUTONOMY_PERM |
| 域名称 | 自治保护 |
| 架构层 | L2_domain |
| 模块总数 | 206 |
| 设计态模块 | 192 |
| 原型态模块 | 8 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 自治保护域。负责自治系统的安全边界保护，包括权限守卫、升级引擎、预算执行器、回滚系统。 |

## 模块清单

共 206 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-AUTONOMY-PERM/AI Autonomy Boundary Not Self-Extendable AI自治边界不可被AI自行扩展 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AI Comprehension Cost Dynamic Estimator AI理解成本动态估算器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AI Governance Framework Compliance Assessor AI治理框架合规性评估器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AI Risk Assessor AI风险评估器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AI Risk Classifier AI风险分类器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AI Risk Dependency Mapper AI风险依赖映射器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AI-Driven Saga Orchestrator AI驱动Saga编排器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/APPROVE 通过 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/ARS Dual-Track Settlement ARS双轨结算模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AWS Agentic AI Security Scoping Matrix AWS Agent AI安全范围矩阵 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Agent Cannot Auto-Execute Large Order Agent不可自动执行大额下单 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Agent Cannot Auto-Online Strategy Agent不可自动上线新策略 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Agent Cannot Autonomously Modify Boundary Agent不可自主修改自治边界 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Audit Trail 审计链 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Audit-Persistence Dual-Write Coordinator 审计-持久化双写协调器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AuditLogWrite 审计日志写入 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/AuditRecord 审计记录 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Auto Fix Engine 自动修复引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Auto-Guard Async Approval Manager Auto-Guard异步审批管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Autonomy Boundary Change Process 自治边界变更流程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Autonomy Fuse 自治熔断器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Backtest-Live Deviation Monitor 回测-实盘偏差监控器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/BacktestRealtimeDeviation 回测-实盘偏差 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/BacktestRealtimeDeviationAlert 回测实盘偏差告警 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/BlockCommand 阻止指令 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Budget Enforcer On-Demand Activator Budget Enforcer按需激活器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/BudgetExemption 预算豁免 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Choreography Saga Engine 协调式Saga引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Circuit Breaker State Machine 熔断器状态机 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Cluster Behavior Risk Protection 群集行为风险防护 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Code Health Assessor 代码健康度评估器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Compensation Action Manager 补偿动作管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Compensation Dependency Graph Analyzer 补偿依赖图分析器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Core Chain E2E Health Monitor 核心链路端到端健康监控器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/CoreReadOnlyState CORE只读状态 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Cross-Saga Transaction Coordinator 跨Saga事务协调器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/D-AUT-PERM |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/D-AUTONOMY-PERM |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Dependency Upgrade Sandbox Approval Gateway 依赖升级沙箱审批网关 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/DependencyUpgradeApproval 依赖升级审批 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/DependencyUpgradeCompleted 依赖库升级完成 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Drift Detector Statistical Drift Checker Drift Detector统计漂移检测器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Drift Guard 漂移守卫 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/DriftDetected 漂移检测 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Dual-Storage Rollback Coordinator 双存储回滚协调器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Enhanced Confidence Cascade Mapper 增强置信度级联映射器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Escalation Protocol 升级协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/FLATTEN 紧急平仓 |  | design_only | design | 0 | 0 |
| ...TONOMY-PERM/Feedback Loop Three-Layer Escalation Trigger Feedback Loop三层升级触发器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Four-Level Autonomy Boundary Agent自治边界分四级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Four-Level Autonomy Model 四级自治模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Governance Dashboard 治理仪表盘 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Governance Phase Check Slimmer Governance Phase Check精简器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Governance Policy Engine 治理策略引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/HITL Confidence Upgrade HITL置信度升级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/HITL Human-in-the-Loop 人在闭环机制 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/HITL Mechanism HITL人在闭环机制 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Half-Open Probe 熔断器半开试探 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Hard Block 硬阻断 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Hard Reset Permission Gate Hard Reset权限门控 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Hard-Gate 硬门禁架构 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Health Check Service 健康检查服务 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/HealthReport 健康报告 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Immutable Audit Log Writer 不可变审计日志写入器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/KILLSWITCH.md AI Agent Emergency Stop Protocol AI Agent紧急停止协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Kill Switch Controlled Reentry Kill Switch激活后必须受控重入 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Kill Switch Direct Path Kill Switch直通路径 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Kill Switch Layered & Local Evaluated Kill Switch必须分层且本地评估 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Kill Switch 紧急制动开关 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/KillSwitchDirect Kill Switch直通 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/KillSwitchDirectActivated Kill Switch直通激活 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/KillSwitch直通路径 KillSwitch Direct Path |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Knowledge Snapshot Rollback Manager 知识快照回滚管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Knowledge Write Guard Protector 知识Write Guard保护器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/LLM Cost Guard LLM成本守卫 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Large Order Requires Approval 大额下单需人工审批 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Learning System Kill Switch 学习系统Kill Switch |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Level 0-3 Autonomy Levels 0-3自治级别 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Local Model 本地推理模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/M10 Audit Report Finding Format Generator M10审计报告Finding格式生成器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/MCP Gateway Rate-Limit Audit Manager MCP网关限流审计管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Drift Dependency Propagator 模型漂移依赖传播器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Drift Detector 模型漂移检测器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Inventory Dependency Graph Builder 模型清单依赖图构建器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Monitoring Dependency Tracker 模型监控依赖追踪器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Override Dependency Impact Analyzer 模型覆盖依赖影响分析器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Override Impact Analyzer 模型覆盖影响分析器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Registry 模型注册表 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Risk Tier Classifier 模型风险分级器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Risk Tier Dependency Classifier 模型风险等级依赖分类器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Validation Dependency Orchestrator v2 模型验证依赖编排器v2 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Model Validation Dependency Orchestrator 模型验证依赖编排器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/NIST AI 100-5 Three-Layer Security NIST AI 100-5三层安全 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/NVIDIA Agentic Autonomy Levels NVIDIA Agent自治级别 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Non-AI Boundary Guard 非AI边界守卫 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Non-worsening 不恶化性 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Orchestrated Saga Engine 编排式Saga引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERM Budget Exempt Executor PERM预算豁免执行器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERM Independent Health Checker PERM独立健康检查器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERM-CORE Read-Only Interface Contract PERM-CORE只读接口契约 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERMBlockCommand PERM阻止命令 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERMBlockExecuted PERM阻止指令执行 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERMBudgetExemption PERM预算豁免 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERMBudgetExemptionUsed PERM预算豁免被使用 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERMIndependentHealthCheck PERM独立健康检查 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERM不修改CORE状态 PERM No Modify CORE State |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PERM预算豁免 PERM Budget Exemption |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Parameter Optimizer 参数优化器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PermissionCheck 权限检查 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/PermissionDenied 权限拒绝 |  | design_only | design | 0 | 0 |
| ...MY-PERM/PipelineOrchestrator CostTracker Component PipelineOrchestrator成本追踪组件 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/RBAC Permission Check Embedded Bridge RBAC权限检查内嵌桥接器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/RBACDecision RBAC决策 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/REDUCE 缩量保留方向 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/REJECT 完全阻断 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Red-Blue Validator 红蓝对抗验证器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Responsible AI Dependency Auditor 负责任AI依赖审计器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Reversibility 可撤销性 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Risk Alert Notification Dispatcher 风控告警通知分发器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Risk Check RBAC Permission Controller 风控检查RBAC权限控制器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Role and Interaction Journey 角色与交互旅程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Rollback Four-Tier Strategy Selector 回滚四级策略选择器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Rollback Operation Visual Tracker 回滚操作可视化追踪器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Rollback System 回滚系统 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Saga Deadlock Detector Saga死锁检测器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Saga Definition Saga定义器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Saga Observability Tracer Saga可观测性追踪器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Saga State Tracker Saga状态追踪器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Saga Version Compatibility Manager Saga版本兼容性管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Saga/Process Manager Dependency Orchestrator Saga/流程管理器依赖编排器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Soft Block 软阻断 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/System Health Five-Star Scorer 系统健康度五星评分器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/System Version Upgrade Path Manager 系统版本升级路径管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Szpruch Conditional Gate Szpruch条件门禁 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/TNR Safety Specification TNR安全规范 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/TaskCard Six-Dimension Anti-Drift Validator TaskCard六维防漂移校验器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Temporal GNN Dependency Drift Predictor 时序GNN依赖漂移预测器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Token Budget Coordinator Token预算协调器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Token Budget Manager Token预算管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Trading Session Aware Ops Scheduler 交易时段感知运维调度器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/TradingSessionSchedule 交易时段调度 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/TradingSessionSwitch 交易时段切换 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Transactionality 事务性 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Vector Index Health Monitor 向量索引健康监控器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/Zone Crossing Boundary Validator Zone Crossing边界校验器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/agent_creation_policy.py Agent创建策略 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/ai_modifiable 自治区 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/anomaly_detector.py 异常检测器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/anti_pattern_guard.py 反模式守卫 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/asymmetric_audit.py 非对称审计 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/auto_maintenance.py 自动维护 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/bootstrap_verifier.py 引导验证器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/build_sanitizer.py 构建清洗器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/cache_invalidation.py 缓存失效器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/contract_verifier.py 契约验证器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/cross_cutting.py 横切关注点 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/dependency_auditor.py 依赖审计器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/environment_manager.py 环境管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/exceptions.py 异常定义 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/genesis_bootstrap.py 创世引导 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/human_gated 门控区 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/immutable 禁区 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/串谋/策略同质化 Collusion/Strategy Homogeneity |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/交易时段仅监控 Trading Session Monitor Only |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/决策一致性 Decision Consistency |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/权限边界偏离 Permission Boundary Deviation |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/涌现行为 Emergent Behavior |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/禁止AI自动升级交易时段依赖库 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/禁止AI自动清理未归档交易日志和审计记录 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/禁止AI自动订阅付费数据源 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/禁止AI自动重启交易时段核心进程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/资源消耗异常 Resource Consumption Anomaly |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/通信异常 Communication Anomaly |  | design_only | design | 0 | 0 |
| D-AUTONOMY-PERM/隐性串谋 Implicit Collusion |  | design_only | design | 0 | 0 |
| src/zephyr/autonomy_perm/__init__.py | MOD-AUTONOMY_PERM | orphan | prototype | 0 | 0 |
| src/zephyr/autonomy_perm/_extensions/__init__.py | MOD-AUTONOMY_PERM | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/autonomy_perm/api/__init__.py | MOD-AUTONOMY_PERM | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/autonomy_perm/core/__init__.py | MOD-AUTONOMY_PERM | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/autonomy_perm/infrastructure/__init__.py | MOD-AUTONOMY_PERM | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/autonomy_perm/models/__init__.py | MOD-AUTONOMY_PERM | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/autonomy_perm/red_blue_validator/__init__.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 6 |
| src/zephyr/autonomy_perm/red_blue_validator/attack_registry.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 1 |
| src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 1 |
| src/zephyr/autonomy_perm/red_blue_validator/constitution_guard.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 1 |
| src/zephyr/autonomy_perm/red_blue_validator/convergence_checker.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 1 |
| src/zephyr/autonomy_perm/red_blue_validator/defense_runner.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 1 |
| src/zephyr/autonomy_perm/red_blue_validator/game_day_runner.py | MOD-AUTONOMY_PERM | draft | prototype | 0 | 1 |
| src/zephyr/autonomy_perm/services/__init__.py | MOD-AUTONOMY_PERM | orphan | scaffold_placeholder | 0 | 0 |
| 自治保护域-双写协调/D-AUTONOMY-166 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-反馈升级/D-AUTONOMY-184 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-向量索引/D-AUTONOMY-74 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-回滚协调/D-AUTONOMY-106 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-审计报告/D-AUTONOMY-203 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-成本/D-AUTONOMY-16 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-治理精简/D-AUTONOMY-128 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-理解成本/D-AUTONOMY-145 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-系统评分/D-AUTONOMY-151 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-链路监控/D-AUTONOMY-120 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域-风控通知/D-AUTONOMY-52 | MOD-AUTONOMY_PERM | design_only | design | 0 | 0 |
| 自治保护域/D-AUTONOMY-10 | MOD-AUTONOMY_PERM | design_only | design | 0 | 4 |

> (仅显示前 200 个模块，共 206 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 48 | contract,config_depends,data,event |
| D-SECURITY | 45 | contract,import_depends,domain_dependency,event,data,config_depends |
| D-SIGNAL | 15 | event,data,config_depends,contract |
| D-MKT_DATA | 15 | contract,data,event,config_depends |
| D-INTELLIGENCE | 10 | data,config_depends,contract |
| D-INTEGRATION | 10 | contract,data,event,config_depends |
| D-FACTOR | 10 | data,event,contract,config_depends |
| D-INFRA_RUNTIME | 9 | event,data,config_depends,contract |
| D-EX_SOR | 8 | config_depends,event,data,contract |
| D-KNOWLEDGE | 7 | contract,data,event,config_depends |
| D-DATA_ENG | 5 | data,contract,event |
| D-EX_CORE | 4 | event,contract |
| D-POSITION | 3 | data |
| D-PF_CORE | 3 | contract,data |
| D-ML_TRAIN | 3 | data,config_depends,event |
| D-TRADING | 2 | contract,config_depends |
| D-ML_SERVE | 1 | data |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 46 | event,contract,config_depends,data |
| D-AUTONOMY_CORE | 31 | config_depends,domain_dependency,contract,data,event |
| D-GOVERNANCE | 23 | config_depends,event,data,contract |
| D-OPS | 13 | config_depends,data,contract,event |
| D-INFRA_OPS | 11 | data,contract,event,config_depends |
| D-FRONTEND | 10 | data,contract,event |
| D-SIMULATION | 7 | config_depends,data,contract |
| D-PF_ALLOC | 5 | event,contract,data |
| D-REPORTING | 4 | data,contract,event,config_depends |
| D-CROSS_ASSET | 3 | contract,data,event |
| D-SELL_DECISION | 2 | config_depends,data |
| D-DATA_SEC | 1 | contract |
| D-DATA_GOV | 1 | contract |
| D-ALT_DATA | 1 | data |

## 域内依赖图

详见 [d_autonomy_perm_dependency.mmd](d_autonomy_perm_dependency.mmd)
