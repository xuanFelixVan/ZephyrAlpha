---
ttl: permanent
doc_type: architecture_view
title: 方法论约束遗留提案
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.0.3"
date: 2026-08-15
topic: methodology_open_questions
scope: 07_trading_decision_architecture
---

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**（开放式问题文档——本体任务=逐项裁定）：21 项遗留提案已于 v2.0.0（2026-08-12 架构审查终审）全部完成裁定并升 active（维持 4 / 新裁定 10 / 合并 2 / 暂缓·远期 2 / 待用户裁定 P-1~P-5）；「已施工设施盘点」（8 已施工/8 部分/5 未施工）与注册表建成态为裁定提供实证底座。本篇自身的"提案评审"职能已闭环。
>
> **最终成果**（2026-08-19 实证）：每项裁定含结论+施工方案+过度工程审查；讨论优先级表已转施工优先级表（Phase 1 三项 + Phase 2 十一项 + 暂缓/远期 + P-1~P-5 待人裁定）；§22 五个作战地图 design 环节登记远期/Phase 2 候选并附边界消歧。
>
> **未做事项及原因**（施工优先级表的衍生施工承诺——2026-08-19 代码实证全部未施工）：
> - P1 三项：① #5 cost_model_registry 做T成本条目 CST-T0-001（实证：注册表零命中）+ 最低佣金 5 元建模确认；② #13 benchmark_registry 增补中证1000/中证2000/万得全A（实证：注册表零命中）；③ #19 algo_execution_selector 默认限价单 + 打板专用执行路径（实证：未见配置项落地）。均属登记待排期；裁定=未来工程-小型。
> - P2 十一项：#2 BHY FDR 校正+滚动分位嵌入 decay_monitor（实证：src 零命中）/ #8 liquidity_monitor 压力退出时间+LVaR 简化式+跌停 ST 维度（实证：零命中）/ #9 半衰期样本权重（实证：零命中）/ #15 universe_registry 两维字段 / #16 生存线监控落码（55 号范围）/ #17 单一订单出口验证+YAML 规则归并 / #18 Instrument Master 轻量表 / #20 策略指纹库+DTW+correlation_gate 持久化 / #21 做T 四规则配置化（实证：零命中）/ #14 deliberate future-date 泄漏测试自动化 / #1 新增策略族归属声明治理流程（零代码即时生效）。均属 Phase 2 登记待排期；裁定=未来工程-小型（单件均 ≤100 行，建议组 1-2 个专项小批清偿）。
> - #7 T+1 8 态预测 / #10 密度预测——已裁定暂缓建设/远期维持（重启条件未达）；裁定=过度工程（当前阶段；91 号承载密度预测规划态登记）。
> - P-1~P-5（Wasserstein 收敛 / Conformal 五变体栈 / Robust HMM 选型 / RL 执行 / 过拟合检测协议）——仍全部待用户裁定（方向已给；A2 PASS 后 P-1/P-3 紧迫性已下调）；裁定=待 Owner。
> - §22 五环节：BM-SEL-05-D/05-E/06/10 远期候选 MVP 不建（重评条件在档）——裁定=过度工程（当前阶段）；BM-SEL-26 C-030 决策溯源链 Phase 2 候选——裁定=未来工程-小型（结构化决策快照最小实现先行）。

# 方法论约束遗留提案

> **状态**：21 项遗留提案。#1-#11 源自原《能力定位书》§3 约束一~十三；#12-#21 源自系统宪章多轮精简移出项（成功指标/基准/PIT/资产分级/行为边界/资产覆盖/大额下单/工程细节/做T方法论）。
>
> **v2.0.0 全量裁定（2026-08-12，架构审查终审）**：21 项遗留提案**全部完成裁定**，文档从 draft 升 active。逐项裁定分布见下表「v2.0.0 裁定」列（维持 4 / 新裁定 10 / 合并 2 / 暂缓·远期 2）；📝 待用户裁定 5 项（P-1~P-5 方向已给，见「待定问题」节）。
>
> **v2.0.0 重要更正**：
> ① 11 号 v1.5.2 确认 A2 验证器降 4 态后已 **PASS**（OOS/IS=1.042）——Wasserstein HMM 降为 Phase 3+ 可选增强（详见 §7）；
> ② 91 号实际仅 v0.1.2 骨架，本文档引用的"91 号 v0.4.0~v1.4.0"内容（四阶段路线/RWC/Lévy/Exformer）**均未落盘到 91 号**，标注为规划态；
> ③ 30 号锚点更新至 v2.5.0（Kelly 已升级 Fractional Kelly 25-50% 三档演进，PerformanceScore 口径已改 Sortino）；
> ④ §3 FirmRiskAggregator 模块编号 MOD-POS-001→MOD-POS-021 修正；
> ⑤ #5 印花税"千1"→卖出单边万5（2023-08 减半后现行）；
> ⑥ BM-BT-07/BT-10 状态三方口径对齐（decision_gate.py 策略路径已 production，regime 验证 Phase 5 门控未完成；BT-10 PIT 已 production）。
> 新增「已施工设施盘点」节（通用规则 #11）。v0.2.0~v1.18.1 历次审查（逐项对齐现状+补施工算法缺口+登记 2026 选项外更优算法，过度工程纠偏贯穿、MVP 零新增）明细已并入正文各节"2026 补充论据"与文末修订记录。
>
> **重要**：讨论时以项目实际代码和已定稿文档为准。regime 检测器实际实现为 **4 态 HMM + 3 overlay = 7 维概率**（非 spec 12 态，详见 §7 更正要点）。

## 遗留提案总览

| 原编号 | 主题 | 对应G主题 | 与现状的关系 | v2.0.0 裁定 |
|:------:|------|:--------:|-------------|:-----------:|
| 约束一 | 策略类型目录(6大类) | G04 | 项目实际"首批3策略"；registry 6类口径（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）与本稿6大类不一致 | ✅ 修订采纳（四族双层标注，原6大类表 deprecated） |
| 约束二 | 因子分类与IC阈值 | G01 | G01因子工程总纲已定稿（15号），IC阈值未验证 | ✅ 修订采纳（静态地板+滚动分位双轨+BHY FDR+ICIR≥0.5） |
| 约束三 | 组合构建硬约束 | G12 | ✅ 已裁定：30_multi_strategy 定 risk parity + Kelly firm层，非risk budgeting | ✅ 维持（锚点更新 v2.5.0，MOD-POS-021 编号修正） |
| 约束四 | 风险模型(L1/L2/L3) | G16-G18 | ✅ 已裁定：30_multi_strategy §2.5 定 4级回撤Protocol(8/15/20/25%)，非L1/L2/L3 | ✅ 维持（代码 5/10 阈值与文档 8/15/20/25 口径对账待 G13/G14） |
| 约束五 | 成本模型细节 | G22 | 宪章只保留成本结构(不含费率)，细节待讨论 | ✅ 简化采纳（砍 Almgren-Chriss MVP、最低佣金5元显式建模、印花税更正万5） |
| 约束七 | 回测门禁(V1~V6) | G23 | ✅ 已裁定：项目用 BM-BT-01~07 体系，V1-V6 已映射（见 §6） | ✅ 维持（BT-10 PIT 已 production、BM-BT-07 口径澄清） |
| 约束九 | T+1次日预测(8态) | G02 | 8态(BM-SEL-04)是独立下游消费者(未建)；8态→直接决策映射过时(Model A) | ❌ 暂缓建设（52-53%天花板未突破，远期窄目标重启条件已定义） |
| 约束十 | 流动性风险 | G18 | G18已定稿（37号 v1.0.16），liquidity_monitor(Amihud) 已 production | ✅ 简化采纳（压力退出时间>1天→禁开仓；LVaR 简化式 Phase 2） |
| 约束十一 | 数据分层使用(Layer0~4) | G01 | Layer2 引用已更正为 regime 检测；样本权重代码未施工 | ✅ 修订采纳（半衰期 HL 2-3年参数化；断裂期降权保留不剔除） |
| 约束十二 | 密度预测(QNN) | 无 | 已拆为91_density_prediction独立讨论（⚠️ 91号实际 v0.1.2 骨架，引用内容未落盘） | ⏸️ 远期维持（Phase 0 基线=slow unweighted conformal，91号待回填） |
| 约束十三 | 仓位管理(C-047) | G12/G13 | ✅ 已裁定：30_multi_strategy §2.1/§7.2 用 MOD-POS-020/021/022，非C-047 | ✅ 维持（半Kelly→Fractional Kelly 25-50% 锚点更新） |
| §9移出 | 成功指标交易参数 | — | 阈值拍脑袋未验证 | ✅ 并入 #16（线性收紧规则 deprecated，已被4级Protocol替代） |
| §3移出 | 基准设计 | — | benchmark_registry 已建（沪深300/中证500/中证全指/绝对收益） | ✅ 修订采纳（sleeve级多基准；废弃60/40拼合基准） |
| §3移出 | PIT一致性 | — | pit_query + pit_manager 已 production | ✅ 确认已施工（双值存储等价语义已覆盖；泄漏检查增强 Phase 2） |
| §4移出 | 资产分级(P0-P3) | — | universe_registry 已建（static/dynamic/rule_based） | ✅ 修订采纳（两维精简：准入×数据覆盖；P0-P3 deprecated） |
| §9移出 | 系统级成功指标 | — | KPI 监控代码未施工（55号 draft） | ✅ 修订采纳（生存线下调 Sharpe≥0.8；健康/卓越线实盘6-12月校准） |
| §5移出 | 行为边界(B-002~B-005) | G16/G22 | 43门禁+风控强制+时段校验已施工；OPA 未施工 | ✅ 修订采纳（拒绝 OPA；choke point+YAML规则，OPA 降远期） |
| §4移出 | 资产与市场覆盖 | — | instrument 契约+symbol_normalizer+~100 schema 已施工 | ✅ 修订采纳（轻量 Instrument Master 表 Phase 2，拒绝重型系统） |
| B-013.6 | 大额下单 | G22 | ex_sor TWAP/VWAP/POV/ICEBERG 已施工 | ✅ 修订采纳（默认限价单+打板专用路径；删5%ADV硬条款；算法执行降远期） |
| B-008/010/012/013 | 工程细节 | — | echo-guard/退役/相关性门禁已施工；指纹库/DTW 未施工 | ✅ 逐项裁定（B-010 三维指纹 Phase 2；B-012/B-013 归治理文档闭环） |
| — | 做T方法论 | — | 3个做T策略+tick基类+回放已 production | ✅ 采纳为受约束 overlay（sizing/regime过滤/失败处置/冲突管理四规则） |

---

## 已施工设施盘点（v2.0.0 新增，通用规则 #11）

> 盘点日期 2026-08-12。范围：src/zephyr/ 代码、docs/01_policies_and_standards/_registry/catalogs/ 注册表、schemas/、tests/、治理脚本。**先清楚有什么→才知道怎么改→才知道该删除/退役什么**。21 项中 8 项已施工、8 项部分施工、5 项未施工（施工缺口均已在对应条目登记 Phase 2 方案）。

| # | 主题 | 判定 | 已施工设施（证据路径） | 缺口 |
|---|------|:----:|----------------------|------|
| 1 | 策略类型/工厂/注册表 | 🟧 部分 | `catalogs/strategy_registry.yaml`（REG-STR-001 active，6类口径=daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation，含 lifecycle/decay/capacity 字段）；`governance/strategies/strategy_base.py` StrategyRegistry（production）；`pf_core/strategy_engine/strategy_runner.py`（MOD-L05-001） | 独立 strategy_factory 模块未建（runner autodiscover 已覆盖注册职能） |
| 2 | 因子分类与IC | 🟦 主干 | `catalogs/factor_registry.yaml`（含 ic_mean/icir 阈值字段）；`factor/analysis/` 全套（ic_decay/ic_ir_calc/decay_monitor/three_level_judgment/correlation_analyzer）+ `governance/factor_pool_manager.py`（8状态生命周期）+ 测试齐备 | SHAP 未施工；多重检验校正（Bonferroni/BHY）未施工 |
| 3 | 组合构建 | 🟦 已施工 | `position/core/strategy_book.py`（MOD-POS-020 production，equal_weight/risk_parity/custom，显式禁 Kelly/MVO）；`firm_risk_aggregator.py`（MOD-POS-021 production，pre_kelly_aggregate→Kelly→post_kelly_clip，kelly_param_source="density_pdf" 接口预留）；`budget_change_handler.py`（MOD-POS-022）；`pf_alloc/core/regime_meta_allocator.py`（MOD-PA-007，Shrinkage 只减不增、floor 5%/cap 40%） | 30号 §7.2 自注 RegimeMetaAllocator 代码仍骨架（C1验证已过） |
| 4 | 风险模型 | 🟦 已施工 | `position/core/drawdown_controller.py`（MOD-POS-008 production：5级 VaR 风险级 GREEN~BLACK + Soft 5%/Hard 10% 策略止损 + 黑天鹅 7 模式）；`risk/core/var_calculator.py`+`var_backtester.py`+`tail_risk_monitor.py`+`stress_test_engine.py`；kill_switch 三处实现；`catalogs/risk_limit_registry.yaml`（9类限额） | ⚠️ 代码阈值（Soft 5%/Hard 10%）与文档 4级 Protocol（8/15/20/25%）双轨并存，30号 §2.5 已自注"须 G13/G14 明确映射"——对账未闭环 |
| 5 | 成本模型 | 🟦 已施工 | `catalogs/cost_model_registry.yaml`（CST-ASTOCK-001：佣金万3/印花税万5/过户费/滑点；slippage_model: fixed/linear/square_root）；`ex_sor/services/slippage_analyzer.py`（平方根冲击律 impact=coeff×√participation×vol_bps）；`transaction_cost_optimizer.py`（Kyle λ 简化） | 做T额外成本专门条目未建 |
| 6 | 回测门禁 | 🟦 主干 | 双引擎 `backtest/implementations/vectorized_engine.py`+`event_driven_engine.py`；`core/decision_gate.py`（MOD-BT-001 production：IS Sharpe>0.5→WFA 多数通过+灾难否决→OOS≥70% IS；偏差>30%告警/>50%退役）；`core/overfitting_detector.py`（三维度）；`core/walk_forward.py`；`core/tick_replay.py`；`simulation/deflated_sharpe_calculator.py` 代码已存在 | Purged K-Fold/Permutation Test/PBO 未施工（文档级）；CPCV 配置预留；⚠️ BM-BT-05-G（DSR）battle_map 标 design 但代码已存在——口径需对账 |
| 7 | T+1 次日8态预测 | ⬜ 未施工 | 仅登记：BM-SEL-04 status=design（10号 §2.1"下游消费者，非检测器本身"） | 全部未建——v2.0.0 裁定暂缓建设 |
| 8 | 流动性风险 | 🟧 部分 | `risk/core/liquidity_monitor.py`（production：Amihud ILLIQ+成交量萎缩比率+HALT/WARNING，已接入 default_risk_manager_orchestrator，有测试）；37号流动性危机 memo | LVaR、退出时间估算、流动性评分体系、跌停/停牌概率维度未施工 |
| 9 | 数据分层 | 🟧 部分 | `docs/.../contracts/data_retention_contract.yaml` 10层留存分层（数据治理语义）；`config/data/survivorship_policy.yaml` | 训练样本 Layer0-4 分层+指数衰减/半衰期样本权重未施工（与留存分层语义正交） |
| 10 | 密度预测 | ⬜ 未施工 | `feedback_loop/evolution/conformal_prediction.py` 简易 CP 骨架（进化模块用，非市场密度）；firm_risk_aggregator `kelly_param_source="density_pdf"` 消费接口预留 | RWC/LSTM+GMM/MDN 均未实现；91号文档 v0.1.2 骨架待回填 |
| 11 | 仓位管理 | 🟦 已施工 | `position/core/` 14 模块全家桶（position_sizing_engine MOD-POS-001、position_drift_monitor MOD-POS-003、position_audit_logger MOD-POS-009 哈希链、position_limit_enforcer 单票≤5%NAV、rebalance_engine、cash_manager 等） | ±2%/±3% 漂移带数值未在源码直接确认（drift monitor 存在，阈值在 blueprint/配置）；"再平衡收益>2×成本"规则无显式实现（30号用 ε_pos=5% 收敛容差+no-trade 半带 Phase 2 候选替代） |
| 12/16 | 成功指标/KPI | ⬜ 未施工 | 相邻设施：`config/sli_registry.yaml`+`alert_rules.yaml`（基础设施 SLO，非交易 KPI）；decision_gate "偏差>50%退役"是最接近的健康线逻辑 | 生存/健康/卓越/失败四档监控代码未建（55号 monitoring draft） |
| 13 | 基准设计 | 🟦 注册表 | `catalogs/benchmark_registry.yaml`（REG-BMK-001：沪深300/中证500/中证全指/绝对收益，含 active_share/style_drift_detection 字段）；`backtest/core/metrics.py`；`pf_core/core/performance_attribution_engine.py` | 中证1000/中证2000/万得全A sleeve 级基准条目未登记；benchmark_symbol 仅字符串未结构化（注册表自注） |
| 14 | PIT一致性 | 🟦 已施工 | `data/pit_query.py`（announce_date<=query_time+LIMIT 1 BY 取查询时点最新版本+embargo_clause+AS OF JOIN，白名单财务表）；`backtest/core/pit_manager.py`（PIT三公理+pit_consistency_test）；`scripts/arch_guard/fitness_functions/check_survivorship_bias.py`；测试齐备 | 术语映射：first_filed≈announce_date（已覆盖）；重述双值=ClickHouse ReplacingMergeTree 版本语义（等价覆盖）；deliberate future-date 泄漏测试未自动化 |
| 15 | 资产分级 | 🟧 部分 | `catalogs/universe_registry.yaml`（REG-UNI-001：static/dynamic/rule_based 三型；UNI-RULE-001 全A可交易池[剔ST/退市风险/次新<60天/日均成交额<1000万]） | P0-P3/eligible 三态未施工；流通市值分层字段未建；tradability_mask 函数代码零命中 |
| 17 | 行为边界 | 🟧 部分 | 43门禁引擎 `gov_enforcement/rule_enforcement/gate_engine/gate_engine.py`+`_registry.yaml`；`scripts/git_guard.py`；`risk/risk_limits.py`+`implementations/default_position_limit_checker.py`+`g7_position_limits.yaml`（集中度/仓位上限）；`ex_core/trading_session.py`（时段校验）；`programmatic_trading_guard.py`/`cancel_rate_guard.py`/`price_cage.py` | OPA/Rego 未施工（v2.0.0 裁定拒绝，改 choke point 方案）；单一订单出口架构确认待验证（40号 G22 已施工 commit 015826ae） |
| 18 | 资产与市场覆盖 | 🟧 部分 | `trading/trading_contracts/market/instrument.py`（Stock/ETF/Future/Option/Bond/FX/Crypto 契约）；`data/symbol_normalizer/normalizer.py`；schemas ~100 类（A股/ST/港股/可转债/期货/期权/ETF/LOF/美股/指数成分/日历） | 独立 Instrument Master 主数据模块未建；ST 状态 PIT 跟踪散见于 universe 过滤规则未独立成表 |
| 19 | 大额下单/算法执行 | 🟦 MVP | `ex_sor/core/algo_execution_selector.py`（TWAP/VWAP/ICEBERG/POV 选择器，>5%ADV 倾向 ICEBERG，决策留痕）；`algo_trading_engine.py`；ADV/参与率计算在 slippage_analyzer；`reporting/default_tca_engine.py`（TCA） | v2.0.0 裁定默认路径改限价单——选择器默认策略配置项待调（非新建） |
| 20 | 工程细节 | 🟧 部分 | echo-guard/CodeSAGE（`echo-guard.yml`+`clone_guard/engines/echo_guard_adapter.py` 主检测引擎+多引擎聚合器）；策略退役 lifecycle（strategy_registry candidate→retired）+`pf_alloc/strategy_lifecycle_event.py`；decay_monitor 双实现；`pf_alloc/core/strategy_correlation_gate.py`（MOD-PA-004：>0.85 REJECT/>0.90 HARD_REJECT/尾部相关0.70） | 策略指纹库未建；DTW PnL 相似度未施工；intent netting 零命中；90天滚动相关持久化条件未确认 |
| 21 | 做T | 🟦 已施工 | `pf_core/intraday_surge_fall_strategy.py`（30秒冲高回落）+`orderbook_imbalance_strategy.py`（盘口失衡）+`vwap_reversion_strategy.py`（VWAP回归）+`strategy_engine/tick_strategy_base.py` 基类+`backtest/core/tick_replay.py` 回放引擎；测试齐备 | 做T sizing/regime过滤/失败处置/冲突管理四规则未配置化（v2.0.0 裁定补齐）；做T成本条目（见#5） |

**注册表配套（12 个业务注册表已建 6 个）**：✅ factor/strategy/universe/benchmark/cost_model/risk_limit；❌ technical_indicator/execution_algo/data_asset/chart_pattern/field_dictionary/experiment（62 号文档规划中，`experiment_tracking/` 代码模块已施工但注册表未建）。

