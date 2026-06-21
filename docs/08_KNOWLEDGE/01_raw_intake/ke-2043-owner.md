---
module_id: KE-1952----------owner-003
status: active
title: 2.9 硬中断协议 —— Owner的最终控制权
category: module_blueprint
---

# 2.9 硬中断协议 —— Owner的最终控制权

2.9 硬中断协议 —— Owner的最终控制权

> **对标**：Anthropic Agent Framework —— "humans can stop Claude whenever they want" + Claude Code 的 Esc 两次回退。

```yaml
hard_interrupt:
  # === 硬中断触发方式 ===
  triggers:
    explicit_stop:
      keywords: ["停止", "stop", "halt", "不要做", "让我来", "取消"]
      action: "立即终止当前操作 + 保存当前状态 + 等待 Owner 下一条指令"
      override_level: "最高——绕过所有规则引擎"

    emergency_rewind:
      keywords: ["回退", "rewind", "撤销", "undo"]
      action: "回退到最近 checkpoint + 恢复对话上下文"
      scope: "当前 session 的所有变更"

  # === 硬中断后的行为 ===
  post_interrupt:
    state_save: "中断点状态写入 HANDOFF/INTERRUPT-{timestamp}.yaml"
    escalation_reset: "中断后恢复时，升级级别重置为 autonomous（信任重建）"
    require_explicit_continue: "Owner 必须明确说'继续'/'继续做'才能恢复AI操作"

  # === 紧急覆盖（Emergency Override） ===
  emergency_override:
    purpose: "Owner确认某个blocked操作是安全且必要的"
    trigger: "Owner 明确指令 + 包含理由"
    constraints:
      - "一次性有效——操作完成后覆盖自动失效"
      - "写入独立审计日志（EMERGENCY-OVERRIDE-{timestamp}）"
      - "覆盖期间所有操作仍写审计记录"
      - "覆盖不适用于 ESC-008（API Key/Secret——永不可覆盖）"
```

---
