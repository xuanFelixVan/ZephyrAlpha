---
ttl: task_bound
title: T1-α 节点挖矿：TDM PP-001 sleeve 资金分配规则内核
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 节点挖矿：TDM PP-001 sleeve 资金分配规则内核（父环节 S11_assembled_backtest；真源 trading_decision_map.yaml portfolio_plan）

> 挖矿依据：decision_kernel_mining §5 子节点第 2 件——auto_mount 的 sleeve_plan 资金
> 分配规则（新 sleeve 0.05 等权起步/老 sleeve 等比缩水）从未被论证过。产出=数据，
> 采纳裁定归主力会话施工班。

## 1 现状盘点（逐条带 file:line 锚点）

### 1.1 分配规则本体（auto_mount.py）

- **起步档**：新挂 sleeve 固定 `NEW_SLEEVE_WEIGHT=0.05`（auto_mount.py:60），与策略
  历史表现/容量/回撤无关（sleeve_plan L150-157）。
- **老 sleeve 等比缩水**：`scale=(1-0.05×n_new)/keep`，全体老 sleeve 同乘（L152-157）。
- **红蓝语义门 only_add_assert**（L246-274）：挂载/格子/证据只增不减不改；sleeve 只增
  不减；老权重仅允许全局等比变动（rel_tol=2e-3）；新 sleeve 必 0.05 起步——**伪改造权重
  会被硬拒**，设计纪律合格。
- **activation 判定**（_state_attribution L120-147）：翻译件 build(IS_WIN)→日收益×
  六态 dom 序（R2SIX L73：r10→capitulation、r4→accumulation、r11→accumulation、
  r3→expansion、r12→ignition）→段内 SR=mean/std×√252，SR>0 且段内天数≥MIN_SEG_DAYS
  →该段激活；`candidates=None`（选股类）→全段。
- **实证核对**：fw-tdm-current 16 员中 8 个 STR 成员 0.045（历史缩水痕）/2 个 0.05
  （framework_plans.yaml:268-291）——与等比缩水历史一致，规则执行正常。

### 1.2 数学与机制审查发现

**F1 起步权重与表现零耦合 + 单调稀释无再平衡**：新 sleeve 不看 SR/回撤/容量一律 0.05；
每挂一批，老成员等比缩水。6 个 STR 已累计吃掉 0.30 质量 fw-tdm-current——但**没有任何
"整装回测证据→sleeve 权重升降"的回路**（S11 README 欠账 7+decision_kernel ①下游同源）。
业界多策略组合惯例=sleeve 权重带约束+表现驱动再平衡（Man Group 多策略构建；arXiv:2406.09578
2024 asset-specific regime allocation）。0.05 保守起步本身可辩护（新成员观察期），缺的是
观察期之后的**晋级/降级机制**。

**F2 activation 判定的三处弱点**（_state_attribution L120-147）：
- **无多重检验纪律**：6 态×N 策略逐段做"SR>0"判定，无 FDR/Wilson 类校正——C3 验证链
  （S03）在别处执行多重检验纪律，此处为旁路。样本=IS_WIN 段内（in-sample），无 OOS 确认。
- **R2SIX 语义对表（已核实，2026-09-15 本挖矿）**：TDM 六段真源注释=capitulation 恐慌
  投降/accumulation 吸筹修复/ignition 点火/expansion 发酵/euphoria 亢奋/distribution
  派发（trading_decision_map.yaml:4310-4311），六段预算带（L3591-3593：euphoria ≤30%
  只卖不买/distribution 0% 空仓）。R2SIX 对表结论：r4 熊市阴跌→accumulation（吸筹修复）
  **语义可辩护**（阴跌≈修复期吸筹，与 4310 行定义相容）；**结构性盲区=euphoria 与
  distribution 无任何 regime 态映射**（R2SIX 仅覆盖 r3/r4/r10/r11/r12→四段）——
  整装/预算带中最关键的防守两段（亢奋只卖、派发空仓）在 auto_mount 归因链上**永不触发**。
- **段内判定参数（已核实）**：MIN_SEG_DAYS=30、IS_WIN=("2020-01-01","2023-12-31")
  固定窗口（auto_mount.py:59-60）——**IS 窗冻结**：2024-01 起的市场数据完全不参与
  activation 判定（build() 权重与段内 SR 同源冻结），新鲜度问题归 SLE-3 加固范围。

