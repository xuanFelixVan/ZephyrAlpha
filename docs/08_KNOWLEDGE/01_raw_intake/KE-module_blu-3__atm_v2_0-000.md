---
module_id: KE-module_blu-3__atm_v2_0-000
title: 3. ATM v2.0 原子事务管理器
category: module_blueprint
---

# 3. ATM v2.0 原子事务管理器

3. ATM v2.0 原子事务管理器

```yaml
atm_contract: P0-DB-ATM-v2
description: "跨 SQLite / 文件系统的两阶段提交（v2.0 增强）"

version: "2.0.0"

phase_1_prepare:
  - 所有参与者（SQLite + 文件系统操作）进入 PREPARE 状态
  - 在 tx_idempotency 表登记为 PREPARED（防止重复提交）
  - 任何参与者 PREPARE 失败 → 全部 ROLLBACK + 标记 ROLLED_BACK

phase_2_commit:
  - 预验证所有 tmp 文件存在且可读
  - SQLite COMMIT
  - 对所有 staged 文件执行 os.replace(tmp, target)
  - 更新 tx_idempotency 为 COMMITTED
  - 文件 rename 失败但 SQLite 已 COMMIT → 写 compensation event + 标记 COMPENSATED

timeout: 30s（事务级，超时自动 ROLLBACK）
idempotency: tx_idempotency 表去重，同一 tx_id 重复调用 commit() 会报 TransactionError
fallback: WAL 模式自动回退 → 不丢数据
```

---
