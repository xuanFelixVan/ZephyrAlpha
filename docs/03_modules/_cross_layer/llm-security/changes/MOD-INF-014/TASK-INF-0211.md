---
task_id: "TASK-INF-0211"
source_blueprint: "MOD-INF-014"
source_section: "§11 L2a + §11 Process Sandbox + §25.5 盲点五"
title: "L2a 进程级沙箱保留方案——容器化+WASI运行时+资源隔离+文件系统审计"
description: |
  实现 ProcessSandboxLayer: 在 Docker 容器中执行任意代码、WASI WebAssembly 运行时代理、
  网络隔离白名单、资源限制(cpu/memory/disk/timeout)、文件系统审计日志、
  BlindSpot5 ProcessSandboxGuard 复杂性数据提取防护。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l2a_process_sandbox.py"
    description: "L2a ProcessSandboxLayer——Docker+WASI+资源隔离+文件审计+盲点五防护"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l2a_process_sandbox.py"
    description: "L2a 进程沙箱单元测试——8条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l2a_process_sandbox.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l2a_process_sandbox.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§11+§25.5 完整定义"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 10000
timeout_minutes: 60
acceptance_criteria:
  - "ProcessSandboxLayer 含 execute_in_sandbox/audit_filesystem_access/validate_changes 3个方法"
  - "SandboxContainerConfig Pydantic V2: image/cpu_limit/memory_limit/disk_limit/timeout_seconds"
  - "WASIRuntimeConfig Pydantic V2: wasm_file_path/entry_point/memory_pages/max_execution_ms"
  - "BlindSpot5ProcessSandboxGuard: 检测容器/运行时内复杂性数据提取行为"
  - "8条单元测试全部通过"
rollback_instructions: |
  1. 删除 l2a_process_sandbox.py
  2. 删除 test_l2a_process_sandbox.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","sandbox"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 L2a 进程级沙箱保留方案——以 Docker + WASI 双运行时隔离代码执行。作为可选安全控制供应用层按需启用。

## 执行步骤

### 做
1. 实现 ProcessSandboxLayer 3个方法
2. 实现 BlindSpot5ProcessSandboxGuard
3. 编写 8 条单元测试
