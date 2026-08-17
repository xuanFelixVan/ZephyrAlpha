---
ttl: permanent
doc_type: architecture_view
title: 买入流 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.7.1"
date: 2026-08-15
topic: buy_flow
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-13 第二批施工（会话 AI-BUY-001），修复 detect_breakout_failure（突破失败检测）算法顺序缺陷，新建 6 模块（MOD-PA-006/TRIG-001/PLAN-001~003），合并回 dev；后续统筹补建 5 份模块蓝图（遗留 #29 闭环）。
>
> **最终成果**：83 测试两轮全绿；分批建仓、突破失败降级、买入时序、价格锚定、资金协同、T+1 约束按本档契约落码。
>
> **未做事项及原因**：
> - ~~5 个新文件 token 与既有能力名称重叠~~ ✅ 已消解（2026-08-17 AI-REGF-001，遗留 #15）：实证现库无硬碰撞，唯一异常=3 个 plan 蓝图共享伞名 tomorrow_plan_engine（跨 3 模块歧义+与先注册 decision_table_plan_engine(2026-08-05) 词干相近）——按后注册让先注册，3 token capability 改模块本名 tomorrow_boundary_planner/premarket_constraint_loader/closing_session_decision（blueprint_registry SSoT 对齐），另 2 token（buy_flow_batched_entry/trigger_list_registry）实证无碰撞保留；token 字符串未动，CREATE-GUARD 按 file 索引不受影响。
> - ~~MOD-PLAN-001/002/003 域归属不一致~~ ✅ 已裁定（2026-08-17 AI-REGF-001，遗留 #16）：读三文件实际职责（盘后边界计算/盘前约束加载/尾盘加减仓决策，消费方=买卖融合层 BM-BUY-02/BM-SELL-02，与 MOD-TRIG-001 同域同链路）——depgraph D_TRADING 实证为最佳既存域且与文件头 [DOMAIN] 一致、DOMAIN-FK 通过，零变更；D_PLAN_ENGINE 新域创建属 Owner 书面审批权限（域归属铁律），本批不自建，blueprint_registry functional_domain=plan_engine 作功能标签保留（全库 10+ 处非映射标签先例）。

# 买入流 spec

> 本备忘把 [battle_map_06_buy_flow](../battle_map/battle_map_06_buy_flow.md) 25 环节的"what is"落地为买入侧"how + when"的可施工 spec：分批节奏、时序、价格锚定、资金协同、T+1 约束。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 边界：本备忘只定买入**流的编排与时序**（when + how to enter）；选股信号（G04/G05）、板块回踩质量（G06）、仓位算法（G12）、回撤风控（G16）不在本备忘范围，本备忘只消费其产出。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G19 买入流 spec |
| 所属 | 作战地图 06 |
| 依赖 | G04-G06（选股+板块）、G12（仓位）、G16（风控） |
| 对标 | 机构分批建仓 / Wyckoff 吸筹时序 / A 股 T+1 集合竞价惯例 |
| 正交性 | ✅ 与 regime 正交（buy_flow 只消费 budget 数字，不读市场态） |
| 优先级 | P3 |
| 状态 | 已定稿·可施工（MVP 路径已明确，22/35 未就绪有降级） |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，**T+1，不能做空**）
- 选股→仓位→执行三段已由 [31_position_sizing](31_position_sizing.md) 分层裁定框架定稿（策略层粗仓位 → firm 层 Kelly → 硬上限裁剪），产出 `FirmTargetPortfolio`
- 但"拿到目标组合后，**怎么把单子打进去**"——分几批、什么时点、锚什么价、资金怎么排——尚未定 spec
- battle_map_06 已有 25 环节（6 运营态 / 18 设计态 / 1 缺失态），其中 **BM-BUY-04 分批建仓**是核心待施工环节（设计态，锚点 MOD-PA-006）

### 2.2 核心问题
battle_map_06 锁定了买入流的**环节拓扑**（多情景对策→四轨融合→决策编排→分批建仓→纪律闸→执行），但未定义：
- 分批建仓的批次划分、间隔、放行条件怎么定（BM-BUY-04 参数只给范围未定值）
- 板块回踩质量 A/B/C（[22_sector_rotation_spec](22_sector_rotation_spec.md) ②）目前是骨架，分批建仓是否硬依赖它
- 买入在盘中什么时点执行（集合竞价 / 连续竞价 / 尾盘），如何避开开盘波动与尾盘操纵检测窗口
- 买入价格锚什么（限价锚压力位/支撑位/VWAP？市价仅应急？）
- 多标的资金如何分配到单（由 31 算好的权重如何落到订单）
- budget 节流（G15）与买入执行如何协同
- T+1 约束如何影响建仓节奏与资金可用性

### 2.2.1 上游四轨与情景对策现状

> battle_map_06 锁定的买入流环节拓扑中，**BM-BUY-01 多情景对策生成 → BM-BUY-02 四轨融合 → BM-BUY-03 决策编排**是进入分批建仓（§3.2）前的上游三段。本节对这三段及其子环节给出裁定结论，闭合设计缺口。

| 环节 | 定位 | 裁定 | 一句话理由 | 重评条件 |
|---|---|---|---|---|
| BM-BUY-01 多情景对策生成 | L3 design，7 种价格运动情景（C-005）生成买入预案，consumes BM-SEL-04 次日 8 态预测 + C-006 策略库，下游 BM-BUY-02 四轨融合 | **暂缓** | 7 种情景依赖 BM-SEL-04 次日 8 态预测，而 [90_methodology_open_questions](90_methodology_open_questions.md) §7 已对 8 态预测作出"暂缓建设"正式裁定（52-53% 天花板实证）；上游预测被暂缓，本环节无可靠输入 | 90 §7 重启三条件满足 |
| BM-BUY-02-A-1 市场状态预测汇总层 | L2C design，汇总 a 3×3 矩阵 / b 叠加态 / c 8 态预测 / d 体制转换四子项，下游 BM-BUY-02-A 逻辑轨 | **分途承载，不单独建设** | a 3×3 矩阵 / b 叠加态 / d 体制转换已由 [10_regime_detector_spec](10_regime_detector_spec.md) 实质覆盖；c 8 态预测被 90 §7 暂缓——四子项各有归属或已被裁定，汇总层本身无新增价值 | 若未来 10 号与 90 号覆盖范围收缩，再评估是否需独立汇总层 |
| BM-BUY-02-A-2 因子直通裁决 Model-Free Factor Fusion | L3 design，因子加权融合绕过策略层直接产生买入决策，consumes L1 因子池 + L2-A 买入信号 + C-006 覆盖状态 | **不建设** | 与 [21_stock_selection_engine](21_stock_selection_engine.md) §3.2"双引擎融合=打板 sleeve 内部，非跨策略层"架构裁定冲突；绕过策略层直裁违反 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A 独立账本原则——策略未覆盖/冲突时应降级 L6 审查，而非因子直通 | 若 21 号 §3.2 双引擎融合边界扩展至跨策略层，或 30 号 Model A 原则修订，再重评 |
| BM-BUY-02-B 数据驱动轨 | L3 design，AI Discovery 轨道（量能/因子突变→数据轨信号），consumes BM-SEL-02 因子池 + 量能/分布特征 | **暂缓** | AI Discovery 轨道当前无承载模块；41 §4.5 已裁定 buy_flow 不读市场态；四轨中仅人工/应急两轨落地，逻辑轨降级为固定策略查表（BM-BUY-01 暂缓连带） | 信号工厂（BM-SEL-02-J）建成后，具备实时因子突变检测能力再评估 |
| BM-BUY-02-C 人工指令轨 | L3 **production**，人工指令经 MTF 仲裁覆盖自动轨，consumes 前端指令输入 + 用户策略配置 | **补接口契约**（见下） | 已落地但接口格式未在本文显式定义，补全字段表与仲裁机制 | — |
| BM-BUY-03 决策编排 | L3 design，DO 决策编排器 5 路径（买/卖/做T/人工/应急）优先级仲裁+冲突消解+去重+时序编排 | **部分建设** | 触发器级编排已由 §3.9 扳机清单 TriggerList 覆盖（注册/优先级仲裁/同源去重/事件总线派发）；DO 的决策路径编排（5 路径冲突消解与时序）与 TriggerList 职责重叠度高，**不建独立 DO**，由 TriggerList + 硬边界承载 | 若 Phase 2 多策略并发后出现 TriggerList 无法仲裁的跨路径冲突（如买入路径与做T路径同时竞争同一资金），再评估独立 DO |

**BM-BUY-02-C 人工指令轨接口契约**（production 补全）：

人工指令信号格式：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `instruction_id` | str | ✅ | 唯一标识，格式 `MANUAL-{YYYYMMDD}-{seq}` |
| `symbol` | str | ✅ | 标的代码 |
| `direction` | str | ✅ | `BUY` / `SELL` |
| `quantity` | int | ✅ | 数量（股），须为 100 整数倍 |
| `order_type` | str | ✅ | `LIMIT` / `MARKET`，默认 `LIMIT` |
| `limit_price` | float | 条件 | `order_type=LIMIT` 时必填 |
| `source` | str | ✅ | 固定 `MANUAL_FRONTEND` |
| `timestamp` | datetime | ✅ | 指令下达时间 |
| `confirm_large` | bool | ✅ | 大额确认标记（单笔 >5 万元须 true，防误触） |
| `override_reason` | str | 否 | 覆盖自动轨的理由（审计留痕） |

MTF 仲裁优先级：**应急轨（emergency）> 人工轨（manual）> 自动轨（auto）**。人工轨覆盖自动轨的机制：同一标的同一时段内，若人工指令与自动策略信号冲突，人工指令优先执行，自动策略信号挂起（`SUSPENDED_BY_MANUAL`）至人工指令成交或撤销后恢复。人工轨不覆盖应急轨——风控止损/极端行情触发时，人工买入指令被应急轨拦截。

与既有节的衔接：人工指令在 §3.4 集合竞价窗口（9:15-9:25）允许买入（自动策略不允许）；在 §3.5 允许市价单（自动策略限价为主）；在 §3.8 集合竞价 T+1 约束下，人工集合竞价买入的标的当日盘中不能卖。人工指令同样须过 BM-BUY-08 纪律闸四项严禁检测（追高/补仓/骄傲/报复），但人工确认后仅记录违规不拦截（终态决策权在人工，与"无降级"设计一致）。

**BM-BUY-03 5 路径冲突消解规则**（不建独立 DO，由 TriggerList + 硬边界承载）：

