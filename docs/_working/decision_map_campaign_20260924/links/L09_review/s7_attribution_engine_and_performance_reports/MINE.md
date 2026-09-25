---
ttl: task_bound
title: L09-S7 子模块挖矿簿 · 归因引擎与绩效归因报告（Brinson 族）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
status: MINE 完成（六向封口；attribution_results 零行与 sim 归因密度为只读探针实测）
---

# L09 · S7 归因引擎与绩效归因报告

**① 职责一句话**：回答"钱是从哪一层/哪个 sleeve/哪一笔赚来的、亏在哪一步执行"，并把这个答案**回灌**成退役、调权、校准的输入——它是全链自我进化的发动机，也是 L09 里断点最多的一环。

**② 现状实测（2026-09-26）**

### 2.1 引擎侧：算法齐、落盘空

| 件 | module_id | 实码锚 | 成熟度 | 消费方实测 |
|---|---|---|---|---|
| 绩效归因引擎 | MOD-PF-007 | `src/zephyr/pf_core/core/performance_attribution_engine.py`：`brinson_attribute:296`、`factor_attribute:360`、`risk_attribute:389`、`detect_degradation:424`、`detect_crowding:487`、`attribute:550`、`attribute_full:591`、`attribute_multi_period:668`；守恒断言 `total_attribution:157` / `is_consistent:162` | **production** | ①`risk/core/performance_attribution_degradation.py` ②`risk/core/factor_exposure_manager.py` ⇒ **两个消费方全在风险域，报表面零** |
| 多期链接计算器 | MOD-RPT-036 | `src/zephyr/reporting/attribution_calculator.py`（BHB + Carino 恒等，residual<1e-6 门禁） | **testing** | 仅 `attribution_result_store` |
| 归因落库 | MOD-RPT-037 | `src/zephyr/reporting/attribution_result_store.py`（sqlite） | **testing** | 头注 `[CONSUMERS] 归因报告生成链路(54号 BM-REC-02-B); 55号复盘(归因结果消费)` ⇒ **两者均为"将建"语态** |
| 三维归因 | MOD-PLAN-009 | `scenario_attribution_stats`（情景×维度×信号源），由 dloop `attribution` 段调（`daily_loop_master_switch.py:330` 附近 `compute_scenario_attribution(window_days=20)`） | 在产（观察面） | dloop 报告 dict（人看） |
| 执行偏差六类归因 | MOD-PLAN-016 | `execution_deviation_attributor`（纯函数） | 纯函数库 | **零挂点** |
| sim 归因日账 | — | `c1_backtest.sim_attribution_daily`；`scripts/backtest/sim_attribution_report.py` 挂 FIFO 末位 | 在产 | **实测 72 行 / 9 个唯一交易日**（09-14、09-15=47 批量、09-16、09-17、09-18、09-20、09-21、09-23、09-24）⇒ **缺 09-19、09-22** |

### 2.2 本册最硬的一条实测：`attribution_results` = **0 行**
`data/databases/governance.db` 内 `attribution_results` 表**存在、schema 完整、行数 0**。列全集实测：
`id, period, portfolio_id, layer, allocation_effect, selection_effect, interaction_effect, total_return, transaction_cost_drag, net_pnl, invariant_status, computed_at, idempotency_key, schema_version`。
⇒ 结论修正：SKEL S9-7④ 记"MOD-RPT-037 全仓消费方=0（仅 calculator↔store 互引）"——**本册再往下一格：连生产者都没写过一行数据**。三件套（PF-007 production 引擎 → RPT-036 链接 → RPT-037 落库）**没有一条端到端跑通过**，中间断在"谁调用 RPT-036/037"这一拍。
⇒ 与 S6 册"死总线"同构：本仓的典型失效模式是**组件全部就位、装配批次永不落地**（`[CONSUMERS]` 里写"XX 链路/另批"=未装的统一签名）。

