---
module_id: MOD-GOVERNANCE
title: "Governance Domain 蓝图 — Agent治理八件套跨模块集成契约"
doc_type: blueprint
status: Active
version: "0.13.0"
layer: L1_foundation
layer_name: domain
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
ttl: permanent
last_updated: "2026-05-15"
last_verified: "2026-05-14"
construction_progress: partially_implemented
actual_disk_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_governance\\blueprint.md"
template_for: blueprint
generation: 2
functional_domain: governance
responsibility_domain: D_GOVERNANCE
parent_module: "SYS-MASTER-001"
belongs_to: "SYS-MASTER-001"
rule_form: structural
scope: global
stability: evolving
verifiability: automated
priority: P0
runtime_plane: cold
summary: "治理域Level 1集成蓝图——覆盖Agent治理八件套（MOD-INF-018~025）跨模块集成契约。容量升级设计已拆分至MOD-GOV-CAP-001。三轮审计29项D-GAP全覆盖。"
codification_level: L1
codification_at: "2026-05-14"
submodule_path: src/zephyr/governance/
depends_on:
  - target: "SYS-MASTER-001"
    at: "全篇"
    why: "Level 0系统总蓝图——治理域是金字塔Level 1节点"
  - target: "MOD-MASTER_BLUEPRINT"
    at: "全篇"
    why: "基础设施域集成蓝图——治理域依赖基建域基础能力"
  - target: "MOD-GATE_ENGINE"
    at: "§3"
    why: "Gate Engine——线3权限判定链第3步（ARB-9），G-CT契约隐含依赖"
  - target: "MOD-INF-016"
    at: "§3"
    why: "Shared Core——_concurrency.py/AiAuditLogger/PermissionGuard等共享组件"
  - target: "MOD-GOV-CAP-001"
    at: "§0/§3.10~3.13/§9/§11"
    why: "容量升级设计独立蓝图——分层执行/熔断器/分片存储/GPU加速/施工路线图/测试矩阵权威来源"
  - target: "MOD-DATABASE"
    at: "§9"
    why: "Database——ARB-8裁定events表为审计唯一权威存储，分片存储设计直接依赖"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_system_master\\blueprint.md"
    section: "全篇"
    why: "系统总蓝图"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint.md"
    section: "全篇"
    why: "基础设施域集成蓝图"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "全篇"
    why: "蓝图模板v3.5/v3.6"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "全篇"
    why: "压缩工作流标准"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_governance\\capacity-upgrade\\blueprint.md"
    section: "全篇"
    why: "容量升级设计独立蓝图（MOD-GOV-CAP-001）"
tags:
  - domain-blueprint
  - governance
  - level-1
  - agent-rbac
  - audit-trail
  - rollback
  - escalation
  - drift-detector
  - budget-enforcer
  - a2a-protocol
  - agent-spec
  - integration-contracts
  - capacity-planning
ssot_claims:
  - claim: "Agent治理八件套跨模块集成契约(G-CT-001~022)"
    scope: layer
  - claim: "治理域循环依赖裁定(ARB-1~9)"
    scope: layer
  - claim: "治理域设计缺失追踪(D-GAP-01~12索引 + D-GAP-13~29设计)"
    scope: layer
    note: "D-GAP-01~12设计真源在MOD-GOV-CAP-001，本蓝图仅保留索引+引用"
  - claim: "治理域Phase施工路线图与进度"
    scope: layer
design_maturity: design
build_status: generated
---

# Governance Domain 蓝图 — Agent治理八件套跨模块集成契约

> module_id: MOD-GOVERNANCE | version: 0.5.1 | status: active | layer: domain | blueprint_level: domain
> actual_disk_path: D:\ZephyrAlpha\docs\03_modules\_domain_governance\blueprint.md | generation: 2 | construction_progress: partially_implemented

## 概述

本蓝图是 ZephyrAlpha 治理域的 Level 1 集成蓝图。核心职责：定义 Agent 治理八件套（RBAC→Audit→Rollback→Escalation→Drift→Budget→A2A→Agent Spec）之间的跨模块集成契约（G-CT-*）。容量升级设计已拆分至 [MOD-GOV-CAP-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/capacity-upgrade/blueprint.md)。三轮审计合计 29 项 D-GAP 全覆盖。上游依赖 SYS-MASTER-001（系统总蓝图）和 MOD-MASTER_BLUEPRINT（基础设施域），下游被 8 个治理模块消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

## 模板章节映射表

> 本文件按审计轮次+域内逻辑组织（A/B/C/D + 0~10），以下映射表说明与蓝图模板 v3.5/v3.6 必需章节的对应关系。

| 模板必需章节 | 本文件对应章节 | 状态 |
|------------|-------------|:---:|
| §1 设计背景与目标 | A.1 审计总结 + 1.域定位 | ✅ |
| §2 模块边界 | 2.域内模块清单 | ✅ |
| §3 架构设计 | 3.域内集成契约 | ✅ |
| §4 接口契约 | 3.域内集成契约 G-CT-* | ✅ |
| §5 约束条件 | 0.容量升级设计与SLO | ✅ |
| §6 错误处理 | 3.域内契约异常处理 | ✅ |
| §8 安全考量 | D-GAP-22 沙箱隔离 | ✅ |
| §9 测试策略 | 10.升级后测试矩阵 | ✅ |
| §10 依赖关系 | 10.依赖关系（四子节） | ✅ |
| §11 产出物 | 2.域内模块清单路径 | ✅ |
| §12 集成目标 | 3.域内集成契约 | ✅ |
| §13 需要更新 | 4.域内施工顺序 | ✅ |
| §14 风险 | 6.风险与缓解 | ✅ |
| §0 代码对齐 | C.蓝图与代码对齐施工 | ✅ |
| §16 施工指引 | 9.施工升级路线图 | ✅ |
| §17 容量升级 | 0.容量升级设计与SLO | ✅ |
| §18 决策记录 | 见§18决策记录（永久时态） | ✅ |
| 治理信息 | 见文件末尾 | ✅ |
| §7 备选方案 | 已删除→§18决策记录覆盖 | v3.6删除 |
| §15 后果 | 已删除→正面在§1，负面在§14 | v3.6删除 |
| §0.2 对齐验证矩阵 | 见下方 §0.2 | ✅ |
| §0.3 版本-代码映射 | 见下方 §0.3 | ✅ |
| §0.4 SSoT与责任唯一性 | 见下方 §0.4 | ✅ |
| §0.5 代码目录唯一性 | 见下方 §0.5 | ✅ |
| §5.5 自动化触发机制 | 见下方 §5.5 | ✅ |
| §6.2 退化矩阵 | 见下方 §6.2 | ✅ |

---

---

### §0.2 对齐验证矩阵

| 验证项 | 蓝图声称 | 代码实际 | 对齐状态 |
|--------|---------|---------|:---:|
| BulkheadExecutorV2 接线 | §12: ✅ 已接线 | run_all.py `_USE_BULKHEAD=True` + `dispatch_with_locks()` | ✅ |
| ShardRouter shard_count=16 | §3.12 + ALIGN-04 | `_concurrency.py` `_shard_count=16` | ✅ |
| ShardRouter SHA256 路由 | ALIGN-05 | `_concurrency.py` `hashlib.sha256` | ✅ |
| get_audit_writer() 单例 | G-CT-014 旁路桥接 | `audit_trail/writer.py` 双重检查锁定 | ✅ |
| AuditEventType.SESSION_RECORD | G-CT-014 | `models.py` 枚举值 | ✅ |
| AuditEventType.BUDGET_ENFORCEMENT | G-CT-014 | `models.py` 枚举值 | ✅ |
| FindingLifecycleManager 自动清理 | D-GAP-13 | lifecycle_manager CircadianScheduler hour=4 | ✅ |
| GovernanceWatchdog Boot 启动 | D-GAP-20 | lifecycle_manager boot step 09a | ✅ |
| GateCache 每日清空 | D-GAP-16 | lifecycle_manager CircadianScheduler hour=0 | ✅ |
| ChangeImpactAnalyzer 增量触发 | G-CT-017 | run_incremental.py 自动串联 | ✅ |
| NEW-01~15 脚本 | §12 C.3 | 14 已实现 + 1 复用(NEW-14) | ✅ |
| D-GAP-01~12 设计真源 | ssot_claims | → MOD-GOV-CAP-001 §1.3 | ✅ |

### §0.3 版本-代码映射

| 版本 | 核心变更 | 代码影响范围 | 施工状态 |
|------|---------|------------|:---:|
| v0.1.0 | 初始蓝图（203行） | 无代码变更 | ✅ |
| v0.2.0 | 容量扩展设计 | +§0/§3.9~3.15/§9/§10 | ✅ |
| v0.3.0 | NEW-01~08 实现 | `_concurrency.py` + 6 个新脚本 | ✅ |
| v0.3.1 | NEW-09~15 实现 | 3 个新脚本 + `_concurrency.py` 3 类 | ✅ |
| v0.13.0 | 自动化接线 + SSoT 修复 | lifecycle_manager + run_incremental + ssot_claims | ✅ |

### §0.4 SSoT与责任唯一性

| SSoT 声明 | 真源蓝图 | 委托蓝图 | 判定 |
|-----------|---------|---------|------|
| Agent治理八件套跨模块集成契约(G-CT-001~022) | MOD-GOVERNANCE | — | 真源 |
| 治理域循环依赖裁定(ARB-1~9) | MOD-GOVERNANCE | — | 真源 |
| 治理域设计缺失追踪(D-GAP-01~12索引) | MOD-GOVERNANCE | MOD-GOV-CAP-001(设计真源) | 索引+引用 |
| 治理域设计缺失追踪(D-GAP-13~29设计) | MOD-GOVERNANCE | — | 真源 |
| 治理域Phase施工路线图与进度 | MOD-GOVERNANCE | — | 真源 |
| 治理域容量升级架构 | MOD-GOV-CAP-001 | — | 真源 |
| 容量升级D-GAP-01~12设计方案 | MOD-GOV-CAP-001 | — | 真源 |
| G-CT-* 契约（非 CT-*） | MOD-GOVERNANCE | MOD-MASTER-002 仅引用 | 真源 |

### §0.5 代码目录唯一性

| 代码类型 | 主目录 | 已知副本/重叠 | 唯一性判定 |
|---------|--------|-------------|:---:|
| 治理脚本 | `scripts/governance/` | 无 | ✅ 唯一 |
| 治理模块 | `src/zephyr/governance/` | 无 | ✅ 唯一 |
| 审计模块 | `src/zephyr/audit-trail/` | 无 | ✅ 唯一 |
| 共享组件 | `src/zephyr/shared/` | 无 | ✅ 唯一 |
| 并发基础设施 | `scripts/governance/_concurrency.py` | 无 | ✅ 唯一 |
| 运行时 | `src/zephyr/runtime/` | 无 | ✅ 唯一 |

---

## 审计结论（v0.2.0 + v0.3.0 + v0.3.1 合并）

| D-GAP | 描述 | 优先级 | 状态 | 对应章节 |
|-------|------|:-----:|:----:|---------|
| D-GAP-01 | 容量 SLO（7 条） | P0 | → MOD-GOV-CAP-001 §1.3 | §0 |
| D-GAP-02 | 脚本生命周期治理 | P0 | → MOD-GOV-CAP-001 §1.3 | §3.9, G-CT-013 |
| D-GAP-03 | Module→Script 精准映射 | P0 | → MOD-GOV-CAP-001 §1.3 | G-CT-009 |
| D-GAP-04 | 分层执行模型 | P0 | → MOD-GOV-CAP-001 §1.3 | §3.10 |
| D-GAP-05 | 熔断器策略 | P0 | → MOD-GOV-CAP-001 §1.3 | §3.11 |
| D-GAP-06 | 分片存储架构 | P0 | → MOD-GOV-CAP-001 §1.3 | §3.12 |
| D-GAP-07 | 多 AI 协调模型 | P0 | → MOD-GOV-CAP-001 §1.3 | G-CT-010 |
| D-GAP-08 | GPU 加速策略 | P1 | → MOD-GOV-CAP-001 §1.3 | §3.13 |
| D-GAP-09 | 可观测性架构 | P1 | → MOD-GOV-CAP-001 §1.3 | §3.14 |
| D-GAP-10 | 维度模型扩展 | P1 | → MOD-GOV-CAP-001 §1.3 | §3.15 |
| D-GAP-11 | 业务模块治理适配 | P1 | → MOD-GOV-CAP-001 §1.3 | G-CT-011 |
| D-GAP-12 | Finding 冲突仲裁 | P1 | → MOD-GOV-CAP-001 §1.3 | G-CT-012 |
| D-GAP-13 | Finding 存储容量爆炸保留策略 | P0 | 已设计 | G-CT-015 |
| D-GAP-14 | 硬件资源预算量化 | P0 | 已设计 | G-CT-016 |
| D-GAP-15 | 传递依赖变更影响面分析 | P0 | 已设计 | G-CT-017 |
| D-GAP-16 | Phase Gate 并发缓存策略 | P1 | 已设计 | §3.14 |
| D-GAP-17 | 脚本注册表冷启动性能预算 | P1 | 已设计 | §3.9 |
| D-GAP-18 | Backpressure 信号协议 | P1 | 已设计 | — |
| D-GAP-19 | 跨 Agent 增量扫描请求去重 | P1 | 已设计 | — |
| D-GAP-20 | 治理系统自身故障恢复 SLA | P1 | 已设计 | — |
| D-GAP-21 | 增量扫描的脚本间依赖排序 | P0 | 已设计 | G-CT-018 |
| D-GAP-22 | 治理脚本的进程级沙箱隔离 | P0 | 已设计 | G-CT-019 |
| D-GAP-23 | 全量扫描的分片感知调度 | P1 | 已设计 | — |
| D-GAP-24 | 治理系统的热升级与零停机策略 | P1 | 已设计 | — |
| D-GAP-25 | 长时间运行的内存碎片化防护 | P1 | 已设计 | — |
| D-GAP-26 | 治理结果的异步推送/订阅机制 | P1 | 已设计 | — |
| D-GAP-27 | Manifest 注册表的热重载与增量更新 | P1 | 已设计 | — |
| D-GAP-28 | 治理策略的灰度发布与回滚 | P2 | 已设计 | G-CT-020 |
| D-GAP-29 | 跨模块治理的因果冲突检测 | P2 | 已设计 | — |
| ALIGN-01 | POOL_CONFIGS worker 数对齐 | P0 | 已实现 | C.2 |
| ALIGN-02 | S0 超时值对齐蓝图 | P0 | 已实现 | C.2 |
| ALIGN-03 | 维度总超时对齐 | P0 | 已实现 | C.2 |
| ALIGN-04 | 分片数 4→16 | P0 | 已实现 | C.2 |
| ALIGN-05 | ShardRouter SHA256 路由 | P0 | 已实现 | C.2 |
| ALIGN-06 | run_all.py 接入 BulkheadExecutorV2 | P0 | 已实现 | C.2 |
| ALIGN-07 | L0 ProcessLock 降级 | P0 | 已实现 | C.2 |
| ALIGN-08 | 维度→tier 映射调整 | P1 | 已实现 | C.2 |

---

## 设计方案（D-GAP-13 ~ D-GAP-29）


### B.1 D-GAP-13: Finding 存储容量规划与保留策略

> 10,000 脚本 × 3 条 Finding/次 × 100 AI × 10 次/天 = 30,000,000 条 Finding/天（峰值）。每条 ~500B → 峰值 15GB/天。

