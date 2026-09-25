---
ttl: task_bound
title: L08-C01 两套五级互认仲裁序 v1 立法稿（P0 起草班交付，待 Owner 追认）
created: 2026-09-25
sid: st-mining-l08-20260925（L08 风控挖矿班·C01 起草批）
lane: decision_map_campaign
status: DRAFT（立法稿=规则文本+伪代码，禁施工；生效须 Owner 追认=TRD-A13 裁定门位）
doc_version: v1.0-draft
skeleton_source: ./SKEL.md §4 L08-C01 行（账本号=TRD-A13，13号文 §九 :478）
new_gates: 0
new_components: 0
criterion_source: ../../17_quantified_acceptance.md §四 TRD-A12 行（:43）
---

# 两套五级互认仲裁序 v1（立法稿）

> **一句话**：交易五级熔断（执行秒级，DAILY_LOSS=-3% AUM）与 TDM 熔断五级 L0-L4（组合日级，日亏 6% 减仓）同日双触发时——**动作取并集、姿态取最保守、恢复各自走但合成禁止面不放宽**（§2，全标"建议"待 Owner 追认）；仲裁收口在 `ex_core/risk_layer_orchestrator` 熔断单一仲裁点既有聚合位，**零新组件零新机制**（§3）；阈值不映射不归一——两套数字三套口径并存的统一归 L08-C03 内收债，本稿不碰（§1.3）。

**立法边界**：本稿只裁"同日双触发谁说了算"（TRD-A13 范围原文，13号文 :478）；不裁 MOD-RK-049 三选一（L08-C03）、不裁 reset 权限闸（L08-C05）、不裁全史物化表（L08-C06）、不裁白名单二选一（L08-C08）——四事解耦，禁搭车（§2 AR-5）。

---

## §0 立法边界与净零对价

1. **本稿=规则文本+伪代码，禁施工**：伪代码块全部为规则语义表达，非生产代码；任何落码走 `docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md` 15 步闭环另立施工项（宪法 §0 RULE-CAPABILITY-LOOKUP 入口）。
2. **零新组件零新机制**：收口位=`src/zephyr/ex_core/risk_layer_orchestrator.py` 的熔断单一仲裁点（`_engage_kill_switch`，头注 INVARIANTS :8"熔断单一仲裁点(重复触发不重复清算)"、ALGO_FLOW A1 :114）——该件头注自述"只编排不重造"，本稿沿用同一信条；仲裁序=把编排层**已在用**的"最严口径合成"先例（破产底线击穿轮 position_cap 0.0+禁新开仓，"最严口径，每轮按当前 nav 重算故不锁死其他层语义"，orchestrator :74-85）立法化为通用合成规则，不新增任何检查器/状态机/事件通道。
3. **建议档标注纪律**：§2 仲裁原则全部为**新立提案，标"（建议）"**，Owner 追认（TRD-A13 裁定，同 commit 原子登记 ruling_registry，宪法 RULE-RULING）后方生效；凡引用既有代码常量/图面口径的数值一律**冻结在其各自真源**，本稿不新增不修改任何阈值（净零铁律，宪法 §4）。
4. **调整通道**：任何数值或严格序变更走裁定登记，禁在代码/文档散改（对齐 L06 立法稿 §0.4 同款条款）。

## §1 两套体系语义对照表（使命①）

### 1.1 对照总表

