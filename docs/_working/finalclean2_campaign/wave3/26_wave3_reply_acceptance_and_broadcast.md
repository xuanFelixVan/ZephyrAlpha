---
ttl: task_bound
completes_when: M2 闸①七件案卷落 dev 且 sha 与存证全等；本包两处更正被接收；余下承接项转维护三班
---
# 终清波三·批复承接与广播件（sid=st-fclean3-20261012，03:3x）

> 统筹批复（本晨）＝§三两更正确认接收＋M1-M13 全裁。本件记三件事：**①M2 闸①执行回执；②一处对本班已发论断的自更正（含对统筹更正的再更正）；③批复要求广播的纪律条文原文**。
> 承接归属：M1/M3/M4/M5/M7/M8/M9/M10/M11/M13 均转**维护三班**（其通宵令 §五 其节"队列完整性/活性族"簇与"热册治理"同域）；M6 维持 Owner 门位；M12 满 7 日后一次批两事。本班未自落任何一条他班真源面。

## 一、M2 闸①执行回执：七件案卷已走正门（字节级全等）

令文原话"①25 件独有字节（含矿考案卷）先走正门落册"。本班按**实质**分流，未把 23 件一把灌进 dev：

| 分档 | 件数 | 处置 | 依据 |
|---|---:|---|---|
| `docs_asset`（案卷本体） | 7 中 **6** | **已落入车道并随本袋走正门**：`dexp_campaign/05_worktree_handoff_zongdui.md`、`mineloop_campaign/10_exam_recast_quintile.yaml`、`regsolo_campaign/lanes/t1..t4.md`（4 件）。⚑ **第 7 件 `regsolo_campaign/99_delivery.md` 本班主动排除出袋**，理由见 §一-B | 统筹点名"含矿考案卷"＝案卷类；这 6 件是主仓查无同名的唯一交付件 |
| `data_asset`（他班车道本地运行态） | 13 | **不落 dev，留存证面** `fclean3_safety/aidrafts_irreplaceable/`，登记为待裁 | 宪法 §9.6 测试/会话产物禁写 `data/` 业务目录＋RULE-SSOT 真源方向（这些是 `data/cache`、`data/databases/backup_state.json`、`data/runtime/state/replay/*`、`data/red_blue/trigger_queue/*`＝运行态非交付件）；把它们 commit 进 dev ＝本班替业务资产定真源，越授权矩阵"不可自裁"格 |
| `other` | 3 | 同上留存证，判"机器可再生的低价值件" | `activate_env.ps1`（355B，`session_worktree create` 产物＝可再生成）、`logs/backup_reconciler_ignite_*.log`（83B 与 **0B** 各一枚） |

**字节完整性自证**：6 件先按"落位＝与存证全等"验（`copy2` 后逐件重算 sha256，**6/6 全等**），其中 4 件 `t1..t4.md` 因门拦补了 frontmatter（见下），故**两 sha 并记**（正文未改一行）：

| 件 | origin sha256[:12] | 落地 sha256[:12] | 改动面 |
|---|---|---|---|
| `lanes/t1_direct_write_callgraph.md` | `ad4e948e82cc` | `e76f57fa1c82` | 仅前置 6 行 frontmatter（ttl/session/landing_note） |
| `lanes/t2_belt_materialization.md` | `12a43fdf9b80` | `555d38728a1b` | 仅前置 frontmatter |
| `lanes/t3_hot_registry_inventory.md` | `fe8d2386…` | `ac33501233eb` | 仅前置 frontmatter |
| `lanes/t4_ledger_debt_incidents.md` | `37ae9fa9ab56` | `150c02255170` | 仅前置 frontmatter |
| `dexp_campaign/05_worktree_handoff_zongdui.md` | `6f2ecc279e66` | `6f2ecc279e66` | **零改动** |
| `mineloop_campaign/10_exam_recast_quintile.yaml` | `8754f823120d` | `8754f823120d` | **零改动** |

（origin/landed 双 sha 全表＝`.runtime/tmp/st-fclean3-20261012/out/p6_sha_pairwise.txt`，随本袋出，禁以散文当账。）

