---
ttl: task_bound
title: RSK-3 MINE
doc_type: log
---

# RSK-3 TDM 熔断五级 L0-L4 状态机（X-R1-01/02/03）— 深挖簿

> 车道 L08 风控 · 子块 3 · 班次 st-qmine-20260925 · 只读挖掘（未跑测试、未触熔断）。
> 起点真源=`../SKEL.md` §2 RSK-3 + §3 MINING 清单 + §4 L08-C03。本簿主产出=**L08-C03 三选一裁定材料（代码面/数据面/运维面代价）**；裁定权在 Owner，本班只出案卷。

## ① 职责一句话

把"组合日亏 + 组合回撤"双轴读数收敛成一个**带迟滞、带最短持有、带复位守卫、可持久化**的熔断级别，并对下游只暴露语义化输出（position_cap / defensive_only / recovery_factor）。

## ② 现状实测（生产触发面判定：**缺失（判定腿与消费腿双断，但状态机本体是全仓最完整的熔断件）**）

| 面 | 实测（本层高价值更正用 ★） |
|---|---|
| 实码 | `src/zephyr/risk/core/drawdown_state_machine.py`（MOD-RK-049）：六态 `NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY`（`:94-102`）；配置卡 `:146-173`（默认 dd 5/10/15/25% + VaR95 2/4/6% + CVaR10% + hysteresis 0.5 + sustained 3/3/5 + min_hold 5/10/20 + recovery_step 5 + 毕业准则 + `reset_window_days=20 / max_resets_per_window=3 / reset_cooldown_days=3 / permanent_lock_threshold=5`）；`__post_init__` 阈值单调性硬校验 `:175-209` |
| ★ 转换/降级/复位三守卫均已实现（骨架 MINING 债清空） | 降级路径表 `_DEESCALATION_PATH :120-124`（CRISIS→DANGER→WARN→NORMAL，禁跳级）；KILL 唯一出口 `request_manual_reset :560-613`：先查"仅 KILL 态可复位"→ 三项确认（持仓清零/挂单已撤/锁新开仓）→ 永久锁定（`total_resets ≥ 5` CRITICAL 留痕后拒）→ 冷却期（`:584-589`，按 **calendar days**）→ 窗口计数（`:590-595`）→ 追加 reset history → 迁 RECOVERY step 0 → `persist()` |
| ★ 持久化面已实现（骨架"无可达落盘位"需精确化） | `snapshot()/persist()/load_or_none()` `:617-692`：经 `JsonStateStore.save/load(self._state_ns)`，损坏记录抛 `InvalidDrawdownStateError`（`:688-691` 注释明确"消费方必须 fail-closed，本层不兜底"）、`recovery_step` 越界拒载（`:690-691`）。**缺的不是能力，是"装配 + 调用点"** |
| ★ 消费腿断链的**性质**被本班改判 | 骨架/13 号文记 `daily_gate_snapshot` 读态恒 `absent`。实测位置=`src/zephyr/strategy_pipeline/daily_gate_snapshot.py:382`，且它是 **硬编码常量赋值**：`out["drawdown_state_machine"] = {"status":"absent","error":"no_persisted_level_v1"}`——**上方 `:374-381` 的 try 只读 kill_switch（且 kill_switch 读失败有 conservative_treatment="tripped"），drawdown 一侧连一次 `load_or_none()` 尝试都没有**。同函数注释 `:370-371` 自称"v1 无持久化级位可读=absent 如实登记"——登记诚实，但**读代码是零行而不是三行** |
| 实例化面（唯一） | `drawdown_session_persistence.py`（`premarket_initialization` / `postmarket_persist` 两入口 **src 零调用者**），并由 **上锁测试** 固化：`tests/risk/test_risk_signal_consumer_wiring.py:168-173`（`assert set(files) == {SESSION_PERSIST_FILE}` + 两入口 `_call_sites(...) == {}`，消息="若被调用则需重新核定"）=**tripwire 型诚实锁，接线必须同批改该测试**（施工面代价，不是障碍） |
| 账实矛盾（文档事故候选，新证） | `docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md:160-162` 判 TDM-X-R1 / X-R1-01 / X-R1-02 = **"已接电"**，理由列"drawdown_state_machine 有 session_persistence+defensive_whitelist 消费"——被本班实测证伪（session_persistence 自身零调用者；defensive_asset_whitelist MATURITY=design 只声明不判定）；同页 :162 判 X-R1-02 `drawdown_liquidation_guard` 亦"已接电"（该件 src 内除 algo_flow/registry 登记外无消费点，`capability_canonical_file_registry.yaml:6122` 有蓝图卡）。**口径来源=模块级"有代码即接电"，与链路级判据（有生产事件链）冲突** → 建议登记为账实不符样本（L08-C24） |
| 阈值三套并存（骨架已记，补实测） | TDM 叙事 L1≥2%/L2≥4%/L3≥6%/L4 回撤 25%（`config/trading_decision_map.yaml:3193-3227`）∥ 代码默认 dd 5/10/15/25% + VaR/CVaR 轴（`:146-153`）∥ `alert_threshold_registry.yaml:64-102` THD-DRAWDOWN-001/002/003=5/10/15%。**代码默认值与 TDM 叙事在 L1/L2/L3 上不同名同值**，yaml 内 `module_ref: src/zephyr/risk/core/drawdown_state_machine.py`（`:3216`）却把两者绑成同一节点 |
| 词汇面（新） | `docs/_working/vocab_legislation/02_state_vocabulary_mapping_register.md:85` X5：`RECOVERY` 三轴同名（HMM regime / 风控状态机 / StockCategory），立法"同名不同轴、禁互转"——本块态名与 :87 `var_breach_state_machine.py` 的 RECOVERY 同族，**跨簿消费时必须带轴前缀**，否则 L09 复盘/前端展示会串轴 |

