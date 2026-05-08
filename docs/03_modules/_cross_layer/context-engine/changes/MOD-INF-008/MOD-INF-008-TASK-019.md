---
task_id: "MOD-INF-008-TASK-019"
task_title: "第十五轮上下文生命线审计落地 — B23-B38 + AP32-AP39 + DD97-DD112 + beta y-ab"
module_id: "MOD-INF-008"
blueprint_section: "§22 第十五轮终端取证 B23-B38 + §22.4 AP32-AP39 + §22.5 DD97-DD112 + §22.6 beta y-ab"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 36
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-017"
    why: "第十五轮在第十三轮基础上扩展时间维度审计"
  - task_id: "MOD-INF-008-TASK-018"
    why: "跨模块契约修补支撑 AtomicInjection 和 CEModeSwitch"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids:
  - "MOD-INF-008-TASK-019A"
  - "MOD-INF-008-TASK-019B"
  - "MOD-INF-008-TASK-019C"
  - "MOD-INF-008-TASK-019D"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_poisoning_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_diff_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ke_inclusion_rationale.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\session_checkpoint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\atomic_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ce_mode_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\complexity_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\injection_position_optimizer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ke_integrity_check.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\domain_decay_config.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\cold_start_warmup.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_fragmentation_index.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\emergency_kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\mcp_ide_adapter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\build_inject_staleness.py"
tags: ["context-engine", "round-15", "lifeline-audit", "running-system", "poisoning", "diff-injection", "atomic"]
acceptance_criteria:
  - "AC-001: B23 毒化无感知: context_poisoning_monitor.py 注入后 30min→追踪 Agent action success_rate; 低成功率 KE 标记 suspect (DD97)"
  - "AC-002: B24 无差异注入: context_diff_injector.py 计算与上次 inject 的 diff→仅注入 delta→锚定前次 inject_id (DD98)"
  - "AC-003: B25 不可解释: ke_inclusion_rationale.py per-KE 结构化决策链→{similarity, keyword, authority, freshness, final_weight} (DD99)"
  - "AC-004: B26 跨Session失忆: session_checkpoint.py session 上下文状态序列化→restore on reconnect→diff 自上次 checkpoint (DD100)"
  - "AC-005: B27 健康分无自动动作: HealthScore<50 持续>30min→自动标识受影响 session→触发 ContextReset (DD101)"
  - "AC-006: B28 领域衰减无差异化: domain_decay_config.py per-domain halflife→freshness=e^(-age/halflife_domain) (DD105)"
  - "AC-007: B29 注入无原子性: atomic_injector.py shadow-then-swap→4 层全部构建→校验→一次性注入 (DD102)"
  - "AC-008: B30 多Agent预算无仲裁: 全局 BudgetPool→加权分配 (priority×task_complexity)→per-agent cap"
  - "AC-009: B31 静态上文明文存储: Confidential+级别 KE 上下文块 AES-256-GCM 加密后落盘"
  - "AC-010: B32 KE 无完整性校验: ke_integrity_check.py SHA-256→存储→检索验证→损坏率月报 (DD106)"
  - "AC-011: B33 CE 无模式感知: ce_mode_manager.py CE_MODE env→全局参数 profile 切换 (DD104)"
  - "AC-012: B34 注入位置未优化: injection_position_optimizer.py primacy/recency 双锚重排 (DD107)"
  - "AC-013: B35 复杂度不感知: complexity_budget.py TaskCard.complexity(1-5)→动态 budget (DD103)"
  - "AC-014: B36 碎片化: context_fragmentation_index.py CI=1-(max_chunk/total)→>0.7 warn (DD108)"
  - "AC-015: B37 冷启动: cold_start_warmup.py 异步预热→preload models→warm_up_complete signal (DD109)"
  - "AC-016: B38 紧急熔断: emergency_kill_switch.py /ce:kill→停止新注入→标记 CE_KILLED (DD110)"
  - "AC-017: DD111 MCP IDE 适配器 + DD112 Build-Inject Staleness: mcp_ide_adapter.py + build_inject_staleness.py"
rollback_instructions: "删除 beta y-ab 所有新增文件和升级代码"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §22"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-019: 第十五轮上下文生命线审计落地

## 1. Purpose

将第十五轮终端取证（Context-As-Living-System 生命线审计）发现的 16 个时间维度盲点落地，补齐 CE 作为"活的运行时服务"的全生命周期缺口。

## 2. Blindspot Summary B23-B38

| 类别 | 数量 | 严重度 |
|------|:---:|------|
| P0 | 5 (B23, B24, B25, B26, B27) | 上下文毒化/无差异/不可解释/跨Session/健康分无动作 |
| P1 | 8 (B28-B35) | 领域衰减/无原子性/多Agent仲裁/明文存储/无校验/无模式感知/位置未优化/复杂度不感知 |
| P2 | 3 (B36-B38) | 碎片化/冷启动/紧急熔断 |

## 3. beta y (4 Files) — 生命线基座

context_poisoning_monitor + context_diff_injector + ke_inclusion_rationale + session_checkpoint

## 4. beta z (6 Files) — 原子性与自适应

atomic_injector + ce_mode_manager + complexity_budget + injection_position_optimizer + ke_integrity_check + domain_decay_config

## 5. beta aa (5 Files) — 运维生存

cold_start_warmup + context_fragmentation_index + emergency_kill_switch + mcp_ide_adapter + build_inject_staleness

## 6. beta ab (3 Files) — 氛围编程集成

ce_playground_v2 + ce_explain_cli + ce_vibe_shortcuts (部分在 TASK-016 中)

## 7. Acceptance Criteria

- 15 个新文件全部创建
- 5 个 P0 盲点功能可单元测试验证
- context_poisoning_monitor 可检测低成功率 KE
- context_diff_injector 可计算并注入增量 diff
- atomic_injector 的 shadow-then-swap 保证 4 层全或无
- emergency_kill_switch 的 /ce:kill 可在 <1s 内停止所有新注入
