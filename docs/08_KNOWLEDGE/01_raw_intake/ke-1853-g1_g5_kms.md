---
module_id: KE-1762
status: active
title: 2.2 G1-G5 KMS 决策门（知识生命周期判定）
category: module_blueprint
---

# 2.2 G1-G5 KMS 决策门（知识生命周期判定）

2.2 G1-G5 KMS 决策门（知识生命周期判定）

```
G1 Ingest Gate — 入库门禁
  • 判定：这个内容是否值得进入知识库？
  • 检查：来源可追溯？内容可验证？格式合规？
  • FAIL → 拒绝入库

G2 Triage Gate — 分拣门禁
  • 判定：这个KE应该归档/激活/丢弃？
  • 检查：重复性、时效性、关联性
  • FAIL → 分流到 ARCHIVE 或废弃

G3 Evaluate Gate — 评估门禁
  • 判定：这个KE的质量是否达标？
  • 检查：四模型审计流水线通过？
  • FAIL → 退回修改

G4 Activate Gate — 激活门禁
  • 判定：这个KE是否可以注入Agent上下文？
  • 检查：人工确认 + 新鲜度 + 冲突裁决
  • FAIL → 保持 ANALYZED 状态

G5 Extract Gate — 提取门禁
  • 判定：是否可以从历史KE中提取模式？
  • 检查：≥3 个同类KE存在？模式置信度？
  • FAIL → 等待更多同类KE积累
```

---
