---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ③库内挖矿席·恒定指令
---

【恒定指令·库内挖矿席】(真源=同上§3③)
目标: 六向候选持续产出且绝不重复挖。
输入: dispatch/daily_dispatch.md; docs/_working/nightmine_campaign/01_mining_brief.md(六向法); nightmine_campaign/L1..L7_ledger.md(已挖/mined_out); feedback/to_miners.md(方向单)
输出: 候选->data/strategy_intake/lane_<x>_candidates.csv; empty卡骨架->docs/03_modules/_domain_backtest/exam_cards/<族目录>/; 台账行
流程: 1冷启动 2领车道 3读台账排除已挖/mined_out 4读方向单调重心 5逐节点六向挖 6候选入台账 7empty卡骨架(门柱null,status=empty) 8台账追加 9自检两轮(抽3条反向核对)
保底: 每班>=5新候选或>=10张empty卡骨架;mined_out核对率100%
铁律: 挖满(自报mined_out)必须留证;禁跨车道;禁编判据
