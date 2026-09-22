---
ttl: task_bound
---

# 环节3：belt daemon 与排空触发拓扑

> 挖矿：子代理 2026-09-22 凌晨（含 03:37-03:45 实时进程/队列现场取证）；主会话裁定融合。

## A 职责与输入输出

- **定位**：提交传送带的**补位常驻消费者**。主消费者其实是"入队方内联自举"；daemon 只补"夜间/无人入队窗口"的残余消化——这个定位决定了它死后无人立刻察觉。
- **职责五件事**：① watchdog 事件驱动自举排空（M10 豁免留痕 L17）；② 新死信自动登记堵点本；③ 堵点积压阈值告警（R-06 冷却状态机）；④ 连续环境失败 ≥3 升级 CRITICAL；⑤ 门禁代码+判据真源纪元自检、安全点原地 re-exec（裁定#281①）。
- **输入**：pending/、dead/ 两目录文件事件（仅此两处）；`ZEPHYR_BELT_DAEMON_NO_REEXEC` 逃生旗。**输出**：drain 调用；堵点本 JSONL；冷却态；`os.execv` 换血。
- **明确不做**：不持 lease（永远借道 bootstrap）；不轮询；不自杀退出（无计划任务重拉，退出=掐断全仓排队落地）。

## B 代码地图

commit_belt_daemon.py（463 行）：52-66 常量（观察子目录集/锁名/防抖 0.5s/堵点阈 20 条 24h/冷却 1800s）；69-97 单例锁（PID+600s TTL+僵尸检测）；100-108 `_drain_once`；111-139 死信记账；142-243 积压自检+R-06 档位冷却；269-329 纪元（`src/zephyr/gov_enforcement` + `scripts/governance` 两子树 sha 合成）；332-381 lease 活体判定/re-exec；384-446 run_daemon 主循环（poke.wait(timeout=30) 超时=continue 零动作；事件→双 clear→drain→记账→自检→re-exec）；449-458 main 仅 --once/--status（**头注声称的 stop 未实现**）。

## C 六向台账（关键发现）

**① 上游触发**：启动=纯手动 CLI（16 个 register_*.ps1 零引用、schtasks 无任务）——**不是计划任务常驻**。实时取证：进程表无 belt_daemon、belt_daemon.lock 不存在、堵点本最后一条 2026-09-18T06:00:54Z——**daemon 至少自 09-18 14:00(+08) 起就没跑过**。"昨晚持续排空"靠三个内联触发器供血：enqueue 后自举（git_commit.py:867 / landing:1157 / commit_queue.py:1733）、**status 查询自带排空尝试**（:1743）、requeue 自举（:1826）。

**② 漏唤醒判定（修正版）**：watchdog 只观察 pending/+dead/（:418-419），serializer.lease 在队列根**不被观察**——代码成立。但"直连提交持租约"系误读：全仓仅 drain_queue（commit_queue.py:1119）持有租约，直连提交不走它；且 sweep 每轮重读 heads（:1134 在 while 内），会把持租约期间新入队的项一并吃掉。**真实漏唤醒窗=两处窄缝**：事件恰在最后一次 head-check 与 lease 释放之间落地；sweep 异常中断（BaseException 上抛，项滞留 processing 等下轮孤儿回收）。**更大的"无兜底"是 daemon 本体死亡**——队列延迟完全由他会话 enqueue/status 节奏决定，无上界。

**③ epoch 换血盲区**：两棵纪元子树字面量**不含 scripts/ 根**——改 commit_queue.py（SerializerLease/drain_queue 判据所在地）不触发守护换血，与 #ARCH-323 实证同构。

**④ 05:52→08:03 悬停复合归因（CONCERN 级结论）**：daemon 已死属实；但窗内 drain 仍持续在跑，**主放大器=qid 字典序饥饿**——FIFO 按 qid 字典序（:1134）=会话名字母序，st-workclean 在当日活跃会话中垫底，被 code-doc/data-fix/disk-ch/taskcards/ulib 持续供血系统性插队，直到 08:03 一轮 sweep 才轮到（08:03-08:05 死信爆发簇=同一 sweep）。

**⑤ lease_unavailable 静默**：daemon 对 LeaseUnavailable 的 skipped 结果零日志零计数（:430 只匹配 bootstrap_error）。

**⑥ 测试**：16 例（单例锁/记账/--once/积压阈值/冷却/连续失败升级/epoch 四态）；未覆盖：run_daemon 主循环本体、漏唤醒竞态、lease_unavailable 路径、main 参数解析（含幽灵 stop）。

## D 成本模型

空闲零 CPU（watchdog OS 事件通知）；每事件一次 full sweep；单项落地分钟级（活体实证 8min+）。**daemon 死亡的成本转嫁**：每个 enqueue 进程同步扛全队列 sweep（活体：入队进程持租约 8min+ 未返回），与"入袋即返回"话术相悖；队列延迟无上界（2h11m 实证）。

## E 升级机会清单

1. 【快】lease 事件纳入观察（R4）：补一条对 serializer.lease 的观察，删除即 poke——封堵漏唤醒窄缝，~10 行。
2. 【快】main() 补 --stop（头注声称有实际无；裸 stop 会在 ./stop/ 建目录）。
3. 【快】epoch 第三子树：把 scripts/commit_queue.py 纳入纪元合成——否则改判据后守护按旧码常驻。
4. 【快】enqueue 自举有界化：bootstrap 传 max_items=K（或 interactive 车道限界），入队进程不再同步扛全队列。
5. 【快】process_reaper_keep.txt 重复行清理。
6. 【快】守护失联可观测：status 探测 belt_daemon.lock 缺失→提示"补位消费者离线，排空纯靠内联自举"。
7. 🌑 跨车道字典序饥饿：治本=按 created_at 排序，动 :1134 判据真源需裁定登记——挂起（本战役先以拆批+预检压缩单项时长缓解）。
8. 🌑 daemon 生命周期立法：登录自启或周期 --once 兜底（与运行中 daemon 的 lease 让位语义兼容）——涉裁定#281/M10 边界，挂 Owner。
9. 🌑 pathspec 死信簇根因清账：workclean 快照含已消失路径的 git add 缺陷——维护班专人专事。

## F 挖矿日志表

全文精读/全仓 grep/进程表取证/队列现场/385 条死信 JSON 解析/堵点本 4172 行解析/触发点 5 处定位/测试 16 例清单/git log --follow 演化链（0121e3c→c372943→3d81a85 #281①→95f1832 #ARCH-323→a693936 R-06）。

## G 自审闸三态裁定（主会话融合）

- **施工（本战役）**：E1 lease 事件观察（R4）+E3 epoch 第三子树（改判据必须换血的闭环）+E6 守护失联可观测（并入 R5 status）+E4 有界化（max_items 常量默认保守值，需配测试）。
- **挂起**：E7 字典序饥饿（created_at 排序，涉 FIFO 判据变更需裁定）；E8 daemon 生命周期（Owner）。
- **封矿**：E2 --stop（修文档头注即可，无需求）；E9 pathspec 簇（非本环节，转维护班台账）。
