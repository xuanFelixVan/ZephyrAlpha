---
title: "大扫除盘点矿·全仓遗留混乱只读盘点清单（04 号件）"
created_at: "2026-09-23"
session: "st-cleaninv-20260923"
ttl: "task_bound"
---

# 04_mess_inventory — 全仓遗留混乱只读盘点（零修复零删除）

> 盘点窗：2026-09-23 02:12–02:55。HEAD 起点 e3de925d，窗内 dev 两度前进（02:23 emomine 批1=a9818b2ef2 → 02:4x b10 复职终态+chainpile 复职W8=fc929ddd16）——主干在移动，各节均注明测量时点。本件全程零修复零删除；写面仅本报告 + creation_token 1 条。
> 判读纪律：暂存遗留一律走 `scripts/governance/classify_workspace_wip.py`（禁肉眼判罚）；死信只核状态不重判（C2 台账为准）；不确定项归 §7 需 Owner 批。

## 1. 主区暂存遗留（令①）

普查口径：`git status --porcelain=v1 -uall` 全量 61,127 行（证据：`.runtime/tmp/cleaninv_git_status.txt`）。

两位状态码分桶（02:15 时点，HEAD=e3de925d）：

| 状态 | 件数 | 说明 |
|---|---|---|
| `??` 未跟踪 | 60,369 | 其中 **data/c4_pdf_cache/ 60,245**（PDF 缓存区未入 .gitignore）、data/strategy_intake 42、data/local_fallback_quarantine 21、其余散件 61 |
| ` M` 未暂存改 | 302 | |
| `M ` 已暂存改 | 173 | |
| ` D` 未暂存删 | 137 | |
| `A ` 已暂存增 | 111 | |
| `MM` | 14 | |
| `AM` | 10 | |
| `D ` 已暂存删 | 9 | |
| `RM`/`AD` | 1+1 | |

追踪面脏文件合计 758（reaper 独立报 820、判读器报 829，口径差异=判读器含 untracked 白名单面）。

官方判读器结论（`classify_workspace_wip.py`，基线 HEAD=e3de925d，活跃会话 4：st-integrated-bt / st-emomine / st-regfix-laneA / st-xhs-full；证据：`.runtime/tmp/cleaninv_wip_classify.txt|.json`）：

| 判读类别 | 件数 | 处置语义 |
|---|---|---|
| active_wip（活跃会话 claim 在途） | 16 | 勿动勿报，等各会话自己提交/释放。含 capability 册/in_process_gate 册/module_translation 册/library INDEX 族/cohort_daily_writer 等，全部 claim=st-integrated-bt |
| derived_sync（后台派生缓存再生） | 451 | watchdog 自动收敛/随下次提交吸收，禁报警禁擅动（blueprint 族为主） |
| stale_rollback（疑似死会话陈旧回退） | 285 | watchdog 死会话清扫自动卸载 staged；人工处置须 lock+审计 |
| fresh_change（新鲜写入待归因） | 13 | 见下明细 |
| untracked_new（新文件待归因） | 64 | 见下明细 |

判读器原话：**待归因 362 件（陈旧回退/新修改/新文件）——只有这三类才值得汇报**。

fresh_change 13 件归属核对：`commit_queue_landing.py`、`registry_mass_deletion_gate.py`、`tag_vocab_gate.yaml`、`library_blood_flesh_gate.yaml`、`state_vocab_registry_gate.yaml`、`test_tag_vocab_gate.py`、`test_state_vocab_registry_gate.py`、`test_registry_mass_deletion_gate.py`、`test_registry_batch_edit_and_mass_deletion_gate.py`（staged）= **Lane A W2/W3/W4 治本套件在途**（DISPATCH Lane A 卡片+热修令在案）；`in_process_gate_registry.yaml`（staged）= **st-gslim-20260923 已持锁（02:5x 实测，.ailocks 在册）**；`fail_open_register.yaml`、`docs/02_.../09_ai_architecture/implementation_plans/index.md`（判读器标注"判读异常"）、`docs/library/pipeline.md` 三件归属不明 → §7-11。

