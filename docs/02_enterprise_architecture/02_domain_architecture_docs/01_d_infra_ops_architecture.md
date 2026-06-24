---
doc_type: domain_architecture_diagram
title: D-INFRA_OPS 基础设施运维架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 01_d_infra_ops / 基础设施运维 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示基础设施运维（D-INFRA_OPS）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 基础设施运维（D-INFRA_OPS）的模块分布。共 430 个模块 / 430 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│         L0 基础设施层 / Infrastructure Layer (5 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   基础设施运维域  [design]                                       │
│   告警管理  [design]                                             │
│   容量管理  [design]                                             │
│   部署管理  [design]                                             │
│   基础设施监控  [design]                                         │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (29 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   config/infra/grafana/dashboards/provider.yml  [production]     │
│   config/infra/grafana/datasources/prometheus.yml  [production]  │
│   config/infra/prometheus/prometheus.yml  [production]           │
│   src/zephyr/governance/auto_rollback_trigger.py  [prototype]    │
│   src/zephyr/governance/rollback_simulator.py  [prototype]       │
│   src/zephyr/governance/rollback_wal.py  [prototype]             │
│   src/zephyr/infra_ops/__init__.py  [prototype]                  │
│   src/zephyr/infra_ops/_extensions/__init__.py  [scaffold_pla... │
│   src/zephyr/infra_ops/api/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/infra_ops/core/__init__.py  [scaffold_placeholder]  │
│   src/zephyr/infra_ops/dashboard/app.py  [prototype]             │
│   src/zephyr/infra_ops/dashboard/components/fitness_functions... │
│   src/zephyr/infra_ops/dashboard/components/gate_statistics.p... │
│   src/zephyr/infra_ops/dashboard/components/knowledge_overvie... │
│   src/zephyr/infra_ops/dashboard/components/olap_trend.py  [p... │
│   src/zephyr/infra_ops/dashboard/components/task_progress.py ... │
│   src/zephyr/infra_ops/infrastructure/__init__.py  [scaffold_... │
│   src/zephyr/infra_ops/interface_base.py  [prototype]            │
│   ...还有 11 个模块 / 11 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (396 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   12层架构与九大平台映射分析器 Analyzer  [design]                │
│   12层架构健康检查与故障隔离器 12-Layer Architecture Health C... │
│   A-Share Intraday Monitor Dashboard Configurator A股盘中监控... │
│   AI API Cost Manager AI API成本管理器  [design]                 │
│   API文档自动版本同步器  [design]                                │
│   Administrator 管理员  [design]                                 │
│   Agent 365 OTel Enterprise Pipeline Agent 365 OTel企业级管道... │
│   Agent Communication Protocol Agent通信协议  [design]           │
│   Agent RBAC / Permission Guard Agent RBAC/权限守卫器  [design]  │
│   Agent SRE Formal SLO Agent SRE正式SLO  [design]                │
│   Agent SRE Reliability Engineering Agent SRE可靠性工程  [des... │
│   Agent调用审计日志器  [design]                                  │
│   Alert Manager 告警管理器  [design]                             │
│   AlertEscalated 告警升级事件  [design]                          │
│   AlertEscalation 告警升级契约  [design]                         │
│   AlertFired 告警触发事件  [design]                              │
│   Ant Design+ECharts可视化组件集成器  [design]                   │
│   Backup Manager 备份管理器  [design]                            │
│   ...还有 378 个模块 / 378 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 430 个模块 / 430 modules）。

### L0 基础设施层 / Infrastructure Layer (5 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/infra_ops/ | 基础设施运维域 | design | design_only |
| 2 | src/zephyr/infra_ops/alerting/ | 告警管理 | design | design_only |
| 3 | src/zephyr/infra_ops/capacity/ | 容量管理 | design | design_only |
| 4 | src/zephyr/infra_ops/deployment/ | 部署管理 | design | design_only |
| 5 | src/zephyr/infra_ops/monitoring/ | 基础设施监控 | design | design_only |

### L1 基础层 / Foundation Layer (29 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/infra/grafana/dashboards/provider.yml | config/infra/grafana/dashboards/provi... | production | orphan |
| 2 | config/infra/grafana/datasources/prometheus.yml | config/infra/grafana/datasources/prom... | production | orphan |
| 3 | config/infra/prometheus/prometheus.yml | config/infra/prometheus/prometheus.yml | production | orphan |
| 4 | src/zephyr/governance/auto_rollback_trigger.py | src/zephyr/governance/auto_rollback_t... | prototype | draft |
| 5 | src/zephyr/governance/rollback_simulator.py | src/zephyr/governance/rollback_simula... | prototype | draft |
| 6 | src/zephyr/governance/rollback_wal.py | src/zephyr/governance/rollback_wal.py | prototype | draft |
| 7 | src/zephyr/infra_ops/__init__.py | src/zephyr/infra_ops/__init__.py | prototype | draft |
| 8 | src/zephyr/infra_ops/_extensions/__init__.py | src/zephyr/infra_ops/_extensions/__in... | scaffold_placeholder | orphan |
| 9 | src/zephyr/infra_ops/api/__init__.py | src/zephyr/infra_ops/api/__init__.py | scaffold_placeholder | orphan |
| 10 | src/zephyr/infra_ops/core/__init__.py | src/zephyr/infra_ops/core/__init__.py | scaffold_placeholder | orphan |
| 11 | src/zephyr/infra_ops/dashboard/app.py | src/zephyr/infra_ops/dashboard/app.py | prototype | draft |
| 12 | src/zephyr/infra_ops/dashboard/components/fitness_functio... | src/zephyr/infra_ops/dashboard/compon... | prototype | draft |
| 13 | src/zephyr/infra_ops/dashboard/components/gate_statistics.py | src/zephyr/infra_ops/dashboard/compon... | prototype | draft |
| 14 | src/zephyr/infra_ops/dashboard/components/knowledge_overv... | src/zephyr/infra_ops/dashboard/compon... | prototype | draft |
| 15 | src/zephyr/infra_ops/dashboard/components/olap_trend.py | src/zephyr/infra_ops/dashboard/compon... | prototype | draft |
| 16 | src/zephyr/infra_ops/dashboard/components/task_progress.py | src/zephyr/infra_ops/dashboard/compon... | prototype | draft |
| 17 | src/zephyr/infra_ops/infrastructure/__init__.py | src/zephyr/infra_ops/infrastructure/_... | scaffold_placeholder | orphan |
| 18 | src/zephyr/infra_ops/interface_base.py | src/zephyr/infra_ops/interface_base.py | prototype | draft |
| 19 | src/zephyr/infra_ops/models/__init__.py | src/zephyr/infra_ops/models/__init__.py | scaffold_placeholder | orphan |
| 20 | src/zephyr/infra_ops/services/__init__.py | src/zephyr/infra_ops/services/__init_... | scaffold_placeholder | orphan |
| 21 | src/zephyr/infrastructure/rollback/governance/__init__.py | src/zephyr/infrastructure/rollback/go... | prototype | draft |
| 22 | src/zephyr/infrastructure/rollback/governance/auditor.py | src/zephyr/infrastructure/rollback/go... | prototype | draft |
| 23 | src/zephyr/infrastructure/rollback/governance/budget_trac... | src/zephyr/infrastructure/rollback/go... | prototype | draft |
| 24 | src/zephyr/infrastructure/rollback/governance/contracts.py | src/zephyr/infrastructure/rollback/go... | prototype | draft |
| 25 | src/zephyr/infrastructure/rollback/governance/drift_fix.py | src/zephyr/infrastructure/rollback/go... | prototype | draft |
| 26 | src/zephyr/infrastructure/rollback/governance/result_type... | src/zephyr/infrastructure/rollback/go... | prototype | draft |
| 27 | tests/test_auto_rollback_trigger.py | tests/test_auto_rollback_trigger.py | prototype | draft |
| 28 | tests/test_rollback_simulator.py | tests/test_rollback_simulator.py | prototype | draft |
| 29 | tests/test_rollback_wal.py | tests/test_rollback_wal.py | prototype | draft |

### 未分类 / Unclassified (396 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-INFRA-OPS/12层架构与九大平台映射分析器 Analyzer | 12层架构与九大平台映射分析器 Analyzer | design | design_only |
| 2 | D-INFRA-OPS/12层架构健康检查与故障隔离器 12-Layer Archite... | 12层架构健康检查与故障隔离器 12-Layer... | design | design_only |
| 3 | D-INFRA-OPS/A-Share Intraday Monitor Dashboard Configurat... | A-Share Intraday Monitor Dashboard Co... | design | design_only |
| 4 | D-INFRA-OPS/AI API Cost Manager AI API成本管理器 | AI API Cost Manager AI API成本管理器 | design | design_only |
| 5 | D-INFRA-OPS/API文档自动版本同步器 | API文档自动版本同步器 | design | design_only |
| 6 | D-INFRA-OPS/Administrator 管理员 | Administrator 管理员 | design | design_only |
| 7 | D-INFRA-OPS/Agent 365 OTel Enterprise Pipeline Agent 365 ... | Agent 365 OTel Enterprise Pipeline Ag... | design | design_only |
| 8 | D-INFRA-OPS/Agent Communication Protocol Agent通信协议 | Agent Communication Protocol Agent通... | design | design_only |
| 9 | D-INFRA-OPS/Agent RBAC / Permission Guard Agent RBAC/权限... | Agent RBAC / Permission Guard Agent R... | design | design_only |
| 10 | D-INFRA-OPS/Agent SRE Formal SLO Agent SRE正式SLO | Agent SRE Formal SLO Agent SRE正式SLO | design | design_only |
| 11 | D-INFRA-OPS/Agent SRE Reliability Engineering Agent SRE可... | Agent SRE Reliability Engineering Age... | design | design_only |
| 12 | D-INFRA-OPS/Agent调用审计日志器 | Agent调用审计日志器 | design | design_only |
| 13 | D-INFRA-OPS/Alert Manager 告警管理器 | Alert Manager 告警管理器 | design | design_only |
| 14 | D-INFRA-OPS/AlertEscalated 告警升级事件 | AlertEscalated 告警升级事件 | design | design_only |
| 15 | D-INFRA-OPS/AlertEscalation 告警升级契约 | AlertEscalation 告警升级契约 | design | design_only |
| 16 | D-INFRA-OPS/AlertFired 告警触发事件 | AlertFired 告警触发事件 | design | design_only |
| 17 | D-INFRA-OPS/Ant Design+ECharts可视化组件集成器 | Ant Design+ECharts可视化组件集成器 | design | design_only |
| 18 | D-INFRA-OPS/Backup Manager 备份管理器 | Backup Manager 备份管理器 | design | design_only |
| 19 | D-INFRA-OPS/Backup Manager 自动备份管理器 | Backup Manager 自动备份管理器 | design | design_only |
| 20 | D-INFRA-OPS/BackupCompleted 备份完成事件 | BackupCompleted 备份完成事件 | design | design_only |
| 21 | D-INFRA-OPS/BackupConfirmation 备份确认契约 | BackupConfirmation 备份确认契约 | design | design_only |
| 22 | D-INFRA-OPS/BackupFailed 备份失败事件 | BackupFailed 备份失败事件 | design | design_only |
| 23 | D-INFRA-OPS/CI/CD Pipeline 持续集成部署流水线 | CI/CD Pipeline 持续集成部署流水线 | design | design_only |
| 24 | D-INFRA-OPS/CI/CD Pipeline 管线 | CI/CD Pipeline 管线 | design | design_only |
| 25 | D-INFRA-OPS/CI/CD流水线编排 | CI/CD流水线编排 | design | design_only |
| 26 | D-INFRA-OPS/CI/CD流水线集成器 | CI/CD流水线集成器 | design | design_only |
| 27 | D-INFRA-OPS/CI管道命令封装脚本 | CI管道命令封装脚本 | design | design_only |
| 28 | D-INFRA-OPS/CQRS/Event Sourcing模型 CQRS/Event Sourcing M... | CQRS/Event Sourcing模型 CQRS/Event So... | design | design_only |
| 29 | D-INFRA-OPS/CapabilityReport 能力报告 | CapabilityReport 能力报告 | design | design_only |
| 30 | D-INFRA-OPS/Capacity Assurance & SLI/SLO 容量保障与服务等级 | Capacity Assurance & SLI/SLO 容量保障... | design | design_only |
| 31 | D-INFRA-OPS/Capacity Planner 容量规划器 | Capacity Planner 容量规划器 | design | design_only |
| 32 | D-INFRA-OPS/Cold Data Archive Manager 冷数据归档管理器 | Cold Data Archive Manager 冷数据归档... | design | design_only |
| 33 | D-INFRA-OPS/Communication Encryption Config 通信加密配置 | Communication Encryption Config 通信... | design | design_only |
| 34 | D-INFRA-OPS/Cost Optimizer 成本优化器 | Cost Optimizer 成本优化器 | design | design_only |
| 35 | D-INFRA-OPS/Cybersecurity Shield 网络安全防护 | Cybersecurity Shield 网络安全防护 | design | design_only |
| 36 | D-INFRA-OPS/D Drive Complete Failure D盘完全故障 | D Drive Complete Failure D盘完全故障 | design | design_only |
| 37 | D-INFRA-OPS/D-INFRA-OPS | D-INFRA-OPS | design | design_only |
| 38 | D-INFRA-OPS/DR Manager 灾备管理器 | DR Manager 灾备管理器 | design | design_only |
| 39 | D-INFRA-OPS/DRDrillCompleted 灾备演练完成事件 | DRDrillCompleted 灾备演练完成事件 | design | design_only |
| 40 | D-INFRA-OPS/Data Mesh 数据网格 | Data Mesh 数据网格 | design | design_only |
| 41 | D-INFRA-OPS/Deployment Manager 部署管理器 | Deployment Manager 部署管理器 | design | design_only |
| 42 | D-INFRA-OPS/DeploymentStageAdvanced 灰度发布阶段推进事件 | DeploymentStageAdvanced 灰度发布阶段... | design | design_only |
| 43 | D-INFRA-OPS/Disaster Recovery Level L6 灾备分级L6日志审计 | Disaster Recovery Level L6 灾备分级L6... | design | design_only |
| 44 | D-INFRA-OPS/Disaster Recovery 灾难恢复 | Disaster Recovery 灾难恢复 | design | design_only |
| 45 | D-INFRA-OPS/Docker Docker容器 | Docker Docker容器 | design | design_only |
| 46 | D-INFRA-OPS/Docker健康检查器 | Docker健康检查器 | design | design_only |
| 47 | D-INFRA-OPS/Docker容器化研究环境管理器 | Docker容器化研究环境管理器 | design | design_only |
| 48 | D-INFRA-OPS/D→E盘本地双副本 D→E Dual Copy | D→E盘本地双副本 D→E Dual Copy | design | design_only |
| 49 | D-INFRA-OPS/D到E盘双副本策略 双副本架构 | D到E盘双副本策略 双副本架构 | design | design_only |
| 50 | D-INFRA-OPS/ECharts大规模数据渲染 | ECharts大规模数据渲染 | design | design_only |
| 51 | D-INFRA-OPS/ELK日志管理器 | ELK日志管理器 | design | design_only |
| 52 | D-INFRA-OPS/External Instruction Monitoring 外部指令盯盘 | External Instruction Monitoring 外部... | design | design_only |
| 53 | D-INFRA-OPS/FPGA Conditional Gate FPGA条件门禁 | FPGA Conditional Gate FPGA条件门禁 | design | design_only |
| 54 | D-INFRA-OPS/GATE-FPGA FPGA硬件升级汇总 | GATE-FPGA FPGA硬件升级汇总 | design | design_only |
| 55 | D-INFRA-OPS/GATE-FPGA-03 FPGA开发能力 | GATE-FPGA-03 FPGA开发能力 | design | design_only |
| 56 | D-INFRA-OPS/HPC Manager HPC管理器 | HPC Manager HPC管理器 | design | design_only |
| 57 | D-INFRA-OPS/Health Dashboard 健康仪表盘 | Health Dashboard 健康仪表盘 | design | design_only |
| 58 | D-INFRA-OPS/HealthDashboard 健康仪表板契约 | HealthDashboard 健康仪表板契约 | design | design_only |
| 59 | D-INFRA-OPS/IaC Manager IaC管理器 | IaC Manager IaC管理器 | design | design_only |
| 60 | D-INFRA-OPS/Infrastructure Health Patrol Inspector 基础设... | Infrastructure Health Patrol Inspecto... | design | design_only |
| 61 | D-INFRA-OPS/Infrastructure as Code 基础设施即代码 | Infrastructure as Code 基础设施即代码 | design | design_only |
| 62 | D-INFRA-OPS/InfrastructureStatus 基础设施状态契约 | InfrastructureStatus 基础设施状态契约 | design | design_only |
| 63 | D-INFRA-OPS/Key Observability Metrics 关键可观测性指标 | Key Observability Metrics 关键可观测... | design | design_only |
| 64 | D-INFRA-OPS/KrakenD/Kong替代API网关评估 | KrakenD/Kong替代API网关评估 | design | design_only |
| 65 | D-INFRA-OPS/LLM模型分级路由 LLM Model Tiered Routing | LLM模型分级路由 LLM Model Tiered Routing | design | design_only |
| 66 | D-INFRA-OPS/Layer文档位置索引与完整性检查器 | Layer文档位置索引与完整性检查器 | design | design_only |
| 67 | D-INFRA-OPS/Log Aggregator 日志聚合器 | Log Aggregator 日志聚合器 | design | design_only |
| 68 | D-INFRA-OPS/LogAnomalyDetected 日志异常检测事件 | LogAnomalyDetected 日志异常检测事件 | design | design_only |
| 69 | D-INFRA-OPS/Loki日志聚合 Loki Log Aggregation | Loki日志聚合 Loki Log Aggregation | design | design_only |
| 70 | D-INFRA-OPS/MLflow性能基准测试器 | MLflow性能基准测试器 | design | design_only |
| 71 | D-INFRA-OPS/MOD-INF-024 | MOD-INF-024 | design | design_only |
| 72 | D-INFRA-OPS/MOD-INF-026 | MOD-INF-026 | design | design_only |
| 73 | D-INFRA-OPS/MOD-INF-033 | MOD-INF-033 | design | design_only |
| 74 | D-INFRA-OPS/MOD-INF-034 | MOD-INF-034 | design | design_only |
| 75 | D-INFRA-OPS/MOD-INF-035 | MOD-INF-035 | design | design_only |
| 76 | D-INFRA-OPS/MOD-INF-036 | MOD-INF-036 | design | design_only |
| 77 | D-INFRA-OPS/MOD-MASTER-001 | MOD-MASTER-001 | design | design_only |
| 78 | D-INFRA-OPS/Markdown表格校验器 | Markdown表格校验器 | design | design_only |
| 79 | D-INFRA-OPS/Mermaid流程图渲染器 | Mermaid流程图渲染器 | design | design_only |
| 80 | D-INFRA-OPS/Microsoft Agent 365 OTel Microsoft Agent 365 ... | Microsoft Agent 365 OTel Microsoft Ag... | design | design_only |
| 81 | D-INFRA-OPS/Microsoft/Cisco OpenTelemetry Multi-Agent Sem... | Microsoft/Cisco OpenTelemetry Multi-A... | design | design_only |
| 82 | D-INFRA-OPS/Migration Strategy 迁移策略 | Migration Strategy 迁移策略 | design | design_only |
| 83 | D-INFRA-OPS/Model Profiler & Capability Exam 模型画像与能... | Model Profiler & Capability Exam 模型... | design | design_only |
| 84 | D-INFRA-OPS/ModelProfile 模型画像 | ModelProfile 模型画像 | design | design_only |
| 85 | D-INFRA-OPS/Monitoring Stack 监控栈 | Monitoring Stack 监控栈 | design | design_only |
| 86 | D-INFRA-OPS/Monitoring System 监控系统 | Monitoring System 监控系统 | design | design_only |
| 87 | D-INFRA-OPS/Network Manager 网络管理器 | Network Manager 网络管理器 | design | design_only |
| 88 | D-INFRA-OPS/NozyIO多语言代码编辑集成器 | NozyIO多语言代码编辑集成器 | design | design_only |
| 89 | D-INFRA-OPS/Observability Three Pillars 可观测性三支柱 | Observability Three Pillars 可观测性... | design | design_only |
| 90 | D-INFRA-OPS/Observability 可观测性 | Observability 可观测性 | design | design_only |
| 91 | D-INFRA-OPS/OpenTelemetry | OpenTelemetry | design | design_only |
| 92 | D-INFRA-OPS/OpenTelemetry Collector OpenTelemetry收集器 | OpenTelemetry Collector OpenTelemetry... | design | design_only |
| 93 | D-INFRA-OPS/PIT Manager Point-in-Time管理器 | PIT Manager Point-in-Time管理器 | design | design_only |
| 94 | D-INFRA-OPS/Pipeline吞吐量瓶颈分析器 | Pipeline吞吐量瓶颈分析器 | design | design_only |
| 95 | D-INFRA-OPS/Pipeline编排器 Pipeline Orchestrator | Pipeline编排器 Pipeline Orchestrator | design | design_only |
| 96 | D-INFRA-OPS/Pipeline节点健康度探针 | Pipeline节点健康度探针 | design | design_only |
| 97 | D-INFRA-OPS/Prometheus Prometheus监控系统 | Prometheus Prometheus监控系统 | design | design_only |
| 98 | D-INFRA-OPS/Prometheus+Grafana监控栈 Prometheus Grafana M... | Prometheus+Grafana监控栈 Prometheus G... | design | design_only |
| 99 | D-INFRA-OPS/PyQt5桌面GUI集成器 | PyQt5桌面GUI集成器 | design | design_only |
| 100 | D-INFRA-OPS/Quantum-Classical Hybrid Computing Roadmap 量... | Quantum-Classical Hybrid Computing Ro... | design | design_only |
| 101 | D-INFRA-OPS/RED Metrics Specification RED指标规格 | RED Metrics Specification RED指标规格 | design | design_only |
| 102 | D-INFRA-OPS/React组件库定制 | React组件库定制 | design | design_only |
| 103 | D-INFRA-OPS/Real-Time Dashboard Visual Renderer 实时仪表... | Real-Time Dashboard Visual Renderer ... | design | design_only |
| 104 | D-INFRA-OPS/Resilience Manager 弹性管理器 | Resilience Manager 弹性管理器 | design | design_only |
| 105 | D-INFRA-OPS/Resilience Testing Engine 韧性测试引擎 | Resilience Testing Engine 韧性测试引擎 | design | design_only |
| 106 | D-INFRA-OPS/SLA监控与保障器 | SLA监控与保障器 | design | design_only |
| 107 | D-INFRA-OPS/SSL证书自动更新 | SSL证书自动更新 | design | design_only |
| 108 | D-INFRA-OPS/Saga事务编排 Saga Transaction Orchestration | Saga事务编排 Saga Transaction Orchest... | design | design_only |
| 109 | D-INFRA-OPS/Security Infra Manager 安全基础设施管理器 | Security Infra Manager 安全基础设施管... | design | design_only |
| 110 | D-INFRA-OPS/Shared Infrastructure 共享基础设施 | Shared Infrastructure 共享基础设施 | design | design_only |
| 111 | D-INFRA-OPS/Streamlit快速原型开发器 | Streamlit快速原型开发器 | design | design_only |
| 112 | D-INFRA-OPS/Test Automation & CI/CD Integration 测试自动... | Test Automation & CI/CD Integration ... | design | design_only |
| 113 | D-INFRA-OPS/Tool Scripts 工具脚本 | Tool Scripts 工具脚本 | design | design_only |
| 114 | D-INFRA-OPS/Trace Hierarchical Model Trace层级模型 | Trace Hierarchical Model Trace层级模型 | design | design_only |
| 115 | D-INFRA-OPS/Trace Hierarchy Model Trace层级模型 | Trace Hierarchy Model Trace层级模型 | design | design_only |
| 116 | D-INFRA-OPS/W3C TraceContext W3C TraceContext追踪标准 | W3C TraceContext W3C TraceContext追踪... | design | design_only |
| 117 | D-INFRA-OPS/eBPF eBPF无侵入Span补全 | eBPF eBPF无侵入Span补全 | design | design_only |
| 118 | D-INFRA-OPS/mypy增量类型检查模式 | mypy增量类型检查模式 | design | design_only |
| 119 | D-INFRA-OPS/pre-commit git钩子自动配置器 | pre-commit git钩子自动配置器 | design | design_only |
| 120 | D-INFRA-OPS/wandb使用成本追踪器 | wandb使用成本追踪器 | design | design_only |
| 121 | D-INFRA-OPS/业务指标量化与追踪器 Business Metric Quantifi... | 业务指标量化与追踪器 Business Metric ... | design | design_only |
| 122 | D-INFRA-OPS/个性化界面配置管理器 Management Config | 个性化界面配置管理器 Management Config | design | design_only |
| 123 | D-INFRA-OPS/主题与样式引擎 Engine | 主题与样式引擎 Engine | design | design_only |
| 124 | D-INFRA-OPS/事件总线监控 Monitoring Event | 事件总线监控 Monitoring Event | design | design_only |
| 125 | D-INFRA-OPS/五区域布局渲染引擎 Engine | 五区域布局渲染引擎 Engine | design | design_only |
| 126 | D-INFRA-OPS/五区域布局管理器 Management | 五区域布局管理器 Management | design | design_only |
| 127 | D-INFRA-OPS/交互反馈系统 Interactive Feedback System | 交互反馈系统 Interactive Feedback System | design | design_only |
| 128 | D-INFRA-OPS/交互操作埋点 Interactive Operation Tracking | 交互操作埋点 Interactive Operation Tr... | design | design_only |
| 129 | D-INFRA-OPS/交互方式使用统计热力图 Interaction Method Usa... | 交互方式使用统计热力图 Interaction Me... | design | design_only |
| 130 | D-INFRA-OPS/交互方式成本效率分析器 Analyzer | 交互方式成本效率分析器 Analyzer | design | design_only |
| 131 | D-INFRA-OPS/交互界面迁移方案器 Interactive Interface Migr... | 交互界面迁移方案器 Interactive Interf... | design | design_only |
| 132 | D-INFRA-OPS/交互设计规范合规检查器 Compliance | 交互设计规范合规检查器 Compliance | design | design_only |
| 133 | D-INFRA-OPS/交付物模板标准化器 Deliverable Template Stand... | 交付物模板标准化器 Deliverable Templa... | design | design_only |
| 134 | D-INFRA-OPS/交付物模板管理 Management | 交付物模板管理 Management | design | design_only |
| 135 | D-INFRA-OPS/交付物自动检查 Deliverable Auto Check | 交付物自动检查 Deliverable Auto Check | design | design_only |
| 136 | D-INFRA-OPS/交易日志不可自动清理 Logger | 交易日志不可自动清理 Logger | design | design_only |
| 137 | D-INFRA-OPS/交易时段依赖库不可自动升级 Trading Session De... | 交易时段依赖库不可自动升级 Trading Se... | design | design_only |
| 138 | D-INFRA-OPS/代码块语法校验器 Checker | 代码块语法校验器 Checker | design | design_only |
| 139 | D-INFRA-OPS/代码质量度量看板 Code Quality Metrics Dashboard | 代码质量度量看板 Code Quality Metrics... | design | design_only |
| 140 | D-INFRA-OPS/优先级冲突解决器 Priority Conflict Resolver | 优先级冲突解决器 Priority Conflict Re... | design | design_only |
| 141 | D-INFRA-OPS/优先级动态调整器 Priority Dynamic Adjuster | 优先级动态调整器 Priority Dynamic Adj... | design | design_only |
| 142 | D-INFRA-OPS/优先级时间预算与延期预警器 Priority Time Budg... | 优先级时间预算与延期预警器 Priority T... | design | design_only |
| 143 | D-INFRA-OPS/优先级自动评估器 Priority Auto Evaluator | 优先级自动评估器 Priority Auto Evaluator | design | design_only |
| 144 | D-INFRA-OPS/优雅降级规划器 Fallback | 优雅降级规划器 Fallback | design | design_only |
| 145 | D-INFRA-OPS/依赖冲突检测 Dependency Conflict Detection | 依赖冲突检测 Dependency Conflict Dete... | design | design_only |
| 146 | D-INFRA-OPS/依赖冲突检测器 Detector | 依赖冲突检测器 Detector | design | design_only |
| 147 | D-INFRA-OPS/依赖图韧性评分增强 Dependency Graph Resilienc... | 依赖图韧性评分增强 Dependency Graph R... | design | design_only |
| 148 | D-INFRA-OPS/依赖库升级流程 依赖库升级 Workflow | 依赖库升级流程 依赖库升级 Workflow | design | design_only |
| 149 | D-INFRA-OPS/依赖版本兼容性检查器 Dependency Version Compa... | 依赖版本兼容性检查器 Dependency Versi... | design | design_only |
| 150 | D-INFRA-OPS/依赖版本自动升级建议器 Dependency Version Aut... | 依赖版本自动升级建议器 Dependency Ver... | design | design_only |
| 151 | D-INFRA-OPS/信号质量评估消费桥接器 Signal | 信号质量评估消费桥接器 Signal | design | design_only |
| 152 | D-INFRA-OPS/元数据Schema迁移管理器 | 元数据Schema迁移管理器 | design | design_only |
| 153 | D-INFRA-OPS/全局快捷键管理 Management | 全局快捷键管理 Management | design | design_only |
| 154 | D-INFRA-OPS/全量恢复演练 Full Recovery Drill | 全量恢复演练 Full Recovery Drill | design | design_only |
| 155 | D-INFRA-OPS/内存泄漏检测器 Detector Memory | 内存泄漏检测器 Detector Memory | design | design_only |
| 156 | D-INFRA-OPS/决策流节点耗时瓶颈分析器 Analyzer Node | 决策流节点耗时瓶颈分析器 Analyzer Node | design | design_only |
| 157 | D-INFRA-OPS/决策路径频次统计器 Path | 决策路径频次统计器 Path | design | design_only |
| 158 | D-INFRA-OPS/分阶段实施编排器 Phased Implementation Orches... | 分阶段实施编排器 Phased Implementatio... | design | design_only |
| 159 | D-INFRA-OPS/前端安全审计 Audit Security Frontend | 前端安全审计 Audit Security Frontend | design | design_only |
| 160 | D-INFRA-OPS/前端性能基准测试 Frontend Performance | 前端性能基准测试 Frontend Performance | design | design_only |
| 161 | D-INFRA-OPS/前端组件渲染性能监控器 Monitor Frontend Perfo... | 前端组件渲染性能监控器 Monitor Fronte... | design | design_only |
| 162 | D-INFRA-OPS/功能废弃影响范围追踪器 Feature Deprecation Im... | 功能废弃影响范围追踪器 Feature Deprec... | design | design_only |
| 163 | D-INFRA-OPS/动态韧性调整器 Dynamic Resilience Adjuster | 动态韧性调整器 Dynamic Resilience Adj... | design | design_only |
| 164 | D-INFRA-OPS/协作过程动画回放器 Collaboration Process Anim... | 协作过程动画回放器 Collaboration Proc... | design | design_only |
| 165 | D-INFRA-OPS/双机热备 Active-Standby | 双机热备 Active-Standby | design | design_only |
| 166 | D-INFRA-OPS/变更必须灰度发布 Changes Must Be Canary Released | 变更必须灰度发布 Changes Must Be Cana... | design | design_only |
| 167 | D-INFRA-OPS/变更管理 变更管理 Management | 变更管理 变更管理 Management | design | design_only |
| 168 | D-INFRA-OPS/变更管理是灰度而非直接发布 Grayscale Release | 变更管理是灰度而非直接发布 Grayscale ... | design | design_only |
| 169 | D-INFRA-OPS/可拖拽面板引擎 Engine | 可拖拽面板引擎 Engine | design | design_only |
| 170 | D-INFRA-OPS/可视化组件库 Visualization Component Library | 可视化组件库 Visualization Component ... | design | design_only |
| 171 | D-INFRA-OPS/可视化组件注册中心 Visualization Component Re... | 可视化组件注册中心 Visualization Comp... | design | design_only |
| 172 | D-INFRA-OPS/可配置规则引擎 Configurable Rule Engine | 可配置规则引擎 Configurable Rule Engine | design | design_only |
| 173 | D-INFRA-OPS/命名规范CI门禁集成器 | 命名规范CI门禁集成器 | design | design_only |
| 174 | D-INFRA-OPS/命名规范自动修复建议器 Naming Convention Auto... | 命名规范自动修复建议器 Naming Convent... | design | design_only |
| 175 | D-INFRA-OPS/响应式断点适配 Response | 响应式断点适配 Response | design | design_only |
| 176 | D-INFRA-OPS/回滚策略 回滚策略 Strategy | 回滚策略 回滚策略 Strategy | design | design_only |
| 177 | D-INFRA-OPS/图表主题动态切换 Table | 图表主题动态切换 Table | design | design_only |
| 178 | D-INFRA-OPS/图表主题标准化导出导入器 Importer Table | 图表主题标准化导出导入器 Importer Table | design | design_only |
| 179 | D-INFRA-OPS/图表导出与分享 Table | 图表导出与分享 Table | design | design_only |
| 180 | D-INFRA-OPS/备份策略 Backup Strategy | 备份策略 Backup Strategy | design | design_only |
| 181 | D-INFRA-OPS/复杂操作进度提示器 Complex Operation Progress... | 复杂操作进度提示器 Complex Operation ... | design | design_only |
| 182 | D-INFRA-OPS/多数据库SLA监控与告警器 | 多数据库SLA监控与告警器 | design | design_only |
| 183 | D-INFRA-OPS/多标签页管理器 Management Tag | 多标签页管理器 Management Tag | design | design_only |
| 184 | D-INFRA-OPS/大数据量图表优化 Table | 大数据量图表优化 Table | design | design_only |
| 185 | D-INFRA-OPS/委员会决策耗时监控器 Monitor | 委员会决策耗时监控器 Monitor | design | design_only |
| 186 | D-INFRA-OPS/字段类型变更影响分析器 Analyzer Field | 字段类型变更影响分析器 Analyzer Field | design | design_only |
| 187 | D-INFRA-OPS/存储层性能基准测试器 Storage Performance | 存储层性能基准测试器 Storage Performance | design | design_only |
| 188 | D-INFRA-OPS/存储成本量化核算器 Storage Cost Calculator | 存储成本量化核算器 Storage Cost Calcu... | design | design_only |
| 189 | D-INFRA-OPS/学习进度量化评估 Learning Progress Quantitati... | 学习进度量化评估 Learning Progress Qu... | design | design_only |
| 190 | D-INFRA-OPS/实时数据流图表 Real-time Table | 实时数据流图表 Real-time Table | design | design_only |
| 191 | D-INFRA-OPS/实验追踪方案决策记录器 Experiment Tracking Sc... | 实验追踪方案决策记录器 Experiment Tra... | design | design_only |
| 192 | D-INFRA-OPS/实验追踪方案切换触发器 Experiment Tracking Sc... | 实验追踪方案切换触发器 Experiment Tra... | design | design_only |
| 193 | D-INFRA-OPS/审计报告自动生成器 Generator Audit Report | 审计报告自动生成器 Generator Audit Re... | design | design_only |
| 194 | D-INFRA-OPS/审计日志分析 Audit Logger | 审计日志分析 Audit Logger | design | design_only |
| 195 | D-INFRA-OPS/审计重建演练 Audit Reconstruction Drill | 审计重建演练 Audit Reconstruction Drill | design | design_only |
| 196 | D-INFRA-OPS/容器健康检查 Container Health Check | 容器健康检查 Container Health Check | design | design_only |
| 197 | D-INFRA-OPS/容器安全扫描 Security | 容器安全扫描 Security | design | design_only |
| 198 | D-INFRA-OPS/容器资源限制 Container Resource Limit | 容器资源限制 Container Resource Limit | design | design_only |
| 199 | D-INFRA-OPS/密钥轮换模块 Key Rotation Module | 密钥轮换模块 Key Rotation Module | design | design_only |
| 200 | D-INFRA-OPS/导航使用热力图生成器 Generator | 导航使用热力图生成器 Generator | design | design_only |

> (仅显示前 200 个模块，共 396 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 419 条 / 419 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 419 条 / 419 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 361 条 / edges                               │
│   [config_depends]: 18 条 / edges                                │
│   [contract]: 15 条 / edges                                      │
│   [event]: 12 条 / edges                                         │
│   [data]: 10 条 / edges                                          │
│   [runtime]: 3 条 / edges                                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (361 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   app.py → __init__.py                                           │
│   External Instruction Moni... → Log Aggregator 日志聚合器       │
│   通知与告警 Alerting Notif... → 字段类型变更影响分析器 An...    │
│   D-INFRA-OPS → MOD-INF-034                                      │
│   MOD-INF-034 → MOD-INF-036                                      │
│   MOD-INF-036 → MOD-INF-033                                      │
│   MOD-INF-033 → MOD-INF-024                                      │
│   MOD-INF-024 → MOD-INF-035                                      │
│   MOD-INF-035 → MOD-INF-026                                      │
│   MOD-INF-026 → MOD-MASTER-001                                   │
│   MOD-MASTER-001 → CI/CD Pipeline 管线                           │
│   CI/CD Pipeline 管线 → Monitoring System 监控系统               │
│   Monitoring System 监控系统 → Backup Manager 备份管理器         │
│   Backup Manager 备份管理器 → Disaster Recovery 灾难恢复         │
│   Disaster Recovery 灾难恢复 → Health Dashboard 健康仪表盘       │
│   Health Dashboard 健康仪表盘 → Log Aggregator 日志聚合器        │
│   Log Aggregator 日志聚合器 → Resilience Manager 弹性管...       │
│   Resilience Manager 弹性管... → Network Manager 网络管理器      │
│   Network Manager 网络管理器 → IaC Manager IaC管理器             │
│   IaC Manager IaC管理器 → Security Infra Manager 安...           │
│   Security Infra Manager 安... → HPC Manager HPC管理器           │
│   HPC Manager HPC管理器 → Deployment Manager 部署管...           │
│   Deployment Manager 部署管... → Alert Manager 告警管理器        │
│   Alert Manager 告警管理器 → 备份策略 Backup Strategy            │
│   备份策略 Backup Strategy → Backup Manager 自动备份管...        │
│   Backup Manager 自动备份管... → Cold Data Archive Manager...    │
│   Cold Data Archive Manager... → 数据源可用性SLA追踪器 Dat...    │
│   数据源可用性SLA追踪器 Dat... → 存储成本量化核算器 Storag...    │
│   存储成本量化核算器 Storag... → 日快照恢复演练 Daily Snap...    │
│   日快照恢复演练 Daily Snap... → 盘中恢复演练 Intraday Rec...    │
│   盘中恢复演练 Intraday Rec... → 全量恢复演练 Full Recover...    │
│   全量恢复演练 Full Recover... → 审计重建演练 Audit Recons...    │
│   审计重建演练 Audit Recons... → Shared Infrastructure 共...     │
│   Shared Infrastructure 共... → Tool Scripts 工具脚本            │
│   Tool Scripts 工具脚本 → Quantum-Classical Hybrid ...           │
│   Quantum-Classical Hybrid ... → Cost Optimizer 成本优化器       │
│   Cost Optimizer 成本优化器 → Agent RBAC / Permission G...       │
│   Agent RBAC / Permission G... → Communication Encryption ...    │
│   Communication Encryption ... → 数据血缘追踪 Data Lineage...    │
│   数据血缘追踪 Data Lineage... → AI API Cost Manager AI AP...    │
│   AI API Cost Manager AI AP... → Agent Communication Proto...    │
│   Agent Communication Proto... → Capacity Assurance & SLI/...    │
│   Capacity Assurance & SLI/... → Model Profiler & Capabili...    │
│   Model Profiler & Capabili... → PIT Manager Point-in-Time...    │
│   PIT Manager Point-in-Time... → Pipeline编排器 Pipeline O...    │
│   Pipeline编排器 Pipeline O... → Saga事务编排 Saga Transac...    │
│   Saga事务编排 Saga Transac... → 可配置规则引擎 Configurab...    │
│   可配置规则引擎 Configurab... → 数字孪生系列 Digital Twin...    │
│   数字孪生系列 Digital Twin... → LLM模型分级路由 LLM Model...    │
│   ...还有 312 条 / 312 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (18 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (15 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (12 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (10 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (3 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 419 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `01_d_infra_ops_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
