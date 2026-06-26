---
module_id: KE-602-------policy---standard---a-005
status: active
title: L1 治理模板（`policy` `standard` `ai_governance`）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# L1 治理模板（`policy` `standard` `ai_governance`）

L1 治理模板（`policy` `standard` `ai_governance`）

对标：ISO International Standard / IETF Standards Track / IEEE Standard / W3C Recommendation

> v3.1.0：下表列出 L1 模板的全部 19 章基准清单。实际必含章节取决于子类型（见 §3.2），
> 不是所有标准都需要全部 19 章。§16 和 §17 已由 frontmatter 字段替代。

| # | 章节 | 必要性 | 说明 |
|---|------|:------:|------|
| 1 | **目的与范围** | MUST | 包含 §1.2 责任范围（管什么）+ §1.3 责任边界（不管什么） |
| 2 | **SSoT 声明** | MUST | 声明本文档是什么的真源，取代了什么，与什么互补 |
| 3 | **受控枚举定义** | SHOULD | 如果本文档定义了枚举值，必须列出完整清单和代码真源 |
| 4 | **消费者注册表** | MUST | 列出所有依赖本文档的文件，分 Tier |
| 5 | **主体内容** | MUST | 规则条款，使用 MUST/SHOULD/MAY |
| 6 | **禁止行为** | MUST | 明确列出违反本规则的禁止操作 |
| 7 | **变更同步规则** | MUST | 变更类型 × 消费者 Tier 的同步要求矩阵 |
| 8 | **修改条件** | MUST | 修改本文档需要满足的条件和审批流程 |
| 9 | **标准间引用规范** | MUST | normative（必须遵守）vs informative（仅供参考）引用 |
| 10 | **废弃流程** | MUST | 取代→通知消费者→过渡期→确认无引用→删除 |
| 11 | **审查周期** | SHOULD | ISO 11179 要求定期审查标准是否仍然适用 |
| 12 | **异常豁免机制** | SHOULD | 什么时候可以违反标准？谁批准？记录在哪？ |
| 13 | **与 PS-STD-001 的字段不重复声明** | MUST | 防止两个标准都定义同一个字段导致漂移 |
| 14 | **跨标准字段交叉引用** | SHOULD | 改一个字段名时，知道哪些标准也用了这个字段 |
| 15 | **AI 可消费性声明** | MUST | 氛围编程语境下，AI 能否无歧义理解并执行本标准 |
| 16 | **AI 自治权限标注** | ~~MUST~~ → 见 frontmatter | v3.1.0 起由 frontmatter `ai_autonomy` 字段替代，禁止 body 重复 |
| 17 | **可验证性标注** | ~~MUST~~ → 见 frontmatter | v3.1.0 起由 frontmatter `verifiability` 字段替代，禁止 body 重复 |
| 18 | **完整性自检清单** | MUST | AI/人类创建标准时逐项勾选的 checklist |
| 19 | **变更记录** | MUST | 版本历史表 |
