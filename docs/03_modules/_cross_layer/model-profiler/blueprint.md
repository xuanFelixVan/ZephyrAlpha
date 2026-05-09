---
module_id: "MOD-INF-034"
title: "模型性能检测与任务学习引擎蓝图 — 7 维评测 + 任务×模型增量学习 + 智能路由决策"
doc_type: blueprint
status: Active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
valid_from: "2026-05-08"
ttl: permanent
construction_progress: phase_1_complete
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha 模型性能检测与任务学习引擎蓝图 v1.0.0——实现后追认蓝图。提供三层能力：① 模型发现——自动枚举所有 Ollama 本地模型和注册远程 API 模型；② 性能基准测试——7 维度 × 26 项标准化 benchmark，输出延迟 P50/P95/P99、吞吐量、正确率、幻觉率、代码质量等指标；③ 增量学习——ModelTaskMatrix 追踪每个任务类型在每个模型上的实际运行表现，逐步收敛到最优任务→模型映射。集成点覆盖 PipelineOrchestrator（触发策略）、BudgetEnforcer/ModelRouter（消费推荐）、AutoRuntimeCore 大脑（全生命周期管理）。与入职考试（specs/model-capability-exam/）形成互补：ModelProfiler 提供基础设施层模型评测 + 任务路由优化，入职考试提供细粒度能力认证（9 种能力 × 3 级难度）。"
tags: [model-profiler, benchmark, performance, latency, throughput, hallucination, drift, task-learning, model-router, routing, ollama, model-discovery, task-model-matrix, composite-score, continuous-learning]
priority: P1
depends_on:
  - {target: "MOD-INF-009", at: "§B584/B212/B405", why: "Pipeline——ModelProfiler 是 Pipeline 的子组件，复用 ModuleResult.duration_ms/tokens_used 数据"}
  - {target: "MOD-INF-024", at: "§model-router", why: "Budget Enforcer——ModelRouter 消费 benchmark 结果实现性能感知路由"}
  - {target: "MOD-MASTER-001", at: "§runtime", why: "AutoRuntimeCore——大脑 boot/reconcile/status_panel 全生命周期管理"}
  - {target: "MOD-INF-011", at: "§ollama", why: "Vector Memory——复用 OllamaChat 的 /api/chat 调用模式"}
---

## DOM-GOV-001 集成契约锚点

