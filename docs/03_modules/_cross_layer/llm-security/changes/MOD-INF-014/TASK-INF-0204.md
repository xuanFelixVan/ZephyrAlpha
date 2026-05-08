---
task_id: "TASK-INF-0204"
source_blueprint: "MOD-INF-014"
source_section: "§4 L1 + §38 ToolResultTransform + §59 Prompt混淆编码逃逸防御"
title: "L1 输入防护层完整实现——直接注入+间接注入+越狱检测+ToolResultTransform+编码逃逸防御"
description: |
  实现 InputDefenseLayer 类：整合现有 input_sanitizer.py 的直接注入检测 + 新增间接注入检测（RAG/文件/URL/邮件）
  + 越狱专项检测（角色扮演/编码混淆/多语言绕过/嵌套攻击）+ ToolResultTransform 预上下文注入拦截 +
  编码逃逸防御（递归解码扫描+Unicode隐形字符+同形字标准化）。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l1_input.py"
    description: "L1 InputDefenseLayer——直接+间接+越狱+ToolResultTransform+编码逃逸"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\patterns\\injection_patterns.py"
    description: "注入 Payload 特征库"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l1_input_defense.py"
    description: "L1 输入防护单元测试——20 条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l1_input.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\patterns\\injection_patterns.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l1_input_defense.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§4 L1完整接口+§38 ToolResultTransform+§59编码逃逸防御"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
    reason: "现有直接注入检测——L1子层1A整合"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 15000
timeout_minutes: 90
acceptance_criteria:
  - "InputDefenseLayer 含 check_direct_input/check_indirect_content/check_jailbreak/sanitize_and_wrap 4个核心方法"
  - "injection_patterns.py 含 _INDIRECT_INJECTION_PATTERNS 5组正则+_FILE_TYPE_CHECKS 6种文件类型"
  - "ToolResultTransform 拦截器：工具执行结果→LLM上下文之间注入防御"
  - "编码逃逸防御：递归解码扫描（Base64/Rot13/Unicode）+同形字标准化+3层防御架构"
  - "Pydantic V2 DefenseResult/SourceType 模型"
  - "20条单元测试全部通过"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l1_input.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\patterns\injection_patterns.py
  3. 删除 D:\ZephyrAlpha\tests\llm_security\test_l1_input_defense.py
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

实现 LSG L1 输入防护层——三层检测体系（直接注入+间接注入+越狱检测）的完整防御能力。整合现有 input_sanitizer.py 作为子层1A，新增子层1B（间接注入扫描 RAG/文件/URL/邮件内容）、子层1C（越狱专项检测），以及 ToolResultTransform 预上下文注入拦截和编码逃逸防御。

## 触发条件
- TASK-INF-0201 已通过
- 现有 input_sanitizer.py 已实现直接注入检测基础

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §4+§38+§59
- `D:\ZephyrAlpha\src\zephyr\llm_security\input_sanitizer.py`（直接注入检测——待整合）

### 做
1. 创建 `l1_input.py` ——InputDefenseLayer 类，构造函数接收 InputSanitizer 实例用于子层1A
2. 实现 `check_indirect_content()` ——RAG/文件/URL/邮件内容注入扫描
3. 实现 `check_jailbreak()` ——角色扮演/编码混淆/多语言绕过/嵌套攻击检测
4. 实现 `sanitize_and_wrap()` ——外部内容隔离包裹标记
5. 实现 `ToolResultTransformGuard` ——填补工具执行→LLM上下文之间的零防护窗口
6. 实现 `EncodingBypassDefender` ——递归解码扫描+Unicode隐形字符检测+同形字标准化
7. 创建 `injection_patterns.py` ——间接注入特征库
8. 编写 20 条单元测试

### 产
- `l1_input.py` / `injection_patterns.py` / `test_l1_input_defense.py`

### 检
```bash
pytest tests/llm_security/test_l1_input_defense.py -v
```
