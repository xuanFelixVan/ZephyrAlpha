---
ttl: task_bound
volume: 90_backfill_wave
session: st-ailayer-final-20260924
creation_token: fullflow-m7-backfill-wave-20260926
---

# M7 补挖波 90 收卷册（20260926 · 本车道封矿波）

> 车道=M7 实盘执行链；工作面=worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`。
> 零提交、零入队、零 claim/release（作业簿 §一-2）；**绝对禁触真实交易**：本波未 import/未执行任何下单撤单报单路径，运行态取证仅用只读 `Get-ScheduledTask*`、日志/目录 `ls·sed·grep`。
> 派单依据＝交接书 `docs/_working/ai_layer_vision/HANDOFF_st_ailayer_final.md` §四"EX+RC 深挖组限速失败未重派"；本波补该空缺。

## 〇、RC 口径实测（先定口径再开工，结论=不可考）

- 实测：`grep -rn "EX\+RC|RC 深挖|EX/RC|KS/FR|挖矿组|12 组" docs/_working/ai_layer_vision/` → **仅命中 `LEDGER_final.md:110-111` 两行流水账**，用作组名标签，无任务书/口径定义件；`m7_live_execution/00_m7_overview.md` 全篇无 "RC" 字样（已整册读）。
- ⇒ **RC 组原始口径不可考**（该组撞账户限速 1302 未重派，任务书随车道未落地而失存）。本波按**环节真源字面族**开工，理由与依据：
  1. RC 取"**R**econ**c**iliation"字面族＝F57（`00_全环节总册.md:102` 名"结算对账与三方核对"）＋F63（`:113` 名"仓位管理与对账"）；
  2. 加上 F58（`:103` 执行成本反馈，总册标 partial）凑成"下单→成交→对账→成本反馈"闭环，与 EX 面（F53-F56）严格互补、与既有 7 册差集最小（既有册一字未动，见 §二）；
  3. 该口径**不侵入邻车道**：F42 报告面、TDM 状态机、M3 拦截器均未碰。
- 若总筹认定 RC 另有所指（如 risk-control 族），本波四册仍全部有效（EX 面与对账面都是 M7 在册空缺），只需另派 risk 族。

## 一、本波产物（6 件，全部新建）

| 件 | 环节 | 一句话结论 | 三态 |
|---|---|---|---|
| `10_f53_f56_dataflow.md` | F53-F56 | 四条边实测：预检器绿、入账边绿、**E4 报告边只半通**、**Fill 落盘边结构性零样本（D1=P0 根因）**；价格笼子两腿均在调但恒 UNKNOWN 无判别力（D3，含首稿误判自审更正） | 挖干（1 项待挖：CH 表行数） |
| `20_f57_settlement_recon.md` | F57 | 四件套只有 1 件接通；15:30 任务真跑但"0 笔对 0 笔"恒绿；台账表无写方；双入口分叉 | 部分挖干（3 项待挖） |
| `30_f58_execution_cost_feedback.md` | F58 | 反馈环两端互指空头指针＋历史是进程内 list ⇒ 环即使接线也闭不上；修复次序锁 D1→F57-B1→F58 | 挖干（1 项待挖：零样本 verdict 未实测） |
| `40_f63_position_recon.md` | F63 | 对账/NAV/漂移三腿全悬空；**同名双 PositionReconciler**，判据强的一套没跑；总册真源列路径错 | 挖干（2 项待挖：行数直证、仓位计算腿 20 件空白） |
| `pending_rulings.md` | 跨册 | 10 案，呈前已扫 `ruling_registry.yaml` 确认无既有裁定覆盖 | 待裁 10 |
| `90_backfill_wave.md` | — | 本册 | — |

## 二、与既有 7 册的差集（防重挖自证）

| 既有册 | 它已答 | 本波只答（差集） |
|---|---|---|
| `01_qmt_bridge.md`（F56） | 桥本体、HTTP/文件双通道、柜台镜像、SimBridgeExecute 执行腿断（B1） | **桥产物往下游流的那条边**：E4 生产端只装在 `QmtFileBridgeAssembly`（import 方仅 construction/tests），日循环腿不装；Fill JSONL 无人写 |
| `04_ex_core_ladder.md`（F53/F54） | 状态机白名单、Saga 零接线、打板执行半边挂 G22 | F53 六向里**未列真源清单的 `check_price_cage`（0 调用）**＋`AsyncFillDispatcher` 接通实测（该册只画在链路图，未核装配） |
| `05_ex_sor.md`（F55） | SOR 27 件真身、传递性不可达（B2） | F58 三件套（services 层）的调用方穷尽＝仅包级 re-export；并把 B2 的下游腿（XS-018→XS-011 环）单独钉死 |
| `03_position_sell.md`（T6/T7） | 仓位状态机＋卖出融合仲裁 | F63 的**对账腿/NAV 腿/漂移腿**（该册未涉） |
| `02_kill_switch.md`、`06_compliance_gates.md`、`00_m7_overview.md` | 熔断/合规/总览 | 本波零重叠（F57/F58/F63 与 E4/笼子均不在其范围）；仅 `00_m7_overview.md` §三"实盘就绪度"需按本波追加第四类缺口（§四） |

既有 7 册**一字未改**（只读取证），需回写的三条判据变更全在 §五 交总筹。

## 三、"建了没接"清单（本波新证，file:line，全部可复跑；N5 属变种＝"接了但供数断"）

| # | 件 | 病灶 | 证据锚 |
|---|---|---|---|
| N1 | `src/zephyr/ex_core/fill_handler.py:381-397`（Fill JSONL 写侧，56 号文 G3 病根修复件） | **生产链无写者**：装配根成交终点是 `scripts/start_paper_session.py:359 tracker.apply_fill`，全仓 `FillHandler(fills_dir=…)` 非 test 命中只有 `scripts/run_post_settlement.py:273/:429`（读侧）；盘上 `D:/ZephyrAlpha/data/fills/` 自 08-27 起零文件 | 10 册 D1（三证）；**后果=F57 系统侧输入恒空** |
| N2 | `src/zephyr/trading/three_way_reconciliation.py:175`（MOD-TRADING-013，TDM-E-L4-13 标 **auto**） | 生产零 import（非 test 命中=0）；头注 :29 自称"被 eod_processor 调度消费"，全仓无此调用 | 20 册 3.2/B1 |
| N3 | `src/zephyr/ex_core/eod_reconciliation.py:95`（EOD 四步器） | 头注 :5 `[CONSUMERS] 运行时装配批（盘后 15:30 任务链/日终调度接线）`＝**声明的消费方从未装配**；非 test 零 import | 20 册 3.3/B2 |
| N4 | `schemas/categories/market/market_reconciliation_differences.py:64`（差异台账表） | 表＋DDL 在，唯一写方 `recon_runner` 不跑（testing 封顶挂 Owner）⇒ 现役调度链零行 | 20 册 3.7/B5 |
| N5 | `src/zephyr/ex_core/price_cage.py:153 check_price_cage`（F53"硬约束"） | **两腿都在调、但恒不生效（供数断而非接线断）**：唯一调用方 `order_manager.py:345 broker.submit_order(order)` 不传 `prev_close/order_book` ⇒ miniqmt 腿 `adapters/miniqmt_broker.py:818-860` 基准价恒缺→恒 `UNKNOWN`→仅 warn 放行（:824 自述"不阻断下单"）；文件桥腿 `adapters/qmt_file_bridge_broker.py:536-546` 只传三参、UNKNOWN 分支连告警都没有、随后取 `clamped_price`（=原价，`price_cage.py:188-197`）；对照正确用法已存在于第三处调用方 `src/zephyr/signal_ashare/tradability_preflight.py:191`（传了基准价） | 10 册 D3（首稿"零调用"误判已更正） |
| N6 | `src/zephyr/ex_core/execution_report_producer.py`（断点 E4"闭合"件） | 装配点 `adapters/qmt_file_bridge_integration.py:160`；`QmtFileBridgeAssembly` 的 import 方只有 construction 烟测/E2E 脚本/test ⇒ 日循环腿无生产写方，E4 闭合只在测试路径成立 | 10 册 1.6/D2 |
| N7 | `src/zephyr/ex_sor/services/execution_quality_scorer.py`（F58 全族） | 三件套 158 命中/7 文件＝3 自身＋`services/__init__.py` re-export＋3 test；`[CONSUMERS] MOD-XS-011 算法选择器反馈环`＝selector 不读它；历史评分是进程内 `_history`（:312/:411） | 30 册 F1/F2 |
| N8 | `src/zephyr/position/position_reconciler.py:123`（MOD-INF-022） | `[CONSUMERS]` 自认"无生产消费方（BRK-016 在册断点）"却标 `[MATURITY] production`；同名的 ex_core 版在跑但判据较松 | 40 册 4.1/C1 |
| N9 | `src/zephyr/position/live_nav_recorder.py`（GAP-F-29 净值腿） | `schemas/.../market_account_nav_daily.py:5` 自记"writer 注入位，生产接线待排期"；旁证 `scripts/research/verify_g07_sentiment_stratified_correlation.py:25`"account_nav_daily 空表"（09-11 至今） | 40 册 4.3/C2 |
| N10 | `src/zephyr/position/core/position_drift_monitor.py`（MOD-POS-003） | 类型 `TriageLevel` 被生产 import（`sell_decision/core/position_triage.py:46`），监控主体 `PositionDriftMonitor` 非 test 零实例化＝枚举活、监控死 | 40 册 4.4 |

**少见的反例（本波同时证"接通"的三件，防一边倒结论）**：`PreExecutionChecker`（`trading_session.py:103/:490` 真注入）、`AsyncFillDispatcher`（`start_paper_session.py:358-366/:387/:570` 含停机排空）、`ex_core/position_reconciler`（装配根 :465 真注入）。⇒ 病灶不是"全链没接"，而是**成交事实离开内存之后的每一站都没接**（落盘/报告/对账/成本反馈四站）。

## 四、本车道净结论（供总筹并入 00_m7_overview §三）

实盘就绪度缺口在原三类（00 册 §三）之外追加**第四类：数据流断层类**——原三类的取证前提"链路在跑"不成立：
只要 N1 未修，F57/F58/F63 三环节的任何"绿"都是**零样本绿**，任何演练结论都不可信。⇒ 建议总筹把 **N1 列为 M7 车道唯一 P0 前置**（1 天量级，纯代码＋测试，不触判据不改下单，本车道未施工因红线=只读）。

## 五、遗留待挖清单（交接用，逐条标缺什么）

| # | 待挖项 | 缺的取证 | 归属建议 |
|---|---|---|---|
| T1 | `c1_market.execution_report`／`reconciliation_differences`／`account_nav_daily` 三表实际行数 | 本车道禁连生产库；须以 `DatabaseService` 只读通道各跑一次 `SELECT count()` | 总筹（一次取数解三册共缺） |
| T2 | `ThreeWayReconEngine` 匹配算法与容差逐行核 | 本波只取口径（头注/类签名）；若 M7-BF-1 裁①需补 | M7 后继班 |
| T3 | PostSettlement 历史轮 exit code 分布（现仅有 last_run 单文件） | 日志被覆盖，无历史归档面 ⇒ 顺带登记"运行台账缺失"（M7-BF-10 相关） | M7 后继班 |
| T4 | F63 仓位**计算腿**（`position/core/` 另 20 件：sizing/capital/budget/limit_enforcer 等）调用方穷尽 | 本波按任务书真源列范围收口未扩面；03 册只挖状态机 | 建议另开 `50_f63_position_sizing.md`（M7 唯一在册空白） |
| T5 | F58 零样本时 `_verdict/average_score` 实际返回值 | 刻意未跑（不为取证执行交易域代码路径） | 测试侧补（tests 可覆盖，非挖矿项） |

## 六、需总筹代做的登记（本车道按红线未自改）

1. **creation_token**：本波 6 件已在各册头注自带唯一 token（`fullflow-m7-backfill-*`），请总筹统一补 creation_token 与 `module_translation_registry` 登记。
2. **总册回写 5 条**（`00_全环节总册.md`）：`:98` F53 built→partial（笼子两腿恒 UNKNOWN＝供数断，非未接线）｜`:101` F56 补 Fill 落盘零写方备注｜`:102` F57 built→partial｜`:103` F58 备注三条｜`:113` F63 built→partial **且真源列路径改正**（两件不在 `core/`）。
3. **depgraph 设计节点**：本波零新建 .py ⇒ **无新节点**；但 N1/N6 若施工，涉及既有节点 `MOD-EX-056/MOD-L06-001/MOD-TRADING-003` 的产物边，请登记为"待接线一行"。
4. **TDM 卡纠错**：`trading_map_04_e_l4_exec.md:105`（TDM-E-L4-13 自动化列 auto）为假，随 M7-BF-1 一并改。

## 七、复核命令（10 分钟读完本波）

```bash
ls docs/_working/fullflow_mining/m7_live_execution/backfill_wave2/        # 6 件在盘
git status --porcelain docs/_working/fullflow_mining/m7_live_execution/    # 只应见新目录，既有 7 册零改动
# 本波"建了没接"抽验三条（计数式，非截断式）
grep -rn "FillHandler(" src scripts --include=*.py | grep -v tests        # 期望 5 行：aggregate_root_manager:156（无 fills_dir=不落盘）+fill_handler:187（docstring）+run_post_settlement:34/273/429（读侧）
grep -rn "EodReconciler\|ThreeWayReconEngine" src scripts --include=*.py | grep -v "^src/zephyr/ex_core/eod_reconciliation.py" | grep -v "^src/zephyr/trading/three_way_reconciliation.py"   # 期望 0 命中（N2/N3）
grep -rn "check_price_cage" src scripts --include=*.py                     # 期望 10 行含两 broker 腿调用（N5 是"恒 UNKNOWN"而非"零调用"，勿照首稿复述）
# 运行态两证（只读）
powershell -NoProfile -Command "Get-ScheduledTaskInfo -TaskName 'ZephyrAlpha_PostSettlement' | Select LastRunTime,LastTaskResult,NextRunTime"
grep -nE "原始=0|records=0|status=PASS|空快照最小输入" /d/ZephyrAlpha/data/runtime/post_settlement_last_run.log | tail -5
# 红线复核：本车道零提交
git log --oneline -1        # 应为基底 f3cac8b95c（挖矿班 0 提交）
```
