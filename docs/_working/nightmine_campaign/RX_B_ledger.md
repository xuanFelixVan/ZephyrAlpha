---
ttl: task_bound
title: RX-B 交叉复挖车道台账（夜矿战役 st-nightmine-20261010）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: RX-B
family_id: NIGHTMINE-CAMPAIGN
scope: L5 离场族 / L6 组合族 / L7 知识层 已收口车道的 20% 交叉复挖
---

# RX-B 交叉复挖台账（11 节点，逐节点三态留痕）

## 〇、复挖判据与口径（开工先钉，禁凭记忆）

- 漏矿的**唯一合法来源** = `config/trading_decision_map.yaml` 该节点原文（decision_question /
  algo_note_zh / factor_refs / data_refs / ai_autonomy 注 / fallback / invalidation）里**写了、
  但对方现有卡未考**的判据性陈述。对方长尾自陈里的项**不自动等于漏矿**——长尾=可挖但超出本卡范围，
  漏矿=节点原话已给判据却零卡覆盖。本车道只对后者负责，前者计入"长尾属实/不属实"。
- "未考"的判定含卡库全量 grep（不只看被复挖节点的卡目录），并区分 `generated: true` 骨架件
  （`status: empty`=未冻结禁考，**不构成判据覆盖**）。
- 阻塞复核（③向）= 独立实测：CH 覆盖窗+行数一律走 `scripts/backtest/fexam/ch_data.py::ch_query_df`
  （禁裸 duckdb）；代码/件存在性走 ls + `python -m zephyr.library.lookup "<kw>" --limit N`
  （工棚版无 `state` 子命令，按 mining_sop §7.5 降级手工阶梯并留痕）。
  空结果先判静默失败：本车道用**同形控制查询**（同库同 system.tables 形状、返回 8 行）排除静默空。
- 零新增是合格交付；硬凑=污染覆盖尺与 DSR 分母。
- 未改动对方任何既有卡的一个字节；未执行任何 git 写操作；未跑生成器；未改注册表/TDM/分数册。
  临时件仅 `.runtime/tmp/st-nightmine-20261010/rxb_probe.py`、`rxb_probe2.py`。

## 一、三态总览（11 节点：漏矿 7 节点出 10 卡 / 复挖零新增 4 节点 / 翻案 2 项）

| node_id | 车道 | 三态 | 一句话结论 |
|---|---|---|---|
| TDM-X-FLOW | L5 | 复挖零新增（六向已尽） | terminal+aggregation 节点自陈"只承载结构与指向，不写机制不存实时数据"，唯一可判陈述（整链总账+R1 横切增量）已在 02 卡三臂与门柱中 |
| TDM-X-R1-01 | L5 | **漏矿 1 张** | 节点原文"与六段情绪的市场轴正交"零卡覆盖；L5 收尾 §六 自己点名请求该交叉复挖（重复计价风险）——已立 ablation/03 |
| TDM-X-S1-04 | L5 | **漏矿 2 张** | D68"除权除息参考价分母…否则除息日误判核按钮清仓"、D69"时段可靠性系数（早盘假信号高发窗）"两句节点原话无卡；情绪退潮 blocked 经复测维持 |
| TDM-X-S2-02 | L5 | **漏矿 2 张 + 翻案 1** | ①"可卖额度=t1_sellable 核对（当日买入不可卖）"全战役卡库零命中；②D71 新股首日"开盘 4 成/冲高出 4 成/留 2 成"配比无卡；③翻案：新股首日分支被 L5 记为"日内时段数据受限"而挂起，实测日线 OHLC+list_date 即可定价，改判可考 |
| TDM-F-C1-02 | L6 | **漏矿 1 张** | decision_question 前半"按置信度配比当日资金（如 5:1:1:1:2）"无卡——grep 仅命中 `generated:true` 骨架件（status: empty=未冻结禁考），02 卡五臂不含此臂 |
| TDM-F-C2-02 | L6 | **漏矿 2 张 + mined_out 被推翻** | 该节点自报 `mined_out=是（六向齐）`，但 algo_note_zh"过哪层裁哪层，按非策略仓优先裁"只在 02 卡 signal_derivation 里被提及、从未成为被检验的臂；D85 资金侧四句（先卖后买/买入额度公式/只削买入不削卖出/逆回购互斥）卡库 grep"先卖后买"零命中 |
| TDM-F-C3-01 | L6 | **漏矿 1 张 + mined_out 被推翻** | 自报 `mined_out=是`，但 algo_note_zh 正文第三句"加做T vs 持仓盈亏二分、IS 三分解（延迟/冲击/机会成本）"grep"三分解"零命中，02 卡只考了 D84 的第①句 |
| TDM-E-L9-A01 | L7 | 复挖零新增（长尾属实） | 决策问题两句由 02（截面 20 日动量）/03（分钟 RV）分答；PIT 句"复权因子禁进 PIT 窗"已由 position_flow P1-01/02 复权口径双臂卡覆盖（同域重复簇，禁双计）；自报长尾（隔夜跳空/周月频反转）节点未给数值判据=真长尾 |
| TDM-E-L9-A06 | L7 | 复挖零新增（长尾属实） | 三条阻塞断言逐位复测命中；"主力/大单"两档由 02 卡主列+备用列各跑一版覆盖，北向半问由 03 卡 blocked 覆盖；长尾（席位 1152 日/融资 505 日）非节点原文判据=真长尾 |
| TDM-E-L9-B03 | L7 | 复挖零新增（整表缺失成立） | 三词库筛=空且同形控制查询返回 8 行（排除静默失败）；馆查"招聘"→no results；半问"行业景气"判为 02 卡 target 面设计缺口（同一张不存在的表再挂一张 blocked 卡=凑卡污染覆盖尺，故不立） |
| TDM-E-L9-D1 | L7 | **漏矿 1 张 + 翻案（部分）** | 02 卡 blocked_on_data 的**理由**含两处不实子断言（node_verdict 有 window_start/window_end 且 5 行跨 2019-04-01..2026-09-11；strategy_screen 有 169 行 oos_tested），但结论维持——真实阻断原因是轨道身份无列承载（model 414 行全为 qwen3:8b）；节点原话"验证必交考试链"可即时证伪而零卡 → 立 ablation/03 漏斗闭环率 |

