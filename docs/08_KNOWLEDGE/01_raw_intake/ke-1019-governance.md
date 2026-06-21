---
module_id: KE-940
status: active
title: 5.1 流程决策树
category: governance
---

# 5.1 流程决策树

5.1 流程决策树

```
开始审计
  │
  ├─ QUICK? ──→ run_all.py --dimensions D3 D5 D6 D7 --warn-only
  │              │
  │              ├─ P0=0? ──→ PASS → 记录结果 → 结束
  │              └─ P0>0? ──→ FAIL → 进入步骤5闭环
  │
  ├─ FULL? ──→ env_check.py → run_all.py（全量177脚本）
  │            │
  │            ├─ L2通过? ──→ score_architecture.py → 生成报告 → 结束
  │            └─ L2未通过? ──→ 进入步骤5闭环 → 修复后重跑
  │
  └─ TARGETED? ──→ run_all.py --dimensions <指定> --warn-only
                   │
                   ├─ 目标维度P0=0? ──→ PASS → 记录结果 → 结束
                   └─ 目标维度P0>0? ──→ FAIL → 进入步骤5闭环
```

---
