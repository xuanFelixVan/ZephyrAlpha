---
module_id: KE-governance-mlc-002-000
title: MLC-002：逆向转换限制
category: governance
---

# MLC-002：逆向转换限制

MLC-002：逆向转换限制

模块阶段**禁止**以下逆向转换：

| 禁止的逆向 | 替代做法 |
|-----------|---------|
| active → in_dev | 创建新模块（新 module_id），旧模块标记 deprecated |
| testing → in_dev | **例外允许**：测试发现非破坏性 bug 可回退至 in_dev 修复，修复后重新走 testing。不改变 module_id，但须在 Session Log 记录回退原因 |
| active → testing | 创建新模块 |
| suspended → 任何在 suspended 之前的阶段 | 先恢复至 active（suspended → active 允许），再决策后续路径 |
