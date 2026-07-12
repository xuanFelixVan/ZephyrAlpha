---
module_id: MOD-INF-029
submodule_path: src/zephyr/security/access_control/orphan_judge
title: "Orphan Judge 蓝图 — 孤儿判定器·三决策树处置"
doc_type: blueprint
status: Active
version: "2.1.0"
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
generation: 3
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
construction_progress: scaffold
actual_disk_path: "src/zephyr/security/access_control/orphan_judge/"
summary: "孤儿判定子系统——五层分级价值判定引擎，对孤儿文件执行注册检查→引用图→功能重复→独特价值→独立价值判定，输出六种处置建议。"
tags: [orphan-judgment, asset-lifecycle, dedup, value-assessment, extract-merge, decision-tree, confidence-scoring, reference-graph, swid-tag, auto-governance, MOD-INF-029]
priority: P1
activation_phase: current
runtime_plane: warm
depends_on:
  - {target: "MOD-INF-017", at: "§2", why: "Code Dedup Engine——L2功能重复检测的语义相似度引擎"}
  - {target: "MOD-INF-020", at: "full", why: "Audit Trail——每一次孤儿生死判决MUST记录不可变审计日志"}
  - {target: "MOD-INF-026", at: "§1", why: "Asset Inventory——孤儿文件的元数据来源+资产对账引擎"}
  - {target: "MOD-INF-023", at: "§6.28", why: "Drift Detector——漂移事件与孤儿判定的双向桥接+漂移预算约束"}
  - {target: "MOD-INF-022", at: "§3", why: "Escalation Protocol——低置信度判定升级+安全围栏触发升级"}
  - {target: "MOD-INF-018", at: "§4", why: "Agent RBAC——删除操作的权限校验+AUTO_GUARD后验"}
  - {target: "MOD-KB-001", at: "§4.5", why: "Knowledge Base——判定决策记录的查询与写入"}
  - {target: "MOD-INF-027", at: "section 4", why: "Audit Orchestrator (编排)"}
references:
  - {id: "MOD-INF-027", at: "full", why: "Audit Orchestrator——OrphanJudge作为Phase 3修复阶段的核心子系统"}
  - {id: "MOD-INF-031", at: "§2", why: "AutoFix Engine——提取融合和注册保留的最终执行由AutoFixEngine完成"}
  - {id: "MOD-FEEDBACK_LOOP", at: "§2", why: "Feedback Loop——误判反馈回写优化判定规则"}
  - {id: "MOD-INF-013", at: "full", why: "Governance MCP Server——orphan_judge MCP Tool暴露入口"}
  - {id: "MOD-INF-019", at: "full", why: "Agent Spec——SKILL-DOM-ORP-001技能注册与发现"}
  - {id: "MOD-GATE_ENGINE", at: "§2", why: "Phase Manager——gate_orphan_judge门禁检查注册"}
responsibility_domain: 
build_status: planned
design_maturity: design
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
蓝图 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/check_blueprint_compliance.py <蓝图路径>
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  §0: "代码对齐验证"
  §0.1: "代码文件清单"
  §0.2: "对齐验证矩阵"
  §0.3: "版本-代码映射"
  §1: "设计背景与目标"
  §1.1: "背景"
  §1.2: "目标"
  §1.3: "不包含的目标"
  §1.4: "运行场景约束"
  §2: "模块边界"
  §2.1: "职责范围"
  §2.2: "不包含的职责"
  §3: "架构设计"
  §3.1: "组件架构"
  §3.2: "数据流"
  §3.3: "状态生命周期"
  §4: "接口契约"
  §4.1: "公共 API"
  §4.2: "数据模型"
  §4.3: "输入契约"
  §4.4: "输出契约"
  §4.5: "MCP 接口"
  §4.6: "契约版本"
  §5: "约束条件"
  §5.1: "技术约束"
  §5.2: "容量估算"
  §5.3: "迁移"
  §6: "错误处理"
  §8: "安全考量"
  §9: "测试策略"
  §10: "依赖关系"
  §10.1: "依赖声明"
  §10.2: "依赖图对齐声明"
  §10.3: "内部依赖图"
  §10.4: "自动化规格"
  §11: "产出物"
  §12: "集成目标"
  §13: "需要更新"
  §14: "风险"
  §16: "施工指引"
  §17: "容量升级"
  §18: "决策记录"
  pre_1: "Vibe Coding"
  pre_2: "安全删除"
  pre_3: "必备链接"
  pre_4: "已有类似功能"
  pre_5: "涉及的文件范围"
END_REQUIRED_SECTIONS
-->

# Orphan Judge 蓝图 — 孤儿判定器·三决策树处置

> module_id: MOD-INF-029 | version: 2.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/orphan-judge/ | generation: 3 | construction_progress: scaffold

## 概述

OrphanJudge 是孤儿文件的资产生死判决引擎——解决"文件不在任何登记表里，该活还是该死"的问题。核心职责：对每个孤儿文件执行五层分级价值判定（L0注册检查→L1引用图可达性→L2功能重复→L3独特价值→L4独立价值），输出六种确定性处置建议（NOT_ORPHAN/REGISTER/EXTRACT_AND_MERGE/DELETE/DEPRECATE_FIRST/ESCALATE）。当前规模~400文件/60孤儿，目标容量10,000脚本/1,500模块/100 AI并发。上游依赖audit_registration.py/orphan_scanner.py/reconciler.py三个发现源，下游被MOD-INF-031 AutoFixEngine消费执行。

