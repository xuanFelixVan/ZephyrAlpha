---
module_id: KE-2367
status: active
title: 6.13 混沌工程——主动漂移注入
category: module_blueprint
---

# 6.13 混沌工程——主动漂移注入

6.13 混沌工程——主动漂移注入

```yaml
chaos_drift_injection:
  description: "定期主动注入可控漂移——测试 drift detector 的检测灵敏度和修复能力。与'故障演练'同理——不测试就不知道检测器是否真的有效"

  injection_types:
    - type: "path_rename"
      description: "随机重命名一个非关键文件 → 验证 blueprint_code_sync 检测器是否发现"
    - type: "yaml_field_flip"
      description: "将某个 YAML 字段值改为合法但不正确的值 → 验证语义漂移检测器"
    - type: "fake_todo_bomb"
      description: "在非关键模块注入高密度 TODO → 验证 broken_logic 检测器"
    - type: "import_hallucination"
      description: "注入一条不存在的 import → 验证 AI 幻觉检测器"

  schedule: "每周一次自动混沌演练（在维护窗口内执行）"

  safeguards:
    - "仅对 P2 模块注入（零生产影响）"
    - "注入前自动拍 pre-chaos 基线"
    - "检测通过后自动回滚注入（恢复 pre-chaos 状态）"
    - "若检测器未发现 → 标记检测器为 DEGRADED → 通知 Owner"

  metrics:
    - "detection_rate: 混沌注入被检测到的比例"
    - "time_to_detect: 注入到被检测到的延迟"
    - "false_negative_trend: 未被检测到的注入是否在增加"
```