**盘点结论对裁定的约束**：① 凡"已施工"项的裁定以代码真源为准（不做文档级重复设计）；② 缺口项全部登记 Phase 2 施工方案（见各条目"施工方案"），MVP 零新增——符合 system_charter §2 硬边界（单人单机不新增架构组件）；③ 需退役/降级的历史内容在各条目标 deprecated，不删除（保留历史可追溯）。

---

## 1. 策略类型目录（原约束一）

> 对应 G04（首批3策略定义）｜ ✅ **v2.0.0 裁定：修订采纳（四族+管线双层标注），原 6 大类表 deprecated**

**✅ v2.0.0 裁定结论**：

- **本质**：策略分类的目的是隔离收益来源、衰减假设与风控属性，不是越细越好。2026 业界/社区已收敛到"按收益来源"的四族（动量趋势/因子投资/均值回归/事件驱动），本稿原 6 大类按"信号来源"分类且与 strategy_registry.yaml 实际登记的 6 类（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）口径不一致。
- **裁定**：① **原 6 大类表（动量/均值回归/价值/事件驱动/做T/防御）标 deprecated** 作历史参考——其中"防御"不是策略族而是 regime 下组合层风控行为（归 34 号 Shrinkage 节流），"做T"不是独立策略族而是底仓 overlay（见 §21）；② **项目现行口径以 strategy_registry.yaml 6 类为真源**（已施工注册表），新增策略沿用该 6 类声明族归属，四族+管线谱系作分析标注层（四族管"是什么 alpha"，管线管"在哪个环节"）；③ **首批 3 策略 ⊂ 目录关系确认**：打板=事件驱动族×短线情绪动量交叉（daban）、多因子=因子投资族（multifactor）、事件驱动=事件驱动族（event_driven）；④ **策略工厂强制目录内生产——采纳为治理规则**：AI 生成策略必须声明族归属+alpha 假设+容量，防无法归类的过拟合怪物（经 strategy_registry candidate 状态+43 门禁强制）。
- **施工方案**：零新增施工——strategy_registry.yaml 已有 lifecycle/capacity/decay 字段，新增策略登记时强制族归属声明即可（治理流程，Phase 0 生效）。
- **过度工程审查**：四族标注是元数据非新架构；不建独立 strategy_factory 模块（strategy_runner autodiscover 已覆盖注册职能）。✅ 通过。

**原始内容（deprecated，保留作历史记录）**：

| 策略大类 | 子类 | 信号来源 | 适用市场状态 |
|---------|------|---------|------------|
| 动量类 | 趋势跟踪/突破/动量反转/板块轮动 | 量价因子 | ①②③趋势向上/⑪板块轮动 |
| 均值回归类 | 统计套利/配对交易/超跌反弹 | 价差/估值因子 | ④⑤震荡/⑥压缩突破 |
| 价值类 | 深度价值/GARP/质量因子 | 基本面因子 | ④⑤震荡/①②趋势向上 |
| 事件驱动类 | 财报超预期/政策催化/重组 | 事件因子+另类数据 | ⑩事件驱动叠加态 |
| 做T类 | 日内T+0套利(底仓) | 分时因子+波动率 | ③⑥高波动列 |
| 防御类 | 低波动/红利/对冲 | 风险因子 | ⑦⑧⑨趋势向下 |

**原待讨论问题（已闭环）**：6大类框架是否采用/与首批3策略关系→✅ 四族+registry 6类双层，首批3策略映射已确认；策略工厂是否强制目录内生产→✅ 采纳为治理规则。

**2026 补充论据**：

- **四族分类+管线谱系（v0.4.0）**：四族（vzeman 2026-05）=A 动量/趋势（cross-sectional momentum 12-1，net Sharpe ~0.65）/B 因子投资（Big Five value/momentum/quality/size/low-vol）/C 均值回归 StatArb（pairs+OU）/D 事件驱动；管线谱系（Shehral 2026-04）=六阶段信息处理管线（数据获取→信号生成→组合构建→交易执行→风险管理→元层编排），暴露跨领域依赖。项目映射：首批 3 策略落 B+D 两族；原"做T类/防御类"归入 C（日内均值回归）/B（low-vol 因子）。
- **打板环境剧变实证（v0.6.0，东方财富 2026-08-03）**：打板次日平均溢价 2023 年 4.2%→2026 年 **1.7%**（高位科技涨停次日溢价中位数为负），炸板率 40%→**68%**；量化成交占全市场 35%+（中小盘题材 50%+），完整复刻游资盘口特征成"最大对手盘"；2026-04 程序化新规（实时监控多账户联动/大额对倒/频繁撤单，申报速率≤15笔/秒、撤单率≤15% 硬约束已在 24 号登记）。情绪量化算法：legulegu 6 指标评分（封单强度/炸板率/连板转化率/涨停成交额/封板效率/涨停均市值，0-100）；炸板率 4 阶段（<20% 高潮/30-50% 分歧/>50% 退潮/极高回落冰点）对应项目情绪周期 4+1 阶段。**启示**：① 打板 alpha 衰减须纳入 §20 Alpha Decay 监控；② 24 号需补炸板率/溢价率情绪门控（退潮期>50% 炸板率停打板）；③ 策略从"跟游资"转向"反量化"（低位干净筹码小票+事件催化新题材）。
- **打板筛选施工算法（v0.7.0）**：akshare 连板接力筛选（CSDN 2026-08-05 开源：股价≤30元/总市值≤300亿/流通市值≤250亿/最后封板≤14:30/炸板≤5次/排除断板再涨停/**封成比≥5%**；排序=连板数降序→首次封板时间升序）——直接补 24 号"涨停时间分层量化"施工缺口；6 维度涨停规律（犇犇浅谈 2026-08，3200 只复盘）4 个分时硬性指标（90% 时间均价线上方回踩秒级收回/2-3 次脉冲试盘冲高 2-4% 回落/全天振幅≤2.5%/压力位大单压盘不砸盘）可作前置筛选特征，与 24 号 BM-SEL-22 短线评分卡 7 维互补（91% 隔日涨停概率为社区声称值，需独立回测）；8 月游资转型实证（电子板块主力净流出 187 亿/12 算力龙头减持 22%/工业富联盘中跌停）确认剧变结论。
- **开源打板工具生态（v0.8.0）**：short-term-stock-picker（MIT，6 维筛选+评分系统，可作 BM-SEL-22 对照）；A-Share-Sector-Alpha-Hunter（板块"蓄势弹簧"+小盘 Bottom 20%）；stk_explore zhangting.py（同花顺+akshare 双数据源+历史封板率字段）。三维筛选=历史封板率+当日封成比+6 维度规律。
- **Tail-Aware MDN（v1.0.0，arxiv 2601.14049 Paris-Dauphine + ESANN 2026 扩展）**：skewed Student-t MDN 专攻 locally explosive time series，与打板"涨停→炸板"动力学原生匹配（右偏涨停上限+左重尾炸板暴跌，Gaussian mixture 需 5+ 分量近似）；dual reweighting 解决炸板日稀有极端事件学习不足+post-hoc PIT recalibration（conformal 校准区间的密度预测对应）；配套 local explosive dynamics 检测（Blasques/Koopman JTSA 2025 46(5):966-980）作气泡态前置门控（检测到气泡→炸板防御模式）。定位：91 号 Phase 1 LSTM+GMM 的"算法替换"升级（Gaussian→skewed t），非新增栈。Lévy 家族升级交叉引用（v1.3.0，见 91 号 v1.2.0 规划态）：DeepLévy（α-stable mixture+CFM，α<2 方差无限）极端尾部升级+Lévy-Flow（VG/NIG normalizing flow，VaR Kupiec p=1.00）Phase 2 生成式替代——Student-t/α-stable/VG-NIG 三家族重尾密度谱系，Student-t 族是 baseline。
- **tick size 归一化存活判据（v1.14.0，arxiv 2607.01550 Kurth/Eisler/Rej/Bouchaud）**：~100 种流动性期货（1995-2025）文档化 2009 年后短期趋势跟踪 PnL 崩塌，横截面存活判据=波动率归一化 tick size（小 tick 合约崩塌、大 tick 保持；机制=HFT 做市商在小 tick 稀疏订单簿撤流动性打破自我实现反馈循环）。打板标的 tick 占比约 0.01%-0.2% 属"小 tick"类——启示是量化对手盘流动性撤回加剧炸板风险（与 24 号 §2.4 PEAD Inversion 协同），期货趋势结论不直接迁移。定位：20/24 号策略容量评估诊断指标（`tick_size_pct=0.01/close`，成本=0），Phase 2 动量趋势 sleeve 扩展时作标的筛选维度（优先股价≥50 元或 tick 占比≥0.5%）。

---

## 2. 因子分类与IC阈值（原约束二）

> 对应 G01（数据与特征层规范）｜ ✅ **v2.0.0 裁定：修订采纳（双轨阈值 + BHY FDR + ICIR≥0.5）**

**✅ v2.0.0 裁定结论**：

- **本质**：IC 门槛的真正问题是多重检验下的假阳性控制，不是绝对水平。2026 实证：A 股 |IC|>0.02 微弱有效、>0.05 优秀、ICIR>0.5 可用；qlib Alpha158 基准 RankIC≈0.04-0.05；|IC|>0.1 大概率有前视偏差。
- **裁定**：① **静态地板保留**（|RankIC|≥0.03 量价 / 0.02 基本面 / 0.025 另类）——与研究共识不冲突，作快速初筛；② **叠加相对轨道**：同类因子滚动 RankIC 分布前 50% 分位（抗 regime 漂移，替代"绝对阈值一刀切"）；③ **硬性统计门禁**：ICIR≥0.5 + BHY 控制 FDR q=10%（单批筛选 >100 因子时 t 门槛升 2.8，Harvey-Liu-Zhu 标准）；④ **5 大类入池角色保留**（量价/基本面/另类/宏观/风险），与项目 factor 域 10 类属性分类（value/quality/momentum/...）正交并存——前者管"入池角色与阈值"，后者管"因子属性标注"，映射关系待 G01/15 号对齐；⑤ 另类因子样本短，静态门槛仅辅助，以 3 个月样本外跟踪为准。
- **Alpha 因子入池流程**（闭环原待讨论问题）：IC/RankIC 回测 → BHY FDR 校正 → ICIR≥0.5 → 滚动分位前 50% → factor_pool_manager candidate 状态 → 3 个月样本外跟踪 → active。
- **施工方案**：① **BHY FDR 多重检验校正**（factor/analysis/ 新增 ~80 行，statsmodels multipletests 直接可用，Phase 2）；② 滚动分位评估嵌入 decay_monitor（Phase 2）；③ SHAP 非线性评估（远期，Phase 3+，借开源库）；④ GP 自动因子挖掘（远期探索，非 MVP）。集成点：factor_pool_manager 入池门禁（abs001_gate）。
- **过度工程审查**：BHY 是统计标准工具非新架构；SHAP/GP 均降级远期。✅ 通过。

**原始内容**：

| 因子大类 | 入池IC阈值 | 在组合中的角色 |
|---------|-----------|-------------|
| 量价因子 | \|IC\|>0.03 | Alpha来源 |
| 基本面因子 | \|IC\|>0.02 | Alpha来源+风险控制 |
| 另类因子 | \|IC\|>0.025 | Alpha补充 |
| 宏观因子 | —（不直接入池） | 市场状态判定输入 |
| 风险因子 | —（不要求IC） | 风险分解+中性化 |

**原待讨论问题（已闭环）**：IC 阈值依据→✅ 双轨化+2026 实证锚点；5 大类分类是否合理→✅ 保留并与 10 类属性正交；Alpha 因子入池流程实现→✅ 见上流程链。

**2026 补充论据**：

- **SHAP 评估 + GP 发现（v0.3.0/v0.5.0）**：SHAP（MSCI 2026-03 因子评估标准：一致性公理+非线性交互+全局/局部解释，可揭示因子贡献跨 regime 漂移）与 IC 互补不替代（IC 快速初筛管线性，SHAP 深度评估管非线性）；MinShap（arxiv 2604.15107）识别非冗余特征；注意：高相关数据归因稀释→需 VIF 过滤或 Group Shapley，随机背景数据集→前视偏差须严格时序滚动窗口，SHAP 是统计相关非因果。**发现维度**：遗传规划自动挖掘（终端集=基础数据，函数集=rank/ts_corr/delay 算子，适应度=IC/Sharpe；AlphaNet 用深度学习替代）+EAFD（arxiv 2603.15713，LLM 自反思特征生成 +5.8%）；GP 计算量大且易过拟合，列 G01 远期探索（非 MVP）。
- **PPO 自适应 alpha 加权（v0.7.0，arxiv 2509.01393 U Hyogo）**：PPO agent 实时调整 50 个 formulaic alpha 权重（状态=波动率+近期收益+信号相关性，奖励=Sharpe 惩罚 MaxDD），多数情况 Sharpe 更高+MaxDD 更小——核心价值抗 alpha decay（动态重分配资本远离衰减信号）。与 25 号五静态方法（IC 加权/等权/回归/max_ir/min_variance）互补，列 25 号 Phase 2 远期（IC 半衰期加权先行）。
- **LLM+多智能体+PPO 三层框架（v0.8.0，PeerJ cs-3630）**：LLM 语义层+5 专业 agent 协作层+PPO 决策层（波动率调整仓位+交易成本感知）；OOS 2024-07~2025-06 平均年化 **53.87%**/Sharpe **1.702**/MaxDD **12.54%**（vs B&H 0.765），vs 15 基线 DM p<0.0001，消融证实三层协同 +15.35pp。定位 25 号 Phase 3+ 远期终局（MVP 五静态方法→Phase 2 PPO 单层→Phase 3+ 三层框架）。
- **CGX 对抗辩论 + 多智能体细化三研究（v0.8.0/v0.9.0）**：CGX（MDPI Electronics 15:3453）Bull/Bear 三轮结构化辩论+Meta-Evaluator 共识门控，52 周 Sharpe **1.90**，4 年多 regime 验证 **MaxDD 降 85%/波动率降 86%**（2022 熊市 Bear gate 阻止 93% sessions）——28 号情绪周期 LLM 化 Phase 4+ 远期选项（情绪周期管"什么阶段"，CGX 管"该不该交易"）。细化三研究：F²Agent（arxiv 2608.05668 NUS，多模态+modality-aware adaptive fusion，GOOG 120.48%/TSLA 148.41%）；市场依赖通信（arxiv 2511.13614 CMU，450 实验：竞争式适用高波动科技股/协作式适用稳定股/金融股抵抗所有通信；对话质量与收益零相关）；MarketSenseAI（arxiv 2604.17327，ICIR +0.489，agent 贡献随 regime 轮换非主导 agent）。共同启示：关键在通信/融合设计非 agent 数量；A 股小盘低效市场更适用；可对接 regime→agent 权重映射。均 28 号 Phase 4+ 远期。
- **Cross-Sectional Heterogeneity LSTM（v1.4.0，arxiv 2608.05755 Döbelt）**：learnable sector embeddings+宏观协变量+label smoothing/dropout/gradient clipping，S&P 500 long-short 超基准+可解释 sector contribution 归因——是 25 号合成前"输入端截面增强"（非新增架构，~50 行）+22 号板块轮动的板块向量表示；A 股板块效应更强预期增益更大。Phase 1.5+（对接 91 号 v1.3.0 截面特征增强，规划态）。
- **Body-Tail Factor Test + Robust Spatial-Sign 检验（v1.11.0）**：Body-Tail（arxiv 2606.23596 Shin）分解因子收益 body/tail——q5 因子 spanning 最强但 body alpha 负、tail alpha 正，A 股涨跌停下 IC 可能被 tail 主导而 body 无信号；对每个候选因子同报 body IC+tail IC+total IC，淘汰"total 正 body 负"伪信号（~50 行，25 号 Phase 2）。Spatial-Sign（arxiv 2604.12252）重尾+时变系数+高维 N>T 场景鲁棒的因子显著性检验（优于 GRS/sub-Gaussian 方法），替代 IC t 检验作重尾默认检验（~60 行，Phase 2）。
- **Uncertainty-Adjusted Sorting（v1.12.0，arxiv 2601.00593）**：不确定性调整预测区间替代点预测排序，增益主要来自波动率降低（避开高不确定性股票），灵活 ML 模型上最强，区间部分错误设定仍鲁棒。与 25 号 ML 合成栈正交：LambdaRankIC 管训练目标/RankGLU 管预测头/本项管组合构建排序（"训练→输出→排序"各自独立增强）；A 股涨跌停/停牌/缺口使不确定性天然偏高，与 Mask-First 掩码协同两层防御。~30 行，Phase 4 ML 合成引入后启用。
- **财信"情绪浓度"第三维（v1.13.0，财信证券 2026-08-10 三维情绪模型周报）**：情绪浓度=中信三级行业指数收益率 PCA 第一主成分方差贡献率（低频 ~30 天），高浓度→Beta 行情/低浓度→Alpha 分化，>0.83 警戒线+顶部形态预示拐点。28 号已有 5 阶段情绪温度但无"行业联动度"维度——情绪浓度管"资金是否共识"，与 22 号虹吸态（管"资金往哪去"）正交；数据源 sector_snapshot（582 只板块指数）已有，PCA ~20 行。温度维重叠不整合、预期维（期货升贴水+PCR）无数据接入不适用。28 号 Phase 2 远期候选（浓度>0.83 触发退潮预警，领先评分降级 1-2 日）。
- **IGF BBP 相变因子数检测（v1.14.0，arxiv 2607.06908 García-Medina）**：自适应 Marčenko-Pastur 边缘重校准+participation-ratio 去局域化滤波，BBP 相变附近同时检查谱分离+特征向量延展性恢复真实因子数（S&P 500 中位 7 个，比 Onatski 更丰富）。与 15 号 v1.19.0 RMT 去噪权重层正交（IGF 管"有多少因子"的检测层，RMT 管"怎么加权"），~80 行，15 号 Phase 2+（因子池 20+ 时启用）。
- **量化"双杀"拥挤度实证（v1.6.0，数据详见附录 A.3）**：机制=因子拥挤→同质化集中平仓→多杀多。印证因子拥挤度监控必要性，指标：① 因子收益相关性趋 1；② top-N 持仓重叠率；③ 换手率趋同；④ 外部信号（北向集中度/龙虎榜抱团度）。与 32 号 correlation_dedup 互补（策略间事后去重 vs 因子间事前监控）。25 号 Phase 2。

---

## 3. 组合构建硬约束（原约束三）

> 对应 G12（仓位算法spec）｜ ✅ **已裁定（2026-08-05，30_multi_strategy；v2.0.0 锚点更新至 v2.5.0）**

**原始内容**：

| 层次 | 选择 | 核心规则 |
|------|------|---------|
| 信号→仓位 | 风险预算(Risk Budgeting) | 不可使用等权或固定比例 |
| 仓位上限 | 市场状态驱动动态调整 | ①②80%→⑨10%共9档+2叠加态；市场状态仓位上限为硬上限，风险预算不可超过 |
| 再平衡 | 日频信号驱动+周频强制再平衡 | 每周五收盘后强制再平衡 |
| 集中度 | 行业偏离≤基准±10%（⑪时±15%，绝对上限30%）；风格暴露≤±0.3标准差 | 条件性硬约束+风格中性化 |

**✅ 裁定结论**：30_multi_strategy_concurrency §2.1 已定 **Model A（独立账本 + firm 风险聚合）**，分层裁定如下（v2.0.0 注：30 号已演进至 v2.5.0——firm 层 Kelly 升级为三档演进：Phase 1 Fractional Kelly 25-50%、Phase 2 Bayesian Kelly、Phase 3 远期 Conformal Kelly；PerformanceScore 口径 Sharpe→Sortino；具体 fraction 待 31 号 G12 标定）：
- **策略层（StrategyBook）**：risk parity / 等权（**不用 Kelly，不用 MVO**）——"风险预算"方案被 risk parity 替代
- **组合层（MOD-POS-021 FirmRiskAggregator）**：Kelly 精裁决 + 求和 + 硬上限裁剪（**不做 MVO，不做协方差估计**）【v2.0.0 修正：原稿误标 MOD-POS-001——MOD-POS-001=position_sizing_engine，FirmRiskAggregator=MOD-POS-021，见 30 号 §7.2】
- **meta 层（RegimeMetaAllocator）**：regime 灰度概率→Shrinkage 风险节流（**仅节流不重定向**），budget 公式 = normalize(Base × PerformanceScore × Shrinkage)
- **市场状态→仓位**：不通过"9档+2叠加态硬映射"，而是 Shrinkage 置信度→风险节流映射（max(P)<60%→Shrinkage 0.3 … >95%→1.0）
- **再平衡**：budget 变动三级升级（Tier1 封锁→Tier2 自平衡→Tier3 强裁），非固定周频

**2026 行业实证**：Columbia arxiv 2412.12350（2024-12）多因子中性策略对比 equal-weight/risk parity/min-variance，**risk parity 胜出**（更高 Sharpe、更低 beta、更小 MaxDD）；ersantana.com（2026-03）risk parity=equal risk contribution，比 Markowitz 稳定、对收益预测不敏感，2026 主流；Morwane/multi-strategy-alpha-book（30 号 §7.4 核心实证）risk-parity 基准 Sharpe +1.43，regime 风险节流后 MaxDD −14.2%→−10.3%，Calmar +38%。

