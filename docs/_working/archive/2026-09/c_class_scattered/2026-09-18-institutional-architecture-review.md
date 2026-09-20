---
ttl: task_bound
completes_when: 已归档（历史战役载体，2026-09-20 批量归档#374① 同族）
---

# ZephyrAlpha 机构级架构尽调报告

- 审查日期：2026-09-18
- 审查视角：客观第三方 · 顶级量化机构架构师 / 投委会技术尽调
- 审查方式：静态代码勘察 + 台账/注册表实证读取 + 规模与技术债量化扫描（只读，未执行任何写操作与下单操作）
- 被审对象：`D:\ZephyrAlpha` @ branch `dev` @ `34fe6de1a5`

---

## 0. 结论摘要（先说结果）

**它不是个人玩具，也不是机构级。它是一个"中型机构的设计骨架 + 高级工作室的交付成熟度"的 AI 原生原型系统（Proto-Institutional Prototype）。**

三条硬结论：

| 维度 | 判定 | 一句话依据 |
|---|---|---|
| 设计水位 | **中型机构（mid-size fund infra）** | PIT 三公理、元数据驱动 DDL、pre-trade Fail-Closed 四级闸、Almgren-Chriss 冲击模型自标定、三层对账——这些不是爱好者会写的东西 |
| 交付成熟度 | **高级工作室（advanced boutique studio）** | 无实盘证据、0 因子/策略出厂、回测台账 43 节点仅 2 个 valid、OOS 仅 4 个交易日 |
| 综合段位 | **小型机构的下限，尚未达标** | 缺的是"证据"，不是"设计"。当前任何绩效数字都不构成投委会可用资据 |

**最刺眼的一条：项目最大的工程量投在了"管理 AI 自己"上，而不是"产生 alpha"上。**
治理与安全类 937 个 py 文件，是交易执行层（405）的 2.3 倍、Alpha 研究层（459）的 1.9 倍。对一家量化机构而言，这是投入结构的倒挂。

---

## 1. 审计证据基础（量化底盘）

| 指标 | 数值 | 备注 |
|---|---|---|
| 源码 | 3,588 个 py / 832,248 行 | src/ |
| 测试 | 3,586 个 py / 788,524 行 | 测试代码比 ≈ 0.95 : 1 |
| 脚本 | 1,020 个 py / 291,635 行 | scripts/ |
| 文档 | 1,917 个 md / 765,545 行 | 文档量 ≈ 源码量 |
| 规范 | 3,545 个 yaml / 695,080 行 | config + docs |
| git commits | 18,636 次 | 2026-03-28 → 2026-09-18，约 176 天 ⇒ 日均 106 commit |
| git authors | `t` / `風` / `Trae` / `Audit System` / `ZephyrAlpha Maintainer` / `清风量化` | **实质单人 + AI 工具 + 自动审计机器人**，无人类第二开发者 |
| src/zephyr 子包 | 53 个 | feedback_loop 340 / infrastructure 338 / governance 301 / shared 280 / gov_enforcement 207 / security 189 ... |
| 活跃 worktree | **42 个**（.aidrafts 24 + .worktrees 18） | 同一份代码磁盘上 40+ 份副本 |
| 工作区脏文件 | 499 个 | — |
| print() 调用 | **10,046 处** vs logging.getLogger **1,606 处** | 比例 6.3 : 1，生产代码大量裸 print |
| bare `except:` | 37 处 | — |
| `os.getenv` 裸调用 | 85 处 | 违反项目自身 RULE-SECRETS |
| TODO / FIXME | 64 / 12 | 数量反而不多，治理扫得干净 |
| NotImplementedError | 48 处 | 集中在少数脚本 |
| MATURITY 标记 | production **仅 2** / testing 8 | 绝大多数模块**没有成熟度标注**，与本应严格的 MATURITY 制度严重不符 |
| 运行环境 | Windows 11 Pro 宿主 + Hyper-V Ubuntu VM（ClickHouse） + **F 盘移动硬盘备份** | 单机、单 VM、移动硬盘灾备 |

> 注：`os.getenv` / `print` 等指标统计口径为主工作区（已排除 42 个 worktree 副本，否则放大约 33 倍）。

---

## 2. 真实优点（这些必须承认，且确实是真货）

### 2.1 回测引擎的防前视设计达到机构标准

