---
module_id: KE-1876
status: active
title: 2.3 shared-errors（统一错误层次）
category: module_blueprint
---

# 2.3 shared-errors（统一错误层次）

2.3 shared-errors（统一错误层次）

> **补全 ssot_guard.py:L103 标记的「尚未完成的 ZephyrBaseError 体系」。**
> 与 contracts/errors/ 的区别：contracts/errors/ 是 dataclass 值对象（跨层结构化错误传递），
> 本子模块是 Python Exception 继承树（throw/catch 统一入口）。

| 文件 | 职责 |
|------|------|
| `errors.py` | **ZephyrBaseError** + 12 子类——ConfigError / ContractError / SecurityError / ValidationError / TaskError / PipelineError / GateError / ContextError / FeedbackError / DataError / IOError / UnimplementedError |
