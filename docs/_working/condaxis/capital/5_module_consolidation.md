---
ttl: task_bound
title: 四模块收口矿——SIG-021/SIG-022/SIG-088/MOD-SIG-113 同域重复簇 w5_1 合并方案（接口级）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 收口工单落地完成且随 CONDAXIS-CAMPAIGN 归档
---

# 四模块收口矿（5_module_consolidation）

> 任务：研究册 §7.3 病灶①——四个行为归因模块同域，按内收判据 w5_1（宪法 §4.2：同域重复簇→收敛唯一）出"谁吞谁"方案。**本册给到接口级**（哪个类的哪个方法迁哪），不停留在方向性；最终裁定权=P1 统一呈批包（研究册 §10.2），本册是呈批件的矿料。
> 四件全部逐行实读（头注+类/方法清单全展开）；消费方经全 src import 反查实证。

## §1 逐件台账（职责/输入输出/消费方）

| 件 | 真源路径:行号 | 职责（实读） | 输入→输出 | 消费方（import 反查实证） | 现状 |
|---|---|---|---|---|---|
| **SIG-021** institutional_behavior_analyzer（680 行） | `src/zephyr/signal_ashare/institutional_behavior_analyzer.py` | 主力行为学六阶段识别（`BehaviorPhase`:59-68 建仓/洗盘/试盘/再洗盘/拉升/出货+未知）＋洗盘vs出货（`distinguish_wash_vs_distribute`:421）＋诱多检测（`detect_bull_trap`:462）＋主力vs游资打架（`judge_main_force_vs_hot_money`:502）＋分时特征（`recognize_intraday_features`:541）；主入口 `analyze`:218、阶段判别 `identify_behavior_phase`:305（六段打分 `_score_*`:349-419） | `InstitutionalBehaviorInput`:165（量比/价幅/大单方向等）→`InstitutionalBehaviorResult`:177 | **真实触达产线**：short_term_stock_selector.py:4（字段级消费 main_force_phase 字符串，无 import）→ daban_sleeve_strategy.py:71-72/405（**production sleeve 资格门**）；SIG-088 复用其 `BehaviorPhase`（orchestrator.py:59） | production/stable |
| **SIG-022** capital_flow_pattern_analyzer（474 行） | `src/zephyr/signal_ashare/capital_flow_pattern_analyzer.py` | 四线（主力/机构/散户/游资资金线）五类形态识别（`CapitalFlowPattern`:59-67 四线开花/机构独强/背离/弱势反弹/全线溃退）＋**散户狂热反向**（`retail_frenzy_contrarian`:340）＋机构分歧（`detect_institutional_divergence`:369）＋多线共振（`analyze_resonance`:398）；主入口 `analyze`:176、`identify_pattern`:241 | `CapitalFlowInput`:124（四线净流入+价格序列）→`CapitalFlowPatternResult`:137 | short_term_stock_selector.py:4（字段级 capital_flow_pattern 字符串）→同上产线链 | production/stable |
| **SIG-088** capital_behavior_orchestrator（306 行） | `src/zephyr/signal_ashare/capital_behavior_orchestrator.py` | 七类主体画像＋合力合成（`analyze`:216→`CapitalConsensus`:159）＋六阶段**推演**（`_infer_next_phase`:197，复用 SIG-021 链不可跳跃）＋复盘 EMA 偏置（`review`:269，限幅±0.5:75） | `list[CapitalObservation]`:109（**上游注入——注入器不存在**，3_C §3.3）→CapitalConsensus（direction/strength/phase/expected_next_phase/profiles） | **零真实消费方**（全 src import 仅 `signal_ashare/__init__.py:29` 再导出；[CONSUMERS]=候选：C-014、盘前编排） | testing（strength=MVP 初拍 :34-36） |
| **SIG-113** banker_pattern_simulator（349 行） | `src/zephyr/signal_ashare/banker_pattern_simulator.py` | 庄家六阶段词表闭合（`BankerPhase`:58 **建仓/洗盘/拉升/出货/对倒/护盘**——与 SIG-021 词表交叉四项、独有对倒/护盘两项、缺试盘/再洗盘）＋价量规则库匹配（`PriceVolumeRule`:70＋`match_phase`:221/`_score_rule`:266）＋转移矩阵（`transition_allowed`:291/`next_phases`:295）＋反庄沙盒（`sandbox_simulate`:301＋`SandboxResult`:108＋风险警示 `_default_risk_warnings`:191）＋总入口 `analyze`:332 | 规则库+OHLCV 序列（DI 注入回测回调）→`PatternMatchResult`:96 | **零 import 消费方**（[CONSUMERS]="运行时装配批"＝声明面，反查零命中） | production/evolving/**human_gated** |

**重叠矩阵**：SIG-021×SIG-113=**同物**（主力/庄家阶段识别，两套词表两套转移语义）；SIG-022×SIG-088=**同域异粒度**（形态面 vs 归因合成面）；SIG-113 sandbox×回测域=**跨域同语义**。

## §2 与既有资产边界

1. **下游产线契约不可破**：short_term_stock_selector 的 `main_force_phase/capital_flow_pattern: str = "未知"` 字段（selector.py:152-153）是 SIG-021/022 的字段级契约，daban sleeve 资格门经它生效——迁移期两字段语义与字符串值**冻结不变**，改动词表=破产线。
2. **SIG-088 对 SIG-021 的既有依赖**（`BehaviorPhase` 复用+不可跳跃不变量 orchestrator.py:8）——收口后此依赖更紧（同族），不变量条款随迁移一并继承。
3. **SIG-113 的 human_gated 标记**（头注:12）随代码迁移到宿主文件，禁在迁移中降级为 ai_modifiable。
4. **cohort_daily_ledger 盘后结算层**（C 环节 §2.1）与四件全部正交（表消费 vs 信号计算），不在本收口范围。
5. **wyckoff_engine（regime 域，证伪恒零）不参与收口**——不同域不同件（研究册 §7.2 量族），禁借收口顺手并它。

## §3 合并方案（接口级——哪个类的哪个方法迁哪）

### 3.0 目标形态（w5_1 判据逐对）

| 对 | w5_1 判据 | 裁定 |
|---|---|---|
| SIG-021 vs SIG-113 阶段识别 | 同域重复簇→收敛唯一 | **SIG-021 吞 SIG-113 识别面**（SIG-021=production stable+真实产线下游+SIG-088 已依赖其枚举；SIG-113 零消费） |
| SIG-113 sandbox | 跨域不同对象（信号域 vs 回测域）→移域 | 沙盒面迁 execution_simulation/回测域或退役（§3.3） |
| SIG-022 vs SIG-088 | 跨粒度不同对象→**不并文件**；同真源可派生的特征面→功能面供给 | SIG-022 降格为特征供给件（冻结演进），特征经 C 观测适配器喂 SIG-088 |

### 3.1 第一步（零风险）：观测适配器建立供给关系（不动物理文件）

- 新建 `capital_observation_builder.py`（C 环节已裁施工）：
  - `build_retail_observation(input: CapitalFlowInput) -> CapitalObservation`——调 `CapitalFlowPatternAnalyzer.retail_frenzy_contrarian:340`（散户狂热度→散户类 net/conf）；
  - `build_institutional_observation(...)`——调 `detect_institutional_divergence:369`；
  - 共振度 `analyze_resonance:398` → 聚合置信度参考。
- 此步 SIG-022 方法**原位调用不迁移**（组合优于搬移）——selector 契约零风险。

### 3.2 第二步：SIG-113 识别面并入 SIG-021（接口级迁移清单）

1. **词表收敛**：在 institutional_behavior_analyzer.py 增二级标签 `phase_tag: str`（InstitutionalBehaviorResult 新字段，默认 None）承载对倒/护盘；映射表（SIG-021 侧新常量）：
   `BankerPhase.建仓→BehaviorPhase.BUILDING｜洗盘→WASHING｜拉升→PULLING｜出货→DISTRIBUTING｜对倒→WASHING+phase_tag="对倒"（对倒=洗盘的伪量变体）｜护盘→RE_WASHING+phase_tag="护盘"`；反向缺项（试盘/再洗盘）由 SIG-021 打分器原生覆盖——SIG-113 词表不新增能力。
2. **规则库迁移**：`PriceVolumeRule`（:70-95）＋`match_phase`（:221-264）＋`_score_rule`（:266-289）整体迁入 institutional_behavior_analyzer.py，改名 `RuleBasedPhaseRecognizer`（类级组件，作为 `identify_behavior_phase:305` 的规则型第二通道）；`BankerPatternError.error_code="ZA-SIG-0135"` 保留原码迁入。
3. **转移矩阵去重**：`transition_allowed/next_phases`（:291-299）删除——SIG-088 `_infer_next_phase:197`＋SIG-021 主链已承载不可跳跃语义，第二套转移矩阵=漂移温床（w5_1 同真源可派生→必并）。
4. **产线回归**：selector `main_force_phase` 字符串值域不变（六主词+phase_tag 不进该字段）。

### 3.3 第三步：SIG-113 沙盒面处置（二选一呈批）

- **选项 A（推荐）退役挂账**：`sandbox_simulate:301`＋`SandboxResult:108`＋`_default_risk_warnings:191` 零消费——按 w5_1"零触发零消费→退役"判据墓碑制退役（治理资产净删=墓碑 30 天复活窗）；复活条件=反庄回测策略立项。
- 选项 B 移域：迁 execution_simulation 域作回测组件（若 P1 呈批认为反庄沙盒终局有位）。两选项都以"零消费实证（本册 §1 反查）"为凭。

### 3.4 第四步：SIG-022 冻结为特征供给件

- 文件不迁、`identify_pattern` 五类形态保留（selector 消费中）；头注 [MATURITY] 维持 production；**新增演进冻结条款**：新能力一律进观测适配器/SIG-088，SIG-022 停止长新形态（防簇复发）。
- `CapitalFlowPatternConfig` 阈值族不动（产线在用）。

### 3.5 迁移面总清单（施工工单的骨架）

| 动作 | 对象 | 目的地 | 伴随 |
|---|---|---|---|
| 新建 | capital_observation_builder.py | signal_ashare/ | CREATE-GUARD token+模块简介登记 |
| 迁移 | PriceVolumeRule/match_phase/_score_rule/BankerPatternError(ZA-SIG-0135) | institutional_behavior_analyzer.py（RuleBasedPhaseRecognizer） | human_gated 标记随迁；tests/signal_ashare/test_banker_pattern_simulator.py 用例随迁 |
| 扩展 | InstitutionalBehaviorResult.phase_tag + 映射常量 | 同文件 | 行为兼容（默认 None） |
| 删除 | BankerPhase/transition_allowed/next_phases | — | 迁移完成后 |
| 退役/移域 | sandbox_simulate/SandboxResult/_default_risk_warnings | （呈批 A/B） | 墓碑或移域工单 |
| 登记 | MOD-SIG-113 模块册/blueprint/depgraph | 退役或缩编 | RENAME-DEPGRAPH-SYNC 纪律（若文件名变）；净零声明=合并替代 |

**施工顺序**：3.1→3.2→3.3→3.4（每步独立可回退；3.1 不依赖呈批即可与 C 环节同批开工，3.2-3.4 待 P1 呈批 10.2 批准）。

## §4 自审闸三态裁定

| 件 | 裁定 | 理由 |
|---|---|---|
| 本合并方案（呈批件） | **施工**（产物=本册；工单待批） | w5_1 同域重复簇铁律+病灶①在册；消灭"四件各说各话的阶段词表"=终局资金行为层单一真源的前提；研究册 §10.2 建议方向与本方案一致且本方案落到接口级 |
| 3.1 观测适配器 | **施工**（与 C 环节合并批） | 零迁移风险、解锁 SIG-088 激活 |
| 3.2 SIG-113 识别面并入 | **施工（待呈批 10.2）** | 同物收敛；产线契约冻结条款已备 |
| 3.3 沙盒退役（选项 A） | **挂起排期（呈批选 A/B）** | 零消费实证在手；终局有无反庄回测位=Owner 判断面 |
| 3.4 SIG-022 冻结演进 | **施工（随 3.2 批）** | 防簇复发条款，零成本 |
| "四件全并成一件"激进方案 | **方案封矿** | SIG-022（形态面）与 SIG-021/088（阶段/归因面）跨粒度不同对象，w5_1 明令不并；激进合并破坏 selector 字段级契约，终局无位 |

**反驳者一问**（合并方案加试）：①SIG-113 词表的对倒/护盘可能含独有信息，映射丢失（对策：phase_tag 二级标签无损保留，映射表可逆）；②迁移期双通道打分可能打架（对策：主链优先、规则通道仅 advisory 标注，判据待冻结不进产线）；③SIG-113 human_gated 迁移后治理面变更需 Owner 复核（对策：迁移工单显式列 human_gated 继承条款走呈批）。维持施工。
