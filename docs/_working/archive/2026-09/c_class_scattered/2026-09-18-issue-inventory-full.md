---
ttl: task_bound
completes_when: 已归档（历史战役载体，2026-09-20 批量归档#374① 同族）
---

# ZephyrAlpha 架构尽调 — 全量问题清单

- 审查日期：2026-09-18
- 配套报告：`D:\ZephyrAlpha\docs\_working\2026-09-18-institutional-architecture-review.md`
- 分级：P0 = 结论不可采信 / 会亏真钱；P1 = 结构缺陷必修；P2 = 工程债与效率
- 合计：**54 条**（P0 17 / P1 21 / P2 16）+ 5 条元问题 + 3 条环境坑
- 路径说明：均为勘察所得绝对路径，执行前请先确认文件仍存在（项目迭代快）

---

## A 类 · 数据与正确性（10 条）

| # | 级别 | 问题 | 完整路径 / 位置 |
|---|---|---|---|
| A1 | P0 | 回测全程不乘复权因子，除权跳空被记为真实盈亏 | `D:\ZephyrAlpha\src\zephyr\backtest\core\data_handler.py:335` |
| A2 | P0 | 回测默认表名 `daily_kline` 写错，SSoT 应为 `kline_daily`，全仓约 240 处硬编码 | `D:\ZephyrAlpha\src\zephyr\backtest\core\data_handler.py:335`；`table_registry.py` |
| A3 | P0 | `kline_daily.adj_factor` 9,659,286 行恒为 1，无持续生产者 | `D:\ZephyrAlpha\src\zephyr\data\providers\akshare_provider.py:236`（原注释自曝） |
| A4 | P0 | ETF 分钟族 4.12 亿行 trade_time 时区误标（93~95%，≤2026-06-30） | 缺陷报告 `D:\ZephyrAlpha\docs\_working\flash_biz\biz5_etf15min_tz_defect.md`；修复脚本 `D:\ZephyrAlpha\scripts\ch\repair_etf_minute_tz_split.py`（dry-run 待批） |
| A5 | P1 | `kline_daily` 用无版本列 `ReplacingMergeTree`，重复写入保留哪行不确定 | `D:\ZephyrAlpha\schemas\categories\kline\market_kline_daily.py` |
| A6 | P1 | ClickHouse 与 Redis 同处单台 VM（172.24.30.100），无 Replicated 引擎、无副本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure_registry.yaml`；`D:\ZephyrAlpha\README.md` 环境章 |
| A7 | P1 | 断供告警薄弱（MATURITY=new、测试暂缺），历史已发生断供两月才发现 | `D:\ZephyrAlpha\src\zephyr\data\supply_sentinel.py` |
| A8 | P2 | 退市标的无显式标记字段，幸存者偏差敞口 | `D:\ZephyrAlpha\schemas\categories\kline\` 下日线 DDL |
| A9 | P2 | 特征仓在线/离线双写无一致性对账 | `D:\ZephyrAlpha\src\zephyr\factor\offline_store.py`；`feature_store_writer` |
| A10 | P2 | `akshare_provider.py` 超 9,000 行、338 处源关键字，单文件能力过载 | `D:\ZephyrAlpha\src\zephyr\data\providers\akshare_provider.py` |

## B 类 · 回测方法论（12 条）

| # | 级别 | 问题 | 完整路径 / 位置 |
|---|---|---|---|
| B1 | P0 | SOP-B 七步循环未闭环：node_verdict 43 行 = pending 41 / valid 2 | `D:\ZephyrAlpha\docs\_working\2026-09-17-node-verdict-triage.md:20-23`；台账表 `c1_backtest.node_verdict` |
| B2 | P0 | 样本外仅 1,467 笔 fill / 4 个交易日，无统计意义 | 同上报告 :57 |
| B3 | P0 | Walk-Forward 无 embargo，train/test 首尾相接；`purged_kfold.py` 零生产消费者 | `D:\ZephyrAlpha\src\zephyr\backtest\core\walk_forward.py:124-129`；`D:\ZephyrAlpha\src\zephyr\backtest\validation\purged_kfold.py:5` |
| B4 | P0 | 随机种子不固定，White's Reality Check p 值每次不同 | `D:\ZephyrAlpha\src\zephyr\backtest\core\walk_forward.py:272` |
| B5 | P1 | 归因残缺：无换手、无 benchmark 超额/α/β、无行业中性化；benchmark_symbol 存了却从不比较 | `D:\ZephyrAlpha\src\zephyr\backtest\core\vectorized_engine.py:402` |
| B6 | P1 | 成本标定窗仅 39 自然日单窗口、未跨 regime；未单独标定开盘竞价段（而默认成交价就是开盘） | `D:\ZephyrAlpha\src\zephyr\backtest\cost\cost_model_calibration.py` |
| B7 | P1 | 缺 volume 列时参与率上限与冲击模型静默旁路；PitUniverseProvider CH 不可达 fail-open | `D:\ZephyrAlpha\src\zephyr\backtest\core\matching_engine.py` 旁路分支 |
| B8 | P1 | 停牌按最后价结转估值，平滑 MDD 与 Sharpe | `D:\ZephyrAlpha\src\zephyr\backtest\core\portfolio.py:380` |
| B9 | P1 | fill 被拒仅 warn 计数，回测可系统性偏离信号而不 fail | `D:\ZephyrAlpha\src\zephyr\backtest\core\vectorized_engine.py:347-360` |
| B10 | P2 | `allow_same_bar_execution` 一键放行前视，无二次审批 | `D:\ZephyrAlpha\src\zephyr\backtest\core\vectorized_engine.py` |
| B11 | P2 | 无融券成本、无资金成本、无资金容量曲线 | `D:\ZephyrAlpha\src\zephyr\backtest\` |
| B12 | P2 | 实盘一致性仅是预校验，与 xttrader 真实回报未做偏离回归 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py:394` |

