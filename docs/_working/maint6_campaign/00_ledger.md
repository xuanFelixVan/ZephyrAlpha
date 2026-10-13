---
ttl: task_bound
owner: st-maint6-20261013
campaign: 维护六班（Owner 令三 v2·维护线施工总包：P0-1 render 追齐／甲-0 own-scope／M-3 补签号／base_head 字面量／两条 HEAD 级挂死地雷／M-4 采样键复核／第 8 条保护区死锁并案＋四车道退场／补充令第 13 条备份 9 红＋第 14 条两小件／P2 四件）
---

# 维护六班施工账 · st-maint6-20261013（2026-10-13 21:1x 接令 → 当班自收，本机时间为准）

> 接令＝Owner 令三 v2（维护线施工总包）＋统筹补充令（22:1x：原第 7 条销、新增第 13 条备份 9 红、
> 新增第 14 条两小件、并提醒 P0-1 仍是三线索共同堵点）。前任账＝maint4（其班账由本班 §五 代投
> 入库 ac3bc04a98）与 maint5（移交三件见 §九）。本班一条总账：**P0-1/P0-2/13/14/P2-1 全落地或
> 全入册，两处判据面按实测改判了令面表述（§三、§八），三件留呈批（§十）**。

## 〇、冷启动与两处自纠（先认自己的）

1. RULE-ENV：python 3.12.8；RULE-GUARDIAN：reaper 计划任务存活、`--status` 可读；
   RULE-WORKTREE：`session_worktree.py create st-maint6-20261013` → `.aidrafts/st-maint6-20261013`
   （分支 `session/st-maint6-20261013`，基 215e2da12b），心跳守护在跑，全程未降级直改主区。
2. **自纠一（漏步）**：冷启动第 4 步 CAPABILITY-LOOKUP 我首袋没跑，被 `CAPABILITY-LOOKUP-REQUIRED`
   当场拦下——门是对的。补做后留审计，并对反查尺先做**正对照**（`commit_queue`=1 命中、
   `gate`=184 命中）才敢信它的 0 命中读数。
3. **自纠二（本班最贵的一条，机制级）**：本文件**第一版只写在车道、既没 `git add` 也没入袋**，
   后被一次整树操作静默抹掉；我按在册取回通道逐面查过——车道 index 零条目、
   `pending/processing/dead/done` 四态袋 manifest 零命中该路径、队列 blobs 只有引用它的
   capability 投影、`.runtime/quarantine/` 无该件——**git 侧与队列侧零痕迹＝第六态（未跟踪工作件）
   全灭**。现重写并即刻 add。教训入记忆档：**"每轮修改即 git add"对我自己的班账同样成立**，
   班账必须与代码件同等待遇。
4. 提交面纪律：本班全部件走队列正门（17 袋），零裸 `git commit`、零 `--skip-preflight`、
   零 `--force` 越闸；两次"能落地但会多烧一枚死信"的自撤（§二）与一次"熔断拦 requeue 不拦新袋"
   的改道（§五）都按不越闸处理。

## 一、P0-1 render 投影追齐（三线索共同堵点，已验收）

- `module_translation_registry`（REG-MODULE-TRANSLATION-001）：动手前实测分母锁
  `family_key='entries'`——PG active **8,118**／dev 投影 **8,105**／lag **13**／反向 0；
  先按意图 API 对 6 条形如测试夹具的行（`src/zephyr/{degraded,layered,lying,new_mod,orphan,with_extras}.py`，
  盘面与 `git ls-files` 双双查无而账本 status=active）**retire 再 render**，次序不可反
  （先 render＝把测试垃圾首次推进 HEAD＝造事故）。追齐后 lag **13→0**，dev 面
  `agg8_series_materialize` grep 命中。
- `ruling_registry`（REG-RULING-001）：号 514 在 PG active 而 dev YAML 零命中＝投影落后账本；
  render 后 dev 面 grep 命中。本班另按统筹 P1 追加令补签号 515（§三），两号同批物化。
