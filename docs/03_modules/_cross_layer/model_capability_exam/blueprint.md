---
module_id: MOD-INF-036
submodule_path: src/zephyr/intelligence/model_profiling
title: "Model Capability Exam 蓝图 — 模型能力考试·多维度能力评估"
doc_type: blueprint
status: Active
version: "2.3.2"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/infrastructure/model_capability_exam/ + src/zephyr/intelligence/model_evaluation/
last_updated: "2026-06-27"
last_verified: "2026-06-27"
generation: 2
functional_domain: intelligence
summary: "AI模型入职考试系统——五维评测产出CapabilityPassport能力护照，驱动TaskGate任务门控。"
template_for: blueprint
tags: [model-capability-exam, exam, benchmark, capability-passport, task-gate, model-profiler, cross-layer]
priority: P1
activation_phase: current
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
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Model Capability Exam 蓝图 — 模型能力考试·多维度能力评估

> module_id: MOD-INF-036 | version: 2.1.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/intelligence/model_profiling/ | generation: 2 | construction_progress: partially_implemented

## 概述

ModelCapabilityExam（MCE）是 ModelProfiler（MOD-INF-034）的子系统，负责 AI 模型入职考试。每条 AI 进入系统时自动跑五维评测（横轴能力覆盖、纵轴精度深度、速轴延迟吞吐、幻轴幻觉率、稳轴长时间漂移），产出 CapabilityPassport 能力护照，驱动 TaskGate 只分配模型 pass=true 的能力。**v2.3.0新增**：三级考试模式（Quick 5-8min / Standard 20-30min / Deep 2-3h）+ 九维幻觉检测（fabrication/inconsistency/refusal/overclaim/context_drift/source_confusion/instruction_drift/format_hallucination/quantity_hallucination）+ 岗位匹配（JobMatcher 基于 required/bonus/max_hallucination 推荐适合岗位）。**设计原则**：幻觉率与成本均为正常评分维度（非一票否决、非硬门）——任何模型都有幻觉，只是高低问题；成本是岗位匹配考量维度之一，claude 贵但必要时仍可用。当前规模 ~5 模型 / 9 能力类型 / 29 道标准题，目标容量 100 模型并发。上游依赖 ModelProfiler + Pipeline + BudgetEnforcer，下游被 AutoRuntime Core + Gate Engine + 交易决策流水线 C-044⑤ 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-036`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3.1 | 公共导出 | 已实现 | — |
| 2 | `exam_orchestrator.py` | §3.1 / §4.1 | 五轴考试主控 + 九维幻觉检测 + 三级模式 | 已实现 | — |
| 3 | `exam_test_cases.py` | §3.1 / §4.2 | 29 道标准题库（9 能力 × 3 难度 + OLYMPIAD） | 已实现 | — |
| 4 | `capability_passport.py` | §3.1 / §4.2 | 护照数据模型+持久化 + HallucinationBreakdown 九维 + QuickProfile | 已实现 | — |
| 5 | `exam_rubric.py` | §3.1 | 三轨评分规则（rubric 轨） | 已实现 | — |
| 6 | `exam_executor.py` | §3.1 | 三轨评分执行器（executor 轨，运行测试用例） | 已实现 | — |
| 7 | `exam_judge.py` | §3.1 | 三轨评分裁判（judge 轨，LLM/确定性裁判） | 已实现 | — |
| 8 | `job_matcher.py` | §3.1 / §4.1 | 岗位匹配（required/bonus/max_hallucination） | 已实现 | — |
| 9 | `case_assembler.py` | §3.1 | 题目组装器 | 已实现 | — |
| 10 | `provider_data.py` | §3.1 | 模型提供商数据 | 已实现 | — |
| 11 | `scripts/quick_profile.py` | §4.1 | Quick 模式 CLI 入口（--from-passport/--model/--list） | 已实现 | — |
| 12 | `data/brain/job_matrix.yaml` | §4.2 | 岗位匹配矩阵（9 维幻觉权重 + 岗位定义） | 已实现 | — |
| 13 | `tests/test_exam_orchestrator.py` | §9 | ExamOrchestrator 测试（含九维幻觉检测） | 已实现 | — |
| 14 | `tests/test_job_matcher.py` | §9 | JobMatcher 测试（36 tests） | 已实现 | — |

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
| v2.3.0 (三级模式+九维幻觉+岗位匹配) | ExamOrchestrator(九维+三级), capability_passport(HallucinationBreakdown 九维+QuickProfile), job_matcher, quick_profile.py, job_matrix.yaml, exam_rubric/executor/judge(三轨评分) | Cost 轴, Tool 轴 | 见 §17.4 未来路线图 |
| v2.3.1 (Cost+Tool 轴+首个真实护照) | 同 v2.3.0 + CostBreakdown(cost_score)+Tool 轴(function_calling/tool_chaining 6题)+QuickProfile.save()/load()持久化+data/brain/quick_profiles/qwen3_8b.json | 无 (P1 全完成) | 见 §17.4 未来路线图 |
| v2.3.2 (Claude审查修复+CI检查) | 同 v2.3.1 + exam_test_cases.py(23孤儿激活+2废弃删除+2负例对照=127题) + check_exam_case_consistency.py(CI一致性检查) + §17.5方法论风险记录 | 无 | 见 §17.5 已知方法论风险 |

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
| 4 | 题库管理 | ExamTestCases 29 道标准题，9 能力 × 3 难度 + OLYMPIAD 题 |
| 5 | 门控集成 | TaskGate 消费护照做任务分配判定 |
| 6 | 成本效率评估 | 护照新增 cost_efficiency 维度，记录模型在本地GPU vs 云端API两种部署模式下的成本效率，供下游LLM路由成本引擎消费 |
| 7 | 三级考试模式 | Quick（5-8min, 29题+5能力幻觉检测）/ Standard（20-30min, n=1+skip_drift）/ Deep（2-3h, n>=3+full drift+LLM judge） |
| 8 | 九维幻觉检测 | fabrication/inconsistency/refusal/overclaim/context_drift/source_confusion/instruction_drift/format_hallucination/quantity_hallucination |
| 9 | 岗位匹配 | JobMatcher 基于 required(硬性满足)+bonus(加分项)+max_hallucination(期望非硬门) 推荐适合岗位 |

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
| MOD-INF-005 (分布式执行) | 可选 | 并发考试调度（Phase 1） | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |
| MOD-INF-035 (AutoRuntime Core) | 被依赖 | 消费护照做模型路由 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-GATE_ENGINE (Gate Engine) | 被依赖 | TaskGate 消费护照 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
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
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 新增 MOD-INF-005 依赖 | 容量升级依赖 |

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
| Phase 0（当前） | ~5 模型 | 五轴评测 + 护照 + TaskGate + 三级模式 + 九维幻觉 + 岗位匹配 | ✅ 已完成 |
| Phase 1 | ≥20 模型 | 并发管理 + 超时熔断 + 资源量化 | ~3d |
| Phase 2 | ≥50 模型 | 增量考试 + 重考触发 | ~2d |
| Phase 3 | ≥200 模型 | Passport 分片存储 + 索引 | ~1d |
| Phase 4 | ≥500 模型 | 跨模型对比排行 + 周检调度 | ~2d |

### §17.4 未来工作路线图（v2.3.0+）

> **时态属性**：本节属于**永久时态**——记录未来工作规划，AI 修改设计时必读，防止重复决策。
> 路线图按优先级排序，每项标注状态（进行中/暂缓/按需推进）。

#### 设计原则（适用于所有未来工作）

| 原则 | 说明 |
|------|------|
| 幻觉率正常评分 | 幻觉率是正常评分维度，**非一票否决、非硬门**。任何模型都有幻觉（含 Claude），只是高低问题。考试维度可多，但评分正常参与排序。未来岗位匹配时幻觉率权重较高，但当前不做淘汰。 |
| 成本是维度非硬门 | 成本是岗位匹配的考量维度之一，**非一票否决**。claude 贵但必要时仍可用。本地模型成本≈0，云端模型成本按 API 定价计算。 |
| 能力轮廓 > 每题精度 | 岗位匹配用五级粗分级（A/B/C/D/F），能力轮廓比每题精度更重要——测出"擅长什么"比"每题多少分"更有岗位指导价值。 |
| 向内收拢 | 优先扩展已有功能，不创造新文件；优先复用已有数据，不重复采集。 |

#### 路线图清单

| 路线图ID | 工作项 | 优先级 | 状态 | 依赖 | 说明 |
|---------|--------|:---:|:---:|------|------|
| ROADMAP-01 | P2 Cost 轴 | P0 | ✅ 完成 | 无 | 从已有 `_all_latencies_ms`/`_all_tokens` 派生 token 成本，接入岗位匹配矩阵。本地模型成本≈0，云端模型按 API 定价（input/output token 价格）。成本是评分维度非硬门。 |
| ROADMAP-02 | P2 Tool 轴 | P1 | ✅ 完成 | ROADMAP-01 | 设计工具调用能力测试题（function_calling + tool_chaining），扩展能力维度。新增 6 题（EX-FC-001~003, EX-TC-001~003），ExamTestCase 新增 P 类字段（expected_function_args/expected_tool_sequence），DeterministicJudge + _compute_metrics_generic 评分扩展。 |
| ROADMAP-03 | 真实本地模型 Quick 考试验证 | P1 | ✅ 完成 | ROADMAP-01, ROADMAP-02 | 用 quick_profile.py 对真实本地模型跑一次 Quick 考试，验证端到端流程，产出第一个真实护照。qwen3:8b 护照已保存到 data/brain/quick_profiles/qwen3_8b.json，综合分 0.743(B)，推荐规则守门员 88.4%。 |
| ROADMAP-04 | P1-1 题目外置 YAML | P2 | 按需推进 | 无 | 把 exam_test_cases.py 中硬编码题目外置到 YAML，让题目可配置、可扩展。当前题目数（102）足够覆盖岗位匹配，等需要批量加题（每能力 20+ 题）时再做。避免过早工程化。 |
| ROADMAP-05 | P2 Patch 轴 | P3 | 暂缓 | 无 | 补丁生成能力（生成可应用 diff/patch）。本质是代码能力细分，当前 `code_fix`/`refactor` 已部分覆盖。与现有代码能力重叠，优先级低。 |
| ROADMAP-06 | P3 Agent Loop | P3 | 暂缓 | ROADMAP-03 | Agent 循环测试——模型在多轮对话/工具循环中的表现。高级岗位（自主 agent）需要。Quick 模式有真实数据后再推进。 |
| ROADMAP-07 | P3 真实仓库测试 | P3 | 暂缓 | ROADMAP-06 | 在真实代码库上测试模型能力。最贴近实际岗位，但实现复杂度高。 |
| ROADMAP-08 | P4 持续画像 | P4 | 暂缓 | ROADMAP-03 | 模型升级后重新考试，跟踪能力变化。运维需求，等有 3+ 个护照后才有意义。 |

#### 路线图执行顺序

```
当前状态: v2.3.0 已完成（三级模式 + 九维幻觉 + 岗位匹配 + Quick CLI）
    │
    ▼
