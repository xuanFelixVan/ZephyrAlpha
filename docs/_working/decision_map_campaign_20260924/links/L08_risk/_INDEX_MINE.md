---
ttl: task_bound
title: L08 RISK MINE INDEX
doc_type: index
---

# L08 风控 · 深挖簿总勾表（9 子块）+ 本环节穷尽性声明

> 车道 LANE-MINE-L08 · 班次 st-qmine-20260925 · 2026-09-26 · 只读挖掘（**全程未触发/未复位任何熔断，未跑测试，未起 GPU/行情作业**）。
> 骨架=`SKEL.md`（本目录）；方法=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` §2/§5/§6；落盘清单=`../../cmd_successor_20260925/landing/lane_mine_l08.yaml`。
> 本表只勾"落盘/三态/触发面/新账"，细节在各簿；各簿对骨架的改判以 `文件:行号` 为证。

## 一、九子块总勾

| 块 | 目录（落盘件） | ② 生产触发面判定 | 三态 | 本簿新账 | 对骨架的关键改判 |
|---|---|---|---|---|---|
| RSK-1 系统级 KillSwitch | `s1_system_killswitch_agent_behavior/MINE.md` | **已接电**（boot_hooks 开机注册 + 三处 journal 探针 + 告警） | MINING（自 SEALED 主动降级） | C12-C16 | 发现编排器层 MOD-AU-002：**系统级拉闸经 `_trip_system` 传播=交易五级物理全触发**（误用面已由"文档约定"变"代码级联"）；日度门 `_collect_l5` 把 AI 行为闸当"熔断"读、把交易熔断硬编码为 absent |
| RSK-2 交易五级熔断+磁盘影子 | `s2_five_level_circuit_breaker/MINE.md` | **部分覆盖未接电**（判定腿 evaluate 零调用；重臂腿已接线但卡单对象另有其人） | MINING | C17-C22 + H1-H7 七洞 | rebuild 已接线（`trading_session.py:401/434-459`，骨架"零调用方"过期）；**闸门 1 探针真源=`DefaultRiskValidator.kill_switch_active`**，非本块五级 ⇒ **HALT 首演现况不可通过** |
| RSK-3 TDM 熔断五级 L0-L4 | `s3_tdm_drawdown_state_machine/MINE.md` | **缺失**（判定腿+消费腿双断；本体是全仓最完整的熔断件） | MINING | C23-C26 | `daily_gate_snapshot.py:382` 是**硬编码常量**而非"读不到"；`persist/load_or_none` 已完备 ⇒ 甲案（接线）代价被骨架高估；`store=None` 时复位三守卫全失效；09-16 覆盖审计"已接电"判据与链路级实测冲突 |
| RSK-4 35 号回撤协议族 | `s4_drawdown_protocol_family/MINE.md` | **核心闭环已接电**（paper 实装配 + 每轮调仓驱动）；家族六件仅破产底线 1 件被生产消费 | MINING | C28-C31 | "§6.5 接线位"从未落地，真装配点=`start_paper_session.py`（`test_start_paper_session.py:153,174` 锁）；`check_bankruptcy_floor` 真源单点已成立（orchestrator 直接 import）；**前端 `query_drawdown_throttle` 每次新建 DrawdownController 且黑天鹅硬编码默认=展示偏乐观** |
| RSK-5 尾部风险 EVT/POT+UP-5 | `s5_tail_risk_evt_pot/MINE.md` | **三腿分岔**：监控腿已接电、VaR 破限折扣腿只读不推进（哑）、对冲信号腿零消费 | MINING | C32-C36 | 尾部评估节拍被绑在调仓事件上（不调仓=整日不评估）；`_var_breach_machine` 全 src 仅"赋值+读 state"两处⇒乘性折扣恒 1.0；UP-5 yaml 注"2026-09-20 已接线"=**图面接线非代码接线**；tail_hedge docstring 与其实现相互矛盾 |
| RSK-6 流动性监控+37 号危机 | `s6_liquidity_monitoring/MINE.md` | **三腿**：恢复门禁腿已接电（check_recovery）、盘中编排腿未接电、日频监控腿无活消费者 | MINING | C37-C41 | MOD-RK-21 无同名类（六组自由函数），orchestrator 只用其 `check_recovery`+状态类；逃生指令真源=MOD-RK-10；`LiquidityMonitor` 声明消费者 MOD-L04-001 **全仓零实例化=永不可达**；IPO 抽离两套实现重复簇；37 号 §4/§5"拒绝清单"与终局量尺冲突 |
| RSK-7 系统性风险五信号+五级 | `s7_systemic_risk_signals/MINE.md` | **市场侧半接电**（仲裁点就绪，生产进料口 provider 缺位）；**组合侧 RK-34 零消费（确证）** | MINING | C42-C46 | `start_paper_session.py:440/538` 自述 systemic_input_provider 未接线 ⇒ **五信号从未在 paper/实盘跑过一轮**；`cn_macro/Swake` src 零命中（独立复证）；RK-34 BLACK 单布尔清仓 与 RK-10 "≥3 信号清仓"两轴互斥 |
| RSK-8 质押否决器+S41 解禁 | `s8_pledge_veto_unlock_pressure/MINE.md` | **否决器已建码但零装配；入参无生产者；质押载体已建库 src 零消费** | MINING | C47-C53（C48 待复证） | 骨架"未建码/零码"改判：`negative_veto.py`（MOD-SIG-137）六检含"解禁>5% 流通盘"已在产码；链的头（候选池 `vetoed` 真源列）尾（L3-08 留痕设计）都在、中间那一脚调用缺；WO-009 `metaq_pledge` 双时态载体（120,628 行源）建成但零消费；解禁今日唯一活路径=前端人看（含 localStorage 与演示数据） |
| RSK-9 逐单否决与约束栈 | `s9_order_veto_constraint_stack/MINE.md` | **否决引擎已接电**（`pre_execution_checker.py:225` 缺省自造）；约束栈 F-C2 三件零 import；P-P1-04 零消费 | MINING | C54-C59 | 单仓上限三口径（8% firm 宣称/20% P40 实跑/25% sleeve）⇒ **宣称的执行者 FirmRiskAggregator 从未被执行**；`position_sizing_engine:8` 四路 `min()` 是"保守者胜"既成立法先例（L08-C01 应据此收口）；P35 T+1 无真源即跳过=唯一放行型硬规则 |

**计数**：9 子块 / 9 份 MINE 全部落盘；**SEALED 0 · MINING 9 · BLOCKED 0**（骨架原为 SEALED 2 / MINING 7——本车道下钻后两块原判 SEALED 均因新组件与新证据主动降级，未因"读不动"降级）。
**设计态零消费（含子件级）统计**：纯"设计态零消费"子块 2（RSK-3、RSK-8）；含零消费子件的子块 7/9；已接电主链 2（RSK-1 编排面、RSK-9 否决引擎面）。

## 二、新账汇总（L08-C12 .. L08-C60；**C27 预留未用**，不复用以避跨车道号段碰撞）

**条数=47**（含 3 条明确标"待复证"：C29 consecutive_loss→sizing 消费链、C48 数据资产挂死模块是否同名不同域、C59 BudgetChanged 事件链三点连测）。


- **P0 级候选 4 条**：C18（重臂对象≠卡单对象，TRD-A12 真前置）、C32（尾部评估被绑调仓节拍）、C39（盘中流动性编排腿零调用）、C43（市场级进料口缺位⇒系统性风险盲区）、C54（单仓上限三口径）——其中 **C43/C39/C32 同根**：都是"缺一个事件驱动的进料口"，可与 TRD-A07 合并成一个"盘中风控事件环"施工包（净零：三包合一，不各造 runner）。
- **P1 治理面成簇**（账实不符家族）：C24、C30、C34、C38、C48 → 同一病根="以模块级判据（有代码）冒充链路级判据（有生产事件链）"；建议统一在覆盖审计词表里加"模块级/链路级"二义标注，并要求 [CONSUMERS] 头声明诚实（模板=`var_intraday_recalc.py:6` 的"设计性死件"写法）。
- **复位/权限闸同族**：C05（既有）、C13（编排器 approver 仅非空校验）、C23（KILL 复位三项确认为自报 bool）→ 建议一批施工"保命复位代码级取证"。
- **展示层重算同族**：C28、C36、C46 → 治本方向统一=前端只读 `RiskLayerSnapshot`/持久化态，禁新建判定实例（`dashboard_feeds.py:462/613`）。
- **物化表同族**：C15、C26、C45、C57 → 全部收敛进 L08-C06（熔断/否决/降级流转全史物化表，生成器产出，事件触发落盘）。
- 引用不重复：SKEL §4 L08-C01/C02/C03/C04/C05/C06/C07/C08/C09/C10/C11 与 13 号文 TRD-A06/A07/A12/A13/A14、LK-13/LK-14/M-55、O-5 全部按原编号引用，未另立。

## 三、L08-C03 / L08-C18 裁定材料已就位

- L08-C03（MOD-RK-049 三选一）：`s3_tdm_drawdown_state_machine/MINE.md` ④ 末表给出甲/乙/丙三案的代码面·数据面·运维面代价与"与现役闭环的关系"，并标注本班立场（甲代价被高估、乙代价被低估、丙不满足终局量尺）。**本车道未拍、未施工。**
- L08-C18（重臂 vs 卡单不同源）三案在 `s2_.../MINE.md` ④：①探针取并集（与仲裁序 v1"保守者胜并集"同构，改 1 处 lambda）②rebuild 内追加 validator 置位（破坏其唯一真源）③判甲为 advisory 并收编入乙（w5_1）。
- 演练前置清单（HALT 首演，Owner high 门位）：C18 收口 → C19（evaluate 旁路）→ C20（影子补 `triggered_at`/`trading_date`）→ C21（损坏影子可辨+降级告警）→ 再谈首演；SKEL §7 步骤 6 现判定为**预期失败**，据 C18。

## 四、本环节穷尽性声明

1. **范围已尽**：SKEL §1 九子块边界照用未重切；每子块对"实码位/配置真源/生产触发面/消费面"四件套做了 grep 或 Read 级实测，未以文档转述代替实测。
2. **骨架 §3 十三项 MINING 债已清 8 项**：状态机守卫与持久化正文（RSK-3）、家族六件接电判定与真实装配面（RSK-4）、tail_hedge 全文与破限链实测（RSK-5）、流动性三件 API 与归属（RSK-6）、RK-34 正文与消费实证（RSK-7）、负面否决器与质押载体（RSK-8）、veto 引擎正文与 F-C2 三件消费实测（RSK-9）、编排器全文（RSK-1）。
3. **未清项全部点名挂账**（各簿 ⑤ 段"未读指针清单"）：35/36/37/53/33/32/30/15/69/16 号 memo 逐节对表；`risk_layer_orchestrator.py`（1900+ 行）与 `drawdown_controller.py`、`tail_risk_monitor.py`（715 行）、`liquidity_monitor.py`（747 行）、`liquidity_crisis_manager.py`（787 行）、`ashare_systemic_risk_detector.py`、`position_sizing_engine.py`、F-C2 三件、三张 blueprint + 十余个外置 ALGO_FLOW 件；`metaq_pledge` 是否已实部署（**未连库，按"脚本在≠表在"保守挂账**）；`alloc_budget_change_log` 写函数调用方。
4. **禁封矿条款遵守**：本环节 7/9 子块含"零消费/休眠/设计态"件，一律标 MINING 而非以"现状规模小、没触发过、AUM 不大"封矿；量尺=终局全貌（Owner 一人 + 100% AI 自制一切可自动化者），故"进料口缺位/推进器缺位/事件链缺位"记为 P0/P1 缺口而非"暂不需要"。
5. **纪律遵守**：零 `git add/commit/push`；零 `scripts/git_commit.py`/`commit_queue.py` 调用；只读取数走文件与只读 grep，未起数据库写；临时观察未落 `.runtime` 根；未触碰 `D:\zephyr_t1_backup\`；未起 GPU 作业、未跑全量测试、未杀进程；**未触发任何真实或模拟盘熔断/停机**；正文无裸"裁定#未登记数字"引用（既有裁定一律以路径+行号指针引用）；无伪造 Owner 署名。
6. **外部对表状态**：已按车道纪律在九块落盘后统一做一轮最小对表（见 §五）；**RSK-3/4 的逐块细对表（Grossman-Zhou / Yang-Zhang / Choi / Riskfolio-Lib / PyPortfolioOpt）与 RSK-8 的 2025 质押新规原文对表仍标"未做"**，交下一班续挖（各簿 ⑥ 段已留候选清单与 A 股适配闸要求）。
7. **结论口径**：本环节**不封矿**（0/9 SEALED）。理由是产出型的：本车道把"两套五级互认"这一抽象缺口，拆成了 C18/C39/C43/C54 四条可独立施工的具体断点，并证伪了 3 条骨架原判；封矿会把这次改判的证据链埋掉。

## 五、外部对表（九块全部落盘后统一做的一轮，按挖矿 SOP：URL+发布方+年份、≥2 独立来源、A 股适配闸）

### 5.1 已获来源与置信分级

| 对表面 | 来源（发布方 · 年份） | 独立来源数 | 置信 | 支撑的本环节结论 |
|---|---|---|---|---|
| 质押履约保障比例/平仓线口径 | [Mondaq《股票质押式回购（上市公司股票质押）体系化解读（上）》](https://www.mondaq.com/china/wealth-management/819070/)（Mondaq·律所作者 · 2026-03-08）；[国元证券 股票质押式回购业务信息公示页](http://www.gyzq.com.cn/main/company_business/credit_business/stock_pledge/gpzy_business_info_publicity/index.html)（国元证券 · 2025-12-24）；[《…股票质押式回购交易业务交易盯市及违约管理规定》模板](https://wk.baidu.com/view/40cd5af25322aaea998fcc22bcd126fff7055dfa.html)（券商内控制度 · 2025-12-09） | 3（1 律所综述 + 2 券商侧，其中 1 为官方公示） | **中** | 履约保障比例=（质押股票市值+孳息）/（融资本息），**警戒线/平仓线为逐笔协议约定 + 券商公示，不是交易所统一常数** ⇒ **A 股适配闸判定：外部无单一常数可直接当否决阈值**。本环节 RSK-8 的 `P45 质押检` 必须走"仓内自校准 + 券商公示区间作量级标尺"，禁把某个魔法数字（如 130%/150%）硬编进 `risk_veto_engine`（对应 L08-C53 算法层缺失，不因此表而闭合） |
| 限售解禁供给冲击 | [财联社《1.7 万亿限售股压境，港股迎来解禁大考，要如何应对？》](http://www.cls.cn/detail/2315767)（财联社 · 2026-03-18）；[同题转载（新浪财经/智通财经/东方财富）](https://fund.eastmoney.com/a/202603173674725279.html)（东财 · 2026-03-17）；[《中国股改限售股解禁的分析研究成果》](https://www.daowen.com/lilun/1721997.html) 与 [《数量型金融约束政策对股票价格的影响》](https://www.daowen.com/lilun/1721993.html)（论文聚合 daowen · 2026-01）；[《量化交易·事件驱动策略》](https://quant67.com/post/quant/11-event-driven/11-event-driven.html)（quant67 · 2026-05） | 4（含 2 学术向 + 2 财经媒体，媒体多为转载同文，**不重复计数为独立来源**） | **中低** | "解禁窗口=可预期的负向供给冲击、应在窗口前降暴露"方向上被支持，但**A 股个股层面的解禁异常收益不稳定且随制度变迁漂移** ⇒ 支撑本环节结论：`negative_veto` 的 5% 流通盘阈值属**未回测常数**，RSK-8 的 S41 减仓逻辑必须先回测再上（不得据外部媒体直接采数）；且"占总股本 vs 占流通盘"两口径在这些来源中混用 ⇒ 加固 L08-C51（口径真源化） |
| risk overlay（波动率目标+回撤限制+趋势过滤）实务与代价 | [Man Institute《V-Shaped Recoveries and Policy Uncertainty: The Role of Risk Overlay》](https://www.man.com/special/v-shaped-recoveries-swiss)（Man Group / Man Institute · 2025-06-05）；[《Man Group：动态风险管理在股票投资组合中的应用》中文转载](https://cloud.tencent.cn/developer/article/1758330)（腾讯云开发者社区转载 · 2020-12-08） | 2（同机构两文，**独立性偏弱，标注为同一发布方**） | **中** | 直接对表 RSK-3/RSK-4：机构 overlay 的已知代价是**V 型复苏中减仓后回补不足**——这正是本系统 RECOVERY 阶梯（`recovery_step_recovered=(0.50,0.75,1.0)`）+ `min_hold_*` 最短持有 + `reset_cooldown_days=3` 要权衡的对象。**结论：迟滞参数不是"越保守越好"，必须做 V 型复苏情景的敏感性回测**（本环节新挂账 L08-C60）；同时确认"overlay 分层"与本仓 `position_sizing_engine:8` 四路 `min()` 的"保守者胜"同构（外部标准件存在，禁自造新机制） |
| EVT/POT 极值阈值标准件 | 沿用 `SKEL.md` §5 已登记教材 McNeil-Frey-Embrechts《Quantitative Risk Management》（Princeton UP），本轮**未重复搜** | 1（教材） | 沿用 | RSK-5 的 `pot_failure_streak` 降级（0.90→0.85）方向与"拟合失败不得放行"一致；参数细对表仍列未做 |

### 5.2 本轮未做（如实标注，禁止冒充已对表）

- **RSK-2 熔断/停机人工双签与冷却实务**：未做（关键词候选=exchange trading halt / circuit breaker reset dual-key / NII 2010 Flash Crash 事后要求）；当前 L08-C13 仅有仓内证据支撑。
- **RSK-4 回撤控制学术标准件**（Grossman-Zhou 1993 / Yang-Zhang 2012 / Choi 2021 公式级对表）：未做，仅在 `SKEL.md` §5 登记，未逐式核对 `capital_curve_manager`。
- **RSK-6 流动性标准件**（Amihud 2002 原始定义与 A 股成交额口径差异、跌停不可成交建模、VPIN 系列）：未做（37 号 memo §4/§5 的"拒绝清单"复审=本轮 L08-C41，外部材料尚未采）。
- **RSK-9 组合约束标准件**（Riskfolio-Lib BSD-3 / PyPortfolioOpt HRP MIT / T. Rowe Price overlay 分层）：未做依赖级对表（许可证与采用方式仍按 `SKEL.md` §5 登记口径）。
- **RSK-1**：AI Agent 行为熔断的外部对标（如 agent guardrail kill switch 实务）：未做。
- 上述未做项**不构成本环节 P0 缺口的成立条件**（C18/C39/C43/C54 全部由仓内实证独立成立），只影响阈值取值，故不因欠对表而阻塞总指挥立项。

### 5.3 本轮对表新增账

- **L08-C60**：RECOVERY 阶梯与 min_hold/cooldown 迟滞参数缺"V 型复苏"敏感性回测（外部机构实务明确指出该代价，仓内 `graduation_*`/`min_hold_crisis=20` 等参数从未做情景检验）——P2，回测类，建议与 L08-C08（D107 回测批）同窗。

