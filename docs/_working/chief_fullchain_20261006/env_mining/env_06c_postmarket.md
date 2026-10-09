---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_06c_postmarket.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-06c 盘后段（15:00–20:00）挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：FIG13 车道 `docs/_working/map_build/fig13_daycycle/`（00_skeleton.md §2 段 C + 簿06/07/08）；机生图 `config/trading_day_cycle_map.yaml` segments.C（purpose_tag t08/t09/t10 全段覆盖）。
- **现役挖掘 = st-fig13-bone-20261004**。本簿只读其领地；价值=①挂接收编 ②补代码消费面/字段面 ③本役三态裁定。D13-29/31 两格与 ENV-15 共案，本簿挂接、env_15 真挖。
- **职责一句话**：15:05 收盘后 85 分钟窗口里"定格类"（板块/指数分钟K）与"核对类"（持仓对账事件腿/15:30 结算/15:40 三账）排在一起，随后 16:30 日K时钟源→16:45 dloop 全链复盘→17/18/19 三批次。
- **节点与状态（图本体 2026-10-06 机生读数，13 节点）**：✅7（D13-26/28/30/32/34/35/48）｜🔨4（D13-25 恒 T-1 定性、D13-27 拆腿、D13-33、D13-29→fig13 簿06 判 🌑/红条目 recheck 已在册）｜⬜2（D13-31 当日回测跑批=角色在册被挂起、D13-G03 三账差异表恒空且消费方按恒空降级）。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（谁触发） | 15:10 三件同分钟三机制同窗（簿06 O-3：sector_close_final 机制 A、ZephyrAlpha_IndexMinuteEOD 机制 B、尾段收口）；15:30=机制 B（`register_post_settlement_task.ps1:42` + StartWhenAvailable 补火）**且 `POST_SETTLEMENT_CRON="30 15 * * *"` 常量构成同值两处 INV-1 撞车面**——簿06 判：两处都不是运行时真源，ps1 才是触发者；15:40=eod_reconciliation 假通道槽（零任务+零分支+APScheduler 记 success，15:40:03 现场捕获三行日志）；16:45=dloop_post 特殊槽（`scheduler.py:366-433` 唯一 handler，总闸实测开着） | 🌑-3/🌑-4 在册：柜台真实结算单不存在、交易所日终时刻无外部真源→15:30"就绪"永远推定 | signal |
| 下（谁消费） | **本簿补充·代码消费面**：①D13-30"就绪门"读的表不是 kline_daily 而是 `kline_index`（`daily_loop_master_switch.py:88-89,101-102` `_SQL_MAX_KLINE`）——槽名/表名/门源三词指三物，`ready_gate` 照抄槽名必指错（簿08 前置纠偏 A）；②D13-25 恒定格 T-1 且行内 `ts` 写死 15:10:00 假时间戳（`sector_state_pipeline.py:353-360,383`）→D13-10 盘前复制的亦即错位态，可机生红用例"ready_gate 依赖槽 cron 晚于本格⇒恒取 T-1"；③dloop 16 段中 **11 段返回 status 硬编码 "ok"**——段级失败可见性编排层与底层两边都没有（簿07 前置纠偏 C） | battle_map `flow_stage='reconciliation'`+BM-REC-01 承载装配落点→处置=扩展反挂 source_ref 指 D13-28/29 | signal |
| 内（子环节） | D13-28 四棒（系统侧 Fill 读取/券商侧适配/SettlementReconciler/DailyAuditor+VaR）今日全跑但输入 fills=0/`data/fills` 0 文件→**OK-over-zero 红条目**（对"OK"的读数纪律：两侧皆空的一致≠对平）；D13-32 三前置纠偏（段数 16 非 10/11；GRADUATED_PACKAGES 常量真源在 `daily_decision_orchestrator.py:122` 非 master_switch；幂等在底层但 11 段硬编码 ok）；D13-33 段序契约 verify 恒先于 settle 成立，但 09-23 plan 未结算、校准腿 Brier 样本冻结而聚合面照常出数（簿09 总线②） | 57 号 §4 人工回测长命令为 D13-31 唯一真源（已归档） | signal |
| 旁（撞车面） | D13-27 两链不合并：注释自证的事件入口腿（`position/position_reconciler.py:123` handle_execution_report，BRK-016 零生产调用方）vs 真跑的 300s `threading.Timer` 腿（`risk_layer_orchestrator.py:1781-1818`，宿主 PaperSession 进程）——schedule.yaml 注释两句自辩与实态方向相反，图必须画成边（簿06 §3）；D13-29 与 D13-28 的"15:30 就绪→15:40 核对"等待边今日两端一头在跑一头不存在 | 图12 让渡 3：对账/归因装配落点归 BM-REC-*，本图只给时序 | signal |
| 史 | 三件"三账"实现（MOD-TRADING-007 recon_runner/MOD-TRADING-013 three_way_reconciliation 自标 production/MOD-L06-003 ex_core/eod_reconciliation）**全零生产调用方**（簿06 §5 表+本役 2026-10-06 grep 复核仍零）→内收判据 w5_1 候选"零触发零消费→退役"，交总包排裁定；#234 已建表先于接线且接线至今未到 | 普查数字漂移族（27→29→34 槽）见 env_06a §4 轮3 | signal |
| 新 | fig13 溢出 O-1~O-8 在册（假通道子类/OK-over-zero/机制错登/文档滞后运行时输出 run_post_settlement.py:501 等）；D13-31 簿08 改判词："对账 L1 基准腿"是替未裁决问题预先投票——CAND-BT-003（candidate_module_registry.yaml:7799-7820）自陈"向量化不对账、56 号文 §2 已定分工"，阻塞问题「向量化产出是否会被用做对账基准」登记后 34 天未动→**角色在册被挂起，非缺执行体**；PostSettlement `StartWhenAvailable`=日序图少见的"缺席可补"正向样本，进 `miss_fallback` 字段 | 无 | signal |

