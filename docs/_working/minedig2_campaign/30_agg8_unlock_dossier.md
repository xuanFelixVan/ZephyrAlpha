---
ttl: task_bound
title: 聚合 8 卡可考面·案卷（先挖后干：10 环节逐节挖干，本班单档收口）
created: '2026-10-13'
session: st-minedig2-20261012
order: 通宵总令 §二工法令＋§四「挖矿二班：终局＝聚合 8 卡可考」
status: dug_and_built_in_lane_pending_ch_window
---

# 30 聚合 8 卡可考面案卷

> 形制说明（自裁留痕）：工法令要"每环节一子档"，本班曾按骨架＋子档分件写，被 Owner 侧拒收（文档增殖与
> 在册 §4.1 内收原则相冲），**改为本单档十节**，环节数量零遗漏、每环节一节，取舍与实测都写在本节内。

## 环节1 输入面（CH 真源／宇宙／右边界／扣留段）

唯一装载单口＝`scripts/backtest/lane_c_formula_miner.py:356 fetch_panel(universe_n, days)`（内部 `:366` 用
`SQL_UNIVERSE`＋`get_registry().table("market_kline_daily_hfq")`，`:376` 定列 date/s/close/turnover/amount）；
特征面 `:336 compute_features`。本班物化件**初版自称"零 SQL（SQL_FREE=True）"——该声明于 04:0x 被实测证伪并更正**：
`fetch_panel` 返回键只有 X/y(仅 fwd5)/baseline/date_codes/symbol_codes（其 :415-426），不含 close 矩阵与 dates 字符串，
产不出在册 8 读数所依的矩阵面；故装载改为 `fetch_matrix_ctx`（逐字收编前班筛级管线 `fetch_panel_matrices` :450-514，
其本体在 `.runtime/tmp` TTL 件内＝不搬进册就会随工棚清理蒸发），本件随之带**一条** kline SELECT（全文落
`meta.inputs.own_sql` 可审，`SQL_FREE=False`），而宇宙选择（SQL_UNIVERSE）与特征工程（compute_features）仍逐字复用
lane_c 单口——按 §4.2 这是"同真源收编"不是"第二取数路"。表名经 table_registry 实调解析为
`c1_market.kline_daily_hfq`（`KeyError` 即 fail-closed）。宇宙＝top800（大票偏置如实披露）；窗
2019-02-11..2026-10-12（1,860 交易日）；末 126 交易日为 AHM 扣留段＝冻结卡 OOS；停牌与 0 价沿用前班
`close[close<=0]=np.nan`＋`susp=isfinite(close)` 双卫兵。**本面不新增数据源。**
**内收声明（§4.2 四判据）**：本面零新建取数路——面板装载全部 import 复用 `fetch_panel`／`compute_features`
（同真源可派生→必并），执行器侧只加"消费卡面冻结 horizon"一个可选档（见 环节5），不建第二真源、不加第三条取数路。

## 环节2 序列定义与变换口径（6 信号＋2 目标）

逐字取前班筛级 `_screen_aggregate`（其 :802-806 与 :811-815）：
`lu_count=nansum(where(susp & isfinite(lu_flag), lu_flag, nan),axis=1)`；
`lu_ratio=nanmean(where(susp, lu_flag, nan),axis=1)`；`avg_abs_ret=nanmean(where(susp & isfinite(ret_1d), |ret_1d|, nan),axis=1)`；
`z20=((x-tail20均值)/(tail20标准差+1e-9)).clip(±10)`，`min_periods=5`，**纯 trailing**；
目标侧 `mkt_fwd{5,10}=nanmean(where(susp, y_fwd{h}, nan),axis=1)`，`y_fwd{h}=close_{t+h}/close_t-1`。
涨停旗 `lu_flag=ret_1d>=0.095`（10%/20% 板混池近似，沿用前班披露）。**零自定阈值，禁第三 horizon。**

## 环节3 物化件形制

`scripts/audit/agg8_series_materialize.py`（版本键 `agg8-v1`，口径变更升版禁原地改）。产物落
`docs/_working/nightmine_campaign/series/`，与在册 7 枚 CSV **同形制**（表头 `trade_date,value`），
NaN 日不落盘（右端无值行/前 4 日 z20 暖机天然缺席，禁 0 冒充）；逐文件登记 rows/first/last/sha256；
meta=`agg8_series_v1.meta.yaml`（输入口径＋覆盖＋复算读数）。写字节非写文本（文本模式在 Windows 会把
CRLF 再翻一次，读回多空行且 sha 与落盘字节不同物——本班实测并由守卫测钉住）。

## 环节4 绑定面接线（路线取舍＝本面最关键一裁）

