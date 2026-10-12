---
ttl: task_bound
completes_when: 本案卷读数被总包在 dev 侧复核，且其中点名的在册缺陷被属主车道承接
generated_by: 本班只读车道（弱模型出案卷不出裁定），落地面由 st-fclean4-20261012 复核
session: st-fclean4-20261012
lane: wave4-lane_status_checkoff
role: 只读调研案卷（零删除、零 git 写、零改判据）
---
# 终清波四·车道案卷：已裁项 M1/M5/M12 与队列健康核销测量

> 原稿面＝`.runtime/tmp/st-fclean4-20261012/lanes/lane_status_checkoff.md`（TTL 临时区），本件为其入册副本；
> 数值口径以该案卷自带的时刻与参照点声明为准。
# Lane 状态核对册（终清波四 / st-fclean4-20261012）

- 性质：只读测量道，产出事实与计数，不产裁定。
- 开工墙钟：2026-10-12T21:19:13+08:00（`date -Is` 实读）
- HEAD：c52d81aa96b222bdf73cdaf9f6f48e0534c235b2（分支 dev）
- 红线遵守：零写（除本册与 `out/` 机生表）、零删、零 git add/commit/worktree/stash、不修复任何发现。

## 任务 1 — M1 `.runtime` 根散件（裁定=不动）

墙钟：2026-10-12 21:20:00（`date -Is`）；机生表 `out/m1_root_files_diff.tsv`（24 行）。
冻结面=`.runtime/tmp/st-fclean3-20261012/out/p2_root_files_content_evidence.json:2` `measured_at "2026-10-12 02:33:51"`，`files` 共 **22** 枚（逐条 4-224 行，实测条目数=22）。

现状：`.runtime` 根 `find -maxdepth 1 -type f` = **23** 枚（目录 80 枚未计）。

| 判据 | 结果 |
|---|---|
| 冻结 22 枚仍在盘 | **21** 枚（逐件 sha256 全等 14 枚；sha/体积已变 7 枚，见下） |
| 已消失 | **1** 枚＝`backup.lock`（冻结 49 B／mtime 2026-10-12 01:06:06） |
| 冻结后新增 | **2** 枚＝`.probe_21144.tmp`（0 B，17:25:51）、`session_registry.23800.tmp`（4584 B，17:26:11） |

sha 已变 7 枚（=活的运行态件，非外来覆写征兆）：`board_idx_offset.txt` 7→6 B（mtime 10-12 09:21:21）、
`pg_probe_state.json`（18:29:24）、`reconciler_health_warn_dedup.json`（21:06:25）、
`session_registry.json` 5905→6423（21:19:52）、`takeover_ledger.jsonl` 1,026,116→1,061,579（20:57:19）、
`task_board.db` 176,128→180,224（20:17:24）、`worktree_ops_log.jsonl` 3,714,476→3,731,789（21:16:59）。

### TTL 门的真源与规则（读码实证）
门＝`GATE-RUNTIME-CLEANUP`，构造点 `src/zephyr/governance/audit/reconciliation_registry.py:7713`（`make_runtime_cleanup_reconciler`），
注册 `:7880 gate_id=`，`priority=50`（`:7883`），`file_ops={"read","delete"}`（`:7884`）。
- 触发：`:7755-7757` `_trigger` 恒 True ⇒ **每次 commit 后跑**（事件触发，非 cron）。
- 判据：`:7749 _TTL_SECONDS = 7*86400`；`:7803 now-mtime < TTL → continue`；遍历=`:7790 os.walk(.runtime)`（**含根**），剪枝 `:7791`（commit_queue/`__pycache__`/`_wt_*`）。
- 豁免：`:7806 .gitkeep`、`:7809 以 .jsonl 结尾`（append-only 审计日志）⇒ 冻结 22 枚里 **8 枚 .jsonl 受豁免**（algoflow×2／boot_sla_probe／git_performance_log／predictions_v1_backup／takeover_ledger.jsonl／workspace_drift_warn／worktree_ops_log）。
- 单批上限：`:7786 _MAX_DELETES_PER_RUN=2000`（超出留待后续 commit 收敛）。
- ⚑ **"无声吃掉"在审计面不成立（实测更正）**：`:7813-7815` 走 `scripts/ops_guard.py:792 guard_remove`，其 reconciler 分支 `:804-812` 先落审计再删，
  审计文件=`.runtime/gate_audit/ops_guard_delete.jsonl`（`ops_guard.py:347/361/382`），记录含 `command`＋`targets` 全路径＋`reason`。
  正对照（同尺同面）：当前段内 `reason` 含 "reconciler GATE-RUNTIME-CLEANUP 已声明 delete" 的记录 **49,386 条**（样例 targets=`.runtime/tmp/csx_b5/...`）。
  ⇒ 无声＝**不进任何注册表/文档**，但 jsonl 逐条留痕。
  ⚠ 反向风险：该留痕面自身受取证窗约束（见任务 2，实测仅 4.33 日）——**过期删除的证据比自己先被挤掉**。

