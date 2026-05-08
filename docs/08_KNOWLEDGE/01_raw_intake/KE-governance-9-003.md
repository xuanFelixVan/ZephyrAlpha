---
module_id: KE-governance-9-003
title: 9. 推导链
category: governance_rule
---

# 9. 推导链

9. 推导链

```
冲突发生时，按以下链路裁决：

  stability → layer → scope → Owner
```

| 步骤 | 维度 | 规则 | 来源 |
|:----:|------|------|------|
| 1 | stability | `frozen` > `stable` > `evolving` | §6 |
| 2 | layer | `cross_layer` > `L1` > `L2` > `L3` | §4 |
| 3 | scope | `global` > `domain` > `module` | §5 |
| 4 | Owner | 三步推导后仍冲突 → **停止操作，上报 Owner**（MTH-003 目标优先裁决） | PS-STD-011 MTH-003 |

**大白话**：两条规则打架时，先看谁更"硬"（stability——冻结的比稳定的牛逼），再比谁管得宽（layer——全局规则比领域规则优先），最后看谁范围大（scope——全局 > 领域 > 模块）。如果这三步比完还分不出高低，就停手问 Owner。AI 自己不做裁判。

---
