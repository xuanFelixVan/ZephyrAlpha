---
task_id: TASK-INF-0106
status: planned
priority: P0
severity: critical
module_id: MOD-INF-007
phase: 1
category: integration
effort_estimated: 2h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §4、§8.1、CT-SCRIPT-GATE-001
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  - D:\ZephyrAlpha\tool_contracts.yaml
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: GateEngine.evaluate_script_result(exit_code, stdout, stderr) 将 script exit_code=0→PASSED、exit_code≠0→BLOCKED——符合CT-SCRIPT-GATE-001"
  - "AC2: BLOCKED 时 GateResult.violations 包含 stderr 最后 3 行用于诊断"
  - "AC3: exit_code=null/timeout→ERROR，violations=['SCRIPT_TIMEOUT']"
  - "AC4: GateResult.metadata 包含 {'exit_code': int, 'stdout_length': int, 'stderr_length': int} 用于审计"
  - "AC5: 与 §5 G6 Artifact Gate 集成——script 产出文件存在性由 G6 验证，script 退出码由 CT-SCRIPT-GATE-001 验证"
rollback_instructions:
  - "移除 GateEngine.evaluate_script_result() 方法——退化为不校验 script exit code"
  - "执行：python -c \"from zephyr.gates.gate_engine import GateEngine; assert not hasattr(GateEngine, 'evaluate_script_result')\""
  - "G6 Artifact Gate 降级为仅检查文件存在性，不关联 script exit code"
created_at: 2026-05-06T23:40:00Z
updated_at: 2026-05-06T23:40:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0104
blocked_by:
  - TASK-INF-0101
  - TASK-INF-0104
blocks: []
tags:
  - gate-engine
  - CT-SCRIPT-GATE-001
  - integration
  - script-exit-code
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §4 + §8.1 CT-SCRIPT-GATE-001 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections:
    - "§4 集成总览"
    - "§8.1 CT-SCRIPT-GATE-001"
  keywords:
    - CT-SCRIPT-GATE-001
    - script-exit-code
    - GateEngine
    - integrate
  ai_reads_for_inference: true
---

# TASK-INF-0106: CT-SCRIPT-GATE-001 集成——Script 退出码门控

## 背景与动机

gate-engine 通过 CT-SCRIPT-GATE-001 集成契约定义了对脚本执行结果的统一门控逻辑（blueprint.md §4 + §8.1）。任何上游脚本执行后，其 exit_code、stdout、stderr 必须经过 GateEngine.evaluate_script_result() 门控——exit_code=0=PASSED、exit_code≠0=BLOCKED。

## 实施计划

在 `gate_engine.py` 中添加：

```python
def evaluate_script_result(self, exit_code: int | None, stdout: str, stderr: str) -> GateResult:
    if exit_code is None:
        return GateResult(status=GateStatus.ERROR, gate_level="SCRIPT",
                          violations=["SCRIPT_TIMEOUT"],
                          metadata={"exit_code": None, "stdout_length": len(stdout), "stderr_length": len(stderr)})
    if exit_code == 0:
        return GateResult(status=GateStatus.PASSED, gate_level="SCRIPT",
                          metadata={"exit_code": 0, "stdout_length": len(stdout), "stderr_length": len(stderr)})
    last_stderr_lines = stderr.strip().split("\n")[-3:] if stderr.strip() else ["(empty stderr)"]
    return GateResult(status=GateStatus.BLOCKED, gate_level="SCRIPT",
                      violations=[f"exit_code={exit_code}"] + last_stderr_lines,
                      metadata={"exit_code": exit_code, "stdout_length": len(stdout), "stderr_length": len(stderr)})
```

## 回退方案

1. 删除 `evaluate_script_result()` 方法
2. G6 Artifact Gate 降级为仅检查文件存在性
3. 所有脚本执行不再被 gate-engine 门控

## 验收标准

| # | 标准 | 验证 |
|---|------|------|
| AC1 | exit_code=0→PASSED | 单元测试 |
| AC2 | exit_code≠0→BLOCKED + stderr最后3行 | 单元测试 |
| AC3 | exit_code=None→ERROR+SCRIPT_TIMEOUT | 单元测试 |
| AC4 | metadata 含 {exit_code, stdout_length, stderr_length} | assert 检查 |
| AC5 | G6 分割职责——script exit code不归G6管 | 代码审查 |
