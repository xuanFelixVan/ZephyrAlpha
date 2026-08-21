---
ttl: permanent
doc_type: audit_report
title: 2026-08 全模块架构审查与升级清单（外部实践对标）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-08-21
baseline: "depgraph production 6548 / design 205 / planned 115；CAND 91+29+30+6；测试基线 785 failed 清偿在途"
---

# 2026-08 全模块架构审查与升级清单（外部实践对标）

> **定位**：带日期的审计快照——对照 2026 年 8 月最新机构实践、量化社区与氛围编程（vibe coding）社区做法，回答四个问题：①集成/运行方式是否需升级；②代码结构/功能是否需调整；③数据源/因子/算法是否有缺口或更优解；④模块能否运行、集成后能否运行。
>
> **口径声明（防第二真源）**：本文是审查视图不是登记簿。已在 P0 批/残余四项专项批在途施工的事项只标注「在途」，不重复登记；新增升级项集中在 §6 总表，晋升一律走既有 CAND→ROOR / ARCH 流程，经 Owner 裁定后施工。
>
> **宪章红线**：全部结论经 [system_charter.md](../../04_architecture_principles_decisions/system_charter.md) §2 硬边界（单人+AI、单机 PC、个人资金、日频根频率、单机无热备）过滤——凡需集群/K8s/MQ/高频/多租户的"行业做法"一律判定不适用，列入 §7 不做清单。

---

## 0. 与另两批在途施工的关系（冲突规避表）

| 在途批 | 其施工范围 | 本报告对应处理 |
|---|---|---|
| P0 批（总账施工） | P0-1 对账方案 / P0-2 可启动性 / P0-3 测试债 / P0-4 缺口 / P0-5 日循环 SOP+彩排 / P0-6 省 token / P0-7 drift 复产 | §5 标注「在途」，不重复登记、不改其文件 |
| 残余四项专项批 | trend_analyzer 回迁 / Dashboard data_as_of / #63 测试债 785 清偿 / FLE gates 评估 | 同上；drift 复产验证（P0-7）待其 gov_drift 域闭环后启动，本报告支持该排序 |

---

## 1. 执行摘要（四问总答）

| 问题 | 一句话结论 |
|---|---|
| Q1 集成/运行方式 | **架构形态无需升级**——3 常驻进程+Windows 看门狗+进程内事件总线+SQLite/ClickHouse/Redis 的单机形态正是宪章约束下的正确解，2026 年社区同规模实践一致；需要修的是**启动阻断族**（硬编码路径、盘后管线未挂调度、trading 进程看门狗覆盖缺口），不是架构 |
| Q2 代码结构/功能 | **主结构健康**——业务域+治理域双层结构与 2026 agentic engineering 范式（上下文工程+checkpoint 纪律）对齐；问题集中在**模板骨架包误导、38 处 NotImplementedError 待归因、个别命名误导**，均为小切口治理项 |
| Q3 数据源/因子/算法 | **无方向性缺失、有 4 处可补强**——17 Provider+111 因子+BHY-FDR/CPCV/WFA 已达 2026 机构反过拟合标准；补强项：regime 横截面特征（2026 实证最强驱动）、WFA 参数稳定区选择、因子研究案例库（RD-Agent 实证关键件）、情绪因子非对称使用口径 |
| Q4 可运行性 | **模块级能跑=高置信；集成级能跑=待 P0 批闭环**——6548 production 节点+706 测试文件为证；785 failed 清偿、全链路彩排、回测-模拟盘对账均在途，本报告仅补 1 项彩排验收缺口（断点恢复演练） |

**方向性总评**：项目核心路线（LLM 做因子/舆情辅助而非直接下单、统一框架派少而精、IS→WFA→OOS 主路线、Regime Detection 生死线、治理先行）与 2026 年 8 月可检索到的最新研究与机构实践**逐条对齐**，无战略级转向需要。详见 §4.6 路线验证。

---

## 2. Q1 集成与运行方式评估

### 2.1 现状实证（代码级）

| 机制 | 现状 | 证据 |
|---|---|---|
| 常驻进程 | 3 个：data scheduler（APScheduler）、tick_subscriber、trading AutoRuntimeCore | `python -m zephyr.data.scheduler`、`scripts/start_tick_subscriber.ps1`、`python -m zephyr.trading` |
| 看门狗 | Windows 任务计划 while-true 守护（单实例锁+PID+15s 心跳+孤儿清理），覆盖 scheduler/tick_subscriber/drift | `scripts/register_guard_tasks.ps1`、`scripts/start_scheduler.ps1`、`scripts/register_drift_watchdog_task.ps1`、`scripts/deadman_switch.ps1` |
| 事件机制 | 进程内 Queue 事件总线（背压 500）+ ContractBus schema 校验；跨进程经 ClickHouse/Redis 交换 | `src/zephyr/shared/event_bus.py` |
| 存储 | governance.db（SQLite，paths.py SSoT 锚定）+ ClickHouse（行情主库）+ Redis（db0 模拟/db1 实盘/db2 治理缓存） | `src/zephyr/shared/io/paths.py`、`infrastructure/database_service.py` |
| 编排 | docker-compose 已标注 experimental 不启用（#ARCH-065）——正确裁定 | `docker-compose.yml` 头注释 |
| 日循环 | 盘后结算管线存在但**未挂任何调度器**（文件头自述+评审文档双重证实） | `src/zephyr/trading/post_settlement_pipeline.py` L26-29 |

