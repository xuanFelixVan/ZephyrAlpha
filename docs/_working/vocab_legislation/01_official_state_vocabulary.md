---
ttl: task_bound
rule_form: data
verifiability: manual
title: 官方状态/情绪词表本体立法件（词表 SSOT 第一步·W1 配套，裁定#398五①+#399四）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-22
session: st-t0-revival-20260922
---

# 官方状态/情绪词表本体（四轴+命名空间）

> 这是什么：本项目状态/情绪词表散落 28+ 套、撞名 12 类（C1 两轴撞号/C2 三套五段拼写/C11 九种最坏状态写法/最热方向相反陷阱），病根=语义层缺 SSOT 机制（03 自裁书 §1.1）。本件=词表立法第一步的本体件：立四轴官方词表+命名空间，配套 `02_state_vocabulary_mapping_register.md`（存量逐套映射登记册）。
> 常量本体真源：`src/zephyr/shared/vocab/market_state.py`（SH-VOCAB-001，W1 已建成，vnpy constant.py 同构范式）。**本件零行为变更**：存量枚举原地保留+登记映射，迁移随各线自然迭代（防大爆炸式 diff）。

## 1. 命名空间总则（立法）

1. 官方引用格式：`<轴>.<族>.<token>`，token 一律小写 snake_case；跨模块/跨文档/跨会话描述市场状态，**必须用官方词表 token 或在映射登记册登记的存量拼写**，禁现造新词。
2. 代码层引用：优先 `from zephyr.shared.vocab.market_state import ...`（官方常量模块）；存量枚举跨模块传递时必须经映射登记册声明的映射（重点=§3 四类撞名点），禁裸字符串直传。
3. 新模块出厂纪律（挂施工验收清单，construction_workflow_policy.md 验收清单同步追加）：**状态输出是否引用官方词表或在 state_vocabulary 映射登记册登记映射？** 无登记的新封闭状态枚举=验收不通过（执法门 W3 观察期 warn 先行）。
4. 可发现性：官方词表条目登记 capability 册，`capability_lookup.find("情绪周期六段"/"大盘状态")` 可命中（W4，随批登记面动作）。

## 2. 四轴官方词表（本体）

### 轴 M · 宏观 regime 轴（官方=HMM 七态）

| 官方 token | 中文 | 官方常量（market_state.py） | 备注 |
|---|---|---|---|
| m.regime.r1 | 低波震荡 | MacroRegime.R1 | 核心四态 |
| m.regime.r2 | 中波震荡 | MacroRegime.R2 | 核心四态 |
| m.regime.r3 | 牛市趋势 | MacroRegime.R3 | 核心四态；trend_up 常用面 {r3, r11, r12} |
| m.regime.r4 | 熊市阴跌 | MacroRegime.R4 | 核心四态 |
| m.regime.r10 | 危机 CRISIS | MacroRegime.R10 | 覆盖态；**九种"最坏状态"写法的统一归一目标**（见 §3-C11） |
| m.regime.r11 | 复苏 RECOVERY | MacroRegime.R11 | 覆盖态 |
| m.regime.r12 | 突破 BREAKOUT | MacroRegime.R12 | 覆盖态 |

- 态数铁律：7 态是裁定#304 锚定的代码绑定资产；4 态收敛（方向×波动 2×2）走 #398五② 回测证据专项，**证据出来前 7 态不动**。收敛时只改本表+market_state.py 一处（SSOT 的意义）。
- 数据真源：`c1_backtest.regime_state_anchored`（dominant/vol_pct，2017-07-11 起 2236 行实测）。

### 轴 E · 情绪周期轴（官方=TDM 六段）

| 官方 token | 中文 | 官方常量 | 备注 |
|---|---|---|---|
| e.cycle.capitulation | 投降（冰点） | EmotionCycleSix.CAPITULATION | TDM 六段 v1.2 定稿，Owner 已批格子语义 |
| e.cycle.accumulation | 蓄势 | EmotionCycleSix.ACCUMULATION | |
| e.cycle.ignition | 点火 | EmotionCycleSix.IGNITION | |
| e.cycle.expansion | 主升 | EmotionCycleSix.EXPANSION | |
| e.cycle.euphoria | 亢奋 | EmotionCycleSix.EUPHORIA | |
| e.cycle.distribution | 退潮（派发） | EmotionCycleSix.DISTRIBUTION | |

