---
module_id: KE-4060
title: 3.3 按触发方式分类
category: module_blueprint
ttl: permanent
---

# 3.3 按触发方式分类

3.3 按触发方式分类

| 触发方式 | 说明 | 代表脚本 |
|---------|------|---------|
| **pre-commit钩子** | git commit时自动触发 | GATE-18（全量测试收集） |
| **run_all批量** | `python scripts/governance/run_all.py` | 全维度/指定维度扫描 |
| **独立触发** | `python scripts/governance/dX_*/validate_*.py` | 单维度精确检查 |
| **CI管线** | GitHub Actions触发 | check_architecture_gates.py |
