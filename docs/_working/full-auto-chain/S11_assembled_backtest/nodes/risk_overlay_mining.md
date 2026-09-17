---
ttl: task_bound
title: T1-β 节点挖矿：风控叠加层（回测风险信号 vs 生产消费接线 / 蓝图兑现核对）
session: st-qoder-t1b-h-20260916
date: 2026-09-16
parent: S11_assembled_backtest
lane: H
---

# 节点挖矿：风控叠加层（父环节 S11_assembled_backtest）

> 范围：S11 整装回测**产出的风险信号**（overfitting_flag / DSR / sanity / 流动性旁路 / 现金缺口）
> 在**下游是否真被吃掉**——蓝图契约 vs 生产接线。regime 标签漂移（F1）、回测/实盘双轨语义
> （F2）、regime 最后一公里（F3）已由 `regime_supply_chain_mining.md` 覆盖，本文不重复；
> 实盘 pre-trade 风控（`risk/` 域 orchestrator）非本节点，仅在与"回测风险信号是否跨到实盘"
> 交界处点名。实证锚点 file:line + 现网产物（overfitting_flag=True 却 acceptance.ok=true）。

## 1 现状盘点（蓝图宣称 → 生产接线逐一验真/验伪）

### 1.1 回测**产出**了哪些风险信号

| 信号 | 产出处 | 现网值（bt-fw-823d7fd7） |
|------|--------|--------------------------|
| `overfitting_flag` | metrics.py:305 `is_overfitting = dsr<0.5`；引擎回填 vectorized_engine.py:352 | **True** |
| `dsr` / `adjusted_sharpe` / `expected_max_sharpe` | calculate_full_metrics（metrics.py:290-305） | DSR≈0（Sharpe -2.12） |
| `sanity`（极端收益/空跑护栏） | `enforce_result_plausibility`（engine_base.py:184；调用 vectorized_engine.py:357） | 通过（区间 [-95%,+1000%]） |
| 流动性冲击旁路 | matching_engine.py:712-714 | 静默（见 §H1/§H2） |
| 被拒成交（现金/T+1/持仓不足） | vectorized_engine.py:301-312 | 仅日志 |
| n_trials（DSR 原料） | metrics.py:239 默认 10 | **违约**（未传真值） |

### 1.2 生产**消费**接线：只有 sanity 真被吃，其余全断线

- ✅ **sanity_guard 是唯一被硬执行的刹车**：`enforce_result_plausibility` 在 run() 内调用
  （vectorized_engine.py:356-364），越界即 raise。但其容差极宽
  （`max_plausible_total_return=10.0` / `min=-0.95`，vectorized_engine.py:125-126）→ 现网
  -18.5% 轻松通过，**几乎不构成约束**。
- ❌ **overfitting_flag 产而不消**：
  - 引擎内 `strict_overfitting_gate` 默认 **False**（vectorized_engine.py:112,380）；
  - **全仓 `strict_overfitting_gate=True` 零命中**（grep src+scripts，仅 overfitting_detector.py
    注释出现）→ SIM-56"上线前自动门禁阻断"（overfitting_detector.py:28、engine_base.py:82
    文档契约"overfitting_flag=True 下游应降权或拒绝"）**在生产从不触发**；
  - 自动验收 `fw_backtest.py:249-255` = `ok ∧ within_tolerance(panel) ∧ equity_points>0`，
    **不读 overfitting_flag/dsr**；pf_core/strategy_pipeline/governance **无一处引用
    overfitting_flag**（grep 空）。→ **现网实证：overfitting_flag=True 的 run，acceptance.ok=true
    并作为证据固化**。
- ❌ **完整决策门控链零接线**：
  - `DefaultBacktestEngine.evaluate_decision_gate`（vectorized_engine.py:562，
    event_driven_engine.py:452）**全 src 零调用点**（grep：仅两处 def，无 caller）；
  - `run_strategy_validation`（strategy_validation_pipeline.py:123，封装 OverfittingDetector
    三维 + DecisionGate 三阶段）**唯一调用方是离线脚本**
    `scripts/backtest/eval_f2_narrow_backtest.py:232` → **不进 S11 自动/整装回测路径**；
  - DecisionGate 自身 DSR 判定器**默认关闭**（decision_gate.py:260,279 `dsr_threshold=None
    =不参与判定`，注 52号§7③），即便被调，DSR≥0.95 线也需显式注入才生效，且注入路径
    （`evaluate_decision_gate`）本身无人走。
