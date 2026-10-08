---
ttl: task_bound
completes_when: Owner 对 blockers 条目拍板销账批落地后随袋回收
created: 2026-10-08
sid: st-mx07-L12
title: R1/R2 地图名实错位调档一页纸 v1
session: st-mx07-L12
status: 调档简报 v1（只读调档，零施工）
---

# r1r2_misalign_brief_v1 — R1/R2 地图名实错位调档一页纸（st-mx07-L12，2026-10-08 夜战）

## 0. 一句话结论

权威开方页 `docs/_working/matrix_campaign/fac9_05_drift_repair_plan.md` §一 的两处名实错位
（R1=E1A 挂点 035、R2=BT-201 撞号）**本体均已于 2026-10-04/05 治本落 HEAD**（裁定#484③ +
fac9_04_followup§一，commit 9141a83d77 / 46652cc260）；裁定#489⑥ 所推迟的"另立裁定"实为
**销账+残余清理批**（F1-F5 全 S 级，见 §3），无改图/改引用大手術。

## 1. 错位条目清单（名/实/权威出处/现状）

### 条目 R1：FAC-E1A「车道A-社区货源」挂点 MOD-BT-035 名实错位
- **名（错挂时）**：节点 module_ref=MOD-BT-035，册名「C2 粗筛成绩灌表」，真身
  `scripts/backtest/intake_load_screen_c2.py`（path_ownership_map.yaml:22256；册名真源
  module_translation_registry.yaml:9020）——灌表是 A 车道**下游工序**，与节点名对不上。
- **实**：车道A 真身=社区货源盘点归一 `scripts/backtest/strategy_intake_inventory.py`
  （头注自报域蓝图 MOD-BT-001，无独立编号，fac9_02_mount_writeback.md:41 同证）。
- **权威出处**：发现=`docs/_working/map_census/fac9_01_report.md:26`；
  处方=`docs/_working/matrix_campaign/fac9_05_drift_repair_plan.md:17-22`（二选一）。
- **现状：已治本**——`config/strategy_production_map.yaml:117` 现值
  `module_ref: scripts/backtest/strategy_intake_inventory.py`（commit 9141a83d77，
  2026-10-04，st-map9-f4；裁定#484③ 销账=ruling_registry.yaml:4132 起，"F1 名实挂账#2 销账"）。

### 条目 R2：MOD-BT-201 双源冲突（path_ownership vs battle_map）
- **名（冲突时）**：path_ownership_map 两行 owner_blueprint=MOD-BT-201
  （path_ownership_map.yaml:18588=tests/research/backtest/test_forward_post.py、
  :22179=scripts/backtest/forward_post.py）；battle_map_alignment_report 曾表行
  =Closed Book Gate（src/zephyr/backtest/core/closed_book_gate.py）——两真源打架。
- **实（考古定谳=`docs/_working/map_census/fac9_04_followup.md:13-17`）**：**单向撞号非重挂**——
  201 法定=前哨对账器 forward_post（出生 5dc8020401，2026-09-16 四大件蓝图"号段 201-210 空闲"）；
  closed_book_gate.py 2026-10-02 出生（055ad8cf307）第 1 行复制粘贴盖错模板头；
  battle 报告行=三手派生物（生成器扫错误头注再生）。
- **现状：已治本**——closed_book_gate.py:1 头注现值 **MOD-BT-205**（commit 46652cc260，
  2026-10-05，"201撞号改授"）；battle_map_alignment_report.md:132 已自愈（2026-10-05 22:08
  再生=「MOD-BT-205 闭卷读取闸」）；裁定#485 跳号制度化（005/008-012/016-019 永不复用，
  台账=fac9_04_census_ledger）。

## 2. 影响面（谁引用了错的名字）

- **运行时/交易路径：零**——两处均为图册挂点名实错位，无代码按错名调用（重要：非资金面事故）。
- 活体派生册：`config/ai_search_veins.yaml:137` VEIN-FAC-E1A module_ref **仍=MOD-BT-035**
  （册头自注"生成器产出禁手改"，生成时点早于 10-04 修复=陈旧派生残留）。
- 活体地图注记：`config/strategy_production_map.yaml:4126` FAC-E7-M-005 name_zh 内嵌
  「（名实冲突见报告：battle 表作 Closed Book Gate）」历史注记（冲突已解未清洗）。
- 陈旧快照：`docs/02_enterprise_architecture/06_decision_architecture/99_decision_track_placeholder.md:249`
  （2026-08-20 生成）仍列 201 占位行。
