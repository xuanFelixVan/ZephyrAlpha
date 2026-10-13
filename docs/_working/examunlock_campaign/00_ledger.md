---
ttl: task_bound
title: 考试解锁班 st-examunlock-20261013 班台账（修订版施工令执行账）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 〇、头条（Owner 醒来先读这八行）

1. **本班开考 0 张，且这一条不是"没干活"，是三条实测结论叠出来的**。
   基线=本班现取在册 classify 尺：preregistered **177**、A=0／A?=11／B=17／C=121／D=0／U=28；
   分数册 **46 行 32 张卡全 fail**（pass 行 0）。
2. **令卡三条前提被实测证伪，本班按纪律没有硬凑**（逐条证据在本班 05/07/13 号件）：
   ①"9 张单表入配方册"＝11 张 A? 卡**逐张与 A 路语义不同型**（横截面形／聚合口径与 anyLast 不同型／
   序列未冻结到一列），补登记＝把命题洗成日频标量＝造第二判据面 ⇒ 本班**零登记**，出逐表判定册；
   ②"第 4 张 A 类事件卡走现成通道跑掉"＝该卡卡面自书 `blocked_reason` 缺"行业×日研报密度"算子，
   现器装不下（`SQL_DAILY_AGG` 无 industry 维且无逐日去重）⇒ 无"现成"可言；
   ③"horizon 阶梯族 v3+ 预注册"＝挖矿二班已把同族聚合 8 卡（`TDM-E-L1-S2/calibration/40..47`）
   整族立为 blocked_on_impl，真缺口=执行器只算次日面 ⇒ 本班不产第二套（同域重复簇违根宪法 §4.2）。
3. **本班把 20 张反向卡推到了"只差最后一毫米"，并在这最后一毫米上抓到一条全仓未记载的真拦路**：
   卡面把 `window.regimes` 写成散文串，而判官四条消费位（`calibration_exam.py:163/200/402/752`）
   一律按映射读 ⇒ run 面出分前必 `AttributeError`。全库普查该字段形态：**dict=310 / str=22 / 无=186**。
   本班在临时副本里做纯表示层转换后跑通全链，**该卡判 fail 不判 pass**（证据与原文读数在 13 号件）
   ⇒ 修这条不是"凑通"，只是让判据能正常评估它。本班**没有动磁盘卡件**（一字节未改）。
4. **结构性发现：开考面不是"少接了 50 根线"，是绑定的产能与题面形态两头都缺**。
   矿考二班绑定册 14 个 approved 格**14/14 都已有分数行**（零未跑存量）；
   177 张 preregistered 卡里**177/177 没有任何 approved 格**。
   ⇒ 北极星"开考面 ≥50"在现器＋现题面下**没有可达路径**；本班把最长的死路变成了最短的路
   （20 张卡的绑定册格已就位，只等表示层一处定夺＋基序列落盘）。
5. **本班交付面**（12 件已入队 q-20261013-st-examunlock-20261013-0001，其余见 §三）：
   规格册 02／本班自有绑定册 03（20 格，prose_quote 全部机取且过运行器同款子串校验）／
   目标面通道分母 04／配方册逐表判定册 05／骨架 13 张逐张判定册 06／协调单 07／
   **抢救他班 TTL 件 08（六件，归属 st-examrun-20261012）**／矿脉规格 09／ablation 分腿审计 10／
   WO-A2 存在性核查 11／元层基线 12／表示层拦路诊断 13。
