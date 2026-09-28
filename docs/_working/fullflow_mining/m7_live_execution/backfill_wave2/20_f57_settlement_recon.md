---
ttl: task_bound
volume: 20_f57_settlement_recon
session: st-ailayer-final-20260924
creation_token: fullflow-m7-backfill-f57-20260926
---

# 20 · F57 结算对账与三方核对（RC 面主册）

> 补挖波 20260926｜只读取证，零下单零撤单零券商写路径（计划任务取证仅 `Get-ScheduledTask*` 只读查询）。
> 真源口径=`00_skeleton/00_全环节总册.md:102`（F57：结算对账/三方核对/盘后管线/EOD 四步对账，标 built，P0）。
> 既有 7 册覆盖差集：`01_qmt_bridge.md` 只挖到"券商侧数据怎么来"，`03_position_sell.md` 只挖持仓状态机；**F57 四件套（TRADING-003 / TRADING-013 / L06-003 / recon_runner）的调用方与产物真源从未有册核过**，本册补此。

## 一、环节定义与边界

F57 = 下单成交之后的"对不平就报警"层，四步语义（真源=`src/zephyr/ex_core/eod_reconciliation.py:24-29` 自述表）：①持仓全量对账（委托 PositionReconciler）②资金核对③未成交订单日终转 EXPIRED④T+1 以券商为权威对齐。上游=F56 券商通道回报，下游=F42（报告）/F63（仓位对账）。

实测后边界须重划：**F57 实际是三个互不调用的对账引擎 + 一条唯一在跑的 CLI 管线**，而非一族的四步。管线 `scripts/run_post_settlement.py` 只装填了 `SettlementReconciler`（①交易级），**三方核对引擎与 EOD 四步器均不在其调用图内**（§二/§三实证）。故总册 `built` 判定不成立，本册改判 **partial**（判据缺件在 §四）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | 系统侧：`FillHandler(fills_dir=data/fills).query_fills_by_date()` 回放当日 Fill JSONL（`scripts/run_post_settlement.py:34-35` 文档口径，实测日志有成交查询路径）；券商侧：`broker_settlement_adapter.fetch_broker_settlement_records`（`src/zephyr/trading/broker_settlement_adapter.py:49` 反向 import `settlement_reconciliation.BrokerSettlementRecord`）；回测侧：`backtest_fills_adapter.py`（56 号文 G5）。三方核对引擎输入=三向流水注入（`three_way_reconciliation.py:26-30` 查重分工自述） |
| 下游消费 | `PostSettlementRunResult`→stdout + exit code（`run_post_settlement.py:13` 契约：0=OK/SKIPPED、3=DRIFT、1=ERROR）；差异落库真源=`c1_market.reconciliation_differences`（DDL-as-Code=`schemas/categories/market/market_reconciliation_differences.py:64`）——但**写方只有 `recon_runner`**，`run_post_settlement.py:8` INVARIANTS 明写"本脚本不重复写，落库由 recon_runner 负责"⇒ 现役调度链**不落任何差异台账**；`three_way_reconciliation` 的未匹配台账（OPEN→INVESTIGATING→RESOLVED 状态机，:27-29）无任何持久化消费者 |
| 自动化触发 | **唯一活口=计划任务**：`ZephyrAlpha_PostSettlement` STATE=Ready、LastRunTime=09/25/2026 15:30、LastTaskResult=0、NextRunTime=09/28/2026 15:30（实测 §七命令 1）。任务 ACTION 实测=直调 `python -u D:\ZephyrAlpha\scripts\run_post_settlement.py >> D:\ZephyrAlpha\data\runtime\post_settlement_last_run.log`——**绕过了 `scripts/run_post_settlement_daily.ps1`**（该 ps1:17 重定向到 `.runtime\logs\post_settlement.log`，实测两区该文件均不存在）⇒ 注册件与包装件是两条分叉入口，真源不唯一。EOD 四步器/三方引擎=零触发（`eod_reconciliation.py:33` 自述"本模块不挂调度"） |
| 真源与注册表 | 件真源三颗：`src/zephyr/trading/settlement_reconciliation.py`（431 行，MOD-TRADING-003）、`three_way_reconciliation.py`（441 行，MOD-TRADING-013）、`src/zephyr/ex_core/eod_reconciliation.py`（254 行，MOD-L06-003）＋编排 `recon_runner.py`（480 行）；错误码真源=`architecture_model/contracts/error_code_registry.yaml:2562`（ZA-EX-0023）/:3949（TRADING-013）；TDM 卡=TDM-E-L4-13（`docs/02_enterprise_architecture/10_trading_map/trading_map_04_e_l4_exec.md:105`，自动化列标 **auto**、承载标 MOD-TRADING-013）；排班=`config/resource_profile_registry.yaml` 第 24 槽 R-015 日终对账（据 `tests/scripts/test_generate_resource_profile_registry.py:83` 注） |
| 门禁与质量尺 | 容差尺：`EodReconciler.cash_tolerance` 默认 `Decimal("0.01")` 元分位（`eod_reconciliation.py:103/115`）；Fail-Closed 面：`align_to_broker` 默认 False（报告态），显式开启且券商端交割持仓齐备否则抛错（:8/:120-122/:156-163）；`position_reconciler=None` 直接抛（:120）；`recon_runner` 封顶 `testing`（56 号文 G7 + 宪章 B-007，production 启用挂 Owner 批准=`docs/_working/2026-08-28-remaining-construction-roadmap.md:75` B6 行）；alert_sink 异常吞没不阻断（:105-106）——**注意：吞没即"对不平也不响"** |
| 当前运行状态 | **红（三源交叉一致）**：①TRADING-013 三方核对=TDM 标 auto、实测生产零调用方（只 tests import，§三 3.2）；②L06-003 EOD 四步=零调用方，且其头注 [CONSUMERS] 已登记"运行时装配批（盘后 15:30 任务链/日终调度接线）"=**声明的消费方从未装配**；③现役管线虽每日真跑，但实测日志显示是**空对空恒绿**（下详）；④`reconciliation_differences` 台账无写方进入调度链 |

