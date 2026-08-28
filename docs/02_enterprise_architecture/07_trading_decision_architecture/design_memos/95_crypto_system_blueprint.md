---
ttl: permanent
doc_type: architecture_view
title: 数字货币交易系统建设总览（一级→二级→三级结构）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "0.2.0"
date: 2026-08-28
last_updated: 2026-08-28
topic: crypto_system_blueprint
scope: 07_trading_decision_architecture
---

# 数字货币交易系统建设总览

> **定位**：币圈交易系统的**完整建设地图**——按一级结构（领域层）→二级结构（模块层）→三级结构（组件/任务层）分层梳理，与 94 号（启动备忘）互补：94 号记录"为什么启动+复用边界+横切改造点"，本文记录"要造什么+造到什么程度+什么顺序造"。
> **真源边界**：本文是**结构真源**（建设地图）；模块级登记真源 = candidate_module_registry.yaml；94 号 = 设计决策真源；depgraph = 代码状态真源。
> **状态**：active v0.2.0——2026-08-28 循环审查 R1 升级：状态对齐/引用补全/缺失补充/决策冲突修正。

---

## 0. 总览图（一级结构）

```
数字货币交易系统
├── 一、数据层（D-DATA / D-MKT-DATA / D-ALT-DATA）
│   ├── 1.1 行情数据（K线/ tick / 盘口）
│   ├── 1.2 合约数据（资金费率 / OI / 基差 / 爆仓 / 标记价格）
│   ├── 1.3 链上数据（交易所净流入 / 活跃地址 / MVRV / 鲸鱼跟踪 / 稳定币流动）
│   └── 1.4 宏观情绪（恐惧贪婪指数 / BTC占比 / ETF流量 / USDT溢价 / 事件日历）
├── 二、交易规则层（D-EX-CORE）
│   ├── 2.1 市场日历（7×24 连续日历）
│   ├── 2.2 交易规则包（step_size / tick_size / 无涨跌停 / T+0）
│   └── 2.3 执行适配器（订单状态机 / 回执确认 / 疑似丢单重试）
├── 三、策略与信号层（D-FACTOR / D-SIGNAL / D-PC / D-PA）
│   ├── 3.1 币版因子（资金费率因子 / 链上因子 / 趋势因子）
│   ├── 3.2 币版信号（多因子融合 / 信号合成）
│   ├── 3.3 组合构建（portfolio_model 币版实例）
│   └── 3.4 资本分配（RegimeMeta / 预算变更 币版适配）
├── 四、风控层（D-RISK / D-POSITION）
│   ├── 4.1 杠杆风控（爆仓价 / 维持保证金 / 资金费率成本）
│   ├── 4.2 币版阈值实例（波动更大 / 无涨跌停 / 7×24 暴露）
│   └── 4.3 仓位扩展（合约仓位 / 强平价 / 保证金监控）
├── 五、回测与仿真层（D-SIMULATION / D-BACKTEST）
│   ├── 5.1 币版回测三件套（universe / benchmark / cost_model）
│   ├── 5.2 回测引擎适配（T+0 / 无涨跌停 / 4h K线）
│   └── 5.3 模拟盘路径（53号 5态 FSM 币版实例）
├── 六、执行与运营层（D-TRADING / D-EX-CORE / D-REPORTING）
│   ├── 6.1 实盘执行（OKX broker / 订单管理 / 持仓对账）
│   ├── 6.2 班次运营（UTC 日切复盘 / 费率监控 / 强平监控）
│   └── 6.3 绩效报告（币版绩效归因 / 报告生成）
├── 七、基础设施层（D-INFRA / D-GOVERNANCE / D-SECURITY）
│   ├── 7.1 跨境网络（双活传输层 / 热切换状态机）
│   ├── 7.2 密钥管理（OKX API / Glassnode / CryptoQuant）
│   └── 7.3 治理门禁（市场标注 / candidate 晋升 / depgraph 登记）
└── 八、前端与展示层（D-FRONTEND）
    ├── 8.1 币圈盘面（24/7 行情 / 资金费率 / OI / 爆仓）
    ├── 8.2 币圈持仓风控（合约仓位 / 强平价 / 保证金）
    ├── 8.3 班次复盘（UTC 日切 / 费率 / 强平 / 信号验证）
    └── 8.4 情绪资金流（恐惧贪婪 / ETF / 稳定币流向）
```

