---
module_id: MOD-INF-031
submodule_path: src/zephyr/infrastructure/auto_fix_engine
title: "Auto Fix Engine 蓝图 — 自动修复引擎·模板化修复执行"
doc_type: blueprint
status: Active
version: "5.1.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
valid_from: "2026-05-08"
ttl: permanent
construction_progress: design_only
actual_disk_path: "src/zephyr/infrastructure/auto_fix_engine/"
architecture_layer: "L3_执行层"
belongs_to: "MOD-INF-027"
parent_module: "MOD-INF-027"
last_updated: "2026-05-14"
last_verified: "2026-05-14"
generation: 5
functional_domain: governance
codification_level: L1
codification_at: "2026-05-14"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "AutoFixEngine——三通道修复管道（结构→模板化100%确定/语义→LLM Bridge 95~98%置信/行为→Block+Alert永不自动修复）+ 8状态生命周期 + WAL原子修复 + 病因修复法九阶链"
priority: P1
runtime_plane: warm
tags: [auto-fix, repair, zombie-cleanup, dedup-extract, scaffold-register, alignment-sync, fix-validate, audit, self-healing, confidence-gate, fix-budget, cascade-breaker, wal-atomic, drift-fix, rbac-guard, idempotency, conflict-resolution, canary-fix, dead-letter, sandbox, secret-leak, compliance, state-machine, interrupt-safety, event-hooks, fle-integration, preventive-repair, 追问到底, root-cause-analysis, causal-chain, convergence-loop, dual-mode-triage, dimension-fixer-mapping]
depends_on:
  - {target: "MOD-INF-020", at: "full", why: "Audit Trail——每次修复 MUST 记录 before/after 快照"}
  - {target: "MOD-INF-017", at: "§2", why: "Code Dedup Engine——DedupExtractor 的语义相似度引擎 + AutoFixer 安全约束"}
  - {target: "MOD-LLM_SECURITY", at: "§3", why: "LLM Security——L2/L3 LLM 修复文本的安全校验"}
  - {target: "MOD-INF-005", at: "full", why: "Script System——script-manifest.yaml 的注册更新 + Finding AUTO_FIXABLE 枚举"}
  - {target: "MOD-INF-018", at: "full", why: "Agent RBAC——修复操作的七层+六横切面权限校验（G-CT-001）"}
  - {target: "MOD-INF-022", at: "§3", why: "Escalation Protocol——L1_AUTO_FIX 升级路由 + 熔断器 + 委托约束"}
  - {target: "MOD-INF-023", at: "full", why: "Drift Detector——auto_fixable 标记 + 漂移预算联动 + Reconciler 修复闭环"}
  - {target: "MOD-INF-026", at: "§4", why: "Asset Inventory——_auto_fix_orphans() 孤儿注册逻辑收编"}
  - {target: "MOD-INF-027", at: "section 4", why: "Audit Orchestrator (编排)"}
  - {target: "MOD-INF-029", at: "section 4", why: "Orphan Judge (孤儿修复)"}
references:
  - {path: "D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md", section: "REQUIRED_SECTIONS", why: "蓝图模板 v3.5 合规基准"}
  - {path: "D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml", section: "§0.5", why: "压缩工作流标准——Layer 1/2 执行规范"}
  - {id: "MOD-INF-027", at: "full", why: "Audit Orchestrator——AutoFixEngine 作为 Phase 3 修复的核心执行者"}
  - {id: "MOD-INF-029", at: "full", why: "Orphan Judge——EXTRACT_AND_MERGE / REGISTER / DELETE 判决的执行方"}
  - {id: "MOD-INF-030", at: "full", why: "RedBlue Validator——绕过场景修复的执行方"}
  - {id: "MOD-INF-028", at: "§8", why: "Semantic Auditor——L2 LLM 修复的文本生成方"}
  - {id: "MOD-INF-021", at: "§3", why: "Rollback Manager——DriftFixHandler G-CT-005 消费端收编"}
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Auto Fix Engine 蓝图 — 自动修复引擎·模板化修复执行

## 概述

本蓝图描述 AutoFixEngine——ZephyrAlpha 的自动修复引擎。它解决了审计发现问题到自动修复执行的闭环问题。核心职责包括：三通道修复管道（结构→模板化100%确定 / 语义→LLM Bridge 95~98%置信 / 行为→Block+Alert永不自动修复）、8状态修复生命周期、WAL原子修复保证、病因修复法九阶链。当前规模 ~51模块/~268脚本/单Session，目标容量 1500模块/10000脚本/100 AI并发。上游依赖 DriftDetector(MOD-INF-023)/OrphanJudge(MOD-INF-029)/SemanticAuditor(MOD-INF-028) 提供审计发现，下游被 AuditOrchestrator(MOD-INF-027) 消费修复结果。

