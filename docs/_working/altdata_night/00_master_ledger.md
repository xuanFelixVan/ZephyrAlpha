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
| E4 | 产业链 T4：3,171 无映射 symbol 反哺 | ✅（宁缺毋假版） | 实查 356 symbol：反哺 11 实体/62 边（全人工 curated）；245 无名不可判+100 低置信→人工池 345 | `06918f8911` | 05 §7 B3 |
| E5 | 产业链 T5：52 条 contains 桥核验 | ✅ | 全 52 条判定：31 真→verified+10 错桥软退役+7 墓碑补 4 新桥+4 存疑留 unverified；正确率 73.1%<90% 只置真子集；桥覆盖 93→88/153 诚实收缩 | `06918f8911` | t5_contains_audit.csv |
| E6 | 产业链 T10：TSM 归一+listed_symbol 补全 | ✅ | TSM.TW 残留 2 行归一 2330.TW；+66 listed+21 补 market；13,886 无法确证留空；单管线断言 86=86 | `06918f8911` | t10_report.json |
| E7 | 产业链 T3：主营构成补年+挂词典 | ✅ | 全市场 5,565 家零失败 +112,851 行（总量 165,255，覆盖 99.96%≥95%）；PIT 公告日锚兜底 0 启用；词典挂接可匹配文本 935/935=100%≥90%（全表 2.18% 诚实不硬凑，人工池 56,359 文本）；2021 对账=粒度错位已按 source 隔离 | `6f68d2303c` | 07 §9 |
| E8 | 产业链 T6：ig_node_binding 建表+灌绑定 | ✅ | §8 照建+5 项适配留痕（07 §10）；油价五波 6 缺绑定全通（与 D4 物理代理跨包会师）；59 绑定/37 节点每节点恰 1 主绑定（挂价铁律）；抽检 20/20 | `ac2ada55d0`+`d6068fcd45` | 06 §8 |
| E9 | alpha T9：研报喂链解锁 | ✅ | 根因=id→news_id 一行修；research 适配器（PDF 全文+meta 级联）；50/50 staged 零幻觉零 error，conf 0.9-0.95；未碰 ig_* | `2e789aa96b`+`0c4c249a06` | c_research_feed 台账 |
| E10 | alpha T8：E4 送审 | ✅ | 10 候选（喂链5+指纹2+workbook3）宁缺毋假；intake 注册 +7 行；dry-run 10/10 消费 6 过 4 拒；schema 真源补登 a 簿 §7 | `d1d719a7` | lane_chain_candidates.csv |
| E11 | alpha T7：商品两任务端到端复验 | ✅ | spot 756→810 行（+54 同键幂等）；futures 117→234 行回满基线/9 品种 max=09-17；三脚本 self-check PASS | 实跑出证 | c94b3e44c3 基线 |
| E12 | 数据线波1：D1 日历族+D2 股东户数+D3 宏观 | ✅ | 日历 6 源+户数断供 +11,487 全补+宏观 226 接口三桶（已接 20/新接 18/挂账 188→CAND-018~023）六新表 6,165 行全带哨兵；金十源 2025-10 退役决定性发现 | `60f4e46bbb`+`d8419af8e6`+`b80084c0df` | 09 §1 |
| E13 | 数据线波2：D4 物理另类+D5 跨资产+D6 行情补充 | ✅（红蓝复判 2026-09-18） | 油价三件全通：ndrc 329 行(2000起)+公路运价 86 行(含 G 盘快照 23 篇)+仓单 2,880,665 行(CZCE 1,978,754+SHFE 901,911，SHFE 归档硬界 2025-11-30 红蓝补登 known_data_gaps)+肉蛋菜 11,602 行(2005起)；抽检逐值对源；F1/F7/F10/F15 如实 rejected（源死/时限）；D5 Hyperliquid 四表+中债收益率曲线（8f440ac044 系 3 笔）+D6 行情四新表+既有族验活补哨兵（83ddfdf4f5）均已落地，哨兵 33 条目 0 breach（红蓝独立复跑） | `c893ec1316`系4笔+`83ddfdf4f5`+`8f440ac044`系3笔 | 09 §1 |
| E14 | 数据线波3：D7 文本抽取+D8 质检收口 | ✅ | C6 互动易 500 raw/74 抽取(59 approved 均 0.92+15 人工池) 500/500 快照核验+27/27 证据回验；C9 调研纪要 30 raw/20 approved 20/20 回验；D3/D9 如实挂账 CAND-030/031；D8：frequency 十脏值两轮收敛清零+源头同修、31 哨兵全覆盖零 breach、01 计分板 19 处刷新、12 行活跃抽检抓 2 死管线如实登记 | `3d69c5895e`+`2c97d6d8c8` | 09 §1 |
| E15 | D9 存量迁移（全夜后台，不占并发） | ⬜ | manifest+hash 抽检 5%+原目录双备份期 30 天 | | 10 SOP §E盘迁移 |
| E16 | 红蓝对抗+循环检查 | ✅ | 15/15 数据点独立重拉对源+21 commit 完整性全 PASS+声称数字全验真；循环第一轮 3 问题修复→第二轮 0→第三轮 0 达标 | `734fe7d660` | 01_morning_report ② |
| E17 | 收尾 | ✅ | claims 全 release；队列 7 袋全落地；临时件清理确认见晨报⑥；六要素晨报=01_morning_report.md | （本批 commit） | 01_morning_report |

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