| `orphan_detector.py` |
| `orphan_detector.py` |
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

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-029`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3 | 包初始化+__all__导出 | 已实现 | — |
| 2 | `orphan_detector.py` | §3.2 | 孤儿检测器（从runtime/整合） | 已实现 | — |
| 3 | `__main__.py` | §4.1 | CLI入口 | 未实现 | — |
| 4 | `models.py` | §4.2 | 数据模型（10个Pydantic Model） | 未实现 | — |
| 5 | `judge.py` | §4.1 | OrphanJudge主控类（5层全链路+12行决策表） | 已实现 | — |
| 6 | `registration_checker.py` | 蓝图特有§B1 | L0注册检查（14候选注册表+__all__扫描） | 已实现 | — |
| 7 | `reference_graph_engine.py` | 蓝图特有§B2 | L1引用图引擎（import链遍历） | 已实现 | — |
| 8 | `duplicate_detector.py` | 蓝图特有§B1 | L2功能重复检测（语义相似度） | 已实现 | — |
| 9 | `unique_analyzer.py` | 蓝图特有§B1 | L3独特价值检测（AST节点比对） | 已实现 | — |
| 10 | `standalone_evaluator.py` | 蓝图特有§B1 | L4独立价值评估（六指标加权） | 已实现 | — |
| 11 | `decision_table.py` | 蓝图特有§B3 | 决策表（12行路由） | 已实现 | — |
| 12 | `safety_fence.py` | §8 | 安全围栏（6层检查） | 已实现 | — |
| 13 | `deprecation_tracker.py` | 蓝图特有§B4 | 废弃追踪 | 已实现 | — |
| 14 | `cascade_analyzer.py` | 蓝图特有§B5 | 级联清理 | 已实现 | — |
| 15 | `orphan_collector.py` | §3.2 | 统一收集器（3源编排） | 已实现 | — |
| 16 | `report_generator.py` | §4.1 | 报告生成 | 未实现 | — |
| 17 | `config_loader.py` | §5.1 | 配置加载 | 未实现 | — |
| 18 | `db.py` | §5.1 | SQLite持久化 | 未实现 | — |
| 19 | `drift_bridge.py` | §12 | Drift Detector桥接 | 未实现 | — |
| 20 | `escalation_bridge.py` | §12 | Escalation桥接 | 未实现 | — |
| 21 | `rbac_bridge.py` | §12 | RBAC桥接 | 未实现 | — |
| 22 | `kb_bridge.py` | §12 | KB桥接 | 未实现 | — |
| 23 | `feedback_bridge.py` | §12 | Feedback Loop桥接 | 未实现 | — |
| 24 | `mcp_integration.py` | §4.5 | MCP Server Tool注册 | 未实现 | — |
| 25 | `swid_tag.py` | 蓝图特有§B6 | SWID Tag读写 | 未实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = scaffold → __init__.py存在且非空 | `type D:\ZephyrAlpha\src\zephyr\orphan-judge\__init__.py` | ☑ |
| actual_disk_path与§11业务代码路径一致 | 对比frontmatter与§11 | ☑ |
| 蓝图描述的类/函数名=代码中的类/函数名 | `grep "class\|def" D:\ZephyrAlpha\src\zephyr\orphan-judge\*.py` | ☑ |
| §0.1代码文件清单与代码目录一致 | `dir D:\ZephyrAlpha\src\zephyr\orphan-judge\` | ☑ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | orphan_detector.py | 五层判定+决策表+围栏+集成 | 待施工 |
| v2.0.0 (模板升级) | orphan_detector.py | 五层判定+决策表+围栏+集成 | 待施工 |
| v2.1.0 (v3.5模板对齐) | 13/25文件（5层全链路完成） | 12个：__main__/models/report/config/db+6 bridge+swid | L1核心已完成，L2集成+支撑待施工 |

---

## §1 设计背景与目标

### 1.1 背景

项目有~400个.py文件，约15%（60个）不在任何注册表中。现有三个独立孤儿检测能力（audit_registration.py/orphan_scanner.py/reconciler.py）各自只做发现、不做判定。RULE-THREE三步审判缺少"引用图可达性"检查——文件可能不在注册表中但被其他文件import，此时不应删除。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 五层判定架构替代三判决策树 | L0-L4全部有结果，覆盖RULE-THREE三步+引用图盲区 |
| 2 | 不误删率 > 99% | 反向测试集验证 |
| 3 | 孤儿自动处置率 > 90%（不需人工） | ESCALATE比例 < 10% |
| 4 | 单文件判定 < 2s，批量100文件 < 30s | 性能基准测试 |
| 5 | 十系统集成全通 | Drift/Escalation/RBAC/KB/MCP/Skill/Gate/Feedback/SWID/Config |
| 6 | 一人+AI语境下100%自动化 | 高置信度自动执行，低置信度自动升级 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 执行修复操作（删除/注册/提取） | 判定与执行解耦——由MOD-INF-031 AutoFixEngine执行 |
| 2 | 内容安全审计 | 不检测安全漏洞 |
| 3 | 代码质量评估 | 不评估代码质量 |
| 4 | 运行时覆盖率追踪 | 不插桩运行 |
| 5 | 跨项目孤儿检测 | 只检测本项目 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows NTFS + Defender实时扫描 | 原子写入必须用temp-file+os.replace() |
| SQLite单文件数据库 | 100 AI并发写入需WAL+写入队列 |
| 无git备份环境 | 删除不可逆——必须有dry-run+安全围栏 |
| Python 3.12+ / Pydantic V2 | 数据模型强制BaseModel，禁止@dataclass |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 五层判定 | L0注册检查→L1引用图→L2功能重复→L3独特价值→L4独立价值 |
| 2 | 决策路由 | 12行决策表→六种处置建议 |
| 3 | 安全围栏 | 6层检查（大文件/近期修改/RBAC/漂移预算/置信度/级联） |
| 4 | 废弃追踪 | DEPRECATE_FIRST标记→TTL 30天→自动删除 |
| 5 | 级联清理 | 父文件删除→子文件自动检测 |
| 6 | 引用图引擎 | AST解析+import链遍历+可达性分析 |
| 7 | 资产生命周期 | SWID Tag+引用计数衰减+级联清理 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 执行修复操作 | MOD-INF-031 AutoFixEngine |
| 2 | 孤儿发现 | audit_registration.py / orphan_scanner.py / reconciler.py |
| 3 | 内容安全审计 | MOD-INF-017 安全扫描器 |
| 4 | Git历史深度考古 | 人工 / git工具 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | RegistrationChecker | L0注册检查：扫描27个注册表 | registry_of_registries.yaml | 同步调用 |
| 2 | ReferenceGraphEngine | L1引用图：AST解析+import链遍历 | 入口点配置 | 同步调用 |
| 3 | DuplicateDetector | L2功能重复：语义相似度>0.85 | MOD-INF-017 DedupEngine | 同步调用 |
| 4 | UniqueValueAnalyzer | L3独特价值：AST节点比对 | L2结果 | 同步调用 |
| 5 | StandaloneEvaluator | L4独立价值：六指标加权评分 | L3结果 | 同步调用 |
| 6 | DecisionTable | 12行决策路由 | L0-L4结果 | 同步调用 |
| 7 | SafetyFence | 6层安全检查 | DecisionTable+RBAC | 同步调用 |
| 8 | DeprecationTracker | 废弃追踪+TTL管理 | SafetyFence | 同步调用 |
| 9 | CascadeAnalyzer | 级联清理分析 | ReferenceGraphEngine | 同步调用 |
| 10 | OrphanCollector | 统一收集3源孤儿 | 3个发现源 | 同步调用 |
| 11 | OrphanJudge | 主控类：编排五层+决策+围栏 | 所有组件 | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | audit_registration.py | 发现注册表vs磁盘差异→OrphanFile | OrphanJudge.judge() | OrphanFile |
| 2 | orphan_scanner.py | 发现漂移孤儿→OrphanFile | OrphanJudge.judge() | OrphanFile |
| 3 | reconciler.py | 资产对账发现孤儿→OrphanFile | OrphanJudge.judge() | OrphanFile |
| 4 | OrphanJudge | 五层判定→Judgment | AutoFixEngine | Judgment |
| 5 | OrphanJudge | 判定结果→KB写入 | KnowledgeBase | MemoryRecord |
| 6 | OrphanJudge | 判定结果→审计日志 | AuditTrail | AuditEntry |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| DISCOVERED | OrphanCollector发现 | PENDING_JUDGE | — |
| PENDING_JUDGE | OrphanJudge.judge()调用 | JUDGED | 五层判定完成 |
| JUDGED | confidence=high + SafetyFence.passed | AUTO_EXEC | — |
| JUDGED | confidence=medium | DEPRECATE_FIRST | L4有价值但低置信度 |
| JUDGED | confidence=low / SafetyFence.failed | ESCALATED | — |
| DEPRECATE_FIRST | TTL过期 + reference_count=0 | DELETE_ELIGIBLE | 30天观察期 |
| AUTO_EXEC | AutoFixEngine执行完成 | RESOLVED | — |
| ESCALATED | 人工确认 | RESOLVED | — |

---

## §4 接口契约

### 4.1 公共 API

```python
class OrphanJudge:
    """孤儿判定主控类——五层判定→决策路由→安全围栏→处置建议"""

    def judge(self, path: str, dry_run: bool = True) -> Judgment:
        """
        单文件判定
        输入：path=孤儿文件路径，dry_run=是否仅预览
        输出：Judgment（含action/confidence/evidence/reason）
        核心逻辑：L0→L1→L2→L3→L4→DecisionTable→SafetyFence
        """

    def batch_judge(self, scope: str = "src/zephyr/", limit: int = 200,
                    dry_run: bool = True) -> OrphanJudgeReport:
        """
        批量判定（RULE-SEVEN：ThreadPoolExecutor max_workers=8）
        输入：scope=扫描范围，limit=上限
        输出：OrphanJudgeReport（含summary/action分布/置信度分布）
        """

    def quick_scan(self) -> GateResult:
        """
        快速扫描（Phase Gate用，仅L0+L1）
        输出：GREEN(无孤儿)/YELLOW(有孤儿无ESCALATE)/RED(有ESCALATE)
        """

    def deprecate(self, path: str, ttl_days: int = 30) -> DeprecationRecord:
        """标记文件为deprecated，TTL后自动删除"""

    def check_deprecated(self) -> list[DeprecationRecord]:
        """检查过期deprecated文件，返回可删除列表"""
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class OrphanFile(BaseModel):
    path: str
    size: int
    mtime: datetime
    content: str
    content_hash: str
    swid_tag: str = ""
    source: Literal["audit", "drift", "reconcile", "manual"] = "audit"
    discovered_at: datetime = Field(default_factory=datetime.now)

