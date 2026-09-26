---
ttl: task_bound
doc_type: audit_report
title: L05 做T · tick 盘口失衡材料线矿（一档/五档盘口料与闭卷窗交集实测）
created: "2026-09-26"
sid: st-qmine-20260925
lane: L05 个股做T（深挖车道，只读挖掘+写文档）
family_id: L05-T0-TICK-IMBALANCE
executes: SKEL.md §4 C-F5 5.1/5.4 与 §5 D5 的缺口面（34 法"不可卡化排除项"的材料侧）
inputs:
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/t0_state_match_readme.md §4（排除清单：5.4=tick 面）
  - docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §三.1/§三.5（周期集无 tick；闭卷切点 2025-09-09）
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/SKEL.md §4 C-F1（1.4 被动队列）/C-F5/C-F3（3.5）
---

# tick 盘口失衡材料线 · MINE

## ① 职责一句话

判清"盘口失衡（一档/五档 OBI、3s 微观动量、大单失衡）"这条 tick 面矿脉**到底有多少料、料落在研究窗还是闭卷窗、字段够不够算失衡**，从而决定它是"挂起等料"还是"结构性不可考"——不许按 SKEL 的旧口径含糊带过，也不许用日频代理造料。

## ② 现状实测（2026-09-26 只读探针，`DatabaseService().get_clickhouse_conn()`）

**盘口真表有两张，字段面完全不同（SKEL 未逐列核对过）**

| 表 | 列数 | 盘口字段 | 日期范围 | 行数 | 月连续性 |
|---|---|---|---|---|---|
| `c1_market.tick_data` | 18 | **一档**：`bid_price/ask_price/bid_volume/ask_volume` + `direction`（成交向）+ `price/volume/amount` | **2025-01-02 → 2026-09-24** | 8,953,174,466 | 21 个月逐月 3.16亿~5.04亿行，**无断月** |
| `c1_market.tick_depth_5` | 33 | **五档**：`bid_price1..5/ask_price1..5/bid_volume1..5/ask_volume1..5`（无 `direction` 列） | **2026-07-24 → 2026-09-24** | 103,510,134 | 月分布：2026-07=**48 行**、2026-08=**4 行**、2026-09=≈1.035 亿行 |

- 时间字段三件套与时区（实测类型）：`timestamp DateTime64(3,'Asia/Shanghai')` / `recorded_time DateTime64(3,'UTC')` / `ingest_ts DateTime64(3,'UTC')`，`trade_date Date`。→ 同一行内**两个时区并存**，故 tick 时区纪元核验（真源施工项=**L05-C08**，SKEL §7 表）有明确字段靶：需裁"哪个字段=交易所撮合时刻、哪个=本地落库时刻"，以及 `trade_date` 由哪个字段派生。SKEL §4 的 3.5/5.4 两行把该前置写成"L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7）"，而 §7 的 L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7）=个股条件维立卡 → **SKEL 自相矛盾**（登 L05-TK-G7）。
- **研究窗/闭卷窗交集=本矿最硬的事实**（SKEL 与 17 号文均未写过）：tick_data 起点 2025-01-02，研究语料窗=[2021-09-01, 2025-09-09]（`t0_material_line.py:60-61`）⇒ tick 面**可用于研究段的只有 2025-01-02→2025-09-09 ≈ 165 个交易日**（2025-01~09 六月度合计 2,905,199,107 行；按 17 §三.5 切点后的 2025-09-10→2026-09-24 ≈ 200+ 交易日全部属闭卷段，禁入研究）。
- 五档面：研究窗（≤2025-09-09）内 `tick_depth_5` 行数=**0**（表最早 2026-07-24）⇒ 五档 OBI（法 5.1）在研究窗内**结构性无料**；且现存料几乎全在闭卷段（2026-09），2026-07/08 的 48+4 行=残点测试料，须按质量画像隔离。
- SKEL 口径偏差登记（宪法 §4.3 文档矛盾=事故）：§5 D5 写"tick_data（2 年偏牛市）"、C-F1 1.4 写"五档仅 14 日"、C-F5 5.1 写"tick_depth_5 14 日/D36"。实测=一档 21 个月（跨 2025+2026 两个年度，不是"2 年"）、五档为"2026-09 单月 + 52 行残点"。**五档交易日数与 SKEL 的 14 日不一致，须复核 `uniqExact(trade_date)`**（本车道未取该数，避免与 LANE-T0 争 CPU）。
- 生产触发面：tick **采集侧在产**（数据新鲜到 2026-09-24≈T-1，`last_mod` 2026-09-25）；tick **信号侧零接线**——全仓无 OBI/盘口失衡特征件（grep `bid_volume|ask_volume|imbalance` 在 `src/zephyr/{security,trading,strategy}` 与 `scripts/backtest/` 无消费件；`t0_material_line.py:66-72` 取数 SQL 只取 8 列、只读 `kline_1min`）。P2-02 的 `orderbook-imbalance` 策略身份=proposed（SKEL §2 A2 ③），且 5.1 OBI 与之"同族须强制消融"（A2 ⑥）。

