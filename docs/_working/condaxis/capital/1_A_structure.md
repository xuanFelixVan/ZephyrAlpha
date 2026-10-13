---
ttl: task_bound
title: A 筹码结构快照——获利盘/阻力分位/集中度形态/股东户数/CGO 对偶（施工前挖矿作业簿）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: A 环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# A 筹码结构快照（1_A_structure）

> 契约定位（研究册 §2.2-A）：存量体检，日频——"筹码现在什么结构、供给从哪来"。回答：获利盘占比（止盈供给）、上方阻力地图（A2 阻力最小方向可算化）、集中度形态（方向选择临近 vs 无共识）、股东户数（低频硬验证）。
> 本册零冻结：A2/A3/A4/CGO 的判据、阈值、门柱全部"待 P2 预冻结"；A1 考试卡的门柱设计也只给结构不给数值。

## §1 逐项台账

| 件名 | 仓内真源路径:行号 | 现状标记 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| **A1 获利盘占比** CYQ chips_winner | `src/zephyr/factor/technical_indicators/chips.py:289-327`（CYQ 类）；内核 `compute_chip_metrics:181-248`（400 bins 迭代衰减，PIT 只用过去+当日） | ✅实查在产：头注 `[MATURITY] production`（chips.py:7）；CH 实查 `c1_market.technical_indicator` period='daily' 覆盖 2019-01-02..2026-10-12、~1,975 万行、chips_winner 非空日均 ~5.5k 标的（2026-10-08=5,562 uniq symbol） | internal_compute_provider 包级 autodiscover（chips.py:5）→ c1_market.technical_indicator 宽表列；TDM-E-L3-12-3 筹码分布分析节点（config/trading_decision_map.yaml:2452-2455、边:6263）经 chip_distribution_engine winner 剖面 | **消费端考试卡**＝chip_distribution_engine（MOD-REGIME-005 trial）转正唯一通道（裁定 #257④）；宽表→考试卡绑定算子未建 | ②下游：考试卡（见 §3.1 接入设计）；⑥字段：chips_winner/chips_avg_cost/chips_cost_5/15/85/95 六列已在宽表 |
| **A1' winner 剖面**（trial 引擎侧） | `src/zephyr/regime/features/chip_distribution_engine.py:352-434`（compute_winner_profile，直调 chips 内核，换手率三源解析：显式入参>df 列>float_share 派生） | 🔨 trial（chip_distribution_engine.py:11 `[MATURITY] trial`——2026-09-16 #257④ 打回：零消费端+伪分布；量纲已修；SW14 处方①接线已做） | 声明面 MOD-REGIME-002（实际零 import，2026-09-15 CHIP-2 审计）＋TDM-E-L3-12-3 | 同上——转正靠消费端考试卡 | ②下游：考试卡+regime 管道；④后端：本文件自身无第二实现（禁 regime 域第二套分布） |
| **A2 阻力分位数** upside_resistance_quantile（候选名） | 可派生自同内核：`_ChipGrid.day_metrics:163-178` 现只出 6 聚合值；分布质量在 `self.dist`（400 bins）内部 | ⬜ 未建（研究册 §9 A2：内核可派生，指标未建+判据待冻结） | 无 | 价上方 5%/10%/20% 缓冲带内历史筹码密度＝分布带质量计算，day_metrics 不输出；需扩内核或新建指标类 | ③算法：CGO/参考价学术对偶（Grinblatt-Han 2005）；④后端：`chips.py` 扩列 or 新类（§3.2 两条路线）；⑥字段：OHLCV+turnover_rate 已备（kline_daily 1990-12-19 起 1,169 万行） |
| **A3 集中度形态**（单峰密集/双峰/发散） | 标量集中度已有：SCR（chips.py:330-351）＝集中度(90)、CHIP_CONC_70/90（chips.py:400-439）；**形态**（峰结构）零实现 | ⬜ 形态未建；🔨 标量层在产（scr/conc_90/conc_70 宽表列全覆盖，CH 实查 2026-10-09 daily 行 24,183/24,183 非空） | 同 CYQ 落表消费 | D21 蓝图明示待"单峰密集度全语义"（chip_distribution_engine.py:57 头注：**待流通股本工程**，nb1_b6 处方③）；峰检测需要分布导出（400 bins 形状），非标量 | ⑥字段：float_share（流通股本，tushare stock_daily_basic.float_share 万股口径，CH c1_market 在产 710 万行——引擎头注:52-53）；③算法：单峰/双峰判别（众数核密度或 bins 峰谷检测，判据待冻结） |
| **A4 股东户数趋势** | `c3_fundamental.shareholder_count`（tasks.yaml:601-615：2026-09-18 切源东财 datacenter RPT_HOLDERNUM_DET，公告日 HOLD_NOTICE_DATE 窗口） | ✅实查在产：CH 实查 announce_date 1993-01-12..2026-10-13、515,473 行、ingest 2026-10-13（当日新鲜） | 无信号消费方（断供史：2026-07 起断两月无人知→supply_sentinel 诞生，data_supply_sentinel.yaml:11-12） | 因子构造待冻结（连降幅/连降期数——常用构造仅研报线索 ⭕，研究册 §5）；PIT=公告制不定时 | ②下游：D 建仓完成族信号（户数连降）；①上游：东财唯一免费口径，tushare stk_holdernumber 需 2000 分权限未开通（tasks.yaml:615） |
| **CGO 学术对偶**（资本利得覆盖，Grinblatt-Han 2005 JFE 78(2)） | 负存在断言：全 src grep `capital.gain\|CGO\|grinblatt\|参考价` 零有效命中（仅除权参考价假阳性，backtest/matching_engine 等 5 处，与 CGO 无关）——证据=本车道 2026-10-13 grep 留痕 | ⬜ 零实现 | 无 | 实现路径见 §3.4；与 A1 的关系=学术桥（获利盘构成上方供给、套牢盘构成阻力的截面预测力证明），非替代 | ③算法：RP_t=换手率加权历史价递推（与 cyc_inf 同构！chips.py:476-491 DMA(close,换手率/100) 就是简化参考价）；④后端：可由 kline_daily+turnover_rate 直接派生，零新数据 |
| （支撑）流通股本工程 | float_share=tushare stock_daily_basic（chip_distribution_engine.py:52-53 在册口径） | ✅ 在产（引擎头注引 710 万行） | A3 全语义前提 | A3 的解锁件 | ⑥字段已备 |

