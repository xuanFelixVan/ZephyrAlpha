---
ttl: task_bound
---

# 环节8：直连/前台提交路径与会话-claim-心跳体系

> 挖矿：主会话合成（子代理限流阵亡；核心机制由环节2/3 子代理实证补齐）。

## A 交互模型真相表（本战役最重要的一张表）

| 场景 | serializer.lease | _GlobalCommitLock | 队列视角 |
|------|-----------------|-------------------|---------|
| git_commit.py 直连（非 --enqueue） | **不碰** | 拿（commit 临界区，TTL1800s 不判活） | 队列全程无感 |
| git_commit.py --enqueue | 入袋后**同进程内联自举 drain**（GCD:865-867→CQ:1733）拿租约 sweep | 每项 landing 内两进两出 | 本会话项+排空全部队首项 |
| belt daemon | 借道 bootstrap 拿租约 | 同上 | 补位消费者 |
| 等待方 status | 只读四目录 | 不碰 | **不读租约=误报健康** |

- **09-21「9344=ulib 直连提交持租约」系误读**：持有租约的只可能是 drain_queue——9344 实为 ulib 会话 `git_commit.py --enqueue` 进程的内联自举 sweep 在磨大注册表批（队列项），cmdline 长得像直连而已。同理 09-22 03:27 dloop 前台进程持租约+ulib2 项在 processing=dloop 入队后内联 drain 先吃队首（FIFO）。
- **直连大提交不占租约但占网关锁**：租约语义外仍有第二把锁（1800s TTL 到期不判活，环节2 发现的不对称缺陷）。
- 内联自举的副作用：入队进程同步扛全队列 sweep（环节3 成本模型），"入袋即返回"话术不成立（有界化=环节3 E4）。

## B 会话-claim-心跳三件套

- SessionRegistry（session_concurrency.py）：register(pid,...)/heartbeat/_is_session_alive=**PID+TTL 双判据**（register 不带真 pid 会被判死——本战役 03:35 踩坑实证）；活性窗过期→list_active 剔除；lock_files.py cleanup 做 salvage（死会话遗物回收）。
- 双 claim 系统：gateway 只认 SessionRegistry.claim_file；lock_files 另有一套（历史分叉，gateway 路径以 SessionRegistry 为准）。
- heartbeat_daemon.py：常驻 30s 心跳（本战役以 pid 绑定会话注册实战验证有效）。
- SESSION-REQUIRED gate：要求提交时 session 注册且活性新鲜——落地命令 MUST 心跳+提交同 shell（既定配方）。

## C 升级机会

1. 【快】status 读租约（环节7 C1）——本环节痛点的观测面治本。
2. 【快】daemon/直连/队列三类持锁者在 status 中标注类型（drain-active vs commit-critical）。
3. 🌑 直连路径并入队列统一记账：直连是大白名单正门（紧急通道），强行并入会伤逃生能力——封矿；改为 status 可见直连活跃度（锁文件 mtime）即够。
4. 🌑 双 claim 合一：历史债，动 claim 真源涉全链回归——挂起维护班。

## D 自审闸三态裁定

施工：C1+C2（并入 R5）。挂起：C4。封矿：C3。
