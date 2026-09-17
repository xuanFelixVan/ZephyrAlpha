---
ttl: task_bound
module_id: altdata_night.00_master_ledger
title: 通宵双分包战役总簿（产业链+数据线+图谱Alpha并入+D9迁移）
updated: 2026-09-18
---

# 通宵双分包战役总簿（2026-09-18 夜）

> 总统筹会话：st-nightcoord-20260918。Owner 总令：先挖骨架→挖干开工→线间并行流水→红蓝收口→六要素晨报。
> 本簿=环节全景+状态唯一账；环节细节真源=既有文档（勿重复建卷），本战役新增子文档仅限红蓝/晨报/裁定附录。

## 0. 会话册（并发 2-3 纪律）

| 会话 | 职责 | 领地 |
|---|---|---|
| st-nightcoord-20260918 | 总统筹：台账/派发/收口/晨报 | docs/_working/altdata_night/ |
| st-igchain-20260918 | 产业链子分包（T1-T6/T10） | ig_* 表（superuser 通道）、docs/_working/altdata_line/ |
| st-datapack-20260918 | 数据子分包（D1-D8） | schemas/data 实现、CH 业务表；**禁碰 ig_* 写** |
| st-igalpha2-20260918 | 图谱Alpha并入（T7/T8/T9） | scripts/industry_graph、scripts/backtest、factory intake |
| （后台）D9 迁移进程 | E/F 盘研报→G 盘冷库 | G:\zephyr_cold\30_corpus\research_reports\ |

## 1. 环节全景（挖干判据：验收数字+commit hash 落账；未达=不封矿）

| # | 环节 | 状态 | 验收判据 | commit/证据 | 细节真源 |
|---|------|------|---------|------------|---------|
| E0 | 战役基建：总簿/会话册/令牌/心跳 | ✅ 本簿 | 本簿落库 | （本 commit） | 本簿 |
| E1 | altdatamap 双提交并入 dev | ✅ | merge commit 含 5 文件+SOP v1.1.0 | `55a8b7a9ab` | 晨间注配方已执行 |
| E2 | 产业链 T1：R1 精确化（官方对照表→补桥） | ✅ | 63 部门/104 行 official_map；抽 30 正确率 96.7%→103 行 verified=true；1 存疑软退役；58 部门 pending 人工池（图谱节点缺位不硬凑）；官方对照表无电子版已留证 | `71224c42a3` | 07 §1 R1 |
| E3 | 产业链 T2：R5 IO 2020 回填 flow_wan/coefficient | ✅（核验制） | 实证 io_edge 自建表起 100% 非空（审计误报已更正 07 §7）；独立官方转存件五重核验偏差 5.6e-16；零纠偏；staging io_2020_* 四表留档 | `71224c42a3` | 07 §1 R5 |
| E4 | 产业链 T4：3,171 无映射 symbol 反哺 ig_node_company | ⬜ | 反哺行数+抽检；宁缺毋假 | | 05 §7 B3 |
| E5 | 产业链 T5：52 条 contains 桥抽 30 人工核验 | ⬜ | 30 条核验记录+错误率 ≤10% | | 07 §6 R1 预演 |
| E6 | 产业链 T10：TSM placement 归一+14,070 listed_symbol（与 WP-0 单管线） | ⬜ | ig_entity_code_map 单管线写入；2330.TW 归一 | | 06 §8+st-igalpha 交接 |
| E7 | 产业链 T3：主营构成 2022-2025+product_def 词典挂 node_ref | ⬜ | node_ref 填充 ≥90% | | 07 §1 R3 |
| E8 | 产业链 T6：ig_node_binding 建表+灌绑定 | ⬜ | DDL+绑定行数+抽检 | | 06 §8 |
| E9 | alpha T9：研报喂链解锁 | ✅ | 根因=id→news_id 一行修；research 适配器（PDF 全文+meta 级联）；50/50 staged 零幻觉零 error，conf 0.9-0.95；未碰 ig_* | `2e789aa96b`+`0c4c249a06` | c_research_feed 台账 |
| E10 | alpha T8：E4 送审（lane_chain_candidates.csv+intake 注册） | ⬜ | 消费点注册+csv schema 合规 | | a_mining_workbook §7 |
| E11 | alpha T7：商品两任务端到端复验 | ✅ | spot 756→810 行（+54 同键幂等）；futures 117→234 行回满基线/9 品种 max=09-17；三脚本 self-check PASS | 实跑出证 | c94b3e44c3 基线 |
| E12 | 数据线波1：D1 日历族+D2 股东户数+D3 宏观第一梯队 | ⬜ | 每区：增量任务+哨兵+抽检 20 条 | | 09 §1 |
| E13 | 数据线波2：D4 物理另类（油价三件）+D5 跨资产（Hyperliquid 先点火）+D6 行情 | ⬜ | 同上；Hyperliquid 首日快照自积启动 | | 09 §1 |
| E14 | 数据线波3：D7 文本抽取+D8 质检收口 | ⬜ | 抽取置信度门+计分板刷新 | | 09 §1 |
| E15 | D9 存量迁移（全夜后台，不占并发） | ⬜ | manifest+hash 抽检 5%+原目录双备份期 30 天 | | 10 SOP §E盘迁移 |
| E16 | 红蓝对抗+循环检查两轮归零 | ⬜ | 连续两轮 0 问题+红蓝修复记录 | | 总令第五条 |
| E17 | 收尾：release claims/临时清理/骨架回写/晨报 | ⬜ | 六要素晨报落本目录 | | 总令第六/七条 |

