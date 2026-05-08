---
task_id: "TASK-INF-0115"
module_id: "MOD-INF-024"
title: "Budget Policy Sandbox + Policy Versioning — Dry-run 模拟四场景 + 版本回滚/diff（§2.16 + D-024-14）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: sandbox
blueprint_section: "§2.16"
estimated_tokens: 4500
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0103"
  - "TASK-INF-0105"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\pre_flight_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\policy_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy_history\\"
acceptance_criteria:
  - "AC-01: PolicySandbox 四个场景完整：low_complexity(20 lint tasks→tier_0 zero cost), medium_load(50 mixed tasks), budget_exhaustion(100 refactor→L5_halt), runaway_agent(10 tasks→sub-pool limit)"
  - "AC-02: Sandbox 不实际调用 AI——使用模拟 token estimator + mock provider responses"
  - "AC-03: 每个场景输出结构化报告——各等级触发次数、降级链路径、是否正确退出"
  - "AC-04: sandbox 执行后生成 budget_sandbox_report.md——通过/警告/失败 checklist"
  - "AC-05: Policy Versioning——每次 git commit 自动快照 budget_policy.yaml 到 config/budget_policy_history/{version}/"
  - "AC-06: rollback 命令——'zephyr budget policy rollback --version v{N}' 恢复到指定版本"
  - "AC-07: diff 命令——'zephyr budget policy diff --v1 v2' 对比两版本差异"
  - "AC-08: auto_version hook——pre-commit 钩子中调用 snapshot 函数"
  - "AC-09: Sandbox 支持 custom scenario——用户可以定义自定义模拟场景 YAML"
  - "AC-10: Policy 变更后自动触发 sandbox（git hook 中 dry-run）——验证通过才允许 commit"
rollback_instructions: "删除 policy_sandbox.py + budget_policy_history/ 目录。系统退化为无沙盘验证——策略变更直接上线，无 dry-run 保护"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L850-L891 (§2.16 Policy Sandbox + Versioning)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [policy-sandbox, dry-run, scenario-simulation, policy-versioning, rollback, sandbox]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0115: Budget Policy Sandbox + Policy Versioning

## 1. 任务目标

实现预算策略的沙盘验证系统和版本管理——任何对 budget_policy.yaml 的修改上线前必须通过 4 个模拟场景的 dry-run，确保不会把系统卡死。策略版本管理支持一键回滚和 diff 对比。

## 2. 背景

蓝图 §2.16（决策 D-024-14，v0.4.0 新增）：预算策略上线前不验证 = 拿生产环境当试验田。四场景覆盖从轻量到极端的完整风险谱。对标 GitOps 的 policy-as-code + versioned infrastructure 实践。

## 3. 实施步骤

### Step 1: Scenario Runner
```python
@dataclass
class SandboxScenario:
    name: str
    task_count: int
    task_type: str
    budget_initial: int
    expected_path: list[str]  # 预期触发的事件序列

class SandboxRunner:
    def run(self, scenario: SandboxScenario,
            policy: dict) -> SandboxResult:
        # 创建模拟 BudgetTracker + PreFlightGate + DegradationManager
        # 按 scenario 定义运行模拟任务
        # 记录所有事件 → SandboxResult
```

### Step 2: Four Default Scenarios
- `low_complexity`: 20 lint_fix tasks — 验证 tier_0 路由
- `medium_load`: 50 mixed — 验证正常 escalated flow
- `budget_exhaustion`: 100 heavy_refactor — 验证 L5_halt + 无 spiral
- `runaway_agent`: 10 runaway — 验证 sub-pool + global pool cap

### Step 3: PolicyVersionManager
```python
class PolicyVersionManager:
    HISTORY_DIR = "config/budget_policy_history"

    def snapshot(self) -> str:
        version = self._next_version()
        dest = f"{self.HISTORY_DIR}/{version}/budget_policy.yaml"
        shutil.copy2("config/budget_policy.yaml", dest)
        return version

    def rollback(self, version: str):
        src = f"{self.HISTORY_DIR}/{version}/budget_policy.yaml"
        shutil.copy2(src, "config/budget_policy.yaml")

    def diff(self, v1: str, v2: str) -> str:
        # unified diff of two policy versions
```

### Step 4: Pre-commit Integration
- Hook: detect budget_policy.yaml staged → auto sandbox + auto snapshot
- Sandbox fail → block commit, output report
- Sandbox pass → allow commit + record snapshot version

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/policy_sandbox.py` | 新建 |
