---
ttl: task_bound
title: L07-EXE6 子块挖矿簿 · 执行算法 TWAP/VWAP/IS（双层并存）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；新证四条（VWAP 时段丢弃语义 / 参与率自证 / 双参数优化器 / 六算法零 A 股微观结构）
---

# L07 · EXE-6 执行算法 TWAP/VWAP/IS

**① 职责一句话**：把"买 100 万股"这个意图切成一串**何时下、下多少、挂什么价**的子单，并在两套并行体系（评分驱动六算法 ∥ ADV 分档门禁）里决定用哪种切法——是执行成本的主要决定者。

**② 现状实测**

| 件 | 行 | MOD | 关键实测 | 触发面三态 |
|---|---|---|---|---|
| `ex_sor/core/algo_trading_engine.py` | 1,011 | XS-005（safety=**H**，stability=evolving，MATURITY=production，STARTUP=**manual**） | 六算法类：`TwapStrategy:435 / VwapStrategy:471 / IcebergStrategy:512 / PovStrategy:575 / ImplementationShortfallStrategy:646 / AggressiveLiquidityTakingStrategy:693` + `AlgoTradingEngine:749` + **`AlgoParamOptimizer:946`** | **覆盖未接电** |
| `ex_sor/core/algo_execution_selector.py` | 767 | XS-011 | 评分驱动选型；零 scorer 引用（SKEL 09-25 复核成立，本册不重复） | **覆盖未接电** |
| `ex_sor/core/execution_scheduler.py` | 701 | XS-004 | ScheduledChildOrder 优先级队列 P0-P3 | **覆盖未接电**（STARTUP=manual） |
| `ex_sor/core/optimal_order_router.py` | 460 | XS-001 | 三维评分路由 | **覆盖未接电** |
| `ex_sor/core/sor_agent.py` | 376 | XS-015 | Level 0 纯规则 + 滑点回写反馈 + replay | **覆盖未接电** |
| `ex_core` 门禁版（MOD-EX-062 + `order_splitter`） | — | — | ADV 分档表（<1% 限价直发 / 1-5% TWAP / 5-15% VWAP / >15% 拒） | 未在本册复核装配（SKEL 已立"双层并存零互认"，引用不重复） |
| 硬约束实码位 | — | — | `MAX_PARTICIPATION_RATE = Decimal("0.05")` :173、`MAX_ADV_FRACTION = 0.15` :175、`LOT_SIZE=100` :177；校验点：`AlgoParams.__post_init__` :246-252（participation_rate 越界 raise）、engine :865-873（adv_fraction>15% → `OrderTooLargeError` ZA-XS-0005-OL） | — |
| 真单事实 | — | — | `execution_report.algo_type` 恒 `"NONE"`，且全表 1 行（EXE-4 实测）→ **算法层从未有一笔真单通过**，与"零实弹"一致 | — |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：`MarketContext`（:181）要 `last_price / adv / bid_price / ask_price / volume_profile`；**`adv` 是唯一的流动性字段，`volume_profile` 是 4 档粗分布（§13.2 开盘20/上午25/午盘10/尾盘45）**——无逐时段市场成交量预测，因此"参与率"在切片层根本不可计算（见③向）。外部：待办。 |
| ②下游 | 内部：XS-005 产 `AlgoExecutionPlan`→XS-004→XS-001→XS-002 broker；`local_order_queue.py`（**MATURITY=draft**，271 行，切片缓冲）是链条中唯一非 production 件（EXE-2 G6 同条）。真实生产路径**绕过全部六算法**：文件桥 `submit_order` 单笔直投。外部：待办。 |
| ③算法/机制 | 内部四条本册新证：<br>**(a) VWAP 语义偏离**：`sorted(profile.items(), key=占比, reverse=True)[:n]`（:492-494）——当 `max_slice_count < len(volume_profile)` 时**直接丢弃低量时段后再按剩余权重归一**，结果=把本应摊到全天的量集中到少数高量时段，且总量守恒使偏差不显形。真正的 VWAP 跟踪应保留全时段并按占比分配（低量时段可置 0 但不该重归一化到高量时段以外）。`AlgoParamOptimizer` 给的 `max_slices = min(20, max(3, horizon//3))`（:984）→ horizon=15 时 n=3 < 4 档 → **默认参数即触发该偏离**。<br>**(b) IS 实现与自述标签不等**：权重 `w_i = exp(-λ·t_i)`（:663-669），rationale 自称"IS AC 轨迹切片"。AC (2000) 原文最优剩余库存轨迹是**双曲正弦比**（sinh 形式，随时间凹），指数衰减是其高 urgency 渐近形——低 λ（不紧急大单，正是 IS 最常用场景）时两者分布不同。本仓 §5 标准件已把"IsStrategy 切片公式逐项对表 AC 原文"列为合规义务，**该对表未做**（本册读到的实现体为 exp，非 sinh）。<br>**(c) 参与率=自证式约束**：`participation_rate ≤ 5%` 只在 `AlgoParams.__post_init__` 校验**输入参数**（:246），生成的 `list[AlgoSlice]` 从不回算"这套时刻表隐含的实际参与率"（无逐时段市场量可除，见①向）→ §10.1 监管硬约束在代码面上是"调用方说好就好"。<br>**(d) 六算法对 A 股微观结构零感知**：`grep -n "T+1\|涨跌停\|涨停\|集合竞价\|limit_up" algo_trading_engine.py algo_execution_selector.py` = **0 命中**（2026-09-26）；`_mid_price`（:730-734）在缺 ask/bid 时退化用 `last_price`，PASSIVE 挂中间价在涨跌停带上必然挂不到，且切片参考价未做 tick(0.01) 对齐（tick 对齐只在 EXE-2 `price_cage` 里，而桥路径笼子恒 UNKNOWN → **两处失配叠加**）。唯一有涨跌停裁剪的是 `rl_exec_boundary`（XS-008，design 态 RL 包裹层）——即"A 股适配"目前只长在一条尚未接电的 RL 边上。 |
| ④后端 | 内部：`Decimal` 全程 + `ROUND_DOWN` + `_distribute_evenly/_distribute_by_weights` 守恒（INVARIANT "切片数量和=订单总量"，:8）；`@dataclass(frozen=True)` 策略无状态可共享；"下单零重试（HB-07）"在头注层声明。外部：待办。 |
| ⑤前端 | 内部：无算法参数人工面板（`AlgoParamOptimizer` Phase 1 规则全在码内，改档=改码）；MINING 债：dashboard 侧是否有算法视图未查。外部：待办。 |
| ⑥数据字段 | 内部：算法层所需但系统当前无供的字段=**逐时段市场成交量预测**（participation 分母）、**日内量分布的标的级画像**（现只有全域 4 档常数）、**涨停/停牌/临停状态位**（切片时刻表须回避）。"字段在 ≠ 数据可得"反向成立：**字段根本不在模型签名里**（`MarketContext` 无 auction/halt 位）。外部：待办。 |

