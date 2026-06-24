---
module_id: KE-DOCUMENTAT-R36-DATA-ARCHITECTURE-V1-003
status: active
title: 决策 R36：Data Architecture 独立成视图（v1.0.0 新建，非从 IA 迁移）
category: documentation
---

# 决策 R36：Data Architecture 独立成视图（v1.0.0 新建，非从 IA 迁移）

决策 R36：Data Architecture 独立成视图（v1.0.0 新建，非从 IA 迁移）

**决策**：在 `02_enterprise_architecture/target_architecture/` 下新建 `data_architecture.md`，作为独立的 TOGAF DA 视图，与 02-IA 平级。**v1.0.0 是全新创建，0 字内容自 02-IA 搬走。**

**关键事实澄清（任务下达时的预设 vs 实际情况）**：

任务原始指令假设"内容从 02-IA 中拆出数据架构相关部分"。实际查 `information_architecture.md` v1.1.0 全文（383 行）后发现：02-IA 全篇只讲 docs/ 21 抽屉、文档生命周期、frontmatter 元数据标准、抽屉成熟度——**完全不含任何业务数据对象（Order/Fill/Bar/Factor 等）**。也就是说，DA 此前从未存在于任何视图中，包括 02-IA。R36 因此选择"新建"而非"迁移"。

**方案对比**：

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案 A**：保持 DA 缺位，留在未来按需补 | 不新建视图 | 0 工作量 | TOGAF 8 视图覆盖度仍只有 4/8；PIT/Survivorship/血缘等量化红线无 canonical 落盘点；新成员/新 AI 找不到数据架构主入口 | ❌ 否决（被 cda60b89 会话定性为"严重缺失"） |
| **方案 B**：把 DA 内容补到 02-IA 里 | 复用现有 IA 文件 | 0 新文件 | TOGAF 标准里 DA 与 IA 是两个平级视图，混在一起会让 02-IA 同时承担"文档抽屉治理"与"业务数据治理"两套语义，违反 SRP；02-IA 已 v1.1.0 active，强行扩展会造成版本号跳变与读者混淆 | ❌ 否决 |
| **方案 C**：新建独立 `data_architecture.md` ✅ | 与 02-IA 平级、与 03-AA/04-TA 通过 §10 边界关系图严格区分 | 与 TOGAF 标准一致；PIT/Survivorship/Lineage/MDM/Quality/Retention 有 canonical 落盘点；02-IA 不动；未来新增 Security/Integration/Operations 视图时复用同一编号节奏（05-DA / 06-Sec / 07-Integ / 08-Ops） | 多一个文件需维护 | ✅ 采纳 |

**视图内容 10 章节决策依据**（呼应任务书要求与 cda60b89 会话 §5.1/§5.2 量化行业专有清单）：

| 章节 | 来源 | 核心决策点 |
|------|------|----------|
| §2 Data Entity Catalog（19 条） | cda60b89 §5 + 旧体系 L00 工作 | 粒度只到 entity + 字段族；字段级 DDL 归 09_data_platform |
| §3 三维分类（温度×节奏×来源） | 业界 Data Mesh + Lambda 架构通用做法 | 分类驱动 04-TA 选型，但 DA 不指定具体技术 |
| §4 PIT 三字段铁律 | cda60b89 §7 + SQL:2011 bitemporal | `asof_date` / `ts_ingest` / `vendor_release_ts` 三字段必填；CI fitness function 强制 |
| §5 Survivorship 反偏差查询契约 | cda60b89 §5.1 | 强制走 `build_universe(asof, include_delisted=True)`；禁止裸查 `WHERE status='active'` |
| §6 三层血缘模型（Schema/Pipeline/Instance） | OpenLineage / DataHub | DA 定接口标准，不选具体工具 |
| §7 MDM 三件套 | cda60b89 §5.1 + 旧体系 L00-M5 catalog | Security/TradingCalendar/CorporateAction，bitemporal + Steward 责任矩阵 |
| §8 Data Quality 五类断言 | Great Expectations / Soda Core 业界规范 | PIT/Survivorship/Lineage 三类业界工具不覆盖，必须自研（呼应 OQ-032 Build vs Buy 五大铁律） |
| §9 保留与归档矩阵 | 监管 7 年 + 量化历史永久 | Order/Fill 永久保留对齐合规；具体监管条款映射延后到 16_compliance_and_legal |
| §10 与其他视图边界 | TOGAF 标准 + 本项目 by-domain 双轨 | DA vs IA 用"图书馆书架 vs 资金账本"类比强化区分，防止读者混淆 |

**R 编号微调说明**：原任务指令写"R33"，但 rationale-log 里 R33 已被占用（L12 命名锁定，2026-04-19 S14 Phase 1）。本决策使用下一个可用编号 **R36**，符合"R 编号永不复用"约定。

**落盘位置**：
- `02_enterprise_architecture/target_architecture/data_architecture.md` v1.0.0（新建）
- `02_enterprise_architecture/target_architecture/README.md` v1.2.0（文档清单加入 DA 行）
- 本日志 Stage 17 + 结论 R36

**未关闭事项 / 后续衔接**：
- DA 视图引用了若干"未来视图"（06-Security / 09_data_platform 子文档），那些视图的具体内容由后续 G2/G3/G4 任务建设
- DA §6 提到的 `lineage_root` 字段需要在未来 09_data_platform 物化为 schema；本视图只定原则
- DA §8 提到的 `test_no_lookahead_bias.py` / `test_no_survivorship_bias.py` / `test_lineage_completeness.py` 三个 fitness function 待 scripts/fitness_functions/ 实施 Sprint 落盘
