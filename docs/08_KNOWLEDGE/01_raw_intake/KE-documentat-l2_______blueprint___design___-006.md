---
module_id: KE-documentat-l2_______blueprint___design___-006
title: L2 设计模板（`blueprint` `design` `service_spec`）
category: documentation
---

# L2 设计模板（`blueprint` `design` `service_spec`）

L2 设计模板（`blueprint` `design` `service_spec`）

> **2026-05-02 更新**：`construction_plan` 原为独立 L2 模板，现已合并入 `blueprint`。蓝图 §1-§11 承载架构决策，§12 承载施工指引。`construction_plan` doc_type 仅对历史文档保留。

对标：ISO Technical Specification / IETF BCP / IEEE Recommended Practice

| # | 章节 | 必要性 | 说明 |
|---|------|:------:|------|
| 1 | **目的与范围** | MUST | 包含 §1.2 责任范围 + §1.3 责任边界 |
| 2 | **SSoT 声明** | MUST | 声明本文档是什么的真源 |
| 3 | **受控枚举定义** | SHOULD | 如有枚举，列出清单 |
| 4 | **消费者注册表** | MUST | Tier 1/2/3 分级（设计文档的下游消费者是施工图和代码） |
| 5 | **主体内容** | MUST | 使用 SHOULD/MAY（L2 禁止使用 MUST） |
| 6 | **禁止行为** | SHOULD | 列出设计约束 |
| 7 | **变更同步规则** | MUST | 变更时同步下游施工图和代码 |
| 8 | **修改条件** | MUST | 修改审批流程 |
| 9 | **标准间引用规范** | SHOULD | normative/informative 分离 |
| 10 | **已实现代码路径索引** | MUST | 蓝图覆盖范围内所有已实现代码的完整路径表（AGENTS.md §6.14 蓝图-代码同步强制约定）。含：模块ID / 实现状态 / 源码路径 / 测试路径 / 配置路径。CI 门禁 `validate_blueprint_code_sync.py` 自动校验此表与磁盘实际一致 |
| 11 | **变更记录** | MUST | 版本历史 |

> **L2 与 L1 的关键差异**：
> - L2 禁止使用 MUST（只有 L1 治理文档才能设强制要求）
> - L2 不需要审查周期、异常豁免、AI 自治权限标注（这些是治理层专属）
> - L2 不需要完整性自检清单（设计文档有各自专用模板的 checklist）