```
Finding 保留策略（分级 TTL）：
┌────────────┬───────────┬──────────────────────────────┐
│ 严重级      │ TTL       │ 处理方式                      │
├────────────┼───────────┼──────────────────────────────┤
│ CRITICAL   │ 永久      │ 保留完整记录 + 证据文件        │
│ HIGH       │ 90 天     │ 90 天后压缩归档到 cold/ 目录  │
│ MEDIUM     │ 30 天     │ 30 天后聚合为日统计（丢弃原文）│
│ LOW        │ 7 天      │ 7 天后仅保留计数              │
│ DUPLICATE  │ 即时      │ 仲裁合并后原始记录立即丢弃     │
└────────────┴───────────┴──────────────────────────────┘

自动清理策略：
  - cleanup_findings.py 每日运行（cold layer 定时任务）
  - 清理前必须确认 Finding 已关联到 TaskCard（如有）
  - 清理后写入 audit_cleanup_log（保留 12 个月）
  - 预估稳态存储：~5GB/月（含 CRITICAL + HIGH + 聚合统计）

Finding 去重优化（减少写入量）：
  - 同 (file_path, check_name, line_range) 的 Finding → 自动合并为 recurring
  - recurring Finding 不重复写入完整 JSON，仅更新 last_seen 时间戳
  - 预估去重率 60-80% → 实际写入量降低到峰值的 20-40%
```

#### G-CT-015: Finding 存储生命周期契约（新增）

```
方向：Finding 写入路径 → 分片 SQLite → cleanup_findings.py → cold 归档
触发时机：每次 Finding 写入时检查 TTL；每日定时清理
契约定义：
  1. Finding 写入时 MUST 携带 severity（CRITICAL/HIGH/MEDIUM/LOW）和 evidence_hash
  2. 同键 Finding（file+check+line）自动合并，不重复存储
  3. cleanup_findings.py 每日运行，按 TTL 表逐级清理
  4. 清理动作 MUST 写入 audit_cleanup_log（不可变）
  5. 分片 Finding 总数 > 1,000,000 时触发 WARN 告警
  6. 分片 DB 大小超过 50GB 时触发 P0 告警 + 紧急清理

验收标准：
  - 10,000 脚本 × 100 AI 持续运行 24h → Finding 磁盘增长 < 5GB
  - 7 天后 MEDIUM/LOW Finding 自动清理
  - 清理后 CRITICAL/HIGH Finding 完整保留
```

---

### B.2 D-GAP-14: 硬件资源预算量化

> 蓝图说 40 worker，但 i7-12700KF 只有 12 核 20 线程。需量化 CPU/内存/磁盘预算。

```
═══════════════════════════════════════════════════════════════
 硬件资源配置预算（i7-12700KF + 64GB RAM + 1TB NVMe + RTX 3090 24GB）
═══════════════════════════════════════════════════════════════

CPU 预算：
  物理核: 12 (8P + 4E)  |  逻辑线程: 20
  治理系统总 worker: 40 (quick=12, content=8, ai=16, disruptive=4)
  超配比: 40/20 = 2:1 per thread, 40/12 = 3.3:1 per physical core
  合理性: Python 治理脚本以 I/O 为主（读文件/SQLite/子进程），
          CPU 密集仅 D12(embedding)/D5(AST解析)，2:1 超配合理。
  限制: 任一池的 CPU-bound worker 不应超过物理核数。
        ai_generated(16) 中 CPU-bound 脚本（BGE-M3 embedding）
        受 AdmissionController 令牌桶限流（≤ 12 并发 CPU-bound）。

内存预算（64GB 总量）：
  ┌─────────────────────────────────────────────────────┐
  │ OS + 后台服务 (VSCode/Git/Chrome):      ~8 GB       │
  │ 治理 Python 进程 (40 workers):          ~4 GB       │
  │   - 每 worker 基线 50MB RSS × 40        ~2 GB       │
  │   - SQLite WAL 缓冲区 (16 shards):     ~500 MB      │
  │   - AST 解析临时内存 (D5/D10):          ~1 GB       │
  │   - 大文件读取缓冲区:                   ~500 MB      │
  │ ScanCache LRU (5000 entries):           ~500 MB      │
  │ Script Manifest Registry (10K entries): ~200 MB      │
  │ FAISS 索引 (16 shards, RAM):           ~1.2 GB      │
  │ BGE-M3 ONNX 模型 (CPU fallback):       ~2.5 GB      │
  │ GPU 显存 (独立 VRAM, 不计入 RAM):      (7.7 GB)     │
  │ ─────────────────────────────────────────────────    │
  │ AI Agent 自身 (100 session 并发):      ~20 GB       │
  │   - 100 AI Session 各有独立上下文      估 200MB/个   │
  │ 峰值占用:                               ~36.4 GB     │
  │ 剩余余量:                               ~27.6 GB     │
  │                                                    │
  │ 结论: 64GB 充足。峰值 36.4GB + 27.6GB 余量。       │
  │ 风险: AI Agent 上下文膨胀 (> 500MB/个) → 需监控。   │
  └─────────────────────────────────────────────────────┘

磁盘 I/O 预算（NVMe 1TB, ~3500MB/s read, ~3000MB/s write）：
  ┌─────────────────────────────────────────────────────┐
  │ 100 AI 增量扫描峰值 I/O (同时触发):                  │
  │   每次增量: 15-30 脚本, 读 ~200 文件, 写 ~50 Finding │
  │   100 次并发: 读 20,000 文件, 写 5,000 Finding       │
  │   读带宽: 20,000 × 50KB 平均文件 = 1GB → ~0.3s       │
  │   写带宽: 5,000 × 500B = 2.5MB → ~0.001s             │
  │   → NVMe 完全不是瓶颈                                │
  │                                                    │
  │ 全量扫描 I/O (10,000 脚本, 40 workers):             │
  │   脚本读整个 repo (~500MB 源码):  500MB → ~0.15s     │
  │   SQLite 随机读 (16 shards):     估计 200MB → ~0.06s │
  │   写 Finding (估计 5,000-20,000): 10MB → ~0.003s    │
  │   → NVMe 在全量扫描中也远不是瓶颈                     │
  │                                                    │
  │ 真正瓶颈: SQLite WAL 写入串行化。                      │
  │   16 分片可以有效并行 WAL → 每秒可处理 ~160,000 写    │
  │   远超过 5,000 Finding/次 的需求                     │
  └─────────────────────────────────────────────────────┘

Worker 内存上限（OOM 防护）：
  每个 worker 子进程 MUST 设置 resource.setrlimit(RLIMIT_AS, 512MB)
  超出内存上限的脚本 → 被内核 OOM killer 杀死 → 标记 MEMORY_EXCEEDED
  CircuitBreaker 将其计入 failure_count
```

#### G-CT-016: 硬件资源预算契约（新增）

```
方向：治理调度层 → OS 资源限制
触发时机：每次 worker 子进程启动时
契约定义：
  1. 每个治理脚本子进程启动时 MUST 设置:
     - RLIMIT_AS = 512MB (虚拟内存上限)
     - RLIMIT_CPU = tier_timeout × 2 (CPU 时间硬上限)
  2. 治理系统自身进程内存 MUST ≤ 8GB（含所有池 + 缓存）
  3. GPU 显存监控: nvidia-smi 每秒采样 → sla_metrics.jsonl
  4. 内存压力告警:
     - 系统可用 RAM < 8GB → P1 告警 → 拒绝新 P2 扫描请求
     - 系统可用 RAM < 4GB → P0 告警 → Kill Switch 激活
  5. 磁盘压力告警:
     - 磁盘使用率 > 80% → P1 告警 → 触发 Finding 紧急清理
     - 磁盘使用率 > 95% → P0 告警 → 冻结所有扫描
```

---

### B.3 D-GAP-15: 传递依赖变更影响面分析

> G-CT-009 的 module→script 映射是直接映射——改 `src/shared/utils.py` 会传递影响 500+ 模块，但映射表看不出来。

```
传递依赖分析方案：
  实现: analyze_change_impact.py（新建）
  输入: git diff --name-only 变更文件列表
  输出: 受影响模块的完整列表（含传递依赖）

  算法:
    1. 构建全局 import 图:
       - 解析所有 Python 文件的 import 语句（AST）
       - 构建 file→module 归属映射
       - 构建 module→dependents 反向索引
       - 缓存为 dependency-graph.pkl（增量更新）

    2. 变更文件 → 直接受影响模块:
       - 变更文件在哪个模块目录下 → 直接归属
       - 变更文件被哪些模块 import → 直接依赖

    3. 传递闭包:
       - BFS 遍历反向索引
       - 最大深度 = 3 层（防止爆炸——改 utils.py 不需要扫到底）
       - 深度 1: 直接 import utils.py 的模块
       - 深度 2: import 了"深度1模块"的模块
       - 深度 3: import 了"深度2模块"的模块

    4. 影响分级:
       - 直接影响 (depth=1): 全量跑绑定脚本
       - 间接影响 (depth=2): 只跑 hot + warm 层脚本
       - 远距离影响 (depth≥3): 只跑 D2(dependency injection) + D1(structure)

  性能预算:
    - 依赖图构建: 首次 < 30s (1,500 模块, ~15,000 Python 文件)
    - 增量更新: < 2s (仅解析变更文件的 import)
    - 影响面查询: < 100ms (内存索引)

  集成:
    run_incremental.py 调用流程:
      git diff → analyze_change_impact.py → affected_modules 列表
      → module_script_index.yaml 反向查询 → 要跑的脚本列表
      → 按影响深度分级执行
```

#### G-CT-017: 传递依赖影响面分析契约（新增）

```
方向: git diff → analyze_change_impact.py → module_script_index.yaml → run_incremental.py
触发时机: 每次增量扫描触发时
契约定义:
  1. analyze_change_impact.py MUST 返回三级影响列表
  2. 直接影响模块: 全量执行其绑定的治理脚本（所有 tier）
  3. 间接影响模块: 仅执行 hot + warm tier 脚本
  4. 远距离影响模块: 仅执行 D1(structure) + D2(DI) 维度脚本
  5. 影响面 > 200 模块的变更 MUST 发出 WARN（可能是核心库改动）

验收标准:
  - 修改 src/shared/utils.py → 影响面分析 < 3s
  - 修改 src/risk/model.py → 仅标记 MOD-RISK-012 为直接 + 至多 5 个间接
  - 修改 docs/README.md → 零模块受影响 → 跳过扫描
```

---

### B.4 D-GAP-16: Phase Gate 并发缓存策略

> SLO-3 承诺 Phase Gate 启动延迟 < 10s。100 AI 同时启动 = 4,600 次检查，无缓存无法在 10s 内完成。

```
Phase Gate 缓存策略:
  方案: file-hash-based gate result caching

  缓存键: (gate_name, file_path, git_blob_hash)
  缓存存储: meta/gate_cache/ (pickle 文件, 按 gate 分文件)
  缓存 TTL: 文件未变更期间永久有效

  工作流:
    1. AI Session 启动 → Phase Gate 检查
    2. 对每个 gate 的每个目标文件:
       a) 计算 git hash-object(file_path) → blob_hash
       b) 查找缓存 → 命中则直接返回 (< 1ms)
       c) 未命中 → 执行原始检查 → 写入缓存

  缓存效率分析（100 AI 并发启动）:
    假设 80% 文件在 session 间未变更:
    - 第一轮 (1st AI): 4,600 次全量检查（冷启动, 全部 MISS）
    - 第二轮 (2nd AI): 3,680 次 HIT → 仅 920 次执行
    - 第三轮+: 几乎全部 HIT → P95 < 1s
    结论: 缓存预热后, 100 并发 session 启动 < 10s 完全可行

  缓存失效:
    - git commit/push → blob_hash 变更 → 对应 gate 缓存自动 MISS
    - 蓝图更新 → 全量缓存失效
    - 每日 00:00 清空缓存（防止长期腐化）

  实现: observability/gate_cache.py
```

---

### B.5 D-GAP-17: 脚本注册表冷启动性能预算

> 10,000 个脚本 manifest 加载：单线程 268 个约 3-5s，线性外推 10,000 个需要 ~150s。目标 < 10s。

```
脚本注册表性能预算:
  目标: 冷启动 < 10s（首次加载 10,000 脚本 manifest）

  方案: 分层加载 + 预编译缓存

  第一层: 预编译 manifest 缓存
    - generate_script_manifest.py 产出:
      script-manifest.yaml (SSoT, 人类可读)
      script_manifest.pkl  (pickle, 快速加载)
    - pickle 加载 10,000 条目: < 1s（纯反序列化）

  第二层: 延迟验证
    - 启动时不验证 schema
    - 首次使用某脚本时才验证（lazy validation）
    - 日常增量只用到 15-30 个脚本 → 延迟验证极轻

  第三层: 反向索引持久化
    - module_script_index.pkl 预编译
    - 启动时直接读 pickle → < 500ms

  性能预算:
    冷启动总耗时: pickle 加载 (1s) + 延迟验证 (0s 启动时)
    内存占用: 10,000 个 manifest dict → ~200MB (含 AST 缓存)
    索引查询: 内存 dict lookup → < 1μs

  实现: _concurrency.py ScriptRegistry 类 (新建)
```

---

### B.6 D-GAP-18: Backpressure 信号协议

> AdmissionController 拒绝请求后 AI Agent 不知道是被限流还是系统挂了。

```
Backpressure 信号协议:
  GovernanceServer MCP 返回结构化的 AdmissionResponse:

  {
    "admitted": true | false,
    "request_id": "uuid",
    "status": "admitted" | "queued" | "rejected" | "degraded",
    "position": 5,           // 排队位置 (仅 queued 时)
    "estimated_wait_s": 15,  // 预估等待时间 (仅 queued 时)
    "retry_after_s": 30,     // 建议重试等待 (仅 rejected 时)
    "degraded_tier": "warm", // 降级到哪一层 (仅 degraded 时)
    "reason": "P2 priority throttled, 8 requests ahead"
  }

  AI Agent 侧处理:
    admitted → 正常执行
    queued  → 显示排队位置, 轮询或等回调
    rejected → 30s 后自动重试, 最多 3 次
    degraded → 接受降级结果

  优先级队列可见性:
    GET /governance/queue-status → {
      "p0_queue": 0, "p1_queue": 3, "p2_queue": 12,
      "active_scans": 24, "available_slots": 16
    }
```

---

### B.7 D-GAP-19: 跨 Agent 增量扫描请求去重

> 10 个不同 AI Agent 同时改同一文件，G-CT-010 的同 Agent debounce 无法去重。

```
跨 Agent 增量扫描去重方案:
  实现: ScanDeduplicator（_concurrency.py 新增类）

  去重键: (changed_files_hash, tier)
  去重窗口: 5s（跨 Agent, 比同 Agent debounce 2s 更长）

  工作流:
    1. Agent-A 触发增量 (文件 a.py, b.py)
       → 查去重表 → 未命中 → 注册 "running" → 开始扫描
    2. Agent-B 触发增量 (文件 a.py, b.py) ← 完全相同
       → 查去重表 → "running" (Agent-A 正在跑)
       → 订阅结果, 等待广播
    3. Agent-A 扫描完成 → 结果广播给 Agent-B、C、D...
    4. Agent-C 触发增量 (文件 a.py, c.py) ← 不同组合
       → 查去重表 → 未命中 → 注册新条目 → 开始新扫描

  去重效果:
    10 Agent 改同一文件 → 1 次扫描, 结果广播给 10 Agent
    Finding 写入: 1 份 → G-CT-012 仲裁 → 1 份关联 10 session

  实现: _concurrency.py ScanDeduplicator 类
```

---

### B.8 D-GAP-20: 治理系统自身故障恢复 SLA

> 治理系统 crash 后 100 个正在运行的 AI Agent 怎么办？

