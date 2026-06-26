---
blueprint_id: MOD-GOVERNANCE
ttl: task_bound
doc_type: readme
---

# MOD-MASTER_BLUEPRINT 变更目录

> **蓝图**：MOD-MASTER_BLUEPRINT 跨系统集成契约注册中心
> **施工阶段**：phase_2_active — 代码已落地，契约集成施工中
> **卡片总数**：33

## 任务卡清单

| # | task_id | 标题 | 优先级 | 状态 |
|---|---------|------|:---:|:---:|
| 1 | TASK-MST-0001 | 真源优先级宪章冲突检测与裁决机制 | P0 | ✅ |
| 2 | TASK-MST-0002 | AI Agent冷启动分派表与三级Token预算管理器 | P0 | ✅ |
| 3 | TASK-MST-0003 | MOD-MASTER_BLUEPRINT模块骨架搭建 | P0 | ✅ |
| 4 | TASK-MST-0004 | 56条核心跨系统集成契约注册与运行时调用路由（52条已路由，6条可路由） | P0 | 🔶 |
| 5 | TASK-MST-0005 | 共享Schema版本协商机制 | P0 | 🔲 |
| 6 | TASK-MST-0006 | 全局状态传播链与并发容量预算控制器 | P0 | 🔲 |
| 7 | TASK-MST-0007 | 施工Phase规划 | P0 | 🔲 |
| 8 | TASK-MST-0008 | Anti-Patterns运行时防护（wt-006 284行，含35测试） | P0 | 🔶 |
| 9 | TASK-MST-0009 | 设计决策表与施工指南 | P0 | 🔲 |
| 10 | TASK-MST-0010 | 集成测试契约框架（contract_registry/contract_router测试已同步56合同计数） | P0 | 🔶 |
| 11 | TASK-MST-0011 | 风险注册表缓解与集成冲突裁决 | P0 | 🔲 |
| 12 | TASK-MST-0013 | 12系统标准化三态HealthCheck探针（healthcheck_service.py已落地） | P0 | 🔶 |
| 13 | TASK-MST-0014 | CBAC能力访问控制矩阵（cbac_matrix.py已落地，25%集成交付） | P0 | 🔶 |
| 14 | TASK-MST-0015 | CDC消费者驱动契约+Can-I-Deploy+DLQ（3组件已落地+单元测试通过） | P0 | 🔶 |
| 15 | TASK-MST-0016 | SLO/SLI服务等级目标与Error Budget（slo_manager.py+测试通过） | P0 | 🔶 |
| 16 | TASK-MST-0017 | Bulkhead资源池隔舱+Watchdog+备份恢复（bulkhead_manager.py已落地） | P0 | 🔶 |
| 17 | TASK-MST-0018 | 统一配置管理+FeatureFlag+Secrets（config_manager.py+feature_flag.py已落地） | P0 | 🔶 |
| 18 | TASK-MST-0019 | 数据生命周期+多环境隔离+Chaos+Contract→Codegen | P0 | 🔲 |
| 19 | TASK-MST-0020 | LLM模型注册表+外部依赖版本锁定（model_registry.py+dependency_lock.py已落地） | P0 | 🔶 |
| 20 | TASK-MST-0021 | 知识新鲜度废止+文件卫生保洁+AI会话手递手（3组件已落地） | P0 | 🔶 |
| 21 | TASK-MST-0022 | API稳定性+金丝雀发布+事件复盘+竞态条件+LLM成本（canary_manager.py+incident_postmortem.py已落地） | P0 | 🔶 |
| 22 | TASK-MST-0023 | 磁盘空间耗尽防护+网络分区容忍（disk_guard.py+network_partition.py已落地） | P0 | 🔶 |
| 23 | TASK-MST-0024 | 跨系统性能基准与回归预防（benchmark_runner.py已落地） | P0 | 🔶 |
| 24 | TASK-MST-0025 | 零停机滚动升级+数据库Schema演化契约（rolling_upgrade.py+schema_migration.py已落地） | P0 | 🔶 |
| 25 | TASK-MST-0026 | 全局降级级联预防+Owner缺位分级自治（degrade_cascade.py+autonomy_guard.py已落地） | P0 | 🔶 |
| 26 | TASK-MST-0027 | AI Agent质量反馈闭环（agent_quality.py已落地） | P0 | 🔶 |
| 27 | TASK-MST-0028 | AI Prompt版本控制+Session冲突预防契约（prompt_version.py+session_conflict.py已落地） | P0 | 🔶 |
| 28 | TASK-MST-0029 | 死代码/孤儿文件/僵尸引用三扫描+蓝图健康自检（lean_scanner.py+blueprint_health.py已落地） | P0 | 🔶 |
| 29 | TASK-MST-0030 | 系统移交恢复+知识质量评分契约（system_transfer.py+ke_quality.py已落地） | P0 | 🔶 |
| 30 | TASK-MST-0031 | Round 5新盲点关闭B-MOD-301~318 | P0 | 🔲 |
| 31 | TASK-MST-0032 | Round 5新盲点关闭B-MOD-319~335 | P0 | 🔲 |
| 32 | TASK-MST-0033 | 模块全版本管理与文件路径索引 | P0 | 🔲 |
| 33 | TASK-MST-0012 | 端到端场景走查验证器 | P1 | 🔲 |

## 图例
- ✅ = 已完成（施工+测试+集成）
- 🔶 = 部分完成（代码已落地，测试通过，但CT-*全链路+CI集成尚缺）
- 🔲 = 未施工
