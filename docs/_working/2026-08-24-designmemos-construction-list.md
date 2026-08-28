---
ttl: task_bound
---

# design_memos 待施工清单（2026-08-24，T3 审查产出）

> 来源：`design_memos/` 61 份文档全量审查（报告：`.runtime/construction_20260823/reports/T3_memos_review.md`）。
> 收录口径：**未施工 / 部分落地中的未落项**；已正式裁定暂缓且重评条件未触发、纯等实盘数据的校准项不列（在来源文档结案报告中已登记）。
> MOD 号建议纪律：仅顺延既有号段（MOD-SIG→082 起 / MOD-PLAN→018 起 / MOD-EX→063 起 / MOD-POS→024 起 / MOD-SELL→019 起 / MOD-REGIME→009 起 / MOD-RPT→031 起；MOD-CMP 代码实证至 010→011 起、MOD-RK 至 026→027 起、MOD-OBS 至 001→002 起）；无号段域标「待统筹定号」，勿撞号。
> 标注「待复核」者：08-19 复核后代码演进快，施工前须先 grep 实证当前状态再派单。
> 按优先级排序：P0 > P1 > P2 > P3 > Owner 窗口。

> **结案审查（2026-08-28 复核）**：未结案（多项已落地，清单未核销）
> - 已实证落地（未核销）：#1 RUN-05 断网断电演练节已入册（00_index v2.12.0 注记）；#2 S2 五子项 `s2_breadth_thrust_score`/`s2_valuation_score_fundamental`/`_capitulation_daily` 已落码 overlay_features.py + 测试；IC 回填 + FCT 12 条入册（factor-glossary 头部结案报告）。
> - 待复核：experiment_tracking adapters、MOD-OBS-002 等；其余 P2/P3 项继续有效，施工前须 grep 实证再派单。

---

## P0 · 窗口期顺手即做

### 1. RUN-05 断网断电断点恢复演练入 57 号日循环 SOP
- 来源文档：architecture_review_2026_08_module_upgrade_audit.md §5.3（唯一新增项）；57_daily_cycle_sop.md（承载）
- 设计声明摘要：宪章约束五「断电断网→策略状态机断点恢复、持仓 RPO=0」当前无演练项，彩排清单（开盘检查→模拟盘→收盘→回测→对账）未覆盖该最高概率家用故障。
- 建议模块落点：文档项（57 号 SOP 增补一节）+ 演练脚本可选（scripts/ 待统筹）；无需新 MOD。
- 建议 MOD 号：—（SOP 文档修订）
- 优先级：P0（极小工作量，RPO=0 口径实证）
- 验收标准：57 号 SOP 含断网断电演练节（步骤=杀 trading/data 进程+断网 5 分钟→恢复→KillSwitch 状态/持仓/fill 去重集自 state_store 重建核对）；彩排日实测一次并留记录；grep「断网」命中 57 号。

## P1 · 高价值（生死线/验证闭环/前置解锁）

### 2. P1-E9 S2 评分算法重设计五子项（E9a~E9e）
- 来源文档：14_regime_s2_diagnosis.md §4（详设+Step 0 勘探门禁+§4.5 防过拟合栈）；13_regime_phase3_engineering_plan.md（P1-E9 挂载，完成后 13 号可升 active）
- 设计声明摘要：E9a capitulation 衰减加权和+多过滤器／E9b valuation 路 A CAPE/PB 分位+路 B 阈值放宽／E9c spring 复用 wyckoff_engine+深度分级+velocity／E9d breadth_thrust V 反转通路／E9e three_yang 6 维分级。
- 建议模块落点：`src/zephyr/regime/features/`（overlay_features.py 同族，s2_* 评分函数族扩建）
- 建议 MOD 号：**MOD-REGIME-009**（必要时拆 -010）
- 优先级：P1（regime=宪章生死线；详设就绪、零新数据源依赖待 Step 0 勘探确认）
- 验收标准：Step 0 勘探门禁报告（daily_valuation 字段/wyckoff Spring 接口/涨跌家数/期权 put-call 四路实证）→ 五子项落码 testing（grep `s2_breadth_thrust_score`/`s2_valuation_score_fundamental`/`_capitulation_daily` 有命中）→ B4 对 3 个 S2 事件 design_match 翻 true → 13 号 frontmatter 升 active；测试含防过拟合口径（§4.5）。

