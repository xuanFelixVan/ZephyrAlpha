---
ttl: task_bound
---

# 环节2：Serializer 租约层（serializer.lease）全语义挖矿

> 挖矿：子代理 2026-09-22 凌晨，全程只读；主会话裁定融合。文件别名：**CQ**=scripts/commit_queue.py｜**GW**=src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py｜**DAEMON**=src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py｜**LANDING**=scripts/governance/commit_queue_landing.py｜**GCD**=scripts/git_commit.py。

## A 职责与输入输出

- **职责**：`.runtime/commit_queue/serializer.lease` 是提交队列的**单写者租约**（66号§8 v0.4.0 算法 + F9 活体语义）。谁持租约谁独占 drain 主循环（取项→landing→done/dead），保证同一时刻全仓至多一个 Serializer 在操作专用 worktree 与 dev ref。
- **输入**：`drain_queue()` 的一次调用（自举式，无常驻轮询）；租约文件本体 `{pid, acquired_at[, renewed_at]}`。
- **输出**：批次 stats；租约文件创建（O_EXCL）/续写（os.replace）/删除（os.remove）。
- **与网关锁的关系=两把锁，非一把**（CQ:168「独立文件锁，不共用网关 _GlobalCommitLock」）：

| | SerializerLease（租约） | _GlobalCommitLock（网关锁） |
|---|---|---|
| 文件 | `.runtime/commit_queue/serializer.lease` | `<主仓根>/.ailocks/git_commit_global.lock`（GW:473） |
| 作用域 | **整批 drain**（分钟~小时级） | **单次 commit 临界区**（秒~分钟级） |
| TTL/超时 | TTL=300s / 等待 5s（CQ:169-170） | TTL=1800s / 等待 60s（GW:218-219） |
| 活体保护 | **超 TTL 且持 PID 活=绝不抢**（CQ:792-797，F9） | **超 TTL 直接 os.remove 不判活**（GW:519-529，无 is_pid_alive 分支——同族缺陷未回移，潜伏不对称） |
| 心跳 | renew() 逐项续租（CQ:819-868） | 无 |
| 嵌套关系 | 外层：drain 全程持有（CQ:1119） | 内层：每项 landing 两进两出（GW:2446 + LANDING:599-605 CAS 推进 dev） |

- **持锁次序恒定**：lease ⊃ 全局锁，无反向嵌套。直连路径（git_commit.py 非 --enqueue）只碰全局锁、不碰租约。
- 第三把相关锁：daemon 单例锁 `belt_daemon.lock`（DAEMON:84-95，PID+ts+600s TTL+僵尸检测），与租约正交。

## B 代码地图

- CQ:168-171 常量；CQ:275 LeaseUnavailable；CQ:715-868 SerializerLease 类
  - 746-757 O_EXCL 原子创建写 `{pid, acquired_at}`；758-807 争用三分支：764-772 僵尸 PID 立即回收；773-797 超 TTL（774-781 无 PID→回收；782-797 持 PID 活→绝不抢）；798-804 JSON 损坏→清理重试；805-807 有界等待；808 超时抛 LeaseUnavailable
  - 810-817 `__exit__` os.remove；819-868 `renew()`（pid 归属校验→tmp+fsync+os.replace 原子写三键；fail-open 返 False）
- CQ:1080-1234 `drain_queue`：**1119 全仓唯一获取点**；1120 孤儿回收；**1132 循环体首行 `lease.renew()`（返回值被忽略）**；1228-1233 死信告警
- CQ:1237-1274 `try_bootstrap_drain`；CQ:1456-1490 `queue_status`（**不读租约**）
- CLI 自举四处：CQ:1733（enqueue 后）/1743（status 先试排空）/1826（requeue 后）/1785-1788（显式 drain）；GCD:865-867（--enqueue 入袋后自举）；DAEMON:100-110 `_drain_once`→LANDING:1064-1075
- GW:449-558 `_GlobalCommitLock`；GW:2446 commit 临界区；GW:3843 `_commit_auto`（flag 默认 OFF 休眠，GW:3756 改道口）
- DAEMON:332-344 `_serializer_lease_held`（读租约判 pid 活）；DAEMON:377-380 纪元安全点先查租约；DAEMON:418-419 watchdog 只观察 pending/+dead/（**不含租约文件**）

## C 六向台账

**① 上游（六条获取路径，唯一获取点 CQ:1119）**：CLI drain（CQ:1785）/enqueue 自举（1733，--no-bootstrap 可跳）/status 先试排空（1743）/requeue 自举（1826）/git_commit.py --enqueue（GCD:865-867）/belt_daemon 事件驱动（DAEMON:429/453）。休眠：gateway `_commit_auto` 改道（LANDING:1157，flag OFF）。

**② 下游**：drain 批循环每项 landing（LANDING:801）→ 专用 worktree 物化 → gateway.commit 全门禁链（LANDING:873/915→GW:2446）→ CAS update-ref dev（LANDING:599-605）→ 主工作区受限收敛。租约独占对象=serializer worktree 文件系统+dev ref 推进次序；网关锁独占对象=主仓 index/暂存区/commit 临界区。

