---
ttl: task_bound
doc_type: design
title: T0-MATERIAL 做T材料线预注册考试卡（草案，Owner 签发即 frozen）
created: "2026-09-26"
status: draft_pending_owner（签发即 frozen：签后任何字段不得改动，改动=作废重开；frozen 先于正式取数）
family_id: T0-MATERIAL
lane: L05_t0
executes: L05-C02（links/L05_t0/SKEL.md §7）；FINAL_REPORT §五-2 Owner 已点头开工（"点头即可执行，不需再议口径"）
ruling_basis: 裁定#399 二（做T 复活唯一口=新预注册卡+考试制）；裁定#413④（kline_1min=信号法定轴）；Owner 已批材料线开闸（05 号文 §一）
inputs:
  - docs/_working/t0_matrix/FINAL_REPORT_t0_matrix_reexam.md §七（材料线设计要点 0-5，本卡逐条落格）
  - docs/_working/decision_map_campaign/17_quantified_acceptance.md §三.1/§三.5（多周期轴/行情段判据）
  - docs/_working/decision_map_campaign/05_t0_and_strategy_library.md ⓪.1（多周期买卖点轴）
  - scripts/audit/cost_trio_exam.py（判据唯一真源：RT_COST_BP=31.2 / EDGE_PRECONDITION_BP=30 / PAIR_GATE=30 / build_pairs，import 复用禁重写）
  - .worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md §4（材料资格 M-1..M-4 母本）+ §8.3（材料线移交条款）
  - links/L05_t0/material_precapacity_report.md（容量预检先行件，本卡取数前置）
  - scripts/backtest/t0_material_line.py（执行件，M0 参数与本卡 §4 逐字一致）
容量预检: links/L05_t0/material_precapacity_report.md（v1 规则集 ≈23.3h < 48h CPU 预算；语料 ≈282 万对/周期；30 对土规超 5 个数量级达标）
规则数报备（17 号文 §三.1）: '**1 规则（M0 grid=100bp）× 5 周期（1/5/15/30/60min）= 5 次构建**；扩 grid/换模型=修卡重开，禁临场加档'
---

# T0-MATERIAL：分钟驱动同票同日既买又卖语料 · 预注册考试卡（草案）

## 0. 立卡理由与目的声明（逐字承 FINAL_REPORT §七.0，先立此为据）

1. 本卡第一目的**不是"凑够 30 对让 V3 过关"**（D-7/V3 §8.3 禁造料继续有效），
   而是"给有信息源的方法提供足够样本去测它有没有信息"。若某法在足量样本上仍不过，判死即是收获。
2. 容量预检已证（`material_precapacity_report.md`）：语料量级 282 万对/周期，土规解除后
   **无信息探针 M0 在 frozen 判据下净均 −39.12bp=FAIL**——本卡从设计上就不可能被"语料变大"自动洗绿。
3. T0-CEILING 已证成本不是闸、闸在极值次序与预测（`t0_ceiling_verdict.md` §1/§3）；
   本卡据此把语料定位为**判卷底座**（D2 相位×周期×板块族矩阵与各方法卡的共同取数面），不定位为"可行性证明"。

## 1. 假设与判读边界

- **H1（合格性假设）**：在 frozen 成交模型 M0 与日历窗规则下，`c1_market.kline_1min` 研究段
  可构建 n≥30 的同票同日既买又卖语料，且每对可按 CST-T0-001 口径计算毛/净价差与前置命中。
  （预检实测：≈282 万对/周期，达标。）
- **H2（基线假设，预期为红）**：无信息 M0 探针对集满足"开仓前置命中率 ≥0.30 且净均 >0"。
  预期 FAIL；FAIL=诚实基线登记，**禁为转绿而调参**（§9 禁线 1）。
- 判读边界：本卡 verdict 只对上述两条说话；**禁**把任何 PASS 读成"做T 可行"
  （T0-CEILING §5 单向判读同款防误读清单）。

## 2. 对象与配对规则（frozen 口径引用，零重写）

- 材料=分钟驱动的模拟成交两腿（非真单，§9 灰区 2 如实披露）；配对规则唯一真源=
  `scripts/audit/cost_trio_exam.py:build_pairs()`（**同票同日既买又卖计 1 对、配对量=min(Σ买,Σ卖)、
  全侧 VWAP 近似、毛价差 bp=(卖VWAP/买VWAP−1)×1e4**——import 复用，本卡与执行件均不重写该逻辑）。
