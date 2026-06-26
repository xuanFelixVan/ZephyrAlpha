---
module_id: KE-1026
title: 8. 变更记录
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 8. 变更记录

8. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.2.1 | 2026-05-06 | §2：澄清 V1–V4 与 §7「V5 深度审计」关系；§2.1 `index.md` 失真阻断正式注册为 **META-V21**（PS-STD-001 §14.1）。§7.2：ADR 讨论稿处置改为 **KB:decisions**，移除对已删除 `docs/02_enterprise_architecture/adr/` 的指引。修正 §8 历史行 1.1.0 叙述（索引阻断不与 META-V17 混用）。版本号 patch +1。 |
| 1.2.0 | 2026-05-02 | **新增 V5 深度内容审计（minor）**。新增 §7：定义四步审计流程（字段扫描→内容读取→交叉验证→判定修复）、审计判定速查表（7 种常见不一致类型）、可脚本化程度评估（4 级难度）。对标 ISO 42001 §8.2。废除旧 doc_type-vocabulary.yaml v1.1.0 中"文件名不需要与 doc_type 一致"条款。旧 §6~§6 升格为 §7~§8。版本号 minor +1。 |
| 1.1.0 | 2026-05-01 | 新增 **索引一致性 / index 失真** V1 阻断项草案（后在 v1.2.1 正式编号为 **META-V21**，不得与 META-V17「废弃蓝图引用」混用）。版本号 minor +1。 |
| 1.0.1 | 2026-05-01 | 状态升格：draft → active。V1~V4 已在 PS-STD-001 §14 META-V 规则中实现，正式激活为标准。版本号 patch +1。 |
| 1.0.0 | 2026-05-01 | 初始创建——meta/ 目录系统审查后补齐。对标 OWASP ASVS v5 / Kubernetes Conformance / ISO 42001 §8 |
