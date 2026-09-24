---
ttl: task_bound
title: QCure作业簿·producer_enqueue
session: st-qcure-20260925
---
# producer_enqueue 作业簿

## 1 环节定义与边界
生产线/入队 = 队列项从各生产入口到 `enqueue_item` 落袋（blob+pending JSON 原子落盘）为止的全部代码路径。边界内：三条裸入口（裸 CLI/machine 车道/requeue）、交互正门 `git_commit.py --enqueue`（含锁忙/锁超时两处自动改道）、入队轻检与入队侧预检挂点。边界外：drain/landing 落地执行（M2/M3 消费侧）、daemon 排空调度。本环节是 M1 施工面。

## 2 六向台账
### ①上游输入（触发源全集）
- 入口A 裸 CLI：`_cmd_enqueue` scripts/commit_queue.py:2164（下称 CQ），参数面 CQ:2371-2389：`--session/--files/--files-file/--message/--message-file/--worktree-root/--base-head/--depends-on/--queue-root/--no-bootstrap`；基底自取 CQ:2193-2203（`resolve_base_head/resolve_base_blobs`）。
- 入口B machine 车道：`reroute_auto_commit_to_queue` scripts/governance/commit_queue_landing.py:2607（下称 LAND），由 `GitCommitGateway._reroute_commit_auto_to_queue` GW:3870-3886 调，触发源=`_commit_auto` GW:3906-3915 且 flag `commit_queue_serializer`（GW:316/325，config/flags.yaml:90）；保护路径剔除 LAND:2636（`split_auto_commit_snapshot` LAND:2577）；meta `lane=machine` LAND:2664-2667。
- 入口C requeue：`requeue_dead_item` CQ:1425，CLI `_cmd_requeue` CQ:2285；`--from-bag` 走原袋 sha256 自校验 CQ:1486-1499；`meta.requeued_from` CQ:1526。
- 入口D 交互正门：`_enqueue_mode` scripts/git_commit.py:818（下称 GC），flag `commit_queue_interactive`（GC:831，flags.yaml:110）；GC:847-855 有 18 白名单预检 + `extra_skip={"CLAIM-REQUIRED"}`（GC:852）+ exit 8。隐性入口 E/F：锁忙探针自动改道 GC:1240-1257 与 LOCK_TIMEOUT 自动改道 GC:1307-1323 均汇入 `_enqueue_mode`（预检同覆盖）。
### ②下游消费
`enqueue_item` CQ:643-770 产出 pending JSON+blobs → `try_bootstrap_drain` CQ:1342（CLI 后自举，CQ:2216-2221/GC:928-934/LAND:2670）→ `drain_queue`/`drain_queue_pool`（LAND:2201）→ `WorktreeLanding.__call__` LAND:1666；回执=打印 qid（CQ:2215/GC:935-939）或 `CommitResult(OK,"QUEUED:{qid}")` LAND:2679-2683。task_board 联动只在死信侧（CQ:940）。
### ③机制现状+业界参照
现状：入队轻检 6 类（见④）；入队语义"快照入袋即完成"（CQ:8 头注）；`enqueue_item` API 层零 git 依赖在案不变量（CQ:620-625）。业界：GitHub merge queue 用临时分支预验证、失败自动重排/移出（https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue ）；GitLab merge train 串行流水线逐节验证（https://docs.gitlab.com/ee/ci/pipelines/merge_trains.html ）；bors 以 staging 分支先跑测试合者（https://bors.tech/ ）——三者共同点=**准入即验证**，QCure M1 即把验证从落地口前移到入队口，方向一致。pre-commit 框架在本地 commit 前跑 hook 快败（https://pre-commit.com/ ），其 check-merge-conflict 曾因"仅 merge 进行中才检"在 CI 形同虚设、后加 `--always`（https://github.com/pre-commit/pre-commit-hooks/issues/300 ）——对 M2.2 的启示：字节预扫必须无条件的扫描而非依赖状态触发。
### ④代码面（三重搜索）
- 实现：scripts/commit_queue.py（轻检 `_validate_session_id` CQ:434、`_validate_relpath` CQ:442（NUL/反斜杠/~/绝对/..//.git/密钥 CQ:296-299）、`_validate_message` CQ:469、`_validate_blob_size` CQ:476、空清单 CQ:675、重复路径 CQ:694/714、R2 大批硬顶 40 CQ:680-687 豁免 machine/逃生旗）；preflight 白名单 18 gate PF:107-149 + 内联 CREATE-GUARD/NO-BARE-SQL PF:299-304；`run_preflight` 锁外只读、异常降级放行 PF:477-481。
- 测试：tests/governance/test_commit_queue.py（1314 行/66 test，requeue 面 CQ:796-878）、test_commit_queue_landing.py（1851 行）、test_commit_queue_integration.py（913 行）、tests/governance/rule_bridge/test_commit_preflight.py（152 行）。**已查无**：_cmd_enqueue CLI 层无直测（66 test 全走 API 层）——M1 需补 CLI 层预检挂点红蓝例。
- 调用方全集：grep 全仓 `enqueue_item|reroute_auto_commit_to_queue|requeue_dead_item` 生产代码仅上述四入口（tests 直调 API 若干，不入生产面）。
### ⑤运维/呈现面
preflight 审计 `.runtime/audit/preflight_events.jsonl`（PF:397-408，实测 enqueue=2474/direct=1871 行）；堵点本 `.runtime/audit/bottleneck_ledger.jsonl`（8.6MB，slow_item CQ:1595+死信登记 daemon）；`queue_status/queue_health` CQ:1743/1807（lease/队首/位次快照 R5）；裸 CLI 输出 ENQUEUED/DENIED/DRAIN 三态（CQ:2213-2221）。堵点本中本环节痕迹：enqueue 面预检 blocked 事件 top=SESSION-REQUIRED 379、REGISTRY-MASS-DELETION 145、CREATE-GUARD 135、DIRECTORY-CONTRACT 62。
### ⑥失败态与数据面
异常全集：QueueReject→exit 2（CQ:13/CQ:2211）；RequeueError→exit 1（CQ:2313）；message/files-file 读败→exit 1（CQ:2170/2176/2287）；qid 1000 次碰撞 RuntimeError（CQ:764）；reroute 快照读盘失败→降级直提（LAND:2599-2601+GW:3911-3915）；预检网关构造失败→跳过预检（GC:841-845）；预检整体异常→degraded 放行（PF:477-481）。数据面：pending=46/processing=1/done=910/dead=397（2026-09-25 实测）；1353 项中无 base_head=1074（79% 存量）、meta.lane 有 824。

