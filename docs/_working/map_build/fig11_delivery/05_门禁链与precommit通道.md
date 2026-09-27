---
ttl: task_bound
completes_when: 图11 封矿且 D11-C05~C07 环节进 config/dev_delivery_map.yaml 四件套后本件转归档参考
title: 图11 作业簿05·in-process 门禁链与 precommit 通道（D11-C05/C06/C07）
owner: st-mapbuild-20260924（W-B 车道）
---

# 05_门禁链与precommit通道

> 坐标纪律：本簿全部 `文件:行` 为 2026-09-24 在 worktree `.aidrafts/st-mapbuild-20260924` 实查；行号随并发漂移，判据一律走簿末 §末-3 命令。
> 计数纪律：两册均为热文件会漂，本簿所有门禁数量写"以册为准，实测当日 N 条"，图节点 MUST 读字段/跑命令而非抄数（宪法 §4 第 3 条）。
> 引用避坑同簿 04：裁定号去井号、宪法引用只写"宪法 §N 第 M 条"真名口径。

## §0 覆盖环节

- **D11-C05** in-process 门禁链执行
- **D11-C06** 暂存与提交本体
- **D11-C07** precommit 通道（裁定 341 方案二在网关内补获执行权的一拍）

族职责一句话：拿锁之后、ref 移动之前的一切"验货"——C05 在暂存前验同一进程的声明式门，C06 把货装上 index 并落 commit，C07 在落 commit 前用子进程重放一遍 shell 侧门禁册（因为 `--no-verify` 让 git hooks 永不触发）。

---

## §1 D11-C05 in-process 门禁链执行

