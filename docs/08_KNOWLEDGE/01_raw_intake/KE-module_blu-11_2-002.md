---
module_id: KE-module_blu-11_2-002
title: 11.2 核心约束
category: module_blueprint
---

# 11.2 核心约束

11.2 核心约束

- **CWD 白名单**：只在 `src/zephyr/` / `scripts/` / `docs/` 下执行
- **ENV 白名单**：只继承明确列出的环境变量
- **timeout 强制**：默认60s，超时终止进程树
- **shell=True 禁止**：命令必须以 list[str] 形式传入