**F3 无退场机制（单向门）**：only_add_assert 禁删 sleeve+composer 权重域 (0,1] 不收 0
（decision_kernel T1A-3）——**PP-001 结构上无法表达"策略退役"**。策略衰减（S15 判死）
后资金无法回收，唯一出路=老 sleeve 等比继续稀释，组合逐渐碎片化。"废"状态缺执行位。

**F4 数值卫生**：sleeve_plan `round(,6)` 逐项舍入后 Σ 可能漂移 1e-6 级（L154）；下游
fw-tdm-current 校验容差恰为 1e-6——边界同量级，建议生成器侧 Σ 归一兜底（低风险登记）。
`keep=0` 分支 scale=0（L153）在 n_new>20 时 sum≠1——现行 16 员远未触及，仅登记。

**F5 权重质量与 activation 双真源未对表**：TDM sleeves 权重（PP-001）与 activation_state
（分状态归因）同表落库，但 fw-tdm-current 的 activation 只进 x_tdm_provenance 元数据
（decision_kernel F3），两套信息在消费端合流前已断——本节点不重复立项，指向 T1A-3。

## 2 六向挖矿日志表

| 向 | 内部发现 | 外部发现（URL+发布方+年份） | 判定 |
|----|---------|---------------------------|------|
| ①上游 | 新 sleeve 起步权重不消费 S03 验证证据（四闸/DSR 通过≠资金份额），S03→PP-001 之间无传导函数 | 新策略入池渐进配置（Man Group 多策略构建，man.com；Hedge Fund Journal sleeve 带状约束，thehedgefundjournal.com） | signal |
| ②下游 | PP-001 sleeves→generate_framework_plan_from_tdm→fw-tdm-current（已通）；→实盘执行层（pf_alloc 预算）未通——回测/实盘双轨（regime_supply_chain F2 同族） | — | signal |
| ③机制 | F1-F5 五发现（1.2） | 表现驱动 sleeve 再平衡/风险预算（arXiv:2406.09578，2024；Man Group 惯例） | signal |
| ④后端 | 无退场机制的执行位缺口=composer 0 权重域+only_add 断言联合造成（F3） | — | signal |
| ⑤前端 | sleeve 权重变化无面板/播报（仅 auto-mount-report 落盘）——登记不施工 | — | 已查无 |
| ⑥数据字段 | TDM sleeves/activation/挂载证据全在 trading_decision_map.yaml 单表；缺=策略级"观察期起算日/晋级判据"字段 | — | signal |

**计数：signal 5 / noise 0 / 受阻 0 / 已查无 1（⑤前端）。**

## 3 业界与开源对照（逐条过四闸）

| 对照项 | 来源 | 四闸结论 |
|--------|------|---------|
| 表现驱动的 sleeve 权重再平衡 | arXiv:2406.09578 Dynamic Asset Allocation with Asset-Specific Regime Allocation（2024）；Man Group 惯例（man.com，访问 2026-09） | **立卡候选**：观察期后按整装回测分段证据做权重升降（带约束防跳变）。A 股适配：T+1+涨跌停下单次调权幅度需带限。可回测（fw-tdm-current 历史 16 员现成）。**待验证**（单来源+惯例级，施工前补第二来源） |
| 新成员渐进配置（观察期起步档） | Man Group/Hedge Fund Journal（同上） | **对等已有**：0.05 flat 起步属业界常见保守档；缺的是"起步之后" |
| 组合退役/退场纪律 | SR 11-7 关停权限归人（S07 README R4 已引，美联储框架解读） | **立卡候选**：Owner 门位=production 流转（宪法 §5），缺的是"组合层退场"的执行位与流程（F3） |

## 4 堵点与欠账清单（concrete）

