---
module_id: KE-2322-------git-bisect-------d-0-000
status: active
title: 5.6 漂移溯源——Git Bisect 集成（决策 D-023-15）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5.6 漂移溯源——Git Bisect 集成（决策 D-023-15）

5.6 漂移溯源——Git Bisect 集成（决策 D-023-15）

> **决策 D-023-15**：当漂移被检测到时，自动 git bisect 定位引入漂移的 commit。利用 drift_events 的 created_at 时间窗口缩小 bisect 范围。
>
> **决策依据**：AI 施工场景下，漂移的根因溯源比修复本身更重要——知道"哪个 AI session 引入的"才能避免同样问题再次发生。传统 drift detection 只告诉你"漂了"，不告诉你"谁干的、什么时候干的"。

```yaml
git_bisect_integration:
  trigger: "DETECTED 事件——非周期性漂移（周期性漂移通常是系统性问题，非单点引入）"

  scope_narrowing:
    - "last_known_good: 上次 DEEP scan PASS 的 commit hash"
    - "first_known_bad: 当前 HEAD"
    - "bisect_range: [last_known_good, first_known_bad]"
    - "若范围 > 50 commits → 提示 Owner 缩小范围（可能基线过期）"

  automation:
    - "git bisect start first_known_bad last_known_good"
    - "对每个 bisect step → 跑触发该漂移的 detector（LIGHT 扫描）"
    - "detector PASS → git bisect good"
    - "detector FAIL → git bisect bad"
    - "定位到引入 commit → 记录到 drift_events.root_cause_commit"

  output:
    - "root_cause_commit: <hash>"
    - "author: <git author>"
    - "commit_message: <message>"
    - "changed_files: [list]"
    - "ai_session_hint: 从 commit message 中提取 session_id（若 AI commit 规范中包含）"

  bisect_cache:
    description: "缓存已 bisect 的 detector × commit 结果——避免重复跑"
    ttl: "永久（同一 commit 对同一 detector 的结果不变）"
```

---
