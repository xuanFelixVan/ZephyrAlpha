---
ttl: permanent
doc_type: architecture_view
title: 24路并发AI审查回填指令集
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: ai_review_instructions
scope: 07_trading_decision_architecture
---

# 24 路并发 AI 审查回填指令集

> **用途**：本文档包含 24 个 AI 的完整指令，每个指令可一键复制到新 AI 对话中独立执行。
> **任务**：对 `07_trading_decision_architecture/design_memos/` 下 42 篇文档进行回填、审查、扩展、更新、过度工程清理。
> **创建日期**：2026-08-10
> **使用方式**：复制对应 AI 编号的指令块 → 开新对话 → 粘贴 → 执行

---

## 0. 通用规则（所有 AI 必须遵守，已内嵌在每个指令块中）

1. **三层分治**：design_memo 只写 why（决策推理），不写 what is 的细节（当前状态由 battle_map + depgraph 维护），引用用稳定 path/blueprint_id（禁止 node_id/edge_id）
2. **文档规范**：遵循 `01_design_memo_management_spec §4`——frontmatter 字段集（ttl/doc_type/title/owner/language/status/version/date/topic/scope）、末尾必须有「修订记录」节、必须有「开放问题/待定问题/待裁定」等价节
3. **不破坏交叉引用**：含 `#L行号` 锚点的引用不得断裂；章节编号不强制统一；不为"结构统一"重排已有章节
4. **修订升版本**：改动后升 version（小改 1.x.0→1.x.1，大改→1.(x+1).0），修订记录补一行（日期+版本+改了什么+为什么改）
5. **过度工程红线**：本项目是个人+100%AI 开发，凡是"需要多人协作才能用""为了团队协作而设计""需要外部对接/文档交付"的机制一律砍掉或降级为远期愿景；远期愿景（标注 P4/P5/待裁定）可保留
6. **搜索约束**：WebSearch 限定 2026 年（尤其 2026-07/08），找最新研究/实践/开源实证；找到的更好算法登记到文档「考虑过的替代方案」或新增「前沿演进方向」节，不直接替换已定决策（已定决策修订需升版本+记理由）
7. **循环审查**：每轮做完整闭环（回填→审查→搜索→调整→过度工程清理），做完不停，重新通读全文再查一轮，直到连续 1 轮零改动需求 = 任务完成
8. **不擅自定决策**：需人决策的开放问题标在「待定问题」节，AI 不替人拍板；已 active 的定稿决策如要推翻，必须升大版本+写推翻理由+标「待裁定」

---

## 1. 24 个 AI 文档分配总表

| AI | 文档数 | 负责文档 |
|---|---|---|
| AI-01 | 1 | 00_index_trading_decision.md（总索引，全局视角） |
| AI-02 | 2 | 01_design_memo_management_spec.md + 15_data_feature_layer_spec.md |
| AI-03 | 1 | 10_regime_detector_spec.md（184KB 超大 active） |
| AI-04 | 2 | 11_regime_backtest_validation_plan.md + 12_regime_phase2_validation.md |
| AI-05 | 2 | 13_regime_phase3_engineering_plan.md + 14_regime_s2_diagnosis.md |
| AI-06 | 2 | 20_first_batch_strategies.md + 21_stock_selection_engine.md |
| AI-07 | 2 | 22_sector_rotation_spec.md + 23_strategy_correlation_validation.md |
| AI-08 | 2 | 24_daban_strategy_detail.md + 25_multifactor_strategy_detail.md |
| AI-09 | 2 | 26_event_driven_strategy_detail.md + 27_second_batch_strategies.md |
| AI-10 | 2 | 28_sentiment_cycle_trading.md + 30_multi_strategy_concurrency.md |
| AI-11 | 2 | 31_position_sizing.md + 32_firm_risk_aggregator.md |
| AI-12 | 2 | 33_budget_change_handler.md + 34_regime_meta_allocator.md |
| AI-13 | 2 | 35_drawdown_protocol_impl.md + 36_var_es_monitoring.md |
| AI-14 | 2 | 37_liquidity_crisis_protocol.md + 40_execution_broker.md |
| AI-15 | 2 | 41_buy_flow.md + 42_sell_flow.md |
| AI-16 | 2 | 50_backtest_observability_workplan.md + 51_panel_experiment_history_mlflow_retirement.md |
| AI-17 | 2 | 52_backtest_framework_docking.md + 53_simulation_live_path.md |
| AI-18 | 2 | 54_reconciliation_attribution.md + 55_monitoring_review.md |
| AI-19 | 2 | 60_cross_cutting_cleanup.md + 61_lifecycle_multi_ai.md |
| AI-20 | 2 | 90_methodology_open_questions.md + 91_density_prediction.md |
| AI-21 | 1 | 62_business_registry_construction.md（业务资产注册表施工总案） |
| AI-22 | 1 | 63_data_utilization_audit.md（业务数据资产利用率审查） |
| AI-23 | 1 | 19_northbound_hold_snapshot.md（北向资金季度持仓快照 fetcher 施工计划） |
| AI-24 | 1 | 17_special_trading_days_data_assets.md（A股特殊交易日数据资产全景与治理） |

> 合计 6 个 AI 各 1 篇 + 18 个 AI 各 2 篇 = 42 篇，24 个 AI，全覆盖。

---

## AI-01 指令（负责 00_index_trading_decision.md）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】审查并更新 1 篇文档：d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\00_index_trading_decision.md

【文档性质】这是 07_trading_decision_architecture 域的总索引+路线图（G01-G28 主题组），active v2.4.0。它不是骨架，是已定稿的导航文档。

【工作清单】
1. 读现状：读 00_index 全文 + 读 01_design_memo_management_spec §2/§4（三层分治与文档规范）+ 列出 design_memos 目录全部 38 篇的当前 frontmatter status/version（用 LS + Grep frontmatter）
2. 一致性审查：
   - §0 目录表的 38 篇状态是否与各文档 frontmatter 实际 status/version 一致
   - §3 主题组 G01-G28 的"状态"列是否与对应文档实际状态一致
   - §7.3 占用表的认领状态是否最新
   - §9 开放问题汇总的"决策状态"是否与各文档实际一致
   - §10 改名对照表是否有遗漏
3. 完整性审查：
   - G01-G28 主题组是否覆盖赚钱全流程所有环节（研究孵化→模型训练→回测→模拟→选股→买入→卖出→仓位→风控→执行→对账→跨切）
   - 对照 battle_map_01~12 的 12 个阶段，是否每个阶段都有对应 G 主题组
   - 对照 src/zephyr/ 下已施工的 domain（用 LS src/zephyr），是否有关键已施工模块没被任何 G 主题组覆盖
4. 全网搜索：WebSearch 限定 2026 年，搜"quantitative trading system architecture 2026""multi-strategy portfolio framework 2026""algorithmic trading decision pipeline 2026"，看是否有更优的主题组划分范式
5. 过度工程审查：§5 的 3 条并行轨道、§7 多 AI 分工指南是否对个人项目过重（如多 AI 协作流程是否需要简化）
6. 结构调整：§0-§11 的顺序/内容是否需要调整；§4 依赖关系图是否准确反映当前依赖
7. 循环：改完一轮后重新通读全文，再查一轮，直到连续 1 轮零改动

【约束】
- 这是索引文档，不写施工算法细节，只维护导航准确性
- 改动升 version（v2.4.0→v2.5.0 小改 / v3.0.0 大改），修订记录补一行
- 不破坏 38 篇文档的交叉引用链接
- 不擅自新增/删除 G 主题组（需人决策的标在 §9 开放问题）
- 持续改进，不要停下来询问，直到零问题
```

---

## AI-02 指令（负责 01_spec + 15_data_feature）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT，T+1，不能做空）。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\01_design_memo_management_spec.md（管理规范，active v1.2.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\15_data_feature_layer_spec.md（G01 数据与特征层规范，骨架 draft 0.1.0，需大量回填）

【文档1：01_spec 工作清单】
- 读全文，审查 §1-§7 是否与 38 篇文档实际现状一致（命名规则/段位编号/status 枚举/防飘移机制）
- 审查 §4.4 文档种类适配是否覆盖所有实际文档种类
- 全网搜索 2026 年"architecture decision record alternative 2026""design memo vs ADR 2026"，看规范本身是否需迭代
- 过度工程审查：§2.2 三层协作流程、§5.3 修订规则是否对个人项目过重
- 循环审查至零问题

【文档2：15_data_feature 工作清单——重点回填】
- 这是骨架，§2-§6 全空，需要回填项目已施工的数据/因子基础设施 why
- 读项目代码：
  - LS d:\ZephyrAlpha\src\zephyr\ 找 data/factor/feature/mkt_data 相关子包
  - 读 d:\ZephyrAlpha\docs\02_enterprise_architecture\02_domain_architecture_docs\11_d_data.md（D_DATA 域 194 模块）+ 12_d_data_eng.md + 23_d_mkt_data.md + 46_d_factor.md（D_FACTOR 109 模块）了解已施工模块清单
  - 读 d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\battle_map\battle_map_01_research_incubation.md + battle_map_02_model_training.md 了解数据/因子阶段现状
- 回填讨论要点（§7 的 6 项）：
  ① ClickHouse schema 规范——查 src/zephyr 下 clickhouse schema 定义，回填实际 schema 设计 why
  ② miniQMT tick 接入契约——查 miniQMT 接入代码，回填实际契约
  ③ PIT 铁律——查 AS OF JOIN/Embargo 实现，回填实际方案
  ④ 特征仓库架构——查特征计算/缓存/版本实现，回填
  ⑤ 因子工程总纲——查因子库/IC 评估/衰减监控/过拟合监控实现（BM-SEL-02），回填
  ⑥ 数据质量门控——查数据质量检查实现，回填
- 把骨架填成 active：补 §1 背景、§2 决策、§3 替代方案、§4 上限、§5 待裁定、§6 待定问题、§7 引用、§8 修订记录
- 全网搜索 2026 年"feature store architecture 2026""factor IC evaluation 2026""point-in-time database 2026""alpha factory 2026"，找更好算法
- 过度工程审查：特征仓库/因子工程是否对个人项目过重（如是否需要完整 Feature Store，还是轻量缓存即可）
- 循环审查至零问题

【约束】
- 遵循 01_spec 自身的规范（frontmatter/修订记录/开放问题节）
- 15 号从 draft 0.1.0 → active 1.0.0（填满后），修订记录记"骨架填空+回填已施工算法"
- 不破坏交叉引用，引用代码用稳定 path
- 持续改进不停，循环至零问题
```

---