### 到期时刻（=mtime+604800s；实际被吃=该时刻之后的第一次 commit）
| 件 | 现 mtime | TTL 到期 | 距 21:31 |
|---|---|---|---|
| `reconcile_launch.lock` | 2026-10-06 02:39:38 | **2026-10-13 02:39:38** | **5.1 h（ imminent）** |
| `takeover_ledger.jsonl.tmp.23876` | 2026-10-08 04:28:48 | **2026-10-15 04:28:48** | 2.5 d ⚑ 冻结册未列入 TTL 名单的第 4 枚（后缀 `.tmp.23876` 不吃 `.jsonl` 豁免） |
| `archive_watchlist.json` | 2026-10-08 06:15:57 | **2026-10-15 06:15:57** | 2.5 d |
| `depgraph_di_seam_cache.json` | 2026-10-11 23:24:28 | 2026-10-18 23:24:28 | 6.1 d |
| `task_board.db` | 2026-10-12 20:17:24（冻结时 10-11 22:33:01） | **2026-10-19 20:17:24**（按冻结 mtime 则 10-18 22:33:01） | 7.0 d（活件，mtime 每写必推后） |
| `depgraph_scan_cache.json`／`depgraph_ops_last_attempt`／`code_index_sync_last_attempt`／`frontmatter_sync_last_attempt` | 10-12 00:42-00:43 | 10-19 00:42-00:43 | ~6.1 d |
| `board_idx_offset.txt` | 10-12 09:21:21 | 10-19 09:21:21 | 6.5 d |
| `pg_probe_state.json` | 10-12 18:29:24 | 10-19 18:29:24 | 7.0 d |
| `reconciler_health_warn_dedup.json` | 10-12 21:06:25 | 10-19 21:06:25 | 7.0 d |
| `session_registry.json` | 10-12 21:19:52 | 10-19 21:19:52 | 7.0 d（活） |
| 新 2 枚 `.probe_21144.tmp`／`session_registry.23800.tmp` | 10-12 17:25/17:26 | 10-19 17:25/17:26 | 7.0 d |

⚑ 与晨间裁定文本的两处口径差（只报数不判对错）：`24_wave3_morning_package.md:55` 写
"`task_board.db`/`archive_watchlist.json` 10-15/10-18"，按冻结 mtime+7d 实算＝**archive_watchlist 10-15、task_board 10-18**（名序与数序反接）；
且该句列 3 枚待吃，实算待吃非豁免件为 **4 枚**（多 `takeover_ledger.jsonl.tmp.23876`）。
`backup.lock` 已消失但 **不是 TTL**（其 7d 到期=10-19 01:06，未到），且在 `ops_guard_delete.jsonl*` 三面 grep `backup.lock` **0 命中**
（同尺正对照=同族 grep `GATE-RUNTIME-CLEANUP` 命中 4 个文件）⇒ 判为属主进程自解锁，非门食。

## 任务 2 — M5 取证窗/观测窗

墙钟：21:22:15 / 21:28:56 / 21:31:11。

### HEAD 在册裁定原文（带行号）
- `docs/_working/finalclean2_campaign/wave3/22_wave3_p2_mechanical_and_shadow.md:71`："读者实测只有
  `commit_gateway_abuse_monitor_reconciler.py:488/:493-494/:502`，全量逐行读、时间窗在内存里（`since_7d` 于 :749，调用位 :773）"