计数：**漏矿节点 7 / 复挖零新增节点 4 / 新卡 10 张 / 翻案 2 项**（7+4=11）。

## 二、逐节点复挖留痕

### 2.1 TDM-X-FLOW（L5，TDM:L168-194）
- ①已覆盖判据：02 卡（ablation）三臂 no_exit/full/exit_plus_risk + total_gain_floor/risk_layer_increment/
  turnover_cost_gate/tail_guard，已覆盖节点 algo_note_zh 全部可判内容（含"应急保命 R1 横切"→exit_plus_risk 臂）。
- ②原文逐句对表：`node_type=aggregation`、`red_reason=terminal`、algo_note_zh 自陈"本节点只承载结构与指向，
  不写机制不存实时数据"；`decision_question` 后半"什么时候卖"的执行时点属 X-S2-03（该节点已独立出卡）；
  `strategy_mounts` STR-VREV-001 的"家族替身证据…卡级独立回测未跑"=血缘注记非判据；
  `battle_map_refs`/`purpose_tag`/`materiality`=索引字段。**无漏矿。**
- ③无阻塞卡（02 卡 status=preregistered）。
- 结论：复挖零新增，六向已尽——理由一句：终点结构节点不写机制，故除整链总账外无可判陈述，而总账已入卡。

### 2.2 TDM-X-R1-01（L5，TDM:L3726-3764）→ 漏矿 1 张
- ①已覆盖：02 卡（comparison）考"五级表 vs 单一全清 vs 无迟滞"，阈值/迟滞/危机不缺席/换手成本门柱齐；
  梯度 80/60/40% 已入 arm_protocol；`invalidation` 的 fail-closed 近似已披露。
- ②漏矿（节点写了、卡没考）：
  - **"判定轴=组合日盈亏+组合回撤双轴，与六段情绪的市场轴正交"**（algo_note_zh 第一句）——正交性是一个
    带明确反例（重复计价）的可证伪命题，零卡覆盖。L5 收尾 §六 交叉复挖建议第 4 条原文即点名
    "TDM-X-R1-01（与 C 流预算带跨流交叉：同一减仓量在预算带内的重复计价风险）"，对方自认未挖。→ 新卡 03。
  - 次级漏矿（登记未立卡，附理由）：`fallback: 状态判定数据断流→维持当前级别不降级（fail-closed，D103）`
    与 `risk_limit_refs` 4 条（RLM-KILL-SWITCH-006/004、RLM-KILLSW-005/003）。前者属工程可靠性面（需注入断流
    夹具，无市场数值面），后者属阈值册引用面——判为真长尾不立卡，理由=二者无可判的行情数值面，硬立即凑卡。
- ③阻塞复核：02 卡 `data_window_evidence` 记 `account_nav_daily 仅 5 行`（本车道未复测该表，非本卡阻断项）。
  新卡 03 的体制轴载体**实测存在**：`c1_backtest.regime_snapshot_history` 2019-04-01..2026-10-09 / 1824 独立日 / 3635 行；
  节点原文命名的"六段情绪轴"**实测无载体**（见 §四.2 争点裁决）→ 该半面在卡内写死 blocked_on_data。
- ②下游向核实（非漏矿，已由他会话承接）：节点 `ai_autonomy` 注 M-36/D112 写死
  "全系统'熔断禁加期'统一定义=R1-01 状态机 L1 及以上持续期间（P3-01 资格门④消费本节点输出）"。
  本车道**未代建**该消费侧卡（属 position_flow/P3 节点集，越界代建违反作业簿第一节），
  并在 07:54 复验时观察到并发会话已就同一判据立项
  （`docs/03_modules/_domain_backtest/exam_cards/position_flow/P3/TDM-P-P3-01__comparison__04_日亏熔断禁加期分层对照.yaml`）
  ⇒ 该面判为"已入他卡/正在入卡"，不计入本车道漏矿，亦不重复立卡。

### 2.3 TDM-X-S1-04（L5，TDM:L3951-3989）→ 漏矿 2 张
- ①已覆盖：02 卡=突破失败 K 计数（含情绪退潮路 blocked_faces 披露）；03 卡=席位净卖出派发，
  其桶 3"三日榜净卖出<0 且占当日成交额>5%"已覆盖节点"优先三日榜"这句 → **该句不算漏矿**（复挖认定已覆盖）。