| # | 堵点 | 位置 | 验收标准 |
|---|------|------|---------|
| SLE-1 | **晋级/降级回路**：整装回测证据→sleeve 权重调整的闭环（带约束版本，配合 T1A-3 零权重支持）——先出规则设计稿（观察期 N 月/判据=分段 SR+回撤/调幅带限/Owner 门位），再施工 | auto_mount.py sleeve_plan 旁路新增 adjust_sleeve_weights（不动 only_add 语义门，新增语义门） | 规则稿过挖后自审闸；模拟调权一次（只出 diff 不 apply）Owner 审 |
| SLE-2 | **退场执行位**：composer 0 权重支持（T1A-3 同件）落地后，PP-001 增加 weight=0/retired 语义+only_add 断言放行规则（0 视为退役非删行） | auto_mount.py:246-274 + framework_composer.py:241 | 测试：retired sleeve 保留行且不参与合成；38 规则校验绿 |
| SLE-3 | activation 判定加固：①段内 SR 判定加多重检验意识（至少：全段 SR 与段 SR 联合判定/OOS 段确认）；②IS_WIN 解冻改滚动窗（现冻结 2020-2023，2024+ 数据缺席）；③euphoria/distribution 盲区——归因链增"亢奋/派发"检测（可复用 T4 赶顶/T5 逃顶转换信号）或显式登记该两段不适用 sleeve 激活 | auto_mount.py:59-60（IS_WIN）、120-147（归因）、73（R2SIX） | 核实结论+加固方案落档；滚动窗重跑后 activation 清单 diff 出给 Owner |
| SLE-4 | sleeve_plan Σ 归一兜底：round 后 Σ 偏差在生成器侧归一（1e-9 级） | auto_mount.py:150-157 | 单测：极端 n_new 下 Σ=1（容差 1e-6） |
| SLE-5 | sleeve 变动播报：挂权/调权/退役事件进 Alerter（复用 S12 通知链，登记不施工） | — | S12 施工时并入 |

## 5 子节点清单

| 节点 | 为什么值得挖 | 建议投喂材料 |
|------|-------------|-------------|
| PP-001 本体与 state_matrix 格子体系 | ~~R2SIX 六态对表~~（本挖矿已对表完成，见 F2）；剩余：state_matrix 格子 confidence 体系（proposed/verified）与挂载证据链的治理质量 | trading_decision_map.yaml PP-001 节点+state_matrix+design_memos/25_multifactor_strategy_detail.md |
| pf_alloc 预算分配器（实盘侧资金链） | PP-001 静态权重→实盘动态预算之间的 MOD-PA-003/PA-007 从未与回测侧对表（regime_supply_chain F2 下游同源） | src/zephyr/pf_alloc/core/ 14 件 |

## 6 封矿判定

- **本节点主体封批**：分配规则本体挖透（起步档/等比缩水/语义门/activation 判定四件全
  带 file:line）；五发现 concrete 到验收标准（§4 SLE-1~5）。
- **未枯竭部分转子节点**（§5 两件）：TDM 六态语义真源对表、pf_alloc 实盘资金链对表。
- 一句话结论：**PP-001 的资金分配是一台"只进不出、不看业绩"的机器——起步档保守合格、
  语义门纪律合格，但没有晋级/降级/退役三件套：挂上是单向门，权重与整装回测证据零耦合，
  组合会随挂图数量单调碎片化。三件套（SLE-1/2/3）应作为 TDM→实盘资金链的先决件立项。**

## 7 施工回填（#13 T3③ R2SIX 盲区 + IS_WIN 冻结解除，2026-09-16 复验）

> 回填人：st-qoder-t1a-20260915。结论：§4 SLE-3②③ 与 SLE-1 已由车道 B/B2 施工落地并合入主干
> （commit b2b1c5c928 SLE-3②③ + 105b0d02d7 三处真缺陷修复批）。本回填只做真数据复验与残余登记，
> 授权脚本零改动（复验证据见 §7.2）；验收口径=auto_mount `--explain` 的 phase_before/phase_after。

### 7.1 做了什么（对照 SLE-3 / 任务 a·b·c）

- **(a) euphoria/distribution 盲区（SLE-3③）**：归因链新增微观情绪相位 `phase_overlay`
  （广度指数 399106 收盘 + 涨家数占比，全 trailing 无前视），与宏观腿 `R2SIX` 经 `resolve_six_phase`
  两轴合成六段相位；`CLASS_CANDIDATE_STATES["value_reversal"]` 纳入 euphoria/distribution，L1 防御格
  自此进入候选检验队列。设计迭代：v1（乖离+波动分位+HMM r3 门）2019-2026 仅命中 4 天、两处公认
  亢奋顶全漏（根因 HMM dominant 跨期 label switching）→ v2 定稿微观情绪轴，冰点/复苏 r10/r11 优先不被覆盖。
  **映射真源核查（任务"若在 YAML 就改 YAML"）**：六段词表真源=`zephyr.signal_ashare.core.environment_switch.SIX_STATES`
  （代码封闭集，已 import 复用无第二真源）；亢奋/退潮需实时广度计算、非静态字典可表达，故不存在
  "YAML 里有盲区待改"的情形；宏观腿 R2SIX 与 `framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE`
  孪生表由守卫 `test_r2six_drift_guard_vs_framework_composer` 钉防漂移。
