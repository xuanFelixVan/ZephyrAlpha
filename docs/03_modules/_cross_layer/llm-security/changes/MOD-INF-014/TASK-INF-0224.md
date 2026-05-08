---
task_id: "TASK-INF-0224"
source_blueprint: "MOD-INF-014"
source_section: "§48 跨会话持久化状态污染 + §55 多模态注入 + §61 已实现代码路径索引 + 版本记录"
title: "跨会话污染+多模态注入防护+代码路径索引与版本管理"
description: |
  §48 CrossSessionContaminationDefender: SessionStateBaseline哈希自检 + Deep state key枚举
  + Context隔离验证 + 合并验证 + StateDiff违规检测(AUTO_MODIFIED/UNEXPECTED_PROP/etc)
  + ReincarnationMode enum (clean_isolate/inherit_with_validation)
  §55 MultimodalInjectionDefender: Base64恶意指令注入检查 + 隐藏文本检测
  + Image→Description伴生安全策略(上限→输入审计固定为纯text_description→禁止生成自定义prompt)
  + 多维特征检测: interleaved_brackets+control_sequences+visual_layout_manipulation
  §61+版本历史: 已实现代码路径汇总表更新+蓝图版本历史同步
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\cross_session_guard.py"
    description: "跨会话持久化状态污染防护"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\multimodal_injection_defense.py"
    description: "多模态注入防御"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_cross_session_and_multimodal.py"
    description: "跨会话+多模态测试——8条用例"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    description: "更新 §61 代码路径索引 + 版本记录"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\cross_session_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\multimodal_injection_defense.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_cross_session_and_multimodal.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§48+§55+§61"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 10000
timeout_minutes: 60
acceptance_criteria:
  - "CrossSessionGuard: verify_state_integrity()+BaselineValidator+StateDiffDetector+DeepStateBaseline 6方法"
  - "ReincarnationMode enum clean_isolate/inherit_with_validation"
  - "MultimodalDefender: image→OCR→hidden text scan+Image→passthrough text file→inject scan+multi-dim特征检测"
  - "Image_description_prompt: 强制纯文本输出+禁止自定义生成prompt+bind to source bas64 hash"
  - "§61 代码路径索引 100%同步+版本记录更新"
  - "8条测试全部通过"
rollback_instructions: |
  1. 删除 cross_session_guard.py + multimodal_injection_defense.py + test_cross_session_and_multimodal.py
  2. 回退 blueprint.md §61 更新
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "created"
tags_fn: ["security","state"]
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

实现跨会话持久化状态污染防御+多模态注入防御+代码路径索引与版本管理。

## 执行步骤

### 做
1. 实现 CrossSessionGuard——哈希基线+状态违规枚举+ReincarnationMode
2. 实现 MultimodalDefender——图片隐藏文本+空间编码+多模态特征检测三层
3. 更新 §61 代码路径索引表+蓝图版本记录
4. 编写 8 条测试
5. 确认本次session产出的所有 .py 文件已记录至代码路径索引