### 2.3 TDM C3 树五件 + 一条被本册证伪的销口声明
`config/trading_decision_map.yaml:3782` `TDM-F-C3 绩效归因反馈`（layer C3、point 盘后、activation postmarket、`module_ref:` **空**、`red_reason: structural`、`benchmark_refs: [BMK-INDEX-003, BMK-ABSOLUTE-001]`、`threshold_refs: [THD-RETIRE-001..003]`）。五子枝（`:3952-4146` 实测 `node_id / name_zh / module_ref`）：

| 子节点 | name_zh | module_ref | 事件链挂点 |
|---|---|---|---|
| C3-01 | 多维归因引擎 | `pf_core/core/performance_attribution_engine.py` | dloop `attribution` 段只调 MOD-PLAN-009，**未调本引擎** |
| C3-02 | 升降级管线与退役评审 | `factor/governance/lifecycle_state_machine.py` | **无** |
| C3-03 | sleeve 权重调权 | `pf_alloc/core/regime_meta_allocator.py` | 在 pf_alloc 链上，但**不读归因结果** |
| C3-04 | 参数校准闭环 | `backtest/core/walk_forward.py` | **无** |
| C3-05 | 可靠度养成与信号健康 | `signal_quality/signal_degradation_monitor.py` | **无** |

⇒ "归因产出 → 退役评审 → 调权 → 校准 → 可靠度回灌 L1"这条**自我进化闭环，五根接头一个都没焊**（09 号文"未接线"结论维持，本册给逐节点证据）。

**★ 新发现（本册证伪）**：TDM `:3803` 注称 D50 三项欠账（①交易盈亏/持仓盈亏二分（vn.py 范式：日内成交映射 vs 隔夜持仓映射）②策略级 P&L Explain（底仓/做T/加仓腿分离）③逐笔 TCA（decision price→fill price 滑点归因）"**已由 TDM-F-C3-01 多维归因引擎承接落位（D74 轮）**"。
本册对该文件全 `def` 与关键词做反查（`slippage / decision_price / fill_price / TCA / overnight / trade_pnl / position_pnl / intraday_pnl`）：**零命中**；其方法集为 `brinson_attribute / factor_attribute / risk_attribute / detect_degradation / detect_crowding`。
⇒ **该"承接落位"声明与所指件的能力集不符**——MOD-PF-007 做的是配置/选择/风险的**相对基准归因**，不含成交-决策滑点 TCA、不含交易/持仓盈亏二分。三项仍是活债 ⇒ **LK-15 不得按已销口处理**（宪法 §4.3"文档矛盾=事故"的直接实例；本册只登记证据，不擅改 TDM 正文，TDM 为热注册表须走其自身流程）。

