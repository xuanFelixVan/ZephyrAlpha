---
module_id: MOD-INF-027
activation_phase: requires_100ai
submodule_path: src/zephyr/governance
title: "Audit Orchestrator 蓝图 — 审计编排器·三子系统架构"
doc_type: blueprint
status: Active
version: "6.1.0"
layer: L1_foundation
architecture_layer: "L2_编排调度"
layer_name: cross_layer
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
valid_from: "2026-05-01"
date: "2026-05-01"
ttl: permanent
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-14"
last_verified: "2026-05-14"
last_updated: "2026-05-14"
generation: 6
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/governance/"
summary: "审计编排器——MAPE-K五层自治循环驱动三子系统(结构/语义/行为)四阶段闭环迭代收敛审计引擎。v6.1.0: v3.5模板对齐"
priority: P1
runtime_plane: hot
tags: [audit, orchestrator, multi-dimensional, iterative, convergence, governance, self-healing, ai-driven, cross-cutting, orphan-judgment, semantic-audit, red-blue-adversarial, git-backup, chaos-engineering, mape-k, trae, roo-code, api-automation, incremental-audit, meta-audit, observability, telemetry, cron-scheduler, circuit-breaker, plugin-architecture, agent-skill, dora-metrics, compliance-mapping, disaster-recovery, capacity-upgrade, v3.5-template]
depends_on:
  - target: "MOD-GATE_ENGINE"
    at: "full"
    why: "Gate Engine"
  - target: "MOD-INF-017"
    at: "full"
    why: "Code Dedup Engine"
  - target: "MOD-INF-020"
    at: "full"
    why: "Audit Trail"
  - target: "MOD-INF-023"
    at: "section 2"
    why: "Drift Detector"
  - target: "MOD-INF-026"
    at: "full"
    why: "Asset Inventory"
  - target: "MOD-INF-028"
    at: "full"
    why: "SemanticAuditor peer service"
  - target: "MOD-INF-033"
    at: "full"
    why: "BehavioralAuditor peer service"
  - target: "MOD-INF-029"
    at: "full"
    why: "Orphan Judge"
  - target: "MOD-INF-030"
    at: "full"
    why: "RedBlue Validator"
  - target: "MOD-INF-031"
    at: "full"
    why: "AutoFix Engine"
  - target: "MOD-FEEDBACK_LOOP"
    at: "section 2"
    why: "Feedback Loop"
  - target: "MOD-INF-018"
    at: "section 3"
    why: "Agent RBAC"
  - target: "MOD-LLM_SECURITY"
    at: "section 3"
    why: "LLM Security"
  - target: "MOD-INF-015"
    at: "section 2"
    why: "System Telemetry"
references:
  - id: "MOD-INF-005"
    at: "full"
    why: "Script System"
  - id: "MOD-TASK_SYSTEM"
    at: "section 1"
    why: "Task System"
  - id: "MOD-INF-009"
    at: "section 2"
    why: "Pipeline"
  - id: "MOD-INF-019"
    at: "section 3"
    why: "Agent Spec"
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Audit Orchestrator 蓝图 — 审计编排器·三子系统架构

> module_id: MOD-INF-027 | version: 6.1.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/audit-orchestrator/ | generation: 6 | construction_progress: partially_implemented | realized: 7/33

## 概述

