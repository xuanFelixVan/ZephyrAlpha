---
ttl: task_bound
rule_form: data
verifiability: manual
title: L05 个股做T 链路挖干作业簿（子块全树·六向台账·自审闸三态·施工项·标准件）
owner: ZephyrAlpha-Owner
language: zh
created: "2026-09-25"
status: active（本簿=挖干产出；施工项 SEALED 后按 links/README.md 纪律直接进执行队列）
family_id: L05-T0-SKEL
lane: L05_t0（链路 L05）
inputs:
  - docs/_working/decision_map_campaign_20260924/links/README.md（六向台账+三态+施工纪律真源）
  - docs/_working/decision_map_campaign_20260924/09_link_skeletons.md §环节5（骨架八项真源）
  - docs/_working/decision_map_campaign_20260924/05_t0_and_strategy_library.md（⓪ Owner 方法论六条+做T线口径）
  - docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §三（做T六条量化验收判据）
  - docs/_working/t0_matrix/（T0_SCHEME_MATRIX 34 法/FINAL_REPORT/LEDGER/t0_ceiling_*/预注册卡族/REDEVID/T0_CHAIN_WIRING_GAPS）
  - .worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/（METHOD_MINING_t0.md 34 法矿册+BOARD_INDEX_INTRADAY_SUPPLY_DESIGN.md 等 45 件批次盘面）
  - docs/_working/t0_revival/t0_conditional_prereg_card.md（T0-CONDITIONAL v1 frozen）
  - config/trading_decision_map.yaml TDM-P-P2-01..04（yaml:2830-2944 已核对）
  - config/search_space_prereg.yaml（冻结搜索空间，裁定#413 签发）
  - scripts/backtest/auto_mount.py（resolve_six_phase 法定判定器 :129/:225/:248/:262）
  - docs/_working/trading_vision/2026-09-16-data-sufficiency-matrix.md（S-OWNER-001/002 料源）
  - docs/_working/archive/2026-09/bizmine_night/etf_t0_retest/etft0_prereg_card.md（ETF 三宇宙母本卡）
grading_basis: 裁定#325 判档制 + links/README.md 挖干判据；34 法三态承 T0-SCHEME-MATRIX 口径（禁把"不可考"写成"未通过"）
doc_type: log
---

# L05 · 个股做T 链路挖干作业簿

> 授权链：Owner 09-26 凌晨总筹令（links/README.md）→ 环节5 骨架（09 号文 §环节5，758 行总表）→
> 05 号文 ⓪ Owner 方法论六条（立卡为施工要求）→ 17 号文 §三 做T六条量化验收。
> 本簿只有六向台账+三态+施工项+标准件；所有论断带路径；不改任何他件。

## 0. 一页读法（本簿五句话）

1. **研究面已闭环，消费面零接线**：考试/输入包/对账件全在（`scripts/audit/t0_*.py` 7 件），
   但全仓没有任何模块把做T 条件维当搜索轴用（`T0_CHAIN_WIRING_GAPS.md` §B，含 45 件批次盘面：
   `.worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/T0_CHAIN_WIRING_GAPS.md`）。
2. **核心卡点=考试样本 26 对<30**（`docs/_working/t0_matrix/FINAL_REPORT_t0_matrix_reexam.md` §一.2；
   材料流水止于 2026-09-15，1,970/1,996 配对被证伪为跨组合拼凑，V3 卡修口径后真往返仅 26 对）。
3. **容量考试翻转了成本叙事**：日内可达毛价差上界 p50=330bp=成本 31.2bp 的 10.6 倍，share≥成本≈0.9999；
   真闸=①极值次序五五开（50.1%）②极值不可预知（实现 4.3bp=上界 1.3%，损耗 98.7%）
   （`docs/_working/t0_matrix/t0_ceiling_verdict.md` §1；单向判读：上界过≠任何方法可用）。
4. **34 法三态=7 可考/13 待料/8 阻断/6 执行层**；真 T+0 主场（转债）一个都没进可考——
   缺的只是分钟重采样，不是数据源（`docs/_working/t0_matrix/T0_SCHEME_MATRIX.md` §一/§四）。
5. **条件维自由度≈1 是争议悬案**：宏观门"趋势支"实开的是最低波动日（dominant 实为波动四档），
   双门放行支路交集=0，词表三套映射两套冲突（同闸宽差 75%）——三件 Owner 待裁
   （FINAL_REPORT §五-3/4/6），裁定前任何"状态×情绪"两维展开都虚耗时机并虚增显著性。

---

## 1. 子块全树（48 子块）

```
L05 个股做T
├─ A 主干块（TDM-P-P2 四件，config/trading_decision_map.yaml:2830-2944）
│   ├─ A1 P2-01 做T资格与成本前置（三道门+D58 五道门枚举+D111 绝对金额制）
│   ├─ A2 P2-02 做T策略调度（三策略并发，身份=proposed 假说）
│   ├─ A3 P2-03 做T闭环与成功判定（14:50 强平；成功=股数不变+总成本降）
│   └─ A4 P2-04 减仓与再平衡
├─ B 判据考试块（研究面，scripts/audit/t0_*.py）
│   ├─ B1 T0-CONDITIONAL V3 双门考试（E4 判据族）
│   ├─ B2 成本三件套 cost_trio（CST-T0-001+判据件+两级判线）
│   ├─ B3 T0-CEILING 容量上界考卷（单向判读）
│   └─ B4 条件轴供给（六段相位法定判定器+物化件+GPU 输入包）
├─ C 34 法逐法分块（9 族，T0_SCHEME_MATRIX §一/§二 判定，METHOD_MINING_t0.md 矿册）
│   ├─ C-F1 机构执行算法族（1.1-1.4，4 法）
│   ├─ C-F2 底仓滚动族（2.1-2.4，4 法）——做T 正题所在
│   ├─ C-F3 日内动量/回归族（3.1-3.5，5 法）
│   ├─ C-F4 涨跌停制度特色族（4.1-4.4，4 法）
│   ├─ C-F5 订单流/微观结构族（5.1-5.4，4 法）
│   ├─ C-F6 板块/跨资产族（6.1-6.4，4 法）
│   ├─ C-F7 可转债 T+0 族（7.1-7.3，3 法）——真 T+0 主场
│   ├─ C-F8 竞价/情绪族（8.1-8.3，3 法）
│   └─ C-F9 统计/ML 族（9.1-9.3，3 法）
└─ D 增量块（05 号文 ⓪ Owner 方法论六条 → 17 号文 §三 验收版）
    ├─ D1 多周期买卖点轴 {1,5,15,30,60}min
    ├─ D2 全量×状态匹配引擎（相位×周期×板块族 胜率/期望矩阵）
    ├─ D3 个股条件维增补（市值五分位/新闻十分位）
    ├─ D4 ETF 做T线新卡（T0-ETF）
    ├─ D5 行情段覆盖纪律（分钟研究语料/tick 限执行层）
    └─ D6 自动提假设引擎（PG meta_question 衔接）
```

计数：A 4 + B 4 + C 34 + D 6 = **48 子块**；每块六向台账见 §2-§5；三态判定见 §6。

---

## 2. A 主干块（TDM-P-P2 四件）

### A1 · P2-01 做T资格与成本前置

