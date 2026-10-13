---
ttl: task_bound
title: 四模块收口落地呈批件——SIG-021/022/088/113 接口级迁移工单逐件呈批（Owner 轨 B 保留面）
created: '2026-10-13'
session: st-cdx-capital-20261013
status: ruling_draft_for_owner
family_id: CONDAXIS-CAMPAIGN
completes_when: 四步逐件获 Owner 裁决（或按建议默认追认）且迁移工单落地后随 CONDAXIS-CAMPAIGN 归档
---

# 四模块收口落地呈批件（7_consolidation_ruling_draft）

> **上游裁决链**：P1 统一呈批包 C2（01_ruling_package.md §F 组）已裁"按建议方向出接口级合并方案先审后动"——本件即"先审"对象：接口级方案真源=挖矿作业簿 [5_module_consolidation.md](5_module_consolidation.md)（四件逐行实读＋全 src import 反查实证），本件将其正式化为**落地工单逐件呈批**。
> **保留面声明（宪法 §5）**：步骤涉模块退役/降级=业务资产轨 B 保留面——本件**只呈批不执行**；批准后由施工车道按序落地，每步一袋原子提交。
> **回滚总锚**：四步各自独立成袋（独立 commit），任一步回滚=`git revert <该步 commit>`，禁跨步部分回滚；文件迁移步另须 `generate_project_depgraph.py --force` 重建（RENAME-DEPGRAPH-SYNC 纪律）。

## §0 重叠矩阵与目标形态（事实面，全录自 5_module_consolidation §1/§3.0）