```
治理系统自恢复 SLA:
  目标: 治理系统 crash → 30s 内自动恢复 → AI Agent 零感知

  故障分级:
  ┌──────────────┬──────────────────────┬──────────────────────┐
  │ 故障类型      │ 恢复策略              │ AI Agent 感知         │
  ├──────────────┼──────────────────────┼──────────────────────┤
  │ 单 worker 崩溃│ 池内自动重试 (≤3次)    │ 透明 (< 30s 延迟)    │
  ├──────────────┼──────────────────────┼──────────────────────┤
  │ 单池崩溃      │ 脚本降级到其他池       │ degraded 信号         │
  ├──────────────┼──────────────────────┼──────────────────────┤
  │ 治理服务 crash │ watchdog 自动重启     │ 503 + Retry-After     │
  │              │ 断点恢复: checkpoint   │ 目标: < 30s           │
  ├──────────────┼──────────────────────┼──────────────────────┤
  │ 无法恢复      │ Kill Switch 激活      │ "governance_unavail"   │
  │ (> 5min)     │ AI 允许跳过治理检查    │ degraded mode         │
  └──────────────┴──────────────────────┴──────────────────────┘

  断点恢复:
    - 利用现有 ScanCheckpoint（_concurrency.py L613）
    - 每完成一个维度 → 写入 checkpoint
    - crash 后重启 → load_checkpoint → 跳过已完成维度

  Watchdog:
    - 独立进程: governance_watchdog.py
    - 每 5s ping → 无响应 → SIGTERM → 等 5s → SIGKILL → 重启
    - 重启 > 3 次/5min → 放弃 → Kill Switch 激活
```

---


---


### B.9 D-GAP-21: 增量扫描的脚本间依赖排序

> 10,000 脚本中约 15-20%（1,500-2,000 个）存在脚本间数据依赖。G-CT-009 的 module→script 映射无法处理脚本 A 依赖脚本 B 输出的场景。

```
脚本依赖拓扑方案：
  实现: build_script_dep_graph.py（新建）
  输入: 10,000 个脚本的 __manifest__ 中的 depends_on_scripts 字段
  输出: script_dependency_graph.pkl（有向无环图 DAG）

  __manifest__ 新增字段:
    depends_on_scripts:
      - script_id: "d1_structure/validate_directory_layout.py"
        reason: "需要模块结构结论才能做标准合规检查"
        required_output: "module_structure_report.json"
      - script_id: "d6_security/scan_secret_leak.py"
        reason: "需要安全漏洞清单做审计完整性校验"
        required_output: "secret_leak_findings.json"

  增量扫描依赖排序算法:
    1. 查 module→script 反向索引 → 得直接触发脚本集 S
    2. 对 S 中每个脚本 → 查 script_dependency_graph.pkl → 得传递依赖脚本集 D
    3. 合并 S ∪ D → 拓扑排序 → 按依赖顺序串行执行
    4. 无依赖关系的脚本 → 并行执行（BulkheadExecutor）

  依赖深度控制:
    - max_depth = 2（防止依赖爆炸）
    - depth=1: 直接依赖（脚本显式声明的 depends_on_scripts）
    - depth=2: 传递依赖（依赖的依赖）
    - 超出深度 → 使用上次缓存的结果（降级为 stale read）

  依赖缓存:
    - 每个脚本执行完成后 → 缓存其输出到 script_output_cache/
    - 缓存键: (script_id, git_commit_sha)
    - 增量扫描时优先查缓存 → 命中则跳过执行
    - 解决：依赖脚本 B 上次已跑过 → A 可直接读 B 的缓存输出

  性能影响:
    - 依赖图构建: 10,000 脚本 < 500ms（仅解析 depends_on_scripts 字段）
    - 拓扑排序: < 100ms（DAG 规模 ~2,000 节点）
    - 额外执行的依赖脚本: 每次增量平均 +2~5 个 → 总 17-35 脚本（仍在 15-30 范围内）
```

#### G-CT-018: 脚本间依赖排序契约（新增）

```
方向: Module→Script 索引 → 依赖图 → 拓扑排序 → 增量执行
触发时机: 每次增量扫描触发时
契约定义:
  1. 每个脚本 MUST 在 __manifest__ 中声明 depends_on_scripts（可为空列表）
  2. depends_on_scripts 必须形成 DAG（无循环），build_script_dep_graph.py 自动检测循环
  3. 增量扫描时 MUST 按拓扑排序执行依赖链
  4. 依赖脚本的缓存输出 MUST 绑定到 git_commit_sha
  5. 依赖深度 > 2 时 MUST 使用缓存结果（不传递到第 3 层）
  6. 循环依赖检测到 MUST 阻断扫描，报告给 Owner

验收标准:
  - 10,000 脚本依赖图构建 < 1s
  - 增量扫描额外触发依赖脚本 ≤ 5 个（p95）
  - 依赖脚本 80% 命中缓存（同 commit 内）
  - 循环依赖阻断率 100%
```

---

### B.10 D-GAP-22: 治理脚本的进程级沙箱隔离

> 10,000 个脚本中 ~30% 是 AI 自动生成的。§3.9.4 的 `validate_script_isolation.py` 只做静态检查，有漏报（动态 eval/exec/反射调用）。

```
三层脚本沙箱隔离方案：

  ┌─────────────────────────────────────────────────────────────┐
  │ 第一层: 静态隔离验证（已有，增强）                            │
  │ ──────────────────────────────────                          │
  │ validate_script_isolation.py:                               │
  │   - AST 级别检测: open(..., "w") / os.remove / shutil.*     │
  │   - 新增检测: subprocess.run / os.system / eval / exec      │
  │   - 新增检测: import ctypes / import win32api               │
  │   通过标准: 零文件写入调用 + 零系统调用                       │
  │   适用阶段: draft→review 门禁（G-CT-013）                    │
  ├─────────────────────────────────────────────────────────────┤
  │ 第二层: 文件系统虚拟化（新增，核心隔离）                       │
  │ ─────────────────────────────────────                       │
  │ ScriptSandbox 包装器（_concurrency.py 新增类）:              │
  │                                                             │
  │   机制: 每个脚本子进程运行在独立临时目录中                     │
  │                                                             │
  │   def run_in_sandbox(script_path, repo_root):               │
  │       sandbox_dir = tempfile.mkdtemp(prefix="gov_sandbox_") │
  │       # 1. 将脚本复制到沙箱目录                              │
  │       shutil.copy(script_path, sandbox_dir)                 │
  │       # 2. 将被检代码的只读视图挂载到沙箱                    │
  │       #    Windows: mklink /J (目录联结)                     │
  │       #    Linux:   mount --bind -o ro                      │
  │       os.symlink(repo_root, sandbox_dir + "/repo",          │
  │                  target_is_directory=True)                  │
  │       # 3. 子进程 cwd = sandbox_dir                          │
  │       #    所有写入操作离开不了 sandbox_dir                   │
  │       subprocess.run([sys.executable, script_path],         │
  │                      cwd=sandbox_dir, timeout=...)          │
  │       # 4. 执行完毕 → 检查沙箱目录                           │
  │       #    只允许生成 known_outputs（Finding JSON 等）       │
  │       #    其他新增文件 → 标记 SANDBOX_VIOLATION             │
  │       # 5. 清理沙箱目录                                     │
  │       shutil.rmtree(sandbox_dir)                            │
  │                                                             │
  │   只允许访问:                                                │
  │     - repo_root (只读，通过 symlink/junction)                │
  │     - sandbox_dir (读写，隔离)                               │
  │     - Python stdlib (系统级别，择优放行)                      │
  │                                                             │
  │   禁止:                                                      │
  │     - 写入 repo_root 下任何文件                               │
  │     - 网络访问（除显式声明的 API endpoints）                  │
  │     - 修改系统配置/环境变量                                   │
  ├─────────────────────────────────────────────────────────────┤
  │ 第三层: 资源限制强制执行（已有，D-GAP-14 §G-CT-016 增强）     │
  │ ─────────────────────────────────────────────────────       │
  │ RLIMIT_AS = 512MB（虚拟内存上限）                             │
  │ RLIMIT_CPU = tier_timeout × 2                               │
  │ RLIMIT_FSIZE = 50MB（单文件写入上限）                         │
  │ RLIMIT_NOFILE = 256（最大打开文件数）                         │
  └─────────────────────────────────────────────────────────────┘

  AI 生成脚本的特权等级:
    所有 AI 生成的脚本 MUST 以 sandbox_mode="strict" 运行
    人工编写的脚本可选 sandbox_mode="relaxed"（可直接读 repo 文件）
    仅在 strict 模式下强制文件系统虚拟化
```

#### G-CT-019: 脚本沙箱隔离契约（新增）

```
方向: 治理调度层 → ScriptSandbox → 子进程
触发时机: 每次脚本子进程启动时
契约定义:
  1. 所有 AI 生成的脚本 MUST 在 sandbox_mode="strict" 下执行
  2. strict mode: 文件系统虚拟化 + 禁止网络 + RLIMIT 强制执行
  3. 人工编写的脚本默认 sandbox_mode="relaxed"（直接读文件）
  4. SANDBOX_VIOLATION → 脚本标记为 QUARANTINED，禁止执行直到 Owner 审核
  5. 同一脚本连续 3 次 SANDBOX_VIOLATION → 自动退役（active→deprecated）

验收标准:
  - AI 生成脚本尝试写文件 → 沙箱拦截 + 文件未落盘
  - 沙箱内进程 OOM → 子进程被杀 + 沙箱目录正确清理
  - 100 个沙箱并发 → 零目录泄漏
```

---

### B.11 D-GAP-23: 全量扫描的分片感知调度

> 全量扫描 10,000 脚本时，40 worker 随机分配导致大量跨分片 SQLite 读，页面缓存频繁淘汰。

```
分片感知调度方案：

  原理: 将 worker 按分片亲和性分组，同分片的脚本尽可能在同一批 worker 上串行执行。

  调度算法 (ShardAffinityScheduler):
    1. 全量扫描启动 → 获取脚本列表 + 每个脚本的 target_modules
    2. 对每个脚本 → 查 module→shard 映射 → 脚本归属分片
    3. 按分片分组: {shard_00: [342 scripts], shard_01: [356 scripts], ...}
    4. 轮询分配: 16 分片 → 40 worker → ~2.5 worker/分片
       每 2-3 个 worker 绑定到 1 个分片
    5. 同分片脚本在绑定 worker 上串行执行 → SQLite 连接复用 → 页面缓存热命中
    6. 分片内脚本跑完后 → worker 窃取相邻分片的剩余脚本（work-stealing）

  性能提升预估:
    当前（无分片感知）: ~4h 全量（页面缓存频繁淘汰）
    分片感知后: ~1.5-2h 全量（页面缓存热命中率 > 90%）
    提升: 2-2.7×

  SQLite 连接池（按分片）:
    每个分片维护一个持久连接池（3 连接/分片 × 16 = 48 连接总池）
    worker 从池中借 → 用完归还 → 连接不关闭
    连接复用 → 避免了最昂贵的"打开 SQLite + 加载 schema"开销

  实现: _concurrency.py ShardAffinityScheduler 类（新建）
```

---

### B.12 D-GAP-24: 治理系统的热升级与零停机策略

> 100 AI 在线时治理系统升级（kill+restart）会断开全部 AI session。D-GAP-20 只定义 crash 恢复，无计划性升级流程。

```
热升级方案: Graceful Drain + New Instance Handover

  ┌──────────────────────────────────────────────────────────┐
  │ 阶段 1: Drain（排水）                                     │
  │ ────────────────                                         │
  │ 1. Owner 发出 drain 命令 → GovernanceServer MCP            │
  │ 2. AdmissionController 切换为 drain 模式:                 │
  │    - 拒绝所有新扫描请求（返回 503 + Retry-After: 60）      │
  │    - 已有排队请求正常执行                                  │
  │    - 正在执行的脚本 → 等待完成或超时（S3=1800s 最大）       │
  │ 3. 等待队列排空（最长 5min，超时后强制 kill）              │
  ├──────────────────────────────────────────────────────────┤
  │ 阶段 2: Checkpoint & Handover（断点接力）                  │
  │ ──────────────────────────────────────                   │
  │ 1. 全量写入 checkpoint:                                   │
  │    - 所有正在执行的脚本的 ScanCheckpoint → scan_checkpoints.db│
  │    - AdmittedController 队列中有哪些请求 → pending_queue.json│
  │    - CircuitBreaker 状态 → circuit_breaker_state.json    │
  │ 2. 旧实例监听端口 → 切换为 handover 模式                   │
  │ 3. 新实例启动 → 读到 pending_queue.json + checkpoints      │
  │    → 从断点继续执行                                       │
  ├──────────────────────────────────────────────────────────┤
  │ 阶段 3: AI Agent 无感切换                                 │
  │ ─────────────────────────                                │
  │ AI Agent 侧:                                              │
  │   原有请求返回 503 → 自动重试（G-CT-018 Backpressure）      │
  │   新实例就绪 15s 内 → AI Agent 重试成功 → 零感知            │
  │   如果 60s 内新实例未就绪 → AI Agent 收到 degraded 信号     │
  │   → 可选择跳过治理检查（kill switch 模式）                  │
  └──────────────────────────────────────────────────────────┘

  总停机窗口: < 15s（Drain + Handover 窗口）
  AI Agent 感知: 零（重试机制掩盖 15s 窗口）

  兼容滚动升级:
    如果新旧版本不兼容（如 ShardRouter 路由算法变更）:
    → 旧版本先 drain → 新版本冷启动（不走 checkpoint）
    → 全量重扫一次作为"新基线"
    → AI Agent 收到 degraded 信号，允许跳过本次检查
```

---

### B.13 D-GAP-25: 长时间运行的内存碎片化防护

> Python 进程 7×24 运行存在内存碎片化。64GB 总内存，静态峰值 36.4GB，碎片化后实际可用内存下降。

```
内存碎片化防护方案:

  1. 定期内存压缩（GC + malloc_trim）:
     每小时自动触发一次治理进程自检:
       - gc.collect() → 强制垃圾回收
       - ctypes.CDLL("libc.so.6").malloc_trim(0) → 归还碎片内存给 OS（Linux）
       - Windows: ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
       - 效果: 释放 15-30% 的碎片化内存

  2. Worker 子进程定期重启:
     每个 worker 子进程执行 200 个脚本后 → 自动退出 → 池新建替代 worker
     - 200 脚本 ≈ 1-2h 运行时间 → 碎片化程度可控
     - 避免长期运行的 Python 进程内存膨胀问题

  3. RSS 监控 + 主动告警:
     治理系统自身进程:
       RSS > 6GB → P2 告警 → 自动触发内存压缩
       RSS > 8GB → P1 告警 → 触发 worker 滚动重启
       RSS > 12GB → P0 告警 → Kill Switch 激活

  4. 内存压力下的降级:
     系统可用 RAM < 8GB → 拒绝新 P2 扫描
     系统可用 RAM < 4GB → 仅保留 Hot 层（D1/D2/D6 安全核心）

  实现: _concurrency.py GovernanceMemoryGuard 类（新建，避免与 MOD-INF-018 memory_guard.MemoryGuard 同名冲突）
```

---

### B.14 D-GAP-26: 治理结果的异步推送/订阅机制

> AI Agent 轮询增加延迟 + 浪费 CPU。100 AI 同时轮询 = 每秒 20 次查询。