- 同件 `:72`："⚑ **真风险不是体积是取证窗侵蚀**……族上限 200 MiB，`audit_jsonl_writer.py:59-62`，而 `ops_guard_delete` 面只保 **~3.7 日**、
  `feature_flags` ~**0.7 日**……裁决：方案优先级＝**先扩取证窗，再谈缩容**（只动带 `.<N>` 段∧静默>30d，`retention.py:46`……）"
- 菜单面 `24_wave3_morning_package.md:59`（M5 行）同口径；`28_wave3_99_delivery.md:55` 再确认"应先扩取证窗，现仅 3.7d/0.7d"。

### "观测窗"在 HEAD 里到底是什么（实测结论）
1. **代码里没有任何 ≥14 日的观测窗在册**。全 HEAD（wave3+maint3_campaign 五件）grep `14 天|14天|14 日|≥14` = **0 命中**
   （正对照：同 grep 对 `gate_audit/ops_guard_delete/feature_flags` 在同目录命中 20+ 行；单件 `24_` 内 grep `14` = 5 行）。
   ⇒ ≥14 日来自统筹裁定面，未落文档/未落码。
2. **审计族体积是"尺寸窗"不是"时间窗"**：`src/zephyr/shared/io/audit_jsonl_writer.py:59 DEFAULT_MAX_BYTES = 50*1024*1024`、
   `:62 DEFAULT_BACKUP_COUNT = 3`（注释 `:61` "当前段 + 3 历史段 ≈ 200MB/文件 硬上限"），轮转 `_rotate():65-79` 超出份数的最老段 `unlink`。
   该文件在 HEAD 的最后一次改动 = `d69abf35230`（**2026-10-11 07:34，维护二班 P0+P1 袋，T14**）：只把裸 append 五处接入同一道体积闸
   （`rotate_if_oversized :81`，调用 `:102/:133`），**未上调 max_bytes/backup_count** ⇒ 自 10-11 起"窗"仍由 200MB 封顶。
3. **`retention.py:46` 引用漂移**：`src/zephyr/gov_audit/retention.py` 实测 `:42 HOT_RETENTION_DAYS=7 / :43 WARM=90 / :44 COLD=365 / :45 LOG_RETENTION_DAYS=30`，
   `:46` 为空行、`:47 def __init__`（默认 hot=30）；且该类目标目录 `:34 MCP_AUDIT_LOG_DIR = Path("logs/mcp_audit")` **不是 `.runtime/gate_audit`**
   ⇒ 被引作"先扩取证窗"的落点是另一面（logs/mcp_audit），门径未接。
4. **唯一在册的时间窗=读者的 7 日读窗**（非取证窗）：`src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py:208 _WINDOW_24H_SECONDS`、
   `:209 _WINDOW_7D_SECONDS = 7*24*3600`、`:218 BASELINE_WINDOW_DAYS = 7`（滚动保留 7d，cutoff 于 `:335`）；
   起算者=本 reconciler（P1-1 治本 2026-07-20 加 allow_overlap 读法，见 docstring `:481`；force_merge 维 2026-07-21，见 `:204`、`:777`），
   实算于 `:749 since_7d = now_ts - _WINDOW_7D_SECONDS`，消费于 `:773`（allow_overlap）与 `:778`（force_merge）。
   ⇒ **day count = 7 日（读窗）**，与 ≥14 日目标不同物；**不存在"某班自某日起按 14 日计数"的在册观测窗**。

### 现测覆盖率（21:22 记录级时间戳实测，非 mtime）
| 面 | 件数 | 字节 | 族段 | 记录时间跨度 | 现覆盖 | ≥14 日？ |
|---|---|---|---|---|---|---|
| `.runtime/gate_audit/` 全目录 | 340 | 1,303,204,470（du -sb 1,303,204,470；≈1,243 MiB≈1.21 GiB） | — | 目录最老件 2026-08-27 00:35:09 → 最新 10-12 21:16:47 | 46.0 d（目录面） | — |
| `ops_guard_delete*` | 4 段（`.3/.2/.1/` 本体） | 202,375,661（193.0 MiB） | `.3` 52,429,071／`.2` 52,429,085／`.1` 52,429,286／本体 45,088,219 | 2026-10-08 13:03:05 → 2026-10-12 20:56:11 | **4.33 d**（裁定时 ~3.7 d，+0.6 d） | **未达** |
| `.runtime/audit/` 全目录 | 29 | 473,288,062（du -sb 473,156,949，写中漂移） | — | 最老件 2026-08-22 14:04:31 → 最新 10-12 21:21:09 | 51.3 d（目录面） | — |
| `feature_flags*`（在 `audit/`，非 `gate_audit/`） | 2 段 | 37,236,660→实测 `.1` 33,554,527／本体 3,684,xxx 递增 | 无 `.2/.3` | 2026-10-12 16:31:26 → 21:29:00 | **4.96 h ≈ 0.21 d**（裁定时 ~0.7 d，**缩**） | **未达** |