- 盘中五态=官方伴生轴（IntradayFive：low/defense/oscillation/attack/euphoric），经官方映射 INTRADAY_TO_SIX 挂六段（euphoric→ignition 映射为 proposed，未批前不动）。
- 持久化缺口披露：情绪六段历史标签**无持久化表**（c1_market.sentiment_panel 仅 fear_greed_index 等异轴指标，实测 09-22）——T0-CONDITIONAL 卡情绪门因此 unevaluable；六段持久化=前瞻接线义务（本班登记面，不施工）。
- 状态 vs 情绪正交（研究结论，02 决策卡 §2.2）：情绪不并入状态分类器；跨轴映射（regime→六段降维）属预测/预案轴用途，映射键登记见映射册 F4 行。

### 轴 F · 预测/预案轴（数值分布 payload，不设封闭词表）

- 官方立场（03 自裁书 W1 批准口径）：本轴 payload=数值分布，**不设封闭官方词表**，登记豁免。
- 但存量封闭预案枚举（S1_attack/S2_defense/S3_oscillation、HoldingAction、PlaybookStatus、状态转换事件 T1-T6/S1/S2 等）**逐套入映射登记册**；新预案枚举出厂必须登记映射或显式声明豁免（否则=W4 验收不通过）。
- 撞名警示：S0-S4 与水温五档、转换事件 S 系、预案 S1-S3 三处撞号——预案轴 token 一律带 `f.` 前缀（f.plan.s1_attack 等）。

### 轴 S · 个股行为轴（官方=锚定四档+强度档+StockCategory）

| 官方 token | 中文 | 官方常量 | 备注 |
|---|---|---|---|
| s.anchored.r3 / r2 / r1 / r4 | 低/中/中高/高风险 | AnchoredTier.ANCHORED_R3/R2/R1/R4 | 阈值 0.30/0.60/0.80；**与轴 M 的 r1-r4 撞名以此消解**（见 §3-C1） |
| s.strength.a…e | 强度五档（80-100/…/0-35） | quant_short_term_strength_engine（待收编进 market_state.py） | |
| s.category.main_leader 等 | 主升龙头/二进三/跟风/复苏/伪强/地天反包/中性 | StockCategory | FusionDecision 与之同词异源，官方=StockCategory（映射册 S3 行） |

## 3. 四类重点撞名的官方消解裁定（本件核心）

- **C1（r1-r4 两轴撞号，语义近镜像）**：官方消解=命名空间强制 `m.regime.r*`（宏观，r3=牛市趋势）vs `s.anchored.r*`（个股锚定档，r3=最安全）。代码层以 MacroRegime/AnchoredTier 两个官方常量类引用，**禁裸字符串 "r1"-"r4" 跨轴使用**；文档层引用必须带轴前缀。两处实物锚点：宏观=regime_detector.py:107；锚定档=anchored_state_machine.py:86-91。
- **C2（三套五段情绪枚举拼写互不兼容）**：官方拼写=EmotionCycleSix 六段（注意：三套五段与官方六段是"多对六"映射，冰点/反核/主升/疯狂/退潮 五段→官方六段中 capitulation/ignition+expansion/euphoria/distribution 对应，映射逐套登记于映射册 E1-E3 行）；三套枚举原位保留，跨模块取值必须经映射。
- **C11（九种"最坏状态"写法）**：统一归一目标=`m.regime.r10`（CRISIS）。官方执行件=market_state.py `EXTREME_STATE_ALIASES`（r10 CRISIS/crisis/CRISIS(vol)/EMERGENCY/CRASH/S0_ICE/ICE/冰点/退潮 九键全归一，实测在盘）。新代码描述"市场最坏状态"必须用 m.regime.r10 或经该归一表。
- **最热方向相反陷阱**：market_sentiment_analyzer"最热(≥80 分)→RETREATING 退潮"（:989-1000）vs youzi 引擎"最热→MANIA 疯狂"（:450-453）——同分域语义相反。裁定：两引擎的"最热→？"映射行为各自**原位保留**（零行为变更），但跨引擎传值必须经映射册 E2/E3 行声明的方向注记；新消费方接六段词表时按官方语义（最热=euphoria 亢奋，distribution 退潮只由派发证据触发，不由"情绪最热"单指标触发）。

## 4. 收编边界与后续步骤

- 本件+映射登记册=第一步（W2 收编件随本件落地）；W3 执法门（观察期 warn→硬阻断）与 W4 可发现性按 03 自裁书节奏另行施工，本班只做登记面动作。
- 词表收编不减存量行为：存量枚举原地保留，映射迁移随各线自然迭代；4 态收敛专项（②）回测证据出来前，轴 M 官方 7 态不动。
- 全资产净零申报：本立法件+登记册替代"散落词表无册可查"状态（合并评估已入 token 册 merge_evaluation 字段），不新增人工清单。
