---
ttl: task_bound
completes_when: 放量 B/C/D 三面每枚降档有 manifest 行与证据 sha 对应＋附属面残面有主＋99_delivery 收班册落 dev
---
# 死信放量战役·账册（sid=st-deadmass-20261013，2026-10-13 22:4x 起）

> 令据＝Owner 2026-10-13 统筹令「死信放量班开场」＋四条并发权限；接手处＝前任
> `docs/_working/deadclean_campaign/99_delivery.md` §四四条交接卡。
> 判据红线＝dead 每降一枚必有 manifest 行＋证据 sha 对应；存疑一律回态④不硬清；
> blob 存证/墓园走 E: 盘与 git 对象面，不碰 CH；禁按条数估。

## 一、进场基线（实测，非引用前任值）

| 面 | 前任值 | 本班进场实测 | 备注 |
|---|---|---|---|
| dead 死信 | 1,550（A 类清后） | **1,569**（item 977／env 262／other 330） | 他班 22:1x→22:4x 仍在死，＋19 |
| 在途 | — | pending=0／processing=1（`st-cdx-formreg-0003`，与本战役零交集）／done=806 | blobs=27,147 |
| 前任会话 | 收班 | 心跳 22:56:27 仍新鲜，`logical=True`＋W-29 豁免＝**revoke 不 kill 守护** | 见 §三-3 |
| E: 墓园 | 8 件 verified | 288 GB 空闲；INDEX 15 行 | 单点风险见 §三-5 |

## 二、交接卡① 前任车道＋会话壳退场（已完）

序＝Owner 令「先停守护让证 1 合法过期→再 abort」＝S2 四证的证 1 走自然判死不用 `--force-skip-checks`。

1. **停守护**：`.runtime/locks/heartbeat_st-deadclean-20261013.pid`=40348 → taskkill（与在册
   `_teardown_session_governance` 同通道）；前像证据 `.runtime/quarantine/st-deadmass-20261013_predecessor_teardown/01_before_stop.json`。
2. **证 1 合法过期**：心跳末条 22:56:27；>90s 后 registry 分片 `st-deadclean-20261013.json` 被收割，
   三件 claim（commit_queue／session_worktree／blob_gc）随条目消失而释放；死判输出
   `PASS——死车道（registry 无活跃记录 + 无新鲜锁/免疫标记）`。
3. **归档通道执行**：`session_worktree.py archive st-deadclean-20261013 --execute`
   → ①patch 存证 `st-deadclean-20261013-retire-20261013T145910Z.patch`（三分类 substantive=13）
   → ④prune 核实注册表消失 → ⑤`branch -d` 壳分支删 → daemon 终止 → registry 注销。
4. **拆壳器首次自清实测（两支都真跑到）**：
   - 保留支：首跑 archive 时壳含 `keepalive.jsonl`＝实质面 → 输出「会话壳保留（有实质面，先 promote 再收班）」，**没删**；
   - 删除支：按墓碑制把该审计 promote 进 `E:/_tomb_quarantine/st-deadclean-20261013/shell_st-deadclean-20261013/`
     （sha256=050fa9cc… ，INDEX 行 15→16，rollback_cmd＋expires_at=2026-11-12 齐）→ 壳转纯机制件
     → `_prune_session_shell` 返 True，目录消失，pid 文件亦无残留。

## 三、⚑ 本班实测发现（无一遮蔽）

1. **前任车道里躺着两份从未落地的配对测试＋一条在册审批载体**（99_delivery §一称"全落"，实测非全落）：
   - `tests/gov/governance/test_commit_queue.py` 车道版比 dev 多 211 行＝段三内容级四态门＋处置台账三栏＋复发熔断
     衰减窗的配对测试（`TestDeadArchiveContentGate`／`TestRecurrenceDecayWindow`）；dev `tests/` 对
     `_content_dead_bag`／`_archive_ledger_evidence`／`disposition.jsonl` **零命中**；
   - `tests/meta/scripts/test_session_worktree_archive.py` 多 72 行＝拆壳器六支配对测试；dev `tests/` 对
     `_prune_session_shell` **零命中**；
   - `architecture_issue_registry.yaml` 多 9 行＝`ARCH-DEADCLEAN-CONSTITUTION-001` 条目，而 dev 历史
     `81d5a0c6f1` 的 commit message **带着 `[ARCH-APPROVAL:ARCH-DEADCLEAN-CONSTITUTION-001]` 标记**——
     注册表查无此条＝悬空审批载体（Layer2 `check_protected_paths` 只认标记不消费裁定通道，在册已知病族）。
   处置＝本班代投：三件已从车道取字节入本车道＋quarantine 双存证，dev 码面上跑配对测试
   **141 passed**（`test_commit_queue.py` 128＋`test_session_worktree_archive.py` 13，仓外 `--basetemp`，`-n 0` 串行）。
   `capability_canonical_file_registry.yaml` 车道版＝dev 少 25 行的**落后快照**（dev 为严格超集），判外来不救。
2. **主区磁盘码落后 HEAD（在册 P0 形态复发）**：`scripts/session_worktree.py` 工作区＝HEAD 少 57 行且
   `_prune_session_shell` 命中 0（HEAD 命中 2）——若不复位，"拆壳器自清实测"会跑成静默 no-op（降级态与
   未触发同形）。`commit_queue.py`／`blob_gc.py` 工作区已等 HEAD 但 **index 存的是落地前旧 blob**。
   逐行谓词已证三面均无 HEAD 外独有内容（session_worktree 独有行=0；另两件"独有行"均为被段三改写掉的旧行文本）。
   处置＝先 snapshot 三件 WT+INDEX 字节入 `quarantine/st-deadmass-20261013_main_stale_code_surface/MANIFEST.json`，
   再以 HEAD 字节 `safe_write_text` 落盘＋`git restore --staged` 精准三路径，读回三面 sha1 **全等 HEAD**
   （没用 `git restore --worktree`／`checkout --`＝RULE-GIT-SAFE 禁用形态）。