| 冲突场景 | 消解规则 | 承载机制 |
|---|---|---|
| 买入路径 vs 卖出路径（同标的） | 卖出优先（风险优先原则，与 §3.9 止损优先于加仓一致） | TriggerList priority 仲裁（SELL_* priority ≤4 > BUY_* priority 5） |
| 买入路径 vs 做T路径（同标的） | 做T 优先（做T 是日内已持仓的波段操作，买入是新仓，避免同日同标的双向操作混淆） | 硬边界：同标的当日有做T 卖出单时，新买入批次排期到次日 |
| 人工路径 vs 自动路径 | 人工覆盖自动（MTF 仲裁，见上） | MTF priority 仲裁 |
| 应急路径 vs 一切 | 应急覆盖一切（Kill Switch 最高优先） | TriggerList priority=1 无条件覆盖 |
| 多自动路径并发（多策略同时想买同一标的） | 按 C-031 置信度降序 + 先到先服务，低置信度信号挂起 | TriggerList cooldown + priority 仲裁 |

> **为何不建独立 DO**：§3.9 扳机清单已覆盖触发器级编排（注册/优先级仲裁/同源去重/事件总线派发），DO 的决策路径编排与 TriggerList 职责重叠度 >80%。MVP 阶段单标的单策略，5 路径冲突场景极少（上表 5 类冲突均可由 TriggerList priority + 硬边界规则消解）。独立 DO 会增加一层编排抽象，违反"骨架先行"纪律。Phase 2 多策略并发后若出现 TriggerList 无法仲裁的跨路径冲突，再评估独立 DO。

### 2.3 约束条件
- **T+1 不能做空**：当日买入次日才能卖；当日卖出资金 T+1 才可用 → 分批建仓批次间隔天然≥1 交易日
- **system_charter §3 约束四（策略三维度解耦）**：选股（what）/仓位（how much）/执行（how）解耦 → buy_flow 是"how"层，只消费仓位产出，不重算仓位
- **31_position_sizing §2.7 边界**：仓位算法不内置 regime 切换，只收 budget 数字 → buy_flow 同理，不读市场态
- **BM-BUY-08 交易纪律闸**：买入下单前必须过四项严禁检测（追高/补仓/骄傲/报复），buy_flow 不得绕过
- **打板容量极小**（单票几万~几十万）：打板策略建仓必须小账本、限价单、避免冲击

## 3. 决策：分批建仓 + 尾盘集中执行 + 限价锚定 + budget 数字驱动

### 3.1 买入流总览

```
[FirmTargetPortfolio]      [BM-BUY-04 分批建仓]         [BM-BUY-08 纪律闸]        [BM-EXE 执行]
31 产出的目标组合    →    分批方案(2批/置信度驱动)  →   四项严禁检测   →   限价单尾盘集中下单
(权重和=1.0,含CASH)       首仓试探+确认仓              追高/补仓拦截              14:50 锚定价格
                          2/3 条件放行下一批           骄傲/报复告警              T+1 资金口径
```

> **顺序理由**：仓位已由 31 在 firm 层算好（Kelly+裁剪），buy_flow 不重算仓位，只把目标权重拆成"什么时候下多少单"。纪律闸在分批方案之后、执行之前——每批下单前都要重新过纪律闸（防分批变相追高）。

### 3.2 ① 分批建仓（BM-BUY-04）—— 置信度驱动 2 批，板块回踩 A/B/C 为置信度调节因子（v1.4.0 集成）

#### 3.2.1 批次划分（MVP：2 批）

| 参数 | MVP 值 | 范围 | 说明 |
|---|---|---|---|
| `batch_count` | **2** | 2-4 | 首仓试探 + 确认仓；高置信度可合并为 1 批（激进） |
| `batch_interval` | **1 交易日** | 1-3 | 天然满足 T+1；批次间隔让市场给二次确认 |
| `satisfy_threshold` | **2/3** | 1/3-3/3 | 放行下一批需满足 2/3 条件（见下） |
| `confidence_tier_mode` | **C-031 驱动** | 激进/分批 | 高置信度→激进（首仓≥70%）；低置信度→分批（首仓 30-50%） |

**批次比例（首仓 : 确认仓）**：
- 高置信度（C-031 ≥ 阈值）：激进建仓，首仓 70%+，剩余一次性或合并 → 实质 1 批
- 低置信度（C-031 < 阈值）：分批建仓，首仓 30-50%（试单），确认仓 50-70%

> **对标**（10jqka 2026-06 分批入场实战）：首仓试探法则首批 20-30% 验证方向，符合预期再拉满，反转则立即止损——与本项目"首仓试单+确认仓"一致。倒金字塔（10/20/30/40）属左侧逆势加仓，本项目趋势/突破策略不用，仅价值反转策略可选（待 G04 校准）。

**C-031 置信度→批次比例映射算法**（**已施工** `src/zephyr/pf_alloc/batched_position_builder.py` MOD-PA-006）：

```python
def compute_batch_split(confidence_score_c031, strategy_type, sector_quality=None):
    """C-031 置信度→首仓比例映射（MVP 2 批/激进 1 批）

    sector_quality: 板块回踩质量 A/B/C（[22号§3.1②](22_sector_rotation_spec.md)，22号 active 后注入）
        A→置信度+0.1（浅回踩38.2-50%+缩量+板块强≥70，激进建仓倾向）
        B→置信度±0.0（深回踩50-61.8%+混合量能+板块中40-70，中性）
        C→置信度-0.1（破位>61.8%+放量+板块弱<40，分批或放弃倾向）
        None→不调整（22号未就绪降级，MVP 兼容，与§4.2 过度工程审查一致）
    """
    # A/B/C 板块回踩质量调节置信度（22号 v1.8.0 active 后启用，v1.4.0 集成）
    quality_adjustment = {"A": 0.1, "B": 0.0, "C": -0.1}.get(sector_quality, 0.0)
    adjusted_confidence = min(max(confidence_score_c031 + quality_adjustment, 0.0), 1.0)

    # C-031 置信度范围 [0, 1]，阈值按策略类型差异化
    aggressive_threshold = {"daban": 0.75, "multifactor": 0.65, "event": 0.70}
    threshold = aggressive_threshold.get(strategy_type, 0.70)

    if adjusted_confidence >= threshold:
        # 高置信度→激进建仓，首仓 70-100%，实质 1 批
        first_pct = min(0.70 + (adjusted_confidence - threshold) * 1.0, 1.0)
        return {"mode": "AGGRESSIVE", "batches": 1, "first_pct": first_pct,
                "confidence_source": confidence_score_c031, "sector_quality": sector_quality,
                "adjusted_confidence": adjusted_confidence}
    else:
        # 低置信度→分批建仓，首仓 30-50%
        first_pct = 0.30 + (adjusted_confidence / threshold) * 0.20
        return {"mode": "SCALED", "batches": 2, "first_pct": first_pct,
                "confidence_source": confidence_score_c031, "sector_quality": sector_quality,
                "adjusted_confidence": adjusted_confidence}
```

> **MVP 阈值待 G04 校准**：上表阈值（打板 0.75/多因子 0.65/事件 0.70）为初始值，待 [20_first_batch_strategies](20_first_batch_strategies.md) 策略类型定稿后按策略回测校准。

#### 3.2.2 放行下一批的 2/3 条件（MVP 简单信号，A/B/C 为增强）

放行确认仓需满足以下 3 项中≥2 项：

| 条件 | 信号源 | MVP 可用性 |
|---|---|---|
| ① 调整周期到位（进度≥80%） | BM-SEL-03（[22_sector_rotation_spec](22_sector_rotation_spec.md) ③） | 设计态，降级为"距首仓≥1 交易日" |
| ② 二次回落不破首仓入场价 | L0 行情 | ✅ 可用（盘中价格比较） |
| ③ 缩量企稳（量比<1） | BM-SEL-02 量比 | ✅ 可用 |

**板块回踩质量 A/B/C（[22 ②](22_sector_rotation_spec.md)）的定位**：**置信度调节因子，已集成**（v1.4.0）。22号 v1.8.0 active 后，A/B/C 作为置信度调节因子注入 `compute_batch_split` 的 `sector_quality` 参数（A→+0.1 激进/B→±0 中性/C→-0.1 分批或放弃，见 §3.2.1 算法）。A/B/C 不作为硬门——C 类不会直接拦截买入，而是降低置信度使策略更可能走分批路径或因阈值不满足而放弃。**降级兼容**：22号数据未就绪时 `sector_quality=None`，退化为纯 C-031 置信度驱动（MVP 兼容，与 §4.2 过度工程审查一致）。A/B/C→置信度映射 ±0.1 为初始值，待 C1 实盘校准（§5.2 阶段 2）。

#### 3.2.3 分批建仓输出契约

```python
@dataclass
class BatchedEntryPlan:
    symbol: str
    total_weight: float                 # 来自 FirmTargetPortfolio（31 产出）
    batches: list[Batch]                # 按时序排列
    confidence_tier: str                # AGGRESSIVE / SCALED（C-031 驱动）
    degrade_reason: str | None          # A/B/C 未就绪等降级标记

@dataclass
class Batch:
    batch_id: int                       # 1=首仓, 2=确认仓
    weight_fraction: float              # 占 total_weight 的比例（和=1.0）
    trigger_conditions: list[str]       # 2/3 条件
    status: str                         # PENDING / FILLED / DEGRADED / CANCELLED
```

### 3.3 ② 突破失败降级 —— 暂停后续批次 + 触发止损评估

分批建仓任一批次后，若发生**降级条件**，暂停后续批次并联动卖出侧（[42_sell_flow](42_sell_flow.md)）：

| 降级条件 | 动作 | 联动 |
|---|---|---|
| 跌破首仓入场价（突破失败） | 暂停确认仓 | 触发 [BM-SELL-01 突破成败](../battle_map/battle_map_07_sell_flow.md) → 止损评估 |
| 跌破前低（支撑破位） | 暂停全部后续批次 | 触发 [BM-SELL-04-B 止损族](../battle_map/battle_map_07_sell_flow.md) → 止损卖出 |
| 纪律闸拦截（追高/补仓） | 取消后续批次 | BM-BUY-08 Hard Block，记录违规 |

**突破失败检测算法**（**已施工** `src/zephyr/pf_alloc/batched_position_builder.py` MOD-PA-006）：

```python
def detect_breakout_failure(position, lookback_days=10, confirm_bars=2):
    """突破失败检测：收盘价跌破首仓入场价，且连续 confirm_bars 根 K 线确认"""
    # 前低定义：首仓入场前 lookback_days 日最低价
    prior_low = min(position.low_prices[-lookback_days:])
    # 突破失败：收盘价 < 入场价，连续 confirm_bars 根确认（防日内假跌破）
    recent_closes = position.close_prices[-confirm_bars:]
    if all(c < position.entry_price for c in recent_closes):
        return ("BREAKOUT_FAILED", "暂停确认仓", "→ BM-SELL-01 止损评估")
    # 支撑破位：收盘价 < 前低
    if all(c < prior_low for c in recent_closes):
        return ("SUPPORT_BROKEN", "暂停全部后续批次", "→ BM-SELL-04-B 止损卖出")
    return None
```