### 3. 因子 IC 实证回填批（factor_registry 154 条）
- 来源文档：62_business_registry_construction.md（结案残余）；29_factor_strategy_extraction.md（入库后续）；44 号 §2.1（CAND-FAC-003 链路）
- 设计声明摘要：factor_registry 全条目 ic/ir/decay_halflife/turnover/capacity/last_evaluated_at/evidence 七字段空 + code_path=""（DVERIFY §1.4 全库性缺口）；BTRUN 已跑通首份实测范式（momentum_20d IC=-0.0399 / value_factor IC=+0.0216，horizon=5，N=5169）。
- 建议模块落点：流程批（复用 BTRUN `_btrun_multifactor.py` 范式 → scripts/ 或 .runtime 跑批）+ `fragments/BTRUN_ic_backfill.yaml` 草稿合并入册；另需 code-anchored 因子条目裁定（154 条全 NL 条目的 code_path 锚定方案）。
- 建议 MOD 号：—（数据/注册表流程批，无需新 MOD）
- 优先级：P1（A5 因子面板与 G09 校准前置；44 号 12 条 FCT 登记同链路）
- 验收标准：可计算 code 因子条目七字段实测回填（窗口/universe 口径留痕）；NL 条目 code_path 锚定裁定书；回填批次 evidence 字段指向 artifact；factor_registry 过 ROOR 校验。

### 4. 50 号五零件 experiment_tracking adapters
- 来源文档：50_backtest_observability_workplan.md §3 ⑥（自明「核心剩余工作」，预估 1.5 天）
- 设计声明摘要：regime_detector / regime_feature_builder / vectorized_engine / StrategyRunner / C2C3（建时即接入）五零件接入 experiment_tracking，全链路 lineage；当前 adapters/ 仅 c1_adapter.py。
- 建议模块落点：`src/zephyr/experiment_tracking/adapters/`（逐零件一 adapter）
- 建议 MOD 号：**MOD-OBS-002**
- 优先级：P1（验证闭环层；单批可闭环）
- 验收标准：5 adapter 落码 testing；每零件跑一次后 `list_runs` 可查（含 lineage 字段）；51 号 Panel 实验历史 Tab 可见新 run；零侵入（lazy import 同 c1_adapter 先例）。

### 5. Champion-Challenger mSPRT 晋升通道（前置：晋升载体裁定）
- 来源文档：61_lifecycle_multi_ai.md §3.3（纪律 1/2/7/9）；54_reconciliation_attribution.md（BM-REC-02-B/03-D 被阻塞项）
- 设计声明摘要：策略晋升/回滚/归档原以 MLflow alias 为载体，51 号已完全卸载 MLflow（src 零命中）——载体失效须先重裁定（experiment_tracking FallbackBackend 或注册表状态机等价物），再落 mSPRT 统计组件。
- 建议模块落点：裁定书（docs/02_enterprise_architecture/04_architecture_principles_decisions/）→ `src/zephyr/governance/lifecycle_governance/`（strategy_retirement_evaluator 同域）
- 建议 MOD 号：待统筹定号（lifecycle_governance 域，MOD-GOV 族顺延）
- 优先级：P1（阻塞 54 号两环节+首批策略上线后晋升路径）
- 验收标准：载体裁定书落盘（Owner 批准）→ mSPRT 晋升判定组件落码 testing（双阶段：champion 守擂/challenger 挑战，伪代码按 61 号 §3.3 纪律 1）→ 54 号 BM-REC-02-B 绩效归因可排期。

