---
module_id: KE-module_blu-call_model-000
title: _call_model 入口
category: module_blueprint
---

# _call_model 入口

_call_model 入口
async def _call_model(self, module_id, prompt, ...):
    # L1: 输入检测
    if self._lsg is not None:
        l1_result = self._lsg.check_input(prompt)
        if not l1_result.safe:
            raise LSGInputBlocked(l1_result.reason)
    
    response = await self._api_call(model, prompt)
    
    # L3: 输出检测
    if self._lsg is not None:
        l3_result = self._lsg.check_output(response)
        if not l3_result.safe:
            logger.warning(f"LSG L3 blocked: {l3_result.reason}")
            return ModuleResult(status=FAILURE, errors=[l3_result.reason])
```
