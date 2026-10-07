---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# S2 信号与决策地图环节簿

> 战役: fullflow_20261008 ｜ 段: S2 信号与决策 ｜ 挖矿代理: S ｜ 日期: 2026-10-08
> 范围: config/trading_decision_map.yaml（TDMAP-001）→ src/zephyr/signal_ashare/（源线六判据等）→ data/strategy_intake/（策略吸收面）→ 情绪概率/next_day_8state → docs/03_modules/_domain_signal/（蓝图面）
> 纪律: 只读调研+解析/import 冒烟；未改图、未写库、未启动任何服务。**特别声明：源线六判据另一车队正在落地其余判据，本簿只记录现状（4/6 在 dev），不代修不抢道。**

## 一、输入面

| 输入物 | 真源路径 | 实测规模/说明 |
|---|---|---|
| 交易决策地图主图 | `config/trading_decision_map.yaml`（MOD-TRADING-015，schema_version 1.2，map_id=TDMAP-001，effective_from=2026-10-05 知识层 PIT 生效日） | 6360 行；**nodes=186 / edges=261 / module_mounts=188 条（66 节点，去重 180 个模块 id）/ strategy_mounts=50 条（22 节点，43 个唯一 STR id）/ purpose_tags=12（PT-01~PT-12，大白话终审冻结版）**；markets=[cn_a, crypto]（crypto V0 骨架空壳，仅 4 节点） |
| 分层节点（entry_flow=133） | 同上 | LROOT=1、L0=5、L1=10、L2=30、L3=26、L4=16、**L9=45**；图内层轴无 L5-L8 节点（L9=知识供给层；L5 排产闸属 S4 调度闸域） |
| 其余三流节点 | 同上 | position_flow=18（PFLOW 1+P1 7/P2 5/P3 5）、exit_flow=19（XFLOW 1+S1 7/S2 7/X1 4）、portfolio_flow=16（CFLOW 1+C1 4/C2 5/C3 6） |
| 边类型 | 同上 | feed=205、sequence=38、feedback=9、broadcast=9 |
| 状态矩阵 | 同上 state_matrix | 6 态（capitulation/accumulation/ignition/expansion/euphoria/distribution）×24 格，钉在 4 节点：TDM-E-L1 大盘总闸、TDM-E-L4 买卖点与执行、TDM-F-C1 预算切分、TDM-P-P2 做T与加减仓 |
| 组合计划 | 同上 portfolio_plan | PP-001 整装仿真组合 V0（confidence=proposed），16 sleeves（strategy_ref+weight+activation_state） |
| 策略挂载 | 同上（strategy_ref → pf_core StrategyMeta 8 实盘策略 / strategy_registry REG-STR-001） | 50 条挂载：proposed=42、verified=8；引用策略族=STR-MULTIFACTOR×22 / STR-MOMTREND×8 / STR-VREV×4 / STR-DABAN×4 等 |
| 信号域代码 | `src/zephyr/signal_ashare/` | 149 个业务模块（另 15 个 `__init__.py`），子包：core(10)/screening(7)/sector(15)/sentiment(7)/ml_forecast(21)/intraday_t0(7)/limit_up(10)/source_line(4)/strategy_signal(20)+顶层散件 58 |
| 策略吸收面 | `data/strategy_intake/` | **normalized/ 六册聚宽年度精选（2020~2026）共 592 个 .txt 策略**（99/101/99/99/99/95）；raw_manifest.csv 597 条（GBK→统一编码清单）；translated_manifest.csv 仅 10 条候选（qwen3:8b 翻译，多数 translatable=False 拒译）；lane_f_candidates.csv 6159 行等 7 张 lane 候选表 |
| 情绪/8state 相关件 | `src/zephyr/signal_ashare/ml_forecast/`、`sentiment/`、`src/zephyr/plan_engine/` | 见模块面第四节 |
| 蓝图面 | `docs/03_modules/_domain_signal/` | 76 份 blueprint.md（含 source_line 四判据各一份）；域真源=blueprint.md（MOD-L03-001 Signal Generation Core v3.0.12，D_ASHARE_SIGNAL/D_FUNDAMENTAL_SIGNAL/D_SIGQC 三子域） |