## AI-03 指令（负责 10_regime_detector_spec）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 1 篇文档（超大 active 文档）：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\10_regime_detector_spec.md（regime 检测器 spec，active v1.3.1，184KB）

【文档性质】这是已定稿的 regime 检测器 spec，12 态定稿，代码已施工。文档很大（184KB，超 Read 128KB 限制，需用 offset/limit 分段读，或用 Grep 定位章节）。

【工作清单】
1. 读现状：用 Read offset/limit 分段读全文（每段 1500 行），或用 Grep 定位 H2 章节逐段读；同时读 src/zephyr/regime/ 下全部代码（LS src/zephyr/regime + 读 core/regime_detector.py / features/ / validation/）
2. 回填：把 src/zephyr/regime/ 已施工的算法（HMM 9态/12态、Shrinkage、overlay signals、synthetic VIX、walk-forward refit、Phase2 四验证器等）的 why 回填到文档（如已记录则审查完整性）
3. 审查缺失：12 态转换路径/触发确认信号/置信度更新规则/主线识别是否完整；对照 12_regime_phase2_validation 的 A2/B1 FAIL 结果，文档是否已反映"模型需重设计"的后续
4. 全网搜索 2026 年"regime detection HMM 2026""market state detection 2026""Gaussian HMM financial 2026""regime switching model 2026"，找更好算法（如非参数化/深度学习 regime）
5. 过度工程审查：12 态是否过多（个人系统）；overlay signals 的 NLP/资金/板块维度是否过度（P2 待施工的是否应降级）
6. 结构调整：184KB 是否应拆分（如验证部分拆到 11/12 号）；章节顺序是否合理
7. 循环审查至零问题