3. **逻辑会话的 revoke 不等于停守护**：前任 22:15:54 已落 revoke（"本班收班"），但 W-29 `logical=True`
   豁免在 idle 支之前生效（心跳记 `keepalive=logical_session, idle_seconds=2630`），守护照跑、会话照活。
   结论＝"收班即清"对逻辑长会话必须走 teardown（archive/abort→`_teardown_session_governance` kill daemon），
   revoke 只管 grant 续支。本条属观测，不在本班改判据。
4. **尺的自犯一条**：首版逐件对表用 `git rev-parse dev:<path> | awk '{print $3}'` 取字段——`rev-parse` 只出一个
   sha，dev 列整列空＝假读（同在册"强正则 0/13＝假红尺"族）。改 `$1` 后 13 件里 10 件 SAME_as_dev 才现形。
5. **墓园单点**：`E:/_tomb_quarantine/README.md` 自陈"本区未入备份前，任何只写不删累积都构成新的单点"；
   本班 C 类 1.10 GB 唯一证据面按 Owner 红线走 E:，备份覆盖核实列入 §四。

## 四、待办与状态

| # | 项 | 状态 |
|---|---|---|
| ① | 前任车道＋壳退场（拆壳器自清实测） | **已完成**（§二） |
| R | 代投前任未落地配对测试＋审批载体 | 车道就绪 141 绿，待入袋 |
| ② | C 类主役：唯一 blob 存证（墓园 INDEX＋30 天窗）→ 逐批内容级四态判 → 归档 | 待做 |
| ③ | B 类 91：render 袋 `q-20261013-st-maint5-20261013-0010` 内容级判销账；其余租约空窗正门 requeue | 待做 |
| ④ | D 类 2＋45 记"确认已失"；前任 4 枚 content_held 顺做 mv（各留 manifest 行） | 待做 |
| ⑤ | 附属面：工棚 164／会话壳 497 存量／quarantine 非 drift 65／根散件 23／gate_audit 轮转核验／11 枚悬空管理项 | 待做 |
| ⑥ | E: 墓园备份覆盖核实 | 待做 |

## 五、追加令落地（Owner 2026-10-13 23:0x：段二两腿＋blob_gc phase2 存量）

### 五-1 段二两条腿已落码（袋 q-20261013-st-deadmass-20261013-0002，files=7）

两腿都挂在传送带**既有落地方事件缝**上（`_drain_once` 之后，与 `_projection_drift_probe` 同型：
事件驱动＋900s 冷却＋fail-open），零 cron/Timer/sleep-loop（§9.3）：

| 腿 | 函数 | 判据来源 | 动盘范围 | 停法 |
|---|---|---|---|---|
| ① 当日四态分诊 | `dead_triage_probe` | 复用在册 `make_dead_letter_content_gate`（零新判据） | **只判不删**：判定行 append 进 `.runtime/audit/dead_letter_triage_ledger.jsonl` | dev 头寸变更即弃旧索引 |
| ② 主区暂存区巡检 | `phantom_staging_probe` | 三态机器谓词（有主／TierA 纯索引幽灵／TierB 歧义） | TierA 先按 blob sha 存证再 `git restore --staged`；TierB 只记不修 | `.runtime/registry_ledger/phantom_staging.disabled`（只停"动手"支） |

- 记账走既有 `record_phantom_staging` 通道——该 API 自 W7 建成后**全仓零调用者**（装饰性护栏），本批是它的第一个消费者。
- 活死尺与工具守卫同源 `list_active_readonly()`（在册"尺上的死不算死"教训），不用 mutating 版 `list_active()`。
- ALGO_FLOW 外部真源补 A4/A5 两节点，并按代码事件序重接线 `A2→A4→A5→A3→O1`；
  经 `scripts/governance/_shared/algo_flow_validate_marker.validate_graph` 实跑 problems=NONE（8 节点 7 边）。
- 当班先吃自家账：腿①在真队列实跑 `scanned=1587 triaged=1587`，
  分态 C=1376／B=109／A=57／D_MIXED=43／D_LOST=2，与本班独立尺（60/60 与真门对表）同值。
- 测试：新增 13 支（触发/幂等/只判不删/冷却/索引随头寸重建；TierA 复位留证、TierB 不动、有主跳过、
  停腿、execute=False 纯 noop、堵点本行、无证即不复位）；`test_commit_belt_daemon.py` 全文件 **50 passed**，
  本批三文件合跑 **191 passed**（PYTHONPATH 锚车道码面并打 `__file__` 自证，仓外 `--basetemp`，`-n 0`）。
- ruff：`check` All checks passed；`format` 4 件重排（改动全落本批新增区，逐件 numstat 复核
  删行仅本批计划内改写：header 常量 2／图边段 1／import 行 1）。

### 五-2 代投袋首投死于正判，重基方二次入袋

- 首袋 `q-…-0001` 被 **REGISTRY-YAML-PARSE** 拦死：本批 capability 投影以 23:05 主区渲染字节为基，
  dev 在 23:07 又进一条 `tdm_goal_structure` token ⇒ 直提整档会抹掉他道已落条目。**门拦得对。**
- 教训与处方（照门提示执行，不加豁免旗）：行级"我只少=0"是**假安全**——门读的是解析级结构；
  重基后按 `yaml.safe_load` 的 `creation_tokens` 集合差自证 `only_in_dev=[]`（15,436→15,437）才算数。
- 尾追加姿势的第二个坑：把顶部 `from datetime import ... timezone` 改写行吃掉 ⇒ 实测
  `NameError: timezone` 抓到，非肉眼判；补回后定向 15 支复跑全绿。
- 处方：重基后必须把被改文件的配对测试**真跑一遍**，diff 计数救不了自己。
- 案卷 `.md` 新建件暂不随袋：CREATE-GUARD 读**主区**投影盘面（裁定#480 手术③"主区盘面才是登记即时真源"），
  而主区该册 23:05:20 被他道写入 5 行未缩进的 `no_mount_reason:` ⇒ 解析失败 fail-closed 拦一切新建件。
  这 5 行不在 dev、不在任何在册袋 blob、也不在任何其他车道副本＝外来脏面。按 §3-4"他会话在途不代修"，
  本班不修它，案卷袋改期重投（列入呈批面）。

### 五-3 主区混合暂存面实测分母（巡检器的真实账）

