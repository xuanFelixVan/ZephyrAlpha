---
task_id: "TASK-INF-0206"
source_blueprint: "MOD-INF-014"
source_section: "§6 L3 + §25.1 盲点一 + §49 Agent公域交互安全"
title: "L3 输出安全层完整实现——Schema验证+代码沙箱+PII脱敏+幻觉检测+AI代码信任边界"
description: |
  实现 OutputSecurityLayer：Schema验证（Pydantic strict+extra='forbid'）+ 代码执行沙箱（Docker/WASI/subprocess_only）
  + PII脱敏（25+SECRET_PATTERNS三级策略BLOCK/MASK/FLAG）+ 幻觉检测（上下文语义一致性+不确定性标记）
  + AI代码信任边界审计 + Agent公域发言安全检查。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l3_output.py"
    description: "L3 OutputSecurityLayer——Schema+沙箱+脱敏+幻觉+AI代码信任+公域安全"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\patterns\\secrets.py"
    description: "PII/Secret 模式库 25+规则"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l3_output_security.py"
    description: "L3 输出安全单元测试——15条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l3_output.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\patterns\\secrets.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l3_output_security.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§6+§25.1+§49完整接口定义"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 15000
timeout_minutes: 90
acceptance_criteria:
  - "OutputSecurityLayer 含 validate_schema/sandbox_execution/redact_sensitive_data/detect_hallucination/check_content_safety 5个核心方法"
  - "secrets.py 含 SECRET_PATTERNS 列表 25+规则（API Key+PII+内部敏感词）"
  - "三级脱敏策略：BLOCK（完全阻断凭据）/MASK（部分遮盖PII）/FLAG（标记告警内部词）"
  - "AIGeneratedCodeTrustBoundary 类审计6类安全问题"
  - "AgentPublicInteractionGuard 类（GitHub/飞书/社区/API四通道自动脱敏+Agent身份声明规范）"
  - "Pydantic V2 SchemaResult/SandboxResult/RedactResult/HallucinationResult/SafetyResult"
  - "15条单元测试全部通过"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l3_output.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\patterns\secrets.py
  3. 删除 D:\ZephyrAlpha\tests\llm_security\test_l3_output_security.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security"]
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

实现 L3 输出安全层——四层输出验证体系的完整防御。确保所有 LLM 输出在抵达消费者前通过 Schema 验证、沙箱执行、敏感数据脱敏和幻觉检测。

## 触发条件
- TASK-INF-0201 已通过

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §6+§25.1+§49
- `D:\ZephyrAlpha\src\zephyr\llm_security\process_sandbox.py`

### 做
1. 实现 `OutputSecurityLayer` ——4个子层方法
2. 实现 `AIGeneratedCodeTrustBoundary` ——AI生成代码安全检查
3. 实现 `AgentPublicInteractionGuard` ——公域发言安全
4. 创建 `secrets.py` ——25+ SECRET_PATTERNS
5. 编写 15 条单元测试

### 产
- `l3_output.py` / `secrets.py` / `test_l3_output_security.py`

### 检
```bash
pytest tests/llm_security/test_l3_output_security.py -v
```