> module_id: MOD-INF-031 | version: 5.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/auto-fix-engine/ | generation: 5 | construction_progress: design_only

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-031`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §4 | 模块入口 + `__all__` 导出 | 未实现 | |
| 2 | `__main__.py` | §4.5 | CLI 入口 | 未实现 | |
| 3 | `models.py` | §4.2 | 数据模型（FixAction/FixReport/FixHistory 等） | 未实现 | |
| 4 | `engine.py` | §3 | AutoFixEngine 主类 | 未实现 | |
| 5 | `zombie_cleaner.py` | §3 | L1 僵尸引用清理 | 未实现 | |
| 6 | `all_completer.py` | §3 | L1 __all__ 自动补全 | 未实现 | |
| 7 | `dedup_extractor.py` | §3 | L1 重复函数提取 | 未实现 | |
| 8 | `scaffold_registrar.py` | §3 | L1 孤儿文件自动注册 | 未实现 | |
| 9 | `alignment_syncer.py` | §3 | L1 双向对齐差异同步 | 未实现 | |
| 10 | `drift_fixer.py` | §3 | L1 漂移事件自动修复 | 未实现 | |
| 11 | `dep_version_fixer.py` | §3 | L1 依赖版本漂移修复 | 未实现 | |
| 12 | `import_fixer.py` | §3 | L1 损坏 import 修复 | 未实现 | |
| 13 | `config_fixer.py` | §3 | L1 配置漂移修复 | 未实现 | |
| 14 | `llm_fix_adapter.py` | §3 | L2 LLM 修复桥接 | 未实现 | |
| 15 | `self_heal_agent.py` | §3 | L3 Agent 自愈循环 | 未实现 | |
| 16 | `fix_safety.py` | §3 | SafetyGate + LockGuard + WriteSafety + FixValidator + CascadeBreaker + SandboxExecutor + SecretLeakGuard | 未实现 | |
| 17 | `fix_reliability.py` | §3 | IdempotencyGuard + ConflictResolver + FixOrderResolver + FixResultCache + BlastRadiusEstimator + DeadLetterQueue + ApprovalQueue + CanaryFixer | 未实现 | |
| 18 | `fix_budget.py` | §3 | FixBudget + DriftBudgetLink + FixStormGuard + LLMCostEstimator | 未实现 | |
| 19 | `batch_fixer.py` | §3 | 批量修复(ThreadPoolExecutor) | 未实现 | |
| 20 | `shadow_workspace.py` | §3 | 后台预演验证 | 未实现 | |
| 21 | `fix_scheduler.py` | §3 | 修复调度器 | 未实现 | |
| 22 | `fix_health_check.py` | §3 | 健康自检 | 未实现 | |
| 23 | `compliance_auditor.py` | §3 | 合规审计 | 未实现 | |
| 24 | `fix_diff.py` | §3 | Diff 生成 | 未实现 | |
| 25 | `fix_report.py` | §3 | 修复报告 | 未实现 | |
| 26 | `escalation_bridge.py` | §3 | 升级路由桥接 | 未实现 | |
| 27 | `fix_pattern_miner.py` | §3 | 修复模式学习 | 未实现 | |
| 28 | `state_machine.py` | §3.3 | 8 状态修复生命周期 | 未实现 | |
| 29 | `interrupt_guard.py` | §6 | 修复中断安全 | 未实现 | |
| 30 | `event_hooks.py` | §3 | 修复事件钩子 | 未实现 | |
| 31 | `_fixer-registry.yaml` | §4.2 | 修复器注册表 | 未实现 | |
| 32 | `auto_fix_config.yaml` | §5 | 引擎配置 | 未实现 | |
| 33 | `schema.sql` | §4.2 | SQLite Schema | 未实现 | |
| `__main__.py` | § — | — | 已实现 | | 本模块 |
| `__main__.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = design_only → 代码目录不存在或为空 | `ls D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 对比 frontmatter actual_disk_path 与 §11 业务代码路径 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" D:\ZephyrAlpha\src\zephyr\auto-fix-engine\*.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v5.1.0 (当前) | 无（design_only） | 全部 33 个文件 | 待施工 |

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 的审计体系（DriftDetector/SemanticAuditor/OrphanJudge）产出大量审计发现，但修复执行散落在 9 处（`code_dedup_engine/auto_fixer.py`、`behavioral_auditor/reconciler.py`、`asset_inventory/__main__.py._auto_fix_orphans()` 等），缺乏统一安全网、预算控制、幂等保证和冲突解决。旧 `FixDispatcher` 是空壳路由器（if/elif/else），无自有逻辑。

### §1.2 目标

| # | 目标 | 可验证标准 |
|---|------|----------|
| 1 | 统一修复执行中枢——收编 9 处散落 auto-fix 逻辑 | 每个旧入口改为 thin wrapper 调用 AutoFixEngine |
| 2 | 三通道修复管道覆盖三大审计类型 | 结构→模板化100%确定 / 语义→LLM Bridge 95~98%置信 / 行为→Block+Alert永不自动修复 |
| 3 | 8 状态修复生命周期可追踪可恢复可审计 | 每次状态转换写入 AuditTrail |
| 4 | WAL 原子修复——修复要么完整执行要么完全回滚 | 中断后零"半修复"状态 |
| 5 | 修复即证据——每次修改 MUST 附带 before/after 快照 | 审计记录率 100% |
| 6 | 容量支撑 10000 脚本 / 1500 模块 / 100 AI 并发 | 增量扫描 p50 <1min，全量扫描 <3.5h |

### §1.3 不包含的目标

| # | 明确排除 | 原因 | 去哪 |
|---|---------|------|------|
| 1 | 审计发现的具体检测逻辑 | 检测是上游模块职责 | MOD-INF-029/028/023 |
| 2 | LLM 文本生成 | 语义修复由 MOD-INF-028.LLMBridge 执行 | MOD-INF-028 |
| 3 | 行为审计的自动修复 | 行为审计 RED 永不自动修复 | Block+Alert+Rollback |
| 4 | pre-commit 钩子框架 | 已有 `.pre-commit-config.yaml` | 项目根目录 |
| 5 | 容量 SLO 全局注册 | 容量注册由 MOD-INF-001 管理 | MOD-INF-001 §13 |

### §1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 硬件：i7-12700KF (12C20T) + 64GB + 1TB NVMe + RTX 3090 (24GB) | 修复 Worker ≤40 并发，GPU LLM 修复串行化排队 |
| 单机部署，无分布式 | 所有组件在同一台开发机，跨进程用 SQLite WAL + ZephyrLock |
| Python GIL | I/O 密集型用 ThreadPoolExecutor，CPU 密集型用 subprocess 突破 GIL |
| 修复预算有限 | 日度 50 次 / 月度 500 次 / LLM Token 日度 500,000 |

---

## §2 模块边界

### §2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 修复分类与路由 | FixClassifier 分类 + StructuralFixRouter 路由到对应修复器 |
| 2 | L1 规则修复执行 | 9 个确定性修复器（ZombieCleaner/AllCompleter/DedupExtractor/ScaffoldRegistrar/AlignmentSyncer/DriftFixer/DepVersionFixer/ImportFixer/ConfigFixer） |
| 3 | L2 LLM 修复桥接 | LLMFixAdapter → MOD-INF-028.LLMBridge + SecretLeakGuard 扫描 |
| 4 | L3 Agent 自愈循环 | SelfHealAgent OODA 循环（最大 5 轮 + 熔断器） |
| 5 | 修复安全校验 | SafetyGate + FixValidator + LockGuard + WriteSafety + CascadeBreaker + SandboxExecutor + SecretLeakGuard |
| 6 | 修复可靠性保证 | IdempotencyGuard + ConflictResolver + FixOrderResolver + FixResultCache + BlastRadiusEstimator + DeadLetterQueue + ApprovalQueue + CanaryFixer |
| 7 | WAL 原子修复 | PREFLIGHT → CHECKPOINT(tar.gz) → APPLY → RECOVER |
| 8 | 修复预算控制 | FixBudget + DriftBudgetLink + FixStormGuard + LLMCostEstimator |
| 9 | 修复生命周期管理 | 8 状态状态机 + 中断安全 + 事件钩子 |

### §2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 审计发现问题 | MOD-INF-029/028/023 |
| 2 | LLM 文本生成 | MOD-INF-028.LLMBridge |
| 3 | 行为审计自动修复 | 永不自动修复——Block+Alert+Rollback |
| 4 | 回滚执行 | MOD-INF-021 Rollback Manager |
| 5 | 红蓝对抗验证 | MOD-INF-030 RedBlue Validator |

---

## §3 架构设计

### §3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | AutoFixEngine | 模块主类——修复执行中枢 | SafetyGate/Budget/StateMachine | 同步调用 |
| 2 | StructuralFixRouter | 结构审计→模板化修复路由 | L1 修复器 | 同步调用 |
| 3 | L1 修复器组(9个) | 确定性规则修复(>99%成功率) | AtomicFixer/LockGuard | 同步调用 |
| 4 | LLMFixAdapter | L2 LLM 修复桥接 | MOD-INF-028.LLMBridge | 异步调用 |
| 5 | SelfHealAgent | L3 Agent 自愈循环(OODA) | EscalationBridge | 异步循环 |
| 6 | SafetyGate | 置信度门控 + RBAC 联动 | MOD-INF-018 | 同步调用 |
| 7 | CascadeBreaker | 级联熔断 + 修复暂停 | SQLite 全局状态 | 事件驱动 |
| 8 | FixStateMachine | 8 状态修复生命周期 | AuditTrail | 状态转换 |
| 9 | BatchFixer | 批量修复(ThreadPoolExecutor) | SafetyGate/Budget/ConflictResolver | 并发执行 |
| 10 | ShadowWorkspace | 后台预演验证 | pytest/mypy/ruff | 子进程 |
| 11 | ConvergenceController | Phase 4 收敛闭环 | MOD-INF-030/MOD-INF-021 | 对抗验证 |
| 12 | TriageModeDispatcher | Phase 2 双模式调度(Continuous/Event-Driven) | FixPrioritizer/FixDeduplicator | 同步调用 |

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | MOD-INF-029 OrphanJudge | EXTRACT_AND_MERGE→DedupExtractor / REGISTER→ScaffoldRegistrar / DELETE→FileRemover | MOD-INF-020 AuditTrail | FixAction |
| 2 | MOD-INF-028 SemanticAuditor | LLM Bridge→SecretLeakGuard→SafetyGate→AtomicFixer | MOD-INF-020 AuditTrail | FixAction |
| 3 | MOD-INF-023 DriftDetector | auto_fixable=True→DriftFixer / False→EscalationBridge | MOD-INF-020 AuditTrail | FixAction |
| 4 | MOD-INF-026 AssetInventory | 孤儿→ScaffoldRegistrar | MOD-INF-020 AuditTrail | FixAction |
| 5 | MOD-INF-030 RedBlueValidator | 绕过场景→DriftFixer.fix() / 回滚→AtomicFixer.recover() | MOD-INF-020 AuditTrail | FixAction |

### §3.3 状态生命周期

修复 8 状态状态机：

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| DETECTED | 分类器完成分类 | DIAGNOSED | FixClassifier + RootCauseAnalyzer 完成 |
| DIAGNOSED | FixOrderResolver 排序完成 | TRIAGED | 优先级分配 + 依赖解析完成 |
| TRIAGED | 修复器获得执行权 | ACKNOWLEDGED | WAL PREFLIGHT 通过 |
| ACKNOWLEDGED | WAL CHECKPOINT 完成 | RESOLVING | APPLY 阶段开始 |
| RESOLVING | APPLY 成功 | RESOLVED | 修复内容写入 |
| RESOLVING | APPLY 失败 | RESOLVING_FAILED | 重试次数 ≤3 |
| RESOLVING_FAILED | 重试 | RESOLVING | 重试次数 ≤3 |
| RESOLVED | PostFixValidator 通过 | VERIFIED | ShadowWorkspace + RegressionCheck 通过 |
| VERIFIED | 审计日志确认 | CLOSED | ComplianceAuditor 通过 |
| 任意 | 所有修复层级尝试后仍失败 | DEAD_LETTER | 重试耗尽 或 熔断3次 |
| DEAD_LETTER | 人工介入 | CLOSED | 人工确认 |

状态停留超时阈值：DETECTED 5min / DIAGNOSED 10min / TRIAGED 5min / ACKNOWLEDGED 2min / RESOLVING 15min / RESOLVED 10min / VERIFIED 5min。

---

## §4 接口契约

### §4.1 公共 API

```python
class AutoFixEngine:
    """模块主类——修复执行中枢"""

    def fix(self, issue: AuditIssue) -> FixAction:
        """单件修复——检测→分类→路由→修复→验证"""
        ...

    def fix_all(self, issues: list[AuditIssue]) -> FixReport:
        """批量修复——ThreadPoolExecutor(max_workers=8) + 预算 + 风暴 + 熔断 + 冲突"""
        ...

    def canary_fix(self, fixer_type: str) -> FixReport:
        """灰度修复——先验后扩"""
        ...

    def dry_run(self, issues: list[AuditIssue]) -> FixReport:
        """预览修复——不写入，只输出计划"""
        ...
