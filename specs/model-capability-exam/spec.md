# ModelCapabilityExam — AI 模型入职考试系统

> **蓝图编号**: MCE-0001
> **归属轨道**: `b_track` / `l12` / AutoRuntime Core 子系统
> **依赖**: `ActionDispatcher`, `LocalModelScheduler`, `OllamaChat`, 现有 `ModelProfiler` + `BenchmarkSuite`
> **版本**: v1.0.0-design
> **状态**: `design` — 架构设计阶段

---

## 0. 问题定义

### 当前痛点

1. 大脑不知道模型能做什么、不能做什么
2. qwen3:8b 的 code_fix 精度极低（上次实测引入 bug），但系统没有阻止它
3. 所有任务无差别分配给同一个模型，不区分难度
4. 没有模型精度、速度、幻觉率的量化数据
5. 没有长时间运行的漂移追踪

### 设计目标

```
每条 AI 进入系统时，自动跑一场入职考试：

    横轴（Breadth）:  能做什么？ → 能力覆盖范围
    纵轴（Depth）:    做得多好？ → 精度 / 召回 / F1
    速轴（Speed）:    做得多快？ → 延迟 / 吞吐
    幻轴（Halluc）:   会不会瞎编？ → 幻觉率
    稳轴（Drift）:    时间长了还稳吗？ → 长时间漂移
```

---

## 1. 架构全景

```
                   ┌──────────────────────────────────┐
                   │       ModelCapabilityExam         │ ← 入职考试主控
                   │       (exam_orchestrator.py)       │
                   └──────────────┬───────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐     ┌───────────────────┐     ┌───────────────────┐
│ BreadthExam   │     │   DepthExam        │     │   StressTest      │
│ 横轴: 能力边界 │     │   纵轴: 精度深度    │     │   速轴+幻轴+稳轴   │
│               │     │                    │     │                   │
│ 每个能力类型    │     │ 每个能力的:         │     │ 延迟 P50/P95/P99  │
│ 跑 1 道验证题  │     │ - precision        │     │ tokens/sec        │
│ 判断: pass/fail│     │ - recall           │     │ 幻觉触发率         │
│ 门槛: 产出合法  │     │ - edit_distance    │     │ 重复一致性         │
│ 结构化结果即可  │     │ - exact_match      │     │ 长时间漂移曲线     │
└───────┬───────┘     └────────┬──────────┘     └────────┬──────────┘
        │                      │                          │
        └──────────────────────┼──────────────────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │   CapabilityPassport     │ ← 能力护照 (JSON)
                   │   .brain/passports/      │
                   │   {model_id}.json        │
                   └───────────┬─────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │   TaskGate               │ ← 任务门控
                   │   dispatch 前检查护照      │
                   │   只分配 pass=true 的能力  │
                   └─────────────────────────┘
```

---

## 2. 横轴设计 (BreadthExam)

### 2.1 核心逻辑

```
对每个 INFERENCE_CAPABILITIES 类型，生成一个最小验证 prompt，
只要模型能产出结构合法的结果 → pass
不管结果对不对（那是纵轴的事）
```

### 2.2 能力 → 验证 Prompt 映射

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

### 2.3 评分

```
breadth_score = passed_count / total_capabilities
pass 阈值: 产出合法结构即可（不判断语义正确性）
```

---

## 3. 纵轴设计 (DepthExam)

### 3.1 核心逻辑

```
对每个 pass=true 的能力，跑 N 道精心设计的标准题，
计算 precision / recall / edit_distance / exact_match
```

### 3.2 测试用例结构

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

### 3.3 各能力类型深度测试题（首批各 3 道）

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

### 3.4 评分指标

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

---

## 4. 速轴设计 (StressTest — Speed)

### 4.1 测量维度

| 指标 | 计算方式 | 意义 |
|------|----------|------|
| `latency_p50` | 所有推理的中位数延迟 | 典型响应时间 |
| `latency_p95` | 95 分位延迟 | 最坏情况延迟 |
| `latency_p99` | 99 分位延迟 | 极端情况延迟 |
| `tokens_per_second` | 总 output tokens / 总耗时 | 吞吐能力 |
| `time_to_first_token` | 首 token 时间 | 流式感知延迟 |

### 4.2 测量方式

每个能力跑 3 次相同 prompt，取中位数，收集时间戳

---

## 5. 幻轴设计 (StressTest — Hallucination)

### 5.1 幻觉识别

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

### 5.2 幻觉率定义

```
hallucination_rate = 触发幻觉检测的 case / 总测试 case

细分:
  fabrication_rate    — 编造不存在的内容
  inconsistency_rate  — 同 prompt 多次跑结果不一致
  refusal_rate        — 拒绝回答
```

---

## 6. 稳轴设计 (StressTest — Drift)

### 6.1 漂移测试协议

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

### 6.2 漂移指标

```
output_drift = 1 - Jaccard(baseline_output, current_output)
速度漂移     = current_latency / baseline_latency
幻觉漂移     = current_hallucination_rate - baseline_hallucination_rate
```

---

## 7. CapabilityPassport 数据模型

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

---

## 8. TaskGate 门控逻辑

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

---

## 9. 集成到 AutoRuntime 启动流程

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

---

## 10. 文件规划

```
src/zephyr/runtime/
    model_capability_exam/          ← 新目录
        __init__.py
        exam_orchestrator.py        ← 考试主控
        breadth_exam.py             ← 横轴测试
        depth_exam.py               ← 纵轴测试 + 测试用例库
        stress_test.py              ← 速轴 + 幻轴 + 稳轴
        capability_passport.py      ← 护照数据模型 + IO
        task_gate.py                ← 任务门控

data/
    brain/
        passports/                  ← 护照存储
            qwen3:8b.json
            deepseek-r1:8b.json
            ...
```

---

## 11. 踩过的坑 & 设计原则

1. **横轴和纵轴必须分离** — 横轴只问"能产出合法的结构化结果吗"，纵轴才问"结果正确吗"
2. **幻觉检测不是一次性的** — 需要多次重复 + 输入交叉验证
3. **漂移测试需要热负载** — 冷启动测试和长时间运行测试必须分开
4. **Gate 必须是硬阻断** — code_fix 精度 31% 就绝对不能 dispatch，不能只 warn
5. **护照必须可版本化** — 模型更新后要重考，旧护照作废
6. **门槛可配置** — 各能力类型的 pass 阈值应该是可调的，不用改代码