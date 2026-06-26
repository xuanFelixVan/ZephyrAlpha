---
module_id: KE-2362----------canary-deploymen-000
status: active
title: 6.11 检测器金丝雀部署（Canary Deployment）
category: module_blueprint
ttl: permanent
---

# 6.11 检测器金丝雀部署（Canary Deployment）

6.11 检测器金丝雀部署（Canary Deployment）

```yaml
detector_canary:
  description: "检测器逻辑更新时，先以 shadow 模式对比新旧版本——确认行为变更符合预期后再全量切换"

  workflow:
    1. "新版本检测器部署为 canary_detector（独立 ID，结果不入 drift_events）"
    2. "对 N 个代表性模块同时跑 v1 和 v2 → 对比结果差异"
    3. "差异分类：NEW_FINDING（v2 发现 v1 没发现）/ LOST_FINDING（v1 发现 v2 没发现）/ CHANGED_SEVERITY"
    4. "Owner 审查差异 → approve → 全量切换 / reject → 回退 v2"

  metrics:
    - "false_positive_rate_change: v2 FP% - v1 FP%"
    - "new_findings_count / lost_findings_count"
    - "execution_time_change_ms"

  auto_rollback:
    condition: "v2 false_positive_rate > 2 × v1 false_positive_rate"
    action: "自动回退 v2，通知 Owner"
```
