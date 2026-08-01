---
doc_type: audit_report
title: 候选模块清单 — D_DATA
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_DATA 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **1** 条（原有 1 + harvest 0）。

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | 把数据层从pandas DataFrame换成Pydantic强类型模型，运行时能自动校验类型对不对。现在DataFrame够用，等下游真强制要求再迁。 | D_DATA | 延后（deferred） | q2 无需求驱动 | P2 | D_FACTOR消费端明确要求Pydantic(KBG-0040强制) 等3条 | 2027-07-31 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### q2 无需求驱动（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | 把数据层从pandas DataFrame换成Pydantic强类型模型，运行时能自动校验类型对不对。现在DataFrame够用，等下游真强制要求再迁。 | D_DATA | 首次登记,待D_FACTOR强制要求Pydantic或KBG-0040强制时重新评估 | DataFrame+dataclass(当前实现)。代价:无运行时类型校验,下游类型错误难发现 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2027-07-31 | yearly | CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | D_DATA | 延后（deferred） | 首次登记,待D_FACTOR强制要求Pydantic或KBG-0040强制时重新评估 |
