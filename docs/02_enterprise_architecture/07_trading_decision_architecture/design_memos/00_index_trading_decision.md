---
ttl: permanent
doc_type: architecture_view
title: 交易决策架构主题全集（总索引）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.8.2"
date: 2026-08-10
topic: trading_decision_index
scope: 07_trading_decision_architecture
---

# 交易决策架构主题全集（总索引）

> 本文档是 `07_trading_decision_architecture` 下所有"待讨论/已定稿"主题的**总索引与路线图**。
> 性质：永久态路线图，可随项目演进而修订（修订升版本号，见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §5.3）。
> 用途：用户将开启多个 AI，每个 AI 认领一个主题组 → 讨论 → 落盘 discussion/design_memo → 施工。本文档是分工的"作战地图"。
> 关联：[30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)（多策略并发架构，已定稿 v1.3.0）｜ [10_regime_detector_spec](10_regime_detector_spec.md)（regime spec，已定稿 v1.3.1）｜ [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md)（regime 验证，已定稿 v1.0.0）

## 0. 现有文档总目录（44 篇·按段位编号）

> 段位语义：**0x**=meta（规范与索引）｜**1x**=地基层（regime/数据特征）｜**2x**=Alpha 策略层｜**3x**=组合仓位与风控层｜**4x**=交易执行层｜**5x**=验证与可观测性层｜**6x**=跨切治理层｜**9x**=开放问题与远期愿景。
> 命名规则见 §8；新旧名对照见 §10；占用登记见 §7.3。
> **状态图例**：`active`=已定稿/已落地｜`draft`=草案/待讨论｜**骨架**=已建占位文档（frontmatter status=draft，仅含主题组信息与讨论要点清单，§2-§6 待填空；讨论定型后升 active）。

| 文件 | 内容一句话 | 状态 |
|---|---|---|
| [00_index_trading_decision.md](00_index_trading_decision.md) | 本文档：总目录 + G01-G28 主题组路线图 + 多 AI 分工认领 | active |
| [01_design_memo_management_spec.md](01_design_memo_management_spec.md) | 设计备忘管理规范（三层分治 / 命名 / 防飘移机制） | active |
| [10_regime_detector_spec.md](10_regime_detector_spec.md) | regime 检测器 spec（12 态定稿 v1.9.37） | active |
| [11_regime_backtest_validation_plan.md](11_regime_backtest_validation_plan.md) | regime 回测验证方案（Phase 1-5 验收指南） | active |
| [12_regime_phase2_validation.md](12_regime_phase2_validation.md) | Phase 2 模型质量验证（A1/A2/B1/B4 四验证器） | active |
| [13_regime_phase3_engineering_plan.md](13_regime_phase3_engineering_plan.md) | Phase 3 工程规划（降态+校准+NLP+S2/T3） | draft |
| [14_regime_s2_diagnosis.md](14_regime_s2_diagnosis.md) | S2 算法错配诊断报告 | draft |
| [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md) | G01 数据与特征层规范 | active v1.21.2 |
| [16_technical_indicator_build_plan.md](16_technical_indicator_build_plan.md) | 技术指标施工计划（9周期覆盖+增量/全量调度） | active v1.3.0 |
| [16_technical_indicator_catalog.md](16_technical_indicator_catalog.md) | 技术指标目录（8大类指标规范） | active v1.0.0 |
| [18_cold_archive_build_plan.md](18_cold_archive_build_plan.md) | 冷归档施工计划 | draft v0.1.0 |
| [17_special_trading_days_data_assets.md](17_special_trading_days_data_assets.md) | A股特殊交易日数据资产全景与治理（完整清单+已施工盘点+hk_trade_calendar修复#ARCH-DATA-001+治本方案#ARCH-DATA-002 v0.1.0） | draft |
| [19_northbound_hold_snapshot.md](19_northbound_hold_snapshot.md) | 北向资金季度持仓快照 fetcher 施工计划（日频断档替代方案，tushare hk_hold 已验证） | draft v0.1.0 |
| [20_first_batch_strategies.md](20_first_batch_strategies.md) | 首批 3 策略定义（打板+多因子+事件驱动） | active |
| [21_stock_selection_engine.md](21_stock_selection_engine.md) | G05 选股引擎架构 | active v1.1.18 |
| [22_sector_rotation_spec.md](22_sector_rotation_spec.md) | G06 板块轮动 spec | active v1.8.0 |
| [23_strategy_correlation_validation.md](23_strategy_correlation_validation.md) | G07 策略间相关性验证 | active v1.7.0 |
| [24_daban_strategy_detail.md](24_daban_strategy_detail.md) | G08 打板策略细节 | active v1.9.7 |
| [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md) | G09 多因子策略细节 | active v1.12.11 |
| [26_event_driven_strategy_detail.md](26_event_driven_strategy_detail.md) | G10 事件驱动策略细节 | active v1.8.0 |
| [27_second_batch_strategies.md](27_second_batch_strategies.md) | G11 第二批次策略（价值反转/动量趋势，暂缓） | 骨架 |
| [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md) | G21 情绪周期×交易决策 | active v1.11.0 |
| [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) | 多策略并发架构总纲（Model A：独立账本+firm聚合） | active |
| [31_position_sizing.md](31_position_sizing.md) | 仓位算法 spec（策略层粗仓位+firm层Kelly精裁决） | active |
| [32_firm_risk_aggregator.md](32_firm_risk_aggregator.md) | G13 FirmRiskAggregator 逻辑 | active v1.0.20 |
| [33_budget_change_handler.md](33_budget_change_handler.md) | G14 BudgetChangeHandler 三级升级 | active v2.10.0 |
| [34_regime_meta_allocator.md](34_regime_meta_allocator.md) | G15 RegimeMetaAllocator 参数（⚠️等 C1） | active v2.7.0 |
| [35_drawdown_protocol_impl.md](35_drawdown_protocol_impl.md) | G16 回撤 Protocol 落地 | active v1.34.0 |
| [36_var_es_monitoring.md](36_var_es_monitoring.md) | G17 VaR/ES 与波动率监控 | active v1.8.0 |
| [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md) | G18 流动性危机处理 | active v1.0.16 |
| [40_execution_broker.md](40_execution_broker.md) | 执行层下单对接（19项决策+代码已施工） | active |
| [41_buy_flow.md](41_buy_flow.md) | G19 买入流 spec | active v1.5.1 |
| [42_sell_flow.md](42_sell_flow.md) | G20 卖出流 spec | active v1.5.2 |
| [50_backtest_observability_workplan.md](50_backtest_observability_workplan.md) | 回测可观测性工作计划（六零件日志+MLflow方案调研） | draft |
| [51_panel_experiment_history_mlflow_retirement.md](51_panel_experiment_history_mlflow_retirement.md) | Panel 实验历史 Tab + MLflow 退役施工计划 | active |
| [52_backtest_framework_docking.md](52_backtest_framework_docking.md) | G23 回测框架对接 | active v1.7.4 |
| [53_simulation_live_path.md](53_simulation_live_path.md) | G24 模拟与实盘验证路径 | active v1.6.6 |
| [54_reconciliation_attribution.md](54_reconciliation_attribution.md) | G25 对账归因 | active v1.14.0 |
| [55_monitoring_review.md](55_monitoring_review.md) | G26 监控告警与复盘 | active v1.21.0 |
| [60_cross_cutting_cleanup.md](60_cross_cutting_cleanup.md) | G27 冲突矩阵清理与事件总线 | active v1.8.0 |
| [61_lifecycle_multi_ai.md](61_lifecycle_multi_ai.md) | G28 策略生命周期与多 AI 协作 | active v2.9.1 |
| [62_business_registry_construction.md](62_business_registry_construction.md) | 12业务注册表施工（registry_of_registries） | active v1.13.0 |
| [63_data_utilization_audit.md](63_data_utilization_audit.md) | 数据利用审计 | draft v0.9.0 |
| [64_data_source_download_spec.md](64_data_source_download_spec.md) | 数据源与下载体系规范（15 源/130+任务/11档调度/落库/韧性全面盘点+升级讨论载体） | draft v1.0.0 |
| [90_methodology_open_questions.md](90_methodology_open_questions.md) | 方法论遗留提案 21 项（全部待讨论） | draft |
| [91_density_prediction.md](91_density_prediction.md) | 密度预测与 QNN 远期愿景（待讨论） | draft |

