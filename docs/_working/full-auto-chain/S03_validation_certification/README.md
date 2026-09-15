---
ttl: task_bound
title: S03 因子验证与认证挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S03 因子验证与认证

> 挖矿定位：本环节承载**阻断性核查**（Owner 指令最高优先）：decision_gate 的 DSR fail-closed 是否接在 E4 批考或 intake 当前生效路径上。结论先行：**不阻断**（§1.4）。

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 形态证据认证器——✅ 日链自动
- `src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py`（MOD-SIG-148）：四闸纯函数化——闸A 单侧二项检验+BH-FDR q<0.05（Q_THRESHOLD=0.05 预注册）；闸B n_eff=n_events/fwd_window≥30（重叠窗保守折扣）；闸C 分 regime 加权 edge>0 且无单切片>90% 独活；闸D 贝叶斯收缩 shrunk=(hit_rate·n_eff+k·baseline)/(n_eff+k)，k=100。状态机 certified/probation/failed；失败 fail-closed（判不了=failed 不猜）；只读统计表（运动员不兼裁判）。
- FDR 单源：certifier:224 `from zephyr.factor.analysis.bhy_fdr import bh_qvalues`——bhy_fdr.py 为唯一 FDR 实现（BHY 任意相依口径），strategy_pipeline/bh_fdr.py:71 亦包装它。
- 触发：经调度器 daily_kline 档事件触发（STARTUP 声明"禁 cron 自轮询"），产出 c1_market.market_pattern_certification；消费者=PatternWeightSync shrunk 口径+/api/pattern-winrate 认证列（文件头 CONSUMERS 实引）。

### 1.2 策略链 FDR 门——✅ intake 自动
- `src/zephyr/strategy_pipeline/intake.py`：run_intake_auto(:429) 门序列=KillSwitch(:67 kill_switch_clear)→bothwin 及格集（screen_source 台账自取）→**BH-FDR q=0.10**（BH_Q=0.10 :57；fdr_gate :78-82→bh_fdr.bh_filter→bhy_fdr）→ρ>0.6 聚类簇首(:84)→FSM 预授权三条件（双窗过∧FDR 过∧无未决衰减预警，promote_to_sim :162-167）。
- 触发链（全自动）：c4_batch_screen.py:165-174 `_emit_pipeline_hook`→`pipeline_events.emit_c4_batch_completed`(:303)→journal→drain(:159)→`_default_handler`(:140-145)→run_intake_auto(dry_run=False)。

### 1.3 DSR 现状——⚠️ 度量已自动、判定器关闭、台账冻结
- 度量：E4 批考 DSR 自动计算——c4_batch_screen.py:131-136（SSOT=`zephyr.backtest.regime_validation.c4_deflated_sharpe_runner`官方件，经 `_c4_engine.batch_deflated_sharpe` 批内折减）落 strategy_screen.deflated_sharpe 列。
- 判定器：decision_gate.py 的 DSR 判定器默认关闭（见 §1.4）。
- 欠账（2026-09-14-dsr-enable-impact-assessment.md 结案核验后定案）：①0.9809 头名=N=1 solo 零折减虚高；②metrics.py 路径年化/日频量纲错配（z 虚高偏向 1，不可用）；③台账无 N 字段（145 条 DSR 冻结，解冻=N 账本重建+存量重算回填）；④两套实现均缺 Bailey-LdP 正典的跨试验夏普截面方差 V[{SR_n}] 输入。

### 1.4 阻断性核查结论（最高优先项）

**结论：不阻断。当前链路不会因 DSR 不可信而硬阻断策略通过。DSR 修复不是施工班前置。**