6. **施工件被一道在册门拦在库外，本班按纪律没有绕**：
   新 `scripts/audit/ti_daily_mean_materialize.py`（＋配对测试 12 支零 CH 全绿）已走意图 API 单口
   登记 token＋大白话，PG 侧两条都 active；但 TRANSLATION 门读的是投影册的 HEAD 面，
   本班实测 HEAD 投影 vs 盘面 render **差 12 行＝本班 2 行＋他班 5 行＋测试夹具 5 行**
   ⇒ 随袋带册＝把他人 10 行洗进本班 commit＝触在册禁令（Owner 10-10"禁出重打投影袋"）。
   本班选择：**代码件摘出本袋**，缺陷与两案写进 §四 呈批，不弱化门、不加白名单、不改判据。
   **且本班试过"只投两枚代码件"的探测袋（01:3x 实测）**：`git_commit.py --enqueue` 在**锁外预检**即被
   同一道 TRANSLATION-COVERAGE 拒绝、**未进队列**（不留死信）；本班不用 `--skip-preflight` 绕这道预检。
   ⇒ 该门落地侧的读源仍只有间接证据（本班现读 `module_translation_loader.py:130/571/753` 三处
   `yaml.safe_load(_REGISTRY_YAML.read_text())`，确无 PG 通道）＋在案 st-gpuwo 10-12 夜记同一条；
   反例一枚如实登记：`f45ff46d358`(10-11 17:33) 新 .py 只带 2 件、零热册却落过地——
   两派证据都在，本班因此**只呈批不自行翻案**，并把这条列为 R-1 需要净增袋才断得清的疑点。
7. **CH 面本班零查询**（01:00-04:00 让路窗照守；窗后再说 §二 的物化与开考）。
8. **需要 Owner 点头的只有三件**（详见 §五 菜单），其余本班已自决做完或已归位到属主班。

# 一、基线与归因（本班自取，非转述）

- 在册尺读数：见头条 1。与考试班夜间袋差 1 张的归因＝矿考二班 `0e0e32e5fa`(23:41) 把 07 卡考出，
  dev 面 status→examined；本班实测 dev：preregistered 177／examined 32／卡件总数 518。
- **主区盘面条状异常（只报不修）**：07 卡在"主区索引标删（`D `）＋盘上同名未跟踪件（`??`）"双态并存，
  盘上那份 status=preregistered 而 dev 面是 examined ⇒ 主区磁盘落后且与 HEAD 异体。
  属运行面落后 HEAD 的在册形态，本班不在共享主区动它（动它＝碰他人在飞面）。
- dev 考尺健康度复测：`tests/backtest/test_calibration_exam.py` **41 passed**（本班在车道面跑，
  与考试班 23:19 终态同值）；本班新件配对测试 **12 passed**（零 CH）。

# 一·补 两把尺的对账（本班 04 号件 vs 考试班被抢救出的旧普查）

抢救件 `08_rescued_ttl_st_examrun/target_face_census.yaml`（考试班 st-examrun-20261012 出品，
原只活在 `.runtime/tmp/` TTL 区）与本班 `04_target_face_channel_census.yaml` 是**两把独立尺**，
本班逐字段对表如下，免得统筹拿两个数当成两个事实：

| 量 | 考试班旧尺 | 本班新尺 | 差因（本班归因） |
|---|---|---|---|
| 宇宙张数 | 177 | 177 | **一致**＝两把尺独立复测同宇宙（这条是本表唯一硬交叉验证） |
| 目标面非指数腿张数 | 128（对全部 177 张逐张判 target 面） | 118（只数 classify 落在 C 类且 reason=target_face_not_index_next_day 的） | 口径不同非冲突：本班尺只看 C 类；那 10 张差＝同一"非指数腿"命题落在 B(17)/U(28)/A?(11) 类里，被各自更靠前的闸先拦（面板闸/多表闸/配方册闸） |
| 非指数腿"读法"种数 | 104 | 94 | 同样不同口径：旧尺对 128 张归一，本班对 118 张归一，且本班归一只折叠空白（不做近义合并），故本班数是**下界**口径 |
| 在册词表内卡数 | 93（pillars_within_judged_vocab） | 本班未复算此列 | 判据词表面属矿考二班在飞域（其袋 0014 正在扩词表），本班不复算以免用过期快照出数——如实留空 |

