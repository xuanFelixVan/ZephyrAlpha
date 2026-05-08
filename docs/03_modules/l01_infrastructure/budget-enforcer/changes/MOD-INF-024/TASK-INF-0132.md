---
task_id: "TASK-INF-0132"
module_id: "MOD-INF-024"
title: "Cross-Module Integration — 15 集成连接实现 + 集成测试矩阵（§9）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§9"
estimated_tokens: 6000
estimated_time_minutes: 180
owner_signal_required: false
depends_on:
  - "TASK-INF-0101~0131"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\__init__.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\cross_module_integration.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\test_cross_module_integration.py"
acceptance_criteria:
  - "AC-01: MOD-INF-001 Capacity Assurance → Kill Switch 联动 + Degradation 联动：L6 kill_switch 触发/降级链执行 → 调用全局熔断/degradation_chain"
  - "AC-02: MOD-INF-008 Context Engine → 上下文压缩 + 浪费检测联动：L3 compress + waste_ratio > 60% → DocCompressor aggressive 模式"
  - "AC-03: MOD-INF-006 Task System → 任务预算字段 + 状态机预算联动：读取任务预算 + 状态变更联动"
  - "AC-04: MOD-INF-020 Audit Trail → 审计写入：每次降级/熔断/Borrow/Abort → 写入审计事件"
  - "AC-05: MOD-INF-022 Escalation → 升级通知：硬停止 + Kill Switch → 触发升级通知 Owner"
  - "AC-06: MOD-INF-023 Drift Detector → 漂移预算信号：配置漂移对预算的影响 → 调用漂移检测 + 预算影响评估"
  - "AC-07: MOD-MASTER-001 Task System → Batch 路由：task.urgency=low → 自动标记走 Batch API"
  - "AC-08: Git Pre-commit Hook → 策略快照：git commit → 自动快照 budget_policy.yaml 到版本历史"
  - "AC-09: LiteLLM Registry → 新模型发现 + 定价同步：daily sync 发现新 model_id → 评估 + 写摘要 + 通知 Owner"
  - "AC-10: LiteLLM Pricing Strategy Sync → 长上下文定价策略同步：daily sync 检测 pricing strategy 变化 → 更新 non-linear pricing threshold"
  - "AC-11: Context Engine v2 → 历史税加权衰减 + 指令膨胀精简：history_tax_ratio > 5× OR instruction_growth > 20% → DocCompressor 加权衰减 + 生成精简建议"
  - "AC-12: SUPERVISORAGENT LLM-Free Filter → LLM-free 触发：budget_policy LLM-free 阶段提升 → guard 类型从 LLM-dependent → LLM-free"
  - "AC-13: Provenance DAG → 幻觉信息源链追踪：agent output 包含 claim 时 → 追加到 observation provenance DAG"
  - "AC-14: Agent Delegation Registry → 记录 parent-child 委托关系：每次 agent-to-agent call → 记录 delegation edge + 写入 attribution"
  - "AC-15: MOD-INF-014 LLM Security Gateway → IPI 检测 + 策略文件 Ed25519 签名验证 + Trust Ring 隔离：IPI pattern detected / policy modification attempt → 签名验证网关 + Ring escalation"
  - "AC-16: MOD-INF-021 AgentHive 补充集成（蓝图 §2.26 Trust Rings）→ ring gate registration on agent creation + Budget Enforcer 检查委托预算"
  - "AC-17: 每个集成点编写单元集成测试——验证接口契约与蓝图 §9 表一致"
  - "AC-18: 所有 15 个 §9 集成 + 1 个补充集成的状态在 startup check 中展示 'Budget Enforcer → [16 of 16 OK]'"
rollback_instructions: "删除 cross_module_integration.py——各模块退化到零 integration 模式（独立运作无跨模块数据流）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1661-L1680 (§9 Cross-module integration)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1181-L1224 (§2.26 Trust Rings — AgentHive integration)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [cross-module, integration, 15-integrations, contract-testing, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0132: Cross-Module Integration — 15 §9 集成连接实现与集成测试

## 1. 任务目标

实现 Budget Enforcer 与蓝图 §9 定义的全部 15 条集成的连接。每集成有明确的 integration contract（数据流向/调用频率/fallback 模式）。另附 1 条补充集成（MOD-INF-021 AgentHive，来源蓝图 §2.26）。包含 startup health check 显示所有集成点的连通状态。

## 2. 背景

蓝图 §9（Cross-module integration）定义 15 条集成（从 MOD-INF-001 到 MOD-INF-014），涵盖从 Capacity Assurance、Context Engine、Task System 到 LLM Security Gateway 的全景连接。蓝图 §2.26 补充 AgentHive 集成要求。

## 3. 实施步骤

```python
class CrossModuleIntegrator:
    CONTRACTS = {
        "MOD-INF-001": {"section": "§9 row 1", "direction": "bidi", "trigger": "Kill Switch / Degradation"},
        "MOD-INF-008": {"section": "§9 row 2", "direction": "in", "trigger": "L3 compress / waste > 60%"},
        "MOD-INF-006": {"section": "§9 row 3", "direction": "in", "trigger": "task budget / status change"},
        "MOD-INF-020": {"section": "§9 row 4", "direction": "out", "trigger": "降级/熔断/Borrow/Abort"},
        "MOD-INF-022": {"section": "§9 row 5", "direction": "out", "trigger": "硬停止 / Kill Switch"},
        "MOD-INF-023": {"section": "§9 row 6", "direction": "bidi", "trigger": "配置漂移检测"},
        "MOD-MASTER-001": {"section": "§9 row 7", "direction": "in", "trigger": "task.urgency=low"},
        "Git-Precommit": {"section": "§9 row 8", "direction": "hook", "trigger": "git commit"},
        "LiteLLM-Registry": {"section": "§9 row 9", "direction": "in", "trigger": "daily sync"},
        "LiteLLM-Pricing": {"section": "§9 row 10", "direction": "in", "trigger": "pricing strategy delta"},
        "Context-Engine-v2": {"section": "§9 row 11", "direction": "in", "trigger": "history tax / instruction bloat"},
        "SUPERVISORAGENT": {"section": "§9 row 12", "direction": "in", "trigger": "LLM-free phase upgrade"},
        "Provenance-DAG": {"section": "§9 row 13", "direction": "out", "trigger": "agent output claims"},
        "Agent-Delegation": {"section": "§9 row 14", "direction": "out", "trigger": "agent-to-agent call"},
        "MOD-INF-014": {"section": "§9 row 15", "direction": "bidi", "trigger": "IPI / signature / ring"},
        "MOD-INF-021": {"section": "§2.26 Trust Rings", "direction": "bidi", "trigger": "agent creation / delegation budget"},
    }

    def health_check(self) -> IntegrationHealth:
        statuses = {}
        for module_id, contract in self.CONTRACTS.items():
            statuses[module_id] = self._check_module(module_id, contract)
        return IntegrationHealth(statuses)

    def startup_show(self, health: IntegrationHealth):
        ok = sum(1 for v in health.statuses.values() if v.ok)
        total = len(self.CONTRACTS)
        print(f"Budget Enforcer → [{ok} of {total} OK]")
        for mod, status in health.statuses.items():
            icon = "✓" if status.ok else "✗"
            print(f"  {icon} {mod}: {status.detail}")
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/cross_module_integration.py` | 新建 |
| 2 | `src/zephyr/budget_enforcer/test_cross_module_integration.py` | 新建 |