实测运行态证据（09/25 15:30 那轮，逐行取自 `D:/ZephyrAlpha/data/runtime/post_settlement_last_run.log`）：
```
盘后成交查询兜底: trade_date=2026-09-24 原始=0 过滤后=0
券商侧适配: trade_date=2026-09-24 fills=0 records=0 symbols=0
Daily audit: portfolio=miniqmt-sim date=2026-09-24 status=PASS pnl=0.00 gap=0.0000 issues=0
[标注] 日终审计输入=空快照最小输入（持仓/净值/限额真源未接线，57 号文 GAP 族后续批）
[标注] VaR 回测定级：跳过（状态根 ... 无盘前基线归档——预测腿零来源）
exit_code=0（0=OK/SKIPPED, 3=DRIFT, 1=ERROR）
```
⇒ 该轮"对账 OK"= 券商侧 0 笔 对 系统侧 0 笔 的**零样本一致**；审计 PASS 的输入是脚本自己标注的"空快照最小输入"；VaR 定级整步跳过。三处皆**无判别力的绿**，不是缺陷被藏住而是缺陷自己写在日志里（这条是本战役最诚实的假绿样本）。

## 三、子模块清单（ls + grep + 注册表三源交叉）

| # | 子件 | 规模/入口 | 生产调用方实测 | 状态 |
|---|---|---|---|---|
| 3.1 | `SettlementReconciler` 交易级逐笔对账 | `src/zephyr/trading/settlement_reconciliation.py` 431 行 | `scripts/run_post_settlement.py:89`、`src/zephyr/trading/recon_runner.py:88` | **绿（唯一接通件）** |
| 3.2 | `ThreeWayReconEngine` 三方流水核对+台账状态机 | `three_way_reconciliation.py:175`，441 行 | **零**（全仓 `*.py` 非自身/非 tests 无 import；`error_code_registry.yaml:3949`、`governance_operations_map.yaml:2243`、TDM:105 均只是登记面） | **红：建了没接** |
| 3.3 | `EodReconciler` 账户级日终四步 | `eod_reconciliation.py:95`，254 行 | **零**（`EodReconciler` 仅 `tests/ex_core/test_eod_reconciliation.py:33` import） | **红：建了没接**（头注 :5 已声明消费者=装配批，批未落） |
| 3.4 | `recon_runner.run_daily_reconciliation` L1/L2/L3 编排+归因+落库 | 480 行，:433 装 PositionReconciler | 仅 `scripts`/SOP 手工命令行（`docs/_archive/57_daily_cycle_sop.md:88`），且 MATURITY=testing 封顶 | **黄：件在、启用挂 Owner** |
| 3.5 | `broker_settlement_adapter`（138 行）/ `backtest_fills_adapter`（166 行）配对键 `{symbol}\|{seq:03d}` | :49 | 前者被 run_post_settlement 用；后者仅 recon_runner 链 | 绿/黄随 3.4 |
| 3.6 | `post_settlement_pipeline` 流水线真源（180 行） | `src/zephyr/trading/post_settlement_pipeline.py` | run_post_settlement 经其编排（:4 DEPENDENCIES） | 绿 |
| 3.7 | 差异台账表 `c1_market.reconciliation_differences` | DDL-as-Code `schemas/.../market_reconciliation_differences.py:64`，挂 `apply_market_tables_ddl.py:543` | 现役调度链零写方（3.4 不跑即零） | **红：表在、无人写** |
| 3.8 | 盘后计划任务 + 两份入口件 | `ZephyrAlpha_PostSettlement`；`scripts/register_post_settlement_task.ps1`；`scripts/run_post_settlement_daily.ps1` | 任务在跑；ps1 包装件不在任务 ACTION 里 | **黄：双入口分叉** |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| B1 | 三方核对引擎生产零调用，TDM 卡却标 `auto` | 件按 CAND-TRD-011/B13-04352 单独建成，装配批从未把它塞进 15:30 链（`three_way_reconciliation.py:29` 自称"被 eod_processor 调度消费"，但全仓无 `eod_processor` 调用它） | 二选一（属**口径/调度**决策→待裁，见 pending_rulings M7-BF-1）：①在 `run_post_settlement.py` 增第 6 步调 ThreeWayReconEngine 并把未匹配台账写 `reconciliation_differences`；②承认 TRADING-013 与 TRADING-003 同域重复，按 w5_1"同域重复簇→收敛唯一"内收，退役其一并回写 TDM | ①1-2 天 ②0.5 天+回写多册 | 部分（代码可写，**方向须裁**） |
| B2 | EOD 四步器零调用→日终"未成交转 EXPIRED / T+1 对齐 / 资金核对"三语义在生产链路 0 覆盖 | [CONSUMERS] 声明的"运行时装配批"未落地（`eod_reconciliation.py:5`）；它依赖的 ①持仓对账委托件 `ex_core.position_reconciler` 反而**已有生产调用方**（`scripts/start_paper_session.py:99/:465`）——即底层件在用、聚合器挂机 | 把 `EodReconciler` 挂进盘后任务链（③④两步是资金安全动作，align_to_broker 必须保持默认 False，只跑报告态）＋同批补一条集成测试钉"生产入口真调" | 1-2 天 | 是（不改判据即可施工） |
| B3 | 15:30 真跑但恒绿：0 笔对 0 笔算 OK、审计输入=空快照、VaR 整步跳过 | 判据把"无数据"与"对平"混成同一 verdict（`SettlementReconciler` 侧缺 fail-closed 的"样本量为 0 即判不可得"）；对照同族 `position/position_reconciler.py:8` INVARIANTS 已有正解口径："输入不可得即判不平——禁把'没数据'说成'对平了'" | 在管线出口加"零样本→status=INCONCLUSIVE（非 OK）"三态；**这是改判据口径→待裁**（本车道不动阈值，登记 pending_rulings M7-BF-2） | 0.5 天（口径批准后） | 否（口径 Owner/治理门位） |
| B4 | 计划任务绕过 `run_post_settlement_daily.ps1` 直调 python，两条入口的日志路径互不相认（`.runtime/logs/…` vs `data/runtime/…`） | 注册件与包装件双写未收敛；57 号文 GAP-3 当时留"挂调度待批"，批下来后动作定义另起一支 | 让任务 ACTION 改调 ps1（或删 ps1 认 python 直调为唯一真源），二者取一＋回写 `scripts/script-manifest.yaml:273` | 0.5 天 | 是（但改任务=生产流转动作，须门位放行，登记 M7-BF-3） |
| B5 | `reconciliation_differences` 表建成 + DDL 双处口径（CH `c1_market` 与 legacy governance.db sqlite 两系并存，`scripts/ch/apply_cross_asset_ddl.py:24` 自述 legacy 侧曾"坏 DDL 毒化"） | 迁移期双写残留；现役链因 B1/B2 无写方→漂移不可见 | 台账真源单点化=CH 侧（DDL-as-Code），sqlite 侧登记退役（**注册表/表净删属 Owner 门位**，只登记不动） | 1 天 | 否（登记） |
| B6 | `run_post_settlement.py` 日志首行仍打"手动触发未挂调度"，与 :5 头注"挂调度已获批准+已注册"自相矛盾 | 文案未随调度状态更新 | 一行文案修正＋加断言测试防漂移 | 5 分钟 | 是（但改的是本车道外热点件 `scripts/run_post_settlement.py`，回执登记待接线） |
| B7 | 日志明文出现模拟账户号（`account=8886156677`、`session=post_settlement_probe`） | 券商侧适配器把 account_id 打进 INFO；与 `01_qmt_bridge.md` B4"实盘账号明文"同病灶族，且此件是**已注册每日运行**路径 | 脱敏（保留末 4 位）＋日志字段门 | 0.5 天 | 是（属 01-B4 同批裁，登记 M7-BF-4） |