| 向 | 内容 |
|---|---|
| ①上游输入 | TDM-P-P1 持仓体检六件（yaml:2568-2829）；大盘段位 L1-AGG（矩阵仅 accumulation/expansion 开做T）；六段相位真源（B4 块）；CST-T0-001 成本模型；P1-04 风险否决；X-R1 熔断 |
| ②数据原料 | DS-150（大盘段位直喂+20 日振幅+成本模型）；FCT-INTRADAY-028；20 日平均振幅≥3% 振幅门；9:30-9:40 禁开新T 等时段准入矩阵（D58） |
| ③状态输出 | 做T资格三态（状态门×振幅门×成本门 过/不过）；成本门=D111 绝对金额制（每笔保本价差 s*(N)=来回费用÷N+滑点余量；单笔下限 N_floor≈5.86 万@万0.854）；量能闸门（<5日均量 0.8 倍禁开新T）；T量盘口匹配（单笔≤对手一档 50%、日参与≤1-5% ADV） |
| ④下游消费 | P2-02 调度（三关全过才进调度）；P1-05 组合级体检；module_ref=src/zephyr/position/core/t1_sellable.py（MOD-POS-028） |
| ⑤自动化挂点 | activation=premarket（yaml 字段在册）；盘中转单边 invalidation 作废条款在册——**资格判定的实盘自动触发=缺位**（宪法 §9.3 事件触发要求，未接 pipeline_events） |
| ⑥缺口债 | LK-07（三策略无一条 verified，资格门放了也没真策略可调）；X-S1-02 止损族挂 P2-02（yaml X-R1 注释 m-11）；时段准入矩阵/量能闸门无消费代码实证 |

三态：**SEALED**（yaml:2830-2866 已逐行核对；D58/D111 枚举与 09 号文 §环节5① 一致）。

### A2 · P2-02 做T策略调度

| 向 | 内容 |
|---|---|
| ①上游输入 | A1 资格三态；三策略信号源：intraday-surge-fall / orderbook-imbalance / vwap-reversion |
| ②数据原料 | kline_1min（14.83 亿行/2021-09→2026-09/5,853 只，裁定#413④ 信号法定轴）；tick L1 3s（盘口失衡信号=执行增强 v2，05 号文 §一）；单次≤底仓 30% |
| ③状态输出 | 策略调度单（身份=**proposed 假说**，yaml:2867-2907 注释 D111） |
| ④下游消费 | A3 闭环判定；执行层（07 链路）；C3 归因（做T贡献拆账 D50：交易盈亏/持仓盈亏二分+底仓/做T/加仓腿分离，yaml:3798-3803 注释） |
| ⑤自动化挂点 | 调度逻辑在 yaml 在册；**回测验证通过前不生效**（confidence=proposed）→ 产槽休眠 |
| ⑥缺口债 | **LK-07**（09 号文 §环节5⑦ 本表新登）：做T策略层至今无一条 verified；62bp 成本绞肉机实证判死 tick 独立信号（01_goal §三行 7）；orderbook-imbalance 与 5.1 OBI 同族须强制消融（METHOD_MINING_t0.md 判读总纲 3） |

三态：**SEALED**。

### A3 · P2-03 做T闭环与成功判定

| 向 | 内容 |
|---|---|
| ①上游输入 | A2 调度单；日内行情（kline_1min）；14:50 时钟 |
| ②数据原料 | 成交流水（data/backtest_artifacts/bt-*.json trade_log=研究面唯一材料真源，T0-CONDITIONAL 卡 §4） |
| ③状态输出 | 做T闭环成功判定：14:50 未闭环无条件平；**成功=股数不变+总成本降**（yaml:2908-2944）；喂 C3 归因——"做T是降成本工具不是独立盈利来源" |
| ④下游消费 | TDM-F-C3 绩效归因（D50 拆账）；P2-04；P1-05 |
| ⑤自动化挂点 | 闭环判定义务在册；**盘中自动平仓链=缺位**（无事件触发实证） |
| ⑥缺口债 | 配对身份判据已由 V3 卡 M-1..M-4 立法（run 维同体+指纹去重+涨跌停可行域，`t0_conditional_v3_prereg_card.md` §4）——产线闭环判定若不复用该判据，会把跨组合拼凑再当往返（F-1 实测 1,970/1,996 污染） |

三态：**SEALED**。

### A4 · P2-04 减仓与再平衡

| 向 | 内容 |
|---|---|
| ①上游输入 | A3 闭环结果；P1-05 组合体检 |
| ②数据原料 | 底仓/做T 腿分离账（D50）；组合预算账本（L4 层 alloc_budget_daily，data-sufficiency-matrix L4 行） |
| ③状态输出 | 减仓/再平衡指令（proposed） |
| ④下游消费 | 执行层；C3 归因回灌 |
| ⑤自动化挂点 | 缺位（与 A2 同因：LK-07 未解，策略层无 verified 实体） |
| ⑥缺口债 | LK-07；与 L08 风控链（X-R1 中断/熔断停做T）的交接边界未显式登记 |

三态：**SEALED**。

---

## 3. B 判据考试块（研究面真源）

### B1 · T0-CONDITIONAL V3 双门考试（E4 判据族）

| 向 | 内容 |
|---|---|
| ①上游输入 | 宏观门=c1_backtest.regime_state_anchored（vol_pct(T-1)>0.700 或 dominant∈{r3,r12}，卡 §2.1 frozen）；情绪门=六段真源 ∈{ignition,expansion,euphoria}（卡 §2.2）；材料=bt-*.json trade_log |
| ②数据原料 | 成对判据 import 复用 scripts/audit/cost_trio_exam.py:build_pairs()（禁重写，V3 卡 §3）；材料资格 M-1 日内粒度/M-2 run 维同体/M-3 sha256 指纹去重/M-4 涨跌停可行域（V3 卡 §4 frozen） |
| ③状态输出 | verdict 五态枚举（PASS-待考/PASS-单门/FAIL/INSUFFICIENT_SAMPLES/STATE_GATE_NEVER_TRIGGERED，fail-closed）；现值=**STATE_GATE_NEVER_TRIGGERED**，全材料 26 对净均 −36.26bp、前置命中率 0.2308<0.30（docs/_working/t0_matrix/t0_conditional_e4_v3_result.yaml + FINAL_REPORT §任务③） |
| ④下游消费 | GPU 条件维（grid_t0_conditional_v1 包 negatives）；周五矩阵"做T 条件维只能当分层观察不能当判据"（FINAL_REPORT §五-2 不点会怎样）；C3 归因口径 |
| ⑤自动化挂点 | 手工触发（`python scripts/audit/t0_conditional_e4_v3_exam.py --artifacts-dir ...`，FINAL_REPORT §四复算命令 2）；**缺位**：无事件触发（T0_CHAIN_WIRING_GAPS §C 表判"考试体是判据面，可留人工触发"） |
| ⑥缺口债 | 样本 26<30（LK-05 同源）；**D-14 词表三套映射两套冲突**（R2SIX 有漂移守卫 vs daily_decision_orchestrator 占位无守卫，同闸宽差 75%）；**宏观门"趋势支"语义相反**（dominant 实为波动四档，r10/r11/r12 不在取值域；两源逐日一致率 21.09%，FINAL_REPORT §五-6+§六 M-2）；vol 边界 0.700 定档窗越闭卷切点 8.5 个月（M-1，包 caveats 已登记严格闭卷替代值 0.308/0.704） |

