---

doc_type: index
status: active
title: "behavioral-auditor — 目录索引"
version: "3.0.0"
created: "2026-05-08"
updated: "2026-05-10"
belongs_to: "MOD-INF-027"
maturity: "100%"
blueprint_id: DOM-GOV-001
---


# behavioral-auditor

> AI Behavior Boundary Audit Engine v3.0.0 — MOD-INF-033
> 成熟度：100% | 状态：Draft（v3.0.0 容量升级蓝图层已补齐，施工待启动）

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| [blueprint.md](blueprint.md) | Markdown | BehavioralAuditor v3.0.0 全维度蓝图（§0~§44 + 附录 + 容量升级方案） |
| [index.md](index.md) | Index | 本目录索引 |

## 蓝图结构（v3.0.0）

> ═══════════ v3.0.0 容量升级蓝图层 ═══════════

| 章节 | 内容 |
|------|------|
| §30 | PartitionedEventConsumer — 事件流 8 分片并行消费 |
| §31 | PerSessionBaseline — 100 个 AI 独立行为基线 |
| §32 | ShardedSessionStore — 跨 Session 状态 SQLite 分片存储 |
| §33 | TieredEvidenceStore — Evidence Chain Hot→Warm→Cold 三级存储 |
| §34 | TokenBudgetRecalibration — Per-Session 日预算 + 全局月预算 + 风险降级 |
| §35 | SampledMetaAudit — L0 快速 + L1 采样(10%) 分层自审计 |
| §36 | AggregatedMetrics — Prometheus 指标聚合防标签爆炸 |
| §37 | TieredCircuitBreaker — Session 级 + 依赖级双层熔断 |
| §38 | SessionCostLedger — 每 AI 独立 Token 成本账本 |
| §39 | TrustTieredAudit — HIGH/MEDIUM/LOW 三级信任分级审计 |
| §40 | DualModeEngine — REALTIME + MICROBATCH + DEFER 三通道 |
| §41 | LocalPermissionCache — 许可矩阵 TTL 5s 本地缓存 |
| §42 | SharedBlueprintCache — 100 Session 共享只读蓝图缓存 |
| §43 | AnchorAccessBroadcastBus — 锚点文件 <100ms 实时广播 |
| §44 | RateLimitedRedTeam — 红队限速 + 语义去重 + 批量生成 |

> ═══════════ v2.0.0 功能设计层（保留不变） ═══════════

| 章节 | 内容 |
|------|------|
| §0 | 冷启动分派——AI 自动发现路径 |
| §1 | 审计定位——三审计类型差异 + Anthropic 三层安全模型对标 |
| §2 | 架构概览——完整数据流图 |
| §3 | 触发条件——BH-001~008 八类事件驱动触发 |
| §4 | 判定模型——许可矩阵 × 决策树 |
| §5 | 响应模型——Block/Alert/Rollback + Evidence Chain |
| §6 | Provider 集成——11 个 Provider 复用 |
| §7 | Orchestrator 集成——Phase 2 dispatch |
| §8 | 安全边界——自身权限 + Prompt 注入防御 |
| §9 | 版本历史——v1.0.0 → v2.0.0 |
| §10 | Agent Skill 自动发现——SKILL-DOM-BEH-001 |
| §11 | 多模型共识辩论——2/2 共识协议 |
| §12 | 渐进式响应梯度——L0~L6 七级 |
| §13 | Meta-Audit 自审计——谁审计审计者？ |
| §14 | 行为基线画像——6 维异常检测 |
| §15 | 红队对抗攻击自生长——压力测试 |
| §16 | FLE 反馈闭环——规则自适应 |
| §17 | 全系统集成矩阵——18 模块连接契约 |
| §18 | 可观测性——四黄金信号 + Prometheus |
| §19 | 熔断器与降级——防级联故障 |
| §20 | 灾难恢复与离线自治 |
| §21 | 成本感知——Token 预算模型 |
| §22 | CLI + MCP 双入口 |
| §23 | 合规映射——ISO 27001/SOC2/GDPR |
| §24 | RULE-ZERO~NINE/PRE-OP/ZephyrLock 协议集成 |
| §25 | Session 连续性——跨 Session 上下文 |
| §26 | 蓝图自健康诊断 |
| §27 | Prompt 版本锁定与回归测试 |
| §28 | 氛围编程全自动化路径 |
| §29 | 维度补齐验证——一阶~N阶全覆盖 |
| 附录 A | 术语表 |
| 附录 B | 触发条件全清单 |

## 集成关系

| 对端模块 | 关系 |
|---------|------|
| MOD-INF-027 AuditOrchestrator v5.0.0 | 所属调度者（Phase 2 TRIAGE dispatch）+ v5.0.0 ModuleGraph/Coalescer/HashStore 复用 |
| MOD-INF-028 SemanticAuditor | 平级审计子系统 |
| MOD-INF-020 AuditTrail | 数据源（事件流，v3.0.0 需支持分片消费） |
| MOD-INF-007 Gate Engine | 判定依据（许可矩阵）+ AnchorAccessBroadcastBus 实时推送 |
| MOD-INF-021 Rollback | 执行器（回滚） |
| MOD-INF-012 Database System | **新增**：Evidence Chain / Baseline / Session State SQLite 存储 |
| SYS-MASTER-001 §〇 | **新增**：容量升级 Worker Pool / 硬件感知调度 |
| 其余模块 | 见 §17 全系统集成矩阵 + §4 契约变更 |

## 导航

- [上级目录](../index.md)
- [cross_layer 模块索引](../../index.md)
- [项目根](../../../../../docs/index.md)