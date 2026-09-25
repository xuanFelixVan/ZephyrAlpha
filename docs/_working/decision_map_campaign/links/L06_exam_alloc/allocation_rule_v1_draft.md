---
ttl: task_bound
title: L06-C01 条件共振上岗规则 v1 立法稿（P0 起草班交付，待 Owner 采纳）
created: 2026-09-25
sid: st-mining-20260924（L06 挖矿班·C01 起草批）
lane: decision_map_campaign
status: DRAFT（立法稿=规则文本+伪代码，禁施工；生效须 Owner 裁定采纳+D31 confirmed 同批）
doc_version: v1.0-draft
skeleton_source: ./SKEL.md §8 L06-C01（编号新立；既有账本号 LK-10 随附）
merges: ../../../daily_loop_campaign/routing_table_v1_draft.md §3 + ../../../quant_methodology/04_switch_friction.md §1-§3（净零对价=合批呈批为单一立法件，两稿降级为引用，禁另立第二切换册）
new_gates: 0
criterion_source: ../../17_quantified_acceptance.md（下称"17号文"；判据编号约定见 §6）
---

# 条件共振上岗规则 v1（立法稿）

> **一句话**：谁上岗不由单日好坏说了算——**状态轴相位、成绩单资格、统计门、判据守卫四条件同时共振**才许上岗（§2）；上岗有最短任期、下岗有确认窗与冷却期、每次切换先交三行成本账（§3-§4）；本规则只裁"**谁在岗**"（治理层），日频"**激活多少**"（机械层 α）仍归 framework_composer/编排器现行口径，两层不得互相越权（§5.4）。

**判据编号约定**：本文全部判据条目编 `[J-xx]`，逐条挂 17号文锚（§6 索引总表）；按 17号文凡例分两档——**冻结判据**（frozen 真源已有，禁改）与**建议判据**（标"（建议）"，Owner 可调）。正文行内引用格式=（17号文 §X·行Y）。

---

## §0 立法边界与净零对价

1. 本稿=规则文本+伪代码，**禁施工**：伪代码块全部为规则语义表达，非生产代码；任何落码走 construction_workflow_policy 15 步闭环另立施工项。
2. **单一立法件**：本稿合并 `docs/_working/daily_loop_campaign/routing_table_v1_draft.md` §3（落地三步）+ `docs/_working/quant_methodology/04_switch_friction.md` §1-§3（滞回带/最短任职期/成本预算提案）为唯一切换治理立法件；呈批后两稿降级为引用源，禁另立第二切换册（SKEL §8 L06-C01 净零对价原文）。
3. **新 gate=0，新机制=0**：全部零件复用现行代码常量位与在产模块（零件清单见 §3.0），本稿只做"参数入册冻结+判定序立法"，不新增任何检查器。
4. **调整通道**：任何数值（含 0.60×0.5/20 日/60 日）变更走裁定登记（RULE-RULING，同 commit 原子），禁在代码/文档散改。

## §1 输入定义（三路输入）

### 1.1 I1 · GPU 成绩单列（候选资格的唯一数据面）

| 列/项 | 真源 | 用途 |
|---|---|---|
| `cost_adjusted_sharpe`（主目标） | 成绩单=每格 cost_adjusted_sharpe 主目标+毛夏普仅观察，`docs/_working/decision_map_campaign/03_gpu_campaign.md`:27 | 上岗排序主键（§2.3 T1） |
| 毛夏普观察列 | 同上 | 只观察不判定，禁作上岗依据 |
| `cost_tier_sharpes_json`（五档 [0,5,10,20,40]bp） | `config/exam_scale_cost_gate.yaml`:11；manifest 出生证列（`scripts/backtest/factory_grid_executor.py` manifest 段） | 三行账第②行"五档存活证明"原料（§3.5） |
| DSR 浮动门槛 | `config/search_space_prereg.yaml` e7_defense.dsr_floating + `src/zephyr/backtest/core/n_trial_ledger.py`（MOD-BT-200）cumulative_trials 口径（裁定#306） | 统计门半边（J-04） |

