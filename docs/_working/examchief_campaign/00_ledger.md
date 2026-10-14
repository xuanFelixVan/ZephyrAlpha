---
ttl: task_bound
title: 矿考三班·班账（考试线施工总包：D10 甲批落地＋880 截面形＋首张 RRG 分）
created: '2026-10-14T00:54:00+08:00'
sid: st-examchief-20261014
lane: .worktrees/st-examchief-20261014（分支 ai/st-examchief-20261014/task-rrg-v2card-880face）
family_id: MINELOOP-CAMPAIGN
ruling_basis: 统筹令（2026-10-14 晨，D10 Owner 已裁甲）＋同令增补两条（基准保持 000300／投影滞后假拦预警）
depends_on:
  - docs/_working/mineloop2_campaign/00_morning_pack.md（§33.10 对照包＝依据；§33.11 交接卡）
  - docs/_working/mineloop2_campaign/05_composite_leg_face_design.yaml（复合族入口设计稿，批-A 三档排产）
completes_when: 三张版本卡入册＋880 形首张 RRG 分（或负结果如实入册）＋批-A 余量按分档放量后随 MINELOOP-CAMPAIGN 归档
---

# 〇、大白话开场（只给 Owner 看的一段）

上一班算出来一件事：**旧考试卡里写的那条公式是坏的**——用它画"板块强弱图"，497 个交易日里
所有板块都被钉在同一个格子里，等于一把没有刻度的尺。Owner 早上拍板：改用仓库里生产代码
一直在用的那条公式（10/26）。本班的活分三步：①把尺子换对（另起三张新版本卡，旧卡一个字不动，
这是 G4-5 的规矩）；②把"按板块量"的取数通道建起来（880 板块截面形）；③用新尺子考第一场试，
把分数如实写进册子——**分数好不好看不重要，是真的才重要**。

# 一、冷启动与接班面（00:03–00:15，逐条实测）

- RULE-ENV：`python --version`=3.12.8；`setup_dev_env.py --check`＝usercustomize 在岗（指向 D:\ZephyrAlpha）。
- RULE-GUARDIAN：`lock_files.py cleanup` 清掉 4 枚死锁；`process_reaper --status` source=live、
  last_run=2026-10-14 00:03:31、killed=0；水位 commit_pct=70.68%（在册事故面 <85% 可用，非自拟阈值）。
- RULE-WORKTREE：本班车道 `session_worktree.py create st-examchief-20261014 task-rrg-v2card-880face`
  （心跳 daemon PID 38876）；**未在车道外写任何仓库文件**。
- 建道时三件关键面对拍 dev 全等（§33.9 在册教训"车道 HEAD==dev 不等于可读面==落地面"）：
  `sector_rrg.py`=f9527280ca9e、`card_binding.py`=ff30d46e1db8、`02_binding_book.yaml`=31d2b22293e0 三对全 SAME。
- 在飞袋避让扫描：本班 10 枚目标件（含绑定册/分数册/试次册/判官件/用例）在 pending+processing 里
  **零命中**；前任矿考二班袋 0049（班账 §33.11）与 0050（D10 回执）本班一律不碰——
  00:5x 复核两袋 state=done，§33.11 与 `15_d10_two_formula_probe_receipt.yaml` 已随其入 dev
  ⇒ 统筹令"回执数字已落 dev"的前提**成立**（本班 00:52 首查时它还在 pending，未据此下结论）。
- 认领：8 枚热件 `lock_files.py acquire`（TTL 30 分钟，提交前重取）。
- ⚑本班自犯并当班更正一条（在册同族第二次，体感钟快约一倍）：本节初稿把各段时间写成
  "01:2x–02:4x/03:10"，而 `date` 实测当时是 00:5x——真实序列是 00:03 冷启动、00:15 建道、
  00:19 复现探针、00:2x-00:3x 三张卡、00:3x-00:45 代码与变异自证、00:45 R7 基线。
  已按实测值改写全账（未落地面前就地更正，落地面将以此段为准），并记下教训：**写时刻前先 `date`**，
  让路窗类时间闸尤其如此——本班据此纠正过一次"以为已经过了 01:00"的误判。
- RULE-CAPABILITY-LOOKUP：写第一行业务代码前 5 查留审计（RRG 象限 板块截面／sector_family_panel 装载／
  复合腿 combine 算子／考试卡 版本卡 口径变更／横截面 占比 序列）＝4 查零命中＋1 命中
  `multifactor_sleeve_strategy`（D_PF 组合 sleeve 件，不同对象）⇒ 同批有非零命中＝尺在岗，
  结论与上一班一致：**无在册复合装载形可复用，本面属补缺非重复建设**。

# 二、首件小步校准＝复现 §33.10 对照包读数（00:19，6 次 CH 只读）

同尺同参：逐行克隆矿考二班 `.runtime/tmp/mineloop2/d10_two_formula_probe.py`，
**差异只有 5 行**（读取根、输出路径、sid、date、probe 标题），比对＝结构化等值判断。

| 项 | 矿考二班 23:3x | 本班复现 00:19 | 等值 |
|---|---|---|---|
| 抽中 4 板块 | 881187/881252/880360/881002 | 同 | 是 |
| 共同日数 | 497 | 497 | 是 |
| RS 相关（逐板块） | 0.488/0.301/0.389/0.500 | 0.488/0.3013/0.3889/0.4997 | 是 |
| 象限一致率（逐板块，两映射同值） | 0.404/0.429/0.501/0.421 | 0.4044/0.4286/0.501/0.4205 | 是 |
| 卡面 4 日式 share 标准差／种数 | 0.0／1 | 0.0／1 | 是 |
| 在册 10/26 式 share 标准差／种数 | 0.534／9 | 0.5344／9 | 是 |
| 两式横截面 share 相关 | nan（常量⇒无定义） | nan | 是 |
| CH 只读查询次数 | 6 | 6 | 是 |

`cross_sectional_share` 与 `per_sector` 两个子树与前任 receipt **整体等值**（逐项 True）。
⇒ 本班据以动卡面的"4 日式退化"结论**不是转述，是复现**；样本偏照旧披露：只抽 4 个长史板块
（HAVING count()>=500 取前 4），横截面粒度粗，该读数只用于"是否退化为常量"这一条判据。

# 三、三张 G4-5 新版本卡＋变更单（00:2x–00:3x，零 CH）

落点：`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/` 三枚新 yaml（ASCII 文件名，
card_id 用中文承母卡命名族）；旧卡面**零字节改动**（三枚母卡不在本班 files 面内）。

- `TDM-E-L2-02-1/calibration/02b_RRG象限迁移_在册10_26双EMA口径版`（version_of=02）
- `TDM-E-L2-02-1/ablation/03b_象限迁移确认腿与稀有路径护栏_在册10_26口径版`（version_of=03）
- `TDM-E-L2-05-2/ablation/02b_信号响应三件套_在册10_26口径版`（version_of=02）

判据面零自拟的**机械自证**（yaml 子键级 norm 等值比较，非嘴上说）：
`pillars_numeric`／`pillars`／`buckets`（除新增声明键）／`oos_window_ref`／`discipline`／
`signal_kind`／`family`／`node_id`／`window.in_sample·oos·regimes`／
`data_binding.signal_table·signal_column·target_source`／`composite_join_rules.pairs` **全部与母卡等值**；
被改的只有四类，且全是口径面/指针面：①`window.frozen_note`（构造式换成在册 10/26 原文）、
②`data_binding.signal_derivation`（整段替换，旧句在变更单里逐字留痕）、
③`data_window_evidence`（**只追加**本班复现行）、④03b/02b 的 `target.note`（共用口径锚点 02→02b）。

三处"本班没有替卡拍数"的落点，逐条写明在卡面：
1. **基准保持 000300**（统筹增补裁定原文入卡：命题声明的输入面不随甲批文自动切换；
   `sector_rrg.py:120` 的 880001.SH 只是函数缺省参数说明，本班按 leg 显式传 000300 收盘）；
