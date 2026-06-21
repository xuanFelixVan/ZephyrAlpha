---
module_id: KE-3244-----constitution-005
title: 3.1 宪法层（Constitution）
category: documentation
---

# 3.1 宪法层（Constitution）

3.1 宪法层（Constitution）

| 属性 | 值 |
|------|-----|
| 存储位置 | `meta/behavior-boundaries-standard.md`（PS-STD-003） |
| 内容 | 所有 ABS 条目 + 条件性不可逆的 COND 条目 |
| 判定标准 | 违反后后果不可逆（包括条件性不可逆） |
| 修改门槛 | Owner 批准 + ADR |
| AI 权限 | `immutable_core`——AI 禁止自主修改 |
| 编号体系 | ABS-XX |
| 加载策略 | **热记忆（Hot Memory）**——会始终在 AI 系统提示中。对应 CR-010（P0）：Session 活跃时治理规则和门禁规则必须 always loaded |