- 成本口径唯一真源=CST-T0-001（`config` 注册表 + `cost_trio_exam.py:56 RT_COST_BP=31.2`，只读引用）。

## 3. 成本假设（逐字继承，一个数字都不改）

| 项 | 值 | 真源（引用不重写） |
|---|---|---|
| 往返固定成本 rt | **31.2bp**（佣金双边 6+印花 5+过户双边 0.2+滑点 2×10） | `cost_trio_exam.py:56`；CST-T0-001 |
| 开仓前置 | 毛价差 ≥**30bp** | `cost_trio_exam.py:55` |
| 前置命中率门槛 | ≥**0.30** | 同上 |
| 结论土规 | n_symbol_day_pairs ≥**30** 才出结论，否则 `INSUFFICIENT_SAMPLES` | `cost_trio_exam.py:54`（REG-VALM-001） |
| 净价差 | net_bp = gross_bp − 31.2 | 同上 |

## 4. 成交模型 M0（frozen 先于取数；本节=FINAL_REPORT §七.2"必须先写死"的落格）

- **基准价**：当日首根（周期级）bar 的 open。日历规则给定，零拟合。
- **买触发**：bar.low ≤ base×(1−100bp/1e4)；**成交价档=min(bar.open, 触发价)**
  （挂单限价机制：开盘即低于限价按开盘成交；触档即成交的队列假设偏乐观，如实披露）。
- **卖触发**：买后（严格晚于买 bar）bar.high ≥ buy_fill×(1+100bp/1e4)；
  **成交价档=max(bar.open, 触发价)**。
- **收盘强平**：当日末根仍未触发卖出 ⇒ 以末根 close 强平；两腿同日，配对仍成立（如实入样，禁挑样）。
- **单 T**：每 symbol-day 至多一次往返（首触即用）。多次往返属未来另卡，禁在本卡扩。
- **数量**：floor(notional/buy_fill/100)×100 股（整手，notional=10 万 CNY），不足一手按一手。
- **滑点一次了断（§七.2 悬案的终答）**：**滑点不进模拟成交价、也不额外叠加**——CST-T0-001 的
  31.2bp 已含 2×10bp 滑点，模型内再计=双计。V3 卡 §8.2 灰区就此关闭：本卡材料的
  模拟成交价=纯价格档位，成本全部由固定口径承担。逐笔 commission 字段仅填佣金 3bp/腿作披露列
  （`realized_comm_bp`），不进净值。
- **周期重采样**（多周期轴接口，05 号文 ⓪.1）：1min 原生；{5,15,30,60}min 按**日内 bar 序数分桶**
  （每 P 根合成一根，桶内 OHLCV 聚合，桶时刻=桶内末根）；不按钟面对齐 ⇒ 午休/缺 bar 免疫。
  120min 不做（Owner 明令）。
- **可交易过滤**：周期级 bar 数 < `MIN_BARS_BY_PERIOD`（1:200/5:40/15:14/30:7/60:4，
  ≥83% 标准 session）剔；含零价 bar（low=0）剔（`t0_ceiling_verdict.md` §4 除零契约）。
- **模型参数零数据拟合声明**：grid=100bp/notional=10 万/min_bars 全部为写卡既定值，
  与任何取数结果统计无关（frozen 先于取数，mtime 链可核）。

## 5. 窗规则（日历化，禁看结果挑窗；§七.3 落格）

- **研究语料窗=[2021-09-01, 2025-09-09]**：起点=分钟库法定起点（裁定#413④），
  终点=闭卷切点（17 号文 §三.5；HOLDOUT 纪律不变）。**执行件硬拦**：`--end` 越切点=SystemExit
  （`scripts/backtest/t0_material_line.py:enforce_closed_book`），禁闭卷数据入研究。
- 闭卷段（切点后 253 个交易日）**本卡零触碰**；闭卷考属签发后的独立考程（同语料口径另行走卷），
  且取数前不得以任何形式读取切点后数据定档/调参。
- 宇宙=研究段有数的 5,410 只（全库 5,853 只中 443 只首 bar 在切点后，无研究段语料，如实剔除计数）。

## 6. 材料资格审计门（承 V3 卡 §4 M-1..M-4，构造性满足+机械复核）

