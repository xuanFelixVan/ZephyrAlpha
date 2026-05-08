---
task_id: "MOD-INF-008-TASK-009"
task_title: "Anti-Patterns AP1-AP7 防护机制实现"
module_id: "MOD-INF-008"
blueprint_section: "§7 Anti-Patterns AP1-AP7"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 6
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-004"
    why: "AP1, AP5 依赖 Validate 阶段"
  - task_id: "MOD-INF-008-TASK-003"
    why: "AP2 依赖 Compress 阶段"
  - task_id: "MOD-INF-008-TASK-005"
    why: "AP3 依赖 Inject 阶段"
  - task_id: "MOD-INF-008-TASK-002"
    why: "AP4 依赖 Build 阶段"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
tags: ["context-engine", "anti-patterns", "guardrails", "safety", "protection"]
acceptance_criteria:
  - "AC-001: AP1 防护: inject() 注入前必须通过 CT-CE-LSG-001 三层审查——添加 pre-inject safety gate"
  - "AC-002: AP2 防护: compress() 永远保留 raw_text——输出 CompressedContext(compressed, raw) 双字段"
  - "AC-003: AP3 防护: inject() 实现结构化分层注入 Layer1→4，禁止 flat concat——添加结构验证断言"
  - "AC-004: AP4 防护: build() 实现同 session_id+同 query 缓存，TTL=5min——添加 LRU cache 装饰器"
  - "AC-005: AP5 防护: VALIDATE-C01 条件对 context.sources 做 os.path.exists() 验证——添加路径存在性检查"
  - "AC-006: AP6 防护: KE 排序使用 Freshness Decay 公式：created_at 越新→权重越高——实现加权函数"
  - "AC-007: AP7 防护: L3_HARD_STOP 时拒绝追加 context，仅保留 Always-on——添加硬截断守卫"
rollback_instructions: "移除各文件中的 AP 防护代码，恢复到无防护状态"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §7"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-009: Anti-Patterns AP1-AP7 防护

## 1. Purpose

在代码中实现 §7 定义的 7 条反模式防护机制，确保 AI agent 不能执行以下禁止的上下文操作。

## 2. AP Protection Implementation

| # | Anti-Pattern | 防护代码 |
|---|-------------|---------|
| AP1 | 无 LSG 审查直接注入 | `inject()` 入口添加 `assert context.lsg_passed` |
| AP2 | compress 丢弃 raw_text | `CompressedContext` 类必须同时含 `compressed_text` + `raw_text` |
| AP3 | Flat string concat 注入 | `format_context()` 按 Layer1-4 结构化输出 |
| AP4 | 重复查 VMS | `@lru_cache(maxsize=128)` 或 `session_cache[query_hash]` |
| AP5 | 注入不存在文件路径 | `VALIDATE-C01: os.path.exists(source)` |
| AP6 | 旧 KE 与新 KE 权重相同 | `freshness_weight = exp(-age_days / half_life)` |
| AP7 | Token 预算耗尽后强行注入 | `if budget > L3_HARD_STOP: return AlwaysOnOnly` |

## 3. Acceptance Criteria

- AP1: 注释 inject() 中的 lsg_passed 断言 → 测试失败
- AP2: CompressedContext 无 raw_text → 类型检查失败
- AP3: format_context() 输出含 "Layer1:", "Layer2:", ... 标记
- AP4: 同一 query 两次 build() → 第二次命中缓存
- AP5: 注入不存在的路径 → 触发 auto_fix (移除 source)
- AP6: 2 天前的 KE 权重 < 1 天前的 KE 权重
- AP7: 预算 7601 tokens → 不再追加 context