```

### §4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime

class FixLevel(str, Enum):
    L1_RULE = "l1_rule"
    L2_LLM = "l2_llm"
    L3_AGENT = "l3_agent"

class FixConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class FixStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"
    APPROVAL_PENDING = "approval_pending"
    CANCELLED = "cancelled"

class FixAction(BaseModel):
    action_id: str
    action_type: str
    level: FixLevel = FixLevel.L1_RULE
    status: FixStatus = FixStatus.PENDING
    target: str
    before: str = ""
    after: str = ""
    metadata: dict = {}
    validation: Optional["ValidationResult"] = None
    audit_trail_id: str = ""
    timestamp: datetime
    confidence: FixConfidence = FixConfidence.HIGH
    attempts: int = 1
    retry_count: int = 0
    model: str = ""
    context_sources: list[str] = []
    token_cost: int = 0
    verified: bool = False
    escalated: bool = False
    sandbox_verified: bool = False
    fingerprint: str = ""
    blast_radius: Optional["BlastRadius"] = None

class FixHistory(BaseModel):
    fix_id: str
    action_type: str
    target: str
    before_hash: str
    after_hash: str
    timestamp: datetime
    success: bool
    verifier: str
    revert_possible: bool

class FixDeadLetter(BaseModel):
    dead_letter_id: str
    original_fix: FixAction
    failure_reason: str
    retry_count: int
    last_retry: datetime
    escalated: bool

class BlastRadius(BaseModel):
    files: int
    modules: int
    lines_estimate: int
    risk: str

class ValidationResult(BaseModel):
    valid: bool
    check_name: str
    evidence: str
    error: str = ""

class FixReport(BaseModel):
    total_attempted: int
    succeeded: int
    failed: int
    escalated: int
    dead_lettered: int
    budget_remaining: "BudgetInfo"
    actions: list[FixAction]
    cascade_alerts: list[str] = []

class SafetyDecision(BaseModel):
    approved: bool
    confidence: FixConfidence
    reason: str

class BudgetDecision(BaseModel):
    allowed: bool
    reason: str = ""
    remaining_daily: int = 0
    remaining_monthly: int = 0

class FixHealthReport(BaseModel):
    healthy: bool
    fixers: dict[str, str]
    budget_ok: bool
    cascade_active: bool
    dead_letter_count: int
    approval_queue_size: int
    db_accessible: bool = True
    config_loaded: bool = True

class ShadowResult(BaseModel):
    safe_to_apply: bool
    test_result: Optional["TestRunResult"] = None
    type_result: Optional["TypeCheckResult"] = None
    lint_result: Optional["LintResult"] = None
    error: str = ""
    shadow_dir: str = ""

class ComplianceEvidence(BaseModel):
    fix_id: str
    action_type: str
    target: str
    before_hash: str
    after_hash: str
    timestamp: str
    actor: str
    confidence: str
    rbac_decision: str
    validation_result: str
    audit_trail_id: str
    tamper_proof_hash: str
```

### §4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `fix()` | `issue: AuditIssue` | ✅ | 必须有 issue_type + target |
| `fix_all()` | `issues: list[AuditIssue]` | ✅ | 列表非空 |
| `canary_fix()` | `fixer_type: str` | ✅ | 必须是已注册修复器 |
| `dry_run()` | `issues: list[AuditIssue]` | ✅ | 列表非空 |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `fix()` | `FixAction`：status=COMPLETED | `FixAction`：status=DEAD_LETTER / APPROVAL_PENDING |
| `fix_all()` | `FixReport`：succeeded/failed/escalated/dead_lettered | `FixReport`：cascade_alerts 非空 |
| `canary_fix()` | `FixReport`：canary_result 非空 | `FixReport`：canary_result=None |
| `dry_run()` | `FixReport`：actions 全部 PENDING | — |

### §4.5 MCP 接口

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `auto_fix.scan_issues` | `scan_issues()` | `{scope: str}` | `{issues: list[AuditIssue]}` |
| `auto_fix.fix_issue` | `fix()` | `{issue_id: str}` | `{fix_action: FixAction}` |
| `auto_fix.fix_all` | `fix_all()` | `{scope: str}` | `{fix_report: FixReport}` |
| `auto_fix.approve_fix` | `approve()` | `{fix_id: str, approved: bool}` | `{status: str}` |
| `auto_fix.rollback_fix` | `rollback()` | `{fix_id: str}` | `{status: str}` |
| `auto_fix.health_check` | `health_check()` | `{}` | `{health: FixHealthReport}` |

**错误码**：`BUDGET_EXCEEDED(429)` / `STORM_GUARD_ACTIVE(503)` / `CASCADE_FROZEN(503)` / `DEAD_LETTER(410)` / `APPROVAL_REQUIRED(202)`

### §4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增修复器 | ✅ 向后兼容 | 不影响已有修复器 |
| 新增 FixStatus 枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| 修改 FixAction 字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 所有文件写入 MUST 使用 `temp-file + os.replace()` 原子写入 | RULE-ONE 强制 |
| 2 | 批量修复 MUST 使用 `ThreadPoolExecutor(max_workers=8)` | RULE-SEVEN 强制 |
| 3 | 修复操作 MUST 通过 SafetyGate 置信度门控 + RBAC 权限校验 | SafetyGate + MOD-INF-018 |
| 4 | 修复操作 MUST 通过 FixBudget 预算检查 | 日度50/月度500/LLM Token 500,000 |
| 5 | 同文件修复 MUST 通过 ConflictResolver 串行化 | ZephyrLock 跨进程 |
| 6 | LLM 修复文本 MUST 通过 SecretLeakGuard 扫描 | 密钥泄漏拦截率 100% |
| 7 | 行为审计 RED 永不自动修复 | 架构铁律 |
| 8 | 修复指纹 MUST 写入 SQLite 持久化（24h TTL） | 跨 Session 幂等性 |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模块数 | ~51 | 1,500 | — | ❌ | _fixer-registry.yaml 需维护 1,500 模块级修复权限映射 |
| 治理脚本 | ~268 | 10,000 | — | ❌ | 需增量扫描引擎 + ScriptDAG + 分层索引 |
| AI 并发 Session | 1 | 100 | — | ❌ | 需多进程修复调度架构 + 全局预算/风暴/熔断协调 |
| 修复并发执行 | 8 (ThreadPoolExecutor) | 40-100 | — | ❌ | 需跨进程 Worker Pool + ZephyrLock |
| 内存 | ~1GB | ~8GB | 64GB | ✅ | 内存警戒线 >8GB 告警 / >12GB 降级 |
| GPU 显存 | — | 8GB (LLM) | 24GB | ✅ | LLM 修复串行化排队 |