---

## 一、数据层（D-DATA / D-MKT-DATA / D-ALT-DATA）

### 1.1 行情数据

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| OKX 现货 K 线（okx_provider.py） | ✅ production | 公开 REST /candles+/history-candles，分页 300 条/页 | — |
| OKX 永续 K 线（okx_swap_provider.py） | 🔒 candidate | 公开 REST，trigger=spot_track_record>=3_months | 永续 K 线落库 schema |
| 币安现货 K 线 | ⏳ 未施工 | 94号 Q1 裁定币安主+OKX 备，当前仅 OKX | 币安 provider（备用数据源） |
| WebSocket 实时行情 | ⏳ 未施工 | MVP 用 REST 补数，WS 归 009 传输层 | WS 客户端（009 落地后施工） |
| 4h K 线支持 | ✅ production | multi_timeframe_fusion 已支持 | — |

### 1.2 合约数据

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 资金费率历史（okx_swap_provider.py） | 🔒 candidate | /api/v5/public/funding-rate-history | 费率因子化（进 factor 注册表） |
| 持仓量 OI（okx_swap_provider.py） | 🔒 candidate | /api/v5/public/open-interest | OI 变化率计算 |
| 基差（okx_swap_provider.py） | 🔒 candidate | 永续标记价 - 现货指数价 | 基差因子化 |
| 爆仓数据 | ⏳ 未施工 | OKX 仅 WS 推送无历史回填 | 爆仓采集（WS 推送，009 落地后） |
| 标记价格（okx_swap_provider.py） | 🔒 candidate | /api/v5/public/mark-price | — |

### 1.3 链上数据

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 交易所净流入（onchain_provider.py） | 🔒 candidate | Glassnode 免费端点骨架，trigger=paid_api_key | 付费 API 接入后翻 production |
| 活跃地址（onchain_provider.py） | 🔒 candidate | Glassnode 免费端点骨架 | 同上 |
| MVRV Z-Score | ⏳ 未施工 | 需 Glassnode 付费数据 | 因子计算（MVRV<1 深熊抄底区） |
| NVT 比率 | ⏳ 未施工 | 需 Glassnode 付费数据 | 因子计算（币圈"市盈率"） |
| 鲸鱼地址跟踪 | ⏳ 未施工 | 需付费 API | 聪明钱地址监控 |
| 稳定币流动 | 🔒 candidate | CryptoQuant 免费端点骨架 | USDT/USDC 铸造销毁流监控 |
| 币圈档案（发行/流通/链上信息） | ⏳ 未施工 | 币种基本面数据 | 数据源选型（CoinMarketCap/CoinGecko） |

### 1.4 宏观情绪

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 恐惧贪婪指数（sentiment_panel_provider.py） | 🔒 candidate | alternative.me 免费 API 实采 | 日频采集进 regime_cycle |
| BTC 占比（sentiment_panel_provider.py） | 🔒 candidate | CoinMarketCap API 实采 | 占比趋势因子化 |
| ETF 流量（sentiment_panel_provider.py） | 🔒 candidate | 骨架（待接入数据源） | 数据源选型+接入 |
| USDT 场外溢价（sentiment_panel_provider.py） | 🔒 candidate | 骨架（待接入数据源） | 数据源选型+接入 |
| 币版事件日历 | ⏳ 未施工 | 减半/解锁/宏观事件 | event_calendar 币版实例 |

---

## 二、交易规则层（D-EX-CORE）

