---
ttl: task_bound
completes_when: "全部 24 面六列实证图建成 + 三件特别项结论 + 无轮转面 30/90 天外推 + 复算命令清单落盘"
sid: st-fclean3-20261012
lane: lane_consumers
scope: read-only
date: 2026-10-12
note: 案卷不出裁定；零删除/零 commit/零改码。四态仅给倾向+证据等级(E1实测/E2单点/E3推断)。
---

# lane_consumers — `.runtime` 工令未点名附属物面 · 读者/写者/轮转实证图

> 判据：活写者=基础设施不可碰｜有读者=归档不删｜零写∧零读=退役候选｜有写∧无读∧无轮转=无限增长债。
> 教训内化：①"有机制"须实测"谁调/能否改行为"；②单路径消费=YAML 审计面生效/提交面空转→指 file:line；③判"未知读者"先减观测者自节拍（自我观测不算真读者）。

## 0. 复算环境 + 漂移（apparent MB vs 总包 2026-10-11 23:2x）
HEAD=`dev`，python 3.12.8。计件=`find -type f|wc -l`，体积=`find -printf %s` 求和（apparent，非 du：du 对碎文件因簇开销虚高，如 retired_lanes du=86.9MB vs apparent=12.9MB）。

| 面 | 件(基线→重测) | MB(基线→重测) | 最新 mtime | 静默 |
|---|---|---|---|---|
| gate_audit | 401→403 | 1279.9→1281.00 | 10-12 00:18 | 活 |
| audit | 29→29 | 475.4→481.44 | 10-12 00:19 | 活 |
| claim_snapshots | 935→937 | 22.3→22.36 | 10-12 00:12 | 活 |
| retired_lanes | 35095→35095 | 12.9→12.91 | 09-24 17:20 | 17d |
| campaign_trash_20261001 | 1063→1063 | 47.9→47.87 | 10-02 09:40 | 10d |
| fetch_perf | 53→54 | 34.9→34.96 | 10-12 00:18 | 活 |
| sessions(481 子目录) | 550→551 | 32.2→32.45 | 10-12 00:19 | 活 |
| logs | 419→420 | 18.2→18.26 | 10-12 00:18 | 活 |
| session_registry_audit | 2→2 | 16.1→16.09 | 10-11 23:31 | 活 |
| depgraph_scan_cache.json | 1 | 10.5→10.70 | 10-12 00:18 | 活 |
| lookup_audit | 860→861 | 3.2→3.22 | 10-11 23:23 | 活 |
| reconcile_reports | 997→1002 | 3.0→3.00 | 10-12 00:17 | 活 |
| ops_notifications | 2→2 | 10.3→10.35 | 10-11 23:26 | 活 |
| drift_watchdog | 5→5 | 9.9→9.88 | 10-12 00:18 | 活 |
| evaporation_blackbox | 1 | 8.0→7.96 | 10-12 00:16 | 活 |
| _scratchbt2 | 6468→6468 | 3.6→3.62 | 09-24 17:10 | 18d |
| worktree_ops_log.jsonl | 1 | 3.5→3.53 | 10-12 00:12 | 活 |
| takeover | 488→488 | 2.8→2.82 | 10-11 18:09 | 6h |
| gate_cache | 2571 | 0.2→0.18 | 10-11 02:51 | 21h |
| locks | 215 | ~0 | 10-11 23:31 | 活 |
| .runtime/.runtime(嵌套) | 3 | ~0 | 10-09 04:37 | 3d |

漂移结论：与总包一致（件数因并发工单微增 1-5，MB ≤+6）。**三碎文件面静默>10d=退役候选信号**（retired_lanes/_scratchbt2/campaign_trash）。

---

## 1. 逐面六列（实证）