| 门 | 口径 | 本卡实现 |
|---|---|---|
| M-1 日内粒度 | timestamp 含时分 | 构造即含；产物审计列 `by_construction` |
| M-2 往返同体 | 两腿同 run 同组合 | 两腿同 run_id（单跑单语料），`by_construction` |
| M-3 材料去重 | 指纹去重防重放 | 语料直接生成无重放件，`not_applicable`（如实披露） |
| M-4 涨跌停可行域 | \|gross_bp\| ≤ 板别单日极限 | 主板 ±10%/创业科创 ±20%/北交所 ±30%（红蓝 #11），超限剔除并计数 `rejected_price_limit` |

## 7. 判据与 verdict（零改动，fail-closed）

- 判卷=对语料对集复算 frozen 四数（n/前置命中率/净均/毛 p50），verdict 三态：
  - `INSUFFICIENT_SAMPLES`：n<30（预检证明概率≈0，但规则保留不豁免）；
  - `FAIL`：前置命中率 <0.30 或 净均 ≤0（**预期态**；M0 预检实测净均 −39.12bp）；
  - `PASS`：n≥30 且前置命中率 ≥0.30 且 净均 >0 —— **PASS 触发"好得可疑"强制复核**
    （17 号文 §一垃圾触发线同款直觉：无信息探针考绿只可能是双计/前视/口径错，先查实现再谈结论）。
- 禁改判档表述遵裁定#325；全量披露含 RED，禁事后挑样；产物机读=.yaml+.parquet
  （**禁 summary.json**——n_trial_ledger glob 计 DSR 分母=科学污染，
  `src/zephyr/backtest/core/n_trial_ledger.py:421` 教训）。

## 8. 执行件、产物与消费面

- 执行件：`scripts/backtest/t0_material_line.py`（`--symbols/--pool-file/--sample` 参数化；
  `--period 1,5,15,30,60` 多周期接口；分批断点续跑=按 symbol 批落盘）。
- 产物：`data/backtest_artifacts/t0_material_line/` 下 `t0_material_pairs_<tag>_<period>.parquet`
  （对级语料）+ `t0_material_stats_<tag>.yaml`（对数统计：逐周期 n/触档率/M-4 剔除/前置命中/净正/耗时）。
- 测试：`tests/backtest/test_t0_material_line.py`（构造数据 14 例：触发/成交价档/强平/除零挡/
  分桶/板别门/闭卷硬拦/抽样确定性/FakeConn 端到端；**禁真全量跑**）。
- 下游消费：L05-C04 全量×状态匹配引擎（相位×周期×板块族矩阵，P1 四元组+Wilson LB 口径）；
  各方法卡（T0_SCHEME_MATRIX ✅可考 7 法）在同语料基础设施上另立卡考；E4 族若换料重考，
  走 V3 卡作废重开流程，本卡不代改 V3。

## 9. 已知灰区与禁线（写卡时即定，禁临场改）

1. **禁线（D-7 同构）**：禁为转绿/凑 n 而调 grid、改 min_bars、换强平规则、扩窗、并格并票。
   任何此类变更=本卡作废重开。阈值复核（如"30 对土规本身"）走正式裁定通道（FINAL_REPORT §七.5）。
2. **材料是模拟成交非真单**：无排队/无冲击/触档即成交偏乐观；部分被"限价机制取开盘价"抵消，
   方向不完全对冲，判读须带此保留。
3. **1.48 亿行级取数为活表读**（ReplacingMergeTree）：bar 按 (symbol,trade_date,trade_time) 去重
   （`t0_ceiling_verdict.md` §4 uniqExact 教训）；正式跑前后各抽一批对数复核漂移（容差 <0.5%）。
4. **探针与被考方法的独立性**：M0 语料对集本身**不得**作为任何方法卡的"样本外证据"重复计 n
   （同一对两处计分=多重检验污染）；方法卡考各自触发的对集，语料库只供基础设施与对照基线。
5. 六段相位等条件轴取数承 B4 真源（`six_phase_history_v1.csv`），本卡不自带条件定义；
   ignition 等极稀格按 n≥30 如实 INSUFFICIENT，禁并格。

## 10. 与前卡/前裁边界

- 判据、配对、成本：与 V3/CST-T0-001 同源同值（import 复用），本卡零新判据（内收，宪法 §4）。
- 与 V3 的关系：V3 考的是"回测流水对"的条件经济学（26 对，verdict 如实不足）；
  本卡供的是"分钟语料对"的底座与基线。V3 不因本卡存在而自动重跑/改判；
  其词表悬案（D-14）/趋势支换源（§五-6）仍按原升级路径等 Owner 裁。
- 与 ETFT0 卡正交（标的维不同）；与 tick 执行层（05 号文 §一）正交（本卡纯分钟研究面）。
