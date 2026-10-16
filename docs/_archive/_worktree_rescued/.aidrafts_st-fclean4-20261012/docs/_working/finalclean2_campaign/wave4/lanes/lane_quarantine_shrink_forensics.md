---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
completes_when: 本案卷读数被总包在 dev 侧复核，且其中点名的在册缺陷被属主车道承接
generated_by: 本班只读车道（弱模型出案卷不出裁定），落地面由 st-fclean4-20261012 复核
session: st-fclean4-20261012
lane: wave4-lane_quarantine_shrink_forensics
role: 只读调研案卷（零删除、零 git 写、零改判据）
---
# 终清波四·车道案卷：quarantine 家族一夜缩 959 枚的取证（损失形态／时间线／机制归因）

> 原稿面＝`.runtime/tmp/st-fclean4-20261012/lanes/lane_quarantine_shrink_forensics.md`（TTL 临时区），本件为其入册副本；
> 数值口径以该案卷自带的时刻与参照点声明为准。
# 案卷：quarantine 面萎缩归属取证（终清波四）

> **口径**：Baseline A = 前班快照 2026-10-11T15:29Z（7,427 drift_* / 9,388 files / 679,859,943 B），
> 真源身份册 = `.runtime/tmp/st-fclean3-20261012/out/quarantine_drift_byte_audit.csv`（9,388 行逐件：
> drift_dir/relpath/bytes/bucket/q_sha256，实测复核 rows=9388 distinct_drift_dir=7428... 见 §2）。
> Measurement B = 本班 2026-10-12T13:21Z（6,468 / 8,062 / 658,070,696 B）。
> 本班所有测量均带 `date`(UTC+8) + `date -u`(UTC) 双戳；审计文件为 UTC 口径。

## 0. 时钟锚
- 本班开测：local `Mon Oct 12 21:32:49 2026` / UTC `Mon Oct 12 13:32:49 UTC 2026`（machine 时钟 UTC+8）。
- Baseline A 快照：2026-10-11T15:29Z。Measurement B：2026-10-12T13:21Z。窗口 ≈ 21.9h（wall）／≈ 8.5h（到 00:01Z 清扫）。

## 1. 关键代码事实（实测 file:line，非推测）
- `_sweep_quarantine()`（`worktree_drift_watchdog.py:545-606`）**只整目录删**，唯一删除原语
  `safe_rmtree(d, allowed_prefix=qdir)`（:590）；**empty_shell 分支（:579-580）仅在 `_dir_has_files(d)`==False 时触发**；
  expired 分支（:581）需 `ts < now-30d`。审计记录 `quarantine_retention_sweep`（:594-603）字段
  = ts/verdict/kind/file(目录名)/retention_days — **不含被删内容的 sha**（空壳本就无内容可记）。
- `_snapshot()`（:479-498）P2-2 修复"先验源再建目录"（:491 `is_file()` 判在 :493 mkdir 之前）——但
  **残余竞态**：若 :491 通过、:494 `write_bytes` 抛 OSError，则 mkdir 已建 → 留下空壳（:497 捕获 return ""）。
  ⇒ 空壳有两条来源：①带外删文件后残壳；②快照写失败自残壳。**§3/§5 用名字归属判别二者**。
- 写豁免：`write_audit_daemon.py:84` `(".runtime/quarantine", True)` —— **quarantine 下的写/删不进 write_audit**（避免自激）。
- ops_guard `PROTECTED_PREFIXES`（`scripts/ops_guard.py:90-100`）含 `.runtime/quarantine`；:96 注释实证
  "2026-08-25/26 两起带外裸删（drift_* 选择性清除、零审计）"。人工处置须 `ZEPHYR_FORCE_DELETE=1`。

## 2. 损失形状（whole-dir vs selected-file）— 实测（2026-10-12T13:36–13:37Z）

单流进程走盘一次（哈希 8,062 现存件），对 Baseline A 身份册逐件 join：

