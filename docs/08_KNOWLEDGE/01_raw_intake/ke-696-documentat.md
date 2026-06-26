---
module_id: KE-624
status: active
title: 八、活跃 SSoT 矛盾追踪清单
category: documentation
ttl: permanent
---

# 八、活跃 SSoT 矛盾追踪清单

八、活跃 SSoT 矛盾追踪清单

> ⚠️ **scope 声明**：本节是【临时审计追踪】——记录尚未解决的矛盾，便于日常施工时快速查找。本文件的 canonical 职责是"定义受保护字段的权威来源与合法值"，矛盾追踪是附加功能。**未来计划提取至独立 `ssot-contradiction-tracker.yaml`，本节届时仅保留引用链接。** 矛盾解决后应移入 §八（附）已解决归档，不应长期驻留活跃清单。
>
> 🔴 **SRP 违规标记（R5 审计 2026-05-03）**：本节违反单一职责原则——权威定义与运营追踪混合在同一文件。当前保留是因为拆分需要新建文件 + 更新 5+ 个索引（§6.11 索引-实际同步），成本高于收益。当活跃矛盾数 > 10 或本文件总行数 > 300 时，应强制执行拆分。

> 仅列出**未解决**的矛盾。已解决的条目见 §八（附）"已解决的矛盾（历史归档）"。
> 来源：`ssot-contradiction-fix-workorder.md`（已融入本文件后删除）

| ID | 矛盾描述 | 权威来源 | 修复方案 | 状态 | 执行阶段 | 负责人 |
|:---|:---|:---|:---|:---:|:---|:---:|
| SSoT-001 | 层编号双轨制（旧体系 T.XX.XXXX vs 当前项目 L00-L13） | 当前项目 L00-L13 编号系统 | beta 统一迁移，旧体系编号标记 deprecated alias | ⏳ | beta | Owner |
| SSoT-002 | 模块数量不一致（MODULE_INVENTORY vs 候选池清单） | module_id_registry.yaml | experimental 填充时统一注册 | ⏳ | experimental | Owner |
| SSoT-004 | pre-commit hooks 冗余（12→5） | 简化后 5 个核心 hooks | P0C5 执行简化 | 🔧 | scaffold | AI |
| SSoT-006 | 依赖关系未声明 | _schema.yaml depends_on | experimental 填充时声明 | 🔧 | experimental | AI |
| SSoT-007 | OSS 候选信息分散 | _schema.yaml oss_candidate | experimental 填充时关联 | 🔧 | experimental | AI |
