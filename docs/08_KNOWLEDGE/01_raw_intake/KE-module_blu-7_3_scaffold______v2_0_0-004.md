---
module_id: KE-module_blu-7_3_scaffold______v2_0_0-004
title: 7.3 scaffold 验收标准（v2.0.0 更新）
category: module_blueprint
---

# 7.3 scaffold 验收标准（v2.0.0 更新）

7.3 scaffold 验收标准（v2.0.0 更新）

| 维度 | 标准 | 测量方式 |
|------|------|---------|
| 代码 | mypy 100%（新增）| `mypy scripts/governance/` |
| 代码 | ruff 错误 = 0 | `ruff check scripts/` |
| 架构 | CTR-001 重复字段 = 0 | `validate_ssot.py` |
| 架构 | 双源码树 = 0 | `ls src/zephyr/` |
| AI | capacity_slo.yaml ≥ 8 SLI（含 Saturation） | YAML 字段数 |
| AI | error_budget_tracker.py 五级响应可运行 | 单元测试 |
| AI | kill_switch.py 全局熔断可触发 | 集成测试 |
