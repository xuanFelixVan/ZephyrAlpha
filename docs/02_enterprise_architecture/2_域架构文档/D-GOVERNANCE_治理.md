---
doc_type: domain_architecture_doc
title: D-GOVERNANCE lifecycle_management架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-GOVERNANCE lifecycle_management架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-GOVERNANCE |
| 域名称 | lifecycle_management |
| 架构层 | L2_domain |
| 模块总数 | 4289 |
| 设计态模块 | 611 |
| 原型态模块 | 3528 |
| 生产态模块 | 139 |
| 容量 | 138/200 (正常) |
| 描述 | 模块生命周期钩子(hooks) |

## 模块清单

共 4289 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| 01-跨域交叉点 vs 29-D-GOVERNANCE/D-GOV-11 | MOD-GOVERNANCE | design_only | design | 0 | 0 |
| D-GOVERNANCE/45 Capability List 45项能力清单 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/5 Drift Detection 5类漂移检测 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A2A Failure Escalation A2A失败升级 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A2A Gateway Policy Engine A2A检查网关策略引擎 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A2A Iron Law A2A铁律 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A2A Protocol Governance Auditor A2A协议治理审计器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A2A Protocol Governance Contracts A2A协议治理契约 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A2A Protocol Phase Hold A2A协议阶段保持 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ACO多路径依赖搜索器 ACOMultiPathDependencySearcher |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ADR Decision Tracking ADR决策追踪 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ADR Generation ADR架构决策记录自动生成 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ADR Generation ADR生成 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ADR Simulation ADR仿真 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ADR传播/多ADR交互/回溯/变更仿真等 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ADR解析/约束提取/双向关联/校验/推演等 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Autonomy Boundary AI自治边界 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Autonomy Boundary Manager AI自治边界管理器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Code Review AI代码审查 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Code Standards AI代码标准 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Construction Governor AI施工治理器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Ethics Statement AI伦理声明 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Hallucination Detection AI幻觉检测 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI Self Diagnosis AI自诊断监督 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AIConstructionGovernor AI建设治理器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI模型能力持续提升 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI治理框架 AI Governance Framework |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AI生成策略合规 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ALPHA-SIGNAL-DOMAIN-001 Alpha信号域标识 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/API Dependency API依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AST Call Graph AST调用图 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AST Call Graph Generator AST调用图生成器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AST解析/调用图/膨胀检测/清理/可视化等 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AaC Compiler AaC编译器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AaC DSL/约束定义/漂移检测/修复/CI集成等 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AaC DSL编译/CI门禁/漂移/修复/报告等 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Activation Phase Set 激活阶段集 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Administrator 管理员角色 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Admission Response 准入响应 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Adoption Curve Modeler 采纳曲线建模器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent Debate Agent辩论机制 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent Hard Boundary Agent硬边界 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent OS Policy Engine Agent OS策略引擎 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent RBAC Approver Check Agent RBAC审批人检查 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent RBAC Governance Bridges Contracts Agent RBAC治理桥契约 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agentic Drift Protection Agentic Drift防护 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agentic Regulator四层治理框架 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent架构 Agent Architecture |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Agent集群 Agent Cluster MARL |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Approval Escalation 审批升级 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture Contracts 架构契约 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture Drift Detection 架构漂移检测与纠正闭环 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture Principles 架构原则定义 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture Tech Debt Tracker 架构技术债追踪器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture Test Suite 架构测试套件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture as Code Engine 架构即代码引擎 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Architecture as Code 架构即代码 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ArchitectureGovernance 架构治理 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit & Compliance Traceability 审计与合规追溯 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Chain Domain 审计链域 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Engine 审计引擎 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Integrity Verifier 审计完整性验证器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Log Immutable 审计日志不可篡改 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Log Non-Tamperable 审计日志不可篡改 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Log Non-Tamperable 审计日志不可篡改删除 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Audit Orchestrator 审计编排器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AuditContext Consumer Interface AuditContext消费接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AuditContext 审计上下文接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AuditContextUpdate 审计上下文更新 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AuditLedger 审计账本 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/AuditQuery 审计查询 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/A股T+1制度不变 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Behavioral Auditor 行为审计器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Benchmark Integrity 基准完整性 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Blueprint Code Document Three Way Alignment 蓝图-代码-文档三方对齐 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Blueprint Code Document Three Way Alignment 蓝图-代码-文档三方对齐机制 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Blueprint-Code Traceability 蓝图-代码追溯 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Blueprint-Code-Doc Three-Way Alignment 蓝图-代码-文档三方必须对齐 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Broker Resilience Broker韧性 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Budget Handler 预算处理 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Budget Tracker 预算追踪 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Business Capability-Module Mapper 业务能力-模块映射器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/BusinessCapabilityMapper 业务能力映射器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/CFA Institute两层治理框架 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/CQRS/ES Modeling CQRS/ES建模 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/CTR-P1-009 Governance Contract CTR-P1-009治理架构契约 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/CTR-P1-012 ComplianceRule 合规规则 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Captide 对冲基金AI平台 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Causal Conflict Detector 因果冲突检测器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Cedar Cedar策略语言 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Change Approval Chain Not Bypassable 变更审批链不可被绕过 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Change Approval Flow 变更审批流 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Change Impact Analyzer 变更影响分析器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Change Shock Radius Predictor 变更冲击半径预测器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Check Threeway Alignment 检查三对齐 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Closed-Loop Rule 闭环规则 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Code Dedup Engine 代码去重引擎 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/CogAlpha |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Compliance Scripts 合规脚本 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ComplianceAudit 合规审计 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ComplianceAuditCompleted 合规审计完成 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ComplianceAuditor 合规审计器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ComplianceChecker 合规检查器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ComplianceRule Consumer Interface ComplianceRule消费接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ComplianceRuleUpdated 合规规则更新 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Conditional Gate Extension 条件门禁扩展 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ConfigChanged 参数变更事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Consequence Manager 后果管理器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Constitutional Update 宪法更新 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ConstitutionalGuard 宪法守卫 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Construction Gate 施工门禁 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Consume Event Set 消费事件集 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Consumer Interface Set 消费接口集 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Contract Version Management 契约版本管理 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ContractRegistered 契约注册 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ContractRegistry Consumer Interface ContractRegistry消费接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Coupling Metrics 耦合度量 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Coupling Strength Metrics 耦合度量计算器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/CouplingStrengthMetrics 耦合度量 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Critical Path Analyzer 关键路径分析器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Cross Cutting Triangle 横切三角 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Cross Environment Consistency 跨环境一致性校验 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Cross-Domain Intersection 跨域交叉点 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Cycle Detection 环路检测 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/D-GOV-16~26 Dependency Semantic Series 依赖语义系列 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/D-GOVERNANCE 治理 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/D1~D84 独立研究模块 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/D5 Architecture Validators D5架构验证器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DDD Iron Law Three Stage Execution DDD铁律三阶段执行 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DDDRuleCheck DDD铁律检查 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DDDRuleEnforcer DDD铁律执行器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DDDViolationDetected DDD违规检出 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DOM-GOV-CAP-001 容量升级 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Data Classification 数据分类 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Data Lifecycle 数据生命周期 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Data Quality 数据质量 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Data Source Reliability 数据源可靠性 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Decision Audit Trail 决策审计追踪 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Decision Fatigue CLI 决策疲劳CLI |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Decision Fatigue Detector 决策疲劳检测器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DecisionArchived 决策归档 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DecisionProvenance 决策溯源链 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DecisionTrace 决策溯源 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DepMap Engine 分层存储AST依赖扫描引擎 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Adoption Pattern Analyzer 依赖采纳模式分析器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Amplification Analyzer 依赖放大效应分析器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Amplification Mitigation 依赖放大缓解 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Analysis Domain 依赖分析域 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Bloat Meter 依赖膨胀度量器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Change Log 依赖变更日志 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Change Log 模块依赖变更日志 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Deduplication Advisor 依赖去重顾问 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Entropy Calculator 依赖熵计算器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Health Scorecard 依赖健康评分卡 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Manager 依赖管理 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Semantics Layer 依赖语义层 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Temporal Evolution Analyzer 依赖时序演化分析器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependency Update Latency Predictor 依赖更新延迟预测器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DependencyAmplification 依赖放大效应 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DependencySemantics 依赖语义 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dependent Type Verifier 依赖类型验证器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Developer Portal 开发者门户 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dnalyaw |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Downstream Anchors Verifier 下游锚点验证器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Drift Fix 漂移修复 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/DriftGovernance 漂移治理 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dual-Layer Gate Model 双层门控架构 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Durable Execution 持久化执行 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dw150 Update Blueprints dw150更新入 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Dw151 Full Verify dw151满验证 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-0046 执行核心→治理域依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-0093 合规域→治理域依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-0123 前端域→治理域依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-0124 治理域→自治核心依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-0125 治理域→集成域依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-0126 治理域→运行时基础设施依赖 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-GV-01 GatePassed E-GV-01门禁通过 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-GV-02 GateFailed E-GV-02门禁失败 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-GV-03 PolicyUpdated 策略 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/E-GV-04 AuditAnomalyDetected 审计 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EU AI Act Article 14 Compliance Mapping EU AI Act Article 14合规映射 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EU AI Act字面合规 EU AI Act Literal Compliance |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-AUT-AUDIT Consume Event EVT-AUT-AUDIT消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-AUT-PERM Consume Event EVT-AUT-PERM消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-CMP-RULE Consume Event EVT-CMP-RULE消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-DE-LINEAGE Consume Event EVT-DE-LINEAGE消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-EX-AUDIT Consume Event EVT-EX-AUDIT消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-FE-GOV Consume Event EVT-FE-GOV消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-INT-CONTRACT Consume Event EVT-INT-CONTRACT消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-OPS-ALERT Consume Event EVT-OPS-ALERT消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EVT-SEC-SCAN Consume Event EVT-SEC-SCAN消费事件 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Ecosystem Risk Diversification Analyzer 生态风险分散分析器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Entanglement-Aware Scheduler 纠缠感知调度器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Escalation Governance Contracts 升级治理契约 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Evals Evaluation Framework 评估框架 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/Event-Driven Dependency Tracer 事件驱动依赖追踪器 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EventBus Consumer Interface EventBus消费接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/EventBus 事件总线接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ExecutionAudit Consumer Interface ExecutionAudit消费接口 |  | design_only | design | 0 | 0 |
| D-GOVERNANCE/ExecutionAudit 执行审计接口 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 4289 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-OPS | 422 | runtime,import_depends,config_depends,test_depends |
| D-SECURITY | 421 | contract,runtime,import_depends,test_depends,data,config_depends,event |
| D-INTEGRATION | 351 | contract,import_depends,test_depends,event,data,config_depends |
| D-SHARED | 269 | import_depends,test_depends,event,contract,data |
| D-GOV_RULE | 269 | runtime,import_depends,config_depends,test_depends |
| D-TRADING | 248 | import_depends,test_depends,contract,data,event,config_depends |
| D-AUTONOMY_CORE | 220 | runtime,contract,import_depends,test_depends |
| D-INFRA_RUNTIME | 207 | runtime,import_depends,config_depends,test_depends,contract,data,event |
| D-GOV_AUDIT | 192 | import_depends,config_depends,test_depends |
| D-RISK | 130 | import_depends,test_depends,data,contract,event,config_depends |
| D-BEHAVIORAL_AUDIT | 103 | import_depends,test_depends |
| D-INTELLIGENCE | 85 | import_depends,test_depends,contract,data,event,config_depends |
| D-SIGNAL | 57 | import_depends,test_depends,config_depends,event,contract,data |
| D-MKT_DATA | 51 | import_depends,test_depends,event,contract,config_depends,data |
| D-FACTOR | 46 | test_depends,data,config_depends,contract,event |
| D-GOV_DRIFT | 36 | import_depends,config_depends,test_depends |
| D-PF_CORE | 30 | test_depends,event,data,contract,config_depends |
| D-SIMULATION | 28 | import_depends,test_depends,event,contract,data |
| D-DATA_ENG | 26 | event,contract,data,config_depends |
| D-EX_CORE | 23 | import_depends,test_depends,event,data,contract,config_depends |
| D-AUTONOMY_PERM | 23 | data,event,config_depends,contract |
| D-KNOWLEDGE | 19 | contract,event,data |
| D-REPORTING | 17 | import_depends,event,contract,config_depends,data |
| D-EX_SOR | 15 | event,contract,data,config_depends |
| D-POSITION | 14 | contract,data,event,config_depends |
| D-FRONTEND | 11 | test_depends |
| D-ML_SERVE | 9 | contract,event,data,config_depends |
| D-ML_TRAIN | 8 | contract,config_depends,event,data |
| D-SIGNAL_FUNDAMENTAL | 6 | test_depends |
| D-CROSS_ASSET | 2 | test_depends |
| D-PF_ALLOC | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 142 | contract,import_depends,data,config_depends,event,domain_dependency |
| D-OPS | 56 | contract,import_depends,config_depends,runtime,data,event,domain_dependency |
| D-INFRA_OPS | 56 | import_depends,contract,config_depends,data,event |
| D-AUTONOMY_CORE | 45 | import_depends,data,config_depends,contract,event |
| D-TRADING | 36 | runtime,contract,import_depends |
| D-FRONTEND | 23 | import_depends,contract,data,event,config_depends |
| D-INFRA_RUNTIME | 19 | import_depends |
| D-GOV_AUDIT | 15 | import_depends |
| D-PF_ALLOC | 14 | import_depends,config_depends,contract,data,event |
| D-PF_CORE | 12 | contract,import_depends |
| D-REPORTING | 11 | contract,import_depends |
| D-INTEGRATION | 11 | import_depends,config_depends |
| D-EX_CORE | 10 | import_depends,config_depends |
| D-ALT_DATA | 10 | contract,config_depends,data,event |
| D-SELL_DECISION | 7 | data,contract |
| D-SECURITY | 7 | import_depends |
| D-INTELLIGENCE | 7 | import_depends,config_depends |
| D-DATA_SEC | 6 | import_depends,data,contract,event |
| D-CROSS_ASSET | 6 | config_depends,event,contract |
| D-FACTOR | 5 | import_depends,config_depends |
| D-DATA_GOV | 5 | config_depends,data,contract |
| D-SHARED | 3 | import_depends |
| D-GOV_DRIFT | 3 | import_depends |
| D-BEHAVIORAL_AUDIT | 3 | import_depends |
| D-SIGNAL | 2 | contract,import_depends |
| D-MKT_DATA | 2 | config_depends |
| D-GOV_RULE | 2 | import_depends,config_depends |
| D-RISK | 1 | config_depends |
| D-POSITION | 1 | config_depends |

## 域内依赖图

详见 [d_governance_dependency.mmd](d_governance_dependency.mmd)
