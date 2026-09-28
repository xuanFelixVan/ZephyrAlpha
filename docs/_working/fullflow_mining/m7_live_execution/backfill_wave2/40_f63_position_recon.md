---
ttl: task_bound
volume: 40_f63_position_recon
session: st-ailayer-final-20260924
creation_token: fullflow-m7-backfill-f63-20260926
---

# 40 · F63 仓位管理与对账（对账腿＋NAV 腿＋漂移腿）

> 补挖波 20260926｜只读取证，零交易路径。真源口径=`00_skeleton/00_全环节总册.md:113`（F63：持仓状态机/对账/NAV 记录/仓位漂移，上游 F57、下游 F42/F60，状态 **built**，P0，T6）。
> **差集声明**：`03_position_sell.md` 挖的是 T6+T7 的**状态机与卖出融合仲裁**；本册只挖它没挖的三条腿——对账（reconciler）、NAV 记录（live_nav_recorder）、漂移监控（drift monitor），并对总册 `built` 提复核。

## 一、环节定义与边界

F63 = 券商账与系统账之间的"仓位真账"层。四子件按总册列为 `position/core/position_state_machine.py`、`position_reconciler.py`、`live_nav_recorder.py`。实测边界须修正两处：
1. **路径漂移**：`position_reconciler.py`（207 行）与 `live_nav_recorder.py`（253 行）**不在 `core/` 下**，实际在 `src/zephyr/position/` 根（`ls src/zephyr/position/` 实测；`core/` 下只有 `position_state_machine.py` 等 26 件）；
2. **同名两件**：`zephyr.position.position_reconciler`（MOD-INF-022）与 `zephyr.ex_core.position_reconciler`（MOD-EX-056）是**两套并行实现**，生产只认后者（10/20 册实证）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | 对账件（position 版）事件入口=`handle_execution_report(execution_report: dict)`（`src/zephyr/position/position_reconciler.py:123`，:26 自述"调用方通过 handle_execution_report 事件入口触发"）；三向输入定义=execution report + book record + counterparty（:20 标题行）；NAV 件=资产源协议注入（miniQMT broker 鸭型 `get_positions`→cash/total_market_value，头注 :4，且注明"CTR-P1-008 券商未接，当前=miniQMT 模拟净值源"）；漂移件=组合/单标的阈值（`PositionDriftMonitor(portfolio_threshold, symbol_threshold)`，见 tests/position/test_rebalance_engine.py:35） |
| 下游消费 | **position 版对账件 `[CONSUMERS]` 自认空**：`无生产消费方（BRK-016 在册断点；…待 ex_core 终态事件扇出后由装配批挂接）`（:5）；NAV 落库表真源=`schemas/categories/market/market_account_nav_daily.py:48 c1_market.account_nav_daily`（DDL-as-Code，挂 `scripts/ch/apply_market_tables_ddl.py:395/:542`），下游读数方=`src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py:39`（"只读净值序列→SurvivalInput"，存活告警）；ex_core 版对账下游=`trading_session.py`＋`governance.adapters.simulation_broker`（其头注 :5 声明）＋实测装配根 `scripts/start_paper_session.py:99/:465` |
| 自动化触发 | 对账件：零触发（`[STARTUP] imported`＋零 import，`zephyr.position.position_reconciler` 非 test 命中仅其自身头注）；NAV 件：**落库只经 writer 注入**（头注 :8 INVARIANTS"落库仅经 writer 注入，本模块不直连 DB"），而 `schemas/.../market_account_nav_daily.py:5` 明写 `zephyr.position.live_nav_recorder（writer 注入位，生产接线待排期）`⇒ 零触发；漂移件：无自触发（纯库）。反例对照＝ex_core 版在 PaperSession 盘中链有注入点（`start_paper_session.py:465 reconciler=PositionReconciler(...)`，经 RiskLayerOrchestrator） |
| 真源与注册表 | 件真源三颗＋同名双实现事实（MOD-INF-022 vs MOD-EX-056，见 §五-1）；NAV 表真源唯一=DDL-as-Code；模块翻译在册=`docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml` 族（本车道不写，登记交总筹）；BP 引用漂移：position 版对账件的 `[BLUEPRINT]` 指向 **`_domain_autonomy_perm/escalation_protocol/blueprint.md`**（:1，另一域的升级协议蓝图）而非仓位域蓝图；`[A_module]` safety 字段与头注 `[SAFETY] M` 不一致（:8=M vs :15=layer=module…safety=L） |
| 门禁与质量尺 | 本件是全车道**判据健康度最高**的一件：`[INVARIANTS]` :8 "P0-FATAL 必须触发硬中断；事件触发：ExecutionReport 到达时自动对账（**禁止时间触发**）；**输入不可得即判不平（Fail-Closed）——缺键/None/非字典/双空无出处一律 status=input_unavailable，禁把'没数据'说成'对平了'**"；MODIFY-GUARD=escalation 蓝图（:9）；测试=`tests/rollback/test_rollback_position_reconciler.py`＋`tests/e/test_e_position_reconciler.py`；NAV 尺＝输入校验 fail-closed（:12 ERROR_CONTRACT 三态 ValueError）＋首点 base 自身为基准=1.0（:8）；ex_core 版尺＝Decimal-only/冻结集全量重算/纯读不改源（其头注 :8） |
| 当前运行状态 | **红（三腿皆悬空），但 `[MATURITY] production`（:7）——账面与实测反向**：①对账腿零调用方（BRK-016 在册，自证）；②NAV 腿 writer 未接，独立旁证＝`scripts/research/verify_g07_sentiment_stratified_correlation.py:25` 记"无现成三策略历史净值（c1_backtest 无台账、**account_nav_daily 空表**），按 Owner 2026-09-11 立项口径"；③漂移腿的**类型被生产消费、主体零消费**——`sell_decision/core/position_triage.py:46` 只 import `TriageLevel` 枚举，`PositionDriftMonitor` 类的实例化在非 test 代码中 0 命中 |