### §5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | `code_dedup_engine/auto_fixer.py` | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\auto_fixer.py` | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\dedup_extractor.py` | 复制+重构，原文件保留为 thin wrapper | Grep 全项目 import 更新 |
| 2 | `behavioral_auditor/reconciler.py` | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\reconciler.py` | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\drift_fixer.py` | 复制+重构，原文件调用 AutoFixEngine | Grep 全项目 import 更新 |
| 3 | `asset_inventory/__main__.py._auto_fix_orphans()` | `D:\ZephyrAlpha\src\zephyr\asset-inventory\__main__.py` | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\scaffold_registrar.py` | 复制+重构，原函数改为调用 AutoFixEngine | Grep 全项目引用更新 |
| 4 | `governance/rollback/drift_fix.py` | `D:\ZephyrAlpha\src\zephyr\rollback\drift_fix.py` | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\drift_fixer.py` | 替换，原文件改为 thin wrapper | Grep 全项目 import 更新 |
| 5 | `behavioral_auditor/cascade_detector.py` | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\cascade_detector.py` | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\cascade_breaker.py` | 复制+重构，原文件改为 thin wrapper | Grep 全项目 import 更新 |

迁移安全原则：Thin Wrapper 模式（旧文件保留但内部调用 AutoFixEngine）+ 双写验证 + 渐进式切换 + 每 Phase 有回滚点。

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 修复执行失败 | FixValidator 检测 | 重试(≤3次) → DEAD_LETTER → 人工升级 | 单个修复 |
| 2 | 级联修复风暴 | CascadeBreaker 检测(5min内≥10次修复) | 熔断15min + 仅允许 L1 修复 | 模块级 |
| 3 | 全局修复风暴 | FixStormGuard 检测(60s内>150次) | 全局阻断15min | 全局 |
| 4 | 修复预算耗尽 | FixBudget 检测 | 拒绝新修复 + 保留 L1 安全修复 | 全局 |
| 5 | 文件锁冲突 | ConflictResolver 检测 | 排队等待 + 超时返回 FAILURE | 同文件修复 |
| 6 | 修复中断(SIGINT/SIGTERM) | FixInterruptGuard 检测 | WAL 自动 RECOVER + 零"半修复" | 当前修复 |
| 7 | LLM 修复密钥泄漏 | SecretLeakGuard 检测 | 阻断修复 + 告警 | L2/L3 修复 |
| 8 | Shadow Workspace 验证失败 | pytest/mypy/ruff 检测 | 不应用修复 + 返回失败 | 单个修复 |
| 9 | Phase 4 RedBlue 对抗发现 RED | MOD-INF-030 检测 | Rollback → 回到 Phase 1 | 目标模块 |
| 10 | 收敛不收敛(>10轮循环) | ConvergenceController 检测 | 强制 DEAD_LETTER | 目标模块 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 未授权修复执行 | 高 | SafetyGate + RBAC 七层+六横切面权限校验 | 单元测试覆盖每个 RBAC 层级 |
| 2 | LLM 修复文本密钥泄漏 | 高 | SecretLeakGuard 扫描所有 LLM 输出 | 密钥泄漏拦截率 = 100% |
| 3 | 修复级联风暴 | 中 | CascadeBreaker 熔断 + FixStormGuard 全局限流 | 级联熔断响应 <1s |
| 4 | 并发修复数据损坏 | 高 | ConflictResolver + ZephyrLock 跨进程文件锁 | 100 并发修复 0 锁冲突 |
| 5 | 修复预算耗尽 | 中 | FixBudget 全局持久化 + 原子 CAS 消费 | 预算超限率 <5%/月 |
| 6 | 修复中断导致半修复 | 高 | WAL 四阶段 + FixInterruptGuard 原子段 | 中断后零"半修复"状态 |
| 7 | 行为审计误自动修复 | 高 | 架构铁律：行为审计 RED 永不自动修复 | 代码审计确认无行为审计→修复路径 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 9 个 L1 修复器 | 僵尸清理/All补全/Dedup提取/孤儿注册/漂移修复/版本修复/Import修复/配置修复/对齐同步 | 每个修复器独立通过 |
| 2 | 单元测试 | 安全校验(7组件) | SafetyGate/RBAC/CascadeBreaker/SandboxExecutor/SecretLeakGuard | 每个组件独立通过 |
| 3 | 单元测试 | 可靠性(8组件) | 幂等性/冲突解决/排序/缓存/爆炸半径/死信/审批/灰度 | 每个组件独立通过 |
| 4 | 集成测试 | 完整修复管道 | 检测→分类→路由→修复→验证→审计 | 每个修复附带 before/after + 验证 |
| 5 | 集成测试 | Shadow Workspace | 预演修复→验证→应用 | 预演通过才应用 |
| 6 | 集成测试 | 迁移验证 | 旧代码→新代码双写对比 | 双写结果一致 |
| 7 | 反向测试 | 好的文件不被误改 | 0 个误修复 | 0 误修复 |
| 8 | 压力测试 | 100 并发修复请求 | 0 锁冲突 + 0 数据损坏 | 全部通过 |
| 9 | 混沌测试 | 修复过程中断电/杀进程 | WAL 自动恢复 + 零数据丢失 | 全部恢复 |
| 10 | 模糊测试 | 随机输入到修复器 | 无崩溃 + 优雅降级 | 全部降级 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-020 | 必须 | Audit Trail——修复审计记录 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-017 | 必须 | Code Dedup Engine——DedupExtractor 语义引擎 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\code-dedup-engine\blueprint.md` |
| MOD-LLM_SECURITY | 必须 | LLM Security——LLM 修复安全校验 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm_security\blueprint.md` |
| MOD-INF-005 | 必须 | Script System——Finding AUTO_FIXABLE 枚举 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\script-system\blueprint.md` |
| MOD-INF-018 | 必须 | Agent RBAC——修复操作权限校验 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-022 | 必须 | Escalation Protocol——L1_AUTO_FIX 升级路由 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| MOD-INF-023 | 必须 | Drift Detector——auto_fixable 标记 + 漂移预算 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\drift-detector\blueprint.md` |
| MOD-INF-026 | 必须 | Asset Inventory——孤儿注册逻辑 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\asset-inventory\blueprint.md` |
| MOD-INF-027 | 必须 | Audit Orchestrator——Phase 3 修复路由 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` |
| MOD-INF-029 | 必须 | Orphan Judge——EXTRACT_AND_MERGE/REGISTER/DELETE 判决 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\orphan-judge\blueprint.md` |
| MOD-INF-030 | 必须 | RedBlue Validator——绕过场景修复 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\redblue-validator\blueprint.md` |

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-031` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| `models.py` | `engine.py` | 数据模型是引擎的前置条件 | `from zephyr.auto_fix_engine.models import FixAction` 成功 |
| `state_machine.py` | `engine.py` | 状态机是引擎的前置条件 | `from zephyr.auto_fix_engine.state_machine import FixStateMachine` 成功 |
| `fix_safety.py` | `engine.py` | 安全校验是引擎的前置条件 | `from zephyr.auto_fix_engine.fix_safety import SafetyGate` 成功 |
| `fix_budget.py` | `engine.py` | 预算控制是引擎的前置条件 | `from zephyr.auto_fix_engine.fix_budget import FixBudget` 成功 |
| `fix_reliability.py` | `batch_fixer.py` | 可靠性组件是批量修复的前置条件 | `from zephyr.auto_fix_engine.fix_reliability import ConflictResolver` 成功 |
| `engine.py` | `batch_fixer.py` | 引擎是批量修复的前置条件 | `from zephyr.auto_fix_engine.engine import AutoFixEngine` 成功 |
| `engine.py` | `shadow_workspace.py` | 引擎是预演验证的前置条件 | `from zephyr.auto_fix_engine.engine import AutoFixEngine` 成功 |
| `engine.py` | `__main__.py` | 引擎是 CLI 的前置条件 | `python -m zephyr.auto_fix_engine` 成功 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| `models.py` | `engine.py` | FixAction/FixReport/FixStatus | 函数调用 |
| `state_machine.py` | `engine.py` | 状态转换事件 | 函数调用 |
| `fix_safety.py` | `engine.py` | SafetyDecision | 函数调用 |
| `fix_budget.py` | `engine.py` | BudgetDecision | 函数调用 |
| `fix_reliability.py` | `batch_fixer.py` | ConflictResolver/IdempotencyGuard | 函数调用 |
| `engine.py` | `__main__.py` | AutoFixEngine 实例 | 函数调用 |
| `engine.py` | `compliance_auditor.py` | FixAction 审计数据 | 函数调用 |
| `engine.py` | `fix_report.py` | FixReport 数据 | 函数调用 |

### §10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 11个外部依赖 + 8个内部执行顺序依赖 |
| 2 | 依赖对齐自动验证 | 是 | 有11个外部依赖需与全局依赖图对齐 |
| 3 | 临时时态内容自动清理 | 是 | §5.3 迁移方案执行完毕后需从蓝图删除 |
| 4 | 施工步骤完成度自动检测 | 是 | construction_progress = design_only，4个Phase待施工 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + _fixer-registry.yaml | `asset_inventory/dependency.py` | 不覆盖 auto-fix-engine 内部模块 |
| 2 | 依赖对齐自动验证 | CI门禁 | `validate_path_alignment.py` | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | auto-fix-engine 目录文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-fix-engine\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\auto-fix-engine\` | 测试用例 |
| 修复器注册表 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\_fixer-registry.yaml` | 修复器注册（REG-AFX-FIXER-001） |
| 修复模式注册表 | `D:\ZephyrAlpha\data\fix_patterns\pattern_index.yaml` | 修复模式知识库索引（REG-AFX-PATTERN-001，draft） |
| 配置文件 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\auto_fix_config.yaml` | 引擎配置 |
| 数据库 Schema | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\schema.sql` | SQLite Schema |
| Skill 文件 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\auto-fix-engine.md` | Agent Skill |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Audit Orchestrator (MOD-INF-027) | Phase 3 修复执行 | AutoFixEngine.fix() | Phase 3 修复管道端到端测试 |
| MCP Server | MCP Tool 暴露 | governance.auto_fix.* | MCP 调用测试 |
| CLI | `python -m zephyr.auto_fix_engine` | __main__.py | CLI 集成测试 |
| Pipeline Gate | Phase 3 修复阶段 | phase_manager | Gate 集成测试 |

### §12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-001 | 治理 | 修复操作 RBAC 权限校验（消费方） | MOD-INF-018 | 修改权限模型必须同步更新 SafetyGate |
| G-CT-005 | 治理 | 漂移事件自动修复执行（提供方） | MOD-INF-021 | 修改 DriftFixer 必须同步更新 Rollback Manager |
| CT-FIX-001 | 修复 | OrphanJudge 判决执行（提供方） | MOD-INF-029 | 修改 ScaffoldRegistrar/DedupExtractor 必须同步更新 OrphanJudge |
| CT-FIX-002 | 修复 | SemanticAuditor LLM 修复执行（提供方） | MOD-INF-028 | 修改 LLMFixAdapter 必须同步更新 LLMBridge |
| CT-FIX-003 | 修复 | DriftDetector auto_fixable 修复执行（提供方） | MOD-INF-023 | 修改 DriftFixer 必须同步更新 DriftDetector |
| CT-FIX-004 | 修复 | AssetInventory 孤儿注册执行（提供方） | MOD-INF-026 | 修改 ScaffoldRegistrar 必须同步更新 AssetInventory |
| CT-FIX-005 | 修复 | Escalation 修复路由（提供方） | MOD-INF-022 | 修改 EscalationBridge 必须同步更新 EscalationEngine |
| CT-FIX-006 | 修复 | RedBlue 绕过场景修复执行（提供方） | MOD-INF-030 | 修改 DriftFixer 必须同步更新 RedBlueValidator |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 新增 MOD-INF-031 条目 | 新模块注册 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 新增 MOD-INF-031 条目 | 蓝图注册 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 新增条目 | 文档注册 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 新增 MOD-INF-031 依赖关系 | 依赖注册 |
| 5 | 修复器注册表 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\_fixer-registry.yaml` | 创建 9 个 L1 修复器注册 | 修复器注册 |
| 6 | Skill 注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 新增 auto-fix-engine Skill | Skill 注册 |
| 7 | MCP Server | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | 新增 auto_fix MCP Tools | MCP 注册 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 迁移旧代码引入回归 | 中 | 高 | Thin Wrapper + 双写验证 + 渐进式切换 + 每 Phase 回滚点 | 风险 |
| 2 | 100 AI 并发下全局预算/风暴/熔断协调失效 | 中 | 高 | SQLite WAL 全局持久化 + 原子 CAS 消费 + 降级链 | 风险 |
| 3 | LLM 修复文本质量不稳定 | 中 | 中 | 置信度门控 + 人工确认 + SecretLeakGuard | 风险 |
| 4 | 增量扫描引擎设计复杂度 | 高 | 中 | 文件级变更检测(非 AST 级) + ScriptDAG 静态声明 | 风险 |
| 5 | 跨进程文件锁性能 | 低 | 中 | ZephyrLock + 锁粒度控制 + 超时返回 | 风险 |
| 6 | 多进程架构增加运维复杂度 | 中 | 中 | DegradationCoordinator 五级降级链(L0-L4) | 负面后果 |
| 7 | LLM 修复有固有不确定性 | 中 | 中 | 置信度门控 + 人工确认 + SecretLeakGuard | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答编号格式 | ☐ |
| 4 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 5 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 个 Phase |
| 施工模式 | 新建 |
| 核心风险 | 迁移旧代码引入回归 |
| 目标 generation | 5 — 从 design_only 到 partially_implemented |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-018 RBAC 权限校验 API | hard | ☐ | ☐ |
| 2 | MOD-INF-020 Audit Trail 写入 API | hard | ☐ | ☐ |
| 3 | MOD-INF-023 DriftDetector auto_fixable 标记 | hard | ☐ | ☐ |
| 4 | MOD-INF-017 AtomicFixer WAL 四阶段 | hard | ☐ | ☐ |
| 5 | MOD-INF-028 LLMBridge 修复文本生成 | soft | ☐ | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：创建模块骨架 + 数据模型 + 修复器注册表

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 数据模型 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` |
| 验收标准 | `python -c "from zephyr.auto_fix_engine import AutoFixEngine"` 成功 |
| 验证命令 | `python -m pytest tests/auto-fix-engine/test_models.py -v` |
| G7 检查项 | __init__.py 非空 + __all__ 导出完整 + scaffold.py 注册成功 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-031 | `__init__.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\__init__.py` |
| MOD-INF-031 | `models.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\models.py` |
| MOD-INF-031 | `_fixer-registry.yaml` | config | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\_fixer-registry.yaml` |
| MOD-INF-031 | `auto_fix_config.yaml` | config | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\auto_fix_config.yaml` |
| MOD-INF-031 | `schema.sql` | config | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\schema.sql` |

