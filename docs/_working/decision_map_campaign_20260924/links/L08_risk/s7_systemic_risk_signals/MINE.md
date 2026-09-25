---
ttl: task_bound
title: RSK-7 MINE
doc_type: log
---

# RSK-7 系统性风险五信号 + 绿黄橙红黑五级 — 深挖簿

> 车道 L08 风控 · 子块 7 · 班次 st-qmine-20260925 · 只读挖掘。
> 起点真源=`../SKEL.md` §2 RSK-7（其④"仓内未见编排层消费 RK-34 的代码实证"由本簿升级为确定结论，其⑤"地图口径矛盾"给出裁决）。

## ① 职责一句话

两条正交轴各判一次系统性风险：**市场侧**（五信号→三级警报：融资盘平仓潮/量化踩踏/流动性危机/政策转向/外围冲击）与**组合侧**（VaR/CVaR/单日亏/连亏/流动性标记→绿黄橙红黑五级→联动指令），并在最严档把动作交给熔断仲裁点。

## ② 现状实测（生产触发面判定：**市场侧=半接电（仲裁点就绪但生产进料口缺位）；组合侧=零消费（RK-34 无任何 src 消费者）**）

| 件 | 实码 | 生产触发面实测 |
|---|---|---|
| `risk/core/ashare_systemic_risk_detector.py`（MOD-RK-10） | 类定义 `:266`；`check()` 五信号互斥检测 + 情绪断路器；三级=1 信号停开仓 / 2 降 30% / ≥3 清仓；`build_escape_directive(alert)` 是**逃生指令唯一真源**（RSK-6 归属改判的落点） | **半接电**：仲裁点侧完备——`ex_core/risk_layer_orchestrator.py:159` import、`:505-506` 构造参数、`:991` 接线语义"systemic_detector 与 systemic_input_provider **成对注入即生效**"、`:1004-1005` 取实例与 provider、`:1030` detector.check 失效→本轮跳过（状态保持）、`:1062` LEVEL_3→`build_escape_directive`→`_engage_kill_switch`、`:1092/:1138` 降级门禁**直接读 `detector.config` 阈值**（37 号 §3.6"真源唯一"）。**但唯一生产装配点自述缺料**：`scripts/start_paper_session.py:440` 与 `:538` 明文"**未接线（缺市场级进料口生产者，登记 tracker）：systemic_input_provider**" → 生产中成对注入不成立 ⇒ `_evaluate_systemic_risk` 整轮不执行，五信号扫描**从未在实盘/paper 跑过一轮**（`:469-470` 的 `systemic_detector=… systemic_input_provider=lambda: {…}` 是头注用法示例，非装配点） |
| `risk/core/systemic_risk_alert_state_machine.py`（MOD-RK-34，绿黄橙红黑） | 配置校验 `:100-124`（VaR 档边界严格递增 + **CVaR 黑档阈须高于 VaR 红档阈，防档位语义重叠**）；`RiskDirective:128-135`（`new_position_scale/reduce_pct/close_only/liquidate_all/trigger_kill_switch`，注释标"纯数据，执行归编排层"、kill 标记"MOD-INF-016 消费"）；`assess():175-229+` **五路检测不短路（理由全量）**、`_require_finite` 非有限值抛错 Fail-Closed、迁移历史只追加 `:160,171-173` | **零消费（确定结论）**：全 `src/`+`scripts/` grep `SystemicRiskAlertStateMachine` 仅命中定义 `:154`、`__all__ :57`、`risk/core/__init__.py:95-114` 导出、自家测试；**编排层零 import** ⇒ SKEL④的"未见实证"升级为"确证无消费者"。且其 BLACK 指令目标 `MOD-INF-016`（交易五级）自身在生产链无拒单消费点（RSK-2 实测：逐单闸真源=DefaultRiskValidator）⇒ **RK-34 的输出是"两处都断"的双层死链** |
| 市场侧原料 S33 | `cn_macro` / `Swake` 在 `src/`+`scripts/` 内 **grep 零命中**（本簿实测，非引用 14 号文）→ 融资余额/政策新闻/外围指数三条原料无代码级引用；MAC-15 条注册无供数绑定（SKEL 已记） | **原料面缺失**（"字段在"≠"数据可得"：即使有表，未见 provider→detector 的输入装配） |
| 重复簇登记（新） | `data/architecture_health/latest.json:54` 簇(4) 把 `risk/core/drawdown_state_machine.py:current() L343` 与 `risk/core/systemic_risk_alert_state_machine.py:current_level() L208`、`feedback_loop/meta_harness_optimizer.py:current_config() L296` 列进同一 extract 克隆簇 | 状态机 getter 同构=克隆守卫观察项（内收 w5_1 同域重复簇候选，禁各造第三套状态机） |

