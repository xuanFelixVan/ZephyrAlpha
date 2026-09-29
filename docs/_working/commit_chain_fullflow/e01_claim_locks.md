---
created: 2026-09-30
ttl: task_bound
title: E1 claim锁会话层挖矿簿
session: st-gate-rationalize-20260929
---

# E1 claim/锁/会话层 挖矿簿（01）

> 环节定义（00_skeleton §一）：lock_files + claim_snapshots + SessionRegistry + 全局提交锁。
> 全部行号为 2026-09-30 实测（grep 重定位）；种子行号已漂移处以本簿为准。

## 0 自审闸：【挖干】

理由：四大件（lock_files.py 1659 行 / session_concurrency.py 931 行 / gateway claim+全局锁段 / heartbeat_daemon）逐件读毕源码，六向台账齐、每件有 file:line 锚、耗时账有实证数（P2-1 出仓战役 476 件 ~10min、WinError5 退避 ≤160ms、盲轮询 0.1s）。缺口两处已列明（§4）：worktree_manager.get_current_worktree 内部与 .ailocks registry.json 的实时行数未挖（属 E5/E7 lane），不阻塞本环节施工。

## 1 组件全清单

### 1.1 scripts/lock_files.py（.ailocks 文件锁协议，1659 行）

| # | 组件 | 功能 | 代码锚点 | 触发时机 | 耗时账 | 自动化属性 |
|---|------|------|---------|---------|--------|-----------|
| 1 | 常量组 | LOCK_ROOT=.ailocks / TTL=1800s / registry.json / Mutex 名+5s 超时 | lock_files.py:97-107 | 模块加载 | 零 | 静态 |
| 2 | _registry_mutex | Windows 全局命名 Mutex（Global\ZephyrLockFilesRegistry）串行化 registry 整表 RMW；WAIT_ABANDONED(0x80) 所有权转移 | lock_files.py:115-134 | 每次 registry 读改写必经 | 5s 超时上限；无竞争亚毫秒 | 每笔 claim/release 必经 |
| 3 | _is_stale | 锁陈旧判定：裁定#252 锁存活=会话存活（SessionRegistry 判活）→ claim 过期+会话静默窗才回收（T10）→ 旧格式锁退 PID+TTL | lock_files.py:161-214 | acquire/check/cleanup 碰锁时 | 构造 SessionRegistry+整表读 1 次/锁 | 每笔 acquire 必经 |
| 4 | _claim_expired_and_idle + _audit_claim_reclaim | 过期+静默(1800s)回收判定；回收写 .ailocks/reclaim_audit.jsonl 禁静默夺锁 | lock_files.py:222-259 | _is_stale 命中过期分支 | append 1 行 | 条件触发 |
| 5 | _read_owner/_write_owner/_cleanup_stale | owner.json 读写（含 session_id/pid/expires_at/hostname）+锁目录 rmtree | lock_files.py:262-301 | acquire/release 内 | 2 次小文件 IO | 必经 |
| 6 | _load_registry/_save_registry | registry.json 整表读 + tmp+flush+fsync+os.replace 原子写（防崩溃半成品） | lock_files.py:304-329 | Mutex 临界区内 | 整表 IO 随锁量线性（fsync 每次写） | 必经 |
| 7 | _is_git_tracked / _tracked_paths_batch | 逐件 `git ls-files --error-unmatch`（timeout 10s）/批量分片 200 件一次 `git ls-files`（timeout 60s）；判定=存量文件跳过命名门禁（B5③） | lock_files.py:342-363, 646-671 | acquire 前半程 | 单件=1 git 子进程；批量=N/200 次 | 每笔 acquire 必经 |
| 8 | _acquire_prepare | 前半程：命名门禁（未跟踪新文件全量检查 :478-488）+ 原子目录创建 os.makedirs(exist_ok=False) 互斥 + 重入/DENIED/T10 三查实情 :499-517；不碰 registry | lock_files.py:449-546 | 每笔 acquire 必经 | 1 makedirs + 1 write owner.json | 必经 |
| 9 | cmd_acquire | 单件加锁：prepare→登记 registry，Mutex 超时回滚锁目录防半锁 | lock_files.py:549-565 | 单件 claim 场景 | 1 次 Mutex RMW | 条件（批量入口普及后少用） |
| 10 | cmd_acquire_batch | 批量加锁：一次 tracked 批判 + N 次 prepare（零 registry）+ 一次 _add_many 临界区；Mutex 超时回滚全部新锁 | lock_files.py:674-719 | git_commit.py claim 批量链 | 476 件从 ~10min 压到秒级（P2-1 实证，:456-460 docstring） | 每笔提交 claim 必经（经 gateway） |
| 11 | _warn_if_uncommitted | 释放前 git status --porcelain 单文件警告（DM-202919，不阻断） | lock_files.py:568-598 | release（warn=True） | 1 git 子进程/件（千件级=分钟级，:725） | 条件 |
| 12 | _release_prepare/cmd_release | 单件释放：归属判定+孤儿锁清理+registry 摘除 | lock_files.py:601-643 | 单件 release | 1 Mutex RMW | 条件 |
| 13 | cmd_release_batch / cmd_release_all | 批量释放：件级清理+一次摘除临界区（warn=False 免逐件 git status）；release_all 慢操作放 Mutex 外 | lock_files.py:722-783 | 收尾 --release-only | N rmtree + 1 Mutex | 收尾必经 |
| 14 | shorten_claim_ttl | R-04 失败保留 claim 的 TTL 收窄兜底（retention=commit-failed-retained 标记） | lock_files.py:1245-1281 | 提交失败时由 git_commit.py 调 | 逐件 owner.json 重写 + 1 Mutex | 条件（失败路径） |
| 15 | cmd_cleanup | 死锁清扫+R-10 salvage 候选捕获（死会话判定/git 回收在 Mutex 外，:794-797） | lock_files.py:786-884 | 冷启动 RULE-GUARDIAN | 整表读+逐锁 stat | 每会话冷启动必经 |
| 16 | salvage_dead_session | 死会话遗物回收：双证判死(_death_evidence :983)→①merge --abort ②claim 路径 stash 归档 ③双登记处释放，全程审计 | lock_files.py:1160-1232 | cleanup 自动/cleanup 显式 | git 子进程×2-3（仅判死成功后） | 条件 |
| 17 | pre_write_guard/LockGuard/cmd_guard_write/FileLockedError | 写前自动 check+acquire 原子门禁（异常/上下文管理器/CLI 三形态） | lock_files.py:1364-1457 | safe_write_text 等写路径前置 | 同 cmd_acquire | 写操作必经（经封装） |
| 18 | cmd_status/cmd_check/cmd_list | 观测三命令（列锁/查锁/过滤） | lock_files.py:366-419, 1284-1312 | 人工/编排查询 | 整表读 | 只读 |

