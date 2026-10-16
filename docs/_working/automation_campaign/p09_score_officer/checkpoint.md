---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑨成绩官·游标
---

# 游标

cursor: exam_scores_v1.yaml#rows[108]
last_run: 2026-10-16
last_batch: 当日增量 5 行全判（本班 st-qoder-p09-1016-01 班尾 22:33:43 复测＝磁盘 sha bb557705beea260f→682ab7cf437164b4／144451B／rows 109；rows[109] 起待判；⚑ 三面同值仅瞬时条件，详见本班游标推进记录与 ledger §14）
notes: 游标由本岗每批推进；监督员(⑩)可代修。

## 游标推进记录 ｜ st-qoder-p09-1015-02

- cursor: `exam_scores_v1.yaml#rows[74]`（75 行全判；rows[73]/[74] 由前两班出单，其余 73 行为历史补判）
- last_run: 2026-10-15
- last_batch: 当日增量 0 行（册 mtime 03:37 早于台账 rows[74] 条目 03:40，实测无新行）
- 本班更正：本文件原 `cursor: 未开始` 与台账已判到 rows[74] 矛盾＝上一班未推标，非本班新造判据。
- 下一班锚点：首件仍读 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`，只判 rows[75] 起的新行。
## 游标推进记录 ｜ st-qoder-p09-1015-03

- cursor: `exam_scores_v1.yaml#rows[74]`（不变，75 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 0 行（三证：mtime 03:37:20 未变／bytes 105598 未变／sha256 前缀 c7e5b1f8bfb98ae2 与 02 班记录逐位同；机械加载 docs=2 rows=75）
- 本班新增交接事实（下一班必读，勿重查）：
  1. 分数册**不在 HEAD**，只活于主区 index（`A `）＋队列两袋：`q-20261015-st-scorehome-20261014-0003`（旧面 blob c14e6635＝104507B）与 `-0004`（现值 blob c7e5b1f8＝105598B）。**若前袋先落地，册面会回退**，落地后须以 `git log -1 --name-only`＋`git show` 读回核实。
  2. 判卷尺口径已换：族按**卡体 `pillars_numeric` 键集**定（calibration 43／high_event 23／comparison 9），卡体锚点按**卡体内部 `card_id` 字段** join（75/75）。按路径段分族会假红 23 行。
  3. 复跑脚本＝`.runtime/tmp/st-qoder-p09-1015-03/reconcile3_verdict_replay.py`（只读，本班实测 verdict 不可再现＝0）。
## 游标推进记录 ｜ st-qoder-p09-1015-04

- cursor: `exam_scores_v1.yaml#rows[82]`（磁盘面 83 行全判；本班增量 rows[75..82]＝`p07a-agg8-20261015` 批）
- last_run: 2026-10-15
- last_batch: 当日增量 8 行，100% 判卷（verdict 不可再现＝0/8）；6 fail／2 pass；pass 行**未升 verified**（两腿：`ic_ir_min` 柱从未检验＋净/成本面全 NaN，见台账 §4）
- 三证（本班实测，下一班可比对）：mtime `2026-10-15 07:17:15`／bytes `115036`／sha256 前缀 `24ef736d819d0be1`；快照件 `.runtime/tmp/st-qoder-p09-1015-04/score_snapshot.yaml`；复算尺 `reconcile4_delta.py`
- ⚑ 下一班必读事实（勿重查）：`git status` 该册＝`AM`（index 落后磁盘 9438B）；**pending 内 5 个 `st-scorehome-20261014` 袋无一携带现值 83 行面**（`-0003` blob `c14e6635`＝74 行面、`-0004` blob `c7e5b1f8`＝75 行面、`-0005/-0006` 不含该册）⇒ 任一旧袋先落地即回退本批 8 行（含 6 条负结果）。本席未代修未 requeue。
- 本班另开可复用面：正交闸**已可用**（列名契约适配面在 `.runtime/tmp/st-qoder-p09-1015-04/pool6/`，工具输出 `PR=2.1272`）⇒ 02/03 班"PR 零读数"结论作废，正解见 to_impl.md「修⑤ 正解改写」。
## 游标推进记录 ｜ st-qoder-p09-1015-05

- cursor: `exam_scores_v1.yaml#rows[82]`（**不变**，磁盘面 83 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 0 行。四证（本班实测）：mtime `2026-10-15 07:17`／bytes `115036`／sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`（与 04 班逐位同）／`yaml.safe_load_all` doc1.rows=`83`
- ⚑ 下一班必读更正（覆盖 04 班同题结论，旧案卷不删）：
  1. **现值 83 行面在途有袋**：`q-20261015-st-qoder-p07-1015-01-0001`（07:30:18）blob=`24ef736d819d…`＝磁盘现值面。04 班"没有任何一袋带现值面"按 `st-scorehome` 字面成立、按全 pending 面不成立。
  2. **馆级未落地**：`git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**；index＝**30 件**；全部 30 件 `AM`（index≠磁盘，`exam_scores` 差 +9438B，余 29 件差 +164~179B）。
  3. **同路径三面并存**：磁盘 83 行／index=`c7e5b1f8`（75 行）／`st-scorehome-0003`=`c14e6635`（1 doc／74 行）／`-0004`=`c7e5b1f8`（75 行）。落地顺序决定终面。
  4. ⑩席 07:52 读的是 **index 面 rows=75**（`pulse/queue_depths.md:24`），本席读磁盘＝83 行 ⇒ 下一班报行数时须**声明读的是哪一面**。
  5. 15 员池 PR 仍无源：`c1_market.factor_signal`/`factor_feature_value` 复测各 **0 行**；写者模块存在（`src/zephyr/factor/core/batch_output/buffer.py`）⇒ 根因收窄为"生产腿未跑"，非源无数据；`docs/_working/integrated_backtest/` 仍不存在。
- 本班实测面：判卷尺复跑 8 行 verdict 全再现（pass [76,78]/fail 6，不可再现 0）；尺＝`.runtime/tmp/st-qoder-p09-1015-04/reconcile4_delta.py`。
- 本班耗时：08:18:32 起 → 08:29:37 已落四件（≈11.1 分）；六件齐＋两处更正终值 date=08:30:46（累计≈12.2 分，班限内）。
## 游标推进记录 ｜ st-qoder-p09-1015-06

