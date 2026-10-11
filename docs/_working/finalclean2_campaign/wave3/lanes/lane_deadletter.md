---
ttl: task_bound
completes_when: "dead/ 与 done/ 两面全集逐袋元数据分账完成（袋 100% 遍历）、only-copy 面按字节级判据机械核定、四分衔接清单成表；零删除/零改队列状态"
owner_lane: st-fclean3-20261012/lane_deadletter
read_only: true
census_clock_pinned: "2026-10-11T23:56:00+08:00"
dev_head_at_census: b9a0bb9facccc9aa8eebef24934cc16148332156
---

# L 车道案卷：提交队列 dead/ 与 done/ 分账（只读，出案卷不出裁定）

> **纪律声明**：本班零删除、零 `git add`/`git commit`、零队列状态变更（未执行 requeue/drain/cleanup/acquire/release）。
> `blobs/` 大内容**未读一字节**（仅 `stat` 取尺寸）；所有判据为字节级机械判据，逐条配「复算命令＋实测值」。
> **普查时钟钉死** = `2026-10-11T23:56:00+08:00`（年龄桶基准）。队列在活：本会话期间 done 袋由 732→733→735 递增、dead 由 1451→1452、
> `dead/_recurrence_state.json` 由 390,915→**469,395 B**（**皆 belt/daemon 并发写入，本班零写**；复算：`python -c "import os;Q=r'D:/ZephyrAlpha/.runtime/commit_queue';print([len([f for f in os.listdir(os.path.join(Q,d)) if f.startswith('q-') and f.endswith('.json')]) for d in ('dead','done')])"`）。
> 本卷全部计数按普查时点出表，复用者请以同一时点为准。

## 0. 实测底数 vs 工令账面（漂移表）

| 面 | 工令/在册账面 | 本班实测 | 漂移 | 复算命令（§6 编号） |
|----|---|---|---|---|
| `dead/` 袋 | 1453 项；§1 另记 dead_n=1449@22:40 | **1451 个 `q-*.json` 袋**（目录条目 1454，非袋件 3） | −2 / +2（两个账面自相矛盾） | C1 |
| `dead/` 袋面字节 | 43 MB | **40,278,302 B（38.4 MB）** | −4.6 MB | C1 |
| `done/` 袋 | 731 项 / 6.5 MB | **732 项（普查时点）→ 734 行核验表（收尾时点）/ 4,986,693 B（4.8 MB）** | +1～+3 项，−1.7 MB | C1/C7 |
| `blobs/` | 26,276 项 / 5.0 GB | **26,289 项 / 4,998.9 MB** | +13 项（A 类复活完成前零触碰，本班仅 stat） | C1 |
| dead 袋内文件条目 | — | **110,240 条 files 条目／去重 14,440 组 (path, blob_sha256)** | 新增口径 | C2 |

**在册账面被实测推翻的两条**（见 §5 详表）：①"A 类 257 件复活进行中"→ 实测 A 类批表 = **93 袋／63 簇**，且 **93/93 仍在 dead/ 未离开一袋**（复活零落地）；②"呈批态约 1209（only-copy 1089）"→ 实测 only-copy 面 **1425 袋**（口径 A）。

### 0.1 dead 族谱的"归档面"全集（清淤史即证据链，不可漏算）

| 目录 | 条目 | `q-*.json` 袋 | 袋 json 字节 | 目录 | 条目 | 袋 | 袋 json 字节 |
|---|---|---|---|---|---|---|---|
| dead_archive_20261004 | 599 | **598** | 3,879,417 | dead_archive_20261009_deadcure2 | 103 | **101** | 794,836 |
| dead_archive_20261006 | 460 | **459** | 5,722,217 | dead_archive_20261010_deadcure3 | 16 | **15** | 60,870 |
| dead_archive_20261007 | 214 | **213** | 2,709,877 | dead_purged_20260920 | 113 | **113** | 961,191 |
| dead_archive_20261009_deadcure | 394 | **391** | 3,311,297 | dead_archive（裸名） | 1 | 0 | 0 |
| blobs_archive | 44 | 0（皆 blob 实体） | 14.7 MB | — | — | — | — |

> 归档面 json 袋合计 = **1,890 袋 / 17,439,705 B**（复算：`L_dead_bags_fp.csv` 按 `face` 以 `arch:` 前缀 group-by）。
> dead 现盘 1,451 袋 **< 归档面 1,890 袋**：即"死信总量"已被清淤搬走过一轮以上，`dead/` 只是最新一层的窗口。

