---
ttl: task_bound
completes_when: 本班退场执行的逐棵回执落 dev 且与本案卷 §2 决策表逐棵对得上；闸①清点件被回执引用
session: st-fclean4-20261012
lane: wave4-main
role: 总包（本案卷＝施工前案卷，回执另册）
generated: 2026-10-12T21:4x（开工前落盘，边跑边 Edit 追加）
---

# 终清波四·M2 施工前案卷（工作树退场：现面普查＋四态核＋闸①清点＋通道选择）

> 令卡＝Owner 2026-10-12 夜【终清波四 st-fclean4-20261012】大面处置执行令。起点读物＝波三 `wave3/`（15 件在 dev）＋统筹对 M1-M13 批复（波三 `26_` §承接归属）。
> 本案卷只登记**实测与裁定依据**；退场回执在 `21_wave4_m2_receipts.md`。

## 0. 口径与红线（先声明，防后人误用）

- **参照点是移动靶（本班实测坐实，非波三独有）**：本班 21:16 起批时主区 `HEAD`=`c52d81aa96`（跟踪件 20,869），21:21 四态尺跑完时已变 `cac7ac2132`，21:2x 决策表读数为 `7599a6aff2`。
  ⇒ §1/§2 的 A/B/C1/C2 与件数字节**只对各自采样时刻成立**；复算者必须先 `git rev-parse HEAD` 对齐再比数值。
  ⇒ 本班对"某件是否可再生"的结论一律以**逐件 sha 实测**为准，不以本表聚合数为准（波三在册教训）。
- **体积口径**＝逐文件 `os.path.getsize` 求和（apparent），非 `du`（du 因簇开销虚高，波三已证 86.9MB vs 12.9MB）。
- **活性真源**＝`.runtime/session_registry/*.json` 分片面**直读**（本班脚本只做 `json.loads`＋`time.time()` 差）。
  **禁** `list_active()`——它是写操作（判死即写接管台账＋超宽限物理收割分片，`session_concurrency.py:1516` 自述；波三 `26_` §三 广播条文第 1 条）。
- 工具红线：**未对任何在册工具执行 `--help` 或裸跑**；波三四态尺三件套（`census_aidrafts.py`／`four_state_aidrafts.py`／`delta_vs_lane_head.py`）按 `sed` 改 `OUT` 后**复制到本班 tmp 副本**运行，波三原件零触碰（波三 `.runtime/tmp/st-fclean3-20261012/` 是 TTL 面，本班只读不写）。
- 本班在本节之前的动作＝**零删除、零退场、零 git 写**；唯一写面＝本班 `.runtime/tmp/st-fclean4-20261012/` 与本车道 `docs/_working/finalclean2_campaign/wave4/`。

## 1. 现面普查：令卡说 16 棵，实测 18 棵（差因逐条）

| 差因 | 件 | 证据 |
|---|---|---|
| 波三收班自归档 | `st-fclean3-20261012` 已不在面 | 波三 `30_wave3_archive_single_face_note.md`＋`worktree_abort.jsonl` 20:12 行 `verdict=zero_loss reason=lane-archive 完成`；`git worktree list` 与 `.aidrafts/` 均查无 |
| 令卡点名的第二棵**本就不在面** | `deadcure2` 面（真名 `st-deadcure2-20261009`，令卡写作 `…20260909`）| 目录不存在、`.git/worktrees/` 无管理件、`worktree_abort.jsonl` 全文 317 行对 `deadcure2` **零命中** ⇒ 该树是被**在册归档通道之外**的路径移除的（簿记缺口，见 §5-乙）。⚑ **分支仍活**：`session/st-deadcure2-20261009`=`fcfc8e0bc6`，`dev..branch` ahead=**2**（末提交 10-09 21:45 "Merge branch 'dev' into session/…"＋`6065df5fec` "Owner 直接指令"入口说明书回灌"）⇒ 无字节损失，W-8 归并未竟的素材完好；本班按令**不动** |
| 波三之后新开工的车道 | `st-cband-20261012`、`st-minedig-20261012`、`st-gpux3-20261012` | 决策表 `shard=ok`＋心跳 8.2s＋目录静默 0.009-0.739d；`st-gpux3` 的 `.aidrafts` 面 21:1x 才出现（本班 21:16 首扫列到 18 棵，令卡 20:5x 写就） |
| 本班自身 | `st-fclean4-20261012` | `session_worktree_start` 21:0x 产物，排除于处置集 |

