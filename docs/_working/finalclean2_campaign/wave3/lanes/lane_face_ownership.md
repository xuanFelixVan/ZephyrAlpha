---
ttl: task_bound
lane: lane_face_ownership
sid: st-fclean3-20261012
role: read-only investigation lane (zero delete / zero git add / zero write to .runtime root)
completes_when:
  - "每个未建账的 .runtime 顶层面出满六列（写者/读者/轮转/活性/引用/四态倾向），全部实测 file:line"
  - "commit_queue 五子面（pending/done/dead/blobs/worktree）单独建档：写者/读者/轮转"
  - "session_registry 分片面自身的累积判据实测（merge-upsert 永不删 ⇒ 陈旧片数与占比）"
  - "零写者零读者面清单成形（可退役候选真身）"
  - "无轮转面 30/90 天外推表落盘 csv"
  - "复算命令每条自测能跑"
  - "跑不完的部分如实申报剩余（未跑完不算失败）"
north_star: "附属物 63.4GB 存量每面有主有据（Owner 2026-10-12 01:15 通宵令 §〇）"
artifacts:
  face_census_csv: D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_census_20261012.csv
  six_column_csv: D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_six_col.csv
  growth_projection_csv: D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/no_rotation_projection_30_90.csv
  commit_queue_csv: D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/commit_queue_subfaces.csv
  session_registry_shards_csv: 见 §3 专章（逐件名＋mtime 实测在 §3 表内，未另立 csv）
  supporting:
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_files_detail.csv
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_ref_hits.csv
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_code_hits.txt
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_writer_hits.json
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_rotation_class.csv
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_reference_counts.csv
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_two_sample_delta.csv
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_six_col.csv
    - D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/target_faces.json
---

# 车道：`.runtime` 未建账面 逐面归属（写者／读者／轮转／活性／引用／四态倾向）

> 本车道只补**此前没建过账的面**。已完成账面（勿重做）：波三 P1 机生总账
> `../20_wave3_p1_census.yaml`（44 面）、读写者图 `lane_consumers.md`（24 面 + B1/B3 + C2 空壳目录簇 + C3/C4 散件）、
> `lane_quarantine.md`／`lane_deadletter.md`／`lane_tmp_lanes.md`／`lane_untracked_audit.md`／`lane_aidrafts.md`。

## 0. 实测环境与漂移（相对任务书 00:19/01:31 口径）

- 取数时刻：2026-10-12 01:57（本地）；python 3.12.8；cwd=`D:/ZephyrAlpha`（主区只读实测）。
- 顶层面数：**任务书 149 → 实测 102**（80 目录 + 22 文件，`os.scandir` 全遍历，非抽样）。
- 全表面积：**1,026,353 件 / 61.92 GB**（北极星口径 63.4GB 同量级；差值见 §7 漂移解释）。
- 判活铁律：只用 `SessionRegistry(Path("D:/ZephyrAlpha")).list_active_readonly()`；
  禁 `list_active()`（mutating，写接管台账）；禁拿 `.runtime/session_registry.json` 判活（只读兼容副本，允许滞后）。
- 工具红线：全程未对任何在册工具执行 `--help`／裸跑；行为一律读源码确认。

## 1. 差集与覆盖面（待建账面清单）

差集算法＝`ls(.runtime, depth=1)` 全遍历键集合 − 已建账键集合（非抽样）。

| 桶 | 面数 | 件数 | 字节 | 处置 |
|---|---|---|---|---|
| `.runtime` 顶层实测总面 | **102**（80 dir＋22 file） | 1,026,353 | 61.92 GB | 全遍历（`face_census_20261012.csv`） |
| 已由他车道建账（本车道不重做） | 27 | — | — | `tmp`／`quarantine`／`commit_queue`（五子面另立 §4）／`aidrafts`／lane_consumers 24 面含 `.runtime/.runtime` |
| **本车道主面（目录·非空）** | **35** | 1,971（明细见 `face_files_detail.csv`；`pt_*`/`pytest_tmp*` 占 1,325） | ≈2.7 MB＋`guide_reads`/`handoffs` 等小面 | §2 |
| **本车道空壳目录面** | **22** | 0 | 0 | §2-G |
| 根散件（另车道补证据） | 22 | 22 | ≈8.4 MB | 仅列名不裁 |

**漂移（相对任务书 00:19/01:31 口径，必须看）**：
1. 顶层面数 **149 → 102**：差 47＝本轮 46 个零文件目录真删＋1 面再消失；实测残留零文件壳 **22** 个（任务书说"46 已删"，剩余 22 未删，本车道接手判活）。
2. `campaign_trash_20261001` **1,063 件/47.9MB → 100 件/1.6MB**：不是"被处置"，是被 **TTL 清理引擎在吃**（删除审计末段两次采样 8,806／8,932 次命中该面），见 §2-E。
3. `guide_reads` **145 → 96**、`locks` 217、`handoffs` 263：本车道两次量测间隔 10 分钟内被删 49/70 件（审计计数印证），即"活写手＋活清道夫"同面对打。
4. `session_registry` **17 片 → 26 件**（18→20 个 `.json` 片＋**8 个 `.tmp` 残件**），见 §3。
5. `reconcile_reports` 1,002→1,009、`audit` 452MB、`tmp` 51.1GB 持续在长（他会话在飞，属保护面）。
6. 北极星 63.4GB vs 实测 61.92GB：差 1.5GB 主要是 `campaign_trash_20261001` 被 TTL 吃掉＋`tmp` 内 `.jsonl` 保护件净增的净值波动；**逐面对账见 §7**。
7. **02:20 收尾复测（本车道自证"面在动"，非静态账面）**：顶层仍 102 面（80 dir＋22 file，零新增零消失），
   但 `handoffs` 263→**194**、`locks` 217→**159**、`session_registry` 29→28（`.json` 21→20 与 `list_active_readonly()` 同步降）、
   `reconcile_reports` 1,009→1,017、`blobs` 26,342→26,349 件（涨）；`guide_reads` 稳定 96、`registry_ledger` 稳定 94、
   `campaign_trash_20261001` 稳定 100、`_scratchbt2` 稳定 6,468。
   ⇒ 判读：**删除面与增长面同时活跃**，本车道所有件数都是时点值，引用时必须带 §0 取数时刻。
   `locks` 一轮少 58 件＝**归因未定**（两把可能：①GATE-RUNTIME-CLEANUP 7d TTL，末段删除审计确有 62 次命中 `locks`；
   ②`lock_files.py cleanup` 的 30 分钟 claim TTL——`DEFAULT_TTL_S=1800.0` `scripts/lock_files.py:98`，判定 `:238-243`）。
   两把都经 `guard_remove`/删除通道，本车道**未做归因区分**（列剩余申报 §9-6）；
   但无论哪把，结论都指向同一条：**claim/锁件的终态由自动通道决定，施工中的车道不掌握自身 claim 的生命周期**——呈总包注意，不呈裁定。

## 2. 逐面六列（主体，实测；分组＝四态倾向）

证据等级：**甲**＝写者/读者 file:line 双点实测；**乙**＝单点实测＋派生推论；**丙**＝仅盘上形态/引用面观测。

### A 组·活基础设施为主（19 面｜598 件｜2.62 MB；其中 `registry_ledger` 的⑥判"可归档"，列此供读写者对照）