ROADMAP-01: P2 Cost 轴 (进行中)
    │  从已有 latency/token 数据派生成本，接入 job_matrix.yaml
    ▼
ROADMAP-02: P2 Tool 轴 (中工程)
    │  设计工具调用测试题，扩展能力维度
    ▼
ROADMAP-03: 真实 Quick 考试验证
    │  产出第一个真实护照，验证端到端流程
    ▼
按需推进:
    ├ ROADMAP-04: P1-1 题目外置 YAML (当题库需要批量扩展时)
    ├ ROADMAP-05: P2 Patch 轴 (当需要细分代码能力时)
    ├ ROADMAP-06: P3 Agent Loop (当 Quick 有真实数据后)
    ├ ROADMAP-07: P3 真实仓库测试 (当 Agent Loop 成熟后)
    └ ROADMAP-08: P4 持续画像 (当有 3+ 护照后)
```

### §17.5 已知方法论风险（Claude 外部审查记录）

> **时态属性**：本节属于**永久时态**——记录已知方法论风险，AI 修改题库/评分时必读，防止忽视根本性方法论问题。
> **来源**：Claude 对 `exam_test_cases.py` 的外部架构审查（2026-06-27）
> **处理策略**：机械发现（2.1孤儿题/2.2缺负例）已代码修复 + CI 检查脚本 [check_exam_case_consistency.py](file:///D:/ZephyrAlpha/scripts/governance/check_exam_case_consistency.py) 防复发；方法论发现（3.1-3.5 + 2.3）记录在此，不在本轮代码修复，待后续按需推进。

#### 风险清单

| # | 风险ID | 风险 | 严重度 | 状态 | 说明 | 缓解措施/后续行动 |
|---|--------|------|:---:|:---:|------|------|
| 1 | RISK-3.1 | 目标分差反向校准 | 高 | 记录 | 先定分差结论（deepseek vs qwen = 1.2-1.4x）再调题目参数（针密度/通过阈值），颠倒了评测因果链——experimenter degrees of freedom / Goodhart's Law 自我作用。题库"靴带"系在旧结论上，模型升级后偏差隐性自我巩固且难发现。 | 后续：题库参数调整必须基于独立基准（非目标分差）；审查题库变更时检查是否有"调参凑分差"行为；考虑引入盲调机制（出题人不看分差数据）。 |
| 2 | RISK-3.2 | 裁判层偏差不可见 | 高 | 记录 | judge×0.4 占奥赛分 40%，奥赛分决定综合分封顶系数（0.80~1.00）。LLM-as-judge 存在 verbosity bias / self-preference bias / position bias，同源模型互判会系统性偏差，杠杆效应放大（非线性误差）。判分引擎不在题库层，无法在审查范围内验证。 | 后续：审查判分引擎是否做到 (a) 裁判与被测模型解耦（禁止同源/同厂互判）(b) 输出匿名化（隐去模型身份）(c) 关键奥赛题 ≥2 厂商裁判交叉验证 + 人工抽样复核边界题。 |
| 3 | RISK-3.3 | 单题统计可靠性不足 | 中 | 记录 | 多数（能力×难度）单元格 n=1~3，29 轴能力画像多数在统计意义上是噪声，却被当 TaskGate 路由信号。综合分信度尚可（104+ 题汇总），但细粒度能力轴信度不足——一道题的措辞差异就能让分数 0%↔100% 跳变。 | 后续：ROADMAP-04 题目外置后批量扩展至每能力 20+ 题提升单轴信度；当前用五级粗分级（A/B/C/D/F）降低噪声敏感度，能力轮廓 > 每题精度。 |
| 4 | RISK-3.4 | 静态题库污染风险 | 中 | 记录 | 静态题库经 6+ 厂商 API 通道明文传输（DeepSeek/Qwen/Kimi/GLM/MiniMax/Gemini/Claude），长期使用存在被动暴露风险。一旦进入未来模型训练语料，评测体系渐进失效且不可感知（表面分数仍"看起来合理"）。 | 后续：评估题库私有化/加密、动态滚动更新（参考 LiveBench/LiveCodeBench）、题目改写扰动方案；逐家核实厂商数据使用条款。 |
| 5 | RISK-3.5 | 真实源码跨厂商 API 暴露 | 高 | 记录 | OLY-007~023 嵌入 `task_gate.py`/`git_commit_gateway.py` 等核心治理源码（单题 8K-10K 字符），跑分时发往多家第三方 API。与 Trae CN 尽调结论（即使关闭遥测仍上传数据）形成同类风险——核心治理/交易模块源码被常态化发往第三方。 | 后续：评估用脱敏/合成代码替代真实源码，或限制奥赛题仅用本地模型跑分；至少对核心治理文件做 API 暴露评估。 |
| 6 | RISK-2.3 | expected_contains 判分语义不可审计 | 中 | 记录 | 高权重纵轴(0.50)大量用 expected_contains 软匹配，但 AND/OR 语义、大小写/中英文敏感度、字面 vs 语义匹配均未在题库层定义，仅存在于判分引擎。字面子串匹配天然脆弱（假阴/假阳），中英文关键词混填是缓解性打补丁非根治。 | 后续：判分引擎审查时确认 expected_contains 语义并文档化到题库层；评估语义对齐替代方案（如 embedding 相似度）。 |

#### 审查修复对照

| 审查发现 | 类型 | 处理 | 验证 |
|---------|------|------|------|
| 2.1 孤儿题/能力天窗（29道死代码） | 机械 | ✅ 代码修复：23 孤儿激活 + 2 废弃副本删除 + 2 负例新增 = 127 题 | `check_exam_case_consistency.py` → ALL CLEAN（定义127=注册127） |
| 2.2 二元判断缺负例对照组 | 机械 | ✅ 代码修复：EX_SR_005(has_bug=False) + EX_RC_004(compliant=True) | self_review=[T,T,T,T,F], rule_comp=[F,F,F,T] |
| 2.3 expected_contains 语义不可审计 | 方法论 | ⏳ 记录 RISK-2.3 | 待判分引擎审查 |
| 3.1 目标分差反向校准 | 方法论 | ⏳ 记录 RISK-3.1 | 待后续范式调整 |
| 3.2 裁判偏差不可见 | 方法论 | ⏳ 记录 RISK-3.2 | 待判分引擎审查 |
| 3.3 单题统计可靠性 | 方法论 | ⏳ 记录 RISK-3.3 | 待 ROADMAP-04 批量扩题 |
| 3.4 静态题库污染 | 方法论 | ⏳ 记录 RISK-3.4 | 待评估动态更新方案 |
| 3.5 真实源码 API 暴露 | 方法论 | ⏳ 记录 RISK-3.5 | 待评估脱敏/本地化方案 |

> **审查基线说明**：Claude 审查基于旧版本题库（声称 context_management 6 题全未注册）。实际 context_management 已在 P0 修复中全部注册（EX_CFAW_001~003 + EX_CWM_001~003），本审查修复处理了其余仍然成立的发现。

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
| 6 | D-MCE-06 | 幻觉率正常评分（非一票否决） | A:一票否决(硬门) B:正常评分维度 C:不检测 | B | 任何模型都有幻觉（含 Claude），只是高低问题。幻觉率正常参与评分排序，非硬门淘汰。考试维度可多（九维），但评分正常。未来岗位匹配时幻觉率权重较高，但当前不做淘汰。 | 2026-06-27 |
| 7 | D-MCE-07 | 成本是维度非硬门 | A:成本硬门(超阈值淘汰) B:成本是评分维度 C:不测成本 | B | 成本是岗位匹配考量维度之一，非一票否决。claude 贵但必要时仍可用。本地模型成本≈0，云端按 API 定价。成本与幻觉率同为正常评分维度。 | 2026-06-27 |
| 8 | D-MCE-08 | 三级考试模式（Quick/Standard/Deep） | A:单一全量考 B:三级模式 C:仅 Quick | B | 不同场景需要不同精度：Quick 5-8min 快速画像适合岗位初筛；Standard 20-30min 适合正式评测；Deep 2-3h 适合深度认证。能力轮廓 > 每题精度。 | 2026-06-27 |
| 9 | D-MCE-09 | 岗位匹配用五级粗分级 | A:细粒度分数 B:五级粗分级(A/B/C/D/F) C:二值(pass/fail) | B | 岗位匹配关注"擅长什么"而非"每题多少分"。五级粗分级降低噪声，能力轮廓清晰。match_score=0.5(required基础)+bonus_ratio×0.3+hallu_score×0.2。 | 2026-06-27 |
| 10 | D-MCE-10 | 九维幻觉检测（参考 ChatGPT 建议扩展） | A:三维(fab/inc/ref) B:六维 C:九维 | C | 参考业界实践 + ChatGPT 建议，从 3 维扩展到 9 维：新增 context_drift(独立检测)、instruction_drift、format_hallucination、quantity_hallucination。权重总和 1.00，fabrication 仍最重要(0.20)。 | 2026-06-27 |

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
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` | §4 接口契约 |
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
| 2026-06-27 | 2.3.0 | 新增三级考试模式（Quick/Standard/Deep）+ 九维幻觉检测 + 岗位匹配（JobMatcher）。§0.1 代码文件清单新增 10 个文件（exam_rubric/executor/judge, job_matcher, quick_profile.py, job_matrix.yaml, 测试等）；§0.3 新增 v2.3.0 版本映射；§2.1 职责范围新增#7-#9（三级模式/九维幻觉/岗位匹配）；§17 分阶段升级路线 Phase 0 标记已完成；新增 §17.4 未来工作路线图（ROADMAP-01~08，含 P1-1 题目外置/P2 Cost轴/P2 Tool轴/P2 Patch轴/P3 Agent Loop/P3 真实仓库/P4 持续画像）；§18 新增决策 D-MCE-06~10（幻觉率正常评分/成本非硬门/三级模式/五级粗分级/九维幻觉）。设计原则：幻觉率与成本均为正常评分维度，非一票否决。 |
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

