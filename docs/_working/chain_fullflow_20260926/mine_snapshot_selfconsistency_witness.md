---
ttl: task_bound
---

# 提交袋「快照字节 vs 它自己的基底树」自洽见证层 — M2 挖矿案卷

- 案卷 ID: mine_snapshot_selfconsistency_witness ｜ 日期: 2026-09-26 ｜ 班: 全流通战役挖矿班 M2（只挖矿，不施工）
- 铁律遵守: 全程未 add/commit/stash/checkout/reset、未写 ref、未改 src/ scripts/ tests/ docs/01…；
  实验全部在 `mktemp -d` 临时 git 仓；主仓只读 `git show dev:<path>`；探针脚本在 `.runtime/tmp/mine_snapself_w2/`
- hash 口径: 本卷凡"袋字节/blob"比较一律 git blob id 空间（`_git_blob_sha`），与 bytes-sha256（`blob_sha256` 字段）、
  文本 content_sha256 三套互不引用

## 0. 母节点与一句话结论

落地器按袋清单整档覆盖 / 整树重放时，会把不属于该袋的第三方内容写进 commit（归属篡改）或回退已落地的在册修复。
现有五块补丁（逐文件快进 `_conflict_reason`、同字节短路 `_noop_overwrite_paths`、同会话豁免
`_drift_all_same_session`、热册条目级三向合并 `_merge_registry_file`、派生标量自愈 `_heal_derived_totals`）
**判据集恒为「dev 移动 × 袋路径集」**。

> **结论（实测）**：缺的确实是一层「袋字节 × 袋自身基底树」见证，且这层见证**只能封到三类形态**
> （W1 同会话盲区携带 / W3 条目级携带复活删除 / W2 错误基底洗白），
> **封不到另两类**（W9 盘旧于同 sha 的 HEAD、W4/W5 归属证据本身失真）。
> 因此"统一见证层"作为单一构件不成立；成立的是**见证 = 三处接线 + 一份共享判据**
> （落地前 stale-path 档、合并器条目加侧闸、生产侧基底自证），任何一处缺席即整层空转（本卷 W17 实测）。

## 1. 通道枚举表（可达路径穷举；每条带入口与状态）

复现脚本：`.runtime/tmp/mine_snapself_w2/{w1,w2,w3,w4}.py`（统一 tmp 仓夹具：`new_repo`/`wt_at`/`enqueue`/`land`，
`land` = 真函数 `_conflict_reason`→`_apply_snapshot`→带 `[GW:sid:qid]` 提交→`update-ref dev`，绕过门禁链，量判据与快照语义）。
运行：`export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; W=$(mktemp -d); SNAPWORK="$W" python .runtime/tmp/mine_snapself_w2/w1.py`

| ID | 通道 | 入口（dev 面 函数:行） | 触发条件 | 实测状态 |
|----|------|----------------------|---------|---------|
| W1 | 零改动携带 × 同会话豁免盲区 | `commit_queue_landing.py:1191 _conflict_reason` → `:1329 _drift_all_same_session` → `:1517 _apply_snapshot` | 袋内路径字节恰等其自身基底；该路径漂移全出自本会话前袋 | **实测-打穿**（§2.1） |
| W2 | `requeue --from-bag` 基底取重投时刻 | `commit_queue.py:1985+ requeue_dead_item`（`if base_head is None: base_head=resolve_base_head(wt)`） | 死信原袋字节旧于当下 dev 尖 | **实测-打穿**（§2.2） |
| W3 | 注册表合并器加侧无闸＝携带条目复活他人已落地删除 | `:1456 _merge_registry_file` → `:533 _plan_insert_splices`（`base有+ours无+theirs有→采纳`） | 条目引用文件仍在（脚本保留、册除名＝常态） | **实测-打穿**（§2.3，两种基底口径都复活） |
| W4 | 无基底袋 × 时间基底兜底对"无标记提交"失明 | `:1361 _legacy_base_drift_reason`（owner 为空 ⇒ 不计 offender） | 袋无 `base_head`；dev 上同路径他方提交 subject 无 `[GW:]`（合并提交/手工提交/早期提交） | **实测-打穿**（§2.4） |
| W5 | 归属证据＝可伪造文本标记 | `:146 _GW_OWNER_RE`（subject 首个 `[GW:x`） + `:1329` | 他会话提交的 subject 里出现本袋会话的 `[GW:sid]`（引用他人 qid 的文体常态） | **实测-打穿**（§2.5） |
| W6 | CAS 重放整树回退（9de51e673f 病形） | `:2370 _replay_commit_without_gates` `if not drifted:` | `base_dev..new_dev` 任意漂移 + re-parent 旧树 | **实测-已拦**（§2.6，漂移时重建树；零漂移 re-parent 是恒等操作） |
| W7 | 直连 `git_commit.py`（无 --enqueue）陈旧覆盖 | `scripts/git_commit.py:1222+` → gateway 直提 | 主区盘旧于 dev 时 `git add` 取旧字节；HELD-OVERLAP 只在对方已 claim 时触发 | **判据级-不可测**（禁在主仓跑门禁链；直提面无任何"基底"概念＝机理确定，量级未测） |
| W8 | reroute fail-safe 降级直提 | `:3048 reroute_auto_commit_to_queue` 异常上抛 → `_commit_auto` 降级 | 入队设施异常（QueueReject/import/读盘） | **判据级**：检测器 `assert_single_writer_dev_history` **全仓无运行时调用点**（§3 ③），降级=静默 |
| W9 | 生产侧"盘旧于同 sha 的 HEAD" | `resolve_base_head`（基底＝工作区 HEAD）＋ `:1747 _converge_one` skipped_dirty | 盘被收敛跳过/外部回退到比 HEAD 更旧，HEAD 未动 | **实测-打穿，且见证层封不到**（§2.7） |
| W10 | 基底双字段互不自证（base_head 与 base_blob） | `enqueue_item`（两者各自落袋）；落地侧只验 `cat-file -t base` | 调用方在两处分别取基底；合并器 base_head 优先，重校验用 base_blob | **实测**（§2.8）：三种错配组合结果完全相同 ⇒ 落地器**只用 base_head**，base_blob 在合并链上是备用件 |
| W17 | **显式 `--base-head` 入袋 ⇒ 见证层结构性空转** | `commit_queue.py:2782-2796`（`if base_head is None:` 才填 `base_blobs`）＋ H 队见证 `if not entry.get("base_blob"): continue` | 操作者按官方处方 `requeue … --base-head`（cascade_stale 处方原文即如此） | **实测-打穿**（§2.9）：同一袋带/不带 base_blob，见证读数 `[]` vs `['hot.yaml']` |
| W18 | 池化 CAS 重放腿不复跑见证 | `_pool_cas_replay`/`_replay_commit_without_gates` 内零 `_witness_stale_carry` 调用（全仓消费点仅 2 处＝定义＋`__call__`） | 池模式竞态重放 | **判据级-安全面已兜住**（非注册表同路径重叠⇒`nonmergeable` 死信），**留痕面缺**（§2.10） |
| W19 | 见证"剥除"只改内存，事后不可审计 | H 队 `_witness_stale_carry`（`item["files"]=keep`，无写回/无 jsonl） | 部分命中剥除后落地 | **实测**（§2.10）：剥除名单只在 logger，done/ 记录无痕 |

