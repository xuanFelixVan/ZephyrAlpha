---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.1.0"
date: 2026-08-06
topic: discussion_framework
scope: 07_trading_decision_architecture
---

# 讨论框架·交易决策架构主题全集

> 本文档是 `07_trading_decision_architecture` 下所有"待讨论/已定稿"主题的**总索引与路线图**。
> 性质：永久态路线图，可随项目演进而修订（修订升版本号，见 [design_memo_management_spec](design_memo_management_spec.md) §5.3）。
> 用途：用户将开启多个 AI，每个 AI 认领一个主题组 → 讨论 → 落盘 discussion/design_memo → 施工。本文档是分工的"作战地图"。
> 关联：[design_memo_001_multi_strategy_concurrency.md](design_memo_001_multi_strategy_concurrency.md)（多策略并发架构，已定稿 v1.3.0）｜ [discussion_001](discussion_001_regime_detector_spec.md)（regime spec，已定稿 v1.3.1）｜ [discussion_002](discussion_002_regime_backtest_validation_plan.md)（regime 验证，已定稿 v1.0.0）

## 1. 文档定位

### 1.1 为什么有这份文档
- design_memo_001 已锁定多策略并发架构（Model A：独立账本 + firm 聚合 + regime 风险节流），但**只覆盖了"组合层"的 why**
- discussion_001/002 覆盖了 regime 检测器（**地基层**的 why + 验证）
- **选股、板块、仓位细节、风控落地、买入卖出、执行、对账、运营的 why 层全是空白**
- 这些空白需要逐个讨论定型，且数量众多（20+ 主题组），需要一份路线图统一调度

### 1.2 本文不做什么
- **不写 what is 的细节**（当前状态由作战地图 + depgraph 维护，本文只引用稳定 path）
- **不做裁定**（每个主题的裁定落在各自的 discussion/design_memo 里，本文只列"要讨论什么"）
- **不锁死顺序**（标注依赖与推荐顺序，但可根据人力/AI 资源灵活认领）

## 2. 三层现状快照

> 三层分治见 [management_spec §2](design_memo_management_spec.md)。本表标注每个作战地图阶段的"why 层"覆盖状态。

| 作战地图 | 阶段 | why 层（备忘/讨论） | depgraph 模块 | 施工方 | 状态 |
|---|---|---|---|---|---|
| 01 | 研究孵化 | ❌ 空白 | — | — | 待讨论 |
| 02 | 模型训练 | ❌ 空白 | — | — | 待讨论 |
| 03 | 回测验证 | 🟧 仅 regime 验证（discussion_002） | 🟧 shrinkage/c1_comparator | 另一AI 🔄 | 部分覆盖 |
| 04 | 模拟验证 | ❌ 空白 | — | — | 待讨论 |
| 05 | 选股 | ❌ 空白（design_memo_001 §6.1 仅列开放问题） | 🟧 BM-SEL-08/09 proposed | — | **核心空白** |
| 06 | 买入流 | ❌ 空白 | — | — | 待讨论 |
| 07 | 卖出流 | ❌ 空白 | — | — | 待讨论 |
| 08 | 仓位管理 | ✅ design_memo_001 §2.1（分层裁定框架） | ✅ MOD-POS-020/021/022 | 另一AI 🔄 blueprint+骨架 | 框架已定，细节待落 |
| 09 | 风控 | ✅ design_memo_001 §2.5（回撤Protocol四级框架） | — | — | 框架已定，落地待讨论 |
| 10 | 执行 | ✅ design_memo_010 | — | G22-AI | ✅ 已定稿 |
| 11 | 对账 | ❌ 空白 | — | — | 待讨论 |
| 12 | 跨切 | 🟧 design_memo_001 §3 指明大部分冲突因A模型消失 | — | — | 待清理 |

**结论**：12 个阶段里，why 层完整覆盖的只有 08（仓位框架）/09（风控框架）；部分覆盖的 03/12；**全空白的有 8 个**。本文档把空白 + 框架待落地的全部拆成主题组。

## 3. 主题组全集（G01–G23）

> 按"决策架构层次"组织（对标机构量化 pipeline：地基→alpha→组合→风控→交易→执行→验证→运营→治理）。
> 每个主题组是一个**可独立认领的讨论单元**，组内含若干子项。
> **正交性**列：是否与另一 AI 的 regime 施工正交（✅ 正交可并行 / ⚠️ 有依赖需协调）。

---

