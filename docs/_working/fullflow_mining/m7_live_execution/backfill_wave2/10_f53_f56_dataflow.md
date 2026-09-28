---
ttl: task_bound
volume: 10_f53_f56_dataflow
session: st-ailayer-final-20260924
creation_token: fullflow-m7-backfill-f53-f56-dataflow-20260926
---

# 10 · F53-F56 执行链路数据流真接通性（EX 面主册）

> 补挖波 20260926｜只读取证，零下单零撤单零连真实账户（计划任务仅 `Get-ScheduledTask*` 只读查询）。
> **差集声明**：既有 `01_qmt_bridge.md`（F56 桥本体）/`04_ex_core_ladder.md`（F53/F54 状态机与打板）/`05_ex_sor.md`（F55 路由）已把"件在不在、逻辑对不对"挖干；本册**不重复其结论**，只答一个它们没答的问题——
> **成交数据从券商回来后，到底有没有真的流进下游真源？**（本战役核心病灶类型=建了没接）

## 一、环节定义与边界

F53 订单生命周期与预检／F54 打板执行族／F55 执行算法路由／F56 QMT-miniQMT 桥（真源=`00_全环节总册.md:98-101`，四环节全标 **built**）。本册的切面=**四环节之间的四条边**：
① 下单前预检边（F53 内：预检器/价格笼子）② 成交回报边（F56→F53 Fill）③ 终态报告边（F53/F56→D_REPORTING，断点 E4）④ 成交入账边（F53→F63 tracker）。

装配根（composition root）实测唯一=`scripts/start_paper_session.py`（758 行，计划任务 `ZephyrAlpha_PaperSession` 承载，Last=09/25 09:25:02 Res=0 Next=09/26 09:25:00）。**除此件外，全仓无第二处把 F53-F56 装成可跑链路的入口**（文件桥侧的装配件只被烟测/E2E 脚本 import，见 §三 1.4）。

## 二、六向台账（按四条边分列）

| 向 | 内容（证据） |
|---|---|
| 上游输入 | 策略权重→`TradingSession.rebalance`（04 册已挖，本册不重挖）；本册入口=装配根 `scripts/start_paper_session.py:272-277`（读 `config/.env.qmt` 的 QMT_SIM_PATH/QMT_SIM_ACCOUNT → 构造 `MiniQmtBroker`，:275 延迟 import xtquant）；:237 C1 探针 tasklist 实扫 `XtMiniQmt` 进程在否；:661 `broker.connect()` 返回 False 即整轮中止并打印"XtMiniQmt 终端未在线" |
| 下游消费 | ③成交入账：`AsyncFillDispatcher(consumer=lambda fill,order: tracker.apply_fill(fill, order.side))`（:358-362）→ `PositionTracker`（04/03 册域），去重经 `AppendOnlyDedupSet`；④终态报告：`ExecutionReportProducer` → `zephyr.data.ch_writer.write_tsv_outcome()` → 表 `c1_market.execution_report`（`src/zephyr/ex_core/execution_report_producer.py:4` DEPENDENCIES，:5 CONSUMERS 自述三消费方）；②Fill JSONL 落盘（F57 系统侧唯一输入）：**无任何生产写方**（§四 D1，本册核心发现） |
| 自动化触发 | ①下单前预检：`src/zephyr/ex_core/trading_session.py:490 checker = PreExecutionChecker(...)`（:103 import）→ **在装配路径上，触发成立**；②成交回报：券商 C++ 回调线程 → `order_manager.register_fill_callback(dispatcher.enqueue)`（start_paper_session.py:366），且注释 :363-365 明确"先 start 再挂回调，反了会静默积压"→ 顺序正确；③文件桥腿：`qmt_file_bridge_broker.py:8` INVARIANTS"3 秒轮询柜台同步"、`attach_execution_report_producer`（:427）由 `qmt_file_bridge_integration.py:160` 调用；④日终：`ZephyrAlpha_PostSettlement` 15:30（见 20 册） |
| 真源与注册表 | Fill 契约真源=`zephyr.shared.contracts.fill`；ExecutionReport 列序真源=`schemas/categories/intraday/market_execution_report.py`（经 `execution_report_producer.py:4` 声明"不新增字段，以 schemas DDL INSERT_COLUMNS 为唯一列序真源"）；装配根在册面=`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`；断点真源=`docs/_working/fullflow_campaign/skeleton/04_sixway_machine_ledger.yaml`（E4 段，:5805-5861 记录 `qmt_file_bridge_integration` 消费/被调边）；E4 病灶原文=`execution_report_producer.py:20-23`（引 `docs/_working/clean_exam_e2e/env3_e2e_bridge/seg2_execution_log.md T6b`） |
| 门禁与质量尺 | ①预检四道闸（02 册口径）；价格笼子尺=`src/zephyr/ex_core/price_cage.py:153 check_price_cage`（264 行，`CageStatus` 枚举 :65、`_resolve_base_price` :123）；入账 fail-safe：成交查不到本地订单**只告警不入账**（:350-355"漏入账会在下一轮对账暴露为 drift 并冻结该标的，停错方向不静默放行"）；报告端旁路尺：`execution_report_producer.py:8` INVARIANTS"只在终态落一行/幂等/写失败 Fail-Loud 不静默/有量无佣拒绝落行"、:13 ERROR_CONTRACT"不向外抛，生产端旁路不得打断订单主链" |
| 当前运行状态 | **边①黄（预检器绿、价格笼子红—恒 UNKNOWN）/ 边②绿 / 边③黄（半通）/ 边④红（结构性零样本）**——逐条实测见 §三 与 §四 |