### 2.4 触发面与新鲜度小结
| 对象 | 触发面 | 判定 |
|---|---|---|
| MOD-PF-007 | 被风险域 import（降级检测/因子暴露） ⇒ **无自身节拍**，被动函数 | **已接电（仅限风险消费）** |
| RPT-036/037 | 无任何排班、无事件钩子 | **缺失（零产零消）** |
| MOD-PLAN-009 | dloop `attribution` 段 + `last_audit.json` 实测 `attribution_daily=2026-09-25T00:43:11` 记号 | **已接电**（FIFO 末位，账本→日刊→归因次序） |
| sim_attribution_daily | 同上 FIFO | **已接电**（但 9 日中有 2 日缺） |
| MOD-PLAN-016 | 无 | **缺失** |
| D34 执行成本反馈腿（TRD-A08） | 无 | **缺失·前置阻塞** |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：`sim_trade_log`/`sim_pocket_daily` 等模拟盘四件（S37 在途）、L4-14 执行成本反馈（**断链 D34**）、基准 `BMK-INDEX-003`/`BMK-ABSOLUTE-001`；MOD-PLAN-009 读 `prediction_log` outcome 族（S5 册实测 outcome 仅 4 行 ⇒ **三维归因的输入分母只有 4**）。外部：基准选择与超额收益口径为行业标准域 |
| ②下游 | 内部：C3-02/03/04/05（全断，见 2.3）；风险降级检测 + `factor_exposure_manager`（PF-007 唯二活消费）。外部：归因→再平衡/调权闭环为机构组合管理标准链路 |
| ③算法 | 内部：Brinson-Fachler 三效应守恒（`is_consistent`）+ BHB + Carino 多期链接（residual<1e-6 门禁）+ 因子/风险归因 + 六类执行偏差。外部（对表结论沿用 SKEL §5.1，本册复核其内码判断）：Brinson & Fachler (1985, *JPM*)、Brinson/Hood/Beebower (1986, *FAJ*)＝三效应正典；多期链接 Carino/GRAP/Frongello/Menchero 为行业惯例；**开源候选 pybrinson v1.3.1（PyPI，2026-04-12，MIT）要求 Python≥3.14 而本仓 3.12 ⇒ 只可作离线对账基准，不作运行时依赖**（A 股适配闸：无币种/无涨跌停语义，亦不宜直用）。⇒ **本块欠的是装配，不是算法**（SKEL 结论本册认可） |
| ④后端 | 内部：①**双引擎割据**：归因结果在 sqlite（`attribution_results`，0 行）、sim 归因在 CH（`sim_attribution_daily`，72 行）、情景归因走函数返回值 ⇒ 同一"归因"三处落点，无统一主键（`period` vs `trade_date` vs 无）；②`invariant_status` 列存在即守恒断言可落库（好设计）但 0 行 ⇒ 从未验证过；③`idempotency_key`+`schema_version` 在，幂等基建 ready |
| ⑤前端 | 内部：**无任何归因展示面**（PF-007 的 `[CONSUMERS]` 自称 `D_REPORTING(归因报告消费)`，实测该域无消费件）。Owner 判"哪层不赚钱就砍掉"（13 号文/owner-vision §二.3）**当前无界面可依** |
| ⑥数据字段 | 内部：`transaction_cost_drag` 与 `net_pnl` 列已在归因表 ⇒ 成本腿的**字段**已预留，缺的是**数据来源**（D34）；`layer` 列 ⇒ 逐层归因的分组维度已预留。⇒ "字段在≠数据可得"在本块的精确形态：**列都设计好了，从没写进过一行** |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| LK-15 | 归因三欠账（交易/持仓盈亏二分 + 策略级 P&L Explain + 逐笔 TCA） | **在册·本册证伪其"已销口"声明**（见 2.3★），输入面 L4-14/S37 仍在途 |
| TRD-A08 / D34 | 执行成本反馈断链 | 在册（C3-01 承接的先决输入） |
| L09-C07 | C3 消费闭环接线（C3-01→02→03 盘后事件链） | 在册，本册给逐节点断点表 |
| L09-C06 | 结算聚合报告件（S3 册） | 在册，与本块共用"逐层归因数据源" |
| D50（TDM 注） | 见 LK-15（同一事） | 需回改 TDM 注记为"部分承接/未承接"，走注册表流程 |
| L09-S7-G1（本册主项） | **归因装配链从未跑通**：`attribution_results` 0 行，PF-007(production) → RPT-036(testing) → RPT-037(testing) 三段中间无调用者 ⇒ 一切"归因报告/退役依据"当前无数据源 | 新增·P1 |
| L09-S7-G2（新） | 归因三处落点、无统一期次主键 ⇒ "同一天三个归因答案"可长期并存不被发现 | 新增·P2 |
| L09-S7-G3（新） | MOD-PLAN-009 的输入分母=4 条 outcome（S5 册实测）⇒ 三维归因表当前是**统计噪声**而非结论，但报告形态（dloop 段返回 str 截断 300 字）看不出这一点 | 新增·P1（误导风险高于零数据） |
| L09-S7-G4（新） | `[MATURITY] production`（PF-007）与"无报表消费"并存 ⇒ 成熟度标签测的是算法完备度、不是链路完成度，二者需在词表上分离（与 S2 册 G1 同题，本册供第二例） | 新增 |
| L09-S7-G5（新） | 周/月复盘编排（55 号规划）未建；`sim_deviation_report.py` 月度件与 55 号关系未澄清 | 沿用 SKEL §三未挖清单第 4 项，**本册标为未挖** |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 / 解锁条件 |
|---|---|---|
| 引入外部归因库（pybrinson 等） | **封矿** | 三重理由：①仓内 PF-007/RPT-036 已是 Brinson/BHB/Carino 同构且带守恒门禁；②pybrinson 要求 Python≥3.14，本仓 3.12（RULE-ENV 硬约束）；③A 股适配闸未过（无涨跌停/无 T+1 语义）。**限定：封的是"换算法引擎"，不封"归因消费面"**——后者由 G1/L09-C07 承接 |
| L09-S7-G1 装配链打通 | **施工（P1）** | 这是"发动机没挂上传动轴"的最小可解步骤：写一个盘后编排件把 PF-007 的输出喂 RPT-036→037（各件均已存在，净零=零新算法零新表）。解锁条件=无（不依赖 D34/L4-14，因 Brinson 三效应所需输入是现有持仓/基准）；**但 `transaction_cost_drag`/TCA 相关字段保持 NULL 并在报告上显式标"成本腿未接"**，禁止以 0 或估算填充（RULE-DATA-OPS 精神） |
| L09-S7-G3 小样本误导 | 施工（P1，与 G1 同批） | 归因/三维输出必须自带样本量与窗口（n、日期跨度）⇒ 终局全貌下"Owner 自己记得这只有 4 条"不可自动化。**不许以"现在样本少"作为推迟的理由**（方法论明令禁以现状规模小封矿），反过来说：正因样本少，才更不能让它看起来像结论 |
| L09-C07 五接头闭环 | **挂起排期 + 解锁条件** | 解锁=①G1 先跑通产出行（否则 02/03 评审的是空气）②TRD-A08/D34 成本腿先行（原账本已如此记）③涉及调权与退役 = 资金破坏性域（宪法 §5.2 high 门位）⇒ 必须 Owner 门位，不许 AI 直改 `regime_meta_allocator` 权重来源 |
| LK-15 三欠账 | 挂起排期 | 解锁=输入面 L4-14 逐笔成交价（fill price）可得；**同时须回改 TDM `:3803` 注记**——本册已给能力集反查证据，改注记属注册表变更，交热文件专批（本车道不动 TDM） |
| L09-S7-G2 统一期次主键 | 施工（P2，随 G1） | 归因三落点先约定 `period` 语义=交易日 + 引擎 + run_id 三元组；越晚定越难改 |
| L09-S7-G4 成熟度词表 | 移交（非本块施工） | 证据已备两例（S2、S7），交 06/07 治理车道 |
| 周/月复盘 | 挂起排期 | 解锁=G5 澄清后；不许以"日频还没满"封矿 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | 三件头注 + PF-007 全 `def` 清单 | signal | 算法面 production 且方法集完整（brinson/factor/risk/degradation/crowding/multi-period） |
| R2 | 全仓 grep 归因件 import 方 | signal | PF-007 唯二消费全在风险域；RPT-036/037 互引成环 |
| R3 | `attribution_results` 行数 + 列全集（sqlite 只读，经仓内 `get_db_connection` SSoT） | signal | **0 行 ⇒ 端到端从未跑通**（本册主发现） |
| R4 | `sim_attribution_daily` 逐日密度（CH 只读） | signal | 72 行/9 日、缺 09-19/09-22，与 S4/S5 册同源缺日 |
| R5 | TDM `:3782-4146` C3 段五子枝 `module_ref` 逐条读 | signal | 五接头零焊；父节点 `module_ref` 为空 + `red_reason: structural` |
| R6 | 对 D50"已承接落位"声明做能力集关键词反查 | signal | **证伪**：零命中 slippage/decision_price/fill_price/trade_pnl 等 ⇒ LK-15 仍活 |
| R7 | 外部对表 | **部分** | 沿用 SKEL §5.1 已核结论（Brinson 1985/1986 正典、pybrinson 1.3.1 MIT/2026-04-12/Py≥3.14、DolphinDB 工程口径 2025-01）；**本册未做独立二次核验**，延至统一轮，登记为"未做外部对表（引用为前批已核）" |

**本册封矿判据**：六向封口；归因链断点从"未接线"下钻到"0 行数据 + 五节点逐个无挂点 + 一条虚假销口声明"三层实证；封矿范围严格限定为算法选型层。⇒ **子模块封矿**。