### 上
- 唯一执行点：`commit()` 临界区内 `self._check_gates_with_drift_watch(...)`（`git_commit_gateway.py:2529-2541`，无锁降级路径第二调用点 :2570-2581）→ 结果裁决 `self._check_gate_results(gate_results)`（:2542，函数体 :1881-1901）。
- 链的装配：`GitCommitGateway.__init__` 经 `auto_register_gates`（import :98-100，实现 `gate_auto_registrar.py:150-265`）从名册动态注册；名册=`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（`REGISTRY_REL_PATH` `gate_auto_registrar.py:87`）。
- 规模：**以册为准，实测当日 total_gates 字段=99、gates 列表实读 99 条、enabled=true 99 条、内存实注册 99 台**（三数当场相等，复跑 §末-3 命令 1）；`files_trigger` 条件触发 26 台（册内计数与内存计数一致）。册头 :40 行注明 2026-09-23 由 114→99（st-gslim P4 七簇合并）。
- 开关输入：`flags.yaml:91-94 gate_preflight` / `:86-89 gate_result_cache`（实测当日均 enabled:true，复跑命令 2）。

### 下
- 给 C06：`_check_gate_results` 返回 None 才进 `_commit_locked`（:2542-2547）。
- 给簿 04 C01：门阻断 → 六门有专码、其余全落 `COMMIT_FAILED`→exit 1（映射函数 :1881-1901，穷举见簿 04 §1 内矩阵）。
- 给观测：`_audit_commit_block_event`（:1831-1849，写 `.runtime/audit/commit_block_events.jsonl`）+ 慢门统计 `_stat_ms/_stat_flush`（`commit_gate_registry.py:440/:450/:463/:471/:486/:488/:491`）。
- 给逃生审计：`_audit_allow_overlap_usage`（check_all 起手 :414）。

### 内（链的编排语义 = 本车道实查任务，父-子-孙）
- **排序语义**：`check_all` 逐台 `sorted(self._specs.values(), key=lambda s: s.priority)` 升序（`commit_gate_registry.py:431`；预跑侧快照同口径 `specs_sorted()` :502-504）。priority **真源在代码**（各 `make_*_gate()` 返回的 GateSpec 字段，默认 100，:339）；名册 YAML **无 priority 字段**（实读 keys 并集=enabled/factory_function/files_trigger/gate_id/module_path/register_line/source 七种），册头 entry_schema 亦自述"priority: informational — 从 GateSpec 读取，YAML 不覆盖"，装配器 docstring 设计权衡第 4 条重申（:53-55）。实测当日 priority 区间 **28→200**（首=PROTECTED-PATHS，次=FORGED-GW-MARKER 29，末=CAPABILITY-OVERLAP 200；复跑命令 1）。
- **撞号 fail-closed**：`register` 检同 priority 不同 gate_id → 抛 `GateRegistrationError`（:380-389，error_code ZA-GV-0050 :322）；同 gate_id 覆盖幂等（:390）；"后到者让位"五例先例内联（:386-388）。病根注释：warn-only 期 AI 把 warn 当通过（:372-375）。
- **装载 fail-closed（裁定 351，2026-09-19）**：名册存在但解析失败/根非 dict/gates 非 list/含非 dict 条目 → 抛（`gate_auto_registrar.py:104-123`）；名册存在但空列表 → 抛（:177-180）；任一台 import/getattr/factory/register 失败 → 逐台收集后统一抛（:204-235）；**名册文件缺失**是唯一容许的降级=0 门装载 + warn 留痕（:105/:140-146，防蒸发责任转交 REGISTRY-MASS-DELETION 门）。
- **装载数对账**：条数↔`total_gates` 字段 :240-242、enabled 去重集合↔实际注册集合 :244-254、重复 id :246-248，任一不一致 → logger.error + 抛（:256-259）。即"字段落后于列表"这类热册漂移在 in-process 册上**会被当场拦死**（对照：shell 侧 `gate_registry.yaml` 无等价闸，见「旁」与本簿溢出 O-C9）。
- **执行序四道闸（按代码序，命中即 continue 并留 skipped 记录）**：①`files_trigger` 未命中 → passed=True "skipped: files_trigger 未命中（P5 条件触发）"（:432-441，匹配语义=目录前缀尾随 `/` / fnmatch 通配 / 子串，`GateSpec.files_trigger` 注释 :340-344，注入点 `gate_auto_registrar.py:221-223`）；②`skip_gates`（worktree 物理隔离）→ "skipped: worktree 物理隔离（无检测对象）"（:442-451，集合单一真源=`session_worktree.py:367`，**实含 4 门** HELD-OVERLAP/CLAIM-REQUIRED/FOREIGN-CHANGE-DETECTION/WORKTREE-REQUIRED，网关侧注入门槛 :2389-2395）；③结果持久缓存命中 :452-464（P2⑧，白名单=`gate_cache_preflight.py:43` CONTENT_SCAN_CACHE_WHITELIST 实测当日 14 台，只缓存 passed=True，key 含 `own_scope_hash` :140）；④锁外预跑采信 :465-472（P2⑦，白名单由调用方 gateway:2464-2499 计算并带指纹 F，锁内 F′==F 才用 :2513-2523）。
- **单门异常 = fail-closed 且不断链**：`spec.check` 抛异常 → 记 `passed=False, detail="gate 异常（fail-closed）"` 后 continue（:474-487；INVARIANTS 头 :8）。
- **own_scope 拆分（宪法 §3 第 1 条的提交侧实现）**：原语 `_build_own_scope`（`commit_gates/_diff_helpers.py:476-496`，范围=本次 files ∪ SessionRegistry held_files，二者皆空返回 None 让调用方退化为全扫，registry 读异常 fail-open 退 files-only）；标准拆分 `_split_own_foreign`（:549+，C3 名单机械 own 化）；外来 staged 只落审计不阻断 `_audit_foreign_staged`（:518-540，文件名 `<gate 小写下划线>_foreign_staged.jsonl` 于 `.runtime/gate_audit/`，含 `_attribute_foreign` 尽力归因 :500-517）。册面 own_scope 字段为**机生**（`gate_registry.yaml` 的 `own_scope`，实测当日 commit-gate 通道 33 台 True；in-process 册无此字段 → 图节点若要 own_scope 必须挂 shell 册，见溢出 O-C12）。
- **链窗漂移监视（T4-2/CAND-GATEMECH-004 升硬）**：链前后 tracked 区指纹比对（gateway:2902/:2918，快照原语 `_tracked_area_snapshot` :2746，归因 `_attribute_tracked_writes` :2820，白名单真源=`gate_tracked_write_allowlist.yaml`）；变化文件全命中白名单→warn+审计；存在未归因→**own/foreign 二分**：清单外（他会话 WIP，pathspec 构造性隔离）降级 warn（:2934-2941）、清单内且未给 `--allow-tracked-drift` → 追加 `TRACKED-DRIFT-READONLY passed=False`（:2942-2968）。读缓存窗口随链开闭（:2906/:2916-2917）。
- **链前置两道硬闸（编排上属本环，实现不在链内）**：reconciler `critical_warn` 只横幅不阻断（:2413）；`block_next` 阻断并返回 `COMMIT_FAILED`（:2419-2424，横幅函数 import :128-129）；两者均在**拿锁之前**，故不写 commit_block 审计。另 PG 探针前置刷新（:2397-2408，供 depgraph 系门区分"DB 离线降级"vs"真错"）。
- **预检（P0-A，锁外同函数复用）**：`commit_preflight.run_preflight`（:411-460+）跑 `PREFLIGHT_GATES` 白名单（实测当日 **19** 台，`commit_preflight.py:107`），一过式收集不短路 + 逐项逃生旗提示（`_ESCAPE_HINTS` :456）；准入判据=门输入面仅 files∪磁盘∪会话态∪注册表、**禁依赖共享暂存区**（头 INVARIANTS :8）；`run_preflight` 永不抛（ERROR_CONTRACT :13）；审计 `.runtime/audit/preflight_events.jsonl`（:349/:397-405）。与 P2⑦ 的关系=正交互补且**共享两白名单不同集合**（19 vs 14），图节点不宜合并画。
- 自动化程度：全自动（含装载、对账、归因、审计）；无 human_gate。

### 旁（撞车面五选一）
- **与 C07 是否同物 = 本车道实查任务三，结论：不是同物，但同一条链的两层，边界三证**（详证见 §3 C07）。
- **与前战役文档 `docs/_working/commit_chain_mining/15_gate_chain.md`（2026-09-22，"门禁链全景清单（171 台）"）**：同对象不同目的（彼挖成本分档 T0-T3 与死因燃烧模型，本簿挖编排语义）。处置=**引用**（本簿不重述分档；其"L2 114 台 / priority 28→200→830/833"数据已被 09-23 七簇合并推翻为 99 台/28→200，见「史」与溢出 O-C11）。
- 撞 `gate_registry.yaml`（shell 三通道合并册，180 条 / 生成器 `generate_gate_registry.py`）：本环挂 **in-process 册**，该册挂 **通道归属**（55 pre-commit + 113 commit-gate + 12 manual）。处置=骨架 §3 第 9 行"引用+扩展"维持，本簿补一条挂接义务：**新 in-process 门须两册同步**（in-process 册条目 + shell 册 commit-gate 通道自动收录，靠生成器非手工）。
- 撞图14 施工流 15 步（Step10 落地/验收）：**引用**。
- 撞 GOMAP：`config/governance_operations_map.yaml:16-19` 明示"门禁是每模块配套，非运行时流水线节点"→ **引用**（本图立图正门依据）。
- 撞 15 步施工流之外的"capability 卡片/gate 卡片"面（`data/capability_cards/`、`gate_digest_registry.yaml`）：卡片=判据的展示层，本环=判据的执行层 → **引用**（簿 04 C02 为二者接口）。

### 史
- 12 个硬编码 `_check_*` → 4 门声明式注册（gateway 头 INVARIANTS :8，架构债务 #AD-001）→ 75/76 显式 import + register → YAML 动态注册（`gate_auto_registrar.py:20-21`、名册 description L9-13 全链留痕）。
- 装载器自身由 fail-open → fail-closed（裁定 351，2026-09-19）；旧 fail-open 病根"坏门静默免检"（:40-49 逐字）。
- priority 撞号 warn-only → 抛错（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2，`commit_gate_registry.py:372-379`）。
- 2026-09-23 七簇合并 114→99（名册 :40 注：REFERENCE-INTEGRITY / PERMANENT-SYSTEM-TRIGGER / GATE-VOCAB / DEPGRAPH-ENFORCEMENT / MAP-ALIGNMENT / BLUEPRINT-HEADER / COMPLEXITY-GUARD）→ 前战役文档 171 台口径当日失效。
- TRACKED-DRIFT 从"无差别连坐硬阻断"→ own/foreign 二分（2026-09-13 极限红蓝 F3，病根"实测三连中每次整链白跑 19-58s，重试放大 4-6×"，gateway:2924-2933 逐字）。

### 新
- P2⑦/⑧（2026-09-10 方案施工，2026-09-12 Owner 批准转正并声明"回滚通道永久有效=flag OFF（+删 `.runtime/gate_cache/`）"，`flags.yaml:88/:93`）；红蓝#2 缓存投毒/指纹失效 4/4 全防的留痕在册内描述里（同一行）。
- P5 条件触发（2026-09-23 st-gslim，实测当日 26 台带 files_trigger）= 链的最大一次吞吐改造。
- 外部对标一句话：pre-commit 框架自身的 `--hook-stage`/`fail_fast` 语义在本域被显式禁用（gateway:3308"以 foreign 失败掩蔽 own 失败→误放行"），即本域 chose 全跑+归因而非首败即停——与业界 CI 的 fail-fast 相反，属"连坐成本高于白烧成本"的量化结论（数据见前战役 15 号文 §C）。

---

## §2 D11-C06 暂存与提交本体

### 上
- 唯一入口：门全绿后同临界区 `result = self._commit_locked(session_id, existing, full_message, gw_marker)`（gateway:2547；无锁降级路径 :2587）。
- 输入构造在锁外：GW 标记与逃生尾标（:2426-2450，`_GW_MARKER_FMT` :216、`_GATEWAY_ENV` :215）。

### 下
- 产出=HEAD 移动 + `CommitResult(OK, commit_hash)`（:3517-3521）→ CLI exit 0（簿 04）；`.runtime` 侧产物：孤魂/慢/OK 采样 jsonl（:3499-3507/:2590-2608）、post-commit reconciler 链（:2610，环 58+ 台，骨架 C11）、handoff（`_commit_locked_finalize` :3539-3545）。
- 簿 03 S07/S06 与队列落地侧（簿 06 C10）复用同一段代码（零适配），故本环是"全图唯一真 git 落地"的公共底座。

### 内（八拍穷举，全实查行号）
1. **gitignored-tracked 分离** `_stage_gitignored_tracked`（:2698-2716）：已删+已跟踪→`git rm --cached`；已改+已跟踪→`git add -f`；未跟踪 gitignored→跳过；判定原语 `_filter_gitignored`（:2653，`--no-index` 检测，分批 300 防 WinError 206）。
2. **pathspec 文件** `_write_pathspec_file`（:4045）：统一 `--pathspec-from-file` 绕 Windows 命令行长度上限（`_commit_locked` docstring :2980）。
3. **add/rm 分流** `_add_and_remove_normal_files`（:3008-3060）：existing→`git add --pathspec-from-file`（:3028）；deleted→`git rm --cached --ignore-unmatch --pathspec-from-file`（:3045-3047，ARCH-030 病根=对 delete 文件 add 报 "pathspec did not match" 中断全流程）。失败即 `COMMIT_FAILED`（:3032-3035/:3056-3059）。
4. **无 pathspec 判定** `_should_use_no_pathspec`（:2646-2651）= `len(normal_files) < len(files)`（含 gitignored 目标时必须无 pathspec，否则 git 吞不到）；调用侧 :3481。
5. **staged 校验** `git diff --cached --quiet`（:3466-3472）→ returncode 0 即 `NOTHING_TO_COMMIT`（exit 1）。
5.5 **precommit 通道**（=C07，:3473-3479）：阻断转 `COMMIT_FAILED` + `_audit_commit_block_event(elapsed=0.0)`。
6. **提交本体** `_commit_with_file_message`（:3657-3736）：merge 感知强制全量（:3674-3676，注释 :3665-3673 说明 git 禁 merge 期 partial commit + 收编可见性兜底 :3684-3687）→ rename fallback（`_has_staged_renames` :3607，命中 R100 则切无 pathspec :3677-3678）→ staged-clean 校验与自动 unstage（`_verify_staged_is_clean` :3620、`_unstage_non_target_files` :3639，二次不净即失败 :3700-3707）→ message 走 OS temp `gw_commit_msg_*`（:3710-3712，`#ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001` 治"项目根平行真源"）→ `in_commit_flow=True` 放行守卫（:3714，finally 复位 :3731）→ **`git commit --no-verify -F <msg> [--pathspec-from-file=…]`**（:3718-3720）→ `git rev-parse HEAD` 取 hash（:3723-3727）。
7. **孤魂检测**（:3488-3509）：`git merge-base --is-ancestor <hash> HEAD` 非 0 即记 `orphan_commit_detected` + 处方 `git cherry-pick <hash>`；**fail-open**（检测异常不改 OK 判定，:3508-3509）。病根=双锁统一 W4 孤魂 301a6ee82a（2026-09-16 晚）。
8. **finally** `_commit_locked_finalize`（:3523-3557）：红蓝触发 :3533-3537 → `session_shutdown` handoff :3539-3545 → `_verify_post_commit_index`（:4211，warn-only）:3547-3551 → pathspec 清理 → `os.environ.pop(_GATEWAY_ENV)`（:3557）。
- 链前置的两把 index 卫生清扫（属 C06 语义但发生在门链前，锁内）：`_sweep_intent_to_add_residue`（:4141，调用 :2510；ita 标志位常量 `_ITA_FLAG=0x20000000`/空 blob sha :631-634，B2 治本②）与 `_sweep_phantom_staged_adds`（:4166，调用 :2512，P3-2 治本=上次被拦提交的预暂存残留）；审计 `_audit_index_hygiene`（:637-651 → `.runtime/gate_audit/gateway_index_hygiene.jsonl`）。
- GW 标记防伪链：`[GW:<sid>]` 由网关独占写（:2427-2450）+ in-process `FORGED-GW-MARKER`（priority 29，链第二台）+ shell `POST-COMMIT-GUARD` reset 回滚（宪法 §9 第 8 条）+ 禁 plumbing 绕行（`git_guard.py:95`）——**四道**，图节点只画"标记防伪"一条边会漏两层。
- 自动化程度：全自动。

