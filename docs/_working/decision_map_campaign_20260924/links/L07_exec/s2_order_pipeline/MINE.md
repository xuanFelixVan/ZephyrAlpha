---
ttl: task_bound
doc_type: log
title: L07-EXE2 子块挖矿簿 · 委托管线（OMS + 预检闸 + 价格笼子）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口；外部对表标待办）；含 P0 级新证一条（C-GATE-01）
---

# L07 · EXE-2 委托管线（OMS + 预检 + 笼子）

**① 职责一句话**：把"已批准的动作"变成一笔**合规的**申报——五级执行前闸 + 九态订单机 + 价格笼子 + 撤单率/申报笔数合规计数 + 成交回补持仓，是所有下行的最后一道闸、所有回报的上行第一站。

**② 现状实测**（`src/zephyr/ex_core/` 十一件正文级实读）

| 件 | 行数 | MATURITY | 生产触发面（三态口径） | 实测要点 |
|---|---|---|---|---|
| `order_manager.py` | 600 | production | **已接电**（`trading_session.py:351` 装配） | MOD-L06-001；submit 前置挂 C-002 申报计数（cancel_rate_guard 头注 :41 自注"本批接线"） |
| `pre_execution_checker.py` | 351 | production | **已接电**（`trading_session.attach_pre_execution_gate` :513-543 装配 + `scripts/start_paper_session.py:565` 实调用带 kill_switch_probe） | 闸 1 KillSwitch(:233)→1.5 live 档阻断(:259)→2 交易时段(:279)→3 快照装配(:302)→4 风险否决(:316)；全 Fail-Closed |
| `price_cage.py` | 264 | production | **覆盖未接电（桥路径）／已接电（miniqmt 路径）** → 见 §④ C-GATE-01 | 板块表 :96-101（主板/创业板 ±2%+0.1 元兜底、科创 ±2% 无兜底、北交所 ±5% 无兜底）；未知板块回退主板（:104） |
| `cancel_rate_guard.py` | 295 | production | **已接电**（`trading_session.py:351` 实例化，A2 注释 :64 列 can_place_order/can_submit_now/record_submit） | 滚动 500 笔撤单率：>12% 降级"只挂不撤"、>15% 冻结全账户；内部限频 15 笔/秒；单日申报 >5000 预警 />1万 限交易（2026-06-08 新规，自然日滚动清零） |
| `fill_handler.py` | 499 | production | **已接电**（`aggregate_root_manager.py:156` 默认装配 + `scripts/run_post_settlement.py:273/:429` 盘后回放读数） | MOD-EX-001；SUBMITTED→PARTIAL→FILLED 驱动、fill_id 幂等、`DuplicateFillError` |
| `async_fill_dispatcher.py` | 391 | production | **已接电（paper 服务）**：`scripts/start_paper_session.py:358` | C++ 回调线程只 `Queue.put`，daemon 线程消费（实测坑：回调内耗时致回报延迟 3 秒） |
| `order_execution_saga.py` | 894 | production | **覆盖未接电**：全仓 grep `OrderExecutionSaga(` 非测试实例=**0**（2026-09-26，仅 `risk_validation_bridge.py:14` [TESTS] 与 `rejection_action_handler.py:5/:20` 头注引用） | 六步 Saga + 补偿回滚；"撤单返回 False 强制查终态、超时分支不吞成交"（:35-39，裁定书 §三 P0-2 修复）——**这套终态不吞单的先进逻辑当前无人在产使用** |
| `open_order_resolver.py` | 552 | production | **覆盖未接电**：grep `OpenOrderResolver` 非测试引用仅 3 处头注（"可选通道，Phase 1.5 装配批次接线"）+ 自身测试 | 未成交续接决策表（挂单>30s→Make-or-Take 切对手价重挂；PARTIAL 剩余<min_unit→转 CANCELLED；14:55 尾盘清退） |
| `position_reconciler.py` | 218 | production | 部分（`start_paper_session.py` 依赖清单列名，H5-P0 风控接线批） | — |
| `rejection_action_handler.py` | — | — | **孤儿**：`RETRY_ONCE / ALERT_FREEZE / ALERT_RECONCILE` 的"实际动作待 OrderExecutionSaga"（:20 原文）→ 与 saga 互为前提的双孤儿 | — |
| `three_way_reconciliation.py` | — | MOD-TRADING-013 | **覆盖未接电**（SKEL §2 EXE-2⑤ 已立"运行时装配批自注无装配实证"，引用不重复） | — |

