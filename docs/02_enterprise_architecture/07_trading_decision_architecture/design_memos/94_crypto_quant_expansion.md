---
ttl: permanent
doc_type: architecture_view
title: 数字货币量化扩展设计
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-26
last_updated: 2026-08-26
topic: crypto_quant_expansion
scope: 07_trading_decision_architecture
---

# 数字货币量化扩展设计

> 本文是"数字货币量化战线"的启动备忘：记录为什么现在开这条战线、30 域骨架哪些与 A股共用/哪些参数化/哪些新建、四个横切改造点、新建候选清单与施工波次。
> 性质：混合型（决策备忘 + 施工计划）。模块级登记真源 = candidate_module_registry.yaml CAND-CRYPTO-001~010；域级全景真源 = docs/_working/依赖图/00-总览与索引.md（30 域 v7.0）。
> 状态：active v1.1.0——§9 Q1-Q6 已 Owner 拍板（2026-08-26），W0 市场日历抽象已派单（docs/_working/dispatch/2026-08-26-crypto-w0-market-calendar-order.md）。

## 1. 背景与定位

### 1.1 为什么是现在

- 项目 30 域依赖全景（v7.0）已完成设计，A股战线价值链主骨架（数据→因子→信号→组合→仓位→执行→风控）大量域处于"骨架/轻度"态，方法论与基建已就位。
- Owner 2026-08-26 决定启动数字货币量化战线。启动前必须先把"复用边界"设计清楚——否则两条战线各自演进，同一套因子/风控/回测逻辑会出现两份实现，违反 SSoT（单一真源，Single Source of Truth——每个概念只有一个权威实现）铁律。
- 核心判断：**量化系统约 60~70% 是资产无关的**（asset-agnostic，指不依赖具体交易品种特性的通用能力）。技术指标、因子评估、组合构建、风控框架、回测方法论、ML 平台、治理基建——这些对股票和数字货币是同一份代码。真正的差异集中在**接入层**（行情/执行）与**交易规则参数**。

### 1.2 两条战线的关系

| 维度 | A股战线（存量） | 数字货币战线（新增） |
|---|---|---|
| 定位 | 主战场，施工中 | 新战场，设计先行 |
| 共享层 | 30 域骨架、18 业务注册表机制、治理基建 | 同左（同一套代码，禁止 fork 另建） |
| 独立层 | QMT/券商接入、T+1、涨跌停、龙虎榜 | 交易所 API 接入、T+0、7×24、资金费率 |
| 资金 | 独立账户 | 独立账户（30 号 Model A 独立账本体系天然支持多市场扩展） |

**裁定一（复用优先）**：数字货币战线 ≈ 新建"接入层 + 规则参数集 + 市场日历"，**不重写内核**。任何"币版 XX 模块"施工前必须先问：能否用参数/规则集/instance（实例）差异解决，而非新建模块——能合并必须合并（治理预算纪律 D1）。

**裁定二（设计先行，登记先行）**：所有新建构件先登记 CAND 候选库（CAND-CRYPTO 族），施工启动时按晋升流程进 depgraph 设计态，与 A股战线同一套治理纪律。

## 2. 现状盘点

- 域级全景真源：[依赖图 00-总览与索引](../../_working/依赖图/00-总览与索引.md)（30 域 + 30×30 依赖矩阵 + 价值链主线 DAT→FAC→SIG→PC→PA→SELL→POS→XC→RPT）。
- A股侧已落地的可复用资产：技术指标体系（[16_technical_indicator_build_plan](16_technical_indicator_build_plan.md)，9 周期 OHLCV）、多策略并发架构（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)，独立账本+firm 聚合）、风控三模块 production（drawdown/var/kill_switch）、执行对接范式（[40_execution_broker](40_execution_broker.md)）、18 业务注册表机制（[62_business_registry_construction](62_business_registry_construction.md)）。
- 候选库查重：2026-08-26 对 candidate_module_registry.yaml 全量检索"数字货币/加密货币/crypto/BTC/永续/资金费/CCXT/币安"零命中——无重复登记风险，CRYPTO 族为全新前缀。
- 代码侧盘点（2026-08-26 循环审查 R1）：src/zephyr 无 crypto/交易所行情 WS 客户端/CCXT 任何痕迹（仅前端组件与协议层 6 处 websocket 字样，非行情接入）——CAND-CRYPTO-002/005 属全新建设，条目 q1 证据成立；日历消费点预侦察 25 文件命中（scheduler/multi_timeframe_fusion/auto_backfiller/backfill_checker/calendar_position_constraint/三 provider/plan_engine 等），W0 派单消费点盘点的初始清单。

## 3. 域级复用矩阵（三类划分）

> 对依赖全景 30 域逐一裁定。✅=直接共用（零改动）｜🔧=框架共用+参数/规则集差异｜🆕=币版新建（A股无对应物）｜➖=该战线暂不涉及。

### 3.1 横切与基础设施域（全部 ✅）

