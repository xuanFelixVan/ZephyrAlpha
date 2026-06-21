---
module_id: KE-3028
status: active
title: 4.3 写入频率
category: session_log
---

# 4.3 写入频率

4.3 写入频率

- **强制写入**：Session 结束时（任何 ended_reason）
- **可选频繁写入**：每 15 分钟一次（作为 crash 防护），`ended_reason` 暂填 `idle_timeout`，后续被最终写入覆盖

---
