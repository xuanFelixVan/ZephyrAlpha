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

> 本域候选 **3** 条（原有 3 + harvest 0）。

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | DataFrame无运行时类型校验,下游D_FACTOR消费端要求Pydantic强类型契约 | D_DATA | 延后（deferred） | 一问通过 | P2 | D_FACTOR消费端明确要求Pydantic(KBG-0040强制) 等3条 | 2027-07-31 |
| CAND-L00007-001 | MOD-L00-007 存储(功能已由buffered_writer承接) | (已解决)存储抽象已由buffered_writer(MOD-L00-004)承接,后端读写已由ch_writer/ch_reader分层实现 | D_DATA | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-05 |
| CAND-L00008-001 | MOD-L00-008 缓存(功能已上移至H1_REDIS_HOT) | (已解决)缓存已由MOD-H1_REDIS_HOT(D_INFRA_RUNTIME)承接,是CP-01 SLO<10ms和CP-02降级的核心基础设施 | D_DATA | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-05 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### q1 已实现/重复（2 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-L00007-001 | MOD-L00-007 存储(功能已由buffered_writer承接) | (已解决)存储抽象已由buffered_writer(MOD-L00-004)承接,后端读写已由ch_writer/ch_reader分层实现 | D_DATA | buffered_writer.py(MOD-L00-004)在Provider和ch_writer之间插入缓冲层(裁定#ARCH-CH-003攒批写入层即存储抽象)。ch_writer.py(36990字节)+ch_reader.py+wal_codec/已分层实现存储后端。蓝图L145 storage列为C轨占位,代码已清理(2026-07-01)。17处调用ch_writer但多经buffered_writer解耦。 | MOD-L00-004(buffered_writer.py,裁定#ARCH-CH-003攒批写入层即存储抽象)+ch_writer.py/ch_reader.py(分层存储后端读写) |
| CAND-L00008-001 | MOD-L00-008 缓存(功能已上移至H1_REDIS_HOT) | (已解决)缓存已由MOD-H1_REDIS_HOT(D_INFRA_RUNTIME)承接,是CP-01 SLO<10ms和CP-02降级的核心基础设施 | D_DATA | tick_redis_cache.py blueprint_id=MOD-H1_REDIS_HOT domain=D_INFRA_RUNTIME production。h1_redis_hot.md(27972字节)在_cross_layer/database/sub_blueprints/。PIPELINE批量写入tick:{symbol}:latest,best-effort(Redis故障不阻断WAL主路径)。功能从D_DATA上移至D_INFRA_RUNTIME基础设施层(与MOD-EX-004幂等性上移shared/infra同类)。 | MOD-H1_REDIS_HOT(tick_redis_cache.py,D_INFRA_RUNTIME,production,PIPELINE批量写入+best-effort降级) |

### 一问通过（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | DataFrame无运行时类型校验,下游D_FACTOR消费端要求Pydantic强类型契约 | D_DATA | 首次登记,待D_FACTOR强制要求Pydantic或KBG-0040强制时重新评估 | DataFrame+dataclass(当前实现)。代价:无运行时类型校验,下游类型错误难发现 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2027-07-31 | yearly | CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | D_DATA | 延后（deferred） | 首次登记,待D_FACTOR强制要求Pydantic或KBG-0040强制时重新评估 |
| 2027-08-05 | yearly | CAND-L00007-001 | MOD-L00-007 存储(功能已由buffered_writer承接) | D_DATA | 否决（rejected） | rejected,确认功能已承接。存储抽象已由buffered_writer(MOD-L00-004裁定#ARCH-CH-003)承接,后端读写已由ch_writer/ch_reader分层实现。蓝图L145 storage列为C轨占位代码已清理。第一性原理裁定:YAGNI+AI开发减抽象层。软删除防误恢复 |
| 2027-08-05 | yearly | CAND-L00008-001 | MOD-L00-008 缓存(功能已上移至H1_REDIS_HOT) | D_DATA | 否决（rejected） | rejected,确认功能已上移。缓存已由MOD-H1_REDIS_HOT(tick_redis_cache.py D_INFRA_RUNTIME production)承接,功能上移至基础设施层(与MOD-EX-004同类)。保留=双真源风险。tick_redis_cache.py blueprint_id不改(从来属H1_REDIS_HOT体系)。软删除防误恢复 |