untracked_new 64 件要点（全清单在判读器 JSON）：① CAS tmp 残留 **9 件**（`*.tmp.<pid>.<hash>` 形态：alert_threshold_registry.yaml.tmp.21732、infrastructure_registry.yaml.tmp.45444、archiver.py.tmp.18276、check_ssot_gate.py.tmp.20724、commit_queue_landing.py.tmp.21732×4、batch_creation_tokens.py.tmp.21732；pid 核验=45444/20724/18276 进程已死，**21732=ZCode.exe 宿主长活进程无法按 pid 判死**，mtime 09-19~09-22）——删除需 Owner 批（§7-9）；② `scripts/register_belt_daemon_task.ps1`=Lane B 押后件（CREATE-GUARD token 冻结中，HANDOFF §9 有案）；③ grid_2026091* 策略网格目录 ×11（strategy_intake 作业产物）；④ library 族新件（blood_flesh gate/collectors/generators/regen_reconciler）、sim_daily 族（runner+DDL+测试）、standards_governance `__init__`×2、session_logs/st-flashbiz-20260918/ 等散件 → §7-4 打包呈报。

交叉提示：HANDOFF_v1.md §6 表第 5 行"AGENTS.md 两行宪法指针（staged 待批）"的本体此刻落在判读器 stale_rollback 桶（mtime<HEAD）——**机器判读与收口记录冲突，按"待 Owner 批"呈报**（§7-8），不做任何处置。

## 2. 队列死信对账（令②，只核状态不重判）

队列现状（02:20 时点，证据 `.runtime/tmp/cleaninv_queue_status.json`）：pending 10 / processing 1（租约持者 PID 46068 存活=慢项在途不抢）/ done 854 / **dead 363**，总 1,228。belt daemon 在线。

死信画像（363 项，死信 JSON 逐个解析）：

- 按会话 Top：workclean 58、code-doc 36、ulib3 35、chainpile 31、emomine 29、integrated-bt 26、xhs-full 26、dloop 24、gateaudit 21、commitchain 16、residual 16，共 25 个会话。
- 按死因 Top：GATE-PRECOMMIT-RUN 80、CREATE-GUARD 37、.gitignore prestage 拒绝 13、NEW-FILE-DEPGRAPH 11、NOQA-VALIDATION 11、REGISTRY-MASS-DELETION 11、三向合并失败回退人工 10、PermissionError 9、ORPHAN-MODULE 9。
- 按创建日期：09-20=10、09-21=96、09-22=240、09-23=17。
- 历史归档区：dead_archive 296 + dead_archive_20260830 61 + dead_purged_20260920 113 + dead_archive_20260919_x1 912。

与 C2 台账对账（台账=`c2_deadletter_triage/disposition_list.csv` 692 行=691 数据行/62 个唯一 qid；shard2 台账 184 行）：

| 对账项 | 结果 |
|---|---|
| 台账 62 个 qid 当前状态 | **62/62 仍 dead，0 个已解决** |
| 台账覆盖外新增死信 | **301 个 qid 不在 C2 台账**（C2 分诊 09-22 之后新死） |
| 台账 691 行处置建议分布 | REPLAY_MERGE_3WAY 240 / NONE_COVERED 239 / REPLAY_ADD_WHOLE_FILE 94 / COMMIT_FROM_DISK 62 / 其余 56 |

结论：C2 台账没有条目失效（状态核对通过），但**新增 301 qid 未入账**，W8 死信清偿处置清单需扩表 → §7-3。对账明细：`.runtime/tmp/cleaninv_deadletter_recon.json`。

## 3. 分支三态（令③，02:52 终核时点，HEAD=fc929ddd16）

本地分支 17 条 + 远端 4（origin/HEAD、origin/dev、origin/master、origin/backup/pre-rebase-msgfix-8ce48cf0）。worktree 12 处（主区 + .aidrafts×6 + .aidrafts_pool×1 空锁 detached + serializer/commit-queue 锁定 + .worktrees×3；证据=`git worktree list`）。