### 旁
- 与簿 03 S06（worktree 内 session commit）/S07（merge）：物理隔离路径复用同一 `_commit_locked`，差异仅在 skip 集合与 stash（引用）。
- 与簿 06 C10 landing：landing 调网关全门禁链零适配（骨架门②第 7 条），即本环是"直连/队列"两道的共同落地面 → **引用**，不另建第二落地路径。
- 撞宪法 §2 第 5 条"commit 后必做 `git log -1 --name-only` 核实归属"：本环的 pathspec 隔离 + staged-clean 校验正是该守则的机制担保（吸收为节点注解）。
- 撞 `gate-protected-paths` / in-process PROTECTED-PATHS（priority 28 链首台）：**引用**（保护区写入属簿 07 车道 C13/观测面）。

### 史
- stash 隔离（阶段3 前）→ worktree 物理隔离；`StashError` 类与 `stash_ref/stash_kept` 字段留向后兼容（:480/:490-491，死分支同簿 04）。
- `-F msg_file` 自 RULE-TWENTY 裁定 2（gateway 头 INVARIANTS :8，避 PowerShell 特殊字符）；`--no-verify` 与 `ZEPHYR_COMMIT_GATEWAY=1` 同期。
- `run_git` 三面治本史：A11 匿名管道假死（capture_output→临时文件重定向 :4283+，Windows 64KB 缓冲 C 级 join 死锁）、P2-2b timeout 分级（read 15s / write 60s / other 30s，:4247-4251）、A1 读缓存窗口（:4269-4275，与 C05 链窗同生命周期）。
- rename fallback 病根：`git add <新名>` 后目标呈 R100，pathspec 提交会漏侧文件（头 INVARIANTS :8 + :3657-3678）。