- 换算尺：`ops_guard_delete` 均速 46.6 MB/日 ⇒ 14 日需 ≈653 MB ≈ **13 段**（现封顶 4 段）；
  `feature_flags` 本体段 13.4 分钟写 3.64 MB ⇒ ≈16.3 MB/小时（每次网关进程起 一次性灌 ≈3,900 条 `action:"register"`，键=`timestamp/action/key/state/description`，`timestamp` 是 ISO 串不是 epoch）
  ⇒ 单段 50 MB ≈3.1 小时，4 段封顶 ≈12.4 小时 ⇒ 14 日需 ≈5.5 GB ≈ **110 段**。
  ⇒ 事实：两族都**不是靠等天数能到 14 日**的窗（尺寸封顶，且 feature_flags 越跑越短）。
- 7 日读窗的真实读者面：`allow_overlap_usage.jsonl` 单段 782,280 B（最老记录 2026-07-20 10:55:54，**无轮转段**）；
  `force_merge_usage.jsonl` 单段 16,837 B，跨度 79.78 d，最新记录 2026-10-09 12:35:26（静默 3.37 d）
  ⇒ 这两个被 7 日窗消费的面**当前覆盖 ≥7 日**（与 ops_guard_delete/feature_flags 两族不同物，勿混）。
- 读者行号复核（文件真实位置=`src/zephyr/governance/audit/`，22_:71 只写了裸文件名）：
  `:488 audit_file = repo_root/".runtime"/"gate_audit"/"allow_overlap_usage.jsonl"` ✔
  `:493 with audit_file.open(...)` / `:494 for line in f:` ✔
  `:502 if int(rec.get("timestamp", 0)) >= since_ts:` ✔
  `:749 since_7d` ✔ ／ `:773 allow_overlap_count = count_allow_overlap_usage(project_root, since_7d)` ✔
  补充：函数体 `:477`（allow_overlap）／`:510`+`:521`（force_merge）。全部行号未漂移。

## 任务 3 — M12 shadow 轮次记录

墙钟：21:25:11 / 21:29:42。

### 有效轮的判据（交接卡原文）
`docs/_working/finalclean2_campaign/wave3/23_wave3_shadow_daily_handoff.md:38`："判据＝**四件齐**才算一天：
`mode=shadow` ∧ `errors=[]` ∧ `suspected=[]` ∧ `命中在飞=[]`"；`:39-40`："任一件不齐：当日不计，且**暂停转正**……
零异常满 7 个自然日＋统筹签认，才允许 `--execute` 转真 mv；**注册计划任务与转正同批定，影子期不注册**"；
`:7`："影子期**不许**注册任务"。执行方＝周期班/维护三班（`:5` 标题），命令面 `:16-17`
（`python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json`）。
账册口径 `27_wave3_shadow_watch_log.yaml:5`："按自然日计，同日多轮只做幂等自证不累加天数"；判据 `:6`；
存证地 `:7`（quarantine，非 TTL 承载）。
跨轮比较新口径 `29_wave3_shadow_log_addendum.yaml:22`："同日轮次才可用 `would_set_sha256` 全等做幂等自证；
**跨轮比较一律改用 `would_n` ＋ new/gone 差集**"。