【约束】
- active 文档改动升版本（v1.3.1→v1.4.0），重大决策修订需标待裁定
- 不破坏与 11/12/13/14 号文档的交叉引用
- 读取大文件用 offset/limit，不要一次性读
- 持续改进不停，循环至零问题
```

---

## AI-04 指令（负责 11_regime_backtest + 12_phase2_validation）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\11_regime_backtest_validation_plan.md（regime 回测验证方案，active）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\12_regime_phase2_validation.md（Phase 2 模型质量验证，active v0.2.2）

【工作清单——文档1：11号】
- 读全文 + 读 src/zephyr/regime/validation/（LS + 读 c1_comparator/c1_runner/phase2_runner）
- 回填：Phase 1-5 验证方案的已执行结果（C1 已通过 commit 852457e9、Phase 2 已执行见 12 号）回填到 11 号的验收指南
- 审查：Phase 1-5 各阶段验收标准是否完整；C1 Shrinkage 有效性已证，文档是否同步
- 全网搜索 2026 年"regime backtest validation 2026""walk-forward validation 2026""deflated sharpe ratio 2026"
- 过度工程审查：5 个 Phase 是否对个人项目过多
- 循环至零问题

【工作清单——文档2：12号】
- 读全文（12 号已有第一批/第二批执行结果，含 A1/A2/B1/B4 真实数据）+ 读 src/zephyr/regime/validation/phase2/（a1/a2/b1/b4 四验证器代码）
- 回填：把四验证器的实际算法/代码实现 why 补全（如 A2 标签对齐 Hungarian、B1 后续收益代理标签的 12 态映射）
- 审查：A2 FAIL（OOS/IS=0.340）+ B1 FAIL（误差27.6%）的后续修复是否已落盘；§9.4/§10.4 的下一步优先级是否已执行
- 全网搜索 2026 年"HMM overfitting detection 2026""probability calibration 2026""Viterbi label alignment 2026""reliability diagram 2026"
- 过度工程审查：四验证器是否对个人项目过重
- 循环至零问题

【约束】
- active 文档改动升版本，修订记录补行
- 不破坏与 10/13/14 号的交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-05 指令（负责 13_phase3 + 14_s2_diagnosis）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\13_regime_phase3_engineering_plan.md（Phase 3 工程规划，draft）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\14_regime_s2_diagnosis.md（S2 算法错配诊断报告，draft）

【工作清单——文档1：13号】
- 读全文 + 读 src/zephyr/regime/（降态/校准/NLP/S2/T3 相关代码）
- 回填：Phase 3 的降态（9→6）、校准器、NLP 管道、S2/T3 触发逻辑的已施工部分回填 why
- 审查：§2.1 降维裁定、§2.2 校准器设计是否完整；与 12 号 A2/B1 FAIL 的修复方案是否对齐
- 全网搜索 2026 年"HMM state reduction 2026""probability calibration isotonic 2026""NLP financial sentiment 2026"
- 过度工程审查：NLP 管道/资金板块数据管道是否对个人项目过重（是否应降级远期）
- 从 draft → active（如已施工完整）或保持 draft 补全
- 循环至零问题

【工作清单——文档2：14号】
- 读全文 + 读 src/zephyr/regime/（S2 trigger 逻辑、overlay_signals_builder、bad_news_flat/policy stub）
- 回填：S2 算法错配的根因诊断（thresholds 过高/NLP stub=0/合成 VIX 缺失）+ 修复方案（已修合成 VIX commit eb3db21bd8 + S1 门槛 commit 981d59d8cc）回填
- 审查：诊断报告的因果时间线是否完整；S2 仍 0/3 的后续是否登记
- 全网搜索 2026 年"crisis recovery detection 2026""market bottom identification 2026""capitulation signal 2026"
- 过度工程审查：S2 的多维度触发是否过重
- 循环至零问题

【约束】
- draft→active 升版本，修订记录补行
- 不破坏与 10/11/12 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-06 指令（负责 20_first_batch + 21_stock_selection）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT，T+1，不能做空）。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\20_first_batch_strategies.md（首批3策略定义，active v1.2.4）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\21_stock_selection_engine.md（G05 选股引擎架构，骨架 draft 0.1.0）

【工作清单——文档1：20号】
- 读全文 + 读 src/zephyr/pf_core/strategies/ + battle_map_05_stock_selection.md（BM-SEL-22~27 打板链/因子工厂/事件处理）
- 回填：3 策略（打板/多因子/事件驱动）已施工的 alpha 信号链 why 补全（打板链 BM-SEL-22~25、因子工厂 BM-SEL-02、事件处理 BM-SEL-27 的代码实现回填）
- 审查：§2.5 差异化矩阵、§2.6 选股池交集、§4.4 灰度指引是否完整；§5 待裁定 4 项是否已落地
- 全网搜索 2026 年"multi-strategy alpha 2026""daban limit-up strategy 2026""event-driven trading 2026""factor investing 2026"
- 过度工程审查：§4.4 intake 四阶段是否对个人项目过重
- 循环至零问题

【工作清单——文档2：21号——重点回填】
- 骨架，§2-§6 全空，需回填选股引擎已施工部分
- 读 src/zephyr/（LS 找 selection/stock_selection/ashare_signal 相关）+ battle_map_05（BM-SEL-25 双引擎融合、L0→L1→L2-C 分层、量化强度评级）
- 回填讨论要点（§7 的 6 项）：双引擎融合定位、L0→L1→L2-C 分层、量化强度评级、选股 pipeline 标准接口、候选池生成→过滤→排序→输出、与 StrategyBook 对接契约
- 填成 active：补 §1-§8
- 全网搜索 2026 年"stock selection engine 2026""alpha factory layered 2026""quant signal pipeline 2026"
- 过度工程审查：L0→L1→L2-C 三层是否过重
- 循环至零问题

【约束】
- 20 号 active 改动升版本；21 号 draft→active 1.0.0
- 不破坏与 30/24/25/26 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-07 指令（负责 22_sector_rotation + 23_correlation）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\22_sector_rotation_spec.md（G06 板块轮动 spec，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\23_strategy_correlation_validation.md（G07 策略间相关性验证，骨架 0.1.0）

【工作清单——文档1：22号——回填】
- 读 battle_map_05（BM-SEL-08 板块强度 460 板块 880xxx K线、BM-SEL-09 调整周期追踪）+ src/zephyr/（LS 找 sector/rotation/plate 相关）
- 回填讨论要点 7 项：板块强度算法、回踩质量 A/B/C、调整周期追踪、轮动序列、虹吸态、板块资金流、板块→个股传导
- 填成 active
- 全网搜索 2026 年"sector rotation strategy 2026""industry momentum 2026""A-share sector 2026"
- 过度工程审查：460 板块全覆盖是否过重
- 循环至零问题

【工作清单——文档2：23号——回填】
- 读 20_first_batch_strategies §2.5 差异化矩阵（已定）+ src/zephyr/（找 correlation/相关性验证代码，可能未施工）
- 回填讨论要点 5 项：5 候选两两相关矩阵、按情绪周期分层、>0.6 重新审视、验证数据区间、验证报告模板
- 若代码未施工，则填 why 决策（用什么方法：block-bootstrap/pearson/spearman/按情绪周期分层）+ 标"待施工"
- 填成 active 或保持 draft（如纯待施工）
- 全网搜索 2026 年"strategy correlation block bootstrap 2026""multi-strategy decorrelation 2026"
- 过度工程审查：block-bootstrap 2000x 是否过重
- 循环至零问题

【约束】
- 骨架→active 升版本 1.0.0
- 不破坏与 20/30 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-08 指令（负责 24_daban + 25_multifactor）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\24_daban_strategy_detail.md（G08 打板策略细节，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\25_multifactor_strategy_detail.md（G09 多因子策略细节，骨架 0.1.0）

【工作清单——文档1：24号——回填打板】
- 读 battle_map_05（BM-SEL-22 短线评分卡7维、BM-SEL-23 游资接力6因子+情绪周期4+1、BM-SEL-24 量化强度6维、BM-SEL-25 双引擎融合6类决策）+ src/zephyr/（LS 找 daban/limit_up/board_ladder/ashare_signal 相关）
- 回填讨论要点 7 项：连板梯队识别、情绪周期定位器、主升龙头识别、打板容量极小、双引擎融合内部、打板专用风控、T+1 时序
- 填成 active
- 全网搜索 2026 年"limit-up board strategy China 2026""游资打板 2026""consecutive limit-up 2026""dragon list 2026"
- 过度工程审查：7 维评分卡+6 因子+6 维强度是否维度过多
- 循环至零问题

【工作清单——文档2：25号——回填多因子】
- 读 battle_map_05（BM-SEL-02 因子计算/注册表/IC-IR/衰减/合成/治理）+ src/zephyr/factor/（LS + 读 core/factor_dag/dag.py 等）+ 02_domain_architecture_docs/46_d_factor.md（D_FACTOR 109 模块）
- 回填讨论要点 6 项：因子组合方式（打分/IC加权/正交化）、行业中性化、因子衰减监控、多因子换手率、多因子容量、与打板相关性
- 填成 active
- 全网搜索 2026 年"multi-factor model 2026""factor combination IC weighting 2026""factor decay monitoring 2026""industry neutralization 2026"
- 过度工程审查：因子治理生命周期是否过重
- 循环至零问题

【约束】
- 骨架→active 1.0.0
- 不破坏与 20/30 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-09 指令（负责 26_event_driven + 27_second_batch）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\26_event_driven_strategy_detail.md（G10 事件驱动策略细节，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\27_second_batch_strategies.md（G11 第二批次策略，骨架 0.1.0，暂缓）

【工作清单——文档1：26号——回填事件驱动】
- 读 battle_map_05（BM-SEL-27 盘中实时事件处理）+ src/zephyr/（LS 找 event/news/sentiment/announcement 相关）+ 02_domain_architecture_docs/09_d_alt_data.md（另类数据）
- 回填讨论要点 6 项：事件源（公告/新闻/龙虎榜/异动）、事件分类、事件冲击衰减曲线、事件→选股映射、事件换手率、news_data 多源情绪
- 填成 active
- 全网搜索 2026 年"event-driven trading 2026""news sentiment alpha 2026""event impact decay 2026""Hawkes process finance 2026"（20号已引 Janus-Q/Yukka/Hawkes，看是否有更新）
- 过度工程审查：多源 news_data 接入是否过重
- 循环至零问题

【工作清单——文档2：27号——暂缓文档】
- 读 20_first_batch §4.2 演进路径（第三阶段上加第4/5策略）+ 30_multi_strategy §1.1
- 本文档是暂缓骨架（首批 track record 后再讨论），不需要填满，但审查：
  - 暂缓理由是否充分
  - 价值反转/动量趋势的 alpha 信号预研方向是否登记
  - 与首批 3 策略相关性的预判
- 全网搜索 2026 年"value reversal strategy 2026""momentum trend following 2026""Fama French 2026"
- 过度工程审查：暂缓文档是否应精简
- 循环至零问题

【约束】
- 26 号骨架→active 1.0.0；27 号保持 draft 但补全暂缓说明
- 不破坏与 20/30 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-10 指令（负责 28_sentiment + 30_multi_strategy）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\28_sentiment_cycle_trading.md（G21 情绪周期×交易决策，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\30_multi_strategy_concurrency.md（多策略并发架构总纲，active v1.3.3）

【工作清单——文档1：28号——回填情绪周期】
- 读 battle_map_05（BM-SEL-23-B 情绪周期4+1阶段：冰点/反核/主升/疯狂/退潮）+ src/zephyr/（LS 找 sentiment/cycle/emotion 相关）+ 10_regime_detector_spec（regime 12 态含情绪维度，分工边界）
- 回填讨论要点 5 项：5 阶段买卖纪律、情绪周期定位器准确率评估、情绪周期与 regime 12 态映射、各策略不同情绪阶段部署、情绪周期作为隐形驱动
- 重点：明确情绪周期（sleeve 内 alpha 择时）vs regime（市场级风险节流）的分工边界
- 填成 active
- 全网搜索 2026 年"market sentiment cycle 2026""游资情绪周期 2026""limit-up sentiment 2026""emotion cycle trading 2026"
- 过度工程审查：4+1 阶段是否过细
- 循环至零问题

【工作清单——文档2：30号——active 总纲审查】
- 读全文 + 读 src/zephyr/pf_core/ + pf_alloc/ + position/（StrategyBook/FirmRiskAggregator/RegimeMetaAllocator/BudgetChangeHandler 已登记模块）
- 回填：§2.2 三模块、§2.4 三级升级、§2.5 回撤 Protocol 的已施工部分 why 补全
- 审查：§4.3 pod 误标是否已修正（20号 §5 待裁定-2 指出误标）；§5 待裁定 6 项是否需更新；§7.4 开源实证（Morwane 等）是否需补充 2026 新实证
- 全网搜索 2026 年"multi-strategy portfolio 2026""independent book aggregation 2026""risk parity throttle 2026""pod vs unified framework 2026"
- 过度工程审查：§2.5.4 VaR/ES、§2.5.5 Kill Switch 是否对个人项目过重
- 循环至零问题

【约束】
- 28 号骨架→active 1.0.0；30 号 active 改动升版本 v1.3.3→v1.4.0+
- 不破坏与 20/31/32/33/34 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-11 指令（负责 31_position + 32_firm_risk）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\31_position_sizing.md（G12 仓位算法 spec，active v1.2.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\32_firm_risk_aggregator.md（G13 FirmRiskAggregator 逻辑，骨架 0.1.0）

【工作清单——文档1：31号——active 审查】
- 读全文 + 读 src/zephyr/position/core/position_sizing_engine.py + 02_domain_architecture_docs/64_d_position.md（D_POSITION 28 模块）
- 回填：分层裁定（策略层粗仓位 risk parity + firm 层 Kelly 精裁决）的已施工算法 why 补全
- 审查：Kelly 参数估计来源、risk parity inverse-vol 公式、单票 8% 硬上限、现金管理是否完整
- 全网搜索 2026 年"position sizing Kelly 2026""risk parity inverse vol 2026""Kelly criterion practical 2026"
- 过度工程审查：Kelly 精裁决是否对个人项目过重（密度预测需求）
- 循环至零问题

【工作清单——文档2：32号——回填 FirmRiskAggregator】
- 读 30_multi_strategy §2.2/§2.3/§3.1 + src/zephyr/position/core/firm_risk_aggregator.py（MOD-POS-021）+ battle_map_08_position_management.md
- 回填讨论要点 7 项：按标的求和（自然叠加）、单票硬上限裁剪、行业/总仓位硬约束、冲突标的处理、不做 MVO、输出 firm_target_portfolio 契约、O(N) 复杂度
- 填成 active
- 全网搜索 2026 年"firm risk aggregator 2026""portfolio hard limit 2026""position aggregation 2026"
- 过度工程审查：行业/总仓位硬约束是否过重
- 循环至零问题

【约束】
- 31 号 active 升版本；32 号骨架→active 1.0.0
- 不破坏与 30/33 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-12 指令（负责 33_budget + 34_regime_meta）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\33_budget_change_handler.md（G14 BudgetChangeHandler 三级升级，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\34_regime_meta_allocator.md（G15 RegimeMetaAllocator 参数，骨架 0.1.0，⚠️等 C1）

【工作清单——文档1：33号——回填三级升级】
- 读 30_multi_strategy §2.4（三级升级 Tier1/2/3）+ src/zephyr/position/core/budget_change_handler.py（MOD-POS-022）+ battle_map_08
- 回填讨论要点 6 项：Tier1 封锁新仓、Tier2 rebalance_to_budget、Tier3 按比例强裁、convergence_window 差异化、rebalance 接口契约、每级 log/复盘
- 填成 active
- 全网搜索 2026 年"budget rebalance protocol 2026""position de-risking 2026""multi-strategy capital reallocation 2026"
- 过度工程审查：三级升级是否过重（个人系统是否需 Tier2 策略自主）
- 循环至零问题

【工作清单——文档2：34号——回填 RegimeMetaAllocator】
- 读 30_multi_strategy §2.2（分配公式 Base×Performance×Shrinkage）+ src/zephyr/pf_alloc/core/regime_meta_allocator.py（MOD-PA-007）+ 11_regime_backtest C1 验证结果（已通过）
- ⚠️ 本文档前置门槛：参数须等 C1 验证通过 + 首批策略 PnL。C1 已通过（commit 852457e9），但策略 PnL 未有。回填框架 why，参数标"待策略 track record 后校准"
- 回填讨论要点 7 项：分配公式、Base 先验、PerformanceScore 60日 Sharpe 映射、Shrinkage 四档、floor/cap、稀有态差异化、第二阶段时机
- 保持 draft（参数未校准）或填框架→active 标参数待定
- 全网搜索 2026 年"regime meta allocation 2026""performance score shrinkage 2026""dynamic capital allocation 2026"
- 过度工程审查：四档 Shrinkage 是否过细
- 循环至零问题

【约束】
- 33 号骨架→active 1.0.0；34 号保持 draft 或 active（参数待定）
- 不破坏与 30/31/32 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-13 指令（负责 35_drawdown + 36_var_es）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\35_drawdown_protocol_impl.md（G16 回撤 Protocol 落地，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\36_var_es_monitoring.md（G17 VaR/ES 与波动率监控，骨架 0.1.0）

【工作清单——文档1：35号——回填回撤 Protocol】
- 读 30_multi_strategy §2.5（四级回撤阈值 8/15/20/25% + 恢复机制 + 分层风控 + Kill Switch）+ src/zephyr/risk/ + position/（LS 找 drawdown/kill_switch 相关）+ battle_map_09_risk_control.md（14万字）+ 02_domain_architecture_docs/66_d_risk.md（D_RISK 44 模块）
- 回填讨论要点 8 项：四级阈值落到 StrategyBook、单策略 vs 组合分层、恢复机制、Kill Switch 触发执行、日度熔断、Kill Switch 不可覆盖、回撤基准净值口径、与 regime Shrinkage 协同
- 填成 active
- 全网搜索 2026 年"drawdown protocol 2026""kill switch trading 2026""max drawdown control 2026""recovery protocol 2026"
- 过度工程审查：四级+日度熔断+Kill Switch 是否过重
- 循环至零问题

【工作清单——文档2：36号——回填 VaR/ES】
- 读 30_multi_strategy §2.5.4（VaR_95/ES_95/波动率调整）+ src/zephyr/risk/（LS 找 var/es/volatility 相关）
- 回填讨论要点 7 项：VaR_95 计算（历史模拟/参数法）、ES_95、入场基准、触发动作、30 日波动率调整、数据窗口、与回撤 Protocol 协同
- 填成 active
- 全网搜索 2026 年"VaR ES monitoring 2026""expected shortfall 2026""volatility adjusted position 2026"
- 过度工程审查：VaR/ES 对个人系统是否过重（可降级远期）
- 循环至零问题

【约束】
- 骨架→active 1.0.0
- 不破坏与 30 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-14 指令（负责 37_liquidity + 40_execution）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道）。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\37_liquidity_crisis_protocol.md（G18 流动性危机处理，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\40_execution_broker.md（执行层下单对接，active v1.0.0，代码已施工）

【工作清单——文档1：37号——回填流动性危机】
- 读 30_multi_strategy §2.5.5（Kill Switch 流动性危机：买卖价差>5x 停开仓）+ src/zephyr/risk/（LS 找 liquidity/spread 相关）+ battle_map_09
- 回填讨论要点 5 项：买卖价差监控、流动性危机→停开仓仅平仓、流动性指标定义、与 Kill Switch 关系、A 股涨跌停流动性失效
- 填成 active
- 全网搜索 2026 年"liquidity crisis protocol 2026""bid-ask spread monitoring 2026""A-share limit-up liquidity 2026"
- 过度工程审查：流动性监控是否对个人系统过重（小资金容量小）
- 循环至零问题

【工作清单——文档2：40号——active 代码已施工审查】
- 读全文 + 读 src/zephyr/ex_core/ + ex_sor/（LS + 读核心下单/撮合/滑点代码）+ 02_domain_architecture_docs/44_d_ex_core.md（43 模块）+ 45_d_ex_sor.md（18 模块）+ battle_map_10_execution.md
- 回填：19 项决策的已施工代码实现 why 补全（miniQMT 接口/撮合/TWAP/VWAP/滑点/成本/订单状态机/失败重试/执行风控/集合竞价）
- 审查：§7 降级/重构项是否已落地；滑点模型/成本模型参数是否校准
- 全网搜索 2026 年"execution algorithm TWAP VWAP 2026""miniQMT API 2026""market impact model 2026""Almgren Chriss 2026"
- 过度工程审查：TWAP/VWAP/IS 三种算法是否都需要
- 循环至零问题

【约束】
- 37 号骨架→active 1.0.0；40 号 active 升版本
- 不破坏与 30/35 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-15 指令（负责 41_buy_flow + 42_sell_flow）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（T+1，不能做空）。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\41_buy_flow.md（G19 买入流 spec，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\42_sell_flow.md（G20 卖出流 spec，骨架 0.1.0）

【工作清单——文档1：41号——回填买入流】
- 读 battle_map_06_buy_flow.md（BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C）+ src/zephyr/（LS 找 buy/order_entry 相关）+ 22_sector_rotation（板块回踩）+ 31_position_sizing（仓位）+ 35_drawdown（风控）
- 回填讨论要点 7 项：分批建仓、突破失败降级、买入时序、买入价格锚定、资金分配到多标的、与 budget 协同、T+1 约束
- 填成 active
- 全网搜索 2026 年"buy flow protocol 2026""scaling in position 2026""Wyckoff accumulation 2026""分批建仓 2026"
- 过度工程审查：分批建仓 A/B/C 依赖是否过重
- 循环至零问题

【工作清单——文档2：42号——回填卖出流】
- 读 battle_map_07_sell_flow.md + src/zephyr/sell_decision/（LS + 02_domain_architecture_docs/68_d_sell_decision.md 25 模块）+ 28_sentiment_cycle（退潮卖出）+ 35_drawdown（回撤联动）
- 回填讨论要点 8 项：卖出时序、止损触发（固定%/移动/ATR）、止盈逻辑、情绪退潮卖出、破位卖出、分批卖出、T+1 卖出约束、与回撤 Protocol 联动
- 填成 active
- 全网搜索 2026 年"sell flow protocol 2026""stop loss ATR 2026""trailing stop 2026""O'Neil sell rules 2026"
- 过度工程审查：止损/止盈/破位/分批四种是否全需要
- 循环至零问题

【约束】
- 骨架→active 1.0.0
- 不破坏与 22/31/35/28 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-16 指令（负责 50_observability + 51_panel）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\50_backtest_observability_workplan.md（回测可观测性工作计划，draft v1.0.2）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\51_panel_experiment_history_mlflow_retirement.md（Panel 实验历史 Tab + MLflow 退役，active）

【工作清单——文档1：50号——draft 审查】
- 读全文 + 读 src/zephyr/observability/ + frontend/dashboard/ + 02_domain_architecture_docs/07_d_infra_telemetry.md（11 模块）
- 回填：六零件日志（C1/regime/特征/向量化/StrategyRunner/C2C3）的已施工部分 why；§2.3 命名冲突（zephyr.observability vs 4 处子域）的最终裁定
- 审查：§9 待决策点（命名归属 A/B/C）是否已裁定；MLflow 方案是否已落地或退役（看 51 号）
- 全网搜索 2026 年"MLflow 3.0 2026""experiment tracking 2026""backtest observability 2026""quant logging 2026"
- 过度工程审查：MLflow + 薄包装层是否对个人项目过重（用户偏好集成现有 frontend 而非外部 UI）——重点审查是否符合"集成到现有 Panel dashboard"偏好
- 循环至零问题

【工作清单——文档2：51号——active 审查】
- 读全文 + 读 src/zephyr/frontend/dashboard/（LS + 读 app_panel.py / experiment_history.py / backtest_performance.py）
- 回填：Panel 实验历史 Tab 的已施工代码 why；掘金 5-Tab 复用的鸭子类型重建逻辑
- 审查：MLflow 退役进度是否完成；§七 10 项施工算法 + §八 4 项后续增强的落地状态
- 全网搜索 2026 年"Panel HoloViz dashboard 2026""experiment history visualization 2026"
- 过度工程审查：实验历史 Tab 是否过重
- 循环至零问题

【约束】
- 50 号 draft→active 或保持；51 号 active 升版本
- 不破坏交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-17 指令（负责 52_backtest_docking + 53_simulation）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\52_backtest_framework_docking.md（G23 回测框架对接，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\53_simulation_live_path.md（G24 模拟与实盘验证路径，骨架 0.1.0）

【工作清单——文档1：52号——回填回测框架】
- 读 battle_map_03_backtest_validation.md（BM-BT-01~07 体系）+ src/zephyr/backtest/（LS + 读 core/engine_base.py / vectorized_engine）+ 02_domain_architecture_docs/35_d_backtest.md（51 模块）+ 11_regime_backtest §2.1（regime 对接范式）
- 回填讨论要点 5 项：BM-BT-01~07 在策略验证用法、策略回测 vs regime 回测差异、上线门控 IS→WFA→OOS、过拟合检测三维度、Deflated Sharpe
- 填成 active
- 全网搜索 2026 年"backtest framework 2026""walk-forward analysis 2026""deflated sharpe 2026""purged k-fold 2026""overfitting detection 2026"
- 过度工程审查：BM-BT-01~07 七环节是否过多
- 循环至零问题

【工作清单——文档2：53号——回填模拟实盘】
- 读 battle_map_04_simulation_validation.md + src/zephyr/simulation/（LS + 02_domain_architecture_docs/71_d_simulation.md 15 模块）+ 20_first_batch §4.4（灰度指引）
- 回填讨论要点 6 项：paper trading 环境、模拟时长、小资金实盘路径、实盘→模拟差异监控、上线决策门控、灰度上线
- 填成 active
- 全网搜索 2026 年"paper trading simulation 2026""live trading migration 2026""strategy deployment gating 2026"
- 过度工程审查：灰度四阶段是否过重
- 循环至零问题

【约束】
- 骨架→active 1.0.0
- 不破坏与 11/20 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-18 指令（负责 54_reconciliation + 55_monitoring）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\54_reconciliation_attribution.md（G25 对账归因，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\55_monitoring_review.md（G26 监控告警与复盘，骨架 0.1.0）

【工作清单——文档1：54号——回填对账归因】
- 读 battle_map_11_reconciliation.md + src/zephyr/（LS 找 reconciliation/attribution/pnl 相关）+ 02_domain_architecture_docs/（找 reporting/audit 相关）+ 40_execution_broker（执行产出）+ 30_multi_strategy §2.2（StrategyBook 独立 PnL）
- 回填讨论要点 6 项：PnL 归因分解、每日对账、归因维度、与 StrategyBook 对接、异常交易检测、报表生成
- 填成 active
- 全网搜索 2026 年"PnL attribution 2026""Barra factor attribution 2026""reconciliation trading 2026""trade ledger 2026"
- 过度工程审查：Barra 归因是否过重
- 循环至零问题

【工作清单——文档2：55号——回填监控复盘】
- 读 src/zephyr/observability/ + 02_domain_architecture_docs/07_d_infra_telemetry.md + 50_backtest_observability（衔接）
- 回填讨论要点 6 项：系统健康监控、策略偏离监控、告警阈值通知、每日/每周/每月复盘、策略退役标准、复盘文档模板
- 填成 active
- 全网搜索 2026 年"trading system monitoring 2026""strategy deviation alert 2026""strategy retirement criteria 2026""quant review 2026"
- 过度工程审查：三频复盘（日/周/月）是否过重
- 循环至零问题

【约束】
- 骨架→active 1.0.0
- 不破坏与 40/30/50 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-19 指令（负责 60_cross_cutting + 61_lifecycle）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\60_cross_cutting_cleanup.md（G27 冲突矩阵清理与事件总线，骨架 0.1.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\61_lifecycle_multi_ai.md（G28 策略生命周期与多 AI 协作，骨架 0.1.0）

【工作清单——文档1：60号——回填跨切清理】
- 读 battle_map_12_cross_cutting.md §16（31 条冲突仲裁）+ 30_multi_strategy §7.3（A 模型消失的冲突）+ src/zephyr/（LS 找 event_bus/signal_router 相关）
- 回填讨论要点 6 项：31 条冲突仲裁大部分消失、仅留 firm-level 硬上限、事件总线/信号注入、实时计算节奏、配置驱动、多策略投票降级
- 填成 active
- 全网搜索 2026 年"event bus trading system 2026""signal routing 2026""config driven trading 2026"
- 过度工程审查：事件总线是否对个人项目过重（个人系统是否需要微服务级信号路由）
- 循环至零问题

【工作清单——文档2：61号——回填生命周期】
- 读 battle_map_01_research_incubation + battle_map_02_model_training + 01_design_memo_management_spec §2.2（三层协作）+ src/zephyr/（LS 找 lifecycle/strategy_factory 相关）
- 回填讨论要点 6 项：策略生命周期（孵化→训练→回测→模拟→实盘→退役）、BM-RES 规范、BM-MOD 规范、多 AI 协作分工、文档治理、creation_token/depgraph 登记
- 填成 active
- 全网搜索 2026 年"MLOps lifecycle 2026""strategy factory 2026""model lifecycle management 2026""multi-AI collaboration 2026"
- 过度工程审查：多 AI 协作规范是否过重（个人项目实际是多 AI 还是单 AI 多会话）
- 循环至零问题

【约束】
- 骨架→active 1.0.0
- 不破坏与 30/01 号交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-20 指令（负责 90_methodology + 91_density）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统。

【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\90_methodology_open_questions.md（方法论遗留提案 21 项，draft v1.9.0）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\91_density_prediction.md（密度预测远期愿景（EWMA标准化conformal→Bayesian Kelly→Tail-Aware MDN/Lévy族→Info-Entropic DL+GP→GPD/Lévy-Flow/扩散→QNN 六阶段），draft v1.5.0）

【工作清单——文档1：90号——遗留提案审查】
- 读全文（21 项遗留提案，含策略类型/因子IC/组合构建/风险模型/成本/回测门禁/T+1预测/流动性/数据分层/密度/仓位/成功指标/基准/PIT/资产分级/行为边界/资产覆盖/大额下单/工程细节/做T方法论）
- 逐项审查：每项与项目现状（30_multi_strategy / 10_regime / 已施工代码）的对齐状态——已过时的标❌废弃、已裁定的标✅、待讨论的保留
- 重点：#7 T+1次日预测（8态→12态已过时）、#3 组合构建（risk budgeting→risk parity已裁定）、#4 风险模型（L1/L2/L3→4级回撤Protocol）、#6 回测门禁（V1-V6→BM-BT-01~07）、#11 仓位管理（C-047→MOD-POS-001）
- 全网搜索 2026 年各项最新实践（量化方法论 2026）
- 过度工程审查：21 项是否都需保留，已废弃的可否删除或标 deprecated
- 循环至零问题

【工作清单——文档2：91号——远期愿景审查】
- 读全文（密度预测 QNN 远期愿景）+ 10_regime_detector_spec（12态 regime 已定稿，密度预测是否还有增量）
- 审查：4 个待讨论问题（密度预测必需性/QNN 可行性/校准阈值/与风控关系）是否需更新；QNN 在单机 RTX 3090 的 2026 最新可行性
- 全网搜索 2026 年"density prediction finance 2026""QNN quantum neural network 2026""probabilistic forecasting 2026""CRPS calibration 2026"
- 过度工程审查：QNN 远期愿景是否应保留还是降级删除（个人项目算力限制）
- 循环至零问题

【约束】
- draft 保持或→active/deprecated；改动升版本
- 不破坏交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-21 指令（负责 62_business_registry_construction.md）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT，T+1，不能做空）。

【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\62_business_registry_construction.md（业务资产注册表体系施工总案，active v1.0.0，2026-08-10 新建）

【文档性质】这是 12 个业务资产注册表（因子/策略/技术指标/图形形态/股票池/基准/成本模型/执行算法/风控限额/数据资产/字段字典/实验）的施工总案 + 审查底稿 + 调查索引。P0 已完成 3/12（universe/benchmark/cost_model），P1 待施工 7/12，P2 待施工 2/12。文档已 active 但 P1/P2 大量待施工，需深度审查 schema 设计合理性 + 数据来源准确性 + 过度工程。

【工作清单】
1. 读现状：读 62 号全文（723 行）+ 读以下关联资产了解已施工状态：
   - P0 三件套已落盘 YAML：LS d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ 找 universe_registry.yaml / benchmark_registry.yaml / cost_model_registry.yaml，读其内容验证与 62 号 §5 登记是否一致
   - registry_of_registries.yaml：读 tier_2 业务资产段，验证 3 个 P0 是否已登记 + entry_count 是否准确
   - AGENTS.md（L150-153 RULE-REGISTRY 段）：验证业务资产速查是否已显化
   - architecture_issue_registry.yaml #ARCH-BREG-001：验证施工进度登记

2. P0 三件套审查（已完成，查质量）：
   - §5.1 universe_registry：5 条登记是否覆盖项目所有股票池（打板连板梯队/全A可交易/沪深300/中证800/事件驱动）——反查 24/25/26 号文档是否有遗漏的池
   - §5.2 benchmark_registry：4 条是否足够（沪深300/中证500/中证全指/绝对收益）——审查是否需补中证A500/万得全A（90号§13 提到基准选择待讨论）
   - §5.3 cost_model_registry：3 条（标准/保守/零成本）——审查万3佣金/千1印花税/1bp滑点参数是否符合 2026 A股实际费率；square_root 冲击模型参数是否校准
   - 全网搜索 2026 年"A-share trading cost 2026 佣金 印花税""market impact model calibration 2026"验证参数

3. P1 七注册表 schema 审查（待施工，查设计）：
   - §6.1.1 factor_registry：factor_class 10 类（Barra 6 + A股特色 4）是否合理——反查 src/zephyr/factor/ashare/ 15 子目录实际因子，验证分类覆盖；ic/ir/decay/turnover/capacity 性能字段是否够
   - §6.1.2 strategy_registry：strategy_class 6 类是否完整——反查 20/24/25/26/27/22 号文档；variant 单向 variant_of 机制（裁定 S4）是否会有查询困难
   - §6.1.3 technical_indicator_registry：5 大类 + 9 周期——反查 16 号文档 §2 + src/zephyr/factor/technical_indicators/，验证 40 指标/55 输出列覆盖；与 factor_registry 正交边界是否清晰
   - §6.2.1 execution_algo_registry：6 算法（TWAP/VWAP/IS/AC/POV/Adaptive）——反查 40 号 + src/zephyr/ex_sor/
   - §6.2.2 risk_limit_registry：9 种限额类型——反查 35/36/37/32 号 + src/zephyr/risk/ + config/risk_register.yaml；breach_action 对齐 reconciler 约束（warn/skip/fix-in-place，禁止 commit）
   - §6.2.3 data_asset_registry：三实体（sources/datasets/jobs）——反查原 dataflow_graph_registry.yaml（DS-001~029）+ config/.env.qmt；改名裁定（文件名改+registry_id 保留）是否已在 ruling_registry 登记
   - §6.2.4 chart_pattern_registry：8 大类（蜡烛图/经典图表/缠论/波浪/趋势线/支撑阻力/斐波那契/结构）——反查 src/zephyr/factor/technical_indicators/ + signal_ashare/；recognition_algorithm + algorithm_variant 双字段设计是否必要；subjectivity 字段（波浪=high→experimental）是否合理

4. P2 两注册表审查：
   - §7.1 field_dictionary：范围裁定（仅数据字段，不合并 frontmatter_field_registry）是否正确
   - §7.2 experiment_registry：等 51 号 MLflow 退役后施工的时机是否合理；parent_experiment_id 迭代链设计

5. 通用 Schema 设计原则审查（§4 八条）：
   - frontmatter 对齐 frontmatter_field_registry 是否完整
   - entry_schema 按 DB 表设计预留迁移是否合理
   - 编号格式 REG-{NAME}-{NNN} / {PREFIX}-{DOMAIN}-{NNN} 是否与 module_id_registry allocation_rules 一致
   - 状态机对齐 module_lifecycle_status_vocabulary 是否覆盖
   - 半派生（手写真源入 git + 脚本反查补全）是否可执行

6. 裁定审查（§8 八项核心裁定 + S1-S6 修正）：
   - 逐项审查 8 裁定依据是否充分（variant 术语/数据源合并/YAML vs DB/16号降级/AGENTS.md 显化/onboarding/施工顺序/字段字典范围）
   - S1-S6 修正是否已落实到各 schema

7. 全网搜索 2026 年最新实践（重点）：
   - "feature registry 2026""factor catalog 2026"（factor_registry 对标 WorldQuant Alpha Bank / qlib Alpha158）
   - "strategy registry 2026""strategy lifecycle management 2026"（strategy_registry 对标 Numerai / QuantConnect）
   - "technical indicator registry 2026"（对标 TA-Lib / backtrader / QuantConnect Indicators）
   - "chart pattern recognition 2026"（对标 TA-Lib CDLPATTERN + 缠论 + 波浪）
   - "risk limit registry 2026""risk register 2026"
   - "data asset registry 2026""data lineage 2026"（对标 OpenLineage / DAMA-DMBOK）
   - "experiment registry 2026"（对标 MLflow / Neptune.ai / Comet.ml）
   - "field dictionary 2026""data dictionary 2026"（对标 dbt schema.yml）
   - 找有没有更好的 schema 设计/分类法/字段集

8. 过度工程审查（重点，个人项目红线）：
   - 12 个注册表是否对个人项目过多——能否合并？（如 field_dictionary 是否可并入 data_asset_registry；experiment_registry 是否可暂缓用 MLflow/Panel 替代）
   - YAML vs DB：现阶段 YAML 是否合理，还是直接上轻量 SQLite 更省事
   - data_asset_registry 三实体（sources/datasets/jobs）是否过重——个人项目是否需要 OpenLineage 级血缘
   - chart_pattern_registry 8 大类是否过多——MVP 是否应只做 2-3 类（蜡烛图+经典图表）
   - risk_limit_registry 9 种限额是否过多——个人系统 4 级回撤 + Kill Switch 是否够
   - variant 机制、性能指标字段（运行时可空）是否过度设计
   - §11 YAML→DB 迁移路径是否过早规划（个人系统可能永不触发 500 因子阈值）

9. 结构调整：
   - §1-§12 顺序是否合理
   - §10 数据来源映射表是否准确（反查代码验证 code_path）
   - §12 下一步行动的 P1-A/P1-B/P2 顺序是否最优

10. 循环审查：改完一轮后重新通读全文 + 重新反查代码/注册表，再查一轮，直到连续 1 轮零改动

【约束】
- active 文档改动升版本（v1.0.0→v1.1.0 小改 / v2.0.0 大改），修订记录补一行（§13 如无则新增）
- 不破坏与 15/16/20/22/24/25/26/27/32/35/36/37/40/51/52 号文档的交叉引用
- P0 已完成三件套的 YAML 如需改，同步改 catalogs/ 下对应文件 + registry_of_registries.yaml + AGENTS.md
- 引用代码用稳定 path，禁止 node_id/edge_id
- 需人决策的（如基准选择/费率校准/12表是否精简）标在「待定问题」节，不擅自拍板
- 持续改进不停，循环至零问题
```

