---
ttl: permanent
---

# AI-NIGHT-001 阶段3 · design_memos 全量审查分包1（19 篇 / 20 文件）

> **审查人**：AI-NIGHT-001 分包1 子代理 ｜ **日期**：2026-08-19
> **范围**：`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/` 下 10~28 号共 20 个 .md 文件（16 号含 build_plan 与 catalog 两篇）。
> **方法**：① 逐篇读全文识别文档承诺的施工内容；② 代码实证（Grep/Glob 于 `src/zephyr`、`scripts/`、`schemas/`、`tests/`、`docs/01_policies_and_standards/_registry/`、`src/zephyr/data/config/`）；③ 对照 construction_progress_tracker.md §一/§五批次区；④ 结案报告核验/插入/补正；⑤ 未施工清单 + 裁定建议（基准：system_charter §2 约束一~六 + §4 范围边界）。
> **实证口径说明**：`docs/03_modules/_cross_layer/database/depgraph.db` 与 `.runtime/governance.db` 均为 **0 字节空库**（实证），depgraph 状态无法机查，一律以代码/注册表文件级实证为准；批次完工事实以 tracker 记载交叉印证。
> **未改动的文件**：construction_progress_tracker.md（统筹统一登记）、src/（零改动）、无 git commit。

---

## 总览表

| # | 文档 | 施工状态实证（核心结论） | 结案报告动作 | 未施工条数 |
|---|---|---|---|---|
| 10 | regime_detector_spec | 检测器生产态（4 态 HMM+overlay+校准器+RiskSignal） | 已有·核验基本一致，**补正**（追加复核补记） | 7 |
| 11 | regime_backtest_validation_plan | Phase 0-2 完工、Phase 3/4 部分、Phase 5 未启动 | 已有·核验 OK | 9 |
| 12 | regime_phase2_validation | 四验证器+校准器全落码，Phase 2 闭环 | 已有·核验 OK | 0 |
| 13 | regime_phase3_engineering_plan | P0+P1 数据层完工，E9/NLP5-8/E8 未做 | **补写结案报告** | 4 |
| 14 | regime_s2_diagnosis | P0 处置落地，P1-E9 五子项未施工 | **补写结案报告** | 6 |
| 15 | data_feature_layer_spec | 六要点五项 production，特征仓库未施工 | **补写结案报告** | 7 |
| 16 | technical_indicator_build_plan | 计算库/存储/注册表/测试完工，调度未闭环 | 已有·核验 OK（正文 §3 步骤8 滞后已注记） | 2 |
| 16 | technical_indicator_catalog | 同上 | 已有·核验 OK | 1 |
| 17 | special_trading_days_data_assets | 定稿+hk 日历修复落地；清理/MVP 最小集未做 | 已有·核验基本一致，**补正**（追加复核补记） | 8 |
| 18 | cold_archive_build_plan | archiver+契约 v1.2.0+测试全落地 | 已有·核验 OK | 4 |
| 19 | northbound_hold_snapshot | fetcher+调度+schema+登记全落地 | 已有·核验基本一致，**补正**（追加复核补记） | 5 |
| 20 | first_batch_strategies | 信号链组件全 production；3 sleeve 类空壳 | **补写结案报告** | 4 |
| 21 | stock_selection_engine | L0/L1/L2-C production；统一接口未施工 | **补写结案报告** | 10 |
| 22 | sector_rotation_spec | 采集层 production；8+2 项计算层零落码 | **补写结案报告** | 11 |
| 23 | strategy_correlation_validation | 门禁 production；计算生产侧零落码 | **补写结案报告** | 8 |
| 24 | daban_strategy_detail | 四引擎+支撑设施 production；12+8 算法零落码 | **补写结案报告** | 9 |
| 25 | multifactor_strategy_detail | 65 模块 production；8 编排算法零落码 | **补写结案报告** | 6 |
| 26 | event_driven_strategy_detail | 事件源链路 production；sleeve 组件零落码 | **补写结案报告** | 8 |
| 27 | second_batch_strategies | draft 暂缓，无代码（符合文档性质） | **补写结案报告** | 1 |
| 28 | sentiment_cycle_trading | 设计备忘无独立代码（符合文档性质） | 已有·核验 OK | 6 |
| **合计** | | | **插入 11 篇 / 补正 3 篇 / 核验 OK 6 篇** | **116** |

**裁定分布（116 条）**：过度工程 **2** ｜ 未来工程-小型 **92** ｜ 未来工程-大型 **22**（另有 2 条登记为"待 Owner/他域裁定"决策项，不计入三档：26 号 CAND-AISA-001、28 号 #ARCH-ASHARE-002）。