2. **带宽 ±5 随锚点废止**——不是本班放宽，是承接的在册四分规则 `classify_quadrant` 里没有带宽项；
3. **快慢序不自拟**——(RS-Ratio, RS-Momentum) 的坐标序由 `compute_rrg_series` 的签名与
   `classify_quadrant` 的入参序固定（§33.10 第三分叉在甲路下由被承接装置自身消解）。

变更单＝`docs/_working/examchief_campaign/06_d10jia_change_order.yaml`（逐卡废止面/新面/保留面、
基准一行、复现读数表、净零声明、§7 复核命令带期望值）。

⚑ **如实登记的一条开考面缺口**（不遮、不改判据）：02b 的 `buckets.on` 是 (板块×日) 八格 categorical 面，
而判官 series 路径按信号值分位分桶（`calibration_exam.py` 的 `_BUCKET_TYPE_N` 缺省 10 桶）——
一条日频占比差序列**承载不了八格**。在册同型先例＝绑定册 L2-02-2/02 的拒绑理由②
（"分桶协议不可执行／ORDINAL_FALLTHROUGH"）。本班处置＝把该缺口写进卡面
`buckets.machine_face_gap` 与册格 review_note，出分后只按连续面三柱（ic_mean/ic_ir、regime、oos）
读这张卡；**mono 柱若单独决定 outcome，按"机判面与冻结门柱不同物"上报，不签 pass**。
全仓 5 枚 categorical 卡（含三枚 RRG 族）**至今 0 出分**＝这一格缺口是族级而非本班独有，
补法属面板机判面（04_ 稿 P0 族，门位件）。

# 四、880 板块截面形施工（00:3x–00:45，零 CH，全在既有件内）

改动面＝`scripts/backtest/fexam/card_binding.py` 一件的四面扩面＋用例面，**零新建模块**：

1. `_COMPOSITE_LOADERS` 在册形清单：`("face_daily", "sector_family_panel")`——第二支由 D10 甲批解锁；
2. `_load_panel_leg`：族面板长帧腿，装载口与 SQL 模板**全复用**在册
   `load_sector_family_panel`/`SQL_SECTOR_FAMILY_PANEL`；表名/族名/映射表/周期/列名一律整表来自册 args，
   函数体不出现任何族名或表名；四要素缺一即拒、族名非标识符即拒、map_table 非全限定名即拒、
   args.table 与 leg.table 不一致即拒；
3. `assemble_composite_legs` 混合粒度：`inner_on_keys` 在 (日×板块) 长帧与日频序列之间定义为
   **日轴键集交集**（序列 reindex、长帧按日过滤），掉数在**日轴与行数轴分别入凭据**
   （`days_dropped_by_alignment`/`rows_dropped_by_alignment`/`rows_kept`），`fill_policy` 仍 none；
   全 Series 腿时走原分支，凭据面键集**逐键未变**（用例钉死，防新形渗进旧腿形状）；
4. `op_rrg_quadrant_series`（OPS 册第 12 条）：直调 `compute_rrg_series`（缺省 10/26，不传数字）＋
   `classify_quadrant`（100 中枢），采信=raw，分母=当日在数 code 数；62 日门槛由装置自身 raise ⇒
   短史板块整段不参与并逐数披露；基准价 ≤0 点名报错（不剔日、不换基准）；
   引句双校验用卡面原文 `series=当日 leading 占比 − lagging 占比`；
5. `_REGISTERED_TABLES` 登记 `c1_market.kline_sector_880` 三要素：date_col=trade_date、
   where=period='1d'、grain_evidence 逐字抄 DDL 真源
   `schemas/categories/kline/market_kline_sector_880.py:65-67`
   （ReplacingMergeTree(fetched_at)／PARTITION BY (period, toYYYYMM(trade_date))／
   ORDER BY period, sector_code, timestamp）＋版本行收敛用在册模板的 anyLast 形。

⚑ 在册缺陷当班修（前任发现、本班消费时才真疼）：`run_one` 把 `recorded_by` 写死成
`st-mineloop-20261010` ⇒ 复合族出分的试次归属会记错会话＝台账面归属篡改。修法＝
`--recorded-by` 参数化＋**run 面不给值即拒**（不给"猜一个默认"的余地），
动前核过 `recorded_by` 的消费面：`check_exam_loop.py:145` 那条 LIKE 查的是 meta_question 的
PG `exam_result`，与 YAML 试次册不同对象 ⇒ 无尺按该字段分组，改动不影响任何尺。

自证面（全在落地面跑）：
- `tests/backtest/test_card_binding.py` **107 passed**（本班加 23 枚；含 R1–R8 在册红证与新增形/算子/归属红证）；
  判官自家 `tests/backtest/test_calibration_exam.py` **66 passed**——两条都在
  **车道快进到 dev 现值之后**复跑（建道时 HEAD=9631a2e378，04:0x 前 dev 已走到 b05345f8e6、
  中间 87 件面移动；§32.17 在册硬规矩"车道 `--enqueue` 前先核 `git rev-parse HEAD` 等不等于 dev"，
  本班据以 `git merge dev` 后复跑，避免袋基落后 dev 造回退弹）；

- 六条**变异自证**（把守卫挨个关掉，要求配套用例必红，且测完文件字节复原 sha=f6c3e89955db equal=True）：
  M1 形清单退回只 face_daily→红｜M2 基准>0 预检放行→红｜M3 62 日门槛被预削→红｜
  M4 日集交集换成并集→红｜M5 归属写死回上一班→红｜M6 族面板缺要素放行→红；
- 零 CH 端到端形状预演（绑定册真格＋真卡面）：book 16 格加载／prose_quote 在卡面命中／
  R1 腿集合合规／R2 键面合规／R3 配方册含 880／`classify_card` 仍返
  `U:multi_table_needs_composite_recipe`（R8 不扩权自证）／混合装配 70 日对齐 0 掉行／
  算子出 70 行 2 板块；
- 出分前 R7 基线：分数册 73 行、绑定册无 legs 格 16 条、判官件对 dev 零差、
  分数册与试次册对 dev `lost=0 added=0`（车道面与 dev 全等，hash d8ffb9c3b773 双向同值）。

# 五、D8 探针与首张 RRG 分（04:01 起，CH 面）

状态见本节尾（本段在批次结束后由本班补数，不预写结论）。
批次形状：01:00-04:00 让路窗是矿考循环班令 §三 红线在册闸，本班**不绕、不用 override**，
挂起到 04:01 再走（等窗驱动器＋reaper keep 行已登记，收班即撤）。
顺序＝R7 snapshot → D8 交叉核对 → **decision=proceed 才开考** → R7 compare。
D8 的放行判据机械式：象限一致率 <0.90 或 日截面占比差最大值 >0.10 ⇒ halt（卡面"先查口径再开考"），
诊断档 ±5 带宽只回答"差异是不是带宽造成的"，不改本班承接的在册口径。

## 五·补：续跑班 04:2x 实读与结局判定（本段由续跑班 st-examchief-20261014 接班后补，零预写）

**结局＝C（批次未出分），且 08 包 §2 C 给的手跑路径经实测同样不可达——根因是 D8 探针自身的读取形态缺陷，
既不是数据无源，也不是卡面口径分歧。本班据此不开考、不签任何方向的结论。**

1. 04:01:50 等窗驱动器（pid 40916，本班接班时已退，`tasklist` 查无）唤醒后两步原样落日志：
   - `drift_r7.py snapshot` **rc=1**，但内容面全绿：分数册 73 行／绑定册无 legs 格 16 条／判官件对 dev `numstat` 空串／
     分数册与试次册对 dev `lost=0 added=0`；
   - `d8_rrg_crosscheck_probe.py` **rc=2**，原文 `REFUSED: sector_state 列集里没有 rrg_quadrant，交叉核对面无源（列集=['[', "'", 't', …]）`；
   - 驱动器按 fail-closed 分支自行结束（日志末行 `D8 未放行（rc=2 decision=''）＝按卡面纪律不开考，只交回执`）。
   - `evidence/d8_crosscheck.yaml` 与 `evidence/score_run_creds.yaml` **两个文件都不存在**＝回执从未写出（本班 `ls` 实测目录仅有 log／snapshot json／driver.pid／repro 四件）。
