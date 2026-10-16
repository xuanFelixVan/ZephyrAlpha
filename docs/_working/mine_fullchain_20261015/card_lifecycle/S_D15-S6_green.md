---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s6
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S6 判绿 green（P0）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S6 行，挖矿优先级 P0）
---

# D15-S6 判绿 green（卡生命周期十三态之六，P0）

## 1. 定义

- 语义（词表 value=green）：预注册阈值全过且 DSR 校正后仍显著。
- 状态机属性：非终态；credential_required=true；machine_readable=partial；legacy_field=`viability_verdict=supported`（净零直译在册字段，零新枚举）；`config/strategy_card_lifecycle_map.yaml#D15-S6`。
- 判据真源（INV-1 禁复制）：`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:60-66` §6 三态出口"达标"行（factor 回写 registry ic/ir/decay；strategy 走 sop_c C5-C6）。
- 禁边挂钩：X01 S7→S6 就地改判（AI 无翻案权，考试权只在 E4 咽喉）；X05 S2→S6 候选卡直接出 PASS；X10 S9→S6 把挂起读成通过。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M07 S5→S6（机判+人复判，credential=test_evidence=判定书+DSR 校正，skeleton=🔨 有出口无实例）：全仓 viability_verdict=supported 计 0 | `config/strategy_card_lifecycle_map.yaml#D15-M07`（evidence："experiment_registry 实测 supported=0 条"）；`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml:108`（viability_verdict: enum supported/refuted/inconclusive，实测 71 条中 69 null、2 refuted——`config/strategy_card_lifecycle_map.yaml#gaps.D15-G02.measured.viability_verdict_filled_by`=ALGO-VWAP-03/PRERG-MOM-01 皆 refuted） |
| 输出面 | M13 S6→S12 毕业（🔨 无实例）；M11 S6→S10 封卡（凭证通道在，判定书即可封） | `config/strategy_card_lifecycle_map.yaml#D15-M13/#D15-M11` |
| SSOT 真源 | 卡外报告面承载 verdict 三态词汇（PASS/RED/INSUFFICIENT）；在册枚举三值与词表 green/red/insufficient 净零直译 | `docs/_working/archive/2026-09/bizmine_night/algo_mining/momentum_prereg_card.md:36`（verdict 三态声明）；`docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml`（green 行 legacy_field 注） |
| 代码模块 | 回写目标册（人工+提交正门维护）：`docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（status：candidate 170/experimental 4/deprecated 1）、`strategy_registry.yaml`（lifecycle_status：candidate 151/backtest 8/sim 2）；DSR 原料=`docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml` | 上述各件实存；回写动作无专模块（走 GitCommitGateway 文件面） |
| 门禁约束 | X01/X05/X10 三条禁边全指往本态（判绿是全文最被提防的方向）；checker=CV-08/CV-07/CV-07（校验器规格面）；strategy_screen verdict 七值是策略件工序结论，禁隐式派生卡状态（boundary 硬边界 2） | `config/strategy_card_lifecycle_map.yaml#D15-X01/X05/X10`+boundary；`config/strategy_production_map.yaml:20`（"考试权只在 E4 咽喉"三铁律，骨架门③引） |
| 自动化触发 | 策略侧毕业近邻面（非卡态）：`data/strategy_intake/promotion_advisories/ADV-20261014-STR-VREV-025.json`（lifecycle_now=sim，fw_backtest sharpe=-2.12，governance_action=promote_paper，recommendation=promote）——strategy_registry 生命周期轴的推进建议件，与卡态轴 disjoint | `data/strategy_intake/promotion_advisories/ADV-*.json`（3 件，20260930/20261009/20261014 同一 STR-VREV-025 三连拍） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | 判定书判据完备、禁边三面设防，但 supported 零实例=入口从未通电（M07 🔨） |
| 输出面 | warn | 两个出口（M13 毕业/M11 封卡）在册均无 green 起点实例 |
| SSOT 真源 | pass | legacy_field 直译方案（净零）与在册枚举一字不差，词表/图/册三面一致 |
| 代码模块 | warn | 回写目标册在、DSR 原料账在；"判定书→回写→卡标 green"无执行器（纯人工流程） |
| 门禁约束 | pass | 本态禁边密度全图最高（X01/X05/X10），checker 规格齐；无在册活违规指向 S6（没人非法改判成绿过） |
| 自动化触发 | fail | 绿从未发生且无自动化路径可产生：判定书→viability_verdict 回填→card_state=green 三步全人工，历史 71 条 run 仅 2 条回填且皆红 |

## 4. 缺口与建议

1. 缺口（P0 主缺口）：判绿半边状态机未通电——S6 零实例使 M13 毕业链（图15→FACTORY E8 组装挂图）从未实走，骨架 §3 缺口 13"毕业包→挂图→生产闭环对账缺失"因此无法验证。建议 IBT 批D 重考窗选卡走通全链（与 S5 建议 2 同一动作，一次补两态）。
2. 缺口：promotion_advisories 的 ADV 三连拍（同卡 9/30→10/9→10/14 建议 promote）说明 strategy 轴在动、卡轴不动——两轴的凭证（fw_backtest run_id=bt-fw-823d7fd7）无 card_id 关联。建议 graduation 实现时把 advisory advisory_id 写入宿主册 verdict_bindings.evidence_path 族，形成跨轴可追溯。
3. 建议：X01 的机验落点最省的是 credential 流水校验（from=red,to=green 无合法边→凡出现即红，CV-08 规格已有）——随墓碑门复活一并接线。