三态：**SEALED**（卡族 v1/v2 VOID/v3 全读；判据数值零改动纪律核验：FINAL_REPORT §六"7 个常数全部未变"）。

### B2 · 成本三件套 cost_trio

| 向 | 内容 |
|---|---|
| ①上游输入 | 成交流水配对（同 B1 材料）；CST-T0-001 成本注册表 |
| ②数据原料 | **三件**：① CST-T0-001 固定口径 rt=31.2bp（佣金双边 6+印花 5+过户双边 0.2+滑点 2×10，scripts/audit/cost_trio_exam.py:56 `RT_COST_BP=31.2`）；② cost_trio_exam.py 判据件（build_pairs 配对真源+30bp 开仓前置+前置命中率≥0.30，frozen，`[MODIFY-GUARD]` 改判据=作废重开）；③ 两级判线 L1=31.2/L2=61.2（成本 / 成本+前置，t0_ceiling_prereg_card.md §1） |
| ③状态输出 | 每对 gross_bp/net_bp（net=gross−31.2）；n 对数；前置命中率；verdict（frozen 基线五值逐位复现：24 对/0 净正/0≥30bp/毛 −9.2bp/毛 p50 −5.13bp，REDEVID_mutation_probe_matrix.md §同轮另外两条） |
| ④下游消费 | B1/B3 全部考试族的成本腿；34 法成本闸口径（转债/跨境 ETF 无印花税约 1~8bp 单列，T0_SCHEME_MATRIX 判定口径） |
| ⑤自动化挂点 | 手工复算命令在册（FINAL_REPORT §四命令 5）；frozen 与分支 blob 逐字节比对通过 |
| ⑥缺口债 | 灰区 §8.2：滑点已按固定 2×10bp 计、与模拟成交价内是否重复计入未独立复核（V3 卡 §8.2 两向都可能偏）——材料线卡（L05-C02）须一次了断；min5 抬升单列披露未入固定口径 |

三态：**SEALED**。

### B3 · T0-CEILING 容量上界考卷

| 向 | 内容 |
|---|---|
| ①上游输入 | c1_market.kline_1min（argMin(low)/argMax(high) 时刻+方向判据 t_low<t_high）；情绪六段 T-1 + regime_state_anchored（卡 §1 frozen） |
| ②数据原料 | 1,227 交易日/6.15M 股票-日/可做多T 3,079,430 个；停牌表 0 行→bar_n≥200 可交易代理（登记不下修）；`uniqExact(trade_time)` 防ReplacingMergeTree 多版虚增 1.7 倍（t0_ceiling_verdict.md §4） |
| ③状态输出 | 上界 p50=330bp（日际 202–1314bp）；share(≥L1)=0.9999 全状态组；先低后高占比 0.501；判死规则单向（组内 share<0.05 才判死→全部 `CEILING_OK_NOT_A_PROOF`，无一族被判死也无一族被放行）；产物 t0_ceiling_result.yaml+t0_ceiling_daily.csv |
| ④下游消费 | 34 法优先级排序（R1③ 火力指向：钱花在预测不在成本模型）；min(low)=0 零价挡除契约（任何振幅/价差消费方必须先挡零价，verdict §4 契约测试 TestDivisionByZeroRegression 钉住） |
| ⑤自动化挂点 | 手工（FINAL_REPORT §四容量考五项）；复算漂移实测 37/170 数值叶 1.3e-5（活表 merge 所致，结论面不受影响，须容差≥1e-4 禁 byte 硬绑，verdict §6） |
| ⑥缺口债 | 不外推转债/ETF（verdict §5.3 待料）；`FOR SYSTEM_TIME AS OF` 分区快照冻结未实现（登记待料不假装）；容量上界宽裕**不构成任何方法的证据**（单向判读，T0_SCHEME_MATRIX §三尾注） |

三态：**SEALED**。

### B4 · 条件轴供给（六段相位法定判定器+物化件+GPU 输入包）

| 向 | 内容 |
|---|---|
| ①上游输入 | c1_backtest.regime_snapshot_history（2019-04-01→，每日双写须去重）；广度数据（phase_overlay：乖离 250 日分位≥0.90 ∧ 20 日上涨占比分位≥0.85 ∧ 60 日收益>0=亢奋；亢奋记忆窗 60 日内破 MA20=退潮，scripts/backtest/auto_mount.py:225-245） |
| ②数据原料 | **法定判定器**=auto_mount.R2SIX(:129)⊕phase_overlay(:225)→resolve_six_phase(:248，优先级 PHASE_PREEMPT(r10/r11)>distribution>euphoria>基础映射，未映射 r1/r2→NaN 不路由)；漂移守卫测试 test_r2six_drift_guard_vs_framework_composer；物化件=docs/_working/t0_matrix/six_phase_history_v1.csv（1,816 日/1,054 路由/闭卷窗 359 日允许集；段分布 expansion 388/distribution 221/capitulation 202/accumulation 201/euphoria 40/ignition 2） |
| ③状态输出 | GPU 输入包 data/strategy_intake/grid_t0_conditional_v1/（matrix 1,816 行×18 列/cells 20 胞 15 达 30 日地板/negatives 5 条带死因；新轴 t1_amp_bucket3 边界 116.75/188.25bp 只用≤2025-09-09 定档；sha256 前 16=cb6979235cae3bb9/88d4b2d8746c5cea/1f52512937358c8a）——脚本+meta 契约入库、盘面一条命令重建（`python scripts/audit/t0_gpu_condition_pack.py`），**禁落 summary.json**（n_trial_ledger glob grid_*/summary.json 计 DSR 分母=科学污染，src/zephyr/backtest/core/n_trial_ledger.py:421） |
| ④下游消费 | B1/B3 双门取数；周五 GPU 矩阵条件维（**当前零消费者**，T0_CHAIN_WIRING_GAPS §B）；euphoria 三桶+ignition 不可作搜索维（negatives 明令） |
| ⑤自动化挂点 | 手工两件（materialize→pack→reconcile）；--reconcile 逐格对账 1,816 行×10 派生列=0 不一致+20 日×7 源值列 140 格回查 0 不一致（四道加严守卫+18 项变异自探针全红，FINAL_REPORT §六之四）；**自动化=缺位**（D-1..D-5 配方已备，见 L05-C10） |
| ⑥缺口债 | D-3 双写缺陷已修（load_phase_panel 去重+PIT 尾窗切行→切日，76 测绿）；M-1 vol 桶轴闭卷越界登记；ignition 全史 2 日极稀（允许集实际由 expansion/euphoria 主导，禁放宽）；甲位 auto_mount.py 写回=已批开工（07 号文 §行70，非本簿项） |

三态：**SEALED**。

---

## 4. C 34 法逐法分块（六向台账按族紧凑表）

> 逐法考试三态承 T0_SCHEME_MATRIX §一（✅可考 7/⏳待料 13/⛔阻断 8/🔧执行层 6），原理分承
> METHOD_MINING_t0.md 汇总表（HIGH 6/MED 17/LOW 11）。六向口径全族通用项在此总述，表内只填差异：
> ①-②上游/原料=该法数据门实测（矩阵 §二）；③状态输出=预注册卡+E4 verdict（禁绕考）；④下游=P2-02
> 调度池或执行域；⑤自动化挂点=全部**缺位**（无任何法的自动触发/自动考试，全手工考试件）；⑥缺口债=编号。
> **同族近亲强制消融**（1.2↔3.2、2.1↔2.2、3.1↔8.3、4.x↔6.x，矿册判读总纲 3）。

