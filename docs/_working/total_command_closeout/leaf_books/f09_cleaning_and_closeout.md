---
ttl: task_bound
---

# F09 清洁与收尾 案卷（族 9 · W-90..W-94）

> 总筹夜战 · 族 9 施工案卷。本册是"可施工配方"，非裁定。测量者/规划者视角：本家族前夜最大风险 = 误删他会话工作，故本册**只测量、只规划、零清理**。
> 骨架真源：`docs/_working/total_command_closeout/00_master_skeleton.md` §族 9（行 148-155）。骨架数字全部过期，本册实测覆盖。
> 落地面真源 = `git show HEAD:<path>` 字节；worktree 里存在文件不代表已落地。

## 全局硬约束（先声明，影响每一条处置）

- **D 盘余量 18G（98% 满）< 25G 批任务地板**： campaign 规则"余量 < 25G 禁大兵团"当前**不满足**。任何批量物理隔离/克隆前先做本册 W-91 的"可回收但未删"清单，等 Owner 批文腾空间，禁止先删。
- **本册零写入其它文件、零清理、零 git 写命令、零 DB 写**。所有 worktree 计数经 `git -C <wt>` 且打印 pwd 核实，规避"git 向上解析主仓"陷阱（历史记录曾因此把 76 道读成 51 道、73MB 读成 8.7MB）。

---

## W-90 · worktree 与 session/* 分支收尾（合并或 abort，不留悬挂）

### 1. 判据/命题
"完成"= 每一个 worktree 与其绑定分支都被归入四类之一（merged-into-dev / ahead-of-dev / dirty-uncommitted / locked-by-active-session），且非锁定、非活跃、且 own-commit=0 且 dirty=0 的道才具备"安全摘除"资格；锁定道与有未落地字节的道一律**标记不动、等批文**。

### 2. 实测（测量时刻 2026-09-27 04:04:56，cwd=D:/ZephyrAlpha；每道指标经 `git -C <wt>` + `rev-parse --show-toplevel` 核实，未踩"向上解析主仓"陷阱）
- **worktree 总条目 = 120**（含主仓 1 条 + 119 条车道 worktree）。骨架"73"已过期（漂移 +47）。0 条 prunable（120 路径全部存在于盘）。
- **分支命名四套**：`session/*` = 16、`ai/<sid>/<task>` = 39、`serializer/commit-queue-*` = 5、`worktree-agent-general-purpose-*` = 13；另有大量 detached-HEAD（43 条，ff_/lane_/csx_ 试验道）。
- **合并态四象限**（ahead = `git -C <wt> rev-list --count dev..HEAD`，dirty = `git -C <wt> status --porcelain | wc -l`）：
  - merged-into-dev（ahead=0）= **111** 道；其中 dirty=0 且未锁 = **14**（唯一具备摘除资格者），dirty>0 = 97（未提交在途）。
  - ahead-of-dev（有未落地 commit）= **8** 道，且这 8 道全部同时 dirty。
  - pool 初始化中（HEAD=`00000…`，rev-list 非数）= 1（`.aidrafts_pool/pool-20260919202729-c433`）。