Audit Orchestrator 是 ZephyrAlpha 的全维度系统自证清白引擎，基于 MAPE-K 五层自治循环驱动三子系统（Structural/Semantic/Behavioral）四阶段闭环迭代收敛。核心职责：自动发现所有可审计目标 → 四阶段闭环（DISCOVER→TRIAGE→REPAIR→ENFORCE）→ 迭代收敛 → Knowledge 积累 → 直到全局通过。当前规模 86 个 Provider 脚本 / 17 结构维度，目标容量 10,000 脚本 / 1,500 模块 / 100 AI 并发。上游依赖 AssetInventory/GateEngine/AuditTrail，下游被 FeedbackLoop/MCP/Pipeline 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-027`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §4 | 模块导出 | 已实现 | — |
| 2 | `models.py` | §4.2 | 数据模型 | 未实现 | blueprint寄生：文件从未创建 |
| 3 | `contracts.py` | §4 | 接口契约 | 未实现 | blueprint寄生：文件从未创建 |
| 4 | `cli.py` | §4.5 | CLI 入口 | 已实现 | — |
| 5 | `bridge.py` | §12 | 集成桥接 | 未实现 | blueprint寄生：文件从未创建 |
| 6 | `writer.py` | §4.4 | 审计报告写入 | 未实现 | blueprint寄生：文件从未创建 |
| 7 | `query.py` | §4.1 | 审计查询 | 未实现 | blueprint寄生：文件从未创建 |
| 8 | `indexer.py` | §3.1 | 索引构建 | 未实现 | blueprint寄生：文件从未创建 |
| 9 | `cold_start.py` | §3.1 | 冷启动缓存 | 未实现 | blueprint寄生：文件从未创建 |
| 10 | `integrity.py` | §8 | 完整性校验 | 未实现 | blueprint寄生：文件从未创建 |
| 11 | `trust_engine.py` | §8 | 信任引擎 | 未实现 | blueprint寄生：文件从未创建 |
| 12 | `trust_bridge.py` | §12 | 信任桥接 | 未实现 | blueprint寄生：文件从未创建 |
| 13 | `delegation_bridge.py` | §12 | 委托桥接 | 未实现 | blueprint寄生：文件从未创建 |
| 14 | `delegation_auditor.py` | §8 | 委托审计 | 未实现 | blueprint寄生：文件从未创建 |
| 15 | `drift_bridge.py` | §12 | 漂移桥接 | 未实现 | blueprint寄生：文件从未创建 |
| 16 | `feedback_bridge.py` | §12 | 反馈桥接 | 未实现 | blueprint寄生：文件从未创建 |
| 17 | `feedback_policy.py` | §5.1 | 反馈策略 | 未实现 | blueprint寄生：文件从未创建 |
| 18 | `tiered_storage.py` | §5.2 | 分层存储 | 未实现 | blueprint寄生：文件从未创建 |
| 19 | `tiered_storage_bridge.py` | §12 | 分层存储桥接 | 未实现 | blueprint寄生：文件从未创建 |
| 20 | `self_monitor.py` | §3.1 | 自监控 | 未实现 | blueprint寄生：文件从未创建 |
| 21 | `anomaly.py` | §6 | 异常检测 | 未实现 | blueprint寄生：文件从未创建 |
| 22 | `merkle_hourly.py` | §8 | Merkle 小时校验 | 未实现 | blueprint寄生：文件从未创建 |
| 23 | `evidence_pack.py` | §8 | 证据打包 | 未实现 | blueprint寄生：文件从未创建 |
| 24 | `log_rotation.py` | §5.1 | 日志轮转 | 未实现 | blueprint寄生：文件从未创建 |
| 25 | `external_tool_audit.py` | §9 | 外部工具审计 | 未实现 | blueprint寄生：文件从未创建 |
| 26 | `retention.py` | §5.1 | 数据保留策略 | 未实现 | blueprint寄生：文件从未创建 |
| 27 | `genesis.py` | §3.1 | 创世块 | 未实现 | blueprint寄生：文件从未创建 |
| 28 | `replay_engine.py` | §9 | 重放引擎 | 未实现 | blueprint寄生：文件从未创建 |
| 29 | `__main__.py` | §3.1 |   main   | 已实现 | — |
| 30 | `audit_admission_controller.py` | §3.1 | audit admission controller | 已实现 | — |
| 31 | `pipeline_runner.py` | §3.1 | pipeline runner | 已实现 | — |
| 32 | `resource_aware_pool.py` | §3.1 | resource aware pool | 已实现 | — |
| 33 | `text_to_finding_adapter.py` | §3.1 | text to finding adapter | 已实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 7/33 文件实际存在 | `ls src/zephyr/audit-orchestrator/*.py` | ✅ |
| 26 个未实现文件标记为 "blueprint寄生：文件从未创建" | 逐行核对 §0.1 | ✅ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| v5.0.0 容量升级组件尚未实现 | `ls src/zephyr/audit-orchestrator/pool/` 等 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v4.0.0 (基线) | 7 个文件（cli/pipeline_runner/admission_controller/resource_pool/__init__/__main__/text_to_finding） | — | — |
| v5.0.0 (容量升级) | 无 | ResourceAwarePool/ScriptRouter/SessionAuditManager/ScriptDiscovery/HashCacheDB/ScriptDAG/FullScanOrchestrator/GPUMonitor/LiveScoreboard/PatternDB/AdmissionController/Coalescer/CheckpointManager/CapacityPlanner/ProtectionIndex/ModuleLock | 待施工 Phase 0-3 |
| v6.1.0 (模板对齐v3.5) | 同 v4.0.0 | 26 个文件标记为blueprint寄生(从未创建) + 容量升级组件 16 个 | 蓝图膨胀：宣称31个文件"已实现"实际只有7个存在 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 项目规模从 51 模块增长至 1,500 模块，治理脚本从 268 增长至 10,000，AI 并发从 1 增长至 100。v4.0.0 蓝图功能框架完备（MAPE-K/四阶段闭环/三类审计分流/六层触发/CircuitBreaker/Meta-Audit），但容量维度基本空白——核心矛盾不在功能缺失，而在规模扩展能力缺失。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 支持 10,000 脚本 / 1,500 模块 / 100 AI 并发 | ResourceAwarePool 40-100 动态并发 |
| 2 | 增量扫描 < 1 分钟 | ScriptRouter 精准路由 15-30 脚本 |
| 3 | 全量扫描 < 3.5 小时 | ShardExecutor 8 分片并行 |
| 4 | 会话级隔离替代全局锁 | SessionAuditManager 100 并发 |
| 5 | 脚本即插即用自动发现 | ScriptDiscovery + @audit 注解 |
| 6 | 系统级准入控制与背压 | AuditAdmissionController Token Bucket + Circuit Breaker |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 语义审计实现 | MOD-INF-028 独立 peer 服务 |
| 2 | 行为审计实现 | MOD-INF-033 独立 peer 服务 |
| 3 | 修复执行实现 | MOD-INF-031 AutoFix Engine 独立服务 |
| 4 | 红白对抗实现 | MOD-INF-030 RedBlue Validator 独立服务 |
| 5 | 运行时监控 | MOD-INF-015 System Telemetry 职责 |
| 6 | 知识审计 | VectorMemory 自检职责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 硬件：i7-12700KF (12C/20T) / 64GB RAM / 1TB NVMe / RTX 3090 24GB | CPU 池 12 线程 + I/O 池 30 线程 + 内存预留 32GB |
| Windows NTFS + Defender 实时扫描 | 文件写入必须原子操作（temp-file + os.replace） |
| 单机部署，无分布式 | SQLite WAL 模式替代外部数据库，进程内并发 |
| 100 AI Session 并发冷启动 | 共享 BootstrapCache 单例，避免重复加载 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 审计编排 | 四阶段闭环调度：DISCOVER→TRIAGE→REPAIR→ENFORCE |
| 2 | 三类审计分流 | Structural(内建17维) / Semantic(dispatch MOD-INF-028) / Behavioral(dispatch MOD-INF-033) |
| 3 | 增量扫描 | Hash 指纹缓存 + ScriptRouter 精准路由 |
| 4 | 全量扫描 | ShardExecutor 分片并行 + CheckpointManager 断点续跑 |
| 5 | 会话管理 | SessionAuditManager 100 AI 会话级隔离 |
| 6 | 容量调度 | ResourceAwarePool 双池异步 + 四级优先级队列 |
| 7 | 知识积累 | PatternLearner + RuleEvolver + FixTemplateDB |
| 8 | 自审计 | Meta-Audit DIM-META-001 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 语义审计判定 | MOD-INF-028 SemanticAuditor |
| 2 | 行为审计判定 | MOD-INF-033 BehavioralAuditor |
| 3 | 修复执行 | MOD-INF-031 AutoFixEngine |
| 4 | 红白对抗 | MOD-INF-030 RedBlueValidator |
| 5 | 孤儿判定 | MOD-INF-029 OrphanJudge |
| 6 | 资产发现 | MOD-INF-026 AssetInventory |
| 7 | 审计日志 | MOD-INF-020 AuditTrail |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | PhaseController | 四阶段闭环调度 | DiscoveryEngine, TriageScheduler | 同步调用 |
| 2 | DiscoveryEngine | 增量 Hash 指纹变更检测 | AssetInventory, HashStore | 同步调用 |
| 3 | TriageScheduler | 三类审计分流 + 去重 + 排序 | ScriptRouter, ScriptDAG | 同步调用 |
| 4 | ResourceAwarePool | 双池异步并发调度 | CPUMonitor, MemoryMonitor | 异步队列 |
| 5 | SessionAuditManager | 100 AI 会话级隔离 | ResourceAwarePool, ScriptRouter | 事件驱动 |
| 6 | ScriptRouter | 文件→脚本精准路由 | ScriptInventory | 同步查询 |
| 7 | Coalescer | 触发风暴去重 | — | 事件窗口 |
| 8 | AuditAdmissionController | 系统级准入控制 | TokenBucket, CircuitBreaker | 同步拦截 |
| 9 | ShardExecutor | 全量扫描分片并行 | ResourceAwarePool | 异步进程 |
| 10 | CheckpointManager | 长任务断点续跑 | HashStore(SQLite) | 同步读写 |
| 11 | CapacityPlanner | 显式容量预算模型 | CPUMonitor, MemoryMonitor, GPUMonitor | 定时采样 |
| 12 | ProtectionIndex | L0 纯内存哈希表 | — | 同步查询 |
| 13 | LiveScoreboard | 流式结果聚合 | ResourceAwarePool | 事件回调 |
| 14 | PatternLearner | 历史模式识别 | PatternDB(SQLite) | 批量分析 |
| 15 | CircuitBreaker | 维度级熔断 | — | 同步检查 |
| 16 | MetaAuditor | 自审计 | DIM-TYPE-001 | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|------|---------|------|---------|
| 1 | 100 AI Sessions | Coalescer 5s 去重 → AdmissionController 准入 → ScriptRouter 精准路由 → PriorityQueue 4级 → ResourceAwarePool 双池执行 → LiveScoreboard 流式聚合 | AuditReport | Pydantic Model |
| 2 | AssetInventory(mtime) | DiscoveryEngine Hash 比对 → 增量变更集 | TriageScheduler | DiscoveryReport |
| 3 | AuditTrail 事件 | BehavioralAuditor(MOD-INF-033) 消费 | Block/Alert/Rollback | Event |
| 4 | Cron 定时 | FullScanOrchestrator 分片 → ShardExecutor × 8 并行 → GlobalFullScanReport | ReportGenerator | Pydantic Model |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| IDLE | 审计请求到达 | DISCOVERING | AdmissionController.admit() = True |
| DISCOVERING | 变更集生成 | TRIAGING | DiscoveryReport 非空 |
| TRIAGING | 脚本路由完成 | SCHEDULING | ScriptRouter 命中 ≥ 1 脚本 |
| SCHEDULING | 队列排定 | EXECUTING | PriorityQueue 非空 |
| EXECUTING | 脚本完成 | REPAIRING | 存在 RED finding |
| EXECUTING | 脚本完成 | ENFORCING | 全部 GREEN |
| REPAIRING | 修复完成 | ENFORCING | RepairReport 生成 |
| ENFORCING | RedBlue 通过 | CONVERGED | N 次连续零问题 |
| ENFORCING | RedBlue 失败 | DISCOVERING | max_global_rounds 未达 |
| CONVERGED | 知识回写完成 | IDLE | KB writeback 成功 |

---

## §4 接口契约

### 4.1 公共 API

```python
class AuditOrchestrator:
    def run_incremental(self, session_id: str, changed_files: list[Path]) -> AuditReport:
        """增量审计——ScriptRouter 精准路由 15-30 脚本"""
    def run_full(self, shard: tuple[int, int] | None = None, resume: bool = False) -> AuditReport:
        """全量审计——ShardExecutor 分片并行"""
    def run_phase(self, phase: int, context: AuditContext) -> PhaseResult:
        """单阶段执行"""
    def get_status(self) -> OrchestratorStatus:
        """当前状态查询"""
    def get_scoreboard(self, session_id: str) -> ScoreboardSnapshot:
        """实时评分板"""
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class AuditType(str, Enum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"

class Severity(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

class Priority(str, Enum):
    P0_SEC = "P0_SEC"
    P0 = "P0"
    P1 = "P1"
    OPT = "OPT"

class FixLevel(str, Enum):
    L1_AUTO = "L1_AUTO"
    L2_LLM = "L2_LLM"
    L3_HUMAN = "L3_HUMAN"

class DiscoveryReport(BaseModel):
    changed_files: list[ChangedFile]
    total_scanned: int
    skipped_unchanged: int
    audit_type_distribution: dict[str, int]

class ChangedFile(BaseModel):
    path: str
    audit_type: AuditType
    old_hash: str
    new_hash: str
    priority: int

class AuditIssue(BaseModel):
    issue_id: str = Field(..., description="唯一标识")
    dim_id: str = Field(..., description="维度ID")
    check_id: str = Field(..., description="检查项ID")
    target_file: str = Field(..., description="目标文件路径")
    severity: Severity = Field(..., description="严重程度")
    auto_fixable: bool = Field(..., description="是否可自动修复")
    fix_level: FixLevel = Field(..., description="修复级别")
    suggested_fix: str | None = Field(default=None, description="修复建议")

class GlobalAuditReport(BaseModel):
    audit_id: str
    started_at: datetime
    finished_at: datetime | None
    global_rounds: int
    global_converged: bool
    total_issues_found: int
    total_issues_fixed: int
    is_incremental: bool
    skipped_by_cache: int
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `run_incremental()` | `session_id` | ✅ | `session-YYYYMMDD-NNN` 格式 |
| `run_incremental()` | `changed_files` | ✅ | 非空列表，路径必须存在 |
| `run_full()` | `shard` | ❌ | `(N, M)` 格式，1 ≤ N ≤ M |
| `run_full()` | `resume` | ❌ | 默认 False |
| `run_phase()` | `phase` | ✅ | 1-4 整数 |
| `run_phase()` | `context` | ✅ | AuditContext 实例 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `run_incremental()` | `AuditReport`：converged=True/False | `AUDIT_ADMITTED_REJECTED` / `AUDIT_CIRCUIT_OPEN` |
| `run_full()` | `AuditReport`：shard 结果 | `SHARD_TIMEOUT` / `CHECKPOINT_CORRUPT` |
| `run_phase()` | `PhaseResult`：阶段结果 | `PHASE_PRECONDITION_FAILED` |
| `get_status()` | `OrchestratorStatus`：当前状态 | — |
| `get_scoreboard()` | `ScoreboardSnapshot`：实时进度 | `SESSION_NOT_FOUND` |

### 4.5 MCP 接口

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `governance.run_audit` | `run_incremental()` / `run_full()` | `{mode: str, dimensions: list, auto_fix: bool}` | `GlobalAuditReport` |
| `governance.audit_status` | `get_status()` | `{}` | `OrchestratorStatus` |
| `governance.audit_history` | 历史查询 | `{limit: int}` | `list[dict]` |

**错误码**：`ADMISSION_REJECTED(429)` — 限流 / `CIRCUIT_OPEN(503)` — 熔断 / `SESSION_NOT_FOUND(404)`

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 | 3.12+ |
| 2 | 数据验证框架 | Pydantic V2 |
| 3 | 本地数据库 | SQLite WAL 模式 |
| 4 | 并发模型 | ThreadPoolExecutor |
| 5 | 文件写入 | temp-file + os.replace() 原子写入 |
| 6 | 编码 | UTF-8，禁止省略 encoding |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模块数 | 51 | 1,500 | 10,000 | ✅ | ModuleGraph 索引 |
| 治理脚本 | 268 | 10,000 | 50,000 | ✅ | ScriptDiscovery 自动发现 |
| AI 并发 | 1 | 100 | 200 | ✅ | SessionAuditManager 隔离 |
| 脚本并发 | 8 | 40-100 | 200 | ✅ | ResourceAwarePool 双池 |
| 增量扫描 | ~秒级 | <1 分钟 | — | ✅ | ScriptRouter 精准路由 |
| 全量扫描 | <30min | <3.5 小时 | — | ⚠️ | ShardExecutor 8 分片 |
| 内存 | 未约束 | <48GB | 64GB | ✅ | CapacityPlanner 水位监控 |
| 审计事件写入 | 未估算 | ~900 条/峰值批 | 2,000 rows/s | ✅ | WriteBatcher 批量写入 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | hash_index.json | `D:\ZephyrAlpha\data\audit_cache\hash_index.json` | `D:\ZephyrAlpha\data\audit_cache\hash_cache.db` | SQLite 替代 JSON | Grep 全项目引用并更新 |
| 2 | audit-global.lock | 全局锁 | ModuleLock + FileLock | 细粒度锁替代 | 修改 TriageScheduler |
| 3 | run_all.py 单体全扫 | `D:\ZephyrAlpha\scripts\governance\run_all.py` | 保留 + 增加 --shard 参数 | 扩展功能 | 向后兼容 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Doom Loop（修复→新问题→循环） | max_passes 硬上限 + max_global_rounds=3 | NonConvergenceHandler 升级人工 | 本次审计 |
| 2 | 维度检查 hang | 单维度 5min 超时 | CircuitBreaker OPEN → 跳过该维度 | 该维度 |
| 3 | 100 AI 同时触发 | AdmissionController Token Bucket | 限流 10/s + 熔断 50% 失败率 | 触发请求 |
| 4 | 脚本超时 | 5min 硬超时 + 渐进式降级 | LOG→DEGRADE→DISABLE 三级 | 该脚本 |
| 5 | 增量缓存损坏 | Hash 校验失败 | 自动退回全量模式 | 本次审计 |
| 6 | 全量扫描中断 | CheckpointManager | --resume 从断点续跑 | 该分片 |
| 7 | 大面积误修 | Git pre-tag | git checkout pre-tag + rollback_auditor | 修复范围 |
| 8 | KB 写入失败 | 异常捕获 | 不阻塞审计主流程，下次补写 | 知识层 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 审计绕过——AI 跳过审计直接写入 | 高 | L0 pre_op_check 实时阻断 | 测试 AI 写入被拦截 |
| 2 | 审计日志篡改 | 高 | MOD-INF-020 Merkle 根哈希 + 不可变校验 | TamperProofAudit 验证 |
| 3 | 密钥硬编码 | 高 | DIM-SECURITY-001 硬阻断 CI | detect_secrets.py 扫描 |
| 4 | 审计结果伪造 | 中 | RedBlue 对抗验证 | MOD-INF-030 验证 |
| 5 | 会话间数据泄漏 | 中 | SessionAuditManager 隔离 | 测试跨 Session 不可见 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | Discovery/Cache/Router/Pool/CircuitBreaker | Hash 比对/路由命中/优先级排序/熔断状态转换 | >90% 覆盖 |
| 2 | 集成测试 | 单维度完整流程 | 17 个维度全过 | 端到端通过 |
| 3 | 容量测试 | 10,000 脚本注册 + 100 并发 Session | 路由压测/并发压测/全量分片 | <1min 增量 / <3.5h 全量 |
| 4 | 红蓝专项 | 7 个攻击场景 | 100% 防住 + 自生长攻击库 | 无绕过 |
| 5 | 灾难恢复 | 3 种 DR 场景 | DR-1 误删/DR-2 注册表损坏/DR-3 缓存中毒 | 状态完全恢复 |
| 6 | 增量验证 | 修改 1 文件 → 增量审计 | 仅审计该文件 | 正确跳过未变 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-GATE_ENGINE Gate Engine | 必须 | G0 入口 + 蓝方判定 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_infra_ops\gate_engine\blueprint.md` |
| MOD-INF-020 Audit Trail | 必须 | 审计日志 + Merkle 根哈希 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_infra_ops\audit-trail\blueprint.md` |
| MOD-INF-026 Asset Inventory | 必须 | Phase 1 发现目标清单 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_infra_ops\asset-inventory\blueprint.md` |
| MOD-INF-028 SemanticAuditor | 必须 | 语义审计 peer 服务 | v4.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\semantic-auditor\blueprint.md` |
| MOD-INF-033 BehavioralAuditor | 必须 | 行为审计 peer 服务 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\behavioral-auditor\blueprint.md` |
| MOD-INF-029 OrphanJudge | 必须 | 孤儿判定三决策树 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\orphan-judge\blueprint.md` |
| MOD-INF-030 RedBlue Validator | 必须 | 红白对抗验证 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\red-blue-validator\blueprint.md` |
| MOD-INF-031 AutoFix Engine | 必须 | 修复执行 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-fix-engine\blueprint.md` |
| MOD-DATABASE Database v3.0 | 必须 | get_depgraph_pg_connection()（PG）+ get_db_connection()（SQLite）+ WriteBatcher（暂缓待 L 级） | v3.0+ | `D:\ZephyrAlpha\docs\03_modules\_infra_ops\database\blueprint.md` |
| MOD-INF-023 Drift Detector | 可选 | 漂移信号 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_infra_ops\drift-detector\blueprint.md` |
| MOD-FEEDBACK_LOOP Feedback Loop | 可选 | 审计发现回写规则演进 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_infra_ops\feedback_loop\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-027` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| DiscoveryEngine | TriageScheduler | 变更集是分流前置条件 | 检查 DiscoveryReport 非空 |
| TriageScheduler | ScriptRouter | 分流结果驱动路由 | 检查路由命中 ≥ 1 |
| ScriptRouter | PriorityQueue | 路由结果入队 | 检查队列非空 |
| PriorityQueue | ResourceAwarePool | 队列驱动执行 | 检查 worker 分配 |
| ResourceAwarePool | LiveScoreboard | 执行结果聚合 | 检查 ScoreboardSnapshot |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| AssetInventory | DiscoveryEngine | 资产清单 | 函数调用 |
| HashStore | DiscoveryEngine | 历史指纹 | SQLite 查询 |
| DiscoveryEngine | TriageScheduler | DiscoveryReport | Pydantic Model |
| TriageScheduler | ScriptRouter | 待审计文件列表 | 函数调用 |
| ScriptRouter | PriorityQueue | 脚本执行计划 | 函数调用 |
| PriorityQueue | ResourceAwarePool | 执行队列 | 异步队列 |
| ResourceAwarePool | LiveScoreboard | 执行结果 | 事件回调 |
| LiveScoreboard | PatternLearner | 历史模式 | 批量分析 |
| CheckpointManager | ShardExecutor | 断点信息 | SQLite 查询 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 86+ 脚本间有复杂依赖 |
| 2 | 依赖对齐自动验证 | 是 | 11 个外部依赖需对齐 |
| 3 | 临时时态内容自动清理 | 是 | §5.3 有 3 个迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中，5 个 Phase |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | asset-inventory/dependency.py | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\audit-orchestrator\` | 测试用例 |
| 缓存数据 | `D:\ZephyrAlpha\data\audit_cache\` | SQLite HashStore + PatternDB |
| 审计历史 | `D:\ZephyrAlpha\data\audit_history\` | 审计报告 + 趋势数据 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MCP Governance Server | 新增 MCP Tool | `run_audit` / `audit_status` / `audit_history` | MCP 调用返回正确结果 |
| Pipeline Orchestrator | 新增 Pipeline Stage | `PRE-DEPLOY-AUDIT` stage | Pipeline 执行审计门禁 |
| Agent Spec Skill | 注册 Skill | `audit-orchestrator` skill | `python -m zephyr.agent_spec list` 可见 |
| Cron Scheduler | 配置注入 | `config/audit_schedule.yaml` | 定时触发执行 |
| Database v3.0 | 接口契约 CT-AO-DB-001 | get_depgraph_pg_connection()（PG）+ get_db_connection()（SQLite）+ WriteBatcher（暂缓待 L 级） | 审计事件写入 PG |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-001 | 治理域 | 读取 RBAC 策略校验审计权限 | MOD-INF-018 Agent RBAC | 修改 RBAC 策略必须同步审计权限 |
| G-CT-007 | 治理域 | 读取 Agent Spec 校验审计行为规范 | MOD-INF-019 Agent Spec | 修改 Agent Spec 必须同步审计行为 |
| G-CT-003 | 治理域 | 推送审计遥测数据 | MOD-INF-015 System Telemetry | 遥测格式变更必须同步 |
| CT-AO-DB-001 | 数据域 | 审计总控→Database 双库路由集成 | MOD-DATABASE Database v3.0 | Database DDL 变更必须同步 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-027 版本更新 | 蓝图升级 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | MOD-INF-027 版本更新 | 蓝图升级 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 新增容量升级组件依赖 | 新组件 |
| 4 | Skill 注册 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | audit-orchestrator skill | AI 发现 |
| 5 | MCP Server | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | 新增 3 个 MCP Tool | API 集成 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | Doom Loop 修复循环 | 中 | 高 | max_global_rounds=3 + NonConvergenceHandler | 风险 |
| 2 | 孤儿误判 | 低 | 高 | Git pre-tag 可回滚 + OrphanJudge SafetyFence | 风险 |
| 3 | 语义审计误报 | 低 | 中 | 触发条件 100% 机械判定 | 风险 |
| 4 | 审计性能瓶颈 | 中 | 中 | 增量 Hash + ThreadPoolExecutor + 双池 | 风险 |
| 5 | 100 AI 触发风暴 | 高 | 高 | Coalescer 去重 + AdmissionController 限流 | 风险 |
| 6 | 全量扫描 3.5h 超时 | 中 | 中 | ShardExecutor 分片 + 缓存命中 >80% | 风险 |
| 7 | 增量缓存损坏 | 低 | 中 | 自动退回全量模式 | 风险 |
| 8 | 跨蓝图接口不兼容 | 中 | 高 | 跨蓝图对齐验证矩阵 | 风险 |
| 9 | SQLite 依赖增加运维复杂度 | — | 中 | SQLite WAL 模式成熟稳定，单写者模式简单 | 负面后果 |
| 10 | 双池调度增加调试难度 | — | 中 | CapacityPlanner 水位监控 + LiveScoreboard 实时观测 | 负面后果 |
| 11 | Session 隔离增加内存开销（~61MB 共享缓存） | — | 低 | 64GB 内存中可忽略 | 负面后果 |
| 12 | 准入控制可能误拒合法请求 | 中 | 中 | Token Bucket burst=30 余量 + HALF_OPEN 恢复 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 5 Phase（Phase 0-Prep + Phase 0-3） |
| 施工模式 | 扩展 |
| 核心风险 | 容量升级组件与现有 v4.0.0 基础设施的兼容性 |
| 目标 generation | 6 — 本次施工将蓝图从 generation 5 升级到 generation 6 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | Database v3.0 Phase 3A (DDL) 已完成 | hard | ☐ | ☐ |
| 2 | MOD-INF-028 SemanticAuditor 容量审查完成 | hard | ✅ | ✅ |
| 3 | MOD-INF-026 AssetInventory 容量审查完成 | hard | ✅ | ✅ |
| 4 | Owner 确认 6 项缺口补全方案 | hard | ☐ | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。

#### Phase 0-Prep：容量审计补全

| 步骤 | 产出位置 | 验收标准 | 验证命令 |
|------|---------|---------|---------|
| P0-01: AuditAdmissionController | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\admission.py` | Token Bucket + Circuit Breaker 双检 | `python -m pytest tests/audit-orchestrator/test_admission.py -v` |
| P0-02: CT-AO-DB-001 契约定义 | Database 蓝图 §26 | 契约文档同步 | 人工审查 |
| P0-03: ScriptTimeoutPolicy | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\timeout_policy.py` | 三级渐进降级 | `python -m pytest tests/audit-orchestrator/test_timeout_policy.py -v` |
| P0-05: 审计事件写入吞吐量验证 | — | 900 条/批 < 1s | 基准测试 |
| P0-06: AuditOrchestratorBootstrapCache | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\bootstrap_cache.py` | 100 Session 冷启动 < 3s | `python -m pytest tests/audit-orchestrator/test_bootstrap_cache.py -v` |

#### Phase 0：容量地基

| 步骤 | 产出位置 | 验收标准 | 验证命令 |
|------|---------|---------|---------|
| 0.1: ModuleGraph 构建器 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\module_graph.py` | 1.5K 模块索引 < 10s | `python -m pytest tests/audit-orchestrator/test_module_graph.py -v` |
| 0.2: HashStore (SQLite) | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\hash_store.py` | WAL 模式，100 并发读 | `python -m pytest tests/audit-orchestrator/test_hash_store.py -v` |
| 0.3: ProtectionIndex (L0) | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\protection_index.py` | < 500us per check | 基准测试 |

#### Phase 1：并发核心

| 步骤 | 产出位置 | 验收标准 | 验证命令 |
|------|---------|---------|---------|
| 1.1: 双池异步调度 + ResourceRouter | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\pool\` | CPU 池 12 + I/O 池 30 | `python -m pytest tests/audit-orchestrator/test_pool.py -v` |
| 1.2: 四级优先级队列 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\priority_queue.py` | P0_SEC 抢占 | `python -m pytest tests/audit-orchestrator/test_priority_queue.py -v` |
| 1.3: Coalescer | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\coalescer.py` | 5s 窗口去重 | `python -m pytest tests/audit-orchestrator/test_coalescer.py -v` |
| 1.4: StreamCollector | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\scoreboard.py` | P0 实时推送 | `python -m pytest tests/audit-orchestrator/test_scoreboard.py -v` |

#### Phase 2：全量与知识

| 步骤 | 产出位置 | 验收标准 | 验证命令 |
|------|---------|---------|---------|
| 2.1: ShardExecutor | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\full_scan.py` | --shard N/M 分片 | `python -m pytest tests/audit-orchestrator/test_full_scan.py -v` |
| 2.2: CheckpointManager | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\checkpoint.py` | 断点续跑 | `python -m pytest tests/audit-orchestrator/test_checkpoint.py -v` |
| 2.3: CapacityPlanner | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\capacity_planner.py` | 显式预算 + 安全水位 | `python -m pytest tests/audit-orchestrator/test_capacity_planner.py -v` |

#### Phase 3：体验与观测

| 步骤 | 产出位置 | 验收标准 | 验证命令 |
|------|---------|---------|---------|
| 3.1: 细粒度锁 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\locks.py` | ModuleLock + FileLock | `python -m pytest tests/audit-orchestrator/test_locks.py -v` |
| 3.2: 聚合遥测 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\telemetry.py` | 模块级 + 维度级聚合 | `python -m pytest tests/audit-orchestrator/test_telemetry.py -v` |
| 3.3: 增量默认模式短路 | 修改 TriageScheduler | L2 默认入口 | `python -m pytest tests/audit-orchestrator/test_triage.py -v` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| Phase 0-Prep | AdmissionController 限流过严 | 调高 rate/burst 参数 |
| Phase 0 | HashStore 迁移失败 | 保留 hash_index.json 回退 |
| Phase 1 | 双池调度死锁 | 回退到 ThreadPoolExecutor(max_workers=8) |
| Phase 2 | 分片扫描结果不一致 | 禁用分片，回退单体全扫 |
| Phase 3 | 细粒度锁性能差 | 回退全局锁 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 容量升级组件 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\` | ☐ | ☐ | ☐ |
| 2 | 测试代码 | `D:\ZephyrAlpha\tests\audit-orchestrator\` | ☐ | ☐ | ☐ |
| 3 | 缓存数据目录 | `D:\ZephyrAlpha\data\audit_cache\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块数 | 51 | module_registry.yaml |
| 治理脚本 | 268 | script-manifest.yaml |
| AI 并发 | 1 | 运行时观测 |
| 脚本并发 | 8 | TriageScheduler max_workers |
| 增量扫描 | ~秒级 | 计时 |
| 内存峰值 | 未约束 | psutil |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | max_workers=8 硬编码 | ResourceAwarePool 双池 40-100 动态 | 脚本 > 100 |
| GAP-002 | audit_type 粗粒度分流 | ScriptRouter 文件→脚本精准路由 | 模块 > 100 |
| GAP-003 | 全局锁 audit-global.lock | SessionAuditManager 会话级隔离 | AI > 1 |
| GAP-004 | 86 脚本手工注册 | ScriptDiscovery @audit 注解自动发现 | 脚本 > 200 |
| GAP-005 | hash_index.json 单文件 | SQLite HashStore WAL 模式 | 脚本 > 500 |
| GAP-006 | 文件拓扑排序 | ScriptDAG 脚本级依赖图 + 波次并行 | 脚本 > 1000 |
| GAP-007 | run_all.py 单体全扫 | ShardExecutor 模块级分片并行 | 模块 > 500 |
| GAP-008 | 无资源预算 | CapacityPlanner CPU/内存/GPU 配额 | AI > 10 |
| GAP-009 | 批式结果收集 | LiveScoreboard 流式聚合 | AI > 10 |
| GAP-010 | PatternLearner 内存模式 | PatternDB SQLite 持久化 | 审计历史 > 30 天 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v4.0.0 | 5 | 基线 | 四阶段架构 + 三子系统 + 17 维度 | ✅ |
| v5.0.0 | 5 | 容量升级 | 10 GAP + 6 缺口补全 | ⚠️ |
| v6.0.0 | 6 | 蓝图规格化 | v3.3 模板合规 + Layer 2 砍削 | ⚠️ |
| v6.1.0 | 6 | 模板对齐 | v3.5 模板对齐 + Layer 2 砍削 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | Worker Pool 硬编码→资源感知动态池 | P0 | v5.0.0 | 待施工 |
| GAP-002 | 粗粒度分流→精准路由 | P0 | v5.0.0 | 待施工 |
| GAP-003 | 全局锁→会话级隔离 | P0 | v5.0.0 | 待施工 |
| GAP-004 | 手工注册→自动发现 | P1 | v5.0.0 | 待施工 |
| GAP-005 | JSON→SQLite HashStore | P0 | v5.0.0 | 待施工 |
| GAP-006 | 文件排序→脚本 DAG | P1 | v5.0.0 | 待施工 |
| GAP-007 | 单体全扫→分片并行 | P1 | v5.0.0 | 待施工 |
| GAP-008 | 无预算→CapacityPlanner | P1 | v5.0.0 | 待施工 |
| GAP-009 | 批式→流式聚合 | P2 | v5.0.0 | 待施工 |
| GAP-010 | 内存→SQLite PatternDB | P2 | v5.0.0 | 待施工 |
| 缺口#1 | 系统级准入控制与背压 | P0 | v5.0.0 | 设计完成 |
| 缺口#2 | Database v3.0 双库路由集成契约 | P0 | v5.0.0 | 设计完成 |
| 缺口#3 | 脚本超时渐进式降级 | P1 | v5.0.0 | 设计完成 |
| 缺口#4 | 跨蓝图容量对齐验证矩阵 | P1 | v5.0.0 | 设计完成 |
| 缺口#5 | 审计事件写入吞吐量估算 | P2 | v5.0.0 | 设计完成 |
| 缺口#6 | 100 Session 冷启动优化 | P2 | v5.0.0 | 设计完成 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ResourceAwarePool | GAP-001 | `pool/` | Phase 1 | 待施工 |
| ScriptRouter | GAP-002 | `router.py` | Phase 1 | 待施工 |
| SessionAuditManager | GAP-003 | `session_mgr.py` | Phase 1 | 待施工 |
| ScriptDiscovery | GAP-004 | `discovery.py` | Phase 0 | 待施工 |
| HashCacheDB | GAP-005 | `cache_db.py` | Phase 0 | 待施工 |
| ScriptDAG | GAP-006 | `script_dag.py` | Phase 1 | 待施工 |
| FullScanOrchestrator | GAP-007 | `full_scan.py` | Phase 2 | 待施工 |
| GPUMonitor | GAP-008 | `pool/gpu.py` | Phase 2 | 待施工 |
| LiveScoreboard | GAP-009 | `scoreboard.py` | Phase 1 | 待施工 |
| PatternDB | GAP-010 | `knowledge/pattern_db.py` | Phase 2 | 待施工 |
| AuditAdmissionController | 缺口#1 | `admission.py` | Phase 0-Prep | 待施工 |
| ScriptTimeoutPolicy | 缺口#3 | `timeout_policy.py` | Phase 0-Prep | 待施工 |
| AuditOrchestratorBootstrapCache | 缺口#6 | `bootstrap_cache.py` | Phase 0-Prep | 待施工 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> 本节同时覆盖原 §7 备选方案——§18 的"选项"列已包含备选方案信息。
> 本节同时覆盖原 §15 后果——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-AO-01 | 四阶段闭环（非六阶段） | 六阶段/四阶段 | 四阶段 | Git 快照并入修复前置，收敛并入验证阶段 | 2026-05-08 |
| 2 | D-AO-02 | SemanticAuditor 升为 peer 服务 | 子系统/peer | peer | 语义审计独立演进，belongs_to=null | 2026-05-08 |
| 3 | D-AO-03 | SQLite 替代 JSON 缓存 | JSON/Redis/SQLite | SQLite | 零依赖 + WAL 并发读 + 单写者 | 2026-05-08 |
| 4 | D-AO-04 | ThreadPoolExecutor 替代 multiprocessing | 线程/进程 | 线程 | I/O 密集型 GIL 无影响，轻量 | 2026-05-08 |
| 5 | D-AO-05 | 增量=默认主模式 | 增量/全量同等 | 增量优先 | 日常 95% 场景增量，全量仅周检 | 2026-05-08 |
| 6 | D-AO-06 | 双池异步替代单池 | 单池/双池 | 双池 | CPU 密集与 I/O 密集隔离，防饿死 | 2026-05-08 |
| 7 | D-AO-07 | Token Bucket 准入控制 | 无/令牌桶 | 令牌桶 | 100 AI 并发必须限流 | 2026-05-12 |
| 8 | D-AO-08 | 脚本超时三级降级 | 硬超时/渐进式 | 渐进式 | LOG→DEGRADE→DISABLE 避免反复浪费 | 2026-05-12 |
| 9 | D-AO-09 | SessionAuditManager 会话级隔离 | 全局锁+队列化/会话级隔离 | 会话级隔离 | 100 AI 并发下全局锁退化为串行 | 2026-05-14 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于施工声明——AI 进入蓝图修改/施工时必读。永久保留在蓝图中。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径的基准在哪 | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 每次新 session 是零记忆 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | 决策过程是草稿的事——蓝图是施工依据 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范 | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界在哪 | 范围漂移 |
| 6 | **容量估算必须写** | AI 不知道系统能容纳多少 | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | AI 不知道旧东西怎么处理 | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令 | 执行漂移 |
| 9 | **蓝图必须自包含** | AI 可能不读引用的文件 | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 没有git备份，删除不可逆 | 永久丢失 |
| 11 | **construction_progress 必须与代码实际状态一致** | 标completed但代码不存在=虚假进度 | 误导下一个 AI |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 路径不一致=AI找不到代码 | 搜索失败 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是 SSoT，蓝图复制代码=双源漂移 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不同的内容强行塞一个蓝图=职责不清 | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

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
| 审计编排器中"容量升级组件"（16个GAP+6个缺口） | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 审计编排器中"Provider Table"（86脚本映射） | **原地** | Provider 是审计编排的核心数据，不是独立子系统 |
| 审计编排器中"SemanticAuditor peer 服务" | **拆分** | 独立 module_id (MOD-INF-028) + 独立 Phase + depends_on 交集 <30% |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于施工声明——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 安全删除方案 |
|---|---------------|------------|---------|------------|
| 1 | hash_index.json | `D:\ZephyrAlpha\data\audit_cache\hash_index.json` | 迁移型 | SQLite 迁移完成→交叉验证→标记 deprecated→Phase 4 物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于施工声明——AI 进入蓝图时必读。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

> **时态属性**：本节属于施工声明——防重复检查。永久保留在蓝图中。

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | SemanticAuditor | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` | 语义审计 | peer 服务，非子模块，独立演进 |
| 2 | BehavioralAuditor | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\` | 行为审计 | peer 服务，由 MOD-INF-033 定义 |
| 3 | run_all.py | `D:\ZephyrAlpha\scripts\governance\run_all.py` | 全量审计入口 | Orchestrator 编排它，不替代它 |

---

## 涉及的文件范围

> **时态属性**：本节属于施工声明——防范围漂移。永久保留在蓝图中。

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 审计编排器代码 | `D:\ZephyrAlpha\src\zephyr\audit-orchestrator\` | 修改 | 新增容量升级组件 |
| 2 | 审计测试 | `D:\ZephyrAlpha\tests\audit-orchestrator\` | 修改 | 新增测试 |
| 3 | 审计缓存 | `D:\ZephyrAlpha\data\audit_cache\` | 修改 | SQLite 迁移 |
| 4 | 审计历史 | `D:\ZephyrAlpha\data\audit_history\` | 修改 | 新增趋势数据 |
| 5 | MCP Server | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | 修改 | 新增 MCP Tool |
| 6 | Skill 注册 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 修改 | 新增 skill |
| 7 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | 版本更新 |
| 8 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 修改 | 新增依赖 |

---

## 治理信息

> **时态属性**：本节属于施工声明——声明蓝图的治理边界和变更规则。永久保留在蓝图中。

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图的核心架构设计 | **本文档 §1-§10** | 已废弃的旧蓝图 |
| 本模块的施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块的接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| Provider Table | **本文档蓝图特有章节** | 旧版静态列表 |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-FEEDBACK_LOOP Feedback Loop 蓝图 | §4 接口契约、§10 依赖关系 |
| Tier 1 | MOD-INF-030 RedBlue Validator 蓝图 | §4 接口契约 |
| Tier 2 | MCP Governance Server | §4.5 MCP 接口 |
| Tier 2 | Pipeline Orchestrator | §12 集成点 |
| Tier 3 | `src/zephyr/audit-orchestrator/` 代码文件 | §4 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

---

## 蓝图特有章节

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：三子系统架构、维度体系、Provider 映射、容量升级参数是审计编排器独有的设计
> 不可砍理由：砍掉后 AI 无法理解审计编排器的核心设计——三子系统如何分流、17 维度如何映射、86 个 Provider 脚本如何路由

### 三子系统审计架构

| 审计类型 | 输入 | 判定 | 确定性 | LLM 依赖 | 修复方式 |
|---------|------|------|:------:|:-------:|---------|
| Structural | Any file (.py/.yaml/.md) | Boolean: exists/∈/==/< | 100% | Zero | Template |
| Semantic | Rule documents only (.md/.yaml) | Natural language semantics | 95~98% | Core | LLM generated |
| Behavioral | AI action logs (AuditTrail) | Auth boundary vs actual behavior | High | Optional | Block/alert/rollback |

### MAPE-K 映射

| MAPE-K 层 | MDIAE 映射 | 组件 |
|-----------|-----------|------|
| Monitor | Phase 1 发现 + §21 遥测 | DiscoveryEngine + TelemetryCollector |
| Analyze | Phase 2 审计 | DimensionChecker + dispatches to SemanticAuditor |
| Plan | Phase 3 修复判定 | OrphanJudge 三决策树 |
| Execute | Phase 3 修复执行 + Phase 4 红白对抗 | AutoFixEngine + RedBlueValidator |
| Knowledge | §17 知识积累 | PatternLearner + RuleEvolver + FixTemplateDB |

### 六层触发模型

| Layer | When | Triggered By | What Audits | Script |
|:---:|------|-------------|------------|:---:|
| L0 | Before every AI write/delete | AI auto-invoke | Safety redlines (anchor/path/Gate) | `pre_op_check.py` |
| L1 | Every AuditTrail event | AuditTrail event stream | Behavioral (authorization boundary) | MOD-INF-033 |
| L2 | Every AI Session end | Session lifecycle hook | Structural + Semantic, incremental | `run_incremental.py` |
| L3 | Daily/Weekly scheduled | Cron | Full tri-audit + full repair | `run_all.py` |
| L4 | Git commit/push/merge | Git hooks | Security + Registration + Dependencies | `run_all.py --dimensions` |
| L5 | Developer manual | CLI | Any | All scripts |

### 17 结构维度

| dim_id | 名称 | 切法 | 审计内容 | Provider 数 | 收敛 |
|--------|------|------|---------|:---:|:---:|
| DIM-PATH-001 | 文件路径强制合规 | 路径切 | 21 种文件类型强制路径 / 废弃路径 / 根目录白名单 | 7 | 1 |
| DIM-TYPE-001~003 | 注册完整性 & Gate | 横切 | .py/gate/规则文件注册 / 去重 / 一致性 | 8 | 2 |
| DIM-CODE-001 | 代码施工标准 | 代码切 | __init__.py / 类型注解 / import / SSoT 守卫 | 17 | 2 |
| DIM-SECURITY-001 | 安全红线 | 安全切 | 零密钥 / 零 shell=True / 锚点零删除 | 12 | 1 |
| DIM-DEP-001 | 依赖完整性 | 交叉切 | depends_on 存在 / 版本一致 / DAG | 9 | 1 |
| DIM-NAMING-001 | 命名规范 | 命名切 | kebab-case / 禁止版本后缀 / module_id 格式 | 2 | 2 |
| DIM-SCALE-001 | 规模漂移 | 规模切 | 目录平铺计数 / churn / max-depth | 3 | 1 |
| DIM-KBG-001 | KB 决策记录 文档链 | KB 决策记录切 | 编号连续 / 洋葱引用 / frontmatter status | 2 | 1 |
| DIM-CONSTRUCTION-001 | 施工进度 | 施工切 | 蓝图 vs 进度一致 / milestone 不倒退 | 3 | 1 |
| DIM-LIFECYCLE-001 | 生命周期状态机 | 状态切 | 8 态合法值 / 状态迁移路径 | 4 | 1 |
| DIM-DOC-001 | 文档合规 | 文档切 | frontmatter / 模板章节 / 编码 UTF-8 | 3 | 1 |
| DIM-ARCH-001 | 架构结构 | 结构切 | LPC 双轨 / 层一致性 / 依赖方向 | 6 | 1 |
| DIM-SESSION-001 | Session 质量 | 会话切 | Log 字段 / 边界规则 / handoff | 4 | 1 |
| DIM-DIR-001 | Governance 目录 | 竖切 | scripts/governance/ 结构合规 | 1 | 1 |
| DIM-FIELD-001 | Owner 字段 | 字段切 | 所有 YAML owner 有效性 | 1 | 1 |

**总计**: 17 维度 × 86 Provider 脚本 + 6 聚合器。

### Provider Table（完整脚本映射）

#### DIM-PATH-001: 文件路径强制合规

| Provider Script | Description | Priority |
|------|------|:---:|
| `scripts/governance/d1_structure/detect_orphan_py.py` | 根目录 .py 孤儿检测 | P0 |
| `scripts/governance/d4_paths/detect_ruins_references.py` | 废弃路径引用检测 | P0 |
| `scripts/governance/verify_file_paths.py` | 21+ 文件类型路径验证 | P0 |
| `scripts/governance/d5_architecture/validators/validate_directory_structure.py` | 目录树验证 | P0 |
| `scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py` | 嵌套/平铺违规 | P1 |
| `scripts/governance/d5_architecture/validators/validate_blueprint_placement.py` | 蓝图位置验证 | P1 |
| `scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_path_consistency.py` | 蓝图路径一致性 | P1 |

#### DIM-TYPE-001~003: 注册完整性 & Gate

| Provider Script | Description | Priority |
|------|------|:---:|
| `scripts/governance/d11_compliance/audit_registration.py` | AST __all__ 提取 | P0 |
| `scripts/governance/check_registry_consistency.py` | 跨注册表一致性 | P0 |
| `scripts/governance/d5_architecture/validators/validate_ssot.py` | SSoT 验证 | P0 |
| `scripts/governance/d5_architecture/validators/validate_gate_yaml.py` | Gate YAML 验证 | P0 |
| `scripts/governance/d5_architecture/validators/validate_blind_spot_status.py` | 盲点注册状态 | P1 |
| `scripts/governance/d5_architecture/validators/validate_authority_registry.py` | 权限注册完整性 | P1 |
| `scripts/governance/d5_architecture/validators/validate_field_ownership.py` | 字段所有权审计 | P1 |
| `scripts/governance/d5_architecture/validators/yaml_md/validate_yaml_interface_uniqueness.py` | YAML 接口唯一性 | P1 |

#### DIM-CODE-001: 代码施工标准

| Provider Script | Description | Priority |
|------|------|:---:|
| `scripts/governance/fix_orphan_exports.py` | 修复未导出模块 | P0 |
| `scripts/governance/d1_structure/detect_residual_files.py` | 残留文件检测 | P0 |
| `scripts/governance/d7_code/validate_init_all.py` | __init__.py 导出验证 | P0 |
| `scripts/governance/d7_code/validate_import_style.py` | import 风格验证 | P0 |
| `scripts/governance/d7_code/validate_python_syntax.py` | Python 语法验证 | P0 |
| `scripts/governance/d7_code/validate_type_annotation_coverage.py` | 类型注解覆盖 | P1 |
| `scripts/governance/d7_code/validate_docstring_coverage.py` | docstring 覆盖 | P1 |
| `scripts/governance/d7_code/validate_test_coverage.py` | 测试覆盖 | P1 |
| `scripts/governance/d7_code/validate_test_assertion_depth.py` | 测试断言深度 | P1 |
| `scripts/governance/d7_code/detect_absolute_path_hardcoding.py` | 绝对路径硬编码 | P0 |
| `scripts/governance/d7_code/check_encoding.py` | 编码验证 | P0 |
| `scripts/governance/d7_code/check_idempotency.py` | 幂等性检查 | P1 |
| `scripts/governance/d7_code/validate_fle_imports.py` | FLE import 验证 | P1 |
| `scripts/governance/d7_code/validate_contracts_purity.py` | 契约纯度检查 | P1 |
| `scripts/governance/d7_code/detect_pydantic_any_fields.py` | Pydantic Any 字段检测 | P1 |
| `scripts/governance/d7_code/detect_missing_encoding.py` | 缺失编码声明 | P0 |
| `scripts/governance/d7_code/check_pit_compliance.py` | PIT 合规 | P1 |

#### DIM-SECURITY-001: 安全红线

| Provider Script | Description | Priority |
|------|------|:---:|
| `scripts/governance/d6_security/detect_secrets.py` | 密钥检测 | P0 |
| `scripts/governance/d6_security/detect_shell_true.py` | shell=True 检测 | P0 |
| `scripts/governance/d6_security/detect_shell_dangerous.py` | 危险命令检测 | P0 |
| `scripts/governance/d6_security/scan_secret_leak.py` | 密钥泄漏扫描 | P0 |
| `scripts/governance/d6_security/scan_runtime_log_secrets.py` | 运行日志密钥扫描 | P0 |
| `scripts/governance/d6_security/check_protected_paths.py` | 保护路径检测 | P0 |
| `scripts/governance/d6_security/detect_anchor_file_deletion.py` | 锚点文件删除检测 | P0 |
| `scripts/governance/d6_security/detect_permanent_file_deletion.py` | 永久删除检测 | P0 |
| `scripts/governance/d6_security/detect_git_dangerous.py` | 危险 git 操作检测 | P0 |
| `scripts/governance/d6_security/detect_keywords_in_logs.py` | 日志敏感词检测 | P1 |
| `scripts/governance/d6_security/detect_threading_lock.py` | 线程安全锁检测 | P1 |
| `scripts/governance/d6_security/validate_gate_discipline.py` | Gate 纪律验证 | P0 |

#### DIM-DEP-001: 依赖完整性

| Provider Script | Description | Priority |
|------|------|:---:|
| `scripts/governance/d9_knowledge/detect_orphan_documents.py` | 孤儿文档检测 | P1 |
| `scripts/governance/d5_architecture/detectors/detect_depends_on_cycles.py` | 循环依赖检测 | P0 |
| `scripts/governance/d5_architecture/validators/validate_depends_on_format.py` | depends_on 格式验证 | P0 |
| `scripts/governance/d5_architecture/checkers/check_dependency_direction.py` | 依赖方向验证 | P0 |
| `scripts/governance/d5_architecture/analyzers/audit_depends_on_chain_depth.py` | 依赖链深度审计 | P1 |
| `scripts/governance/d5_architecture/validators/validate_dag.py` | DAG 验证 | P0 |
| `scripts/governance/crosschecksystem_master_deps.py` | SYS-MASTER 依赖交叉检查 | P1 |
| `scripts/governance/d5_architecture/validators/validate_interface_contracts.py` | 接口契约验证 | P1 |
| `scripts/governance/d5_architecture/validators/validate_p0_module_contracts.py` | P0 模块契约验证 | P1 |

#### DIM-NAMING-001 / DIM-SCALE-001 / DIM-KBG-001 / DIM-CONSTRUCTION-001 / DIM-LIFECYCLE-001 / DIM-DOC-001 / DIM-ARCH-001 / DIM-SESSION-001

| Provider Script | Dimension | Description | Priority |
|------|------|------|:---:|
| `scripts/governance/d11_compliance/validate_script_naming.py` | NAMING | 脚本命名规范 | P0 |
| `scripts/governance/d5_architecture/detectors/detect_duplicate_module_names.py` | NAMING | 重复模块名检测 | P0 |
| `scripts/governance/d5_architecture/validators/yaml_md/validate_md_yaml_number_drift.py` | SCALE | 数值漂移检测 | P1 |
| `scripts/governance/d5_architecture/validators/validate_layer_consistency.py` | SCALE | 层一致性验证 | P1 | ❌ 已删除（2026-07-09死代码清理） |
| `scripts/governance/d5_architecture/validators/validate_blueprint_code_sync.py` | SCALE | 蓝图代码同步 | P1 |
| `scripts/governance/d5_architecture/validators/validate_adr_frontmatter_consistency.py` | KB 决策记录 | KB 决策记录 frontmatter 一致性 | P1 |
| `scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py` | KB 决策记录 | 废弃 KB 决策记录 引用检测 | P1 |
| `scripts/governance/d5_architecture/validators/validate_ssot_construction_progress.py` | CONSTRUCTION | 施工进度 SSoT | P1 |
| `scripts/governance/construction_gate.py` | CONSTRUCTION | 施工门禁 | P0 |
| `scripts/governance/d5_architecture/validators/validate_code_yaml_alignment.py` | CONSTRUCTION | 代码 YAML 对齐 | P1 |
| `scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py` | LIFECYCLE | 模块生命周期验证 | P1 |
| `scripts/governance/d5_architecture/validators/lifecycle/validate_lifecycle_refs.py` | LIFECYCLE | 生命周期引用验证 | P1 |
| `scripts/governance/d5_architecture/validators/lifecycle/validate_phase_transition.py` | LIFECYCLE | 阶段迁移合法性 | P1 |
| `scripts/governance/d8_doc_sync/validate_document_lifecycle.py` | LIFECYCLE | 文档生命周期验证 | P1 |
| `scripts/governance/d8_doc_sync/validate_document_ttl.py` | DOC | 文档 TTL 检测 | P1 |
| `scripts/governance/d8_doc_sync/detect_dated_snapshots.py` | DOC | 过期快照检测 | P1 |
| `scripts/governance/d8_doc_sync/detect_ai_products_in_docs.py` | DOC | AI 产物检测 | P1 |
| `scripts/governance/d5_architecture/validators/validate_architecture_contract_internal.py` | ARCH | 架构内部契约 | P0 |
| `scripts/governance/d5_architecture/validators/validate_layer_deps.py` | ARCH | 层依赖验证 | P0 | ❌ 已删除（2026-07-09死代码清理） |
| `scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` | ARCH | 契约代码漂移 | P0 |
| `scripts/governance/d5_architecture/validators/validate_load_path_integrity.py` | ARCH | 加载路径完整性 | P1 |
| `scripts/governance/d5_architecture/validators/validate_three_way_consistency.py` | ARCH | 三方一致性 | P1 |
| `scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py` | ARCH | 静态清单漂移 | P1 |
| `scripts/governance/d12_ai_hallucination/validate_session_gate_check.py` | SESSION | Session 门禁检查 | P1 |
| `scripts/governance/d12_ai_hallucination/validate_session_budget.py` | SESSION | Session 预算验证 | P1 |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py` | SESSION | Session 日志索引完整性 | P1 |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_updated.py` | SESSION | Session 日志新鲜度 | P1 |

#### 聚合器

| Provider Script | Description | Priority |
|------|------|:---:|
| `scripts/governance/run_all.py` | 全量审计入口 | P0 |
| `scripts/governance/run_incremental.py` | 增量审计入口 | P0 |
| `scripts/governance/pre_op_check.py` | L0 实时阻断 | P0 |
| `scripts/governance/ci_self_check.py` | CI 自检 | P0 |
| `scripts/governance/_e2e_verify.py` | E2E 验证 | P1 |
| `scripts/governance/status.py` | 审计状态概览 | P1 |

### v5.0.0 容量升级核心设计

#### 双池异步并发架构

| 配置项 | 值 | 说明 |
|--------|:---:|------|
| cpu_pool_max | 12 | P-core 数量，AST/syntax/security |
| io_pool_max | 30 | I/O 密集型，线程几乎不消耗 CPU |
| total_max_concurrent | 40~100 | 动态上限，受 CapacityPlanner 约束 |
| per_script_timeout | 30s | 单脚本超时 |
| adaptive_scaling | true | 空闲扩容 I/O 池到 50，CPU>80% 缩容到 8 |

#### 四级优先级队列

| 级别 | 脚本类型 | 调度策略 |
|------|---------|---------|
| P0_SEC | detect_secrets / detect_shell_true / detect_anchor_file_deletion | 立即调度，抢占式 |
| P0 | audit_registration / check_registry_consistency / validate_gate_yaml | 优先于 P1，不可抢占 |
| P1 | validate_type_annotation / validate_docstring_coverage | 正常排队 |
| OPT | 非关键维度 / DORA / Meta-Audit | skip-on-saturation |

#### ScriptRouter 三层路由

| 层级 | 策略 | 覆盖 |
|------|------|------|
| L1 | PATH-BASED glob 模式→脚本映射 | 80% |
| L2 | EXTENSION-BASED 后缀→脚本映射 | 15% |
| L3 | CROSS-CUT always-run 脚本 | 5% |

#### 准入控制五层架构

| 层 | 组件 | 参数 |
|---|------|------|
| L1 | AdmissionController | Token Bucket rate=10/s, burst=30 |
| L2 | Coalescer | 5s 窗口模块级去重 |
| L3 | PriorityQueue | max_size=1,500 |
| L4 | Worker Pool | semaphore(40-100) |
| L5 | Circuit Breaker | error_rate>50%→OPEN, 60s→HALF_OPEN |

#### 容量参数

| 参数 | 值 | 推导 |
|------|:---:|------|
| admit_rate | 10/s | 100 AI 有效触发率约 5-15/s |
| admit_burst | 30 | 极端瞬间余量 |
| cb_failure_threshold | 50% | 超半脚本失败→全局暂停 |
| cb_recovery_timeout | 60s | 系统恢复时间 |
| coalesce_window_ms | 5000 | 去重窗口 |
| max_coalesce_files | 500 | 超过升级为 sharded mini-full |
| eager_security | true | P0_SEC 不参与去重 |

#### Database 集成契约 CT-AO-DB-001

| 写入路径 | 目标 | 路由 | 吞吐目标 |
|---------|------|------|---------|
| audit_report | audit_reports 表 | get_depgraph_pg_connection()（PG，WriteBatcher 暂缓/待 M-1 级） | ~500 writes/s（待 L 级） |
| hash_cache | SQLite hash_cache.db（本地） | 本地直写 | — |
| script_executions | script_executions 表 | get_depgraph_pg_connection()（PG，WriteBatcher 暂缓/待 M-1 级） | ~500 writes/s（待 M-1 级） |
| pattern_db | SQLite patterns.db（本地） | 单写者 | — |

#### 脚本超时渐进式降级

| 次数 | 行为 |
|------|------|
| 第1次 | TIMEOUT_LOG——标记慢脚本 |
| 第2次 | TIMEOUT_DEGRADE——从 Session 增量列表移除 |
| 第3次 | TIMEOUT_DISABLE——全局禁用，告警 Owner |

#### 冷启动共享缓存

| 共享组件 | 内存占用 | 说明 |
|---------|:---:|------|
| ScriptRouter（单例） | ~50 MB | glob 索引 + 10K 脚本路由表 |
| ProtectionIndex（单例） | ~10 MB | 锚点哈希集 + 保护路径正则 |
| CapacityPlanner（单例） | ~1 MB | 预算配置 |
| **总计** | **~61 MB** | 64GB 内存中可忽略 |

#### 硬件验证

| 验证项 | 预算 | 够用 | 说明 |
|--------|------|:---:|------|
| CPU | 12 P-core + 8 E-core = 20 线程 | YES | AST 用 P-core，文件扫描用 E-core |
| 内存 | 64GB → 审计留 32GB | YES | Python 进程 + HashStore mmap |
| 磁盘 I/O | NVMe 500K IOPS | YES | 10K 脚本全并发 ~100K IOPS |
| GPU | 3090 24GB | YES | SemanticAuditor LLM ~4GB VRAM |
| 增量延迟 | ModuleGraph <1ms + 队列 <100ms + 15-30 脚本 <60s | YES | 核心路径纯 CPU/内存 |

#### 审计事件吞吐量

| 事件类型 | 100 AI 峰值 | 日均 | WriteBatcher 承载 |
|---------|:---:|:---:|:---:|
| AuditReport | 30 | ~300 | ✅ |
| Finding | ~900 | ~9,000 | ✅ |
| ScriptExecution | ~900 | ~9,000 | ✅ |
| Hash 缓存更新 | ~900 | ~9,000 | ✅ SQLite 本地 |
| PatternDB 更新 | ~150 | ~1,500 | ✅ SQLite 本地 |

#### 跨蓝图对齐矩阵

| 审计总控依赖 | 对端模块容量升级 | 接口契约 | 兼容性 |
|-------------|----------------|---------|:---:|
| ScriptScheduler (MOD-INF-005) | §〇-B 并发 | CT-AO-SS-001 | ✅ |
| DualDBRouter (MOD-DATABASE) | §23+§24 | CT-AO-DB-001 | ❌ 已裁定删除，由 get_depgraph_pg_connection()（PG）+ get_db_connection()（SQLite）双入口覆盖 |
| BehavioralAuditor (MOD-INF-033) | §3.1 并行消费 | CT-BEH-* | ✅ |
| SemanticAuditor (MOD-INF-028) | v5.0.0 完整方案 | CT-SEM-001 | ✅ |
| AssetInventory (MOD-INF-026) | v3.0.0 容量升级 | CT-AO-AI-001 | ✅ |

### 成功指标

| 指标 | v4.0.0 | v5.0.0 目标 | 测量方式 |
|------|:---:|:---:|------|
| 脚本注册上限 | 86(手工) | 10,000(自动) | ScriptInventory.count |
| 最大并发 | 8(硬编码) | 40~100(自适应) | ResourceAwarePool.active_workers |
| 增量扫描耗时 | ~秒级 | <1 分钟 | LiveScoreboard.duration |
| 全量扫描耗时 | N/A | <3.5 小时 | FullScanOrchestrator.duration |
| 缓存命中率 | >80% | >85% | HashCacheDB.hit_rate |
| 活跃 AI Session | 1(全局锁) | 100(会话隔离) | SessionAuditManager.active_sessions |
| 进程内存峰值 | 未监控 | <48GB | MemoryMonitor.peak |
| 路由查找延迟 | N/A | <100ms | ScriptRouter.route_latency |

### DORA 四指标映射

| DORA 指标 | MDIAE 映射 | 目标 |
|-----------|-----------|------|
| Deployment Frequency | 审计频率 | ≥1/day |
| Change Failure Rate | RED issue / total checks | <5% |
| Mean Time to Recovery | 平均修复轮数 | <3 rounds |
| Lead Time for Changes | 发现→修复完成 | <30min |

### 合规框架映射

| ISO 27001 控制域 | MDIAE 映射 |
|-----------------|-----------|
| A.8.1 资产责任 | DIM-FIELD-001 |
| A.12.1 操作规程 | DIM-TYPE-001 |
| A.12.4 管理员活动日志 | MOD-INF-020 Audit Trail |
| A.12.7 信息系统审计 | DIM-META-001 |

| SOC2 信任服务标准 | MDIAE 映射 |
|-------------------|-----------|
| Security | DIM-TYPE-001~003 |
| Availability | §21 SLO 99% |
| Processing Integrity | MOD-INF-028 |
| Confidentiality | G-CT-001 RBAC |