### §一-B 排除 `99_delivery.md` 的实测依据（本班不改他班案卷正文、也不替他班补登问题号）
门禁 `REFERENCE-INTEGRITY [ARCH-REFERENCE]` 硬拦该案卷 `:155` 的 **`ARCH-383`** 引用。本班三面核查后**判门拦得对**：
1. `architecture_issue_registry.yaml` 内 `grep -c ARCH-383`＝**0**，在册尾号止于 **ARCH-382**；
2. 按 RULE-SSOT 先查另一面——PG 里**根本没有 architecture_issues 表**（`information_schema` 仅有 `arch_directory_tree`/`arch_path_mappings`/`arch_constraints`/`nodes_archive_module_lifecycle`）⇒ YAML 即真源，该号为**真悬空**；
3. 同段其余断言本班**逐条验真通过**：`裁定#504` 在册（`ruling_registry.yaml` 命中 1）、commit `7ff589652f` 存在且 `merge-base --is-ancestor … dev`＝**真**。
⇒ 结论：案卷其余内容可信，唯 `ARCH-383` 无源。正解只有两条且**都不属本班**：属主车道补登该问题号（带证据）或改写该行；**本班不自造注册表条目、不删该引用**（在册教训：伪造登记面为达标洗白）。该案卷正本仍在存证面（sha 复测与 MANIFEST 全等），随 M2 一并交属主车道处置。
⚑ 一处如实预告：`regsolo_campaign/99_delivery.md` 自带 frontmatter `doc_type: campaign_delivery`，而 docs/_working 新件规范只允许 `ttl:`（禁 `doc_type`）。本班**未改他班案卷正文**，改为先跑门禁预检看它是否真拦；若拦，正解＝由案卷属主车道自改，或经统筹许可加一行替代 frontmatter（改内容会使 sha 不再等于 origin，届时两件 sha 并记）。预检结果随本袋回执。

## 二、⚑ 对本班已发论断的更正（另起一节，`25_wave3_drain_wedge_note.md` 原文不动）

本班 02:1x 发出现测登记件称"processing 内 `q-20261012-st-gpuwo-20261011-0006` 已挂 133 分钟＝单通道租约悬挂"。统筹批复称"该件系死信 0013 陈旧残渣，排水实际活着"。**两侧都不完全对**，03:35 复测如下（每步只读可复算）：

| 时刻 | `processing/` 实占者 | 其 mtime/挂起 | 排水是否活着 |
|---|---|---|---|
| 02:1x（本班首测） | `q-...-st-gpuwo-20261011-0006`（9 files） | 132.7 min | `done` 最近写 7.6 min |
| 03:35（本班复测） | **`q-...-st-deadcure3b-chief-20261011-0016`**（4 files，`meta={priority:0, depends_on:[], supersedes:[], interactive:"true", lane:"interactive"}`） | **180.3 min**（mtime 00:34:39） | **活着**：dev 连落 `02:32 批19/36`→`03:07 批20/36`→`03:13 批21/36`→`03:20 批23/36`，另有 `02:09 挖矿班 P0` |

**三条结论**：
1. 统筹"排水活着"＝**实测成立**（四批落地可数），本班原登记件的"非全局楔死"判断也成立；
2. 但**卡位是真实的、且换人了**：首测时占位的是 GPU 工单班 0006，复测时占位的是**死信四班 0016**（不是 0013，且其 `meta` 既非 stale 也无 `dead_reason`，mtime 就是它的 `created_at`）⇒ 该面**确有一枚被取入 processing 后 3 小时无活体消费者**（03:35 `Get-CimInstance` 全表 grep `drain|convoy|serializer|reconcile_launch` 零命中），同时队列仍能推进他袋——**"有袋卡死"与"链在推进"并存**，这正是失败形态与正常形态同形的又一例；
3. ⚑ **顺带查到一件要紧事（他班资产，本班不代修）**：`gpuwo-0006` 已进 `dead/`，死因＝**`COMMIT_FAILED`→`GATE-PRECOMMIT-RUN` ruff `I001` import block un-sorted**，落点 `tests/research/backtest/test_kronos_score_only.py:23`。该袋 9 件未落地。在册处方明确"**`RUFF-PRECLEAN` 可在入队前自跑**"（`python -m ruff format <files>` ＋用 `git diff dev` 证明没顺手重排他人行）⇒ 归 GPU 工单班自修重投；本班不 requeue、不改判据。