| 面 | 件/字节 | ①写者（file:line＋触发形态） | ②读者（file:line；真读者 vs 自我观测） | ③轮转 | ④活性（mtime/静默/心跳） | ⑤引用（code/_working/catalogs/ruling/rules） | ⑥倾向＋证据 |
|---|---|---|---|---|---|---|---|
| `session_registry` | 26 件/10.2KB | `session_concurrency.py:1007` `_write_shard_only`（per-pid tmp＋os.replace＋WinError5 退避）；事件＝register/heartbeat/claim（会话动作） | **真读者**：`session_concurrency.py:1800`（`_iter_shards` glob `*.json` 聚合）、`_diff_helpers.py:562`（own-scope 判定）、`session_takeover_ledger.py:95`；`.tmp` 后缀**零读者** | 片随 `unregister`/收割 `_delete_shard`（`:1029/:1048`）删除＝**不累积**；`.tmp` 残件**无任何清理代码**（`:1025` 仅同进程异常兜底 unlink） | mtime 02:02（心跳节拍）；静默 0.0d；18→20 个 json 片与 `list_active_readonly()` 18 活会话逐一对齐 | code=31 `_working`=58 catalogs=3 rules=7 | 活基础设施（**活性真源本身**）＋`.tmp` 残件＝可清死面；甲 |
| `abuse_monitor` | 1 件/2.5KB | `commit_gateway_abuse_monitor_reconciler.py:248`（baseline 路径）；post-commit 事件（priority=880 注册，`git_commit_gateway.py:1943` 同族） | **真读者**＝同 reconciler 读回 7d baseline（自持状态，非自我观测）；报告另落 `reconcile_reports/commit_gateway_abuse_monitor_*.json`（n=69，newest 00:56） | 无 rotate；单文件幂等覆写（不增长） | 00:56，静默 0.0d；节拍＝每次 commit | code=4 rules=4(trae_069 `_line 197/198/221/289`) | 活基础设施；甲 |
| `ai_error_patterns` | 1 件/96B | `error_pattern_consumer_reconciler.py:25`（聚合输出）；post-commit 事件 | **真读者**：`session_worktree.py:8476`＋`ai_error_pattern_library.py:382`（加载库供门位判定） | 全量重扫覆盖式幂等（不增长；现 96B＝聚合空/近空） | 00:56，静默 0.0d | code=8 `_working`=3 | 活基础设施；甲 |
| `cache` | 24 件/6.8KB | `reconcile_generators.py:275`（`gen_<name>.success` 时间戳，生成器成功后）；`miniqmt_provider.py:438`（合约元数据缓存）；`generate_domain_doc.py:1895`（指纹） | **真读者**：`reconcile_generators.py:130`（读 success 判漂移兜底）；`ops_guard.py:105` 把 `.runtime/cache` 列入**删除白名单前缀** | 白名单＋TTL 双通道；实测末段审计 1,149 次删除命中 `gate_cache`（`cache` 面自身 2 次） | 02:01（生成器节拍），静默 0.0d | code=6 `_working`=4 | 活基础设施；甲 |
| `derived_dirty` | 3 件/270KB | `derived_dirty_ledger.py:59`（`integrity_intent.jsonl` 追加）；`reconcile_generators.py:110`＋`post_commit_regen_yaml.py:126`（`state.yaml`/dirty 目录）；事件＝post-commit/生成器 | **真读者**：`reconcile_generators.py:110-130`（消费 dirty 清单决定重生成）、`post_commit_regen_yaml.py:126` | `.jsonl` 被 TTL 引擎列为**保护后缀（永不删）**→ 只增；**实测净增 ≈7.9KB/日**（§6-正版①；初版 ctime 法"426,637 B/日"作废） | 01:34，静默 0.0d | code=2 `_working`=4 | 活基础设施／**增长债**（`.jsonl` 豁免＝结构性只增）；甲 |
| `entrance_audit` | 14 件/38.4KB | `entrance_gate_hook.py:28`（`.runtime/entrance_audit/<sid>.jsonl`）；触发＝pre-write hook 事件（每会话一文件） | 读者＝**仅门自身**（`tests/gov/governance/test_entrance_gate_hook.py:54` 断言时序）；src/scripts 内**无第三方读者** → 判"供机械查'反查先于首写'"的设计面，**实测零真读者** | `.jsonl` 保护（永不 TTL）；无自清理 → 每会话 +1 文件永久 | 最新 10-11 18:03，静默 0.3d；随会话产生 | code=2（`_working`/catalogs=0） | 活基础设施（审计面）／件数债；乙 |
| `guide_reads` | **96**（本车道量测 145→96）/18.9KB | `lock_files.py:1728` `_GUIDE_READS_DIR`（首采指南留痕 `<sid>.json`）；触发＝会话首采 | **真读者**＝同文件 `:1727`（存在即"已读"，零输出零开销）——是**功能幂等标记**非自我观测 | 无专属 rotate；被 **GATE-RUNTIME-CLEANUP** 按 7d TTL 删（02:10 窗口审计 **50 次命中**；02:22 窗口该批已滚出轮转段——本车道 145→96 的**直接目击**才是主证） | 02:07，静默 0.0d | code=1（唯一） | 活基础设施（幂等缓存）；甲 |
| `handoffs` | 263 件/349KB（`iterdir` 194＋子目录） | `session_concurrency.py:194` `_HANDOFF_DIR`＋`phase_manager.py:375`（commit summary 落盘）；触发＝会话收尾/相位切换 | **真读者**：`session_concurrency.py:1904`（`glob handoff_*.json` 聚合）、`backup_runtime_state.py:407`（灾备必抄面，被 `tests/data/dr/test_restore_from_backup.py:15` 验恢复）；自我观测＝`generate_dev_delivery_map.py:428` | `generate_dev_delivery_map.py:434` 自记 `retention="留档"`；**实际无留档机制**——TTL 引擎按 7d 删（末段审计 70 次） | 01:49，静默 0.0d | code=15 `_working`=30 catalogs=1 rules=1 | 活基础设施／**在册自相矛盾**（声明"留档"vs 引擎 7d 删）；甲 |
| `process_incubator` | 1 件/1.68MB | `shared/infra/process_incubator.py:22`（`ledger.jsonl`，safe_write_text CAS）；触发＝每次孵化子进程 | **真读者 ×3**：`resource_sampler.py:125`（观测）、`process_reaper.py:85/97`（**reaper 反查 owner 的唯一机械可对账接口**）、`generate_resource_morning_report.py:69` | `.jsonl` 保护永不删、无分段/rotate → **实测净增 ≈55KB/日**（§6-正版①，31 分钟窗 Δ+1,194B；⚠初版 ctime 法算出的"3.37MB/日"已作废，理由见 §6-作废留案） | 01:36，静默 0.0d；计划任务 `ZephyrAlpha_ResourceSamplerScan` 02:08、`_ResourceSamplerWriteback` 10-11 05:40 | code=10 `_working`=9 catalogs=1 | 活基础设施（承重：reaper 认主）／**重增长债**；甲 |
| `process_reaper` | 2 件/10.2KB | `trading/process_reaper.py:189` `_STATUS_DIR`（`last_run.json` 幂等覆写）；触发＝计划任务 | **真读者**：`generate_governance_map.py:482`（`reaper_last_run` 事实源）、宪法 §0-2 `--status` 通道（人读） | 覆写式幂等（1 文件）；**残件** `last_run.39928.tmp`（10-09 00:25，3.6d）＝`.tmp` 崩溃残留，零读者 | `last_run.json` 01:58 静默 0.0d；计划任务 `ZephyrAlpha_ProcessReaper` LastRun 10-12 02:07、NextRun 02:17 | code=2 `_working`=5 | 活基础设施（RULE-GUARDIAN 锚）；甲 |
| `projection` | 3 件/9.7KB | `registry_projection/state.py:65` `STATE_REL`（投影状态）；触发＝registry 投影动作/commit 门 | **真读者**：`registry_yaml_parse_gate.py:131`（门读 watch 状态）＝提交面消费 | 主状态文件覆写；**2 枚 `.quarantine-1933/1952`** 后缀件＝检疫遗留，非 `.jsonl`→TTL 可删但实测存活 8.9d（未被波及） | 01:25，静默 0.0d | code=3 `_working`=9 | 活基础设施＋检疫残件；甲 |
| `registry_ledger` | 94 件/284KB | `wave0_phase0_gate.py:168`（`--out` 默认落该面，`dualtrack_*.json`/`reconcile_*.json`）；触发＝人工/车道跑迁移门 | 读者：`commit_belt_daemon.py:416` 只读 **旗标** `dual_track.enabled`（现已改名 `.retired-20261003` ⇒ 旗标位已退役）；**94 份报告 JSON 零读者**（搜索面见 §8） | 无 rotate；TTL 引擎可吃但实测 **88/94 件 >7d 仍在盘** | 10-08 22:38，静默 3.1d | code=3 `_working`=19 | 可归档（迁移期一次性出货，报告无消费方）；甲 |
| `schedule_consistency` | 1 件/3.4KB | `schedule_consistency_reconciler.py:114/416`（`last_result.json` fix-in-place 唯一写面）；事件＝post-commit | **真读者**：`scripts/ops/schedule_overview.py:66`（`--publish-report` 同源）；stdout 只读 | 覆写式（不增长） | 00:53，静默 0.0d | code=4 | 活基础设施；甲 |
| `secret_drift` | 1 件/101B | `gov_audit/secret_registry_drift.py:333`（`key_fingerprints.json` 状态，`_DEFAULT_STATE_DIR_REL=Path(".runtime")/"secret_drift"` `:81`） | **真读者**＝同模块（指纹比对判漂移；RULE-SECRETS 三道 gate 之一） | 覆写式 | 00:46，静默 0.0d | code=1 | 活基础设施；甲 |
| `session_closeout` | 1 件/8.8KB | `scripts/governance/_tasks/session_closeout_reconciler.py:67` `_STATE_REL`（state.json）；触发＝计划任务/`--once`，**默认 shadow 只判只记** | **真读者**＝同 reconciler（连续 2 轮嫌疑判据需读回上一轮）；实弹开关在 `data/runtime/session_closeout.live` | 覆写式 | 01:55，静默 0.0d（**心跳级活跃**） | `_working`=1 | 活基础设施（收尾判死链）；甲 |
| `strategy_pipeline` | 6 件/6.5KB | `strategy_pipeline/pipeline_events.py:137` `STATE_DIR`＋`:82`（`pending_events.jsonl` 先落盘后出队）；触发＝事件 | **真读者**＝同模块出队 + `ai_layer/intake/intake_events.py:44`（同模式新建方）；`last_receipt.json` 02:02 在写 | `.jsonl` 保护永不删；`c1_seen_laneb.txt`/`.gate.lock`（10-02 起 9.5d）为残件 | 02:02，静默 0.0d | code=4 `_working`=42 | 活基础设施／件数债；甲 |
| `workspace_alerts` | 7 件/10.4KB | **多写者**：`session_worktree.py:7456`（`stash_notice.json`，stash 后写）＋人工投放 4 枚 Owner/让渡通知（`deadpurge_owner_approval_20261004`／`owner_approval_label_freeze_20261004`／`registry_claim_yield_request_*`／`t3a_ignition_handoff`——src/scripts 内**无代码写者**，属会话直写） | **真读者**：宪法 §2-8（"编辑消失先查 stash_notice.json"＝人/AI 正门）；`generate_front_door.py:180/226`（把该路径印进 FRONT_DOOR 门牌）；其余 5 枚通知件**零读者** | 无 rotate；TTL 可删（实测 4/7 件 >7d 仍在盘） | `stash_notice.json` 10-11 23:39（0.1d）；通知件静默 6.1–8.0d | code=5 `_working`=31 catalogs=1 | 活基础设施（stash_notice）＋**无主通知件**（会话直写根侧留痕）；甲/乙分件 |
| `write_audit` | 4 件/29.7KB | `write_audit_daemon.py:74` `_STATE_DIR`（`lifecycle.jsonl`/`.pid`/`.lock`/`_stdout.log`）；触发＝SACL 审计守护常驻 | **真读者**：`collect_write_audit_4663.py:59`（水位线 `sacl_collector_state.json`——**实测该件不在盘**，采集器改读 `lifecycle.jsonl`）；真源汇入 `.runtime/audit/write_audit.jsonl`（`:24`） | 无 rotate；`.pid`/`.lock`/`_stdout.log`＝守护生命周期件，守护 **10-05 17:01 起静默 6.4d**（见下） | 6.4d 静默；`write_audit.pid` 存 PID 未与进程表实测比对（本车道不越界跑守护） | code=3 | **可归档／需核**（疑似守护熄火，非本车道判死范围——在飞七班禁碰，此面不属七班）；乙 |
| `pf_alloc` | 1 件/2.1KB | `pf_alloc/allocation_config.py:101` `persist_path`（TierState 跨日快照）；触发＝再平衡检查运行 | 读者＝同 config 消费方（TierState 载入）；`config/resource_profile_registry.yaml:608` 指向 `.runtime/logs/.../data_slot_pf_alloc_rebalance_check.jsonl`（**非本面**） | 覆写式 | 10-09 16:46，静默 **2.4d**（跨日快照却 2.4 日未刷新） | code=1 | 可归档倾向（快照滞后；若 >7d 静默将被 TTL 当临时件删——状态件同判据风险，见 §2-E）；乙 |