#### 步骤 2：9 个 L1 修复器 + 安全校验 + 可靠性 + 预算控制

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3 架构设计 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` |
| 验收标准 | 每个修复器独立单元测试通过 |
| 验证命令 | `python -m pytest tests/auto-fix-engine/ -v` |
| G7 检查项 | 每个修复器有 [BLUEPRINT] 头部 + 独立测试 + _fixer-registry.yaml 注册 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-031 | `zombie_cleaner.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\zombie_cleaner.py` |
| MOD-INF-031 | `all_completer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\all_completer.py` |
| MOD-INF-031 | `dedup_extractor.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\dedup_extractor.py` |
| MOD-INF-031 | `scaffold_registrar.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\scaffold_registrar.py` |
| MOD-INF-031 | `alignment_syncer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\alignment_syncer.py` |
| MOD-INF-031 | `drift_fixer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\drift_fixer.py` |
| MOD-INF-031 | `dep_version_fixer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\dep_version_fixer.py` |
| MOD-INF-031 | `import_fixer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\import_fixer.py` |
| MOD-INF-031 | `config_fixer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\config_fixer.py` |
| MOD-INF-031 | `fix_safety.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_safety.py` |
| MOD-INF-031 | `fix_reliability.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_reliability.py` |
| MOD-INF-031 | `fix_budget.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_budget.py` |
| MOD-INF-031 | `state_machine.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\state_machine.py` |
| MOD-INF-031 | `interrupt_guard.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\interrupt_guard.py` |
| MOD-INF-031 | `event_hooks.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\event_hooks.py` |

#### 步骤 3：L2/L3 修复 + 批量修复 + Shadow Workspace + 调度 + 健康检查

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3 架构设计 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` |
| 验收标准 | L2 LLM 修复桥接测试通过 + 批量修复并发测试通过 |
| 验证命令 | `python -m pytest tests/auto-fix-engine/ -v -k "llm or batch or shadow"` |
| G7 检查项 | LLMFixAdapter 有 SecretLeakGuard 集成 + BatchFixer 有 ThreadPoolExecutor |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-031 | `llm_fix_adapter.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\llm_fix_adapter.py` |
| MOD-INF-031 | `self_heal_agent.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\self_heal_agent.py` |
| MOD-INF-031 | `batch_fixer.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\batch_fixer.py` |
| MOD-INF-031 | `shadow_workspace.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\shadow_workspace.py` |
| MOD-INF-031 | `fix_scheduler.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_scheduler.py` |
| MOD-INF-031 | `fix_health_check.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_health_check.py` |
| MOD-INF-031 | `compliance_auditor.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\compliance_auditor.py` |
| MOD-INF-031 | `fix_diff.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_diff.py` |
| MOD-INF-031 | `fix_report.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_report.py` |
| MOD-INF-031 | `escalation_bridge.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\escalation_bridge.py` |
| MOD-INF-031 | `fix_pattern_miner.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_pattern_miner.py` |
| MOD-INF-031 | `engine.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\engine.py` |

