---
task_id: TASK-INF-0108
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: implementation
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §5.2
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g1_pre_exec.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g2_resource.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g3_env.py
acceptance_criteria:
  - "AC1: G1_GATE_YAML 定义 gate_name='Task-G1: Pre-execution Readiness'、gate_level='G1'、required_context=['upstream_files']、check_method='validate_file_existence'"
  - "AC2: G2_GATE_YAML 定义 gate_name='Task-G2: Resource Quota'、gate_level='G2'、required_context=['token_budget']、check_method='check_token_quota'、threshold=max_tokens_per_task=100000"
  - "AC3: G3_GATE_YAML 定义 gate_name='Task-G3: Environment Integrity'、gate_level='G3'、required_context=['runtime_environ']、check_method='validate_runtime'、min_python='3.12'、min_disk_gb=1"
  - "AC4: G1 检查 upstream_files 中每条路径 disk.exists()、G2 按 DD4 动态阈值、G3 检查 sys.version_info+shutil+subprocess['powershell']"
rollback_instructions:
  - "g1_pre_exec.py/g2_resource.py/g3_env.py→空桩→check_all() 返回 GateResult.PASSED"
created_at: 2026-05-06T23:42:00Z
updated_at: 2026-05-06T23:42:00Z
closed_at: null
dependencies:
  - TASK-INF-0102
  - TASK-INF-0104
blocked_by: [TASK-INF-0102, TASK-INF-0104]
blocks: []
tags: [gate-engine, G1, G2, G3, pre-execution]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §5.2 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§5.2 G1-G3 预执行门控"]
  keywords: [G1, G2, G3, file-existence, token-quota, environment-check]
  ai_reads_for_inference: true
---

# TASK-INF-0108: G1-G3 预执行门控结构化 YAML 规则落地

## 背景与动机

G1-G3 是任务执行前的预检门控（blueprint.md §5.2）：G1 验证上游文件存在、G2 验证 token 配额、G3 验证运行时环境。三道门逐一放行后任务才进入执行阶段。

## 实施计划

G1-G3 各以 YAML 结构化配置定义规则，然后 Python Gate 类实现。

### G1: Pre-execution Readiness

```yaml
gate_name: "Task-G1: Pre-execution Readiness"
gate_level: "G1"
required_context: ["upstream_files"]
check_method: "validate_file_existence"
```

实现：遍历 `task_dict["upstream_files"]` → `os.path.exists(fp)` → 任一不存在→BLOCKED。

### G2: Resource Quota

```yaml
gate_name: "Task-G2: Resource Quota"
gate_level: "G2"
required_context: ["token_budget"]
check_method: "check_token_quota"
threshold:
  max_tokens_per_task: 100000
```

实现：检查 session token budget>0 → PASSED；超用→SOFT_BLOCKED（DD4 动态阈值）。

### G3: Environment Integrity

```yaml
gate_name: "Task-G3: Environment Integrity"
gate_level: "G3"
required_context: ["runtime_environ"]
check_method: "validate_runtime"
min_python: "3.12"
min_disk_gb: 1
requires: ["powershell"]
```

实现：`sys.version_info>=(3,12)` + `shutil.disk_usage('.') > 1GB` + `subprocess.run(['powershell','-Command','$true'])`。

## 回退方案

三文件→空桩→`check_all()` 返回 `GateResult.PASSED`。

## 验收标准

| # | 标准 |
|---|------|
| AC1 | G1 YAML 含 gate_name/level/context/method |
| AC2 | G2 YAML 含 threshold: {max_tokens_per_task: 100000} |
| AC3 | G3 YAML 含 min_python: "3.12" + min_disk_gb: 1 |
| AC4 | 磁盘检查/环境检查返回合理 GateResult |