进场实测（主区 `git diff --cached` vs HEAD）：**161 条 staged** 全部 index≠HEAD，按巡检器三态分档＝
**TierA 纯索引幽灵 130 条（其中无主 128 条）**／**TierB 工作区也改＝歧义面 31 条**。
TierA 点名样本：`.gitignore`、`AGENTS.md`、`config/flags.yaml`、`gate_registry.yaml`、
`parallel_session_coordination_policy.md`、`_cross_layer/database/business_data_categories.yaml`、
若干 `TDM-E-L1-*` 考试卡——**全部工作区字节==HEAD**，复位＝零内容损失（只清 index）。
这正是 Owner 说的"双臂班只自清自家那份"的系统性病根。

### 五-4 C 类主役与墓园（终值）

- 唯一面存证 **5,898 枚 / 1.034 GiB**，逐枚回读 sha256 `mismatch=0 missing=0`；
  批次目录 `E:/_tomb_quarantine/st-deadmass-20261013/C_unique_20261013/`，
  `MANIFEST.jsonl` 5,898 行（内容寻址去重；3,358 枚被多袋共享，覆盖 39,616 袋次）。
- 墓园 INDEX 行数：16（前任保活审计 promote 行）→ 17（校准批）→ 18（全量批）。
- 归档腿改造两轮：首版"单大调用＋每轮全量重算"在租约被持时空转（23:15→23:44 未见窗，
  每轮重算 1GB 字节＝小时级）⇒ 改为**判定表一次成表**（消费 60/60 对表过的独立尺＋墓园归宿集，
  O(1) 查表）＋**小片抓窗**（20 sid/片，10 片）。判据表分布：
  C_TOMBSTORED=1376／A_LANDED=56／D_MIXED_TOMBSTORED=43／D_CONFIRMED_LOST=2／B_HOLD_FOR_REQUEUE=106。
- B 面剔除依据：基底==dev 现值的未落地件，requeue 才有归宿；归档只等于把它搬进墓园＝假销口。
- render 袋 `q-20261013-st-maint5-20261013-0010` 判**销账**：整档 blob 尺给 C_UNIQUE_WOULD_REGRESS，
  但行级核账 `lines_only_in_bag=0`、dev 反超 18 行 ⇒ 已被维护六班重渲染取代，requeue 反成回退弹。
  证据 `.runtime/quarantine/st-deadmass-20261013_render_bag_supersession/judgment.json`。
  ⚑ 该案＝"整档 sha 尺"与"行级尺"分歧的实证：**判销以行级为终审**。

## 六、附属面实测与清理（残面清单逐项，全部进程外读回）

| 面 | 前任值 | 本班实测终值 | 动作与判据 |
|---|---|---|---|
| 会话壳 | 497（108 空＋382 纯机制可拆＋7 实质） | **507 → 27**：拆 480／留 15 有实质面／活会话跳 12 | 逐壳调用在册 `_prune_session_shell`（本班不另造谓词）；留存的 15 个点名落 `.runtime/tmp/deadmass_shell_kept.json` |
| 主区暂存区 | 161 条 mixed-pool | **165 → 37**：TierA 纯索引幽灵 128 条全部复位（工作区字节零改动，三面对拍 HEAD==IDX==WT）；TierB 歧义 17 只记不修；有主 6 跳过 | 本班新落码 `phantom_staging_probe` 当班跑自家账；128 枚 index 字节按 sha 存证 `.runtime/quarantine/phantom_staging/20261014/`（MANIFEST 128 行＋blobs 128 枚）；堵点本落 `kind=phantom_staging` 行 |
| `.runtime` 根散件 | 23 枚＋嵌套 3 件 | 可证瞬态件 **6 枚清零**（3 枚 `*.tmp<pid>` ＋嵌套 `.runtime/.runtime` 整壳 3 件），空壳目录已 rmdir，嵌套目录 exists=False | 按墓碑制搬 `E:/_tomb_quarantine/st-deadmass-20261013/runtime_root_junk_20261014/`（逐件 sha256 等值回读，INDEX 第 19 行，expires_at=2026-11-13）；**持久态一律不动**（`session_registry.json` 旧表兼容副本／`task_board.db`／`takeover_ledger.jsonl`／`*_last_attempt`／`*.json` 状态）——判据＝名带进程号后缀或位于嵌套影子壳 |
| 工棚管理项 | 41 管理项 vs 磁盘 30 棵＝11 悬空 | `git worktree list` 52 条目中目录已消失仅 **1** 条（`.aidrafts_pool/pool-20260919202729-c433`，且该条 **locked**） | 不自解他人 locked 池位（§3-4 owner 责任制＋"物理不可逆"边界）；前任的 11 枚悬空多数已被各班 `git worktree prune` 消化，本班只如实报数 |
| gate_audit | 1.79 GiB，"轮转是否在转＝未核" | **在转**（`.runtime/gate_audit` 5 个移位保留段＋`.runtime/audit` 6 个，`rotate_if_oversized` 入口闸随每次 append 检查，DEFAULT_MAX_BYTES=50MB）；但存量最大段 120.3MB／65.3MB **超阈值**＝有写侧未过闸；总 1,214MB/293 件，>3 天未动的 182 件仅 26MB（大头在热文件） | 只报不删（审计面删除属政策变更，非机械判据，列呈批） |
| E: 墓园备份覆盖（⑥） | 未核实 | **已覆盖且实时**：`G:/backup/offrepo/tomb_quarantine/st-deadmass-20261013` 5,899 件 / 1,061.8MB，mtime 2026-10-13T23:18:56（本班批次落盘后约 4 分钟即被镜像，与源侧字节数等值）；`scripts/backup/backup_config.yaml` L129-130 点名 `tomb_quarantine` 为备份目标（终清二期批复 B） | ⚑ 结论＝C 类 1.034 GiB 证据面**不构成单点**，README 的"未入备份前"警告条件已消 |

### 六-1 留存 15 壳的实质面分类（下一步归属）

- 保活审计型 11 个（只剩 `keepalive.jsonl`）＝机制件白名单外、但非成果——可按前任先例 promote 入墓园后拆；
  本班未自动做，因 promote 他班会话的授权审计属跨班次动作，留给 Owner/各属主点头。
  点名：examrun/examunlock/fclean3/gpuwo/gpux4/gpux5/maint5/minedig/statsgov（＋maint3、gpuux3v 兼具成果）。