## 1. dead/ 逐袋分账（1451/1451 = 100% 遍历，零抽样）

### 1.0 判据口径（先立尺，后报数）

袋内 `files[].blob_sha256` 与 git 对象库对拍（**字节级**，非 reason 字段猜测）：

| 态 | 定义 | 含义 |
|---|---|---|
| `in_head` | 袋字节 == `dev` HEAD 该 path 现值（sha256 等值） | **零信息量**（内容已在工作面） |
| `in_hist` | 袋字节 == `dev` 历史上某提交的该 path 版本 | git 已存副本，非唯一 |
| `only_copy` | 袋字节不在 dev HEAD **也不在 dev 任何历史提交**，且 `blobs/<sha256>` 物理在场 | **唯一副本**＝Owner 门位面（归档=物理销毁唯一副本） |
| `lost` | 袋字节不在 dev 任何历史 **且 blobs/ 已被清** | 内容不可复原，袋=存在性证据 |

复算：`git rev-list --objects dev`（515,511 行全集）+ `git cat-file --batch` 逐对象 sha256 对拍（pass1 HEAD 7,168 对象/132 MB；pass2 历史 22,987 对象/**5.62 GB**），脚本 `.runtime/tmp/st-fclean3-20261012/L_git_crosscheck.py`，逐对结果 `out/L_blob_state.csv`（7,314 命中对／16,286 候选对）。

**口径对照（诚实披露）**：前班用 `lines_only_in_bag>0` vs 现行 HEAD（行级、只看 HEAD）；本班额外把 dev **全历史** blob 纳入排除集，故本班 only-copy 判定更**保守**（更不容易被判成唯一副本）；即便如此实测仍为 1425 袋 > 账面 1089。两套尺的差异全部来自"dead 面在两班之间长大 + 新增袋以 ghost_session 风暴为主"。

### 1.1 年龄桶（袋数／袋 json 字节／袋内 blob 引用字节[袋内去重、袋间可重叠]）

| 桶 | 袋 | bag_json_bytes | 袋内 blob 引用字节（重叠和） |
|---|---|---|---|
| ≤3d | 202 | 1,553,454 | 400,387,454 |
| 3–7d | **757** | **32,633,566** | **1,753,579,523**（ghost_session＋COMMIT_FAILED 风暴主体） |
| 7–14d | 352 | 4,983,562 | 814,424,087 |
| >14d | 140 | 1,107,720 | 354,688,263 |
| 计 | **1,451** | **40,278,302** | **3,323,079,327**（引用口径，非 dedup） |

> dedup 后的**真字节账**（(path,sha) 去重，全集 14,440 对／可测 1,245,067,788 B）：
> `in_head` 4,072 对 49,983,020 B（**4.01%**）｜`in_hist` 703 对 90,240,857 B（**7.25%**）｜
> **`only_copy` 8,683 对 1,104,843,911 B（88.74%）**｜`lost` 982 对（字节不可测，blob 已清）。

### 1.2 死因族谱 top14（218 个不同签名，全集无抽样）

| 签名 | 袋 | only_copy 字节 | 涉及会话数 | 内容指纹数 | 年龄桶 |
|---|---|---|---|---|---|
| item:网关落盘失败（COMMIT_FAILED） | **309** | 370,124,228 | 57 | 237 | 3-7d/7-14d/le3d |
| other:landing 异常 | **237** | 307,253,128 | 28 | 212 | 同上 |
| env:ghost_session | **219** | 366,340,699 | 34 | 150 | 同上 |
| item:cascade_stale | 73 | 208,582,699 | 12 | 70 | 同上 |
| gate:CREATE-GUARD | 36 | 35,048,864 | 14 | 29 | 7-14d/gt14d |
| head:landing 异常 | 30 | 136,399,810 | 13 | 22 | 7-14d/gt14d |
| item:landing 异常 | 29 | 131,568,391 | 16 | 24 | 3-7d/7-14d/le3d |
| gate:TRANSLATION-COVERAGE | 28 | 86,001,958 | 11 | 28 | 7-14d/gt14d |
| item:CREATE-GUARD | 24 | 100,415,033 | 10 | 20 | 3-7d/le3d |
| item:DOC-HEADER-SUITE | 23 | 3,642,586 | 10 | 21 | 3-7d/le3d |
| item:GATE-PRECOMMIT-RUN | 19 | 5,261,130 | 10 | 16 | 3-7d/le3d |
| item:TAKEOVER-PENDING | 18 | 48,956,267 | 14 | 17 | 3-7d/le3d |
| gate:GATE-VOCAB | 15 | 3,005,876 | 5 | 13 | 7-14d/gt14d |
| gate:GATE-PRECOMMIT-RUN | 12 | 32,892,919 | 9 | 12 | 7-14d/gt14d |

（全 218 行表 = `out/L_dead_by_sig.csv`；会话维＝`L_dead_by_session.csv`，171 个会话；属主维＝`L_dead_by_owner.csv`）

**同一根因的连坐重复（合并候选）——三层实测**：

1. **签名碎片化**（口径不统一造成的假多样性）：`landing 异常` 一因三名（other/item/head = 237+29+30 = **296 袋**）；`CREATE-GUARD` 二名（36+24=**60**）；`GATE-PRECOMMIT-RUN` 二名（19+12=**31**，全 31 袋皆 only_copy，36.4 MB）。合并到根因单可让族谱从 218 签名塌缩到接近 `_root_cause/` 的 **35 张工单**。
2. **内容级完全重复**（真连坐）：同一 `(path,blob)` 集合指纹（content_fp）在 dead 面出现 >1 次者 **340 组／880 袋**，即 **540 袋是同批字段的重复再死**，重复袋自身 json **26,113,505 B**、引用 blob **1,747,286,523 B**。
3. **重投链**（袋内 `requeued_to` 指向另一 dead 袋）：**667 条**（另有 188 条指向面外）。⇒ top3 签名 765 袋 ≈ ①+②+③ 的主体，**"一因一单 + 链首单袋"可把 1451 压到约 700 量级**（口径：540 重复袋 + 链中袋去重，不动唯一副本字节）。

### 1.3 根因工单与复发熔断台账（非袋件，实测）

- `dead/_root_cause/` = **35 张**工单（`env_ghost_session`／`item_GATE-PRECOMMIT-RUN`／`item_landing_异常_*` 4 张哈希分身／2 张"快照基底与 dev 共同祖先冲突"／2 张注册表册面），字段 `signature/first_dead_at/owner_sessions/sample_qid/root_cause_required`（无 count 字段 ⇒ 计数只在 `_recurrence_state.json`）。
- `dead/_recurrence_state.json`（390,915 B）= `signatures` **294** 键、`count` 合计 **2,269**（> 现盘 1451 袋，含已归档/已重投的历史死亡计数）；`session_lanes` 另册。top：COMMIT_FAILED 673／ghost_session 430／other:landing 异常 333／cascade_stale 132／item:landing 异常 79／TAKEOVER-PENDING 57／CLAIM_REQUIRED 45／CREATE-GUARD 40／GATE-PRECOMMIT-RUN 32／DOC-HEADER-SUITE 28。
- 袋上带 `recurrence_fused=true` 者 **1,014 袋**（69.9%），带 `dead_signature/prescription/first_dead_at` 者各 1,014 袋（新尺袋），旧袋（2026-09 批 201 袋）**无 family/signature 字段**，只能按 reason_head 反推 ⇒ 口径断层须在读档时注意。

### 1.4 逐袋四态核定结果（袋级）

| 分类 | 袋 | bag_json 字节 | 袋内唯一副本字节（重叠和） | path 在 dev 面存在性拆分 |
|---|---|---|---|---|
| `only_copy` | **1,382** | 39,330,414 | 2,346,459,832 | 全缺 33／部分缺 1,071／全存在 278 |
| `only_copy+lost` | **43** | 387,404 | 268,344,466 | 部分缺 43 |
| `in_git_history` | 16 | 88,834 | 0 | 全存在 11／部分缺 5 |
| `lost_content` | 2 | 418,632 | 0 | 部分缺 2 |
| `zero_information` | **8** | 53,018 | 0 | 全存在 8 |
| 计 | 1,451 | 40,278,302 | 2,614,804,298 | — |

> 呈批态（Owner 门位）= `only_copy` + `only_copy+lost` = **1,425 袋（98.2%）**。
> 条目级复核：110,240 条目中 `in_head` 51,858（47.0%）／`in_hist` 3,764／`only_copy` 52,443／`lost` 2,175。
>  ⇒ **"半数字节已在 HEAD 现值"与"98% 袋含唯一副本"并存**：大袋里多数文件已落地、少数文件才是唯一副本 ⇒ **禁按袋整批处置，必须按 (path,blob) 条目粒度呈批**（本案卷的 `L_handoff_deadcure4.csv` 已给条目级 path_sample）。
> 明细表：`out/L_bag_classification.csv`（1,451+732 行，含 `only_copy_bytes`/`e_path_absent_at_dev`/`content_fp`/`sig`/`age_bucket`）。

## 2. done/ 分账（732 袋普查点／734 行核验点，100% 遍历）

### 2.1 年龄与时间跨度

| 桶 | 袋 | bag_json 字节 |
|---|---|---|
| ≤3d | 345 | 2,163,915 |
| 3–7d | 382 | 2,809,526 |
| 7–14d | 5 | 13,252 |
| >14d | **0** | 0 |

⇒ done 面**没有任何 >14d 的袋**（最老 done 袋 `created_at` 落在 3–7d 桶内）；即 done 留档面本身已被例行清转过，留存深度天然 ≤7d。

### 2.2 落地真实性（机械对拍，非抽样）

袋内权威字段：`landed_at` + `landed_id`（key census：733/733 袋皆有；56 袋另有 `attempts`/`last_failure`）。

| 核验态 | 袋 | 说明 |
|---|---|---|
| landed_id = 真提交且在 dev 可达 | **645** | `git merge-base` 级实测（`git rev-list dev` 全集 21,191 提交比对） |
| landed_id = `noop@<sha>` 占位（无改动落盘，内容已在目标提交） | **88** | 88/88 的内嵌 sha **全部可解析为真提交**（`git cat-file -e <sha>^{commit}`，零失败） |
| landed_id 不可解析（非 noop 前缀） | **1** | `q-20261007-st-vm12final-20261007-laneC-0002`，landed_id=`3f69cc2135ad89b4374b87df3d3e3b7406b962fc`，1 条目 `config/data_supply_chain_map.yaml`（169,094 B，blob 在场），该字节对拍结果=**in_hist**（内容确在 dev 历史）⇒ 判定为 **landed_id 漂移/重放换 sha**，非内容丢失；点名待四班/他班核 |
| 条目级：落地提交树内含该 path | 6,067 命中／3,684 未命中 | 未命中主体是 `st-tests-chief-20261004` 大袋（单袋 470 条目），与"落地时重写内容/路径"一致 |

⇒ **done 面无伪落地**（646/646 真提交可达 + 88 noop + 1 sha 漂移待核）。

### 2.3 零信息量字节占比（实测）

done 面去重 10,530 组 (path,blob)／可测字节 652,864,922 B：

| 态 | 对 | 字节 | 字节占比 |
|---|---|---|---|
| `in_head`（**完全等于 HEAD 现值＝零信息量**） | 5,286（50.2% 对数） | 96,012,425 | **14.71%** |
| `in_hist`（git 已存，非唯一） | 716 | 230,459,708 | 35.30% |
| `only_copy`（不在 dev 任何历史，blob 在场） | 362 | 326,392,789 | **49.99%** |
| `lost`（blob 已清，字节不可测） | 4,166 | 0 | 0%（条目 4,696） |

袋级：`zero_information` 223／`in_git_history` 265／`only_copy` 224／`lost_content` 17／`only_copy+lost` 3。
`only_copy` 的 224 袋里 **220 袋的所有 path 都存在于 dev HEAD** ⇒ 属"入袋快照 vs 落地内容"的过期版本（enqueue 时字节 ≠ 提交时字节），**不是**需要 Owner 门位的唯一业务副本；仅 1 袋 path 全缺 + 3 袋部分缺需逐条看。

### 2.4 留档期限建议的**实测依据**（禁裸删）

1. done 袋是 **唯一携带 `landed_id` 的审计面**：733/733 袋 100% 有落地指针，其中 14.71% 字节的"哪一次提交落的"关系**只能从袋里读出**（HEAD 无此映射）。删袋 = 删落地溯源链。
2. 4,696 个条目的 `blobs/` 副本已被清（byte 不可测）：袋是这些条目**存在过的唯一登记**。
3. 88 个 `noop@` 袋 = "该提交已含此内容"的**幂等证明**，删后无法重证。
4. 1 袋 landed_id 漂移（§2.2）正待核——此时删袋会毁掉唯一可比对的原始指针。
5. 零信息量面确实可观（50.2% 的 (path,blob) 对 == HEAD 现值），**可压缩的是袋内 files 条目而非袋本身**：建议方向=「按条目瘦袋（删 `in_head` 条目的 `blob_ref` 依赖，保留 qid/session/landed_id 三元组）」而非删袋；本班不出裁定，仅登记依据。

## 3. 与死信四班（st-deadcure4）的衔接清单

### 3.1 四班在途状态（实测，非在册转述）

- **四班零在册痕迹**：`git worktree list` 只到 `st-deadcure3-20261010`／`st-deadcure3b-chief-20261011`；`.runtime/heartbeat`、`.runtime/locks` 无 `deadcure4` 任何 pid；`.runtime/tmp/` 无 `st-deadcure4*` 工棚目录。⇒ **本班向"无在途班长"交接**（最小集仍按有班长可认领的形态给）。
- **A 类批表真身**（唯一在册复活工单）= `D:/ZephyrAlpha/.runtime/tmp/st-deadcure3-20261010/common/shards3/shard3_{0,1}.json`，`face="A_revive_safe"`，**38+25=63 簇／64+29=93 袋**，family 分区纯度 OK（无族跨片），自带配方：属主三态现测→unique_lines 复核→车道内写件→`PYTHONNOUSERSITE=1` pytest 绿且断言 `zephyr.__file__` 落本道→`git_commit.py --enqueue --base-head <现行 dev tip>`→`git log -1 --name-only`。
- **93 袋 100% 仍在 dead/**（0 在 done、0 在归档面）⇒ 工令"A 类 257 件复活进行中"**实测不成立**：件数是 93（257 见 `deadcure_campaign2/01_phase0_ledger.md:576`，上下文是"把 257 件 A 类的可解析性判据换成 AST"＝**校准项条数**，非复活袋数），且**复活落地数 = 0**。
- 前班自陈（同册 §19/§20）：呈批 1209（1201 only-copy + 6 guard 拒收 + 2 有效删除请求）、`dead<200` 本期不可达、地板 ≈1289、差额 1089 皆 only-copy。⇒ 与本班 1425 实测**同向不同量**（差 +216 袋，主因 ghost_session 与 10-08 之后的新袋）。

### 3.2 dead 四分表（互斥，并集=1451 全覆盖）

| 桶 | 袋 | bag_json 字节 | 唯一副本字节（袋内去重和） | 本班动作 |
|---|---|---|---|---|
| ① 四班已认领 | **0** | 0 | 0 | 无认领痕迹（§3.1 实测） |
| ② A 类批表内（shard3 93 袋） | **93** | 876,107 | 6,022,153 | **不动**，配方留给四班 |
| ③ 四班未覆盖·AI 可为（非 only-copy：in_git_history/lost_content/zero_information） | **21** | 535,656 | 0 | **不动**（requeue/archive 须他班或 Owner 授权） |
| ④ 呈批态·Owner 门位（only_copy ±lost，扣除②） | **1,337** | 38,866,539 | 2,608,782,145（dedup 后 1.10 GB） | **登记呈批，本班一律不动** |
| 合计 | **1,451** | 40,278,302 | — | 覆盖自检 93+21+1337=1451 ✓ |

**交接最小集**（每行 = sid＋qid＋死因＋建议动作＋不动声明）：
`D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/L_handoff_deadcure4.csv` — **1,451 行**（②③④三桶全量，含 `age_days`/`only_copy_bytes`/`content_fp`/`path_sample`/`suggested_action`）。
班长开工只需三张表：`L_handoff_deadcure4.csv`（分桶）、`L_dead_reason_family_top.csv`（根因合并）、`L_bag_classification.csv`（条目级字节账）。

**本班明确不动清单**：`blobs/`（零读零删）／dead 面所有袋（含 21 袋 AI 可为面）／done 面所有袋／`_recurrence_state.json`／`_root_cause/` 35 单／9 个 `dead_archive_*`+`blobs_archive` 目录／`pending`(7)+`processing`(1) 在途袋／`worktree`/`worktrees` serializer 工作区／任何判据阈值与门禁代码。

## 4. 净零线索：同义证据区重复登记（实测＋合并方案）

1. **同一内容在 dead 与归档面双登记**：content_fp 交叉命中 **52 组**，涉及 **dead 现盘 68 袋**（其完全相同的内容已存在于 `dead_archive_20261004/06/07/09_deadcure/20261010_deadcure3`/`dead_purged_20260920` 之一）。⇒ 这 68 袋是"搬走又长回来"的双份证据，合并方案=**归档面为唯一存证层，dead 面以指针引用**（`archived_qid` 字段），不新增文件。复算：`L_dead_bags_fp.csv` 按 `content_fp` group-by `face`。
2. **qid 跨面双登记**：3 个 qid 同时出现在两个面（0 个跨 dead↔归档；系 done↔arch 边界），量级小，登记即可。
3. **一因多册**（同义证据区最强形态）：`landing 异常` 一根因在 `_recurrence_state.json`/`_root_cause/`/袋 `dead_reason` 三处各自命名（294 个 signature 键 vs 35 张工单 vs 218 个袋签名），且 `_root_cause/` 内已出现 `item_landing_异常` + `_0722f7e7/_48cb9a9a/_5eb92f7a/_81f34f77` **4 张哈希分身**＋`other_landing_异常`＋`env_landing_异常` **7 册同义**。合并方案=同键集合差归一为 `landing_anomaly` 单工单＋其下 qid 清单（生成器产出，手工不维护）。
4. **归档目录命名漂移**：`dead_archive_YYYYMMDD` vs `dead_archive_YYYYMMDD_deadcure[N]` vs `dead_purged_YYYYMMDD` vs `blobs_archive` 四套同族命名 ⇒ 收敛为单一前缀＋字段化 campaign 标记。
5. **案卷面自身重复**：`docs/_working/` 下 dead 主题册共 8 个目录（`deadcure_campaign`／`deadcure_campaign2`／`deadletter_cure_20261003`／`audit_cure_night`／`commitmap_cure`／`qcure_campaign`／`tests_cure_campaign`／`2026-09-11-commit-queue-dead-zero-closure.md`＋`2026-10-01-commit-chain-cure-report.md`）。本案卷**不新建 campaign 目录**，只挂 `finalclean2_campaign/wave3/lanes/`，即净零自证。

## 5. 在册知识复核（三数全不可考／被实测推翻）

| 在册论断 | 出处核查 | 本班实测现值 |
|---|---|---|
| "844 只死信族谱" | `grep -rn -E '\b844\b' docs/_working/{deadcure_campaign,deadcure_campaign2,finalclean2_campaign}/*.md` → **无命中**；族谱数据真身=`.runtime/tmp/st-deadcure*/lineage.json`（三版：5,487／6,380／**6,396 paths**，键=`dev`/`any`，是 path 维不是袋维） | dead 现盘 **1,451 袋／171 会话／218 签名／14,440 组 (path,blob)** |
| "处置态须内容级（可销 33 非 537）" | 同批 grep `537`／`可销` → **无命中**（仅 `deadcure_campaign/01_ledger.md:144` 无关文本） | 内容级可销面实测：dead 非 only-copy 袋仅 **26 袋**（16 in_hist＋8 zero_info＋2 lost）；33 之近数=`only_copy` 中"全 path 缺于 dev"33 袋 |
| "修 GATE-PRECOMMIT-RUN 可消 222 袋" | 无命中；最接近=`deadcure_campaign/03_ticket_register.md:236`"死于 GATE-PRECOMMIT-RUN……**11 袋 2844 件**"（口径为件非袋） | 现盘 GATE-PRECOMMIT-RUN 相关 **31 袋**（item:19＋gate:12），36.4 MB 唯一副本，全 31 袋皆 only_copy ⇒ 修此门**一袋都不能"消"**，只能转呈批；"222" 无字节级支撑 |

## 6. 复算命令手册（只读，逐条可重跑）

```bash
# C1 底数（袋数/字节）
python -c "import os;Q=r'D:/ZephyrAlpha/.runtime/commit_queue';\
 [print(d,len([f for f in os.listdir(Q+'/'+d) if f.endswith('.json')]),\
 sum(os.path.getsize(Q+'/'+d+'/'+f) for f in os.listdir(Q+'/'+d) if os.path.isfile(Q+'/'+d+'/'+f)))\
 for d in ('dead','done','blobs')]"