- ②漏矿：
  - `ai_autonomy` 注 **D68 必改**："除权除息日卖出口径——溢价率/跳空判定分母改用除权除息参考价
    （除息缺口是价格规则调整非下跌，否则除息日误判核按钮清仓）"——含失效机制与方向断言，卡库 grep"除息"零命中。
    → 新卡 calibration/04。载体实测：`c3_fundamental.ex_dividend_event`（`dr`=除权参考价）1991-03-11..2026-09-24、
    57,864 行、5438 标的，逐年 dr 非空率 100% → **无断供，可 preregistered**。
  - 同注 **"时段可靠性系数——早盘 9:30-10:00 假信号高发窗（开盘 5 分钟波动为全天 4 倍）破位确认从严…尾盘从宽"**
    ——两个可判面（量级断言"4 倍"+时段单调），卡库 grep"早盘|时段可靠|9:30"零命中 → 新卡 comparison/05。
    载体实测：`c1_market.kline_1min` 2021-09-01..2026-10-09、1,493,285,247 行，列含 trade_time/OHLCV →
    时段档可算（另卡另窗，沿用 L5 对 X-S1-02 分时档的成例，本卡 IS 内缩至 2021-09-01 并声明牛段不可考）。
  - 登记未立卡（真长尾）：D69 的肯定面"影线穿越不算、反视为洗盘持有加分"——其否定面已被 02 卡
    signal_derivation（收盘判定）结构性吸收，肯定面属"洗盘加分"的独立正向断言，判为长尾非漏矿。
- ③阻塞复核（情绪退潮路）：**维持 blocked_on_data**。`c1_backtest.decision_daily` 实测
  2026-09-16..2026-10-12、uniqExact(trade_date)=9、rows=138（与 L5 台账数字逐位吻合）；
  `c1_market.emotion_index.stage` 实测枚举=close_final 8617 / pre_open 27 / auction 17 →
  L5 的"快照阶段标记非情绪六段"断言**成立**（见 §四.2，此处 L5 对、L7 V2 卡错）。

### 2.4 TDM-X-S2-02（L5，TDM:L4114-4153）→ 漏矿 2 张 + 翻案 1
- ①已覆盖：02 卡=连续跌停天数 N 分档次日开板概率（含"第 2 日割肉非最优/约 43% 第 3 日开板"待考数字、
  放量/缩量处置分支）；stk_limit 2015-01-05..2026-10-09/9,254,772 行由本车道复测一致。
- ②漏矿：
  - `algo_note_zh` 正文第二句 **"可卖额度=t1_sellable 核对（当日买入不可卖）"** + `ai_autonomy` 注
    "做T仓例外语义（42号§3.8）"——全战役卡库 grep"可卖额度|t1_sellable" **零命中**，
    即 A 股卖出流最基础的制度约束在整套考试体系里无人考 → 新卡 comparison/04。
  - `ai_autonomy` 注 **D71 ①新股首日卖出状态机**："社区分层：开盘出 4 成冲高出 4 成留 2 成"
    （本节点唯一给出具体配比的行动判据）+"首日仅限价单市价申报废单/主板首日竞价限发行价±20%"
    → 新卡 calibration/03。
  - 登记未立卡（真长尾）：D71 ④碎股整单废单+科创板 200 股基准（执行可行性面，无市场数值面）。
- ③**翻案（附实测数字与命令原文，见 §四.3）**：L5 在 02 卡 blocked_faces 写
  "新股首日/临停复牌/风险警示板分支的日内时段数据同样受限"。复挖判定：
  - **新股首日分支不阻断**（改判可考并立卡）：三档卖点（开盘价/当日最高/当日收盘）在日线 OHLC 上即可定价，
    不需日内序列；新股宇宙可全历史重建——`c1_market.stock_basic` list_date 1990-12-10..2026-09-30（带
    valid_from/valid_to 版本轴，2015 段 count=372,254 为版本行，须 uniqExact(symbol) 去重后方可报票数）；
    发行价面 `c3_fundamental.ipo_calendar` list_date 2023-08-21..2026-10-09、11,176 行（含 issue_price/exchange）
    ⇒ 仅"发行价相对约束"子面局部阻断（缺 2015..2023-08 段），已在新卡内分列而非整体挂起。
  - **临停复牌分支维持阻断**：`c1_market.suspend` 实测 2026-09-04..2026-09-23、rows=36（约 20 日窗）。
  - **盘口面维持阻断**：`c1_market.l2_tick` 实测 count()=0；`tick_depth_5` 实测 2026-07-24..2026-09-30、
    130,146,982 行（与 L5 数字逐位吻合）→"越早排越前"的排队位次判据仍不可考，L5 判定正确。

### 2.5 TDM-F-C1-02（L6，TDM:L4378-4400）→ 漏矿 1 张
- ①已覆盖：02 卡=冠军三层栈 vs 四挑战者（ALC-THREELAYER/EQUAL/RK08/PA015/SIG131）影子对拍，
  绑 `allocator_shadow.run_shadow` 真实基建（本车道 ls 实测该件存在）。
- ②漏矿：decision_question 前半 **"激活集内按置信度配比当日资金（如 5:1:1:1:2）"**——
  五臂中无任何"按置信度配比"臂；卡库 grep"5:1:1|置信度配比"仅命中
  `TDM-F-C1-02__shadow.yaml`（`generated: true`、`status: empty`，判据门柱留空）→ 骨架件不构成覆盖。
  → 新卡 shadow/03（并含"高集中度配比与 C2-02 约束栈相互抵消量"的交叉读数，回应本车道对组合层的重复计价警觉）。
