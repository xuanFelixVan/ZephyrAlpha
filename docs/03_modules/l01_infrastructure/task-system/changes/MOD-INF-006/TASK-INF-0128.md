---
task_id: "TASK-INF-0128"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §12 源码文件 8项 + 测试文件 6项"

title: "实现全量测试覆盖——6测试文件 + 8源码文件覆盖"
description: |
  按蓝图 §12 的 6 测试文件路径索引实现全量测试。
  8 源码文件索引验证——确认声明路径与磁盘一致性。
  单元测试——core/models.py / lifecycle / dependency / reliability / observability。
  集成测试——M1-M11 全链路 + pipeline + integration targets。
  测试覆盖率 ≥ 80%。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\task_manager_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\dependency\\dependency_graph.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\**\\*.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\unit\\core\\test_models.py"
    description: "TaskCard 模型 62字段单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\core\\test_lifecycle.py"
    description: "TaskLifecycleManager 状态机 + 门禁测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\core\\test_dependency.py"
    description: "DependencyGraph 拓扑排序 + 循环检测测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\core\\test_reliability.py"
    description: "CircuitBreaker/Retry/ContextGuard 测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\core\\test_observability.py"
    description: "Trace/CostTracker/FailureMatcher 测试"
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_pipeline_e2e.py"
    description: "M1-M11 全链路端到端测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\unit\\core\\test_models.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\core\\test_lifecycle.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\core\\test_dependency.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\core\\test_reliability.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\core\\test_observability.py"
  - "D:\\ZephyrAlpha\\tests\\integration\\test_pipeline_e2e.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§12"
    reason: "源码文件 + 测试文件索引——SSoT"
  - module_id: "GOV-AI-002"
    section: "§5"
    reason: "验收标准——覆盖率≥80%"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§12 源码路径索引 + §3 接口契约——测试依据"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 25000
timeout_minutes: 120

acceptance_criteria:
  - "6 个测试文件全部创建且可执行"
  - "覆盖率 ≥ 80%——pytest-cov 报告确认"
  - "所有 8 个源码文件（models/decomposer/mcp/lifecycle/dependency/reliability/observability/healthcheck）有测试覆盖"
  - "test_pipeline_e2e.py 端到端测试通过"
  - "测试不修改任何源码——仅读取+断言"

rollback_instructions: |
  1. 删除新增的 6 个测试文件

depends_on: ["TASK-INF-0102", "TASK-INF-0103", "TASK-INF-0104", "TASK-INF-0106"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "test"
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

# 实现全量测试覆盖——6测试 + 8源码

## 目标

按蓝图 §12 声明编写完整测试套件：
- 6个测试文件：5单元 + 1集成
- 覆盖全部 8个源码文件
- 覆盖率 ≥ 80%

## 触发条件

- TASK-INF-0102/0103/0104/0106 完成

## 执行步骤

### 做
1. test_models.py——TaskCard 62字段模型验证
2. test_lifecycle.py——G0-G7 门禁 + 状态机
3. test_dependency.py——拓扑排序 + 循环
4. test_reliability.py——断路器 + Retry + 上下文保护
5. test_observability.py——Trace + 成本 + 失败匹配
6. test_pipeline_e2e.py——M1-M11 全链路

### 产
- tests/ 目录 6 个测试文件

### 检
```bash
pytest tests/ -v --cov=src/zephyr/core --cov-report=term
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | test | 6个文件全量通过 |
| 2 | coverage | ≥ 80% |