- 真成果型 4 个：`st-gpuux3v-20261013`（staging/ 三份 v3 章节稿＋handoff）、`st-maint3-20261011`
  （archive/plan_20261011T151409Z 三件）、`st-nightmine2-20261010`（t1_quarantine_hash_index.json）、
  `st-datasop-20260930`/`st-gomap-b-20261006`/`st-mastertc-l5`（`heartbeat.jsonl.takenover-by-*` / `.resolved-by-p12a` 取证改名件）。
  ⚑ 按在册红线"被清除面≠净收官"——这 4 类**不拆不动**，成果 promote 是各属主班或 Owner 的事。

## 七、blob 面与放量窗（跨零点实况）

### 七-1 blob_gc phase1 已跑（Owner 追加令）

`python scripts/governance/blob_gc.py --phase 1 --archive` rc=0：
**已归档 6,129 枚 / 2,193.9 MB**（竞态重扫跳过 0／dst 已存在跳过 0），
`blobs_archive/manifest.jsonl` 逐枚留痕可 `--restore` 逆向；`blobs/` 存量 27,186 → **21,059**。
phase1 干跑基线（00:07）＝A 活引 20／B 仅 dead 8,079／C2 仅 done 1,839／C1 混引 583／
D 仅归档引 5,086（1,201.1MB）／Z 零引 6,156（2,216.8MB）／多类混引 5,423。
⚑ phase2 未跑（按令须"C 类归档推进后"）；在册头册已声明 phase2 复扫的"仍引用"**只数活引用面不计 ARCHIVE**
（否则 D 类被自己的归档 JSON 判成在引＝旗空转）——与 Owner 令括号内要求逐字一致，本班无需改动。

### 七-2 C/D 归档放量＝被传送带租约占死，本班未越闸

判据表已成（O(1) 查表，不再重算 1GB）＋小片化（20 sid/片 ×10 片），
从 23:15 起三轮长跑（40/40/150 次尝试，12-20s 退避）实测：
**pid=36216 的 serializer 租约连续复持 ≥70 分钟**（`state=drain-active`，`acquired_age_s` 在 4→290s 间循环续期），
跨零点时队列 pending=6／processing=1＝多班同时投袋把空窗压到零。
本班按 Owner 红线"租约闸不越"，未用 `--no-verify-landed`、未改门、未停传送带，保持轮询待窗。

⚑ 呈批/待裁一条：放量腿与传送带的互斥是**结构性**的（在册 §2-6 与 dead-archive ①②③④ 闸设计如此），
在队列高饱和时段单靠抓窗做 1,477 袋级清账不可预期。可选正解三选一（本班不自拍）：
①等自然 quiet 时段（凌晨散场后）由本班或下一班跑；
②由 Owner 令"暂停 belt 守护 N 分钟"做一次性大批清账（属共享系统动作）；
③把清袋并入段二腿①的事件面（判定已在自动落账，处置仍留人工＝本班现设计），
   若要把"归档"也自动化＝弱化"存疑回态④不硬清"红线，本班判断**不应做**。

### 七-3 主区投影自愈记录（新建件闸的解锁过程）

23:14 本班首袋被 CREATE-GUARD fail-closed 拦下（主区 capability 投影被他道写入 5 行未缩进
`no_mount_reason:` ⇒ 解析失败拦一切新建件，非本班字节问题）。00:1x 实测主区面 parse=True、
col0 坏行=0（他道后续 render 追齐）；本班随后经在册 `projection_generator.run(mode="render")`
正常口再打一次（ledger_revision=541，added=1=本班 token 行，removed=0），
读回 parse OK。**结论＝在册"投影滞后假拦、render 追齐即通"定案复证一次**，本班未修他道字节。

## 八、二班班账（st-deadmass2-20261014，2026-10-14 02:2x → 03:2x）

令据＝统筹令 2026-10-14 晨（接本班 §七交接卡）；角色与并发四条＝只读类多车道并行／写盘按片分区／
事件驱动不空等／首件小步校准后放量／一口气执行到底中途不问 Owner。

### 八-1 冷启动与保活（复命四步全读回）

RULE-ENV＝python 3.12.8＋`setup_dev_env.py --check` installed=True；RULE-GUARDIAN＝reaper
`source=live`（commit_pct 67.11%、worktree_changes=213 只报不处置）。保活只走 grant 正门：
`register(sid, pid=0)`→心跳守护按在册三元形态起（入口=包模块 `-m zephyr...heartbeat_daemon`，
**非** `scripts/heartbeat_daemon.py`，后者查无＝Popen 假成功旧坑）→`register_heartbeat_keepalive`
→用门自己的尺 `list_active_readonly()` 命中＋心跳龄 ≤90s 收尾核验。实测心跳面 30s 一跳
（`status=alive`，单一 pid=30364，无复数守护），grant 剩余 1,189s 时由保活腿自动续。
⚑ 首版把保活/归档 stdout 直插 `| tail` ⇒ 块缓冲致日志恒空＝"没跑"假象，改用文件重取后
以进程表证实两腿一直在跑（在册"空日志≠没跑"复证，本班自犯登录第八-3 条）。

### 八-2 校准复现（首件小步，未先放量）

`deadmass_c_measure.py --sample 60` 两轮（02:2x/02:5x）：**正对照 MATCH**（AGENTS.md rev-parse
== 尺算 sha）＋**负对照 DIFF**；与在册真门对表 **agree=60 disagree=0**（前任 60/60 复现）。
分母 dead=1,638→1,639；分态 C_UNIQUE_WOULD_REGRESS 1,403/1,404、A_LANDED 75/76、
B_UNIQUE_REQUEUEABLE 115/114、D_MIXED 43、D_LOST 2。
**独立尺对拍**：段二腿①自动分诊账 10-14 面 C 1,400/A 75/B 118/D 43+2＝1,638，与本班上表
同总数、C↔B 差 3 枚（其间他班落地所致）⇒ 两把尺互证，非自证。

### 八-3 墓园接力（存证先行，判据零放宽）