证据链（file:line）：
1. **DSR 判定器默认关闭**：`src/zephyr/backtest/core/decision_gate.py:279` `dsr_threshold: float | None = None`；:616-619 fail-closed 分支仅在 `self.config.dsr_threshold is not None` 时激活；文件头 INVARIANTS:8 自证"DSR可选判定器默认关闭(dsr_threshold=None不参与判定)"。
2. **全部三处构造均无参**（即无任何调用方配置 dsr_threshold）：`implementations/vectorized_engine.py:583` `gate = DecisionGate()`；`implementations/event_driven_engine.py:477` `gate = DecisionGate()`；`core/strategy_validation_pipeline.py:148` `gate = gate if gate is not None else DecisionGate()`。全仓 grep `dsr_threshold` 零 yaml/配置赋值点（唯一数值 0.95 在 simulation/sharpe_calculator_fixer.py，属模拟盘显著性另一体系，不接 decision_gate）。
3. **E4 批考不调 decision_gate**：`scripts/backtest/c4_batch_screen.py` 全文无 decision_gate import；其 DSR 只是度量列（:131-136），判定书明确**"无通过线（C5 差异化再甄别）"**（:260）——E4 是全量批测记账，不是 DSR 闸。
4. **intake 不调 decision_gate**：run_intake_auto 门序列（§1.2）只有 KillSwitch/BH-FDR/聚类/FSM 三条件，无 DSR 无 decision_gate。多检验闸由 BH-FDR q=0.10 承担（bh_fdr.py:28"默认 q=0.10，预授权写死在 intake guard"）。
5. decision_gate（含 OOS/DSR）只在**回测引擎-验证管线**路径（vectorized/event_driven/strategy_validation_pipeline），该路径无 src/scripts 自动链调用方（grep 仅注释引用）——不在 S04→S07 生效链上。

含义：DSR 欠账（N 账本/量纲/冻结）影响的是**未来把 dsr_threshold 配置上去时的判定质量**，以及转正证据包的数字可信度；不影响 S04-S07 链路通断。修复属挂起排期，非本班阻断项。

### 1.5 批次 A 执行器与 ANOVA——建而未跑/未建
- `scripts/backtest/factory_grid_executor.py`（20KB，2026-09-15 在档）：批次 A 主入口(:330)，冻结土规复用 _c4_engine，产出 manifest+**negatives.csv 阴性库**+summary；CONSUMERS 声明 factory_grid_ananova+E2 四车道挂接预留——**首跑未发生**。
- ANOVA：未建。裁定不引 fANOVA（license 非开源，PyPI"free for academic & non-commercial"），改自研约百行 pandas 经典方差分解（docs/_working/2026-09-14-full-chain-factory-blueprint.md C2 节，:287-290 附近）；启动条件=批次 A 普查跑完。

## 2 六向挖矿日志表

| 向 | 内部发现 | 外部发现(URL+年份) | 判定 |
|---|---------|-------------------|------|
| ①上游 | 认证器上游=c1_market.market_pattern_win_rate 统计表（只读）；intake 上游=strategy_screen bothwin p 值（screen_source）；FDR 单源=bhy_fdr | — | signal |
| ②下游 | 认证表下游=PatternWeightSync shrunk 口径+/api/pattern-winrate；intake 下游=FSM sim 流转+registry candidate；阴性库下游=E2 四车道（factory_grid_executor 预留） | — | signal |
| ③算法/机制 | 四闸=BH-FDR/n_eff/regime edge/收缩；intake=BHY q=0.10（任意相依稳健） | ①DSR 正典：纠正选择偏差/回测过拟合/非正态，E[max SR] 由试验数 N+截面方差驱动（https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf ，Bailey & López de Prado，JPM 2014；SSRN https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 ）；②PBO/CSCV：IS 最优策略 OOS 落后中位数的概率（https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf ，Bailey et al.，2015）；R 实现 https://cran.r-project.org/web/packages/pbo/ ；③BHY 任意相依 FDR（https://projecteuclid.org/journals/annals-of-statistics/volume-29/issue-4/The-control-of-the-false-discovery-rate-in-multiple-testing/10.1214/aos/1013699998.short ，Benjamini & Yekutieli，Annals of Statistics，2001）；④Harvey & Liu 回测多重检验折扣 Sharpe（https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF ，Duke，2015-2019）；⑤Palomar 教材 §8.3 回测的危险（https://portfoliooptimizationbook.com/book/8.3-dangers-backtesting.html ，HKUST，2023） | signal |
| ④后端 | **阻断性核查完成**（§1.4，不阻断）；DSR 双实现量纲错配实锤；N 字段落 schema 缺失 | DSR 计算器实践（https://metricgate.com/docs/deflated-johnson-sharpe-ratio/ ，MetricGate，2025）——印证"必须声明试验数 N"是业界标准输入 | signal |
| ⑤前端 | /api/pattern-winrate 认证列已挂；转正页属 S13 边界只登记 | — | signal（登记） |
| ⑥数据字段 | strategy_screen 缺 N/num_trials 列（:117 runner 注释有 num_trials 字段但台账 schema 无）——DSR 冻结根因的字段级定位；n_eff 所需 fwd_window 字段 win_rate 表已有 | — | signal |

外部搜索 3 轮全 signal，无受阻轮。

## 3 业界与开源对照（四闸过滤后）