- **解读纪律（J-09，冻结档）**：成绩=**考尺口径的相对排名**；跨引擎绝对值翻译待 IBT-D01 对照表，同名格 sharpe 差>30% 列差异清单（17号文 §一·解读纪律行）；IBT-D01 对照表**先于解读存在**（L06-C03，`./SKEL.md` §8）。
- **成绩单批准入（J-01/02/03/06/07）**：用于上岗判定的成绩单批必须先过 17号文 §一 全行检查——完成率 3,700±0、成本门真实性抽查、N_eff≥12、负结果纪律；**命中垃圾触发线任一条（完成率<95%/死亡率>1%/sharpe>2 格占比>5%/条件轴零样本/prereg hash 变动）⇒ 该批成绩单整批禁用于上岗判定**，报 Owner（17号文 §一·垃圾触发线行）。

### 1.2 I2 · 状态轴相位（条件共振的"条件"本体）

- **真源链（唯一，禁第二份）**：RegimeSnapshot 7 态（`c1_backtest.regime_snapshot_history` PIT）→ r 态→六段唯一映射位点 `src/zephyr/pf_core/strategy_engine/framework_composer.py`:153 `REGIME_STATE_TO_ACTIVATION_PHASE`（{r10→capitulation, r4→accumulation, r11→accumulation, r3→expansion, r12→ignition}）；六段词表=`src/zephyr/signal_ashare/core/environment_switch.py` SIX_STATES；挂图侧镜像 `scripts/backtest/auto_mount.py`:129 R2SIX（两处同表+漂移守卫）。
- **r1/r2 震荡态不路由=宁漏勿误**（composer 同表口径）；**euphoria/distribution 无 r 态来源**⇒只挂这两段的成员在整装口径下恒不激活（`framework_composer.py`:147-150 头注如实披露，本稿照抄该披露为法定事实）。
- **守卫前置（J-10 前置件）**：判据真源守卫绿才许驱动切换——反面教材=`docs/_working/t0_matrix/FINAL_REPORT_t0_matrix_reexam.md` §五-6（宏观门误把低波当趋势）；修复清单=`docs/_working/quant_methodology/appendix_C_six_state_truth_chain.md` §4 六步（07号文 :72 已批开工；产线切源+守卫测试 `tests/strategy_pipeline/test_decision_orchestrator.py` TestSixStateTruthChainSwitch 已在码，`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py`:527 `_regime_to_segment` 消费法定真源 fail-closed；**收编共享真源/历史结论重算/锚定表语义裁定三步以生效日实测落账为准**，见 §7 P1）。
- **置信度（隶属度）来源**：TDM-E-L1-AGG 因子滚动分位→加权合成→状态分布（主状态+灰度），社区阈值=隶属度 0.5 锚点非硬边界（`config/trading_decision_map.yaml` state_matrix 段头注，:5556 起）；**同一映射禁产线第二份**（appendix_C §2 分叉 75% 教训入法）。

### 1.3 I3 · 置信度来源（统计门的证据面）

1. **mSPRT 序贯证据 M 值**：`src/zephyr/pf_core/core/msprt_champion_challenger.py`（MOD-PF-008）——threshold=1/α（α=0.05→20）、lower_boundary=α（:145-146），M≥1/α 才拒 H0（:261）；tau 标定=历史 OOS 效应量 std，冷启动 0.2（:163-174，**calibrate_tau 细节对表=C01 收尾深读尾差③**，SKEL §7）。
2. **晋升编排**：`src/zephyr/governance/lifecycle_governance/msprt_promotion_channel.py` PromotionChannelManager（ARCH-298 载体重裁定=MOD-L02-013）——证据持续累积到阈值才切换，单日好运翻不了盘（`docs/_working/quant_methodology/04_switch_friction.md` §1 证据件 3）。
3. **状态隶属度**：I2 的灰度分布值，仅供滞回带折减（§3.1），**不得**充当统计证据——隶属度是状态置信，不是策略优劣证据，两源禁混（本稿新立语义条款，零新机制）。

