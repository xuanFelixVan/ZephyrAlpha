---
doc_type: domain_architecture_doc
title: D-INTEGRATION pipeline_routing架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-INTEGRATION pipeline_routing架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-INTEGRATION |
| 域名称 | pipeline_routing |
| 架构层 | L1_platform |
| 模块总数 | 706 |
| 设计态模块 | 416 |
| 原型态模块 | 223 |
| 生产态模块 | 62 |
| 容量 | 62/150 (正常) |
| 描述 | M1-M11双管线路由 |

## 模块清单

共 706 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-INTEGRATION/6-Month Data Retention 6个月数据保留 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2A + MCP Dual Protocol A2A+MCP双协议 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2A MCP Hybrid Orchestration A2A+MCP混合编排 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2A Message Encryption A2A消息加密 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2A Protocol Bridge A2A协议桥接 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2A Protocol Handler A2A协议处理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2A Protocol Integration A2A协议集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/A2AProtocolBridge A2A协议桥 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ACL Anti-Corruption Layer ACL防腐层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AI Gateway AI网关 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AI Security Boundary Execution Layer AI安全边界执行层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AI Track AI轨 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Fuzz Testing API模糊测试 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Gateway API网关 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Gateway Design API网关设计 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Gateway Four Layer Architecture API网关四层架构 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Gateway Layer API网关层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Gateway Unified Entry API网关统一入口 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Key 90-Day Auto Rotation API密钥90天自动轮换 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Key 90-Day Rotation API密钥90天轮换 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Key Encrypted Storage API密钥加密存储 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Lifecycle API生命周期 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Record Replay VCR API录制回放 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Routing Service Discovery API路由与服务发现 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Version Hard Constraint API版本管理硬约束 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/API Version Mismatch Reject API版本不匹配拒绝 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/APIDocumentation API文档 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/APIGatewayRequestRouted API网关请求路由 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Adapter Auto-Discovery 适配器自动发现 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Adapter Baseline Snapshot 适配器基线快照 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Adapter Manager 适配器管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Additive Change 非破坏性变更 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Agent Card Discovery Agent Card发现机制 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AgentAction Agent动作事件 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AkShare Crawler AkShare爬虫 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AkShare HTTP Crawler 另类数据源 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Architecture Governance Integration 架构治理集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Architecture as Code Integration 架构即代码集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Artifact Exchange Artifact交换 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Asynchronous Messaging 异步消息 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Audit Layer 审计层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Audit Log Required 审计日志必须 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Authentication Layer 认证层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Auto Integration Registry 自动集成注册表 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Auto-Scaling Integration 自动扩缩集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/AutoScaling 自动扩缩容 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Backpressure Contract 001 背压契约001 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Backpressure Contract 002 背压契约002 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Backpressure Contract 003 背压契约003 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/BackpressureManager 背压管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Baseline Snapshot Persistence 基线快照持久化 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Batch Import 批量导入 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Behavioral Admission Integration 行为准入门禁集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Blueprint-Architecture Bidirectional Mapping 蓝图架构双向映射 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Breaking Change 破坏性变更 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Bulkhead Isolation Pool 舱壁隔离池 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Bulkhead Isolation 舱壁隔离 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/CI/CDIntegration CI/CD集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/CLOSED 正常状态 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/CQRS Separation CQRS分离 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Capital Flow Behavior Analysis 资金行为分析 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Chaos Engineering Environment 混沌工程环境选择 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Circuit Breaker + Bulkhead 熔断器+舱壁隔离 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Circuit Breaker Layer 熔断层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Circuit Breaker Matrix 熔断器矩阵 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Circuit Breaker State Export 熔断器状态导出 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Circuit Breaker State 熔断器状态 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Claude API 克劳德API |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Client MCP客户端 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Closed Loop Manual Approval 闭环优化人工审批 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Closed State Retry Closed状态重试 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Cloud Backup Desensitization 云端冷备脱敏 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Compliance Gateway Embedded 合规网关嵌入 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Compliance Gateway Layer 合规网关层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Compliance Policy Integration 合规策略集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Component Reuse Manager 组件复用管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Config Git Versioning 配置Git版本化 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ConfigChanged 配置变更 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Consumer-Driven Contract Testing 消费者驱动契约测试 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Baseline Update 契约基线更新 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Drift 契约漂移 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Layer 契约层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Registry Version Query 契约注册表版本查询 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Registry 契约注册表 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Test Block Deploy 契约测试阻断部署 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Test Coverage 契约测试覆盖 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Contract Test Deploy Block 契约测试阻断部署 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ContractFrozen 契约冻结 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ContractVersionManager 契约版本管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ContractViolated 契约违反事件 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ContractViolationError 契约违反错误 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Cost-Aware LLM Routing 成本感知LLM路由 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Cross-Market Data Integrator 跨市场数据集成器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/D-INT-36 ArchitectureAsCode 架构即代码 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/D-INTEGRATION 集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Daily Mode 日频模式 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Consistency Guarantee 数据一致性保证 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Desensitization 数据脱敏 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Fetch Pool 数据拉取池 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Format Transformer 数据格式转换器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Freshness Grading 数据新鲜度分级 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Source Failure Degradation 数据源故障降级 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Source Manager 数据源管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Source Router 数据源路由 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Data Track 数据轨 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/DataSourceConnectorRegistry 数据源连接器注册中心 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/DeepSeek V4 Pro API 深度求索API |  | design_only | design | 0 | 0 |
| D-INTEGRATION/DepMap Integration DepMap集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Dependency Semantics Integration 依赖语义集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Deprecating Change Deprecating变更 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Desensitization Layer 脱敏层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Disaster Recovery State Reconstructability 灾备状态可重建 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Distributed Tracing OTel 分布式追踪OTel |  | design_only | design | 0 | 0 |
| D-INTEGRATION/DistributedTracePropagator 分布式追踪传播器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Dual Version Transition 双版本过渡期 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/E-0119 前端域→集成域依赖 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Email System 邮件系统 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Error Budget 误差预算 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Event Bus Manager 事件总线 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Event Sourcing 事件驱动+Event Sourcing |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Event-Driven 事件驱动 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/EventBusManager 事件总线管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/EventRoutingFailed 事件路由失败事件 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External API Metrics 外部API调用指标 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External API No Position Data 外部API禁止传输持仓 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External API Response Validation 外部API响应合理性校验 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External API Unified Gateway 外部API统一网关 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External System Adapter 外部系统适配器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External System Connector 外部系统连接器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External System Interaction Matrix 外部系统交互矩阵 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External System Isolation 外部系统故障隔离 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/External System Layer 外部系统层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ExternalAPIAccess 外部API访问 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/ExternalAPIEndpoint 外部API端点 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Factor Calculation MCP Server 因子计算MCP服务器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Fault Injection Test 故障注入测试 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Feature Flag Progressive Integration 功能开关渐进式集成 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/FeatureFlagManager 功能开关管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Four-Level Rate Limiting 四级限流架构 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Full Contract Test on Change 变更触发全量契约测试 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Full Sync After Recovery 灾备恢复全量同步 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Git Local Repository Git本地仓库 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Google A2A Protocol Google A2A协议 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/HALF_OPEN 半开试探状态 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Host MCP主机进程 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-02 iFind个人版数据字段覆盖度假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-03 iFind QPS上限维持20假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-04 RTX 3090显存24GB足够假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-05 外部LLM API服务商持续运营假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-06 微信Webhook接口不发生破坏性变更假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-07 Windows操作系统兼容性维持假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-08 家用网络30Mbps带宽足够假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-09 MCP 2026-07-28规范无重大破坏性变更假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-10 AkShare反爬策略不升级到完全封禁假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-11 证监会CN-003程序化交易细则不发生重大修订假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-12 Google A2A协议规范不发生破坏性变更假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IA-13 GitHub私有仓库持续可用且免费额度足够假设 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Idempotency Key Required 幂等Key必须 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Idempotency Key Value Object 幂等Key值对象 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Idempotency Key 幂等Key |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IdempotencyKeyInterceptor 幂等Key拦截器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IdempotencyKeyMissing 幂等Key缺失 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Independent Integration Architecture 独立集成架构 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Capacity Planning 集成容量规划与限流 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Closed Loop Optimization 集成闭环优化 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Closed Loop Optimization 集成闭环优化与自迭代 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Compliance Governance 集成合规治理 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Config Damage 集成配置损坏 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Config GitOps 集成配置GitOps |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Config Manager 集成配置管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Contract 集成契约 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Disaster Recovery 集成层灾备 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Legacy Issue Decision 集成遗留问题裁定17项 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Observability 集成可观测性 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Security Defense 集成安全纵深 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Smoke Test 集成冒烟测试 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Style 集成风格 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Test Framework 集成测试框架 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Integration Test Strategy 集成测试策略 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IntegrationHealthMonitor 集成健康监控 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/IntegrationTester 集成测试器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Interface Contract Governance 接口契约治理 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Internal Consumer Layer 内部消费层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Isolation Layer 隔离层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Isolation Manager 隔离管理器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Isolation Policy Bypass Prevent 隔离策略不可绕过 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Isolation Strategy 隔离策略 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/KS-L4 Reduced Operation KS-L4降额运行1天 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Key 90-Day Rotation 密钥90天轮换 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Kill-Switch Four-Level Cascade Kill-Switch四级阶梯 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Kill-Switch 紧急停机机制 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/Knowledge Graph MCP Server 知识图谱MCP服务器 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L0 Normal L0正常 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L00 Data Source Blueprint L00数据源蓝图 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L1 Contract Layer L1契约层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L1 Mild Degradation L1轻度降级 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L2 Mock Layer L2模拟层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L2 Moderate Degradation L2中度降级 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L3 Real Layer L3真实层 |  | design_only | design | 0 | 0 |
| D-INTEGRATION/L3 Severe Degradation L3重度降级 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 706 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SHARED | 73 | import_depends,contract,event,data |
| D-RISK | 69 | contract,data,event,config_depends |
| D-SECURITY | 60 | import_depends,contract,event,data,config_depends |
| D-SIGNAL | 41 | contract,config_depends,data,event |
| D-INTELLIGENCE | 37 | import_depends,contract,event,data,config_depends |
| D-MKT_DATA | 34 | config_depends,contract,data,event |
| D-INFRA_RUNTIME | 31 | domain_dependency,config_depends,contract,event,data |
| D-FACTOR | 24 | config_depends,contract,data,event |
| D-PF_CORE | 18 | data,contract,event,config_depends |
| D-DATA_ENG | 16 | event,config_depends,contract,data |
| D-KNOWLEDGE | 15 | event,contract,data,config_depends |
| D-EX_CORE | 15 | data,contract,config_depends,event |
| D-GOVERNANCE | 11 | config_depends,import_depends |
| D-EX_SOR | 11 | data,config_depends,contract,event |
| D-TRADING | 10 | import_depends,contract,event,data,config_depends |
| D-ML_TRAIN | 10 | contract,event,data,config_depends |
| D-POSITION | 4 | data,event,contract |
| D-GOV_AUDIT | 3 | import_depends |
| D-ML_SERVE | 2 | config_depends,contract |
| D-GOV_RULE | 2 | import_depends |
| D-AUTONOMY_CORE | 2 | import_depends |
| D-OPS | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 351 | contract,import_depends,test_depends,config_depends,event,data |
| D-COMPLIANCE | 118 | event,data,config_depends,contract |
| D-AUTONOMY_CORE | 76 | import_depends,contract,data,config_depends,event |
| D-TRADING | 55 | import_depends |
| D-INFRA_OPS | 38 | data,contract,config_depends,event |
| D-FRONTEND | 34 | contract,data,config_depends,event |
| D-OPS | 27 | import_depends,runtime,contract,event,config_depends,data |
| D-INFRA_RUNTIME | 26 | import_depends |
| D-SIMULATION | 15 | contract,import_depends,data,event,config_depends |
| D-GOV_RULE | 10 | import_depends |
| D-AUTONOMY_PERM | 10 | event,data,contract,config_depends |
| D-SHARED | 9 | contract,import_depends |
| D-CROSS_ASSET | 9 | contract,data,event,config_depends |
| D-PF_ALLOC | 8 | contract,data,event |
| D-REPORTING | 7 | event,data |
| D-INTELLIGENCE | 6 | import_depends |
| D-SELL_DECISION | 5 | data,event,contract |
| D-ALT_DATA | 5 | event,config_depends,contract |
| D-DATA_GOV | 4 | event,data,contract |
| D-SECURITY | 3 | import_depends |
| D-BEHAVIORAL_AUDIT | 3 | import_depends |
| D-GOV_DRIFT | 2 | import_depends |
| D-GOV_AUDIT | 2 | import_depends |
| D-DATA_SEC | 2 | event,contract |

## 域内依赖图

详见 [d_integration_dependency.mmd](d_integration_dependency.mmd)
