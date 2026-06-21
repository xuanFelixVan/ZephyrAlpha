---
module_id: KE-3002
status: active
title: validate_module_output
category: module_blueprint
---

# validate_module_output

validate_module_output

```python
def validate_module_output(module_id: str, output: dict) -> bool:
    """按模块ID选择Schema→Pydantic验证"""
    schema_map = {
        "M1": ParseOutput, "M2": ContextOutput, "M3": GenerateOutput,
        "M4": FormatOutput, "M5": PackageOutput, "M6": DiffOutput,
        "M7": ReviewOutput, "M8": ComplianceOutput,
    }
    # M9/M10/M11 → GenericModuleOutput
```