- ❌ **n_trials 契约违反**：引擎调用 `calculate_full_metrics` **不传 n_trials**
  （vectorized_engine.py:328-332）→ 落 `DEFAULT_N_TRIALS=10`（metrics.py:239），violates
  "调用方 MUST 传入实际试错次数"（metrics 文档）→ DSR 的多重测试修正基数是**拍脑袋默认**。

### 1.3 回测风险信号 → 实盘：断链

- 实盘 pre-trade 走 `RiskValidationBridge`（governance/adapters/risk_validation_bridge.py）
  包装 `RiskValidatorProtocol`（validate_order/validate_portfolio，:57-115），吃的是
  `shared.contracts.risk_limits.RiskLimits`（限额），**不读回测 overfitting_flag/dsr**。
  → 回测层"这个策略过拟合/不显著"的信号**没有任何通道**传到实盘准入（跨轨断链；
  与 F2 双轨语义互补：F2 讲 regime 口径分叉，此处讲风控裁决口径根本不跨轨传递）。

### 1.4 静默降级面（风险保护"看着在、其实旁路"）

- PIT/ST 过滤 CH 不可达 → fail-open 不过滤（vectorized_engine.py:156,271，warn 一次）；
- 冲击/参与率 volume 缺失 → 旁路记 INFO（:246-249，注释却称 warn）；
- 涨跌停三级解析 provider 不可达 → fail-open（承 summary StkLimitProvider）；
- regime 动态失败 → 静态降级（fw_backtest.py:167-186）。
- → 四类风险护栏**默认全是"拿不到数据就当没事"**，且降级只落日志/INFO，不进 acceptance。

## 2 六向挖矿日志表

| 方向 | 矿点 | 锚点 | 实证 | 结论 |
|------|------|------|------|------|
| ②下游 | overfitting_flag 消费 | fw_backtest.py:249-255 | True 却 ok=true | 产而不消（P0） |
| ②下游 | strict gate | vectorized_engine.py:112 全仓无 True | 零命中 | SIM-56 死配置（P0） |
| ②下游 | 决策门控 | evaluate_decision_gate:562 | 零调用 | 未接线（P1） |
| ①上游 | DSR 基数 | metrics.py:239 n_trials=10 | 引擎不传 | 契约违反（P1） |
| ③机制 | sanity 容差 | vectorized_engine.py:125-126 | [-95%,+1000%] | 唯一刹车却过宽（P2） |
| ②下游 | 跨轨到实盘 | risk_validation_bridge | 不读回测旗标 | 断链（P1） |
| ④后端 | fail-open 面 | :156/:271/:246/:712 | 4 处静默 | 风险护栏假在（P1） |

## 3 业界与开源对照（四闸）

- **过拟合闸须 fail-closed**：合规回测框架（CPCV/PBO，López de Prado；Zipline/quantopian
  的 performance attribution 门禁）以"不显著即拒"为默认。本项目 DecisionGate 已实现
  IS→WFA→OOS 三段 + DSR≥0.95，但**默认关闭 + 唯一走它的路径（整装自动回测）不调用它** →
  蓝图兑现为 0。四闸：可得✓（件都在）A股适配✓ → **纯接线缺口**。
- **多重测试基数 n_trials**：DSR/PBO 要求**真实试验数**（业界强调 trial 登记），本项目
  硬编码 10 且被 metrics 文档自禁 → 违反"来源可溯"。
- **风险旗标跨轨**：成熟系统把回测风控裁决作为实盘准入门（gate-on-artifact）；本项目回测旗标
  与实盘限额校验两两不通 → 四闸"A股适配"层面属能力割裂。

## 4 堵点与欠账清单（文件/函数/验收标准）