### 2.2 判定：单机形态正确，不升级

- 2026 年量化社区同规模（个人/小团队 A 股日频）实践的共识形态=本地进程+看门狗+轻量存储，与本项目一致；引入 Kafka/MQ/K8s 属过度工程，违反宪章约束二/五。
- 进程内事件总线在日频根频率+3 秒 Tick 下吞吐充足（背压 500 从未触发的治理记录），跨进程经 Redis/ClickHouse 交换是单机正确解。
- 看门狗模式（任务计划+while-true+心跳）达成宪章 RTO<5 分钟口径，无需 systemd/supervisor 替代品。

### 2.3 需要修的启动阻断族（非架构升级）

| # | 项 | 证据 | 状态 |
|---|---|---|---|
| INT-01 | **硬编码绝对路径收敛**：QMT 模拟盘 `E:/国金QMT交易端模拟/userdata_mini` 4 处（tick_replay.py:140 / event_driven_engine.py:103 / data_handler.py:515 / miniqmt_provider.py:106）+ 通达信 `E:\tdx` 3 处 + `D:\ZephyrAlpha` 3 处（workspace_telemetry.py:55 / atomic_transaction_manager.py:89 / start_scheduler.ps1:41） | grep 实证 26 处命中/实质 ~10 处 | **新增，P0 顺手批**——实盘路径已走 `config/.env.qmt QMT_REAL_PATH`，模拟盘/通达信/仓根补同机制；换机/换盘即断链，属验证闭环前置 |
| INT-02 | 盘后结算管线挂调度器（15:30 T+1 硬时点） | post_settlement_pipeline.py L26-29 | **在途**（P0-5 日循环 SOP 构成件） |
| INT-03 | **trading AutoRuntimeCore 进程无看门狗覆盖**——现有守护仅覆盖 scheduler/tick_subscriber/drift，交易主进程崩溃无自动拉起 | scripts/ 全量排查无 trading 守护脚本 | **新增检查项，P1**——先实证 AutoRuntimeCore 的生产启动方式，再按 start_scheduler.ps1 同型补守护（风险/可用性族） |
| INT-04 | QMT 无法自动登录→常开策略的人工依赖 | 2026-08-21 Owner 裁定 | **已裁定**——补一条 SOP 注记：QMT 崩溃/掉线场景 RTO<5 分钟口径依赖人工重登，列入开盘前检查项（在途 P0-5 内消化） |

---

## 3. Q2 代码结构与功能评估

### 3.1 现状实证（含两处误报纠正）

- **双层结构**：业务域（data/factor/pf_core/pf_alloc/ex_core/ex_sor/risk/backtest/sell_decision/compliance 等）与 AI 自治治理域（gov_audit/gov_drift/governance/trading autopilot/security）体量相当——这是"99% AI 驱动"定位的直接体现，不是臃肿。
- **误报纠正**（审查中实证）：`sell_decision`（13 实现文件/65 类）、`compliance`（8 实现文件）、`pf_alloc`（regime_meta_allocator 等 5 实现）、`ex_sor`（21 文件含 optimal_order_router/algo_trading_engine）均**非骨架**，depgraph production 计数与此一致。
- **真空壳**：`research/`（仅 `__init__.py`）、`alt_data/`（仅模板 `__init__.py`）；另有约十余个模板包（cross_asset/data_eng/ml_serve/signal_quality/plan_engine 等）以 depgraph design/planned 状态为准。
- **债务点**：NotImplementedError 38 处/24 文件（security/access_control 约 15 处最集中）；TODO/FIXME 仅 33 处（治理体系以裁定书替代 TODO，健康信号）。
- **先进面**：回测三引擎（event_driven/vectorized/shrinkage）+ CPCV/purged_kfold/walk_forward + pit_manager 防未来——与 2026 机构反过拟合协议（IS–WFA–OOS、CPCV 替代标准 CV）完全对齐，属行业前排。

### 3.2 升级项

| # | 项 | 理由 | 优先级 |
|---|---|---|---|
| STR-01 | **真空壳/模板包 dormant 标注**（research/alt_data 实证+其余以 depgraph 为准） | 空包对 AI 协作者是"看起来有模块"的误导源，增加每次任务的检索/判断 token；参照 6 张 dormant 数据表先例（保留、标注、不采集） | P1（省 token 族） |
| STR-02 | **38 处 NotImplementedError 分类处置** | access_control 族（~15 处）单人单信任域下无 RBAC 需求→登记 deferred 防复提；其余逐条归因（补实现/标 design） | P2 |
| STR-03 | `simulation/` 包命名收敛（实为 ExperimentPipelineBase 实验抽象，非撮合仿真） | 命名误导 AI 检索"模拟盘"时误入；加包级 docstring 注记即可，零行为变更 | P2 |
| STR-04 | 治理域:业务域体量比维持现状，**不新建治理层** | D1 查重纪律已覆盖；2026 vibe coding 报告核心结论"上下文工程是 AI 代码质量第一变量"支持现有治理投入，但增量须走年检纪律（I-GOV-3 v2） | 纪律项（非施工） |