2. 本班 04:24 用 08 包 §2 C 的**同一命令、一字未改**复跑：`snapshot` rc=1、`probe` rc=2，输出与上逐字同
   （复跑不为改变结论，只为排除"进程根本没跑起来"那一型）。
3. rc=1 定性＝机械伪影，非判据破：`drift_r7.py:99` 写的是 `raise SystemExit(snapshot() if MODE=="snapshot" else compare())`，
   而 `snapshot()` 返回 **dict**；Python 对非 int 参数会把 repr 打到 stderr 并以 1 退出
   （批次日志第 7 行那段被截断的 `{'scores_rows': 73, 'scores_row_shas': […]}` 就是它）。判据本体 `compare()` 返回 int，rc 语义正常。
   ⇒ R7 四条在册判据（A 判官零差／B only-append／C 无 legs 格不减／D lost=0）在 snapshot 面上无一条被破。
4. "无源"判定**证伪**（本班独立只读探针，共 4 次 CH 只读，04:22–04:25 均在两个让路窗之外、未用任何 override 旗）：
   - `SELECT name,type FROM system.columns WHERE database='c1_market' AND table='sector_state'` ⇒ **14 列，含 `rrg_quadrant LowCardinality(String)`**；
   - 全库 `lower(name) LIKE '%rrg%'` ⇒ 唯一命中就是这一列（表/列/类型三项同帧打印）；
   - 表体量＝**432,817 行**，`trade_date` 覆盖 **2022-09-01..2026-10-09**；
   - 正对照＝同进程把同一 SQL 连读 5 次，**5/5 全等 `(14, True)`**，非偶发也非软失败伪装。
5. 真拒因（行级定位）：探针 `:72` 用 `[str(x) for x in (cols.iloc[0, 0] if len(cols) else [])]` 取列集，
   而 `ch_query_df` 对 `groupArray(name)` 返回的是 **str**（本班实测 `type=str, len=178`，形如 `"['trade_date','stage',…]"`），
   `for x in <str>` 逐**字符**展开 ⇒ `"rrg_quadrant" not in col_list` **恒成立** ⇒ rc=2 自拒。
   ⇒ 该探针在任何数据面下都走不到 `decision:` 那一行，08 包 §2 C 的"decision=proceed 才继续"是**永假前置**
   （本交接包这一条前提被本班实测证伪，按在册纪律停手上报、不自修尺）。
6. 本班动作＝**不开考**，三条理由：①08 包 §2 C 明令"勿改尺"，而唯一能让 D8 真跑起来的动作就是改探针读取形态；
   ②02b 卡面原文（本班逐字复核，`:157-158`）"禁直读 c1_market.sector_state.rrg_quadrant 作信号（那是被测件同族产物，自证循环）；
   该列仅用作口径一致性的交叉核对（差异 >10% 时先查口径再开考）"——交叉核对拿不到任何读数时，"先查口径"这一步无从做起；
   ③判据面零自拟：既无 halt 数值也无 proceed 数值，签 pass／fail／halt 中的任何一个都是自拟结论。
7. 出分面逐字节实测（本班 `bag2_superset_check.py` 现算，非引用他班计数）：
   `exam_scores_v1.yaml` 3804 行 **byte_identical vs dev**（新增分数行=0）；02b 卡 179 行 byte_identical（`status` 未翻＝未出分）；
   `trial_ledger_registry.yaml` 369 行 byte_identical（＋1 试次=0）；码面三件（`card_binding.py` 2256／`test_card_binding.py` 1986／
   `02_binding_book.yaml` 557）与投影册 71112 行全部 byte_identical＝袋 1 已完整落地且车道无回退弹。
   ⇒ **首张 RRG 分不存在，三张 RRG 卡维持 0 出分。** 08 包 §4 三条披露今日**无读对象**但**不作废**
   （原文仍在 08 包 §4 与本账 §六 第 10 条：`ic_ir_min` series 路恒不评估／`mono_spearman` 是 10 分位代理／净费与 `min_obs_per_bucket` 无机器面），
   下一个真开考的班仍须带着这三行读分。
8. 本班自我更正留痕（按在册"更正另起、留旧案卷"）：本班第一次读 `system.columns` 时曾把输出记成"row-form 也无此列"，
   随后同一 SQL 同进程 5/5 读到 `True`、且全库 `%rrg%` 扫描独立命中 ⇒ **该初判作废**，以本 §五-4 的数值为准；
   未覆写他班任何读数，本班零 CH 写操作。
9. 袋 2 组成的连带变化：§3.5 十枚清单里**出分依赖的三件今日无变更**（分数册／试次册／02b 卡 status），
   逐字节对 dev 等值＝放进袋里就是空改动，故本班袋 2 实投 7 枚（00/07/08/09/10/11＋mineloop2 05 稿追加 §9），
   并把 **11 号 PE 规约件并入袋 2**（不在 §3.5 清单内）——理由＝收班要归档车道，而 11 件是统筹已批 PE 批（袋 3）
   的唯一规约成文面且不落 dev 就随归档一起消失；它是纯文档、不碰 `calibration_exam.py`，
   故 R7 判据 A"判官零改动"证据链不自污（§5.0 的硬时序针对的是**动判官件**，本班未动）。
10. 去井号改写留痕（本班动过的唯一文字面，零数值、零判据、零 PG 写）：入袋前一命令自扫＝**直接调门本体**
    `make_reference_integrity_gate().check(gateway, <袋内七件>)`（主区码面＋车道文件面，只读），初判 **passed=False**，
    命中形态＝"裁定"＋井号＋数字三连字符共 **5 处**：本账 §八丁批行 1／08 包 §3.5 的**那句禁令自己**（它把字面写出来了）／
    09 包 §6 一行＋§7 两行。⇒ 按令卡第五条统一改去井号形；09 包 §7 的 PG 复核命令改为 `'ruling_id=裁定' + chr(35) + '520'`
    拼同一个 entry_key，本班把**正文抽出原样**跑到期望值
    （`PG row: RealDictRow({'entry_key': 'ruling_id=…520', 'version': 1, 'updated_by': 'st-examchief-20261014'})`）；
    其间本班自己写坏过一次（`chr(35)` 拼接漏掉"裁定"两字 ⇒ 查询返回 None），当场发现、补回、二次跑通——如实登记不抹。
    改写后同一自扫 **passed=True**。520 号在 PG 真源的实查＝`REG-RULING-001` 现有 510–521 连续在账，`ruling_id=…520 / version=1 / updated_by=st-examchief-20261014` 命中在案。
