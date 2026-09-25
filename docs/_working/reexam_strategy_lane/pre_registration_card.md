---
ttl: task_bound
doc_type: plan
title: 退役/在册策略重考预注册卡（同卷同纪 v1）
session: st-qmine-20260925
lane: LANE-REEXAM
created: '2026-09-25'
schema_version: 1.0.0
---

# 退役/在册策略重考预注册卡（同卷同纪 v1）

> 本卡=重考唯一判据真源。登记时序=先于任何重考跑批（PreRegistrationRegistry 语义：看数据之前锁参，
> 注册后禁覆盖；改参数=作废重开新卡，禁跑中改）。所有阈值一律引用既有 frozen 件，本卡**不自造新数值**；
> 引用不到的项标 "(建议)" 并逐条列出，Owner 可调，调后须回填本卡。
>
> 机器面=下方 `reexam_prereg_params_v1` 代码块：harness 启动时对其做 sha256 并与预注册登记 hash 比对，
> 不一致直接拒绝跑批（防判据漂移）。本卡其余散文=同一参数的出处与不可乐观外推的实测依据。

```yaml
reexam_prereg_params_v1:
  universe:
    stock_pool_caliber: index_constituent_window_union_scd2   # 禁当前快照口径（幸存者偏差）
    daily_window: ['2019-01-04', '2025-09-09']                 # 与 GPU T1 预注册 search_window 同卷
    minute_window: ['2021-09-01', '2025-09-09']                # kline_1min 实测起点 2021-09-01 09:30
    closed_book_from: '2025-09-09'                             # 切点后禁用于校正/定档/调参
    etf_examable: false                                        # 实测 2021-2025 仅 1 只标的，判材料不足
  cost:
    source: config/exam_scale_cost_gate.yaml                   # frozen，禁改
    tiers_bp: [0, 5, 10, 20, 40]
    survival_floor: 0.0
    monotonic_tol: 1.0e-09
    min_days: 60
    turnover_cap_annual_x: 8.0
    days_basis: 244
    engine_caliber: _c4_engine_frozen                          # 佣金2.5bp双边+印花10bp卖+滑点5bp
    primary_objective: cost_adjusted_sharpe
  cpcv:
    splitter: zephyr.backtest.core.cpcv.generate_cpcv_splits   # MOD-BT-001，禁新造切分器
    scorer: zephyr.backtest.core.strategy_cpcv_matrix.build_score_matrix   # MOD-BT-028
    n_groups: 6
    k_test: 2                                                   # C(6,2)=15 折
    t1_horizon_daily: 20                                        # 标签末端 i+20 交易日
    t1_horizon_minute: 5
    embargo_days: 5
  thresholds:
    haircut_sharpe_min: 0.0            # 严格 >0（=原始 SR 越过多重检验临界值）
    dsr_min: 0.95                      # = 仓内 DSR_SIGNIFICANCE_THRESHOLD（MOD-SIM-024）
    pbo_max: 0.50                      # = 仓内 DSR_OVERFITTING_FLOOR 同数值锚；外部证据见散文 §九
    wfe_min: 0.50                      # Pardo 行业线（17 号文 §三.2 已替换自造 30% 线）
    lb_decay_internal_max: 0.30        # 内控更严线，双轨并行披露（17 号文 §三.2）
    cost_gate_required: true
  verdict_labels: [REVIVAL_CANDIDATE, RETAIN_RETIRED, INSUFFICIENT_MATERIAL]
  batch:
    batch_cap: 40
    omp_threads: 2
    gpu_allowed: false
    resume: per_candidate_state_yaml
  negatives:
    out_subdir: runs
    require_header_when_empty: true
    count_into_n_trial_ledger: true
```

## 一、纪律三条（真源=docs/_working/decision_map_campaign/05_t0_and_strategy_library.md §二）

1. **同卷同纪**：重开预注册，禁套旧成绩——本卡所有指标一律由本卡定义的管线**重算**；历史 manifest /
   历史 sharpe 列仅作观察披露，禁作判据输入。
2. **限额分批**：先在册 candidate，退役外部池按族分批封顶（每批 ≤ batch_cap）。
3. **机制门槛+试用期**：过复活线=获"模拟盘试用"资格，**不直接转正**（转正归 Owner 门位）。