---

## AI-22 指令（负责 63_data_utilization_audit.md）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT，T+1，不能做空）。

【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\63_data_utilization_audit.md（业务数据资产利用率审查与施工计划，draft v0.1.0，2026-08-10 新建）

【文档性质】这是业务数据库 101 张表在 design_memos 42 篇文档中的引用审查底稿 + 闲置清单 + 分批接入施工计划。与 62 号配对——62 号建 12 注册表 schema，63 号盘点 101 张表实际利用率（57.4% 已用 / 42.6% 闲置）。draft 状态，审查后可能→active。核心结论：43 张闲置表分 P0-P4 五档，三波分批接入。

【工作清单】
1. 读现状：读 63 号全文（295 行）+ 读以下关联资产验证审查准确性：
   - schemas/categories/：LS d:\ZephyrAlpha\schemas\categories\ 验证实际表数是否=101（数 .py 文件）
   - 逐类核对 §4 八大类表清单（A股K线16/ETF可转债12/跨市场5/Tick4/元数据21/资金事件11/衍生品11/基本面宏观21/衍生2=101）是否与实际文件数一致
   - 反查 §5.2 热度前 15 名表的引用次数是否准确：用 Grep 在 design_memos/*.md 搜表名验证 hit count
   - 反查 §5.3 低频引用表（macro_data/industry_class/三大报表/disclosure_plan/kline_weekly/monthly）是否真的仅 1-2 次

2. 利用率审查方法学审查（§3）：
   - §3.2 双层校验（英文表名 + 中文别名）是否严谨——中文别名表是否穷尽（§3.3 自承"非穷尽"）
   - §3.3 审查局限是否需补强：
     * "tick 关键词过宽"——是否应改用精确正则 \btick\b 排除 ticker/TickTock
     * "只覆盖 design_memos 不含 src/ 代码引用"——是否应补查代码层引用（用 Grep src/zephyr/ 搜表名），否则"闲置"判定可能误杀（代码在用但文档没写）
   - 建议：补一轮代码层引用扫描，把"文档闲置但代码在用"的表从闲置清单移除

3. 闲置表分档审查（§6，43 张 P0-P4）：
   - 🔴 P0 高价值 8 张：逐张验证价值判断是否成立
     * restricted_shares / share_unlock（解禁压力）——是否真是 alpha 信号金矿？全网搜索 2026 年"share unlock alpha 2026""解禁压力 信号 2026"
     * block_trade_detail（大宗折价）——全网搜索"block trade signal 2026""大宗交易 折价 信号"
     * cb_iv（可转债 IV）——是否适合个人系统（可转债套利容量/复杂度）
     * etf_nav（ETF 折溢价）——流动性危机监测是否真需要
     * edb_data（宏观 EDB）——regime 检测器是否真需宏观输入（10 号 regime 已有 12 态，宏观是否增量）
   - 🟡 P1 跨市场 15 张：业务边界裁定项是否完整（A+H/美股/期货/ETF日内）——对照 90 号 §18 资产覆盖范围
   - 🟠 P2 元数据 8 张：注册表治理待登记是否合理（sector_meta/concept_board/msci_adjustment 等）
   - 🟢 P3 分钟级 12 张：后复权周/月线与 16 号三级时间框架栈不一致（§7.3/Q6）——重点审查这个矛盾，建议怎么修
   - ⚪ P4 待归档 5 张：生猪期货 3 张 + LOF/ETF 分钟级——归档理由是否充分

4. 三波施工计划审查（§7）：
   - 第一波 P0 8 张（1-2 周）：7 步骤是否可执行；每张表接入目标文档是否正确；验证标准（至少 1 篇文档显式消费）是否够严
   - 第二波 P1+P2（1 个月）：5 个业务边界决策项是否需人裁定——能否 AI 先给建议
   - 第三波 P3/P4 归档：归档操作在数据采集脚本层，63 号只记录决策——是否需补"归档脚本位置"指引

5. 与 12 注册表关联审查（§8）：
   - data_asset_registry（REG-DATAFLOW-001）首批 66 张表登记清单是否准确
   - factor_registry 候选清单（technical_indicator/money_flow/dragon_tiger/block_trade）是否合理
   - benchmark_registry 扩展（etf_benchmark 闲置）是否应补
   - universe_registry 扩展（convertible_bond_list/etf_list/lof_list 闲置）是否应补

6. 全网搜索 2026 年最新实践：
   - "data utilization audit 2026""data asset inventory 2026"（数据资产利用率审查方法论）
   - "data lineage 2026""data catalog 2026"（对标 OpenLineage / Apache Atlas / Amundsen）
   - "idle data archive 2026""data lifecycle management 2026"（闲置数据归档实践）
   - "alternative data alpha 2026"（限售解禁/大宗交易/可转债 IV 的 alpha 价值实证）
   - "macro regime detection 2026"（EDB 宏观数据对 regime 的增量价值）
   - "ETF arbitrage 2026""ETF premium discount 2026"（ETF 折溢价套利可行性）
   - 找有没有更好的利用率审查方法/闲置判定标准/分档逻辑

7. 过度工程审查（重点，个人项目红线）：
   - 101 张表是否本身就过多——个人系统是否需要覆盖 A股/港股/美股/期货/期权/可转债/生猪全品类
   - 三波施工计划是否过重——个人项目是否应直接"归档为主，接入为辅"（43 闲置里大部分归档，只接 8 张 P0）
   - data_asset_registry 首批 66 张登记是否过重——是否先登记 8 张 P0 + 58 张已用高频表，低频的暂缓
   - §3 双层校验 + 代码层补查是否过度（个人项目是否需要这么严谨的利用率审查）
   - 第二波 5 个业务边界决策项是否都需人定——能否 AI 按个人项目定位直接裁定（如生猪期货必然归档、A+H 必然暂缓）

8. 结构调整：
   - §1-§11 顺序是否合理（§9 不做什么 / §10 开放问题 8 项是否需合并精简）
   - §10 八个开放问题是否都需人决策——Q4/Q5（LOF/生猪归档）AI 可否直接建议
   - 是否应补「待定问题」节与 01_spec §4.4 对齐（63 号是审查清单+施工计划混合，属 §4.4 的"索引/规范/清单"种类）

9. 准确性硬核验证（重点）：
   - 用 Grep 实际扫描 design_memos/*.md，验证 §5.1 利用率数字（58 已用/43 闲置/57.4%）
   - 用 Grep 实际扫描 src/zephyr/ 代码层，找出"文档闲置但代码在用"的表（修正闲置清单）
   - 用 LS schemas/categories/ 验证 101 张表数
   - 如发现数字不准，修正 §5.1 + §6 分档

10. 循环审查：改完一轮后重新通读全文 + 重新 Grep 验证数字，再查一轮，直到连续 1 轮零改动

【约束】
- draft 文档审查后若数据准确+计划可行→升 active 1.0.0；若需大改保持 draft 升 0.2.0
- 修订记录补行（§11 已有，追加即可）
- 不破坏与 62/15/16/26/35/37/10/32/22/50 号文档的交叉引用
- 引用表/代码用稳定 path（schemas/categories/xxx.py）
- 需人决策的（业务边界扩张/归档确认）标在 §10 开放问题，AI 不擅自拍板——但 Q4/Q5 类明显可建议的，AI 给默认建议即可
- 持续改进不停，循环至零问题
```

---

## AI-23 指令（负责 19_northbound_hold_snapshot.md）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】审查并更新 1 篇文档：d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\19_northbound_hold_snapshot.md
这是北向资金季度持仓快照 fetcher 施工计划（draft v0.1.0，10 节结构，§4.4 施工计划类）。北向日频数据 2024-08-19 港交所永久停发后，走 tushare hk_hold 季度快照替代。

【背景知识】
- 01 号规范：§4.1 段位编号制（1x=地基/数据特征，19 空号无冲突）；§4.4 施工计划类按"目标→现状→改动→验证→不做"组织；两条硬约束（必须有修订记录+开放问题等价节）
- 15 号数据特征层：19 号 depends_on 15 号（数据层总纲）
- 62 号注册表：19 号 §5.4 要在 data_asset_registry 登记 northbound_hold_snapshot（REG-DATAFLOW-001 下）
- 63 号数据利用率审查：101 张表盘点，northbound_hold_snapshot 是新建表
- 25 号多因子策略：19 号下游潜在消费方（外资行为因子）
- known_data_gaps.yaml：已登记 hk_connect_flow_source_discontinued + 3 个 akshare 失效接口
- check_algo_quality.py：DEAD_DATA_SOURCES 已标死 4 个北向日频数据源，factor/strategy 无依赖

【工作清单——循环执行直到全部为零】

■ 第 1 轮：读现状（只读不改）
1. 完整读 19 号文档（10 节，~213 行）
2. 核验 §3.1 akshare 1.18.75 实测表：6 个接口状态（stock_hsgt_hist_em 8-19后NaN / individual_em 仅历史 / individual_detail_em 仅历史 / hold_stock_em 失效 / board_rank_em 失效 / stock_statistics_em 失效）——跑 akshare 验证当前是否仍如此
3. 核验 §3.2 tushare hk_hold 实测表：4 个查询日期（20240816/20240819/20260807/20240930/20251231）的北向/南向数字——用项目 tushare token 跑 pro.hk_hold 验证
4. 核验 §5.2 落表 schema：7 列定义 + ORDER BY + 分区 是否符合项目 ClickHouse 建表规范
5. 核验 depends_on（15号/62号）和 related_modules（akshare_provider.py/known_data_gaps.yaml）的 path 是否正确

■ 第 2 轮：数据源选型审查
1. §4.1 四方案对比（A交易所直抓/B东财网页/C tushare/D付费）是否充分——有无遗漏的方案 E（如 akshare 其他接口/华泰中信等券商研报数据/第三方数据商如米筐/jqdata）
2. §4.2 裁定走方案 C 的 4 条理由是否站得住——"工程量最小"是否是唯一考量（数据稳定性/频率/覆盖范围呢）
3. 方案 A 作为 fallback 是否足够——如果 tushare 未来也断，交易所官网爬虫的工程量和维护成本评估
4. 审查 §5.1 fetcher 设计：字段映射（code→src_code, vol→hold_share, ratio→hold_ratio）是否完整——有没有遗漏字段（如 hold_market_value 持股市值？name_change 证券更名？）
5. 审查 §5.3 调度：每季度第 6 个沪深股通交易日跑——这个"第 6 个"如何计算？项目调度系统是否支持？回填 6 个季度是否够（2024Q3~2025Q4）？

■ 第 3 轮：外资行为分析方法论审查（§6，核心审查点）
1. §6.1 持市值变化分解：Δ持股市值 = 主动增减仓 + 股价变动效应。公式"主动增减仓 ≈ Δ持股数量 × 当季VWAP"是否准确——这里用 VWAP 近似成交均价，但外资实际成交价分布未必等于 VWAP，误差有多大？有无更精确的分解方法（如用龙虎榜/大宗交易数据辅助）？
2. §6.2 行业超配/低配：超配比例 = 北向持有该行业市值占比 − 全A该行业市值占比。这里"市值占比"用流通市值还是总市值？行业分类用申万几级？是否需要做风格中性化（Barra 风格因子归因）？
3. §6.3 个股增减持排名：按主动增减仓金额排序——是否需要做归一化（按持股市值占比变化而非绝对金额，避免大市值股永远排前面）？是否需要做显著性过滤（剔除噪声变动）？
4. §6.4 板块切换能力评估：当季加仓行业 vs 下季该行业涨跌幅算相关性——样本量够吗（季度数据，一年才4个样本）？是否需要更长的回看窗口？是否应做滞后分析（加仓后 1/2/4 周而非下季）？
5. §6.5 季度净流入估算：Σ(Δ持股数量 × 当季VWAP)——这是"准净流入"，但与真实净流入的偏差来源有哪些（区间内买卖时点/ VWAP近似误差/ 送转股除权影响）？有无学术文献做过这种估算的误差分析？
6. §6.6 数据需求：季度末持股数量 + 当季VWAP + 申万行业 + 全A市值——这些项目都"已有"，核验是否真的已在 schemas/categories 里就绪（VWAP 计算逻辑、申万行业分类版本、全A市值是否含限售股）
7. 审查是否有遗漏的分析维度：如外资集中度变化（HHI 指数）/ 外资持仓久期分析 / 外资与内资持仓差异 / 外资对个股的定价权测度 / 外资净流入与汇率/美债收益率的外生关联

■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"北向资金 替代数据 2026"——2024-08-19 断档后，业界主流替代方案是什么（季度快照/券商研报估算/另类数据）
2. 搜"沪深港通 季度持仓 外资行为分析 2026"——最新外资行为分析研究方法
3. 搜"northbound capital quarterly holdings analysis 2026"——英文学术文献
4. 搜"tushare hk_hold 季度快照"——tushare 社区有无该接口的使用经验/坑/频率限制
5. 搜"外资持股 行业超配 Barra归因 2026"——是否有人做过北向资金的 Barra 风格归因
6. 搜"季度净流入 估算 误差分析"——学术界对低频净流入估算的精度研究
7. 搜"沪深交易所 沪深股通 季度披露 2026"——官方披露规则是否有新变化（频率/内容/延迟）
8. 审查搜到的最新方法是否有比 §6 六个公式更好的算法——如果有，回填到 §6 并在修订记录登记

■ 第 5 轮：过度工程审查（个人项目标准）
1. P2 优先级是否合理——19 号自标 P2（非 P0，无信号依赖）。审查：季度快照数据是否真的可以等？如果 25 号多因子策略想用外资因子，P2 是否应升 P1？
2. fetcher 设计是否过度——是否需要支持增量/全量/回填三种模式？还是简单全量覆盖即可（季度数据量小，3300行×4季度/年=13200行/年，全量覆盖无压力）
3. 外资行为分析方法论 6 节是否过度——个人项目是否需要做到 Barra 归因级别？还是先做简单的增减持排名 + 净流入估算即可，Barra 归因等外资因子立项时再做
4. 落表是否应新建表——§9 开放问题 Q1"新表 vs 扩展 hk_connect_flow"，审查：新建表（颗粒度不同日频vs季度）vs 扩展现有表（加 period 列），哪种更符合项目惯例（参考 16 号技术指标单表设计 period 列的做法）
5. 是否需要南向数据——§8 不做南向，审查：南向仍日频可用，是否应顺手采集（成本极低）还是坚持不做（聚焦北向，避免范围蔓延）

■ 第 6 轮：一致性与交叉引用审查
1. 与 15 号数据特征层的一致性：19 号的数据源选型/落表规范是否符合 15 号定的数据层架构
2. 与 62 号注册表的一致性：§5.4 登记的 data_asset_registry 字段是否符合 62 号 §3 第 9 项 schema
3. 与 63 号数据利用率审查的一致性：northbound_hold_snapshot 新建表是否需要在 63 号 §4 八大类中登记（当前 101 张表不含此新表）
4. 与 25 号多因子策略的一致性：§1 下游写"25号潜在消费方"，25 号是否真的有外资因子的规划——读 25 号确认
5. 与 known_data_gaps.yaml 的一致性：19 号引用的 3 个 gap（akshare_hsgt_hold_stock_em_broken 等）是否已登记，path 是否正确
6. 与 check_algo_quality.py 的一致性：DEAD_DATA_SOURCES 4 个死源是否与 19 号 §2.2 一致

■ 第 7 轮：文档质量与规范符合性
1. frontmatter：ttl/doc_type/title/owner/language/status/version/date/topic/scope/depends_on/related_modules 是否齐全且合法（对齐 01 号 §4.2）
2. §4.4 施工计划类结构：目标(§1-2)→现状(§3)→改动(§4-6)→验证(§7)→不做(§8)→开放问题(§9)→修订记录(§10)——是否完整
3. §9 开放问题 4 项是否需增减——审查中发现的待人决策的新问题要补登
4. §10 修订记录：本轮审查有改动则升 v0.2.0 并登记
5. 交叉引用全用稳定 path（01 号 §5.2 引用纪律）——无 node_id/edge_id
6. status=draft v0.1.0——审查后若方案定型可建议升 v0.2.0，但 fetcher 未实际施工前不建议升 active

■ 循环条件
- 每轮结束后自检：本轮发现的问题是否全部修复？是否有新发现的问题？
- 若有未修复/新发现，进入下一轮
- 若本轮零发现零修复，再跑一轮确认——连续两轮零发现，任务结束
- 升版本号在 §10 修订记录登记（v0.1.0 → v0.2.0 小改，v1.0.0 大改/升 active）

■ 约束
- 只改 19 号本身，引用 15/62/63/25 号时只读不改
- 如发现 15/62/63/25 号需同步改，记在 19 号 §9 开放问题，不越界改
- 不擅自定决策（如"是否升 P1""是否做南向""新表vs扩展表"），标在 §9 待人决策
- 不破坏与 15/62/63/25/known_data_gaps/check_algo_quality 的交叉引用
- 持续改进不停，循环至零问题
```

---

## AI-24 指令（负责 17_special_trading_days_data_assets.md）

```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。

【你的任务】审查并更新 1 篇文档：d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\17_special_trading_days_data_assets.md
这是 A股"特殊交易日"数据资产全景与治理文档（draft v0.1.0，8 节结构）。承载三件事：特殊交易日完整清单 + 已施工数据资产盘点 + #ARCH-DATA-001/002 治理（港股日历语义错配修复 + 治本方案讨论稿）。

【背景知识】
- 01 号规范：§4.1 段位编号制（1x=地基/数据特征，17 空号无冲突）；§4.4 文档种类适配——17 号是"清单+诊断+讨论稿"混合体，结构按内容组织
- #ARCH-DATA-001：hk_trade_calendar 用 A股日历冒充港股日历的即时止血（已完成验证）
- #ARCH-DATA-002：capability 名↔API 数据语义对齐的系统性治本方案（5 个施工项，讨论稿）
- related_issues 指向 architecture_issue_registry.yaml 的 3 个 ARCH 条目
- 15 号数据特征层：数据层总纲，17 号是数据资产子项
- 62 号注册表：special_trading_days 相关表需在 data_asset_registry 登记
- 63 号数据利用率审查：calendar_event/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/hk_trade_calendar 等表在 101 张表盘点中
- business_data_categories.yaml / tasks.yaml：7 条品类注册 + 6 个采集任务，有悬空引用待修

【工作清单——循环执行直到全部为零】

■ 第 1 轮：读现状（只读不改）
1. 完整读 17 号文档（8 节，~378 行）
2. 核验 §2 特殊交易日完整清单：4 大类（日历结构类 12 事件 / 日历表类 2 / 个股事件类 9 / 待评估项 3）——对照 schemas/categories/ 实际表确认覆盖状态标注是否准确
3. 核验 §3 已施工盘点：7 个 schema 文件 / 7 条品类注册 / 6 个采集任务 / Provider capability——逐一 Grep 确认文件存在且内容与文档一致
4. 核验 §3.5 calendar_event 12 个 event_type 枚举与派生状态——读 internal_compute_provider.py._fetch_calendar_event 确认 9 个已派生 + 3 个预留
5. 核验 §4 #ARCH-DATA-001 修复：internal_compute_provider.py L482-554 的 _fetch_hk_trade_calendar 实现 + akshare_provider.py 的 4 处删除——确认代码与文档描述一致
6. 核验 related_issues 3 个 ARCH 编号在 architecture_issue_registry.yaml 中是否存在

■ 第 2 轮：特殊交易日清单完整性审查（核心审查点）
1. §2.1 日历结构类 12 事件是否有遗漏——审查：国债期货交割日/股指期货最后交易日vs交割日（是否同一天？）/ 央行公开市场操作日 / 经济数据发布日（PMI/CPI/GDP/社融）/ 逆回购到期日 / 可转债申购日 / 转融通交易日 / 融券券源释放日 / 分红季集中期（6-8月/次年4-5月）
2. §2.3 个股事件类 9 项是否有遗漏——审查：限售解禁已列但"定向增发解禁/首发原股东解禁/战略配售解禁"是否需细分 / 股权激励行权日 / 可转债转股开始日/赎回日/回售日 / 要约收购日 / 股东大会召开日（停牌一日）/ 退市风险警示*ST/ST 戴帽摘帽日 / 停牌复牌日
3. §2.4 待评估项 3 项的评估结论是否合理——ETF赎回日"不单独建表"是否正确（T+0实物申赎无固定赎回日的判断）/ 除夕被month_end/year_end覆盖是否充分 / 分红股权登记日"查询层计算"是否够用
4. 2026 年 A 股新增的特殊交易日机制——搜"2026 A股 特殊交易日 新规""2026 期权到期日规则变更""2026 股指期货交割日调整"确认有无新变化
5. 审查 event_type 枚举是否需扩展——如果发现遗漏的特殊日子，评估是否需新增 event_type 或新建表

■ 第 3 轮：#ARCH-DATA-001 修复正确性审查
1. §4.1 病灶描述准确性——akshare 用 ak.tool_trade_date_hist_sina（A股日历）填充港股日历表，确认这个 API 确实返回沪深交易日而非港交所交易日
2. §4.2 即时止血 5 步动作——逐一核验：①internal_compute L482-554 实现是否用 exchange_calendars XHKG ②akshare 4 处删除是否干净（capability frozenset / CapabilityContract / _fetch 方法 / 死常量 _TBL_HK_TRADE_CALENDAR）③tasks.yaml source 改 akshare→internal ④business_data_categories data_source [exchange]→[internal] ⑤ARCH 登记
3. §4.2 验证 9 检查点——圣诞节/节礼日/耶稣受难日/复活节翌日/佛诞/香港特区成立纪念日 不在港股交易日，1478 个交易日——跑代码或 Grep 验证日志确认这些断言
4. 修复是否引入新问题——hk_trade_calendar 改用 internal 后，下游 calendar_event.hk_connect_closed 派生（A股开盘且港股休市=北向停摆日）是否正确产出

■ 第 4 轮：#ARCH-DATA-002 治本方案审查（过度工程重点）
1. §5.1 病根第一性原理——"capability 名↔API 数据语义"维度空白，与 #ARCH-CH-INDUSTRY-CLASS-MIGRATE 同类病——这个归因是否准确
2. §5.2 施工项 1（CapabilityContract 扩展 expected_market/expected_variety）——向后兼容（字段可选）是否真的零迁移成本？现有 capability 不填则不校验，是否有 silently skip 风险
3. §5.3 施工项 2（capability_semantic_registry.yaml）——"只对跨市场/跨品种易混淆 capability 强制登记"的过度工程防线是否合理？哪些 capability 算"易混淆"——需要一个判定标准，否则人工裁量空间太大
4. §5.4 施工项 3（capability_validator AST gate）——AST 解析 _fetch 方法体提取外部 API 符号，技术可行性如何？ak.*/bs.*/xt.*/THS_* 的提取模式是否会漏（如动态调用 getattr(ak, name)）/ 误报
5. §5.5 施工项 4（符号一致性 gate，优先施工）——校验 fetch 路由引用的 _fetch_xxx 是否真实定义，这是最基本的检查，确认是否已有类似 linter/pylint 规则可复用而非自建
6. §5.6 施工项 5（运行时抽样校验，可选推迟）——声明时 gate 已覆盖大部分，本项推迟是否合理
7. §5.7 施工顺序与优先级——施工项4先做（0.5天）→ 1+2+3 同批（3天）→ 5 可选（1天），总成本 4.5 天是否合理？个人项目是否需要全部 5 项，还是施工项 4 + 1 即可（MVP 先防"半截工程"和"语义错配"两大类）
8. 过度工程审查：5 个施工项是否对个人项目过重——参考 project_memory "过度工程处理原则"，MVP 阶段是否应砍到施工项 4+1 两项，其余推迟

