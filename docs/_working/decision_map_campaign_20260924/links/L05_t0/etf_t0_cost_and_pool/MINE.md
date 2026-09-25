---
ttl: task_bound
doc_type: audit_report
title: L05 做T · ETF 做T线成本与池过滤矿（逐只实测 vs 档位代理的口径冲突）
created: "2026-09-26"
sid: st-qmine-20260925
lane: L05 个股做T（深挖车道，只读挖掘+写文档）
family_id: L05-T0-ETF-COST-POOL
executes: SKEL.md §5 D4 / §7 L05-C06 的缺口面
inputs:
  - docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §三.4（每只成本独立实测／池=近 60 日日均成交额 top100 起／30 对门槛）
  - docs/_working/archive/2026-09/bizmine_night/etf_t0_retest/etft0_prereg_card.md（ETFT0-SCREEN，frozen 宇宙规则）
  - docs/_working/archive/2026-09/bizmine_night/etf_t0_retest/etft0_screen_report.md（三宇宙勘测结论）
  - src/zephyr/backtest/core/cost_model_calibration.py:173-197（ADV 五分位与档位滑点真源）
---

# ETF 做T线成本与池过滤 · MINE

## ① 职责一句话

把 T0-ETF 立卡前的两个"必须先有数"的东西钉死：**每只 ETF 自己的成本（佣金腿与价差腿分列）** 和 **池子怎么按近 60 日日均成交额选出来**——判清现有 ETFT0-SCREEN 已经给了什么、还差什么，防止拿"档位代理成本"冒充"逐只实测"过关。

## ② 现状实测

**数据面（2026-09-26 只读探针，min/max(trade_date)+count，零全表扫）**

| 表 | 日期范围 | 行数 | 关键列 |
|---|---|---|---|
| `c1_market.kline_etf_1min` | **2021-07-01 → 2026-09-24** | 5,515,451,992 | 21 列，`open/high/low/close/volume/trade_time`；**无 `amount` 列** |
| `c1_market.kline_etf_60min` | **2005-02-23 → 2026-09-24** | 12,487,426 | 22 列，含 `amount`+`pre_close` |
| `c1_market.kline_etf_daily` | 2021-03-08 → 2026-09-24 | 170,831,204 | 24 列，含 `amount`+`pre_close` |
| 对照：个股 `kline_1min` | 2021-09-01 → 2026-09-24 | 1,485,679,943 | 21 列，同样**无 `amount`**；个股 `kline_15/30/60min` 均有 `amount`（22 列） |

- 新鲜度：ETF 三表全部到 2026-09-24（探针日 2026-09-26 ⇒ T-1/T-2 级，采集在产）；`last_mod` 2026-09-25~26。
- ETF 1min 起点 2021-07-01 **早于**研究语料窗起点 2021-09-01 ⇒ 分钟面 ETF 语料与研究窗完全交叠（无 D5 缺口）；D26（`kline_etf_60min` 四段缺约 9 万 bar）仍在，但 60min 历史深度到 2005 年 ⇒ "60min 不够"这一旧叙事需按 §⑦ 实测改写（L05-ET-G1）。
- **成交额维度分叉**：ETF **分钟面无 `amount`**、日线与 60min 面有 ⇒ "近 60 日日均成交额"只能在**日线/60min** 上算（口径合法），但任何"分钟面按成交额分桶/量能闸门"在 ETF 上不可直算（个股同病，见 L05-PA-G03）。

**成本面（本矿主战场）**