| 检测项 | 定义 | 确认方式 | 联动 |
|---|---|---|---|
| 突破失败 | 收盘价 < 首仓入场价 | 连续 2 根 K 线收盘确认（防日内假跌破） | 暂停确认仓 → BM-SELL-01 |
| 支撑破位 | 收盘价 < 前 10 日最低价 | 连续 2 根 K 线收盘确认 | 暂停全部 → BM-SELL-04-B |
| 前低定义 | 首仓入场前 10 日最低价 | — | MVP 固定 10 日，待 G04 校准 |

> **为何用"连续 2 根收盘确认"而非盘中实时跌破**：A 股盘中波动大（早盘/尾盘操纵），单根 K 线跌破可能是假跌破（猎杀）。连续 2 根收盘确认与 [42_sell_flow](42_sell_flow.md) §3.3 软止损模式（OBSERVING 观察期）逻辑一致——防被一次性插针扫出。

> **与 42_sell_flow 的边界**：买入侧只负责"暂停后续批次"（停止加仓），实际止损卖出动作归卖出侧 BM-SELL-01/04。buy_flow 不越界执行卖出。这符合三维度解耦（执行方式 how 在买入/卖出各自域内）。

### 3.4 ③ 买入时序 —— 尾盘集中执行为主（细分连续竞价/收盘集合竞价窗口）

> **合规基线**：[上交所交易规则 2026 修订](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml)（2026-07-06 生效，2026-08-10 现行有效）§2.4.2：9:15-9:25 开盘集合竞价 / 9:30-11:30、13:00-14:57 连续竞价 / **14:57-15:00 收盘集合竞价（不可撤单）** / 15:05-15:30 盘后固定价格交易。本备忘执行窗口须区分"可撤单连续竞价"与"不可撤单收盘集合竞价"两段。

| 时段 | 接受的指令 | MVP 策略 | 撤单约束 |
|---|---|---|---|
| 开盘集合竞价 09:15-09:25 | 仅人工指令（BM-BUY-06） | 自动策略不在集合竞价下单（价格未稳） | 9:20 后不可撤 |
| 连续竞价 09:30-14:45 | 自动+人工 | 自动策略信号盘前生成，但**不在早盘执行**（避开开盘波动+尾盘操纵检测前置窗口） | 可撤单 |
| 尾盘连续竞价 14:50-14:57 | **自动策略主执行窗口** | MVP 默认：14:50-14:55 集中下限价单，14:55-14:57 检查未成交并撤单改挂 | 可撤单 |
| 收盘集合竞价 14:57-15:00 | 补单/未成交兜底 | 14:57 前挂好收盘竞价单，14:57 后**不可撤单**，吃唯一收盘价 | **不可撤单** |

**尾盘集中执行理由**：
- A 股 T+1，尾盘买入次日即可卖，资金时间成本最低
- 避开开盘 09:30-10:00 高波动（量化策略噪声大、滑点高）
- 避开收盘前操纵检测窗口（BM-SELL-06 尾盘操纵检测在收盘前 N 分钟，买入与之错峰）
- 14:50 价格已基本反映当日信息，限价单锚定当日 VWAP/支撑位更稳
- **2026-07-06 起收盘集合竞价全面覆盖沪深主板/科创板/创业板/ETF**（licai.cofool 2026-08-03）：14:57-15:00 不可撤单+最大成交量原则撮合唯一收盘价，**压缩尾盘操纵空间**——MVP 须把"挂单"动作完成在 14:57 前，收盘竞价段只做"补未成交"，不在 14:57 后临时改单

**A股日内成交量 U 型分布**（2026-07 头条实证，机构 VWAP 执行痕迹识别）：

| 时段 | 成交量 | 含义 |
|---|---|---|
| 9:30-10:30 | 高 | 开盘集中博弈，消息消化——机构 VWAP 第一峰 |
| 10:30-11:00 | 中高 | 早盘第二波 |
| 11:00-13:00 | 低 | 临近午休+午休，观望 |
| 13:00-13:30 | 中高 | 午后开盘，策略重启——机构 VWAP 第二峰 |
| 13:30-14:00 | 中 | 午后第二波 |
| 14:00-14:57 | 逐渐走高 | 尾盘抢筹/抢跑 |
| 14:57-15:00 | 最高 | 收盘集合竞价 |

> **为何 MVP 选 14:50-14:57 而非机构 VWAP 的 10:30/13:30**：10:30/13:30 是机构大单拆执行的峰值，散户/小资金在峰值时段易成对手盘被动方；14:50-14:57 成交量已走高且价格趋稳，限价单锚 VWAP 滑点可控，又能赶在 14:57 收盘竞价前完成挂单。做T 策略（BM-SELL-08）另走 9:45-10:15 卖/13:30-14:30 买回的 U 型节奏（CSDN 2026-08-08 A 股做T 研究），与建仓尾盘窗口错峰。

**执行时序算法**（**已施工** `src/zephyr/pf_alloc/batched_position_builder.py` MOD-PA-006）：

```python
def schedule_buy_orders(batched_plan, current_time):
    """买入时序调度：14:50-14:55 挂单→14:55-14:57 检查→14:57 收盘竞价补单"""
    if current_time < time(14, 50):
        return ("WAIT", "未到尾盘窗口，盘前只生成信号不下单")
    if time(14, 50) <= current_time < time(14, 55):
        return ("PLACE_LIMIT", "挂限价单，锚 VWAP/支撑位")
    if time(14, 55) <= current_time < time(14, 57):
        return ("CHECK_AND_AMEND", "未成交单可撤改挂，防 14:57 后无法撤单")
    if time(14, 57) <= current_time < time(15, 0):
        return ("CLOSING_AUCTION_ONLY", "收盘竞价段不可撤单，仅补未成交兜底单")
    return ("AFTER_HOURS", "15:05-15:30 盘后固定价格交易仅人工大额，自动策略不参与")
```

> **合规约束**：2026 程序化交易新规（中基协私募委专委 2026-07 权威确认）高频认定 = **300 笔/秒 OR 20000 笔/日**（"15 笔/秒"系市场误传，中基协辟谣源自美国误传），异常交易撤单率监控线 50%（内部保守 15%）。MVP 尾盘集中 + 限价单天然合规（单标的 1-2 笔/日，远低于法定 300 笔/秒高频认定线；撤单集中在 14:55-14:57 窗口）。

**例外**：打板策略（[24_daban_strategy_detail](24_daban_strategy_detail.md)）需盘中追板，不走尾盘集中，由策略自定义时点（待 G04 校准）。

### 3.5 ④ 买入价格锚定 —— 限价为主，市价仅应急

| 买入类型 | 锚定价格 | 订单类型 | 理由 |
|---|---|---|---|
| 突破买入 | 压力位 × 0.99-1.00 | 限价单 | 锚压力位，略低防追高（纪律闸追高检测） |
| 回踩买入 | 支撑位 × 1.00-1.01 | 限价单 | 锚支撑位，略高确保成交 |
| 通用兜底 | min(目标价, 当日 VWAP) | 限价单 | VWAP 是机构成本基准，锚定避免被动追涨 |
| 应急（人工/做T回补） | — | 市价单 | 仅 BM-BUY-02-D 应急轨 + 人工指令允许 |

**VWAP 锚定计算**（2026-08 行业共识，shinnytech / CSDN 量化新规）：当日 VWAP = Σ(分钟成交价 × 分钟成交量) / Σ(分钟成交量)。14:50 时点用 9:30-14:50 的累计 VWAP 作锚，收盘竞价单锚 9:30-15:00 全天 VWAP 预测值（用近 20 日 U 型分布外推尾盘 10 分钟增量）。

```python
from random import uniform  # v1.4.1 补：uniform 需从 random 导入

def compute_anchor_price(symbol, buy_type, level_price, intraday_bars, current_time):
    """买入限价锚定价格计算（突破/回踩/兜底三档）"""
    # 当日累计 VWAP（9:30 至 current_time）
    cum_value = sum(bar.close * bar.volume for bar in intraday_bars)
    cum_volume = sum(bar.volume for bar in intraday_bars)
    vwap = cum_value / cum_volume if cum_volume > 0 else level_price

    if buy_type == "BREAKOUT":
        # 突破买入：锚压力位，略低 0-1% 防追高
        return level_price * uniform(0.99, 1.00)
    if buy_type == "PULLBACK":
        # 回踩买入：锚支撑位，略高 0-1% 确保成交
        return level_price * uniform(1.00, 1.01)
    # 通用兜底：min(目标价, 当日 VWAP)，避免被动追涨
    return min(level_price, vwap)
```

> **为何突破买入"略低"而回踩买入"略高"**：突破买入是追势，挂略低于压力位防假突破被套在最高点（与 BM-BUY-08 追高拦截协同）；回踩买入是接势，挂略高于支撑位确保反弹时能成交（限价单不成交是回踩买入最大风险）。方向相反，原理统一——限价单给市场让利，而非用市价单抢筹。

> **对标**（quantstock 2026 / algovestiq 2026）：机构普遍限价单锚技术位 ±1-2% 防猎杀，市价单仅用于必须成交的应急场景。本项目限价为主，与 BM-BUY-08 追高拦截协同（限价天然限制追高）。2026-08-08 CSDN 量化新规实证：TWAP/VWAP 拆单算法在 A 股已成标配，但**个人小资金无需拆单**（单标的几万~几十万，一笔限价单即可），锚 VWAP 即可获机构成本基准，不引入 TWAP/VWAP 拆单复杂度（MVP 不做，演进路径 §5.2 阶段 4）。

### 3.6 ⑤ 资金分配到多标的 —— 消费 31 产出 + 多标的下单排序 + 资金可用性兜底

buy_flow **不重算仓位**，直接消费 [31_position_sizing](31_position_sizing.md) §2.6 产出的 `FirmTargetPortfolio`：

```
FirmTargetPortfolio.holdings = {"600519": 0.08, "000858": 0.06, ..., "CASH": 0.25}
                                ↓ buy_flow 按 weight 落到订单
每标的全仓 = 总资金 × weight（CASH 标的不下单）
每标的分批 = 全仓 × batch.weight_fraction
```

**资金可用性口径**（T+1）：
- 当日可买入资金 = 账户总资金 − 前日买入未结算占用 + 前日卖出今日可用资金
- 31 §2.5 已定 T+1 结算约束：仓位决策按 T+1 可用资金计算，buy_flow 遵循同一口径
- 多标的 pro-rata 归一化在 31 Kelly 层做（§2.3.5），buy_flow 收到的权重和已≤总仓位上限

**资金不足时 pro-rata 削减算法**（**已施工** `src/zephyr/pf_alloc/batched_position_builder.py` MOD-PA-006）：实盘中账户可用资金可能因前日卖出未到账/冻结/手续费占用而**小于** FirmTargetPortfolio 的目标权重和。buy_flow 不重算仓位，但须做兜底削减：