**数据新鲜度**：本册未查 execution/订单实表行数（EXE-4 册查表，避重复）；`config\quarantine\qmt_trade_csv_quarantine_20260622\trade_stats.json:4` 记 `"price_cage_reject": 0`（**历史真实柜台回报统计里笼子拒单=0**，与"从未生效"结论方向一致，作旁证不作主证）。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：入参三源——动作（EXE-1）、`OrderRiskRequest`（risk 域）、`order_book`（miniqmt 实时盘口）；kill_switch 探针经 `DefaultRiskValidator.kill_switch_active` 自动反查（trading_session :526）。外部：待办。 |
| ②下游 | 内部：broker 适配器（`miniqmt_broker.py:836` 传齐 ask1/bid1/last/prev_close、`qmt_file_bridge_broker.py:616` 三参直调）、`execution_report_producer`（EXE-4）、`fill→position_tracker.apply_fill`、`compliance`（MOD-CMP-018 操纵冻结闸）。**关键不对称**：同一次 `check_price_cage` 调用在两条通道上语义完全不同——miniqmt 真校验+夹边，文件桥恒 UNKNOWN。外部：待办。 |
| ③算法/机制 | 内部：(a) 笼子基准价回退链=`ask1→last→prev_close`（`_resolve_base_price` :124-150，买入侧；卖出侧对称 bid1→last→prev_close）——**跳过对手方对侧价**：涨停封板时 ask1 为空，交易所口径应退到"即时揭示的最高买入价（买一）"，本实现直接退到最新成交价，两者在封板场景可差数分位→打板单基准价系统性偏。(b) 超限=**夹到边界不废单**（`was_clamped`+`clamped_price`，miniqmt :846-850 原地改写 `order.limit_price`），与交易所"直接废单"新规语义不同（SKEL 已注，本册补：夹边**无审计行落库**，只 `_logger.warning/info`，事后无法重建"哪几笔被改过价"）。(c) 集合竞价/临停/市价豁免"由调用方判断"——文件桥侧判断=只看 `order_type != MARKET`，无时段判定→**集合竞价窗内对限价单做连续竞价笼子**是潜在错杀面（配合 UNKNOWN 恒放行，实际不触发，一旦补盘口即暴露）。外部：待办。 |
| ④后端 | 内部：全部 `threading` + `deque` + `Decimal`，无 IO 依赖，`AppendOnlyDedupSet`（fill 幂等）与 `JsonStateStore` 是仅有的外部化件；`local_order_queue.py` MATURITY=**draft**（271 行，算法单切片缓冲）——draft 件在链路正中间，上游 production 下游 production。外部：待办。 |
| ⑤前端 | 内部：人工面=`scripts/start_paper_session.py`（--service 常驻）+ 仪表盘无委托管线专窗（本册 grep 未覆，MINING 债：`app_panel.py` 侧是否有订单簿视图未读）；`--verify-only` 是纯自检模式（:1237）。外部：待办。 |
| ⑥数据字段 | 内部：合规生存项所需字段=滚动窗口申报/撤单计数（本件自计，天然齐）、**盘口 ask1/bid1/last + prev_close**（miniqmt 通道齐；文件桥通道**一个都不传**）。"字段在 ≠ 数据可得"：柜台镜像 `CounterStateMirror` 有账户态无盘口，桥侧要拿基准价须另接 quote（EXE-3 wrapper 已有 quote mtime 闸，但那是**新鲜度闸不是基准价供给**）。外部：待办。 |

**④ 缺口清单**（本册新立；SKEL §4 L07-C01..C10 与 13 号文 TRD 项不重复）