| 维度 | 值 | 读法 |
|---|---|---|
| 复测现存 drift_* 目录 | **6,468** | == Measurement B（尺子自校，零偏差） |
| 复测现存文件 / 字节 | **8,062 / 658,070,696 B** | == Measurement B（字节精确吻合） |
| Baseline 目录今在 | 6,293 | 其中**字节全同、零改写** |
| Baseline 目录今失踪 | **1,134** | 全由 watchdog `empty_shell` 清扫（见 §4） |
| 新增目录（>15:29Z 产） | 175 | watchdog 正常在飞增长 |
| Baseline 文件现存·同 sha | **7,886** | 未被动过 |
| Baseline 文件现存·异 sha | **0** | **没有任何文件被就地改写** |
| Baseline 文件消失 | **1,502** | 其中 **1,500 在"整目录失踪"里**，仅 2 在存续目录里 |
| 现存 0 文件目录 | **0** | 空壳已被清（与 §4 清扫一致）；此刻无新空壳 |

**形状定论：损失是"整目录级"，不是"从存续目录里选择性抽文件"。** 1,502 消失件里 1,500 枚随其目录整体消失，
只有 2 枚从存续目录消失（可视为正常在飞抖动）。`diff_sha=0` ⇒ 没有任何文件被篡改，只有"在/无"两态。

**搬迁 vs 真删（内容再出现测试）**：消失的 1,500 件里，其 `(relpath, sha)` 对
**在现存全树任何位置都不再出现 = 1,206 枚**；仍出现在别处 294 枚（§4 of lane_quarantine：热件 relpath 重复度极高，
`capability_canonical_file_registry.yaml` 单 relpath 80 份快照，故"别处仍在"多为幸存的**同 relpath 重复快照**，非搬迁）。
⇒ 主判 = **内容真删**（1,206/1,500 = 80.4% 全树查无此字节），非 move。

## 3. 空壳与目录直方图（现存 6,468 目录 / 每目录文件数）— `out/shrink_dir_histogram.json`

```
files-per-dir: 1→5636  2→469  3→124  4→113  5→93  6→32  7→1  （0 文件目录=0）
```
> 现存目录几乎全是 1 文件（87.1%）；失踪的 1,134 目录基线均值 1.323 文件/目录（多为 1 文件壳）。
> **此刻无 0 文件空壳** ⇒ 不是"新增空壳被清"的良性快照竞态（那要求目录生于空），而是"既存有人文件的目录被掏空"。

## 4. 时间线与 empty_shell 清扫 + tamper 检测器取证 — `out/shrink_tamper_and_seteq.json`

**watchdog 审计**（`.runtime/audit/worktree_drift_watchdog.jsonl` + `.1`，total_lines=97,648，
时标跨 `2026-09-23T06:41:55Z → 2026-10-12T13:37:35Z`，含本班）verdict 计数：
grace_suppressed 26276 / shielded_add 20078 / healed 10316 / alerted 9419 / **quarantine_tamper 8995** /
auto_staged 6843 / observed 4135 / **quarantine_retention_sweep 3493** / claimed 2460 / deletion_alerted 2365 /
grace_delete 1643 / deletion_observed 675 / dead_session_swept 461 / claimed_delete 320 / auto_claimed 111 /
heartbeat 23 / merge_suppressed 14 / derived_auto_committed 3。（bad=18 行）

**清扫 kind 全仓历史：empty_shell=3,493 / expired=0 / 非空目录被删=0。**
⇒ **watchdog 自身删除路径从未删过任何有文件的目录**（代码印证：`_sweep_quarantine` 只经 `safe_rmtree` 整目录删，
且 empty_shell 分支仅在 `_dir_has_files==False` 时触发；expired 分支需 ts<now−30d，本窗口零到期）。