**结论不变且更强**：无论按 104 还是 94 条腿，"目标面通道"都**不是一条通道**；
本班 04 号件另给出的关键增量是**长尾形状**（91/94 条腿各只 1 张卡在用，前 10 条腿合计才覆盖 34 张），
这一条旧普查没有出（旧件 top_target_faces 榜只列前 25 条，且未给单例占比）。

**"旧尺 11 张干净候选 vs 本班开考面 0"不冲突（这条必须写清，否则像是本班漏了 11 张）**：
旧件 `clean_candidates` 11 张的 cls 分布＝**U 5／B 4／A? 2，零张 A/D**
⇒ 它们的"干净"是五闸（目标面/判据词表/分桶机器面/无在册考果/多臂申报）意义上的干净，
到绑定制还差最后一道，与本班实测"177 张 preregistered 卡 177/177 无 approved 格"完全自洽。
反向验证本班 06 号判定册：本班判"接线即可考"的 4 张里有 3 张
（`L1-S0/calibration/03_流动性卡`、`L1-S2/calibration/07_连板家数分布`、`L1-S3/calibration/02_昨日涨停溢价`）
出现在旧尺 11 张名单内；唯一未出现的 `L1-S0/calibration/04_海外卡` 是 bivariate_decile 分桶形，
被旧尺 bucket_machine_faced 那道闸先拦——两把尺在这里给出同一个答案的不同侧面，不互相打脸。

# 二、CH 段实测（窗毕后跑，本班按"同进程复用＋单查询内存帽"执行）

> 依据在册 10-13 凌晨实测的 CH 共享内存墙（上限 7.14 GiB，并发面板装载⇒HTTP 500／code 241）：
> 本班物化件每条查询自带 `max_memory_usage=3GiB` 与 `max_bytes_before_external_group_by=1.5GiB`（外排磁盘），
> 20 列串行、失败即抛（`ch_query` 把所有异常转 CHAccessError，不会把出错洗成"无数据"）。

**本段的实测数字一律落在 `14_series_materialization_receipt.yaml`，本件不重投**——
理由=在册落地仲裁把"同会话同件先后两袋"判双侧皆改真冲突（累计 239 袋），本班自犯过一次
（01:3x 试投探测袋被预检拒，未生成死信），不再犯第二次。物化/复算/逐日截面票数三项读数见 14 号件。

- 物化（materialize）：见 14 号件 `materialize` 段（列数／逐列 rows／窗／meta 落盘名）
- 复算证明（verify，卡面 impl_gap ①）：见 14 号件 `verify` 段（20/20 逐日对拍与 max_abs_diff）
- 开考（run）：**本班不跑**——13 号件表示层拦路未解，且统筹 01:4x 批复已把该修法
  "随考试班立案转挖矿二班"（见 §七），本班越过它去开考＝绕过属主署名，不做。

# 七、统筹批复入账（2026-10-13 01:4x，照守不再自决）

1. **三处证伪全采**："没有硬凑是对的执行"——11 张不同型零登记（出判定册而非造第二判据面）、
   第 4 张卡自书缺算子如实呈、horizon 不产第二套。本班按此定性收口，不再补任何"凑数考面"。
2. **结构结论入册**（＝明晨排产地基）：14 个接线格 14/14 已跑完；177 张未考卡零接线格；
   "开考面 ≥50"在现器＋现题面无可达路径。
3. **本班 R-1（翻译门读 HEAD 投影、新 .py 落不了地）＝并入维护三班 C4 族**，正解同源；
   本班不再自行推进，两案与实测差集留在 §四 供该族取数。
4. **本班 R-2（20 张卡 window.regimes 散文形）＝随考试班立案转挖矿二班**（属主署名改卡面）；
   13 号件即接手证据：症状／四条消费位行号／全库形态普查 dict310-str22-none186／
   临时副本跑通全链且**判 fail 不判 pass** 的原样读数／可机械校验的转换配方。
5. **04:04 自动物化＋复算证明照走**（批复明文），本班值守脚本按窗判据执行，不提前抢库。