**③ 机制对标**：O_EXCL+TTL+僵尸 PID 同族（66号§8「复用同款」）；F9 后语义分叉——租约=活体不可抢+心跳保鲜，网关锁=TTL 到期无条件回收（活体也会被 30min 到期抢掉——窗口短未爆，属潜伏不对称）。设计真源：66号§8；F9 治本=docs/_working/flash_speedup/F9_queue_newfile_deadletter/DESIGN.md（核心洞察「TTL 本意是防崩溃不是防慢」）；S18-R3 裁定=docs/_working/archive/2026-09/kimi_audit/adjudications/S18-R3_并发通道与锁粒度.md。

**④ 后端现状+测试覆盖**：tests/governance/test_commit_queue.py TestSerializerLease（514 起：活体占用→skipped 515/僵尸回收 529/超 TTL 活体不抢回归 538/无 PID TTL 回收 558/renew 保鲜 571/防易主 587/并发竞争 335）；test_commit_belt_daemon.py（单例锁 20-38/纪元三态 146-179）；test_ops_guard_red_team.py（租约删除白名单 519-535）；test_commit_queue_landing.py（多 drain 竞争 335）。**缺口**：无单项>TTL 期间并发 drain 全程让位的端到端长项测试；无 renew 与 __enter__ corrupt 分支竞争窗测试。

**⑤ 观测面**：queue_status 只报四目录计数不读租约——「pid 9344 磨 751s+、processing=0」排查困境的直接根因；renewed_at 生产零消费；堵点本只挂死信积压不挂租约持有时长。

**⑥ 状态数据**：字段三键 pid/acquired_at/renewed_at（首次 renew 才生第三键）。挖矿时刻实测：pid 20688 活、已持 624.6s（超 TTL 两倍余）、acquired==renewed（单项已磨 10 分钟未回头）、pending=3——**F9 后常态：大项在途、租约显示超期、活体分支挡住所有竞争者**。

## D 成本模型

持有方：获取 µs 级；续租每项一次毫秒级。真正成本=批墙钟（单项 landing 含 reconciler ~180s、注册表大批实测 624s/751s+），租约期=批总墙钟。竞争方：每次自举烧 5s 后放弃，无阻塞积累；但大项在途时后续项（含 interactive 车道）全部排队等整批磨完——车道优先只在批内起效，无项间公平。TTL 实际作用已空心化（活体不可抢使 TTL 仅对无 PID 租约有意义），与真实单项墙钟长期倒挂属设计使然。唤醒延迟：租约释放不产生事件，5s 放弃的自举后若无新入队，尾部项要等下一次任何人 enqueue/status。

## E 升级机会清单

1. 【快】**租约观测面入 status**：queue_status 增 `lease: {holder_pid, alive, acquired_age_s, renewed_age_s, over_ttl}`（读一个 100 字节文件）——排查从 ps+手读变 status 一眼可见。
2. 【快】**daemon 观察集加租约文件**：DAEMON:418-419 增对 serializer.lease 的 deleted/created 事件→poke——租约释放即唤醒，消灭「5s 放弃后干等下一入队」。注意 DAEMON:9 [MODIFY-GUARD] 观察目录集登记变更。
3. 【快】**drain 消费 renew() 返回值**：CQ:1132 返回 False=租约丢失/易主，应退回当前项并终止本轮——封死理论双写者窗。
4. 【快】**单项墙钟挂账**：超阈（>TTL）写 bottleneck_ledger.jsonl——大注册表批磨时从无声变有账。
5. 🌑 max-hold-duration 强抢：与 F9「活体绝不可抢」正面对撞（抢=毁 worktree=2026-09-17 死信事故重演），需 Owner 推翻 F9 才可做——不做。
6. 🌑 k=4 分区通道：channel_key_for_files（CQ:203）+热文件单通道闸已「闸在案」，主体通道池待 Owner 签 S18-R3——挂起排期，把大注册表批阻塞交互提交从时间域根治的终局解。

## F 挖矿日志表

| # | 动作 | 结论 |
|---|---|---|
| 1 | Grep SerializerLease 全仓 | 获取点唯一 CQ:1119；DAEMON 只读；ops_guard 白名单 |
| 2-6 | 精读租约类/网关锁/六入口/renew 调用点/字段读方 | 两把锁；GW TTL 不判活（不对称发现）；renew 返回值被忽略；status 不读租约 |
| 7 | 查 F9 文档+66号文+S18-R3 | 活体不抢真源链完整 |
| 8 | 测试扫描 | 覆盖清单成表，两缺口 |
| 9 | 实测租约+pid 判活 | F9 常态活证（624.6s） |
| 10 | 查计划任务/reaper keep | 无 drain 计划任务；keep.txt 含 commit_queue 防误杀两行 |

## G 自审闸三态裁定（主会话融合）

- **施工（本战役）**：E1 租约观测面（=R5 一部分）、E3 renew 返回值消费（防御加固）、E4 单项墙钟挂账、E2 daemon 观察租约文件（=R4 核心；MODIFY-GUARD 头注同步更新+测试）。
- **挂起排期**：E6 k=4 通道池（解锁条件=Owner 签 S18-R3；前置件已齐）。
- **封矿**：E5 活体抢占（终局不需要——预检+拆批把在途时长压下来即达目的；强抢复活事故面）。