## 二、宇宙与时间窗（实测锚定，禁乐观外推）

探针日志=`.runtime/logs/lane_reexam_data_probe.log`（2026-09-25 本车道实测，ch_reader 只读，表名经 TableRegistry）。

| 项 | 冻结值 | 实测依据 |
|---|---|---|
| 主考试窗（日线族） | 2019-01-04 → 2025-09-09 | 与 GPU T1 预注册 search_window 同卷（config/search_space_prereg.yaml tracks.f06_grid） |
| 闭卷段 | > 2025-09-09 | 全仓 PIT/闭卷切点 |
| 分钟族窗 | 2021-09-01 → 2025-09-09 | kline_1min min=2021-09-01 09:30:00+08:00，max=2026-09-24，1,482,319,643 行；年度广度 2021=4,452 → 2026=5,591 只 |
| ETF 族 | **本窗不可考**（INSUFFICIENT_MATERIAL，非判负） | kline_etf_daily 2021-03-08→2025-12-31 仅 1 只标的（159865，1,172 行）；1,675 只批量仅 2026 年落地——`_c4_engine.ETF_START=2021-04-01` 假设今日实测**不成立**（漂移待治理，非本车道施工面） |

**诚实上限（每份报告头必披露）**：日线库虽 1990-12-19 起有行，但 2019 年前是约 230-240 只的存根宇宙
（kline_daily 实测 2014=228 / 2015=235 / 2016=231 / 2017=237 / 2018=237 → 2019=3,771；
stk_limit 同形 2015=239…2018=237 → 2019=3,770）。**任何早于 2019-01-04 的窗都不构成全市场考核**，
本卡一律不采用；Owner 若要求拉长历史窗，须另立卡并明示"结论只代表存根宇宙"。

## 三、成本档（引用 frozen 件，禁改）

真源 = `config/exam_scale_cost_gate.yaml`（E4 考尺成本门预注册参数，冻结件，本卡逐字段照抄不重定义）。
引擎成本口径 = `_c4_engine` 冻结土规；滑点档仅作侧向扫描覆盖，禁把成本档当搜索轴
（search_space_prereg.yaml：`I_cost_tier active_if=False 恒折叠`）。

## 四、切分器（CPCV）与试次 N

复用 `generate_cpcv_splits`（MOD-BT-001，purge+embargo 已有 tests/backtest/test_cpcv.py 覆盖）+
`build_score_matrix`（MOD-BT-028），**本车道不新造切分器、不新造打分器**。

- n_groups=6 / k_test=2 → C(6,2)=15 折：主窗约 1,620 交易日 ⇒ 每组 270 日、test 并集 540 日
  ≥ min_days(60) 的 9 倍，且逐策略纯统计开销可控（实测 1 策略 5.5 年窗 build+回测 19.3s）。
- t1 = i + 20 交易日（在册 candidate 136/139 为日线"波段"，20 日=月度持仓上界）；embargo=5 日。
- 试次 N = `n_trial_ledger.TrialLedger` 累计可审计试验数 **+** 本批卷内同池策略数（卷内互比=真实搜索宽度）；
  每批跑完立即 `record_run` 入账（漏计=DSR 分母污染=科学造假）。

## 五、判据（多重检验三件套，逐格报告）

三件套全部**委托既有件**，本车道只新增 Harvey-Liu haircut 一件（数学落 MOD-SIM-024；DSR/PBO 禁另写公式）：

| # | 指标 | 实现真源 | 复活线 |
|---|---|---|---|
| 1 | Haircut Sharpe（Harvey & Liu 2015 JPM；HTL Bonferroni 加权） | 新增 `deflated_sharpe_calculator.haircut_sharpe_harvey_liu`（与本卡同步登记） | haircut_sharpe > 0（非线性：强信号轻罚、边缘信号重罚） |
| 2 | DSR（Bailey & López de Prado 2014） | `deflated_sharpe_from_moments`（MOD-SIM-024 全仓唯一真源） | DSR ≥ 0.95；degenerate=True 恒判不显著（fail-closed） |
| 3 | PBO（Bailey/Borwein/López de Prado/Zhu，JCF 20(4)） | `cpcv.compute_pbo`（MOD-BT-001） | PBO ≤ 0.50 |
| 辅 | 成本三门 | `exam_cost_gate.evaluate_exam_cost_gate` | 五档单调非增 ∧ 40bp 档 sharpe ≥ 0 ∧ 年换手 ≤ 8x ∧ 天数 ≥ 60 |
| 辅 | WFE（Pardo 线） | `overfitting_guard.walk_forward_efficiency` | OOS/IS ≥ 50%；另双轨披露 Wilson LB 衰减 ≤30% 内控线 |