| 业界标准 | 本仓现状 | 四闸结论 |
|---------|---------|---------|
| DSR 必须输入 N（试验数）+跨试验 SR 截面方差 V[{SR_n}]（Bailey-LdP 2014） | 官方件有 E[max Z_N] 计算但缺 V[{SR_n}] 输入与 N 账本；N=1 solo 零折减事故已实锤 | **完全对口欠账**：N 账本重建+V[{SR_n}] 引入=DSR 解冻的两块拼图，外部正典背书 |
| PBO/CSCV 补 DSR（一个管 Sharpe 折减、一个管排名稳定性） | 未建（overfitting_detector.py 有 WFA 过拟合检测，无 CSCV 全组合秩logit） | 可回测✅（输入=网格策略×日收益矩阵，批次 A 跑完即有）；**立卡挂起**，不引 R 包（自研百行 pandas 同 ANOVA 路线） |
| BHY 任意相依校正（统计正典） | bhy_fdr.py 已是单源，intake q=0.10 + 认证器 q=0.05 双口径预注册 | 已达业界标准，无施工 |
| Harvey-Liu 多重检验折扣 Sharpe / t>3.0 门槛呼声 | 未显式实现（DSR 冻结期间由 BH-FDR+双窗承担） | 长尾登记：若 DSR 长期不解冻，可评估以 Harvey-Liu 门槛作临时折扣口径 |
| A 股适配 | T+1/涨跌停已进成本冻结土规；散户主导→regime 闸（闸C）已覆盖 | 全部通过 |

## 4 堵点与欠账清单

1. **DSR 四坑**（定量，全部有文档真源）：N 未落账（145 条冻结）/双实现量纲错配/solo 零折减虚高/V[{SR_n}] 缺失。
2. **批次 A 首跑未发生**：factory_grid_executor.py 建成在档，阴性库/ANOVA 的上游数据全卡在此。
3. **ANOVA 未建**：裁定已定（自研 pandas 方差分解），启动条件=批次 A 跑完。
4. **PBO/CSCV 未建**（本次挖矿立卡）：多重检验体系第三块拼图。
5. 认证器自身 BH-FDR 文档字符串写 S2 纯函数但实际 import bhy_fdr（:224）——文档字符串与实现轻微漂移，低危登记。

## 5 施工项建议

**本班施工：无阻断项**（§1.4 已证链路通）。若施工班有余力按序：
- **N1（低风险，建议做）**：strategy_screen 台账 **N 字段落 schema**——c4_batch_screen.py 落库列追加 `num_trials`（批内实际行数，非 solo 口径），run 档案 summary 同步；验收=新批每行可查 N，历史行 NULL 留痕。这是 DSR 解冻三步（N 账本→存量重算→回填）的地基，今天不做、每多跑一批冻结债多一批。**【已落地 2026-09-15：c4_batch_screen.py:67/288-294 落库列+scripts/ch/apply_strategy_screen_num_trials_ddl.py 部署件】**
- **N2（文档修正）**：pattern_evidence_certifier.py 文件头 ALGO_FLOW S2 注释改为"消费 bhy_fdr.bh_qvalues"（一处注释，消除单源假象）。**【未修，登记维持】**

**挂起排期（写明解锁条件）**：
- H1 DSR 解冻三步（N 账本重建→存量按可考 N 重算回填→评估拨 dsr_threshold；解锁=N1 落地+重算工具就绪；真源=dsr-enable-impact-assessment.md §六）；
- H2 批次 A 首跑（解锁：Owner 时序/E0 放行；产出=阴性库+ANOVA 上游）；
- H3 ANOVA 自研百行 pandas（解锁：H2 完成；设计真源=factory-blueprint C2 节）；
- H4 PBO/CSCV 自研（解锁：H2 完成，网格策略×日收益矩阵可得；正典 URL 见 §2③）；
- H5 metrics.py 坏口径 DSR 下线或修复（解锁：H1 时一并处置，防未来误用）。

## 6 封矿结论

- 内部 6 向+外部 3 轮全 signal，无 noise 轮——时间盒封批。
- 长尾矿脉登记：①Wilson 下限在 win_rate 与认证器间的口径统一审计（单源已声明，未逐位核）；②FSM 预授权三条件之外是否需增"DSR 过"第四条件——待 H1 解冻后由裁定通道定，**禁止**静默加条件（阈值预注册纪律）。
- 方案封矿：fANOVA 引入（license 非开源+完整网格无需替代模型，既有裁定维持，留痕防重挖）。