- **(b) IS_WIN 冻结（SLE-3②）**：判定窗终点由写死 2023-12-31 改为 `IS_WIN_START` 锚 +
  快照表最新可用日回退 `PIT_TAIL_LAG=1` 行动态派生（`load_phase_panel`，auto_mount.py:80/262）。
- **(c) 0.05 平铺起步（SLE-1）**：**未擅改交易参数**（经核）。F1 判定 0.05 观察期起步"本身可辩护"，
  挂图路径（only-add 放行域）保留 0.05 起步 + 老 sleeve 等比缩水（`sleeve_plan`）；另新增真实分配语义
  `sleeve_weights`（w ∝ 正超额 SR×置信÷年化波动，风险预算口径）作**提案面**，`--rebalance` 只出 diff
  永不写图，落图须过 `weight_adjust_assert` + Owner 门位。第一性理由：0.05 是"新成员观察期"下限、非
  绩效参数，直接改会与 only-add 语义门冲突；缺的是观察期后的晋级回路，已由 SLE-1 提案面补上。

### 7.2 证据（真数据复验，小窗口抽样——全窗仅日频 index/snapshot 级，无重算）

- 数据可用性（CH 只读，经 `zephyr.data.ch_reader.query`）：
  - `c1_backtest.regime_snapshot_history`：**2019-04-01 .. 2026-09-15**（3621 行）→ **2024+ 数据真实存在**，
    IS 窗冻结无数据侧阻碍，解除成立（非假数据、非静默回落旧窗）。
  - 广度 399106 收盘 1996-05-10..2026-09-15；`advance_count>0` 止于 **2026-07-02**（F4 结构性断更，
    known_data_gaps 已登记，provider 侧另有车道修），断更日按 `RegimeFeatureBuilder._load_breadth`
    同门口径回退 `EQW_ALLA`（kline_index_calc，adv>0 覆盖 2019-01-03..2026-09-15）→ 微观相位腿全窗可用。
- **防御段触发前后对比**（`explain_panel`，判定窗 `2020-01-01..2026-09-14`，3248 交易日）：

  | 口径 | euphoria 天数 | distribution 天数 | 防御段合计天数 | 防御段触发次数(episodes) |
  |------|--------------|-------------------|----------------|--------------------------|
  | 改造前（仅宏观腿 R2SIX） | 0 | 0 | **0** | **0** |
  | 改造后（宏观 ⊕ 微观 overlay） | 76 | 362 | **438** | **50**（euphoria 13 / distribution 37） |

  → 盲区从"恒 0、永不触发"变为可被真实触发（**+438 日 / +50 次**）。
- 传播落地图证：`config/framework_plans.yaml:252` 已有 sleeve `activation: ignition+expansion+euphoria`
  经生成器落图，证明补全相位贯通 ②→fw-tdm-current。
- 测试全绿（fake 面板/引擎零 IO，tmp_path 隔离，不触生产 data/）：`test_auto_mount_sle3.py` 12 +
  `test_auto_mount.py` 64 + `test_generate_framework_plan_from_tdm.py` 11 = **87 passed**。

### 7.3 残余（登记不硬闯）

- **SLE-3③ 落地度（防御格挂载待 Owner）**：代码侧防御段"可被触发"已闭环；但
  `config/trading_decision_map.yaml:4417-4418` 的 `TDM-E-L1` euphoria/distribution **格子仍 `mounted: []`**，
  标注 `pending-owner-adoption`——根因=PP-001 sleeves 内无防御型 sleeve 可挂，"是否新设防御档"属
  Owner 资金分配决策（非代码缺陷）。该 map 文件不在本任务授权清单且已由 map 侧如实登记，不代改；
  待 Owner 裁定新设防御 sleeve 后，挂图器即可把过 FDR 门的 value_reversal 件挂上 L1 防御格。
- **SLE-1 Owner 门位**：`--rebalance` 提案→落图的 `weight_adjust_assert` 门位待 Owner 开闸
  （真实非等比调权必然过不了 only_add），本件不自动调权。
- 判定缓存键已升 `v4`（auto_mount.py:154），相位/窗口规则再改需删 `.runtime/tmp/auto_mount_judge_cache.json` 复算。
- 本回填无新增 .py 模块（无 translation 登记义务）；授权脚本复验期未改动，ruff/高复杂度门保持合入态、零新增。
