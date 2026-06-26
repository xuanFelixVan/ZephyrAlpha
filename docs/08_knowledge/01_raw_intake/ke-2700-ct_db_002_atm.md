---
module_id: KE-2603
status: active
title: CT-DB-002：ATM 事务契约
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# CT-DB-002：ATM 事务契约

CT-DB-002：ATM 事务契约

```yaml
contract_id: CT-DB-002
provider: MOD-DATABASE (AtomicTransactionManager)
consumers:
  - MOD-TASK_SYSTEM (task-system)
  - MOD-FEEDBACK_LOOP (feedback-loop)

operations:
  transaction:
    isolation: "BEGIN IMMEDIATE（防写锁饥饿）"
    timeout: "30s 事务级超时——超时自动 ROLLBACK"
    idempotency: "tx_idempotency 表去重——重复 tx_id → TransactionError"
    compensation: "SQLite COMMIT 成功但文件 rename 失败 → compensation event + COMPENSATED 状态"

  write_file:
    safety: "InputSanitizer.validate_path（路径穿越防护）"
    atomicity: "tmp → fsync → os.replace（崩溃安全）"
    rollback: ".bak 文件恢复"
```