### 1.2 src/zephyr/security/access_control/session_concurrency.py（SessionRegistry，931 行）

| # | 组件 | 功能 | 代码锚点 | 触发时机 | 耗时账 | 自动化属性 |
|---|------|------|---------|---------|--------|-----------|
| 19 | 常量组 | session TTL=3600s / 心跳超时 90s / reap 宽限 900s / idle 自退 1800s / registry 路径 .runtime/session_registry.json / 退避(10,50,100)ms | session_concurrency.py:146-174 | 模块加载 | 零 | 静态 |
| 20 | SessionInfo + _is_session_alive | 会话条目（held_files/last_heartbeat/last_activity/logical W-29）；判活双判据：pid>0 → is_pid_alive+TTL3600；pid=0 → 心跳 90s | session_concurrency.py:217-299 | 所有消费方 | 进程内 CPU | 每次判活必经 |
| 21 | SessionRegistry.__init__ | anchor_main_root 锚主仓（#ARCH-324：commit_queue worktree 判据收口）+ threading.RLock（进程内 TOCTOU） | session_concurrency.py:312-330 | 每进程构造 | 零 IO | 必经 |
| 22 | register / mark_logical | 注册会话（re-register 整体重建条目，:358-359）/ 原地翻 logical 旗（零触碰 held_files） | session_concurrency.py:340-400 | 会话开工/续注册 | 1 整表读+1 美化整表写 | 会话生命周期必经 |
| 23 | heartbeat | 刷 last_heartbeat：**整表 load+save**（per-pid tmp+os.replace） | session_concurrency.py:513-521 | daemon 每 30s | 全表 JSON 序列化+replace，30s/次/会话 | 常驻 |
| 24 | list_active | 列活跃+清理死会话（功能判死零窗口；物理删除走 900s 宽限 tombstone，:540-547）——**有写副作用** | session_concurrency.py:523-553 | gateway 警告/gate 消费 | 整表读；有 expired 时+1 写 | 每笔 commit 锁外经 warn_non_worktree_commit |
| 25 | get_session / other_held_files | 只读查询（无写副作用，为网关专用）；他会话持有集 | session_concurrency.py:555-598 | _is_stale/HELD-OVERLAP gate | 整表读 | 每笔 claim/commit 必经 |
| 26 | claim_file / claim_files_batch | 单件=整表 RMW/件（O(N²) 磁盘写，476 件 ~10min 实证）；批量=一次 load+一次 save+懒注册+顺带心跳 | session_concurrency.py:635-672, 703-746 | claim（gateway 走批量 :1394） | 批量版秒级 | 每笔提交必经 |
| 27 | release_file / release_files_batch | 释放：归一化索引匹配摘除；批量=一次 load+save | session_concurrency.py:674-701, 748-768 | 提交成功/收尾 | 秒级 | 成功笔必经 |
| 28 | _load/_save + _replace_with_retry | 整表读 / per-pid tmp+os.replace（AI-NORTH-001 共享 tmp 名竞态治本）；WinError5(EACCES) 3 次退避 ≤160ms（读方毫秒级窗口；等待原语 getattr 形态避 PERM-TRIGGER gate 误拦） | session_concurrency.py:177-203, 770-812 | 每次 RMW | 写=全表美化 JSON+replace；冲突时 +160ms 封顶 | 必经 |
| 29 | heartbeat_daemon（跨件） | 30s 独立 detached 进程刷心跳；idle>1800s 自退（#ARCH-HEARTBEAT-002 活性反转治本）；W-29 logical+C355 队列等待双豁免 | src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py:100, 112-115, 387, 477-503 | worktree 会话期间常驻 | 30s/次整表写（与 commit 进程写互踩面=WinError5 退避） | 常驻 |

