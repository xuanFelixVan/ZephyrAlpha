---
ttl: task_bound
completes_when: "§0 口径声明＋§2 未跟踪面四分表（A/B/C1/C2 件数字节、Owner 门位量、在飞留置量、第六态件逐件带 file:line 或 sha 证据）＋§1 两面逐件分账/top10/30-90d 外推/读者实读行号＋§3 归档与同族收敛方案＋§4 待 Owner 定档逐条出处＋§5 复算命令＋§6 残余申报齐备，且结构自证=7 个二级节(§0-§6)/17 个三级节/零'待补'占位；本班零删除零 git 写"
lane: lane_untracked_audit
session: st-fclean3-20261012
role: read-only recon (只读调研车道，出案卷不出裁定)
created: 2026-10-12
author_note: "案卷先行——所有处置建议均待总包/Owner 判读，本车道未执行任何写/删/index 变更"
---

# 波三 · 未跟踪面 + gate_audit/audit 两面 · 只读案卷（v1 定稿待总包过目）

> 状态：**案卷已成，待总包过目**。骨架在第 9 次工具调用落地，此后全程 Edit 追加（未整档重写）。
> 大表另存 CSV：`D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/`（临时区）。
> 本班零删除、零 `git add`/`git rm`/commit、零写 `.runtime` 根、未改任何判据口径/阈值/门禁代码。
> 零写操作清单：本班对 `gate_audit`/`audit`/工作区/index 全部只读；四把尺的写出点仅
> `.runtime/tmp/st-fclean3-20261012/out/*.csv|json` 与本册（案卷唯一允许写面）。

## 0. 口径声明（先讲清，两面数字都"对"）

- 本仓 `.gitignore:265` 为 `/*`（根白名单模式，注释见 `D:/ZephyrAlpha/.gitignore:260-266`）：不带 `-uall` 的
  `git status --porcelain` 会整体漏掉非白名单根目录 ⇒ 工令账面 182 与实测 558 都"对"，但 182 会漏判。
- 本班取数命令（自测可跑，实测于 2026-10-12，主区 `D:/ZephyrAlpha`）：
  ```bash
  cd /d/ZephyrAlpha && git status --porcelain -uall -- docs scripts src tests config data prompts .trae
  ```
- 实测计数（本班口径，含在飞班新产物，随时间漂移）：
  | 口径 | 行数 |
  |------|------|
  | `-uall` 全量行（含 modified/untracked） | 1252 |
  | 无 `-uall` 全量行 | 872 |
  | `-uall` 且仅 `^??`（未跟踪） | **661** |
- ⚠ 与工令"实测 558"的差 = 取数时刻不同（在飞六班持续产出）＋工令可能限定了更窄的路径集。差异登记为**在册漂移**，不改判据口径。
- 红线遵守：本班**禁 `git add`/`git rm`/commit**，只出清单与判据（2026-09-27 多总包夜里主区一次暂存删 186 枚已入库件事故面）。

## 1. 面② `gate_audit` + `audit`（波三新增最大面，工令 §1 未点名）

### 1.1 体积口径（逐文件 getsize 求和，非 du）

| 面 | 递归文件数 | apparent 字节 | MiB | 零字节件 | 备注 |
|----|-----------|--------------|-----|---------|------|
| `D:/ZephyrAlpha/.runtime/gate_audit` | 337（332 个件族） | 1,286,891,006 | **1,227.3** | 0 | 工令记 403 件/1,281.0 MiB；本班实测 337 件（差 66 件，见 §1.7 漂移判读） |
| `D:/ZephyrAlpha/.runtime/audit` | 29 | 504,794,583 | **481.4** | 0 | 与工令 29 件/478.0 MiB 吻合（MiB 口径差=1024 vs 1000） |

- 逐件明细：`out/face_gate_audit_inventory.csv`、`out/face_audit_inventory.csv`（列：face,rel,bytes,mtime_iso,silent_days,depth,mtime_epoch,head_sha256_1MB,tail_sample）
- 汇总 JSON：`out/face_inventory_all.json`
- 结构：`gate_audit` 含一个子目录 `regen_clean/`；两面无深层嵌套。

### 1.2 结论先行（五条，均实测到取值处）

1. **这两面不是"无界膨胀"，是"从未归档"**：体积闸早已存在且单一口径——
   `src/zephyr/shared/io/audit_jsonl_writer.py:59-62`（`DEFAULT_MAX_BYTES=50MiB`、`DEFAULT_BACKUP_COUNT=3`
   ⇒ 单族硬上限 ≈200 MiB），[INVARIANTS]（同文件 :8）明写"轮转保留 backup_count 份历史段**不物理删除**
   （B-016 合规：旧段改名保留而非清理）"。2026-10-11（T14）刚把该尺补到裸 append 写侧
   （`_diff_helpers.py:643-650`、`order_daemon.py:272-276`、`commit_belt_daemon.py:182-184/222-228/372-377/631-634/714-716`、
   `worktree_drift_watchdog.py:414-422`）⇒ 缩容正解=**一次性把轮转产生的旧段（`.1/.2/.3`）归档**，不另造第二把尺。
2. **`gate_audit` 只有 2 枚文件有生产读者**，其余 330 枚是写侧自留取证面（§1.5 逐读到取值处）。
   那 2 枚的读法="全文件逐行读＋进程内时间窗过滤（最近 7d）"，且**只 `open()` 基名、从不打开 `.1/.2/.3`**
   ⇒ 早于 7d 窗的旧段对读者已经零可见 ⇒ 归档零风险。
3. **warn/shadow 册确有消费者**——不是生产读者而是回归锚测试
   `tests/gov/gov_enforcement/test_create_guard_token_sim_shadow.py:174-179`：它读**生产账本**
   `create_guard_keyword_dup_warn.jsonl` 的**前 50 行**做 R-B2 历史重放（:175 文件缺失→skip；:178 存在但空→断言红）。
   ⇒ §4.2"零触发零消费→退役"**不成立**；且该锚吃的是**文件头部（最老样本）**，
   任何"按大小切尾保留"的瘦身会把锚打死（处置约束见 §3）。