| ID | 级别 | 病灶类 | 堵点 | 可施工验收标准 |
|----|------|--------|------|----------------|
| H5-A | **P0** | 产而不消 | overfitting_flag/dsr 不被 acceptance 读，True 仍放行 | `fw_backtest.py:249-255` acceptance 增列 `overfitting_flag=False ∧ dsr≥阈值` 硬项；验收：现网 bt-fw-823d7fd7 类（flag=True）须判 ok=false |
| H5-B | **P1** | 零消费者 | `evaluate_decision_gate`（:562）/`run_strategy_validation`（离线脚本独占）未接进 S11 | 在 `run_framework_backtest` 收尾调 DecisionGate（含 IS/OOS/DSR 三段），产出 decision 进产物；验收：门控结果成为 acceptance 一部分 |
| H5-C | **P1** | 阈值未校准/契约违反 | n_trials 未传→DSR 用默认 10（vectorized_engine.py:328/metrics.py:239） | 由 plan/TDM 实际试错次数注入 n_trials；验收：DSR 基数可溯源到真实 trial 计数 |
| H5-D | **P1** | 静默降级 | 4 处风险护栏 fail-open 不进 acceptance（:156,246,271,712） | 每次降级计数并落 metrics + WARNING；acceptance 附 `degraded_guard` 列表；验收：不可达运行可见"哪些闸当次失效" |
| H5-E | **P1** | 跨轨断链 | 回测风险旗标不传实盘准入（risk_validation_bridge 不吃旗标） | 定义 backtest→live 准入契约（旗标随产物入实盘门）；验收：被回测判过拟合的策略无法过实盘 pre-trade（或显式豁免留痕） |
| H5-F | **P2** | 阈值过宽 | sanity 容差 [-95%,+1000%]（:125-126） | 收紧或改为相对基准的合理性判据；验收：极端但"合规区间内"的失真结果有二次拦截 |

## 5 子节点清单

- H5.a acceptance 纳入过拟合/DSR 硬项（H5-A，最小改动、最高收益）。
- H5.b DecisionGate/strategy_validation_pipeline 接线 S11（H5-B，复用离线脚本同款调用）。
- H5.c n_trials 真值注入链（TDM→plan→metrics，H5-C）。
- H5.d fail-open 可观测性统一（与 §H1-D/§H3-E 同一 metrics.degraded 字段）。
- H5.e 回测→实盘风险旗标契约（H5-E，跨治理车道）。

## 6 封矿判定

**未封矿**（本脉清晰但接线欠账多）。实证结论：S11 整装回测**唯一真正执行的风险刹车是
sanity_guard**（且容差宽到近乎无效）；overfitting_flag（现网 True）/DSR/DecisionGate/n_trials
**全部产而不消或默认关闭**，SIM-56"过拟合阻断上线"在生产是死配置（全仓 `strict_
overfitting_gate=True` 零命中）；回测风险旗标与实盘风控两轨不通。**未封子脉**：DecisionGate
三阶段接入的回归面、n_trials 真值来源（TDM 试错计数是否可得，联动评估车道）、跨轨旗标契约设计。
P0（H5-A）建议立即移交——它是"过拟合结果被当合格证据固化"的直接闸口，改动小、拦的面大。

## 修复优先级裁定建议

| 编号 | 一句话 | 级别 | 建议归属 |
|------|--------|------|----------|
| H5-A | overfitting=True 仍判 acceptance.ok，风险信号产而不消 | **P0** | 施工班（acceptance 加硬项，最小改动） |
| H5-B | DecisionGate/校验管线整套零接入 S11 | **P1** | 施工班 |
| H5-C | n_trials 违约，DSR 基数=拍脑袋 10 | **P1** | 施工班（联动 TDM） |
| H5-D | 4 处风险护栏 fail-open 不进验收 | **P1** | 施工班（可观测性） |
| H5-E | 回测风险旗标不跨到实盘准入 | **P1** | 治理+实盘车道 |
| H5-F | sanity 容差过宽 | **P2** | 排期 |

## 7 施工回填（H5-B + H5-D，session st-qoder-t1a-20260915，2026-09-17）

> 只记实测结论。开工前逐个 `git status --porcelain` 核实的既有未提交改动（含
> `src/zephyr/pf_core/strategy_engine/framework_composer.py`、`vectorized_engine.py`、
> `event_driven_engine.py`）均为他会话 WIP，本轮**未改一字**。

### 7.1 施工前事实核验（防按旧图施工）

