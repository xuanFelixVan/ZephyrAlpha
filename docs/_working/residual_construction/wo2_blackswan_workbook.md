---
ttl: task_bound
title: WO-2 黑天鹅三件挖干作业簿 v1——危机态三级接线/对冲腿纸面闭环/月度演练
owner: ZephyrAlpha-Owner
session: st-residual-20260917
date: 2026-09-17
status: mining_b1
---

# WO-2 黑天鹅三件 · 挖干作业簿

> **真源**：[pending_items_plan.md](pending_items_plan.md) WORK-ORDER-2。本作业簿=施工前置挖干产物（mining_sop 六向寻路+自审闸），B1 批全部落点带 `路径:行号` 实底，接单会话按此施工免再勘察。

## 0. 挖矿日志（批次 B1）

- 母节点：黑天鹅三件（2a 危机态接线 / 2b 对冲腿 / 2c 演练机制）。
- B1 内部动作=两个并行深度勘察：接线链 8 问 + 风控栈/期货 7 问，全部有 `路径:行号` 实底。
- 外网动作：**本批未出网**（按 SOP 如实记长尾 M-1，非"查无"）。

## 1. 六向台账

### ①上游（还该喂什么进来）

- regime_snapshot_history 7 维概率在产：唯一写方 `scripts/backtest/print_regime_history.py:59`，自动化供给 `pipeline_events.maybe_refresh_regime_snapshot:687-743` → `fw_backtest.ensure_regime_snapshot:1110-1140`（stale≤3 天直通）。
- **G1 危机口径偏窄**：现行 `is_crisis = dominant == r10`（`allocation_inputs.py:523`）。r10 概率高但非 dominant 不触发——恐慌预兆（p_r10=0.5+）不算危机。→ **裁定 D1**：双档口径，`crisis = dominant==r10`（硬拦截）；`warning = p_r10 ≥ θ`（缩额+告警）。θ 初值 0.5，月度演练回看校准 → 开放问题 O1。
- **G2 盘中盲区**：regime 快照日频，盘中闪崩感知不到。**显式不在本批**（挂 WO-5 三期/盘中 L1），防范围膨胀。
- **G3 两套熔断未打通**：模拟盘链 `pipeline_events.kill_switch_clear:151-163` 读的是 Agent 行为风控探针（`security/access_control/kill_switch.py` **纯进程内存单例**，进程崩即归零，docstring 明令禁用于交易资金）；交易真源=`DefaultRiskValidator` JsonStateStore（`data/runtime/state` 持久 JSON，损坏 Fail-Closed 按已熔断，`default_risk_validator.py:156-166`）。→ **裁定 D2**：本闸的危机判定**不新建任何内存态**——每晨从 CH regime 表现读（天然持久），crisis 判定行落 `crisis_gate_log` 表；现有进程内存探针保持"行为熔断"职责不变，不挪用。

### ②下游（输出喂给谁）——三级拦截落点（B1 已探明）

| 级 | 落点 | 语义 | 侵入度 |
|---|---|---|---|
| L1 管线级 | `pipeline_events.run_pf_alloc_daily` :481/:482 之间 | dominant==r10 → alert + `return {"skipped":"crisis_block"}`，**不落 marker**（解除后同日可重放） | 拦"额度重算" |
| L2 裁决级 | `allocation_orchestrator._strategy_layer` :450-481 | 仿 `TIER1_FREEZE_NEW_POSITIONS`（:454-461 先例）读 `facts.is_crisis`（字段 :397/:866 **已备、零消费**——现成闲置 hook） | 拦"新开仓、不动存量" |
| L3 账本级 | `sim_paper_ledger.py` :104 entry 分支前 | 按日 blocked 判断：entry→cash，持有/强平逻辑不动 | 拦"账本自洽" |