## §2 上岗判定（条件共振的机械定义）

### 2.1 条件共振定义（多条件同时满足的合取，缺一即不共振）

**条件共振**=同一评审时点，以下四条件**全部为真**：

| # | 条件 | 机械判据 | 判据锚 |
|---|---|---|---|
| R1 | 状态轴共振 | 当日折算六段相位 s 存在（REGIME_STATE_TO_ACTIVATION_PHASE 命中；r1/r2/快照缺席=None=不共振，fail-closed 宁漏勿误） | §1.2 |
| R2 | 槽位共振 | `config/trading_decision_map.yaml` state_matrix 在 s 段格子**已填格**（pending-owner-adoption 格=残缺不路由，R41 封闭词表）∧ 该段存在上岗缺位（空缺，或在岗者已走完 §4 下岗流程） | yaml:5556-5650 |
| R3 | 证据共振 | 候选者 DSR 校正后 Sharpe≥浮动门槛（J-04）∧ mSPRT M≥1/α 显著（J-05）——两门同时过，单门不算 | §1.3 |
| R4 | 守卫共振 | 六段映射三方同源+守卫测试绿（J-10）∧ 成绩单批未命中垃圾触发线（J-07） | §1.2/§6 |

**不上岗默认态=保持现状**（在岗者留任、空缺继续空缺）——共振是上岗的**必要充分**条件，非共振日不做任何轮换动作。

### 2.2 候选资格前置滤（全部满足才进入 R3 判定）

按序过滤：①成绩单批准入（J-01/02/03/06，§1.1）→②E4 正考 verdict=通过+三道成本门全档证据（`src/zephyr/backtest/regime_validation/exam_cost_gate.py`，<3 档 fail-closed）→③考试政策准入四条（`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md` §1：prereg 冻结/封闭族 N_eff/沙箱三关/负结果台账）→④冷却期已满（§3.3，冷却中禁参选）→⑤多重检验三件套逐格报告在册（J-08；PBO/CPCV 字段接线=LK-08 未落地前，该条以"haircut+DSR 两件在册+PBO 缺位如实标注"过渡，禁静默豁免）。做T 包候选附加 J-13（WFE≥50%∧Wilson LB 衰减≤30%，17号文 §三.2）。

### 2.3 优先级并列决胜规则（机械字典序，禁人工点名）

同段多候选同时满足 R1-R4 时，逐级比较、先分胜负即停：

```
T1  cost_adjusted_sharpe 高者胜            （考尺口径，J-09）
T2  DSR 超出门槛余量大者胜                  （J-04）
T3  mSPRT M 值大者胜                        （证据积累更快的序贯路径，J-05）
T4  三键仍全等 ⇒ 全部不上岗，保持现状，记档报月度复盘
    （宁缺勿滥；禁抽签、禁人工点名、禁"分时段轮换"变体——机械定义）
```

### 2.4 上岗判定伪代码（规则语义表达，非生产代码）

```
function 条件共振上岗判定(评审时点 d):
    s = 折算六段(d)                              # 唯一位点 composer:153；r1/r2/缺席→None
    if s is None:            return 保持现状      # R1 不共振（宁漏勿误）
    if not 守卫绿(d):        return 记档("守卫红") # R4 不共振（J-10/J-07）
    槽位 = state_matrix[s]                        # 只读 TDM（禁复制第二份）
    if 槽位.未填格 or not 槽位.有缺位: return 保持现状   # R2 不共振
    候选 = 成绩单幸存者.filter(资格前置滤, §2.2)     # 含冷却期滤
    达标 = [x for x in 候选 if x.DSR通过 and x.mSPRT.M >= 1/α]   # R3
    if 达标.empty:           return 保持现状
    return 决胜(达标, §2.3)                        # 胜者上任，任期起算=d
```

## §3 切换摩擦治理（四零件+三行账，全现成参数）

### 3.0 零件清单（在产模块位，零新件）

