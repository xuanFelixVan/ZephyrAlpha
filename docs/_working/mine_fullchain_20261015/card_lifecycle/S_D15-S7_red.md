---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s7
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S7 判红 red（P0）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S7 行，挖矿优先级 P0）
---

# D15-S7 判红 red（卡生命周期十三态之七，P0）

## 1. 定义

- 语义（词表 value=red）：阈值未过，机制假设是否可修尚未定。
- 状态机属性：非终态；credential_required=true；machine_readable=partial；legacy_field=`viability_verdict=refuted`；`config/strategy_card_lifecycle_map.yaml#D15-S7`。
- 判据真源：`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:60-66` §6"不达标有假设"出口（回 S0-S3 带假设登记，禁止原地调参重跑凑数）。
- 禁边挂钩：X01 S7→S6 就地改判（机验=状态流水 red→green 即红）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M08 S5→S7（机判，credential=test_evidence 同上，✅ 多例，observed=ALGO-VWAP-03/PRERG-MOM-01/T0-PRERG-02 三卡） | `config/strategy_card_lifecycle_map.yaml#D15-M08`；`docs/_working/archive/2026-09/bizmine_night/algo_mining/vwap_exam_report.md:13`；`docs/_working/archive/2026-09/bizmine_night/crypto_probe/funding_carry_results.md`；登记面 refuted 恰 2 条（`experiment_registry.yaml` CARD-ALGO-VWAP-03/CARD-PRERG-MOM-01 viability_verdict: refuted） |
| 输出面 | M10 S7→S4 一次性重判（裁定#363 唯一活体）；M11 S7→S10 封卡（✅ funding）；M12 S7→S11 判死归档（🔨 无死矿专册，F-06） | `config/strategy_card_lifecycle_map.yaml#D15-M10/#D15-M11/#D15-M12`；`docs/_working/archive/2026-09/bizmine_night/crypto_probe/funding_carry_rejudge.md:20`（"verdict=RED 变硬"，+4.09%→+3.03% 差距 0.91pp→1.97pp 原判方向零翻转） |
| SSOT 真源 | 登记面 red=2（by_registered_state）；台账 card_state=red=2；卡面镜像错位 1 例（ALGO-VWAP-03 card_face_state=frozen 对 registered red） | `config/strategy_card_lifecycle_map.yaml#corpus.by_registered_state`（red: 2）/#card_ledger（CARD-ALGO-VWAP-03 card_state: red + card_face_state: frozen） |
| 代码模块 | 判定书产出面=考试件+报告（`scripts/audit/t0_*_exam.py` 族 + `docs/_working/archive/2026-09/bizmine_night/algo_mining/{momentum,ofi,vwap}_exam_report.md`）；策略件工序判定=CH `c1_backtest.strategy_screen`（verdict 七值 1,340 行，与卡态跨域不并，boundary 硬边界 2） | 上述各件实存；CH 表经 `get_db_service().get_clickhouse_conn()` 正门（骨架 J3 实测） |
| 门禁约束 | X01（CV-08）+ 台账只增纪律（`config/strategy_production_map.yaml:20` 考试权条款 + strategy_screen verdict 只增）；**本态有在册活违规**：校验器 CV-10 判"ALGO-VWAP-03 卡面镜像 frozen ≠ 登记真源 red" | `config/strategy_card_lifecycle_map.yaml#D15-X01`；校验器 2026-10-15 实跑 ERROR：`CV-10——ALGO-VWAP-03 卡面镜像 frozen ≠ 登记真源 red（F-03 同型）` |
| 自动化触发 | 判红动作=考试件跑完出报告，人工转录 verdict 入册；viability_verdict 回填仅 2/71 条（G02 measured）——回填自动化为零 | `config/strategy_card_lifecycle_map.yaml#gaps.D15-G02.measured.viability_verdict_filled_by` |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 三卡红有完整证据链（报告+登记+流水），M08 是全图触发次数最多的边 |
| 输出面 | warn | M10/M11 各 1 例（全押在 funding 一张卡上）；M12 判死口零实例（死矿无专册，判死单承诺落空 F-06） |
| SSOT 真源 | fail | CV-10 活违规：ALGO-VWAP-03 卡面仍写 frozen、登记面已是 red——派生面与真源冲突现行在案（F-03 同型第二例） |
| 代码模块 | warn | 报告/登记面齐；"考试件 verdict→宿主册回填"无代码路径（2 条 refuted 是生成器代扫回填） |
| 门禁约束 | fail | CV-10 活违规未处置+X01 无 commit 接线+专闸墓碑；本态是全图违规密度最高态之一 |
| 自动化触发 | warn | 考试件自动出 verdict 报告在（exam 件+report+results.csv 族），登记回填自动化缺 |

## 4. 缺口与建议

1. 缺口（最急）：CV-10 ×1 活违规（ALGO-VWAP-03 卡头 frozen 未跟登记 red）。处置=按词表 ssot_note 方向"恒为 册→md"回写卡头（一行的 frontmatter 补丁），或按 F-03 先例留裁定登记。这是 8 条校验器 ERROR 中修复成本最低的一条。
2. 缺口：M12 判死口零实例（负结果台账 F-06 缺面）——判据 §5 强制的死矿登记无专册。建议内收进 `trial_ledger_registry.yaml` 增 dead_mines[]（骨架作业簿 05 同案，零新册）。
3. 建议：viability_verdict 回填自动化——生成器已能从 verdict 报告反扫（F-07 即是其副产物），增加"扫到 verdict=RED 即回填 refuted"的确定性腿（禁猜、只认报告 frontmatter verdict 字段）。