### 6. 44 号残余两件：FCT-sentiment 12 条因子登记 + 外盘 8 标的采集接线
- 来源文档：44_premarket_intraday_decision_upgrade.md §2.1/§7；GAPP1B_report.md §4 D3 实测
- 设计声明摘要：① 12 条 FCT 条目（加速度三件套/护盘背离度/量能外推比/大幅回撤数/期指基差两件/期权两件/电风扇速度计/个股分歧度）走 62 号 ROOR 流程登记 factor_registry 并挂 CAND-FAC-003；② 外盘缺口 8 标的（恒生/日经/KOSPI/DXY/USDCNH/WTI/黄金/美债10Y）采集接线——FOREIGN_COLLECTOR_SLOTS 配置位已就位（GAP-F-23），恒生/日经/KOSPI 建议 akshare index_global_em 一路三收、美债10Y 建议 fred_provider DGS10（provider prod 现成，落库表走 CTR）；另 ES/NQ/A50 盘中快照历史深度回填、us_index 29 日历史回填。
- 建议模块落点：① factor_registry.yaml（ROOR 流程）；② src/zephyr/data/config/tasks.yaml + CTR（DDL/品类/任务三件套，Owner 窗口）
- 建议 MOD 号：①—（注册表流程）；②待统筹定号（MOD-DAT 族，照 MOD-DAT-foreign_coverage 惯例）
- 优先级：P1（44 号 M1/M3 消费链完整性；外盘页/传导引擎输入）
- 验收标准：① 12 条 FCT 条目入册（formula/alpha_source 齐全，candidate 态，挂 IC 回填链路）；② 8 标的落库（品类+任务注册+首次采集成功行数留证），check_foreign_coverage 输出 missing=0；③ ES/NQ/A50/us_index 历史回填任务登记。

### 7. 作战室样本积累日常编排接线（45 号 W0 前置）
- 来源文档：45_warroom_playbook.md（W0/W6 验证闭环）；WARROOM_report.md §5（GAP-F-01 解锁评估建议）
- 设计声明摘要：scenario_plan 族需「盘前 9:00 compute_and_record + 盘后 writeback_scenario_outcome」每日跑才能积累 W0 窗口（20 日）样本；当前治理库历史行=0（落库通道 08-23 才建）。MOD-PLAN-008/010/017 消费端已就位，只欠日常编排。
- 建议模块落点：运行时编排（挂 57 号日循环 SOP 环节④/事件驱动管线）；batch_runner 的 target_date 次交易日解析接 market_trade_calendar（WARROOM 遗留 3）。
- 建议 MOD 号：—（编排接线，模块已在码 MOD-PLAN-008~017）
- 优先级：P1（校准样本每晚一天积累即晚一天可用；作战室 W0/W2 概率格真源）
- 验收标准：连续交易日 scenario_plan+outcome 族日行落库（prediction_log 行数逐日递增实证）；target_date=次交易日；20 日后 compute_calibration 产出首份真实 Brier/校准曲线。

## P2 · 专项小批（单件 ≤100 行或单批可闭环）

### 8. 43 号盘中操纵实时检测（对敲/拉抬/洗售）
- 来源文档：43_compliance_discipline.md（结案残余，BM-BUY-15 补强残余）
- 设计声明摘要：Spoofing/Layering/WashTrade 盘中实时检测（市场操纵 4 类检测规则的盘中侧），需盘中实时流驱动。
- 建议模块落点：`src/zephyr/compliance/`（MOD-CMP-001 同族）
- 建议 MOD 号：**MOD-CMP-011**
- 优先级：P2（合规底线但依赖盘中流编排；可先离线批处理口径 MVP）
- 验收标准：三类检测规则落码 testing（阈值入 risk_limit 注册表）；误报率口径留痕；检出事件落 compliance_log。

### 9. 64 号 Q8/Q16/Q17 数据韧性三件
- 来源文档：64_data_source_download_spec.md §16.2（Q18 已闭环，余三件）
- 设计声明摘要：Q8 data parts>100 告警／Q16 fetch_perf scheduler 被动记录／Q17 per-source 自动熔断器。
- 建议模块落点：`src/zephyr/data/`（scheduler/services 同族）
- 建议 MOD 号：待统筹定号（MOD-DAT 族）
- 优先级：P2（数据供应链韧性）
- 验收标准：parts 超阈告警落日志/告警链；fetch_perf 每任务运行指标落库可查；熔断器按源失败计数自动断/复+留痕，测试含故障注入。

