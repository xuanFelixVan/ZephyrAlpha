---
module_id: MOD-INF-036
submodule_path: src/zephyr/intelligence/model_profiling
title: "Model Capability Exam 蓝图 — 模型能力考试·多维度能力评估"
doc_type: blueprint
status: Active
version: "2.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/intelligence/model_profiling/
last_updated: "2026-05-23"
last_verified: "2026-05-14"
generation: 2
functional_domain: intelligence
summary: "AI模型入职考试系统——五维评测产出CapabilityPassport能力护照，驱动TaskGate任务门控。"
template_for: blueprint
tags: [model-capability-exam, exam, benchmark, capability-passport, task-gate, model-profiler, cross-layer]
priority: P1
runtime_plane: warm
belongs_to: "MOD-INF-034"
parent_module: "MOD-INF-034"
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - {target: "MOD-INF-034", at: "全篇", why: "ModelProfiler——MCE是Profiler的子系统，扩展benchmark为入职考试"}
  - {target: "MOD-INF-009", at: "§2", why: "Pipeline——MCE通过管线调度考试任务"}
  - {target: "MOD-INF-035", at: "§2", why: "AutoRuntime Core——大脑消费CapabilityPassport做模型路由"}
  - {target: "MOD-GATE_ENGINE", at: "§2", why: "Gate Engine——TaskGate消费护照做门控判定"}
  - {target: "MOD-INF-005", at: "§35", why: "分布式执行架构——考试并发调度"}
references:
  - {id: "MOD-INF-024", at: "§2", why: "Budget Enforcer——考试消耗Token需预算管控"}
  - {id: "MOD-LLM_SECURITY", at: "§2", why: "LLM Security——考试LLM调用需过安全闸门"}
  - {id: "CFG-CAP-001", at: "全篇", why: "capacity_params.yaml——MCE所有并发/超时参数从该文件读取"}
ssot_ref: "specs/model_capability_exam/spec.md"
---

# Model Capability Exam 蓝图 — 模型能力考试·多维度能力评估

> module_id: MOD-INF-036 | version: 2.1.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/intelligence/model_profiling/ | generation: 2 | construction_progress: partially_implemented

## 概述

ModelCapabilityExam（MCE）是 ModelProfiler（MOD-INF-034）的子系统，负责 AI 模型入职考试。每条 AI 进入系统时自动跑五维评测（横轴能力覆盖、纵轴精度深度、速轴延迟吞吐、幻轴幻觉率、稳轴长时间漂移），产出 CapabilityPassport 能力护照，驱动 TaskGate 只分配模型 pass=true 的能力。**v2.2.0新增**：护照新增 cost_efficiency 维度（本地vs云端API成本效率），支持下游 LLM 路由成本引擎（交易决策流水线 C-044⑤）的消费。当前规模 ~5 模型 / 9 能力类型 / 27 道标准题，目标容量 100 模型并发。上游依赖 ModelProfiler + Pipeline + BudgetEnforcer，下游被 AutoRuntime Core + Gate Engine + 交易决策流水线 C-044⑤ 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/databases/depgraph.db`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-036`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3.1 | 公共导出 | 已实现 | — |
| 2 | `exam_orchestrator.py` | §3.1 / §4.1 | 五轴考试主控 | 已实现 | — |
| 3 | `exam_test_cases.py` | §3.1 / §4.2 | 27 道标准题库 | 已实现 | — |
| 4 | `capability_passport.py` | §3.1 / §4.2 | 护照数据模型+持久化 | 已实现 | — |
| 7 | `test_model_capability_exam.py` | §9 | 测试用例 | 未实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 4/7 文件存在 | ✅ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ✅ |
| 护照存储路径 = 代码 PASSPORTS_DIR | `data/brain/passports/` | ✅ |
| TaskGate 消费 CapabilityPassport | `from zephyr.model_capability_exam.capability_passport import CapabilityPassport` | ✅ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | ExamOrchestrator, ExamTestCases, CapabilityPassport, TaskGate | benchmark_suite, 测试 | 待施工 |
| v2.0.0 (容量升级) | 同 v1.0.0 | ExamMode, PassportIndex, ExamQueueItem | Phase 1-3 待施工 |
| v2.2.0 (成本效率) | 同 v2.0.0 | CostEfficiencyResult 数据模型 | 待施工 |