**2026-10-12T00:01–00:02Z empty_shell 清扫分钟直方图：00:01=710、00:02=424 → 合计 1,134**，
**与 §2 "Baseline 目录今失踪=1,134" 精确相等**。集合等式实测：
`absent_dirs ⊖ swept@20261012 = ∅` 且 `swept@20261012 ⊖ absent_dirs = ∅`、`absent ⊆ swept_all = True`。
⇒ **每一枚失踪的基线目录都是被 watchdog 的 empty_shell 清扫在 00:01Z 移除的；无一枚在清扫之外消失。**
即：目录实体由 watchdog 删（且只在目录已空时删），但**目录内文件的消失发生在清扫之前、且不在 watchdog 删除路径内**。

**`quarantine_tamper`（带外删除检测器）取证 — 关键负面结论**：
- 该 verdict 记录 `kind`? 无；记录 `file`（=登记时的快照**文件路径**，来自 `known_quarantine`←`_snapshot` 返回 :495/:1355）、
  `pid`、`process`、`quarantine_content_sha256`、`worktree_now`。
- 触发条件 `if not (root/d).is_dir()`（:1153）对**文件路径恒为 True**（文件永不是目录）⇒ **登记后的下一扫描必发一条 tamper**，
  随即 `known_q.remove(d)`（:1170）遗忘该条目。**⇒ 带外删除检测器对每枚快照只观察一个扫描周期（≈60s），此后结构性失明。**
- 实测 `quarantine_content_sha256`：**real-sha（文件仍在）8,641 / "missing" 0**。⇒ **检测器从未观测到任何"文件缺失"**；
  8,995 条全是"文件当时还在"的**误报**（把存在的文件当被删登记）。
- 删除窗（15:29Z→00:01Z）内 tamper=147 条，**其中引用 1,134 失踪目录之一者 = 0**。
⇒ **watchdog 的 `quarantine_tamper` 检测器没抓到这次删除**（0 missing、窗口 0 命中失踪目录）——
**但这不等于"零审计"**：见 §5，删除被 `ops_guard` 进程内钩子逐件记录在案。

**⇒ 本案核心归因（§5）：这 1,502 文件删除并非"零审计带外裸删"——`ops_guard_delete.jsonl` 有逐件审计。**

## 5. 带外删除者指纹检索 — 已定位（`out/shrink_deletion_faces_window.json` / `shrink_epoch_faces_window.json` / `shrink_gateruntimecleanup_attribution.json`）

对窗口 `2026-10-11T15:29Z → 2026-10-12T00:30Z` 各审计面逐一命中（尺子正对照：先以 ISO 串筛命中
safe_rmtree=1,149，证明窗口筛可行；再以 epoch→UTC 重筛数字时标面，修正首轮"0 命中"假阴性）：

| 审计面 | 存在 | 覆盖窗口? | quarantine/drift 窗口命中 | 读法 |
|---|---|---|---|---|
| **`ops_guard_delete.jsonl`** | ✅ | 是 | **1,502 个 distinct `.runtime/quarantine/drift_*` 文件对被删**（3,004 行，guard_remove+inprocess_allow 双记） | **真凶审计在此** |
| `safe_rmtree.jsonl` | ✅ | 是 | window drift 目标 distinct=**1,135**（∩absent=1,134） | = watchdog 扫空壳（整目录），非删文件者 |
| `.runtime/audit/write_audit.jsonl(.1-.3)` | ✅ | **否**（最早仅 01:01Z 10-12，窗口段已轮转丢弃） | 0（窗口不可见） | **留存盲区**：删除时刻已滚掉 |
| `.runtime/audit/safe_write.jsonl` | ✅ | 是 | **0**（窗口 1,638 条全非 quarantine） | quarantine 走裸 `write_bytes` 非 safe_write_text ⇒ 此面无痕 |
| `registry_mass_deletion.jsonl` | ✅ | **否**（末条 2026-10-10T02:05Z 后停记） | 0 | **在册盲区**：该面早已不再落新账 |
| `derived_file_deletion_foreign_staged.jsonl` | ✅ | 是 | 2（session st-deadcure3b，docs/_ 件，非 quarantine） | 噪声 |
| `.runtime/evaporation_blackbox/blackbox.jsonl` | ✅ | 是（每 5min，104 帧无断档） | **不适用**——只记 git status **非 ignore** untracked 计数+tracked 删除；quarantine 被 gitignore ⇒ 结构性失明（其 :349 反指"对照 .runtime/quarantine"=循环盲区） | 无法见证 quarantine 内删 |
| `stale_staged_cleanup.jsonl` | ✅ | — | 0 | 无关 |