## 1. 文档定位

### 1.1 为什么有这份文档
- 30_multi_strategy_concurrency 已锁定多策略并发架构（Model A：独立账本 + firm 聚合 + regime 风险节流），但**只覆盖了"组合层"的 why**
- 10_regime_detector_spec/002 覆盖了 regime 检测器（**地基层**的 why + 验证）
- **选股、板块、仓位细节、风控落地、买入卖出、执行、对账、运营的 why 层全是空白**
- 这些空白需要逐个讨论定型，且数量众多（20+ 主题组），需要一份路线图统一调度

### 1.2 本文不做什么
- **不写 what is 的细节**（当前状态由作战地图 + depgraph 维护，本文只引用稳定 path）
- **不做裁定**（每个主题的裁定落在各自的 discussion/design_memo 里，本文只列"要讨论什么"）
- **不锁死顺序**（标注依赖与推荐顺序，但可根据人力/AI 资源灵活认领）

## 2. 三层现状快照

> 三层分治见 [management_spec §2](01_design_memo_management_spec.md)。本表标注每个作战地图阶段的"why 层"覆盖状态。

| 作战地图 | 阶段 | why 层（备忘/讨论） | depgraph 模块 | 施工方 | 状态 |
|---|---|---|---|---|---|
| 01 | 研究孵化 | ❌ 空白 | — | — | 待讨论 |
| 02 | 模型训练 | ❌ 空白 | — | — | 待讨论 |
| 03 | 回测验证 | 🟧 仅 regime 验证（11_regime_backtest_validation_plan） | 🟧 shrinkage/c1_comparator | 另一AI 🔄 | 部分覆盖 |
| 04 | 模拟验证 | ❌ 空白 | — | — | 待讨论 |
| 05 | 选股 | 🟧 G08 打板（24号 active v1.9.7）+ G09 多因子（25号 active v1.12.11）已定稿，G05/G06/G07 待讨论 | 🟧 BM-SEL-02/22-25 | — | **部分覆盖**（2/5 主题组定稿） |
| 06 | 买入流 | ❌ 空白 | — | — | 待讨论 |
| 07 | 卖出流 | ❌ 空白 | — | — | 待讨论 |
| 08 | 仓位管理 | ✅ 30_multi_strategy_concurrency §2.1（分层裁定框架） | ✅ MOD-POS-020/021/022 | 另一AI 🔄 blueprint+骨架 | 框架已定，细节待落 |
| 09 | 风控 | ✅ 30_multi_strategy_concurrency §2.5（回撤Protocol四级框架） | — | — | 框架已定，落地待讨论 |
| 10 | 执行 | ✅ 40_execution_broker | — | G22-AI | ✅ 已定稿+代码已施工 |
| 11 | 对账 | ❌ 空白 | — | — | 待讨论 |
| 12 | 跨切 | 🟧 30_multi_strategy_concurrency §3 指明大部分冲突因A模型消失 | — | — | 待清理 |

**结论**：12 个阶段里，why 层完整覆盖的只有 08（仓位框架）/09（风控框架）/10（执行）；部分覆盖的 03/05/12；**全空白的有 6 个**。本文档把空白 + 框架待落地的全部拆成主题组。

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
| 产出物 | `15_data_feature_layer_spec_data_feature_layer.md` |
| 对标 | WorldQuant Alpha 工厂 / Numerai 数据管线 / qstobody 因子工程 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（部分能力已存在，需汇总成 why） |
| 优先级 | P0（地基，但可后置——策略定义不阻塞） |

#### G02 regime 检测器 spec ✅已定稿
| 项 | 内容 |
|---|---|
| 产出物 | [10_regime_detector_spec](10_regime_detector_spec.md) v1.9.37 |
| 状态 | ✅ 已定稿，另一 AI 施工中（代码骨架 + 特征管线 + Shrinkage + C1 对比器） |
| 正交性 | — 本身就是 regime |

#### G03 regime 回测验证方案 ✅已定稿
| 项 | 内容 |
|---|---|
| 产出物 | [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) v1.10.0 |
| 状态 | ✅ 已定稿（验收指南），等 regime 骨架就绪后执行 Phase 1-5 |

---

### L1·Alpha 选股层

#### G04 首批 3 策略定义 ⭐推荐起点
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 + 30_multi_strategy_concurrency §6.1 |
| 依赖 | 无（alpha 地基） |
| 讨论要点 | ① 确认首批 3 策略（候选：打板 + 多因子 + 事件驱动）② 每策略 alpha 信号来源 ③ 换手率特征（高/中/低）④ 容量上限（打板几万~几十万）⑤ 选股池范围 ⑥ 持仓周期 ⑦ 与 regime 的关系（正交，regime 只节流不选股） |
| 产出物 | `20_first_batch_strategies_first_batch_strategies.md` |
| 对标 | Citadel pod 模型（每 pod 独立 alpha + 独立 book）/ Morwane 双 sleeve |
| 正交性 | ✅ 与 regime 正交（30_multi_strategy_concurrency §2.2 明确） |
| 状态 | 待讨论（30_multi_strategy_concurrency §6.1 开放问题） |
| 优先级 | **P0**（一切 alpha/组合/风控下游的地基） |

#### G05 选股引擎架构
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04（策略定义） |
| 讨论要点 | ① 双引擎融合（BM-SEL-25，30_multi_strategy_concurrency 定位为"打板策略内部融合"，非跨策略层）② L0→L1→L2-C 分层 ③ 量化强度评级 ④ 选股 pipeline 标准接口（输入信号→输出 target_portfolio）⑤ 候选池生成→过滤→排序→输出 ⑥ 与 StrategyBook 的对接契约 |
| 产出物 | `21_stock_selection_engine_stock_selection_engine.md` |
| 对标 | WorldQuant Alpha 工厂分层 / qstobody 多引擎 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P1 |

