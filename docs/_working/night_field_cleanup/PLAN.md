---
ttl: task_bound
---
# 夜战清滩作战书 NIGHT-FIELD-CLEANUP（09-29 布防；09-30 二次蒸发后三建，本次随 token 提交保命）

> 授权锚：Owner 09-29 凌晨令（全场只剩一个活 AI 时清滩对结果负责）+ 09-30 晨批四件（#ARCH-367 载体已登记：裁定#436/#437 落册+W12 翻面+RB2 追认）。
> 执行会话：st-nightclean-20260929。前两版作战书遭并线清扫两次蒸发，本版已入 git。

## 0. 唯一前置=全场无施工队。探测器（缺一不可）：
①队列 pending=0 且 processing=0；②最后提交龄≥2700s；③他会话心跳无 -mmin -45 命中；④status 计数与上次相等；⑤无 MERGE_HEAD。双确认（连续两轮全过+计数相等）才开工。

## 1. BUSY 锁
.runtime/tmp/night_field_cleanup/build.lock（json state/pid/ts）：<20min 退避 / 陈旧验 pid 死后接管 / 结束必删。

## 2. 价值三问 SOP（详见 COMMIT_CHECKLIST.md 三维度十八查）
安全（正门+token+翻译+claim）→不扰他（三 blob 判型 dev 胜/删除验退役/禁 reset --hard 等）→价值（cherry 吸收判定/独有 diff/V2 落 V1 宁留 V0 清）。

## 3. 施工总序
B1 staged 代投→B2 残影清 index→B3 untracked 三分→B4 派生收敛→B5 worktree/分支大扫除（RB4 lane-archive 命令已落 dev 可用）→B6 死信归档（**RB2 dead-archive 子命令已落 dev，裁定#436 已授权首跑**：`python scripts/commit_queue.py dead-archive --days 3 --execute`，须 belt 停窗）。

## 4. 复活封刀：他会话心跳/队列/提交出现=当前批完成即封刀。

## 5. 红线：实盘/资金/DDL/净删/flag 出厂/门禁自身/schtasks 零接触。

## 6. 冷启动：Python3.12 PATH→lock_files cleanup→reaper --status→claim→commit 正门。

## 7. 晨报：MORNING_REPORT.md 终版+台账 jsonl+收官自删自动化。

## 8. 战场注记（09-30 13:20）
- 重启一次：belt 自启（pid 8260）；在途袋全灭（管道断连）内容在工作树完好，本轮批量复活。
- 车队.day shift：c9 线已接手 F02/RB2 同类目标（dead-archive 子命令 c9 版已落 dev）。
- 队列二次重定基线：done=710/dead=718。