class Judgment(BaseModel):
    judgment_id: str
    orphan_path: str
    action: Literal["NOT_ORPHAN", "EXTRACT_AND_MERGE", "REGISTER", "DELETE",
                    "DEPRECATE_FIRST", "ESCALATE"]
    confidence: Literal["high", "medium", "low"]
    reason: str
    evidence: dict
    unique_elements: list[str] = []
    merge_target: str = ""
    register_target: str = ""
    requires_review: bool = False
    safety_checks: list = []
    swid_tag: str = ""
    reference_count: int = 0
    deprecated_record: Optional[dict] = None
    drift_budget_consumed: float = 0.0
    rbac_decision: str = ""
    escalation_event_id: str = ""

class OrphanJudgeReport(BaseModel):
    total_orphans: int
    not_orphan: list[Judgment]
    extract_and_merge: list[Judgment]
    register: list[Judgment]
    delete: list[Judgment]
    deprecate_first: list[Judgment]
    escalate: list[Judgment]
    summary: dict[str, int]
    execution_time_ms: float
    drift_budget_remaining: float
    confidence_distribution: dict[str, int]

class DeprecationRecord(BaseModel):
    file_path: str
    deprecated_at: datetime
    ttl_days: int = 30
    reason: str
    judgment_id: str
    reference_count_at_deprecation: int = 0
    auto_delete_eligible: bool = False

class RegistrationResult(BaseModel):
    is_registered: bool
    registered_in: list[dict]
    confidence: str

class ReachabilityResult(BaseModel):
    is_reachable: bool
    referenced_by: list[str]
    references: list[str]
    reference_count: int
    confidence: str

class DuplicateResult(BaseModel):
    has_duplicates: bool
    top_matches: list[tuple]
    search_duration_ms: float

class UniqueValueResult(BaseModel):
    has_unique: bool
    unique_count: int
    unique_nodes: list[str]
    confidence: str

class StandaloneResult(BaseModel):
    has_value: bool
    confidence: float
    scores: dict[str, float]
    recommendation: str
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `judge()` | `path` | ✅ | 必须存在且可读 |
| `judge()` | `dry_run` | ❌ | 默认True |
| `batch_judge()` | `scope` | ❌ | 合法目录，默认src/zephyr/ |
| `batch_judge()` | `limit` | ❌ | ≤200 |
| MCP `governance.orphan_judge` | `orphan_path` | ✅ | 非空字符串 |
| MCP `governance.orphan_batch_judge` | `scope` | ❌ | 合法目录 |
| MCP `governance.orphan_batch_judge` | `limit` | ❌ | ≤200 |
| MCP `governance.orphan_deprecate` | `path` | ✅ | 非空字符串 |
| MCP `governance.orphan_deprecate` | `ttl_days` | ❌ | 默认30 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `judge()` | `Judgment` | `Judgment(action="ESCALATE", confidence="low")` |
| `batch_judge()` | `OrphanJudgeReport` | `OrphanJudgeReport(escalate=[...])` |
| `quick_scan()` | `GateResult.GREEN/YELLOW/RED` | `GateResult.RED` |
| MCP `orphan_judge` | JSON Judgment | JSON `{error: str}` |
| MCP `orphan_batch_judge` | JSON OrphanJudgeReport | JSON `{error: str}` |

### 4.5 MCP 接口

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `governance.orphan_judge` | `judge()` | `{orphan_path: str}` | `Judgment` |
| `governance.orphan_batch_judge` | `batch_judge()` | `{scope: str?, limit: int?}` | `OrphanJudgeReport` |
| `governance.orphan_judge_report` | `report()` | `{judgment_id: str?}` | JSON report |
| `governance.orphan_deprecate` | `deprecate()` | `{path: str, ttl_days: int?}` | `DeprecationRecord` |

**错误码**：`JUDGMENT_PARSE_ERROR(422)` / `JUDGMENT_TIMEOUT(504)` / `JUDGMENT_RBAC_BLOCKED(403)` / `JUDGMENT_BUDGET_EXHAUSTED(429)`

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增action | ✅ 向后兼容 | 旧消费者忽略未知action |
| 新增判定层 | ✅ 向后兼容 | evidence字典新增key |
| 修改现有action语义 | ❌ 破坏性 | 需Owner审批+迁移方案 |
| 修改confidence阈值 | ⚠️ 需通知 | 消费者需更新逻辑 |
| 删除action | ❌ 破坏性 | 需Owner审批+迁移方案 |
| MCP Tool新增 | ✅ 向后兼容 | 不影响已有消费者 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python版本+数据模型 | Python 3.12+ / Pydantic V2 BaseModel（KBG-0040，禁止@dataclass） |
| 2 | 数据库并发模式 | SQLite WAL模式 + busy_timeout=5000ms |
| 3 | 原子写入方式 | temp-file + os.replace()（RULE-ONE + NTFS+Defender） |
| 4 | 并发模型 | ThreadPoolExecutor(max_workers=8)（RULE-SEVEN） |
| 5 | 默认执行模式 | dry_run=True（Safe-by-Default） |
| 6 | 判定有效期 | TTL=5分钟 |
| 7 | 批量删除上限 | ≤20文件/次 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| .py文件数 | ~400 | ~800 | ~10,000 | ✅当前 ❌远期 | 引用图分区+增量构建 |
| 孤儿文件数 | ~60 | ~120 | ~1,500 | ✅当前 ❌远期 | 增量扫描+分批判定 |
| 判定记录 | ~250 | ~2,000 | ~100,000 | ✅ | TTL归档+冷热分离 |
| 引用图内存 | ~50MB | ~200MB | ~500MB | ✅当前 ⚠️远期 | 分区+增量+只存签名 |
| 数据库大小 | ~4MB | ~57MB | ~100MB | ✅ | 归档+VACUUM |

