---
campaign: matrix-20261006
lane: E-exam-w2
ttl: task_bound
---

# codesym_strategy_exam_v1 — D道 M-8 wave2 策略 code_path 考试分数册（伴读）

- 生成：2026-10-06 12:26:46.605783+00:00｜对象=23 个 code_path（注册册 code_path 非空全量）
- 分类计数：A=8 B=14 C=1 D=0；measured=10 error=3 rework(不跑)=10
- 判定（实跑 10 只）：pass=0 retire_candidate=7 rework=16（判据=PREREG_V1.strategy_pass_line：OOS Sharpe>0 / IS>0 / OOS MDD≤30%）

## 实跑明细（IS=2018-01-02..2025-09-30｜OOS=2025-10-09..2026-09-30｜引擎缺省装置）

| strategy_id | verdict | IS Sharpe | OOS Sharpe | OOS MDD | 备注 |
|---|---|---|---|---|---|
| STR-MOMTREND-002 | retire_candidate | -1.784 | -3.061 | -0.055 |  |
| STR-VREV-001 | retire_candidate | -0.923 | -0.441 | -0.073 |  |
| STR-VREV-002 | retire_candidate | -0.296 | -2.576 | -0.131 |  |
| STR-MOMTREND-019 | retire_candidate | -0.640 | -2.211 | -0.271 |  |
| STR-VAL-001 | rework | 0.588 | -0.080 | -0.376 | 同上估值覆盖稀释 |
| STR-VREV-026 | retire_candidate | -1.187 | -2.276 | -0.103 |  |
| STR-VREV-027 | retire_candidate | -0.938 | -0.106 | -0.220 |  |
| STR-MULTIFACTOR-097 | retire_candidate | -1.605 | -0.134 | -0.018 | 符号归一 shim 重考（symbol_canonical→裸6位，纯格式映射） |
| STR-MULTIFACTOR-098 | rework | 0.052 | -0.042 | -0.396 | 同上估值覆盖稀释 |
| STR-MULTIFACTOR-099 | rework | 0.458 | -1.259 | -0.470 | 同上估值覆盖稀释 |

## 引擎 error（如实记）

- STR-TSMALL-001: engine_error: ImplausibleBacktestError: 回测合理性护栏拦截 (result_id=bt-bb973775): total_return=3.0284 超过合理上限 +300%（前视/无限流动性失真嫌疑）
- STR-DABAN-023: engine_error: ImplausibleBacktestError: 回测合理性护栏拦截 (result_id=bt-f05b6263): total_return=-0.9936 低于合理下限 -95%（无杠杆 long-only 不可能）
- STR-MOMTREND-033: engine_error: ImplausibleBacktestError: 回测合理性护栏拦截 (result_id=bt-3c45feb0): trades_count=0 空跑（信号/撮合/配置失真嫌疑；确需空跑对照请 allow_empty_trades=True）

## rework 适配工单（不跑不凑数）