## 附录 A：详细设计规范（从 specifications/model_capability_exam/spec.md 迁移，2026-07-01）

> 以下内容原存于 specifications/model_capability_exam/spec.md（MOD-SPEC-004），已收敛至本蓝图。
> 注意：本蓝图 v2.3.2 已在部分领域超越 spec.md v1.0.0（如九维幻觉检测、三级考试模式、岗位匹配），
> 附录内容保留 v1.0.0 原始设计细节作为实现参考。

### A.1 能力 → 验证 Prompt 映射（原 spec.md §2.2）

| 能力类型 | 验证 Prompt | 通过条件 |
|----------|------------|----------|
| `task_classification` | "classify this module: hello\nprint('hello')" | 返回 JSON 含 `category` 字段 |
| `tag_completion` | "generate tags for: hello\nprint('hello')" | 返回 JSON 含 `tags` 数组 |
| `summary_extraction` | "summarize: The project uses FastAPI for REST APIs and Pydantic for validation" | 返回 JSON 含 `points` 数组 |
| `naming_suggest` | "suggest names for: def f(x): return x+1" | 返回 JSON 含 `names` 数组 |
| `anomaly_triage` | "triage: 500 Internal Server Error at /api/users" | 返回 JSON 含 `needs_human` 布尔 |
| `code_fix` | "fix: def add(a,b): return a-b  # bug: should be a+b" | 返回 JSON 含 `fixes` 数组 with `old_str`,`new_str` |
| `refactor` | "refactor: def f(): x=1;y=2;return x+y" | 返回 JSON 含 `changes` 数组 |
| `code_generate` | "generate: a function that checks if a number is prime" | 返回 JSON 含 `content` 字段 |
| `dead_code_removal` | "find dead code: def used():pass\ndef unused():pass" | 返回 JSON 含 `dead_sections` 数组 |

