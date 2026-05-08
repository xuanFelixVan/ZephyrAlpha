---
task_id: "TASK-INF-0205"
source_blueprint: "MOD-INF-014"
source_section: "§5 L2 Prompt保护层"
title: "L2 Prompt保护层完整实现——四段式Prompt模板+防泄露检测+话题边界控制"
description: |
  实现 PromptProtectionLayer：System Prompt 硬隔离四段式模板（SYSTEM/HISTORY/EXTERNAL_DATA/USER_INPUT）、
  防泄露检测（子串匹配+语义相似度）+ Prompt试探检测（50+中英文变体）+ 话题边界控制。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l2_prompt_protection.py"
    description: "L2 PromptProtectionLayer——四段式模板+防泄露+话题控制"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l2_prompt_protection.py"
    description: "L2 Prompt保护层单元测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l2_prompt_protection.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l2_prompt_protection.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§5 L2完整接口定义+_LEAK_PROBE_PATTERNS"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 8000
timeout_minutes: 45
acceptance_criteria:
  - "PromptProtectionLayer 含 build_safe_prompt/scan_for_leak/detect_prompt_probing/check_topic_boundary 4个方法"
  - "四段式 Prompt 模板使用明确标记（SYSTEM/HISTORY/EXTERNAL_DATA/USER_INPUT）隔离"
  - "_LEAK_PROBE_PATTERNS 含 50+ 中英文变体"
  - "scan_for_leak() 含快速通道（子串匹配 O(n)）+深度通道（语义相似度可选）"
  - "check_topic_boundary() 检测6个预定义话题域偏离"
  - "10条单元测试全部通过"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l2_prompt_protection.py
  2. 删除 D:\ZephyrAlpha\tests\llm_security\test_l2_prompt_protection.py
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

实现 L2 Prompt 保护层——System Prompt 与用户输入/外部数据的硬隔离，防止 System Prompt 泄露，控制对话话题范围。

## 触发条件
- TASK-INF-0201 已通过

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §5
- `D:\ZephyrAlpha\src\zephyr\llm_security\protocol.py`

### 做
1. 实现四段式 Prompt 模板 `_PROMPT_TEMPLATE`
2. 实现 `scan_for_leak()` ——SHA256片段哈希快速通道+子串匹配
3. 实现 `detect_prompt_probing()` ——50+中英文试探模式匹配
4. 实现 `check_topic_boundary()` ——轻量关键词向量匹配
5. 编写 10 条单元测试

### 产
- `l2_prompt_protection.py` / `test_l2_prompt_protection.py`

### 检
```bash
pytest tests/llm_security/test_l2_prompt_protection.py -v
```
