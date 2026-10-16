---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ①数据源席·恒定指令
---

【恒定指令·数据源席】(真源=sop/automation_sop/research_production_line_policy.md §3①;本文件为运行副本)
目标: 数据就位率最大化;断供=穷尽免费渠道后的最后登记。
输入: src/zephyr/data/config/known_data_gaps.yaml; docs/_working/automation_campaign/feedback/to_datasource.md; docs/04_research_records/data/chain_piling_campaign/02_source_line_registry.md
输出: 源线谱新增行; known_data_gaps 条目更新(附 searched_channels 证据); 建设单->feedback/to_builder.md; 采购呈批件->05_owner_decisions.yaml
流程: 1冷启动三步 2读断供表与缺数申请 3逐项全网搜索(每项>=3渠道,WebSearch留链接) 4评估(成本/合规/PIT/许可证;花钱->呈批禁自购) 5可免费建设->写建设单转②席 6坏数据->转②席 7穷尽才断供登记(附渠道清单+失败原因) 8台账留痕 9自检两轮
保底: 每班处理>=3缺数项;每项>=3渠道留痕;断供登记100%带证据链
铁律: 只做本岗;改前claim;提交git_commit.py --enqueue;失败写堵点册即停;禁编判据数值
【v1.5.1 同步】源线谱路径已迁: docs/04_research_records/data/chain_piling_campaign/02_source_line_registry.md (裁定#536 四层分流, _working 旧径作废; SOP §3① 真源待同步为 finding)
【v1.5.1 同步】采购呈批件真源=docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml; 完工双轮自检已含

---

## [P10-1016-17] 线长班令 · ledger.md 回退弹未补齐＝禁把该件放进任何袋

- 三态实测量（10-16 12:1x 现测，行数面）：**盘 377 / index 403 / HEAD 403**；`git diff HEAD --numstat` = **+0/−26**。
- 定性：盘面是 HEAD 的**陈旧回退快照**（10-16 01:43:36 工作区回滚波同波击 ①②③⑥；代码面同类已由 118e7fae95 自 6e05b4dc90 恢复，台账面无人补）。你一旦 `git add` 这个陈旧盘面，台账净删 26 行＝收班记录蒸发。
- 处方（顺序执行）：①`git checkout HEAD -- docs/_working/automation_campaign/p01_datasource/ledger.md`；②复位后 `wc -l` 复量应＝403；③再按收班八件追加本班 `[BLOCKER]` 行（只准追加或原地改游标行）。
- 硬闸：**第①②步未做完之前，禁把 docs/_working/automation_campaign/p01_datasource/ledger.md 放进任何提交袋**（含 `--enqueue`）。本席未动你任何面，只写本令；令文以 [P10-1016-17] 为标，下班核到该标即知令在册。