⇒ **可处置全集＝18 − 本班自身 1 − 在飞 5 − 令卡排除 1（mineloop）＝ 11 棵**（deadcure2 不在面，故令卡的"两棵排除"实测只有一棵可排除）。

## 2. 逐棵决策表（判型＝在册 RB-4 V 判型原语；活性＝五源）

判型尺（`scripts/session_worktree.py:908-940` `_classify_archive_lane`，本班按 importlib **仅导入**跑探针，零 registry 写）：
`ahead`（`rev-list --count dev..branch`）＋`cherry 全等`＋`status --porcelain` 三查 ⇒ `zero_loss`／`superseded_shell`／`needs_rescue`／`ahead_only`。
活性五源＝①分片心跳年龄 ②进程表命中（`proc_list.json` 21:1x，29 支 python）③目录静默 ④dev 上最后一次提及该 sid 的提交时刻 ⑤队列四态命中数。

| sid | 判型 | ahead | 脏/未跟踪 | 心跳 | 进程 | 目录静默 | dev 末次提及 | **本班裁定** |
|---|---|---|---|---|---|---|---|---|
| st-backfix-patrol-20261011 | zero_loss | 0 | 0/0 | 无分片 | 0 | 1.745d | 10-11 14:33 | **退场** |
| st-backfix3-20261011 | zero_loss | 0 | 0/0 | 9.5s | 1（daemon） | 0.023d | **10-12 21:20** | **态④ 在飞** |
| st-cband-20261012 | needs_rescue | 0 | 19/0 | 8.2s | 1 | 0.739d | **10-12 21:09** | **态④ 在飞** |
| st-deadcure3-20261010 | zero_loss | 0 | 0/0 | 无分片 | 0 | 2.148d | 10-12 00:12 | **退场** |
| st-deadcure3b-chief-20261011 | zero_loss | 0 | 0/0 | 8.2s | 1 | 0.026d | **10-12 21:04** | **态④ 在飞** |
| st-dexp-20261009 | needs_rescue | 0 | 4/4 | 分片损坏 | 0 | 2.7d | 10-12 17:23（波三移交单带出） | **闸① 后清脏再退场** |
| st-final4-20261010 | needs_rescue | 0 | 2/1 | 无分片 | 0 | 2.678d | 10-10 08:39 | **退场** |
| st-finalclean2-20261010 | zero_loss | 0 | 0/0 | 无分片 | 0 | 2.167d | 10-11 04:44 | **退场** |
| st-fullflow2-20261008 | zero_loss | 0 | 0/0 | 无分片 | 0 | 4.131d | 10-09 00:50 | **退场** |
| st-gpux3-20261012 | zero_loss | 0 | 0/0 | 8.2s | 1 | 0.009d | — | **态④ 在飞** |
| st-maint3-20261011 | zero_loss | 0 | 0/0 | 8.2s | 1 | 0.022d | 10-12 20:50 | **态④ 在飞** |
| st-minedig-20261012 | zero_loss | 0 | 0/0 | 8.2s | 2 | 0.022d | **10-12 21:20** | **态④ 在飞** |
| st-mineloop-20261010 | needs_rescue | **1** | 107/28 | 无分片 | 0 | 1.847d | 10-12 20:52 | **令卡排除不动**（矿考二班域；0080 复活未竟；`2087d4160b`＝其救援袋刚落地） |
| st-nightmine-20261010 | needs_rescue | 0 | 259/249 | 无分片 | 0 | 2.603d | 10-10 08:56 | **闸① 后清脏再退场** |
| st-nightmine-20261010b | needs_rescue | 0 | 51/17 | 无分片 | 0 | 2.529d | 10-10 08:56 | **闸① 后清脏再退场** |
| st-nightmine2-20261010 | zero_loss | 0 | 0/0 | 无分片 | 0 | 2.182d | 10-11 01:53 | **退场** |
| st-regsolo-20261010 | needs_rescue | 0 | 4/4 | 无分片 | 0 | 2.397d | 10-10 12:33 | **闸① 后清脏再退场**（唯 1 件受阻，见 §3-c） |
| st-fclean4-20261012 | zero_loss | 0 | 0/0 | 本班 | 1 | 0.011d | — | 本班自身，不动 |