---

## §1 设计背景与目标

### 1.1 背景

AI 模型进入 ZephyrAlpha 系统后，大脑（AutoRuntime Core）需要知道每个模型能做什么、不能做什么。当前无标准化评测机制——模型路由凭经验，任务分配无门控，导致低能力模型被分配高难度任务（代码修改幻觉）、高能力模型被浪费在简单任务上。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 每条 AI 入职时自动跑五维评测 | 新模型注册 → 护照自动产出，覆盖率 100% |
| 2 | 产出 CapabilityPassport 能力护照 | 护照 JSON 包含 5 轴结果 + 推荐 |
| 3 | TaskGate 基于护照做门控 | pass=false 的能力不分配任务 |
| 4 | 支持 100 模型并发考试 | 并发上限可配，默认 100 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 模型训练/微调 | MCE 只评测，不训练 |
| 2 | 跨模型排行榜 | Phase 4 远期目标，当前不实现 |
| 3 | 考试用例自动生成 | 题库人工维护，保证质量 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 考试依赖 Ollama 本地推理 | Ollama 无响应时考试阻塞，需超时熔断 |
| 单次全量考消耗 ~8K-10K tokens | 100 并发占日预算 10%，需分池管控 |
| Windows NTFS 文件锁 | 护照写入需原子操作（temp-file + os.replace） |
| 考试期间模型不可用 | 考试中的模型不应被分配任务 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 五维评测 | 横轴（能力覆盖）/ 纵轴（精度深度）/ 速轴（延迟吞吐）/ 幻轴（幻觉率）/ 稳轴（漂移） |
| 2 | 护照产出 | CapabilityPassport JSON 持久化到 data/brain/passports/ |
| 3 | 考试调度 | ExamOrchestrator 编排五轴考试流程 |
| 4 | 题库管理 | ExamTestCases 27 道标准题，9 能力 × 3 难度 |
| 5 | 门控集成 | TaskGate 消费护照做任务分配判定 |
| 6 | 成本效率评估 | 护照新增 cost_efficiency 维度，记录模型在本地GPU vs 云端API两种部署模式下的成本效率，供下游LLM路由成本引擎消费 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 模型发现与注册 | MOD-INF-034 ModelProfiler |
| 2 | Token 预算管控 | MOD-INF-024 BudgetEnforcer |
| 3 | 管线调度 | MOD-INF-009 Pipeline |
| 4 | 并发调度与背压 | MOD-INF-005 分布式执行架构 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | ExamOrchestrator | 五轴考试主控 | ExamTestCases, CapabilityPassport | 同步调用 |
| 2 | ExamTestCases | 27 道标准题库 | — | 数据提供 |
| 3 | CapabilityPassport | 护照数据模型+持久化 | — | 文件 I/O |
| 4 | TaskGate | 任务门控（消费端） | CapabilityPassport | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | OllamaChat.inference() | 横轴：每能力 1 题验证结构 | BreadthResult | dict |
| 2 | OllamaChat.inference() | 纵轴：通过能力各跑 3 题算 F1 | DepthResult | dict |
| 3 | 考试过程计时 | 速轴：延迟 P50/P95/P99 + 吞吐 | SpeedResult | float |
| 4 | OllamaChat.inference() | 幻轴：编造/不一致/拒绝检测 | HallucinationResult | dict |
| 5 | OllamaChat.inference() | 稳轴：cold→load→hot 三阶段 | DriftResult | dict |
| 6 | 五轴结果聚合 | 护照持久化 | data/brain/passports/{model_id}.json | JSON |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| NOT_EXAMINED | 模型注册 | EXAMINING | Ollama 可用 + Token 预算充足 |
| EXAMINING | 五轴完成 | EXAMINED | 所有轴结果非空 |
| EXAMINING | 超时/熔断 | EXAM_FAILED | 连续 3 次超时 |
| EXAMINED | 模型版本变更 | EXAMINING | need_reexam()=True |
| EXAM_FAILED | 人工重试 | EXAMINING | Owner 审批 |

---

## §4 接口契约

### 4.1 公共 API