---

## 10_regime_detector_spec

**施工状态实证**：`regime/core/regime_detector.py`（4 态 HMM+overlay_gated+predict_log_proba）、`regime_feature_builder.py`、`overlay_signals_builder.py`（_STUB_DIMS=set()）、`risk_signal_builder.py`、`features/`（market/trend/overlay/risk/chip_distribution_engine/synthetic_vix/wyckoff_engine/regime_data_loader 全在）、`validation/phase2/`（a1/a2/b1/b4+confidence_calibrator+phase2_runner+historical_events.yaml）全部落码；C1 经 `backtest/regime_validation/`（c1_comparator/c1_runner/shrinkage_provider）+ `backtest/implementations/shrinkage_engine.py` 落地；scripts/tests 有 scan_hmm_states/dump_s2_scores/run_c1_shrinkage_validation。

**结案报告动作**：已有 2026-08-16 三段式，核验与实证一致；因"未做事项"仅列 S2，**补正追加复核补记**（登记六类额外未落码设计项）。

**未施工清单 + 裁定**：
1. S2 算法重设计（P1-E9）——**未来工程-小型**（14 号详设就绪，单批可闭环）。
2. §4.7.6/§4.8.5/§4.11.10/§4.12.10 机构级数据维度（IV/COT/信用利差/期权异动/CAPE/巴菲特指标/Margin Debt/Put-Call）数据管道与评分——**未来工程-大型**（新数据基础设施；当前生产形态不依赖其通过验证）。
3. §4.8.1 LPPL 赶顶检测——**未来工程-小型**（函数级；T4 已有多维信号兜底，重评条件=T4 实证漏检时）。
4. §6.2 主线识别四阶段评分 + RRG 轮动——**未来工程-小型**（与 22 号 RRG 项同源，函数级）。
5. §6.2.3 NetworkX 资金图谱 PageRank——**过度工程**（单人 MVP 无明确增量价值，memo 自列第四阶段；charter §2 约束一/约束五）。
6. §2.5.4 情绪周期灰度概率输出升级（23-B 硬标签→5 维灰度）——**未来工程-小型**（契约变更+BM-SEL-25 影响评估）。
7. §9 备查升级路径包（HSMM/Student-t/Wasserstein/层次 HMM/TVTP/Shannon/Staggered/BOCPD/Feature Saliency/Conformal/CPCV/动态调制矩阵/RARP/Causal-TS/NLP-regime 连接）——**未来工程-大型**（HMM 引擎重写级/新基础设施级；维持备查）。

## 11_regime_backtest_validation_plan

**施工状态实证**：Phase 0-2 全部落码（同 10 号实证）；`scripts/tests/_smoke_walkforward.py`（E1）与 `simulation/deflated_sharpe_calculator.py`（C4 计算器）存在；`backtest/core/decision_gate.py` 无 regime/shrinkage 引用（Phase 5 未启动实证）。

**结案报告动作**：已有 2026-08-16 三段式，核验与实证一致，无需补正。

**未施工清单 + 裁定**：
1. C4 Deflated Sharpe——**未来工程-小型**（零开发，计算器已存在，跑一次）。
2. E2 stationary bootstrap（替代固定 block）——**未来工程-小型**。
3. E3 参数敏感性 ±20% / E4 交易成本 0-50bps——**未来工程-小型**。
4. D1 ConfidenceSignal 四档 ±20% 网格 / D3 聚合公式参数扰动——**未来工程-小型**。
5. E1 各窗口 MaxDD 改善 CV<0.5 正式统计——**未来工程-小型**。
6. A3 状态转移路径覆盖 ≥80% 正式统计——**未来工程-小型**。
7. A4 特征重要性（Permutation 主轨+SHAP 审计轨）——**未来工程-小型**。
8. B2 CRPS / B3 置信度合理性 / C2 极端事件保护 / C3 节流归因——**未来工程-小型**（分析型，基于既有回测产物）。
9. Phase 5 决策门控（BM-BT-07 适配）——**未来工程-大型**（依赖首批策略层就绪）。

## 12_regime_phase2_validation

**施工状态实证**：四验证器 + confidence_calibrator + phase2_runner + historical_events.yaml + design_match 字段全部落码；tests/regime/phase2/ 套件存在；scripts/tests/run_phase2_validation.py 存在。

**结案报告动作**：已有 2026-08-16 三段式（"未做：无——本档职责范围为 Phase 2，已闭环"），核验与实证一致，无需补正。

**未施工清单 + 裁定**：无。

## 13_regime_phase3_engineering_plan