**risk parity 远期递进谱系（均非 MVP）**：naive risk parity（inverse-vol，MVP 现状）→ HRP（long-only）/ TRP（long-short+信号）→ RRP（A 股实证优化）→ Certified W-DRO → W-GAN 生成式 → MFCCA 多重分形 → MINGLE 因子-图联合。逐项要点：
- **HRP（v0.8.0，López de Prado）**：相关性矩阵层次聚类+自顶向下分配风险，解决 naive inverse-vol 忽略策略间相关性（高相关策略合计风险预算过高）；无需协方差求逆（数值稳定），危机期相关性飙升时更鲁棒。对接：复用 23 号 PnL 相关性矩阵作聚类输入，聚类层级=策略族；与 34 号 Shrinkage 正交（HRP 管静态风险分配，Shrinkage 管 regime 动态节流）。Phase 2 演进，待 G12 细化聚类阈值与重平衡频率。
- **TRP 拓扑风险平价（v1.5.0，arxiv 2604.16773 FMI Technologies）**：直击 HRP 两大局限——① HRP 仅 long-only，TRP 原生多空（w_v=s_v×g_v，正信号→多头/负信号→空头）；② HRP 纯风险分配忽略 alpha 信号，TRP 保留信号方向。方法：相关性-距离图提取稀疏有根 MST+Mantegna 距离+Mixed Split-Replication 系数 α_u(ρ)=(1-ρ)+ρ/b(u)（ρ=0 纯信号归一化/ρ=1 保守等分）+L1 归一化到目标杠杆。Semi-Supervised 变体 II"市场根→行业 ETF→个股"直接对接 22 号板块轮动（申万一级 28 行业作第二层）；ρ 可对接 regime（r3 牛市低 ρ 信号驱动/r4 熊市高 ρ 保守）。~150 行（MST+DFS），Phase 2（与 HRP 二选一：long-only 用 HRP，long-short 用 TRP）。
- **RRP（v1.6.0，Finance Research Letters vol.92(C) 2026）**：risk parity+adaptive perturbation+GARCH 波动率预测+市场状态识别+factor-structured covariance；**中国市场 2012-2024 实证全面优于 TRP/EW/GMV**（A 股 native 实证是最大优势，可复用 10 号市场状态输出+15 号因子暴露矩阵）。Phase 2+ 远期候选。
- **Certified Wasserstein DRO / C-WRP（v1.0.0+v1.6.0，arxiv 2608.07032 Hsieh&Gan）**：Wasserstein 模糊集（经验分布中心+距离半径 δ）内 worst-case 期望效用最大化；order-1+box support+one-norm 下对偶化为多项式规模 LP+certified approximation error bound，476-1000 资产月频可扩展。显式建模"收益分布本身的不确定性"（δ→0 退化经验分布/δ→∞ 过度保守），与 HRP（管相关性结构）、Kelly（管仓位缩放）正交。配套：Shift-Aware δ 校准（arxiv 2512.16748 Columbia，Gaussian-supremum validation+block bootstrap，防固定 δ 在 regime 切换下过保守/不达标——**δ 选择 delicate 是关键告诫**）；Wasserstein-Kelly（JUSTC 2025 USTC，Kelly 分布鲁棒版凸规划可解）。与 #7 Wasserstein HMM（regime 层）构成"Wasserstein 家族"（regime/组合/仓位三层统一鲁棒性度量）。Phase 4+ 远期（MVP 三因子乘法 O(N) 先行，C-WRP 需凸优化求解器复杂度不符）。**生成式扩展（v1.1.0，Huang et al. preprints 2026-02-28）**：WGAN 重建收益潜在分布（捕获非高斯特征+尾部依赖）+模糊集鲁棒优化，与 Certified DRO 分工（经验分布 LP 轻量 vs GAN 表达尾部依赖但训练重），与 91 号 Phase 2 GPD/TailGAN 共享 GAN 栈，Phase 4+ 远期（⚠️ preprint 需独立验证）。
- **MFCCA 多重分形组合分配（v1.3.0，arxiv 2608.04987 Kakinaka&Umeno）**：带符号波动函数作风险泛函（同向/反向运动以相反符号贡献风险，符号保持比波动阶聚合对尾部风险贡献更大），q=2 退化为 mean-variance 的尺度依赖极限；样本内外均降 drawdown/VaR/ES 不损失收益。补 23 号策略相关性的方向维度（Pearson 只看幅度）。Phase 4+/5+ 远期。
- **MINGLE 因子-图联合（v1.9.0，arxiv 2608.06618 Imperial，评估后不采纳 MVP）**：ADMM 联合学习潜在因子暴露+暴露相似性图（替代 HRP/TRP 的观测相关性图，图更对齐经济部门、regime 稳定性更好）。不采纳理由：复杂度与已拒绝 HRP/MVO 同类，5 策略规模边际收益不显著，因子暴露矩阵估计引入不稳定性。**Phase 5+ 远期重评条件：策略数>8 且 32 号 correlation_dedup 漏检率高**。
- **其他远期候选（v1.18.0/v1.18.1）**：SciPhy RL（arxiv 2607.15195，PINN 路径 HJB 离线求解+离散目标持仓适配 T+1+成本内生化，Phase 4+）；HRT 双层 RL（arxiv 2410.14927 MIT，高层选股+低层风险感知执行，turnover/回撤/文本风险惩罚，Sharpe 1.24，与 30 号 sleeve 框架同构，Phase 5+）；VD-MEAC（Front. Artif. Intell. 2026-01，critic 学收益完整分布+熵正则，A 股 Sharpe 2.978，作 HRT"分布 critic"增量不单独登记，Phase 5+）；Finance-Grounded 损失函数（arxiv 2509.04541，turnover 正则化+MDD 损失，仅需改损失函数门槛最低，Phase 2+，25 号升 ML 合成时评估）；Strat-LLM（arxiv 2605.06024，T+1 滚动策略对齐 LLM，牛市 Free/熊市 Strict，35B 严格约束最优，Phase 5+）。
- **稀疏衰减+RMT 去噪（v1.18.1，arxiv 2507.17211 港城大+上财）**：新现象——因子在稀疏组合（ℓ0 约束仅选 m 资产）下衰减**快于**密集组合（稀疏约束放大单资产特异性噪声）；方案=RMT 去噪因子相关矩阵（剔 Marchenko-Pastur 谱噪声特征值）+正则化 QP 权重分配，CSI300/CSI500 实证占优。填补 25 号衰减监控盲区（Alpha-R1/AlphaPROBE/McLean-Pontiff/CUSUM 均假设稠密组合；打板 sleeve 持仓 2-5 只极稀疏，须更短半衰期阈值/更快淘汰节奏）；RMT 去噪与 25 号 §3.1 残差代数 Phase 4 正交（残差代数管合成方法，RMT 管输入矩阵去噪）。Phase 2+（RMT 是矩阵运算门槛低；稀疏衰减阈值校准依赖打板实盘 IC 衰减数据，与 ic_decay.py 联动）。

**保留的待讨论问题**（细节未定，不阻塞核心流程）：
- 集中度硬约束（行业偏离±10%、风格暴露±0.3σ）的阈值依据？——FirmRiskAggregator 裁剪规则待 G13 讨论【v2.0.0 补充：代码侧现状=position_limit_enforcer 单票≤5% NAV + concentration_monitor 单票 8% 告警/行业 30% 上限，G13 对账时以代码真源为起点校准】
- StrategyBook 内 risk parity 的具体实现（inverse-vol？ERC？）？——待 G12 细化【v2.0.0 补充：代码现状=inverse-vol（volatility_data 输入），已 production；远期递进 HRP/TRP→RRP→C-WRP→W-GAN→MFCCA→MINGLE 见上各版本补充，均 Phase 2+/远期，MVP 不变】

---

## 4. 风险模型（原约束四）

> 对应 G16-G18（风控落地）｜ ✅ **已裁定（2026-08-05，30_multi_strategy §2.5；v2.0.0 补口径对账注记）**

**原始内容**：L1实时监控(延迟<1秒)+L2日频因子风险模型(申万31行业+4风格因子)+L3压力测试；VaR/CVaR作为L2量化输入，VaR回测通过率>95%。

**✅ 裁定结论**：30_multi_strategy §2.5 已定 **StrategyBook Drawdown Protocol（4级回撤 + 恢复机制 + 分层风控 + VaR/ES 辅助 + Kill Switch）**，L1/L2/L3 三层架构被替代。映射关系：

| 原始 L1/L2/L3 | 替代方案（30_multi_strategy §2.5） |
|---|---|
| L1 实时监控 | Kill Switch 紧急熔断（单日亏损>6%→平仓+暂停3天；流动性危机→停止开仓）|
| L2 日频因子风险模型 | **4级回撤 Protocol**（Level1 警告 8% / Level2 减仓 15% / Level3 停仓 20% / Level4 清仓 25%）+ VaR/ES 辅助监控 |
| L3 压力测试 | 恢复机制（回撤企稳 50%→解除停仓；Level4 后强制休息 5 交易日）+ 分层风控（单策略 vs 组合）|

- **VaR/ES 角色**：辅助监控指标（VaR_95 > 1.2×入场→减仓 20%；ES_95 > 1.3×入场→再减仓 20%），**不是** L2 量化输入的主模型
- **申万31行业+4风格因子**：FirmRiskAggregator **不做协方差估计**（30_multi_strategy §2.2），因子风险模型未采用
- **行业基准**：LedgerMind 2026-05 / ARKA 2026 / Sina 量化FOF 2026-07 / tradingwyckoff 2026-01 / 赢牛资管 2026-05（详见 30_multi_strategy §2.5 行业来源）

**保留的待讨论问题**（细节未定）：
- 压力测试的场景设计？——4级 Protocol 覆盖回撤场景，但极端事件（黑天鹅）压力测试方案待 G16 细化【v2.0.0 补充：stress_test_engine.py 已内置行业冲击情景；2026-07 量化"双杀"episode 应纳入极端 regime 回测场景（见附录 A.3）】
- VaR/ES 的计算方法（历史模拟法？参数法？蒙特卡洛？）？——待 G17 讨论【v2.0.0 补充：代码现状=var_calculator.py 历史模拟+参数法+var_backtester 回验已 production，G17 对账时以代码真源为准；RWC 压力期校准为 Phase 2 增强】

**⚠️ v2.0.0 口径对账注记**：代码 `drawdown_controller.py`（MOD-POS-008）当前为 5 级 VaR 风险级（GREEN~BLACK）+ Soft Stop 5%/Hard Stop 10% 策略止损 + 黑天鹅 7 模式，与本文档/30 号 §2.5 的 4 级回撤 Protocol（8/15/20/25% 净值域）双轨并存。30 号 §2.5 开头已自注"须在 G13/G14 讨论中明确两视角的映射关系"。**裁定方向（待 G13/G14 闭环）**：4 级回撤 Protocol 是净值域硬红线（mandatory），5 级 VaR 风险级+Soft/Hard 止损是策略级监控层——两者并存不冲突，但触发阈值的映射关系（如 Soft 5% vs Level1 8%）须在 35 号 drawdown_protocol_impl 落码时统一，避免双阈值打架。

**2026 风控理论增强（均非 MVP baseline）**：
- **Landolfi 非高斯回撤查找表（v1.4.0，arxiv 2608.00127，风控优先原则核心）**：扩展 RSB 回撤框架（P&L=带漂移布朗运动），蒙特卡洛生成 4 决策测度查找表——MaxDD/Max Loss/Final Negative Time（水下占比）/Longest Recovery Time。关键发现：① 非高斯下固定 Sharpe+波动率变化偏度/肥尾/波动率聚类，**四测度分化**——单一 Gaussian 表系统性误警（8/15/20/25% 硬阈值若基于 Gaussian 表会在肥尾/偏态 regime 误判）；② fBM 长记忆的回撤"放大"是自相似色散尺度效应 T^(H-1/2)，即 **sqrt(T) 校准失效**非内在危险（长记忆 regime 下 VaR_10d=VaR_1d×√10 系统性高估）。对接：4 级 Protocol 阈值数据驱动校准路径（Level1-4 映射 MaxDD 分布分位数）；恢复机制量化（"企稳 50%"可替换为恢复时间分布中位数）；与 91 号 Lévy 家族形成"密度预测→回撤测度"闭环。~200 行离线仿真，drawdown_controller Phase 2 阈值校准升级。
- **Sharp Tail Bounds（v1.11.0，arxiv 2608.06317 UC Berkeley）**：n 个独立非负、均值≤1 随机变量 P[ΣXi≥t] ≤ 1−(1−1/t)^n（∀t≥2n+1），二元 i.i.d. 下取等且放松问题中仍最优——**分布无关解析上界**（不假设任何参数族，仅依赖均值约束），是历史模拟+参数法之外第三条路径。A 股涨跌停 ±10% 天然近二元分布，对打板策略损失聚合特别紧致；适用 t≥2n+1（3-5 策略 t≥7-11）属 VaR_99.5+/ES_99 极端尾部校验；假设独立性，相关性>0 时界偏松=保守方向。成本=0（闭式公式），36 号 VaR/ES 理论背书工具；与 Landolfi 表形成"单期解析界→多期仿真表"闭环。**Bayesian GP 尾部外推（v1.11.0，arxiv 2510.14637）**：β-mixing 条件下 GP 贝叶斯后验渐近 honest credible regions，尾部分位点估计+置信区间（支持 ARMA/GARCH/Markov copula 依赖），与 Sharp Tail Bounds 互补（精确尾部密度+CI vs 分布无关上界包络），~200 行+MCMC，91 号 Phase 3+ 远期。
- **RWC 压力期 VaR 校准（v1.12.0，arxiv 2602.03903v3 Oxford Schmitt）**：Regime-Weighted Conformal Calibration——model-agnostic 包装器包裹任意条件分位数预测器，用过去预测误差构建安全缓冲，权重=指数时间衰减×regime 相似度；**平滑 regime 漂移下推导覆盖率上下界，不假设加权可交换性**（比经典 conformal 更弱假设）。CRSP+16 组合 Basel 99%/97.5% 实证：TWC（纯时间衰减）是漂移下强默认，regime 加权改善慢适应预测器压力期校准。直击 36 号"VaR 超额发生率集中压力期"已知痛点（VaR 回测通过率>95% 门禁的痛点）；10 号 HMM 后验概率天然提供 regime 相似度权重；适配 52 号 IS→WFA→OOS 门控（WFA 窗口滚动更新 buffer，OOS 用 Basel traffic-light 验证）。~150 行 wrapper，36 号 Phase 2（实盘数据积累后启用）。四项构成"极端尾部上界→精确尾部密度→多期回撤仿真→压力期校准"完整 VaR 风控栈。**分布漂移标度律+核校准（v1.15.0，arxiv 2608.01268 Kaleche）**：检测分布漂移最小样本量标度律 **N\* ≥ log(1/f)/(2ε)**（低于此任何检测器 HMM/CUSUM/MMD/BOCPD 都无法区分真实漂移与采样噪声）+RBF MMD 核带宽应匹配特征尺度；用途=10 号 regime 转换/55/61 号变点检测结果的可信度判据（窗口≥N\*→可信，<N\*→标"低置信变点"），与 RWC 形成"漂移检测→可信度判据→校准启动"闭环；成本≈0 闭式公式，理论背书工具不独立施工。

---

## 5. 成本模型细节（原约束五）

> 对应 G22（下单对接）｜ ✅ **v2.0.0 裁定：简化采纳（砍 Almgren-Chriss MVP、策略分档滑点、最低佣金显式建模）**

**✅ v2.0.0 裁定结论**：

- **本质**：个人小资金成本结构是"固定费用主导、冲击可忽略"——order/ADV<0.1% 时平方根冲击 <5bps，相对价差可忽略。第一性原理：成本模型的精度只需匹配"决策所需精度"——判断策略赚不赚钱需要准确的固定成本，不需要精确的冲击曲线。
- **裁定**：① **Almgren-Chriss 不采纳进 MVP**（留 cost_model_registry impact_model 接口字段，远期资金量级到单票百万+再启用）——v0.3.0 平方根冲击律结论维持（个人资金冲击可忽略）；② **滑点按策略分档**：高流动票 0.05-0.1%，打板/事件票 0.15-0.3% 并乘成交概率折减（打板买入有封板买不进概率，预期滑点须按条件成交修正）；③ **最低 5 元佣金必须显式建模**——单笔 <5 万元时实际费率被抬升至万5以上，是小资金+做T高频的最大隐性成本，回测漏建会系统性高估收益；④ **印花税率更正**：原稿"千1卖出"已过时——2023-08-28 减半后现行为**卖出单边 0.05%（万5）**，与 cost_model_registry CST-ASTOCK-001 登记一致（佣金万3/印花税万5，费率按账户配置不硬编码，宪章已定）；⑤ **做T额外成本**：滑点×2 合理保留（一买一卖两次滑点）；单次往返硬成本≈0.10-0.15%（双边佣金+卖出印花税+双倍滑点），**预期价差≥0.3% 才有正期望**——此阈值作为做T开仓的硬性前置条件（与 §21 regime 过滤规则联动）；失败风险溢价保留，用隔夜底仓暴露×隔夜 VaR 估算（LVaR 简化式见 §8）。
- **施工方案**：① cost_model_registry 增补**做T成本条目**（CST-T0-001：双边佣金+印花税+滑点×2+失败风险溢价，~30 行 YAML，Phase 1）；② 回测成本计算器确认最低佣金 5 元建模（检查项，若未建则 ~20 行修补，Phase 1）；③ 策略分档滑点参数写入各策略配置（Phase 1）。集成点：回测引擎成本注入点 + 做T策略开仓前置检查。
- **过度工程审查**：全部复用已有注册表与成本注入点，无新架构；Almgren-Chriss 显式降级远期。✅ 通过。

**原始内容**：佣金万2.5双边+印花税千1卖出【v2.0.0 更正：现行万5卖出单边】+滑点(基础0.05%+动态)+市场冲击(Almgren-Chriss)+做T额外成本(滑点×2+失败风险溢价)；回测必须包含全部四类成本。**原待讨论问题（已闭环）**：Almgren-Chriss 是否采用/参数校准→✅ 不进 MVP（接口字段保留）；滑点模型实现→✅ 策略分档；做T滑点×2倍率→✅ 合理保留；费率按账户动态配置→✅ 采纳（不硬编码，宪章已定）。

**2026 算法论据（v0.3.0）**：① **平方根冲击律**：`市场冲击 = α × σ × √(order_size / ADV)`（σ=日波动率、ADV=日均成交额），冲击与订单规模呈凹函数（Bouchaud 等经验共识）；个人 A 股 order/ADV<0.1% 时冲击 <1bp 可忽略，仅单标的持仓 >1% ADV 需启用动态冲击模型——slippage_analyzer.py 已实现（impact=coeff×√participation×vol_bps）。② Almgren-Chriss 分解=永久冲击（随成交量线性累积）+临时冲击（当笔后衰减），2026 进阶瞬态冲击模型（指数衰减核+平方根缩放，arxiv 2601.22113）。③ 做T失败风险溢价=隔夜底仓暴露×隔夜 VaR，可用 §8 LVaR 框架量化。

---

## 6. 回测门禁（原约束七）

> 对应 G23（回测框架对接）｜ ✅ **已裁定：项目用 BM-BT-01~07 体系，V1-V6 已映射**

**原始内容**：

| 验证层级 | 验证对象 | 验证方法 | 优先级 |
|---------|---------|---------|:-----:|
| V1 因子验证 | 单因子IC/ICIR/分组单调性 | Purged K-Fold+Embargo | P0 |
| V2 信号验证 | 单信号方向准确率/Brier Score | Walk-Forward | P0 |
| V3 策略验证 | 单策略PnL/Sharpe/回撤 | Walk-Forward+Permutation Test | P0 |
| V4 管线验证 | 全链路端到端 | Walk-Forward+模拟盘 | P0 |
| V5 日内信号验证 | 分时指标/做T买卖点 | Walk-Forward逐笔+滑点建模 | P0 |
| V6 风控验证 | 风控触发/熔断/保护性减仓 | 极端场景重放 | P1 |

**✅ 裁定结论**：项目实际用 **BM-BT-01~07** 编号体系（battle_map_03_backtest_validation + 52_backtest_framework_docking + 11_regime_backtest §2.1）。V1-V6 → BM-BT 映射：