**判档口径**：三件套 + 成本三门全过 = `REVIVAL_CANDIDATE`（仅试用资格）；任一不过 = `RETAIN_RETIRED`
并落 negatives；材料/数据不足 = `INSUFFICIENT_MATERIAL`，单列**禁混入判负**（防把"没测到"说成"测不过"）。
逐格出数字证据，禁"全绿"表述。

**禁调参过谁**：本节任何阈值改动=判据变更，须 (a) 改本卡并升 schema_version，(b) 重开新预注册，
(c) 旧卡成绩全部作废。

## 六、负结果归档纪律

1. 每一落榜格写 `runs/<batch_id>/negatives.csv`（带表头；零阴性也不许空文件——下游 pd.read_csv 会得单匿名列）。
   列：batch_id / candidate_id / scope / failed_criterion / measured / window / caliber / generated_at。
2. 负结果**计入** N 账本（禁删改禁挑样）。
3. 主效应前 20% 之外的格一律如实入账（17 号文 §一 负结果纪律）。
4. 落盘位置 `docs/_working/reexam_strategy_lane/runs/<batch_id>/`，格式仅 .md/.csv/.yaml（DCR-005/006 契约）。

## 七、分批封顶与可断点

batch_cap=40 条/批（实测单策略 19.3s + 15 折纯统计 ⇒ 40 条 ≈ 20 分钟；RAM 余 19.3GB 下逐条串行、
`OMP_NUM_THREADS=2`）；断点续跑=已完成 candidate_id 入 `runs/<batch_id>/state.yaml`，重跑自动跳过，
禁静默重算覆盖已判格。**禁 GPU 作业（T1 独占 36h）**。

## 八、册内/册外账本实测对账（摸底结论，禁抄文档计数）

| 账本 | 文档口径 | 本车道实测 | 差异处置 |
|---|---|---|---|
| 在册策略 REG-STR-001 | 161=19 active+139 candidate+3 deprecated | **161/19/139/3 精确吻合**（yaml Counter 实测，registry last_updated 2026-09-13）；真路径=`docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml` | 09 号文环节 6② 写成 `config/strategy_registry.yaml`——**该文件不存在**（文档漂移，列治理项） |
| 139 candidate 可执行性 | — | **code_path 非空=0 条 / distilled_to_code=True=0 条**，139/139 仅 doc_ref 散文规则，baseline_* 全 null | **在册 candidate 当前不可直接考试**：须先过翻译/蒸馏件（hypothesis_translator + SOP-C 翻译轨）产出 build() 契约件。首考因此改用"已可执行的外部池代理批"（§十） |
| 聚宽出局池 | 322 行机读 | c4_deferrals.csv **记录数=321**（+表头=322 文本行）；md5 全量可回对 raw_manifest（597 行 / 556 唯一 md5，含重复）；其中**有译文代码可跑的仅 13 条**（85 个 c4_*.py ∩ 出局 md5） | 按可执行子集分批。defer_reason=可考性地图：fundamental_gate 112 / non_pv_class 112 / intraday_signal 43 / not_strategy 21 / northbound_gap 7 / 其余 26 |
| 潘潘并入宿主 | 159 条 | 逐条**不可机读枚举**：strategy+factor 两册合计 aliases 268 串 / 152 条目含 alias / 76 条目 doc_ref 标"吸收"，无一等于 159；memo29 §汇总仅散文记 159 | 沿用附录A 既有语义：**重考=对宿主条目做分状态复验，非逐条复活**；本卡不另造枚举口径 |
| strategy_archive | 机制已建零触发 | 目录在，仅 README（零归档） | 无归档可考，等首个真退役触发 |