### L0·地基层

#### G01 数据与特征层规范
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 01/02 + 跨切 |
| 依赖 | 无（地基） |
| 讨论要点 | ① ClickHouse schema 规范（日K/分钟/Tick/板块/期权）② miniQMT tick 接入契约 ③ PIT 铁律（AS OF JOIN + Embargo）④ 特征仓库架构（计算/缓存/版本）⑤ 因子工程总纲（因子库/IC 评估/衰减监控/过拟合监控）⑥ 数据质量门控 |
| 产出物 | `design_memo_002_data_feature_layer.md` |
| 对标 | WorldQuant Alpha 工厂 / Numerai 数据管线 / qstobody 因子工程 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（部分能力已存在，需汇总成 why） |
| 优先级 | P0（地基，但可后置——策略定义不阻塞） |

#### G02 regime 检测器 spec ✅已定稿
| 项 | 内容 |
|---|---|
| 产出物 | [discussion_001](discussion_001_regime_detector_spec.md) v1.3.1 |
| 状态 | ✅ 已定稿，另一 AI 施工中（代码骨架 + 特征管线 + Shrinkage + C1 对比器） |
| 正交性 | — 本身就是 regime |

#### G03 regime 回测验证方案 ✅已定稿
| 项 | 内容 |
|---|---|
| 产出物 | [discussion_002](discussion_002_regime_backtest_validation_plan.md) v1.0.0 |
| 状态 | ✅ 已定稿（验收指南），等 regime 骨架就绪后执行 Phase 1-5 |

---

### L1·Alpha 选股层

#### G04 首批 3 策略定义 ⭐推荐起点
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 + design_memo_001 §6.1 |
| 依赖 | 无（alpha 地基） |
| 讨论要点 | ① 确认首批 3 策略（候选：打板 + 多因子 + 事件驱动）② 每策略 alpha 信号来源 ③ 换手率特征（高/中/低）④ 容量上限（打板几万~几十万）⑤ 选股池范围 ⑥ 持仓周期 ⑦ 与 regime 的关系（正交，regime 只节流不选股） |
| 产出物 | `discussion_003_first_batch_strategies.md` |
| 对标 | Citadel pod 模型（每 pod 独立 alpha + 独立 book）/ Morwane 双 sleeve |
| 正交性 | ✅ 与 regime 正交（design_memo_001 §2.2 明确） |
| 状态 | 待讨论（design_memo_001 §6.1 开放问题） |
| 优先级 | **P0**（一切 alpha/组合/风控下游的地基） |

#### G05 选股引擎架构
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04（策略定义） |
| 讨论要点 | ① 双引擎融合（BM-SEL-25，design_memo_001 定位为"打板策略内部融合"，非跨策略层）② L0→L1→L2-C 分层 ③ 量化强度评级 ④ 选股 pipeline 标准接口（输入信号→输出 target_portfolio）⑤ 候选池生成→过滤→排序→输出 ⑥ 与 StrategyBook 的对接契约 |
| 产出物 | `design_memo_003_stock_selection_engine.md` |
| 对标 | WorldQuant Alpha 工厂分层 / qstobody 多引擎 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P1 |

#### G06 板块轮动 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05（BM-SEL-08/09） |
| 依赖 | G04（板块是选股的输入特征，非独立层） |
| 讨论要点 | ① 板块强度算法（BM-SEL-08，460 板块 880xxx K线）② 回踩质量等级 A/B/C 判定 ③ 调整周期追踪（BM-SEL-09，进度≥80% 激活分批）④ 轮动序列追踪 ⑤ 虹吸态识别（design_memo_001 §1.3 提到情绪周期隐形驱动）⑥ 板块资金流 ⑦ 板块→个股的传导映射 |
| 产出物 | `discussion_004_sector_rotation_spec.md` |
| 对标 | AQR sector momentum / 华泰板块轮动研报 / 申万行业轮动 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（BM-SEL-08/09 已登记 proposed 未实现） |
| 优先级 | P1 |

#### G07 策略间相关性验证
| 项 | 内容 |
|---|---|
| 所属 | design_memo_001 §6.2（施工前必做） |
| 依赖 | G04（需策略定义才能算相关） |
| 讨论要点 | ① 5 候选策略两两相关矩阵 ② 按情绪周期分层看相关性 ③ 若各阶段相关性 >0.6 则"多策略实为情绪 beta 穿多件衣服"→ 重新审视 ④ 验证数据区间 ⑤ 验证报告模板 |
| 产出物 | `discussion_005_strategy_correlation_validation.md` |
| 对标 | Morwane block-bootstrap 相关性验证 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（施工前必做项） |
| 优先级 | P1（G04 后立即） |

