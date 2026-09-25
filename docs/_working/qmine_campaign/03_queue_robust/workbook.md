---
ttl: task_bound
title: QMine作业簿·queue_robust
session: st-qmine-20260925
---
# queue_robust 作业簿（三矿：depends_on 真排序锁 / requeue 计数洗白 / pending sidecar）

## 1 环节定义与边界
队列健壮性 = ①认领排序正确性（meta.depends_on 从"级联标记依据"升级为真排序约束）、②重试/重投计数生命周期（attempts/env_retry/snapshot_retry/requeue_count 跨袋存续）、③pending 袋不可变性（幽灵写手族根因治理）。边界：不含落地器为何判死与环境失败分流内部（→M5），不含门禁判据（→M1/M2），不含死信三分类与属主认领（→qcure deadletter 已挖）。基线：qcure queue_scheduler/workbook.md（其 §5 长尾即本班矿①蓝图）+ deadletter/workbook.md（33% 重投再死数据）。**勘误基线一处**：qcure 簿 §3.2 称"B5 attempts+退避未施工"——已过时，B5 全链已落地（CQ:201-203,1353-1404,1579-1594,1622-1623,2849-2852）。

## 2 六向台账
### ①上游输入
- depends_on 唯一生产口=CLI `--depends-on`（CQ:2661→EnqueueOptions:849→payload meta:995）；git_commit.py --enqueue 与 reroute 车道零注入（grep 实证）。生产已实用：**dead/ 19 笔携带 depends_on，全为会话内串行链形态**（token 先行袋：ulib3c 0001→0002→0003、mapbuild 0006→{0007-0010} 扇入、commitspeed-tbl 0049→0050→0051）——"存量 0 笔"仅对 pending 成立（实测 pending=0，2026-09-25 晚）。
- 计数族生产口：attempts 顶层（`_bump_retry_attempts` CQ:1381-1395，env 失败退回前+1）；env_retry/snapshot_retry 进 meta（`_bump_item_retry` LAND:753-775，持久化 processing/ 项文件）；requeue_count 进 meta（CQ:1820-1827）。
### ②下游消费
- `_pick_head` **四方共享**：drain 认领 CQ:1549、池认领 `_pool_claim_item` LAND:2551、队首快照 `_head_snapshot` CQ:2071、位次表 `_pending_position_map` CQ:2111/2181——改其判据即污染位次呈现（qcure 簿 §5 结论维持）。
- attempts 消费：退避惩罚（≥3，`_backoff_penalty_seconds` CQ:1367-1378 进 `_pick_head._rank`）+ 拾取即死信（≥5，CQ:1579/2778）。env_retry/snapshot_retry 消费：≥`_RETRY_META_MAX`=3 升级死信带处方（LAND:750,1902-1909,2829-2848）。requeue_count 消费：≥`_REQUEUE_CIRCUIT_LIMIT`=3 熔断（CQ:1768,1824）。
- stale 双读点：drain CQ:1596 / 池 LAND:2800（重校验放行或 cascade_stale 死信）；C1 合批资格闸拒 stale/depends_on 件（CQ:699-701,648）。
### ③机制现状（+业界参照）
- **requeue 重建新袋唯一字段通道=meta_extra**（CQ:1924-1933：requeued_from/requeue_count/task_id/envelope/requeue_forced）——attempts、last_failure、last_retry_at（顶层）与 meta.env_retry/snapshot_retry/stale **全部静默丢失**，红队 R3-P2 实锤成立。但语义要二分：袋寿命计数（attempts/env_retry/snapshot_retry，"本快照×本环境失败 N 次"）随 requeue（换快照+过时间）**重置是正确的**——继承即事故：attempts≥5 继承→新袋拾取即死信（requeue 变砖）；env_retry≥3 继承→新袋首次环境失败立即死信（处方"排除环境故障后 requeue 重投"永远无法执行）。链寿命计数 requeue_count 已跨袋累计（M1.3-③），whack-a-mole 信号有真源。真缺陷=①静默（无血统留痕）②计数完整性路径依赖（见⑥③）。
- pending 袋变更全集：O_EXCL 原子创建（CQ:1005）/ rename 认领（drain CQ:1559、池 LAND:2564）/ compaction 与 C1 走 `*.merging-*` 后缀 rename（glob 不可见）/ **唯一 lease 内原地改写=_mark_cascade_stale**（CQ:1270-1319，写 meta.stale/stale_by/stale_at）。幽灵防御 4 补丁全为这一个写手而设：D4 回写前 exists 收窄+写后清扫（CQ:1302-1318）、认领前 done 同名幽灵弃置（LAND:2554-2561）、FileExistsError 清源（LAND:2569-2575）、认领后 done 复查弃置（LAND:2576-2582）。
- 业界参照：Sidekiq=Redis 单库原子取任务（无文件竞态面，https://github.com/sidekiq/sidekiq/wiki ）；GoodJob/Oban=SQL `FOR UPDATE SKIP LOCKED` 事务认领（https://github.com/bensheldon/good_job 、https://github.com/sorentwo/oban ）；SQLite WAL 读写并立（https://www.sqlite.org/wal.html ）；文件锁 msvcrt.locking/flock 句柄即锁生命周期（https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/locking 、https://github.com/WoLpH/portalocker ）；GitHub merge queue=投机分组分支+base 移动重验（https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue ）；Celluloid actor mailbox=append-only 收件箱+单消费者（"单写者"原则，https://github.com/celluloid/celluloid ）——与本仓"pending 变 append-only+lease 单写"同构。
### ④代码面
- 实现：CQ（`_pick_head` 1422-1478 / drain 1481-1680 / `_mark_cascade_stale` 1270-1319 / requeue 1771-1941）；LAND（`_pool_claim_item` 2539-2584 / `_pool_process_item` 2751+ / `_bump_item_retry` 753-775）。锁先例（方案③a 可复用勿引新依赖）：`src/zephyr/gov_audit/writer.py:99-175`（msvcrt LK_LOCK 1s 重试≈10s→TimeoutError fail-closed；锁文件永不删除）；CAS 热写=`src/zephyr/shared/io/file_utils.py:527 safe_write_text`。
- 测试：test_commit_queue.py(66)/test_commit_queue_pool.py(15)/test_commit_queue_ghost_pending.py（幽灵族专测——矿③MVP 需同步改写其断言对象）/test_commit_queue_c1_debounce.py。
### ⑤运维/呈现面
- 实测（2026-09-25 晚）：pending=0、processing=1、done=810、dead=609（较晨间 397 净增 212）。dead 609 中：depends_on=19、attempts=0、env_retry=1、requeue_count=30（分布{1:22, 2:8}，熔断阈值 3 未被触发过）、prescription=95（M3.3 已生效）。
- 观测缺口：若上真排序锁，`queue status` 需增 blocked_by/depends_dead 呈现（`_pending_position_map` 加只读字段），堵点本增 kind=deps_blocked。
### ⑥失败态与数据面
- **计数逃逸实锤**：37 笔死信 dead_reason=`landing 异常: LandingEnvironmentError: …`（attempts/env_retry 双无）——环境类失败经 generic-exception 分支（LAND:2864）死信，绕过 env 计数闸+attempts 闸，无升级无处方；37 笔为 09-23 旧账，但 q-…-commitspeed-tbl-…-0065（env_retry=1 后仍以同型前缀死）证明**修复后仍有逃逸路径**（疑点：pool stale 重校验 `_pool_head_reader` LAND:2801 在 try 块外，或 landing 内部 catch 吞 LDE 后以 result 回传——精确逃逸点移交 M5 联办）。
- depends_on 弱约束代价实证：mapbuild 0006 死于 cascade_stale 后，依赖它的 0007-0010 各自白耗一次 landing 才死于下游门禁（TRANSLATION×3+TTL-METADATA）——真排序+死信链传播可在认领前零成本 depends_dead，省 4 次 landing+门禁全套。
- 幽灵写手残留风险持续在案：4 补丁皆为症状治疗；pending 内 `meta.stale` 原地改写是唯一根因。