■ 第 5 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"A股 特殊交易日 事件研究 2026"——学术界/业界对特殊日子的 event study 最新方法
2. 搜"股指期货交割日效应 2026""期权到期日效应 2026"——交割日/到期日效应的量化研究更新
3. 搜"MSCI 调整 A股 2026 被动资金"——MSCI 调整的数据获取路径与影响研究（§6.2 待讨论项）
4. 搜"capability semantic validation data pipeline 2026"——数据管道 capability 语义校验的业界实践
5. 搜"exchange_calendars XHKG 2026"——exchange_calendars 库港股日历的维护状态与已知问题
6. 搜"A股 日历事件 回测前向特征 2026"——特殊日子作为回测前向特征的最佳实践
7. 审查搜到的方法是否有比 §5 治本方案更好的算法——如果有更轻量的方案，回填到 §5 讨论

■ 第 6 轮：开放讨论项审查（§6，5 项待人决策）
1. §6.1 API 白名单维护责任——选项 A（强制登记）vs B（warn 不拦），文档倾向 A 但建议 MVP 用 B。审查：个人项目是否应该直接用 B（warn），A 的治理强度对单人不必要
2. §6.2 msci_adjustment 数据源——3 条候选路径（爬虫/付费/手工），审查：2026 年有无新的免费 MSCI 数据源？个人项目是否真的需要 MSCI 调整数据（外资因子依赖度评估）
3. §6.3 fomc_meeting/major_meeting/stamp_duty_change 手工填充——3 条候选（CSV/admin接口/SQL），审查：admin 接口已标"过度工程不推荐"是否正确，SQL 脚本是否最轻
4. §6.4 悬空引用修正——business_data_categories.yaml L1923 + tasks.yaml L2371 指向不存在的 .trae 路径，待改为指向 17 号。审查：这是紧随小任务，是否应在本轮直接修复（只改2行引用，不越界改其他文档内容）
5. §6.5 ETF 赎回日不单独建表——审查：T+0 实物申赎无固定赎回日的判断是否准确，净赎回从 etf_nav 衍生的查询层方案是否够用

