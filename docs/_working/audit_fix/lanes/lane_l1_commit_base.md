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
