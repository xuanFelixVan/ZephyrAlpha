---
module_id: KE-module_blu-2_15___________owner_________d-005
title: 2.15 反自动化偏见 —— Owner 审查保障（决策 D-022-09）
category: module_blueprint
---

# 2.15 反自动化偏见 —— Owner 审查保障（决策 D-022-09）

2.15 反自动化偏见 —— Owner 审查保障（决策 D-022-09）

> **决策 D-022-09**：系统必须主动对抗Owner的自动化偏见——不是假设Owner会认真审查，而是用强制机制确保审查发生。包括随机抽样阻断、审查率监控、审查质量评估、反谄媚校准。
>
> **决策依据**：Georgetown CSET 自动化偏见报告——流畅输出"侵蚀用户对AI系统进行有意义控制的能力"。EU AI Act 已收录自动化偏见条款。实际数据：74%从业者用人工验证但Agent输出越来越逼真→"越像真话越不审查"。AI Sycophancy (Anthropic)——58.19%模型谄媚→升级引擎可能"讨好"Owner的意见。

```yaml
anti_automation_bias:
  # === 强制随机抽样审查 ===
  forced_review:
    mechanism: "随机抽取 5% 的 ''autonomous'' 操作——暂停执行→展示diff→要求Owner确认"
    purpose: "刺破自动化偏见——即使系统判定安全，Owner偶尔也要看"
    frequency: "每 20 次 autonomous 操作至少触发 1 次"
    timeout: "30s 内无响应 → 操作中止 + 记录为 '未经审查的自主操作'"

  # === 审查率监控 ===
  review_rate_monitoring:
    metrics:
      - "auto_guard 通知的 Owner 响应时间（趋势检测——是否越来越慢？）"
      - "CRITICAL 通知的确认率（是否每个blocked通知都被看了？）"
      - "连续无关确认模式（Owner是否在机械点'确认'？→检测重复模式）"
    fatigue_detection:
      condition: "响应时间连续增长 > 50% 或 确认率 < 70%"
      action: "降低 auto_guard 阈值（更激进地升级）+ 系统提示 '检测到审查疲劳'"

  # === 审查质量评估 ===
  review_quality:
    check: "对比 Owner 确认 '安全' 的操作 vs 后续实际审计结果"
    metric: "Owner 漏审率——放行但后来证明有问题的比例"
    target: "≤ 1%"

  # === 反谄媚机制 ===
  anti_sycophancy:
    rule: "升级引擎在输出判定结果时——不能因Agent/Owner的语气/身份而偏袒"
    implementation: "引擎不接收Agent的身份元数据/情感信息→只看操作内容"
    calibration: "定期回测引擎判定一致性——同一操作不同包装→判定应相同"
```

---
