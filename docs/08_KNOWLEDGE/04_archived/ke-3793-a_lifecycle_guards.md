---
module_id: KE-3642---lifecycle-guards-002
title: 十、附录 A：与 Lifecycle Guards 的边界
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 十、附录 A：与 Lifecycle Guards 的边界

十、附录 A：与 Lifecycle Guards 的边界

| 守卫 | 触发点 | 归属标准 | 与 5 级 Gate 关系 |
|------|-------|---------|------------------|
| **Write Guard** | ATM 原子写入时 | atomic-write-standard.md | 属基础设施层；G1 之前 |
| **Commit Guard** | git commit pre-commit hooks | `.pre-commit-config.yaml` | G1-G5 之外的版本控制层 |
| **Phase Guard** | Phase 切换 | phase-verification-procedure.md | 聚合 G1-G5 指标作输入 |
| **Contract Guard** | Pydantic v2 校验（KBG-0040）| `src/zephyr/schemas.py` | G4 调用底层实现 |
| **Runtime Guard** | 运行时观测 | runtime-observability-standard.md | 不触发 5 级 Gate |

---