**施工状态实证**：P0（4 态+calibrator）与 P1 数据层（news_collector/nlp_inference/sentiment_sft_trainer + scripts/ml 四脚本、enable_phase2c 参数、t3_* 函数、s2_policy/s2_bad_news_flat 关键词 MVP）全部实证在码；`models/` 目录不在仓（SFT 权重为大件本地产物，未入库属预期）；P1-E9/NLP Phase 5-8/P2-E8 零落码实证。

**结案报告动作**：**补写结案报告**（插入于 frontmatter 之后）。

**未施工清单 + 裁定**：
1. P1-E9 S2 算法重设计——**未来工程-小型**（14 号详设就绪，单批可闭环；当前最高优先）。
2. NLP Phase 5 RLSP（带护栏实验）——**未来工程-大型**（RL 训练基础设施+GPU 实验管线；memo 已定其为可选护栏实验）。
3. NLP Phase 6-8（GGUF 回灌 Ollama / sentiment_aggregator 端到端+离线批量 / 验收）——**未来工程-小型**（转换脚本+单模块+批量任务）。
4. P2-E8 forward_days 参数扫描——**未来工程-小型**（脚本级）。

## 14_regime_s2_diagnosis

**施工状态实证**：P0 处置落码（design_match 字段 b4_transition_accuracy.py:99/212/294 + historical_events.yaml:82/91/100 + z>1 + min_periods=20）；dump_s2_scores.py 存在；P1-E9 五子项零落码（s2_breadth_thrust_score/keys_or_gte/s2_valuation_score_fundamental/_capitulation_daily 均无；s2_three_yang_flag 仅 pct_change 单参数旧版）。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. P1-E9a-e 五子项（capitulation 衰减加权多过滤器 / valuation 路A+路B / spring 复用+深度分级 / breadth_thrust V 反转通路+析取 / three_yang 6 维分级）——**未来工程-小型**（函数级+调用链迁移，单批可闭环）。
2. Step 0 数据/接口勘探（daily_valuation 字段/wyckoff Spring/涨跌家数/期权 put-call）——**未来工程-小型**（勘探脚本已给出）。
3. §4.5 防过拟合方法论栈（事件研究+预注册+DSR+CPCV+MinTRL+WFE）——**未来工程-小型**（vendor Neyt 库+验收流程）。
4. fund 维度升级（融资余额+超大单加权，跨 P1-E4）+ vix 门槛校准（跨 P1-E7）——**未来工程-小型**（函数/配置级）。
5a. 演进方向-大型组（AH-HMM 元体制门控 / LVI 强平级联 / ProRealCode 16 事件 FSM）——**未来工程-大型**。
5b. 演进方向-小型组（滞回边沿触发器 / EVR 量价背离 / flush 桥接信号）——**未来工程-小型**。

## 15_data_feature_layer_spec

**施工状态实证**：103 schema + apply_*_ddl.py；pit_manager 四函数 + pit_query；gov_enforcement/rule_enforcement/quality_gate.py apply_quality_gate:253；factor 治理全链 + technical_indicators 7 文件 + factor_registry.yaml；DQ_SPECS 注册表仅字符串无实现（无 check_completeness 等函数实证）；无特征值宽表 schema；calendar_event_refresh 未登记（tasks.yaml 实证）。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. 要点④特征仓库存储层（CH 宽表）+ data_asset_registry 登记——**未来工程-小型**（单表+写入管道+登记，单批可闭环；选型已定）。
2. DQ_SPECS 八维 check_func 实现绑定——**未来工程-小型**（函数级）。
3. Embargo BDay 近似→真交易日历——**未来工程-小型**（函数级；前置依赖=17 号 calendar_event 回填）。
4. backtest 前置检查器绑定（BM-BT-02-D）——**未来工程-小型**（消费引用方接入；重评条件未触发前可继续暂缓）。
5. 轨 A/轨 B 合流（轨 B miniQMT connector）——**未来工程-大型**（多厂商抽象实现；既定裁定=需求真实出现前维持双轨）。
6. 衰减监控调度化（定时任务）——**未来工程-小型**（调度配置级；重评条件=因子数>50）。
7. #ARCH-CH-009 ingest_ts 版本列统一裁定——**未来工程-小型**（schema 裁定，下次大修时）。

## 16_technical_indicator_build_plan

**施工状态实证**：technical_indicators 7 文件 + tests/zephyr/factor/technical_indicators/ 6 测试文件 + schemas/categories/market_technical_indicator.py + internal_compute_provider（capabilities=["technical_indicator","calendar_event","hk_trade_calendar"]）+ technical_indicator_registry.yaml（REG-IND-001 已建成，tracker AI-REG-IND-001 41 条目实证在库）全部在码；**调度未闭环实证**：scheduler.py create_provider 无 source=="internal" 分支（else→"未知数据源"），tasks.yaml 无 technical_indicator_incremental/full_refresh 条目。