### 轮次表（本机逐件重读 5 枚原始 JSON 所得，非转抄）
| 轮 | ts（UTC→本地） | mode | scanned | would_n | errors | suspected | 在飞命中 | 幂等/差集 | 存证 sha256（前 12） | 判 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10-11 17:31:05Z → **10-12 01:31:05** | shadow | 466 | 288 | 0 | 0 | 0 | would_set `ff19b201c88e8d84` | `5480cbd1f8ad` | PASS |
| 2 | 10-12 01:55:48 | shadow | 466 | 288 | 0 | 0 | 0 | 同上全等 | `890cdb994d9c` | PASS |
| 3 | 10-12 01:55:51 | shadow | 466 | 288 | 0 | 0 | 0 | 同上全等 | `70a721f72763` | PASS |
| 4 | 10-12 11:16:14 | shadow | 466 | 288 | 0 | 0 | 0 | 同上全等（跨 9.7 h 仍幂等） | `56f076e80176` | PASS |
| 5 | 10-12 16:47:03 | shadow | **475** | **296** | 0 | 0 | 0 | would_set `c9739bf5e618`，new_vs_round4=8 支（20261005 系 6＋20261004 系 2），gone=[] | `a5f196b65713` | PASS（跨轮按 would_n+差集口径，非 sha） |

- 逐件重读校验：5 枚 JSON 的 `mode/scanned/errors=[]/suspected=[]` 与账册一致；r1-r4 的 `raw_sha256`
  与 `27_*.yaml:9-12` 登记值**逐字符全等**；r5 不在 `27_` v1 内，登记于 `29_:8-21`（`raw_location` 指到 quarantine）。
- 存证面 `mtime`：quarantine `shadow_rounds/` 5 枚＝01:31/01:55/01:55/11:16/16:47（与 ts 一致，无覆写）；
  `.runtime/tmp/st-fclean3-20261012/out/` 同名 5 枚同 mtime（tmp 面 24 h TTL 会吃，正源在 quarantine）。
- **波三收班后是否有人跑过轮：0**。全集只此 5 枚（`ls .runtime/tmp/*/out/shadow_round*.json` 全域 glob＝这 5 行；
  `shadow_rounds/` 目录 mtime 停在 16:54）；波三末两件交付是 `28_`(20:03) 与 `30_`(20:52)，
  即 **16:47 之后无任何轮**；本道 21:19-21:31 亦未跑轮（禁：本卡要求执行方＝周期班，且 `--dry-run` 仍属他班动作）。
- 合格自然日计数：**1 天**（day1＝2026-10-12）。无任何日有异常（5 轮 errors/suspected/在飞命中全 0；
  would 288→296 已由 `29_:23` 归因为"门 `无注册表条目 ∧ mtime>7d` 陆续跨过 7 天门"的可预期单调增长，非读数抖动）。
- 最早可呈转正批：day2..day7 需 10-13/14/15/16/17/18 **各至少一轮**（`27_:14` 同口径"10-13 至 10-18"）
  ⇒ 第 7 个自然日＝2026-10-18，其"当日不计"判据在当天任一时刻都可能被破 ⇒
  **最早可呈批＝2026-10-19（day7 收盘且零异常之后）**；⚑ 当前风险：day2（10-13）起执行方未见起跑实证
  （见下条：无 shadow 日检计划任务，本道亦不代跑）。
- 计划任务现状（只读 `schtasks /query /fo CSV`，GBK 经 iconv；CSV 共 435 行）：ZephyrAlpha 族 **54 个唯一任务名**
  （含 `\ZephyrAlpha_ProcessReaper`；正对照：grep `AliUpdater`=1 命中、grep `ProcessReaper`=2 命中）；
  grep `closeout|shadow|archiv|finalclean` **仅 1 命中＝`\ZephyrAlpha-BackupShadow`（备份影子，与本影子无关）**
  ⇒ **不存在** session_closeout 影子日检的计划任务，与裁定"转正前不注册"一致（`23_:7/:40`）。

## 任务 4 — 提交队列健康

墙钟：21:26:13 / 21:28:29。机生表 `out/m4_queue_items.tsv`（4,207 行；⚠ 同目录另有 `m4_queue_snapshot.tsv`
＝64 B 仅表头，源自我中途一次报错的脚本，按红线**未删**）。**全程未执行 `scripts/commit_queue.py`**（连 `status` 也未跑，
因其 argparse 块 `:5095-5098` 注明 `--bootstrap` 会触发排空、`cleanup/drain/requeue` 皆改态；已读源码 `:5064-5137`）。