| 清单条目 | 开工前实测 | 结论 |
|---|---|---|
| H5-A acceptance 读 overfitting_flag | `fw_backtest._evaluate_risk_decision` 已在 HEAD 调 `evaluate_strategy_risk_admission`，`acceptance.risk_admitted` 参与 `ok` | 已落地，本轮不重复施工 |
| H5-C n_trials 真值 | 产物 `metrics.n_trials_source="trial_ledger:4497"`（现网 bt-fw-823d7fd7） | 已落地（TrialLedger/MOD-BT-200） |
| H5-B 三段门控 | `DecisionGate.evaluate` 生产调用方仅 `strategy_validation_pipeline`（离线脚本独占）；引擎内 `evaluate_decision_gate` 全仓**只有 2 处 def、0 处调用** | 确为缺件，本轮施工 |
| H5-D fail-open 可见性 | 引擎侧 `PitUniverseProvider._degraded` / ST 腿 / `StkLimitProvider` / 冲击旁路均为私有态，`_engine_chain_diagnostics` 只上收 `last_signal_row_stats`+`last_skipped_fills` | 状态消费端不可达，本轮以出声归类落地（见 7.3 局限） |

### 7.2 H5-B：三段门控进 S11 验收（落点 `src/zephyr/strategy_pipeline/fw_backtest.py`）

- 判定器：`DecisionGate().evaluate(...)`（`_evaluate_staged_gate`，阈值零自造，全取
  `DecisionGateConfig` 默认；DSR 与风险闸同一数值，禁二次计算）。
- 证据口径（**关键裁定**）：S11 窗口内不再拟合参数（方案权重按 plan 指纹锁定），故三段
  证据取自**该次实测净值的时间切片**——IS=首段、WFA=其后各完整折（切分委托既有
  `WalkForwardAnalyzer(mode="expanding")`，零手写切片）、OOS=各折起点后全部后段；
  `scheme.caliber="locked_book_time_split"` 随证据包落档。真正的 fit-window IS 属 TDM 侧
  欠账（本文 §登记远期），此处不假造该数字。
- 样本下限取既有常量 `metrics.MIN_SAMPLES_FOR_SHARPE + 1 = 61`，需切出 IS + ≥2 完整折；
  切不出 → `evidence=None` + `passed=False`（fail-closed，禁"没测=通过"）。
- 结论进验收：`acceptance` 新增 `gate_passed/gate_can_deploy/gate_is_passed/gate_wfa_passed/
  gate_wfa_windows/gate_oos_passed/gate_oos_is_ratio/gate_has_disaster/gate_reasons`，
  `gate_passed` 参与 `ok` 与幂等闸要件（`_IDEMPOTENT_REQUIRED_ACCEPTANCE` 四键，与
  #24 H4-B 同族）；否决时 ERROR 告警带 `三段门控否决: IS=… WFA=…(x/y) OOS=…(ratio=…)`。
- 现网锚点复验（只读 `data/backtest_artifacts/bt-fw-823d7fd7.json`，净值 242 日）：
  风险闸 `accepted=False`（flag=True、DSR=1.69e-9、n_trials=4497/trial_ledger）+ 三段门控
  `passed=False, is_passed=False, oos_passed=False, oos_is_ratio=0.0, wfa_windows="0/0"`
  （IS 未过 → WFA/OOS 依"不可跳级"不评），reasons=
  `["Sharpe准入未通过: -2.3030 <= 0.5", "未提供参数敏感性数据,跳过稳定性门控", "IS阶段未通过,后续阶段跳过"]`，
  IS Sharpe=-2.3030、折 Sharpe=-2.00/-1.78、OOS Sharpe=-2.0525 → **双闸独立否决**。

### 7.3 H5-D：4 处 fail-open 护栏降级在消费侧计数（禁改引擎的替代方案）

- 机制：`_capture_guard_degradations()` 在 `run_framework_backtest` 执行期向
  `logging.getLogger("zephyr.backtest")` 挂 `_GuardDegradationCollector`（同进程、计数=
  当次真事件数，退出即摘钩还原级别；`emit()` 零抛，观测面不得反噬回测）。7 条正则逐条
  实测命中引擎既有出声（grep 验真）：

