---
module_id: KE-1583
status: active
title: 18.2 渐进式门禁激活
category: module_blueprint
---

# 18.2 渐进式门禁激活

18.2 渐进式门禁激活

对标LaunchDarkly percentage rollout：

```yaml
gradual_activation:
  targeting_rules:
    - {rule: "仅P0任务", percent: 100}
    - {rule: "仅src/zephyr/gates/目录修改", percent: 100}
    - {rule: "全部模块，5%任务采样→25%→50%→100%", percent: [5,25,50,100]}
  auto_rollback:
    condition: "新门禁P0阻断率 > 历史基线×3"
    action: "自动回退shadow+通知Owner"
```
