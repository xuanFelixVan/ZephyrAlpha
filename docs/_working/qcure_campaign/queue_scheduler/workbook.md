---
ttl: task_bound
title: QCure作业簿·queue_scheduler
session: st-qcure-20260925
---
# queue_scheduler 作业簿

## 1 环节定义与边界
队列与调度环节 = commit_queue.py 的租约（SerializerLease）与认领排序层（_pick_head/车道/级联标记），加上 k=4 池的认领与心跳（landing 侧 drain_queue_pool/_pool_claim_item/_pool_heartbeat_loop）。边界：不含 CAS 推进与门禁内容判（→cas_converge/gate_chain），不含入队轻检与预检（→producer_enqueue）。

## 2 六向台账

### ①上游输入
- pending/q-*.json（O_EXCL 原子创建，`enqueue_item` CQ:643-780；schema 见 CQ:39-48）；队列根解析序 显式>env>`_REPO_ROOT/.runtime/commit_queue`（CQ:365-387，pytest 禁回退生产根 CQ:381-386）。
- 三条生产入口：CLI `_cmd_enqueue`（CQ:2164）、交互正门 `git_commit.py --enqueue`（flag `commit_queue_interactive` 出厂 OFF，git_commit.py:831-833）、machine 车道 `reroute_auto_commit_to_queue`（LAND:2607，gateway 调用点 git_commit_gateway.py:3886）。后两条已查无额外排序元数据注入（仅 meta.lane/rerouted_from，CQ:1108-1120）。
- 排序判据输入：项内 `created_at`/`meta.lane`/`meta.depends_on`/`meta.stale`。

### ②下游消费
- 认领产物（pending→processing 原子 rename）交 landing：legacy `drain_queue`（CQ:1172-1339）或池 `_pool_process_item`（LAND:2365-2441）；k 分流在 `bootstrap_drain_with_landing`（LAND:2533-2573，thresholds `commit_queue_landing_pool_workers`）。
- 观测消费：`queue_status`/`_head_snapshot`/`_pending_position_map` 复用 _pick_head 同判据（CQ:1654-1741）——改 _pick_head 语义会连带改变位次呈现。

### ③机制现状（现行实现+业界参照）
- lease：O_EXCL 创建 + TTL 300s + 僵尸 PID 即时回收 + 活体不抢（CQ:779-872；"活体超 TTL 判慢项在途绝不抢"的病根记录 CQ:846-861——09-17 双 drain 同跑 worktree、clean -fd 删 untracked 致 11 笔 pathspec 死信）。legacy drain 逐项 `lease.renew()` 心跳（CQ:1224）；k=4 池改单心跳线程 60s 间隔（LAND:2140-2151，"四倍心跳病"）。renew 前校验 pid 防 clobber 新持有者（CQ:906-913）；renew False → 本轮立即终止（CQ:1224-1229）。
- k=4 池：整池一把 lease（LAND:2243）；每波 k 工线程独立 worktree/分支认领（LAND:2282-2362）；认领互斥点=原子 rename + done 同名幽灵弃置 + 8 轮有界重扫（LAND:2153-2198）；同路径项进门禁段前按全局序取进程内路径锁（LAND:2104-2137，超时 600s 归环境失败退 pending）；工线程禁早退（D3：err_streak 20 次才收工，LAND:2306-2348——09-24 三路工熄火 9h 实证）。
- 车道：interactive 优先 / machine 让路 / machine 最老件 30min 防饿死提前放行（`_pick_head` CQ:1123-1169，`_MACHINE_LANE_STARVATION_SEC` CQ:1102）；排序键从 qid 字典序改 created_at 先来先服务（56% 倒挂实证，CQ:1130-1136）；扫描界 `_HEAD_SCAN_BOUND=400`（CQ:1103-1105）。
- 级联：`_mark_cascade_stale`（CQ:1025-1074，depends_on 命中或同 base_head；D4 幽灵写回防御 CQ:1057-1070）→ 队首重验 `_revalidate_stale_base`（CQ:1077-1099，base_blob vs head_reader，fail-closed 降死信）。
- 业界参照：GitHub merge queue=临时 grouped 分支投机验证、base 移动则对新 tip 重验（https://docs.github.com ；https://news.ycombinator.com "optimistic locking" 类比）；GitLab merge train=逐车叠放、整列联合验证、stalled 即 rebase（https://docs.gitlab.com ）；bors=批量 merge commit、优先级不混批（https://bors.tech ）。对照：本系统 k=4 池≈merge queue 的投机验证+串行落地；cascade stale 重验≈merge queue 的"base moved 重验"；缺 bors 式显式优先级/batch 与 train 式叠放序。

### ④代码面（实现/测试/调用方全集）
- 实现：CQ（lease/车道/级联/drain/requeue/cleanup/status/health/alert，2437 行）；LAND 池段（LAND:2042-2530）。
- 测试：tests/governance/test_commit_queue.py(66 test)/test_commit_queue_base_head.py/test_commit_queue_ghost_pending.py/test_commit_queue_integration.py/test_commit_queue_pool.py(15)/test_commit_queue_landing.py(70)/test_commit_queue_landing_nightfix.py。
- 调用方：daemon `run_daemon`→`_drain_once`→`bootstrap_drain_with_landing`（DAEMON:112-125,830）；git_commit.py --enqueue→bootstrap（git_commit.py:930-932）；requeue CLI（CQ:1425/2285）。

