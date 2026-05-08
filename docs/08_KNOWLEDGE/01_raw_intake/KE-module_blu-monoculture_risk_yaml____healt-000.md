---
module_id: KE-module_blu-monoculture_risk_yaml____healt-000
title: monoculture_risk.yaml —— health_monitor.py 产出
category: module_blueprint
---

# monoculture_risk.yaml —— health_monitor.py 产出

monoculture_risk.yaml —— health_monitor.py 产出
monoculture_top_risks:
  - shared_func: "zephyr.shared.time_utils.now_iso"
    blast_radius_score: 78             # DANGEROUS——被 12 模块引用+跨 5 层
    caller_count: 12
    cross_layer_count: 5
    layers_affected: ["L01", "L02", "L04", "L05", "L07"]
    on_critical_path: true             # Event Loop → 所有时间计算依赖此函数
    has_independent_unit_test: false   # 只有集成测试经过此函数
    recommendation: "KEEP_DUPLICATED——为该函数编写独立单元测试后再考虑去重；当前去重风险 > 收益"
    mitigating_action: "先实现 now_iso 的独立单元测试 ≥ 5 条 → BRS 降至 48 → 可去重"
```

**Monoculture 免疫的核心洞察**：不是所有重复都该消除。当 `shared_func.blast_radius_score > duplication_debt_score` 时，去重本身在创造新的、更危险的技术债——**分散的重复是天然的 blast radius 隔离机制**。
