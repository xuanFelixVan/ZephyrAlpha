---
module_id: KE-2003
status: active
title: 3. Four-Layer Structured Injection (§5.4 INJECT-C00)
category: module_blueprint
---

# 3. Four-Layer Structured Injection (§5.4 INJECT-C00)

3. Four-Layer Structured Injection (§5.4 INJECT-C00)

```
Layer1 (system): AGENTS.md core rules → always-on, 不受 token 预算
Layer2 (rules):  CT-* 相关合同 + blueprints → 按 task_type 注入
Layer3 (knowledge): KE + failure_patterns → priority 排序
Layer4 (examples): 类似任务成功案例 → 仅相似度 > 0.7 注入
```

Anti-Pattern AP3 直接破解——禁止 Flat string concat 注入（system/rules/knowledge/examples 混在一起）。