## 二、输出面

| 输出物 | 形态 | 下游消费者 |
|---|---|---|
| 图即配置的决策骨架 | TDMAP-001 YAML（被加载/校验/可视化，不是 CLI） | ① `zephyr.trading.decision_map`（load/validate 单一加载真源）；② DECISION-MAP commit 门（断链阻断）；③ dashboard api_server（地图可视化，S5 段）；④ `scripts/governance/.../check_decision_map.py`（align_all 第七图检查项） |
| 源线判据信号（L9 判据件） | 纯函数核：档位/分位/不平衡单值输出+notes | 图谱 TDM-E-L9-A01/A02/A03/A05 判据口径；module_ref 挂载=总裁终裁批（图侧现为占位） |
| 板块/个股/情绪信号 | sector(15)/sentiment(7)/limit_up(10)/strategy_signal(20) 等 | TDM 图 L1/L2/L3 层 29 个节点经 module_mounts 挂 MOD-SIG-\*×55+MOD-SIGQC-\*×3 |
| 次日概率 | 8 态概率分布（Σ=1.0）/ 9 格情景矩阵 / 放行门动作分档 | MOD-SIG-104 三级放行门槛（图挂 TDM-E-L2-06-1）→ 建仓决策；作战室 W2 矩阵；B10-01464 隔夜收益期望 |
| 知识供给健康读数 | l9_readiness_aggregator 聚合表 | TDM-E-L9-AGG→TDM-E-FLOW 供给健康边；晨报供给健康段 |
| 策略候选漏斗 | strategy_intake 候选表→CAND-\*→考试→STR 挂载 | S3 回测考试段（c4_exam×model_exam）→ TDM strategy_mounts（带 evidence 回填） |

## 三、入口面（图不是 CLI——"图即配置"的验证方式：解析+节点统计实测）

图没有可执行入口；入口=**配置加载与校验链**。以下全部实测（Python 3.12.8，PYTHONPATH=D:\ZephyrAlpha\src）：

| 验证 | 命令要点 | 实测结果 |
|---|---|---|
| 1. 裸解析统计 | `yaml.safe_load('config/trading_decision_map.yaml')` 后数 nodes/edges/mounts | nodes=186、edges=261、module_mounts=188（66 节点）、purpose_tags=12、state_matrix 6 态 24 格、sleeves=16 |
| 2. 官方加载器 | `from zephyr.trading.decision_map import load_decision_map` → `load_decision_map(路径)` | 返回 `DecisionMap` 对象，加载成功（校验逻辑单一真源） |
| 3. 对齐校验器 | `sys.path` 加 scripts 后 `from governance.d5_architecture.generators.check_decision_map import run_checks; run_checks()` | **fails=0 / warns=393 / total=186**（R1-R13 全过，error 级零；warns 大头=module_ref 红节点占位） |
| 4. 信号域 import 冒烟 | `PYTHONPATH=src` 遍历 `zephyr.signal_ashare` 全部 149 模块逐一 `importlib.import_module` | **149/149 全绿，0 失败**（含 source_line 四判据、sentiment、ml_forecast、8state 全家） |
| 5. 判据件 API 抽查 | `dir()` 四判据公共面 | kline: build_from_bars/classify_momentum_tier/MomentumTier；tick: build_from_ticks/ImbalanceTier；sector: build_from_index_rows/LeadTier；fundamental: build_from_report_rows/PeadSignal——公共 API 齐整可调用 |

## 四、模块面

### 4.1 决策地图本体（图=配置，非代码）

- 加载真源：`src/zephyr/trading/decision_map.py`（load_decision_map/validate_decision_map）
- 校验真源：`scripts/governance/d5_architecture/generators/check_decision_map.py`（R1-R13；AST 扫 pf_core 策略 id，免 import 重模块）
- 阻断门：`src/zephyr/gov_enforcement/commit_gates/decision_map_gate.py`（DECISION-MAP，priority=145，触发式：本 commit 触及地图输入面才全量校验）