#### G08 打板策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05（BM-SEL-22~25）+ design_memo_001 §4.3 |
| 依赖 | G04、G05、G06 |
| 讨论要点 | ① 连板梯队识别 ② 情绪周期定位器（BM-SEL-23-B，design_memo_001 §6.3 待评估准确率）③ 主升龙头识别 ④ 打板容量极小（单票几万~几十万）→ 必须小账本 ⑤ 双引擎融合在此策略内部（BM-SEL-25）⑥ 打板专用风控参数 ⑦ T+1 约束下的打板时序 |
| 产出物 | `discussion_006_daban_strategy_detail.md` |
| 对标 | 游资打板体系（龙虎榜/连板梯队/情绪周期）/ 量化社区连板策略 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P2（G04/G05/G06 后） |

#### G09 多因子策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04、G05、G01（因子工程） |
| 讨论要点 | ① 因子组合方式（打分/IC加权/正交化）② 行业中性化 ③ 因子衰减监控 ④ 多因子换手率（低，3-5 天 convergence）⑤ 多因子容量（较大，可承载主资金）⑥ 与打板策略的相关性 |
| 产出物 | `discussion_007_multifactor_strategy_detail.md` |
| 对标 | WorldQuant / Numerai 多因子 / 华泰金工多因子 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P2 |

#### G10 事件驱动策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04、G05 |
| 讨论要点 | ① 事件源（公告/新闻/龙虎榜/异动）② 事件分类（业绩/并购/政策/突发事件）③ 事件冲击衰减曲线 ④ 事件信号→选股映射 ⑤ 事件驱动换手率（中，2-3 天）⑥ news_data 多源情绪接入 |
| 产出物 | `discussion_008_event_driven_strategy_detail.md` |
| 对标 | RavenPack 事件驱动 / 彭博事件策略 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P2 |

#### G11 第二批次策略（价值反转 / 动量趋势）
| 项 | 内容 |
|---|---|
| 所属 | design_memo_001 §1.1（5 候选策略后 2 个） |
| 依赖 | G04 先跑 3 个月有 track record |
| 讨论要点 | ① 价值反转 alpha 信号 ② 动量趋势 alpha 信号 ③ 与首批 3 策略相关性 ④ 上线时机（首批 track record 后） |
| 产出物 | `discussion_009_second_batch_strategies.md` |
| 对标 | AQR 价值/动量 / Fama-French |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 暂缓（首批上线 3 个月后再讨论） |
| 优先级 | P4（远期） |

---

### L2·组合仓位层

#### G12 仓位算法 spec（落地分层裁定）
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + design_memo_001 §2.1 |
| 依赖 | G04（选股结果）+ G05 |
| 讨论要点 | ① 策略层粗仓位（等权 / risk parity，**不用 Kelly**）② 组合层 Kelly 精裁决（MOD-POS-001）③ Kelly 参数（预期收益/方差估计来源）④ risk parity 具体公式（inverse-vol / Morwane 范式）⑤ 单票硬上限 8% 裁剪逻辑 ⑥ 现金管理 ⑦ 分层裁定的接口契约（StrategyBook 输出粗仓位→firm 层 Kelly 精裁决） |
| 产出物 | `design_memo_004_position_sizing.md` |
| 对标 | Morwane inverse-vol risk parity / Kelly criterion 实证 / Morwane sleeve(alpha)+risk-parity-throttle(firm) 分层 |
| 正交性 | ✅ 与 regime 正交（regime 只缩 budget，不调仓位算法） |
| 状态 | 框架已定（design_memo_001 §2.1 分层裁定），细节待落 |
| 优先级 | P1（spec 层可先动） |

#### G13 FirmRiskAggregator 逻辑
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + design_memo_001 §2.2 |
| 依赖 | G12（仓位算法） |
| 讨论要点 | ① 按标的求和（自然叠加，design_memo_001 §2.3）② 单票硬上限裁剪（>8% 按比例削）③ 行业/总仓位硬约束 ④ 冲突标的处理（一策略买一策略卖→净额 or 优先级）⑤ **不做 MVO，不做协方差估计**（design_memo_001 §3.1 拒绝）⑥ 输出 firm_target_portfolio 契约 ⑦ O(N) 复杂度保证 |
| 产出物 | `design_memo_005_firm_risk_aggregator.md` |
| 对标 | Citadel pod 模型 firm 层风险聚合 / Morwane risk-parity-throttle |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 框架已定（MOD-POS-021 已登记），逻辑细节待落 |
| 优先级 | P2 |