# C2 全集逐袋元数据（1451+732+归档面，非抽样）
python .runtime/tmp/st-fclean3-20261012/L_dead_scan.py        # -> out/L_dead_bags_all.csv, out/L_dead_files_all.csv
python .runtime/tmp/st-fclean3-20261012/L_dead_agg.py         # -> out/L_dead_bags_fp.csv, L_dead_by_sig/session/owner/lane/family.csv, L_agg_summary.json

# C3 字节级 only-copy 判定（HEAD + 全 dev 历史 blob 对拍；pass2 需 ~5.6GB 读）
python .runtime/tmp/st-fclean3-20261012/L_git_crosscheck.py   # -> out/L_blob_state.csv（末尾 print 有笔误，CSV 已完整）
python .runtime/tmp/st-fclean3-20261012/L_classify.py         # -> out/L_bag_classification.csv

# C4 四分表 / 族谱 top / 净零 / 去重字节账 / 交接 CSV
python .runtime/tmp/st-fclean3-20261012/L_final2.py           # -> out/L_dead_reason_family_top.csv, out/L_handoff_deadcure4.csv

# C5 四班认领状态与 A 类批表
ls .runtime/heartbeat .runtime/locks | grep -i deadcure4      # 实测：无输出
git worktree list | grep -i deadcure                          # 实测：止于 deadcure3b
python -c "import json;[print(i,json.load(open(rf'D:/ZephyrAlpha/.runtime/tmp/st-deadcure3-20261010/common/shards3/shard3_{i}.json'))['clusters'],json.load(open(rf'D:/ZephyrAlpha/.runtime/tmp/st-deadcure3-20261010/common/shards3/shard3_{i}.json'))['bags']) for i in (0,1)]"

