---
module_id: KE-2530-------11-000
status: active
title: 95/4/1 分布监控（§11 目标分布）
category: module_blueprint
---

# 95/4/1 分布监控（§11 目标分布）

95/4/1 分布监控（§11 目标分布）
distribution_targets:
  auto_guard_pct: 4       # auto_guard ≤ 4%
  agent_review_pct: 95    # agent_review ≥ 95%
  owner_approval_pct: 1   # owner_approval ≤ 1%
  alert_threshold_pct:    # 偏离目标 > 50% → 告警
    auto_guard_max: 8
    owner_approval_max: 3
```

**操作码与 Gate Engine 映射**：

| 操作码 | Gate 判定 | 是否阻断 commit | auto_fix 可用性 |
|:---:|:---:|:---:|:---:|
| `CRITICAL` | FAIL | ✅ 阻断 | ❌ 不自动修（需人工） |
| `ERROR` | FAIL | ✅ 阻断 | ✅ 可自动修（高置信度） |
| `WARN` | WARN | ❌ 不阻断 | ❌ 不自动修 |
| `INFO` | PASS | ❌ 不阻断 | ❌ |
| `SKIP` | PASS（跳过） | ❌ | ❌ |
| `SUPPRESS` | PASS（完全压制） | ❌ | ❌ |