- cursor: `exam_scores_v1.yaml#rows[82]`（**不变**，磁盘面 83 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **0 行**。四证（本班实测，与 04/05 班逐位同）：mtime `2026-10-15 07:17:15`／bytes `115036`／sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`／`safe_load_all` docs=2、doc1.rows=**83**
- ⚑ 本班交接事实（下一班必读，勿重查）：
  1. **读面声明制自本班起落字**：磁盘 83 行／index `c7e5b1f8…`＝**75 行**／HEAD＝**查无此件**（`git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/` 仍 **0 件**，index 30 件）。报行数前先 `git show :<册> | sha256sum` 对表。
  2. **修⑧ P0 未解除**：pending **103 袋**中按**精确路径**携带本册的＝**3 袋**——`q-20261015-st-qoder-p07-1015-01-0001`（blob `24ef736d…`＝现值面）、`st-scorehome-20261014-0003`（`c14e6635…`＝74 行旧面）、`-0004`（`c7e5b1f8…`＝75 行旧面）⇒ **两个旧面袋仍在途**，任一后落地即洗掉 04 班 8 行（含 6 条负结果）。本席未 requeue、未代修。⚠ 谓词坑：用 `endswith('exam_scores_v1.yaml')` 扫会**误计 13 条**（命中 `alt_factor_/factor_/indicator_/indicator_conditional_/strategy_exam_scores_v1.yaml` 五册同后缀）。
  3. **本席 02–05 班的 6 只袋全未落地**（pending 中 `grep p09`＝6 行）；head 袋 `waiting_s=28019`、`lease.state=drain-active`。⇒ 磁盘面可见全靠主区工作树，git 落点为零。
  4. **复测同值面（禁第四次重烧）**：`factor_signal`/`factor_feature_value` 各 **0 行**（三度同值）；修⑥ 面 `51/49/19/30`（两度同值）；P-1 `9 行含 nan 否决／6 行 nan 唯一 fail`（两度同值）。
  5. **本班新产出可复用尺**：`python .runtime/tmp/st-qoder-p09-1015-06/census6_materiality.py`（只读，四段：轮次账／族×柱材料度／单一死因／申报面）。⚠ 该尺按柱名前缀解析，high_event 与 comparison 两族的 **fail 串柱名与卡体 `pillars_numeric` 键不同名**（本班逐行取证），新行落这两族须逐行回卡体。
  6. **会话注册形制**：`register(SID, pid=0, held_files=[路径 list], task_files=[路径 list], logical=True)` ⇒ `logical=True` 会打印"downgraded (chief-form verification failed) … fail-open"＝**预期降级非故障**；随后 `heartbeat`＋`get_session`＋`GitCommitGateway().registry.get_session`＋shard 存在＝四证齐。⚠ **更正（本班终报，旧句保留）**：本班首投 09:06:51 **仍被 SESSION-REQUIRED 拦**（rc=8）——09:06:24 实测本席 08:53 注册的那枚 shard 已**消失**，同目录 03/04/05 席 shard 健在且 mtime 09:06 被心跳刷新 ⇒ 05 班的"注册面 flapping"**连续两班复现**；正解＝注册＋心跳＋双读＋入袋串成一条命令压缩窗口（本班 09:07:07 注册→09:07:57 ENQUEUED `q-20261015-st-qoder-p09-1015-06-0001`）。
- 本班判卷面：增量 0 行；自检轮一＝在册尺正文原样跑，8 行 verdict 全再现（不可再现 0/8）；轮二＝**首次回核 high_event 与 comparison 两族**（rows[8]/[48]/[66]），rows[8]/[48] 门柱未走样，rows[66] **无一根实质柱被检验**（verdict 由 nan 单独决定，复证在册 P-1）。本班**零升级、零新开单号**，未动分数册与判据字节。
## 游标推进记录 ｜ st-qoder-p09-1015-07

- cursor: `exam_scores_v1.yaml#rows[82]`（**不变**，磁盘面 83 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **0 行**。四证（与 04/05/06 班逐位同）：mtime `2026-10-15 07:17:15`／bytes `115036`／sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`／`safe_load_all` doc1 rows=**83**
- ⚑ 本班交接事实（下一班必读，勿重查）：
  1. **修⑧ 面积扩到七册**：谓词换成全路径前缀 `docs/04_research_records/backtest/scores/` 扫全 pending＝(袋,件) 对 38／回退弹 **8 对**；`st-scorehome-0003` 载 7 本册且 7 全回退弹（`exam_scores` Δ10529B＋`alt_factor`/`factor`/`indicator`/`strategy`/`paper_pool` 各 156–168B＋`indicator_conditional` **袋比磁盘大 170B**）。复跑尺＝`python .runtime/tmp/st-qoder-p09-1015-07/sweep7_score_house_regression.py`。
  2. **机制级定性（新证，非复测）**：落地仲裁 ours 取 **HEAD 面而非工作树**（`scripts/governance/commit_queue_landing.py:3436` `old_dev=self._dev_head()`、`:2466`、`:433-444` 全路径恒真）；而该馆在 HEAD 与 `-0003/-0004` 的 base_head（`59b6a7e802`）件数皆 **0** ⇒ base 与 ours 同时不存在 ⇒ 判"仅袋改→取袋"。**旧面回退是默认而非竞态**，修法方向＝该馆先入 HEAD（或 base&ours 皆缺而工作树更新时 fail-closed 不取袋），禁弱化仲裁本身。
  3. **落地顺序**：`-0002` pos=1、`-0003` pos=17、`-0004` pos=41、`-0005` pos=42、`-0006` pos=47，唯一带现值 83 行面的 `q-20261015-st-qoder-p07-1015-01-0001` **pos=63** ⇒ 现值面最后落，中间有"册面=74 行"窗口。本班值守期间 pending 两次读数 96→100（队列在消化，非同一时刻快照）。
  4. **卡状态也会跨面分叉**（比行数更致命）：`TDM-E-L9-A17/calibration/02_研报评级调整事件研究` HEAD/index=`blocked_on_data`、磁盘=`preregistered`（mtime 08:38:14，⑥席改判未入库）；②席 `unblocked.md:17`（07:07 段）按 git 面如实报 blocked。⇒ 报卡状态须声明读面（05 班口径注已扩面）。
  5. **`修⑩` 是悬空单号**（`to_impl.md:130` 引用、全战役仅 1 次命中、无定义）；在册定义止于 `修⑨`。引用 comparison 族 rows[66..71] 请锚 **P-1＋修③**。
  6. **本席交付纪律**：02–06 班 8 袋件集并集 7 件、最新袋 `-06-0002` 只 6 件 ⇒ `to_datasource.md` 现值面唯一承载袋是 `-05-0001`（pos=83）。自本班起**每袋带全 7 件**。本席袋在 done/dead 面 grep p09 计数＝**0/0**（全部未落地，git 落点为零）。
  7. **行级复核尺必须打印 `fails`/`regimes`**（册面无 `failed_pillars`/`reasons` 键）；且 `git cat-file -e` 经 python subprocess 会被 GBK 报错串崩出"HEAD 查无"**假阴性**，改用 `git rev-parse -q --verify HEAD:<path>`。
- 本班判卷面：增量 0 行；自检轮一＝rows[37]/[45]/[67] 回卡体（门柱未走样，rows[67] 复证在册 P-1）；轮二＝全 83 行 × 卡体 `card_id` join **83/83 命中**（口径扩面）。本班**零升级、零新开单号、零新增呈批**，未动分数册与判据字节。
## 游标推进记录 ｜ st-qoder-p09-1015-07 第二段（值守内到件补判）

- cursor: `exam_scores_v1.yaml#rows[83]`（**推进 1 行**；磁盘现值面 84 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **1 行**（rows[83]，`p07a-880rs-20261015` 批，node `TDM-E-L9-A03`）＝1 fail，100% 判卷，门柱未走样；归因＝方向单 1 条（to_miners，单行证据不判死）；零新增单号／零呈批／零对照。
- 四证（本班终态，下一班可比对）：mtime `2026-10-15 09:38:34`／bytes `116029`／sha256 `4f986ec7143a690fc51d4cd01705af94a835963842bcfe093198a97ac2ebe3cf`／`safe_load_all` docs=2、doc1.rows=**84**
- ⚑ 下一班必读（覆盖本班进场读数，旧句不删）：
  1. 本班 09:12 进场时"增量 0 行"（sha `24ef736d…`）在当时为真，**09:38:34 面推进到 84 行** ⇒ 游标已推到 rows[83]；下一班锚点＝sha `4f986ec7…`，只判 rows[84] 起新行，并**在终报前重测一次册面**（S-3：进场四证只锚定进场时刻）。
  2. 该册回退弹现＝**3 只袋**（`scorehome-0003`=`c14e6635` 74 行、`-0004`=`c7e5b1f8` 75 行、`p07-1015-01-0001`=`24ef736d` 83 行也已落后）；载现值 84 行面的袋＝**⑦席 02 班 `-0001`/`-0002` 两只**；分数馆在 HEAD 仍 **0 件**；`pending/.stale/` 有 55 枚 stale 标记件（形制 `{qid,stale,stale_at,stale_by,trigger}`、无 `files` 键，勿计入袋数）。
  3. `修⑩` 悬空（引用见 `to_impl.md:130`，全战役仅 1 次命中无定义）；rows[66..71] 真源锚＝P-1＋修③。
  4. 行级复核必打印 `fails`/`regimes`；`ic_ir` 柱全册仅 3 行有面（rows[83] 是最新一根，修⑥ 新面读数 52/49/22/30）。
- 本班耗时与班限：起批 09:12:33；第二段因值守内到件而就地补判，**跨出 40 分钟班限**（终值见台账 §9/§10，如实登记不压缩成"班限内"）。
- ⚑ 本班自犯并当场修复的第三把坏尺：`write7b_deliverables.py` 的断言写死"块首须为 `## `"，而台账 §10 是 `###` 子节 ⇒ 断言在 ledger 写盘**之后**才失败，重跑一次即把 impl/miners/iter/ledger 四件各复制成两份。剥重正解＝按"最长重复后缀"剥一份＋用本班首袋 blob 文本做前缀正对照（四件均 `startswith(首袋面)`=True 后才收工）。⇒ 教训入册：**追加型交付的断言必须写在写盘之前，且脚本必须幂等（块已存在即跳过）**；本班已在同款脚本里补幂等旗。
## 游标推进记录 ｜ st-qoder-p09-1015-08

