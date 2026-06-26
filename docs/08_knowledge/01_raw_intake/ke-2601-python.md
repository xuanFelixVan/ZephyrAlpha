---
module_id: KE-2506------python-000
status: active
title: 9.1 异常层级（Python 库）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 9.1 异常层级（Python 库）

9.1 异常层级（Python 库）

```python
class VMError(Exception): ...                        # 基类
class VMConfigError(VMError): ...                    # 配置错误（启动即失败）
class VMEmbeddingError(VMError): ...                 # embedding 失败（模型加载 / OOM）
class VMStorageError(VMError): ...                   # ChromaDB 操作失败
class VMConflictError(VMError): ...                  # 幂等冲突 / update cascade 拒绝
class VMNotFoundError(VMError): ...                  # doc_id 不存在
class VMValidationError(VMError): ...                # schema 校验失败
class VMDegradedError(VMError): ...                  # 可降级但记录用（通常被 catch 后返回空结果）
```

HTTP 映射：`VMConfigError`→503 / `VMEmbeddingError`→422 / `VMStorageError`→500 / `VMConflictError`→409 / `VMNotFoundError`→404 / `VMValidationError`→400
