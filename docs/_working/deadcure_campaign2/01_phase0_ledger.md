---
ttl: task_bound
completes_when: 死信二期三段（家族内务/二次裁定/blobs 归档）全清且 cycle_check 连续两轮零问题
---
# 死信清偿二期 · Phase 0 家族内务执行账（生成器产出，禁手工维护）

- 会话 sid=`st-deadcure2-20261009`｜车道基线 HEAD=`89efc8202b`（开工现测，非记忆）
- 门态：Phase 1 门（`git cat-file -e HEAD:docs/_working/chiefc_campaign/99_delivery.md`）= **CLOSED**（开工至今）；Phase 2 门（dead/<200）= CLOSED
- 裁定纪律=《裁定路由政策 v2.0》D1 自裁 + adjudicator 署名 `st-deadcure2-20261009`

## 一、基线读数（现测，与指令口径对平情况）

| 项 | 指令口径 | 本期现测 | 判定 |
|---|---|---|---|
| dead/ 目录条目 | ≈1431 | 1431（其中 q-*.json 袋 1428，非袋 3=`_root_cause`/`_recurrence_state.json`/`archive_flashbiz_superseded_20260918`） | 对平；袋宇宙取 1428 |
| 在坑（继承一期处置面） | ≈1335 | **1335**（`freeze_universe.py` 按一期 action_plan 键集差现算） | 逐位吻合 |
| 一期后新增死袋 | 未给 | 93（chiefc 56／libfront 18／其余 19） | 新增分区面 |
| 一期归档 | 393 袋↔393 行 | 393 物理件↔393 manifest 行，manifest qid 与物理名 100% 对齐 | 对平（判据坑见 §四.3） |
| 队列 | 未给 | pending 12／processing 1／done 646 | 低于暂停投递阈值 |
| D 盘 | 停写线 <15G | 57G 可用 | 可写批 |

## 二、Phase 0a 工具面（.runtime/tmp/st-deadcure2-20261009/tools/，不入仓库）

**前提被实测证伪**：指令称"一期 .runtime/tmp 工具已被 TTL 回收，需重建"。实测一期 `tools/`（34 件）与 `common/` 完整在盘（mtime 10-09 17:19），未回收。故本期策略=**只读引擎复用 + 处置件重写**，不重复造轮：

| 工具 | 来源 | 二期差异（为何不能直接沿用） |
|---|---|---|
| `dead_catalog.py`／`lineage_index.py` | 一期原样复用 | 二者 `--out` 已参数化、纯只读，直接产本期 index/lineage |
| `freeze_universe.py` | 本期新写 | 一期无"继承面/新增面"桥接口径（1704→1335→终值 逐段对平的第一段） |
| `lane_triage.py` | 本期新写 | 接管条道脏件需**对 dev 现面**逐行比（一期无此判据） |
| `token_recon.py` | 本期新写 | 五面（HEAD/盘面/PG/pending 袋/rescue tag）条目级对账 + 字段级差分 |
| `token_publish.py`／`token_publish2.py` | 本期新写 | 账本追平+快照物化+**内存预演 render 伤害半径** |
| `deadcure2.py` | 本期新写 | 归档区改 `dead_archive_20261009_deadcure2`（一期归档区=史实禁改）；署名换本期 sid；新增 `verify` 子命令=归档后按当前 HEAD 逐件反查 |

## 三、Phase 0b 家族接管清理（指令点名的 2 枚 → 实测扩到全族 6 枚）

指令 §二 称"待清家族接管=st-deadcure-g1-chief 与 st-deadcure-restore-chief 两枚 open 条目锁着 token 热册"。现查纠正两处：①`--scan` 全量=**144 条 open**（指令口径 18 条只是单轮新建数），其中真带命中面（=能咬 commit）的仅 10 条；②锁热册的**不是**我家族两枚而是 1 条活会话条目（见 §七 9-1）。因我族其余 4 枚条道封的正是 Phase 1 复活要写的 docs/_working/ 与 tests/ 面，本 Phase 按同规程扩到**全族 6 枚**收口（家族内务，非代修）。

1. **保字节先行**（零写工作树）：`git stash create` → rescue tag 六枚（g1=ec92443c9e／restore=13790d51f0／g2=b1aed46f48／g3=ef0c23255d／g4=a546cd736d／promote=18e4cc8c97；st-deadcure-20261009 与 chief-20261009 tracked 面本就 clean 无需 tag）。
   ⚠ `git stash create --include-untracked` 实测**被忽略**（产出 commit 只有 2 个父，无未跟踪父）→ 未跟踪件另抓 75 枚（18+53+4）复制入二期 tmp 并 sha256 逐位对拍，且**全部 75 枚 sha 命中 `.runtime/commit_queue/blobs/<同值>`**（持久面，非我 tmp）。
