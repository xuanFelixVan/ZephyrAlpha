---
ttl: task_bound
---
# SDSC-16 坏数据修复与回补器族（手动/留盘为主）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 4/8｜真源=config/data_supply_chain_map.yaml#DSC-16｜挖矿时点=2026-10-15（含当日只读复核）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：坏数据修复与回补器族（手动/留盘为主），node_type=stage，build_status=partial，verified_scope=structure。
- 职责一句话：修复纪律四条（污染判据先行/FINAL 逐位验证/勿物理删事实走 valid_to·fact_close/并发写表先 claim）+RULE-DATA-OPS 三步验证；判重正门（DSC-06）与修复配对方才闭环。事件回填通道死（DSC-14D 退役）→全部走一次性脚本。
- 决策问句（图原文）：发现的是缺口还是坏数据？修它有没有正门、正门在不在版本控制里？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 三条入边：DSC-14→16 control（补不回的转修复/转 accepted）+DSC-19→16 feedback（DETACH 隔离=修复段兜底）+差异/缺口台账（known_data_gaps.yaml 为输入锚） | config/data_supply_chain_map.yaml edges DSC-14→16/DSC-19→16；src/zephyr/data/config/known_data_gaps.yaml |
| 输出面 | 修复回灌后由采集段重产（DSC-16→01 feedback）+修复结论回写缺口台账（DSC-16→14 feedback）+修复后 OPTIMIZE 逐位验证（DSC-16→18）；缺口台账=规则真源 YAML（三渠道实证不可恢复→转 accepted） | config/data_supply_chain_map.yaml edges+feedback_loops DSC-16 三条；src/zephyr/data/config/known_data_gaps.yaml |
| SSOT 真源 | 修复纪律真源=data_ops_sop（政策 §3 回补器七件+修复两件）+known_data_gaps.yaml；语义层=图12 DSC-16；known_data_gaps.yaml 无册号（上户口缺口呈 f2z，trigger_facts 在册） | docs/01_policies_and_standards/sop/data_ops_sop/（政策 §3）；src/zephyr/data/config/known_data_gaps.yaml |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/c4_history_repair.py；执行体 repair_kline_degraded_pull.py+c4_history_repair.py 实存；本批 VCS 复核：repair_kline_degraded_pull.py 已 tracked（改善）、backfill_tick_depth5.py+backfill_stock_daily_basic.py 仍 UNTRACKED（仅在主区磁盘） | src/zephyr/data/c4_history_repair.py；scripts/data/repair_kline_degraded_pull.py；scripts/data/backfill_tick_depth5.py；scripts/data/backfill_stock_daily_basic.py（git ls-files 本批复核） |
| 门禁约束 | 修复纪律四条+RULE-DATA-OPS 三步验证（必要/真实/可逆）；accept_gap（源侧永久消失三渠道实证后转 accepted，勿留悬账）；manual_script 零隐式范围纪律（无门禁兜底 residual） | config/data_supply_chain_map.yaml#DSC-16 note_zh/fallback；AGENTS.md §1 RULE-DATA-OPS |
| 自动化触发 | wired_manual（人工门位期望≤1 禁判死）；事件回填语义全落本环节手动/留盘脚本（DSC-14D 退役后兜底） | config/data_supply_chain_map.yaml#DSC-16 wiring_status/trigger_facts |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 两条 control/feedback 边+缺口台账在册；上游巡检/对账产出连日（SDSC-13/20 交叉证） |
| 输出面 | warn | 修复三反馈边在册；但 known_data_gaps open/monitoring 未了账（在册）且修复动作无统一案卷目录（散落一次性脚本 stdout） |
| SSOT 真源 | warn | 政策 §3+台账 YAML 双真源在册；known_data_gaps.yaml 无册号（上户口缺口 f2z 在册未消） |
| 代码模块 | warn | 核心两件实存且一件已纳管（改善）；但政策点名七件中至少两件仍 UNTRACKED（backfill_tick_depth5/backfill_stock_daily_basic，本批 git ls-files 实证）——"未纳管即无 INVARIANTS/无 gate/无测试"风险原样在 |
| 门禁约束 | pass | 修复纪律四条+三步验证+FINAL 逐位在册且与 DSC-06 正门配对（判门缺陷已修，配对完整） |
| 自动化触发 | warn | manual=by design；事件通道退役后脚本兜底 residual（"人记得才补；血缘前推与 auto-retrain 断链"）未变 |

## 4. 缺口与建议

1. 【warn 收口】回补器 VCS 纳管：至少 backfill_tick_depth5.py/backfill_stock_daily_basic.py 两件应立即 git add 纳管（改数据行为不可审=在册原话）；其余政策点名件逐一盘点补齐。
2. 【warn 上户口】known_data_gaps.yaml 登记册号（入 ROOR 或 data 域注册表），消 f2z 状态。
3. 【warn 观察】修复案卷无统一落点：建议比照 data/failures 案卷族建 data/repairs/<gap_id>/*.json（修什么/判据/验证读数），让"修复过"翻得了账。
4. 【正向证据】判重正门修复（DSC-06② fail-visible）后，本环节"判门缺陷"前置障碍已消——修复与判重配对闭环的条件首次齐备。