```python
class ExamOrchestrator:
    """五轴入职考试主控"""

    def __init__(self, chat: Any, model_id: str = "") -> None:
        """
        输入：chat=OllamaChat实例, model_id=模型标识（空则从chat推断）
        输出：ExamOrchestrator实例
        """

    def run_full_exam(self, *, skip_drift: bool = True) -> CapabilityPassport:
        """
        输入：skip_drift=是否跳过稳轴（默认跳过，耗时较长）
        输出：CapabilityPassport——完整护照
        核心逻辑：横轴→纵轴→速轴→幻轴→(稳轴)→聚合→推荐
        """

class CapabilityPassport:
    """能力护照数据模型"""

    def save(self) -> Path:
        """
        输入：无（self包含所有数据）
        输出：护照文件路径
        核心逻辑：原子写入 data/brain/passports/{model_id}.json
        """

    @staticmethod
    def load(model_id: str) -> CapabilityPassport | None:
        """
        输入：model_id
        输出：护照实例或None
        """

    @staticmethod
    def list_all() -> list[str]:
        """
        输入：无
        输出：所有已考试模型的model_id列表
        """

class TaskGate:
    """任务门控——根据护照决定是否允许模型执行某个能力类型"""

    def load_passports(self) -> int:
        """加载所有护照，返回加载数"""

    def can_dispatch(self, model_id: str, capability: str) -> tuple[bool, str]:
        """
        输入：model_id, capability
        输出：(是否允许, 原因)
        """
```

### 4.2 数据模型

```python
from enum import Enum

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ExamMode(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    QUICK_SMOKE = "quick_smoke"
    DRIFT_CHECK = "drift_check"
```

核心 dataclass 模型（当前代码使用 `@dataclass`，后续升级应迁移至 Pydantic V2 BaseModel）：

