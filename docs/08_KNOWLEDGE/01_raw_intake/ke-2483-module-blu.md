---
module_id: KE-2388
status: active
title: 6.4 依赖版本漂移
category: module_blueprint
---

# 6.4 依赖版本漂移

6.4 依赖版本漂移

```yaml
dep_version_drift:
  description: "requirements.txt vs 实际 pip freeze"
  method: "subprocess.run(['pip', 'freeze']) → 解析 → 与 requirements.txt 行级对比"
  auto_fixable: true
  auto_fix_action: "自动更新 requirements.txt 为实际安装版本"
  caution: "自动更新需保留版本范围约束（>=, ~=）的语义，不可暴力锁定为 == 精确版本"
```