- `vectorized_engine.py` 默认 `execution_lag_days=1`，T 日执行 T-1 信号，成交价**开盘优先、收盘兜底**（:299-307）；
- `lag < 1` 且未显式开启 `allow_same_bar_execution` 时**直接抛 `LookaheadExecutionError`**（:245-252）——把前视做成硬断言而非注释，这是真做法；
- T+1 按**日历日**比较并修过 tick 时间戳绕过（`portfolio.py:259-279`）；
- 涨跌停三级解析链（stk_limit PIT 行 → 日期切片 → 板块前缀），含复权 Scaling 自洽检测、方向感知（涨停拒买不拒卖）（`matching_engine.py:1029-1085`）；
- `data/pit_query.py` 实现 as_of / embargo / survivorship 三公理，并对 `announce <= 1970-01-02` 哨兵值置"不可见"。

**这一段可以给中型机构打合格以上。**

### 2.2 交易成本模型是全项目最强环节，而且是"自我加难度"

- `cost_model_calibration.py` 用 **5,519 标的 / 13,119,233 条五档快照**自标定滑点：按 ADV 五分位 2.34~7.24 bp，是旧假设 1 bp 的 **2.3~7 倍**；
- 冲击模型 = Almgren-Chriss，η 0.9776→0.3114、β=0.4205、γ=0（显式防双重计费）；**参与率上限 10%** + 分层 Fail-Closed；
- 费率单一真源（佣金万 0.854 双向 + 5 元地板、印花万 5 卖出单边、过户万 0.1 双向）。

主动把成本改成比原来贵 2~7 倍，这不是自欺的特征。**机构尽调时这一点是强正向信号。**

### 2.3 回测与实盘共用撮合代码

`ex_core/adapters/miniqmt_broker.py:61-64,231` 与回测共用同一份 `MatchingLogic`。这是真正拉开"工作室"与"机构"距离的一条：绝大多数个人系统回测与实盘两套逻辑，盈亏归因永远对不齐。**这条做对了。**

### 2.4 Pre-trade 硬风控与熔断是真 Fail-Closed

- `pre_execution_checker.py` 四级闸门（熔断 → 时段 → 快照 → 否决），探针异常即拒单（:186/209）；
- `risk_layer_orchestrator.py` 单点仲裁 `_engage_kill_switch`，以券商实时持仓清算（限频 15 笔/秒），含破产底线、五态降级、恢复完成前禁止下单；
- 三层对账 `trading/recon_runner.py`（L1/L2/L3）+ `eod_reconciliation.py` + `position_reconciler.py`。

### 2.5 诚实度

项目大量自认缺陷（`akshare_provider.py:236` 自曝 adj_factor 恒 1、`README` 自曝整合iett、`2026-09-12-ai-native-governance-review.md` 自曝"元治理成本与业务开发同量级"）。**能写下来"我不知道/我没做"的项目，比粉饰的有救。**

---

## 3. 问题清单

> 分级：P0 = 结论不可采信 / 会导致真实亏损；P1 = 结构缺陷，必须修；P2 = 工程债与效率问题。

### 3.1 【A 类】数据与正确性 —— 最高优先级，全部会让回测数字变成假的