## 2. 环节→既有文档映射（子文档不重建，指路）

- 产业链修复令（E2-E5/E7）：`docs/_working/altdata_line/07_industry_chain_repair_workorder.md`
- 产业链施工包 WP-0/WP-1（E4/E6/E7）：`docs/_working/altdata_line/05_industry_chain_assets_plan.md`
- 传导链引擎+ig_node_binding DDL（E8）：`docs/_working/altdata_line/06_transmission_chain_engine.md`
- 九环节路线图：`docs/_working/altdata_line/08_full_chain_roadmap.md`
- 数据线七区清单（E12-E14）：`docs/_working/altdata_line/09_data_subpackage_worklist.md`
- G 盘冷库 SOP+上架 SOP §12/§13（E12-E15 通用）：`10_g_drive_cold_storage_sop.md`、`docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md`
- 图谱Alpha四本作业簿（E9-E11）：`docs/_working/industry_chain_alpha/`

## 3. 战役级裁定记录（总令第四条：留分析过程与依据）

| # | 事项 | 裁定 | 依据链 |
|---|------|------|--------|
| Z1 | altdatamap merge 被主区 77+ staged WIP 拦截 | 临时 worktree 三步法（temp merge→ff-only→stash pop），代替晨间注的直 merge 配方 | 第一性：merge 只动 5 文件，主区 index 脏是外生噪声；机构实践：临时 worktree 隔离合并是 git 常规手法；实测直 merge 两次被 ort 拒 |
| Z2 | 主区 03:54 死会话半截 merge（st-regcal→dev，ruling_registry 已解未 commit） | merge --abort 清态；已解决版备份 .runtime/tmp/nightcoord_20260918/merge_prep/；登记遗留不代修（会话已死，内容在其分支 a2ab567992 无损） | 并发红线"别人的在途文件不碰、不代修"+WIP 判读铁律 |
| Z3 | 战役目录命名 | altdata_night（无数字后缀） | R5-DIGIT-SUFFIX 门禁实证（tdchain 死信 q-0001） |
| Z4 | depgraph 快照过期 28h | 波1 发射前 generate_project_depgraph.py 刷新 | DEPGRAPH-FRESHNESS 死信实证 |

## 4. 遗留与移交（滚动更新）

- [ ] st-orchp3/strategy-pipeline 半截 merge 已由 tdchain 线自行收口（2fa92002c3），总统筹 abort 备而未用，stash 备份 stash@{0}/{1} 留至收尾清理。
- [ ] st-orchp3 半截 merge 遗留（Z5，同 Z2 模式，04:03 起晾置 27min 无进展）：已 abort 清态；内容在其分支 51437bb1 无损，归 orchp3/tdchain 线收口。
- [ ] st-regcal 半截 merge 遗留（Z2）：归 st-tdchain/regcal 线收口，备份在案。
- [ ] capability_canonical_file_registry.yaml 常态带他会话 WIP token（st-overseas 等），本战役提交该文件时外来 hunks 随批（暂存区传送带既定容忍模式，own-scope 审计留痕）。