- CST-T0-001 个股口径构成（真源 `scripts/audit/cost_trio_exam.py:56` 与文件头 :8）：`RT_COST_BP = 31.2 = 佣金双边 6 + 印花 5（卖侧）+ 过户双边 0.2 + 滑点 2×10`，且"最低佣金 5 元地板抬升不计入固定口径，单独披露列"。
- ETFT0-SCREEN 实际用的**不是** 31.2bp：`etft0_screen_results.csv` 列头含 `adv_yuan,tier,slip_bp,rt_bp,threshold_bp`，样本行 `589090,Q4,4.0,11.708,16.742` ⇒ 往返成本 ≈**11.7bp**，来源=`cost_model_calibration.py` 的 ADV 五分位档位口径（`TIER_TICK_BPS=(8.783,9.170,7.915,6.940,4.140)`，:196）。
- ⇒ **仓内已并存两套 ETF/高波资产往返成本口径（31.2bp 个股固定 vs ≈11.7bp 档位代理），且两者相差 2.7 倍**；17 §三.4"每只 ETF 成本独立实测（佣金+价差分列）"正是这条分叉的收口要求，而"独立实测"件目前**不存在**（`grep` 全仓无 per-symbol ETF 成本实测件；档位口径不分列佣金与价差）。
- 佣金地板纪律的下游缺位（直接引用 `cost_model_calibration.py:5` 原话）："地板佣金「最小单量」纪律当前以产物侧披露+告警兑现（cost_attribution），**策略侧下单规模硬约束尚无消费者**——勿凭本行臆断已有"。
- 池过滤面现状：ETFT0-SCREEN 的宇宙=**frozen 关键词分类**（宇宙 A 行业/主题 top10、B T+0 类 100 只、C 高波个股 top20，卡 §2），**不是** 17 §三.4 的"近 60 日日均成交额 top100"；结果长表 1,023 行虽带 `adv_yuan`，但排名口径是"宇宙内关键词/振幅"，未做过全 ETF 宇宙的 ADV 降序选池。
- 生产触发面：**无**。`etft0_screen.py` 是一次性勘测脚本，且其产物住在 `docs/_working/archive/2026-09/bizmine_night/etf_t0_retest/`（含 `.json` 结果件，与 docs/_working 目录契约的"禁 .json"条款冲突——L05-ET-G6 登记，不改他人件）。T0-ETF 正式卡未立（SKEL §5 D4 ③ 写"新卡接续编号"，`links/L05_t0/rule_cards/` 现仅 r01~r04 四张个股卡，无 ETF 卡）。

## ③ 六向台账

**①上游（还有什么信息该喂进来）**
- 内部反查：ETF 独有的三条应喂而未喂——(a) **IOPV/折溢价**（`market_etf_share_snapshot` 仅 2026-09-18 一天，SKEL C-F6 6.3 已判"日频 `etf_nav` 禁顶替日内"）；(b) **申赎清单/份额变动**（`kline_etf_*` 之外是否有 `etf_share` 面未普查）；(c) 费率结构（管理费/佣金差异→属静态属性，需登记不属考试数据）。
- 全网搜索：本向已查无（查法=Crossref `query=ETF trading costs bid-ask spread premium discount intraday`；未取到可直接替换"逐只实测"的公开标准实现条目，不硬造引文）。

**②下游（输出还该喂给谁）**
- 内部反查：ETF 成本实测台账的消费方=①T0-ETF 预注册卡的 E4 verdict；②P2-02 调度池（做T 标的池需按成本分层，跨境/债券 ETF 是"允许更小实现边际也划算"的场所，SKEL §5 D4 ④）；③`cost_model_calibration` 的档位滑点若能被逐只实测**校准**，则回灌全部回测成本面（`matching_logic.resolve_slippage_bps`、`vectorized_engine` 默认口径，见其头注 CONSUMERS 列）。
- 全网搜索：已查无（同上查法，见 §③①）。

**③算法/机制**
- 内部反查：`cost_model_calibration.py` 已有可复用件——`floor_drag_bps(notional, commission_rate, min_commission)`（:430）、`notional_for_floor_drag_bps`（:447）、`commission_floor_nonbinding_notional`（:463，注释给出"现结构 ≈ ¥58,548"）⇒ **"佣金腿实测"不需新框架**，缺的是每只 ETF 的 `commission_rate/min_commission` 输入与价差腿观测。
- 全网搜索：待补（本矿外部向只做了 Crossref 一轮，命中的是通用交易成本条目、无 ETF 逐只价差实测标准，判"单源不足→不入图"）。
- 关键待核外部论断（**本矿未取到权威源，如实挂"待验证"，禁当既成事实引用**）：A 股 ETF 是否免印花税/免过户费（若免，则 31.2bp 中的 5.2bp 对 ETF 属结构性高估，"逐只实测"的数值会低于个股口径；方向保守但**口径错配**）。解锁=监管文本双源核（上交所/深交所费率表 + 结算机构费率公告），属 Owner 门位可判的口径变更，AI 不自裁。