```python
def clip_to_available_capital(target_holdings, available_cash, total_account_value):
    """资金不足时按权重 pro-rata 削减（保持相对排序，与 31 §2.5.2 总仓位裁剪一致）"""
    target_invest = sum(w for s, w in target_holdings.items() if s != "CASH") * total_account_value
    if target_invest <= available_cash:
        return target_holdings  # 资金充足，原样执行
    # 资金不足：按比例削减非 CASH 权重，CASH 对应增加
    scale = available_cash / target_invest
    clipped = {s: (w * scale if s != "CASH" else w) for s, w in target_holdings.items()}
    clipped["CASH"] = 1.0 - sum(w for s, w in clipped.items() if s != "CASH")
    clipped["_degrade_reason"] = f"available_cash={available_cash} < target_invest={target_invest}, scale={scale:.3f}"
    return clipped
```

> **为何 pro-rata 而非按优先级截断**：与 [32_firm_risk_aggregator](32_firm_risk_aggregator.md) §2.4 单票硬上限裁剪哲学一致——按比例削保持各标的相对权重不变，归因不被扭曲；优先级截断会抹零低优先级标的，归因失真。资金可用性是执行层约束，不应改变策略层的相对偏好。

**多标的下单排序算法**（**已施工** `src/zephyr/pf_alloc/batched_position_builder.py` MOD-PA-006）：MVP 尾盘 14:50-14:57 窗口集中下单多标的，下单顺序影响成交质量——**流动性差的标的先挂**（防尾盘挂单后无人接单），高置信度标的先挂（防错过窗口）：

```python
def rank_buy_orders(target_holdings, confidence_scores, liquidity_scores):
    """多标的下单排序：流动性差+高置信度优先（防尾盘挂单后无对手盘）"""
    symbols = [s for s in target_holdings if s != "CASH"]
    return sorted(symbols, key=lambda s: (
        liquidity_scores[s],           # 1. 流动性升序（流动性差→成交量小→先挂，防尾盘无对手盘）
        -confidence_scores[s],         # 2. 置信度降序（高置信度先挂，防错过窗口）
        -target_holdings[s],           # 3. 权重降序（大仓先挂，资金占用优先确认）
    ))
```

| 排序键 | 方向 | 理由 |
|---|---|---|
| 流动性评分 | 升序（差→先） | 流动性差标的尾盘挂单后成交概率低，先挂留时间撮合；与 [42_sell_flow](42_sell_flow.md) Kill Switch 清仓排序（流动性差先卖）同源——流动性差=先行动 |
| C-031 置信度 | 降序（高→先） | 高置信度信号时效性强，先挂防 14:57 前未成交 |
| 目标权重 | 降序（大→先） | 大仓资金占用大，先确认成交避免资金闲置 |

> **流动性评分来源**：MVP 用"近 20 日日均成交额"代理（成交额 < 5000 万→低流动性，5000 万-5 亿→中，>5 亿→高），与金策略 2026 实证"日均成交额 ≥5000 万"流动性门槛对齐。BM-SEL-02 量比/订单簿深度施工后，升级为订单簿斜率+深度综合评分（CSDN 2026-07-26 订单簿流动性分析）。

> **为何不引入 TWAP/VWAP 拆单**：2026-08-08 CSDN 量化新规实证 TWAP/VWAP 已成机构标配，但**适用场景是大额建仓**（金策略 2026：单标的数百万以上才需拆单降低冲击）。本项目个人小资金（单标的几万~几十万）一笔限价单即可，拆单反而增加报单次数触碰内部 15 笔/秒限频红线（远低于法定 300 笔/秒高频认定线）。TWAP/VWAP 列入演进路径 §5.2 阶段 4（资金规模 + 实时风控就绪后）。

### 3.7 ⑥ 与 budget 协同 —— 收 budget 数字执行，不读 regime

- budget 由 G15 RegimeMetaAllocator 经 Shrinkage 节流后给定（[34_regime_meta_allocator](34_regime_meta_allocator.md)，第二阶段上线，P3）
- buy_flow 收到的是**缩放后的 budget 数值上限**，不知道当前市场态（与 31 §2.7 仓位算法不内置 regime 一致）
- MVP 阶段 G15 未就绪：budget = 总仓位上限 80%（牛市默认，[31_position_sizing](31_position_sizing.md) §2.4.3），buy_flow 按此执行
- budget 变化（G14 三级升级）触发时，buy_flow 已下未成交的限价单**不撤销**（已挂单尊重市场），新批次按新 budget 评估

### 3.8 ⑦ T+1 约束 —— 贯穿建仓节奏与资金口径

| 约束 | 对 buy_flow 的影响 |
|---|---|
| 当日买入次日才能卖 | 分批建仓批次间隔≥1 交易日天然满足；首仓当日不可止损卖出（除非走做T BM-SELL-08 底仓回补） |
| 当日卖出资金 T+1 才可用 | 换仓场景（卖A买B）：卖A资金次日才可买B → 换仓分两天完成（T 日卖 A，T+1 日买 B） |
| 集合竞价 T+1 | 集合竞价买入的标的，当日盘中不能卖（仅人工指令允许集合竞价买入） |
| 节假日 T+1 | 节前买入节后才能卖，31 §2.5 已定节前 2 天提高现金 5-15%，buy_flow 遵循 |

> **换仓特殊处理**：置换再平衡卖出（BM-SELL-05）卖 A 买 B 时，因 T+1 资金约束，买 B 必须延后到 T+1。buy_flow 收到换仓指令后，将买 B 批次排期到次日（标记 `T_plus_1_pending`），不阻塞卖 A。

### 3.9 ⑧ 条件触发执行队列（扳机清单）—— 买入/卖出/执行/风控触发器统一注册

> **裁定**：买入侧（41）、卖出侧（[42](42_sell_flow.md)）、执行侧（[40](40_execution_broker.md)）、风控侧（[35](35_drawdown_protocol_impl.md)/[36](36_var_es_monitoring.md)/[37](37_liquidity_crisis_protocol.md)）的各类条件触发器统一注册到**扳机清单（TriggerList）**，由执行编排层（[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md) 进程内事件总线承载）统一监控与派发。本节定义扳机清单的注册格式与优先级，**非新建模块**——各触发器的判定逻辑仍在各自 spec 内，扳机清单只做注册、优先级排序与派发。

**为何需要扳机清单**：buy_flow §3.2-§3.3 有分批放行/突破失败触发器，[42_sell_flow](42_sell_flow.md) §3.3-§3.10 有止损/止盈/破位/熔断触发器，[40_execution_broker](40_execution_broker.md) 有订单状态/Make-or-Take/撤单率触发器，[35-37](35_drawdown_protocol_impl.md) 有回撤/VaR/流动性触发器。若各模块独立轮询自己的触发器，存在**冲突无人仲裁**（如确认仓放行 vs 回撤 Level2 暂停同时触发）和**重复检测**（突破失败在 41§3.3 和 42§3.6 都判定）。扳机清单统一注册后，按优先级仲裁冲突、消除重复。

**扳机清单注册格式**（每个触发器一条注册项）：

```python
@dataclass
class TriggerEntry:
    trigger_id: str               # 唯一标识，如 "BUY_BATCH2_RELEASE" / "SELL_ATR_STOP" / "RISK_DRAWDOWN_L2"
    source_module: str            # "41" / "42" / "40" / "35" / "36" / "37"
    condition: Callable           # 判定函数，返回 bool（判定逻辑在各自 spec 内）
    action: str                   # 触发动作，如 "PLACE_ORDER" / "CANCEL_BATCH" / "CLOSE_POSITION" / "HALT_NEW_BUY"
    priority: int                 # 优先级 1(最高)-5(最低)，冲突时高优先级覆盖
    scope: str                    # "POSITION" 单标的 / "STRATEGY" 策略级 / "PORTFOLIO" 组合级
    cooldown_sec: int             # 冷却期，防同触发器重复派发（默认 60s）
```

**MVP 扳机清单（按优先级排序）**：

| 优先级 | trigger_id | source | condition | action | scope | 备注 |
|---|---|---|---|---|---|---|
| 1 | `RISK_KILL_SWITCH` | 35 | 回撤>25% / Kill Switch 触发 | `HALT_ALL` 全停 | PORTFOLIO | 最高优先，覆盖一切 |
| 1 | `RISK_DRAWDOWN_L4` | 35 | 回撤>20% | `CLOSE_ALL_NEW` 清新仓 | PORTFOLIO | 四级回撤 |
| 2 | `RISK_DRAWDOWN_L3` | 35 | 回撤>15% | `HALT_NEW_BUY` 暂停新买 | PORTFOLIO | 三级回撤 |
| 2 | `RISK_LIQUIDITY_CRISIS` | 37 | 流动性危机触发 | `HALT_NEW_BUY` + 逃生执行器 | PORTFOLIO | 37号盘中监控 |
| 2 | `RISK_VAR_BREACH` | 36 | VaR>1.2× | `REDUCE_POSITION_20PCT` | PORTFOLIO | VaR 减仓 |
| 3 | `SELL_BREAKOUT_FAIL` | 42→41 | 收盘<入场价×2根 | `CANCEL_BATCH2` 暂停确认仓 | POSITION | 41§3.3 判定→42 联动 |
| 3 | `SELL_SUPPORT_BREAK` | 42→41 | 收盘<前低×2根 | `CANCEL_ALL_BATCH` 暂停全部 | POSITION | 41§3.3 判定→42 联动 |
| 3 | `SELL_CIRCUIT_BREAKER` | 42 | 策略级连续亏损熔断 | `HALT_STRATEGY` 暂停策略 | STRATEGY | 42§3.10 |
| 4 | `BUY_BREAKOUT_FAIL` | 41 | 同 SELL_BREAKOUT_FAIL 判定 | `CANCEL_BATCH2` | POSITION | 与 SELL_BREAKOUT_FAIL 同源去重（41 判定一次，注册两条 action） |
| 4 | `SELL_ATR_STOP` | 42 | 价格<entry-ATR×mult | `CLOSE_POSITION` 止损卖出 | POSITION | 42§3.3 |
| 4 | `SELL_TRAILING_STOP` | 42 | trailing stop hit | `CLOSE_POSITION` | POSITION | 42§3.3 移动止损 |
| 4 | `SELL_TAKE_PROFIT` | 42 | Chandelier Exit hit | `CLOSE_POSITION` 止盈卖出 | POSITION | 42§3.4 |
| 5 | `BUY_BATCH2_RELEASE` | 41 | 2/3 条件满足 | `PLACE_ORDER` 挂确认仓 | POSITION | 41§3.2.2 |
| 5 | `EXE_MAKE_OR_TAKE` | 40 | 超时未成交 | `AMEND_TO_MARKET` 切主动档 | POSITION | 40号决策⑪ |
| 5 | `EXE_CANCEL_RATE` | 40 | 滚动撤单率>15% | `THROTTLE_ORDERS` 限频 | STRATEGY | 40号合规 |