```
治理结果推送方案: MCP Push Notification（基于现有 MCP 扩展）

  AI Agent 触发扫描后的两种结果获取模式:

  ┌───────────────────────────────────────────────────────────┐
  │ 模式 1: 同步等待（短扫描，< 30s）                           │
  │ ───────────────────────────────                           │
  │ - Agent 调用 run_incremental → 同步等待返回                  │
  │ - 内部超时 30s → 返回 PARTIAL_RESULT + continuation_token  │
  │ - 适用: Hot 层 (D1/D2/D6 密钥)，脚本少且快                  │
  ├───────────────────────────────────────────────────────────┤
  │ 模式 2: 异步推送（长扫描，> 30s）                           │
  │ ───────────────────────────────                           │
  │ - Agent 调用 run_incremental → 立即返回 request_id          │
  │ - GovernanceServer 产出结果 → 推送到 Agent WebSocket        │
  │ - 或 Agent 注册 webhook URL → GovernanceServer POST 结果   │
  │ - Agent 侧事件驱动：收到结果 → 继续工作流，无需轮询          │
  ├───────────────────────────────────────────────────────────┤
  │ 模式 3: 回调（Agent 离线时）                                │
  │ ─────────────────────────                                  │
  │ - Agent 离线前 → 注册 callback:                             │
  │   "notify_on_completion": ["session_resume", "slack_dm"]   │
  │ - 扫描完成后 → GovernanceServer 投递结果到 Agent 消息队列    │
  └───────────────────────────────────────────────────────────┘

  推送通道:
    - Agent WebSocket（首选）: 已连接时直接推送，延迟 < 100ms
    - Webhook: Agent 提供 URL，GovernanceServer POST JSON
    - 消息队列: Redis/Kafka→Agent 消费（Phase V 实施）

  结果分块:
    大 Finding 集（> 1,000 条）→ 分页推送
    每页 100 条 → Agent 确认收到后推下页
    防止单次推送撑爆 Agent 上下文窗口

  实现: src/zephyr/governance/behavioral-admission/mcp_result_push.py（新建）
```

---

### B.15 D-GAP-27: Manifest 注册表的热重载与增量更新

> 100 AI 干活时新脚本持续注册。全量重载 10K manifest 不可接受（~1-2s 窗口 + 索引不一致）。

```
Manifest 热重载方案: 增量更新 + 双缓冲

  1. 事件驱动的增量更新:
     ┌─────────────────────────────────────────────┐
     │ 新脚本注册 → validate_script_quality PASS   │
     │   → generate_script_manifest.py --incremental│
     │     → 只解析新脚本的 __manifest__             │
     │     → 追加到 script_manifest.pkl              │
     │     → 更新 module_script_index.pkl            │
     │     → 发送 MANIFEST_UPDATED 事件              │
     │       → ScriptRegistry 收到事件                │
     │         → 原子替换内存中的单个条目             │
     │   ───────────────────────────────────────    │
     │ 总计耗时: < 100ms（单脚本增量）               │
     └─────────────────────────────────────────────┘

  2. 双缓冲索引:
     ┌─────────────────────────────────────────────┐
     │ ScriptRegistry 内部维护两套索引:              │
     │   - primary_index: 当前活跃索引（reader）     │
     │   - shadow_index: 更新目标（writer）          │
     │                                              │
     │ 更新流程:                                     │
     │   1. 写入 shadow_index                        │
     │   2. 原子交换指针: primary ↔ shadow            │
     │   3. 交换耗时: < 1μs（一次指针赋值）           │
     │                                              │
     │ 效果: reader 永不阻塞，writer 无锁             │
     └─────────────────────────────────────────────┘

  3. 版本号一致性:
     每次更新 → index_version += 1
     正在执行的扫描绑定到它启动时的 index_version
     扫描完成前索引版本号未变 → 结果一致性保证

  实现: _concurrency.py ScriptRegistry 类（已有 D-GAP-17 规划）增强热重载
```

---

### B.16 D-GAP-28: 治理策略的灰度发布与回滚

> `thresholds.yaml` 全局生效——修改一个阈值影响 1,500 模块的 10,000 脚本。需要灰度发布机制。

```
治理策略灰度发布方案:

  ┌───────────────────────────────────────────────────────────┐
  │ 策略分层结构:                                              │
  │                                                           │
  │ thresholds.yaml (全局基线)                                │
  │   ├── thresholds.canary.yaml (灰度超驰)                    │
  │   │     适用范围: canary_modules (标签模块)                │
  │   │     超驰优先级: 高于全局基线                           │
  │   │     自动回滚条件: failure_rate 超过基线 2× 持续 5min  │
  │   └── thresholds.module_override/ (模块级超驰)            │
  │         适用: 单模块 (如 MOD-RISK-012)                     │
  └───────────────────────────────────────────────────────────┘

  灰度发布流程:
    1. Owner 修改 thresholds.canary.yaml
    2. 选择 canary 模块（建议 5-10 个低风险模块）
    3. 部署 → 监控 30min → 指标对比（canary vs 全局基线）
    4. 通过标准:
       - canary 组的 failure_rate ≤ 全局 × 1.5
       - canary 组的 false_positive_rate ≤ 全局 × 1.2
       - 零 P0/P1 告警触发
    5. 通过 → 合并进 thresholds.yaml（全量发布）
    6. 不通过 → 自动回滚到上一个稳定版本

  自动回滚:
    触发条件（任一满足即回滚）:
      - CircuitBreaker OPEN 次数 > 全局基线 3×
      - Error budget 燃烧速度 > 全局基线 5×
      - CRITICAL Finding 产生率 > 全局基线 2×
    回滚动作:
      - 删除 thresholds.canary.yaml
      - 恢复全局 thresholds.yaml 的上一版本
      - 清除受影响的缓存（gate_cache）
      - 通知 Owner + 记录到 audit_rollback_log

  实现: scripts/governance/observability/canary_rollout.py → [REUSE-DECISION] 直接用已有 canary_rollout_manager.py（MOD-INF-018），不新建
```

#### G-CT-020: 治理策略灰度发布契约（新增）

```
方向: Owner → thresholds.canary.yaml → canary_modules → 全量发布
触发时机: 每次治理策略变更时（阈值/超时/熔断参数修改）
契约定义:
  1. 任何治理参数变更 MUST 经过灰度阶段（5-10 个 canary 模块，30min 观察期）
  2. canary 期间的指标 MUST 与全局基线对比（SLO-1~SLO-7 + failure_rate + false_positive_rate）
  3. 不通过灰度 MUST 自动回滚到上一个稳定版本
  4. 全量发布 MUST 保留上一版本 7 天（支持手动回滚）
  5. 所有策略变更 MUST 写入 audit_policy_change_log

验收标准:
  - 阈值修改 → 灰度 30min → 自动或手动决策 → 全量
  - 灰度期间 canary 组的 false_positive 飙升 → 自动回滚 < 1min
  - 回滚后 5 个 canary 模块恢复原状
```

---

### B.17 D-GAP-29: 跨模块治理的因果冲突检测

> D-GAP-12/G-CT-012 只做 Finding 级冲突仲裁（数据冲突），不做因果冲突（治理建议相互矛盾）。

```
因果冲突检测方案:

  冲突类型:
  ┌──────────────────────┬──────────────────────────────────┐
  │ 冲突类型              │ 示例                             │
  ├──────────────────────┼──────────────────────────────────┤
  │ 资源互斥              │ A: 增加缓存（需+200MB）           │
  │                      │ B: 内存不足（需-150MB）           │
  ├──────────────────────┼──────────────────────────────────┤
  │ 架构反方向            │ A: 拆分模块（解耦）               │
  │                      │ B: 合并模块（减少调用链）          │
  ├──────────────────────┼──────────────────────────────────┤
  │ 依赖顺序冲突          │ A: 先修复 D5 架构问题             │
  │                      │ B: 先修复 D6 安全漏洞             │
  │                      │ 但修复顺序不同导致不同后果         │
  ├──────────────────────┼──────────────────────────────────┤
  │ 建议优先级冲突        │ A: 标记为 CRITICAL（D6 安全）     │
  │                      │ B: 标记为 CRITICAL（D12 AI 质量） │
  │                      │ 但资源有限只能先做一个             │
  └──────────────────────┴──────────────────────────────────┘

  检测方法:
    detect_causal_conflicts.py（新建）

    1. 资源互斥检测:
       解析每个 Finding 的 resource_impact 字段（新增 __manifest__ 声明）
       → 检查同模块内 Finding 的资源需求是否超预算
       例: A.resource_impact.memory = +200MB, B.resource_impact.memory = -150MB
       → 净 +50MB → 无冲突
       例: A.resource_impact.memory = +2GB, B.resource_impact.memory = -500MB
       → 净 +1.5GB → 超出模块内存预算(512MB) → 冲突！

    2. 架构反方向检测:
       检测同模块内 Finding 的建议方向是否互斥
       "拆分模块" vs "合并模块" → 语义分析（LLM 辅助，D12 维度）
       → 标记 contradiction

    3. 优先级冲突:
       两方都 CRITICAL → 按 SLO 影响度排序
       D6(安全) > D12(AI质量) → 推荐 D6 优先
       输出: prioritized_recommendations（而非原始 Finding）

  冲突处理:
    - 检测到因果冲突 → 合并为一条 "CONFLICT_RESOLUTION_NEEDED"
    - 包含双方原始 Finding + 冲突分析 + 推荐方案
    - 不自动做决定 → 标记 needs_human_review
    - 推送给 AI Agent 时带 conflict_flag=true + resolution_options

  实现: scripts/governance/arbitrate_findings.py（扩展，已有 G-CT-012）
```

---


---

## 施工任务

### C.1 全局施工优先级（P0-BLOCK → P2-RESILIENCE）

```
P0-BLOCK（阻塞所有其他施工，必须先做）:
  1. ALIGN-06: run_all.py 接入 BulkheadExecutorV2                    ← v0.3.0 最大阻塞项
  2. ALIGN-01: POOL_CONFIGS (12/6/4/2)→(12/8/16/4)                  ← 立即 +67% 并发
  3. ALIGN-07: L0 ProcessLock 降级                                    ← 解锁多 AI 并行
  4. ALIGN-05: ShardRouter SHA256 路由                                ← 跨进程正确性

P0-CORE（容量核心，紧随 P0-BLOCK）:
  5. ALIGN-02/03: 超时值对齐蓝图                                     ← 防止误杀脚本
  6. ALIGN-04: 分片数 4→16                                           ← 锁竞争降低 4×
  7. NEW-03(v0.3.0): 传递依赖影响面分析                                ← 增量扫描精准度
  8. NEW-05(v0.3.0): 脚本注册表快速加载                                ← 冷启动性能
  9. [NEW-v0.3.1] D-GAP-21: 脚本间依赖排序 + G-CT-018                 ← 增量扫描正确性
  10. [NEW-v0.3.1] D-GAP-22: 脚本沙箱隔离 + G-CT-019                  ← AI 生成脚本安全

P1-ENHANCE（容量增强）:
  11. NEW-01(v0.3.0): Finding 存储生命周期                              ← 防止磁盘爆满
  12. NEW-06(v0.3.0): 跨 Agent 扫描去重                                ← 减少重复扫描
  13. NEW-04(v0.3.0): Phase Gate 缓存                                  ← 100 AI session 加速
  14. NEW-02(v0.3.0): 硬件资源监控                                     ← OOM 防护
  15. [NEW-v0.3.1] D-GAP-23: 分片感知调度                              ← 全量扫描加速 2×+
  16. [NEW-v0.3.1] D-GAP-24: 热升级与零停机                            ← 100 AI 在线升级
  17. [NEW-v0.3.1] D-GAP-25: 内存碎片化防护                            ← 7×24 长期运行
  18. [NEW-v0.3.1] D-GAP-26: 治理结果异步推送                           ← AI Agent 实时感知
  19. [NEW-v0.3.1] D-GAP-27: Manifest 热重载                           ← 运行时脚本注册

P2-RESILIENCE（韧性保障）:
  20. NEW-07(v0.3.0): 治理 Watchdog + 自动恢复                         ← 故障自愈
  21. NEW-08(v0.3.0): Backpressure 信号协议                            ← AI 感知系统状态
  22. ALIGN-08: 维度→tier 映射调整                                     ← 脚本归属优化
  23. [NEW-v0.3.1] D-GAP-28: 治理策略灰度发布 + G-CT-020               ← 安全变更
  24. [NEW-v0.3.1] D-GAP-29: 因果冲突检测                               ← 矛盾治理建议
```


---

### C.2 蓝图→代码对齐任务（P0-BLOCK）


| 任务 | 文件 | 当前值 | 目标值 | 影响 | 存在性 |
|------|------|------|------|------|:-----:|
| **ALIGN-01** | `_concurrency.py` L65-94 POOL_CONFIGS | (12/6/4/2) = 24 | (12/8/16/4) = 40 | Worker 总数 +67% | 已实现 |
| **ALIGN-02** | `_concurrency.py` L132-137 TIER_TIMEOUT_SECONDS | S0=10/S1=60/S2=180/S3=120 | S0=30/S1=120/S2=600/S3=1800 | 超时值对齐蓝图 | 已实现 |
| **ALIGN-03** | `_concurrency.py` L139-143 TIER_DIMENSION_TOTAL_TIMEOUT | S0=120/S1=300/S2=600/S3=240 | S0=120/S1=600/S2=1800/S3=3600 | 维度总超时对齐 | 已实现 |
| **ALIGN-04** | `_concurrency.py` L1014 ShardRouter | shard_count=4 | shard_count=16 | 分片数对齐蓝图 | ✅ 已对齐 |
| **ALIGN-05** | `_concurrency.py` L1019 route() | hash(module_id) % N | sha256(module_id)[:8] % 16 | 跨进程一致性 | ✅ 已对齐 |
| **ALIGN-06** | `run_all.py` L55 _MAX_WORKERS | ThreadPoolExecutor(8) | 接入 BulkheadExecutorV2.dispatch_with_locks() | 四池隔离+熔断 | ✅ 已接线 |
| **ALIGN-07** | `_concurrency.py` L60 L0_LOCK_TIMEOUT | 30s 独占锁 | Config Read Lock | 解锁 100 AI 并行 | 已实现 |
| **ALIGN-08** | `_concurrency.py` L106-118 _DIMENSION_TIMEOUT_TIER | D3/D4 在 S0 | D3/D4 移入 S1 (warm 层) | 维度→tier 映射对齐 | 已实现 |


---

### C.3 代码文件清单


| 任务 | 文件 | 对应 D-GAP | 功能 | 存在性 |
|------|------|:---:|------|:-----:|
| **NEW-01** | `scripts/governance/_finding_lifecycle.py` | D-GAP-13 | Finding TTL 管理 + 自动清理 | ✅ 已实现（扩展 finding_state_machine） |
| **NEW-02** | `scripts/governance/_resource_guard.py` | D-GAP-14 | Worker 内存限制 + 资源监控 | ✅ 已实现（扩展 drift-detector.resource_guard） |
| **NEW-03** | `scripts/governance/analyze_change_impact.py` | D-GAP-15 | 传递依赖影响面分析 | ✅ 已实现（串联 llm_impact_analyzer + cascade_detector） |
| **NEW-04** | `scripts/governance/observability/gate_cache.py` | D-GAP-16 | Phase Gate 文件哈希缓存 | ✅ 已实现（新建，复用 gate_engine 接口） |
| **NEW-05** | `_concurrency.py` ScriptRegistry 类 | D-GAP-17 | 10K manifest 快速加载 | ✅ 已实现（对齐 MOD-INF-001 CAP-G01） |
| **NEW-06** | `_concurrency.py` ScanDeduplicator 类 | D-GAP-19 | 跨 Agent 扫描去重 | ✅ 已实现（扫描请求级去重，非代码去重） |
| **NEW-07** | `scripts/governance/governance_watchdog.py` | D-GAP-20 | 治理服务 watchdog + 自动恢复 | ✅ 已实现（扩展 system_telemetry.watchdog） |
| **NEW-08** | `src/zephyr/governance/` MCP 扩展 | D-GAP-18 | AdmissionResponse 结构化响应 | ✅ 已实现（桥接 admission_controller → MCP 格式） |