## 2. 实测输出原文（关键读数）

### 2.1 W1（命令：`SNAPWORK=$W python .runtime/tmp/mine_snapself_w2/w2.py` → w1b 段）
```
=== W1b 零改动携带 × 同会话豁免（夹具修正：基底取两粒种子之后） ===
 bag1: landed base 8c4436cfee
  dev:hot@tip1 = b'v1\n'
 bag2 land: landed 50d56c0098e977750640d982cf37fa4a33da0453
  dev:notes@tip2 = b'n1 own edit\n'
  dev:hot@tip2   = b'v0\n' ⇒ 在册 v1 被旧字节回退？ True
  见证读数 hot.yaml: 袋==base_blob? True  袋==dev? False
  见证读数 notes.txt: 袋==base_blob? False  袋==dev? False
 控制组(他会话漂移) _conflict_reason = 冲突：快照基底 8c4436cfee88 …… 逐文件快进判定失败，死信回退属主会话
```
读法：**"袋==基底 且 袋!=dev" 是这一型唯一可用信号**，五块补丁没有一个读它；控制组证明现有判据不是整体失效，
漏的正好是"自家前袋推进 + 我携带旧字节"。

### 2.2 W2（w2.py → w2b 段）
```
 from_bag 重投 base_head == ecb87a3eb5  原袋 base= 231bb16ca5  当下 tip= ecb87a3eb5  ⇒ base==tip? True
 新袋 hot 字节 = b'vB\n' (=声称基底的在册字节)
 _conflict_reason(新袋, tip) = None
 land: landed  dev:hot = b'vA\n' ⇒ vB 被 vA 吃？ True
```
即"旧袋字节被洗成本包改动"——与 W1 同信号但**见证本身也封不到**（袋 vA ≠ 声称基底 vB），必须修基底口径。

### 2.3 W3（w1.py → W3 段）
```
 dev:E7 在册？ False
 base_head=删前c0: 合并结果含 E7？ True
 base_head=删后tip: 合并结果含 E7？ True
 对照 theirs 真改过 E7：含 seven-edited？ True
```
两口径都复活：删前基底＝W2"宁可多救"规则；删后基底＝E7 被视为 theirs 新增。**注册表族的"删除语义"对陈旧袋零防护**，
且 REGISTRY-MASS-DELETION 只管删不管复活（加法侧无对称闸）。

### 2.4 W4（w3.py → w4c 段；袋经 `enqueue_item` 不带任何基底）
```
 袋 base_head = None  base_blob = None  created_at = 2026-09-26T02:31:19+08:00
 无标记他人落地 → _conflict_reason = None
 land: landed  dev:hot = b'v0 stale\n' ⇒ 无标记他人内容被吃？ True
```
对照（w2.py → w4b 段）：同一夹具但他人提交带 `[GW:laneOther:q-…]` ⇒ 判红（两条腿都红：快进 + 时间基底）。
⇒ **兜底不是死代码**（E 队此项标"推断"，本卷升为"已验证：有效面对 marked、失明面对 unmarked"）。
生产可达性：merge commit（subject 无标记）与手工/早期提交同型；`assert_single_writer_dev_history` 亦豁免 merge。

### 2.5 W5（w1.py → W5 段）
```
 _conflict_reason = None
 land: landed  dev:hot = b'v0 stale\n' ⇒ laneOther 的 v9 被吃？ True
```
夹具里 laneOther 的落地提交 subject 只多写了一句"修复 [GW:laneSelf:q-20260926-laneSelf-0001] 处方件"
（本仓案卷文体常态：提交说明引用他袋 qid），`_drift_all_same_session` 即把**他人**漂移认成本袋会话，
豁免生效、旧字节覆盖。归属证据无签名、且 `re.search` 取首个匹配 ⇒ 见证层若沿用此口径（现确实用了）则该证据链不可信。

