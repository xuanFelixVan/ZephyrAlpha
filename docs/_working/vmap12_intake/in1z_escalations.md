---
ttl: task_bound
completes_when: 总筹逐条消费（裁定/转呈/驳回）后本件退役
title: 图12 步7内收对审·需裁定与Owner门位呈批件（8条）
owner: st-vm12in1-20261004
session: st-vm12in1-20261004
date: "2026-10-04"
discipline: 本会话只出料不终裁——共享面（config/**、注册册、图YAML、代码、tests）零改动；退役/合并类归 Owner 门位（宪法§5.2）
---

# IN1Z 呈批件（8 条）

- id: IN1-E1
  title: 标签层显影——fresh_check 与 ledger_readable 双标签零钉
  finding: 9 标签中 7 个有钉（lineage 5/no_double_write 3/source_fallback 2/schedule_complete 5/can_rollback 6/break_detect 4/break_repair 3=28 格全覆盖），**fresh_check（数据还新鲜吗）与 ledger_readable（账本要能翻）在 purpose_tag 层零钉**——语义分别由 freshness_evidence 字段与 DSC-20 审计面承载，未经标签轴显影（tag_matrix_non_gap counts 键实读）。
  suggest: 三选一归 Owner（标签冻结后机贴不改名，任何动法都是 Owner 门位）：①机制级补钉（把承载 fresh_check 语义的节点/机制加贴该标签）②声明两标签为"字段级语义"不入标签轴（图例注记）③维持现状（零钉合法，下次对审复念）。总筹意见：①最贴 SOP§2.4 显影本意，但会改动 28 格现贴——动静大，呈 Owner 权衡。
  anchors: config/data_supply_chain_map.yaml purpose_tags 段+各节点 purpose_tag；docs/_working/vmap12_intake/in1_four_way_draft.yaml §1 IN1-08

- id: IN1-E2
  title: DSC-15 日终三账对账处置二选一（退或接线复活）
  finding: obs=0/exp=7 判死+唯一"消费方"=backtest_backlog.yaml:1222 按空表降级设计（自愈绕开，非真实消费）；DSC-20 任务级对账 alive（3/3）已覆盖"应跑对打卡"主对账面；15:40 分派分支从未存在（WB12-15 P0 三证）。退与并两判据同指（宪法§4.2 ②+③）。
  suggest: 总筹二选一：①退（三账对账需求面由 DSC-20 覆盖或明示放弃；连带 GAP-RECDIFF 同步处置+MOD-TRADING-007 销挂）②修（补 15:40 分派分支接线复活）。禁默认保留（证据面零触发+零真实消费，留=违内收铁律②）。
  anchors: config/data_supply_chain_map.yaml DSC-15 trigger_facts/consumers；registry:backtest_backlog.yaml:1222；in1_four_way_draft.yaml §2 IN1-10+§3 IN1-15

- id: IN1-E3
  title: GAP-NAV 写器腿 live_nav_recorder 二选一（退+通知消费面 / 复活补供）
  finding: account_nav_daily 表 0 行（max=1970 哨兵）+写器 live_nav_recorder 全仓零调用方（11卷§1C），判死成立；但 **SPM:357(FAC-E8)/SPM:380(FAC-E9)/ops_alert_feed.py:39 三消费面在等**——退役须通知改降级，复活须接线补供。账户净值=资金面数据。
  suggest: Owner 门位二选一：①退写器腿+三消费方改降级设计②复活（接线+补供来源决策）。总筹不代裁（消费面涉及 SPM 因子口径）。
  anchors: config/data_supply_chain_map.yaml DSC-GAP-NAV trigger_facts/consumers；in1_four_way_draft.yaml §2 IN1-11

- id: IN1-E4
  title: 换源双实现收敛（circuit_breaker vs dual_source_guard/redundant_source 族）+ dual_source_guard 本体零调用
  finding: 同域（换源）双实现双平面在岗：source_circuit_breaker.py=2 调用方（scheduler+external_system_connector，盘后批量面）；redundant_source 族=tick_subscriber/connectors/intraday_main 多调用方（盘中 tick 面）；**dual_source_guard.py 本体零外部调用方**（本会话 grep 实证 2026-10-04，疑门面/死件）。
  suggest: 总筹排期代码级收敛（统一换源策略内核+双平面薄壳，F1a §2.2 原判"接线存疑"应升级为"部分在岗+本体死件"）；dual_source_guard 本体退役前须先清 connector 层引用关系（低置信，勿直接删）。本批禁动代码。
  anchors: src/zephyr/data/source_circuit_breaker.py；src/zephyr/data/dual_source_guard.py；src/zephyr/data/redundant_source/*；in1_four_way_draft.yaml §3 IN1-14

- id: IN1-E5
  title: GAP-FFVAL/FFSIG 工厂在线面 DDL 建表待批（Owner 窗口）
  finding: 两表 CH 侧不存在（247 表实测）+DDL 真源在仓未 apply+五个消费锚悬空（feature_store_writer.py:125/offline_store.py:25/ufl_deterministic_layer.py:226/buffer.py:25/78/87）——工厂在线面整体悬空，判死成立但属"待建"非"该退"。
  suggest: Owner 建表窗口批（💰与生产窗口）；批后随 regen 刷 verdict。F2z 已在案，本件仅对审视角重申（内收复审不得误判其退）。
  anchors: config/data_supply_chain_map.yaml DSC-GAP-FFVAL/FFSIG trigger_facts；docs/_working/vmap12_flesh/f2z_escalations.md

- id: IN1-E6
  title: GAP-L2TICK L2 权限外购决策（💰-4）
  finding: l2_tick/suspend 双 0 行+L2 权限=外部采购未做（💰-4）；cost_model_calibration 族 L2 腿消费在等。判死成立但属"待采购"非"该退"。
  suggest: Owner 资金门位：采购或明示放弃（放弃则 cost_model_calibration L2 腿降级设计固化）。同 E5 性质：对审视角重申禁误退。
  anchors: config/data_supply_chain_map.yaml DSC-GAP-L2TICK trigger_facts

- id: IN1-E7
  title: DSC-14D 退役连带面清单（若裁退——Owner 净删门位）
  finding: DSC-14D auto_backfiller 为本批唯一严格零触发零消费退候选（高置信），但退役非删一文件：①wiring_registry pure_library/exempt 条目处置（WB12-14 绕门记录）②MOD-DAT-AUTO-BACKFILLER 模块销册（翻译册/能力册/depgraph 三面）③src/zephyr/data/__init__.py re-export 摘除④骨架 §1 D12-14 第 4 腿分面⬜改判（骨架契约面）⑤图12 节点格处置（退格 or 改注记"退役留档"）。
  suggest: 若总筹裁退→按上五连带面开净删批走 Owner 门位（一次裁清单齐，免二次往返）；若裁"留档退役"（文件在盘摘挂载）→④⑤即可，①②③转为登记性退役。对照先例=storage_tiering 裁定#383 纸面退役（文件在盘未摘）。
  anchors: src/zephyr/data/auto_backfiller.py；docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml；in1_four_way_draft.yaml §2 IN1-09+§3 IN1-13

- id: IN1-E8
  title: sla_tracker 退役执行残腿确认（E-3 已裁，执行件困在 9 文件落地袋）
  finding: E-3 已裁退役（Owner 2026-10-04：复活或退役二选一→裁退役+casebook_registry outside_registry"永久不授册号"），但执行件之一 module_translation_registry.yaml sla_tracker 退役词条仍在 90_landing_handoff 9 文件袋内未落 HEAD（st-vm12g-20261004 停手移交态）。内收对审视角：本批已按"退役已裁"不列退候选，若 9 文件袋长期不落地，退役裁定与 HEAD 面持续漂移。
  suggest: 维护班/ chief 按交接卡两笔方序落地（token 先行+内容袋）；本批无动作，仅登记依赖关系防两案打架。
  anchors: docs/_working/vmap12_flesh/90_landing_handoff.md §落地残腿；docs/_working/vmap12_flesh/f1z_escalations.md E-3；docs/_working/vmap12_flesh/f2z_coverage_report.yaml §1 红1 sla_tracker 行

## 附：不构成呈批的顺带事实（已入草案正文，无需裁）

- DSC-12 双死件历史锚（storage_tiering/compression_archiver）——note_zh 已自述裁定#383 纸面退役+零调用实测，下轮 regen 修剪属总筹随手项（IN1-20）。
- DSC-13/DSC-20 同执行体双格+archiver 三格——一岗多流程合法（SOP§1.4），红2 抄写=0 佐证，观察不入簇（IN1-18）。
- 清洗/质量族与日历族互链非重复——grep 实证在案（IN1-16/17），禁后续对审误并。
- 数据供给链 8 空消费格中 5 格=合法空（17 互验自证/REPLAY/MIRROR/ARCHIVE-AUDIT 腿未接/TERMINUS 终点）——已拆入修候选 IN1-32，不另呈。