# C6 done 落地核验（真提交可达性 + noop 前缀 + 条目级树内命中）
python .runtime/tmp/st-fclean3-20261012/L_done_land.py        # -> out/L_done_landed_check.csv
git rev-list dev --format=%H | wc -l                          # 21191
git cat-file -e 3f69cc2135ad89b4374b87df3d3e3b7406b962fc^{commit} || echo ANOMALY   # §2.2 唯一漂移袋

# C7 单袋抽查（禁抽样当全集，此处仅示范读法）
python -c "import json;d=json.load(open(r'D:/ZephyrAlpha/.runtime/commit_queue/dead/q-20261011-st-mineloop-20261010-0075.json',encoding='utf-8'));print(list(d),d['dead_signature'],d['recurrence_count'])"
```

## 7. 完工申报与残余（零谎报）

- **已跑完全集**：dead 1451/1451、done 732/732（普查点）逐袋解析；9 个归档目录内 `q-*.json` 袋 **1,890/1,890** 载入 fp 表（总扫描行数 4,081 袋）；文件条目 dead 110,240＋done 11,593 全量入 `L_dead_files_all.csv`；**剩余枚数 = 0**。
- **申报未做（口径限制，非遗漏）**：① 归档面 1,890 袋**未做** only-copy 字节对拍（`L_blob_state.csv` 的候选集含它们，但四态分类只对 dead/done 出表）；② `blobs/` 内容零读，故 `lost` 条目（dead 982 对／done 4,166 对）的原始字节数不可报；③ 面外 `requeued_to` 目标（188 条）未逐个定位落地结果；④ done 面 1 个 landed_id 漂移袋只点名未追因（`st-vm12final-20261007-laneC`，属他班 owner 责任面）。
- **口径声明**：年龄桶基准=钉死的 `2026-10-11T23:56:00+08:00`；若复用请同时复用该钟，否则桶边界（3/7/14d）会漂移。

**产物表清单**（`.runtime/tmp/st-fclean3-20261012/out/`，本班前缀 `L_`）：
`L_dead_bags_all.csv`／`L_dead_bags_fp.csv`／`L_dead_files_all.csv`／`L_blob_state.csv`／`L_bag_classification.csv`／`L_dead_by_sig.csv`／`L_dead_by_session.csv`／`L_dead_by_owner.csv`／`L_dead_by_lane.csv`／`L_dead_by_family.csv`／`L_dead_reason_family_top.csv`／`L_done_by_session.csv`／`L_done_landed_check.csv`／`L_handoff_deadcure4.csv`／`L_agg_summary.json`／`L_git_crosscheck.log`。