| guard | 命中源（实测 file:line） |
|---|---|
| pit_universe_filter | vectorized_engine.py:918（标的池过滤降级）/ :923（上市注册表为空） |
| pit_st_filter | vectorized_engine.py:867（PIT ST 判定失败）、matching_engine.py:1259/1267（ST 兜底降级） |
| impact_cost_model | matching_engine.py:809（冲击成本旁路）/ :876（冲击报价失败） |
| liquidity_participation_cap | vectorized_engine.py:288（成交量上限/冲击成本自动旁路） |
| participation_rate_sanity | matching_engine.py:864（冲击报价参与率越界） |
| stk_limit_bounds | matching_engine.py:998（预取失败）/ :1019、:1301（切片真源调用失败）/ :1082（涨跌停表行不可用） |
| fill_integrity | vectorized_engine.py:347（Fill skipped）/ :368（fill 被拒绝） |

- 落地字段：`acceptance.degraded_guard_n` + `acceptance.degraded_guards`，证据包
  `run.guard_degradation_ledger`（schema `degraded_guards/v1`，每条含 count/source/meaning/
  sample 日志原文截样），每条降级各自 WARN 一次。另记 3 条消费侧配置旁路
  （`regime_dynamic_overlay`/`pit_universe_window`/`stk_limit_provider`）与 2 条门控证据
  缺件（`is_param_plateau_gate`/`phase5_regime_gate`）→ watched 共 12 项。
- **不新增否决权**（本轮裁定：护栏降级是否升格为否决属 Owner 门位），且明确
  `count=0 ≠ 健康`（引擎改文案即退为 0=未听见），note 随账落档。
- 局限（如实登记，非"顺手修"范围）：引擎私有 `_degraded` 标志消费端不可达，出声归类是
  替代方案不是治本。治本需二选一——① `framework_composer._engine_chain_diagnostics`
  上收结构化降级计数；② 引擎侧落 `metrics.degraded_guards`。两文件均在本车道禁改清单
  （st-auditfix-20260916 在途），**移交后续车道**。

### 7.4 复验记录（全绿）

- 复杂度门（整文件，上限 15）：`fw_backtest.py` / `decision_gate.py` 一条命令输出**空**。
  顺带清偿存量违规：`run_fw_backtest_due` 原 cc=39 → 抽出
  `_idempotent_skip/_assemble_acceptance/_build_run_block/_acceptance_failure_note` 后达标。
- `python -m ruff check` 三改文件：All checks passed!（与 `git show HEAD:` 基线比零新增）。
- `python -m pytest tests/strategy_pipeline/test_fw_backtest.py -q` → **24 passed**
  （18 既有 + 6 新增：门控正路/时间退化否决/缺证据 fail-closed/幂等闸需 gate_passed/
  降级计数+WARN/账本不升格否决）；`tests/backtest/test_decision_gate.py -q` → **60 passed**。
  全程 tmp_path 隔离（journal/EVIDENCE_DIR/ARTIFACT_DIR 三向 monkeypatch），无生产目录写入。
- 现网证据包形状核验：最新 `fw-auto-20260916-005201-fe90e572.json` 的 acceptance 仅 4 键
  （无 risk_admitted/cash_closure_admitted/gate_passed）→ 产自接线前，按新幂等口径**不会**
  被短路，下轮自动重跑复评（这正是后加闸要求旧证据显式认账的目的）。


## 8 施工回填（T3④ 补：板块集中度进料治本 + 单一真源收编，session st-qoder-t1a-20260915，2026-09-17）

> 注：本节第一次撰写（约 07:40）被仓外 reconciler/pre-merge 整文件还原回 HEAD 后**重写**，
> 与 `repo-test-and-commit-quirks` 记录的"未提交车道成品被还原"同因；重写后随即入 index。

### 8.1 施工前事实核验（CH 只读 + AST，禁按记忆施工）

- **两套实现并行**：`overlay_features.compute_sector_metrics`（新）与
  `overlay_signals_builder._compute_sector_metrics` / `risk_signal_builder._compute_siphon_inputs`
  内各自手写 `unstack("code") → pct_change() → share → hhi`——同一数学两处落笔，其中
  risk_signal_builder 那条是风险信号 #8（板块虹吸）的生产喂数口。
