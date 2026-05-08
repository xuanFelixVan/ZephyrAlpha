---
task_id: "TASK-INF-0202"
source_blueprint: "MOD-INF-014"
source_section: "蓝图 §2 OWASP Top 10 for LLM 2025 完整覆盖矩阵"
title: "OWASP Top 10 for LLM 2025 覆盖矩阵落地——LSG防御层次映射实现"
description: |
  将蓝图 §2 定义的 OWASP Top 10 for LLM 2025 10类风险的 LSG 覆盖策略转化为代码中的可验证断言。
  实现覆盖矩阵验证器——确保每类 OWASP 风险均有对应 LSG 防御层、覆盖策略和门禁检查。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_owasp_coverage.py"
    description: "OWASP Top 10 覆盖验证测试——每类风险必须有 LSG 防御层覆盖"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\owasp_coverage_auditor.py"
    description: "OWASP 覆盖合规审计器——自动检查 LSG 对 OWASP 的覆盖完整性"
allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_owasp_coverage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\owasp_coverage_auditor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-INF-{NNNN}"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "本蓝图——§2 OWASP 覆盖矩阵"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 30
acceptance_criteria:
  - "test_owasp_coverage.py 包含 LLM01-LLM10 全部 10 类风险的覆盖验证测试"
  - "owasp_coverage_auditor.py 包含 OWASP_COVERAGE_MAP 字典——每类风险→LSG防御层+门禁"
  - "Pydantic V2 BaseModel——导入路径 from pydantic import BaseModel"
  - "所有测试用例通过率 100%"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\llm_security\test_owasp_coverage.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\self_protection\owasp_coverage_auditor.py
depends_on:
  - "TASK-INF-0201"
blocked_by: []
status: "created"
tags_fn:
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-014"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

将蓝图 §2 的 OWASP Top 10 for LLM 2025 覆盖矩阵转化为可验证的代码实现。建立覆盖映射表（OWASP 风险 → LSG 防御层 + 覆盖策略），并实现自动化覆盖审计器，确保 LSG 对 10 类风险的 100% 防御覆盖。

## 触发条件

- TASK-INF-0201（模块骨架搭建）已通过
- 蓝图 §2 已定义 LLM01-LLM10 全部覆盖策略

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §2
- `D:\ZephyrAlpha\src\zephyr\llm_security\protocol.py`（LSG 抽象基类）

### 做
1. 创建 `owasp_coverage_auditor.py` ——包含 OWASP_COVERAGE_MAP 字典：LLM01→L1+L2, LLM02→L2+L3+L6, LLM03→L0, LLM04→L0+L7, LLM05→L3, LLM06→L4, LLM07→L2, LLM08→L1+L0, LLM09→L3, LLM10→L5
2. 实现 `OWASPCoverageAuditor.audit()` ——遍历覆盖映射表，检查每个防御层是否存在对应的门禁检查
3. 创建 `test_owasp_coverage.py` ——10 条测试：LLM01-LLM10 每类风险对应一条覆盖验证

### 产
- `owasp_coverage_auditor.py`
- `test_owasp_coverage.py`

### 检
```bash
pytest tests/llm_security/test_owasp_coverage.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | coverage | 10 条测试全部通过 |
| 2 | lint | 0 errors, 0 warnings |
| 3 | files | deliverables 全部存在 + UTF-8 |
