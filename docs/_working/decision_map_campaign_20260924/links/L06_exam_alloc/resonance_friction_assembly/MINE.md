---
ttl: task_bound
title: L06-子模块 条件共振判定·切换摩擦·组合装配（r 态→六段折算 / 滞回 mSPRT / E8 装配）挖干
created: 2026-09-25
sid: st-qmine-20260925
lane: L06_exam_alloc
status: SEALED-CORE（六向内部反查全填、③向外部双源；E8 装配=预注册留白非遗漏）
skeleton_source: ../SKEL.md L06-F/G/H；../../09_link_skeletons.md 环节6
doc_role: L06 挖矿子模块 MINE（覆盖 SKEL L06-F 共振判定 + L06-G 切换摩擦 + L06-H 组合装配）
---

# 子模块 · 条件共振判定 / 切换摩擦治理 / 组合装配（resonance_friction_assembly）

> "条件共振"=当日 r 态折成六段、与成绩单条件格对上→对路策略上岗；本块含三件事：
> 判定（r→六段唯一位点与分叉）、摩擦（滞回带/mSPRT/任职期提案）、装配（E8 权重矩阵留白）。

## ① 职责一句话
把 regime r 态经唯一映射折成六段情绪相位、判定哪些策略成员"今日激活"，用滞回带+mSPRT 管住切换摩擦，
并把激活成员与 PP-001 sleeve 配比装配成组合权重面板。

## ② 现状实测（代码 file:line）

### 共振判定：唯一位点 + 分叉两处
- **法定唯一位点** `framework_composer.py:153-159` `REGIME_STATE_TO_ACTIVATION_PHASE` =
  `{r10:capitulation, r4:accumulation, r11:accumulation, r3:expansion, r12:ignition}`；
  注释 :147-152 铁证：r1 低波/r2 中波无六段对应（不路由）、**六段 euphoria/distribution 无 r 态来源 ⇒
  只挂这两态的成员在整装口径下恒不激活**（结构性如实披露，= 任务令点名"无 r 态来源"，本块不重裁、实测坐实）。
- **镜像第二处** `scripts/backtest/auto_mount.py:129 R2SIX` 与位点**逐键一致**（本块实测比对：五键全等）；
  auto_mount 另有家族→六段 :120-121（value_reversal→{capitulation,accumulation,euphoria,distribution}、
  momentum_trend→{expansion,ignition}）+ 宏观优先 `PHASE_PREEMPT={r10,r11}` :99 + 两轴合成 :249。
  头注 :148-150 自述"两处必须同步，已登记主会话收编为共享真源（候选落点 zephyr.shared.contracts 或 config 规则 YAML）未落"。
- **分叉第三处（产线）** `daily_decision_orchestrator.py:112` 注释坐实"原 `REGIME_TO_SEGMENT`，
  r4→distribution / r1→accumulation / r2→ignition 三键与法定真源冲突"——原三键映射已废为注释、现行件走 BUDGET_BANDS。
  ⚠ 需复核：该产线现网是否仍有活跃六段折算读端（本块 R2 pending）。
- strict/lenient 政策 `framework_composer.py:163-165`：strict=当日态不在成员激活集⇒α 强制 0（宁漏勿误，默认）；
  lenient=回退基准权重（:161-162,855,874）。

### 切换摩擦：三零件在产 + 三提案未立法
- 过渡带 `daily_decision_orchestrator.py:99 TRANSITION_THRESHOLD=0.60` / `:100 TRANSITION_FACTOR=0.5`（隶属度<60% 按保守下缘 0.5 折减，:423-425,587）。
- mSPRT 序贯晋升 `src/zephyr/pf_core/core/msprt_champion_challenger.py`（MOD-PF-008，stability=evolving）：
  delta=challenger_pnl − champion_pnl（:189）；**但 :110-115 明示配对 ExecutionReport 契约未建、契约建成前 delta 为占位** ⇒ 晋升输入虚挂（本块核心漏洞）。
- 退役滞回 `src/zephyr/governance/lifecycle_governance/strategy_retirement_evaluator.py:8` 评审制铁律
  "触发只生成评估报告+人工裁定、永不自动改状态"；阈值 THD-RETIRE-001/002/003+THD-DEVIATION-002 真源=alert_threshold_registry，偏离度量真源=MOD-RK-23（只消费不重算）。