- ③无阻塞卡。`kline_daily_hfq` 2018-01-02..2026-09-30/9,061,473 行/5822 标的由本车道独立复测，
  与 L6 台账数字**逐位吻合**。Owner 面披露：本卡只出判据，冠军晋升/production 流转属 Owner 保留面，未执行任何动作。

### 2.6 TDM-F-C2-02（L6，TDM:L4527-4566）→ 漏矿 2 张，**mined_out=是 被推翻**
- ①已覆盖：02 卡=六层约束栈整体"有栈 vs 无栈"，buckets 含"哪层裁/未过栈"、secondary 含各层裁剪贡献；
  MOD-POS-021 firm_risk_aggregator 在册。
- ②漏矿（L6 记"六向齐、缺什么已穷尽"，但下列两句节点原话无卡）：
  - `algo_note_zh` 第二句 **"过哪层裁哪层，按非策略仓优先裁"**——该句在 02 卡里只作为
    signal_derivation 的实现细节出现（"post_kelly_clip 按比例削，非策略优先级截断"），
    **从未成为被 A/B 检验的臂**（裁谁 vs 裁多少是两个独立判据）→ 新卡 shadow/03。
  - `ai_autonomy` 注 **D85 资金侧四句**："本地维护可用/可取/冻结三态模拟账本与券商镜像；聚合产物**先卖后买**排序；
    买入额度=期初可用+当日计划卖回款−在途买单冻结−预扣费；**额度不足只按比例削买入不削卖出**；
    与现金 sleeve 逆回购互斥"，并 D101"卖出资金 T+0 回转可用；计划不算数防透支"、D106 交易日化口径。
    卡库 grep"先卖后买" **零命中**；持仓侧约束栈有卡、资金侧约束无卡 = 结构性缺口 → 新卡 shadow/04。
- ③阻塞复核：`kline_daily_hfq`（close/volume）双段齐（复测同 02 卡）；真实成交台账
  `sim_trade_log` 仅 84 行（2026-07-17..2026-10-09）→ 资金态不得用真实流水校验，卡内已写死并改由装置账本内建模拟。
  `firm_risk_aggregator` 的裁剪优先级/资金开关是否可注入未经读码确认 → 两卡均标 blocked_on_impl 并注明缺什么
  （禁以"跑不了"改判枯竭，mining_sop §3 结构判据）。

### 2.7 TDM-F-C3-01（L6，TDM:L4640-4682）→ 漏矿 1 张，**mined_out=是 被推翻**
- ①已覆盖：02 卡=D84 第①句（T+1 隔夜漂移切账 vs 不切账对升降级失真）+ brinson_consistency；
  MOD-PF-007 已落码（承接 L6 读码结论）。
- ②漏矿：`algo_note_zh` 正文第三句 **"加做T vs 持仓盈亏二分、IS 三分解（延迟/冲击/机会成本）"**——
  卡库 grep"三分解" **零命中**；02 卡未考二分、未考三分解的**可加闭合性**。该节点被承诺回答"钱从哪赚的亏到哪了"，
  而分解不闭合=这句话为假 → 新卡 comparison/03（主判据=三块之和对 IS 总缺口的闭合误差 <= 20% +
  最大块占比 >= 30% + 二分解释力 >= 95%）。
- ②b 判定不双计（重要，防污染覆盖尺）：D84 第③句"归因侧复权口径——账本存不复权价+复权因子
  （禁存前复权快照防全历史重写漂移）"确为节点写了、C3-01 卡没考，但**同判据已由 position_flow 车道
  `TDM-P-P1-01__comparison__02_复权口径对成本与生死线触发对照` 立为三臂卡**（A_hfq/B_raw/C_adj_corrected，
  事件集=adj_factor 跳变日；本车道复测 `c1_market.adj_factor` 1990-12-19..2026-09-24/2,105,507 行，载体充分）。
  按 mining_sop §4 同域重复簇收敛唯一 → **不另立卡**，仅记入本台账移交（若需归因侧专属读数，
  应由 P1-01 卡扩臂而非新建同判据卡）。D84 第④句孤儿成交 suspense、第⑤句现金贡献（GC001）
  由 L6 自行登记的长尾/TDM-F-C1 预备金卡覆盖，判真长尾/已在他卡。
- ③阻塞复核：`kline_daily_hfq` close/open/high/low/volume 双段齐（复测同 02 卡）；
  机会成本块需"被裁信号"留痕，装置未见该面 → 标 blocked_on_impl 子项并注明近似构造义务。

### 2.8 TDM-E-L9-A01（L7，TDM:L4981-5006）→ 复挖零新增（长尾属实）
- ①已覆盖：02 卡=20 日动量横截面（含过热反转辅读数、右端滞后 7 交易日披露）；03 卡=分钟 RV+偏度。
  决策问题"价量趋势与动量能否预测 N 日收益"两句由两卡分答（02 卡 target.note 明写"本卡答 N=1 与 N=3"）。
- ②原文逐句对表：`algo_note_zh` 其余内容均为源线供给语义/在册描述（DS 锚、U3 频率=daily、时滞=hours、
  挂接密度最高线、"数据本体按 DS/CH 真源引用不在地图复制条目"）——非判据；
  **PIT 句"K线落定不修订，复权因子禁进 PIT 窗"** 是节点写了的判据，但同判据已由 P1-01/02 复权口径卡覆盖
  （§2.7b 同一内收判定，禁双计）→ 不立卡。
