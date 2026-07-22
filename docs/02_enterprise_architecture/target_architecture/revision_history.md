---
doc_type: audit_report
title: "target_architecture/ 完整修订历史"
version: "2.2.0"
status: Active
layer: cross_layer
module_id: ARCH-005
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-17
summary: index.md §10 修订记录的完整归档。活跃修订见 index.md §10。
ttl: permanent
---

# 02_enterprise_architecture/target_architecture/ — 完整修订历史 （被恢复）

> 本文档是 `index.md` §10 修订记录的完整归档。`index.md` 仅保留最近 3 次修订条目。
>
> 当前活跃修订见 `index.md` §10。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-17 | v1.0.0：从 DW-IA-DESIGN-001 拆分升格，建立文档组 canonical 真源。OQ-012/013 已关闭，OQ-014 随本次完成关闭。 |
| 2026-04-18 | v1.1.0：采纳"双轨结构"（OQ-072 closed）。新建 `by-domain/` 容器 + 4 个子目录（docs/src/frontend/scripts-domain）+ 5 个 README 占位（status: skeleton）。01-04 视图保留原位不动；by-domain 用于未来下沉详细架构（触发条件见 `by-domain/README.md §4`）。零内容删除，纯增量。 |
| 2026-04-19 | v1.2.0：新增 `data_architecture.md` v1.0.0（G1，R36）。补齐 TOGAF Data Architecture 维度（此前 02-IA 仅治 docs/ 抽屉、不含业务数据对象，DA 视图缺位）。新增章节：19 条数据实体清单 / 三维分类 / PIT 三字段铁律 / 反 Survivorship 查询契约 / 三层血缘模型 / MDM 三件套 / 五类数据质量断言 / 保留归档矩阵 / 与 IA/AA/TA 边界关系。同步更新文档清单（§2）/ 阅读顺序（§3，新增量化研究员与数据工程师路径）/ 视图依赖图（§4，DA 与 IA 标为正交平行）。 |
| 2026-04-19 | v1.3.0：TOGAF 8 视图体系收口（S14-beta 批次 A）。新增 3 个视图：`integration_architecture.md` v1.0.0（G3，R37，active）/ `security_architecture.md` v0.1.0（G2，R38，skeleton）/ `operations_architecture.md` v0.1.0（G4，R39，skeleton）。同步更新：§2 文档清单（+3 行）/ §3 推荐阅读顺序（完整链 00→01→02→05→03→07→04→06→08）/ §4 视图依赖图（Mermaid）/ 新增 §4bis Skeleton 视图说明。R40 登记 README 收口理由。 |
| 2026-04-19 | v1.4.0（S14-beta 批次 F H11 收口）：diagrams 索引新增 5 张 seq-*.mmd 时序图（R61-F，原号 R61，批次 H 打 -F 后缀以与批次 G 同号区分）+ 3 张 c4-l3-*.mmd 组件图（R54 批次 D 补登，之前未显式登记到 README 表格）。§6 表格从 7 行扩展到 15 行。与 catalogs/ 新增 domain-event-catalog.md v1.0.0（R59-F，H6）+ ddd-aggregates.md v1.0.0（R60-F，H7）协同构成批次 F 完整交付。 |
| 2026-04-19 | v1.5.0（S14-beta 批次 H Z-FE 收口）：新增 `frontend_architecture.md` v1.0.0（TOGAF 第 10 个架构视图，前端独立平台架构，R64）。同步更新：§2 文档清单（+1 行）/ §3 推荐阅读顺序（架构师完整链扩到 10，新增 Frontend developer 路径）/ §4 视图依赖图（Mermaid 新增 FE 节点 + 4 条边：AA→FE、INTEG→FE、FE→OPS、FE→SEC）/ frontmatter related_rationale +R64 + tags +frontend-architecture。同步 `by-domain/frontend-domain/README.md` v0.1.0 skeleton → v0.2.0 draft（仅 status 升级，内容待下沉触发）。同步 `adr/` 目录：KBG-0007 / KBG-0008 从 `adr-drafts/` 追溯性升格为 accepted；KBG-0006 登记为 skipped 空号（不可复用）；僵尸草稿 DRAFT-0004/0005/0007/0008 物理删除。同步 `architecture-rationale-log.md` v1.24.0 顶部追加"R59-R61 重号事故说明"，批次 F 三个 R 号打 `-F` 后缀（R59-F/R60-F/R61-F）以区分批次 G 同号条目，本文件内 §6 5 张 seq-*.mmd 与修订记录 v1.4.0 条目同步打 -F 后缀。 |
| 2026-04-19 | v1.6.0（S14-beta 批次 I-Reopen 治理视图收口）：新增 `governance_architecture.md` v1.0.0 active（TOGAF 第 10 个架构视图最终就位，治理三层边界 Policy/Factory/Runtime，R66）。同步：§2 文档清单（+1 行，9 号视图由 deferred-closure 升 active）/ §3 架构师完整链扩到 `00→...→09→10`，新增 Governance 阅读路径，Security 路径插入 09 节点 / §4 Mermaid 新增 GOV 节点 + 6 条边（GOV 横切 BA/IA/AA/FE、GOV→SEC、OPS→GOV 审计反馈）/ §4bis 标题改写（删"缺位视图"）/ §4ter 彻底改写为"R65 → R66 append-only 决策追溯档案"（T1-T6 从"整体激活触发器"降级为"局部子系统升级触发器"，保留原 R65 理由 + 事后重新评估）/ frontmatter related_rationale +R66 + tags +governance-architecture。配套新建 `working-designs/governance-three-layer-boundary-design.md` v1.0.0 accepted（讨论稿）+ `adr/adr-0010-governance-three-layer-boundary.md` v1.0.0 accepted。OQ-026 closed（采纳 Scheme B 分阶段激活），TOGAF 视图完整度 9/10 → 10/10。 |
| 2026-04-19 | **v1.7.0（S15-experimental J1 批次 — 正交视图体系首次引入，R69 + R70 / KBG-0011 + KBG-0012 accepted / OQ-083 + OQ-084 closed）**：**TOGAF 10 视图之外第一次引入正交视图（Orthogonal View）架构方法论**，响应用户 Q1 "控制面 / 执行面物理切分是单开一层吗" 的架构拷问 + 外部评审 P1 短板 "缺少能力成熟度可视化"。**核心变动**：新增 `runtime_planes.md` v1.0.0 active（第一个正交视图，Runtime Planes Hot/Warm/Cold 三平面切分，对标 Citadel Securities / Jane Street / Two Sigma / Jump Trading / Renaissance 五家顶级机构"控制面 vs 执行面物理切分"一致做法，R69 + KBG-0011，当前 Warm Path only 阶段 + 三档激活触发器 + Sim-to-Real Gap 消除路径 + shared/contracts/runtime_plane_tag.py 契约预留）+ `capability_heatmap.md` v1.0.0 active（第二个正交视图，Capability Maturity Heatmap 14 层业务能力 × 7 核心能力域的 L0-L5 五档成熟度热力图，对标 ArchiMate 3.2 Capability Map + Gartner IT Capability Framework + Goldman Sachs EA Capability Dashboard，R70 + KBG-0012，当前基线快照 + T1/T3/T-ENDGAME 三档目标 + 季度 review 机制）。**README 变动**：(a) §1ter 新整节 "Orthogonal Views 正交视图体系"——说明正交视图方法论 + 5 条铁律（OV-P1 不污染业务分层本体 / OV-P2 命名空间隔离 bis/ter/quater / OV-P3 SSoT 单一源 / OV-P4 零业务决策变动 / OV-P5 起码对标 2 家顶级机构）+ 当前正交视图清单 + 未来扩展预留口（04quater 部署拓扑 / 04quinquies 数据生命周期 / 04sexies 故障域，需 KB 决策记录 立项）；(b) §2 文档清单新增 2 行 04bis + 04ter 登记（🔷 标记 Orthogonal）；(c) §4 Mermaid 视图依赖图新增 RTP + CHM 两个黄色高亮节点 + 9 条虚线正交标注关系（RTP -.> AA/FE/GOV/INTEG/TA，CHM -.> BA/AA/DA/GOV）+ classDef orthogonal 样式定义；(d) frontmatter related_rationale +R69 +R70 / related_open_questions +OQ-083 +OQ-084 / tags +runtime-planes +capability-heatmap +orthogonal-view。**同步变动**（J1 批次其他产出联动）：`application_architecture.md` v1.9.1 → v1.10.0（§4.0 Runtime Plane Attribution Index 索引节，SSoT 指向 04bis）；`governance_architecture.md` v1.1.0 → v1.2.0（§1.2bis 铁律澄清 Runtime 层 ≠ Runtime Plane + §4.5.1 D 家族详表新增 Runtime Plane 列）；`frontend_architecture.md` v1.0.0 → v1.1.0（§7.5 新整节前端三平面归属：React Warm 主 + WebSocket Hot-adjacent + SSR 报表 Cold + 浏览器栈天然不满足 Hot Path 硬门槛澄清）。**零 TOGAF 视图业务决策变动**——01-10 十视图的业务分层、分域、分职责全部保持原样，本批次仅新增两张正交标注叠加图 + 一整套正交视图方法论。TOGAF 视图完整度维持 10/10，正交视图数量从 0 升 2。|
| 2026-04-21 | **v1.8.0（Architecture-as-Code v2.0）**：新增 `architecture_model/` 联邦制 YAML 模型（18 分区 SSoT）+ `check_architecture_gates.py` CI 门禁脚本 + `catalogs/immutable-core-inventory.md` 不变核心清单 + `adr/KBG-0013` 治理准入铁律。§2 文档清单 +3 行。§3 AI 协作者首选路径改为读 `_index.yaml`。视图正文重组织：03-AA 1076→532 / 04-TA 1070→465 / 09-GOV 615→454。 |
| 2026-04-21 | **v1.9.0（catalogs → YAML SSoT 迁移）**：删除 `catalogs/` 目录（9 文件）和 `_toc-cards/` 目录（8 文件），所有结构化数据已迁移到 `architecture_model/` YAML 分区。17 个 YAML 分区文件移除 `catalog_file:` 残留字段。§5 标题从 "View vs Catalog" 改为 "View vs YAML SSoT"。`check_architecture_gates.py` 升级至 v2.0.0（+GATE-06/07/08 +EXTRA-03）。 |
| 2026-05-01 | **v2.0.0（架构审查 P0 修复批次）**：(a) **删除 `dependency-graph-framework.md`**（旧 12 层命名依赖图，11/14 层与实际矛盾），其唯一独有价值——依赖置信度分级（L1/L2/L3）已提取迁入 `architecture_model/layers/schema.yaml` v2.1。未来依赖图从 YAML SSoT 自动生成（对标 K8s/Terraform 声明式）。 (b) **by-domain 双轨结构调整**：`by-domain/` 目录为提前预留的架构骨架（4 个子域目录 + 占位 index.md），待后续按域填充详细架构文档。§1bis 整节切除 + §2 文档清单 5 行 by-domain 删除 + frontmatter tags/summary 同步清理（双轨说明从 README 移除，骨架保留）。v1.1.0/v1.5.0 修订记录保留为历史档案。 (c) **同步 06/08 视图状态**：`security_architecture.md` skeleton → active v1.0.0（2026-04-24 已升格，README 滞后）；`operations_architecture.md` skeleton → draft v0.2.0。§2 表格 / §3 阅读路径 / §4bis 段 / T1 触发条件联动修正。 |
| 2026-05-02 | **v2.1.0（审计修复批次）**：修复 4 项 SSoT 对齐问题：(a) `architecture_model/infra/` 创建 `core_services.yaml`、`shared_infra.yaml` 骨架，`architecture_model/index.yaml` 不再引用缺失文件；(b) `architecture_principles.md` v1.1.0 §0 新增安全红线 R1–R4，`overview.md` 改为引用链接，消除安全红线双源；(c) `ssot-authority-map.md` v2.3.0 移除 `layer_01` 历史误标、矛盾追踪拆分活跃/已解决；(d) 修订历史归档至本文，`index.md` §8 仅保留最近 3 条。 |
| 2026-05-06 | **v2.2.0（AUDIT-04 / 治理收口批次）**：双树读法与 `architecture_model/scope.yaml`、AGENTS §6.9 / `ssot-authority-map` 对齐；Python 基线统一到 ≥3.11（施工树 `technology_landscape.yaml` 与 EA 视图一致，勿混写 TECH-11）；新增 `docs/_working/audit/findings/` 与审计导航；`cross_layer_contracts.yaml` `partition` 增补 `ownership_model`；`validate_ssot.py` 修复模块 docstring、`check_audit_navigation_wiring()` 与 `--ci` 行为；`document-metadata-index` / `directory-registry` / `registry-master-index` 同步；`batch_create_index_md.py` 移除过时 `by-domain` 责任映射并补全 `09_audit/findings`；`invariants.yaml` INV-005 明确源码路径 vs EA 分层文件名；`scripts/arch_guard/manifest.yaml` 日期跟进。 |
