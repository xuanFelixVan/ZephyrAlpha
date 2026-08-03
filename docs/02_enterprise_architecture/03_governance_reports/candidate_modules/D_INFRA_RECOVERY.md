---
doc_type: audit_report
title: 候选模块清单 — D_INFRA_RECOVERY
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_INFRA_RECOVERY 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **1** 条（原有 1 + harvest 0）。

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-DR-001 | Offsite Backup / 异地备份 | audit 7.7 发现本地 restic 备份与主库同物理站点,不满足 3-2-1 备份原则的异地要求 | D_INFRA_RECOVERY | 否决（rejected） | q2 无需求驱动 | P2 | 系统升级为多用户/多站点场景(当前单用户) 等3条 | 2027-07-31 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### q2 无需求驱动（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-DR-001 | Offsite Backup / 异地备份 | audit 7.7 发现本地 restic 备份与主库同物理站点,不满足 3-2-1 备份原则的异地要求 | D_INFRA_RECOVERY | rejected,overruled_by_user #ARCH-CH-032。除非场景升级为多用户/多站点,否则不再评估 | 本地外接盘备份(F:\restic-zephyr,主库+外接盘=2份)。代价:无,用户已确认足够 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2027-07-31 | yearly | CAND-DR-001 | Offsite Backup / 异地备份 | D_INFRA_RECOVERY | 否决（rejected） | rejected,overruled_by_user #ARCH-CH-032。除非场景升级为多用户/多站点,否则不再评估 |