- **进料伪值**：`sector_daily` 全样本 112,048 个 (日×板块) 单元里 ≈186 个单日涨跌幅绝对值
  >21%（A 股板块指数无此物理可能），集中在 ≈7 个坏板块码；这些单元把 HHI 顶成"全市场
  资金挤在一个板块"的假象。
- **前向填充造出假收益**：`pct_change()` 在 pandas 2.3.3 默认 `fill_method='pad'`，跨
  上报断档（实测 ≈3 处 >3 交易日空洞）会"用上周的价格算今天的收益"。

### 8.2 落地的三条口径（阈值数值一律未动 ⇒ 不触发预注册裁定）

| 口径 | 落点 | 语义 |
|---|---|---|
| 坏值剔除 | `SECTOR_DAILY_RET_ABS_MAX`（0.21 绝对界） | 超界单日收益置 NaN，不猜、不前向造 |
| 跨断档不造数 | `pct_change(fill_method=None)` | 断档日收益=NaN（诚实缺席） |
| 覆盖度门 | `MIN_SECTOR_UNIVERSE_SIZE`（板块数下限） | 低覆盖日整条 Sector_HHI/Top_Concentration/昨日Top3今日 置 NaN，并计数 `gated_days` 出声 |

单一真源：`compute_sector_metrics` 是唯一实现，builder 侧改为委托适配器（保留告警位与
返回形状），risk_signal_builder #8 同址委托——三处读同一函数，AST 级测试钉死"禁再出现
第二套 unstack/share**2"。

### 8.3 风险信号 #8（板块虹吸）的实际影响面

- 受影响日：#8 取 0.85 的 ≈6 日 + 取 0.60 的 ≈4 日，**全部**落在坏板块码当日（即伪值
  直接决定过冲档位）；剔除伪值后 sector_hhi 干净最大值 ≈0.0049，远低于最低档阶梯 ⇒
  #8 在整段样本上恒为基线 1.0（=不再被伪造数据触发）。
- 这不是"把风险信号关掉"，是**把喂给它的假数据停掉**：如果哪天板块真的虹吸，干净 HHI
  会真实上行并触发阶梯；触发口径（0.08/0.10/0.15）本轮未改。

### 8.4 复验记录

- 新增 11 条测试（`tests/regime/test_overlay_features.py::TestComputeSectorMetrics` 6 条 +
  `test_risk_signal_builder.py::TestParam8SectorHhiSingleSource` 4 条 +
  `test_overlay_signals_builder.py::test_t3_mainline_gated_below_coverage` 1 条），
  三处红蓝变异实证"测试会咬"：① 去掉坏值剔除 → hhi 从 ≈1/(N-1) 跳到虚高（RED）；
  ② 去掉 `fill_method=None` → 断档日造出假收益（RED）；③ 关掉覆盖度门 → 低覆盖日不再
  NaN（RED）。（首轮变异曾把 patch 打在 `Series.pct_change` 而生产调 `DataFrame.pct_change`，
  得到假绿——变异脚本本身要先证明能红，才算证据。）
- 台账棘轮：`tests/regime/test_overlay_features.py` 分隔符漂移名单已清空（`assert not non_canonical`）。
- 教训登记：**台账不承载实测明细**。首轮把 walk-forward 明细数字写进 ALERT 文案后，
  6 条契约测试同时炸（三段切分被明细里的 `|` 打断 / 未带 `≈` 的实测小数被当成"生产阈值
  常量"要求仍在宿主源码 / 门槛-命中率成对 claims 被拆散）。台账只写 状态 / 指针 / 处置，
  明细进报告文件。
- `tests/regime + tests/backtest + tests/pf_core + tests/strategy_pipeline` 第一轮
  **3529 passed / 1 failed**（失败项见 §8.5），第二轮全绿。

### 8.5 OVB-4 第五项 `s2_breadth_thrust` 闭环清偿（含一次归因纠错）

- 首轮把 `tests/regime/test_breadth_thrust_walkforward.py` 的红灯记成"他会话在途件"
  （R-SEC-3，并按 §3.4 不代修）——**归因错误**：该文件与被还原的报告脚本
  `scripts/regime_breadth_thrust_walkforward.py` 的 `[CONSUMERS]` 头都点名本车道
  st-qoder-t1a-20260915，预注册 JSON 也落在本会话 `.runtime/tmp/st-qoder-t1a-20260915/`。
  实情=本班 09-16 23:04 跑完的 s2 复推管线**只落了 harness，报告与台账回填没落盘**，
  其 ALERT 计数哨兵因此一直红。纠错纪律：**"未跟踪"≠"他会话"**，判归属要查头声明的
  车道 sid 与产物落点目录，不能只看 `git status` 的 `??`。
