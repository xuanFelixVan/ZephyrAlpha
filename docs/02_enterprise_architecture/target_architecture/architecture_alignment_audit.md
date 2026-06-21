---
module_id: ARCH-003
title: 知识库抽屉索引
doc_type: index
status: Active
version: "1.0.0"
date: "2026-05-02"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
ttl: permanent
summary: "08_knowledge/ 知识库抽屉的索引入口。目前处于 planned（已规划）状态——骨架已建立，内容在 M2 Vector Memory Service 建成后逐步填充。"
depends_on:
  - {target: DOCS-INDEX, at: "§子目录", why: "根目录索引——08抽屉为根 docs/ 子目录，引用其抽屉一览"}
  - {target: KBG-0005, at: "§裁定", why: "KMS 架构裁决——知识库抽屉依赖 KBG-0005 的技术选型与架构方向"}
---

# 08 Knowledge — 知识库抽屉索引

## 责任声明（Single Responsibility）

本目录只存放：**项目经验教训（KE）、最佳实践、因子/策略知识库——跨时间沉淀的知识资产**。

> **当前状态**：`planned`（骨架已建立，内容待 M2 KMS 建成后填充）
>
> **对标**：TOGAF Knowledge Management 能力域 | ITIL KM → 知识资产生命周期管理

---

## 激活条件

根据 `information_architecture.md` 的定义，本抽屉在有**跨项目可复用知识**时正式激活。M2 Vector Memory Service（KBG-0016）建成后，KE 条目将通过 AI 驱动的采集管线自动入库。

---

## 计划子目录结构

完整 KMS 10 层子目录体系（详见 KBG-0005 §实施路径）：

| 子目录 | 职责 | 状态 |
|--------|------|:--:|
| `_standards/` | KMS 条目 schema 规范 | planned |
| `01_raw_intake/` | 原始摄入区（6 子类） | planned |
| `02_triaged/` | 初审分类区（3 子类） | planned |
| `03_analyzed/` | 深度分析区 | planned |
| `04_future_capabilities/` | 未来能力蓝图（P3） | planned |
| `05_active_research/` | 活跃研究区 | planned |
| `06_lessons_learned/` | 经验教训区 | planned |
| `07_best_practices/` | 最佳实践区 | planned |
| `08_glossary_and_taxonomy/` | 术语与分类法区 | planned |
| `indexes/` | 索引与路由 | planned |

---

## KE 条目格式

KE（Knowledge Entry，知识条目）命名规则：`ke-{NNN}-{kebab-case-title}.md`（全小写），对应 module_id 格式 `KE-NNN`。

详见 `trae_028_doc_structure_naming.yaml` §2.5。

---

## 排除规则（不应放入本目录的内容）

- ❌ 治理规范/标准/协议 → `01_policies_and_standards/`
- ❌ 架构决策记录 → KB decisions namespace（SQLite knowledge 表，参见 registry-master-index.yaml MOD-HIST-001）
- ❌ 模块蓝图/施工图 → `03_modules/`
- ❌ 审计报告 → `09_audit/`

## 父级目录

- 父级：[docs 根目录](file:///D:/ZephyrAlpha/docs/index.md)
