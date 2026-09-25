---
ttl: task_bound
doc_type: log
title: L07-EXE9 子块挖矿簿 · 卖出执行 X-S2 + 打板执行
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；含四件消费链实查结论（L07-C09 核查项就地销号）+ 三条新证
---

# L07 · EXE-9 卖出执行 X-S2 + 打板执行

**① 职责一句话**：在"必须卖、且卖得掉"两个约束下决定**什么时候卖、走哪个通道、分几笔、每笔多少**——卖出是唯一受 T+1 与跌停不可撤硬约束的执行方向，也是尾部风险的出口。

**② 现状实测（四件消费链实查，本册把 SKEL §2 EXE-9⑤/⑥ 的"未验"就地判死或销号）**

| 件 | 行 | MOD / MATURITY | **真实消费链（全仓 import 反查 2026-09-26）** | 三态判定 |
|---|---|---|---|---|
| `ex_sor/core/sell_session_router.py` | 339 | XS-016 / **design** | 除 `ex_sor/core/__init__.py` re-export + 测试外**零引用** | **覆盖未接电** |
| `sell_decision/core/sell_execution_planner.py` | 333 | MOD-SELL-019 / production | 除 `sell_decision/core/__init__.py` + 测试外**零引用**；[CONSUMERS] 自注的 "D-EX-CORE(40号执行层订单分解)" 与 "MOD-SELL-009" 均无 import 实证 | **覆盖未接电** → **SKEL L07-C09 核查项就此销号（答案=没人调）** |
| `position/core/t1_sellable.py` | 66 | MOD-POS-028 / production | **两条真实边**：`frontend/services/dashboard_feeds.py:66`（前端可卖额度展示）+ `position/core/intraday_position_constraint.py:47`（盘中持仓约束） | **已接电（约束面与展示面）** → 修正 SKEL "消费链未验（如实注）"：t1_sellable 不是孤儿，且其下游 `intraday_position_constraint` 由 `firm_risk_aggregator.py:13` 错误码注释侧证在册 |
| `ex_core/daban_execution.py` | 196 | MOD-EX / **production + SAFETY=H** | **零引用**（[CONSUMERS] 自注"首批实盘接线前暂无"） | **覆盖未接电**（H 级安全件却 STARTUP=imported、ai_autonomy 见头注） |