| 维度 | 甲侧·交易五级熔断 | 乙侧·TDM 熔断五级 L0-L4 |
|---|---|---|
| 真源模块 | `src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py`（MOD-INF-016，production，SAFETY H） | `src/zephyr/risk/core/drawdown_state_machine.py`（MOD-RK-049，production 头衔但 **:6 自述无现役端到端消费方**） |
| 图面锚点 | 图外执行层（13号文环节⑤主对象，:271-275） | TDM-X-R1-01，`config/trading_decision_map.yaml:3193-3227`（父节点 X-R1 :3156-3188） |
| 触发物 | 调用方注入 evaluator（`evaluate` :152-165）+手动 `trigger()`（:130-136） | 组合日盈亏+组合回撤**双轴**（yaml:3203，"与六段情绪的市场轴正交"原文） |
| 五级定义 | POSITION_LIMIT / DAILY_LOSS / CIRCUIT_BREAKER / SECOND_LEVEL / API_TIMEOUT（:52-57，常量 :71-112） | L0 正常 / L1 日亏≥2% 禁加仓 / L2 日亏≥4% 禁开仓+白名单窄门 / L3 日亏≥6% 梯度减仓 / L4 回撤≥25% 或生死线 清仓+Owner 人工接管（yaml:3203-3205） |
| **争议焦点（TRD-A13）** | DAILY_LOSS：`daily_pnl < -0.03 * aum`（**:80-87**），cooldown 86400s、auto_reenable=False | L3：日亏≥6% 梯度减仓（yaml:3205）；同日与 -3% AUM 无映射无升级关系（13号文 :294-296 缺陷 2 原文："同日双触发时的仲裁序未立法"） |
| 动作 | DAILY_LOSS→CANCEL_ALL+DISABLE_NEW（:84）；POSITION_LIMIT→REDUCE_ONLY（:76）；CIRCUIT_BREAKER→DISCONNECT（:92）；SECOND_LEVEL→FULL_SHUTDOWN（:100）；API_TIMEOUT→AUTO_KILL（:108） | L1 禁加仓 / L2 停新开仓 / L3 梯度减仓（重亏仓→高波动仓→压舱石，X-R1-02 yaml:3237-3240）/ L4 无条件全清仓+冻结开仓通道（X-R1 yaml:3167） |
| 时间尺度 | 执行秒级（13号文 :294"执行秒级"原文） | 组合日级（迟滞解除按交易日计） |
| 状态持久化 | 内存唯一真源+磁盘影子 `data/runtime/trading_kill_switch_state.json`（原子写 tmp→os.replace，`kill_switch_state_store.py`:50,60-90；触发/复位自动落盘 trading_kill_switch.py:119-127） | 设计态 JsonStateStore 外部化，但**根目录未装配无可达落盘位**（drawdown_state_machine.py:6 自述） |
| 恢复 | auto_reenable 参数化（DAILY_LOSS=False=当日不再自动恢复）；`reset()` 手动（:139-145，**代码无权限闸**=纪律靠约定，13号文 :299-300 如实注） | 迟滞解除："当日无新低+修复当日跌幅 50% 才降一级，禁 V 型直接回满"（yaml:3206）；L4 仅 Owner 人工解除（yaml:3219 invalidation，fail-closed） |
| 下游消费（2026-09-25 实测） | `active_switches()`→`ex_core/pre_execution_checker.py` 闸门 1 逐单拒单（:176-206，**通**，13号文 :308）；`rebuild_from_disk`（`kill_switch_state_store.py:93-143`）**零调用方=断**（SKEL RSK-2④） | **无现役端到端消费方**：`daily_gate_snapshot.py:235` 读态恒 `absent`；三件声称消费方均待接线（SKEL RSK-3③④；现役回撤分级实由 DrawdownTracker+DrawdownController 闭环，SKEL RSK-4） |
| 现状关系 | **两套并行零互认**（13号文 :294"各自独立状态机……仓内未见映射/升级关系定义"原文） | 同左 |

### 1.2 判定轴正交声明（入法）

乙侧判定轴=组合日盈亏+组合回撤双轴，**与六段情绪市场轴正交**（yaml:3203 原文）；本仲裁序不消费六段状态、不向情绪轴搭桥——轴间正交自 X-R1-01 图面口径入法为仲裁序的边界约束（详见 §6 P4）。

### 1.3 数字口径三分如实注（本稿不统一）

- TDM 图面叙事：L1≥2%/L2≥4%/L3≥6%（日亏轴）/L4≥25%（回撤轴）（yaml:3203-3205）；
- 状态机代码默认：warn 5%/danger 10%/crisis 15%/kill 25%（回撤轴）+VaR 2/4/6%+CVaR 10%（`drawdown_state_machine.py:146-153`）；
- THD 卡：THD-DRAWDOWN-001/002/003=5%/10%/15%（`config/alert_threshold_registry.yaml:64-102`）。
三套数字并存=既有事实（SKEL RSK-3② 如实注）。**仲裁发生在动作层，不发生在阈值层**（AR-1）——故三口径并存不阻断仲裁序立法；阈值统一=MOD-RK-049 收编/接线/退役裁定的连带产物（L08-C03 内收债，w5_1 同域收敛），本稿禁代裁。