### 2.6 W6（w2.py → w6b 段）
```
 漂移集 = {'notes.txt', 'third.txt'}
 重放 != prev？ True
  dev@replay: third = b't1 foreign landed\n'  notes = b'n1 foreign new file\n'  hot = b'v1 mine\n'
 零漂移 re-parent: third = b't0\n' (应=t0), hot = b'v1 mine\n'
```
⇒ 整树回退腿**已闭**（在册守卫＝`if not drifted`，本卷独立复现，未沿用旧结论）。
观察：`need_remerge` 变量在守卫改造后**已无消费点**（死代码，登记为清理项，非缺陷）。

### 2.7 W9（w1.py → W9 段）
```
 盘 vs HEAD 同 sha？ True  盘字节= b'v0\n'
 base_head==tip? True  base_blob= 39999cdf3a
 _conflict_reason = None
 land: landed  dev:hot = b'v0\n' ⇒ 在册修复被回退？ True
 见证读数: 袋==base_blob? False （False ⇒ 危险携带判据不触发 ⇒ 此形态见证层封不到）
```
本型在判据上与"会话故意回写旧版"**不可区分**（袋≠基底＝有改动意图）。
⇒ 任何"见证层一装、陈旧覆盖全消"的宣称都是过度承诺；此型只能由**生产侧新鲜性**（入袋前盘-vs-HEAD 比对＋
收敛未跳过的证据）或 claim/编辑痕迹交叉验证封，不能由袋内自洽封。
生产留痕（F 队原读、本卷复核口径不变）：`.runtime/commit_queue/main_workspace_sync.jsonl` 中 `skipped_dirty` 存量 1799、`error` 3。

### 2.8 W10（w1.py → W10 段）
```
 一致：base_head=c0, base_blob=c0 → 含 E7？ True
 错配：base_head=tip, base_blob=c0 → 含 E7？ True
 错配：base_head=c0, base_blob=tip → 含 E7？ True
 base_head 非 commit 值 → 冲突判定失败：base_head 非可判 commit（deadbeefdead）——死信回退人工
```
⇒ 合并链上 **base_head 恒优先**，base_blob 只在 base_head 不可读时顶上（两字段无交叉校验、无一致性断言）。
后果：级联重校验（用 base_blob）与三向合并（用 base_head）可能各自对着**不同的基底**判同一只袋。

### 2.9 W17（w4.py → w17 段）— 本卷对新证层的最重质疑
```
 袋 base_head= d376111cdc  base_blob= None
 见证读数 dangerous= []  safe= []        ← 显式 --base-head 袋：见证完全空转
        dangerous= ['hot.yaml'] safe= []  ← 同袋若由 resolve_base_blobs 填了 base_blob
 无 base_blob 袋过 _witness_stale_carry = None
 land: landed  dev:hot = b'v0\n'          ← 在册 v1 仍被回退
```
可达性非假想：`commit_queue.py:2783` 的 `if base_head is None:` 使 `--base-head` 显式传入路径**永不填 base_blobs**；
而 `cascade_stale` 死信的官方处方原文就写着"重投前先按当前 dev 重取基底（--base-head）"
（`commit_queue.py:_DEAD_PRESCRIPTIONS`）。⇒ **按处方操作 = 关掉新见证**。

### 2.10 W18/W19（w4.py → w18/w19 段）
```
 见证消费点出现次数（含定义）= 2  在 _pool_cas_replay/_replay_commit_without_gates 内是否调用？ False
 是否 item["files"]=keep（就地改内存）？ True
 是否写回队列 JSON / 审计文件？ False
```
安全面尚兜得住（池化重放对非注册表同路径重叠先判 `nonmergeable` 死信），但：
① 见证只在直连腿一处 ⇒ 新增落地腿=新盲区（结构脆）；② 剥除名单不进 done/ ⇒ 生产上无法回答"哪只袋被见证救过"，
只能翻 log；③ 死信分类只加了一个 `"快照自洽见证"` marker 字符串，若某日 reason 文案改写即掉回 other 族（弱耦合判据）。

## 3. E 队旧称 7 通道逐条重证（推断态→实测态，含证伪）