---

## 4. Q3 数据源 / 因子 / 算法评估

### 4.1 数据源

- **数量与冗余度超社区标准**：17 个 Provider（miniQMT/AKShare/Baostock/Tushare/通达信等）+ vendor 注册/故障转移，远超社区"双源整合"（Tushare 主+AKShare 备，成功率 85%→99%）做法。**数据源不是缺口，PIT 质量才是**。
- 已知缺口均在途或已登记：指数成分 PIT（CAND-MKTDATA-001 / P1-3 #225 tushare index_weight）、退市股 K 线已回填（JOB-084 闭环）、北交所 K 线缺口（数据期）、News Flash 回填（CAND-DAT-002）。
- **新增纪律注记（ALG-06，P2）**：2026 社区避坑共识——AKShare 类爬虫源零 SLA、盘中多线程扫全市场必封 IP，只能作离线补充；项目故障转移已覆盖，但建议把"爬虫源禁盘中关键路径"写进 64 号数据源规范注记，防 AI 未来接线时误用。

### 4.2 因子与 alpha 挖掘

- **现状达 2026 机构标准**：111 因子注册表 + IC/IR + **BHY-FDR 多重检验校正**（Harvey et al. 反假因子标准做法，2026 机构"anti-mirage"协议同款）+ 因子 DAG。
- **LLM 自动挖因子是 2026 最活跃前沿**（QuantaAlpha 轨迹进化/AlphaAgent 抗衰减正则/RD-Agent(Q) 因子-模型联合优化/Hubble AST 沙箱），项目 T3 族（CAND-SIG/RES）已正确登记为数据期事项，**方向对、不抢跑**。
- **新增补强项（ALG-03，P1）**：**因子研究案例库**（成功案例库+失败→修复库，RAG 检索）。RD-Agent CoSTEER 实证：双知识库显著提升首次生成成功率；2026 实测报告进一步显示"模型代码工程能力比推理能力更关键"。该件**零数据依赖**（存假设/因子 JSON/回测统计/失败诊断到 SQLite 即可），现在做=为数据期 LLM 挖因子打底，且即刻降低 AI 重复试错 token。注意：只借鉴机制，**不引入 RD-Agent/Qlib 框架本体**（WSL2 依赖+与现有 backtest 栈重复，见 §7）。
- 因子 IC 实证回填（CAND-FAC-003）在途标注。

### 4.3 Regime 检测（宪章生死线，享有最高优先级）

- 现状：regime_detector + CRPS 校验 + RegimeMeta 分配器（34 号，55 用例锚点），方向正确。
- **新增补强项（ALG-01，P1）**：**regime 特征集补横截面结构特征**（截面收益离散度/平均成对相关/波动率离散/动量宽度）。2026-04 机构白皮书 84,864 组合网格实证：横截面特征是 regime 检测最强驱动，Sharpe lift +0.387、最大回撤 -39.5%→-25.4%；且全部可在日频 OHLCV 上严格 walk-forward 无未来函数计算——单机零成本增量。宪章约束三"Regime Detection 是生死线、施工最高优先级"，此项为当期最高杠杆算法补强。
- **观察不施工**：Wasserstein HMM（2026-02，状态身份追踪+自适应阶数）、BOCPD（CAND-RSK 族已挂）——现有 HMM+CRPS 够用，复杂化有 P9 拒绝先例（LSTM-AE+GHMM），登记观察即可。

### 4.4 情绪 / 舆情 / 另类数据

- **2026 A 股实证关键结论**：LLM 文本因子有效（华泰 LLM-FADT 年化超额 25.36%；东吴调研纪要情绪因子**空头端**年化超额 8.26% 且与量价/基本面低相关）——但alpha 在**非对称使用**：负面情绪是下跌强预警，正面情绪与上涨关系弱。
- **新增口径项（ALG-04，P2）**：把"情绪因子非对称使用"写进 28 号情绪周期/26 号事件驱动设计注记——情绪信号用于风险预警与减仓规避（sleeve 内择时边界不变），不构建多头信号。与宪章"情绪周期=sleeve 内 alpha 择时、regime=风险节流"分工一致。
- 主播监控走音频 ASR（B-020 已裁定）符合另类数据趋势，无新项。

### 4.5 风控算法