## 九、外部方法学出处（URL + 发布方 + 年份；关键结论 ≥2 独立来源）

- **haircut 非线性、明确反对一刀切折扣**（关键结论·来源 1）：Man Group Insights "Backtesting"
  https://www.man.com/insights/backtesting （发布方 Man Group；引 Harvey & Liu 2015）——
  原文立场 "it is a serious mistake to use the rule of thumb 50% haircut"，校正量非线性
  （强信号轻罚、边缘重罚），路径=SR→t 比→按搜索次数调 p 值→回映射 SR。
- **同族校正的对表与反证**（关键结论·来源 2）：Chen, A.Y.（2022 v1 / 2025 v10）
  "Most claimed statistical findings in cross-sectional return predictability are likely true"，
  arXiv:2206.15365 https://arxiv.org/abs/2206.15365 ——以 Harvey-Liu-Zhu HTL 一族为对表基准，
  给出 FDR≤25% / ≤9% 界。**该文同时是"校正幅度仍有争议"的诚实反证**，故本卡不把任何校正倍数当常数，
  只做逐件校正计算。
- **原始文献**：Harvey & Liu（2015）"Backtesting", Journal of Portfolio Management（haircut Sharpe）；
  Harvey, Liu & Zhu（2016）"…and the Cross-Section of Expected Returns", Review of Financial Studies
  （HTL Bonferroni 加权，本卡 haircut 实现即此式）。
- **DSR**：Bailey & López de Prado（2014）"The Deflated Sharpe Ratio", Journal of Portfolio Management
  40(5), 94–107 ——独立转引核实=arXiv:2608.27734 参考清单。
- **PBO/CSCV**：Bailey, Borwein, López de Prado & Zhu（2014/2017），Journal of Computational Finance
  20(4), 39–69 ——独立转引核实同上。
- **最新可复核证据**：Gençay, E.（2026）"What survives honest evaluation? Leakage-safe, search-aware
  assessment of LLM-driven trading strategy discovery", arXiv:2608.27734 https://arxiv.org/abs/2608.27734
  ——实测锚：IS sharpe 1.69 按 102 次搜索 deflate 后 OOS=0.18；认证线 DSR≥0.95；PBO>0.50 一致预示
  样本外退化；LLM 发现策略零存活。并警示 **故意渗漏（leaky oracle，sharpe 35）仍能骗过统计校正**——
  故本卡把 PIT/闭卷结构护栏列为统计判据的**前置条件**，不因有三件套就放松闭卷。
- **IS-WFA-OOS 三段协议**（WFE 报告面辅证）：Pham, Chan Nguyen & Nguyen Thi（2026）
  "AlgoXpert Alpha Research Framework. A Rigorous IS-WFA-OOS Protocol for Mitigating Overfitting",
  arXiv:2603.09219 https://arxiv.org/abs/2603.09219 。
- **未复核项如实记录**：18 号文所引 "Nefedov (2025 SSRN) 天真评估虚增年化夏普约 3.6 倍" ——本车道
  多轮检索（SSRN 站点限定 + 关键词限定）**查无独立来源复核**。处置=**本卡不采用 3.6× 常数**，
  改用可复核实测锚（上条 1.69→0.18 + 本仓自测数字）；18 号文该条建议 Owner 降级为"未复核引述"。

## 十、首考卷定义（本卡签发即锁）

- 代理批 `p1_translated_jq_outpool`：真源池 = `scripts/backtest/translated/` 中 c4_*.py 译件里
  **md5 ∈ 聚宽出局账本且含 build() 契约**的 13 条 ∪ `ibt_mining_matrix.POOL` 17 条，去重后 ≤30 条——
  当前全仓唯一"出局可机读回溯 + 代码可执行"的重考面。
- 卷=§二 主窗，成本=§三，切分=§四，判据=§五，负结果=§六。
- 首考目的=证明 harness 端到端可跑 + 出第一份逐格三件套成绩单，**不为产出复活名单**
  （candidate 蒸馏缺口未闭合前，任何复活建议都属越权）。