| 域 | 裁定 | 说明 |
|---|---|---|
| D-AUTONOMY-CORE / D-AUTONOMY-PERM | ✅ | Agent 引擎与保护层，资产无关 |
| D-INFRA-RUNTIME / D-INFRA-OPS | ✅ | 数据库/事件总线/调度/CI-CD/监控 |
| D-SECURITY / D-INTEGRATION / D-GOVERNANCE / D-OPS | ✅ | 门禁/契约/审计/遥测，同一套 |
| D-FRONTEND | ✅ | 复用同一前端，新增币区页面 |
| D-KNOWLEDGE / D-RESEARCH | ✅ | 知识域/研究基础设施，资产无关 |

### 3.2 核心价值链域

| 域 | 裁定 | 说明 |
|---|---|---|
| D-DATA | 🔧 | provider_base 抽象共用；新建交易所行情 provider（CAND-CRYPTO-002）；落库 schema 沿用分层存储 |
| D-FACTOR | ✅ | 因子框架（factor_base/IC-IR/FDR/CPCV/PIT 门禁）全共用；因子库实例部分独立（币特有因子如资金费率因子 Phase 2 补） |
| D-SIGNAL | ✅ | 信号合成/多因子融合框架共用；币版信号实例独立登记 strategy/factor 注册表 |
| D-PF-CORE / D-PF-ALLOC | ✅ | 组合构建与资本分配方法论共用（portfolio_model 注册表直接复用） |
| D-SELL-DECISION | ✅ | 卖出融合仲裁框架共用 |
| D-POSITION | 🔧 | 仓位裁决/资金曲线共用；Phase 2 合约需扩展爆仓价/维持保证金模型（CAND-CRYPTO-008） |
| D-EX-CORE | 🔧 | OMS 框架共用；券商适配换成交易所适配器（CAND-CRYPTO-005）；回执确认机制沿用 QMT 教训（隔 1~2 秒查委托） |
| D-EX-SOR | 🔧 | 智能路由概念共用；币侧初期单交易所直连，路由域 MVP 不施工 |
| D-REPORTING | ✅ | 绩效归因/报告框架共用 |
| D-RISK | 🔧 | 风控引擎（kill_switch/stop_loss/VaR）共用；risk_limit 注册表新增币版阈值实例（波动更大、无涨跌停、7×24 连续暴露） |
| D-ML-TRAIN / D-ML-SERVE | ✅ | 训练/推理平台共用；模型实例独立 |

### 3.3 数据上游与增强域

| 域 | 裁定 | 说明 |
|---|---|---|
| D-DATA-ENG | ✅ | 数据管道/特征存储共用 |
| D-ALT-DATA | 🆕 | 管道（NLP 情绪/新闻去重）共用；币侧新增链上数据源（CAND-CRYPTO-004）与宏观情绪面板（CAND-CRYPTO-010）；信源独立（X/Telegram 替代东财/同花顺） |
| D-CROSS-ASSET | ➡️受益 | 原为空白域；双市场格局形成后该域（跨市场相关性/BTC 与 A股联动）自然激活，远期 |
| D-COMPLIANCE | 🆕/➖ | A股程序化新规不适用；币侧合规边界=Owner 个人行为自担，系统内只保留"不操纵市场"类通用纪律，门禁级建设暂不启动 |
| D-TRADING | 🔧 | 结算对账框架共用；币版费率/充提/资金划转实例（CAND-CRYPTO-007 成本模型含 maker/taker 费率） |
| D-SIMULATION | ✅ | 回测/仿真引擎共用（52/53 号范式沿用） |
| seat（龙虎榜注册表） | ➖ | A股专属，币无对应物，不建 |

> 技术指标专项说明：technical_indicator 注册表全量共用——指标算法输入是 OHLCV（开高低收量）K 线，币的 K 线同构。唯一注意点：币圈常用 4h 周期（现有 9 周期未含），且 K 线无午休/隔夜断点——这归入 §4 横切改造点①，不是指标算法本身的改动。

## 4. 四个横切改造点（先于一切新建）

> 这四点是"同一套内核服务两个市场"的前提，全部以**抽象接口 + 按市场注入实现**的方式做，禁止 if/else 散落在业务代码里。

### 4.1 市场日历抽象（market_calendar，第一地基）

- **问题**：A股是断点日历（交易日历 + 午间休市 + 隔夜断点 + 节假日），币是 7×24 连续。项目现有 scheduler（调度）、K 线聚合（120min 由 60min 两根聚合等）、回测时间轴、PIT asof 口径全部隐式假设 A股日历。
- **裁定**：抽象 market_calendar 接口（Market Calendar，市场日历——定义"什么时间有交易、K 线如何切分"的策略对象），A股实现=现有交易日历逻辑收编，币实现=7×24 连续日历。所有时间相关计算改为注入日历，不直接读 A股历。
- **风险**：这是影响面最深的改造，必须保证 A股现有逻辑**零行为变化**（纯加接口层，回归测试全绿才算完）。
- 登记：CAND-CRYPTO-001，P0。**已派单 W0**（docs/_working/dispatch/2026-08-26-crypto-w0-market-calendar-order.md，2026-08-26 Owner 拍板后首派）。