2. **字节回读自证**：逐件 `git show rescue/<sid>:<path>` 与车道盘面 EOL 归一相比，六枚条道 100/100、69/69、75/75、1/1、4/4、12/12 **零失验**。
3. **内容级分诊**（`lane_triage.py`，判据=车道字节 × `git show dev:<path>` 行集，EOL 归一）：
   - g1 100 件：identical 57／dev 更新代 4／"超集"35／diff 4 → 有值 0
   - restore 70 tracked+4 未跟踪：identical 24／"超集"33／dev 更新代 4／diff 5／absent_in_dev 4 → 有值=3 枚 token（已消费）+2 枚转工单
   - g2 75 件：identical 73／diff 2 → 有值 0；g3 1 件=dev 更新代；g4 4 件=identical；promote 65 件：identical 24／"超集"33／dev 更新代 4／diff 4 → 有值 0
4. **判据自证（关键伪影，两批共 101 件）**：所谓"车道超集"逐条取行验明，其独有行=`doc_type: campaign_doc`／`doc_type: "census"`——正是 DOC-HEADER-SUITE [EXEMPT-ZONE-FM] 在 docs/_working 豁免区硬拦、一期已"只删该键正文逐字节不动"剥离后落地的**旧代**；按行计数会误判 101 件为待复活，复活即把违禁键重新引入。另 2 件（t0_ceiling_verdict／t0_conditional_e4_v3_verdict）多出行为一期自犯"双插 frontmatter"的错误版（一期台账 §五①在案并已按原袋复原），HEAD 侧才是修复版。
5. **移除与销账**：`git worktree remove --force`（非裸删）6 枚全部执行 + `--resolve` 六次带注记。
   - **resolve 复开缺陷**（重要，供车道 A 修判据时同批）：`--resolve` 只把条目迁 `resolved/`，`--scan` 只要 `.aidrafts/<sid>` 目录还在就**立即重建 open** ⇒ resolve ≠ 终态，终态必须落到"资源面消失"。故先补字节三证再移除目录。
   - 效果读数（可复跑）：open 条目 144→**138**；命中面唯一路径 119→**17**（本族 102 条封路全解）；`docs/03_modules/MOD-SELL-020/blueprint.md`、`docs/_working/chief_fullchain_20261006/*`、`docs/_working/deadcure_campaign/01_ledger.md`、`tests/gov/governance/d5_architecture/*` 由 BLOCK 转 **PASS**。
   - 登记=**裁定#498**（车道分支 58a6c8de9e，队列正门 `q-20261009-st-deadcure2-20261009-0001` 落 dev；主区当时含他人 staged 热册面，按"merge 整条路禁用、只走队列正门"处置）。
6. **4 枚未跟踪件去向定策**（restore 条道）：字节已在 blobs（`55a9a010…`/`6e50046b…`/`a2936ba4…`/`6edb5805…` 与 blob 文件名逐位相等）且被 3-4 枚死袋引用 →
   - `docs/_working/sector_line/{gpu_input_pack,statreplay}/*.py` 2 件：`directory_contract.yaml` 值=`docs/_working/` forbidden 含 `.py`（全局禁令腿同时点名 docs/01~03~/08~）；内容与 `scripts/sector_line/` 现版双向差异（71/115、36/72 行）→ **不自投**，归一期在案的 G7 转车道工单；
   - `final_delivery_campaign/evidence_archive/tmp_{cleanup_inventory,small_evidence}*` 2 件：已入库的 `cleanup_manifest_20260930.md` 按路径**声明**其存在（"存档：evidence_archive/…"，且 md 字节数 152,056 与台账声明逐位相等）而文件从未落地 = 悬空引用 → **转工单**（不代他会话交割面落地）。
   - ⚠ Phase 2 连坐要件：上述 4 枚 sha 对应 blob 是这些内容的**唯一持久面**，blob_gc 归档前必须确认"被 dead/ 与 dead_archive/ 袋引用的 blob 一律不 collect"，否则二期归档会吃掉自己的抢救证据。**本条已被 §6.3 的只读测尺闭环**：B 桶（仅 dead 引用，7710 块）与 D 桶（仅归档引用，4765 块）工具侧标号即"禁碰"。
   - 交叉自证（不是巧合，是同一件事的两面）：这 2 枚 .py 所在的 G7 袋 `q-20260924-st-pipeline-final-20260924-0029` 在一期 action_plan 里 disposition=**pending_owner**（rule=R-8 business-asset，adjudication="unique content in business-asset area — Owner 门位禁代裁"，confidence=high），已被本期 §6.5 记为④结转不出坑 ⇒ "不自投"不是我临时保守，而是该袋本就在 Owner 门位面上；我在 §三.6 写的"归 G7 工单"与该结转账一致。


