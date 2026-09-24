---
ttl: task_bound
---
# L1 提交链基底修复（F-AUDIT-QUEUE-04 治本）· 挖矿簿

> 环节=E05 ｜ 子环节=4（正门口 / 袋字段口 / 落地判定口 / 判据口）｜ 状态=封矿·已施工·待落地复验
> 优先级说明：本件是其余四件的**防护前提**——不修它，L2 落完会被下一个陈旧袋再吃一次（已实证两次）。

## 子环节 1｜正门口：`scripts/git_commit.py` enqueue 通道不传基底

- **现状三态实测**：`grep -c "base-head\|base_head" scripts/git_commit.py` = **0**（14:3x 修前）；
  生产袋读数=本包 0001 号袋（由未修版主区 CLI 投递）`base_head=None`、4 件 `base_blob` 全 None ⇒ **正门全量，非个案**。
  对照：machine 车道 `commit_queue_landing.reroute_auto_commit_to_queue` 一直带基底（`:2277` `rev-parse refs/heads/{_TARGET_BRANCH}`）⇒ **同仓两套入口不一致**是病灶本体。
- **代码位**：`git_commit.py:899` 起 `_enqueue_mode` 的 `enqueue_item(..., EnqueueOptions(deletes=..., meta_extra=...))`。
  三条改道（`--enqueue` / LOCK_TIMEOUT 自动改道 `:1310` / `:1244`）全部汇入同一函数 ⇒ **一个改点覆盖三门**。
- **判据**：`grep -c base-head scripts/git_commit.py ≥ 1`（审计班给的第一半）→ 实测修后 **6**。
  永久化=`tests/governance/test_commit_queue_base_head.py::test_maindoor_enqueue_channel_passes_base`（grep 的断言化，防"删注释即算修好"）。
- **裁定**：基底取 `refs/heads/<_TARGET_BRANCH>` 而非 worktree HEAD。理由：落地侧语义是
  `_changed_paths_between(base, dev)`，用 session 分支 HEAD 会把**本会话自己的改动**算进"dev 推进"，
  造成系统性假冲突死信；用 dev HEAD 才是"我入队时 dev 在哪"的诚实锚点（与 machine 车道同源，不另立口径）。

## 子环节 2｜袋字段口：`base_blob` 全仓无填充点（尺T 的"结构空转"）

- **现状三态实测**：`commit_queue.py:696/712` 两处硬编码 `"base_blob": None  # A 段预留（B 段：git rev-parse HEAD:{path} 填充）`
  ——B 段从未做；`git grep base_blob` 除 tests 外零写点 ⇒ `_revalidate_stale_base`（`:1057`）对每条恒走 `if not base_blob: continue`。
  修前跑尺T：`C1 生产形态 base_blob=[None] → ok=True mismatch=[]`（＝恒放行）而 `C2 填 base 且漂移` 必报 ⇒ **尺非恒红，病灶在生产侧**。
- **口径校验（本包差点踩的坑）**：`base_blob` 必须与 `_pool_head_reader`（`landing:2149` `rev-parse refs/heads/dev:<rel>`）
  同一 id 空间＝**git blob sha**。仓内另有 `blob_sha256`（内容 sha256）与 `content_sha256(text)` 三套口径，
  选错即"每条恒判漂移"的全量假红。实现用 `git ls-tree <base> -- <paths>`（单批多路径）取 blob sha，50 路径分块（Windows 命令行上限）。
- **裁定**：不破坏 `enqueue_item` 的"零 git 依赖"不变量（66 号 §6.1 刻意出入 #3，测试靠它做全 tmp 隔离）——
  取数放 `commit_queue_landing`（本就是 git 感知层），经 `EnqueueOptions.base_blobs` 以**纯数据**入队层。
  裸 CLI `commit_queue.py enqueue`/`requeue` 也补自取（否则"两套入口不一致"复发）。

## 子环节 3｜落地判定口：缺 base 时兜底 `old_dev^`＝把陈旧读成删除

- **现状三态实测**：`_merge_registry_file:1071-1075` `base_sha = item.get("base_head") or ""`，无效即
  `rev-parse {old_dev}^` 兜底 ⇒ 他人条目落在 `old_dev^..old_dev` 之间时，base 已含、陈旧快照不含 ⇒ **合并器判"theirs 主动删除"并忠实执行**。
  实物案例（本包取证锁定加害批）＝`2608b45148`（11:13，袋 `q-…-st-mapcensus-20260924-0006`，`base_head=None`）
  把 L2 的 `related_arch: []` 又写回成 `['MOD-L00-004']` —— **同病灶的第二次实证，且这次连"陈旧 index 会删掉 第 411 号裁定/#412"一起带回来了**。