- cursor: `exam_scores_v1.yaml#rows[83]`（**不变**，磁盘面 84 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **0 行**。四证（本班进场与终报前各测一次，与 07 班终报锚点逐位同）：mtime `2026-10-15 09:38:34`／bytes `116029`／sha256 `4f986ec7143a690fc51d4cd01705af94a835963842bcfe093198a97ac2ebe3cf`／`safe_load_all` docs=2、doc1.rows=**84**
- ⚑ 本班交接事实（下一班必读，勿重查）：
  1. **三面读数**：磁盘 `4f986ec7…`（84 行）／index `c7e5b1f8…`（105598B／75 行，与 06/07 班逐位同）／HEAD 该馆 **0 件**。读 index 面请用 `git show :<path>`；`git rev-parse -q --verify :<path>` 返回**对象 id 文本**，本班拿它算哈希曾得 `d05ae00e…`＝假"第五枚面"，已当场更正。
  2. **修⑧ 面位移**：携带分数馆的袋 **5 只**（回退弹 3＝`scorehome-0003` 74 行／`-0004` 75 行／`p07-1015-01-0001` 83 行；现值 84 行载袋 2＝⑦席 02 班 `-0001`/`-0002`）；`pending/.stale/` 标记件 55 枚无 `files` 键。**本席 11 只袋全在 pending、done/dead＝0**（02–07 班 git 落点连续两班为零）；head 袋 `q-20261015-st-chiefdead6-20261015-0027` `waiting_s=31693`（≈8.8h）、lease `drain-active`、daemon online。
  3. **本班新开**：修改单 `修⑪`（平行卡 `*_derived` 绑定回落母序列，`scripts/backtest/fexam/card_binding.py:364`；6 对 12 行逐字节全等）＋呈批 `P-5`（同读数两卡算不算两次独立考试，A 合并记账／B 物化后重考）＋方向单 1 条产量口径（分母写 59 不写 65）＋`pulse/independent_signals.md` 独立命题分母更正。**零缺数单、零对照单、零升级**。在册定义现止于 `修⑪`；`修⑩` 仍悬空（引用 1 次无定义），comparison 族 rows[66..71] 请锚 P-1＋修③。
  4. **新可复用尺（只读、内置对照）**：`python .runtime/tmp/st-qoder-p09-1015-08/dup8_metrics_identity.py`（跨卡同读数 vs 同卡复跑分面；正对照 rows[2]≡rows[10]、负对照 rows[83] 独占）；`pair8_parallel_of.py`（6/6 命中 `parallel_of`）；`probe8_landing_face.py`（落地面，⚠ 其 `blob_ref` 按 CWD 解析的缺陷未修，面由 blob 文件名 sha 独立证实，下一班复用请自行改路径或直接用文件名）。
  5. **禁烧面扩至四条**：P-1 的 9/6 面（三度同值）、修⑥ 的 52/49/22/30 面（两度同值）、`factor_signal`/`factor_feature_value` 各 0 行（三度同值）、census 轮次直方图 `{1:52,2:7,3:3,4:2}`（06 班直测）。本班全部**未重烧**。
  6. **claim 形制坑（新，本班自犯并当场修复）**：短命进程跑 `acquire-batch` 后，下一次 `lock_files.py check` 会把七个锁全判死并自动清理（锁 pid 随进程退出而死＝"锁存活=会话存活"字面执行）。正解＝`python .runtime/tmp/st-qoder-p09-1015-08/reg8.py && python scripts/lock_files.py acquire-batch <sid> --files-from <清单> --session <sid>` **串成一条命令**（注册 pid=0＋心跳在先），本班第二次 `acquired=7 denied=0`。
- 本班判卷面：增量 0 行；自检轮一＝rows[2]/[17]/[50] 回卡体，三行**门柱均未走样**（rows[17] 复证在册 P-1 的 nan 否决形；rows[50] 复证负向柱方向严格执行；rows[2] 的 `ic_ir` null 静默面属在册修⑥，未重烧）；轮二＝全 84 行 × 卡体 `card_id` join **84/84 命中**（卡池 549 件）。本班**零升级、新开单号 1 条（修⑪）＋呈批 1 条（P-5）**，未动分数册与判据字节。

- ⚑ **本班提交面两条（下一班必读，可省一次被拦）**：
  1. **堵点新形**＝`CLAIM-CHECK-BLOCKED: MESSAGE-CLAIMS-CODE-BAG-EMPTY`——提交消息里写了代码路径（本席写的是修⑪ 的证据指针 `card_binding.py`）而袋内零代码件即被拦。正解＝消息首行带 **`[docs-only]`** 显式申报（闸门自给的两选一之②）；**禁**把他人代码件塞进袋来"喂门"（＝归属篡改，且该件常在他席 claim 下）。
  2. **同会话两袋并存非静默取代**＝本班 `-0001` 与更正袋 `-0002` 同七件，队列打印 `[compaction] … 共享注册表路径不可信合并——拒绝压缩，两袋保留`（伴随一段 YAML `but found another document` 诊断，非致命）。⇒ 下一班按"后袋静默吃前袋"的在册预期去查四态会扑空；判本席袋面请**按 created_at 升序取末袋为严格超集**，并逐件比 `blob==disk`。本班实测 `-0001` 七件 `bag==disk=True`（`base_head=14f18f6271`）；`-0002` 为 ledger §10／checkpoint 本节的现值超集。

- ⚑ **更正（本班自犯，旧句留卷）**：台账 §10 曾写"本班跨出 40 分钟班限"＝错句（体感钟快一倍，落笔未回读 date）。实测起批 `09:55:40`→末袋 `10:27:28`＝班限内。另：`-0002` 只 6/7 件等于盘面现值（不载 checkpoint 补条），`-0003` 才是 7/7；下一班取"末袋为超集"的规则不受影响。

## 游标推进记录 ｜ st-qoder-p09-1015-09

- cursor: `exam_scores_v1.yaml#rows[89]`（**推进 6 行**，磁盘现值面 90 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **6 行**（rows[84..89]，批 `p07a-sector6-20261015`）＝**6 fail／0 pass**，100% 判卷、verdict 不可再现 0/6、门柱未走样；本班零升级（在册两枚 pass rows[76]/[78] 净面与 ic_ir 两腿本班复量仍未齐）
- 四证（本班终报前重测一次，与进场逐位同）：mtime `2026-10-15 10:31:26`／bytes `123768`／sha256 `009c7bbcf87582c29a7482842d545e6f50062f7fc436614c9326d04c04e38850`／`safe_load_all` docs=2、doc1 rows=**90**
- ⚑ 下一班必读事实（勿重查）：
  1. **读面**：磁盘 `009c7bbc…`（90 行）／index `c7e5b1f8…`（105598B／75 行，自 06 班起五班逐位同）／HEAD 该馆 **0 件**。index 用 `git show :<path>` 取字节。
  2. **修⑧ 恶化**：按精确路径携带本册的袋 **8 只**＝现值 90 行载袋 **3**（`q-20261015-st-qoder-p07-1015-03-0001`/`-03-0002`/`q-20261015-st-autoplan-20261015-0010`，blob `009c7bbc…`）＋**回退弹 5**（`-p07-1015-01-0001`=`24ef736d` 83 行、`-p07-1015-02-0001`/`-0002`=`4f986ec7` 84 行、`st-scorehome-0003`=`c14e6635` 74 行、`-0004`=`c7e5b1f8` 75 行）⇒ 回退弹由 3 增至 5。队列 counts（10:5x 本班读数）＝pending 125／processing 4／done 794／dead 146。
  3. **本席落地面仍为零**：`*p09*.json` 扫四态＝**15 只全 pending、done/dead＝0**（本班袋入袋后另计）。⚠ 判本席袋面按 `created_at` 升序取末袋为严格超集，并逐件比 `blob==disk`。
  4. **净/成本面已换代（S-8）**：rows[84..89] 六行 `net_bucket_medians` 非 NaN 且全负、`round_trip_cost_bp=25.0`；全册 has_pos＝**0**；存量 ≤rows[83] 净面 NaN ⇒ 跨批比较须按代分账。禁烧面：本班 `probe9_net_and_rerun.py` 四态分类（32/6/0/52）与 rows[76]/[78] 两腿读数（None＋净面全 NaN＋rt=nan）本班已直测，下一班勿重烧，除非册面 sha 变。
  5. **修⑫ 三形的在册锚**：桶数不一致行集＝**rows[72]/[84]**（nb=10 vs len(net)=4）；`min_obs_per_bucket` 在 `src`/`scripts` **0 命中**；影子键 `numeric_keys_bucket_caliber_proxy` 册面 **0 命中**、HEAD 码面 4 处、工作区面 0 处（他会话在途 +15/−62）。⚠ 取证请用**窄面** grep（`--include=*.py src scripts`），全仓 `grep -rn` 在 5383 脏件面超时。
  6. **在册单号现止于 修⑫／P-6**；`修⑩` 仍悬空（引用 1 次、无定义），comparison 族 rows[66..71] 请锚 **P-1＋修③**。
  7. 判卷尺复用＝`python .runtime/tmp/st-qoder-p09-1015-09/replay9_verdict.py 84 89`（改末两参换行段；含 oos_ok 一致性校验与 UNKNOWN_KEY 兜底）。本席尺对 `high_event`/`comparison` 两族的 fail 串柱名仍与卡体键不同名（06 班在册），新行落那两族须逐行回卡体。
- 本班判卷面：增量 6 行 100% 判卷；自检轮一＝rows[84]/[86]/[88] 回卡体（门柱未走样 3/3）；轮二＝全 90 行 × 卡体 `card_id` join **90/90 命中**＋08 班跨卡同读数尺复跑（cross_card_clusters 仍 6、正负对照均命中）。本班**零升级**、新开单号 **修⑫** ＋呈批 **P-6** ＋缺数待核 2 笔。
- 本班耗时：起批 `10:31:54` → `date` 实测 `12:27:31`（写盘前）＝**跨出 40 分钟班限约 1 小时 16 分**，如实登记（成因三笔见台账 §7）。


## 游标推进记录 ｜ st-qoder-p09-1015-10

