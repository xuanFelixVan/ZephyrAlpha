---
module_id: KE-3807----slo-000
title: 11.1 稳态 SLO
category: module_blueprint
---

# 11.1 稳态 SLO

11.1 稳态 SLO

| 指标 | 目标 | 条件 |
|------|------|------|
| `validate_input()` p50 | ≤ 15 ms | 含 L1 + L2 |
| `validate_input()` p95 | ≤ 50 ms | 同上 |
| `validate_output()` p50 | ≤ 30 ms | 含 L3 + L4 + secret_scan |
| `validate_output()` p95 | ≤ 120 ms | 同上 |
| `scan_secrets(10KB)` p95 | ≤ 80 ms | detect-secrets |
| `inspect_patterns(10KB)` p95 | ≤ 40 ms | 正则库 |
| bypass 率（红队 corpus） | ≤ 5% | experimental 交付门槛 |
| secret 泄漏 | 0 件 | 生产环境 |
