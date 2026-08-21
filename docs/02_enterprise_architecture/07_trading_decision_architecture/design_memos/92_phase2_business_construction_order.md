---
ttl: permanent
doc_type: architecture_view
title: 阶段二业务层施工顺序清单（44 号升级 + 2026-08 架构审查升级项）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-22
topic: phase2_business_construction_order
scope: 07_trading_decision_architecture
completes_when: "阶段二全部波次施工、测试、提交闭环后归档（归档不删除，保留审计链）"
---

# 阶段二业务层施工顺序清单（92 号）

> **性质**：施工排序清单——Owner 2026-08-22 指令（长城任务任务一）驱动，将 [44_premarket_intraday_decision_upgrade.md](44_premarket_intraday_decision_upgrade.md)（M1/M2/M3/M4 全组）与 [architecture_review_2026_08_module_upgrade_audit.md](architecture_review_2026_08_module_upgrade_audit.md)（INT/STR/ALG/SEC/IDX 族）的全部施工内容按依赖与冲突面排序成波次，作为并发施工派单真源。
> **前置状态实证（2026-08-22）**：P0 批全闭环（tracker #232-#244）；残余四项专项批闭环（#61/#62/#63）；提交队列 MVP 已落且 flag 已翻开（#240，dev 写入强制串行化）；P0-4② calendar_event 回填已实证在库（#237，396 行 9 类）；44 号 CAND 登记的缓办条件（残余批任务4闭环）已达成。44 号"全组排 P0 目标态之后"的前置已满足，Owner 指令即开工令。
> **真源分工**：算法公式/阈值以 44 号 §9 与审查报告 §10.2/§11.5 为真源，本文只做排序、施工面划分、实证分支裁定与验收口径，不复制算法伪代码。

## 1. 数据实证结论（2026-08-22 统筹实测，施工分支裁定依据）

对 ClickHouse c1_market 直查（探针脚本 .runtime/_p2_data_probe*.py，用后已删）：

| 数据 | 实测 | 对施工的分支裁定 |
|---|---|---|
| option_iv_surface | ✅ 27,881 行（2026-01-29~08-20）；510050/510300 各 ~3,700 行；含 iv/delta/gamma；**无 OI 持仓列** | M1-⑨ 走**接入分支（降级模式）**：IV Rank 用可用窗（≥60 交易日守卫，不足标 degraded）；持仓 PCR 缺 OI→先实证 option_kline 有无 OI，无则用成交量 PCR 替代并标注；Skew 用 25Δ 沽购 IV 差可算（delta 列在） |
| kline_futures | 🟧 实测 55,939 行（2026-08-03~08-20），IF/IC/IM/IH 各仅 12 行；表内容混入了大量个股 symbol——与 44 号"311 万行 2010-2026"认知漂移 | **登记数据域核查项**（表漂移待数据域归因）；M1-⑧ 期货价腿按"重新配置采集"施工：tasks.yaml 补 IF/IC/IM/IH 主力连续日频（akshare futures_main_sina 回补）+ miniqmt 盘中分钟采集 symbols |
| futures_kline_qmt | ❌ 814 行≈空转，symbols 未配 | M1-⑧/M3-⑥ 唯一硬缺口坐实，波 4 第一项=采集配置 |
| index_quote / auction_book | ✅ 154,024 行至 08-21 / ✅ 1,461,598 行（07-21 起，五档+涨跌停价+昨收全字段） | 基差现货腿、M3-③ 竞价消费数据就绪 |
| us_index | 🟧 19 行（07-24 起）且 **symbol 列空值**（OHLCV 值正常，疑 tickflow 近批 ingestion 缺陷） | M3-①a 模块按"最新可得序列"消费+degraded 标注不阻塞；symbol 空值缺陷登记数据域修复项 |
| margin_trading / money_flow / block_trade×2 / dragon_tiger_seat | ✅ 51,118 / 110,754 / 443+615 / 608,342（2022 起）行 | M3-⑦/M3-⑤ 纯消费接入，零前置 |
| calendar_event | ✅ 396 行 9 类（fomc/major_meeting/stamp_duty 3 类 manual 未填充） | M3-⑧ 直接消费；44 号"写入任务未注册"表述已过时（tasks.yaml:1821 已注册）——fail-open 兜底按 §9.12 设计保留 |
| 五指数（000001/399001/399006/000688/000300） | ✅ kline_index 全部在库（1990 起，至 08-19） | IDX-01 前置检查项关闭 |
| stk_limit / limit_up_down | ✅ 83,263 行 / 1,847 行；**stk_limit 无"曾涨停"字段**（44 号表述漂移）；limit_up_down.limit_type 仅'涨停/跌停'无炸板类 | M1-⑥⑦炸板判定=K线×stk_limit 联算（high≥limit_up 且 close<limit_up=炸板），纯计算 |
| 全市场分钟快照 / llm_daily_analysis / prediction_log | ❌ 均不存在 | M1-④ 新建 market_breadth_snapshot 表（DDL-as-Code+data_asset_registry）；M3-⑨/M4-② 新表属施工产物 |
| adj_factor / stock_basic / kline_1min / kline_sector_880 / kline_sector_intraday | ✅ 21,054,652 / 26,048 / 14.5 亿 / 24,981 / 710 万行 | 复权/universe/分钟计算/板块计算地基全部就绪 |

