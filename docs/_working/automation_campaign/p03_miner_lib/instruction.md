---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ③库内挖矿席·恒定指令
---

【恒定指令·库内挖矿席】(真源=同上§3③)
目标: 六向候选持续产出且绝不重复挖。
输入: dispatch/daily_dispatch.md; docs/04_research_records/mining/ledgers/nightmine_20261010/01_mining_brief.md(六向法); 同目录00_lane_roster.yaml+L0d..L8b_ledger.md(已挖/mined_out); docs/_working/automation_campaign/pulse/mining_directions.md(十方向持久菜单); feedback/to_miners.md(方向单)
输出: 候选->data/strategy_intake/lane_<x>_candidates.csv; empty卡骨架->docs/03_modules/_domain_backtest/exam_cards/<族目录>/; 台账行
流程: 1冷启动 2领车道 3读台账排除已挖/mined_out 4读方向单调重心 5逐节点六向挖 6候选入台账 7empty卡骨架(门柱null,status=empty) 8台账追加 9自检两轮(抽3条反向核对)
保底: 每班>=5新候选或>=10张empty卡骨架;mined_out核对率100%
铁律: 挖满(自报mined_out)必须留证;禁跨车道;禁编判据
【v1.5.1 同步】十方向持久菜单=docs/_working/automation_campaign/pulse/mining_directions.md (按楼轮转/封矿即切, P0=盘口微结构族; 非一次性任务书); 楼图=pulse/coverage_map.md (先读楼图只进未封楼, 楼内查户级台账绝不全量扫描)
【v1.5.1 同步】输入路径已迁: brief/roster/八本台账=docs/04_research_records/mining/ledgers/nightmine_20261010/ (裁定#536; SOP v1.3.0 所引 _archive 路径实不存在, 记 finding); 产卡唯一出口=scripts/backtest/generate_exam_card_skeleton.py only-add 通道 (裸骨架不可考不产, 须具名子题卡)
【v1.5.1 同步】枯竭判定书->docs/04_research_records/mining/exhaustion/<YYYY>/ 逐节点一册 (裁定#536); 枯竭判据对齐 mining_sop v1.9.1 (六向全查+无长尾+挖后自审闸, 双噪音封矿); 挖矿不停, 唯一叫停权=Owner; 完工双轮自检已含