---

#### v0.3.1 新增代码文件


| 任务 | 文件 | 对应 D-GAP | 功能 | 存在性 |
|------|------|:---:|------|:-----:|
| **NEW-09** | `scripts/governance/build_script_dep_graph.py` | D-GAP-21 | 脚本依赖 DAG 构建 + 拓扑排序 | ✅ 已实现（扩展 generate_project_depgraph） |
| **NEW-10** | `_concurrency.py` ScriptSandbox 类 | D-GAP-22 | 脚本文件系统虚拟化沙箱 | ✅ 已实现（只读 repo + 输出白名单） |
| **NEW-11** | `_concurrency.py` ShardAffinityScheduler 类 | D-GAP-23 | 分片感知全量扫描调度 | ✅ 已实现（配合 ShardRouter 分片调度） |
| **NEW-12** | `_concurrency.py` GovernanceMemoryGuard 类 | D-GAP-25 | 内存碎片化检测 + 定期压缩 | ✅ 已实现（重命名避免与 MOD-INF-018 MemoryGuard 冲突） |
| **NEW-13** | `src/zephyr/governance/behavioral-admission/mcp_result_push.py` | D-GAP-26 | MCP 异步结果推送 | ✅ 已实现（callback/event_bus/file_watcher 三模式） |
| **NEW-14** | `scripts/governance/observability/canary_rollout.py` | D-GAP-28 | 治理策略灰度发布 + 自动回滚 | [REUSE-DECISION] 直接用已有 canary_rollout_manager.py（MOD-INF-018） |
| **NEW-15** | `scripts/governance/detect_causal_conflicts.py` | D-GAP-29 | 跨模块因果冲突检测 | ✅ 已实现（串联 conflict_detector + a2a_causal_trace） |

---

---


---

## G-CT 契约下游锚点（验收）（条件可选——下游模块蓝图可选择是否包含锚点表）

以下模块蓝图 **MUST** 在正文前部包含「MOD-GOVERNANCE 集成契约锚点」表，列出本模块作为 **G-CT-*** 的消费方或产出方：**MOD-INF-018、019、020、021、022、023、024、025**。

| module_id | 已锚定 |
|-----------|--------|
| MOD-INF-018 | 是 |
| MOD-INF-019 | 是 |
| MOD-INF-020 | 是 |
| MOD-INF-021 | 是 |
| MOD-INF-022 | 是 |
| MOD-INF-023 | 是 |
| MOD-INF-024 | 是 |
| MOD-INF-025 | 是 |

# 治理域集成蓝图 — Agent 治理八件套

> **module_id**: MOD-GOVERNANCE | **Level**: 1 (域集成蓝图) | **version**: 0.2.0
>
> 本蓝图是 ZephyrAlpha 金字塔体系中的 **Level 1 治理域集成蓝图**。
> 覆盖模块：MOD-INF-018 (RBAC) / 019 (Spec) / 020 (Audit) / 021 (Rollback) / 022 (Escalation) / 023 (Drift) / 024 (Budget) / 025 (A2A)
>
> **v0.2.0 升级主题**：容量扩展——从 51 模块 / 268 脚本 / 单 Agent 扩展到 1,500 模块 / 10,000 脚本 / 100 AI 并发。
> 新增 §0（容量 SLO + 设计升级方案）、§9（施工路线图）、§10（升级后测试矩阵）。

---

## 0. 容量升级设计与 SLO

> **已拆分至** [MOD-GOV-CAP-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/capacity-upgrade/blueprint.md) §1
> 本节内容已迁移至独立蓝图，本蓝图仅保留集成契约定义。

---


## 1. 域定位

治理域负责 ZephyrAlpha 中所有 AI Agent 的**运行时治理**——身份验证、权限执行、操作审计、异常回滚、升级委托、漂移检测、预算控制、多Agent协调。

这8个模块在功能上紧密耦合，在实现上必须按特定顺序推进。本蓝图定义它们之间的集成契约。

### 1.2 目标范围

| 范围 | 包含 | 不包含 |
|------|------|--------|
| 集成契约 | G-CT-001~022 跨模块数据流方向、字段、触发条件 | 各模块内部实现细节（见各模块蓝图） |
| 仲裁裁定 | ARB-1~9 循环依赖/权限/存储裁定 | 裁定执行代码（见各模块蓝图） |
| 容量升级 | —（已拆分至 MOD-GOV-CAP-001） | SLO/分片存储/GPU加速/施工路线图 |
| 孤儿归属 | governance/ 根目录 79 个文件归属映射 | 实际文件迁移执行 |

### 1.4 运行场景约束

| 约束 | 值 |
|------|-----|
| 并发 AI Agent | ≤100 |
| 治理脚本总量 | ≤10,000 |
| 模块总量 | ≤1,500 |
| 审计写入延迟 p99 | <100ms |
| 门禁判定延迟 | <10s |

## 2. 域内模块清单

### 2.1 职责边界

| 本蓝图负责 | 本蓝图不负责 |
|-----------|------------|
| 定义 G-CT-* 契约的方向、字段、触发条件 | 各模块内部实现（见 MOD-INF-018~025 各蓝图） |
| 仲裁循环依赖/权限/存储冲突（ARB-*） | 执行仲裁结果（各模块自行实现） |
| governance/ 根目录孤儿文件归属映射 | 实际文件迁移和目录重组 |
| 定义八件套启动/关闭顺序 | 各模块内部生命周期管理 |

| overlap_check | 声明 | 冲突处理 |
|---------------|------|---------|
| 容量升级 SLO | 已拆分至 MOD-GOV-CAP-001 | 本蓝图仅引用，不重复定义 |
| 各模块 depends_on | 各模块蓝图自行声明 | 本蓝图 G-CT 契约为元层定义，不替代模块级依赖声明 |

| module_id | 名称 | 优先级 | 施工进度 | 核心职责 |
|-----------|------|:---:|:---:|------|
| MOD-INF-018 | Agent RBAC | P0 | phase_2_complete | 七层纵深防御+六横切面运行时权限执行 |
| MOD-INF-019 | Agent Spec | P0 | phase_2_complete | 蓝图→可加载 Skill 升级引擎 |
| MOD-INF-020 | Audit Trail | P0 | phase_2_complete | 不可变审计追踪+密码学Provenance+Agent签名 |
| MOD-INF-021 | Rollback System | P1 | phase_2_complete | Git-native + SQLite Checkpoint 智能回滚 |
| MOD-INF-022 | Escalation Protocol | P1 | phase_2_complete | 规则驱动升级+自动委托+五层防御架构（引擎: v0.14.0） |
| MOD-INF-023 | Drift Detector | P1 | completed | Git-native 运行时漂移检测+自动对账 |
| MOD-INF-024 | Budget Enforcer | P2 | phase_2_complete | Token/Cost/Time 三维预算强制执行（引擎: v0.7.0） |
| MOD-INF-025 | A2A Protocol | P2 | phase_2_complete (Phase 4 Hold) | 多Agent通信协议+冲突仲裁（引擎: v0.10.0，Phase 4 激活） |

> **注意**：GOV-SUB-001~004 已合并至对应 MOD-INF 模块（018/020/021/023），不再作为独立子蓝图维护。其余四个模块（Agent Spec MOD-INF-019、Escalation MOD-INF-022、Budget MOD-INF-024、A2A MOD-INF-025）代码已在各自包目录中，无需独立子蓝图。

### 2.1 governance/ 根级孤儿文件→子模块归属映射

> 79 个 .py 文件位于 `src/zephyr/governance/` 根目录，尚未迁入对应子模块包。

| 归属模块 | 文件数 | 目标目录 | 代表性文件 |
|---------|:---:|---------|---------|
| MOD-INF-018 Agent RBAC | 9 | `src/zephyr/agent-rbac/` | defense_depth.py, kill_switch.py, anti_pattern_guard.py |
| MOD-INF-019 Agent Spec | 6 | `src/zephyr/agent-spec/` | agent_debate.py, agent_dispatch.py, vibe_coding_enforcer.py |
| MOD-INF-020 Audit Trail | 13 | `src/zephyr/audit-trail/` | provenance_tracker.py, changelog_manager.py, sbom_generator.py |
| MOD-INF-021 Rollback System | 9 | `src/zephyr/rollback/` | startup_shutdown.py, phase_manager.py, fault_tolerance.py |
| MOD-INF-022 Escalation Protocol | 10 | `src/zephyr/escalation-engine/` | incident_response.py, risk_matrix.py, spof_checker.py |
| MOD-INF-023 Drift Detector | 15 | `src/zephyr/behavioral-auditor/` | model_drift_monitor.py, architecture_contracts.py, data_quality.py |
| MOD-INF-024 Budget Enforcer | 9 | `src/zephyr/budget-enforcer/` | token_budget.py, cost_router.py, tco_model.py |
| MOD-INF-025 A2A Protocol | 8 | `src/zephyr/infra_ops/a2a_protocol/` | multi_model_consensus.py, prompt_lifecycle.py, offline_autonomy.py |

> **合计**: 79 个孤儿文件已注册归属。迁移时需同步更新 `__init__.py` 的 `__all__` 和 `governance/__init__.py` 的重导出。完整文件列表见 git history 或 `ls src/zephyr/governance/*.py`。

## 3. 域内集成契约（G-CT-*）

### G-CT-001: RBAC → Audit 集成契约

```
方向：MOD-INF-018 (RBAC) → MOD-INF-020 (Audit)
触发时机：每次权限判定完成时
数据流：
  RBAC 产出 → Audit 写入 ← Agent Identity 注入
  - agent_id: str          ← RBAC 从 Agent Identity 获取
  - permission: str        ← RBAC 权限判定结果（allow/approve/block）
  - resource: str          ← 被访问的资源
  - decision_basis: dict   ← 判定依据（角色/策略/上下文）
  - timestamp: datetime    ← 判定时间
  - session_id: str        ← 关联会话
解决循环依赖方案：RBAC 在每次权限判定完成后主动调用 Audit.write()。
  Audit 不需要反向调用 RBAC——Audit 只记录事实，不验证权限。
  调用链：Agent → RBAC.check() → RBAC 返回 result → RBAC 调用 Audit.write(result)
  这意味着 RBAC 单向依赖 Audit。Audit 不依赖 RBAC。
```

### G-CT-002: Audit → Rollback 集成契约

```
方向：MOD-INF-020 (Audit) → MOD-INF-021 (Rollback)
触发时机：Audit 检测到异常操作签名时
数据流：Audit 的 anomaly_detector 产出异常事件 → Rollback 消费
```

### G-CT-003: Rollback → Escalation 集成契约

```
方向：MOD-INF-021 (Rollback) → MOD-INF-022 (Escalation)
触发时机：回滚失败或回滚后验证不通过（Rollback auto_guard 后验失败）
数据流：Rollback 的 rollback_result 产出 → Escalation 消费（触发人工升级）
```

### G-CT-004: Escalation → RBAC 集成契约

```
方向：MOD-INF-022 (Escalation) → MOD-INF-018 (RBAC)
触发时机：升级到人工审批时需要验证审批人权限
数据流：Escalation 的 approval_request → RBAC 验证 human_approver 的代理权限
```

### G-CT-005: Drift → Rollback 集成契约

```
方向：MOD-INF-023 (Drift) → MOD-INF-021 (Rollback)
触发时机：Drift 检测到可自动修复的漂移
数据流：Drift 的 drift_event（含 fix_suggestion）→ Rollback 执行自动修复
```

### G-CT-006: Budget → Escalation 集成契约

```
方向：MOD-INF-024 (Budget) → MOD-INF-022 (Escalation)
触发时机：预算告急（Burn Rate > 阈值 或 全局预算耗尽）
数据流：Budget 的 budget_alert → Escalation 启动升级流程
```

### G-CT-007: Spec → RBAC/Audit 集成契约

```
方向：MOD-INF-019 (Agent Spec) → MOD-INF-018 (RBAC) + MOD-INF-020 (Audit)
触发时机：Skill 加载时
数据流：Spec 的 Skill.manifest 中的 permissions 声明 → RBAC 注册权限策略
       Spec 的 Skill 执行 → Audit 记录 Skill 操作审计
```

### G-CT-008: A2A → RBAC/Escalation 集成契约

```
方向：MOD-INF-025 (A2A) → MOD-INF-018 (RBAC) + MOD-INF-022 (Escalation)
激活条件：Phase 4（A2A 从 Hold 激活时）
```

### G-CT-021: MTH-006 根因分析三向触发器契约

```
方向：PS-STD-011 (MTH-006) → L0 project_rules.md + L1 onboarding_detail.md + skill-registry.yaml
触发时机：sync_rule_registry.py 每次运行时自动验证
契约定义：
  MTH-006（追问到底根源分析原则）的触发器 MUST 同时存在于三个位置：
    1. L0 project_rules.md — 产出五条中包含 "MTH-006" + "追问到底" 关键词
    2. L1 onboarding_detail.md — §八包含 "治根" + "治标" + "MTH-006" 判定标准
    3. skill-registry.yaml — task_keywords 包含 "根因" + "追问到底" + "root_cause" 路由

  验证脚本：scripts/governance/sync_rule_registry.py
  验证函数：check_mth006_triggers()
  不通过 → EXIT_FINDINGS → 禁止关闭任务

  解决问题：压缩 L0 时误删方法论触发器 → 新 AI 进项目不知道追问到底工作方式
  SSoT：docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml MTH-006
```

### G-CT-022: AgentCard ↔ CapabilityRegistry 集成契约

```
方向：MOD-INF-019 (Agent Spec) → MOD-INF-035 (AutoRuntime Core)
触发时机：AgentCard 注册/更新时同步 CapabilityRegistry
契约定义：
  AgentCard（MOD-INF-019）与 CapabilityRegistry（MOD-INF-035）MUST 双向同步：
    1. AgentCard 注册/更新 → CapabilityRegistry.register() 自动调用
    2. CapabilityRegistry.find_by_tags() → 返回结果 MUST 包含 AgentCard 元数据
    3. AgentCard 退役 → CapabilityRegistry 自动注销对应能力

  验证方式：python -m zephyr.agent_spec list → 确认 registry 与 cards 一致
  不通过 → Agent 能力发现断裂 → 孤儿 Skill

  SSoT：src/zephyr/agent-spec/skill-registry.yaml
  ARB 裁决：ARB-14 线6运维保障线
```

### 3.9 脚本生命周期治理（v0.2.0 新增）

> **对应缺陷**：D-GAP-02 | **关联契约**：G-CT-013
>
> 10,000 脚本不是一次性写完的——它们会持续生长、腐化、被替换。
> 没有生命周期管理的脚本存量是不可维护的。本节定义治理脚本自身的治理规则。

#### 3.9.1 生命周期状态机

```
                    ┌──────────┐
          创建 ───→ │  draft   │
                    └────┬─────┘
                         │ validate_script_quality.py 全部通过
                         ▼
                    ┌──────────┐
                    │  review  │
                    └────┬─────┘
                         │ test_all_scripts.py 冒烟 + Owner 审批
                         ▼
                    ┌──────────┐
         superseded ┌┤ active  │◄── 持续产生 Finding
         _by 非空   │└────┬─────┘
         ┌──────────┘    │ 连续 30 天零 Finding（腐化检测）
         ▼               ▼
    ┌──────────┐    ┌──────────┐
    │deprecated│    │ degraded │  ← 非阻塞降级：仍可运行，但权重降为 0.5
    └────┬─────┘    └──────────┘
         │ 30 天冷却期 + 无活跃引用
         ▼
    ┌──────────┐
    │ retired  │
    └────┬─────┘
         │ migrate_to_archive.py
         ▼
    ┌──────────┐
    │ archived │  ← 移出活跃注册表，仅保留历史审计
    └──────────┘
```