## 五、内收与合并机会（判据 w5_1）

1. **必并簇①**：`settlement_reconciliation`（TRADING-003）与 `three_way_reconciliation`（TRADING-013）——两件的输入都是"系统流水 vs 券商流水 + 容差比对"，TRADING-013 多出的只是持仓/资金两向与未匹配台账；同真源可派生→**TRADING-003 应做核、TRADING-013 的台账状态机并入**，禁止"再写第三个对账器"。当前两件零互调＋零调用方＝并的窗口成本最低。
2. **必并簇②（跨册发现，同 40 册 §五）**：`ex_core.position_reconciler`（MOD-EX-056，有生产消费方）与 `position.position_reconciler`（MOD-INF-022，[CONSUMERS] 自述"无生产消费方"）＝同名两实现，EOD 器只认前者（`eod_reconciliation.py:47` import）。
3. **零触发零消费→退役候选**：若 B1 裁②，则 TRADING-013 的"三向流水匹配"部分退役、台账状态机部分保留（内收进 003）。登记，不自行删。
4. **不并**：`recon_runner` 的 L1/L2/L3 是"回测 vs 模拟盘"对账（56 号文口径，比对回测 run_id），对象与 F57 实盘结算不同→跨域不同对象。

## 六、自审闸三态

**待挖→部分挖干**：六向每向均有实证（表内逐格 file:line 或命令输出），四件套调用方以"非自身/非 tests 全仓 import 扫描"穷尽（命令见 §七，输出仅命中 tests，可复跑）。未达"挖干"的自认缺口三条：①未逐行读 `three_way_reconciliation.py` 的容差与匹配算法本体（只取口径），若 B1 裁①需补；②`reconciliation_differences` 在 CH 侧的**实际行数**未查（本车道禁连生产库取证，需总筹以只读通道跑一次 `SELECT count()`）；③09/25 之前若干轮的 exit code 分布未抽样（日志仅 last_run 单文件覆盖）。此三条列 §九 待挖，不计入挖干。