### gate_audit（活基础设施，E1）
- 写者：中心 AuditWriter `src/zephyr/gov_audit/writer.py:75`；各门直写经 `src/zephyr/shared/io/audit_jsonl_writer.py`（append_audit_jsonl）：`ai_layer/redline/negative_list_gates.py:145`、`drop_gate.py:92`、`ai_secret_exposure.py:101`、`session_env_guard.py:63`、`governance/audit/reconciliation_registry.py:9809`、`registry_projection/projection_generator.py:66`。触发=**事件**（每次 commit/gate 开火）。
- 读者（真读者，改行为）：`governance/audit/commit_gateway_abuse_monitor_reconciler.py:488,521`（读 allow_overlap_usage.jsonl/force_merge_usage.jsonl 计数→升级阻断）、`git_guard_bypass_reconciler.py:87`（读 git_guard_self_harm.jsonl）、audit_chain_verifier。
- 轮转：**有** — `audit_jsonl_writer.py:81 rotate_if_oversized(max_bytes=DEFAULT_MAX_BYTES)`，超限 `_rotate` 产 `.1/.2/.3`（实测 test_source_consistency_foreign_staged.jsonl.1=126MB、ops_guard_delete.jsonl.1/.2/.3≈52MB/枚）。单文件封顶，总 1.28GB=多文件×备份副本。
- 引用：`config/governance_operations_map.yaml`（每门 gate_audit 计数，~250 行）、`dev_delivery_map.yaml` 多处点名。
- 倾向：**活基础设施**。禁碰；1.28GB 是"有界但巨大"，缩容属轮转参数议题（需 Owner，不在本判据）。

### audit（活基础设施，E1）
- 写者：`rule_bridge/write_audit_daemon.py`（write_audit.jsonl）、safe_write CAS 日志、worktree_drift_watchdog.jsonl、bottleneck_ledger，同经 audit_jsonl_writer。触发=事件/守护。
- 读者：审计链取证。轮转：**有**（实测 .1/.2/.3 副本）。倾向：**活基础设施**。

### claim_snapshots（活基础设施，E1）
- 写者：`rule_bridge/git_commit_gateway.py:250` `_CLAIM_SNAPSHOTS_DIR`，`:1805` 写 `<sid>.json`，`:1735` `{sid}_adopted.jsonl`；`scripts/git_commit.py:711`。触发=事件（commit/claim）。
- 读者：`worktree_drift_watchdog.py:289`、`coordination_state_board.py:536`（算 stale_claim_snapshots）、`replay_gate_verdicts.py:111`、`commit_gates/foreign_change_gate.py`。
- 轮转：**有** — `worktree_drift_watchdog.py:729,785` 删死会话 `<sid>.json`。倾向：**活基础设施**。

### retired_lanes（可退役候选，E1）
- 写者：**零**（`grep --include=*.py/*.ps1 src scripts`=0 命中）。一次性工单产物。最新 mtime 09-24（静默 17d）。
- 读者：**零代码**；仅 docs 台账概念级点名（branch_zero_takeover 等）。轮转：无。
- 倾向：**可退役候选**（35095 件碎文件，零写零码读=机器不可再生？—内容需属主确认，禁抽样）。

### campaign_trash_20261001（可退役候选，E1）
- 写者：**零代码**；10-01 campaign 显式废纸袋（本身即"已判可弃"暂存）。静默 10d。读者：零。轮转：无。
- 倾向：**可退役候选**（名为 trash；需确认为非墓碑复活窗持有）。

### fetch_perf（可归档／增长债，E2）
- 写者：`src/zephyr/data/fetch_perf_recorder.py:41,62`；调用方 `scheduler.py:2295 _record_fetch_perf`（每任务结束）。触发=事件（调度）。
- 读者：**无程序化读者** —— 该 jsonl 仅被 `src/zephyr/data/config/known_data_gaps.yaml:701,1474` 作为**取证证据**人工引用；api 侧另有 DB 表 `c0_meta.fetch_perf`（speed_tester 写，非本面）。
- 轮转：**无**（日文件 fetch_perf_YYYYMMDD.jsonl 不删旧日）。外推：7d=8 件/2.98MB→~0.43MB/日 → **30d≈+13MB，90d≈+38MB**。倾向：**可归档**（活写无码读无轮转=增长债）。