## 四、Phase 0c token 热册五面对账（本期最重发现）

册=`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`，身份键=册自宣 `unique_key.creation_tokens=[file, token]`（复合；按 file 单键会误报重登为撞车，按行集差会漏掉结构性移动）。

| 面 | 条目数（开工现测） |
|---|---|
| HEAD | 14201 |
| 盘面（主区） | 14203 |
| PG 账本 latest snapshot | **14145** |
| pending/processing 袋内 | 2 条盘面独有 = 全部命中在途袋 |
| 我家族 rescue tag 内 | 3 条三面全无 |

### 1. 蒸发机制本体被截获（非"外来整档快照"）
`commit_belt_daemon.py:468` 在盘检到 `disk_sha != state.content_sha256` 即调 `projection_run(mode="render")`；`_drift_write_phase` 对 `private_edit`/`conflict` 两象限**整档覆写盘面对 PG 渲染值**（PG wins）。开工时 PG 比 HEAD **少 56 条且多 0 条=严格子集** → 下一次 belt 事件就会从盘面删掉 56 条**已入库**条目（含一期台账本体 `deadcure_campaign/01_ledger.md`、dexp/chiefc 战役册、exam-cost 产物等）。
内存预演实测伤害半径：**发布前 58 条（HEAD 56+盘面在途 2）→ 发布后 3 条**。

### 2. 拆除手法（全走在册正道，零门侧改动）
- 意图 API `registry_ledger.api.register`（幂等：同键同指纹=OK_NOOP）补登 **53 条 GAP**；**3 条 GAP 被账本拒**（`CONFLICT_DUPLICATE existing_status=retired`）——拒得对：这 3 条宿主件 HEAD/盘面双缺，退役有效，账本在保护自己的退役决定；
- 补登家族车道 **3 条 token**（宿主件 `adjudication_routing_policy.md`／`2026-10-08-handoff-fullscore-night.md`／`matrix_campaign/HANDOFF_NEXT_SESSION.md` 三件**已在 HEAD 却三面无票**=悬空）；
- 预登 **2 条在途护票**（owner=`st-chiefc-20261009-rb1`(心跳 0.3 分钟前，活会话)／`st-tdm-examcard-20261009`），payload 逐字节取自盘面，未增删字段；
- `publish_snapshot` 物化 → **snapshot v128**，`entry_count=14598`，PG creation_tokens 14145→**14203**（=盘面面）。
- **未自跑 `--render`**：现算显示 render 会把 `ruling_precedent` 条目的 `map_mounts: [governance_legislation_map:D16-N7]` 改成 `no_mount_reason`（见 §四.3），那不是我该提交的语义变更。
- **未提交热册**：盘面仍含他会话在途行 + 一处未提交反转，随袋提交=归属篡改。落地通道=待正道 render 后由需该册变更的袋带上，或后续专袋。

### 3. 二次充气实测（同一条件 35 分钟内重新长回，且这次轮到别人）
拆弹后 35 分钟复算（19:40）：**盘面 14203→14396（+193 行）**，其中 **192 行 PG 无**（owner=st-examchief-20261009 188 枚考试卡 token + st-mastertc-l7 3 + st-chiefc 1），`--check` 复报 `quadrant=private_edit→conflict` ⇒ **下一次 render 的杀伤半径重新充到 192 行**。
处置=`tools/token_backfill_disk.py --execute`：意图 API 预登 189 枚（3 枚被账本按 retired 正确拒收）+ `publish_snapshot` → **snapshot v130**（entry_count 14789，creation_tokens 面 14393）；复测 `C7b_disk_rows_render_would_delete=3`（全为合法退役，宿主件 HEAD/盘面双缺），未解释=0。
附带取证：受害方 st-examchief-20261009 的心跳守护同样在 45 分钟前写 `{status:"exited", reason:"idle timeout", idle_seconds:1824.8}` 后退出（与本会话 §七 9-2 同形态同阈值 1800s）——**keeper 判据缺陷是全会话级而非本店独有**。

### 4. 一处只报不动的 Owner 门语义分歧（呈报面）
`src/zephyr/library/ruling_precedent.py | token=ruling-precedent-ruling-precedent-20261009`（`created_by=st-libfront-20261009`，该 sid 注册表查无=死会话）：
- HEAD=`map_mounts: [governance_legislation_map:D16-N7]`（由 `dbfb6e4cfc` 10-09 直写 YAML 落地）
- 盘面=PG=`no_mount_reason: …裁定域图 governance_legislation_map 为 machinery 结构…扩图例属 Owner 终审事项——同族先例=map_family 三 gate no_mount_reason 申报（74dafed105/3c19488dbd）`
即：**HEAD 多报了一个挂载，而其作者随后自行改判为"不挂，因扩图例属 Owner 终审"**，改判只进了 PG 与盘面，未进 git。三面对此一致，唯 HEAD 例外。撤销挂载/维持挂载都触"扩图例=Owner 终审"语义 → **只报不动**，交 Owner 或专袋。