## 三、四条边逐条实证（子模块清单按"边"组织，非按件）

| # | 边/件 | 规模 | 接通实测 | 三态 |
|---|---|---|---|---|
| 1.1 | `OrderManager`（F53 状态机+撤改） | 595 行 | 装配根 `start_paper_session.py:492 order_manager = OrderManager()`；:366 注册 fill 回调；04 册已证状态机白名单 | **绿** |
| 1.2 | `PreExecutionChecker`（F53 订单级预检） | 351 行 | `trading_session.py:103/:490` 真注入 | **绿** |
| 1.3 | `check_price_cage`（F53 价格笼子硬约束） | 264 行，函数 :153；`CageStatus` :65、`_resolve_base_price` :123 | **两腿都有活调用方，但生产路径上数学上不可能夹边**：`OrderManager.submit_order` 调 broker 时 `broker.submit_order(order)`（`order_manager.py:345`）**不传 prev_close/不传 order_book** ⇒ miniqmt 腿 `_apply_price_cage_locked(order, order_book=None, prev_close=None)`（`adapters/miniqmt_broker.py:489/:818-843`）基准价恒缺→恒 `UNKNOWN`→仅 warn 放行（:824 自述"UNKNOWN 跳过校验并 warn（不阻断下单）"）；文件桥腿 `adapters/qmt_file_bridge_broker.py:536` 更只传三参（`side/limit_price/symbol`）⇒ **恒 UNKNOWN 且连 warn 都不打**（该处仅 CLAMPED 分支记日志，:537-544，随后 :546 `price=float(cage.clamped_price)` 取的是原价） | **红：装饰性护栏（有调用方、零判别力）**（§四 D3；与 memory 在册"价格笼子恒 UNKNOWN"同族，本波补出其**因**） |
| 1.4 | `AsyncFillDispatcher`（F56→F53 成交边） | 391 行 | 唯一生产引用=`start_paper_session.py:96/:358/:365/:366/:387/:402/:522/:570`（含停机排空 `_attach_dispatcher_teardown`，:387 `dispatcher.stop(timeout=…)` 防"在途成交随进程退出"） | **绿（本波少见的真接通件）** |
| 1.5 | `FillHandler` JSONL 落盘（G3，56 号文病根修复件） | 499 行（写 :389 `_append_fill_line`，读 :411-:424） | **写侧零生产调用方**：`FillHandler(fills_dir=…)` 全仓只出现在 `scripts/run_post_settlement.py:273/:429`（读）与 `tests/trading/test_g3_fill_persistence.py`（tmp_path）；装配根的成交终点是 `tracker.apply_fill`（:359），**不经过 FillHandler** | **红：见 §四 D1（本波最重发现）** |
| 1.6 | `ExecutionReportProducer`（断点 E4 生产端） | 455 行 | 由 `qmt_file_bridge_integration.py:40/:122/:160` 装配；而 `QmtFileBridgeAssembly` 的 import 方仅 `scripts/construction/test_qmt_file_bridge_e2e.py:35`、`scripts/construction/qmt_bridge_regression_smoke.py:63`、`tests/ex_core/test_execution_report_producer.py:354`——**日循环装配根（PaperSession/MiniQmtBroker 腿）不装它** | **黄：闭合只发生在烟测/回归路径**（§四 D2） |
| 1.7 | F54 打板执行族 / F55 ex_sor 路由 | 04 册 B3、05 册 B2 已判 | 本波复核其"执行半边挂 G22/SOR 传递性不可达"结论**未被推翻**，不重挖 | 黄（随既有册） |