### 5.3 迁移

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | audit_registration.py | `D:\ZephyrAlpha\scripts\governance\audit_registration.py` | 保留为输入源 | OrphanJudge消费其输出，不迁移 | 无需更新 |
| 2 | orphan_scanner.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\orphan_scanner.py` | 保留为输入源 | OrphanJudge消费其输出，不迁移 | 无需更新 |
| 3 | reconciler.py | `D:\ZephyrAlpha\src\zephyr\asset-inventory\reconciler.py` | 保留为输入源 | OrphanJudge消费其输出，不迁移 | 无需更新 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | AST解析失败 | SyntaxError | 跳过L3，降级到L4 | 单文件判定 |
| 2 | 引用图构建超时 | TimeoutError | 跳过L1，降级到L2 | 单文件判定 |
| 3 | MOD-INF-017不可导入 | ImportError | 跳过L2，降级到L3 | 所有L2判定 |
| 4 | RBAC BLOCKED | GuardDecision.BLOCKED | ESCALATE | 删除操作 |
| 5 | 漂移预算耗尽 | check_budget() | ESCALATE | 所有判定 |
| 6 | 文件读取失败 | OSError/IOError | 跳过该文件 | 单文件 |
| 7 | 注册表损坏 | 数据不一致 | ESCALATE | 全局 |
| 8 | SQLite写锁竞争 | sqlite3.OperationalError | WAL+busy_timeout+重试 | 数据库写入 |

**降级原则**：判定层失败→降级而非中断。L0失败→假设未注册；L1失败→假设不可达；L2失败→假设不重复；L3失败→假设有独特价值；L4失败→ESCALATE。

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 误删有价值文件 | 高 | 五层判定+安全围栏+dry-run+判定TTL | 反向测试集不误删率>99% |
| 2 | 判定投毒攻击 | 极高 | RBAC二次校验+system_critical白名单+异常模式检测 | 混沌工程对抗性测试 |
| 3 | 治理规则自指循环 | 极高 | system_critical白名单+RBAC BLOCKED+自检门禁 | 自检代码验证 |
| 4 | 并发判定冲突 | 极高 | 乐观锁+冲突检测+LWW+ESCALATE | 并发测试 |
| 5 | 安全围栏博弈绕过 | 高 | 关联聚合检查+批量总量限制 | 对抗性测试 |
| 6 | 删除不可逆不对称 | 高 | DELETE要求high置信度+强制DEPRECATE中间态 | 决策表验证 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元-L0 | RegistrationChecker | 已注册文件→is_registered=True | 注册表查询精确匹配 |
| 2 | 单元-L1 | ReferenceGraphEngine | 已知引用链→reachable=True/False | 引用图遍历精确 |
| 3 | 单元-L2 | DuplicateDetector | 已知重复文件对→检测 | 召回100% |
| 4 | 单元-L3 | UniqueValueAnalyzer | 已知有差异文件对→AST差异检测 | 独特节点精确匹配 |
| 5 | 单元-L4 | StandaloneEvaluator | 已知各种大小文件→六指标评分 | 评分与预期一致 |
| 6 | 单元-决策表 | DecisionTable | 12种判定组合 | 全部正确路由 |
| 7 | 单元-安全围栏 | SafetyFence | 大文件/近期修改/RBAC阻断 | 全部降级ESCALATE |
| 8 | 单元-废弃追踪 | DeprecationTracker | 标记→TTL过期→自动删除 | 生命周期正确 |
| 9 | 单元-级联清理 | CascadeAnalyzer | 删除父文件→子文件自动检测 | 级联深度正确 |
| 10 | 集成-完整流程 | 全流程 | 完整孤儿文件集→全流程判定 | 每个文件有Judgment+证据链 |
| 11 | 集成-Drift | DriftOrphanBridge | 漂移事件→孤儿判定→预算消耗 | 双向桥接正确 |
| 12 | 集成-Escalation | OrphanEscalationBridge | 低置信度判定→升级事件 | 升级路由正确 |
| 13 | 反向 | 不误删测试 | "不该删的文件"集→验证不会DELETE | 不误删率>99% |
| 14 | 混沌工程 | 对抗性测试 | 动态导入/伪装孤儿/注册表损坏/判定投毒/级联陷阱/并发判定 | 全部正确处置 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-017 | 必须 | L2功能重复检测引擎 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\code-dedup-engine\blueprint.md` |
| MOD-INF-020 | 必须 | 审计日志记录 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-trail\blueprint.md` |
| MOD-INF-026 | 必须 | 资产元数据来源 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\asset-inventory\blueprint.md` |
| MOD-INF-023 | 可选 | 漂移事件双向桥接 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\drift-detector\blueprint.md` |
| MOD-INF-022 | 可选 | 低置信度升级 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\escalation\blueprint.md` |
| MOD-INF-018 | 必须 | 删除权限校验 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\agent-rbac\blueprint.md` |
| MOD-KB-001 | 可选 | 判定记录查询与写入 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\knowledge_base\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-029` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| audit_registration.py | orphan_collector.py | 注册表vs磁盘差异→OrphanFile | 检查audit_registration.py产出物存在 |
| orphan_scanner.py | orphan_collector.py | 漂移孤儿→OrphanFile | 检查orphan_scanner.py产出物存在 |
| reconciler.py | orphan_collector.py | 资产对账孤儿→OrphanFile | 检查reconciler.py产出物存在 |
| orphan_collector.py | judge.py | OrphanFile列表 | 检查orphan_collector.py输出非空 |
| registration_checker.py | decision_table.py | L0结果 | 检查L0判定完成 |
| reference_graph_engine.py | decision_table.py | L1结果 | 检查L1判定完成 |
| duplicate_detector.py | decision_table.py | L2结果 | 检查L2判定完成 |
| unique_analyzer.py | decision_table.py | L3结果 | 检查L3判定完成 |
| standalone_evaluator.py | decision_table.py | L4结果 | 检查L4判定完成 |
| decision_table.py | safety_fence.py | 决策结果 | 检查决策表输出 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| orphan_collector.py | judge.py | OrphanFile列表 | 函数调用 |
| registration_checker.py | decision_table.py | RegistrationResult | 函数调用 |
| reference_graph_engine.py | decision_table.py | ReachabilityResult | 函数调用 |
| duplicate_detector.py | decision_table.py | DuplicateResult | 函数调用 |
| unique_analyzer.py | decision_table.py | UniqueValueResult | 函数调用 |
| standalone_evaluator.py | decision_table.py | StandaloneResult | 函数调用 |
| decision_table.py | safety_fence.py | 初步处置建议 | 函数调用 |
| safety_fence.py | judge.py | 最终处置建议 | 函数调用 |
| judge.py | db.py | Judgment | SQLite写入 |
| judge.py | drift_bridge.py | 判定结果 | 函数调用 |
| judge.py | escalation_bridge.py | 低置信度判定 | 函数调用 |
| judge.py | rbac_bridge.py | 删除操作 | 函数调用 |
| judge.py | kb_bridge.py | 判定记录 | 函数调用 |
| judge.py | feedback_bridge.py | 误判反馈 | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 脚本数>10，内部依赖复杂 |
| 2 | 依赖对齐自动验证 | 是 | 有7个外部依赖，需CI门禁 |
| 3 | 临时时态内容自动清理 | 否 | 当前无迁移方案需执行 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中，需自动检测进度 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖scripts/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\orphan-judge\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\` | Python源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\orphan-judge\` | 测试用例 |
| 黄金数据集 | `D:\ZephyrAlpha\tests\golden_dataset\orphans\` | 测试数据 |
| 配置文件 | `D:\ZephyrAlpha\config\orphan-judge.yaml` | 主配置 |
| 入口点配置 | `D:\ZephyrAlpha\config\orphan_judge_entry_points.yaml` | 引用图入口点 |
| 数据库 | `D:\ZephyrAlpha\data\orphan-judge\orphan-judge.db` | 判定历史 |
| Skill文件 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\orphan-judge.md` | Agent Skill |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-INF-031 AutoFixEngine | 契约CT-ORPHAN-001 | Judgment输出→AutoFixEngine执行 | 端到端判定→执行→确认闭环 |
| MOD-INF-023 DriftDetector | 双向桥接 | DriftOrphanBridge+OrphanDriftBridge | 漂移事件→孤儿判定→预算消耗 |
| MOD-INF-022 EscalationEngine | 调用方 | OrphanEscalationBridge | 低置信度→升级事件 |
| MOD-INF-018 Agent RBAC | 调用方 | OrphanRbacBridge | 删除操作→RBAC校验 |
| MOD-KB-001 KnowledgeBase | 双向桥接 | OrphanKbBridge | 判定→KB写入→查询闭环 |
| MOD-INF-013 GovernanceServer | MCP Tool注册 | 4个MCP Tools | `governance.orphan_judge`可调用 |
| MOD-GATE_ENGINE PhaseManager | Gate注册 | gate_orphan_judge | Phase 0门禁检查 |
| MOD-INF-019 AgentSpec | Skill注册 | SKILL-DOM-ORP-001 | `python -m zephyr.agent_spec list`可见 |
| MOD-FEEDBACK_LOOP FeedbackLoop | 调用方 | OrphanFeedbackBridge | 误判反馈→阈值校准 |
| scripts/scaffold.py | SWID Tag注入 | _inject_swid_tag() | 新建文件自动含SWID Tag |

### 12.1 域契约锚点