11. 收班与落地账（本班 05:1x 实测；**本节由袋 2B 携带**，其上一袋 `q-20261014-st-examchief-20261014-0003` 已落地）：
    - **首投 dead**：`q-20261014-st-examchief-20261014-0002` 落地判 `[landing] 非注册表族件双侧皆改真冲突: 00_ledger.md`。
      修因＝**袋基不是内容**：`git_commit.py --enqueue` 的 base_head 由 `resolve_base_head(车道)` 取＝车道 HEAD `b05345f8`
      （早于本班袋 1 落地点），故 00_ledger 的 `base_blob=None`，而 dev 现值已含袋 1 的 222 行（blob `cc4e39c5`）
      ⇒ 落地器把"我自己袋 1 的落地"读成 dev 侧改动＝双侧皆改。这条是 §3.3"袋基核验"的**新形态**（当时测的是快进被挡，这次是异步正门取错基）。
    - **重投走正门三步**：①先用尺本体复现不信报文——`_snapshot_head_regressions` 对同一份袋字节跑三种基底
      ＝`None`→1 件／`b05345f8`→1 件／`dev 现值`→**0 件**（唯一被报"缺 dev 已在册"的行＝本班自改的旧标题行，§九 已留痕），
      坐实是基底丢失型假案；②**不写 `[pool-regression-ack:]` 旗**（在册红线：那等于亲手承认要拍回他人落地面，把假阳性固化成豁免面），
      改喂给闸的输入侧＝`git worktree add --detach .runtime/tmp/examchief/wt_dev dev` 装字节（七件逐枚 sha256 与车道对表全 MATCH）；
      ③`commit_queue.py requeue … --worktree-root=<scratch> --base-head=<dev> --force`——`--force` 只因复发熔断按"同签名家族计数"判盲投
      （签名 `other:landing 异常`，窗内 422 次是他班共账，本班 recurrence_count=422），越线理由已写进袋内讯息。
    - **落地 done**：`q-20261014-st-examchief-20261014-0003` → `landed_id=f6966fa18b1b`，`git log -1 --name-only` 核实
      commit 内**恰本班七件、零他班件**；逐字读回＝dev 现值 vs 车道字节 **7/7 行级多重集全等**
      （其中 00/08/09/10 四件 sha 不同＝纯 EOL：袋 CRLF／落地 LF，`only_in_dev=0 且 only_in_lane=0`，非内容损失）。
    - **主区暂存区回退弹已复位**：落地后主区 `git status` 对自家七件报 `MM`／`D `（index 停在袋 pre-image：
      00_ledger index blob `cc4e39c5`＝本 commit 父版本、五枚新件 index 无条目＝父版本也不存在）⇒ 判＝**纯回退弹、零他人独有行**，
      按宪法 §9.4 `git add` 刷成 HEAD，机证 `.runtime/tmp/examchief/evidence/main_index_stale_evidence.json`（随 TTL 退役，结论已在本文）。
    - **死信四态分诊（当日不隔夜）**：`dead-archive --content-level --session st-examchief-20261014 --days 0` 判
      `archived=0 content_held=1`＝**本班 -0002 未销账**。归因实测＝袋 blob sha1 对 dev 现值 4/7 不等，
      而这 4 件 LF 归一后与落地 blob **全等**（`lf_norm_equal=True` 7/7）＝内容级实质已落地、形式判据不认 EOL。
      本班不自改该判据（改尺属死信放量班/统筹门位），只把读数摊在册上。
    - **收班**：reaper keep 两行已撤（`process_reaper_keep.txt` 387→385 行，走 CAS `safe_write_text`；
      两拒一写——首两次 `StaleWriteRefused` 是本班把 base 算成 raw bytes 而工具按 `read_text` 的 LF 归一口径算 hash，
      第三次通过；写后 `verify_failed` 同属 CRLF↔LF 口径差，**按字节读回实测 385 行／CRLF 保留／本班两行已无**＝零内容损失）；
      保活授权 `revoke_heartbeat_keepalive` 已落 `keepalive.jsonl` 末条（`read_active_keepalive`→None）；
      `--release-only --files <七件>` 得 `released=7 denied=0`；车道归档前已扫**14 枚脏件对 dev 逐枚等值＝零独有残留**。

## 五·补2：矿考四班 12:4x 实读与结局判定（本段由四班 st-examchief2-20261014 接班后补，零预写）

**结局＝halt（庚甲菜单甲执行后，D8 首次拿到真 decision；判据机械式双触发）⇒ 按卡纪律不开考，三张 RRG 卡维持 0 出分。**

1. 修读取形态只动三处（其余逐字节未碰）：①探针 `LANE` 指针改指当班车道 `.aidrafts/st-examchief2-20261014`
   （旧车道已归档，环境指针非判据面）；②列集读取改按行读 `SELECT name FROM system.columns … ORDER BY position`
   逐行取值（§七 庚项在册定性：groupArray 经 ch_query_df 返回 str、逐字符迭代恒自拒）；③回执 `sid` 改写本班 sid（归属如实）。
   **判据常数 0.90/0.10、卡面引句、±5 带宽诊断档一字未动**；菜单乙（升常驻件）/丙（随 P0 排）未取。
2. 重跑（12:49:19，CH 只读 2 次，让路窗外、无 override）关键读数逐字：`cells_compared = 1134`、`codes_compared = 189`、
   `quadrant_agreement_in_register_10_26 = 0.5459`（<0.90 ⇒ 触发）、`quadrant_agreement_if_parent_band_pm5 = 0.0`、
   `central_band_share_if_pm5 = 0.978`、`daily_spread_max_absdiff = 0.5556`（>0.10 ⇒ 触发）、
   `daily_spread_mean_absdiff = 0.4859`、`daily_spread_corr = 0.8309`、
   `decision = halt（差异超 10% 线＝先查口径再开考）`。
3. 分母独立复核（本班 2 次 CH 只读，让路窗外）：`rrg_quadrant` 非空面在全表 2022-11-02..2026-10-09，
   但**族宇宙恰 189 码**（sector_code_name_map.code_family IN (industry_l1, industry_ths)）在 sector_state
   只有 **2026-09-24..2026-10-09 共 8 个交易日**有象限值（189 码/日齐）；与本班面板 1257 日轴的交集
   ＝6 日 × 189 码＝1134 格。⇒ 本次一致率是**极短窗读数**，任何长程口径结论都超出样本。
4. ±5 带宽诊断档的归因答案（呈批项见 §七 辛）：本班按在册 10/26 无带宽式与 theirs 一致 54.59%；
   若按母卡 ±5 带宽四分，本班 97.8% 落 CENTRAL 而 theirs 值域只有
   IMPROVING/LAGGING/LEADING/WEAKENING 四象限（无 CENTRAL）⇒ 带宽档一致率恰 0.0。
   **差异不是带宽造成的**——恰相反，带宽是把本班读数压进 CENTRAL 的那一下。
5. CH 配置警告验真：车道缺 config/.env.clickhouse 只触发 ch_config 的 warning
   （已有 os.environ 不覆盖；load_ch_config 对缺 host fail-closed），2 次查询真实往返
   （值域/行数非占位）＝警告是红鲱鱼，非软失败伪装。
6. R7 基线（12:5x，车道 HEAD=dev=1f82fcb26206 后取）：内容面全绿——`scores_rows=73`、
   `book_entries_without_legs=16`、`judge_diff_vs_dev=""`、分数册/试次册对 dev `lost=0 added=0`；
   rc=1＝§五-补 第 3 条在册机械伪影（snapshot 返 dict）非判据破。
   ⇒ 分数册/试次册/02b 卡 status 对 dev 逐字节等值＝三卡维持 0 出分有机证。
7. PE 时序说明：08 包 §5.0/11 稿 §6 的硬时序对象是"首张 RRG 分＋其袋落地"；今日 halt 下该对象不存在，
   本班把 halt 账先落（本节＋§七 辛），再动判官件（袋 B）＝"判官零改动"证据链无可自污对象。

# 六、残余与转他班（不装完）

1. 八格 categorical 无机判面（族级 5 枚卡）＝面板机判面缺口，属 04_ 稿 P0 门位族，非本班可自签；
2. 批-B 5 枚卡的 `sector_state` 键面未冻（22 册自标 `joinable_now: false`）＝属主 examunlock 班补键或卡面删腿；
3. 钉-1 `market_sector_constituent_snapshot` 品类未注册（TableRegistry KeyError 实测复现两次）＝数据班/统筹；
4. 03b 与 L2-05-2/02b 的臂面需要"按臂产出信号序列"的 arm_base_source 新形状，本班未接
   （未接即按 `arm_base_source_unwired` 报错不出分，两卡维持 0 出分）；
5. L2-05-2/02b 的 emotion_index 腿必须带 stage='close_final'＋同键唯一性断言，
   在册先例 `emotion_linkage_exam.py:25,79-80,246-248`（本班未绑该腿＝该卡不出分）；
6. 引用陈旧转他班：02 卡面 `data_window_evidence` 的 000300"5284 行"与 §33.9 实测 5,286 行不同值，
   属主案卷在他班，本班只在新卡里追加本班实测行，不改母卡；
