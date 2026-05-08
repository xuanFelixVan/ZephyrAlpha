---
module_id: KE-documentat-v1_1_0_2026-05-06___session-004
title: v1.1.0（2026-05-06 同 session）
category: documentation
---

# v1.1.0（2026-05-06 同 session）

v1.1.0（2026-05-06 同 session）

| 修复项 | 文件 | 说明 |
|--------|------|------|
| 双树同步工具 | `scripts/governance/d5_architecture/check_dual_tree_sync.py` | 新建 GATE-DTS 闸门，检测 C 轨同步、B 轨差异、文件名映射、module_id 一致性、technology-landscape deprecated 声明 |
| 脚本清单更新 | `scripts/governance/script_manifest.yaml` | 重新生成，178 脚本，GATE-DTS 已注册 |
| P1-002 修复 | `architecture-model/technology-landscape.yaml` | 增加 `status: deprecated` + `deprecation_reason`，指向 EA 树完整版 |
| P2-001 修复 | `docs/.../architecture-model/infra/core-services.yaml` | 增加 `parent_layer: L12` |
| FF maturity 标记 | `scripts/arch_guard/_manifest.yaml` | FF-001/004/016/010 增加 `maturity` + `phase_required` 字段 |
| 报告更新 | `docs/09_audit/reports/AUDIT-04-report.md` | 版本升至 v1.1.0，更新所有修复状态 |

---

*本报告由 Trae AI Agent 于 2026-05-06 生成，基于对 docs/02_enterprise_architecture/ 和 architecture-model/ 全目录的静态分析。如需执行修复，建议按 §三 优先级矩阵从 P0 开始逐级推进。*