- cursor: `exam_scores_v1.yaml#rows[93]`（磁盘面 94 行全判；本班增量＝rows[90..93] 共 4 行）
- last_run: 2026-10-15
- last_batch: 增量 4 行 100% 判卷（双臂尺＋校准尺双尺 PROBLEMS 0）；**3 fail／0 pass／2 blocked**（rows[90]/[91] blocked 不占 fail 分母）；本班零升级
- 本班实测面：判卷锚点快照 `d8a6fd8d52f749ce…`／129267B／rows=93（mtime 15:13:49）→ 写作期间又长至 `b0c9a370fcfc5b08…`／130320B／rows=94（mtime 15:41:28）⇒ **本班是在册首次出现"一班之内册面两代"**，下一班读面须以 `b0c9a370…` 之后为准；index 面 `009c7bbcf87582c2…`＝rows 90（＝09 班磁盘终面已入 index）；HEAD 面该馆仍 **0 件**。
- ⚑ 下一班必读事实（勿重查）：
  1. **对照族 OOS 从未判过**＝在册结论，尺＝`replay10_dualarm.py 0 92`（10/10 `ic_delta_oos` NaN，7 行唯一败根）。勿把这 7 行当"信号无效"分诊，勿重烧判卷。
  2. **在册尺 argv 无效**＝09 班 checkpoint"改末两参换行段"不实（`replay9_verdict.py:77` range 硬编）。本班新尺＝`replay10_calib.py <起> <止>`（校准路）＋`replay10_dualarm.py <起> <止>`（双臂路，含 blocked 行打印 reason 与卡面 `oos_window_ref`）。
  3. **取证纪律（本班自犯并当场更正）**：存在性判定**禁把多面命令用 `&&` 串**——本班首次 `ls docs/_working/fexam/ … && find … && git ls-files …` 因首段 `ls` 失败（该目录不存在）而**短路**，后两段从未执行，零输出被本席误读成"`find` 假阴性"；分面直读实测＝`find docs -name "*_exam_scores_v1.yaml"` **5 枚全命中**，且旧路径件只活在 `.aidrafts/<会话>/docs/_working/fexam/`（主树那份随 10-14 搬迁已删，新路径件 EXISTS 262360B）。零输出≠测得零命中。
  4. **卡 07 轮次＝7**（超 SOP §4 三轮上限，本班已撤该卡复考排程）；全册 94 行＝71 distinct card_id＝65 独立命题；轮次直方图 `{1:58,2:8,3:3,4:1,7:1}`。
  5. **禁烧面续条**（本班未重烧，下一班亦勿）：15 员池 PR 与 `factor_signal`/`factor_feature_value` 各 0 行（三度同值）；rows[76]/[78] 两腿读数（None＋净面 NaN＋rt=nan）；`ic_ir` 有实数＝4 行（rows[73]/[74]/[83]/[93]，4/4 记 FAIL）本班已直测。
  6. **在册单号现止于 修⑬／P-7**；`修⑩` 仍悬空（引用 1 次、无定义，本席未补写）。
  7. **考试在本班期内仍在飞**：缓存件 mtime `14:50–15:10`、册 mtime `15:13→15:41`；`commit_pct` 实测 `83.77%`（reaper --status），rows[91] 的 MemoryError 与同窗内存压力并见（本席未定因果，只登记同窗）。
- 本班耗时：起批 `15:15:49` → 写盘前 `15:5x`＝**跨出 40 分钟班限**（成因三笔见台账 §6）。

## 游标推进记录 ｜ st-qoder-p09-1015-11

- cursor: `exam_scores_v1.yaml#rows[95]`（**推进 2 行**；磁盘现值面 96 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **2 行**（rows[94] `TDM-P-P2-04/calibration/07` 第 1 轮、rows[95] `TDM-E-L9-A01/calibration/02` 第 2 轮），批 `p08b-1015-04-card07`＋`st-autoplan-verify-20261015`＝**2 fail／0 pass**，100% 判卷、两跑 PROBLEMS **0/0**、门柱未走样；本班**零升级**（在册两枚 pass 与 10 班快照逐行 byte-identical ⇒ 两腿仍未齐，未重跑）
- 四证（本班终报前重测）：mtime `2026-10-15 16:28:53`／bytes `132248`／sha256 `d77773545f5b4cc7…`（完整值见本班台账 §2 与本件正文）／`safe_load_all` docs=2、doc1 rows=**96**；⚠ **本班期内册面两代**＝进场 16:11:36 为 `8903ef9e9c731fdc…`／131320B／rows=**95**（mtime 15:55:38），下一班须以 `d77773545f5b4cc7…` 之后为准并**终报前重测一次**（S-3）
- ⚑ 下一班必读事实（勿重查）：
  1. **三面读数**：磁盘 `d77773545f5b4cc7…`（96 行）／index `git show :<册>`＝`009c7bbcf87582c2…`／123768B／**90 行**（＝09 班磁盘终面已入 index，落后磁盘 6 行／8480B）／HEAD 该馆 **0 件**。
  2. **落地链风险换形（修⑧ 追加面）**：旧面回退弹 `st-scorehome-20261014-0001..0007` **全在 dead**（`REGISTRY-MASS-DELETION`×1／`TAKEOVER-PENDING`×1／`ghost_session`（裁定#459）×5）；`pending/` 现仅 **1 袋**＝`q-20261015-st-qoder-p07-1015-04-0003`（1 件，**不载**分数馆）⇒ **现值 96 行无任何在途载体袋**，唯一存活处＝主区工作树。下一班**勿再按"某只旧袋先落地即回退"叙事呈报**，该威胁已由死信终结；新叙事＝"无人投＋HEAD 0 件"。
  3. **本席袋四态换代**＝`*p09*` 扫四态＝**17 dead＋1 done**（唯一落地＝`q-20261015-st-qoder-p09-1015-09-0002`，7 件）。死因二族＝`ghost_session`×9（02/03/06/07/10 班）＋`landing 异常: 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）`×8。⇒ 09/10 班在册"全 pending、done/dead=0"已过期。**本席未 requeue**：requeue 须先修因，而"活袋投出即随收班而死"要 ⑩/统筹定策（本席不自裁）。
  4. **在册尺面新增**：`ic_ir` 有实数 **6 行**（rows[73]/[74]/[83]/[93]/[94]/[95]，6/6 FAIL）；panel 且冻 `mono_spearman_min` **6 行**（同行集，mono 6/6 None）；三处同号负向簇 **10 行／7 卡**（谓词＝`ic_mean<0 且 oos_ic<0 且 regime 有效段全负`）；`oos_same_sign` 冻柱 **73 行**／两侧实数咬合 **61 行**／fails 含 oos **40 行**／该柱披露无面 **0 行**；全册 verdict 分布 `fail 92／pass 2／blocked 2`；96 行＝72 distinct card_id，hist `{1:58,2:9,3:3,4:1,7:1}`，"独立命题 66"＝**派生**（72−6 对平行卡）非直测。
  5. **窗分母（修⑮ 用，勿重算）**＝`c1_market.kline_daily_hfq` `count(DISTINCT trade_date)`：IS `2019-01-04..2023-12-31`=**1212**、OOS `2024-01-01..2026-09-30`=**666**、并集=**1878**（正对照 `SELECT 1`→`[(1,)]`）；rows[93]/[94] 册面 `n=1859`。
  6. **在册单号现止于 修⑮／P-8**；`修⑩` 仍悬空（引用 1 次、无定义，本席未补写）。comparison 族 rows[66..71] 真源锚仍＝**P-1＋修③**；双臂路尺＝`replay10_dualarm.py <起> <止>`（09 班 checkpoint"改末两参"对 `replay9_verdict.py` **不实**，沿 10 班在册）；校准路尺＝`replay10_calib.py <起> <止>`。本席尺对 `high_event`/`comparison` 两族 fail 串柱名与卡体键不同名（06 班在册），新行落那两族须逐行回卡体。
  7. **命名撞车（每班易犯）**：10 班在册"卡 07 已 7 轮、撤排"指 `TDM-X-R1-01/comparison/**07**_熔断五级…`（rows[90..92]）；本班 rows[94] 是 `TDM-P-P2-04/calibration/**07**_冲高反弹…`（第 1 轮）。两个"07"勿并读。
  8. **禁烧面续条**（本班均未重烧）：15 员池 `factor_signal`/`factor_feature_value` 各 0 行（三度同值）；rows[76]/[78] 两腿（本班改用 byte-identical 对表替代重跑）；pool6 PR=2.1272（本班同池重跑＝复现确认，非新读数）；修⑥ 申报面 52/49/22/30。
- 本班判卷面：增量 2 行 100% 判卷；轮一＝rows[94]/[95]/[92] 回卡体（门柱未走样 3/3，含双臂 PROBLEMS 0）；轮二＝96 行 × `card_id` join **96/96**（卡池 550）。本班**零升级**，新开＝**修⑭＋修⑮＋〔对照〕1 条＋呈批 P-8**，缺数单**零新开**，方向单 2 条＋告警 1 条。
- 本班耗时：起批 `16:11:36` → 写盘前 `date` 实测 **≈65 分钟＝跨出 40 分钟班限**（成因三笔见台账 §8）。
- ⚑ 本班自犯并当场更正：§5 路由首稿把 rows[95] 写成"首轮新对象"，与尺打印"该卡 2 行"矛盾 ⇒ 正解第 2 轮，已同步改写迭代史与 to_miners（旧句在此留痕）。

