---
module_id: KE-3510
title: 18. 变更记录
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 18. 变更记录

18. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-06 | 1.1.0 | **SSoT 操作化——§7 新增 #5 功能域重叠否决条件 + §7.1 四步判定流程**。根源：MOD-INF-003/004 与 006 功能域重叠未被拦截——MAD-001 只管层归属唯一，§7 #1 只挡 module_id 重复，缺少"功能域是否已被覆盖"这道闸门。修复：(1) §7 #5 否决条件：新模块 summary/title/tags 与现有模块 responsibility_domain/covers[] 重叠 → 否决；(2) §7.1 四步判定流程：关键词扫描→responsibility_domain匹配→covers[]交叉→输出升级建议。治根逻辑：从"事后 SSoT 冲突裁决"升格为"事前功能域重叠预防"。版本号 minor +1。 |
| 2026-05-01 | 0.6.3 | P2 格式修正：§8 JSON 键名 p1_id→p1_arch（MAD-001 架构必要性）、p2_doc→p2_phase（MAD-002 Phase 相关性）——与 MAD 规则语义对齐 |
| 2026-05-01 | 0.6.2 | 消费者通知机制交叉引用：§13 变更同步规则添加通知机制引用——消费者通知方式见 GOV-MOD-002 §10（Session Log/ADR/registry 三层体系） |
| 2026-05-01 | 0.6.1 | 交叉引用漂移修复：消费者注册表 §5→§7 否决条件映射 INJ 编号——Round 10 插入 §3/§4 后未同步的 self-ref |
| 2026-05-01 | 0.6.0 | 对齐 PS-STD-002 §3.2.4（行为规则型条件性章节）：新增 §3 受控枚举声明 + §4 消费者注册表（Tier 1/2）+ §13 变更同步规则 + §14 修改条件（L0~L3 分级）+ §15 废弃流程（通知→过渡→延期→归档）+ §16 审查周期（ISO 11179）+ §17 完整性自检清单。修正 C1（YAML 路径引用格式）、C2（硬编码层数→引用 architecture_model）、C3（MOD-P3 命名一致性）。全文章节重编号 §3→§18。 |
| 2026-05-01 | 0.5.2 | Common Core 对齐 PS-STD-002 §3.2.1：新增 §2 SSoT声明 + §9 标准间引用规范（normative/informative）+ §10 AI可消费性声明（minimum reading path + lookup_index）+ 全文章节重编号（§2~§8 → §3~§11） |
| 2026-05-01 | 0.5.1 | 深颗粒审计修复：§2 执行顺序添加 GOV-MOD-005 §context.injection_flow 交叉引用——让全新 AI session 一次读完就知道端到端注入流程的完整顺序 |
| 2026-05-01 | 0.5.0 | 元规则对齐审计：frontmatter 添加 valid_from 字段（doc_type-vocabulary.yaml 要求）+ 字段排序对齐 PS-STD-001 §2.3 + layer cross_layer→L1（PS-STD-004 §4.2）+ depends_on 移除 GOV-MOD-005/GOV-ARCH-002 同级引用对齐链深=1层死规则（PS-STD-001 §2.1） |
| 2026-05-01 | 0.4.0 | 第三轮补缺：MAD-003 补齐跨层依赖方向约束（GOV-ARCH-001）+ 紧急豁免增加 30 天上限 + 准入记录定义 JSON format |
| 2026-05-01 | 0.3.0 | 补齐 G1~G10 细颗粒审查缺漏：新增模块变更（UPDATE）准入覆盖 + 临届状态声明 + 紧急豁免路径 + 第三方模块专项检查 + §4 执行顺序说明 |
| 2026-05-01 | 0.2.0 | #24 审批修复：ABS/COND → MAD-（MAD-001~MAD-005）。补齐 `ai_autonomy: human_gated`。`date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