- **STR-VREV-025**（B类，build）：指数/ETF 执行通道缺失：策略标的为指数（kline_index），标准装置 flat 仅股票（kline_daily_hfq）；且指数码与股票码同空间碰撞（000001=上证指数/平安银行、000852=中证1000/石化机械）直接喂引擎=假测错标的。工单：装置增指数/ETF 价格腿（kline_index/kline_etf_daily）+同码碰撞防护闸
- **STR-MULTIFACTOR-069**（A类，VWAPReversionStrategy.on_tick / IntradaySurgeFallStrategy.on_tick -> {symbol:weight}）：tick/盘口数据装置缺口：tick_depth_5 仅 2026-07-24..2026-09-30、tick_data 仅 2026-01-05..2026-09-30，OOS（2025-10-09 起）前段无数据；且标准装置=日频 DefaultBacktestEngine 无法表达 on_tick 级 T+0 round-trip。工单：①回补 2025-10-08..2026-01-04 tick+5档盘口；②建 EDE tick 考试道（tick_replay+matching_logic），禁止在日线装置凑数
- **STR-VREV-017**（A类，IntradaySurgeFallStrategy.on_tick）：tick/盘口数据装置缺口：tick_depth_5 仅 2026-07-24..2026-09-30、tick_data 仅 2026-01-05..2026-09-30，OOS（2025-10-09 起）前段无数据；且标准装置=日频 DefaultBacktestEngine 无法表达 on_tick 级 T+0 round-trip。工单：①回补 2025-10-08..2026-01-04 tick+5档盘口；②建 EDE tick 考试道（tick_replay+matching_logic），禁止在日线装置凑数
- **STR-VREV-018**（A类，VWAPReversionStrategy.on_tick）：tick/盘口数据装置缺口：tick_depth_5 仅 2026-07-24..2026-09-30、tick_data 仅 2026-01-05..2026-09-30，OOS（2025-10-09 起）前段无数据；且标准装置=日频 DefaultBacktestEngine 无法表达 on_tick 级 T+0 round-trip。工单：①回补 2025-10-08..2026-01-04 tick+5档盘口；②建 EDE tick 考试道（tick_replay+matching_logic），禁止在日线装置凑数
- **STR-VREV-019**（A类，VWAPReversionStrategy.on_tick）：tick/盘口数据装置缺口：tick_depth_5 仅 2026-07-24..2026-09-30、tick_data 仅 2026-01-05..2026-09-30，OOS（2025-10-09 起）前段无数据；且标准装置=日频 DefaultBacktestEngine 无法表达 on_tick 级 T+0 round-trip。工单：①回补 2025-10-08..2026-01-04 tick+5档盘口；②建 EDE tick 考试道（tick_replay+matching_logic），禁止在日线装置凑数
- **STR-VREV-024**（A类，OrderBookImbalanceStrategy.on_tick）：tick/盘口数据装置缺口：tick_depth_5 仅 2026-07-24..2026-09-30、tick_data 仅 2026-01-05..2026-09-30，OOS（2025-10-09 起）前段无数据；且标准装置=日频 DefaultBacktestEngine 无法表达 on_tick 级 T+0 round-trip。工单：①回补 2025-10-08..2026-01-04 tick+5档盘口；②建 EDE tick 考试道（tick_replay+matching_logic），禁止在日线装置凑数
- **STR-DABAN-022**（A类，DabanSleeveStrategy.generate_target_weights / build_weight_panel_for_dates（lane A 已消费））：决策负载表 c1_market.daban_engine_load 仅 1651 行（2026-09-01..09-28），OOS 几乎全窗无数据。接口现成（build_weight_panel_for_dates 即权重面板出口）；工单=daban_load_producer 历史回补至 2025-10 前后即可考
- **STR-MULTIFACTOR-096**（A类，MultifactorSleeveStrategy.generate_target_weights(universe,signals,constraints)->dict）：无因子输入契约：册内 alpha_sources=[]、factor_dependencies=[]——喂什么截面=私货（禁）。工单=册内登记该 sleeve 消费的 factor_id 清单+ic_weights 离线产出约定（compute_ic_weights 已备），即可按月频截面注粮接入标准装置
- **STR-EVENT-001**（A类，EventDrivenSleeveStrategy.generate_target_weights(universe,signals,constraints)->dict）：依赖 event_score（[MATURITY] design，事件链 NLP 管道未闭环 #ARCH-NLP-PIPELINE-001）+EventRecord/分钟级异动确认输入；无历史事件数据供给。工单=事件数据管道闭环+历史事件回填后方可考
- **STR-E-TIMING-001**（C类，main()/run_quantile_walkforward（产出 q05/q50/q95 分布预测，非权重面板））：分布预测→仓位映射层缺失（q05/q50/q95 无交易语义）；且预测标的=000300 指数，同指数/ETF 执行通道缺口。工单=定义分布→持仓规则（如 q05 分位择时阈值）+指数/ETF 执行腿，映射层属新增逻辑须 Owner 过目

## 语义与边界（诚实披露）

- 引擎满仓归一：非零行 Σ→1；全零行=不下单维持持仓≠清仓（现金意图需 ShrinkageBacktestEngine——适配工单）。
- translated build 内部 shift(1) PIT + 引擎 T+1 = 双重保守滞后，批内统一可比。
- 估值/财务输入 2020-01 起覆盖：STR-TSMALL-001/STR-VAL-001/STR-MULTIFACTOR-098/STR-MULTIFACTOR-099 的 IS 前段无信号。
- 知识生效日：translated 件哨兵（2026-09/10）晚于考试窗=D120 声明制 drift，放行+披露（yaml 逐条 knowledge_drift）。
- 本批零既有文件改动；D 类（实盘连接）实测为零——tick 组归 A+rework（数据装置缺口非 QMT 连接）。