7. 六跑读数与 D1 甲的只读前置（两臂 `oos_ic` 皆 nan ⇒ delta nan 是下游）在册，本班未动判官面；
9. **批-A 余量四张实测今日一张都不能绑**（逐卡缺件见
   `docs/_working/examchief_campaign/07_batchA_remainder_blocker_dossier.yaml`）：
   A=L1-AGG/03 两腿数据面在全冻结窗内为空（C1/C2 源=daban_board_event，活面 `status:"missing"/obs:0`）
   ＋两处口径未定（raw_value vs percentile；趋势腿两条式）；
   B=L2-01-5/02 与 C=L2-01/03 是**臂面**（`ablation_arm`），但 `pillars_numeric` 无 NAV 级键 ⇒
   判官仍走 calibration 单序列路，四臂/六臂对照落在 `unjudged`＝考不到臂；且 C 的六指数腿
   `face_daily` 承载不了（表级 where 钉死 `symbol='000300'`，无 leg 级过滤）；
   D=L2-04/comparison/02 是唯一路由站得住的（`dual_arm`），但缺新 `ARM_BASE_SOURCES`、
   缺 880 码剔除面，且卡面冻的"单边 10bp"**无处落地**——见下列 10；
10. 三条执行器侧公共缺件（本班逐行读到，对本班 RRG 分同样成立，故读分必须带着这三行）：
    ①`ic_ir_min` 在 series 路**恒不被评估**（`calibration_exam.py:240` 写 None，`:357-360` 归入
    `numeric_keys_no_machine_face`，判官对 NaN 的处置是"跳过加败"）⇒ 卡面 ic_floor 的 ICIR 半边是空柱；
    ②净费真源 `config/exam_scale_cost_gate.yaml` **无 `net_fee` 节**（grep 零命中）⇒
    `_round_trip_cost_bp()` 返回 NaN（`:102-109`）⇒ series 路 `net_bucket_medians` 全 NaN、
    双臂路把它当 `cbp=0.0`（`:283-284`、`:296-297`＝**静默零费**，在册 silent-degradation 同族新面）；
    ③卡面 `min_obs_per_bucket` 在 `scripts/backtest/fexam/*.py` 里**零读取方**＝每桶最少样本数是装饰件；
11. 卡面对装置的引用陈旧（登记不擅改）：L2-01/03 的 `warmup_disclosure` 把 fail-closed 说成
    "件 train_window=500/warmup=30"，实读 `sector_distribution_comparator.py:55` 的 `warmup` **只在签名里、
    从未使用**，真正挡板是 `:63-64` 的 `len(data) < train_window + 10`；
12. 族宇宙无法按日 PIT：`sector_code_name_map` 无业务日期列且 `schemas/` 下无 DDL-as-code
    （grep 命中 0；实测行 `docs/_working/nightmine_campaign/04_exam_feasibility_census.yaml:999-1002`、
    `:3004`）⇒ 任何"按固定族算占比"的读数都只能做到**族口径固定**，做不到**成员时点固定**。
8. 投影归属卫生（本班自证一条）：`batch_creation_tokens.py` 的 render 会把 PG 全账重打进车道 YAML，
   本班袋里那版面比 dev 多 83 行、其中含 **infoaxis 班** 4 枚 `docs/_working/infoaxis/*.md` 的 token 条目
   ——那些是别人尚未入库的登记，随本班袋落地＝把他人工作写进我的 commit。
   处置＝`git checkout dev -- <册>` 复位（本班 token 已真在 PG，复位不丢任何东西），
   车道面与 dev 全等（hash f2c95205b51f 双向同值）＋门禁侧走 PG 第三源正证放行。

# 七、待裁（呈统筹/Owner，本班不代裁）

- 甲：八格 categorical 面要不要立项面板机判面（P0 族）？不裁＝三张 RRG 卡的 `response_monotonicity`
  柱永远只能出代理读数，"新进 vs 持续"这半命题考不了。
- 乙：批-B 5 枚卡的 sector_state 键面由谁补（examunlock 班属主 or 卡面删腿）？
- 丙：钉-1 品类注册归口（数据班补注册 or 判该表为私有派生件禁卡面引用）。
- 丁：**D10 甲批是否补签裁定号**（把"三张卡口径承在册 10/26 式"这条 Owner 裁决转录入册，
  按 #516/#515 先例写 adjudicator＝统筹令转录＋登记执行＝本班 sid）。本班**不代签**——
  Owner 亲笔面在本班可见的只有统筹令一句（根宪法 §5.11：对话内口头"Owner 说"不构成门禁豁免），
  而 RULING-REFERENCE 门只认在册号；点与不都由统筹/Owner 落笔，本班三张卡面一律用
  "统筹令（2026-10-14 晨）"作 authority_ref 文本，未写任何 `裁定#` 字样（防自触未登记号致死信）。
- 戊（**工具健康度上报，按 ESCALATION 要求人判、本班不静默绕**）：`--enqueue` 时网关打印
  `[ESCALATION] session_worktree_start 健康度自检失败 (session=st-examchief-20261014): failed，
  失败项=['lookup_audit dir writable']`。本班实测反证：主区与车道的 `.runtime/lookup_audit`
  均可写（该目录 01:00 被自检自己写入过 `._health_check_test` 探针文件），
  且 capability_lookup 审计在 00:2x 已真实落盘（五查四零命中的审计行为证）
  ⇒ 疑为**自检项判据面误红**（把"探针文件未删/主区根与车道根不同源"当成不可写）。
  袋仍入队成功（qid 尾号 0001），本班未加任何逃生旗。请门主/维护班定性——
  遵 Owner 在册正解：闸误报时改喂给闸的输入指向，不弱化、不白名单、不自修门。
- 己（批-A 余量排产菜单，缺件逐卡点名见 07 案卷）：
  **甲**＝本班域可续做两件装载形（emotion components 提取形＋六指数拆列形，零判据面）——
  但做完只解 C 的装载，不解 C 的宇宙对齐与跨臂对照，收益有限；
  **乙**＝把 B/C/D 的臂面并入 04_ 稿 P0（逐臂净值配对面）一次呈批——**本班认为最治本**：
  三张卡的判据主体都在臂对照上，单序列通道先天考不到臂（B 的四臂、C 的六臂、D 的双臂净值）；
  **丙**＝A 卡转数据班回补 C1/C2 事件面后另卡重考。
  本班建议＝**乙优先**；甲只在乙批下来后作附属件做，避免造出"能装载不能判"的半成品面
  （统筹此前否掉"建了没卡消费＝半成品"那一型，本班照同一条纪律提这一手）。
- 庚（**D8 探针读取形态缺陷＝本班 04:2x 实测定性，续跑班不代修、不代签开考**，证据全在 §五-4/5）：
  事实＝探针 `:72` 把 `ch_query_df` 对 `groupArray(name)` 返回的 **str**（`len=178`，形如 `"['trade_date',…]"`）
  按元素迭代 ⇒ 逐**字符**展开 ⇒ `"rrg_quadrant" not in col_list` **恒成立** ⇒ rc=2 自拒，任何数据面下都到不了 `decision:` 行。
  数据面不缺：该列真实存在（`c1_market.sector_state` 14 列含 `rrg_quadrant LowCardinality(String)`；
  全库 `%rrg%` 唯一命中；432,817 行；2022-09-01..2026-10-09；同进程 5/5 稳定读到）。
  ⇒ 卡面"先查口径再开考"这道纪律**自始至今从未真正执行过一次**（两个班、两次同命令都停在尺的自拒上），
  而"看着像执行过"正是最贵的那种失效。菜单（各带代价与可回退，本班不点）：
  **甲**＝单点修探针读取形态（改按行读 `SELECT name FROM system.columns … ORDER BY position`；
  判据常数 0.90／0.10 与 ±5 诊断档**一字不动**、卡面引句不动、分数册与判官件不动）→ 重跑 D8 拿真 decision，proceed 才开考。
  代价＝零资产净增（该件在 `.runtime/tmp/examchief/`，一次性只读、TTL 自然退役、不落库）；可回退＝无对象可 revert。
  **乙**＝把 D8 交叉核对升为**在册常驻件**（须走能力反查＋大白话简介登记＋净零声明）；
  代价＝与探针 docstring 首行自陈的"一次性只读、不建常驻面"规约冲突，且新增常驻面要过全资产净零闸——值不值由统筹判。
  **丙**＝今日不修，三张 RRG 卡随 09 包 P0 一并排，把"开考闸门"当作 P0 的附属缺件登记。
  本班建议＝**甲**（最小面、当天能拿到真 decision），但**本班不自签**：08 包 §2 C 明令"勿改尺"，
  而这一行改的正是"是否允许开考"的读法，属跨班裁断；遵 Owner 在册正解＝改喂给闸的**输入指向**、不弱化判据、不白名单、不自修门。
  不点后果＝RRG 三卡在 P0 批下来之后**照样出不了分**（闸门自己先死），且 §五 这条"尺永拒"的形态会留给下一班重新踩。