- ⚑ **本班耗时句更正（旧句留卷）**：上行"≈65 分钟＝跨出班限"为落笔前估算，非 date 实测。实测＝起批 `16:11:36`→七件写盘 `date 16:41:35`＝**30.0 分，班限内**；提交段另计。

- ⚑ **本班提交面（终报补条）**：首投 `16:44:19` 被 `[WORKTREE-REQUIRED]` 拦（rc=8，锁外预检 18.3s）→ 按在册加 `--allow-non-worktree` 显式申请制重投；袋 `q-20261015-st-qoder-p09-1015-11-0001`（files=7／created 16:46:01／base_head 63a5ee4c66）；**blob↔磁盘对拍 7/7 通过**（尺坑两枚已更正：袋面键名真名 `blob_sha256` 非 `sha256`；`blob_ref` 相对队列根 `.runtime/commit_queue` 非 CWD）。消息首行 `[docs-only]`。本节随 **`-0002`（严格超集七件）** 入袋，下一班取末袋 `-0002`。生死风险：本席今日 17 袋里 9 死於 ghost_session（存活闸拒自动重投），本席未自跑全队列 drain（会连带落他人袋＝共享态），若本班袋亦入 dead 请按台账 §10 修因方向处置，不自裁。

- ⚑ **本班袋 `-0001` 落地段死亡（§10 落笔时未知，旧句留卷）**：`dead_reason`＝`landing 异常: 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/automation_campaign/feedback/to_impl.md`；机制实测＝本班建袋（base `63a5ee4c66`）后 ④席袋 `429b9327e8` 落地并**同携 to_impl＋to_datasource** ⇒ 双侧皆改。末袋 `-0002`（16:49:18）`base_head` 已取落地后新 HEAD `429b9327e8`、袋侧＝现磁盘面（含 ④席块）属"仅袋改"；`-0003` 携本节。本席 `-0001` **不 requeue**（内容与末袋同面，无抢救缺口）。下一班若见 `-0002/-0003` 同签名再死，正解＝**取基必须等于落地后 HEAD**，非重烧内容；该串行化方向属 ⑩/统筹写域，本席未代裁。

## 游标推进记录 ｜ st-qoder-p09-1015-12

- cursor: `exam_scores_v1.yaml#rows[95]`（**不变**，磁盘现值面 96 行全判；本班增量 0 行）
- last_run: 2026-10-15
- last_batch: 当日增量 **0 行**。四证（进场＋终报前各测一次，逐位同 11 班终报锚点）：mtime `2026-10-15 16:28:53`／bytes `132248`／sha256 `d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c`／`safe_load_all` docs=2、doc1 rows=**96**
- ⚠ **本班修复 11 班遗留的顶部游标头尾分叉**：本件顶部 `cursor` 段自 10 班写死 `rows[93]／10 班在册`，而 11 班详情节已推进 `rows[95]` 却未回写顶部 ⇒ 本班把顶部对齐真实锚点 `rows[95]／12 班在册`（旧句留痕）。
- ⚑ 下一班必读事实（勿重查）：
  1. **三面读数**：磁盘 `d77773545f5b4cc7…`（96 行）／index `git show :<册>`＝`009c7bbcf87582c2…`／123768B／**90 行**（自 11 班起未动，落后磁盘 6 行／8480B）／HEAD 该馆 **0 件**。下一班锚点＝`d77773545f5b4cc7…` 之后，只判 rows[96] 起新行；终报前重测一次（S-3）。
  2. **提交面纪律换形（本班新立）**：增量 0／零新开单的班**只投本班会改的件**，不随袋投 `to_impl/to_miners/to_datasource`（该三件盘面 `MM`、含 ④席经 `429b9327e8` 已落块＝随袋即归属篡改）。判据＝`git diff --numstat HEAD` 对拟投件须纯增或空。08/11 班"每袋带全 7 件"仅在**有新单**时适用。
  3. **首份族×verdict 分账（尺＝`.runtime/tmp/st-qoder-p09-1015-12/measure12.py`，只读）**：校准 61／事件 23／对照 11／maxdd_min 变体 1；pass 唯 2 且全在校准族同一根 `lu_count_z20` 轴；事件族 23 行 0 pass、对照族 11 行 0 pass。禁按路径段分族（03 班在册假红）。
  4. **在册尺续**：`replay10_calib.py <起> <止>` 跑校准族、`replay10_dualarm.py <起> <止>` 跑双臂；校准尺对事件/对照族报 UNKNOWN_KEY＝族盲假红（本班实测 calib 跑 0..95＝PROBLEMS 25，跑校准族 61 行＝**PROBLEMS 0**）。
  5. **在册单号现止于 修⑮／P-8**；`修⑩` 仍悬空（引用 1 次无定义，本席未补写）；comparison 族 rows[66..71] 真源锚＝P-1＋修③。
  6. **禁烧面续条**（本班均未重烧）：15 员池 `factor_signal`/`factor_feature_value` 各 0 行（三度同值）；rows[76]/[78] 两腿（册面 sha 未变⇒未重测）；pool6 PR=2.1272（本班同池重跑＝复现，非新读数）；`reaper commit_pct` 本班冷启动实测 `94.79` 属内存高压面，本班未跑全仓 `git status`。
- 本班判卷面：增量 0 行；轮一＝rows[0]/[44]/[46] 回卡体（门柱未走样 3/3）；轮二＝census11 join 96/96＋calib 校准族 PROBLEMS 0。本班**零升级、零新开单号、零呈批、零对照、零缺数单**，未动分数册与判据字节。
- 本班耗时：见台账 §6（起批 reaper 锚点 `16:57:37`）。

## 游标推进记录 ｜ st-qoder-p09-1015-13

- cursor: `exam_scores_v1.yaml#rows[95]`（**不变**，磁盘现值面 96 行全判；本班增量 0 行）
- last_run: 2026-10-15
- last_batch: 当日增量 **0 行**。四证（进场 17:35＋写盘前各测一次，逐位同 12 班终报锚点）：mtime `2026-10-15 16:28:53`／bytes `132248`／sha256 `d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c`／`safe_load_all` docs=2、doc1 rows=**96**
- ⚑ 下一班必读事实（勿重查）：
  1. **三面读数**：磁盘 `d77773545f5b4cc7…`（96 行）／index `git show :<册>`＝`009c7bbcf87582c2…`／123768B／**90 行**（自 11 班起五班逐位未动）／HEAD 该馆 **0 件**。下一班锚点＝`d77773545f5b4cc7…` 之后，只判 rows[96] 起新行；终报前重测一次（S-3）。
  2. **本班主产出＝事件族 OOS 确认柱"可达性"首份账（在册单号现止于 修⑯／P-9）**：卡面 OOS 窗 23/23 同为 `2024-01-01..2025-09-09`＝**410 交易日**，族内下限 200 事件日同时套该确认窗（`scripts/backtest/fexam/calibration_exam.py:843`、`:872-875`，反号判定仅在 `oos_n>=floor` 分支＝`:877-881`）⇒ 需密度 **48.8%**，实测 19.3%–40.2%（`oos.n_event` 79–165）＝**0/23 可达**；IS 侧 239–363（23/23 过线）。**下一班勿把事件族 23 行当"信号无效"分诊，亦勿自行改 floor（判据面＝P-9 待裁）**。
  3. **在册尺新增（全只读、内置正负对照）**：`python .runtime/tmp/st-qoder-p09-1015-13/measure13d.py`（符号×柱触发 cross-tab＋窗下限分账）／`measure13b.py`＋`measure13c.py`（同卡复跑四类分账）。校准族 61 行 cross-tab＝**翻号&触发 30／同号&未触发 31／另两格 0／0**（61/61 咬合）；同卡复跑"窗同桶同读数变"＝**0**。
  4. **⚠ 本班自犯并当场推翻的假红（形制在册）**：`metrics["oos"]`（事件族）是**嵌套 dict**（含 `n_event/n_none/mean_event/mean_none/gap_bp/t_stat`），按"是否标量实数"判会得"**23/23 无面**"＝**类型盲假红**（旧句留卷于台账 §8）。正解＝取 `oos.gap_bp`／`oos.n_event`。下一班凡碰事件族 OOS 面**必须按嵌套键取**。
  5. **判据换代留痕（修⑯ 形一）**：rows[41]/[42]/[43]（date 10-11）fails 引 `oos_gap 反号` 而 `oos.n_event`=104/81/79<200＝现行码面不可能产出；两串 fail 文案同源于 commit `ed5e59c2890`（`git log -S` 各恰 1 命中）⇒ 册面无版本锚，跨代不可比。下一班引用事件族 OOS 侧须分两代。
  6. **禁烧面续条**（本班均未重烧）：15 员池 `factor_signal`/`factor_feature_value` 各 0 行（三度同值）；rows[76]/[78] 两腿（册面 sha 未变）；pool6 **PR=2.1272**（本班实跑＝复现，非新读数）；双臂行 `ic_delta_oos` 0/10 实数（复现 10 班在册）；`ic_ir` 有实数 6 行。