■ 第 7 轮：一致性与交叉引用审查
1. 与 15 号数据特征层的一致性：17 号的数据资产架构是否符合 15 号数据层规范
2. 与 62 号注册表的一致性：special_trading_days 相关表（calendar_event/index_adjustment 等）是否已在 data_asset_registry 登记——若未登记，标在 §6 开放问题
3. 与 63 号数据利用率审查的一致性：17 号涉及的表（calendar_event/hk_trade_calendar/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment）在 63 号 101 张表盘点中是否正确分类
4. 与 19 号北向资金的一致性：17 号 calendar_event.hk_connect_closed（北向停摆日）与 19 号北向数据断档治理是否衔接——hk_connect_closed 依赖 hk_trade_calendar，而 19 号讨论北向日频断档
5. 与 architecture_issue_registry.yaml 的一致性：#ARCH-SPECIAL-DAYS/#ARCH-DATA-001/#ARCH-DATA-002 三个条目的描述/状态/关联文档是否与 17 号一致
6. 与 business_data_categories.yaml / tasks.yaml 的一致性：§3.2/§3.3 的 7 条品类 + 6 个任务是否与实际 YAML 内容一致——注意悬空引用（§6.4）

■ 第 8 轮：文档质量与规范符合性
1. frontmatter：ttl/doc_type/title/owner/language/status/version/date/topic/scope/related_issues 是否齐全合法——注意 scope 写了两个值（07_trading_decision_architecture / 03_modules_database），是否符合 01 号 §4.2（scope 应为单一值）
2. 文档结构：17 号是"清单+诊断+讨论稿"混合体，§4.4 允许按内容组织——审查 8 节结构是否合理，是否有重复/遗漏
3. §6 开放讨论项 5 项是否需增减——审查中发现的新待人决策问题要补登
4. §8 修订记录：本轮审查有改动则升 v0.2.0 并登记
5. 两条硬约束（§4.4）：有修订记录（§8 ✅）+ 有开放问题等价节（§6 ✅）
6. 交叉引用全用稳定 path（§5.2 引用纪律）——无 node_id/edge_id
7. status=draft v0.1.0——治本方案（§5）定稿后可转 active，但当前讨论稿态合理