### sessions（活基础设施＋孤儿壳债，E1）
- 写者：`rule_bridge/heartbeat_daemon.py:148` heartbeat.jsonl（守护 30s 一跳）；`session_worktree.py:1844` staging；`apply_resource_plan.py` archive。
- 读者（真读者=活性判定）：`scripts/commit_queue.py:2036`、`scripts/lock_files.py:166`（心跳窗内豁免 stale）、`process_reaper.py:441`、`coordination_state_board.py:455`、`session_takeover_ledger.py:744`。
- 轮转：**部分** — `heartbeat_daemon.cleanup_heartbeat_file:418`（merge/abort 删心跳）、`_tasks/session_closeout_reconciler.py:414`（会话目录 mv→sessions_archive/<YYYY-MM>/）、staging TTL `git_commit_gateway.py:1904`（>24h）。
- 倾向：**heartbeat=活基础设施**；但见 B2 孤儿壳 468 个 → closeout 未清空，需核运行态。

### logs（活基础设施，E2）
- 写者：守护/采样（`config/resource_profile_registry.yaml:2248 .runtime/logs/resource_samples/`）。轮转：`gov_audit/log_rotation.py` 仅覆盖 logs/mcp_audit，**其余子目录轮转未逐目录核**（申报剩余）。倾向：**活基础设施**。

### session_registry_audit（活基础设施／自我观测警，E2）
- 写者：`src/zephyr/security/access_control/session_concurrency.py:860,900`（register_rate_guard.jsonl / register_reanimation.jsonl）。
- 读者：**同模块** `:2048` 读自身审计做 verdict 去重 → **自我观测**（写读同子系统的 borderline），非外部独立读者。轮转：无，单 jsonl 16MB 递增。倾向：**活基础设施**（消费者自观测，慎判"未知读者"）。

### depgraph_scan_cache.json（活基础设施，E2）
- 写者/读者：`src/zephyr/trading/decision_map.py:98 _DEPGRAPH_CACHE`（path→blueprint_id 派生缓存，缺失记 warning）；`:485` 读回退。触发=depgraph 生成/决策图查询。倾向：**活基础设施**（派生缓存，可再生）。

### lookup_audit（活基础设施／件数债，E1）
- 写者：`governance/capability_lookup.py:110,331 write_lookup_audit_log`、`integration/mcp/rule_discovery_server.py:77,152`、`library/lookup.py:382`、`library/ruling_precedent.py:235`。触发=反查调用。
- 读者（真，改行为）：`reconciliation_registry.py:10747-10749` CAPABILITY-LOOKUP-HEALTH（空→判 gate 静默失效告警）。
- 轮转：**无**（每会话/调用一文件）。外推：7d=157 件→~22 件/日 → **30d≈+660 件，90d≈+2000 件**；字节小(~+5MB/30d)。倾向：**活基础设施**＋件数/簇债。

### reconcile_reports（活基础设施／件数债，E2）
- 写者：`reconciliation_registry.py:1517,2026,5140,6283`、`reconcile_worker.py:600`、`reconcile_runner.py:127 _REPORTS_SUBDIR`。触发=事件（post-commit reconciler）。
- 读者：`commit_gateway_abuse_monitor_reconciler.py:393`（读 post_commit_guard_*）。
- 轮转：**未见显式 prune**（oldest 仅 10d，但 683 件/7d≈97 件/日累积）。外推：**30d≈+2900 件**。倾向：**活基础设施**＋件数债（无 prune 证据）。

### ops_notifications（活基础设施，E1）
- 写者：`system_telemetry/alerts/ops_alert_feed.py:74` notifications.jsonl，经 `safe_write_text` **CAS 全量重写**（`:474`，非 append→不无限增）。
- 读者（真）：`src/zephyr/frontend/dashboard/api_server.py` `/api/ops-notifications` 端点+前端横幅轮询（模块 [CONSUMERS] 头 line5-6）。
- 轮转：重写=有界。倾向：**活基础设施**。

### drift_watchdog（活基础设施，E1）
- 写者：`rule_bridge/worktree_drift_watchdog.py`（boot 永久服务；计划任务 `sch_worktree_drift_watchdog`=`scripts/tasks/register/register_drift_watchdog_task.ps1`；`process_reaper.py:226` 保活）。触发=计划任务+事件。
- 轮转：**有** — `worktree_drift_watchdog.py:425 rotate_if_oversized`。倾向：**活基础设施**。