- 本班判卷面：增量 0 行；轮一＝rows[48]/[55]/[60] 回卡体（`spot12.py` 在册尺原样跑，门柱未走样 3/3）；轮二＝96 行 join **96/96**＋校准族 cross-tab 61/61 咬合＋双臂 0/10 复现。本班**零升级、零方向单、零缺数单、零对照单**，新开＝**修⑯＋呈批 P-9＋修⑫ 追加面**，未动分数册与判据字节。
- 本班耗时：起批 reaper 锚点 `17:35:49` → 写盘/提交段实测见台账 §9 与提交补条（按在册纪律以落笔前现测 `date` 为准）。


## 游标推进记录 ｜ st-qoder-p09-1015-14

- cursor: `exam_scores_v1.yaml#rows[95]`（**不变**，磁盘现值面 96 行全判；本班增量 0 行）
- last_run: 2026-10-15
- last_batch: 当日增量 **0 行**。四证（进场 18:00＋终报前各测一次，逐位同 13 班终报锚点）：mtime `2026-10-15 16:28:53`／bytes `132248`／sha256 `d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c`／`safe_load_all` docs=2、doc1 rows=**96**
- ⚑ 下一班必读事实（勿重查）：
  1. **在册单号现止于 修⑲／P-9**（本班新开 修⑰＋修⑱＋修⑲；`修⑩` 仍悬空＝引用 1 次无定义，本席未补写；P 系列本班零新开）。
  2. **blocked 两行的根因已量到链条级**＝rows[90] 走 `card_binding.py:1761` → `exit_simulator.py:122 load_indicator` → 旧址 `SCORES_YAML`；rows[91] 属资源面同窗（本班复量 `commit_pct=94.68`）。**两行均禁按"信号无效"分诊、禁作 fail 升降级**（本版对照族说明）。
  3. **断链分面已出账（修⑱/修⑲）**＝84/552 卡含已删 `docs/_working/**` 引用、覆盖 39/96 行，但**机器字段命中仅 3 卡、执行阻断仅 1 行**；引用集中在 `status_reason/mother_score_row/data_window_evidence/same_family_precedent/basis_casefile/paper_trail`。下一班**勿把 40% 册行判成废**，也勿重烧该尺。
  4. **在册尺新增（全只读、内置三对照）**＝`python .runtime/tmp/st-qoder-p09-1015-14/measure14.py`（A join／B 轮一回卡体／C 册内旧址引用判存）＋`measure14b_cards.py`（卡面断链面积）＋`measure14c_keyface.py`（键级分面）。
  5. **门柱走样核查的正解形制（本班实测出）**＝fail 串文案名 ≠ 卡体声明键名，须查到**发射点守卫的键**才可判"未走样"：`calibration_exam.py:623 if p.get("oos_same_sign")` → `:626/:628` 发 `oos_sign_flip`。沿 06 班"两族 fail 串柱名与卡体键不同名"在册，但**不接受它当结论**（否则抽一行就误判门柱走样）。
  6. **OD-1 执行器三面分叉复证**＝`comparison_exam.py` HEAD 无／index 无／磁盘 `??`（`book_channel:` 唯一发射点 `:270/:274/:277`）；`signal_orthogonality.py`＝index 有／HEAD 无（`AM`）。⇒ 从 HEAD 起跑两者皆不存在；本班跑的是磁盘面。
  7. **禁烧面续条**（本班均未重烧）：15 员池 `factor_signal`/`factor_feature_value` 各 0 行（三度同值）；rows[76]/[78] 两腿（册面 sha 未变）；pool6 **PR=2.1272**（本班实跑＝复现，非新读数）；双臂 `ic_delta_oos` 0/10；`ic_ir` 有实数 6 行；`ART_ROOT`。
- 本班判卷面：增量 0 行；轮一＝rows[76]/[78]/[66] 回卡体（门柱未走样 3/3，含发射点 file:line 直查）；轮二＝96 行 join **96/96**＋卡池 552。本班**零升级**，新开＝**修⑰＋修⑱＋修⑲**，方向单／缺数单／对照单／呈批**皆零新开**，未动分数册与判据字节。
- 本班耗时：起批 `date 18:00:09`／reaper 锚点 `18:00:18`；终值见台账 §9 与提交面补条（落笔前现测，不写预估）。


## 游标推进记录 ｜ st-qoder-p09-1015-15

- cursor: `exam_scores_v1.yaml#rows[103]`（**推进 8 行**；磁盘现值面 104 行全判）
- last_run: 2026-10-15
- last_batch: 当日增量 **8 行**（rows[96..103]，`run_id=st-qoder-p07-1015-06`）＝**8 fail／0 pass**，100% 判卷、`replay10_calib.py 96 103` **PROBLEMS 0**、门柱未走样；本班**零升级**
- 四证（本班终报）：mtime `2026-10-15 19:26:44`／bytes `139777`／sha256 `21ce93c0a55c450e969ac177d6378329f4275e887c5e93b63f0bcd3a08928f23`／`safe_load_all` docs=2、doc1 rows=**104**
- ⚑ 下一班必读事实（勿重查）：
  1. **本班值守内册面三代**＝进场 18:52:30 `d77773545f5b4cc7…`（96 行）→ **19:04 整馆目录从磁盘消失**（FileNotFoundError＋父目录不存在）→ 19:07:25 回灌 `21ce93c0a55c450e…`（104 行）。根因＝19:00:01 一枚 **5688 件 `git stash`**（身份 `lane <lane@local>`，基底 dev@`9d94f57219`，commit `fd1eaffebc`）扫走 30 件分数馆；**该 stash 至今未 drop、`stash_notice.json` 未更新（mtime 仍是 10-11 23:39）**。本席两件无损防护＝`refs/recover/p09-scorehouse-20261015 → fd1eaffebc` ＋ 整馆 30 件快照 `.runtime/tmp/st-qoder-p09-1015-15/scorehouse/`（956K）。⇒ 下一班**判"件查无"前先 `git stash list`**（在册三面尺在该窗内全给绿灯）。
  2. **三面读数**＝磁盘 `21ce93c0a55c450e…`（104 行）／index `70c71e7b139780f9…`＝**97 行**（恰＝stash WIP 面，落后磁盘 7 行）／HEAD 该馆 **0 件**。下一班锚点＝`21ce93c0a55c450e…` 之后，只判 rows[104] 起新行；终报前重测一次（S-3）。⚠ 若有人在主区 pop 该 stash，册面会**按回 97 行**＝新型回退弹，已呈 ⑩（修⑳）。
  3. **本班新开**＝修改单 **修⑳**（全域 stash 清面·未 drop 无 notice）＋**修㉑**（四张对照卡只产出 2 个读数面：rows[96]≡rows[97] 整块 metrics 相等；两枚 target 腿卡读数落在对侧血统量级；四卡顶键集**无 `universe` 顶键**）＋**修⑯ 追加面**（形三＝行内无臂身份锚）。零方向单／零缺数单／零对照单／零呈批。在册单号现止于 **修㉑／P-9**；`修⑩` 仍悬空（引用 1 次无定义，本席未补写）；comparison 族 rows[66..71] 真源锚仍＝P-1＋修③。
  4. **在册尺面更新（本班直测，禁重烧）**＝`cross_card_clusters` **6→7**（尺＝`.runtime/tmp/st-qoder-p09-1015-08/dup8_metrics_identity.py` 跑现值面，正/负对照均命中）；`ic_ir` 有实数 **14 行** [73, 74, 83, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103]；panel 且冻 `mono_spearman_min` **14 行**（同行集，mono 全 None，沿 修⑭）；同号负向簇 **17 行／14 卡**；全册 verdict `{'fail': 100, 'pass': 2, 'blocked': 2}`；104 行＝80 distinct card_id，hist `{1: 66, 2: 9, 3: 3, 4: 1, 7: 1}`；卡池 553；join 104/104。
  5. **在册引用路径更正**＝双臂装置真路径 `scripts/backtest/fexam/**exit_sim**/exit_simulator.py`（在册多处只写 `exit_simulator.py:72/:122`，缺子包名）。修⑰ 前置位移实测＝磁盘面 `:72-74` 已指 04 永久区＋`load_pass_columns` 已带双文档兼容，**HEAD 面仍指 10-14 已删旧址**（`git diff --numstat HEAD`＝12 增 4 删、未 staged）；写侧 `:77-78` 未修（`docs/_working/fexam` exists=False 本班直读）。⇒ rows[90] 之堵在**落地面仍未解除**，下一班勿按"已修"呈报。
  6. **禁烧面续条**（本班均未重烧）：15 员池 `factor_signal`/`factor_feature_value` 各 0 行（三度同值）；rows[76]/[78] 两腿（未重跑）；pool6 **PR=2.1272**（本班实跑＝复现，非新读数）；双臂 `ic_delta_oos` 0/10；`ART_ROOT`。