■ 循环条件
- 每轮结束后自检：本轮发现的问题是否全部修复？是否有新发现的问题？
- 若有未修复/新发现，进入下一轮
- 若本轮零发现零修复，再跑一轮确认——连续两轮零发现，任务结束
- 升版本号在 §8 修订记录登记（v0.1.0 → v0.2.0 小改，v1.0.0 大改/转 active）

■ 约束
- 只改 17 号本身，引用 15/19/62/63 号及 architecture_issue_registry/business_data_categories/tasks.yaml 时只读不改
- 例外：§6.4 悬空引用修正（business_data_categories.yaml L1923 + tasks.yaml L2371 改指向 17 号）可越界改，因这是文档自身承接的紧随任务且仅改 2 行引用——改后在 §8 登记并注明
- 如发现 15/19/62/63 号需同步改，记在 17 号 §6 开放问题，不越界改
- 不擅自定决策（如"API白名单A还是B""MSCI走哪条路径""治本方案砍到几项"），标在 §6 待人决策
- 不破坏与 15/19/62/63/ARCH 注册表/YAML 的交叉引用
- 持续改进不停，循环至零问题
```

---

## 使用说明

1. **开新对话**：在 Trae/CLI 中开 24 个新对话窗口（或分批开，如每批 5-7 个并行）
2. **复制指令**：从本文档复制对应 AI 编号的指令块（` ``` ` 之间的内容）
3. **粘贴执行**：粘贴到新对话，AI 会自动开始读取文件、回填、审查、搜索、循环
4. **监控进度**：每个 AI 独立工作，互不通信，通过修改的文档文件交接
5. **冲突处理**：若两个 AI 改同一交叉引用（如 30 号被 AI-10 负责，但 AI-06/11/12/13/14 都引用），各 AI 只改自己负责的文档，引用对方文档时只读不改

