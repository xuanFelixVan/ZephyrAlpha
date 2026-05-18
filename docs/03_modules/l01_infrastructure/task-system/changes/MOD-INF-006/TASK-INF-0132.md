---
task_id: "TASK-INF-0132"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §13.3 路线图 v0.5.0 规划项 — #4 #9 #26 #27"

title: "实现 v0.5.0 路线图遗留四项——DraftAssistant + Hook 事件 + 任务队列 + KMS 接口"
description: |
  实现蓝图 §13.3 优先级路线图中标记为 v0.5.0 但尚未在 §4.1 约束中正式化的四项：
  #4 Hook 事件系统（任务状态变更 → 外部回调触发——MTH-015 模板预留但需实现）；
  #9 主动任务队列/轮询（TaskQueue 后台轮询器——每 N 分钟扫描 READY 任务，AI 自治允许时自动 dispatch）；
  #26 DraftAssistant 蓝图草稿入口（输入想法 → MTH-012 格式蓝图骨架 → Owner 填充 → 涌现式血肉补全）；
  #27 KMS 知识管理接口契约（§3 新增 §3.2.3——KE 推送格式 + KE 生命周期与 TaskCard 状态关联表）。
  本卡作为 v0.5.0 施工收尾的统一收敛点。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\MTH-012\\blueprint-construction-template.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\MTH-015\\hook-template.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\pipeline\\pipeline_orchestrator.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\task-card-meta-registry.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\events\\hook_dispatcher.py"
    description: "HookDispatcher——任务状态变更 → 外部回调"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\queue\\task_queue.py"
    description: "TaskQueue——后台轮询 + auto-dispatch"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\draft\\draft_assistant.py"
    description: "DraftAssistant——想法 → 蓝图骨架生成"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\knowledge\\kms_interface.py"
    description: "KMSInterface——KE 推送契约 + 生命周期关联"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\events\\hook_dispatcher.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\queue\\task_queue.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\draft\\draft_assistant.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\knowledge\\kms_interface.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§13.3 路线图"
    reason: "#4/#9/#26/#27 均为 v0.5.0 路线图规划项——P3/P2 优先级"
  - module_id: "PS-STD-001"
    section: "§7.4"
    reason: "ke_entries 字段——与 KMS 接口关联"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§13.3 路线图——#4/#9/#26/#27 四项 v0.5.0 目标 + 盲点详细登记"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M4"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "HookDispatcher——状态变更回调可配置（MTH-015 模板）"
  - "TaskQueue——后台轮询间隔可配置 + auto_dispatch 模式正确"
  - "DraftAssistant——输入想法 → 产生 MTH-012 格式蓝图骨架（含目标/边界/约束预填）"
  - "KMSInterface——KE 推送格式定义（{task_id, ke_type, content_snippet, source_file, priority}）"
  - "四项均可独立启用/禁用——通过 config/pipeline_modules.yaml 控制"

rollback_instructions: |
  1. 移除 events/queue/draft/knowledge 四个新目录下的文件
  2. 移除 pipeline_modules.yaml 中新增的四条模块配置

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "roadmap"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 实现 v0.5.0 路线图遗留项——DraftAssistant + Hook + 队列 + KMS

## 目标

收敛蓝图 §13.3 路线图中标记为 v0.5.0 但尚未有 §4.1 硬约束的四项：
1. **Hook 事件系统 (#4)**——任务状态变更→外部回调
2. **主动任务队列 (#9)**——后台轮询 + 自动 dispatch
3. **DraftAssistant (#26)**——想法→蓝图骨架
4. **KMS 接口契约 (#27)**——KE 推送契约

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. HookDispatcher——MTH-015 模板实现
2. TaskQueue——轮询扫描 + auto_dispatch
3. DraftAssistant——MTH-012 格式蓝图骨架生成
4. KMSInterface——KE 推送格式契约

### 产
- 4 个新文件

### 检
```bash
pytest tests/unit/core/ -v -k "hook or queue or draft or kms"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | 4 模块可独立 import |
| 2 | test | 各有单元测试覆盖 |
| 3 | config | pipeline_modules.yaml 含 4 条新模块配置 |