- 现状对齐 2026 实践前排：kill switch/VaR/ES/drawdown controller/流动性危机 Protocol 均已施工（第一~三批），2026 机构标准（多层 drawdown 限制+波动率调整仓位+circuit breaker）全覆盖。
- **新增补强项（ALG-02，P1，风险优先族）**：**WFA 流程补"参数稳定区选择+灾难否决"**。2026 AlgoXpert IS–WFA–OOS 协议核心件：不选单点最优、选 SR≥0.9·SR_opt 的平台区，避开悬崖参数；WFA 设多数通过+灾难否决 gate。项目已有 walk_forward/cpcv 基座，补 plateau 选择规则与否决 gate 即可——直接服务"回测-实盘偏差不多"这一验证闭环总目标，且与 B-009 过拟合防护互锁。

### 4.6 路线验证（2026 外部证据支持既有裁定，无需动作）

| 项目既有裁定 | 2026 外部证据 |
|---|---|
| LLM 不直接下单、只做因子/舆情/研究辅助 | KTD-Fin（2026-05）：10 个前沿 LLM 交易 agent 在泄露控制下收益大部分由市场 beta/风格暴露解释，持续选股 alpha 证据有限；AI-Trader（2025-12）：多数 agent 收益低、风控薄弱，**风控能力是鲁棒性决定因素** |
| 统一框架派少而精（宪章 §3 约束二/五） | 2026 决策架构共识：模块化端到端决策架构对长期绩效的贡献大于任何单一预测模型 |
| IS→WFA→OOS 主路线（CAND-SIG-011） | 2026 反过拟合协议标准三段式，逐字一致 |
| CPCV/purged K-fold 替代标准 CV | 2026 机构"anti-mirage"协议标配 |
| 治理先行（AGENTS.md/gates/审计链/提交网关） | 2026 vibe coding→agentic engineering 转向：上下文工程+milestone checkpoint 是防 AI 脱轨第一实践；项目已超前落地 |
| 不做 HFT/日频根频率（B-017） | A 股 T+1+3sTick 现实与 2026 社区判断一致 |

---

## 5. Q4 可运行性与集成验证评估

### 5.1 模块级：高置信能跑

- production 6548 节点、706 个测试文件、xdist+120s timeout+xfail 留痕机制成熟；第一~四批 34 个施工队全部"测试两轮全绿+统筹复跑"闭环（tracker §一）。
- 存量疤：785 failed/17 errors（API 漂移债，单进程可复现）+56 存量红——**在途**（残余四项专项批任务 3 / P0-3），不重复登记。

### 5.2 集成级：待 P0 批闭环（无新增重复项）

| 验证件 | 状态 |
|---|---|
| 回测 vs 模拟盘对账方案（同信号同窗口逐日 diff，偏差归因滑点/部分成交/拒单） | 在途 P0-1② |
| 全模块可启动性收口 | 在途 P0-2（⑤已闭环；①②④残余批） |
| 日循环 SOP+全链路彩排 | 在途 P0-5（Day 5-6） |
| drift 写入链复产验证 | 在途 P0-7（待残余批 gov_drift 闭环，防基线污染——排序正确） |

### 5.3 本报告唯一新增（RUN-05，随 P0-5 消化）

**彩排验收清单补"断网断电→策略状态机断点恢复"演练**。宪章约束五明确"断电断网→策略状态机断点恢复、持仓 RPO=0"，但当前彩排项（开盘检查→模拟盘→收盘→回测→对账）未覆盖该场景——这是家用环境最高概率真实故障，演练成本极低（彩排日手动断进程+断网 5 分钟恢复验证），不补则 RPO=0 口径永远停留在纸面。

---

## 6. 升级清单总表（交付核心）

> 优先级沿用总账尺子：验证闭环 > 风险 > 真实缺口 > 省 token > 数据依赖后置。晋升走 CAND→ROOR/ARCH 流程，Owner 裁定后施工。

| # | 升级项 | 类别 | 建议优先级 | 工作量 | 与在途批关系 | 宪章合规 |
|---|---|---|---|---|---|---|
| INT-01 | 硬编码路径收敛（QMT 模拟盘 4 处+通达信 3 处+仓根 3 处→config/paths.py） | 启动阻断 | **P0 顺手批** | 小（~10 处+测试对齐） | 补充 P0-2 未覆盖面 | ✅ 单机约束内 |
| RUN-05 | 彩排补断网断电断点恢复演练（RPO=0 实证） | 验证闭环 | **P0 随 P0-5** | 极小（SOP 加一项） | 并入 P0-5 | ✅ 约束五直接落地 |
| INT-03 | trading 主进程看门狗补齐（先实证启动方式再同型守护） | 可用性/风险 | P1 | 小 | 无重叠 | ✅ |
| ALG-02 | WFA 参数稳定区选择+灾难否决 gate | 风险/反过拟合 | P1 | 中（walk_forward 基座上补规则） | 无重叠 | ✅ B-009 互锁 |
| ALG-01 | regime 横截面结构特征（离散度/平均相关/宽度） | 算法补强 | P1（regime=生死线） | 小（日频 OHLCV 可算） | 无重叠 | ✅ |
| ALG-03 | 因子研究案例库（成功/失败→修复 RAG 轻件） | 省 token/数据期打底 | P1 | 小（SQLite 即可） | 与 08 提交队列不同域 | ✅ B-011 只存统计量 |
| STR-01 | 真空壳/模板包 dormant 标注 | 省 token 治理 | P1 | 小 | 无重叠 | ✅ |
| ALG-04 | 情绪因子非对称使用口径（负面情绪→预警/减仓） | 设计口径 | P2 | 极小（文档注记） | 无重叠 | ✅ 分工边界一致 |
| ALG-06 | 爬虫源禁盘中关键路径纪律注记（64 号规范补充） | 数据纪律 | P2 | 极小 | 无重叠 | ✅ A-001 互锁 |
| STR-02 | 38 处 NotImplementedError 分类（access_control 族→deferred） | 债务治理 | P2 | 中 | 无重叠 | ✅ |
| STR-03 | simulation 包命名注记 | 防误导 | P2 | 极小 | 无重叠 | ✅ |
| STR-04 | 治理层不新建、增量走年检纪律 | 纪律项 | — | — | 无重叠 | ✅ I-GOV-3 v2 |

