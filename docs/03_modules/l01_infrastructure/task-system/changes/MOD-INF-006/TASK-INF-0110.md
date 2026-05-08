---
task_id: "TASK-INF-0110"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §1.2 目标 #7/#8 + 盲点 #21/#22/#23/#24/#25"

title: "实现 1 人 + AI 维护特需——零配置 + Dogfooding + 渐进增强 + AI 维护手册 + AI 自治 + 跨 Session"
description: |
  实现零配置启动——`task-cli init` 自动创建 SQLite + 注册表 + changes/ 骨架。
  Dogfooding ——用任务卡系统管理任务卡系统自身的施工（约束 #7）。
  渐进增强——按 Scope 优先级实施，低优先级可降级为骨架。
  AI 维护手册——AI 可自主读取的故障排查、诊断、回滚步骤。
  AI 自治等级——按 supervisory_rules 根据 AISelfGovernanceLevel 决定绕过/警告/阻塞。
  跨 Session 上下文复用——thinking_state_json 保存 + context_cache_key 索引（约束 #28/#38）。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\ai\\governance-ai-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\zero_config.py"
    description: "ZeroConfig——零配置初始化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\dogfooding.py"
    description: "Dogfooding——任务系统自管理"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\autonomy.py"
    description: "AIAutonomy——自治等级 + supervisory_rules 决策"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\ai\\ai-maintenance-handbook.md"
    description: "AI 维护手册——故障排查/诊断/回滚"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\zero_config.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\dogfooding.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\autonomy.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\ai\\ai-maintenance-handbook.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§1.2 目标 #7/#8"
    reason: "1人维护特需目标"
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #7/#28/#38"
    reason: "Dogfooding + 跨Session 约束"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§1.2 目标 #7/#8 + 盲点 #21-#25"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "零配置——task-cli init 自动创建所需目录和 SQLite 文件"
  - "Dogfooding——任务系统自身施工用自身任务卡管理"
  - "AI 自治——autonomous 等级可自动执行非破坏性操作"
  - "维护手册——AI 可自主读取并执行回滚步骤"
  - "跨 Session——thinking_state_json 在会话间可恢复"

rollback_instructions: |
  1. 移除 maintenance/ 目录下新增文件
  2. 删除 ai-maintenance-handbook.md

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
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

# 实现 1 人 + AI 维护特需

## 目标

为 1 人 + AI 维护场景提供基础设施：
1. 零配置启动——一键初始化
2. Dogfooding——任务系统自管理
3. AI 自治等级——按等级决定操作范围
4. AI 维护手册——可自主读取的操作指南
5. 跨 Session 复用——思考态持久化

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）
- task_repo 可用

## 执行步骤

### 做
1. ZeroConfig.init()——创建 SQLite/注册表/changes/
2. Dogfooding——MOD-INF-006 任务卡存放在自身 changes/
3. AIAutonomy——五级自治枚举 + supervisory_rules
4. AI维护手册——故障排查/诊断/回滚

### 产
- maintenance/ 目录 3 文件 + ai-maintenance-handbook.md

### 检
```bash
python -m zephyr.cli.task init --db-path data/tasks.db
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | init 命令成功执行 |
| 2 | files | 所需目录 + SQLite 文件存在 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| Dogfooding 循环依赖——任务系统管理任务系统 | 自举阶段：手工创建第一批任务卡，后续由系统自动管理 |