| 零件 | 真源位 | 状态 |
|---|---|---|
| 过渡带折减（滞回带） | `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py`:98 TRANSITION_THRESHOLD=0.60 / :99 TRANSITION_FACTOR=0.5（裁定#305 草案值；SKEL 引 :95-96 为改前快照，现行行号以本表为准） | 在产 |
| 六段预算带+硬顶 | 同文件 :102 BUDGET_BANDS / :97 HARD_CAP=0.60 / :410-420 带内插值×过渡折减×硬顶合成 | 在产 |
| mSPRT 序贯晋升 | `src/zephyr/pf_core/core/msprt_champion_challenger.py` + `src/zephyr/governance/lifecycle_governance/msprt_promotion_channel.py` | 在产 |
| 退役评估（下岗侧） | `src/zephyr/governance/lifecycle_governance/strategy_retirement_evaluator.py`（阈值唯一真源=alert_threshold_registry，fail-closed） | 在产 |

### 3.1 滞回带（置信不够不移交；现行值入册冻结）

1. **数值冻结**：过渡带阈值 0.60×折减系数 0.5（daily_decision_orchestrator.py:98-99 现行值入册）——最大隶属度<60% 进过渡带，仓位上限按保守下缘 0.5 折减（裁定#305；17号文凡例冻结档：frozen 真源已有，禁改，调整走裁定通道）。
2. **不对称语义入法**：上任走统计门+mSPRT 序贯确认（高门槛、多日证据），下岗走 LB 确认窗+评审（§4）——两门槛故意不对称，带内保持现状。
3. **带宽底线（建议）**：滞回带宽≥2×切换成本期望损耗折算，带宽值随各策略成本档预注册（`docs/_working/quant_methodology/04_switch_friction.md` §1 立法建议行）。
4. **预算带连续插值**：六段预算带（capitulation 0-10%/accumulation 20-30%/ignition 30-50%/expansion 50-70%/euphoria ≤30% 只卖不买/distribution 0% 空仓）为连续区间非开关跳变（TDM-F-C1，daily_decision_orchestrator.py:102），天然抑制"全有全无"切换。

### 3.2 mSPRT 晋升（统计版滞回，已立法照用）

上任的统计半边=挑战者 DSR 校正后 Sharpe+mSPRT 达显著（现行晋升通道 PromotionChannelManager，ARCH-298），本稿零改动照用（04册 §1"已立法，照用"原文）；单日成绩单利好**不构成**上岗触发（证据须持续累积到 M≥1/α）。

### 3.3 最短任职期与冷却期（建议值，Owner 采纳后随 D31 confirmed）

1. **最短任职期 ≥20 交易日（建议）**：上任后 20 个交易日内，业绩型触发器**只记档不执行**，期满后统一评审（对齐 memo55 月度复盘编排；`docs/_working/quant_methodology/04_switch_friction.md` §2）。
2. **冷却期 ≥60 交易日（建议）**：下岗后 60 交易日内禁重新参选（复用 refit 间隔常数 `docs/_archive/62_business_registry_construction.md`:825 + `config/exam_scale_cost_gate.yaml`:17 min_days=60 现行值，04册 §2）。
3. **net-zero 对价（04册 §2 原文）**：任职期=月度复盘编排（memo55 §3.6 MonthlyRiskGovernance）加一条评审输入，禁新机制；冷却期=复用 refit 间隔常数。
4. **安全阀不受任期保护（建议）**：KillSwitch 熔断、预算带 0% 段禁开仓、X 流信号驱动离场（distribution 段 D98 语义）等风险关停**即时生效，不受 20 日任期保护**——任期只缓"业绩轮换"，不缓"风险关停"；此条为现行安全机制优先级的重申，零新机制。

### 3.4 切换三行账（缺任一行=评审不受理）

