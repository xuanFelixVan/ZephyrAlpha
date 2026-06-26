---
module_id: KE-2412
status: active
title: 7. Acceptance Criteria
category: module_blueprint
ttl: permanent
---

# 7. Acceptance Criteria

7. Acceptance Criteria

- 15 个新文件全部创建
- 5 个 P0 盲点功能可单元测试验证
- context_poisoning_monitor 可检测低成功率 KE
- context_diff_injector 可计算并注入增量 diff
- atomic_injector 的 shadow-then-swap 保证 4 层全或无
- emergency_kill_switch 的 /ce:kill 可在 <1s 内停止所有新注入