## ③ 六向台账

**①上游（还有什么信息该喂进来）**
- 内部反查：`tick_data.direction`（成交主动性向）+ 一档量 → 可做 **signed volume imbalance / L1 OFI 代理**，此列从未被任何做T 件读取（`grep direction` 在 scripts/backtest 零命中）；`quality_flag UInt8` 语义无字典（L05-TK-G5）；`market_type/exchange` 可补板别维（现仅由 `board_limit_bp` 按 symbol 前缀判，`t0_material_line.py:75-86`）。
- 全网搜索：OFI/OBI 的一阶定义与"未成交订单流的跨日价格影响"两篇可考——Yagi 等《Impact of High-Frequency Trading with an Order Book Imbalance Strategy on Agent-Based Stock Markets》, *Complexity*, 2023, https://doi.org/10.1155/2023/3996948；Zhu 等《The Inter-Day Price Impact of Unfilled Order Imbalance in the After-Hour Fixed-Price Trading》, SSRN 4513622, 2023, https://doi.org/10.2139/ssrn.4513622。二者**均未给出可用 A 股一档口径**⇒ 只作定义族旁证，方法入图状态=待验证（另需第二独立源）。

**②下游（输出还该喂给谁）**
- 内部反查：盘口失衡材料的天然下游有三个且都不是分钟矩阵——(a) 执行域（07 链路，法 1.1/1.4 已划归执行域，不占做T 判据族）；(b) P2-02 三策略之一 `orderbook-imbalance`（yaml:2867-2907，confidence=proposed）；(c) 法 3.5"收盘大单失衡反转"（SKEL C-F3，卡在"tick 时区纪元核验"——真源前置=**L05-C08**，SKEL §4 该行误写 L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7），见 L05-TK-G7）。⇒ 本材料线**不该也无法进 `t0_state_match_matrix`**（17 §三.1 周期集={1,5,15,30,60}min 无 tick 档），排除清单登记正确，但排除理由需从"不可卡化"升级为"研究窗仅 165 日 + 五档零料"的可核事实（L05-TK-G1）。
- 全网搜索：OBI 类信号在业界的下游=执行时机与短周期 alpha 合成（Dong《Deep Reinforcement Learning for Optimizing Order Book Imbalance-Based High-Frequency Trading Strategies》, *Journal of Computing Innovations and Applications*, 2024, https://doi.org/10.63575/cia.2024.20204）。A 股适配闸：该文场景为连续竞价+可做市商环境，A 股 T+1 下"当日买入不可当日卖"⇒ 做T 必须动底仓，失衡信号只能用于**已持底仓**的减增，属适配后可用（改造方案=沿用 M0 的同日两腿配对语义）。

**③算法/机制**
- 内部反查：capability_lookup 面=`t0_*` 三引擎无 tick 通道；`c1_market.tick_data` 的仓内既有消费者是数据集成器/校验侧（`src/zephyr/data/implementations/ch_tick_kline.py:8` 的 OHLCV 口径铁律"open=argMin/close=argMax/volume=Δsum"，Δ 增量口径"负值=新快照重置，sumIf 过滤"）→ **盘口量在 tick 表里是"存量还是增量"必须先定口径**，一档 `bid_volume` 与 5 档 `bid_volume1..5` 的口径是否同源未核（L05-TK-G4，属"字段在≠可用"的典型）。
- 全网搜索：Cui 等《Decomposing High-Frequency Order Flow: Commonality and Idiosyncratic Trade Imbalance》, SSRN 6535019, 2026（https://doi.org/10.2139/ssrn.6535019）→ 提示"共同订单流分量"存在：个股盘口失衡需对大盘/板块同期失衡取残差，否则与相位轴（B4 六段）共线 ⇒ 矩阵的 `phase × tick_imbalance` 格有**内在共线风险**（L05-TK-G6）。

