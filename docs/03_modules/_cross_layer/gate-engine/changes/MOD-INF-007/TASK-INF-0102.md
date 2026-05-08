---
task_id: TASK-INF-0102
status: planned
priority: P0
severity: critical
module_id: MOD-INF-007
phase: 1
category: implementation
effort_estimated: 6h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §2.1、§5、§2.3
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  - D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-lifecycle-standard.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_status.py
  - D:\ZephyrAlpha\src\zephyr\gates\base.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g0_entry.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g1_pre_exec.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g2_resource.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g3_env.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g4_tracking.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g5_error.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g6_artifact.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_gates\g7_delivery.py
acceptance_criteria:
  - AC1: G0-G7 每级门控规则以 YAML 配置形式存在，存储于 `D:\ZephyrAlpha\src\zephyr\gates\task_gates\` 各文件中
  - AC2: G0 入口门控：check_all() 验证 TaskCard 的 21 必填字段完整性（检查 task_id 非空、priority 在 {P0,P1,P2,P3,P4}、status 在有效状态集中）
  - AC3: G1 预执行门控：验证 upstream_files 磁盘存在性（文件路径可读性检查，非内容检查）
  - AC4: G2 资源门控：验证 session token 配额充足（默认 max_tokens_per_task=100000）
  - AC5: G3 环境门控：验证 Python 3.12+、可用磁盘 >1GB、Powershell 可用
  - AC6: G4 追踪门控：插入 MetadataRegistry.tracking_event（event_type=gate_passed, gate_level=<G4>）
  - AC7: G5 错误门控：集成 CircuitBreaker（DD6），记录最近 3 次失败到 task_repo.error_log
  - AC8: G6 产物门控：验证下游输出文件存在（→Path). 路径与 task_card.downstream_outputs 一致，文件 >0 bytes
  - AC9: G7 交付门控：1→全 AC 通过、2→无 ZALP error 残留、3→task_repo MM 与 .md 双轨一致
  - AC10: 每个 G* gate 返回 GateResult(status=GateStatus.{PASSED|BLOCKED|SOFT_BLOCKED}, violations=[...])
  - AC11: G0-G7 各级的 gate_name、gate_level、required_context 字段按 blueprint.md §2.1 定义精确填写
  - AC12: 每级 G* gate 的 rollback 方法返回 None（门控可回退到检查前状态）
rollback_instructions:
  - 将 task_gates/ 下全部 7 个 gate 实现文件替换为空桩（仅保留 `pass` 实现）
  - 空桩 GateResult 始终返回 PASSED——防止因门控误杀 Client-Server 运行时入口
  - 执行 `python -c "from zephyr.gates.task_gates.g0_entry import G0EntryGate; g = G0EntryGate(); print(g.check_all({}))"` 确认空桩模式
created_at: 2026-05-06T23:35:00Z
updated_at: 2026-05-06T23:35:00Z
closed_at: null
dependencies:
  - TASK-INF-0101 (骨架搭建)
  - TASK-INF-0104 (GateResult/GateStatus 数据模型)
blocked_by: [TASK-INF-0101, TASK-INF-0104]
blocks: [TASK-INF-0117, TASK-INF-0118]
tags:
  - gate-engine
  - task-gates
  - G0-G7
  - structured-rules
  - guardrail
version: 1.0.0
change_log: |
  v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §2.1 + §5（v1.4.3）
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections:
    - §2.1 G0-G7 任务级门控
    - §5 核心流程——G0-G7 结构化 YAML 规则
    - §2.3 双门体系总览
  keywords:
    - G0
    - G1
    - G2
    - G3
    - G4
    - G5
    - G6
    - G7
    - task gate
    - guardrail
  ai_reads_for_inference: true
---

# TASK-INF-0102: G0-G7 任务级结构化门控规则实现

## 背景与动机

gate-engine 为任务全生命周期定义 **G0-G7 八级任务级门控**（blueprint.md §2.1）。每级是一个独立 AOP 切面，在任务向下一状态过渡前执行。本任务卡将 §5 的结构化 YAML 规则落地为 Python Gate 类，确保 Permit/Block/Fail 三态门禁。

覆盖：
- `G0` Entry Gate — TaskCard 字段完整性
- `G1` Pre-execution — upstream_files 磁盘存在性
- `G2` Resource — session token 配额
- `G3` Environment — Python/PowerShell/磁盘环境
- `G4` Tracking — 追踪事件注入
- `G5` Error — G5 错误熔断（DD6 CircuitBreaker）
- `G6` Artifact — downstream_outputs 完整性
- `G7` Delivery — 雙轨一致性 + AC 全部通过

## 实施计划

### Step 1: G0 入口门控实现 (`g0_entry.py`)

G0 Gate 强制检查 TaskCard 的所有 21 必填字段：

```python
def check_all(self, task_dict: dict[str, Any]) -> GateResult:
    violations = []
    required_fields = ["task_id","status","priority","severity","module_id",
        "phase","category","effort_estimated","effort_actual","assigned_to",
        "reviewer","approver","source_section","reference_docs","upstream_files",
        "downstream_outputs","acceptance_criteria","rollback_instructions",
        "created_at","updated_at","closed_at"]
    for field in required_fields:
        if field not in task_dict:
            violations.append(f"MISSING_FIELD: {field}")
    priority = task_dict.get("priority")
    if priority not in {"P0","P1","P2","P3","P4"}:
        violations.append(f"INVALID_PRIORITY: {priority}")
    if not violations:
        return GateResult(status=GateStatus.PASSED, gate_level="G0")
    return GateResult(status=GateStatus.BLOCKED, gate_level="G0", violations=violations)
