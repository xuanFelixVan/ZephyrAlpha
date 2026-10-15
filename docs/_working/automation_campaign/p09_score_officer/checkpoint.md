---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑨成绩官·游标
---

# 游标

cursor: exam_scores_v1.yaml#rows[82]
last_run: 2026-10-15
last_batch: 当日增量 8 行已判（rows[83] 起待判）
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