## 四、堵点与病灶（本波新证，均为"建了没接"族）

### D1【P0·根因级】结算对账的系统侧输入结构性恒空——Fill JSONL 无人写

- **现象**：`ZephyrAlpha_PostSettlement` 每日 15:30 真跑且 exit=0，但日志恒为"原始=0 过滤后=0 / records=0"（20 册 §二实测），即交易级对账永远是 0 笔对 0 笔。
- **根因链（三证齐）**：
  1. 读侧口径：`scripts/run_post_settlement.py:429 deps.system_fills_reader = FillHandler(fills_dir=_DEFAULT_FILLS_DIR).query_fills_by_date` —— 系统侧 Fill 唯一来源是 `data/fills/YYYYMMDD.jsonl`；
  2. 写侧缺位：该目录的写者只有 `FillHandler.process_fill` 尾部（`src/zephyr/ex_core/fill_handler.py:381-397`），而成交在生产的终点是 `tracker.apply_fill`（`scripts/start_paper_session.py:359`），装配根**从未构造带 `fills_dir` 的 FillHandler**（`FillHandler(` 全仓非 test 命中仅 run_post_settlement 两处，§三 1.5）；
  3. 盘上实证：`D:/ZephyrAlpha/data/fills/` 目录存在（mtime 2026-08-27 15:30，即 G3 施工日建的空目录），**内零个 JSONL 文件**；worktree 侧目录甚至不存在。
- **后果**：F57 的"对平/DRIFT"三态在生产中不可达 DRIFT——20 册 B3（零样本假绿）的**上游真因就是本条**。二者不是两个缺陷，是一个缺陷的两个面（B3 是判据面、D1 是数据面）。
- **修法草案**：装配根在 `dispatcher` 的 consumer 里追加一路 `FillHandler(fills_dir=data/fills).process_fill(fill)`（或在 `tracker.apply_fill` 之后同事务落盘），并补一条"生产入口真写 JSONL"的集成测试（禁 tmp_path 之外零副作用，宪法 §9.6）。方向：成交落盘的真源应是**单一写者**——建议经 dispatcher consumer 单点写，避免双写不一致（须裁，M7-BF-5）。
- **工作量**：0.5-1 天（含测试）。**本车道可修**：是（纯代码+测试，不改判据不触真实下单），但本车道红线=只读，未施工。

### D2【P1】断点 E4 的"闭合"只在烟测路径成立

- 现象：`execution_report_producer.py:18-23` 自称"断点 E4 闭合"，其引用实测原文（09-18 E2E）是"全仓零生产调用方、模拟盘跑完后台 0 行"。
- 根因：闭合方式=在 `QmtFileBridgeAssembly` 里 `attach_execution_report_producer`（`qmt_file_bridge_integration.py:160`），而日循环走的 `MiniQmtBroker` 腿不装配它；文件桥腿自身又受 01 册 B1（SimBridgeExecute 执行腿断）制约。⇒ 两条腿各缺一段，`c1_market.execution_report` 的行数在日循环下仍无生产写方。
- 修法：装配根统一——PaperSession 腿在 broker 侧同样 attach（或把 E4 的 observe() 轮询挂进 TradingSession 心跳事件）；**并须以"表行数>0"为验收判据**，否则又是一次"接线件自证闭合"。
- 待补实证（本车道未做）：`c1_market.execution_report` 与 `reconciliation_differences` 的实际行数——禁本车道连生产库，请总筹以只读通道各跑一次 `SELECT count()`（列 §六 待挖）。
- 工作量：1-2 天。本车道可修：部分（代码可写，验收取数须总筹）。

### D3【P1·判据级】价格笼子在两条腿上都"被调用但恒不生效"（fail-open by construction）