## 七、复核命令

```bash
# 1) 计划任务真跑态（只读；ACTION 里能看到绕过 ps1 直调 python）
powershell -NoProfile -Command "$t=Get-ScheduledTask -TaskName 'ZephyrAlpha_PostSettlement'; $t.Actions|%%{ $_.Execute+' '+$_.Arguments+' | WD='+$_.WorkingDirectory+' | '$t.State }"
powershell -NoProfile -Command "$i=Get-ScheduledTaskInfo -TaskName 'ZephyrAlpha_PostSettlement'; 'LastRun='+$i.LastRunTime+' Res='+$i.LastTaskResult+' Next='+$i.NextRunTime"
# 2) 那轮到底对没对（零样本假绿三行）
grep -nE "原始=|fills=0 records=0|status=PASS|空快照最小输入|VaR 回测定级" /d/ZephyrAlpha/data/runtime/post_settlement_last_run.log | tail -8
# 3) 两个引擎零生产调用方（期望：只命中 tests 与自身）
grep -rn "ThreeWayReconEngine\|from zephyr.trading.three_way_reconciliation" src scripts tests --include=*.py | grep -v "^src/zephyr/trading/three_way_reconciliation.py"
grep -rn "EodReconciler" src scripts --include=*.py          # 期望 0 命中
# 4) 台账表无写方 + 双 DDL 口径
grep -rn "reconciliation_differences" src scripts --include=*.py | grep -iE "INSERT|write"
# 5) 差异真源与注册面
sed -n '24,33p' src/zephyr/ex_core/eod_reconciliation.py       # 四步语义表 + 查重分工
sed -n '103,106p' src/zephyr/trading/settlement_reconciliation.py  # E-TR-01/02 事件"阶段1回调/阶段2总线"自述
```

## 八、回写总册建议

`00_全环节总册.md:102` 的 F57 状态由 **built → partial**，备注列补："四件套仅 TRADING-003 接通；TRADING-013/L06-003 生产零调用方（TDM-E-L4-13 标 auto 为假）；15:30 任务真跑但零样本恒绿；差异台账表无写方"。