- 辛（**D8 首个真 decision＝halt 的口径差异呈批项**，四班 12:4x 实读，证据全在 §五·补2；本班不代裁"先查口径"的查法）：
  机械事实＝在册 10/26 式本班自算象限与被测件列 c1_market.sector_state.rrg_quadrant 在可比窗（6 日×189 码＝1134 格）
  一致率 0.5459<0.90、日截面占比差最大值 0.5556>0.10，双触发 ⇒ 卡面纪律 halt。
  带宽归因（±5 诊断档）＝**差异非带宽造成**（带宽档一致率 0.0、本方 CENTRAL 占比 0.978、theirs 值域无 CENTRAL）。
  分母事实＝theirs 对族宇宙 189 码仅覆盖 2026-09-24 起的 8 个交易日（爬坡期新面）。
  呈批菜单（各带代价，本班不点）：
  **甲**＝生成端参数对排：把 theirs 的生成端参数（EMA 跨度/中枢/基准价/写库时点）与在册 10/26 式逐项对表，
  把 45.41 个百分点的分歧归因到项；
  **乙**＝等 theirs 对族宇宙积累更长窗（现仅 8 个交易日）后用同探针重跑拿长窗一致率再裁——甲乙可并行不冲突；
  **丙**＝若对排查判定 theirs 与在册式同口径、分歧属爬坡期噪声 ⇒ 由统筹点名重跑 D8，decision=proceed 才开考。
  不点后果＝三张 RRG 卡继续 0 出分（卡面纪律 halt ⇒ 不开考，除非统筹/Owner 另裁）。

# 八、Owner 2026-10-14 批复五件的本班执行账（01:44 令；本班当班办完乙/丙/丁/己四件，戊无可动作）

| 批 | Owner 令 | 本班当班动作 | 落点与实测 |
|---|---|---|---|
| 继续 | 04:01 出分→04:20 收口→袋 2，不绕窗 | 分离进程 pid 40916 等窗（日志已证），04:20 一次性收口任务 id `fe2bc1b3-a9fc-49c6-a73a-811fd67abf1b`（跑完自删）；**未用 override 旗** | `.runtime/tmp/examchief/evidence/shift_batch.log` 两行挂起记录 |
| 乙批 | B/C/D 臂面并入 04_ 稿 P0 一次呈批＋判据面变更汇总表（含三公共缺件）＋甲项并呈 | 出 `09_p0_arm_face_pack_for_approval.yaml`：§1 承接 D1-D4 已裁（不重议）、§2 三卡同缺件论证、§3 五行变更表 W-1..W-5、§4 施工设计、§5 待批五点各给默认与不点后果 | 实测分母（01:5x 全树现算，命令与期望值在 09 包 §7，已逐字实跑对得上）：卡 530 枚／冻 `ic_ir_min` **229**／声明 `min_obs_per_bucket` **334**／桶型不在词表 **402**（缺 type 186＋off-vocab 216）／臂型桶 **120** 枚 38 种 |
| 丙批 | A 卡数据腿转条件轴情绪线，协调后另卡重考 | 出 `10_crossline_daban_backfill_to_condaxis.yaml`：三条实查事实（原料位/史浅 22 日/活面 `status:"missing"` 摘录）＋要回的三个数＋考卷侧三条后手；另列名一处**口径张力**（调研行说"akshare 仅存 30 日需回补"，终报说"daban=kline 派生可全史重放"＝两条不同路径，走后者须先钉与在产 builder 的一致性对拍）——本班不代拍 | 引用全部经本班 grep 命中后落笔（`condaxis/00_campaign_summary.md:23,38`、`sentiment/1_L1_thermometer.md:20`、`00_inputs/…research.md:180`、`matrix_campaign/rescued_tmp_20261007/probes/explore_out.md:25,36,47`） |
| 丁批 | 520 号补签，照 515 先例写 adjudicator，随袋正门落账 | 走意图 API 单口 `api.register(REG-RULING-001,"entries",payload)`→`publish_snapshot`（v28）；PG 实查 `entry_key=ruling_id=520 号裁定（PG 侧字面为"裁定"＋井号＋520，本册按令卡第五条去井号形书写，防 RULING-REFERENCE 门自触） / version=1 / updated_by=st-examchief-20261014`。**册面 YAML 不随袋**：本班 render 比 dev 多 64 行、内含 517/518/519 三条他班未入库条目，随袋＝归属篡改（Owner 10-10 明令"重打投影你不做"）⇒ 案卷内一律写"520 号裁定"去井号引用，投影追齐归册主车道 | 附带自报＋已复位：render 曾把 64 行进主区工作树，本班 `git checkout --` 还原（复位前实测该 diff 为 `+64/-0` 纯新增＝未毁任何在途行；留证副本 `D:/tmp_qoder/ruling_registry_render_with_517_520.yaml`） |
| 戊 | 自检误红已转维护线 | 本班不再动作；不再自修门 | — |
| 己 | 批-A 改口入设计稿（引 07 案卷） | 在 `docs/_working/mineloop2_campaign/05_composite_leg_face_design.yaml` **尾部追加 §9**（§0-§8 原文一字不动，遵 §33.8"更正另起不篡改历史"）：今日可绑＝2 张，其余逐卡缺件表＋归口；并把"按分档放量"的档改成**按缺件类型分档**（缺数据／缺臂面／缺装载形） | 结构自证：前 207 行与 dev 逐行等值、追加 21 行、lost=0、h2 节数 9→10、frontmatter 仍可解析 |

统筹 02:xx 确认三条入本账：①车道退回险情的处置（字节级复原＋改掉整树快进做法＋写入 08 包）批为"处置满分"；
②PE 排袋 3 的时序判断批为正确——"复合面零判官改动"是这张分的证据链命门，先改判官＝自污；
③PE 双触发条件（off-vocab ∧ 真走分位代理）量得对，3 枚 ordinal 假阳避开；
   23 枚 `event_flag_two_state_contrast` 的"命题是否本就按信号分位判"由统筹**并入 PA 包子问题**随 Owner 晨批
   （已登记在 09 包 §5 末，本班不猜）；丙的跨线转达由统筹写入条件轴晨班增补，本班不再向他班案卷落行
   （10 件 §5 末已记状态，防两处成文漂移）。

⚑ 一条自我约束登记：五批里**没有任何一条让本班改判据数值**，本班也没改——
`09` 包 §3 五行全是"加闸/补面/列名呈批"方向，费率值与 ICIR 定义一律待 Owner 给或在册件既有定义，
本班不拍数。

# 九、复核命令（每条都实跑过，期望值随命令）

⚑ 编号更正留痕：本节原为"八、复核命令"，本班 02:0x 追加"八、Owner 批复五件执行账"时
把原标题行当锚点吃掉（在册自犯形态 `edit-append-anchor-consumes-heading` 本班今夜第二次撞，
第一次是初稿时间标签）；已当场发现并以此编号修复，结构自证见下：

本件相对 dev 的行差实测＝**+55/−1**：唯一被删行是旧标题行 `# 八、复核命令（每条都实跑过，期望值随命令）`，其替代行就是本节现标题（改名不改内容，零信息损失）——袋 2 落地时该 −1 属此因，非回退弹。

```
cd /d/ZephyrAlpha/.worktrees/st-examchief-20261014 && grep -c '^# ' docs/_working/examchief_campaign/00_ledger.md
```
期望：`10`（〇 一 二 三 四 五 六 七 八 九 十节齐，其中"九、复核命令"在位）



```
cd /d/ZephyrAlpha/.worktrees/st-examchief-20261014 && PYTHONNOUSERSITE=1 \
  python -m pytest tests/backtest/test_card_binding.py -q --basetemp=D:/tmp_qoder/bt4
```
期望末行：`107 passed`（跑前须先 `mkdir -p` 该 basetemp，不存在会以 FileNotFoundError 集体 ERROR）。