- 现象：F53 真源列把"价格笼子硬约束"写成环节职责之一（`00_全环节总册.md:98`），实测两条 broker 腿都在调 `check_price_cage`（§三 1.3），但**没有一条腿能给出基准价**：
  1. `OrderManager.submit_order` → `broker.submit_order(order)`（`src/zephyr/ex_core/order_manager.py:345`）——签名里根本没有 `prev_close`/`order_book` 参数位（broker 侧默认值 `None`）；
  2. `miniqmt_broker.py:1306-1308` 同类问题的自述："涨跌停校验跳过: 缺少 prev_close"（涨跌停与笼子同腿、同缺因）；
  3. `price_cage.py` UNKNOWN 分支返回 `clamped_price=limit_price, was_clamped=False`（:188-197）⇒ 上游拿它当价格用等于原价通过；
  4. 文件桥腿连 UNKNOWN 告警都没有（`qmt_file_bridge_broker.py:536-546`，只在 CLAMPED 时 warn）。
- 与既有册/memory 关系：memory 在册"价格笼子恒 UNKNOWN（装饰性护栏）"是**果**；本条给出**因**＝唯一调用方不喂基准价，故护栏恒开。⇒ 这不是"没接线"，而是"接了但供数断"，比没接更难发现（有日志有调用有测试，全套自证活着）。
- 修法草案（两步，须裁 M7-BF-6）：
  - ①供数：`submit_order` 增加 `prev_close`/`order_book` 透传位，真源候选=`zephyr.data.instrument_master`（同仓第三处调用方已用正确口径，见 `src/zephyr/signal_ashare/tradability_preflight.py:4/:41/:191`——该处**传了基准价**，照抄即可，不新造）；
  - ②UNKNOWN 语义：拒单（fail-closed）还是放行＋告警——**属判据口径，本车道不改**；
  - ③无论 ①② 怎么定，文件桥腿须补 UNKNOWN 告警（否则该腿永远静默）。
- 工作量：①0.5-1 天 ②口径裁定 ③5 分钟。本车道可修＝①③可、②否（判据）。
- **自审更正（必留）**：本册首稿曾判"笼子生产零调用方"，系 `grep check_price_cage` 结果被 head_limit 截断在 test 文件所致**假结论**；复跑不限量命令见 §七-1b 已推翻首稿。结论改为"有调用、恒不生效"。教训入册：**判"零调用方"必须用不带 head_limit 的计数式命令复算**（本车道另两处 N2/N3 已按此法二次核过＝`grep -rn "EodReconciler\|ThreeWayReconEngine" src scripts` 去定义件后确实 0 命中）。

### D4【P2】两个日循环装配入口无共同真源

- 现象：PaperSession 腿（MiniQmtBroker，xtquant 直连）与 SimBridgeExecute 腿（文件桥）并存，两腿的 broker 类型不同、E4/风控前置注入点也不同（`qmt_file_bridge_broker.py:8` 才有 `risk_validator` 注入位与 `env=real/sim` 双实例隔离，MiniQmtBroker 腿无对应声明）。
- 后果：一条腿上加的护栏对另一条腿天然失效（D3 的笼子在两腿都恒开、E4 只在文件桥腿装配、风控前置 `risk_validator` 注入位只有文件桥腿声明——`qmt_file_bridge_broker.py:8`）。
- 修法：登记"装配根唯一化"案（M7-BF-7，属架构裁定，跨 01 册 B1）。工作量：裁定 0.5 天+施工视裁定。

## 五、内收与合并机会（w5_1）

1. `fill_handler`（交易流水侧）与 `position_tracker.apply_fill`（持仓侧）现是"同一 Fill 的两本账"——D1 修好后必须声明**谁是 Fill 真源**（建议 tracker=持仓真源、JSONL=流水真源，两本账各司其职不合并，但须在总册 F53 行写清，否则下一个人还会当成一个）。
2. `price_cage.py` 与 `ex_core/rules/ashare.py`：同域重复簇（规则包只是委托壳）→ 按"同真源可派生→必并"，若 D3 接闸，应经 rules 包统一入口，禁止第三处再委托 `_get_cage_params`。
3. `qmt_file_bridge_integration.py`（253 行装配壳）与 `start_paper_session.py` 的装配段：跨域不同对象（一条 sim 一条桥）**暂不并**，但 D4 裁定后若收敛为单腿则必并。

