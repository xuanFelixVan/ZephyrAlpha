---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s11
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S11 判死归档 condemned（终态）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S11 行）
---

# D15-S11 判死归档 condemned（卡生命周期十三态之十一，终态）

## 1. 定义

- 语义（词表 value=condemned）：终态，机制证伪或数据面不可修，入死矿账防复挖。
- 状态机属性：terminal=true；credential_required=true；machine_readable=no；`config/strategy_card_lifecycle_map.yaml#D15-S11`（build_status=partial）。
- 判据真源：`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md` §6 出口"判死归档"行 + §5.4 死矿登记（判死单须带 ≥3 个已排除候选与排除理由；复挖须带新机制假设或新数据面，否则禁复挖）。
- 现状：instances_observed=0——判据强制专册，实际无死矿专册（红条目 F-06），判死散在各战役台账"挖干/TERMINATE"行。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M12 S7→S11（actor=human，credential=判死单（≥3 已排除候选+理由）+死矿登记，skeleton=🔨"散在台账 TERMINATE/挖干行，无死矿专册（负结果台账缺面，F-06）"） | `config/strategy_card_lifecycle_map.yaml#D15-M12`；`exam_policy.md` §5（:52-58 五条：全量入册/判死配额/次数留痕/死矿登记/落点）；台账活体=`docs/_working/archive/2026-09/tdchain_mine/a0_master_ledger.md`（状态列实测：执行中 4/挖干 1/挖干待合并 1/阻塞待终端 1/待 W1 1/待 E8 1）；`docs/01_policies_and_standards/sop/mining_sop/sop_b_node_loop.md:73-77`（⑦判死对齐） |
| 输出面 | M17 S11→新卡 S1（带新机制假设或新数据面的新卡，旧卡状态不变）；无其他出口 | `config/strategy_card_lifecycle_map.yaml#D15-M17`；`exam_policy.md` §5.4 |
| SSOT 真源 | 无宿主：负结果/死矿登记"落点=战役台账行+lane 目录全量 results 件"（判据原文），注册表层零专册（76 本 catalogs 无 negative/dead_mine 册，骨架门④实测）；fail-closed 负结果实物范本=`data/strategy_intake/grid_t0_conditional_v1/negatives.csv`（负结果同权在盘的跑批级范本，跑批域非卡域） | `exam_policy.md` §5；`docs/01_policies_and_standards/_registry/catalogs/`（本批 ls 无 negative/dead_mine 册）；`data/strategy_intake/grid_t0_conditional_v1/negatives.csv` |
| 代码模块 | 零实现：死矿登记器、复挖闸（新假设检查）、判死单模板机读化均无；最近邻构件=`src/zephyr/experiment_tracking/`（实验登记 CRUD，无 condemned 语义） | `ls src/zephyr/experiment_tracking/`（__init__/experiment_tracker/fallback_tracker/models/query/config，本批核验） |
| 门禁约束 | X04 S11→S5 无新假设复挖死矿（checker=CV-05，enforcement=machine_checkable 但"⬜ 无机验面（无死矿册）"——禁边对象本身不存在，禁令悬空） | `config/strategy_card_lifecycle_map.yaml#D15-X04`（bypass_guard："此禁令只能靠实例面判"，而实例面=空） |
| 自动化触发 | 零。判死动作散文化；"防同一死矿被反复挖"目前全靠人记（F-06 原文："判据 §5.4 的防同一死矿被反复挖目前靠人记"） | `docs/_working/map_build/fig15_cardlife/00_skeleton.md` 红条目表 F-06 行 |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | 输入判据完备（判死单三候选+理由），台账 TERMINATE 行证明判死在实践中发生，但无一例走成在册 condemned（输入面有实无账） |
| 输出面 | warn | M17 是唯一出口且有语义判据（新机制假设/新数据面）；零实例无法验证 |
| SSOT 真源 | pass（消极意义上） | 图/词表/骨架三面语义一致、无漂移——但宿主缺位本身就是 F-06（真源缺位记在 gap，不记 fail 因为其处置已定为"内收/新册"待决） |
| 代码模块 | fail | 全域零实现（登记器/复挖闸/模板皆无） |
| 门禁约束 | fail | X04 禁边无机验面（无死矿册可查），禁令悬空；"复挖须带新假设"无人机拦 |
| 自动化触发 | fail | 零自动化；防复挖纯人记 |

## 4. 缺口与建议

1. 缺口（F-06 主文）：死矿无专册。两个候选宿主（骨架作业簿 05 已列）：内收 `trial_ledger_registry.yaml` 增 dead_mines[]（计数经机生，零新册）或 `experiment_registry.yaml` 增 entry_kind=condemned 条目类。推荐前者（试验台账已有 counting_rule 机生纪律，死矿正是"试验次数账"的负结果半边）。
2. 缺口：判死单模板（≥3 已排除候选+理由）无机读形态。建议照 prereg 卡模板先例（factor_mining_sop §4 YAML 块）给判死单定 5 字段模板：condemned_card_id/excluded_candidates[≥3]/reason/redata_or_rehypo/refuses_until。
3. 建议：X04 的机验在死矿册落地后自动获得输入（复挖新卡的 hypothesis_key 撞 dead_mines 键且无新假设声明即红）——顺序上先补册，禁边接线随后即来，无需并行开发。
