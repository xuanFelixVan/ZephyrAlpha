---
module_id: KE-699
title: 1.3 核心原则
category: governance
ttl: permanent
---

# 1.3 核心原则

1.3 核心原则

| 原则 | 说明 |
|------|------|
| **双门同时声明** | 每个 stage 必须在 frontmatter 同时声明 `exit_criteria` + `next_stage_entry_criteria` |
| **机器可验证优先** | 每条 criterion 必须能被 `validate_stage_*.py` 自动校验；不可机器验证的标注 `manual: true` |
| **HiL 强制节点** | Stage 过渡必须有用户显式点头（不可跳过）|
| **回滚协议配套** | 每个 stage 都有 `rollback_snapshot_path`，过渡失败可回退 |
| **零暗门**：next_stage_entry_criteria 必须是 stage N-1 的 exit_criteria 子集 | 避免"下一个 stage 引入 stage N-1 没提到的依赖" |

---
