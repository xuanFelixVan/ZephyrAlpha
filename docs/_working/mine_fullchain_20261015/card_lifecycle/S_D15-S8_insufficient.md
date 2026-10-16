---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s8
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S8 不可判 insufficient（P0）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S8 行，挖矿优先级 P0）
---

# D15-S8 不可判 insufficient（卡生命周期十三态之八，P0）

## 1. 定义

- 语义（词表 value=insufficient）：样本或功效不足、fail-closed 存疑，既非绿也非红。
- 状态机属性：非终态；credential_required=true；machine_readable=partial；legacy_field=`viability_verdict=inconclusive`；`config/strategy_card_lifecycle_map.yaml#D15-S8`。
- 进入判据：桶 n<功效门 / 配对数<30 / 判据不可评（骨架 §1）。
- fail-closed 纪律：`docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md` biz4 行"verdict=存疑(fail-closed)…can_deploy=false 放行权 Owner"。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M09 S5→S8（机判 fail-closed，credential=样本/功效不足须显式标，✅ 2 例：insufficient_samples、存疑 fail-closed；observed=P3-E1C-09） | `config/strategy_card_lifecycle_map.yaml#D15-M09`；`docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md`（biz2 行"维持 insufficient_samples：0/24 毛价差≥30bp 前置"；biz4 行 fail-closed） |
| 输出面 | M14 S8→S9 挂起（裁定必备+必填 trigger 表达式，✅ E1C-09 一例）；M11 S8→S10 封卡；S8→S5 重跑（须新卡或触发条件，禁原地重跑） | `config/strategy_card_lifecycle_map.yaml#D15-M14/#D15-M11`；`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（裁定#398 R2 条目+裁定#404 R2："E1C-09 判挂起并入 IBT 批D 新鲜窗重考…零成本保期权，禁直通模拟盘"） |
| SSOT 真源 | 在册枚举=`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（viability_verdict: enum supported/refuted/inconclusive；inconclusive 回填 0 条）；卡面/台账面证据在战役台账 | `experiment_registry.yaml`（schema 行 :108 附近，map 锚 :102 有 6 行漂移）；`experiments_ledger.md` |
| 代码模块 | 功效门判据=考尺参数册 `config/exam_scale_cost_gate.yaml`（考尺/成本门/DSR 全参数）；DSR 原料=`trial_ledger_registry.yaml`（n_eff→校正链）；N_eff 估计器口径件=`docs/_working/2026-09-15-neff-estimator-preregistration.md`（归档孪生在 `docs/_working/archive/2026-09/c_class_scattered/`） | 上述各件实存 |
| 门禁约束 | 本态无专属禁边（fail-closed 本身是"禁读成绿/红"的判据内约束）；出口 M14 强制 trigger 表达式入册；校验器对本态无活违规 | `config/exam_scale_cost_gate.yaml`；`ruling_registry.yaml` 裁定#404 R2 |
| 自动化触发 | 判定链：考尺（exam_scale_cost_gate）→考试件跑批→样本/功效不足显式标——前半自动、末步人工转录；挂起后重考触发（M15）零实现（归 S9 记账） | `config/exam_scale_cost_gate.yaml`（实存）；`config/strategy_card_lifecycle_map.yaml#D15-M15`（⬜ 零活体） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | M09 双活体（biz2 样本不足/biz4 fail-closed 两种成因各一例，形态覆盖好） |
| 输出面 | pass | M14 有唯一完整实例（P3-E1C-09：判挂起+并入批D+凭证裁定#398/#404 双在册） |
| SSOT 真源 | warn | inconclusive 回填 0 条（枚举三值只用其二）；map 锚 experiment_registry.yaml:102 与现行 ：108 有 6 行漂移（锚新鲜度） |
| 代码模块 | pass | 考尺参数册/试验台账/N_eff 口径件三层齐备实存 |
| 门禁约束 | warn | fail-closed 纪律靠判据文本+台账行自律；"存疑卡被当通过消费"无机验（X10 只护 S9 不护 S8） |
| 自动化触发 | warn | 末步显式标人工；且 P3-E1C-09 后续演化（S8→S9）证明本态是过路态——卡在 S8 的驻留应短暂，现无 SLA 约束 |

## 4. 缺口与建议

1. 缺口：S8 无专属禁边——"把不可判读成不可用"或"读成可用"都无机验。建议校验器加廉价腿：登记 inconclusive 的卡若被任何 E7/E8/挂图面引用即 warn（与 X10 的 S9 检查同构）。
2. 缺口：inconclusive 零回填使三值枚举半闲置。建议生成器加确定性腿：台账/报告出现 insufficient_samples/存疑(fail-closed) 词元即回填 inconclusive（认词元不猜语义，与 S7 建议 3 同批）。
3. 建议：S8→S5 重跑须新卡或触发条件的判据建议落成校验规则：credential 流水 from=insufficient,to=executing 且无新卡号/无 trigger 字段即红。