### B 组·可归档／增长债（7 面｜12 件｜0.88 MB）

| 面 | 件/字节 | ①写者 | ②读者 | ③轮转 | ④活性 | ⑤引用 | ⑥倾向＋证据 |
|---|---|---|---|---|---|---|---|
| `chain_piling` | 1 件/332.5KB（`.jsonl`） | `governance/meta_question/meta_question_registry.py:40` `audit_jsonl_path`；触发＝元问题审计动作 | **真读者**：`scripts/governance/check_meta_question_audit_reconcile.py:36/203`（全量窗对账，默认读该 JSONL）；`wo_intake_reconcile/replay_audit_to_jsonl.py:7`（补账追加） | `.jsonl` 保护＝永不 TTL；无自清理 | 10-24 口径：**17.4d 静默**（末写 2026-09-24 15:58）；计划任务 `ZephyrAlpha_MetaqAuditReconcile` 10-11 03:50 仍在跑（**清道夫活着、写者熄火**） | code=5 `_working`=12 | 可归档（追加账本停更 17d，但对账门仍指向它＝不可裸删）；甲 |
| `entity_graph` | 1 件/4.0KB（`.jsonl`） | `scripts/entity_graph/entity_graph_ingest.py:54-55` `RUN_DIR/PROGRESS_PATH`（灌入进度）；触发＝人工/批次灌入 | 读者＝同脚本续灌进度位＋`equity_penetration.py:47` 同 `RUN_DIR` | `.jsonl` 保护；无 rotate | 10-20 01:25，**静默 22.0d** | code（路径拼接形态）＝2；面名在 `_working`/catalogs **零命中**（唯一"零引用＋零精确路径"面） | 可归档（研究批次遗留进度）；甲 |
| `agent_runs` | 4 件/2.2KB | `autonomy_core/agents/_run_store.py:20/50`（`<role>/<run_id>/`＋`audit.jsonl`）；触发＝单次手动运行（明写"不建调度器"） | 读者＝`ticket_queue.py:8` 四态队列（`.runtime/agent_runs/_queue/`，**实测 `_queue/` 不存在**＝从未投单）；`governance_agent_entry.py:23` 自述产出 | `.jsonl` 保护；无 rotate | **静默 50.5d**（08-22 14:05） | code=9 `_working`=1 catalogs=1(`architecture_issue_registry.yaml:1848`) | 可退役候选→降级为可归档（4 个 role 只留 audit.jsonl，无 run_id 目录＝从未完整运行）；乙 |
| `autonomy_gate` | 1 件/756B | `autonomy_core/autonomy_boundary_gate.py:31/32`（`queue/ticket-*.json`＋`alerts.jsonl`） | 读者：`tests/ai/autonomy/test_autonomy_boundary_gate.py:5`（测试断言）；**src 内无告警消费方**；`queue/` 子目录不存在（零升级工单） | `.jsonl` 保护 | **静默 50.5d** | code=3 catalogs=1(`fms_deadref_baseline.yaml:106`) | 可归档（一次性演练留痕；`fms_deadref_baseline` 已把它当死引用基线）；乙 |
| `security_events` | 2 件/1.2KB | `security/security_event_bus.py:30`（协议声明 `security_events.jsonl`）——**实测两件都在 `tnr_drill/events/` 子目录**＝演练落点，非协议正位 | 零读者（src/scripts 除声明文件外无消费；搜索面见 §8） | `.jsonl` 保护 | **静默 50.6d**（08-22 12:12） | code=1 `_working`=4 catalogs=2 ruling=1(`ruling_registry.yaml:1168`) | 可归档（演练件躺在协议面命名空间内，会污染日后总线读取的 glob 判定）；乙 |
| `construction_20260823` | 1 件/450B | 盘上只剩 `nlp_e2e/daily_sentiment.jsonl`；写者＝`scripts/ml/run_sentiment_batch.py:25`（产物名实测匹配）；触发＝计划任务 `ZephyrAlpha_NightlySentiment`（10-11 22:30 跑过，**但不写此路径**——见⑤） | 读者＝`scripts/ml/accept_nlp_pipeline.py:25`（验收表点名该产物） | `.jsonl` 保护 | **静默 48.8d**（08-24 05:53）＝计划任务在跑而该面早停更⇒**批次输出已改道**（丙号证据） | code=3 `_working`=12 | 可退役候选（一次性施工留痕，写者仍存但已不改道至此）；乙 |
| `working_archive` | 2 件/577KB（同字节 `prompts_20_ai.md` ×2，epoch 目录） | `governance/audit/reconciliation_registry.py:5441`（"归档有幽灵引用的文档到 `.runtime/working_archive/`"）；触发＝post-commit 幽灵引用归档 | 零读者（归档即终态）；`check_directory_contract.py:100` 只声明它是 neutral zone | 无 TTL 通道（`.md` 非 `.jsonl`→**理论可删**，实测 98.2d 存活＝引擎从未到达） | **静默 98.2d**（07-05） | code=1 catalogs=2 rules=1(`trae_071:139` **在册系统层白名单**) | 可归档（增长债：两枚 288KB 同字节重复件＝同一文档两次归档，无去重）；甲 |

### C 组·在飞车道资产（**禁碰禁判死**，2 面｜28 件｜0.62 MB）

