---
module_id: KE-656
status: active
title: 三层模板对照表
category: documentation
---

# 三层模板对照表

三层模板对照表

> v3.1.0 L1 列已适配标准子类型。MUST 仅表示 Common Core（6 章对所有子类型必含），
> ▲ 表示条件性（取决于子类型，见 §3.2.4 推导表）。
> v3.2.0：`adr` 从 L2 重分类至 L3，适用 L3 章节约束。

| 章节 | L1 治理 | L2 设计 | L3 基础 |
|------|:------:|:------:|:------:|
| 目的与范围（含责任范围+责任边界） | MUST | MUST | MUST |
| SSoT 声明 | MUST | MUST | — |
| 受控枚举定义 | ▲ 条件 | SHOULD | — |
| 消费者注册表 | ▲ 条件 | MUST | — |
| 主体内容 | MUST (MUST/SHOULD/MAY) | MUST (SHOULD/MAY) | MUST (信息性) |
| 禁止行为 | ▲ 条件 | SHOULD | — |
| 变更同步规则 | ▲ 条件 | MUST | — |
| 修改条件 | ▲ 条件 | MUST | — |
| 标准间引用规范 | MUST | SHOULD | — |
| 废弃流程 | ▲ 条件 | — | — |
| 审查周期 | SHOULD | — | — |
| 异常豁免机制 | ▲ 条件 | — | — |
| 字段不重复声明 | ▲ 条件 | — | — |
| 跨标准交叉引用 | ▲ 条件 | — | — |
| AI 可消费性声明 | MUST | — | — |
| AI 自治权限标注 | 见 frontmatter | — | MUST |
| 可验证性标注 | 见 frontmatter | — | — |
| 完整性自检清单 | ▲ 条件 | — | — |
| 变更记录 | MUST | MUST | SHOULD |
| TTL 与生命周期 | — | — | MUST |