> **注意**：24 个 AI 并发可能产生资源竞争（同时读同一文件 OK，但同时写不同文档时注意 git 冲突）。建议每个 AI 独立 commit，或全部完成后统一 review 合并。
>
> **AI-21 特殊提示**：62 号文档是 12 个业务注册表的施工总案，与 AI-02(15号数据特征层)/AI-06(20/21号策略选股)/AI-08(24/25号打板多因子)/AI-13(35/36号风控)/AI-14(40号执行)/AI-16(51号实验)/AI-17(52号回测) 都有交叉引用。AI-21 只改 62 号本身，引用其他文档时只读不改；如发现其他文档需同步改，记在 62 号「待定问题」节，不越界改。
>
> **AI-22 特殊提示**：63 号文档是 101 张业务表利用率审查，与 AI-02(15号数据特征层)/AI-03(10号regime)/AI-07(22号板块轮动)/AI-08(24/25号策略)/AI-09(26号事件驱动)/AI-10(28号情绪)/AI-11(32号firm风险)/AI-12(33号预算变更)/AI-13(35号回撤)/AI-14(37号流动性)/AI-16(50号可观测)/AI-17(52号回测)/AI-21(62号注册表) 都有交叉引用（数据消费方遍布全链）。AI-22 只改 63 号本身，引用其他文档时只读不改；如发现其他文档需同步改（如 P0 表接入需改 26/35/37/10/32 号的数据源节），记在 63 号 §10 开放问题/§7 施工计划，不越界改。AI-22 与 AI-21 强配对（62 号建 schema、63 号盘点表），两 AI 可对齐协作但各自只改自己负责的文档。
>
> **AI-23 特殊提示**：19 号文档是北向资金季度持仓快照 fetcher 施工计划，与 AI-02(15号数据特征层，上游总纲)/AI-08(25号多因子策略，下游消费方)/AI-21(62号注册表，数据资产登记)/AI-22(63号数据利用率审查，新建表登记) 有交叉引用。AI-23 只改 19 号本身，引用 15/25/62/63 号及 known_data_gaps.yaml/check_algo_quality.py 时只读不改；如发现上游/下游需同步改（如 63 号需补登 northbound_hold_snapshot 新表、62 号需在 data_asset_registry 补登记），记在 19 号 §9 开放问题，不越界改。
>
> **AI-24 特殊提示**：17 号文档是特殊交易日数据资产全景与治理，与 AI-02(15号数据特征层，上游总纲)/AI-21(62号注册表，数据资产登记)/AI-22(63号数据利用率审查，6张表分类)/AI-23(19号北向资金，hk_connect_closed 衔接) 有交叉引用。AI-24 只改 17 号本身，引用 15/19/62/63 号及 architecture_issue_registry/business_data_categories/tasks.yaml 时只读不改。例外：§6.4 悬空引用修正（business_data_categories.yaml + tasks.yaml 各 1 行改指向 17 号）可越界改，因这是文档自身承接的紧随任务且仅改引用行。如发现其他文档需同步改，记在 17 号 §6 开放问题，不越界改。AI-24 与 AI-23 弱关联（17 号 hk_connect_closed 依赖 hk_trade_calendar，19 号讨论北向断档），两 AI 各自只改自己负责的文档。