### 4.2 源线判据件族 `src/zephyr/signal_ashare/source_line/`（六判据，**4/6 已落 dev，落地进行中**）

| 判据件 | 图节点（decision_question 口径） | MOD | 状态 |
|---|---|---|---|
| kline_momentum_criterion.py | TDM-E-L9-A01 日线/分钟行情（价量趋势动量→N 日收益） | MOD-SIG-155 | dev 在案，MATURITY=design，5 级档位单值输出 |
| tick_microstructure_criterion.py | TDM-E-L9-A02 Tick 分笔（日内微观→次日方向与冲击成本） | MOD-SIG-156 | dev 在案，买卖不平衡 ∈[-1,1] |
| sector_rotation_criterion.py | TDM-E-L9-A03 板块/概念指数（轮动强弱领先个股） | MOD-SIG-157 | dev 在案，RS 分位 ∈[0,1]，与市场级 5 态正交 |
| fundamental_pricing_lag_criterion.py | TDM-E-L9-A05 财务（基本面改善能否被定价滞后捕捉，PEAD） | MOD-SIG-158 | dev 在案，公告日哨兵 PIT 铁律 |
| （资金流判据件） | TDM-E-L9-A06 源线·资金流 | — | **未落 dev，另一车队落地进行中** |
| （财经快讯情绪判据件） | TDM-E-L9-A09 源线·财经快讯情绪 | — | **未落 dev，另一车队落地进行中** |

族约定（`source_line/__init__.py`）：DS 读入形态调用方注入、零 IO、契约校验 fail-closed、记录级缺陷跳过记 notes；**module_ref 挂载=总裁终裁批，本包不落图**——图侧 A01-A17 节点 module_mounts/module_ref 现全为 None，非断链而是挂载流程未走完。

### 4.3 情绪概率 / next_day_8state 链

| 模块 | MOD | 图锚点 | 实测 |
|---|---|---|---|
| `ml_forecast/next_day_8state_forecast.py` | MOD-SIG-037 | CONSUMERS=BM-BUY-01 多情景对策/风控节流（**图上无直接挂载**，经下游门间接消费） | MATURITY=production；8 态=高开高走/高开低走/低开高走/低开低走/平开高走/平开低走/震荡收平/剧烈，Σ=1.0 |
| `ml_forecast/next_day_probability_gate.py` | MOD-SIG-104 | **已挂** TDM-E-L2-06-1 三级放行门槛 | MATURITY=testing；动作分档封闭集，拦截出归因不抛错 |
| `plan_engine/scenario_probability_model.py` | MOD-PLAN-017 | 作战室 W2 九格概率 | testing；三层融合纯函数核，9 格行和=1 |
| `plan_engine/intraday_tomorrow_forecast.py` | MOD-SIG-128 | **已挂** TDM-E-L0-04 明日情绪盘中滚动预测 | 消费 8state |
| `sentiment/`（7 件：sentiment_cycle/market_sentiment_analyzer/extreme_sentiment_reversal_detector/sentiment_price_divergence/option_sentiment/sell_news_overdraft_detector/sentiment_cycle_evaluator） | 部分有 MOD（如 MOD-SIG-063 等） | TDM-E-L2-05-1 水温档推导 module_ref=sentiment_cycle.py | import 全绿；CONSUMERS 多标"待 G07/G08/10_regime 接线" |
| `intelligence/news_sentiment_analyzer.py` | — | TDM-E-L1-S0-1 新闻情绪语义分析（module_ref） | 图引用在案 |

### 4.4 图挂载最重的信号节点（module_mounts 实测 TOP）

TDM-E-L2-01-1 结构强度评估→6 MOD-SIG；TDM-E-L2-09-1 事件图谱传导→6；TDM-E-L3-12-4 形态结构识别→6；TDM-E-L3-03-3 双策略合流体检→5；TDM-E-L1-AGG 市场状态判定→3（MOD-SIG-099/108/122）；TDM-F-C3-05 可靠度养成→MOD-SIGQC-003/005/006。信号域合计：MOD-SIG-\* 55 个唯一 id + MOD-SIGQC-\* 3 个，钉在 29 个节点。

