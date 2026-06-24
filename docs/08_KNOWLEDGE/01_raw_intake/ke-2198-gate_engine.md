---
module_id: KE-2105
status: active
title: 3.3 Gate Engine 集成（资产盘点门禁）
category: module_blueprint
---

# 3.3 Gate Engine 集成（资产盘点门禁）

3.3 Gate Engine 集成（资产盘点门禁）

新增 Gate `G?.asset_inventory_gate`：

```yaml
gate_id: "G_asset_inventory"
title: "资产盘点完整性门禁"
category: "inventory"
checks:
  - name: orphan_rate_check
    description: "孤儿率应 < 2%"
    rule: "orphan_count / total_assets < 0.02"
    severity: "P1"
  - name: ghost_rate_check
    description: "幽灵率应为 0%（注册表不引用已删除文件）"
    rule: "ghost_count == 0"
    severity: "P0"
  - name: last_reconciliation_check
    description: "最近一次对账应在 24h 内"
    rule: "now - last_reconciliation_time < 24h"
    severity: "P1"
  - name: health_score_check
    description: "健康评分不应低于 C"
    rule: "health_score in ['A', 'B', 'C']"
    severity: "P1"
```

---