### 4.2 T+0 vs T+1

- A股 T+1（当日买入次日可卖）写在买入流/卖出流/boundary 测试里；币 T+0 无此约束。
- 裁定：结算周期做成市场级参数，回测与实盘同一参数源；卖出决策域不感知差异（T+1 只是"可卖数量"的约束条件）。

### 4.3 交易规则可插拔

- A股规则：board_lot（整手 100 股）、price_cage（价格笼子/涨跌停 ±10%/20%）。
- 币规则：step_size（最小下单量步进）/tick_size（最小报价单位）按交易对各异；无涨跌停（部分交易所有短时价格保护带）。
- 裁定：ex_core 规则引擎改为规则集可插拔——每市场一份规则包，订单校验时按标的所属市场加载。登记：CAND-CRYPTO-006，P0。

### 4.4 杠杆与资金费率（Phase 2，永续合约）

- 永续合约（Perpetual Swap，永续掉期——无到期日的期货合约，靠资金费率锚定现货价）是币圈主力品种，但引入：资金费率（funding rate，多空双方每 8 小时互付的持仓成本）、杠杆、爆仓价、维持保证金。
- 裁定：**Phase 1 只做现货，Phase 2 才上永续**。VO-012 Side 枚举已预留 SHORT/COVER，但仓位域的杠杆/爆仓建模（CAND-CRYPTO-008）与资金费率成本（进 cost_model）在 Phase 2 启动，不在 MVP 范围。

## 5. 新建候选清单（CAND-CRYPTO 族）

> 真源 = candidate_module_registry.yaml。依赖关系决定施工波次（§6）。

| ID | 构件 | 域归属 | 优先级 | 依赖 |
|---|---|---|---|---|
| CAND-CRYPTO-001 | 市场日历抽象（7×24 连续日历 vs A股断点日历） | D-DATA/横切 | P0 | 无 |
| CAND-CRYPTO-002 | 交易所行情 provider（WebSocket 实时 + REST 补数，接 vendor_base 体系） | D-MKT-DATA | P0 | 001 |
| CAND-CRYPTO-003 | 永续合约专属数据（资金费率/持仓量 OI/基差/爆仓/多空比/清算热图） | D-MKT-DATA | P1（Phase 2） | 002 |
| CAND-CRYPTO-004 | 链上数据接入（交易所净流入/活跃地址/MVRV/鲸鱼地址跟踪/稳定币流动） | D-ALT-DATA | P2 | 无 |
| CAND-CRYPTO-005 | 数字货币执行适配器（订单状态机 + 回执确认 + 疑似丢单重试） | D-EX-CORE | P0 | 001/006 |
| CAND-CRYPTO-006 | 交易规则参数化（step_size/tick_size/无涨跌停/T+0 规则包） | D-EX-CORE | P0 | 001 |
| CAND-CRYPTO-007 | 币版回测三件套实例（universe/benchmark/cost_model，含 maker/taker+资金费率成本） | 注册表层 | P1 | 001/002 |
| CAND-CRYPTO-008 | 合约仓位与杠杆风控扩展（爆仓价/维持保证金/资金费率进持仓成本） | D-POSITION/D-RISK | P1（Phase 2） | 007 |
| CAND-CRYPTO-009 | 跨境网络双活传输层（主备双线路+热切换状态机+双层 WAL 传输侧） | D-MKT-DATA | P0 | 无（与 001 并行） |
| CAND-CRYPTO-010 | 币圈宏观情绪面板（恐惧贪婪指数/BTC 占比/ETF 流量/USDT 场外溢价/减半与解锁事件日历） | D-ALT-DATA | P2 | 无 |

> 优先级口径沿用项目惯例（回测环境三件套先于被测对象；风险相关模块先于策略模块——风险优先原则）。008 标 P1 但属 Phase 2 启动线，与 §4.4 裁定一致。009 为 2026-08-26 外部材料审查后补登——境内→境外交易所链路的网络双活是实盘刚需（行情断流=瞎、撤单传不到=资损），v0.1.0 遗漏，设计要点真源见 §7。010 为 2026-08-26 行业调查后补登（§9 拍板联动）：2026 年行业实证必备维度=恐惧贪婪指数六因子（波动率 25%/动量成交量 25%/社交 15%/调查 15%/BTC 占比 10%/谷歌趋势 10%，alternative.me 免费 API）+资金流三网关（交易所储备/稳定币流动/鲸鱼地址）+衍生品四维（资金费率/OI/多空比/清算热图）；其中衍生品四维归 003、鲸鱼与稳定币归 004（条目 tech_notes 已联动扩充），010 承接宏观情绪与事件日历（币版 regime_cycle/event_calendar 输入）。

## 6. 施工波次（建议）

