---
ttl: task_bound
completes_when: 图11 封矿且 config/dev_delivery_map.yaml 四件套落地后本件转归档参考
title: 图11 交付流水线图·环节总骨架（00_skeleton，本图唯一收敛基准）
owner: st-mapbuild-20260924
---

# 图11 交付流水线图 00_skeleton

> 一句话域：**代码从会话诞生到落地 dev 主区的全部"开发时"流水线环节**（不含运行时模块归属——那是 GOMAP）。
> 本件=环节全集 + 三态计分板 + 路由表。环节编号 D11-* 一经定稿即契约，作业簿标题必须引用。
> 普查先验（`docs/_working/map_census/00_panorama_map_census_v1.md` §3 图11）三车道框架成立，本骨架在其上把 15 环节初稿扩至 28 环节（扩面证据见 §4 批次志）。
> 状态标记纪律=`sop/mining_sop/skeleton_mining_policy.md` §5：✅=有活跃管线在产数的实查证据（接口存在≠✅），每条附实查路径。

## §0 域定义与四道门实证（裁定#409 一域一图准入四问）

**域职责**：管"改动如何安全、串行、可复活地从 AI 会话手里到达 dev 分支"——触发是会话启停与提交/入队事件，终点是 dev ref 推进 + claim 释放 + handoff 落盘。

### 门① 独立触发与终点

- 触发：a) 会话启动/收尾（`src/zephyr/governance/ops_governance/phase_manager.py:248 session_startup` / `:368 session_shutdown`）；b) 提交请求=CLI 唯一正门 `scripts/git_commit.py`（文件头 L20"全项目唯一合法 git commit 命令行入口"）；c) 队列新项事件（`src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py` 头：watchdog 监听 `pending/` file-created 事件自举排空）。
- 终点：`landed_at/landed_id` 回填 done/ 台账（实查：done 最新项 q-20260924-st-backup-cold-20260924-0019 landed_at=2026-09-24T12:38:45+08:00）+ claim 释放（`scripts/git_commit.py:734 _settle_claims_after_commit`）+ handoff 落盘（`.runtime/handoffs/` 实查非空）。
- 起止与 GOMAP/TDM 均不重合：GOMAP 管运行时模块（见门③原文），TDM 管决策逻辑。

### 门② 跨模块交接清单（本域天然是一张图而不是一堆散件的证明）

会话车道 → 提交车道 → 死信车道共 10 个交接面，逐一实证：

1. `git_commit.py` → `git_commit_gateway.py`（CLI 封装网关，git_commit.py:101 import）
2. 网关 claim_files → `session_concurrency.SessionRegistry`（registry:295；网关 :1257）
3. 网关全局锁 → `.ailocks/git_commit_global.lock`（网关 :495 _GlobalCommitLock，TTL=1800s，文件头 INVARIANTS）
4. 网关 gate 链 → `in_process_gate_registry.yaml` + `gate_auto_registrar.py`（YAML 动态注册，registry L9-13 description）
5. CLI `--enqueue` → `commit_queue.enqueue_item`（git_commit.py:901 调用；queue:636）
6. belt daemon → `commit_queue_landing.bootstrap_drain_with_landing`（belt 头 DEPENDENCIES；landing:2162）
7. landing → 网关全门禁链零适配（landing 头 INVARIANTS"门禁一套不裁"+ :1473 段）
8. landing 死信 → `task_board.tag_dead_letter`（queue:930；task_board.py:332）
9. 网关 commit finally → post-commit 58 reconciler（网关 :1547 `_register_default_reconcilers` 内 `self._reconciliation_registry.register(` 实测 58 处）+ shell guards（`scripts/governance/git_hooks/post_commit_guard.sh` / `reference_transaction_guard.sh`，目录实查）
10. session_worktree merge → 主区 + 主区收敛快进（landing 头 INVARIANTS"主工作区受限收敛"；`session_worktree.py:6714`）

### 门③ 不被现有图/文档覆盖的证明（引原文）

- **GOMAP 明示排除**：`config/governance_operations_map.yaml:16-19` 逐字——
  `out_of_scope_refs:` / `- name_zh: 提交门禁体系` / `ref: docs/01_policies_and_standards/_registry/catalogs/commit_gate_registry.yaml` / `note_zh: 门禁是每模块配套,非运行时流水线节点`。
  即 GOMAP 人工语义层（其 L8 ssot_note_zh 声明 out_of_scope_refs 为"人工语义层,生成器保留"）**主动把本域排除在自身边界外**，这是立图正门依据（与普查 §1"GOMAP out_of_scope_refs=现成的待建纵轴清单"一致）。