**结案报告动作**：已有 2026-08-16 三段式，核验与实证一致（注册表建成已载）；正文 §3 步骤 8"REG-IND-001 待施工"与 §7② 为滞后表述（注册表实际已建），本报告注记，未改正文。

**未施工清单 + 裁定**：
1. 调度闭环（scheduler.py 补 source=="internal" 分支 + tasks.yaml 登记 technical_indicator_incremental/full_refresh）——**未来工程-小型**（函数分支+配置登记；同根缺口影响 17 号 hk_trade_calendar/calendar_event 等全部 internal 任务）。
2. 分钟周期回算收尾（30/15/5/1min）+ 回算后四重验证（行数对账/通达信抽样/NULL 率/分区分布）——**未来工程-小型**（运行任务+验证脚本，随 18 号阶段 2 联动）。

## 16_technical_indicator_catalog

**施工状态实证**：同 16 plan（40 指标/58 列/5 大类 + Registry↔DDL 双向校验 + REG-IND-001 注册表在库）。

**结案报告动作**：已有 2026-08-16 三段式，核验与实证一致；正文 §7②"REG-IND-001 未施工"为滞后表述，本报告注记。

**未施工清单 + 裁定**：
1. rsi/macd_divergence 简化趋势对比→峰谷检测精度升级——**未来工程-小型**（函数级；重评条件=精度需求出现时）。（调度项与 16 plan 共享，不重复计）

## 17_special_trading_days_data_assets

**施工状态实证**：7 个 schema（calendar_event/index_adjustment/ipo_schedule/margin_target_adjustment/dividend_tax_node/msci_adjustment/hk 相关）全在；internal_compute_provider._fetch_calendar_event（:505）+ _fetch_hk_trade_calendar（:625）落码；**声明残留实证**：akshare_provider.py L275 frozenset + L511 CapabilityContract("hk_trade_calendar") 仍在（方法体已无）；calendar_event_refresh 未登记；6 品类未注册；expected_market/expected_variety 零命中；scheduler 无 internal 分支。

**结案报告动作**：已有 2026-08-16 三段式，核验基本一致；**补正追加复核补记**（登记六项定稿后未落地施工项 + scheduler internal 分支同根缺口）。

**未施工清单 + 裁定**：
1. §6.6-1 akshare hk_trade_calendar 声明残留清理（删 2 处）——**未来工程-小型**（行级删除；防"声明无实现"AttributeError）。
2. §6.6-2 calendar_event_refresh 任务登记 + 回填 7 年——**未来工程-小型**（配置+跑一次；15 号 Embargo 项依赖此）。
3. §6.6-4 六条品类注册补登——**未来工程-小型**（配置级）。
4. §6.6-3 三条 akshare 采集链（index_adjustment/ipo_schedule/margin_target_adjustment 的 provider 方法+任务+品类）——**未来工程-小型**（单批三条链可闭环；v1.0.0 已定稿暂缓至下个数据资产窗口，届时先登 CAND）。
5. §5.8 MVP 最小集（施工项 4 声明-实现符号一致性双向 gate + 施工项 1 CapabilityContract 语义字段）——**未来工程-小型**（AST gate+2 可选字段，~1 天；治理窗口项）。
6. 施工项 2 capability_semantic_registry + 施工项 3 capability_validator AST gate——**未来工程-小型**（~2.5 天，与项 4/1 同治理窗口）。
7. §6.3 FOMC/major_meeting/stamp_duty_change CSV 录入 + 一次性 IMPORT——**未来工程-小型**（数据录入，随项 2 同批）。
8. §2.4 待评估 event_type（bond_futures_delivery/mlf_operation/earnings_deadline/a50_futures_delivery）派生——**未来工程-小型**（派生函数级； earnings_deadline 与事件驱动 sleeve 联动价值最高）。
（§5.6 施工项 5 运行时抽样校验=已定推迟，启动条件未触发，不列入裁定。）

## 18_cold_archive_build_plan

**施工状态实证**：scripts/ch/archiver.py 在码；data_retention_contract.yaml 已升 version 1.2.0（INV-RET-001/003 修订措辞落证实证，AI-ARCH-002 f556515519）；tests/scripts/test_ch_archiver.py 在码；阶段 1/2 执行有 manifest 实证（memo §3.8.2 回填）。

**结案报告动作**：已有 2026-08-16 三段式，核验与实证一致，无需补正。