## 五、自动化面

| 机制 | 触发方式 | 证据 |
|---|---|---|
| DECISION-MAP 门 | commit 触发式（触及地图输入面才全量校验，~8.2s；YAML 损坏 fail-closed 阻断） | decision_map_gate.py INARIANTS，经 in_process_gate_registry 自动注册进 GitCommitGateway |
| pattern_event_job（MOD-SIG-145） | **事件触发**：调度器 daily_kline 档 SUCCESS 唤醒，禁 cron 自轮询 | 模块头 STARTUP 注记；薄适配零业务逻辑（扫描/物化真源在 scripts/data 正身） |
| l9_readiness_aggregator（MOD-DATA-L9AGG） | **事件触发**：pipeline_events task_completed 唤醒+同日 60min DB 侧节流；禁 cron/Timer/sleep；fail-open 禁静默绿 | 模块头 INARIANTS；pit_effective_from 直读本图 YAML |
| 图可视化 | dashboard api_server 启动读图（S5 段实测 54 路由面） | api_server.py 引用 trading_decision_map |
| 未自动化（手动/挂起） | 源线判据→图挂载（总裁终裁批）；L9 B/C 渠道采集（声明式 skip）；V2 情绪快照（定案挂起）；sentiment 多件下游接线（待 G07/G08） | 各模块头 CONSUMERS/AGG 声明 |

## 六、缺口面（[绿|黄|红]）

- **[绿]** 图本体健康：官方 run_checks 实测 fails=0（R1-R13 零 error），186 节点/261 边全连通可解析。
- **[绿]** 信号域代码面健康：signal_ashare 149/149 import 冒烟全绿，零失败零告警。
- **[绿]** 源线判据件质量面：四判据件契约齐（fail-closed/纯函数核/PIT 哨兵/同输入同输出），blueprint+tests 三件套在案。
- **[黄]** **源线六判据 4/6：A01/A02/A03/A05 已落 dev（MATURITY=design），A06 资金流与 A09 财经快讯情绪由另一车队落地进行中——本簿不代修**；且四件 module_ref 均未挂图（挂载=总裁终裁批，流程性缺口非断链）。
- **[黄]** 红节点占位 63 个（module_ref=null，warns=393 全为 warning 级不阻断）；L9 45 节点中 38 个 untested。
- **[黄]** 置信度血肉薄：全图 verified 仅 2 节点（TDM-E-L1 大盘总闸、TDM-E-L3-07-3 其余sleeve选股链），proposed=118、untested=66；策略挂载 verified 仅 8/50。
- **[黄]** 吸收漏斗瓶颈：normalized 592 条策略 vs translated_manifest 仅 10 条候选——翻译/吸收产能是 S2→S3 的流量卡点。
- **[黄]** 8state 生产件（MOD-SIG-037，production）图上无直接挂载，靠 MOD-SIG-104 门与作战室间接消费；sentiment 多件 CONSUMERS 标"待接线"。
- **[黄]** crypto 市场 V0 骨架空壳（4 节点）；L9 B/C 渠道（卫星/社媒/门店客流等 13 源线）声明式 skip 未接。
- **[红]** 无（本段零断链：无 error 级缺口、无 import 失败、无引用死链）。

## 七、自审闸（三态总裁定）

**总裁定：黄（图即配置的通道全通、代码面全绿；但六判据落地与挂载终裁进行中、置信度血肉未填——通道在而血肉未满，非断链）。**

- 绿证据：地图 run_checks 0 fails；loader 加载成功；149/149 模块 import 全绿；四判据 API 抽查可用。
- 黄证据：六判据 4/6（A06/A09 另一车队在途，不代修）；63 红节点占位+393 warns；verified 置信度仅 2 节点；592→10 的策略吸收漏斗卡点；8state/sentiment 接线待完成。
- 红证据：无。**交接提示**：A06/A09 落地完成后须经"源线判据→总裁终裁批→module_ref 挂图"流程接线，届时 DECISION-MAP 门自动全量校验；吸收漏斗提速建议移交总包排产（S3 考试段承接）。
