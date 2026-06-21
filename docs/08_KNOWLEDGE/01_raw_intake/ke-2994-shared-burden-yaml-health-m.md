---
module_id: KE-2894----health-m-000
status: active
title: shared_burden.yaml —— health-monitor.py 产出
category: module_blueprint
---

# shared_burden.yaml —— health-monitor.py 产出

shared_burden.yaml —— health-monitor.py 产出
shared_burden:
  score: 42                        # MODERATE
  shared_import_total: 35          # 项目中有 35 个 from zephyr.shared 导入
  max_dependents_per_func: 12       # 最依赖的 shared 函数被 12 模块引用
  cross_layer_dependency_pct: 25    # 25% 的 shared 引用跨层
  top_burdened_functions:
    - "now_iso()": {dependents: 12, cross_layer: 5, risk: "MEDIUM"}
    - "get_repo_root()": {dependents: 10, cross_layer: 7, risk: "HIGH"}
  recommendation: "now_iso() 被 12 模块引用——修改前确保全量测试"
```
