---
module_id: KE-3448
title: 4.9 架构分层条件禁止
category: documentation
---

# 4.9 架构分层条件禁止

4.9 架构分层条件禁止

| #       | 条件禁止行为                     | 触发条件                      | 替代方案                                                        | 来源                            |
| ------- | -------------------------- | ------------------------- | ----------------------------------------------------------- | ----------------------------- |
| COND-30 | L02-L07 直接调用 LLM Providers | 非 L08 层代码调用 LLM API 时     | 必须通过 L08 LSG 代理                                             | technology_architecture.md |
| COND-31 | 业务数据写入治理 SQLite            | 向治理 SQLite 写入数据时          | 治理 SQLite 只存治理数据，OHLCV/因子等业务数据走专用存储                         | adr-0030                      |
| COND-32 | 在 contracts 目录放业务逻辑        | 向 shared/contracts/ 添加代码时 | 只放数据结构定义（dataclass / Protocol / Enum / Literal / TypedDict） | contracts/__init__.py         |