按 `docs/_working/quant_methodology/04_switch_friction.md` §3 立法口径：①本次切换预估摩擦 bp（按最高成本档 40bp 压力问："换完之后新配置在 40bp 档还活着吗？"，survival_floor=0.0，exam_scale_cost_gate.yaml:13）；②新配置五档存活证明（cost_tier_sharpes_json）；③切换换手计入年度 8x 预算后的余量（turnover_gate.cap_annual_x=8.0，exam_scale_cost_gate.yaml:18-22——**切换产生的换手计入 8x 预算，不得超发**）。

### 3.5 切换执行伪代码（非生产代码）

```
function 切换申请(新配置 n, 旧配置 o):
    三行账 = [摩擦bp按40档(n), 五档存活证明(n), 换手余量(n, 8x)]
    if any(三行账.缺):    return 不受理("三行账缺行")     # §3.4
    if not 冷却期已满(n): return 不受理("冷却期内")         # §3.3.2
    if not 滞回带允许(d): return 保持现状                    # 隶属度<0.60 → ×0.5 保守侧
    return 提交评审(三行账)                                  # 评审制，非自动执行
```

## §4 降级与退出（处理序）

### 4.1 下岗触发器（评审制铁律：触发器非自动关停）

LB（业绩下界）真源=alert_threshold_registry 唯一真源，fail-closed（`src/zephyr/governance/lifecycle_governance/strategy_retirement_evaluator.py`:8/:28-30）：

| 触发器 | 判据 | 窗口 |
|---|---|---|
| THD-RETIRE-001 | 滚动实盘累计收益−基准 < −5% | 滚动 20 日（:214） |
| THD-RETIRE-002 | 滚动 Sharpe < 0 | 滚动 60 日（:215） |
| THD-RETIRE-003 | 当前回撤 > 1.5×历史最大回撤 | 事件型 |

### 4.2 处理序（LB 跌破/任期未满，机械六步）

```
S0 记档：触发器命中只生成记录，永不自动改策略状态（评审制铁律，evaluator:8）
S1 任期检查：任职 <20 交易日 ⇒ 只累计记档，不启动评审（§3.3.1；月度复盘统一过）
S2 连续确认：LB 跌破状态持续 ≥确认窗（建议 20 交易日，与最短任职期对称，
   =04册 §1"连任确认"）⇒ 才生成评审输入；单日跌破在确认窗内自行修复=自动销档
S3 评审：退休评估器出评估报告（THD 阈值 fail-closed 取数，不重算偏离度）
S4 裁定：Owner 评审 → 留任 / 降级 / 退役 三选一；
   降级=registry active→candidate（C3-02 升降级管线，02号文 §四）；退役重考开闸=三纪律
   （同卷同纪重开预注册/限额分批封顶/机制门槛+模拟盘试用期，02号文 §五=LK-09/L06-C06）
S5 冷却：裁定下岗 ⇒ 冷却截止=裁定日+60 交易日（§3.3.2），期内禁参选
S6 段位语义：状态轴相位移出该段 ⇒ 机械层 activation α=0（strict 政策，composer:163/:1009），
   **不构成下岗事件、不中断任期计算**；盘中五态 T3 预警降档只写台账不换策略
   （routing_table_v1_draft §2 消费序原文）
```

### 4.3 降级与退出的语义边界

- **降级**（registry 状态变更）与**失活**（当日 α=0）与**退役**（评审+裁定+死亡证明）三词不得混用；上岗规则只裁决"上岗/下岗"（治理层），registry 流转走 C3-02，死亡证明走退役听证（17号文 §七·退役听证行：零客条目退役须死亡证明，禁静默删）。

## §5 衔接接口（与 E8 装配层、7态×15员矩阵）

### 5.1 与 E8 装配层（未建，IBT-C01=L06-C08）

- 本规则 v1 裁"谁上岗"（sleeve 集合），E8 裁"给多少"（权重）；E8 缺位期间**本规则不得自造权重矩阵**，v1 配比仍走 PP-001 sleeves×预算带+60% 硬顶+过渡带折减现行口径（`config/trading_decision_map.yaml` portfolio_plan 段 PP-001；routing_table §2）。
- **输出契约=PackageDecision**（`docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md`:128）：`enabled_packages`/`per_package_cap`/`source_cell`（TDM-E-L1|<state> 溯源格子）/`source_confidence`（proposed|verified 如实透传不粉饰）/`incomplete`（pending-owner-adoption 空格导致残缺=true）。本规则的上岗名单即该契约的 enabled_packages 真源。

