---
module_id: KE-2736
status: active
title: 模块蓝图 frontmatter（示例）
category: module_blueprint
ttl: permanent
---

# 模块蓝图 frontmatter（示例）

模块蓝图 frontmatter（示例）
module_id: "MOD-INF-006"
belongs_to: "MOD-MASTER-001"     #  ← 关联域蓝图 ID（必填）
```

| 如果... | `belongs_to` 值 | 何时 |
|------|------|------|
| 在 1 期创建的模块蓝图 | `MOD-MASTER-001` | 因为当前只有这个域蓝图 |
| 在 beta+ 创建的 L02 因子蓝图 | `MOD-DOMAIN-SIG-001` | 信号域集成蓝图（待创建）|
| 在 beta+ 创建的 L06 执行蓝图 | `MOD-DOMAIN-RISK-001` | 执行域集成蓝图（待创建）|
| 跨层基础设施模块（如 Telemetry）| `SYS-MASTER-001` | 全系统总蓝图|