- **裁定 D3**：三级一次全上，职责不同不可互替（L1 保系统、L2 保语义、L3 保账本），每级各自告警出声。
- 同构先例（直接抄写法）：`CalendarPositionConstraint` 经 `_dynamic_layer` 的 `CALENDAR_BLOCK_NEW`（allocation_orchestrator :503-524）="今日禁开仓"唯一已接线先例。
- 顺带激活：`RegimeMetaAllocator.CRISIS_SHRINKAGE_FLOOR=0.05`（regime_meta_allocator.py:109/:417，自注当前参数域**数学不可达**）——warning 档接通后变为可达。

### ③算法/机制

- 内部已有件：`stress_test_engine`（MOD-RK-12 production，预置 2015 股灾/2020 疫情 shock + REVERSE + CONTAGION）；`liquidity_crisis_scenarios`（MOD-RK-047 testing，4 情景族，**产而不消**——演练机制顺带治它）；`black_swan_pattern_library`（MOD-RK-14）；`hedge_execution_skill`（MOD-RK-042：IF/IC/IM 词表+乘数+腿单生成+human_gated 双确认，**零消费**）。
- 外网：长尾 **M-1**——机构危机 de-risking 状态机（CPPI/波动率目标/回撤阶梯）参数惯例，需 URL 引文后入图。

### ④后端（代码缺什么）

- 缺三件：①crisis 判读件（薄查询：业务日+最新快照→normal/warning/crisis 三元组，挂 `allocation_inputs.load_regime_input` 旁）②三级拦截代码（落点已探明，零新架构）③`crisis_gate_log` 留痕表（DDL 走 schemas/categories 真源）。
- 期货执行：**全仓下单路径为零**——broker 仅 stock/etf/convertible（`miniqmt_broker.py`）/okx；ex_sor 的 CTP 只是路由评分枚举。→ 2b 本期只做纸面闭环，真实通道显式挂起（见 §3）。

### ⑤前端（只登记不施工）

- `dashboard_feeds` 已消费 `tail_risk_monitor`——crisis 状态卡片可挂同路；task_board 告警面现成。登记，不在本批施工。

### ⑥数据字段

- regime 表列齐：p_r1..r4/r10..r12/dominant/confidence/shrinkage（DDL 真源 `schemas/categories/regime_snapshot_history.py:42-66`）。
- 期货定价源：`c1_market.kline_futures`（IF0/IC0/IM0/IH0 日线全量）+ `c1_market.futures_kline_qmt`（forming bar 5 分钟滚动、日线粒度）——纸面腿定价够用。
- **F1 字段风险**：`futures_kline_qmt` 是 forming 幂等表，纸面腿结算价**必须取当日定格收盘行**，禁用 forming 中间态（施工时 SQL 口径写死）。
- 长尾 **M-2**：期货分钟线（真实执行层需要时再接）。

## 2. 设计裁定（2a 状态机）

- 状态：`normal` / `warning`（p_r10≥θ，θ 待 O1）/ `crisis`（dominant==r10）。
- **动作矩阵**：
  - crisis → L1 管线短路（额度冻结）+ L2 冻结新开仓 + L3 entry→cash；**存量持仓按既有规则自然退出，不强平**（危机中强平=卖在地板上，强平语义归 ex_core 既有回撤阶梯，不归本闸）。
  - warning → 全链照跑 + shrinkage floor 0.05 激活 + 告警出声。
- 持久化：每日判定行入 `c1_backtest.crisis_gate_log`（**裁定 D4**：新表，字段 trade_date/state/p_r10/dominant/action_l1/l2/l3/probe_ts，MergeTree 只增不改）。
- 解除：dominant!=r10 次晨自动解除重放，仅告警不人工。
- **O1（Owner 裁定点）**：warning 阈值 θ（建议 0.5 起步）；是否加"连续 N 日 warning 升 crisis"加速条款（建议暂不加，等演练数据）。

## 3. WO-2b 对冲腿（纸面闭环）