### 新
- 双锁统一·孤魂检测（2026-09-16）与 index 一致性复扫（B2 治本③）是最近两刀；外部对标一句话：与 lint-staged 的"暂存-改-重暂存"三段式相比，本环把"重暂存"降级为"检测+拒绝"（变异即 fail-closed，见 §3），符合其"提交内容==校验内容"不变量。

---

## §3 D11-C07 precommit 通道

### 上
- 调用者唯一：`_resolve_commit_result` step5.5（gateway:3473-3475）→ `_run_precommit_channel`（:3189-3272）。
- 法源：裁定 341 方案二（2026-09-19 Owner 批，:357 注释；W1-D2 st-final3-20260919 施工）；开关 `_precommit_run_enabled`（:411-427，读 `_PRECOMMIT_RUN_FLAG` :358，default=True，异常回退 OFF）。
- **flag 实名不符（本簿推翻性实查，见「新」）**：代码常量=`gate_precommit_run_enabled`，`config/flags.yaml:96` 在册键=`gate_precommit_run`；`global_flag_registry.is_enabled` 对未注册键走 `default`（`src/zephyr/shared/foundation/flags.py:279-296`），实测当日：`is_enabled('gate_precommit_run_enabled', default=True)=True` 且该键**未注册**，`is_enabled('gate_precommit_run')=True` 且已注册（复跑 §末-3 命令 3）。

