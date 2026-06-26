---
module_id: KE-1033
status: active
title: 8.3 保留策略
category: governance
ttl: permanent
---

# 8.3 保留策略

8.3 保留策略

- **门禁运行记录**：永久保留（审计合规）
- **artifact_path 指向文件**：TTL 30 天，过期由 `scripts/governance/cleanup_gate_artifacts.py` 清理
- **每月审计汇报**：统计 `SELECT gate_id, COUNT(*), AVG(passed)` 输出到 `docs/09_audit/reports/monthly/gates-YYYYMM.md`

---
