---
task_id: "TASK-INF-0114"
module_id: "MOD-INF-024"
title: "ENV Profile Manager — dev/staging/prod 三套预算策略自动切换 + Dev Trap Protection（§2.15 + D-024-13）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.15"
estimated_tokens: 3500
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_profile_manager.py"
acceptance_criteria:
  - "AC-01: BudgetProfileManager 三套 Profile：development(default tier_0_free, daily $1, task $0.10), staging(tier_1_cheap, daily $5, task $0.50), production(tier_1_cheap, tier_3 max, daily $10, task $1.00)"
  - "AC-02: 环境检测——ZEPHYR_ENV 环境变量优先，fallback 自动检测（IDE → dev, CI → staging, deployed → prod）"
  - "AC-03: Dev Trap Protection——每次新 Task 自动重置到当前 Profile 的 default_model_tier（防止手动切换到 Tier-3 后遗忘）"
  - "AC-04: persistent_override——'zephyr env override-production' 命令切换（需二次确认 Y/N）"
  - "AC-05: profile 切换写入 audit trail——记录 from_profile, to_profile, reason, timestamp"
  - "AC-06: 跨 Profile 切换时自动 re-evaluate 所有活跃 BudgetCounter 的 soft_limit/hard_limit"
  - "AC-07: dev 环境永久哨兵——即使被 override，每 30 分钟自动检查一次当前环境是否匹配 profile"
  - "AC-08: get_current_profile() → Profile 快照——包含所有 limits + 当前消耗 + remaining"
rollback_instructions: "删除 budget_profile_manager.py，移除所有调用。系统退化为无环境感知——所有环境使用统一默认 budget_policy（可能导致 dev 烧生产预算）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L806-L847 (§2.15 ENV Profile)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [env-profile, dev-staging-prod, budget-strategy, trap-protection, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0114: ENV Profile Manager — 环境感知预算策略自动切换

## 1. 任务目标

实现基于环境变量的三套预算策略自动切换——dev 永远只用免费模型（防调试时烧预算），staging 允许标准模型验证质量，production 开放全能力但有日/任务成本硬顶。此功能对 Solo Maintainer 最关键——"不小心在 dev 调试时烧掉一周预算"是单人维护模式的最大风险。

## 2. 背景

蓝图 §2.15（决策 D-024-13，v0.4.0 新增）：业界标准实践——dev 环境只用最便宜模型，prod 才开全能力。Solo maintainer 环境切换混乱是隐性成本的重要来源。

## 3. 实施步骤

### Step 1: Profile 定义
```python
@dataclass
class EnvProfile:
    name: str  # "development" | "staging" | "production"
    default_model_tier: int
    max_model_tier: int
    daily_cost_cap: float
    task_cost_cap: float
    cache_enabled: bool
    audit_level: str  # "minimal" | "standard" | "full"

class EnvProfiles:
    PROFILES = {
        "development": EnvProfile("development", 0, 1, 1.00, 0.10, True, "minimal"),
        "staging": EnvProfile("staging", 1, 2, 5.00, 0.50, True, "standard"),
        "production": EnvProfile("production", 1, 3, 10.00, 1.00, True, "full"),
    }
```

### Step 2: BudgetProfileManager
```python
class BudgetProfileManager:
    def __init__(self, policy: dict, tracker: BudgetTracker):
        self.current_profile: str = self._detect_env()
        self.override: str | None = None
        self._sentry = SentryCheck(interval=1800)

    def _detect_env(self) -> str:
        env = os.environ.get("ZEPHYR_ENV")
        if env: return env
        # IDE detection heuristics
        if "TRAE" in os.environ or "CURSOR" in os.environ:
            return "development"
        if "CI" in os.environ:
            return "staging"
        return "production"

    def get_active_profile(self) -> EnvProfile:
        profile_name = self.override or self.current_profile
        return EnvProfiles.PROFILES[profile_name]

    def on_new_task(self):
        # 重置 model tier 到 default——Dev Trap Protection
```

### Step 4: Dev Trap Protection
- on_new_task() 事件自动触发 default_tier 重置
- override 需要二次确认 + 写入 audit
- sentry 线程每 30 分钟检查当前实际环境 vs active profile

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/budget_profile_manager.py` | 新建（替代骨架） |