| 契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-001 | governance | 删除操作的RBAC权限校验 | MOD-INF-018 | 修改RBAC规则必须同步 |
| CT-ORPHAN-001 | governance | Judgment输出给AutoFixEngine | MOD-INF-031 | 修改action必须同步 |
| CT-DRIFT-ORPHAN | governance | 漂移事件↔孤儿判定 | MOD-INF-023 | 双向桥接变更必须同步 |
| CT-ESCALATE-ORPHAN | governance | 低置信度升级 | MOD-INF-022 | 升级规则变更必须同步 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 新增MOD-INF-029 | 新模块注册 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 新增本蓝图 | 新蓝图注册 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 新增MOD-INF-029条目 | 资产可发现 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 新增6条依赖 | 依赖可追踪 |
| 5 | MCP Server | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | 追加4个MCP Tool | MCP接口暴露 |
| 6 | Phase Check Registry | `D:\ZephyrAlpha\src\zephyr\governance\phase_check_registry.py` | 追加gate_orphan_judge | 门禁检查注册 |
| 7 | Skill Registry | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 追加SKILL-DOM-ORP-001 | Skill可发现 |
| 8 | scaffold.py | `D:\ZephyrAlpha\scripts\scaffold.py` | 追加SWID Tag注入 | 资产生命周期追踪 |
| 9 | 跨模块依赖 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 追加6条依赖 | 依赖注册 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | AST比对遗漏语义相同的不同写法 | 中 | 中 | 辅助Code Dedup Engine语义相似度 | 风险 |
| 2 | L4阈值过于武断 | 中 | 中 | 安全围栏兜底+DEPRECATE_FIRST+定期校准 | 风险 |
| 3 | 引用图构建慢（大项目） | 低 | 中 | 增量构建+缓存+只存签名 | 风险 |
| 4 | 动态导入（importlib）导致L1误判 | 中 | 高 | 标记dynamic_import，降低L1置信度 | 风险 |
| 5 | 提取融合引入新问题 | 中 | 中 | AutoFixEngine执行后自动检查+漂移预算 | 风险 |
| 6 | 级联清理误删 | 低 | 高 | cascade_max_depth=3+安全围栏 | 风险 |
| 7 | OrphanJudge自身成为孤儿 | 低 | 极高 | RBAC BLOCKED+自检门禁+system_critical白名单 | 风险 |
| 8 | 三体问题涌现（OrphanJudge+Drift+AutoFix交互） | 低 | 极高 | 交互循环检测+操作去重+循环熔断+冷却期 | 风险 |
| 9 | 治理系统自我保护偏差 | 低 | 极高 | 规则修改不需治理系统自身批准+人类直接控制 | 风险 |
| 10 | 治理成本初期高 | 高 | 中 | 随孤儿率下降而降低 | 负面后果 |
| 11 | 过度治理导致架构僵化（AI不敢创建新文件） | 中 | 中 | 复杂度预算约束+治理强度可调 | 负面后果 |
| 12 | 判定逻辑无法证明自身一致性（哥德尔不完备性工程体现） | 低 | 高 | 需人工兜底 | 负面后果 |
| 13 | 系统复杂度只增不减 | 中 | 中 | 需复杂度预算约束 | 负面后果 |

---

## §16 施工指引

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4个Phase |
| 施工模式 | 新建 |
| 核心风险 | 误删有价值文件 |
| 目标generation | 3——本次将蓝图从generation 2升级到generation 3 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-017可导入 | hard | ☐ | ☐ |
| 2 | MOD-INF-020可导入 | hard | ☐ | ☐ |
| 3 | MOD-INF-026可导入 | hard | ☐ | ☐ |
| 4 | scaffold.py可执行 | hard | ☐ | ☐ |
| 5 | 数据目录可写 | hard | ☐ | ☐ |
| 6 | 文件锁可用 | hard | ☐ | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：五判定核心类+决策表+安全围栏

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 + 蓝图特有§B1-B5 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\` |
| 验收标准 | 5个判定类+DecisionTable+SafetyFence全部可导入 |
| 验证命令 | `python -c "from zephyr.orphan_judge.registration_checker import RegistrationChecker; print('OK')"` |
| G7 检查项 | 上游文件全部列出？下游产出物路径精确？回滚方案可执行？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-029 | registration_checker.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\registration_checker.py` |
| MOD-INF-029 | reference_graph_engine.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\reference_graph_engine.py` |
| MOD-INF-029 | duplicate_detector.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\duplicate_detector.py` |
| MOD-INF-029 | unique_analyzer.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\unique_analyzer.py` |
| MOD-INF-029 | standalone_evaluator.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\standalone_evaluator.py` |
| MOD-INF-029 | decision_table.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\decision_table.py` |
| MOD-INF-029 | safety_fence.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\safety_fence.py` |
| MOD-INF-029 | deprecation_tracker.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\deprecation_tracker.py` |
| MOD-INF-029 | cascade_analyzer.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\cascade_analyzer.py` |
| MOD-INF-029 | config_loader.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\config_loader.py` |
| MOD-INF-029 | db.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\db.py` |

#### 步骤 2：OrphanJudge主控+CLI+数据模型

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 + §4.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\` |
| 验收标准 | OrphanJudge可导入+CLI可运行+自测通过 |
| 验证命令 | `python -m zephyr.orphan_judge --warn-only` |
| G7 检查项 | CLI命令全部定义？数据模型与§4.2一致？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-029 | judge.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\judge.py` |
| MOD-INF-029 | models.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\models.py` |
| MOD-INF-029 | __main__.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\__main__.py` |
| MOD-INF-029 | orphan_collector.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\orphan_collector.py` |
| MOD-INF-029 | report_generator.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\report_generator.py` |
| MOD-INF-029 | swid_tag.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\swid_tag.py` |

#### 步骤 3：十系统集成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §12 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\` + 外部文件修改 |
| 验收标准 | 6个Bridge类+MCP Tool注册+Gate注册+Skill注册 |
| 验证命令 | `python -c "from zephyr.mcp.governance_server import GovernanceServer; s=GovernanceServer(); print([t for t in s.tools if 'orphan' in t])"` |
| G7 检查项 | 外部文件修改范围与§13一致？注册表更新完整？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-029 | drift_bridge.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\drift_bridge.py` |
| MOD-INF-029 | escalation_bridge.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\escalation_bridge.py` |
| MOD-INF-029 | rbac_bridge.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\rbac_bridge.py` |
| MOD-INF-029 | kb_bridge.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\kb_bridge.py` |
| MOD-INF-029 | feedback_bridge.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\feedback_bridge.py` |
| MOD-INF-029 | mcp_integration.py | code | `D:\ZephyrAlpha\src\zephyr\orphan-judge\mcp_integration.py` |

