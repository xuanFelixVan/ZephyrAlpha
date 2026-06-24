---
module_id: KE-3780
title: 1.5 目标
category: module_blueprint
---

# 1.5 目标

1.5 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 建立统一脚本入口——一键运行所有审计检查 | `python scripts/governance/run_all.py` 可执行 |
| 2 | 统一输出格式——所有扫描器输出标准 Finding Schema | 全部脚本输出符合 Finding Schema 的 JSONL（以 script-manifest.yaml 为准） |
| 3 | pre-commit 门禁自动化——git commit 时自动阻断 V1 违规 | `.pre-commit-config.yaml` 中核心钩子有效运行 |
| 4 | 覆盖全部 12 维度 | 12/12 维度有可运行的扫描器 |
| 5 | 与任务系统闭合——Finding自动创建任务卡 | CRITICAL/HIGH Finding → 自动创建 BLOCKED 任务 |