| V1-V6（原） | BM-BT（现状） | 验证方法 | 状态 |
|---|---|---|---|
| V1 因子验证 | BM-BT-01~02 | Purged K-Fold + Embargo + 向量化/事件驱动引擎 | ✅ 已施工（BT-01~04 stable） |
| V2 信号验证 | BM-BT-03 | Walk-Forward + 指标计算（Sharpe/Sortino/MaxDD/IC/IR） | ✅ 已施工（BT-05~09 stable） |
| V3 策略验证 | BM-BT-04~05 | Walk-Forward + Permutation Test + **Deflated Sharpe (BM-BT-05-G)** + 过拟合检测三维度 | 🟧 部分（BM-BT-05-G 待实现）【v2.0.0 口径注记：`simulation/deflated_sharpe_calculator.py` 代码已存在，battle_map_03 标 BM-BT-05-G 环节为 design——代码先于登记，G23 对账时确认是否已完成接入 metrics 管线；Purged K-Fold/Permutation Test/PBO 未施工】 |
| V4 管线验证 | BM-BT-06~07 | IS→WFA→OOS 上线门控 + 模拟盘 | 🟧 decision_gate.py（MOD-BT-001）策略路径已 production；regime 验证 Phase 5 门控未完成（11 号 §0.5.1）【v2.0.0 口径澄清】 |
| V5 日内信号验证 | BM-BT（Tick 回放） | Walk-Forward 逐笔 + 滑点建模（秒级/30秒/5秒） | ✅ 已施工（Tick 回放引擎） |
| V6 风控验证 | BM-BT（风控重放） | 极端场景重放 | 📝 待实现 |

**2026 行业实证**（Purged K-Fold / Walk-Forward / DSR 为 2026 标准实践）：
- PurgedKFold+embargo 是防时间泄漏标准（honest-backtest 2026-06，"plain K-fold leaks in time"）；**DSR+PSR** 是多重检验校正标准——测 80 个变体后 p=0.05"显著"结果 98.3% 是噪声（backtest-guard 2026-07）；walk-forward 将 IS Sharpe 0.71 削至 OOS 0.48（-32%，mathandmarkets 2026-05）；purged CV+embargo+regime-aware fold 是生产级标配，CPCV 是进阶替代（walk-forward-validation skill 2026-07）
- **Darmanin 三门控"实际可行性"框架（v1.10.1，arxiv 2607.20093 Hecatus Research）**：比 DSR 单维更全面——(1) 统计优势门控（BY 分层 FDR+平稳 bootstrap CI+暴露匹配基准+单边声明排除+等价性检验）；(2) 经济可行性门控（成本后净 alpha>0——A 股印花税 0.05%+佣金万2.5+滑点 0.1% 三层扣除）；(3) 存活率门控（杠杆下破产概率<阈值）。关键负结果：6 候选策略 4 个 REFUTED（振荡器/成交量/日历/K线形态），趋势/动量 INCONCLUSIVE——印证"简单信号失效"。记 Phase 2（BM-BT-05-G 实施时同步引入经济可行性+存活率两维度，避免"统计显著但实盘亏钱"；FINRA/ESMA 杠杆场景可类比 A 股两融）。

**保留的待讨论问题**：
- "策略上线必须通过 V3+V4+模拟盘"标准是否采用？——对应 BM-BT-07 IS→WFA→OOS 门控，待 52_backtest_framework_docking 细化【v2.0.0 注：52 号实际仍为 v0.1.0 骨架，00 号索引标"active v1.7.4"与 52 号 frontmatter 不符，属索引漂移；决策逻辑已施工于 decision_gate.py】
- 幸存者偏差防护（PIT 股票池）的实现状态？——BM-RES-01 特征存储(PIT) + AS OF JOIN，**BT-10 已 production**（battle_map_03 确认 pit_manager stable/production，"PIT管理器未就绪→回测不可信"硬阻断已生效）【v2.0.0 更正：原稿"BT-10 已规划"过时】

---

## 7. T+1次日预测（原约束九）

> 对应 G02（regime spec，已定稿）｜ ⚠️ **纠正（v0.2.0）：原稿"8态已被12态替代"不准确** ｜ ❌ **v2.0.0 裁定：暂缓建设（BM-SEL-04 降级远期）**

**❌ v2.0.0 裁定结论（暂缓建设）**：

- **本质**：次日方向是低信噪比问题，边际信息被隔夜噪声淹没；T+1 下预测对也未必能兑现（当日买不了）。决策论上仓位调整需要的是期望收益/风险比，不是方向点预测。
- **裁定理由**：① **52-53% 天花板 2026 年无突破证据**——纯价量个股方向准确率天花板（firsh.me 9 版迭代 p=0.007）与 2026 各项独立复现（SPY 57-58% 指数、含乐观偏差）一致；加情绪的混合模型文献报 60-68% 但普遍缺 walk-forward 与成本核算，可信度低；龙虎榜净买入单因子次日胜率≈50%（2026-07 实证）；② **8 类细分后单类准确率更低**——52-53% 的方向边缘摊薄到 8 态后单态可用性极低，且"高开低走"等态的可交易性依赖盘中执行，日线模型给不了；③ **regime 7维概率 + VaR/ES 区间已覆盖其作用**（"明天大概率怎么走"的决策需求=风险节流+区间保证，非方向点预测）；④ 方向≠盈利（非对称亏损吞噬统计优势）。
- **裁定**：**BM-SEL-04 暂缓建设，从 design 降级为远期候选**。8态→直接决策映射确认废弃（v0.2.0 已裁定）；8态→特征输入角色一并暂缓（价量信息已被 regime+因子库覆盖，增量有限）。**唯一例外**：打板策略内部的"次日高开概率"是其自身参数，用条件概率表（历史统计，非独立模型）估计即可，不属于 BM-SEL-04。**远期重启条件**（全部满足才可重启评估）：① 系统稳定盈利（生存线达标）；② 目标收窄为"开盘 30 分钟走势"（非全日 8 态）；③ 概率输出仅接入仓位微调（非直接决策）。
- **⚠️ v2.0.0 重要更正——A2 已 PASS**：11 号 v1.5.2 §0.5.4 确认：经 BIC 扫描降为 4 态后，A2 OOS/IS 一致率从 0.340 升至 **1.042（PASS，门槛 0.7）**，过拟合消除。因此 **Wasserstein HMM 从"A2 修复必需"降级为 Phase 3+ 可选增强**（标签漂移的长期鲁棒性改进，非修复痛点），P-1/P-3 待定项的紧迫性同步下降（见「待定问题」节更新）。
- **过度工程审查**：不建 8 态模型=做减法，✅ 通过。

**原始内容**：次日走势8态叠加模型(高开高走/高开低走/低开高走/低开低走/平开高走/平开低走/震荡收平/剧烈震荡)；8态→今日决策映射(P1+P5>60%→买入加分20%，P4+P6>60%→降权30%推迟，P8>30%→仓位减半)；分阶段实现Phase1=3态→Phase2=5态→Phase3=8态。

**⚠️ 纠正要点（v0.2.0）**：① **8态概念未被替代**——8态 T+1 次日走势预测（BM-SEL-04）是**独立的下游消费者**（回答"明天大概率怎么走"），与 regime 检测器（回答"现在是什么市场"）是不同概念（10_regime_detector_spec §2.1："下游消费者，非检测器本身"，状态 design 未建）；② **8态→直接决策映射确实过时**——与 Model A 冲突（策略自主 alpha 决策，regime 仅 Shrinkage 风险节流），8态若消费应作策略层输入特征或 Shrinkage 置信度参考，非直接"买入加分/降权/仓位减半"；③ **regime 实现态数更正**——实际实现为 **4 态 HMM + 3 overlay = 7 维概率**（11_regime_backtest §0.5.2：r1 低波震荡 27.6%/r2 中波震荡 37.4%/r3 牛市趋势 14.9%/r4 熊市阴跌 20.2% + CRISIS/RECOVERY/BREAKOUT），非 spec 12 态。

**原待讨论问题（v2.0.0 已闭环）**：8态是否仍需建设→✅ 暂缓（regime 7维+策略 alpha 已足够）；8态概率如何消费→远期重启时仅接仓位微调；分阶段计划是否对齐 regime→随暂缓一并冻结。

**2026 补充论据**：
- **预测天花板实证（v0.6.0，firsh.me 2026-07）**：A 股日线纯价量（19 维跨股可比特征）方向准确率天花板约 **52-53%**（71 只 A 股 2017-2026，9 版架构迭代 p=0.007）——突破口在信息源非架构（注意力相对均值池化仅 +2.9-3.5pp；跨股训练>单股训练）；方向准确率≠盈利（盈亏比<1 时 53% 胜率不足）。若建 8态必须加信息源（情绪/资金/事件/龙虎榜 Level2 另类数据），且应复用 regime 多源特征而非另起炉灶。
- **Wasserstein HMM（v0.9.0，arxiv 2603.04441 Columbia）**：严格因果滚动 Gaussian HMM+预测性 model-order selection（one-step-ahead log-likelihood 动态选 regime 数）+Wasserstein template tracking（2-Wasserstein 距离将当前分量映射到持久化 regime 模板，解决 HMM 固有 label-switching）。实证 Sharpe **2.18** vs SPX 1.18/MaxDD **-5.43%**；vs 非参数 KNN 换手率显著更低、权重演化更平滑。原定位 12 号 Phase 2 A2 修复候选，**A2 已 PASS 后降级 Phase 3+ 可选增强**；并列候选谱系：BR-iHMM（v1.1.0，doubly outlier-robust online infinite HMM，预测误差降最多 67%，解决离群点毒化+无限状态自适应）与 Huber Robust/Student-t/GH/Feature Saliency/AH-HMM（v1.2.0，egargale/hmm_test PRD #20）。**VRMD（v1.6.0，arxiv 2608.05373，已评估不整合）**：Gaussian HMM regime+option-Delta velocity 盘中操纵检测，关键反面结果——regime 条件化用 recall 换 precision，**precision 上限约 25%**，细分越多 precision 越低，反面印证项目 4 态 HMM 不过度细分决策；操纵检测场景不适用 A 股个人系统（无期权数据接入）。

---

## 8. 流动性风险（原约束十）

> 对应 G18（流动性危机处理）｜ ✅ **v2.0.0 裁定：简化采纳（压力退出时间禁开仓 + LVaR 简化式 + A股特有维度）**

**✅ v2.0.0 裁定结论**：

- **本质**：个人小资金的流动性风险不是冲击成本（可忽略），而是"极端情形卖不出"（跌停粘连/停牌/ST 退市）。指标服务于仓位上限与开仓许可，不服务于交易信号。
- **裁定**：① **"超1天→降仓位"阈值修订**——个人单票 <0.1% ADV，正常市况退出 <1 小时，原阈值无意义。改为**压力情景退出时间**：`退出天数 = 持仓 / (ADV × 0.3 压力折扣 × 10% 参与率)`，>1 天→**禁新开仓**（精准拦截微盘股与跌停粘连票，与附录 A.2 微盘流动性枯竭联动）；② **连续评分 + 同源 3 档开关并存**：连续 ILLIQ 评分供 Kelly/risk parity 调权，同源派生 3 档离散开关（正常/降档/禁开仓）供 4 级 Protocol 触发——两套输出同一数据源，不建两套指标；③ **LVaR 简化式**：`LVaR = VaR × √退出天数 + 半价差`（完整 Kyle Lambda 估计器不建，日频 Amihud 已足够）；④ **必须加入 A 股特有维度**：跌停概率、停牌/ST/退市警示——比 ILLIQ 更致命（微盘 Q1 归母净利 -79.25% 退市风险，附录 A.2）；⑤ 做T流动性前置检查：量比>1 且预期振幅>2×单边成本（与 §21 联动）；⑥ 流动性降级模式保留（ILLIQ >历史 90 分位→VaR 升级 LVaR，喂入 30 号 §2.5.4 VaR_95 减仓触发）。
- **施工方案**（liquidity_monitor.py Phase 2 扩展，~100 行）：① 压力退出时间计算+禁开仓开关（复用已有 ADV/ILLIQ 输入）；② LVaR 简化式接入 var_calculator；③ 跌停/停牌/ST 维度从 universe_registry 过滤规则取数（已施工）。集成点：default_risk_manager_orchestrator（已接入 liquidity_monitor）+ 4 级 Protocol 触发链。验证：2026-07 微盘枯竭 episode 回放（附录 A.2）。
- **过度工程审查**：复用已 production 的 liquidity_monitor 扩展，不新建独立流动性系统；Kyle Lambda 完整版/实时评分流显式不建。✅ 通过。

**原始内容**：实时流动性评分+流动性调整VaR(LVaR)+退出时间估算(超1天→降仓位)+做T流动性前置检查+流动性降级模式(VaR退化为标准VaR+0.5%溢价)。**原待讨论问题（已闭环）**：评分指标构成/LVaR 切换条件/退出时间模型/超1天阈值合理性/做T前置检查规则——全部见上裁定①-⑥。

**2026 算法论据（v0.3.0）**：① **Amihud 非流动性指标** `ILLIQ = mean(|r_t| / V_t) × 10^6`（仅需日频数据，Kyle's Lambda 的高频代理，liquidity_monitor.py 已 production）；② LVaR 完整式 `LVaR = VaR + ILLIQ × Volume × Kyle_lambda`（GinkGO 2026-05）——裁定采用简化式；③ **Kyle's Lambda** `ΔP = λ × OrderFlow`（OLS 回归，高频精确但需 Tick 数据，日频用 Amihud 替代）；④ 退出时间通用式 `Position_Size / (ADV × max_participation_rate)`，参与率通常 5-10%（超 10% 显著冲击价格）——裁定采用压力折扣变体。

---

## 9. 数据分层使用（原约束十一）

> 对应 G01（数据与特征层规范）｜ 🔧 **更正引用（v0.2.0）** ｜ ✅ **v2.0.0 裁定：修订采纳（半衰期参数化 + 断裂期降权保留 + Layer4 drift 触发）**

**✅ v2.0.0 裁定结论**：

- **本质**：非平稳市场下"近期相关性"与"regime 覆盖度"的权衡；窗口与衰减是同一枚硬币（指数衰减=软窗口）。
- **裁定**：① **Layer0-4 五层分层采纳**，起始年份（1990/2005/2015/2020/近1年）依据成立（1990=A股开市全历史压力测试、2005=股改后现代市场结构、2015=两融+量化兴起、2020=注册制+机构化加速）；② **权重参数化改为半衰期**：`w(t) = 0.5^(t/HL)`，HL≈2-3 年（与原"近1年=1.0/5年=0.3/10年=0.1"等价但更直观、可调单参数）；③ **结构断裂期（2015 股灾/2018 熊市/2024 微盘崩盘）不剔除**——这是 regime 检测与压力测试最稀缺的样本，训练时降权 50% 保留，并单独作为压力测试集（剔除=丢掉最宝贵的极端 regime 训练信号）；④ **Layer4 加 drift 触发**：特征分布漂移或 IC 衰减超阈值即触发重训，不只按日历滚动（与 decay_monitor 联动）；⑤ 用途分配：Layer2 用途已更正为 regime 检测（v0.2.0 ✅）。
- **施工方案**：半衰期样本权重实现在训练数据加载层（15 号/G01 Phase 2，~40 行：`sample_weight = 0.5 ** (days_ago / (HL*252))`，HL 默认 2.5 年），断裂期清单配置化。注意与已有 10 层数据留存分层（data_retention_contract，数据治理语义）正交——留存管"数据存多久"，样本权重管"训练用多重"，两者不冲突。
- **过度工程审查**：单参数半衰期替代 5 层硬权重=做减法；不建独立样本权重服务。✅ 通过。

**原始内容**：Layer0(1990-至今)仅压力测试；Layer1(2005-至今)体制检测+长周期因子验证；Layer2(2015-至今)8态预测+因子IC验证；Layer3(2020-至今)因子模型训练+Walk-Forward；Layer4(近1年252天)在线训练+实时生成。指数衰减权重：近1年=1.0，5年前=0.3，10年前=0.1。

**🔧 更正（v0.2.0）**：Layer2 引用的"8态预测"应更正为 **regime 检测**（spec 12 态 / 实际实现 4 态 HMM + 3 overlay = 7 维概率，见 §7）。8态 T+1 次日预测（BM-SEL-04）是独立的下游消费者，非数据分层用途的引用对象。**原待讨论问题（已闭环）**：五层分层是否采用/起始年份依据/衰减权重合理性/用途分配调整——全部见上裁定①-⑤。

---

## 10. 密度预测（原约束十二）

> 已拆为独立讨论稿：[91_density_prediction.md](91_density_prediction.md) ｜ ⏸️ **v2.0.0 裁定：远期维持，MVP 不建**

**⏸️ v2.0.0 裁定注记**：① **维持远期**——MVP 用历史模拟 VaR + feedback_loop 已有简易 conformal 骨架，密度预测完整栈（RWC→LSTM+skewed-t MDN→扩散→QNN）全部 Phase 1+ 以后；② **⚠️ 文档漂移警示**：91 号实际仅 **v0.1.2 骨架（45 行）**，本文档各版本引用的"91 号 v0.4.0 四阶段路线 / v0.5.0 RWC / v0.6.0 Info-Entropic DL+GP / v1.2.0 Lévy / v1.3.0 Cross-Sectional / v1.4.0 Exformer"等内容**均未落盘到 91 号**——下文所有"见 91 号 vX.Y.Z"引用应视为**规划态提案**（真源在本文档），91 号回填前不代表已定稿方案；③ Phase 0 基线候选维持 slow unweighted rolling conformal（Conformal Kelly v0.8.0 实证"慢而稳"最优）；④ 8 态概率"Phase 4 后从 PDF 积分派生"随 §7 暂缓建设一并冻结。

**FCVE 补充（v1.6.0，Mathematics 14(15):2847 2026-08-06）**：Finite-Sample Conformal Joint VaR-ES——conformal risk control 同时控制 VaR breach frequency（违反频率）与 breach magnitude（违反幅度），non-exchangeable swap-distance bound+regime-drift bound+heavy-tail rate 三重有限样本保证；是 RWC/TWC 的 joint VaR-ES 扩展（RWC 管单一分位数 regime 加权校准，FCVE 管 VaR+ES 联合校准），对 A 股 regime 频繁切换+涨跌停重尾场景适用。36 号需要 joint breach 控制时启用，Phase 2 远期候选。

---

## 11. 仓位管理（原约束十三）

> 对应 G12（仓位算法）/ G13（FirmRiskAggregator）｜ ✅ **已裁定（2026-08-05，30_multi_strategy；v2.0.0 锚点更新至 v2.5.0 + 遗留问题闭环）**

**原始内容**：C-047仓位裁决不可绕过(唯一例外：C-004风控veto)；半Kelly硬上限；漂移再平衡阈值(总仓位±2%/单标的±3%)；再平衡成本-收益规则(收益改善>2×成本才执行)；资金曲线驱动仓位缩放(回撤>5%→总仓位缩减10%，>10%→缩减20%)。

**✅ 裁定结论**：30_multi_strategy §2.1/§7.2 已定模块编号与定位：
- **C-047 → MOD-POS-021（FirmRiskAggregator）+ MOD-POS-001（position_sizing_engine）**：firm 层求和 + 硬上限裁剪（021）+ Kelly 精裁决（001）——C-047 旧"唯一裁决中心"职能由两模块分层承接（§7.2 depgraph 已登记）【v2.0.0 注记：AI_review_instructions.md 写"C-047→MOD-POS-001"系不完整映射；module_translation_registry / battle_map_positioning / sell_conflict_arbitrator blueprint 仍以 C-047 描述现行决策链，属旧架构描述未清理，需 G12/G13 对账时同步修订】
- **半 Kelly 定位**：**firm 层精裁决工具**（非全局硬上限）——StrategyBook 用 risk parity/等权（不用 Kelly），Kelly 仅在 firm 层组合级使用【v2.0.0 锚点更新：30 号 v2.5.0 已升级为 Fractional Kelly 25-50%（Phase 1）→ Bayesian Kelly（Phase 2）→ Conformal Kelly（Phase 3 远期）三档演进，fraction 待 31 号 G12 标定】
- **资金曲线驱动仓位缩放 → 4级回撤 Protocol**（§2.5）：回撤 8%/15%/20%/25% 四级触发，替代原"回撤>5%→-10%，>10%→-20%"线性规则
- **模块编号体系**（§7.2）：MOD-POS-020（StrategyBook）/ MOD-POS-021（FirmRiskAggregator）/ MOD-PA-007（RegimeMetaAllocator）/ MOD-POS-022（BudgetChangeHandler）

**原待讨论问题（v2.0.0 已闭环）**：
- 漂移再平衡阈值（±2%/±3%）的依据？——✅ **已闭环**：30 号 §2.4 实际采用 ε_pos=5% 收敛容差（Tier2→Tier3）+ no-trade 半带公式 `b*=[3cσ²/(2λ)]^(1/3)`（Phase 2 候选）替代 C-047 旧阈值；代码侧 position_drift_monitor（MOD-POS-003）已施工漂移检测，阈值在配置。±2%/±3% 旧值**标 deprecated**（与 Model A 分层架构不兼容——策略层粗仓位天然有波动，±2% 会过度交易）
- 再平衡成本-收益规则（>2×成本）的阈值是否合理？——✅ **已闭环**：no-trade 半带公式即成本-收益规则的理论化（半带宽度由成本 c、波动 σ、风险厌恶 λ 内生决定），Phase 1 用 ε_pos=5% 固定容差已隐含"小漂移不再平衡"；">2×成本"线性规则**标 deprecated**

