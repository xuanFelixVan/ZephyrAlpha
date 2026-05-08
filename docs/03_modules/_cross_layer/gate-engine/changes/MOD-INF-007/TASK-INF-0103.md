---
task_id: TASK-INF-0103
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: implementation
effort_estimated: 4h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §2.2
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_result.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_status.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\kms_gates\g1_decision_scope.py
  - D:\ZephyrAlpha\src\zephyr\gates\kms_gates\g2_doc_quality.py
  - D:\ZephyrAlpha\src\zephyr\gates\kms_gates\g3_contract_consistency.py
  - D:\ZephyrAlpha\src\zephyr\gates\kms_gates\g4_risk_coverage.py
  - D:\ZephyrAlpha\src\zephyr\gates\kms_gates\g5_gov_compliance.py
acceptance_criteria:
  - "AC1: G1 DecisionScopeGate.check(blueprint_path) 验证蓝图必需章节（概述、架构、接口契约、数据模型、风险、Anti-Patterns）全部存在，缺失章节→BLOCKED"
  - "AC2: G2 DocQualityGate.check(blueprint_path) 评分≥0.7→PASSED；评分维度含YAML frontmatter完整度+章节结构+代码块可执行性"
  - "AC3: G3 ContractConsistencyGate.check(blueprint_path) 从蓝图提取CT-*契约→交叉验证tool_contracts.yaml一致性→所有契约匹配→PASSED"
  - "AC4: G4 RiskCoverageGate.check(blueprint_path) 列出所有DD-*编号→逐一证实蓝图§9风险表全覆蓋→所有DD有对应R条目→PASSED"
  - "AC5: G5 GovComplianceGate.check(blueprint_path) 验证产出物目录表非空→路径符合directory-structure-standard.md→满足→PASSED"
  - "AC6: G1-G5每级以YAML/Python Enum形式定义规则，禁止散落if-elif链"
  - "AC7: 每级KMS Gate含rollback方法，返回默认PASSED"
rollback_instructions:
  - "将kms_gates/*.py替换为空桩（check()始终返回GateResult.PASSED）"
  - "执行：python -c \"from zephyr.gates.kms_gates.g1_decision_scope import G1DecisionScopeGate; g = G1DecisionScopeGate(); print(g.check('dummy.md'))\"确认默认PASSED"
  - "删除kms_gates/目录恢复至TASK-INF-0101骨架状态"
created_at: 2026-05-06T23:36:00Z
updated_at: 2026-05-06T23:36:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0104
blocked_by:
  - TASK-INF-0101
  - TASK-INF-0104
blocks:
  - TASK-INF-0117
tags:
  - gate-engine
  - kms-gates
  - G1-G5
  - decision-governance
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 初始创建，基于 blueprint.md §2.2 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections:
    - "§2.2 KMS 决策级门控"
  keywords:
    - KMS
    - G1-decision-scope
    - G2-doc-quality
    - G3-contract-consistency
    - G4-risk-coverage
    - G5-gov-compliance
    - decision-gate
  ai_reads_for_inference: true
---

# TASK-INF-0103: G1-G5 KMS 决策级门控规则实现

## 背景与动机

gate-engine 的第二条 Gate 链——**G1-G5 KMS（Knowledge Management System）决策门**——负责在蓝图被印发到任务分解前的事先治理（blueprint.md §2.2）。五个 G 级依次确保：

- **G1 DecisionScopeGate**：决策范围覆盖完整——蓝图包含概述、架构、接口契约、数据模型、风险、Anti-Patterns 等必需章节
- **G2 DocQualityGate**：文档质量标准——YAML frontmatter 完整性 + 章节结构 + 代码块可执行性 ≥ 0.7
- **G3 ContractConsistencyGate**：契约一致性——蓝图中的 CT-* 契约与 `tool_contracts.yaml` 交叉验证一致
- **G4 RiskCoverageGate**：风险覆盖——蓝图 §9 风险表中所有 DD-* 编号均有对应 R 条目
- **G5 GovComplianceGate**：治理合规——产出物目录表非空且路径符合 directory-structure-standard.md

## 实施计划

### Step 1: G1 DecisionScopeGate (`g1_decision_scope.py`)

```python
class G1DecisionScopeGate(Gate):
    gate_name = "KMS-G1: Decision Scope"
    gate_level = "G1"
    required_context = ["blueprint_path"]

    def check(self, blueprint_path: str) -> GateResult:
        if not os.path.exists(blueprint_path):
            return GateResult(status=GateStatus.BLOCKED, gate_level="G1",
                              violations=[f"invalid_path: {blueprint_path}"])
        with open(blueprint_path, "r", encoding="utf-8") as f:
            content = f.read()
        required = ["概述","架构","接口契约","数据模型","风险","Anti"]
        missing = [s for s in required if s not in content]
        if missing:
            return GateResult(status=GateStatus.BLOCKED, gate_level="G1",
                              violations=[f"missing_section: {m}" for m in missing])
        return GateResult(status=GateStatus.PASSED, gate_level="G1")
```

### Step 2: G2 DocQualityGate (`g2_doc_quality.py`)

评分维度：
1. YAML frontmatter 存在（0.3）
2. frontmatter 中 task_id、status、source_section 字段非空（0.3）
3. 章节结构含 ## 标题≥5 个（0.2）
4. Python 代码块可 parsed（0.2）

threshold = 0.7

### Step 3: G3 ContractConsistencyGate (`g3_contract_consistency.py`)

从 blueprint 正则提取 `CT-[A-Z-]+-\d+` → 与 `tool_contracts.yaml` 对比 → 缺失契约 → BLOCKED

### Step 4: G4 RiskCoverageGate (`g4_risk_coverage.py`)

提取所有 `DD-\d+` → 检查 blueprint §9 风险表中每条 DD 有对应 R 编号

### Step 5: G5 GovComplianceGate (`g5_gov_compliance.py`)

验证产出物目录路径表 → 与 directory-structure-standard.md 对照

## 回退方案

1. 备份 kms_gates/*.py → 替换为空桩（check() 返回 GateResult.PASSED 默认值）
2. 执行：`python -c "from zephyr.gates.kms_gates.g1_decision_scope import G1DecisionScopeGate; g = G1DecisionScopeGate(); print(g.check('dummy.md'))"` 确认默认 PASSED
3. 删除 kms_gates/ 目录至 TASK-INF-0101 clean 状态

## 验收标准

| # | 标准 | 验证方式 |
|---|------|---------|
| AC1 | G1 验证蓝图必需章节全存在 | `python -m pytest tests/gates/test_kms_gates.py::test_g1` |
| AC2 | G2 评分≥0.7→PASSED | `python -m pytest tests/gates/test_kms_gates.py::test_g2` |
| AC3 | G3 CT-* 契约交叉验证一致 | `python -m pytest tests/gates/test_kms_gates.py::test_g3` |
| AC4 | G4 所有 DD 有对应 R 条目 | `python -m pytest tests/gates/test_kms_gates.py::test_g4` |
| AC5 | G5 产出物路径符合目录标准 | `python -m pytest tests/gates/test_kms_gates.py::test_g5` |
| AC6 | YAML/Python 规则结构化，非散落 if-elif | 代码审查 |
| AC7 | rollback 方法存在且可调用 | `python -m pytest tests/gates/test_kms_gates.py::test_rollback` |
