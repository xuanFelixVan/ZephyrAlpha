---
ttl: task_bound
---

# AI-NIGHT-001 阶段1 收尾核查：#199/#200/#201 消费侧实证与裁定建议

- 日期：2026-08-19
- 范围：tracker #199（CorporateActionPipeline 空壳）/ #200（FRED 宏观前视）/ #201（指数成分历史幸存者偏差）三项"待查消费侧/待裁定"遗留项
- 性质：全部只读实证；未改 src/、未改 tracker、未改任何配置/文档（本报告为唯一产出）；无 git commit

---

## 项1 · #199 CorporateActionPipeline 空壳（复权因子恒 1.0）

**结论：零生产消费方，纯测试自用空壳。裁定建议 = 退役（登记 CAND 观察一个周期后删除），不建议"接管改消费 adj_factor 表"。**

### 实证链

- 全仓 Grep `CorporateActionPipeline` / `CorporateActionEvent` / `AdjFactor` / `CAPIPELINE_SOURCES` / `corporate_actions`，命中仅三类：
  1. 定义处 `src/zephyr/gov_audit/corporate_actions.py`（L66-92，管道纯内存态：`events`/`adj_factors` 两个 list，无 IO、不落库）；
  2. 唯一引用方 `tests/governance/audit/test_corporate_actions.py`（13 处命中全部在测试）；
  3. tracker #199 条目自身与 `data/classified` 资产扫描 JSON 元数据（非代码）。
- `src/zephyr/gov_audit/` 包内 grep `corporate`：除自身外仅 `__init__.py` L46 注释列举模块名，无任何 import/接线；`pipeline_runner.py` 等包内设施均不引用。
- 文件头注声称 `[CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP`，代码层实证为零——头注与实测不符（蓝图声明态残留）。
- 生产链路复权另有完整闭环，与本管道无关：`c1_market.adj_factor` 表持续生产者 = miniqmt `_fetch_adj_factor`（miniqmt_provider.py L1389，tasks.yaml `adj_factor_incremental`，#198 治理后确立的 dr 点口径）；消费方 = factor/core/evaluation/backtest.py（#197 修复后 close×adj_factor 面板）、normalized_market_data_producer/producer.py、akshare stk_limit 除权修正——全部直连该表，无人经过 CorporateActionPipeline。

### 裁定建议与改动面

- **退役**：空壳且无消费方，保留只会持续制造"复权已治理"的错觉（validate 恒 []、verify 恒 True 的假绿）。建议登记 CAND 观察一个周期后删除；若统筹倾向直接删，风险同样为零。
- **不建议接管**：#198 已让 adj_factor 表有 miniqmt dr 口径持续生产者、消费侧直连该表；把本管道改为"消费 adj_factor 表"只会造出一个没有消费方的中间封装层，属重复建设。
- 改动面：删 `corporate_actions.py`（101 行）+ 删 `tests/governance/audit/test_corporate_actions.py` + tracker 状态更新；零生产影响面。

---

## 项2 · #200 FRED 宏观数据前视（report_date=观测期，无 vintage）

**结论：落库侧前视推断属实，但 `c1_market.macro_data` 全仓零生产消费方，前视无传导路径——非实锤偏差，裁定建议 = 登记"宏观消费接入前置门槛"隐患 + 修复方案预评（现阶段不动工，不过度工程）。**

### 实证链

- 落库侧（前视成立）：`fred_provider.py` `_fetch_fred_series` 请求参数仅 `series_id/observation_start/observation_end/file_type/api_key`（L474-481），**未带 `realtime_start`/`vintage_dates`**；`report_date = obs["date"]` 即观测期（L503-504）。双分量前视均存在：①修订前视（拿到的是最新修订值，非当时 vintage 值）；②发布滞后前视（如 GDP 观测期 2026-01-01，实际 4 月末才发布，回测在观测日即可见）。
- 消费侧（无传导路径）：`macro_data` 全 src 引用 = 三个写入 provider（akshare/fred/eia）+ tasks.yaml/policies.yaml/known_data_gaps.yaml（配置）+ `speed_tester.py` L132（测速探针，非研究消费）；scripts 侧仅 `check_indicator_prefix.py`（indicator_name 前缀合规治理工具，非消费）。
- 名义消费设施均为空壳/静态：`MacroFactorSignal` 合约（shared/contracts/macro_factor_signal.py）全仓无生产者/消费者实现；factor 层 `'macro'` 仅是 domain 标签字符串；`gov_drift/regime_detector.py` 的 `MACRO_INDICATORS` 是硬编码静态字典，不读库。
- 即：消费侧"是否自做 lag"问题不成立——**没有消费侧**。

### 修复方案预评（供首个宏观消费方立项时强制配套）

| 方案 | 内容 | 改动面 | 评价 |
|---|---|---|---|
| A provider 侧 vintage | 请求加 `realtime_start/realtime_end`（或 `vintage_dates`），解析 vintage 字段，落 vintage 表 | fred_provider ~20-40 行 + **vintage 表 DDL（Owner 审批边界）** + tasks.yaml 任务 | 彻底消除修订前视；发布滞后前视仍需 knowledge_date 语义配合 |
| B 消费侧统一 lag N | 消费方按发布延迟 shift | 当前=0（无消费方可改）；未来每消费方各自 lag，口径分散靠纪律维系，且各序列发布滞后异构（GDP≈1 季、CPI≈半月、利率≈0） | 单独采用则治标不治本 |
| C 混合 | A 治修订 + B 治发布滞后 | 两者叠加 | 长期正解 |

- **推荐路径**：现阶段零消费方 → 仅登记隐患不动工；首个宏观因子/消费方立项时强制配套方案 A，并在消费契约层强制 knowledge_date 对齐（B 的制度化版本，即 C）。
- 附带说明：同表的 EIA（report_date=period，eia_provider L362-373）与世界银行（年度数据强滞后）同结构前视，届时一并治理。