#### 步骤 4：测试+校准

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 |
| 产出位置 | `D:\ZephyrAlpha\tests\orphan-judge\` |
| 验收标准 | 全量测试通过+无孤儿 |
| 验证命令 | `python -m pytest tests/orphan-judge/ -q` |
| G7 检查项 | 测试覆盖§9全部14项？黄金数据集完整？ |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 导入错误 | `Remove-Item -Recurse D:\ZephyrAlpha\src\zephyr\orphan-judge\` + 从__init__.py移除导出 |
| 2 | CLI入口错误 | `Remove-Item D:\ZephyrAlpha\src\zephyr\orphan-judge\__main__.py` |
| 3 | 外部文件修改报错 | `git checkout`对应文件 |
| 4 | 判定执行误删 | `git checkout -- <file>`从git恢复 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 包可导入 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\` | ☐ | ☐ | ☐ |
| 2 | CLI可运行 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\__main__.py` | ☐ | ☐ | ☐ |
| 3 | 自测通过 | — | ☐ | ☐ | ☐ |
| 4 | MCP Tool注册 | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | ☐ | ☐ | ☐ |
| 5 | Gate注册 | `D:\ZephyrAlpha\src\zephyr\governance\phase_check_registry.py` | ☐ | ☐ | ☐ |
| 6 | Skill注册 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | ☐ | ☐ | ☐ |
| 7 | 测试通过 | `D:\ZephyrAlpha\tests\orphan-judge\` | ☐ | ☐ | ☐ |

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
| .py文件数 | ~400 | `dir /s *.py \| find /c ".py"` |
| 孤儿文件数 | ~60 | audit_registration.py --json |
| 判定记录数 | ~250 | SQLite COUNT(*) |
| 引用图内存 | ~50MB | 进程内存监控 |
| 数据库大小 | ~4MB | 文件大小 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 引用图全量构建~3s，10K脚本预计~250s | 分区+增量构建 | 文件数>1000 |
| GAP-002 | 2 Session乐观锁，100 AI并发不可行 | 调度队列+判定缓存+去重 | AI并发>5 |
| GAP-003 | SQLite单文件100 AI写入瓶颈 | WAL+分库+PG迁移路径 | 写入qps>50 |
| GAP-004 | 无增量扫描引擎 | ChangeImpactMapper+ScriptDependencyGraph | 脚本数>500 |
| GAP-005 | max_workers=8硬编码 | 动态0.3×~0.9×cpu_count | CPU核心>12 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 五层判定+决策表+安全围栏 | ❌ |
| v2.0.0 | 2 | 模板升级 | v3.3模板合规+压缩 | ❌ |
| v5.0.0 | 3 | 容量升级 | 10K脚本/100AI并发 | ❌ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | 引用图分区+增量构建 | P0 | v5.0.0 | 待施工 |
| GAP-002 | 100 AI并发模型 | P0 | v5.0.0 | 待施工 |
| GAP-003 | 数据库分库+PG迁移 | P1 | v5.0.0 | 待施工 |
| GAP-004 | 增量扫描引擎 | P0 | v5.0.0 | 待施工 |
| GAP-005 | 动态WorkerPool | P2 | v5.0.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ChangeImpactMapper | GAP-004 | incremental_scanner.py | Phase B1 | 待施工 |
| PriorityDispatchQueue | GAP-002 | script_scheduler.py | Phase B2 | 待施工 |
| ShardedReferenceGraph | GAP-001 | reference_graph_engine.py | Phase B3 | 待施工 |
| JudgmentCache | GAP-002 | judgment_cache.py | Phase C1 | 待施工 |
| RateLimiter | GAP-002 | mcp_handler.py | Phase C3 | 待施工 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-029-01 | 判定架构 | 三判/五判 | 五判 | RULE-THREE缺少引用图可达性 | 2026-05-08 |
| 2 | D-029-02 | L2相似度阈值 | 0.80/0.85/0.90 | 0.85 | 平衡误报漏报 | 2026-05-08 |
| 3 | D-029-03 | L4独立价值阈值 | 0.3/0.5/0.7 | 0.5 | 中间值 | 2026-05-08 |
| 4 | D-029-04 | L4指标权重 | 等权/加权 | 加权 | git_history和contract_anchor更重要 | 2026-05-08 |
| 5 | D-029-05 | DEPRECATE_FIRST TTL | 7/14/30天 | 30天 | 对标Google GWS | 2026-05-08 |
| 6 | D-029-06 | 级联清理深度 | 1/3/5/无限 | 3 | 防止级联雪崩 | 2026-05-08 |
| 7 | D-029-07 | 判定与执行解耦 | 耦合/解耦 | 解耦 | 避免循环论证 | 2026-05-08 |
| 8 | D-029-08 | 默认Dry-run | 默认执行/默认预览 | 默认预览 | Safe-by-Default | 2026-05-08 |
| 9 | D-029-09 | DELETE置信度要求 | medium/high | high | 误删不可逆 | 2026-05-08 |
| 10 | D-029-10 | 引用图存储 | 全量/签名 | 签名 | 内存<200MB约束 | 2026-05-08 |
| 11 | D-029-11 | 废弃标记方式 | 文件头部注释/数据库 | 数据库 | 避免git blame污染 | 2026-05-08 |
| 12 | D-029-12 | 批量删除上限 | 无/20/50 | 20 | 防止批量误删 | 2026-05-08 |
| 13 | D-029-13 | 判定TTL | 无/5分钟/30分钟 | 5分钟 | 防止过时判定 | 2026-05-08 |
| 14 | D-029-14 | 安全围栏大文件阈值 | 5/10/50KB | 10KB | 10KB以上值得人工复核 | 2026-05-08 |
| 15 | D-029-15 | 并发模型 | 串行/ThreadPool/multiprocessing | ThreadPool | RULE-SEVEN+I/O密集型 | 2026-05-08 |
| 16 | D-029-16 | 现有三源处置 | 废弃/保留为输入源 | 保留为输入源 | 三源各有独立用途 | 2026-05-08 |

---

## 蓝图特有章节

### 蓝图特有：五层判定架构详解

> 来源：原蓝图§2-§3核心设计
> 仅本蓝图需要：五层判定是OrphanJudge的核心差异化设计
> 不可砍理由：砍掉后AI施工者无法实现判定逻辑

#### B1. 五层判定与RULE-THREE映射

| RULE-THREE步骤 | OrphanJudge层 | 说明 |
|----------------|---------------|------|
| STEP 1: 登记检查 | L0注册检查 | 文件是否在manifest/registry/__init__.py中被引用？ |
| *(RULE-THREE未覆盖)* | L1引用图 | 是否被任何文件import/require？——RULE-THREE盲区 |
| STEP 2: 重复检查 | L2功能重复 | 是否有byte-for-byte或语义相同的文件？ |
| STEP 3: 逐行价值检查 | L3独特价值+L4独立价值 | 每一行内容是否在其他地方存在？ |

#### B2. 引用图引擎

| 属性 | 值 |
|------|-----|
| 入口点 | `src/zephyr/governance/audit-orchestrator/__main__.py` + `scripts/**/*.py` + `tests/**/*.py` + `src/zephyr/governance/rule_enforcement/*.py` + `config/orphan_judge_entry_points.yaml` |
| 图构建时间 | <10s（全项目） |
| 单文件可达性查询 | <100ms |
| 图内存占用 | <200MB |
| 增量更新 | <2s（单文件变更） |

| 导入类型 | 解析方式 |
|----------|---------|
| 绝对导入 | 直接映射到src/zephyr/下路径 |
| 相对导入 | 基于当前文件位置解析 |
| 脚本导入 | 映射到scripts/下路径 |
| 动态导入 | 标记为dynamic_import，降低L1置信度 |
| YAML引用 | 扫描YAML文件中的路径引用 |

#### B3. 决策表（12行）

| # | L0 | L1 | L2 | L3 | L4 | 处置 | 置信度 | 风险 |
|---|:---:|:---:|:---:|:---:|:---:|------|:---:|:---:|
| 1 | 已注册 | — | — | — | — | NOT_ORPHAN | 高 | 无 |
| 2 | 未注册 | 可达 | — | — | — | REGISTER | 高 | 低 |
| 3 | 未注册 | 不可达 | 重复 | 有独特 | — | EXTRACT_AND_MERGE | 高 | 低 |
| 4 | 未注册 | 不可达 | 重复 | 无独特 | — | DELETE | 高 | 低 |
| 5 | 未注册 | 不可达 | 不重复 | — | 有价值 | REGISTER | 高 | 低 |
| 6 | 未注册 | 不可达 | 不重复 | — | 无价值 | DELETE | 中 | 中 |
| 7 | 未注册 | 不可达 | 不确定 | — | — | ESCALATE | — | — |
| 8 | 未注册 | 不可达 | 不重复 | — | 不确定 | ESCALATE | — | — |
| 9 | 未注册 | 不可达 | 重复 | 不确定 | — | ESCALATE | — | — |
| 10 | 未注册 | 不可达 | 不重复 | — | 有价值(低) | DEPRECATE_FIRST | 中 | 低 |
| 11 | 未注册 | 不可达 | 重复 | 有独特(少) | — | EXTRACT_AND_MERGE+DEPRECATE | 中 | 中 |
| 12 | 任何 | 任何 | 任何 | 任何 | 任何 | ESCALATE(置信度<0.7) | — | — |

#### B4. 资产生命周期追踪

**SWID Tag模式**：scaffold.py创建文件时自动注入唯一标识符头部注释。

**引用计数衰减规则**：

| 状态 | 条件 | 处置 |
|------|------|------|
| ALIVE | reference_count > 0 | 保留 |
| WATCHING | reference_count = 0, < 7天 | 观察 |
| DEPRECATED | reference_count = 0, 7-30天 | 自动标记 |
| DELETE_ELIGIBLE | reference_count = 0, > 30天 | 可进入删除队列 |

**级联清理**：cascade_max_depth=3，父文件删除后仅被父文件引用的子文件自动检测。

#### B5. 安全围栏6层检查

| # | 检查项 | 阈值 | 不通过处置 |
|---|--------|------|-----------|
| 1 | 文件大小 | >10KB | 建议人工复核 |
| 2 | 最近修改 | <7天 | 可能是活跃文件 |
| 3 | RBAC权限 | BLOCKED | ESCALATE |
| 4 | 漂移预算 | 耗尽 | ESCALATE |
| 5 | 判定置信度 | low | ESCALATE |
| 6 | 级联影响 | 超限 | 扩大判定范围 |

#### B6. SWID Tag读写

scaffold.py创建文件时注入：`# SWID-TAG: {module_id}-{package}-{name}-py-{timestamp}` / `# CREATED-BY: scaffold.py module {package} {name}` / `# CREATED-AT: {datetime}` / `# REGISTERED-IN: src/zephyr/{package}/__init__.py __all__`

OrphanJudge通过正则匹配读取SWID Tag信息。

#### B7. 退出码约定

| 退出码 | 含义 | CI/CD行为 |
|:---:|------|-----------|
| 0 | 全部通过 | 通过 |
| 1 | 有孤儿但无ESCALATE | 警告 |
| 2 | 有ESCALATE | 阻断 |
| 3 | 执行错误 | 阻断 |
| 4 | 安全围栏触发 | 阻断 |

#### B8. 并发模型

| 场景 | 风险 | 缓解 |
|------|------|------|
| 两个Session同时判定同一文件 | 重复判定 | 判定前查询KB+乐观锁 |
| Session A判定DELETE，B判定REGISTER | 矛盾判定 | LWW+冲突检测+ESCALATE |
| 批量判定并发写入数据库 | SQLite写锁竞争 | WAL模式+写入队列 |

**Owner缺席模式**：

| 模式 | 触发条件 | 行为 |
|------|---------|------|
| NORMAL | Owner活跃（7天内有session） | 全功能 |
| LENIENT | Owner不活跃7-14天 | 禁止自动DELETE |
| SURVIVAL | Owner不活跃>14天 | 仅dry-run+记录 |

#### B9. 可观测性核心指标

| 指标 | 类型 | 告警阈值 |
|------|------|---------|
| orphan_judge_total_judgments | Counter | — |
| orphan_judge_action_distribution | Gauge | ESCALATE>20%→告警 |
| orphan_judge_avg_confidence | Gauge | <0.7→告警 |
| orphan_judge_execution_time_ms | Histogram | P99>5000ms→告警 |
| orphan_judge_false_positive_rate | Gauge | >5%→告警 |
| orphan_judge_orphan_rate | Gauge | >10%→告警 |
| orphan_judge_db_size_mb | Gauge | >100MB→归档 |

#### B10. SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS judgment_history (
    judgment_id TEXT PRIMARY KEY,
    orphan_path TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('NOT_ORPHAN','EXTRACT_AND_MERGE','REGISTER','DELETE','DEPRECATE_FIRST','ESCALATE')),
    confidence TEXT NOT NULL CHECK(confidence IN ('high','medium','low')),
    reason TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    swid_tag TEXT DEFAULT '',
    reference_count INTEGER DEFAULT 0,
    requires_review BOOLEAN DEFAULT FALSE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT,
    resolved_by TEXT,
    feedback TEXT,
    was_correct BOOLEAN,
    session_id TEXT NOT NULL,
    UNIQUE(orphan_path, created_at)
);

CREATE TABLE IF NOT EXISTS deprecation_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    deprecated_at TEXT NOT NULL DEFAULT (datetime('now')),
    ttl_days INTEGER NOT NULL DEFAULT 30,
    reason TEXT NOT NULL,
    judgment_id TEXT NOT NULL,
    ref_count_at_deprecation INTEGER DEFAULT 0,
    auto_delete_eligible BOOLEAN DEFAULT FALSE,
    expired_at TEXT,
    deleted_at TEXT,
    FOREIGN KEY (judgment_id) REFERENCES judgment_history(judgment_id)
);

CREATE TABLE IF NOT EXISTS reference_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    reference_count INTEGER NOT NULL DEFAULT 0,
    referenced_by TEXT,
    snapshot_at TEXT NOT NULL DEFAULT (datetime('now')),
    session_id TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_judgment_path ON judgment_history(orphan_path);
CREATE INDEX IF NOT EXISTS idx_judgment_action ON judgment_history(action);
CREATE INDEX IF NOT EXISTS idx_deprecation_path ON deprecation_records(file_path);
CREATE INDEX IF NOT EXISTS idx_ref_snapshot_path ON reference_snapshots(file_path);
```

#### B11. 不可删除白名单

```yaml
system_critical:
  paths:
    - "src/zephyr/orphan-judge/**"
    - "src/zephyr/governance/ops_governance/phase_manager.py"
    - "src/zephyr/governance/ops_governance/phase_check_registry.py"
    - "src/zephyr/agent-rbac/**"
    - "src/zephyr/escalation/**"
    - "src/zephyr/behavioral-auditor/**"
    - "src/zephyr/asset-inventory/**"
    - "src/zephyr/kb/**"
    - "src/zephyr/integration/mcp/governance_server.py"
    - "scripts/scaffold.py"
    - "scripts/lock_files.py"
    - "docs/registry_of_registries.yaml"
    - "config/orphan-judge.yaml"
    - "config/orphan_judge_entry_points.yaml"
```

#### B12. 删除铁律

| # | 铁律 |
|---|------|
| 1 | 永远不删除有SWID-TAG且REGISTERED-IN指向有效注册表的文件 |
| 2 | 永远不删除system_critical白名单中的文件 |
| 3 | 永远不删除OrphanJudge自身的源文件 |
| 4 | 永远不删除registry_of_registries.yaml及其引用的注册表文件 |
| 5 | 删除前必须git commit或git stash——确保可恢复 |
| 6 | 批量删除单次不超过20个文件 |
| 7 | 删除后必须验证无废墟引用 |

#### B13. 配置系统

```yaml
orphan_judge:
  version: "2.1.0"
  similarity_threshold: 0.85
  standalone_value_threshold: 0.5
  deprecation_ttl_days: 30
  max_batch_size: 200
  max_workers: 8
  safety_fences:
    max_delete_size_bytes: 10000
    recent_modification_days: 7
    require_review_confidence: 0.3
  entry_points:
    application:
      - "src/zephyr/governance/audit-orchestrator/__main__.py"
      - "src/zephyr/integration/mcp/governance_server.py"
    scripts: "scripts/**/*.py"
    tests: "tests/**/*.py"
    gates: "src/zephyr/governance/rule_enforcement/*.py"
  reference_graph:
    cache_enabled: true
    cache_ttl_seconds: 3600
    incremental_build: true
  lifecycle:
    swid_tag_enabled: true
    reference_count_tracking: true
    cascade_cleanup_enabled: true
    cascade_max_depth: 3
  auto_governance:
    auto_delete_high_confidence: true
    auto_register_high_confidence: true
    auto_deprecate_medium_confidence: true
    auto_escalate_low_confidence: true
    auto_kb_write: true
    auto_drift_budget_consume: true