### A.2 DepthTestCase 数据结构（原 spec.md §3.2）

```python
@dataclass
class DepthTestCase:
    case_id: str           # "DC-001"
    capability: str        # "code_fix"
    difficulty: str        # "easy" | "medium" | "hard"
    prompt: str            # 输入
    expected_old_str: str  # code_fix/refactor/dead_code: 期望找到的旧代码
    expected_new_str: str  # code_fix/refactor: 期望的新代码
    expected_tags: list[str]     # tag_completion: 正确答案
    expected_category: str       # classification: 正确答案
    tolerance: float = 0.0       # 容差（edit_distance 允许误差）
```

### A.3 各能力类型深度测试题（原 spec.md §3.3，首批各 3 道）

**task_classification:**
```
DC-CL-001: classify a FastAPI router → expected: "api" | "web"
DC-CL-002: classify a numpy computation module → expected: "computation" | "numeric"
DC-CL-003: classify a config loader → expected: "config" | "infrastructure"
```

**tag_completion:**
```
DC-TG-001: "OllamaChat 推理引擎" → expected: ["inference","llm","chat","ollama"]
DC-TG-002: "EmbeddingRouter 向量路由" → expected: ["embedding","vector","semantic"]
DC-TG-003: "ActionDispatcher 动作分发" → expected: ["dispatch","action","runtime"]
```

