---
module_id: KE-1026
status: active
title: 5.1 src 代码目录
category: governance
ttl: permanent
---

# 5.1 src 代码目录

5.1 src 代码目录

```
src/zephyr/
├── shared/                    # 跨层公共
├── data/           # L00
├── infra_ops/        # L01
├── factor/          # L02
├── ...
├── ml_train/    # L11（注：目录名为 strategic_decision，层名为 ML Platform）
├── infra_ops/      # L12（规划中）
└── simulation/   # L13（规划中）
```

**命名规则**：`l{xx}_{snake_case_name}/`
