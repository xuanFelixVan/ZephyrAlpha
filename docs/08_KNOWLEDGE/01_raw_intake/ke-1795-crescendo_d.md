---
module_id: KE-1704--------crescendo------d-0-005
status: active
title: 2.13 心理说服防御与Crescendo检测（决策 D-022-07）
category: module_blueprint
ttl: permanent
---

# 2.13 心理说服防御与Crescendo检测（决策 D-022-07）

2.13 心理说服防御与Crescendo检测（决策 D-022-07）

> **决策 D-022-07**：升级引擎必须内建心理说服抵抗力——不是只匹配硬条件，还要检测话术操纵意图和Crescendo渐进升级模式。当检测到Cialdini六原则攻击特征（权威声明/互惠暗示/社会认同/稀缺制造/情感触发/承诺一致性）时，操作需强制升级至少一级。
>
> **决策依据**：UPenn研究——Cialdini六原则系统性地以100%通过率绕过GPT-4o Mini护栏。GOODLIAR (ACL 2025)——RL生成的欺骗性上下文可永久改写LLM核心信念。升级引擎自身也是LLM→同样易受话术操纵。

```yaml
persuasion_defense:
  # === Cialdini 六原则检测 ===
  detection_patterns:
    authority:
      keywords: ["作为...认证的", "上级要求", "官方批准", "合规要求", "FDA/ISO/PCI"]
      action: "操作升级一级 (autonomous→auto_guard, auto_guard→blocked)"
      reason: "权威声明是最有效的绕过手段"

    reciprocity:
      keywords: ["我已经帮了你", "作为回报", "之前你答应过", "礼尚往来"]
      action: "操作升级一级"
      reason: "互惠感会降低引擎的判定阈值"

    social_proof:
      keywords: ["所有人都这样做", "行业惯例", "最佳实践公认", "主流做法"]
      action: "操作升级一级"

    scarcity:
      keywords: ["截止时间", "最后一次机会", "再不...就来不及", "紧急", "必须立即"]
      action: "操作升级一级 + 自动延迟 30s（冷却验证）"

    commitment_consistency:
      pattern: "先提出无害请求→被批准→再升级到有害请求（Crescendo模式）"
      detection: "跨轮次主题漂移检测——同一对话中话题从安全域漂移到危险域"
      action: "从漂移点开始，后续操作全部 auto_guard 起步"

    affective_priming:
      keywords: ["嘿", "伙计", "老兄", "拜托了", "求你了", "就这一次"]
      action: "操作升级一级"

  # === Crescendo 渐进模式检测 ===
  crescendo_detection:
    tracking: "维护对话主题演化图——每轮操作与上一轮的风险级差异"
    threshold: "连续 3 轮风险递增 → 第 4 轮起 auto_guard 起步"
    reset: "Owner 确认操作安全可手动重置演化图"

  # === 意图分析超越条件匹配 ===
  intent_analysis:
    rule: "当 Agent 提交的理由包含结构化论证时——不只判文件数/类型，还要分析意图"
    implementation: "升级引擎用独立小模型做意图分类（无害/可疑/恶意）"
    escalation: "意图=可疑 → 操作升级一级；意图=恶意 → escalated to blocked"
```

---