### 1.3 gateway claim/快照 + 全局提交锁（git_commit_gateway.py 4690 行）

| # | 组件 | 功能 | 代码锚点 | 触发时机 | 耗时账 | 自动化属性 |
|---|------|------|---------|---------|--------|-----------|
| 30 | __init__ | SessionRegistry 构造 + _claim_snapshots/_claim_heads 内存态 + 从磁盘恢复全部快照（glob *.json 逐个解析） | git_commit_gateway.py:1092-1142 | 每进程实例化 | 随 .runtime/claim_snapshots 文件数线性 | 每进程 1 次 |
| 31 | claim_files | 批量 claim（registry.claim_files_batch :1394）→ HEAD 锚捕获（1 git rev-parse，会话首次）→ _files_with_head_diff 一次批量预判（1 git diff HEAD --name-only :1352-1370）→ 逐件基线（预判无 diff=空串免子进程；有 diff 才 capture_baseline_diff 1 git/件）→ 幂等保留首次基线（tracker #92 :1426-1427）→ adopt 认领（空基线+审计）→ 整批落盘 | git_commit_gateway.py:1372-1451 | git_commit.py main :1296 / --claim-only :494 | git 子进程 2+N_dirty/笔 | 每笔提交必经 |
| 32 | release_files | 批量释放 registry + 清内存快照/HEAD 锚 + 删磁盘快照（静默 fail） | git_commit_gateway.py:1453-1486 | R-04 成功结算（git_commit.py:749） | 1 批量 RMW | 成功笔必经 |
| 33 | capture_baseline_diff / _log_adopted_work | 单件 git diff HEAD 基线 / adopt 审计（diff_size+sha256+domain 头解析）→ {sid}_adopted.jsonl | git_commit_gateway.py:1497-1514, 1520-1561 | claim 有 dirty 件时 | 1 git/件；append 1 行 | 条件 |
| 34 | claim 快照落盘三件套 | load（恢复 :1572-1602）/ save（tmp+os.replace 原子 :1608-1637）/ delete（release 时 :1643-1656）；S3-C 治本崩溃恢复 + HOT-FILE-BASE-FRESHNESS claim_head 锚 | git_commit_gateway.py:1572-1660 | claim 后/实例化/release | 每笔 claim 1 写（整批一次，:1448-1450） | 每笔必经 |
| 35 | Rx-2 锁等待账本 | lock_wait/lock_timeout 两事件六字段（timestamp/event/session_id/waited_ms/holder/timeout）append .runtime/audit/lock_wait_events.jsonl；env ZEPHYR_LOCK_WAIT_LEDGER 一键回退 | git_commit_gateway.py:560-593, 2710-2720, 2767-2778 | 每次拿锁（成功+超时）| append 1 行×2 点位 | 每笔必经 |
| 36 | _GlobalCommitLock | 全项目唯一串行锁：<主仓根>/.ailocks/git_commit_global.lock（B22⑤ strip_session_worktree 锚主仓 :616-620）；O_CREAT\|O_EXCL 原子创建 :636；僵尸 PID 清零窗口 :661-676；TTL=1800s :243,677；等待默认 60s :244（lock_wait_timeout 可调 :2546,2704）；**0.1s 盲轮询** :245,704；waited_ms/holder 观测字段 :627-629；锁自清失败降级残锁兜底 :706-719 | git_commit_gateway.py:596-719 | commit() 进锁 :2708 | 无竞争亚毫秒；竞争时 10 次/s 整读锁文件+Event().wait | 每笔 commit 必经 |
| 37 | _audit_commit_lock_fallback | OSError（磁盘满/权限）→ 无锁降级 commit_lock_fallback.jsonl 审计（TRAE-079 铁律6） | git_commit_gateway.py:726-743, 2781-2790 | 锁基础设施故障 | append 1 行 | 条件 |
| 38 | CLI claim 生命周期（git_commit.py） | R-04 决策表：OK/NOTHING_TO_COMMIT→释放；否则保留+TTL 收窄 300s+claim_retention.jsonl；--release-only 走 lock_files 正门双登记处释放（T10 治本 :412-434） | scripts/git_commit.py:652-772, 412-504 | 每笔 CLI 提交 | 1 审计 append（失败时） | 每笔必经 |