| E 编号 | 主张 | 本卷重证结果 | 证据 |
|--------|------|------------|------|
| ①（T-1）直提路径陈旧覆盖 | 未拦，需 own-scope gate | **不改判、但降级**：机理成立（直提面无 base/见证概念），**本次未实测**（禁在主仓跑门禁链）＝仍是读码态 | `scripts/git_commit.py:1222+` 走 gateway 直提；`allow_tracked_drift` 消费点 8 处（gateway 2487/2990/3011 等）证实旗可抑制本袋未归因硬阻断 |
| ②（T-2）`--allow-tracked-drift` 直提豁免 | 未拦点=直提 | **部分证实、部分证伪**：旗确实把 `TRACKED-DRIFT-READONLY` 未归因写入降为放行（`gateway.py:2990 _audit_gate_tracked_drift(allowed=…)`+`:3011`），但它是**审计放行**非静默（留 audit 面）；"热册不豁免"仍待施工 | grep 消费点（本卷 §3 表） |
| ③（T-3）reroute 降级直提 + 检测器离线 | 未拦，检测器仅手动 | **证实且加重**：`assert_single_writer_dev_history` 在主仓**零运行时调用点**（唯一非 docstring 引用是 3 个测试文件），即"单写者不变量"目前**无自动可见性**；模块 docstring 自述"②降级 commit 仅带 [GW:{sid}:auto] 无队列标记"⇒ 检测器即使跑也把降级面判为违例，属已知设计张力 | 本卷 grep 全仓（scripts/ src/ tests/） |
| ④（T-4）`requeue --from-bag` 吃非注册表热件 | 推断态 | **实测-打穿**（升为复现态），见 §2.2 | w2b 输出 |
| ⑤（T-5）盘旧于同 sha HEAD | 已验证（读码） | **实测-打穿**（§2.7），并新增判定：**此型袋内不可判**，E 队"入袋前盘-vs-base 见证"是唯一可行处方方向 | W9 输出 + 见证读数 False |
| ⑥（T-6）热件集全量三方合并（治本首选） | 推荐 C 为骨 | **量化后改判：挂起/形态替换**（见 §8 候选 B）。实测分母：`.runtime/commit_queue/dead/` 686 件中"逐文件快进判定失败"仅 **17 件**（≈2.5%），其触及路径为 `scripts/governance/meta/rules_integrity_db.json`×4、`.py`×7、`.md`×4、`script_manifest.yaml`×2 ⇒ 其中**能被条目级合并救的只有 2 件（≈0.3%）**，而占比最高的 .json/.py/.md 是生成器产物或代码——三方合并对它们语义不成立（正解=重算/让路，非 merge） | 死信普查命令见 §6 第 6 轮；路径直方见 §8 候选 B |
| ⑦（T-7 + ⑦b/⑦c）派生标量面 / 级联精确相等 / pool 已闭 | ⑦a 真、⑦b 观察、⑦c 已闭 | ⑦a **证实**（`_heal_derived_totals` 唯一调用点在 `_merge_registry_file` 出口；`is_registry_mergeable` 覆盖面实测：catalogs 三册=合并，`config/flags.yaml`、`script_manifest.yaml`、`registry_of_registries.yaml`、`AGENTS.md`、`architecture_model/index.yaml`、`data/runtime/*.txt` 全部=整覆盖，见 §2 附表 w13）；⑦b **证实为观察项**（`_mark_cascade_stale` base 精确相等才算命中）；⑦c **实测-已拦**（§2.6，独立复现非引用） | w3.py W13 段输出 |

E 队"7 通道"净结果：**证实 4（④⑤⑦a/⑦c 已拦面亦为证实）、证实并加重 1（③）、部分证实部分证伪 1（②）、
量化后改判 1（⑥）、维持读码态 1（①）**；无一条被证伪为"假通道"，但 ⑥ 的方向被数据改判。

## 4. H 队已写盘见证层的判别力检验（反事实构造）

- 现状（在册核验，只读 `git show dev:`）：`assert_snapshot_selfconsistent` / `_witness_stale_carry` /
  合并器携带闸 `base_idx[key][2].data == t_block.data` / requeue 原袋基底 四项**均未进 dev**；
  `git log dev -S "assert_snapshot_selfconsistent" -- scripts/governance/commit_queue_landing.py` 输出为空
  ⇒ 该符号**从未进入 dev 史**（不是"落了又被抹"，是压根未落地）。
  H 队实现只存在于 `.aidrafts/lane_ff_snapself` 工作树盘上（landing +118 行 / commit_queue +14 行，其 HEAD 3bfeb4b174 是 dev 祖先）。
- **在途时序实测（本卷自证读数可复核，也修正任务书的一个前提）**：本班第 1 次调用跑
  `git -C .aidrafts/lane_ff_snapself status --porcelain` 时输出**只有那一个未跟踪测试文件**（盘上无见证码）；
  约 6 分钟后同一命令报 `M scripts/commit_queue.py`、`M scripts/governance/commit_queue_landing.py`、
  `M tests/governance/test_commit_queue_landing.py`。⇒ 本卷开头"diff 为空 / H 队只写了测试"的读数是**真实的历史瞬间**，
  H 道正在并发写码，任务书所谓"H 队正在做雏形"成立但比我拿到的快照更靠前。
  为避免读到一个移动目标，绿侧复测锚定了盘态指纹（read-only `git hash-object`，未写任何 ref）：
  landing=`594f4082d7906f8b4a4bf90f20c99831b522ea40`、commit_queue=`1748004f26b2183326dced42a9279202e6f53ea6`、
  尺=`8635b5c2e4ca1c2cb1cdc8e40f3d02e2e6993d60`（git blob id 口径，勿与 bytes-sha256 混引）。
- **正向（能否红）**：把 dev 版两份生产文件复制到 `mktemp -d` 最小树，原样跑 H 队尺
  （`cp` dev 文件 + 该测试文件 → `python -m pytest tests/governance/test_commit_queue_snapshot_selfconsistency.py -q --tb=line`）：
```
test_...:204: AssertionError: ATK-3 复发：袋字节恰等其自身基底的陈旧携带路径回退了 dev 在册内容
test_...:234: AssertionError: _witness_stale_carry 未装配
commit_queue.py:1985: ModuleNotFoundError: No module named 'scripts.governance.enqueue_preflight'   ← 我的最小树缺包（夹具缺陷，非尺缺陷）
test_...:322: AssertionError: ATK-1 复发：陈旧携带（袋条目恰等其基底）复活了 dev 已落地的删除
test_...:364 / :398: AttributeError: module '_cql_snapself' has no attribute 'assert_snapshot_selfconsistent'
test_...:412: AssertionError: __call__ 主链未接快照自洽见证＝ATK-3 复发面
7 failed in 8.13s
```
  **判定：有判别力**——不是恒绿尺。且红在**行为半段**（204/322 两行是"在册内容被回退/已删条目被复活"的字节断言，
  非缺席断言），说明尺钉的是后果而非存在性；接线守卫（412）作为第二道，摘线即红。
