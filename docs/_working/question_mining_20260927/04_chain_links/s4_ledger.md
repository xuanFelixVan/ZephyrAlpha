---
ttl: task_bound
title: S4 链路环节面挖矿台账（st-pqmine-20260927）
session: st-pqmine-20260927
date: 2026-09-27
status: 挖干待汇总
candidate_file: s4_candidates.yaml
candidate_count: 22
---

# S4 链路环节面挖矿台账

## 一、矿区与真源（六向之一：真源）

| 真源 | 用途 |
|------|------|
| docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md（122 环节/13 段/依赖 DAG/红叉位 7 处） | 环节清单与断链位唯一骨架 |
| docs/_working/fullflow_mining/00_skeleton/00_挖矿分工册.md | 12 深挖组边界（本题面避开他组主挖车道已收卷件，只出验收考题不重挖） |
| config/strategy_production_map.yaml（FAC-E0..E9） | B 段环节逐字段（algo_note/store_refs/build_status/module_ref） |
| docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md | E4 判据语义（prereg frozen/双口径/暂定档/负结果台账） |
| 模块实件：src/zephyr/data/cross_source_validator.py、scheduler.py、decision_map.py:100、regime/core/regime_detector.py、ex_core/price_cage.py、three_way_reconciliation.py、live_strategy_adapter.py、strategy_pipeline/promotion_advisory.py（缺位） | 接线锚点实测对象 |

## 二、环节覆盖（22 环节，三角度出题）

| 段 | 环节→题 | 主考角度 |
|----|---------|---------|
| A 数据供给 | F04→S4-001、F05→S4-002、F10→S4-003、F11→S4-004 | 三引擎接线/fail-open 判定、判重强制关口、订阅断链回补、交叉轴口径漂移 |
| B 策略工厂 | F13→S4-005、F14→S4-006、F17→S4-007、F21→S4-008、F23→S4-009、F25→S4-010 | 算力闸 fail-closed 演练、进货幂等、白名单刚性、否决留痕、prereg 冻结时序、台账只增 |
| C/H 缺位件 | F26→S4-011、F34→S4-014、F74→S4-022 | sim 流转留痕、汇聚绕行检测、转正门汇总器（insufficient 预注册式出题） |
| D/E/F 决策执行风控 | F27→S4-012、F28→S4-013、F38→S4-015、F47/F61→S4-016、F53→S4-017、F57→S4-018、F62→S4-019 | 空输入 fail-closed、FIELD-GAP 降级诚实、传感器 staleness、熔断拦截刚性、价格笼子、三方不平冻结、合规门注入 |
| G 回测/H 模拟盘 | F64/F66→S4-020、F72→S4-021 | 预注册冻结率 4.2% 实测、SimBridge 静默断链复检 |

红叉位覆盖：总册 §二 7 处中覆盖 6 处（F04/F26/F34/F62/F72/F74）；F20 事件接线、F82 order_daemon 归 SF/SC 深挖组主挖车道，本题面不重复立题（避撞纪律）。

## 三、去重记录

- 283 题主面=meta_question 治理面（PQ-0001..0103）+ 因子/信号 IC 面（PQ-0011..0127）+ 源线谱 U1-U6 面（PQ-0128..0283）——**链路环节接线/断供行为/产出独立验证三类考题在 283 题中成面积缺席**，本题面为首个链路环节验收题簇。
- 近邻题逐一避让：PQ-0020（tick 断档登记 vs S4-003 实时断链行为）、PQ-0044（screen 通过率 vs S4-010 只增语义）、PQ-0104/0107（space 台账/考尺快照 vs S4-009 冻结时序/S4-020 冻结率）、PQ-0090/0094（归因账/仓位上限 vs S4-012/013）、PQ-0046/0081 退役簇（波动状态因子 vs S4-015 运行时断供行为，对象不同非翻案）。
- 退役 30 题主题词扫描 0 命中。

## 四、三态自审（挖干/未干/受阻）

- A 段 4 题：挖干（F04/F05 零接线与旁路面有骨架+代码双锚；F11 三方数值已实锤）。
- B 段 6 题：挖干（工厂图 algo_note 声明值 vs 代码/台账实测的判据全部机解化；S4-009 预期 insufficient 是合法出口——载体缺失本身即结论）。
- C/H 缺位件 3 题：挖干（S4-011/S4-022 按缺位事实出题，S4-022 显式声明现状判 insufficient、建成后复考——预注册式考题）。
- D/E/F 段 7 题：挖干出题；其中 S4-016/017/018 需测试环境注入演练，判据已写死、执行归考试批。
- G/H 段 2 题：挖干（S4-020 的 5/120 冻结率+137/142 计数漂移均为本代理实测新证据）。
- **受阻项**：①PG 侧表（strategy_screen/hypothesis_precheck）未连库实测行级样本（reader 纪律），相关题判据以"经 DatabaseService 取数"前置；②F81 告警消费面、F45 强制清仓绕过、F40 负面否决断供三面已挖出题点但为控总量（25-35 上限）忍痛未入册，留待补挖波。

## 五、未挖尽面（移交后续波次）

1. 其余 100 环节的同构验收题（本题面已给三角度模板：契约/断供/独立验证，可流水复用）。
2. F81 告警阈值 38 条消费面普查；F45 强制清仓绕过授权链；F40 negative_veto 断供日 fail-open 风险。
3. F51 币圈骨架（TDM-C 空 壳）与 F121 三研究域——登记态深，待施工后出题更实。

## 六、净零声明

本波零新册零新 gate 零新脚本：22 题全部挂靠既有骨架册/工厂图/exam_policy/模块实件；产出文件为本战役宪章既定作业位。对 fullflow 挖矿分工册的避撞纪律（引用不重挖）已逐组核对。