**在途不重复登记项**：INT-02（P0-5）、INT-04（P0-5 注记）、ALG-05 指数成分 PIT（CAND-MKTDATA-001/P1-3）、RUN-01~04（P0 批/残余批）。

---

## 7. 明确不做（防过度工程，登记防复提）

| 项 | 判定依据 |
|---|---|
| Kafka/MQ/K8s/集群/docker 栈激活/微服务化 | 宪章约束二/五（单机无集群）；docker-compose experimental 裁定正确维持 |
| L2 行情/高频/微秒级优化 | B-017；miniQMT 10 笔/秒+Tick 3 秒物理上限 |
| 多租户 SaaS | B-019 |
| 视频流处理 | B-020（音频 ASR 已够） |
| Wasserstein HMM/BOCPD/深度学习 regime 复杂化 | 现有 HMM+CRPS 够用；P9 已有 LSTM-AE+GHMM 拒绝先例；登记观察 |
| RD-Agent/Qlib 框架整体引入 | WSL2 依赖违反 A-005 Windows 约束、与现有 backtest 三引擎+CPCV 栈重复；仅借鉴案例库机制（ALG-03） |
| LLM 直接下单/LLM agent 全权交易 | KTD-Fin/AI-Trader 2026 实证 alpha 证据弱+风控薄弱；宪章 AI 伦理+B-007 |
| 付费数据源（Wind/Choice/iFind 续费） | 约束三（免费/券商自带）；AI-DSD-001 已裁定不续费 |

---

## 8. 参考来源（2026 年检索）

- 机构架构与 AI-native 量化平台：Kanopy Labs《How to Build an AI-Native Quantitative Trading Platform 2026》；DeepTradeX《Decision Architecture for Trading Systems》（模块化决策架构迭代快 40-60%）；Rebellion Research《AI Trading Systems 2026》
- 反过拟合与回测协议：arXiv:2603.09219《AlgoXpert Alpha Research Framework: IS–WFA–OOS》（稳定区选择/灾难否决）；skirmani/ivcalc《2026 Quant Frontier》（CPCV/DML 反幻影）；LuxAlgo/TrendsAndBreakouts 2026 WFA 实践
- Regime 检测：vishruthanand.com《Regime-Based Portfolio Optimization via HMM》（2026-04，84,864 组合网格，横截面特征最强驱动）；arXiv:2603.04441《Wasserstein HMM》（状态身份追踪）
- LLM 因子挖掘：arXiv:2602.07085 QuantaAlpha（轨迹进化，CSI300 IC 0.1501）；arXiv:2502.16789 AlphaAgent（AST 正则抗衰减）；arXiv:2505.15155 RD-Agent(Q)；arXiv:2604.09601 Hubble（AST 沙箱）；东吴金工 2026-01《AI 重塑量化》（调研纪要情绪因子空头端 8.26%）
- LLM 交易 agent 评测（路线验证）：arXiv:2605.28359 KTD-Fin（收益多由 beta/风格解释）；arXiv:2512.10971 AI-Trader（风控是鲁棒性决定因素）；华泰金工 2026-03（LLM-FADT 年化超额 25.36%）
- A 股数据源实践：2026 量化数据获取全攻略（AKShare/Tushare/BaoStock 对比）；SegmentFault《2026 Python 量化数据源避坑指南》（爬虫源零 SLA/封 IP 风险）
- 风控实践：FerroQuant（5% 组合回撤 kill switch）；Nurp 2026（7 项风控策略：波动率调整仓位/多层回撤限制）；TradingEngineeringLab（连败 streak 马尔可夫精确计算）
- 氛围编程社区：0xminds《Vibe Coding Report 2026》（上下文工程五支柱/multi-agent 3×）；腾讯云《2026 从 Vibe Coding 到 Agentic Engineering》（MCP 6400+ 服务器/checkpoint 纪律）；微软 RD-Agent 2026 实测（代码工程能力>推理能力）

---

## 9. 附录：depgraph 全域覆盖核对（2026-08-21 补查，应 Owner 追问）