### C-F1 机构执行算法族（执行域，不占做T判据族）

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 1.1 POV 参与率切片 | 🔧 | kline_1min 1,227 日✅ | 分钟全量 | 冲击成本节省量 | 执行算法域（07 链路） | 与 1.2 同族消融未做 |
| 1.2 VWAP 偏离回归 T | 🔧/⏳ | 分钟✅+当日 VWAP 自算 | 同上 | 执行增强/方向性 T 双身份待裁 | 执行域为主 | 当方向性 T 考须先与 1.1 消融（矩阵 §二 1.2） |
| 1.3 IS 松弛带 T | ⏳ | 需母单起止时刻 | 回测件无此字段 | — | — | 字段欠账（D24 同族台账字段缺口） |
| 1.4 被动队列挂单增益 | 🔧 | 五档仅 14 日 | tick_depth_5 | 队列位次不可观测→增益不可归因 | 经验层 | D36（五档差 17 交易日 walkforward，且 14 日历史撑不起 n≥30） |

### C-F2 底仓滚动族（做T 正题所在）

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 2.1 固定网格日内 T | ✅可考 | kline_1min 5,558 只/日✅ | 分钟全量 | E4 考卷待立（判据承 B2/B1 族） | P2-02 调度池 | 难点不在数据在预测（次序先验五五开）；与 2.2 消融 |
| 2.2 波动率自适应带 T | ✅**可考·最高优先** | 分钟✅+六段相位✅+vol_pct✅ | B4 全套 | 带宽=f(状态,情绪段) 预注册卡 | P2-02；与双门真源直连 | **两门在考窗互斥**→考必先解 D-14 词表收敛（矩阵 §二 2.2）；与 2.1 消融 |
| 2.3 融券反向 T | ⛔ | — | 转融券 2024-07-11 暂停/存量 09-30 了结 | 制度性死亡 | 禁预注册 | 外部制度变化才解锁（矿册监管事实来源） |
| 2.4 期指合成空头 T | ⛔ | 期指仅日 K | 无分钟腿 | DATA-BLOCKED | 禁预注册 | 期指分钟源缺（TqSdk 列候选源，矿册 §开源） |

### C-F3 日内动量/回归族

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 3.1 开盘冲高衰减 | ⏳ | 分钟✅；auction_snapshot 仅 52 日 | 分钟首 30 根近似主形态+竞价腿待料 | — | — | 竞价腿 52 日<时序检验地板（且仅 31% 当日入库） |
| 3.2 VWAP 带反转（信号化） | ✅可考 | 分钟✅ | 全输入在库 | E4 待立 | P2-02 | 与 1.2 强制消融 |
| 3.3 ORB 开盘区间突破 | ✅可考 | 分钟✅ | 全输入在库 | E4 待立 | P2-02 | 学术锚点=Market Intraday Momentum 族（§7 标准件） |
| 3.4 尾盘动量次日出 | ⏳ | 分钟尾段✅；龙虎榜仅 34 日 | "次日出"腿需竞价/开盘执行价 | — | — | 事件史薄+执行腿待料 |
| 3.5 收盘大单失衡反转 | ⏳ | tick_data 2025-01→ 缺约 10 日 | 大单失衡 | — | — | tick 时区纪元核验前置（L05-C11）；北交所板别已修（红蓝 #11） |

### C-F4 涨跌停制度特色族

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 4.1 打板/排板 | 🔧/⛔ | 封板事件 16-17 日 | 排队位次不可得→回测必高估 | 执行侧经验 | — | daban_board_event 16 日史 |
| 4.2 炸板回封 T | ⏳ | daban_board_event 1,454 事件/16 日 | 截面可统计时序不可考 | — | — | 16 日<<30 日地板 |
| 4.3 一字开板出货 | ⏳ | 同上 | 同上 | — | — | 同上 |
| 4.4 情绪周期总门 | ⏳→已考 | 六段全史✅（1,816 日/闭卷允许集 359 日） | B1 双门 | verdict=STATE_GATE_NEVER_TRIGGERED | GPU negatives | 待料=流水不是数据；两门互斥悬案（D-14/M-2） |

### C-F5 订单流/微观结构族

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 5.1 五档 OBI | ⛔(时序) | tick_depth_5 14 日 | 截面可看不可判 | — | 执行增强 v2 候选（tick 盘口失衡） | D36；学术锚点=Cont-Kukanov-Stoikov OFI（矿册 §学术锚点） |
| 5.2 大单跟单 L1 代理 | ⛔ | money_flow 日频 | 日频不能代理日内时点 | — | 禁预注册 | 代理=自欺（矩阵 §二 5.2） |
| 5.3 幌骗检测反制 | ⛔ | l2_tick=0 行 | 委托流结构性不可得 | — | 禁预注册 | 权限缺口在册 |
| 5.4 3s 微观动量 | ✅可考(重算力) | tick_data 8.9B 行/21 月 | 时区纪元待核 | E4 待立 | P2-02（算力与存储门槛） | L05-C11 前置；程序化新规 2025-07-07 高频认定线合规边界（矿册监管节） |

### C-F6 板块/跨资产族

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 6.1 龙头-跟风扩散 | ⛔ | 板块盘中源死（sector_snapshot 09-24=0 行/09-17 整日缺；kline_sector_intraday 09-11 后冻结） | R2 情报实测证伪（board_index_tick 全表 5,564 行落 09-15 一个 2 分钟合成窗，data_source='bridge_synth'） | 禁预注册 | — | L05-C12（板块盘中供给 S1-S5）；R2 情报=干跑冒充实盘常驻（矩阵 §五） |
| 6.2 板块内补涨 | ⛔ | 成分映射仅 3 快照日 | 无 PIT 成分序列→任何板块归属=前视 | 禁预注册 | — | 同上（S1 成分 PIT=真瓶颈） |
| 6.3 ETF 申赎/IOPV 折溢价回归 | 🔧→⏳ | market_etf_share_snapshot(iopv/折溢价) 仅 2026-09-18 一天 | 原理 HIGH 数据 1 天；etf_nav(2021-07→) 是日频不得顶替日内量 | 禁顶替 | — | ETF 线新卡（L05-C06）另立，日频近似禁顶日内 |
| 6.4 期指基差日内门 | ⛔ | 无期指分钟线 | DATA-BLOCKED | 禁预注册 | — | 与 2.4 同源 |

### C-F7 可转债 T+0 族（真 T+0 主场）

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 7.1 转股溢价率日内回归 | ⏳ | conversion_premium 33 日；转债无分钟 bar | 溢价率与价格须同日对齐 | — | — | **LK-06**（转债分钟 bar 缺失）；33 日刚过地板 |
| 7.2 转债日内波动网格 | ⏳（**最高优先补料对象**） | tick_data 转债 163 只 2025-01→ | 成本仅 1~8bp=唯一"毛边际可能盖过成本"族 | — | — | **缺的只是重采样不是数据源**（L05-C01，矩阵 §四.1）；监管对高换手 CB 账户监察风险须入每卡止损线（矿册判读总纲 2） |
| 7.3 强赎条款事件 T | ⏳ | market_convertible_bond_clause 约 1 月 | 事件史薄 | — | — | 时间积累或历史源补 |