- 本班判卷面：增量 8 行 100% 判卷；轮一＝rows[96]/[98]/[92] 回卡体（校准尺＋双臂尺各原样跑，PROBLEMS 0／0）；轮二＝104 行 × `card_id` join **104/104**＋跨卡簇尺复跑（6→7）。本班**零升级**，新开＝**修⑳＋修㉑**＋修⑯ 追加面，方向单／缺数单／对照单／呈批**皆零新开**。
- ⚠ 本席纪律声明：未动分数册与任何判据字节；本席**唯一 git 写动作＝新增 `refs/recover/p09-scorehouse-20261015`**（纯增 ref，可 `git update-ref -d` 撤销），未 pop／未 drop／未 checkout／未复位任何面。
- 本班耗时：起批 `18:52:04` → 写盘 `date 19:30`（终值见台账 §9 与提交面补条）。

- ⚑ **本班补条（19:31 实测，旧句留卷）**：§3 与迭代史的"rows[100]/[101]/[102] 三行／三枚"系手打旧行段，正解＝**非对照四枚＝rows[100..103]**；`replay10_calib.py 96 103` 本班已**原样实跑**＝`PROBLEMS 0`（八行 verdict 全再现）。rows[100] 是 **`ablation` 族**卡（路径段 `/ablation/`），校准尺对其 `UNKNOWN_KEY` 为空＝**同词表，下一班勿另立尺、勿按族盲改判**。补条时点册面 sha `21ce93c0a55c450e…`／rows=**104**（未再增长）；本班游标锚点仍是 `rows[103]`，下一班只判 rows[104] 起。

- ⚑ **本班提交面终值（落笔后补）**＝首投 `19:32:08` 被 `[SESSION-REQUIRED]` 拦（预检 55.9s，同段 `git diff --cached` 撞 15s 超时）→ 重注册后原命令重投 → `19:37:25` **`ENQUEUED q-20261015-st-qoder-p09-1015-15-0001`**（files=6／base_head `118ace7c71`／created 19:37:19／消息首行 `[docs-only]`）；**blob↔磁盘对拍 6/6 OK** 且袋内取的是**含本班 §11 补条之后**的现值面。耗时终值＝`18:52:04`→`19:37:25`＝**45.4 分＝跨班限约 5 分**（三笔成因见台账 §12）。如实申报＝本袋 `to_impl.md` 面含 ⑤席 `st-qoder-p05-1015-06` 未落地自署节 28 行（纯增 0 删、归属在文件内自带，本席未改一字）。本班未 release 在飞锁、未 requeue、未 pop/drop 该 stash。

- ⚑ **袋链终态补条（19:41）**＝两袋并存（compaction 拒合并，签名与 08/11 班同）；`-0001` 对拍 **4/6**（`ledger`／`checkpoint` 成袋后被外部推进，其 ledger 面**不含**外部 `[BLOCKER]` 行）⇒ **`-0001` 对这两件已属回退弹**，按它落地会抹掉外部 1 行＋本席 §12；本席不 requeue、不撤袋，呈 ⑩ 按"在途字节变回退弹→让它死"方向处置。`-0002` 对拍 **6/6** 且系 `-0001` 严格超集（内容级零抢救缺口）；本节随 `-0003` 入袋。下一班读四态请**按 created_at 升序取末袋**并逐件比 `blob==disk`。


## 游标推进记录 ｜ st-qoder-p09-1015-16

- cursor：`exam_scores_v1.yaml#rows[103]`（**本班未推进**＝当日增量 0 行，104 行全判状态延续 15 班）。
- last_run: 2026-10-15
- last_batch：当日增量 **0 行**（两时点同值：起批 `19:46:43` 首测与写盘前 `20:09:35` 复测＝磁盘 sha `21ce93c0a55c450e…`／139777B／104 行／mtime `19:26:44` 未变；index 面 97 行（133214B）、HEAD 该册不在库）。本班**判卷对象为空集**，主产出＝种子 [BLOCKER] 三口径实读账＋两条落地面红旗。
- 本班交接事实（下一班必读，勿重查）：
  1. **ic_ir 柱覆盖面已钉**＝冻柱行 69／机判 14（rows={73, 74, 83, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103}）／无面 55（有披露 25＋静默 30）。⚑ 无面行其余柱面数分布＝`{4: 55}`（**全为 4**）⇒ **非"近似单脚"，是"四脚缺一脚"**，缺柱只放宽不放严，受影响判语面＝唯二 pass 行 rows[76]/[78]。尺＝`.runtime/tmp/st-qoder-p09-1015-16/measure16_icir_coverage.py`（负对照 typo 键→0 命中、正对照 mono 柱→69/55/79.7%）。**下一班勿照抄"52/3/5.8%"或"55 行作废"。**
  2. `scripts/backtest/fexam/calibration_exam.py` **三面无一可用**＝磁盘+index 1069 行（缺 10-14 13:52 已落 HEAD 的 PE 止血闸，净 −47 行）／HEAD 1116 行而 `SCORES_PATH` 仍指 10-14 已删旧址；该件 FREE 无 claim、mtime 19:06:00 落在 15 班在册全域 stash 窗内。`scripts/backtest/fexam/comparison_exam.py` 仍未跟踪＋两本热册登记行 HEAD=0＋本班扫 pending/processing 全袋命中载体 **0** 只。
  3. 15 班三袋本班复量＝`-0001`/`-0002` processing 且对 `ledger`/`checkpoint` 两件 **blob≠disk（回退弹）**、`-0003` pending 六件 **blob==disk** ⇒ 四态读数按 `created_at` 升序取末袋并逐件比字节（沿 15 班在册）。
  4. 15 班心跳 mtime 实测停在 `19:40:37`（本班 `getmtime` 直读）而种子 [BLOCKER] 行已在 `-0003`（created 19:42:48）的 ledger blob 内 ⇒ 该行**署名"Owner 裁"在 ruling_registry 查无**（词表 判据面补全／机判检验 三词 0 命中），在册最接近者＝03 馆 D10 批文明示"本裁定不修尺"⇒ 本班按**未裁**处理并开 P-10 草稿。
- 下一班锚点＝游标仍 `rows[103]`，只判 rows[104] 起的新行；⚠ 全域 `stash@{0}` 未 drop 前回灌风险在册（修⑳），行数骤降先查 `git stash list` 与 `refs/recover/p09-scorehouse-20261015`，勿判"成绩已丢"。
- 本班耗时：起批 `19:46:43` → 写盘 `20:09:35`（班中续 claim `20:07:23`，acquired=4 denied=0）；提交面终值落笔后补。


## 游标推进记录 ｜ st-qoder-p09-1016-01