#### 3.9.2 状态转换条件（准入/准出门禁）

| 转换 | 准入条件 | 自动化检查 | 人工审批 |
|------|------|:---:|:---:|
| draft → review | `__manifest__` 完整 + `validate_script_quality.py` D-D-01~08 全通过 | ✅ 自动 | ❌ |
| review → active | `test_all_scripts.py` 冒烟通过 + `score_script_effectiveness.py` 初始评分 ≥ 40 | ✅ 自动 | ✅ Owner |
| active → degraded | `detect_script_rot.py` 标记：连续 30 天零 Finding | ✅ 自动 | ❌ |
| degraded → active | 最近 7 天内产出 ≥ 1 个有效 Finding | ✅ 自动 | ❌ |
| active → deprecated | `superseded_by` 指向有效替代脚本 + `depends_on` 全部迁移完毕 | ✅ 自动 | ✅ Owner |
| deprecated → retired | 30 天冷却期 + 零活跃引用（脚本注册表中无其他脚本引用它） | ✅ 自动 | ❌ |
| retired → archived | 手动执行 `migrate_to_archive.py` | ❌ | ✅ Owner |

#### 3.9.3 版本化规则

```
治理脚本版本号遵循 SemVer 变体：MAJOR.MINOR.PATCH-EFFECTIVENESS

  MAJOR:  检测逻辑根本改变（如从正则匹配改为 AST 解析）
  MINOR:  新增检测规则或阈值调整
  PATCH:  修复误报/漏报，不改检测逻辑
  EFFECTIVENESS: 自动计算的有效性评分（0-100），由 score_script_effectiveness.py 更新

示例：
  scan_secret_leak.py v3.2.1-87  ← 第3代检测逻辑，87分高有效性
  check_agent_identity.py v2.1.0-15 ← 版本新但效果差，疑似误报率高
```

#### 3.9.4 自动化健康检查（每轮 scan 后触发）

| 检查脚本 | 功能 | 触发条件 | 输出 |
|------|------|------|------|
| `detect_script_rot.py` | 检测静默失效脚本（连续 N 天零 Finding） | 每次 scan 后 | 标记状态 `active→degraded` |
| `detect_stale_version.py` | 检测版本长期未更新 + 无 commit 活动 | 每周 | 告警列表（不自动降级） |
| `score_script_effectiveness.py` | 计算有效性评分 = Finding密度 × (1-误报率) × (1-去重率) | 每次 scan 后 | 更新 `__manifest__` EFFECTIVENESS 字段 |
| `validate_script_isolation.py` | 验证脚本无副作用（不修改被检代码） | 脚本 review 时 | PASS/FAIL |
| `generate_script_impact_report.py` | 生成脚本影响力报告（Finding 数量/唯一模块覆盖数/误报率趋势） | 每月 | Markdown 报告 |

#### 3.9.5 10,000 脚本规模的退役预算

```
假设稳态下脚本腐化率 = 2% / 月（合理估计值）

  每月退役脚本数 = 10,000 × 2% = 200 个
  每月新增脚本数 ≈ 退役数 + 净增长 ≈ 200 + 50 = 250 个

  退役流程耗时：
    - degrade 标记：全自动，零耗时
    - deprecated→retired：30 天冷却期（自动计时）
    - retired→archived：手动触发，批量操作

  关键指标：
    - 活跃脚本占比 > 90%（目标: active + degraded / total > 90%）
    - deprecated 到 retired 的自动流转率 > 95%
    - archived 脚本审计日志保留 12 个月
```

---

### 3.10~3.13 容量升级设计（已拆分）

> §3.10 分层执行模型 / §3.11 熔断器策略 / §3.12 分片存储架构 / §3.13 GPU 加速策略
> **全部已拆分至** [MOD-GOV-CAP-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/capacity-upgrade/blueprint.md) §2~5

---


### 3.14 可观测性架构（Observability）（v0.2.0 新增）