**code_fix:**
```
DC-CF-001: def add(a,b): return a-b  # bug → expected_old="a-b", expected_new="a+b"
DC-CF-002: for i in range(len(arr)): arr[i]=arr[i]*2 → expected refactor to comprehension
DC-CF-003: if x = 5: print(x) → expected fix = to ==
```

**refactor:**
```
DC-RF-001: 过长函数 → 期望拆分为多个小函数
DC-RF-002: 重复代码 → 期望提取公共逻辑
DC-RF-003: 魔法数字 → 期望替换为常量
```

**code_generate:**
```
DC-CG-001: 生成 is_prime(n) → 期望: 含 loop + sqrt 优化
DC-CG-002: 生成 fibonacci(n) → 期望: 返回值正确
DC-CG-003: 生成 JSON 解析器 → 期望: try-except + json.loads
```

**dead_code_removal:**
```
DC-DC-001: 发现未使用 import → expectation: 标记对应行
DC-DC-002: 发现不可达代码 → expectation: 标记 return 后的代码
DC-DC-003: 发现未调用函数 → expectation: 标记无引用的 def
```

### A.4 评分指标公式（原 spec.md §3.4）

```python
# 分类/标签类
precision = |predicted ∩ expected| / |predicted|      # 预测中有多少是对的
recall    = |predicted ∩ expected| / |expected|        # 正确答案中找到了多少
f1        = 2 * precision * recall / (precision + recall)

# 代码修改类
edit_distance = Levenshtein(predicted_code, expected_code)
exact_match   = 1 if predicted == expected else 0
normalized_ed = 1 - (edit_distance / max(len(predicted), len(expected)))

# 生成类
pass_rate   = 通过的测试用例 / 总测试用例
code_exec   = 0/1 是否可执行（语法检查通过）

depth_score = Σ(加权 F1/EM/normalized_ED) / 总测试数
```

