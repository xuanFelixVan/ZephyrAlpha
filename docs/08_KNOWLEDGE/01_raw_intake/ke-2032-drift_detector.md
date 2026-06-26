---
module_id: KE-1941-----------drift-detector---003
status: active
title: 2.8 并发竞争与文件锁——Drift Detector 与 AI 施工的并发安全（决策 D-023-11）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.8 并发竞争与文件锁——Drift Detector 与 AI 施工的并发安全（决策 D-023-11）

2.8 并发竞争与文件锁——Drift Detector 与 AI 施工的并发安全（决策 D-023-11）

> **决策 D-023-11**：Drift detector 的自动修复和 AI 施工可能同时修改同一文件。引入乐观并发控制——自动修复前检查文件 mtime，若在 pre-fix 快照后已被修改（AI 正在施工），则放弃自动修复，改为生成建议。AI 施工侧在 task 派发时携带 drift context，避免在已知漂移区域施工。
>
> **决策依据**：100% AI 施工 + 运行时自动修复，二者并发写同一文件是确定性事件。乐观锁成本最低，阻断成本最高。

```yaml
concurrency_control:
  auto_fix_guard:
    before_fix:
      - "拍摄 pre-fix 快照（文件内容 + mtime + SHA256）"
      - "记录快照时间戳 T0"
    before_commit:
      - "检查目标文件 mtime：若 > T0 → 文件已被外部修改"
      - "action: ABORT auto-fix → 生成修复建议 → 记录冲突事件"
      - "若 mtime == T0 → 安全提交修复"

  ai_construction_guard:
    pre_task_injection:
      description: "AI task 派发时自动注入目标模块的漂移上下文"
      content:
        - "当前模块的 active drift events（state ≠ VERIFIED）"
        - "上次 DEEP scan 时间与结果摘要"
        - "与目标文件相关的已知漂移及其修复状态"
      purpose: "AI 在施工前就知道哪些区域有漂移，避免在漂移区域施工或与自动修复冲突"

  lock_free_design:
    principle: "不引入文件锁（避免死锁 + 复杂度）。乐观并发 + 冲突检测 + 重试即可"
    max_retry: 3
    retry_backoff: "exponential: 1s → 2s → 4s"

  conflict_resolution:
    priority_rule: "AI 施工 > 自动修复"
    rationale: "AI 施工是主动变更（创造价值），自动修复是被动补偿（修正偏差）。施工优先，修复等施工完成后重新评估"
```