### evaporation_blackbox（可归档／增长债，E2）
- 写者：`scripts/governance/evaporation_blackbox.py:90,29` blackbox.jsonl（行车记录仪，schtasks 载体追加快照）。
- 读者：仅 `--restore` 自读=**自我观测**；无外部活消费者命中。轮转：无，单文件 8MB 递增。倾向：**可归档**（治理取证 dashcam，活写自读无轮转）。

### _scratchbt2（可退役候选，E1）
- 写者/读者：**零代码**。scratch 回测目录，静默 18d。倾向：**可退役候选**（6468 件）。

### worktree_ops_log.jsonl（活基础设施，E2）
- 写者：`scripts/governance/audit_worktree_ops_telemetry.py:23`（遥测 session_id/file/hash/backup）。触发=worktree 操作。轮转：单文件未核。倾向：**活基础设施**。

### takeover / takeover_ledger.jsonl（活基础设施，E1）
- 写者：`scripts/governance/session_takeover_ledger.py:92,650,651`（takeover_ledger.jsonl + takeover/resolved + salvage/sweep 日志）。
- 读者（真，改行为）：`commit_gates/takeover_pending_gate.py`（L3 硬阻断门 load_open_entries）、`session_concurrency.py` _salvage_takeover_ledger。轮转：resolve 迁 resolved/。倾向：**活基础设施**。

### gate_cache（活基础设施，E1）
- 写者：`rule_bridge/gate_cache_preflight.py:131 _CACHE_DIR=.runtime/gate_cache`（TTL 10min，只存 passed=True）。注：另有 `scripts/governance/observability/gate_cache.py:63`→`data/gate_cache`（**不同面**，勿混）。轮转：TTL 自失效。倾向：**活基础设施**（可再生缓存）。

### locks（215）/ 根 .ailocks（97）（活基础设施／需核双轨，E2）
- `.runtime/locks`：heartbeat_*.pid（lock_files/heartbeat 写）。`.ailocks`：claim 锁轨——`coordination_state_board.py:573` 读 `.ailocks/registry.json`。两者**角色不同**（pid/心跳 vs claim registry），非纯重复；双轨疑点存疑→**需核**（不在本判据裁定）。倾向：均**活基础设施**，双轨收敛属 Owner 议题。

---

## 2. 三件特别判清项

### B1 嵌套 `.runtime/.runtime`（可退役候选／机器残留，E1）
- 溯源：内含 3 件皆 heartbeat/lock 产物（sessions/<sid>/heartbeat.jsonl + locks/heartbeat_*.pid），由 `heartbeat_daemon.py:148` 与 lock_files 以 **project_root 相对参** 落笔——当调用方 cwd 落在 `.runtime` 内时解析成 `.runtime/.runtime/...`。**注**：`autonomy_core/killswitch_response_levels.py:123 runtime_dir=Path(".runtime")` 经核是 **docstring 用法示例非执行码**，真例化 `boot_hooks.py:632` 用绝对 `REPO_ROOT/".runtime"`——非元凶，如实排除。另 `scripts/data/board_index_realtime.py:58` 用 `os.path.join(__file__/../../.runtime,...)` 相对拼接（正解到固定根，非本 bug 但同类风险）。**精确 file:line 触发点未定位（申报剩余）**。
- 重复性实测：`st-gateaudit` 嵌套 heartbeat=364b vs 正主=45112b（**非重复，残缺快照**）；`st-deadcure` 正主 session 目录**不存在**、仅嵌套 210b；`locks/heartbeat_st-deadcure...pid` 嵌套=正主=5b（**字节重复**）。
- 倾向：**可退役候选**（残缺/重复的死亡残留，非权威审计面，机器可再生）。

### B2 481 session 目录孤儿壳（E1）
- 在册数：`.runtime/session_registry.json` 顶层即 sid，实测 **13 个 live**；目录数 **481**；差集=**468 孤儿壳**。
- heartbeat.jsonl **有真读者**（reaper/lock_files/coordination board/takeover ledger 判活）→ heartbeat **非**纯自观测，是活基础设施信号源；但 468 死会话目录的残留 heartbeat=已死会话遗物。
- 清理机制**存在**（`session_closeout_reconciler.py:414` 归档 + `heartbeat_daemon.cleanup_heartbeat_file:418`）但显然**未清空**（累积 468）→ 属主活性需核该 reconciler 是否在册运行。孤儿壳=机器可再生的活性残留（心跳文件），非独立审计面。倾向：**可退役候选（孤儿壳）**＋**需核 reconciler 活性**。