### A.5 HallucinationCheck 类骨架（原 spec.md §5.1）

```python
class HallucinationCheck:
    """三棱镜检测法"""

    @staticmethod
    def fabrication_check(output: dict, source_text: str) -> bool:
        """模型是否编造了输入中不存在的内容"""
        # 检查 output 中的 old_str 是否真的存在于 source_text
        ...

    @staticmethod
    def consistency_check(outputs: list[dict]) -> float:
        """多次跑同一 prompt，输出的一致性"""
        # 计算输出之间的 Jaccard 相似度
        ...

    @staticmethod
    def refusal_check(output: dict) -> bool:
        """模型是否拒绝了任务（输出空/错误/拒绝语）"""
        ...
```

### A.6 漂移测试三阶段协议（原 spec.md §6.1）

```
阶段 1 — 冷启动测试:
    模型刚加载 → 跑完整 depth exam → 记录 baseline

阶段 2 — 负载测试:
    连续提交 20 个随机任务 → 每 5 个任务后穿插 1 道 repeat 题
    → 追踪 repeat 题的输出变化

阶段 3 — 热稳定测试:
    负载完成后静置 30s → 再跑一次 depth exam
    → 与 baseline 比较
```

### A.7 CapabilityPassport 完整 JSON 示例（原 spec.md §7，qwen3:8b 护照）

