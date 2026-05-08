---
module_id: KE-governance-4_1_p0-000
title: 4.1 P0 变更
category: governance_rule
---

# 4.1 P0 变更

4.1 P0 变更

```
1. Owner 识别需要变更的 frozen 文件
2. Owner 直接编辑文件（不通过 AI）
3. Owner 更新 document-metadata-index.yaml
4. Owner 在 Session Log 中记录变更原因
5. Owner 通知所有正在工作的 AI（Session Log next_session_handover）
```

**禁止**：AI 执行 P0 变更（即使 Owner 口头要求——必须 Owner 手动操作）。

**受 P0 约束的文件示例**（按属性判定）：

| 文件 | stability | scope |
|------|-----------|-------|
| PS-STD-001 metadata-registry.md | frozen | global |
| PS-STD-002 document-structure-standard.md | frozen | global |
| PS-STD-003 behavior-boundaries-standard.md | frozen | global |
