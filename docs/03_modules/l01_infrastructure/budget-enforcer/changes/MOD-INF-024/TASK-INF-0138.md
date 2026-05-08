---
task_id: "TASK-INF-0138"
module_id: "MOD-INF-024"
title: "Budget Enforcer —— 全生命周期编排器：Pre-flight → In-flight → Post-flight 三阶段串联（§4 budget_enforcer.py + §1.1 + §2 集成）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§4 (budget_enforcer.py) + §1.1 + §2 all components integration"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0103"
  - "TASK-INF-0105"
  - "TASK-INF-0106"
  - "TASK-INF-0112"
  - "TASK-INF-0113"
  - "TASK-INF-0119"
  - "TASK-INF-0120"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\pre_flight_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\stream_abort_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\output_quality_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\timeout_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\action_history.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\self_budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_enforcer.py"
acceptance_criteria:
  - "AC-01: BudgetEnforcer 类作为模块的单一入口主控——所有外部调用通过此接口接入预算系统"
  - "AC-02: call() 方法实现完整三阶段生命周期——Pre-flight(事前预算检查) → In-flight(流式输出中途控制) → Post-flight(消耗结算+成本归因+Audit写入)"
  - "AC-03: Pre-flight 阶段：调用 PreFlightGate.check()，ALLOW → 继续，非 ALLOW → 返回 GateDecision 并短路"
  - "AC-04: Pre-flight 阶段：ALLOW 后调用 BudgetTracker.consume() 预先核销预估输入 token"
  - "AC-05: In-flight 阶段：将 API 流式输出包装在 StreamAbortGuard.wrap_stream() 中，每 500 token checkpoint"
  - "AC-06: In-flight 阶段：TimeoutGuard 的 request_timer 并行运行，超时即 abort"
  - "AC-07: Post-flight 阶段：流式输出结束后调用 BudgetTracker.consume() 核销实际输出 token"
  - "AC-08: Post-flight 阶段：OutputQualityGate 校验输出质量，fail → auto_retry（最多 2 次）"
  - "AC-09: Post-flight 阶段：调用 ActionHistory.append() 记录此次 action，DedupChecker 检测循环/螺旋"
  - "AC-10: Post-flight 阶段：SelfBudgetTracker.track_call(check_name, tokens) 更新 guard 自身消耗"
  - "AC-11: Post-flight 阶段：DegradationManager.evaluate() 检查是否需要降级"
  - "AC-12: Post-flight 阶段：写入结构化 audit log（含所有三阶段决策和结果）"
  - "AC-13: 提供 enforce_call(messages, model_config, task_context) → EnforcementResult 统一异步接口"
  - "AC-14: EnforcementResult 包含：final_response, total_tokens_consumed, total_cost, gate_decision_path, degradation_level, audit_entry_ids"
  - "AC-15: Startup 时执行健康检查——验证所有子组件可初始化 + 16 cross-module contracts reachable（15 §9 + 1 §2.26） + 输出 'Budget Enforcer → [16 of 16 OK]'"
  - "AC-16: 全局异常兜底——任何子组件抛出未预期异常 → 降级为 fail-safe 模式（按 Fail-Mode Manager 的配置）"
  - "AC-17: 与所有 16 个集成点的连接通过 CrossModuleIntegrator 代理——不直接 import 模块"