### 5.2 与 7态×15员矩阵

- **v1 预注册明确不做**："成员 mix 的 regime 切换（7 态×15 成员权重表）v1 不做（避免自造权重矩阵；留 E8 装配层）"（`docs/_working/integrated_backtest/IBT-PROTOCOL-V1.md` §7:96 原文）——本稿继承该预注册决策，本规则产出=矩阵**未来填格的行原料**（上岗名单），填格数据源=本轮 GPU 成绩单+批 D 新名单（SKEL L06-H/L06-C08），施工随批 D+考试成绩驱动。
- IBT-A 静态整装/IBT-B 四层联动两配置在本规则管辖外（协议 §7 预注册语义不变），本稿零触碰。

### 5.3 消费序（编排器 S4 位次，维持蓝本原文）

编排器 S4 查 state_matrix（挂谁）→ PP-001/alloc_budget_daily（给多少钱）→ 盘中五态行（T3 预警降档，只写台账不换策略——**盘中重判=明确不做**）（`docs/_working/daily_loop_campaign/routing_table_v1_draft.md` §2+蓝本 :29 S4 行）。S4 期望产出 PackageDecision（蓝本 :29），本体不存在=BT-P1-031（消费链虚挂，如实标注）。

### 5.4 双层语义隔离（本稿新立条款，防越权）

1. **机械层**（日频，自动）：activation 折算+预算带+滞回折减+α 强制 0（strict）——framework_composer/编排器现行口径，无人为裁定介入。
2. **治理层**（评审窗，裁定）：上岗/下岗/降级/退役——本规则 §2/§4。
3. 互相越权禁止：**机械层不得替代治理层**（α=0≠下岗，禁"连续 30 日 α=0 就自动除名"式变体）；**治理层不得绕过机械层**（上岗≠每日必激活，euphoria/distribution 挂员恒不激活的披露照抄为法定事实）；死成员摊派闸 DEAD_MEMBER_ALPHA_SHARE_LIMIT=0.25（composer:182 唯一阈值真源）对两层同时生效。

## §6 判据索引总表（17号文对照，凡例=冻结/建议两档）