```
W0  CAND-CRYPTO-001 市场日历抽象        ← 纯加接口层，A股零行为变化（回归全绿门槛）【已派单 2026-08-26】
W1  CAND-CRYPTO-002 行情接入 + 落库     ← 币可"看"（数据进 CH/DuckDB 分层存储）
    + CAND-CRYPTO-009 跨境网络双活层    ← 与 002 同波次：WS 长连接与执行回传共用双线路
W2  CAND-CRYPTO-006 规则参数化
    + CAND-CRYPTO-007 回测三件套         ← 币可"测"（回测环境就绪）
    + risk_limit 币版阈值实例            ← 风险先行，先于任何策略
W3  CAND-CRYPTO-005 执行适配器           ← 币可"交易"（纸面→模拟盘→实盘小资金，走 53 号 5 态 FSM 同一路径）
W4  币版策略首批定义 + 风控参数校准       ← 走 20 号范式（策略注册表登记）
Phase 2  CAND-CRYPTO-003/004/008        ← 永续合约 + 链上增强
         + CAND-CRYPTO-010 宏观情绪面板  ← 轻量采集可提前至 W4（恐惧贪婪/BTC 占比日频即可用，币版 regime 输入）
```

与 A股战线的冲突控制：W0~W2 全部正交（新增目录/注册表条目/接口实现，不改 A股业务逻辑）；W3 起涉及 ex_core 共享代码，须走 ARCH 登记 + 门禁。

## 7. 外部实战参考（已验证设计要点）

> 来源：`docs/_working/低学历勇闯量化/`（小红书 BalletHip 系列，三人团队 Polymarket 预测市场 BTC/ETH 5min 品种实战，54 图 + 内容.md，2026-08-26 全量审查）。该团队方向是高频/预测市场，与本战线"中低频 CEX 现货"定位不同——**只吸收资产/频率无关的工程方法论，不采用其高频定位与收益数据**（小资金+99.5 置信度门控+三周窗口，作者自承"明显有问题"）。

### 7.1 行情录制端设计（补强 CAND-CRYPTO-002）

来源材料：PM 回测上篇 13 页（`从实时盘口到可验证回放我怎么做pm回测系统_1~13_*.jpg`）。可直接当 002 施工 spec 的要点：

1. **录制窗口 > 名义窗口**：提前预热 6 步（发现市场→元数据→建连→订阅→首条真实数据→初始快照），"socket 已连接 ≠ ready"；延迟退出等尾部/结算事件
2. **快照基准 + Delta 绝对量语义**：Delta=档位更新后的绝对数量（零=删除），不是增减量——直接决定盘口重建正确性
3. **make-before-break 连接轮换**：先建新连接收真实数据→新旧短重叠→关旧，不人为造空窗
4. **无可靠 sequence 时不造序列号**：保留真实到达信息+后续快照校正（按交易所能力适配：币安有 sequence 可用则用）
5. **多证据独立保留不过早合成**：Snapshot/Delta/BBO/成交/参考价分存互校（快照查增量漂移、BBO 查最优价、结算事件定真正结束而非定时器）
6. **双时间戳 event_time + recorded_time**：与 A3 双时态建模（business_time/system_time）同构，前者恢复市场顺序、后者分析传输延迟与本地观察视角

### 7.2 跨境网络双活与传输加工（补强 CAND-CRYPTO-009，本族新增）

来源材料：第三篇网络坑 7 图（`低学历勇闯量化赛道(第三篇)低延迟交易网_1~7_*.jpg`）+ 回测中篇 25 页（`回测系统 采集的数据我是怎么加工处理的_*.jpg`）。要点：

1. **主备双线路**：主=HTTPS 直连（Caddy TLS 终结+DNS-01 证书+来源 IP 白名单），备=Cloudflare Tunnel（Access Service Token 鉴权、cloudflared 隧道、不暴露源站）；控制面走 CF、数据面正常直连、异常降级 CF
2. **热切换状态机三条血泪纪律**：①切换不能只看连接存活——失败+吞吐+积压三感知（5 秒桶积压 ~24 个≈2 分钟即主动绕开"活着但跟不上"的主线路）②切回用纯时间驱动 60s 探测，不依赖"积压=0"等发送中永远达不到的静态条件 ③积压计数器饱和递减防无符号下溢（0-1→2^64 曾误判天文数字积压反造 GB 级真实积压）
3. **内核层**：BBR 拥塞控制+fq 公平队列（跨境丢包时防传统拥塞窗口坍缩）
4. **双层 WAL 故障域分离**：边缘 WAL（采集端→后端）+ 后端 WAL（接收→ClickHouse）不可替代；后端"写 WAL 即返回 200"，200 语义=持久接收≠落库完成；与现有 wal_writer 对照校准
5. **at-least-once + 表级去重**：不追 exactly-once（分布式事务成本高）；稳定业务 ID→ReplacingMergeTree 后台折叠，无可靠序列的盘口流→普通 MergeTree 留原始事实、回放阶段谨慎去重——"库里没重复行"≠"能正确回放"
6. **边界全可观测**：5 秒桶/块 ~3000 行/热 WAL 15 分钟/冷溢写/容量硬上限（单写入器 10GiB、进程 20GiB），超限与丢弃全暴露为指标；"最终会重试"不能替代告警
7. **坏数据不拖死队列**：确定性坏请求→回退逐记录重放→隔离告警；临时错误（网络/超时）重试 vs 永久错误（未知表/字段不合法）隔离
8. **基准时间对齐**：跨机器/跨供应商须自建可观测做 offset 校准——时间不准则一切延迟评估失真