- ③数据断言复核：**逐位命中**——`kline_daily_hfq` 1990-12-19..2026-09-30、10,098,785 行（=A01/L5 两车道报数）；
  `kline_1min` 2021-09-01..2026-10-09、1,493,285,247 行（=A01 报数）；`kline_index` 右端 2026-10-09（滞后关系成立）。
- 长尾核实：自报"隔夜跳空、分钟非同步跳动、周-月频动量反转未立卡"——节点原文未给任何 N 值/跳空阈值判据，
  属"节点未写的泛化项" → **真长尾**（非漏矿）。
- 结论：复挖零新增，六向已尽——理由一句：该源线节点的两句决策问题已由两卡分答，PIT 判据在他节点已入卡，余者非节点原话判据。

### 2.9 TDM-E-L9-A06（L7，TDM:L5112-5137）→ 复挖零新增（长尾属实）
- ①已覆盖：02 卡=残差化主力净流入截面（防共线门柱+"raw_vs_resid_gap"读数+备用列
  super_large/large_net_inflow_pct 各单跑一版 ⇒ "主力/大单"两档均在卡面）；03 卡=北向时序 blocked_on_data。
- ②原文逐句对表：`algo_note_zh` 其余=供给语义；PIT 句"日度聚合盘后落定不修订"同 A01（他节点已入卡，禁双计）。
  表列实测 `money_flow` 含 main/super_large/large/medium/small 五档净流入及 _pct 列（18 列）——
  medium/small 两档未入卡，但节点原文只写"主力/大单"，故 medium/small 属"节点未写"=真长尾。
- ③阻塞复核：**三条断言全部独立命中，数字逐位吻合**——
  `hk_connect_flow` 2014-11-17..**2024-08-16**、4052 行（断供终点正确）；
  `northbound_hold_snapshot` 2024-09-30..2026-06-30、**uniqExact(trade_date)=8**、57,458 行；
  `money_flow` 2021-01-04..2026-10-09、1225 日、5,993,328 行。
  ⇒ L7 该节点的"IS 可算/OOS 截断"非典型形态描述成立，03 卡 blocked 无翻案空间。
- 长尾核实：自报"dragon_tiger_seat 1152 日长史=下一富矿；margin_trading 505 日融资余额未挖"——
  本车道复测 margin_trading 确为长表（L7 报 2024-09-02..2026-10-08/505 日/2,100,709 行），但
  **A06 节点原文未写任何关于席位或融资的判据陈述**，二者属下游消费面（L2 板块/L3 选股/X-S1-04 席位）
  → **真长尾，非漏矿**（若在此立卡=跨节点越界代建）。

### 2.10 TDM-E-L9-B03（L7，TDM:L5476-5501）→ 复挖零新增（整表缺失成立）
- ①已覆盖：02 卡=JD 存量动能 + 领先 vs 同步分离（对已披露营收残差化后仍留 IC），status=blocked_on_data
  并写死缺段与主体归并双缺（ig_entity_code_map 仅 2 行）。
- ②原文逐句对表：决策问题"扩缩招动能能否领先营收**与行业景气**"的半问（行业景气）在 02 卡 target 中未列
  → 判为**卡面设计缺口**，但**不另立卡**：同一张完全不存在的表挂第二张 blocked_on_data 卡
  =给覆盖尺与 DSR 分母注水（违本战役"禁凑卡"铁律）。正确处置=渠道接入时在 02 卡扩 target（他车道义务，移交）。
- ③阻塞复核（含静默失败排除）：`system.tables` 筛 database LIKE 'c%' AND
  (table LIKE '%job%' OR '%recruit%' OR '%zhaopin%' OR '%jd%') → **Empty DataFrame（0 行）**；
  **同形控制查询**（同库同表、改筛 '%stock_basic%'/'%suspend%'/'%adj%' 等）返回 8 行 ⇒ 查询管道工作正常，
  空结果为真负而非静默失败；馆查 `python -m zephyr.library.lookup "招聘" --limit 6` → `(no results for '招聘')`。
  另按 §7.5 零命中≠不存在的纪律：本条以"库面枚举 + 表名筛 + 馆查"三源同指，结论钉为
  "渠道未接（B 档外采未落地）"，与 L7 判定一致，**无翻案**。
- 长尾核实：自报"③向英文查询词；主体归并方案未挖"——二者属④/③向工作面非节点原话判据 → 真长尾。
- 结论：复挖零新增，六向已尽——理由一句：节点唯一可判的两句（领先营收/领先景气）都挂在一张实测不存在的表上，
  判据面已入卡，景气半问的归属是扩臂义务而非第二张卡。

### 2.11 TDM-E-L9-D1（L7，TDM:L6007-6032）→ 漏矿 1 张 + 翻案（部分）
- ①已覆盖：02 卡（ablation）=三轨分轨消融 + 自证检测（IS→OOS 衰减 >50% 判过拟合）+
  各臂同数量假设配额相等门柱，status=blocked_on_data。