**④ 缺口清单**（本册新立；SKEL L07-C03 双选择器收口 / L07-C02 断链 / EXE-4 G6 parent_order_id 引用不重复）

| 编号 | 内容 | 级别 |
|---|---|---|
| **L07-S6-G1** | **VWAP 丢弃低量时段语义缺陷**（默认参数即触发，可单测钉住） | P1 |
| **L07-S6-G2** | **IS 轨迹公式未对表 AC 原文**（exp vs sinh），违反本仓 §5 标准件对表义务；对表结论须写进件内 PROVENANCE | P1 |
| **L07-S6-G3** | **参与率监管硬约束无闭环校验**：只校验输入参数，不回算时刻表隐含参与率；缺"逐时段市场成交量"分母 → 5% 上限不可证。合规面上这是"声称有闸、实际无闸"（与 EXE-2 C-GATE-01 同族：闸在、不作用）。 | **P0（合规）** |
| **L07-S6-G4** | **双参数优化器并存零互认**：`AlgoParamOptimizer`（XS-005 :946，Phase 1 规则，无 TCA 输入）∥ `ExecutionParamOptimizer`（MOD-EX-064，TCA 驱动 optuna/网格，零装配）——同域同名概念两套，且前者会静默给后者不认识的参数档位。SKEL §1 只记了"双选择器 / 双成本真源"，本条是**第三对双轨**。 | P1（内收 w5_1） |
| L07-S6-G5 | **六算法零 A 股微观结构适配**（涨跌停/集合竞价/T+1 全盲，见 §③(c)(d)）：TDM L4-14 注"IS/ALT 的 A 股 T+1/涨跌停改造欠账"是**论文级口径**，本册实测=改造面比该注更大（含 `_mid_price` 退化路径与 tick 对齐缺失）。 | P1 |
| L07-S6-G6 | **链条中间件 maturity 断层**：`local_order_queue` draft 夹在 production 之间；safety=H 件（XS-005）STARTUP=manual 且 `ai_autonomy=ai_modifiable` 并存——高安全件可被 AI 直改而无装配测试，门位口径不自洽。 | P2 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G3 | **施工 P0（可与 EXE-2 C-GATE-01 并批：同族"闸在而不作用"）**：先用 `volume_profile × adv` 造保守分母，把隐含参与率回算并入 `OrderTooLargeError` 同一错误族；分母不可得时 **fail-closed 降档**而非放行。 | 监管硬约束不容"信任输入"；sim 无事故不构成放松理由（禁以现状规模小封矿）。 |
| G1 | 施工 P1（纯函数级修复 + 单测钉住，零新件） | 语义错就是错，与是否接电无关；先修再接。 |
| G2 | **挂起排期**：解锁条件=按 §5 纪律取 AC 原文（dm13450 walkthrough 已在 §5 登记 URL）做逐式对表并留 PROVENANCE；对表结论可能是"exp 可接受 + 记偏差界"，故先对表再决定改不改，禁未对表先改公式。 | 本仓 MODIFY-GUARD 式纪律（数值即证据）。 |
| G4 | 挂起排期：解锁条件=并给 L07-C03（Owner 收口裁定）作输入——裁定"哪套选择器活"时必须同时裁定"哪套参数优化器活"，否则收编一半留一半。 | 同域收敛应一次做完（w5_1）。 |
| G5 | 施工 P1，但**排在真实单腿接算法之前**：改造点=`MarketContext` 加 auction/halt/limit-band 位 + `_mid_price` 在带内裁剪。 | 无这些位，算法接真钱即错单。 |
| G6 | 施工 P2（登记类，改 maturity 声明需 depgraph 同步） | 便宜且防"高安全件低门槛改"。 |

