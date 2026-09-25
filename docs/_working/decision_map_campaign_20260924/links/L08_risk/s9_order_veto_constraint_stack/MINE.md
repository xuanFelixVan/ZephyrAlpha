---
ttl: task_bound
title: RSK-9 MINE
---

# RSK-9 逐单否决与组合约束栈 — 深挖簿

> 车道 L08 风控 · 子块 9 · 班次 st-qmine-20260925 · 只读挖掘。
> 起点真源=`../SKEL.md` §2 RSK-9。本簿主产出=**逐单硬否决链的实接电证明 + 约束栈四件的"码在盘、无 import"逐件判定 + 单仓上限三口径冲突**。

## ① 职责一句话

下单前把每一笔委托过一遍**硬否决**（数据完整性→交易约束→限额，全量不短路、异常即否决），并让组合级约束栈（集中度/相关性/风险预算/资金曲线）把"能不能下、下多少"合成成单一仓位上限。

## ② 现状实测（生产触发面判定：**否决引擎已接电（且是"缺省自造"式强接电）；组合约束栈四件中仅 sizing 链在产，F-C2 三件零 import；P-P1-04 零消费**）

| 件 | 实码 | 生产触发面实测 |
|---|---|---|
| `risk/core/risk_veto_engine.py`（MOD-RK-24） | 七条内置硬规则（`:23-31` 全清单）：P10 MISSING_PRICE（双向否决）、P15 LIMITS_UNAVAILABLE（**BUY 否决 / SELL 减仓放行——风险收敛不拦**）、P20 SUSPENDED、P30 SELL_EXCEEDS_POSITION（无裸卖空 B-018）、P35 T1_SELLABLE_EXCEEDED（**sellable 无真源时跳过不臆测**）、P40 SINGLE_POSITION_LIMIT（CTR-003 L1，含 `symbol_overrides`）、P50 GROSS_LEVERAGE_LIMIT；优先级常量 `:128-134`；契约 `OrderRiskRequest:77-85`（`price=None`=市价单按快照估算、`request_id` 默认 uuid）、`VetoVerdict:89-96`、`VetoDecision:100-108`（`approved/vetoes/rules_evaluated/snapshot_id/request_id/evaluated_at`）；`VetoRule` Protocol OCP 扩展点 `:111-121`；`build_default_veto_rules():320`、`evaluate_vetoes():351-374`（`rules=None` 即取默认七条）；**规则异常统一转 RULE_ERROR 否决（Fail-Closed，`:32` "§6 可用性 vs 安全性→安全性优先"）** | **已接电**：`ex_core/pre_execution_checker.py:47-49` import、`:204` 形参、**`:225 self._veto_engine = veto_engine or RiskVetoEngine()`（缺省自构造=只要闸门挂上，七检必跑，不依赖注入是否齐全）**；`ex_core/trading_session.py:116` import `OrderRiskRequest, RiskVetoEngine`、`:516` attach 形参；生产装配=`scripts/start_paper_session.py:565 attach_pre_execution_gate(...)`（同函数已实证挂上熔断探针）→ **闸门 4 在 paper 链在产**（13 号文环节⑤"熔断→逐单拒单=通"的逐单侧本轮独立复证） |
| `position/core/firm_risk_aggregator.py`（MOD-POS-021，F-C2-02） | 含 kelly 相关实现（`grep` 命中本文件）；ERROR_CONTRACT `:13` 自述"**专用异常类未落位（现实现 ValueError 兜底）**；AggregationError/ConstraintViolationError 设计预留——ZA-POS-0021/0023 已被 position_risk_budget_allocator/intraday_position_constraint 注册占用，落位需 Owner 重分配号段" | **覆盖未接电（但被宣称为执行者）**：src/scripts 内唯一实际调用=`strategy_pipeline/daily_gate_snapshot.py:345-354`（新建实例只为读 `risk_limits` 键存在性，状态仍写 `"status":"absent","error":"not_wired_v1"`）；而 `plan_engine/tomorrow_boundary_planner.py:106` 与前端 `warroom.html:284`、`position.html:209` 三处都宣称"单票 ≤8% 总资产=**firm 层 FirmRiskAggregator 硬顶**（30 号 §2.2）"→ **宣称的执行者从未被执行**（L08-C54） |
| `position/core/correlation_regime_monitor.py`（MOD-POS-012，F-C2-03） | 60 日 PnL 相关矩阵 + 层次聚类（ρ>0.70 合并 / >0.85 禁新仓 / cluster≤5%）+ covariance_estimator Ledoit-Wolf | **零 import**：全 src/scripts grep `CorrelationRegimeMonitor\|correlation_regime_monitor` 仅命中自身模块头（`:2,:14,:34` ALGO_FLOW 外部件）与自家测试 `tests/position/test_correlation_regime_monitor.py` → 相关性约束在逐单/组合链上**不生效** |
| `position/core/budget_change_handler.py`（MOD-POS-022，F-C2-04） | 三级响应（<10% 封锁新仓 / 10-25% 差异化窗口 / >25% 按比例强裁，yaml `:3917-3948`）；`:551` "G15→G14 **接线就绪入口**适配（33 号 §7 新发现 3：BudgetChanged 事件链）"、`:597` "**生产调用方接线入口**"；错误码 `ZA-POS-0040` `:102` | **零 import**：grep `BudgetChangeHandler\|budget_change_handler` 仅命中自身定义 + 自家测试 + `pf_alloc/core/regime_meta_allocator.py:5` 的 **[CONSUMERS] 声明**（"MOD-POS-022 收 BudgetChanged 事件"）→ **自我声明"接线就绪"但全仓无调用者**（事件链未产：`BudgetChanged` 事件在本仓无生产者，与骨架一致）。**下游表已有写函数**：`pf_alloc/allocation_persistence.py:152 write_rows(alloc_budget_change_log.TABLE_NAME, …)`，表 DDL=`scripts/ch/apply_pf_alloc_ddl.py:30`（"budget 变动裁决与三级升级事件流水 E-POS-40/41"）→ 写路径存在、其调用方未复证（L08-C57） |
| `position/core/position_sizing_engine.py`（半 Kelly） | INVARIANTS `:8`：`w_kelly <= 0.5*f*`（半 Kelly 硬上限）、**参与率>15% 的标的不得出现在 PositionSizingPlan（否决非截断）**、`total_exposure <= min(市场状态上限, 风控上限, 资金曲线上限, 日历约束上限)`、应急模式单标的≤10%/总仓位≤30%、降级必须 `degraded=true`、`idempotency_key` 防重复；`half_kelly_factor=0.5 :166`（校验 `:193-194`）、`_compute_kelly_fraction(p,b) :357`（f\*=(bp−q)/b）、降级路径 `SIZING_BASIS_DEGRADED="degraded_equal_weight" :130`（Kelly 缺失→等权而非满仓） | **在产**：sizing 链被消费（`strategy_book.py:4`、`drawdown_consecutive_loss→cap_multiplier` 声明、`capital_curve_manager` 依赖链，见 RSK-4）；**`:8` 的四路 `min(...)` 是仓内既有的"保守者胜"合成先例**——L08-C01/TRD-A13 仲裁序应以此为立法模板而非新造机制（与 `risk_layer_orchestrator.py:74-85` 破产底线"最严口径"同构） |
| `risk/core/ashare_stop_loss_engine.py`（MOD-RK-09，P-P1-04） | 四类否决线（生死线 -7% / 时间止损 / 财报解禁禁区 / 板块退潮，yaml `:2735-2760`） | **零消费（本簿独立复证）**：全 src/scripts grep 仅命中 `tests/risk/test_ashare_stop_loss_engine.py`（38 测试的家）→ 骨架"零生产消费"成立。**附带发现**：真实类名=`AshareStopLossRuleEngine`（非 `AshareStopLossEngine`），施工/检索须按类名而非骨架别名 |