### ⑤运维/呈现面（心跳/堵点本/phase stats/监控自动化）
- daemon 心跳文件 `belt_daemon.heartbeat`（30s 线程续写 DAEMON:788-794）+ `--status` 输出 heartbeat_age_s/pool_workers（DAEMON:860-889）。实测：PID 23356 存活、lease 同 PID（池级心跳保鲜中）。
- 堵点本 `.runtime/audit/bottleneck_ledger.jsonl`（DAEMON:60）：dead_letter/landing_staleness（pending 龄>1800s 记账，DAEMON:78,433-465）/registry_drift/serializer_env_abort_loop 升级（DAEMON:598-625）。
- 工出口装表 `pool_wave.log`（LAND:865-879，"必须落文件因 daemon logger 无 handler"）；单项分段账 `<worktree>/.runtime/audit/landing_phase_stats.jsonl`（LAND:794,832-862，A2/A3 装表 st-commitspeed-tbl）。
- 死信积压/爆发告警：`emit_dead_backlog_alert`+`check_dead_burst`（CQ:1865,2081，drain 收尾 lease 外 fail-open CQ:1329-1338）。

### ⑥失败态与数据面（死信/退pending路径全集+当前队列数据）
- 退 pending：环境失败 LandingEnvironmentError（CQ:1285-1297 / LAND:2411-2423，置共享终止旗）；路径锁超时（LAND:2119）；读项失败放回（CQ:1254-1261 / LAND:2377-2386）；孤儿回收（CQ:992-1017，波首 LAND:2291）。
- 死信：cascade_stale 基底重验不适用（CQ:1275-1281，不消耗 landing）；landing 物品失败（CQ:1312-1320 + task_board 打标 CQ:940-972）。
- 实测（2026-09-25 01:2x）：pending=47（全 interactive、20 笔 stale 标记、0 笔带 depends_on、最老 09-24 23:44）、processing=1（q-…-st-wm1-wave0-…-0011）、done=910、dead=397、blobs=19955；近期死因 TOP：NOTHING_TO_COMMIT 快照未真应用 29、GATE-PRECOMMIT-RUN 22、TRANSLATION 17、CREATE-GUARD 15、cascade_stale 7。

## 3 缺陷与矿脉清单
已知→QCure 映射：enqueue 零预检（方案 §1.3#1，M1 挂 CLI 层）；depends_on 弱约束（方案 §1.3#5，M3.4 token 先行袋）。
新矿脉：
1. **【正确性·重放不重跑门禁评估】** pool CAS 重放只重建树不重跑门禁（LAND:1893-1897,1998-2023）：首过门禁的是"base_dev+ours 合并"内容，重放产物是"new_dev+再合并注册表"——再合并结果（含他会话条目）未经 GATE-21/派生计数等整册门禁。正确性缺口已由 65c2285a46 的 `_heal_derived_totals` 补了计数标量一角，但非计数类整册判据仍裸奔；低频（仅同册竞态）但真实。
2. **毒药队首残留**：环境失败退 pending 保留原 created_at，先来先服务下仍居队首（`_pick_head` docstring 自认 CQ:1136-1137，B5 attempts+退避未施工）；47 笔 pending 最老已 1.5h+，与 landing_staleness 记账阈 1800s 同量级。
3. **_pick_head 每次认领全量重读重排**：池路径每工每轮 `_pick_head`（≤400 项×读文件）×8 轮重扫（LAND:2161-2165），47 项无感，队深回 83 项级别时是 CPU/IO 放大点（无缓存）。
4. **车道判定可被历史项误判**：`meta.interactive=="true"`→interactive 的兼容分支（CQ:1111-1112）使旧项永久占 interactive 快道；machine 饿死兜底只看最老 machine 件（CQ:1163），多 machine 深队列时其余件无梯度。
5. **孤儿回收与 ghost 防线已三处打补丁**（CQ:1002-1008、LAND:2168-2196、CQ:1057-1070）：根因是"pending 项 JSON 可被 lease 外写手回写"（_mark_cascade_stale 原地写回），矿脉=把 stale 标记改写旁路文件（sidecar）或入 DB，pending 项变 append-only 可消掉整族幽灵防御。

## 4 自审闸三态裁定
**挂起排期**——调度面无新增死因族主病灶（矿脉 1 归 cas_converge 门禁口径、矿脉 3/5 是性能/卫生件），应让位 M1/M2 同源预检先落地；depends_on 升级（见 §5）与 B5 退避排 QCure 二期。

## 5 长尾清单
- depends_on 强制前置升级路径（M3.4 二期）：勿改 `_pick_head` 本体（被 `_head_snapshot`/`_pending_position_map`/`_pool_claim_item` 三处共享，改判据会污染位次呈现）；在 drain 认领点（CQ:1238 后与 LAND:2165 后）加共享过滤 `_deps_satisfied(item,root)`：依赖 qid ∈ pending/processing→跳过取次选；∈ dead/→当场受控死信（reason=depends_dead，勿无限阻塞）；∈ done/→放行。需配套：requeue 换新 qid 后旧 depends_on 引用失效的改写规则 + `_HEAD_SCAN_BOUND` 内跳过件的可见性（status 显示 blocked_by）。
- 路径锁 `_PATH_LOCKS` 进程内 dict 无淘汰（LAND:2105），长驻 daemon 语义下按路径累积（threading.Lock 极小，卫生件）。
- machine 车道 30min 防饿死判据用"最老 machine 件"单点，可升级为按件计龄。
- `_HEAD_SCAN_BOUND=400` 超界项永久不可见（CQ:1103 注释自认 7 倍余量），队深破 400 需告警。
