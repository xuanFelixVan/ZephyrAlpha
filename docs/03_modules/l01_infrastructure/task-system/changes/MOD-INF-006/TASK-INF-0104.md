---
task_id: "TASK-INF-0104"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §11.3 步骤5 — 重写 task_manager_server.py"

title: "重写 task_manager_server.py — MCP 接入 SQLite（6 Tool + 双轨同步）"
description: |
  重写 `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py`。
  MCP Server 必须初始化 task_repo 连接（SQLite），禁止使用内存 dict 作为任务存储。
  实现 6 个 Tool：decompose_blueprint / create_task / update_task_status / get_task /
  register_from_triage / sync_file_state。
  每个 Tool 对接 task_repo 真源。transition() 成功后自动同步 .md 副本。
  实现 _taskcard_to_md() 生成人类可读副本。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\task_manager_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\task-card-template.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\tool_contracts.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\task_manager_server.py"
    description: "MCP Server——6 Tool + task_repo 初始化 + .md 双轨同步"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\tool_contracts.yaml"
    description: "6 Tool 输入/输出 Schema + 错误码契约"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\task_manager_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\tool_contracts.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§3.5"
    reason: "MCP 接口——5 Tool + register_from_triage + sync_file_state 输入/输出定义"
  - module_id: "MOD-INF-006"
    section: "§3.3-§3.4"
    reason: "输入契约 / 输出契约——错误码规范"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§3.5 MCP 接口 Tool 表格 + §3.3 输入契约 + §3.4 输出契约"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
    reason: "task_repo 完整 API——MCP 对接目标"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
    reason: "decompose_blueprint Tool 的调用目标"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M4"
estimated_tokens: 25000
timeout_minutes: 90

acceptance_criteria:
  - "MCP Server 初始化时 task_repo 连接成功——repo.health_check() 通过"
  - "禁止使用内存 dict 作为任务存储——list_tasks() 返回 SQLite 中的数据"
  - "6 个 Tool 全部注册：decompose_blueprint / create_task / update_task_status / get_task / register_from_triage / sync_file_state"
  - "decompose_blueprint Tool 调用 BlueprintDecomposer.decompose()——写入 SQLite"
  - "create_task Tool：G0+G7 门禁 + task_repo.create() + .md 同步"
  - "update_task_status Tool：状态机转换 + task_repo.transition() + .md 同步"
  - "sync_file_state() 可检测 .md 副本与 SQLite 状态是否一致"
  - "错误码覆盖：TASK_NOT_FOUND(404) / STATUS_MISMATCH(409) / ILLEGAL_TRANSITION(422) / GATE_BLOCKED(422) / VALIDATION_ERROR(400) / PATH_NOT_COMPLIANT(422) / REPO_NOT_INJECTED(500)"

rollback_instructions: |
  1. 恢复 `task_manager_server.py` 为旧版 4 Tool（内存 dict 存储）
  2. 恢复 `tool_contracts.yaml` 为旧版契约
  3. 确认旧的 4 个 Tool 正常工作后再切回新版

depends_on: ["TASK-INF-0102", "TASK-INF-0103"]
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

# 重写 task_manager_server.py — MCP 6 Tool + SQLite

## 目标

重写 MCP Server 为完全基于 SQLite task_repo 的架构：
1. 初始化时注入 TaskRepo 实例——所有 Tool 操作走 SQLite
2. 实现 6 个 Tool 覆盖完整的任务卡生命周期
3. 每个写入操作后自动 .md 双轨同步
4. tool_contracts.yaml 定义所有 Tool 的输入/输出 Schema

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）
- blueprint_decomposer.py 重写完成（TASK-INF-0103）
- task_repo.py 可用

## 执行步骤

### 读
- task_repo.py 完整 API
- 蓝图 §3.5 MCP 接口定义
- core/models.py / blueprint_decomposer.py 新接口

### 做
1. 实现 `initialize_task_repo()` ——从数据库路径初始化 TaskRepo
2. 注册 6 个 Tool：
   - `decompose_blueprint` → 调用 BlueprintDecomposer.decompose()
   - `create_task` → G0+G7 + task_repo.create() + .md
   - `update_task_status` → 状态机 + task_repo.transition() + .md
   - `get_task` → task_repo.get()
   - `register_from_triage` → 从审阅池创建任务
   - `sync_file_state` → 检测 .md vs SQLite 一致性
3. 实现 `_taskcard_to_md()` ——按 TEMPLATE-TASK-001 格式生成 .md
4. 更新 tool_contracts.yaml

### 产
- `task_manager_server.py` + `tool_contracts.yaml`

### 检
```bash
pytest tests/unit/test_mcp_servers.py -v -k task_manager
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | MCP Server 启动无错误 |
| 2 | lint | 0 errors, 0 warnings |
| 3 | files | tool_contracts.yaml 含 6 Tool 定义 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| task_repo 初始化失败 | 健康检查 + 明确错误信息——REPO_NOT_INJECTED(500) |
| .md 同步失败不影响主流程 | .md 写失败 → 仅记录 WARNING，不阻塞 SQLite 操作 |