| 三态 | 分支 | 证据 |
|---|---|---|
| 在用 | dev（主干） | 当前 checkout |
| 在用 | serializer/commit-queue | 队列序列器专用 worktree（locked），与 dev 同 commit |
| **未合并（待收口）** | session/st-t0-revival-20260922 | **独有提交 3 个**（b2a3c8bc7a/1cbe54884a/338bd9bdb4，14 文件 +1,024 行=cost_trio 重建+词表立法+收官报告；即 09-22 已派发的"t0 合并微班"件，等队列落地）；`git rev-list --count dev..该分支`=3 |
| 已合并·可拆（先拆 worktree） | ai/st-b10-final（**盘点窗内其 4 个独有提交已由本尊复职收口进 dev**：02:15 时点曾为 4，02:4x 起=0） | dev log 32b4e138a4+549a4c6b54 在案 |
| 已合并·可拆 | ai/st-chainpile、ai/st-sim-launch、session/{data-fix,maxexec,laneA,laneB,residual-20260917,tilib-clear,workclean,xhs-full}、master（陈旧 09-20，dev 祖先链） | `git branch --merged dev` 16 条 |
| 已合并·在用（新发） | session/st-gslim-20260923、session/st-wm1-mineB-20260923（盘点窗内新出现，均 0 独有提交） | 分支列表实测 |
| 远端滞后 | origin/dev **落后本地 244+ 提交、领先 0**（02:3x 时点；主干仍在前进，读时重测） | `git rev-list --count origin/dev..dev` |
| 远端可拆（需 Owner） | origin/backup/pre-rebase-msgfix-8ce48cf0（08-01 rebase 前备份，在 dev 祖先链内） | `git branch -r --merged dev` 在列 |

净结论：唯一带未合并工作的分支=t0-revival（3 提交，已知派发件非遗失）；其余全部可归并为"拆 worktree 后删分支"的机械动作（§7-10 打包批）。

## 4. 行尾 CRLF 清单（令④，`git ls-files --eol` 全仓 16,542 文件）

- **index 侧干净**：16,503 i/lf + 9 i/-text（二进制）+ 30 i/none——入库面全 LF，无带病提交。
- **工作树侧污染**：**w/crlf 8,534**、w/lf 7,818、**w/mixed 13**。根因=写盘侧 newline=CRLF 违 `.gitattributes eol=lf`（e3de925d 修 capability 册时已定性同款）。git 内容比对经 clean 过滤不受影响，但盘面污染制造 diff 噪声与工具误判面。
- 按扩展名：py 3,454 / yaml 3,241 / md 1,685 / csv 69 / html 31 / json 30 / ps1 8 / jsonl 5 / js 5 / 其余 7。
- 按目录 Top：docs/03_modules 4,397、src/zephyr 3,074、docs/_working 500、scripts/governance 87、tests/signal_ashare 72、schemas/categories 60、docs/01_policies_and_standards 50。
- **注册表族中招 29 个 catalog yaml**（含带病在册的 alert_threshold_registry.yaml——THD-ALERT-007 押后条目所在件、candidate_module_registry、field_dictionary 等，全列见证据文件）。
- w/mixed 13 件全列：.gitignore、data/crypto/universe_manifest.csv、data/strategy_intake/lane_g_seen_urls.csv、data/sz_open_data_catalog/catalog_full.csv、docs/_archive/TASK-OPS-2026062501.md、docs/_working/archive/2026-09/dataqa_audit/index.md、docs/_working/emotion_line/{gap_list_and_construction_proposal,redblue_round_record}.md、docs/_working/fullflow_campaign/{adjudications/req_rbstats_01,lanes/rbstats_prescriptions}.md、docs/_working/sector_line/sector_redblue_round_record.md、scripts/industry_graph/tier_migration_map.yaml、tests/governance/test_git_hooks_marker_forgery.py。
- 全清单证据：`.runtime/tmp/cleaninv_crlf_files.txt`（8,534 行）、`.runtime/tmp/cleaninv_eol.txt`。治本方向（写盘工具 newline 口径统一）呈 §7-5。

