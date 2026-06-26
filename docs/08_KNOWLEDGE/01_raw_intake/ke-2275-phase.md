---
module_id: KE-2181-----phase-006
title: 4. 施工 Phase 规划
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4. 施工 Phase 规划

4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Hold | 等待触发条件命中（monitor §1.4） | ⏸️ Hold |
| scaffold | **Layer 1 完整**：Agent Card 模型 + AGENTS.md 注册 + JWT 身份验证 | 📋 Backlog |
| scaffold | **Layer 2 基础**：Task 状态机 + Message/Part Pydantic schema + 上下文包 | 📋 Backlog |
| scaffold | **Layer 3 核心**：Rule-based Coordinator + 基础任务交接 + Living Spec 同步框架 | 📋 Backlog |
| scaffold | **死锁防护 L1+L2**：Dijkstra 全局资源排序 + 超时熔断 | 📋 Backlog |
| experimental | **Layer 2 完整**：SSE 流式 + Push Notification + 输入协商 | 📋 Backlog |
| experimental | **冲突检测全栈**：语义冲突（AST diff + 依赖图）+ Mirror Mirror Loop 活锁检测 | 📋 Backlog |
| experimental | **仲裁**：三级仲裁 auto→escalate→block + arbitration_rules.yaml | 📋 Backlog |
| experimental | **死锁防护 L3+L4**：优先级抢占 + 序列化降级模式 | 📋 Backlog |
| experimental | **通信安全**：消息签名 + 防重放 + Session Smuggling 防御 | 📋 Backlog |
| experimental | **经济护栏**：委托代价评估 + 全链路 Token 预算 + 模型路由 | 📋 Backlog |
| experimental | **级联故障防护**：Bulkhead + Circuit Breaker + Dead Letter Queue | 📋 Backlog |
| experimental | **共识与协商**：6 状态协商会话机 + 投票/多数决引擎（含法定人数）+ 协商降级 4 级 | 📋 Backlog |
| experimental | **涌现检测框架**：5 类异常分类学 + "Agents of Chaos" 11 模式 F07/F09 信号监测 + Behavior Fingerprint | 📋 Backlog |
| experimental | **ML 异常检测**：Isolation Forest + Autoencoder pipeline + anomaly→throttle→freeze cascade（Phase 1 仅规则引擎） | 📋 Backlog |
| experimental | **Saga 回滚（简化版）**：git revert CT + per-agent worktree checkpoint + git-level 幂等性 | 📋 Backlog |
| experimental | 与 MOD-GATE_ENGINE/018/020/022 集成 + 审计闭环 | 📋 Backlog |
| beta | **可观测性**：分布式追踪 + A2A 指标 + Agent 信誉评分 | 📋 Backlog |
| beta | **性能优化**：消息批处理 + 上下文压缩算法优化 + Lazy Context Loading + Prompt Caching | 📋 Backlog |
| beta | **跨 IDE 一致性**：TRAE/Cursor/RooCode Agent Card 同步协议 + 协议版本协商 | 📋 Backlog |
| beta | **Saga 升级**：完整 Saga——LT/CT 正式注册 + 补偿编排引擎 + 反向拓扑序回滚 | 📋 Backlog |
| beta | **MAScope 集成**：Cross-Agent Semantic Flow PDAG 构建 + GNN 轨迹建模（依赖 scikit-learn/pytorch） | 📋 Backlog |
| beta | **A2A 协议层安全**：Agent Card 供应链完整性 + Task 流防操纵 + Artifact 投毒门禁 + Agent 间 DoS 限流（对标 A2ASECBENCH） | 📋 Backlog |
| beta | **结构化协商帧 (ANP)**：Negotiation Frame 替代 80% YAML 聊天 + Capability Token (JWT) + DelegationChainToken + 委托链权威性缩减 | 📋 Backlog |
| beta | **形式化验证 (TLA+)**：P1 死锁自由 + P2 委托安全 TLA+ 建模 + TLC 模型检查 + 7 属性运行时断言 | 📋 Backlog |
| beta | **多维向量信誉 (TrustFlow)**：5 维信誉向量 + TrustFlow 收缩映射 + LR2 自底向上评分 | 📋 Backlog |
| beta | **上下文腐烂防护**：注意力稀释/位置漂移/检索噪声检测 + 主动压缩 + 三层上下文架构 (Hot/Domain/Cold) | 📋 Backlog |
| beta | **用户同意编排**：4 状态同意机 + Ephemeral Scoped Token + AUTO_CONSENT 策略 + 直接数据通道 | 📋 Backlog |
| beta | **宪法治理引擎**：GovernanceGate 零容忍门控 + CONSTITUTION.md + intent drift 检测 + Cross-Policy Impact Graph（对标 Council + Microsoft AGT ADR 0006 + HC-12） | 📋 Backlog |
| beta | **Agent 免疫系统**：三层免疫 (innate 模式匹配 + adaptive Critic 分析 + memory 哈希查表) + 隔离检疫状态机 + 攻击链因果图 + 工具调用运行时策略治理（对标 ClawGuard） | 📋 Backlog |
| beta | **选择性遗忘引擎**：FSFM 四类遗忘 (passive/active/safety/reinforcement) + Cascading Forget + Two-Pass Deletion + 遗忘审计日志（对标 FSFM + EU AI Act 2026） | 📋 Backlog |
| beta | **空转综合征检测**：PollingStorm 防御 + ana
