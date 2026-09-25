---
ttl: task_bound
completes_when: 封矿战役下游每车道各认领一个 ST-ID 且 S3 全部盲区有归属或关闭；本表经每轮施工后回填不产生新 ST 即收敛
title: S1 提交管道阶段总表（封矿战役·骨架第一步：阶段清单完备性证明）
owner: ZephyrAlpha-Owner
session: st-commitspeed-skeleton
date: 2026-09-24
---

# S1 提交链阶段总表（Stage Inventory）

> 命题：从「AI 会话决定交付文件」到「dev ref 移动且产物持久」的**全部阶段与全部自动化**清点，
> 一个不漏。判据：任何不在本表的写路径 = 封矿失败。下游车道各取一个 ST-ID。
> 计时口径：成本列全部指向可复测真源（`.runtime/audit/*.jsonl` 字段），不背死数；
> 门禁条数以 `gate_execution_stats.jsonl` 的 `n_specs` 字段实测为准（当前观测值 102，勿抄本文）。

| ST-ID | 名称 | 入口 file:line | 串行化范围 | 成本实测（怎么量） | 改动的状态 | 子环节数 | 备注 |
|-------|------|----------------|-----------|------------------|-----------|---------|------|
| ST-01 | 会话建立与 worktree 创建 | `scripts/session_worktree.py:172` (cmd_create)；`zephyr/security/access_control/session_concurrency.py:333` (SessionRegistry.register) | 每会话独立，无全局串行为；worktree.lock 文件锁（`worktree_manager.py` MODIFY-GUARD 声明） | 一次性成本，未计时（S3-GAP-06） | .git（worktree 注册）、`.runtime/sessions/<sid>/`、SessionRegistry | 4 | 路径前缀 `.aidrafts/`，分支前缀 `session/`；pool 变体走 `worktree_pool.py:121`（`.aidrafts_pool/`） |
| ST-02 | 施工前置登记（lookup/token/翻译/depgraph） | capability_lookup（宪法冷启动第 4 步）；`scripts/governance/d3_metadata/batch_creation_tokens.py`；同目录 `add_module_translation.py`；`scripts/governance/apply_depgraph.py` | 无锁但**生成额外 commit**（回灌 ST-04→ST-14） | 每条登记 = 一次完整提交周期（大头见 ST-07/14/20） | 规则 YAML、注册表、DB（架构数据） | 5+ | CREATE-GUARD/TRANSLATION-COVERAGE/DEPGRAPH 的账都折进这里；净零申报也走此路 |
| ST-03 | 修改前 claim | `scripts/lock_files.py`（acquire/release/cleanup）；registry 路径 `.ailocks/registry.json`:101 | Windows 全局命名 Mutex 序列化所有 read-modify-write（`lock_files.py:103` 注释 T10/§3.12 实证） | Mutex 争用尖峰未计时 | .ailocks/registry.json | 3 | 双登记处（.ailocks + SessionRegistry）必须同时放，见 lock_files.py:873 注释 |
| ST-04 | 提交发起与模式分派 | `scripts/git_commit.py:943` (main)；exit codes 8 种；纯 claim 分支 `:476`；release-only `:411` | 无（分派层） | ≈0 | 无 | 6 | 模式：直连 / --enqueue / --release-only / claim-only / --reconciler-verify / emergency |
| ST-05 | 锁外预检快败（P0-A） | `scripts/git_commit.py:775` (_run_preflight)；`commit_preflight.py` (PREFLIGHT_GATES 白名单)；`gate_cache_preflight.py:96` (Fingerprint) | 不占全局锁 | `.runtime/audit/preflight_events.jsonl` `ms` 字段（观测 ~10^4 ms/件） | `.runtime/audit/preflight_events.jsonl` | 3 | 缓存命中则 `preflight_reused` 记入 gate 统计 reused 字典 |
| ST-06 | 全局提交锁 | `git_commit_gateway.py:495` (_GlobalCommitLock)，获取点 :2503；超时缺省 `_LOCK_TIMEOUT_DEFAULT` :219 | **整条 102 门禁链 + pre-commit 68 hook + git add/commit 全在锁内**——这是全局串行点本体 | 排队时长 = 锁持有者整链时长 × 队列深度（无直接计时，S3-GAP-01） | `.runtime` 锁文件；僵尸锁自清 :551；OSError 降级无锁通道 :614 | 4 | 锁按 worktree 键控的并行前提已在 k=4 池施工验证（见记忆卡，本文不背书） |
| ST-07 | 门禁链（in-process 102 门） | `git_commit_gateway.py:1010-1013` (CommitGateRegistry + auto_register_gates)；统计器 `commit_gate_registry.py` (gate_execution_stats) | 锁内、顺序执行（当前无 DAG 并行） | `.runtime/audit/gate_execution_stats.jsonl` `total_ms` 与逐门 `ms` 字典（冷链观测 3.6–4.3×10^5 ms，缓存生效降至 ~5×10^4；单门大头看 ms 字典排序） | 只读为主；部分门写审计 | 5 | 慢门样本：CREATE-GUARD 单门即占数十秒级（同文件 ms 字典可复测）；failed/reused 字段=改道信号 |
| ST-08 | pre-commit 子进程通道（68 hook） | `git_commit_gateway.py:3189` (_run_precommit_channel)；`.pre-commit-config.yaml`（hook 数=`grep -c 'id:'` 现测 69 项含自身） | 锁内、pre-commit 框架并行度有限 | 无逐 hook 计时（S3-GAP-02）；通道整体在 gate_chain_ms 内混测 | index（hook 可改文件→触发"files were modified"重跑 1 次） | 4 | own-diff 作用域：pass_filenames 型限本提交文件；失败与本文件无关=warn 不阻断 |
| ST-09 | 暂存与真提交 | `_commit_locked` :2971 → `_add_and_remove_normal_files` :3008 → `_resolve_commit_result` :3453 → `_commit_locked_finalize` :3523 | 锁内独占 index | 未单独计时（在链尾，占比小，S3-GAP-01 一并补相位计时） | index、.git objects、HEAD/dev | 5 | delete 用 git rm 分离（pathspec 不匹配坑已固化）；index 卫生事件审计 `_audit_index_hygiene` 注释 :638 |
| ST-10 | 锁忙改道入队 | `scripts/git_commit.py:611` (_probe_commit_lock_busy) → `:818` (_enqueue_mode)；flag commit_queue_interactive 出厂翻转门位 | 无（改道决策） | 改道率可从 preflight_events `path=enqueue` 观测 | queue 目录（新袋） | 3 | 陷阱：在 worktree 内跑 --enqueue 会投进 worktree 本地无守护袋（记忆卡在案，S3-GAP-07） |
| ST-11 | 队列存储与幂等 | `commit_queue.py:643` (enqueue_item)、:489 (_store_blob 内容寻址)、:476 (_validate_blob_size)、:548 (_compact_pending)、:1110 (_pick_head，qid 字典序) | 袋写入经文件锁；blob 内容寻址无锁 | 未计时（亚秒级假设，S3-GAP-03） | `.runtime/commit_queue/`（活体守护在消费——本文档只读不写） | 4 | 同 sid 后袋静默超前袋的历史坑在册（记忆卡），条目四态必核字节 |
| ST-12 | 皮带守护驱动 | `commit_belt_daemon.py:112` (_drain_once)、:808 (watchdog Observer 事件驱动 poke)、:743 (_check_and_reexec epoch 自检，:643-695 三 epoch)、:855 (main) | 单守护；epoch 变更自杀重启 | poke→drain 延迟未计时；守护熄火曾零证据（历史事故：无 handler） | `.runtime/commit_queue/`、daemon 心跳 :274 | 4 | 事件触发符合永久系统四要素红线（reconciler 禁 cron） |
| ST-13 | 串行器租约与出队 | `commit_queue.py:779` (SerializerLease 秒级续租 :802)、:1144 (drain_queue)、:1314 (try_bootstrap_drain) | **单串行器 = 当前吞吐天花板**（池模式 k 见 ST-15） | drain 轮次间隔 = lease 续租周期；每轮件数无遥测（S3-GAP-03） | lease 文件、队列条目状态机 | 3 | health/status 入口 :1731，死信告警 :1789 |
| ST-14 | Worktree 落地（单串行器路径） | `commit_queue_landing.py:1501` (WorktreeLanding.__call__)、:885 (ensure_worktree)、:940 (_sync_worktree)、:1268 (_advance_dev CAS) | 每 item 独占 serializer worktree | 每件落地 = sync + apply + commit-tree + CAS，未分段计时 | worktree、dev ref（CAS old→new）、.git | 6 | 注册表热文件走三方合并 :638 (three_way_merge_registry_yaml) / :1113 (_merge_registry_file)，冲突消息 :472 |
| ST-15 | 池并发落地（k worker） | `commit_queue_landing.py:2014` (drain_queue_pool)、:2089 (_run_pool_wave)、:1988 (_pool_claim_item 路径锁)、:1761 (_pool_cas_replay)、:1894 (resolve_pool_workers) | 每路径锁 + dev ref CAS 重放 | 实测并发系数曾恰为 1.000（即名义 k 未兑现并行，前轮战役结论；复测看 pool 心跳 :1975） | 每 worker 独立 worktree (`worker_worktree_path` :1906)、dev ref | 5 | CAS 重放 commit-tree 是跨 worker 冲突的正解 |
| ST-16 | 主区工作区收敛 | `commit_queue_landing.py:1390` (_converge_main_workspace)、:1361 (_converge_one)、:1448 (_refresh_integrity_baseline_main_repo) | 落地后同步主区，避免工作区与 dev 漂移 | 未计时；integrity 基线刷新成本随仓大小涨 | 主区工作树、integrity 基线 | 3 | 主区 clean 是 --reconciler-verify 三前置之一 |
| ST-17 | 队列条目生命周期治理 | `commit_queue.py:1397` (requeue_dead_item)、:1721 (classify_dead_reason)、:1904-1994 (dead-burst 聚合/台账/任务板打标)、:940 (dead-letter 通知) | 无锁，读多写少 | dead 率 = health 输出字段；burst 阈值 :1921 | 队列条目、bottleneck_ledger.jsonl、任务板 | 4 | 队列项 dead 后须读 dead_reason 修正再 requeue（宪法并发条 6） |
| ST-18 | post-commit 同步钩链 | `.git/hooks/post-commit`（git lfs → `scripts/governance/git_hooks/post_commit_regen_yaml.py` → `post_commit_guard.sh` POST-COMMIT-GUARD → Qoder tracker 行）；另 `.git/hooks/reference-transaction` → `reference_transaction_guard.sh` | **每次 commit 在提交进程返回前同步跑** | lfs 探测 + regen spawn + guard git 操作 + 外部 node runtime（Qoder tracker 是最不可控的一环）；无分段计时（S3-GAP-04） | .git、生成目标 YAML；guard 可 reset 回滚（改 dev！） | 4 | POST-COMMIT-GUARD 会回滚无 [GW:] 标记的提交；emergency 标记伪造检测在此 |
| ST-19 | post-commit reconciler 异步 | `git_commit_gateway.py:1063` (run_post_commit_reconcile) → :1034 (_run_post_commit_reconcile_async detached worker)；`zephyr/governance/audit/reconciliation_registry.py:688` (ReconciliationRegistry)、:770 (reconcile_for) | detached 单 worker 内 30+ spec 顺序 | ZEPHYR_RECONCILE_SYNC=1 可复测同步/异步差；priority 排序见注册表 | DB/CH（部分 reconciler 回写，如 exam_result 类）、审计 jsonl | 5 | 事件触发合规（无 cron）；断点4/5 修后 commit_message 全链可追溯 |
| ST-20 | 派生产物再生扇出（已证大头） | `scripts/governance/reconcile_generators.py:605` (reconcile_stale)、:558 (_is_stale mtime)、:162 (_acquire_regen_lock 全局互斥)、:396 (_invoke_parallel 存在但扇出默认串行位)、清单真源 `docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml`（含 path_tree/domain_doc/decision/governance_map 等条目） | **regen 锁全局互斥** → 每件提交后串行扇出 | 单件成本 = 逐生成器 subprocess（超时上限见 :65 注释，domain_doc 最重）；复测：`--stale` 手动跑并计时 | 派生 md/yaml 大量文件 → 又触发 ST-02/ST-04 追加提交（提交放大环） | 4 | 这是"衍生再生串行扇出吃掉大头"的前轮实测结论的机制解释；缓存键含 HEAD 必失效坑在册 |
| ST-21 | 治理记账回灌环 | ST-02 产物 + ST-19/20 产物 → 新的 git_commit.py 调用 | 每轮记账再走一遍全链 | 放大系数 = 每业务件产生的记账件数（无度量，S3-GAP-05） | 注册表 YAML、tokens、depgraph、DB | 3 | 封矿主靶：per-domain 队列 + 门合并的目标对象 |
| ST-22 | 看门狗与收割者干扰 | `src/zephyr/trading/process_reaper.py`（keep 清单 :248-259，`data/runtime/process_reaper_keep.txt`）；`worktree_drift_watchdog.py`（scan_once 判定 claimed/grace/dedup/auto_claim/alert，quarantine 快照 `.runtime/quarantine/`）；`checker_supervisor.py:101`（常驻 worker 消子进程税）；`write_audit_daemon.py:223`；`heartbeat_daemon.py` | reaper 计划任务全局扫描（可杀提交进程！） | 误杀事件无专账（长批任务靠 keep 防误杀） | 杀进程、quarantine 目录、write_audit.jsonl | 5 | 观测样例：`.runtime/audit/worktree_drift_watchdog.jsonl` verdict=grace_delete；reaper 计划任务不存在=写操作硬阻断（宪法冷启动第 2 步） |
| ST-23 | 会话收尾 | `scripts/session_worktree.py:293` (cmd_merge，:398 unmerged 证书校验)、:570 (cmd_abort_inner，:351 _audit_abort)；`git_commit.py:411` (_release_and_verify)；`session_concurrency.py:473` (unregister) | merge 实为主区直连 merge（连坐源，记忆卡在案）；abort 需双登记处释放 | 一次性，未计时 | .git、worktree 目录、SessionRegistry、.ailocks | 5 | staging promote（`.runtime/sessions/<sid>/staging/` 24h TTL）+ handoff 交接包在收尾序列内 |