**未施工清单 + 裁定**：
1. verify 强化（checksum_md5 入 manifest + 抽样 100 行字段值比对 + manifest 补 rows/ch_size_bytes/compress_ratio）——**未来工程-小型**（函数级增强；已归档 1865 分区行数全一致，风险敞口小，"好上加好"项）。
2. 独立 export 子命令（纯备份模式）——**未来工程-小型**（CLI 暴露既有函数）。
3. ETF/LOF 5min+ 周期 2019 年前归档（~3.8 GiB）——**未来工程-小型**（配置级 archive-range 跑一次；开放问题 5 待裁定=一致性 vs 收益成本比）。
4. technical_indicator 30/15/5/1min 2019 年前残留分区归档收尾——**未来工程-小型**（回算完成后运行任务，无新设计）。

## 19_northbound_hold_snapshot

**施工状态实证**：northbound_hold_fetcher.py + tushare_provider 路由 + tasks.yaml:1747 任务 + schemas/categories/market_northbound_hold_snapshot.py + business_data_categories.yaml:814 品类 + data_asset_registry.yaml 条目 + known_data_gaps.yaml（三失效接口+撞码 monitoring 条目）全部实证在库；§6.3/§6.5 分析函数零命中。

**结案报告动作**：已有 2026-08-16 三段式，核验基本一致；**补正追加复核补记**（登记 §6.3/§6.5 MVP 分析层未落码）。

**未施工清单 + 裁定**：
1. §6.3 个股增减持排名（Δ持股×当季 VWAP，top 加仓/减仓）——**未来工程-小型**（pandas 数十行，单批可闭环）。
2. §6.5 季度净流入估算（Σ Δ持股×VWAP）——**未来工程-小型**（同上；可与国信季度估算交叉验证）。
3. 南向（HK）季度快照采集——**未来工程-小型**（复用 fetcher；§9 裁定待外资因子需要时）。
4. 外资行为因子立项——**未来工程-大型**（因子开发立项；待数据积累 2-3 个季度）。
5. §6.1 持市值分解 / §6.2 行业超配 / §6.4 板块切换评估——**未来工程-小型**（随因子立项演进；§6.4 有样本量约束警示）。

## 20_first_batch_strategies

**施工状态实证**：打板四引擎 + 因子工厂 + 事件底座全 production；position/core/{strategy_book, firm_risk_aggregator, budget_change_handler}.py 与 pf_alloc/core/regime_meta_allocator.py 均已成产（budget_change_handler 含 TierLevel/FreezeNewPositions/RebalanceRequest/ForcedTrim/BudgetChangeHandler 完整类，非 memo §2.7 所述骨架）；pf_core/strategies/ 仅 __init__.py 空壳实证；strategy_registry.yaml 的 daban/multifactor 条目均为课程规则 candidate（code_path 空），非 sleeve 策略类。

**结案报告动作**：**补写结案报告**（注记 §2.7 两处"骨架"状态已过时）。

**未施工清单 + 裁定**：
1. 3 个 sleeve 策略类（daban/multifactor/event_driven 组装策略类）——**未来工程-大型**（首批上线主链路，多模块组装 + 依赖 G08/G09/G10 细节定型与 G05 标准接口；与 21 号①同源）。
2. charter §3 约束二措辞物理修订——**未来工程-小型**（文档级；04 域 owner 待认领）。
3. convergence_window 按换手率校准——**未来工程-小型**（配置级，待首批实盘）。
4. 各策略容量精确测算——**未来工程-小型**（分析型，随 G08/G09/G10）。

## 21_stock_selection_engine

**施工状态实证**：L0/L1/L2-C 三层 production（data/+factor/+signal_ashare 4 引擎）；shared/contracts/synthesized_signal.py + signal_fundamental/synth/signal_synthesizer.py 在码；无 SelectionResult 类（仅局部 StockSelectionResult）；BM-SEL-16/17/18 漏斗模块、信号工厂、confidence 算法零命中。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. SelectionResult 统一接口 + 3 sleeve 实现——**未来工程-大型**（与 20 号①同源主链路）。
2. 漏斗三层级（BM-SEL-16 分级指标过滤/17 初筛/18 精筛评分）——**未来工程-小型**（规则层批处理模块，单批可闭环）。
3. 6 维权重 IC 加权校准（路径 A）——**未来工程-小型**（函数级；SHAP 路径 B 远期）。
4. SelectionResult.confidence 算法（按 sleeve 差异化选型）——**未来工程-小型**。
5. 事件 sleeve 过滤置信度阈值——**未来工程-小型**（配置级，G10 校准）。
6. 信号工厂九子阶段流水线 + 信号聚合器——**未来工程-大型**（新层；激活条件=信号冲突实例 ≥3 例，未触发）。
7. LLM alpha 挖掘闭环（Hubble/AlphaEvolve/XAlpha/AlphaMemo/FactorMiner/MAGE/AlphaAgent/AlphaSAGE 八框架）——**未来工程-大型**（离线研发基础设施，远期）。
8. Cross-Sectional LSTM baseline——**未来工程-大型**（远期 ML；重评条件=因子工厂稳定 6+ 月）。
9. BM-SEL-12 分布特征工程（Signature 路径签名）——**未来工程-大型**（signatory 依赖+密度预测配套，远期）。
10. 板块轮动 score 映射公式落地（SECTOR_QUADRANT_BASE 等）——**未来工程-小型**（随 22 号 G06 批次）。

