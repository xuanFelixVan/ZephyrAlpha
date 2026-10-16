---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s5
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S5 在测 executing（P0）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S5 行，挖矿优先级 P0）
---

# D15-S5 在测 executing（卡生命周期十三态之五，P0 咽喉=FACTORY E4 考试执行态）

## 1. 定义

- 语义（词表 value=executing）：试验台账行已开、执行件跑数中。
- 状态机属性：非终态（全图唯一瞬态语义驻留）；credential_required=true；machine_readable=no（卡侧）/yes（run 侧 status=running，两套零交集）；`config/strategy_card_lifecycle_map.yaml#D15-S5`。
- 与工厂轴关系：本态=FACTORY E4 考试咽喉（82 节点）的执行态投影；骨架明示"=E4 考试执行态"（`docs/_working/mine_fullchain_20261015/00_skeleton.md` §2.2 D15-S5 行）；工厂节点 build_status 是工序进度、与卡契约地位无映射（图 boundary 轴区分条款）。
- 禁边挂钩：X06 S1→S5 未冻结先跑数（CV-04，机验=S5 时间戳<S3 冻结时间戳即红，时间真源=git commit）；X07 S5→S6 无试验台账行（CV-09，`exam_policy.md:31`"后补=造假"）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M06 S3\|S4→S5（actor=machine，credential=test_evidence，四条准入全绿：frozen 卡/N_eff 封闭族/沙箱三关/试验台账行已开，✅，observed=T0-PRERG-02×2） | `config/strategy_card_lifecycle_map.yaml#D15-M06`；`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:24-30`（§1 准入四条原文）；`docs/_working/archive/2026-09/bizmine_night/t0_matrix/t0_conditional_e4_result.yaml` + `t0_conditional_e4_verdict.md`（骨架锚在盘核验） |
| 输出面 | M07 S5→S6（🔨 有出口无实例）、M08 S5→S7（✅ 3 卡 observed）、M09 S5→S8（✅ observed=P3-E1C-09） | `config/strategy_card_lifecycle_map.yaml#D15-M07/M08/M09`（observed_in_registered_ledger 字段） |
| SSOT 真源 | 卡侧零实例（instances_observed=0）；run 侧真源=试验台账行+EXP 登记条目 status=running | `docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（counting_rule=screen_runs.total_trials+sum(batch_records.n_trials)，total_trials=269，batch_records 在册，manual_population=0）；`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（entry_schema status: enum running/completed/failed/archived） |
| 代码模块 | 考试执行件族：`scripts/audit/t0_conditional_e4_exam.py`（+v2/v3 同族）、`t0_ceiling_capacity_exam.py`、`t0_gpu_condition_pack.py`、`t0_six_phase_materialize.py`（全带 [BLUEPRINT]/INVARIANTS/MODIFY-GUARD 头）；run 档案器 `src/zephyr/backtest/run_archive.py`（VAL/BACKTEST/SCREEN/ABLATION 四 kind 必选步骤+content_sha256 指纹）；考尺参数册 `config/exam_scale_cost_gate.yaml` | 上述各件实存（本批 ls/grep 核验） |
| 门禁约束 | 准入四条=点火唯一前置（`exam_policy.md:26`"不满足任一条=禁点火，跑了也白跑（结论作废）"）；机验规格 CV-04（时序）/CV-09（台账行）在校验器；无 commit 期强制 | `exam_policy.md:24-30`；`scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py`（CV-04/CV-07 规格） |
| 自动化触发 | 跑批实物：`data/strategy_intake/grid_t0_conditional_v1/`（T0 条件矩阵 v1：1826 行×条件门/价轴/温度计/宏观四轴，truth_sources 指向 `docs/_working/t0_matrix/six_phase_history_v1.csv`+`c1_market.emotion_index`+`c1_backtest.regime_state_anchored`，negatives.csv 负结果同权在盘）——正是 T0-COND-V2/V3 冻结卡的考卷材料 | `data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml`（generated 2026-10-15，sid=st-t0-matrix-20260924）、`t0_condition_matrix_v1.csv`、`negatives.csv` |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | M06 双实证（T0-PRERG-02 credential seq2/seq5 machine_admitted）；准入判据四条全文在 exam_policy §1 |
| 输出面 | warn | M07 判绿口零实例（supported=0）；M08/M09 口畅通——出口偏科=只出红/不可判，绿从未发生 |
| SSOT 真源 | pass | trial_ledger（269 trials/25 runs/8 batch_records）与 EXP 册 status 枚举两面齐备、计数经机生 |
| 代码模块 | pass | 执行件/档案器/考尺参数册三层全实存，BLUEPRINT 反向锚指向的卡在盘（`docs/_working/t0_matrix/` 2026-10-09 裁定#496 死信清偿 22 件复活） |
| 门禁约束 | warn | X06/X07 有机验规格、无 commit 接线；"跑了也白跑"的作废结论依赖人记（M16 零登记，见 S13） |
| 自动化触发 | warn | 跑批自动化在（grid 产物+meta truth_sources 三真源声明），但"开跑即开台账行/卡面转 executing"无自动写——卡面在测实例恒 0 |

## 4. 缺口与建议

1. 缺口：卡面 executing 零实例与 run 侧 running 条目零交集（骨架 §3 B 面结论的现行延续）。建议最低成本收口：grid 跑批 meta 已带 sid/generated——跑批器落 meta 时同步在宿主册 upsert CARD-* 行 card_state=executing，一次性接通两轴。
2. 缺口：M07 判绿口从未走过（`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml` viability_verdict 71 条中 69 条 null、仅 2 条 refuted）——判绿路径未经验证等于状态机半边未通电。建议下一轮考试（IBT 批D 新鲜窗）人为选定一条有望达标的卡走通 S5→S6→S12 全链做黄金样本（骨架作业簿 10 同案）。
3. 建议：X06 时序机验的输入（S3 冻结时间戳）现在只有 git commit 可用；建议 frozen 落盘时在宿主册记 frozen_at（body_fingerprint.frozen_at 字段已在 schema，实测全 null——回填即可用）。
