---
doc_type: audit_report
title: 候选模块清单 — D_DATA_SEC
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_DATA_SEC 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **3** 条（原有 0 + harvest 3）。
> harvest 去重四态: likely_new=3

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0610 | Data Access Auditor 数据访问审计器 | 细粒度访问日志+查询模式分析+异常访问检测+敏感数据追踪+合规报告 | D_DATA_SEC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1312 | Data Masking Engine 数据脱敏引擎 | 静态/动态脱敏+格式保留加密+差分隐私噪声注入+脱敏策略路由 | D_DATA_SEC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2653 | Data Security Compliance Constraint 数据安全与合规约束 | 4级分类+RBAC+AES-256-GCM+AI脱敏 | D_DATA_SEC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 待评估（3 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0610 | Data Access Auditor 数据访问审计器 | 细粒度访问日志+查询模式分析+异常访问检测+敏感数据追踪+合规报告 | D_DATA_SEC | harvest待评估（likely_new） |  |
| CAND-HARVEST-1312 | Data Masking Engine 数据脱敏引擎 | 静态/动态脱敏+格式保留加密+差分隐私噪声注入+脱敏策略路由 | D_DATA_SEC | harvest待评估（likely_new） |  |
| CAND-HARVEST-2653 | Data Security Compliance Constraint 数据安全与合规约束 | 4级分类+RBAC+AES-256-GCM+AI脱敏 | D_DATA_SEC | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0610 | Data Access Auditor 数据访问审计器 | D_DATA_SEC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1312 | Data Masking Engine 数据脱敏引擎 | D_DATA_SEC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2653 | Data Security Compliance Constraint 数据安全与合规约束 | D_DATA_SEC | 候选待评（candidate） | harvest待评估（likely_new） |