- 补账：报告 `breadth_thrust_walkforward_20260916.md`（全部数字由结果 JSON 程序化生成）+
  台账 `s2_breadth_thrust` 依据段回填实测（全样本 thrust 分位 p≈87 / washout p≈8.7、
  on_share≈0.126 超上界、跨折极差比≈6.96 超上限、训练段 4/4 可选值而样本外 2/4 过）+
  哨兵期望改为**现实值**（3 项 ALERT，本项仍 ALERT）。
- 裁定口径：**现值 0.615/0.40 保留、不采纳任何新值**（样本外未全折通过 ⇒ 采纳闸门关闭；
  换值才需要 Owner 门，不改值不需要）⇒ 无预注册口径变更，无新裁定。
- 残余（登记，非顺手修）：
  - **R-BT-1** 2005-2013 早期段广度进料（EQW_ALLA 补位）与该段 EMA 分布漂移未单独归因；
    重推须先补该段覆盖度证据，否则换阈值只是把"偏松"换成"偏紧"。
  - **R-BT-2** 网格 5×3 粗格、未覆盖 thrust<0.58；改滚动分位口径须另一次预注册（禁覆盖 v1 名）。
  - **R-SEC-1** 坏板块码在**供应商侧**（进料管道），本轮只在消费侧剔伪；上游治本属数据进料车道。
  - **R-SEC-2** Sector_HHI 阶梯与 #8 虹吸阈值的重标定受板块史长度限制（现 ≈188 天、
    剔伪可用 ≈126 天，门槛 ≥500 交易日），当前不可观测 ⇒ 不动数值。

---

## 9 施工回填（OVB-4 五项终态 + 本轮未施工两条的显式登记，2026-09-17）

### 9.1 OVB-4「阈值 A 股校准缺口」五项终态（台账 `THRESHOLD_CALIBRATION_LEDGER` 是真源，本表只是索引）

| 项 | 台账状态 | 本土 walk-forward 是否已跑 | 生产数值 | 实证出处 |
|---|---|---|---|---|
| `s2_breadth_thrust` | ALERT（语义已收窄） | 是（预注册 v1，hash 锁） | **未改**（thrust/washout 沿用现值） | `breadth_thrust_walkforward_20260916.md`；harness `scripts/regime_breadth_thrust_walkforward.py` + `tests/regime/test_breadth_thrust_walkforward.py` |
| `t3_money_effect` | ALERT（语义已收窄） | 是（68×6 候选点，1 个过带且无判别力） | **未改**（三档家数沿用） | `t3_threshold_walkforward_20260917.md` §5 |
| `t3_mainline` | ALERT（语义已收窄） | 是（放宽带下 12/12 仍全 FAIL） | **未改**（HHI 三档沿用） | 同上 §0/§6；坏码剔伪见 §8.3 |
| `s2_capitulation_confirm` | RESOLVED | 不适用（confirm 分支未接生产） | 无第二套实阈值 | §2#4 复核 + 签名默认值契约测试 |
| `s1_vix_panic_s2_vix` | RESOLVED | 不适用（分位秩归一已实证等价） | 无 | CH 实测 rank 分布近似均匀 |

**共同结论**：三项 ALERT 全部**已复推、均未过预注册接受带 ⇒ 按「不炸才用」闸门一律不改数值**。
改数值属 Owner 门，不改数值不触发裁定登记（RULE-RULING 只对"口径变更"生效）。ALERT 计数棘轮现
钉在 3 项（`test_ledger_alert_projection_count_does_not_backslide`），回升或误降都会红。台账证据段
已回填分时代新事实（"全历史命中"是混合时代均值、跨时代差≈54 倍）——**留着旧数字不放=明知有偏
差仍让下游继续当依据引用**，那才是台账失实。

### 9.2 本轮未施工的两条（H5-E / H5-F）——第一性原理分析 + 为何不自行落地