> 方法：直连 PostgreSQL depgraph 实测（`DepgraphReader`/`get_depgraph_pg_connection`，只读），将 74 域与本报告 §2-§5 覆盖逐一对账。实测：**nodes 6765（production 6560 / design 205）/ edges 13887 / domains 74**（planned 115 经 build_status 列追踪，与总账口径一致）。

### 9.1 覆盖矩阵

| 分组 | 域数 | 覆盖情况 |
|---|---|---|
| 业务主链（数据→信号→组合→执行→风控→报告） | 20 | 17 域原报告已审；3 域本次补审（见 9.2） |
| 扩展/数据期（ML/另类数据/编排/自进化） | 16 | 全部已审（§2-§4 及 STR-01 模板标注） |
| AI 自治治理基座 | 24 | STR-04 纪律项统一覆盖（非业务模块，不逐域审） |
| 0-node 注册表残余 | 14 | 原报告未提及，本次并入 STR-01（见 9.3） |

### 9.2 补审 3 域（原报告未点名）

| 域 | 实测 | 补审结论 |
|---|---|---|
| D_FUNDAMENTAL_SIGNAL | 12 prod + 2 design | 基本面信号域。数据源（tushare 财务）已在 17 Provider 内，FCT 因子注册表族覆盖；与 §4.2 结论一致——缺口不在源在 IC 实证回填（CAND-FAC-003 在途）。**无新增升级项** |
| D_EXEC_SIM | 7 prod | 执行仿真域。CAND-SIM 族（004~006 执行侧接线/propagator 滑点/CRPS 验证）已挂 T3 数据期；与 §4.6 路线验证一致。**无新增升级项** |
| D_KNOWLEDGE | 0 prod + 1 design | 知识库域，CAND-RES 知识族已挂 T3；ALG-03 因子案例库落地后天然成为其首个消费者。**无新增升级项** |

### 9.3 0-node 残余 14 域（并入 STR-01 处置）

D_ARCHIVE_SCRIPTS（deprecated）/ D_ARCH_GUARD / D_ARCH_SCRIPTS / D_BEHAVIORAL_AUDIT / D_CODE_SCRIPTS / D_COMPLIANCE_SCRIPTS / D_CONTRACTS / D_DATA_SCRIPTS / D_INTEGRATION_GATEWAY / D_META_SCRIPTS / D_SECURITY_LLM / D_SEC_SCRIPTS / D_SIGLEGACY / D_STRUCT_SCRIPTS——均为 scripts 迁移墓地或 planned 空域（0 节点），与真空壳同族。**STR-01 处置范围扩至此 14 域**：dormant 标注防 AI 误读，deprecated 域走既有退役流程。

### 9.4 对账总判

**74 域全部盘点完毕，四问结论不变。** 业务主链 20 域逐域有审查结论或既有在途登记；3 个补审域均验证"无新增升级项"；治理基座 24 域由 STR-04+I-GOV-3 v2 年检纪律覆盖；0-node 14 域并入 STR-01。升级清单（§6）维持 12 项，仅 STR-01 范围扩围。

---

## 10. 施工清单（按单施工版 v1，2026-08-21）

> **用法**：每项按「改动点→步骤→验收→登记→避让」执行；进度登记只写 construction_progress_tracker.md（SSoT），本清单不滚动更新、不作第二真源。新模块晋升走 CAND→ROOR/ARCH 流程，Owner 裁定后施工。

### 10.0 通用纪律（每项必守）

1. commit 一律走 GitCommitGateway：`python scripts/git_commit.py --session <id> --files <逗号相对路径> --message-file <UTF-8 文件>`；单域拆笔；禁 `--no-verify`。
2. 新模块只到 testing/stable，production 启用一律挂起等 Owner（宪章 B-007）；新模块四件套必做：creation_token + capability_canonical_file_registry.yaml + module_translation_registry.yaml + architecture_issue_registry.yaml ARCH 条目。
3. **避让在途批**（2026-08-21 时点）：残余四项专项批施工面=`src/zephyr/gov_drift/`（trend_analyzer.py/dashboard.py）、tests/ 各失败簇、scheduler_safety.py、candidate_module_registry.yaml；P0 批施工面=construction_progress_tracker.md、pre_expiry_full_backlog_roadmap.md、日循环 SOP 文件。冲突面一律等对方闭环或后手 rebase。
4. DB DDL/写操作一律先报 Owner 窗口批准。
5. 完工标准=关联测试域复跑零新增红+登记落账，不留口头结论。

### 10.1 批次排序

| 批次 | 项 | 理由 |
|---|---|---|
| 第一批（文档注记+小切口，与在途批零冲突） | INT-01、STR-03、ALG-06、ALG-04 | 不碰对方施工面，立等可取 |
| 第二批（P1 施工） | ALG-01、ALG-02、ALG-03、INT-03、STR-01 | 算法补强+可用性+省 token |
| 第三批（P2 清偿） | STR-02 | 依赖 CAND 登记面（等残余批任务4闭环） |
| 移交项 | RUN-05 → 移交 P0-5 合并执行 | 不单独施工 |