### 10. 55 号 §6 残余四件
- 来源文档：55_monitoring_review.md §6（四项暂缓，重评条件在档）；RISK/GAP6 报告遗留
- 设计声明摘要：Email/WeChat sender 实发（MOD-L08-001 register_channel 位已就位）／miniQMT 下单链路探针／偏离归因分解 H-A~D／复盘模板引擎固化外化（GAP-F-40 模板迁注册位）。
- 建议模块落点：`src/zephyr/frontend/implementations/`（sender）+ `src/zephyr/reporting/`（探针/归因/模板）
- 建议 MOD 号：**MOD-RPT-031**（归因分解）/ **MOD-RPT-032**（模板引擎外化）；sender/探针随件登记
- 优先级：P2（监控运营完整性；sender 实发需 Owner 渠道凭据）
- 验收标准：sender 注册位接真实 webhook（测试 mock 通道+一次实发留证，Owner 窗口）；探针纳入 source_health 族；H-A~D 归因分解落码 testing；战报模板注册位化（多版本可切换）。

### 11. 36 号 daily_auditor 集成包装层
- 来源文档：36_var_es_monitoring.md §3.11（08-19 复核新发现未落码项）
- 设计声明摘要：`run_var_backtest` + `log_entry_var`/`log_baseline`/`log_recalibration` 包装层（回测 4 法本体已在 var_backtester.py）。
- 建议模块落点：`src/zephyr/risk/core/daily_auditor.py`（追加）
- 建议 MOD 号：**MOD-RK-27**
- 优先级：P2（VaR 背测运营化，单批可闭环）
- 验收标准：包装层落码 testing；日终审计链产出 VaR 背测记录+入场基准/重校准日志三方法落痕。

### 12. 90 号 P2 十一项复核清偿专项
- 来源文档：90_methodology_open_questions.md（v2.0.0 施工优先级表 P2 段）
- 设计声明摘要：#2 BHY FDR 嵌入 decay_monitor（bhy_fdr.py 已在，嵌入待复核）/#8 LVaR+跌停 ST 维度/#9 半衰期样本权重（sample_weights.py 已在，口径待复核）/#15 universe 两维字段/#16 生存线监控/#17 单一订单出口+YAML 归并/#18 Instrument Master 轻量表/#20 策略指纹库+DTW+correlation_gate 持久化/#21 做T四规则配置化（MOD-SIG-068/SELL-018 部分承载，待复核）/#14 deliberate future-date 泄漏测试自动化/#1 策略族归属声明治理流程。
- 建议模块落点：逐件对应既有域（factor/risk/universe/compliance 等），组 1-2 个专项小批。
- 建议 MOD 号：按域顺延（factor 族待统筹 / MOD-SIG-086+ / MOD-RK-028+），派单前逐件 grep 核销已落地者。
- 优先级：P2（单件均 ≤100 行）
- 验收标准：逐件「已落地核销 or 落码 testing」二分闭环；90 号 P2 表逐项标注终态。

### 13. 63 号三波补文档施工 + 审查工具链
- 来源文档：63_data_utilization_audit.md §6.2/§7
- 设计声明摘要：批次 A 9 张风险表→35/37/10/24 号文档引用补齐、批次 B+C 25 张→26/22/15 号、批次 D 记录；工具链 scripts/audit_data_utilization.ps1 + docs/_audit/ CSV 快照。
- 建议模块落点：文档批（design_memos 各文档消费方小节）+ scripts/（工具链）
- 建议 MOD 号：—（文档/脚本批）
- 优先级：P2（消费层覆盖率 35.9% 治理）
- 验收标准：三波批次执行后消费层覆盖复测 ≥目标线（63 号 §3.4 口径）；工具链可重跑产出 CSV 快照。