| 面 | 件/字节 | ①写者 | ②读者 | ③轮转 | ④活性 | ⑤引用 | ⑥倾向＋证据 |
|---|---|---|---|---|---|---|---|
| `nightmine_exploration` | 25 件/478KB | `scripts/backtest/factory_grid_executor.py:134`（模块位 `_EXPLORATION_LEDGER`）←`:3165` `args.exploration_ledger` 注入 ←`:2745-2749` 收尾写盘；触发＝**跑批显式带 `--exploration-ledger`**（事件，非计划任务）；`shard_*.log`＝分片 stdout 重定向；`yield_watchdog.py`＝车道投放脚本（非仓内在册件） | **真读者**：`29_woa4_landing_and_scan_readiness.yaml:130/137`、`32_breadth_scan_result.yaml:45/55`（按 n_cells 逐册判读）；`tests/research/backtest/test_factory_grid_executor.py:784` monkeypatch 同路径 | `.jsonl` 受 TTL 保护永不删；`.log` 理论可删（实测未波及）；无自清理 | 10-11 20:05，静默 0.2d（在飞班 st-mineloop/st-mineloop2 资产） | code=1 `_working`=8（mineloop_campaign/nightmine_campaign 逐件点名） | **活基础设施（在飞）⇒ 保护面**；判"零读者"必须先减自家观测节拍——本面读者正是车道的收件册，非自我观测；甲 |
| `nightmine` | 3 件/171KB | GPU 采样器进程 stdout 重定向（`99_checkpoint.md:303` 在册：pid 22656 pythonw，600s×240 档续写 `gpu_util_long.log`）；**src/scripts 内零代码写者**（`gpu_util_long` 全库仅 1 处命中＝该 checkpoint 册） | **真读者**：`24_exploration_recalc_order_receipt.yaml:82` `baseline_curve: .runtime/nightmine/gpu_util_long.log`（作为 GPU 化验收基线曲线） | `.log`＝TTL 可删（实测 3 件均 <7d）；无 rotate | 10-11 22:15，静默 0.2d（st-gpux/st-gpux2/st-gpuwo 在飞） | code=1 `_working`=13 | **活基础设施（在飞取证基线）⇒ 保护面**；⚑ 该面一旦被 TTL 命中，GPU 验收基线曲线即失（`.log` 不在 `.jsonl` 保护后缀内）；甲 |

### D 组·测试残留与占号残件（7 面｜1,333 件｜1.99 MB）

| 面 | 件/字节 | ①写者 | ②读者 | ③轮转 | ④活性 | ⑤引用 | ⑥倾向＋证据 |
|---|---|---|---|---|---|---|---|
| `pt_20260722015135` | 1,255 件/269KB | 零代码写者（`.runtime/pt_<UTCts>` 形态＝**前代 pytest basetemp 约定**；现约定已改道 `.runtime/tmp/pytest_<PID>`，真源 `tests/conftest.py:84-95`＋`reconciliation_registry.py:7534`） | **零读者**（`pt_20260722015135` 全库精确路径命中 0；搜索面见 §8-R1） | 名义上归 GATE-RUNTIME-CLEANUP（`.json`/其它非 `.jsonl` 件 TTL 可删）；实测末段审计 **879 次删除命中本面**＝**正在被回收**（1,255→实测递减） | 07-22 01:58，静默 **82.0d**；内嵌 `wt_test_repo0/.git`、`test_*0/` fixture 目录 | 引用 0 | **可退役候选（正在自然回收）**；甲 |
| `pt_20260722021816` | 55 件/6.2KB | 同上（同日第二次跑批） | 零读者（精确命中 0） | 末段审计 **55 次删除命中**＝全部件已在回收射程内 | 07-22 02:18，静默 82.0d | 引用 0 | 可退役候选（回收中）；甲 |
| `pytest_tmpdir` | 11 件/7.6KB | 旧 `--basetemp`/`tmp_path` 直写位（`audit-trail/events.jsonl` 形态＝写审计测试产物；现约定 tmp_path→`.runtime/tmp/pytest_<PID>`） | 零读者（精确命中 0） | `.jsonl` 保护后缀 ⇒ **TTL 永不删**（唯一"被豁免而永久驻留"的测试残族） | 07-18 10:59，静默 **85.6d** | 引用 0 | 可退役候选；须显式处置（引擎按设计删不到它）；甲 |
| `pytest_tmp` / `pytest_tmp4` / `pytest_tmp5` | 1/2/2 件，91.9KB/859.9KB/854.4KB | 旧 xdist 并发 basetemp（`sess-pytest-A/B/heartbeat.jsonl`＝心跳 daemon 测试件） | 零读者（精确命中 0） | `.jsonl` 保护 ⇒ 永不 TTL | 07-22 11:47，静默 81.6d | 引用 0 | 可退役候选（三面同因）；甲 |
| `ruling_claims` | 7 件/983B | `scripts/governance/next_ruling_id.py:208`（`os.open(..., O_CREAT|O_EXCL)` 占号），触发＝`--claim`（会话取号时） | **真读者**：同工具 `:147-149` `read_inflight_claims` glob `claim_*.json` 参与"在册最大号＋在途占号"三件断言尺（RULE-RULING 机械化） | 显式 `--release` 才 unlink（`:224-242`，仅可删自占）；**无自动过期**；`.json` 受 TTL（7d）终局 | 10-10 07:30，静默 1.8d | code=3 `_working`=4 catalogs=2(`ruling_registry.yaml:3757/3772`) | 活基础设施（占号协议）＋**残件债**：实测 7/7 对应号 **均已登记**（`ruling_registry` 条目 325、在册最大号 508，486/488/490/497/498/503/507 全命中）⇒ 当前零号段污染；真风险＝"占号未登记"时号段被永久吞且无过期通道；甲 |

### E 组·需核／需 Owner 倾向（不裁，只呈）

1. **TTL 引擎把系统层状态件当临时件**（证据甲机制／乙后果）。
   唯一真源 `reconciliation_registry.py:7713-7885`（`GATE-RUNTIME-CLEANUP`，priority=50，post-commit 事件）：
   遍历 `D:/ZephyrAlpha/.runtime` 全树，**mtime>7d 即 `guard_remove`**；保护仅两型＝`.gitkeep` 与 `*.jsonl`；
   剪枝 `commit_queue`/`__pycache__`/`_wt_*`；**单批上限 2000 件**（`:7786`）。
   后果面：`pf_alloc/budget_tier_state.json`（跨日快照，已 2.4d）、`abuse_monitor/abuse_baseline.json`、
   `secret_drift/key_fingerprints.json`、`session_closeout/state.json`、`projection/registry_projection_state.json`、
   `registry_ledger/*.json`、`handoffs/*.json`——**静默超 7d 即被无声删除**（`trae_071:152` 明写系统层"ttl: null／由各系统自管"，
   与引擎"非 `.jsonl` 即 7d 删"两条口径互斥）。改判据＝门禁代码面 ⇒ 属 Owner 门位，本车道只呈不裁。
2. **`handoffs` 在册自相矛盾**：`generate_dev_delivery_map.py:434` 机生册声明 `retention="留档"`，
   而引擎实测在删（末段审计 70 次命中）。机生册的 retention 声明与真实终态不符＝**在册自犯**形态。
3. **`.runtime` 根 22 枚散件的"保守留"有一个 7 日时钟**（⚑ 本项经自我证伪后重写：先前我按分组脚本读出"末段审计 2,151 次 ROOTFILE 命中"，
   实为**分组口径错**——那批 target 不是 `.runtime/<裸文件名>` 形态；按精确形态重切后，末段窗口内根散件删除记录＝**仅 1 次**
   （`.probe_95036.tmp`，session `st-maint3-20261011`，action `guard_remove`）。教训入册：**分组脚本的桶名不能当结论**）。
   实测 22 枚分类＝8 枚 `.jsonl`（TTL 保护后缀，其中 4 枚已静默 41.8–47.5d 而永久驻留）＋**14 枚 TTL 可删且当前全部 <7d**，
   ⇒ 现在没被删的原因是"还没到期"，不是因为被保护。跨过 7 日线的时刻（＝无人动它们时的无声删除时刻）：

   | 根散件 | mtime | 跨过 7d 线 | 语义 |
   |---|---|---|---|
   | `reconcile_launch.lock` | 10-06 02:39 | **10-13 02:39** | 对账启动锁（0 字节） |
   | `takeover_ledger.jsonl.tmp.23876` | 10-08 04:28 | 10-15 04:28 | 接管台账写残件 |
   | `archive_watchlist.json` | 10-08 06:15 | 10-15 06:15 | 归档观察清单 SSoT（`doc_lifecycle.py:8` 明写"观察清单真源＝该件"） |
   | `board_idx_offset.txt` | 10-11 09:20 | 10-18 09:20 | 板块指数偏移位 |
   | `task_board.db` | 10-11 22:33 | 10-18 22:33 | **SQLite 任务板库**（`commit_queue.py:169` 以 `ZEPHYR_TASK_BOARD_DB` 为先例引用）＝删它有真状态损失 |
   | 余 9 枚（`backup.lock`/`pg_probe_state.json`/`reconciler_health_warn_dedup.json`/`session_registry.json`/`depgraph_*`/`*_last_attempt`） | 0.1d 内 | 随静默推定 | 心跳型状态件 |

   ⇒ 呈总包：本轮"保守留"若跨到明日之后，`reconcile_launch.lock` 与 `task_board.db`/`archive_watchlist.json` 的消失
   **不会留下 git 痕迹**（`.runtime` 整目录免跟踪，`trae_071:22` 已把这条写成病根）。证据等级甲（逐件 mtime＋阈值均实测）。
