---
task_id: "TASK-INF-0113"
module_id: "MOD-INF-024"
title: "Output Quality Gate — 前 N token 快速质量校验（Format/Relevance/Hallucination）+ Auto-Retry（§2.14 + D-024-12）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.14"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0112"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\stream_abort_guard.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\output_quality_gate.py"
acceptance_criteria:
  - "AC-01: format_check——前 200 output tokens 检测 JSON/XML 完整性、代码块闭合、Markdown 语法正确性"
  - "AC-02: format_check fail → ABORT + 追加 '你的输出格式有误，请重新生成' 到下一轮 prompt"
  - "AC-03: relevance_check——前 300 output tokens 做 Fast embedding similarity(partial_output, task_prompt)，similarity < 0.4 → ABORT"
  - "AC-04: hallucination_check——full response 后验证输出中声称的 file_path/module_id 是否真实存在"
  - "AC-05: hallucination fail → MARK_FAILED + 不计入 ROI + 写入 audit trail"
  - "AC-06: auto_retry——max_retries=2, attempt_1 same model + extra 'be accurate' prompt, attempt_2 升级 Tier"
  - "AC-07: 所有 quality check 结果写入预算审计——含 check_type, score, decision, response_fragment"
  - "AC-08: quality gate 自身成本走 Self-Budget（LLM-dependent check 如 relevance 用 tier_0_free）"
  - "AC-09: 支持 disable_quality_gate() 上下文管理器——特定高速场景跳过质量检查"
  - "AC-10: 集成 Drift Detector (MOD-INF-023)——full response 后调用 validator.early_quality_check()"
rollback_instructions: "删除 output_quality_gate.py。系统退化为无实时质量检查——所有输出被接受（依赖事后 ROI 分析发现质量下降）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L768-L804 (§2.14 Output Quality Gate)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [output-quality, format-check, relevance-check, hallucination, auto-retry, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0113: Output Quality Gate — 输出质量实时校验与自动重试

## 1. 任务目标

实现输出质量门——在 LLM 响应生成期间/之后对输出进行快速质量校验。三阶段检查（格式/相关性/幻觉），fail 后自动重试并升级模型。这是 Token ROI 分析的实时互补——不必等到 4000 token 输出完了才知道是垃圾。

## 2. 背景

蓝图 §2.14（决策 D-024-12，v0.4.0 新增）：实时质量信号比事后 ROI 分析更有成本控制价值。前 200-300 token 即可判断输出质量趋势。

## 3. 实施步骤

### Step 1: 类型定义
```python
class QualityCheckType(Enum):
    FORMAT = "format"
    RELEVANCE = "relevance"
    HALLUCINATION = "hallucination"

@dataclass
class QualityCheckResult:
    check_type: QualityCheckType
    score: float
    passed: bool
    details: str
    response_fragment: str
```

### Step 2: FormatChecker
```python
class FormatChecker:
    def check(self, text: str) -> QualityCheckResult:
        # regex-based: JSON brackets, code fences, markdown syntax
        # LLM-free (regex-based per SUPERVISORAGENT principle)
```

### Step 3: RelevanceChecker
```python
class RelevanceChecker:
    def __init__(self, embedding_model):
        self.embedder = embedding_model

    def check(self, partial_output: str,
              task_prompt: str) -> QualityCheckResult:
        sim = cosine_similarity(
            self.embedder.encode(partial_output),
            self.embedder.encode(task_prompt)
        )
        return QualityCheckResult(..., score=sim, passed=sim >= 0.4)
```

### Step 4: HallucinationChecker
```python
class HallucinationChecker:
    def check(self, full_response: str,
              workspace_index: WorkspaceIndex) -> QualityCheckResult:
        # 提取 claimed paths/module_ids
        # 交叉引用 workspace index
        # 不存在的 → flag hallucination
```

### Step 5: Auto-Retry
- max_retries=2
- attempt_1: same model + enhanced prompt
- attempt_2: upgrade tier
- 每次 retry 写入 audit trail

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/output_quality_gate.py` | 新建 |