### 14. 13 号 NLP Phase 5-8 + P2-E8（待复核后派单）
- 来源文档：13_regime_phase3_engineering_plan.md（结案未做②③）
- 设计声明摘要：NLP Phase 5-8（RLSP 带护栏实验/GGUF 回灌 Ollama/sentiment_aggregator 端到端管道+离线批量/验收）；P2-E8 forward_days 参数扫描。
- 建议模块落点：`src/zephyr/nlp/` + `scripts/ml/`（sentiment_aggregator.py 已存在，Phase 5-8 链路完整度待复核）
- 建议 MOD 号：待统筹定号（MOD-NLP 族顺延）
- 优先级：P2
- 验收标准：端到端管道跑通（采集→推理→聚合→落库）+离线批量+验收报告；forward_days 扫描结果回写 13 号。

### 15. 52 号残余三件
- 来源文档：52_backtest_framework_docking.md §7
- 设计声明摘要：DSR 双实现统编（0.5 vs 0.95，待 Owner 裁定 SSoT）→ DSR 入 DecisionGate 判定链（随裁定）；四核心模块零单测（walk_forward/decision_gate/overfitting_detector/pit_manager）。
- 建议模块落点：`src/zephyr/backtest/core/` + `tests/`
- 建议 MOD 号：待统筹定号（backtest 域）；测试件随测试债批
- 优先级：P2（测试债 P1 子项）
- 验收标准：Owner 裁定唯一 DSR SSoT 后单行收敛+DecisionGate 第四条件可选接线；四模块单测补齐（每模块 ≥8 用例，含边界）。

### 16. 61 号其余生命周期残余（等触发类除外）
- 来源文档：61_lifecycle_multi_ai.md（结案未做②④⑤）
- 设计声明摘要：BM-RC-04-F AI 行为基线+异常告警（白名单/额度已部分承载，行为统计告警为增量）；BM-MT-02-A/B 灰度+影子部署+对抗鲁棒性（MLOps L2 批，随策略上线）；退役 5 步工作流+strategy_archive/（等首个退役触发，不抢建）。
- 建议模块落点：`src/zephyr/governance/lifecycle_governance/` 等
- 建议 MOD 号：待统筹定号
- 优先级：P2（BM-RC-04-F）/P3（余者等触发）
- 验收标准：BM-RC-04-F 行为基线统计+异常告警落码 testing（fail-visible 不阻断）；余者触发条件达成后按 61 号伪代码施工。

### 17. 44 号 Phase 3 数据期件（挂账跟踪，不抢跑）
- 来源文档：44_premarket_intraday_decision_upgrade.md §7 Phase 3
- 设计声明摘要：M1-③ 相似日推演启用（需 ≥60 交易日快照积累）/M1-④ 实时调度回路生产化/M2 边界修正闭环实盘验证/M3-② 新闻情绪（tracker #138/#139 闭环后）/M3-⑨ 历史 PIT 全量回填（3 个月验证后，~￥25-60）。
- 建议模块落点：已在码（similar_day_inference/intraday_sentiment_loop/boundary_revision_engine/llm_premarket_analysis），本期=数据积累+编排。
- 建议 MOD 号：—（启用/标定动作，非新模块）
- 优先级：P2（数据期）
- 验收标准：快照积累达标后 KNN 启用（walk-forward 命中率 ≥55% 守门）；M2 修正链路实盘留痕复盘；PIT 回填经 Owner 预算批准。

## P3 · 远期/低优先

### 18. 24 号 DynamicCapacityCalculator + #10 PIT 回测框架全规格（待复核）
- 来源文档：24_daban_strategy_detail.md §3.13/§3.14（#3/#7 Phase 5、#4/#11/#12 Phase 3、#10 首批回测前）
- 建议模块落点：`src/zephyr/ex_core/`（daban_* 同族）/回测域
- 建议 MOD 号：**MOD-SIG-082**（容量计算器）；PIT 框架待统筹（backtest 域）
- 优先级：P3（#10 随首批回测窗口提前）
- 验收标准：DynamicCapacityCalculator 落码 testing（容量分层口径入文档真源）；PIT 框架复用 daban_pit_safety 断言链，回测窗口内零 lookahead 实证。