## 2 六向台账

- **上游触发源**：①git_commit.py CLI（claim_files :1296 → commit → _settle_claims_after_commit :734）②commit_queue 落地器（worktree 内同链路，SessionRegistry 锚主仓 :322）③lock_files.py CLI 直调（人工/编排）④safe_write_text/pre_write_guard 写路径 ⑤heartbeat_daemon 30s 常驻 ⑥session_worktree_start（register）。
- **下游消费方**：①E3 门禁链（CLAIM-REQUIRED/HELD-OVERLAP gate 读 registry.held_files 与 claim 快照）②_is_stale（锁陈旧判定消费会话判活）③commit_preflight/收尾序列（release_files_batch）④reclaim_audit.jsonl/lock_wait_events.jsonl/claim_retention.jsonl→E9 遥测与 commit_perf_report ⑤watchdog/三证 worker（list_active 判活）。
- **输入面**：session_id、文件清单（绝对/相对路径归一两次：_norm_path 与 _normalize_file_path 同源 gateway:1344-1350）、task、ttl_minutes、adopt_prior_work、ZEPHYR_SESSION_ID/ZEPHYR_FAILED_CLAIM_TTL_S/ZEPHYR_LOCK_WAIT_LEDGER env。
- **输出面**：.ailocks/{registry.json, */owner.json, reclaim_audit.jsonl, git_commit_global.lock}；.runtime/session_registry.json；.runtime/claim_snapshots/{sid}.json、{sid}_adopted.jsonl、claim_retention.jsonl；.runtime/audit/lock_wait_events.jsonl。
- **真源锚**：锁 TTL=1800s 真源 trae_001_file_operation_security.yaml ttl_design（lock_files.py:98-99）；锁存活=会话存活=裁定#252（:167）；is_pid_alive 真源唯一=zephyr.shared.infra.process_pool（:89-91 TRAE-001）；路径归一真源=_normalize_file_path（session_concurrency.py:205-214）；claim 基线语义=「首次 claim 时刻」（gateway:1421-1425 tracker #92）。
- **耗时账汇总**：健康笔（无竞争）claim 链 ≈ 2+N_dirty 个 git 子进程 + registry 一次整表写 + 快照一次落盘，秒级；历史病灶=逐件整表重写 476 件 ~10min（P2-1，gateway:1384-1386 与 session_concurrency:706-708 双实证）已被批量入口治本；竞争笔锁等待默认上限 60s（0.1s 盲轮询 10 次/s）；WinError5 尾退避 ≤160ms/次写；心跳 daemon 30s/次整表写为常驻底噪。

## 3 现状缺陷与已修记录

