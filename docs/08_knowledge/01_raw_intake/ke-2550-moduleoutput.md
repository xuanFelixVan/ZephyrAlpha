---
module_id: KE-2455----moduleoutput-000
status: active
title: 8个专用 ModuleOutput 子类
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8个专用 ModuleOutput 子类

8个专用 ModuleOutput 子类

```python
class ParseOutput(ModuleOutput):      # M1 → 结构化执行计划
    parsed_plan: dict
    task_breakdown: list[str]

class ContextOutput(ModuleOutput):    # M2 → 上下文装配结果
    assembled_context: dict
    sources_used: list[str]

class GenerateOutput(ModuleOutput):   # M3 → 代码/文档生成
    generated_code: str
    language: str
    file_path: str|None

class FormatOutput(ModuleOutput):     # M4 → 格式校验
    format_report: dict
    lint_errors: list[str]

class PackageOutput(ModuleOutput):    # M5 → 产物打包
    package_path: str
    files_included: list[str]
    package_hash: str

class DiffOutput(ModuleOutput):       # M6 → 差异检测
    diff_summary: dict
    added_files: list[str]
    modified_files: list[str]
    deleted_files: list[str]

class ReviewOutput(ModuleOutput):     # M7 → 深度审查
    review_report: dict
    findings: list[dict]
    risk_flags: list[str]

class ComplianceOutput(ModuleOutput): # M8 → 标准合规
    compliance_report: dict
    violations: list[dict]
    standard_refs: list[str]
```
