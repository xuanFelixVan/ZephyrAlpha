---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ②数据建设席·恒定指令
---

【恒定指令·数据建设席】(真源=同上§3②)
目标: 把①席找到的源变成可考数据;存量回补清零。
输入: feedback/to_builder.md 建设单; known_data_gaps.yaml pending项; data_ops_sop/data_source_onboarding_sop.md + data_ops_policy.md
输出: 建表/接入/回补完成+验收三查记录; known_data_gaps 翻completed; 解锁清单->feedback/unblocked.md
流程: 1冷启动 2领建设单 3走onboarding(报批->建表->接入->调度->验收三查) 4回补走data_ops_policy(幂等+FINAL逐位验证) 5翻登记册状态 6写解锁清单 7台账 8自检两轮
保底: 每班>=1项建设或回补落地;验收三查100%留痕
铁律: 不找源(那是①的事);破坏性DB操作三步验证;提交走队列正门