- **反向（可否满足）**：H 队工作树盘上（=dev 内容 + 见证改动，未提交）同尺
  **7 passed in 11.07s**（首跑）/ **7 passed in 8.61s**（锚定上述盘态指纹后的复跑）⇒ 不是不可能通过的死尺。
  两侧合起来才构成判别力证明：**同一份尺在册面 7 红、带见证面 7 绿，且红点落在字节后果上**。
- **尺的两处弱点（施工前须补，属案卷意见非裁定）**：
  1. H2（from-bag）只在我这里因缺包未证红——该形态的行为红由本卷 §2.2 独立补位（同形状打穿已实测），
     尺本身无缺陷，但**其红依赖被 import 的旁支模块**，说明尺的隔离面对"最小树"不鲁棒；
  2. 尺**没有钉 W17**（`--base-head` 袋 base_blob 缺位 ⇒ 见证空转）与 W5（归属证据可伪造）：
     即"见证装上之后"这两条仍然打穿，本卷 §2.5/§2.9 为唯一证据；
  3. 尺 L 组只护"部分命中不误杀"，未护"剥除留痕可事后审计"（W19）。

## 5. 六向寻路台账（每向：内码反查 + 外部检索双动作）

**①上游/生产者（谁造袋）** — 内码：入袋生产者共 4 个（`git_commit.py:916` 交互正门、`commit_queue.py:2018` requeue、
`commit_queue.py:2802` 裸 CLI、`commit_queue_landing.py:3525` reconciler 改道），四者都填 base_head/base_blobs，
**但 CLI 仅在 base_head 缺省时填 base_blobs** ⇒ 生产者侧存在"自证素材可由旗关掉"的口子（W17）。
外部对照：GitHub merge queue 要求每个候选按**当前** base 重新组树（不允许自带基底声明）。
发现=成立（W17）。

**②下游/消费者（谁吃落地结果）** — 内码：`_converge_main_workspace`（主区盘，fail-open，skipped_dirty 1799 条）、
`_registry_entry_retired` 的盘存在性判据（读主区盘⇒可被脏盘压制退役判定）、
`generate_script_manifest.py` 读盘字节烤进产物、`validate_static_manifest_drift.py --check` 读盘⇒**自洽台会装绿**
（同 commit 两棵树相反判决：主区 PASS / 净树 FAIL 174≠180，F 队 R3 原读，本卷复核其命令仍成立＝在册 174≠180 未归位）。
外部对照：Bors/Gerrit 的 submit-ability 必须在**目标态**重算（"merge if necessary" 的已知缺陷讨论＝同型问题）。
发现=成立，且属邻班（门禁自洽台）范围，本卷只登记不重裁。

**③算法/机制向外部对照**（≥2 独立来源，入图）：
- git 官方 `read-tree`/`merge-tree` 三方合并语义（Git 项目文档，git-scm.com，2026 更新）：
  1-way read-tree 是**整 index 置换**（我们的重放腿用的正是它，语义＝"以 dev 为准重建"，
  而 re-parent 分支＝"以袋的旧树为准"）⇒ 官方语义支持本卷 §2.6 的"零漂移才可 re-parent"判据。
- GitHub Docs《Managing a merge queue》（GitHub，2024–2026）：队列对每个合并组**按最新 base 重新校验/重组**，
  快照不携带自定义基底 ⇒ 与 W2/W17 的"袋自带基底可信"正是相反取舍；支持"基底必须由落地器重算，不接受生产者声明"。
- Gerrit 邮件列表《Is Gerrit 'merge if necessary' strategy inherently broken?》（repo-discuss，2018）：
  提交可行性依赖"在目标态重算"，否则出现同类静默吞并。
- Jujutsu（LWN 介绍，2024）：冲突是 first-class 数据、随 change 携带，绝不静默覆盖 ⇒ 反证我方 W1/W9 "静默吸收"设计。
- 乐观并发控制 / TOCTOU（Wikipedia OCC，2025；OWASP Race Conditions）：check-then-act 必须带**版本指纹**且
  指纹不可由被校验方自证 ⇒ W5（文本标记归属）与 W10（双字段互不自证）是典型 TOCTOU 面。
内码反查同题：我方 `resolve_base_head` 的"基底＝生产者工作区 HEAD"＝**被校验方自证**，与外部共识相反。
发现=成立（外部五条 vs 我方两处相反设计）。

**④后端/该放哪一层** — 内码：见证三处必需接线各自的可证性：
(a) 生产侧（入袋前新鲜性，封 W9）；(b) 落地前判定（封 W1/W3，H 队现放这一层，位置正确）；
(c) CAS 重放/池化腿（W18 现在**没有**这层）。若只放 (b)，则 (a)(c) 两层的漏网形态由 (b) 背锅——
本卷建议判据函数独立于消费点（`assert_snapshot_selfconsistent` 已如此设计，是好形状），
但**消费点数必须等于落地腿数**（现在 1<2）。发现=成立（结构可施工，接线面缺一条）。

**⑤时间/生命周期** — 内码：袋的基底在三个时刻分别被读：入袋（生产者）、出队判定（`_conflict_reason`）、
重放（`_replay_commit_without_gates`）。三者中只有第一个是可伪造/可陈旧的，后两个读 ref——
所以见证必须在每次"读 dev 之后"重算，而 `base_blob` 是入袋定格值 ⇒ W17/W9 是同一时间轴缺陷的两个断面。
外部对照：GitHub merge queue 的 freshness 检查＝"出队时重算，不接受入队时快照"。发现=成立。

