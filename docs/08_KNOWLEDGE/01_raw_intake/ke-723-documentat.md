---
module_id: KE-648
status: active
title: Step 6：上线验证
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# Step 6：上线验证

Step 6：上线验证

1. 在 dev 环境运行 72 小时，通过标准：
   - 断连次数 ≤ 3 次（72h 内）
   - 重连成功率 = 100%
   - 数据延迟 P99 ≤ 500ms
2. 确认数据质量达标
3. **禁止在交易时段执行上线切换**——切换到 prod 必须在盘后（A股 15:30 后）或周末执行
4. Owner 审批后切换到 prod 环境
5. prod 切换后监控 48 小时，异常次数 ≤ 1 次方可通过