## 5. .runtime 隔离区 / quarantine 快照量（令⑤）

顶层普查（文件数 / 体积）：

| 区 | 量 | 要点 |
|---|---|---|
| .runtime/tmp | **42,525 文件 / 12G** | **bizmine 子目录独占 8.9G**（09-19 通宵战遗留）；pytest_* 3 处 ~21M；p10_t0 16M |
| .runtime/commit_queue | **56,344 文件 / 4.2G** | worktree/ 1.7G+36,121 文件（序列器工作副本）、blobs/ 2.5G+17,052（快照 blob 含死信）、dead 历史归档区×4 合计 1,382 文件 |
| .runtime/quarantine | **2,704 文件 / 408M** | **drift_* 目录 1,983 个**（drift watchdog 09-15T02:10 事件簇，每目录 9 文件）+ branch_refs.log/dead_test_pollution/gova_leftover/pre-merge-cleanup-20260815 各 1 |
| .runtime/orphan_quarantine | 0 文件 | 空 |
| data/local_fallback_quarantine | 21 文件 / 24M | 未跟踪（与 §1 关联） |
| .runtime/audit | 20 文件 / **1.6G** | **feature_flags.jsonl 单文件 1.3G**、worktree_drift_watchdog.jsonl 83M、write_audit.jsonl.{1,2,3} 各 51M |
| .runtime/gate_audit | 50 文件 / 324M | ops_guard_delete.jsonl* 45~51M×5 |
| .runtime/sessions | **240 目录（223 个 >24h 陈旧）** | staging 区文件 623；最老 AI-ARCH-001 陈旧 899h；含误名目录 `--help`（CLI 误用产物） |
| .runtime/gate_cache / reconcile_reports / logs / claim_snapshots / handoffs | 5,783/9.0M、2,170/11M、1,739/15M、858/16M、331/1.1M | 常规在用 |
| pt_20260722015135 + pt_20260722021816 | 1,310 文件 | **7 月遗留**（ec_test_repo0/1 + stash 测试目录） |
| .aidrafts / .worktrees / .aidrafts_pool | 1.2G / 2.4G / 0（locked 空 detached） | 会话隔离区 |
| git stash | **0** | 无悬垂 stash |

## 6. 三线归属核对（令⑥，HANDOFF_v1.md §6 表第 8 行）

### 6.1 dloop 件（st-dloop-20260921，死信 24 个）

唯一文件 34 个，取每文件最新拍 blob_sha256 对 `git show HEAD:<path>` 逐字节哈希比对（路径存在≠内容落地，双口径都做了）：

- **blob==HEAD（真落地）1 件**：fw_backtest.yaml。
- **HEAD 有文件但内容不同（被后续版本覆盖）22 件**：capability 册、in_process_gate 册、noqa_exempt 册、construction_workflow_policy、ROOR、cohort 两 yaml+两 py、tasks/schedule.yaml、scheduler、internal_compute_provider、commit_gates/__init__、daily_loop_master_switch、daily_gate_snapshot、pipeline_events、test_cohort/test_decision_map/test_daily_loop 等。
- **HEAD 无（净缺失）11 件**（全是 state_vocab 族）：state_vocabulary_registry.yaml、state_vocab_registry_gate.py+.yaml、shared/vocab/__init__.py、shared/vocab/market_state.py、test_state_vocab_registry_gate.py、market_state.yaml、vocab__init__.py.yaml、daily_gate_snapshot.yaml、test_daily_gate_snapshot_l2/l5.py。**其中 state_vocab gate yaml+test 两件现已有他线新版本 staged 在飞**（§1 fresh_change）；净缺失实质 9 件只剩 blob（`.runtime/commit_queue/blobs/` 可救）。
- 处置通道：W2 合并器复合键已修，dloop 死信可 requeue 走合并器；但 22 件"被覆盖"类 requeue 前须先判旧快照是否仍有增量价值 → §7-2。

### 6.2 worktree_cleanup 竞态件