### 10.2 逐项工单

---

**INT-01 硬编码路径收敛（P0 顺手批）**

- **目标**：QMT 模拟盘/通达信/仓根路径全部走 config+paths.py，换盘换机不断链。
- **改动点**（grep 实证 10 处）：
  - QMT 模拟盘 `E:/国金QMT交易端模拟/userdata_mini`：[tick_replay.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/tick_replay.py#L140) L140、[event_driven_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/implementations/event_driven_engine.py#L103) L103、[data_handler.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/data_handler.py#L515) L515、[miniqmt_provider.py](file:///d:/ZephyrAlpha/src/zephyr/governance/data_governance/miniqmt_provider.py#L106) L106
  - 通达信 `E:\tdx\PYPlugins\user`：[sector_snapshot_collector.py](file:///d:/ZephyrAlpha/src/zephyr/data/sector_snapshot_collector.py#L55) L55、[sector_kline_downloader.py](file:///d:/ZephyrAlpha/src/zephyr/data/sector_kline_downloader.py#L48) L48、[tqcenter_provider.py](file:///d:/ZephyrAlpha/src/zephyr/data/implementations/tqcenter_provider.py#L55) L55
  - 仓根 `D:\ZephyrAlpha`：[workspace_telemetry.py](file:///d:/ZephyrAlpha/src/zephyr/shared/io/workspace_telemetry.py#L55) L55、[atomic_transaction_manager.py](file:///d:/ZephyrAlpha/src/zephyr/governance/financial_governance/atomic_transaction_manager.py#L89) L89、[start_scheduler.ps1](file:///d:/ZephyrAlpha/scripts/start_scheduler.ps1#L41) L41
- **步骤**：①`config/.env.qmt` 增 `QMT_SIM_PATH`（与既有 `QMT_REAL_PATH` 同机制），`config/.env` 或 paths.py 增 `TDX_PLUGIN_DIR`；②10 处替换为配置读取，仓根 3 处替换为 `paths.find_repo_root()`；③关联测试改为 mock 配置注入对齐。
- **验收**：`grep "E:/国|E:\\tdx|D:/ZephyrAlpha" src/` 零命中；tests/backtest + tests/zephyr/data 复跑零新增红。
- **登记**：tracker 遗留区一行（无新模块，免 ARCH）。
- **避让**：backtest/data 域与残余批测试簇无文件级重叠；动手前先 `git status` 查对方未提交改动。

---

**RUN-05 彩排断点恢复演练（移交 P0-5，不单独施工）**

- **移交内容**：向 P0 批移交一条彩排验收项——「断进程+断网 5 分钟→恢复→核对持仓快照与断前一致（RPO=0）、恢复耗时<5 分钟（RTO）」，结果登记 tracker。
- **本报告验收口径**：无此演练记录=日循环 SOP 不予通过。

---

**STR-03 simulation 包命名注记（第一批）**

- **改动点**：`src/zephyr/simulation/__init__.py`（或 pipeline_base.py 头部 docstring）。
- **步骤**：docstring 加一行——「本包为实验管线抽象（ExperimentPipelineBase），非 QMT 模拟盘撮合；模拟盘链路见 ex_core/trading_session.py + data/tick_subscriber.py」。
- **验收**：落码+gates 过；零行为变更。

---

**ALG-06 爬虫源禁盘中纪律注记（第一批）**

- **改动点**：`64_data_source_download_spec.md` + 爬虫类 Provider（akshare/baostock 等 implementations）docstring。
- **步骤**：64 号规范增注记——「爬虫源（零 SLA）禁入盘中关键路径，仅离线补充；盘中故障转移链=QMT→券商自带」；Provider docstring 同步。
- **验收**：文档落码。

---

**ALG-04 情绪因子非对称使用口径（第一批）**

- **改动点**：[28_sentiment_cycle_trading.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md) + [26_event_driven_strategy_detail.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md)。
- **步骤**：补设计注记——「情绪信号非对称使用：负面情绪→风险预警/减仓规避；不构建多头信号；sleeve 内择时边界不变」，注明 2026 东吴金工实证出处（本报告 §8）。
- **验收**：两文档落码；版本号变更按 01 号管理规范走。

---

**ALG-01 regime 横截面结构特征（第二批，P1，生死线族）**

- **改动点**：[regime_detector.py](file:///d:/ZephyrAlpha/src/zephyr/regime/core/regime_detector.py) 特征集+特征计算模块。
- **特征清单**（全部日频 OHLCV 可算、PIT 安全）：①截面收益离散度；②平均成对相关（市场相关结构）；③波动率离散；④动量宽度（强于 MA 的股票占比）。
- **步骤**：①特征计算落码（仅用 T 日及以前数据，滚动窗口 walk-forward 归一化，禁全样本归一）；②接入 regime_detector 特征管线，配置开关默认关（A/B 对照）；③无前视偏差测试+34 号 55 用例锚点回归；④A/B 对比报告（开/关特征集的识别稳定性）落 docs/_working/reviews/。
- **验收**：新特征单测绿；regime 域 55 用例+关联域零新增红；A/B 报告在案。
- **登记**：10_regime_detector_spec.md 版本升级；feature 变更记录。
- **避让**：regime 域无在途施工，安全。

---

**ALG-02 WFA 参数稳定区选择+灾难否决（第二批，P1，风险族）**

- **改动点**：[walk_forward.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/walk_forward.py)（+ cpcv.py 如需）。
- **步骤**：①参数选择改稳定区规则——`Ω_stable = {θ | SR(θ) ≥ 0.9·SR_opt}`，取区内代表点（中位/质心），禁选单点最优；②WFA 决策 gate——多数窗口通过+单窗灾难否决（单窗回撤超阈值即整体否决）；③构造悬崖/平台合成参数面用例验证选择行为。
- **验收**：合成用例证明「弃高点选平台」；tests/backtest 零新增红。
- **登记**：52 号/90 号注记+与 B-009 互锁口径。

---

**ALG-03 因子研究案例库（第二批，P1，数据期打底）**

- **改动点**：新模块 `src/zephyr/factor/casebook/`（单文件起步）+ 新 SQLite `data/databases/factor_casebook.db`。
- **步骤**：①schema——`cases(id, hypothesis, factor_expr, factor_json, ic, icir, turnover, verdict, failure_diag, created_at)`，**只存统计量不存持仓/金额**（B-011 合规）；②API——`record_case`/`query_similar`（先按因子族标签检索，向量检索后置不抢）；③新模块四件套登记；④单测（写入-检索-空库/重复边界）。
- **验收**：测试绿；成熟度仅到 testing，production 挂起等 Owner。
- **Owner 窗口**：新 DB 文件 DDL 需批准。
- **避让**：factor 域无在途施工。

---

**INT-03 trading 主进程看门狗（第二批，P1）**

- **步骤**：①实证 AutoRuntimeCore 生产启动方式（查 scripts/register_aux_tasks.ps1+日循环 SOP，确认 `python -m zephyr.trading` 当前由谁拉起）；②仿 [start_scheduler.ps1](file:///d:/ZephyrAlpha/scripts/start_scheduler.ps1) 写 start_trading.ps1（while-true+单实例锁+PID+心跳+孤儿清理），register_guard_tasks.ps1 增注册；③书面确认口径——交易时段自动拉起属「恢复服务」非「生产变更」，与 B-014 不冲突。
- **验收**：手动 kill 进程→看门狗 5 分钟内拉起（RTO 实证）；心跳落盘可见。
- **Owner 窗口**：新计划任务注册（生产变更）需批准。
- **避让**：register_guard_tasks.ps1 若 P0 批在改则后手。

---

**STR-01 空壳/0-node 域 dormant 标注（第二批，P1）**

- **改动点**：实证真空壳 `src/zephyr/research/`、`src/zephyr/alt_data/` + 模板包（cross_asset/data_eng/ml_serve/signal_quality/plan_engine/digital_twin 等以 depgraph design 态为准）+ depgraph 0-node 14 域（§9.3 清单）。
- **步骤**：①空壳包 `__init__.py` docstring 头部加「DORMANT（未启用占位模板，勿当实现引用）」；②depgraph domains 表 14 个 0-node 域 build_status 标 dormant/deprecated（**DB 写→Owner 窗口**）；③module_translation_registry.yaml 同步注记（有条目者）。
- **验收**：AI 检索「研究/另类数据」首命中即见 DORMANT；gates 零新增红。
- **Owner 窗口**：depgraph DB 写需批准。

---

**STR-02 NotImplementedError 38 处分类（第三批，P2）**

- **步骤**：①grep 全量清单（38 处/24 文件）归档；②分类——access_control 族 ~15 处→candidate_module_registry.yaml 登记 deferred（单人单信任域无 RBAC 需求；触发条件=多账户/多用户上线）；③其余逐条归因（补实现挂 CAND / 标 design_maturity=design 并同步 depgraph）。
- **验收**：38 处全部有归宿（deferred/CAND/实现），清单归档裁定书。
- **避让**：candidate_module_registry.yaml 是残余批任务4 施工面——**排在其闭环后**，或后手 rebase 处理段落冲突。

### 10.3 移交/不施工项汇总

| 项 | 去向 |
|---|---|
| RUN-05 | 移交 P0-5 彩排（§10.2） |
| INT-02 盘后管线挂调度 / INT-04 QMT 人工登录注记 | 在途 P0-5 消化 |
| ALG-05 指数成分 PIT | 在途 CAND-MKTDATA-001 / P1-3 |
| RUN-01~04（785 清偿/彩排/对账/drift 复产） | 在途 P0 批+残余批 |
| STR-04 | 纪律项，无施工 |

---

> 本报告为 2026-08-21 快照审计；施工状态以 construction_progress_tracker.md 为 SSoT，候选晋升以 candidate_module_registry.yaml 为 SSoT。