- 根口径核实（防车道影子根）：`scripts/commit_queue.py:150 _REPO_ROOT = Path(__file__).resolve().parents[1]`、
  `:169` 环境变量覆盖位 `ZEPHYR_COMMIT_QUEUE_DIR`、`:170` 默认 `.runtime/commit_queue`；`:625/:4055/:4890` 同式。
  本道按目录直接计数＝**主仓根** `D:/ZephyrAlpha/.runtime/commit_queue/`（未设该环境变量，未走任何 lane 副本）。
- 计数（`.json` 条目文件口径；该根全部子目录文件数＝30,853）：
  `pending` **9**／`processing` **4**／`done` **771**／`dead` **1,524**／
  `dead_archive_20261010_deadcure3` 16／`doctor_prescriptions` 3／`hold_st_gov2` 2（另有 `blobs/`、`blobs_archive/`、
  `worktree/`、`worktrees/`、`dead_archive_*`×5、`quarantine_20261004/` 等非状态目录）。
- 队头等待：**最老 pending**＝`q-20261012-st-maint3-20261011-0021.json` `created_at 2026-10-12T21:02:47+08:00`
  ⇒ 21:27:12 时 **24.5 分钟**；9 枚 pending 的 created_at 全部落在 21:02:47→21:18:28（16 分钟内）
  ⇒ 队列在快速消费，**队头等待实测 ≈25 分钟**（最老 `processing`＝`q-...st-maint3-...0020` 20:58:04 ⇒ 已挂 29.2 分钟未落地）。
  旁证：波三 `q-...-0012`（20:52 入队）此刻已在 `done/` ⇒ 夜间"前面 13/30 袋、数小时不动"的局面当前已不是常态。
- `dead` 近 24 h＝**80 枚**（`dead*` 目录合计）。四类高频死因（总包须避让，逐条取自 `dead_reason` 首行原文）：
  1. `landing 异常: RuntimeError: [landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: <点名件>`
     ——例：`scripts/tasks/register/register_sft_train_window_task.ps1`、`docs/_working/gpuwo_campaign/00_ledger.md`、`scripts/backtest/fexam/card_binding.py`
  2. `ghost_session: 属主会话 … 已死（heartbeat=exited / 注册表无在册），自动重投被存活闸拒绝（裁定#459；CLI 手动 requeue 不受闸限，人工可强制）`
  3. `网关落盘失败（COMMIT_FAILED）: 门禁 TAKEOVER-PENDING 阻断 …必须先按接管处方处置再提交（接管显化 L3，00_orchestration.md §2.2）`
  4. `COMMIT_FAILED: 门禁 CAPABILITY-OVERLAP 阻断: CloneGuard 检测到 extract 级代码克隆`／`门禁 GATE-PRECOMMIT-RUN 阻断 …hook=['gate-no-tests-unit']`
- 本战役相关袋现状：`st-fclean3-20261012` **12 枚**（0001-0012）＝`done` 9 枚（0001/0002/0003/0004/0005/0007/0008/0011/0012）、
  `dead` 3 枚：`0006`＝TAKEOVER-PENDING（15:43）、`0009`＋`0010`＝landing 非注册表族件双侧皆改真冲突，点名
  `docs/_working/finalclean2_campaign/wave3/27_wave3_shadow_watch_log.yaml`（与 `29_:5-7` 自述的 base_head 根因同型）。
  `pending/processing` 内 **无波三袋**。
  `st-fclean4-20261012`＝**0 枚**（本道尚未投任何袋；本道只写盘不提交）。

## 任务 5 — 前提交叉核对（补全）

`git log --oneline -5`（HEAD 顶，实测 21:19）：
1. `c52d81aa96` [矿考二班·接线袋] 双臂底座来源注册＋series 面接上（注册与空册桩同批重写，跨域留痕）
2. `d1301c3472` [考试班·止血袋（本体补投）] 本班 02:39 袋 q-…-0001 死于 R5-DIGIT-SUFFIX…
3. `7d71e8a653` [C族邻域班·文档袋⑤] 台账 §11.5 落地实测回填：0005 已进 dev（12bbfd9569）
4. `30fa8dc141` [死信三期·W-8①·二期唯一副本归并袋] 台账 §廿五＝二期历史三节原文附录 [docs-only]
5. `c533918ac7` [矿考二班·文档袋4] 账册§十一：0080 救援红证三件全过