## §2 同日双触发仲裁原则（使命②，本 § 全部为**建议**，待 Owner 追认）

### AR-1 保守者胜（动作并集+姿态最保守）（建议）

1. 同日双触发（两侧各自触发条件在同一交易日内先后或同时成立）时，**生效动作=两侧动作集的并集**；因两套动作全为限制性动作（禁止/减仓/清仓），并集天然不含放宽，无须消解冲突。
2. 若须输出单一合成姿态（position_cap / allow_new_position 类标量），**取各侧要求的最保守值**：`position_cap = min(甲侧上限, 乙侧上限)`；`允许开仓 = 甲侧允许 ∧ 乙侧允许`——与编排层破产底线"最严口径"先例同一合成语义（orchestrator :80-82），零新机制。
3. **阈值不做映射不做归一**：-3% AUM 与日亏 6% 保持各自真源原值；仲裁只发生在动作合成层（§1.3）。
4. 时序无关性：无论甲先乙后或乙先甲后，合成结果唯一（并集与 min 运算满足交换律）——禁"先到先管""后到覆盖"类时序语义。

### AR-2 恢复以先恢复者为准，但不得越过另一套的禁止窗（建议）

1. 任一侧自身恢复条件达成（甲：Owner `reset()` 或 auto_reenable 冷却自然复评；乙：迟滞解除降级），即可解除**本侧**动作——恢复不要求两侧同步，不设联合恢复门（先恢复者先走，减少"熔断粘滞"）。
2. **合成禁止面单向不放宽**：恢复后的合成姿态=max(本侧恢复后禁止级，另一侧现行级别要求的禁止级)——效果语义即"不得越过另一套的禁止窗"；任一侧仍生效的限制在合成面全部保持。
3. 单向铁律：恢复运算只允许收紧、只允许按各侧自身迟滞放宽；**禁跨侧代宽**（甲侧恢复不得替乙侧降级，反之亦然）；禁 V 型回满的乙侧迟滞（yaml:3206）与甲侧 DAILY_LOSS 当日不再自动恢复（trading_kill_switch.py:86 cooldown 86400+auto_reenable=False）各自原样保留，本稿零改动。
4. L4/KILL 例外：乙侧 L4 仅 Owner 人工解除可回（yaml:3219 fail-closed；`drawdown_state_machine.py:9` INVARIANTS"KILL仅人工复位可出"；orchestrator INVARIANTS"KILL态人工复位"）——该侧无自动恢复路径，AR-2.1 的"先恢复者先走"不含此级。
5. 方法论锚：恢复侧"带内保持现状、两门槛故意不对称"=`docs/_working/quant_methodology/04_switch_friction.md` §1 滞回带同构语义（乙侧"修复 50% 才降一级"即下行低门槛+确认带；本稿不新增带宽参数，零件已在两套体系各自迟滞内）。

### AR-3 单调与幂等（既有不变式重申，零新语义）

1. "重复触发不重复清算"（orchestrator INVARIANTS :8）对双触发同样成立：同日第二次触发不产生第二次清算。
2. 合成姿态随行情恶化单调收紧、随恢复单调放宽，无振荡位（各侧迟滞保证）；仲裁点每轮重算合成态，不引入额外锁存。

### AR-4 双触发留痕（记账条款）

仲裁点每次输出合成决定须附两侧当时态快照（甲：active 级别清单；乙：现行级别+判定轴读数）；留痕落库通道=熔断级别流转全史物化表（L08-C06，P1，事件触发落盘禁 cron——宪法 §9 红线 3），本稿只定义**必须记什么**，不建通道。

### AR-5 范围铁律（防搭车）

本仲裁序不裁：MOD-RK-049 三选一（L08-C03）、reset 权限闸代码化（L08-C05）、全史物化表（L08-C06）、白名单二选一（L08-C08）、P-P1-04 接线（L08-C09）——各归其施工项；本稿被 Owner 追认不免除任何一项。

### AR-6 伪代码（规则语义表达，非生产代码；落码走 15 步闭环另立施工项）