- 落地只认 `git log -- <册>` 与盘侧 grep 双证（PG 单源册的袋判 `noop` 而盘上零变化是在册坑）。
- 袋：0002（translation 册）→ 7e25b44708eb；0008（ruling 册）→ 2367ce12d985。

## 二、P0-2 甲-0：GATE-INTEGRITY own-scope 收窄（已落地）

- 改命中面口径与 gate 及设计文档同袋（纪律第 2 条）：`scripts/governance/meta/validate_rules_integrity.py`
  head 模式加 own-diff 收窄（`_own_scope_narrowing(in_commit)`），外来 MISSING→`FOREIGN_MISSING`、
  外来 TAMPERED→`FOREIGN_WIP`（critical=False 不计数）＋`_audit_foreign_staged` 留痕；
  头册 `[INVARIANTS]/[MODIFY-GUARD]/[DEPENDENCIES]` 三行同步填实。
- `gate_registry.yaml` 只改一行：GATE-INTEGRITY `own_scope: false→true`；改前用派生器自证
  `_derive_own_scope_for_entry(...) → True`（机生值==手改值）。该册另有 191→189 的存量 drift
  **故意不随袋**（他案 drift 不代修）。
- 验收＝治理面袋实测解堵：真门 A/B 跑在临时 `GIT_INDEX_FILE`（主区 index 141 条目零污染）。
- 袋：0003 → bd9a708a92b8；配套测试同袋。
- **自纠三（账面纠正）**：我一度把"同会话两袋撞同件"当成"会多死一袋"，据此自撤了 0004 与 0007。
  实际机制＝同字节后袋按内容寻址判 `noop`。两次自撤本身没错（省了排空窗），但**理由是错的**，
  留此防下一班照我的错理由做判断。

## 三、M-3 裁定补签号（已落地，含一处对令面的实测更正）

- 令面写"署名 chief-coordinator-st-20261013 走正门取号"。本班先跑 `approval_resolver` 三口径实测，
  发现车道件被 PROTECTED-PATHS 硬拦的真因不是"没签号"而是 **`.worktrees/<sid>/` 前缀没剥**
  （`resolve_approval` 拿带前缀的路径去查册⇒有授权也判"查无"）。
- 正解＝修**喂给闸的输入**（`_strip_worktree_prefix` 改循环剥 4 种形态：单数/复数/`.aidrafts/`/
  serializer 两形态，上界＝标记种数＋2 防死循环），**不弱化判据、不加白名单、不开豁免**；
  配套钉 `test_dot_worktrees_form_does_not_widen_authorization`（AGENTS.md 仍须被拦）＋嵌套树剥前缀。
- 袋：0001 → 153796c9d83d（gate＋自家测试同批，`--allow-multi-domain` 留痕＝宪法 §2.4 合法面）。
- 取号：按 号514 的先例走意图 API 占号 515 并随 §一 的 ruling 册袋物化。

## 四、base_head 字面量入队侧修正（已落地）

- 病形：袋 manifest 的 `base_head` 可写成分支名，落地侧当字面量用⇒基底不可知时误判漂移。
- 二选一里取**乙（消费侧收口）**并附代价面：新增 `_RE_FULL_SHA`＋`_trusted_base_head()` 三态
  （sha／absent／live-ref）；`_conflict_reason` 遇 live-ref 降级为 warn 并回退既有
  `_legacy_base_drift_reason`；`_merge_registry_file` 退回**逐件 base_blob**，取不到则
  fail-closed 判"基底不可知"。**写侧不动**（写侧属在飞的提交流程属主）。
- 袋：0005 → 78d89452294f；`tests/gov/governance/test_commit_queue_base_head.py` 三钉同袋
  （车道内 33 passed）。

## 五、第 8 条替换文本并案：保护区死锁正解＋四车道退场