> **对应缺陷**：D-GAP-09 | **现有基础设施**：[`sla_metrics.jsonl`](file:///d:/ZephyrAlpha/scripts/governance/_shared/sla_metrics.jsonl) + `compute_sla_metrics.py`
>
> 指标已在采集，但缺失告警规则、Dashboard 和 error budget 仪表盘。本节补全。

#### 3.14.1 三层可观测性体系

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Metrics（指标）                            │
│  ─────────────────                                  │
│  采集: sla_metrics.jsonl (每行一条事件)              │
│  格式: {"ts":"ISO8601","metric":"...","value":...,  │
│         "labels":{"pool":"quick","dimension":"D1"}} │
│  聚合: compute_sla_metrics.py (每 5min 一次)         │
│  输出: metrics/governance_metrics_prom.txt           │
│        (Prometheus text format, 供 Grafana 消费)    │
│  保留: raw jsonl 保留 30 天, 聚合后 90 天            │
├─────────────────────────────────────────────────────┤
│  Layer 2: Logs（日志）                               │
│  ────────────────                                   │
│  结构化 JSON 日志 → data/logs/governance/            │
│  按日期分文件: governance_2026-05-10.jsonl           │
│  日志级别: DEBUG/INFO/WARN/ERROR/CRITICAL            │
│  每条日志必含: ts, session_id, agent_id,             │
│               module_id (如有), dimension (如有)      │
│  保留: 90 天，压缩后 365 天                          │
├─────────────────────────────────────────────────────┤
│  Layer 3: Traces（追踪）——Phase V 实施               │
│  ─────────────────────                              │
│  每次 scan 生成 trace_id                             │
│  span: scan_begin → dimension_run → script_exec →   │
│        finding_write → audit_write → scan_end        │
│  存储: data/traces/ 下 JSONL                         │
│  关联: trace_id 关联 metrics + logs                  │
└─────────────────────────────────────────────────────┘
```

#### 3.14.2 关键指标定义（对等 SLO-1~SLO-7）

| 指标名 | 类型 | 采集方式 | 聚合周期 |
|------|:---:|------|:---:|
| `gov_scan_latency_seconds` | Histogram | 每个脚本执行完即写入 | p50/p95/p99, 5min 窗口 |
| `gov_scan_throughput_scripts_per_min` | Gauge | BulkheadExecutor pool stats | 瞬时值, 每秒采样 |
| `gov_phase_gate_startup_seconds` | Histogram | session_startup_check 结束即写入 | p95, 每次 session |
| `gov_audit_write_latency_ms` | Histogram | 每次 Audit.write() 即写入 | p99, 1min 窗口 |
| `gov_circuit_breaker_state` | Gauge | 状态变化时写入 (0=CLOSED, 1=OPEN, 2=HALF_OPEN) | 事件驱动 |
| `gov_error_budget_remaining_seconds` | Gauge | manage_error_budget.py 每分钟更新 | 实时 |
| `gov_pool_queue_depth` | Gauge | BulkheadExecutor 内部队列长度 | 瞬时值, 每秒采样 |
| `gov_script_failure_rate` | Gauge | 失败脚本数/总执行数, 5min 窗口 | 5min 滚动 |
| `gov_gpu_utilization_percent` | Gauge | nvidia-smi 采样 | 每秒 |

#### 3.14.3 告警规则

```
┌──────────────────────────────────────────────────────────────────────┐
│ 告警规则（由 observability/manage_alert_rules.py 生成 Prometheus     │
│          rules YAML + Grafana alert JSON）                           │
├──────────┬────────────────────────┬────────┬────────────────────────┤
│ 规则 ID   │ 条件                   │ 严重度  │ 动作                   │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-01 │ gov_scan_latency p95    │ P1     │ 通知 Owner +           │
│          │ > 60s, 持续 5min        │        │ escalate_to_human.py   │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-02 │ gov_circuit_breaker     │ P0     │ 通知 Owner +           │
│          │ state=1, 任意池         │        │ 自动降级执行            │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-03 │ gov_error_budget        │ P0     │ 仅保留 Hot 层 +         │
│          │ remaining < 50%         │        │ 通知 Owner              │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-04 │ gov_error_budget        │ P0     │ 全系统扫描冻结 +        │
│          │ remaining = 0           │        │ Kill Switch 激活        │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-05 │ gov_pool_queue_depth    │ P1     │ 自动降级 Warm→Cold      │
│          │ > 200, 任意池           │        │ (见 §3.10.2)            │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-06 │ gov_gpu_utilization     │ P2     │ 日志 WARN:              │
│          │ = 0 AND CUDA available  │        │ "GPU idle when expected" │
├──────────┼────────────────────────┼────────┼────────────────────────┤
│ ALERT-07 │ gov_script_failure_rate │ P1     │ 通知 Owner +            │
│          │ > 5%, 持续 10min        │        │ 自动重试失败脚本        │
└──────────┴────────────────────────┴────────┴────────────────────────┘
```

#### 3.14.4 Dashboard 设计

```
治理域全局 Dashboard (Grafana, SQLite 数据源 + Prometheus-format metrics)

┌─ Row 1: SLO 状态 ────────────────────────────────────────────────┐
│ SLO-1 Gauge (p95 latency)   SLO-2 Gauge (throughput)             │
│ SLO-4 Gauge (audit latency) SLO-6 Gauge (availability %)         │
│ ─────────────────────────────────────────────────                 │
│ Error Budget 燃烧速度: 线图 (剩余秒数 × 时间)                      │
└──────────────────────────────────────────────────────────────────┘
┌─ Row 2: 执行引擎 ────────────────────────────────────────────────┐
│ 四池 Worker 利用率: 4 × Gauge (0-100%)                           │
│ 四池排队深度: 4 × 时序线图                                        │
│ CircuitBreaker 状态: 4 × 状态指示 (绿/黄/红)                       │
│ ─────────────────────────────────────────────────                 │
│ 脚本成功率: 时序线图 (success/total per 5min)                      │
│ 平均执行时间: 时序线图 (按 tier 分层)                              │
└──────────────────────────────────────────────────────────────────┘
┌─ Row 3: 查找与审计 ──────────────────────────────────────────────┐
│ Finding 总数: 计数卡 (按 severity 分色)                            │
│ Finding 趋势: 堆叠柱状图 (按维度 D1-D14 分组, 日聚合)              │
│ ─────────────────────────────────────────────────                 │
│ 最近 20 条 Critical Finding: 表格                                │
└──────────────────────────────────────────────────────────────────┘
┌─ Row 4: 硬件资源 ────────────────────────────────────────────────┐
│ CPU 利用率, RAM 使用量, GPU 利用率 + VRAM 使用量                   │
│ 磁盘 I/O (NVMe read/write MB/s)                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### 3.15 维度模型扩展（D13 / D14 + D10 补全）（v0.2.0 新增）

> **对应缺陷**：D-GAP-10
>
> 12 维度模型中 D10（性能治理）为 0 脚本，扩容后需新增 D13（容量治理）和 D14（依赖健康）。

#### 3.15.1 扩展后的完整维度表（14 个维度）

| 维度 | 名称 | 当前脚本 | 10K 预估脚本 | Tier | 职责 |
|:---:|------|:---:|:---:|:---:|------|
| D1 | 结构治理 | 22 | ~400 | hot | 目录结构/命名/模板对齐 |
| D2 | 依赖注入 | 18 | ~350 | hot | import 合法性/循环依赖/依赖图校验 |
| D3 | 标准合规 | 25 | ~450 | warm | PS-STD 系列标准逐条检查 |
| D4 | 编码规范 | 35 | ~600 | warm | AST 级别编码质量+反模式检测 |
| D5 | 架构治理 | 45 | ~800 | warm | 分层约束/横切面完整性/蓝图一致性 |
| D6 | 安全治理 | 33 | ~1,200 | hot* | 密钥泄露/注入/CVE/权限越界<br>*仅 SECRET_LEAK 类为 hot，其余 warm |
| D7 | 数据治理 | 22 | ~500 | cold | schema/数据流/数据主权/PII 检测 |
| D8 | 契约治理 | 24 | ~450 | warm | API 契约兼容性/G-CT 契约验证 |
| D9 | 审计合规 | 18 | ~350 | cold | 审计完整性/Provenance 链/签名验证 |
| **D10** | **性能治理** | **0→8** | **~200** | **cold** | **执行耗时剖析/内存泄漏/热点路径/复杂度门禁** |
| D11 | 配置治理 | 20 | ~400 | warm | 配置漂移/环境差异/密钥重定向 |
| D12 | AI 生成质量 | 12 | ~800 | cold | AI 幻觉/代码重复度/提示注入/事实一致性 |
| **D13** | **容量治理** | **新增: 5** | **~200** | **cold** | **SLO 达标率/error budget/分片健康/队列深度/worker 利用率** |
| **D14** | **依赖健康** | **新增: 5** | **~200** | **frozen** | **外部依赖版本/漏洞/license/可用性/供应链风险** |
| — | 元治理 | 6 | ~100 | — | 脚本自检/注册表一致性/manifest 验证 |

> **总计**：当前 268；D10 补全 +8；D13 新增 +5；D14 新增 +5；自然增长覆盖到 10,000。
>
> D10/D13/D14 的 10K 预估脚本数包含 AI 自动生成的专项检测脚本。

#### 3.15.2 D10: 性能治理（补全设计）

```
当前状态: 0 脚本
目标: 8 个初始脚本, 10K 规模下 ~200 个

初始脚本清单:
  d10_performance/analyze_execution_hotspots.py  ← 识别治理脚本自身的热点路径
  d10_performance/detect_memory_leak.py          ← 检测 long-running 脚本内存泄漏
  d10_performance/score_complexity.py            ← AST 圈复杂度门禁
  d10_performance/profile_subprocess_overhead.py ← subprocess 启动开销分析
  d10_performance/benchmark_incremental_scan.py  ← 增量扫描耗时基准测试
  d10_performance/detect_n_plus_1_query.py       ← ORM/SQLite N+1 查询检测
  d10_performance/analyze_gpu_utilization.py     ← GPU 利用率监控（配合 §3.13）
  d10_performance/score_cache_hit_rate.py        ← ScanCache/ChromaDB 缓存命中率

适用 tier: cold（每日定时）
```

#### 3.15.3 D13: 容量治理（新增维度）

```
定位: 治理域自身的 SLO 监控与容量规划
触发: 每日定时 + 每次全量扫描后

初始脚本清单:
  d13_capacity/compute_slo_attainment.py         ← SLO-1~SLO-7 达标率计算
  d13_capacity/track_error_budget_burn.py        ← Error budget 燃烧速度追踪
  d13_capacity/monitor_shard_health.py           ← 16 分片健康度（大小/延迟/模块分布）
  d13_capacity/forecast_script_growth.py         ← 基于历史增长趋势预测脚本数
  d13_capacity/recommend_scaling_action.py       ← 自动推荐扩容动作（分片×/worker+/降级）

14 维度中最特殊的一个——D13 是"治理域治理自己"的维度。
D13 发现的问题不能由 D13 自己修复（自指悖论），必须升级到 human Owner 或 MOD-INF-022 Escalation。
```

#### 3.15.4 D14: 依赖健康（新增维度）

```
定位: 外部依赖的供应链安全与可用性
触发: 每周全量扫描 + 依赖变更时

初始脚本清单:
  d14_dependency/audit_pypi_dependencies.py       ← PyPI 包版本/漏洞/许可证检查
  d14_dependency/verify_external_api_availability.py ← 外部 API 可用性 ping
  d14_dependency/detect_dependency_drift.py       ← requirements.txt vs 实际安装的漂移
  d14_dependency/score_supply_chain_risk.py       ← 供应链风险评估（维护者活跃度/CVE 历史）
  d14_dependency/audit_git_submodules.py          ← Git submodule 版本一致性

适用 tier: frozen（每周 + 依赖变更触发）
特殊性: D14 可能产生大量外部网络请求——受 TokenBucket 限流（10 req/s）
```

#### 3.15.5 维度与四层执行模型的映射

```
          D1  D2  D3  D4  D5  D6  D7  D8  D9  D10 D11 D12 D13 D14
hot       ██  ██  ──  ──  ──  ▓▓  ──  ──  ──  ──  ──  ──  ──  ──
warm      ──  ──  ██  ██  ██  ██  ──  ██  ──  ──  ██  ──  ──  ──
cold      ──  ──  ──  ──  ──  ──  ██  ──  ██  ██  ──  ██  ██  ──
frozen    ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██

██ = 该层包含此维度的全部脚本
▓▓ = 部分（D6 仅 SECRET_LEAK 类为 hot）
── = 该层不包含此维度
```

---

## 4. 域内施工顺序（v0.2.0 扩展）

**Phase 1（必须先建的基础）**：
1. MOD-INF-020 Audit Trail——审计是治理的基础设施，其他模块都需要写入审计
2. MOD-INF-018 Agent RBAC——权限执行是治理的核心门禁

**Phase 2（依赖 Phase 1）**：
3. MOD-INF-021 Rollback System——依赖 Audit 记录回滚操作
4. MOD-INF-022 Escalation Protocol——依赖 RBAC 验证升级权限 + Audit 记录升级

**Phase 3（依赖 Phase 2）**：
5. MOD-INF-023 Drift Detector——依赖 Rollback 执行自动修复
6. MOD-INF-024 Budget Enforcer——依赖 Escalation 处理预算告急

**Phase 4（后期激活）**：
7. MOD-INF-019 Agent Spec——依赖以上全部治理模块就绪
8. MOD-INF-025 A2A Protocol——多 Agent 场景，Phase 4 激活

**Phase 5（v0.2.0 新增：治理域内部工具——依赖 Phase 1/2 代码就绪后并行施工）**：
> 以下模块服务于治理域自身运维，按 §0.7 施工优先级排序执行。

9. MOD-INF-021 Shard Router——⚠️ 代码存在但未对齐：ShardRouter shard_count=4（蓝图要求16）+ hash()（蓝图要求sha256）+ ShardedGovernanceDB 未接入 run_all.py
10. MOD-INF-018 Script Lifecycle——脚本状态机 + 腐化检测 + 有效性评分 + 退役流程（优先级 P1-1）
11. MOD-INF-023 Observability Engine——告警规则 + Dashboard + Error Budget 仪表盘（优先级 P1-4）
12. MOD-INF-020 Capacity Planner——SLO 达标率 + 分片健康 + 扩容建议（优先级 P3-2，依赖 D13 维度脚本）
13. **sync_rule_registry.py MTH-006 三向触发器检查**——验证 L0+L1+Skill 三处追问到底触发器完整（G-CT-021）

**Phase 6（v0.2.0 新增：容量升级核心改造——依赖 Phase 5 部分完成）**：
> 以下改造是整个 v0.2.0 升级的核心交付物，优先级最高。

13. **✅ L0 ProcessLock 废弃**：降级为 Config Read Lock（G-CT-010 §0.7 P0-1）——已完成
14. **⚠️ run_all.py 切换 BulkheadExecutorV2**：BulkheadExecutorV2 已实现于 `_concurrency.py`，但 `run_all.py` 仍用 `ThreadPoolExecutor(max_workers=8)` 未接入——**接线未施工**
15. **增量扫描精准化**：`__manifest__` 新增 `target_modules` → `module_script_index.yaml` 反向索引（G-CT-009 §0.7 P0-3）
16. **四层执行模型上线**：hot/warm/cold/frozen tier + TieredTimeout（§3.10 §0.7 P1-3）
17. **四池熔断器策略生效**：threshold 对齐 + 告警升级链（§3.11 §0.7 P2-3）
18. **GPU 加速**：BGE-M3 ONNX→CUDA + FAISS GPU index（§3.13 §0.7 P3-1）
19. **D10/D13/D14 维度上线**：25 个新脚本 + D10 补全（§3.15 §0.7 P3-2）
20. **容量压力测试**：G-CT-014 S1-S4 全部通过（§0.7 P3-3）

## 5. 循环依赖解决裁定

**原问题**：MOD-INF-018 (RBAC) 声明依赖 MOD-INF-020 (Audit)，MOD-INF-020 (Audit) 也声明依赖 MOD-INF-018 (RBAC)——形成循环依赖。

**裁定**：
- **Audit 不依赖 RBAC**。Audit 只记录事实（谁做了什么、什么时候、什么结果）——不需要知道谁有权做。Agent Identity（agent_id）由调用方（RBAC）在调用 Audit.write() 时作为参数传入，Audit 直接使用。
- **RBAC 单向依赖 Audit**。RBAC 在权限判定完成后主动写入 Audit 记录。
- **打破循环的具体方案**：修改 MOD-INF-020 Audit Trail 蓝图的 depends_on，移除对 MOD-INF-018 的依赖。

### §5.5 自动化触发机制

| 组件 | 触发方式 | 触发时机 | 注册位置 | 自动化成熟度 |
|------|---------|---------|---------|:---:|
| merkle_hourly_aggregate | CircadianScheduler cron | 每日 00:00 | lifecycle_manager.py | 90% |
| audit_log_rotation | CircadianScheduler cron | 每日 01:00 | lifecycle_manager.py | 90% |
| audit_retention_dry_run | CircadianScheduler cron | 每日 02:00 | lifecycle_manager.py | 90% |
| audit_tiered_storage_migrate | CircadianScheduler cron | 每日 03:00 | lifecycle_manager.py | 90% |
| finding_lifecycle_cleanup | CircadianScheduler cron | 每日 04:00 | lifecycle_manager.py | 90% |
| gate_cache_daily_invalidate | CircadianScheduler cron | 每日 00:00 | lifecycle_manager.py | 90% |
| governance_watchdog | Boot sequence step 09a | Boot 时启动 | lifecycle_manager.py | 85% |
| change_impact_analysis | run_incremental.py 自动串联 | 增量扫描时 | run_incremental.py | 80% |
| DriftCronScheduler | 独立 Daemon | 30min/6h | drift_cron_scheduler.py | 95% |
| BlueprintWatcher | Boot 启动 + 60s 轮询 | Boot 时 | auto_runtime_core.py | 85% |
| D1-D12 全量扫描 | 手动 `run_all.py` | 按需 | — | 10% |

## 6. 风险与缓解

### §6.2 退化矩阵

| 组件 | 不可用条件 | 退化策略 | 退化影响 | 恢复条件 |
|------|-----------|---------|---------|---------|
| BulkheadExecutorV2 | 线程池耗尽 | fallback ThreadPoolExecutor(8) | 并发降至 8 worker | 池资源释放 |
| ShardRouter | 分片 DB 锁定 | 单文件 SQLite fallback | 写入竞争恢复 | 锁释放 |
| GateCache | 缓存未命中 | 重新执行 Gate 检查 | 首次启动变慢 | 缓存预热完成 |
| GovernanceWatchdog | daemon 崩溃 | CircadianScheduler 健康检查接管 | 自动重启延迟 | watchdog 重启 |
| FindingLifecycleManager | 清理任务失败 | dry_run 模式降级 | 仅报告不执行 | 手动修复后切回 |
| ChangeImpactAnalyzer | 依赖图不可用 | 维度级 fallback | 扫描范围扩大 | 依赖图重建 |
| AuditWriter | 写入失败 | 内存缓冲 + 重试 | 审计记录延迟 | 存储恢复 |
| MCP ResultPush | 推送失败 | 文件落盘 fallback | 结果延迟送达 | 网络恢复 |

| 类型 | 风险 | 影响 | 缓解 |
|------|------|------|------|
| 风险 | 八件套施工进度不统一 | agent-rbac 100%, 其余 7 模块 50%——集成契约已定义但施工未完成 | Phase 2 完成后→Phase 3 推进 |
| 风险 | RBAC/Audit 循环依赖误回 | 两个模块互相阻塞 | 本裁定永久解决——Audit 单向接收 RBAC 写入 |
| 风险 | A2A 依赖所有其他模块 | Phase 4 才可能激活 | 明确 Hold 状态，不阻塞 Phase 1/2/3 |
| 风险 | 100 AI 并发排队 | L0 ProcessLock 未废弃前，100 AI 只能串行执行扫描——并发能力从 100→1 | Phase 6 第一步 L0 降级为 Config Read Lock + G-CT-010 三层文件写入防护 |
| 风险 | 文件并发写入乱码 | 多个 AI 同时写入同一文件导致编码损坏 | G-CT-010 三层防护：L2 FileLock 互斥 + AtomicWrite 防半截 + Git stash/checkout 兜底 |
| 风险 | atomic_write 跨平台兼容 | os.replace() 极端路径可能失败 | 验收测试覆盖：并发 100 进程打同一文件、kill -9 中断、磁盘满场景 |
| 风险 | 10K 脚本全量超时 | 当前 8 worker 跑 268 脚本需 3.5h，10K 脚本需要 130h | Phase 6 切换 BulkheadExecutorV2，40 worker 全量 < 4h |
| 风险 | 增量扫描误扩大 | 维度级映射导致改 1 个模块触发整个维度 100-300 脚本 | Phase 6 G-CT-009 模块→脚本精准映射 |
| 风险 | GPU 长期闲置 | 3090 24GB 完全闲置，D12 AI 检测全 CPU | Phase 6 ONNX→CUDA 迁移 |
| 风险 | SQLite 写锁竞争 | 1,500 模块单 SQLite → 100 AI 并发写入 → 锁竞争吃掉 80% 性能 | Phase 5 ShardRouter 16 分片上线 |
| 风险 | 无告警导致故障累积 | 熔断/CB OPEN/error budget 耗尽靠人肉发现 | Phase 5 Observability Engine 告警规则上线 |
| 负面后果 | L0 ProcessLock 废弃后短暂并发风险 | 废弃瞬间若有 AI 正在写入可能冲突 | G-CT-010 三层防护已覆盖此场景 |
| 负面后果 | BulkheadExecutorV2 切换期间服务中断 | 切换时需短暂停止扫描 | 热升级方案（D-GAP-24）覆盖 |

## 8. 测试用例 P0

> 状态：待施工——本节为测试需求声明，非已实现测试

### P0-U1: 模块核心功能冒烟测试
- G-CT-001~008 每条契约的端到端数据流通断言
- RBAC→Audit 写入验证、Audit→Rollback 回滚触发验证

### P0-U2: 输入校验
- 非法 module_id 引用拒绝
- 循环依赖检测（G-CT-004 Escalation→RBAC 反向引用）

### P0-I1: 与 depends_on 模块集成
- SYS-MASTER-001 金字塔层级约束验证
- MOD-MASTER_BLUEPRINT CT-* 契约与 G-CT-* 契约不冲突验证

### P0-I2: 域内施工顺序验证
- §4 施工顺序的拓扑排序正确性
- 前置模块 not_started 时后续模块禁止开工


## 9. 施工升级路线图

> **已拆分至** [MOD-GOV-CAP-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/capacity-upgrade/blueprint.md) §6
> 本节内容已迁移至独立蓝图，本蓝图仅保留集成契约定义。

---


## 10. 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| SYS-MASTER-001 | 必须 | Level 0 系统总蓝图——治理域是金字塔 Level 1 节点 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |
| MOD-MASTER_BLUEPRINT | 必须 | 基础设施域集成蓝图——治理域依赖基建域基础能力 | — | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-GOVERNANCE` |
| 2 | §11 产出物路径 ↔ 依赖图 path_mappings | 路径一致 | 已对齐 | 同上 |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| d1_structure/validate_directory_layout.py | d3_standards/check_code_style.py | D1 产出的模块结构结论是 D3 的前置条件 | 检查 D1 产出物是否存在 |
| d6_security/scan_secret_leak.py | d9_audit/validate_compliance.py | D6 产出的安全漏洞清单是 D9 审计完整性校验的前置条件 | 检查 D6 产出物是否存在 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| MOD-INF-018 RBAC | MOD-INF-020 Audit | 权限判定结果 | 函数调用 |
| MOD-INF-020 Audit | MOD-INF-021 Rollback | 异常操作事件 | 事件驱动 |
| MOD-INF-021 Rollback | MOD-INF-022 Escalation | 回滚失败事件 | 函数调用 |
| MOD-INF-023 Drift | MOD-INF-021 Rollback | 漂移修复建议 | 函数调用 |
| MOD-INF-024 Budget | MOD-INF-022 Escalation | 预算告警事件 | 事件驱动 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 治理脚本数 > 300，手动维护不可行 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖，需 CI 门禁 |
| 3 | 临时时态内容自动清理 | 否 | 当前无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中模块需持续检测 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | asset-inventory/dependency.py | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 3 | 施工步骤完成度自动检测 | pytest + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## 11. 升级后测试矩阵

> **已拆分至** [MOD-GOV-CAP-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/capacity-upgrade/blueprint.md) §7


## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 6 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 7 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 8 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 9 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #9 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| 本蓝图中 v0.3.1 新增 D-GAP-21~29 设计方案 | **原地** | 服务对象相同（治理域）+ 变更频率同步 + 依赖关系重叠 |
| 本蓝图中 79 个孤儿文件归属映射 | **原地** | 属于治理域内部整理，不是独立子系统 |

---

## ⚠️ 安全删除协议

治理域文件删除MUST遵循RULE-THREE三步审判（见project_rules.md）。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 系统总蓝图 | SYS-MASTER-001 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` | 系统拓扑 |
| 6 | 基础设施域蓝图 | MOD-MASTER_BLUEPRINT | — | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` | 基础设施集成 |
| 7 | 治理方法论标准 | REG-STD-001 / PS-STD-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-001~013 治理决策方法论 |
| 8 | 代码构建标准 | REG-STD-002 / GOV-ENG-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 命名/文件组织/类型注解/SSoT守卫 |
| 9 | AI产出物压缩工作流标准 | REG-STD-004 / GOV-DOC-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 转化优先/15不可删/6砍错模式 |
| 10 | Session状态机规则 | REG-STD-005 / OPS-VC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\operational\vibe_coding\vibe-coding-session-state-runbook.md` | 5状态/7转换/3禁止 |
| 11 | 会话门禁检查清单 | REG-STD-006 / OPS-VC-005 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\operational\vibe_coding\vibe-coding-gate-runbook.md` | 12项门禁检查 |
| 12 | AI事故响应手册 | REG-STD-007 / OPS-VC-004 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\operational\vibe_coding\ai-incident-and-emergency-runbook.md` | P0/P1/P2事故分级 |
| 13 | Vibe Coding操作入口 | REG-STD-008 / OPS-VC-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\operational\vibe_coding\index.md` | Vibe Coding 4文件导航 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | MOD-MASTER_BLUEPRINT | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` | 基础设施域集成 | MOD-MASTER 定义基础设施域，本蓝图定义治理域 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 治理域蓝图 | `D:\ZephyrAlpha\docs\03_modules\_domain_governance\blueprint.md` | 修改 | 本文件 |
| 2 | 治理模块代码 | `D:\ZephyrAlpha\src\zephyr\governance\` | 读取 | 代码对齐 |
| 3 | 治理脚本 | `D:\ZephyrAlpha\scripts\governance\` | 读取 | 脚本清单 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> 本节同时覆盖原 §7 备选方案——决策的"选项"列已包含备选方案信息。
> 负面后果已合并到 §6 风险表（类型=负面后果）。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-GOV-01 | 治理域八件套采用集成蓝图而非8个独立蓝图 | A:集成蓝图 B:8个独立蓝图 | A | 八件套功能紧密耦合，集成契约(G-CT-*)需要统一管理 | 2026-05-06 |
| 2 | D-GOV-02 | Audit 不依赖 RBAC，打破循环依赖 | A:Audit单向接收 B:互相依赖 | A | Audit 只记录事实不需要验证权限，RBAC 主动调用 Audit.write() | 2026-05-06 |
| 3 | D-GOV-03 | L0 ProcessLock 废弃，改用三层精防护 | A:保留L0 B:三层防护 | B | L0 粒度太粗，100 AI 改 100 个不同文件也被迫排队 | 2026-05-10 |
| 4 | D-GOV-04 | 16 分片 SQLite 替代单 SQLite | A:单DB B:16分片 | B | 1,500 模块单 SQLite 锁竞争吃掉 80% 性能 | 2026-05-10 |
| 5 | D-GOV-05 | BulkheadExecutorV2 四池隔离替代全局 ThreadPoolExecutor | A:全局池 B:四池隔离 | B | 不同 tier 脚本超时差异大，全局池慢脚本阻塞快脚本 | 2026-05-10 |
| 6 | D-GOV-06 | GOV-SUB-001~004 合并至 MOD-INF-018/020/021/023 | A:保留子蓝图 B:合并 | B | 子蓝图与父蓝图职责重叠，维护成本高 | 2026-05-10 |
| 7 | D-GOV-07 | 增量扫描默认，全量扫描可选 | A:全量默认 B:增量默认 | B | 日常增量 15-30 脚本 vs 全量 10,000 脚本 | 2026-05-10 |
| 8 | D-GOV-08 | BulkheadExecutorV2 接线完成 | — | — | run_all.py 从 ThreadPoolExecutor(8) 切换到 dispatch_with_locks() | 2026-05-18 |
| 9 | D-GOV-09 | ShardRouter 对齐完成 | — | — | shard_count=4→16 + hash()→sha256 | 2026-05-18 |
| 10 | D-GOV-10 | budget_enforcer↔shared 循环导入修复 | — | — | shared/__init__.py 移除无法导入的声明 | 2026-05-18 |
| 11 | D-GOV-11 | get_audit_writer() 单例工厂创建 | — | — | 旁路桥接引用不存在的函数导致死代码 | 2026-05-18 |
| 12 | D-GOV-12 | AuditEventType 新增枚举值 | — | — | SESSION_RECORD/BUDGET_ENFORCEMENT 语义修复 | 2026-05-18 |
| 13 | D-GOV-13 | 4个自动化缺口修复 | — | — | finding_lifecycle/gate_cache/watchdog/change_impact 全部接入 | 2026-05-18 |
| 14 | D-GOV-14 | D-GAP-01~12 SSoT 收窄 | — | — | 设计真源归 MOD-GOV-CAP-001，本蓝图仅保留索引 | 2026-05-18 |

---

## §19 决策流图架构（decisiongraph，TRAE-061）

> **本节归属**：治理域决策流图基础设施（2026-07-06 新增，TRAE-061）。
> decisiongraph 是继 depgraph（模块依赖图）、dataflowgraph（数据流图）之后的第三张架构图，管理 L0-L6 交易决策链。三图正交，通过 `module_id` 关联。

### §19.1 归属模块

| 文件 | 责任 | capability_id |
|------|------|---------------|
| `src/zephyr/governance/persistence/decisiongraph_schema.py` | PG schema + 连接入口（委托 depgraph 连接） | decisiongraph_schema_management |
| `src/zephyr/governance/persistence/decision_graph_reader.py` | 只读查询 Reader（30+ 方法） | decisiongraph_reader |
| `scripts/governance/extract_decisiongraph.py` | 只读提取 CLI（7 命令） | decisiongraph_extract_cli |
| `scripts/governance/apply_decisiongraph.py` | 写入 CLI（7 操作，pg_advisory_lock=424244） | decisiongraph_apply_cli |
| `scripts/governance/generate_decision_graph.py` | YAML→DB 同步生成器 | decisiongraph_generate_cli |

### §19.2 真源与派生

- **YAML 真源**：`architecture_model/domain/decision_graph_model.yaml`（4 轨 + 10 层 + 6 节点类型 + 4 边类型 + 5 不变量）
- **DB 缓存**：`decision_tracks`/`decision_layers`/`decision_nodes`/`decision_edges`（与 depgraph 共库，表前缀 `decision_*`）
- **派生方向**：YAML → DB 单向同步（`generate_decision_graph.py`），禁止反向
- **词表**：`build_status_values`/`edge_type_values`/`node_type_values`/`track_ids` 从 YAML 动态加载（VOCAB-HARDCODE gate）

### §19.3 五条承重墙不变量

| 编号 | 不变量 | 强制点 |
|------|--------|--------|
| DEC-INV-001 | 风控一票否决：order 节点必有 risk_check→order 的 approving 边 | 应用层 finalize 校验 |
| DEC-INV-002 | 信号仓位分离：signal 不能直接连 order | DB 触发器硬阻断 |
| DEC-INV-003 | DAG 无环 | 应用层 Tarjan SCC |
| DEC-INV-004 | 时间单调性：edges.valid_since ≥ from_node.created_at | DB CHECK |
| DEC-INV-005 | evidence_hash 必填 | DB NOT NULL |

### §19.4 访问协议

- **禁止裸连 DB**：必须通过 `get_decisiongraph_pg_connection()`（委托 `get_depgraph_pg_connection()`，无独立配置）
- **只读查询**：`DecisionGraphReader` 或 `extract_decisiongraph.py`
- **写入设计态**：`apply_decisiongraph.py`（pg_advisory_lock=424244）
- **可视化文档**：`docs/02_enterprise_architecture/06_decision_architecture/`（index + 3 Mermaid）

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 治理域集成契约 G-CT-* | **本文档 §3** | — |
| 治理域容量 SLO | **MOD-GOV-CAP-001 §1** | — |
| 治理域 D-GAP 清单 | **本文档 A/B** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-018 RBAC | G-CT-001~008 |
| Tier 1 | MOD-INF-019 Agent Spec | G-CT-010 |
| Tier 1 | MOD-INF-020 Audit Trail | G-CT-001~008 |
| Tier 1 | MOD-INF-021 Rollback | G-CT-004 |
| Tier 1 | MOD-INF-022 Escalation | G-CT-005 |
| Tier 1 | MOD-INF-023 Drift Detector | G-CT-006 |
| Tier 1 | MOD-INF-024 Budget Enforcer | G-CT-007 |
| Tier 1 | MOD-INF-025 A2A Protocol | G-CT-008 |

### 变更同步规则

| 变更类型 | Tier 1（下游模块） | Tier 2（集成系统） |
|---------|------------------|------------------|
| G-CT-* 契约变更 | 通知所有签约方 | 更新 circuit_breaker.py |
| 容量 SLO 变更 | 更新调度器参数 | 更新监控告警 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| G-CT-* 契约新增 | AI 可自主 |
| G-CT-* 契约修改 | 需 Owner 审批 + 通知所有签约方 |
| 容量 SLO 变更 | 需 Owner 审批 |

---

## §0 代码对齐验证

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

| 验证项 | 命令 | 通过标准 |
|--------|------|---------|
| G-CT-021 MTH-006 三向触发器 | `python scripts/governance/sync_rule_registry.py` | [MTH-006] PASS |
| 孤儿检测 | `python scripts/governance/d11_compliance/audit_registration.py` | exit 0 |
| 契约代码存在性 | `python -m pytest tests/ --collect-only -q` | 0 errors |
| 蓝图-代码双向对齐 | `python scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py` | HIGH=0 |

---

## §5 约束条件

| # | 约束 | 类型 | 违反后果 |
|---|------|------|---------|
| 1 | G-CT-* 契约变更 MUST 通知所有签约方 | 流程约束 | 集成断裂 |
| 2 | 治理八件套 MUST 按 Phase 1-4 顺序推进 | 顺序约束 | 循环依赖 |
| 3 | G-CT-010a 原子写入 MUST 用 temp-file + os.replace() | 技术约束 | Windows 并发写入损坏 |
| 4 | Finding 存储 MUST 有 TTL + 自动清理 | 数据约束 | 存储膨胀 |
| 5 | 容量 SLO MUST 每季度重新校准 | 时间约束 | SLO 过期 |

---

## §6 错误处理

| 错误场景 | 处理方式 | 升级路径 |
|----------|---------|---------|
| G-CT 契约验证失败 | sync_rule_registry.py 报告缺失项 | AI 自主修复 → 重新验证 |
| RBAC 权限判定失败 | PermissionGuard 返回 BLOCKED | G-CT-004 → Escalation → 人工审批 |
| Rollback 失败 | 回滚后验证不通过 | G-CT-003 → Escalation |
| Budget 超限 | BudgetEngine 降级或拒绝 | G-CT-006 → Escalation |
| A2A 冲突 | ConflictDetector 检测 → Arbitrator 仲裁 | G-CT-008 → RBAC 验证仲裁人权限 |
| MTH-006 触发器缺失 | sync_rule_registry.py EXIT_FINDINGS | 禁止关闭任务 → AI 补全触发器 |

---

## §8 安全考量

| 层级 | 措施 | 对应 G-CT |
|------|------|----------|
| 身份验证 | AgentCard 签名 + RBAC 七层纵深 | G-CT-007/022 |
| 操作审计 | 不可变 Audit Trail + 密码学 Provenance | G-CT-001 |
| 异常恢复 | Git-native Rollback + Checkpoint | G-CT-002/005 |
| 权限升级 | 五层防御 + 人工审批 | G-CT-004/006 |
| 数据隔离 | 脚本沙箱 + RLIMIT | G-CT-019 |
| 密钥管理 | LLM Security Gateway fail-closed | MOD-LLM_SECURITY |

---

## §11 产出物

| 产出物 | 路径 | 状态 |
|--------|------|------|
| 治理域蓝图 | `docs/03_modules/_domain_governance/blueprint.md` | Active |
| sync_rule_registry.py | `scripts/governance/sync_rule_registry.py` | Active |
| audit_registration.py | `scripts/governance/d11_compliance/audit_registration.py` | Active |
| pre_write_gate.py | `scripts/governance/d5_architecture/pre_write_gate.py` | Active |
| lock_files.py | `scripts/lock_files.py` | Active |
| rollback.py | `scripts/rollback.py` | Active |
| _concurrency.py | `scripts/governance/_concurrency.py` | Active |
| run_all.py | `scripts/governance/run_all.py` | Active |
| skill-registry.yaml | `src/zephyr/agent-spec/skill-registry.yaml` | Active |
| Agent RBAC 模块 | `src/zephyr/infra_ops/agent-rbac/` | phase_2_complete |
| Audit Trail 模块 | `src/zephyr/infra_ops/audit-trail/` | phase_2_complete |
| Rollback 模块 | `src/zephyr/infra_ops/rollback_system/` | phase_2_complete |
| Escalation 模块 | `src/zephyr/infra_ops/escalation_protocol/` | phase_2_complete |
| Drift Detector 模块 | `src/zephyr/infra_ops/drift-detector/` | completed |
| Budget Enforcer 模块 | `src/zephyr/infra_ops/budget-enforcer/` | phase_2_complete |
| A2A Protocol 模块 | `src/zephyr/infra_ops/a2a_protocol/` | phase_2_complete |
| Agent Spec 模块 | `src/zephyr/infra_ops/agent-spec/` | phase_2_complete |
| check_blueprint_code_alignment.py | `scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py` | Active |
| sync_registry_from_blueprints.py | `scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py` | Active（fail-fast：frontmatter YAML 损坏时 exit 1） |

---

## §12 集成目标

| 目标 | 衡量标准 | 当前状态 |
|------|---------|---------|
| 治理闭环端到端自动化 | RBAC→Audit→Rollback→Escalation 无人工干预 | ✅ LifecycleManager 自动接线（审计任务注册+自监控启动） |
| 8 模块集成契约 100% 覆盖 | G-CT-001~008 全部有代码实现 | ✅ 8/8 数据流验证通过 |
| 孤儿率 0% | audit_registration.py exit 0 | ✅ CLEAN |
| MTH-006 触发器三向完整 | sync_rule_registry.py MTH-006 PASS | ✅ |
| 蓝图↔代码对齐 HIGH=0 | check_blueprint_code_alignment.py | ✅ HIGH=0 |
| 容量 SLO 达标 | 10K 脚本 / 1.5K 模块 / 100 AI 并发 | ⚠️ Phase 6 待施工 |
| BulkheadExecutorV2 接线 | run_all.py 接入 BulkheadExecutorV2 | ✅ 已接线（_USE_BULKHEAD=True，fallback ThreadPoolExecutor） |
| ShardRouter 对齐 | shard_count=16 + sha256 路由 | ✅ 已对齐（sha256 确定性路由，16 分片） |
| NEW-01~15 脚本实现 | 15 个 D-GAP 脚本 | ✅ 14 已实现 + 1 复用已有（NEW-14） |

---

## §13 需要更新

| 触发条件 | 需更新内容 | 更新位置 |
|----------|----------|---------|
| 新增 G-CT-* 契约 | 蓝图 §3 + §A.1 审计表 + dependency_path_panorama.md | 本蓝图 + 依赖图 |
| 新增治理脚本 | script-manifest.yaml + 蓝图 §11 产出物 | scripts/ + 本蓝图 |
| 修改 RULE-* | _index.yaml + sync_rule_registry.py MTH-006 检查 | .trae/rules/ + scripts/ |
| 修改 PS-REG-012 | MUST 同步检查 PS-STD-001 | docs/ |
| 子模块施工进度变更 | 蓝图 §2 域内模块清单 + frontmatter construction_progress | 本蓝图 |

---

## 术语表

| 术语 | 定义 |
|------|------|
| G-CT | Governance Cross-module Contract，治理域跨模块集成契约 |
| RBAC | Role-Based Access Control，基于角色的访问控制 |
| A2A | Agent-to-Agent，Agent 间通信协议 |
| SSoT | Single Source of Truth，唯一真源 |
| D-GAP | Design Gap，设计缺失 |
| ARB | Architecture Review Board，架构评审委员会 |
| MTH | Methodology，治理方法论（MTH-001~013） |
| SLO | Service Level Objective，服务等级目标 |
| TTL | Time To Live，生存时间 |
| RLIMIT | Resource Limit，资源限制（进程级） |

---

## 自检清单

| # | 检查项 | 通过标准 |
|---|--------|---------|
| 1 | frontmatter 33 字段完整 | 无缺失 |
| 2 | §0 代码对齐验证可执行 | 命令 exit 0 |
| 3 | §3 所有 G-CT-* 有方向+触发时机 | 无空定义 |
| 4 | §11 产出物路径与磁盘一致 | 每个路径可 Grep 到 |
| 5 | 蓝图 `[BLUEPRINT]` 标注与代码头部双向对齐 | 代码头部有 MOD-GOVERNANCE |
| 6 | construction_progress 与代码实际状态一致 | 无虚标 |
| 7 | dependency_path_panorama.md G-CT-* 描述与蓝图一致 | 无冲突 |
| 8 | MTH-006 三向触发器完整 | sync_rule_registry.py PASS |

---

## 成熟度声明

| 维度 | 等级 | 证据 |
|------|:---:|------|
| 设计完整性 | L3 | 22 条 G-CT 契约覆盖 8 模块闭环 |
| 代码实现 | L2 | 核心闭环 G-CT-001~008 已实现，G-CT-015~022 待实现 |
| 测试覆盖 | L1 | 端到端测试待补充 |
| 自动化 | L2 | sync_rule_registry.py 自动化，核心闭环需显式调用 |
| 文档完整性 | L3 | 模板必需章节已补全 |