| ID | 判据 | 量化线 | 档 | 17号文锚 |
|---|---|---|---|---|
| J-01 | 成绩单批准入·完成率 | manifest=3,700 格±0；三 dead=0 | 冻结 | §一·完成率行 |
| J-02 | 成绩单批准入·成本门真实性 | 抽查≥50 格五档全真跑；40bp 档 sharpe≥survival_floor(0)；五档单调非增 | 冻结 | §一·成本门真实性行 |
| J-03 | 成绩单批准入·有效样本 | N_eff≥12 | 冻结 | §一·有效样本行 |
| J-04 | 统计门·DSR | e7_defense 浮动门槛（n_trial_ledger 累计口径，裁定#306） | 冻结 | §一·DSR 行 |
| J-05 | 统计门·mSPRT | M≥1/α（α=0.05→20）显著晋升 | 冻结（代码常量位禁改） | §一·DSR 行同族统计门；数值真源=msprt_champion_challenger.py:145-146 |
| J-06 | 负结果纪律 | 主效应前 20% 外全部入 negatives.csv | 冻结 | §一·负结果纪律行 |
| J-07 | 垃圾触发线 | 任一命中⇒整批成绩单禁用于上岗判定+报 Owner | 冻结 | §一·垃圾触发线行 |
| J-08 | 多重检验三件套 | haircut+DSR+PBO 逐格报告（PBO 接线=LK-08 未落地，过渡口径见 §2.2⑤） | 冻结 | §一·多重检验正式判据行 |
| J-09 | 口径纪律 | 考尺口径相对排名；IBT-D01 先于解读；同名格 sharpe 差>30% 列差异清单 | 冻结+(建议容差) | §一·解读纪律行 |
| J-10 | 判据真源守卫 | 六段映射三方同源+守卫绿；垃圾触发线未命中；无守卫映射不得驱动切换 | 冻结（前置=附录C §4 六步落账） | §一·垃圾触发线行（守卫语义）+§五-6 反面教材（04册 §3 锚） |
| J-11 | 下岗 LB 阈值 | THD-RETIRE-001/002/003（−5%/20 日、Sharpe<0/60 日、回撤 1.5x） | 冻结（alert_threshold_registry 唯一真源） | 凡例·冻结判据档；真源=strategy_retirement_evaluator.py:28-30 |
| J-12 | 切换三行账 | 40bp 压力存活/五档存活证明/8x 余量，缺一不受理 | 冻结（8x=预注册） | §一·成本门真实性行（40bp/survival_floor 同源）+§一·DSR 行（五档同源）；细则真源=04册 §3 |
| J-13 | 做T 包附加门 | WFE=OOS/IS≥50% ∧ Wilson LB 衰减≤30% 双轨 | 冻结 | §三.2 行 |
| J-14 | 任期/冷却/确认窗 | 20/60/20 交易日 | **建议**（Owner 可调） | 凡例·建议判据档；提案真源=04册 §2+62号文:825+exam min_days=60 |
| J-15 | 滞回带数值 | 0.60×0.5（现行值入册）+带宽≥2×切换成本（**建议**半条） | 冻结+（建议） | 凡例·两档各半；真源=daily_decision_orchestrator.py:98-99+04册 §1 |

## §7 前置依赖与生效条件（如实标注，逐项可核）

| # | 前置 | 现状（2026-09-25 实测） | 缺位后果 |
|---|---|---|---|
| P1 | 六段切源落账（附录C §4 六步） | 产线切源+守卫测试已在码（orchestrator:527+TestSixStateTruthChainSwitch）；收编共享真源/历史重算/锚定表语义裁定三步以生效日实测为准（07号文 :72 已批开工） | J-10 恒红⇒R4 不共振⇒全保持现状（fail-closed 不误切） |
| P2 | GPU 成绩单落盘 | grid_20260924-213246 T1 3,700 格跑批中，manifest 期末一次落盘（SKEL L06-A③） | 候选集为空⇒全保持现状 |
| P3 | IBT-D01 口径对照表先于解读（L06-C03） | 未出（成绩单周六出，对照表须先在） | J-09 恒红⇒禁解读禁上岗 |
| P4 | D31 数值 proposed→confirmed+L06-C02 三空格 Owner 填格 | 三格 pending-owner-adoption（yaml:5576-5587，AI 禁自填） | ignition/euphoria/distribution 三段 R2 恒不共振 |
| P5 | Owner 采纳裁定（本稿生效门） | 未裁（本稿=DRAFT） | 全文不生效，现行行为零变更 |
| P6 | 编排器 S4 本体（BT-P1-031） | 不存在（消费链虚挂，SKEL L06-E③） | 本规则先进评审/回测侧消费，生产编排侧接线随 S4 施工 |

## §8 落地路径（与 routing_table §3 三步合批呈批）

1. 映射常量收编共享真源（附录C §4 第 2 步对齐，src 禁 import scripts 边界内落位）；
2. 本册数值（滞回 0.60×0.5 已在码；任职期 20/冷却 60/确认窗 20/带宽 2×）经 Owner 采纳后随 D31 同批 confirmed 入 config（Owner 门位逐项批）；
3. 空格填格（TDM-E-L1 三格）=Owner 资金分配门位（R41 封闭词表，L06-C02）。

---

**立法稿完**。自检：六使命项全覆盖（§1=①，§2=②，§3=③，§4=④，§5=⑤，§6=⑥）；伪代码 4 块全为语义表达；零件零新件、gate 零新增；前置 6 项逐项如实；全部引用带仓库路径。