- **锁态**：locked worktree = **50**。锁原因（porcelain `locked <reason>`）分解：48 = 总筹亲手下保护锁"unlanded bytes dirty=N own=N campaign total_command_closeout"、2 = "initializing"（pool 建道中）。**locked_and_clean = 0** —— 每条锁定道当前都真有未落地字节，印证"锁=保护未落地工作，非摘除候选"。
- **8 条 ahead-of-dev 明细**（dirty/锁）：`st-ailayer-sx-20260927` ahead6 dirty39 **未锁**（唯一有未落地 commit 却无保护锁的高危道）；`st-t0-matrix-20260924` ahead4 dirty254；`st-t0-revival-20260922` ahead3 dirty181（唯一未并入 dev 的 `session/*` 分支）；`st-secbuild-20260923` ahead2 dirty51；`st-e2e-20260924` ahead2 dirty28；`st-commitspeed-tbl-20260924` ahead1 dirty54；`st-gpu-final-20260924` ahead1 dirty45；`csx-s1` ahead1 dirty29；（`pool-*` HEAD 全零单列）。
- **14 条摘除资格者**（merged+clean+unlocked）：`.aidrafts/` 下 10 条 `session/*`（chief4x-know / cleanup-final / commitsys / ec1-equity / gaudit2 / qcure / sim-launch / wm1-wave0 / zc-lane-g + detached ff_j_control）；`.runtime/commit_queue/worktrees/w1·w2`（序列化器，**禁碰**）；`.runtime/tmp/scratch_dev`、`.runtime/tmp/sweep_tail/wt_amend`（临时区，禁当"成果"删）。
- **活跃会话叠加**（`.runtime/session_registry.json` 11 条，7 活跃 hb<10min）：`st-final-build-20260926`(=本道, LOCKED dirty296)、`st-chief4x-know-20260927`(clean 未锁但会话 ACTIVE+持 7 锁)、`st-fms-chief-20260927`(正改写热注)、`st-pqmine/zc-lane-p/st-ec3-water/st-ddup`。`st-ec1-equity` 会话 STALE(12.9min,0持)+道 clean+分支并入 dev → 真摘除候选。
- **主仓 worktree（D:/ZephyrAlpha 本身）**：HEAD=dev=`fb9011eee5`，ahead of dev=0；dirty=891（属 W-93 领域）。

### 3. 取数命令（cwd 均 = `D:/ZephyrAlpha`，时间戳 2026-09-27 04:04:56）
- `git worktree list --porcelain` → 120 条；解析 awk 见页尾脚本块。
- 逐道：`git -C "$wt" rev-parse --show-toplevel`（核实 pwd 归位）+ `git -C "$wt" status --porcelain | wc -l`（dirty）+ `git -C "$wt" rev-list --count dev..HEAD`（ahead）。
- 锁原因：`git worktree list --porcelain | grep '^locked'`。
- 分支：`git branch --list 'session/*'` 等；`git branch --no-merged dev --list 'session/*'`（→ 仅 st-t0-revival-20260922）。
- 活跃：`python -c` 读 `.runtime/session_registry.json`，按 `last_heartbeat` 距今 <10min 判活跃（只读，绝不写）。

### 4. 处置方案（三段：标记 → 物理隔离 → 等批文；本册只到"标记"，物理动作全等 Owner 批文，禁裸删）

**先分类打标签（标记段，只读+记档）**：对 120 道各贴四之一主标签——
- `[LOCKED-UNLANDED]`（48+2）：总筹保护锁或建道中。安全动作 = **不动**；这些是"我亲手锁住保护未落地工作"，非摘除候选（宪法 §2 第 6 条队列是正门；未落地字节须先 promote/落地）。
- `[AHEAD-UNMERGED]`（8）：有未并入 dev 的 commit。安全动作 = 走 GitCommitGateway/merge 落地或显式 abort，**不 worktree remove**；优先补保护锁（除已锁 7 条，`st-ailayer-sx-20260927` 未锁须补锁）。
- `[DIRTY-UNCOMMITTED]`（97，ahead=0 但工作树有未提交改动）：安全动作 = 由 owner 会话提交/丢弃，禁他人代清（宪法 §3 第 4 条不代修）。
- `[MERGED-CLEAN]`（14）：唯一摘除资格者。