- **非注册表面（面积比在册记载大一档）**：`_conflict_reason:1007` `if not base: return None` 早退发生在注册表/非注册表**分流之前**
  ⇒ 注释承诺的"非注册表文件维持逐文件快进判定"（`:179-181/196-197`）在生产形态不成立 ⇒ **任意文件＝后落地快照整覆盖**。
  修 base_head 即恢复，无需给 `_apply_snapshot` 再加一道 HEAD 比对（避免双真源）。
- **裁定**：缺基底改 fail-closed 死信（审计班 07:52 块"唯一正解"原文：缺 base 时应死信而非猜 base）。
  代价与收益：历史 47 只 pending 袋重投时会多一轮 dead→requeue（可见、可恢复），换掉的是"静默吃条目"（不可见、不可恢复）。
  **本包自纠一条设计漏洞**：原打算用 `base_blob=None` 表达"基底无此文件（新增件）"，
  但 JSON 里"键缺失"与"值 null"不可区分，会把 null 误读成新增件语义 ⇒ 合并器可能复活已删条目 ⇒ 改为二者一律死信。

## 子环节 4｜判据口：把审计班的一次性探针固化成永久 pytest

- 审计班尺T/尺U 在 `.runtime/tmp/audit_all_20260924/`，随 E12 清理即消失 ⇒ 回归无人守。
- 本包新增 `tests/governance/test_commit_queue_base_head.py`（7 例，tests/ 免 CREATE-GUARD 与 TRANSLATION-COVERAGE，实测源码级豁免条款＝`translation_coverage_gate.py:95,124`）：

| 例 | 类型 | 断言 |
|---|---|---|
| resolve_base_head/blobs 契约 | 阳+阴 | 取到 dev HEAD 与 blob sha；真·非仓库目录 → None |
| >50 路径分块 | 阳 | 120 路径逐块解析一块不丢 |
| CLI enqueue 自取基底 | 阳 | 袋 `base_head==dev`、`base_blob==rev-parse HEAD:path`、重校验可达 |
| 正门接线守卫 | 阴（防摘线） | git_commit.py 含 `resolve_base_head(`+`base_head=base_head`+`base_blobs=base_blobs` |
| **用户口径红测** | 阳+双阴 | A 入队基底 X → B 先落地同路径 → 必报"快进判定失败"；未触同路径不报；基底对齐不报 |
| 注册表不猜基底 | 阳+双阴 | 记真基底→他人条目 B/C 必存活；无基底→raise；退用 base_blob 亦救回 |
| §6.4 重校验活性 | 阳+阴 | 填了 base_blob 后：一致放行、漂移必报（尺T"空转"反证） |

- **本尺自我否证一次（如实记）**：阴性控制组最初用 pytest `tmp_path` 当"非 git 目录"，实测返回主仓 dev HEAD——
  因为 `tmp_path` 落在仓内（`.runtime/tmp/pytest_*`），`git rev-parse` 向上穿透命中外层仓。改用 `tempfile.TemporaryDirectory()`。
  立法：**做"非仓库"阴性对照前，先证该目录确实不在任何仓内**。

## 落地凭据与缺陷追注（实测，勿引早期版本）

- 第①件正门/入队侧＝`c58da6cb06`（HEAD 版 `git_commit.py` grep base_head=6）；
  落地侧与存量兜底同批，但**该批含 S-12 缺陷**（`_legacy_base_drift_reason` 误用实时 dev tip 而非入参点位），
  修好版随补充批落地（见 LEDGER §7 S-12）；本 lane 的最终形态以补充批之后的 HEAD 为准。
- 生产现场双证（比测试更强的证）：袋 0007 被新快进判定拦下（它会静默覆盖本包 3 秒前刚落的 L1 代码）、
  袋 0004 被 §6.4 重校验判 `cascade_stale`（`base_blob` 有数据后该检测器才第一次真正工作）。
- 常驻 `commit_belt_daemon`（05:14 起，旧码）由计划任务探测重拉后接受落地侧改动；
  本包不重启共享守护（非授权面）。入队侧与进程内自举路径已是新码。