- **parallel_session_coordination_policy.md 不承载**：该文是协作契约（协议文本，非机生图、无环节台账）。实查其目录：§1 动机 / §2 注册注销 / §3 held_files / §4 handoff / §5 冲突升级 / §6 close-door / §10 worktree 申请制——全部是"应当如何"的规范层，**没有任何一处描述队列四态、landings、requeue、reconciler 链等机制环节**。普查 §3 图11 已裁定其处置方式="真源路径挂载，不复制内容"（吸收对象），本骨架 §3 沿用。
- **construction_workflow_policy 15 步不承载**：该文 §2 表 L99 自述 `Step 10 GitCommitGateway 落地 | 66_commit_queue_serialization / trae_075 / trae_084 | 不重复，引用`、L101 `Step 12 worktree 合并与清理 | ... | 不重复，引用`——15 步域=单个施工任务的生命周期，其落地两步明确**转引本域真源**，自身不建第二机制视图。
- 结论：三处候选承载面全部以"引用/排除"姿态让位，无第二真源冲突。

### 门④ 机生真源可建性（哪份文件能被生成器扫出来）

| 可扫面 | 真源 | 机生形态 |
|---|---|---|
| 提交流主干 | `git_commit_gateway.py:24-60` `[ALGO_FLOW]` 注释（I1/I2→P1-P5→O1 带 id/name/fields/code 键） | YAML 解析直读，零手画 |
| 会话车道 | `session_concurrency.py:38` `[ALGO_FLOW] external: docs/03_modules/_domain_security/algo_flow/access_control/session_concurrency.yaml`（外部机生件已在盘） | 引用既有 external yaml |
| 队列协议 | `commit_queue.py:52-60` 目录协议 + 队列项 JSON 字段实测（qid/session_id/created_at/branch/base_head/message/files{path,blob_sha256,blob_ref,base_blob,action}/meta） | `.runtime/commit_queue/{pending,processing,done,dead}` JSON 直扫 |
| gate 清单 | `in_process_gate_registry.yaml`（total_gates 字段=99，entry_schema L33-41）；pre-commit shell 侧 `gate_registry.yaml`（generated_by=generate_gate_registry.py，total_gates=174） | YAML 直读，两册均有机器 schema |
| 开关面 | `config/flags.yaml:81/96/101`（commit_queue_serializer / gate_precommit_run / commit_queue_interactive 均 enabled:true）+ gate_result_cache/gate_preflight | YAML 直读 |
| 活跃台账 | `.runtime/session_registry.json`、`.runtime/handoffs/`、`.runtime/commit_queue/belt_daemon.heartbeat` | 运行时 JSON 直扫 |
| 生成器先例 | `scripts/governance/generate_governance_map.py`（GOMAP 427 模块机生样板，GOMAP counts 实测） | 照抄形态 |

## §0.5 目的标签图例与病历挂载声明（血肉四字段=指针真源，禁复制）

> 挂图 SOP（`sop/mining_sop/vertical_map_mounting_policy.md` §2/§3/§4）落地声明节。**四字段内容真源一律指针引用，本骨架禁复制条目正文**（INV-1；2026-10-04 终审修订 5 条标签名自含主体[SOP v1.1.1 §2 规2，st-vm12e-20261004]后，凡复制标签表处即漂移——本节已去复制化，历史复制版见 git 历史）。

- **目的标签图例（12 条冻结）**：真源=`docs/_working/commitmap_cure/f5_purpose_tags.yaml` labels 节（1-11=00_design_basis §1 冻结表逐字、12 号「别把钥匙留在门口」=裁定#480 批准增设）。图头渲染由生成器消费该件（purpose_labels.legend），冻结后机贴不改名。标签贴在**机制**上——门禁级 gate→标签/环节映射=叶层存输入件（INV-1 不进图本体），图内只渲染节点 purpose_tags 直方图（同标签多钉=重复簇显影位）。
- **病历挂载（casebooks）**：真源=`docs/_working/commitmap_cure/f5_casebooks_mount.yaml`（28 环节挂载矩阵，F4 §1 唯一真源）；册号身份反查册=`docs/01_policies_and_standards/_registry/catalogs/casebook_registry.yaml`（REG-CASEBOOK-001，Owner 2026-10-04 上户口批）。完备性铁律=每本永久病历本 ≥1 环节；D11-G01/G02=骨架外缺口件显式不挂（F4 §0 注记）。
- **触发实测/消费者聚合**：真源=`f5_trigger_facts.yaml`/`f5_consumers_agg.yaml`（图内只挂节点级计数与 ≤5 名字指针，明细禁入图）。
- **图外补挂**：三台 in_process 册独有门禁（REAL-KEY-REFERENCE-SCAN / TASK-ORDER-DOCS-LOCK / CONSTITUTION-LINE-LIMIT）标签/环节归属=`chief_purpose_addendum.yaml`（12 号/③/⑨ → D11-C05，2026-10-03 总筹裁定）；QUEUE-LANDING×163 身份核验归裁定#480「门禁身份一本账」收敛批，不在本图单独挂载。

## §1 环节全集（28 环节 = 会话 9 + 提交 13 + 死信 6）

状态列每条附实查路径；⬜/🔨 的区分见 skeleton_mining_policy §5。子环节数=估数（叶层由作业簿枚举，骨架不预枚举品种全集）。