rollback_instructions: "删除 budget_enforcer.py，所有调用方回退到直接调用子组件（PreFlightGate/StreamAbortGuard/OutputQualityGate 独立接口）。系统退化为无编排的分散调用模式"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1421-L1455 (§4 文件组成——budget_enforcer.py 首行)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L48-L69 (§1.1 模块身份 + §1.2 核心职责 + §1.3 升级摘要)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L142-L181 (§2.2 Pre-flight Gate)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L738-L765 (§2.13 Stream Abort Guard)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L768-L804 (§2.14 Output Quality Gate)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [budget-enforcer, orchestrator, lifecycle, pre-flight, in-flight, post-flight, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0138: Budget Enforcer — 全生命周期编排器

## 1. 任务目标

实现 Budget Enforcer 的主编排器——串联 Pre-flight（事前预算检查）→ In-flight（流式输出控制）→ Post-flight（消耗结算+质量校验+降级评估+审计）三个阶段。这是 Budget Enforcer 模块的唯一对外入口，所有 LLM API 调用必须通过此组件。

## 2. 背景

蓝图 §4 文件列表首行：`budget_enforcer.py` — "预算执行器——全生命周期（事前+事中+事后）+ Pre-flight Gate + In-flight Guards"。§1.1 定义运行时平面覆盖"调用前→调用中→调用后全生命周期"。此组件将分散的子组件（PreFlightGate/StreamAbortGuard/OutputQualityGate/DegradationManager/ActionHistory/SelfBudgetTracker）编排为统一的三阶段执行流程。

## 3. 实施步骤

### Step 1: 三阶段生命周期架构
```python
@dataclass
class EnforcementResult:
    final_response: str
    total_tokens_consumed: int
    total_cost: float
    gate_decision_path: list[GateDecision]
    degradation_level: DegradationLevel
    quality_checks: list[QualityCheckResult]
    audit_entry_ids: list[str]

class BudgetEnforcer:
    def __init__(self, policy_path: str, **component_overrides):
        self.tracker = BudgetTracker(policy_path)
        self.gate = PreFlightGate(self.tracker, self.tracker.policy)
        self.router = ModelRouter(self.tracker.pricing_sync)
        self.degradation = DegradationManager(self.tracker, ...)
        self.stream_abort = StreamAbortGuard(self.tracker, ...)
        self.quality_gate = OutputQualityGate(...)
        self.timeout = TimeoutGuard(self.tracker.policy.time_budget)
        self.action_history = ActionHistory()
        self.self_budget = SelfBudgetTracker(self.tracker)
        self.integrator = CrossModuleIntegrator()

    async def enforce_call(self, messages: list[dict],
                           model_config: dict,
                           task_context: TaskContext) -> EnforcementResult:
        # === PHASE 1: Pre-flight ===
        gate_decision = self.gate.check(...)
        if gate_decision.outcome != GateOutcome.ALLOW:
            return EnforcementResult(gate_decision=gate_decision, ...)

        # Pre-consume estimated input tokens
        self.tracker.consume(BudgetLevel.REQUEST,
                            tokens=gate_decision.estimated_input, cost=0, time_s=0)

        # === PHASE 2: In-flight ===
        routed_model = self.router.route(...)
        stream = await self._call_llm_streaming(routed_model, messages)
        wrapped_stream = self.stream_abort.wrap_stream(stream, ...)
        
        # Timeout Guard runs in parallel
        timeout_task = asyncio.create_task(self.timeout.watch_request())

        # === PHASE 3: Post-flight ===
        final_output = await self._collect_stream(wrapped_stream)
        timeout_task.cancel()

        # Settle actual tokens
        self.tracker.consume(BudgetLevel.REQUEST, actual_output_tokens, actual_cost, 0)

        # Quality check + auto-retry
        quality_result = self.quality_gate.check_final(final_output, task_context)
        if not quality_result.passed:
            final_output = await self._retry(messages, model_config, task_context)

        # Record action + dedup check
        action = ActionSignature.from_tool_call(...)
        self.action_history.append(action)

        # Degradation evaluation
        deg_action = self.degradation.evaluate()

        # Self-budget tracking
        self.self_budget.track_call("budget_enforcer", tokens_consumed, is_llm_free=False)

        return EnforcementResult(...)
```

### Step 2: Startup 健康检查
```python
def startup_health_check(self) -> str:
    checks = {
        "BudgetTracker": self._check_tracker(),
        "PreFlightGate": self._check_gate(),
        "DegradationManager": self._check_degradation(),
        "CrossModuleIntegrator": self.integrator.health_check(),
        "TamperEvidentLog": self._verify_audit_chain(),
    }
    status = "READY" if all(checks.values()) else "DEGRADED"
    return f"Budget Enforcer {status} [{' | '.join(f'{k}={v}' for k,v in checks.items())}]"
```

### Step 3: 全局异常兜底
- 任何子组件抛出未预期异常 → 按 FailModeManager 的 per-level fail-open/closed 决定
- L4_global 级别异常 → HALT 整个 Enforcer（fail-closed）
- L3_session 级别异常 → ALLOW_WITH_LIMIT（fail-open限流）

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/budget_enforcer.py` | 新建 |