- 现状：`hedge_execution_skill` 能生成腿单（sell 方向、乘数、双确认）但零消费；期货 broker 为零。
- 纸面闭环：crisis 确认日 → skill 生成腿单 → 纸面撮合以 `futures_kline_qmt` 定格日线价虚拟成交（口径守 F1）→ 虚拟对冲 PnL 记账 → 危机解除平腿 → 全程留痕。
- **裁定 D5**：触发=crisis 确认日（不用 warning，避免频繁开平腿被贴水磨损）；对冲比例=组合 beta×0.5 起步（参数进 crisis 配置）。
- **真实执行通道显式不在本批**：需 CTP/QMT 期货账户+实盘门位（Owner high gate）。解锁条件=纸面闭环跑满 ≥3 次演练 + Owner 批准。合约选择 **O2**：组合以中小盘为主→IM beta 最贴但贴水最贵，建议 IM 起步、月度考基差成本。

## 4. WO-2c 演练机制

- 现状：无"历史区间+当前持仓"一键重放件；可拼=`run_framework_backtest(plan_id, symbols, start, end)`（窗口显式参数，`framework_composer.py:2742-2770`）+ `stress_test_engine`（预置 shock 向量）。
- 设计：`crisis_drill_monthly.py`——①取当前纸面组合持仓 ②跑 4 预置历史窗（2015-06~09 千股跌停 / 2018-03~10 贸易战 / 2020-02 疫情 / 2024-01~02 微盘崩盘）③出伤亡报告（MaxDD/是否触破产地板/恢复天数/对冲腿贡献）④落 task_board。
- 调度：**沿用月频既定模式**（全仓无月频计划任务先例）=每日调度唤醒 + `MONTHLY_DAYS=30` marker 门控（pipeline_events 月频 kind 已有先例 :146-147/:229-249）。
- 顺带收益：`liquidity_crisis_scenarios` 4 情景族在演练中被消费（治"产而不消"）。

## 5. 施工顺序与前置

1. **2a 三级拦截**（约 1 会话）：crisis 判读件 + L1/L2/L3 + crisis_gate_log 表 + 告警。依赖：无（regime 链已在跑）。前置：RULE-DEPGRAPH 登记 design node、capability_lookup。
2. **2c 演练**（约 1 会话）：与 2a 无强依赖，可并行。
3. **2b 纸面对冲腿**（1-2 会话）：依赖 2a 状态机做触发源。

## 6. 验收标准（接电留痕，不以代码写完为准）

- **2a**：①注入/伪造 crisis 快照 → 次晨 L1 短路 + L2 冻结新开仓 + L3 entry→cash 三级全触发且 `crisis_gate_log` 留痕；②危机解除次晨自动恢复、被短路当日可重放成功；③无快照日 fail-closed 平坦分布**不**误触发。
- **2b**：纸面环境完成一次"crisis→开腿→解除→平腿"全流程，虚拟 PnL 与 `futures_kline_qmt` 定格价对得上账。
- **2c**：首份月度演练报告落 task_board，含 4 历史窗伤亡表。

## 7. 长尾矿脉清单（未挖，登记续挖）

- **M-1**：机构危机 de-risking 状态机业界参数（外网引文补）。
- **M-2**：期货分钟线接入（真实执行层立项时）。
- **M-3**：盘中实时危机感知（挂 WO-5 三期/盘中 L1）。
- **M-4**：期权对冲腿（50/300/500 ETF 期权保险）。
- **M-5**：`liquidity_crisis_scenarios` 情景参数校准（演练首份报告后回看）。

## 8. 挖后自审闸（三态裁定）

- **北极星校准**：三件全消灭"Owner 肉眼盯盘做危机决策"的人工环节 → 向终局全貌推进。
- **过度工程三问**：①收益实算=危机响应延迟是资金安全一等风险，接线消灭它；②已有产物覆盖=否——现状是"建而未接"（CRISIS floor 数学不可达、对冲腿零消费、情景族产而不消），本工单本质是**接线**不是新建；③成本实算=3-4 会话，产能占比可控。
- **裁定：施工**（2a/2c 先行，2b 纸面随后；真实期货通道挂起，解锁条件见 §3）。
- **红蓝登记**：本稿为单方挖干，未经对抗轮。预登记红队矿脉：**regime 检测器无外审档案，crisis 误报一次=全链冻结一天的代价**——缓解=warning/crisis 双档（warning 只缩额不冻结）+ 月度演练回看误报率。