**优先级仲裁规则**：
- 同一标的同时触发多触发器时，按 priority 升序取最高优先级执行，同优先级按 scope（PORTFOLIO>STRATEGY>POSITION）排序
- `RISK_KILL_SWITCH`（priority=1）无条件覆盖一切——与 [35号 Kill Switch](35_drawdown_protocol_impl.md) 四级梯子顶端一致
- `SELL_BREAKOUT_FAIL`（priority=3）与 `BUY_BATCH2_RELEASE`（priority=5）冲突时，止损暂停优先于加仓放行——风险优先原则
- `BUY_BREAKOUT_FAIL` 与 `SELL_BREAKOUT_FAIL` 是同一判定的两个 action（41 暂停加仓 + 42 评估止损），注册时去重——condition 只算一次

**去重规则**：突破失败检测（41§3.3 `detect_breakout_failure`）的判定结果同时驱动 41 的"暂停确认仓"和 42 的"止损评估"。扳机清单注册时**共享同一个 condition 函数**，派发时按 trigger_id 分发到各自 action，避免重复计算。

**与三维度解耦的关系**：扳机清单是**编排层**（orchestration），不改变选股（what）/仓位（how much）/执行（how）的解耦——各触发器的判定逻辑和 action 仍在各自 spec 域内，扳机清单只做注册、优先级仲裁与派发。与 [60号进程内事件总线](60_cross_cutting_cleanup.md) 的关系：扳机清单是事件总线的**条件触发订阅模式**——condition 满足时发事件，action 订阅者响应。

> **过度工程审查**：扳机清单是设计模式非新模块——MVP 阶段各触发器已在各自 spec 定义，扳机清单只做注册表与优先级仲裁，不引入新算法/meta 参数。若各模块触发器数量<10 且无冲突场景（单标的单策略 MVP），可降级为各模块独立轮询，扳机清单作为文档参考不强制实现。Phase 2 多策略并发后冲突场景增多时再强制启用。

### 3.10 ⑨ 明日预案双层架构 —— B 盘后生成边界 / C 盘前加载约束 / A 盘中推演在边界内执行

> 本节覆盖作战地图 BM-PLAN-01/02/03 三环节，定位是**买入/卖出/仓位三流的共同上游边界提供者**。明日预案的核心思想：**边界比聪明更重要**——有边界无推演=笨但安全，有推演无边界=聪明但危险。模块真源 MOD-PLAN-001（BM-PLAN-01）/ MOD-PLAN-002（BM-PLAN-02）/ MOD-PLAN-003（BM-PLAN-03）。

#### 3.10.1 双层架构三层触发总览

| 层 | 环节 | 触发时点 | 产出 | 下游 |
|---|---|---|---|---|
| B 盘后边界层 | BM-PLAN-01 明日预案引擎 | 盘后收盘 | `TomorrowBoundary`（箱体上沿/下沿、加仓仓位上限、禁加仓价位、必出止盈价位、突破验证条件） | BM-PLAN-02 盘前加载 |
| C 盘前约束层 | BM-PLAN-02 盘前预案加载 | 次日 9:00 加载 + 9:25 集合竞价情景匹配 | `ConstraintState`（约束状态初始化） | BM-PLAN-01-C 盘中推演 + BM-BUY/SELL/POS 初始指令 |
| A 盘中推演层 | BM-PLAN-01-C 盘中推演（PLAN-01 子层） | 盘中每 15 分钟重算 | `BoundedActionAdvice`（边界内动作建议，毫秒级） | BM-BUY-02 买入融合 + BM-SELL-02 卖出融合 + BM-POS-01 仓位 |
| A 尾盘决策 | BM-PLAN-03 尾盘决策 | 14:45-15:00 | 尾盘调仓指令（加仓博高开/减仓防低开/持有不动） | BM-BUY-02 买入 + BM-SELL-02 卖出 |

#### 3.10.2 BM-PLAN-01 明日预案引擎（design）—— B 盘后生成 TomorrowBoundary

**定位**：盘后收盘后基于当日数据冷静计算明日操作边界，是**边界层（B/C）**的核心产出者。

**裁定**：**建设**——边界层是买入/卖出/仓位三流的共同安全基线，降级铁律明确（边界层坏=致命暂停操作，推演层坏=可接受机械执行边界）。

**参数默认值**（proposed，待实盘校准）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| 箱体上沿 | 昨日冷静算 | 基于昨日收盘数据计算的明日压力位 |
| 箱体下沿 | 昨日冷静算 | 基于昨日收盘数据计算的明日支撑位 |
| 加仓仓位上限 | 30% | 单标的加仓后总仓位不超过此上限 |
| 禁加仓价位 | 接近上沿 | 价格接近箱体上沿时禁止加仓（防追高） |
| 必出止盈价位 | 冲上沿必出 | 价格冲上箱体上沿时必须止盈（纪律） |
| 突破验证条件 | 放量站稳 10 分钟 | 突破上沿需放量且站稳 10 分钟才确认有效突破 |

**consumes**：

| 输入 | 来源 |
|---|---|
| 市场状态 | BM-SEL-03 |
| 次日 8 态预测 | BM-SEL-04 |
| 主力行为 | BM-SEL-05 |
| 情绪周期 | BM-SEL-23 |
| 卖出侧边界 | BM-SELL-07 |

**输出契约**：

```python
@dataclass
class TomorrowBoundary:
    symbol: str
    box_upper: float          # 箱体上沿
    box_lower: float          # 箱体下沿
    max_add_position: float   # 加仓仓位上限（默认 0.30）
    no_add_price: float       # 禁加仓价位（≈上沿）
    must_exit_price: float    # 必出止盈价位（冲上沿必出）
    breakout_confirm: str     # 突破验证条件（"放量站稳10分钟"）

@dataclass
class ConstraintState:
    symbol: str
    boundary: TomorrowBoundary
    scenario: str             # 盘前竞价匹配的 9 情景之一
    initialized: bool         # 盘前加载是否成功

@dataclass
class BoundedActionAdvice:
    symbol: str
    action: str               # "ADD" / "REDUCE" / "HOLD" / "EXIT"
    price_bound: tuple[float, float]  # 动作允许的价格区间（在 boundary 内）
    max_weight: float         # 动作允许的最大权重
    reason: str               # 边界内推演理由
```

**数据流**：市场状态+次日预测+主力行为+情绪周期+卖出侧边界 → 双层架构（B 盘后生成 TomorrowBoundary → C 盘前加载 ConstraintState → A 盘中推演在边界内执行毫秒级）→ 输出 TomorrowBoundary/ConstraintState/BoundedActionAdvice → downstream BM-BUY-02 买入融合 + BM-SELL-02 卖出融合 + BM-POS-01 仓位。

**降级铁律**：

| 层 | 故障后果 | 降级动作 |
|---|---|---|
| 边界层（B/C）坏 | **致命** | 暂停操作，延迟开盘到加载成功或人工介入 |
| 推演层（A）坏 | 可接受 | 机械执行边界（"边界比聪明更重要"） |

> **设计哲学**：有边界无推演=笨但安全（机械执行 boundary 不越界），有推演无边界=聪明但危险（无约束的推演可能追高/抄底）。边界层是安全基线，推演层是效率优化——安全优先于效率。

**与本文既有内容的衔接**：盘中推演（A 层）在边界内执行（毫秒级），挂 §3.4 尾盘执行窗口表——A 层推演的 BoundedActionAdvice 若建议 ADD，实际下单仍走 §3.4 的 14:50-14:57 尾盘窗口与 §3.5 限价锚定；若建议 REDUCE/EXIT，走 42 号卖出流。明日预案不改变本文的时序与锚定设计，只在时序与锚定之上加一道边界约束。

#### 3.10.3 BM-PLAN-02 盘前预案加载（design）—— C 层 9:25 集合竞价情景匹配

**定位**：次日盘前加载昨晚 TomorrowBoundary，9:25 集合竞价匹配 9 种情景，初始化 ConstraintState。

**裁定**：**建设**——盘前加载是边界层（C）的组成部分，加载失败=致命（无约束状态禁止开始交易）。

**参数默认值**：

| 参数 | 默认值 | 说明 |
|---|---|---|
| 竞价匹配窗口 | 9:20-9:25 | 集合竞价最后 5 分钟（9:20 后不可撤单，价格趋稳） |
| 情景分类规则 | 9 种情景 | 高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘 |

**consumes**：昨晚 TomorrowBoundary（BM-PLAN-01）。

**数据流**：昨晚 TomorrowBoundary → 盘前 9:00 加载边界 → 9:25 竞价匹配情景 → 触发对应分支 → 输出 ConstraintState → downstream BM-PLAN-01-C 盘中推演 + BM-BUY/SELL/POS 初始指令。

**降级**：盘前加载失败=致命，延迟开盘到加载成功或人工介入（无约束状态禁止开始交易）。

#### 3.10.4 BM-PLAN-03 尾盘决策（design）—— A 层 14:45 基于明日高/低开概率的加减仓决策

**定位**：14:45 尾盘决策窗口，基于今日盘中实时推演结果与持仓状态，做加减仓决策（加仓博明天高开/减仓防明天低开/持有不动）。

**裁定**：**建设**——与 §3.4 尾盘执行窗口是**分工消歧**关系：§3.4 是**建仓执行层**（驱动源=31 号仓位裁决，把 FirmTargetPortfolio 目标权重按 BatchedEntryPlan 落成限价单），PLAN-03 是**预测调仓决策层**（驱动源=BM-PLAN-01 盘中推演，基于明日高/低开概率调整已有持仓或加仓）。两者时段重叠（14:45-15:00 vs 14:50-14:57）但职责不同——PLAN-03 加仓指令走 §3.4 窗口执行，减仓指令走 42 号卖出流。

**参数默认值**：

| 参数 | 默认值 | 说明 |
|---|---|---|
| 尾盘加仓阈值 | 明日高开概率 >70% | 高开概率超阈值才加仓 |
| 尾盘减仓阈值 | 明日低开概率 >60% | 低开概率超阈值减仓 |
| 尾盘决策窗口 | 14:45-15:00 | A 股尾盘黄金决策点 |

**consumes**：今日盘中实时推演（BM-PLAN-01）+ 今日持仓状态（BM-POS-01）。

**数据流**：盘中推演结果+持仓状态 → 尾盘 15 分钟决策（加仓博明天高开/减仓防明天低开/持有不动）→ 输出尾盘调仓指令 → downstream BM-BUY-02 买入 + BM-SELL-02 卖出。