```json
{
  "passport_version": "1.0.0",
  "model_id": "qwen3:8b",
  "exam_timestamp": "2026-05-08T15:45:56.097326+00:00",
  "exam_duration_seconds": 42.5,
  "git_commit": "23d213b3ab1758faf69843a660d8511fb245745a",

  "overall_grade": "C+",
  "overall_score": 0.62,

  "breadth": {
    "score": 0.89,
    "passed": 8,
    "total": 9,
    "failed_capabilities": ["code_fix"]
  },

  "depth": {
    "overall_score": 0.71,
    "capabilities": {
      "task_classification": {
        "pass": true,
        "grade": "B",
        "precision": 0.85,
        "recall": 0.80,
        "f1": 0.82,
        "samples_tested": 3
      },
      "tag_completion": {
        "pass": true,
        "grade": "B+",
        "precision": 0.90,
        "recall": 0.86,
        "f1": 0.88,
        "samples_tested": 3
      },
      "code_fix": {
        "pass": false,
        "grade": "F",
        "precision": 0.35,
        "recall": 0.28,
        "f1": 0.31,
        "edit_distance_avg": 45.2,
        "exact_match_rate": 0.0,
        "samples_tested": 3,
        "failure_reason": "low_precision_below_threshold"
      }
    }
  },

  "speed": {
    "avg_latency_ms": 520,
    "latency_p50_ms": 480,
    "latency_p95_ms": 890,
    "latency_p99_ms": 1200,
    "tokens_per_second": 42.5,
    "time_to_first_token_ms": 180
  },

  "hallucination": {
    "overall_rate": 0.12,
    "fabrication_rate": 0.08,
    "inconsistency_rate": 0.15,
    "refusal_rate": 0.02
  },

  "drift": {
    "tested": true,
    "output_drift": 0.05,
    "speed_drift_ratio": 1.10,
    "hallucination_drift_delta": 0.02,
    "stable": true
  },

  "recommendations": {
    "safe_capabilities": [
      "task_classification",
      "tag_completion",
      "summary_extraction",
      "naming_suggest",
      "anomaly_triage"
    ],
    "unsafe_capabilities": [
      "code_fix",
      "refactor"
    ],
    "max_concurrent_tasks": 4,
    "note": "code_fix 精度 31% 低于 50% 阈值，已禁用。建议使用更强模型做代码修改类任务。"
  }
}
```