| 模型 | 字段 | 说明 |
|------|------|------|
| BreadthResult | score, passed, total, failed_capabilities | 横轴结果 |
| DepthCapabilityResult | pass_, grade, precision, recall, f1, edit_distance_avg, exact_match_rate, samples_tested, failure_reason | 纵轴单能力结果 |
| DepthResult | overall_score, capabilities: dict[str, DepthCapabilityResult] | 纵轴结果 |
| SpeedResult | avg_latency_ms, latency_p50/p95/p99_ms, tokens_per_second, time_to_first_token_ms | 速轴结果 |
| HallucinationResult | overall_rate, fabrication_rate, inconsistency_rate, refusal_rate | 幻轴结果 |
| DriftResult | tested, output_drift, speed_drift_ratio, hallucination_drift_delta, stable | 稳轴结果 |
| CostEfficiencyResult | local_cost_per_hour, api_cost_per_hour, cost_efficiency_score, deployment_mode(local/api/hybrid), note | 成本效率结果 |
| Recommendations | safe_capabilities, unsafe_capabilities, max_concurrent_tasks, note | 推荐配置 |
| CapabilityPassport | passport_version, model_id, exam_timestamp, exam_duration_seconds, git_commit, overall_grade, overall_score, breadth, depth, speed, hallucination, drift, cost_efficiency, recommendations | 护照主体 |

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `ExamOrchestrator.__init__()` | `chat` | ✅ | 必须有 `.inference(capability, prompt)` 方法 |
| `ExamOrchestrator.__init__()` | `model_id` | ❌ | 空则从 `chat._model` 推断 |
| `run_full_exam()` | `skip_drift` | ❌ | 默认 True |
| `CapabilityPassport.load()` | `model_id` | ✅ | 非空字符串 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `run_full_exam()` | `CapabilityPassport`：五轴结果完整 | 异常冒泡（调用方捕获） |
| `CapabilityPassport.save()` | `Path`：护照文件路径 | `PermissionError`（写入失败） |
| `CapabilityPassport.load()` | `CapabilityPassport` 或 `None` | `None`（文件不存在或解析失败） |
| `TaskGate.can_dispatch()` | `(True, "ok")` | `(False, "no_passport"/"low_accuracy"/"unsafe")` |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增能力类型 | ✅ 向后兼容 | CAPABILITIES 列表扩展 |
| 新增考试模式（ExamMode） | ✅ 向后兼容 | 默认 FULL |
| 护照字段新增 | ✅ 向后兼容 | 旧护照 load 时填默认值 |
| 护照字段删除/重命名 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| DepthResult 评分算法变更 | ⚠️ 需通知 | 影响所有模型排名 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 考试依赖 Ollama 本地推理 | — |
| 2 | 护照存储为 JSON 文件 | — |
| 3 | 当前使用 `@dataclass` 而非 Pydantic V2 | — |
| 4 | 稳轴默认跳过 | `skip_drift=True` |
| 5 | 评分权重 | 横0.30 + 纵0.50 + 幻0.20 |
| 6 | 护照新增 cost_efficiency 维度 | v2.2.0 新增 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模型数 | ~5 | 100 | 1500（capacity_params） | ⚠️ | Passport 分片存储（Phase 3） |
| 能力类型 | 9 | 9 | — | ✅ | — |
| 考试题数 | 27 | 27 | — | ✅ | — |
| 并发考试 | 1（串行） | 100 | 100（capacity_params） | ❌ | 接入 MOD-INF-005 分布式调度（Phase 1） |
| 单次考试 Token | ~10K | ~10K | 日预算 10M | ✅ | 分池管控（全量 vs 增量） |
| 护照存储 | 1 目录 | 100 文件 | — | ⚠️ | ShardRouter 16 分片（Phase 3） |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | `@dataclass` 数据模型 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\capability_passport.py` | 同文件迁移至 Pydantic V2 | 渐进替换 | Grep 所有 import 并更新 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Ollama 无响应 | inference 超时 | 标记该能力 failed，继续其他轴 | 单能力评测缺失 |
| 2 | 护照写入失败 | PermissionError | temp-file 原子写入重试 | 护照丢失 |
| 3 | 护照 JSON 损坏 | json.loads 异常 | load() 返回 None，日志警告 | 该模型无护照，TaskGate 拒绝分配 |
| 4 | 模型连续 3 次超时 | 超时计数 | 标记 EXAM_FAILED_TIMEOUT，护照 blocked | 该模型完全不可用 |
| 5 | Token 预算不足 | BudgetEnforcer 拒绝 | 考试排队等待 | 考试延迟 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 考试题泄露 | 模型针对题库优化 | 题库版本化，定期更新 | 题库 git 变更审计 |
| 2 | 护照篡改 | 模型获得未授权能力 | 护照文件权限控制 + exam_commit SHA | 文件完整性检查 |
| 3 | 考试期间模型被利用 | 资源耗尽 | 考试进程隔离 + Token 预算管控 | BudgetEnforcer 审计 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | ExamOrchestrator 各轴计算 | mock inference 返回，验证 BreadthResult/DepthResult 计算 | 覆盖率 ≥80% |
| 2 | 单元测试 | CapabilityPassport 序列化 | save→load 往返测试 | 数据一致 |
| 3 | 单元测试 | compute_grade 评分 | 边界值 0.90/0.85/0.80/... | 等级正确 |
| 4 | 集成测试 | TaskGate 门控 | pass/unknown/unsafe 三路径 | 门控判定正确 |
| 5 | 集成测试 | 全流程 | OllamaChat→ExamOrchestrator→Passport→TaskGate | 端到端通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-034 (ModelProfiler) | 必须 | benchmark 基础设施、模型发现 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\model_capability_exam\blueprint.md` |
| MOD-INF-009 (Pipeline) | 必须 | 考试任务调度 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-INF-024 (BudgetEnforcer) | 可选 | Token 预算管控 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-INF-005 (分布式执行) | 可选 | 并发考试调度（Phase 1） | — | `D:\ZephyrAlpha\docs\03_modules\_sys-master\blueprint.md` |
| MOD-INF-035 (AutoRuntime Core) | 被依赖 | 消费护照做模型路由 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-GATE_ENGINE (Gate Engine) | 被依赖 | TaskGate 消费护照 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md` |
| 交易决策流水线 C-044⑤ | 被依赖 | 消费护照 cost_efficiency 做LLM路由决策 | — | d:\临时工作区\交易决策流水线设计.md |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-036` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| exam_test_cases.py | exam_orchestrator.py | 题库是考试的前置条件 | 检查 ExamTestCases 实例可导入 |
| exam_orchestrator.py | capability_passport.py | 考试结果写入护照 | 检查 CapabilityPassport.save() 可调用 |
| capability_passport.py | task_gate.py | 护照是门控的前置条件 | 检查护照文件存在 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| exam_orchestrator.py | capability_passport.py | 五轴考试结果 dict | 函数调用 |
| capability_passport.py | task_gate.py | CapabilityPassport JSON | 文件 I/O（load） |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 否 | 模块数<10，手动维护 |
| 2 | 依赖对齐自动验证 | 是 | 有 6 个外部依赖，需自动验证 |
| 3 | 临时时态内容自动清理 | 是 | 有迁移方案（@dataclass→Pydantic） |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中，需检测 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 2 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 3 | 施工步骤完成度自动检测 | pytest+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 2 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 3 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\model_capability_exam\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\` | Python 源码 |
| 考试主控 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` | ExamOrchestrator |
| 题库 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_test_cases.py` | ExamTestCases 27 题 |
| 护照模型 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\capability_passport.py` | CapabilityPassport |
| 包初始化 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\__init__.py` | 公共导出 |
| 任务门控 | `D:\ZephyrAlpha\src\zephyr\runtime\task_gate.py` | TaskGate（消费端） |
| 护照数据 | `D:\ZephyrAlpha\data\brain\passports\` | JSON 护照文件 |
| 测试代码 | `D:\ZephyrAlpha\tests\test_model_capability_exam.py` | 测试用例（待创建） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| AutoRuntime Core | 护照消费 | `CapabilityPassport.load()` | 大脑路由使用护照数据 |
| Gate Engine | 门控判定 | `TaskGate.can_dispatch()` | 低能力模型被拒绝 |
| ModelProfiler | 上游依赖 | benchmark 基础设施复用 | 考试可正常运行 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本升级至 2.1.0 | 蓝图升级 |
| 2 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 更新版本号 | 元数据同步 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\system-dependency-map.md` | 新增 MOD-INF-005 依赖 | 容量升级依赖 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | Ollama 推理不稳定导致考试结果波动 | 中 | 中 | 稳轴漂移检测 + 重考机制 | 风险 |
| 2 | 题库泄露导致模型针对优化 | 低 | 高 | 题库版本化 + 定期更新 | 风险 |
| 3 | 100 并发考试 Token 预算不足 | 中 | 高 | 分池管控 + 增量考试模式 | 风险 |
| 4 | 护照 JSON 单目录 IO 瓶颈 | 低 | 中 | ShardRouter 16 分片（Phase 3） | 风险 |
| 5 | 每次考试消耗 Token | — | 中 | 分池管控 + 增量考试模式 | 负面后果 |
| 6 | 新模型入职有延迟（全量考约 2-5 分钟） | — | 低 | 增量考试模式 + QUICK_SMOKE | 负面后果 |
| 7 | 评分权重固定可能不适用所有场景 | — | 中 | 后续可配置化 | 负面后果 |
| 8 | cost_efficiency 维度依赖外部 API 定价数据 | 中 | 中 | API 定价变化时需重考 cost_efficiency 轴 | 风险 |
| 9 | 本地模型成本受 GPU 占用状态影响（机会成本） | 中 | 中 | cost_efficiency_score 仅记录直接成本，机会成本由下游路由引擎实时计算 | 负面后果 |

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
| 施工阶段数 | 4 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | 考试并发调度与 Token 预算冲突 |
| 目标 generation | 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | Ollama 本地运行 | hard | ☐ | ☐ |
| 2 | MOD-INF-034 ModelProfiler 可用 | hard | ✅ | ✅ |
| 3 | MOD-INF-024 BudgetEnforcer 可用 | soft | ☐ | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：补全测试用例

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 |
| 产出位置 | `D:\ZephyrAlpha\tests\test_model_capability_exam.py` |
| 验收标准 | 覆盖率 ≥80%，所有测试通过 |
| 验证命令 | `python -m pytest tests/test_model_capability_exam.py -v` |
| G7 检查项 | 测试覆盖所有 dataclass 模型 + ExamOrchestrator 各轴 + TaskGate 门控 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-036 | test_model_capability_exam.py | code | `D:\ZephyrAlpha\tests\test_model_capability_exam.py` |