- 提案（未立法，04_switch_friction 册）：最短任职期 ≥20 交易日（期内只记档不执行）+ 下岗冷却 ≥60 日 + 切换三行账——**Owner 采纳门位**，禁新机制。

### 组合装配
- 合成算子 `framework_composer.py:1002` 静态（等权 α=1/15）/ `:1244` 动态（regime 联动）；
  IBT-A 静态整装 15 员 + IBT-B 四层联动=组合仅 2 配置（协议 §7）。
- **E8 装配层未建 = 预注册决策非遗漏**："7 态×15 员 regime 权重矩阵 v1 明确不做（避免自造权重矩阵；留 E8 装配层）"（IBT-PROTOCOL-V1.md §7:96，SKEL L06-H ③）=IBT-C01（P2）。
- 生产侧：pf_alloc 链（allocation_orchestrator/batched_position_builder）日循环 16:45 已跑通；回测侧全手工（SKEL L06-H ⑤）。

### 生产触发面
- 共振折算：**回测侧在用（framework_composer/auto_mount 有码）、生产侧虚挂**（编排器本体不存在，SKEL L06-F ⑤）。
- 摩擦零件：过渡带/mSPRT/退役评审均 production·evolving 在码；**"任职期记档不执行"评审输入挂点未建**（04 册 §2）。

## ③ 六向台账（内部 + 全网双动作）

| 向 | 内部反查发现 | 全网外部反查 |
|---|---|---|
| ①上游 | RegimeSnapshot 7 态（c1_backtest.regime_snapshot_history 3,629 日 PIT，SKEL L06-F ①）；六段词表 `signal_ashare/core/environment_switch.py SIX_STATES`（_states_from_source 惰性加载+fail-closed，framework_composer:186-208）；情绪灰度 condition_package 消费 emotion_index v0.1.0 | 机构对照=regime detection（HMM）+ asset-specific regime switching（见 ③）；r 态来源缺失（euphoria/distribution）业界多由微观结构/情绪轴补，本仓 auto_mount 已有 overlay 腿但整装位点未接（如实注） |
| ②下游 | compose_weight_panels（静态/动态）；IBT-B 四层联动 L1 shrinkage；daily_decision_orchestrator 六段预算带；DEAD_MEMBER_ALPHA_SHARE_LIMIT=0.25 组合完整性闸（framework_composer:178-180，SKEL L06-H ④） | 待外部（滞回/任职期业界实践见 ③） |
| ③算法/机制 | 唯一位点双处同步纪律（:148-150）；strict 宁漏勿误政策；mSPRT=统计版滞回（证据累积到阈值才切换）；RSC-2 收缩"剩余质量落现金禁再归一化"（裁定#270） | **≥2 源**：① arXiv 2406.09578 "Dynamic Asset Allocation with Asset-Specific Regime Switching"（arxiv.org/html/2406.09578v2，2024）——逐资产 regime 状态路由配置=共振判定→装配同构；② 滞回/最短任职期业界主张见 SKEL §9（LuxAlgo 2026-08 / ArrowAlgo 2026-05 / DeepTradeX 2026-07 三处"触发器+评审"，本块沿用不重引）。**A 股适配闸**：mSPRT/滞回无涉做空，A 股适配通过；六段含 euphoria/distribution 防御语义在 A 股 T+1 下靠"预算带 0% 禁新开仓"实现（distribution），非裸对冲 |
| ④后端 | 分叉修复 6 步=quant_methodology/appendix_C_six_state_truth_chain.md，**Owner 已批开工**（SKEL L06-F ⑥/07 号文 C2#3）；E8+矩阵=批 G 未建（IBT-C01/C02）；mSPRT ExecutionReport 配对契约未建（msprt:110-115） | 开源对表（SKEL §9）：mabwiser contextual bandit（Apache-2.0，上岗 v2 用，前置 L06-C01）；Riskfolio-Lib（BSD-3，E8 装配算法参考，替代自造权重矩阵）；hmmlearn/statsmodels regime（BSD-3，零引入，仓内 regime_detector 自研已够） |
| ⑤前端 | 组合权重面板无独立上岗矩阵 UI；framework_composer 输出经 IBT 报告非看板（登记边界，呈现随 L06-C09 上板桥） | 已查无：无"激活矩阵格子"前端；不越界 |
| ⑥数据字段 | regime_snapshot 7 态字段 vs 六段 6 词**基数不等**（7→6 多对一，r1/r2 无对应）；`PlanWeight.activation` 六段子集字段（framework_composer:243-258）；"字段在≠可得"：euphoria/distribution 段有词表位、无 r 态喂入 ⇒ 字段在但数据源缺（结构性空洞，坐实） | 待外部反查（六段↔五态↔七态三套词表业界无标准，记"已查无标准定义+查法=对比 regime taxonomy 文献"） |