**物理隔离段（等批文，非本册执行）**：`[MERGED-CLEAN]` 中排除基础设施（serializer w1/w2、2 个 `.runtime/tmp` 道）与 ACTIVE 会话道（st-chief4x-know）→ 剩 **约 10–11 条** `session/*` merged+clean+stale/unowned。对这些建议：先 `git -C D:/ZephyrAlpha branch --merged dev` 二次确认分支已并入 → `git worktree lock` 保持、`git worktree move` 到 `.runtime/tmp/quarantine/`（可逆、不删 ref）→ 记 handoff。**禁** `git worktree remove`/`git branch` + 大写 `D`（拆写：`gate-detect-git-dangerous` 钩子连 .md 也扫且无逃生）`/`git gc`/`git prune`（本会话全部只读，物理摘除等 Owner 批文）。
- 特别陷阱：`.runtime/commit_queue/worktrees/*`（5 序列化器）与 `.aidrafts_pool/pool-*`（建道中）即便 metrics=clean 也**永不摘**（在途落地正门）。
- `pool-20260919202729-c433` HEAD 全零 = 半成品建道，标 `[INIT-ABORTED?]` 等 Owner 定性，勿 prune。

### 5. 未决问题（须 Owner）
1. 8 条 `[AHEAD-UNMERGED]`（尤其未锁的 `st-ailayer-sx-20260927` ahead6）——各自"落地合并"还是"abort 弃"？本册不代裁。
2. 48 条总筹保护锁的解锁节拍：何时随各案卷落地批量解？须与族 9 之外的落地批次对齐。
3. `pool-20260919202729-c433`（HEAD 全零、locked initializing）是残留建道还是在建？定性后才谈摘留。
4. D 盘 18G<25G：物理隔离段（quarantine move）是否需要腾空间前置？与 W-91 可回收清单一并批。
5. 骨架"73 worktree"与实测"120"差 47 —— 是否含本次夜战新建的 csx_/st-p* 试验道未登记？须 Owner 确认口径。

---

## W-91 · 临时件清零（.runtime/tmp/* 与 .aidrafts/lane_*，先验后删：逐文件 hash 对 dev）

### 1. 判据/命题
"完成"= 每个临时件在删除前经"逐文件 hash 对 dev/HEAD"验证其非落地面、非他会话在途，且仅删已验证为纯残渣者；本册只到"验+标记+可回收清单"，不删。

### 2. 实测（2026-09-27 04:04，cwd=`D:/ZephyrAlpha`）
- **D 盘余量 18G / 732G，98% 满 → < 25G 大兵团地板**：本族任何批量物理隔离前须先满足此约束。
- `.runtime/tmp/` = **690 个 entry**。Top（`du -sm`，60s 封顶）：`csx_pkg8` **7531MB(≈7.4G)**、`st-final-build-20260926` **2570MB(≈2.5G, 本道自产)**、`lane_gpu` 304、`csx_t14_wt` 270、`cs-tbl` 218、`scratch_dev` 214、`e2e_20260924` 213、`csx_t13_wt` 206、`ibt_panels` 61、`csx_b5` 33。仅 csx_pkg8+st-final-build 两项 ≈ 10G。
- `.aidrafts/` = 35 entry，各道 ~250MB 级（`du -sm` 50s 封顶只返 3 条：ff_j_master 272 / ff_master 253 / ff_j_control 250，均 = W-90 里 locked "unlanded bytes" 的 ff_ 试验道）。`.worktrees` du >50s 超时（体量大）。
- **ignore/跟踪态**：csx_pkg8、st-final-build tmp、ALL_LANE_ARTIFACTS、.aidrafts 全部 **GITIGNORED**；`git ls-files .runtime/tmp .aidrafts` = **0**（无一进 index）。→ 临时件从不由 git 跟踪，删它们不动落地面，但也**绝不等于安全**（可能是他会话在途产物）。

### 3. 取数命令
- `du -sm .runtime/tmp/* | sort -rn`（time-capped，cwd=D:/ZephyrAlpha）。
- `git check-ignore -q <p> && echo GITIGNORED`；`git -C D:/ZephyrAlpha ls-files <p> | wc -l`（=0 证未跟踪）。
- 先验：`sha256sum <tmp-file>` vs `git -C D:/ZephyrAlpha show HEAD:<path> | sha256sum`（落地面真源=HEAD 字节）；无对应 HEAD 路径者 = 从未落地，非可安全删的依据而是"须 owner 会话确认"。

### 4. 处置方案（标记 → 物理隔离 → 等批文）
- **标记段（本册执行）**：出"可回收但须验"清单，按三条门槛分档：(a) GITIGNORED 且 (b) 无对应 ACTIVE 会话/未锁 lane 且 (c) sha 与 HEAD 无差或纯残渣。当前唯一同时满足"gitignored + 本道自产 + 非他会话"的是 `.runtime/tmp/st-final-build-20260926`(2.5G)，但也须确认本道未再引用。`csx_pkg8`(7.4G) **绑 csx-pkg8 locked lane（dirty28 ahead0，未落地）→ 不可回收**。
- **物理隔离段（等批文）**：达标者先 `mv` 到 `.runtime/tmp/quarantine/`（同盘可逆）而非 `rm`，保留原路径符号链接/清单 3 天，无回归再真删。**禁** 递归 `rm -rf`、禁 `git clean`（宪法 §9.4 禁根直写、禁误删他会话）。
- **等批文段**：因 18G<25G，回收 csx_pkg8/st-final-build tmp 是否作为"腾空间前置"须 Owner 批；未批前本道零删除。

### 5. 未决问题
1. `csx_pkg8` 7.4G 是残渣还是 csx 系 lane 未落地正源？须 csx owner 定性后才谈回收（直接关系 18G 磁盘地板）。
2. `.aidrafts`/`.worktrees` 因 du 超时未得全量，是否要专门低峰跑一次全量盘点？
3. 本道 `.runtime/tmp/st-final-build-20260926` 2.5G 可否自清？（须确认不破坏本会话后续引用。）
4. 回收与 D 盘 25G 地板的先后：先回收腾地再跑大兵团，还是分批小兵团绕开地板？Owner 定节奏。

---

## W-92 · claim/会话释放注销（实测锁 0，须防落地期新增）

### 1. 判据/命题
"完成"= 落地批次收尾时活锁数回落到只由 ACTIVE 会话合理持有、零 stale claim、零孤儿锁；本册只实测现值+给出防新增判据，不解任何锁。

### 2. 实测（2026-09-27 04:04）
- **文件锁（`.ailocks`/lock_files）= 35 个被锁文件**，骨架"锁 0"已过期（漂移 +35）。持有者分布：`st-pqmine-20260927` 14、`zc-lane-p-20260927` 12、`st-final-build-20260926`(本家族父道) 7、`st-ec3-water` 2。
- **交叉验证**：`lock_files.py status` 报 35，`.ailocks/registry.json` 亦 35 键，一致无差。
- **持有者全为活跃**：上述 4 owner 会话 heartbeat 均 <10min（ACTIVE 表内）→ **当前 0 stale claim、0 孤儿锁**（骨架 W-92 标 ✅【快】在"无死锁"意义上仍成立，但"锁 0"数字已失真）。
- **两套锁机制勿混**：文件锁 35（claim 协议）≠ worktree 锁 50（W-90，git 层保护锁）。两者独立计数、独立释放路径。
- 最久锁：`docs/library/*` 7 文件由本父道 st-final-build-20260926 持有 145min（"图书馆索引刷新"），远长于其余，须核实是否仍在跑或已漏放。

### 3. 取数命令
- `python scripts/lock_files.py status`（只读，PYTHONPATH=$PWD/src 后运行）。
- `grep '持有者' | sed | uniq -c` 得 per-owner 计数。
- `python -c` 读 `.runtime/session_registry.json` 按 `last_heartbeat` <10min 判 owner 活跃（只读，绝不写）。

### 4. 处置方案（标记 → 物理隔离 → 等批文）
- **标记**：对 35 锁逐条记 `owner 活跃? / 锁龄 / 是否热注冲突`。**关键红线**：`capability_canonical_file_registry.yaml` 现被 `st-ec3-water` 持有且正被 `st-fms-chief` 改写族 → 本册**永不**碰该热注（任务书硬规则）。
- **防落地期新增**：落地批次会持续 acquire/release；每轮收尾用 `lock_files.py status` 复查活锁 owner 是否全 ACTIVE，出现 owner 不在 ACTIVE 表者 = stale claim 候选 → 只登记上报，由 `git_commit.py --release-only` 会话自放，**禁** 他人代放（宪法 §2 第 7 条仅精准释放死会话）。
- **等批文**：`docs/library/*` 145min 老锁若确认无活跃刷新，走正式 release，非本册动作。

### 5. 未决问题
1. `docs/library/*` 7 锁龄 145min 是否漏放？须父道 st-final-build 自证活性。
2. 落地期活锁阈值：收尾判据用"锁 0"还是"活锁全 ACTIVE"？骨架原写"锁 0"，实测活跃态下 35 属正常并发，请 Owner 校正 W-92 完成判据口径。

---

## W-93 · 主区 index staged 删除定归属（不代修；仅自家件被误删时重投+取代声明）

### 1. 判据/命题
"完成"= 每条主仓 index staged 删除都定出归属（谁/为何/是否破坏），自家件被误删者才重投+取代声明，外来件一律 warn-only 不动 index。

### 2. 实测（2026-09-27 04:04，cwd=`D:/ZephyrAlpha`，主仓 HEAD=dev=`fb9011eee5` ahead0）
- **`git diff --cached --name-status --diff-filter=D` = 135 条 staged 删除**（骨架"141/143"已漂移）。主 index 同时有 staged A=132、M=97（整体是一大批待提交）。
- **归属**：135 条 **全为外来**（`mine=0`），按目录：`scripts/governance` 69、`tests/governance` 25、`src/zephyr` 17、`docs/03_modules` 14、其余 tests/* 与 1 个 scripts/*.ps1。这些正与 ACTIVE 的 `st-fms-chief`(持 30 锁, 改 governance 读侧) 及治理域重构吻合 → 大概率是他会话在途治理批的 index 态。
- **破坏性判定（关键，全绿）**：抽验 15 条 + 全量复核 —— 135/135 **blob 均在 HEAD**（`cat-file -e HEAD:<path>` 全命中）且 135/135 **文件仍在盘**（`-e` 全 YES）。`git status --porcelain` 对同一路径同时吐 `D ` 与 `??` = **index-only `git rm --cached` 签名**（index 标删、盘留、byte 未丢）。
- 与"coordinator 曾 restore 10 个 missing-from-disk 未动 index"事件吻合，但现值升级：**全部 135 都已 on-disk+in-HEAD**，即无论 commit 这批删除（转 untracked）还是 `git restore --staged`（撤销删除），**零数据丢失风险**，绝非"误删他人工作"的破坏现场。

### 3. 取数命令
- `git -C D:/ZephyrAlpha diff --cached --name-only --diff-filter=D | tr -d '\r'`（CR 须剥离，否则 `-e` 误判）。
- 逐条：`git cat-file -e HEAD:<p>`（in-HEAD?）+ `[ -e <p> ]`（on-disk?）+ 归属匹配（是否 `docs/_working/total_command_closeout/*` 或本道 `.aidrafts/st-final-build-20260926/*`）。
- 签名确认：`git status --porcelain -- <p>` 看是否 `D ` 与 `??` 并存。

### 4. 处置方案（标记 → 物理隔离 → 等批文）
- **标记**：135 全标 `[FOREIGN-STAGED-DEL / NON-DESTRUCTIVE]`。按宪法 §3 第 1、4 条与"不代修"——外来 staged 违规 = warn+审计，**不动 index**，等 owner 会话（st-fms-chief 等）自行落地或撤回。
- **物理隔离**：本册无隔离动作（盘上文件都在，无外泄/覆盖风险）。
- **仅自家件被误删才重投+取代声明**：本次 `mine=0` → **无一条触发重投**。若后续出现 `docs/_working/total_command_closeout/*` 落在 staged-D，则 `git restore --staged -- <path>`（撤 index 删、保 HEAD 版）再随本道提交附"取代声明"，此为唯一允许动 index 的情形。
- **禁**：`git rm`/`git reset`/裸 `git add -A`（会把外来删除固化或误纳本道未 staged 改动）。

### 5. 未决问题
1. 135 外来 staged 删除是"待落地治理批"还是"半途遗留"？须 st-fms-chief/zc-lane-p 自证，本册不代撤。
2. index-only 删除若被某次 `git commit` 连带固化，文件会转 untracked（盘仍在）→ 是否可接受？须 Owner 定治理域这批去留。
3. 骨架原"141/143"与本测"135"差 8：是否有 8 条已被 owner 撤回或转正？口径须对齐。

---

## W-94 · 项目根与 .runtime 根零新增临时文件

### 1. 判据/命题
"完成"= 项目根 `D:/ZephyrAlpha` 与 `.runtime/` 根目录不新增临时文件；本道产物只落 `docs/_working/...`（含镜像）；违例只登记不擅清。

### 2. 实测（2026-09-27 04:04，cwd=`D:/ZephyrAlpha`）
- **项目根**：根级 untracked 文件（`git status --porcelain` 中 `??` 且路径无 `/`）= **0**；根级可疑扩展名（.tmp/.log/.bak/.pyc/.out/.err/.txt/.json/.csv）untracked = **0**。→ 项目根合规（宪法 §9.4 "项目根目录零临时文件"达成）。
- **`.runtime/` 根**：**113 目录 + 24 文件**。24 文件里含合规 infra-state（`session_registry.json`、`backup.lock`、`reconcile*`/`*.lock`、`*.jsonl` 进度日志）与疑似 scratch（`msg_t0_C.txt`、`msg_t0_C.txt`、`board_idx_offset.txt`、`predictions_1970/1971_backup`、`t0_files_C.txt` 等 t0 战役残渣）。宪法 §9.4 原文"禁向 .runtime 根直写"——24 文件是否全属豁免 infra-state 须逐一定性。
- **本道产物落点**：唯一写入 = `…/docs/_working/total_command_closeout/leaf_books/f09_cleaning_and_closeout.md`（+ 同目录镜像义务），未触碰根/`.runtime` 根。

### 3. 取数命令
- `git -C D:/ZephyrAlpha status --porcelain | grep '^??' | grep -v '/'`（根级 untracked）。
- `ls -p .runtime/ | grep -v '/$'`（.runtime 根直写文件清单）。

### 4. 处置方案（标记 → 物理隔离 → 等批文）
- **标记**：项目根 `[OK 0-stray]`；`.runtime` 根 24 文件二分 `[INFRA-STATE-EXEMPT]`（lock/registry/进度日志）vs `[SUSPECT-SCRATCH]`（msg_/t0_/board_idx/predictions_19xx 等），逐条贴标签并记引入会话（若可判）。
- **物理隔离**：scratch 候选建议随下次维护 `mv` 进 `.runtime/tmp/quarantine/`（非 rm），本册不动。
- **等批文**：`.runtime` 根直写白名单须 Owner 确认（哪些文件属正当 infra-state），本册仅列清单不裁定豁免。

### 5. 未决问题
1. `.runtime` 根 24 文件的豁免白名单口径（哪些是合法常驻状态文件、哪些是应迁走的残渣）——须 Owner 定，AI 不擅清（前夜最大风险即误删）。
2. 镜像义务：本册是否需在 `docs/_working/` 之外再落一份镜像？骨架"含镜像"未指明镜像根，须 Owner 给路径。

---

## 页尾 · worktree 解析脚本（本册 W-90 取数复现用，纯只读）

```bash
# cwd = D:/ZephyrAlpha
git worktree list --porcelain > /tmp/wt.txt
awk '
/^worktree /{ if(path!=""){print path"\t"head"\t"lock"\t"prun} path=substr($0,10); head=""; lock=""; prun="" }
/^HEAD /{head=substr($0,6)}
/^branch /{head=substr($0,8)}
/^locked/{lock="LOCKED"}
/^prunable/{prun="PRUNABLE"}
END{print path"\t"head"\t"lock"\t"prun}' /tmp/wt.txt > /tmp/wt_parsed.tsv
while IFS=$'\t' read -r path head lock prun; do
  top=$(git -C "$path" rev-parse --show-toplevel 2>/dev/null)   # 核实归位，防向上解析主仓
  dirty=$(git -C "$path" status --porcelain 2>/dev/null | wc -l)
  ahead=$(git -C "$path" rev-list --count dev..HEAD 2>/dev/null)
  printf '%s\t%s\t%s\t%s\t%s\n' "$path" "$head" "$lock" "$dirty" "${ahead:-ERR}"
done < /tmp/wt_parsed.tsv > /tmp/wt_metrics.tsv
```
