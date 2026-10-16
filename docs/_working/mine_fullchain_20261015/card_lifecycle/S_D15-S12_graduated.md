---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s12
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S12 毕业出卡 graduated（P0，终态）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S12 行，挖矿优先级 P0）
---

# D15-S12 毕业出卡 graduated（卡生命周期十三态之十二，终态，P0）

## 1. 定义

- 语义（词表 value=graduated）：终态，结论已回写因子与策略册，卡使命完成。
- 状态机属性：terminal=true；credential_required=true；machine_readable=partial；`config/strategy_card_lifecycle_map.yaml#D15-S12`（build_status=built）。
- 判据真源：`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:64`（"factor 回写 registry ic/ir/decay；strategy 走 sop_c C5-C6"）+ `docs/01_policies_and_standards/sop/mining_sop/factor_mining_sop_policy.md:71`（三出口之"达标"→S6 备料→回写）。
- 下游（骨架总纲 §2.2）：FACTORY E8 组装/TDM 挂图——`config/strategy_production_map.yaml` FAC-E8 上游显式含"图15-S12 graduated"。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M13 S6→S12（actor=human+提交正门，credential=回写 factor/strategy 册+原卡封存，skeleton=🔨"册侧字段在，卡侧无从反查（J3）"）：**零实例**——因上游 S6 判绿零实例而从未触发 | `config/strategy_card_lifecycle_map.yaml#D15-M13`；`docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（status=experimental 4 条是回写产物侧证据）；`docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml`（lifecycle_status：backtest 8/sim 2） |
| 输出面 | 无（终态）；知识遗产转 E6 衰减监控（属工厂域）；下游交接=FACTORY E8 组装（仓位配方 17 维）与 TDM 挂图 | `config/strategy_production_map.yaml`（FAC-E8 上游行）；`docs/_working/mine_fullchain_20261015/00_skeleton.md` §3 缺口 13（"毕业包→挂图→生产的闭环对账缺失"） |
| SSOT 真源 | 回写目标册两面（factor/strategy registry）字段齐但**无 card 反查键**（J3：两套键空间零交集）；策略侧生命周期近邻实物=`data/strategy_intake/promotion_advisories/ADV-20261014-STR-VREV-025.json`（lifecycle_now=sim→promote_paper 建议，带 fw_backtest run_id 证据） | `factor_registry.yaml`/`strategy_registry.yaml`（无 card 字段，本批 grep 核验）；ADV JSON（strategy_id=STR-VREV-025，evidence.fw_backtest.run_id=bt-fw-823d7fd7） |
| 代码模块 | 组装消费侧：`src/zephyr/pf_alloc/`、`src/zephyr/pf_core/`（E8 面）；衰减监控面：`src/zephyr/factor/analysis/factor_lifecycle_runner.py`、`src/zephyr/feedback_loop/`（E6/E9 面）；毕业回写执行器：无 | 上述目录实存（本批 ls 核验）；回写无专模块 |
| 门禁约束 | X11 把卡内判据正文抄进因子/策略册（CV-12，40 字滑窗机验规格）——毕业回写是 X11 的最高风险场景；X09/X10 联动（同假设双卡防双计、挂起卡禁入 E7/E8） | `config/strategy_card_lifecycle_map.yaml#D15-X11` |
| 自动化触发 | 零卡侧自动化；策略侧自动建议件在（promotion_advisories 3 件连拍），证明"毕业→推进"在策略轴已有半自动节奏，但卡轴无对应物 | `data/strategy_intake/promotion_advisories/`（ADV-20260930/20261009/20261014 同卡三拍） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | fail | M13 零实例：判绿口（S6）零实例的下游连锁——毕业链从未实走，本态纯理论 |
| 输出面 | warn | 下游 E8/TDM 挂图声明在册（FACTORY 图 handoffs），但"毕业包→挂图→生产"无机械对账件（骨架缺口 13） |
| SSOT 真源 | warn | 回写目标册字段在、键断（无 card 反查）；promotion advisory 是完整度更高的策略侧对照物（证据结构化：run_id/回撤/panel_ok） |
| 代码模块 | warn | 消费侧模块全在（pf_alloc/pf_core/factor_lifecycle_runner），缺的只是"卡→册"来源键与回写器 |
| 门禁约束 | warn | X11 机验规格在（校验器 CV-12 实跑未红=图与册面干净）；无毕业专闸 |
| 自动化触发 | fail | 卡侧零自动化且无规划件；策略轴半自动（advisories）与卡轴零自动形成轴间失衡 |

## 4. 缺口与建议

1. 缺口（P0 主缺口之二）：毕业链（S6→S12→E8 挂图）零实走+零对账。建议与 S6 建议 1 合并处置：IBT 批D 走通一条全链后，以该卡为准补"毕业包最小件"定义（verdict 判定书+回写 diff+挂图引用三件）。
2. 缺口：卡→册来源键缺失（J3）。最小修法=`factor_registry.yaml`/`strategy_registry.yaml` 条目增 `source_card_id` 可空字段（净零：字段加列不新增册），M13 执行时必填；生成器下轮回扫即可出"册条目↔卡"覆盖率账。
3. 建议：promotion_advisories 的 ADV 三连拍模式（同一策略按月复拍建议件）值得卡轴借鉴——M13 触发时在宿主册生成 graduation_advisory 行（含 evidence 指针），让毕业有可审计的时间序列而非一次性动作。
