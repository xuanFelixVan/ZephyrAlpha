---
doc_type: domain_architecture_doc
title: D-INFRA_OPS 基础设施运维架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-INFRA_OPS 基础设施运维架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-INFRA_OPS |
| 域名称 | 基础设施运维 |
| 架构层 | L0_infrastructure |
| 模块总数 | 404 |
| 设计态模块 | 387 |
| 原型态模块 | 8 |
| 生产态模块 | 3 |
| 容量 | 3/150 (正常) |
| 描述 | 基础设施运维与监控 |

## 模块清单

共 404 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-INFRA-OPS/12层架构与九大平台映射分析器 Analyzer |  | design_only | design | 0 | 0 |
| ...FRA-OPS/12层架构健康检查与故障隔离器 12-Layer Architecture Health Check and Fault Isolator |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/A-Share Intraday Monitor Dashboard Configurator A股盘中监控看板配置器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/AI API Cost Manager AI API成本管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/API文档自动版本同步器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Administrator 管理员 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Agent 365 OTel Enterprise Pipeline Agent 365 OTel企业级管道 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Agent Communication Protocol Agent通信协议 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Agent RBAC / Permission Guard Agent RBAC/权限守卫器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Agent SRE Formal SLO Agent SRE正式SLO |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Agent SRE Reliability Engineering Agent SRE可靠性工程 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Agent调用审计日志器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Alert Manager 告警管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/AlertEscalated 告警升级事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/AlertEscalation 告警升级契约 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/AlertFired 告警触发事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Ant Design+ECharts可视化组件集成器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Backup Manager 备份管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Backup Manager 自动备份管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/BackupCompleted 备份完成事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/BackupConfirmation 备份确认契约 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/BackupFailed 备份失败事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CI/CD Pipeline 持续集成部署流水线 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CI/CD Pipeline 管线 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CI/CD流水线编排 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CI/CD流水线集成器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CI管道命令封装脚本 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CQRS/Event Sourcing模型 CQRS/Event Sourcing Model |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/CapabilityReport 能力报告 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Capacity Assurance & SLI/SLO 容量保障与服务等级 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Capacity Planner 容量规划器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Cold Data Archive Manager 冷数据归档管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Communication Encryption Config 通信加密配置 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Cost Optimizer 成本优化器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Cybersecurity Shield 网络安全防护 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/D Drive Complete Failure D盘完全故障 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/D-INFRA-OPS |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/DR Manager 灾备管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/DRDrillCompleted 灾备演练完成事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Data Mesh 数据网格 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Deployment Manager 部署管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/DeploymentStageAdvanced 灰度发布阶段推进事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Disaster Recovery Level L6 灾备分级L6日志审计 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Disaster Recovery 灾难恢复 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Docker Docker容器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Docker健康检查器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Docker容器化研究环境管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/D→E盘本地双副本 D→E Dual Copy |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/D到E盘双副本策略 双副本架构 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/ECharts大规模数据渲染 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/ELK日志管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/External Instruction Monitoring 外部指令盯盘 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/FPGA Conditional Gate FPGA条件门禁 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/GATE-FPGA FPGA硬件升级汇总 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/GATE-FPGA-03 FPGA开发能力 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/HPC Manager HPC管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Health Dashboard 健康仪表盘 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/HealthDashboard 健康仪表板契约 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/IaC Manager IaC管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Infrastructure Health Patrol Inspector 基础设施健康巡检器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Infrastructure as Code 基础设施即代码 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/InfrastructureStatus 基础设施状态契约 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Key Observability Metrics 关键可观测性指标 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/KrakenD/Kong替代API网关评估 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/LLM模型分级路由 LLM Model Tiered Routing |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Layer文档位置索引与完整性检查器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Log Aggregator 日志聚合器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/LogAnomalyDetected 日志异常检测事件 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Loki日志聚合 Loki Log Aggregation |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MLflow性能基准测试器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-INF-024 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-INF-026 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-INF-033 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-INF-034 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-INF-035 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-INF-036 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/MOD-MASTER-001 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Markdown表格校验器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Mermaid流程图渲染器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Microsoft Agent 365 OTel Microsoft Agent 365 OTel管道 |  | design_only | design | 0 | 0 |
| ...Cisco OpenTelemetry Multi-Agent Semantic Convention Microsoft/Cisco多Agent语义约定 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Migration Strategy 迁移策略 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Model Profiler & Capability Exam 模型画像与能力考试 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/ModelProfile 模型画像 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Monitoring Stack 监控栈 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Monitoring System 监控系统 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Network Manager 网络管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/NozyIO多语言代码编辑集成器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Observability Three Pillars 可观测性三支柱 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Observability 可观测性 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/OpenTelemetry |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/OpenTelemetry Collector OpenTelemetry收集器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/PIT Manager Point-in-Time管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Pipeline吞吐量瓶颈分析器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Pipeline编排器 Pipeline Orchestrator |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Pipeline节点健康度探针 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Prometheus Prometheus监控系统 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Prometheus+Grafana监控栈 Prometheus Grafana Monitor Stack |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/PyQt5桌面GUI集成器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Quantum-Classical Hybrid Computing Roadmap 量子-经典混合计算路线图 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/RED Metrics Specification RED指标规格 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/React组件库定制 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Real-Time Dashboard Visual Renderer 实时仪表盘可视化渲染器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Resilience Manager 弹性管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Resilience Testing Engine 韧性测试引擎 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/SLA监控与保障器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/SSL证书自动更新 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Saga事务编排 Saga Transaction Orchestration |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Security Infra Manager 安全基础设施管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Shared Infrastructure 共享基础设施 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Streamlit快速原型开发器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Test Automation & CI/CD Integration 测试自动化与CI/CD集成 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Tool Scripts 工具脚本 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Trace Hierarchical Model Trace层级模型 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/Trace Hierarchy Model Trace层级模型 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/W3C TraceContext W3C TraceContext追踪标准 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/eBPF eBPF无侵入Span补全 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/mypy增量类型检查模式 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/pre-commit git钩子自动配置器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/wandb使用成本追踪器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/业务指标量化与追踪器 Business Metric Quantifier and Tracker |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/个性化界面配置管理器 Management Config |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/主题与样式引擎 Engine |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/事件总线监控 Monitoring Event |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/五区域布局渲染引擎 Engine |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/五区域布局管理器 Management |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交互反馈系统 Interactive Feedback System |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交互操作埋点 Interactive Operation Tracking |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交互方式使用统计热力图 Interaction Method Usage Statistics Heatmap |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交互方式成本效率分析器 Analyzer |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交互界面迁移方案器 Interactive Interface Migration Planner |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交互设计规范合规检查器 Compliance |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交付物模板标准化器 Deliverable Template Standardizer |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交付物模板管理 Management |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交付物自动检查 Deliverable Auto Check |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交易日志不可自动清理 Logger |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/交易时段依赖库不可自动升级 Trading Session Dependency Library No Auto Upgrade |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/代码块语法校验器 Checker |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/代码质量度量看板 Code Quality Metrics Dashboard |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/优先级冲突解决器 Priority Conflict Resolver |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/优先级动态调整器 Priority Dynamic Adjuster |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/优先级时间预算与延期预警器 Priority Time Budget and Delay Warmer |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/优先级自动评估器 Priority Auto Evaluator |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/优雅降级规划器 Fallback |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/依赖冲突检测 Dependency Conflict Detection |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/依赖冲突检测器 Detector |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/依赖图韧性评分增强 Dependency Graph Resilience Score Enhancement |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/依赖库升级流程 依赖库升级 Workflow |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/依赖版本兼容性检查器 Dependency Version Compatibility Checker |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/依赖版本自动升级建议器 Dependency Version Auto Upgrade Advisor |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/信号质量评估消费桥接器 Signal |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/元数据Schema迁移管理器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/全局快捷键管理 Management |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/全量恢复演练 Full Recovery Drill |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/内存泄漏检测器 Detector Memory |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/决策流节点耗时瓶颈分析器 Analyzer Node |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/决策路径频次统计器 Path |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/分阶段实施编排器 Phased Implementation Orchestrator |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/前端安全审计 Audit Security Frontend |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/前端性能基准测试 Frontend Performance |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/前端组件渲染性能监控器 Monitor Frontend Performance |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/功能废弃影响范围追踪器 Feature Deprecation Impact Scope Tracker |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/动态韧性调整器 Dynamic Resilience Adjuster |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/协作过程动画回放器 Collaboration Process Animation Player |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/双机热备 Active-Standby |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/变更必须灰度发布 Changes Must Be Canary Released |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/变更管理 变更管理 Management |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/变更管理是灰度而非直接发布 Grayscale Release |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/可拖拽面板引擎 Engine |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/可视化组件库 Visualization Component Library |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/可视化组件注册中心 Visualization Component Registry Center |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/可配置规则引擎 Configurable Rule Engine |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/命名规范CI门禁集成器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/命名规范自动修复建议器 Naming Convention Auto Repair Advisor |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/响应式断点适配 Response |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/回滚策略 回滚策略 Strategy |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/图表主题动态切换 Table |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/图表主题标准化导出导入器 Importer Table |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/图表导出与分享 Table |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/备份策略 Backup Strategy |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/复杂操作进度提示器 Complex Operation Progress Prompter |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/多数据库SLA监控与告警器 |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/多标签页管理器 Management Tag |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/大数据量图表优化 Table |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/委员会决策耗时监控器 Monitor |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/字段类型变更影响分析器 Analyzer Field |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/存储层性能基准测试器 Storage Performance |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/存储成本量化核算器 Storage Cost Calculator |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/学习进度量化评估 Learning Progress Quantitative Assessment |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/实时数据流图表 Real-time Table |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/实验追踪方案决策记录器 Experiment Tracking Scheme Decision Recorder |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/实验追踪方案切换触发器 Experiment Tracking Scheme Switch Trigger |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/审计报告自动生成器 Generator Audit Report |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/审计日志分析 Audit Logger |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/审计重建演练 Audit Reconstruction Drill |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/容器健康检查 Container Health Check |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/容器安全扫描 Security |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/容器资源限制 Container Resource Limit |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/密钥轮换模块 Key Rotation Module |  | design_only | design | 0 | 0 |
| D-INFRA-OPS/导航使用热力图生成器 Generator |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 404 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 68 | data,contract,event,config_depends |
| D-GOVERNANCE | 56 | import_depends,contract,data,event,config_depends |
| D-SECURITY | 53 | contract,config_depends,event,data |
| D-AUTONOMY_CORE | 43 | data,contract,event,config_depends |
| D-SIGNAL | 39 | event,contract,data,config_depends |
| D-INTEGRATION | 38 | contract,data,config_depends,event |
| D-INTELLIGENCE | 30 | event,config_depends,contract,data |
| D-INFRA_RUNTIME | 30 | contract,config_depends,event,data |
| D-FACTOR | 27 | event,contract,data,config_depends |
| D-OPS | 26 | import_depends,contract,event,data,config_depends |
| D-MKT_DATA | 21 | contract,event,data,config_depends |
| D-PF_CORE | 19 | contract,config_depends,data,event |
| D-KNOWLEDGE | 18 | data,contract,event,config_depends |
| D-EX_SOR | 13 | contract,data,config_depends |
| D-TRADING | 12 | contract,event,data |
| D-REPORTING | 12 | config_depends,event,data,contract |
| D-PF_ALLOC | 11 | contract,event,config_depends |
| D-AUTONOMY_PERM | 11 | config_depends,data,contract,event |
| D-ALT_DATA | 11 | data,event,contract,config_depends |
| D-POSITION | 8 | data,config_depends,event,contract |
| D-ML_TRAIN | 8 | config_depends,contract,data,event |
| D-EX_CORE | 7 | contract,data,event |
| D-SIMULATION | 6 | contract,event,data |
| D-SELL_DECISION | 6 | event,contract,data |
| D-ML_SERVE | 6 | event,data,contract |
| D-DATA_ENG | 6 | event,contract,data |
| D-SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 90 | event,contract,config_depends,data |
| D-FRONTEND | 23 | import_depends,contract,config_depends,event,data |
| D-CROSS_ASSET | 5 | event,contract,data |
| D-DATA_SEC | 2 | contract |
| D-DATA_GOV | 2 | config_depends,event |

## 域内依赖图

详见 [d_infra_ops_dependency.mmd](d_infra_ops_dependency.mmd)
