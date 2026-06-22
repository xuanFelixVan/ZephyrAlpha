---
module_id: KE-062
status: active
title: 02_enterprise_architecture/target_architecture/ — 完整修订历史
category: documentation
---

# 02_enterprise_architecture/target_architecture/ — 完整修订历史

02_enterprise_architecture/target_architecture/ — 完整修订历史

> 本文档是 `index.md` §8 修订记录的完整归档。`index.md` 仅保留最近 3 次修订条目。
>
> 当前活跃修订见 `index.md` §8。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-17 | v1.0.0：从 DW-IA-DESIGN-001 拆分升格，建立文档组 canonical 真源。OQ-012/013 已关闭，OQ-014 随本次完成关闭。 |
| 2026-04-18 | v1.1.0：采纳"双轨结构"（OQ-072 closed）。新建 `by-domain/` 容器 + 4 个子目录（docs/src/frontend/scripts-domain）+ 5 个 README 占位（status: skeleton）。01-04 视图保留原位不动；by-domain 用于未来下沉详细架构（触发条件见 `by-domain/README.md §4`）。零内容删除，纯增量。 |
| 2026-04-19 | v1.2.0：新增 `data_architecture.md` v1.0.0（G1，R36）。补齐 TOGAF Data Architecture 维度（此前 02-IA 仅治 docs/ 抽屉、不含业务数据对象，DA 视图缺位）。新增章节：19 条数据实体清单 / 三维分类 / PIT 三字段铁律 / 反 Survivorship 查询契约 / 三层血缘模型 / MDM 三件套 / 五类数据质量断言 / 保留归档矩阵 / 与 IA/AA/TA 边界关系。同步更新文档清单（§2）/ 阅读顺序（§3，新增量化研究员与数据工程师路径）/ 视图依赖图（§4，DA 与 IA 标为正交平行）。 |
| 2026-04-19 | v1.3.0：TOGAF 8 视图体系收口（S14-beta 批次 A）。新增 3 个视图：`integration_architecture.md` v1.0.0（G3，R37，active）/ `security_architecture.md` v0.1.0（G2，R38，skeleton）/ `operations_architecture.md` v0.1.0（G4，R39，skeleton）。同步更新：§2 文档清单（+3 行）/ §3 推荐阅读顺序（完整链 00→01→02→05→03→07→04→06→08）/ §4 视图依赖图（Mermaid）/ 新增 §4bis Skeleton 视图说明。R40 登记 README 收口理由。 |
| 2026-04-19 | v1.4.0（S14-beta 批次 F H11 收口）：diagrams 索引新增 5 张 seq-*.mmd 时序图（R61-F，原号 R61，批次 H 打 -F 后缀以与批次 G 同号区分）+ 3 张 c4-l3-*.mmd 组件图（R54 批次 D 补登，之前未显式登记到 README 表格）。§6 表格从 7 行扩展到 15 行。与 catalogs/ 新增 domain-event-catalog.md v1.0.0（R59-F，H6）+ ddd-aggregates.md v1.0.0（R60-F，H7）协同构成批次 F 完整交付。 |
| 2026-04-19 | v1.5.0（S14-beta 批次 H Z-FE 收口）：新增 `frontend_architecture.md` v1.0.0（TOGAF 第 10 个架构视图，前端独立平台架构，R64）。同步更新：§2 文档清单（+1 行）/ §3 推荐阅读顺序（架构师完整链扩到 10，新增 Frontend developer 路径）/ §4 视图依赖图（Mermaid 新增 FE 节点 + 4 条边：AA→FE、INTEG→FE、FE→OPS、FE→SEC）/ frontmatter related_rationale +R64 + tags +frontend-architecture。同步 `by-domain/frontend-domain/README.md` v0.1.0 skeleton → v0.2.0 draft（仅 status 升级，内容待下沉触发）。同步 `adr/` 目录：KBG-0007 / KBG-0008 从 `adr-drafts/` 追溯性升格为 accepted；KBG-0006 登记为 skipped 空号（不可复用）；僵尸草稿 DRAFT-0004/0005/0007/0008 物理删除。同步 `architecture-rationale-log.md` v1.24.0 顶部追加"R59-R61 重号事故说明"，批次 F 三个 R 号打 `-F` 后缀（R59-F/R60-F/R61-F）以区分批次 G 同号条目，本文件内 §6 5 张 seq-*.mmd 与修订记录 v1.4.0 条目同步打 -F 后缀。 |
| 2026-04-19 | v1.6.0（S14-beta 批次 I-Reopen 治理视图收口）：新增 `governance_architecture.md` v1.0.0 active（TOGAF 第 10 个架构视图最终就位，治理三层边界 Policy/Factory/Runtime，R66）。同步：§2 文档清单（+1 行，9 号视图由 deferred-closure 升 active）/ §3 架构师完整链扩到 `00→...→09→10`，新增 Governance 阅读路径，Security 路径插入 09 节点 / §4 Mermaid 新增 GOV 节点 + 6 条边（GOV 横切 BA/IA/AA/FE、GOV→SEC、OPS→GOV 审计反馈）/ §4bis 标题改写（删"缺位视图"）/ §4ter 彻底改写为"R65 → R66 append-only 决策追溯档案"（T1-T6 从"整体激活触发器"降级为"局部子系统升级触发器"，保留原 R65 理由 + 事后重新评估）/ frontmatter related_rationale +R66 + tags +governance-architecture。配套新建 `working-designs/governance-three-layer-boundary-design.md` v1.0.0 accepted（讨论稿）+ `adr/adr-0010-governance-three-layer-boundary.md` v1.0.0 accepted。OQ-026 closed（采纳 Scheme B 分阶段激活），TOGAF 视图完整度 9/10 → 10/10。 |
| 2026-04-19 | **v1.7.0（S15-experimental J1 批次 — 正交视图体系首