| # | 级别 | 问题 | 证据位置 |
|---|---|---|---|
| A1 | **P0** | **回测全程不乘复权因子**。`data_handler.py:335` 默认表 `"daily_kline"`，SELECT 只取 `date,symbol,open,high,low,close,volume,amount`。除权跳空被记为真实盈亏 ⇒ **所有历史回测收益虚高，方向未知** | `backtest/core/data_handler.py:335` |
| A2 | **P0** | **表名写错**：SSoT 真源是 `kline_daily`，回测默认 `daily_kline`；全仓另有约 240 处硬编码表名，而 commit gate 仍是 WARN 不阻断 | `table_registry.py` 自述 + `data_handler.py:335` |
| A3 | **P0** | `kline_daily.adj_factor` **9,659,286 行恒为 1**，无持续生产者 ⇒ 除权修正静默失效；独立 `adj_factor` 表仅覆盖 2026-07 起，长周期回测系统性错误 | `akshare_provider.py:236` 原注释 |
| A4 | **P0** | ETF 分钟族 **4.12 亿行 trade_time 时区误标**（UTC 误标本地时，占比 93~95%，≤2026-06-30），修复脚本仍停在 dry-run 等批准。任何分钟级研究裸读即错 | `docs/_working/flash_biz/biz5_etf15min_tz_defect.md` |
| A5 | **P1** | `kline_daily` 用**无版本列 `ReplacingMergeTree`**：同键重复写入保留哪行不确定，实际已发生 `hfq_ratio_extend` 行顶掉 dr 行。`FINAL` 只保证去重，不保证取新 | `schemas/categories/kline/market_kline_daily.py` + 该文件自述蓝图矛盾 |
| A6 | **P1** | CH 与 Redis 同处一台 VM（172.24.30.100），无 `Replicated*` 引擎、无副本 ⇒ 单机即全链路单点 | `infrastructure_registry.yaml` / README 环境章 |
| A7 | **P1** | 断供告警薄弱：`supply_sentinel.py` MATURITY=new 且测试暂缺；历史已发生"股东户数表断供两个月才发现" | `data/supply_sentinel.py` |
| A8 | **P2** | 退市标的在 `kline_daily` 无显式标记字段，仅靠数据自然消失 ⇒ 幸存者偏差敞口（PIT survivorship 只覆盖财务白名单表） | schema 缺失 |
| A9 | **P2** | 特征仓在线/离线双写（CH 在线 `feature_store_writer` + Parquet 离线 `factor/offline_store.py`）无一致性对账，漂移不可见 | `factor/offline_store.py` |
| A10 | **P2** | `akshare_provider.py` 超 9,000 行、内含 338 处源关键字，单文件承担过多能力，回归风险高 | — |

### 3.2 【B 类】回测方法论 —— 有零件，但没跑到结论

| # | 级别 | 问题 | 证据位置 |
|---|---|---|---|
| B1 | **P0** | **SOP-B 七步循环几乎没闭环**：`c1_backtest.node_verdict` 43 行 = pending 41 / valid **仅 2**，36 个节点无结论。制度设计完好，执行率为 4.6% | `2026-09-17-node-verdict-triage.md:20-23` |
| B2 | **P0** | **样本外薄到无统计意义**：定稿锚点后仅 1,467 笔 fill / **4 个交易日**。拿这个谈 OOS 无效 | 同上报告 :57 |
| B3 | **P0** | **Walk-Forward 无 embargo**：`WalkForwardConfig` 只有 mode/window/step，train/test 首尾相接 ⇒ 多日标签策略必然泄漏；`purged_kfold.py:5` 自认 `[CONSUMERS] 预留`，全仓仅测试调用 | `walk_forward.py:124-129`、`purged_kfold.py:5` |
| B4 | **P0** | **随机种子不固定**：`walk_forward.py:272` 用 `np.random.default_rng()` 不传种子 ⇒ White's Reality Check 的 p 值每次都不同，显著性结论不可复现 | `walk_forward.py:272` |
| B5 | **P1** | **归因指标残缺**：`calculate_full_metrics` 只有 return/sharpe/sortino/MDD/win_rate/trades/DSR——**无换手、无 benchmark 超额/α/β、无行业中性化**；`benchmark_symbol` 存进 BacktestResult 却**从未比较** | `vectorized_engine.py:402` |
| B6 | **P1** | 成本标定窗仅 **39 个自然日单窗口**，未跨 regime（`known_limits` 自述）；且未单独标定**开盘竞价段**滑点，而默认成交价就是开盘 | `cost_model_calibration.py` |
| B7 | **P1** | 缺 volume 列时，参与率上限 + 冲击模型**静默旁路**（仅 info 日志）；`PitUniverseProvider` CH 不可达时 fail-open ⇒ 幸存者偏差重新开口 | `matching_engine.py` 旁路分支 |
| B8 | **P1** | 停牌按最后价结转估值（`portfolio.py:380`），平滑 MDD 与 Sharpe | `portfolio.py:380` |
| B9 | **P1** | fill 被拒仅 warn 计数（:347-360），回测可系统性偏离信号而不 fail | `vectorized_engine.py:347-360` |
| B10 | **P2** | `allow_same_bar_execution` 一键放行前视，无二次审批链 | `vectorized_engine.py` |
| B11 | **P2** | 无融券成本、无资金成本、无资金容量曲线 | — |
| B12 | **P2** | 实盘一致性是**预校验**而非真实撮合（`miniqmt_broker.py:394` pre_trade_simulate），真实回报来自 xttrader，两者未做偏离回归 | — |

### 3.3 【C 类】实盘执行与风控 —— 设计达标，但从未接过真钱