### 5. 计数判据坑（随批留证，防后人重踩）
一期归档数用 `glob('q-*.json')` 会得 **392**，与 manifest 393 行差 1——差的不是丢失件，而是 1 枚 `.json.bak-orig` 后缀件（一期 1704 宇宙口径="1701 袋 JSON+空壳 1+.bak-orig 1+后继 1"）。归档对账判据必须按 **manifest qid × 物理名（含非 .json 后缀）双向集合差 == 空** 来算，不能按扩展名筛。

## 五、Phase 0d A-12 蒸发复发监视（口径=可复跑，不靠声明）

- 监视判据：`盘面 ⊇ HEAD` 不变量 + `PG snapshot ⊇ HEAD` 不变量，两面各一条命令（见 §七）。开工时 `盘面⊇HEAD` 成立（盘面独有 2、HEAD 独有 0 条），**`PG⊇HEAD` 不成立（缺 56）** → 拆除后成立（缺 3，且 3 条退役宿主件双缺，属合法）。
- 本期新蒸发事件实测=**0**（无一条 HEAD 行在盘面上消失；上表 A 桶=0）。
- **连续监视已装**（20:00 起在任）：`tools/monitor_a12.py`（pid 23596，300s 一采，只测不写）落
  `lanes/a12_monitor.jsonl`，三态判据分开：`ARMED`=下一次 render 将删的行数（盘面/HEAD 有而账本无，
  剔除合法退役）；`FIRED`=上一采样在 HEAD 或"盘面且 HEAD"的行这一采样消失（=真蒸发，须立即上报）；
  `CLEAR`。首采读数 head 14201／disk 14393／pg 14393／ARMED=0／FIRED=0 ⇒ **CLEAR**。
  设计取舍：监视器**不做自动补登**——无人值守地写权威账本会把归因搞脏，拆除动作仍由我按批执行并留事件号。
- 但这不是"治本已到位"的证据，而是**同一病灶的第二回现形**：账本事件 `111099`（2026-10-07 08:38，actor=`st-mastertc-l0`）reason 原文即"**daemon 投影 PG-wins render 与 YAML 手改交战根因修复——HEAD 独有条目补登记 PG**"。同判据修复在 10-07 做过一次，10-09 缺口又长回 56 条 ⇒ 病灶在**写入侧仍允许直改 YAML**（token 先行袋整档写册），而非投影侧。一期 §第六号增补令①"热册「盘面≥HEAD」不变量进门"正是该缺口的门侧治法，本期实测**尚未进门**。

## 六、Phase 1 预备（门未开，先把底图做出来）

1428 袋全量内容级编目已完成（`index.jsonl` 29.4MB，lineage 6189 路径），关键分布：

- `bag_verdict`：archivable **48**／needs_review 1378／delete_still_effectful 2（`aggregate()` 是 fail-closed：任一文件态非可归档即整袋 needs_review，故 needs_review ≠ 该复活）
- `revive_class`：regression_risk **1207**／safe_forward 134／nothing_to_replay 48／manual 28／additive_only 11
- 文件态：exact_in_head 39776／content_diff 22148／absent_in_head 16814／superset_in_head 16380／relocated_in_head 9333／landed_then_evolved 2873／delete_req_head_absent 1942／superset_relocated 391／eol_only 280／delete_req_head_present 233
- 族顶：st-tests-chief-20261004 157／st-cure-p01 138／st-closeout-basereq 104／st-f15-frombag 92／st-chiefc-20261009 58（其中 56 为新增）／st-cure-p08b 56
- ⚠ 直接重放风险量化：`head_only_lines_replay_would_destroy` 中 >100 行的文件 1647 个、21-100 行 1874 个——"requeue --from-bag" 对 regression_risk 1207 袋是回退弹，处置必须走键集/行级并袋而非整档重放。

### 6.1 车道分区（`partition_lanes.py`，族不拆散+贪心配平）
152 族 / 1428 袋 → 8 车道各 178-179 袋。族顶：F1=st-tests-chief-20261004(157)…F5=st-chiefc-20261009(58，其中 56 为本期新增)…F4=st-f15-frombag(92)+st-libfront(18)。分区文件=`common/partition.json`。