#### G06 板块轮动 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05（BM-SEL-08/09） |
| 依赖 | G04（板块是选股的输入特征，非独立层） |
| 讨论要点 | ① 板块强度算法（BM-SEL-08，460 板块 880xxx K线）② 回踩质量等级 A/B/C 判定 ③ 调整周期追踪（BM-SEL-09，进度≥80% 激活分批）④ 轮动序列追踪 ⑤ 虹吸态识别（30_multi_strategy_concurrency §1.3 提到情绪周期隐形驱动）⑥ 板块资金流 ⑦ 板块→个股的传导映射 |
| 产出物 | `22_sector_rotation_spec.md` |
| 对标 | AQR sector momentum / 华泰板块轮动研报 / 申万行业轮动 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（BM-SEL-08/09 已登记 proposed 未实现） |
| 优先级 | P1 |

#### G07 策略间相关性验证
| 项 | 内容 |
|---|---|
| 所属 | 30_multi_strategy_concurrency §6.2（施工前必做） |
| 依赖 | G04（需策略定义才能算相关） |
| 讨论要点 | ① 5 候选策略两两相关矩阵 ② 按情绪周期分层看相关性 ③ 若各阶段相关性 >0.6 则"多策略实为情绪 beta 穿多件衣服"→ 重新审视 ④ 验证数据区间 ⑤ 验证报告模板 |
| 产出物 | `23_strategy_correlation_validation_strategy_correlation_validation.md` |
| 对标 | Morwane block-bootstrap 相关性验证 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（施工前必做项） |
| 优先级 | P1（G04 后立即） |

#### G08 打板策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05（BM-SEL-22~25）+ 30_multi_strategy_concurrency §4.3 |
| 依赖 | G04、G05、G06 |
| 讨论要点 | ① 连板梯队识别 ② 情绪周期定位器（BM-SEL-23-B，30_multi_strategy_concurrency §6.3 待评估准确率）③ 主升龙头识别 ④ 打板容量极小（单票几万~几十万）→ 必须小账本 ⑤ 双引擎融合在此策略内部（BM-SEL-25）⑥ 打板专用风控参数 ⑦ T+1 约束下的打板时序 ⑧ 助攻梯队权重真源裁定 |
| 产出物 | `24_daban_strategy_detail.md`（active v1.9.7：8 项讨论要点全对齐+§3.13/§3.14 施工算法 12 项补全+2026-08 arXiv 最新研究整合） |
| 对标 | 游资打板体系（龙虎榜/连板梯队/情绪周期）/ 量化社区连板策略 / 华安涨停板Alpha 2026-03 / caifuhao 连板复盘 2026-08 |
| 正交性 | ✅ 与 regime 正交（打板读情绪周期不读 regime） |
| 状态 | ✅ active v1.9.7（8 项讨论要点全对齐+施工算法 12 项补全） |
| 优先级 | P1（高换手、小容量、高频 alpha） |

#### G09 多因子策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04、G05、G01（因子工程） |
| 讨论要点 | ① 因子组合方式（打分/IC加权/正交化）② 行业中性化 ③ 因子衰减监控 ④ 多因子换手率（低，3-5 天 convergence）⑤ 多因子容量（较大，可承载主资金）⑥ 与打板策略的相关性 |
| 产出物 | `25_multifactor_strategy_detail.md`（active v1.12.11：6 项讨论要点全对齐+§3.7 施工算法 8 项补全+Phase 4.1-4.20 远期候选栈+2026-08 arXiv 最新研究整合） |
| 对标 | WorldQuant / Numerai 多因子 / 华泰金工多因子 / BigQuant ICIR 2026-07 |
| 正交性 | ✅ 与 regime 正交（纯横截面选股） |
| 状态 | ✅ active v1.12.11（6 项讨论要点全对齐+施工算法 8 项补全） |
| 优先级 | P2（承载主力资金的低频基石） |

#### G10 事件驱动策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04、G05 |
| 讨论要点 | ① 事件源（公告/新闻/龙虎榜/异动）② 事件分类（业绩/并购/政策/突发事件）③ 事件冲击衰减曲线 ④ 事件信号→选股映射 ⑤ 事件驱动换手率（中，2-3 天）⑥ news_data 多源情绪接入 |
| 产出物 | `26_event_driven_strategy_detail_event_driven_strategy_detail.md` |
| 对标 | RavenPack 事件驱动 / 彭博事件策略 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论 |
| 优先级 | P2 |

#### G11 第二批次策略（价值反转 / 动量趋势）
| 项 | 内容 |
|---|---|
| 所属 | 30_multi_strategy_concurrency §1.1（5 候选策略后 2 个） |
| 依赖 | G04 先跑 3 个月有 track record |
| 讨论要点 | ① 价值反转 alpha 信号 ② 动量趋势 alpha 信号 ③ 与首批 3 策略相关性 ④ 上线时机（首批 track record 后） |
| 产出物 | `27_second_batch_strategies_second_batch_strategies.md` |
| 对标 | AQR 价值/动量 / Fama-French |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 暂缓（首批上线 3 个月后再讨论） |
| 优先级 | P4（远期） |

---

### L2·组合仓位层

#### G12 仓位算法 spec（落地分层裁定）
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.1 |
| 依赖 | G04（选股结果）+ G05 |
| 讨论要点 | ① 策略层粗仓位（等权 / risk parity，**不用 Kelly**）② 组合层 Kelly 精裁决（MOD-POS-001）③ Kelly 参数（预期收益/方差估计来源）④ risk parity 具体公式（inverse-vol / Morwane 范式）⑤ 单票硬上限 8% 裁剪逻辑 ⑥ 现金管理 ⑦ 分层裁定的接口契约（StrategyBook 输出粗仓位→firm 层 Kelly 精裁决） |
| 产出物 | `31_position_sizing.md` |
| 对标 | Morwane inverse-vol risk parity / Kelly criterion 实证 / Morwane sleeve(alpha)+risk-parity-throttle(firm) 分层 |
| 正交性 | ✅ 与 regime 正交（regime 只缩 budget，不调仓位算法） |
| 状态 | ✅ 已定稿 v1.23.0（[31_position_sizing](31_position_sizing.md)） |
| 优先级 | P1（spec 层可先动） |

#### G13 FirmRiskAggregator 逻辑
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | G12（仓位算法） |
| 讨论要点 | ① 按标的求和（自然叠加，30_multi_strategy_concurrency §2.3）② 单票硬上限裁剪（>8% 按比例削）③ 行业/总仓位硬约束 ④ 冲突标的处理（一策略买一策略卖→净额 or 优先级）⑤ **不做 MVO，不做协方差估计**（30_multi_strategy_concurrency §3.1 拒绝）⑥ 输出 firm_target_portfolio 契约 ⑦ O(N) 复杂度保证 |
| 产出物 | `32_firm_risk_aggregator_firm_risk_aggregator.md` |
| 对标 | Citadel pod 模型 firm 层风险聚合 / Morwane risk-parity-throttle |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 框架已定（MOD-POS-021 已登记），逻辑细节待落 |
| 优先级 | P2 |

