---
module_id: MOD-INF-028
submodule_path: src/zephyr/governance/semantic_auditor
title: "Semantic Auditor 蓝图 — 语义审计器·规则文档LLM桥接"
doc_type: blueprint
status: Active
version: "6.1.0"
layer: L1_foundation
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
generation: 5
construction_progress: mostly_implemented
actual_disk_path: 'D:\ZephyrAlpha\src\zephyr\governance\semantic_auditor\'
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "语义审计引擎——2类纯语义触发(F跨文档引用+G依赖链断裂)+9阶段管道+LLM Bridge修复文本生成，从单Session审计到100 AI并发/10000脚本的规模跃迁"
tags:
  - semantic-audit
  - rule-validation
  - staleness-detection
  - llm-bridge
  - trigger-engine
  - safety-boundary
  - governance
  - self-healing
  - cross-session-continuity
  - ontology-convergence
  - pure-semantic-audit
  - capacity-upgrade
priority: P1
activation_phase: current
runtime_plane: warm
depends_on:
  - target: MOD-INF-020
    at: "writer.py + models.py"
    why: "AuditTrail"
  - target: MOD-LLM_SECURITY
    at: "section 3"
    why: "LLM Security"
  - target: MOD-INF-026
    at: "section 1"
    why: "Asset Inventory"
  - target: MOD-FEEDBACK_LOOP
    at: "section 2"
    why: "Feedback Loop"
  - target: MOD-INF-021
    at: "section 3"
    why: "Rollback"
  - target: MOD-INF-024
    at: "section 2"
    why: "Budget Enforcer"
  - target: MOD-INF-027
    at: "section 4"
    why: "Audit Orchestrator (编排)"
  - target: MOD-INF-031
    at: "section 3"
    why: "Auto-Fix Engine (修复触发)"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\audit-orchestrator\\blueprint.md"
    section: "§0,§1"
    why: "AuditOrchestrator——平级协调方，结构审计维度承接10类二元触发"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_system_master\\blueprint.md"
    section: "§0"
    why: "系统级容量升级方案（Worker Pool/双通道调度/拥塞控制）"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared_core\\blueprint.md"
    section: "§0"
    why: "Shared/Core基础组件18项压力测试"
  - path: "D:\\ZephyrAlpha\\config\\capacity_params.yaml"
    section: "full"
    why: "CFG-CAP-001——所有并发/容量参数真源"
architecture_layer: "L1_分析引擎"
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Semantic Auditor 蓝图 — 语义审计器·规则文档LLM桥接

> module_id: MOD-INF-028 | version: 6.1.0 | status: active | layer: cross_layer
> actual_disk_path: `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` | generation: 5 | construction_progress: partially_implemented

## 概述