## ③ 六向台账

| 向 | 台账 |
|---|---|
| 上游 | 市场侧：`systemic_input_provider()` 返回 Mapping（市场级输入：融资余额变化、成交额/换手、政策新闻情绪、外围指数、量化拥挤度）——**生产无生产者**；组合侧：`assess(var95_pct, cvar_pct, daily_pnl_pct, prev_day_pnl_pct, liquidity_crisis)` 五入参由调用方注入，VaR 口径=MOD-RK-05，`liquidity_crisis` 上游口径声明"MOD-RK-048/21"（RSK-6） |
| 下游 | RK-10 → orchestrator `_evaluate_systemic_risk` → `build_escape_directive` → `_engage_kill_switch`（单一仲裁点，与回撤/破产/流动性/五态降级共六源合流，见 `arbitration_order_v1_draft.md:103`）；RK-10 → `liquidity_crisis_manager.py:656,685`（`detector or AshareSystemicRiskDetector()` 自建默认，且头注 `:34` 明写"本模块不提供第二套检测阈值，触发阈值一律从 check() 取"=**阈值真源单点，正面样板**）；RK-34 → 名义上"编排层执行 + MOD-INF-016 BLACK 标记 + 风险仪表盘"，**三者实测均无代码链接** |
| 算法/机制 | 五信号互斥检测 + 情绪断路器（防误清仓）；命中数→三级（1/2/≥3）；RK-34 取最严级（BLACK 可由 `liquidity_crisis=True` **单布尔直接触发**，`:207-208`）；VaR 分档 [2,4)/[4,6)/≥6%、CVaR≥10%、单日亏 -2%/-4%、连 2 日 -1%（配置默认，校验强制单调）；理由全量不短路（可解释性优先）；Fail-Closed 输入校验 |
| 后端 | detector 无状态实例可被多处自建（`liquidity_crisis_manager:685` 默认新建=**阈值实例化多点，但值单源**）；RK-34 `_history` 纯内存列表（进程重启清零，迁移史无处落，同 RSK-6 L08-C40 病根）；orchestrator 降级机读 `detector.config` 复用阈值（无第二套） |
| 前端 | 名义"风险仪表盘"消费 RK-34 五档 = **无实现**（`frontend/services/dashboard_feeds.py` 内无 SystemicRiskAlertStateMachine 引用，实测）；warroom 现有位是 BFE-26/30/31（回撤/流动性/尾部），五档系统性色带未接 |
| 数据字段 | RK-34 入参五字段 + `RiskLevel` 枚举 + `SystemicRiskAssessment{level, directive, reasons}`；RK-10 输入=市场级 Mapping（**字段清单未真源化**：provider 应返回哪些键、谁负责产数，`start_paper_session.py:440` 只说"缺生产者"）；缺：信号命中明细/断路器状态/级别流转的物化字段（L08-C06）；`prev_day_pnl_pct` 需跨日真源（当前无声明的取数口） |

## ④ 缺口清单（本层新增）

| # | 缺口 | 证据 | 判级 |
|---|---|---|---|
| L08-C43 | **市场级进料口生产者是五信号链的唯一断点**：detector+仲裁点+降级门禁全就绪，只差一个 provider（且其原料 S33 三源在代码层零引用）→ 本块施工=产数（CH/akshare 侧）+ 一个 provider 闭包，不是重造算法 | `start_paper_session.py:440,538`；`orchestrator:991-1030`；`cn_macro/Swake` 零命中 | **P0**（系统性风险"看不见"是当前最大单点：2015/2016/2024 型流动性事件在本系统内**不会被五信号捕获**） |
| L08-C42 | **五信号"≥3 才清仓"与 RK-34"流动性标记单布尔即 BLACK 清仓"两轴并存且互斥**：若同时接电，同一分钟可判"清仓"与"只停开仓"，无仲裁（正是 L08-C01/TRD-A13 仲裁序必须覆盖的第 7、8 源） | `ashare_systemic_risk_detector` 三级语义 vs `systemic_risk_alert_state_machine.py:207-210` | P1（裁定材料已交 `arbitration_order_v1_draft.md`，本条补具体冲突样例） |
| L08-C44 | RK-34 双层死链（无消费者 + 其 BLACK 目标 MOD-INF-016 无拒单消费点）→ 三选一裁定（接编排层/收编进 RK-10 三级/退役）需并入 L08-C03 同一次内收窗口，禁"两套五级"长期并行 | 本簿 ② 表 | P1 |
| L08-C45 | RK-34 迁移史纯内存（`_history`）→ 五档流转不可复盘、不可回测校准（θ 校准需要历史命中序列，与 L08-C07 crisis_gate 0 行同病） | `:160,171-173` | P2 |
| L08-C46 | 前端五档色带未接（面板读的是 RK-10 侧的 BFE-26/30/31 三行且 mock） | `live.html:287` | P2 |
| 引用不重复 | SKEL RSK-7⑥（RK-34→编排层接线缺口、S33 原料零引用、BM-RC-06-C 三级警报清仓执行设计态、crisis θ 校准 O-5/TRD-A14）；`battle_map_09_risk_control.md` 两节点"自报 production / 有效状态🟧"矛盾 → 本簿裁决：**仲裁点与算法=production，进料口=未接线**，地图应写"半接电"而非单态 | — | 已在账 |