其他：`X-S2-01` 四路输入仲裁序（强清中断≥强裁>纪律强平>常规，D95 终裁）与 `D70/D71/D72` 流动性三查/IS 急卖 preset/ICEBERG 抖动**全在 TDM yaml 层**（SKEL §②已录原文口径，本册不重复抄），代码侧对应件即上表 XS-016/SELL-019，**均未接电** → "设计完备、执行裸奔"是本块主形态。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：卖出决策链 S2-02 限价→S2-03 时段路由→SOR 下单；紧迫度/仓位/流动性三输入（X-S2-01 路由表）。**外部：待办**。 |
| ②下游 | 内部：XS-016 的下游是 ex_sor SOR 链（整条链 STARTUP=manual，见 EXE-6 册）→ **即使把 XS-016 接电，它下游也是断的**；这是"接电顺序"约束而非缺口，但对 L07-C09 的裁定含义要写清：卖出侧接电的前置是算法层收口（L07-C03），不是 XS-016 本身。外部：待办。 |
| ③算法/机制（本册三条新证） | **(a) 打板 SaR 前置检查在空/缺失盘口时被静默跳过，且跳过方向是反保守**：`build_execution_plan` 用 `if order_book:` 守卫（:91），空 dict `{}` 与 None 同样为假 → **整段 SaR 削量逻辑不执行**；而件内 [ERROR_CONTRACT]（:14）与 `estimate_sar` docstring（:81）都声称"空订单簿→depth=0/concentration=0 兜底（保守方向）"——兜底只在**函数被调用**时成立，计划构造器根本不调它。文档承诺的 Fail-Closed 与实现路径背离，且背离方向=放行更大单量。<br>**(b) SaR 阈值量级使保护近乎恒不触发（可算证）**：`sar = (vol/max(depth,1))·(1+conc)·η`，η=`price_impact_eta=0.001`（:64），削减门槛 `sar>0.02`（:93）→ 需 `vol/depth > 20/(1+conc) ≥ 10`。即**下单量要超过可见五档买量的 10 倍才削 30%**；A 股打板是排队买入（vol 通常 ≤ 封单量），该条件实际不可达，"SaR>2%→削30%" INVARIANT 属**声明有闸、算下来无闸**（与 EXE-2 C-GATE-01、EXE-6 G3 同族第三条）。<br>**(c) 分笔量无整手对齐**：`int(target_volume*0.6)` / `int(*0.3)`（:98/:107）纯截断，件 [DEPENDENCIES]=**stdlib**（:5）→ 不引 `board_lot`/`LOT_SIZE`，产出的 batch qty 可能是非 100 整数倍；同域 XS-005 有 `LOT_SIZE=100`（EXE-6 册 :177）、EXE-2 桥侧有最小申报单位硬拒 → **三段分笔一旦接真单会在最后一米被拒**。<br>**(d) 打板与撤单率闸互不知情**：`cancel_timeout_sec=30`（:68，"30 秒未成交考虑撤单"）是打板重挂节奏参数，而 `CancelRateGuard` 滚动 500 笔窗 12%/15% 阈值（EXE-2 册）是全局闸；两者无引用关系。打板三段 × N 标的 × 30s 重挂=**撤单率天然高企**，实盘首个被冻结的会是打板腿，且冻结原因（算法节奏）与告警口径（合规计数）对不上，事后归因困难。外部：待办。 |
| ④后端 | 内部：四件均纯函数/纯数据结构（fail-closed 盘外恒 NO_ROUTE 在 XS-016 头注声明）；无 IO。外部：已查无（查法：本块四件无存储/并发面）。 |
| ⑤前端 | 内部：**t1_sellable 有真实前端面**（`dashboard_feeds.py:66`）——本环节唯一"人在看"的执行字段；卖出路由/分笔计划无人工确认界面（SELL-019 零消费，亦无 UI）。外部：待办。 |
| ⑥数据字段 | 内部：XS-016 时段窗口表所需字段=深市 14:57 后集合竞价不可撤旗标、竞价逃命单 9:15 窗、14:30-14:45 跳水窗——件内是**常数窗口表**（design 态），未接 `pretrade_quote.trading_phase`（该字段**已在 EXE-3 册实测存在**：`now_trading_phase()` 可判）→ **接电成本低、可派生**：时段路由可直接吃现成 phase 字段，这是本块最明确的"零成本增量"。跌停侧：`is_sealed_limit_down`（EXE-3 册实测）同样是现成件，XS-016 未消费。外部：待办。 |

**④ 缺口清单**（本册新立；SKEL L07-C09 核查型→本册已就地销号，L07-C07/打板域界归属引用不重复）

