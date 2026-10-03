---
ttl: task_bound
completes_when: 总筹逐条消费（裁定/转呈/驳回）后本件退役
title: 图12 F1·需裁定与共享面发现呈批件
owner: st-vm12f1-20261003
session: st-vm12f1-20261003
date: "2026-10-03"
discipline: 勿自行处置——本会话只出料不终裁，共享面(config/**、注册册、图YAML)只读
---

# F1Z 呈批件：需裁定或需改共享面的发现（10 条）

- id: E-1
  title: DSC-12 缺"真源=契约非模块"注记
  finding: DSC-12 module_id=null 合法（真源=data_retention_contract.yaml，WB12-17/裁定#383 storage_tiering 纸面退役），但节点面无 red_reason/invalidation 说明为何无模块号——裁定二规2 要求"无实现代码⇒module_id null 且 red_reason 必填"。
  suggest: 总包/生成器给 DSC-12 补 red_reason 注记（图 YAML 是共享面，本会话未动）。
  anchors: config/data_supply_chain_map.yaml DSC-12 节点；docs/_working/map_build/fig12_datachain/90_writeback_inventory.md WB12-17；docs/_working/map_build/03_final_blueprint_and_schema.md §2 规2。

- id: E-2
  title: DSC-HA/DSC-HC（+database_service 落点）module_id 补挂建议
  finding: DSC-HA 建议挂 MOD-L00-004（ch_reader=出图的手）、DSC-HC 建议挂 MOD-INF-043（恢复演练件所有权实查在册）；handoff 格挂模块缺先例。database_service.py 建议挂 DSC-04+全节点一岗多流程注记。
  suggest: 总筹裁；裁后随生成器刷新落图（非手改）。
  anchors: 表A §1.2/§2.1；docs/03_modules/path_ownership_map.yaml ownership（scripts/ch/_recovery_drill.py→MOD-INF-043）。

- id: E-3
  title: 源SLA监测环死亡（机制零消费+台账停更 38 天）
  finding: source_sla_tracker.py（MOD-DATA-066）全仓零外部调用方（grep 实测 2026-10-03）；data/sla/ 最新件 SLA-20260826-180754.json，停更 38 天。内收四判据"零触发零消费→退役"候选；但 DSC-SRC decision_question 明确要"源侧停供定性"能力——退役或复活属 Owner 门位。
  suggest: 呈 Owner 二选一：复活接线（挂 DSC-SRC+进 schedule）或退役销册（册随裁定归档）。
  anchors: src/zephyr/data/source_sla_tracker.py；data/sla/（16 件）；宪法 §4 内收判据。

- id: E-4
  title: tasks.yaml cohort_ledger_daily 任务 id 重复
  finding: machine 层机生自证 tasks_total=271/unique=270/duplicate=[cohort_ledger_daily]（config/data_supply_chain_map.yaml machine.tasks_yaml）。共享配置面 src/zephyr/data/config/tasks.yaml 有重复登记。
  suggest: 数据班/域内会话修 tasks.yaml（本会话硬边界只读未动）；修后生成器重跑自然消账。
  anchors: machine.tasks_yaml.duplicate_task_ids（机生，禁手改即真）。

- id: E-5
  title: DDL-as-Code 族约 27 台无图12 归属格
  finding: scripts/ch/apply_*_ddl.py 族（script-manifest domain=ch 52 台中约 27 台）+verify_schema_truth.py 表结构演进面在图12 无节点——五段链无"表结构生命周期"格。
  suggest: 总筹二选一：新设一格（过停止判据三问）或判 out_of_domain（架构面→depgraph/图16 域）并写 boundary。
  anchors: scripts/script-manifest.yaml domain=ch；表A §2.4。

- id: E-6
  title: data/failures/ 案卷库升册号建议
  finding: 对账案卷库 15,134 件、今日仍产、机械命名约定齐备，但纯路径身份无册号（SOP §3 机规1 要求登记身份；fig11 f4 方案 §3 已有同款"身份缺口呈批"先例）。
  suggest: 上户口批统一授 CASEBOOK-* 册号或入 ROOR 登记（与 fig11 四本同批办，勿单开第二通道）。
  anchors: 表B §1.1；docs/_working/commitmap_cure/f4_casebook_mount_plan.md §3。

- id: E-7
  title: DSC-19 审计腿应建未建
  finding: corrupted_parts_audit.jsonl 不存在（本会话 ls+cons12 §2 双证）；机制零触发自 07-16 故从未产出病历——"检测器活着但病历本没建过"。
  suggest: 总筹裁：接受零触发无档（残废可容）或给 scheduler 探测器补"首触发即建档"逻辑（代码面改动归域内会话）。
  anchors: src/zephyr/data/scheduler.py:1067（cons12 锚）；表B §1.2。

- id: E-8
  title: 数据域断供事故台账不存在
  finding: SectorSnapshot 09-15 案（95,124 行修复）只有会话级处置、kline_sector_intraday 09-11 案只有 task_bound 散页、consensus 停 10 日案只在 11 卷——三断供案皆"病例有页无本"，违 §3 机规2 精神（病历价值在翻阅）。
  suggest: 总筹三选一：新设断供台账册/约定断供案必落 data/failures 案卷（配命名段）/判个案散页够用（写明边界）。
  anchors: 表B §1.2；docs/_working/archive/2026-09/2026-09-15-kline1min-valuation-coverage-investigation.md。

- id: E-9
  title: gap 格四字段可用性口径待入法
  finding: 15 个 gap 节点 module_id 禁挂（裁定二）但 casebooks/consumers/trigger_facts/purpose_tag 四字段正该挂（在等消费方/缺口病历挂在缺口格）；生成器 schema 0.2 无四字段，SOP v1.0.0 新增四字段未写 gap 格细则。
  suggest: 生成器 schema 升 0.3 时补"gap 格四字段挂载合法+module_id 保持 null"判据；与记忆在案的 SOP v1.1.0 节拍归一补丁同窗办。
  anchors: 表A §1.1；vertical_map_mounting_policy.md §4；03_final_blueprint_and_schema.md §2。

- id: E-10
  title: 枚举源面漂移三处（呈报不改）
  finding: ①docs/03_modules/_domain_data/index.md 陈旧（61 任务旧数/仅 3 个 module_id，实际 15 子目录+machine 投影 271 任务）；②_domain_data_security 实为 4 目录/3 个 MOD-DATSEC 号（任务书口径"5 模块"）；③scripts/ch/rebuild_news_data.py 引用的 design_memos/67 备忘目录未定位到（docs/_working/design_memos/ 与 docs/design_memos/ 均不存在）。
  suggest: 各归 Owner 责任制——索引册漂移归域内会话，备忘路径漂移归原施工会话；本会话仅登记。
  anchors: docs/03_modules/_domain_data/index.md:38；ls 实测记录在表A 自审/表B 自审。

## 附：不构成呈批的顺带事实（已入表，无需裁）

- data_asset_registry.yaml datasets declared=293 vs actual=294（drift 1，machine 机生自证）——注册册日常漂移，归数据班例行。
- realtime_snapshot 盘中零行供数形态疑点——11 卷 §4-N4 已在案复裁通道，本会话不重复呈。