- 历史文书（不改，防再引即可）：factory_flow_20261007/E7_模拟盘前哨.md:22、
  decision_map_campaign_20260924/cmd_successor_20260925/PIT_closed_book_and_dsr.md:61
  （"closed_book_gate=201"早于定谳）、fullflow_mining/01_strategy_factory/03_f15_lane_a_community.md:6、
  fullconnect_campaign/b_factory_inbound/03_f15_lane_a_community.md:17、
  circulation_chief/skeleton/00_skeleton.md:94、full-auto-chain/S04_hypothesis_intake/README.md:22
  （均按"车道A=035"旧挂点引）。
- 账面滞后：fac9_05_drift_repair_plan.md §一（开方册创建 2026-10-06 晚于修复，未见销账注记）、
  master_backlog_v2.md:56 P3-5（挂"调档中"）。

## 3. 修复处方（全 S 级；F1 需 Owner 随批，F2-F5 可并入地图值班队下一笔）

| # | 处方 | 对象 | 工作量 |
|---|------|------|--------|
| F1 | 销账裁定（Owner 随批）：fac9_05 §一 R1/R2 标 resolved（引裁定#484③+fac9_04_followup§一+commit 9141a83d77/46652cc260）；backlog P3-5 销行 | 裁定册+backlog | S（登记级） |
| F2 | 重跑 `scripts/ai_layer/gen_search_veins.py` 自愈 VEIN-FAC-E1A（生成时拷贝地图 module_ref，gen_search_veins.py:104），跑后核对 :137 | ai_search_veins.yaml | S |
| F3 | FAC-E7-M-005 name_zh 去历史冲突注记→净名「E7 前哨对账器」+validator 复验 | strategy_production_map.yaml:4126 | S（1 行） |
| F4 | TDM-P-P1 补 `module_id: MOD-POS-030`（真身自报 src/zephyr/position/core/position_checkup_orchestrator.py:1；TDM R21 族 3→1 后最后一枚"有 ref 无 id"） | trading_decision_map.yaml:2899 | S（1 行） |
| F5 | placeholder 轨重跑再生自愈 201 行（或册头声明快照时点），防再引 | 99_decision_track_placeholder.md | S |
| 不动 | path_ownership_map（生成器产物禁手改，裁定#485 明文"台账=权威记录面"）；34_d_backtest.md:5026（035 本名"灌表"无错，错在挂点）；§2 所列历史文书 | — | — |

## 4. 同号异义族澄清（任务卡三条线索定谳，防再混）

- L9 workbook C28 段「R1-R3 试点批」=**镜像树迁移批次号**（M3_mirror_tree_migration/mirror_tree_prep.md），非名实错位。
- TDM「R1/R21 漂移族」=validate_decision_map **校验规则号**：R1（ref 漂移）28→25、R21（"有 ref 无 id"）0→3
  见 docs/_working/2026-09-09-tdm-missing-modules-construction.md:279；2026-10-08 复测：三节点已全补 id
  （TDM-E-L2-09-1=MOD-INT-NEWS-CHAIN / TDM-E-L2-09-2=MOD-INT-CHAIN-IMPACT / TDM-E-L3-08=MOD-SIG-142），
  仅余 TDM-P-P1 一枚（→F4 处方）。
- L09 800ms 复测尺「R1/R2/R3」=性能口径分层（全进程/进程内冷/热），非名实错位。
- **唯一权威「R1/R2 名实错位」=fac9_05_drift_repair_plan.md §一（lane R-road-repair）两处**，即本简报条目 R1/R2；
  总包链路锚：master_backlog_v2.md:56（P3-5）→ 裁定#489⑥（ruling_registry.yaml:4275 起）→ 99_delivery.md:55。

## 5. 盲点自查（禁留白）

1. 本简报只读调档：F2-F5 均未实跑，净效果以施工队跑批读数为准。
2. fac9_05 作者（R-road-repair 车道）未吸收 #484/#485 的时序原因未考古，只记事实不诛心。
3. VEIN-FAC-E1A 自愈后 module_ref 将变路径形态（同图锚），矿脉消费方是否接受路径形态 ref 未验证。
4. fig13/fig16 等在飞队伍若正改 strategy_production_map，F3 需错峰（本册零触碰，冲突面留给施工队申报）。
5. placeholder 轨真源=decision_graph_model.yaml→PG，201 行是否随再生消除未实测（按 2026-08-20 快照推断）。
6. 未复核 battle_map 报告生成器调度节律（下次再生时点），F5 的"自愈"依赖该节律。