**降级**：尾盘决策未就绪→不操作（保持现有持仓过夜），宁可不操作也不在尾盘盲动。

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 一次性满仓建仓 —— 拒绝
- **拒绝理由**：择时风险高——一次性在错误时点满仓，无二次确认机会。battle_map BM-BUY-04 明确"分几批买，每批重新确认条件"。分批建仓是行业共识（10jqka 2026-06 / Wyckoff Phase D LPS 二次确认）
- **采用**：2 批分批（首仓试探+确认仓），高置信度可合并为 1 批

### 4.2 分批建仓硬依赖板块回踩 A/B/C —— 拒绝
- **拒绝理由**：[22_sector_rotation_spec](22_sector_rotation_spec.md) ② A/B/C 判定当前是骨架未定义，硬依赖会导致 41 ← 22 循环阻塞（41 无法独立施工）。过度工程：A/B/C 是增强信号，不应作为建仓硬门
- **采用**：C-031 置信度驱动 + 2/3 简单信号（量比/二次回落/调整周期）兜底，A/B/C 为 22 active 后的增强输入

### 4.3 盘中实时分散下单 —— 拒绝（MVP）
- **拒绝理由**：盘中实时下单需实时信号+实时风控+低延迟执行，MVP 复杂度过高；早盘高波动滑点大；与尾盘操纵检测窗口冲突
- **采用**：尾盘 14:50 集中执行（MVP），盘中仅人工指令+应急。盘中实时分散作为演进路径（§5.2 阶段 3）

### 4.4 市价单为主 —— 拒绝
- **拒绝理由**：市价单无价格保护，A 股流动性差的标的滑点可达 1-3%，且与 BM-BUY-08 追高拦截冲突（市价单天然追涨）
- **采用**：限价单为主（锚技术位/VWAP），市价单仅应急轨+人工大额确认后

### 4.5 buy_flow 内置 regime 切换 —— 拒绝
- **拒绝理由**：与 [31_position_sizing](31_position_sizing.md) §2.7 仓位算法不内置 regime 一致。regime 只通过 Shrinkage 缩 budget 间接影响，buy_flow 不读市场态，避免归因纠缠
- **采用**：buy_flow 只收 budget 数字，regime 节流归 G15

## 5. 上限定义

### 5.1 参数上限汇总

| 参数 | MVP 值 | 上限/范围 | 性质 |
|---|---|---|---|
| 分批数 | 2 | 2-4 | MVP 2 批，高置信度合并 1 批 |
| 批次间隔 | 1 交易日 | 1-3 | 天然满足 T+1 |
| 放行阈值 | 2/3 | 1/3-3/3 | 3 项条件满足 2 项 |
| 首仓比例（低置信度） | 30-50% | — | 试单性质 |
| 首仓比例（高置信度） | ≥70% | ≤100% | 激进可合并 |
| 执行窗口 | 14:50-14:57（主）+14:57-15:00（收盘竞价兜底，不可撤单） | — | 尾盘集中，细分连续竞价/收盘集合竞价两段 |
| 订单类型 | 限价单 | — | 市价仅应急 |
| 单笔风险 | 2%（Level1 降至 1.5%） | ≤2% | 与 35 回撤 Protocol 联动 |

### 5.2 演进路径