---

## 项3 · #201 指数成分历史幸存者偏差

**结论：历史 universe 回测消费路径不存在（零消费方），偏差无传导路径；且表结构已前瞻布局 SCD-2。裁定建议 = 过度工程（当前不做）→ 登记"未来工程-小型"，触发条件 = 首个指数 universe 历史回测/指数增强需求立项。**

### 实证链

**① universe 构造消费方 = 零**

- `c1_market.index_constituent` 全 src 读方仅 `speed_tester.py`（探针）；策略/回测的 universe 全部是调用方显式传入的 `list[str]`（ex_core/trading_session.py L175、pf_core/topn_momentum_strategy.py、factor/core/evaluation/backtest.py `load_history(symbols, start, end)` L162、pf_core/strategy_engine/strategy_runner.py L362）——无任何代码按历史时点读成分表构建 universe。
- 全仓 `000300/沪深300` 引用（约 40 处）全部是**基准指数 K 线**（regime 特征、回测 benchmark，读 `kline_index` 表），非成分 membership。
- 即：当前不存在"用当前成分回测历史"的代码路径，幸存者偏差无实锤受害者（若使用方手工以当前成分列表传 universe 回测历史，属使用纪律问题而非管线缺陷）。

**② 生产者快照口径属实，但表结构已 SCD-2 前瞻布局**

- 快照口径：miniqmt `fetch_index_constituent`（trade_date=payload.end，L1174）/`fetch_index_weight`（L4153）、baostock `query_hs300_stocks`（仅当前成分，L229-234）、akshare `index_stock_cons_csindex`（当前快照+月末权重）。
- 结构侧：`index_constituent` 表 2026-08-10 已 SCD-2 重建（valid_from/valid_to，schema 头注明示"消除幸存者偏差"，`schemas/categories/market_index_constituent.py` L19-26）；`index_weight` 表 2026-07-23 起 SCD-2；akshare `index_member_premarket`/`index_member_postclose` 日频快照任务在跑——**2026-08 起历史向前累积，仅管线启动日前段无从重建**（#201 判断成立但范围应限定为回填段）。
- **附带发现（同族空壳，建议一并登记）**：`c1_market.index_adjustment` 事件表（2026-08-10 建，announcement_date/effective_date/inclusion/exclusion 结构完备，本是历史成分重建的最优事件源）全 src **零生产者零消费者**——schema 头注声称消费者为 akshare_provider，实证无任何引用。

**③ tushare index_weight 接入现状**

- `tushare_provider.py`：production，已转正为正式主源（industry_class_suppl，#ARCH-IFIND-FAILOVER）；token = `TUSHARE_TOKEN` 环境变量经 `get_required_secret` 读取（L120）；capability 路由 9 项（news_data/industry_class/industry_class_suppl/lof_list/money_flow/futures_term_structure/etf_nav/st_namechange_backfill/northbound_hold_snapshot），**无 index_weight**。
- 风险点：meta.known_issues 已载明"积分不足API受限"（L112）——tushare `index_weight` 接口需 2000 积分门槛，接入前需先验证账户积分。

**④ 工程量评估（若启动）**

- 新增 tushare `_fetch_index_weight` capability：`pro.index_weight(index_code, start_date, end_date)` 月频权重快照，仿现有 `_fetch_*` 模式 ~80-120 行 + CapabilityContract + tasks.yaml 任务注册 → **小型**。
- 月频→日频成分推导：月快照按 trade_date ffill 至日频，membership=weight>0；生效日精确化可选（接 index_adjustment 事件表，同时治愈该表空壳）→ 含此项升级为**中型**。
- 落表：复用 `index_weight`（SCD-2 已就绪）或 `index_constituent`（SCD-2）→ **无需新 DDL**；如需专用历史表则 DDL 属 Owner 审批边界。
- 已知误差源：指数调整真实生效日规则（公告后第二个星期五次日）若以月快照日近似，引入 ±数日 membership 误差；tushare 历史深度受积分与接口限制待验。

### 裁定建议

- **当前：过度工程，不动工。** 零消费方 + SCD-2 快照已向前累积，急迫性低。
- **登记：未来工程-小型**（纯 tushare 回填路径；含事件表接线则中型），触发条件 = 首个指数 universe 历史回测/指数增强需求立项；立项时一并把 index_adjustment 事件表接入生产者（akshare 中证调整公告），避免重蹈 #199 式空壳。

---

## 汇总

| # | 遗留项 | 消费方实证 | 裁定建议 | 改动面 |
|---|---|---|---|---|
| 199 | CorporateActionPipeline 空壳 | **零生产消费方**（仅测试） | 退役（登记 CAND→删）；不接管 | 删 1 src 文件+1 测试文件，零生产影响 |
| 200 | FRED 宏观前视 | **零生产消费方**（macro_data 仅探针/治理工具读取） | 非实锤，登记"宏观消费接入前置门槛"隐患；方案预评 A/B/C，推荐立项时强制 C（A 治修订+B 制度化 knowledge_date） | 现阶段 0；启动时 provider ~20-40 行+vintage 表 DDL（Owner 审批） |
| 201 | 指数成分幸存者偏差 | **零生产消费方**（universe 全为显式传参；SCD-2 快照已自 2026-08 累积） | 过度工程（当前）→ 未来工程-小型；附带登记 index_adjustment 表零生产者空壳 | 启动时 ~80-120 行+任务注册+积分验证；无新 DDL |

**阻塞**：无。边界提示：本报告全部只读；涉及的 DDL 变更建议（vintage 表/历史成分专用表）均属 Owner 审批边界，本批未触碰。