- ②漏矿：`algo_note_zh` 第二句 **"只产出决策假设不自证对错，验证必交考试链"**——
  这是一句结构承诺（凡产出假设必走完考试链拿到 verdict），今日即可证伪，且零卡覆盖 → 新卡 ablation/03
  （漏斗五段闭环率 + DSR 覆盖率 + 配额离散度 + 死档占比）。
- ③**翻案（部分）**：L7 02 卡 blocked 的理由句
  "实测 hypothesis_precheck 414 行、strategy_screen 1406 行、node_verdict 58 行**且均无日期跨度**
  ⇒ IS(2019-23)/OOS(2024-25) 两段根本没数据"——三处实测显示其中两个子断言不成立：
  - `node_verdict` **有** window_start/window_end 列（本车道实测列面），且窗口组合 3 种：
    2026-09-10 单日 38 行 / 2026-09-10..09-15 15 行 / **2019-04-01..2026-09-11 共 5 行**（横跨名义 IS 与 OOS）
    ⇒ "均无日期跨度"对该表为假。
  - `strategy_screen.verdict` 分布含 **oos_tested 169 行**，且 screen_batch 自带行情窗名
    （C4-OOS-2024-2026 47 / C4-OOS2-20260914 51 / C4-OOS2-20260913 35 / C4-OOS3-BACKLOG3-20260915 14）
    ⇒ "两段根本没数据"对 OOS 面为过断。
  - **但 02 卡的 blocked 结论维持**，真实阻断理由须改写为：轨道身份**无列承载**——
    `hypothesis_precheck.model` 414 行全为单值 `qwen3:8b`；`birth_channel` 实测 6 值
    （F 142/B 83/C 81/D 68/I 30/C2 10）是因子族轴不是搜索轨；两表均无 track/algorithm 家族列；
    且 screened_at/prechecked_at 是审计时戳非行情窗标注 ⇒ 各臂 IS→OOS 衰减不可归因。
    馆查（§7.5 降级形）："gplearn"→no results、"三轨"→no results、"MCTS"→命中
    `scripts/backtest/mcts_expression_search.py`+2 测试件；按"零命中≠不存在"纪律，
    结论钉为"三轨身份未证实可区分"，任何按 birth_channel 的读数不得被表述为"按三轨"。
  - 02 卡未被本车道改动（禁改他人卡字节）；改写义务移交 L7，记入 §五。
- 长尾核实：自报"GPU 燃料属 Owner 资源门位；三轨产能铺开后的实跑"——前者属 Owner 面（真长尾）；
  后者中"产能铺开"半句被本车道证伪为**已可测**（414/114/579/381/169/58 的漏斗现值可立即读数），
  故该项**不属实**，已以 ablation/03 落地。

## 三、新卡清单（RX-B 署名，10 张，绝对路径；均为另建新文件，未改任何既有卡）

1. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__ablation__03_市场体制条件下熔断减仓增量.yaml`
2. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-04__calibration__04_除权除息参考价分母误判清仓.yaml`
3. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S1/TDM-X-S1-04__comparison__05_早盘破位假信号时段可靠性.yaml`
4. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-02__calibration__03_新股首日分层卖出三臂.yaml`
5. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/exit_flow/S2/TDM-X-S2-02__comparison__04_T1可卖额度做T回转延迟成本.yaml`
6. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/portfolio_flow/C1/TDM-F-C1-02__shadow__03_置信度配比资金臂.yaml`
7. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/portfolio_flow/C2/TDM-F-C2-02__shadow__03_裁剪优先级非策略仓优先.yaml`
8. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/portfolio_flow/C2/TDM-F-C2-02__shadow__04_资金额度约束先卖后买与只削买入.yaml`
9. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/portfolio_flow/C3/TDM-F-C3-01__comparison__03_IS三分解与交易持仓二分.yaml`
10. `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010/docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9/TDM-E-L9-D1__ablation__03_假设漏斗闭环率与考试链缺口.yaml`

号段核对（先 ls 后接号，无冲突）：X-R1-01 已用 01(骨架 comparison)/02 → 本卡 03；
X-S1-04 已用 01/02/03 → 本卡 04、05；X-S2-02 已用 01/02 → 本卡 03、04；
F-C1-02 已用 01(骨架 shadow)/02 → 03；F-C2-02 已用 01/02 → 03、04；F-C3-01 已用 01(骨架 shadow)/02 → 03；
E-L9-D1 已用 01(骨架 comparison)/02 → 03。

机检：10/10 件 `yaml.safe_load` 全绿（修复 1 处 YAML 标量起始双引号、1 处 `**` 起始被解析为 alias、
补 4 件缺失的 `lineage` 面）；逐件必填面 status=preregistered / signal_kind / pillars_numeric(5-8 键) /
window(in_sample+oos+regimes+frozen_note) / buckets / pillars / target / lineage.confidence_writeback /
data_binding(signal_table+signal_column+signal_derivation+target_source+data_window_evidence) /
preregistered_by=st-nightmine-20261010-RXB / preregistered_at='2026-10-10' 全齐，且无 `generated: true`。

## 四、跨车道争点裁决与阻塞复核实测（命令原文+输出数字）

### 4.1 复测汇总（RX-B 独立执行，未引用他道数字）

| 复测面 | 实测结果 | 对他道断言的裁决 |
|---|---|---|
| c1_backtest.decision_daily | 2026-09-16..2026-10-12 / 9 个独立日 / 138 行 | L5 X-S1-04 数字命中 ✓ |
| c1_market.emotion_index.stage | close_final 8617 / pre_open 27 / auction 17（全表 8661 行、8622 独立日） | L5 "非情绪六段"成立 ✓；**L7 V2 卡的六段相位代理失效** ✗ |
| c1_market.l2_tick | count()=0（空表） | L5 X-S2-02 断言命中 ✓ |
| c1_market.tick_depth_5 | 2026-07-24..2026-09-30 / 130,146,982 行 | L5 断言命中 ✓ |
| c1_market.hk_connect_flow | 2014-11-17..2024-08-16 / 4052 行 | L7 A06 断供终点命中 ✓ |
| c1_market.northbound_hold_snapshot | 2024-09-30..2026-06-30 / uniqExact(trade_date)=8 / 57,458 行 | L7 A06 "独立日期仅 8 个"命中 ✓ |
| c1_market.money_flow | 2021-01-04..2026-10-09 / 1225 日 / 5,993,328 行 | L7 A06 命中 ✓ |
| c1_market.kline_daily_hfq | 1990-12-19..2026-09-30 / 10,098,785 行 / 5916 标的；IS 段(2018-01-02..2026-09-30) 9,061,473 行 / 5822 标的 | L5/L6/L7 三处报数逐位吻合 ✓ |
| c1_market.kline_1min | 2021-09-01..2026-10-09 / 1,493,285,247 行 | L7 A01 命中 ✓ |
| c1_market.stk_limit | 2015-01-05..2026-10-09 / 9,254,772 行 / 5831 标的 | L5 X-S2-02 命中 ✓ |
| c1_market.dragon_tiger_seat | 2022-01-04..2026-10-09 / 622,365 行 | L5 X-S1-04/03 卡命中 ✓ |
| 全库表名筛 %job%/%recruit%/%zhaopin%/%jd% | 0 行（同形控制查询返回 8 行 ⇒ 排除静默失败） | L7 B03 "整表缺失"成立 ✓ |
| c1_backtest.regime_snapshot_history | 2019-04-01..2026-10-09 / 1824 独立日 / 3635 行 | 新（X-R1-01/03 体制轴载体） |
| c3_fundamental.ex_dividend_event | 1991-03-11..2026-09-24 / 57,864 行 / 5438 标的；dr 非空率逐年 100% | 新（X-S1-04/04 载体，无断供） |
| c3_fundamental.ipo_calendar | list_date 2023-08-21..2026-10-09 / 11,176 行（含 issue_price/exchange） | 新（X-S2-02/03，发行价子面局部阻断） |
| c1_market.stock_basic | list_date 1990-12-10..2026-09-30（版本表 valid_from/valid_to；2015 段 372,254 为版本行） | 新（新股宇宙可全历史重建 → 翻案依据） |
| c1_market.suspend | 2026-09-04..2026-09-23 / 36 行 | 临停复牌分支真断供（L5 判定维持） |
| c1_market.adj_factor | 1990-12-19..2026-09-24 / 2,105,507 行 | 复权口径判据载体充分（P1-01 卡已覆盖，禁双计） |
| c1_backtest.sim_trade_log | 2026-07-17..2026-10-09 / 84 行 / 49 run_id | 真实流水不足以分桶 ⇒ 新卡一律改用装置信号流构造并披露 |
| c1_backtest.hypothesis_precheck | 414 行；model 全为 qwen3:8b；birth_channel F142/B83/C81/D68/I30/C210；verdict rejected155/deferred145/passed114；prechecked_at 2026-09-14..2026-10-08（34 批） | D1 翻案依据（轨道身份无列） |
| c1_backtest.strategy_screen | 1406 行；uniqExact(strategy_id)=579；screened_at 全 2026；verdict screened_in381/deferred_c4 321/rejected216/translated_c4 211/oos_tested169/sim_deviation104/failed_obsolete4；num_trials 1..20646 均 1442；deflated_sharpe 非空 376 ⇒ DSR 覆盖 26.7% | D1 翻案依据 + 新卡 03 主读数 |
| c1_backtest.node_verdict | 窗口组合 3 种：2026-09-10 单日 38 / 09-10..09-15 15 / 2019-04-01..2026-09-11 5 | D1 "无日期跨度"子断言不实 |
| 装置件 ls | allocator_shadow.py / exit_sim/exit_simulator.py / exit_sim/prereg_frozen.yaml / fexam/ch_data.py 均存在 | L6"真实基建"断言成立 ✓ |

### 4.2 争点裁决：emotion_index.stage 到底是什么
两条车道对同一列给出相反结论：L5（X-S1-04/02 卡 blocked_faces）="快照阶段标记，非情绪六段"；
L7（V2 卡）=用该列作"六段相位"代理读数面。本车道枚举实测：该列全表只有三个取值
（close_final 8617 / pre_open 27 / auction 17，共 8661 行）。**裁决：L5 对、L7 V2 卡的代理失效**。
后果与处置：
- X-S1-04 情绪退潮路的 blocked_on_data **维持**（六段态在 CH 确无载体）；
- 本车道 X-R1-01/03 卡因此不能以"六段情绪轴"为正交性对照，改用 regime_snapshot_history 作体制轴，
  并在新卡 blocked_faces 中写死"节点原文命名的六段轴无载体⇒结论上界仅为'与体制轴正交'"；
- L7 的 `TDM-E-L9-V2__ablation__02` 卡代理失效属他车道资产，V2 不在本车道 11 节点名单内，
  **未改动该卡一个字节**，仅在此登记并移交 L7/Owner（该卡已把结论上界钉为"代理版"，
  但其代理选错了列——严重度高于"上界声明"所能吸收的范围）。

## 五、对 L5/L6/L7 枯竭自报可信度的判断

1. **数据断言层：可信度高**。本车道独立复测 18 个关键表/列面，L5/L6/L7 的覆盖窗与行数断言
   **逐位吻合、零伪造**（含 hk_connect_flow 断供终点、northbound 8 个独立日、money_flow 5,993,328 行、
   l2_tick=0、decision_daily=138 行、allocator_shadow 件存在性）。负存在断言均带三源（库筛+馆查+控制查询）。
2. **判据覆盖层：不可靠，且"mined_out"自报最不可靠**。
   - L6 自报 5 个 `mined_out=是`，本车道复挖其 3 个（名单内），其中 **2 个被推翻**
     （TDM-F-C2-02 两句节点原话无卡、TDM-F-C3-01 algo_note_zh 第三句无卡）⇒ 名单内 mined_out 误判率 2/3；
     据外推，L6 另 3 个 mined_out（C2-01/C2-03/C3-01 之外的 C2-01、C2-03）按同一"整体 vs 单条判据"
     盲区推断同样不可信——三者的共同卡设计都是"整栈/整环有 vs 无"，把节点原文里的**次序与优先级句**
     当成了实现细节而非判据。这是**结构性盲区不是偶发疏漏**。
   - L5 未自报任何 mined_out（其收尾明写"mined_out 名单：空"，理由是"每一节点都仍有长尾"）——
     **该自我克制是诚实的**，且它自己在 §六 点名的 4 个复挖候选里，2 个（X-S1-02 之外本车道只碰了
     X-R1-01、X-S2-02）确实被复挖出漏矿，即 **L5 对自己长尾位置的判断是准的**，
     但它把"新股首日/临停复牌/风险警示板"打包挂起属**过度阻断**（本车道对新股首日翻案）。
   - L7 自报 45 节点仅 5 个 mined_out、余 40 挂长尾——本车道复挖 4 个：**3 个长尾属实**（A01/A06/B03 的
     自报长尾经逐句对表确认为"节点未写的泛化项"或"他节点/他车道义务"），**1 个不属实**（D1 的
     "三轨产能铺开后的实跑"被证伪为今日可测，其 blocked 理由含 2 处不实子断言）。
     ⇒ L7 的长尾申报总体可信（3/4），但它的**阻塞理由文字**存在"用错证据描述真阻断"的问题。
3. **总结论（一句）**：三条车道的**数字诚实、封矿保守、但判据覆盖自报系统性偏乐观**——
   共性失误模式=把"整链/整栈有无对照"当成了"该节点全部判据已考"，导致节点原文中的**次序句、
   优先级句、口径分母句、额度约束句**四类"实现细节形态的判据"被整体漏掉；
   L5/L6 的 `mined_out` 自报在交叉复挖下不成立，据 mining_sop §3"复挖零新增才准封矿"，
   **L5（未报封矿，无碍）/ L6（其 5 个 mined_out 中已证的 2 个须撤销，余 3 个建议同法复挖后再裁）/
   L7（其 5 个 mined_out 均在本车道名单之外，但 D1 的 blocked 理由须改写）**——三条车道**均不得据现报封矿**。

## 六、移交清单（不代改，等他车道/Owner）

1. → L7：`TDM-E-L9-D1__ablation__02` 的 blocked_on_data **理由**须改写（结论维持）：
   删除"三表均无日期跨度 / IS-OOS 两段根本没数据"，改为"轨道身份无列承载（model 单值 qwen3:8b、
   birth_channel 为因子族轴）+ 审计时戳非行情窗标注"；实测数字见本台账 §二.11 与 §四.1。
2. → L7 / Owner：`TDM-E-L9-V2__ablation__02` 的六段相位代理列失效（emotion_index.stage 实测仅三值、
   为快照阶段标记），该卡代理选错列，严重度高于其已声明的"结论上界"可吸收范围。V2 不在 RX-B 名单，未改。
3. → L6：撤销 TDM-F-C2-02 / TDM-F-C3-01 的 mined_out 自报；对同型设计的 C2-01 / C2-03 建议同法复挖
   （查"次序句/优先级句"是否被当作实现细节）。
4. → L6 或 P1 车道：F-C3-01 的 D84③ 复权口径判据与 P1-01/02 复权口径卡属同域重复簇，
   建议由 P1-01 卡扩臂（归因侧专属读数）而非新建第二卡（mining_sop §4 同域重复簇收敛唯一）。
5. → L7 A06 / L2/L3：A06 的 02 卡 target 面建议扩"行业景气"半问（B03 同理，节点决策问题后半），
   扩臂即可，不必新建同表 blocked 卡。
6. → Owner（门位登记，非执行）：本车道 10 个新 .yaml 属 CREATE-GUARD 需 creation_token 面；
   禁区明令禁改注册表，故 token 未落册，按 L5 台账 §六 先例（token 随批落）由 Owner/批车道统一登记。
   组合层一切"切换/晋升/退役"动作本车道**只出卡与判据、零执行**（新卡 06/07/08 卡内 owner_gate_note 已写明）。