合计 **23 个阶段**；子环节总数 = S2 树第一层节点计数（见同目录 `s2_substage_tree.yaml`）。
分段：ST-01~03 预提交，ST-04~09 直连提交路径，ST-10~17 队列路径（ST-14 与 ST-15 是同一落地的两代实现并存——封存时必须显式裁决谁是正门），ST-18~21 提交后异步与放大环，ST-22 全程旁路干扰，ST-23 收尾。

## 完备性自证（挖干交叉核对，详见 S3）

- (a) `src/zephyr/gov_enforcement/rule_bridge/` 全部 20 模块逐一归位：git_commit_gateway→ST-06~09/18~19，commit_gate_registry/gate_auto_registrar/gate_cache_preflight→ST-07，commit_preflight→ST-05，commit_queue 侧→ST-12，session_claim→ST-03，session_worktree→ST-01/23（与 scripts/ 同名壳为双入口，已合并），worktree_pool/lifecycle/manager/drift_watchdog→ST-01/22，checker_supervisor/write_audit_daemon/heartbeat_daemon→ST-22，**emergency_commit→ST-04 分支但未单列（S3-GAP-08）**，**batched_auto_committer→无归位（S3-GAP-09）**。
- (b) scripts 匹配 commit|queue|worktree|gate|lock|session 全清单已核：git_commit/commit_queue/lock_files/session_worktree 归位；`record_session_start_commit.py`、`pre_commit/` 目录、三个 register_*.ps1 计划任务见 S3-GAP-10。
- (c) 68~69 个 pre-commit hook 全部折进 ST-07/ST-08 两阶段（hook 不是阶段是门），逐 hook 计时缺失=S3-GAP-02。
- (d) reconciler 注册表 30+ spec 折进 ST-19（按 priority 排序），其派生扇出单列 ST-20。
- (e) 计划任务/守护：reaper（ST-22）、belt daemon（ST-12）、serializer（ST-13）、drift watchdog（ST-22）、write_audit/heartbeat（ST-22）；`register_gate_fulltree_audit_task.ps1` 等注册任务清单未逐条打开=S3-GAP-10。