SemanticAuditor 是 ZephyrAlpha 的纯语义审计引擎——它解决"规则文档中的引用和依赖是否仍然有效"这一核心问题。核心职责包括：F 类触发（跨文档引用语义断裂检测）、G 类触发（depends-on 治理意图链断裂检测）、LLM Bridge 修复文本生成、9 阶段审计管道。当前规模 ~51 模块/~268 脚本/单 Session 审计，目标容量 1,500 模块/10,000 脚本/100 AI 并发。上游依赖 AuditOrchestrator（MOD-INF-027）调度、AuditTrail（MOD-INF-020）记录、LLM Security（MOD-LLM_SECURITY）校验；下游被 AuditOrchestrator 消费审计报告。

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

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-028`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3.1 | 包初始化+公共API导出 | 已实现 | |
| 2 | `__main__.py` | §10 | CLI 入口 `python -m zephyr.semantic_auditor` | 已实现 | |
| 3 | `cli.py` | §10 | CLI 命令实现(scan/check/health) | 已实现 | |
| 4 | `spec_auditor.py` | §3.1 | 规格审计(挂靠自 MOD-INF-020) | 已实现 | |
| 5 | `compliance_map.py` | §3.1 | 合规映射(挂靠自 MOD-INF-020) | 已实现 | |
| 6 | `supply_chain.py` | §3.1 | 供应链检查(挂靠自 MOD-INF-020) | 已实现 | |
| 7 | `feedback_self_audit.py` | §3.1 | 反馈自审计(挂靠自 MOD-INF-020) | 已实现 | |
| 8 | `kb_gate.py` | §3.1 | 知识库门禁(挂靠自 MOD-INF-020) | 已实现 | |
| 9 | `privacy.py` | §3.1 | 隐私检查(挂靠自 MOD-INF-020) | 已实现 | |
| 10 | `self_healer.py` | §3.1 Stage 7 | 自愈闭环(修复→自测→回滚) | 已实现 | |
| 11 | `models.py` | §4.2 | Pydantic 数据模型(SemanticAuditReport等) | 已实现 | |
| 12 | `reference_extractor.py` | §3.1 Stage 1 | 9种引用维度提取 | 已实现 | |
| 13 | `trigger_engine.py` | §3.1 Stage 2 | F+G 两类纯语义触发检测 | 已实现 | |
| 14 | `safety_boundary.py` | §3.1 Stage 3 | 禁碰规则过滤+置信度阈值 | 已实现 | |
| 15 | `alignment_engine.py` | §3.1 Stage 4 | 注册表↔磁盘双向对齐(6对) | 已实现 | |
| 16 | `issue_aggregator.py` | §3.1 Stage 5 | 去重聚合问题清单 | 已实现 | |
| 17 | `llm_bridge.py` | §3.1 Stage 6 | LLM修复文本生成+模板降级 | 已实现 | |
| 18 | `fix_prioritizer.py` | §3.1 Stage 8 | 修复优先级排序+批处理分组 | 已实现 | |
| 19 | `blast_radius.py` | §3.1 Stage 9 | 影响爆炸半径+级联过时检测 | 已实现 | |
| 20 | `self_health.py` | §3.1 | 7 SLI+5容量SLI健康监控 | 已实现 | |
| 21 | `token_budget.py` | §3.1 | Token预算管控 | 未实现 | |
| 22 | `cross_session.py` | §3.1 | 跨Session状态延续 | 未实现 | |
| 23 | `forbidden_patterns.yaml` | §3.1 Stage 3 | 禁碰规则配置(YAML) | 已实现 | |
| 24 | `rule_document_registry.yaml` | §3.1 Stage 1 | 规则文档注册表(YAML) | 已实现 | |
| 25 | `system_state_registry.yaml` | §3.1 | 系统状态注册表(YAML) | 未实现 | |
| 26 | `llm_bridge_prompt.yaml` | §3.1 Stage 6 | Prompt版本锁定(YAML) | 未实现 | |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现代码文件 21 个 | `ls D:\ZephyrAlpha\src\zephyr\semantic-auditor\` | ☐ |
| 蓝图描述的 9 阶段管道组件 → Stage 1-5, 7-9 已实现 (Stage 6 LLM 待接通) | 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path = §11 业务代码路径 | 路径比对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v4.0.0 (基线) | 7 个已有文件（spec_auditor/compliance_map/supply_chain/feedback_self_audit/kb_gate/privacy/__init__） | 9 阶段管道核心组件 | 待施工 |
| v5.0.0 (容量升级) | — | 增量审计/全局索引/缓存/异步队列 | 待施工 |
| v6.1.0 (模板对齐v3.5) | 21/26 文件已实现 | token_budget.py, cross_session.py, system_state_registry.yaml, llm_bridge_prompt.yaml | LLM API 未接通, 暂不施工 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 有 140+ 规则/策略/蓝图文档，文档间存在大量跨文档引用（`see X`/`参见 X`/`ref: X`）和 depends_on 依赖。当被引用文档重构后，引用者文档中的章节号、路径、数字可能过时——但文件本身仍存在，二元触发（`Path.exists()`）无法检测。需要语义理解才能判定引用是否断裂。

v3.0.0 本体论收敛：12 类触发（A~L）精简为 2 类纯语义触发（F+G）。10 类二元/结构性触发归还 AuditOrchestrator 结构审计维度。v4.0.0 从 Orchestrator 子系统提升为独立 peer service（`belongs_to: null`）。v5.0.0 容量升级方案通过审计，面向 100 AI 并发设计。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 检测跨文档引用语义断裂（F） | 黄金数据集召回率 >99% |
| 2 | 检测 depends-on 链断裂（G） | 黄金数据集召回率 >99% |
| 3 | LLM Bridge 生成可用修复文本 | 人工审核可用率 >90% |
| 4 | 自愈闭环（修复→自测→回滚） | 修复成功率 >80% |
| 5 | 100 AI 并发增量审计 | 零数据竞态/零锁死/零审计结果错误 |
| 6 | 增量扫描 30 文档 P95 <60s | 含 LLM Bridge |

### 1.3 不包含的目标

| # | 明确排除 | 原因 | 归属 |
|---|---------|------|------|
| 1 | 二元触发（A/E 文件失联/TTL过期） | `Path.exists()` / 日期比较 = 确定性 | DIM-TYPE-003 (Orchestrator) |
| 2 | 结构触发（C/D 结构缺失/跨注册表不一致） | 集合查找/等式判断 = 确定性 | DIM-SSoT-001 (Orchestrator) |
| 3 | 数值触发（B 系统超越） | 数值比较 = 确定性 | DIM-SCALE-001 (Orchestrator) |
| 4 | 施工触发（I/L/J/K） | 布尔组合/文件存在性 = 确定性 | DIM-CONSTRUCTION-001/DIM-KBG-001/DIM-DEP-001 |
| 5 | AI 行为审计 | 审计 AI 操作行为 ≠ 审计规则文档 | MOD-INF-020 AuditTrail |
| 6 | 结构修复执行 | 语义修复文本应用 ≠ 结构修复 | MOD-INF-031 AutoFixEngine |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 单文档审计 <30s（不含 LLM），含 LLM <60s | 管道设计必须快速阶段先行 |
| LLM API 可能不可用 | Stage 6 必须可跳过，降级为 detect-only |
| 100 AI 并发写入同一规则文档 | 需 ZephyrLock + 修复队列 + 幂等性 |
| Windows NTFS 原子写入 | temp-file + os.replace() |
| Token 预算有限 | per-session 配额 + 全局核算 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | F 类触发检测 | 跨文档引用语义断裂——HeadingExtractor 解析目标文档章节，判定引用 §N 是否存在 |
| 2 | G 类触发检测 | depends-on 链断裂——解析 depends_on + module-registry 定位目标文件 + 判定 at 章节是否存在 |
| 3 | 安全边界过滤 | 8 条禁碰规则 + 置信度阈值 95%——不确定=不动 |
| 4 | 双向对齐检测 | 注册表↔磁盘双向对齐（6 对保留，4 对移交 Orchestrator） |
| 5 | LLM Bridge 修复文本生成 | 将机械发现转为自然语言修复文本——LLM 不做判断 |
| 6 | 自愈闭环 | 修复应用→自测验证→失败回滚 |
| 7 | 影响爆炸半径分析 | 修复前评估影响范围 |
| 8 | 递归自审计 | max_depth=1，审计自身配置文件 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | AI 行为漂移检测 | MOD-INF-020 AuditTrail |
| 2 | 密码学完整性验证 | MOD-INF-020 AuditTrail |
| 3 | 结构性审计（86 个脚本） | MOD-INF-027 AuditOrchestrator |
| 4 | 结构修复执行 | MOD-INF-031 AutoFixEngine |
| 5 | 容量参数管理 | config/capacity_params.yaml |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | ReferenceExtractor | 从规则文档提取结构化引用（8 种语义相关类型） | — | 同步调用 |
| 2 | TriggerEngine | F+G 两类纯语义触发检测 | ReferenceExtractor | 同步调用 |
| 3 | SafetyBoundary | 禁碰规则过滤 + 置信度阈值 | — | 同步调用 |
| 4 | AlignmentEngine | 注册表↔磁盘双向对齐（6 对） | — | 同步调用 |
| 5 | IssueAggregator | 去重聚合问题清单 | TriggerEngine, AlignmentEngine | 同步调用 |
| 6 | LLMBridge | 修复文本生成（LLM 只润色，不做判断） | MOD-LLM_SECURITY, MOD-INF-024 | 异步队列(v5) |
| 7 | SelfHealer | 修复→自测→回滚闭环 | LLMBridge, MOD-INF-021, MOD-INF-020 | 同步调用 |
| 8 | FixPrioritizer + DiffPreview | 修复优先级排序 + 干跑 diff 预览 | — | 同步调用 |
| 9 | ImpactBlastRadius | 影响爆炸半径 + 级联过时检测 | ReferenceExtractor | 同步调用 |
| 10 | CrossSessionContinuity | 跨 Session 状态延续 + 历史趋势 | — | 文件存储 |
| 11 | SelfHealthMonitor | 7 SLI + 5 容量 SLI + 退化检测 | — | 定时自检 |
| 12 | TokenBudgetManager | Token 预算管控 | MOD-INF-024 | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | 规则文档 Markdown/YAML | Stage 1 引用提取 | TriggerEngine | ExtractedReferences |
| 2 | ExtractedReferences | Stage 2 F+G 触发检测 | SafetyBoundary | list[TriggerResult] |
| 3 | TriggerResult | Stage 3 安全过滤 | AlignmentEngine | list[AuditIssue] |
| 4 | 注册表+磁盘 | Stage 4 双向对齐 | IssueAggregator | AlignmentReport |
| 5 | Stage 2+3+4 | Stage 5 去重聚合 | LLMBridge | AggregatedIssues |
| 6 | RED 问题 | Stage 6 LLM 修复文本 | SelfHealer | LLMFixResult |
| 7 | 修复文本+目标文档 | Stage 7 自愈闭环 | FixPrioritizer | HealResult |
| 8 | 审计报告 | Stage 8 优先级+Diff | ImpactBlastRadius | PrioritizedFix |
| 9 | 修复后文档 | Stage 9 影响半径+级联 | — | BlastReport |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| idle | `audit(doc)` 调用 | extracting | — |
| extracting | Stage 1 完成 | triggering | ExtractedReferences 非空 |
| triggering | Stage 2 完成 | filtering | TriggerResult 列表生成 |
| filtering | Stage 3 完成 | aligning | 安全边界通过 |
| aligning | Stage 4 完成 | aggregating | AlignmentReport 生成 |
| aggregating | Stage 5 完成 | fixing (if RED) / reporting (if no RED) | RED 问题存在 |
| fixing | Stage 6+7 完成 | reporting | 修复结果确定 |
| reporting | Stage 8+9 完成 | idle | SemanticAuditReport 生成 |

---

## §4 接口契约

### 4.1 公共 API

```python
class SemanticAuditor:
    """语义审计主类——2类纯语义触发+9阶段管道"""

    def audit(self, doc_path: Path, mode: str = "full") -> SemanticAuditReport:
        """
        审计单个规则文档

        输入：doc_path 规则文档路径，mode=full/incremental/detect-only
        输出：SemanticAuditReport 含所有触发+对齐+修复结果
        核心逻辑：9阶段管道顺序执行
        """

    def audit_batch(self, doc_paths: list[Path], mode: str = "incremental") -> list[SemanticAuditReport]:
        """
        批量审计（增量模式默认）

        输入：doc_paths 变更文档列表
        输出：每个文档的审计报告
        核心逻辑：ThreadPoolExecutor 并行审计
        """

    def health_check(self) -> HealthStatus:
        """
        自身健康检查

        输入：无
        输出：HealthStatus 含 7 SLI + 5 容量 SLI
        核心逻辑：黄金数据集回归 + 禁碰规则完整性 + Token 趋势
        """
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime

class Severity(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    INFO = "INFO"

class SafetyDecision(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    FORBIDDEN = "FORBIDDEN"

class ExtractedReferences(BaseModel):
    file_paths: list[str] = Field(default_factory=list, description="完整路径引用")
    relative_paths_with_ids: list[str] = Field(default_factory=list, description="相对路径+ID格式")
    depends_on_targets: list[dict] = Field(default_factory=list, description="depends_on提取")
    internal_rule_ids: list[str] = Field(default_factory=list, description="DOC-001等内部规则ID")
    section_refs: list[str] = Field(default_factory=list, description="§2.5等章节引用")
    numeric_claims: list[dict] = Field(default_factory=list, description="中英文数值声明")
    script_refs: list[str] = Field(default_factory=list, description="脚本名称引用")
    module_id_refs: list[str] = Field(default_factory=list, description="MOD-INF-XXX等模块ID")
    blueprint_links: list[str] = Field(default_factory=list, description="Markdown蓝图链接")
    frontmatter_metadata: Optional[dict] = Field(default=None, description="TTL/Stability/Autonomy")

class TriggerResult(BaseModel):
    trigger_type: str = Field(..., description="cross_doc_ref_broken或dependson_chain_broken")
    certainty: float = Field(..., description="确定性0-1")
    severity: Severity
    target_location: str
    evidence: str

class AlignmentReport(BaseModel):
    aligned_count: int
    zombie_count: int
    orphan_count: int
    alignment_score: float
    staleness_severity: Severity

class LLMFixResult(BaseModel):
    success: bool
    fix_text: str = ""
    token_used: int = 0
    error: str = ""

class HealResult(BaseModel):
    success: bool
    reason: str = ""
    rollback_applied: bool = False

class SemanticAuditReport(BaseModel):
    audit_id: str
    rule_document: str
    total_triggers: int
    safety_filtered_out: int
    red_issues: list[dict]
    yellow_issues: list[dict]
    alignment_reports: list[AlignmentReport]
    llm_fixes: list[LLMFixResult]
    heal_results: list[HealResult]
    duration_ms: int
    token_used: int
    fresh_until: datetime
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `audit()` | `doc_path` | ✅ | 必须是 .md 或 .yaml 文件路径 |
| `audit()` | `mode` | ❌ | full/incremental/detect-only，默认 full |
| `audit_batch()` | `doc_paths` | ✅ | 非空列表，每项为有效文件路径 |
| `health_check()` | — | — | 无输入 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `audit()` | `SemanticAuditReport`：含所有触发+对齐+修复结果 | `AUDIT_TIMEOUT` / `DOC_NOT_FOUND` / `LLM_UNAVAILABLE` |
| `audit_batch()` | `list[SemanticAuditReport]` | 部分成功部分失败，失败项含 error 字段 |
| `health_check()` | `HealthStatus`：HEALTHY/DEGRADED/CRITICAL | — |

### 4.5 MCP 接口

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `audit_rule_document` | `audit()` | `{doc_path: str, mode: str}` | `{report: SemanticAuditReport}` |
| `audit_all_rules` | `audit_batch()` | `{mode: str}` | `{reports: list}` |
| `check_alignment` | AlignmentEngine | `{registry_path: str, disk_path: str}` | `{report: AlignmentReport}` |

**错误码**：`AUDIT_TIMEOUT(408)` / `LLM_UNAVAILABLE(503)` / `DOC_NOT_FOUND(404)`

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增触发类型 | ❌ 破坏性 | 需 Owner 审批 |
| 新增对齐对 | ✅ 向后兼容 | 不影响已有消费者 |
| LLM prompt 变更 | ⚠️ 需通知 | 修复质量可能变化 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| 审计报告字段新增 | ✅ 向后兼容 | 不破坏已有逻辑 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 | 3.12+ |
| 2 | 数据模型 | Pydantic V2 BaseModel，禁止 `@dataclass` |
| 3 | 文件输出 | temp-file + os.replace() 原子写入 |
| 4 | 写入前锁 | lock_files.py 三步（check→acquire→write→release） |
| 5 | 批量 IO | ThreadPoolExecutor(max_workers=8) |
| 6 | LLM 角色 | 只做文本润色，不做判断 |
| 7 | 禁碰规则内容 | 禁止自动修改 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 规则文档数 | ~36 | 5,000+ | — | ❌ | KBG-0056 分层自动发现 |
| AI 并发 Session | 1 | 100 | — | ❌ | KBG-0052 异步队列 4→12 workers |
| LLM API 调用/批次 | 偶尔 | 200-500 | 4 并发槽位 | ❌ | KBG-0052 异步队列+批处理 |
| 全量扫描耗时 | 未定义 | <3.5h | — | ❌ | KBG-0050 增量审计+KBG-0051 全局索引 |
| 跨文档引用关系 | ~200 | 25,000 | O(n²) | ❌ | KBG-0051 cross_ref_index.db |
| Checkpoint 文件/天 | 偶尔 | 900 | 无清理 | ❌ | KBG-0060 轻量化+7天清理 |
| 对齐对 | 10 | 50+ | 手工维护 | ❌ | 自动发现+分区 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | 触发 A/C/D/E/H | 本蓝图 §4 | MOD-INF-027 结构审计维度 | 已迁移(v3.0.0) | 搜索全项目引用已更新 |
| 2 | 触发 I/J/K/L | 本蓝图 §4 | MOD-INF-027 DIM-CONSTRUCTION-001等 | 已迁移(v3.0.0) | 搜索全项目引用已更新 |
| 3 | ArchitectureModelDetector | 本蓝图 §3.7 | MOD-INF-027 ArchitectureModelScanner | 已迁移(v3.0.0) | 搜索全项目引用已更新 |
| 4 | CrossDirectoryConsistencyEngine | 本蓝图 §3.8 | MOD-INF-027 CrossDirChecker | 已迁移(v3.0.0) | 搜索全项目引用已更新 |
| 5 | ScanMutex(FileExistsError) | `scan_mutex.py` | ZephyrLock(portalocker+TTL) | 待替换(v5.0.0) | KBG-0054 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | LLM API 不可用 | 超时/异常 | 跳过 Stage 6，降级为 detect-only | 无修复文本，触发仍100%检出 |
| 2 | 审计日志写入失败 | MOD-INF-020 异常 | 取消修复操作（不记录=不操作） | 修复不执行 |
| 3 | 回滚失败 | MOD-INF-021 异常 | 标记 CRITICAL + 通知 Owner + 锁定目标文件 | 目标文件锁定 |
| 4 | Token 预算耗尽 | TokenBudgetManager | 跳过 LLM 阶段，仅输出机械检测 | 无修复文本 |
| 5 | 并发锁争用 | ZephyrLock 超时 | 修复请求排队，串行应用 | 延迟增加 |
| 6 | 文件不存在 | Path.exists() | 跳过该文档，报告 WARN | 该文档不审计 |
| 7 | YAML 解析失败 | yaml.YAMLError | 跳过 frontmatter 提取，仅正文提取 | 部分引用未提取 |
| 8 | 修复后仍有 RED | 自测审计 | 自动回滚到 checkpoint | 修复不生效 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | Prompt 注入嵌入规则文档 | LLM 生成恶意修复文本 | PromptInjectionDefense 5 条正则 + MOD-LLM_SECURITY 安全校验 | 对抗样本测试 |
| 2 | 路径遍历攻击 | 访问非预期文件 | 路径归一化 + 项目根目录边界检查 | `../../etc/passwd` 测试 |
| 3 | 并发修复覆盖 | 数据丢失 | ZephyrLock + 修复队列 + 幂等性 | 100 并发压测 |
| 4 | LLM 幻觉修复 | 错误修复写入 | 输出完整性校验 + 自测审计 + 自动回滚 | 黄金数据集回归 |
| 5 | Token 预算超支 | 成本失控 | per-session 配额 + 全局核算 + 降级 | Budget Enforcer 集成测试 |
| 6 | 超大文档 DoS | 资源耗尽 | 1MB 文档上限 + 优雅跳过 | 10MB 文档测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元-提取器 | ReferenceExtractor | 8 种引用类型提取 | 召回率 >99% |
| 2 | 单元-触发F | 跨文档引用断裂 | 已知断裂引用 | 100% 检出 |
| 3 | 单元-触发G | depends-on 链断裂 | 已知断裂依赖 | 100% 检出 |
| 4 | 单元-安全 | 禁碰规则过滤 | 架构决策/性能参数/安全策略 | 100% 过滤 |
| 5 | 单元-自愈 | 修复→自测→回滚 | 修复成功/修复失败/回滚 | 全路径覆盖 |
| 6 | 集成-管道 | 完整 9 阶段 | 已知过时规则文档 | 与金标准一致 |
| 7 | 集成-回滚 | 错误修复回滚 | 修复后仍有 RED | 回滚后哈希一致 |
| 8 | E2E | 实际 project_rules.md | 全量审计 | 所有触发可追溯证据 |
| 9 | 模糊-对抗 | 空文档/超大/Unicode | 边界条件 | 零崩溃，优雅降级 |
| 10 | 并发-安全 | 100 并发审计 | 同一文档并发修复 | 零数据竞态 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-020 | 必须 | AuditTrail 记录修复操作 | v4+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-LLM_SECURITY | 必须 | LLM Security Gateway 校验 | v4+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm_security\blueprint.md` |
| MOD-INF-026 | 必须 | Asset Inventory 文件存在性查询 | v4+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\asset-inventory\blueprint.md` |
| MOD-INF-021 | 必须 | Rollback System checkpoint/restore | v4+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback-system\blueprint.md` |
| MOD-INF-024 | 必须 | Budget Enforcer Token 预算 | v4+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\budget-enforcer\blueprint.md` |
| MOD-INF-027 | 可选 | AuditOrchestrator 调度协调 | v4+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` |
| MOD-FEEDBACK_LOOP | 可选 | Feedback Loop 发现注入 | v4+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-028` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| reference_extractor.py | trigger_engine.py | ExtractedReferences 是 TriggerEngine 输入 | 检查 ExtractedReferences 非空 |
| trigger_engine.py | safety_boundary.py | TriggerResult 列表是 SafetyBoundary 输入 | 检查 TriggerResult 列表生成 |
| safety_boundary.py | issue_aggregator.py | 过滤后 AuditIssue 是聚合输入 | 检查 AuditIssue 列表 |
| alignment_engine.py | issue_aggregator.py | AlignmentReport 是聚合输入 | 检查 AlignmentReport 生成 |
| issue_aggregator.py | llm_bridge.py | AggregatedIssues 中 RED 问题触发 LLM | 检查 RED 问题存在 |
| llm_bridge.py | self_healer.py | LLMFixResult 是自愈输入 | 检查 LLMFixResult 生成 |
| self_healer.py | fix_prioritizer.py | HealResult 是优先级排序输入 | 检查 HealResult 确定 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| reference_extractor.py | trigger_engine.py | ExtractedReferences | 函数调用 |
| trigger_engine.py | safety_boundary.py | list[TriggerResult] | 函数调用 |
| alignment_engine.py | issue_aggregator.py | AlignmentReport | 函数调用 |
| llm_bridge.py | self_healer.py | LLMFixResult | 异步队列(v5) |
| self_healer.py | fix_prioritizer.py | HealResult | 函数调用 |
| token_budget.py | llm_bridge.py | Token 配额状态 | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 7 个外部依赖 + 12 个内部组件 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖，需 CI 门禁 |
| 3 | 临时时态内容自动清理 | 是 | §5.3 迁移方案执行后需清理 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中，需 pytest+mypy+ruff 验证 |

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
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\semantic-auditor\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\semantic-auditor\` | 测试用例 |
| CLI 入口 | `D:\ZephyrAlpha\scripts\governance\run_semantic_audit.py` | 审计脚本 |
| 黄金数据集 | `D:\ZephyrAlpha\tests\semantic-auditor\golden_dataset\` | 已知案例 |
| 配置文件 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\forbidden_patterns.yaml` | 禁碰规则 |
| 配置文件 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\rule_document_registry.yaml` | 规则文档注册表 |
| 配置文件 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\system_state_registry.yaml` | 系统状态注册表 |
| LLM Prompt | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\llm_bridge_prompt.yaml` | Prompt 版本锁定 |
| Agent Skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\semantic-auditor.md` | 渐进式披露 |
| 审计数据 | `D:\ZephyrAlpha\data\semantic-auditor\` | 报告/checkpoint/日志 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| AuditOrchestrator (MOD-INF-027) | 新增接口 | CT-SEM-001 `audit(rule_documents)→SemanticAuditReport` | 端到端调度测试 |
| AuditTrail (MOD-INF-020) | 新增接口 | CT-SEM-002 `record(AuditEvent)` | 写入验证 |
| LLM Security (MOD-LLM_SECURITY) | 新增接口 | CT-SEM-003 `validate_prompt()/validate_response()` | 安全校验测试 |
| Asset Inventory (MOD-INF-026) | 新增接口 | CT-SEM-004 `file_exists(path)→bool` | 查询验证 |
| Rollback System (MOD-INF-021) | 新增接口 | CT-SEM-006 `create_checkpoint()/restore_checkpoint()` | 回滚验证 |
| Budget Enforcer (MOD-INF-024) | 新增接口 | CT-SEM-008 `check_token_budget(estimated)→bool` | 预算检查验证 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-001 | 治理域 | 语义审计操作需 RBAC 权限 | MOD-INF-018 | 修改此契约必须同步更新对方蓝图 |
| G-CT-007 | 治理域 | LLM 桥接行为需 Agent Spec 约束 | MOD-INF-019 | 修改此契约必须同步更新对方蓝图 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 新增 MOD-INF-028 | 编号注册 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 更新 MOD-INF-028 条目 | 蓝图版本升级 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 新增本蓝图元数据 | 自动扫描 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 新增 MOD-INF-028 依赖 | 依赖注册 |
| 5 | 脚本清单 | `D:\ZephyrAlpha\scripts\script-manifest.yaml` | 新增 run_semantic_audit.py | 脚本注册 |
| 6 | Skill 注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 新增 SKILL-DOM-SEM-001 | Skill 注册 |
| 7 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 新增 MOD-INF-028 10 条依赖 | 依赖注册 |
| 8 | 系统蓝图 | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` | §0 分派表新增语义审计任务 | 分派更新 |
| 9 | 资产索引 | `D:\ZephyrAlpha\data\asset_index\unified-asset-index.yaml` | 自动扫描发现 | 自动 |
| 10 | 项目规则 | `D:\ZephyrAlpha\.trae\rules\project_rules.md` | 强制集成对照表新增语义审计 | 规则更新 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 正则提取遗漏引用（Stage 1 漏检） | 中 | 高 | 黄金数据集持续扩充 + 人工抽样验证 | 风险 |
| 2 | LLM 修复文本质量不一致 | 中 | 中 | 固定 prompt 版本 + 人工 spot-check | 风险 |
| 3 | 禁碰规则过于宽泛 | 低 | 中 | 精确匹配关键词，不做语义推断 | 风险 |
| 4 | 并发审计导致数据竞态 | 中 | 高 | ZephyrLock + 修复队列 + 幂等性 | 风险 |
| 5 | Prompt 注入导致错误修复 | 低 | 高 | PromptInjectionDefense + MOD-LLM_SECURITY | 风险 |
| 6 | 审计系统自身退化未检测 | 低 | 高 | SelfHealthMonitor 黄金数据集回归 | 风险 |
| 7 | Token 预算超支 | 中 | 中 | TokenBudgetManager + 每日/每周配额 | 风险 |
| 8 | 自动修复引入新问题 | 中 | 高 | Stage 7 自测 + 失败自动回滚 | 风险 |
| 9 | SQLite 单写者瓶颈 | 中 | 中 | MOD-INF-016 §〇 幂等性/Outbox/写入缓冲 | 风险 |
| 10 | LLM API 调用产生 Token 成本 | 高 | 中 | per-session 配额 + 全局核算 + 降级 | 负面后果 |
| 11 | 9 阶段管道增加系统复杂度 | 高 | 中 | 每阶段独立可测试 + 降级模式 | 负面后果 |
| 12 | 并发场景需额外基础设施（ZephyrLock+修复队列） | 高 | 中 | 复用 SYS-MASTER 已有组件 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§10 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答编号规则 | ☐ |
| 4 | GOV-DOC-002 路径映射已理解 | 能回答文件该放哪 | ☐ |
| 5 | 每个施工步骤对应明确蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 个 Phase |
| 施工模式 | 扩展（已有 7 个文件 + 新增 9 阶段管道组件） |
| 核心风险 | 9 阶段管道组件与已有文件的功能边界 |
| 目标 generation | 5 — 本次将蓝图从 generation 4 升级到 generation 5 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-020 AuditTrail 可用 | hard | 已施工 | ☐ |
| 2 | MOD-LLM_SECURITY LLM Security 可用 | hard | 已施工 | ☐ |
| 3 | MOD-INF-021 Rollback System 可用 | hard | 已施工 | ☐ |
| 4 | MOD-INF-024 Budget Enforcer 可用 | hard | 已施工 | ☐ |
| 5 | MOD-INF-026 Asset Inventory 可用 | hard | 已施工 | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：1.代码文件存在且非空 2.pytest exit 0 3.mypy 通过 4.ruff 通过

#### 步骤 1：骨架——数据模型 + 引用提取 + 触发检测

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 + §3.1 Stage 1-2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` |
| 验收标准 | models.py + reference_extractor.py + trigger_engine.py 可导入且单元测试通过 |
| 验证命令 | `python -m pytest tests/semantic-auditor/ -k "test_extract or test_trigger" -v` |
| G7 检查项 | 上游文件已列出；下游产出物路径精确；回滚方案=删除新建文件 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-028 | models.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\models.py` |
| MOD-INF-028 | reference_extractor.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\reference_extractor.py` |
| MOD-INF-028 | trigger_engine.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\trigger_engine.py` |

#### 步骤 2：安全边界 + 对齐引擎 + 问题聚合

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.1 Stage 3-5 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` |
| 验收标准 | safety_boundary.py + alignment_engine.py + issue_aggregator.py 可导入且单元测试通过 |
| 验证命令 | `python -m pytest tests/semantic-auditor/ -k "test_safety or test_alignment or test_aggregate" -v` |
| G7 检查项 | 禁碰规则 8 条完整；对齐对 6 对完整；回滚方案=删除新建文件 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-028 | safety_boundary.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\safety_boundary.py` |
| MOD-INF-028 | alignment_engine.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\alignment_engine.py` |
| MOD-INF-028 | issue_aggregator.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\issue_aggregator.py` |
| MOD-INF-028 | forbidden_patterns.yaml | config | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\forbidden_patterns.yaml` |

#### 步骤 3：LLM Bridge + 自愈闭环 + 优先级排序

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.1 Stage 6-8 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` |
| 验收标准 | llm_bridge.py + self_healer.py + fix_prioritizer.py 可导入且集成测试通过 |
| 验证命令 | `python -m pytest tests/semantic-auditor/ -k "test_llm or test_heal or test_prioritize" -v` |
| G7 检查项 | LLM 安全校验集成；回滚系统集成；Token 预算集成 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-028 | llm_bridge.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\llm_bridge.py` |
| MOD-INF-028 | self_healer.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\self_healer.py` |
| MOD-INF-028 | fix_prioritizer.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\fix_prioritizer.py` |
| MOD-INF-028 | token_budget.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\token_budget.py` |
| MOD-INF-028 | llm_bridge_prompt.yaml | config | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\llm_bridge_prompt.yaml` |

#### 步骤 4：影响半径 + 自审计 + CLI + 注册

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.1 Stage 9 + §4.1 + §13 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` + `D:\ZephyrAlpha\scripts\governance\` |
| 验收标准 | blast_radius.py + self_health.py + run_semantic_audit.py 可运行且 E2E 测试通过 |
| 验证命令 | `python -m pytest tests/semantic-auditor/ -k "test_blast or test_self_audit or test_e2e" -v` |
| G7 检查项 | 全注册表同步完成；CLI 全接口可用；黄金数据集通过 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-028 | blast_radius.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\blast_radius.py` |
| MOD-INF-028 | self_health.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\self_health.py` |
| MOD-INF-028 | cross_session.py | code | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\cross_session.py` |
| MOD-INF-028 | run_semantic_audit.py | script | `D:\ZephyrAlpha\scripts\governance\run_semantic_audit.py` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 模型/提取器/触发器编译失败 | 删除新建的 3 个 .py 文件 |
| 2 | 安全边界/对齐引擎测试失败 | 删除新建的 3 个 .py + 1 个 .yaml 文件 |
| 3 | LLM/自愈/优先级集成失败 | 删除新建的 4 个 .py + 1 个 .yaml 文件 |
| 4 | E2E 测试失败 | 删除新建文件，回滚注册表更新 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | models.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\models.py` | ☐ | ☐ | ☐ |
| 2 | reference_extractor.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\reference_extractor.py` | ☐ | ☐ | ☐ |
| 3 | trigger_engine.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\trigger_engine.py` | ☐ | ☐ | ☐ |
| 4 | safety_boundary.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\safety_boundary.py` | ☐ | ☐ | ☐ |
| 5 | alignment_engine.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\alignment_engine.py` | ☐ | ☐ | ☐ |
| 6 | llm_bridge.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\llm_bridge.py` | ☐ | ☐ | ☐ |
| 7 | self_healer.py | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\self_healer.py` | ☐ | ☐ | ☐ |
| 8 | run_semantic_audit.py | `D:\ZephyrAlpha\scripts\governance\run_semantic_audit.py` | ☐ | ☐ | ☐ |

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
| 规则文档数 | ~36 | rule_document_registry.yaml 条目数 |
| AI 并发 Session | 1 | 隐含假设 |
| LLM 并发槽位 | 4 | max_concurrent 配置 |
| 全量扫描耗时 | 未定义 | 无全量基准 |
| 对齐对数 | 10 | alignment_pairs 配置 |
| Token 日预算 | 5,000 | DAILY_BUDGET 配置 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-SEM-001 | 规则文档 36→5,000+，手工注册不可行 | KBG-0056 分层自动发现 | 文档数 >200 |
| GAP-SEM-002 | LLM 4 并发 vs 100 Session | KBG-0052 异步队列 4→12 workers | 并发 >10 |
| GAP-SEM-003 | 全量审计无增量模式 | KBG-0050 增量审计默认 | 文档数 >100 |
| GAP-SEM-004 | 跨文档引用 O(n²) | KBG-0051 cross_ref_index.db | 引用关系 >1,000 |
| GAP-SEM-005 | ScanMutex TOCTOU 竞态 | KBG-0054 ZephyrLock 升级 | 并发 >2 |
| GAP-SEM-006 | SelfHealer 并发争用 | KBG-0055 修复队列+幂等 | 并发 >2 |
| GAP-SEM-007 | 审计结果无缓存 | KBG-0053 L1 Mem + L2 SQLite | 重复审计 >5/min |
| GAP-SEM-008 | Checkpoint 无限增长 | KBG-0060 轻量化+7天清理 | 文件数 >100 |
| GAP-SEM-009 | Token 预算无多进程核算 | KBG-0059 SQLite 持久化 | 并发 >1 |
| GAP-SEM-010 | 无事件驱动触发 | KBG-0058 git hook→Orchestrator→SA | 手动触发频率 >10/天 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v4.0.0 | 4 | 基线 | Peer Service 提升 | ⚠️ |
| v5.0.0 | 4 | 容量升级 | 13 项瓶颈方案+11 KB 决策记录 | ❌ |
| v6.1.0 | 5 | 模板对齐 | v3.5 蓝图模板合规+章节重排 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-SEM-001 | 规则文档注册表规模爆炸 | P0 | v5.0.0 | 待施工 |
| GAP-SEM-002 | LLM Bridge 并发容量 | P0 | v5.0.0 | 待施工 |
| GAP-SEM-003 | 增量审计缺失 | P0 | v5.0.0 | 待施工 |
| GAP-SEM-004 | 跨文档引用 O(n²) | P0 | v5.0.0 | 待施工 |
| GAP-SEM-005 | ScanMutex TOCTOU | P1 | v5.0.0 | 待施工 |
| GAP-SEM-006 | SelfHealer 争用 | P1 | v5.0.0 | 待施工 |
| GAP-SEM-007 | 审计结果缓存 | P1 | v5.0.0 | 待施工 |
| GAP-SEM-008 | Checkpoint 爆炸 | P2 | v5.0.0 | 待施工 |
| GAP-SEM-009 | Token 多进程核算 | P1 | v5.0.0 | 待施工 |
| GAP-SEM-010 | 事件驱动触发 | P2 | v5.0.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| CrossRefIndexBuilder | GAP-SEM-004 | cross_ref_index.py | Phase 1 | 待施工 |
| AuditResultCache | GAP-SEM-007 | audit_cache.py | Phase 1 | 待施工 |
| LLMFixWorker (async) | GAP-SEM-002 | llm_bridge.py (升级) | Phase 1 | 待施工 |
| ZephyrLock (替换 ScanMutex) | GAP-SEM-005 | scan_mutex.py (替换) | Phase 1 | 待施工 |
| HealQueue | GAP-SEM-006 | heal_queue.py | Phase 1 | 待施工 |
| TokenPersist (SQLite) | GAP-SEM-009 | token_budget.py (升级) | Phase 1 | 待施工 |
| TriggerFDebouncer | GAP-SEM-004 | debouncer.py | Phase 2 | 待施工 |
| EventDrivenTrigger | GAP-SEM-010 | event_trigger.py | Phase 2 | 待施工 |
| RuleDocAutoDiscovery | GAP-SEM-001 | auto_discovery.py | Phase 2 | 待施工 |
| LLMBatchProcessor | GAP-SEM-002 | llm_bridge.py (升级) | Phase 2 | 待施工 |
| FullScanSharder (16 shard) | GAP-SEM-003 | sharder.py | Phase 2 | 待施工 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> 本节同时覆盖原 §7 备选方案——"选项"列已包含备选方案信息。本节同时覆盖原 §15 后果——负面后果合并到 §14 风险，正面后果与 §1 目标重复。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-SEM-01 | 2 类纯语义触发（F+G）vs 12 类混合触发 | A:12类/B:2类 | B | 本体论收敛——10类二元触发不需要语义理解 | 2026-05-08 |
| 2 | D-SEM-02 | LLM 只润色不做判断 | A:LLM判断+B:只润色 | B | "不确定=不动"原则 | 2026-05-08 |
| 3 | D-SEM-03 | Peer Service vs Orchestrator 子系统 | A:子系统/B:Peer | B | 独立测试/迭代/部署/冷启动 | 2026-05-08 |
| 4 | D-SEM-04 | 增量审计默认 vs 全量默认 | A:全量/B:增量 | B | 5000文档全量>3.5h不可接受 | 2026-05-12 |
| 5 | D-SEM-05 | ZephyrLock vs ScanMutex | A:ScanMutex/B:ZephyrLock | B | TOCTOU竞态+对齐SYS-MASTER KBG-0037 | 2026-05-12 |
| 6 | D-SEM-06 | 修复队列 vs 并发抢占 | A:并发/B:队列 | B | 串行化修复避免覆盖+幂等性 | 2026-05-12 |
| 7 | D-SEM-07 | Token SQLite 持久化 vs 内存 | A:内存/B:SQLite | B | 多进程全局核算 | 2026-05-12 |
| 8 | D-SEM-08 | 全局引用索引 vs 每次遍历 | A:遍历/B:索引 | B | O(n²)→O(1) | 2026-05-12 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移——AI 自行决定 |
| 9 | **蓝图必须自包含** | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议** | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
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

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | ScanMutex 实现 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\scan_mutex.py` | 覆盖型 | ZephyrLock (SYS-MASTER) | KBG-0054 替换→交叉验证→标记 deprecated→Phase 4 物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012+MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 代码头部标准 |
| 10 | 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 产出物规格化 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-INF-023 Drift Detector | `D:\ZephyrAlpha\src\zephyr\infra_ops\drift-detector\` | 检测代码与契约漂移 | 检测代码漂移≠检测规则文档语义断裂 |
| 2 | check_contract_code_drift.py | `D:\ZephyrAlpha\scripts\governance\d5_architecture\checkers\check_contract_code_drift.py` | 检查契约漂移 | 检查契约≠检查规则文档声明-实际一致性 |
| 3 | MOD-INF-020 AuditTrail | `D:\ZephyrAlpha\src\zephyr\infra_ops\audit-trail\` | 审计系统 | 审计 AI 行为≠审计规则文档自身 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | semantic-auditor 包 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` | 修改+新建 | 新增 9 阶段管道组件 |
| 2 | 测试目录 | `D:\ZephyrAlpha\tests\semantic-auditor\` | 新建 | 测试用例+黄金数据集 |
| 3 | CLI 脚本 | `D:\ZephyrAlpha\scripts\governance\run_semantic_audit.py` | 新建 | 审计入口 |
| 4 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\semantic-auditor\blueprint.md` | 修改 | 本次升级 |
| 5 | Agent Skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\semantic-auditor.md` | 新建 | 渐进式披露 |
| 6 | 审计数据目录 | `D:\ZephyrAlpha\data\semantic-auditor\` | 新建 | 报告/checkpoint/日志 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 语义审计架构设计 | **本文档 §1-§10** | 已取代的旧版蓝图 |
| 语义审计施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 语义审计接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 2 | `D:\ZephyrAlpha\scripts\governance\run_semantic_audit.py` | §4 数据模型、§11 产出物路径 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\semantic-auditor\` | §4 数据模型、§11 产出物路径 |

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

### 蓝图特有：触发 F——跨文档引用语义断裂

> 来源：v3.0.0 本体论收敛
> 仅本蓝图需要：跨文档引用格式多样性需要语义解析，纯正则不够
> 不可砍理由：砍掉=丢失 SemanticAuditor 核心价值

| 属性 | 值 |
|------|-----|
| **确定性** | **95%** — 锚点/章节号存在性是布尔值，但改名后是否等效不确定 |
| **检测逻辑** | 文档 A 引用 "B §N" → HeadingExtractor 解析 B → §N 不存在 = 触发 |
| **严重性** | RED — 引用断裂比文件失联更隐蔽 |
| **可自动修复** | ❌ — 被引用文档结构变化可能很大 |

### 蓝图特有：触发 G——Depends-On 治理意图断裂

> 来源：v3.0.0 本体论收敛
> 仅本蓝图需要：depends_on 的 why 字段是自然语言治理意图，需要 LLM 理解
> 不可砍理由：砍掉=丢失依赖链断裂检测能力

| 属性 | 值 |
|------|-----|
| **确定性** | **98%** — target 存在于 module-registry + at 章节存在于目标文件 |
| **检测逻辑** | 解析 depends_on → 查 module-registry 定位目标文件 → 读文件解析 headings → § 是否存在 |
| **严重性** | RED — 依赖断裂破坏治理体系连线 |
| **可自动修复** | ❌ — at 章节号需人工重新映射 |

### 蓝图特有：LLM Bridge 安全边界——LLM 不做判断

> 来源：v1.0.0 核心设计决策
> 仅本蓝图需要：LLM Bridge 是不可替代能力，安全边界是核心约束
> 不可砍理由：砍掉=LLM 可能越权判断

| LLM 做什么 | LLM 不做什么 |
|-----------|------------|
| 把结构化修复数据转为自然语言文档 | 判断"这条规则是否过时" |
| 根据模板生成更新后的规则段落文本 | 判断"这个引用是否应该删除" |
| 格式化输出为规则文档的 Markdown 段落 | 修改规则文档的逻辑和语义 |

### 蓝图特有：置信度模型——判定金字塔

> 来源：v1.0.0 核心设计
> 仅本蓝图需要：语义审计的确定性分级是安全边界的基础
> 不可砍理由：砍掉=安全边界失去判定依据

| 区域 | 确定性 | 操作 |
|------|:---:|------|
| 禁区 | — | 绝对不动（命中安全边界） |
| 不确定区 | <95% | 也不动 |
| 确定区域 | ≥95% | 只有这里可以操作（F:95%/G:98%） |

### 蓝图特有：禁碰规则（8 条）

> 来源：v1.0.0 + v1.1.0 补完
> 仅本蓝图需要：规则文档中的架构决策/性能参数/安全策略不可自动修改
> 不可砍理由：砍掉=自动修复可能破坏关键约束

| 禁碰 ID | 描述 | 检测方式 |
|:---:|------|---------|
| F-001 | 架构决策 | 关键词 "选择"/"决定"/"架构"/"为什么" |
| F-002 | 跨模块契约 | 关键词 "CT-"/"契约"/"depends_on" |
| F-003 | 性能参数 | 关键词 "TTL"/"超时"/"配额"/"max_" |
| F-004 | 安全策略 | 关键词 "密钥"/"加密"/"L4"/"secret" |
| F-005 | 人为定义的阈值 | 关键词 ">"/"<"/"≥"/"阈值"/"门限" |
| F-006 | Owner/Maintainer 声明 | 关键词 "owner"/"belongs_to" |
| F-007 | 版本锁定声明 | 关键词 "version_lock"/"frozen"/"不可改" |
| F-008 | AI 角色指令 | 关键词 "ai_role_instruction"/"MUST"/"SHALL" |

### 蓝图特有：9 阶段管道 Stage 表

> 来源：v1.0.0 核心 + v1.1.0~v1.2.0 补完
> 仅本蓝图需要：9 阶段管道是核心执行架构
> 不可砍理由：砍掉=施工者不知道管道怎么执行

| Stage | 输入 | 输出 | 调用 LLM | RULE 合规 |
|:---:|------|------|:---:|------|
| 1 | 规则文档 Markdown/YAML | ExtractedReferences | ❌ | RULE-SEVEN（批量IO并行） |
| 2 | ExtractedReferences | F+G 触发命中结果 | ❌ | RULE-ONE（原子写入） |
| 3 | 触发命中结果 | 安全过滤后可操作问题 | ❌ | RULE-THREE（删除禁碰内置） |
| 4 | 注册表清单+磁盘清单 | AlignmentReport | ❌ | RULE-ONE（原子写入） |
| 5 | Stage 2+3+4 结果 | 去重聚合问题清单 | ❌ | — |
| 6 | RED 问题+修复文本请求 | LLMFixResult | ✅（仅此处） | RULE-ZERO（写前加锁） |
| 7 | 修复文本+规则文档路径 | HealResult | ❌（机械应用） | RULE-THREE（删前审判） |
| 8 | 审计报告+RED 问题 | PrioritizedFix+DiffPreview | ❌ | — |
| 9 | 修复后文档+全量规则文档 | BlastReport | ❌（9c 可选调 LLM 仅自检） | RecursionGuard |

### 蓝图特有：对齐对清单（6 对保留）

> 来源：v2.0.0 新增架构域对齐对 + v3.0.0 精简
> 仅本蓝图需要：6 对语义相关对齐对是 AlignmentEngine 的核心配置
> 不可砍理由：砍掉=对齐检测无法执行

| pair_id | 注册表源 | 磁盘源 | 严重性 |
|---------|---------|--------|:---:|
| ALIGN-SCRIPT-001 | scripts/script-manifest.yaml | scripts/ | RED |
| ALIGN-GATE-001 | src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml | src/zephyr/gov_enforcement/rule_enforcement/ | RED |
| ALIGN-MODULE-001 | docs/03_modules/blueprint_registry.yaml | src/zephyr/ | RED |
| ALIGN-BLUEPRINT-001 | docs/03_modules/blueprint_registry.yaml | docs/03_modules/ | YELLOW |
| ALIGN-DEPENDENCY-001 | cross-module-dependency-registry.yaml | src/zephyr/ | YELLOW |
| ALIGN-SKILL-001 | src/zephyr/agent-spec/skill-registry.yaml | src/zephyr/agent-spec/ | YELLOW |

### 蓝图特有：跨模块集成契约全表（10 条）

> 来源：v1.0.0 二阶补完
> 仅本蓝图需要：10 条契约定义了与其他模块的交互边界
> 不可砍理由：砍掉=集成时不知道接口和 SLA

| 契约 ID | 提供方 | 消费方 | 接口方法 | SLA |
|---------|--------|--------|---------|-----|
| CT-SEM-001 | MOD-INF-028 | MOD-INF-027 | `audit(rule_documents)→SemanticAuditReport` | <30s/doc |
| CT-SEM-002 | MOD-INF-020 | MOD-INF-028 | `record(AuditEvent)` | <100ms |
| CT-SEM-003 | MOD-LLM_SECURITY | MOD-INF-028 | `validate_prompt()/validate_response()` | <500ms |
| CT-SEM-004 | MOD-INF-026 | MOD-INF-028 | `file_exists(path)→bool` | <50ms |
| CT-SEM-005 | MOD-FEEDBACK_LOOP | MOD-INF-028 | `ingest_finding(SemanticAuditReport)` | <1s |
| CT-SEM-006 | MOD-INF-021 | MOD-INF-028 | `create_checkpoint()/restore_checkpoint()` | <500ms |
| CT-SEM-007 | MOD-GATE_ENGINE | MOD-INF-028 | `gate_exists(gate_id)→bool` | <50ms |
| CT-SEM-008 | MOD-INF-024 | MOD-INF-028 | `check_token_budget(estimated)→bool` | <50ms |
| CT-SEM-009 | MOD-INF-005 | MOD-INF-028 | `list_registered_scripts()→list[str]` | <100ms |
| CT-SEM-010 | MOD-INF-023 | MOD-INF-028 | `get_drift_signals(doc)→list[DriftSignal]` | <500ms |

### 蓝图特有：自身健康 SLI（7+5 项）

> 来源：v1.0.0 三阶补完 + v5.0.0 容量 SLI
> 仅本蓝图需要：12 项 SLI 是 SelfHealthMonitor 的核心配置
> 不可砍理由：砍掉=无法检测自身退化

| SLI | 指标 | 健康阈值 | 数据源 |
|-----|------|:---:|------|
| 审计延迟 | P95 管道耗时 | <30s | 自身计时 |
| 触发召回率 | 黄金数据集检出率 | >99% | 黄金数据集回归 |
| 安全误拦率 | 该过被拦概率 | <0.5% | 人工审查样本 |
| LLM 可用率 | Stage 6 成功率 | >90% | LLMBridge 统计 |
| Token 效率 | 每次审计 Token 用量 | ≤500 tokens | Budget Enforcer |
| 自愈成功率 | Stage 7 修复成功率 | >80% | SelfHealer 统计 |
| 退化评估 | 连续 N 次性能趋势 | 无连续退化 | 时间序列分析 |
| SLI-CAP-SEM-01 | 并发审计数 | <max_concurrent | 运行时计数 |
| SLI-CAP-SEM-02 | LLM Fix Queue 深度 | <50 | 队列监控 |
| SLI-CAP-SEM-03 | 审计缓存命中率 | >60% | 缓存统计 |
| SLI-CAP-SEM-04 | 全局引用索引新鲜度 | <300s | 索引 mtime |
| SLI-CAP-SEM-05 | SelfHealer 修复队列长度 | <20 | 队列监控 |

### 蓝图特有：v5.0.0 容量升级 KB 决策记录 决策（11 条）

> 来源：v5.0.0 容量升级方案
> 仅本蓝图需要：11 条 KB 决策记录 是容量升级的设计决策依据
> 不可砍理由：砍掉=施工者不知道为什么这样设计容量升级

| KBG-ID | 标题 | 覆盖瓶颈 |
|--------|------|:---:|
| KBG-0050 | 增量审计模式——replace --all as default | #3 |
| KBG-0051 | 全局引用索引 cross_ref_index.db | #4,#5,#8 |
| KBG-0052 | LLM Bridge 异步队列——4→12 workers | #2 |
| KBG-0053 | 审计结果缓存——L1 Mem + L2 SQLite | #9,#12 |
| KBG-0054 | ScanMutex → ZephyrLock 升级 | #7 |
| KBG-0055 | SelfHealer 修复队列+幂等性 | #7 |
| KBG-0056 | Rule Document Registry 分层自动发现 | #1 |
| KBG-0057 | 容量 SLI 新增 5 项 | #10 |
| KBG-0058 | 事件驱动触发集成 | #11 |
| KBG-0059 | Token 预算多 Session 核算 | #2,#13 |
| KBG-0060 | CrossSessionContinuity 轻量化 | #12 |

### 蓝图特有：v5.0.0 容量升级 3 Phase 路线

> 来源：v5.0.0 容量升级方案
> 仅本蓝图需要：3 Phase 路线是容量升级的施工顺序
> 不可砍理由：砍掉=施工者不知道先做什么后做什么

**Phase 1：容量底座**

| 任务 | 描述 | 依赖 |
|------|------|------|
| PH1-SEM-01 | 增量审计模式 | AuditOrchestrator 双通道调度 |
| PH1-SEM-02 | 全局引用索引 cross_ref_index.db | PH1-SEM-01 |
| PH1-SEM-03 | 审计结果缓存 L1+L2 | shared/cache.py 升级 |
| PH1-SEM-04 | LLM Bridge 异步队列 | shared/limiter.py 分区限流 |
| PH1-SEM-05 | ZephyrLock 替换 ScanMutex | SYS-MASTER KBG-0037 |
| PH1-SEM-06 | SelfHealer 修复队列+幂等 | PH1-SEM-05 |
| PH1-SEM-07 | Token 计数器持久化 SQLite | MOD-INF-024 |

**Phase 1 验收**：增量 30 文档 P95<60s / detect-only P95<15s / 全局索引构建<5min / 100 并发零竞态

**Phase 2：智能调度**

| 任务 | 描述 | 依赖 |
|------|------|------|
| PH2-SEM-08 | 引用智能过滤 | PH1-SEM-02 |
| PH2-SEM-09 | 触发 F 去抖合并 | Phase 1 |
| PH2-SEM-10 | 事件驱动触发集成 | AuditOrchestrator 施工 |
| PH2-SEM-11 | Rule Doc Registry 分层自动发现 | MOD-INF-026 |
| PH2-SEM-12 | LLM 修复批处理 | PH1-SEM-04 |
| PH2-SEM-13 | 全量审计分片 16 shard | SYS-MASTER Worker Pool |

**Phase 2 验收**：去抖后触发频率降 70% / LLM 调用减少 60% / 全量 detect-only<2h

**Phase 3：满负荷优化**

| 任务 | 描述 | 依赖 |
|------|------|------|
| PH3-SEM-14 | 100 AI 并发全链路压测 | Phase 2 |
| PH3-SEM-15 | 容量 SLI 面板 | MOD-INF-015 |
| PH3-SEM-16 | 自动降级策略 | Phase 2 |
| PH3-SEM-17 | 自愈闭环完全体 | Phase 2 |
| PH3-SEM-18 | 长期数据归档 | Phase 2 |

**Phase 3 验收**：100 并发稳定 24h / 全量周检<3h / 缓存命中率>60% / Token 误差<1%

### 蓝图特有：RULE-ZERO~NINE 对齐矩阵

> 来源：v1.0.0 一阶补完
> 仅本蓝图需要：确保每个设计决策对应项目硬规则
> 不可砍理由：砍掉=无法验证合规

| 项目规则 | 本模块如何遵守 | 验证方式 |
|---------|--------------|---------|
| RULE-ZERO（锁协议） | 写入规则文件前 MUST 走 lock_files.py 三步 | check→acquire→写入→release |
| RULE-ONE（并发写入） | 所有文件输出用 temp-file + atomic rename | _write_atomic() 内部实现 |
| RULE-TWO（反孤儿） | 本蓝图自含 + 所有产出均注册（§13 全登记表） | audit_registration.py 零孤儿 |
| RULE-THREE（删除协议） | 语义审计建议"删除"时 MUST 先经三步审判 | SafetyBoundary.should_delete() 内置 |
| RULE-FOUR（创建即注册） | 所有 .py 文件通过 scaffold.py 创建 | scaffold.py module semantic-auditor ... |
| RULE-FIVE（零残留） | 审计临时文件 session 结束时清理 | .cleanup() 在 __exit__ 中调用 |
| RULE-SIX（任务粒度） | 本蓝图创建时触发了指标+3 已建 TaskCard | TaskCard 在数据库中有记录 |
| RULE-SEVEN（多线程强制） | TriggerEngine 批量文件存在性检查用 ThreadPoolExecutor | _batch_exists() 实现 |
| RULE-EIGHT（功能发现） | 本模块创建前已搜索：无已有语义审计功能 | 搜索记录见类似功能章节 |
| RULE-NINE（资产认知） | 本蓝图在冷启动 STEP 4.5 unified-asset-index.yaml 中可发现 | 资产盘点自动扫描 |

### 蓝图特有：冷启动发现链

> 来源：v1.0.0 一阶补完
> 仅本蓝图需要：确保新 AI Session 能发现本模块
> 不可砍理由：砍掉=本模块成为孤儿功能

| 路径 | 发现方式 |
|------|---------|
| 路径 1 | SYS-MASTER-001 §0 分派表 → 任务域"语义审计"→ 导航 MOD-INF-028 |
| 路径 2 | registry_of_registries.yaml → REG-MOD-ALPHA_SIGNAL_DOMAIN → 搜索 "semantic"/"audit" → MOD-INF-028 |
| 路径 3 | skill-registry.yaml → task_keywords: "semantic"/"staleness"/"rule-audit" → SKILL-DOM-SEM-001 |
| 路径 4 | project_rules.md 强制集成对照表 → "修改 YAML 契约/配置" → 触发语义审计 |
| 路径 5 | CLI 入口自描述 → `python scripts/governance/run_semantic_audit.py --help` |

| 用户/任务关键词 | 匹配 Skill | 加载方式 |
|---------------|-----------|---------|
| `semantic` `语义` `审计规则` `过时文档` | SKILL-DOM-SEM-001 | `progressive_load("semantic-auditor")` |
| `rule staleness` `规则过时` `文件失联` | SKILL-DOM-SEM-001 | 同上 |
| `双向对齐` `孤儿检测` `僵尸条目` | SKILL-DOM-SEM-001 | 同上 |

### 蓝图特有：MOD-INF-020 vs MOD-INF-028 职责边界

> 来源：v1.0.1 术语冲突消除
> 仅本蓝图需要：两个审计模块的术语边界
> 不可砍理由：砍掉=术语混淆导致重复造轮子

| 维度 | MOD-INF-020 AuditTrail | MOD-INF-028 SemanticAuditor | 关系 |
|------|:---|:---|:---|
| 审计对象 | AI 操作行为 | 规则文档自身 | 互补 |
| "漂移检测" | 行为漂移（MOD-INF-020 术语） | 规则过时检测（staleness） | 术语属 MOD-INF-020 |
| 文件对齐检查 | ❌ | Stage 4 AlignmentEngine | 唯一拥有者 |
| LLM 修复生成 | ❌ | Stage 6 LLMBridge | 唯一拥有者 |

### 蓝图特有：CLI 入口

> 来源：v1.0.0 五阶补完
> 仅本蓝图需要：CLI 是人机交互入口
> 不可砍理由：砍掉=无法手动触发审计

```bash
python scripts/governance/run_semantic_audit.py --doc project_rules.md          # 单文档审计
python scripts/governance/run_semantic_audit.py --all                           # 全量审计
python scripts/governance/run_semantic_audit.py --doc X --detect-only           # 仅检测（零Token）
python scripts/governance/run_semantic_audit.py --doc X --auto-fix              # 自动修复
python scripts/governance/run_semantic_audit.py --doc X --dry-run               # 干跑模式
python scripts/governance/run_semantic_audit.py --doc X --output json           # JSON 输出
python scripts/governance/run_semantic_audit.py --doc X --output yaml           # YAML 输出
python scripts/governance/run_semantic_audit.py --health-check                  # 健康自检
```

### 蓝图特有：自动化调度

> 来源：v1.0.0 六阶补完
> 仅本蓝图需要：Cron 调度是一人开发+AI 维护的运维必需
> 不可砍理由：砍掉=审计只能手动触发

| 调度名 | Cron | 命令 |
|--------|------|------|
| 每日语义审计 | `0 3 * * *` | `run_semantic_audit.py --all --detect-only --output yaml` |
| 每周自动修复 | `0 4 * * 0` | `run_semantic_audit.py --all --auto-fix --dry-run` |
| 健康自检 | `0 * * * *` | `run_semantic_audit.py --health-check` |
