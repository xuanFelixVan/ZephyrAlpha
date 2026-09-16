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