**③-bis 外部对表补录（统一外部轮，2026-09-26）**

| 论断 | 外部源（发布方+年份+URL） | 对本册判定的作用 |
|---|---|---|
| Almgren-Chriss 框架把执行摩擦分为**临时冲击（瞬时滑点）与永久冲击（中间价位移）**；最小化"期望成本+风险"目标化为线性 ODE，**闭式解为双曲正弦（hyperbolic-sine）轨迹**；风险厌恶系数 λ/τ→0 时退化为**均匀清算（TWAP）**，λ/τ 大时**前置加载** | EmergentMind（学术聚合站），更新于 2026-01-22 https://www.emergentmind.com/topics/almgren-chriss-market-impact-model ；二源=本仓 §5 标准件已登记 dm13450 求解教程（2024-06） | **G2 判定成立且升级为"外部确证"**：件内 `ImplementationShortfallStrategy` 用 `w_i=exp(-λ·t_i)`（algo_trading_engine.py:663-669），与 AC 闭式 sinh 形式**不同族**（指数是渐近形而非解）；且件内 TWAP 自称"λ=0 的 AC 特例"与外部口径**方向一致**（λ/τ→0 ⇒ uniform），故此条对 TWAP 无指控、只对 IS 有指控 → 裁定保持"先逐式对表再决定是否改公式"，不擅自改数 |
| A 股适配闸（T+1/涨跌停/散户主导/无做市商）在算法层的后果 | 本块未获权威外部二源（查法：本轮未针对"A 股算法交易参与率限制"另开检索，避与 EXE-2 已确证的监管条目重复占预算）→ **受阻如实记** | G5（六算法零 A 股微观结构）仍以**仓内实现体证据**为准，不外推业界 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | `ex_sor/core` 五件定位（**首查 `ls` 直接在顶层未命中，二次 find 才定位到 core/ 子包**）+ 行数/头注 | signal | SKEL §1 路径书写略去了 core/ 层，后续引用建议补全路径 |
| R2 | 六算法实现体（Twap/Vwap/IS 逐行 + price helpers） | signal | **G1/G2/G5 主证** |
| R3 | 约束实码位 grep（`MAX_PARTICIPATION_RATE/MAX_ADV_FRACTION` 全出现点 :173/:175/:246/:865/:929/:981） | signal | G3 主证（校验点全在参数层，无切片层） |
| R4 | `AlgoParamOptimizer` 正文（:946-985） | signal | G4 主证（第三对双轨） |
| R5 | A 股微观结构关键词零命中复证 | signal | G5 |
| R6 | 外部对表（VWAP 时段处理 / AC 轨迹闭式 / LEAN 执行模型语义） | **未做** | 推迟到统一外部轮；G2 尤其依赖此轮，故其裁定故意留"先对表再改" |

**本册封矿判据**：六向封口；XS-005 算法族实现体已逐行读到（六件里读完 3 件 + helpers + optimizer，其余 `PovStrategy/IcebergStrategy/AggressiveLiquidityTaking` 与 `execution_scheduler/optimal_order_router/sor_agent` 正文=长尾，已具名沿用 SKEL §3）；A 股适配闸与标准件对表义务两条判定已落到实现体层 → **判 MINING（三件正文长尾），核心结论封口**。