前任池自证：MANIFEST 5,898 行 == dst 在盘 5,898（manifest-only=0／disk-only=0）。
本班新面缺口 85 枚／37.10 MiB → 独立池 `E:/_tomb_quarantine/st-deadmass2-20261014/C_unique_20261014/`
（署名/回滚/到期各行自成一册，不与前任混账）。逐枚回读 **mismatch=0 missing=0**；
现表唯一面 5,980/5,980 归宿＝**覆盖率 100.0000%**，源 blob 缺失 0 枚。

### 八-4 租约空窗实测（本班主役的真瓶颈）

0.2s×898 样本连续采样 180s：**FREE 跨段=0**；`_lease_snapshot` 全程 `present&alive`
（holder_pid=3452 为常驻守护级进程）。读码定性＝这不是尺的bug而是闸的本义：
①`commit_queue.py:1394-1420` 活体持有者超 TTL 判"慢项在途，**绝不可抢**"（2026-09-17
11 条 pathspec 死信病根治本，抢=两 drain 并发同 serializer worktree，硬复位加深扫清理毁未 commit 新文件
毁未 commit 新文件）；②`dead_archive_letters:3855` 官方通道**自身**即以"serializer 租约存活"
整体拒绝并行维护操作。⇒ pending 非空期"抓窗"结构上不可达；本班按令挂轮询不越闸不停带，
并把该片实测作为呈批依据（前任 §四-1 "若仍无空窗"分支）。带量吞吐实测：done 838→845、
pending 27→25，约 8–9 min/枚 ⇒ 25 枚积压需 ~3.5h 才可能出真空窗。

### 八-5 B 面改判（按属主活性分道，统筹令第 4 条落地）

115 枚 B_UNIQUE_REQUEUEABLE 分账：**活属主 18 枚**（5 sid：bakdr/condaxis/gpux6/libstale/maint7）
⇒ 留位不代投（代投字节会因本道后落地变回退弹，在册 parked-bag 条）；
**死属主 97 枚**（35 sid）⇒ 走内容级通道。判据不是偏好而是机械的：属主已死之袋 requeue 必再死于
`ghost_session`（`commit_queue.py:2129/2396`），而唯一面已逐枚入墓园 ⇒ mv＋manifest 行＋证据 sha
零丢失且留 30 天复活窗。render 袋 0010 按前任"被重渲染取代＝销账"随 C 面走，本班未 requeue。
归档器因此重投一次（旧进程按 PID 39100 精确停，无按镜像名杀）：新分布
C_TOMBSTORED 1,404／B_DEAD_OWNER_TOMBSTORED 97／A_LANDED 76／D_MIXED 43／D_CONFIRMED_LOST 2
＝放行 1,622，B_LIVE_OWNER_LEAVE 17 不放行。

### 八-6 blob_gc phase2 首轮（随清袋走，仍只归档不删）

`scripts/governance/blob_gc.py --phase 2 --archive`：**moved 4,710 枚／984.3 MiB，
竞态复扫 skip=0，dst 既存=0**；blobs/ 21,209→16,501，blobs_archive/ 10,883。
承重墙复证＝竞态复扫的"仍引用"只数活引用面（不计 ARCHIVE），否则 D 类被自己的归档 JSON
判成在引而旗空转——本轮 skip=0 即该墙的正面读数。第二pass 挂本班 C/D 归档之后。

### 八-7 前班车道退场（统筹令第 2 条，接线核查＝已落）

钩子在 `scripts/ops_guard.py:1288-1316`；**调用侧**实测落 dev：
`scripts/session_worktree.py:1080 _tomb_ctx_factory` 被 `:1197` 消费（`man.verified` 为假时
factory=None＝fail-closed 不放宽），`:1139 _patch_new_file_bytes` 从退役 patch 真读回正文字节。
退场前先落前任未落地交接面：车道 99_delivery 127 行 vs dev 77 行，且 **dev 字节是车道字节的
严格前缀**（`new[:len(old)]==old` 实测 True）⇒ 纯追加 4,418 字节搬入，走正门
`--enqueue`（袋 q-20261014-st-deadmass2-20261014-0001；网关 lease 被持自动改道入队，非直连强抢）。
退场四处读回＝worktree 目录消失／`git worktree list` 无该条／分支 `ai/st-deadmass-20261013/*` 已删／
session 已注销；退役 patch substantive=11（1,436 行 `+`）；**执行窗内接管台账新增 0 行**
（192→192，按 ts_epoch 过滤非按字符串猜），动手前同分钟实测 10 个在册活会话心跳龄 ≤22s ⇒ 无外班分片可收。

### 八-8 会话壳与根散件

壳面 33 → **17**。13 壳只剩 keepalive.jsonl ⇒ promote 入墓园后走在册 `_prune_session_shell`
拆壳（拆 13 保留 0）；3 枚取证改名件（datasop/gomap-b/mastertc-l5）按"已存证即放行"mv＋拆
（dst 逐枚 sha 等值才 unlink，一物一行不重记）。3 壳真成果（gpuux3v 17 面／maint3 17 面／
nightmine2 1 面）实质面 38 枚／927,352 字节全部 tomb 复制留证，**壳暂不拆**——理由见八-10。
墓园总账：MANIFEST 136 行（85 blob＋38 实质＋13 keepalive）逐枚回读 **mismatch=0 missing=0**，
INDEX 21→40 行，本班 20 行 expires=2026-11-13。备份覆盖面核实＝
`scripts/backup/backup_config.yaml:129-130` tomb_quarantine 源＝`E:\_tomb_quarantine` 整根，
本班新子池自动入 G 盘夜镜像。
根层平铺未跟踪件=**0**（正对照＝同一尺在全仓面报 168 条 `??`／未跟踪总数 550，非零命中尺）。

### 八-9 gate_audit 一条前提被实测改判

存量 292 件／1,209.5 MB；最大两段 `test_source_consistency_foreign_staged.jsonl.1` 120.3MB／
`no_upward_import_foreign_staged.jsonl.1` 65.3MB **同前任读数一致**，但两族的 **live 段实测仅
2.2MB／1.2MB** ⇒ 这两段是**已移位保留段**（轮转在转），不是"此刻还在涨的不过闸热文件"。
本班未修他道字节，只把该读数呈维护线（维护七班班账 dev 面 `gate_audit` 零命中＝尚未定性）。
删除属政策变更，本班不删、不自造豁免。

