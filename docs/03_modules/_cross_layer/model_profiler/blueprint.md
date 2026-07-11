---
module_id: MOD-INF-034
submodule_path: src/zephyr/intelligence/model_profiling
title: "Model Profiler 蓝图 — 模型画像器·LLM能力基线测量"
doc_type: blueprint
status: Active
version: "2.2.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/intelligence/model_profiling/
last_updated: "2026-05-23"
last_verified: "2026-05-14"
generation: 2
functional_domain: intelligence
summary: "LLM 模型画像器——7 维评测 + 任务×模型增量学习 + 智能路由推荐"
tags: [model-profiler, benchmark, performance, latency, throughput, hallucination, drift, task-learning, model-router, routing, ollama, model-discovery, task-model-matrix, composite-score, continuous-learning]
priority: P1
runtime_plane: warm
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: "MOD-INF-009"
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - {target: "MOD-INF-009", at: "§B584/B212/B405", why: "Pipeline——ModelProfiler 是 Pipeline 子组件，复用 ModuleResult.duration_ms/tokens_used"}
  - {target: "MOD-INF-024", at: "§model-router", why: "Budget Enforcer——ModelRouter 消费 benchmark 结果实现性能感知路由"}
  - {target: "MOD-MASTER_BLUEPRINT", at: "§runtime", why: "AutoRuntimeCore——大脑 boot/reconcile/status_panel 全生命周期管理"}
  - {target: "MOD-INF-011", at: "§ollama", why: "Vector Memory——复用 OllamaChat 的 /api/chat 调用模式"}
