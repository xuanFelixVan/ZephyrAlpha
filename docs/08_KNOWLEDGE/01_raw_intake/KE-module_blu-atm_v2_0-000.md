---
module_id: KE-module_blu-atm_v2_0-000
title: ATM v2.0 关键特性验证
category: module_blueprint
---

# ATM v2.0 关键特性验证

ATM v2.0 关键特性验证

| # | 特性 | 蓝图要求 | 验证方式 |
|---|------|---------|---------|
| 1 | 两阶段提交 | phase_1_prepare → phase_2_commit | 审查 `atomic_transaction_manager.py` |
| 2 | 幂等去重 | tx_idempotency 表 + 重复 tx_id → TransactionError | 搜索 `tx_idempotency` / `TransactionError` |
| 3 | 补偿事务 | rename 失败 → compensation event + COMPENSATED | 搜索 `compensat` |
| 4 | 超时控制 | 30s 事务级超时，超时自动 ROLLBACK | 搜索 `timeout` / `30` |
| 5 | 文件原子写入 | tmp → fsync → os.replace | 搜索 `os.replace` / `tmp` |
