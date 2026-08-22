---
ttl: task_bound
---

# 长城任务施工进度核对报告（2026-08-23）

> **定位**：进度对账快照——回答"长城任务的两阶段主体施工清单当前真实进度如何"。
> **口径**：本报告只做核对不施工；逐项以代码实体/测试/注册表/治理留痕为证据，防凭记忆报数。
> **方法**：5 路并行只读核查（审查清单第一批/P1 批、板块大盘专项、44号文 M1/M2/M3、09号文 GP0~GP3），逐件给到文件路径+类/函数实证。

---

## 0. 一句话总判

**两份阶段二文档的施工项全部落地（INT-01 最后 2 处硬编码已于 2026-08-23 收官批收敛清零），阶段三 AI 层 GP0 确定性件已全量落地并经 M0 终审宣布达成；GP1/GP2/GP3 按纪律未抢建（结构性阻塞）。** 长城任务的"主体施工"层面已收官，残余全部是"数据期积累/实盘验证/Owner 窗口/前端批接线"性质，无代码缺口。

---

## 1. 阶段二 · 审查清单（architecture_review_2026_08_module_upgrade_audit.md）

§10.2/§11.5 施工单逐项核对：

| # | 施工项 | 结论 | 证据 |
|---|---|---|---|
| INT-01 | 硬编码路径收敛 | ✅ **已闭环（2026-08-23 收官批）** | 9 处已改 `get_service_secret`/`find_repo_root`；`config/.env.qmt` 有 `QMT_SIM_PATH`、`secret_registry.yaml` 有 `TDX_PLUGIN_DIR`。收官批补最后 2 处：`start_scheduler.ps1:41` 仓根改 `Split-Path -Parent $PSScriptRoot`；`data_sources_registry.yaml:404` 通达信路径改 `${TDX_PLUGIN_DIR}` 占位（policies.yaml 由 generate_policies.py 重派生同步）。src/ 残留扫描确认无活跃裸硬编码执行路径 |
| RUN-05 | 彩排断网断电断点恢复演练 | ➡️ 移交 P0-5（不单独施工） | 按 §10.3 移交项处理 |
| STR-03 | simulation 包命名注记 | ✅ 已落地 | `simulation/__init__.py:45` 命名消歧注记 |
| ALG-06 | 爬虫源禁盘中纪律注记 | ✅ 已落地 | `64_data_source_download_spec.md:612` §9.1 注记 |
| ALG-04 | 情绪因子非对称使用口径 | ✅ 已落地 | `28_sentiment_cycle_trading.md:603` + `26_event_driven_strategy_detail.md:555` |
| ALG-01 | regime 横截面结构特征 | ✅ 已落地 | `regime/cross_sectional_features.py`（MOD-REGIME-007）4 特征+`regime_feature_builder.py:153` 开关默认关+18 测试+A/B 报告在案 |
| ALG-02 | WFA 参数稳定区+灾难否决 | ✅ 已落地 | `param_analyzer.py:463 select_plateau_param`（默认关）+ `decision_gate.py:282 check_wfa_stage` 灾难否决（既有件复用，按 92号§5.2 实证纠偏裁定） |
| ALG-03 | 因子研究案例库 | ✅ 已落地 | `factor/casebook/casebook.py`（MOD-L02-027）schema+record_case/query_similar；`.db` 惰性建库（设计内运行时产物）；testing 封顶 |
| INT-03 | trading 主进程看门狗 | ✅ 已落地 | `scripts/start_trading.ps1` while-true 全套 + `register_guard_tasks.ps1:100-129` Disabled 注册块（翻开=Owner 窗口） |
| STR-01 | 空壳/0-node 域 dormant 标注 | ✅ 已落地 | 42 文件 DORMANT docstring（6 包）+ #248 的 42 处 MATURITY→design（752e913e64）双工作流均施工；research 按 #ARCH-143 R4 纪律合法摘除（已有 evidence 真实子包） |
| STR-02 | 38 处 NotImplementedError 分类 | ✅ 已落地 | `2026-08-22-notimplementederror-classification.md`：29 处/19 文件全分类（合法免责 13/deferred 13/历史注记 3），CAND-SEC-002/003 登记 |
| STR-04 | 治理层不新建 | ✅ 纪律项（无施工） | I-GOV-3 v2 年检纪律覆盖 |

**板块/大盘专项（§11.5）**：

