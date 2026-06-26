---
module_id: KE-3562
title: 3.1 分层要求
category: governance
ttl: permanent
---

# 3.1 分层要求

3.1 分层要求

| 层级 | mypy 模式 | 要求 |
|------|:---:|------|
| L00-L01（数据源/基础设施） | `strict` | 100% 覆盖，`disallow_untyped_defs=true` |
| L02-L08（因子→界面） | 关键接口 `strict` | 跨模块接口 100%，内部实现 80%+ |
| L09-L15（上层业务） | public API `strict` | public 函数/方法 100%，private 不强制 |