| 编号 | 内容 | 级别 |
|---|---|---|
| **L07-S9-G1** | 打板 SaR 空盘口静默跳过 + 阈值量级近恒不触发 + 分笔无整手对齐（同一件三病，可一批修，含"文档承诺与实现路径背离"） | **P0**（接实弹前置） |
| **L07-S9-G2** | **打板节奏与撤单率合规闸无联动**：`cancel_timeout_sec` 类节奏参数不感知全局撤单率状态，合规冻结触发时算法侧无退让分支（"只挂不撤"降级应由算法侧显式遵守，而非在提交处被拒） | P1 |
| L07-S9-G3 | **卖出链现成字段未接**：XS-016 时段判定可用 `now_trading_phase()`/`is_sealed_limit_down()` 现成件派生，却仍是常数窗口表 + design 态；本条是"挂起"结论的反例——不是所有卖出侧工作都要等算法层。 | P1 |
| L07-S9-G4 | **H 安全级件零装配无休眠裁定**：`daban_execution` SAFETY=H、MATURITY=production、零消费、无 PROVENANCE（参数全默认值，对比 EXE-7 的 MODIFY-GUARD/PROVENANCE 纪律）→ maturity=production 与"无消费方"并存=口径失真（与 EXE-2 G4 双孤儿同类，本条是其中的 H 级实例，风险更高） | P1（登记类，Owner 知情） |
| L07-S9-G5 | **打板成本假设与 EXE-7 实测冲突未回写至可行性口径**：STR-DABAN-022 用 `slippage fixed 1bp + impact none`，而标定给 Q1_illiquid=7.24bp（**低估至 1/7.2**）→ 打板预期收益含 6.2bp 的系统性乐观；本册不重做成本模型，只要求打板可行性结论必须带该偏差标注（真源=EXE-7 S7-G1/G2）。 | **P0（口径标注，非施工）** |
| L07-S9-G6 | 四论文参数（Passive MI λ(d)=λ₀e^(−κd)、SaR、Hawkes 长记忆核、扩散悖论）均为件内自述 arXiv 编号，**引用可核性未做外部验证**，参数亦无标定；本册按"仓内论断"处理，不作外部依据引用。 | MINING 债 + 外部对表待办 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 | **施工 P0**（纯函数级三修：`order_book is None or not order_book` 显式分支改为"缺盘口→保守削量或拒绝出计划"；η/阈值重标或改相对深度定义；batch qty 过 `board_lot`） | 打板是 L07 唯一"高滑点+高冲击+不可撤+散户对手盘"四叠加方向，终局全貌下它必然要接电；现在把三修做掉，成本是三行代码 + 三个单测。 |
| G2 | 挂起排期：解锁条件=XS-016/daban 任一接电（接电即需感知 `CancelRateGuard` 状态），或提前把 guard 状态做成只读探针供算法侧查询 | 顺序依赖，但探针可先做（可与 EXE-4 G3 观测批并）。 |
| G3 | **施工 P1**：把 XS-016 的时段/封板判定改为消费现成 phase 件 | 零新增件、可派生、同真源——按内收 w5_1"同真源可派生→必并"，这是**该做**而非"等裁定"。 |
| G4 | 施工 P2（登记 + maturity 口径校正提案；不擅自退役） | "零触发零消费→退役"是内收判据，但 H 级件退役需 Owner 门位（§5 high 域），本册只登记不裁。 |
| G5 | 施工 P0（文档口径，随 EXE-7 批走） | 不修就把 6.2bp 乐观带进可行性判断。 |
| G6 | **挂起排期**：解锁条件=外部对表统一轮（arXiv 编号可核性 + 被动冲击实证量级）；核不实则件内引用降为"待证注释" | 禁凭模型记忆断言业界做法，亦禁替件内引用背书。 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | 四件定位（分属 `sell_decision/core`、`position/core`、`ex_core`、`ex_sor/core` 四包）+ 头注身份 | signal | SKEL §1 未标 `sell_execution_planner` 在 sell_decision 域，路径易误判为 ex_core |
| R2 | 全仓 import 反查（四件逐条） | signal | **L07-C09 就地销号** + t1_sellable 已接电（修正 SKEL） |
| R3 | `t1_sellable → intraday_position_constraint → firm_risk_aggregator` 链追 | signal（链到聚合器注释层止） | 聚合器是否真调约束件未再深（越界 risk 车道，主动止） |
| R4 | `daban_execution` 正文（:59-110 + 常量 :62-68 + INVARIANTS/ERROR_CONTRACT） | signal | **G1 三条主证**（含可算证的不触发条件） |
| R5 | XS-016 所需字段 × 现成 phase 件比对（借 EXE-3 册实测） | signal | G3（低成本可接） |
| R6 | 打板成本口径交叉（EXE-7 册 S7-G2） | signal | G5 |
| R7 | 外部对表（SaR/Passive MI/Hawkes 四论文 + 打板/涨停业界做法） | **未做** | 推迟；G6 因此留挂起 |

**本册封矿判据**：六向封口；四件消费链已实查到 import 级（L07-C09 核查型就地闭环，不留悬案）；打板件实现体已读关键区（构造器+三常量+SaR）；长尾=`sell_session_router`/`sell_execution_planner` 正文（各 333-339 行，本册未逐行）、`42 号 memo §3.7/3.8`、`XS-016 blueprint` → **判 MINING（两件正文未逐行），消费链与打板件判定封口**。