- **口径自纠（2026-09-24 21:5x，F-AUDITFIX-STALE-01）**：本包第一版把 `base_head` 取成
  "入队那一刻看到的 `refs/heads/dev` 尖"——工作区落后 dev 时这是**错的**：快照字节来自本工作区
  自己的树，基底却记成了比字节还新的点位 ⇒ `diff(base, dev)` 恒空 ⇒ 快进判定结构性失明。
  今晚正是这个口径让 `q-20260924-st-commitspeed-tbl-20260924-0005`（**带** base_head=e500df6dfe）
  把已在册的 `4442b1b4f6`（本 lane S-12 那一批）整文件覆回旧版——修复被自己的修复口径吃掉，
  构成 ① 号任务的实际未收口面（不是"没记基底"，而是"记的点位不是字节的来源"）。
  现口径三改：`resolve_base_head(工作区) = git rev-parse HEAD`（快照真源）；dev 侧推进一律以
  `merge-base` 为界度量（会话分支上有自有未并入提交时不得假红）；仅当"快照字节与 dev 现态同
  git blob id"（覆盖＝无操作）才短接放行。`reroute_auto_commit_to_queue` 里另写的那条
  `rev-parse refs/heads/dev` 同步改调 `resolve_base_head`——两通道一律同源，禁各写一条口径。
  永久尺＝本文件末 4 例（`tests/governance/test_commit_queue_base_head.py`），其中含**反事实
  控制组**：把同一袋的基底填回旧口径必判 None，用以证明本红来自口径而非路径重叠。


## 子环节 5｜CAS 冲突重放的**整树回退**（红队 P0，2026-09-24 22:34 生产实证）

- 症状：本包 0027 落地 `deffd84640`（22:33:19）后 41 秒，`q-…-st-mapbuild-…-0017` 落地
  `9de51e673f` 把本包 4 件在册文件全部回退，而**那只袋的 `files` 里根本没有它们**
  （只有能力册 + 其自己的 map_build 案卷）。⇒ 只看袋内容与基底判据永远查不到这条腿。
- 机理：k=4 池 `dev ref CAS` 冲突时走 `_replay_commit_without_gates` 分支①——
  `commit-tree prev_commit^{tree} -p new_dev`。而 `prev_commit` 的树是
  「base_dev + 本袋」的**全量快照**：本袋未列出的路径在树里仍是 base_dev 的旧字节。
  旧判据 `need_remerge = 注册表路径 ∩ drift` 只看得见注册表，看不见"非注册表路径被他人
  在期间推进"，于是零重叠即 re-parent ⇒ **期间他人落地的一切路径被整树退回**。
  同族先例：09-22 fb5a7821d、09-24 通宵"0 增 N 删"（那两条在合并器，本条在重放器）。
- 治本（`_replay_commit_without_gates`）：仅当 `changed_paths(base_dev, new_dev)` **为空**
  时才复用旧树（此时 re-parent 数学上是恒等操作，保 message 逐字节的初衷不受影响）；
  有任何漂移 ⇒ 一律在 new_dev 上重建树（read-tree new_dev + prestage 本袋件 + write-tree）。
- 永久尺：`test_cas_replay_does_not_revert_third_party_paths`（tmp 真 git 仓 + 真 worktree，
  断言重放 commit 同时含他人新字节与本袋件；把判据改回旧式即红，已双向验）。
- 同批红队补硬（同一函数的其余三条腿）：
  ① `_merge_registry_file` 的 `ours is None` 分支不再无条件写回——若本袋**基底**里有该
     注册表文件而 dev 已删，那是"复活已删件"，死信回人工（`_base_had_path` 只认正证据，
     基底不可知仍按新增件放行，避免把新建册通道拦死）；
  ② `_conflict_reason` 的基底合法性从 `cat-file -e` 改为 `cat-file -t == commit`
     （`-e` 认 blob/tree/tag，非 commit 值会让 merge-base 失败后再抛异常＝崩栈而非受控死信）；
  ③ 新增 `_drift_all_same_session`：同路径漂移若**全部**由本会话此前落地构成 ⇒ 判为
     同包迭代放行（否则工作区停在分叉点的会话从第二袋起系统性假死信，会堵死整个车队；
     判据用 `[GW:sid]` 归属，任一提交无标记或属他会话即不豁免）。
- 登记未做的两项（不在本夜扩面）：
  ① 交互正门 `resolve_base_head` 取不到 HEAD（工作区 unborn，如 session_worktree 刚建未提交）
     时现落 `None` → 走时间兜底（fail-open）。正解＝**门侧拒投**（`git_commit.py`/
     `commit_queue.py enqueue`：目录是 git 仓但 HEAD 不可解 ⇒ 报错退出，而非静默无基底袋）。
  ② `--allow-tracked-drift` 的语义仍是"把工作区与 dev 的差异一并带上"——陈旧工作区下这会
     把他人落地列入本袋（本条 5 的 ①②③ 已在落地侧拦住其后果，但门的清单本身应改为
     "只带与本会话自身 HEAD 有差异的路径"）。
