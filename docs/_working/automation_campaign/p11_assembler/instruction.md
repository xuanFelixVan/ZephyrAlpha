---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑪整装回测席·恒定指令
---

【恒定指令·整装回测席】(真源=sop/automation_sop/research_production_line_policy.md §3⑪)
目标: 每夜一次整装回测,晨报直答两问——现在这套能不能赚钱?下浮率多少?
输入: config/strategy_production_map.yaml(装配状态册); verified晋级件(exam_scores/registry); backtest_system_sop四卷
输出: 整装成绩台账(本目录ledger.md); 问题清单(环节/数据/结构)转⑨归因; 晨报整装结论段
流程: 1冷启动三步 2读装配状态(在产模块/challenger待入) 3触发或核对整装回测runner(backtest sop_a四窗口径,真实成本+护栏) 4出分判读(通过判据/下浮率/对比昨夜) 5成绩台账 6问题清单分类转⑨ 7晨报附结论 8自检两轮
保底: 每晚1次(21:30,收盘数据落库后/23:00夜挖前);晨报必含赚钱+下浮率直答;问题清单100%分流
铁律: 新施工模块必须先经环节考试verified才准进装配;fail不藏;整装口径=考试口径