| ID | 分析（为什么不能顺手做） | 建议归属 | 可验收标准（下一班施工用） |
|---|---|---|---|
| **H5-E** 回测风险旗标 → 实盘 pre-trade（**R-H5E-1**） | 落点在 `risk_validation_bridge`＝在途下单链路，属宪章 §5 的 high 域 Owner 门（production 流转）。技术上契约已成形（回测产物 `metrics` 里的 `risk_admitted/overfitting_flag/dsr/gate_passed` 四键即准入输入，零新造字段），但"拒单 vs 显式豁免留痕"的失败语义一旦选错，代价是**真实资金被拦在门外或带病下单**——这不是代码难度问题而是门位问题，自行落地=越权 | Owner 定失败语义 → 治理+实盘车道施工 | 被回测判 `risk_admitted=False` 的策略过 pre-trade 必拒（或走带审批人的豁免并落审计行）；豁免项在仪表盘可见；"旗标缺省=None"不得当作通过（fail-closed 测试覆盖） |
| **H5-F** sanity 容差过宽（**R-H5F-1**） | 收紧数值本身是**回测验收口径变更**（现网已固化的 `bt-fw-*` 产物可能从"合格"翻成"不合格"），而 §7.4 已证旧证据包会被新幂等闸要求重跑复评——两件事叠加＝触发一轮全量重跑，属排期决策而非补件。且引擎两文件（`vectorized_engine.py`/`event_driven_engine.py`）经 §7.1 核实为车道 A 在途件，HELD-OVERLAP 不硬闯 | 排期（与车道 A 落地合并做） | 改为相对基准/换手分层的合理性判据；极端但落在旧宽区间内的失真须有二次拦截并落 `metrics.degraded_guard` 同族字段 |

### 9.3 工作区清退事故（本轮第二次，观测面缺口已并入 reconciler 脉 RC-15）

`framework_composer.py` 的 #24 执行链接线（`cash_curve` + 五键 metrics + `chain` warn）与
CloneGuard 治本改动，在未提交状态下**两次**被整文件还原到 HEAD（2026-09-16 一次、本轮
2026-09-17 一次），事后由 `tests/backtest/test_h3h4_cash_pit_exec_chain.py` 报红才被发现；
恢复途径＝编辑器 file-history 快照（字节级，sha `6e5b9c0e309bb7b2`），**不是** git 对象库
（内容从未 commit，git 里没有）。**这是"清退无观测面"**：还原动作不落审计行、不进 stash、
不通知当事人，只留下一堆自红测试——本轮实测核实：现存 4 个 stash（`stash@{0..3}`，含
`session_worktree_pre_merge` 两件）内的 `framework_composer.py` 版本 `cash_ledger_reconciliation`
命中数一律为 0 ⇒ 我的内容**在任何 git 可恢复对象里都不存在**，file-history 是唯一救生索。
登记位点与验收标准见
`reconciler_event_trigger_chain_mining.md` §4 **RC-15**。本轮实测教训：未提交的工作区内容
在本仓**不是安全位置**——改完立刻 `git add`，跨轮次保留的中间产物必须出仓到 `docs/_working/`
或走队列落地，不信"我改过它就还在"。

**同轮第三次（2026-09-17 08:2x，只清暂存层）**：11 个 lane 文件的**工作区内容完好**，但
`git diff --cached HEAD` 对 `framework_composer.py`/`overlay_features.py`/本文三文件已归零
（index 被打回 HEAD），同时 `.ailocks/registry.json` 里自家 11 条 claim 的 `ttl_left` 全为
**−3 分钟**（claim TTL 30min < 跨轮次实际间隔）。⇒ 上一段"改完立刻 git add"的结论**只覆盖了
工作区层**：`git add` 后仍可能被整批 unstage，且它发生时不会有任何提示（与 RC-15 同一观测面
缺口，只是打击面从工作区缩到 index）。修正后的收尾不变式：**commit 前三步一起做**——重新
`acquire-batch`（过期 claim 会 RECLAIMED，不报错但必须看到）→ `git add --pathspec-from-file`
→ `git diff --cached --stat HEAD` 逐文件核对插入数与预期一致，任一为空即视为事故重演，禁裸提交。