**⑥字段（EnqueueItem 现有素材够不够）** — 已有足以构造见证的：`base_head`、逐路径 `base_blob`（git blob 空间，
与 `_git_blob_sha` 同 id 空间，可直接比）、`files[].blob_ref`/`blob_sha256`、`action`、`session_id`、`qid`、`created_at`、
`meta.worktree_root`。缺的（本卷判定为施工必答项）：
① `base_source`／`base_declared_by`（基底是生产者自报还是落地器重算）；
② `disk_matched_base`（入袋时盘字节是否==该基底树，逐路径位图；= 封 W9 的唯一素材）；
③ `worktree_head_is_dev_ancestor`（基底与 dev 的祖先关系，现由落地器 `merge-base` 现算，袋内无凭据）；
④ `blob 归属签名`（W5：`[GW:sid]` 是文本，袋内无不可伪造归属；需要"提交点位的归属由 ref/对象而非 subject 证明"）。

## 6. 挖矿日志表

| 轮 | 矿脉 | signal / noise + 归因 | 产出 | 复现命令 |
|----|------|----------------------|------|---------|
| 1 | 资产盘点（车道/工件/前案卷） | signal：F/E 两队案卷**仍在盘上**（`ALL_LANE_ARTIFACTS/`），任务书假定"已消失"是错的——归因＝INDEX.json 归档机制把已阵亡车道工件复制留存 | 找到 ATK-1/2/3 与 T-1..T-7 原文 | `ls .runtime/tmp/ALL_LANE_ARTIFACTS/` |
| 2 | 落地器判据链读码 | signal：五块补丁的判据集同型（dev×袋路径） | 通道骨架 W1–W10 | `grep -n "^def \|^class " scripts/governance/commit_queue_landing.py` |
| 3 | 首轮实测（W1/W3/W4/W5/W6/W9/W10） | noise：W1 首跑"已拦"＝我夹具错（基底取在第二粒种子之前，把 notes 的种子提交当成他人漂移）；W6 首跑"整树回退"＝我把 foreign sha 取成 `git rev-parse HEAD`（工作树分支尖）——**两处都是量尺错不是生产错**，第二轮修正后各得反向结论 | §2.1/2.3–2.8 全部输出 | `SNAPWORK=$W python .runtime/tmp/mine_snapself_w2/w1.py` |
| 4 | 二轮实测（夹具修正） | signal：W1/W2 打穿复现、W6 已拦、W4 的 marked 对照判红 | 同上 | `… w2.py` |
| 5 | 无基底袋真形态 + 覆盖面 + 在册核验 | signal：`is_registry_mergeable` 只护 catalogs 前缀（11 取样：3 合并/8 整覆盖）；H/E/F 主张的四个修**均未进 dev** | W13/W14 | `… w3.py` |
| 6 | 死信普查（为候选 B 找分母） | signal：快进失败 17/686，触及路径以生成器产物与 .py 为主 ⇒ 通用三方合并可救面 ≈0.3% | §8 候选 B 裁定依据 | `grep -rl "逐文件快进判定失败" .runtime/commit_queue/dead/ \| wc -l` + 逐件 dead_reason 路径直方（脚本见 §8） |
| 7 | H 队尺判别力双向测 | signal：dev 上 7 红（2 红在行为半段）、H 树上 7 绿；noise：我最小树缺 `enqueue_preflight` 致 H2 error（夹具噪声，已如实标注） | §4 结论 | `cp dev 文件→mktemp 树; python -m pytest … -q --tb=line` |
| 8 | 见证层自身覆盖面（W17–W19） | signal：`--base-head` ⇒ 见证空转（本卷最重发现）；池化腿无见证；剥除无痕 | §2.9/2.10 | `… w4.py` |
| 9 | 归属证据可伪造性 | signal：subject 文本即可骗取同会话豁免（§2.5） | W5 | `… w1.py`（W5 段） |
| 10 | 外部对照检索（4 次检索，未触发限流） | signal：外部共识=出队重算基底＋冲突须 first-class | §5 ③ | WebSearch |
| 11 | H 道在途时序 + 剥除语义下游一致性 | signal：①同一命令 6 分钟内从"只有未跟踪测试"变"三件 M"⇒ 见证码是**此刻正在写**的，任务书拿到的快照更靠前，我的"盘上有码/ref 无痕"两条读数都真；②落地链 6 处路径集全从 `_item_paths` 现读 ⇒ stale-path 级剥除不会引发 gate 假红（A 可施工的关键前提） | §4 时序实测、§8 候选 A 补段 | `git -C .aidrafts/lane_ff_snapself status --porcelain`；`grep -n "_item_paths(item)" scripts/governance/commit_queue_landing.py` |
| 12 | 候选 B 分母复核（生成器产物族） | signal：17 只快进死信里 6 只触及"可重算产物"（`rules_integrity_db.json`×4／`script_manifest.yaml`×2）⇒ 正解是让路/重算（B′），非合并（B） | §8 候选 B/B′ | 见 §6 第 6 轮同一命令的路径直方段 |

## 7. 防噪音四闸过闸记录

- **闸1 在册性核验**（判"已落地"只读 ref）：候选修 4 项 dev 面缺席实测（W14）；`快照自洽见证` 在死信库计数=0（未出厂）；
  邻班案卷 `mine_door_registration_completion.md` 已在册，本卷不重裁其结论。**过**。