- ① 代投 `docs/_working/maint4_campaign/00_ledger.md` 入库：墓园字节逐字 cp（25,323 B，
  sha `e7999b2080a28ff4…`，取回面 `E:/_tomb_quarantine/st-deadclean-20261013/st-maint4-20261013/`），
  落地 = ac3bc04a984e。先例＝维护五班自落班账＋07:07 代投维护三班。
- ② OPS-GUARD↔未入库案卷两法互卡的正解＝给 archive 通道加**"墓园存证已核验"查证支路**：
  消费侧 `scripts/ops_guard.py` 新增 contextvars 通道 `_TOMB_VERIFY_CTX`（与既有 `_RECONCILER_CTX`
  /`_BULK_APPROVED` 同构，**非 env、非全局开关**）＋`load_tomb_manifest`（只收
  `verified is True ∧ sha256==readback ∧ 64 位十六制` 的行，其余一律丢；表无合格行即抛）
  ＋三接入点（`_enforce_docs_untracked`／`_judge_protected`／`_inprocess_judge`）；
  生产侧 `scripts/session_worktree.py` archive 写可回读存证表（原始活体 sha 双写＋`patch_sha256`
  ＋`eol_normalized_readback`，核验口径＝袋字节==EOL 归一活体）并在 rescue 外包上下文。
  判据式零改动＝扩既有通道不立新门（净零）。测试 `TestTombVerification` 8 钉，
  类级 `@usefixtures("_restore_primitives")`（否则 audit-only 模式下硬拦断言会假绿）。
  - 双面自证：`maint6_tomb_twoside.py <unfixed|fixed>` **分进程**跑（同进程内 guard 打补丁是
    进程全局⇒两面共用第一个 wrapper＝假 A/B，我在这一点上先自证伪过一次）⇒ 未修面 BLOCKED、
    修好面放行。
  - 死因两则与处置：袋 0010 死于 `RELATIVE-PATH-LITERAL`（`.lstrip("./")` 里的裸字面量）
    ⇒ 改拆串常量 `_CUR_DOT_SLASH` 后**另投新袋**（内容修好的袋 requeue 会 `SNAPSHOT-DRIFT`）；
    袋 0011 死于 `TAKEOVER-PENDING`（st-deadclean 死会话 open 条目命中 `scripts/session_worktree.py`）
    ⇒ 该接管条目已在 §九 内容级处置完并 `--resolve`；复发熔断拦的是 requeue 不拦新袋，
    本班不用 `--force`，改道正门新袋 0014。
  - **取回手法（机制级，值得在册）**：车道那三件的编辑连同本班班账一起被整树操作抹掉后，
    唯一活面＝死信袋 manifest 的 `blob_sha256`。取回＝`cp` 自 blobs（禁 `git checkout`——会污染
    共享 index），三件 sha 自检全中；且实测 **dev 对这三件 == 袋 base_head 3adc34d1ca 字节**
    ⇒ 我的袋字节＝base＋我的改动，零他人面回退风险（动手前量的这条是关键，否则就是静默蒸发）。
- ③ 四棵卡死车道退场复验：maint4／maint5／examunlock 三棵按处方停心跳守护让证 1 合法过期后
  archive/abort 收口；deadclean 当时判活（"活车道禁止归档"无逃生 flag）⇒ 本班**不越闸**，
  只登记；至 §九 时该会话已被台账判死（idle 7230.6s>7200s），本班按其处方复验三项资源面
  （claims／worktree／heartbeat）实测均已归零后收口。

## 六、第 13 条：备份线 9 支存量红（考古＋改尺，已落地）

- 实测起点：车道内该文件 **9 failed**，失败形态全是指向不存在的物件
  （`shipping backup.ps1 lost the $structural aggregate verdict line`、缺 `last_backup_partial_items`）。