**2026 Kelly 分数论据**：
- **Kelly 分数实证（v0.7.0）**：Kelly 最优增长率 `g(f*)=SR²/2`（Sharpe 翻倍→增长率 4 倍，提升 Sharpe 比提升 Kelly 分数更有效）；Half-Kelly 捕获 75% 增长@50% 波动，**1/4 Kelly 捕获 95% 增长+显著降回撤**（Lisa Chang 案例：full Kelly 16.8%→6 连败→-62% 回撤；切 1/4 Kelly→6 个月 +56% 恢复，MaxDD -12%）；drawdown 恢复数学（-20% 需 +25%、-50% 需 +100%）——Level4（25%）需 +33% 恢复，Kelly 分数选择直接影响是否触发 Level 4。**动态分数 Kelly 方向**：低波 regime（r1/r2）half-Kelly、高波/CRISIS overlay quarter-Kelly；regime→分数映射表待 G12 细化。
- **Conformal Kelly（v0.8.0，arxiv 2608.01494 ACS Athens）**：75% conformal 区间宽度缩放仓位（窄→加仓/宽→缩仓），6 年开发窗口含成本+1 日延迟+杠杆上限：**28.5% 年化净对数增长/Sharpe 1.34/MaxDD 27.7%**（vs B&H 15.9%）。**反直觉关键发现：每加快自适应/regime 加权 tweak 反损 0.7-5.3pp 年化——最简方法（slow, unweighted, per-asset rolling conformal）最优**（区间用于仓位缩放时宽度稳定性>局部锐度）；drawdown dial 风控（连续下行失误远超历史率→降杠杆）MaxDD 27.7%→20.3%（rank-based p≈0.024）；lockbox OOS 校准保持（0.745 vs 0.750）但增长未保持——**价值在校准+风控而非增长**。对接：91 号 Phase 0 先实现 slow unweighted baseline 再评估 RWC 增量；可作动态分数 Kelly 的数据驱动实现（替代手工 regime→分数映射表）；drawdown dial 是 4 级 Protocol 的事前软预警补充。**轻量级 Kelly 校准（v0.8.0，Phase 0.5 介于 RWC 与完整密度之间）**：Bayesian Kelly `f* = (p̄ - (1-p̄)/b) · n_eff/(n_eff+κ)`（Beta 共轭先验，样本少自动收缩到 0、样本多逼近经典 Kelly，~20 行）；RMSE 校准 Kelly `f* = 2p-1; α = max(0, 1 - c·RMSE/|f*|); f = α·f*`（c=1.0-2.0 保守系数，低置信信号平滑近零分配，比硬阈值切换更平滑）。

---

## 讨论优先级建议（v2.0.0 更新：全量裁定完成，此表转为施工优先级）

> **v2.0.0 更新**：21 项全部裁定完成（✅ 维持 4 项+新裁定 12 项+合并 1 项+暂缓/远期 2 项+待用户裁定 P-1~P-5）。原"讨论优先级"转为**施工优先级**——指导 Phase 1/2 施工排期。

| 施工优先级 | 主题 | v2.0.0 裁定 | 施工动作 |
|:------:|------|:----:|------|
| — | #3 组合构建 / #4 风险模型 / #6 回测门禁 / #11 仓位管理 | ✅ 已裁定维持 | 无新增施工；G12/G13/G14 对账项跟进（阈值口径/C-047 旧描述清理/52号索引漂移） |
| P1 | #5 成本模型 | ✅ 简化采纳 | cost_model_registry 增补做T成本条目 CST-T0-001 + 最低佣金5元建模确认（Phase 1） |
| P1 | #13 基准设计 | ✅ sleeve 级多基准 | benchmark_registry 增补中证1000/2000/万得全A 条目（Phase 1，~30行 YAML） |
| P1 | #19 大额下单 | ✅ 默认限价单 | ex_sor 选择器默认策略配置项调整 + 打板专用执行路径确认（Phase 1，40号已施工范围内） |
| P2 | #2 因子IC | ✅ 双轨采纳 | BHY FDR 校正 ~80行 + 滚动分位嵌入 decay_monitor（Phase 2） |
| P2 | #8 流动性 | ✅ 简化采纳 | liquidity_monitor 扩展：压力退出时间+LVaR简化式+跌停/ST维度 ~100行（Phase 2） |
| P2 | #9 数据分层 | ✅ 修订采纳 | 半衰期样本权重 ~40行（Phase 2，15号/G01） |
| P2 | #15 资产分级 | ✅ 两维精简 | universe_registry 增补准入×数据覆盖维度字段+流通市值分层计算字段（Phase 2） |
| P2 | #16 成功指标 | ✅ 修订采纳 | 生存线监控落码（55号 KPI 监控施工）；健康/卓越线实盘 6-12 月后校准（Phase 2+） |
| P2 | #17 行为边界 | ✅ choke point | 单一订单出口架构验证（40号范围内）+ YAML 规则归并（Phase 2） |
| P2 | #18 资产覆盖 | ✅ 轻量 IM | Instrument Master 轻量表（复用现有 schema，盘前 xtdata 同步，Phase 2） |
| P2 | #20 工程细节 | ✅ 逐项裁定 | 策略指纹库+DTW（echo-guard Phase 2）；B-008/B-012/B-013 归治理配置闭环 |
| P2 | #21 做T | ✅ 受约束 overlay | 四规则配置化（sizing/regime过滤/失败处置/冲突管理，Phase 2，做T策略配置项） |
| P2 | #1 策略类型 | ✅ 修订采纳 | 零新增施工——新增策略强制族归属声明（治理流程，即时生效） |
| P2 | #14 PIT | ✅ 确认已施工 | deliberate future-date 泄漏测试自动化（Phase 2 增强，BT-10 体系内） |
| ⏸️ | #7 T+1 8态 / #10 密度预测 | ❌ 暂缓/远期 | 不施工（重启条件见 §7；91号待回填） |
| 📝 | P-1~P-5 选项收敛 | 待用户裁定 | 方向见「待定问题」节，用户确认后按方向执行 |

---

## 12. 成功指标中的交易参数（原§9健康线+灰色地带）

> 源自宪章§9系统级成功指标。宪章保留成功指标的结构（生存/健康/卓越/失败四档），但具体交易参数移入此处待讨论校准。｜ ✅ **v2.0.0 裁定：并入 #16，线性收紧规则 deprecated**

**✅ v2.0.0 裁定结论**：

- **IC 阈值作为成功指标**：随 #2 双轨化（静态地板+BHY FDR+ICIR≥0.5），不再单列。
- **"每+1%→仓位-2%"线性收紧规则：标 deprecated**——已被 4 级回撤 Protocol（8/15/20/25% 离散档位+恢复机制）替代。离散档位优于线性规则：① 触发点明确可审计（线性规则在连续回撤下每日微调仓位，产生不必要的换手成本）；② 恢复机制防抖动（线性规则无 hysteresis，回撤在阈值附近震荡会反复调仓）。灰色地带 15-25% 区间即 Level2~Level4 覆盖域，无需另设规则。
- **"20%触发紧急告警"与 4 级 Protocol Level 3（20% 停仓）一致** ✅——告警是 Level 3 动作的配套通知，无冲突。
- **审批频次阈值（3次通知/4次审视）**：保留为 C-031 信任模型的默认配置，上线后按实盘审批数据校准（Phase 2）。第一性原理：审批频次阈值的本质是"AI 置信度退化预警"，合理阈值只能从实盘审批分布反推，拍脑袋值作默认、实盘校准是标准做法。

**原始内容**：
- 健康线IC阈值：因子池分类平均IC | 量价>0.03/基本面>0.02/另类>0.025
- 灰色地带：回撤15%-25%→C-004自动收紧(回撤每+1%仓位上限-2%)，20%触发紧急告警
- 灰色地带：审批2~5次/天→3次通知提醒，4次触发C-031信任模型审视

**原待讨论问题（已闭环）**：IC 阈值与 #2 合并→✅ 随双轨化不单列；线性收紧与 #11/4级Protocol 统一→✅ 线性规则 deprecated；20%告警与 Level 3 一致性→✅ 一致；审批频次阈值依据→✅ 默认配置+实盘校准（Phase 2）。

---

## 13. 基准设计选择（原§3约束二）

> 基准选择会随市场发展和投资策略变化，不是硬边界。｜ ✅ **v2.0.0 裁定：sleeve 级多基准，废弃 60/40 拼合基准**

**✅ v2.0.0 裁定结论**：

- **本质**：基准的唯一功能是"刻画策略可被动获得的机会集（opportunity set）"——超额=主动部分。基准与策略持仓风格错配，测出来的 alpha 就是噪音。打板策略对标沪深300，等于用大盘蓝筹尺量小票情绪策略，超额虚高且无信息量。
- **裁定**：① **废弃 60%沪深300+40%中证500 拼合基准**（两边都不贴合，属伪精确）；② **采纳 sleeve 级多基准**：打板/事件驱动→中证2000（小盘机会集，2026 私募中证2000指增近1年平均超额 17.41% 是主战场）；多因子→中证1000（若偏小盘）或万得全A（全市场选股）；③ **沪深300 保留为大盘宽基锚**（绝对超额参照+与公募对比的统一口径）；中证A500 并列观察（2026 公募基准改革后 A500 是机构新锚，A500 ETF 成交额已超沪深300 ETF，但个人系统 sleeve 级基准优先）；④ **组合层仅报绝对收益+最大回撤**，不强行设相对基准（多 sleeve 拼合后相对基准无意义）；⑤ Smart Beta 基准暂缓（个人系统过度——v0.4.0 Barra 归因+Smart Beta 双层方案降级为远期，style-adjusted alpha 概念保留为分析视角）；⑥ 资产覆盖扩展（港股/期货）后按 sleeve 各自增设基准，不建统一全球基准。
- **施工方案**：benchmark_registry.yaml 增补中证1000/中证2000/万得全A 条目（~30 行 YAML，Phase 1）；策略注册表条目关联 sleeve 基准（strategy_registry 已有 BMK-INDEX-001 引用机制）。验证：回测报告同时输出 sleeve 基准超额+组合绝对收益。
- **过度工程审查**：仅注册表条目增补，无新架构；Smart Beta/Barra 归因降级远期。✅ 通过。

**原始内容**：相对基准=沪深300；超额收益=组合收益-沪深300收益；组合基准=60%沪深300+40%中证500(仅绩效评估)。**原待讨论问题（已闭环）**：沪深300 是否最合适/中证A500 等替代→✅ sleeve 级多基准+宽基锚保留；60/40 配比依据→✅ 废弃；资产扩展后基准调整→✅ 按 sleeve 各自增设。

**2026 算法论据（v0.4.0）**：归因驱动的基准选择——① **Barra 式归因**（KTD-Fin arxiv 2605.28359）：组合收益分解 market beta+style exposure+stock-selection alpha；关键发现 LLM 交易 agent 的"alpha"在泄漏控制后**大部分是被动市场/风格暴露**——若项目超额主要是小盘/低波风格暴露，应对标风格基准而非沪深300；② **Smart Beta 基准**（中证指数 2026-07：红利多因子 932315/价值多因子 931052/质量多因子 930939/沪深300质量成长低波 931375）——策略有明确风格倾斜时用对应 Smart Beta 指数作基准。两层框架（宽基管绝对超额+风格层管 style-adjusted alpha，仅 style-adjusted alpha>0 才是真选股能力）已降级远期，概念保留。

---

## 14. PIT一致性实现方案（原§3约束三）

> PIT原则是量化回测铁律（防止前视偏差），原则本身不变，但实现方案会演进。｜ ✅ **v2.0.0 裁定：确认已施工主干，补 2 项 Phase 2 增强**

**✅ v2.0.0 裁定结论**（对照已施工设施逐项闭环原待讨论问题）：

- **PIT 数据架构实现方案**：✅ 已施工——`data/pit_query.py`（announce_date<=query_time + LIMIT 1 BY 取查询时点最新版本 + embargo_clause + AS OF JOIN，白名单财务表）+ `backtest/core/pit_manager.py`（PIT 三公理 + pit_consistency_test）。**采纳"时间戳标注+AS OF JOIN"路线，不建独立 PIT 数据库**（与已施工一致）。
- **财报双日期问题**：✅ 已覆盖——A 股语义映射：`first_filed ≈ announce_date`（公告日），pit_query 用 announce_date 过滤即"必须用 first_filed join"的等价实现。**重述泄漏双值存储**：✅ 等价覆盖——ClickHouse ReplacingMergeTree 版本语义下，"取查询时点最新版本"= 当时的 original_value，最新修订值通过全量刷新可得，restated 标志可由版本数>1 派生。
- **特征版本管理机制**：✅ experiment_tracking 模块已施工（config/models/query）；配合 factor_registry 版本字段。"旧版保留≥5年"**采纳**（监管+复现需要，ClickHouse 存储成本可忽略）。
- **PIT 自动化校验**：🟧 Phase 2 增强——deliberate future-date test（label_date=tomorrow 确认零特征 join）自动化纳入 BT-10 体系；时间精度陷阱（date vs timestamp 粒度统一用 date_trunc）加入 PIT 校验 checklist。
- **施工方案**：仅 Phase 2 泄漏测试自动化增强（~50 行测试用例，tests/backtest/ 体系内）。其余无新增施工。
- **过度工程审查**：确认现有实现等价覆盖 2026 标准做法，不引入新组件。✅ 通过。

**原始内容**：因子统一定义-计算-存储-服务(Single Source of Truth)；训练数据Day T因子值=Day T收盘可计算值(PIT铁律)；特征版本管理(逻辑变更时训练集与推理版本号一致，旧版保留≥5年)。**原待讨论问题（已闭环）**：PIT 架构方案→✅ 时间戳标注+AS OF JOIN；版本管理机制→✅ experiment_tracking+registry 版本字段；≥5年保留→✅ 采纳；自动化校验→🟧 Phase 2 泄漏测试自动化。

**2026 算法论据（v0.4.0）**：① **财报双日期**（tradevodata 2026-07，313,562 行实测）：period_end（报告期末）vs first_filed（首次发布日）**平均差距 43 天**（SEC 大型加速申报人 60 天/加速 75 天/其他 90 天）——用 period_end join=给回测 43 天"免费预知"，**必须用 first_filed join**；② **重述泄漏**：18,539 行（5.9%）被后续申报修订 >0.5%，解法=original_value（回测用）+latest_value（实时筛选用）+restated 标志；③ **Observation Spine 模式**：entity×as_of_time 主键，所有特征相对 as_of_time 计算（AS OF JOIN/window aggregate `WHERE feature_time ≤ as_of_time`），标签必须 label_time>as_of_time；④ **时间精度陷阱**：cast('date') 截断到午夜掩盖日内泄漏，须 date_trunc 显式统一粒度，**泄漏检查必须在所有 join 之后**（上游单个泄漏 join 感染整个特征行）。

---

## 15. 资产分级标准（原§4 P0-P3）

> 当前P0-P3自制分级混合了交易准入、数据覆盖、研究范围三个维度，需按专业标准重设计。｜ ✅ **v2.0.0 裁定：两维精简采纳（准入×数据覆盖），P0-P3 deprecated，研究范围维暂缓**

**✅ v2.0.0 裁定结论**：

- **本质**：分级的目的是驱动差异化行为（能不能交易/数据订多频/研究跟不跟），维度数应与行为决策数匹配。3-5 策略小系统只有两类行为决策：交易准入（风控拦截）+ 数据订阅（成本决策）——第三维"研究范围"对 3-5 策略小系统是过度设计。
- **裁定**：① **采纳两维**：交易准入（eligible/restricted/prohibited——直接驱动风控拦截）+ 数据覆盖（real-time/EOD——直接驱动订阅成本，miniQMT 实时流与盘后批量分层）；② **研究范围维暂缓**——用 universe_registry 已有 static/dynamic/rule_based 标签字段承载（已施工），不建独立维度；③ **P0-P3 自制分级标 deprecated**（语义混叠：P0"交易级"≈eligible、P1"待验证"≈candidate 状态、P2"背景级"≈EOD 数据——全部可由两维+universe 标签等价表达，且不映射任何执行动作）；④ **流通市值 6 级分层采纳为交易准入内的子维度**（"市值定调子"原则：同一信号在不同市值段含义不同，是打板/信号解释的第一道筛子——1000亿+/300-1000/100-300/50-100/20-50/<20亿）；⑤ 与 #18 关系确认：本节定义分类框架（两维+市值子维度），#18 定义品种清单，互补不变。
- **施工方案**（Phase 2）：universe_registry 增补 `eligibility`（eligible/restricted/prohibited）与 `data_tier`（realtime/eod）两字段 + 流通市值分层计算字段（数据已有，~30 行计算+登记）；eligible 判定规则复用 UNI-RULE-001 已有过滤链（剔 ST/退市风险/次新/低成交额）。
- **过度工程审查**：三维全套+P0-P3 双轨并行被显式拒绝（减法）；市值分层是计算字段非新数据源。✅ 通过。

**原始内容**：P0 交易级（直接下单）/ P1 待验证交易级（技术可交易，是否交易由回测决定）/ P1 信号级（不买但盯着看）/ P2 背景级（盘前拉取一次）/ P3 远期（预留接口）。**专业机构做法（参考）**：交易准入维度 eligible/restricted/prohibited；数据覆盖维度 real-time/delayed/EOD；研究范围维度 investment/tracking/research universe。**原待讨论问题（已闭环）**：三维度分离还是单一维度→✅ 两维；各维度分类标准→✅ 见裁定①④；与 P0-P3 映射→✅ deprecated（两维+标签等价表达）。

**2026 算法论据（v0.4.0）——A 股流通市值 6 级分层（CSDN 2026-08-08）**：

| 流通市值 | 角色 | 主要玩家 | 波动逻辑 |
|---|---|---|---|
| 1000 亿+ | 超级大蓝筹 | 公募/社保/北向 | 业绩驱动，波动小 |
| 300-1000 亿 | 行业头部/白马 | 北向/公募核心 | 行业景气驱动 |
| 100-300 亿 | 成长股/二线龙头 | 机构覆盖中等 | 成长+估值博弈 |
| 50-100 亿 | 中小盘 | 机构覆盖少 | 共识弱、流动性中等 |
| 20-50 亿 | 小盘(游资主场) | 游资 | 题材/资金驱动，波动大 |
| <20 亿 | 超小盘 | 散户/游资做妖 | 高风险，主力不太进 |

**"市值定调子"原则**：同一信号在不同市值段含义不同——大蓝筹"放量大涨"=机构业绩建仓，小盘"放量大涨"=游资拉题材准备出货；不先看市值就把两种信号喂同一模型=训练精神分裂的判断器。流通市值是第一道筛子，排在所有技术指标之前。市值分层=交易准入维度的子维度（eligible 内再按市值分档），与数据覆盖/研究范围维度正交。

---

## 16. 系统级成功指标（原§9全文）

> 具体收益率/Sharpe/回撤阈值均为拍脑袋数字，不属于硬边界。宪章使命已定义"资产长期复利增长"为成功标准。｜ ✅ **v2.0.0 裁定：修订采纳（生存线数值下调 + 健康/卓越线实盘校准 + 五层框架映射）**

**✅ v2.0.0 裁定结论**：

- **本质**：KPI 阈值的意义是触发"继续/降仓/关停"决策，不是许愿。拍脑袋的绝对数值在 regime 切换时必然失效；2026-07 量化双杀后，"年化超额≥10%"是头部机构水平，设为生存线会误杀可用策略。
- **2026 实证锚点**：私募股票量化多头 2026 上半年平均超额仅 3.11%（去年同期 14.17%）；公募 300 指增 YTD 超额 3.00%；头部 50 亿+私募超额 5.51%；Sharpe 1.0-2.0 为专业合格线，>3.0 持续反而可疑；回测 Sharpe 2.0 实盘通常衰减至 1.0-1.5。
- **裁定**：① **生存线修订**：滚动 12 个月超额>0 且 MaxDD<15% 且 Sharpe≥0.8（替换原"年化超额≥10%、Sharpe≥1.0"）；失败指标维持（连续 6 个月亏损/回撤>25% 与 4 级 Protocol Level4 一致✅）；② **健康线/卓越线暂缓定死**——上线时只锁死生存线（风控属性），运行 6-12 个月（≥30 个收益观测点，统计显著性下限）后用实盘分布校准；③ **五层评估框架采纳为结构**（存活→边际→效率→鲁棒→部署，v0.5.0 已补），原三档映射进前三层：存活=生存线（MaxDD 三维度：深度+持续时间+恢复时间）、健康=边际（Profit Factor>1.5+Expectancy>0）+效率（Sharpe/Calmar）、卓越=鲁棒（跨 regime 稳定性+OOS 一致性）；④ **打板 KPI 单列**：炸板率、隔日溢价、胜率（打板 alpha 结构与多因子不同，不共用超额阈值）；⑤ 成功指标分阶段设定：MVP 期=生存线+失败指标；完整版=五层全量（实盘校准后）。
- **施工方案**（Phase 2，55 号监控文档施工范围内）：生存线+失败指标监控落码（复用 decision_gate 偏差告警通道+alert_rules.yaml 框架，~100 行）；健康/卓越线定义为配置占位，实盘校准后启用。验证：用回测数据回放生存线触发逻辑。
- **过度工程审查**：砍掉拍脑袋阈值=减误报；五层框架是评估结构非新系统；不建独立 KPI 平台（复用 alert_rules）。✅ 通过。