事故源头=q-20260922-st-gateaudit-20260922-0002 死信，dead_reason 原文："NOTHING_TO_COMMIT 但快照未真应用（blob 与 old_dev 不符：['docs/01_policies_and_standards/sop/ops_sop/worktree_cleanup_policy.md']）——应用静默丢失，死信回退重新入队（2026-09-15 q-0003 假落地事故防线）"。C2 台账该文件两行（st-gateaudit-0003 + st-gov-closeout-0028）verdict 均=**head_absorbed、NONE_COVERED**。HEAD 现状=ff38b1964c（workclean W8-r2-G4v3，09-21）在册。**结论：竞态件内容已由他会话自家提交平账，无残留动作。**

### 6.3 residual 押后件（st-residual-20260922，死信 16 个）

唯一文件 22 个，同法哈希比对：**blob==HEAD 3 件**（test_td3_trainer/test_session_worktree_audit_wrapper/test_crisis_gate）、**HEAD 有但内容不同 19 件**（ex_sor rl_trainer 四件、crisis_gate.py、apply_market_tables_ddl、residual_resume 两件、capability 册、full-auto-chain 证据件等）、**净缺失 0 件**。押后实质在 `residual_resume/01_plan.md` 波次表白纸黑字：**S1 接线两段等 Max A5 裁定、S6 B21 复跑等净窗**，其余波次 09-22 已执行。归属清楚，无遗失面。

死因分布（16 死信）：GATE-PRECOMMIT-RUN 5、CREATE-GUARD 2、DEPGRAPH-PRE-REGISTRATION 2、MUTABLE-CONST-WITHOUT-FINAL 2、RULING-REFERENCE/ALGO-FLOW-LINK/NEW-FILE-DEPGRAPH/VOCAB-HARDCODE/ORPHAN-MODULE 各 1。

## 7. 需 Owner 批清单（不确定/破坏性/越判读权项，逐项带证据指针）

| # | 事项 | 证据 | 建议 |
|---|---|---|---|
| 1 | t0-revival 3 个未合并提交落地排期 | §3；=已知"t0 合并微班"派发件 | 复职令队列正门消化，无需新裁定 |
| 2 | dloop 22 件"被覆盖"旧快照是否仍有增量价值、9 件净缺失是否回灌 | §6.1 双口径哈希比对 | 走 W2 合并器 requeue 前逐件人工看 diff |
| 3 | 301 个 C2 台账外新增死信 → W8 处置清单扩表 | §2 对账 | 按 C2 同款分诊流程补账后处置 |
| 4 | data/c4_pdf_cache/ 60,245 文件 + grid_*×11 + 散件 untracked 归属（gitignore 登记 vs 纳管） | §1 判读器 JSON | c4_pdf_cache=缓存区应 gitignore；散件逐簇归线认领 |
| 5 | CRLF 治本：写盘工具 newline 口径统一 + 8,534 文件存量归一是否做 | §4 | 先治写面（防再污），存量归一单独排窗 |
| 6 | .runtime 大扫除额度：tmp 12G（bizmine 8.9G）/ feature_flags.jsonl 1.3G / drift quarantine 1,983 目录 / 7 月 pt_* 遗留 | §5 表 | 按保留期分档批（机械可证=可自动；"未来无用"=逐项批） |
| 7 | 223 个陈旧 session 目录 + 623 staging 文件 TTL 清扫 | §5 | 24h TTL 机械 sweep + 白名单 |
| 8 | AGENTS.md staged 改动：机器判 stale_rollback vs HANDOFF §6.5"待 Owner 批"冲突 | §1 交叉提示 | 人工定夺，两说取一 |
| 9 | CAS tmp 残留 9 件删除（6 件写入 pid=ZCode.exe 宿主活进程，不能按 pid 机械判死） | §1 | mtime>24h 且内容与 HEAD/staged 无差异者可删，逐件核后批 |
| 10 | 分支/远端机械清理批：14 条已合并分支（先拆各自 worktree）+ origin/backup 备份分支 + origin/dev push 补齐（落后 244+） | §3 | 一揽子打包一个裁定 |
| 11 | fresh_change 中 3 件归属不明（fail_open_register.yaml / implementation_plans/index.md 判读异常 / docs/library/pipeline.md） | §1 | 撤到活跃会话认领或 Owner 判 |