### 2.1 市场日历

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| CryptoCalendar（7×24） | ✅ production | 7×24 连续日历，UTC 日界 | — |
| PreExecutionChecker 日历注入 | ✅ production | market_calendar 参数注入 | — |
| 扩展消费点注入（20+ 文件） | ⏳ 未施工 | [#261](construction_progress_tracker.md) 遗留：A/B/C/D 类消费点（event_score/intraday_main/backfill_checker/tick_subscriber/plan_engine 等） | 后续波次顺带或专项 |

### 2.2 交易规则包

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| TradingRulePack 接口 | ✅ production | 抽象接口 | — |
| AshareRulePack（A股收编） | ✅ production | 委托 board_lot/price_cage 真源 | — |
| CryptoRulePack（币版骨架） | ✅ production | 默认 step_size/tick_size | 交易所 exchangeInfo 元数据接入后按交易对注入 |
| T+0/T+1 结算周期参数化 | ✅ production | settlement_cycle 属性 | 卖出决策域消费（待接线） |

### 2.3 执行适配器

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| OKX Broker（okx_broker.py） | ✅ production | HMAC-SHA256+幂等+回执确认 | — |
| 币安 Broker | ⏳ 未施工 | [94号 §9 Q1](94_crypto_quant_expansion.md) 裁定币安主+OKX 备，当前 OKX 先落地 | 币安 broker（备用通道，等币安 API 密钥配置） |
| 回执确认机制 | ✅ production | 隔 1.5 秒查委托，3 次重试 | 参数化（按交易所调） |
| 订单状态机 | ✅ production | OrderManager 共用 | — |

---

## 三、策略与信号层（D-FACTOR / D-SIGNAL / D-PC / D-PA）

### 3.1 币版因子

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 资金费率因子 | ⏳ 未施工 | 资金费率均值/极值/趋势 | 进 factor 注册表（等 003 落地） |
| 链上因子（MVRV/NVT/鲸鱼） | ⏳ 未施工 | 需 004 付费数据 | 因子计算+注册（等 004 落地） |
| 趋势因子（币版动量） | ⏳ 未施工 | 币圈趋势跟踪（[94号 §7.6](94_crypto_quant_expansion.md) 裁定首批方向） | 币版动量因子实例（W4 波次） |
| 波动率因子 | ⏳ 未施工 | 币圈高波动特性 | 波动率 regime 输入 |
| 条件选币（市值前 20 框架） | ⏳ 未施工 | 条件宇宙=市值前 20，框架共用，宇宙独立 | 进 universe 注册表（Phase 2 扩池） |

### 3.2 币版信号

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 币版信号实例 | ⏳ 未施工 | strategy/factor 注册表币版实例 | 首批趋势跟踪信号 |
| 多因子融合 | ✅ production | 框架共用 | 币版因子接入后配置 |

### 3.3 组合构建

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| portfolio_model 币版实例 | ⏳ 未施工 | 组合构建方法论共用 | 币版组合实例登记 |

### 3.4 资本分配

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| RegimeMeta 币版适配 | ⏳ 未施工 | 币圈 regime 与 A股不同 | 币版 regime_cycle 实例 |
| 预算变更币版适配 | ⏳ 未施工 | 30号 Model A 天然支持多市场 | 币版账本实例 |

---

## 四、风控层（D-RISK / D-POSITION）

### 4.1 杠杆风控

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 爆仓价计算（leverage_risk_model.py） | 🔒 candidate | 多头/空头爆仓价公式 | trigger=CAND-CRYPTO-003 promoted |
| 维持保证金阶梯（leverage_risk_model.py） | 🔒 candidate | 交易所 5 档阶梯 | 同上 |
| 资金费率成本（leverage_risk_model.py） | 🔒 candidate | notional*funding_rate*periods | 同上 |
| 风险指标（margin_ratio/distance） | 🔒 candidate | 聚合 LeverageRiskSnapshot | 同上 |

### 4.2 币版阈值实例

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| risk_limit 币版实例 | 🔒 candidate | 3 条核心阈值（2026-08-28），[risk_limit_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml) | 翻 promoted |
| 稳定币 depeg 告警阈值 | ⏳ 未施工 | USDT/USDC 脱锚监控 | 进 risk_limit 注册表 |
| 币版波动率阈值 | ⏳ 未施工 | 高波动环境适配 | 阈值校准 |

### 4.3 仓位扩展

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 合约仓位模型 | ⏳ 未施工 | 永续合约仓位+杠杆 | 等 003/008 落地 |
| 强平价监控 | ⏳ 未施工 | 实时爆仓价预警 | 等 008 落地 |
| 保证金监控 | ⏳ 未施工 | 维持保证金率预警 | 等 008 落地 |

---

## 五、回测与仿真层（D-SIMULATION / D-BACKTEST）

### 5.1 币版回测三件套

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| universe 币版实例（UNI-CRYPTO-001） | 🔒 candidate | BTC+ETH MVP 池，[universe_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml) L299 | 翻 promoted |
| benchmark 币版实例（BMK-CRYPTO-001） | 🔒 candidate | BTC 买入持有基准，[benchmark_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/benchmark_registry.yaml) L341 | 翻 promoted |
| cost_model 币版实例（CST-CRYPTO-001） | 🔒 candidate | maker/taker 费率，[cost_model_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cost_model_registry.yaml) L272 | 翻 promoted |

### 5.2 回测引擎适配

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| T+0 回测支持 | ⏳ 未施工 | 回测引擎 T+0 模式 | 结算周期参数消费 |
| 无涨跌停回测支持 | ⏳ 未施工 | 回测引擎无价格笼子模式 | 规则包注入回测 |
| 4h K 线回测支持 | ✅ production | 日历+聚合已支持 | — |

### 5.3 模拟盘路径

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 53号 5态 FSM 币版实例 | ⏳ 未施工 | 纸面→模拟→实盘小资金 | 币版 FSM 实例 |
| 模拟盘 OKX 对接 | ⏳ 未施工 | OKX paper trading | OKX 模拟盘 API 对接 |

---

## 六、执行与运营层（D-TRADING / D-EX-CORE / D-REPORTING）

### 6.1 实盘执行

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| OKX 实盘下单 | ✅ production | okx_broker 已落地 | 实盘小资金验证 |
| 订单管理 | ✅ production | OrderManager 共用 | — |
| 持仓对账 | ⏳ 未施工 | 币版持仓对账 | PositionReconciler 币版适配 |

### 6.2 班次运营（24/7 连续市场）

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| UTC 日切复盘 | ⏳ 未施工 | 24/7 无盘后，按 UTC 日切班次运转（00:00/08:00/16:00 三班） | 复盘脚本+报告模板+班次交接清单 |
| 费率监控 | ⏳ 未施工 | 资金费率异常告警（>0.1%/8h 或 <-0.1%/8h） | 监控面板+告警规则+历史费率曲线 |
| 强平监控 | ⏳ 未施工 | 爆仓风险实时监控（距离爆仓价<10% 预警） | 等 008 落地 |
| 班次交接检查清单 | ⏳ 未施工 | 每班开始前检查：持仓/保证金/费率/信号/系统状态 |  checklist 模板+自动化脚本 |

### 6.3 绩效报告

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 币版绩效归因 | ⏳ 未施工 | 绩效归因框架共用 | 币版归因实例 |
| 币版报告生成 | ⏳ 未施工 | 报告框架共用 | 币版报告模板 |

---

## 七、基础设施层（D-INFRA / D-GOVERNANCE / D-SECURITY）

### 7.1 跨境网络

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| Cloudflare Tunnel 配置生成（cross_border_dual.py） | 🔒 candidate | cloudflared YAML 生成 | trigger=cloudflare_account_configured |
| 双线路热切换状态机（cross_border_dual.py） | 🔒 candidate | 三感知切备/60s 切回 | 同上 |
| WS 长连接传输 | ⏳ 未施工 | 行情 WS 走双活 | 等 009 落地 |

### 7.2 密钥管理

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| OKX API 密钥 | ✅ 已登记 | OKX_API_KEY/SECRET_KEY/PASSPHRASE | 权限最小化审查（禁提现） |
| Glassnode API 密钥 | ⏳ 未配置 | 付费 API | Owner 注册后配置 |
| CryptoQuant API 密钥 | ⏳ 未配置 | 付费 API | Owner 注册后配置 |

### 7.3 治理门禁

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 市场标注三道闸 | ✅ production | 物理/数据/治理三闸 | — |
| CAND 候选晋升机制 | ✅ production | candidate→promoted 流程 | — |
| depgraph 登记 | ✅ production | 设计态→production 流转 | — |

---

## 八、前端与展示层（D-FRONTEND）

### 8.1 币圈盘面

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 24/7 行情面板 | ⏳ 未施工 | 币圈 K 线+资金费率+OI | 前端组件开发 |
| 爆仓热图 | ⏳ 未施工 | 爆仓数据可视化 | 等爆仓数据采集 |

### 8.2 币圈持仓风控

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 合约仓位面板 | ⏳ 未施工 | 合约仓位+强平价+保证金 | 等 008 落地 |
| 风险预警面板 | ⏳ 未施工 | 爆仓/保证金/depeg 预警 | 等 008/稳定币监控落地 |

### 8.3 班次复盘

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| UTC 日切复盘面板 | ⏳ 未施工 | 日切复盘数据展示 | 等复盘脚本落地 |
| 费率/强平/信号验证面板 | ⏳ 未施工 | 班次运营数据 | 等运营脚本落地 |

### 8.4 情绪资金流

| 模块 | 状态 | 说明 | 三级任务 |
|---|---|---|---|
| 恐惧贪婪指数面板 | ⏳ 未施工 | 情绪指标可视化 | 等 010 落地 |
| ETF 资金流面板 | ⏳ 未施工 | ETF 流量可视化 | 等数据源接入 |
| 稳定币流向面板 | ⏳ 未施工 | 稳定币流动可视化 | 等 004 落地 |

---

## 九、施工顺序建议（按依赖关系）

### Phase 1（当前可施工，无外部依赖）
1. **CAND-CRYPTO-007 翻 promoted**（三件套已登记 candidate，翻状态尾巴）
2. **#261 日历扩展消费点注入改造**（20+ 文件，A/B/C/D 类）
3. **币版策略首批定义**（趋势跟踪信号，进 strategy/factor 注册表，W4 波次）
4. **risk_limit 币版实例翻 promoted**（3 条核心阈值已登记）

### Phase 2（等 Owner 操作/外部条件）
5. **CAND-CRYPTO-009 跨境双活**（等 Cloudflare 账号注册）
6. **CAND-CRYPTO-004 链上数据**（等付费 API 密钥：Glassnode/CryptoQuant）
7. **币安 broker**（等币安 API 密钥配置，[94号 §9 Q1](94_crypto_quant_expansion.md) 裁定主备顺序）

### Phase 3（等现货 track record ≥3 个月）
8. **CAND-CRYPTO-003 永续合约数据翻 promoted**
9. **CAND-CRYPTO-008 杠杆风控翻 promoted**
10. **合约仓位/强平价/保证金监控**

### Phase 4（等 Phase 3 落地）
11. **CAND-CRYPTO-010 宏观情绪面板翻 promoted**
12. **币版策略回测验证**
13. **前端面板开发**（币圈盘面/持仓风控/班次复盘/情绪资金流）

---

## 十、修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-28 | 0.1.0 | 初稿落盘：一级 8 层 + 二级 24 模块 + 三级任务清单，基于 94 号 v1.4.0 + 当前代码实证 | Owner 指令梳理币圈完整建设地图，按结构分层 |
| 2026-08-28 | 0.2.0 | **循环审查 R1 升级**：①状态对齐（三件套/risk_limit 实例改 🔒 candidate 与注册表一致）②引用补全（#261 链接/94号 §9 Q1/§7.6 引用）③缺失补充（币圈档案/条件选币/班次运营细化）④决策冲突修正（开放问题 #2 网格策略标注已否定）⑤施工顺序编号修正（Phase 1-4 连续编号） | AI_review_instructions 循环审查协议第一轮：问题 8 项全修复 |

---

## 十一、开放问题

| # | 问题 | 状态 |
|---|---|---|
| 1 | 币安 vs OKX 主备顺序是否调整？（94号 Q1 裁定币安主+OKX 备，当前 OKX 先落地） | 待 Owner 裁定 |
| 2 | 币版策略首批方向：趋势跟踪 vs 费率套利 vs 网格？ | **已裁定**：趋势跟踪系（[94号 §7.6](94_crypto_quant_expansion.md)）；**已否定**：网格（做市变种）、配对协整（Meridian 实证结构性不成立） |
| 3 | 前端币圈面板技术栈：复用现有 dashboard 还是新建？ | 待 Owner 裁定 |
| 4 | UTC 日切复盘脚本归属：D-REPORTING 还是 D-TRADING？ | 待 Owner 裁定 |