**自审更正一条（必留）**：D3 首稿判"笼子零调用方"是 `grep` 被 head_limit 截断在 test 文件造成的**假结论**，复跑不限量命令后推翻，现结论="两腿都有调用、但恒 UNKNOWN 无判别力"。同法二次核过 N2/N3（`EodReconciler`/`ThreeWayReconEngine` 去定义件后确实 0 命中），二者维持。⇒ 本册所有"零调用方"判语均已用**计数式**命令复核，非截断式。

**少见的反例（防一边倒结论）**：真正接通的有三件——`PreExecutionChecker`（`trading_session.py:103/:490`）、`AsyncFillDispatcher`（`start_paper_session.py:358-366/:387/:570`，含停机排空）、`ex_core/position_reconciler`（装配根 :465）。

## 六、自审闸三态

**挖干（4 条边全有实证）＋1 条待挖**：边①②③④各有 file:line 与盘上取证；六向每向均有证据格。**未达挖干的一条**：D2 的表行数实证未取得（本车道禁连生产库，已列交总筹取数）。自审另记两条自我约束：①本册未复跑任何装配根脚本（避免任何触券商路径），全部结论来自静态取证＋只读计划任务查询＋日志/目录只读；②`data/fills` 空目录是"零文件"而非"零成交"——若当日实有成交而 JSONL 不写，须由成交真源（柜台侧）交叉核，本册按"读侧永空"陈述，不推论"市场无成交"。

## 七、复核命令

```bash
# 1) 价格笼子：调用方存在（两 broker 腿＋signal_ashare 一处）——本波首稿"零调用"结论已被此命令推翻，更正见 §四 D3 自审
grep -rn "check_price_cage" src scripts --include=*.py
# 1b) 恒 UNKNOWN 的因：唯一下单调用方不喂基准价（期望 :345 行只有 order 一个实参）
sed -n '321,346p' src/zephyr/ex_core/order_manager.py
sed -n '188,197p' src/zephyr/ex_core/price_cage.py          # UNKNOWN 返回 clamped_price=原价
sed -n '536,546p' src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py   # 三参调用＋无 UNKNOWN 告警
sed -n '818,860p' src/zephyr/ex_core/adapters/miniqmt_broker.py           # 回退链与"不阻断下单"自述
# 1c) 对照：正确用法（传基准价）在 signal_ashare 腿已存在，可照抄
sed -n '186,196p' src/zephyr/signal_ashare/tradability_preflight.py
# 2) 成交落盘写侧缺位（期望：非 test 命中只有 run_post_settlement 两处读）
grep -rn "FillHandler(" src scripts --include=*.py | grep -v tests
# 3) 盘上零 JSONL（D1 第三证）
ls -la /d/ZephyrAlpha/data/fills
# 4) E4 装配只在桥壳、日循环根不装（期望：integration 的 import 方只 construction/tests）
grep -rn "QmtFileBridgeAssembly" src scripts tests --include=*.py
grep -n "ExecutionReportProducer\|attach_execution_report" scripts/start_paper_session.py   # 期望 0 命中
# 5) 成交入账边真接通（对照 D1：入账通、落盘断）
sed -n '358,367p' scripts/start_paper_session.py
# 6) 预检闸在装配路径上
sed -n '488,494p' src/zephyr/ex_core/trading_session.py
# 7) 日循环任务态（只读）
powershell -NoProfile -Command "$i=Get-ScheduledTaskInfo -TaskName 'ZephyrAlpha_PaperSession'; $i.LastRunTime.ToString()+' Res='+$i.LastTaskResult+' Next='+$i.NextRunTime.ToString()"
```

## 八、回写总册建议

`:98`（F53 built）→ **partial**，备注补："价格笼子两腿均在调但唯一调用方 `order_manager.py:345` 不喂基准价 ⇒ 恒 UNKNOWN 放行＝护栏恒开（本波 D3，含首稿误判更正）"；`:101`（F56 built）与 F53 的 Fill 边补一行"Fill JSONL 无生产写方 ⇒ F57 系统侧输入恒空（本波 D1，P0）"；E4 相关（F53/F56→D_REPORTING）备注"闭合仅烟测路径，日循环腿未装配"。
