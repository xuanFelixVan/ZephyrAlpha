---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.infrastructure（160 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.infrastructure（160 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=5，wired=111，wired_by_header=43，wired_dynamic=1；初判汇总：dispute=5，mount=155

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/infrastructure/_extensions/__init__.py` | D_INFRA_RUNTIME/_extensions sub-package | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 infrastructure 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/infrastructure/api/__init__.py` | D_INFRA_RUNTIME/api sub-package | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 infrastructure 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/infrastructure/core/__init__.py` | D_INFRA_RUNTIME/core sub-package | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 infrastructure 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/infrastructure/models/__init__.py` | D_INFRA_RUNTIME/models sub-package | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 infrastructure 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/infrastructure/services/__init__.py` | D_INFRA_RUNTIME/services sub-package | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 infrastructure 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/infrastructure/a2a_protocol/a2a_card_registry.py` | A2A Card Registry — 全局 Agent Card 注册单例 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/__init__.py` | A2A Protocol — MOD-INF-025 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/_base_server.py` | class-name-alias: a2a_protocol governance MCP 基类（极简 stub），区别于 infrastructure/_base_server.py 和 integration/mcp/_base_ser | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/audit_logger.py` | （无文档头，按文件名语义：audit_logger） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/auditor.py` | G-CT-008 契约：A2A -> Audit 审计 Agent 间通信. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/error_codes.py` | （无文档头，按文件名语义：error_codes） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/governance_adapter.py` | A2A GovernanceAdapter — Phase 4 治理集成桥接器 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/phase_hold.py` | Phase 4 Hold — governance 子包派生扩展（真源收敛）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/policy_engine.py` | （无文档头，按文件名语义：policy_engine） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/protocol.py` | G-CT-008 — A2ACommunication Pydantic V2 BaseModel agent-to-agent 通信数据结构. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/rate_limiter.py` | 5.36.4 修复：按 key 分桶，替代单一 _requests 列表 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/governance/session_manager.py` | （无文档头，按文件名语义：session_manager） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer1_discovery/__init__.py` | Layer 1: 发现+身份 — Agent Card 模型, AGENTS.md 注册, JWT 身份验证 | 2026-09-18（16天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer1_discovery/a2a_registry.py` | A2A Registry — Agent Card 注册与发现 | 2026-09-16（18天） | in=4/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer1_discovery/agent_card.py` | Agent Card 模型 — A2A Layer 1 Discovery | 2026-09-16（18天） | in=4/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer1_discovery/identity_verifier.py` | Identity Verifier — JWT 身份验证器 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/a2a_schemas.py` | A2A Message/Part 系统 — Layer 2 Communication | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/a2a_state.py` | A2A Task 状态机 — Layer 2 Communication | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/context_package.py` | Context Package — A2A 上下文包 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/handoff_manager.py` | Handoff Manager — Agent 间任务交接 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/message_router.py` | Message Router — A2A 消息路由 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/push_notifier.py` | Push Notifier — A2A 推送通知 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer2_communication/streaming.py` | Streaming — A2A 流式传输 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/_consensus.py` | Re-export bridge for layer3_coordination consensus symbols. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/_governance_integration.py` | Re-export bridge for layer3_coordination governance integration symbols. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/_intelligence.py` | Re-export bridge for layer3_coordination intelligence symbols. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_agent_blocklist.py` | A2A Agent 黑名单管理（重命名自 a2a_protocol_security.py，AI-14 审计 P5 修复） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_anomaly_detector.py` | A2A 统计异常检测引擎 — 基线学习 + 实时异常判断 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_behavior_fingerprint.py` | A2A 行为指纹 — Agent 行为模式学习与画像 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_blame_attribution.py` | A2A 责任归属引擎 — 因果链分析 + 责任分配 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_causal_trace.py` | A2A 因果追踪 — 跨 Agent 操作因果链图谱 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_collusion_detector.py` | A2A 合谋检测器 — Agent 间串通模式识别 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_cross_agent_semantic_flow.py` | A2A 跨 Agent 语义流追踪 — 知识+意图在 Agent 间传递 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_dashboard.py` | A2A 监控仪表盘 — Agent 集群运行状态可视化面板 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_debate.py` | A2A 结构化辩论协议 — 多轮主张->反驳->合成 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_delegation_chain.py` | 委托链 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_economics.py` | A2A 经济学——Token/API成本追踪 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_forgetting.py` | A2A 遗忘机制 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_formal_verification.py` | A2A 形式化验证 — 协议属性模型检查 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_frame_negotiation.py` | A2A ANP 帧协商协议 — Agent Negotiation Protocol 帧层协商 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_governance_adapter.py` | A2A 治理适配器 — 连接 A2A 协议与 Governance 层 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_idempotency.py` | A2A 幂等性保证 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_idle_guard.py` | A2A 空闲守卫 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_knowledge_distill.py` | A2A 知识蒸馏 — 跨 Agent 经验提炼与共享 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_latent_comm.py` | A2A 隐性通信检测 — 检测 Agent 通过副作用隐式通信 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_negotiation.py` | A2A 协商协议 — Agent 间资源/任务分配协商 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_protocol_gateway.py` | A2A 协议网关 — Agent 间请求分发与协议转换 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_saga.py` | A2A Saga 事务协议 — 多 Agent 跨步分布式事务 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_security.py` | A2A 安全内容扫描器 — 六大类威胁检测 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_temporal_admission.py` | 时序准入控制 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_tracing.py` | A2A 分布式追踪 — 跨 Agent 请求链追踪 (Span-based) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_voting.py` | A2A 加权投票协议 — 多 Agent 共识达成机制 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_work_steal.py` | A2A 工作窃取调度器 — 跨 Agent 负载均衡 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/cascade_guard.py` | 级联守卫——防止失败在Agent间级联 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/conflict_detector.py` | A2A 冲突检测引擎 — 语义+文本+资源三维冲突检测 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/construction_verifier.py` | 施工后验证器 — 自指悖论防御：不橡胶图章，真正验证 A2A 协议模块的施工完整性 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/deadlock_guard.py` | P2: 死锁守卫 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/livelock_detector.py` | P2: 活锁检测器 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/semantic_diff.py` | A2A 语义差异引擎 — 结构感知的 Agent 间差异检测 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/session_smuggling_defense.py` | A2A Session 走私防御 — 防止跨 Agent session 上下文伪造 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/spec_sync.py` | A2A Living Spec 同步 — 蓝图与实现的双向漂移管理 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/local_first_arch.py` | （无文档头，按文件名语义：local_first_arch） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/migration_strategy.py` | （无文档头，按文件名语义：migration_strategy） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/multi_model_consensus.py` | （无文档头，按文件名语义：multi_model_consensus） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/offline_autonomy.py` | （无文档头，按文件名语义：offline_autonomy） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/offline_resilience.py` | （无文档头，按文件名语义：offline_resilience） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/a2a_protocol/phase_hold.py` | [BLUEPRINT] MOD-INF-025 \| docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md \| §3 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/adaptation/__init__.py` | Re-export wrapper: true source is zephyr.shared.adaptation. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/__init__.py` | asset-inventory — MOD-INF-026 · 资产盘点系统：发现->分类->登记->对账->生命周期 | 2026-09-18（16天） | in=0/out=0·wired_dynamic | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/classifier.py` | AssetClassifier — MOD-INF-026 L2 资产自动分类器 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/dependency.py` | MOD-INF-026 §18 — 资产依赖图。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/index_generator.py` | UnifiedAssetIndex — MOD-INF-026 L3 统一资产索引生成器 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/mcp_server.py` | AssetInventory MCP Server — MOD-INF-026 蓝图 §21 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/models.py` | AssetInventoryModels — MOD-INF-026 Pydantic V2 共享数据模型 | 2026-09-16（18天） | in=8/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/registry_adapter.py` | MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/asset_inventory/scanner.py` | AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描器 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/auto_diagnostics.py` | RI-12 AutoDiagnostics — 自动诊断引擎 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/blueprint_code_sync.py` | Blueprint-Code Sync — 蓝图-代码索引同步验证。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/compensation/__init__.py` | Re-export wrapper: true source is zephyr.shared.compensation. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/config/__init__.py` | ZephyrAlpha — 基础设施 Infrastructure Layer — Configuration Management | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/config/app_config.py` | app_config.py — 应用配置数据类与加载/热重载逻辑 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/config/config_center.py` | ConfigCenter — 统一配置中心（MOD-INF-091）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/config_validator.py` | M-12 ConfigValidator — 配置参数校验器 | 2026-09-20（14天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/contract_tester.py` | M-11 ContractTester — 契约测试框架 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/cost_tracker.py` | RI-15 CostTracker — 成本追踪器 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/dashboard/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/dashboard/components/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/dependency/__init__.py` | Re-export wrapper: true source is zephyr.shared.dependency. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/draft/__init__.py` | Re-export wrapper: true source is zephyr.shared.draft. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/dry_run_simulator.py` | RI-14 DryRunSimulator — 干运行模拟器 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/duckdb_runtime_gate.py` | duckdb_runtime_gate.py — 裸 duckdb.connect 运行时拦截器（bare_sql_gate 的运行时后备防线） | 2026-09-29（5天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/event_bus_upgrade.py` | DEPRECATED: 此文件已废弃。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/event_store.py` | RI-13 EventStore — 事件存储 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/h1_redis_hot/__init__.py` | H1 Redis 热缓存模块——盘中实盘/模拟盘 <5ms 因子截面在线存储（DD-11-01）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/h1_redis_hot/h1_cqrs_projectors.py` | H1CqrsProjectors — 事件→Redis 物化视图投影器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/h1_redis_hot/h1_integration.py` | H1 Redis 集成适配器——连接 D-FACTOR/SIGNAL/RISK 与 H1 热缓存。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/h1_redis_hot/h1_redis_reader.py` | H1RedisReader — 决策引擎 <5ms 在线特征查询。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/h1_redis_hot/h1_redis_schema.py` | H1 Redis 热缓存 Key Schema（DDL-as-Code）。 | 2026-09-16（18天） | in=9/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/h1_redis_hot/h1_redis_writer.py` | H1RedisWriter — D-FACTOR Engine 每 3 秒截面写入 Redis（PIPELINE 模式）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/impact/__init__.py` | core.impact — auto-generated package init. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/impact/impact_propagator.py` | Impact Propagator — 变更影响传播分析。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/impact/llm_impact_analyzer.py` | LLM Impact Analyzer — 语义影响分析器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/infrastructure_base.py` | 基础设施 — Infrastructure Layer Skeleton | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/maintenance/__init__.py` | Re-export wrapper: true source is zephyr.shared.maintenance. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/model_profiler/__init__.py` | Model Profiler — 本地 + 远程模型性能基准测试 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/observability/trace_decorator.py` | （无文档头，按文件名语义：trace_decorator） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/backpressure_manager.py` | Pipeline — Backpressure Manager | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/backpressure_types.py` | backpressure_types.py - Pipeline backpressure signal data types | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/cost_tracker.py` | CostTracker —— LLM 调用成本追踪器（SRC-0025） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/ct_pipe_routing.py` | CT-PIPE-ORC-001 — TaskCard -> 管线入口节点路由 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/dead_letter_queue.py` | DeadLetterQueue — 死信队列 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/model_router.py` | ModelRouter — 模型路由与降级链管理 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/models.py` | Pipeline 数据模型 | 2026-09-16（18天） | in=9/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/pipeline_agent_bridge.py` | Pipeline -> Agent Bridge — 双编排器桥接层 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/pipeline_roadmap.py` | Pipeline 未来版本路线图——v0.10.0 -> v0.12.0 规划骨架。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pipeline/routing_plugins.py` | Pipeline Routing Plugin System — K8s Scheduling Framework 对标 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/pydantic_v2_migrator.py` | M-15 PydanticV2Migrator — Pydantic V2 迁移工具 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/queue/__init__.py` | core.queue — auto-generated package init. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/queue/task_scheduler.py` | Task Scheduler — 任务调度器。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/registry_governance.py` | Registry Governance — MOD-INF-037 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/reliability/__init__.py` | core.reliability — auto-generated package init. | 2026-09-21（13天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/reliability/context_guard.py` | Context Guard — 上下文契约守卫。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/agent_cooldown.py` | AgentCooldown — Agent 冷却隔离器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/auto_rollback_trigger.py` | AutoRollbackTrigger — 自动回滚触发器。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/checkpoint_gc.py` | CheckpointGC — Checkpoint 垃圾回收。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/commit_quality_gate.py` | CommitQualityGate — Commit 质量基础设施。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/contract.py` | CT-RBK-GATE-001 集成契约落地——Rollback System Exit Code 完整定义。 | 2026-09-16（18天） | in=4/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/contracts.py` | [BLUEPRINT] MOD-INF-021 \| docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/credential_rotation_trigger.py` | CredentialRotationDetector — 回滚后凭据泄露检测（仅检测，不轮换）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/cross_platform_shell.py` | CrossPlatformShell — 跨平台 Shell 脚本双输出。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/drift_fix.py` | （无文档头，按文件名语义：drift_fix） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/env_watcher.py` | EnvWatcher — 环境变量热重载监控器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/external_merkle_proof.py` | External Merkle Proof — 外部可验证回滚完整性证明。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/git_infra_snapshot.py` | GitInfraSnapshot — Git 基础设施快照与污染防护。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/hallucination_guard.py` | HallucinationGuard — AI 幻觉防护：回滚后强制状态验证。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/intent_archiver.py` | IntentArchiver — 意图存档保护。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/knowngoodstate_ledger.py` | KnowngoodstateLedger — 已验证正确状态收据。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/right_to_be_forgotten.py` | Right to be Forgotten — GDPR 遗忘权合规检查器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/rollback_context_restorer.py` | RollbackContextRestorer — 上下文恢复器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/rollback_dashboard.py` | RollbackDashboard — 回滚仪表盘（零依赖 Markdown）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/rollback_loop_detector.py` | RollbackLoopDetector — 回滚循环检测器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/rollback_state_machine.py` | RollbackStateMachine — 回滚步骤级状态机。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/rollback_verifier.py` | RollbackVerifier — 回滚后验证器。 | 2026-09-19（15天） | in=3/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/rollback_wal.py` | RollbackWAL — 回滚预写日志。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/runbook_generator.py` | RunbookGenerator — 回滚操作 Runbook 自动生成。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/secret_rotation_aware.py` | SecretRotationAware — 密钥轮替感知器。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/semantic_similar_detector.py` | SemanticSimilarDetector — 语义变形攻击检测。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/rollback/temporal_context_adapter.py` | TemporalContextAdapter — AI 时间上下文断裂修复。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/runtime/concurrency_guard.py` | concurrency_guard — 回滚操作并发安全守卫。 | 2026-09-16（18天） | in=4/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/runtime/gate_coordinator.py` | Rollback->Gate 协调器 — freeze_all / thaw_all | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/runtime/sandbox_enforcer.py` | SandboxEnforcer — Agent 沙盒隔离。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/session/__init__.py` | Re-export wrapper: true source is zephyr.shared.session / zephyr.shared.session_continuity. | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/strategy_canary_release.py` | StrategyCanaryRelease — 策略灰度发布（MOD-INF-072）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/system_snapshot.py` | SystemSnapshotter — M1 系统状态镜像（CL-017 RI 扩展模式） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
| `src/zephyr/infrastructure/warm_hot_gate.py` | M-14 WarmHotGate — Warm->Hot 阻断门 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 infrastructure 无预设映射）（活线在身未挂线） |