## §2 挖干自评

- **三扫收敛**：fig13 三簿（06/07/08）覆盖 13 节点全部六向，dloop 16 段解剖到"每段可指认执行体"粒度；本役补面后增量归零。
- **长尾**：①D13-29 三账接线方案（谁调用 run_daily_reconciliation/还是并入 post_settlement 第 5 棒）+②三件实现收敛裁定+③D13-31 角色裁决（CAND-BT-003 阻塞问题）——三项均为 Owner 级决策，证据面已齐，归 env_15 簿汇总给裁定。
- **🌑 清点**：D13-29 🌑（环节今日不存在）、🌑-3 柜台结算单、🌑-4 外部日终真源、🌑-5 尾段成交口径——全部骨架 §6 在册，本簿不消不加。

## §3 挖后自审闸三态裁定

**挂起排期**（本段主体）；D13-29/31 两格移交 env_15 簿出独立裁定。
- 理由：①盘后段是全图挖得最透的一段（簿06 含 15:40 现场捕获这类一次性证据），本役无增量矿脉；②段内红条目（D13-29 空转、D13-28 OK-over-zero、D13-31 挂起）的施工路径全部收敛到一个 Owner 裁定点——"15:30/15:40 对账链怎么接、三件实现留谁、基准腿供不供"——在裁定前任何单点施工都是提前投票；③定格类缺口（D13-25 恒 T-1）修法=调序至 daily_kline 之后，牵动 15:10-16:30 整段排布，随图本体 ready_gate 施工统一落。
- 解锁条件：fig13 封矿 + env_15 簿 §3 裁定获批（对账链接线方案+三件实现收敛+CAND-BT-003 阻塞问题三项同批裁）。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 产出 |
|---|---|---|---|
| 1 | 读簿06 全文+簿07/08 §0-§2 关键节 | 挂接完成：D13-29 🌑 三证、D13-27 拆腿、D13-31 改判词、OK-over-zero 全部收编 | §0/§1 |
| 2 | 机生图 segments.C 解析 + t09/t10 purpose_tag 对表 | signal：D13-29 recheck=🌑/unreachable 已在册，图簿一致 | §0 状态行 |
| 3 | 三件三账实现调用方 2026-10-06 grep 复核 | signal：仍全零（见 env_15 §1），簿06 结论维持 | §1 史 向 |
| 4 | 三态裁定自审 | 挂起排期成立；D13-29/31 移交 env_15 | §3 |