## 2. 统筹自主裁定记录（Owner 离场授权，留复核）

| # | 裁定项 | 裁定结果 | 理由（第一性原理） |
|---|---|---|---|
| D1 | 施工隔离方式 | **主工作区文件级隔离并行**，不开 session_worktree | 提交队列已强制串行化 dev 写入（#240），并发事故根因（多会话整文件覆写）已被队列+即时提交纪律覆盖；worktree merge 冲突处置成本（P1-补17 实证 9 路串行 merge）远大于当前单统筹+文件级划面的风险；派单明确文件清单+每批提交前 git status 审查替代物理隔离 |
| D2 | DB 写/DDL 类 Owner 窗口项 | 按 Owner"自己裁定"授权执行，逐项登记本文留复核 | 新表均为新增非破坏（不改既有表 schema）；风险方向可逆（删表即回滚） |
| D3 | INT-03 trading 看门狗 | 脚本+测试全施工；**计划任务注册为 disabled 态**（RestartMiniQmt disable 先例） | 实证 AutoRuntimeCore 当前无常驻生产进程在跑，注册 enabled 看门狗会拉起本不在跑的交易进程=生产行为变更；disabled 保留恢复可能，翻开=Owner 一键 |
| D4 | M1-⑨ 期权分支 | 接入分支+降级模式（D1 表已裁） | 数据 7 个月可用，250 日窗不足不是不做的理由——华泰范式价值在 PCR/IV 极端分位，可用窗分位同样表达极端 |
| D5 | M3-⑨ 分拆施工 | 核心件（打包器/prompt/契约/表）在阶段二波 5；LLM 接线在阶段三 gateway 后 | 44 号自明前置=10 号 llm_runtime_gateway（阶段三 GP0 件）；拆分不违"全量施工"——两阶段是同一长城任务 |
| D6 | IDX-02 前端接入 | **移交前端会话**，本批不碰 | Owner 明令另一对话在做前端（docs/_working/2026-08-20-* 为其施工面）；SEC/IDX 输出落 DB/报告文件即天然可被前端消费，无耦合损失 |
| D7 | 新模块成熟度 | 一律 testing 封顶（宪章 B-007），production 启用留 Owner | 既有铁律 |
| D8 | M3-④ 日韩数据 | 波 5 接口评估，akshare 接口不顺即砍（44 号裁定三授权） | 跟随盘价值最低，不恋战 |
| D9 | 03 号文域边界 Owner 裁定（阶段三 E0-8） | 登记+跳过 | 人工裁定项，非施工可解 |
| D10 | AGENTS.md 速查联动（M4-①） | MVP=registry_of_logs.yaml 登记表+校验脚本；AGENTS.md 改动走 Owner 审批通道（PROTECTED） | PROTECTED-PATHS 硬边界不绕 |
| D11 | 44 号 §6 文档漂移 | 随批修订 44 号（auction_book 已启用/calendar_event 任务已注册/stk_limit 无曾涨停字段/kline_futures 行数漂移 4 处实证更正） | 文档-真源漂移防AI误读（D1 查重纪律同族） |

## 3. 施工波次总表

| 波 | 内容 | 并行度 | 依赖 |
|---|---|---|---|
| 波 0 | 统筹自施：数据实证（已闭环）+ 44 号 CAND 三（CAND-SIG M1 全组/CAND-PLAN-001 M2/CAND-PLAN-002 M3）+ 审查报告新增项 CAND 补登 + secret_registry（qwen key）提交 | 统筹串行 | 无 |
| 波 1 | 文档注记+小切口：INT-01 硬编码路径收敛 / STR-03 simulation 命名注记 / ALG-06 爬虫源禁盘中注记 / ALG-04 情绪非对称口径 | 4 并行 | 零冲突 |
| 波 2 | P1 算法基建：ALG-01 regime 横截面特征 / ALG-02 参数稳定区 / ALG-03 因子案例库 / INT-03 trading 看门狗 / STR-01 dormant 标注 / STR-02 NotImplementedError 分类 | 6 并行（按域隔离） | 波 1 |
| 波 3 | 44 号 Phase 1：M1 情绪增量包（①②a/b⑤⑥⑦）/ M3 盘前包（①a⑦⑧）/ M3-⑤ 龙虎榜溢价 / 外盘接口评估批 | 4 并行 | 波 1（文档口径先落） |
| 波 4 | 44 号 Phase 2 + 观测层：期指采集配置+M1-⑧/M3-⑥ 基差 / ES/NQ 采集 / M1-⑨ 期权 / M1-⑩+SEC-03 分歧标定 / SEC-01/02/04/05 / IDX-01 / M1-②c / M3-③ / M4-① / M4-② / FCT 12 条登记 | 分组并行（文件级划面） | 波 3 |
| 波 5 | 数据期项代码（带降级兜底）：M1-③ 相似日 / M1-④ 调度回路+快照落库 / M2 边界修正闭环 / M3-② 新闻情绪（#138/#139）/ M3-④ 日韩评估 / M3-⑨ 核心件 / M4-④ 调参闭环 | 分组并行 | 波 4（消费其产出物） |
| 波 6 | E2E 测试：全部新功能+集成功能两轮，问题≠0 则修复后重测，至连续两轮问题=0 | 修复分组并行 | 波 5 |
| 波 7 | GitCommitGateway 落地收尾 + 临时文件清理 + tracker 登记 | 统筹串行 | 波 6 |