- 考古三证：①测册由 88890cb6801（09-30）入库；②配套脚本腿**确实死在队列**＝blob
  `d882e1314ade9ab70d0cf6ecc5028e327e881d3bce8f6437280125804c831e00`（63,276 B 带
  `Set-VaultMtime`/`$structural`/两 state 键，被 ≥9 只死信携带），**但对 backup.ps1 全史 45 版
  逐版 sha256 比对零命中＝从未落地**；③该腿要治的病已被后落地三件替代——
  `Copy-FileShareTolerant`（cad41feb2f 09-29，只读位在复制层断根，且
  `tests/data/dr/test_backup_copy_share.py` 已有常驻尺钉旧路必炸/新路绿/只读位不遗传/mtime 逐刻一致）、
  `source_missing`（E-2 10-09）、`share_locked`（E-6 10-09，注释自证历史 vault 失败 15/17 属此类）、
  `vanished`（09-15）⇒ 残差 `$linkFail` 按构造＝结构性。
- 裁定＝令面第二条路（**改测册对齐真实键集**），旧腿**不救回**。代价面（在册）：
  救回＝给 `last_backup_status` 引入 partial 且 overall 仍 ok ⇒
  `scripts/ch/rolling_archive_reconciler.py:121` 的 `!= "ok"` 轮转闸会放行、
  `backup_daily_trigger.ps1` 日检 SLO 停报＝**弱化判据**，本班不做，呈备份线按 W4-R3 定策。
- 新尺四条：shipped `$vaultOk` 真值表 6 档（跑在**抽取的 shipped 判据**上，非复刻）／
  三条瞬态通道不得回流否决式／STAGE 4 state 键面精确到 `-NotePropertyName <k> -NotePropertyValue`
  位＋`code_backup` 三个可解释性字段／wave-4 键若落地必须与消费方同批（防"写了没人读"）。
- 双面自证：零突变基线 9 passed（含邻尺共 **12 passed** 正对照）；五类突变体**全红**
  （`transient_back_in_veto`／`veto_neutralised`／`state_key_renamed`／`interpretability_field_gone`
  ／`key_without_consumer`），脚本 `.runtime/tmp/maint6_item13_redproof.py`。
  **其中 `state_key_renamed` 第一版不红＝裸子串被 `last_attempt_status_renamed` 吞掉**，
  改精确到位后复验才红——这条自证过程本身值得留档。
- 袋：0012 → 1ecef831bfa0（`dumps_exposure_min` 的验收读法与销账见 §七）。

## 七、第 14 条：①branch 白名单通道清；②06:00 与 24h 节流定性入册

- ① `ai/st-bakday-20261013/task-bakday-wu5`：`git cherry` 判 tip 全等 dev（零丢失）。
  `-d` 被拒、`-D` 在危险命令清单内（宪法 §1.12）⇒ 本班**不越闸**，走在册白名单通道：
  `.runtime/quarantine/ahead_branches.log` 追加 `RESOLVED` 行（含判据与执行者）＋
  tip SHA 入 `branch_refs.log`（已读回：`0ba7828941de…` 实测在该文件末行）。
  分支 ref 本体留存，人工删除命令已在呈批面（§十）交回 Owner。
- ② 定性（五证，命令与期望值随注入册）：**对令面表述有一处机制更正**——
  计划任务 `ZephyrAlpha-DailyBackup` 执行体带 `-Force`（`wscript.exe launch_hidden.vbs
  backup.ps1 -Mode all -Force`），被 `backup.ps1:642` 的 `-not $Force` 短路⇒**06:00 那发不受
  24h 节流约束**；它不承载 CH 腿的真因是**撞锁早退**（10-12/10-13 两发 06:00 窗四轮即出：
  `Another backup is running (holder PID 34004 alive, lock age 5.4h)`＋`LOCK_HELD exit 0`）。
  "差 4 分 36 秒"的实测位置有两条：state 锚点 `2026-10-13T06:04:36+08:00` 对次日 06:00:00
  elapsed 1435.40 分 < 1440 分＝差 4.60 分；同一时长也体现在**锚点取整轮收尾时刻而非 CH 腿完成时刻**
  （CH 01:21:08 完成、整轮 06:04:36 收尾，`duration_seconds=19707.2`）⇒ 锚点被抬高 4h43m28s。
  10-13 全天分档：CH 真跑 1 发／cadence skip 13 发／撞锁早退 4 发。
  令面结论"06:00 结构性跳过 CH 腿、靠傍晚点火承载，功能通但判读易误读"**成立**，病名更正为
  "长轮跨过次日触发点"。