## 8. 方法与证据文件

- 冷启动：Python 3.12.8 PATH 修正；reaper 活性确认（last_run 2026-09-23 02:10:30）；lock_files cleanup 顺手清了死会话 st-ulib3-20260922 的 3 个死锁（残留在案=本盘点活体样本）。
- 判读工具：scripts/governance/classify_workspace_wip.py（#ARCH-308 B1 官方判读器）；死信对账=纯脚本逐 JSON 解析；行尾=`git ls-files --eol`；哈希比对=sha256(git show HEAD:path) vs 死信 blob_sha256。
- 本会话零删除零修改；唯一写面=本报告 + creation_token 登记（CREATE-GUARD 7 格式覆盖要求，`create_guard.py:167 _OTHER_FORMAT_EXTENSIONS` 含 .md）。
- 证据留档（.runtime/tmp/）：cleaninv_git_status.txt（61,127 行全量）、cleaninv_wip_classify.txt/.json、cleaninv_queue_status.json、cleaninv_deadletter_recon.json、cleaninv_eol.txt、cleaninv_crlf_files.txt（8,534 行）。

## 9. 本件落地记录（如实登记，含一次死信）

1. 02:53 首批入队 q-20260923-st-cleaninv-20260923-0001（本报告+capability 册 token 行两件）→ **死信**："[landing] 注册表三向合并失败（死信回退人工）：ours 同侧身份键重复: file=src/zephyr/data/alerter.py"。机械定性：HEAD 中该文件两条目 token 不同（HEAD 行 7425=auto-data-alerter-20260706 / 行 7429=auto-data-alert-channel-20260723），复合键 (file,token) 下唯一不冲突 → **当时跑合并器的是旧版 file 单键身份**（W2 热修版在 staged 面未被 daemon 生效），与 HANDOFF §3 q-0079/0080 死锁同类。非本批内容问题，死信留作 Lane A/Lane 0 判据（同 q-0079/0080 先例），不 requeue（确定性再死）。
2. 处置：本件改走纯报告批落地（CREATE-GUARD 读盘面注册表，token 行已在盘）；token 行留 staged 面随注册表解冻批（Lane A 正式批发射/Lane 0 下轮外科批）落地。
3. 教训补一句（本轮实证）：safe_write_text 默认 newline 落 CRLF（git add 时告警实证），显式 newline='\n' 后归零——§4 根因当场复演一遍。

## 10. 深清执行记录（st-deepclean-20260923，Owner 全批 §7 后机械处置）

> 执行窗 2026-09-23 13:40–15:00。基线 HEAD=66e6b31346→371bc6e6d1（窗内队列落地 ailayer 批）。全程"破坏动作前机械判据+可逆归档"：G 盘归档总仓=`G:/backup/working_vault/env_cleanup_20260923/`（9.5G，含 sha256 清单）。

