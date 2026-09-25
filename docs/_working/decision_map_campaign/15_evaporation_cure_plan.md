---
ttl: task_bound
title: 15 蒸发案治本施工方案（EV-01~06）
doc_type: plan
---

# 15 · 蒸发案治本施工方案（依据=10 号文取证报告，Owner 批后开工）

## 案情一句话

四例主区蒸发（untracked 全灭+index 567→9，reset--hard+clean-fd 静默通道）头号嫌疑人锁定：**提交队列落地器的 worktree 同步动作经 worktree .git 链接缺失/竞态"打穿"主仓**（置信度 ~65%，复合解释 ~80%）；代码三处自认前科（commit_queue_landing.py:949 / commit_queue.py:850,889,1220），凌晨 03:47 四落地 worktree 300ms 同步爆发=第一现场；reflog 零 reset 记录排除计划任务定时犯。

## 治本施工项（EV-01~06）

| # | 施工项 | 落点 | 验收 |
|---|---|---|---|
| EV-01 | **主仓快照黑匣子**：5 分钟级记录 index tree hash+untracked 计数+stash 列表+reflog 尾巴到 .runtime/evaporation_blackbox/（追加式 JSONL） | 新脚本+注册 schtasks 5min（防御性快照非 reconciler，不违 §9.3） | 蒸发再发时可从黑匣子恢复+精确定位分钟级现场 |
| EV-02 | **_git_wt 改执行后验证**：check-then-act（TOCTOU）改执行后复核 worktree .git 链接存在性+主仓 untracked 计数快照比对，不一致即中止+告警 | commit_queue.py:850,889,1220 / commit_queue_landing.py:949 | 缩比实验：复现穿透场景→守卫拦截 |
| EV-03 | **landing 守恒断言**：落地前后 `git diff --cached` 快照比对（align_dirty D12 处方落地生效） | commit_queue_landing 落地事务 | 断言不成立=落地中止+报警，禁静默 |
| EV-04 | **worktree .git 链接守卫**：GATE-ROOT-TEMP-SWEEP 扫描面排除 worktree .git 指针+serializer 启动自检四 worktree 链接完整性 | temp-sweep gate+serializer bootstrap | sweep 干跑零误扫+自检红灯可测 |
| EV-05 | **_pre_merge_auto_clean 场景2 修**：物理删除 untracked 改"暂存保全（staging 母本）"，merge abort 后回搬 | session_worktree.py:5283 | 复现实验：abort 后 untracked 完整回搬 |
| EV-06 | **drift watchdog A1 死会话清扫复核**：`git reset HEAD`（卸 staged）与后续 clean 的配合改"只卸 index 不喂 clean"或改回收站模式 | drift watchdog 清扫路径 | 死会话清扫后文件可在回收站找到 |

## 排期与依赖

- **全部等 Owner 治本施工令**（07 号文 C 栏已登记）——建议与"六段分叉修复"同批批（都是小手术族）。
- EV-01 可先行（纯增量、零风险、即刻止损定位能力）；EV-02/03/04 动落地器热路径，须配合并窗口+红蓝（landing 缩比实验）；EV-05/06 独立小改。
- 验收总判据：治本上线后连续 7 天零新蒸发案+黑匣子至少一次成功定位演练。

## 附：为什么这是"举一反三"的样板

469 vs 800+（宇宙不完整）与蒸发案（机制静默吞件）同属"**没有机械账本，问题靠 Owner 灵魂拷问才暴露**"。治本双管齐下：数据面=12 号文宇宙普查制度化；代码面=本方案黑匣子+守恒断言把"静默"变"有声"。