## ③ 六向台账

| 向 | 台账 |
|---|---|
| 上游 | `RiskSnapshot`（MOD-RK-25 统一风控快照，经 `risk_data_pipeline`，由 `trading_session.build_risk_snapshot():465-479` 四路真源装配：持仓 broker/行情 price_provider/成交 fill 回报/限额 config 原值透传，**按调仓批次装配一次**）+ `OrderRiskRequest`；全图 sleeve 目标仓位/intent 隐式订阅（yaml `:3843` M-12）；`BudgetChanged` 事件（**无生产者**）；组合约束栈输入=60 日 PnL 矩阵 + Ledoit-Wolf 协方差 |
| 下游 | `PreExecutionReport` 四级闸（闸门 1 熔断探针/1.5 会话窗/闸门 3 快照/闸门 4 否决，`:193-206`，闸门 1+1.5 fail-closed）→ MOD-EX-024 硬拦 + MOD-L06-001；`sizing` 计划→订单；`tomorrow_boundary_planner`（边界计划引用 firm 8% 口径）；候选池 `vetoed/veto_reasons` 标记（RSK-8）；`warroom/position` 页面展示越限计数（**自述"演示口径"**） |
| 算法/机制 | 全量评估不短路（理由可审计）；优先级序=数据完整性<交易约束<限额（`:114`）；非对称否决（P15 只拦 BUY、放行减仓=风险收敛方向不拦，与 RSK-8 信号侧"证据不足不否决"构成**两套非对称哲学**，L08-C50 已记）；RULE_ERROR=否决（fail-closed）；T+1 无真源→**跳过**（P35，唯一"无真源即放行"的规则，A 股 T+1 是硬约束，此为最弱一环 L08-C56）；半 Kelly 截断；ρ 双档（0.70/0.85）；预算三级强裁 |
| 后端 | 纯函数判定核心（引擎只编排、无 IO）；`snapshot_id/request_id` 双键幂等可追溯；OCP 规则注入（`RiskVetoEngine(rules=[...])`）；错误码号段冲突（ZA-POS-0020/0021/0022/0023 被占，导致专用异常类无法落位 → **约束违例以 `ValueError` 抛出，调用方难以分型处置** L08-C55）；表侧 `alloc_budget_change_log`/`alloc_budget_daily`/`alloc_shrinkage_daily` 三册真源在 `allocation_persistence.py:56-77` |
| 前端 | `warroom.html:284` 单笔硬约束行、`position.html:209` 口径注（单票 8% 建仓口径"涨超不计越限"、偏离带 ±5pp、行业集中度 25%、**"越限 0 次/近 5 日（演示口径）"**）、`reglib/reg-engine.js:166` RC-005 解禁高峰窗口规则卡；**面板"越限 0 次"与执行链实际否决计数无数据通路**（无物化表 → L08-C06 的直接用户侧后果） |
| 数据字段 | `OrderRiskRequest`（symbol/side/quantity/price/strategy_id/request_id）、`VetoDecision`（approved/vetoes/rules_evaluated/snapshot_id/evaluated_at）、`RiskSnapshot` 限额原值透传、`PositionSizingPlan`（含 `idempotency_key`/`degraded`/basis 枚举 `kelly_budget`/`degraded_equal_weight`）、`alloc_budget_change_log` 事件流水列；**缺**：否决事件不落库（`VetoDecision` 只在内存/日志，无历史可复盘 → 无法算"否决率/误否率"）、单仓上限三口径未真源化（8% firm / 20% P40 CTR-003 / 25% sleeve `max_single_sleeve`）、相关性约束无字段输出 |