### 7.3 实盘运营参考（挂 53 号 FSM 与 55 号监控）

- 灰度金丝雀放仓 + 高置信度门控（99~99.5 才下单，先养 track record 再放敞口）——与 53 号 5 态 FSM 同思路
- 多市场配置参考实现：TOML `[[symbol]]/[[market]]`、per-symbol 通道/模型/状态、参数下沉 market 层——与本文"同一内核多市场"裁定互证
- 订单侧：事务式订单状态机、execution_constraints 从 artifact 动态读取、启动自动处理遗留仓位、断线自动重连
- 可观测：信号→执行漏斗大盘、下单耗时拆 build/sign/post 三段打点、丢包统计内置

### 7.4 不采用项（审查裁定）

- 高频定位（700ns/120ms/Rust 重写）——§8 已裁定不做高频/做市，性能工程仅参考不立项
- 收益数据（"周 80%/胜率 100%"）——小资金+高门控+短窗口，不作收益预期锚点
- Polymarket 市场本身——见 §8 不做什么
- L2 深度数据——作者实证 L1 足够，与币侧 MVP 口径一致（中低频不依赖 L2）
- 回测下篇（盘口重建+延迟建模）——作者未发布（fixbug 中），后续跟踪补充

### 7.5 机构实践与开源框架对照（2026-08-26 循环审查 R1）

> 来源：DolphinDB 币圈量化平台参考架构（2026-05）/ 机构策略研究报告（2026-02）/ OSS 框架全景调研（2026-04）/ Freqtrade 半年实测（2026-04）/ Meridian 桌诚实数字派研究（2026-06）。**采用总口径：项目已自建全链路，不引入外部框架；只吸收"已验证的运行纪律与对照检查项"。**

**机构参考架构五要点 ↔ 项目现状互证**：

| 机构实践 | 项目现状 | 结论 |
|---|---|---|
| 流批一体统一计算核（研究/生产同一代码，防双系统不一致） | 回测/模拟/实盘同路径（52/53 号）+ #ARCH-QUANT-001 proposed | ✅ 已对齐 |
| 数据韧性五件套：双写流表按键去重 / 断连重试+本地缓存+恢复重载 / 流表与库状态周期监控告警 / OHLC 前日完整性周期校验+缺失重取 | wal_writer 双层 + quality_gate + auto_backfiller | ✅ 同构（002 施工时逐项对照，已写入条目 tech_notes） |
| 风控模块与交易逻辑隔离（只读账户数据运行） | risk 域独立 + Broker ACL（INV-005） | ✅ 已对齐 |
| 因子库 191 Alpha + WorldQuant 101 Alpha 流批双算 | wq_alpha_87.py 已有基底 | 🔧 远期对照补全（不立项，W4 因子批次评估） |
| 资金费率套利为机构 2025-2026 主力盈利策略（delta-neutral：多现货+空永续 1x，8 小时收资金费，2025 均值 0.015%/8h） | Phase 2（003/008） | 📌 定为 **Phase 2 首个候选策略方向**；费束缚公式 breakeven hold ≈ fee ÷ funding-rate（短持有被费吃掉，Meridian 实证）已写入 003 tech_notes |

**开源框架格局（2026-04/08）与采用口径**：

| 框架 | 现状 | 吸收什么 |
|---|---|---|
| Freqtrade（48.4k★，币圈事实标准） | 活跃（111 版本） | ①lookahead-analysis/recursive-analysis **未来函数主动自检命令化**——项目 look_ahead_bias_detector 已有模块，裁定为回测前置必跑命令（运行方式升级，不新建）②Hyperopt 参数优化纪律：样本外留 20-30%+迭代≤200+多 loss 交叉验证——与项目 CPCV/FDR 纪律互证合并 ③FreqAI rolling retrain 范式——ml_train 已有，互证 |
| Hummingbot（15.9k★，Apache-2.0） | 活跃（做市/DEX/跨所） | 不做市不引用；Condor AI harness 仅作 agentic 架构参照 |
| Jesse（7.4k★，MIT） | 活跃 | 声明式策略语法参考；多周期无前视原生对齐项目 PIT 铁律 |
| NautilusTrader（Rust 核+Python 面） | 活跃 | #ARCH-QUANT-001 已记其内核抽象，远期迁移选项，不采用 |
| Backtrader 等僵尸项目 | 已死 | bus factor=1 教训：项目模块工厂+文档 why 锚定正是对策 |

**交易所官方 agent 工具包（2025-11~2026-03，已成生产基建）**：Kraken 开源 Rust CLI（134 命令+MCP+paper trading）/ 币安 7 个 agent skills（订单执行/钱包情报/聪明钱跟踪/合约风险筛查）/ OKX Agent Trade Kit（开源 MCP，60+ 链 500+ DEX）/ Coinbase agentic wallets。→ **CAND-CRYPTO-005 acquisition 首选评估变更：币安官方 agent skills（MCP 协议，与 A10 集成架构 MCP 路线一致）优先于 CCXT 社区层**（官方维护+原生 paper 模式；CCXT 降为备选兼容层）。已写入 005 条目。