**决定性证据（`ops_guard_delete.jsonl` 窗口内 targeting `.runtime/quarantine/drift_*`）**：
```
distinct_quarantine_file_pairs_deleted = 1,502   ← == §2 files_gone（1,500 absent-dir + 2 present-dir）
deleted_pairs_matching_baseline_gone   = 1,500   ← 逐一对上 Baseline A 消失件 (dir,relpath)
deleted_dirs = 1,135  (∩absent = 1,134)          ← 逐一 == watchdog 扫空壳的目录
verdict            = ALLOWED (3004/3004)
is_protected_zone  = true   (3004/3004)          ← ops_guard 明知在保护区
reason = "reconciler GATE-RUNTIME-CLEANUP 已声明 delete（声明制直通）"(1502)+ "…已声明 delete"(1502)
session_id: ops-guard-unknown ×3026, st-maint3-20261011 ×77
```
**⇒ 删除者 = `GATE-RUNTIME-CLEANUP` reconciler（TTL 清理器）。** 它把 1,502 个 drift 文件（含保护区内）
经 **"声明制直通"** 让 ops_guard 放行（`verdict=ALLOWED` 尽管 `is_protected_zone=true`）；删空后 drift 目录成空壳，
watchdog 于 00:01Z 合法扫壳。三把独立尺互证闭环：GATE-RUNTIME-CLEANUP 删件对(1,502)+safe_rmtree 扫目录(1,135)
↔ §2 消失件(1,502)/消失目录(1,134) **精确对齐**。

## 6. 候选机制逐一核查（Task 5）— `out/proc_snapshot.json`（109,841 B，快照 2026-10-12T13:48Z，watchdog PID 10548 daemon 在跑）

| 候选 | 能删 quarantine 内文件? | 窗口内实际运行? | 判定 |
|---|---|---|---|
| **GATE-RUNTIME-CLEANUP reconciler**（TTL 清理，声明制直通） | 能（已证逐件删 1,502） | **是**（ops_guard_delete 3,004 窗口记录） | **命中，真凶** |
| watchdog `_sweep_quarantine` empty_shell 分支 | 只删**空**目录（整目录），不删文件 | 是（00:01Z 扫 1,134） | 只扫壳，非删文件者 |
| watchdog `_sweep_quarantine` expired 分支 | 整目录删 | 全仓历史 expired=**0** | 未触发（30d 未到期） |
| `scripts/session_worktree.py::_rescue_untracked_files` | `shutil.move` **移**（留 mapping.json 台账） | — | **排除**：目标=worktree `git status` 未跟踪件，非被 ignore 的 `.runtime/quarantine`；move 保内容，与"1,206 全树查无字节"矛盾 |
| `src/…/session_worktree.py` `_quarantine_file`/`_sweep_quarantine` | 根=`.runtime/**orphan_quarantine**`（异目录）；`safe_rmtree(allowed_prefix=orphan_quarantine)` 碰不到本面 | — | **排除**（只往 `.runtime/quarantine` **写** patch :864，不删 drift） |
| `.runtime/tmp` 24h TTL 清理 | 若视 quarantine 为 tmp 则危 | 进程面窗口无 tmp-clean 常驻 | 未见其删 quarantine 证据（quarantine 非 tmp 子路径） |
| `git clean`（-fdx）主区 | 可清 ignore 文件 | **未见**——blackbox 窗口无 untracked/index 崩塌，ops_guard 本面无 git_clean；且 -d 连目录删不留空壳，与签名不符 | **排除** |
| 匿名裸 `os.remove`/`shutil.rmtree` 带外删 | 会撞 ops_guard 保护区 BLOCK | — | 本案删件全 `verdict=ALLOWED`+GATE 声明直通 ⇒ 非匿名裸删 |