## ③ 六向台账

| 向 | 台账 |
|---|---|
| 上游 | 调用方注入 `evaluate(trade_date, drawdown_pct, var_95, cvar_95, recovered_pct, black_swan_systemic, strategy_pnls)`（`:344-359`，**全仓零生产调用方**）；数据源本应=组合净值/回撤（S70）+ MOD-RK-05 VaR 口径；数据断流语义=维持级别不降级（fail-closed，D103，TDM 侧叙事） |
| 下游 | 语义输出四件：`position_cap`（`:312-326`：NORMAL 1.0/WARN 0.8/DANGER 0.5/CRISIS 0.3/KILL 0.0/RECOVERY 0.25×(step+1)）、`recovery_factor`（`:329-335`，非 RECOVERY 恒 1.0、KILL 恒 0）、`defensive_only`（`:338-340` CRISIS/KILL 禁新开）、`kill_switch_closed`（`:308-309`）——**四者现役均无消费方**；名义消费方 `defensive_asset_whitelist.py:55`（design，声明"只消费不判定"）、X-R1-02 `drawdown_liquidation_guard`（design，`decision_algo_registry`/`backtest_backlog:1499` 有卡无链）；`daily_gate_snapshot._collect_l5()`（硬编码 absent） |
| 算法/机制 | 升级单调取最严可跳级；降级三守卫（半阈值 hysteresis 0.5 + min_hold + sustained 窗 + VaR 交叉验证）；RECOVERY 阶梯 0→1→2（`recovery_step_recovered=(0.50,0.75,1.0)`）+ 毕业准则（≥3 笔 / 连盈 3 / expectancy ≥0.3R / 守规率 ≥80% / 单笔亏损 ≤1.2R，窗口 10）；`recovery_freeze_days=5`（恢复期 dd>5% 冻结）；日推进计交易日的幂等约定（`:265-267`）；与 36 号 `var_breach_state_machine` 的正交分工=**账户级已发生回撤** vs **组合级前瞻风险**，经 `drawdown_controller.evaluate(var_breach_state=…)` context 参数**乘性折扣**协同（`module_translation_registry.yaml:59352` 大白话卡，"任一触发即整体保守，不累乘冲突"） |
| 后端 | 依赖 `JsonStateStore`（同族后端另见 `scripts/start_paper_session.py:494 state_store = JsonStateStore(state_dir or _RISK_STATE_DIR)`、`scripts/backtest/sim_daily_runner.py:978 JsonStateStore(PLAN_BRIDGE_RISK_STATE_DIR)`——**两个真实运行装配点都已存在，只是装的是 DefaultRiskValidator 而非本件**）；双 namespace：`DRAWDOWN_STATE_NAMESPACE` + `RESET_HISTORY_NAMESPACE`；`store=None` 时 `persist()` 跳过、reset history 走 `getattr(self,"_mem_reset_history", …)`（`:694-704`）→ **进程重启即清零，冷却/窗口/永久锁定三守卫在纯内存模式全部失效（新缺口 L08-C25）** |
| 前端 | 无 UI 消费实证；L5 门快照键 `drawdown_state_machine` 已占位（编排器降级矩阵按 absent 层折算 no_trade，见 `2026-09-16-daily-orchestrator-blueprint.md:110`）→ **前端可见性=有槽位无真值** |
| 数据字段 | 快照载荷 `current/recovery_step/days_in_state/dd_history(窗内)/freeze_days_remaining/as_of_date/last_transition{from,to,reason,trade_date,from_step,to_step}`（`:634-653`）；reset history `total_resets/records[{date,confirmed_by,reason}]`（`:597-604`）；**缺字段**：级别判定时输入读数留痕（dd/var/cvar 三值未随 transition 落盘 → 事后无法复核"当时凭什么升级"）、无 `source`/`data_quality` 轴（断流日与正常日同态）；熔断流转全史**无物化表**（骨架 L08-C06） |