```
# ═══ L08-C01 仲裁序伪代码 v1（2026-09-25 起草班稿；AR-1~AR-4 语义，全部"建议"待 Owner 追认）═══

function 双触发仲裁(时点 d):                       # 收口位=risk_layer_orchestrator 既有评估轮内（§3）
    甲_生效级 = trading_kill_switch.active_switches()      # 内存唯一真源；重启后=rebuild 重臂态（P3 前置）
    乙_现行级 = TDM_熔断级别评估(d)                         # 图面口径锚 yaml:3193-3227；现役载体随 L08-C03 裁定

    动作集   = 甲_生效级.动作 ∪ 乙_现行级.动作              # AR-1.1 保守者胜=并集
    姿态.cap  = min(甲.位置上限, 乙.位置上限)               # AR-1.2 标量取最保守
    姿态.允新 = 甲.允许开仓 and 乙.允许开仓

    if 动作集.含清算级 and 未清算过(当日):                  # AR-3.1 重复触发不重复清算
        _engage_kill_switch(动作集)                         # 唯一发单点（orchestrator INVARIANTS）

    仲裁留痕(甲_生效级.快照, 乙_现行级.快照, 动作集, 姿态)   # AR-4（落库通道=L08-C06，本稿不建）

function 侧恢复请求(侧 s):                          # AR-2 先恢复者先走，合成面不放宽
    if not s.自身恢复条件达成: return 拒绝                  # 甲=Owner reset/冷却自然复评；乙=迟滞降级（禁 V 型）
    if s.级别 ∈ {L4, KILL}: return 转_Owner人工解除通道     # AR-2.4 无自动恢复路径
    s.解除本侧动作()
    合成面 = max(其余侧.现行禁止级, s.恢复后禁止级)          # 单向不放宽；禁跨侧代宽
    return 合成面
```

## §3 接线点：熔断单一仲裁点收口（使命③，零新机制声明）

1. **单一仲裁点**=`src/zephyr/ex_core/risk_layer_orchestrator.py` `_engage_kill_switch`（头注 :8"熔断单一仲裁点(重复触发不重复清算)"；ALGO_FLOW A1 :114——EMERGENCY/尾部极值/BS-007/系统性 LEVEL_3/五态 UNWINDING/破产底线击穿六源已在同一仲裁点合流）。本仲裁序的甲乙两源=该仲裁点的**第 7、8 个既有语义源**的立法化确认，不是新分支：甲侧经闸门 1 探针（`pre_execution_checker.py:176-206`）逐单拒单链路已在产（13号文 :308"熔断→逐单拒单：通"）；乙侧语义经 `evaluate_intraday` 既有评估轮合成（同轮已内嵌系统性/五态/破产底线判定，F2-F4 :110-112）。
2. **零新机制声明**：不新增组件/状态机/事件通道/gate；合成运算（并集+min+AND）落在编排层既有"最严口径"先例的同一语义族（orchestrator :74-85）；new_gates=0、new_components=0（头注声明）。
3. **职责边界**（P1-2 澄清，trading_kill_switch.py:23-34 头注原文）：本仲裁序只涉交易资金安全侧两套五级；`zephyr.security.access_control/kill_switch.py`（MOD-INF-018，AI Agent 行为熔断、纯进程内存态）**不在本仲裁序范围**，禁误用作交易熔断（SKEL RSK-1⑥ 同款澄清）。
4. **接线次序约束**：乙侧现役载体未定（L08-C03 三选一）期间，落码施工**不得启动**——裁定先行，施工随裁定（SKEL §4 L08-C03"裁定先行，施工随裁定"原文）；本稿生效（Owner 追认）只立法语义，不等于接线完成。

## §4 演练验收（使命④，锚=17号文）

1. **冻结档引用**：TRD-A12 行（`docs/_working/decision_map_campaign/17_quantified_acceptance.md`:43）——"rebuild_from_disk 演练（kill-9→重启→状态逐字段一致）通过+首次 HALT 全流程演练+HALT→恢复人工步骤 ≤5"。本仲裁序的演练在其 HALT 全流程演练之上叠加，不另立重复判据（净零，引用不重复立项——对齐 SKEL L08-C10 手法）。
2. **建议档新增判据**（Owner 可调，随追认同批确认）：
   - **V-1 双触发注入**：sim 环境人为同时满足 DAILY_LOSS（-3% AUM）与乙侧 L3（日亏≥6%）注入用例 → 断言生效动作=两侧并集（CANCEL_ALL+DISABLE_NEW ∧ 梯度减仓指令），且仲裁点清算恰一次（AR-3.1 回归，`tests/ex_core/test_risk_layer_orchestrator.py` 既有测试位扩展）。
   - **V-2 恢复越窗反演**：先人工 reset 甲侧 → 断言乙侧现行禁止级在合成面原样保持（AR-2.2）；反向同测。
   - **V-3 台账计数**：演练记入 `live_admission_checklist` R7 计数（与 L08-C02 首演共享台账，0→1 口径同 SKEL §4 该行）。