## 22_sector_rotation_spec

**施工状态实证**：sector_snapshot_collector/sector_kline_downloader/sector_ranking_engine + sector_analyzer 六方法 + sector_constituent/money_flow/market_kline_sector_880 schema 全 production；RRG/回踩/调整周期/虹吸/q3/5 状态/门槛/水温/涨停比/资金聚合零命中实证。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**（全部纯函数规则层、无新数据源，按 §5.2 第二~三阶段批次）：
1. 板块涨停比归一化（涨停数→涨停比）——**未来工程-小型**。
2. aggregate_capital_nature_to_sector 资金性质板块级聚合——**未来工程-小型**。
3. 回踩质量 A/B/C 判定（Fib+量能衰减+时间窗）——**未来工程-小型**。
4. 调整周期进度追踪（MOD-SIG-040，扩散指标）——**未来工程-小型**。
5. RRG 轮动序列（DualEma 10/26+四象限+whipsaw 确认）——**未来工程-小型**。
6. 虹吸态 HHI 识别（三信号 z-score 加权）——**未来工程-小型**。
7. q3/q5/q20 多时间框架动量加权——**未来工程-小型**。
8. 板块轮动 5 状态分类（4 维输入规则映射+watch_score）——**未来工程-小型**。
9. 三级放行门槛（准入 gate v2.1+水温动态阈值）——**未来工程-小型**。
10. 水温→板块信号响应映射（5 档 signal_weight/gate/rrg_filter）——**未来工程-小型**。
（⑩ 板块→个股传导映射（龙头识别+加权传导）同批，计入第 1-10 项集合不单列。）
11. lead-lag network / ML 转折点检测 / 板块相关性聚类——**未来工程-大型**（第四阶段远期）。

## 23_strategy_correlation_validation

**施工状态实证**：strategy_correlation_gate.py + correlation_analyzer.py + deflated_sharpe_calculator.py + walk_forward.py 在码；策略级矩阵/bootstrap/分层标签/Neff/过拟合引擎/CUSUM 漂移零命中实证。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. 数据预处理 pipeline（对数收益率+ADF+Modified Z-score+交易日对齐）+ 策略级 Pearson/Spearman 矩阵——**未来工程-小型**。
2. multivariate stationary block-bootstrap 引擎（Patton-Politis-White 自动 block size，2000×同步行重采样）——**未来工程-小型**（引擎级，单批可闭环）。
3. 情绪周期分层标签器（消费 BM-SEL-23-B 输出+置信度兜底）——**未来工程-小型**。
4. Neff 特征值分解引擎（Ledoit-Wolf 收缩前置）——**未来工程-小型**。
5. 过拟合检测引擎（deflated-alpha v0.3.0 vendor 评估+audit() 集成+PDR/PSI/DFR）——**未来工程-小型**（外部包集成+封装；vendor 评估为前置决策）。
6. §5.4 CUSUM/PSI 相关性漂移监控（复用 deadman/reconciler 基础设施）——**未来工程-小型**。
7. DCC-GARCH 时变相关（第二阶段）——**未来工程-大型**（arch 库两步估计；Markov-switching DCC 已裁定拒绝不列）。
8. §5.5 Alpha 半衰期定理/双曲衰减拥挤度建模——**未来工程-大型**（远期；需首批实盘 12 月数据）。

## 24_daban_strategy_detail

**施工状态实证**：四引擎+支撑设施全 production（cancel_rate_guard.py/price_cage.py 在码实证）；§3.13 七项+§3.14 五项+8 具名函数 grep 零命中实证；MOD-POS-022 已落成（非骨架）。

**结案报告动作**：**补写结案报告**（注记 §3.6"budget_change_handler 骨架"表述已过时）。