### 7.6 前沿研究与远期方向（2026-06~08 最新）

1. **多 agent LLM 交易面板——价值在下行风险管理，不在收益增强**（两条独立实证收敛）：CGX 共识门控执行（MDPI 2026-08-04）：Bull/Bear 对抗辩论三轮+Meta-Evaluator 按共识强度门控，Sharpe 1.90、最大回撤 -85%、2022 崩盘期 Bear 门拦截 93% 时段 vs 2024 牛市仅 12%；1/3/5/9 面板实验（2026-06）：**面板构成比数量重要**（9 面板 5 多 3 空 1 混合最优；多空均等极化面板=决策瘫痪放大亏损）。→ 项目 A7 辩论机制（agent_debate）+风控否决链已同构，币侧远期直接复用，**不新建模块**；门控定位=下行风险管理（与项目"风险优先"原则互证）
2. **LLM MAS 加密货币组合管理**（UCL/NTU 2026）：三 agent（Crypto/News/Trading）分层架构，52 周回测 Sharpe 1.502；Crypto Agent（市场数据处理）贡献最大（移除 -42.57pp）。→ 与项目信号域多模态融合路线互证，远期参考
3. **Meta-RL-Crypto**（arXiv 2026-02）：LLM actor/judge/meta-judge 三角闭环自改进交易 agent。→ 远期研究跟踪，不立项
4. **Funding-aware 最优做市**（arXiv 2605）：perp DEX 做市 HJB 框架，资金费率 OU 过程建模（半衰期 2-6 小时，OU+jump 更优）。→ Phase 2 学术参考，不立项
5. **币版统计套利否定式裁定（Meridian 实证）**：币圈配对协整是短窗口假象——90~180 天窗口协整存活数坍缩到 ≈0（资产类 regime 不稳定的结构属性，非方法问题）；唯一例外=稳定币 peg（窄、费束缚）。→ **币版禁止立项配对协整/统计套利策略**（写入 §8），省下一条死路
6. **成本模型翻转排行榜（Meridian）**：薄边缘策略加真实成本（半价差+冲击+资金费）后排名反转；仓位是风险杠杆不是 alpha 杠杆（flat fees 下 Sharpe 与规模无关）；fill-on-touch 是上界、队列位置才是真相。→ 互证并强化 W2 cost_model 先行裁定；币版回测撮合至少做到"保守成交假设"档（中低频影响小，tick 级回测再议）
7. **中低频策略格局与成本铁律（2026-05 实证，循环审查 R2）**：四大"耐用策略"（历史正期望）=DCA 定投/趋势跟踪带止损/basis cash-and-carry（期现基差，与资金费 carry 同族）/窄区间网格；短线交易者 65-80% 净亏损（Barber&Odean/CFTC/FCA 披露口径）；费+资金费拖累 0.05-0.5%/往返（50 笔/周=年化 2.5-25% 仓位成本）。风控五规则（0.5-2% 单笔风险/预定义自动止损/接受 40% 胜率配 2:1 盈亏比/日周月回撤上限/交易资金与持有资金分离）与 35 号回撤 Protocol 互证。另：KuCoin 排行榜 24h 收益排序=结构性幸存者偏差陷阱（正确读法按运行时长排序）——互证 INV-014。→ **币版首批策略方向锚定趋势跟踪系（W4），basis carry 为 Phase 2 首候选（§7.5 已裁定）**；网格类零售策略不做（做市变种，与 §8 不做市一致）
8. **链上估值因子 8 年回测实证（2018-2026，12 策略组合）**：MVRV Z-Score（市值 vs 实现市值偏离：<1=历史深熊抄底区（2015/2018/2022 底）、>5=顶部区）与 NVT（币圈"市盈率"=价格/链上转账活跃度）为币版宏观因子中少数实证有效维度——归 CAND-CRYPTO-004 因子清单（tech_notes 已联动）；同批实证"主动策略大多跑不赢买入持有"——**因子开发纪律：任何币版主动因子/策略须先过买入持有基准门**（与 20 号首批策略基准纪律一致）
9. **稳定币 depeg 风险监控（2026-07 最新）**：USDT/USDC 双风险画像——USDT=储备不透明+法域压力（59% 份额），USDC=银行集中度+监管扣押（24%，2026-07-10 Circle 获 OCC 国家信托银行牌照）；监控信号=多场所持续折价（vs $1 偏差）+铸造销毁流突变+传染五联动（资金费率/OI/清算量/借贷利用率/稳定币池同时异动）；实践口径=发行方敞口≤30%+赎回路径季度测试+不当无风险替代品（3% depeg=3% 浮亏）。→ 币版资金载体风险（USDT 计价结算）——**归 risk_limit 币版实例（depeg 告警阈值）+ CAND-CRYPTO-010 面板信号（日频轻量，tech_notes 已联动）**

