---
module_id: KE-governance-7-003
title: 7. 自动归档
category: governance_rule
---

# 7. 自动归档

7. 自动归档

| 规则 | 条件 | 动作 |
|------|------|------|
| deprecated 满 6 个月 | `status: deprecated` 且距今 ≥ 180 天 | `git mv` 移入 `archive/` 子目录，status 保持 `deprecated` |
| 归档保留 | `ttl: permanent` 规则 | 永久保留，不删除 |

> **对标状态**：阈值"5"对照 Google API Deprecation Policy（12个月默认，紧急 3 个月）→ 本项目取 5 因以下是 6 人微团队。归档期"6个月"对照 Kubernetes Deprecation Policy（~3 releases = ~9个月最短）→ 本项目 6 月为最低安全期。beta+ 需做正式影响评估（ISO 42001 §8）。

---
