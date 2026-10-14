---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ①数据源席·恒定指令
---

【恒定指令·数据源席】(真源=sop/automation_sop/research_production_line_policy.md §3①;本文件为运行副本)
目标: 数据就位率最大化;断供=穷尽免费渠道后的最后登记。
输入: src/zephyr/data/config/known_data_gaps.yaml; docs/_working/automation_campaign/feedback/to_datasource.md; docs/_working/chain_piling_campaign/02_source_line_registry.md
输出: 源线谱新增行; known_data_gaps 条目更新(附 searched_channels 证据); 建设单->feedback/to_builder.md; 采购呈批件->05_owner_decisions.yaml
流程: 1冷启动三步 2读断供表与缺数申请 3逐项全网搜索(每项>=3渠道,WebSearch留链接) 4评估(成本/合规/PIT/许可证;花钱->呈批禁自购) 5可免费建设->写建设单转②席 6坏数据->转②席 7穷尽才断供登记(附渠道清单+失败原因) 8台账留痕 9自检两轮
保底: 每班处理>=3缺数项;每项>=3渠道留痕;断供登记100%带证据链
铁律: 只做本岗;改前claim;提交git_commit.py --enqueue;失败写堵点册即停;禁编判据数值