### 下
- 放行 → 直接进 step6 落地；阻断 → 返回 message 前缀"门禁 GATE-PRECOMMIT-RUN 阻断"，转 `COMMIT_FAILED`（:3476-3479）→ **exit 1，无专用码**（簿 04 矩阵码 1 行含此支）。
- 审计：`_append_commit_anomaly_jsonl`（:1815）三类 event=`precommit_channel_infra_error` / `precommit_channel_blocked` / `precommit_channel_global_debt_warned`（:3259-3267/:3403-3411/:3442-3450）。

### 内（temp-index own-scope 全链，父-子-孙）
- 父 `_run_precommit_channel`（:3189-3272）：flag 闸 :3226-3227 → merge 闸（merge 携带分支侧已验提交）:3228-3229 → 空清单闸 :3230-3233 → `git rev-parse --git-dir` 定位（:3235-3239，**linked worktree 下 .git 是指针文件**故须绝对化）→ 临时索引 mkstemp 落于 git_dir（:3240-3241）→ env 四件（`GIT_INDEX_FILE` / `ZEPHYR_COMMIT_GATEWAY=1` / `PRE_COMMIT_COLOR=never` / `SKIP=_PRECOMMIT_CHANNEL_SKIP_HOOKS`，:3242-3248）。
- 子①**own-scope 临时索引构建** `_precommit_run_scoped`（:3274-3324）：`rev-parse --verify HEAD` 失败→`skipped=True` 放行（:3293-3296，空 repo 场景）→ `read-tree HEAD`（:3297）→ `_precommit_build_temp_index`（:3091-3108：`git add -f` 分批 200 只装本提交现存件 + `git rm --cached --ignore-unmatch --quiet` 移除删除目标）→ finally 删临时索引（:3319-3323）。git 调用统一走 `_precommit_git`（:3076-3089，env 携带 GIT_INDEX_FILE）。删除件**不进 `--files`**（无内容可检）仅在索引中移除（docstring :3200-3202）。
- 子②**D3 Phase-A 快败子集** `_precommit_fast_subset`（:3326-3364）：`SKIP = 原 SKIP + _PRECOMMIT_SLOW_TAIL_HOOKS`（:3338-3341 反选，慢尾清单 :364-387 实测 20 台，含 gate-triple-align/gate-schema-truth/gate-test/gate-21-manifest-drudge 等分钟级台）→ 单次调用逐 chunk 首败即 break（:3358-3359）；**故意不用 pre-commit 全局 fail_fast**（:3307-3308"会以 foreign 失败掩蔽 own 失败→误放行"）；子集开关 `_precommit_fast_subset_enabled`（:390-398：env `ZEPHYR_PRECOMMIT_FAST_SUBSET=0` 一键关，**pytest 环境自动关**）。
- 子③**全通道执行** `_precommit_execute`（:3110-3164）：`[sys.executable, "-m", "pre_commit", "run", "--files", *chunk]`（:3116）timeout=`_PRECOMMIT_RUN_TIMEOUT_S=900`（:359）；变异侦测重跑 `attempts=2`（:3126-3163，判据串"files were modified by this hook" :3155）；TimeoutExpired/FileNotFoundError → `infra_error`（:3144-3152）。
- 子④**失败裁决四态** `_precommit_decide_failure`（:3388-3451）：infra_error → warn+审计+**放行**（:3256-3268，"基础设施故障非违规证据，可用性优先"）；rc=0 放行（:3270）；mutation 重跑仍变异 → **阻断**（:3401-3417，带修改落盘=校验内容与提交内容不一致，fail-closed）；own_failed → **阻断**（:3419-3434，附 hook 清单）；foreign_failed → warn+审计放行（:3436-3450，存量全局债）。归因原语 `_precommit_classify`（:3366-3386）+ 段解析 `_precommit_failed_segments`（:3166-3187，`- exit code: N` 正则 `_PRECOMMIT_EXIT_CODE_RE` :408），且**剥离修复提示样板**再匹配（`_HINT_PREFIXES=("Fix:","->","python ","pass [")` :3379，病根=GATE-21 的 Fix 指引含批内生成器路径致 own 假阳）。
- SKIP 三门及理由（`_PRECOMMIT_CHANNEL_SKIP_HOOKS` :401-407）：`gate-commit-gw`（判定前提"hook 运行=裸 commit"，本调用即在网关内→恒真冲突）、`gate-worktree-required`（与 in-process WORKTREE-REQUIRED 双重计数冲突）、`gate-protected-paths`（**2026-09-24 四死信实证后加入**：该 hook 消息盲，而其 `[ARCH-APPROVAL]` 豁免语义定义在 message 上，实测 env 全链透传仍被杀；防护不降级=Layer-1 in-process PROTECTED-PATHS 消息感知继续全量拦）。注意 `flags.yaml:98` 描述仍只列前两门（Skip 清单已漂，见溢出 O-C13）。
- 规模口径：**以册为准，实测当日** `gate_registry.yaml` 的 `enforcement_channel=pre-commit` 台目 **55** 条；`.pre-commit-config.yaml` hook 全集 **68** 条（其中 `gate-*` 58 + 非 gate 10）。两口径命名形不同（册内短形 `GATE-12` 对 config 长形 `gate-12-blueprint-provenance`），严格 1:1 须按生成器映射核——本簿未做，标待补（溢出 O-C9）。
- 自动化程度：全自动（无任何人工豁免面）。