| 环节编号 | 环节名 | 车道 | 状态 | 真源映射（文件:行 或 命令） | 子环节数估计 |
|---|---|---|---|---|---|
| D11-S01 | 会话冷启动与开班检查 | 会话 | ✅ | `phase_manager.py:248`；`.runtime/session_registry.json` 在盘（实查 2026-09-24）；AGENTS §0 冷启动序列 | ≈5 |
| D11-S02 | worktree 分配与池化 | 会话 | ✅ | `session_worktree.py:2607 session_worktree_start`；`worktree_pool.py:277 lease`（P3.3 池化+prefetch）；本会话工作目录=`.aidrafts/st-mapbuild-20260924` 即活体 | ≈6 |
| D11-S03 | 会话心跳与活性判定 | 会话 | ✅ | `heartbeat_daemon.py:39-40`（30s 刷新+jsonl 审计）；`session_concurrency.py:148`（90s 新鲜窗+1800s idle 自退） | ≈4 |
| D11-S04 | 改前 claim（文件锁+基线快照） | 会话 | ✅ | `lock_files.py:549 cmd_acquire`；`git_commit_gateway.py:1257 claim_files`（基线=首次 claim 快照，tracker #92）；`git_commit.py:476 --claim-only 前移协议` | ≈6 |
| D11-S05 | 在途编辑与暂存晋升 | 会话 | 🔨 | worktree 编辑隔离=✅（D11-S02 活体）；`.runtime/sessions/<sid>/staging/ 24h TTL→promote docs/_working` 见于 AGENTS §9.4 与共识件 §1，专属 promote 工具代码侧本扫未定位，TTL 清理由 `reconciliation_registry.py:7677 make_runtime_cleanup_reconciler` 兜底——**作业簿须实查 promote 是否有独立代码面，无则此环降为纪律-only 环节** | ≈3 |
| D11-S06 | 会话内 worktree 提交 | 会话 | ✅ | `session_worktree.py:4580 session_worktree_commit`；`:3312 _ensure_worktree_base_fresh`（裁定#19-B）；`:5254/7261` stash 留痕+`stash_notice.json` 恢复通道（AGENTS §2.8）；DCR 检测+worktree 兼容 gate 子集（头 INVARIANTS） | ≈7 |
| D11-S07 | 合并回主区（merge 正门） | 会话 | ✅ | `session_worktree.py:6714 session_worktree_merge`；`:5828 _run_pre_merge_topo_check`（HIGH drift 阻断）；`:6025 _pre_merge_gate_check`；`git_commit.py:1053 --merge-finalize` 配套（B2 治本①，exit 10 拒晾置） | ≈6 |
| D11-S08 | 放弃与死会话回收 | 会话 | ✅ | `session_worktree.py:7497 abort`；`lock_files.py:786 cmd_cleanup`（auto-salvage）+`:1160 salvage_dead_session`（双证判死→merge abort+stash 归档+释放 claim，审计 `.ailocks/salvage_audit.jsonl`） | ≈5 |
| D11-S09 | 收尾注销与 handoff 交接 | 会话 | ✅ | `session_concurrency.py:786 SessionHandoff`；`git_commit_gateway.py:3538-3545` commit finally 写 handoff（政策 §8 L250 "已接入"）；`.runtime/handoffs/` 实查非空；close-door STEP0=`parallel_session_coordination_policy.md:215-228` | ≈5 |
| D11-C01 | 提交正门 CLI 与危险命令外壳 | 提交 | ✅ | `git_commit.py:18-50`（唯一入口+exit 0-10 契约+拆批纪律 L46-47）；`scripts/git_safety_wrapper.ps1:19,115,153`（dangerous subcommand BLOCKED）；`scripts/git_guard.py` 透传层 | ≈6 |
| D11-C02 | 失败指引锚点递送 | 提交 | 🔨 | `git_commit.py:109-113`（②递送接口 2026-09-24 刚落，锚=commit_navigation_playbook.md+gate_digest_registry.yaml 两文件 ls 实查在盘）；代码已落地但**触发审计记录本扫未实查**——按 §5 纪律"接口存在≠✅"记 🔨，作业簿补一次实弹核验即转 ✅ | ≈3 |
| D11-C03 | claim 结算与失败重试语义 | 提交 | ✅ | `git_commit.py:32-36`（R-04：成功才释放/失败保留+`--failed-claim-ttl` 300s）；`:680 _retain_claims_after_failure`/`:734 _settle_claims_after_commit`；`--adopt-prior-work`（:1071，FOREIGN-CHANGE 恶性循环治本）；死会话 stale claim 精准释放=网关 `release_files`（:1338，AGENTS §2.7） | ≈6 |
| D11-C04 | 全局串行锁与锁争用改道 | 提交 | ✅ | `git_commit_gateway.py:495 _GlobalCommitLock`（.ailocks/git_commit_global.lock TTL=1800s，头 INVARIANTS）；gate→stage→commit 不可分割铁律（ALGO_FLOW P2）；`git_commit.py:1150 --no-auto-enqueue`+`:1306 AUTO-ENQUEUE 锁超时自动改道入队`（P2⑨b） | ≈5 |
| D11-C05 | in-process 门禁链执行 | 提交 | ✅ | `in_process_gate_registry.yaml:41 total_gates: 99`；`gate_auto_registrar.py auto_register_gates`（网关 :98-100 import，YAML 动态注册，registry L9-13 description）；锁外预跑+指纹采信=`gateway:347 _preflight_flag_enabled`+`:2880 _check_gates_with_drift_watch`（flags.yaml gate_preflight/gate_result_cache enabled:true）；worktree 跳过面 `_WORKTREE_SKIP_GATES`（头 INVARIANTS tracker#92） | ≈99（gate 数勿背，读 total_gates 字段） |
| D11-C06 | 暂存与提交本体 | 提交 | ✅ | `gateway:2971 _commit_locked`（gitignored-tracked 分离 :2698；add/rm pathspec-from-file :3008）；`:3607 _has_staged_renames` rename fallback；`:3657 _commit_with_file_message`（`--no-verify -F msg`）；`[GW:<sid>]` 尾标+FORGED-GW-MARKER 防伪（registry gate_id FORGED-GW-MARKER/priority=29 见 landing 头） | ≈6 |
| D11-C07 | pre-commit shell 门禁通道 | 提交 | ✅ | `gateway:3189 _run_precommit_channel`+`:3091 _precommit_build_temp_index`（GIT_INDEX_FILE own-scope，裁定#341 方案②）；`flags.yaml:96 gate_precommit_run enabled:true`（"55 台 pre-commit 门禁在网关通道补获执行权"，SKIP=gate-commit-gw/gate-worktree-required） | ≈4 |
| D11-C08 | 入队即转活（快照入袋） | 提交 | ✅ | `commit_queue.py:636 enqueue_item`（轻检 :442 路径穿越/:469 message/:476 10MB上限，密钥名黑名单 :296 _SECRET_NAME_RE；`:489 _store_blob` 内容寻址去重；`:534 _create_item_excl` O_EXCL；`:548 _compact_pending` 同键覆盖）；实查：`.runtime/commit_queue/blobs/`=19044 个、pending=29（2026-09-24 只读 ls 计数） | ≈7 |
| D11-C09 | 排空调度与消费端 | 提交 | ✅ | `commit_queue.py:769 SerializerLease`（TTL=300s+僵尸 PID :819-821）；通道路由 `:207 channel_key_for_files`（hot/shared 单通道 :197-198）；k=4 池 `commit_queue_landing.py:1938 drain_queue_pool`+`:1685 _pool_cas_replay`（实查 `worktrees/w0..w3` 四目录在盘）；补位消费者 `commit_belt_daemon.py`（事件触发+`:2162 bootstrap_drain_with_landing`，belt_daemon.heartbeat 文件实查在盘） | ≈7 |
| D11-C10 | 真落盘（worktree+CAS+收敛） | 提交 | ✅ | `commit_queue_landing.py` 头"落盘流水线"1-5 步（幂等三重判定→reset --hard dev→基底冲突判定→blob 应用+净树 claim→gateway 全门禁→`update-ref` CAS→主区快进收敛 fail-open）；`:158 _TRANSIENT_GIT_MARKERS`→LandingEnvironmentError 退回 pending 绝不死信；`:2315 assert_single_writer_dev_history`；实查：done=891、最新 landed_at=2026-09-24T12:38、近 3 日 dev 含 `[GW:` 标记 commit=1242 条其中队列落地 283 条（命令见 §7） | ≈8 |
| D11-C11 | post-commit 对账与守卫 | 提交 | ✅ | `gateway:1547 _register_default_reconcilers`（register 调用实测 58 处）；异步编排 `:1034 run_post_commit_reconcile_async`；shell guards `scripts/governance/git_hooks/post_commit_guard.sh`/`reference_transaction_guard.sh`；红蓝触发 `:3559 _post_commit_red_blue_trigger` | ≈58+（勿背数，扫 register( 调用） |
| D11-C12 | 机器车道与紧急通道 | 提交 | ✅ | `gateway:3845 _commit_auto`+`:3827 _reroute_commit_auto_to_queue`（flag `commit_queue_serializer` ON，flags.yaml:81-84，2026-08-22 Owner 翻旗留痕+单写者断言）；`BatchedAutoCommitter`（网关 :97 import/:1007 实例化）；`emergency_commit.py:20-63`（commit-tree plumbing+[GW:sid:emergency]+落册审计，仅锁不可用时合法） | ≈5 |
| D11-C13 | 队列台账与运维观测 | 提交 | ✅ | `commit_queue.py:166 _STATES` 四态；`:2311 cleanup`（done TTL 7 天 :187，dead 永不清理不变量）；`:1719 queue_health`+`:1777 emit_dead_backlog_alert`（阈值真源 alert_threshold_registry THD-ALERT-003，:234-238）；堵点本 `.runtime/audit/bottleneck_ledger.jsonl`（belt 头 INVARIANTS）；归属核实纪律 `git log -1 --name-only`（AGENTS §2.5） | ≈5 |
| D11-D01 | 死信产生（不卡队） | 死信 | ✅ | `commit_queue.py:71-80`（landing 普通 Exception→dead/；BaseException 留 processing 等回收 :73）；实查 dead/=267 项含 dead_reason/dead_at 字段（样例 q-20260922-st-chainpile-20260922-0031 只读核验） | ≈4 |
| D11-D02 | 死因三分类甄别 | 死信 | ✅ | `commit_queue.py:240-290 _DEAD_REASON_ENV_MARKERS/_DEAD_REASON_ITEM_MARKERS`（含 2026-09-16 LOCK_TIMEOUT 归 env、0922 WinError5/206 补盲实证批注）+`:1709 classify_dead_reason`（env/item/other） | ≈3 |
| D11-D03 | 死信台账联动与告警 | 死信 | ✅ | `commit_queue.py:930 _notify_task_board_dead_letter`→`task_board.py:332 tag_dead_letter`（metadata_json.deadletter，头 INVARIANTS L8"不改表"）；`:1349 _notify_task_board_requeued` 同步标注 | ≈3 |
| D11-D04 | requeue 复活链路 | 死信 | ✅ | `commit_queue.py:1387 requeue_dead_item`+`:2184 CLI requeue`（基于当前工作区重建快照→新 qid 排队尾，原项留痕）；实查样例 0031 项 `requeued: {new_qid: q-20260923-...-0055, at: 2026-09-23}`——复活闭环有活体数据（AGENTS §2.6） | ≈4 |
| D11-D05 | 级联失效判定（cascade_stale） | 死信 | ✅ | `commit_queue.py:104-114` B 段头（项 X 落盘后扫 pending：depends_on/base_blob vs HEAD 仍适用→清标放行；不适用→dead_reason=cascade_stale 死信候选不消耗 landing）；item 标记表 :288 收录 cascade_stale | ≈3 |
| D11-D06 | 死信归档轮换与清零战役 | 死信 | ✅ | `dead/` 永不自动清理不变量（queue:56）；实查队列根 8 个轮换袋目录（dead_archive_20260830/…_x1/_x1b/_w8_20260923/_ulib3_zombie_20260923、dead_purged_20260920 等）；战役记录=`docs/_working/2026-09-11-commit-queue-dead-zero-closure.md`（952 项闭环+PURGE 183 项 Owner gated）与 `docs/_working/archive/2026-09/final3_campaign/p12_queue_terminal_record.md`（死信三分法：superseded/真未落地/历史留档）；**残留待查**：`hold_st_gov2`/`hold_stress_phaseB_20260923` 两目录全仓 grep 无出处（见 §6🌑候选/§5） | ≈5 |

**计分板**：✅ 26 / 🔨 2（D11-S05、D11-C02）/ ⬜ 0 / 🌑 点名见 §6。✅ 占比 26/28=92.9%，本域是全仓少见的"机制已高度建成"域——骨架的价值不在补缺，在**把 28 环节钉成收敛基准防作业簿漏族**。

**停止判据三问示例（为何 28 不再拆）**：99 个 in-process gate 不再拆（同生产者同触发口径，只是标签变→C05 叶层）；10MB/穿越/密钥三种入队轻检不再拆（同验证口径→C08 叶层）；dead_archive 各轮换袋不再拆（同一处置动作的参数变体→D06 叶层）。**拆的边界**：生产者系统变（belt daemon vs 入队自举 vs 手动 drain 是三种触发但同一 lease 消费端→不拆）；验证口径变（pre-merge topo-check 与 pre-commit gate 校验对象不同→拆成 S07 子环节而非 S06）。

## §2 三车道分层与同域论证

**车道起止与交接点**：

- **会话车道（S01-S09）**：起=对话启动（冷启动序列）；行=池化取 worktree→心跳→claim→编辑→worktree 内提交→merge/abort→handoff；止=会话注销。**交接点**：S06 worktree 内 commit 产出的 commit 经 S07 merge 进主区后，**等价于**提交车道的一个"已 staged 的变更集"——merge 后的收尾批若要再过正门则入 C 道；S09 handoff 是跨会话状态交接唯一格式真源。
- **提交车道（C01-C13）**：起=任何通道（直连/enqueue/机器 _commit_auto）的提交请求；行=claim 结算→锁→门禁→暂存→落地；止=done/ 回填+归属核实。C 道内部是串行流水线（ALGO_FLOW P1→P5 即其机生主干）。**交接点**：C10 落盘失败→D 道；C11 post-commit reconciler 反过来又是 C12 机器车道（_commit_auto）的上游触发者——环路已声明（reconciler 产 commit→经 flag 改道回队列）。
- **死信车道（D01-D06）**：起=C10 失败判定（普通 Exception）；行=分类→打标→分诊→requeue 或归档；止=requeue 回 pending（复活）或留 dead/ 终态。**交接点**：D04 回 C08 入队（新 qid）；D03 出域到 task_board（任务治理域，引用不吸收）。

**是否同一域（裁定#409 域内收敛）**：一张图成立，不拆。实证：三车道共享同一组不变量与同一批真源实体——死信车道是提交车道的失败分支闭环（同一 JSON 台账、同一 lease、同一 requeue→enqueue 回路，D04 实查样例 new_qid 即 C08 产物）；会话车道与提交车道在 C10 处物理重合（landing 调用的就是网关全门禁链，"门禁一套不裁"）。拆开任何一条都制造跨图假父子边（普查 §2 第 2 条"同域三车道，一域一图收敛示范"结论被本次实查维持，无推翻证据）。

## §3 重叠判定（旁轴，处置五选一）

| # | 撞车面 | 实证坐标 | 处置 | 理由 |
|---|---|---|---|---|
| 1 | GOMAP（config/governance_operations_map.yaml） | :16-19 out_of_scope 排除本域；其 pipeline L0-L6=运行时模块层 | **引用** | 域不同（开发时 vs 运行时）无连接点（普查 §2 第 2 条）；本图节点引用 GOMAP 稳定标识符，禁复制内容（GOMAP L8-9 自己声明的 INV-1 同款纪律） |
| 2 | construction_workflow_policy 15 步 | 该文 L99/L101 Step10/Step12 自标"不重复，引用" | **引用** | 15 步=单施工任务生命周期域（图14 候选）；本图=流水线机制域；互为引用不互吞 |
| 3 | parallel_session_coordination_policy.md | §2-§6 契约文本，无机制环节台账 | **吸收**（按普查"真源路径挂载"口径：其 schema/路径作为 S03/S09 节点挂载件） | 契约层并入流程图为节点注解，文档本体不迁就不复制 |
| 4 | 66 号备忘/08 号文（design_memos） | commit_queue.py/landing.py 头"真源"节逐处引用 | **引用** | 设计史文档，图节点引编号即可（如 §6/§8/§9.7） |
| 5 | git_safety_wrapper.ps1 / git_guard.py | wrapper :19/:115/:153 BLOCKED 清单 | **吸收**（为 C01 子环节"危险命令外壳"） | 同属提交正门工具簇，独立不成环节（停止判据：生产者=同一批脚本，口径未变） |
| 6 | 宪法 L0 §2 并发与提交 | 宪法 9 条纪律 | **引用** | 人机操作纪律=规范的规范，图承载机制不承载守则 |
| 7 | task_board 死信标签 | task_board.py 头 CONSUMERS"66 号提交队列死信标签承载" | **扩展**（task_board 侧不改，本图 D03 记录联动接口） | 消费向：本图是生产方，标签存储归任务治理域 |
| 8 | worktree_drift_watchdog / worktree_lifecycle | 两文件 MATURITY=production 实查头 | **吸收**（S02/S08 子环节：漂移看门狗与生命周期回收） | 无独立起止（服务于 worktree 分配-回收），不构成独立环节 |
| 9 | gate_registry.yaml（shell 174）与 in_process_gate_registry.yaml（99） | 两册均有 total_gates 字段+generator | **引用+扩展**（C05/C07 各自挂一册指针；机生图新增节点须两册同步登记义务=施工期挂接清单） | 门禁册自身有生成器真源，本图只画"执行环节"不抄清单 |
| 10 | 宪章 §8/alignment_checklist §3 挂轴 | 共识件 §5 施工配方 | **引用** | 施工期由总包挂总线（module_id 轴），骨架不预占挂轴内容 |

## §4 批次志（增量计数曲线）

| 批次 | 视角 | 做法 | 环节增量 | 累计 |
|---|---|---|---|---|
| 批1（2026-09-24 上午） | 需求批 | 从普查 §3 图11 三车道骨架反推环节初稿（会话 7+提交 5+死信 3） | +15 | 15 |
| 批2 | 三重扫描批①按生产者逐个过 | 11 个生产者实体逐一读头+定位函数行：git_commit.py / git_commit_gateway.py / commit_queue.py / commit_queue_landing.py / session_worktree.py / session_concurrency.py+heartbeat_daemon / lock_files.py / commit_belt_daemon+worktree_pool / task_board.py / emergency_commit.py / git_hooks 目录 | +11（新增：指引锚点 C02、机器/紧急车道 C12、观测 C13、心跳 S03、salvage S08、handoff S09、precommit 通道 C07、级联 D05、归档轮换 D06、claim 结算 C03、暂存晋升 S05） | 26 |
| 批3 | 三重扫描批②按形态过（队列目录协议逐目录）+ 案例批 | 只读实测 `.runtime/commit_queue` 全目录形态：发现 worktrees/w0-w3 池、hold_st_gov2、hold_stress_phaseB、8 个 dead_archive/hold 袋、processing 孤儿 1 项；反向拆 4 个真实案例（today pending 项 schema / dead→requeue 活链 / 最新 landed 项 / 近 3 日 1242 GW commit 分布） | +2（C09 拆出"消费端 daemon vs 自举"并入环节不增枝、D06 归档轮换正式立环节、通道池归 C09——净增 2：D06 与 C13 细化后确认 C13 批2 已计，最终净 +2） | 28 |
| 批4 | 考古批 | docs/_working 全量 grep（dead_reason/requeue/FOREIGN_CHANGE/LOCK_TIMEOUT/hold_/dead_purged）：命中 perf-plan、dead-zero-closure、p12 终态记录、redblue-v3 等 20+ 篇；确认全部考古发现均落于既有环节（毒缓存修复→C09 子环节、死信三分法→D06 子环节、sys.path 清洗→C08 子环节） | +0 | 28 |

**三扫收敛判定**：批3 与批4 相邻两批增量分别 +2、+0，曲线 15→26→28→28 拉平；按生产者/按形态/按消费者文献三视角各完整过一轮且第二轮零新增——**三扫收敛成立**。唯一未闭环观察=hold_* 两目录出处（不影响增枝，计入 §5 作业簿线索与 §6 🌑候选）。

## §5 待挖清单（作业簿领取入口；编号即文件名契约）

优先挖序（给总包排产）：**C10 > D04 > S07**（理由：C10 是全域唯一"真 git 落地"环节且 INVARIANTS 密度最高、k=4 池最新演化最快；D04 是普查三车道承诺的"复活"闭环且活体样例已备；S07 的 pre-merge 双检测是 HIGH drift 硬阻断所在、作业簿最容易发现未声明子面）。

| 作业簿文件 | 覆盖环节 | 领条目提示（首查坐标） |
|---|---|---|
| 01_D11-S01_会话冷启动.md | S01 | phase_manager.py session_startup 全文 + record_session_start_commit.py |
| 02_D11-S02_worktree分配与池化.md | S02 | worktree_pool.py 全文 + session_worktree_start 双向阻断分支 |
| 03_D11-S03_心跳与活性.md | S03 | heartbeat_daemon.run_daemon + session_concurrency 判死双轨 |
| 04_D11-S04_claim协议.md | S04 | lock_files acquire-batch + claim_snapshots 目录机生面 |
| 05_D11-S05_暂存与晋升.md | S05 | 🔨→先实查 promote 有无代码面（全仓 grep "promote"）|
| 06_D11-S06_worktree内提交.md | S06 | session_worktree_commit 的 sync/stash/DCR/base-fresh 四段 |
| 07_D11-S07_merge回主区.md | S07 | _pre_merge_auto_clean + topo-check + pre-merge gate + reconcile_verify 三前置 |
| 08_D11-S08_放弃与salvage.md | S08 | salvage_dead_session 双证判死 + _death_evidence |
| 09_D11-S09_handoff交接.md | S09 | SessionHandoff schema vs 政策 §4.3 + 活体 handoffs 抽样 |
| 10_D11-C01_提交正门.md | C01 | exit code 全谱 × 触发分支矩阵；git_safety_wrapper 清单 |
| 11_D11-C02_指引锚点.md | C02 | 实弹触发一次记审计转 ✅；playbook/digest 双件结构 |
| 12_D11-C03_claim结算.md | C03 | R-04 矩阵（成功/gate 阻断/锁超时/异常 × TTL）；adopt-prior-work 审计件 |
| 13_D11-C04_全局锁与改道.md | C04 | _GlobalCommitLock 等待循环 + 探针 _probe_commit_lock_busy + 堵点横幅 |
| 14_D11-C05_in-process门禁链.md | C05 | 99 gate × priority × own_scope 分簇（**叶层，勿全抄进图本体，INV-1**）|
| 15_D11-C06_暂存与提交本体.md | C06 | rename fallback / gitignored-tracked / --no-verify -F / GW 标记链 |
| 16_D11-C07_precommit通道.md | C07 | temp-index own-scope + 55 台 pre-commit 归属（挂 gate_registry 指针）|
| 17_D11-C08_入队协议.md | C08 | 轻检四规则 + compaction 竞态 + O_EXCL/qid 唯一性 |
| 18_D11-C09_排空与消费端.md | C09 | lease 算法 + 孤儿回收 + belt 事件面 + k=4 池路径锁 |
| 19_D11-C10_真落盘.md | C10 | 落盘五步逐步拆 + 主区快进收敛三态 + 双 guard 交互（WORKTREE-REQUIRED/FORGED-GW 逃生语义）|
| 20_D11-C11_post-commit对账.md | C11 | 58 reconciler 分族 + async 编排 + 两 shell guard 触发链 |
| 21_D11-C12_机器与紧急车道.md | C12 | _commit_auto 改道全分支 + emergency_commit 合法边界（伪造标记判则）|
| 22_D11-C13_台账与观测.md | C13 | health 快照字段 + THD-ALERT-003 + done TTL + 归属核实配方 |
| 23_D11-D01_死信产生.md | D01 | Exception vs BaseException vs LandingEnvironmentError 三分流 |
| 24_D11-D02_死因甄别.md | D02 | 标记表演化史（0916/0922 补盲批注全收）|
| 25_D11-D03_台账联动.md | D03 | task_board deadletter 标签读写两侧 + requeued 不解除语义 |
| 26_D11-D04_requeue复活.md | D04 | 活体样例 0031→0055 全链复跑 + requeue 取回失败面 |
| 27_D11-D05_级联失效.md | D05 | depends_on/base_head 重校验 + interactive/machine 双车道 head 选取 |
| 28_D11-D06_归档与清零.md | D06 | dead 三分法战役复跑 + **hold_st_gov2 / hold_stress_phaseB 出处考古**（全仓无命中，查 git log/会话台账 2026-09-23 窗口）|

溢出规则提醒（共识件 §3）：作业簿发现骨架外新环节 → 先回写本 §1 再施工；本件回写权=总包与本骨架主。

## §6 封顶声明与🌑点名

**封顶**：自 2026-09-24 起，图11 环节全集冻结为 D11-S01~S09 / C01~C13 / D01~D06 共 28 环节。此后增长=叶→数据集的实现（gate 条目、reconciler 条目、标记串条目进作业簿），不再增枝；增枝须过 skeleton_mining_policy §3 停止判据三问并留批次号。封顶≠死亡：新战役（如队列再演化 k>4、新消费端 daemon）可触发批次重开。

**🌑 点名（个人/当前形态不可得，留档）**：

1. **IDE 对话层触发源**：会话"诞生"发生在 Trae IDE 内部（注入/弹窗/上下文组装），仓库内无机生面可扫——机生边界只能停在 session_worktree_start 被调用这一可观测点（session_worktree.py 头 CONSUMERS"AI 对话启动时调用"即上限）。
2. **Owner 灰度翻窗过程记录**：flag 翻开的对话现场（如 2026-08-22 serializer 翻 ON、2026-09-12 interactive 批准）只余 flags.yaml 描述内引与 commit 号（281b7f469），过程本身不可机生——图节点以 flag 状态为可扫描面，历史过程引用裁定/留痕文号。
3. **hold_st_gov2 / hold_stress_phaseB_20260923 目录出处**：全仓（.py/.md/.yaml/.json）grep 零命中，只能确认是人工搬运留袋（疑似 st-gov2 会话与 st-k4-20260923 压测 Phase B 的隔离袋）——先按 ⬜ 处理：D06 作业簿领"考古定罪"条目，若从 git log/会话台账仍不可考则转 🌑 终态。**2026-10-03 更新（F6 基线复核）**：hold_stress_phaseB_20260923 出处已考——压测 Phase B 空转死信隔离袋，判明于 cleanup_final 班（`docs/_working/cleanup_final/cleanup_ledger.md:26` + `docs/_working/cmd_ledger/automation_master_plan.md:63`「禁擅自 requeue」）；hold_st_gov2 仍无出处（`commitmap_cure/f3_trigger_evidence_readme.md:184` 仅列表提及）——本项 🌑 收窄为 hold_st_gov2 一件。

## §7 实查命令附录（Owner/后续会话照跑即可复核；全部只读）

```bash
# 0) 环境（RULE-ENV）
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd D:/ZephyrAlpha

# 1) 队列四态+blobs 计数与最新落地（复核 §1 C08/C10/D01 实查数）
python scripts/commit_queue.py health --no-alert   # 只读快照；勿跑 status（status 会触发自举排空）
for d in pending processing done dead blobs; do echo "$d $(ls .runtime/commit_queue/$d | wc -l)"; done
ls -t .runtime/commit_queue/done/*.json | head -1   # 看最新 landed_at/landed_id

# 2) 近 3 日 dev 真落地活性（复核 1242/283 计数）
git log refs/heads/dev --since="3 days ago" --format=%B | grep -c "\[GW:"
git log refs/heads/dev --since="3 days ago" --format=%B | grep -c "q-2026"

# 3) 单写者断言（C12 改道后终态判据，只读）
python -c "import sys;sys.path.insert(0,'scripts/governance');import commit_queue_landing as m;print(m.assert_single_writer_dev_history.__doc__)"

# 4) 开关面（复核 §0 门④）
grep -n "commit_queue_serializer\|commit_queue_interactive\|gate_precommit_run\|gate_result_cache\|gate_preflight" config/flags.yaml

# 5) 门禁册计数（勿背数，读字段）
grep -n "total_gates" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml

# 6) reconciler 注册数（复核 58；口径=register 调用行数，动态值以命令为准）
grep -c "self._reconciliation_registry.register(" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py

# 7) 会话车道活性
python scripts/lock_files.py status
python -c "import json;d=json.load(open('.runtime/session_registry.json',encoding='utf-8'));print(len(d.get('sessions',d)))"
ls .runtime/handoffs | head -5

# 8) 死信复活活链抽查（§1 D04 样例）
python -c "import json;d=json.load(open(r'.runtime/commit_queue/dead/q-20260922-st-chainpile-20260922-0031.json',encoding='utf-8'));print(d['dead_reason'][:80]);print(d['requeued'])"

# 9) hold_* 袋出处考古（§6🌑-3，可复核"全仓无命中"）
grep -rn "hold_st_gov2\|hold_stress" scripts src docs --include="*.py" --include="*.md" --include="*.yaml" | head

# 10) GOMAP 排除面原文（§0 门③立图依据）
sed -n '16,19p' config/governance_operations_map.yaml
```

——本骨架主：st-mapbuild-20260924（图11 车道）· 落盘 2026-09-24 · 批1-4 记录见 §4