**④后端（代码侧缺什么）**
- 内部反查：缺三件，全部小件——(1) ETF ADV top100 选池件（可复用 `cost_model_calibration` 的 ADV 五分位边界做分层，但需"近 60 交易日窗口"滚动排序；数据=有 `amount` 的日线/60min，禁在分钟面硬算）；(2) 逐只成本实测件（佣金腿=券商费率表输入，价差腿=见 ⑥）；(3) 与 CST-T0-001 的关系声明件（ETF 用独立口径后，做T 判据族里"净=毛−31.2"这条对 ETF 是否成立，须在新卡里显式写死，禁临场替换）。
- 全网搜索：已查无（同③）。

**⑤前端（只登记不施工）**
- 内部反查：`etft0_screen_results.csv`（1,023 行长表）是唯一呈现面，属一次性勘测；无仪表盘消费。登记：逐只成本台账呈现=新卡交付物的一部分，不自造呈现层。

**⑥数据字段（要什么/有吗/质量画像）**
- 佣金腿字段：**不在库**（券商费率是账户属性非市场数据）⇒ 属"Owner 终局必做四类事"里的 API/账号侧输入，非本仓可自采；解锁条件=费率表以机器可读形式登记（一次性）。
- 价差腿字段：真实买卖价差只在 `c1_market.tick_depth_5`（五档，实测 2026-07-24→2026-09-24 且 2026-07/08 仅 52 行，见 `tick_imbalance_material/MINE.md`）⇒ **ETF 逐只价差实测在研究窗内结构性无料**；退而求其次的代理=分钟面 `high-low` 或收盘竞价价差，均是**近似**、须标"非实测"。这是本矿最硬的结论：17 §三.4 的"价差分列实测"与现有 tick 保留窗（约 1 个月滚动）直接冲突（L05-ET-G3）。
- ETF 宇宙规模未实测（`uniqExact(symbol)` 需扫表，本车道让路 LANE-T0 未跑）——列长尾；`kline_etf_daily` 有 `pre_close` 可做涨跌幅/涨跌停适配（ETF 涨跌停 ±10%，跨境 ETF 无涨跌幅限制问题须单核，A 股适配闸项）。

## ④ 缺口清单（新登 `L05-ET-G*`，在册映射见末列）

| 编号 | 缺口 | 归属 |
|---|---|---|
| L05-ET-G1 | "D26=60min ETF 深度缺口"旧叙事与实测不符：`kline_etf_60min` 覆盖 2005-02-23→2026-09-24，四段缺口的**段界与量级**未复核 | 承 L05-C13（D26） |
| L05-ET-G2 | 仓内并存两套 ETF 往返成本口径（31.2bp 个股固定 vs ETFT0-SCREEN ≈11.7bp 档位代理），相差 2.7 倍，无收口件 | **DU 类（同对象异口径）** + 承 L05-C06 |
| L05-ET-G3 | "价差分列逐只实测"与五档保留窗（约 1 个月且全在闭卷段）结构冲突：研究窗内不可得 | 承 L05-C13（D36）/L05-C08 |
| L05-ET-G4 | 佣金腿输入不在库（券商费率），且佣金地板纪律**无策略侧消费者**（`cost_model_calibration.py:5` 自陈） | LK 类（接线缺位，既有在册） |
| L05-ET-G5 | 17 §三.4 要求的"近 60 日日均成交额 top100 选池件"未建；ETFT0-SCREEN 的宇宙=frozen 关键词，两者不可互相顶替 | 承 L05-C06 |
| L05-ET-G6 | ETF 分钟面 `amount` 缺失 → 量能/成交额维在分钟不可算（与 L05-PA-G03 同源，跨个股/ETF） | 取数画像项 |
| L05-ET-G7 | A 股 ETF 印花税/过户费豁免论断**未取权威双源**（若成立则 31.2bp 对 ETF 口径错配） | CNS/Owner 门位项 |
| L05-ET-G8 | T0-ETF 正式卡零存在（`rule_cards/` 仅 r01~r04），且旧勘测产物含 `.json` 与目录契约冲突（不改他人件，只登记） | 承 L05-C06 |