### 19. 23 号情绪周期分层标签器（待复核）+ 22 号残余三小件（待复核）
- 来源文档：23_strategy_correlation_validation.md（分层标签器）；22_sector_rotation_spec.md（水温响应映射/sector_limit_up_ratio 归一/aggregate_capital_nature_to_sector）
- 建议模块落点：`src/zephyr/signal_ashare/` / `src/zephyr/factor/analysis/`
- 建议 MOD 号：**MOD-SIG-083**（分层标签器）/ **MOD-SIG-084**（22 号小件打包）
- 优先级：P3
- 验收标准：grep 复核确认未落后落码 testing；分层标签消费 BM-SEL-23-B 输出；22 号三件与既有 sector_* 口径一致（不重复造轮子，已落地则核销）。

### 20. 26 号六因子矩阵待施工项（待复核）
- 来源文档：26_event_driven_strategy_detail.md（dReport/Jump on PEAD/隔夜趋势/AStockEvent Feed）
- 建议模块落点：`src/zephyr/intelligence/`（event_factor_matrix.py 扩展）
- 建议 MOD 号：**MOD-SIG-085**
- 优先级：P3
- 验收标准：复核 event_factor_matrix.py 覆盖度后补缺落码 testing；因子口径与 §2.4 PEAD Inversion 一致。

### 21. 15 号 DQ_SPECS 八维 check_func 绑定 + Embargo 真日历切换核销（待复核）
- 来源文档：15_data_feature_layer_spec.md（结案未做②③）
- 建议模块落点：`src/zephyr/data_governance/` + `src/zephyr/backtest/core/pit_manager.py`
- 建议 MOD 号：待统筹定号（data_governance 域）
- 优先级：P3（③前置已就绪可顺手核销）
- 验收标准：八维 check_func 实现并注册（抽样跑通出报告）；Embargo 切真交易日历（calendar_event 数据源）+回归测试零新增红。

### 22. 17 号残余四项
- 来源文档：17_special_trading_days_data_assets.md（复核补记①③④⑤）
- 设计声明摘要：akshare hk_trade_calendar 声明残留删除／六条品类注册补登／§5.8 符号一致性双向 gate+expected_market/expected_variety 字段／manual 三类（fomc/major_meeting/stamp_duty）填充。
- 建议模块落点：`src/zephyr/data/implementations/akshare_provider.py` + business_data_categories.yaml + 治理门禁层
- 建议 MOD 号：—（清理/登记/门禁小件，随数据域批）
- 优先级：P3
- 验收标准：声明-实现一致（#ARCH-DATA-002 门禁口径）；品类六条入册；双向 gate 落码 testing；manual 三类填充后 calendar_event 覆盖 12 类。

### 23. 10 号机构级数据维度族（远期）
- 来源文档：10_regime_detector_spec.md §4.7.6/§4.8.5/§4.11.10/§4.12.10（复核补记①②④）
- 设计声明摘要：IV/COT 拥挤度/信用利差/期权异动/CAPE/巴菲特指标/Margin Debt/Put-Call 数据管道+评分；LPPL 赶顶检测；NetworkX 资金图谱 PageRank。
- 建议模块落点：数据域新管道（CTR 流程）→ regime/features
- 建议 MOD 号：待统筹定号（P3 立项时）
- 优先级：P3（个人 A 股中低频口径下边际收益待证，建议逐维立项评审）
- 验收标准：逐维立项裁定书→管道+评分落码 testing→Phase 2 验证器复跑无回归。

