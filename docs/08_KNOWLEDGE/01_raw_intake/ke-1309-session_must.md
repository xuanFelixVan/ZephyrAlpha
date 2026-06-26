---
module_id: KE-1222-----must-005
title: 强制二选一处置（session 结束前 MUST 完成）
category: governance_rule
ttl: permanent
---

# 强制二选一处置（session 结束前 MUST 完成）

强制二选一处置（session 结束前 MUST 完成）

| 路径 | 条件 | 操作 |
|------|------|------|
| **归档** | 文件有持续使用价值 | ①移动到标准三目录之一（`scripts/governance/` / `tests/` / `src/zephyr/`）②注册到 `script-manifest.yaml` 或对应注册表 |
| **删除** | 文件为一次性检查/临时验证/实验脚本 | 物理删除（`DeleteFile` 或 `Remove-Item`），不留残骸 |