# 三、交付清单与复核命令

| 件 | 路径 | 复核命令（原样可跑，期望值随件） |
|---|---|---|
| 物化件规格 | docs/_working/examunlock_campaign/02_ti_series_spec.md | `git show dev:docs/_working/examunlock_campaign/02_ti_series_spec.md \| head -20` |
| 本班绑定册 20 格 | docs/_working/examunlock_campaign/03_binding_book_event20.yaml | `python -c "import yaml;d=yaml.safe_load(open('docs/_working/examunlock_campaign/03_binding_book_event20.yaml',encoding='utf-8'));print(len(d['entries']),sum(1 for e in d['entries'] if e['status']=='approved'))"` 期望 `20 20` |
| 目标面通道分母 | docs/_working/examunlock_campaign/04_target_face_channel_census.yaml | 期望 universe.preregistered=177、blocked_on_target_face=118、channel_summary.distinct_legs_required=94 |
| 配方册逐表判定 | docs/_working/examunlock_campaign/05_recipe_book_grain_verdicts.yaml | 期望四表 verdict 全"拒登本批"，fit 合计 0 |
| 骨架 13 张判定 | docs/_working/examunlock_campaign/06_skeleton_card_verdicts.yaml | 期望 count=13，直方=接线 4／新版本卡 2／拒考 7 |
| 协调单 | docs/_working/examunlock_campaign/07_interface_notes_for_mineloop2.md | §二 的 blocked_reason 原文可 grep：`grep -c 催化剂密度 docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-09__calibration__06_催化剂密度过热事件开关.yaml` 期望 ≥1 |
| 抢救件（他班归属） | docs/_working/examunlock_campaign/08_rescued_ttl_st_examrun/ | `ls docs/_working/examunlock_campaign/08_rescued_ttl_st_examrun \| wc -l` 期望 6 |
| 隔夜/日内矿脉规格 | docs/_working/examunlock_campaign/09_overnight_intraday_vein_spec.md | §二 的 36/19 分母来自本班普查（命令见该节） |
| ablation 8 审计 | docs/_working/examunlock_campaign/10_ablation8_leg_audit.yaml | 期望 roster_8 八条中 alpha_sources 非空仅 2 条，distinct_legs=1 |
| WO-A2 存在性核查 | docs/_working/examunlock_campaign/11_woa2_minute_face_check.md | `grep -n "个股面未证" docs/_working/mineloop_campaign/99_checkpoint.md` 期望命中 218 行 |
| 元层基线 | docs/_working/examunlock_campaign/12_meta_baseline_lanes.yaml | 期望三指标仅 m1 出数；headline_finding 记 3988 行候选在 518 张卡中命中 0 |
| 表示层拦路诊断 | docs/_working/examunlock_campaign/13_run_path_block_regimes_representation.yaml | 预演件可重跑：`python .runtime/tmp/st-examunlock-20261013/rehearse_run_path.py`（零 CH 零生产写）期望末行 `REHEARSAL PASS` |
| 施工代码件（**未入库**） | scripts/audit/ti_daily_mean_materialize.py ＋ tests/gov/audit/test_ti_daily_mean_materialize.py | 见 §四 呈批件 R-1；入库前只在本班车道存在 |

# 四、呈批两案（本班不自决的门/面缺陷）

- **R-1 翻译门读 HEAD 投影，登记在册却落不了地**（同一病灶在 10-10 已由 CREATE-GUARD 打过 PG 第三源，
  半治半漏）。本班实测数据全在 06/13 号件与 §头条 6。
  甲＝请册主车道出一次 **render 净增袋**（把 PG 与 HEAD 的 12 行差集清账；含 5 行测试夹具须定性）；
  乙＝按 CREATE-GUARD 先例给 `module_translation_loader` 加 **PG 第三源，只加正证不松门禁**。
  本班不选（属门禁本体面，且在维护三班/注册表车道域内）。