## ④ 缺口清单（本层新增）

| # | 缺口 | 证据 | 判级 |
|---|---|---|---|
| L08-C54 | **单仓上限三口径、两个宣示执行者，实际生效只有 P40**：firm 层 8%（三处文档/前端宣称，件无调用）∥ CTR-003 L1 单仓 20%（P40，真在跑）∥ sleeve 25%（sizing 侧）→ 谁越限、谁放行取决于走哪条路，且 `symbol_overrides` 又能在 P40 里改 | `tomorrow_boundary_planner.py:106`+`warroom.html:284` vs `daily_gate_snapshot.py:345-354`(not_wired_v1) vs `risk_veto_engine.py:262-280` | **P0**（并入 L08-C01 仲裁序：单仓上限必须先唯一化，否则仲裁序收口的仍是三把尺） |
| L08-C58 | **约束栈三件（F-C2-02/03/04）零 import**：相关性禁新仓、预算三级强裁、firm 聚合都无执行点 ⇒ "六层约束栈顺序 D76"在代码层只落地 2 层（市场状态 + 风控/资金曲线经 sizing min） | 三件 grep 零命中 + `budget_change_handler.py:551,597` 自述就绪 | P1（与 L08-C03 同一次内收窗口：要么接、要么按 w5_1 退役，禁"注册态永生"） |
| L08-C55 | 约束/聚合层专用异常类未落位（`ValueError` 兜底），号段被占需 Owner 重分配 → 约束违例与编程错误不可分型 | `firm_risk_aggregator.py:13`、`strategy_book.py:13` | P1（错误码号段裁定，机械可改） |
| L08-C56 | P35 T+1 无真源即跳过（唯一放行型规则），A 股可卖数量错 = 必被券商拒并消耗申报额度；应与 `position/core/t1_sellable.py` 语义件绑定为硬真源或升级为 fail-closed | `risk_veto_engine.py:28` | P1 |
| L08-C57 | 否决事件零物化（无法复盘否决率/误否率；面板"越限 0 次"是演示口径） | `VetoDecision` 无落库点 | P1（并 L08-C06） |
| L08-C59 | `BudgetChanged` 事件链：处理器"接线入口"已写好但全仓无事件生产者，`alloc_budget_change_log` 写函数存在（`allocation_persistence.py:152`）而其调用方未复证 → 需一次性把"事件产侧-消费侧-表"三点连测 | 本簿 ② 表 | P2（待复证后升/降） |
| 引用不重复 | SKEL L08-C09（P-P1-04 接线裁定：本簿复证零消费 + 给出真实类名 `AshareStopLossRuleEngine`）、L08-C10（THD-TRD-001..004 风险侧消费面，引用不重登）、BM-RC-10/RC-11 design 态（09 号文⑦）、F-C2-02 流动性约束（3 日可退出）消费实证（本簿判定=无执行点，归 L08-C58） | — | 已在账 |