## §2 与既有资产边界

1. **chips.py（IND 族指标库）≠ chip_distribution_engine（regime 域 trial）**：前者=指标（production，落宽表），后者=剖面引擎（trial，winner 剖面直调前者内核，chip_distribution_engine.py:69 import）。**禁建第三套分布实现**（引擎头注:50 明令"真源唯一"）——A2/A3/CGO 的实现一律以 chips.py 内核为单一真源扩展。
2. **SCR/CHIP_CONC_90 同公式双条目**是扩项工单明令保留（chips.py:379-381 overlap 说明）——A3 立卡时勿再重复立"集中度标量"，只立"形态"。
3. **cyc_inf 已是简化参考价**（DMA(close,换手率/100)，chips.py:476-491）：CGO 实现应显式声明与 cyc_inf 的同构/差异（换手率加权窗口无限长 vs GH2005 递减权重口径），防"第二实现"判定。
4. **A4 与 D 解禁/户数信号**：户数归 A（结构证据）与 D（拐点信号族）共用同一表，卡要分开立（骨架 SOP §3：验证口径变→拆）。
5. 与 2_B（流量性质）正交：A 全部为存量（分布/结构），B 全部为增量（当日量性质），禁混卡。

## §3 施工要点（实读代码的坑）

### 3.1 A1 获利盘消费端考试卡——接入设计要点（本册核心交付）

考试卡机制现状（实读）：
- 卡目录=`docs/03_modules/_domain_backtest/exam_cards/`（entry/exit/portfolio/position 四 flow，527 张卡）；执行器=`scripts/backtest/fexam/calibration_exam.py`（MOD-BT-243：只考 preregistered 卡，门柱=pillars_numeric 零裁量，分数 only-add 落 exam_scores_v1.yaml）；绑定层=`scripts/backtest/fexam/card_binding.py`（MOD-BT-248：classify/run 两形，class A=series 单表单列+配方表算子可绑、class B=panel 宽表后置、C=需重放引擎、U=无 data_binding 不考）。
- 卡面必备段（两融 07 卡实例，`exam_cards/entry_flow/L1/TDM-E-L1-S0__calibration__07_margin_flow_shortwindow.yaml`）：card_id/node_id/family/hypothesis/window(in_sample+oos+regimes)/buckets/pillars+pillars_numeric/status(preregistered→examined)/lineage/signal_kind(series|panel)/data_binding(signal_table/signal_column/signal_derivation/target_source/data_window_evidence——**最后一段必须带实查命令原文与行数**)。