#### 步骤 2：新增 ExamMode 枚举 + 增量考试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` |
| 验收标准 | ExamMode 四枚举值可用，run_incremental_exam() 可运行 |
| 验证命令 | `python -m pytest tests/test_model_capability_exam.py -k exam_mode -v` |
| G7 检查项 | ExamMode 枚举完整，增量考试只重考受影响轴 |

#### 步骤 3：并发考试调度（Phase 1）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` |
| 验收标准 | ThreadPoolExecutor 并发考试，上限可配 |
| 验证命令 | `python -m pytest tests/test_model_capability_exam.py -k concurrent -v` |
| G7 检查项 | 并发上限从 capacity_params.yaml 读取，超时熔断生效 |

#### 步骤 4：超时与熔断

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §6 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` |
| 验收标准 | 单轴超时 120s，全局超时 900s，3 次超时标记 blocked |
| 验证命令 | `python -m pytest tests/test_model_capability_exam.py -k timeout -v` |
| G7 检查项 | 超时参数从 capacity_params.yaml 读取，blocked 护照 TaskGate 拒绝 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 测试失败 | 修复测试，不影响生产代码 |
| 2 | ExamMode 引入导致旧代码不兼容 | ExamMode 默认 FULL，旧调用无需修改 |
| 3 | 并发调度死锁 | 降级为串行，设置 max_workers=1 |
| 4 | 超时误判 | 调大超时阈值，重新考试 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 测试代码 | `D:\ZephyrAlpha\tests\test_model_capability_exam.py` | ☐ | ☐ | ☐ |
| 2 | ExamMode 枚举 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` | ✅ | ☐ | ☐ |
| 3 | 并发调度 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` | ✅ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模型数 | ~5 | `CapabilityPassport.list_all()` |
| 并发考试 | 1（串行） | 代码无并发逻辑 |
| 单次考试 Token | ~8K-10K | 实测估算 |
| 护照存储 | 单目录 | `data/brain/passports/` |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 无并发管理 | 接入 MOD-INF-005 Coordinator | ≥20 模型 |
| GAP-002 | 只有全量考 | ExamMode 增量模式 | ≥50 模型 |
| GAP-003 | 护照单目录 | ShardRouter 16 分片 | ≥200 模型 |
| GAP-004 | 无重考触发 | exam_commit SHA 对比 | ≥20 模型 |
| GAP-005 | 无超时熔断 | 引用 capacity_params.yaml timeouts | 立即 |
| GAP-006 | 无跨模型对比 | CrossModelRanking | ≥500 模型 |
| GAP-007 | Token 消耗未量化 | 分池管控（全量 vs 增量） | 立即 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 五轴评测 + 护照 + TaskGate | ✅ |
| v2.0.0 | 2 | 容量升级 | 并发管理 + 超时熔断 + ExamMode + 资源量化 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | 考试并发管理 | P0 | v2.0.0 | 待施工 |
| GAP-005 | 超时与熔断 | P0 | v2.0.0 | 待施工 |
| GAP-007 | Token 消耗量化 | P1 | v2.0.0 | 待施工 |
| GAP-002 | 增量考试模式 | P1 | v2.1.0 | 待施工 |
| GAP-004 | 重考触发机制 | P1 | v2.1.0 | 待施工 |
| GAP-003 | Passport 分片存储 | P2 | v3.0.0 | 待施工 |
| GAP-006 | 跨模型对比排行 | P2 | v4.0.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ExamMode 枚举 | GAP-002 | exam_orchestrator.py | Phase 1 | 待施工 |
| ExamQueueItem | GAP-001 | exam_orchestrator.py | Phase 1 | 待施工 |
| 超时熔断逻辑 | GAP-005 | exam_orchestrator.py | Phase 1 | 待施工 |
| PassportIndex | GAP-003 | capability_passport.py | Phase 3 | 待施工 |
| CrossModelRanking | GAP-006 | ranking.py（新建） | Phase 4 | 待施工 |

### 分阶段升级路线

| 阶段 | 触发条件 | 升级内容 | 预计工作量 |
|------|:---:|------|:---:|
| Phase 0（当前） | ~5 模型 | 五轴评测 + 护照 + TaskGate | ✅ 已完成 |
| Phase 1 | ≥20 模型 | 并发管理 + 超时熔断 + 资源量化 | ~3d |
| Phase 2 | ≥50 模型 | 增量考试 + 重考触发 | ~2d |
| Phase 3 | ≥200 模型 | Passport 分片存储 + 索引 | ~1d |
| Phase 4 | ≥500 模型 | 跨模型对比排行 + 周检调度 | ~2d |

---

## §18 决策记录

> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。
> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-MCE-01 | 评分权重：横0.30+纵0.50+幻0.20 | A:均等 B:纵优先 C:自定义 | B | 纵轴精度是任务分配最关键指标 | 2026-05-10 |
| 2 | D-MCE-02 | 数据模型用 @dataclass 而非 Pydantic | A:Pydantic B:@dataclass | B | 快速实现，后续迁移 | 2026-05-10 |
| 3 | D-MCE-03 | 稳轴默认跳过 | A:全跑 B:默认跳过 | B | 稳轴耗时过长，非每次必跑 | 2026-05-10 |
| 4 | D-MCE-04 | 容量升级按规模触发器分阶段 | A:一次性 B:分阶段 | B | 模型慢慢加入，不提前过度工程 | 2026-05-12 |
| 5 | D-MCE-05 | 护照新增 cost_efficiency 维度 | A:独立蓝图 B:护照内新增维度 | B | 成本效率是模型能力的固有属性，与护照其他维度变更频率同步，无需独立蓝图 | 2026-05-23 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径的基准在哪 | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 每次新 session 是零记忆 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | 蓝图是施工依据，不是讨论记录 | 关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范 | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界在哪 | 范围漂移 |
| 6 | **容量估算必须写** | AI 不知道系统能容纳多少 | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | AI 不知道旧东西怎么处理 | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令 | 执行漂移 |
| 9 | **蓝图必须自包含** | AI 可能不读引用的文件 | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 删除不可逆 | 永久丢失 |
| 11 | **construction_progress 必须与代码实际状态一致** | 虚假进度误导下一个AI | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 路径不一致=AI找不到代码 | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是 SSoT，蓝图复制代码=双源漂移 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
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
| MCE 蓝图中"容量升级附录"（GAP-001~007） | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| MCE 蓝图中"Token消耗估算" | **原地** | Token 消耗是 MCE 的核心约束，不是独立子系统 |
| MCE 蓝图中"跨模型排行"（GAP-006） | **拆分**（Phase 4） | 独立功能域 + 独立 Phase + 与主体 depends_on 交集<30% |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

本蓝图不涉及文件废弃/迁移/删除。

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期 |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 容量参数配置 | CFG-CAP-001 | — | `D:\ZephyrAlpha\config\capacity_params.yaml` | 并发/超时参数 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | ModelProfiler | `D:\ZephyrAlpha\src\zephyr\pipeline\model-profiler\profiler.py` | benchmark 基础设施 | MCE 是 Profiler 的子系统，扩展 benchmark 为入职考试，不是替代 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\model_capability_exam\blueprint.md` | 修改 | 升级至 v2.1.0 |
| 2 | 考试主控 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_orchestrator.py` | 修改 | 新增 ExamMode + 并发 + 超时 |
| 3 | 护照模型 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\capability_passport.py` | 修改 | 新增 PassportIndex |
| 4 | 题库 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\exam_test_cases.py` | 读取 | 不变更 |
| 5 | 任务门控 | `D:\ZephyrAlpha\src\zephyr\runtime\task_gate.py` | 修改 | 支持 blocked 状态 |
| 6 | 护照数据目录 | `D:\ZephyrAlpha\data\brain\passports\` | 读取 | 不变更 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| MCE 核心架构设计 | **本文档 §1-§10** | 旧 v1.0.0 蓝图 |
| 施工步骤 | **本文档 §16** | — |
| 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 旧 §〇.1-〇.5（已合并） |

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md` | §4 接口契约 |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\runtime\task_gate.py` | CapabilityPassport 数据模型 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\*.py` | §4 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调 | AI 可自主修改 |
| 非关键补充 | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-23 | 2.2.0 | 新增 cost_efficiency 维度：护照新增 CostEfficiencyResult 数据模型（local_cost_per_hour/api_cost_per_hour/cost_efficiency_score/deployment_mode）；§2.1 职责范围新增"成本效率评估"；§5.1 技术约束新增护照 cost_efficiency 维度；§10.1 新增交易决策流水线 C-044⑤ 被依赖声明；§14 新增风险#8/#9；§18 新增决策 D-MCE-05 |
| 2026-05-14 | 2.1.0 | v3.5 模板对齐：§0前移至概述后；§7备选方案删除（由§18决策记录覆盖）；§15后果删除（负面合并到§14风险+增加类型列）；§0.1新增存在性列；§5.1去掉原因列；§10拆为§10.1~§10.4；铁律新增#13~#15；新增蓝图拆分判定标准；施工声明标注时态属性；§18增加覆盖说明+时态属性 |
| 2026-05-14 | 2.0.0 | v3.3 模板对齐升级：H1标题格式+概述段+frontmatter补全+标准锚点+章节重排+补缺章节+容量升级内容合并至§17+construction_progress修正为partially_implemented+绝对路径+蓝图特有章节保留 |
| 2026-05-12 | 1.0.0 | 初始蓝图：五轴评测+护照+TaskGate+容量升级分析 |

