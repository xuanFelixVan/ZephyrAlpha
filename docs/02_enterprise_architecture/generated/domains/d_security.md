---
doc_type: domain_architecture_doc
title: D-SECURITY adversarial_validation架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SECURITY adversarial_validation架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SECURITY |
| 域名称 | adversarial_validation |
| 架构层 | L1_platform |
| 模块总数 | 849 |
| 设计态模块 | 603 |
| 原型态模块 | 106 |
| 生产态模块 | 134 |
| 容量 | 134/200 (正常) |
| 描述 | 红蓝对抗验证 |

## 模块清单

共 849 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-SECURITY/4层guardrails 4-layer Guardrails |  | design_only | design | 0 | 0 |
| D-SECURITY/6W Log Specification 6W日志规范 |  | design_only | design | 0 | 0 |
| D-SECURITY/AAAI 2026 FinJailbreak AAAI 2026金融越狱 |  | design_only | design | 0 | 0 |
| D-SECURITY/ABAC策略引擎 ABAC Policy Engine |  | design_only | design | 0 | 0 |
| D-SECURITY/ACLGuard 访问控制 |  | design_only | design | 0 | 0 |
| D-SECURITY/AES-256-GCM AES-256-GCM加密 |  | design_only | design | 0 | 0 |
| D-SECURITY/AES-256加密 AES-256 Encryption |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Agent Dependency Sandbox AI Agent依赖沙箱 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Agent Dependency Security Sandbox AI Agent依赖安全沙箱 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Code Modification Auditor AI代码修改审计器 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Construction Governor AI代码质量门控 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Driven Insider Trading Monitoring AI驱动内幕交易监控 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Hallucination Package Name Guard AI幻觉包名防护 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Read-Only Permission Executor AI只读权限执行器 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI Writable Permission Controller AI可写权限控制器 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI-driven Automated Red Team AI驱动自动化红队 |  | design_only | design | 0 | 0 |
| D-SECURITY/AI-driven Insider Trading Monitoring 监控 |  | design_only | design | 0 | 0 |
| D-SECURITY/AISGBlocked AISG门禁拦截 |  | design_only | design | 0 | 0 |
| D-SECURITY/AISGGate AISG拦截门禁 |  | design_only | design | 0 | 0 |
| D-SECURITY/AISG拦截门禁 AISG Intercept Gate |  | design_only | design | 0 | 0 |
| D-SECURITY/AISG门禁与gateway.py关系 AISG Gate gateway.py Relationship |  | design_only | design | 0 | 0 |
| D-SECURITY/AI_Agent |  | design_only | design | 0 | 0 |
| D-SECURITY/AI脱敏管道 AI Desensitization Pipeline |  | design_only | design | 0 | 0 |
| D-SECURITY/AI驱动自动化红队 AI-driven Automated Red Team |  | design_only | design | 0 | 0 |
| D-SECURITY/API Security Gateway API安全网关 |  | design_only | design | 0 | 0 |
| D-SECURITY/AWS Agentic AI Security Scope Matrix 安全 |  | design_only | design | 0 | 0 |
| D-SECURITY/AWS Bedrock AgentCore沙箱逃逸 AWS Bedrock AgentCore Sandbox Escape |  | design_only | design | 0 | 0 |
| D-SECURITY/AWS Security Scope 2 AWS安全范围Scope 2 |  | design_only | design | 0 | 0 |
| D-SECURITY/AWS Security Scope 4 AWS安全范围Scope 4 |  | design_only | design | 0 | 0 |
| D-SECURITY/Abnormal Access Pattern Detection 异常访问模式检测 |  | design_only | design | 0 | 0 |
| D-SECURITY/Abnormal Profit Rate 异常盈利率 |  | design_only | design | 0 | 0 |
| D-SECURITY/Abnormal Profit 异常盈利检测 |  | design_only | design | 0 | 0 |
| D-SECURITY/Abnormal Trading Pattern Detection 异常交易模式检测 |  | design_only | design | 0 | 0 |
| D-SECURITY/Access Controller 访问控制器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Access Record 审计记录 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Alignment Checks Agent对齐检查 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Behavior Baseline Learner Agent行为基线学习器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Cannot Impersonate Agent不可冒充其他Agent |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Collusion Must Be Detected Agent串谋行为必须被检测和阻断 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Communication Encryptor Agent间通信加密器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Cryptographic Identity DID Ed25519 Agent密码学身份 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Emergent Behavior Must Be Detected Agent涌现行为必须被检测和管控 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Goal Hijack Agent目标劫持 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Identity Non-Impersonation Agent身份不可冒充 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Mesh Cryptographic Identity Agent Mesh密码学身份 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Output Content Filter Agent输出内容过滤器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Permission Dynamic Shrinker Agent权限动态收缩器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Security Agent安全 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Security Agent安全串谋/涌现/幻觉/记忆投毒 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent Security Module Agent安全模块 |  | design_only | design | 0 | 0 |
| D-SECURITY/AgentSandbox Agent沙箱隔离 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agentic Supply Chain Vulnerabilities Agent供应链漏洞 |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent不可绕过安全检查 Agent No Bypass Security Check |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent安全 Agent Security |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent安全是独立关注点 Agent Security Independent Concern |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent工具调用白名单 Agent Tool Call Whitelist |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent持久化记忆写入验证 Agent Memory Write Validation |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent沙箱实例不可共享 Agent Sandbox No Sharing |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent漂移检测 Agent Drift Detection |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent预算上限 Agent Budget Limit |  | design_only | design | 0 | 0 |
| D-SECURITY/Agent预算不可超限 Agent Budget Limit |  | design_only | design | 0 | 0 |
| D-SECURITY/Application and API Layer 应用与API层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Attack Behavior Auto Blocker 攻击行为自动阻断器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Attack Surface Simulator 攻击面模拟器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Audit Chain 审计链 |  | design_only | design | 0 | 0 |
| D-SECURITY/Audit Log Protector 审计日志保护器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Audit Trail 不可变审计轨迹 |  | design_only | design | 0 | 0 |
| D-SECURITY/Authentication Failure Handler 认证失败处理器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Auto Alert and Manual Review 自动告警与人工审查 |  | design_only | design | 0 | 0 |
| D-SECURITY/BLACKICE Red Team Toolkit BLACKICE红队工具包 |  | design_only | design | 0 | 0 |
| D-SECURITY/BLACKICE 红队工具包 |  | design_only | design | 0 | 0 |
| D-SECURITY/Behavior Pattern Testing 行为模式测试 |  | design_only | design | 0 | 0 |
| D-SECURITY/Behavior Trajectory Similarity 行为轨迹相似度 |  | design_only | design | 0 | 0 |
| D-SECURITY/Blockchain Anchored Timestamp 区块链锚定时间戳 |  | design_only | design | 0 | 0 |
| D-SECURITY/Blockchain Anchoring 区块链锚定 |  | design_only | design | 0 | 0 |
| D-SECURITY/CEO Annual Certification CEO年度认证 |  | design_only | design | 0 | 0 |
| D-SECURITY/Casbin RBAC Permission Controller Casbin RBAC权限控制器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Cascading Failures 级联失败 |  | design_only | design | 0 | 0 |
| D-SECURITY/Cloud Security Alliance Agentic Trust Framework 云安全联盟自治信任框架 |  | design_only | design | 0 | 0 |
| D-SECURITY/Code Security Auto Scanner 代码安全自动扫描器 |  | design_only | design | 0 | 0 |
| D-SECURITY/CodeShield CodeShield代码盾 |  | design_only | design | 0 | 0 |
| D-SECURITY/Collective Score 核心 |  | design_only | design | 0 | 0 |
| D-SECURITY/Collusion Detection Threshold 串谋检测阈值 |  | design_only | design | 0 | 0 |
| D-SECURITY/Collusion Detection via Communication Pattern 串谋检测采用通信模式分析 |  | design_only | design | 0 | 0 |
| D-SECURITY/Collusion Pattern Simulation 串谋模式模拟 |  | design_only | design | 0 | 0 |
| D-SECURITY/CollusionDetected 共谋检测触发 |  | design_only | design | 0 | 0 |
| D-SECURITY/CollusionDetection 串谋检测 |  | design_only | design | 0 | 0 |
| D-SECURITY/Communication Security 通信安全 |  | design_only | design | 0 | 0 |
| D-SECURITY/Compliance Framework Comprehensive Benchmark 合规框架综合对标 |  | design_only | design | 0 | 0 |
| D-SECURITY/Compliance Governance 合规与治理 |  | design_only | design | 0 | 0 |
| D-SECURITY/Compliance Security Module Completion 合规安全模块补全 |  | design_only | design | 0 | 0 |
| D-SECURITY/Confidence Scoring Mechanism 置信度评分机制 |  | design_only | design | 0 | 0 |
| D-SECURITY/Consistency Check 一致性检查 |  | design_only | design | 0 | 0 |
| D-SECURITY/Content Fingerprint Generator Verifier 内容指纹生成验证器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Content Security 内容安全 |  | design_only | design | 0 | 0 |
| D-SECURITY/Correlation 相关性 |  | design_only | design | 0 | 0 |
| D-SECURITY/Cross Wall Audit Chain 跨墙操作审计链 |  | design_only | design | 0 | 0 |
| D-SECURITY/Cross Wall End 跨墙结束 |  | design_only | design | 0 | 0 |
| D-SECURITY/Cross Wall Request 跨墙请求 |  | design_only | design | 0 | 0 |
| D-SECURITY/Cross-wall Approval Procedure 跨墙审批流程 |  | design_only | design | 0 | 0 |
| D-SECURITY/Crypto-Shredding Interface Crypto-Shredding接口 |  | design_only | design | 0 | 0 |
| D-SECURITY/Crypto-Shredding Key Destruction Restricted Crypto-Shredding密钥销毁受限 |  | design_only | design | 0 | 0 |
| D-SECURITY/Crypto-Shredding 加密粉碎 |  | design_only | design | 0 | 0 |
| D-SECURITY/Crypto-Shredding 密码粉碎 |  | design_only | design | 0 | 0 |
| D-SECURITY/D-SECURITY 安全 |  | design_only | design | 0 | 0 |
| D-SECURITY/D-SECURITY→D-AUTONOMY-CORE 安全域硬依赖自治核心 |  | design_only | design | 0 | 0 |
| D-SECURITY/D-SECURITY→D-INFRA-RUNTIME 安全域软依赖运行时 |  | design_only | design | 0 | 0 |
| D-SECURITY/D-SECURITY→D-INTEGRATION 安全域软依赖集成域 |  | design_only | design | 0 | 0 |
| D-SECURITY/DID Decentralized Identifier DID去中心化标识符 |  | design_only | design | 0 | 0 |
| D-SECURITY/DLP Data Loss Prevention 事件 |  | design_only | design | 0 | 0 |
| D-SECURITY/Daily Data Access Report 每日数据访问报告 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Access Audit 数据访问审计 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Access Controller 数据访问控制器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Classification Determination 数据分级判定 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Desensitization Engine 数据脱敏引擎 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Encryption and Masking Processor 数据加密与脱敏处理器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Layer 数据层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Masking & Privacy 数据脱敏与隐私 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Protection 数据保护 |  | design_only | design | 0 | 0 |
| D-SECURITY/Data Source API Key Security Storage 数据源API密钥安全存储器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Deception Split 欺骗分割 |  | design_only | design | 0 | 0 |
| D-SECURITY/Defense in Depth 6 Layer 纵深防御6层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Defense in Depth 6 Layers 纵深防御6层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Dependency Behavior eBPF Monitor 依赖行为eBPF监控器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Dependency Graph ZK Proof 依赖图ZK证明 |  | design_only | design | 0 | 0 |
| D-SECURITY/Dependency Penetration Mapper 依赖穿透映射器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Dependency Vulnerability Auto Detector 依赖漏洞自动检测器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Deutsche Bank AI Compliance 德意志银行AI合规监控 |  | design_only | design | 0 | 0 |
| D-SECURITY/Direct Exclusive Control 直接且独占的控制权 |  | design_only | design | 0 | 0 |
| D-SECURITY/Docker Container Docker容器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Dynamic Permission Allocation 动态权限分配 |  | design_only | design | 0 | 0 |
| D-SECURITY/E2B沙箱 E2B Sandbox |  | design_only | design | 0 | 0 |
| D-SECURITY/EncryptionKeyRotated 密钥轮换完成 |  | design_only | design | 0 | 0 |
| D-SECURITY/End-to-End Data Encryption and Access Controller 数据端到端加密与访问控制器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Ensemble 集成 |  | design_only | design | 0 | 0 |
| D-SECURITY/Error Duplicate Order Control 错误/重复订单控制 |  | design_only | design | 0 | 0 |
| D-SECURITY/Ethical Wall 信息隔离墙 |  | design_only | design | 0 | 0 |
| D-SECURITY/FCFT金融宪法微调 FCFT Financial Constitution Fine-Tuning |  | design_only | design | 0 | 0 |
| D-SECURITY/FHE Fully Homomorphic Encryption 全量 |  | design_only | design | 0 | 0 |
| D-SECURITY/FL Federated Learning FL联邦学习 |  | design_only | design | 0 | 0 |
| D-SECURITY/Fact Checking 事实核查 |  | design_only | design | 0 | 0 |
| D-SECURITY/Fail-Closed Policy Manager 失败关闭策略管理器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Financial Constitution Fine-Tuning 金融宪法微调 |  | design_only | design | 0 | 0 |
| D-SECURITY/Financial Security Compliance Checker 金融安全合规检查器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Firecracker microVM Firecracker微虚拟机 |  | design_only | design | 0 | 0 |
| D-SECURITY/Firecracker microVM Sandbox Isolation Firecracker microVM沙箱隔离 |  | design_only | design | 0 | 0 |
| D-SECURITY/Formal Verification形式化验证 Formal Verification |  | design_only | design | 0 | 0 |
| D-SECURITY/GATE-PQC 纯PQC模式门禁 |  | design_only | design | 0 | 0 |
| D-SECURITY/GATE-SOC2 SOC 2认证汇总 |  | design_only | design | 0 | 0 |
| D-SECURITY/GATE-SOC2-01 第三方服务 |  | design_only | design | 0 | 0 |
| D-SECURITY/GATE-SOC2-02 资金规模 |  | design_only | design | 0 | 0 |
| D-SECURITY/GATE-SOC2-03 审计观察期 |  | design_only | design | 0 | 0 |
| D-SECURITY/Gap Ratio 缺口比率 |  | design_only | design | 0 | 0 |
| D-SECURITY/Goal Drift Detection 目标漂移检测 |  | design_only | design | 0 | 0 |
| D-SECURITY/Goldman Sachs Agentic AI 高盛Agentic AI合规工具 |  | design_only | design | 0 | 0 |
| D-SECURITY/Graph 图谱 |  | design_only | design | 0 | 0 |
| D-SECURITY/Hard Boundary HB-SEC-01~13 硬边界 |  | design_only | design | 0 | 0 |
| D-SECURITY/Host and OS Layer 主机与操作系统层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Human-Agent Trust Exploitation 人机信任利用 |  | design_only | design | 0 | 0 |
| D-SECURITY/IAM Access Control IAM与访问控制 |  | design_only | design | 0 | 0 |
| D-SECURITY/IAM与访问控制 IAM and Access Control |  | design_only | design | 0 | 0 |
| D-SECURITY/IAM仍然重要 IAM Still Important |  | design_only | design | 0 | 0 |
| D-SECURITY/IP Whitelist Manager IP白名单管理 |  | design_only | design | 0 | 0 |
| D-SECURITY/ISOLATEGPT hub-spoke ISOLATEGPT中心辐射 |  | design_only | design | 0 | 0 |
| D-SECURITY/Identity & Access Manager 身份与访问管理器 |  | design_only | design | 0 | 0 |
| D-SECURITY/Identity Access 身份与访问 |  | design_only | design | 0 | 0 |
| D-SECURITY/Identity Privilege Abuse 身份与权限滥用 |  | design_only | design | 0 | 0 |
| D-SECURITY/Identity Rotation and Anonymization 身份轮换与匿名化 |  | design_only | design | 0 | 0 |
| D-SECURITY/Identity and Access Layer 身份与访问层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Info Trading Time Lag 信息-交易时滞 |  | design_only | design | 0 | 0 |
| D-SECURITY/Input Detection/Auth/Scan 输入检测/认证/扫描等 |  | design_only | design | 0 | 0 |
| D-SECURITY/Input Provenance Tagging 标签 |  | design_only | design | 0 | 0 |
| D-SECURITY/InputOutputGuard 输入输出防护 |  | design_only | design | 0 | 0 |
| D-SECURITY/Insecure Inter-Agent Communication 不安全Agent间通信 |  | design_only | design | 0 | 0 |
| D-SECURITY/Insider Trading Prevention 内幕交易防护 |  | design_only | design | 0 | 0 |
| D-SECURITY/Insider Trading Protection 内幕交易防护 |  | design_only | design | 0 | 0 |
| D-SECURITY/IntegrityViolation 完整性违规 |  | design_only | design | 0 | 0 |
| D-SECURITY/Invariant Labs MCP工具投毒 Invariant Labs MCP Tool Poisoning |  | design_only | design | 0 | 0 |
| D-SECURITY/KILLSWITCH.md标准化 KILLSWITCH Standardization |  | design_only | design | 0 | 0 |
| D-SECURITY/Key Destruction 密钥销毁 |  | design_only | design | 0 | 0 |
| D-SECURITY/Key Hierarchy Management 密钥层级管理 |  | design_only | design | 0 | 0 |
| D-SECURITY/Key Layer Management 密钥层级管理 |  | design_only | design | 0 | 0 |
| D-SECURITY/KeySecretManager 密钥管理 |  | design_only | design | 0 | 0 |
| D-SECURITY/Kill Switch 15c3-5 Kill Switch市场接入 |  | design_only | design | 0 | 0 |
| D-SECURITY/Kill Switch Five Layer Defense Kill Switch五层防御 |  | design_only | design | 0 | 0 |
| D-SECURITY/Kill Switch Infrastructure Layer OWASP ASI08 Kill Switch基础设施层 |  | design_only | design | 0 | 0 |
| D-SECURITY/Kill Switch Invariant Kill Switch不变量 |  | design_only | design | 0 | 0 |
| D-SECURITY/Kill Switch 紧急停机开关 |  | design_only | design | 0 | 0 |
| D-SECURITY/Knowledge Access Control 知识访问控制 |  | design_only | design | 0 | 0 |
| D-SECURITY/L0 Supply Chain SHA256 Verifier L0供应链SHA256验证器 |  | design_only | design | 0 | 0 |
| D-SECURITY/L2 Auto Approval L2自动审批 |  | design_only | design | 0 | 0 |
| D-SECURITY/L2 L3 Data Access Audit L2/L3数据访问审计 |  | design_only | design | 0 | 0 |
| D-SECURITY/L3 Manual Approval L3人工审批 |  | design_only | design | 0 | 0 |
| D-SECURITY/L4 Agent Security Permission Isolator L4 Agent安全权限隔离器 |  | design_only | design | 0 | 0 |
| D-SECURITY/LLM Guardrails MCP Triple Gate LLM guardrails+MCP Triple Gate |  | design_only | design | 0 | 0 |
| D-SECURITY/LLM Pentesting 5-layer Methodology LLM渗透测试5层方法论 |  | design_only | design | 0 | 0 |
| D-SECURITY/LLM Pentesting 5层方法论 LLM Pentesting 5-layer Methodology |  | design_only | design | 0 | 0 |
| D-SECURITY/LLM Security Gateway LLM安全网关 |  | design_only | design | 0 | 0 |
| D-SECURITY/LLM Security LLM安全网关 |  | design_only | design | 0 | 0 |
| D-SECURITY/LLM调用脱敏 LLM Call Desensitization |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 849 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SIGNAL | 62 | contract,data,config_depends,event |
| D-BEHAVIORAL_AUDIT | 51 | import_depends |
| D-INFRA_RUNTIME | 50 | contract,config_depends,event,data |
| D-FACTOR | 46 | contract,event,data,config_depends |
| D-MKT_DATA | 38 | event,data,contract,config_depends |
| D-TRADING | 23 | import_depends,contract,event,data,config_depends |
| D-EX_SOR | 23 | contract,data,event,config_depends |
| D-DATA_ENG | 17 | event,config_depends,data,contract |
| D-EX_CORE | 16 | event,data,contract,config_depends |
| D-ML_TRAIN | 13 | data,contract,event |
| D-SHARED | 9 | import_depends,event,data,contract |
| D-POSITION | 8 | data,event,contract |
| D-GOVERNANCE | 7 | import_depends |
| D-GOV_RULE | 4 | import_depends |
| D-INTEGRATION | 3 | import_depends |
| D-GOV_AUDIT | 3 | import_depends |
| D-INTELLIGENCE | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 421 | import_depends,test_depends,contract,runtime,event,data,config_depends |
| D-COMPLIANCE | 130 | data,contract,config_depends,event |
| D-RISK | 98 | data,contract,event,config_depends |
| D-AUTONOMY_CORE | 67 | import_depends,event,data,contract,config_depends |
| D-INTEGRATION | 60 | import_depends,data,config_depends,contract,event |
| D-INFRA_OPS | 53 | contract,event,data,config_depends |
| D-AUTONOMY_PERM | 45 | contract,import_depends,domain_dependency,event,data,config_depends |
| D-OPS | 34 | import_depends,contract,event,config_depends,data |
| D-FRONTEND | 29 | event,contract,config_depends,data |
| D-INTELLIGENCE | 23 | data,contract,config_depends,event |
| D-PF_CORE | 22 | data,event,contract |
| D-KNOWLEDGE | 17 | contract,data,event,config_depends |
| D-SIMULATION | 16 | data,config_depends,contract |
| D-PF_ALLOC | 14 | contract,data,event,config_depends |
| D-TRADING | 12 | import_depends |
| D-REPORTING | 12 | config_depends,event,data,contract |
| D-ML_SERVE | 11 | data,contract,event,config_depends |
| D-ALT_DATA | 10 | event,contract,data,config_depends |
| D-SELL_DECISION | 9 | data,event,contract |
| D-DATA_SEC | 7 | domain_dependency,event,contract,data |
| D-CROSS_ASSET | 7 | data,contract,event |
| D-DATA_GOV | 5 | data,config_depends,contract |
| D-GOV_AUDIT | 4 | import_depends |

## 域内依赖图

详见 [d_security_dependency.mmd](d_security_dependency.mmd)
