---
module_id: KE-1718--------drift-detector-----002
status: active
title: 2.15 多实例竞态——Drift Detector 自身并发安全（决策 D-023-24）
category: module_blueprint
ttl: permanent
---

# 2.15 多实例竞态——Drift Detector 自身并发安全（决策 D-023-24）

2.15 多实例竞态——Drift Detector 自身并发安全（决策 D-023-24）

> **决策 D-023-24**：Post-commit 触发 LIGHT scan + 定时 periodic scan + Owner 手动 on-demand scan 可能同时运行。引入 scan mutex——同一时间最多一个 scan 实例在运行。新触发排队或合并。scan_id 写入 lock file，避免两实例同时写 drift_events。
>
> **决策依据**：2.8 解决了 detector vs AI 的并发，但没有解决 detector vs detector 自身的并发。两个 scan 同时跑会导致 drift_events 重复写入 + 告警重复发送。

```yaml
instance_mutex:
  lock_mechanism:
    method: "文件锁——data/drift_scan.lock"
    content: "pid + scan_id + scan_start_time + scan_level"
    timeout: "锁持有超过 scan SLO × 2 → 判定为 stale lock → 强制清除 + 通知 Owner"

  collision_policy:
    same_level_collision:
      description: "两个 LIGHT scan 或两个 DEEP scan 同时触发"
      action: "后者排队——等待前者完成后执行（max wait = SLO × 2）"

    level_preemption:
      description: "LIGHT scan 正在跑，DEEP scan 被触发"
      action: "DEEP 排队等待 LIGHT 完成——LIGHT 优先级高（post-commit 必须快）"

    reverse_preemption:
      description: "DEEP scan 正在跑，LIGHT scan 被触发（post-commit）"
      action: "LIGHT scan 使用 DEEP scan 的当前进度作为缓存基础——不等待、不冲突"
      note: "DEEP scan 已完成模块的结果对 LIGHT scan 直接有效（只要 mtime 未变）"

  merge_strategy:
    description: "若排队队列中已有同 level scan → 合并（后者覆盖前者——因为后者基于更新的 HEAD）"
```