### 八-10 本班自犯与未做（无一遮蔽）

1. **Edit 追加把他班 keep 行写坏**：给 `process_reaper_keep.txt` 追加本班两行时，锚文本里
   `ZephyrAlpha-CHVMConfigSnapshot` 被我误打成 `ZephyrCHVMConfigSnapshot`（备份线夜班那一行被
   静默改写）。下一步即 grep 自纠复原＋行数对拍（385→387 恰为本班两行）。教训＝追加型热件的
   锚段必须逐字复制，改后要用**行数差＝计划差**自证，不能只看"我的两行进去了"。
2. **保活/归档日志管道坑**（八-1 已记）：`python -u … | tail -N` 在长跑下等于把输出锁在缓冲区，
   据此判"没跑"会误杀自己的腿。
3. **`clone_guard_audit.py` 无 argparse**：本想读它的用法，`--help` 被当位置参数直跑了一轮
   L2 全量 .py 审计（findings=0 健康 A，产物 `.runtime/clone_guard_audit/audit_20261014T031448.json`）。
   副作用登记在此；该尺只覆 .py，对本班 .md promote 无判别力。
4. **宪法宣称的写前预查 API 不存在**（`clone_guard.check_before_write`/`resolve_finding` 全仓零命中，
   在册案卷 `fullflow_mining/m3_governance/06_f103_clone_guard_code_dedup.md` 已记为须治理裁定）
   ⇒ 本班**无法**在写前判克隆，只能在 commit 面吃事后 `check(staged)`。
5. **仓库侧 promote 本班未做（有意搁置，非漏做）**：复测证伪了交接卡的两处计数——
   gpuux3v 实质面是 **17 枚非 3 枚**、maint3 是 **两个 plan 批（151409Z＋162521Z）共 17 枚非一个**；
   且 `v5_section_13_O.md` 签名行实测**已存在**于 dev 的 `gpufeed_campaign/03_gpux_final_report.md`
   ⇒ 前置（CLONEGUARD acknowledged 对／散文去重）未清，在 25 枚积压、8–9 min/枚的拥堵队列里
   盲投一个可能死信的袋＝给下一班新增死信，与本班"每降一枚有 manifest 行"的判据反向。
   四道前置按实测排（详见收班册 §五-2）：**TTL-METADATA**＝16 枚 .md **全无 frontmatter 围栏**
   （仅 `handoff_*.md` 首行有 ttl 行但缺 `---` 包裹）；**CLONEGUARD**＝上述 v5 重叠；
   **DOC-REF-BROKEN**＝相对链接在目标位实存本班未逐一验；**SSOT 方向**＝maint3 的 `orig/` 面
   是已跟踪件前像（85KB/51KB 级）属第二真源，不进仓库（已走墓园，行内含 rollback_cmd）。
   ⇒ 该活须开自己车道迭代这道门，不在主区队列试错。
   ⚑ 反向一条实测收获：`create_guard._pg_confirmed_token_files` 对本班三件（新册＋两既存册）
   全数正证在册 ⇒ **"内容袋不随投影册"这条路实跑通**，非引用他班结论。
   处方已命令化进二班收班册 §五-2，3 壳因此保留未拆（内容另有墓园双证）。

### 八-11 死因普查（放量等窗期的预防面，只读零处置）

全 1,643 枚在册死信按 `dead_reason` **本体**正则取门名（尺的更正：measure 表的
`dead_reason_head` 截 80 字符会把门名切掉，145 枚因此落到 "other" 桶 ⇒ 普查必须读袋本体），
147 个死因类，头部如下（表存 `.runtime/tmp/deadmass2_death_cause_census.json`）：

| 死因 | 枚数 | 占比 |
|---|---:|---:|
| landing 异常（RuntimeError 级） | 369 | 22.5% |
| ghost_session（属主会话已死） | 259 | 15.8% |
| GATE-PRECOMMIT-RUN | 119 | 7.2% |
| DOC-HEADER-SUITE | 117 | 7.1% |
| CREATE-GUARD | 102 | 6.2% |
| TAKEOVER-PENDING | 45 | 2.7% |
| TRANSLATION-COVERAGE | 40 | 2.4% |
| TEST-SOURCE-CONSISTENCY | 31 | 1.9% |
| cascade_stale（基底重校验不适用，src/ 与 docs/ 两簇） | 50 | 3.0% |
| ALGO-FLOW-LINK 27／GATE-VOCAB 26／R5-DIGIT-SUFFIX 22／CLAIM_REQUIRED 21 | 96 | 5.8% |

两条可读结论（只出案卷不出裁定，处置属维护线/Owner 面）：
①**ghost_session 259 枚＝15.8%**——2026-10-11 保活正门（grant）治的是"idle 自退使袋判幽灵"，
本面是**存量**而非新伤；本班实测保活三件套（grant＋守护 30s 一跳＋`list_active_readonly` 命中）
可复现，说明增量通道有效，存量只能靠本班这类放量清。
②**GATE-PRECOMMIT-RUN 119 枚**与在册族谱档案"修此门可消 222 袋"同量级——该门仍是净增死信的头号
门禁型来源，优先级排在 DOC-HEADER/CREATE-GUARD 之前（后两者多为新建件登记时序问题，
本班 §八-4 与前任 §六 各复证一次"投影滞后假拦"形态）。
本班**未**据此改任何门判据（红线：判据改动只认任务书与总筹通道）。

### 八-12 统筹增补令（P2 加半件·claim 观察面）落地与一条前提回交

令原文＝"接维护七班·车道B 定性——claim 观察不可复核（34 条活 claim 无 expires_at、惰性清理）
＝你班 P2 加半件：给 claim 落 expires_at 字段＋巡检打印剩余寿命（只加观察面，不动锁语义）"。

**先核出处**：维护七班车道B 收口册（`maint7_campaign/lanes/lane_b_closeout.md`，145 行）内
`expires_at` 零命中；该定性实在其主账 `maint7_campaign/00_ledger.md:155-163`，原文口径是
"**claim TTL 三处口径分叉**……⇒ 定性＝打印口径与实际过期点不同源，属可观测性缺口
（打印面未反映 expires_at 被改写）"，且他们自记"本班只报不改（改打印面属会话/锁族判据面，
需与 `--failed-claim-ttl` /env 口径同批定）"。⇒ 本袋即那次"同批定"后的落地件。