---

## 蓝图特有章节

### 蓝图特有：五维评测架构详解

> 来源：v1.0.0 蓝图 §2-§5，规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：五维评测是 MCE 的核心架构，其他蓝图无此评测体系
> 不可砍理由：砍掉后 AI 施工者无法理解五轴评测的具体逻辑

五轴评测流程：横轴（BreadthExam，每能力 1 题验证结构）→ 纵轴（DepthExam，通过能力各跑 3 题算 F1）→ 速轴（延迟 P50/P95/P99 + 吞吐 + TTFT）→ 幻轴（编造/不一致/拒绝三率）→ 稳轴（cold→load→hot 三阶段漂移）。

纵轴深度阈值（DEPTH_THRESHOLDS）：

| 能力类型 | 阈值 |
|---------|:---:|
| task_classification | 0.60 |
| code_fix | 0.60 |
| tag_completion | 0.55 |
| summary_extraction | 0.55 |
| refactor | 0.55 |
| code_generate | 0.55 |
| dead_code_removal | 0.55 |
| naming_suggest | 0.50 |
| anomaly_triage | 0.50 |

评分等级（compute_grade）：A+(≥0.90) / A(≥0.85) / A-(≥0.80) / B+(≥0.75) / B(≥0.70) / B-(≥0.65) / C+(≥0.60) / C(≥0.55) / C-(≥0.50) / D(≥0.40) / F(<0.40)。

