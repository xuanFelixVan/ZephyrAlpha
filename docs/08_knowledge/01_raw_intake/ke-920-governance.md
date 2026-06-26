---
module_id: KE-842
title: 22. 变更记录
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 22. 变更记录

22. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 2.0.2 | 2026-05-01 | 交叉引用同步——PS-STD-002 v3.1.0 引入标准子类型，§4.1 layer 画像表中 L1/cross_layer 的章节数从"19 章"改为"6~15 章（按子类型，见 PS-STD-002 §3.2）"。版本号 patch +1。 |
| 2.0.1 | 2026-05-01 | 编辑性变更——frontmatter 字段排序对齐 PS-STD-001 §2.3（date 移至 created_by 之后，ai_autonomy 移至 verifiability 之后）。版本号 patch +1。 |
| 2.0.0 | 2026-05-01 | **合并 PS-STD-008**。原 PS-STD-008（rule-priority-hierarchy.md）的冲突裁决推导链（§1-§5）内容整合为本标准 §9-§11（推导链 + 示例 + 禁止行为）。更新 §1.3 术语（新增强推导链/终极仲裁）、§8.1 画像表（删除 PS-STD-008 行，新增 PS-STD-012 行）、§13 消费者注册表（新增 PS-STD-009 消费推导链）、§14 Normative 引用（新增 PS-STD-011 MTH-003）、§17 审查周期（新增推导链审查项）、§18 修改条件（新增推导链修改条件）、§20 可验证性（新增推导链一致性校验）。精简 title（"规则分类标准"→"规则分类与冲突裁决标准"）。原 PS-STD-008 编号释放回编号池。 |
| 1.2.0 | 2026-05-01 | Vibe Coding 社区对标补遗。新增 §2.2 Vibe Coding AI 检索策略映射——五维分类从"定义分类"到"AI 怎么用"的检索路径：五类查询意图→检索策略映射表（domain→stability→SSoT 路径）+ 四条检索原则（SSoT优先/稳定性过滤/层级收敛/领域隔离）。 |
| 1.1.0 | 2026-05-01 | B6 审查修复。(1) frontmatter 补 `date` 字段。(2) 全文 `stability: immutable` → `frozen`（13 处）。(3) 全文 `ai_editable` → `ai_modifiable`（2 处）。(4) §6.3 约束从全硬绑定改为单向。(5) PS-STD-004 自身定位从 `frozen+immutable_core` 改为 `stable+human_gated`。(6) §8 画像表清废：删除 4 个已废弃/已迁移文件。(7) PS-STD-008/009 `layer` 从 `L1` 改为 `cross_layer`。 |
| 1.0.0 | 2026-04-29 | 初始版本。定义五维分类体系（Domain/Layer/Scope/Stability/Executor），引入 `scope`、`stability` 两个新 frontmatter 字段，完成所有现有文件的规则画像。 |