### C-F8 竞价/情绪族

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 8.1 竞价失衡信息 | ⏳ | auction_snapshot 52 日 266k 行（pre-06 无源） | 截面能算时序不能判 | — | — | 回填占多（仅 31% 当日入库） |
| 8.2 竞价撤单悬崖 | 🔧/⛔ | l2_tick=0+9:20-9:25 禁撤制度 | 可观测性+制度双限 | — | — | 无解锁路径 |
| 8.3 隔夜新闻情绪过冲 | ⏳ | news_sentiment_window✅ 19,819 行 | 源在库 | — | — | 须先过发布时点审计（既有班在册）；与 3.1 消融 |

### C-F9 统计/ML 族

| 法 | 考试三态 | ①上游输入 | ②数据原料 | ③状态输出 | ④下游消费 | ⑥缺口债 |
|---|---|---|---|---|---|---|
| 9.1 分钟 GBM 信号器 | ✅可考 | 分钟✅ | 特征工程参照 qlib Alpha158（§7 标准件） | E4 待立 | P2-02 | 同族近亲强制消融（与 3.x 对照）防多重检验虚高 |
| 9.2 RL 执行调参 | ⏳ | 训练器在库 | real_training=False 默认 | — | — | 真训练=Owner 门（05 号文重考纪律 3 同构）；首发不建议 |
| 9.3 日内高频因子族 | ✅**可考·算力最大** | 分钟✅ 1,227 日×5,558 只 | 数据最厚族；进周五 GPU 条件维候选 | E4 待立 | P2-02+GPU 包 | 算力预算承 search_space_prereg.yaml budget_caps（per_point_seconds_measured=35.33 实测，59h 窗有效容量≈4,809 格） |

---

## 5. D 增量块（Owner 方法论六条落地）

### D1 · 多周期买卖点轴 {1,5,15,30,60}min（05 号文 ⓪.1）

| 向 | 内容 |
|---|---|
| ①上游输入 | kline_1min 全量（1min 原生轴）→5/15/30/60min 由 1min 重采样派生（120min 不做，Owner 明令） |
| ②数据原料 | 全市场 5,853 只×两年；买卖点=指标规则 YAML 卡预注册（**禁主观盘感**，17 号文 §三.1）；周期维=当前 t0 矩阵条件轴未显式含"周期"维→立卡补轴 |
| ③状态输出 | 周期×规则的买卖点信号（proposed）；每周期×每规则组合数与耗时**容量预检报告先行**（超 48h CPU 预算即分层，17 §三.1） |
| ④下游消费 | D2 状态匹配引擎（相位×周期矩阵）；P2-02 调度池 |
| ⑤自动化挂点 | 缺位（重采样件+预检件均未建） |
| ⑥缺口债 | 规则数先行报备（17 §三.1）；与 B4 GPU 包轴（六段×振幅桶）的正交性未登记 |

三态：**SEALED**（判据/口径/红线全在 17 §三.1，无需再挖）。

### D2 · 全量×状态匹配引擎（05 号文 ⓪.2）

| 向 | 内容 |
|---|---|
| ①上游输入 | 两年做T全算成绩分布（全股票）×大盘相位×板块状态×情绪状态 |
| ②数据原料 | 六段相位真源（B4）；P1 表四元组行规范（raw/n/Wilson LB/区间宽，04 号文 §15"排序只认 Wilson LB"）；**样本外判据=WFE=OOS/IS≥50%（Pardo）+内控更严线 Wilson LB 衰减≤30% 双轨并行**（17 §三.2） |
| ③状态输出 | 相位×周期×板块族 胜率/期望矩阵；高胜率组合→今年数据闭卷考→不过则迭代再考（=P1 表逻辑在个股日内的复制，与 t0 条件化矩阵同构） |
| ④下游消费 | **消费链缺口=LK-05**（09 号文环节5 引 05 号文 ⓪.2）；GPU 成绩单+P1 概率表=条件共振选策略组合的原料（05 号文 §二长期愿景） |
| ⑤自动化挂点 | 缺位（T0_CHAIN_WIRING_GAPS §D 配方：显式常量路径读包，禁 glob——grid_t0_conditional_v1 字典序会劫持 lane-F latest_grid_manifest） |
| ⑥缺口债 | **条件维自由度≈1 争议悬案**（FINAL_REPORT §五-3：按两维独立展开会试大量永假格+族规模低估→DSR 显著性虚高；Owner 未裁前搜索空间不得扩）；报告必须披露各相位样本数（17 §三.5）；闭卷切点 2025-09-09 禁越 |

三态：**SEALED**。

### D3 · 个股条件维增补：市值/新闻（05 号文 ⓪.3）

| 向 | 内容 |
|---|---|
| ①上游输入 | 市值（circ_mv，09-17 起断供已愈=data-sufficiency-matrix L3 行）；新闻活跃度（近 30 日新闻条数） |
| ②数据原料 | 市值五分位、新闻十分位；每格 n≥30 同门槛（17 §三.3）；选股传导层条件维（跨 L04/L05） |
| ③状态输出 | 市值×新闻分格的做T成绩分层（观察维先行） |
| ④下游消费 | L04 选股传导链+D2 匹配引擎 |
| ⑤自动化挂点 | 缺位 |
| ⑥缺口债 | 新闻发布时点审计（PIT 前视风险，8.3 同源在册项）；新闻源覆盖度未普查（本簿未探项之一） |

三态：**SEALED**（新闻源覆盖普查列 L05-C06 后补探清单）。

### D4 · ETF 做T线新卡 T0-ETF（05 号文 ⓪.4）

| 向 | 内容 |
|---|---|
| ①上游输入 | kline_etf_1min（合成可救 D26 缺口 ~95%）+kline_etf_60min（四段结构缺口约 9.0 万 bar，data-sufficiency-matrix §S-OWNER-001/002） |
| ②数据原料 | **每只 ETF 成本独立实测（佣金+价差分列，高于个股且离散）**；池=近 60 日日均成交额过滤（建议 top100 起）；格门槛同 30 对（17 §三.4）；宇宙分类母本=ETFT0-SCREEN 三宇宙卡（宇宙 A 行业/主题 top10、宇宙 B T+0 类全入组：债券/黄金商品/跨境QDII/REITs、宇宙 C 高波个股 top20，etft0_prereg_card.md §2 分类关键词 frozen） |
| ③状态输出 | T0-ETF 预注册卡+逐只成本实测台账+E4 verdict（新卡接续编号，links/README 施工纪律） |
| ④下游消费 | 跨境/债券 ETF=真 T+0 场所——"允许更小实现边际也划算"（4.3bp 在 31.2bp 成本下必死、在 1~8bp 下可活，t0_ceiling_verdict.md §3）；P2-02 |
| ⑤自动化挂点 | 缺位 |
| ⑥缺口债 | D26（60min 四段缺口→工单在 docs/_working/datavein/2026-09-17-etf60min-depth-workorder.md，首选通道 C=etf_1min 合成）；ETF 池 ADV top100 实测未做；6.3 折溢价日内腿（iopv 仅 1 天）单列不并入本卡 |

三态：**SEALED**（判据/母本卡/缺口全在；池实测属施工 L05-C06 取数面）。