## 任务 5b — 前提交叉核对（wave4 / 工作区）
- `docs/_working/finalclean2_campaign/wave4/` 在 dev：**不存在**。
  `git ls-tree -r --name-only dev | grep wave4` = 5 行命中，全部属别战役路径：
  `docs/_working/circulation_chief/logs/wave4d.md`、`wave4e.md`、`wave4f.md`、
  `docs/_working/total_command_closeout/wave4/dr_chain_report.md`、
  `docs/_working/total_command_closeout/wave4/registration_needs.yaml`
  ⇒ 命中数 5 但本战役 wave4 目录 0（正对照有效：同 grep 能命中别处 wave4）。
  主工作区亦无该目录：`ls docs/_working/finalclean2_campaign/` = `00_ledger.md`／`10_t0_inflight_triage.md`／
  `11_tmp_dir_dossier.md`／`wave3`（**无 wave4**，21:34:50 实测）。
- `git status --porcelain docs/_working/finalclean2_campaign/wave3/` = **空**（0 行）⇒ wave3 无未提交改动
  （正对照：同尺全仓 `git status --porcelain` = **716 行**，21:34:50）。
- 分支＝`dev`；HEAD＝`c52d81aa96b222bdf73cdaf9f6f48e0534c235b2`。

## 零写自证（本道）
- 唯一写出点＝`D:/ZephyrAlpha/.runtime/tmp/st-fclean4-20261012/lanes/lane_status_checkoff.md`
  ＋ `.../out/m1_root_files_diff.tsv`、`.../out/m4_queue_items.tsv`（+一次报错留下的 64 B 仅表头 `out/m4_queue_snapshot.tsv`，按红线未删）。
- 未跑 `commit_queue.py`／`git_commit.py`／`lock_files.py acquire`／任何 `--help`；未调用 `SessionRegistry.list_active()`
  （波三分片与本道无关，全程只 `os.listdir`/`git` 只读子命令）；零 mv／零 rm／零 git add/commit/stash/worktree。
- 注意：`.runtime/tmp/st-fclean4-20261012/out/` 是**共用车道目录**，21:18-21:29 另有同役他道文件
  （`aidrafts_*`/`c1_*`/`c2_*`/`q1_*`/`q2_*`/`m2_decision_table.json`/`proc_list.json`/`scan_log.txt`），本道一律未触碰。

## 残余未覆盖面
1. **队列"健康"仅文件计数面**：未读 lease/serializer 状态、未读 `.runtime/locks`、未跑 `commit_queue status`
   ⇒ "processing 4 枚挂 29 分钟"无法区分"正在落地"与"卡死"；`done/771` 未做 TTL 口径核对（`cleanup` 默认天数未读死）。
2. **TTL 门的"注册即生效"未证**：只读到货构造点（`reconciliation_registry.py:7713/:7880`），
   未核该 reconciler 在当前 `gate_registry.yaml`/flag 面是否处于 enable（若被 flag 关掉，M1 的到期表全部不发生）。
3. **取证窗"扩"的落地面未测**：HEAD 无 14 日窗、无 backup_count/max_bytes 上调（已证），
   但未查是否存在他班"待批的扩窗袋"（未 grep 队列 blobs 内容面，成本超限）。
4. **M1 内容判据仅 sha/字节级**：未逐件重取 head/tail 样本与冻结面对拍（`p2_*` 只存 head/tail 80 字，判"内容等价"以 sha256 全等为准，已覆盖 21 枚）。
5. **M12 day2 执行方排班未追**：只判"无任务、无新轮"，未读 `maint3_campaign/` 与周期班工牌确认谁负责 10-13 的轮
   （`docs/_working/maint3_campaign/` 只 ls 了前 5 项，未 grep shadow 字样）。
6. **`.runtime` 子目录里的 22 枚同名件未排除干扰**：比对严格按"根层"（`-maxdepth 1 -type f`），
   若他班把同名件移入子目录，本表会判"根层消失"——实测仅 `backup.lock` 一枚判消失，未再下钻证实/否。
7. **时间基准**：全部结论基于本机 21:19-21:31 的 `date -Is`＋NTFS mtime；`session_registry.json`/`task_board.db`
   等活件在测量窗口内仍在跳变（21:19:52→21:28），其"到期时刻"随写入推后，不可当固定值使用。
