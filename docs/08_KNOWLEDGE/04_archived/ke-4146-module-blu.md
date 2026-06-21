---
module_id: KE-3991
title: 2.1 大厂与工业界
category: module_blueprint
---

# 2.1 大厂与工业界

2.1 大厂与工业界

| 机构 | 工具 | 方法 | 我们能学什么 |
|------|------|------|------------|
| Google | Kythe + Tricorder | 全局符号索引 + AST 结构匹配 + 跨仓库追踪 | **先建图、再查重**——符号级图谱是基础。Kythe 能回答"`now_iso` 被谁定义/引用/调用链是什么"，`function_cache.json` 只能回答"哪些函数签名相似"。全局图谱建一次，后续 import 整理、循环依赖检测、影响分析都可复用 |
| Meta | Glean + Pyre | **增量式、按需**代码索引 + 类型推断辅助匹配 | **函数粒度增量**而非文件粒度——一个文件 10 个函数只改 1 个，只重新索引这 1 个。类型签名是强力指纹，`(int, str) -> bool` 比函数名更可靠 |
| SonarQube | 内置重复检测 | Token 序列归一化 + Karp-Rabin 哈希 + **可配置最小克隆长度（token 数）** | 工业级可靠性——快、稳、可集成 CI。**最小克隆长度**是关键参数：4行 import 在 20 文件中重复是严重问题，4 行函数体可能不值得提取——用 token 数而非行数判定 |
| PMD CPD | Copy-Paste Detector | Token 序列匹配 + 跨语言支持 | 零依赖、开源、CLI 友好 |
| JetBrains | IntelliJ 重复检测 | AST 子树哈希 + 滑动窗口 | IDE 内实时反馈——开发时阻止而非提交时拦截 |
| CodeAnt AI | AI 驱动检测 | **跨服务/跨语言逻辑级重复** + PR 评论 | 不只匹配文本，识别"看起来不同但行为相同" |