### D5 · 行情段覆盖纪律（05 号文 ⓪.5）

| 向 | 内容 |
|---|---|
| ①上游输入 | kline_1min（2021-09→，天然含 2021-2024 熊市震荡）；tick_data（2 年偏牛市） |
| ②数据原料 | 研究面用分钟 5 年；tick 行情偏科**只限执行层验证**；闭卷保留今年=现有 HOLDOUT 制度（切点 2025-09-09） |
| ③状态输出 | 研究语料/闭卷窗切分声明（每份考试报告必载） |
| ④下游消费 | 全部 B/C/D 考试族 |
| ⑤自动化挂点 | 闭卷纪律已由 `_CLOSED_BOOK_*`+search_space_prereg.yaml 双写一致（LEDGER.md §1 补充实测：闭卷窗=[2019-01-04,2025-09-09] 实测 1,622 交易日） |
| ⑥缺口债 | **文档矛盾登记**：17 号文 §三.5 写"研究语料=分钟 2019-2024 段"，但裁定#413④ 立法 kline_1min 起点=2021-09-01（05 号文 §一、T0_SCHEME_MATRIX 数据门实测）——2019-2021 无分钟语料，两文须对齐（宪法 §4.3 文档矛盾=事故；建议口径=分钟 2021-09→2024 段+日线更早史，交总指挥裁定） |

三态：**SEALED**。

### D6 · 自动提假设引擎（05 号文 ⓪.6）

| 向 | 内容 |
|---|---|
| ①上游输入 | PG meta_question 283 题机制（代码在库：src/zephyr/governance/meta_question/ registry.py+exam_ops.py+exam_loop/{state_machine,arbitration,ledger,event_codes}.py） |
| ②数据原料 | "不断提假设→自动跑→自动收集入库"循环；每周 ≥5 条新假设入 meta_question（带考试卡草稿）；人工裁决率与自动考试通过率双周报（17 §三.6） |
| ③状态输出 | 假设卡草稿流+双周报 |
| ④下游消费 | B/C/D 全部考试族（假设进=预注册卡进）；11 号文实证：**meta_question 283 题全 registered/answered=0/exam_result=0 行——治理级考试循环是空壳**（docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md §30/§185） |
| ⑤自动化挂点 | 机制代码在库但**考试循环本体从未自动运行**（挂点缺位实证如上） |
| ⑥缺口债 | exam_loop 状态机内部语义未深读（本簿唯一未探指针，清单=上述 4 件源码）；"Owner 定性属原问题"（05 号文 ⓪.6）——引擎属 Owner 定向，非本簿可自裁 |

三态：**MINING**（未探清单：exam_loop 4 件源码深读；放行条件=D6 立卡施工时补读，不阻断其余 47 块）。

---

## 6. 自审闸三态总表

### 6.1 逐块三态（48 子块）

| 分区 | SEALED | MINING | BLOCKED |
|---|---|---|---|
| A 主干块（4） | 4 | 0 | 0 |
| B 判据考试块（4） | 4 | 0 | 0 |
| C 34 法分块（34） | 34 | 0 | 0 |
| D 增量块（6） | 5 | 1（D6） | 0 |
| **合计（48）** | **47** | **1** | **0** |

> 挖干三态与 34 法**考试三态**（7 可考/13 待料/8 阻断/6 执行层）是两条正交轴：
> 前者=本作业簿对该子块的挖掘完成度；后者=该法在仓内数据下的可考性判定（禁混淆——
> "⛔阻断"法如 2.3/5.3 的挖干已封矿：结构性不可得的判定本身就是完整结论）。

### 6.2 本簿总判

**MINING（差一块即封矿）**——SEALED 判据三查：
1. 六向台账：48/48 全填 ✓（§2-§5）。
2. 章节内全部指针已读：README/09 号文环节5/05/17 号文/t0_matrix 主区 10 件+批次盘面 45 件目录
   （METHOD_MINING_t0/BOARD_INDEX_INTRADAY_SUPPLY_DESIGN/T0_CHAIN_WIRING_GAPS/预注册卡族/
   REDEVID/ceiling 三件）/TDM yaml:2830-2944 逐行/auto_mount.py 判定器四锚点/
   search_space_prereg.yaml 全文/etft0 母本卡/S-OWNER-001/07 号文甲位行 ✓；
   唯一未探=D6 的 exam_loop 4 件源码（§5 D6 ⑥ 已列清单）✗。
3. 最新算法对表（18 号文纪律：有行业标准/开源实现必须引用并采用）：§7 标准件已完成
   （web 检索 2024-2025 学术锚点+开源框架许可证），费率/容量预检/WFE 判据与 17 号文 §三逐条对上 ✓。

**放行条件**：exam_loop 4 件源码补读后本簿整体转 SEALED（不影响 §7 施工项进队——
links/README 挖干即开工条款，47/48 已封矿部分先行）。

---

## 7. 施工项（L05-C01 起；判据全部承 17 号文 §三；容量预检先行）

> 编号 L05-Cxx（本簿新立，接续 links/README 编号规则）；既有账本映射列于各项。
> 排序按性价比与解锁面（矩阵 §四 顺序+Owner 定调做T=主攻）。