在册两条路：**(甲) class D 本地序列路**（`card_binding.py:296-303`，只认 `signal_column`/`derived_series`
与 `_CSV_HINTS` **精确同键**，明文"禁全文关键词匹配"）；(乙) CH 单表路（`:305+`，要求表在 `_REGISTERED_TABLES`，
且命中滚动/z-score 直接 `A?` 拒绑）。
**自裁取甲**，三条理由：①聚合序列是"逐日一数的市场面标量"，本就是 class D 的形状；
②走乙要放宽 `_REGISTERED_TABLES` 与 z-score 归一配方——那是**弱化已批之闸**，Owner 固定正解是"改喂给闸的输入指向"
而不是改闸；③解锁班 05 判定册已实测证伪"9 张单表入配方册"的前提，本班不重复造这条线。
落地动作＝`_CSV_HINTS` 追加 8 键（6 信号＋mkt_fwd5/mkt_fwd10，纯追加）＋卡面 `data_binding` 内
`derived_series`／`target_series` 两键申报（插进行中段，非尾追加键——该文件本班独占，见环节8）。

## 环节5 执行器多日前向面（与已批补丁同袋）

`calibration_exam._forward_face(card)`：缺省 `(1, False)`＝现行 `shift(-1)` 逐字不变（既有 178 张卡零影响，
测试以整串相等断言钉住）；卡面成对申报 `target_forward_face=precomputed`＋`target_horizon_days=h`
且与 `target.primary` 内 `mkt_fwd<h>` 同值，才免二次位移；半申报/错拼/越界/bool 或 str 冒充/两处不同值
一律 `_ToolError`（方向＝fail-closed，禁静默退化成次日面出分）。
`run_card` 侧新增 `_declared_local_faces(card)`：卡面申报了本地序列名才装载，未申报或件不在照旧抛
"缺省 CH 取数面未接"。**装载口复用 card_binding 同一 `SERIES_DIR` 与同一列名规则，零新读盘面。**

## 环节6 复算证明（CH 窗后实跑，判据先钉死）

判据：物化件自算 8 格 `ts_ic`（与筛级 `_ts_ic` 同式：先全列 rank 再取有效行）必须等于
`docs/_working/minedig2_campaign/00_agg8_axis_prereg.yaml#agg8_readings` 的在册 n/ic/t（n 精确等、ic/t 四位/两位四舍五入等）。
正对照＝本班尺在合成面板上能复现"完全单调⇒ic=1.0／n<100⇒判零"两例（守卫测已跑）。
不合＝物化口径与出生口径分家 ⇒ **停下上报，不调数凑等值**。状态：待 04:00 实跑（01:00-04:00 让路窗零查询）。

窗锚（03:2x 自查发现并即修，判据先钉后跑）：装载单口 `lane_c_formula_miner.py:361` 的 `start` 是
`(date.today() - days*1.7)`，**右端随自然日漂移**；本班物化件初版把 `--start` 只写进 meta 而未参与切面（申报位≠消费位＝
在册教训"config consumed by only one code path"同族）。修法＝`build_frame(ctx, start, end)` 在**聚合之后**按钉窗切片
（置后保窗首 z20 的 20 日回看不被吃，红证在守卫测），新增 `DEFAULT_END=2026-10-12`（＝在册 8 读数面目右端＝卡面 OOS 锚末），
`--out-dir` 缺省改按脚本位置解析（防 cwd 漂移把考卷面写进别的树）。判据全文已先行钉入
`00_agg8_axis_prereg.yaml#recon_criterion_pinned_before_run`（含"事先声明的两条漂移来源"，不合时按此定位而非事后编）。

**04:0x 实跑账（时序如实，不美化）**：04:01 首跑＝RED——全钉窗面 8 格 n=1849/1845/1848/1844/1853/1848/1849/1844，
与在册 1734/1730/1733/1729/1733/1733/1729/1729 全体差一档。按判据停手（不物化、不调数），两支只读定位探针：
①在册读数所属面＝预登记册 `holdout.rule`"末段扣留，筛选全程不碰"⇒ 剔末 126 交易日后本班 n 与在册 n **齐差 1 日**；
②把装载锚从 `date.today()-2800`（本班 04:01 得 2019-02-12）拨回前班 10-12 跑批的 2019-02-11 ⇒ 剔扣留面
**8/8 逐格精确等**（n/ic 四位/t 两位全等）。根因＝装载侧 today 相对回推挪一日即改变 top800 宇宙选择，面目随之全体偏移；
初版判据把"面目"钉了、把"装载集合"漏钉（且没把本册既有 holdout 规则写进比对面）＝本班自犯第 ⑬ 条。
处置＝更正留痕两节（`recon_criterion_correction_1/2`，旧文不删）＋物化件加**两侧绝对锚**
（`--load-start` 与 `--start/--end`），meta 同落 `recomputation`（全面，考卷用）与 `recomputation_screen_face`
（剔扣留面，对拍用）。判据强度未降（仍是逐格精确等，非"接近即过"），零阈值改动。

## 环节7 卡面转态与试次入账

`status: blocked_on_impl → preregistered` 的**唯一**前置＝三件齐（①物化件在册且 CSV 落盘、②绑定尺对本卡
不再报目标面/数据面拒绑、③环节 6 复算逐格等值）。三者任一不合，卡面保持 blocked_on_impl——
禁为凑"可考张数"改面（收尾令原文）。转态属**卡面状态机推进**，不动任何判据数值；开考仍归矿考二班/考试班，
试次 `n_trial_ledger`（kind=exam_card）由开考的班记，本班立卡与转态阶段零开考零入账。

