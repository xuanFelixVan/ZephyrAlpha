---
module_id: KE-1735
status: active
title: 2.18 合规映射 —— 法律护栏
category: module_blueprint
ttl: permanent
---

# 2.18 合规映射 —— 法律护栏

2.18 合规映射 —— 法律护栏

> **对标**：中国信通院行为护栏六维度（最小权限、人机共决、输入隔离、输出脱敏、操作审计、策略引擎）+ EU AI Act 高风险AI系统要求。

```yaml
compliance_mapping:
  # === 法律法规映射 ===
  legal_mapping:
    - regulation: "EU AI Act Art.14 (Human Oversight)"
      requirement: "高风险AI系统必须有有效的人类监督"
      implementation: "硬中断协议 (§2.9) + 反自动化偏见强制审查 (§2.15)"
      strength: "不可削弱——法律要求"

    - regulation: "中国《生成式人工智能服务管理暂行办法》"
      requirement: "提供安全、可靠的服务"
      implementation: "三级升级策略的全部 blocked 规则"

    - regulation: "中国信通院—人机共决机制"
      requirement: "高风险操作必须有人的最终确认"
      implementation: "blocked 规则+通知改为——blocked→通知Owner→等待确认→收到确认才释放"
      strength: "blocked 通知改为同步等待确认（不是异步放行）"

  # === 规则强度分类 ===
  rule_strength:
    hard_legal:
      rules: ["ESC-003", "ESC-008", "ESC-GIT-001", "ESC-DB-002"]
      description: "法律合规强制——不可由 Owner 覆盖"
      override_allowed: false

    strong_recommendation:
      rules: ["ESC-001", "ESC-002", "ESC-006", "ESC-007"]
      description: "强烈推荐——Owner 可通过紧急覆盖绕过"
      override_allowed: "仅紧急覆盖 (§2.9)"

    configurable:
      rules: ["ESC-009", "ESC-010", "ESC-011"]
      description: "可配置——Owner 可调整阈值"
      override_allowed: "是的——通过 §2.5 change_process"

  # === blocked 同步确认（合规增强） ===
  blocked_confirmation:
    old: "异步通知 Owner + 阻塞操作"
    new: "阻塞操作 + 同步通知 Owner → 等待 Owner 确认 → (确认)释放操作 / (拒绝)永久阻断"
    timeout: "24h 内无响应→永久阻断"
    reason: "对齐'人机共决'——人的确认是释放条件，不是事后告知"
```

---