> 权威定义见 [`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-034-01 | 数据提供方（benchmark 结果 → ModelRouter） | MOD-INF-024 |
| G-CT-034-02 | 消费者（ModuleResult → 学习矩阵） | MOD-INF-009 |
| G-CT-034-03 | 被调用方（大脑 boot/reconcile 触发） | MOD-MASTER-001 |

# 模型性能检测与任务学习引擎蓝图 — 7 维评测 + 增量学习 + 智能路由

> **module_id**: MOD-INF-034 | **version**: 1.0.0 | **status**: Active | **layer**: cross_layer

> **实现后追认蓝图**：本蓝图对已实现并验证的功能进行架构文档化，记录架构决策、集成边界、API 契约和演进方向。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-034 |
| 代码落位 | `src/zephyr/pipeline/model_profiler/` |
| 施工落盘确认 | 代码嵌入 `src/zephyr/pipeline/model_profiler/` 子目录（已存在，含 `__init__.py`、`profiler.py`、`model_discovery.py`、`benchmark_suite.py`、`results_writer.py`、`task_model_learner.py`、`cli.py`、`exam_orchestrator.py`、`exam_test_cases.py`、`capability_passport.py`、`deepseek_v4_chat.py` 共 11 文件）。无独立顶层代码目录。 |
| 运行时平面 | Hot memory（benchmark 期间旋转模型执行），Warm disk（结果持久化到 JSONL + 学习矩阵到 JSON） |
| 核心职责 | 发现 → 评测 → 学习 → 推荐 四阶段闭环：自动发现所有可用模型，运行标准化 benchmark，增量学习任务×模型最优映射，向路由系统输出推荐决策 |

### 1.2 核心职能（一句话）

**ModelProfiler 是系统的质检部门 + 猎头顾问**——对所有可用模型进行标准化能力考试，追踪每个任务类型在每个模型上的实际表现，逐步优化出"每个任务用什么模型最好"的决策矩阵。它不是一次性评测，而是持续学习、持续收敛的系统。

### 1.3 与其他模块的关系

```
                    ┌──────────────────────┐
                    │ 入职考试 (specs/)      │
                    │ 5 轴 × 9 能力 × 3 难度│
                    │ "qwen3 能做 code_fix?" │
                    └──────────┬───────────┘
                               │ 可复用基础设施
                               ▼
┌──────────────────────────────────────────────────────────┐
│  ModelProfiler + ModelTaskMatrix (MOD-INF-034)            │
│  ┌───────────────┐  ┌─────────────┐  ┌────────────────┐ │
│  │ ModelDiscovery │  │ Profiler    │  │ TaskLearner    │ │
│  │ 枚举 Ollama +  │→│ 7 维 × 26 题│→│ 任务×模型矩阵  │ │
│  │ 远程 API 模型  │  │ benchmark   │  │ 增量学习+推荐  │ │
│  └───────────────┘  └──────┬──────┘  └───────┬────────┘ │
│                            │                  │          │
└────────────────────────────┼──────────────────┼──────────┘
                             │                  │
              ┌──────────────▼──┐  ┌────────────▼─────────┐
              │ ModelRouter     │  │ AutoRuntimeCore 大脑  │
              │ (MOD-INF-024)   │  │ (MOD-MASTER-001)      │
              │ 性能感知路由     │  │ boot/reconcile/panel │
              └─────────────────┘  └──────────────────────┘
```

### 1.4 v1.0.0 设计决策

| 决策 ID | 内容 | 理由 |
|---------|------|------|
| D-034-01 | 归属 Pipeline 子组件，不独立为顶层模块 | 复用 ModuleResult 数据，减少跨层通信开销 |
| D-034-02 | 三段式推荐策略：learned(≥3样本) > baseline(benchmark) > static(模块spec) | 从静态到动态渐进收敛，避免冷启动无推荐 |
| D-034-03 | 评分公式：speed×0.40 + quality×0.35 + consistency×0.25 | 优先吞吐量（用户体感最直接），质量次之，稳定性作为 tie-breaker |
| D-034-04 | 跳过 embedding 模型（bge/nomic/mxbai 等） | 这些模型不支持 /api/chat，benchmark 无意义 |
| D-034-05 | 使用 /api/chat 而非 /api/generate | Qwen3/DeepSeek-R1 等 reasoning 模型通过 chat API 正确返回内容（含 thinking 字段处理） |

---

## 2. 核心架构

### 2.1 组件全景

```
src/zephyr/pipeline/model_profiler/
├── __init__.py              # 模块导出
├── model_discovery.py       # §2.2 模型发现
├── benchmark_suite.py       # §2.3 评测用例
├── profiler.py              # §2.4 评测引擎
├── results_writer.py        # §2.5 结果持久化 + 漂移
├── task_model_learner.py    # §2.6 任务×模型学习
├── cli.py                   # §2.7 CLI 入口
├── exam_orchestrator.py     # 入职考试编排器（外部 agent 生成，互补使用）
├── exam_test_cases.py       # 入职考试 27 题（外部 agent 生成）
├── capability_passport.py   # 能力护照数据模型（外部 agent 生成）
└── deepseek_v4_chat.py      # DeepSeek V4 专用 Chat 适配器
```

### 2.2 模型发现 —— model_discovery.py

通过 Ollama HTTP API `/api/tags` 枚举所有本地模型，同时合并 Budget Enforcer 中注册的外部 API 模型。

```yaml
discovery:
  ollama_endpoint: "http://localhost:11434/api/tags"
  timeout_s: 15.0

  discovered_model_fields:
    - name: str               # 模型名（如 "qwen3:8b"）
    - source: str             # "ollama" | "remote_api"
    - provider: str           # 提供商（如 "qwen3"）
    - size_bytes: int         # 模型文件大小
    - parameter_size: str     # 参数量（如 "8B"）
    - quantization_level: str # 量化等级（如 "Q4_K_M"）
    - family: str             # 模型家族
    - available: bool         # 是否可用
    - metadata: dict          # 扩展元数据

  skip_patterns: ["bge", "embed", "nomic", "mxbai", "all-minilm",
                   "multilingual-e5", "snowflake", "gte-", "e5-",
                   "stella", "jina-embed"]

  max_ollama_models: 10       # 防止过多细小模型拖慢 benchmark
```

### 2.3 评测用例 —— benchmark_suite.py

7 维度 × 26 项标准化测试，覆盖从代码生成到逻辑推理的全频谱。

```yaml
benchmark_dimensions:
  code_generation:       # 5 题 —— 函数实现、数据结构、异步代码、异常处理、算法
  code_fix:              # 3 题 —— Bug 修复、重构、功能添加
  semantic:              # 4 题 —— 情感分析、NLI、摘要、分类
  hallucination:         # 5 题 —— API 编造、事实检查、参数编造、已知结果、诚实拒绝
  latency:               # 3 题 —— 简单响应、JSON 输出、短代码（用于精确测速）
  quality:               # 3 题 —— JSON 格式、Markdown 格式、指令遵循
  reasoning:             # 3 题 —— 演绎推理、数学、代码追踪
```

每个 BenchmarkCase 包含：
- `prompt` / `expected_patterns`（正则匹配）/ `forbidden_patterns`（越界检测）
- `expected_output_type`（code|text|json|classification）/ `weight`
- `reference_answer`（用于相似度对比评分）

### 2.4 评测引擎 —— profiler.py

```yaml
profiler:
  profile_all():               # 全量评测（Ollama + 远程）
  profile_ollama_only():       # 仅 Ollama 本地模型
  quick_profile(model_name):   # 快速评测（5 题：latency + semantic）

  ollama_call:
    endpoint: "POST /api/chat"
    options:
      temperature: 0.0         # 零温度确保可复现
      num_predict: max(tokens, 256)  # 给 reasoning 模型留足 thinking 空间
    thinking_models:           # Qwen3/DeepSeek-R1 的 thinking 字段处理
      fallback: "message.thinking if message.content is empty"

  output_metrics:
    model_level:
      - average_score           # 加权综合评分
      - latency_p50_ms          # 中位延迟
      - latency_p95_ms          # 95 分位延迟
      - latency_p99_ms          # 99 分位延迟
      - throughput_tokens_per_sec  # 综合吞吐
      - hallucination_rate      # 幻觉率（0-1）
      - code_validity_rate      # 代码质量率
      - json_validity_rate      # JSON 合法性率
    case_level:
      - case_id / category / subcategory
      - passed / score / latency_ms / tokens_generated / tokens_per_second
      - expected_matches / forbidden_hits

  ranking:
    algorithm: "sort_by_composite_score_descending"
    recommendation_format: |
      BEST_OVERALL: score=X.XX P50=XXXms throughput=XXX tok/s
      RANK #N: gap=X.XX latency_delta=XXXms vs best
```

### 2.5 结果持久化与漂移检测 —— results_writer.py

```yaml
persistence:
  format: "JSONL（每行一个模型）"
  path: "data/model_profiles/benchmark_{timestamp}.jsonl"

  drift_detection:
    method: "对比最新 2 次 benchmark 结果的 score/latency/throughput 变化"
    thresholds:
      score_decline: 0.10      # 分数下降 > 0.10 → 漂移
      latency_increase_pct: 0.50  # 延迟增加 > 50% → 漂移
    output:
      drift_detected: bool
      details:
        score_delta / latency_delta_ms / latency_increase_pct
        throughput_delta_tok_per_sec / hallucination_rate_delta
        category_drift: {cat: delta}
```

### 2.6 任务×模型学习引擎 —— task_model_learner.py

核心创新：不只是评测模型能力，而是追踪每个**任务类型**在每个**模型**上的实际运行表现。

```yaml
ModelTaskMatrix:
  data_structure: |
    {
      "M3_code_generation": {
        "qwen3:8b": {sample_count: 42, avg_duration_ms: 850, avg_tokens_per_sec: 72, composite_score: 0.76},
        "deepseek-r1:8b": {sample_count: 15, avg_duration_ms: 1200, avg_tokens_per_sec: 40, composite_score: 0.68}
      },
      ...
    }

  record(task_type, model, duration_ms, tokens, confidence):
    - 增量更新样本统计
    - 每次 record 后重新计算 composite_score
    - 自动截断历史样本（保留最近 200 个）

  recommend(task_type):
    strategy: |
      if sample_count >= 3:
        source = "learned"        # 用实际运行数据
      elif benchmark_baseline:
        source = "benchmark_baseline"  # 用 benchmark 基准
      else:
        source = "static_spec"    # 回退到 M_MODULE_SPECS

  composite_formula: |
    speed_score = min(throughput / 200, 1.0)
    quality_score = avg_confidence
    consistency_score = 1.0 - stddev(duration) / max(avg_duration, 1.0)
    composite = speed × 0.40 + quality × 0.35 + consistency × 0.25

  persistence:
    path: "data/model_learning/task_model_matrix.json"
    load_on_init: true           # 启动时从磁盘恢复历史
    save_on_update: 自动保存
```

### 2.7 CLI 入口 —— cli.py

```bash
python -m zephyr.pipeline.model_profiler.cli discover     # 列出所有可用模型
python -m zephyr.pipeline.model_profiler.cli quick <model>       # 快速测试单个模型
python -m zephyr.pipeline.model_profiler.cli benchmark            # 全量 benchmark
python -m zephyr.pipeline.model_profiler.cli best               # 显示最佳模型
python -m zephyr.pipeline.model_profiler.cli drift <model>      # 漂移检测
python -m zephyr.pipeline.model_profiler.cli history            # 查看历史记录
```

---

## 3. 集成架构

### 3.1 PipelineOrchestrator 集成

```
PipelineOrchestrator.__init__():
  if auto_profile_on_startup:
    _start_auto_profile()       # 后台线程，不阻塞初始化
  _start_periodic_profile()     # 定时调度（可配置间隔）

PipelineOrchestrator.run_model_benchmark():
  → ModelProfiler.profile_ollama_only()
  → to_model_benchmark_result()
  → write_benchmark_results()  # 持久化
  → _feed_results_to_router()  # 注入 ModelRouter
  → return results

配置项:
  auto_profile_on_startup: bool = False
  periodic_profile_interval_s: float = 0.0  (0=禁用)
```

### 3.2 Budget Enforcer / ModelRouter 集成

```
ModelRouter.load_benchmark_profiles(profiles):
  → 存储到 _benchmark_profiles dict

ModelRouter.load_benchmark_from_disk(results_dir):
  → 从 data/model_profiles/ 加载最近的 JSONL

ModelRouter.route():
  原: candidates.sort(key=cost)          # 仅按价格
  新: candidates.sort(key=composite)     # 按价格×速度×质量综合排序

RoutingDecision 新增字段:
  performance_score: float       # 该路由决策的性能评分
  benchmark_available: bool      # benchmark 数据是否可用

新增 API:
  router.has_benchmarks: bool
  router.benchmark_count: int
  router.set_perf_weights(cost, speed, quality)  # 动态调权
```

### 3.3 AutoRuntimeCore 大脑集成

```
AutoRuntimeCore.boot():
  ├── _start_local_models()       # 启动 Ollama + Scheduler
  ├── _init_task_learner()        # 初始化 ModelTaskMatrix
  └── _benchmark_and_learn()      # 后台线程跑 benchmark → 播种矩阵 + 注入路由

AutoRuntimeCore.reconcile():
  └── _learn_from_completed_tasks()  # 从已完成任务中学习 → 更新矩阵

AutoRuntimeCore.status_panel():
  └── 追加 learner.summary()      # 显示任务→模型推荐矩阵

AutoRuntimeCore.shutdown():
  └── _task_learner._save()      # 持久化学习状态

新增 API:
  core.learn_from_task_result(task_type, model, duration_ms, tokens, confidence)
  core.get_task_model_recommendations() → list[dict]
  core.learner_summary() → str
```

---

## 4. 性能与资源约束

```yaml
benchmark_performance:
  quick_profile:
    estimated_duration: "10-30s per model"
    api_calls_per_model: 5

  full_benchmark:
    estimated_duration: "2-5 min per model"
    api_calls_per_model: 26
    total_models_max: 10

  resource_impact:
    cpu: "minimal（仅 HTTP 客户端）"
    memory: "negligible"
    network: "localhost only"

task_learning:
  storage: "< 1MB per 1000 task records"
  compute: "O(1) per record() call"
  memory: "rolling window of 200 samples per (task,model) pair"
```

---

## 5. 故障模式与恢复策略

```yaml
failure_modes:
  ollama_unavailable:
    detection: "ModelDiscovery.ollama_available() → False"
    behavior: "跳过 Ollama 模型，仅返回远程 API 模型"
    no_panic: true

  model_timeout:
    detection: "单个 benchmark case > 60s"
    behavior: "标记该 case 为 FAIL，继续下一个 case"
    no_panic: true

  learner_corrupted:
    detection: "JSON 反序列化异常"
    behavior: "丢弃损坏文件，从空矩阵重新开始"
    recovery: "下次 benchmark 自动播种基准数据"

  router_without_profiles:
    behavior: "回退到 cost-only 排序"
    reason: "least-cost-tier"

  disk_write_failure:
    behavior: "静默跳过，log warning"
    impact: "本次结果不持久化，但不影响内存中的路由决策"
```

---

## 6. 演进路线

```yaml
roadmap:
  v1.1.0:
    - 远程 API 模型 benchmark（需要 API key 注入机制）
    - benchmark 结果可视化图表（雷达图）
    - 历史趋势线（score/latency 随时间变化）

  v1.2.0:
    - 自动重跑策略：检测到新模型/模型版本变化时自动触发 benchmark
    - A/B 对比：同一任务类型在不同模型上的平行对比
    - 成本感知推荐：综合考虑价格 + 性能 + 质量

  v2.0.0:
    - 强化学习路由：ModelTaskMatrix 驱动的自动路由权重调整
    - 预测性推荐：在任务执行前预测最佳模型（基于任务特征 embedding）
    - 跨任务模型共享优化：多任务共用同一个模型的调度策略
```

---

## 7. 盲点与风险

```yaml
known_blind_spots:
  BS-034-001:
    description: "远程 API 模型未进行 benchmark"
    severity: medium
    mitigation: "v1.1.0 加入 API key injection 后补齐"

  BS-034-002:
    description: "模型版本升级后旧 benchmark 结果失效"
    severity: medium
    mitigation: "v1.2.0 自动检测模型 digest 变化触发重测"

  BS-034-003:
    description: "幻觉检测依赖静态 QA 数据集，可能被模型 '记忆' 绕过"
    severity: low
    mitigation: "定期轮换测试用例（已有 rotate exam_test_cases 规划）"

  BS-034-004:
    description: "cold start: 系统首次启动无任何 benchmark 数据"
    severity: low
    mitigation: "auto_profile_on_startup=True + ModelRouter cost-only 回退"

  BS-034-005:
    description: "learning bias: 热路径任务样本远多于冷路径（如 M3 > M11）"
    severity: low
    mitigation: "基准线兜底——冷路径任务回退到 benchmark baseline 推荐"
```

---

## 附录 A：模块导出清单

```python
# zephyr.pipeline 通过 __init__.py 导出以下符号
ALL_BENCHMARK_CASES    # 26 个 BenchmarkCase
BenchmarkCase          # 评测用例数据模型
CaseResult             # 单个评测结果
CATEGORY_MAP           # 维度 → 用例列表映射
DiscoveredModel        # 发现的模型
ModelDiscovery         # 模型发现器
ModelProfile           # 模型评测 Profile
ModelProfiler          # 核心评测引擎
ModelTaskEntry         # 任务×模型学习条目
ModelTaskMatrix        # 任务×模型学习矩阵
TaskRecommendation     # 任务推荐
detect_drift           # 漂移检测函数
load_benchmark_history # 加载历史
to_model_benchmark_result # Profile → BenchmarkResult
write_benchmark_results   # 持久化写入
```

## 附录 B：消费者集成示例

```python
# Budget Enforcer 集成
router = ModelRouter()
router.load_benchmark_from_disk("data/model_profiles")
router.set_perf_weights(cost=5, speed=3, quality=2)
decision = router.route()  # now perf-aware

# 大脑集成
core = AutoRuntimeCore(config)
core.learn_from_task_result("M3", "qwen3:8b", 850, 62, 0.87)
recs = core.get_task_model_recommendations()
for r in recs:
    print(f"{r['task_type']}: {r['best_model']} ({r['source']})")
```