#### G14 BudgetChangeHandler 三级升级
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + design_memo_001 §2.4 |
| 依赖 | G12、G13 |
| 讨论要点 | ① Tier 1 封锁新仓（瞬时）② Tier 2 rebalance_to_budget 信号（策略自选砍仓）③ Tier 3 按比例强裁（firm 层兜底）④ convergence_window 按换手率差异化（design_memo_001 §6.4：打板 1-2 天/多因子 3-5 天/事件 2-3 天）⑤ rebalance_to_budget 接口契约（策略不能说"我不卖"）⑥ 每级独立 log/复盘 |
| 产出物 | `design_memo_006_budget_change_handler.md` |
| 对标 | 机构级 budget rebalance 协议 |
| 正交性 | ⚠️ budget 来源依赖 RegimeMetaAllocator（G15），但三级升级逻辑本身正交 |
| 状态 | 框架已定（MOD-POS-022 已登记），窗口参数待校准 |
| 优先级 | P2 |

#### G15 RegimeMetaAllocator 参数
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + design_memo_001 §2.2 |
| 依赖 | ⚠️ **依赖 discussion_002 C1 验证结果**（Shrinkage 有效性）+ G04（PerformanceScore 需策略 PnL） |
| 讨论要点 | ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` ② Base_i 先验权重 ③ PerformanceScore 60 日 Sharpe 映射 [0.5,1.5] ④ Shrinkage 置信度→风险节流映射（design_memo_001 §2.2 四档）⑤ floor≥5% / cap≤40% ⑥ 稀有态差异化收缩 ⑦ 第二阶段上线时机 |
| 产出物 | `design_memo_007_regime_meta_allocator.md` |
| 对标 | Morwane risk-throttle / RegimeScore 移除裁定（design_memo_001 §2.2） |
| 正交性 | ⚠️ 本身就是 regime 节流的消费者，**等 C1 验证通过后再定参数** |
| 状态 | 框架已定（MOD-PA-007 已登记），参数待 C1 验证后校准 |
| 优先级 | P3（第二阶段，等 regime 验证 + 策略 track record） |

---

### L3·风控层

#### G16 回撤 Protocol 落地
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + design_memo_001 §2.5 |
| 依赖 | G12（仓位）—— 但框架已有，可并行 |
| 讨论要点 | ① 四级阈值（8/15/20/25%）落到 StrategyBook 内部的实现 spec ② 单策略 vs 组合层面分层（§2.5.3）③ 恢复机制（企稳 50%/创新高/强制休息 5 天，§2.5.2）④ Kill Switch 触发条件与执行路径（§2.5.5）⑤ 日度熔断（组合 -4%/单策略 -5%）⑥ Kill Switch 不可覆盖原则 ⑦ 回撤基准净值计算口径 ⑧ 与 regime Shrinkage 的协同（drawdown 是账户风险，regime 是市场风险，§2.5 定位） |
| 产出物 | `discussion_010_drawdown_protocol_impl.md` |
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff（§2.5 已引） |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 状态 | 框架已定（§2.5），落地 spec 待讨论 |
| 优先级 | P2（与 G12 并行） |

#### G17 VaR/ES 与波动率监控
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + design_memo_001 §2.5.4 |
| 依赖 | G16 |
| 讨论要点 | ① VaR_95 计算（历史模拟/参数法）② ES_95 计算 ③ 入场 VaR/ES 基准 ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）⑤ 30 日波动率调整（每增10%→仓位减20%）⑥ 数据窗口 ⑦ 与回撤 Protocol 的协同 |
| 产出物 | `discussion_011_var_es_monitoring.md` |
| 对标 | 赢牛资管 VaR-ES / Sina 量化风控 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 框架已列（§2.5.4），参数待定 |
| 优先级 | P3 |

#### G18 流动性危机处理
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + design_memo_001 §2.5.5 |
| 依赖 | G16 |
| 讨论要点 | ① 买卖价差监控（>正常 5x 触发）② 流动性危机→立即停止开仓仅允许平仓 ③ 流动性指标定义（换手率/成交额/盘口深度）④ 与 Kill Switch 的关系 ⑤ A 股涨跌停流动性失效处理 |
| 产出物 | `discussion_012_liquidity_crisis_protocol.md` |
| 对标 | tradingwyckoff Kill Switch / 机构流动性风控 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（§2.5.5 提及） |
| 优先级 | P3 |

---

### L4·交易流层

#### G19 买入流 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 06 |
| 依赖 | G04-G06（选股+板块）、G12（仓位）、G16（风控） |
| 讨论要点 | ① 分批建仓（BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C）② 突破失败降级 ③ 买入时序（盘中/盘后/集合竞价）④ 买入价格锚定 ⑤ 资金分配到多标的 ⑥ 与 budget 的协同 ⑦ T+1 约束 |
| 产出物 | `design_memo_008_buy_flow.md` |
| 对标 | 机构分批建仓 / Wyckoff 吸筹时序 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P3 |

#### G20 卖出流 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 07 |
| 依赖 | G19 |
| 讨论要点 | ① 卖出时序（止损/止盈/时间止损）② 止损触发（固定%/移动/ATR）③ 止盈逻辑 ④ 情绪退潮卖出（与 regime CRISIS/RECOVERY 协同）⑤ 破位卖出 ⑥ 分批卖出 ⑦ T+1 卖出约束 ⑧ 与回撤 Protocol 的联动 |
| 产出物 | `design_memo_009_sell_flow.md` |
| 对标 | 机构卖出纪律 / O'Neil 卖出法则 |
| 正交性 | ⚠️ 情绪退潮卖出与 regime 协同（但 regime 只给 Shrinkage，卖出逻辑在策略内） |
| 状态 | 待讨论 |
| 优先级 | P3 |

#### G21 情绪周期×交易决策
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 05/06/07/09 |
| 依赖 | G04、G08（打板最依赖情绪周期） |
| 讨论要点 | ① 5 阶段（冰点/反核/主升/疯狂/退潮）各阶段的买卖纪律 ② 情绪周期定位器准确率评估（design_memo_001 §6.3）③ 情绪周期与 regime 12 态的映射关系 ④ 各策略在不同情绪阶段的部署策略 ⑤ 情绪周期是"隐形驱动"（design_memo_001 §1.3）→ 策略间相关性来源 |
| 产出物 | `discussion_013_sentiment_cycle_trading.md` |
| 对标 | 游资情绪周期体系 / 龙虎榜情绪 / 涨跌停情绪温度 |
| 正交性 | ⚠️ 与 regime 部分重叠（regime 12 态含情绪维度），需明确分工 |
| 状态 | 待讨论（§6.3 待评估） |
| 优先级 | P2（打板策略前置） |

---

### L5·执行层

#### G22 下单对接与撮合
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 10 |
| 依赖 | G19/G20（买卖信号） |
| 讨论要点 | ① miniQMT 下单接口对接 ② 撮合算法（TWAP/VWAP/拆单/被动成交）③ 滑点模型 ④ 交易成本模型（佣金/印花税/过户费）⑤ 订单状态机 ⑥ 失败重试 ⑦ 执行风控（订单层熔断）⑧ 集合竞价处理 |
| 产出物 | [design_memo_010](design_memo_010_execution_broker.md) |
| 对标 | miniQMT 文档 / 机构执行算法（TWAP/VWAP/IS） |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.0.0（2026-08-08，G22-AI） |
| 优先级 | P4 |

---

### L6·验证层

#### G23 回测框架对接
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义） |
| 讨论要点 | ① BM-BT-01~07 环节在策略验证中的用法（regime 验证已映射，见 discussion_002 §2.1）② 策略回测 vs regime 回测的差异 ③ 策略上线门控 IS→WFA→OOS（BM-BT-07）④ 过拟合检测三维度（BM-BT-05）⑤ Deflated Sharpe（BM-BT-05-G） |
| 产出物 | `discussion_014_backtest_framework_docking.md` |
| 对标 | discussion_002 已建立的对接范式 / Morwane walk-forward |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 状态 | 部分覆盖（regime 已对接，策略侧待补） |
| 优先级 | P2（G04 后） |

#### G24 模拟与实盘验证路径
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 04 |
| 依赖 | G23（回测通过） |
| 讨论要点 | ① 模拟验证（paper trading）环境 ② 模拟时长 ③ 实盘小资金验证路径 ④ 实盘→模拟差异监控 ⑤ 上线决策门控 ⑥ 灰度上线（单策略先上） |
| 产出物 | `discussion_015_simulation_live_path.md` |
| 对标 | 机构 paper trading → 小资金 → 全量 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P4 |

---

### L7·运营层

#### G25 对账归因
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 11 |
| 依赖 | G22（执行）+ G04（策略） |
| 讨论要点 | ① PnL 归因（策略贡献分解）② 每日对账（成交 vs 持仓 vs 资金）③ 归因维度（策略/标的/因子/时段）④ 与 StrategyBook 独立 PnL 归因的对接（design_memo_001 §2.2）⑤ 异常交易检测 ⑥ 报表生成 |
| 产出物 | `design_memo_011_reconciliation_attribution.md` |
| 对标 | 机构中后台对账 / Barra 归因 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P5 |

#### G26 监控告警与复盘
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 |
| 依赖 | G25 |
| 讨论要点 | ① 系统健康监控（数据/引擎/下单链路）② 策略偏离监控（实盘 vs 回测）③ 告警阈值与通知 ④ 每日/每周/每月复盘机制 ⑤ 策略退役标准（连续跑输/逻辑失效）⑥ 复盘文档模板 |
| 产出物 | `discussion_016_monitoring_review.md` |
| 对标 | 机构 PM 周报 / 风控周报 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P5 |

---

### L8·跨切与治理层

#### G27 冲突矩阵清理与事件总线
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 12 |
| 依赖 | G04-G13（架构定型后才能清理冲突） |
| 讨论要点 | ① battle_map_12 §16 的 31 条跨策略冲突仲裁→大部分因 A 模型消失（design_memo_001 §7.3）② 仅留 firm-level 硬上限 ③ 事件总线/信号注入机制 ④ 实时计算节奏（盘中 vs 盘后）⑤ 配置驱动（参数热更新/AB 测试）⑥ 多策略投票降级（BM-SEL-20 已 rejected，§7.3） |
| 产出物 | `design_memo_012_cross_cutting_cleanup.md` |
| 对标 | 机构事件总线 / 微服务信号路由 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（部分已裁定 rejected） |
| 优先级 | P3（架构定型后） |

#### G28 策略生命周期与多 AI 协作
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 01/02/03/04 |
| 依赖 | 全局 |
| 讨论要点 | ① 策略生命周期（孵化→训练→回测→模拟→实盘→退役，对应作战地图 01-04/11）② 研究孵化阶段（BM-RES）规范 ③ 模型训练阶段（BM-MOD）规范 ④ 多 AI 协作分工规范（另一 AI 做 regime，本边做选股，交接点）⑤ 文档治理（design_memo 编号体系，本文档建立）⑥ creation_token / depgraph 登记流程 |
| 产出物 | `design_memo_013_lifecycle_multi_ai.md` |
| 对标 | MLOps 生命周期 / 机构策略研发流程 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P3（治理类，可后置） |

## 4. 依赖关系图

```
                    [G01 数据特征层] ─────────────────────────┐
                         │（地基，可后置）                      │
                         ↓                                    │
