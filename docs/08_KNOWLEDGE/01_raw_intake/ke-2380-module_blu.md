---
module_id: KE-2285
status: active
title: 5.1 14 层扩展路线（新增）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5.1 14 层扩展路线（新增）

5.1 14 层扩展路线（新增）

```yaml
layer_expansion:
  description: "随着 ZephyrAlpha 14 层架构推进，同步创建对应层的 Domain Skills"
  current_coverage: "L01 基础设施层（当前所有蓝图均在此层）"
  expansion_strategy: "来一个模块，配一个 Skill——不追求一次性到位"

  planned_domain_skills:
    L02_factor:
      modules: [factor-definition, factor-computation, factor-registry, factor-evaluation]
      trigger_per_module: true

    L04_risk:
      modules: [position-limits, stress-testing, stop-loss]
      trigger_per_module: true

    L06_execution:
      modules: [order-router, algorithmic-execution, slippage-control]
      trigger_per_module: true

    L00_foundation:
      modules: [configuration, logging, health-check]

  skill_count_projection:
    phase_1: "5 Domain Skills + 3 Role Skills = 8 Skills（scaffold-2 完成）"
    phase_2: "~20 Domain Skills（L01 全部 + L02 部分）"
    phase_3: "~50 Domain Skills（L00-L06 全覆盖）"
    final: "~80-120 Domain Skills（14 层全覆盖）+ 3 Role Skills = 约 100 Skills"
```

---