| 阶段 | 内容 | 触发条件 |
|---|---|---|
| **MVP（当前）** | 2 批分批 + 尾盘集中 + 限价锚定 + C-031 置信度驱动；22/35 未就绪用降级 | 本备忘定稿即可施工 |
| **阶段 2** | [22_sector_rotation_spec](22_sector_rotation_spec.md) 定稿，A/B/C→置信度映射注入 C-031 | 22 active |
| **阶段 3** | [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 定稿，四级阈值联动建仓节奏（Level1 新仓风险降 75%） | 35 active |
| **阶段 4** | 盘中实时分散下单 + TWAP/VWAP 拆单（需实时信号+实时风控+大资金规模就绪） | G15 + 实时风控 + 资金规模施工完成 |
| **阶段 5（待裁定）** | 动态分批数（按策略类型/波动率自适应选 2-4 批） | 各策略 6+ 月实盘 track record |
| **阶段 6（远期·待裁定）** | ML 加仓决策：Conformal Kelly 用 75% 预测区间宽度作 fractional Kelly scale（区间宽→缩首仓，区间窄→加首仓）+ PACE LLM 分层执行（长Horizon规划+短Horizon执行，超越 TWAP/AC） | 各策略 12+ 月 track record + conformal 预测模型校准通过 |
| **阶段 7（远期·待裁定）** | TT-DAC-PS 执行强化学习（twin-target actor-critic + policy smoothing，超 PPO/SAC/TWAP/VWAP/AC）+ MAP-Elites regime-specialist 执行组合（按流动性/波动率 niche 索引多策略）+ Constrained RL+Shield 合规执行（硬约束 Shield 保证零违规：volume participation/价格边界/自成交避免） | 资金规模达需拆单量级（单标的≥数百万）+ 订单簿 Level-2 数据接入 + 深交所/A 股 LOB 历史数据训练集就绪 |

**阶段 6 ML 加仓远期实证**（完整出处见 §8.3）：

- **Conformal Kelly**（[arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)）：conformal prediction 75% 区间宽度作 fractional Kelly scale——区间宽（模型不确定）缩仓、区间窄加仓；6 年回测（2016-2021 含成本+1 日延迟+杠杆上限）年化净 log 增长 28.5%、Sharpe 1.34、MaxDD 27.7%（drawdown dial 后 20.3%）；slow/unweighted/per-asset rolling 优于 locally adaptive（区间稳定性>局部锐度）。**本项目映射**：§3.2.1 C-031→批次比例映射可演进为 conformal interval→fractional Kelly scale，`confidence_score_c031` 参数可平滑替换为 conformal_width（替代手工阈值 0.65/0.70/0.75）。
- **PACE LLM 执行**（[arXiv:2607.28410](https://arxiv.org/html/2607.28410v1)，深交所 Level-1 数据）：长 Horizon 规划+短 Horizon 执行分层框架，超 TWAP/Almgren-Chriss 0.65 bps。**本项目映射**：MVP 尾盘集中执行可演进为"策略层 LLM 规划建仓节奏（分批间隔/时点）+执行层 LLM 分钟级下单"。
- **订单簿流动性 RL 拆单**（CSDN 2026-07-26）：ARIMA/LSTM 预测订单簿流动性+PPO/DQN 优化拆单（liquidity_score>0.8 不拆/>0.5 拆 2 份/≤0.5 拆 5 份）。**本项目映射**：§3.6 多标的排序算法可演进为 RL 动态拆单，需 Level-2 数据接入（MVP 不具备）。

> **为何 MVP 不做 ML 加仓**：Conformal Kelly 需 6+ 月校准数据（75% 覆盖率），PACE 需 LLM 推理基础设施+Level-1 历史数据，RL 拆单需 Level-2 数据——前置条件 MVP 均不满足，强行引入增加 meta 参数（模型选择/超参/重训周期）违反"骨架先行"纪律。阶段 6 为远期演进路径，接口替换点已预留（见上）。

**阶段 7 执行 RL 远期实证**（完整出处见 §8.3）：

- **TT-DAC-PS**（[arXiv:2606.08379](https://arxiv.org/html/2606.08379v1)，Reading/Göttingen/ICMA）：twin EMA critic targets+pessimistic min backup+TD3 target policy smoothing+delayed actor updates+conservative Q 正则，OU 噪声+混合衰减探索；10 只美股 LOB 一致降低 mean IS，超 PPO/SAC/A2C 及 TWAP/VWAP/AC 全部基线。**本项目映射**：阶段 4 TWAP/VWAP 拆单的远期升级（自适应流动性波动），需 LOB 数据+训练基础设施。
- **MAP-Elites regime-specialist 执行组合**（[arXiv:2601.22113](https://arxiv.org/pdf/2601.22113)，Imperial/BoA）：按流动性/波动率索引 specialist 策略组合，niche 内 +8-10%；PPO baseline 2.13 bps arrival slippage vs VWAP 5.23 bps（4900 笔 OOS/$21B）；每 cell 需大量算力。**本项目映射**：可与 [34 号 regime meta-allocator](34_regime_meta_allocator.md) 状态索引对接（r3 牛市激进执行/r4 熊市保守拆单），适用资金规模达拆单量级后。
- **Constrained RL + Shield 合规执行**（[arXiv:2510.04952](https://arxiv.org/pdf/2510.04952v1)，Probe Group）：CMDP 形式化硬约束（volume participation/price boundary/self-trading avoidance）+Shield 模块 action projection 保证**零违规**；ABIDES 多场测试超 TWAP/VWAP 且零合规违规。**A 股适配**：高频认定 300 笔/秒、撤单率监控 50%、涨跌停不申报、14:57 后不可撤、T+1 资金口径均可编码为 Shield 约束——纯 PPO/TT-DAC-PS（无 Shield）无法提供的形式化合规保证。

> **三法分工与协同**：TT-DAC-PS 优化**执行成本**（最小化 IS）/ MAP-Elites 优化**执行适应性**（regime-specialist 组合）/ Constrained RL+Shield 优化**执行合规性**（零违规）；可叠加（MAP-Elites 生成 specialist 池→TT-DAC-PS 训练→Shield 包裹保证合规），三法均属阶段 7 远期。
>
> **为何 MVP 不做执行强化学习**：①资金规模不达标——个人小资金单标的一笔限价单即可（金策略 2026：日均成交额≥5000 万、单标的数百万以上才需拆单）；②数据不达标——TT-DAC-PS/MAP-Elites 需 LOB 数据，MVP 仅 L0/L1 行情；③合规已由限价+尾盘集中保证（单标的 1-2 笔/日，远低于法定 300 笔/秒认定线）；④过度工程风险——RL 执行增加 meta 参数违反"骨架先行"。**接口预留**：§3.6 排序→MAP-Elites specialist 选择器、§3.5 锚定→TT-DAC-PS action 输出、§3.4 时序→Shield 约束投影层。
>
> **MPC 确定性执行远期候选**（阶段 4→7 桥接，[31_position_sizing §7.4](31_position_sizing.md) 反向引用）：[arXiv:2603.28898](https://arxiv.org/abs/2603.28898)（McAuliffe et al., Bayforest+Bertsekas 2026-03）凸 QP 每步求解，平衡 completion/impact/opportunity cost，NASDAQ Level-3 降 schedule shortfall 40-50%。**为何是最优桥接**：①比 TWAP/VWAP（阶段 4）更自适应（每步按实时量/价差重优化）；②比 RL（阶段 7）更轻量（凸 QP 闭式解，无需 LOB/训练设施）；③确定性可审计（QP 解可追溯）；④合规友好（凸约束直接编码 300 笔/秒+50% 撤单率线）。**为何 MVP 不做**：与阶段 7 RL 同理（资金/数据不达标），但前置门槛更低（仅需 L1 量数据）——阶段 4 就绪后可优先升级 MPC 而非直接跳 RL。

### 5.3 为何这是上限而非妥协
- 2 批分批 + 尾盘集中 + 限价锚定是 A 股 T+1 个人量化的实务共识（10jqka 2026-06 / eastmoney 2026-07）
- 不硬依赖 22/35 骨架，保证 MVP 可独立施工——这是"骨架先行"纪律下避免循环阻塞的关键
- 真正的上限 = 在 C-031 置信度驱动框架内把分批节奏做到极致，而不是堆 A/B/C/密度感知等未就绪信号

## 6. 待裁定（暂缓项）

> 以下项目暂不施工，**非永久禁止**。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **盘中实时分散下单** | 需实时信号+实时风控+低延迟执行，MVP 复杂度过高 | G15 + 实时风控就绪 |
| **动态分批数自适应** | MVP 固定 2 批；动态（按波动率/策略类型选 2-4）增加 meta 参数 | 各策略 6+ 月 track record |
| **倒金字塔左侧加仓** | 逆势加仓仅适用价值反转策略，趋势/突破策略不用 | G04 价值反转策略定稿后评估 |
| **Wyckoff Spring 识别建仓** | Spring（假破净吸筹）是高阶入场点，需 L2-B 主力阶段识别就绪 | BM-SEL-05 主力阶段识别施工完成 |

## 7. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 首仓/确认仓比例按策略类型差异化（打板 vs 多因子 vs 事件） | 本备忘 §3.2.1 | 待 G04（20_first_batch_strategies）产出校准 |
| 14:50 执行窗口对打板策略不适用，打板时点自定义 | 本备忘 §3.4 | 待 [24_daban_strategy_detail](24_daban_strategy_detail.md) 定稿 |
| 换仓 T+1 延后买 B 的批次排期与 budget 变化冲突时如何处理 | 本备忘 §3.8 | G14 已定稿 v1.0.0（[33_budget_change_handler](33_budget_change_handler.md)），可对齐 §3.8 |
| 35 四级回撤阈值触发时，进行中的分批建仓是否立即暂停 | 与 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 联动 | 待 35 active |

> **循环至零检查**：41 → 22（G06 骨架）/35（G16 骨架）/31（G12 active）。22/35 的框架在 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)（active）已有定义（35 §2.5 四级阈值已定），MVP 降级路径明确（22 未就绪→C-031 兜底；35 未就绪→30 §2.5 框架）。**无真循环阻塞**，41 可独立施工。✓

## 8. 引用

### 8.1 相关 design_memo
- [31_position_sizing](31_position_sizing.md) —— 仓位产出（FirmTargetPortfolio）来源，buy_flow 消费其权重
- [22_sector_rotation_spec](22_sector_rotation_spec.md) —— 板块回踩质量 A/B/C（骨架，增强输入）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) —— 回撤 Protocol（骨架，框架在 30 §2.5）
- [42_sell_flow](42_sell_flow.md) —— 卖出流（突破失败降级联动）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 —— 回撤四级阈值框架（35 未就绪时真源）

### 8.2 相关 battle_map
- [battle_map_06_buy_flow](../battle_map/battle_map_06_buy_flow.md) —— BM-BUY-04 分批建仓 / BM-BUY-08 纪律闸 / BM-BUY-02 四轨融合
- [battle_map_07_sell_flow](../battle_map/battle_map_07_sell_flow.md) —— BM-SELL-01 突破成败（降级联动）

### 8.3 开源实证参考
- **10jqka 分批入场实战（2026-06）** —— 首仓试探法则 20-30% 验证方向、等份均分法、倒金字塔左侧加仓；印证 2 批分批首仓试单设计（§3.2）
- **Wyckoff Accumulation（trading-charts / thecoinzone 2026-04）** —— Phase D LPS 二次确认入场、Spring 假破净吸筹；印证分批二次确认思想，Spring 识别记为待裁定（§6）
- **eastmoney 止损与资金管理（2026-07）** —— 单笔风险 1-3%、组合熔断；与 35 回撤 Protocol 单笔 2% 一致（§5.1）
- **水母量化分批低吸/高抛（新浪财经 2026-08-02）** —— 以基准价为锚每下跌预设幅度触发买入、每上涨触发卖出；印证"分批"是 A 股 2026 实务共识，模板化参数化执行（§3.2）
- **上交所交易规则 2026 修订（2026-07-06 生效）** —— §2.4.2 集合竞价/连续竞价/收盘集合竞价时段+14:57 后不可撤单；本备忘执行窗口细分的合规基线（§3.4）
- **A 股日内成交量 U 型分布（头条 2026-07-30）** —— 9:30-10:30/13:00-13:30 双峰、14:57-15:00 收盘竞价最高；机构 VWAP 执行痕迹识别三步法（看时点/看方向/看时点变化）；印证 MVP 选 14:50-14:57 而非机构峰值窗口的合理性（§3.4）
- **A 股做T 策略研究（CSDN 2026-08-08）** —— 冲高回落型 9:45-10:15 卖/13:30-14:30 买回、低开反弹型 10:00-11:00 买/13:30-14:30 卖；印证建仓尾盘窗口与做T U 型节奏错峰设计（§3.4）
- **2026 程序化交易新规（中基协 2026-07 权威确认 + CSDN 2026-08-08）** —— 高频认定 300 笔/秒 OR 20000 笔/日（"15 笔/秒"系市场误传，中基协辟谣源自美国误传）、TWAP/VWAP 成机构标配、Kelly+风险平价+动态再平衡头寸管理；印证 MVP 限价单+尾盘集中天然合规、个人小资金无需拆单（§3.4/§3.5/§3.6）
- **VWAP 算法详解（shinnytech 2026）** —— VWAP = Σ(成交价×成交量)/Σ(成交量)、被动型算法按历史成交量分布拆单；本备忘 VWAP 锚定计算来源（§3.5）
- **TWAP/VWAP 智能拆单（金策略 2026）** —— 日均成交额≥5000 万流动性门槛、篮子算法对高流动性用 VWAP/小盘股用 TWAP；本备忘流动性评分门槛来源（§3.6）
- **订单簿流动性与机器学习（CSDN 2026-07-26）** —— 订单簿深度/宽度/价差/斜率衡量流动性、ARIMA/LSTM 预测流动性、PPO/DQN 优化拆单、liquidity_score 分档拆单；本备忘多标的排序+流动性评分+阶段 6 演进来源（§3.6/§5.2）
- **Conformal Kelly（[arxiv 2608.01494](https://arxiv.org/html/2608.01494v1)，2026-08-02）** —— conformal prediction 75% 区间作 fractional Kelly scale、6 年回测年化 28.5%/Sharpe 1.34/MaxDD 27.7%、slow per-asset rolling 优于 adaptive、drawdown dial 降 MaxDD 至 20.3%；本备忘阶段 6 ML 加仓远期实证（§5.2）
- **PACE LLM 执行（[arxiv 2607.28410](https://arxiv.org/html/2607.28410v1)，2026-07-30）** —— LLM 做 parent-order execution 分层框架、深交所 Level-1 数据、超 TWAP/AC 0.65 bps、LLM 高 confidence 预示更好表现；本备忘阶段 6 ML 执行远期实证（§5.2）
- **TT-DAC-PS 执行强化学习（[arxiv 2606.08379](https://arxiv.org/html/2606.08379v1)，2026-06-07）** —— Twin-Target Deterministic Actor-Critic + Policy Smoothing，twin EMA critic + pessimistic min backup + TD3 smoothing + conservative Q 正则 + OU 混合探索；10 只美股 LOB 超全部 RL/传统基线；本备忘阶段 7 执行 RL 远期实证（§5.2）
- **MAP-Elites regime-specialist 执行（[arxiv 2601.22113](https://arxiv.org/pdf/2601.22113)，2026-01-30）** —— 质量多样性算法首次用于交易执行，按流动性/波动率 niche 索引多策略组合，specialist 8-10% 性能提升；PPO CNN baseline 2.13 bps vs VWAP 5.23 bps；本备忘阶段 7 regime-adaptive 执行远期实证（§5.2）
- **Constrained RL + Shield 合规执行（[arxiv 2510.04952](https://arxiv.org/pdf/2510.04952v1)，2025-10-06）** —— CMDP 形式化交易执行硬约束（volume/price/self-trade），Shield 模块 action projection 保证零违规，ABIDES 多场测试超 TWAP/VWAP 且零违规；本备忘阶段 7 合规执行远期实证，A 股 300 笔/秒高频认定约束编码（§5.2）
- **MPC for Trade Execution（[arXiv:2603.28898](https://arxiv.org/abs/2603.28898)，McAuliffe et al., Bayforest + Bertsekas, 2026-03）** —— 凸 QP 每步求解大单执行 MPC 框架，平衡 completion/impact/opportunity cost，NASDAQ Level-3 降 schedule shortfall 40-50%，比 RL 轻量（凸 QP vs 神经网络）；本备忘阶段 4→7 桥接远期候选（§5.2），31_position_sizing §7.4 反向引用

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-15 | 1.7.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-07） | §5.2 阶段 6/7 实证背书与 §8.3 引用重复处指针化收拢（关键数值 28.5%/Sharpe 1.34/MaxDD 27.7%→20.3%/0.65bps/2.13 vs 5.23bps/40-50% 全保留，出处归 §8.3）；§3.2.2 过度工程审查重复段并入上行（A/B/C→置信度 ±0.1 待 C1 校准保留）；§3.10.4 与 §3.4 分工消歧重复段并入 §3.10.4 裁定；§6 已实施 strikethrough 行删除（v1.4.0 修订记录已载）；分批 2 批/2/3 条件/14:50-14:57 窗口/限价锚定/pro-rata 削减/扳机清单 15 条/T+1 两日型换仓全保留，章节标题编号一字不动 |
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G19 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active，回填 7 项讨论要点 | 分批建仓（置信度驱动 2 批，A/B/C 为增强非硬门）/突破失败降级/尾盘集中时序/限价锚定/消费 31 产出/budget 数字驱动/T+1 约束；过度工程审查（不硬依赖 22 骨架）；循环至零检查通过 |
| 2026-08-10 | 1.0.1 | §7 开放问题"待 G14 定稿"→"G14 已定稿 v1.0.0，可对齐 §3.8"（由 G12-AI 同步） | 33号于本日升 active v1.0.0，本备忘引用的"待定稿"措辞陈旧 |
| 2026-08-10 | 1.1.0 | 施工算法补全 + 2026-08 最新实证 + ML 加仓远期 | §3.2.1 C-031 置信度→批次比例映射算法；§3.3 突破失败检测算法（连续 2 根收盘确认）；§3.4 执行窗口细分（14:50-14:57 主+14:57-15:00 收盘竞价兜底，对齐上交所 2026 修订规则）+ U 型成交量分布+执行时序调度算法+15 笔/秒合规约束；§3.5 VWAP 锚定计算+价格锚定算法（突破略低/回踩略高）；§3.6 资金不足 pro-rata 削减算法+多标的下单排序算法（流动性差+高置信度优先）；§5.2 新增阶段 6 ML 加仓远期（Conformal Kelly+PACE LLM 执行+RL 拆单）；§8.3 补 9 项 2026-08 最新实证 | 用户要求审查施工环节流程算法缺失、选项之外更好算法、2026-08-08 最新研究、文档结构内容调整 |
| 2026-08-10 | 1.2.0 | 阶段 7 执行强化学习远期实证 + 三法分工 | §5.2 新增阶段 7（TT-DAC-PS 执行 RL + MAP-Elites regime-specialist 组合 + Constrained RL+Shield 合规执行）；§5.2 补三法实证背书（arXiv:2606.08379 超全部 RL/传统基线 / arXiv:2601.22113 specialist 8-10% 提升 + PPO 2.13 bps vs VWAP 5.23 bps / arXiv:2510.04952 Shield 零违规 + A 股 15 笔/秒约束编码）；§5.2 补三法分工与协同 + 为何 MVP 不做 RL 执行四理由（资金/数据/合规/过度工程）；§8.3 补 3 条阶段 7 实证引用 | 用户要求全网搜索 2026-08-08 最新执行算法、选项外更优答案；TT-DAC-PS/MAP-Elites/Constrained RL+Shield 是 2026 执行 RL 前沿三法，分别优化成本/适应性/合规性，可叠加但属远期 |
| 2026-08-10 | 1.3.0 | MPC 确定性执行远期候选（阶段 4→7 桥接）+ 修复 31→41 断链 | §5.2 新增 MPC 确定性执行远期候选段落（arXiv:2603.28898 McAuliffe 2026-03：凸 QP 每步求解大单执行，降 schedule shortfall 40-50%，比 RL 轻量）；§5.2 补为何 MPC 是阶段 4→7 最优桥接四理由（比 TWAP/VWAP 自适应/比 RL 轻量/确定性可审计/合规友好）+ 为何 MVP 不做（资金/数据不达标但门槛低于 RL）；§8.3 补 MPC for Trade Execution 引用 | 31_position_sizing §7.4（v1.12.0）反向引用"arXiv:2603.28898 属执行层远期候选 41_buy_flow §5.2 阶段 5/6"但 41 未提及 MPC 构成断链。本次补全 MPC 远期候选段落修复断链，MPC 定位为阶段 4 TWAP/VWAP→阶段 7 RL 的确定性桥接路径（凸 QP 比 RL 轻量，比 TWAP/VWAP 自适应），前置门槛低于 RL（仅需 L1 成交量数据不需 LOB） |
| 2026-08-10 | 1.3.1 | 高频认定阈值事实订正（15笔/秒→300笔/秒法定线） | §3.4 合规约束订正（CSDN"15笔/秒"误传→中基协权威确认 300笔/秒 OR 20000笔/日）；§3.6 TWAP/VWAP 拆单红线（15→300 法定线）；§5.2 Constrained RL+Shield A 股约束（15→300）；§5.2 MPC 合规约束（15→300）；§5.2 为何 MVP 不做 RL（15→300）；§8.3 引用订正（300→15 误传→300 法定+15 内部安全垫） | 与 [24_daban_strategy_detail](24_daban_strategy_detail.md) v1.4.1 + [40_execution_broker](40_execution_broker.md) v1.5.0 权威证据链对齐：中基协私募委专委 2026-07 明确确认"目前 A 股高频交易认定标准设置为每秒 300 笔以上"，"15笔/秒"系市场误传（皮海洲"建议"被以讹传讹+自媒体将"撤单率15%"与"高频认定300笔/秒"混同），中基协辟谣"15笔/秒""50微秒最小停留"均源自美国误传。本项目内部限频 15 笔/秒保留为安全垫（远低于法定 20×） |
| 2026-08-10 | 1.4.0 | A/B/C 板块回踩质量集成 + 扳机清单统一条件触发执行队列 | ①§3.2.1 `compute_batch_split` 新增 `sector_quality` 参数（A→+0.1/B→±0/C→-0.1 置信度调节，22号 v1.8.0 active 后启用，`None` 降级兼容）；②§3.2.2 A/B/C 定位从"增强非硬门"升级为"置信度调节因子，已集成"；③§3.9 新增⑧条件触发执行队列（扳机清单）—— 买入/卖出/执行/风控触发器统一注册 TriggerEntry（trigger_id/source/condition/action/priority/scope/cooldown）+ MVP 15 条扳机清单按优先级 1-5 排序 + 优先级仲裁规则（Kill Switch 覆盖一切/止损优先于加仓/同源去重）+ 与三维度解耦关系（编排层不改变 what/how much/how 解耦）+ 过度工程审查（设计模式非新模块，MVP 可降级为独立轮询）；④§6 待裁定 A/B/C→置信度映射表从暂缓升级为已实施（待 C1 校准） | 用户要求审查施工环节流程算法缺失+文档结构内容调整+持续改进。22号 v1.8.0 active 使 A/B/C 集成解锁——原 v1.0.0 设计为"A/B/C 增强"避免 41←22 循环阻塞，现 22 active 可正式注入 `sector_quality`。扳机清单解决多模块触发器冲突无人仲裁+重复检测问题（如确认仓放行 vs 回撤 Level2 暂停同时触发），是编排层设计模式非新模块，MVP 可降级为独立轮询 |
| 2026-08-10 | 1.5.0 | 施工标注清理——"施工缺失补全"→"施工伪代码已补全" | §3.3 突破失败检测算法 / §3.4 执行时序算法 / §3.6 资金不足 pro-rata 削减算法 / §3.6 多标的下单排序算法 共 4 处标注从"施工缺失补全"更新为"施工伪代码已补全"——v1.1.0 已补全全部伪代码（detect_breakout_failure/schedule_buy_orders/clip_to_available_capital/rank_buy_orders 四函数完整），标注为历史遗留未同步 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+持续改进。核查发现 41 号 4 处算法伪代码早在 v1.1.0 已完整补全，但"施工缺失补全"标注未同步更新造成"算法缺失"的误读。本次清理过时标注，准确反映施工状态 |
| 2026-08-10 | 1.5.1 | 伪代码精度审计——uniform 导入补全 + 跨文档调用链验证 | §3.5 `compute_anchor_price` 补 `from random import uniform` 导入语句（原伪代码直接调用 `uniform()` 未声明导入，施工方可能遗漏）。跨文档调用链验证：41 号扳机清单 14 条 TriggerEntry 的 condition 函数来源均已确认（detect_breakout_failure 在 41§3.3 定义、triage_position 在 42§3.2 定义、has_volume_confirmation 在 26§2.5 定义），无悬空函数。边界条件审计：clip_to_available_capital 有 target_invest<=available_cash 保护 + pro-rata 削减逻辑正确；compute_batch_split 有 sector_quality=None 降级兼容；detect_breakout_failure 有连续 2 根确认防假跌破 | 七十二轮伪代码边界条件深度审计——换三个新角度（跨文档调用链验证/伪代码边界条件审计/参数来源追踪）发现 1 处导入缺失，已修复 |
| 2026-08-12 | 1.6.0 | 作战地图全覆盖补丁——新增明日预案小节（BM-PLAN-01/02/03）+ 上游四轨与情景对策小节（BM-BUY-01/02-A-1/02-A-2/02-B/02-C/03） | ①§3.10 新增⑨明日预案双层架构——B 盘后生成 TomorrowBoundary（箱体上沿/下沿、加仓上限 30%、禁加仓价位、必出止盈价位、突破验证放量站稳 10 分钟）/ C 盘前 9:25 集合竞价 9 情景匹配加载 ConstraintState / A 盘中推演在边界内执行毫秒级 + 尾盘 14:45 预测驱动调仓；降级铁律（边界层坏=致命暂停，推演层坏=可接受机械执行）；与 §3.4 尾盘窗口分工消歧（§3.4 建仓执行 vs PLAN-03 预测调仓）；输出契约 TomorrowBoundary/ConstraintState/BoundedActionAdvice 三 dataclass；模块真源 MOD-PLAN-001/002/003。②§2.2.1 新增上游四轨与情景对策现状——BM-BUY-01 暂缓（8 态预测被 90 §7 暂缓连带）/ BM-BUY-02-A-1 分途承载不单独建设（a/b/d 由 10 号覆盖，c 被 90 §7 暂缓）/ BM-BUY-02-A-2 不建设（与 21 §3.2 双引擎融合边界冲突+违反 30 Model A 独立账本）/ BM-BUY-02-B 暂缓（AI Discovery 无承载+41 §4.5 不读市场态）/ BM-BUY-02-C 补人工指令接口契约（字段表+MTF 仲裁应急>人工>自动+与 §3.4/§3.5/§3.8 衔接）/ BM-BUY-03 部分建设不建独立 DO（TriggerList+硬边界承载，5 路径冲突消解规则表） | 作战地图 9 环节设计缺口闭合：BM-PLAN-01/02/03 明日预案三环节 + BM-BUY-01/02-A-1/02-A-2/02-B/02-C/03 上游六环节，每环节显式 BM 编号映射（定位→裁定→契约/参数/接口），建设项参数默认值优先采用 steps JSON proposed 值 |
| 2026-08-13 | 1.7.0 | 施工落地——6 算法+6 dataclass+15 TriggerList 落码 | ①§3.2.1 `compute_batch_split` → `src/zephyr/pf_alloc/batched_position_builder.py`（MOD-PA-006）；②§3.3 `detect_breakout_failure` → 同上（算法顺序修正：支撑破位优先于突破失败检查，因收盘<前低必然也<入场价）；③§3.4 `schedule_buy_orders` → 同上；④§3.5 `compute_anchor_price` → 同上；⑤§3.6 `clip_to_available_capital` + `rank_buy_orders` → 同上；⑥§3.2.3 `Batch`/`BatchedEntryPlan` dataclass → 同上；⑦§3.9 `TriggerEntry` dataclass + 15 条 MVP 扳机清单 → `src/zephyr/trading/trigger_registry.py`（MOD-TRIG-001）；⑧§3.10.2 `TomorrowBoundary`/`ConstraintState`/`BoundedActionAdvice` dataclass → `src/zephyr/plan_engine/`（MOD-PLAN-001/002/003）。83 测试连续 2 轮全部通过 | AI-BUY-001 施工：验证 6 算法伪代码落码完整性+6 个 dataclass 契约+15 条 TriggerList。detect_breakout_failure 算法顺序修正（SUPPORT_BROKEN 优先于 BREAKOUT_FAILED 检查）——原伪代码先检查 BREAKOUT_FAILED 导致 SUPPORT_BROKEN 永远不会触发（收盘<前低必然也<入场价），修正为先检查更严重的支撑破位 |