- 验收读法入册（统筹已裁）：`dumps_exposure_min ≤ 5 分钟` 只按 **chRan=True** 那发读，
  节流跳过轮的 0.17-0.32 分不作达标证据＝假绿陷阱；chRan 判别位沿用 backfix 班账在册命令，
  不另立二套尺。
- 袋：0013（backfix 班账纯尾追加一节；结构自证＝写前 1291 行/9 个 `## ` 节，写后 1350 行/10 节，
  前 1291 行与 dev 逐行字节相同，python 前缀差分实跑 True）。

## 八、P1-4 M-4 采样键复核（结论，落本账不碰他班在途件）

依赖"171／87 枚采样命中 0 枚"的在册结论实测复核（键面证据：`scripts/backtest/factory_grid_executor.py:2252`
`rec["gpu_self_sm_pct"] = attrib.get("sm_util_pct")`＝现行心跳用的是**正确键**）：

| 在册位 | 原结论 | 复核裁定 | 依据 |
|---|---|---|---|
| `docs/_working/gpufeed_campaign/03_gpux_final_report.md:857` | "1s 一拍共 171／87 枚采样命中 0 枚；**这不是尺坏**，是占空比算得过来" | **改写** | 该 0 是尺空读：吞吐针 `b2_throughput_sm.py:61` 存 `r.get("sm_pct")` 而 `nvml_process_util()` 实测返回键是 `sm_util_pct`（无 `sm_pct`），守卫用对键、存储用错键⇒`sm_unavailable` 恒等于总拍数。gpux4 复跑 n=120：226 拍里 **167 拍非空**，逐进程 SM 中位 6-9%／p90 12-14%／峰值 31%／≥70% 0/167 |
| 同册 `:37`／`:1296` 那条"批形下 ≥70% 在逐格形态**测不到**" | 半句依赖上条实证 | **改写**（"测不到"不成立、"没达到"成立且现为实测） | 同上；`:1296-1297` 已由 gpux4 自行改判，本班确认其改判成立 |
| 同册 `:625`／`00_gpufeed_report.md:341` M-8"≥70% 这条验收尺无判别力（60s 一拍 0/7）" | 不涉键错位 | **成立** | 心跳面键名正确（:2252 实证），0/7 是拍数与占空比的真实现象 |
| 同册 `:1954` "施工班自报 `sm_samples=0/sm_unavailable=268`＝尺没坏，是采样落进卡空窗" | 与 857 同族 | **改写** | `268` 那面对应键错位（存储侧取 `sm_pct`），须与"卡空窗"两因分计 |

- 未做的一件事与理由：本想把上表以一行指针追加进 `03_gpux_final_report.md`（其 :1350 挂着
  "属 M-4 待裁"），实测该件在主区是 **MM**（index 与工作树双向在途）＝他会话在途件，
  按纪律第 1 条**不代修、不随班提交**，结论全落本账，待裁销账交 GPU 线自走。

## 九、P2-1 死信班四件 merge-or-abort（已收口，判据数值零自拟）