## 3 三矿方案草案
### 矿① depends_on 真排序锁（挂起排期——设计定稿，施工需先立生产者规约）
- 判定函数：`_deps_satisfied(item, queue_root) -> tuple[bool, str]`（返回 satisfied, detail）。逐 ref 四态：∈done→满足；∈pending/processing→未满足(blocked_by=ref)；∈dead→**读时链跟踪**：dead 项带 `requeued.new_qid` 则递归代换（visited 集防环，深度上界=熔断阈+2），链终dead→受控死信（depends_dead+处方）；四处皆无→满足（fail-open：done 有 7 天 TTL 清理，"无"合法出现在清理后/compaction 吸收后/幻觉 ref——审计留痕不阻塞）。**读时跟踪优先于写回改写**（requeue 不改写新袋 depends_on，与矿③ append-only 方向一致）。
- 挂点=仅两认领处，不动 `_pick_head` 本体：加可选参 `_pick_head(heads, exclude: frozenset[str] = frozenset())`（按 path.name 排除，缺省空集→三显示消费方逐字节不变）；drain CQ:1549 后与 `_pool_claim_item` LAND:2551 后循环"取→blocked 则入 exclude 重取"，全 blocked→本轮结束（deps 只会因 landing/requeue 变化，二者都触发新波，事件驱动无轮询）。**interactive 优先/machine 防饿死语义不破**：exclude 在车道分流前生效，interactive 快道内跳过 blocked 取次老；machine 30min 强制放行（CQ:1472）**不得越权依赖**——该分支改为"最老未 blocked machine"，防排序锁恰在 30min 时点破防。防饿死双保险：blocked 自身龄>`_DEPS_BLOCK_TIMEOUT_SEC`（建议 7200s，与 landing_staleness 同量级）→强制放行+堵点本挂账（依赖永不来=生产者会话死亡场景，fail-open 放行优于永塞）；依赖进 dead→depends_dead 即时受控死信不空等。
- 存量零影响证明：①触发条件=meta.depends_on 非空，当前 pending=0、在途生产口唯一且需显式 flag；②缺省参数=既有 66+15 测试与三显示消费方零感知；③C1 合批早已拒 depends_on 件（CQ:648）无交互；④19 笔 dead 存量已成终态不回读。施工前置：与 M3.4 token 先行袋合流定"谁允许写 depends_on"规约+status 呈现字段。
### 矿② requeue 计数洗白（施工——今晚可落，最小件）
- 裁定：袋寿命计数**重置为正确语义**，堵"静默"不留痕即可。方案：`requeue_dead_item` 的 meta_extra 增 `requeue_lineage={from:qid, attempts_prev, env_retry_prev, snapshot_retry_prev, last_failure_prev(截500), dead_reason_prev, at}`——纯审计字段零消费方，无副作用面；attempts/env_retry/snapshot_retry 保持不继承。明确**不采纳**全继承：见③②继承副作用（新环境被旧环境计数误杀）。
- 配套小件（与 M5 联办）：generic-exception 死信分支（LAND:2863-2864 与 CQ:1633-1634）前加 isinstance(ex, cq.LandingEnvironmentError) 分流——环境类失败永不以"landing 异常"名义死信（计数完整性是洗白议题的前置：计数本身会漏记，继承与否都失真）。
- 熔断相互作用：三层阈值各守一面不打架——attempts≥5（袋内毒药）／env_retry≥3（同类环境失败）／requeue_count≥3（跨袋连败链，唯一跨 requeue 累计者）。lineage 留痕后，requeue CLI 可打印"上袋 attempts=X env_retry=Y"辅助人工判断是否 --force 越熔断。
### 矿③ pending 袋 sidecar 化（MVP 施工——今晚可落；完整方案二期）
- **a) 文件锁=不做**：msvcrt/portalocker 是建议锁，锁不住非合作读者（status/health/_pick_head 全是裸读）；且 rename 认领换目录项不换句柄，锁不随 rename 转移——对幽灵竞态（rename×原地写）无根治力；引 portalocker 违反零新依赖，msvcrt 直用又新增第二套锁语义（writer.py 已有先例但场景是单文件 append，非此竞态）。成本中、收益负。
- **b) sidecar 校验（sha）=降级为观测件**：写时记 sha 读时验只能**检测**不能阻止，且 sidecar 自身写入同样面临竞态（两文件原子序不存在）；保留其价值做"袋篡改 fsck"挂 queue_health（对账 blob_sha256+字段签名），二期与 manifest 合并实施。
- **c) SQLite 单库=三期再议（倾向不做）**：认领协议全重写（O_EXCL+rename→事务/`SKIP LOCKED`），status/health/测试/排障习惯（cat 袋文件）全断，收益仅在中高并发——k=4 单机文件语义未见瓶颈（pending 峰值 83）。大爆炸迁移违反内收判据。
- **MVP（今晚）=stale 指令旁路化，pending 变 append-only**：`_mark_cascade_stale` 停止原地改写袋 JSON，改 O_EXCL 原子写旁路指令 `pending/.stale/<qid>.json`（{stale_by, stale_at, trigger}）；stale 双读点（CQ:1596/LAND:2800）与 C1 资格闸（CQ:699）改双读（袋内 meta.stale 旧位 OR 指令文件，一版过渡）；清标放行=unlink 指令（替代 meta.pop+CQ:1601-1603 回写）。收益：袋文件创建后不可变→D4 四补丁失去存在理由（先留一版作保险带，下版净零拆除——新增 1 个旁路目录+1 个读函数，拆除 4 个防御段，总量负增长）。规模：~60-80 行+改 ghost 专测断言+3 新测试。
- 完整方案（二期）：pending 目录升级为"write-once 对象+append-only 指令日志（manifest.jsonl，代际编号）"，认领时验袋完整性（含 stale/依赖指令回放），即 Celluloid mailbox/GitHub manifest 校验同构；再往上是 SQLite（三期，仅当跨机或多写者需求出现）。