4. **`write_audit` 守护 6.4d 静默**（`lifecycle.jsonl`/`.pid` 末写 10-05 17:01）＝疑似守护熄火；
   判死须进程表实测＋与门禁同源的活性判据，本车道只读不裁。
5. **`security_events`/`agent_runs`/`autonomy_gate` 三面的 08-22 演练件**（50.5–50.6d）与在册协议命名空间冲突：
   `security_events/tnr_drill/events/*.jsonl` 占住了总线协议的正名（协议声明写 `.runtime/security_events/security_events.jsonl`），
   日后真总线接入会被演练子目录污染 glob ⇒ 建议走"归档改名"而非删除（处置权属 Owner/AI 视资产类别，本车道只标）。

### F 组·零读者面（＝"有据"缺位真身，搜索面实测）

| 面 | 精确路径命中（src/scripts/config/tests） | 判定 |
|---|---|---|
| `entity_graph` | 0（面名在 catalogs/`_working`/ruling 亦 0） | 写者存在（`entity_graph_ingest.py:54-55`）**＋零外部读者**（仅自脚本续灌） |
| `pt_20260722015135` / `pt_20260722021816` / `pytest_tmp` / `pytest_tmp4` / `pytest_tmp5` / `pytest_tmpdir` | 各 0 | 零写者＋零读者 ⇒ §2-D 可退役候选真身 |
| `module_factory` / `t9` / `foreign8_wiring` | 各 0（foreign8 仅 `foreign_market_coverage.py:169` 注释提一次，非路径写者） | 零写者＋零读者（无主壳） |
| `heartbeat` / `reports` / `strategy_screen` / `pg_backups` / `pytest_cache` | 0 代码写者；`heartbeat`/`reports`/`strategy_screen` 在 `trae_071:141/142/14` 在册；`pg_backups` 在 `directory_contract.yaml:678/1036` 判 **DEPRECATED（已迁 `tmp/pg_backups/`）** | 在册但无代码写者 ⇒ 约定残留壳；`pg_backups` 属"已裁废面仍在盘" |
| `entrance_audit` | 写者 1（`entrance_gate_hook.py:28`），读者 0（除自家测试断言） | 审计面零消费＝**只写不读**（增长债型） |
| `registry_ledger` | 写者 1（`wave0_phase0_gate.py:168`），旗标读者 1（`commit_belt_daemon.py:416`，**该旗标已改名 `.retired-20261003`**） | 94 份报告 JSON 零读者＝一次性出货堆积 |

搜索面与命令（每条自测能跑）＝§8-R1/R2。判"未知读者"前已按在案教训**减掉波三自家观测节拍**
（`wave3/20_wave3_p1_census.yaml`、`lane_*` 对 `nightmine*`/`guide_reads`/`handoffs` 的点名不计为读者）。

### G 组·22 枚零文件目录壳（本车道接手，逐壳出主）

判据：壳内 0 文件；有无代码写者（mkdir/落盘点）＝"有主"；有主者即便空也是**活接口空态**，无主者才是垃圾壳。

| 类别 | 面（22 枚） | 证据 |
|---|---|---|
| **有写者·活接口空态（11）** | `coordination`（`split_coordination.py:100` 写、`split_coordination_gate.py:74` 读——空＝无在途 split）、`emergency_counts`（`emergency_commit.py:115/309` 计数桶）、`orphan_quarantine`（`session_worktree.py:530` 检疫区根，裁定#B）、`recycle_bin`（`ops_guard.py:840/921`，30 天可恢复）、`reexam`（`scripts/backtest/reexam_cpcv_harness.py:59` `PREREG_LOCK`）、`semantic_audit`（`run_semantic_audit.py:59`）、`clone_guard_audit`（`clone_guard/orchestrator.py:530`＋`scripts/clone_guard_audit.py:26`）、`translation_coverage`（`translation_coverage_reconciler.py:285`）、`stash_archive`（`d1_structure/cleanup_stash.py:70`）、`industry_graph`（`execute_r1_chain_plans.py:24/25`、`io_ingest.py:286`、`igfact_fill.py:503`）、`ai_heritage`（`ai_layer/heritage/heritage_events.py:16`、`scripts/ai_layer/gen_heritage_dedup_snapshot.py:95`） | 甲；处置含义＝**删壳会导致下次写者 mkdir 前的一次性失败面**（多数写者自带 mkdir，但 `PREREG_LOCK`/`O_EXCL` 型不带），判"零文件目录真删"时须按面区分——本轮 46 枚已删壳若含本组，写者会自愈重建（实测 `guide_reads`/`session_registry` 壳均被写者 mkdir 复活） |
| **无代码写者·无主壳（11）** | `module_factory`、`t9`、`foreign8_wiring`、`bdpan_tick`、`pytest_cache`、`pg_backups`（**在册已废**：`directory_contract.yaml:678/1036` 明写 DEPRECATED，真源改 `tmp/pg_backups/`）、`heartbeat`、`reports`、`strategy_screen`、`construction_20260825`、`construction_20260823`（此面有 1 件，见 B 组）——实数 **无主壳 10 枚＋1 枚在册已废** | 甲（精确路径命中 0，见 §8-R2）；四态倾向＝可退役候选；`strategy_screen` 是 `trae_071:14/589` 记载的 **2026-07-20 无声删除事故纪念壳**（Owner 三级分类立法的起因），删它＝抹掉立法起因锚点 ⇒ 倾向"需 Owner"而非"可退役"；证据等级甲（引用实测） |

## 3. `session_registry` 分片面自身累积（专章，实测）

**问题**：merge-upsert 永不删 ⇒ 陈旧片数与占比？
**实测答复**：**"永不删"不成立**——分片真源有删除通道，`.json` 片**不累积**；累积的是**崩溃残件 `.tmp`**。

| 项 | 实测值（02:12 复测） | 判据出处 |
|---|---|---|
| 面内文件 | 29＝21 个 `.json` 片＋**8 个 `.tmp` 残件** | `os.scandir` 全遍历 |
| `list_active_readonly()` 活会话 | **20** | `SessionRegistry(Path("D:/ZephyrAlpha"))` 实调（禁 mutating 版） |
| `.json` 片 vs 活会话 | 21 vs 20 ⇒ 差 1＝`st-mineloop2-20261012.json`（片在、活性判据已不认）＝**心跳滞后型，非删除通道缺失** | 键集合差 |
| 删除通道 | `_delete_shard_only` `:1029-1035`（`p.unlink(missing_ok=True)`），由 `unregister()` `:1476` 与 `list_active` 收割支路 `:1557/1563` 调用 | 源码实测 |
| `.tmp` 残件成因 | `:1015` `tmp_path = p.with_name(f"{p.stem}.{os.getpid()}.tmp")`；`:1021` `os.replace` 失败（WinError 5）→ `:1025` 仅**同进程** best-effort unlink ⇒ 进程被杀即永留 | 源码实测 |
| `.tmp` 读者 | **零**：`_iter` 侧 glob `*.json`（`:1801`），`.tmp` 不进聚合 ⇒ 纯死字节（8 件 2,676B） | 源码实测 |
| `.tmp` 轮转 | **无任何代码清理**（全库无 `session_registry/*.tmp` 形态 glob）；`.tmp` 后缀非 `.jsonl` ⇒ **受 TTL 覆盖**，实测 8 件全部 10-02 生成（静默 9.3d）仍未被删＝引擎从未到达本面（cap/walk 序） | 实测＋§2-E |
| 陈旧占比 | 8/29＝**27.6%**（全为 `.tmp`）；`.json` 陈旧率 1/21＝4.8%（滞后片） | 实测 |
| 兼容副本面（根 `session_registry.json`，8.1KB，mtime 02:12） | 仍在被双写镜像刷新（`_save_shard` `:1044-1046`），**允许滞后**＝按判活铁律禁用它判孤儿；本车道只用它做字节归属登记 | 源码＋铁律 |

**四态倾向**：`.json` 分片＝活基础设施（真源，保护面，禁碰）；`.tmp` 8 枚＝可退役候选（零读者＋零轮转＋字节 2.7KB），
倾向等级甲；删除属机械面（零业务语义），但**不在本车道权限内**（只读车道）。

## 4. `commit_queue` 五子面读写轮转（专章；机读表 `commit_queue_subfaces.csv`）

队列根＝`.runtime/commit_queue`（`scripts/commit_queue.py:170` `_QUEUE_DIR_DEFAULT`，`QUEUE_ENV_VAR` 可覆盖——
⚑ worktree 内跑队列副本会静默解析到影子根，是**另一条在案车道面**，本表只测主区根）。
实测整根：172,588 件 / 8.33 GB（面内含 21 个节点＝15 子目录＋1,082 根散件）。**blobs 全程只 `os.stat`，零 read**。

