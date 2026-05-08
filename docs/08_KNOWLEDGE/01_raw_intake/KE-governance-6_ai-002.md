---
module_id: KE-governance-6_ai-002
title: §6 AI 使用方式
category: governance
---

# §6 AI 使用方式

§6 AI 使用方式

AI session 在准备"写 Python 代码"时，按以下路径加载本标准：

1. AGENTS.md → 读到 §6.15 的引用 → 定位到本文件
2. 加载本文件全部章节
3. 根据当前任务所在层级（L00-L15），确定适用的类型注解强制级别（§3）
4. 代码写完后，pre-commit 阶段的 `ruff + mypy` 自动执行对应层级的检查

---