**未施工清单 + 裁定**：
1. §3.13#1 NextDayExitDecision（含 classify_position_status）+#2 DabanInstantCircuitBreaker +#5 get_dragon_tiger_pit（PIT 断言，**必须修复**）+§3.14#8 pre_validate_daban_signal +#9 HoldingPeriodMicrostructureMonitor——**未来工程-小型**（函数级，首批实盘前必做）。
2. §3.14#10 DabanPITBacktestFramework（全数据源 PIT 回测框架）——**未来工程-小型**（首批回测前必做）。
3. §3.13#6 SignalDecayMonitor（CUSUM+PSI+方差压缩）——**未来工程-小型**（实盘后即需）。
4. §3.13#3 classify_decision_v192 第 7 类 +#7 reflush_next_day_exit_decision——**未来工程-小型**（Phase 5）。
5. §3.13#4 DabanExecutionAlgorithm +§3.14#11 DabanTimingDecision +#12 DynamicCapacityCalculator——**未来工程-小型**（Phase 3，依赖 G22）。
6. 8 具名函数（classify_echelon_health/score_consecutive_height_with_death_pool/score_auction_3d/detect_auction_paper_tiger/score_seal_structure/forecast_next_day_premium/classify_reflush_board/detect_quant_seat_warning）——**未来工程-小型**（函数级，首批回测校准）。
7. 双引擎两层分类法统一裁定（动作层是否吸收进 production 引擎）——**未来工程-小型**（设计裁定+落码 REFLUSH_DIVE）。
8. Phase 5 ML 栈（CatBoost 破板预测/Siamese LOB/Du 混合模型/QFCQT/Hawkes 长记忆核/速度域签名）——**未来工程-大型**（ML 基础设施，远期）。
9. C9 换手率按流通盘分层校准 + 42 号时间止损口径校准——**未来工程-小型**（配置级，首批回测时）。
（battle_map BM-SEL-23-A-6 修正属他域文档，登记不列裁定。）

## 25_multifactor_strategy_detail

**施工状态实证**：65 production 模块逐项实证在码（合成/评估/治理/DAG/组合优化/registry）；§3.7 八项+Mask-First+CUSUM/淘汰层零命中实证。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. §3.7 八项编排算法（SynthesisDegradationChain/ConstraintArbitration/DecayActionLifecycle 6 态/SimpleFactorAttribution/CrowdingRealTimeMonitor/RebalanceTrigger 含 Inaction Cost/MultifactorPITBacktestFramework/HoldingDriftMonitor）——**未来工程-小型**（纯增量 30-80 行函数级；可组"多因子编排算法批"单批闭环，#5/#6/#8 标 MVP 即做、#7 首批回测前必做）。
2. Mask-First tradability mask——**未来工程-小型**（~40 行，MVP 最高优先）。
3. CUSUM 预警层+自动淘汰层——**未来工程-小型**（随 #1 之 DecayActionLifecycle 同批）。
4. C1-C7 策略级约束链 ↔ MOD-PF-006 对齐（CTR-003 注入）——**未来工程-小型**（配置级，上线前）。
5. DecayActionLifecycle 6 态 ↔ factor_registry 5 态映射规则——**未来工程-小型**（规则定义+回写 62 号）。
6. Phase 4.1-4.20 ML 栈 + BM-SEL-02-E LLM 语义去重 + BM-SEL-02-M 因果验证 + BM-RC-06-D 三深度增强——**未来工程-大型**（远期 ML/基础设施；各有重评条件）。

## 26_event_driven_strategy_detail

**施工状态实证**：事件源链路全 production（三源+collector+dedup+dragon_tiger 双表+corporate_action_processor+market_event_integrator+nlp_inference+ipo_calendar）；sentiment_aggregator 缺失实证；sleeve 组件（event_score 族/进出场/辅助/异动/IPO/地缘/dt modifier/薄封装）与 BM-SEL-19/MOD-SIG-049 零命中实证。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. sentiment_aggregator.py（跨源一致性投票聚合）——**未来工程-小型**（单模块；NLP Phase 7）。
2. event_score 公式族（单/双/三因子）+ should_enter/should_exit + 5 辅助函数 + event_store/volume_series/volume_ma/trading_days_ago 四薄封装——**未来工程-小型**（函数级集合；薄封装 <1 天）。
3. detect_anomaly 异动识别器（国盛异动雷达施工化）——**未来工程-小型**（函数级，G23 校准参数）。
4. compute_ipo_siphon_coefficient + ipo_siphon_position_adjustment + map_geopolitical_event_to_sectors + dragon_tiger_corroboration_modifier——**未来工程-小型**。
5. 六因子矩阵数值项（dReport/Jump on PEAD/隔夜趋势；AStockEvent 远期）——**未来工程-小型**。
6. BM-SEL-19 事件驱动分布筛选漏斗（MOD-SIG-049）——**未来工程-大型**（依赖知识图谱 BM-SEL-11 design 态+NLP 管道就绪，依赖链未闭合）。
7a. Hawkes 自激发/CNN 可视化盈余/LLM 动态知识图谱/Data Funnel 双阶段——**未来工程-大型**（§5 暂缓项，各有重评条件）。
7b. Janus-Q 10 类细分类+端到端 LLM 决策——**过度工程**（需 62,400 篇标注语料+微调，违反 charter §2 约束一单人带宽；memo 已自我裁定暂缓，复核维持）。
8. CAND-AISA-001 AI 舆情分析器——**待 Owner/G28 四问裁定**（决策项，不计工程裁定）。

