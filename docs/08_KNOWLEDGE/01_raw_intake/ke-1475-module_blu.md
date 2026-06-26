---
module_id: KE-1385
status: active
title: 11.1 异常层级
category: module_blueprint
ttl: permanent
---

# 11.1 异常层级

11.1 异常层级

```python
class FLEError(Exception): ...
class FLEConfigError(FLEError): ...
class FLESinkError(FLEError): ...                     # record_metric 写入失败
class FLEAnalyzerError(FLEError): ...                 # 基线计算失败
class FLEActionDispatchError(FLEError): ...           # 下游 Protocol 调用失败
```