| # | 级别 | 问题 | 证据位置 |
|---|---|---|---|
| C1 | **P0** | **幂等防重复下单不可持久化**：`miniqmt_broker.py:244` `_idempotency_map` 纯内存；`order_manager.py:251` `idempotency_key=str(uuid.uuid4())` 每次随机 ⇒ 崩溃重启后去重表清零且键必不同，**重复下单是实锤风险** | 两处明确位置 |
| C2 | **P0** | **无实盘入口**：唯一入口 `scripts/start_paper_session.py` 只读 `QMT_SIM_*`（:119 明确"QMT_REAL_* 永不触碰"）；`LiveSimulationSwitcher` 切实盘需令牌但**全仓无调用方**。data/logs 内**零真实成交/持仓/资金曲线产物** | `start_paper_session.py:119` |
| C3 | **P0** | 熔断探针未接线即静默放行：`pre_execution_checker.py:181` `probe is None` 只打 DEBUG 后继续——这是全链路**唯一的 fail-open 缺口**，且依赖人工注入，遗漏无声失效 | `pre_execution_checker.py:181` |
| C4 | **P1** | pre-trade 仅 7 条硬规则，**无行业/板块集中度、换手率、黑名单/ST、流动性约束**；买入"**新停牌**"股不拦（只查已持有的 `suspended_held_symbols`） | `risk_veto_engine.py:320`、`risk_data_pipeline.py:163` |
| C5 | **P1** | 单点故障：依赖 Windows 单终端 `XtMiniQmt.exe`；心跳 `touch_tick()` **生产零接线**（`miniqmt_broker.py:1065` 自述未接线） | — |
| C6 | **P1** | 对账未闭环：`eod_reconciliation.py:31` `align_to_broker` 默认 False（dry-run）；`recon_runner` 不挂调度，需人工触发 | — |
| C7 | **P2** | 密钥明文：`config/.env.qmt` 存 `QMT_REAL_*`，未见加密托管（85 处裸 `os.getenv` 与之呼应，违反自身 RULE-SECRETS） | `config/secret_registry.yaml:817` |
| C8 | **P2** | `security/access_control/kill_switch.py` 是 **AI Agent 行为熔断，不是交易熔断**，且纯进程内存（:32）——**勿误当作资金安全依赖** | `kill_switch.py:32` |
| C9 | **P2** | 涨跌停/价格笼子在 `prev_close` 缺失或 `CageStatus.UNKNOWN` 时**跳过校验继续下单**（fail-open） | `miniqmt_broker.py:749,1199` |

### 3.4 【D 类】Alpha 研究层 —— 管道极完备，管道里没有水

| # | 级别 | 问题 | 证据位置 |
|---|---|---|---|
| D1 | **P0** | **0 出厂**：`strategy_registry.yaml` 161 条 STR-*，candidate 139 / active 19 / deprecated 3，**sim / paper / production 全为 0**；仅 8 条有 `mount_route` | `_registry/catalogs/strategy_registry.yaml` |
| D2 | **P0** | **因子是文档抽取，不是资产**：`factor_registry.yaml` 175 条 FCT-*，`ic: null` 占 **161 条**（仅 14 条有 IC 数值）、`code_path: ""` 占 **157 条**，status 无一 production | `_registry/catalogs/factor_registry.yaml` |
| D3 | **P0** | **因子代码层是空壳**：真正继承 `FactorBase` 并 `@FactorRegistry.register` 的**只有 4 个类**（value / momentum / intraday_snapshot ×2） | `factor/` |
| D4 | **P0** | **因子门禁形同虚设**：`factor/factor_factory.py:218-220` IC / 因果 / 回测三重门**默认 `lambda c: True`**，不注入即全通过 | `factor_factory.py:218-220` |
| D5 | **P1** | 87 个 alpha 是抄的：`factor/wq_alpha_87.py` = WorldQuant 101 剔 14 存 87，5 个 IndNeutralize 降级为截面 demean；**公开且公认衰减的第三方公式**，非自研 | `factor/wq_alpha_87.py` |
| D6 | **P1** | 工厂未接线：`pf_core/core/strategy_factory.py` 10 阶段机 MATURITY=design、**纯内存无 IO**；DSR>0 且 pbo≤0.5 的指标靠注入，本地无计算 | `strategy_factory.py` |
| D7 | **P1** | ML 层无产物：`model_version_registry.py` 五阶段含人工闸门，但 design + 无持久化，**未发现任何模型产物或版本台账** | `ml_train/core/` |
| D8 | **P1** | 无 benchmark 超额台账（仅有 `benchmark_id` 字段）、无容量分析（`capacity` / `turnover` / `decay_halflife` 全 null）、无正交化/共线性处理（`correlation_group`、`redundancy_status` 全 null） | 各注册表 |
| D9 | **P2** | 数量注水：`signal_ashare` 对外称 153 文件，实际 50 个 py；`__init__.py` 中 5 个类被显式注释"实现就位前保持包可导入" | `signal_ashare/__init__.py` |
| D10 | **P2** | GP 过拟合风险：`research/gp_strategy_discovery.py` 自研遗传规划 + 161 条策略海选，而 DSR/PBO 无本地实现 | — |