### 旁 —— **本环与 C05 的关系钉界（三证 + 结论）**
- **证一（载体不同）**：C05=同进程 Python 闭包 `GateSpec.check`（`commit_gate_registry.py:475`）；C07=子进程 `python -m pre_commit run --files`（gateway:3116）+ 独立临时 index（:3240-3248）。
- **证二（群体基本不相交）**：生成器注释逐字（`generate_gate_registry.py:643-648`）"#341 亲验：in_process 113 与 commit-gate 全等、与 pre-commit 交集 0"；本簿复跑实测当日 in-process 99 台 ∩ 册内 pre-commit 通道 55 台 = **恰好 1 台 `GATE-VOCAB`**（`in_process_gate_registry.yaml` 条目 module_path=`commit_gates/vocab_hardcode_gate.py` 与 `.pre-commit-config.yaml` hook `gate-vocab` 同一判据两处执行）→ 结论仍是"两拨门"，但"交集 0"断言今日已不成立（溢出 O-C10）。
- **证三（链位不同）**：C05 在**暂存前**（:2529，与 stage/commit 同临界区）；C07 在**暂存后、`git commit --no-verify` 前**（:3473-3475）。二者对同一 index 状态的两个时点负责，不可互换。
- **骨架判定=确认成立（C05/C07 不同物，不推翻）**；但骨架把 C07 写作"pre-commit shell 门禁通道"存在**易误读**：实测 git hooks 对经网关的提交**永不触发**（`--no-verify` :3718-3720；hook 自述 `.pre-commit-config.yaml:955`"经 gateway 的 commit 用 --no-verify 绕过本门禁"）。故 C07 不是"git hook 通道"，而是"网关内以子进程重放 pre-commit 框架的补执行拍"，其 hook 原生通道只服务裸提交/其他工具提交（那一支由 `gate-commit-gw` 反向拦截）。建议环节名改述为"precommit 重放通道"（溢出 O-C7b）。
- 与宪法 §3 第 1 条：own-scope 立法在提交侧的**第二实现**（第一实现=`_build_own_scope` 系列，§1 C05）→ 图节点建议以 `own_scope_mechanism` 字段区分两实现（temp-index vs files∪held 集合）。
- 与图14 15 步 / 与 GOMAP：**引用**（同 §1）。
- 与 `run_gate_chain.py`（hook entry 载体，`.pre-commit-config.yaml` GATE-VOCAB 行）：被 C07 以子进程方式复用 → **引用**。