## 8. 不做什么

| 不做 | 理由 |
|---|---|
| 不 fork 代码库另建币版系统 | SSoT 铁律；差异只许走参数/规则集/实例 |
| Phase 1 不做合约/杠杆/做空 | 现货 MVP 先行（§4.4），杠杆把回撤 Protocol 复杂度抬一个量级 |
| 不做高频/做市 | 与项目中低频+因子驱动定位一致（40 号 §2.12 通道平权裁定同逻辑） |
| 不做 DeFi 链上交互 | 链上数据只读（CAND-CRYPTO-004），不签名不上链 |
| 不建 seat 类 A股专属注册表 | 币无龙虎榜对应物 |
| 不重写技术指标/因子框架 | OHLCV 资产无关，原样复用 |
| 不启动币侧合规门禁建设 | 个人交易自担边界，系统只保留通用交易纪律（§3.3） |
| 不纳入 Polymarket 等预测市场 | 品种机制（赔率合约）与 CEX 现货本质不同+合规灰色；外部材料仅作知识储备（§7），不建接入 |
| 不做跨所延迟套利 | 需 20-50ms 延迟目标+多区域 AWS 部署（机构基建口径），超单机/30Mbps 家用硬边界（system_charter §2） |
| 不做 MEV/验证者/私有 mempool 基建 | DeFi 链上交互已裁定不做（上表）；超个人资金与运维边界 |
| 不做币版配对协整/统计套利策略 | Meridian 实证（§7.6-5）：币圈协整 90~180 天窗口存活数坍缩≈0，结构性不成立；稳定币 peg 为唯一例外（Phase 2 再议） |

## 9. 开放问题（Owner 已拍板 2026-08-26）

| # | 问题 | 裁定（2026-08-26 Owner 拍板） | 落地位置 |
|---|---|---|---|
| Q1 | 交易所选型 | **币安（主）+ OKX（备/数据互备源）**；provider 可插拔架构，密钥按 Owner 账户在执行层配置，不阻塞设计 | CAND-CRYPTO-002/005 |
| Q2 | 交易池范围 | **MVP=BTC+ETH 现货**；Phase 2 扩市值前 20 | CAND-CRYPTO-007 |
| Q3 | Phase 2 时点 | **现货实盘 track record ≥3 个月后启动永续**（003/008 启动线） | CAND-CRYPTO-003/008 |
| Q4 | 行情数据源 | **MVP=交易所免费 WS 直连+REST 补数**；quality_gate 连续不达标再评付费聚合源 | CAND-CRYPTO-002 |
| Q5 | 资金安排 | **独立账本与 A股完全隔离**（30 号 Model A 天然支持多市场账本）；初始规模执行层定，不阻塞设计 | 30 号账本体系 |
| Q6 | 新闻/情绪信源 | **MVP=免费聚合（官方公告+主流快讯）**，X API 付费后置；恐惧贪婪指数/BTC 占比等宏观情绪指标由 CAND-CRYPTO-010 承接 | CAND-CRYPTO-010 |

## 10. 引用