| 块 | 处置 | 前→后 | 判据/去 向 |
|---|---|---|---|
| A 分支 | 15 条已合并分支 `git branch -d` 全数删除（含 master 陈旧祖先链）；origin/dev push 补齐 307 提交；origin/backup 删支 | 本地 20→5 | rev-list 独有提交=0 机械验证；-d 自带未合并拒删闸 |
| B worktree | 11 棚拆除（8 零 dirty 直拆 + 3 棚 569 dirty 文件先归档后 --force 拆） | 16→6 | 保留 5 棚均有名有据：t0-revival=微班在办(3 独有提交)、secbuild=待 merge(2 独有提交)、combine=棚内 pf_alloc 未落地实体(5 件 dev 无+allocation 三件大段独有行)、pool/serializer=基建禁碰 |
| C 暂存区 | 官方判读器现测三分：derived 466 全还原（watchdog 可再生）；stale 450 staged 摘除+content==HEAD 还原；真改动 266 保留 | 追踪脏 938→284 | `restore --staged` 构造零丢失；266 件历史 blob 全史无匹配=真独有，归属登记见 §10.1 |
| D CRLF | ①写面治本：file_utils atomic_write/safe_write_text 默认 newline 翻 `"
"`（旧阴性护栏 09-19 车道未授权锁 None，本批 Owner §7-5 授权翻转为正向护栏锁 LF，47 测试绿+行为探针过）；②存量归一：7,876 干净件索引 blob 重写 | w/crlf 7,989→12、w/mixed 10→0 | 余 12 件=处置时在飞真脏件，随批次走新写面自然归一；重写只动"完全干净"件，内容字节级等同（cmp 验证） |
| E .runtime | bizmine 8.86G→G 盘；quarantine 303M→G 盘清零；audit 轮转件 150M+drift watchdog 88M→G 盘；sessions 227 陈旧→G 盘 | tmp 9.3G→350M；sessions 254→27 | feature_flags.jsonl 1.43G 活句柄在写不可搬=留待停窗轮转；gate_audit 未获点名不越界；pt_* 已由前序会话消 |
| F 死信 W8 | 505 封归档 `dead_archive_w8_20260923/`（absorbed 19/expired_derived 72/content_dead 407/继主 nightfix 7），manifest JSONL 在档 | dead 582→77 | 吸收判定=blob EOL 归一哈希 vs HEAD 逐封；余 77=活属主争议面不代修：ulib3 50（有在飞 processing+claim 在手）、combine 17、nightfix 10——若 Owner 判 ulib3 僵尸，一条命令可再归档 |

### 10.1 真改动归属登记（待 Owner 点名，266 件簇谱）

| 簇 | 件数 | 推断属主/战役 |
|---|---|---|
| scripts/governance 族（batch_creation_tokens W4 宽前缀防呆+38 行等） | ~60 | 注册表事故 W4 治本套件（laneA/夜手术线） |
| config/*.yaml 17 件（ai_search_veins/switch_criteria 等，未跟踪） | 17 | ailayer/夜班新增策略册（队列 blob 有快照） |
| docs/03_modules 蓝图挂图+trading_map 8 件 | ~40 | tdm20/wm1-buildB 在飞 |
| src/zephyr 未跟踪新源码 76 件+tests/ai_layer 60 件 | 136 | ailayer 批次（队列 q-0028/29 落地中，盘面件随之转正） |
| docs/_working 战役册 106 件 | 106 | 各战役交付物（byte 级未落地部分） |
| backtest/ibt/sim 族 | ~15 | ibt-remedy/sim-launch 尾件 |

全量机器清单=`.runtime/tmp/deepclean_C_disposition.json`（true_unique 266 条含逐件路径）。处置原则：一件未删，全部留在盘面原位等属主批次吸收或 Owner 点名。

### 10.2 判不了停手项（如实登记）

1. st-combine 棚保留：pf_alloc 接线实体与 tdm20 已落 AGG 批是并行施工关系，语义归属需属主裁定。
2. feature_flags.jsonl 1.43G：活进程写句柄，Windows 不可搬；建议停窗轮转。
3. ulib3 50 封死信：lock 系统判其 claim 有效（未过期），但其 session 目录已 >24h 陈旧被本批按 TTL 归档——半活状态唯 Owner 可裁。
4. 266 件真改动中 trading_map 8 件 mtime≥HEAD=有会话正在写（fresh 19 件同理），未做任何处置。
5. **【结构性发现】registry_incident_20260922/ 全目录从未落 HEAD**（DISPATCH_v1/HANDOFF_v1/c1/c2 取证件皆盘面态，git log --all 空）：R5-DIGIT-SUFFIX 对日期后缀目录结构死锁——任何触碰该目录的队列批必死信（本班 q-0001 实证，gslim q-0015 先例同根）。该目录是注册表事故链的真源载体，全会话实际按"盘面即真源"运转一日余。按 trae_028 L1242 存量另案（改名如 registry_incident/ 归 Owner 裁量，rename 须 depgraph --force 同批）；本班 DISPATCH 越界登记行已写入盘面版，随另案一并落。