### 史
- 裁定 341 之前：55 台 pre-commit 门在网关通道**零执行**，形成"守规会话永久免检"（:3192-3195 与生成器注释 :645-647 双处留痕）→ 方案二被 Owner 批准、flag 出厂 ON。
- D3 两段式（2026-09-22 st-commitchain-20260922）：从"逐 hook 调用"改"全通道减慢尾反选单次调用"（病根=50-commit 真落地套件逐 hook 会把时长乘 N 倍挂死，:3329-3331）；同批 ruff-format 移出慢尾（Owner E7 两段式定案 :385-386）。
- 变异处理从"直接阻断"改"重跑 1 次消解并发假阳后仍变异才阻断"（:3121-3124）。

### 新
- 2026-09-24 `gate-protected-paths` 入 SKIP（四死信 q-…-sweep-tail-0041/0050/0052/0053 实证）。
- **本簿最硬新发现（运维坑，建议按高优先处置）**：因 flag 名漂移，`flags.yaml` 上写的"回滚通道=flag OFF"对本通道**实际无效**（未注册键 + default=True ⇒ 恒 ON）；当前唯一可停用手柄是 env `ZEPHYR_PRECOMMIT_FAST_SUBSET=0`，且它只关 Phase-A 子集、不关通道本体（:390-398）。复跑判据=§末-3 命令 3。溢出 O-C8。外部对标一句话：业界 lint-staged/pre-commit 均把"绕过钩子"设计为显式 `--no-verify`（人的动作），本域把它反转为"网关代跑 + 显式 SKIP 清单"，方向正确，但**开关面与注册表必须同名**才谈得上 Owner 门位（宪法 §5 第 2 条的 flag 翻转在本通道不可翻转）。

---

## §末-1 溢出条目（骨架外发现，交总包落 00_skeleton，本簿未改骨架）

| # | 条目 | 建议落点 | 证据 |
|---|---|---|---|
| O-C7b | C07 环节名"pre-commit shell 门禁通道"→ 改述"precommit 重放通道（网关内子进程）"，并在真源格标注 git hooks 对网关提交恒不触发 | §1 C07 环节名+状态列 | gateway:3718-3720；`.pre-commit-config.yaml:955` |
| O-C8 | **flag 名不符致 Owner 停用手柄失效**：代码读 `gate_precommit_run_enabled`，在册键为 `gate_precommit_run`，未注册键走 default=True ⇒ 通道恒 ON | C07 状态列 + 建议总包列"提交链高危微修" | gateway:358 vs `flags.yaml:96`；`flags.py:279-296`；§末-3 命令 3 |
| O-C9 | 机生 shell 册字段与列表漂移：`total_gates: 174` vs 生成实数 180（`--check` 当场报 DRIFT 且 exit 1）；in-process 册同题由装载对账当场拦死 → 两册新鲜度机制不对称 | §0 门④可建性表 + §3 第 9 行 | `generate_gate_registry.py:665/:682-683` + 簿末命令 4 |
| O-C10 | 两通道交集实测=1 台（GATE-VOCAB 双执行），生成器注释"交集 0"断言过期 | C05/C07 关系边（画成"两层不相交"须加例外注） | `generate_gate_registry.py:643-648`；`gate_registry.yaml` GATE-VOCAB 条目 vs `in_process_gate_registry.yaml` GATE-VOCAB 条目 |
| O-C11 | 前战役文档口径过期：`commit_chain_mining/15_gate_chain.md` 的"114 台 / priority 830-833 / 171 台合计"已被 2026-09-23 合并推翻 | 图11 §3 重叠表新增一行"引用（标过期）" | 该文 :8-12 vs 本簿 §末-3 命令 1 |
| O-C12 | 骨架 C05 格"99 gate × priority × own_scope 分簇"不可从 in-process 册读出（该册 keys 无 priority/own_scope）；priority 在代码、own_scope 在 shell 册机生字段 | C05 真源格拆成两坐标 | `gate_auto_registrar.py:53-55` + 册 entry_schema L33-41 + keys 实读（命令 1）；`gate_registry.yaml` own_scope 计数（命令 5） |
| O-C13 | SKIP 清单已增至 3 门，`flags.yaml:98` 描述仍写 2 门（flag 描述与常量漂移，属文档矛盾=事故族） | 总包收口（flags 册描述面，车道禁直写） | gateway:401-407 vs `flags.yaml:98` |
| O-C14 | 链前置两道闸（reconciler `block_next` 硬阻断 / `critical_warn` 横幅）发生在拿锁与门链之前，骨架 C05/C11 均未归属 → 建议作为 C05 子环节登记（不增枝：同生产者同验证口径） | C05「内」向 | gateway:2413/:2419-2424、import :128-129 |