#### 步骤 4：CLI + MCP + 迁移旧代码 + 全量回归测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.5 MCP 接口 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` |
| 验收标准 | CLI 可用 + MCP Tool 可调用 + 旧代码全部迁移 + 全量回归测试通过 |
| 验证命令 | `python -m pytest tests/ -q` |
| G7 检查项 | 旧代码 thin wrapper 工作正常 + 全量测试 0 新增失败 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-031 | `__main__.py` | code | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\__main__.py` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 模块骨架创建失败 | 删除 `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` 目录 |
| 2 | 修复器实现失败 | 保留已完成的修复器，标记未完成的为 TODO（仅此步骤豁免——因回滚需要） |
| 3 | L2/L3 修复失败 | 保留 L1 修复器，L2/L3 降级为 EscalationBridge 人工升级 |
| 4 | 迁移旧代码失败 | 恢复旧代码原始版本，删除 thin wrapper |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 模块入口 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\__init__.py` | ☐ | ☐ | ☐ |
| 2 | 9 个 L1 修复器 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\*_fixer.py` 等 | ☐ | ☐ | ☐ |
| 3 | 安全校验 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_safety.py` | ☐ | ☐ | ☐ |
| 4 | 可靠性保证 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_reliability.py` | ☐ | ☐ | ☐ |
| 5 | 预算控制 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\fix_budget.py` | ☐ | ☐ | ☐ |
| 6 | 测试套件 | `D:\ZephyrAlpha\tests\auto-fix-engine\` | ☐ | ☐ | ☐ |

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
| 模块数 | ~51 | blueprint_registry.yaml |
| 治理脚本 | ~268 | script-manifest.yaml |
| AI 并发 Session | 1 | 运行时观察 |
| 修复并发执行 | 8 (ThreadPoolExecutor) | BatchFixer MAX_WORKERS |
| 内存占用 | ~1GB | 进程监控 |
| 单次修复耗时 | <5s | FixHistory 统计 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 无增量扫描引擎 | ChangeDetector + ScriptDAG + IncrementalRouter | 脚本数 >500 |
| GAP-002 | 无脚本→修复器 DAG 路由 | script-manifest.yaml 新增 fixer_bindings + ScriptDAG | 脚本数 >500 |
| GAP-003 | 单进程线程池 | 三层调度(Session/Worker/Script) + 多进程 Worker Pool | AI Session >5 |
| GAP-004 | per-instance 预算 | SQLite WAL 全局预算表 + 原子 CAS 消费 | AI Session >5 |
| GAP-005 | per-instance 风暴防护 | 全局 60s/150次硬限制 + per-Session 软限制 | AI Session >5 |
| GAP-006 | 内存级级联熔断 | SQLite 持久化级联状态 + 跨进程传播 | AI Session >5 |
| GAP-007 | 内存级文件锁 | ZephyrLock 跨进程文件锁 | AI Session >5 |
| GAP-008 | 无冷启动风暴防护 | 分阶段启动(5批×20/批×30s) + 120s 豁免窗口 | AI Session >20 |
| GAP-009 | 无脚本优先级 | 四级优先级(P0-P3) + 饥饿防护 | 脚本数 >1000 |
| GAP-010 | 无优雅降级链 | 五级降级链(L0-L4) + DegradationCoordinator | 任意 2+ 全局阻断同时触发 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v5.1.0 | 5 | v3.5模板合规 | §0前移+§7/§15删除+§10拆分+铁律#13-#15+存在性列+类型列 | ❌ |
| v5.0.0 | 5 | 蓝图规格化 | v3.3 模板合规 + 压缩工作流 | ❌ |
| v4.4 | 4 | 容量架构补全 | 增量扫描+预算+风暴+熔断+冲突+幂等(20 Session) | ❌ |
| v4.5 | 4 | 全量扫描+调度 | 全量扫描+Shadow Workspace+审批/Canary/FixOrderResolver(50 Session) | ❌ |
| v1.0 | 4 | 满负荷验证 | 7天压力测试+Pattern分区+容量SLI(100 Session) | ❌ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | 增量扫描引擎缺失 | P0 | v4.4 | 待施工 |
| GAP-002 | 脚本→修复器 DAG 缺失 | P0 | v4.4 | 待施工 |
| GAP-003 | 多进程调度架构缺失 | P0 | v4.4 | 待施工 |
| GAP-004 | 全局预算协调缺失 | P1 | v4.4 | 待施工 |
| GAP-005 | 全局风暴防护缺失 | P1 | v4.4 | 待施工 |
| GAP-006 | 全局级联熔断缺失 | P1 | v4.4 | 待施工 |
| GAP-007 | 跨进程文件锁缺失 | P1 | v4.4 | 待施工 |
| GAP-008 | 冷启动风暴防护缺失 | P2 | v4.5 | 待施工 |
| GAP-009 | 脚本优先级缺失 | P2 | v4.5 | 待施工 |
| GAP-010 | 优雅降级链缺失 | P2 | v4.5 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ChangeDetector | GAP-001 | change_detector.py | Phase 1 | 待施工 |
| ScriptDAG | GAP-002 | script_dag.py | Phase 1 | 待施工 |
| IncrementalRouter | GAP-001 | incremental_router.py | Phase 1 | 待施工 |
| FixOrchestrator | GAP-003 | fix_orchestrator.py | Phase 1 | 待施工 |
| FixBudgetGlobal | GAP-004 | fix_budget_global.py | Phase 1 | 待施工 |
| FixStormGuardGlobal | GAP-005 | fix_storm_guard_global.py | Phase 1 | 待施工 |
| CascadeBreakerGlobal | GAP-006 | cascade_breaker_global.py | Phase 1 | 待施工 |
| DegradationCoordinator | GAP-010 | degradation_coordinator.py | Phase 2 | 待施工 |
| ModuleAffinityGroup | GAP-008 | module_affinity_group.py | Phase 2 | 待施工 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-AFE-01 | 三通道修复管道 | 单通道/双通道/三通道 | 三通道 | v4.0.0 架构总图定义——三大审计类型需要三种修复方法 | 2026-05-08 |
| 2 | D-AFE-02 | 行为审计永不自动修复 | 可自动修复/需确认/永不 | 永不 | 不确定根因下自动修复最危险——可能从异常进入更严重故障 | 2026-05-08 |
| 3 | D-AFE-03 | 三层调度架构 | 单进程/多线程/三层 | 三层 | 100 AI 并发需要 Session/Worker/Script 三级调度 | 2026-05-10 |
| 4 | D-AFE-04 | WAL 原子修复 | Git revert/tar.gz/WAL | WAL+tar.gz | 不依赖 Git 状态——修复中断后零"半修复" | 2026-05-08 |
| 5 | D-AFE-05 | 全局预算持久化 | 内存/SQLite/Redis | SQLite WAL | 单机部署 + SQLite WAL 原子 CAS + 跨 Session 可见 | 2026-05-10 |
| 6 | D-AFE-06 | 收编 9 处散落 auto-fix | 不收编/全量收编/渐进收编 | 渐进收编 | Thin Wrapper + 双写验证 + 渐进切换 | 2026-05-08 |
| 7 | D-AFE-07 | 8 状态修复生命周期 | 4状态/6状态/8状态 | 8状态 | DETECTED→DIAGNOSED→TRIAGED→ACKNOWLEDGED→RESOLVING→RESOLVED→VERIFIED→CLOSED + DEAD_LETTER | 2026-05-08 |
| 8 | D-AFE-08 | 冷启动分阶段启动 | 全量启动/分批启动 | 分批启动(5批×20/批×30s) | 防止冷启动风暴 | 2026-05-10 |
| 9 | D-AFE-09 | 四级脚本优先级 | 无优先级/两级/四级 | P0-P3+饥饿防护 | 安全关键脚本必须在风格检查之前 | 2026-05-10 |
| 10 | D-AFE-10 | 五级优雅降级链 | 无降级/三级/五级 | L0-L4 | 多个阻断同时触发时逐步收紧而非全部阻断 | 2026-05-10 |
| 11 | D-AFE-11 | Phase 4 收敛闭环 | 修完即关/验证即关/收敛闭环 | 收敛闭环(RedBlue对抗→N次连续零问题→CLOSED) | 确保修复真正解决了根本问题 | 2026-05-08 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | 断链——旧引用找不到文件 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移——AI 自行决定 |
| 9 | **蓝图必须自包含** | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议** | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 虚假进度误导下一个AI |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
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
| 本蓝图"蓝图特有：三通道修复管道" | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 本蓝图"蓝图特有：Phase 2 双模式调度" | **原地** | 双模式调度是 AutoFixEngine 核心调度架构 |
| 本蓝图"蓝图特有：Phase 4 收敛闭环" | **原地** | 收敛闭环是修复生命周期的核心环节 |
| 本蓝图"蓝图特有：散落 auto-fix 逻辑收编映射" | **原地** | 收编映射是迁移上下文，与蓝图主体强关联 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | `code_dedup_engine/auto_fixer.py`（迁移后） | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\auto_fixer.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\dedup_extractor.py` | 迁移→双写验证→标记deprecated→Phase4物理删除 |
| 2 | `behavioral_auditor/cascade_detector.py`（迁移后） | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\cascade_detector.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\cascade_breaker.py` | 迁移→双写验证→标记deprecated→Phase4物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 蓝图模板 | TPL-BLUEPRINT-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` | 模板合规基准 |
| 10 | 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 规格化标准 |
| 11 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 十五字段头部 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | `code_dedup_engine/auto_fixer.py` | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\auto_fixer.py` | 重复函数自动修复 | 无统一安全网/预算/幂等/冲突解决——需收编到 AutoFixEngine |
| 2 | `behavioral_auditor/reconciler.py` | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\reconciler.py` | 漂移修复 | 修复策略路由不统一——需收编到 DriftFixer |
| 3 | `asset_inventory/__main__.py._auto_fix_orphans()` | `D:\ZephyrAlpha\src\zephyr\asset-inventory\__main__.py` | 孤儿注册 | 无安全校验——需收编到 ScaffoldRegistrar |
| 4 | `behavioral_auditor/cascade_detector.py` | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\cascade_detector.py` | 级联检测 | 内存级不跨进程——需升级到 CascadeBreaker |
| 5 | `rollback/drift_fix.py` | `D:\ZephyrAlpha\src\zephyr\rollback\drift_fix.py` | 漂移修复 | G-CT-005 消费端——需收编到 DriftFixer |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | auto-fix-engine 目录 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\` | 新建 | 创建模块 |
| 2 | auto-fix-engine 测试 | `D:\ZephyrAlpha\tests\auto-fix-engine\` | 新建 | 创建测试 |
| 3 | auto_fixer.py | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\auto_fixer.py` | 修改 | 改为 thin wrapper |
| 4 | reconciler.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\reconciler.py` | 修改 | 改为调用 AutoFixEngine |
| 5 | asset-inventory/__main__.py | `D:\ZephyrAlpha\src\zephyr\asset-inventory\__main__.py` | 修改 | _auto_fix_orphans 改为调用 AutoFixEngine |
| 6 | drift_fix.py | `D:\ZephyrAlpha\src\zephyr\rollback\drift_fix.py` | 修改 | 改为 thin wrapper |
| 7 | cascade_detector.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\cascade_detector.py` | 修改 | 改为 thin wrapper |
| 8 | governance_server.py | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | 修改 | 新增 MCP Tools |
| 9 | skill-registry.yaml | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 修改 | 新增 Skill |
| 10 | auto-fix-engine.md | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\auto-fix-engine.md` | 读取 | Skill 定义 |

---

## 蓝图特有章节

### 蓝图特有：三通道修复管道（Phase 3）

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：三通道修复管道是 AutoFixEngine 独有的架构设计
> 不可砍理由：砍掉后 AI 不知道结构/语义/行为审计的修复路由规则

| 通道 | 审计类型 | 修复方法 | 置信度 | 执行者 | 人工确认 |
|------|---------|---------|:---:|------|:---:|
| 1 | 结构审计 RED | 模板化修复（PATH_FIX/ID_FIX/VALUE_FIX） | 100% | MOD-INF-031 AutoFixEngine | ❌ |
| 2 | 语义审计 RED | 人工确认→LLM Bridge→自然语言修复 | 95~98% | MOD-INF-028.LLMBridge | ✅ MUST |
| 3 | 行为审计 RED | Block + Alert + Rollback | N/A | MOD-INF-020+023+021 | N/A 永不自动修复 |

19 结构审计维度→修复器映射：

| # | 维度 ID | 名称 | 修复器 | 修复方法 | 可自动修复 |
|:---:|---------|------|--------|---------|:---:|
| 1 | DIM-PATH-001 | 路径合法性 | ZombieCleaner + StaleRefFixer | PATH_FIX | ✅ |
| 2 | DIM-TYPE-001 | 注册完整性 | AllCompleter | ID_FIX | ✅ |
| 3 | DIM-TYPE-002 | 类型注册 | ScaffoldRegistrar | ID_FIX | ✅ |
| 4 | DIM-TYPE-003 | 消费者注册 | ConsumerRegistryFixer | ID_FIX | ✅ |
| 5 | DIM-CODE-001 | 代码标准 | DedupExtractor + ImportFixer | PATH_FIX | ✅ |
| 6 | DIM-DEP-001 | 依赖链完整性 | DependsOnFixer | VALUE_FIX | ✅ |
| 7 | DIM-NAMING-001 | 命名规范 | RuleTaxonomyFixer | VALUE_FIX | ⚠️ 建议人工审核 |
| 8 | DIM-SECURITY-001 | 安全红线 | NO AUTO-FIX→EscalationBridge | BLOCK | ❌ |
| 9 | DIM-SCALE-001 | 规模漂移 | NumericClaimFixer | VALUE_FIX | ✅ |
| 10 | DIM-KBG-001 | KB 决策记录文档链 | ADRChainFixer | VALUE_FIX | ⚠️ LLM辅助 |
| 11 | DIM-CROSS-REG-001 | 跨注册表一致性 | CrossRegistryFixer | ID_FIX | ✅ |
| 12 | DIM-CONTRACT-001 | 契约ID链 | ContractIDChainFixer | ID_FIX | ✅ |
| 13 | DIM-CONSTRUCTION-001 | 施工状态 | ConstructionPlanFixer | VALUE_FIX | ✅ |
| 14 | DIM-BLUEPRINT-CODE-001 | 蓝图代码同步 | BlueprintConstructionFixer | VALUE_FIX | ⚠️ LLM辅助 |
| 15 | DIM-ORPHAN-001 | 孤儿文件 | ScaffoldRegistrar | PATH_FIX | ✅ |
| 16 | DIM-ALIGNMENT-001 | 双向对齐 | AlignmentSyncer | PATH_FIX | ✅ |
| 17 | DIM-DRIFT-001 | 配置漂移 | DriftFixer + ConfigFixer | VALUE_FIX | ✅ |
| 18 | DIM-DEP-VERSION-001 | 依赖版本 | DepVersionFixer | VALUE_FIX | ✅ |
| 19 | DIM-STRUCTURE-MISSING-001 | 结构缺失 | StructureMissingFixer | ID_FIX | ⚠️ LLM辅助 |

三条不可自动修复红线：DIM-SECURITY-001（安全红线）→ Block→EscalationBridge；DIM-NAMING-001（命名规范）→ 需人工判断语境；Phase 4 RED findings（RedBlue 对抗发现）→ Block+Rollback。

### 蓝图特有：Phase 2 双模式调度

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：双模式调度是 AutoFixEngine 独有的调度架构
> 不可砍理由：砍掉后 AI 不知道 Continuous 和 Event-Driven 的行为差异

| 属性 | Continuous（批量） | Event-Driven（即时） |
|------|:---:|:---:|
| max_batch_size | 50 | 1 |
| max_concurrent_fixes | 5 | 1 |
| allow_defer | True | False |
| allow_merge | True | False |
| allow_pause | True | False（除非级联熔断） |
| priority_base | 50 | 0（最高） |
| notification | summary | immediate |

### 蓝图特有：Phase 4 收敛闭环

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：收敛闭环是 AutoFixEngine 与 RedBlue Validator 的独特集成
> 不可砍理由：砍掉后 AI 不知道修复何时算"真正解决"

ConvergenceController：RedBlue 对抗验证→全部 GREEN→收敛检测→N 次连续零问题(默认3次)→CLOSED；仍有 RED→Rollback→回到 Phase 1；超过 10 轮循环→强制 DEAD_LETTER。

### 蓝图特有：散落 auto-fix 逻辑收编映射

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：收编映射是 AutoFixEngine 独有的迁移上下文
> 不可砍理由：砍掉后 AI 不知道旧代码在哪、怎么迁移

| 原位置 | 原类/函数 | 收编为 | 收编方式 |
|--------|----------|--------|---------|
| `code_dedup_engine/auto_fixer.py` | AutoFixer.can_fix()/fix() | DedupExtractor + SafetyGate | 逻辑合并，安全约束升级为全局 SafetyGate |
| `code_dedup_engine/prioritizer.py` | Prioritizer.rank()→AUTO_FIX | FixPrioritizer | 优先级排序逻辑统一 |
| `behavioral_auditor/reconciler.py` | AutoFixer.auto_fix()/rollback_fix() | DriftFixer + AtomicFixer | 修复策略路由统一，原子性由 WAL 保证 |
| `behavioral_auditor/cascade_detector.py` | is_auto_fix_paused() | CascadeBreaker | 级联熔断逻辑升级为全局组件 |
| `asset_inventory/__main__.py` | _auto_fix_orphans() | ScaffoldRegistrar | 孤儿注册逻辑统一入口 |
| `governance/rollback/drift_fix.py` | DriftFixHandler.on_drift_fix() | DriftFixer | G-CT-005 消费端收编 |
| `escalation/escalation_models.py` | L1_AUTO_FIX | EscalationBridge | 升级路由保留，修复执行委托给 AutoFixEngine |
| `script_system/finding.py` | RecommendationType.AUTO_FIXABLE | FindingBridge | Finding 枚举保留，修复执行委托给 AutoFixEngine |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| AutoFixEngine 架构设计 | **本文档 §1-§10** | 旧 FixDispatcher 文档 |
| 修复执行施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 修复接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 三通道修复管道映射 | **本文档 蓝图特有** | v4.0.0 架构总图（引用） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-027 Audit Orchestrator | §4 接口契约、§12 集成点 |
| Tier 1 | MOD-INF-029 OrphanJudge | CT-FIX-001 契约 |
| Tier 1 | MOD-INF-028 SemanticAuditor | CT-FIX-002 契约 |
| Tier 1 | MOD-INF-023 DriftDetector | CT-FIX-003 契约 |
| Tier 2 | MCP governance.auto_fix | §4.5 MCP 接口 |
| Tier 2 | CLI `python -m zephyr.auto_fix_engine` | §4.1 公共 API |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\auto-fix-engine\*.py` | §4 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改修复器注册表 | 下游更新修复器引用 | 更新 MCP Tool |
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
| 三通道修复管道映射变更 | 需 Owner 审批 + 通知 MOD-INF-027/028/029/030 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-14 | 5.1.0 | v3.5模板合规升级：§0前移至概述后、§7备选方案删除（信息由§18决策记录覆盖）、§15后果删除（正面与§1重复，负面合并到§14风险+增加"类型"列）、§0.1代码文件清单新增"存在性"列（未实现/已实现/已阻塞/已废弃）、§5.1技术约束去掉"原因"列改为"值"列、§10拆为§10.1依赖声明+§10.2依赖图对齐声明+§10.3内部依赖图+§10.4自动化规格、铁律新增#13~#15、新增蓝图拆分判定标准段落、施工声明标注时态属性、§18决策记录增加时态属性标注、§5.3迁移方案标注临时时态属性、§16.3施工步骤标注临时时态属性+删除前置条件、references v3.3→v3.5 |
| 2026-05-14 | 5.0.0 | v3.3 模板合规升级：H1标题格式+概述段+标准锚点+章节重排(概述→§1-§15→§0→§16-§18→规则参考)+补缺章节+压缩工作流(Layer1合规+Layer2砍削)+绝对路径+construction_progress与代码实际状态对齐(design_only)+actual_disk_path与§11一致+蓝图特有章节(三通道/双模式/收敛闭环/收编映射) |
| 2026-05-12 | 4.3.0 | 病因修复法九阶链+FiveWhysAnalyzer/ProblemLegitimacyAdjudicator/RuleLayerDiagnoser/PreventionGenerator/CausalGraph/CounterfactualAnalyzer/RootCauseTaxonomy/FixEffectivenessTracker/FixPatternMemory/SelfEvolvingRule/MetaProblemInterrogator |
| 2026-05-10 | 4.2.0 | 四级原子修复边界(LINE/FILE/MULTI/2PC)+FixBufferIsolator+MultiFileAtomicFixer |
| 2026-05-08 | 4.1.0 | 审计→修复 1:1 精准映射(37条精确规则×3审计类型) |