### B3 predictions_v1_backup_1971.jsonl（可退役候选／归因失败，E2）
- 内容实测：akshare_research_report 情绪记录，publish_date 全为 2026-02-23；mtime 2026-08-25。
- 写者：`grep -rn "predictions_v1" src scripts`=**0**；全仓 `predictions_v1` 仅命中 `.gitignore:355 data/eval/zero_shot_predictions_v1_thinkoff.jsonl`（**不相关文件**）。
- 结论：**1971 无法归因到任何 file:line**——无任何在册代码构造 `predictions_v1_backup` 文件名。1971 是经典 epoch-0 年（`fromtimestamp(0)`）特征，但仓内无可复现代码路径，判定为**人工/一次性 ad-hoc 命名的孤儿件**，非在册格式化 bug，亦非有意哨兵（无引用无读者）。倾向：**可退役候选**；如实申报"bug vs 哨兵"=证据不足以二选一（禁臆断）。

---

## 3. 散文件与空壳目录面（部分申报剩余）

### C2 根下 69 个零文件空壳目录（可退役候选，E1）
- 实测 `for d in .runtime/*/; do find "$d" -type f|head -1; done` 零内容计数=**69**。含 pytest_tmp*/tmp_pytest/pytest_cache*（**20** 个，违反"测试隔离：输出一律 tmp_path"红线）、*_backup（_boot002/ai12/ai_dc2_05/night001_akshare/stale_untracked/tracker246）、stash_archive、recycle_bin、_kimi3_checks、_senti_wtest。
- 零写者∧零读者（0 文件）→ 倾向：**可退役候选**。

### C3/C4 散文件（E2，多数逐行 file:line 未定位=申报剩余）
- `worktree_ops_log.jsonl`=audit_worktree_ops_telemetry 遥测（活）。`boot_sla_probe_report.jsonl`=`run_boot_sla_probe.py:48` 探针报告（活，读者疑仅自报告）。`board_idx_offset.txt`=`board_index_realtime.py:58`（活）。`depgraph_scan_cache.json`=decision_map 缓存（活）。
- 未逐行定位写者（grep 变量拼接未命中字面量，申报剩余）：`git_performance_log.jsonl`、`workspace_drift_warn.jsonl`、`algoflow_progress.jsonl`、`algoflow_skipped.jsonl`、`*_last_attempt`×3、`archive_watchlist.json`、`.probe_95036.tmp`、`takeover_ledger.jsonl.tmp.23876`（原子写 os.replace 残 tmp）、`backup.lock`、`reconcile_launch.lock`、`registry_ledger`(94，PG schema 名同名需辨)、`handoffs`(260，`generate_architecture_context.py:126` 读=有读者)、`registry`/`derived_dirty`(3)、`pt_20260722015135`(1255 件，7 月孤儿)。
- `pt_20260722015135` 及 3 枚 `pt_*`（015121/015135/021816）= 7 月同刻 pytest_tmp 系列，静默>80d → **可退役候选**（同 pytest 隔离红线违规）。

---

## 4. 汇总

### D1 四态分组（件数＋apparent MB；仅本面清单覆盖项）
- **活基础设施（禁碰）**：gate_audit 403/1281.0、audit 29/481.4、claim_snapshots 937/22.4、sessions-heartbeat 551/32.5、lookup_audit 861/3.2、reconcile_reports 1002/3.0、ops_notifications 2/10.35、drift_watchdog 5/9.88、takeover 488/2.82、gate_cache 2571/0.18、locks 215/~0、.ailocks 97、depgraph_scan_cache 1/10.7、worktree_ops_log 1/3.5、logs 420/18.3、session_registry_audit 2/16.1、boot_sla_probe、board_idx_offset ≈ **1017 件 / 2095 MB**。
- **可归档（活写·弱/无码读·需保序）**：fetch_perf 54/34.96、evaporation_blackbox 1/7.96、session_registry_audit(自观测,已计入活)。≈ **55 件 / 43 MB**。
- **可退役候选（零写∧零读 / 死残留 / 静默）**：retired_lanes 35095/12.9、campaign_trash 1063/47.87、_scratchbt2 6468/3.62、嵌套 .runtime/.runtime 3/~0、69 空壳目录 0/0、pt_20260722015135 1255、predictions_v1_backup_1971 1/0.38、3×pt_*。≈ **43,953 件 / ~65 MB**。
- **需 Owner／需核**：locks∧.ailocks 双轨收敛、gate_audit 1.28GB 轮转缩容、sessions closeout reconciler 活性（468 孤儿未清）、reconcile_reports/lookup_audit 无 prune 件数债。