### 3.5 【E 类】治理与工程体系 —— 已从资产转为负债

| # | 级别 | 问题 | 证据位置 |
|---|---|---|---|
| E1 | **P0** | **审计链零真实数据**：`data/audit_trail/gate_chain.jsonl` 165 条**全部是 `gate_id:"G0"` / `reasons:["test"]` 冒烟记录** ⇒ 防篡改门禁链不可作为合规证据 | `data/audit_trail/gate_chain.jsonl` |
| E2 | **P0** | **reconciler 拦完即放行**：真执行只在 `.runtime/logs/reconcile_worker_*.log`，212 处 blueprint 违规、149 处漂移（HIGH 41），全部被 **auto_committed 自动修复** ⇒ 阻断语义失效，等于"事后补票" | `reconcile_worker_*.log` |
| E3 | **P0** | **CI 不跑测试**：`.github/workflows/governance.yml` 约 40 步，测试只有 `pytest tests/ --collect-only`（**只收集**）+ 3 个子集；**3,586 个测试文件 / 79 万行从未在 CI 里执行过**；另有 2 步 `continue-on-error: true` | `.github/workflows/governance.yml` |
| E4 | **P0** | **AI 自证闭环，全链无人类签字位**：AI 写规则 → AI 写检查脚本 → AI 写测试 → AI 写结案报告（`2026-09-12-ai-native-governance-review.md` 顶部自述"本报告由清理批自动生成"）。宪法 §5 仅 high 域保留 Owner 门位 | 宪法 + 上述报告 |
| E5 | **P1** | **规范通胀已自我确诊**：86 个 trae yaml / 33,380 行、76 个注册表、751 个 `#ARCH-XXX`；项目自述"元治理成本已与业务开发同量级"、"8 个逃生 flag 默认可用，阻断强度实际取决于 AI 自觉" | `2026-09-12-ai-native-governance-review.md` |
| E6 | **P1** | **169 个 gate 中 113 个是自动桩**（description 仅等于 ID），122 个 `files_trigger:''`，仅 1 个 `always_run:true`；且 `registry_of_registries.yaml` **自相矛盾**：REG-GATE-001 写"43 门禁/91 条目"，REG-GATE-CAT-001 写 169，description 写 25 | 两处 registry |
| E7 | **P1** | 宪法 §4 要求的"gate 触发率季度退役机制"**从未落地**（无 `reconcile_execution_log`） | 宪法 §4.2 |
| E8 | **P1** | **架构真源在仓库不可自举**：`architecture_model/index.yaml` 明示 domains/b_track 由本地 PostgreSQL depgraph 派生（75 域 / 9,148 节点 / 20,279 边）且"禁止手编" ⇒ clone 仓库 ≠ 可验证架构；53 个子包**无循环依赖检测** | `architecture_model/index.yaml` |
| E9 | **P1** | 测试质量两极且无人发现：抽样多数为真断言（阈值/边界/异常，质量可用），但 `tests/signal_ashare/test_capital_flow_pattern_analyzer.py:392` 残留 AI 自语 "Let me recompute" 并把断言降级为 `>= 0.0`；全仓 9 个文件含 `assert True`；`tests/conftest.py:225-234` 注入**假包** `zephyr.testing.code_dedup.*`，auto_test_generator 注释直言"测试仅断言 mod is not None" | 三个位置 |
| E10 | **P1** | **42 个 worktree 常驻**（.aidrafts 24 + .worktrees 18），同一份代码 40+ 份副本；`docs/_working/` 同一文件三处并存（根 + archive/ + `__flatdup` 后缀） | 文件系统实证 |
| E11 | **P2** | 依赖无 lock / 无 hash；`requirements.txt` 是 pyproject 的**手工镜像**（必然漂移）；ruff ignore 近 50 条（含 F401/F811/F841）；`fail_under=70` 但 CI 未见执行 | `requirements.txt`、`pyproject.toml` |
| E12 | **P2** | `print()` 10,046 处 vs logging 1,606 处；37 处 bare except；85 处裸 getenv | 全仓扫描 |
| E13 | **P2** | MATURITY 制度空转：全仓仅 2 个 production / 8 个 testing 标记，绝大多数模块无成熟度标注，管制形同不设 | 全仓扫描 |