```

### Step 2: G1-G6 逐级实现

- **G1 Pre-execution Gate** (`g1_pre_exec.py`): `validate_upstream_files()` — `os.path.exists()` 遍历 `task_dict["upstream_files"]`
- **G2 Resource Gate** (`g2_resource.py`): `check_token_quota()` — 默认 max_tokens_per_task=100000
- **G3 Environment Gate** (`g3_env.py`): `validate_runtime()` — sys.version_info>=3.12 + shutil 磁盘检查 >1GB
- **G4 Tracking Gate** (`g4_tracking.py`): `inject_tracking_event()` — event_type=gate_passed
- **G5 Error Gate** (`g5_error.py`): `integrate_circuit_breaker()` — 检查最近 3 次失败计数
- **G6 Artifact Gate** (`g6_artifact.py`): `verify_downstream_outputs()` — 文件 >0 bytes + 路径匹配

每级 gate 返回结构：
```python
GateResult(status=GateStatus.PASSED | BLOCKED | SOFT_BLOCKED, 
           violations=["...",]).to_dict()
```

### Step 3: G7 交付门控 (`g7_delivery.py`)

G7 三步验证：
1. 全部 AC 通过
2. 无 ZALP-error 残留
3. task_repo（SQLite）与 .md 双轨一致性

## 回退方案

1. 将 `task_gates/*.py` 替换为空桩实现（`check_all()` 始终返回 PASS）
2. 测试：`pytest tests/gates/test_task_gates.py -x` 显示全部 PASS（空桩不应阻执行）
3. 回退到 TASK-INF-0101 的 clean 版本

## 验收标准

| # | 标准 |
|---|------|
| AC1 | G0-G7 各 Python Gate 类包含 YAML 配置级的定义（gate_name、gate_level、required_context） |
| AC2 | G0 check_all 验证 21 必填字段——缺 field → BLOCKED |
| AC3 | G1 验证 upstream_files 磁盘存在——缺文件 → BLOCKED |
| AC4 | G2 验证 token 配额——超限 → SOFT_BLOCKED |
| AC5 | G3 验证 Python 3.12+——不满足 → BLOCKED |
| AC6 | G4 注入 trace → 成功返回 PASSED |
| AC7 | G5 检查 3 次失败 → ≥3 → BLOCKED |
| AC8 | G6 验证 downstream_outputs >0 bytes |
| AC9 | G7 三步 AC+ZALP+双轨验证 |
| AC10 | 返回 Protocol 格式 GateResult |
| AC11 | gate_name/gate_level/required_context 精确 |
| AC12 | rollback 方法存在且正确 |
