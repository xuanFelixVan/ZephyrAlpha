---
module_id: KE-894
status: active
title: 4.1.3 降级策略
category: governance
ttl: permanent
---

# 4.1.3 降级策略

4.1.3 降级策略

- **P0 失败** → `GateViolationError` 抛出；`task_repo.transition` 回滚，任务保持 `PENDING`；调用方必须修正文件后重试
- **P1 失败** → 记 `gates.details.p1_count+1`，继续推进；每日聚合 `p1_count ≥ 10` 触发 Owner 告警
- **`auto_fix` 特例**：G1-C03 允许引擎先执行 CRLF→LF 替换再重新验证；成功后视为 PASS 并 `events.insert(auto_fix)`