**⇒ 退场集＝10 棵**（zero_loss 死车道 6 棵＋needs_rescue 死车道 4 棵；`st-dexp` 计入后者），
在飞 5 棵（backfix3/cband/deadcure3b-chief/gpux3/maint3/minedig ＝ **6 棵**，其中 minedig 与 maint3 均在 20:5x-21:2x 有 dev 落地）＋令卡排除 1 棵＋自身 1 棵。
⚑ **与令卡的差在分母**：令卡按"十六棵全退（除 2）"书写；实测有 **6 棵的主人正在提交**（minedig 21:20:28、backfix3 21:20:54、deadcure3b 21:04:42、cband 21:09:13、maint3 20:50:41、gpux3 21:13），令卡纪律条"在飞班资产禁碰"优先于菜单字母，故本班**只退 10 棵**并把 6 棵的当窗证据留在此表。

## 3. 闸① 清点：非缓存独有字节 318 件 / 169.4 MB（全集零抽样）

尺 β 产物（`out/c2_orphan_items.jsonl`＋`out/c1_unique_items.jsonl`，本班复跑）分层：

| 层 | 件数 | 字节 | 备注 |
|---|---:|---:|---|
| derived_cache（`.pyc`/`__pycache__`/`.ruff_cache`） | 3,081 | — | 可再生，零取证价值 |
| lane_local_runtime（`<lane>/.runtime/**`） | 1,800 | — | 车道本地台账，波三口径"只登记" |
| **非缓存业务件合计** | **318** | **169,400,774** | 逐件表 `out/m2_irreplaceable_manifest.jsonl` |
| └ docs_asset | 279 | 66,807,227＋ | **252 件/66.8 MB 属 `st-cband`（在飞态④，不动）** |
| └ code_or_config | 17 | 93,698,329 | 10 件/93.7 MB 亦属 `st-cband` |
| └ data_asset / secret_like / other | 13/4/5 | — | 多为波三已存证件 |

- **a) 波三存证面覆盖率实测**：318 件中 **24 件**已在 `.runtime/quarantine/fclean3_safety/aidrafts_irreplaceable/MANIFEST.jsonl` 登记（mineloop 12＋regsolo 12），与波三 `26_` §一"25 件按实质分流"一致。
- **b) 已在 dev 的件**：`already_in_dev_equal=0` **是口径必然**（尺 β 只输出 C1_unique/C2_orphan，二者定义即"与 dev 字节不等/查无"），不是"波三六件没落"的反证。波三落地的 5 件（dexp 05 交接单＋regsolo t1..t4）本班按**路径存在性**单独核：`git ls-tree dev` 命中 5/5 ⇒ 闸① 那 5 件已闭。
- **c) 唯一受阻件＝`st-regsolo-20261010 docs/_working/regsolo_campaign/99_delivery.md`**：波三以 `REFERENCE-INTEGRITY [ARCH-REFERENCE]` 实测判"门拦得对"（`ARCH-383` 在册尾号止于 382、PG 无 architecture_issues 表）后**主动排除出袋**。本班复核：该件 `not_in_dev=1`、正本在波三存证面（sha 在 MANIFEST）⇒ 字节不会因退场而灭失；落册须属主补登或改写，**本班不自造注册表条目、不改他班案卷正文**（波三在册教训）。登记为呈批件（见 `23_` §待裁）。
- **d) 死车道脏面（退场前必存证）**：nightmine 259 脏/249 未跟踪（非缓存 docs 15 件＋code 1 件，其"dev 有同名而字节异"形态＝**陈旧快照**，波三已判"取证价值＝历史版本，别当必须救，但要留 sha 指纹"）；nightmineb 51/17；dexp 4/4；final4 2/1；regsolo 4/4。本班处置＝走在册 lane-archive 的 ①patch 存证（`_generate_retire_patch_evidence`，fail-closed）＋ ②未跟踪 rescue，**外加**本班把非缓存独有件复制到非 TTL 安全面 `.runtime/quarantine/fclean4_safety/`（在册 rescue 落点 `.runtime/tmp/rescue/` 受 24h TTL 管，不可再生件不该寄存在会被清的面上）。

## 4. 通道选择（令卡字面 vs 在册 SOP，本班按实质）