```

#### B14. CLI接口

```bash
python -m zephyr.orphan_judge judge --path <file>          # 单文件判定（默认dry-run）
python -m zephyr.orphan_judge judge --path <file> --execute # 显式执行
python -m zephyr.orphan_judge batch --scope src/zephyr/     # 批量判定（默认dry-run）
python -m zephyr.orphan_judge quick-scan                    # 快速扫描（Phase Gate用）
python -m zephyr.orphan_judge deprecate --path <file> --ttl 30
python -m zephyr.orphan_judge check-deprecated
python -m zephyr.orphan_judge report --format json --output data/orphan_judge_report.json
python -m zephyr.orphan_judge refs --path <file>
python -m zephyr.orphan_judge --warn-only                   # 自测
```

#### B15. 自动化分级

| 判定置信度 | 自动化行为 | 人工干预 |
|-----------|-----------|---------|
| high + 安全围栏通过 | 自动执行（DELETE/REGISTER/EXTRACT_AND_MERGE） | 无需 |
| high + 安全围栏触发 | 自动升级ESCALATE | 需人工确认 |
| medium | 自动DEPRECATE_FIRST | 30天后自动删除 |
| low | 自动升级ESCALATE | 需人工确认 |
| 任何 + RBAC BLOCKED | 自动升级ESCALATE | 需人工确认 |

#### B16. 注册登记清单

| # | 注册表 | 注册表ID | 登记内容 | 状态 |
|---|--------|----------|---------|:---:|
| 1 | 模块登记表 | REG-MOD-ALPHA_SIGNAL_DOMAIN | MOD-INF-029 orphan-judge cross_layer | 待登记 |
| 2 | 蓝图注册表 | REG-BLUEPRINT-001 | 本蓝图文件 | 自动同步 |
| 3 | 脚本清单 | REG-SCRIPT-001 | orphan_judge_cli | 待登记 |
| 4 | Agent Skill注册表 | REG-SKILL-001 | SKILL-DOM-ORP-001 | 待登记 |
| 5 | 跨模块依赖登记表 | REG-CROSS-002 | 6条依赖关系 | 待登记 |
| 6 | Gate注册表 | REG-GATE-001 | gate_orphan_judge | 待登记 |
| 7 | Phase Check Registry | — | gate_orphan_judge检查函数 | 待登记 |
| 8 | MCP Server Tools | — | 4个MCP Tools | 待登记 |
| 9 | Rule Registry | — | TRAE-003/TRAE-004升级 | 待登记 |
| 10 | __init__.py | — | __all__导出 | 待登记 |
| 11 | 契约冻结清单 | REG-FREEZE-001 | CT-ORPHAN-001 | 待登记 |
| 12 | 资产盘点注册表 | REG-INV-001 | 本模块所有文件 | 自动同步 |
| 13 | 入口点配置 | — | config/orphan_judge_entry_points.yaml | 待登记 |
| 14 | skill-registry.yaml | REG-SKILL-001 | 触发关键词路由 | 待登记 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符D:\） | AI零记忆，不知道相对路径基准 | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI每次新session零记忆 | AI跳过不读，缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | 蓝图是施工依据，不是讨论记录 | 关键信息被噪音淹没 |
| 4 | **产出物路径必须与GOV-DOC-002一致** | AI不知道项目目录规范 | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | AI不知道边界 | 范围漂移 |
| 6 | **容量估算必须写** | AI不知道系统能容纳多少 | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | AI不知道旧东西怎么处理 | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI无法处理模糊指令 | 执行漂移 |
| 9 | **蓝图必须自包含** | AI可能不读引用的文件 | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 没有git备份，删除不可逆 | 永久丢失 |
| 11 | **construction_progress必须与代码实际状态一致** | 虚假进度误导下一个AI | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path必须与§11产出物路径一致** | 路径不一致=AI找不到代码 | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是SSoT，蓝图复制代码=双源漂移 | AI改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不同的内容强行塞一个蓝图=职责不清 | AI不知道该读哪个蓝图，跨模块影响无法追踪 |

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
| 容量保障蓝图中"执行层设计"（18个CAP-G需求+28个SLO） | **拆分** | 独立CAP-G前缀 + 独立Phase + 独立SLO体系 + 与主体depends_on交集<30% |
| 容量保障蓝图中"Error Budget五级响应" | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 容量保障蓝图中"容量预测模型" | **原地** | 预测是容量保障的核心能力，不是独立子系统 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| — | 当前无文件需删除 | — | — | — | — |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在stable搬入阶段执行 | 给足缓冲期 |
| 4 | 物理删除必须人类确认 | AI不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 中央注册表 | — | `D:\ZephyrAlpha\docs\registry_of_registries.yaml` | 知道项目有什么 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 知道文件该放哪 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | 知道怎么治理 |
| 4 | 项目规则 | — | `D:\ZephyrAlpha\.trae\rules\project_rules.md` | RULE-ZERO~NINE |
| 5 | 模块注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 知道有哪些模块 |
| 6 | 蓝图注册表 | — | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 知道有哪些蓝图 |
| 7 | 脚本清单 | — | `D:\ZephyrAlpha\scripts\script-manifest.yaml` | 知道有哪些脚本 |
| 8 | 跨模块依赖 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 知道依赖关系 |
| 9 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 10 | AI自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | audit_registration.py | `D:\ZephyrAlpha\scripts\governance\audit_registration.py` | 发现不在注册表中的文件 | 只做发现不做判定——OrphanJudge消费其输出 |
| 2 | orphan_scanner.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\orphan_scanner.py` | 发现漂移孤儿 | 属于drift_detector子模块——OrphanJudge消费其输出 |
| 3 | reconciler.py | `D:\ZephyrAlpha\src\zephyr\asset-inventory\reconciler.py` | 资产对账发现孤儿 | 属于asset_inventory子模块——OrphanJudge消费其输出 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | orphan_judge包 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\` | 新建 | 新建25个文件 |
| 2 | 配置文件 | `D:\ZephyrAlpha\config\orphan-judge.yaml` | 新建 | 主配置 |
| 3 | 入口点配置 | `D:\ZephyrAlpha\config\orphan_judge_entry_points.yaml` | 新建 | 引用图入口点 |
| 4 | 数据目录 | `D:\ZephyrAlpha\data\orphan-judge\` | 新建 | 数据库 |
| 5 | 测试目录 | `D:\ZephyrAlpha\tests\orphan-judge\` | 新建 | 测试用例 |
| 6 | 黄金数据集 | `D:\ZephyrAlpha\tests\golden_dataset\orphans\` | 新建 | 测试数据 |
| 7 | MCP Server | `D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py` | 修改 | 追加4个MCP Tool |
| 8 | Phase Check Registry | `D:\ZephyrAlpha\src\zephyr\governance\phase_check_registry.py` | 修改 | 追加gate_orphan_judge |
| 9 | Skill Registry | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 修改 | 追加SKILL-DOM-ORP-001 |
| 10 | scaffold.py | `D:\ZephyrAlpha\scripts\scaffold.py` | 修改 | 追加SWID Tag注入 |
| 11 | 模块注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 修改 | 追加MOD-INF-029 |
| 12 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | 追加本蓝图 |
| 13 | 跨模块依赖 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 修改 | 追加6条依赖 |
| 14 | 中央注册表 | `D:\ZephyrAlpha\docs\registry_of_registries.yaml` | 读取 | 只读 |
| 15 | 脚本清单 | `D:\ZephyrAlpha\scripts\script-manifest.yaml` | 读取 | 只读 |
| 16 | Gate注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 读取 | 只读 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图核心架构设计 | **本文档 §1-§14** | 已被取代的旧蓝图 |
| 本模块施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-031 AutoFixEngine蓝图 | §4接口契约、§10依赖关系 |
| Tier 2 | MCP Server / PhaseManager / SkillRegistry | §12集成点 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\orphan-judge\*.py` | §4数据模型、§11产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 修改construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需Owner审批+通知所有消费者 |
| 模块边界修改（§2） | 需Owner审批 |
| construction_progress变更 | 需§0对齐验证通过 |
| 施工步骤微调（命令、路径修正） | AI可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI可自主修改 |
| 容量升级方案新增（§17） | 需Owner审批 |