### 6.2 机判预分桶（给舰队同质工单，非给结论）
| 桶 | 袋数 | 含义 | 计划通道 |
|---|---:|---|---|
| A0_archivable | **48** | 全部文件态可归档（exact/EOL/superset/relocated/landed_then_evolved/delete_absent） | ①归档（开门即投，先 dry-run 后 --execute 后 verify） |
| A1_delete_effectful | 2 | 袋请求删的路径在 HEAD 仍存活 | 逐袋复核（删除类=Owner 保留面判据，不自裁） |
| B3_pure_new_additive | **121** | 仅有 absent_in_head 无冲突行=纯增量 | ②复活候选（token 两面登记+一次一袋） |
| B4_regression_risk_diff | **1235** | 双向独有行（重放即毁 HEAD 行） | ③联言判退 或 ④结转（逐族取证，禁整档重放） |
| B5_forward_diff | 22 | additive_only（HEAD 是袋子集） | ②复活（安全向） |

### 6.3 Phase 2 只读测尺（`scripts/governance/blob_gc.py --json` 默认 dry-run，20:02 现测，零写）
指令 §三 把 A-9 blobs 归档排在 Phase 2，但**测尺是只读的**，先量出来才知开门后要跑几批：

| 桶 | 块数 | 字节 | 处置含义 |
|---|---:|---:|---|
| A 活引用(pending/processing/hold) | 29 | 18.6 MB | 禁碰 |
| B 仅 dead 引用 | 7710 | 865 MB | 回放面，禁碰 |
| C1 done+归档混引 | 774 | 227 MB | 禁碰 |
| C2 仅 done 引用 | 1219 | 433 MB | 等 cleanup 消化 |
| D 仅归档引用 | 4765 | 1.115 GB | **禁碰**——本表自证了我对 Phase 2 的连坐担忧已被工具挡住 |
| Z 零引用孤儿 | 5539 | 2.105 GB | 本轮处置对象 |
| 多类混引 | 4914 | 294 MB | 罕见，禁碰 |
| **孤儿∧过 7 天宽限=可归档候选** | **4831** | **1.542 GB** | 分批 --archive 的真实工作量 |

- 附带取证（回应二期开工前我自己提的风险）：§三.6 那 4 枚"唯一持久面在 blobs"的车道件（`55a9a010…`/`6e50046b…`/`a2936ba4…`/`6edb5805…`）被 3-4 枚 dead/ 袋引用=落 B 桶（禁碰），且归档后转 D 桶仍禁碰 ⇒ **二期归档不会吃掉自己的抢救证据**，此条已闭环不需额外保护清单。
- 完整读数=`.runtime/tmp/st-deadcure2-20261009/blob_gc_dryrun.json`（364 KB，含孤儿 sha 清单）。

### 6.4 F 盘前提消失规则机判化（指令 §八.5）
`tools/f_probe.py` 袋信封面扫描（路径/dead_reason/message）=**2 袋**命中（`q-20260929-st-nightsweep-sw17-20260929-0001`、`q-20261006-st-cure-p12a-20261006-0022`），路径级命中 0；内容级命中留给车道在开袋时确认（全量 blob 扫描为求一个提示需读 GB 级，不值）。清单=`common/f_probe.json`。**未做盲归档**：命中仅作路由提示，处置仍按四终态取证。

### 6.5 ④结转账先行入账（记账≠处置，不越门）
`tools/carry_over.py` 把一期 disposition∈{pending_owner, returned_to_owner} 且仍在本期宇宙的袋**原样结转**入台账：
写入 **49 行**（pending_owner 37／returned_to_owner 12，与指令 §二基线"呈批 37／归主 12"逐位吻合），
每行证据=一期 action_plan 的 rule/adjudication/evidence/confidence/ticket/flags **原字段值**（零自造，
rows_without_p1_note=0）。cycle_check2 的 `dispositions_logged` 由 0 → 49，`C1_uncovered_bags_n` 1428→1379。
车道文件=`lanes/carry_over.jsonl`（该文件按"一期 plan 的纯派生"用 w 模式重写，禁 append 防自计双账）。

### 6.6 判据收紧一次（试点车道逼出的真盲区，非放宽）
试点车道（只读，48 袋逐件实测，报告=`lanes/pilot_archivable48.jsonl`）交回 8 袋 needs_review，理由=
**内容曾真落地、后被 tests 搬家批删掉、而取代面至今未提交**（既非"未落地"也非"可安全归档"）。
我独立复验两条断言均为**真**：
- `src/zephyr/gov_enforcement/commit_gates/r5_digit_suffix_gate.py` 的 `_is_r5_exempt` 豁免腿在 HEAD（L97/L180），
  但其 5 例豁免测试 `TestExemptionMarker` 在 HEAD **零命中**——`ee5b52cc147`(10-05) 加过、被 `87cb48bf0e5`
  (10-05"旧路径删除·补刀2/6") 删掉 ⇒ **在岗的逃生阀没有已提交的测试**；