- **R-2 20 张反向卡的 `window.regimes` 表示层**：甲（改卡面 20×2 行，属主署名，本班已备可机械校验配方，
  且证明转换后判 fail）／乙（判官加 fail-closed 归一解析器，覆盖面 310→332 张）／丙（不动，20 卡永停 blocked_on_impl）。
  本班推荐**甲**（依据＝在册先例"闸没误杀时改输入面，别放宽判据面"）。

# 五、给 Owner 的话（大白话；统筹 01:4x 已把原三条里的两条转走，只剩一条真要您点头）

先把话翻译完：本班说的"卡"＝预先写好评判标准的考题；"开考"＝真去跑数据判这道题过没过；
"绑定册"＝考题与取数方法一一对应的接线表；"投影册"＝由数据库自动生成、不许手改的名册文件。

1. ~~"那 20 道题差什么格式"~~ → **已由统筹转挖矿二班**（随考试班立案，属主署名改卡面）。
   本班交出去的接手证据是 13 号件，其中最要的一条实测事实是：**把格式改对之后那道题判 fail 不判 pass**，
   所以这不是"放水让题通过"，只是让判卷程序能正常判它。
2. ~~"本班写的小工具为什么进不了库"~~ → **已由统筹并入维护三班 C4 族**（与"门只认旧名册"那条老病同源）。
   本班实测给该族的数：HEAD 旧名册 vs 数据库现值差 12 行＝本班 2＋他班 5＋src/zephyr 测试夹具 5，反向 0 行。
3. **只剩这条**："目标面通道"这条立项还值不值得按原口径批？
   本班量出来的真相是——它不是一条通道：要支持的读法 94 种，其中 **91 种各自只服务 1 道题**，
   前 10 种合起来才覆盖 34 道；剩下 60 种是"每道题一种读法"的长尾。
   ⇒ 按"一条通道解 119 道"去批会严重高估收益；按"先批 4 类通道（覆盖 34＋16 道双臂形）＋长尾逐类再说"去批才合身。
   —— 您回：**照 04 号件改立项口径／只批前 4 类／先搁，等明晨排产表出来再定**

另外两件本班如实上报、不需要您回的（已入账）：
- 会话保活第三种形态复现：本班 00:1x 建车道时注册＋心跳守护正常，00:5x 投袋时被
  `SESSION-REQUIRED` 判"未注册"拒投（注册条目被回收），本班按在册复命四步重注册＋重拉守护后过。
  这条与"活性族/守护自退"同簇，归维护三班在案面，本班不自修。
- 考试序列真源库的落脚不稳：`SERIES_DIR` 指向 `docs/_working/nightmine_campaign/series/`，
  而同目录的册面文件都写 `ttl: task_bound`、`sid: st-nightmine-20261010`（一个已收班的班）。
  ⇒ 考试卡的"基序列真源"寄存在**他班 task_bound 目录**里，按目录契约归档器/清理器管辖面，它可被搬走或清理
  而在册面看不出异常。本班照此落 20 枚序列（不另起第二库），并把这条定性登记，是否迁到 permanent 库归统筹排产。

# 六、纪律自证（本班全程）

- 零 CH 查询（截至本袋写入时刻）；零生产库写；零分数册改；磁盘卡件改动=0。
- 未动他班属主面：`card_binding.py`／`calibration_exam.py`／`mineloop_campaign/02_binding_book.yaml` 零接触
  （矿考二班在途袋 0014 正在改前两件，本班全程避开同件并发）。
- 两本热册（capability／module_translation）的 render 字节**零随袋**（§头条 6 的实测差集为据）。
- 同会话同件不跨袋：本袋 12 件与后续落地批件面互不相交。
- 交袋前真钩子干跑三段全读；被抓到的两道硬拦按在册处置：能自修的（depgraph 节点）当场修，
  属门禁本体的（翻译门）摘件呈批不绕。