```
cd /d/ZephyrAlpha/.worktrees/st-examchief-20261014 && PYTHONNOUSERSITE=1 \
  python D:/ZephyrAlpha/.runtime/tmp/examchief/drift_r7.py snapshot --root=D:/ZephyrAlpha/.worktrees/st-examchief-20261014
```
期望：`scores_rows` ≥73、`judge_diff_vs_dev` 为空串、两册 `lost=0`。

```
cd /d/ZephyrAlpha/.worktrees/st-examchief-20261014 && PYTHONNOUSERSITE=1 \
  python D:/ZephyrAlpha/.runtime/tmp/examchief/repro_d10_probe.py
```
期望末行（逐字）：`WROTE D:\ZephyrAlpha\.runtime\tmp\examchief\evidence\repro_d10_probe.yaml ch_queries=6 板块数=4`
＋四行 `RS相关=0.488 / 0.3013 / 0.3889 / 0.4997`。

```
cd /d/ZephyrAlpha/.worktrees/st-examchief-20261014 && PYTHONNOUSERSITE=1 python -c "
import sys; sys.path.insert(0,'src')
from zephyr.gov_enforcement.commit_gates.create_guard import _pg_confirmed_token_files as f
c=['docs/03_modules/_domain_backtest/exam_cards/entry_flow/L2/TDM-E-L2-02-1__calibration__02b_rrg_quadrant_10_26_caliber.yaml',
'docs/_working/examchief_campaign/00_ledger.md']
print(len(f(c,set())),'of',len(c))"
```
期望：`2 of 2`（五枚新建件的 creation_token 经 **PG 账本正证**在册；本班把车道里的
`capability_canonical_file_registry.yaml` 复位成 dev 现值字节、**不随袋带投影**——
渲染面里同时含 infoaxis 班尚未入库的条目，替他班落地=归属篡改；
投影滞后形态由门本体 PG 第三源 `_pg_confirmed_token_files` 正证放行，非豁免）。

## 四班追加复核命令（st-examchief2-20261014，每条都实跑过，期望值随命令）

```
cd /d/ZephyrAlpha/.aidrafts/st-examchief2-20261014 && PYTHONNOUSERSITE=1 \
  python D:/ZephyrAlpha/.runtime/tmp/examchief/d8_rrg_crosscheck_probe.py
```
期望末段逐字：`WROTE D:\ZephyrAlpha\.runtime\tmp\examchief\evidence\d8_crosscheck.yaml ch_queries=2`
＋`quadrant_agreement_in_register_10_26 = 0.5459`＋`daily_spread_max_absdiff = 0.5556`＋
`decision = halt（差异超 10% 线＝先查口径再开考）`（探针只读无状态面，重跑应同值；
让路窗 21:00-22:30/01:00-04:00 内自拒 rc=3＝在册让路面非故障）。

```
cd /d/ZephyrAlpha/.aidrafts/st-examchief2-20261014 && PYTHONNOUSERSITE=1 python -c "
import sys; sys.path.insert(0,'src'); sys.path.insert(0,'scripts/backtest')
from fexam.ch_data import ch_query_df
codes_df = ch_query_df(\"SELECT DISTINCT sector_code FROM c1_market.sector_code_name_map WHERE code_family IN ('industry_l1','industry_ths')\")
codes = sorted(codes_df.iloc[:,0].astype(str).tolist())
print('family_universe_codes =', len(codes))
inlist = ','.join(f\"'{c}'\" for c in codes)
r = ch_query_df(f'SELECT toDate(trade_date) AS d, uniqExact(sector_code) AS codes FROM c1_market.sector_state WHERE sector_code IN ({inlist}) AND rrg_quadrant != \'\' GROUP BY d ORDER BY d')
print('sector_state_days_for_family_codes =', len(r))
print(r.iloc[0,0], r.iloc[-1,0])"
```
期望：`family_universe_codes = 189`、`sector_state_days_for_family_codes = 8`、`2026-09-24 2026-10-09`
（§五·补2 第 3 条分母事实的真源查询；本班首跑曾把映射列误写成 family 吃 404，改 code_family 后通——留痕不抹）。


# 十、矿考四班·PE 止血闸施工账（2026-10-14 午班，sid=st-examchief2-20261014；规约=11_pe_shadow_plan.yaml，统筹 2026-10-14 批）

1. 时序前提：08 包 §5.0/11 稿 §6 的硬时序对象（"首张 RRG 分＋其袋落地先于动判官件"）在 halt 下无对象
   （§五·补2 第 7 条），halt 账已随袋 A（3703046c）落地后再动 `calibration_exam.py`＝证据链无可自污对象。
2. 施工面（唯一落点，warn-only/shadow）：`scripts/backtest/fexam/calibration_exam.py`——
   ①新观测器 `_bucket_type_off_vocab`（规约 §2 条件①：buckets.type 声明且不在 `_BUCKET_TYPE_N`
   词表且不匹配 `quantile_<n>` 形；无 buckets 声明＝没冻切法，不报）；②新披露装配 `_bucket_caliber_proxy`
   （条件②＝信号唯一值数 > 实跑桶数＝真走分位分支；ordinal 按档值分桶不报＝钉住 §3 那 3 枚假阳；
   mono 无面 None/NaN 不报＝披露只注解存在的数）；③`_unjudged_pillars` 加 keyword-only 形参
   `signal_unique`（缺省 None＝既有调用面零破）并在返回面追加披露键
   `numeric_keys_bucket_caliber_proxy`（载荷逐字照 11 稿 §2：buckets.type 原文名／n_buckets_used／
   mono_spearman=按信号值分位分桶的代理读数（非卡面冻的格）／mode=warn_only）；
   ④`run_card` 单点观测位：仅 series 路取 `int(signal.nunique())` 传入。
3. 越权面零：不进 `fails`、不改 verdict、不改任何数值、不加阈值、不新建 gate/配置节/常驻清单
   （shadow 旗＝件内常量与注释带规约路径；净零声明照 11 稿 §7）。
4. 行形状面：metrics／unjudged 既有键零动——已出分行与未出分行的既有形状不变；新行仅在 unjudged
   面可能多该披露键（＝11 稿 §7"观察期台账行由分数册自身承载"）。回退判据 R-a 的读法据此＝
   在册 73 行的 outcome/数值列零变化（73 行是冻结字节，本施工不触碰任何已落地行）。
5. scope 边界（如实登记）：披露只落 series 路顶层 metrics；dual_arm 路的嵌套臂面
   （arm_open/arm_base 内的 mono）与 event 路不在 11 稿 §2 文字内（规约未指定双臂取哪臂信号），
   本班不越权披露——若 enforce 议点要扩，属再批事项。信号唯一值数取注入序列 raw 面
   （对齐丢行只在"整档值恰好全落目标 NaN 行"这一 exotic 形态下可能高报；R-c 观察窗正是钉这个）。
6. 测试（同批合法，全绿实跑）：`tests/backtest/test_calibration_exam.py` **72 passed**（原 66＋新 6：
   T1 改前/改后对拍 verdict/fails/metrics 逐位等值（NaN 感知比较——dict 相等把 nan!=nan 判假是
   伪影非漂移，测试里留注释）＋unjudged 恰多一披露键｜T2 词表内不报｜T3 4 档离散信号不报（删条件②必红）｜
   T4 连续信号必报且禁进 fails｜条件①词表边界（quantile_7/大小写/空 buckets）｜mono 无面不报）；
   `tests/backtest/test_card_binding.py` **107 passed**＝零连带（run 面端到端行形状不被破坏）。
   两条均 `PYTHONNOUSERSITE=1`＋仓外 `--basetemp`（D:/tmp_qoder/bt_pe1、bt_pe3）。
7. 完成判据（照 11 稿 frontmatter）：2026-10-21 观察期满且 §5 判据齐 ⇒ 议 enforce（须再批）；
   任一回退条件触发即 `git revert` 本 PE commit，不议不改。

## §七辛-补（甲案对排结论，st-examdx2-20261014）

