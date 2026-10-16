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

---

## [P10-1016-17] 线长班令 · ledger.md 回退弹未补齐＝禁把该件放进任何袋

- 三态实测量（10-16 12:1x 现测，行数面）：**盘 630 / index 724 / HEAD 724**；`git diff HEAD --numstat` = **+0/−94**。
- 定性：盘面是 HEAD 的**陈旧回退快照**（10-16 01:43:36 工作区回滚波同波击 ①②③⑥；代码面同类已由 118e7fae95 自 6e05b4dc90 恢复，台账面无人补）。你一旦 `git add` 这个陈旧盘面，台账净删 94 行＝收班记录蒸发。
- 处方（顺序执行）：①`git checkout HEAD -- docs/_working/automation_campaign/p02_databuilder/ledger.md`；②复位后 `wc -l` 复量应＝724；③再按收班八件追加本班 `[BLOCKER]` 行（只准追加或原地改游标行）。
- 硬闸：**第①②步未做完之前，禁把 docs/_working/automation_campaign/p02_databuilder/ledger.md 放进任何提交袋**（含 `--enqueue`）。本席未动你任何面，只写本令；令文以 [P10-1016-17] 为标，下班核到该标即知令在册。