| # | 施工项 | 内容与判据（17 号文 §三 条款） | 账本映射 | 优先级 |
|---|---|---|---|---|
| L05-C01 | **转债分钟腿重建** | tick_data 转债 163 只（2025-01→）重采样为分钟 bar；与 w2_sector_minute_resample_dryrun 同族技术路线；解锁 7.1/7.2/7.3 真 T+0 主场（成本 1~8bp）；每法另立预注册卡走 E4 | LK-06 | **P1** |
| L05-C02 | **T0-MATERIAL 做T材料线预注册卡+重考** | 设计要点全备（FINAL_REPORT §七 0-5）：成交模型先写死（滑点与 CST-T0-001 是否重复计入一次了断）+窗规则日历化禁看结果挑窗+判据零改动+n≥30 才出结论；Owner 已批材料线开闸（05 号文 §一）；目的不是"凑 30 对让 V3 过关"而是"给有信息源的方法足够样本"（D-7 禁造料） | 样本 26<30（09 号文环节5⑦ 首项） | **P1** |
| L05-C03 | **多周期买卖点轴立卡** | 周期集 {1,5,15,30,60}min×5,853 只×两年；买卖点=指标规则 YAML 卡预注册禁主观盘感；**容量预检报告先行**（超 48h CPU 预算即分层）；规则数先行报备（17 §三.1）；1min→高周期重采样件 | 05 号文 ⓪.1 | **P1** |
| L05-C04 | **全量×状态匹配引擎** | 相位×周期×板块族 胜率/期望矩阵；格子四元组（n≥30/raw/Wilson LB/区间宽）同 P1（04 号文 §15）；WFE≥50%+Wilson LB 衰减≤30% 双轨（17 §三.2）；消费链接线=显式常量路径读 grid 包（禁 glob，T0_CHAIN_WIRING_GAPS §A） | LK-05 | **P1** |
| L05-C05 | 六段词表真源统一（Owner 门位） | D-14：R2SIX（有漂移守卫）vs 产线占位（无守卫）同闸宽差 75%；裁后产线改消费六段真源=生产决策链行为变更 | FINAL_REPORT §五-4 | P1（Owner 批后即施工） |
| L05-C06 | **ETF 做T线立卡落地 T0-ETF** | 每只 ETF 成本独立实测（佣金+价差分列）；池=近 60 日日均成交额过滤 top100 起；格门槛 30 对（17 §三.4）；宇宙分类复用 ETFT0-SCREEN frozen 关键词（etft0_prereg_card.md §2）；D26 通道 C=etf_1min 合成先行 | 05 号文 ⓪.4；D26 | **P1** |
| L05-C07 | 宏观门"趋势支"换源裁定（Owner 门位） | dominant 实为波动四档非趋势，卡面语义方向相反；两源一致率 21.09%；修法①换源 regime_snapshot_history 七态 HMM 或②改态集——任一=作废重开考试卡 | FINAL_REPORT §五-6 | P2（Owner 批后重开卡） |
| L05-C08 | tick 时区纪元核验 | tick_data 早期行 01:30 UTC-wall-clock 混用嫌疑（与已解决 ETF 分钟案同类）；不定此，5.4/3.5 任何日内顺序主张=沙上塔（矩阵 §四.2） | 普查 PIT 红旗 | P2 |
| L05-C09 | 板块盘中供给修复 S1→S5 | 设计稿全备（BOARD_INDEX_INTRADAY_SUPPLY_DESIGN.md §6）：S1 成分 PIT 快照落库=真瓶颈、S2 tick 纪元、S3 板块 1 分钟自算回填 2021-09→、S4 厂商流降级对账、S5 事件层停回填+注册表纠偏；验收=§4 六条（含"切断厂商流一日下游不变红"免疫测试）；解锁 6.1/6.2 | 矩阵 §四.3 | P2（数据线车道） |
| L05-C10 | 做T链路自动化接线批 | T0_CHAIN_WIRING_GAPS §D 配方（按风险升序）：D-1 pipeline_events 新 kind t0_condition_pack_due（事件触发，宪法 §9.3）→D-2 build_anchored_state_history 自动产出者（头部空洞）→D-3 factory_grid_executor+grid schema 增 T_cond_pack 轴（显式常量路径）→D-4 search_space_prereg.yaml 加 t0 axes+实测回填 per_point_seconds（Owner 签）→D-5 f06_survivors.csv 补生成器（消手工清单违宪 §9.5） | T0_CHAIN_WIRING_GAPS §D | P2 |
| L05-C11 | 个股条件维（市值/新闻）立卡 | 市值五分位、新闻十分位、每格 n≥30（17 §三.3）；新闻发布时点审计先行；跨 L04 交接 | 05 号文 ⓪.3 | P3 |
| L05-C12 | 自动提假设引擎立卡 | 每周≥5 条新假设入 meta_question 带考试卡草稿；双周报双率（17 §三.6）；激活 exam_loop 空壳（11 号文 §185） | 05 号文 ⓪.6 | P3 |
| L05-C13 | D24/D26/D36 数据缺口销项 | D24 封单 tick 买一档量代理+MFE/MAE 台账字段；D26 etf_60min 四段 9 万 bar（工单已移交 datavein，本项只跟踪）；D36 五档差 17 交易日（服务器 ~1 月保留窗每晚一天少一天，data-sufficiency-matrix L5 行） | DU 账本 | P3（D36 时间敏感建议提级） |
| L05-C14 | GPU 做T条件维消费接线 | 前置=C05/C07 词表裁定；自由度≈1 结论落入搜索空间（禁按"状态×情绪"两维独立展开）；B4 包经 C10-D3/D4 正门接入 | FINAL_REPORT §五-3 | P3（悬案裁后启动） |

施工项计数：**14 项**（P1×6 / P2×4 / P3×4）。

**内收声明（净零增长，宪法 §4）**：C01 复用 w2_sector_minute_resample 技术路线不新建框架；
C03/C04 全部复用 B4 既有包+P1 四元组判据（04 号文），零新判据；
C06 复用 ETFT0-SCREEN frozen 分类与 17 §三.4 判据，替代并退役 6.3 的"日频近似"歧路；
C09 复用 BOARD_INDEX_INTRADAY_SUPPLY_DESIGN 设计稿（零新设计）；
C10 全部为既有件接线零新系统；C02 复用 cost_trio_exam.py 判据（import 复用禁重写）。

---

## 8. 标准件（18 号文纪律：有行业标准/开源实现必须引用并采用，不自造）

### 8.1 学术锚点（2024-2025 最新+承矿册既有锚点）

| # | 标准/文献 | 出处 | 对 L05 的采用点 |
|---|---|---|---|
| S1 | Market Intraday Momentum（首半小时收益预测尾半小时） | Gao, Han, Li & Zhou, *JFE* 129(2) 2018, pp.394-414；国际版 *JFQA* 2020（43 国） | 3.3 ORB/3.1 开盘冲高族的假设卡经济解释与先验方向；A 股本地化须重估（T+1/涨跌停制度差） |
| S2 | Intraday Time-Series Momentum: International Evidence（16 个发达市场日内时序动量） | Liu et al., Lancaster Univ. working paper（wp.lancs.ac.uk）；Liu 2023 "Time Series Momentum and Reversal: Intraday Information"（RePEc，被引 11） | 2.2 波动率自适应带与 3.x 族的"信息源是什么"回答（对应 T0_SCHEME_MATRIX §三推论 2 的三问） |
| S3 | Infrequent Rebalancing, Return Autocorrelation, and Seasonality | Bogousslavsky, *JF* 71(6) 2016, pp.2967-3006（被引 ~186）；后续 Bogousslavsky & Collin-Dufresne, *JFE* 141(1) 2021 "The Cross-Section of Intraday and Overnight Returns" | 隔夜/日内收益负自相关+日内季节性=3.4 尾盘动量与 8.3 隔夜过冲的机制先验；D3 市值维的经济解释 |
| S4 | Interday Cross-Sectional Momentum: Global Evidence（半小时收益跨日企业级预测，高频新数据集） | SSRN 2025-07-19 | 9.3 日内高频因子族的多重检验对照面（2025 最新证据锚） |
| S5 | Intraday Price Reversals and Momentum（阈值法而非相对同伴法） | Heldens, Tilburg Univ.（arno.uvt.nl） | 3.2 VWAP 带反转的带宽定档方法论（阈值法先于分位相对法） |
| S6 | 微观结构四基石（做T价差=逆向选择成本分解）：Roll 1984 JF / Glosten-Milgrom 1985 JET / Kyle 1985 ECMA / OFI：Cont-Kukanov-Stoikov 2014 JF | 矿册 §学术锚点 已录（METHOD_MINING_t0.md:538-547） | 5.x 订单流族与成本三件套（B2）的价差成分解释 |
| S7 | 执行优化经典：Almgren-Chriss 2001 JPM / Bertsimas-Lo 1998 JPM / Almgren et al. 2005；做市：Avellaneda-Stoikov 2008 QF；RL 做市 2024-2025 沿革=AS 报价嵌入 RL 动作空间（PPO/SAC vs AS 基准，arXiv q-fin.TR 在线系列，检索受限未能锁定单篇，登记待补锚） | 矿册已录+本簿补 2024-2025 方向 | F1 执行族与 9.2 RL 调参的考尺设计；9.2 首发不建议的依据 |
| S8 | 多重检验与回测过拟合三件套：Harvey-Liu 2015 JPM haircut Sharpe / Bailey-López de Prado 2014 DSR / Bailey et al. 2017 PBO-CSCV；最新证据=Nefedov 2025 SSRN（天真评估虚增年化夏普 ~3.6 倍，严格协议下六因子全灭）；WFA：Pardo（WFE=OOS/IS≥50% 行业线，arXiv 2025-12 严格 WFA 框架同口径） | 17 号文 §一/§三.2 与 18 号文 §二 已立法 | 全部 B/C/D 考试族的判卷底线（禁自造判据） |
| S9 | 日内 U 形量价季节性：Jain-Joh 1988 / Admati-Pfleiderer 1988；涨跌停磁吸：Chan-Fong 2000 JFQA（A 股结论分歧按"存在但强度状态依赖"保守处理） | 矿册 §学术锚点 已录 | 时段准入矩阵（A1 D58）的学术背书 |
| S10 | 日内高频因子：Bollen, Ibbotson, Jiang & Insley 2017 *Financial Analysts Journal*；A 股隔夜/日内分解（Heston 框架本地化） | 矿册 §学术锚点 已录 | 9.3 因子族候选清单与 8.3 隔夜腿 |