- **闸2 活性核验（谁调它）**：每块补丁与每个候选都取调用点——`assert_single_writer_dev_history` 零运行时调用点（W8/③ 因此升级）；
  `_heal_derived_totals` 唯一调用点；见证消费点 2 处（定义+`__call__`）⇒ 重放腿无消费（W18）。**过**。
- **闸3 判别力核验（能红）**：H 尺双向测（§4）；本卷每条"打穿"都给了字节级后果断言，不用"函数返回 None"充当证据。**过**。
- **闸4 复现可核 + 口径唯一**：三套 hash 口径分列（§0）；两处夹具自错（轮 3）已在日志点名并给修正版；
  引用他班数字（1799/3、174≠180）均标"原读复核"而非重算。**过（有 1 条受阻）**：
  主仓直提门禁链（W7）与 `--allow-tracked-drift` 行为面（W2/E②）受铁律"禁在主仓跑门禁/写 ref"限制**未实测**＝登记为受阻，不记"查无"。

## 8. 挖后自审闸（三态裁定；量尺=终局全貌）

候选 A —「H 队 stale-path 见证（落地前档 + 合并器条目加侧闸 + requeue 原袋基底）」
→ **施工**。判据可证（§4 双向）、误杀面有 L 组尺、死信分类与处方三处齐。
施工必答补面（缺一即视为未收口）：① W17 封口（见候选 D）；② W18 重放腿补消费；③ W19 剥除留痕落册。
**剥除语义的下游一致性（本卷补测，是 A 可以施工的关键前提）**：落地链上所有路径集都从
`_item_paths(item)` 现读（`:1552` 快进判定 / `:1721` 时间基底 / `:2421` claim 清单 / `:2497` "快照未真应用"
诊断 / `:2596`、`:2666` 两处 CAS 重叠判定），而 H 的实现是就地改 `item["files"]` ⇒ 剥除之后**没有任何一处**
仍按原袋清单行动，不会出现"gate 按四件查、实际落三件"的假红/假绿。该一致性若不成立，A 就只能走"整袋死信"档。

候选 B —「非注册表文件通用三方合并」（我上一轮自提、后以 6% 占比挂起）
→ **方案封矿（封"通用三方合并"这一形态），但其 2/3 死因另有正解，转为候选 B′**。
证据（新算分母，非沿用 6%）：686 只死信中快进失败 17 只（2.5%），其触及路径直方
`rules_integrity_db.json`×4、`.py`×7（commit_queue/landing/gateway/daily_gate_snapshot/registry_mass_deletion_gate/align_all）、
`.md` 案卷×4、`script_manifest.yaml`×2 ⇒ 条目级合并语义**只对那 2 只成立**（≈0.3%）；
占比最高的三类是"生成器产物/代码/案卷"，对这些做三方合并**语义即错**（合并出的字节无人能再生产，且违反"静态清单禁手工"方向）。
反驳者一问（三条最强反对"封矿"）：
 (1) "0.3% 是死信口径，活下来的静默吃掉根本不死信，所以分母不可知" —— 答：对，但本卷实测的三类打穿形态
 （W1/W2/W3）**全部在 17 只之外**，且全部由候选 A/D 封，不由合并封；合并的分母只会更小不会更大。
 (2) "`config/flags.yaml` 这类结构册未来会热，现在封了将来要重挖" —— 答：解锁条件写进候选 B′（见下），不是保留矿。
 (3) "git 自带 merge-file 一行就能合，成本极低" —— 答：`git merge-file` 曾被同战役踩过"假重基"坑
 （基底取错点位即自证 0 冲突），成本低但**证不了基**，正是候选 D 要补的那块。
**候选 B′（新矿，挂起排期）**=「派生件（生成器产物）落地的让路/重算语义」：对 `rules_integrity_db.json`/
`script_manifest.yaml` 等"可由再生成器重算"的热件，落地遇漂移时不覆盖也不死信，而是**判重算并让路**。
解锁条件：该族死信/事故计数（本卷口径：4+2=6/686≈0.9%）连续两个战役窗口 ≥5% 或出现一次静默吃掉在册产物的实测。

候选 C —「生产侧盘-vs-base 新鲜性见证（封 W9）」
→ **施工（高优，且必须与 A 并案）**。A 单独出厂会在 §2.7 那型上给出"已装见证"的错觉——**这是本卷最重要的负面结论**。
最小形态：入袋前逐路径 `git hash-object(盘)` vs `base_head 树 blob`，结果作为袋内字段 `disk_matched_base` 位图（⑤⑥两向的素材缺口），
不一致 ⇒ requires-sync/拒入袋（不是拒落地）。
反驳者一问：
 (1) "盘≠HEAD 就是会话故意改的，你凭什么拒？" —— 答：不拒"改"，只把"改"标成显式声明的 reverse-intent（并要求该路径有 claim），
     这与直提面 CLAIM-REQUIRED 语义同构；改的是**入袋侧不再无偿信任**。
 (2) "skipped_dirty 1799 条会一次性全变 requires-sync，噪声灾难。" —— 答：首波只对该会话本袋清单内路径判，量级=袋大小；
     且 skipped_dirty 是"未收敛"证据不是"必回退"证据，需要与 reverse-intent 双条件才拦。
 (3) "见证层已经绿了尺，再动生产侧=扩面违规。" —— 答：尺的 L 组只测了落地侧误杀，没测生产侧漏杀（§2.7），扩面有实测支撑。

