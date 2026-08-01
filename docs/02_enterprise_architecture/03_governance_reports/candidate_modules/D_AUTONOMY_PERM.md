---
doc_type: audit_report
title: 候选模块清单 — D_AUTONOMY_PERM
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_AUTONOMY_PERM 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **98** 条（原有 0 + harvest 98）。
> harvest 去重四态: likely_new=82 / likely_implemented=16

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0339 | Non-AI Boundary Guard 非AI边界守卫 | / D-AUTONOMY-33 / Non-AI Boundary Guard / ✅ 能建 / / AI/non-AI边界守卫+权重≤30% / | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0705 | Model Registry 模型注册表 | 注册AI/ML模型及其依赖(对标MLflow) | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0706 | Model Drift Detector 模型漂移检测器 | 检测模型漂移和数据漂移(对标Evidently AI) | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0887 | Kill Switch 紧急制动开关 | 紧急制动开关状态机(OPEN/CLOSED)+多路径触发+冷却期+Owner确认重置+分层制动 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0888 | Autonomy Fuse 自治熔断器 | 自治熔断器熔断条件+熔断执行+熔断恢复+熔断审计+自治降级 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0889 | Drift Guard 漂移守卫 | 漂移守卫行为漂移检测+性能漂移检测+概念漂移检测+漂移告警+漂移纠正 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0934 | Rollback System 回滚系统 | 回滚系统(preflight+AutoTrigger+Kill Switch) | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0986 | Escalation Protocol 升级协议 | 升级协议 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0989 | Red-Blue Validator 红蓝对抗验证器 | Hard-Gate+Verifier AI | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0990 | Auto Fix Engine 自动修复引擎 | 自动修复引擎 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0994 | Local Model 本地推理模型 | Agentic Drift | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1074 | Knowledge Write Guard Protector 知识Write Guard保护器 | 知识库写保护+审批+审计 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1075 | Knowledge Snapshot Rollback Manager 知识快照回滚管理器 | 知识库快照+回滚+差异对比 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1076 | LLM Cost Guard LLM成本守卫 | LLM API成本监控+预算+告警 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1077 | Token Budget Manager Token预算管理器 | Token预算+消耗追踪+熔断 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1078 | Zone Crossing Boundary Validator Zone Crossing边界校验器 | 跨域边界校验+违规告警 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1080 | Auto-Guard Async Approval Manager Auto-Guard异步审批管理器 | 4%先干后验5分钟超时机制 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1262 | Parameter Optimizer 参数优化器 | 三层优化：实时微调/周期优化/结构进化 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1263 | Risk Check RBAC Permission Controller 风控检查RBAC权限控制器 | 检查权限由Agent RBAC控制+风控检查权限定义/校验/审计 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1264 | Risk Alert Notification Dispatcher 风控告警通知分发器 | 告警级别→通知渠道映射/告警聚合/告警去重+分发性能监控 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1265 | Health Check Service 健康检查服务 | healthcheck_service.py体检中心+定期检查各模块是否健康 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1267 | Rollback Four-Tier Strategy Selector 回滚四级策略选择器 | full_revert/partial_revert/discard/hard_reset四级回滚策略智能选择 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1268 | Dual-Storage Rollback Coordinator 双存储回滚协调器 | git revert+SQLite恢复双存储一致性协调+事务性保证 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1271 | Governance Phase Check Slimmer Governance Phase Check精简器 | 63个Phase Check精简到10项核心+检查使用率/重要性/精简计划 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1272 | Budget Enforcer On-Demand Activator Budget Enforcer按需激活器 | 默认warn日费>$10开strict的按需激活策略+成本监控/激活阈值 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1273 | AI Comprehension Cost Dynamic Estimator AI理解成本动态估算器 | 代码行数→AI理解时间的动态估算+理解成本阈值告警+代码精简建议 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1274 | PipelineOrchestrator CostTracker Component PipelineOrchestrator成本追踪组件 | PipelineOrchestrator拆分后独立成本追踪组件+Token计数/成本累计 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1276 | AI Governance Framework Compliance Assessor AI治理框架合规性评估器 | AI治理框架=门禁+安全+审计+反馈的治理合规性评估 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1277 | RBAC Permission Check Embedded Bridge RBAC权限检查内嵌桥接器 | PipelineOrchestrator._rbac_check()内嵌RBAC检查的桥接器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1278 | Rollback Operation Visual Tracker 回滚操作可视化追踪器 | 回滚操作可视化追踪+回滚步骤展示+回滚影响范围可视化 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1279 | Feedback Loop Three-Layer Escalation Trigger Feedback Loop三层升级触发器 | L1任务→L2模式→L3架构三层升级触发+升级条件+升级审计 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1280 | Token Budget Coordinator Token预算协调器 | Pipeline中Token预算协调+预算分配+预算超限告警+预算回收 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1282 | Drift Detector Statistical Drift Checker Drift Detector统计漂移检测器 | Drift Detector统计方法→统计漂移检测+漂移基线+漂移告警+漂移审计 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1283 | System Version Upgrade Path Manager 系统版本升级路径管理器 | v3→v4→v5系统级升级路径：前置条件检查+分阶段编排+升级验证 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1284 | Saga Definition Saga定义器 | 定义Saga事务步骤和依赖关系 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1285 | Orchestrated Saga Engine 编排式Saga引擎 | 中央协调器控制Saga步骤执行 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1286 | Choreography Saga Engine 协调式Saga引擎 | 事件驱动去中心化Saga执行 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1287 | Compensation Action Manager 补偿动作管理器 | 管理Saga补偿动作和回滚逻辑 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1288 | Saga State Tracker Saga状态追踪器 | 追踪Saga执行状态和进度 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1289 | Saga Observability Tracer Saga可观测性追踪器 | Saga执行全过程可观测性：步骤耗时/补偿触发率/死锁检测 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1290 | AI-Driven Saga Orchestrator AI驱动Saga编排器 | AI决策参与Saga编排：AI判断是否需要补偿 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1291 | Compensation Dependency Graph Analyzer 补偿依赖图分析器 | 补偿动作间依赖分析：补偿A必须在补偿B之前执行 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1292 | Saga Deadlock Detector Saga死锁检测器 | 多Saga实例间资源竞争死锁检测 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1293 | Saga Version Compatibility Manager Saga版本兼容性管理器 | Saga定义变更时运行中实例兼容性管理 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1294 | Cross-Saga Transaction Coordinator 跨Saga事务协调器 | 多Saga间协调：嵌套Saga/并行Saga | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1295 | AI Risk Classifier AI风险分类器 | 分类AI系统风险等级(EU AI Act:不可接受/高/中/低) | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1296 | Governance Policy Engine 治理策略引擎 | 执行AI治理策略(42个统一控制措施) | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1297 | Governance Dashboard 治理仪表盘 | 可视化AI治理状态和合规进度 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1298 | AI Risk Assessor AI风险评估器 | 评估AI系统风险：偏见/可解释性/隐私/安全 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1299 | AI Risk Dependency Mapper AI风险依赖映射器 | AI风险间依赖映射：数据偏见→模型偏见→决策偏见 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1300 | Responsible AI Dependency Auditor 负责任AI依赖审计器 | 负责任AI原则依赖审计：公平性依赖数据代表性等 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1301 | Enhanced Confidence Cascade Mapper 增强置信度级联映射器 | 置信度级联增强建模(D80增强) | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1302 | Saga/Process Manager Dependency Orchestrator Saga/流程管理器依赖编排器 | Saga/流程管理器依赖编排器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1303 | Model Validation Dependency Orchestrator 模型验证依赖编排器 | 编排模型验证活动的依赖 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1304 | Model Monitoring Dependency Tracker 模型监控依赖追踪器 | 追踪模型监控依赖 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1305 | Model Risk Tier Classifier 模型风险分级器 | 按风险等级分级模型 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1306 | Model Override Impact Analyzer 模型覆盖影响分析器 | 分析人工覆盖模型决策的影响 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1307 | Model Drift Dependency Propagator 模型漂移依赖传播器 | 模型漂移依赖传播器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1308 | Model Validation Dependency Orchestrator v2 模型验证依赖编排器v2 | 模型验证依赖编排器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1309 | Model Risk Tier Dependency Classifier 模型风险等级依赖分类器 | 模型风险等级依赖分类器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1310 | Model Override Dependency Impact Analyzer 模型覆盖依赖影响分析器 | 模型覆盖依赖影响分析器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1311 | Model Inventory Dependency Graph Builder 模型清单依赖图构建器 | 模型清单依赖图构建器 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1312 | Temporal GNN Dependency Drift Predictor 时序GNN依赖漂移预测器 | 时序GNN建模依赖图演化预测3个月依赖断裂风险 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1315 | PERM Budget Exempt Executor PERM预算豁免执行器 | PERM自身不受budget限制，防止死锁 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1316 | Kill Switch Direct Path Kill Switch直通路径 | 不经过CORE的Kill Switch直通执行路径 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1317 | Backtest-Live Deviation Monitor 回测-实盘偏差监控器 | 防止过拟合参数调整生效到实盘 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2174 | Four-Level Autonomy Model 四级自治模型 | 四级自治模型Level 0-3 NVIDIA对标 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2175 | ai_modifiable 自治区 | ai_modifiable自治区Agent可自主修改的范围 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2176 | human_gated 门控区 | human_gated门控区需人工审批的范围 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2177 | immutable 禁区 | immutable禁区绝对不可变的范围 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2178 | HITL Human-in-the-Loop 人在闭环机制 | HITL人在闭环机制置信度驱动升级策略 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2335 | Level 0-3 Autonomy Levels 0-3自治级别 | ║  ║  Level 0 推理API → Level 1 确定性系统 → Level 2 弱自主 → Level 3 全自主                                  ║  ║ | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2336 | HITL Confidence Upgrade HITL置信度升级 | ║  ║  HITL置信度升级: ≥90%自动 / 70-89%标记 / 50-69%审批 / <50%拒绝                                          ║  ║ | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2352 | Autonomy Boundary Change Process 自治边界变更流程 | 自治边界变更流程5步变更提案到影响评估到审批决策到变更执行到变更验证 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2353 | HITL Mechanism HITL人在闭环机制 | HITL人在闭环机制触发条件与分级置信度驱动升级策略EU AI Act Article 14合规映射 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2438 | Role and Interaction Journey 角色与交互旅程 | 角色与交互旅程4角色Trader到Administrator到AI到风控系统含交互方式AI自动化程度人工介入点 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3367 | 隐性串谋 Implicit Collusion | 行为相关性超越策略指纹+市场结果异常AP-08反事实仿真 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3549 | agent_creation_policy.py Agent创建策略 | / agent_creation_policy.py / D-AUT-PERM / Agent创建策略是自治保护职责 / | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3550 | anti_pattern_guard.py 反模式守卫 | DD-SEC-002归入AP反模式守卫是自治行为约束 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3551 | anomaly_detector.py 异常检测器 | DD-SEC-002归入AP异常检测是自治健康监控 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3553 | auto_maintenance.py 自动维护 | DD-SEC-002归入AP自动维护是自治自愈 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3554 | bootstrap_verifier.py 引导验证器 | DD-SEC-002归入AP引导验证是自治启动 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3555 | genesis_bootstrap.py 创世引导 | DD-SEC-002归入AP引导验证是自治启动 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3556 | build_sanitizer.py 构建清洗器 | DD-SEC-002归入AP构建清洗是自治质量 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3557 | cache_invalidation.py 缓存失效器 | DD-SEC-002归入AP缓存失效是自治运行时 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3558 | cross_cutting.py 横切关注点 | DD-SEC-002归入AP横切关注点是自治编排 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3559 | dependency_auditor.py 依赖审计器 | DD-SEC-002归入AP依赖审计是自治保护 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3560 | environment_manager.py 环境管理器 | DD-SEC-002归入AP环境管理是自治运行时 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3561 | exceptions.py 异常定义 | DD-SEC-002归入AP异常定义是自治基础设施 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4879 | 决策一致性 Decision Consistency | / S-02 / 决策一致性 / Agent多次决策的一致性评分 / AP-08 Drift Detector / | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4880 | 通信异常 Communication Anomaly | / S-03 / 通信异常 / Agent间通信频率/内容异常 / AP-05 Health Monitor / | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4881 | 资源消耗异常 Resource Consumption Anomaly | / S-04 / 资源消耗异常 / Token/时间/资金预算偏离基线 / AP-04 Budget Enforcer / | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4882 | 串谋/策略同质化 Collusion/Strategy Homogeneity | 策略指纹相似度+持仓相关性AP-08行为相关性分析 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4883 | 涌现行为 Emergent Behavior | 单个Agent行为正常但整体偏离预期AP-08系统级行为基线 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5062 | Half-Open Probe 熔断器半开试探 | 1次/超时周期的半开试探机制 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5063 | Learning System Kill Switch 学习系统Kill Switch | 独立于学习系统的硬开关可立即暂停所有学习系统操作物理隔离 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5064 | Agent Capability Assessment Agent能力评估协议 | 每季度评估Agent能力边界评估结果纳入漂移检测基线METR/UK AISI 2025 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5065 | Cluster Behavior Risk Protection 群集行为风险防护 | 相关性>0.7自动差异化+市场压力时降仓防止AI版闪崩 | D_AUTONOMY_PERM | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（98 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0339 | Non-AI Boundary Guard 非AI边界守卫 | / D-AUTONOMY-33 / Non-AI Boundary Guard / ✅ 能建 / / AI/non-AI边界守卫+权重≤30% / | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0705 | Model Registry 模型注册表 | 注册AI/ML模型及其依赖(对标MLflow) | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0706 | Model Drift Detector 模型漂移检测器 | 检测模型漂移和数据漂移(对标Evidently AI) | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0887 | Kill Switch 紧急制动开关 | 紧急制动开关状态机(OPEN/CLOSED)+多路径触发+冷却期+Owner确认重置+分层制动 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0888 | Autonomy Fuse 自治熔断器 | 自治熔断器熔断条件+熔断执行+熔断恢复+熔断审计+自治降级 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0889 | Drift Guard 漂移守卫 | 漂移守卫行为漂移检测+性能漂移检测+概念漂移检测+漂移告警+漂移纠正 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0934 | Rollback System 回滚系统 | 回滚系统(preflight+AutoTrigger+Kill Switch) | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0986 | Escalation Protocol 升级协议 | 升级协议 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0989 | Red-Blue Validator 红蓝对抗验证器 | Hard-Gate+Verifier AI | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0990 | Auto Fix Engine 自动修复引擎 | 自动修复引擎 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-0994 | Local Model 本地推理模型 | Agentic Drift | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1074 | Knowledge Write Guard Protector 知识Write Guard保护器 | 知识库写保护+审批+审计 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1075 | Knowledge Snapshot Rollback Manager 知识快照回滚管理器 | 知识库快照+回滚+差异对比 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1076 | LLM Cost Guard LLM成本守卫 | LLM API成本监控+预算+告警 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1077 | Token Budget Manager Token预算管理器 | Token预算+消耗追踪+熔断 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1078 | Zone Crossing Boundary Validator Zone Crossing边界校验器 | 跨域边界校验+违规告警 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1080 | Auto-Guard Async Approval Manager Auto-Guard异步审批管理器 | 4%先干后验5分钟超时机制 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1262 | Parameter Optimizer 参数优化器 | 三层优化：实时微调/周期优化/结构进化 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1263 | Risk Check RBAC Permission Controller 风控检查RBAC权限控制器 | 检查权限由Agent RBAC控制+风控检查权限定义/校验/审计 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1264 | Risk Alert Notification Dispatcher 风控告警通知分发器 | 告警级别→通知渠道映射/告警聚合/告警去重+分发性能监控 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1265 | Health Check Service 健康检查服务 | healthcheck_service.py体检中心+定期检查各模块是否健康 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1267 | Rollback Four-Tier Strategy Selector 回滚四级策略选择器 | full_revert/partial_revert/discard/hard_reset四级回滚策略智能选择 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1268 | Dual-Storage Rollback Coordinator 双存储回滚协调器 | git revert+SQLite恢复双存储一致性协调+事务性保证 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1271 | Governance Phase Check Slimmer Governance Phase Check精简器 | 63个Phase Check精简到10项核心+检查使用率/重要性/精简计划 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1272 | Budget Enforcer On-Demand Activator Budget Enforcer按需激活器 | 默认warn日费>$10开strict的按需激活策略+成本监控/激活阈值 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1273 | AI Comprehension Cost Dynamic Estimator AI理解成本动态估算器 | 代码行数→AI理解时间的动态估算+理解成本阈值告警+代码精简建议 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1274 | PipelineOrchestrator CostTracker Component PipelineOrchestrator成本追踪组件 | PipelineOrchestrator拆分后独立成本追踪组件+Token计数/成本累计 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1276 | AI Governance Framework Compliance Assessor AI治理框架合规性评估器 | AI治理框架=门禁+安全+审计+反馈的治理合规性评估 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1277 | RBAC Permission Check Embedded Bridge RBAC权限检查内嵌桥接器 | PipelineOrchestrator._rbac_check()内嵌RBAC检查的桥接器 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1278 | Rollback Operation Visual Tracker 回滚操作可视化追踪器 | 回滚操作可视化追踪+回滚步骤展示+回滚影响范围可视化 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1279 | Feedback Loop Three-Layer Escalation Trigger Feedback Loop三层升级触发器 | L1任务→L2模式→L3架构三层升级触发+升级条件+升级审计 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1280 | Token Budget Coordinator Token预算协调器 | Pipeline中Token预算协调+预算分配+预算超限告警+预算回收 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1282 | Drift Detector Statistical Drift Checker Drift Detector统计漂移检测器 | Drift Detector统计方法→统计漂移检测+漂移基线+漂移告警+漂移审计 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1283 | System Version Upgrade Path Manager 系统版本升级路径管理器 | v3→v4→v5系统级升级路径：前置条件检查+分阶段编排+升级验证 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1284 | Saga Definition Saga定义器 | 定义Saga事务步骤和依赖关系 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1285 | Orchestrated Saga Engine 编排式Saga引擎 | 中央协调器控制Saga步骤执行 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1286 | Choreography Saga Engine 协调式Saga引擎 | 事件驱动去中心化Saga执行 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1287 | Compensation Action Manager 补偿动作管理器 | 管理Saga补偿动作和回滚逻辑 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1288 | Saga State Tracker Saga状态追踪器 | 追踪Saga执行状态和进度 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1289 | Saga Observability Tracer Saga可观测性追踪器 | Saga执行全过程可观测性：步骤耗时/补偿触发率/死锁检测 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1290 | AI-Driven Saga Orchestrator AI驱动Saga编排器 | AI决策参与Saga编排：AI判断是否需要补偿 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1291 | Compensation Dependency Graph Analyzer 补偿依赖图分析器 | 补偿动作间依赖分析：补偿A必须在补偿B之前执行 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1292 | Saga Deadlock Detector Saga死锁检测器 | 多Saga实例间资源竞争死锁检测 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1293 | Saga Version Compatibility Manager Saga版本兼容性管理器 | Saga定义变更时运行中实例兼容性管理 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1294 | Cross-Saga Transaction Coordinator 跨Saga事务协调器 | 多Saga间协调：嵌套Saga/并行Saga | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1295 | AI Risk Classifier AI风险分类器 | 分类AI系统风险等级(EU AI Act:不可接受/高/中/低) | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1296 | Governance Policy Engine 治理策略引擎 | 执行AI治理策略(42个统一控制措施) | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1297 | Governance Dashboard 治理仪表盘 | 可视化AI治理状态和合规进度 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1298 | AI Risk Assessor AI风险评估器 | 评估AI系统风险：偏见/可解释性/隐私/安全 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1299 | AI Risk Dependency Mapper AI风险依赖映射器 | AI风险间依赖映射：数据偏见→模型偏见→决策偏见 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1300 | Responsible AI Dependency Auditor 负责任AI依赖审计器 | 负责任AI原则依赖审计：公平性依赖数据代表性等 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1301 | Enhanced Confidence Cascade Mapper 增强置信度级联映射器 | 置信度级联增强建模(D80增强) | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1302 | Saga/Process Manager Dependency Orchestrator Saga/流程管理器依赖编排器 | Saga/流程管理器依赖编排器 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1303 | Model Validation Dependency Orchestrator 模型验证依赖编排器 | 编排模型验证活动的依赖 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1304 | Model Monitoring Dependency Tracker 模型监控依赖追踪器 | 追踪模型监控依赖 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1305 | Model Risk Tier Classifier 模型风险分级器 | 按风险等级分级模型 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1306 | Model Override Impact Analyzer 模型覆盖影响分析器 | 分析人工覆盖模型决策的影响 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1307 | Model Drift Dependency Propagator 模型漂移依赖传播器 | 模型漂移依赖传播器 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1308 | Model Validation Dependency Orchestrator v2 模型验证依赖编排器v2 | 模型验证依赖编排器 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1309 | Model Risk Tier Dependency Classifier 模型风险等级依赖分类器 | 模型风险等级依赖分类器 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1310 | Model Override Dependency Impact Analyzer 模型覆盖依赖影响分析器 | 模型覆盖依赖影响分析器 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1311 | Model Inventory Dependency Graph Builder 模型清单依赖图构建器 | 模型清单依赖图构建器 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1312 | Temporal GNN Dependency Drift Predictor 时序GNN依赖漂移预测器 | 时序GNN建模依赖图演化预测3个月依赖断裂风险 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1315 | PERM Budget Exempt Executor PERM预算豁免执行器 | PERM自身不受budget限制，防止死锁 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-1316 | Kill Switch Direct Path Kill Switch直通路径 | 不经过CORE的Kill Switch直通执行路径 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1317 | Backtest-Live Deviation Monitor 回测-实盘偏差监控器 | 防止过拟合参数调整生效到实盘 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2174 | Four-Level Autonomy Model 四级自治模型 | 四级自治模型Level 0-3 NVIDIA对标 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2175 | ai_modifiable 自治区 | ai_modifiable自治区Agent可自主修改的范围 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2176 | human_gated 门控区 | human_gated门控区需人工审批的范围 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2177 | immutable 禁区 | immutable禁区绝对不可变的范围 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2178 | HITL Human-in-the-Loop 人在闭环机制 | HITL人在闭环机制置信度驱动升级策略 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2335 | Level 0-3 Autonomy Levels 0-3自治级别 | ║  ║  Level 0 推理API → Level 1 确定性系统 → Level 2 弱自主 → Level 3 全自主                                  ║  ║ | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2336 | HITL Confidence Upgrade HITL置信度升级 | ║  ║  HITL置信度升级: ≥90%自动 / 70-89%标记 / 50-69%审批 / <50%拒绝                                          ║  ║ | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2352 | Autonomy Boundary Change Process 自治边界变更流程 | 自治边界变更流程5步变更提案到影响评估到审批决策到变更执行到变更验证 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2353 | HITL Mechanism HITL人在闭环机制 | HITL人在闭环机制触发条件与分级置信度驱动升级策略EU AI Act Article 14合规映射 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-2438 | Role and Interaction Journey 角色与交互旅程 | 角色与交互旅程4角色Trader到Administrator到AI到风控系统含交互方式AI自动化程度人工介入点 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3367 | 隐性串谋 Implicit Collusion | 行为相关性超越策略指纹+市场结果异常AP-08反事实仿真 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3549 | agent_creation_policy.py Agent创建策略 | / agent_creation_policy.py / D-AUT-PERM / Agent创建策略是自治保护职责 / | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3550 | anti_pattern_guard.py 反模式守卫 | DD-SEC-002归入AP反模式守卫是自治行为约束 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3551 | anomaly_detector.py 异常检测器 | DD-SEC-002归入AP异常检测是自治健康监控 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3553 | auto_maintenance.py 自动维护 | DD-SEC-002归入AP自动维护是自治自愈 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3554 | bootstrap_verifier.py 引导验证器 | DD-SEC-002归入AP引导验证是自治启动 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3555 | genesis_bootstrap.py 创世引导 | DD-SEC-002归入AP引导验证是自治启动 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3556 | build_sanitizer.py 构建清洗器 | DD-SEC-002归入AP构建清洗是自治质量 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3557 | cache_invalidation.py 缓存失效器 | DD-SEC-002归入AP缓存失效是自治运行时 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3558 | cross_cutting.py 横切关注点 | DD-SEC-002归入AP横切关注点是自治编排 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3559 | dependency_auditor.py 依赖审计器 | DD-SEC-002归入AP依赖审计是自治保护 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3560 | environment_manager.py 环境管理器 | DD-SEC-002归入AP环境管理是自治运行时 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-3561 | exceptions.py 异常定义 | DD-SEC-002归入AP异常定义是自治基础设施 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-4879 | 决策一致性 Decision Consistency | / S-02 / 决策一致性 / Agent多次决策的一致性评分 / AP-08 Drift Detector / | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-4880 | 通信异常 Communication Anomaly | / S-03 / 通信异常 / Agent间通信频率/内容异常 / AP-05 Health Monitor / | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-4881 | 资源消耗异常 Resource Consumption Anomaly | / S-04 / 资源消耗异常 / Token/时间/资金预算偏离基线 / AP-04 Budget Enforcer / | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-4882 | 串谋/策略同质化 Collusion/Strategy Homogeneity | 策略指纹相似度+持仓相关性AP-08行为相关性分析 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-4883 | 涌现行为 Emergent Behavior | 单个Agent行为正常但整体偏离预期AP-08系统级行为基线 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-5062 | Half-Open Probe 熔断器半开试探 | 1次/超时周期的半开试探机制 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-5063 | Learning System Kill Switch 学习系统Kill Switch | 独立于学习系统的硬开关可立即暂停所有学习系统操作物理隔离 | D_AUTONOMY_PERM | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5064 | Agent Capability Assessment Agent能力评估协议 | 每季度评估Agent能力边界评估结果纳入漂移检测基线METR/UK AISI 2025 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |
| CAND-HARVEST-5065 | Cluster Behavior Risk Protection 群集行为风险防护 | 相关性>0.7自动差异化+市场压力时降仓防止AI版闪崩 | D_AUTONOMY_PERM | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0339 | Non-AI Boundary Guard 非AI边界守卫 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0705 | Model Registry 模型注册表 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0706 | Model Drift Detector 模型漂移检测器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0887 | Kill Switch 紧急制动开关 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0888 | Autonomy Fuse 自治熔断器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0889 | Drift Guard 漂移守卫 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0934 | Rollback System 回滚系统 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0986 | Escalation Protocol 升级协议 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0989 | Red-Blue Validator 红蓝对抗验证器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0990 | Auto Fix Engine 自动修复引擎 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0994 | Local Model 本地推理模型 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1074 | Knowledge Write Guard Protector 知识Write Guard保护器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1075 | Knowledge Snapshot Rollback Manager 知识快照回滚管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1076 | LLM Cost Guard LLM成本守卫 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1077 | Token Budget Manager Token预算管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1078 | Zone Crossing Boundary Validator Zone Crossing边界校验器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1080 | Auto-Guard Async Approval Manager Auto-Guard异步审批管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1262 | Parameter Optimizer 参数优化器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1263 | Risk Check RBAC Permission Controller 风控检查RBAC权限控制器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1264 | Risk Alert Notification Dispatcher 风控告警通知分发器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1265 | Health Check Service 健康检查服务 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1267 | Rollback Four-Tier Strategy Selector 回滚四级策略选择器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1268 | Dual-Storage Rollback Coordinator 双存储回滚协调器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1271 | Governance Phase Check Slimmer Governance Phase Check精简器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1272 | Budget Enforcer On-Demand Activator Budget Enforcer按需激活器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1273 | AI Comprehension Cost Dynamic Estimator AI理解成本动态估算器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1274 | PipelineOrchestrator CostTracker Component PipelineOrchestrator成本追踪组件 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1276 | AI Governance Framework Compliance Assessor AI治理框架合规性评估器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1277 | RBAC Permission Check Embedded Bridge RBAC权限检查内嵌桥接器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1278 | Rollback Operation Visual Tracker 回滚操作可视化追踪器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1279 | Feedback Loop Three-Layer Escalation Trigger Feedback Loop三层升级触发器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1280 | Token Budget Coordinator Token预算协调器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1282 | Drift Detector Statistical Drift Checker Drift Detector统计漂移检测器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1283 | System Version Upgrade Path Manager 系统版本升级路径管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1284 | Saga Definition Saga定义器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1285 | Orchestrated Saga Engine 编排式Saga引擎 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1286 | Choreography Saga Engine 协调式Saga引擎 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1287 | Compensation Action Manager 补偿动作管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1288 | Saga State Tracker Saga状态追踪器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1289 | Saga Observability Tracer Saga可观测性追踪器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1290 | AI-Driven Saga Orchestrator AI驱动Saga编排器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1291 | Compensation Dependency Graph Analyzer 补偿依赖图分析器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1292 | Saga Deadlock Detector Saga死锁检测器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1293 | Saga Version Compatibility Manager Saga版本兼容性管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1294 | Cross-Saga Transaction Coordinator 跨Saga事务协调器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1295 | AI Risk Classifier AI风险分类器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1296 | Governance Policy Engine 治理策略引擎 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1297 | Governance Dashboard 治理仪表盘 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1298 | AI Risk Assessor AI风险评估器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1299 | AI Risk Dependency Mapper AI风险依赖映射器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1300 | Responsible AI Dependency Auditor 负责任AI依赖审计器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1301 | Enhanced Confidence Cascade Mapper 增强置信度级联映射器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1302 | Saga/Process Manager Dependency Orchestrator Saga/流程管理器依赖编排器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1303 | Model Validation Dependency Orchestrator 模型验证依赖编排器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1304 | Model Monitoring Dependency Tracker 模型监控依赖追踪器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1305 | Model Risk Tier Classifier 模型风险分级器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1306 | Model Override Impact Analyzer 模型覆盖影响分析器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1307 | Model Drift Dependency Propagator 模型漂移依赖传播器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1308 | Model Validation Dependency Orchestrator v2 模型验证依赖编排器v2 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1309 | Model Risk Tier Dependency Classifier 模型风险等级依赖分类器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1310 | Model Override Dependency Impact Analyzer 模型覆盖依赖影响分析器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1311 | Model Inventory Dependency Graph Builder 模型清单依赖图构建器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1312 | Temporal GNN Dependency Drift Predictor 时序GNN依赖漂移预测器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1315 | PERM Budget Exempt Executor PERM预算豁免执行器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1316 | Kill Switch Direct Path Kill Switch直通路径 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1317 | Backtest-Live Deviation Monitor 回测-实盘偏差监控器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2174 | Four-Level Autonomy Model 四级自治模型 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2175 | ai_modifiable 自治区 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2176 | human_gated 门控区 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2177 | immutable 禁区 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2178 | HITL Human-in-the-Loop 人在闭环机制 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2335 | Level 0-3 Autonomy Levels 0-3自治级别 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2336 | HITL Confidence Upgrade HITL置信度升级 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2352 | Autonomy Boundary Change Process 自治边界变更流程 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2353 | HITL Mechanism HITL人在闭环机制 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2438 | Role and Interaction Journey 角色与交互旅程 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3367 | 隐性串谋 Implicit Collusion | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3549 | agent_creation_policy.py Agent创建策略 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3550 | anti_pattern_guard.py 反模式守卫 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3551 | anomaly_detector.py 异常检测器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3553 | auto_maintenance.py 自动维护 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3554 | bootstrap_verifier.py 引导验证器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3555 | genesis_bootstrap.py 创世引导 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3556 | build_sanitizer.py 构建清洗器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3557 | cache_invalidation.py 缓存失效器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3558 | cross_cutting.py 横切关注点 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3559 | dependency_auditor.py 依赖审计器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3560 | environment_manager.py 环境管理器 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3561 | exceptions.py 异常定义 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4879 | 决策一致性 Decision Consistency | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4880 | 通信异常 Communication Anomaly | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4881 | 资源消耗异常 Resource Consumption Anomaly | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4882 | 串谋/策略同质化 Collusion/Strategy Homogeneity | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4883 | 涌现行为 Emergent Behavior | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5062 | Half-Open Probe 熔断器半开试探 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5063 | Learning System Kill Switch 学习系统Kill Switch | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5064 | Agent Capability Assessment Agent能力评估协议 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5065 | Cluster Behavior Risk Protection 群集行为风险防护 | D_AUTONOMY_PERM | 候选待评（candidate） | harvest待评估（likely_new） |