## ④ 缺口清单 + **L08-C03 三选一裁定材料**（不拍、不施工）

**新缺口**：

| # | 缺口 | 证据 | 判级 |
|---|---|---|---|
| L08-C24 | 账实不符：09-16 覆盖审计以"有代码即已接电"判 X-R1/01/02，与链路级实测冲突（本块与 RSK-4 家族头注 §6.5 矛盾同源） | `2026-09-16-skeleton-coverage-audit.md:160-162` vs `test_risk_signal_consumer_wiring.py:168-173` | P1（治理面：判据词表需加"链路级/模块级"二义标注） |
| L08-C25 | `store=None` 静默降级：复位三守卫（冷却/窗口/永久锁）在内存模式下形同虚设，构造期无 WARNING | `:694-704` + `:629-632` | P1（保命守卫的"无 store 即哑"应 fail-closed 出声） |
| L08-C23 | 复位三项确认=调用方自报 bool，无代码取证（持仓清零/挂单撤清本可由券商侧 + 现成幽灵检测 `default_risk_validator.py:71 GHOST_KILL_SWITCH_ACTIVE` 交叉核验） | `:565-570`（ResetConfirmation `:237-245` 默认全 False 但可由 caller 直接置 True） | P1（与 RSK-1 L08-C13 / RSK-2 L08-C05 同族：保命复位三处都缺"代码级取证"） |
| L08-C26 | 转换记录不落输入读数 → 升级/降级不可事后复核（终局全貌要求：100% AI 自制 = 每一次熔断流转必须自证） | `:641-652` | P2 |

**L08-C03（MOD-RK-049 三选一）裁定材料**：

| 案 | 代码面代价 | 数据面代价 | 运维面代价 | 与现役闭环的关系 |
|---|---|---|---|---|
| **甲：接线** | ①`drawdown_session_persistence.premarket/postmarket` 挂进日度编排/盘后链（1 个事件订阅点，禁 cron——运维红线 3）②`daily_gate_snapshot.py:382` 由常量改为 `load_or_none()` 读态 + 异常折算 conservative（约 5 行，与 :374-381 kill_switch 同款模板）③JsonStateStore 根目录装配（复用 `start_paper_session.py:494` 的 `_RISK_STATE_DIR` 模板）④`position_cap/defensive_only` 接入 sizing/权重链，或明确"只由 DrawdownController 消费"避免双头 ⑤同批改 `test_risk_signal_consumer_wiring.py:168-173` tripwire + `drawdown_state_machine.py:6` 自述头注 | 快照结构已定（`DrawdownStateSnapshot`），仅需补 2 字段（输入读数 + 数据质量轴，L08-C26）；THD 卡与 yaml 叙事阈值须**二选一收口**（三套数字并存不可持续） | 多一条日度状态链要维护"数据断流不降级"的告警面；复位链引入三项确认的取证施工（L08-C23）；tripwire 测试要重登 | 与 DrawdownTracker/Controller（RSK-4 现役）**功能重叠但语义更严**（迟滞/min_hold/永久锁在现役闭环中均无对应）→ 接线等于用设计件替换现役判定轴的一部分，**必须同批定义两轴冲突时谁说了算（并入 L08-C01 仲裁序）** |
| **乙：收编** | 把本件的**独有守卫**（hysteresis 半阈值 + min_hold + RECOVERY 阶梯 + 毕业准则 + 复位守卫）作为 `DrawdownController` 的判定内核或共享 util 抽用；删除/退役 MOD-RK-049 独立身份 | 无新表；状态字段并入 Controller 现有落盘（需先测 Controller 是否已有持久化与键位，未测=本项材料缺口） | 只留一条回撤链，运维面最省；但需重登 blueprint/decision_algo_registry/backtest_backlog 三处身份（`capability_canonical_file_registry.yaml:6118,14279,39483`） | 符合 w5_1"同域重复簇→收敛唯一"；风险=守卫实现随身份退役而丢（须逐守卫搬迁，工作量>甲的"只读接线"） |
| **丙：退役** | 删件（+ 删 session_persistence 的状态机腿、删 3 处登记、改 tripwire 测试） | 零 | 零；但 `docs/03_modules/_domain_risk/drawdown_state_machine/`（blueprint/index/algo_flow）成套文档资产变孤儿，须同批退役 | **代价最低但能力净损**：仓内将无"迟滞 + min_hold + 永久锁定"型回撤守卫（现役 Tracker/Controller 无此三件）→ 与"终局全貌量尺"相悖；且 X-R1-02/03（保命清算门+护盘白名单）设计上以本件级别为输入，退役会连带悬空 L08-C08 |
| 本班立场 | 只出材料：**甲的数据/代码代价被骨架高估**（读态是 5 行常量替换、持久化能力已完备、装配模板在两个真实脚本里现成）；**乙的隐性代价被低估**（守卫搬迁）；丙不满足终局量尺 | — | — | 裁定归 Owner（high 门位，涉注册表净删/流转） |