> 检索纪律披露：本次 web 检索中学术查询多轮被源端限流（HTTP 429），S1-S5 为成功回传结果；
> S7 的 2024-2025 RL 做市单篇与 S4 全文未能逐篇核验，已在表中如实登记"待补锚"，
> 不以记忆冒充出处（18 号文引用纪律）。

### 8.2 开源可复用实现（仓库+许可证；承矿册 §开源"仅登记不克隆不运行"）

| 仓库 | 许可证 | 性能/能力要点 | 对 L05 的采用点与边界 |
|---|---|---|---|
| polakowo/vectorbt | **fair-code：Apache 2.0 with Commons Clause**（禁转售软件本身；内部自用无碍，vectorbt.dev Terms 实证） | NumPy/Numba 全向量化，暴力参数扫（百万级组合）；分钟-bar 大行情=其最佳场景 | **D2 全量×状态匹配引擎的首选对表件**（向量化扫 周期×规则 格点）；注意其组合优化式回测对"同体往返"语义弱，配对判据仍以 cost_trio_exam.py 为真源 |
| polakowo/vectorbt PRO | 专有商业（付费） | 标准版之上增强 | 不引入（预算与许可双边界），登记存在即可 |
| nautechsystems/nautilus_trader | **LGPL**（Rust 核心+Python 策略层） | 事件驱动、纳秒级时钟、回测/沙箱/实盘同代码；保真高、暴力扫慢于 vectorbt | **A2 三策略执行语义与 P2-03 闭环的对表件**（live/backtest parity）；A 股适配层须自建（现货费率/涨跌停/T+1 约束仓内已有真源，禁框架默认值顶替） |
| nkaz001/hftbacktest | **MIT** | tick 级回测：队列位次建模+feed/订单延迟建模+概率成交；Rust+Python | 1.4 被动队列与 5.4 3s 微观动量的成交概率模型参照；数据口径需 A 股化（矿册已录此边界） |
| microsoft/qlib | **MIT** | Alpha158/Alpha360 OHLCV 因子集+分钟数据处理管线 | 9.1/9.3 特征工程对表（禁逐因子重造）；其日内数据格式可作转债分钟腿（C01）存储参照 |
| vnpy / wondertrader / QUANTAXIS | 各自开源许可（vnpy MIT；wondertrader 自有许可；引入前逐核） | 国内实盘接入（wondertrader 支持 CTP 期指腿） | 07 执行链路对照，非本线施工件（矿册已录） |
| TqSdk / openctp | 各自许可 | 中金所行情/撮合仿真 | 2.4/6.4 若补期指分钟线的候选源；4.2/7.x 排队成交概率测试床（矿册已录） |
| akshare / mootdx / pytdx；easytrader+easyquotation | 各自许可 | 采集链同源；券商 API 灰产边界 | 前者=现采集链同源；后者=**反面教材禁引入**（合规红线，矿册已录） |

### 8.3 仓内自产标准件（对表纪律的"内部标准"面，禁重写）

- 成本口径：`scripts/audit/cost_trio_exam.py`（RT_COST_BP=31.2，:56；build_pairs 配对真源——任何新考卷 import 复用，V3 卡 §3 明令禁重写）。
- 六段判定：`scripts/backtest/auto_mount.py` R2SIX(:129)/phase_overlay(:225)/resolve_six_phase(:248)（法定判定器，禁本地字典顶替——REDEVID 探针 5 已证测试承重）。
- 对账范式：`t0_gpu_condition_pack.py --reconcile`（逐格对账+变异自探针+包外真源结构校验，FINAL_REPORT §六之四）——新考卷的承重测试模板。
- 容量预检范式：T0-CEILING 单向判读卡（`t0_ceiling_prereg_card.md` §0）——C03 多周期轴的容量预检先行即复制此范式。
- ETF 宇宙分类：`etft0_prereg_card.md` §2 frozen 关键词（C06 直接复用）。

---

## 9. 与他链路交接（防撞车）

| 链路 | 交接物 | 边界 |
|---|---|---|
| L04 选股传导 | D3 市值/新闻条件维（选股层条件维） | 本簿只登记判据（17 §三.3），立卡施工归 L04 主责 |
| L06 考试分配 | B4 GPU 包+B1 verdict+自由度≈1 悬案 | 悬案裁定前 L06 不得按两维独立展开做T条件维 |
| L07 执行 | F1 执行族+A2 三策略+tick 盘口失衡执行增强 v2 | tick 独立信号判死口径不放宽（01_goal §三行 7） |
| L08 风控 | X-R1 熔断停做T/D111 风控层三档止损（yaml A1 注释） | 止损三档只评底仓不评 T 腿（外审 m-12） |
| L09 复盘 | A3 闭环判定→C3 归因 D50 拆账 | 做T贡献拆账口径=交易盈亏/持仓盈亏二分+三腿分离 |
| 数据线（datavein） | C09 板块供给 S1-S5+D26 工单+C01 转债重采样排期协调 | 设计稿已交（BOARD_INDEX_INTRADAY_SUPPLY_DESIGN next_action 字段），本簿不代施工 |
| Owner 门位 | C05 词表（§五-4）/C07 趋势支换源（§五-6）/自由度≈1（§五-3）/材料线已批（05 §一） | 三件待裁+一件已批； Owner 不裁则 C07/C14 阻断，其余照常 |

---

## 10. 本簿治理注记

- 本簿为本次任务**唯一可写件**（只读挖矿约束）；CREATE-GUARD 的 creation_token 登记与
  新模块大白话翻译未做（登记动作须写他件，超出本任务可写面）——移交下一批施工会话随批登记
  （links/README 施工纪律：落地前置=先行批）。
- 45 件 t0 批次盘面在 `.worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/`（主区 docs/_working/t0_matrix/ 仅 10 件），
  本簿引用时对两处分别注明；队列落地以 commit_queue 为准（07 号文：做T 3 批 46 件 pending、甲位已批）。
- 文档矛盾 1 处已登记（§5 D5 ⑥：17 号文 §三.5 分钟语料起点 2019 vs 裁定#413④ 实测 2021-09），
  处置=交总指挥裁定，本簿不代改 17 号文。
