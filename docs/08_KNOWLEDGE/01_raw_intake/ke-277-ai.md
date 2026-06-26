---
module_id: KE-255
status: active
title: 3.15 AI 过度依赖与状态验证
category: documentation
ttl: permanent
---

# 3.15 AI 过度依赖与状态验证

3.15 AI 过度依赖与状态验证

> **对标**：OWASP LLM Top 10 #9（Overreliance——过度依赖 AI）、Vibe Coding 社区"Read before Write"原则。

| # | 禁止行为 | 原因 | 替代方案 | 来源 |
|---|---------|------|---------|------|
| ABS-51 | AI 将自身分析结果作为唯一不可逆交易决策依据 | OWASP LLM #9：过度依赖 AI——AI 的市场分析是"无产能上限建议"（Recommendation without Capacity Ceiling），账户实际能承受的风险和流动性约束由 Owner 判定。AI 建议止损/调仓/加仓时如果不经 Owner 确认直接执行，后果不可逆 | AI 可产出分析结果和建议，但最终执行需 Owner 确认（confirm-action gate），且建议必须附带置信区间和回测数据 | OWASP LLM #9 Overreliance / MiFID II → suitability assessment（适合性评估由人完成，AI 的建议≠授权） |
| ABS-52 | AI 在未读取文件当前版本的情况下修改该文件 | Vibe Coding 环境下的"记忆"是幻觉——上一 session 读到内容不等于当前文件状态。基于过期内容做修改 = 覆盖其他 session 的变更 = 数据丢失不可逆。Vibe Coding 社区将此列为第一安全准则 | 修改任意文件前必须重新读取文件全文（含 frontmatter），验证当前内容与预期基线一致后再操作。标题+module_id+版本号匹配失败时阻断 | Cursor Rules → "always read before write" / Windsurf → "confirm current file state before edits" / Anthropic Claude Code → "re-read, don't assume" |

***