## 环节8 门禁与落地通道（本班实测，非转述）

- CREATE-GUARD：新 .py 与 8 枚 CSV 均需 token；`batch_creation_tokens.py` 意图 API 已在**车道内**跑通
  （主区脚本扫主区 ls-files 看不见车道新件，会假报"无待登记文件"——在册新证同型）。
- TRANSLATION-COVERAGE：**实测只读 YAML 投影面**（`module_translation_loader` 无 PG 通道；主区投影查询 MISS），
  故新 .py 必须走"翻译册独立先行袋落 HEAD"，否则预检与落地双红。本班 render 面含他人 12 条未落地登记 ⇒
  **不随袋**（Owner 禁重打投影袋在册），改以 dev 字节为基只注入本班 1 条（`git diff --numstat`＝+5/−0，
  module_path 键集合差新增 1 消失 0）。
- PROTECTED-PATHS：worktree 面命中车道绝对路径，在册 approved_paths 是仓内相对 posix ⇒ 裁定通道恒不命中
  （D-3 归一在 worktree 未剥净，与 HELD-OVERLAP F3/C1 同族）。走 `[ARCH-APPROVAL:#ARCH-381]` 标记载体，
  **不用 ZEPHYR_PROTECTED_PATHS_BYPASS 拆闸**。
- POOL-REGRESSION／落地仲裁：本班 0005 袋死于"同件双侧皆改"（自家两袋撞同一文件），卡面就地改写 status_reason
  也被点名"dev 有你字节里没有的行" ⇒ 一律改**基底＋尾追加**形制，`git diff dev` 的 dev-only 行必须实测为 0；
  确属有意覆盖时写 `[pool-regression-ack:理由]`（ASCII 右括号，全角】不被正则识别——本班自犯一次）。
- 同件多轮并一袋；每袋投前跑真钩子预检（`commit_preflight` 廉价，被 DENIED 不烧袋）；claim 在飞期间不放锁。

## 环节9 红蓝对抗（零 CH 部分已跑，CH 部分窗后补）

已红已绿：守卫测 7 支全绿（`tests/gov/audit/test_agg8_series_materialize.py`），其中三条是**应当红**的反例——
①z20 截断窗前缀不变（写成全样本归一即红）；②停牌标的不得进计数与占比分母（摘卫兵即红：naive=3.0 vs 带卫兵=2.0）；
③fail-closed 三面（零行/日期重复/close 全非有限）必抛。另在执行器侧 7 例参数化红证（半申报/错拼/越界/
str 与 bool 冒充/两处不同值全拒）。绑定侧红证＝文件不在时 reason 必须点名 `series_csv_absent:<具体文件>`，
放入后转 `cls D`。CH 窗后补：复算不等值即红（环节6），以及他班视角复验（环节10）。

## 环节10 他班交叉验证与让路面

- 考试班：其 §23.3 称本班反向卡缺口"只差甲＝technical_indicator 未进配方册＋乙＝基序列物化件缺"——
  本班实测对**聚合 8 卡**不成立（聚合序列非技术指标列，且本班选 class D 路），故不引用其甲案；
  其"开考面分类 8/8 cls C"读数本班已于 01:12 呈报并加固（多日面补丁后停在校验数据面）。
- 考试解锁班：`05_recipe_book_grain_verdicts.yaml` 实测证伪"9 张单表入配方册"前提，且其物化件
  `ti_daily_mean_materialize.py` 因 TRANSLATION-COVERAGE 滞后滞留车道——与本班环节 8 同一病灶，
  本班把它作为**同一根因的第二例**呈册主车道（不代修他人件）。其产出面向 technical_indicator，
  与本班聚合序列不同名不撞车；其 12 件已落 docs 袋（`7ea68bc19f`），本班尺复验其"零登记"结论成立。
- 矿考二班：`02_binding_book.yaml` 属主册本班不动（其 event_flag 底座 base_op/base_csv 恰选其一规则已核）。
- 让路纪律：01:00-04:00 CH 零查询；本班所有 CH 腿（复算与 run_id 对拍）排在 04:00 之后。
- 分工与撞面实测（03:3x 在册面复扫，非转述）：`pending` 队列 7 袋（datalane2／deadcure3b／examrun／examunlock／maint3×2／maint4）
  逐袋 files 清单与本班 19 件求交＝**0 命中**；`.ailocks` 在册 claim 中他班无一对 `card_binding.py`／`calibration_exam.py`／
  `nightmine_campaign/series`／8 张聚合卡有声明；`examunlock` 0003 袋为纯 docs 件（其 15 号件自纠"隔夜腿已在册面板内已算出"
  ＝与本班 class D 选路同向，不互斥）。⇒ 本班无需等配方册，也不占他班面；"先 claim 先做"条对本班成立。