## C 类 · 实盘执行与风控（9 条）

| # | 级别 | 问题 | 完整路径 / 位置 |
|---|---|---|---|
| C1 | P0 | 幂等去重纯内存 + 幂等键每次 uuid4 随机 ⇒ 重启后重复下单实锤 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py:244`；`D:\ZephyrAlpha\src\zephyr\ex_core\order_manager.py:251` |
| C2 | P0 | 无实盘入口，唯一入口只读 `QMT_SIM_*`；data/logs 零真实成交产物 | `D:\ZephyrAlpha\scripts\start_paper_session.py:119` |
| C3 | P0 | 熔断探针未接线即静默放行（唯一 fail-open 缺口） | `D:\ZephyrAlpha\src\zephyr\ex_core\pre_execution_checker.py:181` |
| C4 | P1 | pre-trade 仅 7 条硬规则，无行业集中度/换手/黑名单 ST/流动性；买入新停牌股不拦 | `D:\ZephyrAlpha\src\zephyr\risk\core\risk_veto_engine.py:320`；`D:\ZephyrAlpha\src\zephyr\risk\risk_data_pipeline.py:163` |
| C5 | P1 | 依赖 Windows 单终端 XtMiniQmt.exe；心跳 `touch_tick()` 生产零接线 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py:1065` |
| C6 | P1 | 对账未闭环：`align_to_broker` 默认 False；recon_runner 不挂调度 | `D:\ZephyrAlpha\src\zephyr\ex_core\eod_reconciliation.py:31`；`D:\ZephyrAlpha\src\zephyr\trading\recon_runner.py` |
| C7 | P2 | 密钥明文存 QMT_REAL_*，未加密托管；对应 85 处裸 os.getenv | `D:\ZephyrAlpha\config\.env.qmt`；`D:\ZephyrAlpha\config\secret_registry.yaml:817` |
| C8 | P2 | `kill_switch.py` 是 AI Agent 行为熔断而非交易熔断，纯进程内存，勿误当资金安全依赖 | `D:\ZephyrAlpha\src\zephyr\security\access_control\kill_switch.py:32` |
| C9 | P2 | 涨跌停/价格笼子在 prev_close 缺失或 CageStatus.UNKNOWN 时跳过校验继续下单 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py:749,1199` |

## D 类 · Alpha 研究层（10 条）

| # | 级别 | 问题 | 完整路径 / 位置 |
|---|---|---|---|
| D1 | P0 | 161 条 STR-*，sim/paper/production 全为 0，仅 8 条有 mount_route | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\strategy_registry.yaml` |
| D2 | P0 | 175 条 FCT-*：161 条 ic=null、157 条 code_path 空、无一 production | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\factor_registry.yaml` |
| D3 | P0 | 真正继承 FactorBase 并 @FactorRegistry.register 的只有 4 个类 | `D:\ZephyrAlpha\src\zephyr\factor\` |
| D4 | P0 | 因子三重检验门默认 `lambda c: True`，不注入即全通过 | `D:\ZephyrAlpha\src\zephyr\factor\factor_factory.py:218-220` |
| D5 | P1 | 87 个 alpha 抄自 WorldQuant 101（剔 14 存 87），IndNeutralize 降级为截面 demean，公开且公认衰减 | `D:\ZephyrAlpha\src\zephyr\factor\wq_alpha_87.py` |
| D6 | P1 | strategy_factory 10 阶段机 design 级、纯内存无 IO，指标靠注入 | `D:\ZephyrAlpha\src\zephyr\pf_core\core\strategy_factory.py` |
| D7 | P1 | ML 模型版本台账无持久化，无任何模型产物 | `D:\ZephyrAlpha\src\zephyr\ml_train\core\model_version_registry.py` |
| D8 | P1 | 无 benchmark 超额台账；capacity/turnover/decay_halflife 全 null；无正交化/共线性处理 | 各 `_registry/catalogs/*.yaml` |
| D9 | P2 | signal_ashare 实际 50 个 py（对外称 153）；5 个类是"保持包可导入"占位 | `D:\ZephyrAlpha\src\zephyr\signal_ashare\__init__.py` |
| D10 | P2 | GP 遗传规划 + 161 条海选，DSR/PBO 无本地实现，过拟合风险敞口 | `D:\ZephyrAlpha\src\zephyr\research\gp_strategy_discovery.py` |

## E 类 · 治理与工程体系（13 条）

| # | 级别 | 问题 | 完整路径 / 位置 |
|---|---|---|---|
| E1 | P0 | 审计链 165 条全为 `gate_id:"G0"` 冒烟，零真实门禁记录 | `D:\ZephyrAlpha\data\audit_trail\gate_chain.jsonl` |
| E2 | P0 | reconciler 212 处违规、149 处漂移被 auto_commit 自动修复，拦完即放行 | `D:\ZephyrAlpha\.runtime\logs\reconcile_worker_*.log` |
| E3 | P0 | CI 只有 `pytest --collect-only`，3,586 个测试从未真正执行；2 步 continue-on-error | `D:\ZephyrAlpha\.github\workflows\governance.yml` |
| E4 | P0 | AI 写规则→检查→测试→结案，全链无人类签字位 | 宪法 `D:\ZephyrAlpha\AGENTS.md` §5；`D:\ZephyrAlpha\docs\_working\2026-09-12-ai-native-governance-review.md` |
| E5 | P1 | 规范通胀：86 个 trae yaml/33,380 行、76 注册表、751 个 #ARCH-XXX；8 个逃生 flag 默认可用 | `D:\ZephyrAlpha\docs\_working\2026-09-12-ai-native-governance-review.md` |
| E6 | P1 | 169 gate 中 113 个自动桩；registry 自相矛盾（43/169/25 三个数字） | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\gate_registry.yaml`；`D:\ZephyrAlpha\docs\registry_of_registries.yaml` |
| E7 | P1 | 宪法 §4 要求的 gate 触发率季度退役机制从未落地 | `D:\ZephyrAlpha\AGENTS.md` §4.2 |
| E8 | P1 | 架构真源在本地 PostgreSQL，仓库不可自举；53 子包无循环依赖检测 | `D:\ZephyrAlpha\architecture_model\index.yaml` |
| E9 | P1 | 测试注水：`test_capital_flow_pattern_analyzer.py:392` 残留 AI 自语并把断言降级为 `>=0.0`；9 个文件含 `assert True`；conftest 注入假包 | `D:\ZephyrAlpha\tests\signal_ashare\test_capital_flow_pattern_analyzer.py:392`；`D:\ZephyrAlpha\tests\conftest.py:225-234` |
| E10 | P1 | 42 个常驻 worktree（.aidrafts 24 + .worktrees 18）；_working 三份重复 | `D:\ZephyrAlpha\.aidrafts\`、`D:\ZephyrAlpha\.worktrees\`、`D:\ZephyrAlpha\docs\_working\` |
| E11 | P2 | 依赖无 lock/hash；requirements.txt 是 pyproject 手工镜像；ruff ignore 近 50 条；fail_under=70 未执行 | `D:\ZephyrAlpha\requirements.txt`；`D:\ZephyrAlpha\pyproject.toml` |
| E12 | P2 | print() 10,046 处 vs logging 1,606 处；bare except 37；裸 getenv 85 | 全仓扫描（主工作区口径） |
| E13 | P2 | MATURITY 制度空转：全仓仅 2 个 production / 8 个 testing | 全仓扫描 |

## 元问题（根因层，5 条）

1. **AI 产能与人类验收不匹配** —— 日均 106 commit，治理层是为"管住 AI"而长出来的症状性投入（937 个文件）。
2. **规范替代了验证** —— 正确性难验证时倾向加流程，流程又没产出可信审计数据（E1/E2/E3）。
3. **自证循环无法自证** —— AI 检查 AI，链条内缺独立性，架构缺人类签字位。
4. **数据正确性被推迟太久** —— A1~A4 是最基础问题，却在 83 万行之后仍未修，地基问题让上层结论全部失效。
5. **alpha 排在最末** —— 唯一产生利润的事，产出最少（D1~D4）。

## 环境坑（新会话必读，3 条）

1. **本机 Bash coreutils 损坏**：`wc` / `find` / `dirname` / `head` / `cd` 均不可用。批量统计必须走
   `"C:/Users/fanzi/.workbuddy/binaries/python/versions/3.13.12/python.exe" <脚本路径>`。
2. **PowerShell 工具当前不回显 stdout**，不可用于取值；只适合执行不关心输出的动作。
3. **统计口径要排除 worktree 副本**（`.aidrafts` 24 + `.worktrees` 18），否则计数放大约 33 倍。