候选 D —「基底自证链：不接受生产者自报基底」
→ **施工（判据小、收益顶）**。三处必改：① `--base-head` 显式传入必须同时补 `resolve_base_blobs`（否则拒绝旗用，W17）；
② 落地器对每只袋复算 `blob(袋内字节) vs blob(base_head:path)` 与 `base_blob` 一致性，不一致 ⇒ 死信点名（W10）；
③ requeue/改道/CLI 三处基底重算收敛为单一函数（现在四处各写一条 `resolve_base_head` 调用）。
成本：一次批量 `ls-tree`（与现有 `resolve_base_blobs` 同批，无新增子进程风暴）。

候选 E —「归属证据去文本化」（W5）
→ **挂起排期**，解锁条件＝出现一次"跨车道 subject 引用他袋 qid 导致的静默吃掉"生产实证（本卷仅 tmp 复现，未证生产已发生）。
理由：修法牵动 `[GW:]` 体系（宪法 §9 第 8 条明令标记不可伪造，但**读取侧**目前完全按文本信任），属跨包改造；
且候选 A/D 落地后，W5 型攻击的**收益面**大幅缩小（陈旧携带档被见证拦，只剩"袋真改过"型，而那型属直提面 W7 域）。

候选 F —「池化重放腿补见证 + 剥除留痕」（W18/W19）
→ **施工**（并入候选 A 的补面，不单独立项）。判据：消费点数==落地腿数；留痕必须落 done/dead JSON，不能只落 log。

候选 G —「时间基底兜底对无标记提交失明」（W4）
→ **挂起排基**：先补"可达性计数"（dev 上 merge commit 触及热路径且被后续无基底袋覆盖的次数），
本卷未取到该计数＝不设"规模小"为封矿理由，只登记为"待补分母"。

候选 H —「GATE-21/自洽台双锚」（邻班）
→ **只登记不重裁**（F 队 R3 已在册，且属门禁自洽台班职责）。

条数：三态裁定 **8 条**（施工 4：A/C/D/F；挂起排期 3：B′/E/G；封矿 1：B 的"通用三方合并"形态）。

## 9. 长尾矿脉清单与已查无记录

长尾（未挖，按性价比排序）：
1. `_noop_overwrite_paths` 与见证的口径重叠——它已经读了"袋字节 vs dev"，**为什么不顺手读"袋字节 vs base"**？
   （一函数内可同批取，候选 A/D 的实现位置选择，未测性能面）
2. `three_way_merge_registry_yaml` 的 passthrough/drift 分流（`_split_passthrough_and_drift`）对**整文件头尾区**的处理：
   头部注释/标量区是逐字节取 ours 还是可被携带改写？（与派生标量自愈同域，本卷未挖）
3. `_prestage_snapshot` 的 `git add --pathspec-from-file`：袋清单外的 worktree 残留在 index 里会不会被 write-tree 带进重放树？
   （W6 实测只覆盖 read-tree 置换路径，未覆盖"worktree 曾被他袋污染后复用"的池常驻工棚形态——**这是未挖的最大单点**）
4. `_already_landed` 的 noop 哨兵前缀与 `landed_id` 双证：崩溃窗口内是否会跳过见证（见证在 `_conflict_reason` 之后，
   而 `_already_landed` 更早）？
5. `queue_marker`/`_QUEUE_MARKER_RE` 与 `_GW_OWNER_RE` 两套标记正则的**豁免口径差异**（merge 豁免只在断言函数里，
   `_drift_all_same_session` 不豁免 merge ⇒ 一处漏一处窄，未逐型对齐）
6. 死信分类三处补齐的机生性（`_DEAD_REASON_ITEM_MARKERS` 字符串表 vs 处方表 vs 尺配对表）——新死因族靠人记，
   属"静态清单禁手工"违例面，本卷只点名未立案。
7. `resolve_base_blobs` 的 `--` 与 pathspec 上限（`_LSTREE_CHUNK`）在超长袋上分批失败时"块内全 None"＝见证素材静默缺失（W17 的第二可达路径，未测）。

已查无（记录在案，别再回头找）：
- `git update-index --assume-unchanged/--skip-worktree`：全仓代码路径零使用（F 队同题，本卷在 lane 树上复核
  `git ls-files -v | grep -v '^H '` 为空）⇒ 该子型无自动到达路径。
- `.aidrafts/lane_ff_single_writer`、`lane_f_redteam_repro` 工作树内的"残件代码"：均无（只有案卷 md，已在 `ALL_LANE_ARTIFACTS/`）。
- 「H 队已把见证层提交到某分支/rebase 进 dev」：dev 无该符号且 `-S` 全史无命中 ⇒ 从未落地；码在 H 道工作树盘上
  （02:3x 起 `git status` 可见三件 M），非在册面（见 §4 时序实测）。
- 「CAS 重放整树回退仍存在」：实测已拦（§2.6）。

## 10. 待 Owner 门位登记项（只登记，不自裁）

1. 候选 A（H 队见证层）与其三项补面是否并案出厂——涉及队列落地主链判据收紧（死信量会变多），属 high 域（flag/注册表邻近面）。
2. 候选 C 的入袋侧 requires-sync：会改变 `--enqueue` 的可用性手感（首波可能批量拦），需 Owner 定"宁停勿吃"是否适用于交互正门。
3. 候选 D-①：`--base-head` 旗的语义变更（要么补 base_blobs、要么禁用该旗）＝既有 CLI 契约变更。
4. 候选 E：`[GW:]` 归属证据去文本化牵动提交工具红线（宪法 §9 第 8 条域）。
5. 邻班重述（不重裁）：`gate_registry` 在册 174≠180 的归位通道；自洽台双锚化。
6. 本卷在册事实：`assert_single_writer_dev_history` 零运行时调用点＝#ARCH-317 强制面至今无自动可见性（是否提为事件触发 reconciler）。