## 4 自审闸三态裁定
- **矿②：施工**（今晚）——requeue_lineage 留痕+逃逸分流两小件，挂点单一（CQ:1924-1933/LAND:2863），风险最低、红队 P2 直接闭环。
- **矿③：MVP 施工**（今晚可落）——stale 旁路化；完整 sidecar 校验/SQLite=挂起（二期/三期）；文件锁=不做（有据裁定）。
- **矿①：挂起排期**——设计已定稿（本簿 §3①），施工卡生产者规约（谁可写 depends_on，与 M3.4 合流）+status 呈现配套；无存量 pending 受影响，不抢 M1/M5 主病灶窗口。
## 5 长尾清单
- 37+1 笔 LDE-in-generic 死信无升级无处方：精确逃逸点定位移交 M5（疑 `_pool_head_reader` try 块外/landing 内部吞 LDE），本班只立分流原则。
- requeue_lineage 与 deadletter 班"处方/owner_session"字段同袋共存，二期可合并为袋级 `lineage` 单结构（避免字段簇增生）。
- depends_dead 死因需登记 `_DEAD_REASON_*` 三分类表（qcure deadletter 矿 2 同点）——否则落 other 桶成新暗数。
- `pending/.stale/` 旁路目录需入 `_STATES`/health 四态计数视野之外的白名单（勿成新 hold_* 式暗仓）。
- CREATE-GUARD：本簿新建 .md 需 creation_token 登记（tests/ 外不豁免），由战役协调口统一补登。