### A.8 TaskGate 代码骨架（原 spec.md §8）

```python
class TaskGate:
    """任务门控——dispatch 前检查护照"""

    def __init__(self, passport_dir: Path):
        self._passports: dict[str, CapabilityPassport] = {}
        self._passport_dir = passport_dir

    def load_passport(self, model_id: str) -> CapabilityPassport | None:
        """加载模型的能力护照"""
        ...

    def can_dispatch(self, model_id: str, capability: str) -> tuple[bool, str]:
        """判断模型是否可以执行某个能力类型的任务"""
        passport = self._passports.get(model_id)
        if passport is None:
            return (False, "no_passport")
        cap = passport.depth.capabilities.get(capability)
        if cap is None:
            return (False, "capability_not_tested")
        if not cap.pass_:
            return (False, f"low_accuracy: {cap.failure_reason}")
        return (True, "ok")

    def get_safe_capabilities(self, model_id: str) -> list[str]:
        """返回模型安全可用的能力列表"""
        ...
```

### A.9 集成到 AutoRuntime 启动流程（原 spec.md §9）

```
boot_sequence 当前 16 步 → 扩展为 17 步:

Step 15: LocalModelScheduler 启动
Step 16: 模型 Benchmark (现有)
Step 17: ModelCapabilityExam 入职考试     ← NEW
Step 18: TaskGate 加载护照                 ← NEW

_run_cycle 修改:
    AutoTaskGenerator.generate() 生成任务时,
    对每个任务检查 TaskGate.can_dispatch(model_id, capability),
    不通过 → 跳过该任务类型
```

### A.10 文件规划（原 spec.md §10）

> **SSoT**：考试系统 + 模型画像器已合并至 `src/zephyr/intelligence/model_profiling/`（唯一真源 #3）。
> `infrastructure/model_profiler/` 与 `infrastructure/model_capability_exam/` 仅保留 `__init__.py` 垫片转发。

```
src/zephyr/intelligence/model_profiling/   ← SSoT #3（考试系统 + 模型画像器）
    __init__.py                ← 公共导出
    exam_orchestrator.py       ← 五轴考试主控（横/纵/速/幻/稳轴合并实现）
    exam_test_cases.py         ← 27 道标准题库（9 能力 × 3 难度）
    capability_passport.py     ← 护照数据模型 + IO（TaskGate 消费）
    benchmark_suite.py         ← 7 维 × 26 项 benchmark 用例（profiler）
    profiler.py                ← 评测引擎（profiler）
    model_discovery.py         ← 模型发现（profiler）
    results_writer.py          ← 结果持久化 + 漂移检测（profiler）
    task_model_learner.py       ← 任务×模型学习矩阵（profiler）
    cli.py                     ← CLI 入口（profiler）
    deepseek_v4_chat.py        ← DeepSeek V4 Chat 适配器（profiler）
    provider_data.py           ← provider 数据（profiler）

data/
    brain/
        passports/                  ← 护照存储
            qwen3:8b.json
            deepseek-r1:8b.json
            ...
```

### A.11 踩过的坑 & 设计原则（原 spec.md §11，6 条 v1.0.0 设计原则）

1. **横轴和纵轴必须分离** — 横轴只问"能产出合法的结构化结果吗"，纵轴才问"结果正确吗"
2. **幻觉检测不是一次性的** — 需要多次重复 + 输入交叉验证
3. **漂移测试需要热负载** — 冷启动测试和长时间运行测试必须分开
4. **Gate 必须是硬阻断** — code_fix 精度 31% 就绝对不能 dispatch，不能只 warn
5. **护照必须可版本化** — 模型更新后要重考，旧护照作废
6. **门槛可配置** — 各能力类型的 pass 阈值应该是可调的，不用改代码

---