## ⑤ 自审闸三态裁定

**MINING**。骨架 §3 六项债：本簿清空 3 项（risk_veto_engine 正文 `:20-364` 七规则/契约/扩展点全读；三件 F-C2 消费实测；P-P1-04 零消费复证）。仍欠：
1. `risk_veto_engine.py:364-末` （`evaluate_vetoes` 后半 + `RiskVetoEngine` 类体与 `RULE_ERROR` 转否决的具体实现、`snapshot_id` 传递）；
2. `correlation_regime_monitor.py` / `budget_change_handler.py` / `firm_risk_aggregator.py` 三件正文（阈值默认值、层次聚类实现、三级响应算法——**L08-C58 内收裁定必须逐守卫清点，否则会误删能力**）；
3. `pre_execution_checker.py` 闸门 2/3 正文（四级闸完整语义与 Fail-Closed 分级）；
4. 33 号（budget_change_handler）/ 32 号 / 30 号（多策略并发 §2.4、§2.2 单票硬顶）memo 全文对表（`scripts/check_risk_memos.ps1:4` 已给出这批 memo 的关键词覆盖闸，可复用）；
5. `ashare_stop_loss_engine.py` 正文四类否决线（L08-C09 裁定材料）；
6. `docs/03_modules/_domain_position/algo_flow/{correlation_regime_monitor,budget_change_handler,position_risk_budget_allocator}.yaml` 与实现一致性。
禁封矿：约束栈是终局"100% AI 自制"里唯一能替 Owner 看住组合敞口的一层，三件死码不是"够用"而是"缺件"。

## ⑥ 挖矿日志

- Grep src+scripts `RiskVetoEngine|risk_veto_engine|FirmRiskAggregator|CorrelationRegimeMonitor|budget_change|AshareStopLoss|kelly`（45 命中，截断）→ 定位闸门 4 强接电（`pre_execution_checker.py:225` 缺省自造）+ 前端/规划层三处"firm 层执行 8% 硬顶"宣称 + 候选池/裁决层查重分工声明（`negative_veto.py:29`、`human_trust_model.py:26` 两处均主动写明"risk_veto_engine=订单级硬否决"，说明**双否决器问题已被作者意识到并靠注释分工，未靠机制**）。
- Bash 只读列目录 + 定向 grep → 证实 `position/core/` 三件文件确实存在（排除"文件不存在"误判），并挖出 `position_sizing_engine.py:8` INVARIANTS 四路 `min()` 与参与率 15% 否决非截断、`_compute_kelly_fraction:357`、降级等权 `:130`；同时挖出 `firm_risk_aggregator.py:13`/`strategy_book.py:13` 的错误码号段冲突（→ L08-C55）。
- Grep `correlation_regime_monitor|budget_change_handler|alloc_budget_change_log|BudgetChanged|position_risk_budget_allocator` → 三件零 import 定案；`budget_change_handler.py:551,597` "接线就绪/生产调用方接线入口"自我声明；`regime_meta_allocator.py:5` 仅 CONSUMERS 声明；表侧 DDL 与写函数落点确认。
- Grep `ashare_stop_loss|AshareStopLoss|write_budget_change|risk_veto_engine import|RiskVetoEngine(` → P-P1-04 零 src 消费（仅 `tests/risk/test_ashare_stop_loss_engine.py`）+ 真实类名 `AshareStopLossRuleEngine` + 否决引擎引用面全集（3 处）。
- Read `risk_veto_engine.py:20-134` → 七规则语义与非对称细节（P15 放行减仓 / P35 无真源跳过）。
- 跨块顺带取证（零额外调用）：`daily_gate_snapshot.py:345-354`（约束栈 only-existence 读，`not_wired_v1`）、`trading_session.py:465-479`（快照四路真源）。
- 纪律：只读；未跑测试；未构造订单/未触发闸门；无 git 写；未触碰熔断与生产路径。
- 外部对表：未做（留统一轮；SKEL §5 已登记 Riskfolio-Lib（BSD-3，风险贡献/波动率目标）、PyPortfolioOpt HRPOpt（MIT，层次聚类对表可只对算法不引依赖）、T. Rowe Price risk overlay 分层实务（vol target+DD limit+trend filter 对照 D76 六层顺序）——**A 股适配闸**：HRP/Riskfolio 的协方差假设与 A 股涨跌停+T+1 的不可交易区间需在采前显式建模，否则 ρ 阈值 0.70/0.85 在停牌日失真）。