A1 卡接入设计要点：
1. **signal_kind 选 series 不选 panel**：calibration_exam 虽支持 panel（ic_exam.fast_rank_ic，calibration_exam.py 头注"两形信号"），但 card_binding 对 panel 宽表现判 class B 后置（card_binding.py:50-56 分类面）——A1 首卡走 series 通道：`chips_winner` 截面聚合（如全市场/基准成分日度中位数）→"市场获利盘水位"序列，对次日指数收益分桶。
2. **需在 card_binding RECIPES 增一个算子**（如 `op_chips_winner_cs_median`）：读 `c1_market.technical_indicator WHERE period='daily'`，按 trade_date 聚合 median(chips_winner)。坑：宽表 ReplacingMergeTree 未合并版本（CH 实查 2026-10-08 行数 15,885/uniq symbol 5,562≈2.86 倍）——**聚合必须 FINAL 或 argMax(ingest_ts) 去重**（card_binding 头注已有 anyLast 去重纪律，同坑同律）。
3. **period 过滤坑**：period 列值='daily'（非 '1day'，实测 9 种 period 值），漏 WHERE 会把 1min 行搅进来。
4. **data_window_evidence 三件必查**：`SELECT min(trade_date),max(trade_date),countIf(isNotNull(chips_winner)) FROM c1_market.technical_indicator WHERE period='daily'`→2019-01-02..今/~1,970 万行；窗口只能从 2019 起（kline_daily 虽有 1990 起数据，指标回算窗自 2019）。
5. **hypothesis 方向（预注册用草案，数值零自拟）**：获利盘高位（截面中位数高档）=止盈供给积聚→前向收益承压/波动放大；分桶单调性与牛熊分段同号为门柱族（对齐 07 卡 pillars 结构：response_monotonicity/ic_floor/lag_profile/regime_stability）。
6. **转正语义**：卡过考=chip_distribution_engine 的消费端证据（#257④"消费端考试卡"要求），流程上卡 status: preregistered 由本战役 P2 冻结后开考，**本作业簿不写卡文件、不开考**。
7. 目标面 target_source 对齐 07 卡先例：kline_index 000300 次日收益；禁借外部指数冒充（SOP §8.5.3 e/r 位纪律）。

### 3.2 A2 施工路线二选一（呈批项）

- 路线甲（扩内核）：`compute_chip_metrics` 输出加 `chips_res_5/10/20` 三列=价上方 (close, close×(1+x)] 带内质量占比。坑：CYQ output_columns 契约变更会牵动宽表 schema（technical_indicator 列族）与 INSERT_COLUMNS 对齐（internal_compute_provider.py:703 注），迁移面大。
- 路线乙（新指标类，推荐）：chips.py 新增 `UPSIDE_RESISTANCE` 类，复用 `_ChipGrid` 状态机重算或让 compute_chip_metrics 带可选输出开关——宽表加三列一次到位，CYQ 六列契约不动。两条路线都只依赖既有 OHLCV+turnover_rate，零新数据闸。

### 3.3 A3 的坑

- 峰检测在 400 bins 上做，**先归一**（分布 Σ=1）再找峰谷；跨股比较需相对价格网格（chip_distribution_engine 的 32 相对网格是现成参照，但那是 regime 域件——A3 若在指标域实现须自带归一，禁跨域 import 反向依赖）。
- 单峰密集度全语义卡在 float_share 工程（引擎头注:57 D21 后续）；A3 施工顺序=先流通股本日频序列可用性审计（6_data_audit §C 系），后形态判据预冻结。

### 3.4 CGO 实现路径（学术对偶，另立卡）

- 基础版：RP_t = 未加权过去价格长期均值代理（仅 kline_daily）；标准版：换手率加权递推 RP_t = (1−τ_t/(1+λ))RP_{t−1} + (τ_t/(1+λ))P_t（Grinblatt-Han 口径），CGO=(P_t−RP_t)/P_t。与 cyc_inf（chips.py:476-491）同构差异须在卡内声明。
- A 股适配闸：除权日参考价跳变（复权因子作用于 P 序列，kline_daily 有 hfq 表 tasks.yaml:2303 依赖链）；涨跌停日换手率失真。两闸都要在卡 data_binding.derivation 写明处置。

## §4 自审闸三态裁定

| 件 | 裁定 | 理由（终局全貌量尺） |
|---|---|---|
| A1 获利盘考试卡接入 | **施工** | 转正唯一通道（#257④）；数据全就位（宽表 2019 起）；消灭"trial 卡死循环"这段人工争议=向终局推进；施工面=1 张卡+1 个绑定算子（小） |
| A2 阻力分位数 | **挂起排期** | 终局有位（"阻力最小方向"可算化的核心件）；解锁条件=A1 卡过考（同一内核扩展有消费端先例后）＋P2 判据冻结；先路线乙设计稿随 P1 呈批 |
| A3 集中度形态 | **挂起排期** | 依赖 float_share 工程+判据冻结（D21 蓝图既定次序）；解锁条件=float_share 日频序列审计通过（6_data_audit）＋A1/A2 至少一件过考 |
| A4 股东户数因子 | **施工（仅台账面）** | 表在产新鲜；施工物=候选卡一张（连降计数/降幅构造进预注册，数值待冻结）；终局有位（D 族信号硬证据） |
| CGO 对偶 | **挂起排期** | 学术桥价值在（研究册 §4），但与 A1 同信息源高度相关——增量账纪律（SOP §8.5.2）要求先看 A1 族残差化增量，排序在 A1 卡后 |

**反驳者一问**（A1 高成本项加试）：最强三条"不该做"——①获利盘与动量/反转因子相关性高，可能零边际增量（对策：卡内 pre-register 对既有因子族残差化）；②换手率衰减模型假设（均匀换手）系统性失真（对策：与 A4 户数硬证据交叉验证列）；③考试卡本身可能因 2019 起算窗短而检验力不足（对策：如实披露窗结构，对齐 07 卡"诚实样本"先例）。三条均有对策，维持施工裁定。