### D2 无轮转面 30/90 天外推（仅真·活写无轮转；rotation-bounded 面因轮转刷 mtime 不外推）
| 面 | 增速 | 30d | 90d |
|---|---|---|---|
| fetch_perf | ~0.43MB/d | +13MB | +38MB |
| lookup_audit | ~22 件/d | +660 件/~5MB | +2000 件/~15MB |
| reconcile_reports | ~97 件/d | +2900 件/~7MB | +8700 件/~21MB |
| session_registry_audit | 单文件递增 | +?MB(线性待核) | +? |
| evaporation_blackbox | 单文件 8MB/递增 | 待逐日核 | 待逐日核 |

### D3 复算命令清单
```
# 漂移/件数/体积
find .runtime/<面> -type f | wc -l
find .runtime/<面> -type f -printf '%s\n' | awk '{s+=$1}END{print s/1048576}'
find .runtime/<面> -type f -printf '%TY-%Tm-%Td %TH:%TM\n'|sort|tail -1
# 7d 增速
find .runtime/<面> -type f -mtime -7 -printf '%s\n'|awk '{n++;s+=$1}END{print n,s}'
# 零写/零读确认
grep -rn --include=*.py --include=*.ps1 -E "retired_lanes|campaign_trash_20261001|_scratchbt2|predictions_v1" src scripts
# 孤儿壳差集
python -c "import json;print(len(json.load(open('.runtime/session_registry.json',encoding='utf-8'))))"
find .runtime/sessions -mindepth 1 -maxdepth 1 -type d | wc -l
# 空壳
for d in .runtime/*/; do [ "$(find "$d" -type f|head -1)" = "" ] && echo "$d"; done | wc -l
# 双轨
find .ailocks -type f|wc -l; find .runtime/locks -type f|wc -l
# 计划任务（PowerShell 通道，勿 Git Bash 吞 /）
powershell -NoProfile -c "Get-ScheduledTask -TaskName *drift_watchdog*,*evaporation*"
```

### D4 三件特别项结论（倾向，非裁定）
- B1 嵌套 .runtime = 相对路径 cwd 落 .runtime 的 heartbeat/lock 残留，内容残缺/字节重复，**可退役候选**；精确触发 file:line 未定位（剩余）。
- B2 481 目录 vs 13 在册 = 468 孤儿壳；heartbeat 有真读者故活基础设施，但死会话残留待 closeout reconciler（运行态需核）。
- B3 predictions_v1_backup_1971 无任何在册写者/引用，1971 不可归因 file:line，**可退役候选**；"bug vs 哨兵"证据不足，不臆断。

## 5. 申报剩余（未穷尽项）
1. 散文件写者 file:line：git_performance_log / workspace_drift_warn / algoflow_* / *_last_attempt×3 / archive_watchlist / registry_ledger(.runtime 94) / handoffs(260) 写侧 / derived_dirty / backup.lock / reconcile_launch.lock / .probe_95036.tmp / tmp.23876 —— 字面量 grep 未命中（疑变量拼接），未逐个定位。
2. logs 子目录逐目录轮转覆盖度未全核（仅确认 log_rotation=mcp_audit）。
3. 嵌套 .runtime 精确相对根来源 file:line 未钉死。
4. session_closeout_reconciler / evaporation / boot_sla_probe 计划任务在盘态未跑 Get-ScheduledTask 实机确认（内存红线优先保 GPU 工单班 PID 44836，未起额外重进程）。
5. 三碎文件面内容全集是否含唯一审计价值（禁抽样结论）——仅测 mtime 静默信号，未逐件内容判。
