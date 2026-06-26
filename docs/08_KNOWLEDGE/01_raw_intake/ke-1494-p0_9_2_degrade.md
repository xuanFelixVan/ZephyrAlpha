---
module_id: KE-1404------p0--9-2-degrade-001-000
title: 11.6 降级路径 P0（§9.2 DEGRADE-001 对应）
category: module_blueprint
ttl: permanent
---

# 11.6 降级路径 P0（§9.2 DEGRADE-001 对应）

11.6 降级路径 P0（§9.2 DEGRADE-001 对应）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-D1 | ChromaDB 读失败降级 | mock chroma 抛异常 | `await vm.search(...)` | 返回 `[]` + `degraded=True`，不抛异常 |
| P0-D2 | 空 Collection 首次 search | 未 bootstrap | `await vm.search(...)` | 返回 `[]` + `degraded=True` + reason="empty_collection" |
| P0-D3 | 降级日志落盘 | 触发 DEGRADE-001 | 检查 `logs/vms_degrade.log` | 含触发原因 + 时间戳 + 调用方 + query sha256 |

---