- 一次性临时件全在 `.runtime/tmp/st-examunlock-20261013/`（本班 02:0x 实测 13 面：
  5 个册生成器＋1 个状态翻转件＋1 个离线预演件＋1 个引用自审件＋1 个窗候脚本＋2 份袋讯息
  ＋1 份物化日志＋1 个预演输出目录），交付件无一处引用临时件路径作真源。
  （04:4x 补口径：交付件里出现的 `.runtime/tmp/...` 只有两类——册内 `built_by` 溯源注记，
  与"该件字节已内嵌 17 §六、按式复原即可"的取回指引；两类都不把临时件当判据真源。）

# 八、统筹批复入账（03:1x 与 04:1x 两批）＋纪律读数刷新（04:4x）

1. **【03:1x】裁 as-of 规则先行**（判 `TDM-E-L2-01/ablation/02_四路等权合成分边际`）：
   月频成分×日频行情的对齐规则＝判据面，归卡面属主；**形状预签＝必须 PIT 安全**
   （取严格早于该交易日的最近一次月频行，禁未来泄漏），规则文本冻上卡面后呈统筹批；
   **不写 as-of 的任何"配方"＝偷时间，禁开考**。本班 19 号件据此把该张落在 `as_of_rule_first` 堆，
   未写任何配方、未开任何考。
2. **【03:1x】裁登记数据缺真源项**（判 `TDM-E-L2-09/calibration/04_业绩预增催化剂腿`）：
   与 WO-A2 分钟面同族（缺 DDL 真源＝数据缺真源项），转数据域缺真源积压清单，不代声明、不硬凑
   ⇒ 该张落 `blocked_on_source`，**不进即签项**。
3. **【03:1x】复合共键深化面接受**：本班 19 号件的三堆分法（`sign_now` 12／`as_of_rule_first` 1／
   `blocked_on_source` 1，求和自证 14=Σ）连同 06 号判定册的骨架 13 张，统筹口径＝
   **27 张进入"只差签字"态**，随晨包分发各属主班。
4. **【04:1x】177 张逐张交接矩阵＝本班最高价值交付**，本班照自走路径收尾（末袋＝序列＋回执＋晨包＋
   19 号件＋两处自查更正）。
5. **纪律读数刷新（04:4x 记，05:3x 用 `system.query_log` 反查后再次更正——这次不是"我记得"）**：
   CH **只读**＝完成态 SELECT **182 条**（argMax 口径 140 ＋ 换口径前 anyLast 42；`type=2` 计数），
   首条本地 04:04:13／末条 04:25:06；本班 04:2x 那份"2 轮×20＋3 轮×20＋诊断≈10（≈110）"**是低记**，
   04:1x 之前还写成背数 25——两次都就地更正，最终以日志反查数为准（分解见 `14_ti_series_receipt.yaml`
   `discipline.ch_read_decomposition`）；
   CH 写＝0；分数册写＝0；卡面磁盘改动＝0；热册 render 随袋＝0；绕门＝0；
   让路窗 01:00-04:00 内本班查询＝**0**（同一把尺的 `countIf(event_time < 20:00Z)`＝0，窗内零查询这条由自述升级为可核）。
   量这条时又踩一次在案老坑：**本班自己的审计 SQL 含有过滤词，会被自己数进命中**（不加
   `query NOT LIKE '%query_log%'` 时命中从 182 涨到 366，并凭空多出一条"05:26 自查"读数）。
6. **本班 04:3x 实测到的一次自家工作树事故如实登记**：车道**内层** worktree
   （`.worktrees/st-examunlock-20261013/.aidrafts/st-examunlock-20261013`）被自动重基拍平回 HEAD，
   本班未落地编辑在该面全数消失（`git status` 显示 clean 而文件确实少了）；
   **外层**工作树完好，故末袋未受影响。教训与在案"重基清单须先排除自己未落地编辑"同型，
   本班 04:4x 因此把三件不可弃件的字节写入 17 §六（不依赖任何工作树存活）。