## ⑤ 自审闸三态裁定

**MINING**。骨架 §3 三项债：本簿清空"RK-34 正文 120 行后"（配置校验/指令结构/assess 五路逻辑/历史面已读，`:100-229`）与"RK-34 消费实证"（升级为确证零消费）。仍欠：
1. `ashare_systemic_risk_detector.py` 正文（266 行起的五信号阈值实现、互斥检测与情绪断路器逻辑——**本块最关键未读件**，L08-C43 施工要据其 provider 字段清单产数）；
2. `docs/03_modules/_domain_risk/systemic_risk_alert_state_machine/blueprint.md` + `.../algo_flow/systemic_risk_alert_state_machine.yaml`；同族另有 `.../ashare_systemic_risk_detector/`（blueprint/index/algo_flow，`capability_canonical_file_registry.yaml:14179,14451,39451`）；
3. **路径幽灵复核**：`module_translation_registry.yaml:26788` 仍存 `src/zephyr/risk/ashare_systemic_risk_detector.py`（旧路径，文件不存在），正确路径=`risk/core/…`；历史同案见 `candidate_module_registry.yaml.bak_pre_one_question:2214-2229`（MOD-RSK-010 幽灵节点，前缀 RSK 非规范 RK，已 rejected）→ 需确认翻译注册表是否仍被 depgraph/前端消费（若消费=错路径会传染）；
4. `battle_map_09_risk_control.md:1214`（S33 供数声明）与 `ulib3b_supply_relationship_ledger.md:68` 对表；
5. 六套状态机互认全景（SKEL §1 末段）中 RK-10/RK-34 与 ex_core 五态降级机的迁移语义（`orchestrator:1039-1095` 只读了门禁段，五态机正文未读）。
禁封矿：市场侧"看不见"不能作为封矿理由；量尺=终局全貌（AI 自制 = 进料口必须由系统自己产出，而非等 Owner 手喂）。

## ⑥ 挖矿日志

- Grep src+scripts `SystemicRiskAlertStateMachine|AshareSystemicRiskDetector|systemic_detector|systemic_input_provider|cn_macro|Swake`（45 命中）→ 一次拿到三件事：①仲裁点接线语义 ②`start_paper_session.py:440/538` 自述 provider 未接线 ③`cn_macro/Swake` 在代码层零命中（原为 14 号文文档结论，本簿独立复证）。
- Read `systemic_risk_alert_state_machine.py:100-229` → 清空骨架正文债（校验/指令/五路不短路/BLACK 单布尔）。
- 跨块顺带取证（零额外调用，来自 RSK-2/RSK-6 结果集）：`orchestrator:1062` 逃生指令在系统性风险分支（归属改判支撑）、`liquidity_crisis_manager.py:34` "阈值一律从 check() 取"（单源正面样板，与 RK-34 自成一套形成对照）、`architecture_health/latest.json:54` 克隆簇、`candidate_module_registry.*.bak:2214-2229` 幽灵节点史。
- 判定链：provider 缺位 → 成对注入不成立 → `_evaluate_systemic_risk` 早退 → 五信号从未扫描 → 三级警报/逃生/降级门禁均不被激励 → 与 RK-34 零消费叠加 ⇒ **本块是全 L08 里"算法最完备、现实最盲区"的一块**（值得在 `_INDEX_MINE.md` 单列）。
- 纪律：只读；未起行情/宏观取数作业；未跑测试；无 git 写；未触碰熔断。
- 外部对表：未做（留统一轮；候选=融资余额/量化拥挤度作为系统性信号的可得性与滞后（A 股融资余额 T+1 公布 → **发布方与年份必须标注**，且过 A 股适配闸）、2015 千股跌停与 2024 微盘踩踏的事后指标研究；SKEL §5 已登记 Cassandra-Risk (Nayani 2026, SSRN) 作前瞻信号候选，采前须回测）。