已修（引用留痕，勿重做——gate_survival_adjudication.md:362「已执行勿重做」清单含 Rx-2）：
1. registry.json 并发丢锁（26 session RMW 实证）→ §7.28 全局 Mutex+fsync+os.replace（lock_files.py:103-107, 314-329）。
2. 批量半程：逐件 registry 重写 476 件 ~10min → _acquire_prepare 拆分+claim_files_batch/release_files_batch 一次临界区（lock_files.py:449-460; session_concurrency.py:703-708）。
3. 裁定#252 锁存活=会话存活，瞬时 PID 必死误杀活锁 → owner.json 带 session_id 走 SessionRegistry 判活（lock_files.py:167-201）。
4. T10 治本：#252 短路 claim 自身 expires_at 致交接班互挡 → 过期+静默 1800s 才回收+DENIED 三查实情（lock_files.py:193-194, 217-231, 502-510）。
5. SessionRegistry 共享 tmp 名竞态（AI-NORTH-001 2026-08-15 心跳丢失假过期）→ per-pid tmp；WinError5 读方持锁 → 3 次退避 ≤160ms（session_concurrency.py:781-812, 173-203）。
6. 心跳 daemon 活性反转（僵尸 daemon 永久保活死 session，实测 sess-39820/sess-53456）→ last_activity 独立锚+idle 1800s 自退+W-29 logical 豁免（session_concurrency.py:162-169, 236-240; heartbeat_daemon.py:477-503）。
7. R-04 claim 生命周期与提交事务对齐（CLAIM-REQUIRED ×50/24h 根因）→ 成功才释放+失败 TTL 收窄 300s 兜底（scripts/git_commit.py:652-677；lock_files.py:1245-1281）。
8. --release-only 漏 .ailocks 登记处（T10 收尾误判）→ lock_files 正门双登记处释放+回读校验（git_commit.py:412-434）。
9. Rx-2 锁等待落账已落（st-finaldel-crx2-20260929，02_prescriptions.md:25 处方真源=docs/_working/final_delivery_campaign/mining_commit_chain/02_prescriptions.md）→ 成功+超时双点位六字段（gateway:560-593, 2710-2720, 2767-2778）。
10. 锁不可用静默降级 → TRAE-079 铁律6 fail-open 审计（gateway:726-743）。
11. #ARCH-324 落地器 SESSION-REQUIRED 假红（worktree 双 registry 分裂）→ anchor_main_root gitdir 指针解析（session_concurrency.py:314-322）。

现存缺陷（未修，均有锚）：
- D1 盲轮询：_GlobalCommitLock 竞争时 0.1s 间隔 O_EXCL+整读锁文件，10 次/s（gateway:245, 704；adjudication:285 定性【优化】P2 指数退避）。
- D2 全局锁无 holder 死锁自愈外的公平性：先到先得纯靠轮询巧合，无 FIFO（与 E7 队列 serialized 通道互补，直连路径仍裸抢）。
- D3 SessionRegistry 每次心跳整表重写（session_concurrency.py:513-521），N 会话常驻时 30s×N 次全表 IO 底噪——增量写待办（skeleton:34 B2）。
- D4 list_active 带写副作用（清理+整表写 :540-547），只读消费者误用会放大写放大（get_session 已提供只读面 :564-577，但 warn_non_worktree_commit 仍走 list_active gateway:1319）。
- D5 registry 无 vacuum：.ailocks/registry.json 只增不减死条目依赖 cleanup/salvage 人工/冷启动触发。

## 4 待办与移交

1. 【st-gate-rationalize-20260929 认领】盲轮询退避：0.1s 固定轮询→指数退避（处方 adjudication:285；施工点 gateway:704）。A/B 段施工。
2. 【st-gate-rationalize-20260929 认领】SessionRegistry 增量写（skeleton:34 B2 条目）：心跳/claim 改增量或降噪（施工点 session_concurrency.py:513-521, 781-812）。
3. 移交 E3：CLAIM-REQUIRED/HELD-OVERLAP gate 消费本层输出的判定细节（skip 映射 git_commit.py:640-648）。
4. 移交 E7：队列通道与直连通道对全局锁的混抢现状（AGENTS.md §2.6）；serializer worktree 干净暂存区机制。
5. 未挖缺口（不阻塞）：WorktreeManager.get_current_worktree 内部实现（属 E5 worktree 段）；.ailocks/registry.json 实时锁量行数（本次只读探测超时未取得，施工前可 `python scripts/lock_files.py status` 补测）。
