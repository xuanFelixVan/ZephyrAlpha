---
task_id: "TASK-INF-0128"
module_id: "MOD-INF-024"
title: "Fail-Mode Manager — per-degradation-level + per-budget-level Fail-Open/Closed 配置 + Heartbeat + Cold Start Anti-Abuse + Bootstrapping Revisit（§2.29 + D-024-27 + D-024-28）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.29"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0105"
  - "TASK-INF-0116"
  - "TASK-INF-0130"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\context_waste_detector.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\fail_mode_manager.py"
acceptance_criteria:
  - "AC-01: FailModeManager 每降级级独立 fail-open/closed 可配置——prevent denial-of-service through budget exhaustion"
  - "AC-02: L0_notify/L1_warning → fail_open (记录日志但允许继续) — NaN-proof"
  - "AC-03: L1.5_sunk_cost → fail_open_WARN (强制执行级联检查) — NaN-proof"
  - "AC-04: L2_model_switch → fail_closed (如果定价信息缺失/同步失败 → 禁止降级模型 (保持当前 tier 并告警))"
  - "AC-05: L3_compress → fail_open (如果 Context Engine 不可用 → 压成最后 5 轮 + 标记为 'todo: 检查压缩器')"
  - "AC-06: L4_minimal → fail_closed (不 minimal 继续消耗) — possible loss of production budget"
  - "AC-07: L5_halt → fail_closed (halt 是必须的——预算耗尽已经是业务层面的损失)"
  - "AC-08: L6_kill_switch → fail_closed (全局熔断不能被 bypass——基础设施故障是 Agent 无法判断的)"
  - "AC-09: 预算层级 fail-mode——独立于降级级 fail-mode，按预算层级（l0_request→l4_5_self）指定各组件的故障行为——蓝图 §2.29 中 per_level_fail_mode YAML 定义"
  - "AC-10: l0_request → fail-closed（单次请求故障拒止——防止故障请求炎上）"
  - "AC-11: l1_turn → fail-closed（单轮循环故障拒止——防止失效工具递归）"
  - "AC-12: l2_task → fail-closed（任务故障拒止——防止失控任务消耗预算）"
  - "AC-13: l3_session → fail-open限流（会话故障限流 25% 正常运行速率——保证系统可用性）"
  - "AC-14: l3_5_workflow → fail-open限流（Workflow 故障限流——防止跨任务链锁死）"
  - "AC-15: l4_global → fail-closed（全局故障必须拒止——这是基础设施级决策）"
  - "AC-16: l4_5_self → fail-open限流（Self-Budget 故障适当限流——允许 guard 有限度运作）"
  - "AC-17: Heartbeat 监控——每 30 秒检查各组件健康（BudgetTracker/PreFlightGate/DegradationManager/StreamAbortGuard/OutputQualityGate/TimeoutGuard），连续 3 次 heartbeat 失败触发对应 fail_mode"
  - "AC-18: Auto-Recovery——组件恢复后自动从 fail_mode 恢复正常模式（notify Owner + write audit trail）"
  - "AC-19: Cold Start Anti-Abuse——同一 Owner 1 小时内最多 3 个 Session（超过则冷启动豁免降为 1000 token）；24 小时内冷启动豁免累计不超过 27,500 token（= 5 × 5500）——蓝图 §2.29 cold_start_anti_abuse YAML"
  - "AC-20: Cold Start 超限检测告警——超过速率限制触发 WARN '检测到频繁 Session 重启——冷启动豁免已缩容'——蓝图 §2.29 detection 字段"
  - "AC-21: Bootstrapping 退出条件验证——至少 100 个任务数据点且连续 10 个任务预算预估偏差 < 20%，Owner 可手动执行 `zephyr budget exit-calibration` 提前结束——蓝图 §2.30 exit_criteria"
  - "AC-22: Bootstrapping 校准模式下的日消耗硬约束——hard_limit ×3 仅影响告警阈值，daily_cap 仍保持生效——蓝图 §2.30 calibration_profile"
  - "AC-23: Heartbeat monitor 自身也必须被心跳检查——Meta-heartbeat（watchdog 守护 heartbeat monitor 自身）"
rollback_instructions: "删除 fail_mode_manager.py。系统退化为无 fail-mode 控制——每个降级级使用默认 fail-open（优先级 producability > cost safety）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1335-L1396 (§2.29 Fail-Mode + Cold Start + Bootstrap)")
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [fail-mode, fail-open-closed, cold-start-abuse, bootstrap-revisit, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0128: Fail-Mode Manager + Cold Start Anti-Abuse + Bootstrapping Revisit

## 1. 任务目标

实现故障模式管理器——当 Budget Enforcer 各组件自身故障时（Context Engine 不可用、定价同步失败等），每级降级独立决定 fail-open（允许继续）还是 fail-closed（拒绝继续）。同步实现 Cold Start 防滥用和 Bootstrapping 回退校验。

## 2. 背景

蓝图 §2.29（D-024-27 Fail-Mode, D-024-28 Cold Start Revisit + Bootstrap Revisit）：Temporal research findings 要求 fail-open/closed 机制。Cold Start 在 Race Condition / Multi-Session 场景有潜在滥用风险。Bootstrap 30 天积累数据可能不足以生成有效阈值。

## 3. 实施步骤

```python
class FailModePolicy(Enum):
    FAIL_OPEN = "fail_open"
    FAIL_CLOSED = "fail_closed"
    FAIL_OPEN_WARN = "fail_open_warn"

class FailModeManager:
    DEFAULT_POLICIES = {
        DegradationLevel.L0_NOTIFY: FailModePolicy.FAIL_OPEN,
        DegradationLevel.L1_WARNING: FailModePolicy.FAIL_OPEN,
        DegradationLevel.L1_5_SUNK_COST: FailModePolicy.FAIL_OPEN_WARN,
        DegradationLevel.L2_MODEL_SWITCH: FailModePolicy.FAIL_CLOSED,
        DegradationLevel.L3_COMPRESS: FailModePolicy.FAIL_OPEN,
        DegradationLevel.L4_MINIMAL: FailModePolicy.FAIL_CLOSED,
        DegradationLevel.L5_HALT: FailModePolicy.FAIL_CLOSED,
        DegradationLevel.L6_KILL_SWITCH: FailModePolicy.FAIL_CLOSED,
    }

    def evaluate(self, level: DegradationLevel,
                 dependency_status: dict[str, bool]) -> FailDecision:
        policy = self.DEFAULT_POLICIES[level]
        if policy == FailModePolicy.FAIL_CLOSED:
            return FailDecision.DENY
        if policy == FailModePolicy.FAIL_OPEN:
            return FailDecision.ALLOW_WITH_WARNING
        # FAIL_OPEN_WARN: allow but require cascade check

class ColdStartAbuse:
    def __init__(self):
        self.used_nonces: set[str] = set()

    def grant(self, session_id: str, signature: bytes) -> bool:
        if session_id in self.used_nonces:
            return False
        self.used_nonces.add(session_id)
        return True
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/fail_mode_manager.py` | 新建 |