**前提实测（交回判据，非代签）**：`.ailocks/registry.json` 22 条 locks 与 `.ailocks/*owner.json`
22 条**全部带 `expires_at`（缺=0）**，写侧 `_write_owner` 自 v2.1.0 就在落该字段；
现面＝活 21／已过期仍挂册 1／带 `renewed_at` 8／带 `retention` 0。
⇒ "34 条活 claim 无 expires_at"在本刻不成立。真正无该字段的面是 `SessionRegistry.held_files`
（现 7 条纯路径列表），**在那里补一份到期字段＝给同一事实造第二真源**（违 RULE-SSOT 与 §4 净零），
故本班不落，改为让巡检把 `.ailocks` 这本正源的过期点显示出来——可复核性由本袋取得。

**落地面（只观察，语义零改）**：`lock_files.py` 新增单一渲染函数 `_remaining_life_face`
（def 数 69→70），`status／check／guard-write／list` 四面共用（调用点=4）；
`status` 头行加三态计数"活 a／已过期仍挂册 b／旧格式无 expires_at c"，
空册分支 "CLEAN — 当前无任何文件锁" 逐字未动（`config/construction_workflow_map.yaml:979` 等
拿它当读数，改它会破他人读数）。判定分支 `_is_stale`/cleanup/acquire 零改动。

**绿先证能红（同形双面，一把探针 `.runtime/tmp/deadmass2_redproof_claim_print.py`）**：
改前（HEAD 字节）status=False／list=True／check=False／guard-write=False
⇒ "四面同源"断言改前必红，非恒绿；改后（工作区字节）四面全 True。
病态被复现成一句话：**改前跑 status 的人看不到任何过期信息，跑 list 的人才看得到——同一把锁两个答案**。

**配对测试**：追加在既有族册 `tests/gov/git/test_lock_files_ttl_mutex.py` §10（六支，不新建测试件）；
反向自证一条＝失败收窄 300s 那支除断言报 5m 级外，还断言"不得报 ~30m"（防打印面退回 acquire 口径而测试隐形）。
实测 39 passed（本文件 34＋同族 first_acquire_guide 5）＋`ruff check` 干净；
格式化由 `ruff format` 正门做（首投被 ruff-format 门拦下未成袋，零副作用；改后 diff 仍 171+/8-，
证明未波及他人行）。落地袋＝q-20261014-st-deadmass2-20261014-0005。

⚑ 破例自记：0004 袋讯息里我写过"本袋之后本班不再改这两件"，本节的 P2 账是**该承诺之后**因
统筹增补令到达而追加的一次，非分投习惯复发；此后本班不再改这两件。

### 八-13 主役真实战果（04:0x–10:5x 跨段实测；本班两次汇报之间隔了约 6.7 小时）

先自陈时间形态：本班前一轮汇报写在 03:5x，之后归档器与队列各自跑了数小时。**下面每个数都是 10:4x
重取的现值**，不沿用 03:5x 的读数（在册"运行态断言须同分钟复测"）。

**战果**：dead **1,638 → 1,236**（净降 402）；`dead_archive_20261014/manifest.jsonl` **449 行**
＝两批之和（05:0x 批 424 枚＋10:4x 批 25 枚）。逐行核账全过：

- qid 去重后仍 449（**零重复行**）；台账点名的 449 枚**全部已不在 `dead/`**，且 449/449 在归档目录内实存；
- `verify` 字段 **449/449 = "on"**（本班全程在三闸全开下跑，未放宽任何一道）；
- 每行 `bag_json_sha256`＋`blob_set_sha256`＋`content_evidence` 三段齐（缺行 **0**）；
- 内容级证据：`n_no_home>0` 的行 **0**、`n_evidence_tampered>0` 的行 **0**、累计存证枚次 **1,806**
  （尺＝`.runtime/tmp/deadmass2_audit_manifest.py`，本册 §六-补-8 同一条）；
-  ⇒ 统筹红线"dead 每降一枚必有 manifest 行与证据 sha 对应"在**这 449 枚上逐行成立**。

**⚑ 尺的自纠（差点误报红线）**：我第一版核账按顶层键 `evidence`／`session_id` 查，报出
"387 行无证据 sha"＝**假事故**；真键形是 `content_evidence`（嵌套）＋`bag_json_sha256`＋`blob_set_sha256`。
改对键形后同一尺报缺行 0。复犯在册"错列/零命中尺"形态，当轮自纠并留此条——
教训＝**判"缺字段"前先用一行真实样本打清键形**，否则自己的错尺会差点让 Owner 以为红线破了。

**真瓶颈定位（这是本班对主役最重要的结论）**：10:4x 那一轮**空窗抓到了**（`pending=0`、`lease=FREE`），
内容级门也全放行（命中 C_TOMBSTORED 1,036／B_DEAD_OWNER 100／A_LANDED 51／D_MIXED 41），
但 `kept` 里 **`unlanded` 1,205**、该轮只动盘 **25 枚**。⇒ 挡量的不是租约、不是内容级门，而是通道自己的
**第三闸（逐路径 dev 落地校验）**：C 类按定义是"内容唯一**且未落**"，路径闸与内容级归档在语义上互斥。
双证齐（在册"结论只出自落地实测或自然实验"）：干跑侧 verify=off ⇒ 会动盘 **1,215**；
落地侧 verify=on ⇒ 实动 **25**、留 **1,205**。两条同向，差值即该闸的拦截面。
⚑ 该口径开关（`--no-verify-landed`，在册要求留 `verify=off` 痕）属判据口径面，**本班未自拍**，
也未用 `--force`；呈批见收班册 §五-8。

**blob_gc 三轮（随归档推进，仍只归档不删）**：pass1 moved **4,710**／984.3 MiB；
pass2 moved **940**／151.5 MiB；pass3 moved **1**／3.6 MiB。竞态复扫 skip **三轮全 0**。
blobs/ 21,209→**15,618**。pass3 几乎空手＝**剩余 1,236 枚仍引用着那些 blob** ⇒
blob 释放面与上面那道口径闸直接联动，呈批不批则 blob 面也清不动。