**④后端（代码侧缺什么）**
- 内部反查：缺三件——(1) tick→一档失衡特征件（无）；(2) tick→分钟重采样件（`ch_tick_kline.py:19,78` 已实现 tick→`kline_1min`/`kline_5min` 的**生产写入侧**，研究侧若要 3s 微观动量须复用禁重写）；(3) 闭卷硬拦在 tick 面**缺位**——`enforce_closed_book`（`t0_material_line.py:338`）只服务分钟线，tick 面若有人开跑没有同款闸门（L05-TK-G2，本矿最可施工项）。
- 全网搜索：已查无（查法=Crossref `query=tick data timezone exchange timestamp China A-share`，无 A 股时区条目）——记录为"外部无标准可引"，非"业界都这么做"。

**⑤前端**
- 内部反查：盘口料无任何呈现件（`src/zephyr/frontend/dashboard/api_server.py` 无 tick 失衡消费）。已查无外部惯例（查法=未做，判为向无矿：呈现依赖信号存在，信号不存在时呈现无对象）。
- 登记边界：五档深度/队列位次可视化属执行域（07 链路），本矿不越界。

**⑥数据字段（要什么/有吗/质量画像）**
- 一档 OBI 所需字段=**齐**（bid/ask 价量 + direction + amount）；五档 OBI 所需字段=**齐但研究窗零行**（结构性不可得）。
- 质量画像三项实测：①21 个月无断月（好）；②2026-02 仅 3.16 亿行/14 交易日、2026-06=3.19 亿/21 日（**月度不均衡，须按日均而非月总量判覆盖**）；③五档 2026-07/08 合计 52 行=异常残点，任何"取全表最早日期"的窗口逻辑会被其污染（L05-TK-G3）。
- 覆盖度未测：单日多少 symbol 有 tick（全市场 or 抽样）——本车道未跑，列长尾。

## ④ 缺口清单

| 编号 | 缺口 | 性质 |
|---|---|---|
| L05-TK-G1 | 排除清单的"5.4 不可卡化"理由未量化为"研究窗 165 交易日 / 五档研究窗 0 行"两条可核事实 | 文档口径项（不改判据） |
| L05-TK-G2 | tick 面**无闭卷硬拦**：`enforce_closed_book` 仅覆盖分钟线，未来任何 tick 研究件默认会吃到 2025-09-10 之后的 200+ 日闭卷料 | 施工候选（≤40 行复用件） |
| L05-TK-G3 | `tick_depth_5` 52 行 2026-07/08 残点 + 2026-09 主体料未做隔离字典（`quality_flag` 无字典） | 数据质量项（取数面） |
| L05-TK-G4 | 一档/五档 `*_volume` 是挂单存量还是增量未核（对照 `ch_tick_kline.py:8` 的"Δ 增量口径"铁律只覆盖 `volume/amount`） | 口径核验项，**盘口失衡公式的前置** |
| L05-TK-G5 | `direction`/`market_type`/`exchange` 三列零消费者且无字典 | 字段画像项 |
| L05-TK-G6 | 盘口失衡与六段相位的共线性未登记（若日后入轴，须与相位轴做残差化，否则矩阵格虚增显著性） | LK 判读纪律项（承在册 **LK-05** 消费链接线纪律 + 自由度≈1 悬案） |
| L05-TK-G7 | SKEL §4 的 3.5/5.4 两行把 tick 时区前置写作 **L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7）**，而 §7 定义 L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7）=个股条件维立卡、**L05-C08** 才是"tick 时区纪元核验" | CNS 项：SKEL 自相矛盾，交总指挥对齐（本矿不改 SKEL） |
| L05-TK-G8 | SKEL §5 D5"tick 2 年偏牛市"与 C-F5"五档仅 14 日"未复核即引用；2026-09-26 实测=一档 21 个月（2025-01-02→2026-09-24）、五档几乎全落 2026-09 ⇒ **在册 D36 的"~1 月保留窗每晚一天少一天"已实质恶化到"只剩一个月滚动料且整段在闭卷窗内"**（L05-C13 的"D36 时间敏感建议提级"获实测支持） | CNS 项 + **提级依据**（承 L05-C13） |

