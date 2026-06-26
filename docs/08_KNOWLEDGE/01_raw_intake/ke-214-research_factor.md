---
module_id: KE-194---factor-000
title: 2.3 Research & Factor 域（研究与因子）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.3 Research & Factor 域（研究与因子）

2.3 Research & Factor 域（研究与因子）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E08 | `Factor` | 因子定义（factor_id, name, formula_ref, frequency, asof_offset, lineage_root） | 注册即不可变（变更=新版本） | — | OLTP（registry） |
| E09 | `FactorValue` | 因子取值（factor_id, symbol, asof_date, ts_calc, value, status） | append-only；**必须含 asof_date 与 ts_calc** | 🔴 高（PIT 红线） | 列存 / 特征仓 |
| E10 | `FeatureSet` | 特征集（feature_set_id, factor_ids[], asof_date, lineage_root） | append-only；快照式 | 🔴 高 | 特征仓 / 对象存储 |