### 24. 91 号远期件 + 与 90 号 §10 口径复核（前置）
- 来源文档：91_density_prediction.md；90_methodology_open_questions.md §10/P-2
- 设计声明摘要：08-23 已落密度 MVP 三件套+TCP-RM 轻量（与 90 号「远期不建」裁定存在口径张力）；RWC 最优变体（待 P-2 裁定）/BM-SEL-14 Phase 0 全规格/BM-SEL-15 激活（需模型验证）/QNN（远期）；真实特征接口+训练数据管道（DS-074）。
- 建议模块落点：`src/zephyr/ml_train/implementations/`、`src/zephyr/signal_ashare/`（既有件扩建）
- 建议 MOD 号：待统筹定号（激活时）
- 优先级：P3（前置=Owner 口径确认+密度头真分位数带验证）
- 验收标准：Owner 回写 90/91 号口径（推翻或维持）；密度头 coverage/pinball 真实数据验收通过后 BM-SEL-15 激活评审。

### 25. 51 号 PNG 退役 + §九 BM-RES-02-B/C 契约
- 来源文档：51_panel_experiment_history_mlflow_retirement.md（结案残余）
- 建议模块落点：`src/zephyr/experiment_tracking/adapters/c1_adapter.py` + 契约层
- 建议 MOD 号：—（函数级删除+契约小件）
- 优先级：P3（PNG 退役待 Owner 确认；B/C 重评条件=日均 run≥50）
- 验收标准：Owner 确认后删 _render_nav_png+关联测试；repro_manifest 五字段落盘契约随实验量达标启用。

### 26. 19 号外资行为分析层（远期立项）
- 来源文档：19_northbound_hold_snapshot.md §6.3/§6.5
- 设计声明摘要：个股增减持排名+季度净流入估算（Δ持股×当季 VWAP，pandas 数十行）。
- 建议模块落点：`src/zephyr/alt_data/` 或 signal 族
- 建议 MOD 号：待统筹定号
- 优先级：P3（外资行为因子未立项）
- 验收标准：立项后落码 testing+季度快照驱动产出排名/估算表。

### 27. 66 号 task_board 死信标签联动 + 00_index 版本同步（治理小件打包）
- 来源文档：66_commit_queue_serialization.md（残余 P1 小项）；00_index_trading_decision.md（44 v1.3.0/68 v1.2.1/92 号未入索引）
- 建议模块落点：scripts/task_board.py + 00_index 文档
- 建议 MOD 号：—
- 优先级：P3
- 验收标准：死信任务自动打标签可查；00_index §0 目录/§7.3 与各文档 frontmatter 全量对齐一轮。

## Owner 窗口（禁 AI 自决/需凭据或裁定）

### 28. Owner 裁定/行动四项
- ① **DeepSeek 账户充值**（tracker #253，M3-⑨ 主通道恢复；当前 Qwen 降级链承载）。
- ② **61 号晋升载体裁定**（清单 #5 前置；experiment_tracking vs 注册表状态机）。
- ③ **65 号 #ARCH-AIGOV-001~010**（proposed，铁律#9 待确认：PATH-shim no-verify/secret 双层扫描/幻觉检测/git 四步纪律/对抗式多 agent/AGENTS.md 嵌套/静态分析反馈环/多层 guardrails/图不变量/agentic OWASP）。
- ④ **90 号 P-1~P-5**（Wasserstein 收敛/Conformal 五变体栈/Robust HMM/RL 执行/过拟合检测协议，方向已给）+ **91 号口径确认**（清单 #24 前置）。
- 验收标准：裁定书/凭据落位后对应清单项解锁。

---

## 附：不收录说明（防复提）

- 纯等实盘数据类：34 号参数校准、G04 参数校准（tracker #48）、G07 相关性实测、28 号定位器准确率评估、30 号 cold_start_ratio/score→weight、11 号 Phase 3-5、61 号 Drift Observatory/退役工作流/strategy_archive/冷启动 T0-T2——重评条件未达，来源文档已登记。
- 正式暂缓/远期裁定类：27 号（二批次策略）、15 号 ④⑤、35 号 §6 P0-P4 部分、36 号 QbSD/Vol-Targeting、40 号三项 Phase 项、42 号 TradeLevelCircuitBreaker（CAND-SELL-001）、52 号 CPCV/PBO/CRPS、91 号 QNN、63 号 Leiden/SPC 族、64 号 §12 常驻议题——按各自触发条件评估，不重列。