[L0地基]  G02 regime spec ✅ ──→ G03 regime验证 ✅ ──→ (C1验证通过)
                                    │                          │
                                    │ ⚠️ G15 RegimeMetaAllocator│
                                    │   等 C1 + 策略PnL         │
                                    ↓                          ↓
[L1 Alpha] G04 首批3策略⭐ ──→ G05 选股引擎 ──→ G06 板块轮动 ──→ G07 相关性验证
                │              │                                │
                ├──→ G08 打板细节 ←── G21 情绪周期×交易          │
                ├──→ G09 多因子细节 ←── G01 因子工程              │
                ├──→ G10 事件驱动细节                            │
                └──→ G11 第二批次（远期 P4）                      │
                │                                              │
                ↓                                              │
[L2 组合] G12 仓位算法 ──→ G13 FirmRiskAggregator ──→ G14 BudgetChangeHandler
                │              │
                │              └──→ G15 RegimeMetaAllocator（⚠️依赖C1）
                ↓
[L3 风控] G16 回撤Protocol落地 ──→ G17 VaR/ES ──→ G18 流动性危机
                │（与G12并行）
                ↓
[L4 交易] G19 买入流 ──→ G20 卖出流 ──→ G21 情绪周期×交易
                │
                ↓
[L5 执行] G22 下单对接撮合
                │
                ↓
