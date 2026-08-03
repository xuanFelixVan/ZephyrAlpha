---
doc_type: audit_report
title: 候选模块清单 — D_INFRA_OPS
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_INFRA_OPS 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **352** 条（原有 0 + harvest 352）。
> harvest 去重四态: likely_new=346 / uncertain=6

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0036 | 通知与告警 Alerting Notification | C 015：通知与告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0049 | MOD-INF-034 | **与ZephyrAlpha上岗测试系统的对接**：本系统的LLM路由消费ZephyrAlpha项目ModelProfiler(MOD-INF-034)的7维benchmark基线+ModelCapabilityExam(MOD-INF-0 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0050 | MOD-INF-036 | **与ZephyrAlpha上岗测试系统的对接**：本系统的LLM路由消费ZephyrAlpha项目ModelProfiler(MOD-INF-034)的7维benchmark基线+ModelCapabilityExam(MOD-INF-0 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0052 | MOD-INF-033 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0054 | MOD-INF-024 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0055 | MOD-INF-035 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0056 | MOD-INF-026 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0273 | MOD-MASTER-001 | > ⚠️ **计数说明**：D-ML-TRAIN域104个模块中✅82+❌22=104；D-ML-SERVE域MS-xx未标注15个模块中✅10+❌5=15，与域级裁定✅35+❌11=46存在1项计数差异(可能存在优先级交叉归类)；D-DA | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0289 | CI/CD Pipeline 管线 | / IO-01 / CI/CD Pipeline / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-005已建设 / GitHub Actions+门禁 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0290 | Monitoring System 监控系统 | / IO-02 / Monitoring System / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-015已建设 / Prometheus+Grafana / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0291 | Backup Manager 备份管理器 | / IO-03 / Backup Manager / ✅ 能建 / / 自动备份+增量+离线存储 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0292 | Disaster Recovery 灾难恢复 | / IO-04 / Disaster Recovery / ❌ 不能建 / / 门禁: 需双活基础设施 / 双活+故障切换 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0293 | Health Dashboard 健康仪表盘 | / IO-05 / Health Dashboard / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-015已建设 / 统一健康面板 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0294 | Log Aggregator 日志聚合器 | / IO-06 / Log Aggregator / ❌ 不能建 / / 门禁: 需ELK集群 / 集中化日志+全文检索 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0295 | Resilience Manager 弹性管理器 | / IO-07 / Resilience Manager / ❌ 不能建 / / 门禁: 需多实例+自动扩缩容 / 弹性伸缩+故障转移 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0296 | Network Manager 网络管理器 | / IO-08 / Network Manager / ❌ 不能建 / / 门禁: 需网络设备+VPN / DNS+负载均衡+防火墙 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0297 | IaC Manager IaC管理器 | / IO-09 / IaC Manager / ❌ 不能建 / / 门禁: 需Terraform/Pulumi+云环境 / 声明式基础设施 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0298 | Security Infra Manager 安全基础设施管理器 | / IO-10 / Security Infra Manager / ❌ 不能建 / / 门禁: 需WAF+IDS硬件 / WAF+IDS+密钥管理 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0299 | HPC Manager HPC管理器 | / IO-11 / HPC Manager / ❌ 不能建 / / 门禁: 需GPU集群 / GPU集群调度 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0300 | Deployment Manager 部署管理器 | / IO-12 / Deployment Manager / ❌ 不能建 / / 门禁: 需多实例环境 / Blue-Green+Canary / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0301 | Alert Manager 告警管理器 | / IO-13 / Alert Manager / ✅ 能建 / / 告警分级+降噪+升级 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0522 | 备份策略 Backup Strategy | 增量/日快照/周全量/配置备份+RTO/RPO | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0638 | Backup Manager 自动备份管理器 | 自动备份+增量引擎+加密+校验+恢复测试+保留策略 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0639 | Cold Data Archive Manager 冷数据归档管理器 | 冷数据归档存储+归档策略/压缩/检索/清理+生命周期 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0640 | 数据源可用性SLA追踪器 Data Source Availability SLA Tracker | 各数据源历史可用率+延迟统计+SLA达标率 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0641 | 存储成本量化核算器 Storage Cost Calculator | 热/温/冷各层存储成本/TB自动计算与对比 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0679 | 日快照恢复演练 Daily Snapshot Recovery Drill | 每周从日快照恢复前一交易日状态恢复时间<1s数据完整 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0680 | 盘中恢复演练 Intraday Recovery Drill | 每月模拟盘中崩溃从快照+事件回放恢复恢复时间<30s RPO=0 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0681 | 全量恢复演练 Full Recovery Drill | 每季度从空状态恢复到最新状态恢复时间<5min数据完整 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0682 | 审计重建演练 Audit Reconstruction Drill | 每半年重建指定历史时间点的完整状态与历史记录一致 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0903 | Shared Infrastructure 共享基础设施 | 共享基础设施(配置/日志/错误/事件总线/健康检查) | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0909 | Tool Scripts 工具脚本 | 工具脚本(scaffold/lock_files/ide_health等) | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0918 | Quantum-Classical Hybrid Computing Roadmap 量子-经典混合计算路线图 | 量子-经典混合计算路线图 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1238 | Cost Optimizer 成本优化器 | 云资源成本监控+成本分摊+资源利用率分析+成本预测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1443 | Agent RBAC / Permission Guard Agent RBAC/权限守卫器 | 七层纵深防御+RBAC+ABAC+零信任，蓝图已建设，≡D-AUTONOMY-01 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1771 | Communication Encryption Config 通信加密配置 | 归属D-INFRA；✅能建 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1902 | 数据血缘追踪 Data Lineage Tracking | 数据源→特征→因子→信号→策略→交易→PnL全链路可追溯 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1904 | AI API Cost Manager AI API成本管理器 | LLM API成本纳入预算管理超限自动降级 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1905 | Agent Communication Protocol Agent通信协议 | Agent间通信必须通过结构化消息协议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1906 | Capacity Assurance & SLI/SLO 容量保障与服务等级 | 学习系统关键操作必须满足SLI/SLO指标 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1909 | Model Profiler & Capability Exam 模型画像与能力考试 | LLM模型能力基线测量+多维度能力评估 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1950 | PIT Manager Point-in-Time管理器 | ├─ 与R-15 Point-in-Time门控/R-69 PIT Manager的边界：PIT门控是验证规则（确保无前瞻偏差），Feature Store是数据基础设施（提供PIT AS OF JOIN查询能力），PIT Manager是 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2005 | Pipeline编排器 Pipeline Orchestrator | 12. Pipeline编排器（v7.0新增，裁定✅R-89 / 项目内有蓝图MOD-INF-009但是没建设🔧） | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2006 | Saga事务编排 Saga Transaction Orchestration | 编排式Saga+协调式Saga+补偿事务任一步骤失败时执行补偿操作回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2007 | 可配置规则引擎 Configurable Rule Engine | YAML/DSL规则定义+热更新规则变更无需重启服务即可生效 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2028 | 数字孪生系列 Digital Twin Series | 依赖图/实时同步/混沌实验:系统级数字孪生(❌) | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2038 | LLM模型分级路由 LLM Model Tiered Routing | M1/M3/M7/M9四级模型路由按任务复杂度选择不同规模LLM(❌) | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2039 | Data Mesh 数据网格 | 域所有权/数据产品/联邦治理:去中心化数据架构(❌) | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2040 | CQRS/Event Sourcing模型 CQRS/Event Sourcing Model | 命令查询职责分离+事件溯源:读写分离+完整事件历史(❌) | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2107 | Observability 可观测性 | 横切层7可观测性OpenTelemetry+GAAT | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2138 | Agent 365 OTel Enterprise Pipeline Agent 365 OTel企业级管道 | Agent 365 OTel企业级管道MVP暂缓多机部署 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2184 | OpenTelemetry | > **设计哲学**：多Agent系统的可观测性是安全与治理的基础。2025-2026年行业实践（OpenTelemetry多Agent语义约定、GAAT治理感知遥测、Microsoft Agent Governance Toolkit ( | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2189 | Agent SRE Reliability Engineering Agent SRE可靠性工程 | Agent SRE可靠性工程SLO定义熔断器混沌实验 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2192 | Trace Hierarchy Model Trace层级模型 | Trace层级模型Root Span Agent Span LLM Span Tool Span | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2224 | Prometheus Prometheus监控系统 | / 系统可用率 / 交易时段≥99.99%/非交易≥99.9% / 日 / Prometheus / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2272 | eBPF eBPF无侵入Span补全 | eBPF无侵入Span补全可观测性技术 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2282 | Docker Docker容器 | Docker容器L2集成测试执行环境每日构建+每次PR | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2283 | W3C TraceContext W3C TraceContext追踪标准 | > **Flow ID传播（参考MAN+ESM, Adya 2026）**：借鉴MAN+ESM的Flow ID概念，本系统在§3.2消息格式的metadata中传播traceId（与W3C TraceContext惯例一致），实现全链路可追 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2346 | Observability Three Pillars 可观测性三支柱 | 可观测性三支柱Traces链路追踪7年+Metrics指标度量5年+Logs结构化日志7年 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2347 | Trace Hierarchical Model Trace层级模型 | Trace层级模型Root Span到Agent Span到LLM Span到Tool Span到Retriever Span到Rule Span到A2A Span | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2352 | Test Automation & CI/CD Integration 测试自动化与CI/CD集成 | 测试自动化与CI/CD集成5测试类型L1单Agent单元测试到L5行为测试触发条件执行环境通过标准失败处理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2388 | Disaster Recovery Level L6 灾备分级L6日志审计 | 灾备分级(L6日志审计)：RTO<240min, RPO≤24hour, 交易日志/操作日志/审计记录, 压缩归档+双副本。 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2408 | Key Observability Metrics 关键可观测性指标 | 关键可观测性指标7项Trace完整率+Agent决策延迟P99+A2A检查通过率+自治边界违规+LLM调用成本+串谋行为相关性+涌现行为检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3894 | 灾备3-2-1-1-0+D到E 灾备架构 | robocopy每小时增量RTO小于5min | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3912 | 灾备架构 灾备架构 Disaster Recovery Architecture | RTO/RPO分级故障切换数据恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3913 | D到E盘双副本策略 双副本架构 | robocopy每小时增量同步 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3915 | 数据恢复流程 数据恢复 Workflow | Redis Parquet模型配置多场景恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3916 | 灾备演练计划 灾备演练 Disaster Recovery Drill Plan | 每月每季度每半年演练频率 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3917 | 混沌工程实践 混沌工程 Chaos Engineering Practice | Netflix Chaos Monkey主动注入故障 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3927 | 变更管理 变更管理 Management | 灰度金丝雀扩大全量回滚审批 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3928 | 灰度发布流程 灰度发布 Workflow | 构建金丝雀1-5%扩大25-50%全量100% | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3929 | 金丝雀验证 金丝雀验证 Canary Verification | 功能性能错误率资源风控数据六维验证 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3930 | 回滚策略 回滚策略 Strategy | 金丝雀扩大全量配置依赖库多场景回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3931 | 依赖库升级流程 依赖库升级 Workflow | 安全评估沙箱审批备份灰度验证7步 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4001 | 双机热备 Active-Standby | 单机是单点故障双机热备不能建约束二 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4249 | Migration Strategy 迁移策略 | / migration_strategy.py / governance/ / 迁移策略 / ❌ 属于D-INFRA-OPS——迁移是运维基础设施域 / | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4517 | CI/CD Pipeline 持续集成部署流水线 | 持续集成/部署：构建器+测试编排器+部署器+回滚器+质量门禁 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4518 | Monitoring Stack 监控栈 | 监控栈：指标采集+日志收集+分布式追踪+告警引擎+仪表盘 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4519 | DR Manager 灾备管理器 | 灾备管理：故障检测+切换编排+数据同步+演练引擎+状态机 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4520 | Infrastructure as Code 基础设施即代码 | / D-INFRA-10 / Infrastructure as Code / 基础设施即代码：Terraform/Pulumi适配器+状态管理+漂移检测+计划预览 / P1 / ❌ / Terraform/Pulumi; IaC理论/声明 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4521 | Cybersecurity Shield 网络安全防护 | 威胁检测+漏洞扫描+入侵检测+WAF+密钥管理+事件响应 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4522 | Resilience Testing Engine 韧性测试引擎 | 故障注入器+爆炸半径控制+稳态假设+实验编排+报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4523 | Capacity Planner 容量规划器 | 容量需求预测+资源规划+扩展计划+容量报告+容量告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4524 | A-Share Intraday Monitor Dashboard Configurator A股盘中监控看板配置器 | 四类实时监控指标配置+版面布局+看板模板管理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4525 | Real-Time Dashboard Visual Renderer 实时仪表盘可视化渲染器 | 实时监控数据可视化渲染+图表类型自动选择+告警阈值可视化 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4526 | Infrastructure Health Patrol Inspector 基础设施健康巡检器 | 基础设施健康巡检+巡检项定义+巡检报告+巡检告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4527 | 模块隔离部署编排器 Module Isolation Deployment Orchestrator | 模块独立开发/测试/部署编排+依赖解析+部署顺序+故障隔离 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4528 | 组件复用注册中心 Component Reuse Registry Center | 可复用模块注册/发现/版本管理+接口标准化 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4529 | 开源框架评估与集成器 Integration | 开源框架评估/选型/版本兼容性检查/集成适配 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4530 | 统一交互入口管理器 Management | 统一交互入口+仪表盘/菜单导航/权限管理/用户配置 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4531 | 模块边界与依赖识别器 Module Boundary and Dependency Identifier | 分析现有模块结构+识别边界和关系+依赖图自动生成 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4532 | 系统集成测试编排器 Integration | 模块间集成测试+系统级测试+故障注入测试+测试报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4533 | 部署监控优化器 Monitoring | 系统部署+监控+性能优化+蓝绿部署+回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4534 | 五区域布局管理器 Management | 五区域布局+NozyIO可视化编辑系统集成+旧版布局兼容迁移 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4535 | SLA监控与保障器 | / D-INFRA-49 / SLA监控与保障器 / SLA监控与保障器：7×24稳定运行+数据流延迟<1s+按钮≤100ms+页面≤500ms+查询≤1s的SLA监控+告警+自动恢复 / P1 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4536 | 复杂操作进度提示器 Complex Operation Progress Prompter | 复杂操作进度追踪+进度条渲染+取消支持+超时处理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4537 | 故障自动检测诊断器 Fault Auto Detection Diagnoser | 故障自动检测和诊断+异常识别+根因分析+诊断报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4538 | 五区域布局渲染引擎 Engine | 五区域布局渲染+区域尺寸调整+区域折叠+布局持久化 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4539 | 系统级导航与功能入口管理器 Management | 顶部导航栏+系统级功能入口+快捷键+最近访问 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4540 | 多标签页管理器 Management Tag | 多标签页布局+标签页切换+标签页状态保存+标签页恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4541 | 可拖拽面板引擎 Engine | 可拖拽面板+面板布局自定义+布局保存+布局恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4542 | 桌面端大屏优化器 Desktop Large Screen Optimizer | 桌面端大屏幕优化+分辨率适配+DPI缩放+多显示器支持 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4543 | 桌面端专属交互优化器 Desktop Exclusive Interaction Optimizer | 桌面端交互优势利用+键盘快捷键+鼠标手势+右键菜单 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4544 | 分阶段实施编排器 Phased Implementation Orchestrator | 5阶段实施计划+阶段依赖+阶段门禁+阶段验收 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4545 | 层间依赖与部署顺序编排器 Inter-layer Dependency and Deployment Order Orchestrator | 12层部署顺序+层间依赖解析+并行部署+部署验证 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4546 | 系统资源监控告警器 Monitoring Alerting | CPU+内存+磁盘+网络4维资源监控+阈值告警+自动扩容 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4547 | Streamlit快速原型开发器 | / D-INFRA-66 / Streamlit快速原型开发器 / Streamlit快速原型开发器：Streamlit Web界面快速原型+数据展示+交互控件+实时更新 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4548 | PyQt5桌面GUI集成器 | / D-INFRA-67 / PyQt5桌面GUI集成器 / PyQt5桌面GUI集成器：PyQt5 VeighNa启动器界面+桌面集成+系统托盘+原生通知 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4549 | 渐进式增强管理器 Management | 基础功能先行+高级功能后续+功能开关+灰度发布+回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4550 | 文档中心索引管理器 Management Index | / D-INFRA-70 / 文档中心索引管理器 / 文档中心索引管理器：docs文档中心+INDEX.md快速导航+System_Manifest系统清单+API_Contract接口契约+7子目录文档管理 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4551 | 项目目录结构生成器 Generator Directory | / D-INFRA-71 / 项目目录结构生成器 / 项目目录结构生成器：quant_system_v4项目目录结构自动生成+目录校验+目录规范检查+目录初始化 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4552 | 模块实现状态追踪器 State | 8模块实现状态追踪+已实现/规划中/开发中+状态变更记录 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4553 | 依赖版本兼容性检查器 Dependency Version Compatibility Checker | 8库版本兼容性检查+版本冲突检测+升级建议+安全漏洞检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4554 | 目录结构规范校验器 Checker Directory | 目录结构规范校验+必需目录检查+目录权限检查+目录命名规范 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4555 | 文件命名规范检查器 File | 文件命名规范检查+模块/策略/因子/测试/配置5类命名规则 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4556 | 优先级自动评估器 Priority Auto Evaluator | 模块优先级自动评估+依赖分析+影响范围+开发成本+优先级建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4557 | 性能基准测试器 Performance | / D-INFRA-83 / 性能基准测试器 / 性能基准测试器：性能基准测试+启动时间+响应时间+吞吐量+资源使用率+基准报告+回归检测 / P1 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4558 | Docker容器化研究环境管理器 | / D-INFRA-85 / Docker容器化研究环境管理器 / Docker容器化研究环境管理器：Docker容器化技术+Python/R环境配置+VS Code/Jupyter Lab+Git版本控制 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4559 | CI/CD流水线集成器 | / D-INFRA-86 / CI/CD流水线集成器 / CI/CD流水线集成器：pytest单元测试+CI/CD流程+自动构建+自动部署+自动测试 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4560 | Ant Design+ECharts可视化组件集成器 | / D-INFRA-88 / Ant Design+ECharts可视化组件集成器 / Ant Design+ECharts可视化组件集成器：Ant Design+Element Plus统一可视化组件库+ECharts+D3.js交互式图 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4561 | 硬件资源优化建议器 Hardware Resource Optimization Advisor | / D-INFRA-91 / 硬件资源优化建议器 / 硬件资源优化建议器：CPU优化+内存管理+GPU加速+存储优化+psutil+Node Exporter资源监控 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4562 | 架构性能瓶颈识别器 Performance | 性能分析与瓶颈识别+系统可靠性评估+扩展性优化+优化建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4563 | NozyIO多语言代码编辑集成器 | / D-INFRA-94 / NozyIO多语言代码编辑集成器 / NozyIO多语言代码编辑集成器：支持Python/R/SQL多语言编辑+模块间跳转+系统命令执行+Docker容器管理 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4564 | 系统健康度评分器 System Health Score Rater | 整体运行状态监控+关键指标展示+系统健康度评分+健康度趋势 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4565 | 个性化界面配置管理器 Management Config | 模块快速访问+功能菜单管理+常用功能快捷键+个性化界面配置 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4566 | 模块实现进度追踪器 Module Implementation Progress Tracker | 高优先级模块实现进度追踪+阶段完成度+交付物检查+延期预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4567 | 模块间集成测试计划器 Integration | 各模块开发完成后的集成测试计划+集成顺序+集成接口 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4568 | 性能测试Locust/JMeter集成器 | / D-INFRA-99 / 性能测试Locust/JMeter集成器 / 性能测试Locust/JMeter集成器：Locust+JMeter性能测试+大数据处理场景+性能基准+性能报告 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4569 | ELK日志管理器 | / D-INFRA-100 / ELK日志管理器 / ELK日志管理器：ELK Stack完整日志收集+分析+可视化+日志搜索+日志告警+日志归档 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4570 | 灾备方案管理器 Management | / D-INFRA-101 / 灾备方案管理器 / 灾备方案管理器：pgBackRest+Redis Sentinel数据备份和恢复机制+备份策略+恢复验证+灾备演练 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4571 | 预测性维护与自愈修复器 Predictive Maintenance and Self-Healing Repairer | / D-INFRA-103 / 预测性维护与自愈修复器 / 预测性维护与自愈修复器：基于历史数据预测系统故障+ML预测模型+自动修复脚本+自愈验证 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4572 | 12层架构与九大平台映射分析器 Analyzer | 详细对比12层架构与九大核心平台+映射关系+差距识别 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4573 | 文档链接有效性检查器 Document Link Validity Checker | / D-INFRA-109 / 文档链接有效性检查器 / 文档链接有效性检查器：提取所有链接+验证内部链接+curl/wget检查外部链接+链接报告 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4574 | 文档单一信息源管理器 Management | / D-INFRA-110 / 文档单一信息源管理器 / 文档单一信息源管理器：核心文档权威技术描述+其他文档引用关联+信息源注册+信息源版本 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4575 | 数据库备份与恢复方案器 Database | 数据备份与恢复+备份策略+恢复验证+灾备演练+备份加密 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4576 | 模块依赖分析器 Analyzer | 模块间依赖关系图+依赖冲突检测+循环依赖识别+依赖版本管理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4577 | 开源组件评估器 Open Source Component Evaluator | 开源许可证合规检查+组件安全漏洞扫描+组件活跃度评估 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4578 | 目录结构验证器 Validator Directory | / D-INFRA-116 / 目录结构验证器 / 目录结构验证器：目录规范校验+路径引用完整性检查+配置文件路径一致性+硬编码路径扫描 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4579 | 配置迁移工具 Config Utils | / D-INFRA-117 / 配置迁移工具 / 配置迁移工具：docker-compose配置更新+启动脚本更新+环境变量迁移+文档链接更新 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4580 | 交互界面迁移方案器 Interactive Interface Migration Planner | NozyIO四层架构迁移路径+界面组件映射+交互逻辑迁移 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4581 | 阶段交付物定义器 Phase Deliverable Definer | / D-INFRA-121 / 阶段交付物定义器 / 阶段交付物定义器：各阶段交付物清单+交付物质量标准+交付物评审流程+阶段验收标准 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4582 | 自动化代码审查流水线 Automated Code Review Pipeline | / D-INFRA-122 / 自动化代码审查流水线 / 自动化代码审查流水线：Ruff+mypy+Bandit集成+审查结果聚合+审查报告生成+审查规则自定义 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4583 | 代码质量度量看板 Code Quality Metrics Dashboard | 代码复杂度趋势+测试覆盖率趋势+技术债务追踪+代码重复率监控 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4584 | 主题与样式引擎 Engine | / D-INFRA-124 / 主题与样式引擎 / 主题与样式引擎：主题切换+色彩方案管理+字体方案管理+暗色模式+自定义主题导入导出 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4585 | 交互反馈系统 Interactive Feedback System | / D-INFRA-125 / 交互反馈系统 / 交互反馈系统：操作反馈组件+错误提示组件+加载状态组件+操作确认组件+通知消息组件 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4586 | 可视化组件库 Visualization Component Library | / D-INFRA-126 / 可视化组件库 / 可视化组件库：K线图组件+折线图组件+柱状图组件+饼图组件+热力图组件+数据表格组件 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4587 | 文档一致性校验器 Checker | / D-INFRA-127 / 文档一致性校验器 / 文档一致性校验器：文档编号重复检测+版本号格式校验+术语一致性检查+结构规范验证 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4588 | 文档完整性扫描器 Document Completeness Scanner | / D-INFRA-128 / 文档完整性扫描器 / 文档完整性扫描器：README缺失检测+文档与代码结构比对+缺失文档识别+文档覆盖率统计 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4589 | 审计报告自动生成器 Generator Audit Report | / D-INFRA-129 / 审计报告自动生成器 / 审计报告自动生成器：目录结构评估+文档质量评分+一致性检测+价值评估+改进建议生成 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4590 | 遗产代码迁移适配器 Adapter | / D-INFRA-130 / 遗产代码迁移适配器 / 遗产代码迁移适配器：旧接口适配+数据格式转换+配置映射+功能等效验证+迁移进度追踪 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4591 | 环境初始化一键脚本 Environment | 自动完成venv创建、依赖安装、配置生成 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4592 | 数据迁移模块 Data Migration Module | 数据结构变更时的自动迁移工具 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4593 | CI/CD流水线编排 | 自动化构建测试部署流水线 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4594 | 依赖冲突检测 Dependency Conflict Detection | 模块间依赖的循环检测与冲突预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4595 | 里程碑健康检查 Milestone Health Check | 阶段完成前的质量门禁检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4596 | 交付物自动检查 Deliverable Auto Check | 交付物完整性与质量的自动验证 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4597 | 测试报告生成 Report | 自动化测试报告生成与通知 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4598 | 日志聚合模块 Aggregator Logger | 分布式日志的聚合查询与全文检索 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4599 | 审计日志分析 Audit Logger | 审计日志的自动化分析与异常行为检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4600 | 模块依赖图生成 Module Dependency Graph Generator | 自动生成模块依赖关系图与循环依赖检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4601 | 蓝绿部署策略 Strategy | 零停机部署的蓝绿切换机制 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4602 | 配置漂移检测 Config | 运行环境与基准配置的偏差检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4603 | 灰度发布控制器 Canary Release Controller | 新版本的渐进式灰度发布 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4604 | 开发环境标准化 Environment | 开发环境的统一容器化与一致性保障 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4605 | 接口健康探测 Interface | 接口可用性的定期探测与告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4606 | 依赖冲突检测器 Detector | 检测包版本冲突与兼容性问题 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4607 | 容器健康检查 Container Health Check | 容器级别的健康探针与自动重启 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4608 | 通信性能监控模块 Monitoring Performance | 监控模块间通信延迟和吞吐量 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4609 | 接口性能监控 Monitoring Interface Performance | API响应时间与错误率监控 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4610 | 容器资源限制 Container Resource Limit | 内存/CPU限制配置与OOM保护 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4611 | 日志异步写入 Logger Async | 日志写入的性能优化与批量刷盘 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4612 | 部署性能基准 Performance | 部署后自动性能基准测试 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4613 | 流水线性能监控 Monitoring Performance | 流水线各阶段耗时监控与瓶颈定位 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4614 | 配置模板生成器 Generator Config | 根据.env.example自动交互式生成.env | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4615 | 交付物模板管理 Management | 交付物文档模板的统一管理与版本控制 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4616 | 测试环境管理 Management Environment | 测试环境的配置隔离与数据准备 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4617 | 配置变更审计 Audit Config | 配置变更的审计追踪与回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4618 | 容器安全扫描 Security | Docker镜像安全漏洞扫描 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4619 | 密钥轮换模块 Key Rotation Module | API密钥的定期自动轮换与无缝切换 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4620 | 部署安全扫描 Security | 部署前的安全漏洞与配置扫描 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4621 | 日志脱敏模块 Logger | 敏感信息的自动脱敏与过滤 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4622 | 事件总线监控 Monitoring Event | 事件吞吐量/延迟/积压的监控指标 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4623 | 工作流健康检查 Workflow Health Check | 工作流运行状态的定期巡检 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4624 | 报告导出模块 Report | 报告导出为PDF/HTML/Excel格式 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4625 | 自定义监控面板 Monitoring | 用户自定义监控视图与告警阈值 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4626 | 自定义检查项 Custom Check Item | 用户自定义健康检查规则与阈值 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4627 | 自定义统计指标 Custom Statistics Metric | 用户自定义统计指标与可视化 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4628 | 交互设计规范合规检查器 Compliance | 桌面端适配验证+术语一致性检查+设计规范覆盖率 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4629 | 文件智能解析器 Parser File | / D-INFRA-204 / 文件智能解析器 / 文件智能解析器：PDF/DOC/Excel/CSV/JSON/YAML解析+关键信息提取+结构化转换 / P2 / ❌ / — | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4630 | 自动化运维执行器 Execution Operations | 健康状态巡检+性能优化自动执行+故障自愈+安全补丁自动应用 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4631 | 代码块语法校验器 Checker | Python/SQL语法自动校验 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4632 | Mermaid流程图渲染器 | 流程图语法解析与预览 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4633 | Markdown表格校验器 | 表格格式规范检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4634 | 树状图自动生成器 Generator | 从文档结构自动解析生成 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4635 | 层级深度校验器 Checker | 层级完整性与深度规范检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4636 | 节点关联分析器 Analyzer Node | 节点间依赖与引用关系分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4637 | 树状图差异对比器 Tree View Diff Comparator | 版本间结构差异对比 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4638 | 优先级动态调整器 Priority Dynamic Adjuster | 基于依赖关系的优先级自动调整 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4639 | 模块依赖关系图 Module Dependency Relationship Graph | 模块间依赖可视化与冲突检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4640 | 开发进度追踪器 Development Progress Tracker | 任务进度实时追踪与偏差预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4641 | 验收标准量化器 Acceptance Criteria Quantifier | 验收标准可量化指标定义 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4642 | 里程碑风险预警 Risk | 里程碑延期风险自动预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4643 | 阶段交付物检查器 Phase Deliverable Checker | 各阶段交付物完整性检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4644 | 进度偏差分析器 Analyzer | 实际进度与计划偏差分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4645 | Docker健康检查器 | 容器状态自动巡检与告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4646 | SSL证书自动更新 | 镜像源证书自动管理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4647 | 日志智能分析器 Analyzer Logger | 日志异常模式自动识别 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4648 | 内存泄漏检测器 Detector Memory | 内存使用趋势监控与泄漏预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4649 | 运维操作审计 Audit Operations | 运维操作记录与审计追踪 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4650 | 流水线执行监控 Execution Monitoring | 各阶段执行状态与耗时监控 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4651 | 数据延迟检测 Latency | 数据更新延迟检测与告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4652 | 布局持久化 Layout Persistence | 用户自定义布局保存与恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4653 | 响应式断点适配 Response | 不同分辨率下的布局自适应 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4654 | 面板拖拽状态同步 Sync State | 多面板拖拽布局状态实时同步 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4655 | 全局快捷键管理 Management | 系统级快捷键注册与冲突检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4656 | 标签页状态管理 Management State Tag | 标签页数据缓存与恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4657 | 拖拽面板布局引擎 Engine | 面板自由拖拽与吸附布局 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4658 | 文件上传预览 File | 上传文件内容预览与格式校验 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4659 | 导航权限控制 Navigation Permission Control | 基于角色的导航菜单动态渲染 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4660 | 表单自动保存 Table | 表单数据定时自动保存与草稿恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4661 | 操作撤销重做栈 Operation Undo Redo Stack | 用户操作撤销与重做历史管理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4662 | 交互操作埋点 Interactive Operation Tracking | 用户交互行为采集与分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4663 | 图表主题动态切换 Table | 明暗主题与色盲友好配色 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4664 | 大数据量图表优化 Table | 百万级数据点降采样与虚拟滚动 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4665 | 图表导出与分享 Table | 图表PNG/SVG导出与链接分享 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4666 | 实时数据流图表 Real-time Table | 流式数据实时追加渲染 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4667 | 学习进度量化评估 Learning Progress Quantitative Assessment | 学习效果多维量化评分 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4668 | 运维变更审批流 Operations | 自动化运维变更审批与回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4669 | React组件库定制 | Ant Design主题定制与业务组件封装 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4670 | ECharts大规模数据渲染 | 百万级数据点高性能渲染 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4671 | 无障碍访问适配 Accessibility Adaptation | 键盘导航与屏幕阅读器支持 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4672 | 前端性能基准测试 Frontend Performance | 前端渲染性能基准与回归检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4673 | 前端安全审计 Audit Security Frontend | XSS/CSRF防护与依赖漏洞扫描 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4674 | 文档状态变更通知与依赖影响分析器 Analyzer Notification State | 文档状态变更时自动通知引用模块+依赖链影响范围分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4675 | 文档完整性自动化校验器 Checker | 检查标记为完整的章节是否真实包含所有必需内容字段 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4676 | 文档版本依赖一致性检查器 Document Version Dependency Consistency Checker | 多章节共享同一源文件时的内容一致性检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4677 | 功能废弃影响范围追踪器 Feature Deprecation Impact Scope Tracker | 被标记为未实现的功能的上游依赖和下游消费方追踪 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4678 | 技术栈版本兼容性矩阵自动检测器 Detector | 13类技术版本组合的自动兼容性检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4679 | 技术栈技术债务追踪器 Tech Stack Technical Debt Tracker | 小众/老旧技术的技术债务追踪+社区活跃度+替代方案评估 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4680 | 开发时间预算与实际偏差追踪器 Development Time Budget vs Actual Deviation Tracker | 开发时间预算追踪+实际耗时偏差分析+偏差预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4681 | 优先级冲突解决器 Priority Conflict Resolver | 多个P0功能资源争抢时的冲突检测+协调策略+资源分配 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4682 | 优先级时间预算与延期预警器 Priority Time Budget and Delay Warmer | P1本周完成/P2有时间再做的自动时间追踪+延期预警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4683 | 阶段门禁自动验证器 Validator | 各阶段完成条件自动验证+交付物检查+门禁通过判定 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4684 | 跨模块阶段协调器 Cross-Module Phase Coordinator | 4个模块阶段计划的隐式依赖检测+协调+冲突解决 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4685 | 阶段门禁检查器 Phase Gate Checker | 阶段完成后的门禁检查清单+完成标准判定+切换审批+回退机制 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4686 | 阶段交付物验收清单生成器 Generator | 各阶段交付物验收标准模板+验收流程编排+验收报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4687 | 阶段资源分配与调度器 Scheduler | 各阶段人力资源+计算资源+时间资源分配+冲突检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4688 | 阶段过渡触发器 Phase Transition Trigger | 研究→回测→模拟→实盘的阶段过渡条件判定+触发机制 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4689 | 技术选型加权评分器 Technology Selection Weighted Scorer | 多维度权重配置+自动评分+选型报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4690 | 技术选型决策记录追踪器 Technology Selection Decision Record Tracker | 选型理由+时间+参与者的完整审计记录 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4691 | 技术选型决策框架 Technology Selection Decision Framework | 统一技术选型评估标准+评分模型+决策模板+加权评分 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4692 | 开源项目许可证兼容性检查器 Open Source Project License Compatibility Checker | 开源项目许可证兼容性检查+GPL类许可证影响评估 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4693 | KrakenD/Kong替代API网关评估 | 高性能场景下专业API网关替代评估+对比报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4694 | 技术栈冗余检测与收敛建议器 Tech Stack Redundancy Detection and Convergence Advisor | 技术栈冗余检测+收敛建议+合并方案 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4695 | 技术栈版本兼容性矩阵检查器 Tech Stack Version Compatibility Matrix Checker | 各技术版本交叉兼容性自动校验+兼容性报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4696 | 技术栈废弃预警器 Tech Stack Deprecation Warmer | 开源项目停止维护/版本过期自动提醒+替代方案推荐 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4697 | 技术栈许可证合规检查器 Compliance | 各依赖库开源协议兼容性扫描+合规报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4698 | 12层架构健康检查与故障隔离器 12-Layer Architecture Health Check and Fault Isolator | 每层健康状态检查+层间依赖健康传播+故障隔离 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4699 | 路线图版本差异对比器 Roadmap Version Diff Comparator | 不同版本路线图变更可视化+差异高亮+变更日志 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4700 | 里程碑依赖图自动生成器 Generator | 阶段间依赖关系自动拓扑展示+依赖分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4701 | 交付物模板标准化器 Deliverable Template Standardizer | 各阶段交付物清单模板复用+模板管理+模板版本 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4702 | 命名规范自动修复建议器 Naming Convention Auto Repair Advisor | 违规文件自动推荐修正名称+批量重命名建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4703 | 批量重命名脚手架生成器 Generator Batch | 基于命名规范的批量文件重命名脚本生成 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4704 | 命名规范CI门禁集成器 | git commit前自动检查命名合规+CI集成 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4705 | 流水线执行延时统计分析器 Analyzer Execution | 各环节实际耗时vs计划耗时偏差统计+趋势分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4706 | 流水线执行时间偏差告警器 Execution Alerting | 实际执行时间与计划偏差超过阈值告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4707 | 流水线执行日报自动生成器 Generator Execution | 每日流水线执行摘要+异常+趋势报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4708 | 依赖版本自动升级建议器 Dependency Version Auto Upgrade Advisor | 自动检测并建议最优升级版本+升级时机+兼容性检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4709 | 导航状态持久化与恢复器 State | 用户导航位置+展开状态保存与恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4710 | 导航使用热力图生成器 Generator | 各导航项点击频次+路径分析+使用统计 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4711 | 表单Schema版本管理器 | 表单字段定义版本追踪+向下兼容+版本回滚 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4712 | 表单草稿自动保存与恢复器 Table | 用户输入内容定时自动存储+意外关闭恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4713 | 按钮状态机管理器 State Machine Management | 按钮禁用/加载中/成功/失败状态自动流转控制 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4714 | 图表主题标准化导出导入器 Importer Table | 主题配置JSON序列化+跨实例共享+主题市场 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4715 | 色盲友好配色自动验证器 Validator | 配色方案无障碍合规性检查+色盲模式切换 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4716 | 数据格式国际化本地化器 Local | 金额/百分比/时间格式按地域自动切换 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4717 | 表格列配置持久化器 Config Table | 用户自定义列宽/排序/显隐状态保存与恢复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4718 | 交互方式使用统计热力图 Interaction Method Usage Statistics Heatmap | 各交互模式使用频率+场景+效果量化对比 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4719 | 交互方式成本效率分析器 Analyzer | 语音/文字/图形各方式耗时与准确率对比 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4720 | 辅助效果量化评估器 Helper | 辅助前后用户操作效率对比统计+效果报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4721 | 自动化运维变更影响预分析器 Analyzer Operations | 运维变更前自动评估影响范围+风险分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4722 | 布局版本迁移转换器 Converter | 旧版布局到新版布局的自动映射与转换工具 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4723 | 协作过程动画回放器 Collaboration Process Animation Player | 历史人机协作步骤的动画式回溯查看 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4724 | Pipeline节点健康度探针 | 各环节存活/延迟/吞吐量实时检测+健康评分 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4725 | Pipeline吞吐量瓶颈分析器 | 各环节处理能力对比+瓶颈定位+优化建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4726 | 验证流程定制化编辑器 Workflow | 允许用户自定义验证步骤与顺序+流程模板 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4727 | 验证流程耗时基准器 Workflow | 各验证环节耗时基线建立+退化检测+优化建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4728 | 树状图节点实时搜索与过滤器 Filter Real-time Node | 按关键字/层级快速定位节点+过滤 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4729 | 树状图版本差异可视化器 Tree View Version Diff Visualizer | 两版本树状图结构变更高亮对比+差异报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4730 | 存储层性能基准测试器 Storage Performance | 各层实际读写延迟/吞吐量基准测试+退化检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4731 | 前端组件渲染性能监控器 Monitor Frontend Performance | 组件加载/更新/卸载耗时自动采集+告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4732 | 布局组件依赖关系检测器 Detector | 组件间调用/通信依赖自动识别+可视化 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4733 | 可视化组件注册中心 Visualization Component Registry Center | 组件版本/依赖/兼容性/文档统一管理 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4734 | 组件使用频次统计数据采集器 Component Usage Frequency Statistics Collector | 各组件渲染频次+耗时+错误率统计 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4735 | 数据流断点调试器 Data Flow Breakpoint Debugger | 数据流转中途暂停+检查+修改+继续 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4736 | 部署架构漂移检测器 Detector | 实际部署拓扑与蓝图文档差异自动比对+告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4737 | 部署依赖顺序校验器 Checker | 各层部署顺序+依赖关系自动检查+冲突检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4738 | pre-commit git钩子自动配置器 | 静态检查工具自动注册到pre-commit | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4739 | CI管道命令封装脚本 | 统一命令行接口+参数配置+结果格式化输出 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4740 | mypy增量类型检查模式 | 只检查git变更文件而非全量+增量检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4741 | 目录结构一致性巡检器 Directory | 实际目录vs文档定义目录差异告警+修复建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4742 | 目录模板快速初始化脚手架 Directory | new project一键创建标准化目录+模板文件 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4743 | 新模块子模块脚手架自动生成器 Generator | 基于规范的目录+模板文件一键创建 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4744 | 文档结构导航地图自动生成器 Generator | 基于章节层级自动生成交互式导航树 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4745 | 文档章节链接有效性批量检查器 Batch | 交叉引用链接自动扫描+断链修复 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4746 | 目录迁移影响预分析器 Analyzer Directory | 目录结构调整对配置文件/代码路径/依赖的影响分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4747 | 目录迁移回滚方案器 Directory | 目录结构调整失败后自动恢复到原始状态 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4748 | 监控方案迁移路径规划器 Monitoring Path | 从自研到Grafana的迁移方案+数据迁移+仪表板导入 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4749 | 监控阈值自适应调整器 Monitoring | 根据系统运行状态自动调整监控阈值+合理性评估 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4750 | 性能指标SLA实时仪表板 | 性能指标实时仪表板+SLA达标率+趋势分析 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4751 | 性能基准回归检测器 Detector Performance | 每次代码变更后的性能基准回归测试+退化检测 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4752 | 异常使用统计与热点分析器 Analyzer | 异常使用频率统计+分布分析+趋势+热点识别 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4753 | 多数据库SLA监控与告警器 | 多数据库SLA监控+查询延迟+同步延迟+备份恢复成功率 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4754 | 实验追踪方案决策记录器 Experiment Tracking Scheme Decision Recorder | 记录选择wandb而非自研的决策依据+切换条件+回退策略 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4755 | 实验追踪方案切换触发器 Experiment Tracking Scheme Switch Trigger | wandb服务中断时的切换条件+本地备选方案+数据同步 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4756 | 指标阈值动态调整与合理性评估器 Metric Threshold Dynamic Adjustment and Rationality Evaluator | 根据系统运行数据动态调整指标阈值+合理性评估 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4757 | 业务指标量化与追踪器 Business Metric Quantifier and Tracker | 将定性业务指标转化为可量化指标+计算公式+数据采集 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4758 | API文档自动版本同步器 | API实现变更时文档自动同步更新+版本对应 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4759 | 字段类型变更影响分析器 Analyzer Field | 表字段类型修改影响下游查询分析+影响报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4760 | 模型文件路径安全性检查器 Security Model File Path | 路径穿越+越权访问防护+安全检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4761 | 模型推理性能基准测试器 Inference Model Performance | 每次推理耗时基准记录+退化告警+性能趋势 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4762 | Agent调用审计日志器 | 每次Agent决策/操作的完整记录+审计查询 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4763 | 配置变更审计日志追踪器 Audit Logger Config | 每次配置修改的差异/时间/操作人记录 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4764 | 委员会决策耗时监控器 Monitor | 各委员决策延迟统计+超时告警+性能报告 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4765 | 决策流节点耗时瓶颈分析器 Analyzer Node | 各决策环节CPU/IO耗时分布+瓶颈定位 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4766 | 决策路径频次统计器 Path | 历史决策路径选择频次+成功率分析+优化建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4767 | 元数据Schema迁移管理器 | 因子元数据字段变更时的自动迁移脚本生成 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4768 | wandb使用成本追踪器 | API调用次数+存储用量+费用自动统计+预算告警 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4769 | 知识来源质量评分器 Knowledge | 各来源知识质量/准确率/时效性评分+评分更新 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4770 | Layer文档位置索引与完整性检查器 | 各Layer文档位置自动索引+完整性检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4771 | 架构版本演进追踪器 Architecture Version Evolution Tracker | Layer 0-7架构版本变更记录+差异对比+兼容性检查 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4772 | MLflow性能基准测试器 | MLflow性能基准定义+退化检测+优化建议 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4773 | 桌面端多显示器布局管理 Management | 多显示器扩展桌面布局与窗口位置记忆 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4774 | 技术债务追踪 Technical Debt Tracking | 开发过程中技术债务的记录和追踪机制 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4775 | 日志保留与归档策略 Strategy Logger | 不同级别日志的保留期限和归档策略 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4776 | 知识生命周期管理 Lifecycle Knowledge Management | 知识的时效性检测与自动归档 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4777 | 系统版本兼容 System Version Compatibility | 系统版本间的兼容性保障与迁移路径 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4778 | 架构决策记录 Architecture Decision Record | 架构决策的记录追踪与评审 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4779 | 监控事件聚合器 Monitoring Aggregator Event | 各域→INFRA监控事件聚合与降采样 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4780 | 数据质量监控桥接器 Data Quality Monitoring | D-DATA→D-INFRA数据质量监控桥接 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4781 | 信号质量评估消费桥接器 Signal | D-SIGNAL→D-INFRA信号质量监控桥接 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4782 | 风控事件告警桥接器 Risk Control Alerting Event | D-RISK→D-INFRA风控告警桥接 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4783 | 灰度发布与蓝绿部署框架 Canary Release and Blue-Green Deployment Framework | 系统更新的灰度发布与蓝绿部署编排 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4784 | 统一健康检查框架 Unified Health Check Framework | 各子模块健康检查端点的统一注册与聚合 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4785 | 跨域向后兼容性检查器 Cross-Domain Backward Compatibility Checker | / D-INFRA-473 / 跨域向后兼容性检查器 / 新版本发布前自动检查与旧版本数据/接口/配置/事件格式的兼容性 / P2 / ❌ / 第六轮迁移进化/运维数据管理推导 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4786 | 动态韧性调整器 Dynamic Resilience Adjuster | 基于运行时状态的韧性动态调整+自适应优化 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4787 | 优雅降级规划器 Fallback | 依赖故障时优雅降级路径规划+策略选择+执行编排 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4788 | 依赖图韧性评分增强 Dependency Graph Resilience Score Enhancement | 5维韧性评分增强+动态调整+预测性评分 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4789 | 韧性评分标准化器 Resilience Score Standardizer | 韧性评分标准化定义+跨系统可比+基准建立 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4796 | OpenTelemetry Collector OpenTelemetry收集器 | / OpenTelemetry Collector / 本地进程部署 / 接收OTLP协议，导出至SQLite(热)+Parquet(冷)；MVP使用JSON文件导出，未来升级门禁：多机部署+企业级监控需求+有第二位开发人员加入时可接入Ag | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4797 | Prometheus+Grafana监控栈 Prometheus Grafana Monitor Stack | / Prometheus + Grafana监控栈 / 本地单实例 / Prometheus采集Agent Metrics（Agent延迟、协作成功率、成本、反思有效率）；Grafana仪表盘展示Agent健康度/协作效率/自治质量/记忆效 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4798 | Loki日志聚合 Loki Log Aggregation | 本地单实例接收JSON结构化日志+LogQL查询支持 | D_INFRA_OPS | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（352 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0036 | 通知与告警 Alerting Notification | C 015：通知与告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0049 | MOD-INF-034 | **与ZephyrAlpha上岗测试系统的对接**：本系统的LLM路由消费ZephyrAlpha项目ModelProfiler(MOD-INF-034)的7维benchmark基线+ModelCapabilityExam(MOD-INF-0 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0050 | MOD-INF-036 | **与ZephyrAlpha上岗测试系统的对接**：本系统的LLM路由消费ZephyrAlpha项目ModelProfiler(MOD-INF-034)的7维benchmark基线+ModelCapabilityExam(MOD-INF-0 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0052 | MOD-INF-033 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0054 | MOD-INF-024 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0055 | MOD-INF-035 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0056 | MOD-INF-026 | / Resource Optimization Engine / MOD-INF-033 / `snapshot()`实时资源快照（CPU/GPU/内存/IO） / 实时获取GPU显存/计算核心利用率→动态调整GPU留给因子计算的算力 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0273 | MOD-MASTER-001 | > ⚠️ **计数说明**：D-ML-TRAIN域104个模块中✅82+❌22=104；D-ML-SERVE域MS-xx未标注15个模块中✅10+❌5=15，与域级裁定✅35+❌11=46存在1项计数差异(可能存在优先级交叉归类)；D-DA | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0289 | CI/CD Pipeline 管线 | / IO-01 / CI/CD Pipeline / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-005已建设 / GitHub Actions+门禁 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0290 | Monitoring System 监控系统 | / IO-02 / Monitoring System / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-015已建设 / Prometheus+Grafana / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0291 | Backup Manager 备份管理器 | / IO-03 / Backup Manager / ✅ 能建 / / 自动备份+增量+离线存储 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0292 | Disaster Recovery 灾难恢复 | / IO-04 / Disaster Recovery / ❌ 不能建 / / 门禁: 需双活基础设施 / 双活+故障切换 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0293 | Health Dashboard 健康仪表盘 | / IO-05 / Health Dashboard / ✅ 能建 / 📋 项目内有蓝图编号MOD-INF-015已建设 / 统一健康面板 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0294 | Log Aggregator 日志聚合器 | / IO-06 / Log Aggregator / ❌ 不能建 / / 门禁: 需ELK集群 / 集中化日志+全文检索 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0295 | Resilience Manager 弹性管理器 | / IO-07 / Resilience Manager / ❌ 不能建 / / 门禁: 需多实例+自动扩缩容 / 弹性伸缩+故障转移 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0296 | Network Manager 网络管理器 | / IO-08 / Network Manager / ❌ 不能建 / / 门禁: 需网络设备+VPN / DNS+负载均衡+防火墙 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0297 | IaC Manager IaC管理器 | / IO-09 / IaC Manager / ❌ 不能建 / / 门禁: 需Terraform/Pulumi+云环境 / 声明式基础设施 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0298 | Security Infra Manager 安全基础设施管理器 | / IO-10 / Security Infra Manager / ❌ 不能建 / / 门禁: 需WAF+IDS硬件 / WAF+IDS+密钥管理 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0299 | HPC Manager HPC管理器 | / IO-11 / HPC Manager / ❌ 不能建 / / 门禁: 需GPU集群 / GPU集群调度 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0300 | Deployment Manager 部署管理器 | / IO-12 / Deployment Manager / ❌ 不能建 / / 门禁: 需多实例环境 / Blue-Green+Canary / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0301 | Alert Manager 告警管理器 | / IO-13 / Alert Manager / ✅ 能建 / / 告警分级+降噪+升级 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0522 | 备份策略 Backup Strategy | 增量/日快照/周全量/配置备份+RTO/RPO | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0638 | Backup Manager 自动备份管理器 | 自动备份+增量引擎+加密+校验+恢复测试+保留策略 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0639 | Cold Data Archive Manager 冷数据归档管理器 | 冷数据归档存储+归档策略/压缩/检索/清理+生命周期 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0640 | 数据源可用性SLA追踪器 Data Source Availability SLA Tracker | 各数据源历史可用率+延迟统计+SLA达标率 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0641 | 存储成本量化核算器 Storage Cost Calculator | 热/温/冷各层存储成本/TB自动计算与对比 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0679 | 日快照恢复演练 Daily Snapshot Recovery Drill | 每周从日快照恢复前一交易日状态恢复时间<1s数据完整 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0680 | 盘中恢复演练 Intraday Recovery Drill | 每月模拟盘中崩溃从快照+事件回放恢复恢复时间<30s RPO=0 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0681 | 全量恢复演练 Full Recovery Drill | 每季度从空状态恢复到最新状态恢复时间<5min数据完整 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0682 | 审计重建演练 Audit Reconstruction Drill | 每半年重建指定历史时间点的完整状态与历史记录一致 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0903 | Shared Infrastructure 共享基础设施 | 共享基础设施(配置/日志/错误/事件总线/健康检查) | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0909 | Tool Scripts 工具脚本 | 工具脚本(scaffold/lock_files/ide_health等) | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-0918 | Quantum-Classical Hybrid Computing Roadmap 量子-经典混合计算路线图 | 量子-经典混合计算路线图 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1238 | Cost Optimizer 成本优化器 | 云资源成本监控+成本分摊+资源利用率分析+成本预测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1443 | Agent RBAC / Permission Guard Agent RBAC/权限守卫器 | 七层纵深防御+RBAC+ABAC+零信任，蓝图已建设，≡D-AUTONOMY-01 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1771 | Communication Encryption Config 通信加密配置 | 归属D-INFRA；✅能建 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1902 | 数据血缘追踪 Data Lineage Tracking | 数据源→特征→因子→信号→策略→交易→PnL全链路可追溯 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1904 | AI API Cost Manager AI API成本管理器 | LLM API成本纳入预算管理超限自动降级 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1905 | Agent Communication Protocol Agent通信协议 | Agent间通信必须通过结构化消息协议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1906 | Capacity Assurance & SLI/SLO 容量保障与服务等级 | 学习系统关键操作必须满足SLI/SLO指标 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1909 | Model Profiler & Capability Exam 模型画像与能力考试 | LLM模型能力基线测量+多维度能力评估 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-1950 | PIT Manager Point-in-Time管理器 | ├─ 与R-15 Point-in-Time门控/R-69 PIT Manager的边界：PIT门控是验证规则（确保无前瞻偏差），Feature Store是数据基础设施（提供PIT AS OF JOIN查询能力），PIT Manager是 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2005 | Pipeline编排器 Pipeline Orchestrator | 12. Pipeline编排器（v7.0新增，裁定✅R-89 / 项目内有蓝图MOD-INF-009但是没建设🔧） | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2006 | Saga事务编排 Saga Transaction Orchestration | 编排式Saga+协调式Saga+补偿事务任一步骤失败时执行补偿操作回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2007 | 可配置规则引擎 Configurable Rule Engine | YAML/DSL规则定义+热更新规则变更无需重启服务即可生效 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2028 | 数字孪生系列 Digital Twin Series | 依赖图/实时同步/混沌实验:系统级数字孪生(❌) | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2038 | LLM模型分级路由 LLM Model Tiered Routing | M1/M3/M7/M9四级模型路由按任务复杂度选择不同规模LLM(❌) | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2039 | Data Mesh 数据网格 | 域所有权/数据产品/联邦治理:去中心化数据架构(❌) | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2040 | CQRS/Event Sourcing模型 CQRS/Event Sourcing Model | 命令查询职责分离+事件溯源:读写分离+完整事件历史(❌) | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2107 | Observability 可观测性 | 横切层7可观测性OpenTelemetry+GAAT | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2138 | Agent 365 OTel Enterprise Pipeline Agent 365 OTel企业级管道 | Agent 365 OTel企业级管道MVP暂缓多机部署 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2184 | OpenTelemetry | > **设计哲学**：多Agent系统的可观测性是安全与治理的基础。2025-2026年行业实践（OpenTelemetry多Agent语义约定、GAAT治理感知遥测、Microsoft Agent Governance Toolkit ( | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2189 | Agent SRE Reliability Engineering Agent SRE可靠性工程 | Agent SRE可靠性工程SLO定义熔断器混沌实验 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2192 | Trace Hierarchy Model Trace层级模型 | Trace层级模型Root Span Agent Span LLM Span Tool Span | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2224 | Prometheus Prometheus监控系统 | / 系统可用率 / 交易时段≥99.99%/非交易≥99.9% / 日 / Prometheus / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2272 | eBPF eBPF无侵入Span补全 | eBPF无侵入Span补全可观测性技术 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2282 | Docker Docker容器 | Docker容器L2集成测试执行环境每日构建+每次PR | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2283 | W3C TraceContext W3C TraceContext追踪标准 | > **Flow ID传播（参考MAN+ESM, Adya 2026）**：借鉴MAN+ESM的Flow ID概念，本系统在§3.2消息格式的metadata中传播traceId（与W3C TraceContext惯例一致），实现全链路可追 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2346 | Observability Three Pillars 可观测性三支柱 | 可观测性三支柱Traces链路追踪7年+Metrics指标度量5年+Logs结构化日志7年 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2347 | Trace Hierarchical Model Trace层级模型 | Trace层级模型Root Span到Agent Span到LLM Span到Tool Span到Retriever Span到Rule Span到A2A Span | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2352 | Test Automation & CI/CD Integration 测试自动化与CI/CD集成 | 测试自动化与CI/CD集成5测试类型L1单Agent单元测试到L5行为测试触发条件执行环境通过标准失败处理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2388 | Disaster Recovery Level L6 灾备分级L6日志审计 | 灾备分级(L6日志审计)：RTO<240min, RPO≤24hour, 交易日志/操作日志/审计记录, 压缩归档+双副本。 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-2408 | Key Observability Metrics 关键可观测性指标 | 关键可观测性指标7项Trace完整率+Agent决策延迟P99+A2A检查通过率+自治边界违规+LLM调用成本+串谋行为相关性+涌现行为检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3894 | 灾备3-2-1-1-0+D到E 灾备架构 | robocopy每小时增量RTO小于5min | D_INFRA_OPS | harvest待评估（uncertain） |  |
| CAND-HARVEST-3912 | 灾备架构 灾备架构 Disaster Recovery Architecture | RTO/RPO分级故障切换数据恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3913 | D到E盘双副本策略 双副本架构 | robocopy每小时增量同步 | D_INFRA_OPS | harvest待评估（uncertain） |  |
| CAND-HARVEST-3915 | 数据恢复流程 数据恢复 Workflow | Redis Parquet模型配置多场景恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3916 | 灾备演练计划 灾备演练 Disaster Recovery Drill Plan | 每月每季度每半年演练频率 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3917 | 混沌工程实践 混沌工程 Chaos Engineering Practice | Netflix Chaos Monkey主动注入故障 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3927 | 变更管理 变更管理 Management | 灰度金丝雀扩大全量回滚审批 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3928 | 灰度发布流程 灰度发布 Workflow | 构建金丝雀1-5%扩大25-50%全量100% | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3929 | 金丝雀验证 金丝雀验证 Canary Verification | 功能性能错误率资源风控数据六维验证 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3930 | 回滚策略 回滚策略 Strategy | 金丝雀扩大全量配置依赖库多场景回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-3931 | 依赖库升级流程 依赖库升级 Workflow | 安全评估沙箱审批备份灰度验证7步 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4001 | 双机热备 Active-Standby | 单机是单点故障双机热备不能建约束二 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4249 | Migration Strategy 迁移策略 | / migration_strategy.py / governance/ / 迁移策略 / ❌ 属于D-INFRA-OPS——迁移是运维基础设施域 / | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4517 | CI/CD Pipeline 持续集成部署流水线 | 持续集成/部署：构建器+测试编排器+部署器+回滚器+质量门禁 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4518 | Monitoring Stack 监控栈 | 监控栈：指标采集+日志收集+分布式追踪+告警引擎+仪表盘 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4519 | DR Manager 灾备管理器 | 灾备管理：故障检测+切换编排+数据同步+演练引擎+状态机 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4520 | Infrastructure as Code 基础设施即代码 | / D-INFRA-10 / Infrastructure as Code / 基础设施即代码：Terraform/Pulumi适配器+状态管理+漂移检测+计划预览 / P1 / ❌ / Terraform/Pulumi; IaC理论/声明 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4521 | Cybersecurity Shield 网络安全防护 | 威胁检测+漏洞扫描+入侵检测+WAF+密钥管理+事件响应 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4522 | Resilience Testing Engine 韧性测试引擎 | 故障注入器+爆炸半径控制+稳态假设+实验编排+报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4523 | Capacity Planner 容量规划器 | 容量需求预测+资源规划+扩展计划+容量报告+容量告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4524 | A-Share Intraday Monitor Dashboard Configurator A股盘中监控看板配置器 | 四类实时监控指标配置+版面布局+看板模板管理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4525 | Real-Time Dashboard Visual Renderer 实时仪表盘可视化渲染器 | 实时监控数据可视化渲染+图表类型自动选择+告警阈值可视化 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4526 | Infrastructure Health Patrol Inspector 基础设施健康巡检器 | 基础设施健康巡检+巡检项定义+巡检报告+巡检告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4527 | 模块隔离部署编排器 Module Isolation Deployment Orchestrator | 模块独立开发/测试/部署编排+依赖解析+部署顺序+故障隔离 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4528 | 组件复用注册中心 Component Reuse Registry Center | 可复用模块注册/发现/版本管理+接口标准化 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4529 | 开源框架评估与集成器 Integration | 开源框架评估/选型/版本兼容性检查/集成适配 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4530 | 统一交互入口管理器 Management | 统一交互入口+仪表盘/菜单导航/权限管理/用户配置 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4531 | 模块边界与依赖识别器 Module Boundary and Dependency Identifier | 分析现有模块结构+识别边界和关系+依赖图自动生成 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4532 | 系统集成测试编排器 Integration | 模块间集成测试+系统级测试+故障注入测试+测试报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4533 | 部署监控优化器 Monitoring | 系统部署+监控+性能优化+蓝绿部署+回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4534 | 五区域布局管理器 Management | 五区域布局+NozyIO可视化编辑系统集成+旧版布局兼容迁移 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4535 | SLA监控与保障器 | / D-INFRA-49 / SLA监控与保障器 / SLA监控与保障器：7×24稳定运行+数据流延迟<1s+按钮≤100ms+页面≤500ms+查询≤1s的SLA监控+告警+自动恢复 / P1 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4536 | 复杂操作进度提示器 Complex Operation Progress Prompter | 复杂操作进度追踪+进度条渲染+取消支持+超时处理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4537 | 故障自动检测诊断器 Fault Auto Detection Diagnoser | 故障自动检测和诊断+异常识别+根因分析+诊断报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4538 | 五区域布局渲染引擎 Engine | 五区域布局渲染+区域尺寸调整+区域折叠+布局持久化 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4539 | 系统级导航与功能入口管理器 Management | 顶部导航栏+系统级功能入口+快捷键+最近访问 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4540 | 多标签页管理器 Management Tag | 多标签页布局+标签页切换+标签页状态保存+标签页恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4541 | 可拖拽面板引擎 Engine | 可拖拽面板+面板布局自定义+布局保存+布局恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4542 | 桌面端大屏优化器 Desktop Large Screen Optimizer | 桌面端大屏幕优化+分辨率适配+DPI缩放+多显示器支持 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4543 | 桌面端专属交互优化器 Desktop Exclusive Interaction Optimizer | 桌面端交互优势利用+键盘快捷键+鼠标手势+右键菜单 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4544 | 分阶段实施编排器 Phased Implementation Orchestrator | 5阶段实施计划+阶段依赖+阶段门禁+阶段验收 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4545 | 层间依赖与部署顺序编排器 Inter-layer Dependency and Deployment Order Orchestrator | 12层部署顺序+层间依赖解析+并行部署+部署验证 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4546 | 系统资源监控告警器 Monitoring Alerting | CPU+内存+磁盘+网络4维资源监控+阈值告警+自动扩容 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4547 | Streamlit快速原型开发器 | / D-INFRA-66 / Streamlit快速原型开发器 / Streamlit快速原型开发器：Streamlit Web界面快速原型+数据展示+交互控件+实时更新 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4548 | PyQt5桌面GUI集成器 | / D-INFRA-67 / PyQt5桌面GUI集成器 / PyQt5桌面GUI集成器：PyQt5 VeighNa启动器界面+桌面集成+系统托盘+原生通知 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4549 | 渐进式增强管理器 Management | 基础功能先行+高级功能后续+功能开关+灰度发布+回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4550 | 文档中心索引管理器 Management Index | / D-INFRA-70 / 文档中心索引管理器 / 文档中心索引管理器：docs文档中心+INDEX.md快速导航+System_Manifest系统清单+API_Contract接口契约+7子目录文档管理 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4551 | 项目目录结构生成器 Generator Directory | / D-INFRA-71 / 项目目录结构生成器 / 项目目录结构生成器：quant_system_v4项目目录结构自动生成+目录校验+目录规范检查+目录初始化 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4552 | 模块实现状态追踪器 State | 8模块实现状态追踪+已实现/规划中/开发中+状态变更记录 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4553 | 依赖版本兼容性检查器 Dependency Version Compatibility Checker | 8库版本兼容性检查+版本冲突检测+升级建议+安全漏洞检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4554 | 目录结构规范校验器 Checker Directory | 目录结构规范校验+必需目录检查+目录权限检查+目录命名规范 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4555 | 文件命名规范检查器 File | 文件命名规范检查+模块/策略/因子/测试/配置5类命名规则 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4556 | 优先级自动评估器 Priority Auto Evaluator | 模块优先级自动评估+依赖分析+影响范围+开发成本+优先级建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4557 | 性能基准测试器 Performance | / D-INFRA-83 / 性能基准测试器 / 性能基准测试器：性能基准测试+启动时间+响应时间+吞吐量+资源使用率+基准报告+回归检测 / P1 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4558 | Docker容器化研究环境管理器 | / D-INFRA-85 / Docker容器化研究环境管理器 / Docker容器化研究环境管理器：Docker容器化技术+Python/R环境配置+VS Code/Jupyter Lab+Git版本控制 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4559 | CI/CD流水线集成器 | / D-INFRA-86 / CI/CD流水线集成器 / CI/CD流水线集成器：pytest单元测试+CI/CD流程+自动构建+自动部署+自动测试 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（uncertain） |  |
| CAND-HARVEST-4560 | Ant Design+ECharts可视化组件集成器 | / D-INFRA-88 / Ant Design+ECharts可视化组件集成器 / Ant Design+ECharts可视化组件集成器：Ant Design+Element Plus统一可视化组件库+ECharts+D3.js交互式图 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4561 | 硬件资源优化建议器 Hardware Resource Optimization Advisor | / D-INFRA-91 / 硬件资源优化建议器 / 硬件资源优化建议器：CPU优化+内存管理+GPU加速+存储优化+psutil+Node Exporter资源监控 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4562 | 架构性能瓶颈识别器 Performance | 性能分析与瓶颈识别+系统可靠性评估+扩展性优化+优化建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4563 | NozyIO多语言代码编辑集成器 | / D-INFRA-94 / NozyIO多语言代码编辑集成器 / NozyIO多语言代码编辑集成器：支持Python/R/SQL多语言编辑+模块间跳转+系统命令执行+Docker容器管理 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4564 | 系统健康度评分器 System Health Score Rater | 整体运行状态监控+关键指标展示+系统健康度评分+健康度趋势 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4565 | 个性化界面配置管理器 Management Config | 模块快速访问+功能菜单管理+常用功能快捷键+个性化界面配置 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4566 | 模块实现进度追踪器 Module Implementation Progress Tracker | 高优先级模块实现进度追踪+阶段完成度+交付物检查+延期预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4567 | 模块间集成测试计划器 Integration | 各模块开发完成后的集成测试计划+集成顺序+集成接口 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4568 | 性能测试Locust/JMeter集成器 | / D-INFRA-99 / 性能测试Locust/JMeter集成器 / 性能测试Locust/JMeter集成器：Locust+JMeter性能测试+大数据处理场景+性能基准+性能报告 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4569 | ELK日志管理器 | / D-INFRA-100 / ELK日志管理器 / ELK日志管理器：ELK Stack完整日志收集+分析+可视化+日志搜索+日志告警+日志归档 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4570 | 灾备方案管理器 Management | / D-INFRA-101 / 灾备方案管理器 / 灾备方案管理器：pgBackRest+Redis Sentinel数据备份和恢复机制+备份策略+恢复验证+灾备演练 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4571 | 预测性维护与自愈修复器 Predictive Maintenance and Self-Healing Repairer | / D-INFRA-103 / 预测性维护与自愈修复器 / 预测性维护与自愈修复器：基于历史数据预测系统故障+ML预测模型+自动修复脚本+自愈验证 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4572 | 12层架构与九大平台映射分析器 Analyzer | 详细对比12层架构与九大核心平台+映射关系+差距识别 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4573 | 文档链接有效性检查器 Document Link Validity Checker | / D-INFRA-109 / 文档链接有效性检查器 / 文档链接有效性检查器：提取所有链接+验证内部链接+curl/wget检查外部链接+链接报告 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4574 | 文档单一信息源管理器 Management | / D-INFRA-110 / 文档单一信息源管理器 / 文档单一信息源管理器：核心文档权威技术描述+其他文档引用关联+信息源注册+信息源版本 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4575 | 数据库备份与恢复方案器 Database | 数据备份与恢复+备份策略+恢复验证+灾备演练+备份加密 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4576 | 模块依赖分析器 Analyzer | 模块间依赖关系图+依赖冲突检测+循环依赖识别+依赖版本管理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4577 | 开源组件评估器 Open Source Component Evaluator | 开源许可证合规检查+组件安全漏洞扫描+组件活跃度评估 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4578 | 目录结构验证器 Validator Directory | / D-INFRA-116 / 目录结构验证器 / 目录结构验证器：目录规范校验+路径引用完整性检查+配置文件路径一致性+硬编码路径扫描 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4579 | 配置迁移工具 Config Utils | / D-INFRA-117 / 配置迁移工具 / 配置迁移工具：docker-compose配置更新+启动脚本更新+环境变量迁移+文档链接更新 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4580 | 交互界面迁移方案器 Interactive Interface Migration Planner | NozyIO四层架构迁移路径+界面组件映射+交互逻辑迁移 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4581 | 阶段交付物定义器 Phase Deliverable Definer | / D-INFRA-121 / 阶段交付物定义器 / 阶段交付物定义器：各阶段交付物清单+交付物质量标准+交付物评审流程+阶段验收标准 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4582 | 自动化代码审查流水线 Automated Code Review Pipeline | / D-INFRA-122 / 自动化代码审查流水线 / 自动化代码审查流水线：Ruff+mypy+Bandit集成+审查结果聚合+审查报告生成+审查规则自定义 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4583 | 代码质量度量看板 Code Quality Metrics Dashboard | 代码复杂度趋势+测试覆盖率趋势+技术债务追踪+代码重复率监控 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4584 | 主题与样式引擎 Engine | / D-INFRA-124 / 主题与样式引擎 / 主题与样式引擎：主题切换+色彩方案管理+字体方案管理+暗色模式+自定义主题导入导出 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4585 | 交互反馈系统 Interactive Feedback System | / D-INFRA-125 / 交互反馈系统 / 交互反馈系统：操作反馈组件+错误提示组件+加载状态组件+操作确认组件+通知消息组件 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4586 | 可视化组件库 Visualization Component Library | / D-INFRA-126 / 可视化组件库 / 可视化组件库：K线图组件+折线图组件+柱状图组件+饼图组件+热力图组件+数据表格组件 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4587 | 文档一致性校验器 Checker | / D-INFRA-127 / 文档一致性校验器 / 文档一致性校验器：文档编号重复检测+版本号格式校验+术语一致性检查+结构规范验证 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4588 | 文档完整性扫描器 Document Completeness Scanner | / D-INFRA-128 / 文档完整性扫描器 / 文档完整性扫描器：README缺失检测+文档与代码结构比对+缺失文档识别+文档覆盖率统计 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4589 | 审计报告自动生成器 Generator Audit Report | / D-INFRA-129 / 审计报告自动生成器 / 审计报告自动生成器：目录结构评估+文档质量评分+一致性检测+价值评估+改进建议生成 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4590 | 遗产代码迁移适配器 Adapter | / D-INFRA-130 / 遗产代码迁移适配器 / 遗产代码迁移适配器：旧接口适配+数据格式转换+配置映射+功能等效验证+迁移进度追踪 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4591 | 环境初始化一键脚本 Environment | 自动完成venv创建、依赖安装、配置生成 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4592 | 数据迁移模块 Data Migration Module | 数据结构变更时的自动迁移工具 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4593 | CI/CD流水线编排 | 自动化构建测试部署流水线 | D_INFRA_OPS | harvest待评估（uncertain） |  |
| CAND-HARVEST-4594 | 依赖冲突检测 Dependency Conflict Detection | 模块间依赖的循环检测与冲突预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4595 | 里程碑健康检查 Milestone Health Check | 阶段完成前的质量门禁检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4596 | 交付物自动检查 Deliverable Auto Check | 交付物完整性与质量的自动验证 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4597 | 测试报告生成 Report | 自动化测试报告生成与通知 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4598 | 日志聚合模块 Aggregator Logger | 分布式日志的聚合查询与全文检索 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4599 | 审计日志分析 Audit Logger | 审计日志的自动化分析与异常行为检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4600 | 模块依赖图生成 Module Dependency Graph Generator | 自动生成模块依赖关系图与循环依赖检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4601 | 蓝绿部署策略 Strategy | 零停机部署的蓝绿切换机制 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4602 | 配置漂移检测 Config | 运行环境与基准配置的偏差检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4603 | 灰度发布控制器 Canary Release Controller | 新版本的渐进式灰度发布 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4604 | 开发环境标准化 Environment | 开发环境的统一容器化与一致性保障 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4605 | 接口健康探测 Interface | 接口可用性的定期探测与告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4606 | 依赖冲突检测器 Detector | 检测包版本冲突与兼容性问题 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4607 | 容器健康检查 Container Health Check | 容器级别的健康探针与自动重启 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4608 | 通信性能监控模块 Monitoring Performance | 监控模块间通信延迟和吞吐量 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4609 | 接口性能监控 Monitoring Interface Performance | API响应时间与错误率监控 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4610 | 容器资源限制 Container Resource Limit | 内存/CPU限制配置与OOM保护 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4611 | 日志异步写入 Logger Async | 日志写入的性能优化与批量刷盘 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4612 | 部署性能基准 Performance | 部署后自动性能基准测试 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4613 | 流水线性能监控 Monitoring Performance | 流水线各阶段耗时监控与瓶颈定位 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4614 | 配置模板生成器 Generator Config | 根据.env.example自动交互式生成.env | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4615 | 交付物模板管理 Management | 交付物文档模板的统一管理与版本控制 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4616 | 测试环境管理 Management Environment | 测试环境的配置隔离与数据准备 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4617 | 配置变更审计 Audit Config | 配置变更的审计追踪与回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4618 | 容器安全扫描 Security | Docker镜像安全漏洞扫描 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4619 | 密钥轮换模块 Key Rotation Module | API密钥的定期自动轮换与无缝切换 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4620 | 部署安全扫描 Security | 部署前的安全漏洞与配置扫描 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4621 | 日志脱敏模块 Logger | 敏感信息的自动脱敏与过滤 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4622 | 事件总线监控 Monitoring Event | 事件吞吐量/延迟/积压的监控指标 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4623 | 工作流健康检查 Workflow Health Check | 工作流运行状态的定期巡检 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4624 | 报告导出模块 Report | 报告导出为PDF/HTML/Excel格式 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4625 | 自定义监控面板 Monitoring | 用户自定义监控视图与告警阈值 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4626 | 自定义检查项 Custom Check Item | 用户自定义健康检查规则与阈值 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4627 | 自定义统计指标 Custom Statistics Metric | 用户自定义统计指标与可视化 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4628 | 交互设计规范合规检查器 Compliance | 桌面端适配验证+术语一致性检查+设计规范覆盖率 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4629 | 文件智能解析器 Parser File | / D-INFRA-204 / 文件智能解析器 / 文件智能解析器：PDF/DOC/Excel/CSV/JSON/YAML解析+关键信息提取+结构化转换 / P2 / ❌ / — | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4630 | 自动化运维执行器 Execution Operations | 健康状态巡检+性能优化自动执行+故障自愈+安全补丁自动应用 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4631 | 代码块语法校验器 Checker | Python/SQL语法自动校验 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4632 | Mermaid流程图渲染器 | 流程图语法解析与预览 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4633 | Markdown表格校验器 | 表格格式规范检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4634 | 树状图自动生成器 Generator | 从文档结构自动解析生成 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4635 | 层级深度校验器 Checker | 层级完整性与深度规范检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4636 | 节点关联分析器 Analyzer Node | 节点间依赖与引用关系分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4637 | 树状图差异对比器 Tree View Diff Comparator | 版本间结构差异对比 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4638 | 优先级动态调整器 Priority Dynamic Adjuster | 基于依赖关系的优先级自动调整 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4639 | 模块依赖关系图 Module Dependency Relationship Graph | 模块间依赖可视化与冲突检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4640 | 开发进度追踪器 Development Progress Tracker | 任务进度实时追踪与偏差预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4641 | 验收标准量化器 Acceptance Criteria Quantifier | 验收标准可量化指标定义 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4642 | 里程碑风险预警 Risk | 里程碑延期风险自动预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4643 | 阶段交付物检查器 Phase Deliverable Checker | 各阶段交付物完整性检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4644 | 进度偏差分析器 Analyzer | 实际进度与计划偏差分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4645 | Docker健康检查器 | 容器状态自动巡检与告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4646 | SSL证书自动更新 | 镜像源证书自动管理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4647 | 日志智能分析器 Analyzer Logger | 日志异常模式自动识别 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4648 | 内存泄漏检测器 Detector Memory | 内存使用趋势监控与泄漏预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4649 | 运维操作审计 Audit Operations | 运维操作记录与审计追踪 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4650 | 流水线执行监控 Execution Monitoring | 各阶段执行状态与耗时监控 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4651 | 数据延迟检测 Latency | 数据更新延迟检测与告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4652 | 布局持久化 Layout Persistence | 用户自定义布局保存与恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4653 | 响应式断点适配 Response | 不同分辨率下的布局自适应 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4654 | 面板拖拽状态同步 Sync State | 多面板拖拽布局状态实时同步 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4655 | 全局快捷键管理 Management | 系统级快捷键注册与冲突检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4656 | 标签页状态管理 Management State Tag | 标签页数据缓存与恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4657 | 拖拽面板布局引擎 Engine | 面板自由拖拽与吸附布局 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4658 | 文件上传预览 File | 上传文件内容预览与格式校验 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4659 | 导航权限控制 Navigation Permission Control | 基于角色的导航菜单动态渲染 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4660 | 表单自动保存 Table | 表单数据定时自动保存与草稿恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4661 | 操作撤销重做栈 Operation Undo Redo Stack | 用户操作撤销与重做历史管理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4662 | 交互操作埋点 Interactive Operation Tracking | 用户交互行为采集与分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4663 | 图表主题动态切换 Table | 明暗主题与色盲友好配色 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4664 | 大数据量图表优化 Table | 百万级数据点降采样与虚拟滚动 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4665 | 图表导出与分享 Table | 图表PNG/SVG导出与链接分享 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4666 | 实时数据流图表 Real-time Table | 流式数据实时追加渲染 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4667 | 学习进度量化评估 Learning Progress Quantitative Assessment | 学习效果多维量化评分 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4668 | 运维变更审批流 Operations | 自动化运维变更审批与回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4669 | React组件库定制 | Ant Design主题定制与业务组件封装 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4670 | ECharts大规模数据渲染 | 百万级数据点高性能渲染 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4671 | 无障碍访问适配 Accessibility Adaptation | 键盘导航与屏幕阅读器支持 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4672 | 前端性能基准测试 Frontend Performance | 前端渲染性能基准与回归检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4673 | 前端安全审计 Audit Security Frontend | XSS/CSRF防护与依赖漏洞扫描 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4674 | 文档状态变更通知与依赖影响分析器 Analyzer Notification State | 文档状态变更时自动通知引用模块+依赖链影响范围分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4675 | 文档完整性自动化校验器 Checker | 检查标记为完整的章节是否真实包含所有必需内容字段 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4676 | 文档版本依赖一致性检查器 Document Version Dependency Consistency Checker | 多章节共享同一源文件时的内容一致性检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4677 | 功能废弃影响范围追踪器 Feature Deprecation Impact Scope Tracker | 被标记为未实现的功能的上游依赖和下游消费方追踪 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4678 | 技术栈版本兼容性矩阵自动检测器 Detector | 13类技术版本组合的自动兼容性检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4679 | 技术栈技术债务追踪器 Tech Stack Technical Debt Tracker | 小众/老旧技术的技术债务追踪+社区活跃度+替代方案评估 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4680 | 开发时间预算与实际偏差追踪器 Development Time Budget vs Actual Deviation Tracker | 开发时间预算追踪+实际耗时偏差分析+偏差预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4681 | 优先级冲突解决器 Priority Conflict Resolver | 多个P0功能资源争抢时的冲突检测+协调策略+资源分配 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4682 | 优先级时间预算与延期预警器 Priority Time Budget and Delay Warmer | P1本周完成/P2有时间再做的自动时间追踪+延期预警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4683 | 阶段门禁自动验证器 Validator | 各阶段完成条件自动验证+交付物检查+门禁通过判定 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4684 | 跨模块阶段协调器 Cross-Module Phase Coordinator | 4个模块阶段计划的隐式依赖检测+协调+冲突解决 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4685 | 阶段门禁检查器 Phase Gate Checker | 阶段完成后的门禁检查清单+完成标准判定+切换审批+回退机制 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4686 | 阶段交付物验收清单生成器 Generator | 各阶段交付物验收标准模板+验收流程编排+验收报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4687 | 阶段资源分配与调度器 Scheduler | 各阶段人力资源+计算资源+时间资源分配+冲突检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4688 | 阶段过渡触发器 Phase Transition Trigger | 研究→回测→模拟→实盘的阶段过渡条件判定+触发机制 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4689 | 技术选型加权评分器 Technology Selection Weighted Scorer | 多维度权重配置+自动评分+选型报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4690 | 技术选型决策记录追踪器 Technology Selection Decision Record Tracker | 选型理由+时间+参与者的完整审计记录 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4691 | 技术选型决策框架 Technology Selection Decision Framework | 统一技术选型评估标准+评分模型+决策模板+加权评分 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4692 | 开源项目许可证兼容性检查器 Open Source Project License Compatibility Checker | 开源项目许可证兼容性检查+GPL类许可证影响评估 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4693 | KrakenD/Kong替代API网关评估 | 高性能场景下专业API网关替代评估+对比报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4694 | 技术栈冗余检测与收敛建议器 Tech Stack Redundancy Detection and Convergence Advisor | 技术栈冗余检测+收敛建议+合并方案 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4695 | 技术栈版本兼容性矩阵检查器 Tech Stack Version Compatibility Matrix Checker | 各技术版本交叉兼容性自动校验+兼容性报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4696 | 技术栈废弃预警器 Tech Stack Deprecation Warmer | 开源项目停止维护/版本过期自动提醒+替代方案推荐 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4697 | 技术栈许可证合规检查器 Compliance | 各依赖库开源协议兼容性扫描+合规报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4698 | 12层架构健康检查与故障隔离器 12-Layer Architecture Health Check and Fault Isolator | 每层健康状态检查+层间依赖健康传播+故障隔离 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4699 | 路线图版本差异对比器 Roadmap Version Diff Comparator | 不同版本路线图变更可视化+差异高亮+变更日志 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4700 | 里程碑依赖图自动生成器 Generator | 阶段间依赖关系自动拓扑展示+依赖分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4701 | 交付物模板标准化器 Deliverable Template Standardizer | 各阶段交付物清单模板复用+模板管理+模板版本 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4702 | 命名规范自动修复建议器 Naming Convention Auto Repair Advisor | 违规文件自动推荐修正名称+批量重命名建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4703 | 批量重命名脚手架生成器 Generator Batch | 基于命名规范的批量文件重命名脚本生成 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4704 | 命名规范CI门禁集成器 | git commit前自动检查命名合规+CI集成 | D_INFRA_OPS | harvest待评估（uncertain） |  |
| CAND-HARVEST-4705 | 流水线执行延时统计分析器 Analyzer Execution | 各环节实际耗时vs计划耗时偏差统计+趋势分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4706 | 流水线执行时间偏差告警器 Execution Alerting | 实际执行时间与计划偏差超过阈值告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4707 | 流水线执行日报自动生成器 Generator Execution | 每日流水线执行摘要+异常+趋势报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4708 | 依赖版本自动升级建议器 Dependency Version Auto Upgrade Advisor | 自动检测并建议最优升级版本+升级时机+兼容性检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4709 | 导航状态持久化与恢复器 State | 用户导航位置+展开状态保存与恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4710 | 导航使用热力图生成器 Generator | 各导航项点击频次+路径分析+使用统计 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4711 | 表单Schema版本管理器 | 表单字段定义版本追踪+向下兼容+版本回滚 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4712 | 表单草稿自动保存与恢复器 Table | 用户输入内容定时自动存储+意外关闭恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4713 | 按钮状态机管理器 State Machine Management | 按钮禁用/加载中/成功/失败状态自动流转控制 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4714 | 图表主题标准化导出导入器 Importer Table | 主题配置JSON序列化+跨实例共享+主题市场 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4715 | 色盲友好配色自动验证器 Validator | 配色方案无障碍合规性检查+色盲模式切换 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4716 | 数据格式国际化本地化器 Local | 金额/百分比/时间格式按地域自动切换 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4717 | 表格列配置持久化器 Config Table | 用户自定义列宽/排序/显隐状态保存与恢复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4718 | 交互方式使用统计热力图 Interaction Method Usage Statistics Heatmap | 各交互模式使用频率+场景+效果量化对比 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4719 | 交互方式成本效率分析器 Analyzer | 语音/文字/图形各方式耗时与准确率对比 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4720 | 辅助效果量化评估器 Helper | 辅助前后用户操作效率对比统计+效果报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4721 | 自动化运维变更影响预分析器 Analyzer Operations | 运维变更前自动评估影响范围+风险分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4722 | 布局版本迁移转换器 Converter | 旧版布局到新版布局的自动映射与转换工具 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4723 | 协作过程动画回放器 Collaboration Process Animation Player | 历史人机协作步骤的动画式回溯查看 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4724 | Pipeline节点健康度探针 | 各环节存活/延迟/吞吐量实时检测+健康评分 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4725 | Pipeline吞吐量瓶颈分析器 | 各环节处理能力对比+瓶颈定位+优化建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4726 | 验证流程定制化编辑器 Workflow | 允许用户自定义验证步骤与顺序+流程模板 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4727 | 验证流程耗时基准器 Workflow | 各验证环节耗时基线建立+退化检测+优化建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4728 | 树状图节点实时搜索与过滤器 Filter Real-time Node | 按关键字/层级快速定位节点+过滤 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4729 | 树状图版本差异可视化器 Tree View Version Diff Visualizer | 两版本树状图结构变更高亮对比+差异报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4730 | 存储层性能基准测试器 Storage Performance | 各层实际读写延迟/吞吐量基准测试+退化检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4731 | 前端组件渲染性能监控器 Monitor Frontend Performance | 组件加载/更新/卸载耗时自动采集+告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4732 | 布局组件依赖关系检测器 Detector | 组件间调用/通信依赖自动识别+可视化 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4733 | 可视化组件注册中心 Visualization Component Registry Center | 组件版本/依赖/兼容性/文档统一管理 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4734 | 组件使用频次统计数据采集器 Component Usage Frequency Statistics Collector | 各组件渲染频次+耗时+错误率统计 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4735 | 数据流断点调试器 Data Flow Breakpoint Debugger | 数据流转中途暂停+检查+修改+继续 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4736 | 部署架构漂移检测器 Detector | 实际部署拓扑与蓝图文档差异自动比对+告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4737 | 部署依赖顺序校验器 Checker | 各层部署顺序+依赖关系自动检查+冲突检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4738 | pre-commit git钩子自动配置器 | 静态检查工具自动注册到pre-commit | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4739 | CI管道命令封装脚本 | 统一命令行接口+参数配置+结果格式化输出 | D_INFRA_OPS | harvest待评估（uncertain） |  |
| CAND-HARVEST-4740 | mypy增量类型检查模式 | 只检查git变更文件而非全量+增量检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4741 | 目录结构一致性巡检器 Directory | 实际目录vs文档定义目录差异告警+修复建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4742 | 目录模板快速初始化脚手架 Directory | new project一键创建标准化目录+模板文件 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4743 | 新模块子模块脚手架自动生成器 Generator | 基于规范的目录+模板文件一键创建 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4744 | 文档结构导航地图自动生成器 Generator | 基于章节层级自动生成交互式导航树 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4745 | 文档章节链接有效性批量检查器 Batch | 交叉引用链接自动扫描+断链修复 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4746 | 目录迁移影响预分析器 Analyzer Directory | 目录结构调整对配置文件/代码路径/依赖的影响分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4747 | 目录迁移回滚方案器 Directory | 目录结构调整失败后自动恢复到原始状态 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4748 | 监控方案迁移路径规划器 Monitoring Path | 从自研到Grafana的迁移方案+数据迁移+仪表板导入 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4749 | 监控阈值自适应调整器 Monitoring | 根据系统运行状态自动调整监控阈值+合理性评估 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4750 | 性能指标SLA实时仪表板 | 性能指标实时仪表板+SLA达标率+趋势分析 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4751 | 性能基准回归检测器 Detector Performance | 每次代码变更后的性能基准回归测试+退化检测 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4752 | 异常使用统计与热点分析器 Analyzer | 异常使用频率统计+分布分析+趋势+热点识别 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4753 | 多数据库SLA监控与告警器 | 多数据库SLA监控+查询延迟+同步延迟+备份恢复成功率 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4754 | 实验追踪方案决策记录器 Experiment Tracking Scheme Decision Recorder | 记录选择wandb而非自研的决策依据+切换条件+回退策略 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4755 | 实验追踪方案切换触发器 Experiment Tracking Scheme Switch Trigger | wandb服务中断时的切换条件+本地备选方案+数据同步 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4756 | 指标阈值动态调整与合理性评估器 Metric Threshold Dynamic Adjustment and Rationality Evaluator | 根据系统运行数据动态调整指标阈值+合理性评估 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4757 | 业务指标量化与追踪器 Business Metric Quantifier and Tracker | 将定性业务指标转化为可量化指标+计算公式+数据采集 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4758 | API文档自动版本同步器 | API实现变更时文档自动同步更新+版本对应 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4759 | 字段类型变更影响分析器 Analyzer Field | 表字段类型修改影响下游查询分析+影响报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4760 | 模型文件路径安全性检查器 Security Model File Path | 路径穿越+越权访问防护+安全检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4761 | 模型推理性能基准测试器 Inference Model Performance | 每次推理耗时基准记录+退化告警+性能趋势 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4762 | Agent调用审计日志器 | 每次Agent决策/操作的完整记录+审计查询 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4763 | 配置变更审计日志追踪器 Audit Logger Config | 每次配置修改的差异/时间/操作人记录 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4764 | 委员会决策耗时监控器 Monitor | 各委员决策延迟统计+超时告警+性能报告 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4765 | 决策流节点耗时瓶颈分析器 Analyzer Node | 各决策环节CPU/IO耗时分布+瓶颈定位 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4766 | 决策路径频次统计器 Path | 历史决策路径选择频次+成功率分析+优化建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4767 | 元数据Schema迁移管理器 | 因子元数据字段变更时的自动迁移脚本生成 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4768 | wandb使用成本追踪器 | API调用次数+存储用量+费用自动统计+预算告警 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4769 | 知识来源质量评分器 Knowledge | 各来源知识质量/准确率/时效性评分+评分更新 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4770 | Layer文档位置索引与完整性检查器 | 各Layer文档位置自动索引+完整性检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4771 | 架构版本演进追踪器 Architecture Version Evolution Tracker | Layer 0-7架构版本变更记录+差异对比+兼容性检查 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4772 | MLflow性能基准测试器 | MLflow性能基准定义+退化检测+优化建议 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4773 | 桌面端多显示器布局管理 Management | 多显示器扩展桌面布局与窗口位置记忆 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4774 | 技术债务追踪 Technical Debt Tracking | 开发过程中技术债务的记录和追踪机制 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4775 | 日志保留与归档策略 Strategy Logger | 不同级别日志的保留期限和归档策略 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4776 | 知识生命周期管理 Lifecycle Knowledge Management | 知识的时效性检测与自动归档 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4777 | 系统版本兼容 System Version Compatibility | 系统版本间的兼容性保障与迁移路径 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4778 | 架构决策记录 Architecture Decision Record | 架构决策的记录追踪与评审 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4779 | 监控事件聚合器 Monitoring Aggregator Event | 各域→INFRA监控事件聚合与降采样 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4780 | 数据质量监控桥接器 Data Quality Monitoring | D-DATA→D-INFRA数据质量监控桥接 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4781 | 信号质量评估消费桥接器 Signal | D-SIGNAL→D-INFRA信号质量监控桥接 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4782 | 风控事件告警桥接器 Risk Control Alerting Event | D-RISK→D-INFRA风控告警桥接 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4783 | 灰度发布与蓝绿部署框架 Canary Release and Blue-Green Deployment Framework | 系统更新的灰度发布与蓝绿部署编排 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4784 | 统一健康检查框架 Unified Health Check Framework | 各子模块健康检查端点的统一注册与聚合 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4785 | 跨域向后兼容性检查器 Cross-Domain Backward Compatibility Checker | / D-INFRA-473 / 跨域向后兼容性检查器 / 新版本发布前自动检查与旧版本数据/接口/配置/事件格式的兼容性 / P2 / ❌ / 第六轮迁移进化/运维数据管理推导 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4786 | 动态韧性调整器 Dynamic Resilience Adjuster | 基于运行时状态的韧性动态调整+自适应优化 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4787 | 优雅降级规划器 Fallback | 依赖故障时优雅降级路径规划+策略选择+执行编排 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4788 | 依赖图韧性评分增强 Dependency Graph Resilience Score Enhancement | 5维韧性评分增强+动态调整+预测性评分 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4789 | 韧性评分标准化器 Resilience Score Standardizer | 韧性评分标准化定义+跨系统可比+基准建立 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4796 | OpenTelemetry Collector OpenTelemetry收集器 | / OpenTelemetry Collector / 本地进程部署 / 接收OTLP协议，导出至SQLite(热)+Parquet(冷)；MVP使用JSON文件导出，未来升级门禁：多机部署+企业级监控需求+有第二位开发人员加入时可接入Ag | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4797 | Prometheus+Grafana监控栈 Prometheus Grafana Monitor Stack | / Prometheus + Grafana监控栈 / 本地单实例 / Prometheus采集Agent Metrics（Agent延迟、协作成功率、成本、反思有效率）；Grafana仪表盘展示Agent健康度/协作效率/自治质量/记忆效 | D_INFRA_OPS | harvest待评估（likely_new） |  |
| CAND-HARVEST-4798 | Loki日志聚合 Loki Log Aggregation | 本地单实例接收JSON结构化日志+LogQL查询支持 | D_INFRA_OPS | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0036 | 通知与告警 Alerting Notification | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0049 | MOD-INF-034 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0050 | MOD-INF-036 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0052 | MOD-INF-033 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0054 | MOD-INF-024 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0055 | MOD-INF-035 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0056 | MOD-INF-026 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0273 | MOD-MASTER-001 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0289 | CI/CD Pipeline 管线 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0290 | Monitoring System 监控系统 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0291 | Backup Manager 备份管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0292 | Disaster Recovery 灾难恢复 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0293 | Health Dashboard 健康仪表盘 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0294 | Log Aggregator 日志聚合器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0295 | Resilience Manager 弹性管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0296 | Network Manager 网络管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0297 | IaC Manager IaC管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0298 | Security Infra Manager 安全基础设施管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0299 | HPC Manager HPC管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0300 | Deployment Manager 部署管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0301 | Alert Manager 告警管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0522 | 备份策略 Backup Strategy | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0638 | Backup Manager 自动备份管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0639 | Cold Data Archive Manager 冷数据归档管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0640 | 数据源可用性SLA追踪器 Data Source Availability SLA Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0641 | 存储成本量化核算器 Storage Cost Calculator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0679 | 日快照恢复演练 Daily Snapshot Recovery Drill | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0680 | 盘中恢复演练 Intraday Recovery Drill | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0681 | 全量恢复演练 Full Recovery Drill | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0682 | 审计重建演练 Audit Reconstruction Drill | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0903 | Shared Infrastructure 共享基础设施 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0909 | Tool Scripts 工具脚本 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0918 | Quantum-Classical Hybrid Computing Roadmap 量子-经典混合计算路线图 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1238 | Cost Optimizer 成本优化器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1443 | Agent RBAC / Permission Guard Agent RBAC/权限守卫器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1771 | Communication Encryption Config 通信加密配置 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1902 | 数据血缘追踪 Data Lineage Tracking | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1904 | AI API Cost Manager AI API成本管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1905 | Agent Communication Protocol Agent通信协议 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1906 | Capacity Assurance & SLI/SLO 容量保障与服务等级 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1909 | Model Profiler & Capability Exam 模型画像与能力考试 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1950 | PIT Manager Point-in-Time管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2005 | Pipeline编排器 Pipeline Orchestrator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2006 | Saga事务编排 Saga Transaction Orchestration | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2007 | 可配置规则引擎 Configurable Rule Engine | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2028 | 数字孪生系列 Digital Twin Series | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2038 | LLM模型分级路由 LLM Model Tiered Routing | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2039 | Data Mesh 数据网格 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2040 | CQRS/Event Sourcing模型 CQRS/Event Sourcing Model | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2107 | Observability 可观测性 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2138 | Agent 365 OTel Enterprise Pipeline Agent 365 OTel企业级管道 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2184 | OpenTelemetry | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2189 | Agent SRE Reliability Engineering Agent SRE可靠性工程 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2192 | Trace Hierarchy Model Trace层级模型 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2224 | Prometheus Prometheus监控系统 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2272 | eBPF eBPF无侵入Span补全 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2282 | Docker Docker容器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2283 | W3C TraceContext W3C TraceContext追踪标准 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2346 | Observability Three Pillars 可观测性三支柱 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2347 | Trace Hierarchical Model Trace层级模型 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2352 | Test Automation & CI/CD Integration 测试自动化与CI/CD集成 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2388 | Disaster Recovery Level L6 灾备分级L6日志审计 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2408 | Key Observability Metrics 关键可观测性指标 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3894 | 灾备3-2-1-1-0+D到E 灾备架构 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3912 | 灾备架构 灾备架构 Disaster Recovery Architecture | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3913 | D到E盘双副本策略 双副本架构 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3915 | 数据恢复流程 数据恢复 Workflow | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3916 | 灾备演练计划 灾备演练 Disaster Recovery Drill Plan | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3917 | 混沌工程实践 混沌工程 Chaos Engineering Practice | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3927 | 变更管理 变更管理 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3928 | 灰度发布流程 灰度发布 Workflow | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3929 | 金丝雀验证 金丝雀验证 Canary Verification | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3930 | 回滚策略 回滚策略 Strategy | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3931 | 依赖库升级流程 依赖库升级 Workflow | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4001 | 双机热备 Active-Standby | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4249 | Migration Strategy 迁移策略 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4517 | CI/CD Pipeline 持续集成部署流水线 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4518 | Monitoring Stack 监控栈 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4519 | DR Manager 灾备管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4520 | Infrastructure as Code 基础设施即代码 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4521 | Cybersecurity Shield 网络安全防护 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4522 | Resilience Testing Engine 韧性测试引擎 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4523 | Capacity Planner 容量规划器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4524 | A-Share Intraday Monitor Dashboard Configurator A股盘中监控看板配置器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4525 | Real-Time Dashboard Visual Renderer 实时仪表盘可视化渲染器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4526 | Infrastructure Health Patrol Inspector 基础设施健康巡检器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4527 | 模块隔离部署编排器 Module Isolation Deployment Orchestrator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4528 | 组件复用注册中心 Component Reuse Registry Center | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4529 | 开源框架评估与集成器 Integration | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4530 | 统一交互入口管理器 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4531 | 模块边界与依赖识别器 Module Boundary and Dependency Identifier | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4532 | 系统集成测试编排器 Integration | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4533 | 部署监控优化器 Monitoring | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4534 | 五区域布局管理器 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4535 | SLA监控与保障器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4536 | 复杂操作进度提示器 Complex Operation Progress Prompter | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4537 | 故障自动检测诊断器 Fault Auto Detection Diagnoser | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4538 | 五区域布局渲染引擎 Engine | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4539 | 系统级导航与功能入口管理器 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4540 | 多标签页管理器 Management Tag | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4541 | 可拖拽面板引擎 Engine | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4542 | 桌面端大屏优化器 Desktop Large Screen Optimizer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4543 | 桌面端专属交互优化器 Desktop Exclusive Interaction Optimizer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4544 | 分阶段实施编排器 Phased Implementation Orchestrator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4545 | 层间依赖与部署顺序编排器 Inter-layer Dependency and Deployment Order Orchestrator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4546 | 系统资源监控告警器 Monitoring Alerting | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4547 | Streamlit快速原型开发器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4548 | PyQt5桌面GUI集成器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4549 | 渐进式增强管理器 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4550 | 文档中心索引管理器 Management Index | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4551 | 项目目录结构生成器 Generator Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4552 | 模块实现状态追踪器 State | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4553 | 依赖版本兼容性检查器 Dependency Version Compatibility Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4554 | 目录结构规范校验器 Checker Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4555 | 文件命名规范检查器 File | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4556 | 优先级自动评估器 Priority Auto Evaluator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4557 | 性能基准测试器 Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4558 | Docker容器化研究环境管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4559 | CI/CD流水线集成器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-4560 | Ant Design+ECharts可视化组件集成器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4561 | 硬件资源优化建议器 Hardware Resource Optimization Advisor | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4562 | 架构性能瓶颈识别器 Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4563 | NozyIO多语言代码编辑集成器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4564 | 系统健康度评分器 System Health Score Rater | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4565 | 个性化界面配置管理器 Management Config | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4566 | 模块实现进度追踪器 Module Implementation Progress Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4567 | 模块间集成测试计划器 Integration | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4568 | 性能测试Locust/JMeter集成器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4569 | ELK日志管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4570 | 灾备方案管理器 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4571 | 预测性维护与自愈修复器 Predictive Maintenance and Self-Healing Repairer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4572 | 12层架构与九大平台映射分析器 Analyzer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4573 | 文档链接有效性检查器 Document Link Validity Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4574 | 文档单一信息源管理器 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4575 | 数据库备份与恢复方案器 Database | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4576 | 模块依赖分析器 Analyzer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4577 | 开源组件评估器 Open Source Component Evaluator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4578 | 目录结构验证器 Validator Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4579 | 配置迁移工具 Config Utils | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4580 | 交互界面迁移方案器 Interactive Interface Migration Planner | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4581 | 阶段交付物定义器 Phase Deliverable Definer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4582 | 自动化代码审查流水线 Automated Code Review Pipeline | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4583 | 代码质量度量看板 Code Quality Metrics Dashboard | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4584 | 主题与样式引擎 Engine | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4585 | 交互反馈系统 Interactive Feedback System | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4586 | 可视化组件库 Visualization Component Library | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4587 | 文档一致性校验器 Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4588 | 文档完整性扫描器 Document Completeness Scanner | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4589 | 审计报告自动生成器 Generator Audit Report | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4590 | 遗产代码迁移适配器 Adapter | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4591 | 环境初始化一键脚本 Environment | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4592 | 数据迁移模块 Data Migration Module | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4593 | CI/CD流水线编排 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-4594 | 依赖冲突检测 Dependency Conflict Detection | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4595 | 里程碑健康检查 Milestone Health Check | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4596 | 交付物自动检查 Deliverable Auto Check | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4597 | 测试报告生成 Report | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4598 | 日志聚合模块 Aggregator Logger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4599 | 审计日志分析 Audit Logger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4600 | 模块依赖图生成 Module Dependency Graph Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4601 | 蓝绿部署策略 Strategy | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4602 | 配置漂移检测 Config | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4603 | 灰度发布控制器 Canary Release Controller | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4604 | 开发环境标准化 Environment | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4605 | 接口健康探测 Interface | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4606 | 依赖冲突检测器 Detector | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4607 | 容器健康检查 Container Health Check | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4608 | 通信性能监控模块 Monitoring Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4609 | 接口性能监控 Monitoring Interface Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4610 | 容器资源限制 Container Resource Limit | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4611 | 日志异步写入 Logger Async | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4612 | 部署性能基准 Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4613 | 流水线性能监控 Monitoring Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4614 | 配置模板生成器 Generator Config | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4615 | 交付物模板管理 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4616 | 测试环境管理 Management Environment | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4617 | 配置变更审计 Audit Config | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4618 | 容器安全扫描 Security | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4619 | 密钥轮换模块 Key Rotation Module | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4620 | 部署安全扫描 Security | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4621 | 日志脱敏模块 Logger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4622 | 事件总线监控 Monitoring Event | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4623 | 工作流健康检查 Workflow Health Check | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4624 | 报告导出模块 Report | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4625 | 自定义监控面板 Monitoring | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4626 | 自定义检查项 Custom Check Item | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4627 | 自定义统计指标 Custom Statistics Metric | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4628 | 交互设计规范合规检查器 Compliance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4629 | 文件智能解析器 Parser File | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4630 | 自动化运维执行器 Execution Operations | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4631 | 代码块语法校验器 Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4632 | Mermaid流程图渲染器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4633 | Markdown表格校验器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4634 | 树状图自动生成器 Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4635 | 层级深度校验器 Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4636 | 节点关联分析器 Analyzer Node | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4637 | 树状图差异对比器 Tree View Diff Comparator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4638 | 优先级动态调整器 Priority Dynamic Adjuster | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4639 | 模块依赖关系图 Module Dependency Relationship Graph | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4640 | 开发进度追踪器 Development Progress Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4641 | 验收标准量化器 Acceptance Criteria Quantifier | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4642 | 里程碑风险预警 Risk | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4643 | 阶段交付物检查器 Phase Deliverable Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4644 | 进度偏差分析器 Analyzer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4645 | Docker健康检查器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4646 | SSL证书自动更新 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4647 | 日志智能分析器 Analyzer Logger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4648 | 内存泄漏检测器 Detector Memory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4649 | 运维操作审计 Audit Operations | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4650 | 流水线执行监控 Execution Monitoring | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4651 | 数据延迟检测 Latency | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4652 | 布局持久化 Layout Persistence | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4653 | 响应式断点适配 Response | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4654 | 面板拖拽状态同步 Sync State | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4655 | 全局快捷键管理 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4656 | 标签页状态管理 Management State Tag | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4657 | 拖拽面板布局引擎 Engine | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4658 | 文件上传预览 File | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4659 | 导航权限控制 Navigation Permission Control | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4660 | 表单自动保存 Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4661 | 操作撤销重做栈 Operation Undo Redo Stack | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4662 | 交互操作埋点 Interactive Operation Tracking | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4663 | 图表主题动态切换 Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4664 | 大数据量图表优化 Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4665 | 图表导出与分享 Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4666 | 实时数据流图表 Real-time Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4667 | 学习进度量化评估 Learning Progress Quantitative Assessment | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4668 | 运维变更审批流 Operations | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4669 | React组件库定制 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4670 | ECharts大规模数据渲染 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4671 | 无障碍访问适配 Accessibility Adaptation | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4672 | 前端性能基准测试 Frontend Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4673 | 前端安全审计 Audit Security Frontend | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4674 | 文档状态变更通知与依赖影响分析器 Analyzer Notification State | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4675 | 文档完整性自动化校验器 Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4676 | 文档版本依赖一致性检查器 Document Version Dependency Consistency Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4677 | 功能废弃影响范围追踪器 Feature Deprecation Impact Scope Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4678 | 技术栈版本兼容性矩阵自动检测器 Detector | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4679 | 技术栈技术债务追踪器 Tech Stack Technical Debt Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4680 | 开发时间预算与实际偏差追踪器 Development Time Budget vs Actual Deviation Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4681 | 优先级冲突解决器 Priority Conflict Resolver | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4682 | 优先级时间预算与延期预警器 Priority Time Budget and Delay Warmer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4683 | 阶段门禁自动验证器 Validator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4684 | 跨模块阶段协调器 Cross-Module Phase Coordinator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4685 | 阶段门禁检查器 Phase Gate Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4686 | 阶段交付物验收清单生成器 Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4687 | 阶段资源分配与调度器 Scheduler | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4688 | 阶段过渡触发器 Phase Transition Trigger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4689 | 技术选型加权评分器 Technology Selection Weighted Scorer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4690 | 技术选型决策记录追踪器 Technology Selection Decision Record Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4691 | 技术选型决策框架 Technology Selection Decision Framework | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4692 | 开源项目许可证兼容性检查器 Open Source Project License Compatibility Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4693 | KrakenD/Kong替代API网关评估 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4694 | 技术栈冗余检测与收敛建议器 Tech Stack Redundancy Detection and Convergence Advisor | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4695 | 技术栈版本兼容性矩阵检查器 Tech Stack Version Compatibility Matrix Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4696 | 技术栈废弃预警器 Tech Stack Deprecation Warmer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4697 | 技术栈许可证合规检查器 Compliance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4698 | 12层架构健康检查与故障隔离器 12-Layer Architecture Health Check and Fault Isolator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4699 | 路线图版本差异对比器 Roadmap Version Diff Comparator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4700 | 里程碑依赖图自动生成器 Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4701 | 交付物模板标准化器 Deliverable Template Standardizer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4702 | 命名规范自动修复建议器 Naming Convention Auto Repair Advisor | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4703 | 批量重命名脚手架生成器 Generator Batch | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4704 | 命名规范CI门禁集成器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-4705 | 流水线执行延时统计分析器 Analyzer Execution | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4706 | 流水线执行时间偏差告警器 Execution Alerting | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4707 | 流水线执行日报自动生成器 Generator Execution | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4708 | 依赖版本自动升级建议器 Dependency Version Auto Upgrade Advisor | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4709 | 导航状态持久化与恢复器 State | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4710 | 导航使用热力图生成器 Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4711 | 表单Schema版本管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4712 | 表单草稿自动保存与恢复器 Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4713 | 按钮状态机管理器 State Machine Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4714 | 图表主题标准化导出导入器 Importer Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4715 | 色盲友好配色自动验证器 Validator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4716 | 数据格式国际化本地化器 Local | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4717 | 表格列配置持久化器 Config Table | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4718 | 交互方式使用统计热力图 Interaction Method Usage Statistics Heatmap | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4719 | 交互方式成本效率分析器 Analyzer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4720 | 辅助效果量化评估器 Helper | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4721 | 自动化运维变更影响预分析器 Analyzer Operations | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4722 | 布局版本迁移转换器 Converter | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4723 | 协作过程动画回放器 Collaboration Process Animation Player | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4724 | Pipeline节点健康度探针 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4725 | Pipeline吞吐量瓶颈分析器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4726 | 验证流程定制化编辑器 Workflow | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4727 | 验证流程耗时基准器 Workflow | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4728 | 树状图节点实时搜索与过滤器 Filter Real-time Node | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4729 | 树状图版本差异可视化器 Tree View Version Diff Visualizer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4730 | 存储层性能基准测试器 Storage Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4731 | 前端组件渲染性能监控器 Monitor Frontend Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4732 | 布局组件依赖关系检测器 Detector | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4733 | 可视化组件注册中心 Visualization Component Registry Center | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4734 | 组件使用频次统计数据采集器 Component Usage Frequency Statistics Collector | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4735 | 数据流断点调试器 Data Flow Breakpoint Debugger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4736 | 部署架构漂移检测器 Detector | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4737 | 部署依赖顺序校验器 Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4738 | pre-commit git钩子自动配置器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4739 | CI管道命令封装脚本 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-4740 | mypy增量类型检查模式 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4741 | 目录结构一致性巡检器 Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4742 | 目录模板快速初始化脚手架 Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4743 | 新模块子模块脚手架自动生成器 Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4744 | 文档结构导航地图自动生成器 Generator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4745 | 文档章节链接有效性批量检查器 Batch | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4746 | 目录迁移影响预分析器 Analyzer Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4747 | 目录迁移回滚方案器 Directory | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4748 | 监控方案迁移路径规划器 Monitoring Path | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4749 | 监控阈值自适应调整器 Monitoring | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4750 | 性能指标SLA实时仪表板 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4751 | 性能基准回归检测器 Detector Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4752 | 异常使用统计与热点分析器 Analyzer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4753 | 多数据库SLA监控与告警器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4754 | 实验追踪方案决策记录器 Experiment Tracking Scheme Decision Recorder | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4755 | 实验追踪方案切换触发器 Experiment Tracking Scheme Switch Trigger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4756 | 指标阈值动态调整与合理性评估器 Metric Threshold Dynamic Adjustment and Rationality Evaluator | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4757 | 业务指标量化与追踪器 Business Metric Quantifier and Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4758 | API文档自动版本同步器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4759 | 字段类型变更影响分析器 Analyzer Field | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4760 | 模型文件路径安全性检查器 Security Model File Path | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4761 | 模型推理性能基准测试器 Inference Model Performance | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4762 | Agent调用审计日志器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4763 | 配置变更审计日志追踪器 Audit Logger Config | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4764 | 委员会决策耗时监控器 Monitor | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4765 | 决策流节点耗时瓶颈分析器 Analyzer Node | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4766 | 决策路径频次统计器 Path | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4767 | 元数据Schema迁移管理器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4768 | wandb使用成本追踪器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4769 | 知识来源质量评分器 Knowledge | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4770 | Layer文档位置索引与完整性检查器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4771 | 架构版本演进追踪器 Architecture Version Evolution Tracker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4772 | MLflow性能基准测试器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4773 | 桌面端多显示器布局管理 Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4774 | 技术债务追踪 Technical Debt Tracking | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4775 | 日志保留与归档策略 Strategy Logger | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4776 | 知识生命周期管理 Lifecycle Knowledge Management | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4777 | 系统版本兼容 System Version Compatibility | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4778 | 架构决策记录 Architecture Decision Record | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4779 | 监控事件聚合器 Monitoring Aggregator Event | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4780 | 数据质量监控桥接器 Data Quality Monitoring | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4781 | 信号质量评估消费桥接器 Signal | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4782 | 风控事件告警桥接器 Risk Control Alerting Event | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4783 | 灰度发布与蓝绿部署框架 Canary Release and Blue-Green Deployment Framework | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4784 | 统一健康检查框架 Unified Health Check Framework | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4785 | 跨域向后兼容性检查器 Cross-Domain Backward Compatibility Checker | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4786 | 动态韧性调整器 Dynamic Resilience Adjuster | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4787 | 优雅降级规划器 Fallback | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4788 | 依赖图韧性评分增强 Dependency Graph Resilience Score Enhancement | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4789 | 韧性评分标准化器 Resilience Score Standardizer | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4796 | OpenTelemetry Collector OpenTelemetry收集器 | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4797 | Prometheus+Grafana监控栈 Prometheus Grafana Monitor Stack | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4798 | Loki日志聚合 Loki Log Aggregation | D_INFRA_OPS | 候选待评（candidate） | harvest待评估（likely_new） |