## 27_second_batch_strategies

**施工状态实证**：无代码（符合 draft 暂缓性质）；33 条 momentum_trend registry 条目为课程规则 candidate 实证。

**结案报告动作**：**补写结案报告**。

**未施工清单 + 裁定**：
1. 价值反转/动量趋势两策略（重启时：alpha 信号定稿+财报 PIT 面板深加工+全市场时序扫描+相关性实测）——**未来工程-大型**（主动暂缓非缺口；重启条件=首批 3 策略实盘 ≥3 月+复盘 ≥12 期+因子衰减基线，未满足）。

## 28_sentiment_cycle_trading

**施工状态实证**：设计备忘无独立代码（符合文档性质）；BM-SEL-23-B 生产实现=market_sentiment_analyzer.py（5 阶段硬标签，非灰度）；本文 spec 函数集（locate_sentiment_phase/compute_sentiment_temperature/detect_phase_transition/apply_sentiment_soft_influence/combine_sentiment_regime/PHASE_DISCIPLINE/STRATEGY_DEPLOYMENT_MATRIX/Hawkes 系）零命中实证。

**结案报告动作**：已有 2026-08-16 三段式，核验与实证一致（"本档为设计备忘，无独立代码施工"属实），无需补正。

**未施工清单 + 裁定**：
1. 定位器准确率历史回测评估（30 号 §6.3 挂载）——**未来工程-小型**（回测分析型，随 G07 批次）。
2. BM-SEL-23-B 输出契约升级（4+1 硬标签→5 维灰度概率）——**未来工程-小型**（契约变更+BM-SEL-25 影响评估；与 10 号⑥同源）。
3. §3.5.2 映射表权重标定（Phase 2 人工调参）——**未来工程-小型**（配置级，实盘后）。
4. Phase 3 HMM/小模型学习映射权重——**未来工程-大型**（升级触发条件未满足）。
5. §3.7.4 Hawkes+block-bootstrap 隐形驱动验证脚本——**未来工程-小型**（验证级，随 G07）。
6a. §3.10 八个标准函数签名落码（设计态准入时）——**未来工程-小型**（函数级，随首批策略/G05）。
6b. #ARCH-ASHARE-002 情绪周期 6 阶段标准化+4 盘面指标——**待 Owner 裁定**（proposed；6 阶段需先证伪五阶段不足，决策项不计工程裁定）。

---

## 附：跨篇同根缺口（供统筹合并立项参考）

1. **scheduler.py 无 source=="internal" 分支**（实证）——16 号调度闭环、17 号 hk_trade_calendar/calendar_event 及一切 internal 任务的共同根因；一处修复（函数分支）+ tasks.yaml 配置登记可解多篇缺口。**未来工程-小型**，建议单批闭环。
2. **3 sleeve 策略类 + SelectionResult 统一接口**（20 号①=21 号①）——首批上线主链路"最后一公里"，跨 signal/position/pf_core 多模块。**未来工程-大型**，依赖 G08/G09/G10 定型。
3. **S2 算法重设计 P1-E9**（10 号①=13 号①=14 号①）——同一工程项三处引用，14 号 v0.4.5 详设就绪。**未来工程-小型**，建议单批闭环（TDD-first+Step 0 勘探门禁）。
4. **23-B 灰度输出升级**（10 号⑥=28 号②）——同一契约变更两处引用。**未来工程-小型**。
5. **calendar_event 回填**（17 号②→15 号③ Embargo 真日历的依赖）——**未来工程-小型**。
6. **RRG 轮动序列**（10 号④=22 号⑤）——同一函数两处引用。**未来工程-小型**。

## 阻塞

无。全部实证与文档编辑已完成；depgraph.db/governance.db 为 0 字节空库（实证），depgraph 状态以代码级实证替代，已在口径说明中声明。
