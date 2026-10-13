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