4. **两面字节占 `.runtime` 审计族 99.7%**：`gate_audit` 1,228.3 + `audit` 491.9 = 1,720.2 MiB；
   同族 `gate_cache`(1,628 件/0.1 MiB)、`write_audit`(4/0.0)、`lookup_audit`(861/3.2)、`reconcile_reports`(1,004/2.1)
   合计 3,497 件/5.4 MiB ⇒ **同族收敛＝"并命名/并归档器"，不是"并体积"**（§3.4）。
5. **归档动作本身是 Owner 门位且真源已在册**：`src/zephyr/gov_audit/tiered_storage.py:11-12`
   `[SAFETY] H` / `[AI_AUTONOMY] human_gated`；`src/zephyr/gov_audit/retention.py:43-46`
   已定 HOT7/WARM90/COLD365/**LOG_RETENTION_DAYS=30**；`RetentionEnforcer.enforce(dry_run, owner_approved)`
   （:183）要求批文参数；冷库硬红线=`F:\zephyr_cold\AUDIT_SOP.md` 首段"全程只读+台账追加；
   任何删除需 Owner 批文+两份验证副本+台账留痕"（§六处置分级）。⇒ **本车道只出方案不执行**。

### 1.3 逐件分账补充（明细与大表位置）

- 逐件明细（apparent 字节 / mtime / 静默天数 / 首末记录时间戳 / 轮转段号 / 代码引用位）：
  - `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_gate_audit_inventory.csv`（337 行）
  - `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_audit_inventory.csv`（29 行）
  - `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_gate_audit_family_rollup.csv`（332 族，含速率/外推/引用位）
  - `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_audit_family_rollup.csv`（23 族）
  - `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/code_audit_mentions.csv`（3,299 条代码内审计路径提及＝归属判据源）
  - `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/face_inventory_all.json`（全量机读）
- append-only 判定：两面 jsonl **全部 append-only**（写侧唯一收口 `append_audit_jsonl` :109-138 与各 gate
  的 `open(...,"a")`，无覆写型写者）；例外=`registry_drift_<ts>.diff` 快照件与 `keep_shadow_*.json`。
- 零字节件=0（工令担心的"破损件簇"在这两面不存在）。
- 族分布：`gate_audit` 332 族 / 337 件 ⇒ 仅 1 族（`ops_guard_delete.jsonl`）触到 rot=3 上限；
  329 族仍是单段（尚未触发 50 MiB 轮转）；>10 MiB 的 26 族＝1,014.6 MiB（占面 82.6%）；
  top15 族＝797.4 MiB（占面 64.9%）。**体积高度集中 ⇒ 缩容只需动 26 族。**

### 1.4 单件体积 top10 与增长速率（30/90 天外推）

速率口径=（同族最老段首记录时间戳 → 最新段末记录时间戳）跨天差 ＋ 族内 apparent 字节求和。
⚠ **对已触顶族该数字是吞吐量（churn）不是净增长**——净增被 §1.2-① 的族上限钳制。

`gate_audit` top10（MiB / 段数 / MiB·d⁻¹ / +30d / +90d 线性外推）：

| # | 件族 | MiB | 段 | MiB/日 | +30d | +90d | 生产读者 |
|---|------|-----|----|--------|------|------|---------|
| 1 | `ops_guard_delete.jsonl` | 190.10 | 4（已到 rot 上限） | 54.42 | 1,632.6 | 4,897.8 | 无（仅取证） |
| 2 | `test_source_consistency_foreign_staged.jsonl` | 121.03 | 2 | 4.66 | 139.9 | 419.6 | 无 |
| 3 | `no_upward_import_foreign_staged.jsonl` | 65.53 | 2 | 3.47 | 104.0 | 311.9 | 无 |
| 4 | `undefined_name_foreign_staged.jsonl` | 44.38 | 1 | 1.41 | 42.3 | 126.9 | 无 |
| 5 | `secret_registry_consistency_foreign_staged.jsonl` | 39.37 | 1 | 2.08 | 62.5 | 187.4 | 无 |
| 6 | `asyncio_run_in_context_foreign_staged.jsonl` | 38.26 | 1 | 1.23 | 36.9 | 110.6 | 无 |
| 7 | `ssot_redefinition_foreign_staged.jsonl` | 35.52 | 1 | 1.88 | 56.4 | 169.1 | 无 |
| 8 | `mcp_version_field_foreign_staged.jsonl` | 34.54 | 1 | 1.83 | 54.8 | 164.4 | 无 |
| 9 | `constitution_line_limit_foreign_staged.jsonl` | 34.20 | 1 | 1.90 | 57.0 | 170.9 | 无 |
| 10 | `real_key_reference_scan_foreign_staged.jsonl` | 34.20 | 1 | 1.90 | 57.0 | 170.9 | 无 |

`audit` 全 11 个有意义族（件数少，一次列全）：

| # | 件族 | MiB | 段 | MiB/日 | 读者/写者实位 |
|---|------|-----|----|--------|--------------|
| 1 | `write_audit.jsonl` | 181.30 | 4 | 首末 ts 不可析（残余 §6） | 读侧未逐读到取值处 |
| 2 | `bottleneck_ledger.jsonl` | 113.36 | 2 | 未测 | 路径=`order_daemon.py:106`；写=`commit_belt_daemon.py:60`（均过 T14 闸） |
| 3 | `feature_flags.jsonl` | 57.22 | 2 | **90.86**（吞吐） | 写=`flags.py:223-243`＋自带 32 MiB×2 代独立闸（:244）；**零读者** |
| 4 | `worktree_drift_watchdog.jsonl` | 56.97 | 2 | 未测 | 写=`worktree_drift_watchdog.py:426`；消费=`scripts/governance/commit_perf_report.py:10` |
| 5 | `safe_write.jsonl` | 49.06 | 1 | 未测（逼近 50 MiB 闸） | 写=`file_utils.py:427`；读侧未测 |
| 6 | `gate_execution_stats.jsonl` | 9.74 | 1 | 0.38 | **有读者**=`ai_layer/tools/usage_stats.py:93`、`standards_governance/standard_checkup.py:69` |
| 7 | `emergency_track.jsonl` | 4.62 | 1 | 未测 | 写=`emergency_track_guardian.py:75` |
| 8 | `commit_block_events.jsonl` | 4.49 | 1 | 0.16 | 写=`git_commit_gateway.py:863/2108`；取证口径=`commit_preflight.py:20` |
| 9 | `hook_tracked_drift.jsonl` | 2.49 | 1 | 0.04 | — |
| 10 | `preflight_events.jsonl` | 2.20 | 1 | 0.08 | 15 处提及（多为文档口径引用） |
| 11 | 其余 12 族（`precommit_channel_stats/lock_wait_events/algo_flow_translation_sync_runs/create_guard_parse_fail/kill_switch_orchestrator/keep_shadow_20261007_104200.json` 等） | 0.75 | — | ≤0.03 | 含 1 枚影子点火存证 `keep_shadow_20261007_104200.json`（**零代码引用**，在册=10-11 影子点火班产物） |

**面级外推（净增）**：
- `gate_audit`：可测速率族合计 **98.69 MiB/日**（90 族），其中 `*_foreign_staged` 族 65 枚=42.86 MiB/日。
  线性 30d=+2.89 GiB、90d=+8.67 GiB；但 foreign_staged 自 T14 起单族 ≤200 MiB ⇒ 族渐近上限 65×200 MiB≈**12.7 GiB**
  （现 915.9 MiB，约 300 日填满）⇒ **实际 30d≈2.3-2.6 GiB、90d≈4.5-5.0 GiB**（超出部分由轮转丢最老段吸收）。
- `audit`：可测合计 91.57 MiB/日，其中 90.86 来自 `feature_flags`（自带 64 MiB 顶）⇒ **净增≈0**；
  30d≈+11-15 MiB、90d≈+35-45 MiB（`gate_execution_stats`/`commit_block_events`/`safe_write` 触顶余量为主）。
- **缩容紧迫度定论**：**不定在"磁盘将爆"，定在①存量 1.72 GiB 从未归档 ②取证窗口侵蚀**。
  实测窗口：`ops_guard_delete` 200 MiB ÷ 54 MiB/日 ⇒ **历史仅保 ~3.7 日**；
  `feature_flags` 64 MiB ÷ 91 MiB/日 ⇒ **仅保 ~0.7 日**；`test_source_consistency` 类 200 MiB ÷ 4.66 ⇒ ~43 日。
  宪法 §3.1"外来 staged=warn+审计（不阻断）"的连坐取证在 3-4 日外的提交即无据可查——**这才是缩容/归档的立论依据**。

### 1.5 读者实读语义（打开到取值处，禁凭函数名推断）

`src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py`（工令所称 `abuse_monitor_reconciler.py:488` 实名）：

- :488 `audit_file = repo_root / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"`
- :489-490 不存在即 `return 0`（fail-open："无审计=无证据，不误报"）
- :493 `with audit_file.open(encoding="utf-8") as f:` → :494 `for line in f:`
  ⇒ **从文件头到尾全量逐行；无 seek、无 tail-N、无时间预过滤**
- :502 `if int(rec.get("timestamp", 0)) >= since_ts: count += 1` ⇒ **时间窗过滤发生在内存端，不在读取端**
- 调用位 :773 `count_allow_overlap_usage(project_root, since_7d)`；窗定义 :747-749
  `now_ts=int(time.time())` / `since_7d = now_ts - _WINDOW_7D_SECONDS`
- 同函数镜像 :521 + :526-535 + 调用位 :778（`force_merge_usage.jsonl`，同样 7d 窗）

⇒ 裁决要点（供总包签字，非本车道裁定）：**"读到哪一行为止"= 只认基名件的最近 7 天记录**。
故 (a) 基名件中早于 7d 的行＝读者读了即丢，归档无损；(b) `.1/.2/.3` 段＝读者从不打开，**已经零可见**，
移出目录对判定零影响；(c) 唯一风险是"基名件被切成两段后前段被移走"——只要归档**只动带 `.<N>` 后缀的段**，
不动基名件，即可结构性免疫。实测两面：`allow_overlap_usage.jsonl` 0.728 MiB、`force_merge_usage.jsonl` 0.016 MiB，
均 n=1（无轮转段）⇒ 7d 窗当前完整可读。

其余被代码点名的 `gate_audit` 读者（各 1 处，同样只读基名）：

| 件 | 读者 file:line | 现量 | 备注 |
|----|---------------|------|------|
| `git_guard_self_harm.jsonl` | `governance/audit/git_guard_bypass_reconciler.py:87`（`_AUDIT_LOG_REL`） | 0.006 MiB | 末记录 2026-08-27 ⇒ **已静默 46 日** |
| `stash_drop_governance.jsonl` | `governance/audit/reconciliation_registry.py:9809`（`STASH_DROP_AUDIT_RELPATH`） | 见 CSV | stash 清扫留痕＝"证据面不是裁决面"（:9874 自述） |
| `obj_s_ai_exposure_forbidden.jsonl` | `ai_layer/redline/ai_secret_exposure.py:101`（`DEFAULT_FORBIDDEN_LEDGER`） | 0.000 MiB | ⚠ **"只扩不缩"名单台账**：读的是"上一次读数"作对照基线（:13 自述）⇒ **禁动面**，归档=拆基线 |
| `algo_note_payload_review.jsonl` | `gov_enforcement/commit_gates/algo_note_sync_gate.py:69`（`_AUDIT_REL`） | 0.013 MiB | 复审提醒（warning 级不阻断） |
| `registry_drift_<ts>.diff` | `governance/registry_projection/projection_generator.py:66`（`EVIDENCE_REL`） | 私改 diff 留档 | 一次性证据形态 |

**零字面引用面**：285 族（646.1 MiB）在 `src|scripts|tests|config|prompts|.trae` 内查无字面引用——
其中 65 族是 `_diff_helpers.py:630` 由 `gate_name` 派生的 `*_foreign_staged.jsonl`
（派生命名⇒字面必然查不到，**有写者无读者**），其余多为 `obj_s_*`/gate 事件面。
⚠ 本册如实限定："零字面引用"只证明**无代码读者**，不自动等于可退役——退役还需文档/裁定/看板引用面扫描（§6 残余）。

### 1.6 写侧收口与绕过点（缩容着力点）

- 唯一体积闸单口=`zephyr.shared.io.audit_jsonl_writer`（`rotate_if_oversized` :81-106、`append_audit_jsonl` :109-138；
  [CONSUMERS] :5 已登记 T14 消费面）。
- **仍裸 `open(...,"a")` 且未见入口闸前置的写侧（=未来净增长源，6 处）**：
  `ai_layer/redline/drop_gate.py:94`｜`ai_layer/redline/negative_list_gates.py:147-148`｜
  `commit_gates/registry_mass_deletion_gate.py:197`｜`commit_gates/registry_yaml_parse_gate.py:265`｜
  `rule_bridge/session_worktree.py:1056`｜`scripts/governance/commit_queue_landing.py:3800`。
  ⇒ 建议=这 6 处补 T14 同一道闸（**改门禁代码属施工班职责，本车道不动**；全资产净零：零新配置册）。
- **为什么以前从不清**：`GATE-RUNTIME-CLEANUP` 显式豁免 `*.jsonl`
  ——真源 `src/zephyr/governance/audit/reconciliation_registry.py:7734`（"*.jsonl：append-only 审计日志"），
  该豁免正是 `audit_jsonl_writer.py:22-26` 自述的膨胀根因（曾实测 `ops_guard_delete.jsonl` 42 小时 3.7 GiB）。
  ⇒ 任何"让 runtime 自动清 jsonl"的设想会与既有豁免对撞；正解=走归档器（§3），不走清扫器。

### 1.7 账面漂移（如实登记，不改口径）

- 工令记 `gate_audit` **403 件 / 1,281.0 MiB**；本班实测 **337 件 / 1,286,891,006 B（1,227.3 MiB）**：
  字节**升** 5.9 MiB（面在活写）、件数**降** 66（与 T14 上线后轮转丢弃最老段一致，`_rotate` :71-73）。
  **两个数字都"对"，差=取数时刻不同**；提请总包在案卷定稿时按"取数时刻＋口径"双标注。
- `audit` 481.4 MiB（2²⁰）vs 工令 478.0 MiB（10⁶）＝单位口径差，非实物差。本册统一 **MiB=2²⁰**。
- ⚑ `.runtime/sessions/--help/`（目录名字面为 `--help`）＝头号红线事故的物理证据，本班未触碰；
  提请总包把它列"一次性证据区"而非"杂物"。

## 2. 面① 未跟踪件四分归属（实测 661 件 / 755.31 MiB）

### 2.1 四分表（判据=波二原语，未另写第二套）

基线核实：主区当前分支＝`dev`（`git rev-parse --abbrev-ref HEAD`＝dev，HEAD＝`ee0fd9478b`，
`dev..HEAD` ahead=0/behind=0）⇒ `git show dev:<rel>` 与 HEAD 同树，四态判据基线一致。
原语来源＝`D:/ZephyrAlpha/.runtime/tmp/st-finalclean2-20261010/tools/scan_dev_delta.py`
的 `dev_blob_sha / disk_sha / norm_dev_sha / norm_disk_sha`（:28-60），
**本班经 `importlib` 只导入这 4 个函数使用（模块体仅 def，`main()` 受 `__main__` 保护，未执行该文件）**。

| 态 | 定义 | 件数 | 字节 |
|----|------|------|------|
| A | 磁盘原始字节 == dev blob（纯冗余） | 2 | 0.01 MiB |
| B | 仅行尾归一（`\r\n`→`\n`）后相等 | 0 | 0 |
| C1 | dev 有同名件但字节不等（有增量） | 0 | 0 |
| C2 | `git show dev:<path>` 返回码≠0，dev 查无同名 | **658** | 667.09 MiB |
| （守卫） | >64 MiB 未整读（内存红线，只记账不哈希） | 1 | 88.21 MiB |

- 复核"dev: 取空"在册坑：全表 `disk_sha256` 无一条等于空 blob（`e3b0c442…`）⇒ 未中招；
  另抽 3 件用 `git cat-file -e dev:<path>` 独立复核，均报 "exists on disk, but not in 'dev'"（一致）。
- ⚑ **A 态 2 件是异常形态，不是冗余**：`scripts/tasks/run/run_sft_train_task.ps1`（7,463 B）与
  `scripts/tasks/register/register_sft_train_window_task.ps1`（4,535 B）在 `git status --porcelain -uall` 里
  **同时**呈现 `D `（暂存删除）与 `??`（未跟踪），且字节与 dev blob 全等、并在
  `.runtime/commit_queue/worktrees/w0/` 有同 sha 副本 ⇒ 形态＝**他会话已在共享 index 里删了这两件、盘上仍在**。
  这正是 2026-09-27"主区一次暂存删 186 枚已入库件"事故的**同型微缩版（2 枚）**。
  本班未碰 index（零 `git add`/`git rm`），**提请总包立即按"归属=删除发起方会话"处置，勿由波三代修**。

### 2.2 按根的分布（口径：8 个白名单根，`-uall`）

| 根 | 件数 | MiB | 判读 |
|----|------|-----|------|
| `data/` | 449 | 752.48 | **业务资产面**（宪法 §5 Owner 门位）：`strategy_intake` 372/670.52、`backup` 6/52.31、`local_fallback_quarantine` 21/23.16、`registers` 7/6.09、`cleaning_*_gate` 29/0.30，余为 `backups/quality_sentinel/databases/…` 小宗 |
| `tests/` | 140 | 1.94 | 复活/补面工作区：134 件静默 <1 日（`tests/gov/f_lifecycle/` 14 件、`tests/gov/governance/commit_gates/` 66 件、`tests/data/db/` 5 件当日新落）⇒ **在飞班产物** |
| `scripts/` | 36 | 0.79 | 混合：`_archive/ops/*`（静默 19-72 日＝清账候选）、`backtest/fexam/*`（GPU 化班）、5 枚 `.tmp.<pid>.<hex>` 原子写残留（见 §2.5）、`governance/*`、`data_ops/*`、`tasks/*.ps1` |
| `docs/` | 30 | 0.02 | 全为生成器产物（`docs/03_modules/**/index.md`、`algo_flow/*.yaml`、`map_query/blueprint.md`），单件 0.5-3.5 KiB，静默 2.55-10.13 日 ⇒ 无主候选（治理面，AI 可下放） |
| `src/` | 4 | 0.06 | `factor/ah_premium_factor.py`、`governance/map_query.py`、`sell_decision/services/exit_execution_orchestrator.py`、`strategy_pipeline/t0_condition_pack.py`＝**dev 查无新模块**（含 [TTL]/14 字段头），归"在飞班代码产物"，须由对应班落袋 |
| `config/` | 2 | 0.02 | `tdm_mount_exemption_registry.yaml`（内容含 `chief-20261004`）、`data_masking_policy.yaml`（静默 10.78 日） |

### 2.3 三件定窗（在飞判据：真源活性 ∧ 进程表现测 ∧ mtime）

- **真源活性**＝`.runtime/session_registry.json` 15 个在册会话 `last_heartbeat` 全部 **0.1-0.4 分钟前**（取数时刻实测）；
  `held_files` 全为 0（各会话未持 claim）⇒ claim 面**不能**用作归属依据（已如实记录）。
- **进程表现测**＝`psutil.process_iter` cmdline 扫到的 sid 令牌与进程数：
  `st-deadcure2-20261009`=15、`st-gpux2-20261011`=11、`st-fclean3-20261012`=7（本车道）、`st-final4-20261010`=8、
  `backfix`=6、`chief-20261011`=5、`st-fullflow2-20260922…20261008`=5、`st-nightmine-20261010`=4、
  `st-finalclean2-20261010`=2、`st-mineloop-20261010`=2、`st-backfix3-20261011`=2、`st-backfix-20261010`=2、
  `st-gpuwo-20261011`=1、`st-maint3-20261011`=1、`st-gpux-20261011`=1、`st-dexp-20261009`=1
  ⇒ 工令所称"今晚在飞六班"（矿考/追凶/GPU 化/数据车道/维护三班/GPU 工单）**六班进程全部在册存活**。
- **mtime**：静默 0-1 日 179 件（5.31 MiB）、1-2 日 144 件（**410.01 MiB**，主体＝`grid_20261010/20261011` 网格出货）、
  2-3 日 30 件（0.12 MiB）、3-7 日 165 件（180.61 MiB）、7-30 日 142 件（159.26 MiB）、30 日+ 1 件。
- **归属交叉证据**（内容级）：19 件正文里带 sid/chief 令牌（`out/untracked_attribution.csv` `content_sid_tokens` 列），
  其中 `gpuwo/st-gpuwo-20261011` → `scripts/tasks/run/run_sft_train_task.ps1`（GPU 工单班）、
  `backfix` → `data/databases/backup_state_shadow.json`（追凶班）、
  `st-matrix-20261006` → `scripts/backtest/fexam/grid_adapter/grid_configs/fire_plan.yaml`（GPU 化网格）、
  `st-l3altdata-20261007` → `scripts/data_ops/l3_alt_health_*.py`（数据车道）、
  `st-emomine-20260923` → `scripts/ch/backfill_rzrq_history.py`（矿考族）。
- **在飞留置量（结论）**：mtime ≤3 日 ∧ 上述任一班在飞 ⇒ **353 件 / 415.44 MiB** 建议"留并登记"；
  其中 `grid_20261010`（135 件/409.39 MiB）与 `grid_20261011`（36 件/3.43 MiB）＝网格/GPU 化班当日出货，
  在册关联＝`grid-run-nonreproducible-column-order-20261012`（02 件 p₀/p₁ 家族被污染待重判）⇒ **绝不可动，等重判**。

### 2.4 第六态件（车道快照态：别处有同字节副本）—— 全部标出给总包判读，本班未删

判据升级：先按 (basename, size) 在 `.runtime/quarantine` + `.runtime/safety` + `.runtime/commit_queue`
（含 `worktree/`、`worktrees/*` serializer 工作树，共 75,762 个镜像键）命中 116 件，
再**逐件 sha256 实证**：

| 结论 | 件数 | 主体 |
|------|------|------|
| **同字节副本实证成立** | **88** | `tests/gov/governance/**` 66 件、`tests/gov/f_lifecycle/**` 14 件（均在 `.runtime/quarantine/finalclean2_safety/inflight_20261010/**`，79 件同批）、`data/registers/metaq_io_2018/*` 2 件（在 `.runtime/commit_queue/worktree/`，注意镜像侧目录名是 `metaq-io-2018` 连字符版）、`scripts/tasks/{register,run}/*.ps1` 2 件（worktrees/w0）、`scripts/governance/check_registry_field_legality.py`（`quarantine/drift_20261007T072134/`）、`tests/research/**` 3 件 |
| 同字节**不成立**（仅同名同尺寸，sha 有差异） | 28 | 多为 `docs/03_modules/**/index.md`（同名不同内容，**弱信号，不得当副本**） |

⇒ 呈报判读点：那 79 件 `tests/gov/*` 是**波二 `finalclean2_safety/inflight_20261010` 双抄之后又在主区复现**的件，
与在册"deadcure P0 tests 树被删未补 2203 件、2325 条可自 blob 恢复"同链——
**这是复活班的取回面，不是杂物**；`register_sft_train_window_task.ps1`/`run_sft_train_task.ps1` 两件则同时带 A 态 + `D ` 暂存删除（§2.1），
两案并呈，**本班不自删、不 add、不 checkout**。

### 2.5 附带发现（不在工令账面，须上报）

1. **原子写残留泄漏 5 件**：`scripts/backtest/factory_grid_executor.py.tmp.21772.{12f2ad2e5186,14f3fe2b051b,a2a6e73f8f2f,b3bce6f82cf9,c1a69a7ee935}`
   ＝127.8/127.7/126.0/128.6/129.9 KiB，静默 1.28-1.29 日，同 pid 21772 五版尺寸递增
   ⇒ 目标件 `scripts/backtest/factory_grid_executor.py` 是在册热文件（GPU 化/网格班，
   且 `trial-ledger-undercount` 在册根因就在该文件），形态＝`safe_write_text` CAS 冲突/失败留下的旁路临时件。
   **登记为"待归属清理"（属 GPU 化班结案后随批清），本班未动。**
2. **一次性证据区形态在本班扫描根内零命中**：`index_stale_blobs_*`／`pool_rollbackbomb_*` 在
   `docs scripts src tests config data prompts .trae` 八根内 `one_shot_form n=0`；
   其实际位置在 `.runtime/tmp/<sid>/`（属波三 `lane_tmp_lanes.md` 车道面），本班不越面处置。
   ⚑ 工令原文"维护三班根因项结案前保留 `pool_rollbackbomb_20261011`"照此登记为**不可动项**
   （`st-maint3-20261011` 心跳 0.1 分钟前＝仍活跃）。
3. **`data/backup/stock_indicator_circmv_20260916/`（4 件 52.31 MiB，静默 25.06 日）**＝带 README.txt 自述 `st-stkind-20260916`
   的旧班存证包，形态＝"数据出仓前快照"，是 C2 里最像"可归档"的一宗（业务数据 ⇒ Owner 门位，见 §4-⑦）。

## 3. 处置方案（禁裸删；两面均为门禁审计面＝防连坐取证面；**只提方案不执行**）

### 3.1 `gate_audit`/`audit` 切片归档（一次性存量 1.72 GiB）

- **切片键＝"段文件"而非"时间窗"**：只动带 `.<N>` 后缀（`.1/.2/.3`）的轮转段。
  依据（§1.5 实测）：生产读者一律只 `open()` 基名 ⇒ 段文件对读者已零可见，动它**结构性免疫连坐**；
  基名件一律不动（含 §1.5 那 2 枚 7d 窗证据面与 `obj_s_ai_exposure_forbidden.jsonl` 基线面）。
- **准入判据（三条全满足才入归档清单）**：① 文件名带轮转后缀；② 段末记录时间戳距今 > `LOG_RETENTION_DAYS=30`
  （真源 `src/zephyr/gov_audit/retention.py:46`，不新造数）；③ 段内不跨越任何在册锚（§3.3 禁动面）。
  按此实测首批候选＝触顶族 `ops_guard_delete`(.1/.2/.3)、`write_audit`(.1/.2/.3)、`bottleneck_ledger`(.1)、
  `test_source_consistency_foreign_staged`(.1)、`no_upward_import_foreign_staged`(.1)、`feature_flags`(.1)、
  `worktree_drift_watchdog`(.1)、`safe_write`(若切段) 等——**逐件清单见 `out/face_*_family_rollup.csv` 的 `max_rot_index` 列**。
- **落点（只提方案，执行须 Owner 批文）**：
  - 唯一冷储＝`F:/zephyr_cold/50_archive/runtime_audit/<face>/<stem>/<segment>[.gz]`
    （**不走 G**：宪法 §7 一盘一责——F=冷库、G=备份总仓；G 侧只作为**第二验证副本**存在，
    由 `F:\zephyr_cold\AUDIT_SOP.md` §二.2 的 `G:\zephyr_cold\60_mirror` 每夜同步自动达成，
    或按 §三.5 以 `G:/backup/predelete_deltas` 证据包 sha256 清单全验）。
  - 台账必登：`F:\zephyr_cold\00_manifest\drawers.jsonl` 逐行 `path/bytes/sha256`（在册月检§三.3 会全量核对）。
  - 动作序：dry-run 清单 → `cp` 落 F（非 `mv`）→ 两份验证副本 sha256 全验 → **Owner 批文** → 再删源 → 台账留痕。
    与 AUDIT_SOP"任何删除需 Owner 批文+两份验证副本+台账留痕"逐字对齐。
- **保留窗口建议与依据**：段文件=30 日（`retention.LOG_RETENTION_DAYS`）；基名件=永久（读者 7d 窗证据面，
  且轮转自带 200 MiB 顶，无需再瘦身）；若总包要更紧，可用 `tiered_storage.HOT_DAYS=7 / WARM_DAYS=30`
  （`tiered_storage.py:34-35`）——**注意两面现均未接入 tiered_storage**：其目标目录
  `data/audit_history`、`data/audit_archive/{warm,cold}` 实测**全部不存在**（`ls` 证）⇒
  归档器"有码无跑"，接入即复用，不新建（净零）。

### 3.2 是否生成器化（宪法 §4.3/§9.5）

- **必须**：两面的"件数/字节/速率/静默天数/读者引用位"已由本班四支脚本产出（§5），
  手工维护必漂移——本册自身就是证据（工令 403 件 vs 实测 337 件，§1.7）。
- 建议收编为**永久尺**（一次登记，替代而非新增）：把 `face_*_family_rollup.csv` 生成逻辑并入
  既有审计盘点面（`src/zephyr/ai_layer/tools/inventory_generator.py` 或 `usage_stats.py` 族），
  输出改为**字段化册**（`total_files`/`total_bytes`/`mib_per_day`/`last_record_ts`），
  散文只引用字段不写死数字；净零声明＝**替代**工令里"人工点面"这一旧做法，不新增册。

### 3.3 禁动面（归档前必须逐件排除，已在 CSV 标记）

1. `gate_audit/obj_s_ai_exposure_forbidden.jsonl`——"只扩不缩"名单台账，读的是上一次读数基线
   （`ai_secret_exposure.py:13`＋:101），截/移＝拆基线。
2. `gate_audit/create_guard_keyword_dup_warn.jsonl`——R-B2 历史重放锚吃**前 50 行**
   （`tests/gov/gov_enforcement/test_create_guard_token_sim_shadow.py:174-179`）；
   **切尾保头＝可行，截头/清空＝测试红**（:175 缺失→skip，:178 存在但空→断言失败）。
3. `.runtime/audit/keep_shadow_20261007_104200.json`——影子点火在册存证（10-11 备份影子点火案），待结案。
4. 一切基名 jsonl（无 `.<N>` 后缀者）——7d 窗读者证据面。

### 3.4 同族收敛建议（谁并谁，按 §4.2 四判据）

| 对 | 判据 | 建议 |
|----|------|------|
| `.runtime/audit/write_audit.jsonl`（181 MiB）↔ `.runtime/write_audit/`（4 件/0.0 MiB） | **同域重复簇** | 收敛到 `audit_jsonl_writer` 单口 jsonl，退役目录形态（先确认目录 4 件的写者身份，未查＝残余） |
| `gate_audit` ↔ `audit` 两面 | **同真源可派生**（都是门链/运行事件，同一轮转尺、同一 retention 参数） | **并"尺与归档器"，不并目录**：两面共用 `audit_jsonl_writer` 段命名 + 同一份归档清单；目录语义保留（gate 层 vs 运行层），便于读者定位 |
| `.runtime/reconcile_reports/`（1,004 件/2.1 MiB） | 同读窗（`abuse_monitor` :752-763 亦 7d/24h 窗） | **并入同一归档批次**（同一把 30 日尺），不并目录 |
| `.runtime/gate_cache/`（1,628 件/0.1 MiB，TTL 10min） | **跨域不同对象**（缓存≠审计） | **不并**；仅提示 inode 成本（0.1 MiB/1,628 件＝每件 66 B），TTL 清扫已覆盖，勿纳入归档清单 |
| `.runtime/lookup_audit/`（861 件/3.2 MiB） | 已有收敛声明（`create_guard.py:952` "不新建日志文件"，走 find() 既有通道） | **不并**（读者不同：result_count 漂移 vs 事件取证）；登记为"已收敛态" |
| 6 处裸 `open("a")` 写侧（§1.6） | **同真源可派生**（体积判据只能有一把尺） | 由施工班补 T14 入口闸；**零新配置册**（复用 `DEFAULT_MAX_BYTES/BACKUP_COUNT`） |

### 3.5 面① 处置（只出动作清单，本班零 delete）

- 353 件/415.44 MiB（≤3 日 ∧ 班在飞）＝**留并登记**，移交对应班落袋（`grid_20261010/20261011` 尤其等
  列序重判结论）。
- 88 件 sha 实证副本＝**移交归属判读**（复活/取回面），随 deadcure/backfix 班结案；
- `data/` 449 件/752.48 MiB ＝**Owner 门位呈批清单**（业务资产退役/物理删＝Owner；建议按"数据驻留公理"
  走 F 冷库归档＋两份验证副本，而非删除）；
- `docs/` 30 件生成物＋`scripts/_archive/*` 3 件（静默 19-72 日）＋`config/data_masking_policy.yaml`＝
  **无主候选**（治理面，AI 可下放），但均需先做引用面扫描再定退役（残余 §6-②）；
- 2 枚 A 态 `.ps1`（`D `+`??`）＝**代修禁止**，退回删除发起方会话。

## 4. 待 Owner 定档的在册承诺（逐条给出处；本车道未登记/未伪造任何裁定）

1. **CREATE-GUARD S4-B 影子册"一周后定档"已逾期 4 日**——出处
   `src/zephyr/gov_enforcement/commit_gates/create_guard.py:8` [INVARIANTS] 原文：
   "audit-only 只落 `.runtime/gate_audit/create_guard_token_sim_shadow.jsonl`（fail-open），
   `would_block` 恒 False/`threshold` 恒 None——不改任何判定，**相似度分布一周后 Owner 门位定档**"。
   实测册内首记录 2026-10-01T18:59:55+00:00、末记录 2026-10-10T04:26:02、0.162 MiB、5 处代码引用
   ⇒ 一周到期≈2026-10-08。**待裁：定档（给 threshold）或延窗**。虽有 §4.2"零触发零消费→退役"表象，
   **不得自判退役**（在册承诺 + 测试锚 `test_create_guard_token_sim_shadow.py:158/:174` 双消费）。
2. **裁定#456 判重两档化的 warn-only 过渡窗升级**——出处 `create_guard.py:8`
   "裁定#456（2026-09-30）判重腿两档化……仅命中 description（散文面）降为 warn（审计
   `create_guard_keyword_dup_warn.jsonl`，不阻断）"＋同段"warn-only——硬阻断会把存量 token 全打红，
   **留过渡窗由季度审计评估升级**"。⇒ 册 0.097 MiB / 末记录 2026-10-10；**待裁：升级时点**。
3. **`merge_evaluation` 字段 warn-only 的季度审计评估**——出处 `create_guard.py:8`＋`:46`＋`:275`
   （`create_guard_merge_evaluation.jsonl`，0.137 MiB，末记录 2026-10-04）。**待裁**。
4. **挂图申报 `no_mount_reason` 的季度复核**——出处 `create_guard.py:8` 末段
   "（Owner 2026-10-04 三点批准，st-mapmount-surg-20261004）……非空理由逃生+审计
   `.runtime/gate_audit/create_guard_map_mounts_escape.jsonl` **季度复核**；两者皆无→硬阻断；
   scripts/.ps1 面 v1 暂缓"。⇒ 册 0.053 MiB / 末记录 2026-10-09；**待裁：季度复核＋scripts/.ps1 面是否解冻**。
5. **两面归档/物理删本身＝Owner 门位**——出处 `tiered_storage.py:12` `[AI_AUTONOMY] human_gated`、
   `retention.py:183 enforce(dry_run=False, owner_approved=False)`、`F:\zephyr_cold\AUDIT_SOP.md` 硬红线
   "任何删除需 Owner 批文+两份验证副本+台账留痕"、宪法 §5（物理不可逆删除/资产出域）。
6. **B-016 与"归档后删源"的关系需澄清**——出处 `audit_jsonl_writer.py:8` [INVARIANTS]
   "轮转保留 backup_count 份历史段不物理删除（B-016 合规：旧段改名保留而非清理）"＋:33-35
   "超出 backup_count 的最老段才丢弃"。⇒ **待裁**：归档后删源是否满足 B-016（本车道不自解合规条）。
7. **未跟踪面 C2 业务资产 658 件/755.31 MiB（其中 `data/` 449 件/752.48 MiB）＝Owner 门位**——宪法 §5
   "业务资产概念级退役＝Owner；物理不可逆删除＝Owner"；`docs/`+`scripts/`+`src/`+`config/` 212 件/2.83 MiB
   属治理面（AI 可下放，但须先补引用面扫描）。
8. **`pool_rollbackbomb_20261011` 结案前不可动**——工令 §2 原文规定；
   关联会话 `st-maint3-20261011` 心跳实测 0.1 分钟前（活跃）⇒ 照登为不可动项。

## 5. 复算命令（每条均已本班实测可跑；Git Bash 下已避 `git -C /d/…` 分域坑——一律先 `cd`）

```bash
# 面① 取数（-uall + 8 个白名单根；无 -uall 口径会漏判：实测 872 vs 1252 行）
cd /d/ZephyrAlpha && git status --porcelain -uall -- docs scripts src tests config data prompts .trae | grep -c '^??'   # 661

# 面② 逐件分账（apparent 字节 getsize 求和，非 du）
cd /d/ZephyrAlpha && python .runtime/tmp/st-fclean3-20261012/scan_lane_audit_faces.py

# 面② 族聚合 + 首末记录时间戳 + 速率外推 + 代码引用位（写面仅 out/*.csv）
cd /d/ZephyrAlpha && python .runtime/tmp/st-fclean3-20261012/rollup_and_rate.py

# 面① 四态 + 三件定窗（import 波二原语，未执行 scan_dev_delta.main）
cd /d/ZephyrAlpha && python .runtime/tmp/st-fclean3-20261012/census_untracked.py

# 面① 内容级归属 + 镜像副本 sha 实证
cd /d/ZephyrAlpha && python .runtime/tmp/st-fclean3-20261012/attribution_signals.py

# 读者语义复算（禁凭函数名；读到 :493-502 全量逐行＋:749 7d 窗）
sed -n '477,540p;740,800p' /d/ZephyrAlpha/src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py

# 轮转单口与上限
sed -n '55,140p' /d/ZephyrAlpha/src/zephyr/shared/io/audit_jsonl_writer.py

# A 态异常复算（暂存删除与未跟踪并存）
cd /d/ZephyrAlpha && git status --porcelain -uall -- scripts/tasks

# tiered_storage 目标目录"有码无跑"复算
cd /d/ZephyrAlpha && ls -d data/audit_history data/audit_archive 2>&1   # 两者均不存在
```

- 写面自证：四支脚本唯一写出点＝`.runtime/tmp/st-fclean3-20261012/out/`（`OUT` 常量单一入口），
  全目录内**无任何 `unlink`/`rmtree`/`remove`**；`scan_dev_delta.py` 的写面在 `main()` 内，本班未调用。
- ⚠ 未对任何在册工具跑 `--help` 或裸跑（波二 22 支无 argparse 工具＝执行主逻辑）。

## 6. 残余申报（未跑完，勿当已结案）

1. `audit` 面 5 个大件（`write_audit`/`bottleneck_ledger`/`worktree_drift_watchdog`/`safe_write`/`feature_flags`）
   的**读者**只到"路径定义/写侧 file:line"证据级；`write_audit.jsonl`、`safe_write.jsonl` 的读侧**完全未查**
   ⇒ 归档前必须补读（§3.1 首批候选里若含它们，须先补这一课）。
   另 `write_audit`/`bottleneck_ledger`/`worktree_drift_watchdog`/`emergency_track` 首末记录时间戳不可解析
   （记录体无 `timestamp` 字段或格式非 ISO）⇒ 速率与 30 日准入判据对这 4 族**暂缺**。
2. `gate_audit` 285 个"零字面引用"族（646.1 MiB）只完成**代码面**引用查；
   docs/裁定/看板/仪表盘 SQL 的引用面未扫 ⇒ 退役判据不完整。
3. `gate_audit/regen_clean/` 子目录件与两面内非 jsonl 件（`.diff`/`.json`）未做读者定性。
4. `data/strategy_intake/grid_*`（372 件/670.52 MiB）是否与 DB/冷库存在派生源
   （§4.2"同真源可派生→必并"）未查——需 `DatabaseService` 侧对账，本车道未跑。
5. 第六态反查只做在 116 件 basename+size 命中集上（88 sha 实证 / 28 反证）；
   其余 545 件未与 quarantine/safety/queue blobs 全量反查（成本）⇒ 按在册"袋会被 purge，抢救有时限"，
   全量反查应另起车道，勿拖到队列 purge 之后。
6. `.runtime/write_audit/` 4 件的写者身份未定（§3.4 收敛建议的前置条件）。
7. 工令"账面 182 / 实测 558"与本班 661 的差＝取数时刻差（在飞班 0-1 日桶 179 件在长）；
   未做"182 口径"的复算路径（工令未给其取数命令）⇒ 若总包要钉死账面数，需回问取数命令。
8. 内存红线：起批前实测 `mem_pct=59.3%、avail=25.96 GiB`（工令所称 75% 为 00:5x 波动值）；
   全程单进程分批，>64 MiB 件不整读。终检时未复量（残余）。