## ④ 缺口清单（沿用 + 续编）

| 编号 | 缺口 | 册内可见性 | 状态/解锁 |
|---|---|---|---|
| LK-16 | 六段↔五态↔七态三套词表映射无统一定义 | SKEL L06-E/F | 挂起→施工（映射常量入 plan_engine，Owner 批后） |
| **L06-C14（新，册内未见）** | **mSPRT 晋升输入虚挂**：champion/challenger 配对 ExecutionReport 契约未建，delta=占位（msprt:110-115） ⇒ 序贯晋升无真实成交流 | 本块新立 | 施工；解锁=成交回报契约（属执行链 L07，本块登记边界不越界建） |
| **L06-C15（新，册内未见）** | **euphoria/distribution 覆盖空洞互为前置**：D30 填格需防御 sleeve 且需 r 态来源，framework_composer:151-152 证无 ⇒ 填格与"是否新设防御档/是否补微观相位源"须同批裁 | 本块新立（呼应任务令"结构性问题已登记"） | 挂起；解锁=Owner 裁防御档 + 微观相位源接入位点 |
| L06-C01 | 上岗规则 v1 立法（滞回带 0.60×0.5 + 任职期 20 日 + 冷却 60 日提案→立法） | SKEL §8 C01 | 挂起；解锁=Owner 采纳 + 六段分叉 6 步修复完成 |
| IBT-C01/C02 | E8 装配层 + 7 态×15 员矩阵 + Σ<1 直通 | SKEL L06-H | 挂起排期；解锁=批 D 新名单 + 成绩单驱动（禁自造=协议 §7 预注册原话） |

## ⑤ 自审闸三态裁定（mining_sop §6）

- **终局定位**：共振判定是"当日天气→上岗"的机器咽喉，终局必自动化 ⇒ **不封矿**。
- 三态分布：
  - **施工**：LK-16 映射常量、六段分叉 6 步修复（**Owner 已批开工**，appendix_C）——纯代码。
  - **挂起排期（解锁明确）**：L06-C01（Owner 采纳门位 + 修复完成）；D30/防御档（Owner 资金门位 + 微观相位源）；IBT-C01/C02（批 D 新名单 + 成绩单驱动，**预注册留白非未挖**）。
  - **边界登记不越界施工**：L06-C14 mSPRT 成交流契约属执行链 L07；本块只登记"该面虚挂、解锁在他链"。
- **矿脉判读**：唯一位点+分叉两处+strict/lenient+无 r 态披露+mSPRT 占位+装配留白全部 file:line 坐实；外部双源锚定 regime-switching 机构原型。残余长尾=六段分叉修复完成后的 config/plan_engine 落地（施工，非挖掘）。

## ⑥ 挖矿日志（mining_sop §7）

| 轮 | 矿脉 | 动作 | 判定 | 归因 |
|---|---|---|---|---|
| R1 | 共振折算位点 + 分叉 + 摩擦零件 + 装配留白 | 读 framework_composer:145-162 + grep auto_mount R2SIX/orchestrator 常量/msprt/retirement（逐键比对） | **signal**（五键全等实证、euphoria/distribution 无 r 态坐实、mSPRT delta 占位新洞、E8 预注册留白定性） | — |
| R2 | ③算法向外 + 产线读端复核 | WebSearch regime-switching/meta-labeling + 待 grep orchestrator 是否仍有活跃六段读端 | **signal（外）/pending（内复核）** | 内部复核列 pending，非查无 |
| R3 | 开源件对表 | 沿用 SKEL §9（mabwiser/Riskfolio/hmmlearn 许可证经检索确认） | **signal（复用已检索件，未重复烧搜索）** | 归因=标准件已在册检索过，本块登记对表不重挖 |

> 本块无 noise 轮。邻块边界：上岗规则 config 落地/填格 → `../onboarding_rules_matrix/MINE.md`；考试结果落库 → `../exam_result_writeback/MINE.md`。
