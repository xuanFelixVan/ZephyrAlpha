---
module_id: KE-4052
title: 3. 文件组成
category: module_blueprint
ttl: permanent
---

# 3. 文件组成

3. 文件组成

| 文件 | 职责 | 状态 |
|------|------|:---:|
| `agent_card.py` | Agent Card 数据模型——Pydantic V2 + 校验 | ⏸️ Hold |
| `a2a_registry.py` | Agent 注册表——Agent 启动时注册能力到 AGENTS.md | ⏸️ Hold |
| `a2a_schemas.py` | A2A 全协议 Pydantic Schemas——Task/Message/Part/ContextPackage | ⏸️ Hold |
| `a2a_state.py` | A2A TaskState 枚举 + 合法转移矩阵 | ⏸️ Hold |
| `identity_verifier.py` | Agent 身份验证——JWT 签发/校验 + SPIFFE + 克隆检测 | ⏸️ Hold |
| `handoff_manager.py` | 任务交接管理——SUBMITTED → dispatch → WORKING 生命周期 | ⏸️ Hold |
| `context_package.py` | 委托上下文包——7 字段结构化状态传递（对标 KBG-0041） | ⏸️ Hold |
| `message_router.py` | Message/Part 路由器——校验 schema + 分发到目标 Agent | ⏸️ Hold |
| `streaming.py` | SSE 流式传输——长任务实时进度推送 | ⏸️ Hold |
| `push_notifier.py` | Push Notification——任务状态变更主动推送 | ⏸️ Hold |
| `supervisor.py` | Rule-based Coordinator——任务分解 + Agent 分配 + 进度监控 + 结果整合 | ⏸️ Hold |
| `spec_sync.py` | Living Spec 管理器——扫描/同步/验证接口规范 | ⏸️ Hold |
| `conflict_detector.py` | 冲突检测主引擎——文本 + 语义双层（SC-DETECT-001~004） | ⏸️ Hold |
| `semantic_diff.py` | 语义差异分析——AST diff + 依赖图 + 接口契约对比 | ⏸️ Hold |
| `arbitrator.py` | 仲裁器——三级递进 auto→escalate→block | ⏸️ Hold |
| `arbitration_rules.yaml` | 仲裁规则 SSoT——文本冲突/语义冲突各场景的处理规则（对 AI 只读） | ⏸️ Hold |
| `deadlock_guard.py` | 死锁防护——四层（Dijkstra+Timeout+Preemption+Sequentialization）+ 等待图 | ⏸️ Hold |
| `livelock_detector.py` | 活锁检测——Politeness/Mirror/EndlessChain 三模式 | ⏸️ Hold |
| `a2a_security.py` | A2A 消息安全——签名/防重放/防篡改 | ⏸️ Hold |
| `session_smuggling_defense.py` | Agent Session Smuggling 防御——信任评分 + 意图一致性 | ⏸️ Hold |
| `a2a_economics.py` | 经济护栏——委托代价评估 + 全链路 Token 预算 + 模型路由 | ⏸️ Hold |
| `a2a_tracing.py` | 分布式追踪——Correlation ID + Span Context + trace YAML 落盘 | ⏸️ Hold |
| `a2a_metrics.py` | A2A 指标收集——消息延迟/交接时间/冲突解决时间/死锁事件 | ⏸️ Hold |
| `cascade_guard.py` | 级联故障防护——Bulkhead + Circuit Breaker + Dead Letter Queue | ⏸️ Hold |
| `construction_verifier.py` | 施工验证——编译时检查 + 独立验证 checklist 生成 | ⏸️ Hold |
| `a2a_negotiation.py` | 协商会话机——6 状态 PROPOSED→ACTIVE→AGREED/REJECTED/EXPIRED→DORMANT | ⏸️ Hold |
| `a2a_voting.py` | 投票/多数决引擎——多数决 + 加权投票 + 否决权 + 法定人数 | ⏸️ Hold |
| `a2a_collusion_detector.py` | 合谋检测——Pairwise Vote Correlation + Jaccard 异常检测 | ⏸️ Hold |
| `a2a_anomaly_detector.py` | 异常检测管道——Isolation Forest + Autoencoder + 三级响应 cascade | ⏸️ Hold |
| `a2a_anomaly.yaml` | 异常检测规则 SSoT——5 类异常的行为信号 + 规则阈值（对 AI 只读） | ⏸️ Hold |
| `a2a_cross_agent_semantic_flow.py` | Cross-Agent Semantic Flow——PDAG 构建 + GNN 轨迹建模（对标 MAScope） | ⏸️ Hold |
| `a2a_behavior_fingerprint.py` | Behavior Fingerprint 库——Agent 完成习惯模式记录 + 行为偏离检测 | ⏸️ Hold |
| `a2a_saga.py` | Saga 事务管理器——LT/CT 配对注册 + 补偿编排 + 回滚链 | ⏸️ Hold |
| `a2a_checkpoint.py` | 分布式检查点——per-agent worktree snapshot + 全局检查点目录 | ⏸️ Hold |
| `a2a_idempotency.py` | 幂等性门禁——Task-level + Operation-level + Git-level 三层去重 | ⏸️ Hold |
| `a2a_protocol_security.py` | A2A 协议层安全——Agent Card 供应链完整性 + Task 流防操纵 + Artifact 投毒门禁 + Agent 间 DoS 限流（对标 A2ASECBENCH） | ⏸️ Hold |
| `a2a_card_registry.py` | Agent Card 注册表——SHA-256 指纹 + 签名强制校验 + 克隆检测 | ⏸️ Hold |
| `a2a_frame_negotiation.p