## ⑤ 自审闸三态裁定

**裁定=施工（限三小件）+ 一项挂起排期，不封矿。**

- **施工**：L05-ET-G5（ADV top100 选池件）、L05-ET-G2（成本口径收口声明件）、L05-ET-G1（D26 复核）——三件全是"机器可判的数"，消灭的是"人工凭旧叙事判 ETF 能不能做T"，且都是 L05-C06 立卡的硬前置；口径**一个不改**（31.2bp/30 对/30bp 前置照抄，ETF 若用新成本必须走新预注册卡显式声明）。
- **挂起排期**：L05-ET-G3（价差逐只实测）解锁条件明写=①`tick_depth_5` 具备 ≥1 个研究窗段连续覆盖，或 ②Owner 裁"以分钟面近似代理 + 明标非实测"降级方案。G4 佣金腿解锁条件=费率表机器可读登记（Owner 账号/API 侧）。G7 解锁条件=监管双源核 + Owner 门位。
- **不封矿**：本矿 ②⑥两向仍在出发现；长尾=ETF 宇宙规模实测、`etf_share`/申赎面普查、跨境 ETF 涨跌停适配。
- 反驳者一问（对"是否现在就为 ETF 立分钟规则卡"）：(a) 高波宇宙勘测已给出振幅经济学可行性（宇宙 B 中 13 只跨境簇绿区、最优 req_cap 0.195），继续立卡顺理 → **但勘测报告自己的诚实条款写明"不是净边际为正的证明"，且用的是 11.7bp 口径**，成本口径未收口就立卡=把最贵的一环跳过；(b) ETF 无 T+1 约束困扰（真 T+0）→ 成立，正是终局价值所在；(c) 复用 r01 网格即可 → 成本口径不同则判据不可比，**先收口后立卡**，故本矿裁定维持"三小件施工 + 立卡待前置"。

## ⑥ 挖矿日志

| 轮 | 矿脉 | 动作 | 判定 | 产出 |
|---|---|---|---|---|
| R1 | ETF 三表覆盖 | CH 只读 min/max(trade_date)+count | signal | ETF 1min 起点 2021-07-01（早于研究窗）、60min 深达 2005、分钟面无 amount |
| R2 | 成本真源对表 | 读 `cost_trio_exam.py:8,29-32,56` + `cost_model_calibration.py:173-197,430-463` | signal | 31.2bp 构成含印花 5bp；档位口径与地板佣金件可复用 |
| R3 | ETFT0-SCREEN 现状 | 读 prereg 卡 §1/§2 + 报告首段 + results 表头（1,023 行） | signal | 宇宙=关键词 frozen 非 ADV top100；rt_bp≈11.708 与 31.2bp 分叉（G2） |
| R4 | 五档可否支撑价差实测 | 承 `tick_imbalance_material` R2/R4 探针（复用不重跑） | signal | 研究窗内五档 0 行 ⇒ 价差实测结构性不可得（G3） |
| R5 | 生产触发面 | 目录/grep 反查 ETF 成本件 | 已查无（阴性=结论） | 无 per-symbol ETF 成本件、无 T0-ETF 卡 |
| R6 | 外部：ETF 成本标准做法 | Crossref 一轮（ETF trading cost spread premium discount） | 已查无/单源不入图 | 未取到可引标准件；印花税豁免论断如实挂"待验证"（G7） |
| R7 | 未做（长尾） | ETF 宇宙 `uniqExact(symbol)`、`etf_share`/申赎面普查、跨境 ETF 涨跌幅适配 | 移长尾（让路 LANE-T0，不跑重扫） | 交接后继 |