> **波间提交纪律**：每波完工即提交（单域拆笔经 GitCommitGateway），不攒到波 7——tracker/注册表改动立即单文件提交（多会话并发期铁律）。波 7 是"最终收口"非"唯一提交点"。

## 4. 波 1 工单（文档注记+小切口，4 路并行）

### 4.1 INT-01 硬编码路径收敛

- **改动点**（2026-08-22 实证 9 处负载+测试对齐）：
  - QMT 模拟盘 `E:/国金QMT交易端模拟/userdata_mini`：[event_driven_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/implementations/event_driven_engine.py#L103) L103、[tick_replay.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/tick_replay.py#L140) L140、[data_handler.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/data_handler.py#L515) L515、[miniqmt_provider.py](file:///d:/ZephyrAlpha/src/zephyr/governance/data_governance/miniqmt_provider.py#L106) L106
  - 通达信 `E:\tdx\PYPlugins\user`：[sector_snapshot_collector.py](file:///d:/ZephyrAlpha/src/zephyr/data/sector_snapshot_collector.py#L55) L55、[sector_kline_downloader.py](file:///d:/ZephyrAlpha/src/zephyr/data/sector_kline_downloader.py#L48) L48、[tqcenter_provider.py](file:///d:/ZephyrAlpha/src/zephyr/data/implementations/tqcenter_provider.py#L55) L55
  - 仓根 `D:/ZephyrAlpha`：[workspace_telemetry.py](file:///d:/ZephyrAlpha/src/zephyr/shared/io/workspace_telemetry.py#L55) L55、[atomic_transaction_manager.py](file:///d:/ZephyrAlpha/src/zephyr/governance/financial_governance/atomic_transaction_manager.py#L89) L89
- **步骤**：QMT 四处改读 `get_service_secret("QMT_SIM_PATH", "qmt")`（config/.env.qmt 已有该 key）；tdx 三处 `_TQCENTER_PATH` 改读配置（.env 增 `TDX_PLUGIN_DIR`+secret_registry 登记）；仓根两处改 `paths.find_repo_root()`；关联测试改 mock 配置注入。scripts/*.ps1 的 `$RepoRoot` 自指型不改（脚本自锚定仓根属正当）。
- **验收**：grep `E:/国金|E:\\tdx|D:/ZephyrAlpha` src/ 零负载命中；tests/backtest+tests/zephyr/data+tests/governance 关联域复跑零新增红。
- **登记**：tracker 一行；无新模块免 ARCH。

### 4.2 STR-03 simulation 包命名注记

- **改动点**：`src/zephyr/simulation/__init__.py` docstring 加消歧行——「本包为实验管线抽象（ExperimentPipelineBase/策略仿真），非 QMT 模拟盘撮合；模拟盘链路见 ex_core/trading_session.py + data/tick_subscriber.py」。零行为变更。

### 4.3 ALG-06 爬虫源禁盘中纪律注记

- **改动点**：64_data_source_download_spec.md 增注记——「爬虫源（akshare/baostock 类，零 SLA、盘中多线程扫全市场必封 IP）禁入盘中关键路径，仅离线补充；盘中故障转移链=QMT→券商自带」；akshare_provider/baostock_provider docstring 同步一行。

### 4.4 ALG-04 情绪因子非对称使用口径

- **改动点**：28_sentiment_cycle_trading.md + 26_event_driven_strategy_detail.md 补设计注记——「情绪信号非对称使用：负面情绪→风险预警/减仓规避；不构建多头信号；sleeve 内择时边界不变」（注明东吴金工 2026-01 实证出处：调研纪要情绪因子空头端年化超额 8.26%）。版本号按 01 号管理规范走。

## 5. 波 2 工单（P1 算法基建，6 路并行按域隔离）

### 5.1 ALG-01 regime 横截面结构特征（regime 域）

- **改动点**：`src/zephyr/regime/` 新增横截面特征计算模块（如 `cross_sectional_features.py`）+ regime_feature_builder 增量。
- **特征清单**（日频 OHLCV 可算、PIT 安全、滚动窗口 walk-forward 归一化禁全样本）：①截面收益离散度（全市场个股日收益 std/IQR）②平均成对相关（个股收益两两相关均值，抽样 panel）③波动率离散（个股 20 日 HV 的截面 std）④动量宽度（强于 MA20 的股票占比）。
- **契约警示**：`FEATURE_NAMES` 6 列列序被 `[INVARIANTS]` 钉死——**新特征不得插入既有 6 列**，走新增可选特征列+配置开关默认关（A/B 对照），消费方契约零破坏。
- **验收**：无前视偏差测试（T 日特征只用 ≤T 数据）+34 号 55 用例锚点回归+regime 域零新增红；A/B 对比报告（开/关特征集）落 docs/_working/reviews/。
- **登记**：10_regime_detector_spec.md 版本升级注记；新模块四件套。

### 5.2 ALG-02 WFA 参数稳定区选择（backtest 域）

- **实证纠偏**（2026-08-22 勘察）：walk_forward.py 只做切分不选参数；单点最优在 `param_analyzer.py` L287 `max(runs, key=objective)`；plateau 判定工具已存在于 decision_gate.check_stability_plateau、灾难否决已在 check_wfa_stage。
- **改动点**：param_analyzer.py 参数选择改稳定区规则——`Ω_stable={θ | SR(θ)≥0.9·SR_opt}`，取区内代表点（中位/质心），禁选单点最优；复用 decision_gate plateau 工具不重复造；配置开关默认关（A/B 对照，对齐 ALG-01 纪律）。
- **验收**：合成悬崖/平台参数面用例证明「弃高点选平台」；tests/backtest 零新增红。
- **登记**：52 号注记+B-009 互锁口径。

### 5.3 ALG-03 因子研究案例库（factor 域，新模块+新 DB）

- **改动点**：新模块 `src/zephyr/factor/casebook/`（单文件起步）+ 新 SQLite `data/databases/factor_casebook.db`（D2 裁定已授权）。
- **schema**：`cases(id, hypothesis, factor_expr, factor_json, ic, icir, turnover, verdict, failure_diag, created_at)`——只存统计量不存持仓/金额（B-011）。
- **API**：`record_case`/`query_similar`（先按因子族标签检索，向量检索后置）。
- **验收**：写入-检索-空库/重复边界单测绿；testing 封顶；新模块四件套+ARCH 条目。

### 5.4 INT-03 trading 主进程看门狗（scripts 域）

- **步骤**：①实证 AutoRuntimeCore 生产启动方式（`python -m zephyr.trading`，查 register_aux_tasks.ps1/57 号日循环 SOP 谁拉起）；②仿 start_scheduler.ps1 写 start_trading.ps1（while-true+单实例锁+PID+心跳+孤儿清理）；③register_guard_tasks.ps1 增注册——**disabled 态**（D3 裁定）。
- **验收**：脚本单测/静态检查过；手动起停实证（不起生产 trading 进程，用 --dry-run 或测试替身）；RTO<5min 口径注记。
- **登记**：tracker+SOP 注记（QMT 崩溃/掉线 RTO 依赖人工重登同族口径）。

### 5.5 STR-01 空壳/0-node 域 dormant 标注

- **改动点**：实证真空壳 `src/zephyr/research/__init__.py`、`src/zephyr/alt_data/__init__.py`（含 5 子包空壳，注意 alt_data 头注 MATURITY=production 与实况不符需勘正）+ 模板包（cross_asset/data_eng/ml_serve/signal_quality 等以 depgraph design 态为准）。
- **步骤**：①空壳包 `__init__.py` docstring 头部加「DORMANT（未启用占位模板，勿当实现引用）」；②depgraph 0-node 14 域 build_status 标 dormant（D2 裁定授权，PG 写）；③module_translation_registry.yaml 同步注记（有条目者）。
- **验收**：grep DORMANT 命中即见；gates 零新增红。

### 5.6 STR-02 NotImplementedError 分类（29 处/19 文件，2026-08-22 实证数）

- **步骤**：①全量清单归档；②access_control 族 16 处→candidate_module_registry.yaml 登记 deferred（单人单信任域无 RBAC 需求；触发条件=多账户/多用户上线）；③其余 13 处逐条归因（抽象基类正常用法标注免责/补实现挂 CAND/标 design_maturity=design）。
- **验收**：29 处全部有归宿，清单归档。
- **避让**：candidate_module_registry 与波 0 CAND 登记同文件——本项排波 2，波 0 先提交即无冲突。

## 6. 波 3 工单（44 号 Phase 1，4 路并行）

### 6.1 M1 情绪增量包（signal_ashare 域，单文件主战场）

- **改动点**：`market_sentiment_analyzer.py`（MOD-SIG-025，production 基座上增量）+必要的新辅助模块。
- **内容**（算法真源=44 号 §9.1/§9.2/§9.4）：
  - M1-① 涨跌加速度三件套：breadth_vel_5m/breadth_acc_15m/lu_net_rate_5m/break_rate_5m；MarketSentimentInput 增 Optional time_series 字段；拐点信号（修复中/恶化中）；20 日滚动 z-score 归一；快照缺失>2min 置 NaN 不外推。
  - M1-②a/b 护盘检测（过渡近似版）：a) 指数贡献度拆解（固定权重股名单 TOP≈10 近似，精确版权重待 #225）；b) 黄白线剪刀差（加权 vs 不加权 spread>1σ_20d 且 30min 走扩）；a/b 任一触发→distortion_flag=True→情绪分降权 0.7；合成维度⑧接入 analyze()。
  - M1-⑤ 量能盘中预测：p̄(t)=20 日同时刻累计成交占比中位数曲线（240 点）；ŷ_full=cum_vol/p̄；缩量警示 <0.85×/放量确认 >1.2×。
  - M1-⑥ 大幅回撤个股数：日内曾冲高≥5% 且回吐≥50% 计数；≥7 且最大回撤>10%→追涨被埋警示。
  - M1-⑦ 昨日破板今表现：炸板判定=K线×stk_limit 联算（high≥limit_up 且 close<limit_up，D11 实证口径）；昨日炸板股今日平均收益=承接力指标。
- **纪律**：analyze() 既有 7 维契约与 analyze_grayscale 灰度链零破坏（增维度⑧需同步灰度路径权重归一）；全部阈值 config 化默认值取 44 号研究实证口径。
- **验收**：新特征单测（含 NaN 缺失/边界/合成序列拐点用例）+signal_ashare 域复跑零新增红。

### 6.2 M3 盘前包（plan_engine 域，新模块为主）

- **改动点**：新建 `src/zephyr/plan_engine/overnight_boundary_reviser.py`（MOD-PLAN 新号段）——MOD-PLAN-002 的"修正"增量载体；既有三文件（tomorrow_boundary_planner/premarket_constraint_loader/closing_session_decision）本波不动。
- **内容**（算法真源=44 号 §9.6/§9.10/§9.12）：
  - M3-①a 外盘通道：gap_adj=w1·ret_SPX+w2·ret_NDX（us_index 消费，symbol 空值缺陷下按"最新可得序列"取数+degraded 标注）；|gap_adj|<0.5% 不变档/0.5-1.5% ±半档/≥1.5% 或 BS-005 触发 ±一档。
  - M3-⑦ 盘后资金面四件套：fund_score=0.4·z(margin_delta)+0.3·z(mf_net)+0.2·z(bt_premium)+0.1·z(etf_flow 候选缺省 0)；与 gap_adj 同向确认×1.0/反向且 |fund_score|>1σ 否决半档×0.5。
  - M3-⑧ 事件日历联动：高影响事件夜敏感度升半档/期权到期日 M1 阈值×0.8/交割周基差降权 0.5/A50 交割日敏感度升半档+A50 权重 0.45；calendar_event 空表 fail-open 静默跳过+留痕。
- **验收**：三通道单测（含缺数据降级/事件空表/修正档位映射）；plan_engine 域 17 用例零回归+零新增红。

### 6.3 M3-⑤ 龙虎榜盘后溢价（signal_ashare 域）

- **改动点**：seat_pattern_analyzer.py（MOD-SIG-056）增量或新模块 `lhb_premium_analyzer.py`（查重后定，倾向新模块——MOD-SIG-056 是席位形态，本项是次日溢价预判）。
- **内容**（44 号 §9.7）：高开候选（净买/成交>5% 且机构+一线游资≥2 席）/降权（独食>60% 或一日游隔日卖出率>70% →×0.3）/低开风险（机构净卖>5%）/反核观察（跌停股买一知名游资）；数据=dragon_tiger_seat（608k 行 2022 起实证就绪）。
- **验收**：四规则单测（含空数据 degraded=True 契约对齐 MOD-SIG-056 范式）；域复跑零新增红。

### 6.4 外盘接口评估批（数据域，纯验证+登记）

- **内容**：①akshare 接口实测：A50 期指（futures_global_em 族）/中概互联网 ETF（金龙指数代理）/原油黄金铜——字段/稳定性/历史深度；②新浪 hf_ES/hf_NQ（akshare futures_foreign_commodity_realtime）——字段/秒级延时/日内连续性实证（裁定五前置验证）；③东财 futures_global_em 兜底验证；④日韩股指接口初评（M3-④ 用）。
- **产出**：docs/_working/reviews/2026-08-22-foreign-interface-evaluation.md 评估报告（接口可用性矩阵+主源/兜底裁定建议）；**不接生产调度**（采集任务接线在波 4）。
- **纪律**：接口不顺即砍不恋战；评估脚本用完即删。

## 7. 波 4 工单（44 号 Phase 2 + 观测层，分组并行）

> 文件级划面：期指/ES-NQ 数据组（tasks.yaml+data 域）∥ 情绪新模块组（signal_ashare 新文件）∥ 板块观测组（signal_ashare/data 新文件）∥ regime 面板组（regime 域）∥ plan_engine 组（M3-③）∥ 治理登记组（M4-①/②+FCT）。tasks.yaml 多单并发编辑风险=同文件——数据组内部串行，与其余组并行。

### 7.1 期指采集配置 + M1-⑧/M3-⑥ 基差模块

- **步骤**：①tasks.yaml futures_kline_qmt 补 symbols=IF/IC/IM/IH 主力连续（miniqmt IF.CFFEX 族）+移盘中层；②日频腿修复：kline_futures 的 IF/IC/IM/IH 日频回补（akshare futures_main_sina，实证仅 12 行）——登记数据域任务；③新建 `src/zephyr/signal_ashare/futures_basis_monitor.py`：basis_rate=(F主力-S现货)/S现货、basis_vel_30m、贴水急扩<-1.5σ→降档触发输出、交割周降权 0.5、持仓同步激增确认；IM 对中小盘/IF 对大盘分工注解。
- **验收**：计算模块单测（合成序列：贴水急扩/交割周/持仓背离）；采集配置=YAML 静态校验（实采等次交易日 QMT 在线）。

### 7.2 ES/NQ 盘中实时采集任务

- **步骤**：tasks.yaml L1 族新增任务（1 分钟级轮询，主源 akshare futures_foreign_commodity_realtime 新浪 hf_ES/hf_NQ，兜底东财 futures_global_em；主源连续 3 次失败自动切兜底+告警）；provider 函数落码+新表（us_futures_intraday，DDL-as-Code+data_asset_registry）。
- **验收**：provider 单测（mock 接口）+failover 逻辑用例；盘中异动规则（±1%/±2% 分级+5min>|0.5%| 脉冲）单测。
- **避让**：与 7.1 同碰 tasks.yaml——数据组内部串行。

### 7.3 M1-⑨ 期权情绪三件套（新模块）

- **改动点**：新建 `src/zephyr/signal_ashare/option_sentiment.py`：持仓/成交量 PCR（先实证 OI 列，缺则用成交量 PCR+标注）、IV Rank 分位（可用窗≥60 日守卫+degraded 标注）、Skew=IV(25Δ沽)-IV(25Δ购) 归一化；三件套作注解维度⑨接 MOD-SIG-025（权重≤0.10）；期权到期日 M1 阈值×0.8 联动。
- **验收**：单测（含数据不足降级/极端分位/背离组合警示）；不碰 market_sentiment_analyzer.py 本体（经输入契约注入，防与波 3 M1 包冲突）。

### 7.4 M1-⑩+SEC-03 板块分歧度+概率标定（合并施工，审查报告 §11.5 防双真源裁定）

- **改动点**：新建 `src/zephyr/signal_ashare/sector_divergence.py`：a) 消费 sector_rotation_state 5 状态+sector_siphon 虹吸态（接通消费方）；b) 电风扇速度计（周度行业排名变化均值>75 分位_250d）+Top3 次日重合率<20%；c) 个股分歧度（0.4·z(换手突增)+0.3·上影占比+0.2·炸板标记+0.1·龙虎榜对打）；d) **SEC-03 概率标定器**：5 状态×后续 3/5 日涨跌历史条件频率（滚动 250 日窗，输出"状态+条件概率+样本量"）。
- **验收**：单测（合成板块序列五状态/速度计分位/标定器样本量不足兜底）；映射纪律=个股分歧只出风险清单不出方向（44 号 §9.13）。

### 7.5 SEC-01 板块盘后全景报告器（新模块）

- **改动点**：`src/zephyr/data/sector_report_builder.py`（或 signal_ashare，查重后定）：编排 ranking+breadth+siphon+rotation_state+momentum+analyzer 已落码库模块→日频 sector_report（Top10 板块榜+资金流 money_flow×constituent 聚合+5 状态+主线候选+涨停梯队）；输出落报告文件（docs/_working/reports/ 或 data/reports/，派生不入 git）。
- **验收**：编排纯函数单测（mock 各库模块输出）+一次真实数据端到端跑通留痕。

### 7.6 SEC-02 盘中板块实时聚合器（新模块，与 M1-④ 共用载体）

- **改动点**：`src/zephyr/data/sector_intraday_aggregator.py`：sector_snapshot 30s 字段→板块资金流/涨跌家数/涨速榜/新开板聚合，18-30s 刷新级；纯函数聚合器+调度挂接点留 M1-④ 载体（波 5）。
- **验收**：聚合逻辑单测（合成快照序列）。

### 7.7 SEC-04 龙头识别（新模块）

- **改动点**：`src/zephyr/signal_ashare/sector_leader.py`：22 号 §3.1⑦ 落码——连板高度+成交额+涨幅辨识度→龙头×1.5/中军×1.2/跟风×0.8/中位股×0 四档；观测先行不接交易。
- **验收**：单测（合成梯队场景四档划分+无龙头兜底）。

### 7.8 SEC-05 主线候选榜（新模块）

- **改动点**：`src/zephyr/signal_ashare/mainline_candidates.py`：HEALTHY_MAINLINE 判定+lead_streak+q3 动量+RRG 改善象限综合 Top3-5+理由标签；盘后出榜+盘中快照修正接口预留。
- **验收**：单测（含无主线混沌态空榜兜底）。

### 7.9 IDX-01 四指数 regime 面板（regime 域新模块）

- **改动点**：`src/zephyr/regime/index_regime_panel.py`：同一 HMM 框架 4 代理（000300/000001/399006/000688）各出 regime 概率分布+强弱排序+背离警示（消费 M1-② distortion_flag）；**不建点预测模型**（90 号 §7 铁律）；4 套配置非 4 套模型（特征层复用 regime_feature_builder）。
- **验收**：单测（四代理配置生成/概率输出契约/强弱排序/背离警示注入）；regime 域 55 用例零回归。

### 7.10 M1-②c 板块属性标签（注册表增量）

- **改动点**：板块属性标签注册表增量（防御族=银行/保险/公用/煤炭，进攻族=科技/券商——板块代码映射 yaml）；M1-②c 相对强度雷达计算已在波 3 M1 包含通道 c 兜底，本项=标签真源+rs_ratio 计算接线。
- **避让**：若波 3 M1 包已内含通道 c 简化版，本项收敛为"标签注册表+接线对账"，不重复造。

### 7.11 M3-③ 多情景方案+竞价三细节（plan_engine 域）

- **改动点**：premarket_constraint_loader.py 增量+新建 `scenario_planner.py`：9:00 输出今日三情景操作预案（高开/平开/低开各对应边界与动作清单）；9:25 竞价实况二次匹配修正（复用既有 9 情景）；竞价三细节（44 号 §9.11：虚拟开盘价偏离/匹配量放大≥1.2×/9:20 撤单识别 fake_ratio>0.6 作废）+昨日涨停竞价溢价；消费 auction_book（1.46M 行实证就绪）；**竞价仅作验证信号不作下单通道**（40 号决策⑧）。
- **验收**：三细节单测（合成竞价序列：虚假申报/量缩/方向背离）；plan_engine 域零新增红。

### 7.12 M4-① 日志总账索引（治理登记组）

- **改动点**：新建 `docs/01_policies_and_standards/_registry/catalogs/registry_of_logs.yaml`（每个日志：路径/写入方/消费方/schema/保留期/状态）+生成/校验脚本（GATE-REGISTRY-SYNC 同族 warn-only MVP）；AGENTS.md 速查联动走 Owner 审批通道（D10）。
- **验收**：登记表 schema 校验脚本绿；覆盖度实证（全仓 .log/.jsonl/.ndjson 写入点 grep 对账≥95% 在册）。

### 7.13 M4-② prediction_log 统一落库（治理登记组）

- **改动点**：governance.db 新表 prediction_log（DDL：date/module/prediction_type/payload_json/asof_ts/model_version 等——对齐 reconciliation_differences 落 governance.db 先例，D2 授权）+统一写入器 `src/zephyr/reporting/prediction_log.py`（或 governance 域，查重后定）；M1 情绪分/M2 边界修正事件/M3 三情景的写入点在本批各模块预留接口，波 5/后续批逐步接。
- **验收**：写入器单测（写入-查询-重复日期幂等）；DDL 落库实证。

### 7.14 FCT 因子条目登记（ROOR 流程）

- **内容**：44 号 §2.1 裁定的 12 条 FCT-sentiment 条目（加速度三件套/护盘背离度/量能外推比/大幅回撤数/期指基差×2/期权 PCR+IV Rank/电风扇速度计/个股分歧度）随各模块完工登记 factor_registry.yaml（code_symbol 锚定实现函数）；挂 CAND-FAC-003 IC 实证回填链路。
- **纪律**：模块未完工不登记（防 code_symbol 空挂）；ROOR 流程字段齐全（formula/alpha_source/factor_class=sentiment）。

## 8. 波 5 工单（数据期项代码，带降级兜底）

### 8.1 M1-③ 相似日推演（新模块）

- **改动点**：`src/zephyr/signal_ashare/similar_day_inference.py`：特征向量（breadth_vel/lu_net/量能外推比/黄白线 spread/IF 基差曲线重采样 30 时点）+KNN k=10 同时刻切片相关距离+P(尾盘走强/持平/转弱) 三档概率；**D<60 或近邻距离超阈→退化五阶段转移先验**（28 号阶段转移表）；只出档位概率不出点位；walk-forward 命中率<55% 自动停用开关。
- **数据源**：market_breadth_snapshot（8.2 新建表）——当前零积累，模块上线即走兜底分支，数据期自动升级。

### 8.2 M1-④ 实时调度回路+全市场分钟快照落库（数据域+signal_ashare）

- **改动点**：①新 CH 表 market_breadth_snapshot（分钟级全市场快照：adv/dec/lu/attempted/成交额等，DDL-as-Code+data_asset_registry）；②采集任务（miniqmt 盘中实时取数，tasks.yaml L1/L2 族注册）；③调度回路模块 `intraday_sentiment_loop.py`：分钟级喂快照给 MOD-SIG-025 增量特征组+结果写 prediction_log（7.13）；与 P0-5 日循环 SOP 对接注记；SEC-02 聚合器挂接同载体。
- **验收**：快照采集=任务配置静态校验+mock 采集单测；回路模块单测（快照序列→特征→落库链）；实采等次交易日。

### 8.3 M2 边界修正闭环（plan_engine 域）

- **改动点**：tomorrow_boundary_planner.py/closing_session_decision.py 增量+新建 `boundary_revision_engine.py`（44 号 §9.5 逐条落地）：14:00/14:45 双时点评估；防抖≥15min；升/降档当日各最多 1 次冷却；降档七触发（情绪分<35 且 lu_net_rate_30m<0/distortion 且 spread>2σ/大幅回撤≥7/IM 贴水急扩>1.5σ/5 状态见顶族/虹吸+电风扇共振/BS-005）；升档全满足（情绪>65 且 ŷ_full≥1.1× 且 rs_ratio>0）；档位映射（保守=加仓上限×0.5 禁加仓价位上移 0.5×ATR(14)/进攻=×1.2 封顶 firm 硬约束）；**修正仅当日有效次日覆盖**；每次修正写 plan_revision 事件（M4-② prediction_log）。
- **验收**：七触发+防抖+冷却+当日有效+次日覆盖全行为单测；红队向量（毛刺单分钟不触发/双时点各一次后第三次拒/跨日不累积）。

### 8.4 M3-② 夜间新闻情绪（intelligence 域，#138/#139 闭环）

- **改动点**：①#138：sentiment 持久化表 DDL（CH 新表 news_sentiment_window，data_asset_registry+DDL-as-Code——D2 授权）；②#139：标的关联层（公告已有标的字段；新闻 NER/规则提取 MVP——证券简称/代码词表匹配）；③夜间窗口情绪聚合→M3 盘前修正微调输入（接 6.2 overnight_boundary_reviser 的 news_sentiment 入参）。
- **验收**：表 DDL 落库+关联层单测（简称匹配/歧义处理/无关联兜底）+聚合链路单测；AISA #137 LLM 切换条件不变（规则法默认）。

### 8.5 M3-④ 日韩数据（评估→接入或砍）

- 依波 3 接口评估结论：akshare 有可用日径/韩指接口→最小接入（盘前参考输入，权重≤10%）；接口不顺→登记"砍"留痕，零代码。

### 8.6 M3-⑨ LLM 盘前分析核心件（plan_engine/reporting 域）

- **改动点**：①新建 `src/zephyr/plan_engine/llm_premarket_analysis.py`：数据打包器（44 号 §9.14 七族输入：指数/情绪/板块/衍生/外盘/资金/日历，全部"T+1 日 8:00 前可见"PIT 铁律）+prompt 模板（版本化 prompt_version）+输出契约 JSON（scenarios 三情景/risk_points/watch_sectors/confidence_note）+input_hash SHA-256；②llm_daily_analysis 表 DDL（governance.db，含 model_version/prompt_version/input_hash 字段，D2 授权）+data_asset_registry 登记；③LLM 调用经 gateway 客户端接口注入（阶段三接通，本批接口定义+mock 测试）；④v2 多空辩论模式=prompt 编排三调用（多/空/综合席），配置开关默认 v1。
- **验收**：打包器 PIT 单测（8:00 后信息零泄漏断言）+契约 schema 校验+mock LLM 端到端；真跑留阶段三。

### 8.7 M4-④ 日志→参数校准反馈闭环（governance 域）

- **改动点**：experiment_registry 联动触发器——预测命中率/边界修正胜率统计（读 prediction_log）→参数校准评审触发（G04 校准/CAND-SELL-001 同族触发器形态）；数据期需命中率积累，本批=统计器+触发器骨架+样本量守卫（<30 样本不触发）。
- **验收**：统计器单测（合成 prediction_log 序列）+触发阈值行为用例。

## 9. 波 6 测试纪律（E2E 两轮零问题）

- **范围**：全部新模块单测+集成测试（跨模块链路：M1 增量→M2 修正→prediction_log 落库；M3 盘前包→M3-③ 情景→竞价验证；期指基差→M2 降档触发；观测层 SEC/IDX 端到端真实数据跑通）。
- **执行拓扑教训遵守**：簇内串行 `-n 0`×簇间 3 路并发+假死簇逐文件 300s 墙钟强杀（AI-RESIDUAL-001 实证姿势）；禁 `-p no:xdist`。
- **通过标准**：连续两轮（全量关联域+新测试套件）问题=0；问题≠0→修复分组并行→重测。
- **存量基线**：以 2026-08-21 基线（56 存量红清单）比对，新增红才算问题。

## 10. 波 7 收尾纪律

- 全部改动经 GitCommitGateway 落地（单域拆笔；常态三旗标 --allow-overlap/--allow-multi-domain/[no-lookup:白名单词] 按场景）；禁 --no-verify。
- 临时文件清零（.runtime/_p2_*、评估脚本、message 文件等）。
- tracker 登记批次总账+遗留项；44 号/审查报告文档状态随批修订（D11）。
- 新模块 depgraph planned→generated→testing 两跳流转（production 留 Owner，D7）。

## 11. 移交/不做清单

| 项 | 去向 |
|---|---|
| IDX-02 Dashboard 四指数卡+板块页接入 | 前端会话施工面（D6） |
| RUN-05 彩排断点恢复演练 | 已在 P0-5 闭环链内（审查报告 §10.3 移交件，不重复施工） |
| INT-02/INT-04 | P0-5 已消化（#241/#244③ post_settlement 已挂调度） |
| ALG-05 指数成分 PIT | 在途 #225（CAND-MKTDATA-001/P1-3），不重复 |
| M3-⑨ LLM 真跑+PIT 历史回填 | 阶段三 gateway 就绪后接线；回填待 3 个月验证后（44 号 §9.14 纪律） |
| M1-②a 精确版（index_weight） | 等 #225 闭环 |
| 03 号文域边界裁定 | Owner 人审项（D9） |
| kline_futures 表内容漂移归因 | 数据域专项登记（本批只补 IF/IC/IM/IH 采集配置） |
| us_index symbol 空值修复 | 数据域专项登记（M3-①a 降级消费不阻塞） |

## 12. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-22 | 1.0.0 | 初版：数据实证（§1）+自主裁定（§2）+七波排序+全工单 | Owner 长城任务指令——44 号全组+审查报告升级项施工排序 |
