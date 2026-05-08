---
module_id: KE-governance-8_3-003
title: 8.3 保留策略
category: governance
---

# 8.3 保留策略

8.3 保留策略

- **门禁运行记录**：永久保留（审计合规）
- **artifact_path 指向文件**：TTL 30 天，过期由 `scripts/governance/cleanup_gate_artifacts.py` 清理
- **每月审计汇报**：统计 `SELECT gate_id, COUNT(*), AVG(passed)` 输出到 `docs/09_audit/reports/monthly/gates-YYYYMM.md`

---
