---
module_id: KE-972
title: 6.1 脚本功能
category: governance
---

# 6.1 脚本功能

6.1 脚本功能

| 命令 | 功能 | 完整调用示例 |
|------|------|-------------|
| `--scan` | 扫描指定路径，输出残留文件分类报告 | `python src/zephyr/gates/task_completion_gate.py --scan --task-id {TASK_ID} --scope-paths "{PATH1}" "{PATH2}"` |
| `--clean` | 自动删除 ORPHAN_SHELL / STALE_SKELETON / DUPLICATE / LEGACY_TEST 类别的文件 | `python src/zephyr/gates/task_completion_gate.py --clean --task-id {TASK_ID} --scope-paths "{PATH1}"` |
| `--verify` | 验证任务产出物全部在 deliverables 内 | `python src/zephyr/gates/task_completion_gate.py --verify --task-id {TASK_ID}` |