| 编号 | 内容 | 级别 |
|---|---|---|
| **C-GATE-01** | **价格笼子在实际桥路径上恒为 UNKNOWN=静默不校验**：`qmt_file_bridge_broker.py:616` 只传 `(side, limit_price, symbol)`，`ask1/bid1/last_price/prev_close` 四参全默认 None → `_resolve_base_price` 必返 None → `status=UNKNOWN`、`clamped_price=limit_price`（原价直发）。头注注释自认"降级无盘口：UNKNOWN 原价通过"（:610）。后果=**唯一在产的申报通道上，2% 价格笼子合规闸零作用**，且无 warn 无落库（只有 CLAMPED 才 warn，而 CLAMPED 不可达）。属"同类静默丢失"家族中**监管面**的一条，与 LANE-BUILD 在办的两缺陷（隔夜单/撤单竞态）不重叠。 | **P0** |
| L07-S2-G2 | 笼子"夹到边界"与交易所"直接废单"的语义差**无审计痕迹**：`was_clamped` 不落任何持久化记录，仅日志。终局全貌下"哪笔单被系统改过价"必须是可查询事实（否则归因/TCA/审计三处都缺）。 | P1 |
| L07-S2-G3 | 基准价回退链缺 bid1（买一）一步（涨停封板场景），卖出侧缺 ask1（跌停封板），与交易所基准价定义不一致；且该缺步恰与 EXE-9 打板/逃命单场景重叠。 | P1 |
| L07-S2-G4 | **双孤儿件**：`order_execution_saga`（894 行，含"超时不吞成交"的终态保真逻辑）与 `open_order_resolver`（552 行，含 14:55 尾盘清退/Make-or-Take）皆 production-maturity 零非测试装配，且 `rejection_action_handler` 的三个动作显式"待 saga"（:20）→ 互锁挂起。终局全貌下这是执行层最贵的两块死代码。 | P1 |
| L07-S2-G5 | 撤单率冻结（>15%）与"只挂不撤"降级（>12%）**触发后无恢复路径实查**：自然日清零只覆盖申报计数，`CancelRateStatus` 的解冻条件（滚动窗口滑出？）未读实现体（MINING 债：本册未覆 :60-295 正文）。 | MINING 债（不立项，登记） |
| L07-S2-G6 | `local_order_queue.py`（算法单切片缓冲，链路中间件）MATURITY=**draft** 而两端 production—— maturity 口径不一致；且它是 EXE-6 算法层落地必需，与"算法层零实弹"（EXE-6 册）同因。 | P2 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| C-GATE-01 | **施工 P0**（接线型，不新增件）：桥路径须喂基准价（桥已有 quote 新鲜度闸可复用）或在无基准价时**fail-closed 拒单并计数**；无论哪种都先补"UNKNOWN 计数落库"，因为它同时是 EXE-3 回报断链的同类探针。 | 监管硬闸静默失效=闷声出事典型；不做"现状无事故"辩解（sim 阶段未爆≠不会爆）。 |
| L07-S2-G2/G3 | 施工（并入 GATE-01 同批，改同一函数族） | 同一处代码的三面，拆批必返工。 |
| L07-S2-G4 | **挂起排期**：解锁条件=(a) 单一 broker 通道收口（当前双通道语义分叉未收，装配 saga 会把分叉固化）；(b) 与 L07-C03 算法层收口同批——saga 的 step4"等 Fill 回调 timeout"与 open_order_resolver 的 30s Make-or-Take 在算法切片下会互相抢控制权，先定归属再装配。 | 终局必要；顺序依赖型挂起，非规模借口。 |
| L07-S2-G5 | MINING 债留档，不裁定 | 未读实现体不立项（零伪造纪律）。 |
| L07-S2-G6 | 挂起排期：随 EXE-6 算法层收口批一并定 maturity |  maturity 是结论不是工作。 |

**③-bis 外部对表补录（统一外部轮，2026-09-26）**