- [依赖图 00-总览与索引](../../_working/依赖图/00-总览与索引.md)（30 域全景与依赖矩阵真源）
- [16_technical_indicator_build_plan](16_technical_indicator_build_plan.md)（技术指标体系，OHLCV 资产无关依据）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)（独立账本体系——多市场扩展的账本基础）
- [40_execution_broker](40_execution_broker.md)（执行对接范式：回执确认/疑似丢单重试等教训沿用）
- [52_backtest_framework_docking](52_backtest_framework_docking.md) / [53_simulation_live_path](53_simulation_live_path.md)（回测/模拟/实盘路径，币版沿用）
- [62_business_registry_construction](62_business_registry_construction.md)（18 业务注册表机制，币版实例登记入口）
- candidate_module_registry.yaml：CAND-CRYPTO-001~010（新建构件登记真源）
- `docs/_working/低学历勇闯量化/`（外部实战参考材料，§7.1~7.4 设计要点真源：第三篇网络坑 7 图 / PM 回测上篇 13 页 / 回测中篇 25 页）
- 2026-08-26 行业调查（币圈必备数据维度，§5 候选 010 与 003/004 扩充的实证来源）：alternative.me 恐惧贪婪指数六因子口径 / CoinGlass 衍生品聚合（资金费率/OI/多空比/清算热图）/ 资金流三网关实践（交易所储备、稳定币、鲸鱼地址，CryptoQuant/Glassnode/Nansen 工具体系）
- 2026-08-26 循环审查 R1 调查（§7.5/§7.6 真源）：DolphinDB 币圈量化平台参考架构（2026-05）/ 机构策略研究报告（2026-02）/ OSS 框架全景调研（2026-04）/ Freqtrade 实测（2026-04）/ Meridian RESEARCH_FINDINGS（2026-06）/ MDPI CGX 共识门控（2026-08）/ UCL-NTU LLM MAS（2026）/ arXiv 2605 funding-aware MM / arXiv 2509 Meta-RL-Crypto / 交易所官方 agent 工具包（Kraken CLI 2025-11、币安 skills 2026-03、OKX Agent Trade Kit 2026-03）
- W0 派工单：docs/_working/dispatch/2026-08-26-crypto-w0-market-calendar-order.md（CAND-CRYPTO-001 施工派单真源）

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-26 | 0.1.0 | 初稿落盘（draft） | Owner 宣布启动数字货币量化战线；先定复用边界与横切改造点，CAND-CRYPTO 族 8 条同步登记，开放问题 6 项待 Owner 拍板后升 active |
| 2026-08-26 | 0.2.0 | 外部材料审查升级：新增 §7 外部实战参考（BalletHip 系列 54 图全量审查——行情录制端 6 要点/网络双活+传输加工 8 要点/实盘运营 4 项/不采用 5 项）；补登 CAND-CRYPTO-009（跨境网络双活传输层，P0，W1 波次）；§5 候选清单 8→9 条；§6 波次 W1 加网络层；§8 不做什么加"不纳入预测市场" | Owner 裁定批准（外部材料审查报告三动作）：v0.1.0 遗漏跨境网络层（境内→境外交易所双活是实盘刚需），录制端/传输加工已验证设计直接吸收为 002/009 施工参考，Polymarket 维度裁定不纳入仅知识储备 |
| 2026-08-26 | 1.0.0 | **翻正 active**：§9 Q1-Q6 Owner 拍板落地（交易所=币安主+OKX 备/池=BTC+ETH 现货/Phase 2≥3 个月实盘记录/免费 WS 直连/独立账本隔离/免费信源）；行业调查补登 CAND-CRYPTO-010（币圈宏观情绪面板：恐惧贪婪指数/BTC 占比/ETF 流量/USDT 溢价/减半与解锁日历，P2），003/004 条目 tech_notes 联动扩充（多空比+清算热图/鲸鱼+稳定币）；§5 候选 9→10 条；§6 Phase 2 加 010；W0 市场日历抽象派单（dispatch/2026-08-26-crypto-w0-market-calendar-order.md）。本轮同时为并发覆写修复：v0.2.0 提交后工作区与 HEAD 出现混合态（frontmatter 回滚 0.1.0/§5 表丢 009），以全量覆写重建完整 v1.0.0 并立即提交固化 | Owner 拍板 Q1-Q6 并批准行业调查结论；备忘翻正 active 后 W0 正式开工；共享工作区并发覆写事故以"全量重建+立即提交"处置 |
| 2026-08-26 | 1.1.0 | **循环审查 R1（AI_review_instructions 方式）**：新增 §7.5 机构实践与开源框架对照（DolphinDB 流批一体/数据韧性五件套互证、Freqtrade 三件套——lookahead 自检命令化+Hyperopt 纪律+FreqAI 范式、交易所官方 agent 工具包成生产基建→005 acquisition 首选变更币安官方 skills/MCP）+ §7.6 前沿研究与远期方向（CGX 共识门控+面板构成实证——多 agent 价值在下行风险管理不新建模块/LLM MAS/Meta-RL-Crypto/funding-aware MM 远期参考/币版统计套利否定式裁定/成本模型翻转互证）；§8 不做什么补 3 行（跨所延迟套利/MEV 基建/配对协整）；§2 补代码侧盘点（零 crypto 件+日历消费点 25 文件预侦察）；CAND 注册表联动（005 acquisition 首选币安官方 skills/002 tech_notes 补数据韧性五件套对照/003 tech_notes 补 carry 费束缚公式）。过度工程筛除：跨所套利多区域 AWS/MEV 验证者/HFT 做市 HJB/K8s 部署 | Owner 指令驱动（全网搜索最新 2026-08+第一性原理+不过度工程）；三维度审查结论：集成方式补 lookahead 命令化+005 acquisition 变更，代码结构无需调整，数据源因子补否定式裁定与 Phase 2 carry 方向 |
| 2026-08-26 | 1.2.0 | **循环审查 R2+R3**：§7.6 补 3 条（⑦中低频策略格局与成本铁律——四大耐用策略/短线 65-80% 净亏损/费+资金费 0.05-0.5% 往返/风控五规则互证，币版首批策略锚定趋势跟踪系；⑧链上估值因子 8 年回测实证——MVRV Z-Score<1 深熊区/>5 顶部区+NVT 市盈率归 004 因子清单，因子开发纪律=先过买入持有基准门；⑨稳定币 depeg 风险监控——USDT/USDC 双风险画像+传染五联动信号+发行方敞口≤30%，归 risk_limit 币版实例+010 面板信号）；CAND 联动（004/010 tech_notes R2 补充+007 delisting 幸存者偏差纪律 R3+002 risks 交易所维护窗口 R3+010 笔误修正） | 策略格局/链上因子/稳定币风险三路实证（Skrumble 2026-05/KuCoin bots 2026-05/12 策略组合 8 年回测/Circle OCC 2026-07/Hacken 监控体系）；税务记账维度裁定不适用（非美法域，过度工程） |