- 逐件内容级四态（逐行差集实测）：
  - 袋 0001＋0004（`architecture_issue_registry.yaml`）＝袋独有 6 行／dev 独有 0 行＝strict
    superset。该册 PG 单源（REG-ARCH-ISSUE-001／family=entries），袋内字节退出物化⇒requeue
    只会假 done ⇒ 走意图 API 正门 merge：`api.register`（payload 从袋 blob 逐字解析，九字段零改，
    `entry_pk=90080`）→ `publish_snapshot`（v13／entry_count 820／content_sha `47e123c81b0772a7`）
    → `registry_projection_generator --render`（车道面 **+9/-0**）。落地自证尺＝该册相对 dev
    恰好 9 增 0 删且新增行即该案卷（无他人行混入）。
  - 袋 0003＋0006（`scripts/commit_queue.py`）＝袋独有 **0** 行／dev 独有 3 行＝**回退弹，判 abort**
    禁 requeue；同袋 `scripts/session_worktree.py` 袋字节==dev＝零差可销；0006 的死因
    BARE-SUBPROCESS 随弃码面一并失效。
  - 袋 0002 已在 `dead_archive`（先前四态分诊完成）；袋 0005 已落地 81d5a0c6f177
    （AGENTS.md＋并行协调政策＋deadclean 班账）＝本班不动。
- 接管条目 `st-deadclean-20261013`：`--resolve ... --by st-maint6-20261013` 已移入
  `.runtime/takeover/resolved`，处方逐项核完（claims／worktree／heartbeat 三面实测均归零）。
- 连带解锁：§五 的存证钩子袋得以改道新袋 0014 重投（未越闸）。

## 十、呈批面与残余（不代签、不自裁）

1. **备份线两件（本班只入册不动码）**：①`dumps_exposure_min` 锚点应记 CH 腿完成时刻而非整轮
   收尾时刻，或在固定触发点与 24h 节流之间留安全余量（否则 06:00 计划任务名实不符）；
   ②wave-4 四键（`last_backup_partial_items` 等）是否落 partial 档属判据面，落则须同批改
   `rolling_archive_reconciler.py:121` 的 `!= "ok"` 轮转闸与日检 SLO 读法。
2. **`ai/st-bakday-20261013/task-bakday-wu5` 分支 ref 人工删除**：
   `git branch -D ai/st-bakday-20261013/task-bakday-wu5`（`-d` 对 cherry-等值分支必拒、
   `-D` 在危险命令清单内）；内容零丢失已双证（cherry 判全等＋tip SHA 入 branch_refs.log）。
3. **`tests/gov/governance/audit/test_file_ops_enforcement.py::test_undeclared_delete_blocked_and_critical_warn`
   ＝存量红（非本班）**：车道红／主区红／两面按 HEAD 字节检出后仍红（三跑同集），本班已按
   "先备份 edited 再换 pristine"的处方做过换面 A/B。属 OPS-GUARD 判定面，建议维护线下一班
   与 §十.4 并案。
4. **MSG-STYLE 门的结构性盲区（在册病族）**：`_is_exception_constructor` 只认 Error/Exception
   后缀⇒`ArmParamUnfrozen` 这类非后缀异常名不被消费。原第 7 条本体统筹已销（dev 面实测干净版，
   本班 0006 早于该读数落地了字面改口），但**盲区未修**，属门禁判据面。
5. **P1-3 两条 HEAD 级 pytest 挂死地雷**：定性已完成（ Cartesian 全量展开
   725,760／13,063,680／52,254,720 名义格数；`position_recipe_compiler._expand` 每轮重建组合＋
   每配方两份 dict＋两次 json.dumps；Windows 上 pytest-timeout 的 thread 法杀不掉工作线程⇒
   表现为挂死而非失败）。**修未落**（本班上下文预算用尽，见 §十一）。邻家已有一条同族修法在册
   （矿考二班：测试走查面一律绑到模块自带有界常量，禁 `Path(".").rglob` 起手），
   下一班可照该式做"零展开 count_n_raw 路径／冻结窄批"两选一。
