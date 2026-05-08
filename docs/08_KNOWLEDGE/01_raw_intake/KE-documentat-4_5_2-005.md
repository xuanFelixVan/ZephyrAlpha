---
module_id: KE-documentat-4_5_2-005
title: 4.5.2 为什么枚举值用小写？
category: documentation
---

# 4.5.2 为什么枚举值用小写？

4.5.2 为什么枚举值用小写？

1. **Vibe Coding 语境**：本项目的 frontmatter 主要由 AI 读取、AI 写入、AI 工作。AI 做字符串比较时严格区分大小写，`Active != active`，大小写不一致是最常见的 AI 识别错误来源。统一小写消除了这个出错点。

2. **零认知负担**：枚举值全小写，不需要记"哪个首字母大写、哪个不大写"。AI 和人类都不用想。

3. **与文件命名规则一致**：项目已裁定所有文件名和文件夹名全小写（kebab-case）。枚举值也全小写，跟文件命名规则保持一致。

4. **行业参考**：OpenSSF ADR-0013 讨论了 YAML 枚举值的 4 种大小写方案（Title Case / kebab-lower / camelCase / PascalCase），最终选择 Title Case 的理由是"为人类作者优化，视觉区分键和值"。但本项目的场景不同——AI 是主要消费者，"为 AI 优化"比"为人类视觉优化"更重要。Hugo/Jekyll 等工具也采用全小写方案。

5. **pre-commit 校验**：校验脚本只需匹配一种写法，不需要同时接受 `Active` 和 `active`，简化了门禁逻辑。
