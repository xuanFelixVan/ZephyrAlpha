---
task_id: "TASK-INF-0101"
module_id: "MOD-INF-024"
title: "Module Skeleton + Directory Structure + budget_policy.yaml（§1 + §2.1 + §3 + §4）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§1.1 + §2.1 + §3 + §4"
estimated_tokens: 2000
estimated_time_minutes: 45
owner_signal_required: false
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy_history\\"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_overrides.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_profile_manager.py"
acceptance_criteria:
  - "AC-01: src/zephyr/budget_enforcer/ 目录存在且包含 __init__.py，其 docstring 声明轨道归属（B轨/cross_layer）和架构真源（blueprint.md 路径）"
  - "AC-02: config/budget_policy.yaml 存在，结构完整覆盖 §2.1 七级预算体系所有字段（global/session/workflow/task/turn/request/self_budget）"
  - "AC-03: budget_policy.yaml 中每个 level 均包含 soft_limit、hard_limit、action_on_soft_exceed、action_on_hard_exceed、reset 五个必填字段"
  - "AC-04: budget_policy.yaml 包含 time_budget 三维配置（request_timeout 120s / turn_timeout 300s / task_timeout 3600s / session_timeout 28800s）"
  - "AC-05: budget_policy.yaml 包含 borrow_pool、pool_share、cross_session_savings、per_agent_sub_pool、cold_start_allowance 完整结构"
  - "AC-06: config/budget_overrides.yaml 存在骨架——Owner 手动覆盖预算阈值的通道"
  - "AC-07: config/budget_policy_history/ 目录存在——为 Policy Versioning 提供存储空间"
  - "AC-08: budget_profile_manager.py 骨架存在——ENV Profile 切换逻辑（dev/staging/prod 三套策略映射）"
  - "AC-09: 所有新建文件使用 UTF-8 编码（encoding='utf-8'）"
  - "AC-10: budget_policy.yaml 顶部注释标注 "Budget Policy as Code — MOD-INF-024 唯一策略真源。修改须 Ed25519 签名验证""
rollback_instructions: "删除 src/zephyr/budget_enforcer/ 目录及其所有内容即可完全回滚——此阶段仅创建骨架文件，无运行时依赖"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1-L28 (frontmatter + module identity)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L30-L138 (§1.1-§1.3 + §2.1 five-level budget + time_budget)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1356-L1417 (§3 Solo Maintainer)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1421-L1455 (§4 File composition)"
  fallback:
    - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md#L189-L193 (budget_enforcer/ path in src/zephyr)"
assigned_agent: any
tags: [module-skeleton, budget-policy, directory-structure, scaffold, config]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0101: Module Skeleton + Directory Structure + budget_policy.yaml

## 1. 任务目标

创建 MOD-INF-024 Budget Enforcer 模块的完整骨架——源代码目录、配置文件、策略 YAML 初始化。这是所有后续 Phase 任务卡的前置基础。

## 2. 背景

蓝图 §1.1 定义 module_id=MOD-INF-024，代码落位 `src/zephyr/budget_enforcer/`，运行时平面 Hot memory。蓝图 §2.1 定义七级预算体系（global→session→workflow→task→turn→request→self_budget）含 Token/Cost/Time 三维。蓝图 §3 定义 Solo Maintainer 优化（自学习阈值、自静默告警、周自动摘要）。蓝图 §4 列出 30 个源文件和 3 个配置文件。

## 3. 实施步骤

### Step 1: 创建源码目录骨架
```
src/zephyr/budget_enforcer/
├── __init__.py           # 模块入口——声明 B轨/cross_layer 归属 + blueprint.md 路径
├── config/
│   ├── budget_policy.yaml      # 七级预算策略唯一真源（Policy as Code）
│   ├── budget_policy_history/   # 策略版本历史存储
│   └── budget_overrides.yaml   # Owner 手动锁定阈值
└── budget_profile_manager.py   # ENV Profile 切换逻辑骨架
```

### Step 2: 实现 __init__.py
- 顶层 docstring 声明模块信息：module_id、layer、blueprint 路径、架构对标
- 导入 L0 logging 配置

### Step 3: 编写 budget_policy.yaml
- 完整翻译 §2.1 的 7 级预算 YAML 结构
- 每级包含：description, soft_limit, hard_limit, action_on_soft_exceed, action_on_hard_exceed, reset
- 维度：token + cost + time（time_budget 独立章节）
- 包含：borrow_pool, pool_share, cross_session_savings, per_agent_sub_pool, cold_start_allowance
- 顶部注释标注签名验证要求

### Step 4: 编写 budget_overrides.yaml 骨架
- 结构：{budget_level: {parameter: {value, locked_by, locked_at}}}

### Step 5: 编写 budget_profile_manager.py 骨架
- 类 BudgetProfileManager
- 方法：detect_env() → "development"|"staging"|"production"
- 方法：get_profile(env) → profile dict
- 方法：validate_profile_switch(from_env, to_env) → bool

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/__init__.py` | 新建 |
| 2 | `src/zephyr/budget_enforcer/config/budget_policy.yaml` | 新建 |
| 3 | `src/zephyr/budget_enforcer/config/budget_policy_history/.gitkeep` | 新建 |
| 4 | `src/zephyr/budget_enforcer/config/budget_overrides.yaml` | 新建 |
| 5 | `src/zephyr/budget_enforcer/budget_profile_manager.py` | 新建 |