## 三、子模块清单（ls + grep + 注册表三源）

`src/zephyr/position/` 实测根＝`_extensions/ api/ core/ infrastructure/ models/ services/` ＋根级三件（`live_nav_recorder.py`、`position_reconciler.py`、`__init__.py`）；`core/` 26 件（含 `position_state_machine.py` 572 行、`position_drift_monitor.py`、`position_limit_enforcer.py`、`cash_manager.py`、`rebalance_engine.py` 等，03 册已挖状态机，本册不重挖）。

| # | 子件 | 入口 file:line | 生产调用方 | 三态 |
|---|---|---|---|---|
| 4.1 | 对账（position 版，三向+Fail-Closed 判据） | `src/zephyr/position/position_reconciler.py:123`（207 行） | **0**（BRK-016 自认） | **红** |
| 4.2 | 对账（ex_core 版，双源快照比对+冻结） | `src/zephyr/ex_core/position_reconciler.py`（218 行，MOD-EX-056） | `scripts/start_paper_session.py:99/:465`、`src/zephyr/trading/recon_runner.py:78/:433`、被 `ex_core/eod_reconciliation.py:47` 委托 | **绿** |
| 4.3 | NAV 记录 | `src/zephyr/position/live_nav_recorder.py`（253 行，MOD-POS-023，`[MATURITY] testing`） | **0**（`zephyr.position.live_nav_recorder` 非 test 命中仅 schemas 头注引用） | **红** |
| 4.4 | 漂移监控 | `src/zephyr/position/core/position_drift_monitor.py`（MOD-POS-003） | 仅 `TriageLevel` 枚举被 `sell_decision/core/position_triage.py:46` import；监控主体 0 | **黄（枚举活、监控死）** |
| 4.5 | 仓位状态机 | `core/position_state_machine.py`（572 行） | 03 册已挖（其结论本册不推翻） | 随 03 册 |
| 4.6 | NAV 表 DDL + 装配 | `schemas/categories/market/market_account_nav_daily.py:48/:66/:68`；`apply_market_tables_ddl.py:542`、engine 归一 :1154 ReplacingMergeTree | DDL 装配活、数据面空（§二 旁证） | **黄（表活、行零）** |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| C1【P0】 | 两套 PositionReconciler 并行，**判据更好的那套没跑** | 两域各自建设：D_POSITION 版带"输入不可得即判不平"的假绿免疫判据（:8）却零装配；D_EX_CORE 版在跑但无该条不变量 ⇒ 现在跑的这套正是 20 册 B3 零样本假绿的口径来源 | 优先"把 4.1 的 fail-closed 口径移植进 4.2 或在装配层调 4.1"，二选一后**同名收敛**（§五-1）；改判据口径部分→待裁（M7-BF-9），装配部分可施工 | 1-2 天 | 部分（口径须裁） |
| C2【P1】 | NAV 腿 writer 未接 ⇒ 存活告警 `ops_alert_feed` 的净值读数面永远空 | 件建成时 `[CONSUMERS]` 就只写"候选"（:5），DDL 侧承认"生产接线待排期"（`market_account_nav_daily.py:5`），排期未落；且 09-11 已被研究件用作"空表"事实旁证 ⇒ 缺口至少存活 15 天 | 把 `live_nav_recorder` 的 writer 装进盘后链（与 20 册 B2 EOD 装配同一次改动最省：两者都要"盘后取券商快照"）＋验收判据=**表行数>0 且净值比连续** | 1 天 | 是（ writer 注入属装配，不改判据；但写 CH 表须走 DatabaseService/ch_writer 正门） |
| C3【P2】 | position 版对账件头注三处漂移：BLUEPRINT 指向别的域（escalation_protocol）、`[SAFETY] M` 与 `[A_module] …safety=L` 不一致、`MATURITY=production` 与"无生产消费方"矛盾 | 建件时蓝图复用＋元数据手工填写未校验 | 元数据归位（MOD-INF-022 是否误挂须治理确认）；`MATURITY` 字段建议与"调用方计数"联动而非手填（机判方向，登记不施工） | 0.5 天 | 是（属文档/元数据面，须总筹落，本车道未改） |
| C4【P2】 | 总册 F63 真源列路径错（`core/` 前缀对两件不成立） | 生成器/手工混填 | 回写总册 :113 路径（交总筹，本车道只登记） | 5 分钟 | 是（总册是热件，本车道禁改） |
| C5【登记】 | BRK-016/BRK-017 在册断点：本车道发现既有普查的一处**误归因已由他件自证纠正** | `src/zephyr/orchestrator/execution/reconciliation_loop.py:25-33`（BRK-017 澄清：该"调和循环"调和编排器自身 5 项不变量，**不是** FF-11→FF-12 成交对账链；把它当对账链接了就是假闭环） | 无需施工；本条价值=防止施工班拿 `reconciliation_loop` 去"闭" C1（该文件 :28 已点名 `position_reconciler.handle_execution_report` 才是那条链入口） | — | — |