### 蓝图特有：考试题库命名空间

> 来源：v1.0.0 代码 exam_test_cases.py
> 仅本蓝图需要：题库 ID 命名规则仅 MCE 使用
> 不可砍理由：砍掉后 AI 新增题时不知道 ID 格式

题库 ID 格式：`EX-{能力缩写}-{序号}`

| 能力类型 | 缩写 | 题数 |
|---------|:---:|:---:|
| task_classification | CL | 3 |
| tag_completion | TG | 3 |
| summary_extraction | SE | 3 |
| naming_suggest | NS | 3 |
| anomaly_triage | AT | 3 |
| code_fix | CF | 3 |
| refactor | RF | 3 |
| code_generate | CG | 3 |
| dead_code_removal | DC | 3 |

### 蓝图特有：Token 消耗估算

> 来源：v1.0.0 蓝图 §〇.3 缺口③
> 仅本蓝图需要：MCE 是唯一需要量化考试 Token 消耗的模块
> 不可砍理由：砍掉后 BudgetEnforcer 无法精确管控

| 考试模式 | 估算 Token 消耗 |
|---------|:---:|
| 全量考（FULL） | ~8,000-10,000 |
| 增量考（INCREMENTAL） | ~2,000 |
| 快速冒烟（QUICK_SMOKE） | ~500 |
| 漂移复查（DRIFT_CHECK） | ~1,500 |
| 100 并发全量考 | ~1,000,000（占日预算 10%） |

---
