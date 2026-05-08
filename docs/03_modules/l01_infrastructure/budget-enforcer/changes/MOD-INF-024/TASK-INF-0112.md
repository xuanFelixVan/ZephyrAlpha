---
task_id: "TASK-INF-0112"
module_id: "MOD-INF-024"
title: "Stream Abort Guard — 流式输出中途三维预算二次确认（§2.13 + D-024-11）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.13"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\stream_abort_guard.py"
acceptance_criteria:
  - "AC-01: StreamAbortGuard 在流式输出生命周期中位置 in_flight——Pre-flight（事前）和 Post-flight（事后）之间"
  - "AC-02: 每 500 output token 做一次 checkpoint 预算检查——非阻塞不中断流"
  - "AC-03: Checkpoint 1：remaining_budget - estimated_completion_cost < 0 → IMMEDIATE_ABORT（发 abort signal 给 provider）"
  - "AC-04: Checkpoint 2：output_quality_gate.score < 0.3 AND tokens_emitted > 200 → ABORT_AND_RETRY（换更便宜模型重试）"
  - "AC-05: Checkpoint 3：cumulative_response_too_verbose（token_count > expected × 3）→ ABORT_WITH_WARNING"
  - "AC-06: Provider 适配四家：Anthropic(SSE stop_reason='max_tokens'), OpenAI(finish_reason='length'), Google(finishReason='MAX_TOKENS'), DeepSeek(同 OpenAI 协议)"
  - "AC-07: partial_output_handling——abort 时保存 partial_response 到 context_budget_tracker"
  - "AC-08: resume_strategy——下次调用时 append partial_response 到 system prompt '之前的回答在 [X] token 处中断'"
  - "AC-09: abort 决策写入 audit trail——含 checkpoint_id, reason, tokens_emitted, tokens_saved"
  - "AC-10: 支持 disable_stream_abort() 上下文管理器——特定关键调用禁止中途 abort"
rollback_instructions: "删除 stream_abort_guard.py，移除调用点。系统退化为无流式控制模式——输出任由模型完成，无中途干预（预飞行仍有 Pre-flight Gate）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L738-L765 (§2.13 Stream Abort Guard)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [stream-abort, in-flight, streaming-sse, checkpoint, partial-output, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0112: Stream Abort Guard — 流式输出事中预算控制

## 1. 任务目标

实现流式输出中途预算二次确认——在 LLM 流式输出期间，每 500 tokens 执行 checkpoint 检查。如果预算剩余不足以完成响应、输出质量差、或响应过于冗长，立即 abort 并保存部分结果。这是 Pre-flight Gate 的事中互补组件。

## 2. 背景

蓝图 §2.13（决策 D-024-11，v0.4.0 新增）：Pre-flight Gate 只能管输入端——流式输出开始后，输出中途无控制能力。87% 的成本超支发生在输出阶段。此组件补齐 in-flight 控制短板。

## 3. 实施步骤

### Step 1: 类型定义
```python
@dataclass
class StreamCheckpoint:
    token_count: int
    remaining_budget: int
    estimated_completion_cost: int
    quality_score: float
    verbose_ratio: float

@dataclass
class AbortDecision:
    action: str  # "IMMEDIATE_ABORT" | "ABORT_AND_RETRY" | "ABORT_WITH_WARNING" | "CONTINUE"
    reason: str
    partial_output: str
    tokens_saved: int
```

### Step 2: StreamAbortGuard 核心
```python
class StreamAbortGuard:
    CHECKPOINT_FREQUENCY = 500

    def __init__(self, tracker: BudgetTracker, quality_gate):
        self.tracker = tracker
        self.quality_gate = quality_gate
        self._disabled = False

    async def wrap_stream(self, stream: AsyncIterator[str],
                          estimated_total: int,
                          provider: str) -> AsyncIterator[StreamChunk]:
        tokens_emitted = 0
        partial_output = []
        async for chunk in stream:
            tokens_emitted += self._count_tokens(chunk)
            partial_output.append(chunk)
            if tokens_emitted % self.CHECKPOINT_FREQUENCY == 0:
                decision = self._checkpoint(tokens_emitted, partial_output,
                                            estimated_total, provider)
                if decision.action != "CONTINUE":
                    yield StreamChunk(abort=decision)
                    return
            yield StreamChunk(chunk=chunk)
```

### Step 3: 四 Provider Adaptors
- AnthropicSSEAdaptor: 监听 stop_reason
- OpenAISSEAdaptor: 监听 finish_reason
- GoogleSSEAdaptor: 监听 finishReason
- DeepSeekSSEAdaptor: 同 OpenAI 协议

### Step 4: Partial Output Saving
- abort 时保存 partial_response JSON
- 标记 checkpoint_token_count
- 下次调用时 append 到 system prompt

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/stream_abort_guard.py` | 新建 |