| # | 施工项 | 结论 | 证据 |
|---|---|---|---|
| SEC-01 | 板块盘后全景报告器 | ✅ 已落地 | `data/sector_report_builder.py`（MOD-L00-009）编排 6 库模块→Top10 榜+资金流+5状态+主线候选 |
| SEC-02 | 盘中板块实时聚合器 | ✅ 已落地 | `data/sector_intraday_aggregator.py`（MOD-DATA-061），挂接 `intraday_sentiment_loop.py:368`（与 M1-④ 共载体） |
| SEC-03 | 分歧概率标定器 | ✅ 已落地（并入 M1-⑩） | `signal_ashare/sector_divergence.py:1000 _calibrate_states` 5状态×3/5日条件频率 |
| SEC-04 | 龙头识别四档 | ✅ 已落地 | `signal_ashare/sector_leader.py`（MOD-SIG-062）龙头/中军/跟风/中位股四档 1.5/1.2/0.8/0 |
| SEC-05 | 主线候选榜 | ✅ 已落地（盘后榜） | `signal_ashare/mainline_candidates.py`（MOD-SIG-061）score≥2 取 Top3-5，已被 SEC-01 消费；盘中修正接线预留（设计内） |
| IDX-01 | 四指数 regime 面板 | ✅ 已落地 | `regime/index_regime_panel.py`（MOD-REGIME-008）1 引擎×4 代理（000300/000001/399006/000688）7 态概率+强弱排序+背离警示；不建点预测 |
| IDX-02 | Dashboard 四指数卡+板块页 | ✅ 前端原型层已落地 | `2026-08-20-dashboard-mockup.html` 四指数卡+板块页（Top10 主线/梯队/8维详情）；**真实数据接线待前端批**（mockup:465 自述占位） |

**前端展示清单（§12.1 Part A，D-01~D-07）**：归前端批统一落地，其中 D-07 大盘情绪面板排 44号文分期。

---

## 2. 阶段二 · 44号文（44_premarket_intraday_decision_upgrade.md）

M1/M2/M3 全 17 关键件逐项实证——**全部有真实代码实体，零"未施工"、零"仅骨架"**：

| # | 施工项 | 结论 | 证据 |
|---|---|---|---|
| M1-① | 涨跌加速度三件套 | ✅ 代码落地（数据期兜底） | `market_sentiment_analyzer.py:745 analyze_breadth_acceleration`；zscore 统计待数据期供给 |
| M1-② | 护盘/风格失真三通道 | ✅ 代码落地 | `detect_distortion`（a/b 通道本模块）+ `sector_divergence.py:930 _compute_rs_radar`（c 通道合并施工） |
| M1-③ | KNN 剩余走势推演 | ✅ 代码落地（数据期兜底） | `similar_day_inference.py:283 infer_remaining_session`（MOD-SIG-063）D<60 恒走五阶段先验兜底 |
| M1-④ | 实时调度回路 | ✅ 代码落地 | `intraday_sentiment_loop.py:332 run_once`（MOD-DATA-063）落 prediction_log |
| M1-⑤ | 量能盘中预测 | ✅ 代码落地（数据期兜底） | `forecast_volume:919`；p̄(t) 曲线待数据期供给 |
| M1-⑥ | 大幅回撤个股数 | ✅ 代码落地 | `count_large_drawdowns:951` |
| M1-⑦ | 昨日破板今表现 | ✅ 代码落地 | `track_broken_boards:980`（K线×stk_limit 联算口径） |
| M1-⑧ | 期指基差情绪 | ✅ 代码落地（部分数据期） | `futures_basis_monitor.py:489 compute_futures_basis`（MOD-SIG-058）；basis_vel 暂日频代理 d1_proxy（分钟腿未配置） |
| M1-⑨ | 期权情绪三件套 | ✅ 代码落地（降级口径留痕） | `option_sentiment.py:488 compute_option_sentiment`（MOD-SIG-059）；PCR 成交量口径（无 OI 列） |
| M1-⑩ | 板块分歧+速度计+个股分歧 | ✅ 代码落地（数据期兜底） | `sector_divergence.py:1075 compute_sector_divergence`（MOD-SIG-060）；250日窗 insufficient 降级 |
| M2 | 边界修正通道 | ✅ 代码落地 | `plan_engine/boundary_revision_engine.py:523`（MOD-PLAN-006）14:00/14:45 双时点+防抖15min+冷却+档位映射，挂接 `tomorrow_boundary_planner.py:90 apply_revision` |
| M3-① | 外盘四通道→gap_adj | ✅ 代码落地 | `overnight_boundary_reviser.py:295 _compute_gap_adj`（MOD-PLAN-002 增量）；A50/ES/NQ/日韩占位 None（数据源缺口） |
| M3-③ | 多情景+竞价三细节 | ✅ 代码落地 | `scenario_planner.py:262`（MOD-PLAN-005）D1 偏离/D2 量放/D3 撤单识别 |
| M3-⑤ | 龙虎榜盘后溢价 | ✅ 代码落地 | `lhb_premium_analyzer.py:335`（MOD-SIG-057）三名单+独食/一日游降权 |
| M3-⑦ | 盘后资金面四件套 | ✅ 代码落地 | `overnight_boundary_reviser.py:352 _compute_fund_score` 合成+确认/否决 |
| M3-⑧ | 事件日历联动 | ✅ 代码落地 | `overnight_boundary_reviser.py:467 _compute_event_flags`，fail-open |
| M3-⑨ | LLM 盘前分析 | ✅ 代码落地（数据期兜底） | `plan_engine/llm_premarket_analysis.py`（MOD-PLAN-007）llm_daily_analysis 表 DDL+PIT 双护栏+v1/v2 模式；`llm_client=None` 常态 skipped_not_wired 留痕 |

