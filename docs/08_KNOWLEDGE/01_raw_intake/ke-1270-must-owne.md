---
module_id: KE-1183---------must------owne-003
status: active
title: MTH-007：决策质量四问 [MUST — 每次向Owner提交方案时强制执行]
category: governance
---

# MTH-007：决策质量四问 [MUST — 每次向Owner提交方案时强制执行]

MTH-007：决策质量四问 [MUST — 每次向Owner提交方案时强制执行]

每次向 Owner 提交方案或建议时，**MUST** 完成以下四个维度的检查。缺少任一维度的方案 **MUST NOT** 进入 Owner 决策环节。

- **四问模板**：
  1. **埋雷检查**（Forward Cost）：这个选择会不会给未来埋雷？——如果选 A 方案，未来纠正它需要重写架构吗？需要不可逆迁移吗？有清晰的拆除路径吗？（对齐 AGENTS.md §6.3 未来成本评估）
  2. **容量检查**（Scalability）：这个选择会不会限制未来容量？——如果用 `A-` 作为前缀（2 字符），未来其他文件想用 `A-` 怎么办？容量被谁消耗的？还有多少余量？（对齐 MTH-005 1500+ 目标）
  3. **专业对标**（Professional Reference）：专业机构/Vibe Coding 社区怎么做的？——ISO 用家族号段、OWASP 用项目缩写、Kubernetes 用 API 组前缀。我们的选择在行业中有没有先例支撑？（对齐 MTH-004 对标=架构标准）
  4. **最终建议**（Recommendation with Reasoning）：基于以上三维度的综合判断给出建议——不是"我觉得 A 好"，而是"A 在埋雷维度无风险、容量维度有余量、对标维度有 IETF/OWASP 先例支撑，因此推荐 A"

- **反模式**：
  - "这个看着顺眼就选它吧"——跳过四问
  - "我觉得没问题"——跳过对标
  - "以后再说"——跳过埋雷检查
- **验证方式**：每次建议被 Owner 采纳后，未来 3 个 session 内是否因为该建议埋的雷而需要返工？如果是，四问执行不到位
- **专业参考**：ITIL → Change Impact Assessment（变更影响评估四维度：风险、范围、合规、替代方案）/ ISO 31000 → Risk Assessment（风险评估——任何决策前必须评估潜在后果）
