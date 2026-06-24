---
module_id: KE-1779-------1-------------003
status: active
title: 2.20 Owner 缺席模式——1人维护的独特性挑战（决策 D-023-34）
category: module_blueprint
---

# 2.20 Owner 缺席模式——1人维护的独特性挑战（决策 D-023-34）

2.20 Owner 缺席模式——1人维护的独特性挑战（决策 D-023-34）

> **决策 D-023-34**：1人维护下，Owner 可能因休假/出差/生病离线 1-2 周。在此期间漂移预算会重置、hotfix 会过期、storm 可能发生。Drift detector 不能在 Owner 缺席时堆积 P0 告警或错误地阻断施工。引入 absence mode——预设的降级运维策略。
>
> **决策依据**：这是 4 轮审查中从未触及的核心问题。所有 SRE/DevOps 方案都假设多人值班，但你是 1 人。缺席时系统必须能自我保护。

```yaml
absence_mode:
  activation:
    - manual: "Owner 手动声明 ABSENCE_START → ABSENCE_END"
    - auto_detect: "连续 48h 无人确认任何告警 → 自动进入 LENIENT_ABSENCE"

  modes:
    LENIENT:
      description: "Owner 短期离线（< 3 天）——宽松但不放任"
      policies:
        - "漂移预算消耗阈值从 100% 提升到 200%（双倍容忍）"
        - "自动修复仍执行（修复比不修复好）"
        - "告警聚合为日报（不逐条推送）"
        - "级联故障检测正常工作（P0 仍告警——因为这是安全问题）"

    SURVIVAL:
      description: "Owner 长期离线（> 3 天）——仅维持系统不崩溃"
      policies:
        - "漂移预算完全关闭（不阻断任何施工）"
        - "自动修复关闭（风险太高，无 Owner 审查）"
        - "告警静默存储，Owner 回来后批量推送摘要"
        - "所有扫描正常执行但结果仅存档"
        - "热修复 72h 过期规则暂停（因为没人处理）"

  return_handover:
    description: "Owner 标记 ABSENCE_END → 系统生成缺席期摘要"
    report_content:
      - "缺席期间产生的漂移总数 / 按维度分布"
      - "缺席期间自动修复执行次数 / 成功率"
      - "缺席期间级联故障 / 风暴事件"
      - "当前预算状态（哪些模块超支）"
      - "Top 5 需要 Owner 立即处理的事项（ROI 排序）"
    report_format: "Feishu 推送 + CLI 可读摘要"
```