6. **P2-2／P2-4 未办**（接管台账"存量条目刷新出口"立法化＋刷 cband/fclean4、P-9 提案设计面）：
   均为独立判据面，逐件前置取证未做，留待下一班或另行派工。
7. **P2-3②（超时乙丙袋代投取正版）＝本班判定不投，附实测依据**：目标件
   `tests/gov/governance/rule_bridge/test_timeout_tier_thresholds.py` 的正版 blob
   `5e361f6dbdf9…`（6,422 B）与 dev 现值 `4ac2ddd426cc…`（6,228 B）的实质差＝**一行**：
   `REPO = Path(__file__).resolve().parents[3]` → `parents[4]`（件改道进 `rule_bridge/` 后深度+1，
   旧值把仓根解析到 `tests/gov/governance`）。复核主区面时实测 **index==worktree==目标 blob
   （三面 True）**＝该改动已由在途面自行到位并暂存，本班若代投＝把他人暂存件挂在我 commit 上
   ＝归属篡改（在册禁令）。⇒ 本班只登记，落地归属交该在途会话或下一班按 `git log -- <件>` 核。
8. **P2-3①③ 未办**（维护五班移交三件的另两件：P7 本体施工卡 §十二.4 与 26 件存证面、
   sim 班 `test_sim_daily_runner.py:111` monkeypatch 只登记待属主）：同 §十.6 处理。

## 十一、本班袋账（17 袋全清单）

| 袋 | 态 | 件 | 落地 |
|---|---|---|---|
| 0001 | done | approval_resolver ＋ test_approval_wiring | 153796c9d83d |
| 0002 | done | module_translation_registry（render 追齐） | 7e25b44708eb |
| 0003 | done | validate_rules_integrity ＋ 折叠测试 ＋ gate_registry 一行 | bd9a708a92b8 |
| 0004 | dead（自撤） | 与 0003 同字节重复袋 | — |
| 0005 | done | commit_queue_landing（`_trusted_base_head`）＋ 3 钉 | 78d89452294f |
| 0006 | done | arm_protocol_binding.py:298 字面改口 | 174b70ddaad1 |
| 0007 | dead（让路自撤） | ruling 册（改与 0008 合批带 509-515） | — |
| 0008 | done | ruling_registry（render 物化 514/515） | 2367ce12d985 |
| 0009 | done | maint4 班账代投 | ac3bc04a984e |
| 0010 | dead | ops_guard 存证钩子（RELATIVE-PATH-LITERAL） | — |
| 0011 | dead | 同件三袋（TAKEOVER-PENDING，后已 resolve） | — |
| 0012 | done | 第 13 条测册重写 | 1ecef831bfa0 |
| 0013 | processing | 第 14② 条 backfix 班账尾追加 | — |
| 0014 | pending | 第 8② 条存证钩子三件（blobs 取回后重投） | — |
| 0015 | pending | P2-1 案卷行 render 追齐 | — |
| 0016 | pending | 本班班账（本件第一版） | — |
| 0017 | pending | 本班班账（含 §十.7 P2-3② 不代投依据）＝以后袋为准 | — |

## 十二、零面声明

本班对 `G:\backup`／`F:` 业务面零写；未碰 `.runtime/commit_queue/blobs`（只读取回）；
未改任何判据阈值·保留线·计划任务·任务时限；未 `--force` 越闸、未 `--skip-preflight`、
未用 plumbing 命令；未杀停任何在飞进程（06:00 那发长轮的持有者全程未干预）；
改前 claim、毕后 release；本账与代码件同袋规则例外（班账单独成袋，在册口径"今后班账只单独成袋"）。

- 署名：st-maint6-20261013（令三 v2 维护线施工总包；对令面的两处实测更正见 §三与 §七.②，
  均为"结论不变、机制/病名更正"，按"留旧案卷、另起一节"口径单列，未改任何他人旧叙述）。