references:
  - {path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\auto-runtime-core\\blueprint.md", section: "§3", why: "AutoRuntimeCore 集成架构"}
  - {path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_governance\\blueprint.md", section: "§3", why: "MOD-GOVERNANCE 集成契约定义"}
codification_level: L1
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Model Profiler 蓝图 — 模型画像器·LLM能力基线测量

> ⛔ **自动化准入门禁 (AUTOMATION-GATE)**
>
> | 条件 | 当前值 | 门槛 | 状态 |
> |------|--------|------|:----:|
> | 可用 LLM 模型数 | 1 | ≥3 | ❌ |
> | Benchmark 运行次数 | 0 | ≥50 | ❌ |
> | 模型切换频率 | 0次/周 | ≥3次/周 | ❌ |
>
> **为什么现在不自动化**: Model Profiler 需要长时间采样才有统计意义——"这个模型在代码任务上比那个快 20%"这种结论至少需要 50 次对比。现在 LLM 调用都很少，数据不够做分析。只有 1 个模型时，画像没有对比对象。
> **什么时候建**: 当可用 LLM 模型 ≥3，且 Benchmark 运行 ≥50 次，或 Owner 要求模型性能对比选优时。
> **自动化宿主**: CircadianScheduler `hour=6` → `_model_profiler_benchmark()` + FLE `_periodic_checks()` → `_model_performance_check()`

> module_id: MOD-INF-034 | version: 2.1.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/intelligence/model_profiling/ | generation: 2 | construction_progress: partially_implemented

## 概述

ModelProfiler 是 ZephyrAlpha 的 LLM 模型画像器——对所有可用模型进行标准化能力考试，追踪每个任务类型在每个模型上的实际运行表现，逐步优化"每个任务用什么模型最好"的决策矩阵。**v2.2.0新增**：TaskModelMatrix 综合评分公式新增 cost_efficiency 维度（权重0.15），支持下游 LLM 路由成本引擎（交易决策流水线 C-044⑤）的消费。核心闭环：发现→评测→学习→推荐。当前规模 ~10 个模型、7 维度 26 项 benchmark，目标容量 30-50 个模型 + 100 AI 并发写入。上游依赖 PipelineOrchestrator（触发评测）和 Ollama/API（模型调用），下游被 ModelRouter（消费推荐）、AutoRuntimeCore（生命周期管理）和交易决策流水线 C-044⑤（LLM路由成本引擎）消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-034`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §4 | 模块导出 | 已实现 | |
| 2 | `model_discovery.py` | §3.1 #1 | 模型发现 | 已实现 | |
| 3 | `benchmark_suite.py` | §3.1 #2 | 7 维 × 26 项评测用例 | 已实现 | |
| 4 | `profiler.py` | §3.1 #3 | 评测引擎 | 已实现 | |
| 5 | `results_writer.py` | §3.1 #4 | 结果持久化 + 漂移检测 | 已实现 | |
| 6 | `task_model_learner.py` | §3.1 #5 | 任务×模型学习矩阵 | 已实现 | |
| 7 | `cli.py` | §3.1 #7 | CLI 入口 | 已实现 | |
| 8 | `deepseek_v4_chat.py` | §3.1 #6 | DeepSeek V4 Chat 适配器 | 已实现 | |
| `capability_passport.py` | § — | — | 已实现 | | 本模块 |
| `exam_orchestrator.py` | § — | — | 已实现 | | 本模块 |
| `exam_test_cases.py` | § — | — | 已实现 | | 本模块 |
| `provider_data.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 8 文件 | ✅ |
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/intelligence/model_profiling/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ✅ |
| actual_disk_path 与 §11 一致 | 两者均为 src/zephyr/intelligence/model_profiling/ | ✅ |
| __init__.py 导出符号与蓝图 §4 一致 | 读取 __init__.py __all__ | ✅ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | 8 文件全部实现 | — | — |
| v2.0.0 (容量升级) | 基线 8 文件 | G-1~G-7 升级组件 | 待施工 |
| v2.2.0 (成本效率) | 基线 8 文件 | TaskModelMatrix cost_efficiency 维度 | 待施工 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 接入多种 LLM（Ollama 本地 + 远程 API），需要统一的能力基线测量和任务→模型最优映射。当前无标准化评测机制，模型选择依赖静态 spec 或人工判断，无法感知模型版本升级后的性能漂移。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 自动发现所有可用模型 | Ollama + 远程 API 模型 100% 枚举 |
| 2 | 标准化 7 维度评测 | 26 项 benchmark 覆盖 code/semantic/hallucination/latency/quality/reasoning |
| 3 | 增量学习任务×模型映射 | ModelTaskMatrix 样本数 ≥3 后自动切换 learned 策略 |
| 4 | 性能+成本感知路由推荐 | ModelRouter 消费 benchmark 结果，综合 cost×speed×quality×cost_efficiency 排序 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 治理脚本执行系统容量扩容 | 主体容量需求落在 _concurrency.py 和 run_all.py，非本模块职责 |
| 2 | 入职考试细粒度能力认证 | 入职考试（specs/model-capability-exam/）提供 9 能力 × 3 难度认证，与 ModelProfiler 互补 |
| 3 | LLM Gateway 并发队列管理 | 100 AI 并发的 /api/chat 排队是 Gateway 层问题（MOD-INF-011） |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| RTX 3090 24GB VRAM，同时加载 ≤2 个 8B 模型 | 评测必须串行或限制并行度 ≤2 |
| Ollama 本地模型池上限 ~50 个（含量化变体） | discovery 上限设 50，防止 API 响应过大 |
| 远程 API 模型需 API key 注入 | v1.0.0 仅支持 Ollama 本地 benchmark |
| 100 AI 并发写入 TaskModelMatrix | 同步 JSON 写导致锁竞争，需异步写入 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 模型发现 | 枚举 Ollama 本地模型 + Budget Enforcer 注册的远程 API 模型 |
| 2 | 标准化评测 | 7 维度 × 26 项 benchmark，输出延迟 P50/P95/P99、吞吐量、正确率、幻觉率 |
| 3 | 增量学习 | ModelTaskMatrix 追踪任务×模型实际表现，三段式推荐策略 |
| 4 | 漂移检测 | 对比最新 2 次 benchmark 结果，检测 score/latency/throughput 变化 |
| 5 | 结果持久化 | JSONL 格式写入 data/model_profiles/，学习矩阵写入 data/model_learning/ |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | BulkheadExecutor 并发池扩容 | MOD-INF-005 §5.7（_concurrency.py） |
| 2 | 治理脚本全量→增量切换 | MOD-INF-023（incremental_scanner.py） |
| 3 | run_all.py 全量扫描性能 | scripts/governance/run_all.py |
| 4 | ShardRouter 模块分片 | _concurrency.py §ShardRouter |
| 5 | 100 AI 进程级隔离 | L0 ProcessLock（_concurrency.py） |
| 6 | LLM Gateway 并发管理 | MOD-INF-011（OllamaChat） |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | ModelDiscovery | 枚举 Ollama + 远程 API 模型 | Ollama HTTP API, BudgetEnforcer config | 同步 HTTP 调用 |
| 2 | BenchmarkSuite | 7 维 × 26 项评测用例定义 | — | 静态数据 |
| 3 | ModelProfiler | 评测引擎，调度 benchmark 执行 | ModelDiscovery, BenchmarkSuite | 同步调用 |
| 4 | ResultsWriter | 结果持久化 + 漂移检测 | ModelProfile 数据 | 同步文件写入 |
| 5 | TaskModelMatrix | 任务×模型学习矩阵 | ModuleResult 数据 | 同步内存 + 异步磁盘 |
| 6 | DeepSeekV4Chat | DeepSeek V4 专用 Chat 适配器 | Ollama /api/chat | 同步 HTTP |
| 7 | CLI | 命令行入口 | 所有组件 | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | Ollama /api/tags | ModelDiscovery 枚举模型 | ModelProfiler | DiscoveredModel |
| 2 | ModelProfiler | 运行 benchmark 评测 | ResultsWriter | ModelProfile |
| 3 | ResultsWriter | 持久化 + 漂移检测 | data/model_profiles/*.jsonl | JSONL |
| 4 | PipelineOrchestrator | ModuleResult 数据 | TaskModelMatrix.record() | (task_type, model, duration, tokens) |
| 5 | TaskModelMatrix | 增量学习 + 推荐计算 | ModelRouter | TaskRecommendation |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| idle | PipelineOrchestrator 启动 / CLI benchmark | profiling | Ollama 可用 |
| profiling | 全部 benchmark case 完成 | results_ready | — |
| results_ready | write_benchmark_results() | persisted | 磁盘写入成功 |
| persisted | detect_drift() 发现漂移 | drift_detected | score_decline > 0.10 或 latency_increase > 50% |
| drift_detected | 人工确认 / 自动重测 | profiling | — |

---

## §4 接口契约

### 4.1 公共 API

```python
class ModelDiscovery:
    """模型发现器——枚举 Ollama + 远程 API 模型"""
    def discover_all() -> list[DiscoveredModel]: ...
    def ollama_available() -> bool: ...

class ModelProfiler:
    """评测引擎——调度 benchmark 执行"""
    def profile_all() -> list[ModelProfile]: ...
    def profile_ollama_only() -> list[ModelProfile]: ...
    def quick_profile(model_name: str) -> ModelProfile: ...
    def print_ranking(results: list[ModelProfile]) -> None: ...

class ModelTaskMatrix:
    """任务×模型学习矩阵"""
    def record(task_type: str, model: str, duration_ms: float, tokens: int, confidence: float) -> None: ...
    def recommend(task_type: str) -> TaskRecommendation: ...
    def summary() -> str: ...

class DeepSeekV4Chat:
    """DeepSeek V4 专用 Chat 适配器"""
    def chat(model: str, messages: list, **kwargs) -> dict: ...
```

### 4.2 数据模型

```python
class DiscoveredModel(BaseModel):
    name: str = Field(..., description="模型名，如 qwen3:8b")
    source: str = Field(..., description="ollama | remote_api")
    provider: str = Field(default="", description="提供商")
    size_bytes: int = Field(default=0, description="模型文件大小")
    parameter_size: str = Field(default="", description="参数量，如 8B")
    quantization_level: str = Field(default="", description="量化等级，如 Q4_K_M")
    family: str = Field(default="", description="模型家族")
    available: bool = Field(default=True, description="是否可用")
    metadata: dict = Field(default_factory=dict, description="扩展元数据")

class ModelProfile(BaseModel):
    model_name: str = Field(..., description="模型名")
    average_score: float = Field(..., description="加权综合评分")
    latency_p50_ms: float = Field(..., description="中位延迟")
    latency_p95_ms: float = Field(..., description="95 分位延迟")
    latency_p99_ms: float = Field(..., description="99 分位延迟")
    throughput_tokens_per_sec: float = Field(..., description="综合吞吐")
    hallucination_rate: float = Field(..., description="幻觉率 0-1")
    code_validity_rate: float = Field(default=0.0, description="代码质量率")
    json_validity_rate: float = Field(default=0.0, description="JSON 合法性率")
    case_results: list[CaseResult] = Field(default_factory=list, description="逐题结果")

class TaskRecommendation(BaseModel):
    task_type: str = Field(..., description="任务类型")
    best_model: str = Field(..., description="推荐模型")
    composite_score: float = Field(..., description="综合评分")
    source: str = Field(..., description="learned | benchmark_baseline | static_spec")
    sample_count: int = Field(default=0, description="样本数")

class BenchmarkCase(BaseModel):
    case_id: str = Field(..., description="用例 ID")
    category: str = Field(..., description="维度")
    subcategory: str = Field(..., description="子维度")
    prompt: str = Field(..., description="输入提示")
    expected_patterns: list[str] = Field(default_factory=list, description="正则匹配")
    forbidden_patterns: list[str] = Field(default_factory=list, description="越界检测")
    expected_output_type: str = Field(..., description="code|text|json|classification")
    weight: float = Field(default=1.0, description="权重")
    reference_answer: str = Field(default="", description="参考答案")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `profile_all()` | — | — | Ollama 可用或远程 API 已配置 |
| `quick_profile()` | `model_name` | ✅ | 必须是已发现模型名 |
| `record()` | `task_type`, `model`, `duration_ms`, `tokens`, `confidence` | ✅ | duration_ms > 0, 0 ≤ confidence ≤ 1 |
| `recommend()` | `task_type` | ✅ | 非空字符串 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `discover_all()` | `list[DiscoveredModel]` | Ollama 不可用 → 仅返回远程 API 模型 |
| `profile_all()` | `list[ModelProfile]` | 单模型超时 → 标记 FAIL，继续下一个 |
| `quick_profile()` | `ModelProfile` | 模型不可用 → `ModelProfile(average_score=0.0)` |
| `record()` | `None` | JSON 写入失败 → 静默跳过，log warning |
| `recommend()` | `TaskRecommendation` | 无数据 → source="static_spec" |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 benchmark 维度 | ✅ 向后兼容 | 不影响已有评测结果 |
| 修改评分公式权重 | ⚠️ 需通知 | 影响排名，消费者需重新加载 |
| 新增 TaskRecommendation 字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 修改 recommend() 返回结构 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 修改 discovery skip_patterns | ✅ 向后兼容 | 不破坏已有逻辑 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 使用 /api/chat 而非 /api/generate | /api/chat |
| 2 | 跳过 embedding 模型 | bge/nomic/mxbai 等前缀 |
| 3 | 评测温度 | temperature=0.0 |
| 4 | 最大输出 token 数 | num_predict=max(tokens, 256) |
| 5 | thinking_models 处理 | message.thinking if message.content is empty |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模型数量 | ~10 | 30-50 | max_ollama_models=10 | ❌ | 上调至 50（G-1） |
| 评测时间 | 2-5 min/model | 30 models × 5 min = 150 min | 串行评测 | ❌ | 并行评测 --parallel 2（G-2） |
| TaskModelMatrix 写入 | ~1 次/min | 50-100 次/s（100 AI 并发） | 同步 JSON 写 | ❌ | 异步写入 + 写合并（G-3） |
| 样本窗口 | 200/(task,model) | 200/(task,model) | — | ✅ | 可选按 module_id 分区（G-4） |
| 存储空间 | < 1MB/1000 records | < 50MB | — | ✅ | — |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。

本蓝图不涉及现有文件废弃或迁移。

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Ollama 不可用 | `ModelDiscovery.ollama_available() → False` | 跳过 Ollama 模型，仅返回远程 API 模型 | 本地模型评测跳过 |
| 2 | 单模型 benchmark 超时 | 单 case > 60s | 标记该 case 为 FAIL，继续下一个 | 该模型评分偏低 |
| 3 | 学习矩阵 JSON 损坏 | JSON 反序列化异常 | 丢弃损坏文件，从空矩阵重新开始 | 历史学习数据丢失，下次 benchmark 自动播种 |
| 4 | ModelRouter 无 benchmark 数据 | `router.has_benchmarks == False` | 回退到 cost-only 排序 | 路由不感知性能 |
| 5 | 磁盘写入失败 | PermissionError / IOError | 静默跳过，log warning | 本次结果不持久化，内存路由决策不受影响 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 远程 API key 泄露 | 高 | API key 通过 BudgetEnforcer 配置注入，不硬编码 | Grep 项目无明文 key |
| 2 | 幻觉检测数据集被模型"记忆" | 低 | 定期轮换测试用例（rotate exam_test_cases 规划） | 版本化测试用例 |
| 3 | benchmark 期间资源占用 | 低 | 后台线程执行，不阻塞主流程 | PipelineOrchestrator 非阻塞验证 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | ModelDiscovery, TaskModelMatrix, ResultsWriter | discover_all(), record(), recommend(), detect_drift() | 覆盖率 ≥ 80% |
| 2 | 集成测试 | PipelineOrchestrator → ModelProfiler → ModelRouter | 完整评测→持久化→路由消费链路 | 端到端通过 |
| 3 | CLI 测试 | discover/quick/benchmark/best/drift/history 命令 | 每个命令 exit 0 | 全部通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-009 | 必须 | Pipeline ModuleResult 数据 | ≥1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-INF-024 | 必须 | ModelRouter 消费 benchmark 结果 | ≥1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-MASTER_BLUEPRINT | 必须 | AutoRuntimeCore 生命周期管理 | ≥1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` |
| MOD-INF-011 | 可选 | OllamaChat /api/chat 调用模式 | ≥1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\vector_memory\blueprint.md` |
| 交易决策流水线 C-044⑤ | 被依赖 | 消费 TaskModelMatrix cost_efficiency 做LLM路由决策 | — | d:\\临时工作区\\交易决策流水线设计.md |

### 10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。不一致 = 漂移。
> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> 机器 SSoT：[cross-module-dependency-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml)

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-034` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| model_discovery.py | profiler.py | discovered models 是 profiling 的前置条件 | 检查 discover_all() 返回非空 |
| benchmark_suite.py | profiler.py | benchmark cases 是 profiling 的前置条件 | 检查 ALL_BENCHMARK_CASES 非空 |
| profiler.py | results_writer.py | profile results 是持久化的前置条件 | 检查 ModelProfile 列表非空 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| model_discovery.py | profiler.py | DiscoveredModel 列表 | 函数调用 |
| profiler.py | results_writer.py | ModelProfile 列表 | 函数调用 |
| results_writer.py | data/model_profiles/ | JSONL benchmark 结果 | 文件写入 |
| PipelineOrchestrator | task_model_learner.py | ModuleResult (task_type, model, duration, tokens) | 函数调用 |
| task_model_learner.py | ModelRouter | TaskRecommendation | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 模块有 4 个外部依赖 + 内部依赖图 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖，需验证蓝图与 registry 一致 |
| 3 | 临时时态内容自动清理 | 否 | 无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | construction_progress = partially_implemented |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | asset-inventory/dependency.py | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 3 | 施工步骤完成度自动检测 | pytest + ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\model_profiler\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\` | Python 源码（8 文件） |
| 测试代码 | `D:\ZephyrAlpha\tests\test_model_profiler\` | 测试用例 |
| 评测结果 | `D:\ZephyrAlpha\data\model_profiles\` | JSONL 格式 benchmark 结果 |
| 学习矩阵 | `D:\ZephyrAlpha\data\model_learning\` | JSON 格式 TaskModelMatrix |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| PipelineOrchestrator | 新增接口 | `_start_auto_profile()`, `_start_periodic_profile()`, `run_model_benchmark()` | benchmark 后路由数据可用 |
| ModelRouter | 修改现有接口 | `load_benchmark_profiles()`, `load_benchmark_from_disk()`, `route()` perf-aware | 路由决策包含 performance_score |
| AutoRuntimeCore | 新增接口 | `boot()._benchmark_and_learn()`, `reconcile()._learn_from_completed_tasks()`, `status_panel()` | 大脑面板显示推荐矩阵 |

### 12.1 域契约锚点

> 权威定义见 [MOD-GOVERNANCE blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md) §3。

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-034-01 | 治理域 | benchmark 结果 → ModelRouter | MOD-INF-024 | 修改输出格式必须同步更新 ModelRouter |
| G-CT-034-02 | 治理域 | ModuleResult → 学习矩阵 | MOD-INF-009 | 修改 record() 签名必须同步更新 Pipeline |
| G-CT-034-03 | 治理域 | 大脑 boot/reconcile 触发 | MOD-MASTER_BLUEPRINT | 修改集成点必须同步更新 AutoRuntimeCore |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 更新 version/generation/last_updated | 蓝图升级 |
| 2 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 更新版本号 | 文档版本追踪 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 确认 MOD-INF-034 依赖关系 | 依赖变更 |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——设计决策带来的已知代价。
> 正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 远程 API 模型未 benchmark | 高 | 中 | v1.1.0 加入 API key injection 后补齐 | 风险 |
| 2 | 模型版本升级后旧 benchmark 失效 | 中 | 中 | v1.1.0 自动检测模型 digest 变化触发重测（G-6） | 风险 |
| 3 | 幻觉检测数据集被模型"记忆" | 低 | 低 | 定期轮换测试用例 | 风险 |
| 4 | 冷启动无 benchmark 数据 | 中 | 低 | auto_profile_on_startup=True + ModelRouter cost-only 回退 | 风险 |
| 5 | 学习偏差：热路径样本远多于冷路径 | 中 | 低 | 基准线兜底——冷路径回退到 benchmark baseline | 风险 |
| 6 | benchmark 执行耗时（2-5 min/model × 30 models = 60-150 min 串行） | — | 中 | --parallel 2 并行评测（G-2） | 负面后果 |
| 7 | TaskModelMatrix 写入在 100 AI 并发下需异步改造 | — | 中 | AsyncWriteQueue + debounce 500ms（G-3） | 负面后果 |
| 8 | 评测结果依赖 Ollama 可用性 | — | 中 | Ollama 不可用时跳过本地模型，仅返回远程 API 模型 | 负面后果 |
| 9 | cost_efficiency 维度依赖外部 API 定价数据 | 中 | 中 | API 定价变化时需重算 cost_efficiency，下游路由引擎应缓存定价并定期刷新 | 风险 |
| 10 | 本地模型成本受 GPU 占用状态影响（机会成本） | 中 | 中 | TaskModelMatrix 的 cost_efficiency 仅记录直接成本，机会成本由下游 LLM 路由成本引擎实时计算 | 负面后果 |

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
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | 100 AI 并发下 TaskModelMatrix 写入竞争 |
| 目标 generation | 2 — 本次施工将蓝图从 generation 1 升级到 generation 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-009 Pipeline 已就绪 | hard | ✅ | ✅ |
| 2 | Ollama 服务可用 | soft | ✅ | ✅ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `ruff` lint 通过
> 4. 以上 3 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：Phase 1 — 配置调整 + 异步写入 + digest 重测

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 容量估算 G-1/G-3/G-6 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\` |
| 验收标准 | max_ollama_models=50；AsyncWriteQueue 500ms 合并；digest 变化自动重测 |
| 验证命令 | `python -m pytest tests/test_model_profiler/ -k "async_write or digest" -v` |
| G7 检查项 | 上游 ModuleResult 签名未变；下游 ModelRouter 加载兼容 |

**修改文件清单**：

| module_id | 文件名 | 完整绝对路径 |
|-----------|--------|------------|
| MOD-INF-034 | profiler.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\profiler.py` |
| MOD-INF-034 | task_model_learner.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\task_model_learner.py` |
| MOD-INF-034 | model_discovery.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\model_discovery.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| profiler.py | 增加 check_and_retrigger() digest 变化检测 | digest 快照对比逻辑；增量 benchmark 触发 |
| task_model_learner.py | 增加 AsyncWriteQueue 异步写入 | WriteBuffer 内存缓冲；500ms debounce 合并；shutdown() flush |
| model_discovery.py | max_ollama_models 上调至 50 | 配置值修改；上限理由注释 |

#### 步骤 2：Phase 2 — 并行评测 + GPU 显存感知

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 容量估算 G-2/G-5 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\` |
| 验收标准 | --parallel N 支持（默认 N=2，上限 4）；ProfileQueue 显存检查 |
| 验证命令 | `python -m zephyr.model_profiler.cli benchmark --parallel 2` |
| G7 检查项 | 并行评测不超显存；单模型超时不阻塞其他模型 |

**修改/新建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-034 | profiler.py | 修改 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\profiler.py` |
| MOD-INF-034 | profile_queue.py | 新建 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\profile_queue.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| profiler.py | ThreadPoolExecutor 包装并行评测 | max_workers 参数；模型间隔离 |
| profile_queue.py | ProfileQueue 等待队列 + 显存检查 | Ollama 当前加载模型数检查；排队等待逻辑 |

#### 步骤 3：Phase 3 — 可观测性 + 精细化

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 容量估算 G-4/G-7 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\` |
| 验收标准 | TaskModelMatrix 可选 module_id 维度；record() 路径调用计数 + 延迟直方图 |
| 验证命令 | `python -m pytest tests/test_model_profiler/ -k "module_id_partition or metrics" -v` |
| G7 检查项 | 可选维度不破坏已有 API；metrics 不影响主流程性能 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | AsyncWriteQueue 数据丢失 | 恢复同步写入；从 JSONL benchmark 结果重新播种矩阵 |
| 2 | 并行评测显存溢出 | 回退 --parallel 1（串行）；降低 num_predict |
| 3 | metrics 影响主流程 | 移除 metrics 埋点；恢复原始 record() 路径 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | profiler.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\profiler.py` | ☐ | ☐ | ☐ |
| 2 | task_model_learner.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\task_model_learner.py` | ☐ | ☐ | ☐ |
| 3 | model_discovery.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\model_discovery.py` | ☐ | ☐ | ☐ |
| 4 | profile_queue.py | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\profile_queue.py` | ☐ | ☐ | ☐ |

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
| 模型发现上限 | max_ollama_models: 10 | model_discovery.py 配置 |
| 评测并发 | 串行 | profiler.py 执行模式 |
| TaskModelMatrix 写入 | 同步 JSON | task_model_learner.py _save() |
| 重测触发 | 手动 CLI | 无自动检测 |
| GPU 调度 | 无感知 | 无显存检查 |
| 可观测性 | 无 | 无 metrics 埋点 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-034-01 | 模型发现上限 10 | max_ollama_models → 50 | 模型数 > 8 |
| GAP-034-02 | 串行评测耗时 150 min | --parallel 2 并行评测 | 评测时间 > 60 min |
| GAP-034-03 | 同步 JSON 写锁竞争 | AsyncWriteQueue + debounce 500ms | 并发 record() > 10/s |
| GAP-034-04 | 无 module_id 维度 | 可选 module_id 分区 | 同 task_type 多模块触发 |
| GAP-034-05 | 无 GPU 显存感知 | ProfileQueue + 显存检查 | 并行评测 OOM |
| GAP-034-06 | 无自动重测 | digest 快照 + 增量重测 | 模型版本变更 |
| GAP-034-07 | 无桥接监控 | record() metrics 埋点 | 需定位"脚本慢因模型慢" |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 发现→评测→学习→推荐闭环 | ✅ |
| v2.0.0 | 2 | 容量升级 | G-1~G-7 七项扩容 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-034-01 | 模型发现上限 | P1 | v2.0.0 Phase 1 | 待施工 |
| GAP-034-03 | 异步写入 | P1 | v2.0.0 Phase 1 | 待施工 |
| GAP-034-06 | digest 自动重测 | P1 | v2.0.0 Phase 1 | 待施工 |
| GAP-034-02 | 并行评测 | P2 | v2.0.0 Phase 2 | 待施工 |
| GAP-034-05 | GPU 显存感知 | P2 | v2.0.0 Phase 2 | 待施工 |
| GAP-034-04 | module_id 分区 | P3 | v2.0.0 Phase 3 | 待施工 |
| GAP-034-07 | 桥接监控 | P3 | v2.0.0 Phase 3 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| AsyncWriteQueue | GAP-034-03 | task_model_learner.py | Phase 1 | 待施工 |
| DigestChecker | GAP-034-06 | profiler.py | Phase 1 | 待施工 |
| ParallelProfiler | GAP-034-02 | profiler.py | Phase 2 | 待施工 |
| ProfileQueue | GAP-034-05 | profile_queue.py | Phase 2 | 待施工 |
| ModuleIdPartition | GAP-034-04 | task_model_learner.py | Phase 3 | 待施工 |
| MetricsInstrumentation | GAP-034-07 | task_model_learner.py | Phase 3 | 待施工 |

---

## §18 决策记录

> 记录蓝图中的关键设计决策。与变更记录不同——变更记录记"改了什么"，决策记录记"为什么这样设计"。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。
> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-034-01 | 归属 Pipeline 子组件 | A:独立顶层 / B:Pipeline子组件 | B | 复用 ModuleResult 数据，减少跨层通信开销 | 2026-05-08 |
| 2 | D-034-02 | 三段式推荐策略 | A:纯静态 / B:纯学习 / C:三段退避 | C | 从静态到动态渐进收敛，避免冷启动无推荐 | 2026-05-08 |
| 3 | D-034-03 | 评分公式权重 | A:quality优先 / B:speed优先 / B:speed×0.40+quality×0.35+consistency×0.25 | B | 用户体感最直接的是速度，质量次之，稳定性作 tie-breaker | 2026-05-08 |
| 4 | D-034-04 | 跳过 embedding 模型 | A:全量评测 / B:跳过embedding | B | embedding 模型不支持 /api/chat，benchmark 无意义 | 2026-05-08 |
| 5 | D-034-05 | 使用 /api/chat | A:/api/generate / B:/api/chat | B | reasoning 模型通过 chat API 正确返回 thinking 字段 | 2026-05-08 |
| 6 | D-034-06 | 评测温度 temperature=0.0 | A:temperature=0.7 / B:temperature=0.0 | B | 零温度确保可复现，评测需要确定性输出 | 2026-05-08 |
| 7 | D-034-07 | num_predict=max(tokens, 256) | A:固定256 / B:max(tokens,256) | B | 给 reasoning 模型留足 thinking 空间，避免截断 | 2026-05-08 |
| 8 | D-034-08 | thinking_models 处理逻辑 | A:忽略thinking / B:提取thinking | B | reasoning 模型 content 为空时 thinking 包含实际回答 | 2026-05-08 |
| 9 | D-034-09 | 综合评分公式新增 cost_efficiency 维度 | A:不新增(纯speed+quality+consistency) B:新增cost_efficiency×0.15(调整其他权重) | B | 交易决策流水线需要成本感知路由，cost_efficiency 是独立维度不应被 speed/quality 吞没；权重0.15确保成本是决策因子但不压倒质量 | 2026-05-23 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径的基准在哪 | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 每次新 session 是零记忆 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | 蓝图是施工依据，不是讨论记录 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范 | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界在哪 | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | AI 不知道系统能容纳多少 | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | AI 不知道旧东西怎么处理 | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令 | 执行漂移——AI 自行决定 |
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
| ModelProfiler 容量升级（G-1~G-7） | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| ModelProfiler 中"入职考试"独立子系统 | **拆分**（已有独立蓝图 MOD-INF-035） | 独立 module_id + 独立评测体系 + 互补非替代 |
| ModelProfiler 中"DeepSeek V4 Chat 适配器" | **原地** | 适配器是评测引擎的子组件，服务对象和依赖关系与主体一致 |

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
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | 入职考试 | `D:\ZephyrAlpha\specs\model-capability-exam\` | 模型能力评测 | 入职考试是 9 能力 × 3 难度细粒度认证，ModelProfiler 是 7 维度标准化 benchmark + 任务学习，互补非替代 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | model-profiler/ | `D:\ZephyrAlpha\src\zephyr\intelligence\model_profiling\` | 修改 | Phase 1-3 代码变更 |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\model_profiler\blueprint.md` | 修改 | 本文件 |
| 3 | 评测结果目录 | `D:\ZephyrAlpha\data\model_profiles\` | 读取 | benchmark 结果持久化 |
| 4 | 学习矩阵目录 | `D:\ZephyrAlpha\data\model_learning\` | 读取 | TaskModelMatrix 持久化 |

---

## 蓝图特有章节

### 蓝图特有：7 维度 Benchmark 用例定义

> 来源：v1.0.0 原始蓝图 §2.3
> 仅本蓝图需要：7 维度 × 26 项用例是 ModelProfiler 独有的评测体系
> 不可砍理由：砍掉后 AI 无法知道 benchmark 覆盖了哪些维度

| 维度 | 题数 | 覆盖范围 |
|------|:---:|---------|
| code_generation | 5 | 函数实现、数据结构、异步代码、异常处理、算法 |
| code_fix | 3 | Bug 修复、重构、功能添加 |
| semantic | 4 | 情感分析、NLI、摘要、分类 |
| hallucination | 5 | API 编造、事实检查、参数编造、已知结果、诚实拒绝 |
| latency | 3 | 简单响应、JSON 输出、短代码（精确测速） |
| quality | 3 | JSON 格式、Markdown 格式、指令遵循 |
| reasoning | 3 | 演绎推理、数学、代码追踪 |

### 蓝图特有：TaskModelMatrix 推荐策略

> 来源：v1.0.0 原始蓝图 §2.6
> 仅本蓝图需要：三段式推荐策略是 ModelProfiler 独有的学习→推荐机制
> 不可砍理由：砍掉后 AI 无法理解推荐策略的退避逻辑

```
recommend(task_type):
  if sample_count >= 3: source = "learned"
  elif benchmark_baseline: source = "benchmark_baseline"
  else: source = "static_spec"

composite_formula:
  speed_score = min(throughput / 200, 1.0)
  quality_score = avg_confidence
  consistency_score = 1.0 - stddev(duration) / max(avg(duration), 1.0)
  cost_efficiency = 1.0 - (actual_cost / max_acceptable_cost)
  composite = speed × 0.30 + quality × 0.35 + consistency × 0.20 + cost_efficiency × 0.15

cost_efficiency_source:
  local_cost = (electricity_cost + depreciation_cost) × duration_hours + opportunity_cost
  api_cost = input_tokens × input_price + output_tokens × output_price
  actual_cost = min(local_cost, api_cost)
  max_acceptable_cost = max(local_cost, api_cost) × 1.5
  note: opportunity_cost由下游LLM路由成本引擎实时计算（GPU空闲时=0，GPU忙碌时=∞），此处cost_efficiency仅记录直接成本
```

### 蓝图特有：CLI 命令参考

> 来源：v1.0.0 原始蓝图 §2.7
> 仅本蓝图需要：CLI 是 ModelProfiler 的唯一交互入口
> 不可砍理由：砍掉后 AI 不知道如何触发评测

```bash
python -m zephyr.model_profiler.cli discover     # 列出所有可用模型
python -m zephyr.model_profiler.cli quick <model> # 快速测试单个模型
python -m zephyr.model_profiler.cli benchmark     # 全量 benchmark
python -m zephyr.model_profiler.cli best          # 显示最佳模型
python -m zephyr.model_profiler.cli drift <model> # 漂移检测
python -m zephyr.model_profiler.cli history       # 查看历史记录
```

### 蓝图特有：模块导出清单

> 来源：v1.0.0 原始蓝图 附录A
> 仅本蓝图需要：导出符号是 ModelProfiler 对外 API 契约的一部分
> 不可砍理由：砍掉后下游模块不知道可导入哪些符号

```python
ALL_BENCHMARK_CASES, BenchmarkCase, CaseResult, CATEGORY_MAP,
DiscoveredModel, ModelDiscovery, ModelProfile, ModelProfiler,
ModelTaskEntry, ModelTaskMatrix, TaskRecommendation,
detect_drift, load_benchmark_history, to_model_benchmark_result,
write_benchmark_results, DeepSeekV4Chat, DEFAULT_OLLAMA_URL,
MAX_OLLAMA_MODELS, SKIP_MODEL_PATTERNS
```

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| ModelProfiler 架构设计 | **本文档 §1-§10** | v1.0.0 原始蓝图（已取代） |
| ModelProfiler 施工步骤 | **本文档 §16** | — |
| ModelProfiler 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-024 ModelRouter | §4 接口契约、§10 依赖关系 |
| Tier 1 | MOD-INF-009 PipelineOrchestrator | §4 接口契约、§12 集成点 |
| Tier 2 | MOD-MASTER_BLUEPRINT AutoRuntimeCore | §12 集成点 |
| Tier 3 | `src/zephyr/intelligence/model_profiling/*.py` | §4 数据模型、§11 产出物路径 |

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

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-23 | 2.2.0 | 新增 cost_efficiency 维度：TaskModelMatrix 综合评分公式从 speed×0.40+quality×0.35+consistency×0.25 调整为 speed×0.30+quality×0.35+consistency×0.20+cost_efficiency×0.15；§1.2 目标#4 更新为"性能+成本感知路由推荐"；§10.1 新增交易决策流水线 C-044⑤ 被依赖声明；§14 新增风险#9/#10；§18 新增决策 D-034-09 |
| 2026-05-14 | 2.1.0 | v3.5 模板对齐升级：§0 前移至概述之后；§7 备选方案删除（信息由§18决策记录覆盖）；§15 后果删除（正面与§1重复，负面合并到§14风险+增加"类型"列）；§0.1 代码文件清单新增"存在性"列（已实现/已阻塞/已废弃）；§5.1 技术约束去掉"原因"列（原因属决策过程，记录在§18）；§10 拆为§10.1依赖声明+§10.2依赖图对齐声明+§10.3内部依赖图+§10.4自动化规格；铁律新增#13~#15；新增蓝图拆分判定标准段落；施工声明标注时态属性；§18 决策记录新增 D-034-06~D-034-08（承接§5.1 原因列） |
| 2026-05-14 | 2.0.0 | v3.3 模板对齐升级：H1 格式更新；新增概述段+标准锚点；frontmatter 补全（generation/functional_domain/parent_module/references/codification_level/last_verified）；章节重排（概述→§1-§15→§0→§16-§18→规则参考）；补缺 §1.3/§1.4/§2.2/§3.2/§3.3/§4.3-§4.6/§5.3/§7/§8/§9/§12.1/§13/§15/§0/§16/§17/§18；v1.1.0 升级规划整合至 §17；绝对路径统一 D:\；construction_progress 与代码一致（8 文件）；actual_disk_path 与 §11 一致；蓝图特有内容保留（benchmark 用例/推荐策略/CLI/导出清单）；ASCII 图砍削（信息已在表格中） |
| 2026-05-12 | 1.0.0 | v1.0.0 初始蓝图——实现后追认 |