---

## 4. 根因分析（为什么会长成这样）

1. **AI 产能与人类验收能力严重不匹配。** 6 个月 18,636 commit、日均 106 次，人类不可能逐条审阅。于是项目**自发长出治理层来约束 AI**——这就是 937 个治理文件的由来。治理不是为了业务需求，是为了解决"AI 太快"的副作用。这是**症状性投入，不是价值性投入**。
2. **规范替代了验证。** 当正确性难以验证时，系统倾向于增加流程（gate/审查/台账）来制造安全感。E1/E2/E3 表明这套流程**没有产生可信审计数据**，于是安全感是虚的。
3. **自证循环无法自证。** AI 检查 AI、AI 给 AI 结案，链条内不存在独立性。这不是 AI 的错，是架构缺一个**人类签字位**（宪法 §5 只在 high 域才有，且 medium/low 全自动）。
4. **数据正确性被推迟太久。** A1~A4（复权、时区、表名）是最基础的正确性问题，却在 83 万行代码之后仍未修。这是典型的"先建高楼、后补地基"——地基问题会让上面所有结论失效。
5. **alpha 被排在最后。** D1~D4 显示"发现 alpha"这件唯一产生利润的事，反而是产出最少的。

---

## 5. 给 Owner 的行动建议（按 ROI 排序，不是按技术优雅排序）

**第一批（不做这些，其他讨论都无意义）：**
1. 修 A1/A2/A3 —— 回测必须乘复权因子，统一表名到 `kline_daily`，重建 adj_factor 生产链。**在此之前，所有历史回测数字应视为作废。**
2. 修 A4 —— 批准并执行 ETF 分钟时区修复脚本。
3. 修 C1 —— 幂等键持久化；这是唯一可能**一次性炸掉账户**的缺陷。
4. 修 E3 —— CI 真正跑测试（`pytest -n 4`），先跑通再谈覆盖率。

**第二批（决定能否从"原型"毕业）：**
5. 修 B3/B4 —— Walk-Forward 加 embargo + 固定随机种子，让结论可复现。
6. 修 D1/D2/D4 —— 要么让至少 1~3 个因子走完"有 IC 记录 + 有 code_path + 三重门真校验"的完整闭环，要么把注册表里 157 条无 code_path 的因子**标记为 aspirational**，禁止计入能力清单。诚实降级比注水更有价值。
7. 修 E1/E2 —— 把 `gate_chain.jsonl` 接到真实 reconcile 事件；auto_commit 的自动修复每周抽检 N 条人工复核。
8. 清理 42 个 worktree + `_working` 三份重复，降低认知负担。

**第三批（决定能否称"机构级"）：**
9. 跑满 ≥1 年真实 paper trading，产出资金曲线与回测偏离回归（B12）。
10. CH/Redis 拆分 + Replicated 引擎 + 异地灾备（当前是移动硬盘）。
11. 引入第二位人类 reviewer，哪怕是兼职，只为打破 AI 自证循环（E4）。

**一条反向建议：不要在修完第一批之前增加任何新模块。** 这个项目当前的边际收益，来自"把已有东西验证对"，而不是"再建一层"。

---

## 6. 投委会口径的一句话

> **值得按中型机构标准继续尽调，但当前没有任何一组数字可以采信。给它 3 个月：修完复权 + 固种 + embargo + 幂等，跑满一年 paper，再拿 evidence 来谈绩效。在此之前，它是一个非常优秀的架构原型，不是一个可投资的系统。**

---

*本报告基于只读勘察，所有引用均可复核。数据规模与技术债指标由脚本扫描主工作区得出（已排除 42 个 worktree 副本）。*