- `tests/gov/compliance/test_f62_compliance_gate_wiring.py` 盘面 `??` 未跟踪且不在 HEAD（blob 对各 ref 树零命中）
  ⇒ F-1b 新路径面是**未提交件**，无声丢失风险成立。

盲区定位（是我编目器的设计缺陷，不是数据问题）：`classify_file` 里 `landed_dev=True` 分支**在重定位检查之前
就返回** `landed_then_evolved`，而该态在可归档集合内 ⇒ "曾入库现已被删"被当作"已被取代"。影响面现测：
**224 袋含 630 个"入库后被删"文件，其中 595 个是 tests/**；A0 48 袋里 10 袋属此形。
治法（方向=收紧）：该分支改为先试同基名重定位（同字节=relocated_in_head 可归档；袋⊆新家=superset_relocated 可归档），
**都找不到新家才落 `landed_then_removed_no_home`**，并把该态同时加进 `ARCHIVABLE_STATES` 之外的归档闸
（`deadcure2.py NON_ARCHIVABLE`）与 `revive_class` 的 opens 集。
收敛证据=**两条独立方法给出同一批 10 袋**（机判 fresh_slice 输出含 ffchief-0013／sJ-0039／sP-0071·0080／
closeout-0107·0202／cure-p01-0029／cure-p12b-0004／f15-0087／cure-p01-0084，与试点人工点名一致）。
⚠ 连带后果（Phase 1 开门必做）：冻结索引是用旧规则算的，**1428 袋必须用收紧后的引擎整册重跑**再判归档；
并且归档执行前逐族跑 `fresh_slice.py`（锚点漂移实证：试点期间 HEAD 从 218636c1 跳到 df609238eb，
chiefc-0021 的 backup.ps1 由 exact_in_head 变 content_diff——冻结判据不可直接落地）。

## 七、设施缺陷升旗（本期实测，交总筹/门位车道——本专车不做第二施工队）

### 9-1 TAKEOVER-PENDING 把热册提交面整体封死，且封者含**活会话**（死信发生器）
零写探针（直接调 `make_takeover_pending_gate().check`，读 `src/zephyr/gov_enforcement/commit_gates/takeover_pending_gate.py:160-176` 的 fail-closed return 行）实测：

| 提交文件面 | 结果 | 命中 open 条目 |
|---|---|---|
| `capability_canonical_file_registry.yaml`（热册） | **BLOCK** | st-chiefc-20261009-rb1 + st-deadcure-g1-chief + st-deadcure-restore-chief |
| `docs/_working/deadcure_campaign/01_ledger.md` | **BLOCK** | g2/g3/g4/promote/g1/restore 六条 |
| `docs/_working/chief_fullchain_20261006/99_final_delivery.md` | **BLOCK** | g2/g1/restore |
| `docs/_working/deadcure_campaign2/01_phase0_ledger.md`（本册，新目录） | PASS | — |

判死口径缺陷：`session_takeover_ledger.py:764-789` 取 `session_registry[pid]` 存活位，**心跳新鲜度与 logical 旗不参与判死**。实测受害者=`st-chiefc-20261009-rb1`：注册表 `pid=0, logical=True, hb_age=9.5s`，其 heartbeat.jsonl 末行 `{status:"alive", pid:3048}` 且 3048 进程存活——却被记 `pid 46260 dead` 判死入 open。另一形态=`st-chiefc-20261009`（总队，心跳 29.7s 新鲜）`logical=False` → 按"非 logical"判死。
后果链=热册是全会话单一热文件（一期实测 272 只袋引用），其面被封 ⇒ **任何**需要 token 先行袋落地的会话必死于此 ⇒ 死袋增多 ⇒ 更多车道成孤儿 ⇒ 封面更宽。这正是裁定#478 当年为"命中面不能吞死袋文件"立判据所防的同族形态（过咬=永久禁提交区），差别是这次咬进面的是**活会话的 worktree 脏面**。
本专车处方（不代修门侧）：① 台账件走**新目录**（不在任何命中面）；② token 走**两面登记**（PG 意图 API + 盘面 add-only，`tools/token_add_disk.py`，CREATE-GUARD 读盘面= create_guard.py:762 anchor_main_root，render 读 PG，单面必被另一面打飞），从而**不需要**提交热册；③ 判死口径修正要件（交车道 A，可与一期 第六号增补令② 并件）：`logical=True` 或 `last_heartbeat` 新鲜 ⇒ 不判死；`pid` 位只作辅证（9-2 给本会话自身实弹复现）。

### 9-2 keeper 判据缺陷本期再自犯一次（一期 第六号增补令② 未进门实证）
本会话自己的心跳守护 18:48 写 `{status:"exited", reason:"idle timeout", idle_seconds:1828.7, timeout:1800}` 后自行退出，`session_registry.json` 里本会话条目同时消失（注册表 4 条目无我）——若按一期 keeper 的 `mtime<900s 视为新鲜` 判据，此后 15 分钟内 keeper 都不会重 spawn，期间任何投递必死 ghost_session（一期 g3 车道即死于此，`01_ledger §§G-续 六号②`）。
本期治法（工具面，门侧仍待车道 A）=`tools/keeper2.py`：**读末行 status 而非 mtime**，`{无文件｜末行≠alive｜age>240s｜注册表查无}` 任一即无条件 register(pid=0,logical=True)+重 spawn。实测首轮（19:03:37）`cycle=1 respawns=1 note="RESPAWN(last_status=exited reason=idle timeout)"`，`--scan` 复跑对本 sid 零命中，注册表回到 5 条目含本会话。
恢复链三段（含我自己两处错判，留证防后人误读）：
② 19:47 复测发现守护仍写 `{status:"exited", reason:"session not in registry"}` 且心跳断流——真因=**注册表条目 90s TTL 过期后 daemon 自查即退**（`session_concurrency.SessionRegistry.get_session` 对过期条目返 None），keeper 的 register 与 spawn 之间存在过期窗口；同形态在 st-examchief-20261009 独立命中（其守护 18:57 亦写 exited/idle timeout 1824.8s，阈值同 1800）⇒ keeper 判据缺陷是全会话级；
③ 19:56 现况=daemon pid 38668 在任（每 30s 写 alive）、`get_session()=True`、keeper pid 56136 在岗。我一度以 `Where-Object CommandLine -like '*keeper2*'` 查询返空而误判 keeper 已死，实为**查询面误差**（改用 sid 子串匹配即见 56136）——"进程死活要用命令行实读，不要用我的模式串猜"。
待车道 A 的门侧要件：`_spawn_heartbeat_daemon` 与 registry TTL(90s) 之间需一次"注册后即时校验再退"的补偿（现形态下 register 与首轮 check 撞过期即秒退，只能靠外部 respawn 兜）；idle timeout 1800s 对**长思考型会话**（无文件活动但在干活）天然误杀，本会话与 examchief 两条独立命中即实证。

### 9-3 `--sweep-absorbed` 本专车未执行（避连坐，留证）
该命令的 `execute` 腿会把 dead/ 袋直接 `os.replace` 到 `dead_archive/absorbed`（`session_takeover_ledger.py:630-712`），**绕过本期四终态台账与归档区**，并以 `"w"` 模式重写 `salvage_ledger.jsonl`（覆盖既有抢救面）。二期使命=逐袋四终态入账，故只用其判据思想、不投其写腿；本会话仅跑零写诊断且未据此处置任何袋。判据复跑=`python scripts/governance/session_takeover_ledger.py --sweep-absorbed`（勿带 `--execute`）。

### 9-4 两处覆盖空洞升旗（交 tests 新家/门代码 owner 车道，本专车不代施工）
1. **在岗逃生阀无已提交测试**：`r5_digit_suffix_gate._is_r5_exempt`（HEAD L97/L180）的 5 例
   `TestExemptionMarker` 在 HEAD 零命中（`ee5b52cc147` 加过、`87cb48bf0e5` 随 tests 搬家删掉）。
   死信袋 `q-20261004-st-sJ-doctorb2-20261004-0039`（及同簇 -0080/-0004）持该测试字节，可按
   `ee5b52cc147` 版字节补投新路径而非放袋。
2. **F-1b 取代面未提交**：`tests/gov/compliance/test_f62_compliance_gate_wiring.py` 盘面未跟踪、
   不在 HEAD；5 袋（`q-20261001-st-ffchief-20261001-0013` 等）持其老路径版。老路径已被 `6324c9e0f6f` 删，
   新路径若继续不提交=**双头落空**（老的没了、新的没入库）。
   复跑：`git -C D:/ZephyrAlpha status --porcelain tests/gov/compliance/test_f62_compliance_gate_wiring.py`

### 9-5 试点车道本身的两处方法产出（供放量复用）
- **去重簇**：48 袋实为 **26 个内容簇**（requeue 链，最大簇 5 袋）⇒ 里程碑裁定按簇合并登记，逐袋入账仍保留（四终态台账覆盖袋不覆盖簇）。
- **车道纪律实证**：每行带自己的 anchor_head，试点期间 HEAD 从 218636c1 漂到 37b50057/df609238eb——不带锚的结论不可复跑。

### 9-6 队列假 done 新形态（我自己踩的，可复跑判据）
时序=**先在车道 `git_commit.py` 提交 → 再 `commit_queue.py enqueue`** 时，enqueue 的 `base_head` 自动取
**调用方工作树 HEAD**（此时已是我自己的 commit `58a6c8de9e`），袋对"自己的 base"零差异 ⇒
落地回执 `landed_id = "noop@436bbd89…"`、状态记 **done**，而 dev 分支**一条字节都没变**。
现测：done 袋 `q-20261009-st-deadcure2-20261009-0001` 回执 noop，`git show dev:ruling_registry.yaml | grep -c 裁定#498` = **0**。
处方=`--base-head <dev tip>` 显式传入（CLI 帮助原文："A 段显式传入，B 段自动取"）；重投
`q-20261009-st-deadcure2-20261009-0002` 实测袋 blob vs dev = **bag-only 36 行 / dev-only 0 行**（纯增量，含 #498）。
判据（放量前每袋自查，别只信 done）：`landed_id` 以 `noop@` 开头 ⇒ 立即用 `git show <branch>:<path> | grep -c <新键>` 反查，
不要以 done 目录存在为交付证据。**旧 done 袋保留不清**（它是这条死亡模式的实物证据）。

## 八、复核命令原文

```bash
cd /d/ZephyrAlpha
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:$PATH"
# 基线与桥接
python .runtime/tmp/st-deadcure2-20261009/tools/freeze_universe.py
# 接管条道内容级分诊（逐件行集对 dev）
python .runtime/tmp/st-deadcure2-20261009/tools/lane_triage.py --wt st-deadcure-g1-chief --out .runtime/tmp/st-deadcure2-20261009/common/lane_g1_chief.jsonl
python .runtime/tmp/st-deadcure2-20261009/tools/lane_triage.py --wt st-deadcure-restore-chief --out .runtime/tmp/st-deadcure2-20261009/common/lane_restore_chief.jsonl
# 热册五面对账（只读）
python .runtime/tmp/st-deadcure2-20261009/tools/token_recon.py
# 蒸发不变量两检（PG⊇HEAD 应=0 缺；HEAD 独有盘面行应=0）
git show HEAD:docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml > /tmp/head_reg.yaml
# rescue 与字节保真
git tag -l 'rescue/*'
git cat-file -t rescue/st-deadcure-g1-chief; git cat-file -t rescue/st-deadcure-restore-chief
# 归档区对平（判据=集合差为空，非扩展名计数）
python -c "import json,glob,pathlib;A=pathlib.Path('.runtime/commit_queue/dead_archive_20261009_deadcure');man={json.loads(l)['qid'] for l in (A/'manifest.jsonl').open(encoding='utf-8') if l.strip()};phys={p.name[:-5] if p.name.endswith('.json') else p.name for p in A.iterdir() if p.name!='manifest.jsonl'};print('manifest',len(man),'physical',len(phys),'sym-diff',len(man^phys))"
# 台账自身落地核验
git log --oneline -1 --name-only
# TAKEOVER-PENDING 零写探针（判据复跑，不投递）
python - <<'PY'
import sys,types
from pathlib import Path
sys.path.insert(0,'src')
from zephyr.gov_enforcement.commit_gates.takeover_pending_gate import make_takeover_pending_gate
gw=types.SimpleNamespace(project_root=Path('.').resolve())
spec=make_takeover_pending_gate()
for f in ['docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml',
          'docs/_working/deadcure_campaign2/01_phase0_ledger.md']:
    ok,_=spec.check(gw,[f]); print('PASS' if ok else 'BLOCK',f)
PY
# 二期自洽环（连续两轮 CLEAN 才算过）
python .runtime/tmp/st-deadcure2-20261009/tools/cycle_check2.py
# 心跳守护实况
cat .runtime/tmp/st-deadcure2-20261009/lanes/keeper_st-deadcure2-20261009.log
```

## 九、净零申报

- 零新 gate、零新注册表、零新真源轴、零新业务资产。
- 新增文件=本册 1 枚（二期首册，承接一期 `deadcure_campaign/` 使命，非重复轴：一期=裁定面+G 组执行面，本期=Phase 0-2 执行面）。
- 工具 6 枚全部落 `.runtime/tmp/st-deadcure2-20261009/tools/`（不入仓库）。
- 袋只迁移不删除；PG 写入=幂等补登（可 retire 反悔，事件全留痕：本会话 `register` 事件 61 条 = event_id **111867–111927**、`publish` 事件 1 条 = **111928**；本会话名下 `active` 新条目 **58** 条 = 53 GAP+3 车道补票+2 在途护票；册内 creation_tokens 现态 active 14203／retired 169）。