3. **演练环境红线**：kill switch 治理档位豁免——"任何 ai_autonomy 档位下均为真实执行，不随 paper 模拟"（yaml:3185-3186 原文）⇒ 演练必须在 sim 环境以隔离券商 feed 执行，**禁止在生产资金面彩排**；演练触发/复位后状态影子逐字段还原（TRD-A12"状态逐字段一致"判据复用）。
4. **验收凡例**：按 17号文头注凡例两档执行——TRD-A12 行=冻结档引用禁改；V-1/V-2/V-3=建议档，验收时打钩+附实测数，未达=未完工。

## §5 生效与落地路径

1. Owner 追认 §2 仲裁原则（AR-1~AR-4）→ 裁定登记 ruling_registry（RULE-RULING，同 commit 原子；TRD-A13 销账）；
2. 追认同批确认建议档判据（V-1/V-2/V-3）与 §6 前置处置；
3. 落码施工项另立（走 15 步闭环），施工前置=§6 P2/P3 就绪；本稿批准≠施工令。

## §6 前置依赖与生效条件（如实标注，逐项可核；现状=2026-09-25 实测）

| # | 前置 | 现状 | 缺位后果 |
|---|---|---|---|
| P1 | Owner 追认（TRD-A13 裁定门位，13号文 §九 :478"裁定｜Owner"） | 未裁（本稿=DRAFT） | 全文不生效，两套并行现状零变更（如实保留=13号文 :296"禁臆断"纪律） |
| P2 | L08-C03 MOD-RK-049 三选一裁定（接线/收编/退役） | 未裁（SKEL §4）；乙侧无现役端到端消费方（drawdown_state_machine.py:6 自述） | 仲裁序乙侧现役载体悬空——语义已立法、接线不可施工 |
| P3 | L08-C02/TRD-A12 rebuild_from_disk 会话启动接线 | 零调用方=断（kill_switch_state_store.py:93-143 在码无人调） | 甲侧重启即失忆窗口实存（13号文 :293），仲裁输入甲侧态在重启后不可信；演练 V-1 前置 |
| P4 | **六段同族前置（正交性声明，非依赖）** | 六段真源链分叉 601 vs 1,051 日待修复（`docs/_working/quant_methodology/appendix_C_six_state_truth_chain.md` §2/§4，07号文已批开工） | 本仲裁序**不消费六段轴**（yaml:3203 正交原文），该修复不构成本稿前置；但禁借仲裁序向情绪轴搭桥（§1.2 入法）——若未来修法引入情绪轴输入，须先清 appendix_C 分叉 |
| P5 | **pf_alloc 同族前置（休眠声明）** | TDM L2 白名单窄门=R1-03 `defensive_asset_whitelist.py`（design 态）；UP-5 对冲建议=`src/zephyr/pf_alloc/core/tail_hedge_signal.py`（MOD-PA-024，D107 回测验证前休眠 fallback，yaml:3170-3173；09号文 :602） | 恢复语义涉"白名单窄门"处，L08-C08 二选一裁定前一律按**窄门不开**保守侧解释；UP-5 信号非指令（yaml:3171-3173），不参与仲裁，D107 休眠不阻断本稿 |
| P6 | 入 HEAD 走 GitCommitGateway 正门 | 本稿随批落 HEAD（campaign README 纪律：safe_write CAS+整包随批落 HEAD） | CREATE-GUARD creation_token 随批登记（新建 .md）；禁裸 commit（宪法 §2） |

---

**立法稿完**。自检：五使命项全覆盖（§1=①对照表，§2=②仲裁原则全标"建议"，§3=③收口位+零新机制声明，§4=④演练验收引 17号文 TRD-A12 行，§2 AR-6=⑤伪代码）；伪代码 1 块纯语义表达，生产代码 0 行；前置 6 项逐项如实（六段=正交声明非依赖、pf_alloc=休眠声明保守侧解释）；阈值零新增零修改（净零）；全部引用带仓库路径。