## 7. 不可判定项与所需证据

1. **GATE-RUNTIME-CLEANUP 的 scope 是否*应当*覆盖 `.runtime/quarantine`**——已证它*事实上*删了 drift 文件；
   但属"配置本就允许"还是"TTL 清理误把 quarantine 纳入可清集（作用域 bug）"，**本车道未读到该 reconciler
   计算删除集的源码/配置**（`commit_gates/reconciler_file_ops_gate.py` / 声明直通侧未逐行核）。
   所需证据=该 reconciler 声明删除根的白名单来源（只读读源码/配置）。定性（intended vs 误伤）**归总包/Owner**。
2. **session 归因偏薄**：3,026/3,103 记录 `session_id="ops-guard-unknown"`（reconciler 未带会话身份运行）——
   机制清晰但会话归属弱（st-maint3-20261011 仅 77）。所需证据=reconciler 本轮触发上下文 / `reconcile_execution_log`。
3. **窗口内删除逐分钟曲线**：ops_guard `timestamp` 可精确到秒，本车道仅定界窗口 [15:29Z, ~00:00Z]；逐分钟可后补。
4. **write_audit/registry_mass_deletion 对窗口失明**系留存/停记（非未发生）；若需第三方时间线交叉=查 D: 卷 NTFS USN journal。

## 残余未覆盖面

- 未读 GATE-RUNTIME-CLEANUP reconciler 删除集实现/配置（作用域"是否允许碰 quarantine 前缀"仅由 ops_guard 记录侧反推，未从实现侧证实）。
- 未 `git check-ignore` 实测 `.runtime/quarantine` 的 ignore 态（据 ops_guard/blackbox 行为强推断）。
- 未跑窗口逐分钟删除曲线；未起 DatabaseService 查 `reconcile_execution_log` 里 GATE-RUNTIME-CLEANUP 删除声明台账。
- 未判定 GATE-RUNTIME-CLEANUP 删 drift 是否"合规"——本卷只出事实：全审计、ALLOWED、明知保护区、声明直通；合规/Owner 级定性归总包。
- 零越界：除本卷 + out/ 机读表外零写面；未删任何件、未 `--help`/裸跑 governance 工具、未调 `SessionRegistry.list_active()`、进程快照只读。

## 8. 结案陈词（供总包裁定，非裁定本身）

1. **损失形状 = 整目录级**（非存续目录内选择性抽件；`diff_sha=0` 无篡改）。1,502 消失件里 1,500 随 1,134 目录整枚消失，2 枚从存续目录消失。
2. **时间线界**：last-known-present=**2026-10-11T15:29Z**（Baseline A 满员快照）；first-known-gone-as-empty=**2026-10-12T00:01Z**（watchdog 记 empty_shell）；实体删除落此 8.5h 窗内。
3. **审计存否 = 存在**（非零审计带外裸删）：`ops_guard_delete.jsonl` 逐件 1,502 记录，`verdict=ALLOWED`/`is_protected_zone=true`/reason=GATE-RUNTIME-CLEANUP 声明直通。唯 quarantine 专属 tamper 检测器（0 missing、窗口 0 命中）与 write_audit/registry_mass_deletion（留存/停记）对本案失明——**"看错门才会误判零审计"**。
4. **最强支撑机制**：**GATE-RUNTIME-CLEANUP TTL 清理 reconciler** 经 ops_guard "声明制直通"删除 1,502 个 drift 件（明知 `.runtime/quarantine` 为保护区仍放行），watchdog 随后合法扫 1,134 空壳。
5. **对去重**：**不阻断事实层去重**（面此刻稳定、无空壳、无持续裸删者；删除者=按需 reconciler）。但**阻断"以本面为唯一真源且默认可静默再生"**——去重/清扫方案须与 GATE-RUNTIME-CLEANUP 删除集协调。建议总包裁：是否收紧该 reconciler 对 quarantine 的声明直通范围（本卷定性证据已备；改配置/收紧=写面，越出本只读车道权限）。