| 子面 | 件/字节 | 写者（file:line＋触发） | 读者（file:line） | 轮转/终态 |
|---|---|---|---|---|
| `pending/` | 39 袋＋`.stale/` 297 影子指令（58.5KB） | `commit_queue.py:1226` 区（enqueue 落袋，`_atomic_write`）；触发＝**会话提交/LOCK_TIMEOUT 改道入队**（`git_commit_gateway` 侧）；`.stale` 影子指令写者 `:1571`（`pending/.stale/<qid>.json`）`_mark_cascade_stale` `:1742` | 真读者＝serializer 排空 `:2334-2344`（`pending→processing` 原子取项）、孤儿回收 `:1523-1524`（`processing/q-*.json`）、`.stale` 读回 `:1615`；`--depends` 前置检查 `:3600` | **无自动清理**（袋是待落地资产，语义上不可 TTL）；`.stale` 影子指令无独立 TTL |
| `processing/` | 1 袋/12.3KB | `:2336`（`os.replace` 原语迁入） | `:2145`（环境失败退回失败则留此等孤儿回收）、`queue_status` `:3988-4009`（`oldest_processing_created`） | 生命周期=在途；残袋由 `:1524` 回收 |
| `done/` | 745 袋/5.07MB | `:2441`（`os.replace(processing→done)`） | `:1733`（同名存在性判定）、`coordination_state_board.py:753`（状态板聚合）、`_spot_check_dev_blob` `:3467` | **有 TTL＝7.0 天**（`_DONE_TTL_DAYS_DEFAULT` `:192-194`，66 号 §12 Q3），**但仅 `cleanup` 子命令触发**（`:4784` 打印"done/ 超 TTL 项已清理；dead/ 永不清理"）⇒ 非自动；实测 745 件堆积＝cleanup 未被周期调用 |
| `dead/` | 1,455 袋＋`archive_flashbiz_superseded_20260918/`(14)＋`_root_cause/`(36) = 1,505 件/40.9MB | `:2135/2264/2383/2474`（`os.replace(processing→dead)`，四路死信出口） | `commit_queue.py requeue`（`:3600` 反查）、`lane_deadletter.md` 案卷（本战役车道，**已建账**） | **设计性永不清理**（RB2：mv 非删）；人工 `dead-archive` → 根级 `dead_archive_<yyyymmdd>/`（`:3556`），实测 6 枚归档目录＝**2,264 件/22.6MB**；前置＝serializer 租约必须空闲（`:3550` 拒绝并行） |
| `blobs/` | **26,342 件/4.88 GB**（sha256 命名内容寻址） | `:556-558` `_store_blob`（`if not blob_path.exists()` ⇒ **天然去重**，同内容不重存），单件上限 10MB（`:185`，超限拒入队 `:544`） | `:3143`（`(root/f["blob_ref"]).read_bytes()` 落地取快照）、`:3150/3167` sha 双校验、`:4371-4392` blob 史证反查、`scripts/governance/blob_gc.py:90`（动态 import 队列本体） | **唯一退役通道＝`blob_gc.py --archive`**（默认 dry-run；孤儿∧mtime>7d → `blobs_archive/`＋manifest，可 `--restore`）⇒ 实测 `blobs_archive` 仅 **44 件/15.5MB** ⇒ **GC 从未放量执行**＝4.88GB A 类复活字节源全部在盘。⚑ 本车道零 read 零 execute |
| `worktree/`（serializer 专用，**保护面**） | 52,561 件/**1.91 GB** | `commit_queue_landing.py:121` `_WORKTREE_DIR_NAME="worktree"`；`:1837/1839` `git worktree add <wt> <serializer_branch>` | landing 全流程（快照重建/落地/git 校验）、`_read_files_from_worktree` `:4513` | `:1814/1828` `git worktree prune`；GATE-RUNTIME-CLEANUP **显式剪枝 `commit_queue` 整树**（`reconciliation_registry.py:7781/7791`，注释理由＝"TTL 删除会腐蚀 worktree 完整性"）⇒ 引擎不会误删；mtime 0.14d |
| `worktrees/`（落地 worker 池 w0–w3） | 87,895 件/**1.44 GB** | `commit_queue_landing.py:3690/3711`（`<queue_root>/worktrees/w<worker_id>`） | `session_takeover_ledger.py:913/958`（`_collect_worktrees` 资源清点→接管台账）、`wave1b/claim_gate_repro.py:156/180`（复现脚本） | 同样受 TTL 剪枝保护；实测 w0 02:04 活跃、w1–w3 停于 10-11 22:2x（池缩到单工？——本车道不判，属队列班资产） |
| 根级散件（1,082 件） | 1,066 `*.seq`（2–5B）＋7 `.jsonl`（4.9MB）＋4 `.json`＋`belt_daemon.heartbeat`/`.lock`/`serializer.lease`/`serializer.lease.renew-26548`/`pool_wave.log`(21.3MB)/`.log` | `.seq`＝`:583` 每会话单调 qid 计数器（enqueue 时写）；heartbeat/lock＝`commit_belt_daemon.py:90`（PID＋TTL600s＋僵尸检测）；`serializer.lease`＝`:1316`（TTL 300s） | `.seq`＝`:585` `read_text`；lease＝`:1377-1380`（超 TTL 但 PID 存活＝判定慢项在途） | `.seq` 无清理（1,066 枚永久计数位，最老 08-26 静默 46d 仍在盘）；**`serializer.lease.renew-26548`（10-08 03:00，4.0d）＝续期残件，零读者**；`pool_wave.log` 21.3MB 无 rotate（`.log` 受 TTL 覆盖，尚未到 7d） |

## 5. 零写者＋零读者面清单（＝可退役候选真身，实测键集合）

搜索面＝`src/ scripts/ config/ tests/`（精确 `.runtime/<face>` 路径匹配）＋`docs/**`（引用面）。

| 面 | 件数 | 字节 | 静默 | 零写者证据 | 零读者证据 |
|---|---|---|---|---|---|
| `pt_20260722015135` | 1,255 | 269KB | 82.0d | 全库精确命中 0；现行 basetemp 约定为 `.runtime/tmp/pytest_<PID>`（`tests/conftest.py:84-95`） | 同 0 命中 |
| `pt_20260722021816` | 55 | 6.2KB | 82.0d | 同上 | 同上 |
| `pytest_tmpdir` | 11 | 7.6KB | 85.6d | 同上（旧 `--basetemp` 直写位） | 同上 |
| `pytest_tmp` / `pytest_tmp4` / `pytest_tmp5` | 1/2/2 | 91.9KB/860KB/854KB | 81.6d | 同上 | 同上 |
| `module_factory` | 0（壳） | 0 | 35.7d | 精确命中 0（`module_factory` 只作为源码包名存在，非 `.runtime` 面） | 0 |
| `t9` | 0（壳） | 0 | 8.1d | 命中 0 | 0 |
| `foreign8_wiring` | 0（壳） | 0 | 35.7d | 仅 `src/zephyr/data/foreign_market_coverage.py:169` 一次注释性提及（无写代码） | 0 |
| `bdpan_tick` | 0（壳） | 0 | 51.1d | 精确命中 0；同名看门狗写点在 `.runtime/logs/resource_samples/`（`config/resource_profile_registry.yaml:940/1318`） | 0 |
| `pytest_cache` | 0（壳） | 0 | 24.4d | 精确命中 0；真 pytest 缓存走 `.pytest_cache`/`cache_dir=.runtime/tmp/pytest_cache`（`tests/gov/governance/d7_code/test_compare_pytest_configs.py:91`） | 0 |
| `pg_backups` | 0（壳） | 0 | 46.5d | 精确命中 0；真源已迁 `tmp/pg_backups/`（`reconciliation_registry.py:5332/5385`、`backup_runtime_state.py:324`） | 0，且 `directory_contract.yaml:678/1036` 判 **DEPRECATED** |
| `heartbeat` | 0（壳） | 0 | 76.5d | 精确命中 0；真心跳落 `.runtime/sessions/<sid>/heartbeat.jsonl`（`heartbeat_daemon.py:47`、`trae_071:132`） | 0（`trae_071:141` 仍把它列进系统层白名单＝**在册死名**） |
| `reports` | 0（壳） | 0 | 43.6d | 唯一提及是 `scripts/reports/index.md:22` 的**建议语**（非代码写点） | 0（`trae_071:142` 在册死名） |
| `strategy_screen` | 0（壳） | 0 | 76.5d | 精确命中 0；同名只作为脚本/表名存在 | 0（`trae_071:14/589` 引它作事故起因 ⇒ 删前须保锚点） |
| `construction_20260825` | 0（壳） | 0 | 37.4d | 仅 `daban_board_event_deriver.py:23/49` 注释引用（留痕描述，非写点） | catalogs 命中 1（`architecture_issue_registry.yaml:2506`） |

**小计**：14 个可退役候选面（含 8 枚零文件壳），件数 1,324、字节 ≈2.3 MB（`pt_*`/`pytest_tmp*` 全量）。
字节占比可忽略，但**件数占比＝本车道主面的 68%**（1,324/1,971）——"每面有主有据"的缺口主要是这一族。

## 6. 无轮转面 30/90 天外推（机读表 `no_rotation_projection_30_90.csv`；Δ 表 `face_two_sample_delta.csv`）

### 6-作废留案（第一版口径错误，按在案"更正另起一节留旧案卷"纪律保留原文数字）
初版用 `size/(now-st_ctime)` 作 append 速率，得出 `process_incubator` 3.37MB/日、`derived_dirty` 427KB/日、
`nightmine_exploration` 430KB/日 等——**作废**。作废原因实测定位：Windows `st_ctime` 在
`safe_write_text`/CAS 的 `os.replace` 重写路径上**被刷新**（`process_incubator.py:22` 明写 CAS），
盘上直证＝`ledger.jsonl` 的 ctime 与 mtime **同到毫秒**（02:18:19.254717 / .258970），分母塌成 0 ⇒ 速率虚高一个量级。
另 `span<2d` 的单件面用 size/span 外推会得 45.7MB/日 的荒谬值（`process_incubator` 首版gross列），同批作废。

### 6-正版（两条可辩护口径，逐面标注 basis）
- **口径①「net_measured」**＝本车道两次全表采样（01:57 → 02:28，Δt=0.52h）件数/字节净差年化；
  这是**唯一实测口径**，含"毛写−TTL 删"的净值，可直接回答"会不会涨"。
- **口径②「gross_from_span」**＝面内现存件数 /（最早 mtime→现在），仅对 **≥3 件且 span≥2 天** 的面启用，
  且因 TTL 已删部分，它是**毛增速下界**（低估），只用于判"件数债"方向。
- **口径③「not_extrapolable」**＝短窗内 Δ=0 且不满足②条件（单件覆写面/静默面）⇒ **不外推**，如实报需长窗采样。

| 面 | basis | 实测/派生速率 | 30d 外推 | 90d 外推 | 备注 |
|---|---|---|---|---|---|
| `handoffs` | ①net | **−3,652,839 B/日（净减）**；Δ件 **263→194（−69）** | 件数收缩 | — | 毛增 26 件/日（②）与 TTL 删同量对打 ⇒ **净不涨**；但"留档"声明失效（§2-E-2） |
| `guide_reads` | ①net | **−297,020 B/日**；Δ件 145→97（−48） | 收缩 | — | 同上（毛 17.7 件/日） |
| `projection` | ①net | **−297,708 B/日**；Δ件 **3→1（−2）** | 收缩 | — | **本车道当场目击两枚 `.quarantine-*` 被删**＝引擎到达本面的直接证据 |
| `process_reaper` | ①net | −35,976 B/日 | — | — | 覆写件缩小（`last_run.json` 幂等重写） |
| `session_registry` | ①net | **+20,164 B/日**；Δ件 +2 | 件数≈活会话数＋8 `.tmp` | — | `.json` 随注册/收割涨落；`.tmp` 只增不减 |
| `process_incubator` | ①net | **+54,720 B/日** | ≈3.3 MB | ≈9.9 MB | 承上：`.jsonl` TTL 豁免 ⇒ **只增**；90d 约 1.7×现量（现 1.6MB→~9.9MB）——仍远低于旧版虚高值，但无轮转即无上界 |
| `derived_dirty` | ①net | **+7,928 B/日** | ≈0.5 MB | ≈1.0 MB | `.jsonl` 豁免，只增 |
| `registry_ledger` | ②gross | 9.37 件/日（毛下界） | 375 件/1.1MB | 937 件/2.7MB | 零读者堆积；实际迁移已结束 ⇒ 未来增速≈0 |
| `entrance_audit` | ②gross | 3.88 件/日 | 130 件/0.3MB | 362 件/0.9MB | 零读者审计面 |
| `cache` | ②gross | 5.4 件/日 | 186 件/0.1MB | 510 件/0.1MB | 白名单删除区，实际有轮转 ⇒ 外推为上界 |
| `workspace_alerts` | ②gross | 0.89 件/日 | 33 件 | 86 件 | 人工通知件型 |
| `write_audit` | ②gross | 0.35 件/日 | 14 件/0.1MB | 35 件/0.2MB | 守护若熄火则增速归零 |
| `strategy_pipeline` | ②gross | 0.64 件/日 | 25 件 | 63 件 | `.jsonl` 件只增 |
| `ruling_claims` | ②gross | 1.1 件/日 | 40 件 | 106 件 | TTL 会在 7d 兜底删（§2-D） |
| `agent_runs` | ②gross | 0.08 件/日 | 6 件 | 11 件 | 已 50.5d 静默 ⇒ 外推无意义 |
| `pt_*`/`pytest_tmp*` | ②gross | 2.6／0.67／0.13 件/日 | 收缩中 | 收缩中 | 残件时间戳含内嵌 `.git` 对象 ⇒ span 被拉到 482d，速率列不可信；实际 Δ=0（窗口内） |
| **17 面 basis=③不外推** | ③ | 31 分钟窗内 Δ=0（单件覆写或静默） | — | — | `abuse_monitor`/`ai_error_patterns`/`schedule_consistency`/`secret_drift`/`session_closeout`/`pf_alloc`/`autonomy_gate`/`entity_graph`/`chain_piling`/`security_events`/`nightmine*`/`working_archive` 等 ⇒ 需 ≥24h 长窗复采（命令见 §8-R10） |

## 7. 漂移与口径解释（北极星 63.4GB vs 实测 61.92GB）

| 项 | 口径 |
|---|---|
| 实测全表面 | 102 面 / 1,026,353 件 / **61.92 GB**（`os.scandir`＋`os.stat` 全遍历，非 apparent size；单进程零并发） |
| 字节去向 Top | `tmp` 51.09GB（他车道已建账）＞`commit_queue` 8.33GB（§4）＞`gate_audit` 1.20GB＞`worktree(s)` 已含在队列内＞`audit` 0.43GB＞`quarantine` 0.67GB＞`claim_snapshots` 22.4MB |
| 差 1.5GB 的可解释部分 | ①`campaign_trash_20261001` 47.9MB→1.6MB（TTL 实删，审计 8,932 次命中）；②`tmp` 内 TTL 正以 2000 件/commit 的速率削 `.jsonl` 之外的件（末段审计 6,125 次命中 `tmp`）；③北极星口径若含 apparent/簇大小（NTFS 压缩与簇对齐差异），与 `st_size` 差可达 GB 级——**本车道一律用 `st_size`**，两口径不可混 |
| 结论 | "63.4GB 存量每面有主有据"在本车道覆盖面上成立：本车道 57 面全部出主（写者或"零写者"实证）；**"有据"缺位集中在 §5 的 14 面与 §2-F 的零读者审计面** |

## 8. 复算命令（每条自测能跑，均只读）

- **R0 顶层面全账（102 面/件/字节/mtime）**
  `python -c "import os,time,csv,datetime;from pathlib import Path;R=Path('D:/ZephyrAlpha/.runtime');print(sum(1 for _ in os.scandir(R)))"` ⇒ 实测 102；全量脚本＝本车道 `face_census_20261012.csv` 生成段（§9 附）
- **R1 读者搜索面（判零读者用这条）**
  `python -c "import os;from pathlib import Path;R=Path('D:/ZephyrAlpha');[print(p,i) for b in ['src','scripts','config','tests'] for dp,dn,fn in os.walk(R/b) for f in fn if f.endswith(('.py','.yaml','.yml','.ps1','.sh','.ini','.toml')) for i,l in enumerate((R/dp/f).read_text(encoding='utf-8',errors='replace').splitlines(),1) if '.runtime/pt_20260722015135' in l.replace(chr(92),'/')]"` ⇒ 0 行（自测通过）
- **R2 面名精确路径命中全集**：`Grep -n '\.runtime/<face>' --glob '*.{py,yaml,ps1,sh}'`（本车道已产 `face_ref_hits.csv`，571 条精确命中可复核）
- **R3 活性判据（唯一合法形态）**
  `python -c "import sys;sys.path.insert(0,'D:/ZephyrAlpha/src');from pathlib import Path;from zephyr.security.access_control.session_concurrency import SessionRegistry as S;print(len(S(Path('D:/ZephyrAlpha')).list_active_readonly()))"` ⇒ 实测 **18→20→18 波动**（02:04→18、02:12→20、02:20→18，新班注册与收割即时交替）；**禁 `list_active()`**——mutating 版会写接管台账
- **R4 分片面累积复算**
  `python -c "from pathlib import Path;q=Path('D:/ZephyrAlpha/.runtime/session_registry');j=[x for x in q.iterdir() if x.suffix=='.json'];t=[x for x in q.iterdir() if x.name.endswith('.tmp')];print(len(j),len(t))"` ⇒ 02:12 `21 8` → 02:20 `20 8`
  （`.json` 片随 R3 同步骤降＝**删除通道在岗的直接实证**；`.tmp` 恒 8＝无人清理的直接实证）
- **R5 轮转真源（判"TTL 是否覆盖本面"）**
  `python -c "from pathlib import Path;t=Path('D:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py').read_text(encoding='utf-8');print(t.splitlines()[7748][:60], '|', t.splitlines()[7752][:60], '|', t.splitlines()[7780][:60])"` ⇒ `_TTL_SECONDS=7*86400` / `_PROTECTED_SUFFIX='.jsonl'` / `_PRUNE_DIR_NAMES={'commit_queue','__pycache__'}`
- **R6 删除终态实测（引擎真的删了什么）**
  `python -c "import json,collections;from pathlib import Path;p=Path('D:/ZephyrAlpha/.runtime/gate_audit/ops_guard_delete.jsonl');d=open(p,'rb');d.seek(max(0,p.stat().st_size-14000000));rows=[json.loads(l) for l in d.read().decode('utf-8','replace').splitlines()[1:] if l.strip()];face=lambda r:(str((r.get('targets') or ['?'])[0]).replace(chr(92),'/').split('/')[1] if str((r.get('targets') or ['?'])[0]).startswith('.runtime') else 'OUTSIDE_RUNTIME');print(len(rows));print(collections.Counter((r.get('action'),face(r)) for r in rows).most_common(14))"`
  ⇒ 02:22 自测输出（22,933 条窗口）：`guard_remove/campaign_trash_20261001` 8,806｜`guard_rmtree/tmp` 4,496｜
  `guard_remove/OUTSIDE_RUNTIME` 3,664｜`guard_remove/quarantine`＋`inprocess_allow/quarantine` 各 1,508｜`gate_cache` 1,149｜
  `pt_20260722015135` 879｜`tmp` 197｜`sessions` 138｜`logs` 115｜`gate_audit` 73｜`handoffs` 70｜`inprocess_would_block/OUTSIDE_RUNTIME` 67
  ⚠ 三点口径声明：①该册 50MB **分段轮转**，另有 `.1/.2/.3` 三段未纳入＝窗口非全集；
  ②`face()` 分桶只看 target 第一段，`.runtime` 之外的 target（含 worktree 内镜像路径）单独归 `OUTSIDE_RUNTIME`，
  **不得**把它读成"根散件被删次数"（本车道已在此自犯一次并在 §2-E-3 更正）；
  ③根散件删除要按"恰两段"形态重切，命令＝把 `face` 换成
  `lambda r:sum(1 for t in (r.get('targets') or []) if len(str(t).replace(chr(92),'/').split('/'))==2 and str(t).startswith('.runtime'))`
  ⇒ 本窗口命中 **1 次**（`st-maint3-20261011` 删 `.probe_95036.tmp`）
- **R7 计划任务对照（活性外证，Git Bash 吞 `/query` ⇒ 必走 PS 通道）**
  `powershell -NoProfile -Command "Get-ScheduledTask | Where-Object TaskName -match 'Zephyr|reaper' | Get-ScheduledTaskInfo | Select-Object TaskName,LastRunTime,NextRunTime | Format-Table -AutoSize"` ⇒ 52 支 Zephyr 任务，含 `ZephyrAlpha_ProcessReaper` LastRun 10-12 02:07（⚑ `Where-Object` 用简化语法，含 `$_` 的写法会被 Git Bash 吞成 `extglob`）
- **R8 blobs 体量（零读内容，只 stat）**
  `python -c "import os;b='D:/ZephyrAlpha/.runtime/commit_queue/blobs';print(sum(1 for _,_,fs in os.walk(b) for f in fs), sum(os.path.getsize(os.path.join(d,f)) for d,_,fs in os.walk(b) for f in fs))"` ⇒ 26,342 件 / 5,244,876,678 B（02:20 复测 26,349 件 / 5,245,108,534 B＝**仍在涨**）
- **R9 在册系统层白名单对照（判"有据"用）**
  `python -c "from pathlib import Path;t=Path('D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_071_temporary_file_lifecycle.yaml').read_text(encoding='utf-8').splitlines();print(chr(10).join(t[129:152]))"` ⇒ 输出 **12 个在册子目录**（sessions／claim_snapshots／emergency_counts／gate_audit／handoffs／lookup_audit／reconcile_reports／working_archive／locks／heartbeat／reports／aidrafts）＋**6 个在册根文件**＋`ttl: null  # 系统文件生命周期由各系统自管`；
  **本车道 57 面中仅 `handoffs`/`working_archive`/`heartbeat`/`reports`/`emergency_counts` 5 面在名单内**（其余 52 面＝未在册面，其中 `heartbeat`/`reports` 虽在册却零代码写者＝死名）
- **R10 净增速复采（§6-正版①的可跑形态；两采样间隔越长越准）**
  `python -c "import os,time;from pathlib import Path;R=Path('D:/ZephyrAlpha/.runtime');f=lambda n:sum(os.path.getsize(os.path.join(d,x)) for d,_,fs in os.walk(R/n) for x in fs);c=lambda n:sum(len(fs) for _,_,fs in os.walk(R/n));n='process_incubator';print(n,c(n),f(n))"`
  跑两次（间隔 ≥24h）后取差即净增速；本车道实测两样本对＝`face_two_sample_delta.csv`（01:57/02:28，Δt=0.52h）。
  ⚑ 判"增速"禁再用 `size/st_ctime`——CAS/`os.replace` 会刷新 ctime（§6-作废留案已实盘直证）。

## 9. 剩余申报（未穷尽项＝如实报，非失败）

1. **`.tmp`/残件的 PID 归属未逐件实测**：`session_registry` 8 枚 `.tmp`、`process_reaper/last_run.39928.tmp`、
   `projection/*.quarantine-1952/1933`、`serializer.lease.renew-26548`、`write_audit/write_audit.pid` 的
   "对应进程是否已死"未查进程表（本车道为免越界未跑 `Get-Process` 全表；名字里的数字是 PID 线索，非结论）。
2. **TTL 引擎"为什么没删到 X 面"未做全链取证**：我给了机制性假说（`:7786` 单批 2000 上限＋
   `tmp` 551,913 件 >7d 可删＝需 276 个 commit 才能穷尽 tmp 一轮 ⇒ 其他面被排队饿死），
   证据等级乙；要升到甲需读 `reconcile_runner` 的 per-gate 执行日志（本次未见 `runtime_cleanup` 命名的报告文件，
   `reconcile_reports` 13 类前缀中不含它——这条本身是**引擎可观测性缺口**，值得单独立项）。
3. **6 个面的逐件 file:line 写者未定位**（面级已判，件级未判）：`guide_reads` 145→96 的逐件 sid 归属、
   `workspace_alerts` 5 枚人工通知件的投放会话、`working_archive` 2 枚同字节件的双写归因、
   `nightmine` 采样器进程归属、`construction_20260823` 产物改道后的新落点、`industry_graph` 空壳的历史批次。
4. **`tmp`/`quarantine`/`sessions`/`retired_lanes`/`commit_queue` 的字节面**按任务书分工未重做（他车道已建账）。
5. 未跑完的部分（**申报为剩余**）：`cache`/`gate_cache` 两面的生成器→删除对账（`gate_cache` 1,628 件、末段被删 1,149 件）；
   `pt_*` 族与 `tests/conftest.py` 沿革的 git 侧证据（未跑 `git log -- tests/conftest.py`，避免长批）；
   `reexam`/`semantic_audit`/`stash_archive` 三面的**最近一次真实跑批时刻**（需查计划任务动作面而非状态面）。
6. **`locks` 件数下降归因未定**（§1-7 两把候选并存）：未逐条追 `guard_remove` 审计记录的 `session_id`/`action`
   以区分"引擎 TTL"与"`lock_files.py cleanup` claim-TTL"通道；升甲需按 §8-R6 输出加 `session_id` 维度重切。
7. 本车道零删除、零 `git add`/commit、零写 `.runtime` 根；写入面仅
   `docs/_working/finalclean2_campaign/wave3/lanes/lane_face_ownership.md` ＋
   `.runtime/tmp/st-fclean3-20261012/out/`（`face_census_20261012.csv`／`face_files_detail.csv`／
   `face_ref_hits.csv`／`face_code_hits.txt`／`face_writer_hits.json`／`face_rotation_class.csv`／
   `no_rotation_projection_30_90.csv`／`commit_queue_subfaces.csv`／`target_faces.json`／
   **`face_six_col.csv`（57 面六列机读总表，§2 的机生对应件）**／`face_reference_counts.csv`）。
   ⚠ 该 out 目录**与他会话车道共用**（实测目录内另有 `L_*`／`*_rows.csv`／`shadow_round*.json` 等 190＋ 他班产物）；
   本车道十个产物 mtime 全落 01:58–02:13（＝本车道窗口内），但**写前未做同名存在性探测**，
   若他班曾以完全同名产出，本车道为覆盖式写入——列此如实申报，总包如需追索他班原件请以 mtime 分段判定。
