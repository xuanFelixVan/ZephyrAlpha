---
module_id: KE-248
title: 3.1 Process inventory / 进程清单（单进程）
category: documentation
---

# 3.1 Process inventory / 进程清单（单进程）

3.1 Process inventory / 进程清单（单进程）

| 进程 | 运行环境 | 职责 | 启动方式 |
|------|---------|------|---------|
| **ZephyrAlpha Main Process** | Windows / Linux (Python) | 运行 L00-L13 全链路主业务逻辑 | `python -m src.zephyr.main` |
| **Pre-commit Guard** | Git hook（本地） | 文件治理检查（编码 / frontmatter / 命名） | `git commit` 触发 |
| **CI Audit Process** | GitHub Actions / CI | 全仓库审计扫描 | push / PR 触发 |