| 论断 | 外部源（发布方+年份+URL） | 对本册判定的作用 |
|---|---|---|
| 价格笼子基准价回退链四步：①即时揭示的最低卖出（最高买入）申报价 → ②**若无则取即时揭示的最高买入（最低卖出）申报价** → ③前一次成交价 → ④当日无成交则最近一交易日收盘价 | 上游新闻（条目转载于百科聚合站，未载具体日期）https://baike.quark.cn/baike?id=c3d3822aeda443b69ba4e4a6879c221c | **G3 由"本册推断"升为"外部确证"**：现行 `_resolve_base_price`（price_cage.py:124-150）缺第二步（买入侧无 ask1 时直接用 last_price 而非 bid1），涨停封板场景基准价取错，属实现与交易所定义不一致，非口径选择问题 |
| 全面注册制下越界申报的处理：由"订单暂存"改为**"直接拒单"** | 手机新浪网/财经网，2023-02-06 https://finance.sina.cn/2023-02-06/detail-imyetumr6340646.d.html | **G2 升为外部确证**：本仓"夹到边界不废单"与交易所"直接拒单"语义相反（SKEL 早注，本册补二源）；夹边还须与"拒单事实落库"配套，否则连"该单本应被拒"都查不到 |
| 《程序化交易管理实施细则》2025-07-07 起实施（件内引用之规的独立二源） | 经济日报，2025-07-08 http://m.ce.cn/gp/gd/202507/t20250708_2353701.shtml ；东方财富（新版《程序化交易委托协议》落地、高频投资者四项报告），2025-07-10 https://fund.eastmoney.com/a/202507103453647663.html | `cancel_rate_guard` 头注所引规约**存在性二源确认**；但"12%/15% 撤单率线"是**本仓自设保守垫**（头注自述），未见外部规定对应数值，不得当合规真值使用 |
| A 股适配闸三件（T+1 / 涨跌停 / 无做市商）在价格笼子侧的具体体现 | 同上两源（回退链与拒单处理均为交易所明示口径，散户主导市场由券商投教条目转载） | C-GATE-01（桥路径笼子在 2% 硬闸下静默放行）的**合规暴露面**由外部口径坐实，非仅本仓自证 |

**本项未能对外（受阻如实记）**：`pre_execution_checker` 五级闸与业界 pre-trade compliance 框架（如 SEC Rule 15c3-5 风控闸清单）的对表**未取得第二独立来源**（本轮检索未命中可用一手/权威二手页面），故不外推"业界都这么做"，仅保留仓内实证。

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | ex_core 11 件定位 + 头注 [MATURITY]/[DEPENDENCIES] 全表 | signal | 见 §② |
| R2 | 六件 docstring 正文（fill_handler/saga/cancel_rate_guard/open_order_resolver/async_fill_dispatcher/pre_execution_checker） | signal | 新规依据（实施细则 2025-07-07、程序化新规 2026-06-08）均在件内引用，属仓内既有论断非本册新增外部论断 |
| R3 | 装配面全仓 grep（`Xxx(` 实例化 + CONSUMERS 头注交叉） | signal | GATE-01 与 G4 双孤儿由此来 |
| R4 | 笼子正文 :88-200 + 两 broker 调用点比对 | signal | **C-GATE-01 主证** |
| R5 | 假设"rules/ashare 与 price_cage 双真源" | **noise（已否）** | 查法：读 `rules/ashare.py:30-57` → 实测 `price_cage_rule()` 直接委托 `_pc._get_cage_params`，单源无重复，**不立项**（记录否证过程以免重复怀疑） |
| R6 | 假设"BSE 缺笼子参数" | **noise（已否）** | 查法：`price_cage.py:101` BSE ±5% 在表，SKEL 口径正确 |
| R7 | 外部对表（OMS/pre-trade compliance gate 业界做法） | **未做** | 按轮次纪律推迟 |

**本册封矿判据**：六向封口（外部向统一标待办）；§③⑤ 遗留 MINING 债两条已具名（cancel_rate_guard 解冻条件实现体、app_panel 订单视图）；C-GATE-01 为**代码级直读证据**（非推断），可直接进施工队列 → **子模块判 MINING（正文级长尾已具名），主结论封口**。