**44号文 §7 自标核对**：Phase 1/2 已落地 testing 封顶 ✅ 属实；Phase 3 数据期项代码已落兜底分支、数据积累待实盘 ✅ 属实。

---

## 3. 阶段三 · 09号文 AI 层（09_ai_architecture）

**GP0 确定性件已全量落地，M0 于 2026-08-22 Owner 终审宣布达成**（E0-1~E0-8 全绿，E2E 两轮零问题 4941 绿+4360 绿）：

| GP0 件 | 落地 | 证据 |
|---|---|---|
| llm_runtime_gateway（10号，登记对账网关） | ✅ testing→stable | `integration/llm_runtime_gateway.py`（MOD-INF-051）DeepSeek/Qwen/Ollama 三通道+llm_call_log 登记+reconcile_daily_calls 对账+LSG fail-closed；**预算硬门/路由级联属 GP1 明确未做** |
| 提交队列 MVP（08号 E0-1） | ✅ 已落地，flag 开启 | `scripts/commit_queue.py`（MOD-GOV-046）+ `commit_queue_landing.py`，`config/flags.yaml commit_queue_serializer.enabled: true` |
| Context Engine（07号） | ✅ 三段 production | `autonomy_core/context/` 39 文件四段管道；**inject 段数据源未接线（已知空段，归 GP1 Phase 1）** |
| 证据关联组件（11号 E0-6） | ✅ testing | `research/evidence/` 四件（hypothesis_registry/evidence_chain/iteration_guide/batch_entry） |
| capability_passport+task_gate（06号） | ✅ production | `intelligence/model_profiling/` 18 文件+`trading/task_gate.py` |
| LSG 主链路（09号 E0-2） | ✅ | `integration/local_model/lsg_gate.py`（MOD-INF-052）fail-closed |
| 三分类 gate+KS 编排（15号 E0-3） | ✅ | `autonomy_boundary_gate.py`+`kill_switch_orchestrator.py`，P95<1ms |
| 事件流+TNR（16号 E0-4） | ✅ | `security/security_event_bus.py` 四域 adapter |
| L1 反思+模块工厂 SOP（12/13号 E0-6） | ✅ | `intelligence/reflexion/`+`19_module_factory_manual_sop.md` active |
| 四类薄入口（14号 E0-7） | ✅ testing | `autonomy_core/agents/` 四 entry（产出 100% human_gated） |
| 域边界裁定（03号 E0-8） | ✅ 已闭环 | 选项C 混合方案，03号文 active v0.3.0（#ARCH-169） |

**GP1/GP2/GP3 结构性阻塞（未施工，符合纪律）**：GP1 半自动（gateway 预算硬门/CE inject 接线/Drift 防护/技能库等）零代码，18号文 §7 明文"不抢"；GP2 进入条件 I2-2/I2-3 要求 Phase 0/1 production（当前仅 testing→stable，production 启用留 Owner 窗口 B-007）；GP3 远期 P4 锁定 ICL 路线不承诺时间表。**无越期施工证据。**

---

## 4. 残余项汇总（全部非代码缺口）

| 类别 | 项 | 性质 |
|---|---|---|
| **代码小尾巴** | ~~INT-01 硬编码~~ | ✅ 已清零（2026-08-23 收官批） |
| **前端接线** | IDX-02 四指数卡/板块页真实数据接入（消费 IDX-01/SEC-01/02） | 归前端批，mockup 已占位 |
| **CE inject 段** | context_injector 生产数据源接线（UnifiedMemoryAPI） | 归 GP1 Phase 1 |
| **数据期积累** | M1-①③⑤⑧⑨⑩ 的统计窗/命中率/分钟腿供给 | 需实盘数据积累，兜底分支已在 |
| **Owner 窗口** | DeepSeek 402 充值（#253）/trading watchdog 翻开/production 启用审批（B-007）/M3-⑨ API key+预算 | 人工行动项 |
| **移交项** | RUN-05 断点恢复演练（P0-5）/INT-02/INT-04（P0-5）/ALG-05（CAND-MKTDATA-001） | 归在途批 |

---

## 5. 结论与建议

**长城任务"主体施工"层面已基本收官**：阶段二两份文档施工项 ≈ 全落地（唯一真代码尾巴=INT-01 两处硬编码），阶段三 GP0 已 M0 终审达成，GP1+ 按纪律未抢建。

**"连续两次测试问题=0"判定参考**：阶段三 GP0 已实证 E2E 两轮零问题（4941 绿+4360 绿）；阶段二各模块均带配套 pytest 且关联域复跑零新增红。

**建议 Owner 裁定的下一步**（三选一）：
1. **认定收官**——主体施工已实证落地，仅清理 INT-01 两处硬编码尾巴 + 收尾登记，长城任务正式结束；
2. **补 INT-01 尾巴 + 一轮全量 E2E 复跑**——把最后两处硬编码收敛，再跑一次全量测试双确认后收官；
3. **转数据期/Owner 窗口项**——主体不动，转处理残余的实盘验证与审批项。

> 本报告为 2026-08-23 核对快照；施工状态 SSoT 仍以 construction_progress_tracker.md 为准。