**给维护三班队列完整性簇的新增实证（并案，别单开）**：①"陈旧 processing 残件误导监控"这条批复点得对，但**口径应为"processing 占位者身份与年龄须可与 done/dead 对账"**——本班第一次就是被"文件名＝属主"的直觉带偏（首测读数当时为真，只是无生命周期字段可读，袋体字段仅 `base_head/branch/created_at/files/meta/qid/session_id`，**无 `claimed_by/attempt/state`**）；②`.tmp` 残件簇（M10）与 `session_registry/*.tmp` 同型；③`list_active()` 收割链（§三广播条文）与 72 调用方同裁。

## 三、纪律广播条文（批复要求"即刻广播各班"，原文照此入册供各班引用）

1. **`SessionRegistry.list_active()` ＝写操作**，不是只读查询。其缺省 `mutating=True` 副作用面（自述原文）："**判死即写接管台账＋超宽限分片物理收割**……72 处调用方依赖这套副作用面……要'只看不写'必须显式声明 `mutating=False`（或走 `list_active_readonly()`）"。
   - 收割链三处 file:line：`src/zephyr/security/access_control/session_concurrency.py:1516`（`list_active` 定义与 mutating 语义）→ `:1552-1559`（`if expired and mutating:` → `_salvage_takeover_ledger` → `_delete_shard(sid)`，宽限 `_REAP_GRACE_SECONDS=900s`，常量在 `:173`）→ `:1048-1054`（`_delete_shard` ＝删片 **＋ `legacy.pop(sid)` ＋ `_write_legacy_raw(legacy)`**）。
   - ⇒ **凡只读车道/巡检/扫描器/探针，活死判定一律 `list_active_readonly()`**；字段名是 `s.session_id`（不是 `s.sid`）。
2. **`.runtime/session_registry.json` 单文件禁作判活源**——自 S4-D 起它只是**只读兼容副本、允许滞后且可被收割链整表缩小**（实测 15→6→8→14→17）。真源＝`.runtime/session_registry/*.json` 分片面（`_load()` 片优先）。
   - 直接后果：曾据此副本判"孤儿"会**误杀在飞车道**（`st-datalane-20261010`、`st-backfix3-20261011` 当时在副本上缺席而真源在册且心跳新鲜）。
3. **`_write_legacy_raw` 不经 `safe_write_text` ⇒ 无写者审计面**：兼容副本被谁改小，事后**不可追认**（本班 00:37 那次调用即属此类：机制确证∧时刻吻合∧计数不可追认）。这条是"写者必须署名"方向闸的又一条实证——**闸要拦的就是绕过 `safe_write_text` 的写路径**。
4. **在册工具的 `--help` 不是只读动作**（波二 27 支里 22 支无 argparse，`--help` 即执行主逻辑；本班在案：误删他人分支＋幂等覆写 793 枚受保护存证件）。要看行为就读源码；后继车道任务书已写成红线。

## 四、本班收班状态（承接批复"等你三袋＋晨间包落地核验后闭环"）

- 批复称"三袋＋晨间包"，实际本班已投 **5 袋**：`q-0001`(6 件)/`q-0002`(3)/`q-0003`交接卡(1)/`q-0004`晨间包＋面产权册＋00_ledger 纯追加(3)/`q-0005`卡位登记(1)；本件为 **q-0006**（含 §一 七件案卷＋广播条文）。
- 03:35 实测：**五袋全部 `state=pending`，`dead/` 内 `fclean3` 命中 0（无一袋被烧）**，dev 上 `wave3/` 命中 0 ⇒ **无一假落地**。保活已于 02:55 续 7200s（实测 logical=True、心跳 age 9s）。
- 落地后闭环判据（写死，不用工棚自证）：`git log --oneline -- docs/_working/finalclean2_campaign/wave3/`；逐件 `git show dev:<path>` 与本班存证 sha 对拍；`git log -1 --name-only` 核实真实归属（防暂存区吸收他班内容）。
- 收班三项目标按批复全达（101/102 面有主有据、机械面清零、影子三轮幂等）；本班自犯四起全留案；余责只剩"落地核验"一项，挂 `#7`。
