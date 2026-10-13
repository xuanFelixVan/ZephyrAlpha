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


# 八、复核命令（每条都实跑过，期望值随命令）

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