**原始内容**：
- 生存线：年化超额≥10%、Sharpe≥1.0、回撤<15%、uptime>99.9%、审批<2次、Sharpe偏差<30%
- 健康线：年化超额≥15%、Sharpe≥1.5、回撤<10%、A/B周期<6周、IC达标、准确率>60%、修复率>90%、误触发<5%
- 卓越线：年化超额≥25%、Sharpe≥2.0、回撤<8%、容量>3x
- 失败指标：连续6个月亏损、回撤>25%、停机>5分钟/月、审批>5次/月
- 灰色地带：回撤15-25%按4级Protocol、停机50秒-5分钟加强监控、审批偏高触发审视

**原待讨论问题（已闭环）**：阈值需回测验证→✅ 2026 实证锚点+实盘校准；三档划分合理性→✅ 映射五层框架；失败指标依据→✅ 与 Level4 一致；分阶段设定→✅ MVP=生存线+失败指标。

**2026 算法论据（v0.5.0）**：五层评估框架（nexusfi 2026-06：① 存活层 MDD 深度+持续时间+恢复时间 → ② 边际层 Profit Factor>1.5/Expectancy>0 → ③ 效率层 Sharpe/Sortino/Calmar → ④ 鲁棒性层跨 regime 稳定性+OOS 一致性 → ⑤ 可部署层容量/延迟/操作可靠性；每层回答不同问题不能跨层比较）。阈值共识（LedgerMind/tradingwyckoff/nexusfi）：Sharpe <1.0 差/1.0-2.0 好/2.0-3.0 优/**>3.0 可疑过拟合**（BarclayHedge 对冲基金均值仅 0.89）；Calmar >5.0 极罕见；Profit Factor 趋近 1.0=edge 消失；MDD 不能只看深度。**单一指标陷阱**：Sharpe 2.0 在 6 个月低波窗口好看但未经 VIX 飙升≠好；75% 胜率但平均亏损 4×平均盈利=负期望——必须多维交叉验证。

---

## 17. 行为边界重构（原B-002~B-005）

> 这4条从§5移除，不是因为概念错误，而是框架不专业——把风险参数、交易所规则、架构原则包装成"禁止AI做"的行为禁令。机构做法是通过系统设计让这些事架构上不可能发生。｜ ✅ **v2.0.0 裁定：拒绝 OPA/Rego，采纳 choke point + 配置化 YAML 规则**

**✅ v2.0.0 裁定结论**：

- **本质**：B-002~B-005 是"永不成立"约束，需要的是**架构上的不可绕过性**（所有订单唯一出口+默认拒绝），而非策略语言表达力。机构标准做法（SEC 15c3-5 / MiFID II RTS 6 强制盘前检查）：pre-trade risk gate 作为订单路径上同进程单一 choke point——"不存在任何绕过网关到达交易所的路径"。
- **裁定**：① **拒绝 OPA/Rego**——OPA 是云原生多团队多服务授权治理的事实标准，但对单机单人 Python 系统引入 sidecar 进程+Rego 学习曲线，属杀鸡用牛刀（v0.4.0 的 PaC/OPA 方案**修订降级为远期**：若未来演化为多进程微服务再议）；② **采纳 choke point 方案**：唯一 OrderGateway 持有 xttrader 句柄，策略层不 import 交易接口——物理不可绕过；规则用 YAML 声明（杠杆上限/集中度/交易时段白名单/单日限额）+ Pydantic 校验 + Gateway 内顺序检查链 + **默认拒绝**；每次拒绝写结构化审计日志；③ **已施工等效设施确认**：43 门禁引擎 + risk_limits + default_position_limit_checker + g7_position_limits.yaml（集中度/仓位）+ trading_session（时段）+ programmatic_trading_guard + cancel_rate_guard + price_cage——B-002~B-005 语义已**大部分覆盖**，缺口=单一订单出口的架构确认。
- **原待讨论问题闭环**：杠杆/集中度上限→risk_limit_registry（limit_type=leverage/concentration 已登记）+ g7_position_limits；交易时段校验→ex_core/trading_session.py（已施工）；不可绕过保证→choke point 架构（见施工方案）。
- **施工方案**（Phase 2）：① 验证 40 号执行层（G22 已施工 commit 015826ae）所有下单路径收敛到单一出口（架构检查项，若非单一出口则归并）；② 将散落的硬编码限额（position_limit_enforcer 单票≤5% NAV 等）归并到 risk_limit_registry YAML 声明式配置。
- **过度工程审查**：拒绝 OPA=做减法；复用已有门禁体系。✅ 通过。

**原始内容**：
- B-002 禁止AI使用超过杠杆上限 → 应在风险模型中设定，由风控引擎强制
- B-003 禁止AI对单一标的集中度超上限 → 应由回测和风险模型决定，不硬编码
- B-004 禁止AI在非交易时段提交订单 → 交易所规则，执行层技术校验
- B-005 禁止AI绕过风控引擎直接下单 → 架构原则，风控引擎在关键路径

**原待讨论问题（已闭环）**：杠杆/集中度上限模块位置→✅ risk_limit_registry+g7；时段校验组件→✅ trading_session；不可绕过架构保证→✅ choke point。

**2026 PaC 对标（v0.4.0；OPA 已裁定拒绝，保留作远期参考）**：Policy-as-Code 把"禁止 AI 做 X"从文档规则变为可执行代码，订单提交前自动拦截（OPA+Rego 是 2026 事实标准，CNCF 毕业项目，Netflix/Capital One 在用；金融级权限矩阵 NIST SP 800-204D：(subject, object, context) 三元组实时评估+SPIFFE ID）；其优势（策略与代码解耦/Git 版本控制/审计日志自动）对个人系统由 choke point+YAML 方案等价覆盖，OPA 仅远期微服务化时再议。B-002~B-005 的 PaC 映射：

| 原行为边界 | PaC 实现（Rego 策略） | 评估点 |
|---|---|---|
| B-002 杠杆上限 | `deny if order.leverage > config.max_leverage` | FirmRiskAggregator 下单前 |
| B-003 集中度上限 | `deny if portfolio.concentration(symbol) > config.max_concentration` | FirmRiskAggregator 下单前 |
| B-004 非交易时段 | `deny if not is_trading_hours(now())` | 执行层 C-002 订单提交前 |
| B-005 绕过风控 | 架构保证——OPA 在关键路径，所有订单必经 OPA 评估，无 bypass 路径 | 架构铁律 |

---

## 18. 资产与市场覆盖范围（原§4）

> 市场覆盖范围会随账户权限开放、新品种上市、策略演进随时变化，不是硬边界。Charter 只保留原则"能不能买看账户通道，值不值得买看回测结果"，具体品种清单和分级移入此处待讨论。｜ ✅ **v2.0.0 裁定：轻量 Instrument Master（见本节裁定结论）**

**原始内容**：

A股核心矩阵：

| 品种 | 级别 | 数据源 | 数量 | 交易通道 |
|------|:----:|--------|:----:|---------|
| A股全市场 | P0 | miniQMT+iFind | ~5000只 | miniQMT |
| ETF | P0 | miniQMT | ~800只 | miniQMT |
| LOF | P0 | miniQMT | ~400只 | miniQMT |
| REITs | P0 | miniQMT | ~30只 | miniQMT |
| 可转债 | P1待验证 | miniQMT | ~500只 | miniQMT |
| 新股申购 | P1信号级 | iFind/交易所 | 按日历 | — |
| 股指期货 | P2背景级 | iFind | IF/IC/IH/IM | ❌需期货账户 |

其他市场：港股(恒生+AH联动股，P1待验证)；全球(美股指数/行业ETF/中概股/期货/VIX/美债，P2背景级)；汇率/大宗/债券(P2背景级)；加密货币(P3远期)。

**专业机构做法**：Instrument Master（标的主数据：代码/类型/上市日/退市日等静态属性，运行时维护）；Eligibility Engine（按账户权限+券商能力+法规动态计算"能不能交易"）；Universe Definition（投资策略决定"研究哪些、交易哪些"）；三套系统独立运行，不在 charter 中硬编码品种清单。**与 #15 资产分级的关系**：#15 定义分类框架（准入×数据覆盖两维+市值子维度），本节定义品种清单和覆盖范围，两者互补。

**✅ v2.0.0 裁定结论**：

- **裁定**：① **采纳轻量 Instrument Master**——不自建重型系统（机构 200+ 字段对个人系统是公认过度设计教训），用 miniQMT 标的信息 + ClickHouse 补充字段 = 轻量 A 股 IM；② **最小字段集**：v0.4.0 的 15 字段 + A 股必需补充——板块代码（主板/科创/创业/北证，决定涨跌幅 ±10%/20%/30%）、ST/*ST 标志及变更日期（2026-07 新规后主板 ST 已 ±10%+单日买入≤50万股限制，直接影响交易准入）、退市整理期标志、上市日期（次新过滤）、停牌标志、昨收价（算涨跌停价）、最小申报单位（主板 100 股/科创板 200 股起）；③ **ST 状态 PIT 跟踪采纳**（A 股特有需求，schema 已有 market_st_stock_list，落 effective_date 表）；④ **标识符映射采纳**——证券代码+交易所作 canonical ID，symbol_normalizer 已施工✅；⑤ **准入引擎**用 #17 choke point 方案的 YAML 规则（非 OPA）；⑥ **投资域定义放 universe_registry**（已施工✅）；⑦ 新品种扩展路径：可转债（schema 已有 market_convertible_bond 系列，P1 待验证→回测验证后转 eligible）→港股（schema 已有 hk 系列，需港股通权限）→期货（P2 背景级维持，需期货账户）。
- **原待讨论问题闭环**：IM 建设=轻量表（非重型系统）✅；准入规则配置=YAML（账户权限+券商能力+法规）✅；投资域=universe_registry ✅；新品种流程=可转债→港股→期货渐进路径 ✅。
- **施工方案**（Phase 2）：ClickHouse 建轻量 IM 表（复用现有 schema，~1 张表+每日盘前 xtdata 同步脚本 ~80 行），ST 状态 PIT 子表；与 universe_registry 的 eligibility 字段联动（#15）。
- **过度工程审查**：拒绝 200+ 字段重型 IM/独立 Eligibility Engine 服务=做减法；全部复用现有 schema。✅ 通过。

**2026 算法论据（v0.4.0）**：① **最小 15 字段集**（Finantrix 2026-03：机构级 200+ 字段实际常用 <50）——证券代码/交易所(SH/SZ/BJ)/证券类型/上市日期/退市日期/复权因子历史/股本变更历史/ST/*ST 状态变更/流通股本/总股本/行业分类/交易单位/最小变动价位/涨跌停规则/是否融资融券标的；② **PIT 跟踪**（Intrinio 2026-02）：退市公司、ST 变更、股本变更都需 effective_date 记录，否则回测有幸存者偏差——A 股退市率低但 ST/*ST 变更频繁，**ST 状态 PIT 跟踪是 A 股特有需求**；③ **标识符映射**：证券代码+交易所作 canonical（比全球 CUSIP/ISIN/FIGI 简单），但 miniQMT/iFind/交易所代码可能不一致需映射层。

**CAI++ 防御信号补充（v1.4.0，Risks 2026,14,86 Hatzopoulos&Statiou）**：CAI（Copula Asymmetry Index）=滚动窗口联合"股跌&波升"尾部事件经验频率−镜像"股升&波降"经验频率（rank-based 非参数，无需 copula 拟合）；CAI++ 框架（smoothing→standardization→delayed execution 防假信号→hysteresis 防抖动→cost-aware portfolio mapping）转防御分配信号。2000 年起 50 个 equity-volatility 对实证 vs 60-40 占优，但**不替代 risk parity**（定位 tail-aware overlay 非低波动基线替代）。对接：§18 股指期货 P2 背景级→防御信号转化路径（用 IF/IC 收益+10 号 synthetic VIX 算 CAI，CAI 高位→降仓位）；延迟执行+迟滞与 4 级 Protocol 恢复机制同构防抖动；与 91 号 conformal 同为分布无关哲学正交可叠加。CAI ~30 行+框架 ~100 行，drawdown_controller/kill_switch Phase 2 事前防御 overlay（A 股需独立验证）。

---

## 19. 大额下单控制与算法执行（原B-013.6）

> 单笔限额应由风险模型动态计算（基于 ADV、波动率、流动性），不是 charter 硬编码。大额订单用算法执行（TWAP/VWAP/IS），不是人工审批。｜ ✅ **v2.0.0 裁定：默认限价单 + 打板专用路径，删 5%ADV 硬条款，算法执行降远期**

**✅ v2.0.0 裁定结论**：

- **本质**：TWAP/VWAP 解决的是"订单规模相对市场成交量足够大、自身冲击推动价格"的问题。个人单票几万~几十万 vs A 股小盘日成交数千万~数亿，占比通常 <0.5% ADV，冲击成本可忽略（见 §5）；拆单反而增加时延暴露（执行越慢，逆向价格风险越大）。
- **裁定**：① **删除"单笔>5% ADV 切算法执行"硬条款**——个人资金量级永远触不到，是伪精确；② **默认单笔限价单**（miniQMT 10 笔/秒限制对单账户个人策略绰绰有余）；③ **打板买入逻辑上不可拆单**——打板是"抢排队优先级"（封板后买不进、未封时抢速度），正确做法是**打板专用执行路径**：集合竞价/早盘瞬时单笔限价（涨停价）申报+封单强度过滤（封成比≥5%，见 §1 v0.7.0）；④ **防异常交易监控**：单笔 >该票分钟级均量 5 倍时简单分 2-3 笔、间隔 3-5 秒（避免单笔记入交易所异常交易监控，2026-04 程序化新规）；⑤ **IS（Implementation Shortfall）作为记录指标**（每日复盘校准滑点假设，default_tca_engine 已施工），非执行算法选型依据；⑥ **人工审批仅用于极端情况**（突破风险预算上限），常规订单零审批（原 B-013.6"大额必审批"语义废弃——X 随 AUM 变化，硬编码无意义）；⑦ **TWAP/VWAP/POV/ICEBERG 代码保留但降级远期**——ex_sor 已施工的算法族在资金量级到单票百万+前不启用；RL 执行/MAP-Elites 维持"已评估不整合"（v0.8.0/v1.6.0 结论）。
- **原待讨论问题闭环**：ADV 阈值→删除✅；算法选择策略→默认限价单✅；模块位置→ex_sor 已施工✅；流动性枯竭 fallback→#8 压力退出时间禁开仓开关+kill_switch 流动性危机停开仓（已施工）✅；与 BudgetChangeHandler 协同→大额 budget 变动走三级升级（30 号 §2.4 已定）✅。
- **施工方案**（Phase 1，40 号已施工范围内的配置调整）：algo_execution_selector 默认策略改为限价单直投；打板策略走独立执行函数。验证：TCA 复盘 IS 分布与滑点假设偏差。
- **过度工程审查**：删硬条款+降级算法族=做减法；无新增组件。✅ 通过。

**原始内容**：B-013.6 禁止AI自主执行大额下单（超过风控框架设定的单笔限额）→ C-002交易执行在单笔金额超过限额时自动拦截→推送人工审批→C-031置信度分层中大额下单永远属于"需人工确认"级别。

**专业机构做法**：仓位限额 = f(ADV, 波动率, 流动性, 相关性) 全部动态参数；大额订单用算法执行（TWAP/VWAP/IS）自动拆单；真正的控制=单笔订单量/ADV > X% 时自动切算法执行，X 由风险模型计算；机构不会在 charter 写"超过X万需审批"（X 随 AUM 变化）；人工审批仅用于极端情况（如突破风险预算上限），不用于常规大额订单。

**原待讨论问题（已闭环）**：ADV 阈值/算法选择策略/模块位置/流动性枯竭 fallback/与 BudgetChangeHandler 协同——全部见上裁定①-⑦。

**2026 执行算法四层谱系（v0.3.0）**：① **静态算法（TWAP/VWAP/POV）**——基线（TWAP 均匀时间切片抗操纵但可预测/VWAP 按成交量曲线需在线纠偏/POV 跟单陷阱），A 股散户默认用此层；② **优化算法（Almgren-Chriss IS）**——均值-方差最优轨迹，λ→0 退化 TWAP，λ>0 前置加载减少价格风险；③ **RL 自适应（PPO/TD3/TT-DAC-PS）**——PPO 在 LOB 回放上 IS 2.13bps vs VWAP 5.23bps（$21B 名义），TT-DAC-PS 双目标+策略平滑超 PPO/SAC/A2C，但**需 LOB 数据+仿真器+~20h 训练，个人 A 股不适用**（无 LOB 接入、资金量小、T+1 限制）；④ **质量多样性（MAP-Elites）**——regime 专家集成（按流动性×波动率索引），niche 内 8-10% 提升，计算密集机构级。统一度量 `IS = (P_execution - P_decision) / P_decision`。

**A-CRaQL（v1.6.0，arxiv 2608.04305 ICAIF'26，已评估不整合）**：不改 CVaR 估计器与 Bellman 不动点，仅重设计训练流程（6 项协同机制：逐格内步长/外层速率衰减/VaR 内变量早期校正/覆盖优先采样/渐进后缀聚合/在线标度校准），CVaR Bellman residual 降 ~85%。不整合理由：仍是 RL 训练流程，不改变"RL 执行在个人系统必要性存疑"的根本结论——与 v0.8.0 SOIC Vol.16（U Hull 2026-08）实证一致（conformal 门控成本方差 19.1→10.0bps 优于 PPO 跨种子高方差，"慢而稳 conformal 胜过 RL"在执行域成立）；且 P-4 已议放弃 41 号阶段 7 执行 RL。记 41 号 Phase 5+ RL 训练流程候选，未来资金量增长重启 RL 执行时评估。

---

## 20. 工程细节移出项（原B-008/B-010/B-012/B-013）

> 以下条目从 charter §4 移出，原因是工程实现细节或重复映射，不属于 charter 级安全边界。归入各自模块配置项。｜ ✅ **v2.0.0 裁定：逐项闭环（见本节开头裁定结论）**

**✅ v2.0.0 裁定结论**：

- **B-008（单次自迭代变更范围）**：✅ 采纳归 C-007 配置项。阈值裁定：**单轮迭代 ≤3 个参数 或 ≤1 个模块**（按影响半径分组，取更严者）——第一性原理：变更范围阈值的本质是"故障爆炸半径控制"，单人系统无并行团队，小步快跑+git 可回滚是最优；具体数值上线后按迭代成功率校准（Phase 2）。
- **B-010（退役策略相似度）**：✅ 采纳**三维指纹**（AST 哈希精确复制 + CodeSAGE 语义嵌入 + DTW PnL 形态）——AST/CodeSAGE 已施工（echo-guard），**DTW 为 Phase 2 施工缺口**（~80 行，dtw-python/fastdtw 库）；退役决策树采纳五选项版（人工重优化 / EvoQuant LLM 自演化[远期] / Layering / 暂停减仓 / 退役），**触发条件**用 v0.5.0 决策树+5 预警信号（`Sharpe<1.5 AND IC<0.05 AND 3次改造失败 AND 维护成本>收益30%`）。**90 天滚动相关性剔除规则**：与已施工 strategy_correlation_gate（MOD-PA-004：>0.85 REJECT/>0.90 HARD_REJECT）口径统一——**采用现有 0.85/0.90 阈值 + 补"持续 30 天"持久化条件**（Phase 2，避免单日噪声误剔除）；intent netting 列为 41/42 号 Phase 2 订单合并优化（非本节）。
- **B-012（付费数据源审批）**：✅ 闭环——归运营策略文档+Administrator 审批，治理规则已足够，无需代码。
- **B-013（版权）**：✅ 闭环——依赖 §5 L-005 合规映射（《著作权法》第24条），策略工厂产出不含原始内容即可，**不增加额外版权检查步骤**（避免重复治理）。
- **施工方案**（Phase 2）：① echo-guard 扩展策略指纹库（退役策略 AST+CodeSAGE+DTW 三维入库，~100 行）；② strategy_correlation_gate 补持久化条件；③ EvoQuant LLM 自演化重优化列远期（验证器引导管线=BM-BT 体系原生对接，非 MVP）。
- **过度工程审查**：指纹库复用 echo-guard 引擎非新建；EvoQuant 显式远期；B-012/B-013 零代码。✅ 通过。

**原始内容**：
- **B-008 禁止AI在单次自迭代中同时修改过多关联参数** → 工程实现细节，归 C-007 闭环优化引擎配置项（每轮迭代变更范围阈值，原问题：阈值如何配置/按参数类型分组/按影响半径）
- **B-010 禁止AI上线与已退役策略高度相似的新策略** → 工程实现细节，归 C-006 策略工厂配置项（退役策略指纹库+相似度比对阈值，原问题：相似度比对用什么算法）
- **B-012 禁止AI自动订阅付费数据源** → 成本控制是运营策略，归运营策略文档（数据源变更需 Administrator 审批）
- **B-013 禁止AI在未经用户确认的情况下使用用户提供的UP主/频道内容做商业用途** → 版权合规已在 §5 L-005 法规映射覆盖（《著作权法》第24条），重复

**原待讨论问题（v2.0.0 已闭环）**：B-008 阈值配置→✅ ≤3参数或≤1模块取严者，上线后校准；B-010 相似度算法→✅ 三维指纹；B-012 审批流程位置→✅ 运营策略文档+Administrator；B-013 版权检查步骤→✅ 不需要，依赖 L-005。

**2026 施工参考论据**：

- **三维指纹分工（v0.3.0）**：代码逻辑相似度（防换名复活）=AST 哈希 Tier1+CodeSAGE 语义嵌入 Tier2（sim≥0.94，echo-guard 已施工）；PnL 曲线相似度（防行为等价新瓶旧酒）=**DTW 优于 Pearson**（允许时间轴非线性对齐，捕获"形态相似但相位偏移"）——DTW 管形状、Pearson 管方向，两者均超阈值才算相似。DTW 局限（Polito 2026-03）：稳定低波 regime 有用、高波 regime 传统指标更好、跨资产不迁移需重新校准——作 echo-guard 的 PnL 维度补充非替代。
- **策略退役决策树（v0.5.0）**：生命周期事实——68% 系统化策略 18-24 个月内需重大修改或退役（DeepTradeX 2026）；**Edge Decay 三分法**（luxalgo 2026-08-03）：重优化（核心逻辑成立+OOS 正+邻近参数相似）/暂停减仓（证据混合+expectancy 趋零+回撤超常但可辩护→砍半观察）/退役（OOS expectancy 负+walk-forward 持续失败+成本吞噬 edge+前提不再成立）；**5 预警信号**（WorldQuant Alpha 失效，CSDN 2026-06）：① 因子拥挤度（相关性>0.6 或 HHI>0.25）；② 收益分布异变（偏度>1.5/峰度>3.5 或<2.5/日胜率连续 20 日<52%）；③ 市场状态适应性衰减（HMM 检测状态切换亏损）；④ IC 持续<0.05；⑤ 维护成本>收益 30%。滚动窗口：30-50 笔早期预警/100+ 笔确认；回撤漂移>1.5-2×历史最大回撤；胜率降 10-15pp 连续两窗口；Profit Factor 从 1.5-2.0 滑向 1.0。指纹入库前先用决策树量化确认"确实应退役"而非"正常回撤恐慌"。
- **Alpha Decay 数学模型（v0.6.0，mathandmarkets/hftradingbook）**：指数衰减 `α(t) = α₀ · e^(-λt)`，半衰期 `t½ = 0.693/λ`（动量策略 t½≈20 个月 λ≈0.035，因子拥挤后缩短）；**成本地板**——alpha 衰减到成本地板（个人 A 股往返 1-2%，年化<1.5% 即拖累）以下不可交易，可交易半衰期<数学半衰期（α₀=5%、λ=0.035 时数学 t½=20 月、可交易期约 34 月）；**复杂度-过拟合差距**（V1 简单动量 backtest-reality gap -66%→V5 ML -100% 完全反转——复杂策略回测更需 DSR/PSR 校正）；**容量 4/9 规则**：net edge per unit = g − c·√Q，盈亏平衡 `Q*=(g/c)²`，**利润最大化规模 Qmax = 4/9·Q\***（约 44%）——策略应运行在容量天花板内 44% 处。对接：上线后记录 α₀ 估算 λ/t½；α(t) 跌至成本地板触发三分法；单策略资金 ≤ Qmax。
- **2026-07 量化"双杀"实证（v0.9.0）**：动量因子月回撤超 **20pp**（十年罕见），摩根士丹利 TMT 动量组合 17 交易日峰谷回撤约 40%，中证 500 指增平均 -17.80%（超额 -4.54%）/中证 1000 指增 -19.13%（超额 -1.69%）；根因=极致风格收敛+AI 板块高位回调+动量信号滞后+因子同向回撤（分散逻辑短期失效）；量化私募 3 万亿规模（71 家百亿）加剧容量压力。印证：① 退役决策树触发条件的真实形态；② 4 级 Protocol Level3（20%）必要性（7 月创业板指 -23% 已触达）；③ HRP 识别因子隐性相关性的价值（naive risk parity 因子同向回撤时分散失效）。
- **退役决策树第 4 选项 Layering（v0.7.0，pomegra.io 2026）**：保留衰减策略运行（reduced allocation）+叠加新 alpha 源（residual edge+fresh edge=组合 edge 回升）——比退役灵活、比重优化激进；三分法管"原策略怎么办"，Layering 管"原策略+新信号怎么办"，非互斥（先 Layering 观察，不回升再走三分法）；机构多用 hybrid，formal alpha decay analysis 是 portfolio governance 标准组成。打板策略可 Layering"反量化"新信号（低位干净筹码小票+事件催化，见 §1 v0.6.0）。决策树更新：`if (α(t) < 成本地板) → {重优化 | Layering | 暂停减仓 | 退役}`。
- **退役决策树第 5 选项 EvoQuant（v0.8.0，arxiv 2607.12455 HKUST）**：LLM 自演化+验证器引导自动化重优化（四模块：摄入表示 AST+语义图→瓶颈定位→语义受控候选编辑→多阶段验证管线选最优+经验蒸馏）；7 策略（4 A 股+3 加密）平均 test Sharpe **-0.298→0.538**，最佳 +199%（含 walk-forward+成本压力测试+消融）。工程参考 LangGraph+Harness CI/CD（CSDN 2026-08-07）：严苛风控守门人路由 `Sharpe>=1.5 AND MaxDD<=15%→submit；iteration>=max→abort；else→reflect`——**未达标坚决 ABORT 非 submit**。对接：验证管线=BM-BT 体系原生对接；should_continue 路由可编码进 C-007 迭代逻辑；知识蒸馏与 echo-guard 指纹库互补（防重复 vs 促复用）。远期，决策树更新为五选项。
- **revalidate 衰减感知再验证（v1.5.0，AlphaCrafter arxiv 2605.05580）**：周期性重验因子 IC/ICIR/换手/覆盖/**跨 regime 衰减剖面**+自动剪枝显著衰减因子——项目 factor_pool_manager（ADR-FAC-006）8 状态生命周期+decay_monitor+three_level_judgment 的学术印证；新增维度=跨 regime 分桶衰减剖面（熊市态衰减可能加速，与 10 号 regime 分桶输出协同）。多智能体框架本身不采纳（过度工程）。factor_pool_manager Phase 2 增强方向。**Johnson S_U 尾部羊群指标（v1.6.0，arxiv 2607.27063）**：CSAD 的尾部增强版（非线性变换恢复极端羊群信息，CSAD 线性偏离度压缩尾部），重大冲击期上升；A 股散户主导羊群显著，可作 25 号另类因子或 37 号预警信号（scipy.stats.johnsonsu ~50 行，Phase 2 与 32 号 HBI/CSAD 并列评估，实盘 6 月后校准参数）；agent-based 网络模型本身不采纳（理论工具）。
- **MINGLE 评估不采纳（v1.6.0，arxiv 2608.06618）**：ADMM+图拓扑学习对个人系统偏重（与已拒绝 HRP/MVO 同类复杂度），5 策略规模边际收益不显著（优势在 N>20 大资产池），依赖因子暴露矩阵估计引入不稳定性。**Phase 5+ 远期重评条件：策略数>8 且 correlation_dedup 实测漏检率高**。
- **90 天滚动相关性剔除规则（v0.8.0，youcanbuildthings 2026-05）**：两策略 90 天滚动相关性 >0.70 持续 30 天→剔除低 Sharpe 策略（分散收益消失，只增加经纪费+操作风险）；per-strategy drawdown circuit breaker 15% half/25% zero——与 4 级 Protocol Level2/Level4 原生对接；intent netting（同标的反向订单送 broker 前净额结算，减一半经纪费）列 41/42 号 Phase 2。23 号策略相关性文档可补入作退役的相关性触发条件（与 Alpha Decay 的 Sharpe/IC 触发并列）。

---

## 21. 做T方法论定义

> "做T"在 charter §1.3（13个优化维度之一）/ §3 约束一（做T额外成本）/ §7 A-003（T+1制度不变→做T）多处引用但从未正式定义。系统已有3个做T策略代码实现但无方法论文档。本节补全定义。｜ ✅ **v2.0.0 裁定：采纳为受约束 overlay + 补齐四规则**

**✅ v2.0.0 裁定结论**（闭环原待讨论问题）：

- **容量上限**：个人资金（单票几万~几十万）远触不到容量顶——真正约束是**成本**（单次往返硬成本≈0.10-0.15%，见 §5）与**胜率纪律**。容量估算式留档：容量≈底仓市值×做T仓位比×日内可成交性。
- **底仓 sizing 规则**：**单次做T仓位 ≤ 底仓 20-30%**（取保守端——打板/事件策略底仓本身波动大；文档原建议 1/3~1/2 偏激进），做T专用资金与主策略仓位**分账记账**（成交回报分账以归因）。
- **做T 与 regime 关系**：**仅在量比>1 且预期振幅 >2×单边成本（≈0.3%）时开仓**；低波/缩量日强制不做（r1 低波震荡态默认关闭做T）；与 §8 流动性前置检查共用阈值。
- **做T 失败处置**：① 反T 未接回：**14:30 后强制限价/市价接回**（宁可亏价差不留隔夜敞口）；② 正T 买入后无法当日卖出是 T+1 固有风险——以**"买入前底仓可卖量"为硬约束**（可卖量=0 时禁开正T），且设单笔止损 -1.5%~-2%。
- **与主策略协同/冲突**：**主策略卖出信号优先于做T持有**；做T层每日开盘从主策略持仓快照同步"可用底仓额度"，两层成交回报分账记录。
- **3 个已有策略整合**：暂不整合为统一框架——三者 alpha 来源不同（冲高回落=日内动量反转、盘口失衡=微结构、VWAP回归=均值回归），保留独立策略，统一走 tick_strategy_base 基类（已施工✅）；是否合并待实盘 6 个月各自 IC/胜率数据说话。
- **施工方案**（Phase 2）：四规则配置化写入做T策略配置（tick_strategy_base 配置项：max_t_position_ratio=0.25 / min_volume_ratio=1.0 / min_expected_amplitude=2×cost / force_cover_time=14:30 / stop_loss=-1.5%~-2%，~50 行配置+校验）。验证：tick_replay 回放四规则触发正确性（已有回放引擎）。
- **过度工程审查**：全部配置项非新架构；不建统一做T框架。✅ 通过。

**定义**：

做T = 持有底仓 + 日内高抛低吸。在A股T+1制度下，通过持有底仓变相实现T+0：当日卖出底仓份额（高抛），当日再买回等量份额（低吸），收盘后底仓数量不变但持仓成本降低。本质是利用日内波动赚取差价，非方向性策略。

**与"日内T+0额外成本"的区别**："做T"是策略类型（底仓+日内高抛低吸）；"做T额外成本"是该策略产生的额外成本（滑点×2+失败风险溢价），是成本模型的一个组成部分（charter §3 约束一）。

**已有代码实现**（src/zephyr/pf_core/）：`intraday_surge_fall_strategy.py`（30秒冲高回落做T）/ `orderbook_imbalance_strategy.py`（盘口失衡反转做T）/ `vwap_reversion_strategy.py`（VWAP回归做T）/ `tick_strategy_base.py`（Tick级策略/做T基类）/ `core/tick_replay.py`（秒级做T专用回放引擎）。

**成本模型**（charter §3 约束一引用）：做T额外成本 = 滑点×2（一买一卖两次滑点）+ 失败风险溢价（日内未买回底仓的隔夜风险）；具体滑点模型和失败风险溢价计算见 §5。

**适用条件**：标的=高波动+高流动性（日内波动空间>做T额外成本）；底仓=已有持仓且不动用底仓做方向性赌注；频率=3秒Tick用于做T买卖点触发（charter §2 约束四）；风控=底仓暴露风险+日内操作风险（纳入风险模型）。

**原待讨论问题（已闭环）**：容量上限/底仓 sizing/regime 关系/失败处置/主策略协同/3 策略整合——全部见上裁定六项。

**2026 方法论论据（v0.3.0）**：**正 T**（先低吸后高抛：盘中低位买入→反弹后卖出等量底仓，适用震荡上行/低开反弹；风险=买入后持续大跌仓位被动加重）与**反 T**（先高抛后低吸：高位卖出底仓→回落后买回等量，适用震荡下行/高开回落；风险=卖出后持续拉升踏空丢筹码，**反 T 难度更高**，单边大涨慎用）；仓位管理原建议底仓 1/3~1/2 做日内（v2.0.0 裁定收紧为 20-30%），收盘持仓总量≈开盘（做T不增加总仓位）；日内指标三层栈（quantzee 2026-06：VWAP 日内公允价值+趋势工具 SuperTrend/EMA+动量振荡器 RSI/MACD，专业交易员 2-4 个指标**不超过 4 个**）；**避开前 30 分钟**（开盘假信号率最高）；量化做T路径参考（arxiv 2103.13507：MLP 预测日内趋势→11:20 前买入→14:50 卖出，每日重训练防隔日 gap）。

---

## 22. 作战地图选股层补充环节（v2.0.1 作战地图全覆盖补丁新增）

> 以下 5 条为作战地图（battle_map）stock_selection 流程的 design 态环节，在本稿登记为**开放问题**——均未进入 MVP 施工清单，各含与既有环节的边界消歧（防止与已 production/已裁定环节混淆）。裁定统一格式：定位 → 裁定（理由+重评条件）→ 契约/参数/接口 → 边界消歧。

### 22.1 BM-SEL-05-D 主力行为自迭代推演（C-034，L2-B，design）

- **定位**：实时识别主力在场（BM-SEL-05-B）之后，动态推演主力后续行为以指导操作——行为分类 5 态（出货/做T/调仓/加仓/观望）+ 出货派发概率 + 假动作识别 6 类（假拉升/假突破/假吸筹/假洗盘/假护盘/假反弹）+ 行为模式库自迭代（持续学习）。消费=实时识别层结果 + 历史主力行为样本 + 底部筹码变化 + 大单净流向 + 龙虎榜席位；产出注入 SEL-02-L 聚合器。
- **裁定：登记远期候选，MVP 不建**。理由：① 输入层（资金性质 5 类分类，见边界）已 production，本环节是在其上的**时序推演层**——推演准确率依赖行为样本库积累，个人系统无标注数据冷启动；② 假动作 6 类识别的误报代价高（误判"假突破"会系统性踏空真突破）；③ 模式库自迭代属在线学习，与 project_memory"Mamba/SSM/RL 不采纳"的模型纪律边界需谨慎对齐。**重评条件**：资金性质特征实盘跑满 6 个月且人工复盘确认"行为误判"是主要亏损源时，先建规则版 5 态分类器（非自迭代），模式库自迭代再后移。
- **契约/参数**：行为分类 5 态 enum + 出货派发概率 float∈[0,1] + 假动作 6 类 enum + 决策建议（跟随/回避/减仓）三值；降级=推演失效仅输出实时识别结果（SEL-05-B），不输出行为预判。
- **边界消歧**：**25 号 §647-656 资金性质 5 类（拉升/吸筹/弱托底/对倒嫌疑/出货）已 production，是输入特征层**（静态截面分类"资金在干什么"）；本环节是**行为推演层**（动态时序推演"主力下一步要干什么"+ 假动作识别 + 模式库自迭代）——两者是"特征输入 vs 行为预测"的上下游关系，不是重复建设。

### 22.2 BM-SEL-05-E 庄家行为识别与模拟（C-035，L2-B，design）

- **定位**：小盘股庄家操作模式（建仓/洗盘/拉升/出货 4 阶段）与一般主力不同，需专项识别——庄家 4 阶段识别 + 对倒识别（同营业部买卖）+ 庄股特征（控盘度/筹码锁定）+ 模拟庄家意图（博弈论）。消费=筹码分布（底部筹码长度/集中度）+ 龙虎榜（同一营业部对倒）+ 分时量价 + 盘口挂单时序；产出=庄股回避/跟随建议注入聚合器。
- **裁定：登记远期候选，MVP 不建**。理由：① 与 22.1 同源——特征输入层已 production，专项层依赖龙虎榜席位数据质量（同一营业部对倒识别需席位级关联，AKShare 龙虎榜数据粒度待验证）；② 博弈论意图模拟是研究课题非工程任务，个人系统样本不足以校准；③ 回避需求（不碰庄股）可由 universe_registry 过滤规则低成本覆盖（市值/流动性/波动异常筛选），专项识别是"跟随"需求的增强而非"回避"的必需。**重评条件**：打板/事件 sleeve 实盘中庄股踩雷（洗盘误止损/出货误接盘）成为可归因亏损源时，先建 4 阶段规则识别器（控盘度+筹码锁定双特征），意图模拟永列研究候选。
- **契约/参数**：庄家阶段 4 态 enum（建仓/洗盘/拉升/出货）+ 控盘度 float + 筹码锁定度 float + 对倒嫌疑 bool + 回避/跟随建议；降级=庄家识别失效按一般主力行为处理（回落 BM-SEL-05-D）。
- **边界消歧**：同 22.1——25 号资金性质 5 类是输入特征层（其中"对倒嫌疑"已是 5 类之一，production），本环节是**庄家专项推演层**（4 阶段时序 + 意图模拟），是 22.1 的庄家特化分支而非并行重复。

### 22.3 BM-SEL-06 跨市场传导感知（C-039，L2C，design）

- **定位**：美股/港股/汇率/商品异动到达时，用 C-039 传导系数模型计算**对 A 股的影响幅度量化预测**——消费全球市场数据（L0）+ 传导路径图（L2-D 知识图谱），产出"A股影响幅度预测"，下游触发全量/板块重算（MOD-SIG-038，planned）。
- **裁定：登记远期候选，MVP 不建**。理由：① 风控侧已有前兆监控（见边界），alpha 侧量化预测是"预测明天哪些板块受益/受损"的增量——传导系数需分板块历史回归估计，样本稀疏（极端外围异动每年仅数次）系数不稳定；② 个人系统交易日频策略，传导的首日冲击已反映在开仓价中，T+1 下无法抢跑；③ 板块重算触发器可由 36 号风控前兆告警人工/半自动代理。**重评条件**：22 号板块轮动 sleeve 实盘化且外围传导误判成为其可归因亏损源时，先建"板块×外围资产"静态传导系数表（年度回归更新），动态模型后移。
- **契约/参数**：传导系数模型（板块×外围资产回归系数表）+ A股影响幅度预测（分板块 float）；降级=C-039 未就绪时异动仅告警不量化传导（即 36 号现状）。
- **边界消歧**：**36 号 §3 BS-005（BS005_CONTAGION）跨市场传导是风控前兆监控（已 production）**——管"外围异动来了要不要盘中重算 VaR/降仓"（防守触发器）；本环节是 **alpha 侧传导量化**——管"外围异动对哪个板块是机会/风险、幅度多大"（进攻预测）。前者已建，后者登记远期，两者消费同一外围行情输入但产出与用途正交。

### 22.4 BM-SEL-10 行情生命周期阶段（L2C，design）

- **定位**：盘后判定行情生命周期**春夏秋冬 4 阶段**——输入=板块新高占比趋势（L0），输出=春夏秋冬标签，下游约束=**冬季禁抄底 / 秋季强制离场**（MOD-SIG-041，planned，草图§6.7 v4.1）。
- **裁定：登记远期候选，MVP 不建**。理由：① 与 regime（市场级节流）和情绪周期（sleeve 内择时）三者共存会引入第三套"市场阶段"标签，标签间冲突仲裁成本高于增量收益——新高占比趋势与 regime 4 态 HMM 的波动率/趋势维度高度相关；② "冬季禁抄底/秋季强制离场"的硬约束语义可暂由 regime r4 熊市阴跌态的 Shrinkage 节流代理；③ 4 阶段划分的历史回测校准（新高占比阈值）未做。**重评条件**：regime 4 态在跨年级别牛熊转换中被证明颗粒度不足（如 2024 微盘崩盘式结构性冬季 r4 无法区分）时，评估将生命周期作为 regime 的**低频 overlay**（季度级判定）而非并行体系接入。
- **契约/参数**：阶段数 4（春夏秋冬）+ 新高占比趋势输入 + 季节约束规则（冬季禁抄底/秋季强制离场）；降级=生命周期未就绪不加季节性约束（现状）。
- **边界消歧**：**28 号情绪周期 4+1 阶段是 sleeve 内 alpha 择时**（游资情绪温度驱动，决定打板链买卖什么、几成仓，BM-SEL-23-B 已 production）；**10 号 regime 是市场级风险节流**（4 态 HMM+3 overlay，决定全组合多谨慎，已 production）；本环节是**行情生命周期**（板块新高占比趋势驱动的低频牛熊季节判定）——三者输入源、时间尺度、消费方式均不同（情绪=日频游资数据/sleeve 内；regime=日频价量/市场级节流；生命周期=周月频新高占比/季节级禁为），不是同一物的三种说法。

### 22.5 BM-SEL-26 决策可解释性与人机协作（C-030，L6，design）

- **定位**：决策产出时/人工复核请求时，提供 **C-030 决策溯源链**（决策→因子贡献→信号源→数据链路的完整回溯）+ 人机协作接口。消费=决策链路+置信度+因子贡献度；产出=溯源链路 → 置信度分层 → 人机协作输出 → 执行/拒绝（planned，D_INTELLIGENCE 域）。
- **裁定：登记 Phase 2 候选，溯源链先于协作接口建设**。理由：① C-031 置信度分层与审批频次已裁定（见边界），缺的是"为什么这么决策"的可回溯性——个人+100%AI 开发模式下，Owner 复盘时唯一信任来源就是溯源链；② 溯源链的工程依赖（决策链路埋点/因子贡献度计算）横跨信号/组合/执行多层，MVP 阶段先用结构化日志（决策时快照输入因子值+触发规则 id）低成本实现 80% 价值；③ 人机协作接口（对话式追问）依赖 LLM 基建，列 Phase 3+。**重评条件**：首批策略实盘上线后，Owner 周复盘出现"无法回答为什么这笔交易"的具体案例时，立项结构化决策快照（最小实现），完整溯源链与协作接口随 D_INTELLIGENCE 域施工排期。
- **契约/参数**：溯源链=决策 id → 触发信号列表+因子贡献度+数据版本引用；协作接口=查询/复核/否决三类操作；降级=可解释性缺失时降级人工复核（不阻塞交易链路）。
- **边界消歧**：**本稿 §12/§19 已裁定 C-031 置信度分层与审批频次**（审批 2~5 次/天灰色地带→3 次通知/4 次触发审视；大额下单永远属"需人工确认"级别）——C-031 管"什么时候该问人"（置信度分层触发），本环节补 C-030 管"问人时给人看什么"（溯源链证据）。两者是同一 L6 层的触发侧与呈现侧，C-031 已定默认配置，C-030 登记建设路径。
- **Phase 2 排期登记（2026-08-20，AI-NIGHT-001 包 Q2）**：Phase 1 最小实现已落地——`src/zephyr/signal_fundamental/audit/decision_snapshot.py`（MOD-SIG-DSNAP，MATURITY=testing）：`DecisionSnapshot` 不可变快照（decision_id/strategy_id/symbol/action + input_factors + triggered_rule_ids + factor_contributions + data_versions + confidence）+ JSONL append-only 记录器，双空即 degraded=True 降级不阻塞（§22.5 契约口径）；配套测试 tests/signal_fundamental/audit/test_decision_snapshot.py。**Phase 2 剩余两项排期**：① **消费方接入点**——决策链路埋点接线（信号层信号产出点/组合层 sizing 决策点/执行层下单提交点三处调用 `DecisionSnapshotRecorder.record`），当前全 src 无生产调用方（模块头 [CONSUMERS] 已声明"决策链路埋点接线挂起待 Owner"，宪章 B-007 纪律），排期=首批策略实盘上线前装配批（与 41/42 号买卖流接线同批评估）；② **存储后端评估**——现状 JSONL 本地文件（append-only，与 66 号 commit_queue/实验跟踪 FallbackBackend 同款 JSON 纪律），评估候选=维持 JSONL（默认，快照量级低）vs 复用 experiment_tracking FallbackBackend 目录结构统一查询面（与 51 号实验历史 Tab 联动）vs DB 表（远期，随 62 号 YAML→DB 迁移批）；排期=首个实盘决策快照积累 ≥100 条或 Owner 周复盘首例"无法回答为什么这笔交易"时裁定（§22.5 既定重评条件）。人机协作接口（对话式追问）维持 Phase 3+ 不排期（LLM 基建依赖）。

## A股市场结构变化（2026-07/08）

> **v1.6.0 新增（对应文档 v1.17.0）**：2026-07/08 A 股市场结构发生多项重要变化，影响策略施工约束。需在 24/25/26 号策略文档同步更新。

### A.1 A 股交易新规（2026-07-06 实施）

**核心变化**：
1. **盘后固定价格交易扩容**——从科创板/创业板扩展至**全部 A 股和沪深 ETF**（15:05-15:30）。影响：尾盘流动性结构已变，龙虎榜 2026 机构信号校准需同步更新（尾盘定价机制变化影响"尾盘抢筹"信号解读）
2. **主板 ST/*ST 涨跌幅放宽**——从 5% 放宽至 **10%**。影响：ST 股波动率结构变化（波动率上限翻倍），影响 ST 股策略的风险参数校准+VaR 估算
3. **上交所基金收盘竞价调整**——收盘连续竞价改为**集合竞价**。影响：ETF 策略尾盘执行需调整（集合竞价 vs 连续竞价的冲击成本模型不同）
4. **深交所创业板引入做市商**——影响：创业板流动性结构改善，但做市商行为可能引入新的微观结构模式

**施工约束影响**：
- **24 号打板策略**：尾盘执行逻辑需评估"盘后固定价格交易"对打板尾盘抢筹的影响（15:00 收盘后 15:05-15:30 的盘后交易可能分流尾盘流动性）
- **26 号龙虎榜策略**：2026 机构信号校准需更新（尾盘流动性结构已变，传统"尾盘抢筹=机构买入"假设需重新验证）
- **ST 股策略**：涨跌幅 5%→10% 后，ST 股波动率参数需重新校准（历史波动率数据含 5% 涨跌幅限制，需 regime 切换处理）

### A.2 微盘股策略失效机制（2026-07 深度复盘）

**核心机制**：科技股虹吸 → 微盘流动性枯竭 → 量化同质化多杀多 → 退市新规基本面恶化
- **科技股虹吸**：2026-07 科技板块（AI/算力/半导体）持续吸金，微盘股资金净流出
- **流动性枯竭**：微盘股日均成交额下降，买卖价差扩大
- **多杀多**：量化策略同质化（拥挤因子+相似仓位）→ 压力期同时平仓 → 多杀多加速下跌
- **退市新规基本面恶化**：微盘股 2026 Q1 归母净利同比 **-79.25%**，退市风险加剧

**施工约束影响**：
- **25 号多因子策略 build_tradability_mask**：需强化流动性门槛——① 提高日均成交额下限（微盘流动性枯竭使原阈值过低）；② 增加退市风险预警（基本面恶化+退市新规）；③ 监控因子拥挤度（同质化多杀多风险）
- **选股策略流动性过滤**：流动性过滤阈值需 regime 感知（压力期提高门槛，正常期维持）

### A.3 量化"双杀"压力测试（2026-07）

**核心数据**：沪深300 指增平均超额 **-1.51%**；中证500 指增 **-4.54%**；动量因子单月回撤超 **20 个百分点**（十年罕见）；因子拥挤（crowding）→ 同质化量化策略集中平仓 → 多杀多。

**施工约束影响**：
- **#2 因子工程**：需在因子监控模块增加拥挤度指标（详见 §2 量化"双杀"压力测试条目）
- **#6 回测门禁**：压力测试场景需纳入 2026-07 量化"双杀"episode 作极端 regime 回测
- **#4 风险模型**：动量因子单月回撤超 20pp 印证 4 级回撤 Protocol（8/15/20/25%）的 20% Level3 触发必要性

## 待定问题（v1.2.0 新增——需人决策的开放问题）

> 以下 5 项均源自十一轮审查（v1.2.0）过度工程纠偏——多轮审查累积的"加法"（Wasserstein 家族四件套+conformal 五变体栈+Robust HMM 七候选+RL 执行+过拟合检测三协议）已超出 MVP 最小可行边界，需人决策收敛选项。AI 不擅自发挥，标记如下供人裁定。

| # | 决策项 | 背景 | 最小可行 baseline | 候选项 | 方向（非裁定） |
|---|---|---|---|---|---|
| **P-1** | **Wasserstein 家族是否收敛** | v0.9.0-v1.1.0 累积形成 regime 层（W-HMM）+组合层（Certified DRO）+仓位层（W-Kelly）+生成式扩展（W-GAN）"四件套"，统一用 Wasserstein 距离作鲁棒性度量 | **regime 层 W-HMM 单独先上**（直接对应 12 号 A2 FAIL 修复），组合层+仓位层+生成式扩展列为 Phase 3+ 远期 | ① 全上四件套（统一度量但工程量大）② 只上 W-HMM（最小可行，其余 naive risk parity+参数化 Kelly+经验分布已足够 MVP）③ 不上（现有方案已足够，Wasserstein 是锦上添花） | **方向②**：W-HMM 先上（有 A2 FAIL 痛点驱动），其余 Phase 3+ 引入，避免一次性堆栈 |
| **P-2** | **Conformal 五变体栈是否收敛** | v0.4.0-v0.9.0 累积形成 slow unweighted → EWMA 标准化 → RWC regime 加权 → ACI → COP 五变体递进栈（91 号 Phase 0） | **slow unweighted + EWMA 标准化**（Conformal Kelly 实证最优 baseline + v0.8.0 修复 conditional coverage 8pp gap，共 ~60 行） | ① 全上五变体（最完备但维护复杂）② baseline+ACI（修复 post-break，A 股政策市 regime break 频繁场景必需，~80 行）③ baseline+RWC（复用 regime 检测器，压力期校准更好，~140 行）④ 只上 baseline（最简但 conditional coverage 未修复） | **方向②**：slow unweighted+EWMA+ACI 三层（Conformal Kelly"慢而稳"最优+EWMA 修复 conditional+ACI 修复 post-break），RWC/COP 作为压力期不达标时的升级 |
| **P-3** | **Robust HMM 候选选哪个** | v0.9.0-v1.2.0 累积 7 候选：Wasserstein HMM（标签漂移）+BR-iHMM（离群鲁棒）+Huber Robust HMM+Student-t HMM+GH HMM+Feature Saliency HMM+AH-HMM（egargale/hmm_test PRD #20 2026-05-29） | **Wasserstein HMM**（v0.9.0：Columbia 实证 Sharpe 2.18 vs SPX 1.18，直接对应 12 号 A2 FAIL 标签对齐失败，model-order selection+template tracking 双重解决） | ① Wasserstein HMM（标签漂移，轻量）② BR-iHMM（离群鲁棒+无限状态，67% 误差降低，但更重）③ Student-t HMM（肥尾鲁棒，最轻量但只解决 emission 不解决 label-switching）④ Huber Robust HMM（折中） | **方向①**：Wasserstein HMM 先上（直接解决 A2 FAIL），BR-iHMM 作离群点密集场景升级，其余列为对照评估 |
| **P-4** | **RL 执行是否实施** | v0.3.0 定执行算法四层谱系（TWAP/VWAP→AC→RL PPO/TD3→MAP-Elites），v1.2.0 补 Conformal-gated 执行（SOIC Vol.16 2026-08 U Hull）实证 conformal 门控成本方差 19.1→10.0bps 优于 PPO RL 执行（跨种子高方差不稳定），反向印证"慢而稳 conformal 胜过 RL"在执行域成立 | **TWAP/VWAP + 平方根冲击律成本估算**（v0.3.0 已定：个人 A 股散户默认用此层，足够） | ① 放弃 41 号阶段 7 执行 RL（Conformal-gated 实证更优+个人系统无 LOB 接入+资金量小+T+1 限制）② 保留 RL 执行作远期选项（资金量增长后可能需要）③ Conformal-gated 执行替代 RL 执行（中等复杂度，需 conformal 校准层） | **方向①**：放弃 41 号阶段 7 执行 RL（个人系统过度工程），保留 TWAP/VWAP 作 MVP 执行层，Conformal-gated 作远期升级选项 |
| **P-5** | **过拟合检测协议选哪个** | v1.2.0 补 3 项：AlgoXpert IS-WFA-OOS 协议（arxiv 2603.09219v1 2026-03-10，plateau 优先+purge gap+majority-pass/catastrophic-veto 门控）+plateau 启发式受控验证（Soloviov plateau.marketmaker.cc 2026，选择偏置有效 +0.12-0.31 OOS Sharpe 但独立检验弱）+PBO 零假设=0.5（marketmaker.cc 2026-07-01，PBO≈0.5=完全过拟合=抛硬币） | **现有 BM-BT-01~07 体系**（项目已裁定：#6 v0.2.0 标✅已裁定，Purged K-Fold+DSR/PSR 已含） | ① 现有体系+AlgoXpert IS-WFA-OOS（最严谨，plateau 优先+purge gap+双门控）② 现有体系+PBO 零假设=0.5（最简增量，仅改 PBO 零假设）③ 现有体系+plateau 启发式（选择偏置有效但独立检验弱，作辅助非主协议）④ 不改（现有 BM-BT-01~07 已足够） | **方向②**：现有体系+PBO 零假设=0.5 修正（最小增量，修正 PBO 零假设从 1 改为 0.5 即可，AlgoXpert/plateau 列为 Phase 2+ 升级） |

> **v2.0.0 更新（A2 PASS 后续航重估）**：① **P-1/P-3 紧迫性下调**——A2 已 PASS（OOS/IS=1.042，详见 §7 更正），P-1 原方向②的"A2 FAIL 痛点驱动"理由已消失——若用户确认 P-1，改为"W-HMM 与 BR-iHMM 均列 Phase 3+ 远期对照评估，MVP 维持 4 态 HMM+3 overlay 不动"；② **P-5 修订**——v1.7.0 Soloviov 实证 PSR AUC 0.808 > DSR 0.785 > PBO 0.669，方向②修正为"现有体系 + PSR 主诊断 + DSR 补充 + PBO 零假设=0.5 修正"；③ P-2/P-4 维持原方向（方向② slow unweighted+EWMA+ACI / 方向① 放弃 RL 执行）。**五项仍全部待用户裁定**。
>
> **收敛原则**：MVP 阶段优先选择"最小可行 baseline"列方案，候选项列为 Phase 2+/3+ 引入。多轮审查累积的"加法"需通过人决策收敛为"减法"——保留有痛点驱动的，暂缓锦上添花的（Wasserstein 组合/仓位层、COP、RL 执行、AlgoXpert 协议）。【v2.0.0 注：W-HMM 的 A2 痛点已随 A2 PASS 消失，收敛原则相应更新】

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.1~0.1.2 | 文件名 discussion_020_methodology_open_questions.md → 90_methodology_open_questions.md（段位编号制）；文档头统一：title/H1 去"讨论稿："前缀，scope 归一为 07_trading_decision_architecture；章节编号与正文零变更 | 文档体系重排+15 篇有内容文档结构统一，规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-10 | 0.2.0 | 首轮逐项审查 21 提案与项目现状对齐：① #3/#4/#6/#11 标✅已裁定（30_multi_strategy v1.3.3 替代方案+映射）；② #7 纠正"8态已被12态替代"不准确（8态 BM-SEL-04 是独立下游消费者未建，8态→直接决策映射过时），补 regime spec 12态 vs 实际 4态+3overlay=7维差异；③ #9 更正 Layer2 "8态预测"引用为 regime 检测；④ #3/#6 补 2026 行业实证（risk parity/Purged K-Fold/DSR） | 架构审查：与 30/10/11 号文档+已施工代码对齐 |
| 2026-08-10 | 0.3.0~0.9.0 | 二~七轮审查补施工算法缺口+选项外更优算法（逐项明细见正文各节"2026 补充论据"）：#1 打板环境剧变（溢价 4.2%→1.7%/炸板率 40%→68%/程序化新规）+akshare 连板筛选+6 维度涨停规律+开源工具生态；#2 SHAP/MinShap+GP/EAFD+PPO 自适应加权+三层框架+CGX；#3 HRP；#5 平方根冲击律+AC 分解；#7 预测天花板 52-53%；#8 Amihud+LVaR+Kyle λ；#11 Kelly 分数实证+Conformal Kelly+Bayesian/RMSE 轻量校准；#13 Barra 归因+Smart Beta；#14 财报双日期+重述泄漏+Observation Spine；#15 流通市值 6 级分层；#16 五层评估框架；#17 PaC/OPA；#18 IM 15 字段+ST PIT；#19 执行四层谱系；#20 DTW+退役决策树+5 预警+Alpha Decay 模型+Layering+EvoQuant+90 天相关剔除；#21 正T/反T+日内三层栈 | 多轮审查记录合并（v2.0.2 压缩）：保留算法名称与关键数据，折叠调研过程叙述 |
| 2026-08-10 | 1.0.0~1.5.1 | 八~十四轮审查：Wasserstein 家族成形（#7 W-HMM 对应 A2 FAIL+#3 Certified DRO+Shift-Aware δ 校准+W-Kelly+W-GAN 生成式）；#1 Tail-Aware MDN（skewed t 原生匹配打板）+Lévy 家族交叉引用；#7 BR-iHMM+Robust HMM 谱系；#3 MFCCA+TRP；#2 F²Agent/市场依赖通信/MarketSenseAI+Cross-Sectional LSTM；#4 Landolfi 非高斯回撤查找表；#18 CAI++；#1/#2 涨跌停 upstream contamination（IC 虚高 18%）；#6 AlgoXpert 协议+plateau 验证+PBO 零假设=0.5；#19 Conformal-gated 执行 vs RL；#20 AlphaCrafter revalidate；91 号同步 RWC/Info-Entropic/Exformer（规划态）；v1.2.0 起过度工程纠偏+新增待定问题 P-1~P-5 | 多轮审查记录合并（v2.0.2 压缩） |
| 2026-08-10 | 1.6.0 | 十五轮审查+2026-07/08 市场结构变化登记：C-WRP（LP 化+certified bound 视角）+RRP（中国 2012-2024 实证）+VRMD（已评估不整合，precision 上限 25% 反面支持 4 态 HMM）+FCVE+A-CRaQL（已评估不整合）+量化"双杀"实证+Johnson S_U（部分采纳）+MINGLE（不采纳，Phase 5+ 条件）；新增「A股市场结构变化」节（交易新规/微盘失效/双杀），需 24/25/26 号同步施工约束 | 市场结构变化影响施工约束需登记 |
| 2026-08-10 | 1.7.0~1.18.1 | 十六~七十四轮审查持续评估选项外算法（对照已集成清单去重）：部分采纳 ARM 变点归因/PSR>DSR>PBO 排序（更新 P-5）/Systemic Fragility Index/簿册单边性/Student-t ν/SAM（数据依赖条件性）/华泰三级 EWS/QLoRA 情感负结果背书/Markov GoF/CVaR Q-Learning 训练流程/AlphaSchema/FINSABER/LETF 操纵监控/Body-Tail/Spatial-Sign/Sharp Tail Bounds/Bayesian GP/RWC/Uncertainty-Adjusted Sorting/财信情绪浓度/IGF/tick size 判据/分布漂移标度律/TIPS/SciPhy/HRT/Finance-Grounded 损失/Strat-LLM/稀疏衰减+RMT；不采纳项均记 Phase 5+ 或理论参考（含 ReCAP/VD-MEAC 作 HRT 增量）。结论：高价值算法已基本整合完毕，价值增长点转向代码施工 | 多轮审查记录合并（v2.0.2 压缩） |
| 2026-08-12 | 2.0.0 | 架构审查终审全量裁定（draft→active）：21 项全部裁定——维持 4 项（#3/#4/#6/#11 锚点更新 v2.5.0）+新裁定 12 项+合并 1 项（#12 并入 #16）+暂缓/远期 2 项（#7/#10）+P-1~P-5 待用户裁定。新增「已施工设施盘点」节（8 已施工/8 部分/5 未施工，12 注册表 6/12 已建）。6 处口径修复（MOD-POS-001→021/印花税千1→万5/BM-BT-07 三方口径/BT-10 已 production/30号锚点 v2.5.0/91号引用标注规划态）。A2 已 PASS 更正（W-HMM 降 Phase 3+）。讨论优先级表转施工优先级表 | 全量架构审查：基础设施盘点+第一性原理逐项裁定+2026-08 调研+system_charter §2 硬边界适配+交叉文档口径对账 |
| 2026-08-12 | 2.0.1 | 作战地图全覆盖补丁——新增 §22 作战地图选股层补充环节 5 条开放问题（BM-SEL-05-D 主力行为推演/BM-SEL-05-E 庄家识别/BM-SEL-06 跨市场传导/BM-SEL-10 行情生命周期/BM-SEL-26 决策可解释性，均 design 态、登记远期/Phase 2 候选、MVP 不建，各含定位→裁定理由+重评条件→契约/参数→边界消歧四层） | 作战地图 stock_selection design 态环节登记 |
| 2026-08-14 | 2.0.2 | 压缩精简：噪音去除，提案本体全保留（AI-DOCS-001） | 21 项提案的命题/核心论据（结构化表格+关键数据）/触发条件/重评条件/当前状态逐项保留；折叠各版本调研过程叙述、冗长背景与对标散文（结构化对标表格保留）；修订记录中间版本按区间合并 |
| 2026-08-15 | 2.0.3 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-10） | 格式噪音清理（论据节"各版本登记/关键数据保留"meta 标签）；头部 v2.0.0 更正单段散文要点化、裁定分布改指总览表；跨节重复数据改真源+指针（量化双杀→附录 A.3、A2 PASS→§7）；21 项提案命题/触发/重评/裁定/链接零丢失 |
