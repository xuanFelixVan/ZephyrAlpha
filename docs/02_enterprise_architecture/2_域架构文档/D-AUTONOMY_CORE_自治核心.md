---
doc_type: domain_architecture_doc
title: D-AUTONOMY_CORE 自治核心架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-AUTONOMY_CORE 自治核心架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-AUTONOMY_CORE |
| 域名称 | 自治核心 |
| 架构层 | L1_platform |
| 模块总数 | 650 |
| 设计态模块 | 475 |
| 原型态模块 | 168 |
| 生产态模块 | 1 |
| 容量 | 1/150 (正常) |
| 描述 | 自治核心域。负责Agent自治运行时核心，包括AutoRuntime Core、PipelineOrchestrator、AgentOrchestrator、Task状态机。 |

## 模块清单

共 650 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-AUTONOMY-CORE/11 Agents Full MVP 11个Agent全部MVP实现 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/8-Collection Unified Schema Manager 8大Collection统一Schema管理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Check A2A检查 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Check Gateway A2A检查网关 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Check Gateway Policy Engine A2A检查网关策略引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Check Non-Bypassable A2A检查不可绕过 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Check Protocol A2A检查协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Communication Agent间通信 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/A2A Protocol A2A协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ABAC策略 ABAC Policy |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AGENTICAITA AGENTICAITA框架 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI 人工智能 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI 治理执行者角色 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AISI 2026报告 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI自主执行率阈值 AI Autonomous Execution Rate Threshold |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI自治行为审计 AI Autonomous Behavior Audit |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI自治运维是闭环而非开环 Closed-Loop Autonomy |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI自治运维闭环 AI自治运维 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AI自治进化与闭环优化 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/API LLM |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ARA Adaptive Risk Architecture ARA自适应风险架构 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ARA自适应风险架构 ARA Adaptive Risk Architecture |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ARS双轨结算模型 ARS Dual-track Settlement Model |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AWQ 4-bit Quantization AWQ 4-bit量化 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AWS Agentic AI安全范围矩阵 AWS Agentic AI Security Scope Matrix |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AWS Resilient AI Agents AWS弹性AI Agent |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Actor Actor执行器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Actor 执行器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Actor-Evaluator-SelfReflection Actor-Evaluator-SelfReflection三组件 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Adaptive Z-Score Trigger Engine 自适应Z分数触发引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Architecture Position Agent架构在全局架构中的位置 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Architecture Unified Source Agent架构唯一真源 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Audit Trail Agent审计链 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Autonomy Boundary Agent自治边界 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Budget Enforcer Agent预算执行器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Card Registry Agent Card注册表 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Challenge 代理挑战 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Cold Start Agent冷启动与技能注册 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Cold Start Skill Registration Agent冷启动与技能注册 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Collaboration Flow Panorama Agent协作流全景图 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Command Chain Agent分层指挥链 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Communication Protocol Agent间通信协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Communication Security Agent通信安全 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Coordination Agent协调 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Dispatch Agent调度分发 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Drift Guard Agent漂移守卫 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Drift量化检查器 Agent Drift Quantitative Checker |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Error Recovery Agent错误恢复与优雅降级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Escalation Engine Agent升级引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Four Level Autonomy Model Agent四级自治模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Identity Manager Agent身份管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Kill Switch Agent紧急制动 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Legacy Issue Decision Agent遗留问题裁定21项 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Memory Agent记忆 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Memory Architecture Agent记忆架构 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Memory Vector Retrieval RAG Agent记忆向量检索 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Observability Agent可观测性 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Permission Guard Agent权限守卫 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Process Crash Agent进程崩溃 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Registry Agent注册表 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Resource Manager Agent资源管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Spec Agent规格 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Stability Index ASI 索引 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent State Agent状态检查点 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent State Manager Agent状态管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Test Chaos Engineering Agent测试与混沌工程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Testing Chaos Engineering Agent测试与混沌工程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Three Layer Command Chain Agent三层指挥链 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Upgrade Safety Mode Agent升级安全模式 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent Version Management Agent版本管理策略 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent-R Agent-R实时反思 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AgentCard Agent技能卡 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agentic Financial Market Model AFMM 模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent串谋检测 Agent Collusion Detection |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent可观测性 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent安全约束 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent架构安全约束 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent漏洞全景与防御升级 Agent Vulnerability Panorama and Defense Upgrade |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent行为约束 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent身份注册与认证 Agent Identity Registration and Authentication |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent轮换策略 Agent Rotation Strategy |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent间信任利用攻击 Inter-agent Trust Exploitation |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Agent间通信协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Anthropic Agent Skills Anthropic Agent技能标准 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Architecture Component to Domain Mapping 架构组件到功能域映射 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Architecture Diagram Relations 与其他架构图的关系 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Assurance Gap Manager 保障缺口管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Async Reflection 反思为异步执行 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Audit Trail 审计追踪 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AuditLogger 审计日志器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AuditTrace Interface 审计追踪接口 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Auto-Fix Engine 自动修复引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AutoGen 2.0 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Automated Operations Execution 自动化运维执行 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/AutonomousExecutionRateDegraded 自主执行率降级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Autonomy Boundary Enforcer 自治边界执行器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Autonomy Circuit Breaker 自治熔断条件 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Autonomy Maturity Grading 自治成熟度分级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Autonomy Passport 自治护照 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Autopilot 自动驾驶 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/BEST-Route BEST-Route路由 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Backtest Execution 回测执行 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Benchmark Analysis 对标分析 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/BlackSwanDetected 黑天鹅检测 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Bootstrap Superadmin 超级管理员引导 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Bounded Autonomy Level Manager 有界自治等级管理器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Budget Enforcer 预算执行器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Budget Management 预算管理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/BudgetExceeded 预算超限 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CSCR CSCR路由 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CTR-P1-014 ExperimentResult CTR-P1-014实验结果 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CTR-TRACE-001 AuditTrace 审计追踪 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CapabilityCard 能力卡片 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Causal LLM Routing 因果LLM路由 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Chaos Engineering Experiment Library 混沌工程实验库 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cheng Adaptive LLM Multi-Agent Cheng自适应LLM多Agent |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ChromaDB Runtime Validator ChromaDB运行验证器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Circuit Breaker 熔断器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Claude Claude模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cold Start 6-Step 冷启动6步流程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cold Start Process 冷启动流程 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cold Start Requires Skill Registration Agent冷启动需要技能注册 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cold Start Skill Registration 冷启动与技能注册 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Command Flow 指令流 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Command Priority 指令优先级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Compliance Check 合规检查 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Config Update 配置更新 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Conflict & Contradiction Matrix 冲突与矛盾矩阵 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Conflict Resolution 冲突解决 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ContestTrade ContestTrade框架 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Context Engine 上下文引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Context Manager 上下文管理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Context Recycling 上下文回收 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CoreReadOnlyState 核心只读状态 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cost Control 成本控制 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cost Controller 成本控制器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cost Governance 成本治理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cost-Aware Routing 成本感知路由 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CrewAI |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cross-Layer Interaction Matrix 跨层交互矩阵 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Cross-Layer Interaction Rules 跨层交互规则 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/CrowdnessWarning 拥挤度告警 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/D-AUT |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/D-AUT-CORE 核心 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/D-AUTONOMY |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/D-AUTONOMY-CORE 核心 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Data Quality Check 数据质量检查 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Data Quality Self-Management 数据质量自管理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Decision Checkpoint 决策前快照检查点 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/DecisionTraceBroken 决策溯源断链 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/DeepSeek V4 Pro DeepSeek V4 Pro模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/DeepSeek-7B DeepSeek-7B模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Degradation Strategy Matrix 降级策略矩阵 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Detect 异常检测 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Diagnose 根因分析 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Drift Detection 漂移检测 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Drift Detector 漂移检测器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Dual Channel Scheduler Decision 双通道调度决策 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Episodic Memory 情景记忆 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Error Classification Recovery Strategy 错误分类与恢复策略 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Error Recovery 优雅降级 错误恢复与优雅降级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Error Recovery 错误恢复 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Escalation Engine 升级引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/EscalationTriggered 升级触发 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Evaluator Evaluator评估器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Evaluator 评估器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Evolution Agent 进化Agent |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Execution Bus 执行层消息总线 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Execution Layer Agents 执行层Agent组 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Execution Traces Collection Manager 执行追踪Collection管理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/ExperimentAnomaly 实验异常检测 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/FAISS FAISS向量检索引擎 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/FCA Mills Review自治光谱 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/FSM Verifier FSM验证器 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Factor Computation 因子计算 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Feature Store Dependency Drift Detector 特征依赖链漂移检测 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Fee Track 费用轨道 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Feedback Flow 反馈流 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Five-Stage Memory Pipeline 五阶段记忆流水线 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Four Track Decision Path Agent Responsibility 四轨决策路径中Agent的职责 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Four-Layer Memory Model 四层记忆模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Four-Layer Versioning 四层版本化 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Four-Layer Versioning 四层版本化分类法 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/Functional Domain List 功能域清单 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-GA 守护智能体汇总 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-GA-01 多Agent架构 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-GA-02 监控盲区 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-GA-03 独立运行环境 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-SZP Szpruch运行时治理汇总 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-SZP-01 日内高频 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-SZP-02 多Agent工作流 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-SZP-03 轨迹漂移盲区 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-TRUST Agent间信任防护汇总 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-TRUST-01 多Agent通信 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-TRUST-02 Agent间协议 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GATE-TRUST-03 Meta-Governance 治理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GD-02 AI自治边界分三级 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GLM-5.1 GLM-5.1模型 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GPU Management GPU管理 |  | design_only | design | 0 | 0 |
| D-AUTONOMY-CORE/GPU Memory Insufficient GPU显存不足 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 650 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 87 | event,contract,config_depends,data |
| D-INTEGRATION | 76 | import_depends,data,event,contract,config_depends |
| D-SECURITY | 67 | import_depends,event,data,contract,config_depends |
| D-SIGNAL | 53 | event,contract,config_depends,data |
| D-GOVERNANCE | 45 | import_depends,event,config_depends,contract,data |
| D-FACTOR | 34 | contract,config_depends,data,event |
| D-INTELLIGENCE | 32 | import_depends,contract,domain_dependency,data,config_depends,event |
| D-INFRA_RUNTIME | 31 | contract,event,data,config_depends |
| D-AUTONOMY_PERM | 31 | data,domain_dependency,contract,event,config_depends |
| D-MKT_DATA | 26 | data,event,contract,config_depends |
| D-DATA_ENG | 20 | config_depends,contract,event,data |
| D-TRADING | 17 | data,contract,config_depends,event |
| D-KNOWLEDGE | 17 | event,data,config_depends,contract |
| D-PF_CORE | 15 | event,contract,data,config_depends |
| D-ML_TRAIN | 15 | data,event,contract,config_depends |
| D-EX_SOR | 15 | data,event,contract,config_depends |
| D-EX_CORE | 15 | data,config_depends,contract,event |
| D-REPORTING | 10 | config_depends,contract,data,event |
| D-SIMULATION | 8 | contract,data,config_depends |
| D-POSITION | 7 | contract,event,data |
| D-ML_SERVE | 7 | event,data,contract,config_depends |
| D-SHARED | 6 | import_depends |
| D-GOV_AUDIT | 3 | import_depends |
| D-GOV_RULE | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 220 | contract,runtime,import_depends,test_depends |
| D-COMPLIANCE | 126 | config_depends,data,event,contract |
| D-INFRA_OPS | 43 | data,event,config_depends,contract |
| D-OPS | 37 | import_depends,config_depends,event,data,contract,runtime |
| D-FRONTEND | 25 | data,event,config_depends,contract |
| D-ALT_DATA | 9 | contract,data,config_depends |
| D-SELL_DECISION | 6 | data,config_depends,contract,event |
| D-PF_ALLOC | 6 | data,event,contract |
| D-CROSS_ASSET | 6 | contract,data,event |
| D-DATA_GOV | 5 | config_depends,data,contract |
| D-TRADING | 3 | import_depends |
| D-INTEGRATION | 2 | import_depends |
| D-DATA_SEC | 2 | data,contract |
| D-INTELLIGENCE | 1 | import_depends |

## 域内依赖图

详见 [d_autonomy_core_dependency.mmd](d_autonomy_core_dependency.mmd)