- **SIG-021** institutional_behavior_analyzer（680 行，production/stable）：六阶段识别＋洗盘vs出货＋诱多＋主力vs游资；**真实触达产线**（short_term_stock_selector 字段级 main_force_phase → daban_sleeve_strategy production 资格门）；SIG-088 已依赖其 BehaviorPhase 枚举。
- **SIG-022** capital_flow_pattern_analyzer（474 行，production/stable）：四线五形态＋散户狂热反向；经 selector 字段级 capital_flow_pattern 触达同一产线链。
- **SIG-088** capital_behavior_orchestrator（306 行，testing）：七类画像＋合力合成＋阶段推演；**零真实消费方**（全 src import 仅 __init__ 再导出）。
- **SIG-113** banker_pattern_simulator（349 行，production/evolving/**human_gated**）：庄家六阶段词表（与 SIG-021 交叉四项、独有对倒/护盘、缺试盘/再洗盘）＋规则库＋转移矩阵＋反庄沙盒；**零 import 消费方**。
- w5_1 逐对裁定：SIG-021×SIG-113=**同物**（两套词表两套转移语义→收敛唯一，SIG-021 吞 SIG-113 识别面）；SIG-113 sandbox=跨域同语义（移域或退役）；SIG-022×SIG-088=**跨粒度不同对象**（形态面 vs 归因合成面→不并文件，功能面供给）。

## §1 四步逐件呈批

### 第一步（3.1）观测适配器建立供给关系 ——【纯机械可先行·零保留面】

| 面 | 内容 |
|---|---|
| 工单 | 新建 `src/zephyr/signal_ashare/capital_observation_builder.py`：`build_retail_observation`（调 SIG-022 `retail_frenzy_contrarian:340`）＋`build_institutional_observation`（调 `detect_institutional_divergence:369`）＋共振度（`analyze_resonance:398`）→ 喂 SIG-088 `CapitalObservation`。**SIG-022 方法原位调用不迁移**（组合优于搬移），selector 契约零风险 |
| 前置 | CREATE-GUARD token＋模块大白话简介登记（add_module_translation.py）＋depgraph file 节点登记（apply_depgraph.py --add-design-node … D_SIGNAL --granularity file，nightmine MOD-BT-249 先例 node_id=16575810 同式） |
| 回滚锚 | 单袋提交；回滚=`git revert <袋1>`（纯新增文件，revert 即净删；无既有件改动） |
| 停点 | **非保留面**——P1 C2 已裁"方案先行"；此步与 C 环节观测适配器同件（挖矿册 3_C §4 已裁施工），无需再批，**列此仅为工单完整性与回滚锚登记** |

### 第二步（3.2）SIG-113 识别面并入 SIG-021 ——【保留面·须 Owner 批（涉 SIG-113 缩编与词表治理）】

| 面 | 内容 |
|---|---|
| 工单 a | **词表收敛**：InstitutionalBehaviorResult 新增 `phase_tag: str = None` 二级标签；映射常量 `BankerPhase→BehaviorPhase`（建仓→BUILDING｜洗盘→WASHING｜拉升→PULLING｜出货→DISTRIBUTING｜对倒→WASHING+tag"对倒"｜护盘→RE_WASHING+tag"护盘"）；反向缺项（试盘/再洗盘）由 SIG-021 打分器原生覆盖——**词表收敛后 SIG-113 六词表退役** |
| 工单 b | **规则库迁移**：`PriceVolumeRule`(:70-95)＋`match_phase`(:221-264)＋`_score_rule`(:266-289) 整体迁入 institutional_behavior_analyzer.py 改名 `RuleBasedPhaseRecognizer`（`identify_behavior_phase:305` 的规则型第二通道，advisory 标注不进产线）；`BankerPatternError` 保留原码 ZA-SIG-0135 迁入；**human_gated 标记随迁禁降级** |
| 工单 c | **转移矩阵去重**：删 `transition_allowed/next_phases`(:291-299)——SIG-088 `_infer_next_phase:197`＋SIG-021 主链已承载不可跳跃语义（w5_1 同真源可派生→必并） |
| 工单 d | **产线回归**：selector `main_force_phase` 字符串值域**冻结不变**（六主词；phase_tag 不进该字段）——daban sleeve 资格门契约保全 |
| 选项 | A 按上表四件执行（SIG-113 缩编为空壳随第三步一并处置）；B 仅迁规则库保留双词表（**不推荐**：双词表=漂移温床，病灶①原样） |
| 建议默认 | **A** |
| 回滚锚 | 单袋提交（迁移+删除原子）；回滚=`git revert <袋2>`＋`generate_project_depgraph.py --force`；测试随袋（test_banker_pattern_simulator.py 用例随迁，删除行=0 纪律） |
| 停点 | **保留面**：SIG-113 识别面退役=模块缩编（轨 B）；词表=治理资产。**批准即动工，不批冻结** |

### 第三步（3.3）SIG-113 沙盒面处置 ——【保留面·须 Owner 二选一】

| 面 | 内容 |
|---|---|
| 事实 | `sandbox_simulate`(:301)＋`SandboxResult`(:108)＋`_default_risk_warnings`(:191) 零消费实证（5_module_consolidation §1 全 src import 反查）；w5_1"零触发零消费→退役"判据命中 |
| 选项 A（推荐） | **退役挂账（墓碑制）**：30 天复活窗＋引用即复活评估＋季度打包清账（宪法 §5 治理资产净删下放面）；复活条件=反庄回测策略立项 |
| 选项 B | **移域**：迁 execution_simulation 域作回测组件（若 Owner 认为反庄沙盒终局有位） |
| 建议默认 | **A**（零消费实证在手；B=为不存在的消费方保维护面） |
| 回滚锚 | A：墓碑登记袋，回滚=revert＋复活窗内可直接恢复；B：`git mv` 袋＋depgraph --force（RENAME-DEPGRAPH-SYNC） |
| 停点 | **保留面**：退役/移域均须 Owner（轨 B） |

### 第四步（3.4）SIG-022 冻结为特征供给件 ——【保留面·须 Owner 批（降级=演进权收缴）】

| 面 | 内容 |
|---|---|
| 工单 | 文件不迁、五类形态保留（selector 消费中）、`CapitalFlowPatternConfig` 阈值族不动；头注新增**演进冻结条款**：新能力一律进观测适配器/SIG-088，SIG-022 停止长新形态（防簇复发） |
| 选项 | A 批准冻结条款（[MATURITY] production 维持）；B 维持自由演进（**不推荐**：同域簇复发入口） |
| 建议默认 | **A** |
| 回滚锚 | 单袋提交（头注+条款纯文档面）；回滚=`git revert <袋4>` |
| 停点 | **保留面**：production 模块演进权收缴=降级面（轨 B） |

## §2 施工顺序与依赖（批准后）

```
批准 ──→ 第一步（可立即动工，无需等批）──→ 第二步 ──→ 第三步(A/B) ──→ 第四步
                                         （袋2 依赖袋1 无强耦合，仅序贯纪律）
```
- 每步独立可回退（§1 各回滚锚）；**禁跨步部分回滚**（词表收敛与矩阵删除必须同袋原子，半袋=双词表漂移态）。
- 全程产线契约冻结条款（selector 两字段字符串值域不变）由第二步工单 d 承载，任何一步违反即整批回退。
- MOD-SIG-113 模块册/blueprint/depgraph 随第二/三步同步缩编登记；净零声明=合并替代（宪法 §4.1）。

## §3 呈批请求

| # | 请求 | 建议默认 |
|---|---|---|
| R1 | 第二步四件工单（词表收敛＋规则库迁移＋矩阵删除＋产线回归）批准 | A 批准 |
| R2 | 第三步沙盒面 A（墓碑退役）/B（移域）二选一 | A 墓碑退役 |
| R3 | 第四步 SIG-022 演进冻结条款批准 | A 批准 |
| R4 | （随批确认）第一步已按 P1 C2 先行授权动工——如需补批请一并署名 | 追认 |

> 呈批不空等：R1-R3 冻结待裁期间，四模块现状零改动（本件纯呈批件，零代码零注册表变更）。