#### G14 BudgetChangeHandler 三级升级
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.4 |
| 依赖 | G12、G13 |
| 讨论要点 | ① Tier 1 封锁新仓（瞬时）② Tier 2 rebalance_to_budget 信号（策略自选砍仓）③ Tier 3 按比例强裁（firm 层兜底）④ convergence_window 按换手率差异化（30_multi_strategy_concurrency §6.4：打板 1-2 天/多因子 3-5 天/事件 2-3 天）⑤ rebalance_to_budget 接口契约（策略不能说"我不卖"）⑥ 每级独立 log/复盘 |
| 产出物 | `33_budget_change_handler_budget_change_handler.md` |
| 对标 | 机构级 budget rebalance 协议 |
| 正交性 | ⚠️ budget 来源依赖 RegimeMetaAllocator（G15），但三级升级逻辑本身正交 |
| 状态 | 框架已定（MOD-POS-022 已登记），窗口参数待校准 |
| 优先级 | P2 |

#### G15 RegimeMetaAllocator 参数
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | ⚠️ **依赖 11_regime_backtest_validation_plan C1 验证结果**（Shrinkage 有效性）+ G04（PerformanceScore 需策略 PnL） |
| 讨论要点 | ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` ② Base_i 先验权重 ③ PerformanceScore 60 日 Sharpe 映射 [0.5,1.5] ④ Shrinkage 置信度→风险节流映射（30_multi_strategy_concurrency §2.2 四档）⑤ floor≥5% / cap≤40% ⑥ 稀有态差异化收缩 ⑦ 第二阶段上线时机 |
| 产出物 | `34_regime_meta_allocator_regime_meta_allocator.md` |
| 对标 | Morwane risk-throttle / RegimeScore 移除裁定（30_multi_strategy_concurrency §2.2） |
| 正交性 | ⚠️ 本身就是 regime 节流的消费者，**等 C1 验证通过后再定参数** |
| 状态 | 框架已定（MOD-PA-007 已登记），参数待 C1 验证后校准 |
| 优先级 | P3（第二阶段，等 regime 验证 + 策略 track record） |

---

### L3·风控层

#### G16 回撤 Protocol 落地
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5 |
| 依赖 | G12（仓位）—— 但框架已有，可并行 |
| 讨论要点 | ① 四级阈值（8/15/20/25%）落到 StrategyBook 内部的实现 spec ② 单策略 vs 组合层面分层（§2.5.3）③ 恢复机制（企稳 50%/创新高/强制休息 5 天，§2.5.2）④ Kill Switch 触发条件与执行路径（§2.5.5）⑤ 日度熔断（组合 -4%/单策略 -5%）⑥ Kill Switch 不可覆盖原则 ⑦ 回撤基准净值计算口径 ⑧ 与 regime Shrinkage 的协同（drawdown 是账户风险，regime 是市场风险，§2.5 定位） |
| 产出物 | `35_drawdown_protocol_impl.md` |
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff（§2.5 已引） |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 状态 | ✅ active v1.34.0 |
| 优先级 | P2（与 G12 并行） |

#### G17 VaR/ES 与波动率监控
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.4 |
| 依赖 | G16 |
| 讨论要点 | ① VaR_95 计算（历史模拟/参数法）② ES_95 计算 ③ 入场 VaR/ES 基准 ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）⑤ 30 日波动率调整（每增10%→仓位减20%）⑥ 数据窗口 ⑦ 与回撤 Protocol 的协同 |
| 产出物 | `36_var_es_monitoring.md` |
| 对标 | 赢牛资管 VaR-ES / Sina 量化风控 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.6.0 |
| 优先级 | P3 |

#### G18 流动性危机处理
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.5 |
| 依赖 | G16 |
| 讨论要点 | ① 买卖价差监控（>正常 5x 触发）② 流动性危机→立即停止开仓仅允许平仓 ③ 流动性指标定义（换手率/成交额/盘口深度）④ 与 Kill Switch 的关系 ⑤ A 股涨跌停流动性失效处理 |
| 产出物 | `37_liquidity_crisis_protocol.md` |
| 对标 | tradingwyckoff Kill Switch / 机构流动性风控 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.0.16 |
| 优先级 | P3 |

---

### L4·交易流层

#### G19 买入流 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 06 |
| 依赖 | G04-G06（选股+板块）、G12（仓位）、G16（风控） |
| 讨论要点 | ① 分批建仓（BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C）② 突破失败降级 ③ 买入时序（盘中/盘后/集合竞价）④ 买入价格锚定 ⑤ 资金分配到多标的 ⑥ 与 budget 的协同 ⑦ T+1 约束 |
| 产出物 | `41_buy_flow_buy_flow.md` |
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
| 产出物 | `42_sell_flow_sell_flow.md` |
| 对标 | 机构卖出纪律 / O'Neil 卖出法则 |
| 正交性 | ⚠️ 情绪退潮卖出与 regime 协同（但 regime 只给 Shrinkage，卖出逻辑在策略内） |
| 状态 | 待讨论 |
| 优先级 | P3 |

#### G21 情绪周期×交易决策
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 05/06/07/09 |
| 依赖 | G04、G08（打板最依赖情绪周期） |
| 讨论要点 | ① 5 阶段（冰点/反核/主升/疯狂/退潮）各阶段的买卖纪律 ② 情绪周期定位器准确率评估（30_multi_strategy_concurrency §6.3）③ 情绪周期与 regime 12 态的映射关系 ④ 各策略在不同情绪阶段的部署策略 ⑤ 情绪周期是"隐形驱动"（30_multi_strategy_concurrency §1.3）→ 策略间相关性来源 |
| 产出物 | `28_sentiment_cycle_trading_sentiment_cycle_trading.md` |
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
| 产出物 | [40_execution_broker](40_execution_broker.md) |
| 对标 | miniQMT 文档 / 机构执行算法（TWAP/VWAP/IS） |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v2.9.2 + 代码已施工（commit 015826ae，2026-08-08，G22-AI） |
| 优先级 | P4 |

---

### L6·验证层

#### G23 回测框架对接
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义） |
| 讨论要点 | ① BM-BT-01~07 环节在策略验证中的用法（regime 验证已映射，见 11_regime_backtest_validation_plan §2.1）② 策略回测 vs regime 回测的差异 ③ 策略上线门控 IS→WFA→OOS（BM-BT-07）④ 过拟合检测三维度（BM-BT-05）⑤ Deflated Sharpe（BM-BT-05-G） |
| 产出物 | `52_backtest_framework_docking_backtest_framework_docking.md` |
| 对标 | 11_regime_backtest_validation_plan 已建立的对接范式 / Morwane walk-forward |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 状态 | 部分覆盖（regime 已对接，策略侧待补） |
| 优先级 | P2（G04 后） |

#### G24 模拟与实盘验证路径
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 04 |
| 依赖 | G23（回测通过） |
| 讨论要点 | ① 模拟验证（paper trading）环境 ② 模拟时长 ③ 实盘小资金验证路径 ④ 实盘→模拟差异监控 ⑤ 上线决策门控 ⑥ 灰度上线（单策略先上） |
| 产出物 | `53_simulation_live_path_simulation_live_path.md` |
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
| 讨论要点 | ① PnL 归因（策略贡献分解）② 每日对账（成交 vs 持仓 vs 资金）③ 归因维度（策略/标的/因子/时段）④ 与 StrategyBook 独立 PnL 归因的对接（30_multi_strategy_concurrency §2.2）⑤ 异常交易检测 ⑥ 报表生成 |
| 产出物 | `54_reconciliation_attribution.md` |
| 对标 | 机构中后台对账 / Barra 归因 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.14.0 |
| 优先级 | P5 |

#### G26 监控告警与复盘
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 |
| 依赖 | G25 |
| 讨论要点 | ① 系统健康监控（数据/引擎/下单链路）② 策略偏离监控（实盘 vs 回测）③ 告警阈值与通知 ④ 每日/每周/每月复盘机制 ⑤ 策略退役标准（连续跑输/逻辑失效）⑥ 复盘文档模板 |
| 产出物 | `55_monitoring_review.md` |
| 对标 | 机构 PM 周报 / 风控周报 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.21.0 |
| 优先级 | P5 |

---

### L8·跨切与治理层

#### G27 冲突矩阵清理与事件总线
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 12 |
| 依赖 | G04-G13（架构定型后才能清理冲突） |
| 讨论要点 | ① battle_map_12 §16 的 31 条跨策略冲突仲裁→大部分因 A 模型消失（30_multi_strategy_concurrency §7.3）② 仅留 firm-level 硬上限 ③ 事件总线/信号注入机制 ④ 实时计算节奏（盘中 vs 盘后）⑤ 配置驱动（参数热更新/AB 测试）⑥ 多策略投票降级（BM-SEL-20 已 rejected，§7.3） |
| 产出物 | `60_cross_cutting_cleanup.md` |
| 对标 | 机构事件总线 / 微服务信号路由 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.8.0 |
| 优先级 | P3（架构定型后） |

#### G28 策略生命周期与多 AI 协作
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 01/02/03/04 |
| 依赖 | 全局 |
| 讨论要点 | ① 策略生命周期（孵化→训练→回测→模拟→实盘→退役，对应作战地图 01-04/11）② 研究孵化阶段（BM-RES）规范 ③ 模型训练阶段（BM-MOD）规范 ④ 多 AI 协作分工规范（另一 AI 做 regime，本边做选股，交接点）⑤ 文档治理（design_memo 编号体系，本文档建立）⑥ creation_token / depgraph 登记流程 |
| 产出物 | `61_lifecycle_multi_ai.md` |
| 对标 | MLOps 生命周期 / 机构策略研发流程 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v2.9.1 |
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
- **理由**：仓位/风控框架已定（30_multi_strategy_concurrency §2.1/§2.5），spec 层可不等选股细节先动；待 G04 产出后接口对齐
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

> 30_multi_strategy_concurrency §2.2 核心裁定：**regime 只做风险节流（Shrinkage），不做 alpha 择时；不参与选股，只参与 budget 缩放。**

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
2. 该 AI 首读本文档 + 30_multi_strategy_concurrency + 相关作战地图
3. AI 按本主题组的"讨论要点"逐项讨论，与用户对齐
4. 讨论定型后落盘产出物（discussion_NNN / design_memo_NNN）
5. 涉及模块施工的，按 management_spec §2.2 流程登记 depgraph

### 7.2 交接点纪律
- **AI 间不直接通信**，通过产出物（discussion/design_memo）+ depgraph path 交接
- 认领 G05 的 AI 必须先读 G04 的产出物 `20_first_batch_strategies`
- 认领 G12 的 AI 必须先读 30_multi_strategy_concurrency §2.1 分层裁定
- 所有 AI 必读：30_multi_strategy_concurrency（架构总纲）+ 本文档（路线图）

### 7.3 编号占用表（避免冲突）

> ⚠️ 2026-08-09 起改段位编号制，下表已同步更新为新名。2026-08-10 第二轮版本同步：所有"骨架已建 v0.1.0"已更新为实际 active 版本。新文档按 §8 段位规则命名，不再使用此表分配编号。

> 认领时在此登记，避免产出物编号冲突。

| 产出物编号 | 主题组 | 认领方 | 状态 |
|---|---|---|---|
| 10_regime_detector_spec | G02 regime spec | 另一AI | ✅ v1.9.37 |
| 11_regime_backtest_validation_plan | G03 regime 验证 | 另一AI | ✅ v1.10.0 |
| 20_first_batch_strategies | G04 首批3策略 | G04-AI | ✅ v1.2.0 |
| discussion_004 | ⚠️ 编号冲突已澄清：代码误用此号指代 13 号文档（Phase 3 降维裁定）；G06 板块轮动实际产出物为 `22_sector_rotation_spec.md` | — | 已澄清 |
| 15_data_feature_layer_spec | G01 数据特征层 | ✅ 已定稿 | active v1.21.2 |
| 21_stock_selection_engine | G05 选股引擎 | ✅ 已定稿 | active v1.1.18 |
| 22_sector_rotation_spec | G06 板块轮动 | ✅ 已定稿 | active v1.8.0 |
| 23_strategy_correlation_validation | G07 相关性验证 | ✅ 已定稿 | active v1.7.0 |
| 24_daban_strategy_detail | G08 打板细节 | ✅ 已定稿 | active v1.9.7（8 要点+12 施工算法） |
| 25_multifactor_strategy_detail | G09 多因子细节 | ✅ 已定稿 | active v1.12.11（6 要点+8 施工算法+Phase 4 栈） |
| 26_event_driven_strategy_detail | G10 事件驱动 | ✅ 已定稿 | active v1.8.0 |
| 27_second_batch_strategies | G11 第二批次 | （待认领） | draft v0.4.0（暂缓讨论） |
| 35_drawdown_protocol_impl | G16 回撤落地 | ✅ 已定稿 | active v1.34.0 |
| 36_var_es_monitoring | G17 VaR/ES | ✅ 已定稿 | active v1.8.0 |
| 37_liquidity_crisis_protocol | G18 流动性危机 | ✅ 已定稿 | active v1.0.16 |
| 28_sentiment_cycle_trading | G21 情绪周期 | ✅ 已定稿 | active v1.11.0 |
| 52_backtest_framework_docking | G23 回测对接 | ✅ 已定稿 | active v1.7.4 |
| 53_simulation_live_path | G24 模拟实盘 | ✅ 已定稿 | active v1.6.6 |
| 55_monitoring_review | G26 监控复盘 | ✅ 已定稿 | active v1.21.0 |
| 12_regime_phase2_validation | Phase 2 模型质量验证（工程文档，非G主题） | 已落地 | ✅ v0.2.0 |
| 50_backtest_observability_workplan | 回测可观测性工作计划（工程文档，非G主题） | 已提议 | 待确认 |
| 13_regime_phase3_engineering_plan | Phase 3 工程规划（工程文档，非G主题） | 已提议 | 草案 |
| 90_methodology_open_questions | 方法论遗留提案（工程文档，非G主题） | 已提议 | 待讨论 |
| 91_density_prediction | 密度预测远期愿景（工程文档，非G主题） | 已提议 | 待讨论 |
| 51_panel_experiment_history_mlflow_retirement | Panel 实验历史 Tab + mlflow 退役施工计划（工程文档，非G主题，50_backtest_observability_workplan M2 下游） | 已提议 | 待施工 |
| 30_multi_strategy_concurrency | 多策略并发架构 | ✅ 已定稿 | active v2.5.0 |
| 31_position_sizing | G12 仓位算法 | ✅ 已定稿 | active v1.23.0 |
| 32_firm_risk_aggregator | G13 FirmRiskAggregator | ✅ 已定稿 | active v1.0.20 |
| 33_budget_change_handler | G14 BudgetChangeHandler | ✅ 已定稿 | active v2.10.0 |
| 34_regime_meta_allocator | G15 RegimeMetaAllocator | ✅ 已定稿 | active v2.7.0（⚠️参数等C1） |
| 41_buy_flow | G19 买入流 | ✅ 已定稿 | active v1.5.1 |
| 42_sell_flow | G20 卖出流 | ✅ 已定稿 | active v1.5.2 |
| 40_execution_broker | G22 下单对接 | G22-AI | ✅ v2.9.2 + 代码已施工 |
| 54_reconciliation_attribution | G25 对账归因 | ✅ 已定稿 | active v1.14.0 |
| 60_cross_cutting_cleanup | G27 冲突矩阵清理 | ✅ 已定稿 | active v1.8.0 |
| 61_lifecycle_multi_ai | G28 生命周期多AI | ✅ 已定稿 | active v2.9.1 |
| 19_northbound_hold_snapshot | 北向季度快照 fetcher（数据地基层子项） | 待施工 | draft v0.1.0 |
| 64_data_source_download_spec | G29 数据源与下载体系（跨切治理层·6x 段位） | 待讨论 | draft v1.0.0 |

## 8. 产出物命名规范

遵循 [management_spec §4.1](01_design_memo_management_spec.md)：
- 全部文档：`<段位号>_<topic>.md`（topic 为 snake_case 主题）
- 段位语义：**0x** meta｜**1x** 地基（regime/数据特征）｜**2x** Alpha 策略｜**3x** 组合仓位与风控｜**4x** 交易执行｜**5x** 验证与可观测性｜**6x** 跨切治理｜**9x** 开放问题与远期
- 新文档按业务域入段，段内取下一个空号；不预留坑位
- 全部 snake_case，遵循项目命名铁律
- status 枚举：`active`（已定稿/已落地）/ `draft`（草案/待讨论/待施工）/ `deprecated`（废弃）

**历史**：2026-08-09 前使用 `discussion_NNN` / `design_memo_NNN` 双前缀制，因前缀与内容性质错位、编号断档严重而废止。新旧名对照见 §10。
## 9. 待人决策的开放问题汇总

> 以下问题需用户拍板，散落在各主题组内，集中索引便于追踪。

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 首批 3 策略确认（打板+多因子+事件驱动） | 30_multi_strategy_concurrency §6.1 / G04 | ✅ 已定 v1.2.0（20_first_batch_strategies；主升龙头并入打板，多因子新增） |
| convergence_window 按换手率定（打板1-2/多因子3-5/事件2-3天） | 30_multi_strategy_concurrency §6.4 / G14 | 待首批策略定后校准 |
| 情绪周期定位器准确率评估 | 30_multi_strategy_concurrency §6.3 / G21 | 待评估 |
| regime 检测器业务规则 spec | 30_multi_strategy_concurrency §6.6 / 10_regime_detector_spec | ✅ 已定 v1.9.37 |
| 12 态×N 策略样本量 | 30_multi_strategy_concurrency §6.5 | ✅ 已决策（灰度+软分配） |
| 第二批次策略上线时机 | G11 | 暂缓（首批 track record 后） |
| G15 RegimeMetaAllocator 上线 | G15 | ⚠️ 等 C1 验证 |

### 9.1 2026-08-11 第一性原理调研发现的 35 项缺失议题（全部 status=proposed）

> 来源：客观架构师对标专业机构 + 量化社区 + 氛围编程社区的差距分析报告。
> 决策依据：5 条第一性原理（P1 资金安全 / P2 回测可复现 / P3 状态确定性 / P4 决策可追溯 / P5 风险不可累积）。
> 替代机制：项目已有 `ruling_registry.yaml`（裁定#NNN 含 `superseded_by` 链，可推翻）替代 ADR（ADR 不可推翻，对个人项目是过度工程），故不引入 ADR。
> 完整议题内容见 [architecture_issue_registry.yaml](../../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 末尾 35 条新增条目。

#### AI 治理类（10 项，#ARCH-AIGOV-001~010）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-AIGOV-001 | PATH-shim git wrapper 补充拦截 git commit --no-verify（65 号 §7.1 扩展） | P0 致命 | proposed |
| #ARCH-AIGOV-002 | Secret 双层扫描（pre-commit detect-secrets + post-push GitGuardian） | P0 致命 | proposed |
| #ARCH-AIGOV-003 | Library Hallucination 检测（Mypy + Pyright + 包名验证） | P0 致命 | proposed |
| #ARCH-AIGOV-004 | Revertability git 四步纪律（push before risky run） | P0 致命 | proposed |
| #ARCH-AIGOV-005 | 对抗式多 agent（生成/审查/测试分离，禁止单 agent 自审） | P1 高 | proposed |
| #ARCH-AIGOV-006 | AGENTS.md 嵌套就近优先（拆分 327KB 根文件） | P2 中 | proposed |
| #ARCH-AIGOV-007 | 静态分析反馈环（Bandit+Pylint+CodeQL→AI 修复迭代） | P1 高 | proposed |
| #ARCH-AIGOV-008 | 多层 Guardrails（pre/post-input/tool-call/output） | P1 高 | proposed |
| #ARCH-AIGOV-009 | Patchwork Problem 图不变量验证框架 | P2 中 | proposed |
| #ARCH-AIGOV-010 | OWASP Agentic Top 10 安全扫描（agent-audit CI 集成） | P1 高 | proposed |

#### AI 协作类（1 项，#ARCH-AICOLLAB-001，方案已写入 65 号 §12）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-AICOLLAB-001 | Git Worktree + File Lock(TTL) + Task Board 三件套（26 路协调层） | P1 高 | proposed（方案已落 65 号 §12，另一 AI 正施工） |

#### 机构风控类（5 项，#ARCH-RISK-001~005）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-RISK-001 | Kill Switch 经纪商侧硬止损（miniQMT 平台崩溃托底） | P0 致命 | proposed |
| #ARCH-RISK-002 | 7-Trigger 熔断器（补"系统错误频发"触发） | P0 致命 | proposed |
| #ARCH-RISK-003 | 14-Check 事前风控（A 股特化） | P0 致命 | proposed |
| #ARCH-RISK-004 | 单笔风控 L1（0.5-1% risk / 最小 R:R 2:1） | P0 致命 | proposed |
| #ARCH-RISK-005 | 3-Tier 回撤协议（Green/Amber/Red 中间态减仓） | P1 高 | proposed |

#### 量化架构类（5 项，#ARCH-QUANT-001~005）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-QUANT-001 | 回测-模拟-实盘同一内核（NautilusKernel 式抽象） | P1 高 | proposed |
| #ARCH-QUANT-002 | Crash-only 设计 + 状态外部化（Redis） | P1 高 | proposed |
| #ARCH-QUANT-003 | 53_simulation_live_path 5 态 FSM 状态机代码落地 | P1 高 | proposed |
| #ARCH-QUANT-004 | pf_core / pf_alloc / ex_sor 三个 stub 落地 | P1 高 | proposed |
| #ARCH-QUANT-005 | VaR → ES 范式迁移（ES 进决策层） | P2 中 | proposed |

#### 治理/注册表类（5 项，#ARCH-REG-001~005）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-REG-001 | factor_registry schema + provenance | P1 高 | proposed |
| #ARCH-REG-002 | strategy_registry 退役状态机 | P1 高 | proposed |
| #ARCH-REG-003 | 策略衰减检测（30 天滚动 + 20% 退化阈值） | P1 高 | proposed |
| #ARCH-REG-004 | MLOps 四支柱简化版（无 model card） | P2 中 | proposed（用户已裁定不引入 model card） |
| #ARCH-REG-005 | 多策略独立 sub-book + 归因到"框架决策 vs override" | P2 中 | proposed |

#### A 股特化类（2 项，#ARCH-ASHARE-001~002）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-ASHARE-001 | 北向资金配置型/交易型双结构信号 + regime 信号源 | P1 高 | proposed |
| #ARCH-ASHARE-002 | 情绪周期 6 阶段标准化 + 4 盘面指标自动检测 | P1 高 | proposed |

#### 合规类（1 项，#ARCH-COMPLIANCE-001，P0-5 与 P2-8 合并）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-COMPLIANCE-001 | 2026-06-08 程序化交易新规模块（5000 笔预警 + 撤单率 80% + 存档 20 年） | P0 致命 | proposed |

#### SDD / 审计 / drift / 执行 / CI / 注册表治本（6 项）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-SDD-001 | GitHub Spec Kit / AWS Kiro SDD 四阶段闭环 | P2 中 | proposed |
| #ARCH-AUDIT-001 | 简化版 IETF AAT audit trail（SHA-256 + action classification + tamper-evident，砍个体归属） | P1 高 | proposed（用户已裁定简化） |
| #ARCH-DRIFT-002 | Spec drift detection CI job（design_memo 与代码漂移自动检测） | P1 高 | proposed |
| #ARCH-EXEC-001 | 40_execution_broker 10 项 P0 gap 落地 | P0 致命 | proposed |
| #ARCH-CI-001 | CI 真正运行（首次 push origin/dev + 后续自动触发） | P0 致命 | proposed（循环审查第 1 轮追加） |
| #ARCH-REGCAN-001 | ROOR entry_count 自动同步 reconciler（治本元数据漂移） | P1 高 | proposed（循环审查第 1 轮追加） |

#### 已排除项（用户裁定不引入）

| 项 | 不引入理由 |
|---|---|
| P1-10 ADR supersede 链 | 项目已有 `ruling_registry.yaml`（裁定#NNN 含 `superseded_by` 链，可推翻）完美替代 ADR；ADR 不可推翻对个人项目是过度工程 |
| P2-5 model card 部分 | 用户裁定不引入 model card（量化策略不是 ML 模型，无需伦理考虑），保留 MLOps 其他三支柱 |
| 测试覆盖率监控 | 用户裁定不引入（个人项目 158 处 TODO/stub，强制阈值太严；靠对抗式多 agent + 静态分析反馈环已够） |
| 部署运维（Docker 真用） | 用户裁定不引入（65 号 §4.1 已确认 Trae IDE + Windows 本地环境，纯本地开发，Docker 是过度工程） |

#### 状态汇总

- **登记总数**：35 项（全部 `status=proposed`，铁律#9 决策类议题待用户确认）
- **优先级分布**：P0 致命 11 项 / P1 高 17 项 / P2 中 7 项
- **域分布**：AI 治理 10 / AI 协作 1 / 机构风控 5 / 量化架构 5 / 治理注册表 5 / A 股特化 2 / 合规 1 / SDD 1 / 审计 1 / drift 1 / 执行 1 / CI 1 / 注册表治本 1
- **第一性原理覆盖**：P1 资金安全 ✓ / P2 回测可复现 ✓ / P3 状态确定性 ✓ / P4 决策可追溯 ✓ / P5 风险不可累积 ✓
- **用户裁定记录**：Git Worktree 三件套全部加入（写入 65 号 §12）/ SDD 全部加入 / IETF AAT 简化版 / model card 不引入 / 测试覆盖率不引入 / Docker 部署不引入

## 10. 改名对照表（2026-08-09 文档体系重排）

| 旧名 | 新名 |
|---|---|
| discussion_000_discussion_framework.md | 00_index_trading_decision.md |
| design_memo_management_spec.md | 01_design_memo_management_spec.md |
| discussion_001_regime_detector_spec.md | 10_regime_detector_spec.md |
| discussion_002_regime_backtest_validation_plan.md | 11_regime_backtest_validation_plan.md |
| discussion_017_phase2_model_quality_validation.md | 12_regime_phase2_validation.md |
| discussion_019_phase3_engineering_plan.md | 13_regime_phase3_engineering_plan.md |
| discussion_023_s2_algorithm_misalignment_diagnosis.md | 14_regime_s2_diagnosis.md |
| discussion_003_first_batch_strategies.md | 20_first_batch_strategies.md |
| design_memo_001_multi_strategy_concurrency.md | 30_multi_strategy_concurrency.md |
| design_memo_004_position_sizing.md | 31_position_sizing.md |
| design_memo_010_execution_broker.md | 40_execution_broker.md |
| discussion_018_backtest_observability_workplan.md | 50_backtest_observability_workplan.md |
| discussion_022_panel_experiment_history_tab_and_mlflow_retirement.md | 51_panel_experiment_history_mlflow_retirement.md |
| discussion_020_methodology_open_questions.md | 90_methodology_open_questions.md |
| discussion_021_density_prediction.md | 91_density_prediction.md |

> 旧"编号占用表"预定坑位（design_memo_002/003/005-009/011-013、discussion_004-016）同步废止，未来文档按 §8 段位规则命名。
> ✅ 已修正（2026-08-09）：discussion_004 §2.1/§2.2 全仓统一替换为 13_regime_phase3_engineering_plan §2.1/§2.2——13 号文档即代码所引用内容，章节号完全对应，无需补落盘。

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-06 | 1.0.0 | 初稿 | 建立 28 个主题组（G01-G28）的讨论框架路线图，供多 AI 分工认领；梳理依赖关系与 3 条并行轨道；建立产出物编号占用表 |
| 2026-08-07 | 1.1.0 | §7.3 标记 G04/G12/G22 认领状态为已分配 | 三主题组分配给并行 AI 开工，避免后续编号撞车 |
| 2026-08-08 | 1.2.0 | 20_first_batch_strategies 占用状态更新为 ✅ v1.0.0；§9 首批3策略开放问题标记已定 | G04-AI 落盘 20_first_batch_strategies（首批3策略=打板+多因子+事件驱动；主升龙头并入打板，多因子新增；§1.4 对齐 charter §3 裁定 Model A 非 Citadel pod） |
| 2026-08-08 | 1.3.0 | 20_first_batch_strategies 占用状态同步至 ✅ v1.2.0（补施工流程+灰度判据）；G22 40_execution_broker 状态更新为"代码已施工" | 20_first_batch_strategies 经多轮审查迭代至 v1.2.0（补施工环节流程算法+2026灰度判据）；G22-AI 完成 40_execution_broker 代码施工（commit 015826ae） |
| 2026-08-08 | 1.4.0 | 51_panel_experiment_history_mlflow_retirement 落盘登记 | Panel 实验历史 Tab + mlflow 退役施工计划定稿（50_backtest_observability_workplan M2 下游），补 §七 10 项施工算法补遗 + §八 4 项后续增强登记 |
| 2026-08-09 | 2.1.0 | §3 G06 产出物改为 `22_sector_rotation_spec.md`；§7.3 discussion_004 占用行澄清为编号冲突；全仓 `discussion_004`→`13_regime_phase3_engineering_plan`（保留 §2.1/§2.2 章节号） | `discussion_004` 从未落盘，代码/11号文档误用此号引用 13 号文档（Phase 3 降维 §2.1 + 校准器 §2.2）；G06 板块轮动与 regime 降维无关 |
| 2026-08-09 | 2.2.0 | §0 目录 14_regime_s2_diagnosis 状态 active→draft、51_panel 状态 draft→active 对齐各文档 frontmatter；补登 12/13/14/50/90/91 六篇改名修订记录 | 00_index §0 目录与各文档 frontmatter status 一致性；上一轮改名工程遗漏的六篇修订记录补齐 |
| 2026-08-09 | 2.3.0 | §0 目录 15→38 篇（新增 23 篇骨架文档行 + 状态图例）；§7.3 占用表 23 项状态更新为"骨架已建 v0.1.0"，补登 22_sector_rotation_spec（G06）占用行 | 施工图骨架先行：G01-G28 全部待讨论主题组的产出物骨架一次性落盘（frontmatter status=draft，仅含主题组信息+讨论要点清单，§2-§6 待填空），统一结构后再逐篇讨论填空；22 号此前仅有 discussion_004 澄清行、无独立占用行 |
| 2026-08-09 | 2.3.1 | 关联行+§3/§5/G22 产出物行修复 7 处重复后缀断链（`_name_name.md`→`_name.md`，涉及 30/10/11/31/40 号） | 改名工程遗留：段位前缀重复拼接产生断链，全量断链扫描发现并修复 |
| 2026-08-09 | 2.4.0 | 15 篇有内容文档文档头统一登记：frontmatter 字段集/顺序统一（补齐 title/owner/language/topic/scope，12/13/14 的 doc_id/priority/depends_on 等扩展字段保留），H1 去前缀与 title 对齐（废止"讨论框架·/讨论文档·/讨论·/设计备忘·/讨论稿：/NN_filename —"六种混用风格），修订记录各补一行（14 号补建修订记录章节）；00 自身同步 | 骨架体系收尾：结构统一只动文档头元数据与标题行，章节编号与正文内容零变更、零遗漏风险；规范真源见 01_design_memo_management_spec §4.2/§4.3（v1.1.1 同步） |
| 2026-08-10 | 2.4.1 | 40号 v2.9.0→v2.9.1 版本同步：§2.12通道平权行补2026-07-31正式关闭局域网行情通道事件 | 40号§2.12监管约束表"通道平权"行从"已推进"更新为完整事件描述——2026-07-31交易所正式关闭局域网行情通道，微秒级延迟→毫秒级，量化从拼速度转向拼深度，与项目中低频+因子驱动定位一致 |
| 2026-08-10 | 2.5.0 | 系统性版本同步+61号arXiv:2608.01789整合 | ①批量frontmatter核对发现21个文档已升级为active但00_index仍标注"骨架v0.1.0"（15/21-23/25-26/28/32-37/41-42/52-55/60-61），§0目录表+§7.3占用表共40处版本引用更新为实际frontmatter版本；②61号§3.2补arXiv:2608.01789自主Alpha发现综述六组件统一框架作为理论参照（八篇候选统一分类视角，Memory组件覆盖最薄弱印证FactorMiner独特价值）|
| 2026-08-10 | 2.6.0 | 系统性版本同步第二轮+缺失文档补登+61号漂移检测体系增强 | ①§0目录补登5篇缺失文档（16号×2/18号/62号/63号）；②§0目录+§7.3批量版本同步：36号v1.0.0→v1.2.0/55号骨架→v1.21.0/54号骨架→v1.13.0/60号骨架→v1.8.0/61号骨架→v2.9.1/30号v1.3.0→v2.5.0/31号v1.2.0→v1.23.0/G02 v1.3.1→v1.9.25/G03 v1.0.0→v1.10.0；③G09状态从"骨架v0.1.0"更正为"active v1.12.6"（重大状态失同步修复）；④G16/G17/G18/G25/G26/G27/G28状态从"待讨论/框架已定"更新为对应active版本号+修复6处重复后缀断链；⑤61号§3.3漂移检测体系补Modular CP via Residual Decomposition（arXiv:2510.04406阶段级归因）+SA-BCP（arXiv:2605.00432时空解耦CP），漂移归因从"特征级→资产级"扩展为"特征级→阶段级→资产级"三级体系 |
| 2026-08-10 | 2.7.0 | §0目录+§7.3补登19号 | 北向日频断档后实测 akshare 三接口失效/tushare hk_hold 季度末可行，新建 19_northbound_hold_snapshot 施工计划（fetcher+落表+外资行为方法论），1x段位新占19号 |
| 2026-08-10 | 2.7.1 | §0目录+§3+§7.3+§9 第三轮系统性版本同步 | 持续改进：用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。frontmatter 批量核对发现 4 篇文档版本失同步：①10号 v1.3.1→v1.9.31（§0目录/§3 G02/§7.3/§9 开放问题 4 处）；②25号 v1.12.6→v1.12.11（§0目录/§3 G09/§7.3 3 处+施工算法数 6→8）；③35号 v1.30.6→v1.32.0（§0目录/§3 G16/§7.3 3 处）；④36号 v1.2.0→v1.6.0（§0目录/§3 G17/§7.3 3 处）。本轮同步为版本号对齐，无文档结构调整 |
| 2026-08-10 | 2.8.0 | §0目录补登 64 号+§7.3 占用表补登 64 号 | 用户要求新建专门聊"数据集成下载/数据下载/数据源"的设计备忘录，把项目里所有已施工落盘的数据源/下载相关内容全面写入作为讨论升级载体。64_data_source_download_spec.md 落盘（6x 段位 64 号·跨切治理层，1x 地基层 10-19 已满；与 63 号数据利用审计配套——63 审"用得怎么样"64 审"下得怎么样"）。spec 工程详设类，§3-§10 按数据获取管线 8 对象分节，§12 缺口与升级方向含 12 项待裁定+12 个开放问题。§0 目录 43→44 篇 |
| 2026-08-10 | 2.8.1 | §0目录+§3 G16+§7.3 35号版本同步 | 35_drawdown_protocol_impl frontmatter 已升级至 v1.34.0，00_index 三处版本引用仍标 v1.32.0（§0目录第56行/§3 G16状态行第310行/§7.3占用表第603行），本次同步为 v1.32.0→v1.34.0 版本对齐，无文档结构调整 |
| 2026-08-10 | 2.8.2 | §0目录+§3+§7.3+§9 第三轮版本同步 | 第三轮版本同步——10号 v1.9.31→v1.9.37、24号 v1.9.4→v1.9.7、40号 v2.9.1→v2.9.2，三处 frontmatter 版本漂移修复 |