**结论＝B：存在实质参数/口径差异（四项），非"纯爬坡窗+无 CENTRAL 档"所能解释。** 本班只读诊断：零判据/零卡面/零探针改动、零出分、零 CH 写；CH 只读 15 次（让路窗外、无 override），证据=`.runtime/tmp/examchief/evidence/d8_jia_duipai_evidence_st-examdx2-20261014.yaml`（本班全新实跑；前役 st-examdx-20261014 同题未落账件 `d8_jia_duipai_evidence_st-examdx-20261014.yaml`（14:17，额度中断）留作旁证，其输入侧读数与本班重合）。引用面自证：两造生成端六关键件（02b 卡/02 绑定册/card_binding.py/sector_rrg.py/sector_state_aggregator.py/sector_state_pipeline.py）自探针时点 dev=1f82fcb26206 至今 `git diff --stat` 空输出＋工作树对 HEAD 等值（02b 卡在树呈"staged 删除+未跟踪重建"半成品态、磁盘=HEAD 逐字节等值，归属他班在途，本班不代清）。

逐参数对排（本方在册值＝主区文件:行号；theirs 实测＝CH 只读或其在册代码:行号）：

| # | 参数 | 本方在册（D8 探针承接面） | theirs（sector_state 生成端） | 同/异 |
|---|---|---|---|---|
| 1 | 构造式 | RS=100×P_sec/P_bench、RS-Ratio=EMA(RS,10)/EMA(RS,26)×100、RS-Mom 二级同构（02b 卡 signal_derivation :145-148；sector_rrg.py:138-145） | 直调同册 `compute_rrg_series`（sector_state_aggregator.py:416，short/long 不传＝缺省） | 同 |
| 2 | EMA 跨度/种子 | 10/26；alpha=2/(span+1)、种子=首值无预热（sector_rrg.py:47-48,93-101） | 同一函数同缺省 | 同 |
| 3 | 中枢/分档边界 | 100 中枢四分、无带宽项（classify_quadrant sector_rrg.py:153-157；02b 卡:54"在册四分规则无带宽参数"；±5 只存在于探针诊断档与 02 卡已废止冻结注） | 同一 classify_quadrant；落库值域实测恰 4 值小写 improving/lagging/leading/weakening、无 CENTRAL（Q5） | 同（带宽两侧生产面皆无——四班 §五·补2 第 4 条归因成立） |
| 4 | whipsaw 确认 | 无——探针逐日落 raw 象限（probe:104-105；卡面/册均无确认项） | `confirm_quadrant_series` 2 日连续确认后取末点小写（aggregator:417-419；sector_rrg.py:49 DEFAULT_CONFIRM_DAYS=2） | **异（实质）** |
| 5 | 基准价 | 000300 收盘（c1_market.kline_index where symbol='000300'：card_binding.py:222,404-407；02 绑定册 bench leg :521-526＋审阅注 :546；02b 卡:34-36＝统筹 2026-10-14 增补裁定） | 880001.SH 收盘（c1_market.kline_sector_880：sector_state_pipeline.py:84-88 `_BENCH_SQL`；恰同 sector_rrg.py:120 docstring 缺省意图） | **异（实质，量级最大）**：两基准日收益在可比窗 6/6 日非零差、mean 0.19%/max 0.35%（Q9）；theirs 有效窗（2026-06-01..10-09）两基准比价系统性漂移 +5.738%（本班补测）⇒ RS=100×P/P_bench 水平位移，近 100 边界码大面积翻档 |
| 6 | 历史窗长 | 全史族面板∩基准日轴＝1257 日（02 绑定册 panel leg 全量 kline880 族面板，装载 SQL card_binding.py:103-109；D8 回执 aligned_days=1257） | 75 交易日硬窗（pipeline:65 `_PANEL_LOOKBACK_DAYS=75`、:66-67 日历 115 日、:236 bench LIMIT 75、aggregator:416 尾切 n=min）⇒ 有效输入 62..75 点 | **异（实质）**：EMA 种子=首值 ⇒ 窗长直接进值；族码 kline880 全史在库（2021-08-02 起 189 码 236387 行，Q4）⇒ 75 日是**管线参数选择、非数据爬坡** |
| 7 | 最小数据量 | 62 日＝long×2+short，函数自守 raise（sector_rrg.py:132-134；02b 卡:155） | 同源同值（RRG_MIN_LEN=62，aggregator:64-65,412） | 同 |
| 8 | code_family 宇宙过滤 | families=[industry_l1,industry_ths] 经 sector_code_name_map＝189 码（02 绑定册:516-517；SQL :106-107） | 生成端**无族过滤**——写 kline880 全部面板码（rrg 非空全表 728 码）；族过滤只在读取侧套用 | 比较面同 189 码；生成端 theirs 写超集（结构差，不影响本次宇宙一致性） |
| 9 | 复权/停牌处理 | 880 指数收盘原值无复权概念；(日,码) anyLast 去重（card_binding.py:104-105）；缺日＝per-code 与基准内连自然落（probe:102） | 同为 880 收盘原值无复权；FINAL+Python (code,date) 去重写胜（pipeline:198-217）；缺日＝尾切 n=min 逐元素 zip **无日期再对齐**（aggregator:416）——实测族码 1/189 在有效窗内日数≠基准（Q8），该码存在日期错配暴露 | 基本同（1 码错配，量级小非主因） |
| 10 | 时区/日界 | toDate(trade_date)，无时区换算（SQL :104；probe:88） | 同源同式（pipeline 写 kline max(trade_date) 日期面），无换算 | 同 |
| 11 | 写库时点/stage 语义 | 无落库——探针现算单面 | 双面：close_final ts=15:10 当日鲜算＋pre_open ts=09:15＝**次日贴昨日定格拷贝**（pipeline:425-449，骨架稿§6 设计；Q6 ts 实测吻合）；族码 8 个有值日期＝4 鲜算日（09-24/09-28/09-30/10-08）＋4 拷贝日（09-25/09-29/10-01/10-09，其中 09-25 与 10-01 两 kline 源皆无＝非交易日，Q1/Q7）；**D8 比较面 1134 格中 378 格（33.3%＝09-29、10-09 两日）theirs 值为前一交易日滞后值**（Q3b：探针原式 anyLast 无 stage 过滤 vs close_final-only 分歧 756/1512 格；每 (日,码) 恰一 stage、anyLast 无歧义，滞后是写库面结构性的） | **异（实质）** |

（chief 清单"分位基准"项：两造象限链均无分位基准——RS 比价锚=100 中枢即上表#3；theirs 另有 P90 分位等辅助成分（aggregator:71 `_ROTATION_SPEED_P90`、momentum_pct 多 TF 分位）但**不进 rrg_quadrant 判定**，该项两造同无。）

四项实质差的归口（本班只指格、不代裁改哪端）：
1. **基准价**：卡面端 000300＝统筹 2026-10-14 增补裁定钉死（02b 卡:34-37，且 :37 已预留"RRG 基准唯一化再统一呈批"口）；管线端 880001.SH＝数据线 pipeline 代码。跨线基准确一化＝统筹/Owner 呈批项。
2. **窗长 75 日**：数据线 sector_state_pipeline 参数（:65）。
3. **确认平滑 2 日**：信号线 aggregator（:417-419）vs 考试线卡面承接（无确认项）；对拍基准面取 raw 还是 confirmed 须呈批点名。
4. **双 stage 滞后格**：theirs 管线设计（盘前=昨日态）×探针读取未滤 stage（庚甲同款读取形态性质；一次性件，本班不代修、只量化）。

对呈批菜单的含义：**乙案前提（两造同口径、分歧属爬坡）不成立**——窗长非数据稀缺（全史在库），基准/确认/写库时点三项不随时间消失，"等 theirs 攒长窗后同探针重跑"会复现 halt；丙案（统筹点名重跑 D8）的机械前置＝先裁四项归一或明示"以哪端为准"对拍，否则任何重跑双触发照旧。另实测对乙案不利的事实：theirs 鲜算面出勤＝8 个有值日仅 4 个 close_final（09-29、10-09 是交易日但只落 pre_open 未落盘后），按此出勤攒鲜算窗速度减半。