## §末-2 自审裁定

**干**。C05/C06/C07 六向齐；C05 把链的编排语义穷举到 priority 真源位置、撞号/装载/对账三处 fail-closed、四道执行序闸、own_scope 两实现、fail-open 分级判据（装载面与违规面=closed，性能与观测面=open）；C06 八拍全带行号含 GW 标记四道防伪；C07 钉死与 C05 的三证边界（**确认骨架两环节划分成立**，仅改述环节名）并翻出 flag 名不符这一停用手柄失效坑（O-C8）。欠账：C07 台目 55（册）↔68/58（config）的 1:1 映射未核（缺生成器短形↔长形映射表解读，已列 O-C9 待补）；C05「史」向未逐簇列 22→7 合并明细（属叶层实现，图不增枝）。溢=8 条。

## §末-3 实查命令（可复跑，全部只读）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd D:/ZephyrAlpha/.aidrafts/st-mapbuild-20260924

# 1) C05 链实测：内存注册台数 / priority 区间 / files_trigger 数 / 名册 keys
python -c "
import sys,yaml,io;sys.path.insert(0,'src')
from pathlib import Path
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry as R
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates as A
r=R();A(r,Path('.').resolve());s=r.list_all()
print('registered',len(s),'prio',s[0].gate_id,s[0].priority,'->',s[-1].gate_id,s[-1].priority)
print('files_trigger',sum(1 for x in s if x.files_trigger))
ks=set()
for e in yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml',encoding='utf-8'))['gates']: ks|=set(e)
print('roster keys',sorted(ks))"

# 2) 两册计数以册为准（勿背数）+ 通道拆分
grep -n "total_gates" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
grep -n "commit_queue_serializer\|gate_result_cache\|gate_preflight\|gate_precommit_run\|commit_queue_interactive" config/flags.yaml

# 3) C07 flag 实名核验（期望：yaml 键已注册=True，代码键未注册且 default=True 恒返 True）
python -c "
import sys;sys.path.insert(0,'src')
from zephyr.shared.foundation.flags import ensure_global_flags_loaded, global_flag_registry as r
ensure_global_flags_loaded()
print('code key registered:', 'gate_precommit_run_enabled' in r._flags, '| is_enabled=True?', r.is_enabled('gate_precommit_run_enabled', default=True))
print('yaml key registered:', 'gate_precommit_run' in r._flags, '| is_enabled?', r.is_enabled('gate_precommit_run'))"

# 4) shell 册新鲜度可红判据（DRIFT + exit 1）
python scripts/governance/generators/generate_gate_registry.py --check; echo "exit=$?"

# 5) C05/C07 群体关系三证：own_scope 机生计数 / 交集 1 台 / 两链位
python -c "
import yaml,io
g=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml',encoding='utf-8'))['gates']
ip={x['gate_id'] for x in yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml',encoding='utf-8'))['gates']}
pc={x['gate_id'] for x in g if x.get('enforcement_channel')=='pre-commit'}
print('pre-commit 通道',len(pc),'| own_scope True(commit-gate)',sum(1 for x in g if x.get('own_scope') and x.get('enforcement_channel')=='commit-gate'),'| 交集',sorted(ip&pc))"
grep -n "_check_gates_with_drift_watch(\|_run_precommit_channel(\|_commit_with_file_message(\|\"--no-verify\"" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | head

# 6) C06 八拍锚点（一次拿全）
grep -n "def _stage_gitignored_tracked\|def _write_pathspec_file\|def _add_and_remove_normal_files\|def _should_use_no_pathspec\|def _has_staged_renames\|def _verify_staged_is_clean\|def _commit_with_file_message\|def _commit_locked_finalize\|def _sweep_intent_to_add_residue\|def _sweep_phantom_staged_adds" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py

# 7) 台数目口径（68 hook / 58 gate-* / 名册 55）
python -c "
import yaml,io
d=yaml.safe_load(io.open('.pre-commit-config.yaml',encoding='utf-8'))
h=[hk['id'] for repo in d['repos'] for hk in repo.get('hooks',[])]
print('hooks',len(h),'gate-*',len([i for i in h if str(i).startswith('gate-')]))"
```