## 五、内收与合并机会（w5_1）

1. **同名双实现必并（本波最强内收项）**：`zephyr.position.position_reconciler` ↔ `zephyr.ex_core.position_reconciler`。判据＝"同域重复簇→收敛唯一"。建议收敛方向：以**在跑的 4.2 为体**、以**判据严的 4.1 为魂**（移植 fail-closed 口径与 `status=input_unavailable` 态），并连带撤掉一处伪 `production` 标签。禁"再写第三个 reconciler"——F57 的 20 册 B1 里三方核对引擎正是第三个候选（两件应收，勿成三件）。
2. **NAV 与 EOD 共用一次券商快照**：C2 的 writer 与 20 册 B2 的 EOD 装配都要"日终取券商账"，同真源可派生⇒同批施工，避免两次连接（miniQMT 连接数有限制，见 01 册 B4/B5 限速教训）。
3. **不并**：`position_drift_monitor`（组合偏离，面向再平衡触发）与 reconciler（系统账 vs 券商账，面向停错冻结）不同对象，保留两件；但 4.4 的"类型被消费、主体零消费"须在总册 F63 备注写清，防被当作已建功能引用。

## 六、自审闸三态

**挖干（三腿六向全有实证）**，两处刻意不做的取证列入待挖：①`c1_market.account_nav_daily` 实际行数未直查（禁本车道连生产库；已用 09-11 研究件旁证，旁证≠直证）；②`core/` 其余 23 件（`position_sizing_engine`、`capital_curve_manager`、`cash_manager` 等）的调用方未穷尽——03 册口径只覆盖状态机与卖出链，本册只覆盖对账/NAV/漂移三腿 ⇒ **F63 域的"仓位计算腿"（sizing/capital/budget 族约 20 件）仍是空白**，交总筹决定是否另开一册（本波按任务书 F63 真源列范围收口，未扩面）。

## 七、复核命令

```bash
# 1) 同名双实现与各自调用方（期望：position 版非 test 零命中；ex_core 版命中 start_paper_session/recon_runner）
grep -rn "zephyr.position.position_reconciler\|zephyr.position import position_reconciler" src scripts --include=*.py
grep -rn "ex_core.position_reconciler" src scripts --include=*.py
# 2) 对账件的假绿免疫判据原文（C1 的"魂"）
sed -n '1,15p;20,30p;120,130p' src/zephyr/position/position_reconciler.py
# 3) NAV writer 未接（三件旁证同看）
sed -n '1,16p' src/zephyr/position/live_nav_recorder.py
sed -n '1,10p;44,50p' schemas/categories/market/market_account_nav_daily.py
grep -n "account_nav_daily 空表" scripts/research/verify_g07_sentiment_stratified_correlation.py
# 4) 漂移件"枚举活、监控死"
grep -rn "PositionDriftMonitor\|from zephyr.position.core.position_drift_monitor import" src --include=*.py
# 5) 误归因纠正原文（防拿 reconciliation_loop 去闭 C1）
sed -n '25,33p' src/zephyr/orchestrator/execution/reconciliation_loop.py
# 6) 总册路径漂移
sed -n '113p' docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
ls src/zephyr/position/ src/zephyr/position/core/ | head -40
```

## 八、回写总册建议

`:113` F63 状态 **built → partial**，备注三条：①对账腿与 NAV 腿生产零装配（BRK-016 + writer 待排期），仅 ex_core 版对在跑；②真源列路径改正（两件不在 `core/`）；③新增同名双实现内收项（`position.position_reconciler` ↔ `ex_core.position_reconciler`，判据强的那套没跑）。
