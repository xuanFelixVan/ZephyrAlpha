---
module_id: KE-1284
status: active
title: 1. Conditional Execution（B100）
category: module_blueprint
---

# 1. Conditional Execution（B100）

1. Conditional Execution（B100）

```python
async def _execute_module_with_skip(self, node_id: str, ...) -> ModuleResult:
    if node_id == "M6":
        result = await self._call_model(node_id, ...)
        if not result.diff_found:
            # 标记M7/M8/M9为SKIPPED
            return result  # Pipeline顺势跳过后续审计节点
        
    elif result_from_M6 and not result_from_M6.diff_found:
        if node_id in ("M7","M8","M9"):
            return ModuleResult(status=SKIPPED, reason="M6_no_diff")
    
    return await self._call_model(node_id, ...)