- 令卡写"→ `git worktree remove`（禁裸 rm）→ `branch -d`"。
- 在册 SOP `docs/01_policies_and_standards/sop/ops_sop/worktree_cleanup_policy.md` §1 表末行与 §5 第 1 条：**禁止直接调用 `git worktree remove` 清他人 worktree**，一律走四证流程；§4 表把四证自动化挂在 `session_worktree.py` 的 `abort`/`archive` 上。
- ⇒ 本班按 **SOP ∩ 令卡实质**＝走在册 `scripts/session_worktree.py archive`（RB-4 车道生命周期治本，`:723-728` 流程注释）：其内部第 ③ 步就是 `git worktree remove --force --force`＋`prune`＋进程外核实，第 ① 步是 fail-closed patch 存证，第 ② 步是未跟踪 rescue，第 ⑤ 步是 `branch -d` 且**真 ahead 禁 `-D` 落白名单台账**（`_record_ahead_branch`→`.runtime/quarantine/ahead_branches.log`）。
  选 `archive` 不选 `abort`：`abort` 用 `branch -D`（`:694` 强删），`archive` 用 `-d`＋ahead 白名单——令卡要的正是后者语义。
- **死判副作用前置证明（动手前实测，非事后解释）**：`archive` 的死判 `:856` 调 mutating `list_active()`，其写面＝`_salvage_takeover_ledger`（判死即生成接管条目）＋超 900s 宽限分片物理收割（`session_concurrency.py:1546-1560`）。
  本班 21:35:16 实测在册 13 片：心跳年龄 **6.8-29.9s**，唯一较大者 `st-gpuwo-20261011`=687.9s 且其 pid 30476 在进程表**活着**；**无任何一片过 TTL(3600s)** ⇒ `expired=[]` ⇒ 接管台账写入与收割分支**均不触发**。
  ⇒ 结论：本班用在册通道退场，对他班**零接管写入、零收割**（每批执行前复测此表，见回执）。

## 5. 本班挖到的两处在册簿记缺口（登记呈批，本班不代修）

- **甲）主区战役账册挂着"删除波三第十四节"的暂存回退弹**（实测 21:4x）：`docs/_working/finalclean2_campaign/00_ledger.md` 状态 `MM`；
  `HEAD`＝628 行/18 节，`INDEX`＝616 行/17 节，`git diff --cached` 的删除集**恰为第十四节整段 12 行**（波三·通宵执行与晨间裁定包）；`DISK`＝620 行＝INDEX＋4 行外来批注（`【05:1x 已结案】` 等，属他班在途）。
  后果：任何会话从主区 index 直提该册，波三第十四节即**静默蒸发**（同型事故在册：热注册表被外来非 CAS 写蒸发、CAS 重放整树回退）。
  本班处置＝**不碰主区字节**（不 reset、不代提他班 4 行批注），改在**本车道以 `git show dev:` 全等基线纯追加**波四节（落地面删除行断言见回执）；本条与那 4 行原文一并呈维护三班（其热册治理簇在册）。
- **乙）`deadcure2` 树消失但零在册审计行**：`worktree_abort.jsonl` 317 行对该 sid **零命中**，`.runtime/quarantine/ahead_branches.log`（5 行）亦无其条目，而它的分支实测 ahead=2 ⇒
  该树是经**四证流程之外**的路径移除的（真 ahead 未落白名单、无 retire patch）。字节无损（分支 ref 完好），但"真 ahead 车道必须有白名单行"这条在册判据在它身上是**空的**。
  ⇒ 本班按 SOP 补一条登记（回执 §补账），并把它列为"退场必走在册通道"的实证理由之一。

## 6. 残余与未覆盖面（如实报）

- 四态尺聚合数受参照点漂移影响（§0），**逐件结论以 sha 实测为准**；本班未对 3,081 件派生缓存逐件求 sha（无需：可再生判据＝路径形态）。
- `st-cband` 的 169 MB 非缓存独有面（252 docs＋10 code）**未逐件定性**——它是态④在飞车道，本班无权限也无必要动；退场窗口留给它自己的班。
- 12 支面级通配读者的产物校验：已由只读车道实测"无 git 跟踪产物需同批再生"（`lanes/lane_face_readers.md`：真尺＝枚举面，10 模块/12 枚举点；面派生输出 `three_piece_infra/visibility_board/*` 与接管台账均**不在 git 跟踪面**），本班退场后仍复跑其枚举点计数留证（见回执）。
- `.git/worktrees/` 管理面体量与 1 枚 STALE（`pool-20260919202729-c433`：locked、HEAD 全零、目录已不在）未处置——不在本班集合（`.aidrafts_pool` 属池面），列维护三班。
- 本班未取"分支面当窗写活动"的直接证明（波三 §3.1 同款 E0 缺口）；本班以"无分片＋进程表零非 daemon 命中＋目录静默>1.7d＋dev 末次提及>10h"四源替代，**不称铁证**。