## 3 缺陷与矿脉清单
1. 【已知·M1.1/M1.2/M1.3】三裸入口零预检（CQ:2164/LAND:2607/CQ:1514），唯一有预检的是交互正门 GC:847-855——QCure M1 全覆盖。
2. 【新矿·假红面】enqueue 面预检 top1 拦截=SESSION-REQUIRED 379 次（preflight_events 实测）——裸 CLI/machine/requeue 入口的调用会话可能未在 SessionRegistry 注册，M1 直接全量接白名单会在三裸入口制造假红风暴。施工须逐入口定 skip 集（建议三裸入口首版 skip {SESSION-REQUIRED, CLAIM-REQUIRED}，与 GC:852 先例对齐并留审计）。
3. 【新矿·语义冲突】machine 车道预检拒绝后走 GW:3911 fail-safe 会**降级直提**——把注定死信的批改道回直提老路，违背 M1 初衷；应改为返回 CommitResult(FAILED, 预检处方) 且不走降级（方案 §M1.2 未覆盖此点，需裁定）。
4. 【新矿·顺手件】requeue 从不填 base_blobs（CQ:1521 调用 EnqueueOptions 只传 base_head）⇒ requeue 袋 base_blob 恒 null，级联重校验 CQ:1089-1091 对其结构空转、且注册表合并 LAND:1300-1307 fail-closed 死信面未闭合；M1.3 挂预检时顺手补 `resolve_base_blobs` 一行。
5. 【新矿·性能】preflight 实测样本 9.6s（30 文件 TABLE-NAME-REGISTRY，preflight_events 2026-09-24T17:19）——方案验收"单件 ≤5s P50"按当前白名单有超支风险，M1 施工前先跑一遍 P50/P90 实测定 skip 面。
6. 【M1 挂点建议·精确】入口A：CQ:2189 `_read_files_from_worktree` 之后、CQ:2204 `enqueue_item` 之前；签名 `_run_enqueue_preflight(gateway, files: list[str], session_id: str, message: str, extra_skip: frozenset[str]) -> int`（0 放行/2 拒绝，对齐 CQ:13 ERROR_CONTRACT 与 GC:775 同名先例）；gateway=GitCommitGateway(project_root=worktree_root)（worktree_root≠cwd，CQ:2165）；拒绝分支独立于 QueueReject catch（保留结构化处方 M3.3），拒绝点在 blob 落袋前=零垃圾 blob（_store_blob 在 enqueue_item 内 CQ:690-709）。并发约束：预检全程锁外不持 `_session_locks`（CQ:735）与 `_GlobalCommitLock`（PF:8 不变量），degraded 放行绝不堵队列（PF:477-481）。
7. 【已知·非本环节】`_commit_auto` 降级直提窗口=瞬态双写者（LAND docstring 80-86 已声明+assert_single_writer_dev_history LAND:2691 可点名）。

## 4 自审闸三态裁定
施工——四个入口挂点全部实锚（CQ:2189/LAND:2636 后/CQ:1510 前/GC 已有），现成 `run_preflight` 零新检测器；但第 2/3 条矿（SESSION-REQUIRED 假红面、machine 拒绝语义）必须进 M1 施工清单，否则上线即假红风暴或改道回直提老路。

## 5 长尾清单
- _cmd_enqueue CLI 层零直测（④归因），M1 需补 2×2 红蓝例（带/不带预检 × blocking/degraded）。
- 裸 CLI 不传 meta.lane（依赖 _item_lane 缺省 interactive CQ:1108-1120）——machine/interactive 判定三通道（lane 显式/rerouted_from/缺省）的长尾一致性未挖。
- preflight 各 gate 单独耗时剖面未拆（只有总 ms 字段）——5s 预算超支时需 per-gate 计时装表。
- GC:1240-1257 锁忙探针只读 `.ailocks/git_commit_global.lock`（GC:611-631），探针误判"不忙"面未挖。
- 预检事件 jsonl 与死信 dead_reason 的对消统计口径（方案 §4.2）未实做——留验收阶段。