- cursor: `exam_scores_v1.yaml#rows[107]`（**推进 4 行**；磁盘现值面 **108 行全判**）
- last_run: 2026-10-16
- last_batch: 当日增量 **4 行**＝rows[104]/[105]（`run_id=st-qoder-p07c-1016-01`，本班起批时点已在册）＋rows[106]/[107]（`run_id=st-qoder-p07c-1016-02`，本班值守内 22:09:54 新出）＝**4 fail／0 pass**，100% 判卷；在册尺**正文原样实跑** `replay10_calib.py 104 105` 与 `replay10_calib.py 106 107` 末行均 **PROBLEMS 0**、门柱未走样；本班**零升级**
- 读数四证（本班三时点，实测非推算）＝`21:52` 磁盘 sha `05bc7ce014f204a0…`／141704B／**106 行**／mtime `15:49:46`（此刻 **index==HEAD==磁盘**）；`22:11` 写盘前复测同值；`22:12:21` 复测磁盘 **`bb557705beea260f…`／143510B／108 行／mtime `22:09:54`**，index==HEAD 仍 **106 行**（`git status`＝` M`，`git diff --numstat HEAD`＝**67 增 0 删**）。⚑ 结论＝**"该册已在 HEAD"是换代事实**（经 `e1033fb48d` 10-16 03:14 保护性入库＋`98410ca45f` 16:17 ⑦c 袋），**"三面同值"只是瞬时条件**，⑦c 出分与正门落地都单边推进磁盘面 ⇒ 下一班勿把同值当常备绿灯。
- ⚑ 下一班必读事实（勿重查）：
  1. **在册"该册不在 HEAD／唯一存活面＝磁盘／判落地只认 `git log -1 -- <册>`"判据今日作废**；但**"行数骤降先查 `git stash list`"必须保留**（全域 `stash@{0}` 未 drop；本班 reaper 现读 `stash_count=30`／`worktree_changes=1686`）。⚠ ⑩ 1016-05 在册令"③④席任何班不要把该册放进袋"仍有效，本席亦从未随袋带该册（本班袋内只有自家四面）。
  2. **本班新开＝修㉔＋P-11**（在册单号此前止于 修㉓／P-10；`修⑩` 仍悬空＝引用 1 次无定义，本席沿 14–16 班未补写）。修㉔＝`scripts/backtest/fexam/calibration_exam.py` 的 **PE 止血闸被 `1c79317949` 整档快照落地净删 47 行**（`_bucket_caliber_proxy` 4→0、`_bucket_type_off_vocab` 2→0、行数 1115→1068；该 commit 消息只述"分数册双文档读写兼容"），16:48 补齐袋 `8caf2743b9`（`#ARCH-383`，96 增 1 删）**未恢复**；**现值受影响面＝0 行**＝披露键 `numeric_keys_bucket_caliber_proxy` 全册 108 行**零命中**（正对照＝同尺读 `numeric_keys_no_machine_face` 命中 75；负对照＝typo 键 0）。⇒ 定性＝功能净删（治理／落地事故），非读数污染；**上界 55 行勿当事故面积**（谓词与世代账见 ledger §3(2)）。
  3. **修㉒/修㉓ 今日收口读数（实测）**＝`calibration_exam.py` 的 `SCORES_PATH`→04 腿**已在 HEAD**（本班直读 `:60`；磁盘==HEAD，`git hash-object`＝`91937c098a3d…`；**index 面 1115 行仍指 03 旧址且含 PE 4 命中**＝落后一版，属在册"正门落地后主区 index 停在落地前一版"形态，**勿代复位**）；`comparison_exam.py`／`signal_orthogonality.py` **已落 HEAD**（三面逐字节同＝`04682070c42a…`／`a8a760ae0883…`，`git status` 干净）⇒ 14/15/16 班"从 HEAD 起跑两工具不存在"红旗**解除**。
  4. **在册尺面更新（本班直测，替换 16 班账）**＝rows **108**／distinct card_id **84**／verdict `{'fail':104,'pass':2,'blocked':2}`／轮次直方图 `{1:70,2:9,3:3,4:1,7:1}`／卡池 **553** 件＝553 distinct、join **108/108**；`ic_ir` 冻柱 **73**／机判 **18＝24.7%**／无面 55；panel 且冻 `mono_spearman_min` 无面 **18 行**（行集与 `ic_ir` 有实数 18 行**逐位同**＝rows{73,74,83,93,94,…,107}）；同号负向簇 **18 行／谓词沿 15 班**（rows[104]/[106]/[107] 皆正号不入）。⚑ **"五柱全有面"的行＝0**（缺面计数 ic_ir 55／mono 18／regime 1／oos 2）＝P-11 量化底座。
  5. **署名/裁定面红旗（本席按未裁续记）**＝台账末行 `[BLOCKER] 2026-10-16|p09（更正行·Owner 裁定三）` 重述"52/3/5.8% 以本条为准"，而 `ruling_registry.yaml` **盘==HEAD==5025 行**、`ruling_id` 最大值**两侧都＝#534**、`#537-539` 与 `ARCH-383` **两面 0 命中**、该册最后 commit＝`5fbfbc3add`（10-14 21:37）⇒ **停发解除裁定在治理面不成立**（比 ⑩ 1016-19 班时点更严：那班盘上尚有 +94 行，本班连盘面也没了＝热册蒸发复证）。本席据"判落地只认 git/blob"继续**零方向单**；蒸发面已入本班 [BLOCKER]（要 ⑫/⑩ 走 chief staging 救援件 blob `c5c67013`/`87af5b43`）。
  6. **在册禁烧面续条**（本班均未重烧）：15 员池 `factor_signal`/`factor_feature_value` 各 0 行（本班未第四次重烧）；pool6 **PR=2.1272**（本班 `22:01:33` 实跑＝复现，非新读数）；`ART_ROOT`；rows[90]/[91] 两枚 blocked（在册分诊沿用，禁按"信号无效"、禁作 fail 升降级）；双臂行 `ic_delta_oos` 0/10 实数；rows[76]/[78] 未重跑（仅 `replay10_calib.py 76 76` 尺读，未考试）。
- **本班判卷面**＝增量 4 行 100% 判卷（四枚皆 fail）；轮一＝`replay10_calib.py 104 105`／`106 107`／`76 76` 三条**原样实跑**，末行均 **PROBLEMS 0**（含 pass 行可再现＝尺的能绿性自证）；轮二＝108 行 × `card_id` join **108/108**＋正/负对照齐备（ledger §8 与 §11）。本班**零升级**，新开＝**修㉔＋P-11**，方向单／缺数单／对照单／呈批（除 P-11 草稿）**皆零新开**。
- ⚠ 本席纪律声明＝未动分数册与任何判据字节；未 commit 任何他人代码件；未复位 index；未 pop/drop/清任何 stash；**零 worktree**（TRAE-079 Phase 2 遵令，未调用任何工棚/工作树入口）。
- **本班耗时**＝起批 `date 21:50:13` → 写盘段实测 `NOW=22:15:24`（iter 面末次追加）；提交段终值（袋号/files/base_head/对拍）由下方"提交面补条"按实报，**禁预写未发生的读数**。

- ⚑ **班尾补条（22:33–22:35 实测，旧句留卷）**＝册面再长 1 行＝`rows[108]` `TDM-E-L3-05/calibration/02_连板顺位`（`run_id=st-qoder-p07-1016-02`＝⑦A 席 02 班）⇒ 当日增量 **5 行全判**、游标改推 **rows[108]**；`replay10_calib.py 108 108` 原样实跑末行 **PROBLEMS 0**（`ic_ir −0.469`／`ic_mean −0.0211` 两柱独立 fail，oos/regime 同号负）＝四段同号负，进同号负向簇 **18→19 行**；全册现值 rows **109**／distinct **85**／verdict `{fail:105,pass:2,blocked:2}`；`ic_ir` 冻柱 74／机判 19（席位 16＋非席位 3＝21.6%，通道分面口径见 ledger §13）／mono 无面 19；"五柱全有面"仍 **0 行**。下一班读面＝`682ab7cf437164b4…` 之后，只判 rows[109] 起。


## 游标推进记录 ｜ st-qoder-p09-1016-02

- **本班游标＝`rows[109]`**（上一班止于 `rows[108]`）；当日增量＝**1 行全判**（`rows[109]` `TDM-X-S1-04/calibration/02_突破失败连续次数前瞻收益`，`run_id=p08b-1016-02-x-s1-04-02`＝⑧b 席，`verdict=fail`，判卷全文＝本席台账 1016-02 班 §2）。
- **读面三证（写盘前实测）**＝磁盘 sha256 `a9532fceb0899c9409b6…`／145458B／rows **110**／mtime `22:45:20`；index blob==HEAD blob＝`493f4b1fbaa2…`（`git status`＝` M`）⇒ 磁盘面领先，判卷取磁盘面；上一班留下的"下一班读面＝`682ab7cf…` 之后"已按实兑现（换代到 `a9532fce…`，无跳号）。
- **本班升级＝零**（唯二 pass 仍＝rows[76]/[78]，未重跑；红线"fail 永不升级"）。新开单号＝**修㉕**（转 ⑤，两点披露腿）＋结构性观察 **S-10/S-11**；在册单号此前止于 修㉔／P-11。零呈批草稿新开、零缺数单、零对照单。
- ⚑ **上一班交给本班的"末袋对拍"首查判据＝本班已跑，结论如下（内容级，禁按条数估）**＝本席同名 `st-qoder-p09-1016-01` 四袋＝`-0001 done`＋`-0002/-0003/-0004 dead`，三枚死因逐字同＝`landing 异常: RuntimeError: [landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）`。判据与读数＝逐袋读 `files[].blob_sha256`＋`blob_ref` 正文，对现盘面做 `in` 判定与 difflib 行级差：四枚 ledger 正文**全部在盘面内**（`在盘面内=True`×4），行数链＝1165/1177/1188/**1196**，`-0004` 与本班起批基线**逐字节等值**（行差 0、增行 0、且盘是它的超集=True）⇒ **三枚 dead 袋＝同会话后袋把前袋打成回退弹的既有形态，内容零丢失、无需 requeue**；本班袋（1016-02）落地面将原生携带 `-0004` 全文＋本班 §1–§8。⚠ **本班不执行 mv 销账**＝`process_reaper --status` 现读 `dead_archive: ok=False rc=1`，理由逐字＝`ERROR: serializer 租约存活（pid=47508），拒绝并行维护操作`⇒ 在册工具自己挡并行维护，本席不绕、不手搬；判据与读数留此，待租约释放后由正门 `dead-archive --session st-qoder-p09-1016-01 --content-level` 通道销账（要 ⑩ 认这条归属：死信属 ⑨ 席前任，本席代分诊、不代销账）。
- **下一班首查判据（正文可原样跑）**＝①`python .runtime/tmp/st-qoder-p09-1016-02/replay10_calib.py <起始行> <结束行>`（在册尺副本，若 tmp 已被清扫则回 1015-10 班原件路径 `find .runtime/tmp -name replay10_calib.py`）；正对照＝任一已知 PROBLEMS 0 的行（如 `108 108`）先跑，别把"尺不认新键"读成"判卷不符"（本班 `109 109` 末行 PROBLEMS 1＝尺与执行器同缺 `gap_k3_vs_k0_5d_max` 面，两侧 verdict 皆 fail）。②写前必 `python scripts/lock_files.py check <自家面>` 自证在册＝本班据此抓到自家 4 条 claim 被 ⑧b 席 23:02 的整册写洗掉（详见台账 §8 第一条 [BLOCKER]）。
- 本班耗时锚＝冷启动 `process_reaper --status` 日志时戳 `2026-10-16 22:50:48`（本席未另测起批那一秒，故只用该实测锚、不自报"约 22:49"）；提交段终值（袋号/files/base_head/对拍）由收班段按实报，禁预写未发生的读数。