## ⑤ 自审闸三态裁定

**裁定=挂起排期（主）+ 一项小施工（L05-TK-G2）。**

- 五档 OBI（法 5.1）=**挂起排期**：终局要（做T 真到执行层必须有盘口），现在无料（研究窗 0 行）。解锁条件明写：①`tick_depth_5` 连续覆盖 ≥1 个研究窗段（即历史回填或研究窗右移，两者都属 Owner 门位的语料决策）②L05-TK-G4 口径核过 ③队列位次可观测性（法 1.4 的死因）不解决则只能做"失衡→短期价移"不能做"增益归因"。
- 一档失衡/3s 微观动量（法 5.4）=**挂起排期**：料在（165 交易日），但 165 日 vs 30 对土规 × 相位×周期×板块族多维展开→绝大多数格必 INSUFFICIENT；且 17 §三.1 周期集不含 tick 档，要进矩阵须**改判据=Owner 门位**。解锁条件=时区纪元核验（L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7））过 + 单独立卡（另走预注册，不与 R01~R04 混批）。
- L05-TK-G2（tick 闭卷硬拦件）=**施工候选**：纯防呆复用件，消灭的是"未来某个 tick 研究默认越闭卷线"的人工审计环节，属终局必需要素，工时极小。
- **不封矿**：本矿六向中④⑥两向仍在出发现（覆盖度、日均不均衡、存量/增量口径），长尾已列（见 §⑥ 日志未做项）。
- 反驳者一问（对"要不要现在就立 tick 卡"）：(a) 165 日撑不起任何状态维格 → 成立，故只允许"不分维"的边际分布考试；(b) 时区未核验即跑=结果全废 → 成立，故 L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7） 是硬前置；(c) 62bp 成本绞肉机已实证判死 tick 独立信号（SKEL §0.4）→ **决定性反证**：即便有边际信号也过不了 31.2bp 成本线，除非落在转债 1~8bp 成本族（C-F7）。故本矿对**个股** tick 只维持"材料线可核 + 挂起"，不立卡、不造料；盘口失衡的真价值出口指向转债/执行域（另矿/另链路）。

## ⑥ 挖矿日志

| 轮 | 矿脉 | 动作 | 判定 | 关键产出 |
|---|---|---|---|---|
| R1 | 盘口表定位 | `system.tables` LIKE 'tick%' + `system.parts` 交叉 | signal | 真表=tick_data(18 列) 与 tick_depth_5(33 列)；SKEL 引用的"表名级"线索需重核 |
| R2 | 字段与日期范围 | `system.columns` + `min/max(trade_date)` + `count()` | signal | 一档 2025-01-02→2026-09-24 / 89.5 亿行；五档 2026-07-24→2026-09-24 / 1.035 亿行 |
| R3 | 时区/类型 | `system.columns` type 面 | signal | 同行两时区（Asia/Shanghai 与 UTC），L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7） 有字段靶 |
| R4 | 覆盖连续性 | `toStartOfMonth` 分组计数（21+3 月） | signal | 一档无断月；二档月不均衡；五档 52 行残点污染"最早日期"逻辑 |
| R5 | 与 SKEL/D5 口径对表 | 读 SKEL §5 D5 / §4 C-F1/C-F5 | signal（矛盾登记） | L05-TK-G7 |
| R6 | 外部 OBI/OFI | Crossref 2 轮（order book imbalance price impact / 高频订单流分解） | signal（≥3 题录，均有 DOI+发布方+年份） | 全部单源→标"待验证不入图"；A 股适配闸逐条过 |
| R7 | 生产触发面 | grep `direction|bid_volume|imbalance` 于 src/+scripts/ | 已查无（阴性=结论） | 信号侧零接线 |
| R8 | 未做（长尾） | 单日 symbol 覆盖度 / 五档 `uniqExact(trade_date)` / `quality_flag` 取值分布 | 移长尾（禁与本车跑重扫，让路 LANE-T0） | 交接 L05-C08（时区纪元核验；SKEL §4 两处误作 L05-C11，见 L05-TK-G7） 或后继车道 |