**⚑ 本班第二次破例与自犯（不抹旧账）**：
①上节"此后本班不再改这两件"我**又破了一次**——原因是主役出了真实战果，不落账即成"被清除面≠净收官"。
本节即最后一次，此后确不再改。
②**同件连投四袋的实际代价已量化**：0002 先落地使 dev 基底前进，本班 0003/0004/0006 三袋遂同死于
`cascade_stale: 基底重校验不适用（stale_by=q-…-0002）`＝**本班自己制造了 3 枚新死信**，
与本班"每降一枚"的判据反向。这正是本班在 §八-10 批评过的袋 churn，只是这次落在自己身上。
修因＝**单袋重投＋基底取当下 dev**（0007 已落地：台账 §八 十二节与收班册"六-补"均读到 dev 面）。
③取回死袋时撞**复发熔断**（同签名死信窗内 147 次＋距上次同签名死亡 ≤ 7 天衰减窗）——
熔断语义＝拦盲重投不拦新袋，故走新袋，**未用 `--force` 越过**。
④全仓读数附带一条给维护线：在册 1,261 枚死信里 `cascade_stale` 族 **102 枚（8.1%）**，
属主 top 簇＝st-f15-frombag-20261005(36)／st-sP-bottleneck-20261005(18)／st-closeout-basereq-20261006(12)，
即该形态是**跨班系统性**的，非本班独有（本班贡献 3 枚，已自记于②）。

**保活与收尾**：480 分钟保活腿于 10:34:52 **到界自退**（`ticks=479`，非崩溃）；grant 仅剩 1,452s 且无人续时
我复起 300 分钟腿并按复命四步读回（在册命中＋心跳 ≤30s＋grant 在岗＋held_files 实数）。
本班结束时归档器／量尺／存证器**进程清零**（不留无人监督的动盘手），
`st-deadmass2-20261014` 的车道壳与保活面按收班序列处置。

### 八-14 收班终账（11:1x 实测；含一条未解释的测量伪影与一项有意未完的退场）

**主役终数**：dead **1,638 → 1,242**（本班净清 **452 枚**＝05:0x 批 424＋10:4x 批 25＋11:1x 批 3）；
`dead_archive_20261014/manifest.jsonl` 452 行。逐行核账尺（`deadmass2_audit_manifest.py`）末次读数：
行=452、qid 去重=452（零重复）、`verify` **on 452/452**、缺双 sha 或 `content_evidence` 的行 **0**、
台账点名件仍在 `dead/` 的 **0**、归档目录实存 **452/452**、`n_no_home>0` 与 `n_evidence_tampered>0` 均 **0**。
⇒ 统筹红线在本班 452 枚上逐行成立。
分 verdict 的存证枚次分解＝C_TOMBSTORED 1,753／B_DEAD_OWNER 24／D_MIXED 2／A_LANDED 0（合计 1,779）。

**⚑ 未解释的测量伪影（登记待查，不硬圆）**：同一条 `存证枚次合计` 在本班三次读数间为
**1,751（424 行）→ 1,806（449 行）→ 1,779（452 行）**——行数只增不减而合计先升后降。
台账是 append-only（`open('a')`）且 qid 零重复，按该语义此数列**应当单调不降**，故这不是"数据变了"
而是"有一把尺或一次读法不同源"。本班已排查两向：脚本两次运行同一份文件、同一求和式；
分 verdict 求和与逐行求和一致（1,779 可复算）。**未定位到差异来源**，末次以 1,779 为准并留此条；
⚑ 收班册 §六-补-8 的期望值随之更正（原写 1806）。此列非红线判据（红线＝每行双 sha＋content_evidence 齐，
该项 452/452 稳定成立），故不阻塞交付，但**下一班若要复用该数请先复算**。

**本班自己的 3 枚死袋已自清**：0003/0004/0006 于 11:1x 批归档（2 枚 C_TOMBSTORED＋1 枚 A_LANDED）。
此前它们留在 `dead/` 的原因经查是**保守设计正确生效**——归档范围剔除"属主在册活"的 sid，
而本班会话当时活着；本班注销会话后才进入范围。本班袋终态＝pending 0／dead 0。

**⚑ 一项有意未完的退场（不硬闯，交回判据）**：本班车道 `D:/ZephyrAlpha/.aidrafts/st-deadmass2-20261014`
（分支 `session/st-deadmass2-20261014`，ahead=0、脏 0，零未落地字节，dry-run 判型 **zero_loss**）
**本班未执行退场**，原因＝`session_worktree.py archive` 内部的死判调 `list_active()`（**变异式**：
判死即写接管台账并收割心跳超宽限 900s 的分片）。动手前同分钟实测
`st-infoaxis-20261013` 心跳末行 `status=exited`、龄 **22,449s** 却**仍在 `list_active_readonly()` 内**
⇒ 我一跑该命令，极可能顺手收走**他班**的注册分片（其壳内另有实质件 `heartbeat.json`）。
按红线"他班条目不代解／不硬闯保护区"，本班停手并把命令留此：
`python scripts/session_worktree.py archive "D:/ZephyrAlpha/.aidrafts/st-deadmass2-20261014" --execute`
（执行前请同样同分钟复测全部活会话心跳龄；`st-infoaxis-20261013` 的 exited-仍在册 形态本身
属维护线活性族新读数，建议一并记账）。
本班其余面已清：会话壳 promote 入墓园后按在册谓词拆（两次，因保活腿在被停前又续过一次 grant）、
归档器/量尺/存证器进程清零、reaper keep 行按"收班即撤"删除（删后行数 383，邻行完好；
其间 387→385 的 2 行差是他班自撤其 keep 行，非本班所为，行数对得平）。

**墓园终账**：`E:/_tomb_quarantine/INDEX.jsonl` 总行 44（本班 24 行），本班 files 合计 383 枚、
MANIFEST 行合计 203（85＋13 唯一 blob 面＋38 壳实质面＋13＋1＋1 保活/取证面）；
逐枚回读 mismatch=0。备份覆盖面 `backup_config.yaml:129-130` 指 `E:\_tomb_quarantine` 整根，
本班新子池自动入 G 盘夜镜像。