[L6 验证] G23 回测框架对接 ──→ G24 模拟实盘验证
                │
                ↓
[L7 运营] G25 对账归因 ──→ G26 监控告警复盘
                │
                ↓
[L8 治理] G27 冲突矩阵清理 + G28 生命周期与多AI协作
```

## 5. 推荐认领顺序（3 条并行轨道）

> 另一 AI 持续做 regime（G02/G03 + C1 验证）。本边开启多 AI，每条轨道一个 AI，**3 条轨道并行**。

### 轨道 A：Alpha 链（核心关键路径）
```
G04 首批3策略⭐ → G05 选股引擎 → G06 板块轮动 → G07 相关性验证
                                    ↓
                    G08 打板 / G09 多因子 / G10 事件驱动（3个可并行）
```
- **理由**：策略定义是一切 alpha/组合/风控下游的地基，且与 regime 正交，可立即开工
- **认领建议**：1 个 AI 串行 G04→G05→G06→G07，再分 3 个 AI 并行 G08/G09/G10

### 轨道 B：组合风控链（spec 层先动）
```
G12 仓位算法spec → G13 FirmRiskAggregator → G14 BudgetChangeHandler
        ↓（并行）
G16 回撤Protocol落地 → G17 VaR/ES → G18 流动性危机
```
- **理由**：仓位/风控框架已定（design_memo_001 §2.1/§2.5），spec 层可不等选股细节先动；待 G04 产出后接口对齐
- **认领建议**：1 个 AI 串行 G12→G13→G14，另 1 个 AI 并行 G16→G17→G18

### 轨道 C：执行运营链（下游，可延后）
```
G22 下单对接 → G19 买入流 → G20 卖出流 → G23 回测对接 → G25 对账 → G26 监控复盘
```
- **理由**：执行/运营依赖上游信号定型，但 G22（miniQMT 对接）和 G23（回测对接）可独立预研
- **认领建议**：1 个 AI 串行，待轨道 A/B 产出后接口对齐

### 三条轨道的交汇点
- **G04 产出后**：轨道 B 的 G12 接口对齐、轨道 C 的 G23 策略载体就绪
- **C1 验证通过后**：G15 RegimeMetaAllocator 参数校准（另一 AI 产出）
- **G08/G09/G10 产出后**：G27 冲突矩阵清理（架构全定型）

## 6. 与 regime 施工的正交性说明

> design_memo_001 §2.2 核心裁定：**regime 只做风险节流（Shrinkage），不做 alpha 择时；不参与选股，只参与 budget 缩放。**

| 主题组 | 与 regime 关系 | 说明 |
|---|---|---|
| G04-G11（Alpha 全部） | ✅ 完全正交 | regime 不管选股，策略 alpha 独立 |
| G12-G14（组合仓位） | ✅ 正交 | regime 只缩 budget 数值，不调仓位算法 |
| G15（RegimeMetaAllocator） | ⚠️ 消费者 | 等 C1 验证 + 策略 PnL，第二阶段 |
| G16-G18（风控） | ✅ 正交 | drawdown 是账户级，regime 是市场级（§2.5 定位） |
| G19-G22（交易执行） | ✅ 正交 | |
| G21（情绪周期） | ⚠️ 部分重叠 | regime 12 态含情绪维度，需明确分工边界 |
| G23-G28（验证运营治理） | ✅ 正交 | |

**结论**：除 G15（等 C1）和 G21（需定分工边界）外，**其余 21 个主题组全部可与 regime 并行讨论**。

## 7. 多 AI 分工认领指南

### 7.1 认领流程
1. 用户为每个主题组开启一个 AI 对话
2. 该 AI 首读本文档 + design_memo_001 + 相关作战地图
3. AI 按本主题组的"讨论要点"逐项讨论，与用户对齐
4. 讨论定型后落盘产出物（discussion_NNN / design_memo_NNN）
5. 涉及模块施工的，按 management_spec §2.2 流程登记 depgraph

### 7.2 交接点纪律
- **AI 间不直接通信**，通过产出物（discussion/design_memo）+ depgraph path 交接
- 认领 G05 的 AI 必须先读 G04 的产出物 `discussion_003`
- 认领 G12 的 AI 必须先读 design_memo_001 §2.1 分层裁定
- 所有 AI 必读：design_memo_001（架构总纲）+ 本文档（路线图）

### 7.3 编号占用表（避免冲突）

> 认领时在此登记，避免产出物编号冲突。

| 产出物编号 | 主题组 | 认领方 | 状态 |
|---|---|---|---|
| discussion_001 | G02 regime spec | 另一AI | ✅ v1.3.1 |
| discussion_002 | G03 regime 验证 | 另一AI | ✅ v1.0.0 |
| discussion_003 | G04 首批3策略 | 已分配 | 讨论中 |
| discussion_004 | G06 板块轮动 | （待认领） | 待开工 |
| discussion_005 | G07 相关性验证 | （待认领） | 待开工 |
| discussion_006 | G08 打板细节 | （待认领） | 待开工 |
| discussion_007 | G09 多因子细节 | （待认领） | 待开工 |
| discussion_008 | G10 事件驱动 | （待认领） | 待开工 |
| discussion_009 | G11 第二批次 | （待认领） | 暂缓 |
| discussion_010 | G16 回撤落地 | （待认领） | 待开工 |
| discussion_011 | G17 VaR/ES | （待认领） | 待开工 |
| discussion_012 | G18 流动性危机 | （待认领） | 待开工 |
| discussion_013 | G21 情绪周期 | （待认领） | 待开工 |
| discussion_014 | G23 回测对接 | （待认领） | 待开工 |
| discussion_015 | G24 模拟实盘 | （待认领） | 待开工 |
| discussion_016 | G26 监控复盘 | （待认领） | 待开工 |
| design_memo_001 | 多策略并发架构 | 已定稿 | ✅ v1.3.0 |
| design_memo_002 | G01 数据特征层 | （待认领） | 待开工 |
| design_memo_003 | G05 选股引擎 | （待认领） | 待开工 |
| design_memo_004 | G12 仓位算法 | 已分配 | 讨论中 |
| design_memo_005 | G13 FirmRiskAggregator | （待认领） | 待开工 |
| design_memo_006 | G14 BudgetChangeHandler | （待认领） | 待开工 |
| design_memo_007 | G15 RegimeMetaAllocator | （待认领） | ⚠️等C1 |
| design_memo_008 | G19 买入流 | （待认领） | 待开工 |
| design_memo_009 | G20 卖出流 | （待认领） | 待开工 |
| design_memo_010 | G22 下单对接 | G22-AI | ✅ v1.0.0 |
| design_memo_011 | G25 对账归因 | （待认领） | 待开工 |
| design_memo_012 | G27 冲突矩阵清理 | （待认领） | 待开工 |
| design_memo_013 | G28 生命周期多AI | （待认领） | 待开工 |

## 8. 产出物命名规范

遵循 [management_spec §4.1](design_memo_management_spec.md)：
- 讨论文档：`discussion_NNN_topic.md`（NNN 三位序号，见 §7.3 占用表）
- 设计备忘：`design_memo_NNN_topic.md`
- topic 用 snake_case
- frontmatter 按 management_spec §4.2

**性质区分**：
- `discussion_*`：开放性讨论、待人决策的问题、spec 定义（如 regime spec、策略定义、板块算法 spec）
- `design_memo_*`：架构决策记录、why 层裁定（如选股引擎架构、仓位算法、风控落地）

## 9. 待人决策的开放问题汇总

> 以下问题需用户拍板，散落在各主题组内，集中索引便于追踪。

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 首批 3 策略确认（打板+多因子+事件驱动） | design_memo_001 §6.1 / G04 | 待决策 |
| convergence_window 按换手率定（打板1-2/多因子3-5/事件2-3天） | design_memo_001 §6.4 / G14 | 待首批策略定后校准 |
| 情绪周期定位器准确率评估 | design_memo_001 §6.3 / G21 | 待评估 |
| regime 检测器业务规则 spec | design_memo_001 §6.6 / discussion_001 | ✅ 已定 v1.3.1 |
| 12 态×N 策略样本量 | design_memo_001 §6.5 | ✅ 已决策（灰度+软分配） |
| 第二批次策略上线时机 | G11 | 暂缓（首批 track record 后） |
| G15 RegimeMetaAllocator 上线 | G15 | ⚠️ 等 C1 验证 |

## 10. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-06 | 1.0.0 | 初稿 | 建立 28 个主题组（G01-G28）的讨论框架路线图，供多 AI 分工认领；梳理依赖关系与 3 条并行轨道；建立产出物编号占用表 |
| 2026-08-07 | 1.1.0 | §7.3 标记 G04/G12/G22 认领状态为已分配 | 三主题组分配给并行 AI 开工，避免后续编号撞车 |