引用不重复：L08-C01（双五级仲裁序）、L08-C03（本项）、L08-C06（流转全史物化表）、L08-C08（R1-03 白名单回测 or 显式休眠，禁永久 proposed）、LK-13/LK-14、M-55。

## ⑤ 自审闸三态裁定

**MINING**。骨架 §3 的四条 MINING 债中"状态机正文 160 行后"已清空（本簿给出守卫/持久化实现行号）；仍欠：
1. `docs/03_modules/_domain_risk/algo_flow/drawdown_state_machine.yaml`（ALGO_FLOW 外部件，推导图与代码口径核对）；
2. `drawdown_session_persistence.py` 正文（它如何构造 store、是否真为唯一实例化点、premarket/postmarket 的输入从哪取）；
3. `drawdown_liquidation_guard.py` 正文 + blueprint（X-R1-02，账实矛盾另一半）；
4. 69 号 design memo §2.34；
5. `var_breach_state_machine.py` 正文 + `drawdown_controller.evaluate(var_breach_state=…)` 的乘性折扣实现（乙案材料必备）；
6. `alert_threshold_registry.yaml:64-102` THD-DRAWDOWN 卡的消费方（阈值收口要选真源）。
禁以"设计件规模小/无人消费"封矿——量尺=终局全貌。

## ⑥ 挖矿日志

- 读 `../SKEL.md` → 定本块主产出=L08-C03 裁定材料（骨架只给了"欠账"未给"三案代价"）。
- Read `drawdown_state_machine.py:120-360`（配置卡/守卫/输出面）+ `:560-710`（复位守卫/持久化/reset history）→ 清空骨架 MINING 债首项，并发现 L08-C25（内存模式守卫失效）。
- Grep 全仓 `drawdown_state_machine|no_persisted_level_v1|liquidation_guard` → 命中 09-16 覆盖审计"已接电"判定（账实矛盾）+ 词汇立法 X5 + 上锁测试。
- Read `daily_gate_snapshot.py:340-409` → **决定性证据**：L5 读态是硬编码常量（:382），同函数 kill_switch 侧有 try+保守侧处理，drawdown 侧零尝试。
- Read `test_risk_signal_consumer_wiring.py:140-215` → 拿到 tripwire 语义；**顺带挖出跨块事实**：`DefaultRiskManagerOrchestrator`（MOD-L04-001）全仓零实例化=永不可达（:160-165），ConcentrationMonitor/IntradayVarRecalcController/CrowdingMonitor 三只监控器零消费——直接改写 RSK-6/RSK-9 的"下游消费"台账（已分别记入）。
- Grep `JsonStateStore(` → 两个真实装配模板（paper/sim runner）都装 DefaultRiskValidator，佐证"能力现成、只是没装本件"。
- 纪律：只读；未实例化状态机、未跑测试、未写 `.runtime` 根；无 git 写。
- 外部对表：未做（留统一轮；候选=回撤控制标准件 Grossman-Zhou 1993 / Yang-Zhang 2012 / Choi 2021，`../SKEL.md` §5 已登记，本块 hysteresis+min_hold 与机构 risk overlay 的"降仓后不得立即回补"实务对表）。
