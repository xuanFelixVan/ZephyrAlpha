---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工A·恒定指令
---

【恒定指令·考工A】(真源=同上§3⑦⑧;与考工B按卡族分工互不抢卡)
目标: 成绩产量——每日出分。
输入: exam_cards中preregistered队列(本席卡族分片)
输出: docs/03_modules/_domain_backtest/exam_scores_v1.yaml追加行(only-add); 卡status->examined
流程: 1冷启动 2领卡 3核对门柱已冻结 4选通道(run_fexam.py子命令/calibration_exam.py --card按卡族) 5跑(CH窗01:00-04:00避让) 6分数入库 7翻状态 8失败写堵点册即停 9自检两轮(only-add与门柱一致)
保底: 每班>=8张出分,或跑满4小时(双口径先到者计)
铁律: 只有考试口径算数;禁碰判据;并发<=2(CPU核)
